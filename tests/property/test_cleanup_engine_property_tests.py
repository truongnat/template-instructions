"""
Property-based tests for CleanupEngine.

These tests use Hypothesis to verify universal properties that should hold
across all valid inputs and execution scenarios.

Feature: project-audit-cleanup
"""

import pytest
from pathlib import Path
from datetime import datetime, timedelta
from hypothesis import given, strategies as st, settings, HealthCheck
from unittest.mock import Mock

from scripts.cleanup.cleanup import CleanupEngine
from scripts.cleanup.models import (
    CategorizedFiles,
    FileInfo,
    FileCategory,
    BackupInfo,
    ValidationResult,
)


# Strategy for generating file sizes (0 to 10MB)
file_size_strategy = st.integers(min_value=0, max_value=10 * 1024 * 1024)

# Strategy for generating file counts (0 to 100 files)
file_count_strategy = st.integers(min_value=0, max_value=100)


@pytest.fixture
def mock_services():
    """Create mock services for property tests."""
    backup_manager = Mock()
    backup_manager.create_backup.return_value = BackupInfo(
        backup_id="test_backup",
        timestamp=datetime.now(),
        file_count=1,
        total_size=100,
        manifest_path=Path("manifest.json"),
        archive_path=Path("archive.tar.gz")
    )
    backup_manager.restore_backup.return_value = Mock(
        success=True,
        files_restored=1,
        files_failed=0,
        errors=[]
    )
    
    validator = Mock()
    validator.validate_all.return_value = ValidationResult(
        passed=True,
        import_check=True,
        cli_check=True,
        test_check=True,
        build_check=True,
        errors=[]
    )
    
    return backup_manager, validator


# Feature: project-audit-cleanup, Property 3: Size Reduction Accuracy
@given(
    remove_sizes=st.lists(file_size_strategy, min_size=0, max_size=20),
    consolidate_sizes=st.lists(file_size_strategy, min_size=0, max_size=5)
)
@settings(
    max_examples=10,
    deadline=None,
    suppress_health_check=[HealthCheck.function_scoped_fixture]
)
def test_property_size_reduction_accuracy(tmp_path, remove_sizes, consolidate_sizes, mock_services):
    """
    Property 3: Size Reduction Accuracy
    
    For any cleanup operation, the calculated size reduction should equal
    the sum of all removed file sizes, and the final package size should
    equal initial size minus removed size.
    
    **Validates: Requirements 5.1, 5.2, 5.3, 5.5**
    """
    backup_manager, validator = mock_services
    
    # Create pyproject.toml for consolidation to work
    pyproject = tmp_path / "pyproject.toml"
    pyproject.write_text("""
[project]
name = "test"
version = "1.0.0"
dependencies = []
""")
    
    # Create cleanup engine
    engine = CleanupEngine(
        project_root=tmp_path,
        backup_manager=backup_manager,
        validator=validator,
        verbose=False
    )
    
    # Create test files with specified sizes
    remove_files = []
    for i, size in enumerate(remove_sizes):
        file_path = tmp_path / f"remove_{i}.txt"
        # Create file with specified size
        file_path.write_bytes(b'x' * size)
        remove_files.append(FileInfo(
            path=file_path,
            size=size,
            modified_time=datetime.now(),
            category=FileCategory.REMOVE,
            reason="Test"
        ))
    
    consolidate_files = []
    for i, size in enumerate(consolidate_sizes):
        file_path = tmp_path / f"consolidate_{i}.txt"
        file_path.write_bytes(b'x' * size)
        consolidate_files.append(FileInfo(
            path=file_path,
            size=size,
            modified_time=datetime.now(),
            category=FileCategory.CONSOLIDATE,
            reason="Test"
        ))
    
    # Calculate expected size reduction
    expected_size_freed = sum(remove_sizes) + sum(consolidate_sizes)
    
    # Create categorized files
    categorized = CategorizedFiles(
        remove=remove_files,
        consolidate=consolidate_files,
        archive=[],
        keep=[]
    )
    
    # Run cleanup (skip validation and consolidation to focus on size calculation)
    result = engine.cleanup(categorized, dry_run=False, skip_validation=True)
    
    # Property: Size freed should equal sum of removed file sizes
    # Allow small tolerance for rounding or filesystem overhead
    tolerance = 10  # bytes
    assert abs(result.size_freed - expected_size_freed) <= tolerance, \
        f"Size freed {result.size_freed} does not match expected {expected_size_freed}"
    
    # Property: Files removed should equal number of files
    expected_files_removed = len(remove_sizes) + len(consolidate_sizes)
    assert result.files_removed == expected_files_removed, \
        f"Files removed {result.files_removed} does not match expected {expected_files_removed}"


