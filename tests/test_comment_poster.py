"""
Tests for CommentPoster

Validates comment posting, formatting, and debug footer functionality.
"""

import os
import pytest
from unittest.mock import patch, MagicMock
from app.comment_poster import (
    CommentPoster,
    get_app_version,
    get_debug_footer,
)


class TestGetAppVersion:
    """Tests for get_app_version function."""

    def test_version_from_env_var(self):
        """Test that env var takes priority."""
        with patch.dict(os.environ, {"ACCESSIBILITY_FIXER_VERSION": "v1.2.3"}):
            version = get_app_version()
            assert version == "v1.2.3"

    def test_version_from_git(self):
        """Test git fallback when env var not set."""
        with patch.dict(os.environ, {}, clear=True):
            with patch("subprocess.run") as mock_run:
                mock_run.return_value = MagicMock(
                    returncode=0,
                    stdout="abc1234\n"
                )
                version = get_app_version()
                assert version == "abc1234"

    def test_version_unknown_fallback(self):
        """Test fallback to 'unknown' when git fails."""
        with patch.dict(os.environ, {}, clear=True):
            with patch("subprocess.run") as mock_run:
                mock_run.side_effect = Exception("Git not found")
                version = get_app_version()
                assert version == "unknown"


class TestGetDebugFooter:
    """Tests for get_debug_footer function."""

    def test_footer_basic_format(self):
        """Test basic footer format."""
        with patch("app.comment_poster.get_app_version", return_value="abc123"):
            footer = get_debug_footer()
            assert "---" in footer
            assert "_debug:" in footer
            assert "accessibility-fixer@abc123" in footer

    def test_footer_with_reviewer_config(self):
        """Test footer includes reviewer config."""
        with patch("app.comment_poster.get_app_version", return_value="abc123"):
            config = {
                "model": "gpt-5.2",
                "base_url": "https://example.com/api",
                "files_per_batch": 3,
                "max_diff_chars": 200000,
            }
            footer = get_debug_footer(config)
            
            assert "accessibility-fixer@abc123" in footer
            assert "model=gpt-5.2" in footer
            assert "provider=example.com" in footer
            assert "files_per_batch=3" in footer
            assert "max_diff_chars=200000" in footer

    def test_footer_with_sarif_enabled(self):
        """Test footer includes SARIF status."""
        with patch("app.comment_poster.get_app_version", return_value="abc123"):
            with patch.dict(os.environ, {"OUTPUT_SARIF": "1"}):
                config = {"model": "gpt-5.2"}
                footer = get_debug_footer(config)
                assert "sarif=enabled" in footer

    def test_footer_without_sarif(self):
        """Test footer doesn't include SARIF when disabled."""
        with patch("app.comment_poster.get_app_version", return_value="abc123"):
            with patch.dict(os.environ, {}, clear=True):
                config = {"model": "gpt-5.2"}
                footer = get_debug_footer(config)
                assert "sarif=enabled" not in footer


class TestCommentPosterDebugFooter:
    """Tests for CommentPoster debug footer integration."""

    def test_review_summary_without_debug_stamp(self):
        """Test that review summary doesn't include debug footer by default."""
        with patch.dict(os.environ, {}, clear=True):
            poster = CommentPoster()
            summary = poster._format_review_summary({"Critical": 2, "High": 1})
            
            assert "# Accessibility Review Summary" in summary
            assert "_debug:" not in summary
            # The main footer should still be present
            assert "🤖 Automated by [accessibility-fixer]" in summary

    def test_review_summary_with_debug_stamp_enabled(self):
        """Test that review summary includes debug footer when enabled."""
        with patch.dict(os.environ, {"DEBUG_REVIEW_STAMP": "1"}):
            with patch("app.comment_poster.get_app_version", return_value="abc123"):
                config = {
                    "model": "gpt-5.2",
                    "files_per_batch": 1,
                    "max_diff_chars": 180000,
                }
                poster = CommentPoster(reviewer_config=config)
                summary = poster._format_review_summary({"Medium": 3})
                
                assert "# Accessibility Review Summary" in summary
                assert "---" in summary
                assert "_debug:" in summary
                assert "accessibility-fixer@abc123" in summary
                assert "model=gpt-5.2" in summary
                assert "files_per_batch=1" in summary

    def test_review_summary_debug_stamp_various_flags(self):
        """Test different DEBUG_REVIEW_STAMP values."""
        config = {"model": "test-model"}
        
        # Test "true"
        with patch.dict(os.environ, {"DEBUG_REVIEW_STAMP": "true"}):
            with patch("app.comment_poster.get_app_version", return_value="abc123"):
                poster = CommentPoster(reviewer_config=config)
                summary = poster._format_review_summary({"Low": 1})
                assert "_debug:" in summary
        
        # Test "yes"
        with patch.dict(os.environ, {"DEBUG_REVIEW_STAMP": "yes"}):
            with patch("app.comment_poster.get_app_version", return_value="abc123"):
                poster = CommentPoster(reviewer_config=config)
                summary = poster._format_review_summary({"Low": 1})
                assert "_debug:" in summary
        
        # Test "0" (disabled)
        with patch.dict(os.environ, {"DEBUG_REVIEW_STAMP": "0"}):
            poster = CommentPoster(reviewer_config=config)
            summary = poster._format_review_summary({"Low": 1})
            assert "_debug:" not in summary

    def test_review_summary_no_issues_with_debug(self):
        """Test debug footer appears even when no issues found."""
        with patch.dict(os.environ, {"DEBUG_REVIEW_STAMP": "1"}):
            with patch("app.comment_poster.get_app_version", return_value="test123"):
                config = {"model": "gpt-5.2"}
                poster = CommentPoster(reviewer_config=config)
                summary = poster._format_review_summary({})
                
                assert "✅ No accessibility issues found" in summary
                assert "_debug:" in summary
                assert "accessibility-fixer@test123" in summary
                assert "model=gpt-5.2" in summary


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
