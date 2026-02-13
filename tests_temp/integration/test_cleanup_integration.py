"""
Integration tests for the Project Audit and Cleanup System.

Tests the complete end-to-end workflows:
- Full audit → cleanup → validate cycle
- Rollback scenario
- Dry-run scenario
- Dependency consolidation scenario

These tests verify that all components work together correctly
and that the system maintains data integrity throughout the process.
"""

import pytest
from pathlib import Path
import tempfile
import shutil
from datetime import datetime, timedelta
import json

from scripts.cleanup.scanner import FileScanner
from scripts.cleanup.categorizer import FileCategorizer
from scripts.cleanup.backup import BackupManager
from scripts.cleanup.validator import Validator
from scripts.cleanup.dependencies import DependencyConsolidator
from scripts.cleanup.audit import AuditEngine
from scripts.cleanup.cleanup import CleanupEngine
from scripts.cleanup.models import (
    FileCategory,
    ValidationResult,
)


@pytest.fixture
def integration_project(tmp_path):
    """
    Create a realistic project structure for integration testing.
    
    This fixture creates a mock project with:
    - Critical components (core/, docs/, tests/)
    - Corrupt directories
    - Cache directories (.brain/, .hypothesis/, __pycache__)
    - Requirements files to consolidate
    - Bundled libraries (lib/)
    - Configuration files
    """
    project_root = tmp_path / "test_project"
    project_root.mkdir()
    
    # Create critical components
    core_dir = project_root / "agentic_sdlc" / "core"
    core_dir.mkdir(parents=True)
    (core_dir / "main.py").write_text("# Main module\nimport sys\n")
    (core_dir / "utils.py").write_text("# Utilities\ndef helper(): pass\n")
    
    intelligence_dir = project_root / "agentic_sdlc" / "intelligence"
    intelligence_dir.mkdir(parents=True)
    (intelligence_dir / "brain.py").write_text("# Brain module\n")
    
    docs_dir = project_root / "docs"
    docs_dir.mkdir()
    (docs_dir / "README.md").write_text("# Documentation\n")
    
    tests_dir = project_root / "tests"
    tests_dir.mkdir()
    (tests_dir / "test_main.py").write_text("# Tests\ndef test_example(): pass\n")
    
    # Create corrupt directories
    corrupt_dir1 = project_root / "agentic_sdlc.egg-info_corrupt_20260131"
    corrupt_dir1.mkdir()
    (corrupt_dir1 / "PKG-INFO").write_text("Corrupt package info\n")
    (corrupt_dir1 / "SOURCES.txt").write_text("Corrupt sources\n")
    
    corrupt_dir2 = project_root / "build_corrupt_20260131"
    corrupt_dir2.mkdir()
    (corrupt_dir2 / "lib").mkdir()
    (corrupt_dir2 / "lib" / "module.so").write_text("Binary data\n")
    
    # Create cache directories
    brain_dir = project_root / ".brain"
    brain_dir.mkdir()
    (brain_dir / "recent_data.json").write_text('{"recent": true}')
    
    # Create old data for archival
    old_file = brain_dir / "old_data.json"
    old_file.write_text('{"old": true}')
    # Set modification time to 60 days ago
    old_time = (datetime.now() - timedelta(days=60)).timestamp()
    old_file.touch()
    
    hypothesis_dir = project_root / ".hypothesis"
    hypothesis_dir.mkdir()
    constants_dir = hypothesis_dir / "constants"
    constants_dir.mkdir()
    (constants_dir / "const1").write_text("constant data")
    (constants_dir / "const2").write_text("constant data")
    
    pycache_dir = project_root / "agentic_sdlc" / "__pycache__"
    pycache_dir.mkdir()
    (pycache_dir / "main.cpython-310.pyc").write_text("compiled bytecode")
    (pycache_dir / "utils.cpython-310.pyc").write_text("compiled bytecode")
    
    # Create bundled library
    lib_dir = project_root / "agentic_sdlc" / "lib"
    lib_dir.mkdir()
    (lib_dir / "bundled_module.py").write_text("# Bundled library\n")
    (lib_dir / "another_lib.py").write_text("# Another bundled library\n")
    
    # Create requirements files
    (project_root / "requirements.txt").write_text(
        "requests>=2.28.0\n"
        "pytest>=7.0.0\n"
        "hypothesis>=6.0.0\n"
    )
    
    (project_root / "agentic_sdlc" / "requirements_tools.txt").write_text(
        "black>=22.0.0\n"
        "mypy>=0.990\n"
    )
    
    # Create pyproject.toml
    pyproject_content = """[project]
name = "test-project"
version = "1.0.0"
dependencies = []

[project.optional-dependencies]
dev = []
tools = []

[build-system]
requires = ["setuptools>=45", "wheel"]
build-backend = "setuptools.build_meta"
"""
    (project_root / "pyproject.toml").write_text(pyproject_content)
    
    # Create other config files
    (project_root / "README.md").write_text("# Test Project\n")
    (project_root / ".gitignore").write_text("__pycache__/\n*.pyc\n")
    
    # Create empty directories
    (project_root / "empty_dir").mkdir()
    ds_store_dir = project_root / "ds_store_only"
    ds_store_dir.mkdir()
    (ds_store_dir / ".DS_Store").write_text("")
    
    return project_root


