"""
Unit tests for AuditEngine.

Tests audit report generation, size impact calculations, and report formatting.
"""

import pytest
from pathlib import Path
import tempfile
from datetime import datetime

from scripts.cleanup.audit import AuditEngine
from scripts.cleanup.scanner import FileScanner
from scripts.cleanup.categorizer import FileCategorizer
from scripts.cleanup.models import (
    ProjectInventory,
    CategorizedFiles,
    FileInfo,
    DirectoryInfo,
    FileCategory,
    SizeImpact,
    AuditReport,
)


class TestAuditEngineBasics:
    """Test basic AuditEngine functionality."""
    
    def test_audit_engine_initialization(self):
        """Test AuditEngine can be initialized with scanner and categorizer."""
        scanner = FileScanner()
        categorizer = FileCategorizer()
        engine = AuditEngine(scanner, categorizer)
        
        assert engine.scanner is scanner
        assert engine.categorizer is categorizer
        assert engine._inventory is None
        assert engine._categorized is None
    
    def test_scan_project_empty_directory(self):
        """Test scanning an empty project directory."""
        with tempfile.TemporaryDirectory() as tmpdir:
            scanner = FileScanner()
            categorizer = FileCategorizer()
            engine = AuditEngine(scanner, categorizer)
            
            inventory = engine.scan_project(Path(tmpdir))
            
            assert isinstance(inventory, ProjectInventory)
            assert len(inventory.all_files) == 0
            assert inventory.total_size == 0
    
    def test_scan_project_with_files(self):
        """Test scanning a project with files."""
        with tempfile.TemporaryDirectory() as tmpdir:
            tmp_path = Path(tmpdir)
            
            # Create test files
            (tmp_path / "file1.txt").write_text("content1")
            (tmp_path / "file2.py").write_text("content2")
            
            scanner = FileScanner()
            categorizer = FileCategorizer()
            engine = AuditEngine(scanner, categorizer)
            
            inventory = engine.scan_project(tmp_path)
            
            assert len(inventory.all_files) == 2
            assert inventory.total_size > 0
            
            filenames = {f.path.name for f in inventory.all_files}
            assert filenames == {"file1.txt", "file2.py"}


class TestFileCategorization:
    """Test file categorization in audit engine."""
    
    def test_categorize_files_empty_inventory(self):
        """Test categorizing an empty inventory."""
        scanner = FileScanner()
        categorizer = FileCategorizer()
        engine = AuditEngine(scanner, categorizer)
        
        inventory = ProjectInventory(all_files=[], all_directories=[], total_size=0)
        categorized = engine.categorize_files(inventory)
        
        assert isinstance(categorized, CategorizedFiles)
        assert len(categorized.keep) == 0
        assert len(categorized.remove) == 0
        assert len(categorized.consolidate) == 0
        assert len(categorized.archive) == 0
    
    def test_categorize_files_with_critical_files(self):
        """Test categorizing files with critical components."""
        scanner = FileScanner()
        categorizer = FileCategorizer()
        engine = AuditEngine(scanner, categorizer)
        
        # Create mock file infos
        file1 = FileInfo(
            path=Path("agentic_sdlc/core/main.py"),
            size=1000,
            modified_time=datetime.now()
        )
        file2 = FileInfo(
            path=Path("pyproject.toml"),
            size=500,
            modified_time=datetime.now()
        )
        
        inventory = ProjectInventory(
            all_files=[file1, file2],
            all_directories=[],
            total_size=1500
        )
        
        categorized = engine.categorize_files(inventory)
        
        assert len(categorized.keep) == 2
        assert file1.category == FileCategory.KEEP
        assert file2.category == FileCategory.KEEP
    
    def test_categorize_files_with_corrupt_directory(self):
        """Test categorizing files in corrupt directories."""
        scanner = FileScanner()
        categorizer = FileCategorizer()
        engine = AuditEngine(scanner, categorizer)
        
        # Create mock file info in corrupt directory
        file1 = FileInfo(
            path=Path("build_corrupt_20260131/test.py"),
            size=1000,
            modified_time=datetime.now()
        )
        
        inventory = ProjectInventory(
            all_files=[file1],
            all_directories=[],
            total_size=1000
        )
        
        categorized = engine.categorize_files(inventory)
        
        assert len(categorized.remove) == 1
        assert file1.category == FileCategory.REMOVE
        assert "_corrupt_" in file1.reason.lower() or "corrupt" in file1.reason.lower()
    
    def test_categorize_files_with_requirements_file(self):
        """Test categorizing requirements files."""
        scanner = FileScanner()
        categorizer = FileCategorizer()
        engine = AuditEngine(scanner, categorizer)
        
        # Create mock requirements file
        file1 = FileInfo(
            path=Path("requirements_tools.txt"),
            size=500,
            modified_time=datetime.now()
        )
        
        inventory = ProjectInventory(
            all_files=[file1],
            all_directories=[],
            total_size=500
        )
        
        categorized = engine.categorize_files(inventory)
        
        assert len(categorized.consolidate) == 1
        assert file1.category == FileCategory.CONSOLIDATE


