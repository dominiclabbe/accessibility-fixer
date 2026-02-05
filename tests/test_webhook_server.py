"""
Tests for webhook_server functions

Validates posted_locations unpacking in is_near_existing_comment.
Tests refined deduplication logic that uses issue identity (title/anchor signature).
"""

import logging

# Set up logging for tests
logging.basicConfig(level=logging.DEBUG)


def _create_is_near_existing_comment_function(posted_locations):
    """
    Helper function to create an is_near_existing_comment function with the given posted_locations.
    This matches the refined implementation in app/webhook_server.py.
    """
    # Mock logger for tests
    class MockLogger:
        def debug(self, msg):
            pass
    
    logger = MockLogger()

    def is_near_existing_comment(
        file_path: str, 
        line: int, 
        issue: dict = None,
        range_threshold: int = 5
    ) -> tuple:
        """
        Check if a location is near any existing comment AND if it's the same issue.
        
        Returns:
            Tuple of (should_skip: bool, skip_reason: str, matched_entry: dict or None)
        """
        # Extract issue identity for matching
        issue_title = ""
        issue_anchor = ""
        if issue:
            issue_title = str(issue.get("title", "")).strip()[:50].lower()
            # Get anchor signature
            if issue.get("_anchor_matched_text"):
                issue_anchor = str(issue.get("_anchor_matched_text", "")).strip().lower()
            elif issue.get("anchor_text"):
                issue_anchor = str(issue.get("anchor_text", "")).strip().lower()
        
        for entry in posted_locations:
            try:
                # Parse entry based on type
                existing_file = None
                existing_line = None
                existing_snippet = ""
                
                # Handle dictionary entries
                if isinstance(entry, dict):
                    existing_file = entry.get("file") or entry.get("path")
                    existing_line = entry.get("line")
                    existing_snippet = entry.get("snippet", "")
                    if not existing_file or not existing_line:
                        continue
                # Handle tuple/list entries with 2+ values
                elif isinstance(entry, (tuple, list)) and len(entry) >= 2:
                    existing_file = entry[0]
                    existing_line = entry[1]
                    # Extract body snippet if available (3rd element)
                    if len(entry) >= 3:
                        existing_snippet = str(entry[2]) if entry[2] else ""
                else:
                    # Skip malformed entries
                    continue

                # Check if same file
                if existing_file != file_path:
                    continue
                
                # Calculate distance
                distance = abs(existing_line - line)
                
                # Check if within range
                if distance > range_threshold:
                    continue
                
                # Within range - now check if it's the SAME issue
                is_same_issue = False
                match_reason = ""
                
                # If we have issue metadata, check for identity match
                if issue and (issue_title or issue_anchor):
                    # Normalize existing snippet for comparison
                    existing_title = existing_snippet.strip()[:50].lower()
                    
                    # Check title match
                    if issue_title and existing_title:
                        # Fuzzy match: check if titles are similar enough
                        if issue_title == existing_title:
                            is_same_issue = True
                            match_reason = "exact title match"
                        elif len(issue_title) >= 30 and len(existing_title) >= 30:
                            # For longer titles, check prefix match
                            min_len = min(len(issue_title), len(existing_title))
                            threshold = int(min_len * 0.8)
                            if issue_title[:threshold] == existing_title[:threshold]:
                                is_same_issue = True
                                match_reason = "fuzzy title match"
                    
                    # Check anchor match (if title didn't match)
                    if not is_same_issue and issue_anchor and existing_snippet:
                        # Check if anchor text appears in existing snippet
                        # Normalize both for comparison
                        anchor_normalized = "".join(issue_anchor.split()).lower()[:40]
                        snippet_normalized = "".join(existing_snippet.split()).lower()
                        
                        # Try substring match
                        if anchor_normalized and len(anchor_normalized) >= 3:
                            if anchor_normalized in snippet_normalized:
                                is_same_issue = True
                                match_reason = "anchor signature match"
                        
                        # Also try matching just the keyword (before parenthesis or special chars)
                        if not is_same_issue and anchor_normalized:
                            # Extract keyword: take alphanumeric part before special chars
                            import re
                            keyword_match = re.match(r'^([a-z0-9_]+)', anchor_normalized)
                            if keyword_match:
                                keyword = keyword_match.group(1)
                                if len(keyword) >= 4 and keyword in snippet_normalized:
                                    is_same_issue = True
                                    match_reason = "anchor signature match"
                
                # If same issue detected, skip it
                if is_same_issue:
                    matched_entry = {
                        "file": existing_file,
                        "line": existing_line,
                        "distance": distance,
                        "snippet": existing_snippet[:100],
                    }
                    return (True, match_reason, matched_entry)
                
                # Within range but NOT same issue - this is likely a corrected anchor
                logger.debug(
                    f"Location {file_path}:{line} is near {existing_file}:{existing_line} "
                    f"(distance={distance}) but appears to be a different issue. Not suppressing."
                )
                
            except (TypeError, ValueError, IndexError, AttributeError):
                # Skip malformed entries safely
                continue
        
        # No matching existing comment found
        return (False, "", None)

    return is_near_existing_comment