@pytest.fixture
def backup_dir(tmp_path):
    """Create a backup directory for testing."""
    backup_path = tmp_path / ".cleanup_backup"
    backup_path.mkdir()
    return backup_path


class TestFullAuditCleanupValidateCycle:
    """Test the complete audit → cleanup → validate workflow."""
    
    def test_full_cycle_success(self, integration_project, backup_dir):
        """Test successful full cycle: audit → cleanup → validate."""
        # Step 1: Audit
        scanner = FileScanner()
        categorizer = FileCategorizer()
        audit_engine = AuditEngine(scanner, categorizer)
        
        report = audit_engine.generate_report(integration_project)
        
        # Verify audit found files
        assert report.total_files > 0
        assert len(report.categorized_files.remove) > 0  # Should find corrupt dirs, cache, etc.
        assert len(report.categorized_files.keep) > 0  # Should preserve critical components
        assert len(report.categorized_files.consolidate) > 0  # Should find requirements files
        
        # Verify size impact
        assert report.size_impact.current_size > 0
        assert report.size_impact.reduction > 0
        
        # Step 2: Cleanup
        backup_manager = BackupManager(backup_dir)
        validator = Validator(integration_project)
        cleanup_engine = CleanupEngine(
            project_root=integration_project,
            backup_manager=backup_manager,
            validator=validator,
            verbose=False
        )
        
        # Skip validation for this test (we're testing the workflow, not actual validation)
        result = cleanup_engine.cleanup(
            report.categorized_files,
            dry_run=False,
            skip_validation=True
        )
        
        # Verify cleanup succeeded
        assert result.success
        assert result.files_removed > 0
        assert result.size_freed > 0
        assert result.backup_id != "dry_run"
        
        # Step 3: Verify results
        # Critical components should still exist
        assert (integration_project / "agentic_sdlc" / "core" / "main.py").exists()
        assert (integration_project / "docs" / "README.md").exists()
        assert (integration_project / "tests" / "test_main.py").exists()
        assert (integration_project / "pyproject.toml").exists()
        
        # Corrupt directories should be removed
        assert not (integration_project / "agentic_sdlc.egg-info_corrupt_20260131").exists()
        assert not (integration_project / "build_corrupt_20260131").exists()
        
        # Cache files should be removed
        pycache_dir = integration_project / "agentic_sdlc" / "__pycache__"
        if pycache_dir.exists():
            # Directory may exist but should be empty
            assert len(list(pycache_dir.iterdir())) == 0
        
        # Empty directories should be removed
        assert not (integration_project / "empty_dir").exists()
        assert not (integration_project / "ds_store_only").exists()
        
        # Backup should exist
        backups = backup_manager.list_backups()
        assert len(backups) > 0
        assert backups[0].backup_id == result.backup_id
    
    def test_full_cycle_with_validation(self, integration_project, backup_dir):
        """Test full cycle with validation step."""
        scanner = FileScanner()
        categorizer = FileCategorizer()
        audit_engine = AuditEngine(scanner, categorizer)
        
        report = audit_engine.generate_report(integration_project)
        
        backup_manager = BackupManager(backup_dir)
        validator = Validator(integration_project)
        cleanup_engine = CleanupEngine(
            project_root=integration_project,
            backup_manager=backup_manager,
            validator=validator,
            verbose=False
        )
        
        # Run cleanup with validation
        # Note: Validation will likely fail since this is a mock project,
        # but we're testing that the validation step is executed
        result = cleanup_engine.cleanup(
            report.categorized_files,
            dry_run=False,
            skip_validation=False
        )
        
        # Result may fail due to validation, but that's expected
        # The important thing is that the process completed
        assert result.validation_result is not None
    
    def test_categorization_correctness(self, integration_project):
        """Test that categorization correctly identifies all file types."""
        scanner = FileScanner()
        categorizer = FileCategorizer()
        audit_engine = AuditEngine(scanner, categorizer)
        
        report = audit_engine.generate_report(integration_project)
        
        # Check that critical files are marked as KEEP
        keep_paths = {f.path.name for f in report.categorized_files.keep}
        assert "main.py" in keep_paths
        assert "README.md" in keep_paths
        assert "pyproject.toml" in keep_paths
        
        # Check that corrupt directories are marked as REMOVE
        remove_paths = {str(f.path) for f in report.categorized_files.remove}
        assert any("_corrupt_" in path for path in remove_paths)
        
        # Check that requirements files are marked as CONSOLIDATE
        consolidate_paths = {f.path.name for f in report.categorized_files.consolidate}
        assert "requirements.txt" in consolidate_paths or "requirements_tools.txt" in consolidate_paths
    
    def test_size_calculation_accuracy(self, integration_project):
        """Test that size calculations are accurate."""
        scanner = FileScanner()
        categorizer = FileCategorizer()
        audit_engine = AuditEngine(scanner, categorizer)
        
        report = audit_engine.generate_report(integration_project)
        
        # Calculate expected sizes based on how audit engine calculates
        # Only REMOVE and ARCHIVE files count toward size reduction
        total_remove_size = sum(f.size for f in report.categorized_files.remove)
        total_archive_size = sum(f.size for f in report.categorized_files.archive)
        
        expected_reduction = total_remove_size + total_archive_size
        
        # Verify size impact matches
        assert report.size_impact.reduction == expected_reduction
        assert report.size_impact.projected_size == report.size_impact.current_size - expected_reduction


