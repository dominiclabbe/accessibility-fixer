"""
Tests for DiffParser

Validates diff parsing, line mapping, and validation logic.
"""

import pytest
from app.diff_parser import (
    DiffParser,
    validate_issues_in_batch,
    is_no_issues_placeholder,
)

# Test fixtures - sample diffs
SAMPLE_SINGLE_FILE_DIFF = """diff --git a/app/test.py b/app/test.py
index 1234567..abcdefg 100644
--- a/app/test.py
+++ b/app/test.py
@@ -1,5 +1,7 @@
 def hello():
+    # New comment
     print("Hello")
+    print("World")
     return True
 
 def goodbye():
"""

SAMPLE_MULTI_FILE_DIFF = """diff --git a/app/file1.py b/app/file1.py
index 1111111..2222222 100644
--- a/app/file1.py
+++ b/app/file1.py
@@ -10,4 +10,5 @@ def func1():
     pass
+    # Added line in file1

diff --git a/app/file2.js b/app/file2.js
index 3333333..4444444 100644
--- a/app/file2.js
+++ b/app/file2.js
@@ -5,3 +5,4 @@ function func2() {
   console.log("test");
+  console.log("new line");
 }
"""

SAMPLE_ANDROID_LAYOUT_DIFF = """diff --git a/app/src/main/res/layout/activity_main.xml b/app/src/main/res/layout/activity_main.xml
index aaaaaaa..bbbbbbb 100644
--- a/app/src/main/res/layout/activity_main.xml
+++ b/app/src/main/res/layout/activity_main.xml
@@ -15,6 +15,7 @@
         android:layout_width="wrap_content"
         android:layout_height="wrap_content"
+        android:contentDescription="@null"
         android:src="@drawable/icon" />
 
     <Button
"""


class TestDiffParser:
    """Tests for DiffParser class."""

    def test_parse_diff_single_file(self):
        """Test parsing diff with single file."""
        parser = DiffParser()
        result = parser.parse_diff(SAMPLE_SINGLE_FILE_DIFF)

        assert "app/test.py" in result
        assert "def hello():" in result["app/test.py"]
        assert "+    # New comment" in result["app/test.py"]

    def test_parse_diff_multiple_files(self):
        """Test parsing diff with multiple files."""
        parser = DiffParser()
        result = parser.parse_diff(SAMPLE_MULTI_FILE_DIFF)

        assert "app/file1.py" in result
        assert "app/file2.js" in result
        assert "file1" in result["app/file1.py"]
        assert "file2" in result["app/file2.js"]

    def test_filter_diff_for_single_file(self):
        """Test filtering diff to single file."""
        parser = DiffParser()
        filtered = parser.filter_diff_for_files(
            SAMPLE_MULTI_FILE_DIFF, ["app/file1.py"]
        )

        assert "file1.py" in filtered
        assert "file2.js" not in filtered

    def test_filter_diff_for_multiple_files(self):
        """Test filtering diff to multiple files."""
        parser = DiffParser()
        filtered = parser.filter_diff_for_files(
            SAMPLE_MULTI_FILE_DIFF, ["app/file1.py", "app/file2.js"]
        )

        assert "file1.py" in filtered
        assert "file2.js" in filtered

    def test_filter_diff_empty_file_list(self):
        """Test filtering with empty file list returns empty string."""
        parser = DiffParser()
        filtered = parser.filter_diff_for_files(SAMPLE_MULTI_FILE_DIFF, [])

        assert filtered == ""

    def test_extract_commentable_lines_single_file(self):
        """Test extracting commentable lines from single file diff."""
        parser = DiffParser()
        commentable = parser.extract_commentable_lines(SAMPLE_SINGLE_FILE_DIFF)

        assert "app/test.py" in commentable
        lines = commentable["app/test.py"]

        # Check that added lines are commentable
        # Line 1: def hello() (context)
        # Line 2: # New comment (added)
        # Line 3: print("Hello") (context)
        # Line 4: print("World") (added)
        # Line 5: return True (context)
        assert 1 in lines  # context line
        assert 2 in lines  # added line
        assert 3 in lines  # context line
        assert 4 in lines  # added line
        assert 5 in lines  # context line

    def test_extract_commentable_lines_android_layout(self):
        """Test extracting commentable lines from Android layout XML."""
        parser = DiffParser()
        commentable = parser.extract_commentable_lines(SAMPLE_ANDROID_LAYOUT_DIFF)

        file_path = "app/src/main/res/layout/activity_main.xml"
        assert file_path in commentable

        lines = commentable[file_path]
        # The added line should be commentable
        assert 18 in lines  # android:contentDescription line (added)

    def test_extract_changed_line_ranges(self):
        """Test extracting changed line ranges."""
        parser = DiffParser()
        ranges = parser.extract_changed_line_ranges(SAMPLE_SINGLE_FILE_DIFF)

        assert "app/test.py" in ranges
        assert len(ranges["app/test.py"]) > 0

        # Should have at least one range
        start, end = ranges["app/test.py"][0]
        assert start == 1
        assert end >= start

    def test_find_nearest_commentable_line_exact_match(self):
        """Test finding nearest line when target is commentable."""
        parser = DiffParser()
        commentable_lines = [1, 2, 5, 10, 15]

        # Target line is in the list
        result = parser.find_nearest_commentable_line(5, commentable_lines)
        assert result == 5

    def test_find_nearest_commentable_line_nearby(self):
        """Test finding nearest line when target is not commentable."""
        parser = DiffParser()
        commentable_lines = [1, 2, 5, 10, 15]

        # Target line 6 should find 5 (distance 1)
        result = parser.find_nearest_commentable_line(6, commentable_lines)
        assert result == 5

        # Target line 12 should find 10 (distance 2)
        result = parser.find_nearest_commentable_line(12, commentable_lines)
        assert result == 10

    def test_find_nearest_commentable_line_max_distance(self):
        """Test that max_distance is respected."""
        parser = DiffParser()
        commentable_lines = [1, 2, 5]

        # Target line 20 is too far (>10 from nearest)
        result = parser.find_nearest_commentable_line(
            20, commentable_lines, max_distance=10
        )
        assert result is None

        # But with higher max_distance, should find something
        result = parser.find_nearest_commentable_line(
            20, commentable_lines, max_distance=20
        )
        assert result == 5

    def test_find_nearest_commentable_line_empty_list(self):
        """Test finding nearest line with empty list."""
        parser = DiffParser()
        result = parser.find_nearest_commentable_line(5, [])
        assert result is None


