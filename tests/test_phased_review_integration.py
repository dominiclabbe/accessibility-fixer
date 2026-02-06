"""
Integration tests for platform-phased reviews

Tests the end-to-end phased review flow with multiple platforms.
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
from app.platform_bucketing import bucket_files_by_platform, get_platforms_in_order


class TestPhasedReviewIntegration:
    """Integration tests for phased review workflow."""
    
    def test_phased_review_flow_multiple_platforms(self):
        """
        Test that files from multiple platforms are bucketed correctly
        and would be reviewed in the correct order.
        """
        # Simulate a PR with files from all platforms
        changed_files = [
            "android/MainActivity.kt",
            "android/Fragment.java",
            "ios/ViewController.swift",
            "ios/Bridge.m",
            "web/styles.css",
            "web/index.html",
            "mobile/App.tsx",  # React Native
            "flutter/lib/main.dart",
        ]
        
        # Create a diff with React Native import for mobile/App.tsx
        pr_diff = """
diff --git a/android/MainActivity.kt b/android/MainActivity.kt
index 123..456
--- a/android/MainActivity.kt
+++ b/android/MainActivity.kt
@@ -1,3 +1,3 @@
+class MainActivity {}

diff --git a/android/Fragment.java b/android/Fragment.java
index 123..456
--- a/android/Fragment.java
+++ b/android/Fragment.java
@@ -1,3 +1,3 @@
+class Fragment {}

diff --git a/ios/ViewController.swift b/ios/ViewController.swift
index 123..456
--- a/ios/ViewController.swift
+++ b/ios/ViewController.swift
@@ -1,3 +1,3 @@
+class ViewController {}

diff --git a/ios/Bridge.m b/ios/Bridge.m
index 123..456
--- a/ios/Bridge.m
+++ b/ios/Bridge.m
@@ -1,3 +1,3 @@
+@implementation Bridge

diff --git a/web/styles.css b/web/styles.css
index 123..456
--- a/web/styles.css
+++ b/web/styles.css
@@ -1,3 +1,3 @@
+.button {}

diff --git a/web/index.html b/web/index.html
index 123..456
--- a/web/index.html
+++ b/web/index.html
@@ -1,3 +1,3 @@
+<html></html>

diff --git a/mobile/App.tsx b/mobile/App.tsx
index 123..456
--- a/mobile/App.tsx
+++ b/mobile/App.tsx
@@ -1,3 +1,5 @@
+import { View, Text } from 'react-native';
+export default function App() { return <View><Text>Hi</Text></View>; }

diff --git a/flutter/lib/main.dart b/flutter/lib/main.dart
index 123..456
--- a/flutter/lib/main.dart
+++ b/flutter/lib/main.dart
@@ -1,3 +1,3 @@
+void main() {}
"""
        
        # Bucket files
        buckets = bucket_files_by_platform(changed_files, pr_diff)
        platforms = get_platforms_in_order(buckets)
        
        # Verify correct order
        assert platforms == ["Android", "iOS", "Web", "React Native", "Flutter"]
        
        # Verify correct bucketing
        assert len(buckets["Android"]) == 2
        assert "android/MainActivity.kt" in buckets["Android"]
        assert "android/Fragment.java" in buckets["Android"]
        
        assert len(buckets["iOS"]) == 2
        assert "ios/ViewController.swift" in buckets["iOS"]
        assert "ios/Bridge.m" in buckets["iOS"]
        
        assert len(buckets["Web"]) == 2
        assert "web/styles.css" in buckets["Web"]
        assert "web/index.html" in buckets["Web"]
        
        assert len(buckets["React Native"]) == 1
        assert "mobile/App.tsx" in buckets["React Native"]
        
        assert len(buckets["Flutter"]) == 1
        assert "flutter/lib/main.dart" in buckets["Flutter"]
    
    def test_phased_review_single_platform(self):
        """Test that single platform PRs still work correctly."""
        changed_files = [
            "MainActivity.kt",
            "Fragment.java",
        ]
        
        pr_diff = """
diff --git a/MainActivity.kt b/MainActivity.kt
index 123..456
--- a/MainActivity.kt
+++ b/MainActivity.kt
@@ -1,3 +1,3 @@
+class MainActivity {}
"""
        
        buckets = bucket_files_by_platform(changed_files, pr_diff)
        platforms = get_platforms_in_order(buckets)
        
        # Should only have Android
        assert platforms == ["Android"]
        assert len(buckets["Android"]) == 2
    
    def test_phased_review_web_vs_react_native_detection(self):
        """Test that Web and React Native files are correctly distinguished."""
        changed_files = [
            "web/Button.tsx",  # Web
            "mobile/Button.tsx",  # React Native
        ]
        
        pr_diff = """
diff --git a/web/Button.tsx b/web/Button.tsx
index 123..456
--- a/web/Button.tsx
+++ b/web/Button.tsx
@@ -1,3 +1,3 @@
+import React from 'react';
+export default function Button() { return <button>Click</button>; }

