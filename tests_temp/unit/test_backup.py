"""
Unit tests for BackupManager.

These tests verify specific examples and edge cases for backup and restore
operations, complementing the property-based tests.

Feature: project-audit-cleanup
Requirements: 7.1, 7.2, 7.3, 7.5
"""

import pytest
import tempfile
import json
import tarfile
import os
from pathlib import Path
from datetime import datetime
from unittest.mock import patch, MagicMock

from scripts.cleanup import BackupManager
from scripts.cleanup.models import BackupInfo, RestoreResult


class TestBackupCreation:
    """Tests for backup creation functionality."""
    
    def test_create_backup_with_known_files(self):
        """Test backup creation with a known set of files."""
        with tempfile.TemporaryDirectory() as tmpdir:
            tmpdir = Path(tmpdir)
            backup_dir = tmpdir / "backups"
            test_files_dir = tmpdir / "test_files"
            test_files_dir.mkdir()
            
            # Create known test files
            file1 = test_files_dir / "file1.txt"
            file2 = test_files_dir / "file2.py"
            file3 = test_files_dir / "subdir" / "file3.md"
            
            file1.write_text("Content of file 1")
            file2.write_text("print('Hello, World!')")
            file3.parent.mkdir(parents=True)
            file3.write_text("# Markdown content")
            
            files_to_backup = [file1, file2, file3]
            
            # Create backup
            manager = BackupManager(backup_dir, verbose=False)
            backup_info = manager.create_backup(files_to_backup, base_path=test_files_dir)
            
            # Verify backup info
            assert backup_info.file_count == 3
            assert backup_info.backup_id.startswith("backup_")
            assert backup_info.archive_path.exists()
            assert backup_info.manifest_path.exists()
            
            # Verify total size is sum of file sizes
            expected_size = sum(f.stat().st_size for f in files_to_backup)
            assert backup_info.total_size == expected_size
    
    def test_create_backup_empty_list(self):
        """Test backup creation with empty file list."""
        with tempfile.TemporaryDirectory() as tmpdir:
            tmpdir = Path(tmpdir)
            backup_dir = tmpdir / "backups"
            
            manager = BackupManager(backup_dir, verbose=False)
            backup_info = manager.create_backup([], base_path=tmpdir)
            
            # Should create backup with 0 files
            assert backup_info.file_count == 0
            assert backup_info.total_size == 0
            assert backup_info.archive_path.exists()
            assert backup_info.manifest_path.exists()
    
    def test_create_backup_nonexistent_files(self):
        """Test backup creation with non-existent files."""
        with tempfile.TemporaryDirectory() as tmpdir:
            tmpdir = Path(tmpdir)
            backup_dir = tmpdir / "backups"
            
            # Try to backup files that don't exist
            nonexistent_files = [
                Path(tmpdir) / "does_not_exist.txt",
                Path(tmpdir) / "also_missing.py"
            ]
            
            manager = BackupManager(backup_dir, verbose=False)
            backup_info = manager.create_backup(nonexistent_files, base_path=tmpdir)
            
            # Should create backup with 0 files (skipped non-existent)
            assert backup_info.file_count == 0
    
    def test_create_backup_mixed_existent_nonexistent(self):
        """Test backup with mix of existent and non-existent files."""
        with tempfile.TemporaryDirectory() as tmpdir:
            tmpdir = Path(tmpdir)
            backup_dir = tmpdir / "backups"
            test_files_dir = tmpdir / "test_files"
            test_files_dir.mkdir()
            
            # Create one real file
            real_file = test_files_dir / "real.txt"
            real_file.write_text("I exist")
            
            # Mix with non-existent file
            files_to_backup = [
                real_file,
                test_files_dir / "fake.txt"
            ]
            
            manager = BackupManager(backup_dir, verbose=False)
            backup_info = manager.create_backup(files_to_backup, base_path=test_files_dir)
            
            # Should only backup the existing file
            assert backup_info.file_count == 1
    
    def test_backup_directory_created_automatically(self):
        """Test that backup directory is created if it doesn't exist."""
        with tempfile.TemporaryDirectory() as tmpdir:
            tmpdir = Path(tmpdir)
            backup_dir = tmpdir / "new_backup_dir"
            
            # Backup directory doesn't exist yet
            assert not backup_dir.exists()
            
            # Initialize manager
            manager = BackupManager(backup_dir, verbose=False)
            
            # Directory should now exist
            assert backup_dir.exists()
            assert backup_dir.is_dir()
    
    def test_backup_id_format(self):
        """Test that backup ID follows expected timestamp format."""
        with tempfile.TemporaryDirectory() as tmpdir:
            tmpdir = Path(tmpdir)
            backup_dir = tmpdir / "backups"
            test_file = tmpdir / "test.txt"
            test_file.write_text("test")
            
            manager = BackupManager(backup_dir, verbose=False)
            backup_info = manager.create_backup([test_file], base_path=tmpdir)
            
            # Verify format: backup_YYYYMMDD_HHMMSS_microseconds
            assert backup_info.backup_id.startswith("backup_")
            parts = backup_info.backup_id.split("_")
            assert len(parts) == 4  # backup, YYYYMMDD, HHMMSS, microseconds
            assert len(parts[1]) == 8  # YYYYMMDD
            assert len(parts[2]) == 6  # HHMMSS
            assert len(parts[3]) == 6  # microseconds


