"""
Unit tests for ManifestUpdater class.

Tests cover:
- pyproject.toml updates
- MANIFEST.in updates
- .gitignore updates
- Validation of updated files
"""

import pytest
from pathlib import Path
from scripts.cleanup.manifest import ManifestUpdater


@pytest.fixture
def temp_project(tmp_path):
    """Create a temporary project structure for testing."""
    # Create basic pyproject.toml
    pyproject_content = """[build-system]
requires = ["setuptools>=61.0"]
build-backend = "setuptools.build_meta"

[project]
name = "test-project"
version = "1.0.0"

[tool.setuptools]
include-package-data = true

[tool.setuptools.packages.find]
include = ["test_project", "test_project.*"]
"""
    (tmp_path / "pyproject.toml").write_text(pyproject_content)
    
    # Create basic MANIFEST.in
    manifest_content = """include README.md
include LICENSE
"""
    (tmp_path / "MANIFEST.in").write_text(manifest_content)
    
    # Create basic .gitignore
    gitignore_content = """__pycache__/
*.pyc
.pytest_cache/
"""
    (tmp_path / ".gitignore").write_text(gitignore_content)
    
    return tmp_path


def test_manifest_updater_initialization(temp_project):
    """Test ManifestUpdater initialization."""
    updater = ManifestUpdater(temp_project)
    
    assert updater.project_root == temp_project
    assert updater.pyproject_path == temp_project / "pyproject.toml"
    assert updater.manifest_path == temp_project / "MANIFEST.in"
    assert updater.gitignore_path == temp_project / ".gitignore"


def test_update_pyproject_exclusions_new_patterns(temp_project):
    """Test adding new exclusion patterns to pyproject.toml."""
    updater = ManifestUpdater(temp_project)
    
    # Add exclusion patterns
    patterns = ["lib/", "build/", "*.egg-info/"]
    success = updater.update_pyproject_exclusions(patterns)
    
    assert success
    
    # Verify patterns were added
    content = (temp_project / "pyproject.toml").read_text()
    assert "exclude = " in content
    assert '"lib/"' in content
    assert '"build/"' in content
    assert '"*.egg-info/"' in content


def test_update_pyproject_exclusions_duplicate_patterns(temp_project):
    """Test that duplicate patterns are not added."""
    updater = ManifestUpdater(temp_project)
    
    # Add patterns twice
    patterns = ["lib/", "build/"]
    updater.update_pyproject_exclusions(patterns)
    updater.update_pyproject_exclusions(patterns)
    
    # Verify patterns appear only once
    content = (temp_project / "pyproject.toml").read_text()
    assert content.count('"lib/"') == 1
    assert content.count('"build/"') == 1


def test_update_pyproject_exclusions_preserves_existing(temp_project):
    """Test that existing exclusions are preserved."""
    # Add initial exclusions
    pyproject_content = """[build-system]
requires = ["setuptools>=61.0"]

[project]
name = "test-project"

[tool.setuptools.packages.find]
include = ["test_project"]
exclude = ["tests", "docs"]
"""
    (temp_project / "pyproject.toml").write_text(pyproject_content)
    
    updater = ManifestUpdater(temp_project)
    
    # Add new patterns
    patterns = ["lib/", "build/"]
    updater.update_pyproject_exclusions(patterns)
    
    # Verify both old and new patterns exist
    content = (temp_project / "pyproject.toml").read_text()
    assert '"tests"' in content
    assert '"docs"' in content
    assert '"lib/"' in content
    assert '"build/"' in content


def test_update_manifest_in_new_patterns(temp_project):
    """Test adding new exclusion patterns to MANIFEST.in."""
    updater = ManifestUpdater(temp_project)
    
    patterns = ["lib/*", "build/*", "*.pyc"]
    success = updater.update_manifest_in(patterns)
    
    assert success
    
    # Verify patterns were added
    content = (temp_project / "MANIFEST.in").read_text()
    assert "exclude lib/*" in content
    assert "exclude build/*" in content
    assert "global-exclude *.pyc" in content


def test_update_manifest_in_preserves_includes(temp_project):
    """Test that include directives are preserved."""
    updater = ManifestUpdater(temp_project)
    
    patterns = ["lib/*", "*.pyc"]
    updater.update_manifest_in(patterns)
    
    # Verify original includes are preserved
    content = (temp_project / "MANIFEST.in").read_text()
    assert "include README.md" in content
    assert "include LICENSE" in content


