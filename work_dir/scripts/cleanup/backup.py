"""
Backup Manager for Project Audit and Cleanup System.

This module provides functionality for creating, managing, and restoring backups
of files before cleanup operations. All backups are compressed using tar.gz format
and include a JSON manifest for tracking.

Key Features:
    - Create timestamped backups with tar.gz compression
    - Generate JSON manifests with file metadata and checksums
    - List all available backups
    - Restore files from backup archives
    - Automatic backup directory management

Requirements Addressed:
    - 7.1: Create timestamped backup before removal
    - 7.2: Compress backups using tar.gz format
    - 7.3: Maintain manifest file with original paths
    - 7.4: Provide rollback command to restore from backup
    - 7.5: Restore all files to original locations
"""

import json
import tarfile
import hashlib
import shutil
from pathlib import Path
from datetime import datetime
from typing import List, Optional, Dict, Any

from .models import BackupInfo, RestoreResult
from .logger import get_logger


class BackupManager:
    """Manages backup creation and restoration for cleanup operations.
    
    The BackupManager creates compressed archives of files before they are removed,
    maintains manifests for tracking, and provides restoration capabilities.
    
    Attributes:
        backup_dir: Root directory for storing backups
        logger: Logger instance for operation tracking
    
    Example:
        >>> manager = BackupManager(Path(".cleanup_backup"))
        >>> backup_info = manager.create_backup([Path("file1.txt"), Path("file2.py")])
        >>> print(f"Backup created: {backup_info.backup_id}")
        >>> result = manager.restore_backup(backup_info.backup_id)
        >>> print(f"Restored {result.files_restored} files")
    """
    
    def __init__(self, backup_dir: Path, verbose: bool = False):
        """Initialize BackupManager with backup directory.
        
        Args:
            backup_dir: Directory where backups will be stored
            verbose: Enable verbose logging
        """
        self.backup_dir = Path(backup_dir)
        self.logger = get_logger(verbose=verbose)
        
        # Create backup directory if it doesn't exist
        self.backup_dir.mkdir(parents=True, exist_ok=True)
        self.logger.info(f"BackupManager initialized with directory: {self.backup_dir}")
    
    def create_backup(self, files: List[Path], base_path: Optional[Path] = None) -> BackupInfo:
        """Create a compressed backup of specified files.
        
        Creates a timestamped backup directory containing:
        - files.tar.gz: Compressed archive of all files
        - manifest.json: Metadata about backed up files
        - metadata.json: Backup-level metadata
        
        Args:
            files: List of file paths to backup
            base_path: Base path for calculating relative paths in archive.
                      If None, uses current working directory.
        
        Returns:
            BackupInfo object with backup metadata
        
        Raises:
            IOError: If backup creation fails
            PermissionError: If insufficient permissions to create backup
        
        Example:
            >>> files = [Path("agentic_sdlc/lib/module.py")]
            >>> backup = manager.create_backup(files, base_path=Path("."))
        """
        # Generate backup ID with timestamp (including microseconds for uniqueness)
        timestamp = datetime.now()
        backup_id = f"backup_{timestamp.strftime('%Y%m%d_%H%M%S_%f')}"
        
        # Create backup subdirectory
        backup_path = self.backup_dir / backup_id
        backup_path.mkdir(parents=True, exist_ok=True)
        
        self.logger.info(f"Creating backup: {backup_id}")
        
        # Set base path for relative path calculation
        if base_path is None:
            base_path = Path.cwd()
        else:
            base_path = Path(base_path).resolve()
        
        # Prepare archive path
        archive_path = backup_path / "files.tar.gz"
        manifest_path = backup_path / "manifest.json"
        
        # Filter out non-existent files
        existing_files = [f for f in files if Path(f).exists()]
        if len(existing_files) < len(files):
            missing_count = len(files) - len(existing_files)
            self.logger.warning(f"{missing_count} files do not exist and will be skipped")
        
        # Create tar.gz archive
        total_size = 0
        manifest_entries = []
        
        try:
            with tarfile.open(archive_path, "w:gz") as tar:
                for file_path in existing_files:
                    file_path = Path(file_path).resolve()
                    
                    # Skip if file doesn't exist or is not a file
                    if not file_path.exists():
                        self.logger.warning(f"Skipping non-existent file: {file_path}")
                        continue
                    
                    if not file_path.is_file():
                        self.logger.warning(f"Skipping non-file: {file_path}")
                        continue
                    
                    # Calculate relative path for archive
                    try:
                        arcname = file_path.relative_to(base_path)
                    except ValueError:
                        # File is outside base_path, use absolute path
                        arcname = file_path
                    
                    # Add file to archive
                    tar.add(file_path, arcname=str(arcname))
                    
                    # Calculate file size and checksum
                    file_size = file_path.stat().st_size
                    total_size += file_size
                    checksum = self._calculate_checksum(file_path)
                    
                    # Add to manifest
                    manifest_entries.append({
                        "original_path": str(file_path),
                        "backup_path": f"files.tar.gz:{arcname}",
                        "size": file_size,
                        "checksum": checksum
                    })
                    
                    self.logger.debug(f"Added to backup: {file_path}")
            
            self.logger.info(f"Archive created: {archive_path} ({len(manifest_entries)} files)")
            
        except Exception as e:
            self.logger.error(f"Failed to create archive: {e}")
            # Clean up partial backup
            if backup_path.exists():
                shutil.rmtree(backup_path)
            raise IOError(f"Backup creation failed: {e}")
        
        # Create manifest
        manifest_data = {
            "backup_id": backup_id,
            "timestamp": timestamp.isoformat(),
            "files": manifest_entries,
            "total_size": total_size,
            "total_files": len(manifest_entries),
            "base_path": str(base_path)
        }
        
        try:
            with open(manifest_path, 'w') as f:
                json.dump(manifest_data, f, indent=2)
            self.logger.info(f"Manifest created: {manifest_path}")
        except Exception as e:
            self.logger.error(f"Failed to create manifest: {e}")
            # Clean up backup
            if backup_path.exists():
                shutil.rmtree(backup_path)
            raise IOError(f"Manifest creation failed: {e}")
        
        # Create metadata file
        metadata_path = backup_path / "metadata.json"
        metadata = {
            "backup_id": backup_id,
            "timestamp": timestamp.isoformat(),
            "file_count": len(manifest_entries),
            "total_size": total_size,
            "archive_path": str(archive_path),
            "manifest_path": str(manifest_path)
        }
        
        try:
            with open(metadata_path, 'w') as f:
                json.dump(metadata, f, indent=2)
        except Exception as e:
            self.logger.warning(f"Failed to create metadata file: {e}")
        
        # Create BackupInfo object
        backup_info = BackupInfo(
            backup_id=backup_id,
            timestamp=timestamp,
            file_count=len(manifest_entries),
            total_size=total_size,
            manifest_path=manifest_path,
            archive_path=archive_path
        )
        
        self.logger.info(f"Backup completed: {backup_id} ({len(manifest_entries)} files, {total_size} bytes)")
        
        return backup_info
    
    def create_manifest(self, backup_id: str, files: List[Path]) -> None:
        """Create a manifest file for a backup.
        
        This method is typically called internally by create_backup, but can be
        used separately if needed.
        
        Args:
            backup_id: Unique identifier for the backup
            files: List of files to include in manifest
        
        Raises:
            ValueError: If backup_id doesn't exist
            IOError: If manifest creation fails
        """
        backup_path = self.backup_dir / backup_id
        if not backup_path.exists():
            raise ValueError(f"Backup directory does not exist: {backup_id}")
        
        manifest_path = backup_path / "manifest.json"
        
        manifest_entries = []
        total_size = 0
        
        for file_path in files:
            file_path = Path(file_path)
            if file_path.exists() and file_path.is_file():
                file_size = file_path.stat().st_size
                total_size += file_size
                checksum = self._calculate_checksum(file_path)
                
                manifest_entries.append({
                    "original_path": str(file_path),
                    "backup_path": f"files.tar.gz:{file_path.name}",
                    "size": file_size,
                    "checksum": checksum
                })
        
        manifest_data = {
            "backup_id": backup_id,
            "timestamp": datetime.now().isoformat(),
            "files": manifest_entries,
            "total_size": total_size,
            "total_files": len(manifest_entries)
        }
        
        with open(manifest_path, 'w') as f:
            json.dump(manifest_data, f, indent=2)
        
        self.logger.info(f"Manifest created for backup {backup_id}")
    
    def list_backups(self) -> List[BackupInfo]:
        """List all available backups.
        
        Scans the backup directory and returns information about all backups.
        
        Returns:
            List of BackupInfo objects, sorted by timestamp (newest first)
        
        Example:
            >>> backups = manager.list_backups()
            >>> for backup in backups:
            ...     print(f"{backup.backup_id}: {backup.file_count} files")
        """
        backups = []
        
        if not self.backup_dir.exists():
            self.logger.warning(f"Backup directory does not exist: {self.backup_dir}")
            return backups
        
        # Scan backup directory for backup subdirectories
        for backup_path in self.backup_dir.iterdir():
            if not backup_path.is_dir():
                continue
            
            # Check for manifest file
            manifest_path = backup_path / "manifest.json"
            if not manifest_path.exists():
                self.logger.warning(f"Backup missing manifest: {backup_path.name}")
                continue
            
            # Load manifest
            try:
                with open(manifest_path, 'r') as f:
                    manifest = json.load(f)
                
                backup_info = BackupInfo(
                    backup_id=manifest["backup_id"],
                    timestamp=datetime.fromisoformat(manifest["timestamp"]),
                    file_count=manifest["total_files"],
                    total_size=manifest["total_size"],
                    manifest_path=manifest_path,
                    archive_path=backup_path / "files.tar.gz"
                )
                
                backups.append(backup_info)
                
            except Exception as e:
                self.logger.error(f"Failed to load backup {backup_path.name}: {e}")
                continue
        
        # Sort by timestamp, newest first
        backups.sort(key=lambda b: b.timestamp, reverse=True)
        
        self.logger.info(f"Found {len(backups)} backups")
        
        return backups
    
    def restore_backup(self, backup_id: str, target_dir: Optional[Path] = None) -> RestoreResult:
        """Restore files from a backup archive.
        
        Extracts all files from the backup archive and restores them to their
        original locations (or to target_dir if specified).
        
        Args:
            backup_id: ID of the backup to restore
            target_dir: Optional target directory for restoration.
                       If None, restores to original locations from manifest.
        
        Returns:
            RestoreResult with restoration statistics
        
        Raises:
            ValueError: If backup_id doesn't exist
            IOError: If restoration fails
        
        Example:
            >>> result = manager.restore_backup("backup_20260131_143022")
            >>> if result.success:
            ...     print(f"Restored {result.files_restored} files")
        """
        backup_path = self.backup_dir / backup_id
        
        if not backup_path.exists():
            raise ValueError(f"Backup does not exist: {backup_id}")
        
        manifest_path = backup_path / "manifest.json"
        archive_path = backup_path / "files.tar.gz"
        
        if not manifest_path.exists():
            raise ValueError(f"Backup manifest not found: {backup_id}")
        
        if not archive_path.exists():
            raise ValueError(f"Backup archive not found: {backup_id}")
        
        self.logger.info(f"Restoring backup: {backup_id}")
        
        # Load manifest
        try:
            with open(manifest_path, 'r') as f:
                manifest = json.load(f)
        except Exception as e:
            raise IOError(f"Failed to load manifest: {e}")
        
        files_restored = 0
        files_failed = 0
        errors = []
        
        # Extract archive
        try:
            with tarfile.open(archive_path, "r:gz") as tar:
                # Get base path from manifest if available
                base_path = manifest.get("base_path")
                if base_path:
                    base_path = Path(base_path)
                else:
                    base_path = Path.cwd()
                
                # Restore each file
                for file_entry in manifest["files"]:
                    original_path = Path(file_entry["original_path"])
                    
                    # Determine restoration path
                    if target_dir:
                        # Restore to target directory, preserving relative structure
                        try:
                            rel_path = original_path.relative_to(base_path)
                            restore_path = target_dir / rel_path
                        except ValueError:
                            # Can't make relative, use filename only
                            restore_path = target_dir / original_path.name
                    else:
                        # Restore to original location
                        restore_path = original_path
                    
                    # Extract archive name from backup_path
                    backup_path_str = file_entry["backup_path"]
                    if ":" in backup_path_str:
                        arcname = backup_path_str.split(":", 1)[1]
                    else:
                        arcname = original_path.name
                    
                    try:
                        # Find member in archive
                        member = None
                        for m in tar.getmembers():
                            if m.name == arcname or m.name == str(arcname):
                                member = m
                                break
                        
                        if member is None:
                            self.logger.warning(f"File not found in archive: {arcname}")
                            files_failed += 1
                            errors.append(f"File not found in archive: {arcname}")
                            continue
                        
                        # Create parent directory if needed
                        restore_path.parent.mkdir(parents=True, exist_ok=True)
                        
                        # Extract file
                        with tar.extractfile(member) as source:
                            if source:
                                with open(restore_path, 'wb') as target:
                                    shutil.copyfileobj(source, target)
                        
                        # Verify checksum if available
                        expected_checksum = file_entry.get("checksum")
                        if expected_checksum:
                            actual_checksum = self._calculate_checksum(restore_path)
                            if actual_checksum != expected_checksum:
                                self.logger.warning(f"Checksum mismatch for {restore_path}")
                                errors.append(f"Checksum mismatch: {restore_path}")
                        
                        files_restored += 1
                        self.logger.debug(f"Restored: {restore_path}")
                        
                    except Exception as e:
                        self.logger.error(f"Failed to restore {original_path}: {e}")
                        files_failed += 1
                        errors.append(f"Failed to restore {original_path}: {e}")
                        continue
        
        except Exception as e:
            self.logger.error(f"Failed to extract archive: {e}")
            raise IOError(f"Restoration failed: {e}")
        
        success = files_failed == 0
        
        result = RestoreResult(
            success=success,
            files_restored=files_restored,
            files_failed=files_failed,
            errors=errors
        )
        
        if success:
            self.logger.info(f"Restoration completed: {files_restored} files restored")
        else:
            self.logger.warning(f"Restoration completed with errors: {files_restored} restored, {files_failed} failed")
        
        return result
    
    def _calculate_checksum(self, file_path: Path) -> str:
        """Calculate SHA256 checksum of a file.
        
        Args:
            file_path: Path to file
        
        Returns:
            SHA256 checksum as hex string
        """
        sha256_hash = hashlib.sha256()
        
        try:
            with open(file_path, "rb") as f:
                # Read in chunks to handle large files
                for byte_block in iter(lambda: f.read(4096), b""):
                    sha256_hash.update(byte_block)
            
            return f"sha256:{sha256_hash.hexdigest()}"
        
        except Exception as e:
            self.logger.warning(f"Failed to calculate checksum for {file_path}: {e}")
            return "sha256:unknown"
    
    def get_backup_info(self, backup_id: str) -> Optional[BackupInfo]:
        """Get information about a specific backup.
        
        Args:
            backup_id: ID of the backup
        
        Returns:
            BackupInfo object if backup exists, None otherwise
        """
        backup_path = self.backup_dir / backup_id
        
        if not backup_path.exists():
            return None
        
        manifest_path = backup_path / "manifest.json"
        if not manifest_path.exists():
            return None
        
        try:
            with open(manifest_path, 'r') as f:
                manifest = json.load(f)
            
            return BackupInfo(
                backup_id=manifest["backup_id"],
                timestamp=datetime.fromisoformat(manifest["timestamp"]),
                file_count=manifest["total_files"],
                total_size=manifest["total_size"],
                manifest_path=manifest_path,
                archive_path=backup_path / "files.tar.gz"
            )
        
        except Exception as e:
            self.logger.error(f"Failed to load backup info: {e}")
            return None
    
    def delete_backup(self, backup_id: str) -> bool:
        """Delete a backup and all its files.
        
        Args:
            backup_id: ID of the backup to delete
        
        Returns:
            True if deletion succeeded, False otherwise
        """
        backup_path = self.backup_dir / backup_id
        
        if not backup_path.exists():
            self.logger.warning(f"Backup does not exist: {backup_id}")
            return False
        
        try:
            shutil.rmtree(backup_path)
            self.logger.info(f"Deleted backup: {backup_id}")
            return True
        
        except Exception as e:
            self.logger.error(f"Failed to delete backup {backup_id}: {e}")
            return False