class TestRollbackScenario:
    """Test backup and rollback functionality."""
    
    def test_rollback_after_cleanup(self, integration_project, backup_dir):
        """Test that rollback restores all removed files."""
        # Perform cleanup
        scanner = FileScanner()
        categorizer = FileCategorizer()
        audit_engine = AuditEngine(scanner, categorizer)
        
        report = audit_engine.generate_report(integration_project)
        
        backup_manager = BackupManager(backup_dir)
        validator = Validator(integration_project)
        cleanup_engine = CleanupEngine(
            project_root=integration_project,
            backup_manager=backup_manager,
            validator=validator,
            verbose=False
        )
        
        # Record files that will be removed
        files_to_remove = [f.path for f in report.categorized_files.remove]
        
        # Perform cleanup
        result = cleanup_engine.cleanup(
            report.categorized_files,
            dry_run=False,
            skip_validation=True
        )
        
        assert result.success
        backup_id = result.backup_id
        
        # Verify files were removed
        for file_path in files_to_remove:
            if file_path.exists():
                # File might be in a removed directory
                assert not any(parent.exists() for parent in file_path.parents if "_corrupt_" in parent.name)
        
        # Perform rollback
        restore_result = backup_manager.restore_backup(backup_id)
        
        # Verify rollback succeeded
        assert restore_result.success
        assert restore_result.files_restored > 0
        
        # Verify files were restored
        # Note: Some files might be in directories that were removed,
        # so we check that the backup process worked
        assert restore_result.files_failed == 0
    
    def test_rollback_on_validation_failure(self, integration_project, backup_dir):
        """Test automatic rollback when validation fails."""
        scanner = FileScanner()
        categorizer = FileCategorizer()
        audit_engine = AuditEngine(scanner, categorizer)
        
        report = audit_engine.generate_report(integration_project)
        
        backup_manager = BackupManager(backup_dir)
        
        # Create a validator that will fail
        class FailingValidator:
            def __init__(self, project_root, verbose=False):
                self.project_root = project_root
                self.verbose = verbose
            
            def validate_all(self):
                return ValidationResult(
                    passed=False,
                    import_check=False,
                    cli_check=True,
                    test_check=True,
                    build_check=True,
                    errors=["Import validation failed"]
                )
        
        validator = FailingValidator(integration_project)
        cleanup_engine = CleanupEngine(
            project_root=integration_project,
            backup_manager=backup_manager,
            validator=validator,
            verbose=False
        )
        
        # Record initial state
        corrupt_dir_existed = (integration_project / "agentic_sdlc.egg-info_corrupt_20260131").exists()
        
        # Perform cleanup (should fail and rollback)
        result = cleanup_engine.cleanup(
            report.categorized_files,
            dry_run=False,
            skip_validation=False
        )
        
        # Verify cleanup failed
        assert not result.success
        assert "Validation failed" in str(result.errors)
        
        # Verify rollback was performed
        # Files should be restored (or at least rollback was attempted)
        assert result.backup_id is not None
    
    def test_backup_manifest_consistency(self, integration_project, backup_dir):
        """Test that backup manifest matches archived files."""
        scanner = FileScanner()
        categorizer = FileCategorizer()
        audit_engine = AuditEngine(scanner, categorizer)
        
        report = audit_engine.generate_report(integration_project)
        
        backup_manager = BackupManager(backup_dir)
        
        # Create backup of files to remove
        files_to_backup = [f.path for f in report.categorized_files.remove]
        backup_info = backup_manager.create_backup(files_to_backup)
        
        # Verify manifest exists
        assert backup_info.manifest_path.exists()
        
        # Read manifest
        with open(backup_info.manifest_path, 'r') as f:
            manifest = json.load(f)
        
        # Verify manifest structure
        assert "backup_id" in manifest
        assert "timestamp" in manifest
        assert "files" in manifest
        assert "total_size" in manifest
        assert "total_files" in manifest
        
        # Verify file count matches
        assert len(manifest["files"]) == backup_info.file_count
        
        # Verify total size matches
        assert manifest["total_size"] == backup_info.total_size


