"""
Diff Parser

Parses unified diffs and provides accurate line mapping for GitHub PR comments.
Handles per-file diff filtering and commentable line extraction.
"""

import os
import re
import logging
from difflib import get_close_matches
from typing import Dict, List, Tuple, Optional, Set
from pathlib import Path

from app.constants import WEB_EXTENSIONS

logger = logging.getLogger(__name__)


class DiffParser:
    """Parses unified diffs and provides line mapping utilities."""

    @staticmethod
    def _normalize_diff(diff_text: str) -> str:
        """
        Normalize diff text to handle CRLF/newline issues.
        
        Args:
            diff_text: Raw diff text
            
        Returns:
            Normalized diff text with consistent line endings
        """
        # Replace CRLF with LF
        diff_text = diff_text.replace("\r\n", "\n")
        # Strip any remaining standalone CR characters
        diff_text = diff_text.replace("\r", "")
        return diff_text

    @staticmethod
    def parse_diff(diff_text: str) -> Dict[str, str]:
        """
        Parse unified diff into per-file sections.

        Args:
            diff_text: Full unified diff text

        Returns:
            Dict mapping file paths to their diff sections
        """
        # Normalize diff text to handle CRLF issues
        diff_text = DiffParser._normalize_diff(diff_text)
        
        file_diffs = {}
        current_file = None
        current_diff_lines = []

        for line in diff_text.split("\n"):
            # Match diff header: diff --git a/path b/path
            if line.startswith("diff --git "):
                # Save previous file if exists
                if current_file and current_diff_lines:
                    # Remove trailing empty lines from previous file
                    while current_diff_lines and current_diff_lines[-1].strip() == "":
                        current_diff_lines.pop()
                    file_diffs[current_file] = "\n".join(current_diff_lines)

                # Extract file path from "a/..." or "b/..."
                # Match "b/" followed by path, stopping at whitespace to avoid line-bleed
                # Use negative lookbehind to skip "a/" paths
                match = re.search(r"\sb/(\S+)", line)
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
            file_diffs[current_file] = "\n".join(current_diff_lines)

        return file_diffs

    @staticmethod
    def filter_diff_for_files(full_diff: str, file_paths: List[str]) -> str:
        """
        Filter diff to only include specified files.

        Implements path normalization to handle cases where requested paths
        differ from diff paths by leading directory components.

        Args:
            full_diff: Full unified diff text
            file_paths: List of file paths to include

        Returns:
            Filtered diff containing only specified files
        """
        if not file_paths:
            return ""

        # Normalize diff text to handle CRLF issues
        full_diff = DiffParser._normalize_diff(full_diff)

        debug_web_review = os.getenv("DEBUG_WEB_REVIEW", "").lower() in [
            "1",
            "true",
            "yes",
        ]

        file_set = set(file_paths)
        parsed = DiffParser.parse_diff(full_diff)
        diff_paths = list(parsed.keys())

        # DEBUG_WEB_REVIEW: Log path matching details
        if debug_web_review:
            logger.info("[DEBUG_WEB_REVIEW] filter_diff_for_files called")
            logger.info(f"  Requested files ({len(file_paths)}): {file_paths}")
            logger.info(f"  Diff paths found ({len(diff_paths)}): {diff_paths}")

        # Collect diffs for requested files
        filtered_sections = []
        for file_path in file_paths:
            matched_diff_path = None

            # 1. Try exact match first
            if file_path in parsed:
                matched_diff_path = file_path
                if debug_web_review:
                    logger.info(f"  [{file_path}] Exact match found")
            else:
                # 2. Try suffix matching (handles different leading directory components)
                # Only use suffix match if it's unambiguous (exactly one match)
                suffix_matches = []
                for diff_path in diff_paths:
                    # Check if either path is a suffix of the other
                    if diff_path.endswith("/" + file_path) or file_path.endswith(
                        "/" + diff_path
                    ):
                        suffix_matches.append(diff_path)
                    # Also check without leading slash for edge cases
                    elif diff_path.endswith(file_path) or file_path.endswith(diff_path):
                        # But only if they differ in directory components
                        if "/" in file_path or "/" in diff_path:
                            suffix_matches.append(diff_path)

                if len(suffix_matches) == 1:
                    matched_diff_path = suffix_matches[0]
                    if debug_web_review:
                        logger.info(
                            f"  [{file_path}] Suffix match: {matched_diff_path}"
                        )
                elif len(suffix_matches) > 1:
                    if debug_web_review:
                        logger.info(
                            f"  [{file_path}] Multiple suffix matches, skipping: {suffix_matches}"
                        )
                else:
                    # 3. Last resort: basename matching (only if unique)
                    file_basename = os.path.basename(file_path)
                    basename_matches = [
                        dp for dp in diff_paths if os.path.basename(dp) == file_basename
                    ]

                    if len(basename_matches) == 1:
                        matched_diff_path = basename_matches[0]
                        if debug_web_review:
                            logger.info(
                                f"  [{file_path}] Basename match: {matched_diff_path}"
                            )
                    elif len(basename_matches) > 1:
                        if debug_web_review:
                            logger.info(
                                f"  [{file_path}] Ambiguous basename matches: {basename_matches}"
                            )
                    else:
                        if debug_web_review:
                            logger.info(f"  [{file_path}] No match found")

            if matched_diff_path:
                filtered_sections.append(parsed[matched_diff_path])

        return "\n".join(filtered_sections)

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
        # Normalize diff text to handle CRLF issues
        diff_text = DiffParser._normalize_diff(diff_text)
        
        commentable = {}
        current_file = None
        current_line = 0
        in_hunk = False

        for line in diff_text.split("\n"):
            # Match file header: +++ b/path/to/file
            # Extract path, stopping at whitespace to avoid line-bleed
            if line.startswith("+++ b/"):
                path_part = line[6:]  # Skip '+++ b/'
                # Split on whitespace and take first token
                current_file = path_part.split()[0] if path_part else ""
                commentable[current_file] = []
                in_hunk = False
                continue

            # Match hunk header: @@ -old_start,old_count +new_start,new_count @@
            hunk_match = re.match(r"^@@ -\d+(?:,\d+)? \+(\d+)(?:,\d+)? @@", line)
            if hunk_match and current_file:
                current_line = int(hunk_match.group(1))
                in_hunk = True
                continue

            # Process lines in hunk
            if in_hunk and current_file:
                if line.startswith("+") and not line.startswith("+++"):
                    # Added line - commentable
                    commentable[current_file].append(current_line)
                    current_line += 1
                elif line.startswith(" "):
                    # Context line - also commentable
                    commentable[current_file].append(current_line)
                    current_line += 1
                elif line.startswith("-"):
                    # Removed line - don't increment new file line number
                    pass
                else:
                    # Empty or other line - might be end of hunk
                    if line and not line.startswith("\\"):
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
        # Normalize diff text to handle CRLF issues
        diff_text = DiffParser._normalize_diff(diff_text)
        
        ranges = {}
        current_file = None

        for line in diff_text.split("\n"):
            # Match file header
            # Extract path, stopping at whitespace to avoid line-bleed
            if line.startswith("+++ b/"):
                path_part = line[6:]
                current_file = path_part.split()[0] if path_part else ""
                ranges[current_file] = []
                continue

            # Match hunk header
            hunk_match = re.match(r"^@@ -\d+(?:,\d+)? \+(\d+)(?:,(\d+))? @@", line)
            if hunk_match and current_file:
                start = int(hunk_match.group(1))
                count = int(hunk_match.group(2)) if hunk_match.group(2) else 1
                if count > 0:
                    end = start + count - 1
                    ranges[current_file].append((start, end))

        return ranges

    @staticmethod
    def find_nearest_commentable_line(
        target_line: int, commentable_lines: List[int], max_distance: int = 10
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
        min_distance = float("inf")
        nearest = None

        for line_num in commentable_lines:
            distance = abs(line_num - target_line)
            if distance < min_distance and distance <= max_distance:
                min_distance = distance
                nearest = line_num

        return nearest

    @staticmethod
    def get_code_anchor(
        diff_text: str, file_path: str, line_num: int, context_lines: int = 2
    ) -> str:
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
        # Normalize diff text to handle CRLF issues
        diff_text = DiffParser._normalize_diff(diff_text)
        
        current_file = None
        current_line = 0
        in_hunk = False
        lines_buffer = []

        for line in diff_text.split("\n"):
            # Match file header
            # Extract path, stopping at whitespace to avoid line-bleed
            if line.startswith("+++ b/"):
                path_part = line[6:]
                current_file = path_part.split()[0] if path_part else ""
                in_hunk = False
                current_line = 0
                lines_buffer = []
                continue

            # Match hunk header
            hunk_match = re.match(r"^@@ -\d+(?:,\d+)? \+(\d+)(?:,\d+)? @@", line)
            if hunk_match and current_file == file_path:
                current_line = int(hunk_match.group(1))
                in_hunk = True
                lines_buffer = []
                continue

            # Collect lines in hunk for target file
            if in_hunk and current_file == file_path:
                if line.startswith("+") and not line.startswith("+++"):
                    lines_buffer.append((current_line, line[1:]))  # Remove '+'
                    current_line += 1
                elif line.startswith(" "):
                    lines_buffer.append((current_line, line[1:]))  # Remove ' '
                    current_line += 1
                elif line.startswith("-"):
                    # Skip removed lines
                    pass

        # Find target line in buffer and extract with context
        for i, (ln, content) in enumerate(lines_buffer):
            if ln == line_num:
                start_idx = max(0, i - context_lines)
                end_idx = min(len(lines_buffer), i + context_lines + 1)
                snippet_lines = [
                    content for _, content in lines_buffer[start_idx:end_idx]
                ]
                return "\n".join(snippet_lines).strip()

        return ""


def _find_closest_files(
    file_path: str, batch_files: List[str], n: int = 2
) -> List[str]:
    """
    Find closest matching files based on filename similarity.

    Args:
        file_path: The file to find matches for
        batch_files: List of files to search within
        n: Number of matches to return

    Returns:
        List of closest matching file paths
    """
    file_basename = os.path.basename(file_path)
    batch_basenames = {os.path.basename(f): f for f in batch_files}
    close_matches = get_close_matches(
        file_basename, batch_basenames.keys(), n=n, cutoff=0.6
    )
    return [
        batch_basenames[match]
        for match in close_matches
        if batch_basenames[match] != file_path
    ]


def _is_web_file(file_path: str) -> bool:
    """
    Check if a file is a web file (for DEBUG_WEB_REVIEW filtering).

    Args:
        file_path: File path to check

    Returns:
        True if file is a web file (.tsx/.ts/.jsx/.js/.css/.html or in web/ dir)
    """
    return file_path.startswith("web/") or Path(file_path).suffix in WEB_EXTENSIONS


def validate_issues_in_batch(
    issues: List[Dict],
    batch_files: List[str],
    commentable_lines: Dict[str, List[int]],
    diff_text: Optional[str] = None,
) -> List[Dict]:
    """
    Validate and adjust issues to ensure they're in the batch and on commentable lines.

    Uses deterministic diff-grounded anchor resolution to find the correct UI element
    declaration/call site before falling back to nearest commentable line.

    Args:
        issues: List of issues from model
        batch_files: List of files in current batch
        commentable_lines: Dict of file -> commentable line numbers
        diff_text: Optional unified diff text for anchor resolution

    Returns:
        List of validated issues (may be adjusted or filtered)
    """
    from app.semantic_anchor_resolver import SemanticAnchorResolver

    validated = []
    batch_file_set = set(batch_files)

    # Check if debug logging is enabled
    debug_enabled = os.getenv("DEBUG_ANCHOR_RESOLUTION", "").lower() in [
        "1",
        "true",
        "yes",
    ]
    debug_web_review = os.getenv("DEBUG_WEB_REVIEW", "").lower() in ["1", "true", "yes"]

    # Track drop reasons for DEBUG_WEB_REVIEW
    drop_reasons = []

    # Extract line texts for anchor resolution if diff provided
    line_texts = {}
    if diff_text:
        line_texts = SemanticAnchorResolver.extract_commentable_line_texts(
            diff_text, commentable_lines
        )

        # DEBUG_WEB_REVIEW: Log right_line_to_text counts
        if debug_web_review:
            logger.info("[DEBUG_WEB_REVIEW] right_line_to_text mapping:")
            for file_path, line_to_text in line_texts.items():
                logger.info(
                    f"  {file_path}: {len(line_to_text)} commentable lines with text"
                )

    for issue in issues:
        file_path = issue.get("file", "")
        line = issue.get("line", 0)
        is_web = _is_web_file(file_path)

        # Skip if file not in batch
        if file_path not in batch_file_set:
            reason_code = "file_not_in_batch"
            drop_reason = (
                f"{reason_code}: proposed={file_path}, batch_size={len(batch_files)}"
            )

            # Always log warning for dropped issues (not gated by DEBUG_WEB_REVIEW)
            print(f"⚠️  Dropping issue for {file_path}:{line} - {drop_reason}")

            # DEBUG_WEB_REVIEW: Add detailed logging for web files
            if debug_web_review and is_web:
                # Find closest matches based on filename similarity
                closest_files = _find_closest_files(file_path, batch_files, n=3)

                # Check for basename matches in batch
                file_basename = os.path.basename(file_path)
                basename_matches = [
                    f for f in batch_files if os.path.basename(f) == file_basename
                ]

                drop_reasons.append(
                    {
                        "file": file_path,
                        "line": line,
                        "reason_code": reason_code,
                        "reason": drop_reason,
                        "title": issue.get("title", "")[:60],
                        "closest_files": closest_files if closest_files else [],
                        "basename_matches": (
                            basename_matches if basename_matches else []
                        ),
                    }
                )
            continue

        # Skip if line is invalid
        if line <= 0:
            reason_code = "invalid_line_number"
            drop_reason = f"{reason_code}: line={line}"
            print(f"⚠️  Dropping issue for {file_path}:{line} - {drop_reason}")

            if debug_web_review and is_web:
                drop_reasons.append(
                    {
                        "file": file_path,
                        "line": line,
                        "reason_code": reason_code,
                        "reason": drop_reason,
                        "title": issue.get("title", "")[:60],
                    }
                )
            continue

        # Check if file has no commentable lines at all
        if file_path not in commentable_lines or not commentable_lines[file_path]:
            reason_code = "no_commentable_lines_for_file"
            drop_reason = f"{reason_code}: file={file_path}"
            print(f"⚠️  Dropping issue for {file_path}:{line} - {drop_reason}")

            if debug_web_review and is_web:
                drop_reasons.append(
                    {
                        "file": file_path,
                        "line": line,
                        "reason_code": reason_code,
                        "reason": drop_reason,
                        "title": issue.get("title", "")[:60],
                    }
                )
            continue

        # Check if line is commentable
        if file_path in commentable_lines:
            file_commentable = commentable_lines[file_path]
            if line not in file_commentable:
                # Try deterministic anchor resolution first
                resolved_line = None
                matched_text = None

                if diff_text and file_path in line_texts:
                    # Get file extension for framework inference
                    file_ext = Path(file_path).suffix

                    # Build right_line_to_text mapping for this file
                    right_line_to_text = line_texts[file_path]

                    if debug_enabled:
                        print(
                            f"\n[DEBUG_ANCHOR_RESOLUTION] Resolving non-commentable line"
                        )
                        print(f"  File: {file_path}")
                        print(f"  Proposed line: {line}")
                        print(f"  Issue: {issue.get('title', '')[:80]}")
                        print(
                            f"  Explicit anchor_text: {issue.get('anchor_text', 'N/A')}"
                        )
                        call_site_from_current = (
                            SemanticAnchorResolver.extract_call_site_token(
                                issue.get("current_code")
                            )
                        )
                        if call_site_from_current:
                            print(
                                f"  Extracted call-site token: {call_site_from_current}"
                            )

                    # Use new deterministic resolve_anchor_line function
                    resolved_line, matched_text = (
                        SemanticAnchorResolver.resolve_anchor_line(
                            issue=issue,
                            right_line_to_text=right_line_to_text,
                            fallback_line=line,
                            file_extension=file_ext,
                            debug=debug_enabled,
                        )
                    )

                if resolved_line:
                    if debug_enabled:
                        print(
                            f"  [RESULT] Adjusted {file_path}:{line} -> {resolved_line}"
                        )
                        print(
                            f"  [RESULT] Matched text: {matched_text[:80] if matched_text else 'N/A'}\n"
                        )
                    else:
                        print(
                            f"  ✓ Adjusted {file_path}:{line} -> {resolved_line} (anchor: {matched_text[:60] if matched_text else 'N/A'})"
                        )
                    issue["line"] = resolved_line
                    # Store matched text for fingerprinting
                    issue["_anchor_matched_text"] = matched_text
                else:
                    # Determine specific drop reason
                    anchor_attempted = bool(diff_text and file_path in line_texts)

                    # Fall back to nearest commentable line
                    nearest = DiffParser.find_nearest_commentable_line(
                        line, file_commentable
                    )
                    if nearest:
                        if debug_enabled:
                            print(
                                f"  [RESULT] Adjusted {file_path}:{line} -> {nearest} (nearest commentable, no anchor found)\n"
                            )
                        else:
                            print(
                                f"  ⚠️  Adjusted {file_path}:{line} -> {nearest} (nearest commentable, no anchor found)"
                            )
                        issue["line"] = nearest

                        # DEBUG_WEB_REVIEW: Track anchor resolution failure for web files
                        if debug_web_review and is_web and anchor_attempted:
                            reason_code = "anchor_not_found"
                            drop_reasons.append(
                                {
                                    "file": file_path,
                                    "line": line,
                                    "adjusted_to": nearest,
                                    "reason_code": reason_code,
                                    "reason": f"{reason_code}: fell back to nearest commentable line {nearest}",
                                    "title": issue.get("title", "")[:60],
                                }
                            )
                    else:
                        # No nearest commentable line found - must drop
                        reason_code = (
                            "nearest_commentable_none"
                            if anchor_attempted
                            else "line_not_commentable"
                        )
                        drop_reason = f"{reason_code}: proposed_line={line}, commentable_range={min(file_commentable) if file_commentable else 'N/A'}-{max(file_commentable) if file_commentable else 'N/A'}"

                        if debug_enabled:
                            print(f"  [RESULT] Dropping issue - {drop_reason}\n")
                        print(
                            f"⚠️  Dropping issue for {file_path}:{line} - {drop_reason}"
                        )

                        if debug_web_review and is_web:
                            drop_reasons.append(
                                {
                                    "file": file_path,
                                    "line": line,
                                    "reason_code": reason_code,
                                    "reason": drop_reason,
                                    "title": issue.get("title", "")[:60],
                                    "commentable_lines_count": (
                                        len(file_commentable) if file_commentable else 0
                                    ),
                                }
                            )
                        continue
            else:
                # Line is already commentable - log if debug enabled
                if debug_enabled:
                    print(f"\n[DEBUG_ANCHOR_RESOLUTION] Line already commentable")
                    print(f"  File: {file_path}")
                    print(f"  Line: {line}")
                    print(f"  Issue: {issue.get('title', '')[:80]}")
                    print(
                        f"  [RESULT] Using proposed line {line} (already commentable)\n"
                    )

        validated.append(issue)

    # DEBUG_WEB_REVIEW: Log drop reasons summary
    if debug_web_review and drop_reasons:
        logger.info("\n[DEBUG_WEB_REVIEW] Validation drop reasons (web files only):")
        for drop in drop_reasons:
            reason_code = drop.get("reason_code", "unknown")
            logger.info(f"  {drop['file']}:{drop['line']} - {reason_code}")
            logger.info(f"    Title: {drop['title']}")
            logger.info(f"    Reason: {drop['reason']}")

            if drop.get("adjusted_to"):
                logger.info(f"    Adjusted to line: {drop['adjusted_to']}")
            if drop.get("basename_matches"):
                logger.info(
                    f"    Basename matches in batch: {drop['basename_matches']}"
                )
            if drop.get("closest_files"):
                logger.info(f"    Closest files (difflib): {drop['closest_files']}")
            if "commentable_lines_count" in drop:
                logger.info(
                    f"    Commentable lines in file: {drop['commentable_lines_count']}"
                )

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
    wcag_sc = issue.get("wcag_sc", "").upper()
    if wcag_sc in ["N/A", "NONE", ""]:
        return True

    # Check title/description for "no issues" phrases
    title = issue.get("title", "").lower()
    description = issue.get("description", "").lower()

    no_issue_phrases = [
        "no accessibility issues",
        "no issues found",
        "no issues detected",
        "looks good",
        "no problems",
        "all good",
        "compliant",
    ]

    for phrase in no_issue_phrases:
        if phrase in title or phrase in description:
            return True

    return False
