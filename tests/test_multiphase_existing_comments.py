"""
Tests to ensure existing comments persist across all phases.

This test addresses the concern that existing comments might only be
available on the first running phase and then ignored for following ones.
"""

import pytest
from app.platform_bucketing import filter_locations_for_files


class TestMultiphaseExistingComments:
    """Test that existing comments work correctly across multiple phases."""

    def test_existing_comments_persist_across_all_phases(self):
        """
        Test that the same existing_locations set can be used across
        multiple phases without being modified.

        This simulates the webhook_server behavior where:
        1. existing_locations is fetched ONCE at the start
        2. Each phase filters existing_locations for its files
        3. The original existing_locations should remain unchanged
        """
        # Simulate existing comments from a previous full review
        existing_locations = {
            # Android comments
            ("android/MainActivity.kt", 10, "Missing content description"),
            ("android/Fragment.java", 20, "Missing accessibility delegate"),
            # iOS comments
            ("ios/ViewController.swift", 30, "Missing accessibility label"),
            ("ios/Bridge.m", 40, "Missing accessibility hint"),
            # Web comments
            ("web/src/Button.tsx", 50, "Missing aria-label"),
            ("web/src/Form.tsx", 60, "Missing form labels"),
        }

        # Store original size for comparison
        original_size = len(existing_locations)

        # PHASE 1: Android
        android_files = ["android/MainActivity.kt", "android/Fragment.java"]
        android_comments = filter_locations_for_files(
            list(existing_locations), android_files
        )

        # Should find 2 Android comments
        assert len(android_comments) == 2
        android_paths = {comment[0] for comment in android_comments}
        assert "android/MainActivity.kt" in android_paths
        assert "android/Fragment.java" in android_paths

        # PHASE 2: iOS
        ios_files = ["ios/ViewController.swift", "ios/Bridge.m"]
        ios_comments = filter_locations_for_files(list(existing_locations), ios_files)

        # Should STILL find 2 iOS comments (existing_locations unchanged)
        assert len(ios_comments) == 2, (
            f"iOS phase should find 2 comments but found {len(ios_comments)}. "
            "This suggests existing_locations was modified during Android phase."
        )
        ios_paths = {comment[0] for comment in ios_comments}
        assert "ios/ViewController.swift" in ios_paths
        assert "ios/Bridge.m" in ios_paths

        # PHASE 3: Web
        web_files = ["web/src/Button.tsx", "web/src/Form.tsx"]
        web_comments = filter_locations_for_files(list(existing_locations), web_files)

        # Should STILL find 2 Web comments (existing_locations unchanged)
        assert len(web_comments) == 2, (
            f"Web phase should find 2 comments but found {len(web_comments)}. "
            "This suggests existing_locations was modified during previous phases."
        )
        web_paths = {comment[0] for comment in web_comments}
        assert "web/src/Button.tsx" in web_paths
        assert "web/src/Form.tsx" in web_paths

        # Verify original set was never modified
        assert (
            len(existing_locations) == original_size
        ), "existing_locations should not be modified during filtering"

    def test_review_threads_persist_across_all_phases(self):
        """
        Test that the same review_threads list can be used across
        multiple phases without being modified.
        """
        # Simulate review threads from a previous full review
        review_threads = [
            # Android threads
            {
                "path": "android/MainActivity.kt",
                "line": 10,
                "body": "Missing content description",
            },
            {
                "path": "android/Fragment.java",
                "line": 20,
                "body": "Missing accessibility delegate",
            },
            # iOS threads
            {
                "path": "ios/ViewController.swift",
                "line": 30,
                "body": "Missing accessibility label",
            },
            {"path": "ios/Bridge.m", "line": 40, "body": "Missing accessibility hint"},
            # Web threads
            {"path": "web/src/Button.tsx", "line": 50, "body": "Missing aria-label"},
            {
                "path": "web/src/Form.tsx",
                "line": 60,
                "body": "Missing form labels",
            },
        ]

        # Store original size for comparison
        original_size = len(review_threads)

        # PHASE 1: Android
        android_files = ["android/MainActivity.kt", "android/Fragment.java"]
        android_threads = filter_locations_for_files(review_threads, android_files)

        # Should find 2 Android threads
        assert len(android_threads) == 2
        android_paths = {thread["path"] for thread in android_threads}
        assert "android/MainActivity.kt" in android_paths
        assert "android/Fragment.java" in android_paths

        # PHASE 2: iOS
        ios_files = ["ios/ViewController.swift", "ios/Bridge.m"]
        ios_threads = filter_locations_for_files(review_threads, ios_files)

        # Should STILL find 2 iOS threads (review_threads unchanged)
        assert len(ios_threads) == 2, (
            f"iOS phase should find 2 threads but found {len(ios_threads)}. "
            "This suggests review_threads was modified during Android phase."
        )
        ios_paths = {thread["path"] for thread in ios_threads}
        assert "ios/ViewController.swift" in ios_paths
        assert "ios/Bridge.m" in ios_paths

        # PHASE 3: Web
        web_files = ["web/src/Button.tsx", "web/src/Form.tsx"]
        web_threads = filter_locations_for_files(review_threads, web_files)

        # Should STILL find 2 Web threads (review_threads unchanged)
        assert len(web_threads) == 2, (
            f"Web phase should find 2 threads but found {len(web_threads)}. "
            "This suggests review_threads was modified during previous phases."
        )
        web_paths = {thread["path"] for thread in web_threads}
        assert "web/src/Button.tsx" in web_paths
        assert "web/src/Form.tsx" in web_paths

        # Verify original list was never modified
        assert (
            len(review_threads) == original_size
        ), "review_threads should not be modified during filtering"

    def test_filter_does_not_modify_input_set(self):
        """
        Test that filter_locations_for_files does not modify the input
        when it's a set converted to list.
        """
        # Original set of locations
        original_set = {
            ("android/MainActivity.kt", 10, "Issue 1"),
            ("ios/ViewController.swift", 20, "Issue 2"),
            ("web/Button.tsx", 30, "Issue 3"),
        }

        # Store a copy to verify later
        original_copy = set(original_set)

        # Filter multiple times for different phases
        filter_locations_for_files(list(original_set), ["android/MainActivity.kt"])
        filter_locations_for_files(list(original_set), ["ios/ViewController.swift"])
        filter_locations_for_files(list(original_set), ["web/Button.tsx"])

        # Verify original set is unchanged
        assert original_set == original_copy, "Original set should not be modified"

    def test_filter_does_not_modify_input_list(self):
        """
        Test that filter_locations_for_files does not modify the input
        when it's a list.
        """
        # Original list of locations
        original_list = [
            {"path": "android/MainActivity.kt", "line": 10},
            {"path": "ios/ViewController.swift", "line": 20},
            {"path": "web/Button.tsx", "line": 30},
        ]

        # Store a copy to verify later
        original_copy = list(original_list)

        # Filter multiple times for different phases
        filter_locations_for_files(original_list, ["android/MainActivity.kt"])
        filter_locations_for_files(original_list, ["ios/ViewController.swift"])
        filter_locations_for_files(original_list, ["web/Button.tsx"])

        # Verify original list is unchanged
        assert original_list == original_copy, "Original list should not be modified"
        assert len(original_list) == 3, "Original list size should not change"