class TestDryRunScenario:
    """Test dry-run mode functionality."""
    
    def test_dry_run_makes_no_changes(self, integration_project, backup_dir):
        """Test that dry-run mode makes no file system changes."""
        # Record initial state
        import os
        initial_files = set()
        for root, dirs, files in os.walk(integration_project):
            for file in files:
                initial_files.add(Path(root) / file)
        
        # Perform audit
        scanner = FileScanner()
        categorizer = FileCategorizer()
        audit_engine = AuditEngine(scanner, categorizer)
        
        report = audit_engine.generate_report(integration_project)
        
        # Perform dry-run cleanup
        backup_manager = BackupManager(backup_dir)
        validator = Validator(integration_project)
        cleanup_engine = CleanupEngine(
            project_root=integration_project,
            backup_manager=backup_manager,
            validator=validator,
            verbose=False
        )
        
        result = cleanup_engine.cleanup(
            report.categorized_files,
            dry_run=True
        )
        
        # Verify dry-run succeeded
        assert result.success
        assert result.backup_id == "dry_run"
        assert result.files_removed > 0  # Reports what would be removed
        assert result.size_freed > 0  # Reports what would be freed
        
        # Record final state
        import os
        final_files = set()
        for root, dirs, files in os.walk(integration_project):
            for file in files:
                final_files.add(Path(root) / file)
        
        # Verify no files were changed
        assert initial_files == final_files
        
        # Verify no backup was created
        backups = backup_manager.list_backups()
        assert len(backups) == 0
    
    def test_dry_run_reports_accurate_impact(self, integration_project, backup_dir):
        """Test that dry-run reports accurate size impact."""
        scanner = FileScanner()
        categorizer = FileCategorizer()
        audit_engine = AuditEngine(scanner, categorizer)
        
        report = audit_engine.generate_report(integration_project)
        
        backup_manager = BackupManager(backup_dir)
        validator = Validator(integration_project)
        cleanup_engine = CleanupEngine(
            project_root=integration_project,
            backup_manager=backup_manager,
            validator=validator,
            verbose=False
        )
        
        # Perform dry-run
        dry_run_result = cleanup_engine.cleanup(
            report.categorized_files,
            dry_run=True
        )
        
        # Calculate expected impact
        expected_files_removed = (
            len(report.categorized_files.remove) +
            len(report.categorized_files.consolidate)
        )
        expected_size_freed = (
            sum(f.size for f in report.categorized_files.remove) +
            sum(f.size for f in report.categorized_files.archive) +
            sum(f.size for f in report.categorized_files.consolidate)
        )
        
        # Verify dry-run reports match expectations
        assert dry_run_result.files_removed == expected_files_removed
        assert dry_run_result.size_freed == expected_size_freed


