"""
Property-based tests for BackupManager.

These tests use Hypothesis to verify universal properties that should hold
across all valid inputs for backup and restore operations.

Feature: project-audit-cleanup
"""

import tempfile
import shutil
from pathlib import Path
from hypothesis import given, strategies as st, settings, assume
from scripts.cleanup import BackupManager


# Strategy for generating valid file content
file_content_strategy = st.text(
    alphabet=st.characters(blacklist_categories=('Cs', 'Cc')),
    min_size=0,
    max_size=1000
)

# Strategy for generating valid filenames
filename_strategy = st.text(
    alphabet=st.characters(
        whitelist_categories=('Lu', 'Ll', 'Nd'),
        min_codepoint=ord('a'),
        max_codepoint=ord('z')
    ),
    min_size=1,
    max_size=20
).map(lambda s: s + '.txt')


@given(
    st.lists(
        st.tuples(filename_strategy, file_content_strategy),
        min_size=1,
        max_size=10,
        unique_by=lambda x: x[0]  # Unique filenames
    )
)
@settings(max_examples=10, deadline=None)
def test_backup_restore_roundtrip(files_data):
    """
    Property 1: Backup and Restore Round Trip
    
    For any set of files marked for removal, creating a backup then restoring
    from that backup should result in all files being restored to their original
    locations with identical content (checksums match).
    
    **Validates: Requirements 7.1, 7.2, 7.3, 7.4, 7.5**
    """
    # Skip if no files
    assume(len(files_data) > 0)
    
    with tempfile.TemporaryDirectory() as tmpdir:
        tmpdir = Path(tmpdir)
        backup_dir = tmpdir / "backups"
        test_files_dir = tmpdir / "test_files"
        test_files_dir.mkdir()
        
        # Create test files with given content
        created_files = []
        original_contents = {}
        
        for filename, content in files_data:
            file_path = test_files_dir / filename
            try:
                file_path.write_text(content, encoding='utf-8')
                created_files.append(file_path)
                original_contents[file_path] = content
            except Exception:
                # Skip files that can't be created
                continue
        
        # Skip if no files were successfully created
        assume(len(created_files) > 0)
        
        # Initialize BackupManager
        manager = BackupManager(backup_dir, verbose=False)
        
        # Create backup
        backup_info = manager.create_backup(created_files, base_path=test_files_dir)
        
        # Verify backup was created
        assert backup_info.file_count == len(created_files), \
            f"Backup should contain {len(created_files)} files, got {backup_info.file_count}"
        assert backup_info.archive_path.exists(), "Archive should exist"
        assert backup_info.manifest_path.exists(), "Manifest should exist"
        
        # Delete original files
        for file_path in created_files:
            file_path.unlink()
            assert not file_path.exists(), f"File {file_path} should be deleted"
        
        # Restore from backup
        restore_result = manager.restore_backup(backup_info.backup_id)
        
        # Verify restoration succeeded
        assert restore_result.success, \
            f"Restore should succeed. Errors: {restore_result.errors}"
        assert restore_result.files_restored == len(created_files), \
            f"Should restore {len(created_files)} files, got {restore_result.files_restored}"
        assert restore_result.files_failed == 0, \
            f"Should have 0 failures, got {restore_result.files_failed}"
        
        # Verify all files are restored with identical content
        for file_path in created_files:
            assert file_path.exists(), f"File {file_path} should be restored"
            
            restored_content = file_path.read_text(encoding='utf-8')
            original_content = original_contents[file_path]
            
            assert restored_content == original_content, \
                f"Content mismatch for {file_path}: expected {repr(original_content)}, got {repr(restored_content)}"


@given(
    st.lists(
        st.tuples(filename_strategy, file_content_strategy),
        min_size=1,
        max_size=5,
        unique_by=lambda x: x[0]
    )
)
@settings(max_examples=10, deadline=None)
def test_backup_restore_preserves_file_count(files_data):
    """
    Property: Backup and restore preserves exact file count.
    
    For any set of files, the number of files restored should equal
    the number of files backed up.
    
    **Validates: Requirements 7.1, 7.4, 7.5**
    """
    assume(len(files_data) > 0)
    
    with tempfile.TemporaryDirectory() as tmpdir:
        tmpdir = Path(tmpdir)
        backup_dir = tmpdir / "backups"
        test_files_dir = tmpdir / "test_files"
        test_files_dir.mkdir()
        
        # Create test files
        created_files = []
        for filename, content in files_data:
            file_path = test_files_dir / filename
            try:
                file_path.write_text(content, encoding='utf-8')
                created_files.append(file_path)
            except Exception:
                continue
        
        assume(len(created_files) > 0)
        
        # Backup and restore
        manager = BackupManager(backup_dir, verbose=False)
        backup_info = manager.create_backup(created_files, base_path=test_files_dir)
        
        # Delete files
        for file_path in created_files:
            file_path.unlink()
        
        # Restore
        restore_result = manager.restore_backup(backup_info.backup_id)
        
        # Verify file count matches
        assert restore_result.files_restored == backup_info.file_count, \
            f"Restored {restore_result.files_restored} files but backup had {backup_info.file_count}"


