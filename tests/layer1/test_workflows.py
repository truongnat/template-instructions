
import pytest
import yaml
from pathlib import Path

WORKFLOWS_DIR = Path(__file__).parent.parent / ".agent" / "workflows"

def test_workflows_directory_exists():
    assert WORKFLOWS_DIR.exists()
    assert WORKFLOWS_DIR.is_dir()

def test_workflow_frontmatter():
    for workflow_file in WORKFLOWS_DIR.glob("*.md"):
        content = workflow_file.read_text(encoding="utf-8")
        if content.startswith("---"):
            try:
                # Extract frontmatter
                _, frontmatter, _ = content.split("---", 2)
                data = yaml.safe_load(frontmatter)
                assert "description" in data, f"{workflow_file.name} missing description in frontmatter"
            except (ValueError, yaml.YAMLError):
                pytest.fail(f"{workflow_file.name} has invalid frontmatter format")

import re

# ... (rest of the file)

def test_workflow_steps():
    for workflow_file in WORKFLOWS_DIR.glob("*.md"):
        content = workflow_file.read_text(encoding="utf-8")
        # Heuristic: check for markdown headers as steps
        assert re.search(r'^##\s', content, re.MULTILINE), f"{workflow_file.name} appears to miss structured steps"
