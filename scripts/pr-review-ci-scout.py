#!/usr/bin/env python3
"""
Scout (OpenAI-compatible) Automated PR Accessibility Review Script

Env required:
- PR_NUMBER
- GITHUB_TOKEN
- FRAMEWORK_PATH (optional)
- GITHUB_REPOSITORY (optional)

Scout env:
- SCOUT_API_KEY
- SCOUT_BASE_URL  (OpenAI compatibility base url, must end with /v1)
- SCOUT_MODEL     (e.g. gpt-4-1-mini)

Optional:
- SCOUT_MAX_TOKENS (default 8000)
- SCOUT_TEMPERATURE (default 0)
"""

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
SCOUT_BASE_URL = os.environ.get("SCOUT_BASE_URL")  # ex: https://.../v1
SCOUT_MODEL = os.environ.get("SCOUT_MODEL", "gpt-4-1-mini")
SCOUT_MAX_TOKENS = int(os.environ.get("SCOUT_MAX_TOKENS", "8000"))
SCOUT_TEMPERATURE = float(os.environ.get("SCOUT_TEMPERATURE", "0"))

# Exit codes
EXIT_SUCCESS = 0
EXIT_CRITICAL_ISSUES = 1
EXIT_HIGH_PRIORITY = 2


def run_command(cmd, capture_output=True):
    """Run a shell command and return stdout (stripped)."""
    result = subprocess.run(
        cmd,
        shell=True,
        capture_output=capture_output,
        text=True,
    )
    return result.stdout.strip() if capture_output else None


def get_pr_diff():
    """Get the PR diff using GitHub CLI."""
    print(f"Fetching PR #{PR_NUMBER} diff...")
    return run_command(f"gh pr diff {PR_NUMBER}")


def get_pr_files():
    """Get list of changed files in PR."""
    print("Getting changed files...")
    files_json = run_command(f"gh pr view {PR_NUMBER} --json files")
    files_data = json.loads(files_json)
    return [f["path"] for f in files_data.get("files", [])]


def detect_platforms(files):
    """Detect which platforms are affected by file extensions."""
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


def load_guides(platforms):
    """Load relevant accessibility guides from framework."""
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


def create_review_prompt(pr_diff, files, platforms, guides):
    """Create the prompt for AI to review the PR."""
    guides_text = "\n\n".join([f"## {path}\n\n{content}" for path, content in guides.items()])
    files_list = "\n".join([f"- {f}" for f in files])
    platforms_list = ", ".join(platforms) if platforms else "Unknown"

    parts = []
    parts.append("You are performing an automated accessibility review on a GitHub Pull Request.\n")

    parts.append("# PR Information")
    parts.append(f"**Platforms detected:** {platforms_list}")
    parts.append(f"**Files changed:** {len(files)}")
    parts.append(files_list)
    parts.append("")

    parts.append("# Your Task")
    parts.append("Review ONLY the changed code in this PR for accessibility issues. Focus on:")
    parts.append("1. New UI components - accessibility labels, hints, roles")
    parts.append("2. Modified accessibility properties - ensure no regressions")
    parts.append("3. Interactive elements - buttons/links/inputs must be accessible")
    parts.append("4. Images/icons - alt text / content descriptions")
    parts.append("5. Text and labels - semantic structure and clarity")
    parts.append("6. Form inputs - labels, hints, error messages")
    parts.append("7. Touch targets - minimum size")
    parts.append("8. Contrast - text and UI elements")
    parts.append("")

    parts.append("# Guidelines to Follow")
    parts.append(guides_text)
    parts.append("")

    parts.append("# PR Diff")
    parts.append("```diff")
    parts.append(pr_diff)
    parts.append("```")
    parts.append("")

    parts.append("# Output Format")
    parts.append("Provide your review as a JSON array of issues. Each issue should have:")
    parts.append("")
    parts.append("{")
    parts.append('  "file": "path/to/file.ext",')
    parts.append('  "line": 123,')
    parts.append('  "severity": "Critical|High|Medium|Low",')
    parts.append('  "wcag_sc": "X.X.X - Name",')
    parts.append('  "wcag_level": "A|AA|AAA",')
    parts.append('  "title": "Brief title",')
    parts.append('  "description": "Detailed description",')
    parts.append('  "impact": "Who is affected and how",')
    parts.append('  "current_code": "code snippet",')
    parts.append('  "suggested_fix": "corrected code snippet",')
    parts.append('  "resources": ["URL1", "URL2"]')
    parts.append("}")
    parts.append("")
    parts.append("IMPORTANT:")
    parts.append("- Only report issues found in the CHANGED code")
    parts.append("- Do NOT report issues in unchanged code")
    parts.append("- Focus on accessibility only")
    parts.append("- Be specific with file paths and line numbers")
    parts.append("- Provide actionable fixes")
    parts.append("- If no issues found, return empty array: []")

    return "\n".join(parts)


def parse_json_response(response_text):
    """Parse JSON from AI response (might be wrapped in markdown)."""
    if "```json" in response_text:
        start = response_text.find("```json") + 7
        end = response_text.find("```", start)
        response_text = response_text[start:end].strip()
    elif "```" in response_text:
        start = response_text.find("```") + 3
        end = response_text.find("```", start)
        response_text = response_text[start:end].strip()

    try:
        return json.loads(response_text)
    except json.JSONDecodeError as e:
        print(f"Error parsing JSON response: {e}")
        print(f"Response was: {response_text[:800]}...")
        return []


def review_pr_with_scout(prompt):
    """Send review request to Scout endpoint (OpenAI-compatible)."""
    try:
        import openai
    except ImportError:
        print("Error: openai library not installed. Run: pip install openai")
        sys.exit(1)

    if not SCOUT_API_KEY:
        print("Error: SCOUT_API_KEY not set")
        sys.exit(1)

    if not SCOUT_BASE_URL:
        print("Error: SCOUT_BASE_URL not set (must end with /v1)")
        sys.exit(1)

    print("Analyzing with Scout (OpenAI-compatible)...")
    print(f"Base URL: {SCOUT_BASE_URL}")
    print(f"Model: {SCOUT_MODEL}")

    client = openai.OpenAI(
        api_key=SCOUT_API_KEY,
        base_url=SCOUT_BASE_URL,
    )

    try:
        response = client.chat.completions.create(
            model=SCOUT_MODEL,
            max_tokens=SCOUT_MAX_TOKENS,
            temperature=SCOUT_TEMPERATURE,
            messages=[{"role": "user", "content": prompt}],
        )

        response_text = response.choices[0].message.content or ""
        return parse_json_response(response_text)

    except Exception as e:
        print(f"Error calling Scout endpoint: {e}")
        sys.exit(1)


def format_issue_comment(issue):
    """Format an issue as a GitHub comment."""
    severity_emoji = {
        "Critical": "🔴",
        "High": "🟠",
        "Medium": "🟡",
        "Low": "🔵",
    }

    emoji = severity_emoji.get(issue.get("severity"), "⚪")

    resources = ""
    if issue.get("resources"):
        resources = "\n\n**Resources:**\n" + "\n".join([f"- {url}" for url in issue["resources"]])

    return f"""## {emoji} Accessibility Issue: {issue['title']}

**WCAG SC:** {issue['wcag_sc']} (Level {issue['wcag_level']})
**Severity:** {issue['severity']}
**Location:** `{issue['file']}:{issue['line']}`

**Issue:**
{issue['description']}

**Impact:**
{issue['impact']}

**Current code:**