class TestManifestFormat:
    """Tests for manifest file format and content."""
    
    def test_manifest_json_structure(self):
        """Test that manifest has correct JSON structure."""
        with tempfile.TemporaryDirectory() as tmpdir:
            tmpdir = Path(tmpdir)
            backup_dir = tmpdir / "backups"
            test_file = tmpdir / "test.txt"
            test_file.write_text("test content")
            
            manager = BackupManager(backup_dir, verbose=False)
            backup_info = manager.create_backup([test_file], base_path=tmpdir)
            
            # Load and verify manifest structure
            with open(backup_info.manifest_path, 'r') as f:
                manifest = json.load(f)
            
            # Verify required fields
            assert "backup_id" in manifest
            assert "timestamp" in manifest
            assert "files" in manifest
            assert "total_size" in manifest
            assert "total_files" in manifest
            assert "base_path" in manifest
            
            # Verify types
            assert isinstance(manifest["backup_id"], str)
            assert isinstance(manifest["timestamp"], str)
            assert isinstance(manifest["files"], list)
            assert isinstance(manifest["total_size"], int)
            assert isinstance(manifest["total_files"], int)
    
    def test_manifest_file_entry_structure(self):
        """Test that each file entry in manifest has correct structure."""
        with tempfile.TemporaryDirectory() as tmpdir:
            tmpdir = Path(tmpdir)
            backup_dir = tmpdir / "backups"
            test_file = tmpdir / "test.txt"
            test_file.write_text("test content")
            
            manager = BackupManager(backup_dir, verbose=False)
            backup_info = manager.create_backup([test_file], base_path=tmpdir)
            
            # Load manifest
            with open(backup_info.manifest_path, 'r') as f:
                manifest = json.load(f)
            
            # Verify file entry structure
            assert len(manifest["files"]) == 1
            file_entry = manifest["files"][0]
            
            assert "original_path" in file_entry
            assert "backup_path" in file_entry
            assert "size" in file_entry
            assert "checksum" in file_entry
            
            # Verify checksum format
            assert file_entry["checksum"].startswith("sha256:")
    
    def test_manifest_total_size_accuracy(self):
        """Test that manifest total_size matches sum of file sizes."""
        with tempfile.TemporaryDirectory() as tmpdir:
            tmpdir = Path(tmpdir)
            backup_dir = tmpdir / "backups"
            test_files_dir = tmpdir / "test_files"
            test_files_dir.mkdir()
            
            # Create files with known sizes
            file1 = test_files_dir / "file1.txt"
            file2 = test_files_dir / "file2.txt"
            file1.write_text("A" * 100)  # 100 bytes
            file2.write_text("B" * 200)  # 200 bytes
            
            manager = BackupManager(backup_dir, verbose=False)
            backup_info = manager.create_backup([file1, file2], base_path=test_files_dir)
            
            # Load manifest
            with open(backup_info.manifest_path, 'r') as f:
                manifest = json.load(f)
            
            # Verify total size
            expected_size = 100 + 200
            assert manifest["total_size"] == expected_size
            
            # Verify individual file sizes
            file_sizes = [entry["size"] for entry in manifest["files"]]
            assert sum(file_sizes) == expected_size
    
    def test_manifest_timestamp_format(self):
        """Test that manifest timestamp is in ISO format."""
        with tempfile.TemporaryDirectory() as tmpdir:
            tmpdir = Path(tmpdir)
            backup_dir = tmpdir / "backups"
            test_file = tmpdir / "test.txt"
            test_file.write_text("test")
            
            manager = BackupManager(backup_dir, verbose=False)
            backup_info = manager.create_backup([test_file], base_path=tmpdir)
            
            # Load manifest
            with open(backup_info.manifest_path, 'r') as f:
                manifest = json.load(f)
            
            # Verify timestamp can be parsed as ISO format
            timestamp = datetime.fromisoformat(manifest["timestamp"])
            assert isinstance(timestamp, datetime)