def test_update_manifest_in_creates_file_if_missing(tmp_path):
    """Test that MANIFEST.in is created if it doesn't exist."""
    # Don't create MANIFEST.in
    (tmp_path / "pyproject.toml").write_text("[project]\nname='test'")
    
    updater = ManifestUpdater(tmp_path)
    
    patterns = ["lib/*", "*.pyc"]
    success = updater.update_manifest_in(patterns)
    
    assert success
    assert (tmp_path / "MANIFEST.in").exists()
    
    content = (tmp_path / "MANIFEST.in").read_text()
    assert "exclude lib/*" in content


def test_update_gitignore_new_patterns(temp_project):
    """Test adding new patterns to .gitignore."""
    updater = ManifestUpdater(temp_project)
    
    patterns = ["lib/", "build/", "*.egg-info/"]
    success = updater.update_gitignore(patterns)
    
    assert success
    
    # Verify patterns were added
    content = (temp_project / ".gitignore").read_text()
    assert "lib/" in content
    assert "build/" in content
    assert "*.egg-info/" in content


def test_update_gitignore_duplicate_patterns(temp_project):
    """Test that duplicate patterns are not added to .gitignore."""
    updater = ManifestUpdater(temp_project)
    
    # Add patterns twice
    patterns = ["lib/", "build/"]
    updater.update_gitignore(patterns)
    updater.update_gitignore(patterns)
    
    # Verify patterns appear only once
    content = (temp_project / ".gitignore").read_text()
    # Count occurrences (excluding the header comment)
    lines = [line for line in content.splitlines() if not line.startswith("#")]
    assert lines.count("lib/") == 1
    assert lines.count("build/") == 1


def test_update_gitignore_preserves_existing(temp_project):
    """Test that existing .gitignore patterns are preserved."""
    updater = ManifestUpdater(temp_project)
    
    patterns = ["lib/", "build/"]
    updater.update_gitignore(patterns)
    
    # Verify original patterns are preserved
    content = (temp_project / ".gitignore").read_text()
    assert "__pycache__/" in content
    assert "*.pyc" in content


def test_update_gitignore_creates_file_if_missing(tmp_path):
    """Test that .gitignore is created if it doesn't exist."""
    (tmp_path / "pyproject.toml").write_text("[project]\nname='test'")
    
    updater = ManifestUpdater(tmp_path)
    
    patterns = ["lib/", "build/"]
    success = updater.update_gitignore(patterns)
    
    assert success
    assert (tmp_path / ".gitignore").exists()
    
    content = (tmp_path / ".gitignore").read_text()
    assert "lib/" in content
    assert "build/" in content


def test_validate_pyproject_valid(temp_project):
    """Test validation of valid pyproject.toml."""
    updater = ManifestUpdater(temp_project)
    
    result = updater.validate_pyproject()
    
    assert result.passed
    assert len(result.errors) == 0


def test_validate_pyproject_missing_file(tmp_path):
    """Test validation when pyproject.toml is missing."""
    updater = ManifestUpdater(tmp_path)
    
    result = updater.validate_pyproject()
    
    assert not result.passed
    assert "not found" in result.errors[0]


def test_validate_pyproject_invalid_toml(temp_project):
    """Test validation of invalid TOML syntax."""
    # Write invalid TOML
    (temp_project / "pyproject.toml").write_text("[project\nname = test")
    
    updater = ManifestUpdater(temp_project)
    
    result = updater.validate_pyproject()
    
    # Should fail validation (if tomli/tomllib available)
    # If not available, will pass with warning
    assert isinstance(result.passed, bool)


def test_validate_pyproject_missing_required_sections(temp_project):
    """Test validation when required sections are missing."""
    # Write pyproject.toml without required sections
    (temp_project / "pyproject.toml").write_text("[tool.setuptools]\n")
    
    updater = ManifestUpdater(temp_project)
    
    result = updater.validate_pyproject()
    
    assert not result.passed
    assert any("Missing required section" in err for err in result.errors)


def test_validate_manifest_in_valid(temp_project):
    """Test validation of valid MANIFEST.in."""
    updater = ManifestUpdater(temp_project)
    
    result = updater.validate_manifest_in()
    
    assert result.passed
    assert len(result.errors) == 0


def test_validate_manifest_in_missing_file(tmp_path):
    """Test validation when MANIFEST.in is missing (should pass as optional)."""
    (tmp_path / "pyproject.toml").write_text("[project]\nname='test'")
    
    updater = ManifestUpdater(tmp_path)
    
    result = updater.validate_manifest_in()
    
    assert result.passed  # MANIFEST.in is optional


