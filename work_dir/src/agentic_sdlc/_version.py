"""Version information for the Agentic SDLC SDK.

This module provides the version string for the SDK. The version is the single
source of truth and is used by pyproject.toml and other tools.
"""

from pathlib import Path
from typing import Optional


def _read_version_from_file() -> Optional[str]:
    """Read version from VERSION file if it exists.

    Looks for a VERSION file in the package root directory. This allows
    version to be managed separately from the code if needed.

    Returns:
        Version string if VERSION file exists and is readable, None otherwise.
    """
    version_file = Path(__file__).parent.parent.parent / "VERSION"
    if version_file.exists():
        try:
            return version_file.read_text(encoding="utf-8").strip()
        except (IOError, OSError):
            return None
    return None


# Try to read from VERSION file first, fall back to hardcoded version
__version__ = _read_version_from_file() or "3.0.0"
