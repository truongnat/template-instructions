"""
Unit tests for CleanupEngine.

Tests the cleanup orchestration logic including:
- Cleanup sequence execution
- Backup creation before removal
- File removal with backup
- Cache archival
- Empty directory removal
- Automatic rollback on validation failure
"""

import pytest
from pathlib import Path
from datetime import datetime, timedelta
from unittest.mock import Mock, MagicMock, patch

from scripts.cleanup.cleanup import CleanupEngine
from scripts.cleanup.models import (
    CategorizedFiles,
    FileInfo,
    FileCategory,
    BackupInfo,
    ValidationResult,
    RemovalResult,
    ArchiveResult,
    ConsolidationResult,
)


@pytest.fixture
def mock_backup_manager():
    """Create a mock BackupManager."""
    manager = Mock()
    manager.create_backup.return_value = BackupInfo(
        backup_id="test_backup_123",
        timestamp=datetime.now(),
        file_count=5,
        total_size=1000,
        manifest_path=Path(".cleanup_backup/test_backup_123/manifest.json"),
        archive_path=Path(".cleanup_backup/test_backup_123/files.tar.gz")
    )
    manager.restore_backup.return_value = Mock(
        success=True,
        files_restored=5,
        files_failed=0,
        errors=[]
    )
    return manager


@pytest.fixture
def mock_validator():
    """Create a mock Validator."""
    validator = Mock()
    validator.validate_all.return_value = ValidationResult(
        passed=True,
        import_check=True,
        cli_check=True,
        test_check=True,
        build_check=True,
        errors=[]
    )
    return validator


@pytest.fixture
def cleanup_engine(tmp_path, mock_backup_manager, mock_validator):
    """Create a CleanupEngine instance for testing."""
    return CleanupEngine(
        project_root=tmp_path,
        backup_manager=mock_backup_manager,
        validator=mock_validator,
        verbose=False
    )


@pytest.fixture
def sample_categorized_files(tmp_path):
    """Create sample categorized files for testing."""
    # Create pyproject.toml for consolidation
    pyproject = tmp_path / "pyproject.toml"
    pyproject.write_text("""
[project]
name = "test"
version = "1.0.0"
dependencies = []
""")
    
    # Create some test files
    remove_file1 = tmp_path / "remove1.txt"
    remove_file1.write_text("remove me")
    
    remove_file2 = tmp_path / "remove2.txt"
    remove_file2.write_text("remove me too")
    
    consolidate_file = tmp_path / "requirements.txt"
    consolidate_file.write_text("requests>=2.0.0")
    
    archive_file = tmp_path / ".brain" / "old_data.json"
    archive_file.parent.mkdir(parents=True, exist_ok=True)
    archive_file.write_text("{}")
    
    keep_file = tmp_path / "keep.txt"
    keep_file.write_text("keep me")
    
    return CategorizedFiles(
        remove=[
            FileInfo(
                path=remove_file1,
                size=remove_file1.stat().st_size,
                modified_time=datetime.now(),
                category=FileCategory.REMOVE,
                reason="Test removal"
            ),
            FileInfo(
                path=remove_file2,
                size=remove_file2.stat().st_size,
                modified_time=datetime.now(),
                category=FileCategory.REMOVE,
                reason="Test removal"
            ),
        ],
        consolidate=[
            FileInfo(
                path=consolidate_file,
                size=consolidate_file.stat().st_size,
                modified_time=datetime.now(),
                category=FileCategory.CONSOLIDATE,
                reason="Test consolidation"
            ),
        ],
        archive=[
            FileInfo(
                path=archive_file,
                size=archive_file.stat().st_size,
                modified_time=datetime.now() - timedelta(days=60),
                category=FileCategory.ARCHIVE,
                reason="Test archival"
            ),
        ],
        keep=[
            FileInfo(
                path=keep_file,
                size=keep_file.stat().st_size,
                modified_time=datetime.now(),
                category=FileCategory.KEEP,
                reason="Test keep"
            ),
        ]
    )


def test_cleanup_engine_initialization(tmp_path, mock_backup_manager, mock_validator):
    """Test CleanupEngine initialization."""
    engine = CleanupEngine(
        project_root=tmp_path,
        backup_manager=mock_backup_manager,
        validator=mock_validator
    )
    
    assert engine.project_root == tmp_path
    assert engine.backup_manager == mock_backup_manager
    assert engine.validator == mock_validator


def test_cleanup_dry_run(cleanup_engine, sample_categorized_files):
    """Test cleanup in dry-run mode makes no changes."""
    result = cleanup_engine.cleanup(sample_categorized_files, dry_run=True)
    
    assert result.success
    assert result.backup_id == "dry_run"
    assert result.files_removed > 0  # Reports what would be removed
    assert result.size_freed > 0  # Reports what would be freed
    
    # Verify files still exist
    for file_info in sample_categorized_files.remove:
        assert file_info.path.exists()
    
    for file_info in sample_categorized_files.consolidate:
        assert file_info.path.exists()


