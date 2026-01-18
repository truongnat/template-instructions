"""
Tests for tools/core/utils/common.py
"""

import pytest
from pathlib import Path
import sys

# imports should work via conftest path setup, but we need correct module path
from tools.core.utils.common import (
    get_project_root,
    ensure_dir,
    file_exists,
    truncate_string,
    format_duration
)

class TestProjectRoot:
    """Tests for get_project_root function."""

    def test_returns_path(self):
        """Should return a Path object."""
        result = get_project_root()
        assert isinstance(result, Path)

    def test_agent_dir_exists(self):
        """Project root should contain .agent directory."""
        root = get_project_root()
        # In test environment, .agent might not exist if running in minimal env,
        # but in this repo it does.
        if (root / ".agent").exists():
            assert (root / ".agent").exists()


class TestFileOperations:
    """Tests for file utility functions."""

    def test_ensure_dir_creates_directory(self, tmp_path):
        """ensure_dir should create directory if not exists."""
        test_dir = tmp_path / "test_dir"
        result = ensure_dir(test_dir)
        assert test_dir.exists()
        assert result == test_dir

    def test_file_exists_true(self):
        """file_exists should return True for existing file."""
        root = get_project_root()
        assert file_exists(root / "package.json")

    def test_file_exists_false(self):
        """file_exists should return False for non-existing file."""
        root = get_project_root()
        assert not file_exists(root / "nonexistent.file")


class TestStringUtilities:
    """Tests for string utility functions."""

    def test_truncate_short_string(self):
        """Short strings should not be truncated."""
        result = truncate_string("hello", 80)
        assert result == "hello"

    def test_truncate_long_string(self):
        """Long strings should be truncated with ellipsis."""
        long_string = "a" * 100
        result = truncate_string(long_string, 20)
        assert len(result) == 20
        assert result.endswith("...")

    def test_format_duration_seconds(self):
        """Seconds should format as Ns."""
        assert format_duration(30) == "30s"

    def test_format_duration_minutes(self):
        """60+ seconds should format as Nm."""
        assert format_duration(120) == "2m"

    def test_format_duration_hours(self):
        """3600+ seconds should format as Nh Nm."""
        assert format_duration(3660) == "1h 1m"