class TestValidateIssuesInBatch:
    """Tests for validate_issues_in_batch function."""

    def test_validate_issues_all_valid(self):
        """Test validation when all issues are valid."""
        issues = [
            {"file": "app/test.py", "line": 1, "title": "Issue 1"},
            {"file": "app/test.py", "line": 2, "title": "Issue 2"},
        ]
        batch_files = ["app/test.py"]
        commentable = {"app/test.py": [1, 2, 3, 4]}

        result = validate_issues_in_batch(issues, batch_files, commentable)

        assert len(result) == 2
        assert result[0]["line"] == 1
        assert result[1]["line"] == 2

    def test_validate_issues_file_not_in_batch(self):
        """Test that issues for files not in batch are dropped."""
        issues = [
            {"file": "app/test.py", "line": 1, "title": "Issue 1"},
            {"file": "app/other.py", "line": 5, "title": "Issue 2"},  # Not in batch
        ]
        batch_files = ["app/test.py"]
        commentable = {"app/test.py": [1, 2, 3], "app/other.py": [5, 6]}

        result = validate_issues_in_batch(issues, batch_files, commentable)

        assert len(result) == 1
        assert result[0]["file"] == "app/test.py"

    def test_validate_issues_invalid_line_number(self):
        """Test that issues with invalid line numbers are dropped."""
        issues = [
            {"file": "app/test.py", "line": 0, "title": "Issue 1"},  # Invalid
            {"file": "app/test.py", "line": -1, "title": "Issue 2"},  # Invalid
            {"file": "app/test.py", "line": 5, "title": "Issue 3"},  # Valid
        ]
        batch_files = ["app/test.py"]
        commentable = {"app/test.py": [5, 6, 7]}

        result = validate_issues_in_batch(issues, batch_files, commentable)

        assert len(result) == 1
        assert result[0]["line"] == 5

    def test_validate_issues_adjust_to_commentable(self):
        """Test that non-commentable lines are adjusted to nearest commentable."""
        issues = [
            {"file": "app/test.py", "line": 4, "title": "Issue 1"},  # Not commentable
        ]
        batch_files = ["app/test.py"]
        commentable = {"app/test.py": [1, 2, 5, 10]}  # Line 4 not in list

        result = validate_issues_in_batch(issues, batch_files, commentable)

        assert len(result) == 1
        # Line 4 should be adjusted to nearest (5)
        assert result[0]["line"] == 5

    def test_validate_issues_no_nearby_commentable(self):
        """Test that issues with no nearby commentable lines are dropped."""
        issues = [
            {"file": "app/test.py", "line": 100, "title": "Issue 1"},  # Too far
        ]
        batch_files = ["app/test.py"]
        commentable = {"app/test.py": [1, 2, 3]}  # All far from line 100

        result = validate_issues_in_batch(issues, batch_files, commentable)

        # Should be dropped (no line within max_distance=10)
        assert len(result) == 0