def test_cleanup_creates_backup(cleanup_engine, sample_categorized_files, mock_backup_manager):
    """Test that cleanup creates backup before removal."""
    with patch.object(cleanup_engine, 'remove_files') as mock_remove, \
         patch.object(cleanup_engine, 'archive_cache') as mock_archive, \
         patch.object(cleanup_engine, 'consolidate_dependencies') as mock_consolidate:
        
        mock_remove.return_value = RemovalResult(
            success=True,
            files_removed=2,
            files_failed=0,
            size_freed=100,
            errors=[]
        )
        mock_archive.return_value = ArchiveResult(
            success=True,
            files_archived=1,
            archive_path=Path(".brain/archive"),
            errors=[]
        )
        mock_consolidate.return_value = ConsolidationResult(
            success=True,
            dependencies_merged=1,
            files_removed=1,
            duplicates_found=0,
            errors=[]
        )
        
        result = cleanup_engine.cleanup(sample_categorized_files, dry_run=False)
        
        # Verify backup was created
        mock_backup_manager.create_backup.assert_called_once()
        assert result.backup_id == "test_backup_123"


def test_cleanup_removes_files(cleanup_engine, sample_categorized_files):
    """Test that cleanup removes files marked for removal."""
    result = cleanup_engine.cleanup(
        sample_categorized_files,
        dry_run=False,
        skip_validation=True
    )
    
    assert result.success
    assert result.files_removed > 0
    
    # Verify files were removed
    for file_info in sample_categorized_files.remove:
        assert not file_info.path.exists()


def test_remove_files_with_backup(cleanup_engine, sample_categorized_files, mock_backup_manager):
    """Test remove_files creates backup when requested."""
    result = cleanup_engine.remove_files(sample_categorized_files.remove, backup=True)
    
    assert result.success
    assert result.files_removed == 2
    assert result.files_failed == 0
    assert result.size_freed > 0
    
    # Verify backup was created
    mock_backup_manager.create_backup.assert_called_once()


def test_remove_files_without_backup(cleanup_engine, sample_categorized_files, mock_backup_manager):
    """Test remove_files skips backup when not requested."""
    result = cleanup_engine.remove_files(sample_categorized_files.remove, backup=False)
    
    assert result.success
    assert result.files_removed == 2
    
    # Verify backup was not created
    mock_backup_manager.create_backup.assert_not_called()


def test_remove_files_handles_errors(cleanup_engine, tmp_path):
    """Test remove_files handles permission errors gracefully."""
    # Create a file that will fail to remove
    test_file = tmp_path / "protected.txt"
    test_file.write_text("protected")
    
    file_info = FileInfo(
        path=test_file,
        size=test_file.stat().st_size,
        modified_time=datetime.now(),
        category=FileCategory.REMOVE,
        reason="Test"
    )
    
    # Mock unlink to raise PermissionError
    with patch.object(Path, 'unlink', side_effect=PermissionError("Access denied")):
        result = cleanup_engine.remove_files([file_info], backup=False)
        
        assert not result.success
        assert result.files_failed == 1
        assert len(result.errors) > 0


def test_archive_cache_preserves_structure(cleanup_engine, sample_categorized_files):
    """Test archive_cache preserves directory structure."""
    result = cleanup_engine.archive_cache(sample_categorized_files.archive)
    
    assert result.success
    assert result.files_archived > 0
    
    # Verify archive directory was created
    archive_path = cleanup_engine.project_root / ".brain" / "archive"
    assert archive_path.exists()


def test_archive_cache_only_archives_brain_files(cleanup_engine, tmp_path):
    """Test archive_cache only archives .brain/ files."""
    # Create a non-.brain file
    non_brain_file = tmp_path / "other.txt"
    non_brain_file.write_text("not brain")
    
    file_info = FileInfo(
        path=non_brain_file,
        size=non_brain_file.stat().st_size,
        modified_time=datetime.now() - timedelta(days=60),
        category=FileCategory.ARCHIVE,
        reason="Test"
    )
    
    result = cleanup_engine.archive_cache([file_info])
    
    # Should succeed but not archive the file
    assert result.success
    assert result.files_archived == 0


def test_consolidate_dependencies(cleanup_engine, tmp_path):
    """Test consolidate_dependencies merges requirements files."""
    # Create pyproject.toml
    pyproject = tmp_path / "pyproject.toml"
    pyproject.write_text("""
[project]
name = "test"
version = "1.0.0"
dependencies = []
""")
    
    # Create requirements file
    req_file = tmp_path / "requirements.txt"
    req_file.write_text("requests>=2.0.0\npytest>=7.0.0")
    
    file_info = FileInfo(
        path=req_file,
        size=req_file.stat().st_size,
        modified_time=datetime.now(),
        category=FileCategory.CONSOLIDATE,
        reason="Test"
    )
    
    result = cleanup_engine.consolidate_dependencies([file_info])
    
    assert result.success
    assert result.dependencies_merged > 0


