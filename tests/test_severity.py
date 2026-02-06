"""
Tests for severity-based functionality

Validates severity normalization, commit status logic, and max severity calculation.
"""

import pytest
from unittest.mock import patch, Mock
from app.pr_reviewer import PRReviewer
from app.comment_poster import CommentPoster
from app.webhook_server import get_max_severity, determine_commit_status


class TestSeverityNormalization:
    """Tests for severity normalization in PRReviewer._normalize_issue()."""

    @pytest.fixture
    def reviewer(self):
        """Create a mock PRReviewer instance."""
        with patch("app.pr_reviewer.openai.OpenAI"):
            reviewer = PRReviewer(
                scout_api_key="test-key",
                scout_base_url="https://test.example.com",
                scout_model="test-model",
            )
            return reviewer

    def test_normalize_issue_defaults_missing_severity_to_minor(self, reviewer):
        """Test that missing severity defaults to 'minor'."""
        issue = {
            "file": "test.swift",
            "line": 10,
            "title": "Test Issue",
            "description": "Test description",
            "impact": "Test impact",
            "wcag_sc": "1.1.1",
            "wcag_level": "A",
            "current_code": "test code",
            "suggested_fix": "test fix",
            "resources": [],
        }
        
        normalized = reviewer._normalize_issue(issue)
        
        assert normalized is not None
        assert normalized["severity"] == "minor"

    def test_normalize_issue_defaults_empty_severity_to_minor(self, reviewer):
        """Test that empty string severity defaults to 'minor'."""
        issue = {
            "file": "test.swift",
            "line": 10,
            "severity": "",
            "title": "Test Issue",
            "description": "Test description",
            "impact": "Test impact",
            "wcag_sc": "1.1.1",
            "wcag_level": "A",
            "current_code": "test code",
            "suggested_fix": "test fix",
            "resources": [],
        }
        
        normalized = reviewer._normalize_issue(issue)
        
        assert normalized is not None
        assert normalized["severity"] == "minor"

    def test_normalize_issue_defaults_none_severity_to_minor(self, reviewer):
        """Test that None severity defaults to 'minor'."""
        issue = {
            "file": "test.swift",
            "line": 10,
            "severity": None,
            "title": "Test Issue",
            "description": "Test description",
            "impact": "Test impact",
            "wcag_sc": "1.1.1",
            "wcag_level": "A",
            "current_code": "test code",
            "suggested_fix": "test fix",
            "resources": [],
        }
        
        normalized = reviewer._normalize_issue(issue)
        
        assert normalized is not None
        assert normalized["severity"] == "minor"

    def test_normalize_issue_preserves_valid_severity_lowercase(self, reviewer):
        """Test that valid lowercase severity values are preserved."""
        for severity in ["info", "minor", "major", "critical"]:
            issue = {
                "file": "test.swift",
                "line": 10,
                "severity": severity,
                "title": "Test Issue",
                "description": "Test description",
                "impact": "Test impact",
                "wcag_sc": "1.1.1",
                "wcag_level": "A",
                "current_code": "test code",
                "suggested_fix": "test fix",
                "resources": [],
            }
            
            normalized = reviewer._normalize_issue(issue)
            
            assert normalized is not None
            assert normalized["severity"] == severity

    def test_normalize_issue_converts_uppercase_to_lowercase(self, reviewer):
        """Test that uppercase severity values are converted to lowercase."""
        issue = {
            "file": "test.swift",
            "line": 10,
            "severity": "CRITICAL",
            "title": "Test Issue",
            "description": "Test description",
            "impact": "Test impact",
            "wcag_sc": "1.1.1",
            "wcag_level": "A",
            "current_code": "test code",
            "suggested_fix": "test fix",
            "resources": [],
        }
        
        normalized = reviewer._normalize_issue(issue)
        
        assert normalized is not None
        assert normalized["severity"] == "critical"

    def test_normalize_issue_coerces_invalid_severity_to_minor(self, reviewer):
        """Test that invalid severity values are coerced to 'minor'."""
        invalid_severities = ["high", "medium", "low", "unknown", "test", "123"]
        
        for invalid_severity in invalid_severities:
            issue = {
                "file": "test.swift",
                "line": 10,
                "severity": invalid_severity,
                "title": "Test Issue",
                "description": "Test description",
                "impact": "Test impact",
                "wcag_sc": "1.1.1",
                "wcag_level": "A",
                "current_code": "test code",
                "suggested_fix": "test fix",
                "resources": [],
            }
            
            normalized = reviewer._normalize_issue(issue)
            
            assert normalized is not None
            assert normalized["severity"] == "minor", f"Failed for invalid severity: {invalid_severity}"


