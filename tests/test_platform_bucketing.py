"""
Tests for Platform Bucketing

Tests platform detection, file bucketing, and location filtering.
"""

import pytest
from app.platform_bucketing import (
    detect_react_native_in_diff,
    bucket_files_by_platform,
    get_platforms_in_order,
    filter_locations_for_files,
    PLATFORM_ORDER,
)


class TestReactNativeDetection:
    """Tests for React Native content-based detection."""
    
    def test_detect_rn_import_from(self):
        """Test detection of React Native via 'from' import."""
        pr_diff = """
diff --git a/App.tsx b/App.tsx
index 123..456 789
--- a/App.tsx
+++ b/App.tsx
@@ -1,5 +1,5 @@
+import { View, Text } from 'react-native';
+
+export default function App() {
+  return <View><Text>Hello</Text></View>;
+}
"""
        assert detect_react_native_in_diff("App.tsx", pr_diff) is True
    
    def test_detect_rn_require(self):
        """Test detection of React Native via require."""
        pr_diff = """
diff --git a/components/Button.js b/components/Button.js
index 123..456 789
--- a/components/Button.js
+++ b/components/Button.js
@@ -1,3 +1,3 @@
+const { TouchableOpacity } = require('react-native');
"""
        assert detect_react_native_in_diff("components/Button.js", pr_diff) is True
    
    def test_detect_rn_component_tags(self):
        """Test detection via React Native component tags."""
        pr_diff = """
diff --git a/screens/Home.tsx b/screens/Home.tsx
index 123..456 789
--- a/screens/Home.tsx
+++ b/screens/Home.tsx
@@ -1,5 +1,5 @@
+export default function Home() {
+  return (
+    <View>
+      <Text>Welcome</Text>
+      <TouchableOpacity onPress={() => {}}>
+        <Text>Press me</Text>
+      </TouchableOpacity>
+    </View>
+  );
+}
"""
        assert detect_react_native_in_diff("screens/Home.tsx", pr_diff) is True
    
    def test_no_rn_detection_web(self):
        """Test that pure web React files are not detected as RN."""
        pr_diff = """
diff --git a/components/Button.tsx b/components/Button.tsx
index 123..456 789
--- a/components/Button.tsx
+++ b/components/Button.tsx
@@ -1,5 +1,5 @@
+import React from 'react';
+
+export default function Button() {
+  return <button>Click me</button>;
+}
"""
        assert detect_react_native_in_diff("components/Button.tsx", pr_diff) is False
    
    def test_no_rn_detection_empty_diff(self):
        """Test that empty diff returns False."""
        pr_diff = ""
        assert detect_react_native_in_diff("App.tsx", pr_diff) is False


class TestFileBucketing:
    """Tests for file bucketing by platform."""
    
    def test_bucket_android_files(self):
        """Test Android file bucketing."""
        files = [
            "app/src/main/java/MainActivity.java",
            "app/src/main/kotlin/Screen.kt",
        ]
        pr_diff = ""  # No diff needed for extension-based detection
        
        buckets = bucket_files_by_platform(files, pr_diff)
        
        assert len(buckets["Android"]) == 2
        assert "app/src/main/java/MainActivity.java" in buckets["Android"]
        assert "app/src/main/kotlin/Screen.kt" in buckets["Android"]
    
    def test_bucket_ios_files(self):
        """Test iOS file bucketing."""
        files = [
            "ios/App/ViewController.swift",
            "ios/App/Bridge.m",
            "ios/App/Utils.mm",
        ]
        pr_diff = ""
        
        buckets = bucket_files_by_platform(files, pr_diff)
        
        assert len(buckets["iOS"]) == 3
        assert "ios/App/ViewController.swift" in buckets["iOS"]
        assert "ios/App/Bridge.m" in buckets["iOS"]
        assert "ios/App/Utils.mm" in buckets["iOS"]
    
    def test_bucket_flutter_files(self):
        """Test Flutter file bucketing."""
        files = ["lib/main.dart", "lib/screens/home.dart"]
        pr_diff = ""
        
        buckets = bucket_files_by_platform(files, pr_diff)
        
        assert len(buckets["Flutter"]) == 2
        assert "lib/main.dart" in buckets["Flutter"]
    
    def test_bucket_web_unconditional(self):
        """Test unconditional Web files (.css, .html)."""
        files = ["styles/main.css", "public/index.html"]
        pr_diff = ""
        
        buckets = bucket_files_by_platform(files, pr_diff)
        
        assert len(buckets["Web"]) == 2
        assert "styles/main.css" in buckets["Web"]
        assert "public/index.html" in buckets["Web"]
    
    def test_bucket_web_tsx_without_rn(self):
        """Test that .tsx files without RN are bucketed as Web."""
        files = ["components/Button.tsx"]
        pr_diff = """
diff --git a/components/Button.tsx b/components/Button.tsx
index 123..456 789
--- a/components/Button.tsx
+++ b/components/Button.tsx
@@ -1,3 +1,3 @@
+import React from 'react';
+export default function Button() {
+  return <button>Click</button>;
+}
"""
        
        buckets = bucket_files_by_platform(files, pr_diff)
        
        assert len(buckets["Web"]) == 1
        assert "components/Button.tsx" in buckets["Web"]
        assert len(buckets["React Native"]) == 0
    
    def test_bucket_react_native_tsx_with_rn(self):
        """Test that .tsx files with RN are bucketed as React Native."""
        files = ["components/Button.tsx"]
        pr_diff = """
diff --git a/components/Button.tsx b/components/Button.tsx
index 123..456 789
--- a/components/Button.tsx
+++ b/components/Button.tsx
@@ -1,3 +1,5 @@
+import { TouchableOpacity, Text } from 'react-native';
+export default function Button() {
+  return <TouchableOpacity><Text>Click</Text></TouchableOpacity>;
+}
"""
        
        buckets = bucket_files_by_platform(files, pr_diff)
        
        assert len(buckets["React Native"]) == 1
        assert "components/Button.tsx" in buckets["React Native"]
        assert len(buckets["Web"]) == 0
    
    def test_bucket_mixed_platforms(self):
        """Test bucketing files from multiple platforms."""
        files = [
            "MainActivity.java",
            "ViewController.swift",
            "styles.css",
            "App.tsx",
            "main.dart",
        ]
        pr_diff = """
diff --git a/App.tsx b/App.tsx
index 123..456 789
--- a/App.tsx
+++ b/App.tsx
@@ -1,3 +1,3 @@
+import { View } from 'react-native';
"""
        
        buckets = bucket_files_by_platform(files, pr_diff)
        
        assert len(buckets["Android"]) == 1
        assert len(buckets["iOS"]) == 1
        assert len(buckets["Web"]) == 1  # styles.css
        assert len(buckets["React Native"]) == 1  # App.tsx
        assert len(buckets["Flutter"]) == 1