class TestBackupRestore:
    """Tests for backup restoration functionality."""
    
    def test_restore_with_known_backup(self):
        """Test restoration from a known backup."""
        with tempfile.TemporaryDirectory() as tmpdir:
            tmpdir = Path(tmpdir)
            backup_dir = tmpdir / "backups"
            test_files_dir = tmpdir / "test_files"
            test_files_dir.mkdir()
            
            # Create and backup files
            file1 = test_files_dir / "file1.txt"
            file2 = test_files_dir / "file2.txt"
            file1.write_text("Content 1")
            file2.write_text("Content 2")
            
            manager = BackupManager(backup_dir, verbose=False)
            backup_info = manager.create_backup([file1, file2], base_path=test_files_dir)
            
            # Delete original files
            file1.unlink()
            file2.unlink()
            assert not file1.exists()
            assert not file2.exists()
            
            # Restore
            result = manager.restore_backup(backup_info.backup_id)
            
            # Verify restoration
            assert result.success
            assert result.files_restored == 2
            assert result.files_failed == 0
            assert len(result.errors) == 0
            
            # Verify files exist and have correct content
            assert file1.exists()
            assert file2.exists()
            assert file1.read_text() == "Content 1"
            assert file2.read_text() == "Content 2"
    
    def test_restore_to_target_directory(self):
        """Test restoration to a different target directory."""
        with tempfile.TemporaryDirectory() as tmpdir:
            tmpdir = Path(tmpdir)
            backup_dir = tmpdir / "backups"
            test_files_dir = tmpdir / "test_files"
            restore_dir = tmpdir / "restore_target"
            test_files_dir.mkdir()
            restore_dir.mkdir()
            
            # Create and backup file
            original_file = test_files_dir / "file.txt"
            original_file.write_text("Original content")
            
            manager = BackupManager(backup_dir, verbose=False)
            backup_info = manager.create_backup([original_file], base_path=test_files_dir)
            
            # Restore to different directory
            result = manager.restore_backup(backup_info.backup_id, target_dir=restore_dir)
            
            # Verify restoration to target directory
            assert result.success
            assert result.files_restored == 1
            
            restored_file = restore_dir / "file.txt"
            assert restored_file.exists()
            assert restored_file.read_text() == "Original content"
    
    def test_restore_nonexistent_backup(self):
        """Test restoration of non-existent backup raises error."""
        with tempfile.TemporaryDirectory() as tmpdir:
            tmpdir = Path(tmpdir)
            backup_dir = tmpdir / "backups"
            
            manager = BackupManager(backup_dir, verbose=False)
            
            # Try to restore non-existent backup
            with pytest.raises(ValueError, match="Backup does not exist"):
                manager.restore_backup("backup_99999999_999999")
    
    def test_restore_creates_parent_directories(self):
        """Test that restore creates parent directories as needed."""
        with tempfile.TemporaryDirectory() as tmpdir:
            tmpdir = Path(tmpdir)
            backup_dir = tmpdir / "backups"
            test_files_dir = tmpdir / "test_files"
            test_files_dir.mkdir()
            
            # Create nested file structure
            nested_dir = test_files_dir / "level1" / "level2"
            nested_dir.mkdir(parents=True)
            nested_file = nested_dir / "deep_file.txt"
            nested_file.write_text("Deep content")
            
            manager = BackupManager(backup_dir, verbose=False)
            backup_info = manager.create_backup([nested_file], base_path=test_files_dir)
            
            # Delete entire directory structure
            import shutil
            shutil.rmtree(test_files_dir / "level1")
            assert not nested_file.exists()
            
            # Restore
            result = manager.restore_backup(backup_info.backup_id)
            
            # Verify nested structure is recreated
            assert result.success
            assert nested_file.exists()
            assert nested_file.read_text() == "Deep content"
    
    def test_restore_result_structure(self):
        """Test that RestoreResult has correct structure."""
        with tempfile.TemporaryDirectory() as tmpdir:
            tmpdir = Path(tmpdir)
            backup_dir = tmpdir / "backups"
            test_file = tmpdir / "test.txt"
            test_file.write_text("test")
            
            manager = BackupManager(backup_dir, verbose=False)
            backup_info = manager.create_backup([test_file], base_path=tmpdir)
            
            test_file.unlink()
            result = manager.restore_backup(backup_info.backup_id)
            
            # Verify RestoreResult structure
            assert isinstance(result, RestoreResult)
            assert hasattr(result, 'success')
            assert hasattr(result, 'files_restored')
            assert hasattr(result, 'files_failed')
            assert hasattr(result, 'errors')
            assert isinstance(result.success, bool)
            assert isinstance(result.files_restored, int)
            assert isinstance(result.files_failed, int)
            assert isinstance(result.errors, list)


