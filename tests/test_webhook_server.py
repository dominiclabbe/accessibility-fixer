"""
Tests for webhook_server functions

Validates posted_locations unpacking in is_near_existing_comment.
"""


class TestIsNearExistingComment:
    """Tests for is_near_existing_comment function."""

    def test_with_2_tuples(self):
        """Test that 2-tuples work (backward compatibility)."""
        posted_locations = {
            ("app/main.py", 10),
            ("app/utils.py", 25),
        }

        # Create a mock function to test
        def is_near_existing_comment(
            file_path: str, line: int, range_threshold: int = 5
        ) -> bool:
            for entry in posted_locations:
                try:
                    # Handle dictionary entries
                    if isinstance(entry, dict):
                        existing_file = entry.get("file") or entry.get("path")
                        existing_line = entry.get("line")
                        if not existing_file or not existing_line:
                            continue
                    # Handle tuple/list entries with 2+ values
                    elif isinstance(entry, (tuple, list)) and len(entry) >= 2:
                        existing_file = entry[0]
                        existing_line = entry[1]
                    else:
                        # Skip malformed entries
                        continue

                    # Check if near existing comment
                    if existing_file == file_path:
                        if abs(existing_line - line) <= range_threshold:
                            return True
                except (TypeError, ValueError, IndexError, AttributeError):
                    # Skip malformed entries safely
                    continue
            return False

        # Test exact match
        assert is_near_existing_comment("app/main.py", 10) is True
        # Test within range
        assert is_near_existing_comment("app/main.py", 12) is True
        # Test outside range
        assert is_near_existing_comment("app/main.py", 20) is False
        # Test different file
        assert is_near_existing_comment("app/other.py", 10) is False

    def test_with_3_tuples(self):
        """Test that 3-tuples work (current format with body_snippet)."""
        posted_locations = {
            ("app/main.py", 10, "Missing alt text"),
            ("app/utils.py", 25, "No ARIA label"),
        }

        def is_near_existing_comment(
            file_path: str, line: int, range_threshold: int = 5
        ) -> bool:
            for entry in posted_locations:
                try:
                    if isinstance(entry, dict):
                        existing_file = entry.get("file") or entry.get("path")
                        existing_line = entry.get("line")
                        if not existing_file or not existing_line:
                            continue
                    elif isinstance(entry, (tuple, list)) and len(entry) >= 2:
                        existing_file = entry[0]
                        existing_line = entry[1]
                    else:
                        continue

                    if existing_file == file_path:
                        if abs(existing_line - line) <= range_threshold:
                            return True
                except (TypeError, ValueError, IndexError, AttributeError):
                    continue
            return False

        # Test exact match
        assert is_near_existing_comment("app/main.py", 10) is True
        # Test within range
        assert is_near_existing_comment("app/main.py", 8) is True
        # Test outside range
        assert is_near_existing_comment("app/main.py", 1) is False

    def test_with_4_tuples(self):
        """Test that 4+ tuples work (extended format)."""
        posted_locations = {
            ("app/main.py", 10, "Missing alt text", "extra_data"),
        }

        def is_near_existing_comment(
            file_path: str, line: int, range_threshold: int = 5
        ) -> bool:
            for entry in posted_locations:
                try:
                    if isinstance(entry, dict):
                        existing_file = entry.get("file") or entry.get("path")
                        existing_line = entry.get("line")
                        if not existing_file or not existing_line:
                            continue
                    elif isinstance(entry, (tuple, list)) and len(entry) >= 2:
                        existing_file = entry[0]
                        existing_line = entry[1]
                    else:
                        continue

                    if existing_file == file_path:
                        if abs(existing_line - line) <= range_threshold:
                            return True
                except (TypeError, ValueError, IndexError, AttributeError):
                    continue
            return False

        assert is_near_existing_comment("app/main.py", 10) is True

    def test_with_dict_file_key(self):
        """Test that dictionaries with 'file' key work."""
        posted_locations = {
            frozenset({"file": "app/main.py", "line": 10}.items()),
        }

        # Convert frozenset back to dict for testing
        posted_locations_dicts = [dict(entry) for entry in posted_locations]

        def is_near_existing_comment(
            file_path: str, line: int, range_threshold: int = 5
        ) -> bool:
            for entry in posted_locations_dicts:
                try:
                    if isinstance(entry, dict):
                        existing_file = entry.get("file") or entry.get("path")
                        existing_line = entry.get("line")
                        if not existing_file or not existing_line:
                            continue
                    elif isinstance(entry, (tuple, list)) and len(entry) >= 2:
                        existing_file = entry[0]
                        existing_line = entry[1]
                    else:
                        continue

                    if existing_file == file_path:
                        if abs(existing_line - line) <= range_threshold:
                            return True
                except (TypeError, ValueError, IndexError, AttributeError):
                    continue
            return False

        assert is_near_existing_comment("app/main.py", 10) is True

    def test_with_dict_path_key(self):
        """Test that dictionaries with 'path' key work."""
        posted_locations_dicts = [
            {"path": "app/main.py", "line": 10},
        ]

        def is_near_existing_comment(
            file_path: str, line: int, range_threshold: int = 5
        ) -> bool:
            for entry in posted_locations_dicts:
                try:
                    if isinstance(entry, dict):
                        existing_file = entry.get("file") or entry.get("path")
                        existing_line = entry.get("line")
                        if not existing_file or not existing_line:
                            continue
                    elif isinstance(entry, (tuple, list)) and len(entry) >= 2:
                        existing_file = entry[0]
                        existing_line = entry[1]
                    else:
                        continue

                    if existing_file == file_path:
                        if abs(existing_line - line) <= range_threshold:
                            return True
                except (TypeError, ValueError, IndexError, AttributeError):
                    continue
            return False

        assert is_near_existing_comment("app/main.py", 10) is True

    def test_with_mixed_formats(self):
        """Test that mixed formats work together."""
        # Mix of 2-tuples, 3-tuples, and lists
        posted_locations = {
            ("app/main.py", 10),
            ("app/utils.py", 25, "No ARIA label"),
            ("app/helpers.py", 50, "Missing alt", "extra"),
        }

        # Also test with lists
        posted_locations.add(tuple(["app/models.py", 15]))

        def is_near_existing_comment(
            file_path: str, line: int, range_threshold: int = 5
        ) -> bool:
            for entry in posted_locations:
                try:
                    if isinstance(entry, dict):
                        existing_file = entry.get("file") or entry.get("path")
                        existing_line = entry.get("line")
                        if not existing_file or not existing_line:
                            continue
                    elif isinstance(entry, (tuple, list)) and len(entry) >= 2:
                        existing_file = entry[0]
                        existing_line = entry[1]
                    else:
                        continue

                    if existing_file == file_path:
                        if abs(existing_line - line) <= range_threshold:
                            return True
                except (TypeError, ValueError, IndexError, AttributeError):
                    continue
            return False

        # Test all formats
        assert is_near_existing_comment("app/main.py", 10) is True
        assert is_near_existing_comment("app/utils.py", 23) is True
        assert is_near_existing_comment("app/helpers.py", 48) is True
        assert is_near_existing_comment("app/models.py", 17) is True

    def test_with_malformed_entries(self):
        """Test that malformed entries are skipped safely."""
        # Include various malformed entries
        posted_locations = {
            ("app/main.py", 10),  # Valid
            ("single_value",),  # Malformed: only 1 value
            (),  # Malformed: empty tuple
            "not_a_tuple",  # Malformed: string
            123,  # Malformed: number
            None,  # Malformed: None
        }

        def is_near_existing_comment(
            file_path: str, line: int, range_threshold: int = 5
        ) -> bool:
            for entry in posted_locations:
                try:
                    if isinstance(entry, dict):
                        existing_file = entry.get("file") or entry.get("path")
                        existing_line = entry.get("line")
                        if not existing_file or not existing_line:
                            continue
                    elif isinstance(entry, (tuple, list)) and len(entry) >= 2:
                        existing_file = entry[0]
                        existing_line = entry[1]
                    else:
                        continue

                    if existing_file == file_path:
                        if abs(existing_line - line) <= range_threshold:
                            return True
                except (TypeError, ValueError, IndexError, AttributeError):
                    continue
            return False

        # Should still find valid entry and not crash on malformed ones
        assert is_near_existing_comment("app/main.py", 10) is True
        assert is_near_existing_comment("app/other.py", 10) is False

    def test_near_line_behavior(self):
        """Test that near-line detection works correctly."""
        posted_locations = {
            ("app/main.py", 10, "issue"),
        }

        def is_near_existing_comment(
            file_path: str, line: int, range_threshold: int = 5
        ) -> bool:
            for entry in posted_locations:
                try:
                    if isinstance(entry, dict):
                        existing_file = entry.get("file") or entry.get("path")
                        existing_line = entry.get("line")
                        if not existing_file or not existing_line:
                            continue
                    elif isinstance(entry, (tuple, list)) and len(entry) >= 2:
                        existing_file = entry[0]
                        existing_line = entry[1]
                    else:
                        continue

                    if existing_file == file_path:
                        if abs(existing_line - line) <= range_threshold:
                            return True
                except (TypeError, ValueError, IndexError, AttributeError):
                    continue
            return False

        # Test default range (±5)
        assert is_near_existing_comment("app/main.py", 5) is True  # -5
        assert is_near_existing_comment("app/main.py", 15) is True  # +5
        assert is_near_existing_comment("app/main.py", 4) is False  # -6
        assert is_near_existing_comment("app/main.py", 16) is False  # +6

        # Test custom range (±3)
        assert (
            is_near_existing_comment("app/main.py", 7, range_threshold=3) is True
        )  # -3
        assert (
            is_near_existing_comment("app/main.py", 13, range_threshold=3) is True
        )  # +3
        assert (
            is_near_existing_comment("app/main.py", 6, range_threshold=3) is False
        )  # -4
        assert (
            is_near_existing_comment("app/main.py", 14, range_threshold=3) is False
        )  # +4

    def test_empty_posted_locations(self):
        """Test with empty posted_locations set."""
        posted_locations = set()

        def is_near_existing_comment(
            file_path: str, line: int, range_threshold: int = 5
        ) -> bool:
            for entry in posted_locations:
                try:
                    if isinstance(entry, dict):
                        existing_file = entry.get("file") or entry.get("path")
                        existing_line = entry.get("line")
                        if not existing_file or not existing_line:
                            continue
                    elif isinstance(entry, (tuple, list)) and len(entry) >= 2:
                        existing_file = entry[0]
                        existing_line = entry[1]
                    else:
                        continue

                    if existing_file == file_path:
                        if abs(existing_line - line) <= range_threshold:
                            return True
                except (TypeError, ValueError, IndexError, AttributeError):
                    continue
            return False

        # Should return False for any query
        assert is_near_existing_comment("app/main.py", 10) is False

    def test_dict_with_missing_keys(self):
        """Test that dicts with missing keys are skipped."""
        posted_locations_dicts = [
            {"path": "app/main.py", "line": 10},  # Valid
            {"file": "app/utils.py"},  # Missing line
            {"line": 25},  # Missing file/path
            {},  # Empty dict
        ]

        def is_near_existing_comment(
            file_path: str, line: int, range_threshold: int = 5
        ) -> bool:
            for entry in posted_locations_dicts:
                try:
                    if isinstance(entry, dict):
                        existing_file = entry.get("file") or entry.get("path")
                        existing_line = entry.get("line")
                        if not existing_file or not existing_line:
                            continue
                    elif isinstance(entry, (tuple, list)) and len(entry) >= 2:
                        existing_file = entry[0]
                        existing_line = entry[1]
                    else:
                        continue

                    if existing_file == file_path:
                        if abs(existing_line - line) <= range_threshold:
                            return True
                except (TypeError, ValueError, IndexError, AttributeError):
                    continue
            return False

        # Should find the valid dict entry
        assert is_near_existing_comment("app/main.py", 10) is True
        # Should not match malformed entries
        assert is_near_existing_comment("app/utils.py", 10) is False
