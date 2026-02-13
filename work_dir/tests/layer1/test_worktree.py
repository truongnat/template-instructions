"""
Tests for .agent/workflows/worktree.md
Worktrunk workflow validation tests
"""

import pytest
from pathlib import Path

WORKTREE_WORKFLOW = Path("agentic_sdlc/defaults/workflows/worktree.md")


class TestWorktreeWorkflowExists:
    """Tests for worktree workflow file existence and structure"""

    def test_worktree_workflow_exists(self):
        """Test that worktree.md workflow file exists"""
        assert WORKTREE_WORKFLOW.exists(), "worktree.md workflow should exist"
        assert WORKTREE_WORKFLOW.is_file(), "worktree.md should be a file"

    def test_worktree_workflow_not_empty(self):
        """Test that worktree.md is not empty"""
        content = WORKTREE_WORKFLOW.read_text(encoding="utf-8")
        assert len(content) > 100, "worktree.md should have substantial content"


class TestWorktreeWorkflowFrontmatter:
    """Tests for worktree workflow YAML frontmatter"""

    def test_has_valid_frontmatter(self):
        """Test that worktree.md has valid YAML frontmatter"""
        import yaml
        
        content = WORKTREE_WORKFLOW.read_text(encoding="utf-8")
        assert content.startswith("---"), "Workflow should start with frontmatter"
        
        # Extract frontmatter
        parts = content.split("---", 2)
        assert len(parts) >= 3, "Should have frontmatter delimiters"
        
        frontmatter = yaml.safe_load(parts[1])
        assert frontmatter is not None, "Frontmatter should be valid YAML"

    def test_has_description(self):
        """Test that worktree.md has description in frontmatter"""
        import yaml
        
        content = WORKTREE_WORKFLOW.read_text(encoding="utf-8")
        _, frontmatter_str, _ = content.split("---", 2)
        frontmatter = yaml.safe_load(frontmatter_str)
        
        assert "description" in frontmatter, "Should have description field"
        assert len(frontmatter["description"]) > 10, "Description should be meaningful"


class TestWorktreeWorkflowContent:
    """Tests for worktree workflow content structure"""

    def test_has_prerequisites_section(self):
        """Test that workflow has prerequisites section"""
        content = WORKTREE_WORKFLOW.read_text(encoding="utf-8")
        assert "## Prerequisites" in content, "Should have Prerequisites section"

    def test_has_installation_instructions(self):
        """Test that workflow has installation instructions"""
        content = WORKTREE_WORKFLOW.read_text(encoding="utf-8")
        assert "cargo install worktrunk" in content, "Should have Cargo installation"
        # Homebrew is optional (macOS/Linux only)

    def test_has_core_commands_section(self):
        """Test that workflow documents core commands"""
        content = WORKTREE_WORKFLOW.read_text(encoding="utf-8")
        assert "## Core Commands" in content, "Should have Core Commands section"

    def test_has_workflow_steps(self):
        """Test that workflow has structured steps"""
        content = WORKTREE_WORKFLOW.read_text(encoding="utf-8")
        assert "## Workflow Steps" in content, "Should have Workflow Steps section"

    def test_documents_key_commands(self):
        """Test that key wt commands are documented"""
        content = WORKTREE_WORKFLOW.read_text(encoding="utf-8")
        
        key_commands = [
            "wt switch",
            "wt list",
            "wt merge",
            "wt remove",
        ]
        
        for cmd in key_commands:
            assert cmd in content, f"Should document '{cmd}' command"

    def test_has_troubleshooting_section(self):
        """Test that workflow has troubleshooting section"""
        content = WORKTREE_WORKFLOW.read_text(encoding="utf-8")
        assert "## Troubleshooting" in content, "Should have Troubleshooting section"

    def test_has_windows_compatibility_notes(self):
        """Test that workflow addresses Windows compatibility"""
        content = WORKTREE_WORKFLOW.read_text(encoding="utf-8")
        assert "Windows" in content, "Should mention Windows compatibility"
        assert "Git Bash" in content, "Should mention Git Bash for Windows"


class TestWorktreeWorkflowIntegration:
    """Tests for worktree workflow integration with other workflows"""

    def test_references_dev_role(self):
        """Test that workflow references @DEV role"""
        content = WORKTREE_WORKFLOW.read_text(encoding="utf-8")
        assert "@DEV" in content, "Should reference @DEV role"

    def test_has_tags(self):
        """Test that workflow has proper tags at the end"""
        content = WORKTREE_WORKFLOW.read_text(encoding="utf-8")
        assert "#worktree" in content, "Should have #worktree tag"
        assert "#git" in content, "Should have #git tag"

    def test_has_references_section(self):
        """Test that workflow has external references"""
        content = WORKTREE_WORKFLOW.read_text(encoding="utf-8")
        assert "worktrunk.dev" in content, "Should reference worktrunk.dev"
        assert "github.com/max-sixty/worktrunk" in content, "Should reference GitHub repo"
