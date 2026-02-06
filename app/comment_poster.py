"""
PR Comment Poster

Posts inline review comments and commit statuses to GitHub PRs.
"""

import os
import subprocess
import requests
from typing import List, Dict, Optional


def get_app_version() -> str:
    """
    Get application version/git SHA for debug footer.

    Priority:
    1. ACCESSIBILITY_FIXER_VERSION env var
    2. git rev-parse --short HEAD
    3. "unknown" fallback

    Returns:
        Short git SHA or version string
    """
    # Try env var override first
    env_version = os.getenv("ACCESSIBILITY_FIXER_VERSION")
    if env_version:
        return env_version

    # Try git command
    try:
        # Get repository root (two levels up from this file)
        repo_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

        result = subprocess.run(
            ["git", "rev-parse", "--short", "HEAD"],
            capture_output=True,
            text=True,
            timeout=2,
            cwd=repo_root,
        )
        if result.returncode == 0:
            return result.stdout.strip()
    except Exception:
        pass

    return "unknown"


def get_debug_footer(reviewer_config: Optional[Dict] = None) -> str:
    """
    Generate debug footer for review summary.

    Args:
        reviewer_config: Optional dict with reviewer configuration
                        (model, files_per_batch, max_diff_chars, etc.)

    Returns:
        Debug footer string in format:
        ---
        _debug: accessibility-fixer@<sha> model=<model> files_per_batch=<n> ..._
    """
    version = get_app_version()

    parts = [f"accessibility-fixer@{version}"]

    if reviewer_config:
        # Add model info
        model = reviewer_config.get("model")
        if model is None:
            model = os.getenv("SCOUT_MODEL", "unknown")
        parts.append(f"model={model}")

        # Add base URL/provider if available
        base_url = reviewer_config.get("base_url")
        if base_url is None:
            base_url = os.getenv("SCOUT_BASE_URL", "")
        if base_url:
            # Extract just the domain for brevity
            try:
                if "://" in base_url:
                    # Split on :// and then on / to get domain
                    url_parts = base_url.split("://", 1)
                    if len(url_parts) > 1:
                        domain = url_parts[1].split("/")[0]
                        parts.append(f"provider={domain}")
            except Exception:
                # Skip provider if URL parsing fails
                pass

        # Add key runtime settings
        files_per_batch = reviewer_config.get("files_per_batch")
        if files_per_batch is None:
            files_per_batch = os.getenv("SCOUT_FILES_PER_BATCH", "1")
        parts.append(f"files_per_batch={files_per_batch}")

        max_diff_chars = reviewer_config.get("max_diff_chars")
        if max_diff_chars is None:
            max_diff_chars = os.getenv("SCOUT_MAX_DIFF_CHARS", "180000")
        parts.append(f"max_diff_chars={max_diff_chars}")

        # Check if SARIF is enabled
        sarif_enabled = os.getenv("OUTPUT_SARIF", "").lower() in ["1", "true", "yes"]
        if sarif_enabled:
            parts.append("sarif=enabled")

    return f"\n\n---\n_debug: {' '.join(parts)}_"


