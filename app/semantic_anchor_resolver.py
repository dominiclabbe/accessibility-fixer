"""
Semantic Anchor Resolver

Resolves issue line numbers to semantically correct UI element declarations/call sites
using framework-specific heuristics. Prevents comment mis-anchoring by matching issues
to the actual UI elements they reference, not just the nearest syntactically valid line.

Supports:
- Android Compose/Kotlin
- Android XML layouts
- iOS SwiftUI
- iOS UIKit (Swift/Objective-C)
- Web (React/JSX/TSX/HTML/CSS)
"""

import re
from typing import Dict, List, Optional, Tuple
from pathlib import Path


class SemanticAnchorResolver:
    """Resolves issue line numbers to semantic UI element anchors."""

    # Framework-specific UI element patterns
    # These are used to identify relevant lines in diffs
    COMPOSE_PATTERNS = [
        r'\bSlider\s*\(',
        r'\bSwitch\s*\(',
        r'\bButton\s*\(',
        r'\bText\s*\(',
        r'\bTextField\s*\(',
        r'\bOutlinedTextField\s*\(',
        r'\bIcon\s*\(',
        r'\.clickable\s*[{\(]',
        r'\.semantics\s*[{\(]',
        r'\bModifier\.',
    ]

    ANDROID_XML_PATTERNS = [
        r'android:contentDescription',
        r'android:hint',
        r'android:text\s*=',
        r'android:labelFor',
        r'<Button\b',
        r'<ImageView\b',
        r'<TextView\b',
        r'<EditText\b',
        r'<Switch\b',
        r'<CheckBox\b',
        r'<RadioButton\b',
        r'<Spinner\b',
        r'<SeekBar\b',
    ]

    SWIFTUI_PATTERNS = [
        r'\bText\s*\(',
        r'\bButton\s*\(',
        r'\bToggle\s*\(',
        r'\bSlider\s*\(',
        r'\bTextField\s*\(',
        r'\bSecureField\s*\(',
        r'\.accessibilityLabel\s*\(',
        r'\.accessibilityHint\s*\(',
        r'\.accessibilityValue\s*\(',
        r'\.accessibilityAddTraits\s*\(',
    ]

    UIKIT_PATTERNS = [
        r'\bUIButton\b',
        r'\bUILabel\b',
        r'\bUIImageView\b',
        r'\bUITextField\b',
        r'\bUISwitch\b',
        r'\bUISlider\b',
        r'\.accessibilityLabel\s*=',
        r'\.accessibilityHint\s*=',
        r'\.accessibilityTraits\s*=',
    ]

    REACT_WEB_PATTERNS = [
        r'<button\b',
        r'<input\b',
        r'<img\b',
        r'<label\b',
        r'<select\b',
        r'<textarea\b',
        r'aria-label\s*=',
        r'aria-labelledby\s*=',
        r'aria-describedby\s*=',
        r'role\s*=',
        r'alt\s*=',
        r'onClick\s*=',
    ]

    # Map issue keywords to specific UI element patterns
    ISSUE_KEYWORD_PATTERNS = {
        # Common UI elements
        'slider': [r'\bSlider\s*\(', r'<SeekBar\b', r'\bUISlider\b', r'<input[^>]*type\s*=\s*["\']range'],
        'switch': [r'\bSwitch\s*\(', r'<Switch\b', r'\bUISwitch\b', r'<input[^>]*type\s*=\s*["\']checkbox'],
        'toggle': [r'\bToggle\s*\(', r'\bSwitch\s*\(', r'<Switch\b'],
        'button': [r'\bButton\s*\(', r'<Button\b', r'\bUIButton\b', r'<button\b'],
        'text': [r'\bText\s*\(', r'<TextView\b', r'\bUILabel\b', r'<label\b'],
        'textfield': [r'\bTextField\s*\(', r'\bOutlinedTextField\s*\(', r'<EditText\b', r'\bUITextField\b', r'<input\b'],
        'image': [r'<ImageView\b', r'\bUIImageView\b', r'<img\b', r'\bIcon\s*\('],
        'checkbox': [r'<CheckBox\b', r'<input[^>]*type\s*=\s*["\']checkbox'],
        'radio': [r'<RadioButton\b', r'<input[^>]*type\s*=\s*["\']radio'],
        'label': [r'accessibilityLabel', r'android:contentDescription', r'aria-label', r'alt\s*='],
        'hint': [r'accessibilityHint', r'android:hint', r'aria-describedby'],
        'contentdescription': [r'android:contentDescription', r'contentDescription\s*='],
    }

    @staticmethod
    def extract_commentable_line_texts(
        diff_text: str,
        commentable_lines: Dict[str, List[int]]
    ) -> Dict[str, Dict[int, str]]:
        """
        Extract the text content of commentable lines from a diff.

        Args:
            diff_text: Unified diff text
            commentable_lines: Dict mapping file paths to lists of commentable line numbers

        Returns:
            Dict mapping file paths to dicts of {line_number: line_text}
        """
        line_texts = {}
        current_file = None
        current_line = 0
        in_hunk = False

        for line in diff_text.split('\n'):
            # Match file header: +++ b/path/to/file
            if line.startswith('+++ b/'):
                current_file = line[6:]  # Skip '+++ b/'
                if current_file in commentable_lines:
                    line_texts[current_file] = {}
                in_hunk = False
                continue

            # Match hunk header: @@ -old_start,old_count +new_start,new_count @@
            hunk_match = re.match(r'^@@ -\d+(?:,\d+)? \+(\d+)(?:,\d+)? @@', line)
            if hunk_match and current_file:
                current_line = int(hunk_match.group(1))
                in_hunk = True
                continue

            # Process lines in hunk
            if in_hunk and current_file and current_file in commentable_lines:
                if line.startswith('+') and not line.startswith('+++'):
                    # Added line
                    if current_line in commentable_lines[current_file]:
                        line_texts[current_file][current_line] = line[1:]  # Remove '+'
                    current_line += 1
                elif line.startswith(' '):
                    # Context line
                    if current_line in commentable_lines[current_file]:
                        line_texts[current_file][current_line] = line[1:]  # Remove ' '
                    current_line += 1
                elif line.startswith('-'):
                    # Removed line - don't increment
                    pass

        return line_texts

    @staticmethod
    def extract_anchor_candidates(issue: Dict, file_extension: Optional[str] = None) -> List[str]:
        """
        Extract anchor text candidates from issue metadata.

        Looks for explicit anchor hints and derives candidates from:
        - issue.get('anchor_text') or issue.get('anchor')
        - Keywords in title/description
        - WCAG SC specific patterns
        - File extension-based framework detection

        Args:
            issue: Issue dict
            file_extension: Optional file extension (e.g., '.kt', '.swift', '.tsx') for framework-specific inference

        Returns:
            List of anchor text candidates (e.g., ['Slider(', 'slider'])
        """
        candidates = []

        # 1. Check for explicit anchor field (highest priority)
        explicit_anchor = issue.get('anchor_text') or issue.get('anchor')
        if explicit_anchor:
            candidates.append(str(explicit_anchor))

        # 2. Extract from title and description
        title = issue.get('title', '').lower()
        description = issue.get('description', '').lower()
        combined_text = f"{title} {description}"

        # Check for keyword matches
        for keyword, patterns in SemanticAnchorResolver.ISSUE_KEYWORD_PATTERNS.items():
            if keyword in combined_text:
                candidates.extend(patterns)

        # 3. Extract specific element names from title/description
        # Look for capitalized UI element names (e.g., "Slider", "Button")
        element_name_pattern = r'\b([A-Z][a-z]+(?:Field|View|Button|Text|Icon|Slider|Switch|Toggle|Label))\b'
        for match in re.finditer(element_name_pattern, issue.get('title', '') + ' ' + issue.get('description', '')):
            element_name = match.group(1)
            candidates.append(element_name)  # Exact match
            candidates.append(f'{element_name}(')  # Function call
            candidates.append(f'<{element_name}')  # XML/HTML tag

        # 4. Add framework-specific patterns based on file extension
        if file_extension:
            ext = file_extension.lower()
            # Compose/Kotlin
            if ext in ['.kt', '.kts']:
                candidates.extend(SemanticAnchorResolver.COMPOSE_PATTERNS)
            # Android XML
            elif ext == '.xml':
                candidates.extend(SemanticAnchorResolver.ANDROID_XML_PATTERNS)
            # SwiftUI/Swift
            elif ext == '.swift':
                candidates.extend(SemanticAnchorResolver.SWIFTUI_PATTERNS)
                candidates.extend(SemanticAnchorResolver.UIKIT_PATTERNS)
            # React/Web
            elif ext in ['.tsx', '.jsx', '.ts', '.js', '.html', '.css']:
                candidates.extend(SemanticAnchorResolver.REACT_WEB_PATTERNS)

        return candidates

    @staticmethod
    def resolve_anchor_line(
        issue: Dict,
        right_line_to_text: Dict[int, str],
        fallback_line: Optional[int] = None,
        file_extension: Optional[str] = None,
        debug: bool = False
    ) -> Tuple[Optional[int], Optional[str]]:
        """
        Resolve issue anchor to exact line using diff-grounded algorithm.

        This is the primary deterministic anchoring function that implements:
        a) If issue.anchor_text exists: search for it in right_line_to_text
        b) If missing: infer candidates from issue metadata and file extension
        c) If still no match: return None (caller should use fallback)

        When multiple matches found, chooses closest to issue.line if provided,
        otherwise closest to fallback_line, or first match in line-number order.

        Args:
            issue: Issue dict with 'line', 'title', 'description', optionally 'anchor_text'
            right_line_to_text: Dict mapping commentable RIGHT-side line numbers to their text
            fallback_line: Optional fallback line number for tie-breaking
            file_extension: Optional file extension for framework inference
            debug: If True, print debug information

        Returns:
            Tuple of (resolved_line_number, matched_text) or (None, None) if no match
        """
        if not right_line_to_text:
            if debug:
                print("  [anchor] No line texts available")
            return None, None

        # Step 1: Get anchor text from issue or infer candidates
        explicit_anchor = issue.get('anchor_text') or issue.get('anchor')
        
        if explicit_anchor:
            # Use explicit anchor_text
            anchor_candidates = [str(explicit_anchor)]
            if debug:
                print(f"  [anchor] Using explicit anchor_text: {explicit_anchor}")
        else:
            # Infer candidates from issue metadata
            anchor_candidates = SemanticAnchorResolver.extract_anchor_candidates(issue, file_extension)
            if debug:
                print(f"  [anchor] Inferred {len(anchor_candidates)} candidates from issue metadata")

        if not anchor_candidates:
            if debug:
                print("  [anchor] No anchor candidates found")
            return None, None

        # Step 2: Search for candidates in right_line_to_text
        matches = []  # List of (line_num, matched_text, candidate_pattern)
        
        for line_num, line_text in right_line_to_text.items():
            if not line_text:
                continue
            
            for candidate in anchor_candidates:
                # Check if candidate is a regex pattern
                is_regex_pattern = any(char in candidate for char in [r'\b', r'\s', r'\(', r'[', r'^', r'$', r'.', r'*'])
                
                try:
                    if is_regex_pattern:
                        # Use as regex pattern
                        if re.search(candidate, line_text):
                            matches.append((line_num, line_text.strip(), candidate))
                            break
                        # Try case-insensitive for keyword patterns
                        elif re.search(candidate, line_text, re.IGNORECASE):
                            matches.append((line_num, line_text.strip(), candidate))
                            break
                    else:
                        # Try exact substring match (case-sensitive)
                        if candidate in line_text:
                            matches.append((line_num, line_text.strip(), candidate))
                            break
                        # Try case-insensitive substring match
                        elif candidate.lower() in line_text.lower():
                            matches.append((line_num, line_text.strip(), candidate))
                            break
                except re.error:
                    # Invalid regex, skip
                    continue

        if not matches:
            if debug:
                print(f"  [anchor] No matches found for {len(anchor_candidates)} candidates")
            return None, None

        if debug:
            print(f"  [anchor] Found {len(matches)} matches")

        # Step 3: Choose best match based on proximity
        if len(matches) == 1:
            resolved_line, matched_text, _ = matches[0]
            if debug:
                print(f"  [anchor] Single match at line {resolved_line}: {matched_text[:60]}")
            return resolved_line, matched_text

        # Multiple matches - choose closest to proposed line or fallback
        reference_line = issue.get('line', 0) or fallback_line or 0
        
        if reference_line > 0:
            # Sort by distance from reference line
            matches_with_distance = [
                (line, text, abs(line - reference_line), pattern)
                for line, text, pattern in matches
            ]
            matches_with_distance.sort(key=lambda x: x[2])  # Sort by distance
            resolved_line, matched_text, _, _ = matches_with_distance[0]
            if debug:
                print(f"  [anchor] Multiple matches, chose line {resolved_line} (closest to {reference_line}): {matched_text[:60]}")
        else:
            # No reference line, choose first match in line order
            matches.sort(key=lambda x: x[0])  # Sort by line number
            resolved_line, matched_text, _ = matches[0]
            if debug:
                print(f"  [anchor] Multiple matches, chose first at line {resolved_line}: {matched_text[:60]}")

        return resolved_line, matched_text

    @staticmethod
    def resolve_issue_line(
        issue: Dict,
        file_path: str,
        commentable_lines: List[int],
        line_texts: Dict[int, str],
        max_distance: int = 20
    ) -> Optional[int]:
        """
        Resolve issue line to a semantically correct anchor.

        Algorithm:
        1. Extract anchor candidates from issue metadata
        2. Search for candidates in commentable line texts
        3. Choose match closest to model-proposed line
        4. Return resolved line or None if no match found

        Args:
            issue: Issue dict with 'line', 'title', 'description', etc.
            file_path: File path for this issue
            commentable_lines: List of commentable line numbers for this file
            line_texts: Dict mapping line numbers to their text content
            max_distance: Maximum distance from proposed line to consider

        Returns:
            Resolved line number or None if no semantic anchor found
        """
        if not commentable_lines or not line_texts:
            return None

        proposed_line = issue.get('line', 0)
        if proposed_line <= 0:
            return None

        # Extract anchor candidates
        candidates = SemanticAnchorResolver.extract_anchor_candidates(issue)
        if not candidates:
            return None

        # Find all matching lines
        matches = []
        for line_num in commentable_lines:
            line_text = line_texts.get(line_num, '')
            if not line_text:
                continue

            for candidate in candidates:
                # Check if candidate is a regex pattern (contains regex metacharacters)
                is_regex_pattern = any(char in candidate for char in [r'\b', r'\s', r'\(', r'[', r'^', r'$'])
                
                try:
                    # Try exact match first (case-sensitive for code patterns)
                    pattern = candidate if is_regex_pattern else re.escape(candidate)
                    if re.search(pattern, line_text):
                        distance = abs(line_num - proposed_line)
                        matches.append((line_num, distance, candidate))
                        break
                    # Try case-insensitive match for keywords
                    elif re.search(pattern, line_text, re.IGNORECASE):
                        distance = abs(line_num - proposed_line)
                        matches.append((line_num, distance, candidate))
                        break
                except re.error:
                    # If regex is invalid, skip this candidate
                    continue

        if not matches:
            return None

        # Filter by max distance
        matches = [(line, dist, cand) for line, dist, cand in matches if dist <= max_distance]
        if not matches:
            return None

        # Sort by distance (prefer closer to proposed line)
        matches.sort(key=lambda x: x[1])

        # Return closest match
        resolved_line = matches[0][0]
        return resolved_line

    @staticmethod
    def get_all_framework_patterns() -> List[str]:
        """
        Get all UI element patterns across all frameworks.

        Returns:
            List of regex patterns
        """
        return (
            SemanticAnchorResolver.COMPOSE_PATTERNS +
            SemanticAnchorResolver.ANDROID_XML_PATTERNS +
            SemanticAnchorResolver.SWIFTUI_PATTERNS +
            SemanticAnchorResolver.UIKIT_PATTERNS +
            SemanticAnchorResolver.REACT_WEB_PATTERNS
        )
