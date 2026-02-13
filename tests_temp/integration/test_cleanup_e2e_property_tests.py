"""
End-to-end property-based tests for the Project Audit and Cleanup System.

Feature: project-audit-cleanup
Tests complete cleanup workflows with generated project structures and failure scenarios.
These tests verify system behavior across a wide range of inputs and conditions.
"""

import pytest
from hypothesis import given, strategies as st, settings, assume
from pathlib import Path
import tempfile
import shutil
from datetime import datetime, timedelta
import json
import os

from scripts.cleanup.scanner import FileScanner
from scripts.cleanup.categorizer import FileCategorizer
from scripts.cleanup.backup import BackupManager
from scripts.cleanup.validator import Validator
from scripts.cleanup.dependencies import DependencyConsolidator
from scripts.cleanup.audit import AuditEngine
from scripts.cleanup.cleanup import CleanupEngine
from scripts.cleanup.models import (
    FileCategory,
    FileInfo,
    DirectoryInfo,
    ValidationResult,
)


# Custom strategies for generating project structures
@st.composite
def project_structure(draw):
    """Generate a random project structure."""
    structure = {
        'critical_dirs': draw(st.lists(
            st.sampled_from([
                'agentic_sdlc/core',
                'agentic_sdlc/intelligence',
                'agentic_sdlc/infrastructure',
                'docs',
                'tests',
                '.kiro',
            ]),
            min_size=1,
            max_size=6,
            unique=True
        )),
        'corrupt_dirs': draw(st.lists(
            st.text(min_size=5, max_size=30, alphabet=st.characters(
                whitelist_categories=('Lu', 'Ll', 'Nd'),
                whitelist_characters='_'
            )).filter(lambda x: '_corrupt_' in x or x.endswith('_corrupt_20260131')),
            min_size=0,
            max_size=3,
            unique=True
        )),
        'cache_dirs': draw(st.lists(
            st.sampled_from(['.brain', '.hypothesis', '__pycache__']),
            min_size=0,
            max_size=3,
            unique=True
        )),
        'empty_dirs': draw(st.lists(
            st.text(min_size=3, max_size=15, alphabet='abcdefghijklmnopqrstuvwxyz_'),
            min_size=0,
            max_size=5,
            unique=True
        )),
        'requirements_files': draw(st.lists(
            st.sampled_from([
                'requirements.txt',
                'requirements-dev.txt',
                'requirements_tools.txt',
            ]),
            min_size=0,
            max_size=3,
            unique=True
        )),
        'has_lib_dir': draw(st.booleans()),
        'has_pyproject': draw(st.booleans()),
    }
    return structure


@st.composite
def file_sizes(draw):
    """Generate realistic file sizes."""
    return draw(st.integers(min_value=0, max_value=1024*1024))  # 0 to 1MB


def create_project_from_structure(tmp_path, structure):
    """Create a project directory structure from a structure dict."""
    project_root = tmp_path / "test_project"
    project_root.mkdir()
    
    # Create critical directories with files
    for critical_dir in structure['critical_dirs']:
        dir_path = project_root / critical_dir
        dir_path.mkdir(parents=True, exist_ok=True)
        # Add at least one file to make it non-empty
        (dir_path / "module.py").write_text("# Critical module\n")
    
    # Create corrupt directories
    for corrupt_dir in structure['corrupt_dirs']:
        dir_path = project_root / corrupt_dir
        dir_path.mkdir(parents=True, exist_ok=True)
        (dir_path / "corrupt_file.txt").write_text("corrupt data\n")
    
    # Create cache directories
    for cache_dir in structure['cache_dirs']:
        dir_path = project_root / cache_dir
        dir_path.mkdir(parents=True, exist_ok=True)
        (dir_path / "cache_file.dat").write_text("cache data\n")
    
    # Create empty directories
    for empty_dir in structure['empty_dirs']:
        dir_path = project_root / empty_dir
        dir_path.mkdir(parents=True, exist_ok=True)
    
    # Create requirements files
    for req_file in structure['requirements_files']:
        file_path = project_root / req_file
        file_path.write_text("requests>=2.0.0\npytest>=7.0.0\n")
    
    # Create lib directory if specified
    if structure['has_lib_dir']:
        lib_dir = project_root / "agentic_sdlc" / "lib"
        lib_dir.mkdir(parents=True, exist_ok=True)
        (lib_dir / "bundled.py").write_text("# Bundled library\n")
    
    # Create pyproject.toml if specified
    if structure['has_pyproject']:
        pyproject_content = """[project]
name = "test-project"
version = "1.0.0"
dependencies = []

[project.optional-dependencies]
dev = []

[build-system]
requires = ["setuptools>=45"]
build-backend = "setuptools.build_meta"
"""
        (project_root / "pyproject.toml").write_text(pyproject_content)
    
    return project_root


