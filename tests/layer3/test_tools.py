
import pytest
import sys
from pathlib import Path

# imports should work via conftest path setup

def test_release_tool_import():
    try:
        from agentic_sdlc.infrastructure.release import release
        assert release is not None
    except ImportError as e:
        pytest.fail(f"Failed to import release tool: {e}")

def test_semver_parsing():
    from agentic_sdlc.infrastructure.release.release import ReleaseManager
    rm = ReleaseManager()
    major, minor, patch = rm.parse_version("1.2.3")
    assert major == 1
    assert minor == 2
    assert patch == 3

def test_version_bump_logic():
    from agentic_sdlc.infrastructure.release.release import ReleaseManager
    rm = ReleaseManager()
    assert rm.bump_version("patch", "1.0.0") == "1.0.1"
    assert rm.bump_version("minor", "1.0.0") == "1.1.0"
    assert rm.bump_version("major", "1.0.0") == "2.0.0"