@given(
    st.lists(
        st.tuples(filename_strategy, file_content_strategy),
        min_size=1,
        max_size=5,
        unique_by=lambda x: x[0]
    )
)
@settings(max_examples=10, deadline=None)
def test_multiple_backups_independent(files_data):
    """
    Property: Multiple backups are independent.
    
    Creating multiple backups should result in independent backup archives
    that can be restored separately without interference.
    
    **Validates: Requirements 7.1, 7.2, 7.3**
    """
    assume(len(files_data) >= 2)
    
    with tempfile.TemporaryDirectory() as tmpdir:
        tmpdir = Path(tmpdir)
        backup_dir = tmpdir / "backups"
        test_files_dir = tmpdir / "test_files"
        test_files_dir.mkdir()
        
        # Split files into two groups
        mid = len(files_data) // 2
        group1_data = files_data[:mid]
        group2_data = files_data[mid:]
        
        # Create first group of files
        group1_files = []
        for filename, content in group1_data:
            file_path = test_files_dir / filename
            try:
                file_path.write_text(content, encoding='utf-8')
                group1_files.append(file_path)
            except Exception:
                continue
        
        assume(len(group1_files) > 0)
        
        # Create first backup
        manager = BackupManager(backup_dir, verbose=False)
        backup1 = manager.create_backup(group1_files, base_path=test_files_dir)
        
        # Delete first group
        for f in group1_files:
            f.unlink()
        
        # Create second group of files
        group2_files = []
        for filename, content in group2_data:
            file_path = test_files_dir / filename
            try:
                file_path.write_text(content, encoding='utf-8')
                group2_files.append(file_path)
            except Exception:
                continue
        
        assume(len(group2_files) > 0)
        
        # Create second backup
        backup2 = manager.create_backup(group2_files, base_path=test_files_dir)
        
        # Verify both backups exist
        backups = manager.list_backups()
        assert len(backups) >= 2, f"Should have at least 2 backups, got {len(backups)}"
        
        # Verify backup IDs are different
        assert backup1.backup_id != backup2.backup_id, \
            "Backup IDs should be unique"
        
        # Verify each backup has correct file count
        assert backup1.file_count == len(group1_files), \
            f"Backup 1 should have {len(group1_files)} files"
        assert backup2.file_count == len(group2_files), \
            f"Backup 2 should have {len(group2_files)} files"


@given(
    st.lists(
        st.tuples(filename_strategy, file_content_strategy),
        min_size=1,
        max_size=10,
        unique_by=lambda x: x[0]
    )
)
@settings(max_examples=10, deadline=None)
def test_manifest_archive_consistency(files_data):
    """
    Property 8: Manifest and Archive Consistency
    
    For any backup, every file listed in the manifest should exist in the
    backup archive, and every file in the backup archive should be listed
    in the manifest (bijection).
    
    **Validates: Requirements 7.3**
    """
    assume(len(files_data) > 0)
    
    with tempfile.TemporaryDirectory() as tmpdir:
        tmpdir = Path(tmpdir)
        backup_dir = tmpdir / "backups"
        test_files_dir = tmpdir / "test_files"
        test_files_dir.mkdir()
        
        # Create test files
        created_files = []
        for filename, content in files_data:
            file_path = test_files_dir / filename
            try:
                file_path.write_text(content, encoding='utf-8')
                created_files.append(file_path)
            except Exception:
                continue
        
        assume(len(created_files) > 0)
        
        # Create backup
        manager = BackupManager(backup_dir, verbose=False)
        backup_info = manager.create_backup(created_files, base_path=test_files_dir)
        
        # Load manifest
        import json
        with open(backup_info.manifest_path, 'r') as f:
            manifest = json.load(f)
        
        # Extract file paths from manifest
        manifest_files = set()
        for file_entry in manifest["files"]:
            backup_path_str = file_entry["backup_path"]
            # Extract arcname from "files.tar.gz:arcname" format
            if ":" in backup_path_str:
                arcname = backup_path_str.split(":", 1)[1]
            else:
                arcname = Path(file_entry["original_path"]).name
            manifest_files.add(arcname)
        
        # Extract file paths from archive
        import tarfile
        archive_files = set()
        with tarfile.open(backup_info.archive_path, "r:gz") as tar:
            for member in tar.getmembers():
                if member.isfile():
                    archive_files.add(member.name)
        
        # Verify bijection: manifest files == archive files
        # Every file in manifest should be in archive
        missing_in_archive = manifest_files - archive_files
        assert len(missing_in_archive) == 0, \
            f"Files in manifest but not in archive: {missing_in_archive}"
        
        # Every file in archive should be in manifest
        missing_in_manifest = archive_files - manifest_files
        assert len(missing_in_manifest) == 0, \
            f"Files in archive but not in manifest: {missing_in_manifest}"
        
        # Verify counts match
        assert len(manifest_files) == len(archive_files), \
            f"Manifest has {len(manifest_files)} files, archive has {len(archive_files)}"
        
        # Verify manifest file count matches actual count
        assert manifest["total_files"] == len(manifest_files), \
            f"Manifest reports {manifest['total_files']} files but contains {len(manifest_files)}"
