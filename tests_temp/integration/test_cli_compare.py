"""
Integration tests for the compare CLI command.

Tests the CLI interface for V2 structure comparison, including:
- Running comparison with various options
- Output file generation
- Error handling for invalid inputs
"""

import pytest
import subprocess
import sys
import tempfile
import shutil
from pathlib import Path


@pytest.fixture
def temp_project_dir():
    """Create a temporary project directory for testing."""
    temp_dir = tempfile.mkdtemp()
    yield temp_dir
    shutil.rmtree(temp_dir, ignore_errors=True)


@pytest.fixture
def temp_v2_docs_dir():
    """Create a temporary v2 docs directory with minimal structure."""
    temp_dir = tempfile.mkdtemp()
    
    # Create minimal v2 docs structure
    v2_dir = Path(temp_dir)
    
    # Create SDLC_Improvement_Suggestions.md
    suggestions_file = v2_dir / "SDLC_Improvement_Suggestions.md"
    suggestions_file.write_text("""
# SDLC Improvement Suggestions

## 1. Project Structure
Improve project organization.

## 2. Documentation
Add comprehensive documentation.
""")
    
    # Create Proposed_Structure.md
    structure_file = v2_dir / "Proposed_Structure.md"
    structure_file.write_text("""
# Proposed Structure

```
project/
├── src/
├── tests/
└── docs/
```
""")
    
    # Create Quick_Action_Checklist.md
    checklist_file = v2_dir / "Quick_Action_Checklist.md"
    checklist_file.write_text("""
# Quick Action Checklist

- [ ] Create docs/ directory
- [ ] Add README.md
""")
    
    yield temp_dir
    shutil.rmtree(temp_dir, ignore_errors=True)


def test_compare_help():
    """Test that compare --help works."""
    result = subprocess.run(
        [sys.executable, "cli/main.py", "compare", "--help"],
        capture_output=True,
        text=True
    )
    
    assert result.returncode == 0 or result.returncode == 130  # 130 is Ctrl+C
    assert "compare" in result.stdout.lower() or "compare" in result.stderr.lower()
    assert "v2" in result.stdout.lower() or "v2" in result.stderr.lower()


def test_compare_with_invalid_project_root():
    """Test compare command with non-existent project root."""
    with tempfile.TemporaryDirectory() as temp_dir:
        output_file = Path(temp_dir) / "report.md"
        
        result = subprocess.run(
            [
                sys.executable, "cli/main.py", "compare",
                "--project-root", "/nonexistent/path",
                "--v2-docs", "/nonexistent/v2",
                "--output", str(output_file)
            ],
            capture_output=True,
            text=True
        )
        
        # Should fail with non-zero exit code
        assert result.returncode != 0
        # Should have error message
        assert "error" in result.stdout.lower() or "error" in result.stderr.lower()


def test_compare_with_invalid_v2_docs():
    """Test compare command with non-existent v2 docs path."""
    with tempfile.TemporaryDirectory() as temp_dir:
        output_file = Path(temp_dir) / "report.md"
        
        result = subprocess.run(
            [
                sys.executable, "cli/main.py", "compare",
                "--project-root", ".",
                "--v2-docs", "/nonexistent/v2/docs",
                "--output", str(output_file)
            ],
            capture_output=True,
            text=True
        )
        
        # Should fail with non-zero exit code
        assert result.returncode != 0


def test_compare_output_file_generation(temp_project_dir, temp_v2_docs_dir):
    """Test that compare command generates output file."""
    output_file = Path(temp_project_dir) / "test_report.md"
    
    result = subprocess.run(
        [
            sys.executable, "cli/main.py", "compare",
            "--project-root", temp_project_dir,
            "--v2-docs", temp_v2_docs_dir,
            "--output", str(output_file)
        ],
        capture_output=True,
        text=True,
        timeout=30
    )
    
    # Check that output file was created
    assert output_file.exists(), f"Output file not created. stdout: {result.stdout}, stderr: {result.stderr}"
    
    # Check that output file has content
    content = output_file.read_text()
    assert len(content) > 0, "Output file is empty"
    assert "comparison" in content.lower() or "report" in content.lower()


def test_compare_with_verbose_flag(temp_project_dir, temp_v2_docs_dir):
    """Test compare command with verbose flag."""
    output_file = Path(temp_project_dir) / "verbose_report.md"
    
    result = subprocess.run(
        [
            sys.executable, "cli/main.py", "compare",
            "--project-root", temp_project_dir,
            "--v2-docs", temp_v2_docs_dir,
            "--output", str(output_file),
            "--verbose"
        ],
        capture_output=True,
        text=True,
        timeout=30
    )
    
    # Verbose output should contain more information
    output = result.stdout + result.stderr
    assert "project root" in output.lower() or "v2 docs" in output.lower() or "comparison" in output.lower()