class TestIsNearExistingComment:
    """Tests for is_near_existing_comment function."""

    def test_with_2_tuples(self):
        """Test that 2-tuples work (backward compatibility) - no issue metadata."""
        posted_locations = {
            ("app/main.py", 10),
            ("app/utils.py", 25),
        }

        is_near_existing_comment = _create_is_near_existing_comment_function(
            posted_locations
        )

        # Without issue metadata, proximity alone doesn't suppress (returns False)
        should_skip, reason, matched = is_near_existing_comment("app/main.py", 10)
        assert should_skip is False
        
        should_skip, reason, matched = is_near_existing_comment("app/main.py", 12)
        assert should_skip is False
        
        # Test outside range
        should_skip, reason, matched = is_near_existing_comment("app/main.py", 20)
        assert should_skip is False
        
        # Test different file
        should_skip, reason, matched = is_near_existing_comment("app/other.py", 10)
        assert should_skip is False

    def test_with_3_tuples(self):
        """Test that 3-tuples work (current format with body_snippet)."""
        posted_locations = {
            ("app/main.py", 10, "Missing alt text"),
            ("app/utils.py", 25, "No ARIA label"),
        }

        is_near_existing_comment = _create_is_near_existing_comment_function(
            posted_locations
        )

        # Without issue metadata, no suppression
        should_skip, reason, matched = is_near_existing_comment("app/main.py", 10)
        assert should_skip is False
        
        # With matching issue
        issue = {"title": "Missing alt text", "file": "app/main.py", "line": 10}
        should_skip, reason, matched = is_near_existing_comment("app/main.py", 10, issue)
        assert should_skip is True
        assert reason == "exact title match"
        assert matched is not None
        assert matched["line"] == 10
        
        # With different issue at nearby location
        different_issue = {"title": "Different issue", "file": "app/main.py", "line": 8}
        should_skip, reason, matched = is_near_existing_comment("app/main.py", 8, different_issue)
        assert should_skip is False  # Should NOT suppress different issue

    def test_with_4_tuples(self):
        """Test that 4+ tuples work (extended format)."""
        posted_locations = {
            ("app/main.py", 10, "Missing alt text", "extra_data"),
        }

        is_near_existing_comment = _create_is_near_existing_comment_function(
            posted_locations
        )

        # With matching issue
        issue = {"title": "Missing alt text"}
        should_skip, reason, matched = is_near_existing_comment("app/main.py", 10, issue)
        assert should_skip is True
        assert reason == "exact title match"

    def test_with_dict_file_key(self):
        """Test that dictionaries with 'file' key work."""
        posted_locations = [
            {"file": "app/main.py", "line": 10, "snippet": "Button missing label"},
        ]

        is_near_existing_comment = _create_is_near_existing_comment_function(
            posted_locations
        )

        # With matching issue
        issue = {"title": "Button missing label"}
        should_skip, reason, matched = is_near_existing_comment("app/main.py", 10, issue)
        assert should_skip is True

    def test_with_dict_path_key(self):
        """Test that dictionaries with 'path' key work."""
        posted_locations = [
            {"path": "app/main.py", "line": 10, "snippet": "Icon without alt"},
        ]

        is_near_existing_comment = _create_is_near_existing_comment_function(
            posted_locations
        )

        # With matching issue
        issue = {"title": "Icon without alt"}
        should_skip, reason, matched = is_near_existing_comment("app/main.py", 10, issue)
        assert should_skip is True

    def test_with_mixed_formats(self):
        """Test that mixed formats work together."""
        posted_locations = [
            ("app/main.py", 10),
            ("app/utils.py", 25, "No ARIA label"),
            ("app/helpers.py", 50, "Missing alt", "extra"),
            ["app/models.py", 15],
        ]

        is_near_existing_comment = _create_is_near_existing_comment_function(
            posted_locations
        )

        # Test with issue metadata
        issue = {"title": "No ARIA label"}
        should_skip, reason, matched = is_near_existing_comment("app/utils.py", 23, issue)
        assert should_skip is True
        assert reason == "exact title match"

    def test_with_malformed_entries(self):
        """Test that malformed entries are skipped safely."""
        posted_locations = [
            ("app/main.py", 10, "Issue title"),  # Valid
            ("single_value",),  # Malformed: only 1 value
            (),  # Malformed: empty tuple
            "not_a_tuple",  # Malformed: string
            123,  # Malformed: number
            None,  # Malformed: None
        ]

        is_near_existing_comment = _create_is_near_existing_comment_function(
            posted_locations
        )

        # Should still find valid entry with matching issue
        issue = {"title": "Issue title"}
        should_skip, reason, matched = is_near_existing_comment("app/main.py", 10, issue)
        assert should_skip is True
        
        # Different issue should not be suppressed
        diff_issue = {"title": "Different issue"}
        should_skip, reason, matched = is_near_existing_comment("app/main.py", 10, diff_issue)
        assert should_skip is False

    def test_near_line_behavior(self):
        """Test that near-line detection works correctly with issue identity."""
        posted_locations = {
            ("app/main.py", 10, "TextField missing label"),
        }

        is_near_existing_comment = _create_is_near_existing_comment_function(
            posted_locations
        )

        # Same issue within range - should suppress
        same_issue = {"title": "TextField missing label"}
        should_skip, reason, matched = is_near_existing_comment("app/main.py", 5, same_issue)
        assert should_skip is True
        assert matched["distance"] == 5
        
        should_skip, reason, matched = is_near_existing_comment("app/main.py", 15, same_issue)
        assert should_skip is True
        assert matched["distance"] == 5
        
        # Same issue outside range - should NOT suppress
        should_skip, reason, matched = is_near_existing_comment("app/main.py", 4, same_issue)
        assert should_skip is False
        
        should_skip, reason, matched = is_near_existing_comment("app/main.py", 16, same_issue)
        assert should_skip is False
        
        # Different issue within range - should NOT suppress (key improvement!)
        diff_issue = {"title": "Button missing label"}
        should_skip, reason, matched = is_near_existing_comment("app/main.py", 12, diff_issue)
        assert should_skip is False

    def test_empty_posted_locations(self):
        """Test with empty posted_locations set."""
        posted_locations = set()

        is_near_existing_comment = _create_is_near_existing_comment_function(
            posted_locations
        )

        # Should return False for any query
        issue = {"title": "Some issue"}
        should_skip, reason, matched = is_near_existing_comment("app/main.py", 10, issue)
        assert should_skip is False

    def test_dict_with_missing_keys(self):
        """Test that dicts with missing keys are skipped."""
        posted_locations = [
            {"path": "app/main.py", "line": 10, "snippet": "Valid issue"},  # Valid
            {"file": "app/utils.py"},  # Missing line
            {"line": 25},  # Missing file/path
            {},  # Empty dict
        ]

        is_near_existing_comment = _create_is_near_existing_comment_function(
            posted_locations
        )

        # Should find the valid dict entry with matching issue
        issue = {"title": "Valid issue"}
        should_skip, reason, matched = is_near_existing_comment("app/main.py", 10, issue)
        assert should_skip is True
        
        # Should not match malformed entries
        issue2 = {"title": "Any issue"}
        should_skip, reason, matched = is_near_existing_comment("app/utils.py", 10, issue2)
        assert should_skip is False