diff --git a/mobile/Button.tsx b/mobile/Button.tsx
index 123..456
--- a/mobile/Button.tsx
+++ b/mobile/Button.tsx
@@ -1,3 +1,3 @@
+import { TouchableOpacity } from 'react-native';
+export default function Button() { return <TouchableOpacity />; }
"""
        
        buckets = bucket_files_by_platform(changed_files, pr_diff)
        platforms = get_platforms_in_order(buckets)
        
        # Should have both Web and React Native
        assert "Web" in platforms
        assert "React Native" in platforms
        
        # Verify correct detection
        assert "web/Button.tsx" in buckets["Web"]
        assert "mobile/Button.tsx" in buckets["React Native"]
    
    def test_phased_review_order_is_strict(self):
        """Test that platforms are always reviewed in strict order."""
        # Create PR with only Flutter and Android (skip iOS, Web, RN)
        changed_files = [
            "lib/main.dart",
            "MainActivity.kt",
        ]
        
        pr_diff = """
diff --git a/lib/main.dart b/lib/main.dart
index 123..456
--- a/lib/main.dart
+++ b/lib/main.dart
@@ -1,3 +1,3 @@
+void main() {}

diff --git a/MainActivity.kt b/MainActivity.kt
index 123..456
--- a/MainActivity.kt
+++ b/MainActivity.kt
@@ -1,3 +1,3 @@
+class MainActivity {}
"""
        
        buckets = bucket_files_by_platform(changed_files, pr_diff)
        platforms = get_platforms_in_order(buckets)
        
        # Android should come before Flutter
        assert platforms == ["Android", "Flutter"]
    
    def test_empty_pr_no_reviewable_files(self):
        """Test handling of PR with no reviewable files."""
        changed_files = ["README.md", "config.json"]
        pr_diff = ""
        
        buckets = bucket_files_by_platform(changed_files, pr_diff)
        platforms = get_platforms_in_order(buckets)
        
        # Should have no platforms
        assert platforms == []


class TestPhasedReviewGuideLoading:
    """Test guide loading per phase."""
    
    def test_single_platform_guides_loaded_per_phase(self):
        """Test that each phase loads guides for only that platform."""
        from app.guide_loader import GuideLoader
        
        loader = GuideLoader()
        
        # Simulate loading guides for each platform individually
        android_guides = loader.load_platform_specific_guides(["Android"])
        ios_guides = loader.load_platform_specific_guides(["iOS"])
        web_guides = loader.load_platform_specific_guides(["Web"])
        rn_guides = loader.load_platform_specific_guides(["React Native"])
        flutter_guides = loader.load_platform_specific_guides(["Flutter"])
        
        # All should return some guides (actual content varies by repo setup)
        # Just verify they can be called without errors
        assert isinstance(android_guides, str)
        assert isinstance(ios_guides, str)
        assert isinstance(web_guides, str)
        assert isinstance(rn_guides, str)
        assert isinstance(flutter_guides, str)


class TestLocationFilteringForPhases:
    """Test filtering of existing_comments and review_threads per phase."""
    
    def test_filter_existing_comments_per_phase(self):
        """Test that existing comments are filtered per phase."""
        from app.platform_bucketing import filter_locations_for_files
        
        # All existing comments across all files
        existing_comments = [
            ("MainActivity.kt", 10),
            ("ViewController.swift", 20),
            ("Button.tsx", 30),
            ("main.dart", 40),
        ]
        
        # Phase 1: Android files only
        android_files = ["MainActivity.kt"]
        filtered = filter_locations_for_files(existing_comments, android_files)
        assert len(filtered) == 1
        assert ("MainActivity.kt", 10) in filtered
        
        # Phase 2: iOS files only
        ios_files = ["ViewController.swift"]
        filtered = filter_locations_for_files(existing_comments, ios_files)
        assert len(filtered) == 1
        assert ("ViewController.swift", 20) in filtered
    
    def test_filter_review_threads_per_phase(self):
        """Test that review threads are filtered per phase."""
        from app.platform_bucketing import filter_locations_for_files
        
        # All review threads across all files
        review_threads = [
            {"file": "MainActivity.kt", "line": 10, "body": "Missing description"},
            {"file": "ViewController.swift", "line": 20, "body": "Missing label"},
            {"file": "Button.tsx", "line": 30, "body": "Missing alt text"},
        ]
        
        # Phase 1: Android files only
        android_files = ["MainActivity.kt"]
        filtered = filter_locations_for_files(review_threads, android_files)
        assert len(filtered) == 1
        assert filtered[0]["file"] == "MainActivity.kt"
        
        # Phase 2: iOS files only
        ios_files = ["ViewController.swift"]
        filtered = filter_locations_for_files(review_threads, ios_files)
        assert len(filtered) == 1
        assert filtered[0]["file"] == "ViewController.swift"