class TestSizeImpactCalculation:
    """Test size impact calculations."""
    
    def test_calculate_impact_no_removal(self):
        """Test calculating impact when no files are removed."""
        scanner = FileScanner()
        categorizer = FileCategorizer()
        engine = AuditEngine(scanner, categorizer)
        
        # Create inventory with only KEEP files
        file1 = FileInfo(
            path=Path("agentic_sdlc/core/main.py"),
            size=1000,
            modified_time=datetime.now(),
            category=FileCategory.KEEP
        )
        
        engine._inventory = ProjectInventory(
            all_files=[file1],
            all_directories=[],
            total_size=1000
        )
        engine._categorized = CategorizedFiles(keep=[file1])
        
        impact = engine.calculate_impact()
        
        assert isinstance(impact, SizeImpact)
        assert impact.current_size == 1000
        assert impact.projected_size == 1000
        assert impact.reduction == 0
        assert impact.reduction_percent == 0.0
    
    def test_calculate_impact_with_removal(self):
        """Test calculating impact with files to remove."""
        scanner = FileScanner()
        categorizer = FileCategorizer()
        engine = AuditEngine(scanner, categorizer)
        
        # Create inventory with KEEP and REMOVE files
        file1 = FileInfo(
            path=Path("agentic_sdlc/core/main.py"),
            size=1000,
            modified_time=datetime.now(),
            category=FileCategory.KEEP
        )
        file2 = FileInfo(
            path=Path("build_corrupt_20260131/test.py"),
            size=500,
            modified_time=datetime.now(),
            category=FileCategory.REMOVE
        )
        
        engine._inventory = ProjectInventory(
            all_files=[file1, file2],
            all_directories=[],
            total_size=1500
        )
        engine._categorized = CategorizedFiles(keep=[file1], remove=[file2])
        
        impact = engine.calculate_impact()
        
        assert impact.current_size == 1500
        assert impact.projected_size == 1000
        assert impact.reduction == 500
        assert impact.reduction_percent == pytest.approx(33.33, rel=0.1)
    
    def test_calculate_impact_with_archive(self):
        """Test calculating impact with files to archive."""
        scanner = FileScanner()
        categorizer = FileCategorizer()
        engine = AuditEngine(scanner, categorizer)
        
        # Create inventory with KEEP and ARCHIVE files
        file1 = FileInfo(
            path=Path("agentic_sdlc/core/main.py"),
            size=1000,
            modified_time=datetime.now(),
            category=FileCategory.KEEP
        )
        file2 = FileInfo(
            path=Path(".brain/old_data.json"),
            size=300,
            modified_time=datetime.now(),
            category=FileCategory.ARCHIVE
        )
        
        engine._inventory = ProjectInventory(
            all_files=[file1, file2],
            all_directories=[],
            total_size=1300
        )
        engine._categorized = CategorizedFiles(keep=[file1], archive=[file2])
        
        impact = engine.calculate_impact()
        
        assert impact.current_size == 1300
        assert impact.projected_size == 1000
        assert impact.reduction == 300
        assert impact.reduction_percent == pytest.approx(23.08, rel=0.1)
    
    def test_calculate_impact_before_scan_raises_error(self):
        """Test that calculate_impact raises error if scan not performed."""
        scanner = FileScanner()
        categorizer = FileCategorizer()
        engine = AuditEngine(scanner, categorizer)
        
        with pytest.raises(RuntimeError, match="Must call scan_project"):
            engine.calculate_impact()