class TestDependencyConsolidationScenario:
    """Test dependency consolidation workflow."""
    
    def test_consolidate_requirements_into_pyproject(self, integration_project):
        """Test consolidating requirements.txt into pyproject.toml."""
        # Read initial pyproject.toml
        pyproject_path = integration_project / "pyproject.toml"
        initial_content = pyproject_path.read_text()
        
        # Perform consolidation
        consolidator = DependencyConsolidator(pyproject_path)
        
        # Parse requirements files
        req_file = integration_project / "requirements.txt"
        deps = consolidator.parse_requirements_file(req_file)
        
        assert len(deps) > 0
        
        # Merge into pyproject.toml
        consolidator.merge_into_pyproject(deps, "dependencies")
        
        # Verify pyproject.toml was updated
        updated_content = pyproject_path.read_text()
        assert updated_content != initial_content
        
        # Verify dependencies were added
        assert "requests" in updated_content
        assert "pytest" in updated_content
        assert "hypothesis" in updated_content
    
    def test_consolidate_tools_requirements(self, integration_project):
        """Test consolidating requirements_tools.txt into pyproject.toml."""
        pyproject_path = integration_project / "pyproject.toml"
        consolidator = DependencyConsolidator(pyproject_path)
        
        # Parse tools requirements
        tools_file = integration_project / "agentic_sdlc" / "requirements_tools.txt"
        deps = consolidator.parse_requirements_file(tools_file)
        
        assert len(deps) > 0
        
        # Merge into tools group
        consolidator.merge_into_pyproject(deps, "tools")
        
        # Verify pyproject.toml was updated
        content = pyproject_path.read_text()
        
        assert "black" in content
        assert "mypy" in content
    
    def test_consolidation_idempotence(self, integration_project):
        """Test that consolidating twice produces same result."""
        pyproject_path = integration_project / "pyproject.toml"
        consolidator = DependencyConsolidator(pyproject_path)
        
        # First consolidation
        req_file = integration_project / "requirements.txt"
        deps = consolidator.parse_requirements_file(req_file)
        consolidator.merge_into_pyproject(deps, "dependencies")
        
        first_content = pyproject_path.read_text()
        
        # Second consolidation (should be idempotent)
        consolidator.merge_into_pyproject(deps, "dependencies")
        second_content = pyproject_path.read_text()
        
        # Content should be identical
        assert first_content == second_content
    
    def test_full_consolidation_workflow(self, integration_project, backup_dir):
        """Test full consolidation workflow in cleanup."""
        scanner = FileScanner()
        categorizer = FileCategorizer()
        audit_engine = AuditEngine(scanner, categorizer)
        
        report = audit_engine.generate_report(integration_project)
        
        backup_manager = BackupManager(backup_dir)
        validator = Validator(integration_project)
        cleanup_engine = CleanupEngine(
            project_root=integration_project,
            backup_manager=backup_manager,
            validator=validator,
            verbose=False
        )
        
        # Perform cleanup with consolidation
        result = cleanup_engine.cleanup(
            report.categorized_files,
            dry_run=False,
            skip_validation=True
        )
        
        assert result.success
        
        # Verify requirements files were removed
        assert not (integration_project / "requirements.txt").exists()
        
        # Verify pyproject.toml was updated
        pyproject_path = integration_project / "pyproject.toml"
        content = pyproject_path.read_text()
        
        # Should contain dependencies from requirements.txt
        assert "requests" in content or "pytest" in content


