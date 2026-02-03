#!/usr/bin/env python3
#
# Scout (OpenAI-compatible) Automated PR Accessibility Review Script
# - Splits review per file to avoid timeouts on large PRs
# - Retries on transient 5xx / 504 Gateway Timeout (CloudFront)
# - Forces strict JSON output and normalizes common schema deviations
#
# Required env:
# - PR_NUMBER
# - GITHUB_TOKEN
# - FRAMEWORK_PATH (optional)
# - GITHUB_REPOSITORY (optional)
#
# Scout env:
# - SCOUT_API_KEY
# - SCOUT_BASE_URL  (OpenAI compatibility base url; in your setup it works without /v1)
# - SCOUT_MODEL     (e.g. gpt-5.2, claude-sonnet-4-5, gpt-4-1-mini)
#
# Optional:
# - SCOUT_MAX_TOKENS (default 2500)
# - SCOUT_TEMPERATURE (default 0)
# - SCOUT_FILES_PER_BATCH (default 1)  # keep 1 for true per-file
# - SCOUT_MAX_DIFF_CHARS (default 180000)  # truncates overly large diffs per request
# - SCOUT_MAX_SNIPPET_LINES (default 30)   # clamp code snippets (current_code / suggested_fix)
# - SCOUT_RETRY_ATTEMPTS (default 4)
#

import os
import sys
import json
import subprocess
from pathlib import Path


# --- GitHub / CI env ---
GITHUB_TOKEN = os.environ.get("GITHUB_TOKEN")
PR_NUMBER = os.environ.get("PR_NUMBER")
GITHUB_REPOSITORY = os.environ.get("GITHUB_REPOSITORY", "")
FRAMEWORK_PATH = os.environ.get("FRAMEWORK_PATH", "/tmp/accessibility-fixer")

# --- Scout env (OpenAI-compatible) ---
SCOUT_API_KEY = os.environ.get("SCOUT_API_KEY")
SCOUT_BASE_URL = os.environ.get("SCOUT_BASE_URL")
SCOUT_MODEL = os.environ.get("SCOUT_MODEL", "gpt-4-1-mini")

SCOUT_MAX_TOKENS = int(os.environ.get("SCOUT_MAX_TOKENS", "2500"))
SCOUT_TEMPERATURE = float(os.environ.get("SCOUT_TEMPERATURE", "0"))

SCOUT_FILES_PER_BATCH = int(os.environ.get("SCOUT_FILES_PER_BATCH", "1"))
SCOUT_MAX_DIFF_CHARS = int(os.environ.get("SCOUT_MAX_DIFF_CHARS", "180000"))
SCOUT_MAX_SNIPPET_LINES = int(os.environ.get("SCOUT_MAX_SNIPPET_LINES", "30"))

SCOUT_RETRY_ATTEMPTS = int(os.environ.get("SCOUT_RETRY_ATTEMPTS", "4"))

# Exit codes
EXIT_SUCCESS = 0
EXIT_CRITICAL_ISSUES = 1
EXIT_HIGH_PRIORITY = 2


# ---- helpers ----
def run_command(cmd, capture_output=True):
    result = subprocess.run(
        cmd,
        shell=True,
        capture_output=capture_output,
        text=True,
    )
    return result.stdout.strip() if capture_output else None


def sleep_seconds(seconds):
    # Keep it shell-based to avoid any runner weirdness
    run_command("sleep {}".format(int(seconds)), capture_output=False)


def chunk_list(items, size):
    if size <= 0:
        size = 1
    for i in range(0, len(items), size):
        yield items[i : i + size]


def dedupe_issues(issues):
    seen = set()
    out = []
    for i in issues:
        key = (
            str(i.get("file", "")),
            str(i.get("line", "")),
            str(i.get("title", "")),
            str(i.get("wcag_sc", "")),
        )
        if key in seen:
            continue
        seen.add(key)
        out.append(i)
    return out


def clamp_lines(text, max_lines):
    if not isinstance(text, str):
        return ""
    lines = text.splitlines()
    if len(lines) <= max_lines:
        return text
    return "\n".join(lines[:max_lines]) + "\n... [truncated]"