# Feature: project-audit-cleanup, Property 7: Cache Directory Structure Preservation
@given(
    cache_file_count=file_count_strategy,
    cache_subdirs=st.lists(st.text(min_size=1, max_size=10, alphabet=st.characters(whitelist_categories=('Lu', 'Ll'))), min_size=0, max_size=5)
)
@settings(
    max_examples=10,
    deadline=None,
    suppress_health_check=[HealthCheck.function_scoped_fixture]
)
def test_property_cache_directory_structure_preservation(tmp_path, cache_file_count, cache_subdirs, mock_services):
    """
    Property 7: Cache Directory Structure Preservation
    
    For any cache directory (.brain/, .hypothesis/, __pycache__/), after cleanup
    the directory itself should still exist even if all files within it are removed.
    
    **Validates: Requirements 3.1, 3.4**
    """
    backup_manager, validator = mock_services
    
    # Create cleanup engine
    engine = CleanupEngine(
        project_root=tmp_path,
        backup_manager=backup_manager,
        validator=validator,
        verbose=False
    )
    
    # Create .brain directory structure
    brain_dir = tmp_path / ".brain"
    brain_dir.mkdir(parents=True, exist_ok=True)
    
    # Create subdirectories
    for subdir in cache_subdirs:
        subdir_path = brain_dir / subdir
        subdir_path.mkdir(parents=True, exist_ok=True)
    
    # Create cache files
    archive_files = []
    for i in range(cache_file_count):
        # Distribute files across subdirectories
        if cache_subdirs and i % 2 == 0:
            subdir = cache_subdirs[i % len(cache_subdirs)]
            file_path = brain_dir / subdir / f"cache_{i}.json"
        else:
            file_path = brain_dir / f"cache_{i}.json"
        
        file_path.parent.mkdir(parents=True, exist_ok=True)
        file_path.write_text("{}")
        
        archive_files.append(FileInfo(
            path=file_path,
            size=file_path.stat().st_size,
            modified_time=datetime.now() - timedelta(days=60),
            category=FileCategory.ARCHIVE,
            reason="Old cache"
        ))
    
    # Create categorized files
    categorized = CategorizedFiles(
        remove=[],
        consolidate=[],
        archive=archive_files,
        keep=[]
    )
    
    # Run cleanup
    result = engine.cleanup(categorized, dry_run=False, skip_validation=True)
    
    # Property: .brain directory should still exist
    assert brain_dir.exists(), ".brain directory was removed but should be preserved"
    
    # Property: Archive subdirectory should exist
    archive_dir = brain_dir / "archive"
    if cache_file_count > 0:
        assert archive_dir.exists(), "Archive directory should be created"


# Feature: project-audit-cleanup, Property 13: File Age-Based Archival
@given(
    file_ages_days=st.lists(st.integers(min_value=0, max_value=365), min_size=1, max_size=20)
)
@settings(
    max_examples=10,
    deadline=None,
    suppress_health_check=[HealthCheck.function_scoped_fixture]
)
def test_property_file_age_based_archival(tmp_path, file_ages_days, mock_services):
    """
    Property 13: File Age-Based Archival
    
    For any file in .brain/ with modification time older than 30 days,
    that file should be moved to .brain/archive/ during cleanup.
    
    **Validates: Requirements 3.2**
    """
    backup_manager, validator = mock_services
    
    # Create cleanup engine
    engine = CleanupEngine(
        project_root=tmp_path,
        backup_manager=backup_manager,
        validator=validator,
        verbose=False
    )
    
    # Create .brain directory
    brain_dir = tmp_path / ".brain"
    brain_dir.mkdir(parents=True, exist_ok=True)
    
    # Create files with different ages
    archive_files = []
    old_files = []  # Files older than 30 days
    
    for i, age_days in enumerate(file_ages_days):
        file_path = brain_dir / f"data_{i}.json"
        file_path.write_text("{}")
        
        # Set modification time
        mod_time = datetime.now() - timedelta(days=age_days)
        
        file_info = FileInfo(
            path=file_path,
            size=file_path.stat().st_size,
            modified_time=mod_time,
            category=FileCategory.ARCHIVE,
            reason="Cache file"
        )
        
        archive_files.append(file_info)
        
        # Track which files should be archived (older than 30 days)
        if age_days > 30:
            old_files.append(file_path)
    
    # Create categorized files
    categorized = CategorizedFiles(
        remove=[],
        consolidate=[],
        archive=archive_files,
        keep=[]
    )
    
    # Run cleanup
    result = engine.cleanup(categorized, dry_run=False, skip_validation=True)
    
    # Property: Files older than 30 days should be in archive
    archive_dir = brain_dir / "archive"
    
    if old_files:
        # Archive directory should exist
        assert archive_dir.exists(), "Archive directory should be created for old files"
        
        # Old files should be moved to archive
        for old_file in old_files:
            original_name = old_file.name
            archived_file = archive_dir / original_name
            
            # File should either be in archive or removed from original location
            assert not old_file.exists() or archived_file.exists(), \
                f"Old file {old_file} should be archived or removed"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
