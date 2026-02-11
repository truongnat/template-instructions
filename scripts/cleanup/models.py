"""
Core data models for the Project Audit and Cleanup System.

This module defines all data structures used throughout the cleanup system,
including file information, categorization, backup metadata, and results.
"""

from enum import Enum
from dataclasses import dataclass, field
from pathlib import Path
from datetime import datetime
from typing import List, Optional, Dict


class FileCategory(Enum):
    """Categories for file classification during audit."""
    KEEP = "keep"
    REMOVE = "remove"
    CONSOLIDATE = "consolidate"
    ARCHIVE = "archive"


@dataclass
class FileInfo:
    """Information about a single file in the project.
    
    Attributes:
        path: Absolute or relative path to the file
        size: File size in bytes
        modified_time: Last modification timestamp
        category: Assigned category (KEEP/REMOVE/CONSOLIDATE/ARCHIVE)
        is_critical: Whether this file is critical to project functionality
        reason: Human-readable explanation for the assigned category
    """
    path: Path
    size: int
    modified_time: datetime
    category: Optional[FileCategory] = None
    is_critical: bool = False
    reason: str = ""


@dataclass
class DirectoryInfo:
    """Information about a directory in the project.
    
    Attributes:
        path: Absolute or relative path to the directory
        size: Total size of all files in directory (recursive)
        file_count: Number of files in directory (recursive)
        is_empty: Whether directory contains no files or only .DS_Store/.gitkeep
        is_critical: Whether this directory is critical to project functionality
    """
    path: Path
    size: int
    file_count: int
    is_empty: bool
    is_critical: bool = False


@dataclass
class Dependency:
    """Represents a Python package dependency.
    
    Attributes:
        name: Package name (e.g., 'requests')
        version_spec: Version specification (e.g., '>=2.0.0', '==1.2.3')
        source_file: Path to the requirements file where this was found
        target_group: Target dependency group in pyproject.toml
    """
    name: str
    version_spec: str
    source_file: Path
    target_group: str


@dataclass
class BackupInfo:
    """Metadata about a backup archive.
    
    Attributes:
        backup_id: Unique identifier for this backup (e.g., 'backup_20260131_143022')
        timestamp: When the backup was created
        file_count: Number of files in the backup
        total_size: Total size of backed up files in bytes
        manifest_path: Path to the JSON manifest file
        archive_path: Path to the compressed tar.gz archive
    """
    backup_id: str
    timestamp: datetime
    file_count: int
    total_size: int
    manifest_path: Path
    archive_path: Path


@dataclass
class ProjectInventory:
    """Complete inventory of project files and directories.
    
    Attributes:
        all_files: List of all files found during scan
        all_directories: List of all directories found during scan
        total_size: Total size of all files in bytes
    """
    all_files: List[FileInfo] = field(default_factory=list)
    all_directories: List[DirectoryInfo] = field(default_factory=list)
    total_size: int = 0


@dataclass
class CategorizedFiles:
    """Files organized by their assigned categories.
    
    Attributes:
        keep: Files to preserve (critical components)
        remove: Files to delete (corrupt, bloat, cache)
        consolidate: Files to merge (requirements files)
        archive: Files to archive (old cache data)
    """
    keep: List[FileInfo] = field(default_factory=list)
    remove: List[FileInfo] = field(default_factory=list)
    consolidate: List[FileInfo] = field(default_factory=list)
    archive: List[FileInfo] = field(default_factory=list)


@dataclass
class SizeImpact:
    """Size impact analysis for cleanup operation.
    
    Attributes:
        current_size: Current total project size in bytes
        projected_size: Projected size after cleanup in bytes
        reduction: Size reduction in bytes
        reduction_percent: Percentage reduction (0-100)
    """
    current_size: int
    projected_size: int
    reduction: int
    reduction_percent: float


@dataclass
class ValidationResult:
    """Results from post-cleanup validation tests.
    
    Attributes:
        passed: Whether all validations passed
        import_check: Whether import validation passed
        cli_check: Whether CLI entry point validation passed
        test_check: Whether test suite validation passed
        build_check: Whether package build validation passed
        errors: List of error messages from failed validations
    """
    passed: bool
    import_check: bool = False
    cli_check: bool = False
    test_check: bool = False
    build_check: bool = False
    errors: List[str] = field(default_factory=list)


@dataclass
class CleanupResult:
    """Results from a cleanup operation.
    
    Attributes:
        success: Whether cleanup completed successfully
        backup_id: ID of the backup created before cleanup
        files_removed: Number of files removed
        size_freed: Total size freed in bytes
        errors: List of error messages encountered
        validation_result: Results from post-cleanup validation
    """
    success: bool
    backup_id: str
    files_removed: int
    size_freed: int
    errors: List[str] = field(default_factory=list)
    validation_result: Optional[ValidationResult] = None


