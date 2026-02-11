"""
Project Audit and Cleanup System

A comprehensive tool for auditing, categorizing, and safely removing unnecessary
files from the Agentic SDLC project. Includes backup, rollback, and validation
capabilities to ensure safe cleanup operations.

Main Components:
    - FileScanner: Recursively scan project directories
    - FileCategorizer: Categorize files into KEEP/REMOVE/CONSOLIDATE/ARCHIVE
    - BackupManager: Create and manage backups before removal
    - CleanupEngine: Execute safe cleanup operations
    - AuditEngine: Generate audit reports
    - Validator: Validate project integrity after cleanup

Usage:
    from cleanup import get_logger, FileCategory, FileInfo
    
    logger = get_logger(verbose=True)
    logger.info("Starting cleanup operation")
"""

from .models import (
    # Enums
    FileCategory,
    RecoveryAction,
    
    # Core data structures
    FileInfo,
    DirectoryInfo,
    Dependency,
    BackupInfo,
    ProjectInventory,
    CategorizedFiles,
    SizeImpact,
    
    # Result types
    ValidationResult,
    CleanupResult,
    AuditReport,
    RemovalResult,
    ArchiveResult,
    ConsolidationResult,
    RestoreResult,
    TestResult,
    ImportResult,
    CLIResult,
    BuildResult,
    
    # Error handling
    ErrorContext,
)

from .logger import get_logger, CleanupLogger
from .scanner import FileScanner
from .categorizer import FileCategorizer
from .backup import BackupManager
from .dependencies import DependencyConsolidator
from .validator import Validator
from .audit import AuditEngine
from .cleanup import CleanupEngine
from .reporter import ReportGenerator
from .manifest import ManifestUpdater
from .docs import DocumentationUpdater
from .imports import ImportDetector, ImportReference

__version__ = "1.0.0"

__all__ = [
    # Enums
    "FileCategory",
    "RecoveryAction",
    
    # Core data structures
    "FileInfo",
    "DirectoryInfo",
    "Dependency",
    "BackupInfo",
    "ProjectInventory",
    "CategorizedFiles",
    "SizeImpact",
    
    # Result types
    "ValidationResult",
    "CleanupResult",
    "AuditReport",
    "RemovalResult",
    "ArchiveResult",
    "ConsolidationResult",
    "RestoreResult",
    "TestResult",
    "ImportResult",
    "CLIResult",
    "BuildResult",
    
    # Error handling
    "ErrorContext",
    
    # Logging
    "get_logger",
    "CleanupLogger",
    
    # Services
    "FileScanner",
    "FileCategorizer",
    "BackupManager",
    "DependencyConsolidator",
    "Validator",
    "AuditEngine",
    "CleanupEngine",
    "ReportGenerator",
    "ManifestUpdater",
    "DocumentationUpdater",
    "ImportDetector",
    "ImportReference",
]