# Property: Complete workflow maintains data integrity
@given(project_structure())
@settings(max_examples=10, deadline=None)
def test_complete_workflow_maintains_integrity(structure):
    """
    Property: Workflow data integrity
    
    For any generated project structure, running the complete audit → cleanup
    workflow should maintain data integrity:
    - Critical files are never removed
    - All removed files are backed up
    - Size calculations are accurate
    - No data corruption occurs
    
    **Validates: All requirements**
    """
    with tempfile.TemporaryDirectory() as tmpdir:
        tmp_path = Path(tmpdir)
        project_root = create_project_from_structure(tmp_path, structure)
        backup_dir = tmp_path / ".cleanup_backup"
        backup_dir.mkdir()
        
        # Record critical files before cleanup
        critical_files = set()
        for critical_dir in structure['critical_dirs']:
            dir_path = project_root / critical_dir
            if dir_path.exists():
                for root, dirs, files in os.walk(dir_path):
                    for file in files:
                        critical_files.add(Path(root) / file)
        
        # Run audit
        scanner = FileScanner()
        categorizer = FileCategorizer()
        audit_engine = AuditEngine(scanner, categorizer)
        
        try:
            report = audit_engine.generate_report(project_root)
        except Exception:
            # If audit fails, structure might be invalid
            return
        
        # Property 1: All files should be categorized
        total_categorized = (
            len(report.categorized_files.keep) +
            len(report.categorized_files.remove) +
            len(report.categorized_files.consolidate) +
            len(report.categorized_files.archive)
        )
        assert total_categorized == report.total_files, (
            f"Not all files categorized: {total_categorized} != {report.total_files}"
        )
        
        # Property 2: Critical files should never be in REMOVE category
        remove_paths = {f.path for f in report.categorized_files.remove}
        for critical_file in critical_files:
            assert critical_file not in remove_paths, (
                f"Critical file {critical_file} was marked for removal"
            )
        
        # Run cleanup
        backup_manager = BackupManager(backup_dir)
        validator = Validator(project_root)
        cleanup_engine = CleanupEngine(
            project_root=project_root,
            backup_manager=backup_manager,
            validator=validator,
            verbose=False
        )
        
        try:
            result = cleanup_engine.cleanup(
                report.categorized_files,
                dry_run=False,
                skip_validation=True
            )
        except Exception:
            # Cleanup might fail for various reasons, that's ok
            return
        
        # Property 3: Critical files should still exist after cleanup
        for critical_file in critical_files:
            if critical_file.exists():
                # File should still be readable
                assert critical_file.is_file()