def normalize_issue(issue):
    # Ensure a consistent schema to prevent KeyErrors later
    if not isinstance(issue, dict):
        return None

    normalized = dict(issue)

    # wcag_sc sometimes comes back as a list; convert to a single string
    wcag_sc = normalized.get("wcag_sc", "")
    if isinstance(wcag_sc, list):
        normalized["wcag_sc"] = "; ".join([str(x) for x in wcag_sc])
    elif wcag_sc is None:
        normalized["wcag_sc"] = ""
    else:
        normalized["wcag_sc"] = str(wcag_sc)

    # Ensure wcag_level is a string
    wcag_level = normalized.get("wcag_level", "")
    normalized["wcag_level"] = "" if wcag_level is None else str(wcag_level)

    # Ensure severity/title/file are strings
    for k in ["file", "severity", "title", "description", "impact"]:
        v = normalized.get(k, "")
        normalized[k] = "" if v is None else str(v)

    # line should be an int if possible
    line = normalized.get("line", 0)
    try:
        normalized["line"] = int(line)
    except Exception:
        normalized["line"] = 0

    # resources should be a list of strings
    resources = normalized.get("resources", [])
    if resources is None:
        resources = []
    if isinstance(resources, str):
        resources = [resources]
    if not isinstance(resources, list):
        resources = []
    normalized["resources"] = [str(x) for x in resources]

    # Clamp code snippets (defensive; prompt also asks for it)
    normalized["current_code"] = clamp_lines(normalized.get("current_code", ""), SCOUT_MAX_SNIPPET_LINES)
    normalized["suggested_fix"] = clamp_lines(normalized.get("suggested_fix", ""), SCOUT_MAX_SNIPPET_LINES)

    return normalized


# ---- PR data ----
def get_pr_files():
    print("Getting changed files...")
    files_json = run_command("gh pr view {} --json files".format(PR_NUMBER))
    files_data = json.loads(files_json)
    return [f["path"] for f in files_data.get("files", [])]


def detect_platforms(files):
    platforms = set()
    for file in files:
        ext = Path(file).suffix.lower()
        if ext in [".swift", ".m", ".mm"]:
            platforms.add("iOS")
        elif ext in [".kt", ".java"]:
            platforms.add("Android")
        elif ext in [".tsx", ".jsx", ".ts", ".js", ".html", ".css"]:
            platforms.add("Web")
        elif ext == ".dart":
            platforms.add("Flutter")
    return list(platforms)


def get_pr_base_head_shas():
    base = run_command('gh pr view {} --json baseRefOid -q .baseRefOid'.format(PR_NUMBER))
    head = run_command('gh pr view {} --json headRefOid -q .headRefOid'.format(PR_NUMBER))

    # Fallbacks
    if not head:
        head = run_command("git rev-parse HEAD")
    if not base and head:
        # Try merge-base against origin if available; otherwise best effort
        base = run_command("git merge-base {} origin/HEAD".format(head)) or run_command("git merge-base {} HEAD~1".format(head))

    return base, head


def get_diff_for_files(base_sha, head_sha, files):
    quoted = " ".join(["'{}'".format(p.replace("'", "'\\''")) for p in files])
    cmd = "git diff {}...{} -- {}".format(base_sha, head_sha, quoted)
    diff = run_command(cmd) or ""
    if len(diff) > SCOUT_MAX_DIFF_CHARS:
        diff = diff[:SCOUT_MAX_DIFF_CHARS] + "\n\n# [TRUNCATED] Diff exceeded SCOUT_MAX_DIFF_CHARS.\n"
    return diff


# ---- guides + prompt ----
def load_guides(platforms):
    guides = {}
    framework_path = Path(FRAMEWORK_PATH)

    core_guides = [
        "guides/GUIDE_WCAG_REFERENCE.md",
        "guides/wcag/QUICK_LOOKUP.md",
        "guides/wcag/SEVERITY_GUIDELINES.md",
        "guides/COMMON_ISSUES.md",
    ]

    print("Loading accessibility guides...")

    for guide_path in core_guides:
        full_path = framework_path / guide_path
        if full_path.exists():
            with open(full_path, "r", encoding="utf-8") as f:
                guides[guide_path] = f.read()

    platform_guide_map = {
        "iOS": "guides/GUIDE_IOS.md",
        "Android": "guides/GUIDE_ANDROID.md",
        "Web": "guides/GUIDE_WEB.md",
        "Flutter": "guides/GUIDE_FLUTTER.md",
    }

    for platform in platforms:
        guide_path = platform_guide_map.get(platform)
        if not guide_path:
            continue
        full_path = framework_path / guide_path
        if full_path.exists():
            with open(full_path, "r", encoding="utf-8") as f:
                guides[guide_path] = f.read()

    return guides