class TestPlatformOrder:
    """Tests for platform ordering."""
    
    def test_platform_order_is_correct(self):
        """Test that PLATFORM_ORDER is in the expected strict order."""
        expected = ["Android", "iOS", "Web", "React Native", "Flutter"]
        assert PLATFORM_ORDER == expected
    
    def test_get_platforms_in_order_all(self):
        """Test getting all platforms in order."""
        buckets = {
            "Android": ["file1.kt"],
            "iOS": ["file2.swift"],
            "Web": ["file3.html"],
            "React Native": ["file4.tsx"],
            "Flutter": ["file5.dart"],
        }
        
        platforms = get_platforms_in_order(buckets)
        
        assert platforms == ["Android", "iOS", "Web", "React Native", "Flutter"]
    
    def test_get_platforms_in_order_subset(self):
        """Test getting subset of platforms in order."""
        buckets = {
            "Android": [],
            "iOS": ["file1.swift"],
            "Web": [],
            "React Native": ["file2.tsx"],
            "Flutter": [],
        }
        
        platforms = get_platforms_in_order(buckets)
        
        assert platforms == ["iOS", "React Native"]
    
    def test_get_platforms_in_order_empty(self):
        """Test getting platforms when no files."""
        buckets = {
            "Android": [],
            "iOS": [],
            "Web": [],
            "React Native": [],
            "Flutter": [],
        }
        
        platforms = get_platforms_in_order(buckets)
        
        assert platforms == []


class TestLocationFiltering:
    """Tests for filtering locations by files."""
    
    def test_filter_tuple_locations(self):
        """Test filtering tuple-based locations."""
        locations = [
            ("file1.swift", 10),
            ("file2.kt", 20),
            ("file3.swift", 30),
        ]
        file_paths = ["file1.swift", "file3.swift"]
        
        filtered = filter_locations_for_files(locations, file_paths)
        
        assert len(filtered) == 2
        assert ("file1.swift", 10) in filtered
        assert ("file3.swift", 30) in filtered
        assert ("file2.kt", 20) not in filtered
    
    def test_filter_dict_locations_file_key(self):
        """Test filtering dict-based locations with 'file' key."""
        locations = [
            {"file": "file1.swift", "line": 10},
            {"file": "file2.kt", "line": 20},
        ]
        file_paths = ["file1.swift"]
        
        filtered = filter_locations_for_files(locations, file_paths)
        
        assert len(filtered) == 1
        assert {"file": "file1.swift", "line": 10} in filtered
    
    def test_filter_dict_locations_path_key(self):
        """Test filtering dict-based locations with 'path' key."""
        locations = [
            {"path": "file1.swift", "line": 10},
            {"path": "file2.kt", "line": 20},
        ]
        file_paths = ["file2.kt"]
        
        filtered = filter_locations_for_files(locations, file_paths)
        
        assert len(filtered) == 1
        assert {"path": "file2.kt", "line": 20} in filtered
    
    def test_filter_empty_locations(self):
        """Test filtering with empty locations list."""
        locations = []
        file_paths = ["file1.swift"]
        
        filtered = filter_locations_for_files(locations, file_paths)
        
        assert filtered == []
    
    def test_filter_three_tuple_locations(self):
        """Test filtering 3-tuple locations (file, line, snippet)."""
        locations = [
            ("file1.swift", 10, "Button missing label"),
            ("file2.kt", 20, "Image missing description"),
            ("file3.swift", 30, "Text too small"),
        ]
        file_paths = ["file1.swift", "file3.swift"]
        
        filtered = filter_locations_for_files(locations, file_paths)
        
        assert len(filtered) == 2
        assert ("file1.swift", 10, "Button missing label") in filtered
        assert ("file3.swift", 30, "Text too small") in filtered