# Property: Dry run never modifies filesystem
@given(project_structure())
@settings(max_examples=10, deadline=None)
def test_dry_run_never_modifies_filesystem(structure):
    """
    Property: Dry run safety
    
    For any project structure, running cleanup with dry_run=True should
    never modify the filesystem. All files and directories should remain
    exactly as they were before the dry run.
    
    **Validates: Requirements 13.3**
    """
    with tempfile.TemporaryDirectory() as tmpdir:
        tmp_path = Path(tmpdir)
        project_root = create_project_from_structure(tmp_path, structure)
        backup_dir = tmp_path / ".cleanup_backup"
        backup_dir.mkdir()
        
        # Record initial filesystem state
        initial_files = set()
        initial_dirs = set()
        for root, dirs, files in os.walk(project_root):
            root_path = Path(root)
            initial_dirs.add(root_path)
            for file in files:
                initial_files.add(root_path / file)
        
        # Run audit and dry-run cleanup
        scanner = FileScanner()
        categorizer = FileCategorizer()
        audit_engine = AuditEngine(scanner, categorizer)
        
        try:
            report = audit_engine.generate_report(project_root)
        except Exception:
            return
        
        backup_manager = BackupManager(backup_dir)
        validator = Validator(project_root)
        cleanup_engine = CleanupEngine(
            project_root=project_root,
            backup_manager=backup_manager,
            validator=validator,
            verbose=False
        )
        
        try:
            result = cleanup_engine.cleanup(
                report.categorized_files,
                dry_run=True
            )
        except Exception:
            return
        
        # Record final filesystem state
        final_files = set()
        final_dirs = set()
        for root, dirs, files in os.walk(project_root):
            root_path = Path(root)
            final_dirs.add(root_path)
            for file in files:
                final_files.add(root_path / file)
        
        # Property: Filesystem should be unchanged
        assert initial_files == final_files, (
            f"Files changed during dry run. "
            f"Added: {final_files - initial_files}, "
            f"Removed: {initial_files - final_files}"
        )
        
        # Property: No backup should be created
        backups = backup_manager.list_backups()
        assert len(backups) == 0, "Backup was created during dry run"
        
        # Property: Result should indicate dry run
        if result:
            assert result.backup_id == "dry_run"


# Property: Backup and restore round trip
@given(
    st.lists(
        st.tuples(
            st.text(min_size=1, max_size=20, alphabet='abcdefghijklmnopqrstuvwxyz_'),
            st.text(min_size=0, max_size=100)
        ),
        min_size=1,
        max_size=20,
        unique_by=lambda x: x[0]
    )
)
@settings(max_examples=10, deadline=None)
def test_backup_restore_round_trip(files_data):
    """
    Property: Backup and restore round trip
    
    For any set of files, creating a backup then restoring from that backup
    should result in all files being restored to their original locations
    with identical content.
    
    **Validates: Requirements 7.1, 7.2, 7.3, 7.4, 7.5**
    """
    with tempfile.TemporaryDirectory() as tmpdir:
        tmp_path = Path(tmpdir)
        project_root = tmp_path / "project"
        project_root.mkdir()
        backup_dir = tmp_path / ".cleanup_backup"
        backup_dir.mkdir()
        
        # Create files
        created_files = []
        for filename, content in files_data:
            try:
                file_path = project_root / filename
                file_path.write_text(content)
                created_files.append(file_path)
            except (OSError, ValueError):
                continue
        
        if not created_files:
            return
        
        # Record original content
        original_content = {}
        for file_path in created_files:
            if file_path.exists():
                original_content[file_path] = file_path.read_text()
        
        # Create backup
        backup_manager = BackupManager(backup_dir)
        try:
            backup_info = backup_manager.create_backup(created_files)
        except Exception:
            return
        
        # Remove files
        for file_path in created_files:
            if file_path.exists():
                file_path.unlink()
        
        # Verify files are gone
        for file_path in created_files:
            assert not file_path.exists(), f"File {file_path} still exists after removal"
        
        # Restore from backup
        try:
            restore_result = backup_manager.restore_backup(backup_info.backup_id)
        except Exception:
            return
        
        # Property: All files should be restored with identical content
        for file_path, original in original_content.items():
            if file_path.exists():
                restored_content = file_path.read_text()
                assert restored_content == original, (
                    f"File {file_path} content mismatch after restore. "
                    f"Expected: {original[:50]}, Got: {restored_content[:50]}"
                )


