"""
Cleanup Engine for Project Audit and Cleanup System.

This module provides the main cleanup orchestration logic, integrating
BackupManager, DependencyConsolidator, and Validator to perform safe
file removal operations with automatic rollback on validation failure.

Key Features:
    - Orchestrates complete cleanup sequence
    - Creates backups before any removal
    - Removes files, archives caches, consolidates dependencies
    - Validates package integrity after cleanup
    - Automatic rollback on validation failure
    - Empty directory cleanup

Requirements Addressed:
    - 1.3: Create backup archive before removal
    - 1.4: Remove corrupt directories with verification
    - 1.5: Restore from backup if removal fails
    - 2.4: Remove lib/ directory
    - 3.1: Preserve cache directory structure
    - 3.2: Archive old learning data
    - 3.3: Remove hypothesis constant files
    - 3.5: Remove __pycache__ files
    - 9.5: Automatic rollback on validation failure
    - 11.4: Remove empty directories
"""

import shutil
from pathlib import Path
from typing import List, Optional
from datetime import datetime, timedelta

from .models import (
    CategorizedFiles,
    CleanupResult,
    RemovalResult,
    ArchiveResult,
    FileInfo,
    DirectoryInfo,
)
from .backup import BackupManager
from .dependencies import DependencyConsolidator
from .validator import Validator
from .logger import get_logger


