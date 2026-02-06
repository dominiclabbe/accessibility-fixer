"""
Platform Bucketing

Detects platforms from file extensions and content, and buckets files by platform
for phased reviews.
"""

import re
import logging
from pathlib import Path
from typing import List, Dict, Set

from app.diff_parser import DiffParser

logger = logging.getLogger(__name__)


# Platform detection order (strict)
PLATFORM_ORDER = ["Android", "iOS", "Web", "React Native", "Flutter"]

# Minimum length for a valid file path (e.g., "a/b" is 3 chars)
MIN_PATH_LENGTH = 2


def detect_react_native_in_diff(file_path: str, pr_diff: str) -> bool:
    """
    Detect if a file is React Native by analyzing its diff content.

    Strong signals for React Native:
    - import/require from 'react-native'
    - RN component tags like <View>, <Text>, <TouchableOpacity>

    Args:
        file_path: Path to the file
        pr_diff: Full PR diff

    Returns:
        True if file is detected as React Native
    """
    # Get the diff chunk for this specific file
    file_diff = DiffParser.filter_diff_for_files(pr_diff, [file_path])
    if not file_diff:
        return False

    # Check for React Native imports
    rn_import_patterns = [
        r"from\s+['\"]react-native['\"]",
        r"require\s*\(['\"]react-native['\"]\)",
    ]

    for pattern in rn_import_patterns:
        if re.search(pattern, file_diff):
            logger.debug(f"Detected React Native import in {file_path}")
            return True

    # Check for React Native component tags
    # Look for common RN components in JSX/TSX
    rn_components = [
        r"<View[\s>]",
        r"<Text[\s>]",
        r"<TouchableOpacity[\s>]",
        r"<ScrollView[\s>]",
        r"<FlatList[\s>]",
        r"<Image[\s>]",
        r"<TextInput[\s>]",
        r"<SafeAreaView[\s>]",
        r"<Pressable[\s>]",
    ]

    for component_pattern in rn_components:
        if re.search(component_pattern, file_diff):
            logger.debug(f"Detected React Native component in {file_path}")
            return True

    return False


def bucket_files_by_platform(
    changed_files: List[str], pr_diff: str
) -> Dict[str, List[str]]:
    """
    Bucket files by platform based on extension and content.

    File bucketing rules:
    - Android: .kt, .java
    - iOS: .swift, .m, .mm
    - Flutter: .dart
    - Web: .css, .html (unconditional)
    - Web/React Native: .tsx, .jsx, .ts, .js (content-based detection)

    Args:
        changed_files: List of changed file paths
        pr_diff: Full PR diff for content-based detection

    Returns:
        Dict mapping platform name to list of files
    """
    buckets: Dict[str, List[str]] = {
        "Android": [],
        "iOS": [],
        "Web": [],
        "React Native": [],
        "Flutter": [],
    }

    for file_path in changed_files:
        ext = Path(file_path).suffix.lower()

        # Android
        if ext in [".kt", ".java"]:
            buckets["Android"].append(file_path)

        # iOS
        elif ext in [".swift", ".m", ".mm"]:
            buckets["iOS"].append(file_path)

        # Flutter
        elif ext == ".dart":
            buckets["Flutter"].append(file_path)

        # Web unconditional
        elif ext in [".css", ".html"]:
            buckets["Web"].append(file_path)

        # Web-ish: requires content-based detection
        elif ext in [".tsx", ".jsx", ".ts", ".js"]:
            if detect_react_native_in_diff(file_path, pr_diff):
                buckets["React Native"].append(file_path)
            else:
                buckets["Web"].append(file_path)

        else:
            # Unknown extension, skip
            logger.debug(f"Skipping file with unknown extension: {file_path}")

    # Log bucketing results
    for platform in PLATFORM_ORDER:
        if buckets[platform]:
            logger.info(f"Bucketed {len(buckets[platform])} files for {platform}")

    return buckets


def get_platforms_in_order(buckets: Dict[str, List[str]]) -> List[str]:
    """
    Get list of platforms that have files, in the strict order.

    Args:
        buckets: Dict mapping platform name to list of files

    Returns:
        List of platform names in order that have files
    """
    return [platform for platform in PLATFORM_ORDER if buckets[platform]]


def normalize_path(path: str) -> str:
    """
    Normalize a file path for consistent comparison.

    - Converts backslashes to forward slashes
    - Strips leading slash
    - Returns lowercase for case-insensitive comparison

    Args:
        path: File path to normalize

    Returns:
        Normalized path
    """
    if not path:
        return ""

    # Convert backslashes to forward slashes
    normalized = path.replace("\\", "/")

    # Strip leading slash
    if normalized.startswith("/"):
        normalized = normalized[1:]

    return normalized


def extract_path_from_entry(entry) -> str:
    """
    Extract file path from various entry formats.

    Supports:
    - Tuples: Intelligently detects which element is the file path by looking for
              strings containing '/' or '\' that resemble file paths
    - Dicts: {'file': ...}, {'path': ...}, {'file_path': ...}
    - Nested: {'comment': {'path': ...}}

    Args:
        entry: Location entry (tuple or dict)

    Returns:
        Extracted file path or empty string if not found
    """
    if isinstance(entry, tuple) and len(entry) >= 1:
        # Intelligently find the file path element
        # A file path typically:
        # - Is a string
        # - Contains '/' or '\' (path separator)
        # - Has a reasonable length (not just a single char)
        # - May have a file extension
        for element in entry:
            if not isinstance(element, str):
                continue
            
            # Check if this looks like a file path
            if ('/' in element or '\\' in element) and len(element) > MIN_PATH_LENGTH:
                # This looks like a file path
                return element
        
        # Fallback: if no obvious path found, use first string element
        for element in entry:
            if isinstance(element, str) and len(element) > 0:
                return element
        
        # Last resort: convert first element to string
        return str(entry[0])
    
    elif isinstance(entry, dict):
        # Try multiple key names
        path = entry.get("path") or entry.get("file") or entry.get("file_path")

        # If not found at top level, try nested comment object
        if not path and "comment" in entry:
            comment = entry["comment"]
            if isinstance(comment, dict):
                path = (
                    comment.get("path")
                    or comment.get("file")
                    or comment.get("file_path")
                )

        return str(path) if path else ""

    return ""


def filter_locations_for_files(locations: List, file_paths: List[str]) -> List:
    """
    Filter a list of locations (comments/threads) to only include those
    matching the given file paths.

    Supports multiple entry formats:
    - Tuples: (file, line, ...) where file is first element
    - Dicts: {'file': ...} or {'path': ...} or {'file_path': ...}
    - Nested: {'comment': {'path': ...}}

    Paths are normalized before comparison:
    - Backslashes converted to forward slashes
    - Leading slashes stripped

    Args:
        locations: List of location entries (tuples or dicts)
        file_paths: List of file paths to include

    Returns:
        Filtered list of locations
    """
    if not locations:
        return []

    # Normalize file paths for comparison
    normalized_file_set = {normalize_path(f) for f in file_paths}
    filtered = []

    for entry in locations:
        file_path = extract_path_from_entry(entry)
        normalized_path = normalize_path(file_path)

        if normalized_path and normalized_path in normalized_file_set:
            filtered.append(entry)

    return filtered