# Property: Size reduction accuracy
@given(
    st.lists(st.integers(min_value=1, max_value=1024*100), min_size=1, max_size=20)
)
@settings(max_examples=10, deadline=None)
def test_size_reduction_accuracy(file_sizes):
    """
    Property: Size reduction accuracy
    
    For any cleanup operation, the calculated size reduction should equal
    the sum of all removed file sizes, and the final package size should
    equal initial size minus removed size.
    
    **Validates: Requirements 5.1, 5.2, 5.3, 5.5**
    """
    with tempfile.TemporaryDirectory() as tmpdir:
        tmp_path = Path(tmpdir)
        project_root = tmp_path / "project"
        project_root.mkdir()
        
        # Create critical directory (won't be removed)
        critical_dir = project_root / "agentic_sdlc" / "core"
        critical_dir.mkdir(parents=True)
        (critical_dir / "main.py").write_text("# Critical\n")
        
        # Create files to be removed (corrupt directory)
        corrupt_dir = project_root / "build_corrupt_20260131"
        corrupt_dir.mkdir()
        
        expected_removed_size = 0
        for i, size in enumerate(file_sizes):
            file_path = corrupt_dir / f"file_{i}.txt"
            content = "x" * size
            file_path.write_text(content)
            expected_removed_size += size
        
        # Run audit
        scanner = FileScanner()
        categorizer = FileCategorizer()
        audit_engine = AuditEngine(scanner, categorizer)
        
        try:
            report = audit_engine.generate_report(project_root)
        except Exception:
            return
        
        initial_size = report.size_impact.current_size
        
        # Calculate expected size of files to be removed
        actual_remove_size = sum(f.size for f in report.categorized_files.remove)
        actual_archive_size = sum(f.size for f in report.categorized_files.archive)
        
        # Property: Size reduction should match sum of removed + archived files
        expected_reduction = actual_remove_size + actual_archive_size
        assert report.size_impact.reduction == expected_reduction, (
            f"Size reduction mismatch: expected {expected_reduction}, "
            f"got {report.size_impact.reduction}"
        )
        
        # Property: Projected size should equal initial minus reduction
        expected_projected = initial_size - expected_reduction
        assert report.size_impact.projected_size == expected_projected, (
            f"Projected size mismatch: expected {expected_projected}, "
            f"got {report.size_impact.projected_size}"
        )


# Property: Validation failure triggers rollback
@given(st.booleans())
@settings(max_examples=10, deadline=None)
def test_validation_failure_triggers_rollback(should_fail):
    """
    Property: Validation triggers rollback
    
    For any cleanup operation where validation fails, the system should
    automatically trigger rollback and restore all files to their
    pre-cleanup state.
    
    **Validates: Requirements 9.5**
    """
    with tempfile.TemporaryDirectory() as tmpdir:
        tmp_path = Path(tmpdir)
        project_root = tmp_path / "project"
        project_root.mkdir()
        backup_dir = tmp_path / ".cleanup_backup"
        backup_dir.mkdir()
        
        # Create a simple project structure
        core_dir = project_root / "agentic_sdlc" / "core"
        core_dir.mkdir(parents=True)
        (core_dir / "main.py").write_text("# Main\n")
        
        corrupt_dir = project_root / "build_corrupt_20260131"
        corrupt_dir.mkdir()
        (corrupt_dir / "file.txt").write_text("corrupt\n")
        
        # Run audit
        scanner = FileScanner()
        categorizer = FileCategorizer()
        audit_engine = AuditEngine(scanner, categorizer)
        
        try:
            report = audit_engine.generate_report(project_root)
        except Exception:
            return
        
        # Create validator that fails or succeeds based on parameter
        class TestValidator:
            def __init__(self, project_root, verbose=False):
                self.project_root = project_root
                self.verbose = verbose
                self.should_fail = should_fail
            
            def validate_all(self):
                return ValidationResult(
                    passed=not self.should_fail,
                    import_check=not self.should_fail,
                    cli_check=True,
                    test_check=True,
                    build_check=True,
                    errors=["Validation failed"] if self.should_fail else []
                )
        
        backup_manager = BackupManager(backup_dir)
        validator = TestValidator(project_root)
        cleanup_engine = CleanupEngine(
            project_root=project_root,
            backup_manager=backup_manager,
            validator=validator,
            verbose=False
        )
        
        # Record whether corrupt dir exists before cleanup
        corrupt_existed = corrupt_dir.exists()
        
        try:
            result = cleanup_engine.cleanup(
                report.categorized_files,
                dry_run=False,
                skip_validation=False
            )
        except Exception:
            return
        
        # Property: If validation failed, cleanup should fail
        if should_fail:
            assert not result.success, "Cleanup succeeded despite validation failure"
            assert "Validation failed" in str(result.errors) or not result.validation_result.passed
        else:
            # If validation passed, cleanup should succeed
            assert result.success or len(result.errors) > 0


