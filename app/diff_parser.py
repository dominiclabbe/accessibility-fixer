"""
Diff Parser

Parses unified diffs and provides accurate line mapping for GitHub PR comments.
Handles per-file diff filtering and commentable line extraction.
"""

import re
from typing import Dict, List, Tuple, Optional, Set


class DiffParser:
    """Parses unified diffs and provides line mapping utilities."""

    @staticmethod
    def parse_diff(diff_text: str) -> Dict[str, str]:
        """
        Parse unified diff into per-file sections.

        Args:
            diff_text: Full unified diff text

        Returns:
            Dict mapping file paths to their diff sections
        """
        file_diffs = {}
        current_file = None
        current_diff_lines = []

        for line in diff_text.split('\n'):
            # Match diff header: diff --git a/path b/path
            if line.startswith('diff --git '):
                # Save previous file if exists
                if current_file and current_diff_lines:
                    file_diffs[current_file] = '\n'.join(current_diff_lines)

                # Extract file path from "a/..." or "b/..."
                match = re.search(r'b/(.+)$', line)
                if match:
                    current_file = match.group(1)
                    current_diff_lines = [line]
                else:
                    current_file = None
                    current_diff_lines = []
            elif current_file is not None:
                current_diff_lines.append(line)

        # Save last file
        if current_file and current_diff_lines:
            file_diffs[current_file] = '\n'.join(current_diff_lines)

        return file_diffs

    @staticmethod
    def filter_diff_for_files(full_diff: str, file_paths: List[str]) -> str:
        """
        Filter diff to only include specified files.

        Args:
            full_diff: Full unified diff text
            file_paths: List of file paths to include

        Returns:
            Filtered diff containing only specified files
        """
        if not file_paths:
            return ""

        file_set = set(file_paths)
        parsed = DiffParser.parse_diff(full_diff)

        # Collect diffs for requested files
        filtered_sections = []
        for file_path in file_paths:
            if file_path in parsed:
                filtered_sections.append(parsed[file_path])

        return '\n'.join(filtered_sections)

    @staticmethod
    def extract_commentable_lines(diff_text: str) -> Dict[str, List[int]]:
        """
        Extract commentable line numbers from diff.

        For GitHub PR comments, commentable lines are:
        - Added lines (lines starting with '+')
        - Context lines (lines starting with ' ')

        Args:
            diff_text: Unified diff text

        Returns:
            Dict mapping file paths to lists of commentable line numbers
        """
        commentable = {}
        current_file = None
        current_line = 0
        in_hunk = False

        for line in diff_text.split('\n'):
            # Match file header: +++ b/path/to/file
            if line.startswith('+++ b/'):
                current_file = line[6:]  # Skip '+++ b/'
                commentable[current_file] = []
                in_hunk = False
                continue

            # Match hunk header: @@ -old_start,old_count +new_start,new_count @@
            hunk_match = re.match(r'^@@ -\d+(?:,\d+)? \+(\d+)(?:,\d+)? @@', line)
            if hunk_match and current_file:
                current_line = int(hunk_match.group(1))
                in_hunk = True
                continue

            # Process lines in hunk
            if in_hunk and current_file:
                if line.startswith('+') and not line.startswith('+++'):
                    # Added line - commentable
                    commentable[current_file].append(current_line)
                    current_line += 1
                elif line.startswith(' '):
                    # Context line - also commentable
                    commentable[current_file].append(current_line)
                    current_line += 1
                elif line.startswith('-'):
                    # Removed line - don't increment new file line number
                    pass
                else:
                    # Empty or other line - might be end of hunk
                    if line and not line.startswith('\\'):
                        in_hunk = False

        return commentable

    @staticmethod
    def extract_changed_line_ranges(diff_text: str) -> Dict[str, List[Tuple[int, int]]]:
        """
        Extract changed line ranges from diff (for validation).

        Returns ranges that cover all hunks in each file.

        Args:
            diff_text: Unified diff text

        Returns:
            Dict mapping file paths to list of (start_line, end_line) tuples
        """
        ranges = {}
        current_file = None

        for line in diff_text.split('\n'):
            # Match file header
            if line.startswith('+++ b/'):
                current_file = line[6:]
                ranges[current_file] = []
                continue

            # Match hunk header
            hunk_match = re.match(r'^@@ -\d+(?:,\d+)? \+(\d+)(?:,(\d+))? @@', line)
            if hunk_match and current_file:
                start = int(hunk_match.group(1))
                count = int(hunk_match.group(2)) if hunk_match.group(2) else 1
                if count > 0:
                    end = start + count - 1
                    ranges[current_file].append((start, end))

        return ranges

    @staticmethod
    def find_nearest_commentable_line(
        target_line: int,
        commentable_lines: List[int],
        max_distance: int = 10
    ) -> Optional[int]:
        """
        Find the nearest commentable line to a target line.

        Args:
            target_line: Target line number
            commentable_lines: List of commentable line numbers
            max_distance: Maximum distance to search (default: 10)

        Returns:
            Nearest commentable line number or None if none found within max_distance
        """
        if not commentable_lines:
            return None

        # If target is already commentable, return it
        if target_line in commentable_lines:
            return target_line

        # Find closest line
        min_distance = float('inf')
        nearest = None

        for line_num in commentable_lines:
            distance = abs(line_num - target_line)
            if distance < min_distance and distance <= max_distance:
                min_distance = distance
                nearest = line_num

        return nearest

    @staticmethod
    def get_code_anchor(diff_text: str, file_path: str, line_num: int, context_lines: int = 2) -> str:
        """
        Extract a code anchor (snippet) from diff for a specific file and line.

        Used for fingerprinting issues.

        Args:
            diff_text: Unified diff text
            file_path: File path
            line_num: Line number
            context_lines: Number of context lines to include

        Returns:
            Code snippet as string (empty if not found)
        """
        current_file = None
        current_line = 0
        in_hunk = False
        lines_buffer = []

        for line in diff_text.split('\n'):
            # Match file header
            if line.startswith('+++ b/'):
                current_file = line[6:]
                in_hunk = False
                current_line = 0
                lines_buffer = []
                continue

            # Match hunk header
            hunk_match = re.match(r'^@@ -\d+(?:,\d+)? \+(\d+)(?:,\d+)? @@', line)
            if hunk_match and current_file == file_path:
                current_line = int(hunk_match.group(1))
                in_hunk = True
                lines_buffer = []
                continue

            # Collect lines in hunk for target file
            if in_hunk and current_file == file_path:
                if line.startswith('+') and not line.startswith('+++'):
                    lines_buffer.append((current_line, line[1:]))  # Remove '+'
                    current_line += 1
                elif line.startswith(' '):
                    lines_buffer.append((current_line, line[1:]))  # Remove ' '
                    current_line += 1
                elif line.startswith('-'):
                    # Skip removed lines
                    pass

        # Find target line in buffer and extract with context
        for i, (ln, content) in enumerate(lines_buffer):
            if ln == line_num:
                start_idx = max(0, i - context_lines)
                end_idx = min(len(lines_buffer), i + context_lines + 1)
                snippet_lines = [content for _, content in lines_buffer[start_idx:end_idx]]
                return '\n'.join(snippet_lines).strip()

        return ""


