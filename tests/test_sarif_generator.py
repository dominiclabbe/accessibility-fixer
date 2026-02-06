"""
Tests for SARIF Generator

Validates SARIF report generation from accessibility issues.
"""

import pytest
import json
import tempfile
from pathlib import Path
from app.sarif_generator import SARIFGenerator, generate_and_write_sarif


class TestSARIFGenerator:
    """Tests for SARIFGenerator class."""

    def test_generate_sarif_empty_issues(self):
        """Test generating SARIF with no issues."""
        generator = SARIFGenerator()
        sarif = generator.generate_sarif([])

        assert sarif["version"] == "2.1.0"
        assert len(sarif["runs"]) == 1
        assert len(sarif["runs"][0]["results"]) == 0
        # Should still have at least the generic rule
        assert len(sarif["runs"][0]["tool"]["driver"]["rules"]) >= 1

    def test_generate_sarif_single_issue(self):
        """Test generating SARIF with single issue."""
        issues = [
            {
                "file": "app/test.py",
                "line": 42,
                "severity": "major",
                "wcag_sc": "1.1.1",
                "wcag_level": "A",
                "title": "Missing alt text",
                "description": "Image lacks alternative text",
                "impact": "Screen readers cannot describe image",
                "suggested_fix": "Add alt attribute",
            }
        ]

        generator = SARIFGenerator()
        sarif = generator.generate_sarif(issues)

        # Check structure
        assert sarif["version"] == "2.1.0"
        assert len(sarif["runs"]) == 1

        # Check results
        results = sarif["runs"][0]["results"]
        assert len(results) == 1

        result = results[0]
        assert result["ruleId"] == "wcag-1-1-1"
        assert result["level"] == "error"  # major -> error
        assert result["message"]["text"]
        assert "Image lacks alternative text" in result["message"]["text"]

        # Check location
        location = result["locations"][0]["physicalLocation"]
        assert location["artifactLocation"]["uri"] == "app/test.py"
        assert location["region"]["startLine"] == 42

        # Check properties
        assert result["properties"]["severity"] == "major"
        assert result["properties"]["wcag_sc"] == "1.1.1"

    def test_generate_sarif_multiple_issues(self):
        """Test generating SARIF with multiple issues."""
        issues = [
            {
                "file": "app/page1.html",
                "line": 10,
                "severity": "critical",
                "wcag_sc": "1.1.1",
                "wcag_level": "A",
                "title": "Missing alt text",
                "description": "Critical issue",
            },
            {
                "file": "app/page2.html",
                "line": 20,
                "severity": "minor",
                "wcag_sc": "2.4.6",
                "wcag_level": "AA",
                "title": "Poor heading structure",
                "description": "Minor issue",
            },
        ]

        generator = SARIFGenerator()
        sarif = generator.generate_sarif(issues)

        results = sarif["runs"][0]["results"]
        assert len(results) == 2

        # Check first result
        assert results[0]["ruleId"] == "wcag-1-1-1"
        assert results[0]["level"] == "error"  # critical -> error

        # Check second result
        assert results[1]["ruleId"] == "wcag-2-4-6"
        assert results[1]["level"] == "warning"  # minor -> warning

    def test_severity_mapping(self):
        """Test severity to SARIF level mapping."""
        test_cases = [
            ("critical", "error"),
            ("major", "error"),
            ("minor", "warning"),
            ("info", "note"),
        ]

        for severity, expected_level in test_cases:
            issues = [
                {
                    "file": "test.py",
                    "line": 1,
                    "severity": severity,
                    "wcag_sc": "1.1.1",
                    "title": "Test",
                }
            ]

            generator = SARIFGenerator()
            sarif = generator.generate_sarif(issues)
            result = sarif["runs"][0]["results"][0]

            assert result["level"] == expected_level, f"Failed for severity {severity}"

    def test_make_rule_id_simple(self):
        """Test rule ID generation for simple WCAG SC."""
        generator = SARIFGenerator()

        assert generator._make_rule_id("1.1.1") == "wcag-1-1-1"
        assert generator._make_rule_id("2.4.6") == "wcag-2-4-6"
        assert generator._make_rule_id("3.3.2") == "wcag-3-3-2"

    def test_make_rule_id_multiple_sc(self):
        """Test rule ID generation for multiple WCAG SCs."""
        generator = SARIFGenerator()

        # Should use first SC when multiple are present
        assert generator._make_rule_id("1.1.1; 2.4.6") == "wcag-1-1-1"
        assert generator._make_rule_id("3.3.2 ; 4.1.2") == "wcag-3-3-2"

    def test_generate_sarif_with_repo_info(self):
        """Test generating SARIF with repository information."""
        issues = [
            {
                "file": "app/test.py",
                "line": 1,
                "severity": "Low",
                "wcag_sc": "1.1.1",
                "title": "Test issue",
            }
        ]

        generator = SARIFGenerator()
        sarif = generator.generate_sarif(
            issues,
            repo_uri="https://github.com/owner/repo",
            repo_ref="abc123def",
        )

        # Check version control provenance
        provenance = sarif["runs"][0]["versionControlProvenance"]
        assert len(provenance) == 1
        assert provenance[0]["repositoryUri"] == "https://github.com/owner/repo"
        assert provenance[0]["revisionId"] == "abc123def"

    def test_generate_rules_from_issues(self):
        """Test that rules are generated from unique WCAG SCs."""
        issues = [
            {"file": "a.py", "line": 1, "wcag_sc": "1.1.1", "title": "Issue 1", "severity": "High"},
            {"file": "b.py", "line": 2, "wcag_sc": "1.1.1", "title": "Issue 2", "severity": "Medium"},
            {"file": "c.py", "line": 3, "wcag_sc": "2.4.6", "title": "Issue 3", "severity": "Low"},
        ]

        generator = SARIFGenerator()
        sarif = generator.generate_sarif(issues)

        rules = sarif["runs"][0]["tool"]["driver"]["rules"]

        # Should have rules for 1.1.1, 2.4.6, and generic
        rule_ids = [rule["id"] for rule in rules]
        assert "wcag-1-1-1" in rule_ids
        assert "wcag-2-4-6" in rule_ids
        assert "accessibility-generic" in rule_ids

    def test_issue_without_wcag_sc(self):
        """Test handling issues without WCAG SC."""
        issues = [
            {
                "file": "test.py",
                "line": 1,
                "severity": "Medium",
                "wcag_sc": "",  # No WCAG SC
                "title": "Generic issue",
                "description": "Some problem",
            }
        ]

        generator = SARIFGenerator()
        sarif = generator.generate_sarif(issues)

        result = sarif["runs"][0]["results"][0]
        assert result["ruleId"] == "accessibility-generic"

    def test_write_sarif_file(self):
        """Test writing SARIF to file."""
        issues = [
            {
                "file": "test.py",
                "line": 1,
                "severity": "Low",
                "wcag_sc": "1.1.1",
                "title": "Test",
            }
        ]

        generator = SARIFGenerator()
        sarif = generator.generate_sarif(issues)

        # Write to temp file
        with tempfile.TemporaryDirectory() as tmpdir:
            output_path = Path(tmpdir) / "test.sarif"
            success = generator.write_sarif_file(sarif, str(output_path))

            assert success is True
            assert output_path.exists()

            # Verify content
            with output_path.open() as f:
                loaded = json.load(f)
                assert loaded["version"] == "2.1.0"
                assert len(loaded["runs"]) == 1

    def test_write_sarif_file_creates_directories(self):
        """Test that write_sarif_file creates parent directories."""
        issues = [{"file": "test.py", "line": 1, "severity": "Low", "wcag_sc": "1.1.1", "title": "Test"}]

        generator = SARIFGenerator()
        sarif = generator.generate_sarif(issues)

        with tempfile.TemporaryDirectory() as tmpdir:
            # Use nested path
            output_path = Path(tmpdir) / "subdir" / "nested" / "report.sarif"
            success = generator.write_sarif_file(sarif, str(output_path))

            assert success is True
            assert output_path.exists()


class TestGenerateAndWriteSarif:
    """Tests for generate_and_write_sarif convenience function."""

    def test_generate_and_write_sarif_complete_flow(self):
        """Test complete flow of generating and writing SARIF."""
        issues = [
            {
                "file": "app/main.py",
                "line": 42,
                "severity": "High",
                "wcag_sc": "1.1.1",
                "wcag_level": "A",
                "title": "Missing alt text",
                "description": "Image lacks alt text",
            }
        ]

        with tempfile.TemporaryDirectory() as tmpdir:
            output_path = Path(tmpdir) / "report.sarif"

            success = generate_and_write_sarif(
                issues,
                str(output_path),
                repo_uri="https://github.com/test/repo",
                repo_ref="main",
            )

            assert success is True
            assert output_path.exists()

            # Verify content
            with output_path.open() as f:
                sarif = json.load(f)
                assert sarif["version"] == "2.1.0"
                assert len(sarif["runs"][0]["results"]) == 1
                assert sarif["runs"][0]["versionControlProvenance"][0]["repositoryUri"] == "https://github.com/test/repo"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