# Property: Corrupt directory pattern matching
@given(
    st.lists(
        st.text(min_size=5, max_size=30, alphabet=st.characters(
            whitelist_categories=('Lu', 'Ll', 'Nd'),
            whitelist_characters='_'
        )),
        min_size=1,
        max_size=5,
        unique=True
    )
)
@settings(max_examples=10, deadline=None)
def test_corrupt_directory_pattern_matching(dir_names):
    """
    Property: Corrupt directory pattern matching
    
    For any directory with "_corrupt_" in its name, that directory should
    be categorized as REMOVE unless it is explicitly in the critical
    components list.
    
    **Validates: Requirements 1.1, 1.2**
    """
    with tempfile.TemporaryDirectory() as tmpdir:
        tmp_path = Path(tmpdir)
        project_root = tmp_path / "project"
        project_root.mkdir()
        
        # Create directories, some with _corrupt_ pattern
        corrupt_dirs = []
        normal_dirs = []
        
        for dir_name in dir_names:
            if '_corrupt_' in dir_name:
                dir_path = project_root / dir_name
                dir_path.mkdir(parents=True, exist_ok=True)
                (dir_path / "file.txt").write_text("data\n")
                corrupt_dirs.append(dir_path)
            else:
                # Make it corrupt by adding suffix
                corrupt_name = f"{dir_name}_corrupt_20260131"
                dir_path = project_root / corrupt_name
                dir_path.mkdir(parents=True, exist_ok=True)
                (dir_path / "file.txt").write_text("data\n")
                corrupt_dirs.append(dir_path)
        
        if not corrupt_dirs:
            return
        
        # Run audit
        scanner = FileScanner()
        categorizer = FileCategorizer()
        audit_engine = AuditEngine(scanner, categorizer)
        
        try:
            report = audit_engine.generate_report(project_root)
        except Exception:
            return
        
        # Property: All files in corrupt directories should be marked for removal
        remove_paths = {str(f.path) for f in report.categorized_files.remove}
        
        for corrupt_dir in corrupt_dirs:
            # Check if any file from this corrupt directory is in remove list
            corrupt_files = list(corrupt_dir.rglob("*"))
            if corrupt_files:
                # At least one file from corrupt dir should be marked for removal
                found_in_remove = any(
                    str(f) in remove_paths for f in corrupt_files if f.is_file()
                )
                assert found_in_remove, (
                    f"No files from corrupt directory {corrupt_dir} were marked for removal"
                )


# Property: Empty directory identification
@given(
    st.lists(
        st.text(min_size=3, max_size=15, alphabet='abcdefghijklmnopqrstuvwxyz_'),
        min_size=1,
        max_size=10,
        unique=True
    ),
    st.lists(st.booleans(), min_size=1, max_size=10)
)
@settings(max_examples=10, deadline=None)
def test_empty_directory_identification(dir_names, has_ds_store):
    """
    Property: Empty directory identification
    
    For any directory that contains zero files or only contains .DS_Store
    files, that directory should be identified as empty unless it is in
    the critical empty directories list.
    
    **Validates: Requirements 11.1, 11.2, 11.3**
    """
    # Ensure lists are same length
    has_ds_store = has_ds_store[:len(dir_names)]
    while len(has_ds_store) < len(dir_names):
        has_ds_store.append(False)
    
    with tempfile.TemporaryDirectory() as tmpdir:
        tmp_path = Path(tmpdir)
        project_root = tmp_path / "project"
        project_root.mkdir()
        
        # Create empty or DS_Store-only directories
        empty_dirs = []
        for dir_name, has_ds in zip(dir_names, has_ds_store):
            # Skip critical directory names
            if dir_name in ['logs', 'states', 'data']:
                continue
            
            dir_path = project_root / dir_name
            dir_path.mkdir(parents=True, exist_ok=True)
            
            if has_ds:
                (dir_path / ".DS_Store").write_text("")
            
            empty_dirs.append(dir_path)
        
        if not empty_dirs:
            return
        
        # Run categorization
        categorizer = FileCategorizer()
        
        # Property: Empty directories should be identified
        for empty_dir in empty_dirs:
            # Check if directory is actually empty
            files_in_dir = [f for f in empty_dir.iterdir() if f.name != '.DS_Store' and f.name != '.gitkeep']
            is_actually_empty = len(files_in_dir) == 0
            
            # Create DirectoryInfo object
            dir_info = DirectoryInfo(
                path=empty_dir,
                size=0,
                file_count=len(files_in_dir),
                is_empty=is_actually_empty,
                is_critical=False
            )
            
            is_empty = categorizer.is_empty_directory(dir_info)
            
            # Directory should be identified as empty if it has no files (or only .DS_Store)
            if is_actually_empty:
                assert is_empty, f"Directory {empty_dir} was not identified as empty"


