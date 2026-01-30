
import pytest
import os
from pathlib import Path

SKILLS_DIR = Path(".agent/skills")

def test_skills_directory_exists():
    assert SKILLS_DIR.exists()
    assert SKILLS_DIR.is_dir()

def get_skill_files():
    skill_files = []
    for skill_dir in SKILLS_DIR.iterdir():
        if skill_dir.is_dir():
            skill_file = skill_dir / "SKILL.md"
            if skill_file.exists():
                skill_files.append(skill_file)
    return skill_files

@pytest.mark.parametrize("skill_file", get_skill_files())
def test_skill_format(skill_file):
    content = skill_file.read_text(encoding="utf-8")
    assert "name:" in content, f"{skill_file.name} missing name"
    assert "description:" in content, f"{skill_file.name} missing description"

@pytest.mark.parametrize("skill_file", get_skill_files())
def test_skill_tags(skill_file):
    content = skill_file.read_text(encoding="utf-8")
    assert "#" in content, f"{skill_file.name} missing tags"
