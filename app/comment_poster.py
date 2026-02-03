"""
PR Comment Poster

Posts inline review comments and commit statuses to GitHub PRs.
"""

import requests
from typing import List, Dict, Optional


class CommentPoster:
    """Posts accessibility issues as PR review comments."""

    def __init__(self, github_api_url: str = "https://api.github.com"):
        """
        Initialize comment poster.

        Args:
            github_api_url: GitHub API base URL
        """
        self.github_api_url = github_api_url

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

        # Build review comments with deduplication
        comments = []
        seen_locations = set()

        for issue in issues:
            comment = self._format_inline_comment(issue)
            if comment:
                location_key = (comment['path'], comment['line'])

                # Skip if comment already exists from previous review
                if location_key in existing_locations:
                    print(f"Skipping existing comment at {comment['path']}:{comment['line']}")
                    continue

                # Skip if duplicate in this batch
                if location_key in seen_locations:
                    print(f"Skipping duplicate comment at {comment['path']}:{comment['line']}")
                    continue

                comments.append(comment)
                seen_locations.add(location_key)

        if not comments:
            print("No valid comments to post")
            return True

        # Build review body
        severity_counts = self._count_severities(issues)
        review_body = self._format_review_summary(severity_counts)

        # Determine event based on severities
        if event == "COMMENT" and severity_counts.get("Critical", 0) > 0:
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
            print(f"❌ Error posting review: {e}")
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
            print(f"Skipping issue without valid file/line: {issue.get('title', 'Unknown')}")
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
            "Critical": "🔴",
            "High": "🟠",
            "Medium": "🟡",
            "Low": "🔵",
        }
        emoji = severity_emoji.get(issue.get("severity", ""), "⚪")

        parts = []

        # Header
        parts.append(f"## {emoji} Accessibility Issue: {issue.get('title', '')}")
        parts.append("")

        # Metadata
        parts.append(f"**WCAG SC:** {issue.get('wcag_sc', '')} (Level {issue.get('wcag_level', '')})")
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
        parts.append("🤖 Automated by [accessibility-fixer](https://github.com/dominiclabbe/accessibility-fixer)")

        return "\n".join(parts)

    def _format_review_summary(self, severity_counts: Dict[str, int]) -> str:
        """Format review summary body."""
        parts = []

        parts.append("# Accessibility Review Summary")
        parts.append("")

        total = sum(severity_counts.values())

        if total == 0:
            parts.append("✅ No accessibility issues found in this PR!")
        else:
            parts.append(f"Found {total} accessibility issue(s):")
            parts.append("")

            if severity_counts.get("Critical", 0) > 0:
                parts.append(f"- 🔴 **Critical**: {severity_counts['Critical']}")
            if severity_counts.get("High", 0) > 0:
                parts.append(f"- 🟠 **High**: {severity_counts['High']}")
            if severity_counts.get("Medium", 0) > 0:
                parts.append(f"- 🟡 **Medium**: {severity_counts['Medium']}")
            if severity_counts.get("Low", 0) > 0:
                parts.append(f"- 🔵 **Low**: {severity_counts['Low']}")

            parts.append("")

            if severity_counts.get("Critical", 0) > 0:
                parts.append("⚠️ **Critical issues found - please address before merging.**")
            else:
                parts.append("ℹ️ Please review and address the issues when possible.")

        parts.append("")
        parts.append("---")
        parts.append("🤖 Automated by [accessibility-fixer](https://github.com/dominiclabbe/accessibility-fixer)")

        return "\n".join(parts)

    def _get_existing_comment_locations(
        self,
        repo_owner: str,
        repo_name: str,
        pr_number: int,
        headers: Dict[str, str],
    ) -> set:
        """
        Fetch existing UNRESOLVED review comment locations to avoid re-posting.
        Resolved comments are not included here - they'll be fetched separately
        for the AI to review and validate the resolution.

        Returns:
            Set of (file_path, line) tuples for existing UNRESOLVED comments
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
                if path and line:
                    locations.add((path, line))

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
                        thread["replies"].append({
                            "body": reply.get("body", ""),
                            "user": reply.get("user", {}).get("login", "unknown"),
                            "created_at": reply.get("created_at", ""),
                        })

                result.append(thread)

            return result

        except Exception as e:
            print(f"Warning: Could not fetch review threads: {e}")
            return []

    @staticmethod
    def _count_severities(issues: List[Dict]) -> Dict[str, int]:
        """Count issues by severity."""
        counts = {"Critical": 0, "High": 0, "Medium": 0, "Low": 0}

        for issue in issues:
            severity = issue.get("severity", "")
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
