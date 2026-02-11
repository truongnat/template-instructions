"""
Unit tests for version management module.
"""

import pytest
from pathlib import Path
from agentic_sdlc.version import read_version, get_version_info, __version__


def test_read_version():
    """Test that read_version returns a valid version string."""
    version = read_version()
    
    # Should not be empty
    assert version
    
    # Should contain at least one dot (semantic versioning)
    assert "." in version
    
    # Should match the module-level __version__
    assert version == __version__


def test_get_version_info():
    """Test that get_version_info returns correct version components."""
    info = get_version_info()
    
    # Should have all required keys
    assert "version" in info
    assert "major" in info
    assert "minor" in info
    assert "patch" in info
    assert "prerelease" in info
    
    # Version should match read_version
    assert info["version"] == read_version()
    
    # If version is not "unknown", should have numeric components
    if info["version"] != "unknown":
        assert isinstance(info["major"], int)
        assert isinstance(info["minor"], int)
        assert isinstance(info["patch"], int)
        assert info["major"] >= 0
        assert info["minor"] >= 0
        assert info["patch"] >= 0


def test_version_format():
    """Test that version follows semantic versioning format."""
    version = read_version()
    
    if version != "unknown":
        # Split by dash to separate version from prerelease
        parts = version.split("-", 1)
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
    from agentic_sdlc.version import __version__ as version_module_version
    
    # Both should return the same version
    assert init_version == version_module_version


def test_prerelease_parsing():
    """Test that prerelease versions are parsed correctly."""
    # This test uses the actual version, but documents expected behavior
    info = get_version_info()
    
    # If version contains a dash, prerelease should be populated
    if "-" in info["version"]:
        assert info["prerelease"] is not None
        assert isinstance(info["prerelease"], str)
    else:
        # Stable release should have no prerelease
        assert info["prerelease"] is None


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