class TestErrorHandling:
    """Tests for error handling scenarios."""
    
    def test_backup_with_permission_denied(self):
        """Test backup creation when file permissions are denied."""
        with tempfile.TemporaryDirectory() as tmpdir:
            tmpdir = Path(tmpdir)
            backup_dir = tmpdir / "backups"
            test_file = tmpdir / "test.txt"
            test_file.write_text("test")
            
            manager = BackupManager(backup_dir, verbose=False)
            
            # Mock file operations to simulate permission error
            with patch('tarfile.open') as mock_tar:
                mock_tar.side_effect = PermissionError("Permission denied")
                
                # Should raise IOError
                with pytest.raises(IOError, match="Backup creation failed"):
                    manager.create_backup([test_file], base_path=tmpdir)
    
    def test_backup_cleanup_on_failure(self):
        """Test that partial backup is cleaned up on failure."""
        with tempfile.TemporaryDirectory() as tmpdir:
            tmpdir = Path(tmpdir)
            backup_dir = tmpdir / "backups"
            test_file = tmpdir / "test.txt"
            test_file.write_text("test")
            
            manager = BackupManager(backup_dir, verbose=False)
            
            # Mock to cause failure during archive creation
            with patch('tarfile.open') as mock_tar:
                mock_tar.side_effect = Exception("Simulated failure")
                
                # Attempt backup
                try:
                    manager.create_backup([test_file], base_path=tmpdir)
                except IOError:
                    pass
                
                # Verify no partial backup directories remain
                # (only the main backup_dir should exist, empty)
                backup_subdirs = list(backup_dir.iterdir())
                # Filter out any non-directory items
                backup_subdirs = [d for d in backup_subdirs if d.is_dir()]
                assert len(backup_subdirs) == 0
    
    def test_restore_with_corrupted_manifest(self):
        """Test restoration when manifest is corrupted."""
        with tempfile.TemporaryDirectory() as tmpdir:
            tmpdir = Path(tmpdir)
            backup_dir = tmpdir / "backups"
            test_file = tmpdir / "test.txt"
            test_file.write_text("test")
            
            manager = BackupManager(backup_dir, verbose=False)
            backup_info = manager.create_backup([test_file], base_path=tmpdir)
            
            # Corrupt the manifest
            with open(backup_info.manifest_path, 'w') as f:
                f.write("{ invalid json }")
            
            # Try to restore
            with pytest.raises(IOError, match="Failed to load manifest"):
                manager.restore_backup(backup_info.backup_id)
    
    def test_restore_with_missing_archive(self):
        """Test restoration when archive file is missing."""
        with tempfile.TemporaryDirectory() as tmpdir:
            tmpdir = Path(tmpdir)
            backup_dir = tmpdir / "backups"
            test_file = tmpdir / "test.txt"
            test_file.write_text("test")
            
            manager = BackupManager(backup_dir, verbose=False)
            backup_info = manager.create_backup([test_file], base_path=tmpdir)
            
            # Delete the archive file
            backup_info.archive_path.unlink()
            
            # Try to restore
            with pytest.raises(ValueError, match="Backup archive not found"):
                manager.restore_backup(backup_info.backup_id)
    
    def test_restore_partial_failure(self):
        """Test restoration when some files fail to restore."""
        with tempfile.TemporaryDirectory() as tmpdir:
            tmpdir = Path(tmpdir)
            backup_dir = tmpdir / "backups"
            test_files_dir = tmpdir / "test_files"
            test_files_dir.mkdir()
            
            # Create files
            file1 = test_files_dir / "file1.txt"
            file2 = test_files_dir / "file2.txt"
            file1.write_text("Content 1")
            file2.write_text("Content 2")
            
            manager = BackupManager(backup_dir, verbose=False)
            backup_info = manager.create_backup([file1, file2], base_path=test_files_dir)
            
            # Delete files
            file1.unlink()
            file2.unlink()
            
            # Mock to cause failure for one file during restore
            original_open = open
            call_count = [0]
            
            def mock_open(*args, **kwargs):
                # Fail on second file write
                if 'wb' in args or kwargs.get('mode') == 'wb':
                    call_count[0] += 1
                    if call_count[0] == 2:
                        raise PermissionError("Simulated permission error")
                return original_open(*args, **kwargs)
            
            with patch('builtins.open', side_effect=mock_open):
                result = manager.restore_backup(backup_info.backup_id)
            
            # Should report partial success
            assert not result.success  # Overall failure due to one file failing
            assert result.files_failed > 0
            assert len(result.errors) > 0


