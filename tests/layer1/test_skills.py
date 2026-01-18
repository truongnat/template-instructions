
import pytest
import os
from pathlib import Path

SKILLS_DIR = Path("agentic_sdlc/defaults/skills")

def test_skills_directory_exists():
    assert SKILLS_DIR.exists()
    assert SKILLS_DIR.is_dir()

def test_all_roles_exist():
    expected_roles = [
        "role-pm.md",
        "role-ba.md",
        "role-sa.md",
        "role-uiux.md",
        "role-seca.md",
        "role-tester.md",
        "role-dev.md",
        "role-devops.md",
        "role-orchestrator.md"
        # Add other roles as needed
    ]
    existing_files = [f.name for f in SKILLS_DIR.glob("*.md")]
    for role in expected_roles:
        assert role in existing_files, f"Missing role: {role}"

def test_skill_format():
    for skill_file in SKILLS_DIR.glob("*.md"):
        content = skill_file.read_text(encoding="utf-8")
        assert "# @ROLE" in content, f"{skill_file.name} missing @ROLE header"
        assert "## Identity" in content, f"{skill_file.name} missing Identity section"
        assert "## Commands" in content, f"{skill_file.name} missing Commands section"
        assert "## Integration" in content, f"{skill_file.name} missing Integration section"

def test_skill_tags():
    for skill_file in SKILLS_DIR.glob("*.md"):
        content = skill_file.read_text(encoding="utf-8")
        assert "#role-tag" in content or "#skills-enabled" in content, f"{skill_file.name} missing required tags"