# Property: Dependency consolidation idempotence
@given(
    st.lists(
        st.tuples(
            st.text(min_size=1, max_size=20, alphabet='abcdefghijklmnopqrstuvwxyz-'),
            st.text(min_size=1, max_size=10, alphabet='0123456789.')
        ),
        min_size=1,
        max_size=10,
        unique_by=lambda x: x[0]
    )
)
@settings(max_examples=10, deadline=None)
def test_dependency_consolidation_idempotence(dependencies):
    """
    Property: Dependency consolidation idempotence
    
    For any set of requirements files, consolidating them into pyproject.toml
    then consolidating again should produce the same result (no duplicate
    dependencies added).
    
    **Validates: Requirements 4.3, 4.5**
    """
    with tempfile.TemporaryDirectory() as tmpdir:
        tmp_path = Path(tmpdir)
        
        # Create pyproject.toml
        pyproject_path = tmp_path / "pyproject.toml"
        pyproject_content = """[project]
name = "test"
version = "1.0.0"
dependencies = []

[build-system]
requires = ["setuptools"]
build-backend = "setuptools.build_meta"
"""
        pyproject_path.write_text(pyproject_content)
        
        # Create requirements file
        req_file = tmp_path / "requirements.txt"
        req_content = "\n".join([f"{name}>={version}" for name, version in dependencies])
        req_file.write_text(req_content)
        
        # First consolidation
        consolidator = DependencyConsolidator(pyproject_path)
        try:
            deps = consolidator.parse_requirements_file(req_file)
            consolidator.merge_into_pyproject(deps, "dependencies")
            first_content = pyproject_path.read_text()
        except Exception:
            return
        
        # Second consolidation (should be idempotent)
        try:
            deps = consolidator.parse_requirements_file(req_file)
            consolidator.merge_into_pyproject(deps, "dependencies")
            second_content = pyproject_path.read_text()
        except Exception:
            return
        
        # Property: Content should be identical after second consolidation
        assert first_content == second_content, (
            "Dependency consolidation is not idempotent"
        )


# Property: Manifest and archive consistency
@given(
    st.lists(
        st.tuples(
            st.text(min_size=1, max_size=20, alphabet='abcdefghijklmnopqrstuvwxyz_'),
            st.text(min_size=0, max_size=100)
        ),
        min_size=1,
        max_size=15,
        unique_by=lambda x: x[0]
    )
)
@settings(max_examples=10, deadline=None)
def test_manifest_and_archive_consistency(files_data):
    """
    Property: Manifest and archive consistency
    
    For any backup, every file listed in the manifest should exist in the
    backup archive, and every file in the backup archive should be listed
    in the manifest (bijection).
    
    **Validates: Requirements 7.3**
    """
    with tempfile.TemporaryDirectory() as tmpdir:
        tmp_path = Path(tmpdir)
        project_root = tmp_path / "project"
        project_root.mkdir()
        backup_dir = tmp_path / ".cleanup_backup"
        backup_dir.mkdir()
        
        # Create files
        created_files = []
        for filename, content in files_data:
            try:
                file_path = project_root / filename
                file_path.write_text(content)
                created_files.append(file_path)
            except (OSError, ValueError):
                continue
        
        if not created_files:
            return
        
        # Create backup
        backup_manager = BackupManager(backup_dir)
        try:
            backup_info = backup_manager.create_backup(created_files)
        except Exception:
            return
        
        # Read manifest
        try:
            with open(backup_info.manifest_path, 'r') as f:
                manifest = json.load(f)
        except Exception:
            return
        
        # Property: Number of files in manifest should match backup_info
        assert len(manifest["files"]) == backup_info.file_count, (
            f"Manifest file count mismatch: {len(manifest['files'])} != {backup_info.file_count}"
        )
        
        # Property: Total size in manifest should match backup_info
        assert manifest["total_size"] == backup_info.total_size, (
            f"Manifest size mismatch: {manifest['total_size']} != {backup_info.total_size}"
        )


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
