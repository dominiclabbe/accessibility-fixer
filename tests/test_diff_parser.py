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
        filtered = parser.filter_diff_for_files(SAMPLE_MULTI_FILE_DIFF, ["app/file1.py"])

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
        result = parser.find_nearest_commentable_line(20, commentable_lines, max_distance=10)
        assert result is None

        # But with higher max_distance, should find something
        result = parser.find_nearest_commentable_line(20, commentable_lines, max_distance=20)
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


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
