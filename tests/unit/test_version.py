"""
Unit tests for version management module.
"""

import pytest
from pathlib import Path


def test_version_module_importable():
    """Test that _version module is importable."""
    from agentic_sdlc._version import __version__
    assert __version__


def test_version_string_valid():
    """Test that __version__ returns a valid version string."""
    from agentic_sdlc._version import __version__
    
    # Should not be empty
    assert __version__
    
    # Should contain at least one dot (semantic versioning)
    assert "." in __version__


def test_version_format():
    """Test that version follows semantic versioning format."""
    from agentic_sdlc._version import __version__
    
    # Split by dash to separate version from prerelease
    parts = __version__.split("-", 1)
    version_core = parts[0]
    
    # Version core should have 2 or 3 parts (major.minor or major.minor.patch)
    version_parts = version_core.split(".")
    assert len(version_parts) >= 2
    assert len(version_parts) <= 3
    
    # All parts should be numeric
    for part in version_parts:
        assert part.isdigit(), f"Version part '{part}' is not numeric"


def test_version_file_exists():
    """Test that VERSION file exists at expected location."""
    version_file = Path(__file__).resolve().parent.parent.parent / "VERSION"
    assert version_file.exists(), "VERSION file should exist at project root"


def test_version_consistency():
    """Test that version is consistent across different access methods."""
    from agentic_sdlc import __version__ as init_version
    from agentic_sdlc._version import __version__ as version_module_version
    
    # Both should return the same version
    assert init_version == version_module_version


def test_prerelease_parsing():
    """Test that prerelease versions are parsed correctly."""
    from agentic_sdlc._version import __version__
    
    # If version contains a dash after the core, it has a prerelease part
    parts = __version__.split("-", 1)
    if len(parts) > 1:
        prerelease = parts[1]
        assert isinstance(prerelease, str)
        assert len(prerelease) > 0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