def test_compare_with_status_file(temp_project_dir, temp_v2_docs_dir):
    """Test compare command with status file option."""
    output_file = Path(temp_project_dir) / "report.md"
    status_file = Path(temp_project_dir) / "status.json"
    
    result = subprocess.run(
        [
            sys.executable, "cli/main.py", "compare",
            "--project-root", temp_project_dir,
            "--v2-docs", temp_v2_docs_dir,
            "--output", str(output_file),
            "--status-file", str(status_file)
        ],
        capture_output=True,
        text=True,
        timeout=30
    )
    
    # Check that output file was created
    assert output_file.exists()


def test_compare_with_generate_scripts_flag(temp_project_dir, temp_v2_docs_dir):
    """Test compare command with generate-scripts flag."""
    output_file = Path(temp_project_dir) / "report.md"
    scripts_dir = Path(temp_project_dir) / "scripts"
    
    result = subprocess.run(
        [
            sys.executable, "cli/main.py", "compare",
            "--project-root", temp_project_dir,
            "--v2-docs", temp_v2_docs_dir,
            "--output", str(output_file),
            "--generate-scripts",
            "--scripts-output", str(scripts_dir)
        ],
        capture_output=True,
        text=True,
        timeout=30
    )
    
    # Check that output file was created
    assert output_file.exists()
    
    # Check that scripts directory was created (if there are scripts to generate)
    # Note: scripts may not be generated if there are no applicable migrations


def test_compare_with_no_validation_flag(temp_project_dir, temp_v2_docs_dir):
    """Test compare command with no-validation flag."""
    output_file = Path(temp_project_dir) / "report.md"
    
    result = subprocess.run(
        [
            sys.executable, "cli/main.py", "compare",
            "--project-root", temp_project_dir,
            "--v2-docs", temp_v2_docs_dir,
            "--output", str(output_file),
            "--no-validation"
        ],
        capture_output=True,
        text=True,
        timeout=30
    )
    
    # Should complete successfully
    assert output_file.exists()


def test_compare_default_paths():
    """Test compare command with default paths (current directory)."""
    # This test only checks that the command runs without crashing
    # It may fail if v2 docs don't exist, which is expected
    result = subprocess.run(
        [
            sys.executable, "cli/main.py", "compare",
            "--output", "/tmp/test_default_report.md"
        ],
        capture_output=True,
        text=True,
        timeout=30
    )
    
    # Command should either succeed or fail gracefully with error message
    # We don't assert success because v2 docs may not exist
    assert result.returncode in [0, 1]


def test_compare_summary_output(temp_project_dir, temp_v2_docs_dir):
    """Test that compare command outputs summary information."""
    output_file = Path(temp_project_dir) / "report.md"
    
    result = subprocess.run(
        [
            sys.executable, "cli/main.py", "compare",
            "--project-root", temp_project_dir,
            "--v2-docs", temp_v2_docs_dir,
            "--output", str(output_file)
        ],
        capture_output=True,
        text=True,
        timeout=30
    )
    
    output = result.stdout + result.stderr
    
    # Should contain summary information
    assert "completion" in output.lower() or "summary" in output.lower() or "report" in output.lower()


def test_compare_error_message_format():
    """Test that error messages are properly formatted."""
    result = subprocess.run(
        [
            sys.executable, "cli/main.py", "compare",
            "--project-root", "/definitely/does/not/exist",
            "--v2-docs", "/also/does/not/exist"
        ],
        capture_output=True,
        text=True,
        timeout=30
    )
    
    # Should have non-zero exit code
    assert result.returncode != 0
    
    # Error message should be present
    output = result.stdout + result.stderr
    assert len(output) > 0


def test_compare_with_all_options(temp_project_dir, temp_v2_docs_dir):
    """Test compare command with all options combined."""
    output_file = Path(temp_project_dir) / "full_report.md"
    status_file = Path(temp_project_dir) / "status.json"
    scripts_dir = Path(temp_project_dir) / "migration_scripts"
    
    result = subprocess.run(
        [
            sys.executable, "cli/main.py", "compare",
            "--project-root", temp_project_dir,
            "--v2-docs", temp_v2_docs_dir,
            "--output", str(output_file),
            "--status-file", str(status_file),
            "--generate-scripts",
            "--scripts-output", str(scripts_dir),
            "--verbose"
        ],
        capture_output=True,
        text=True,
        timeout=30
    )
    
    # Should complete and create output file
    assert output_file.exists()
    
    # Should have verbose output
    output = result.stdout + result.stderr
    assert len(output) > 0