def validate_issues_in_batch(
    issues: List[Dict],
    batch_files: List[str],
    commentable_lines: Dict[str, List[int]]
) -> List[Dict]:
    """
    Validate and adjust issues to ensure they're in the batch and on commentable lines.

    Args:
        issues: List of issues from model
        batch_files: List of files in current batch
        commentable_lines: Dict of file -> commentable line numbers

    Returns:
        List of validated issues (may be adjusted or filtered)
    """
    validated = []
    batch_file_set = set(batch_files)

    for issue in issues:
        file_path = issue.get('file', '')
        line = issue.get('line', 0)

        # Skip if file not in batch
        if file_path not in batch_file_set:
            print(f"⚠️  Dropping issue for {file_path}:{line} - file not in batch")
            continue

        # Skip if line is invalid
        if line <= 0:
            print(f"⚠️  Dropping issue for {file_path}:{line} - invalid line number")
            continue

        # Check if line is commentable
        if file_path in commentable_lines:
            file_commentable = commentable_lines[file_path]
            if line not in file_commentable:
                # Try to adjust to nearest commentable line
                nearest = DiffParser.find_nearest_commentable_line(line, file_commentable)
                if nearest:
                    print(f"  Adjusted {file_path}:{line} -> {nearest} (nearest commentable)")
                    issue['line'] = nearest
                else:
                    print(f"⚠️  Dropping issue for {file_path}:{line} - no commentable line nearby")
                    continue

        validated.append(issue)

    return validated


def is_no_issues_placeholder(issue: Dict) -> bool:
    """
    Check if an issue is a "no issues found" placeholder.

    Args:
        issue: Issue dict

    Returns:
        True if this is a placeholder issue
    """
    # Check for explicit N/A marker
    wcag_sc = issue.get('wcag_sc', '').upper()
    if wcag_sc in ['N/A', 'NONE', '']:
        return True

    # Check title/description for "no issues" phrases
    title = issue.get('title', '').lower()
    description = issue.get('description', '').lower()

    no_issue_phrases = [
        'no accessibility issues',
        'no issues found',
        'no issues detected',
        'looks good',
        'no problems',
        'all good',
        'compliant',
    ]

    for phrase in no_issue_phrases:
        if phrase in title or phrase in description:
            return True

    return False