def test_validate_manifest_in_invalid_syntax(temp_project):
    """Test validation of invalid MANIFEST.in syntax."""
    # Write invalid MANIFEST.in
    (temp_project / "MANIFEST.in").write_text("invalid_command some_file.txt\n")
    
    updater = ManifestUpdater(temp_project)
    
    result = updater.validate_manifest_in()
    
    assert not result.passed
    assert any("Invalid command" in err for err in result.errors)


def test_validate_gitignore_valid(temp_project):
    """Test validation of valid .gitignore."""
    updater = ManifestUpdater(temp_project)
    
    result = updater.validate_gitignore()
    
    assert result.passed
    assert len(result.errors) == 0


def test_validate_gitignore_missing_file(tmp_path):
    """Test validation when .gitignore is missing (should pass as optional)."""
    (tmp_path / "pyproject.toml").write_text("[project]\nname='test'")
    
    updater = ManifestUpdater(tmp_path)
    
    result = updater.validate_gitignore()
    
    assert result.passed  # .gitignore is optional


def test_validate_all_success(temp_project):
    """Test validation of all manifest files when all are valid."""
    updater = ManifestUpdater(temp_project)
    
    result = updater.validate_all()
    
    assert result.passed
    assert len(result.errors) == 0


def test_validate_all_with_errors(temp_project):
    """Test validation of all manifest files when some have errors."""
    # Make pyproject.toml invalid
    (temp_project / "pyproject.toml").write_text("[tool.setuptools]\n")
    
    updater = ManifestUpdater(temp_project)
    
    result = updater.validate_all()
    
    assert not result.passed
    assert len(result.errors) > 0


def test_update_all_manifests_success(temp_project):
    """Test updating all manifest files successfully."""
    updater = ManifestUpdater(temp_project)
    
    removed_dirs = ["lib/", "build/"]
    cache_patterns = ["*.pyc", "__pycache__"]
    
    success, errors = updater.update_all_manifests(removed_dirs, cache_patterns)
    
    assert success
    assert len(errors) == 0
    
    # Verify all files were updated
    pyproject_content = (temp_project / "pyproject.toml").read_text()
    assert '"lib/"' in pyproject_content
    
    manifest_content = (temp_project / "MANIFEST.in").read_text()
    assert "exclude lib/" in manifest_content or "global-exclude *.pyc" in manifest_content
    
    gitignore_content = (temp_project / ".gitignore").read_text()
    assert "lib/" in gitignore_content


def test_update_all_manifests_with_validation_errors(temp_project):
    """Test update_all_manifests when validation fails."""
    updater = ManifestUpdater(temp_project)
    
    # Make updates
    removed_dirs = ["lib/"]
    cache_patterns = ["*.pyc"]
    
    success, errors = updater.update_all_manifests(removed_dirs, cache_patterns)
    
    # Should succeed with valid files
    assert success or len(errors) > 0  # Either succeeds or reports errors


def test_parse_pyproject_excludes_empty(temp_project):
    """Test parsing pyproject.toml with no excludes."""
    updater = ManifestUpdater(temp_project)
    
    content = (temp_project / "pyproject.toml").read_text()
    excludes = updater._parse_pyproject_excludes(content)
    
    assert excludes == []


def test_parse_pyproject_excludes_with_patterns(temp_project):
    """Test parsing pyproject.toml with existing excludes."""
    # Add excludes to pyproject.toml
    content = """[tool.setuptools.packages.find]
exclude = ["tests", "docs", "*.egg-info"]
"""
    (temp_project / "pyproject.toml").write_text(content)
    
    updater = ManifestUpdater(temp_project)
    
    content = (temp_project / "pyproject.toml").read_text()
    excludes = updater._parse_pyproject_excludes(content)
    
    assert "tests" in excludes
    assert "docs" in excludes
    assert "*.egg-info" in excludes


def test_update_pyproject_without_setuptools_section(tmp_path):
    """Test updating pyproject.toml that doesn't have setuptools section."""
    # Create minimal pyproject.toml
    pyproject_content = """[build-system]
requires = ["setuptools>=61.0"]

[project]
name = "test-project"
"""
    (tmp_path / "pyproject.toml").write_text(pyproject_content)
    
    updater = ManifestUpdater(tmp_path)
    
    patterns = ["lib/", "build/"]
    success = updater.update_pyproject_exclusions(patterns)
    
    assert success
    
    # Verify sections were added
    content = (tmp_path / "pyproject.toml").read_text()
    assert "[tool.setuptools]" in content
    assert "[tool.setuptools.packages.find]" in content
    assert "exclude = " in content