class TestBackupListing:
    """Tests for listing backups."""
    
    def test_list_backups_empty(self):
        """Test listing backups when none exist."""
        with tempfile.TemporaryDirectory() as tmpdir:
            tmpdir = Path(tmpdir)
            backup_dir = tmpdir / "backups"
            
            manager = BackupManager(backup_dir, verbose=False)
            backups = manager.list_backups()
            
            assert isinstance(backups, list)
            assert len(backups) == 0
    
    def test_list_backups_multiple(self):
        """Test listing multiple backups."""
        import time
        
        with tempfile.TemporaryDirectory() as tmpdir:
            tmpdir = Path(tmpdir)
            backup_dir = tmpdir / "backups"
            test_file = tmpdir / "test.txt"
            test_file.write_text("test")
            
            manager = BackupManager(backup_dir, verbose=False)
            
            # Create multiple backups
            backup1 = manager.create_backup([test_file], base_path=tmpdir)
            
            # Wait to ensure different timestamp
            time.sleep(1.1)
            
            # Modify file and create another backup
            test_file.write_text("modified")
            backup2 = manager.create_backup([test_file], base_path=tmpdir)
            
            # List backups
            backups = manager.list_backups()
            
            assert len(backups) == 2
            
            # Verify backups are sorted by timestamp (newest first)
            assert backups[0].timestamp >= backups[1].timestamp
            
            # Verify backup IDs
            backup_ids = {b.backup_id for b in backups}
            assert backup1.backup_id in backup_ids
            assert backup2.backup_id in backup_ids
    
    def test_list_backups_returns_backup_info(self):
        """Test that list_backups returns proper BackupInfo objects."""
        with tempfile.TemporaryDirectory() as tmpdir:
            tmpdir = Path(tmpdir)
            backup_dir = tmpdir / "backups"
            test_file = tmpdir / "test.txt"
            test_file.write_text("test")
            
            manager = BackupManager(backup_dir, verbose=False)
            manager.create_backup([test_file], base_path=tmpdir)
            
            backups = manager.list_backups()
            
            assert len(backups) == 1
            backup_info = backups[0]
            
            # Verify BackupInfo structure
            assert isinstance(backup_info, BackupInfo)
            assert isinstance(backup_info.backup_id, str)
            assert isinstance(backup_info.timestamp, datetime)
            assert isinstance(backup_info.file_count, int)
            assert isinstance(backup_info.total_size, int)
            assert isinstance(backup_info.manifest_path, Path)
            assert isinstance(backup_info.archive_path, Path)