class CommentPoster:
    """Posts accessibility issues as PR review comments."""

    def __init__(
        self,
        github_api_url: str = "https://api.github.com",
        reviewer_config: Optional[Dict] = None,
    ):
        """
        Initialize comment poster.

        Args:
            github_api_url: GitHub API base URL
            reviewer_config: Optional reviewer configuration for debug footer
        """
        self.github_api_url = github_api_url
        self.reviewer_config = reviewer_config

    def post_review_comments(
        self,
        repo_owner: str,
        repo_name: str,
        pr_number: int,
        commit_sha: str,
        issues: List[Dict],
        headers: Dict[str, str],
        event: str = "COMMENT",
        skip_existing_check: bool = False,
        is_final: bool = True,
        current_phase: Optional[int] = None,
        total_phases: Optional[int] = None,
    ) -> bool:
        """
        Post review comments for accessibility issues.

        Args:
            repo_owner: Repository owner
            repo_name: Repository name
            pr_number: PR number
            commit_sha: Commit SHA to review
            issues: List of accessibility issues
            headers: Headers with authorization token
            event: Review event type (COMMENT, REQUEST_CHANGES, APPROVE)
            skip_existing_check: Skip checking for existing comments
            is_final: Whether this is the final review (default: True)
            current_phase: Current phase number for in-progress message (optional)
            total_phases: Total number of phases for in-progress message (optional)

        Returns:
            True if successful, False otherwise
        """
        if not issues:
            print("No issues to post")
            return True

        # Fetch existing review comments to avoid re-posting (unless already done by caller)
        if skip_existing_check:
            existing_locations = set()
        else:
            existing_locations = self._get_existing_comment_locations(
                repo_owner, repo_name, pr_number, headers
            )
            print(f"Found {len(existing_locations)} existing comment locations")

        # Build review comments with enhanced deduplication
        comments = []
        seen_locations = set()

        for issue in issues:
            comment = self._format_inline_comment(issue)
            if comment:
                location_key = (comment["path"], comment["line"])

                # Extract title from issue for matching
                issue_title = issue.get("title", "")[:50].strip()

                # Check if similar comment already exists
                # Match by location AND title to handle anchor-based duplicates
                is_duplicate = False
                for existing_path, existing_line, existing_title in existing_locations:
                    if existing_path == comment["path"]:
                        # Check if line numbers are close (within 5 lines) and titles match
                        line_distance = abs(existing_line - comment["line"])
                        if line_distance <= 5 and existing_title == issue_title:
                            print(
                                f"Skipping existing comment at {comment['path']}:{comment['line']} (similar to {existing_line})"
                            )
                            is_duplicate = True
                            break

                if is_duplicate:
                    continue

                # Skip if duplicate in this batch
                if location_key in seen_locations:
                    print(
                        f"Skipping duplicate comment at {comment['path']}:{comment['line']}"
                    )
                    continue

                comments.append(comment)
                seen_locations.add(location_key)

        if not comments:
            print("No valid comments to post")
            return True

        # Build review body
        severity_counts = self._count_severities(issues)
        review_body = self._format_review_summary(
            severity_counts,
            is_final=is_final,
            current_phase=current_phase,
            total_phases=total_phases,
        )

        # Determine event based on severities
        if event == "COMMENT" and severity_counts.get("critical", 0) > 0:
            event = "REQUEST_CHANGES"

        # Post review
        url = f"{self.github_api_url}/repos/{repo_owner}/{repo_name}/pulls/{pr_number}/reviews"

        payload = {
            "commit_id": commit_sha,
            "body": review_body,
            "event": event,
            "comments": comments,
        }

        try:
            response = requests.post(url, json=payload, headers=headers)
            response.raise_for_status()

            print(f"✅ Posted review with {len(comments)} comments")
            return True

        except requests.exceptions.HTTPError as e:
            # Handle 422 errors (invalid line numbers) with fallback
            if e.response and e.response.status_code == 422:
                print(f"⚠️  422 Error posting review (likely invalid line numbers)")
                print(f"Response: {e.response.text}")

                # Try posting as non-inline comments instead
                print("Attempting fallback: posting as non-inline PR comments...")
                return self._post_as_fallback_comments(
                    repo_owner, repo_name, pr_number, issues, headers
                )

            print(f"❌ Error posting review: {e}")
            print(f"Response: {e.response.text if e.response else 'No response'}")
            return False

    def _post_as_fallback_comments(
        self,
        repo_owner: str,
        repo_name: str,
        pr_number: int,
        issues: List[Dict],
        headers: Dict[str, str],
    ) -> bool:
        """
        Post issues as non-inline PR comments when inline posting fails.

        Args:
            repo_owner: Repository owner
            repo_name: Repository name
            pr_number: PR number
            issues: List of issues that failed to post inline
            headers: Headers with authorization

        Returns:
            True if successful, False otherwise
        """
        # Group issues by file for cleaner output
        issues_by_file = {}
        for issue in issues:
            file_path = issue.get("file", "unknown")
            if file_path not in issues_by_file:
                issues_by_file[file_path] = []
            issues_by_file[file_path].append(issue)

        # Build comment body
        body_parts = [
            "## ⚠️ Accessibility Review (Fallback Mode)",
            "",
            "The following accessibility issues were found but could not be posted as inline comments.",
            "This may be due to line number conflicts or diff changes.",
            "",
        ]

        for file_path, file_issues in sorted(issues_by_file.items()):
            body_parts.append(f"### 📄 {file_path}")
            body_parts.append("")

            for issue in file_issues:
                line = issue.get("line", "?")
                severity = issue.get("severity", "")
                title = issue.get("title", "")
                wcag_sc = issue.get("wcag_sc", "")
                description = issue.get("description", "")

                # Severity emoji
                severity_emoji = {
                    "critical": "🔴",
                    "major": "🟠",
                    "minor": "🟡",
                    "info": "🔵",
                }.get(severity, "⚪")

                body_parts.append(f"#### {severity_emoji} Line {line}: {title}")
                body_parts.append(f"**WCAG:** {wcag_sc} | **Severity:** {severity}")
                if description:
                    body_parts.append(f"> {description}")
                body_parts.append("")

        body_parts.append("---")
        body_parts.append(
            "🤖 Posted by [accessibility-fixer](https://github.com/dominiclabbe/accessibility-fixer)"
        )

        comment_body = "\n".join(body_parts)

        # Post as simple comment
        return self.post_simple_comment(
            repo_owner, repo_name, pr_number, comment_body, headers
        )

    def post_final_review_summary(
        self,
        repo_owner: str,
        repo_name: str,
        pr_number: int,
        commit_sha: str,
        all_issues: List[Dict],
        headers: Dict[str, str],
        event: str = "COMMENT",
    ) -> bool:
        """
        Post a final review summary without inline comments.

        This is used after all platform phases are complete to post a single
        comprehensive summary of all issues found across all phases.

        Args:
            repo_owner: Repository owner
            repo_name: Repository name
            pr_number: PR number
            commit_sha: Commit SHA to review
            all_issues: List of all accessibility issues from all phases
            headers: Headers with authorization token
            event: Review event type (COMMENT, REQUEST_CHANGES, APPROVE)

        Returns:
            True if successful, False otherwise
        """
        # Build review body with full summary
        severity_counts = self._count_severities(all_issues)
        review_body = self._format_review_summary(
            severity_counts,
            is_final=True,
        )

        # Determine event based on severities
        if event == "COMMENT" and severity_counts.get("critical", 0) > 0:
            event = "REQUEST_CHANGES"

        # Post review without comments (just the summary body)
        url = f"{self.github_api_url}/repos/{repo_owner}/{repo_name}/pulls/{pr_number}/reviews"

        payload = {
            "commit_id": commit_sha,
            "body": review_body,
            "event": event,
        }

        try:
            response = requests.post(url, json=payload, headers=headers)
            response.raise_for_status()

            print(f"✅ Posted final review summary")
            return True

        except requests.exceptions.HTTPError as e:
            print(f"❌ Error posting final review summary: {e}")
            print(f"Response: {e.response.text if e.response else 'No response'}")
            return False

    def post_commit_status(
        self,
        repo_owner: str,
        repo_name: str,
        commit_sha: str,
        state: str,
        description: str,
        headers: Dict[str, str],
        context: str = "accessibility-review",
    ) -> bool:
        """
        Post commit status for accessibility review.

        Args:
            repo_owner: Repository owner
            repo_name: Repository name
            commit_sha: Commit SHA
            state: Status state (success, failure, pending, error)
            description: Status description
            headers: Headers with authorization token
            context: Status context name

        Returns:
            True if successful, False otherwise
        """
        url = f"{self.github_api_url}/repos/{repo_owner}/{repo_name}/statuses/{commit_sha}"

        payload = {
            "state": state,
            "description": description,
            "context": context,
        }

        try:
            response = requests.post(url, json=payload, headers=headers)
            response.raise_for_status()

            print(f"✅ Posted commit status: {state}")
            return True

        except requests.exceptions.HTTPError as e:
            print(f"❌ Error posting status: {e}")
            return False

    def _format_inline_comment(self, issue: Dict) -> Optional[Dict]:
        """
        Format issue as inline comment.

        Args:
            issue: Accessibility issue

        Returns:
            Comment dict or None if invalid
        """
        file_path = issue.get("file", "")
        line = issue.get("line", 0)

        if not file_path or line <= 0:
            print(
                f"Skipping issue without valid file/line: {issue.get('title', 'Unknown')}"
            )
            return None

        body = self._format_issue_body(issue)

        return {
            "path": file_path,
            "line": line,
            "side": "RIGHT",  # RIGHT = new code
            "body": body,
        }

    def _format_issue_body(self, issue: Dict) -> str:
        """Format issue as markdown comment body."""
        severity_emoji = {
            "critical": "🔴",
            "major": "🟠",
            "minor": "🟡",
            "info": "🔵",
        }
        emoji = severity_emoji.get(issue.get("severity", ""), "⚪")

        parts = []

        # Header
        parts.append(f"## {emoji} Accessibility Issue: {issue.get('title', '')}")
        parts.append("")

        # Metadata
        parts.append(
            f"**WCAG SC:** {issue.get('wcag_sc', '')} (Level {issue.get('wcag_level', '')})"
        )
        parts.append(f"**Severity:** {issue.get('severity', '')}")
        parts.append("")

        # Issue description
        if issue.get("description"):
            parts.append("**Issue:**")
            parts.append(issue.get("description", ""))
            parts.append("")

        # Impact
        if issue.get("impact"):
            parts.append("**Impact:**")
            parts.append(issue.get("impact", ""))
            parts.append("")

        # Current code
        if issue.get("current_code"):
            parts.append("**Current code:**")
            parts.append("```")
            parts.append(issue.get("current_code", ""))
            parts.append("```")
            parts.append("")

        # Suggested fix
        if issue.get("suggested_fix"):
            parts.append("**Suggested fix:**")
            parts.append("```")
            parts.append(issue.get("suggested_fix", ""))
            parts.append("```")
            parts.append("")

        # Resources
        resources = issue.get("resources", [])
        if resources:
            parts.append("**Resources:**")
            for resource in resources:
                parts.append(f"- {resource}")
            parts.append("")

        # Footer
        parts.append("---")
        parts.append(
            "🤖 Automated by [accessibility-fixer](https://github.com/dominiclabbe/accessibility-fixer)"
        )

        return "\n".join(parts)

    def _format_review_summary(
        self,
        severity_counts: Dict[str, int],
        is_final: bool = True,
        current_phase: Optional[int] = None,
        total_phases: Optional[int] = None,
    ) -> str:
        """
        Format review summary body.

        Args:
            severity_counts: Dictionary of severity counts
            is_final: Whether this is the final review (default: True)
            current_phase: Current phase number for in-progress message (optional)
            total_phases: Total number of phases for in-progress message (optional)

        Returns:
            Review summary string
        """
        parts = []

        # For intermediate reviews, use minimal "in progress" body
        if not is_final:
            if current_phase and total_phases:
                parts.append(
                    f"⏳ Accessibility review in progress… Phase {current_phase}/{total_phases}"
                )
            else:
                parts.append("⏳ Accessibility review in progress…")
            return "\n".join(parts)

        # For final review, include full summary
        parts.append("# Accessibility Review Summary")
        parts.append("")

        total = sum(severity_counts.values())

        if total == 0:
            parts.append("✅ No accessibility issues found in this PR!")
        else:
            parts.append(f"Found {total} accessibility issue(s):")
            parts.append("")

            if severity_counts.get("critical", 0) > 0:
                parts.append(f"- 🔴 **Critical**: {severity_counts['critical']}")
            if severity_counts.get("major", 0) > 0:
                parts.append(f"- 🟠 **Major**: {severity_counts['major']}")
            if severity_counts.get("minor", 0) > 0:
                parts.append(f"- 🟡 **Minor**: {severity_counts['minor']}")
            if severity_counts.get("info", 0) > 0:
                parts.append(f"- 🔵 **Info**: {severity_counts['info']}")

            parts.append("")

            if severity_counts.get("critical", 0) > 0:
                parts.append(
                    "⚠️ **Critical issues found - please address before merging.**"
                )
            else:
                parts.append("ℹ️ Please review and address the issues when possible.")

        parts.append("")
        parts.append("---")
        parts.append(
            "🤖 Automated by [accessibility-fixer](https://github.com/dominiclabbe/accessibility-fixer)"
        )

        # Add debug footer if enabled
        if os.getenv("DEBUG_REVIEW_STAMP", "").lower() in ["1", "true", "yes"]:
            debug_footer = get_debug_footer(self.reviewer_config)
            parts.append(debug_footer)

        return "\n".join(parts)

    def _get_existing_comment_locations(
        self,
        repo_owner: str,
        repo_name: str,
        pr_number: int,
        headers: Dict[str, str],
    ) -> set:
        """
        Fetch existing review comment locations to avoid re-posting.

        Returns locations with anchor signature support for better deduplication.
        Uses comment body snippet to detect duplicates even if line number changes slightly.

        Returns:
            Set of (file_path, line, body_snippet) tuples for existing comments
        """
        url = f"{self.github_api_url}/repos/{repo_owner}/{repo_name}/pulls/{pr_number}/comments"

        try:
            response = requests.get(url, headers=headers)
            response.raise_for_status()

            comments = response.json()
            locations = set()

            # For now, we treat ALL comments as existing since GitHub's comments API
            # doesn't expose resolution status directly. We'll only use this for
            # simple deduplication. Resolved comment validation happens in the AI prompt.
            for comment in comments:
                path = comment.get("path")
                line = comment.get("line") or comment.get("original_line")
                body = comment.get("body", "")

                # Extract title from body for fingerprinting
                # Look for pattern: ## <emoji> Accessibility Issue: <title>
                body_snippet = ""
                if "Accessibility Issue:" in body:
                    try:
                        # Extract the title part
                        title_start = body.index("Accessibility Issue:") + len(
                            "Accessibility Issue:"
                        )
                        title_end = body.index("\n", title_start)
                        body_snippet = body[title_start:title_end].strip()[:50]
                    except (ValueError, IndexError):
                        # Fallback to first 50 chars of body
                        body_snippet = body[:50].strip()

                if path and line:
                    # Store with body snippet for anchor-based matching
                    locations.add((path, line, body_snippet))

            return locations

        except Exception as e:
            print(f"Warning: Could not fetch existing comments: {e}")
            return set()

    def get_review_threads(
        self,
        repo_owner: str,
        repo_name: str,
        pr_number: int,
        headers: Dict[str, str],
    ) -> List[Dict]:
        """
        Fetch PR review threads including resolved/unresolved status and replies.
        This is used to pass context to the AI for validating resolutions.

        Returns:
            List of thread objects with comment details and resolution status
        """
        # Use the review comments endpoint and build threads manually
        url = f"{self.github_api_url}/repos/{repo_owner}/{repo_name}/pulls/{pr_number}/comments"

        try:
            response = requests.get(url, headers=headers)
            response.raise_for_status()

            comments = response.json()

            # Group comments by thread (based on in_reply_to_id)
            threads = {}
            root_comments = []

            for comment in comments:
                if comment.get("in_reply_to_id"):
                    # This is a reply
                    reply_to_id = comment["in_reply_to_id"]
                    if reply_to_id not in threads:
                        threads[reply_to_id] = []
                    threads[reply_to_id].append(comment)
                else:
                    # This is a root comment
                    root_comments.append(comment)

            # Build thread objects
            result = []
            for root in root_comments:
                thread = {
                    "path": root.get("path"),
                    "line": root.get("line") or root.get("original_line"),
                    "body": root.get("body", ""),
                    "user": root.get("user", {}).get("login", "unknown"),
                    "created_at": root.get("created_at", ""),
                    "replies": [],
                }

                # Add replies if any
                comment_id = root.get("id")
                if comment_id in threads:
                    for reply in threads[comment_id]:
                        thread["replies"].append(
                            {
                                "body": reply.get("body", ""),
                                "user": reply.get("user", {}).get("login", "unknown"),
                                "created_at": reply.get("created_at", ""),
                            }
                        )

                result.append(thread)

            return result

        except Exception as e:
            print(f"Warning: Could not fetch review threads: {e}")
            return []

    @staticmethod
    def _count_severities(issues: List[Dict]) -> Dict[str, int]:
        """Count issues by severity."""
        counts = {"critical": 0, "major": 0, "minor": 0, "info": 0}

        for issue in issues:
            severity = issue.get("severity", "minor")
            if severity in counts:
                counts[severity] += 1

        return counts

    def post_simple_comment(
        self,
        repo_owner: str,
        repo_name: str,
        pr_number: int,
        body: str,
        headers: Dict[str, str],
    ) -> bool:
        """
        Post a simple comment (not a review comment).

        Useful for errors or summary messages.

        Args:
            repo_owner: Repository owner
            repo_name: Repository name
            pr_number: PR number
            body: Comment body
            headers: Headers with authorization token

        Returns:
            True if successful, False otherwise
        """
        url = f"{self.github_api_url}/repos/{repo_owner}/{repo_name}/issues/{pr_number}/comments"

        payload = {"body": body}

        try:
            response = requests.post(url, json=payload, headers=headers)
            response.raise_for_status()

            print("✅ Posted simple comment")
            return True

        except requests.exceptions.HTTPError as e:
            print(f"❌ Error posting comment: {e}")
            return False