class TestRefinedDeduplicationLogic:
    """
    Regression tests for refined deduplication logic.
    Tests the scenarios from the problem statement.
    """
    
    def test_corrected_anchor_not_suppressed(self):
        """
        Test that a corrected anchor is NOT suppressed even if near a mis-anchored comment.
        
        Scenario: A TextField issue was previously mis-anchored to a Button line.
        Now the corrected TextField issue should be posted even though it's within
        proximity of the existing mis-anchored comment.
        """
        # Existing comment at line 460 was for TextField but mis-anchored to Button
        posted_locations = [
            ("androidApp/src/main/kotlin/com/app/App.kt", 460, "Button missing label"),
        ]
        
        is_near_existing_comment = _create_is_near_existing_comment_function(
            posted_locations
        )
        
        # New issue: TextField at line 465 (within 5 lines of existing comment)
        # This is the CORRECTED anchor for a different issue
        textfield_issue = {
            "title": "TextField missing hint",  # Different title
            "file": "androidApp/src/main/kotlin/com/app/App.kt",
            "line": 465,
            "anchor_text": "TextField(",
        }
        
        # Should NOT be suppressed because it's a different issue
        should_skip, reason, matched = is_near_existing_comment(
            "androidApp/src/main/kotlin/com/app/App.kt",
            465,
            textfield_issue
        )
        assert should_skip is False, "Corrected anchor for different issue should NOT be suppressed"
    
    def test_same_issue_already_posted_suppressed(self):
        """
        Test that the same issue already posted at a nearby line SHOULD be suppressed.
        
        Scenario: A TextField issue was correctly posted at line 460.
        The AI returns the same issue at line 462 (slightly different line due to
        re-anchoring or variance). This should be suppressed as a duplicate.
        """
        # Existing comment at line 460
        posted_locations = [
            ("androidApp/src/main/kotlin/com/app/App.kt", 460, "TextField missing hint"),
        ]
        
        is_near_existing_comment = _create_is_near_existing_comment_function(
            posted_locations
        )
        
        # Same issue at nearby line
        same_issue = {
            "title": "TextField missing hint",  # Same title
            "file": "androidApp/src/main/kotlin/com/app/App.kt",
            "line": 462,
        }
        
        # Should be suppressed because it's the same issue
        should_skip, reason, matched = is_near_existing_comment(
            "androidApp/src/main/kotlin/com/app/App.kt",
            462,
            same_issue
        )
        assert should_skip is True, "Same issue at nearby line should be suppressed"
        assert reason == "exact title match"
        assert matched is not None
        assert matched["line"] == 460
        assert matched["distance"] == 2
    
    def test_anchor_signature_matching(self):
        """
        Test that anchor signature matching works for deduplication.
        
        Even if titles differ slightly, anchor signature can identify duplicates.
        """
        posted_locations = [
            ("app/UI.swift", 100, "Slider without accessibility label"),
        ]
        
        is_near_existing_comment = _create_is_near_existing_comment_function(
            posted_locations
        )
        
        # Issue with anchor_text that matches the existing snippet
        issue_with_anchor = {
            "title": "Slider lacks label",  # Slightly different title
            "file": "app/UI.swift",
            "line": 102,
            "anchor_text": "Slider(",  # This should match "Slider" in snippet
        }
        
        should_skip, reason, matched = is_near_existing_comment(
            "app/UI.swift",
            102,
            issue_with_anchor
        )
        # Should match by anchor signature
        assert should_skip is True
        assert "anchor signature match" in reason
    
    def test_fuzzy_title_matching(self):
        """
        Test that fuzzy title matching works for long titles.
        
        Titles with minor variations should still match if they're similar enough.
        """
        posted_locations = [
            ("app/View.kt", 50, 
             "Interactive element missing accessibility label and hint for screen readers"),
        ]
        
        is_near_existing_comment = _create_is_near_existing_comment_function(
            posted_locations
        )
        
        # Issue with slightly different but similar title
        similar_issue = {
            "title": "Interactive element missing accessibility label and hint for screen reader support",
            "file": "app/View.kt",
            "line": 52,
        }
        
        should_skip, reason, matched = is_near_existing_comment(
            "app/View.kt",
            52,
            similar_issue
        )
        # Should match by fuzzy title matching (80% threshold)
        assert should_skip is True
        assert "title match" in reason
    
    def test_multiple_different_issues_near_each_other(self):
        """
        Test that multiple different issues can be posted near each other.
        
        This validates that proximity alone doesn't suppress issues.
        """
        posted_locations = [
            ("app/Form.tsx", 100, "Button missing label"),
            ("app/Form.tsx", 105, "Input missing placeholder"),
        ]
        
        is_near_existing_comment = _create_is_near_existing_comment_function(
            posted_locations
        )
        
        # New different issue at line 103 (between existing comments)
        new_issue = {
            "title": "Image missing alt text",  # Different from both existing
            "file": "app/Form.tsx",
            "line": 103,
        }
        
        should_skip, reason, matched = is_near_existing_comment(
            "app/Form.tsx",
            103,
            new_issue
        )
        # Should NOT be suppressed
        assert should_skip is False
    
    def test_resolved_line_in_matched_entry(self):
        """
        Test that matched_entry includes useful debug information.
        """
        posted_locations = [
            ("app/main.py", 100, "Missing aria-label on interactive element"),
        ]
        
        is_near_existing_comment = _create_is_near_existing_comment_function(
            posted_locations
        )
        
        same_issue = {
            "title": "Missing aria-label on interactive element",
            "file": "app/main.py",
            "line": 102,
            "_resolved_line": 102,  # Set by semantic anchor resolver
        }
        
        should_skip, reason, matched = is_near_existing_comment(
            "app/main.py",
            102,
            same_issue
        )
        
        assert should_skip is True
        assert matched is not None
        assert matched["file"] == "app/main.py"
        assert matched["line"] == 100
        assert matched["distance"] == 2
        assert "snippet" in matched
        assert "Missing aria-label" in matched["snippet"]
    
    def test_backward_compat_without_issue_metadata(self):
        """
        Test backward compatibility: when no issue metadata provided,
        proximity-based check returns False (doesn't suppress).
        
        This ensures the new logic is additive and doesn't break existing
        code that might call without issue parameter.
        """
        posted_locations = [
            ("app/main.py", 100, "Some issue"),
        ]
        
        is_near_existing_comment = _create_is_near_existing_comment_function(
            posted_locations
        )
        
        # Call without issue parameter (backward compat)
        should_skip, reason, matched = is_near_existing_comment("app/main.py", 102)
        assert should_skip is False  # Should NOT suppress without issue identity
        
        # Call with None issue (backward compat)
        should_skip, reason, matched = is_near_existing_comment("app/main.py", 102, None)
        assert should_skip is False
    
    def test_anchor_matched_text_priority(self):
        """
        Test that _anchor_matched_text takes priority over anchor_text.
        
        _anchor_matched_text is set by semantic anchor resolver and contains
        the actual matched line from the diff.
        """
        posted_locations = [
            ("app/UI.kt", 200, "Toggle without label"),
        ]
        
        is_near_existing_comment = _create_is_near_existing_comment_function(
            posted_locations
        )
        
        # Issue with both _anchor_matched_text and anchor_text
        issue = {
            "title": "Toggle needs label",  # Different title
            "file": "app/UI.kt",
            "line": 203,
            "_anchor_matched_text": "Toggle(\"Enable notifications\", isOn:",  # Resolved
            "anchor_text": "Toggle(",  # Original from AI
        }
        
        should_skip, reason, matched = is_near_existing_comment(
            "app/UI.kt",
            203,
            issue
        )
        
        # Should use _anchor_matched_text for matching
        assert should_skip is True
        assert "anchor signature match" in reason