def create_review_prompt(pr_diff, files_in_batch, platforms, guides):
    guides_text = "\n\n".join(["## {}\n\n{}".format(path, content) for path, content in guides.items()])
    files_list = "\n".join(["- {}".format(f) for f in files_in_batch])
    platforms_list = ", ".join(platforms) if platforms else "Unknown"

    parts = []
    parts.append("You are performing an automated accessibility review on a GitHub Pull Request.")
    parts.append("")
    parts.append("# PR Information")
    parts.append("Platforms detected: {}".format(platforms_list))
    parts.append("Files in this batch: {}".format(len(files_in_batch)))
    parts.append(files_list)
    parts.append("")
    parts.append("# Task")
    parts.append("Review ONLY the changed code in this diff for accessibility issues.")
    parts.append("Focus on labels/hints/roles, interactive elements, images/icons alt text, form inputs, touch targets, Dynamic Type/font scaling, semantics, and contrast.")
    parts.append("")
    parts.append("# Guidelines")
    parts.append(guides_text)
    parts.append("")
    parts.append("# PR Diff (Batch Only)")
    parts.append("```diff")
    parts.append(pr_diff)
    parts.append("```")
    parts.append("")
    parts.append("# Output Format (STRICT)")
    parts.append("Return ONLY a valid JSON array. No markdown. No prose. No code fences.")
    parts.append("If no issues found, return: []")
    parts.append("")
    parts.append("Each issue must have these keys (all values MUST be strings, except line which must be a number):")
    parts.append('file, line, severity ("Critical|High|Medium|Low"), wcag_sc, wcag_level, title, description, impact, current_code, suggested_fix, resources.')
    parts.append("")
    parts.append("Rules:")
    parts.append("- Report issues ONLY in the CHANGED code shown in this batch diff.")
    parts.append("- wcag_sc MUST be a single string. If multiple SC apply, join with '; '.")
    parts.append("- current_code and suggested_fix must be short snippets (max {} lines each).".format(SCOUT_MAX_SNIPPET_LINES))
    parts.append("- resources MUST be an array of strings (or empty array []).")
    parts.append("- Do not invent line numbers; if unsure, pick the closest changed line.")

    return "\n".join(parts)


# ---- Scout call ----
def parse_json_response(response_text):
    # Try direct JSON parse
    try:
        data = json.loads(response_text)
        return data if isinstance(data, list) else []
    except Exception:
        pass

    # Try to extract first [...] block
    start = response_text.find("[")
    end = response_text.rfind("]")
    if start != -1 and end != -1 and end > start:
        candidate = response_text[start : end + 1]
        try:
            data = json.loads(candidate)
            return data if isinstance(data, list) else []
        except Exception as e:
            print("Error parsing extracted JSON: {}".format(e))
            print("Extracted snippet: {}...".format(candidate[:800]))
            return []

    print("Error parsing JSON response (no JSON array found).")
    print("Raw response (first 800 chars): {}...".format(response_text[:800]))
    return []


def is_transient_error_message(msg):
    m = msg.lower()
    return (
        ("504" in msg)
        or ("gateway timeout" in m)
        or ("cloudfront" in m)
        or ("internalservererror" in m)
        or ("502" in msg)
        or ("503" in msg)
        or ("server error" in m)
        or ("timed out" in m)
    )


