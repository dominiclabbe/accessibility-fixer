"""
Tests for PRReviewer

Validates the review logic and existing_comments handling.
"""

import pytest
from unittest.mock import patch
from app.pr_reviewer import PRReviewer


class TestPRReviewerExistingComments:
    """Tests for existing_comments handling in _create_review_prompt."""

    @pytest.fixture
    def reviewer(self):
        """Create a mock PRReviewer instance."""
        # Mock the openai client to avoid actual API calls
        with patch("app.pr_reviewer.openai.OpenAI"):
            reviewer = PRReviewer(
                scout_api_key="test-key",
                scout_base_url="https://test.example.com",
                scout_model="test-model",
            )
            return reviewer

    def test_create_prompt_with_2_tuple_existing_comments(self, reviewer):
        """Test that 2-tuple existing_comments work correctly."""
        pr_diff = "mock diff content"
        files = ["file1.swift"]
        platforms = ["iOS"]
        guides = "mock guides"
        existing_comments = [
            ("file1.swift", 10),
            ("file2.swift", 25),
        ]

        prompt = reviewer._create_review_prompt(
            pr_diff, files, platforms, guides, existing_comments, None
        )

        # Verify the prompt was generated without errors
        assert prompt is not None
        assert "# Existing Comments" in prompt
        assert "file1.swift:10" in prompt
        assert "file2.swift:25" in prompt
        assert "Do NOT report issues at these locations" in prompt

    def test_create_prompt_with_3_tuple_existing_comments(self, reviewer):
        """Test that 3-tuple existing_comments (with anchor_signature) work correctly."""
        pr_diff = "mock diff content"
        files = ["file1.swift"]
        platforms = ["iOS"]
        guides = "mock guides"
        existing_comments = [
            ("file1.swift", 10, "Button missing label"),
            ("file2.swift", 25, "Image missing alt text"),
            ("file3.kt", 30, "Missing content description"),
        ]

        prompt = reviewer._create_review_prompt(
            pr_diff, files, platforms, guides, existing_comments, None
        )

        # Verify the prompt was generated without errors
        assert prompt is not None
        assert "# Existing Comments" in prompt
        # Should use first two elements of each tuple
        assert "file1.swift:10" in prompt
        assert "file2.swift:25" in prompt
        assert "file3.kt:30" in prompt
        # The third element (body snippet) should not appear as part of the location line
        # Verify format is "- file:line" not "- file:line:snippet"
        lines = prompt.split("\n")
        location_lines = [l for l in lines if l.startswith("- ") and ":" in l]
        for loc_line in location_lines:
            # Each location line should be "- path:line" format, not include extra data
            parts = loc_line.replace("- ", "").split(":")
            assert (
                len(parts) == 2
            ), f"Location line should be '- path:line' format: {loc_line}"
        assert "Do NOT report issues at these locations" in prompt

    def test_create_prompt_with_dict_existing_comments(self, reviewer):
        """Test that dict-based existing_comments work correctly."""
        pr_diff = "mock diff content"
        files = ["file1.swift"]
        platforms = ["iOS"]
        guides = "mock guides"
        existing_comments = [
            {"file": "file1.swift", "line": 15},
            {"path": "file2.kt", "line": 42},  # Alternative 'path' key
        ]

        prompt = reviewer._create_review_prompt(
            pr_diff, files, platforms, guides, existing_comments, None
        )

        # Verify the prompt was generated without errors
        assert prompt is not None
        assert "# Existing Comments" in prompt
        assert "file1.swift:15" in prompt
        assert "file2.kt:42" in prompt
        assert "Do NOT report issues at these locations" in prompt

    def test_create_prompt_with_mixed_existing_comments(self, reviewer):
        """Test that mixed entry shapes work correctly."""
        pr_diff = "mock diff content"
        files = ["file1.swift"]
        platforms = ["iOS"]
        guides = "mock guides"
        existing_comments = [
            ("file1.swift", 10),  # 2-tuple
            ("file2.swift", 25, "anchor"),  # 3-tuple
            {"file": "file3.kt", "line": 30},  # dict with 'file'
            {"path": "file4.js", "line": 45},  # dict with 'path'
        ]

        prompt = reviewer._create_review_prompt(
            pr_diff, files, platforms, guides, existing_comments, None
        )

        # Verify the prompt was generated without errors
        assert prompt is not None
        assert "# Existing Comments" in prompt
        assert "file1.swift:10" in prompt
        assert "file2.swift:25" in prompt
        assert "file3.kt:30" in prompt
        assert "file4.js:45" in prompt
        assert "Do NOT report issues at these locations" in prompt

    def test_create_prompt_with_malformed_existing_comments(self, reviewer):
        """Test that malformed entries are gracefully ignored."""
        pr_diff = "mock diff content"
        files = ["file1.swift"]
        platforms = ["iOS"]
        guides = "mock guides"
        existing_comments = [
            ("file1.swift", 10),  # Valid 2-tuple
            ("single_value",),  # Malformed: only 1 element
            [],  # Malformed: empty list
            {},  # Malformed: empty dict
            {"file": "file2.swift"},  # Malformed: missing 'line'
            {"line": 50},  # Malformed: missing 'file'/'path'
            "not a tuple or dict",  # Malformed: wrong type
            None,  # Malformed: None
            42,  # Malformed: number
        ]

        # Should not raise an error - malformed entries should be skipped
        prompt = reviewer._create_review_prompt(
            pr_diff, files, platforms, guides, existing_comments, None
        )

        # Verify the prompt was generated without errors
        assert prompt is not None
        assert "# Existing Comments" in prompt
        # Only the valid entry should appear
        assert "file1.swift:10" in prompt
        # Verify malformed entries don't appear as valid "path:line" patterns
        # Look specifically in the Existing Comments section
        sections = prompt.split("# ")
        existing_section = None
        for section in sections:
            if section.startswith("Existing Comments"):
                existing_section = section
                break
        assert existing_section is not None
        # Count location lines in existing comments section only
        location_lines = [
            l.strip() for l in existing_section.split("\n") if l.strip().startswith("- ") and ":" in l
        ]
        # Should only have 1 valid location from the valid 2-tuple
        assert (
            len(location_lines) == 1
        ), f"Expected 1 location line, found {len(location_lines)}: {location_lines}"
        assert location_lines[0] == "- file1.swift:10"

    def test_create_prompt_with_empty_existing_comments(self, reviewer):
        """Test that empty existing_comments list doesn't add the section."""
        pr_diff = "mock diff content"
        files = ["file1.swift"]
        platforms = ["iOS"]
        guides = "mock guides"
        existing_comments = []

        prompt = reviewer._create_review_prompt(
            pr_diff, files, platforms, guides, existing_comments, None
        )

        # Verify the prompt was generated without errors
        assert prompt is not None
        # Empty list should be treated as falsy, so no section should be added
        assert "# Existing Comments" not in prompt

    def test_create_prompt_without_existing_comments(self, reviewer):
        """Test that None existing_comments doesn't add the section."""
        pr_diff = "mock diff content"
        files = ["file1.swift"]
        platforms = ["iOS"]
        guides = "mock guides"

        prompt = reviewer._create_review_prompt(
            pr_diff, files, platforms, guides, None, None
        )

        # Verify the prompt was generated without errors
        assert prompt is not None
        # No existing_comments should mean no section
        assert "# Existing Comments" not in prompt

    def test_create_prompt_with_4_tuple_existing_comments(self, reviewer):
        """Test that tuples with 4+ elements work (use first two)."""
        pr_diff = "mock diff content"
        files = ["file1.swift"]
        platforms = ["iOS"]
        guides = "mock guides"
        existing_comments = [
            ("file1.swift", 10, "extra1", "extra2", "extra3"),
        ]

        prompt = reviewer._create_review_prompt(
            pr_diff, files, platforms, guides, existing_comments, None
        )

        # Verify the prompt was generated without errors
        assert prompt is not None
        assert "# Existing Comments" in prompt
        assert "file1.swift:10" in prompt

    def test_backward_compatibility_with_original_2_tuple_format(self, reviewer):
        """Test complete backward compatibility with the original 2-tuple format."""
        pr_diff = """
@@ -1,3 +1,5 @@
 func MyComponent() {
+  Button("Click me")
+  Image("icon")
 }
"""
        files = ["MyView.swift"]
        platforms = ["iOS"]
        guides = "Check accessibility labels."
        # Original format: List[Tuple[str, int]]
        existing_comments = [
            ("MyView.swift", 10),
            ("OtherView.swift", 20),
        ]

        # Should work exactly as before
        prompt = reviewer._create_review_prompt(
            pr_diff, files, platforms, guides, existing_comments, None
        )

        assert prompt is not None
        assert "MyView.swift:10" in prompt
        assert "OtherView.swift:20" in prompt
        assert "# Existing Comments" in prompt
        assert "Do NOT report issues at these locations" in prompt
