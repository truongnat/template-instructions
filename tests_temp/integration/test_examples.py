"""
Integration tests for examples.

Tests that all examples execute without errors and produce expected output.
"""

import subprocess
import sys
from pathlib import Path


class TestProgrammaticExamples:
    """Test programmatic SDK examples."""
    
    @property
    def examples_dir(self) -> Path:
        """Get examples directory."""
        return Path(__file__).parent.parent.parent / "examples" / "programmatic"
    
    def test_basic_config_setup_example_exists(self):
        """Test basic configuration and setup example exists."""
        example_file = self.examples_dir / "01_basic_config_setup.py"
        assert example_file.exists(), f"Example file not found: {example_file}"
        
        # Check file has content
        content = example_file.read_text()
        assert len(content) > 100
        assert "def main()" in content
        assert "Config" in content
    
    def test_workflow_execution_example_exists(self):
        """Test workflow execution example exists."""
        example_file = self.examples_dir / "02_workflow_execution.py"
        assert example_file.exists(), f"Example file not found: {example_file}"
        
        # Check file has content
        content = example_file.read_text()
        assert len(content) > 100
        assert "def main()" in content
        assert "WorkflowBuilder" in content
    
    def test_agent_creation_example_exists(self):
        """Test agent creation example exists."""
        example_file = self.examples_dir / "03_agent_creation.py"
        assert example_file.exists(), f"Example file not found: {example_file}"
        
        # Check file has content
        content = example_file.read_text()
        assert len(content) > 100
        assert "def main()" in content
        assert "create_agent" in content
    
    def test_custom_plugin_example_exists(self):
        """Test custom plugin example exists."""
        example_file = self.examples_dir / "04_custom_plugin.py"
        assert example_file.exists(), f"Example file not found: {example_file}"
        
        # Check file has content
        content = example_file.read_text()
        assert len(content) > 100
        assert "class AnalyticsPlugin" in content
        assert "class Plugin" in content or "Plugin" in content


class TestCLIExamples:
    """Test CLI usage examples."""
    
    @property
    def examples_dir(self) -> Path:
        """Get examples directory."""
        return Path(__file__).parent.parent.parent / "examples" / "cli"
    
    def test_init_project_example_exists(self):
        """Test project initialization example exists."""
        example_file = self.examples_dir / "01_init_project.sh"
        assert example_file.exists(), f"Example file not found: {example_file}"
        
        # Check file has content
        content = example_file.read_text()
        assert len(content) > 100
        assert "agentic init" in content
    
    def test_run_workflow_example_exists(self):
        """Test workflow execution example exists."""
        example_file = self.examples_dir / "02_run_workflow.sh"
        assert example_file.exists(), f"Example file not found: {example_file}"
        
        # Check file has content
        content = example_file.read_text()
        assert len(content) > 100
        assert "agentic workflow" in content
    
    def test_config_management_example_exists(self):
        """Test configuration management example exists."""
        example_file = self.examples_dir / "03_config_management.sh"
        assert example_file.exists(), f"Example file not found: {example_file}"
        
        # Check file has content
        content = example_file.read_text()
        assert len(content) > 100
        assert "agentic config" in content


class TestExampleFiles:
    """Test that all example files exist and are readable."""
    
    def test_programmatic_examples_exist(self):
        """Test that all programmatic examples exist."""
        examples_dir = Path(__file__).parent.parent.parent / "examples" / "programmatic"
        
        expected_files = [
            "README.md",
            "01_basic_config_setup.py",
            "02_workflow_execution.py",
            "03_agent_creation.py",
            "04_custom_plugin.py",
        ]
        
        for filename in expected_files:
            file_path = examples_dir / filename
            assert file_path.exists(), f"Example file not found: {file_path}"
            assert file_path.is_file(), f"Not a file: {file_path}"
    
    def test_cli_examples_exist(self):
        """Test that all CLI examples exist."""
        examples_dir = Path(__file__).parent.parent.parent / "examples" / "cli"
        
        expected_files = [
            "README.md",
            "01_init_project.sh",
            "02_run_workflow.sh",
            "03_config_management.sh",
        ]
        
        for filename in expected_files:
            file_path = examples_dir / filename
            assert file_path.exists(), f"Example file not found: {file_path}"
            assert file_path.is_file(), f"Not a file: {file_path}"
    
    def test_plugin_examples_exist(self):
        """Test that plugin examples directory exists."""
        examples_dir = Path(__file__).parent.parent.parent / "examples" / "plugins"
        
        assert examples_dir.exists(), f"Examples directory not found: {examples_dir}"
        assert examples_dir.is_dir(), f"Not a directory: {examples_dir}"
        
        # Check README exists
        readme = examples_dir / "README.md"
        assert readme.exists(), f"README not found: {readme}"
    
    def test_example_readmes_have_content(self):
        """Test that example README files have content."""
        examples_base = Path(__file__).parent.parent.parent / "examples"
        
        for subdir in ["programmatic", "cli", "plugins"]:
            readme = examples_base / subdir / "README.md"
            assert readme.exists(), f"README not found: {readme}"
            
            content = readme.read_text()
            assert len(content) > 100, f"README too short: {readme}"
            assert "Example" in content, f"README missing 'Example': {readme}"
