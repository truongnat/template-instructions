"""
Tests for tools/utils/common.py
"""

import pytest
from pathlib import Path


class TestProjectRoot:
    """Tests for get_project_root function."""

    def test_returns_path(self, project_root):
        """Should return a Path object."""
        from utils.common import get_project_root
        result = get_project_root()
        assert isinstance(result, Path)

    def test_agent_dir_exists(self, project_root):
        """Project root should contain .agent directory."""
        from utils.common import get_project_root
        root = get_project_root()
        assert (root / ".agent").exists()


class TestFileOperations:
    """Tests for file utility functions."""

    def test_ensure_dir_creates_directory(self, tmp_path):
        """ensure_dir should create directory if not exists."""
        from utils.common import ensure_dir
        test_dir = tmp_path / "test_dir"
        result = ensure_dir(test_dir)
        assert test_dir.exists()
        assert result == test_dir

    def test_file_exists_true(self, project_root):
        """file_exists should return True for existing file."""
        from utils.common import file_exists
        assert file_exists(project_root / "package.json")

    def test_file_exists_false(self, project_root):
        """file_exists should return False for non-existing file."""
        from utils.common import file_exists
        assert not file_exists(project_root / "nonexistent.file")


class TestStringUtilities:
    """Tests for string utility functions."""

    def test_truncate_short_string(self):
        """Short strings should not be truncated."""
        from utils.common import truncate_string
        result = truncate_string("hello", 80)
        assert result == "hello"

    def test_truncate_long_string(self):
        """Long strings should be truncated with ellipsis."""
        from utils.common import truncate_string
        long_string = "a" * 100
        result = truncate_string(long_string, 20)
        assert len(result) == 20
        assert result.endswith("...")

    def test_format_duration_seconds(self):
        """Seconds should format as Ns."""
        from utils.common import format_duration
        assert format_duration(30) == "30s"

    def test_format_duration_minutes(self):
        """60+ seconds should format as Nm."""
        from utils.common import format_duration
        assert format_duration(120) == "2m"

    def test_format_duration_hours(self):
        """3600+ seconds should format as Nh Nm."""
        from utils.common import format_duration
        assert format_duration(3660) == "1h 1m"
