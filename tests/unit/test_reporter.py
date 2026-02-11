"""
Unit tests for ReportGenerator.

Tests cover:
- Audit report markdown generation
- Cleanup summary markdown generation
- Report saving to docs/
- Size formatting utilities
- Timestamp formatting
"""

import pytest
from pathlib import Path
from datetime import datetime
from scripts.cleanup.reporter import ReportGenerator
from scripts.cleanup.models import (
    AuditReport,
    CleanupResult,
    CategorizedFiles,
    SizeImpact,
    FileInfo,
    ValidationResult,
    FileCategory,
)


class TestReportGenerator:
    """Test suite for ReportGenerator class."""
    
    @pytest.fixture
    def temp_docs_dir(self, tmp_path):
        """Create temporary docs directory."""
        docs_dir = tmp_path / "docs"
        docs_dir.mkdir()
        return docs_dir
    
    @pytest.fixture
    def generator(self, temp_docs_dir):
        """Create ReportGenerator instance."""
        return ReportGenerator(docs_dir=temp_docs_dir, verbose=False)
    
    @pytest.fixture
    def sample_audit_report(self):
        """Create sample audit report for testing."""
        # Create sample files
        file1 = FileInfo(
            path=Path("test_corrupt/file1.py"),
            size=1024 * 1024,  # 1 MB
            modified_time=datetime.now(),
            category=FileCategory.REMOVE,
            is_critical=False,
            reason="Corrupt directory"
        )
        
        file2 = FileInfo(
            path=Path("requirements.txt"),
            size=512,
            modified_time=datetime.now(),
            category=FileCategory.CONSOLIDATE,
            is_critical=False,
            reason="Dependency consolidation"
        )
        
        file3 = FileInfo(
            path=Path(".brain/old_data.json"),
            size=2048 * 1024,  # 2 MB
            modified_time=datetime.now(),
            category=FileCategory.ARCHIVE,
            is_critical=False,
            reason="Old cache data"
        )
        
        categorized = CategorizedFiles(
            keep=[],
            remove=[file1],
            consolidate=[file2],
            archive=[file3]
        )
        
        size_impact = SizeImpact(
            current_size=10 * 1024 * 1024,  # 10 MB
            projected_size=7 * 1024 * 1024,  # 7 MB
            reduction=3 * 1024 * 1024,  # 3 MB
            reduction_percent=30.0
        )
        
        return AuditReport(
            timestamp=datetime(2026, 1, 31, 14, 30, 22),
            total_files=100,
            categorized_files=categorized,
            size_impact=size_impact,
            recommendations=[
                "Create backup before cleanup",
                "Run validation tests after cleanup"
            ]
        )
    
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
            size_freed=3 * 1024 * 1024,  # 3 MB
            errors=[],
            validation_result=validation_result
        )
    
    def test_format_size_bytes(self):
        """Test size formatting for bytes."""
        assert ReportGenerator.format_size(0) == "0 B"
        assert ReportGenerator.format_size(512) == "512 B"
        assert ReportGenerator.format_size(1023) == "1023 B"
    
    def test_format_size_kilobytes(self):
        """Test size formatting for kilobytes."""
        assert ReportGenerator.format_size(1024) == "1.00 KB"
        assert ReportGenerator.format_size(1536) == "1.50 KB"
        assert ReportGenerator.format_size(10240) == "10.00 KB"
    
    def test_format_size_megabytes(self):
        """Test size formatting for megabytes."""
        assert ReportGenerator.format_size(1024 * 1024) == "1.00 MB"
        assert ReportGenerator.format_size(1536 * 1024) == "1.50 MB"
        assert ReportGenerator.format_size(10 * 1024 * 1024) == "10.00 MB"
    
    def test_format_size_gigabytes(self):
        """Test size formatting for gigabytes."""
        assert ReportGenerator.format_size(1024 * 1024 * 1024) == "1.00 GB"
        assert ReportGenerator.format_size(2.5 * 1024 * 1024 * 1024) == "2.50 GB"
    
    def test_format_timestamp(self):
        """Test timestamp formatting."""
        dt = datetime(2026, 1, 31, 14, 30, 22)
        formatted = ReportGenerator.format_timestamp(dt)
        assert formatted == "2026-01-31 14:30:22"
    
    def test_generate_audit_report_structure(self, generator, sample_audit_report):
        """Test audit report markdown structure."""
        markdown = generator.generate_audit_report(sample_audit_report)
        
        # Check header
        assert "# Cleanup Audit Report" in markdown
        assert "**Generated**: 2026-01-31 14:30:22" in markdown
        assert "**Project**: Agentic SDLC" in markdown
        
        # Check summary section
        assert "## Summary" in markdown
        assert "Total Files Scanned: 100" in markdown
        assert "Files to Remove: 1" in markdown
        assert "Files to Consolidate: 1" in markdown
        assert "Files to Archive: 1" in markdown
        
        # Check size impact section
        assert "## Size Impact" in markdown
        assert "10.00 MB" in markdown  # Current size
        assert "7.00 MB" in markdown  # Projected size
        assert "3.00 MB" in markdown  # Reduction
        assert "30.0%" in markdown  # Reduction percent
    
    def test_generate_audit_report_files_to_remove(self, generator, sample_audit_report):
        """Test files to remove section in audit report."""
        markdown = generator.generate_audit_report(sample_audit_report)
        
        assert "## Files to Remove" in markdown
        assert "Corrupt directory" in markdown
        assert "test_corrupt/file1.py" in markdown
        assert "1.00 MB" in markdown
    
    def test_generate_audit_report_files_to_consolidate(self, generator, sample_audit_report):
        """Test files to consolidate section in audit report."""
        markdown = generator.generate_audit_report(sample_audit_report)
        
        assert "## Files to Consolidate" in markdown
        assert "requirements.txt" in markdown
        assert "Dependency consolidation" in markdown
    
    def test_generate_audit_report_files_to_archive(self, generator, sample_audit_report):
        """Test files to archive section in audit report."""
        markdown = generator.generate_audit_report(sample_audit_report)
        
        assert "## Files to Archive" in markdown
        assert ".brain/" in markdown
        assert "2.00 MB" in markdown
    
    def test_generate_audit_report_recommendations(self, generator, sample_audit_report):
        """Test recommendations section in audit report."""
        markdown = generator.generate_audit_report(sample_audit_report)
        
        assert "## Recommendations" in markdown
        assert "Create backup before cleanup" in markdown
        assert "Run validation tests after cleanup" in markdown
    
    def test_generate_cleanup_summary_structure(self, generator, sample_cleanup_result):
        """Test cleanup summary markdown structure."""
        markdown = generator.generate_cleanup_summary(sample_cleanup_result)
        
        # Check header
        assert "# Cleanup Summary" in markdown
        assert "**Status**: ✅ Success" in markdown
        
        # Check statistics section
        assert "## Statistics" in markdown
        assert "Files Removed: 50" in markdown
        assert "3.00 MB" in markdown
        assert "backup_20260131_143022" in markdown
    
    def test_generate_cleanup_summary_validation_results(self, generator, sample_cleanup_result):
        """Test validation results section in cleanup summary."""
        markdown = generator.generate_cleanup_summary(sample_cleanup_result)
        
        assert "## Validation Results" in markdown
        assert "Overall: ✅ Passed" in markdown
        assert "Import Check: ✅ Passed" in markdown
        assert "CLI Check: ✅ Passed" in markdown
        assert "Test Suite: ✅ Passed" in markdown
        assert "Package Build: ✅ Passed" in markdown
    
    def test_generate_cleanup_summary_failed_status(self, generator):
        """Test cleanup summary with failed status."""
        result = CleanupResult(
            success=False,
            backup_id="backup_test",
            files_removed=0,
            size_freed=0,
            errors=["Test error 1", "Test error 2"]
        )
        
        markdown = generator.generate_cleanup_summary(result)
        
        assert "**Status**: ❌ Failed" in markdown
        assert "## Errors Encountered" in markdown
        assert "Test error 1" in markdown
        assert "Test error 2" in markdown
    
    def test_generate_cleanup_summary_backup_info(self, generator, sample_cleanup_result):
        """Test backup information section in cleanup summary."""
        markdown = generator.generate_cleanup_summary(sample_cleanup_result)
        
        assert "## Backup Information" in markdown
        assert "backup_20260131_143022" in markdown
        assert "python scripts/cleanup.py --rollback" in markdown
    
    def test_generate_cleanup_summary_next_steps(self, generator, sample_cleanup_result):
        """Test next steps section in cleanup summary."""
        markdown = generator.generate_cleanup_summary(sample_cleanup_result)
        
        assert "## Next Steps" in markdown
        assert "Review the changes" in markdown
    
    def test_save_audit_report(self, generator, sample_audit_report, temp_docs_dir):
        """Test saving audit report to file."""
        report_path = generator.save_audit_report(sample_audit_report)
        
        # Check file was created
        assert report_path.exists()
        assert report_path.parent == temp_docs_dir
        
        # Check filename format
        assert report_path.name.startswith("CLEANUP-AUDIT-REPORT-")
        assert report_path.name.endswith(".md")
        
        # Check content
        content = report_path.read_text()
        assert "# Cleanup Audit Report" in content
        assert "Total Files Scanned: 100" in content
    
    def test_save_cleanup_summary(self, generator, sample_cleanup_result, temp_docs_dir):
        """Test saving cleanup summary to file."""
        summary_path = generator.save_cleanup_summary(sample_cleanup_result)
        
        # Check file was created
        assert summary_path.exists()
        assert summary_path.parent == temp_docs_dir
        
        # Check filename format
        assert summary_path.name.startswith("CLEANUP-SUMMARY-")
        assert summary_path.name.endswith(".md")
        
        # Check content
        content = summary_path.read_text()
        assert "# Cleanup Summary" in content
        assert "Files Removed: 50" in content
    
    def test_docs_dir_creation(self, tmp_path):
        """Test that docs directory is created if it doesn't exist."""
        docs_dir = tmp_path / "new_docs"
        assert not docs_dir.exists()
        
        generator = ReportGenerator(docs_dir=docs_dir)
        
        assert docs_dir.exists()
        assert docs_dir.is_dir()
    
    def test_generate_audit_report_empty_categories(self, generator):
        """Test audit report with empty file categories."""
        categorized = CategorizedFiles(
            keep=[],
            remove=[],
            consolidate=[],
            archive=[]
        )
        
        size_impact = SizeImpact(
            current_size=1024,
            projected_size=1024,
            reduction=0,
            reduction_percent=0.0
        )
        
        report = AuditReport(
            timestamp=datetime.now(),
            total_files=0,
            categorized_files=categorized,
            size_impact=size_impact,
            recommendations=[]
        )
        
        markdown = generator.generate_audit_report(report)
        
        # Should still have structure but no file lists
        assert "# Cleanup Audit Report" in markdown
        assert "## Summary" in markdown
        assert "Total Files Scanned: 0" in markdown
        assert "Files to Remove: 0" in markdown
    
    def test_generate_audit_report_many_files(self, generator):
        """Test audit report with many files (should truncate list)."""
        # Create 20 files to remove
        remove_files = []
        for i in range(20):
            file_info = FileInfo(
                path=Path(f"file{i}.py"),
                size=1024 * i,
                modified_time=datetime.now(),
                category=FileCategory.REMOVE,
                is_critical=False,
                reason="Test reason"
            )
            remove_files.append(file_info)
        
        categorized = CategorizedFiles(
            keep=[],
            remove=remove_files,
            consolidate=[],
            archive=[]
        )
        
        size_impact = SizeImpact(
            current_size=1024 * 1024,
            projected_size=512 * 1024,
            reduction=512 * 1024,
            reduction_percent=50.0
        )
        
        report = AuditReport(
            timestamp=datetime.now(),
            total_files=20,
            categorized_files=categorized,
            size_impact=size_impact,
            recommendations=[]
        )
        
        markdown = generator.generate_audit_report(report)
        
        # Should show first 10 files and indicate more
        assert "... and 10 more files" in markdown
    
    def test_generate_cleanup_summary_validation_errors(self, generator):
        """Test cleanup summary with validation errors."""
        validation_result = ValidationResult(
            passed=False,
            import_check=False,
            cli_check=True,
            test_check=False,
            build_check=True,
            errors=["Import failed: module not found", "Tests failed: 3 failures"]
        )
        
        result = CleanupResult(
            success=False,
            backup_id="backup_test",
            files_removed=10,
            size_freed=1024,
            errors=["Validation failed"],
            validation_result=validation_result
        )
        
        markdown = generator.generate_cleanup_summary(result)
        
        assert "Import Check: ❌ Failed" in markdown
        assert "Test Suite: ❌ Failed" in markdown
        assert "### Validation Errors" in markdown
        assert "Import failed: module not found" in markdown
        assert "Tests failed: 3 failures" in markdown