class TestReportGeneration:
    """Test audit report generation."""
    
    def test_generate_report_empty_project(self):
        """Test generating report for empty project."""
        with tempfile.TemporaryDirectory() as tmpdir:
            scanner = FileScanner()
            categorizer = FileCategorizer()
            engine = AuditEngine(scanner, categorizer)
            
            report = engine.generate_report(Path(tmpdir))
            
            assert isinstance(report, AuditReport)
            assert report.total_files == 0
            assert report.size_impact.current_size == 0
            assert len(report.recommendations) > 0
    
    def test_generate_report_with_files(self):
        """Test generating report for project with files."""
        with tempfile.TemporaryDirectory() as tmpdir:
            tmp_path = Path(tmpdir)
            
            # Create test files
            (tmp_path / "README.md").write_text("# Project")
            (tmp_path / "test.pyc").write_text("compiled")
            
            scanner = FileScanner()
            categorizer = FileCategorizer()
            engine = AuditEngine(scanner, categorizer)
            
            report = engine.generate_report(tmp_path)
            
            assert report.total_files == 2
            assert report.size_impact.current_size > 0
            assert len(report.categorized_files.keep) >= 1  # README.md
            assert len(report.categorized_files.remove) >= 1  # test.pyc


class TestReportFormatting:
    """Test markdown report formatting."""
    
    def test_format_report_markdown_structure(self):
        """Test that formatted report has correct markdown structure."""
        scanner = FileScanner()
        categorizer = FileCategorizer()
        engine = AuditEngine(scanner, categorizer)
        
        # Create mock report
        file1 = FileInfo(
            path=Path("test.py"),
            size=1000,
            modified_time=datetime.now(),
            category=FileCategory.KEEP,
            reason="Test file"
        )
        
        categorized = CategorizedFiles(keep=[file1])
        impact = SizeImpact(
            current_size=1000,
            projected_size=1000,
            reduction=0,
            reduction_percent=0.0
        )
        
        report = AuditReport(
            timestamp=datetime.now(),
            total_files=1,
            categorized_files=categorized,
            size_impact=impact,
            recommendations=["Test recommendation"]
        )
        
        markdown = engine.format_report_markdown(report)
        
        # Check for key sections
        assert "# Cleanup Audit Report" in markdown
        assert "## Summary" in markdown
        assert "## Size Impact" in markdown
        assert "## Recommendations" in markdown
        assert "Total Files Scanned: 1" in markdown
    
    def test_format_report_markdown_with_removals(self):
        """Test formatting report with files to remove."""
        scanner = FileScanner()
        categorizer = FileCategorizer()
        engine = AuditEngine(scanner, categorizer)
        
        # Create mock report with removals
        file1 = FileInfo(
            path=Path("test.pyc"),
            size=500,
            modified_time=datetime.now(),
            category=FileCategory.REMOVE,
            reason="Cache file - remove"
        )
        
        categorized = CategorizedFiles(remove=[file1])
        impact = SizeImpact(
            current_size=500,
            projected_size=0,
            reduction=500,
            reduction_percent=100.0
        )
        
        report = AuditReport(
            timestamp=datetime.now(),
            total_files=1,
            categorized_files=categorized,
            size_impact=impact,
            recommendations=[]
        )
        
        markdown = engine.format_report_markdown(report)
        
        assert "## Files to Remove" in markdown
        assert "Cache file - remove" in markdown
        assert "test.pyc" in markdown
    
    def test_format_report_markdown_with_consolidation(self):
        """Test formatting report with files to consolidate."""
        scanner = FileScanner()
        categorizer = FileCategorizer()
        engine = AuditEngine(scanner, categorizer)
        
        # Create mock report with consolidation
        file1 = FileInfo(
            path=Path("requirements.txt"),
            size=200,
            modified_time=datetime.now(),
            category=FileCategory.CONSOLIDATE,
            reason="Requirements file - consolidate into pyproject.toml"
        )
        
        categorized = CategorizedFiles(consolidate=[file1])
        impact = SizeImpact(
            current_size=200,
            projected_size=0,
            reduction=200,
            reduction_percent=100.0
        )
        
        report = AuditReport(
            timestamp=datetime.now(),
            total_files=1,
            categorized_files=categorized,
            size_impact=impact,
            recommendations=[]
        )
        
        markdown = engine.format_report_markdown(report)
        
        assert "## Files to Consolidate" in markdown
        assert "requirements.txt" in markdown


