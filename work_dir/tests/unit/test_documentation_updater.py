"""
Unit tests for DocumentationUpdater.

Tests cover:
- README.md size update
- CLEANUP-SUMMARY.md generation
- CONTRIBUTING.md updates with dependency management guidelines
- .gitignore updates
"""

import pytest
from pathlib import Path
from datetime import datetime
from scripts.cleanup.docs import DocumentationUpdater
from scripts.cleanup.models import (
    CleanupResult,
    CategorizedFiles,
    SizeImpact,
    FileInfo,
    ValidationResult,
    FileCategory,
)


class TestDocumentationUpdater:
    """Test suite for DocumentationUpdater class."""
    
    @pytest.fixture
    def temp_project_root(self, tmp_path):
        """Create temporary project root with basic files."""
        # Create README.md
        readme_content = """# Test Project
![Version](https://img.shields.io/badge/version-1.0.0-blue.svg)

> A test project for documentation updater

## 🚀 Quick Start

Install the package:
```bash
pip install test-project
```

## 🧠 Features

- Feature 1
- Feature 2

## 📄 License
MIT License
"""
        (tmp_path / "README.md").write_text(readme_content)
        
        # Create CONTRIBUTING.md
        contributing_content = """# Contributing to Test Project

## Getting Started

1. Fork the repository
2. Clone your fork

## Development Workflow

1. Create a new branch
2. Make your changes
3. Run tests

## Pull Request Process

1. Push your branch
2. Open a Pull Request

## Code of Conduct

Be respectful.

## License

MIT License
"""
        (tmp_path / "CONTRIBUTING.md").write_text(contributing_content)
        
        # Create .gitignore
        gitignore_content = """# Python
*.pyc
.venv/

# IDE
.vscode/
"""
        (tmp_path / ".gitignore").write_text(gitignore_content)
        
        # Create docs directory
        (tmp_path / "docs").mkdir()
        
        return tmp_path
    
    @pytest.fixture
    def updater(self, temp_project_root):
        """Create DocumentationUpdater instance."""
        return DocumentationUpdater(project_root=temp_project_root, verbose=False)
    
    @pytest.fixture
    def sample_cleanup_result(self):
        """Create sample cleanup result for testing."""
        validation_result = ValidationResult(
            passed=True,
            import_check=True,
            cli_check=True,
            test_check=True,
            build_check=True,
            errors=[]
        )
        
        return CleanupResult(
            success=True,
            backup_id="backup_20260131_143022",
            files_removed=50,
            size_freed=115 * 1024 * 1024,  # 115 MB
            errors=[],
            validation_result=validation_result
        )
    
    @pytest.fixture
    def sample_categorized_files(self):
        """Create sample categorized files for testing."""
        file1 = FileInfo(
            path=Path("corrupt_dir/file1.py"),
            size=45 * 1024 * 1024,  # 45 MB
            modified_time=datetime.now(),
            category=FileCategory.REMOVE,
            is_critical=False,
            reason="Corrupt directory"
        )
        
        file2 = FileInfo(
            path=Path("lib/bundled.py"),
            size=68 * 1024 * 1024,  # 68 MB
            modified_time=datetime.now(),
            category=FileCategory.REMOVE,
            is_critical=False,
            reason="Bundled library"
        )
        
        file3 = FileInfo(
            path=Path("requirements_tools.txt"),
            size=512,
            modified_time=datetime.now(),
            category=FileCategory.CONSOLIDATE,
            is_critical=False,
            reason="Dependency consolidation"
        )
        
        file4 = FileInfo(
            path=Path(".brain/old_data.json"),
            size=2 * 1024 * 1024,  # 2 MB
            modified_time=datetime.now(),
            category=FileCategory.ARCHIVE,
            is_critical=False,
            reason="Old cache data"
        )
        
        return CategorizedFiles(
            keep=[],
            remove=[file1, file2],
            consolidate=[file3],
            archive=[file4]
        )
    
    @pytest.fixture
    def sample_size_impact(self):
        """Create sample size impact for testing."""
        return SizeImpact(
            current_size=120 * 1024 * 1024,  # 120 MB
            projected_size=5 * 1024 * 1024,  # 5 MB
            reduction=115 * 1024 * 1024,  # 115 MB
            reduction_percent=95.8
        )
    
    def test_update_readme_size_success(self, updater, temp_project_root):
        """Test successful README.md size update."""
        old_size = 120 * 1024 * 1024  # 120 MB
        new_size = 5 * 1024 * 1024  # 5 MB
        
        result = updater.update_readme_size(old_size, new_size)
        
        assert result is True
        
        # Check README was updated
        readme_path = temp_project_root / "README.md"
        content = readme_path.read_text()
        
        # Should contain package size information
        assert "Package Size" in content or "5.0MB" in content or "5 MB" in content
        assert "120" in content or "120MB" in content  # Old size mentioned
    
    def test_update_readme_size_file_not_found(self, tmp_path):
        """Test README.md update when file doesn't exist."""
        updater = DocumentationUpdater(project_root=tmp_path, verbose=False)
        
        result = updater.update_readme_size(1024, 512)
        
        assert result is False
    
    def test_update_readme_size_formatting(self, updater, temp_project_root):
        """Test README.md size formatting."""
        old_size = 125829120  # ~120 MB
        new_size = 5242880  # ~5 MB
        
        result = updater.update_readme_size(old_size, new_size)
        
        assert result is True
        
        readme_path = temp_project_root / "README.md"
        content = readme_path.read_text()
        
        # Should contain formatted sizes
        assert "MB" in content
    
    def test_generate_cleanup_summary_structure(
        self,
        updater,
        sample_cleanup_result,
        sample_categorized_files,
        sample_size_impact,
        temp_project_root
    ):
        """Test CLEANUP-SUMMARY.md structure."""
        summary_path = updater.generate_cleanup_summary(
            sample_cleanup_result,
            sample_categorized_files,
            sample_size_impact
        )
        
        # Check file was created
        assert summary_path.exists()
        assert summary_path.name == "CLEANUP-SUMMARY.md"
        assert summary_path.parent == temp_project_root / "docs"
        
        # Check content structure
        content = summary_path.read_text()
        
        assert "# Project Cleanup Summary" in content
        assert "## Overview" in content
        assert "## Size Reduction" in content
        assert "## What Was Removed" in content
        assert "## Backup and Rollback" in content
        assert "## Validation Results" in content
        assert "## Next Steps for Developers" in content
    
    def test_generate_cleanup_summary_size_reduction(
        self,
        updater,
        sample_cleanup_result,
        sample_categorized_files,
        sample_size_impact
    ):
        """Test size reduction section in CLEANUP-SUMMARY.md."""
        summary_path = updater.generate_cleanup_summary(
            sample_cleanup_result,
            sample_categorized_files,
            sample_size_impact
        )
        
        content = summary_path.read_text()
        
        assert "Before Cleanup" in content
        assert "After Cleanup" in content
        assert "Size Freed" in content
        assert "120.0MB" in content or "120MB" in content
        assert "5.0MB" in content or "5MB" in content
        assert "95.8%" in content
    
    def test_generate_cleanup_summary_removed_files(
        self,
        updater,
        sample_cleanup_result,
        sample_categorized_files,
        sample_size_impact
    ):
        """Test removed files section in CLEANUP-SUMMARY.md."""
        summary_path = updater.generate_cleanup_summary(
            sample_cleanup_result,
            sample_categorized_files,
            sample_size_impact
        )
        
        content = summary_path.read_text()
        
        # Check removed files are listed by reason
        assert "Corrupt directory" in content
        assert "Bundled library" in content
        assert "corrupt_dir/file1.py" in content
        assert "lib/bundled.py" in content
    
    def test_generate_cleanup_summary_consolidated_dependencies(
        self,
        updater,
        sample_cleanup_result,
        sample_categorized_files,
        sample_size_impact
    ):
        """Test consolidated dependencies section in CLEANUP-SUMMARY.md."""
        summary_path = updater.generate_cleanup_summary(
            sample_cleanup_result,
            sample_categorized_files,
            sample_size_impact
        )
        
        content = summary_path.read_text()
        
        assert "Dependencies Consolidated" in content
        assert "requirements_tools.txt" in content
        assert "pyproject.toml" in content
    
    def test_generate_cleanup_summary_archived_files(
        self,
        updater,
        sample_cleanup_result,
        sample_categorized_files,
        sample_size_impact
    ):
        """Test archived files section in CLEANUP-SUMMARY.md."""
        summary_path = updater.generate_cleanup_summary(
            sample_cleanup_result,
            sample_categorized_files,
            sample_size_impact
        )
        
        content = summary_path.read_text()
        
        assert "Files Archived" in content
        assert "1 files" in content
    
    def test_generate_cleanup_summary_backup_info(
        self,
        updater,
        sample_cleanup_result,
        sample_categorized_files,
        sample_size_impact
    ):
        """Test backup information section in CLEANUP-SUMMARY.md."""
        summary_path = updater.generate_cleanup_summary(
            sample_cleanup_result,
            sample_categorized_files,
            sample_size_impact
        )
        
        content = summary_path.read_text()
        
        assert "Backup ID" in content
        assert "backup_20260131_143022" in content
        assert "python scripts/cleanup.py --rollback" in content
    
    def test_generate_cleanup_summary_validation_results(
        self,
        updater,
        sample_cleanup_result,
        sample_categorized_files,
        sample_size_impact
    ):
        """Test validation results section in CLEANUP-SUMMARY.md."""
        summary_path = updater.generate_cleanup_summary(
            sample_cleanup_result,
            sample_categorized_files,
            sample_size_impact
        )
        
        content = summary_path.read_text()
        
        assert "Validation Results" in content
        assert "✅ Passed" in content
        assert "Import Check" in content
        assert "CLI Check" in content
        assert "Test Suite" in content
        assert "Package Build" in content
    
    def test_generate_cleanup_summary_next_steps(
        self,
        updater,
        sample_cleanup_result,
        sample_categorized_files,
        sample_size_impact
    ):
        """Test next steps section in CLEANUP-SUMMARY.md."""
        summary_path = updater.generate_cleanup_summary(
            sample_cleanup_result,
            sample_categorized_files,
            sample_size_impact
        )
        
        content = summary_path.read_text()
        
        assert "Next Steps for Developers" in content
        assert "Review Changes" in content
        assert "Run Tests" in content
        assert "pip install -e .[dev]" in content
    
    def test_update_contributing_guidelines_success(self, updater, temp_project_root):
        """Test successful CONTRIBUTING.md update."""
        result = updater.update_contributing_guidelines()
        
        assert result is True
        
        # Check CONTRIBUTING.md was updated
        contributing_path = temp_project_root / "CONTRIBUTING.md"
        content = contributing_path.read_text()
        
        # Should contain dependency management section
        assert "## Dependency Management" in content
        assert "pyproject.toml" in content
        assert "Dependency Groups" in content
        assert "Adding a New Dependency" in content
        assert "Best Practices" in content
    
    def test_update_contributing_guidelines_file_not_found(self, tmp_path):
        """Test CONTRIBUTING.md update when file doesn't exist."""
        updater = DocumentationUpdater(project_root=tmp_path, verbose=False)
        
        result = updater.update_contributing_guidelines()
        
        assert result is False
    
    def test_update_contributing_guidelines_dependency_groups(self, updater, temp_project_root):
        """Test dependency groups section in CONTRIBUTING.md."""
        result = updater.update_contributing_guidelines()
        
        assert result is True
        
        contributing_path = temp_project_root / "CONTRIBUTING.md"
        content = contributing_path.read_text()
        
        # Check dependency groups are documented
        assert "[project.dependencies]" in content
        assert "[project.optional-dependencies.dev]" in content
        assert "[project.optional-dependencies.graph]" in content
        assert "[project.optional-dependencies.mcp]" in content
        assert "[project.optional-dependencies.tools]" in content
    
    def test_update_contributing_guidelines_best_practices(self, updater, temp_project_root):
        """Test best practices section in CONTRIBUTING.md."""
        result = updater.update_contributing_guidelines()
        
        assert result is True
        
        contributing_path = temp_project_root / "CONTRIBUTING.md"
        content = contributing_path.read_text()
        
        # Check best practices are included
        assert "Pin major versions" in content
        assert "Avoid overly strict pinning" in content
        assert "Test with minimum versions" in content
    
    def test_update_contributing_guidelines_insertion_before_pr_section(
        self,
        updater,
        temp_project_root
    ):
        """Test that dependency management is inserted before Pull Request Process."""
        result = updater.update_contributing_guidelines()
        
        assert result is True
        
        contributing_path = temp_project_root / "CONTRIBUTING.md"
        content = contributing_path.read_text()
        
        # Find positions
        dep_mgmt_pos = content.find("## Dependency Management")
        pr_process_pos = content.find("## Pull Request Process")
        
        # Dependency management should come before PR process
        assert dep_mgmt_pos < pr_process_pos
    
    def test_update_contributing_guidelines_idempotent(self, updater, temp_project_root):
        """Test that updating CONTRIBUTING.md twice doesn't duplicate content."""
        # First update
        result1 = updater.update_contributing_guidelines()
        assert result1 is True
        
        # Second update
        result2 = updater.update_contributing_guidelines()
        assert result2 is True
        
        # Check content wasn't duplicated
        contributing_path = temp_project_root / "CONTRIBUTING.md"
        content = contributing_path.read_text()
        
        # Should only have one dependency management section
        assert content.count("## Dependency Management") == 1
    
    def test_update_gitignore_default_patterns(self, updater, temp_project_root):
        """Test updating .gitignore with default patterns."""
        result = updater.update_gitignore()
        
        assert result is True
        
        # Check .gitignore was updated
        gitignore_path = temp_project_root / ".gitignore"
        content = gitignore_path.read_text()
        
        # Should contain cleanup backup pattern
        assert ".cleanup_backup/" in content
    
    def test_update_gitignore_custom_patterns(self, updater, temp_project_root):
        """Test updating .gitignore with custom patterns."""
        custom_patterns = ["*.log", "temp/", "*.tmp"]
        
        result = updater.update_gitignore(patterns=custom_patterns)
        
        assert result is True
        
        gitignore_path = temp_project_root / ".gitignore"
        content = gitignore_path.read_text()
        
        # Should contain custom patterns
        assert "*.log" in content
        assert "temp/" in content
        assert "*.tmp" in content
    
    def test_update_gitignore_file_not_found(self, tmp_path):
        """Test .gitignore update when file doesn't exist."""
        updater = DocumentationUpdater(project_root=tmp_path, verbose=False)
        
        result = updater.update_gitignore()
        
        assert result is False
    
    def test_update_gitignore_idempotent(self, updater, temp_project_root):
        """Test that updating .gitignore twice doesn't duplicate patterns."""
        # First update
        result1 = updater.update_gitignore()
        assert result1 is True
        
        # Second update
        result2 = updater.update_gitignore()
        assert result2 is True
        
        # Check patterns weren't duplicated
        gitignore_path = temp_project_root / ".gitignore"
        content = gitignore_path.read_text()
        
        # Count occurrences of a pattern
        assert content.count(".cleanup_backup/") == 1
    
    def test_format_size_simple_bytes(self):
        """Test simple size formatting for bytes."""
        assert DocumentationUpdater._format_size_simple(0) == "0B"
        assert DocumentationUpdater._format_size_simple(512) == "512B"
        assert DocumentationUpdater._format_size_simple(1023) == "1023B"
    
    def test_format_size_simple_kilobytes(self):
        """Test simple size formatting for kilobytes."""
        assert DocumentationUpdater._format_size_simple(1024) == "1.0KB"
        assert DocumentationUpdater._format_size_simple(1536) == "1.5KB"
        assert DocumentationUpdater._format_size_simple(10240) == "10.0KB"
    
    def test_format_size_simple_megabytes(self):
        """Test simple size formatting for megabytes."""
        assert DocumentationUpdater._format_size_simple(1024 * 1024) == "1.0MB"
        assert DocumentationUpdater._format_size_simple(5 * 1024 * 1024) == "5.0MB"
        assert DocumentationUpdater._format_size_simple(120 * 1024 * 1024) == "120.0MB"
    
    def test_format_size_simple_gigabytes(self):
        """Test simple size formatting for gigabytes."""
        assert DocumentationUpdater._format_size_simple(1024 * 1024 * 1024) == "1.0GB"
        assert DocumentationUpdater._format_size_simple(int(2.5 * 1024 * 1024 * 1024)) == "2.5GB"
    
    def test_generate_cleanup_summary_empty_categories(
        self,
        updater,
        sample_cleanup_result,
        sample_size_impact
    ):
        """Test CLEANUP-SUMMARY.md with empty file categories."""
        empty_categorized = CategorizedFiles(
            keep=[],
            remove=[],
            consolidate=[],
            archive=[]
        )
        
        summary_path = updater.generate_cleanup_summary(
            sample_cleanup_result,
            empty_categorized,
            sample_size_impact
        )
        
        content = summary_path.read_text()
        
        # Should still have structure
        assert "# Project Cleanup Summary" in content
        assert "No files were removed" in content
    
    def test_generate_cleanup_summary_failed_cleanup(
        self,
        updater,
        sample_categorized_files,
        sample_size_impact
    ):
        """Test CLEANUP-SUMMARY.md with failed cleanup."""
        failed_result = CleanupResult(
            success=False,
            backup_id="backup_test",
            files_removed=0,
            size_freed=0,
            errors=["Test error 1", "Test error 2"]
        )
        
        summary_path = updater.generate_cleanup_summary(
            failed_result,
            sample_categorized_files,
            sample_size_impact
        )
        
        content = summary_path.read_text()
        
        assert "❌ Failed" in content