@dataclass
class AuditReport:
    """Complete audit report of the project.
    
    Attributes:
        timestamp: When the audit was performed
        total_files: Total number of files scanned
        categorized_files: Files organized by category
        size_impact: Projected size impact of cleanup
        recommendations: List of recommended actions
    """
    timestamp: datetime
    total_files: int
    categorized_files: CategorizedFiles
    size_impact: SizeImpact
    recommendations: List[str] = field(default_factory=list)


@dataclass
class RemovalResult:
    """Results from file removal operation.
    
    Attributes:
        success: Whether removal completed successfully
        files_removed: Number of files successfully removed
        files_failed: Number of files that failed to remove
        size_freed: Total size freed in bytes
        errors: List of error messages
    """
    success: bool
    files_removed: int
    files_failed: int
    size_freed: int
    errors: List[str] = field(default_factory=list)


@dataclass
class ArchiveResult:
    """Results from cache archival operation.
    
    Attributes:
        success: Whether archival completed successfully
        files_archived: Number of files archived
        archive_path: Path to the archive directory
        errors: List of error messages
    """
    success: bool
    files_archived: int
    archive_path: Path
    errors: List[str] = field(default_factory=list)


@dataclass
class ConsolidationResult:
    """Results from dependency consolidation operation.
    
    Attributes:
        success: Whether consolidation completed successfully
        dependencies_merged: Number of dependencies merged
        files_removed: Number of requirements files removed
        duplicates_found: Number of duplicate dependencies detected
        conflicts: List of version conflicts found
        errors: List of error messages
    """
    success: bool
    dependencies_merged: int
    files_removed: int
    duplicates_found: int
    conflicts: List[str] = field(default_factory=list)
    errors: List[str] = field(default_factory=list)


@dataclass
class RestoreResult:
    """Results from backup restoration operation.
    
    Attributes:
        success: Whether restoration completed successfully
        files_restored: Number of files successfully restored
        files_failed: Number of files that failed to restore
        errors: List of error messages
    """
    success: bool
    files_restored: int
    files_failed: int
    errors: List[str] = field(default_factory=list)


@dataclass
class TestResult:
    """Results from test suite execution.
    
    Attributes:
        passed: Whether all tests passed
        tests_run: Number of tests executed
        tests_failed: Number of tests that failed
        output: Test execution output
    """
    passed: bool
    tests_run: int
    tests_failed: int
    output: str


@dataclass
class ImportResult:
    """Results from import validation.
    
    Attributes:
        passed: Whether all imports succeeded
        successful_imports: List of successfully imported modules
        failed_imports: List of modules that failed to import
        errors: List of error messages
    """
    passed: bool
    successful_imports: List[str] = field(default_factory=list)
    failed_imports: List[str] = field(default_factory=list)
    errors: List[str] = field(default_factory=list)


@dataclass
class CLIResult:
    """Results from CLI entry point validation.
    
    Attributes:
        passed: Whether all CLI commands succeeded
        successful_commands: List of commands that executed successfully
        failed_commands: List of commands that failed
        errors: List of error messages
    """
    passed: bool
    successful_commands: List[str] = field(default_factory=list)
    failed_commands: List[str] = field(default_factory=list)
    errors: List[str] = field(default_factory=list)


@dataclass
class BuildResult:
    """Results from package build validation.
    
    Attributes:
        passed: Whether build succeeded
        package_size: Size of built package in bytes
        output: Build command output
        errors: List of error messages
    """
    passed: bool
    package_size: int = 0
    output: str = ""
    errors: List[str] = field(default_factory=list)


@dataclass
class ErrorContext:
    """Context information for error handling.
    
    Attributes:
        operation: Name of the operation that failed
        file_path: Path to file involved in the error (if applicable)
        error_type: Type of error that occurred
        message: Error message
        can_continue: Whether cleanup can continue after this error
        should_rollback: Whether rollback is required
    """
    operation: str
    file_path: Optional[Path] = None
    error_type: str = ""
    message: str = ""
    can_continue: bool = True
    should_rollback: bool = False


class RecoveryAction(Enum):
    """Actions to take when recovering from errors."""
    CONTINUE = "continue"  # Log error, skip item, continue with remaining
    ABORT = "abort"  # Stop cleanup, preserve current state, no rollback
    ROLLBACK = "rollback"  # Stop cleanup, restore from backup