class TestIsNoIssuesPlaceholder:
    """Tests for is_no_issues_placeholder function."""

    def test_explicit_na_wcag(self):
        """Test detection of N/A WCAG SC."""
        issue = {"wcag_sc": "N/A", "title": "Some title"}
        assert is_no_issues_placeholder(issue) is True

        issue = {"wcag_sc": "none", "title": "Some title"}
        assert is_no_issues_placeholder(issue) is True

        issue = {"wcag_sc": "", "title": "Some title"}
        assert is_no_issues_placeholder(issue) is True

    def test_no_issues_in_title(self):
        """Test detection of 'no issues' phrases in title."""
        issue = {"wcag_sc": "1.1.1", "title": "No accessibility issues found"}
        assert is_no_issues_placeholder(issue) is True

        issue = {"wcag_sc": "1.1.1", "title": "No issues detected"}
        assert is_no_issues_placeholder(issue) is True

        issue = {"wcag_sc": "1.1.1", "title": "Looks good - no problems"}
        assert is_no_issues_placeholder(issue) is True

    def test_no_issues_in_description(self):
        """Test detection of 'no issues' phrases in description."""
        issue = {
            "wcag_sc": "1.1.1",
            "title": "Review complete",
            "description": "No accessibility issues found in this file",
        }
        assert is_no_issues_placeholder(issue) is True

    def test_valid_issue_not_placeholder(self):
        """Test that valid issues are not marked as placeholders."""
        issue = {
            "wcag_sc": "1.1.1",
            "title": "Missing alt text",
            "description": "Image lacks alternative text",
        }
        assert is_no_issues_placeholder(issue) is False

        issue = {"wcag_sc": "2.4.6", "title": "Heading structure issue"}
        assert is_no_issues_placeholder(issue) is False