class CleanupEngine:
    """Orchestrates safe cleanup operations with backup and validation.
    
    The CleanupEngine integrates multiple services to perform comprehensive
    cleanup operations:
    1. Creates backup of all files to be removed
    2. Removes files based on categorization
    3. Archives old cache files
    4. Consolidates dependencies into pyproject.toml
    5. Removes empty directories
    6. Validates package integrity
    7. Automatically rolls back on validation failure
    
    Attributes:
        project_root: Root directory of the project
        backup_manager: BackupManager instance for backup operations
        validator: Validator instance for post-cleanup validation
        logger: Logger instance for operation tracking
    
    Example:
        >>> engine = CleanupEngine(
        ...     project_root=Path("."),
        ...     backup_manager=BackupManager(Path(".cleanup_backup")),
        ...     validator=Validator(Path("."))
        ... )
        >>> result = engine.cleanup(categorized_files, dry_run=False)
        >>> if result.success:
        ...     print(f"Cleanup successful: {result.files_removed} files removed")
    """
    
    def __init__(
        self,
        project_root: Path,
        backup_manager: BackupManager,
        validator: Validator,
        verbose: bool = False
    ):
        """Initialize CleanupEngine with required services.
        
        Args:
            project_root: Root directory of the project
            backup_manager: BackupManager instance for backup operations
            validator: Validator instance for validation
            verbose: Enable verbose logging
        """
        self.project_root = Path(project_root)
        self.backup_manager = backup_manager
        self.validator = validator
        self.logger = get_logger(verbose=verbose)
        
        self.logger.info(f"CleanupEngine initialized for project: {self.project_root}")
    
    def cleanup(
        self,
        categorized: CategorizedFiles,
        dry_run: bool = False,
        skip_validation: bool = False
    ) -> CleanupResult:
        """Execute complete cleanup sequence with backup and validation.
        
        Cleanup sequence:
        1. Create backup of all files to be removed
        2. Remove files marked for removal
        3. Archive cache files marked for archival
        4. Consolidate dependencies from requirements files
        5. Remove empty directories
        6. Validate package integrity
        7. Rollback if validation fails
        
        Args:
            categorized: CategorizedFiles with files organized by action
            dry_run: If True, report actions without executing them
            skip_validation: If True, skip post-cleanup validation
        
        Returns:
            CleanupResult with cleanup statistics and validation results
        
        Example:
            >>> result = engine.cleanup(categorized_files, dry_run=False)
            >>> if not result.success:
            ...     print(f"Cleanup failed: {result.errors}")
        """
        self.logger.info("Starting cleanup sequence")
        
        if dry_run:
            self.logger.info("DRY RUN MODE - No changes will be made")
            return self._dry_run_report(categorized)
        
        errors = []
        backup_id = ""
        files_removed = 0
        size_freed = 0
        
        # Step 1: Create backup of all files to be removed
        try:
            files_to_backup = categorized.remove + categorized.consolidate
            if files_to_backup:
                self.logger.info(f"Creating backup of {len(files_to_backup)} files")
                backup_paths = [f.path for f in files_to_backup]
                backup_info = self.backup_manager.create_backup(
                    backup_paths,
                    base_path=self.project_root
                )
                backup_id = backup_info.backup_id
                self.logger.info(f"Backup created: {backup_id}")
            else:
                self.logger.info("No files to backup")
        except Exception as e:
            error_msg = f"Backup creation failed: {e}"
            self.logger.error(error_msg)
            errors.append(error_msg)
            return CleanupResult(
                success=False,
                backup_id="",
                files_removed=0,
                size_freed=0,
                errors=errors
            )
        
        # Step 2: Remove files marked for removal
        try:
            if categorized.remove:
                self.logger.info(f"Removing {len(categorized.remove)} files")
                removal_result = self.remove_files(categorized.remove, backup=False)
                files_removed += removal_result.files_removed
                size_freed += removal_result.size_freed
                
                if not removal_result.success:
                    errors.extend(removal_result.errors)
                    self.logger.warning(
                        f"Some files failed to remove: {removal_result.files_failed}"
                    )
        except Exception as e:
            error_msg = f"File removal failed: {e}"
            self.logger.error(error_msg)
            errors.append(error_msg)
        
        # Step 3: Archive cache files
        try:
            if categorized.archive:
                self.logger.info(f"Archiving {len(categorized.archive)} cache files")
                archive_result = self.archive_cache(categorized.archive)
                
                if not archive_result.success:
                    errors.extend(archive_result.errors)
                    self.logger.warning("Some cache files failed to archive")
        except Exception as e:
            error_msg = f"Cache archival failed: {e}"
            self.logger.error(error_msg)
            errors.append(error_msg)
        
        # Step 4: Consolidate dependencies
        try:
            if categorized.consolidate:
                self.logger.info(
                    f"Consolidating {len(categorized.consolidate)} dependency files"
                )
                consolidation_result = self.consolidate_dependencies(
                    categorized.consolidate
                )
                
                if consolidation_result.success:
                    # Remove consolidated requirements files
                    for file_info in categorized.consolidate:
                        try:
                            if file_info.path.exists():
                                file_info.path.unlink()
                                files_removed += 1
                                size_freed += file_info.size
                                self.logger.debug(f"Removed: {file_info.path}")
                        except Exception as e:
                            error_msg = f"Failed to remove {file_info.path}: {e}"
                            self.logger.error(error_msg)
                            errors.append(error_msg)
                else:
                    errors.extend(consolidation_result.errors)
                    self.logger.warning("Dependency consolidation had errors")
        except Exception as e:
            error_msg = f"Dependency consolidation failed: {e}"
            self.logger.error(error_msg)
            errors.append(error_msg)
        
        # Step 5: Remove empty directories
        try:
            self.logger.info("Removing empty directories")
            empty_dirs_removed = self._remove_empty_directories()
            self.logger.info(f"Removed {empty_dirs_removed} empty directories")
        except Exception as e:
            error_msg = f"Empty directory removal failed: {e}"
            self.logger.error(error_msg)
            errors.append(error_msg)
        
        # Step 6: Validate package integrity
        validation_result = None
        if not skip_validation:
            try:
                self.logger.info("Validating package integrity")
                validation_result = self.validator.validate_all()
                
                if not validation_result.passed:
                    self.logger.error("Validation failed - initiating rollback")
                    errors.append("Validation failed after cleanup")
                    errors.extend(validation_result.errors)
                    
                    # Step 7: Rollback on validation failure
                    if backup_id:
                        try:
                            self.logger.info(f"Rolling back from backup: {backup_id}")
                            restore_result = self.backup_manager.restore_backup(backup_id)
                            
                            if restore_result.success:
                                self.logger.info("Rollback successful")
                                errors.append("Cleanup rolled back due to validation failure")
                            else:
                                self.logger.error("Rollback failed")
                                errors.append("CRITICAL: Rollback failed after validation failure")
                                errors.extend(restore_result.errors)
                        except Exception as e:
                            error_msg = f"Rollback failed: {e}"
                            self.logger.error(error_msg)
                            errors.append(error_msg)
                    
                    return CleanupResult(
                        success=False,
                        backup_id=backup_id,
                        files_removed=files_removed,
                        size_freed=size_freed,
                        errors=errors,
                        validation_result=validation_result
                    )
                else:
                    self.logger.info("Validation passed")
            except Exception as e:
                error_msg = f"Validation failed with exception: {e}"
                self.logger.error(error_msg)
                errors.append(error_msg)
        else:
            self.logger.info("Skipping validation (skip_validation=True)")
        
        # Cleanup successful
        success = len(errors) == 0 or all(
            "failed to remove" in e.lower() for e in errors
        )
        
        self.logger.info(
            f"Cleanup completed: {files_removed} files removed, "
            f"{size_freed} bytes freed"
        )
        
        return CleanupResult(
            success=success,
            backup_id=backup_id,
            files_removed=files_removed,
            size_freed=size_freed,
            errors=errors,
            validation_result=validation_result
        )
    
    def remove_files(self, files: List[FileInfo], backup: bool = True) -> RemovalResult:
        """Remove files with optional backup.
        
        Args:
            files: List of FileInfo objects to remove
            backup: If True, create backup before removal (default: True)
        
        Returns:
            RemovalResult with removal statistics
        
        Example:
            >>> result = engine.remove_files(files_to_remove, backup=True)
            >>> print(f"Removed {result.files_removed} files")
        """
        self.logger.info(f"Removing {len(files)} files (backup={backup})")
        
        files_removed = 0
        files_failed = 0
        size_freed = 0
        errors = []
        
        # Create backup if requested
        if backup:
            try:
                backup_paths = [f.path for f in files]
                backup_info = self.backup_manager.create_backup(
                    backup_paths,
                    base_path=self.project_root
                )
                self.logger.info(f"Backup created: {backup_info.backup_id}")
            except Exception as e:
                error_msg = f"Backup creation failed: {e}"
                self.logger.error(error_msg)
                errors.append(error_msg)
                return RemovalResult(
                    success=False,
                    files_removed=0,
                    files_failed=len(files),
                    size_freed=0,
                    errors=errors
                )
        
        # Remove each file
        for file_info in files:
            try:
                path = file_info.path
                
                # Handle both files and directories
                if path.exists():
                    if path.is_file():
                        path.unlink()
                        files_removed += 1
                        size_freed += file_info.size
                        self.logger.debug(f"Removed file: {path}")
                    elif path.is_dir():
                        shutil.rmtree(path)
                        files_removed += 1
                        size_freed += file_info.size
                        self.logger.debug(f"Removed directory: {path}")
                    else:
                        self.logger.warning(f"Skipping non-file/non-directory: {path}")
                else:
                    self.logger.warning(f"File does not exist: {path}")
                    
            except PermissionError as e:
                files_failed += 1
                error_msg = f"Permission denied: {file_info.path}"
                self.logger.error(error_msg)
                errors.append(error_msg)
            except Exception as e:
                files_failed += 1
                error_msg = f"Failed to remove {file_info.path}: {e}"
                self.logger.error(error_msg)
                errors.append(error_msg)
        
        success = files_failed == 0
        
        if success:
            self.logger.info(
                f"Successfully removed {files_removed} files ({size_freed} bytes)"
            )
        else:
            self.logger.warning(
                f"Removed {files_removed} files, {files_failed} failed"
            )
        
        return RemovalResult(
            success=success,
            files_removed=files_removed,
            files_failed=files_failed,
            size_freed=size_freed,
            errors=errors
        )
    
    def archive_cache(self, cache_files: List[FileInfo]) -> ArchiveResult:
        """Archive old cache files while preserving directory structure.
        
        Archives files from .brain/ that are older than the threshold.
        Preserves the directory structure by creating archive/ subdirectories.
        
        Args:
            cache_files: List of FileInfo objects to archive
        
        Returns:
            ArchiveResult with archival statistics
        
        Example:
            >>> result = engine.archive_cache(old_cache_files)
            >>> print(f"Archived {result.files_archived} files")
        """
        self.logger.info(f"Archiving {len(cache_files)} cache files")
        
        files_archived = 0
        errors = []
        archive_base = self.project_root / ".brain" / "archive"
        
        # Create archive directory if it doesn't exist
        try:
            archive_base.mkdir(parents=True, exist_ok=True)
        except Exception as e:
            error_msg = f"Failed to create archive directory: {e}"
            self.logger.error(error_msg)
            errors.append(error_msg)
            return ArchiveResult(
                success=False,
                files_archived=0,
                archive_path=archive_base,
                errors=errors
            )
        
        # Archive each file
        for file_info in cache_files:
            try:
                source_path = file_info.path
                
                # Only archive .brain/ files
                if ".brain" not in str(source_path):
                    self.logger.debug(f"Skipping non-.brain file: {source_path}")
                    continue
                
                if not source_path.exists():
                    self.logger.warning(f"File does not exist: {source_path}")
                    continue
                
                # Calculate relative path from .brain/
                try:
                    brain_root = self.project_root / ".brain"
                    rel_path = source_path.relative_to(brain_root)
                    
                    # Create archive path preserving structure
                    archive_path = archive_base / rel_path
                    archive_path.parent.mkdir(parents=True, exist_ok=True)
                    
                    # Move file to archive
                    shutil.move(str(source_path), str(archive_path))
                    files_archived += 1
                    self.logger.debug(f"Archived: {source_path} -> {archive_path}")
                    
                except ValueError:
                    # File is not under .brain/, skip
                    self.logger.warning(f"File not under .brain/: {source_path}")
                    continue
                    
            except Exception as e:
                error_msg = f"Failed to archive {file_info.path}: {e}"
                self.logger.error(error_msg)
                errors.append(error_msg)
        
        success = len(errors) == 0
        
        if success:
            self.logger.info(f"Successfully archived {files_archived} files")
        else:
            self.logger.warning(
                f"Archived {files_archived} files with {len(errors)} errors"
            )
        
        return ArchiveResult(
            success=success,
            files_archived=files_archived,
            archive_path=archive_base,
            errors=errors
        )
    
    def consolidate_dependencies(self, requirements_files: List[FileInfo]):
        """Consolidate dependencies from requirements files into pyproject.toml.
        
        Args:
            requirements_files: List of FileInfo objects for requirements files
        
        Returns:
            ConsolidationResult with consolidation statistics
        
        Example:
            >>> result = engine.consolidate_dependencies(req_files)
            >>> print(f"Merged {result.dependencies_merged} dependencies")
        """
        self.logger.info(f"Consolidating {len(requirements_files)} requirements files")
        
        pyproject_path = self.project_root / "pyproject.toml"
        
        if not pyproject_path.exists():
            error_msg = "pyproject.toml not found"
            self.logger.error(error_msg)
            from .models import ConsolidationResult
            return ConsolidationResult(
                success=False,
                dependencies_merged=0,
                files_removed=0,
                duplicates_found=0,
                errors=[error_msg]
            )
        
        # Create consolidator
        consolidator = DependencyConsolidator(pyproject_path, logger=self.logger)
        
        # Parse and merge each requirements file
        all_dependencies = []
        for file_info in requirements_files:
            try:
                if file_info.path.exists():
                    deps = consolidator.parse_requirements_file(file_info.path)
                    all_dependencies.extend(deps)
                    self.logger.debug(
                        f"Parsed {len(deps)} dependencies from {file_info.path}"
                    )
            except Exception as e:
                error_msg = f"Failed to parse {file_info.path}: {e}"
                self.logger.error(error_msg)
        
        # Merge into pyproject.toml
        if all_dependencies:
            result = consolidator.merge_into_pyproject(all_dependencies)
            self.logger.info(
                f"Merged {result.dependencies_merged} dependencies into pyproject.toml"
            )
            return result
        else:
            from .models import ConsolidationResult
            return ConsolidationResult(
                success=True,
                dependencies_merged=0,
                files_removed=0,
                duplicates_found=0
            )
    
    def _remove_empty_directories(self) -> int:
        """Remove empty directories from the project.
        
        Scans the project for empty directories and removes them, excluding
        critical empty directories like logs/, states/, data/.
        
        Returns:
            Number of directories removed
        """
        from .categorizer import FileCategorizer
        import os
        
        categorizer = FileCategorizer()
        removed_count = 0
        
        # Walk the project tree bottom-up to handle nested empty directories
        for root, dirs, files in os.walk(self.project_root, topdown=False):
            root_path = Path(root)
            
            # Check if directory is empty (no files, or only .DS_Store/.gitkeep)
            contents = list(root_path.iterdir())
            
            if not contents:
                # Completely empty
                is_empty = True
            elif len(contents) <= 2:
                # Check if only contains .DS_Store or .gitkeep
                names = {f.name for f in contents}
                is_empty = names.issubset({".DS_Store", ".gitkeep"})
            else:
                is_empty = False
            
            if is_empty:
                # Check if it's a critical empty directory
                if root_path.name not in categorizer.critical_empty_dirs:
                    # Don't remove the project root itself
                    if root_path != self.project_root:
                        try:
                            shutil.rmtree(root_path)
                            removed_count += 1
                            self.logger.debug(f"Removed empty directory: {root_path}")
                        except Exception as e:
                            self.logger.warning(
                                f"Failed to remove empty directory {root_path}: {e}"
                            )
        
        return removed_count
    
    def _dry_run_report(self, categorized: CategorizedFiles) -> CleanupResult:
        """Generate a dry-run report without making changes.
        
        Args:
            categorized: CategorizedFiles with files organized by action
        
        Returns:
            CleanupResult with projected statistics
        """
        self.logger.info("=== DRY RUN REPORT ===")
        
        # Calculate statistics
        files_to_remove = len(categorized.remove) + len(categorized.consolidate)
        size_to_free = sum(f.size for f in categorized.remove)
        size_to_free += sum(f.size for f in categorized.consolidate)
        
        self.logger.info(f"Files to remove: {files_to_remove}")
        self.logger.info(f"Size to free: {size_to_free} bytes ({size_to_free / (1024*1024):.2f} MB)")
        self.logger.info(f"Files to archive: {len(categorized.archive)}")
        self.logger.info(f"Files to keep: {len(categorized.keep)}")
        
        # List files by category
        if categorized.remove:
            self.logger.info("\nFiles to REMOVE:")
            for file_info in categorized.remove[:10]:  # Show first 10
                self.logger.info(f"  - {file_info.path} ({file_info.size} bytes)")
            if len(categorized.remove) > 10:
                self.logger.info(f"  ... and {len(categorized.remove) - 10} more")
        
        if categorized.consolidate:
            self.logger.info("\nFiles to CONSOLIDATE:")
            for file_info in categorized.consolidate:
                self.logger.info(f"  - {file_info.path}")
        
        if categorized.archive:
            self.logger.info("\nFiles to ARCHIVE:")
            for file_info in categorized.archive[:10]:  # Show first 10
                self.logger.info(f"  - {file_info.path}")
            if len(categorized.archive) > 10:
                self.logger.info(f"  ... and {len(categorized.archive) - 10} more")
        
        self.logger.info("\n=== END DRY RUN REPORT ===")
        
        return CleanupResult(
            success=True,
            backup_id="dry_run",
            files_removed=files_to_remove,
            size_freed=size_to_free,
            errors=[]
        )