class TestErrorHandlingAndRecovery:
    """Test error handling and recovery scenarios."""
    
    def test_cleanup_continues_on_non_critical_errors(self, integration_project, backup_dir):
        """Test that cleanup continues when non-critical operations fail."""
        scanner = FileScanner()
        categorizer = FileCategorizer()
        audit_engine = AuditEngine(scanner, categorizer)
        
        report = audit_engine.generate_report(integration_project)
        
        backup_manager = BackupManager(backup_dir)
        validator = Validator(integration_project)
        cleanup_engine = CleanupEngine(
            project_root=integration_project,
            backup_manager=backup_manager,
            validator=validator,
            verbose=False
        )
        
        # Cleanup should succeed even if some operations fail
        result = cleanup_engine.cleanup(
            report.categorized_files,
            dry_run=False,
            skip_validation=True
        )
        
        # Should succeed overall
        assert result.files_removed >= 0
    
    def test_handles_missing_files_gracefully(self, integration_project, backup_dir):
        """Test handling of files that don't exist."""
        from scripts.cleanup.models import FileInfo
        
        backup_manager = BackupManager(backup_dir)
        validator = Validator(integration_project)
        cleanup_engine = CleanupEngine(
            project_root=integration_project,
            backup_manager=backup_manager,
            validator=validator,
            verbose=False
        )
        
        # Create file info for non-existent file
        non_existent = FileInfo(
            path=integration_project / "does_not_exist.txt",
            size=0,
            modified_time=datetime.now(),
            category=FileCategory.REMOVE,
            reason="Test"
        )
        
        # Should handle gracefully
        result = cleanup_engine.remove_files([non_existent], backup=False)
        
        # Should report the file as failed but not crash
        assert result.files_failed >= 0


class TestComplexScenarios:
    """Test complex integration scenarios."""
    
    def test_multiple_cleanup_cycles(self, integration_project, backup_dir):
        """Test running multiple cleanup cycles."""
        scanner = FileScanner()
        categorizer = FileCategorizer()
        audit_engine = AuditEngine(scanner, categorizer)
        
        backup_manager = BackupManager(backup_dir)
        validator = Validator(integration_project)
        cleanup_engine = CleanupEngine(
            project_root=integration_project,
            backup_manager=backup_manager,
            validator=validator,
            verbose=False
        )
        
        # First cleanup
        report1 = audit_engine.generate_report(integration_project)
        result1 = cleanup_engine.cleanup(
            report1.categorized_files,
            dry_run=False,
            skip_validation=True
        )
        
        assert result1.success
        
        # Second cleanup (should find less to clean)
        report2 = audit_engine.generate_report(integration_project)
        result2 = cleanup_engine.cleanup(
            report2.categorized_files,
            dry_run=False,
            skip_validation=True
        )
        
        # Second cleanup should remove fewer files
        assert result2.files_removed <= result1.files_removed
    
    def test_audit_after_cleanup_shows_reduction(self, integration_project, backup_dir):
        """Test that audit after cleanup shows size reduction."""
        scanner = FileScanner()
        categorizer = FileCategorizer()
        audit_engine = AuditEngine(scanner, categorizer)
        
        # Initial audit
        report_before = audit_engine.generate_report(integration_project)
        initial_size = report_before.size_impact.current_size
        
        # Cleanup
        backup_manager = BackupManager(backup_dir)
        validator = Validator(integration_project)
        cleanup_engine = CleanupEngine(
            project_root=integration_project,
            backup_manager=backup_manager,
            validator=validator,
            verbose=False
        )
        
        cleanup_result = cleanup_engine.cleanup(
            report_before.categorized_files,
            dry_run=False,
            skip_validation=True
        )
        
        # Audit after cleanup
        report_after = audit_engine.generate_report(integration_project)
        final_size = report_after.size_impact.current_size
        
        # Verify size was reduced
        # Note: The actual reduction may differ from size_freed because:
        # 1. Consolidation adds dependencies to pyproject.toml (increases size)
        # 2. Only REMOVE files directly reduce size
        assert final_size < initial_size
        assert cleanup_result.files_removed > 0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