def review_with_scout(prompt):
    try:
        import openai
    except ImportError:
        print("Error: openai library not installed. Run: pip install openai")
        sys.exit(1)

    if not SCOUT_API_KEY:
        print("Error: SCOUT_API_KEY not set")
        sys.exit(1)
    if not SCOUT_BASE_URL:
        print("Error: SCOUT_BASE_URL not set")
        sys.exit(1)

    client = openai.OpenAI(
        api_key=SCOUT_API_KEY,
        base_url=SCOUT_BASE_URL,
    )

    delays = [5, 15, 45, 90, 180]

    last_exc = None
    for attempt in range(SCOUT_RETRY_ATTEMPTS):
        try:
            response = client.chat.completions.create(
                model=SCOUT_MODEL,
                max_tokens=SCOUT_MAX_TOKENS,
                temperature=SCOUT_TEMPERATURE,
                messages=[{"role": "user", "content": prompt}],
            )
            text = response.choices[0].message.content or ""
            return parse_json_response(text)

        except Exception as e:
            last_exc = e
            msg = str(e)

            if attempt < SCOUT_RETRY_ATTEMPTS - 1 and is_transient_error_message(msg):
                wait = delays[attempt] if attempt < len(delays) else 60
                print("Transient error from Scout (attempt {}/{}). Will retry in {}s.".format(attempt + 1, SCOUT_RETRY_ATTEMPTS, wait))
                print("Error snippet: {}".format(msg[:220]))
                sleep_seconds(wait)
                continue

            # Not transient or out of retries
            raise

    # Shouldn't reach here, but just in case
    raise last_exc


# ---- commenting ----
def format_issue_comment(issue):
    severity_emoji = {"Critical": "🔴", "High": "🟠", "Medium": "🟡", "Low": "🔵"}
    emoji = severity_emoji.get(issue.get("severity"), "⚪")
    loc = "{}:{}".format(issue.get("file", ""), issue.get("line", ""))

    resources = ""
    res_list = issue.get("resources") or []
    if res_list:
        resources = "\n\nResources:\n" + "\n".join(["- {}".format(u) for u in res_list])

    lines = []
    lines.append("## {} Accessibility Issue: {}".format(emoji, issue.get("title", "")))
    lines.append("")
    lines.append("WCAG SC: {} (Level {})".format(issue.get("wcag_sc", ""), issue.get("wcag_level", "")))
    lines.append("Severity: {}".format(issue.get("severity", "")))
    lines.append("Location: `{}`".format(loc))
    lines.append("")
    lines.append("Issue:")
    lines.append(issue.get("description", ""))
    lines.append("")
    lines.append("Impact:")
    lines.append(issue.get("impact", ""))
    lines.append("")
    lines.append("Current code:")
    lines.append("```")
    lines.append(issue.get("current_code", ""))
    lines.append("```")
    lines.append("")
    lines.append("Suggested fix:")
    lines.append("```")
    lines.append(issue.get("suggested_fix", ""))
    lines.append("```")
    if resources:
        lines.append(resources)
    lines.append("")
    lines.append("---")
    lines.append("Automated by accessibility-fixer using Scout ({})".format(SCOUT_MODEL))
    return "\n".join(lines)


def post_summary_comment(issues, total_files):
    if not issues:
        summary_lines = [
            "## ✅ Accessibility Review Complete",
            "",
            "No accessibility issues found.",
            "",
            "Files reviewed: {}".format(total_files),
            "",
            "---",
            "Reviewed: {}".format(run_command('date -u +"%Y-%m-%d %H:%M UTC"')),
            "Powered by: Scout ({})".format(SCOUT_MODEL),
        ]
    else:
        critical = [i for i in issues if i.get("severity") == "Critical"]
        high = [i for i in issues if i.get("severity") == "High"]
        medium = [i for i in issues if i.get("severity") == "Medium"]
        low = [i for i in issues if i.get("severity") == "Low"]
        wcag_scs = list(set([i.get("wcag_sc") for i in issues if i.get("wcag_sc")]))

        summary_lines = [
            "## 🔍 Accessibility Review Summary",
            "",
            "Total Issues Found: {}".format(len(issues)),
            "- Critical: {}".format(len(critical)),
            "- High: {}".format(len(high)),
            "- Medium: {}".format(len(medium)),
            "- Low: {}".format(len(low)),
            "",
            "WCAG Success Criteria Affected:",
        ]
        for sc in wcag_scs[:12]:
            summary_lines.append("- {}".format(sc))

        summary_lines += [
            "",
            "Files reviewed: {}".format(total_files),
            "",
            "---",
            "Reviewed: {}".format(run_command('date -u +"%Y-%m-%d %H:%M UTC"')),
            "Powered by: Scout ({})".format(SCOUT_MODEL),
        ]

    summary = "\n".join(summary_lines)
    escaped = summary.replace('"', '\\"').replace("\n", "\\n").replace("$", "\\$")
    run_command('gh pr comment {} --body "{}"'.format(PR_NUMBER, escaped))