class TestDebugWebReviewLogging:
    """Tests for DEBUG_WEB_REVIEW logging functionality."""

    def test_validate_issues_with_debug_web_review_env(self, monkeypatch, capsys):
        """Test that DEBUG_WEB_REVIEW logs drop reasons for web files."""
        # Enable DEBUG_WEB_REVIEW
        monkeypatch.setenv("DEBUG_WEB_REVIEW", "1")

        # Sample diff for web file
        diff = """diff --git a/web/components/Button.tsx b/web/components/Button.tsx
index 1234567..abcdefg 100644
--- a/web/components/Button.tsx
+++ b/web/components/Button.tsx
@@ -1,3 +1,5 @@
+import React from 'react';
+
 function Button() {
   return <button>Click</button>;
 }
"""

        batch_files = ["web/components/Button.tsx"]
        commentable = {"web/components/Button.tsx": [1, 2, 3, 4, 5]}

        # Issue for a file not in batch (web file)
        issues = [
            {
                "file": "web/components/NotInBatch.tsx",
                "line": 10,
                "title": "Missing aria-label",
                "wcag_sc": "4.1.2",
            }
        ]

        validated = validate_issues_in_batch(issues, batch_files, commentable, diff)

        # Should drop the issue
        assert len(validated) == 0

        # Check that logs were captured (via print, not logger in tests)
        captured = capsys.readouterr()
        assert "Dropping issue" in captured.out
        assert "web/components/NotInBatch.tsx" in captured.out

    def test_validate_issues_without_debug_web_review(self, monkeypatch, capsys):
        """Test that without DEBUG_WEB_REVIEW, detailed logs are not shown."""
        # Ensure DEBUG_WEB_REVIEW is off
        monkeypatch.setenv("DEBUG_WEB_REVIEW", "0")

        diff = """diff --git a/web/test.tsx b/web/test.tsx
index 1234567..abcdefg 100644
--- a/web/test.tsx
+++ b/web/test.tsx
@@ -1,3 +1,4 @@
+// New line
 export default Test;
"""

        batch_files = ["web/test.tsx"]
        commentable = {"web/test.tsx": [1, 2]}

        # Issue for non-existent file
        issues = [
            {"file": "web/other.tsx", "line": 10, "title": "Test", "wcag_sc": "1.1.1"}
        ]

        validated = validate_issues_in_batch(issues, batch_files, commentable, diff)

        # Should drop the issue
        assert len(validated) == 0

        # Basic warning should still appear
        captured = capsys.readouterr()
        assert "Dropping issue" in captured.out

    def test_web_file_detection(self):
        """Test that _is_web_file correctly identifies web files."""
        from app.diff_parser import _is_web_file

        # Test web directory
        assert _is_web_file("web/components/Button.tsx") is True
        assert _is_web_file("web/styles/main.css") is True

        # Test web extensions
        assert _is_web_file("src/components/Button.tsx") is True
        assert _is_web_file("src/components/Button.jsx") is True
        assert _is_web_file("app/script.js") is True
        assert _is_web_file("styles/main.css") is True
        assert _is_web_file("index.html") is True

        # Test non-web files
        assert _is_web_file("app/main.py") is False
        assert _is_web_file("src/Main.swift") is False
        assert _is_web_file("app/MainActivity.kt") is False

    def test_drop_reason_codes(self, monkeypatch, capsys):
        """Test that drop reason codes are correctly generated."""
        monkeypatch.setenv("DEBUG_WEB_REVIEW", "1")

        diff = """diff --git a/web/test.tsx b/web/test.tsx
index 1234567..abcdefg 100644
--- a/web/test.tsx
+++ b/web/test.tsx
@@ -10,3 +10,4 @@ function Test() {
   return <div>Test</div>;
+  // New line
 }
"""

        batch_files = ["web/test.tsx"]
        commentable = {"web/test.tsx": [10, 11, 12, 13]}

        # Test various drop reasons
        issues = [
            # Invalid line number
            {
                "file": "web/test.tsx",
                "line": 0,
                "title": "Invalid line",
                "wcag_sc": "1.1.1",
            },
            # File not in batch
            {
                "file": "web/other.tsx",
                "line": 5,
                "title": "Not in batch",
                "wcag_sc": "1.1.1",
            },
        ]

        validated = validate_issues_in_batch(issues, batch_files, commentable, diff)

        # Both should be dropped
        assert len(validated) == 0

        # Check output contains reason codes
        captured = capsys.readouterr()
        assert "invalid_line_number" in captured.out
        assert "file_not_in_batch" in captured.out


