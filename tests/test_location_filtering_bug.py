"""
Tests for location filtering bug - Web phase filtering to zero
"""

import pytest
from app.platform_bucketing import filter_locations_for_files


class TestLocationFilteringBug:
    """Test cases to reproduce and fix the Web phase filtering bug."""
    
    def test_filter_existing_comments_3tuple_format(self):
        """
        Test that existing comments (3-tuple format) are filtered correctly.
        
        Existing comments from _get_existing_comment_locations() are 3-tuples:
        (file_path, line, body_snippet)
        """
        # Existing comments from GitHub API
        existing_comments = [
            ("web/src/components/Button.tsx", 10, "Missing aria-label"),
            ("web/src/styles.css", 20, "Color contrast too low"),
            ("android/MainActivity.kt", 30, "Missing content description"),
            ("ios/ViewController.swift", 40, "Missing accessibility label"),
        ]
        
        # Phase: Web files only
        web_files = [
            "web/src/components/Button.tsx",
            "web/src/styles.css",
        ]
        
        filtered = filter_locations_for_files(existing_comments, web_files)
        
        # Should include 2 web comments
        assert len(filtered) == 2
        assert ("web/src/components/Button.tsx", 10, "Missing aria-label") in filtered
        assert ("web/src/styles.css", 20, "Color contrast too low") in filtered
    
    def test_filter_review_threads_dict_format(self):
        """
        Test that review threads (dict format) are filtered correctly.
        
        Review threads from get_review_threads() are dicts with "path" key.
        """
        # Review threads from GitHub API
        review_threads = [
            {
                "path": "web/src/components/Button.tsx",
                "line": 10,
                "body": "Missing aria-label",
                "user": "bot",
                "created_at": "2024-01-01",
                "replies": [],
            },
            {
                "path": "web/src/styles.css",
                "line": 20,
                "body": "Color contrast too low",
                "user": "bot",
                "created_at": "2024-01-01",
                "replies": [],
            },
            {
                "path": "android/MainActivity.kt",
                "line": 30,
                "body": "Missing content description",
                "user": "bot",
                "created_at": "2024-01-01",
                "replies": [],
            },
        ]
        
        # Phase: Web files only
        web_files = [
            "web/src/components/Button.tsx",
            "web/src/styles.css",
        ]
        
        filtered = filter_locations_for_files(review_threads, web_files)
        
        # Should include 2 web threads
        assert len(filtered) == 2
        assert filtered[0]["path"] == "web/src/components/Button.tsx"
        assert filtered[1]["path"] == "web/src/styles.css"
    
    def test_path_normalization_backslashes(self):
        """Test that backslashes in paths are normalized to forward slashes."""
        # Some systems may return backslashes
        locations = [
            ("web\\src\\Button.tsx", 10, "Issue"),
            ("android/MainActivity.kt", 20, "Issue"),
        ]
        
        # File list uses forward slashes
        files = ["web/src/Button.tsx"]
        
        filtered = filter_locations_for_files(locations, files)
        
        # Should match after normalization
        assert len(filtered) == 1
    
    def test_path_normalization_leading_slash(self):
        """Test that leading slashes are stripped before comparison."""
        # GitHub may return paths with leading slash
        locations = [
            ("/web/src/Button.tsx", 10, "Issue"),
            ("web/src/Button.tsx", 20, "Issue"),
        ]
        
        # File list without leading slash
        files = ["web/src/Button.tsx"]
        
        filtered = filter_locations_for_files(locations, files)
        
        # Both should match after normalization
        assert len(filtered) == 2
    
    def test_review_threads_with_nested_comment_path(self):
        """
        Test filtering when path is in a nested comment object.
        
        Some GitHub APIs may return threads with path in nested structures.
        """
        # Hypothetical nested structure
        review_threads = [
            {
                "comment": {
                    "path": "web/Button.tsx",
                    "line": 10,
                },
                "body": "Issue",
            },
            {
                "path": "android/MainActivity.kt",
                "line": 20,
                "body": "Issue",
            },
        ]
        
        files = ["web/Button.tsx"]
        
        filtered = filter_locations_for_files(review_threads, files)
        
        # Should handle nested path
        # This test may fail initially - we'll fix it
        assert len(filtered) >= 1
    
    def test_empty_locations_list(self):
        """Test that empty locations list returns empty result."""
        filtered = filter_locations_for_files([], ["web/Button.tsx"])
        assert filtered == []
    
    def test_empty_files_list(self):
        """Test that empty files list returns empty result."""
        locations = [("web/Button.tsx", 10, "Issue")]
        filtered = filter_locations_for_files(locations, [])
        assert filtered == []
    
    def test_mixed_formats_in_same_list(self):
        """Test filtering works with mixed tuple and dict formats."""
        locations = [
            ("web/Button.tsx", 10, "Issue"),  # 3-tuple
            {"path": "web/styles.css", "line": 20},  # dict
            {"file": "android/MainActivity.kt", "line": 30},  # dict with "file" key
        ]
        
        files = ["web/Button.tsx", "web/styles.css"]
        
        filtered = filter_locations_for_files(locations, files)
        
        # Should include both web entries
        assert len(filtered) == 2
    
    def test_rerun_scenario_web_phase_matches_existing_comments(self):
        """
        Regression test: In a rerun scenario, web phase should not filter 
        existing comments to 0 when matching web paths exist.
        
        This simulates the reported bug where Web phase shows:
        "Filtered existing comments: 0 (out of 30 total)" even though 
        there are web comments.
        """
        # Simulate existing comments from a previous review across all platforms
        existing_comments = [
            # Android comments
            ("android/MainActivity.kt", 10, "Missing content description"),
            ("android/Fragment.java", 20, "Missing accessibility delegate"),
            # iOS comments
            ("ios/ViewController.swift", 30, "Missing accessibility label"),
            ("ios/Bridge.m", 40, "Missing accessibility hint"),
            # Web comments - these should be matched!
            ("web/src/components/Button.tsx", 50, "Missing aria-label"),
            ("web/src/components/Form.tsx", 60, "Missing form labels"),
            ("web/src/styles.css", 70, "Color contrast too low"),
            ("web/public/index.html", 80, "Missing lang attribute"),
        ]
        
        # Simulate Web phase with its platform files
        web_files = [
            "web/src/components/Button.tsx",
            "web/src/components/Form.tsx",
            "web/src/styles.css",
            "web/public/index.html",
        ]
        
        # Filter for Web phase
        web_comments = filter_locations_for_files(existing_comments, web_files)
        
        # CRITICAL: Should NOT be 0! Should match all 4 web comments
        assert len(web_comments) > 0, "Web phase should find matching existing comments"
        assert len(web_comments) == 4, f"Expected 4 web comments, got {len(web_comments)}"
        
        # Verify the right comments were filtered
        web_paths = {comment[0] for comment in web_comments}
        assert "web/src/components/Button.tsx" in web_paths
        assert "web/src/components/Form.tsx" in web_paths
        assert "web/src/styles.css" in web_paths
        assert "web/public/index.html" in web_paths
    
    def test_rerun_scenario_web_phase_matches_review_threads(self):
        """
        Regression test: In a rerun scenario, web phase should not filter 
        review threads to 0 when matching web paths exist.
        """
        # Simulate review threads from a previous review across all platforms
        review_threads = [
            # Android threads
            {"path": "android/MainActivity.kt", "line": 10, "body": "Issue"},
            {"path": "android/Fragment.java", "line": 20, "body": "Issue"},
            # iOS threads
            {"path": "ios/ViewController.swift", "line": 30, "body": "Issue"},
            {"path": "ios/Bridge.m", "line": 40, "body": "Issue"},
            # Web threads - these should be matched!
            {"path": "web/src/components/Button.tsx", "line": 50, "body": "Issue"},
            {"path": "web/src/components/Form.tsx", "line": 60, "body": "Issue"},
            {"path": "web/src/styles.css", "line": 70, "body": "Issue"},
        ]
        
        # Simulate Web phase with its platform files
        web_files = [
            "web/src/components/Button.tsx",
            "web/src/components/Form.tsx",
            "web/src/styles.css",
        ]
        
        # Filter for Web phase
        web_threads = filter_locations_for_files(review_threads, web_files)
        
        # CRITICAL: Should NOT be 0! Should match all 3 web threads
        assert len(web_threads) > 0, "Web phase should find matching existing threads"
        assert len(web_threads) == 3, f"Expected 3 web threads, got {len(web_threads)}"
        
        # Verify the right threads were filtered
        web_paths = {thread["path"] for thread in web_threads}
        assert "web/src/components/Button.tsx" in web_paths
        assert "web/src/components/Form.tsx" in web_paths
        assert "web/src/styles.css" in web_paths