class TestSeverityCounting:
    """Tests for severity counting in CommentPoster."""

    def test_count_severities_with_all_levels(self):
        """Test counting with all severity levels."""
        issues = [
            {"severity": "critical"},
            {"severity": "critical"},
            {"severity": "major"},
            {"severity": "minor"},
            {"severity": "minor"},
            {"severity": "minor"},
            {"severity": "info"},
        ]
        
        counts = CommentPoster._count_severities(issues)
        
        assert counts["critical"] == 2
        assert counts["major"] == 1
        assert counts["minor"] == 3
        assert counts["info"] == 1

    def test_count_severities_empty_list(self):
        """Test counting with empty list."""
        issues = []
        
        counts = CommentPoster._count_severities(issues)
        
        assert counts["critical"] == 0
        assert counts["major"] == 0
        assert counts["minor"] == 0
        assert counts["info"] == 0

    def test_count_severities_with_missing_severity(self):
        """Test counting when issues have missing severity (defaults to minor via .get())."""
        issues = [
            {"severity": "critical"},
            {},  # Missing severity - will default to "minor" via .get("severity", "minor")
            {"severity": "major"},
        ]
        
        counts = CommentPoster._count_severities(issues)
        
        # _count_severities uses .get("severity", "minor"), so missing keys default to "minor"
        assert counts["critical"] == 1
        assert counts["major"] == 1
        assert counts["minor"] == 1
        assert counts["info"] == 0


class TestMaxSeverity:
    """Tests for max severity calculation."""

    def test_get_max_severity_critical(self):
        """Test that critical is identified as max severity."""
        issues = [
            {"severity": "info"},
            {"severity": "minor"},
            {"severity": "critical"},
            {"severity": "major"},
        ]
        
        max_sev = get_max_severity(issues)
        
        assert max_sev == "critical"

    def test_get_max_severity_major(self):
        """Test that major is identified as max severity when no critical."""
        issues = [
            {"severity": "info"},
            {"severity": "minor"},
            {"severity": "major"},
            {"severity": "minor"},
        ]
        
        max_sev = get_max_severity(issues)
        
        assert max_sev == "major"

    def test_get_max_severity_minor(self):
        """Test that minor is identified as max severity when no major or critical."""
        issues = [
            {"severity": "info"},
            {"severity": "minor"},
            {"severity": "info"},
        ]
        
        max_sev = get_max_severity(issues)
        
        assert max_sev == "minor"

    def test_get_max_severity_info(self):
        """Test that info is identified as max severity when only info issues."""
        issues = [
            {"severity": "info"},
            {"severity": "info"},
        ]
        
        max_sev = get_max_severity(issues)
        
        assert max_sev == "info"

    def test_get_max_severity_empty_list(self):
        """Test that info is returned for empty list."""
        issues = []
        
        max_sev = get_max_severity(issues)
        
        assert max_sev == "info"

    def test_get_max_severity_with_missing_severity(self):
        """Test that missing severity defaults to minor via .get() in max calculation."""
        issues = [
            {"severity": "info"},
            {},  # Missing severity - will default to "minor" via .get("severity", "minor")
        ]
        
        max_sev = get_max_severity(issues)
        
        # get_max_severity uses .get("severity", "minor"), so missing keys default to "minor"
        assert max_sev == "minor"


class TestCommitStatusLogic:
    """Tests for commit status selection logic."""

    def test_commit_status_no_issues_returns_success(self):
        """Test that 0 issues results in 'success' status."""
        issues = []
        
        status, description = determine_commit_status(issues)
        
        assert status == "success"
        assert "No accessibility issues found" in description

    def test_commit_status_critical_issues_returns_failure(self):
        """Test that critical issues result in 'failure' status."""
        issues = [
            {"severity": "minor"},
            {"severity": "critical"},
            {"severity": "major"},
        ]
        
        status, description = determine_commit_status(issues)
        
        assert status == "failure"
        assert "3 issue(s) found (max severity: critical)" in description

    def test_commit_status_non_critical_issues_returns_neutral(self):
        """Test that non-critical issues result in 'neutral' status."""
        test_cases = [
            [{"severity": "major"}],
            [{"severity": "minor"}],
            [{"severity": "info"}],
            [{"severity": "major"}, {"severity": "minor"}],
        ]
        
        for issues in test_cases:
            status, description = determine_commit_status(issues)
            max_sev = get_max_severity(issues)
            
            assert status == "neutral"
            assert f"{len(issues)} issue(s) found (max severity: {max_sev})" in description

    def test_commit_status_description_format(self):
        """Test that commit status description follows the required format."""
        issues = [
            {"severity": "major"},
            {"severity": "minor"},
            {"severity": "minor"},
        ]
        
        status, description = determine_commit_status(issues)
        
        assert "3 issue(s) found (max severity: major)" in description
        assert "max severity:" in description
        assert "3 issue(s)" in description