class TestPathNormalization:
    """Tests for path normalization in filter_diff_for_files."""

    def test_crlf_normalization_in_parse_diff(self):
        """Test that CRLF line endings are normalized properly."""
        # Diff with CRLF line endings
        diff_with_crlf = (
            "diff --git a/test.py b/test.py\r\n"
            "index 1234567..abcdefg 100644\r\n"
            "--- a/test.py\r\n"
            "+++ b/test.py\r\n"
            "@@ -1,2 +1,3 @@\r\n"
            " def hello():\r\n"
            "+    print('world')\r\n"
            "     pass\r\n"
        )
        parser = DiffParser()
        result = parser.parse_diff(diff_with_crlf)

        # Should successfully parse file
        assert "test.py" in result
        assert "def hello():" in result["test.py"]
        # Should not have \r in the result
        assert "\r" not in result["test.py"]

    def test_corrupted_path_with_space_and_extra_path(self):
        """Test that we extract only the destination path from rename/move diffs.

        When a file is renamed (e.g., src/Main.tsx -> web/src/Main.tsx), the diff
        header is 'diff --git a/src/Main.tsx b/web/src/Main.tsx'. Without proper
        parsing, we could incorrectly capture both paths as one (corruption).
        This test ensures we extract only 'web/src/Main.tsx' (the destination).
        """
        # This simulates a file rename in Git
        diff = (
            "diff --git a/src/components/Main.tsx b/web/src/components/Main.tsx\n"
            "index 1234567..abcdefg 100644\n"
            "--- a/src/components/Main.tsx\n"
            "+++ b/web/src/components/Main.tsx\n"
            "@@ -1,3 +1,5 @@\n"
            "+import React from 'react';\n"
            "+\n"
            " export function Main() {\n"
            "   return <div>Main</div>;\n"
            " }\n"
        )
        parser = DiffParser()
        result = parser.parse_diff(diff)

        # Should extract only the destination path (after "b/")
        assert "web/src/components/Main.tsx" in result
        # Should NOT have corrupted path that includes both src and dest
        assert "src/components/Main.tsx b/web/src/components/Main.tsx" not in result

    def test_path_with_trailing_whitespace(self):
        """Test that trailing whitespace in paths is handled."""
        diff = (
            "diff --git a/test.py b/test.py   \n"
            "index 1234567..abcdefg 100644\n"
            "--- a/test.py\n"
            "+++ b/test.py   \n"
            "@@ -1,2 +1,3 @@\n"
            " line1\n"
            "+line2\n"
        )
        parser = DiffParser()

        # Test parse_diff
        result = parser.parse_diff(diff)
        assert "test.py" in result

        # Test extract_commentable_lines
        commentable = parser.extract_commentable_lines(diff)
        assert "test.py" in commentable
        assert len(commentable["test.py"]) > 0

    def test_mixed_line_endings(self):
        """Test handling of mixed line endings (LF and CRLF)."""
        diff = (
            "diff --git a/test.py b/test.py\r\n"
            "index 1234567..abcdefg 100644\n"  # LF here
            "--- a/test.py\r\n"
            "+++ b/test.py\n"  # LF here
            "@@ -1,2 +1,3 @@\r\n"
            " line1\n"
            "+line2\r\n"
            " line3\n"
        )
        parser = DiffParser()

        # Should normalize and parse correctly
        result = parser.parse_diff(diff)
        assert "test.py" in result

        commentable = parser.extract_commentable_lines(diff)
        assert "test.py" in commentable
        assert 2 in commentable["test.py"]  # The added line

    def test_extract_commentable_lines_with_path_corruption(self):
        """Test extract_commentable_lines with potential path corruption."""
        diff = (
            "diff --git a/test.tsx b/test.tsx\n"
            "index 1234567..abcdefg 100644\n"
            "--- a/test.tsx\n"
            "+++ b/test.tsx   extra-garbage\n"  # Trailing garbage
            "@@ -1,2 +1,3 @@\n"
            " function test() {\n"
            "+  console.log('hi');\n"
            " }\n"
        )
        parser = DiffParser()
        commentable = parser.extract_commentable_lines(diff)

        # Should extract clean path
        assert "test.tsx" in commentable
        assert "test.tsx   extra-garbage" not in commentable

    def test_suffix_match_when_diff_has_shorter_path(self):
        """Test suffix matching when diff has '+++ b/src/components/Main.tsx'
        but requested file is 'web/src/components/Main.tsx'."""
        diff = """diff --git a/src/components/Main.tsx b/src/components/Main.tsx
index 1234567..abcdefg 100644
--- a/src/components/Main.tsx
+++ b/src/components/Main.tsx
@@ -1,3 +1,5 @@
+import React from 'react';
+
 export function Main() {
   return <div>Main</div>;
 }
"""
        parser = DiffParser()

        # Request with different leading path component
        filtered = parser.filter_diff_for_files(diff, ["web/src/components/Main.tsx"])

        # Should match because 'src/components/Main.tsx' is suffix of 'web/src/components/Main.tsx'
        assert "Main.tsx" in filtered
        assert "import React" in filtered

    def test_suffix_match_when_requested_has_shorter_path(self):
        """Test suffix matching when diff has '+++ b/web/src/components/Main.tsx'
        but requested file is 'src/components/Main.tsx'."""
        diff = """diff --git a/web/src/components/Main.tsx b/web/src/components/Main.tsx
index 1234567..abcdefg 100644
--- a/web/src/components/Main.tsx
+++ b/web/src/components/Main.tsx
@@ -1,3 +1,5 @@
+import React from 'react';
+
 export function Main() {
   return <div>Main</div>;
 }
"""
        parser = DiffParser()

        # Request with shorter path
        filtered = parser.filter_diff_for_files(diff, ["src/components/Main.tsx"])

        # Should match because 'src/components/Main.tsx' is suffix of 'web/src/components/Main.tsx'
        assert "Main.tsx" in filtered
        assert "import React" in filtered

    def test_basename_match_when_unique(self):
        """Test basename matching when only one file has that basename."""
        diff = """diff --git a/web/components/Button.tsx b/web/components/Button.tsx
index 1234567..abcdefg 100644
--- a/web/components/Button.tsx
+++ b/web/components/Button.tsx
@@ -1,3 +1,4 @@
+import React from 'react';
 export function Button() {}
"""
        parser = DiffParser()

        # Request with just basename (should match if unique)
        filtered = parser.filter_diff_for_files(diff, ["Button.tsx"])

        # Should match because only one Button.tsx exists
        assert "Button.tsx" in filtered
        assert "import React" in filtered

    def test_ambiguous_basename_no_match(self):
        """Test that basename matching doesn't match when multiple files
        have the same basename."""
        diff = """diff --git a/web/components/Main.tsx b/web/components/Main.tsx
index 1111111..2222222 100644
--- a/web/components/Main.tsx
+++ b/web/components/Main.tsx
@@ -1,3 +1,4 @@
+import React from 'react';
 export function Main1() {}

diff --git a/app/views/Main.tsx b/app/views/Main.tsx
index 3333333..4444444 100644
--- a/app/views/Main.tsx
+++ b/app/views/Main.tsx
@@ -1,3 +1,4 @@
+import { Component } from 'react';
 export function Main2() {}
"""
        parser = DiffParser()

        # Request with just basename when multiple exist - should not match
        filtered = parser.filter_diff_for_files(diff, ["Main.tsx"])

        # Should be empty because basename is ambiguous
        assert filtered == ""

    def test_exact_match_preferred_over_suffix(self):
        """Test that exact match is always preferred."""
        diff = """diff --git a/src/components/Main.tsx b/src/components/Main.tsx
index 1111111..2222222 100644
--- a/src/components/Main.tsx
+++ b/src/components/Main.tsx
@@ -1,3 +1,4 @@
+// Exact match
 export function Main1() {}

diff --git a/web/src/components/Main.tsx b/web/src/components/Main.tsx
index 3333333..4444444 100644
--- a/web/src/components/Main.tsx
+++ b/web/src/components/Main.tsx
@@ -1,3 +1,4 @@
+// Suffix match
 export function Main2() {}
"""
        parser = DiffParser()

        # Request exact match
        filtered = parser.filter_diff_for_files(diff, ["src/components/Main.tsx"])

        # Should get exact match, not the suffix match
        assert "// Exact match" in filtered
        assert "// Suffix match" not in filtered

    def test_multiple_suffix_matches_no_match(self):
        """Test that ambiguous suffix matches are not used."""
        diff = """diff --git a/web/src/Main.tsx b/web/src/Main.tsx
index 1111111..2222222 100644
--- a/web/src/Main.tsx
+++ b/web/src/Main.tsx
@@ -1,3 +1,4 @@
+// First
 export function Main1() {}

diff --git a/app/src/Main.tsx b/app/src/Main.tsx
index 3333333..4444444 100644
--- a/app/src/Main.tsx
+++ b/app/src/Main.tsx
@@ -1,3 +1,4 @@
+// Second
 export function Main2() {}
"""
        parser = DiffParser()

        # Request with path that could match either via suffix
        filtered = parser.filter_diff_for_files(diff, ["src/Main.tsx"])

        # Should be empty because multiple paths end with 'src/Main.tsx'
        assert filtered == ""


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
