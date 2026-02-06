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


def bucket_files_by_platform(changed_files: List[str], pr_diff: str) -> Dict[str, List[str]]:
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


def filter_locations_for_files(
    locations: List, 
    file_paths: List[str]
) -> List:
    """
    Filter a list of locations (comments/threads) to only include those
    matching the given file paths.
    
    Supports multiple entry formats:
    - Tuples: (file, line, ...) where file is first element
    - Dicts: {'file': ...} or {'path': ...}
    
    Args:
        locations: List of location entries (tuples or dicts)
        file_paths: List of file paths to include
        
    Returns:
        Filtered list of locations
    """
    if not locations:
        return []
    
    file_set = set(file_paths)
    filtered = []
    
    for entry in locations:
        file_path = None
        
        if isinstance(entry, tuple) and len(entry) >= 1:
            file_path = entry[0]
        elif isinstance(entry, dict):
            file_path = entry.get("file") or entry.get("path")
        
        if file_path and file_path in file_set:
            filtered.append(entry)
    
    return filtered
