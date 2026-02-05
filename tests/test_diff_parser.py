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

# Kotlin Compose diff with Slider for anchor testing
SAMPLE_COMPOSE_SLIDER_DIFF = """diff --git a/shared/src/commonMain/kotlin/App.kt b/shared/src/commonMain/kotlin/App.kt
index 1111111..2222222 100644
--- a/shared/src/commonMain/kotlin/App.kt
+++ b/shared/src/commonMain/kotlin/App.kt
@@ -375,20 +375,30 @@ fun SettingsTab() {
     Column(
         modifier = Modifier.fillMaxSize().padding(16.dp)
     ) {
+        Text("Volume Settings")
+        
+        // Volume slider - missing accessibility label
+        Slider(
+            value = 0.5f,
+            onValueChange = { },
+            modifier = Modifier.fillMaxWidth()
+        )
+        
         Text("Notification Settings")
         
-        Switch(
-            checked = true,
-            onCheckedChange = { }
+        Box(
+            modifier = Modifier
+                .clickable { /* handle click */ }
+                .padding(8.dp)
+        ) {
+            Text("Clickable item")
+        }
+        
+        TextField(
+            value = "test",
+            onValueChange = { }
         )
     }
 }
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


class TestExtractLineTexts:
    """Tests for extract_line_texts function."""

    def test_extract_line_texts_single_file(self):
        """Test extracting line texts from single file diff."""
        parser = DiffParser()
        line_texts = parser.extract_line_texts(SAMPLE_SINGLE_FILE_DIFF)

        assert "app/test.py" in line_texts
        texts = line_texts["app/test.py"]

        # Check that we have line texts for added and context lines
        assert 1 in texts  # def hello():
        assert 2 in texts  # # New comment
        assert 3 in texts  # print("Hello")
        assert 4 in texts  # print("World")
        assert "def hello():" in texts[1]
        assert "# New comment" in texts[2]

    def test_extract_line_texts_compose_diff(self):
        """Test extracting line texts from Compose diff."""
        parser = DiffParser()
        line_texts = parser.extract_line_texts(SAMPLE_COMPOSE_SLIDER_DIFF)

        file_path = "shared/src/commonMain/kotlin/App.kt"
        assert file_path in line_texts
        texts = line_texts[file_path]

        # Find the Slider( line
        slider_lines = [ln for ln, text in texts.items() if "Slider(" in text]
        assert len(slider_lines) > 0, "Should find Slider( in diff"

        # Find clickable line
        clickable_lines = [ln for ln, text in texts.items() if ".clickable" in text]
        assert len(clickable_lines) > 0, "Should find .clickable in diff"


class TestInferAnchorText:
    """Tests for infer_anchor_text function."""

    def test_infer_slider_from_title(self):
        """Test inferring Slider anchor from title."""
        issue = {"title": "Slider missing accessibility label"}
        result = DiffParser.infer_anchor_text(issue)
        assert result == "Slider("

    def test_infer_switch_from_title(self):
        """Test inferring Switch anchor from title."""
        issue = {"title": "Switch needs content description"}
        result = DiffParser.infer_anchor_text(issue)
        assert result == "Switch("

    def test_infer_textfield_from_title(self):
        """Test inferring TextField anchor from title."""
        issue = {"title": "Text field missing label"}
        result = DiffParser.infer_anchor_text(issue)
        assert result == "TextField("

    def test_infer_button_from_title(self):
        """Test inferring Button anchor from title."""
        issue = {"title": "Button lacks accessible name"}
        result = DiffParser.infer_anchor_text(issue)
        assert result == "Button("

    def test_infer_clickable_from_title(self):
        """Test inferring clickable anchor from title."""
        issue = {
            "title": "Clickable element missing semantics",
            "suggested_fix": "modifier = Modifier.clickable { }.semantics { }"
        }
        result = DiffParser.infer_anchor_text(issue)
        assert result == ".clickable"

    def test_infer_semantics_from_suggested_fix(self):
        """Test inferring semantics anchor from suggested_fix."""
        issue = {
            "title": "Missing role information",
            "suggested_fix": "Modifier.semantics { role = Role.Button }"
        }
        result = DiffParser.infer_anchor_text(issue)
        assert result == ".semantics"

    def test_no_inference_for_unrecognized_pattern(self):
        """Test that no anchor is inferred for unrecognized patterns."""
        issue = {"title": "Complex layout issue"}
        result = DiffParser.infer_anchor_text(issue)
        assert result is None


class TestResolveAnchorLine:
    """Tests for resolve_anchor_line function."""

    def test_resolve_with_explicit_anchor_text(self):
        """Test resolution with explicit anchor_text."""
        issue = {
            "line": 379,
            "title": "Slider missing label",
            "anchor": {"anchor_text": "Slider("}
        }
        
        # Mock commentable lines and line texts
        commentable_lines = [378, 379, 380, 381, 388, 389, 390]
        line_texts = {
            378: "    Text(\"Volume Settings\")",
            379: "    ",
            380: "    // Volume slider",
            381: "    Slider(",
            388: "        value = 0.5f,",
            389: "        onValueChange = { },",
            390: "        modifier = Modifier.fillMaxWidth()"
        }
        
        result = DiffParser.resolve_anchor_line(issue, commentable_lines, line_texts)
        assert result == 381, "Should anchor to Slider( line, not line 379"

    def test_resolve_with_inferred_anchor(self):
        """Test resolution with inferred anchor from title."""
        issue = {
            "line": 390,
            "title": "TextField missing accessibility label"
        }
        
        commentable_lines = [390, 391, 392, 393, 400, 401, 402]
        line_texts = {
            390: "    Text(\"Settings\")",
            391: "    ",
            392: "    TextField(",
            393: "        value = \"test\",",
            400: "        onValueChange = { }",
            401: "    )",
            402: "}"
        }
        
        result = DiffParser.resolve_anchor_line(issue, commentable_lines, line_texts)
        assert result == 392, "Should infer TextField( and anchor to that line"

    def test_resolve_clickable_modifier(self):
        """Test resolution for clickable modifier."""
        issue = {
            "line": 395,
            "title": "Clickable Box missing semantics",
            "suggested_fix": "modifier = Modifier.clickable { }.semantics { }"
        }
        
        commentable_lines = [393, 394, 395, 396, 397]
        line_texts = {
            393: "    Box(",
            394: "        modifier = Modifier",
            395: "            .clickable { /* handle */ }",
            396: "            .padding(8.dp)",
            397: "    ) {"
        }
        
        result = DiffParser.resolve_anchor_line(issue, commentable_lines, line_texts)
        assert result == 395, "Should anchor to .clickable line"

    def test_resolve_case_insensitive_match(self):
        """Test that case-insensitive matching works as fallback."""
        issue = {
            "line": 100,
            "title": "Button accessibility issue",
            "anchor": {"anchor_text": "button("}  # lowercase
        }
        
        commentable_lines = [100, 101, 102, 103]
        line_texts = {
            100: "    Text(\"Click here\")",
            101: "    Button(",  # uppercase B
            102: "        onClick = { }",
            103: "    )"
        }
        
        result = DiffParser.resolve_anchor_line(issue, commentable_lines, line_texts)
        assert result == 101, "Should match case-insensitively"

    def test_resolve_picks_closest_when_multiple_matches(self):
        """Test that closest match is picked when multiple exist."""
        issue = {
            "line": 200,
            "title": "Button missing label",
            "anchor": {"anchor_text": "Button("}
        }
        
        # Two Button( calls - one at 150, one at 210
        commentable_lines = [150, 151, 200, 201, 210, 211]
        line_texts = {
            150: "    Button(",  # Far from line 200
            151: "        onClick = { }",
            200: "    Text(\"Actions\")",
            201: "    ",
            210: "    Button(",  # Close to line 200
            211: "        onClick = { }"
        }
        
        result = DiffParser.resolve_anchor_line(issue, commentable_lines, line_texts)
        assert result == 210, "Should pick the Button( closest to original line 200"

    def test_resolve_fallback_to_nearest_when_no_anchor(self):
        """Test fallback to nearest commentable line when no anchor match."""
        issue = {
            "line": 104,
            "title": "Generic issue"
        }
        
        commentable_lines = [100, 101, 105, 110]
        line_texts = {
            100: "    fun test() {",
            101: "        val x = 1",
            105: "        return x",
            110: "    }"
        }
        
        result = DiffParser.resolve_anchor_line(issue, commentable_lines, line_texts)
        # Should fall back to nearest - line 105 (distance 1 from 104)
        assert result == 105

    def test_resolve_returns_none_for_invalid_input(self):
        """Test that None is returned for invalid inputs."""
        issue = {"line": 0}
        result = DiffParser.resolve_anchor_line(issue, [], {})
        assert result is None

        issue = {"line": -5}
        result = DiffParser.resolve_anchor_line(issue, [1, 2, 3], {1: "test"})
        assert result is None


class TestValidateIssuesWithAnchorResolution:
    """Tests for validate_issues_in_batch with anchor resolution."""

    def test_validate_with_anchor_resolution(self):
        """Test that anchor resolution is used when line_texts provided."""
        parser = DiffParser()
        line_texts = parser.extract_line_texts(SAMPLE_COMPOSE_SLIDER_DIFF)
        commentable_lines = parser.extract_commentable_lines(SAMPLE_COMPOSE_SLIDER_DIFF)
        
        file_path = "shared/src/commonMain/kotlin/App.kt"
        
        # Issue pointing to early line but should anchor to Slider(
        issues = [
            {
                "file": file_path,
                "line": 379,  # Early in the hunk
                "title": "Slider missing accessibility label",
                "severity": "High",
                "wcag_sc": "4.1.2"
            }
        ]
        
        validated = validate_issues_in_batch(
            issues, [file_path], commentable_lines, line_texts
        )
        
        assert len(validated) == 1
        # Line should be adjusted to Slider( line (inferred anchor)
        # The exact line depends on the diff, but it should be higher than 379
        assert validated[0]["line"] != 379
        assert validated[0]["line"] > 379

    def test_validate_with_explicit_anchor(self):
        """Test validation with explicit anchor object."""
        parser = DiffParser()
        line_texts = parser.extract_line_texts(SAMPLE_COMPOSE_SLIDER_DIFF)
        commentable_lines = parser.extract_commentable_lines(SAMPLE_COMPOSE_SLIDER_DIFF)
        
        file_path = "shared/src/commonMain/kotlin/App.kt"
        
        issues = [
            {
                "file": file_path,
                "line": 385,
                "title": "Clickable Box missing semantics",
                "severity": "High",
                "wcag_sc": "4.1.2",
                "anchor": {"anchor_text": ".clickable"}
            }
        ]
        
        validated = validate_issues_in_batch(
            issues, [file_path], commentable_lines, line_texts
        )
        
        assert len(validated) == 1
        # Should anchor to .clickable line
        validated_line = validated[0]["line"]
        assert ".clickable" in line_texts[file_path][validated_line]

    def test_validate_backward_compatibility_without_line_texts(self):
        """Test that validation still works without line_texts (backward compat)."""
        issues = [
            {"file": "app/test.py", "line": 4, "title": "Issue 1"},
        ]
        batch_files = ["app/test.py"]
        commentable = {"app/test.py": [1, 2, 5, 10]}
        
        # Call without line_texts (old behavior)
        result = validate_issues_in_batch(issues, batch_files, commentable)
        
        assert len(result) == 1
        # Should adjust to nearest commentable (5)
        assert result[0]["line"] == 5


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