def test_cleanup_rollback_on_validation_failure(
    cleanup_engine,
    sample_categorized_files,
    mock_validator,
    mock_backup_manager
):
    """Test cleanup rolls back when validation fails."""
    # Make validation fail
    mock_validator.validate_all.return_value = ValidationResult(
        passed=False,
        import_check=False,
        cli_check=True,
        test_check=True,
        build_check=True,
        errors=["Import failed"]
    )
    
    result = cleanup_engine.cleanup(sample_categorized_files, dry_run=False)
    
    # Cleanup should fail
    assert not result.success
    assert "Validation failed" in str(result.errors)
    
    # Rollback should have been called
    mock_backup_manager.restore_backup.assert_called_once()


def test_cleanup_skips_validation_when_requested(
    cleanup_engine,
    sample_categorized_files,
    mock_validator
):
    """Test cleanup skips validation when skip_validation=True."""
    result = cleanup_engine.cleanup(
        sample_categorized_files,
        dry_run=False,
        skip_validation=True
    )
    
    # Validation should not have been called
    mock_validator.validate_all.assert_not_called()


def test_cleanup_handles_empty_categorized_files(cleanup_engine):
    """Test cleanup handles empty categorized files gracefully."""
    empty_categorized = CategorizedFiles()
    
    result = cleanup_engine.cleanup(empty_categorized, dry_run=False, skip_validation=True)
    
    assert result.success
    assert result.files_removed == 0
    assert result.size_freed == 0


def test_remove_empty_directories(cleanup_engine, tmp_path):
    """Test _remove_empty_directories removes empty dirs."""
    # Create empty directory
    empty_dir = tmp_path / "empty"
    empty_dir.mkdir()
    
    # Create directory with only .DS_Store
    ds_store_dir = tmp_path / "ds_store_only"
    ds_store_dir.mkdir()
    (ds_store_dir / ".DS_Store").write_text("")
    
    # Create directory with files
    non_empty_dir = tmp_path / "non_empty"
    non_empty_dir.mkdir()
    (non_empty_dir / "file.txt").write_text("content")
    
    removed = cleanup_engine._remove_empty_directories()
    
    # Empty directories should be removed
    assert not empty_dir.exists()
    assert not ds_store_dir.exists()
    
    # Non-empty directory should remain
    assert non_empty_dir.exists()


def test_cleanup_sequence_order(cleanup_engine, sample_categorized_files):
    """Test cleanup executes operations in correct order."""
    call_order = []
    
    def track_backup(*args, **kwargs):
        call_order.append("backup")
        return BackupInfo(
            backup_id="test",
            timestamp=datetime.now(),
            file_count=1,
            total_size=100,
            manifest_path=Path("manifest.json"),
            archive_path=Path("archive.tar.gz")
        )
    
    def track_remove(*args, **kwargs):
        call_order.append("remove")
        return RemovalResult(success=True, files_removed=1, files_failed=0, size_freed=100)
    
    def track_archive(*args, **kwargs):
        call_order.append("archive")
        return ArchiveResult(success=True, files_archived=1, archive_path=Path(".brain/archive"))
    
    def track_consolidate(*args, **kwargs):
        call_order.append("consolidate")
        return ConsolidationResult(
            success=True,
            dependencies_merged=1,
            files_removed=1,
            duplicates_found=0
        )
    
    def track_validate(*args, **kwargs):
        call_order.append("validate")
        return ValidationResult(passed=True, import_check=True, cli_check=True, test_check=True, build_check=True)
    
    with patch.object(cleanup_engine.backup_manager, 'create_backup', side_effect=track_backup), \
         patch.object(cleanup_engine, 'remove_files', side_effect=track_remove), \
         patch.object(cleanup_engine, 'archive_cache', side_effect=track_archive), \
         patch.object(cleanup_engine, 'consolidate_dependencies', side_effect=track_consolidate), \
         patch.object(cleanup_engine.validator, 'validate_all', side_effect=track_validate), \
         patch.object(cleanup_engine, '_remove_empty_directories', return_value=0):
        
        result = cleanup_engine.cleanup(sample_categorized_files, dry_run=False)
        
        # Verify correct order: backup -> remove -> archive -> consolidate -> validate
        assert call_order == ["backup", "remove", "archive", "consolidate", "validate"]


def test_cleanup_continues_on_non_critical_errors(cleanup_engine, sample_categorized_files):
    """Test cleanup continues when non-critical operations fail."""
    with patch.object(cleanup_engine, 'archive_cache') as mock_archive:
        # Make archive fail
        mock_archive.return_value = ArchiveResult(
            success=False,
            files_archived=0,
            archive_path=Path(".brain/archive"),
            errors=["Archive failed"]
        )
        
        result = cleanup_engine.cleanup(
            sample_categorized_files,
            dry_run=False,
            skip_validation=True
        )
        
        # Cleanup should still succeed overall
        # (archive failure is not critical)
        assert result.files_removed > 0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
