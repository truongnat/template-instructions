"""Unit tests for version management.

Tests the version string and version reading functionality.
"""

import re
from pathlib import Path

import pytest

from agentic_sdlc import __version__


class TestVersionManagement:
    """Tests for version management."""

    def test_version_is_string(self) -> None:
        """Test that __version__ is a string."""
        assert isinstance(__version__, str)

    def test_version_is_not_empty(self) -> None:
        """Test that __version__ is not empty."""
        assert len(__version__) > 0

    def test_version_matches_semver_format(self) -> None:
        """Test that __version__ matches semantic versioning format.

        Semantic versioning format: MAJOR.MINOR.PATCH[-prerelease][+build]
        """
        # Pattern for semantic versioning
        semver_pattern = r"^\d+\.\d+\.\d+(-[a-zA-Z0-9]+(\.[a-zA-Z0-9]+)*)?(\+[a-zA-Z0-9]+(\.[a-zA-Z0-9]+)*)?$"
        assert re.match(
            semver_pattern, __version__
        ), f"Version {__version__} does not match semantic versioning format"

    def test_version_accessible_from_public_api(self) -> None:
        """Test that version is accessible from the public API."""
        # This test verifies that __version__ is properly exported
        from agentic_sdlc import __version__ as version

        assert version == __version__

    def test_version_is_in_all_exports(self) -> None:
        """Test that __version__ is in the public API __all__ list."""
        from agentic_sdlc import __all__

        assert "__version__" in __all__

    def test_version_default_value(self) -> None:
        """Test that version has a reasonable default value."""
        # The version should have valid major, minor, and patch components
        parts = __version__.split(".")[:3]
        assert len(parts) >= 3
        major, minor, patch = parts
        assert int(major) >= 0
        assert int(minor) >= 0
        assert int(patch) >= 0

    def test_version_string_representation(self) -> None:
        """Test that version can be used in string operations."""
        version_str = f"agentic-sdlc=={__version__}"
        assert "agentic-sdlc==" in version_str
        assert __version__ in version_str