class TestBackupUtilities:
    """Tests for utility methods."""
    
    def test_get_backup_info_existing(self):
        """Test getting info for an existing backup."""
        with tempfile.TemporaryDirectory() as tmpdir:
            tmpdir = Path(tmpdir)
            backup_dir = tmpdir / "backups"
            test_file = tmpdir / "test.txt"
            test_file.write_text("test")
            
            manager = BackupManager(backup_dir, verbose=False)
            backup_info = manager.create_backup([test_file], base_path=tmpdir)
            
            # Get backup info
            retrieved_info = manager.get_backup_info(backup_info.backup_id)
            
            assert retrieved_info is not None
            assert retrieved_info.backup_id == backup_info.backup_id
            assert retrieved_info.file_count == backup_info.file_count
            assert retrieved_info.total_size == backup_info.total_size
    
    def test_get_backup_info_nonexistent(self):
        """Test getting info for non-existent backup."""
        with tempfile.TemporaryDirectory() as tmpdir:
            tmpdir = Path(tmpdir)
            backup_dir = tmpdir / "backups"
            
            manager = BackupManager(backup_dir, verbose=False)
            
            # Try to get non-existent backup
            info = manager.get_backup_info("backup_99999999_999999")
            
            assert info is None
    
    def test_delete_backup_existing(self):
        """Test deleting an existing backup."""
        with tempfile.TemporaryDirectory() as tmpdir:
            tmpdir = Path(tmpdir)
            backup_dir = tmpdir / "backups"
            test_file = tmpdir / "test.txt"
            test_file.write_text("test")
            
            manager = BackupManager(backup_dir, verbose=False)
            backup_info = manager.create_backup([test_file], base_path=tmpdir)
            
            # Verify backup exists
            assert (backup_dir / backup_info.backup_id).exists()
            
            # Delete backup
            result = manager.delete_backup(backup_info.backup_id)
            
            assert result is True
            assert not (backup_dir / backup_info.backup_id).exists()
    
    def test_delete_backup_nonexistent(self):
        """Test deleting non-existent backup."""
        with tempfile.TemporaryDirectory() as tmpdir:
            tmpdir = Path(tmpdir)
            backup_dir = tmpdir / "backups"
            
            manager = BackupManager(backup_dir, verbose=False)
            
            # Try to delete non-existent backup
            result = manager.delete_backup("backup_99999999_999999")
            
            assert result is False
    
    def test_checksum_calculation(self):
        """Test checksum calculation for files."""
        with tempfile.TemporaryDirectory() as tmpdir:
            tmpdir = Path(tmpdir)
            backup_dir = tmpdir / "backups"
            test_file = tmpdir / "test.txt"
            
            # Create file with known content
            content = "Test content for checksum"
            test_file.write_text(content)
            
            manager = BackupManager(backup_dir, verbose=False)
            backup_info = manager.create_backup([test_file], base_path=tmpdir)
            
            # Load manifest and check checksum format
            with open(backup_info.manifest_path, 'r') as f:
                manifest = json.load(f)
            
            checksum = manifest["files"][0]["checksum"]
            
            # Verify checksum format
            assert checksum.startswith("sha256:")
            assert len(checksum) > 7  # "sha256:" + hex digest
            
            # Verify checksum is consistent
            backup_info2 = manager.create_backup([test_file], base_path=tmpdir)
            with open(backup_info2.manifest_path, 'r') as f:
                manifest2 = json.load(f)
            
            checksum2 = manifest2["files"][0]["checksum"]
            assert checksum == checksum2  # Same content = same checksum