class TestRecommendations:
    """Test recommendation generation."""
    
    def test_recommendations_significant_reduction(self):
        """Test recommendations for significant size reduction."""
        scanner = FileScanner()
        categorizer = FileCategorizer()
        engine = AuditEngine(scanner, categorizer)
        
        # Create scenario with significant reduction
        file1 = FileInfo(
            path=Path("large_file.bin"),
            size=100_000_000,  # 100 MB
            modified_time=datetime.now(),
            category=FileCategory.REMOVE
        )
        
        categorized = CategorizedFiles(remove=[file1])
        impact = SizeImpact(
            current_size=120_000_000,
            projected_size=20_000_000,
            reduction=100_000_000,
            reduction_percent=83.33
        )
        
        recommendations = engine._generate_recommendations(categorized, impact)
        
        assert len(recommendations) > 0
        assert any("Significant" in rec or "significant" in rec for rec in recommendations)
    
    def test_recommendations_corrupt_directories(self):
        """Test recommendations mention corrupt directories."""
        scanner = FileScanner()
        categorizer = FileCategorizer()
        engine = AuditEngine(scanner, categorizer)
        
        # Create scenario with corrupt directory
        file1 = FileInfo(
            path=Path("build_corrupt_20260131/test.py"),
            size=1000,
            modified_time=datetime.now(),
            category=FileCategory.REMOVE,
            reason="Corrupt directory"
        )
        
        categorized = CategorizedFiles(remove=[file1])
        impact = SizeImpact(
            current_size=1000,
            projected_size=0,
            reduction=1000,
            reduction_percent=100.0
        )
        
        recommendations = engine._generate_recommendations(categorized, impact)
        
        assert any("corrupt" in rec.lower() for rec in recommendations)
    
    def test_recommendations_dependency_consolidation(self):
        """Test recommendations mention dependency consolidation."""
        scanner = FileScanner()
        categorizer = FileCategorizer()
        engine = AuditEngine(scanner, categorizer)
        
        # Create scenario with requirements files
        file1 = FileInfo(
            path=Path("requirements.txt"),
            size=100,
            modified_time=datetime.now(),
            category=FileCategory.CONSOLIDATE
        )
        
        categorized = CategorizedFiles(consolidate=[file1])
        impact = SizeImpact(
            current_size=100,
            projected_size=0,
            reduction=100,
            reduction_percent=100.0
        )
        
        recommendations = engine._generate_recommendations(categorized, impact)
        
        assert any("consolidate" in rec.lower() for rec in recommendations)
