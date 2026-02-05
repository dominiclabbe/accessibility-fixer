"""
PR Reviewer

Core accessibility review logic using Scout AI and accessibility guides.
Adapted from scripts/pr-review-ci-scout.py for GitHub App context.
"""

import os
import json
import time
import hashlib
from typing import List, Dict, Optional, Tuple
from pathlib import Path

try:
    import openai
except ImportError:
    raise ImportError("openai library required. Install: pip install openai")

from app.diff_parser import (
    DiffParser,
    validate_issues_in_batch,
    is_no_issues_placeholder,
)


class PRReviewer:
    """Reviews PRs for accessibility issues using Scout AI."""

    def __init__(
        self,
        scout_api_key: str,
        scout_base_url: str,
        scout_model: str = "gpt-5.2",
        max_tokens: int = 2500,
        temperature: float = 0.0,
        files_per_batch: int = 1,
        max_diff_chars: int = 180000,
        max_snippet_lines: int = 30,
        retry_attempts: int = 4,
    ):
        """
        Initialize PR reviewer.

        Args:
            scout_api_key: Scout API key
            scout_base_url: Scout base URL
            scout_model: Model name
            max_tokens: Max tokens per request
            temperature: Temperature for AI
            files_per_batch: Files per batch (1 = per-file)
            max_diff_chars: Max diff characters per request
            max_snippet_lines: Max lines in code snippets
            retry_attempts: Number of retry attempts
        """
        self.client = openai.OpenAI(api_key=scout_api_key, base_url=scout_base_url)
        self.model = scout_model
        self.max_tokens = max_tokens
        self.temperature = temperature
        self.files_per_batch = files_per_batch
        self.max_diff_chars = max_diff_chars
        self.max_snippet_lines = max_snippet_lines
        self.retry_attempts = retry_attempts

    def review_pr_diff(
        self,
        pr_diff: str,
        changed_files: List[str],
        platforms: List[str],
        guides: str,
        on_batch_complete=None,
        existing_comments: Optional[List[Tuple[str, int]]] = None,
        review_threads: Optional[List[Dict]] = None,
    ) -> List[Dict]:
        """
        Review PR diff for accessibility issues.

        Args:
            pr_diff: Git diff string
            changed_files: List of changed file paths
            platforms: Detected platforms (e.g., ['android', 'ios'])
            guides: Combined accessibility guides
            on_batch_complete: Optional callback(issues) called after each batch
            existing_comments: List of (file_path, line) tuples for existing comments
            review_threads: List of review thread objects including replies for validation

        Returns:
            List of accessibility issues
        """
        # Split into batches if needed
        batches = list(self._chunk_list(changed_files, self.files_per_batch))

        all_issues = []
        batch_size_for_posting = 5  # Post every 5 batches

        # DEBUG_WEB_REVIEW: Track web files in batches
        debug_web_review = os.getenv("DEBUG_WEB_REVIEW", "").lower() in ["1", "true", "yes"]
        web_extensions = {".tsx", ".jsx", ".ts", ".js", ".html", ".css"}

        for batch_idx, file_batch in enumerate(batches):
            print(
                f"  Reviewing batch {batch_idx + 1}/{len(batches)} ({len(file_batch)} files)..."
            )

            # Get diff for this batch using proper diff parser
            batch_diff = DiffParser.filter_diff_for_files(pr_diff, file_batch)
            if not batch_diff:
                print(f"  No diff content for batch {batch_idx + 1}, skipping")
                continue

            # Truncate if too large
            original_diff_size = len(batch_diff)
            if len(batch_diff) > self.max_diff_chars:
                batch_diff = (
                    batch_diff[: self.max_diff_chars]
                    + "\n\n# [TRUNCATED] Diff exceeded max characters.\n"
                )

            # Extract commentable lines for validation
            commentable_lines = DiffParser.extract_commentable_lines(batch_diff)

            # DEBUG_WEB_REVIEW: Log batch composition and commentable lines
            if debug_web_review:
                web_files_in_batch = [f for f in file_batch if any(f.endswith(ext) for ext in web_extensions)]
                print(f"[DEBUG_WEB_REVIEW] Batch {batch_idx + 1}/{len(batches)}:")
                print(f"  Files in batch: {file_batch}")
                print(f"  Web files in batch: {web_files_in_batch}")
                print(f"  Diff size: {original_diff_size} chars (truncated: {len(batch_diff) < original_diff_size})")
                
                # Log commentable lines per file
                for file_path in file_batch:
                    file_commentable = commentable_lines.get(file_path, {})
                    print(f"  Commentable lines for {file_path}:")
                    print(f"    Total commentable lines: {len(file_commentable)}")
                    if file_commentable:
                        print(f"    Line range: {min(file_commentable.keys())} - {max(file_commentable.keys())}")

            # Create prompt
            prompt = self._create_review_prompt(
                batch_diff,
                file_batch,
                platforms,
                guides,
                existing_comments,
                review_threads,
            )

            # Call Scout AI
            raw_issues = self._review_with_scout(prompt)

            # DEBUG_WEB_REVIEW: Log raw issues from LLM
            if debug_web_review:
                print(f"[DEBUG_WEB_REVIEW] Raw issues from LLM (batch {batch_idx + 1}):")
                print(f"  Total raw issues: {len(raw_issues)}")
                
                # Group by file
                issues_by_file = {}
                for issue in raw_issues:
                    file_path = issue.get("file", "unknown")
                    if file_path not in issues_by_file:
                        issues_by_file[file_path] = []
                    issues_by_file[file_path].append(issue)
                
                # Log grouped issues
                for file_path, file_issues in issues_by_file.items():
                    is_web = any(file_path.endswith(ext) for ext in web_extensions)
                    print(f"  {file_path} ({'WEB' if is_web else 'NON-WEB'}): {len(file_issues)} issues")
                    for idx, issue in enumerate(file_issues, 1):
                        line = issue.get("line", "?")
                        title = issue.get("title", "")[:60]
                        print(f"    [{idx}] Line {line}: {title}")
                
                # Count web vs non-web issues
                web_issue_count = sum(
                    len(issues_by_file.get(f, []))
                    for f in web_files_in_batch
                )
                total_issues = len(raw_issues)
                print(f"  Web issues: {web_issue_count}/{total_issues}")

            # Filter out "no issues" placeholders
            raw_issues = [
                issue for issue in raw_issues if not is_no_issues_placeholder(issue)
            ]

            # Normalize issues
            normalized_issues = []
            for issue in raw_issues:
                normalized = self._normalize_issue(issue)
                if normalized:
                    normalized_issues.append(normalized)

            # Validate issues are in batch and on commentable lines
            # Pass batch_diff for semantic anchor resolution
            validated_issues = validate_issues_in_batch(
                normalized_issues, file_batch, commentable_lines, batch_diff
            )

            # Add validated issues to results
            all_issues.extend(validated_issues)

            # Post comments progressively every N batches
            if (
                on_batch_complete
                and len(all_issues) > 0
                and (batch_idx + 1) % batch_size_for_posting == 0
            ):
                # Deduplicate current batch
                deduped = self._dedupe_issues(all_issues)
                if deduped:
                    on_batch_complete(deduped)
                    all_issues = []  # Clear posted issues

        # Post any remaining issues
        if on_batch_complete and len(all_issues) > 0:
            deduped = self._dedupe_issues(all_issues)
            if deduped:
                on_batch_complete(deduped)
            return []  # Already posted

        # If no callback, return all issues (existing behavior)
        return self._dedupe_issues(all_issues)

    def _create_review_prompt(
        self,
        pr_diff: str,
        files_in_batch: List[str],
        platforms: List[str],
        guides: str,
        existing_comments: Optional[List[Tuple[str, int]]] = None,
        review_threads: Optional[List[Dict]] = None,
    ) -> str:
        """Create review prompt for Scout AI."""
        files_list = "\n".join([f"- {f}" for f in files_in_batch])
        platforms_list = ", ".join(platforms) if platforms else "Unknown"

        parts = [
            "You are performing an automated accessibility review on a GitHub Pull Request.",
            "",
            "# PR Information",
            f"Platforms detected: {platforms_list}",
            f"Files in this batch: {len(files_in_batch)}",
            files_list,
            "",
        ]

        # Add existing comments section if provided
        if existing_comments:
            parts.extend(
                [
                    "# Existing Comments",
                    "The following locations already have accessibility comments posted:",
                    "",
                ]
            )
            for entry in existing_comments:
                # Handle different entry shapes for backward compatibility
                file_path = None
                line_num = None

                if isinstance(entry, dict):
                    # Dict entry: {'file': ..., 'line': ...} or {'path': ..., 'line': ...}
                    file_path = entry.get("file") or entry.get("path")
                    line_num = entry.get("line")
                elif isinstance(entry, (list, tuple)):
                    # Tuple/list entry: (file_path, line_num, ...) - use first two
                    if len(entry) >= 2:
                        file_path = entry[0]
                        line_num = entry[1]
                else:
                    # Unsupported shape - skip gracefully
                    continue

                # Only add if we have both values (explicit None checks to handle line 0)
                if file_path is not None and line_num is not None:
                    parts.append(f"- {file_path}:{line_num}")

            parts.extend(
                [
                    "",
                    "IMPORTANT: Do NOT report issues at these locations or within 5 lines of them.",
                    "These issues have already been identified and commented on.",
                    "",
                ]
            )

        # Add review threads with replies for resolution validation
        if review_threads:
            parts.extend(
                [
                    "# Previous Review Discussions",
                    "Below are previous accessibility comments and their discussion threads.",
                    "Your job is to:",
                    "1. Check if issues mentioned in these threads are actually fixed in the current diff",
                    "2. If someone replied 'resolved' or 'fixed' but the code still has the issue, CHALLENGE IT",
                    "3. If the resolution was insufficient (e.g., 'wontfix' without good reason), POST A FOLLOW-UP",
                    "",
                ]
            )

            for thread in review_threads:
                if thread.get(
                    "replies"
                ):  # Only show threads with replies (discussions)
                    parts.append(f"## Thread: {thread['path']}:{thread['line']}")
                    parts.append(f"**Original Comment by @{thread['user']}:**")
                    parts.append(thread["body"][:500])  # Truncate long comments
                    parts.append("")

                    if thread.get("replies"):
                        parts.append("**Replies:**")
                        for reply in thread["replies"][:5]:  # Max 5 replies per thread
                            parts.append(f"- @{reply['user']}: {reply['body'][:300]}")
                        parts.append("")

            parts.extend(
                [
                    "",
                    "**Resolution Validation Task:**",
                    "- If any discussed issue STILL EXISTS in the current diff, report it again with context",
                    "- If someone claimed to fix it but didn't, call it out: 'Previously marked resolved but issue persists'",
                    "- Be respectful but firm about accessibility requirements",
                    "",
                ]
            )

        parts.extend(
            [
                "# Task",
                "Review ONLY the changed code in this diff for accessibility issues.",
                "Focus on labels/hints/roles, interactive elements, images/icons alt text, form inputs, touch targets, Dynamic Type/font scaling, semantics, and contrast.",
                "",
                "# CRITICAL: Issue Consolidation",
                "BEFORE reporting issues, consolidate similar/related issues that are close together:",
                "- If multiple UI elements within 5 lines have the SAME problem (e.g., all missing labels), report ONE issue that mentions all affected elements",
                "- Example: Instead of 2 separate comments for 'Button on line 15 missing label' and 'Button on line 19 missing label',",
                "  Report ONE: 'Multiple buttons missing labels (lines 15, 19)'",
                "- Choose the FIRST line number as the location when consolidating",
                "- Only consolidate issues that are IDENTICAL in nature (same WCAG SC, same fix)",
                "- Do NOT consolidate issues that are different even if they're close together",
                "",
                "# Guidelines",
                guides,
                "",
                "# PR Diff (Batch Only)",
                "```diff",
                pr_diff,
                "```",
                "",
                "# CRITICAL: Line Number Accuracy",
                "Getting the EXACT line number is CRITICAL for inline comments to appear at the right location.",
                "",
                "How to count line numbers in diffs:",
                "1. Find the hunk header: '@@ -old_start,old_count +NEW_START,new_count @@'",
                "2. The +NEW_START is the line number for the FIRST LINE after the header",
                "3. Count EVERY line that starts with '+' or ' ' (space) from that point",
                "4. Lines starting with '-' do NOT count (they're removed lines)",
                "",
                "Example:",
                "```",
                "@@ -10,5 +25,8 @@ function MyComponent() {",
                " export function Button() {           // Line 25 (NEW_START)",
                "+  const [state, setState] = useState() // Line 26 (+ means added)",
                "   return (",
                "-    <button>                          // DON'T COUNT (- means removed)",
                "+    <button                           // Line 27",
                "+      onClick=",
                "{...}                 // Line 28",
                "+    >                                  // Line 29",
                "       Click                            // Line 30",
                "     </button>",
                "   )",
                " }",
                "```",
                "",
                "Report the line number where the PROBLEMATIC CODE actually appears.",
                "NOT the function name, NOT the component name, but the EXACT line with the issue.",
                "",
                "# Output Format (STRICT)",
                "Return ONLY a valid JSON array. No markdown. No prose. No code fences.",
                "If no issues found, return: []",
                "",
                "Each issue must have these keys (all values MUST be strings, except line which must be a number):",
                'file, line, severity ("Critical|High|Medium|Low"), wcag_sc, wcag_level, title, description, impact, current_code, suggested_fix, resources.',
                "",
                "OPTIONAL field (highly recommended for accurate inline comment placement):",
                "- anchor_text: An exact substring/line from the diff that identifies WHERE to place the comment.",
                "  This should be the EXACT code line to comment on (e.g., 'Slider(', 'Toggle(\"Enable\", isOn:', '<input type=\"range\"', 'android:contentDescription=', '.clickable {', '<Button').",
                "  Choose the specific UI call/declaration line and ensure it exists in the diff shown above.",
                "  If provided, this helps ensure the comment appears at the precise UI element line.",
                "",
                "Rules:",
                "- Report issues ONLY in the CHANGED code shown in this batch diff.",
            ]
        )

        # Add rule about existing comments if any exist
        if existing_comments:
            parts.append(
                "- Do NOT report issues at locations that already have comments (or within 5 lines of them)."
            )

        parts.extend(
            [
                "- CONSOLIDATE identical issues within 5 lines into ONE comment mentioning all affected lines.",
                "- The 'line' field MUST be the EXACT line number in the NEW file where the issue occurs (not a guess or range).",
                "- Count carefully from the '@@ ... +START ...' marker to get the correct line number.",
                "- Point to the specific line with the problem (e.g., the line with contentDescription=null, not the function declaration).",
                "- wcag_sc MUST be a single string. If multiple SC apply, join with '; '.",
                f"- current_code and suggested_fix must be short snippets (max {self.max_snippet_lines} lines each).",
                "- resources MUST be an array of strings (or empty array []).",
            ]
        )

        return "\n".join(parts)

    def _review_with_scout(self, prompt: str) -> List[Dict]:
        """Call Scout API with retry logic."""
        delays = [5, 15, 45, 90, 180]
        last_exc = None

        for attempt in range(self.retry_attempts):
            try:
                response = self.client.chat.completions.create(
                    model=self.model,
                    max_tokens=self.max_tokens,
                    temperature=self.temperature,
                    messages=[{"role": "user", "content": prompt}],
                )
                text = response.choices[0].message.content or ""
                return self._parse_json_response(text)

            except Exception as e:
                last_exc = e
                msg = str(e)

                if attempt < self.retry_attempts - 1 and self._is_transient_error(msg):
                    wait = delays[attempt] if attempt < len(delays) else 60
                    print(
                        f"  Transient error (attempt {attempt + 1}/{self.retry_attempts}). "
                        f"Retrying in {wait}s..."
                    )
                    print(f"  Error: {msg[:200]}")
                    time.sleep(wait)
                    continue

                # Not transient or out of retries
                raise

        raise last_exc

    def _parse_json_response(self, response_text: str) -> List[Dict]:
        """Parse JSON response from Scout AI."""
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
                print(f"Error parsing extracted JSON: {e}")
                print(f"Extracted snippet: {candidate[:800]}...")
                return []

        print("Error parsing JSON response (no JSON array found).")
        print(f"Raw response (first 800 chars): {response_text[:800]}...")
        return []

    def _normalize_issue(self, issue: Dict) -> Optional[Dict]:
        """Normalize issue to consistent schema."""
        if not isinstance(issue, dict):
            return None

        normalized = dict(issue)

        # wcag_sc sometimes comes as list; convert to string
        wcag_sc = normalized.get("wcag_sc", "")
        if isinstance(wcag_sc, list):
            normalized["wcag_sc"] = "; ".join([str(x) for x in wcag_sc])
        elif wcag_sc is None:
            normalized["wcag_sc"] = ""
        else:
            normalized["wcag_sc"] = str(wcag_sc)

        # Ensure wcag_level is string
        wcag_level = normalized.get("wcag_level", "")
        normalized["wcag_level"] = "" if wcag_level is None else str(wcag_level)

        # Ensure other fields are strings
        for k in ["file", "severity", "title", "description", "impact"]:
            v = normalized.get(k, "")
            normalized[k] = "" if v is None else str(v)

        # line should be int
        line = normalized.get("line", 0)
        try:
            normalized["line"] = int(line)
        except Exception:
            normalized["line"] = 0

        # resources should be list of strings
        resources = normalized.get("resources", [])
        if resources is None:
            resources = []
        if isinstance(resources, str):
            resources = [resources]
        if not isinstance(resources, list):
            resources = []
        normalized["resources"] = [str(x) for x in resources]

        # Clamp code snippets
        normalized["current_code"] = self._clamp_lines(
            normalized.get("current_code", ""), self.max_snippet_lines
        )
        normalized["suggested_fix"] = self._clamp_lines(
            normalized.get("suggested_fix", ""), self.max_snippet_lines
        )

        return normalized

    def _dedupe_issues(self, issues: List[Dict]) -> List[Dict]:
        """
        Remove duplicate issues using fingerprinting.

        Uses a stable fingerprint based on:
        - File path
        - WCAG SC (normalized)
        - Title (normalized)
        - Line number (with tolerance for near-duplicates)

        This prevents duplicate issues while allowing different issues
        at the same location.
        """
        seen_fingerprints = set()
        out = []
        
        # Track dedupe drops for DEBUG_WEB_REVIEW
        debug_web_review = os.getenv("DEBUG_WEB_REVIEW", "").lower() in ["1", "true", "yes"]
        dedupe_drops = []

        for issue in issues:
            fingerprint = self._compute_issue_fingerprint(issue)

            if fingerprint not in seen_fingerprints:
                seen_fingerprints.add(fingerprint)
                out.append(issue)
            else:
                file_path = issue.get("file", "")
                line = issue.get("line", 0)
                title = issue.get("title", "")
                print(f"  Skipping duplicate: {file_path}:{line} - {title[:50]}")
                
                if debug_web_review:
                    dedupe_drops.append({
                        "file": file_path,
                        "line": line,
                        "title": title[:60],
                        "fingerprint": fingerprint,
                        "reason": "duplicate fingerprint"
                    })

        # DEBUG_WEB_REVIEW: Log dedupe drops
        if debug_web_review and dedupe_drops:
            print("\n[DEBUG_WEB_REVIEW] Deduplication drops:")
            for drop in dedupe_drops:
                print(f"  {drop['file']}:{drop['line']} - {drop['reason']}")
                print(f"    Title: {drop['title']}")
                print(f"    Fingerprint: {drop['fingerprint']}")

        return out

    @staticmethod
    def _compute_issue_fingerprint(issue: Dict) -> str:
        """
        Compute a stable fingerprint for an issue.

        Includes anchor signature derived from resolved anchor text or matched line
        to improve dedupe accuracy and prevent rerun duplicates.

        Args:
            issue: Issue dict

        Returns:
            Fingerprint string
        """
        # Normalize components
        file_path = str(issue.get("file", "")).strip()
        line = issue.get("line", 0)

        # Normalize line to nearest 5 to catch near-duplicates
        # (e.g., line 42 and 44 would both map to 40)
        line_bucket = (line // 5) * 5

        # Normalize WCAG SC (remove spaces, lowercase, take first if multiple)
        wcag_sc = str(issue.get("wcag_sc", "")).strip().lower()
        if ";" in wcag_sc:
            wcag_sc = wcag_sc.split(";")[0].strip()
        wcag_sc = wcag_sc.replace(" ", "")

        # Normalize title (lowercase, remove extra whitespace)
        title = str(issue.get("title", "")).strip().lower()
        title = " ".join(title.split())  # Normalize whitespace

        # Truncate title to first 50 chars for fingerprint
        title_key = title[:50]

        # Add anchor signature if available
        # This improves dedupe by including the actual code line that was matched
        anchor_sig = ""
        if issue.get("_anchor_matched_text"):
            # Use matched text from anchor resolution
            matched = str(issue.get("_anchor_matched_text", "")).strip()
            # Normalize: remove whitespace, lowercase, take first 40 chars
            anchor_sig = "".join(matched.split()).lower()[:40]
        elif issue.get("anchor_text"):
            # Use explicit anchor_text from model
            anchor = str(issue.get("anchor_text", "")).strip()
            anchor_sig = "".join(anchor.split()).lower()[:40]

        # Build fingerprint with anchor signature if available
        if anchor_sig:
            fingerprint_str = (
                f"{file_path}|{line_bucket}|{wcag_sc}|{title_key}|{anchor_sig}"
            )
        else:
            fingerprint_str = f"{file_path}|{line_bucket}|{wcag_sc}|{title_key}"

        # Hash for consistent length
        return hashlib.md5(fingerprint_str.encode()).hexdigest()

    @staticmethod
    def _clamp_lines(text: str, max_lines: int) -> str:
        """Clamp text to max lines."""
        if not isinstance(text, str):
            return ""
        lines = text.splitlines()
        if len(lines) <= max_lines:
            return text
        return "\n".join(lines[:max_lines]) + "\n... [truncated]"

    @staticmethod
    def _chunk_list(items: List, size: int) -> List[List]:
        """Split list into chunks."""
        if size <= 0:
            size = 1
        for i in range(0, len(items), size):
            yield items[i : i + size]

    @staticmethod
    def _is_transient_error(msg: str) -> bool:
        """Check if error is transient and should be retried."""
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

    @staticmethod
    def detect_platforms(files: List[str]) -> List[str]:
        """Detect platforms from file extensions."""
        platforms = set()
        for file_path in files:
            ext = Path(file_path).suffix.lower()

            if ext in [".swift", ".m", ".mm"]:
                platforms.add("iOS")
            elif ext in [".kt", ".java"]:
                platforms.add("Android")
            elif ext in [".tsx", ".jsx", ".ts", ".js", ".html", ".css"]:
                platforms.add("Web")
            elif ext == ".dart":
                platforms.add("Flutter")

        return list(platforms) if platforms else ["Web"]


def create_reviewer_from_env() -> Optional[PRReviewer]:
    """
    Create PRReviewer from environment variables.

    Required env vars:
        SCOUT_API_KEY: Scout API key
        SCOUT_BASE_URL: Scout base URL

    Optional env vars:
        SCOUT_MODEL: Model name (default: gpt-5.2)
        SCOUT_MAX_TOKENS: Max tokens (default: 2500)
        SCOUT_TEMPERATURE: Temperature (default: 0.0)
        SCOUT_FILES_PER_BATCH: Files per batch (default: 1)
        SCOUT_MAX_DIFF_CHARS: Max diff chars (default: 180000)
        SCOUT_MAX_SNIPPET_LINES: Max snippet lines (default: 30)
        SCOUT_RETRY_ATTEMPTS: Retry attempts (default: 4)

    Returns:
        PRReviewer instance or None if env vars not set
    """
    scout_api_key = os.getenv("SCOUT_API_KEY")
    scout_base_url = os.getenv("SCOUT_BASE_URL")

    if not scout_api_key or not scout_base_url:
        return None

    return PRReviewer(
        scout_api_key=scout_api_key,
        scout_base_url=scout_base_url,
        scout_model=os.getenv("SCOUT_MODEL", "gpt-5.2"),
        max_tokens=int(os.getenv("SCOUT_MAX_TOKENS", "2500")),
        temperature=float(os.getenv("SCOUT_TEMPERATURE", "0.0")),
        files_per_batch=int(os.getenv("SCOUT_FILES_PER_BATCH", "1")),
        max_diff_chars=int(os.getenv("SCOUT_MAX_DIFF_CHARS", "180000")),
        max_snippet_lines=int(os.getenv("SCOUT_MAX_SNIPPET_LINES", "30")),
        retry_attempts=int(os.getenv("SCOUT_RETRY_ATTEMPTS", "4")),
    )