def post_issue_comments(issues):
    for issue in issues:
        comment = format_issue_comment(issue)
        escaped_comment = comment.replace('"', '\\"').replace("\n", "\\n")
        run_command('gh pr comment {} --body "{}"'.format(PR_NUMBER, escaped_comment))


def exit_code_for_issues(issues):
    if any(i.get("severity") == "Critical" for i in issues):
        return EXIT_CRITICAL_ISSUES
    if any(i.get("severity") == "High" for i in issues):
        return EXIT_HIGH_PRIORITY
    return EXIT_SUCCESS


# ---- main ----
def main():
    print("=" * 60)
    print("Scout PR Accessibility Review (split by file, retries, strict JSON)")
    print("=" * 60)

    if not PR_NUMBER:
        print("Error: PR_NUMBER not set")
        sys.exit(1)
    if not GITHUB_TOKEN:
        print("Error: GITHUB_TOKEN not set")
        sys.exit(1)
    if not SCOUT_API_KEY:
        print("Error: SCOUT_API_KEY not set")
        sys.exit(1)
    if not SCOUT_BASE_URL:
        print("Error: SCOUT_BASE_URL not set")
        sys.exit(1)

    print("Repo: {}".format(GITHUB_REPOSITORY))
    print("Framework path: {}".format(FRAMEWORK_PATH))
    print("Scout base URL: {}".format(SCOUT_BASE_URL))
    print("Model: {}".format(SCOUT_MODEL))
    print("Files per batch: {}".format(SCOUT_FILES_PER_BATCH))
    print("Max diff chars: {}".format(SCOUT_MAX_DIFF_CHARS))
    print("Max snippet lines: {}".format(SCOUT_MAX_SNIPPET_LINES))
    print("Retry attempts: {}".format(SCOUT_RETRY_ATTEMPTS))
    print("")

    files = get_pr_files()
    platforms = detect_platforms(files)

    print("Platforms: {}".format(", ".join(platforms) if platforms else "None detected"))
    print("Files changed: {}".format(len(files)))

    base_sha, head_sha = get_pr_base_head_shas()
    if not base_sha or not head_sha:
        print("Error: Could not determine base/head SHAs for diff splitting")
        sys.exit(1)

    print("Base SHA: {}".format(base_sha))
    print("Head SHA: {}".format(head_sha))
    print("")

    guides = load_guides(platforms)
    print("Loaded {} guide(s)".format(len(guides)))
    print("")

    all_issues = []
    batches = list(chunk_list(files, SCOUT_FILES_PER_BATCH))
    print("Splitting into {} batch(es)...".format(len(batches)))
    print("")

    for idx, batch in enumerate(batches, start=1):
        print("Batch {}/{}: reviewing {} file(s)".format(idx, len(batches), len(batch)))
        diff = get_diff_for_files(base_sha, head_sha, batch)

        if not diff.strip():
            print(" - Skipping (empty diff)")
            continue

        prompt = create_review_prompt(diff, batch, platforms, guides)

        try:
            raw_issues = review_with_scout(prompt) or []
        except Exception as e:
            # Do not fail the whole run on one file; log and continue
            print(" - ERROR reviewing batch {}: {}".format(idx, str(e)[:240]))
            print(" - Continuing to next batch.")
            continue

        normalized_batch_issues = []
        for it in raw_issues:
            n = normalize_issue(it)
            if n:
                normalized_batch_issues.append(n)

        print(" - Issues found in batch: {}".format(len(normalized_batch_issues)))
        all_issues.extend(normalized_batch_issues)

    issues = dedupe_issues(all_issues)
    print("")
    print("Aggregated issues (deduped): {}".format(len(issues)))

    if issues:
        print("Posting issue comments...")
        post_issue_comments(issues)
    else:
        print("No issues to post.")

    print("Posting summary comment...")
    post_summary_comment(issues, total_files=len(files))

    code = exit_code_for_issues(issues)
    if code == EXIT_CRITICAL_ISSUES:
        print("CRITICAL issues found - blocking merge")
    elif code == EXIT_HIGH_PRIORITY:
        print("HIGH priority issues found")
    else:
        print("Review complete - OK")

    sys.exit(code)


if __name__ == "__main__":
    main()
