#!/usr/bin/env python3
"""
Version Bump Script

Automatically bumps version based on conventional commit messages.
Supports semantic versioning (MAJOR.MINOR.PATCH).

Commit message format:
- feat: ... → minor bump (3.0.0 → 3.1.0)
- fix: ... → patch bump (3.0.0 → 3.0.1)
- BREAKING CHANGE: ... → major bump (3.0.0 → 4.0.0)
"""

import re
import sys
from pathlib import Path
from typing import Tuple


def parse_version(version_str: str) -> Tuple[int, int, int]:
    """Parse version string into (major, minor, patch) tuple."""
    match = re.match(r"(\d+)\.(\d+)\.(\d+)", version_str.strip())
    if not match:
        raise ValueError(f"Invalid version format: {version_str}")
    return int(match.group(1)), int(match.group(2)), int(match.group(3))


def format_version(major: int, minor: int, patch: int) -> str:
    """Format version tuple into string."""
    return f"{major}.{minor}.{patch}"


def get_bump_type(commit_msg: str) -> str:
    """Determine version bump type from commit message."""
    if "BREAKING CHANGE:" in commit_msg or commit_msg.startswith("!"):
        return "major"
    elif commit_msg.startswith("feat:") or commit_msg.startswith("feat("):
        return "minor"
    elif commit_msg.startswith("fix:") or commit_msg.startswith("fix("):
        return "patch"
    else:
        return "none"


def bump_version(version_str: str, bump_type: str) -> str:
    """Bump version based on type."""
    major, minor, patch = parse_version(version_str)
    
    if bump_type == "major":
        major += 1
        minor = 0
        patch = 0
    elif bump_type == "minor":
        minor += 1
        patch = 0
    elif bump_type == "patch":
        patch += 1
    
    return format_version(major, minor, patch)


def update_version_file(project_root: Path, new_version: str) -> None:
    """Update VERSION file."""
    version_file = project_root / "VERSION"
    version_file.write_text(new_version + "\n")
    print(f"✓ Updated VERSION: {new_version}")


def update_pyproject_toml(project_root: Path, new_version: str) -> None:
    """Update version in pyproject.toml."""
    pyproject_file = project_root / "pyproject.toml"
    content = pyproject_file.read_text()
    
    # Replace version line
    updated_content = re.sub(
        r'version = "[^"]+"',
        f'version = "{new_version}"',
        content,
        count=1
    )
    
    pyproject_file.write_text(updated_content)
    print(f"✓ Updated pyproject.toml: {new_version}")


def main():
    """Main entry point."""
    if len(sys.argv) < 2:
        print("Usage: version_bump.py <commit_message>")
        sys.exit(1)
    
    commit_msg = sys.argv[1]
    
    # Find project root
    script_dir = Path(__file__).parent
    project_root = script_dir.parent
    
    # Read current version
    version_file = project_root / "VERSION"
    if not version_file.exists():
        print("ERROR: VERSION file not found")
        sys.exit(1)
    
    current_version = version_file.read_text().strip()
    
    # Determine bump type
    bump_type = get_bump_type(commit_msg)
    
    if bump_type == "none":
        print(f"ℹ No version bump needed for commit: {commit_msg[:50]}...")
        sys.exit(0)
    
    # Bump version
    new_version = bump_version(current_version, bump_type)
    
    print(f"Version bump: {current_version} → {new_version} ({bump_type})")
    
    # Update files
    update_version_file(project_root, new_version)
    update_pyproject_toml(project_root, new_version)
    
    print(f"✓ Version bumped successfully!")
    print(f"  Tag: v{new_version}")


if __name__ == "__main__":
    main()
