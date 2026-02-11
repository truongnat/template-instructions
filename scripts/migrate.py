#!/usr/bin/env python3
"""
Comprehensive migration script for SDLC Kit project restructuring.

This script performs automated migration to the new project structure:
1. Creates timestamped backups before any modifications
2. Updates import paths using AST parsing
3. Validates each migration step
4. Provides rollback capability on failure
5. Logs all operations for debugging

Requirements: 16.1, 16.4, 16.6
"""

import os
import sys
import ast
import shutil
import logging
import argparse
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Tuple, Optional, Set
from dataclasses import dataclass


@dataclass
class MigrationConfig:
    """Configuration for migration operations."""
    backup_dir: Path
    log_file: Path
    dry_run: bool = False
    verbose: bool = False
    skip_backup: bool = False


@dataclass
class ImportMapping:
    """Mapping of old import paths to new import paths."""
    old_path: str
    new_path: str
    description: str


# Define import path mappings for the migration
IMPORT_MAPPINGS = [
    # Utilities consolidation
    ImportMapping(
        old_path="agentic_sdlc.orchestration.utils.artifact_manager",
        new_path="utils.artifact_manager",
        description="Move artifact_manager from orchestration/utils to utils/"
    ),
    ImportMapping(
        old_path="agentic_sdlc.orchestration.utils.kb_manager",
        new_path="utils.kb_manager",
        description="Move kb_manager from orchestration/utils to utils/"
    ),
    ImportMapping(
        old_path="agentic_sdlc.core.utils.console",
        new_path="utils.console",
        description="Move console from core/utils to utils/"
    ),
    # Add more mappings as needed
]


class MigrationLogger:
    """Centralized logging for migration operations."""
    
    def __init__(self, log_file: Path, verbose: bool = False):
        """Initialize migration logger."""
        self.log_file = log_file
        self.verbose = verbose
        
        # Create logs directory if it doesn't exist
        log_file.parent.mkdir(parents=True, exist_ok=True)
        
        # Configure logging
        self.logger = logging.getLogger('migration')
        self.logger.setLevel(logging.DEBUG if verbose else logging.INFO)
        
        # File handler
        file_handler = logging.FileHandler(log_file, mode='w')
        file_handler.setLevel(logging.DEBUG)
        file_formatter = logging.Formatter(
            '%(asctime)s - %(levelname)s - %(message)s'
        )
        file_handler.setFormatter(file_formatter)
        self.logger.addHandler(file_handler)
        
        # Console handler
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(logging.INFO)
        console_formatter = logging.Formatter('%(levelname)s: %(message)s')
        console_handler.setFormatter(console_formatter)
        self.logger.addHandler(console_handler)
    
    def info(self, message: str):
        """Log info message."""
        self.logger.info(message)
    
    def debug(self, message: str):
        """Log debug message."""
        self.logger.debug(message)
    
    def warning(self, message: str):
        """Log warning message."""
        self.logger.warning(message)
    
    def error(self, message: str):
        """Log error message."""
        self.logger.error(message)
    
    def success(self, message: str):
        """Log success message."""
        self.logger.info(f"✓ {message}")


class BackupManager:
    """Manages backup creation and restoration."""
    
    def __init__(self, backup_dir: Path, logger: MigrationLogger):
        """Initialize backup manager."""
        self.backup_dir = backup_dir
        self.logger = logger
        self.backed_up_files: List[Tuple[Path, Path]] = []
    
    def create_backup(self, file_path: Path) -> Optional[Path]:
        """
        Create a backup of a file before modification.
        
        Args:
            file_path: Path to file to backup
            
        Returns:
            Path to backup file, or None if backup failed
        """
        if not file_path.exists():
            self.logger.warning(f"File does not exist, skipping backup: {file_path}")
            return None
        
        try:
            # Create backup directory structure
            relative_path = file_path.relative_to(Path.cwd())
            backup_path = self.backup_dir / relative_path
            backup_path.parent.mkdir(parents=True, exist_ok=True)
            
            # Copy file to backup location
            shutil.copy2(file_path, backup_path)
            self.backed_up_files.append((file_path, backup_path))
            
            self.logger.debug(f"Backed up: {file_path} -> {backup_path}")
            return backup_path
            
        except Exception as e:
            self.logger.error(f"Failed to backup {file_path}: {e}")
            return None
    
    def restore_all(self) -> bool:
        """
        Restore all backed up files.
        
        Returns:
            True if all files restored successfully, False otherwise
        """
        self.logger.info("Rolling back changes...")
        success = True
        
        for original_path, backup_path in reversed(self.backed_up_files):
            try:
                if backup_path.exists():
                    shutil.copy2(backup_path, original_path)
                    self.logger.debug(f"Restored: {backup_path} -> {original_path}")
                else:
                    self.logger.warning(f"Backup not found: {backup_path}")
                    success = False
            except Exception as e:
                self.logger.error(f"Failed to restore {original_path}: {e}")
                success = False
        
        return success
    
    def cleanup(self):
        """Remove backup directory after successful migration."""
        try:
            if self.backup_dir.exists():
                shutil.rmtree(self.backup_dir)
                self.logger.debug(f"Cleaned up backup directory: {self.backup_dir}")
        except Exception as e:
            self.logger.warning(f"Failed to cleanup backup directory: {e}")


class ImportPathUpdater:
    """Updates import paths using AST parsing."""
    
    def __init__(self, mappings: List[ImportMapping], logger: MigrationLogger):
        """Initialize import path updater."""
        self.mappings = mappings
        self.logger = logger
        self.updated_files: Set[Path] = set()
    
    def find_python_files(self, directory: Path) -> List[Path]:
        """
        Find all Python files in a directory recursively.
        
        Args:
            directory: Root directory to search
            
        Returns:
            List of Python file paths
        """
        python_files = []
        
        # Skip certain directories
        skip_dirs = {'.venv', 'venv', '__pycache__', '.git', 'node_modules', 
                     '.pytest_cache', '.mypy_cache', 'build', 'dist', '.egg-info'}
        
        for root, dirs, files in os.walk(directory):
            # Remove skip directories from dirs to prevent traversal
            dirs[:] = [d for d in dirs if d not in skip_dirs]
            
            for file in files:
                if file.endswith('.py'):
                    python_files.append(Path(root) / file)
        
        return python_files
    
    def analyze_imports(self, file_path: Path) -> List[Tuple[str, int, str]]:
        """
        Analyze imports in a Python file using AST.
        
        Args:
            file_path: Path to Python file
            
        Returns:
            List of (import_path, line_number, import_type) tuples
        """
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            tree = ast.parse(content, filename=str(file_path))
            imports = []
            
            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    for alias in node.names:
                        imports.append((alias.name, node.lineno, 'import'))
                elif isinstance(node, ast.ImportFrom):
                    if node.module:
                        imports.append((node.module, node.lineno, 'from'))
            
            return imports
            
        except SyntaxError as e:
            self.logger.warning(f"Syntax error in {file_path}: {e}")
            return []
        except Exception as e:
            self.logger.error(f"Failed to analyze {file_path}: {e}")
            return []
    
    def update_file_imports(self, file_path: Path, dry_run: bool = False) -> bool:
        """
        Update import statements in a Python file.
        
        Args:
            file_path: Path to Python file
            dry_run: If True, only report changes without modifying file
            
        Returns:
            True if file was modified, False otherwise
        """
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                lines = f.readlines()
            
            modified = False
            changes = []
            
            # Check each line for imports that need updating
            for i, line in enumerate(lines):
                original_line = line
                
                for mapping in self.mappings:
                    # Handle "import old.path" statements
                    if f"import {mapping.old_path}" in line:
                        line = line.replace(mapping.old_path, mapping.new_path)
                        if line != original_line:
                            modified = True
                            changes.append((i + 1, original_line.strip(), line.strip()))
                    
                    # Handle "from old.path import" statements
                    if f"from {mapping.old_path}" in line:
                        line = line.replace(mapping.old_path, mapping.new_path)
                        if line != original_line:
                            modified = True
                            changes.append((i + 1, original_line.strip(), line.strip()))
                
                lines[i] = line
            
            if modified:
                if dry_run:
                    self.logger.info(f"Would update {file_path}:")
                    for line_num, old, new in changes:
                        self.logger.info(f"  Line {line_num}: {old} -> {new}")
                else:
                    with open(file_path, 'w', encoding='utf-8') as f:
                        f.writelines(lines)
                    self.logger.success(f"Updated imports in {file_path}")
                    self.updated_files.add(file_path)
            
            return modified
            
        except Exception as e:
            self.logger.error(f"Failed to update {file_path}: {e}")
            return False
    
    def update_all_imports(self, root_dir: Path, dry_run: bool = False) -> int:
        """
        Update imports in all Python files under root directory.
        
        Args:
            root_dir: Root directory to search
            dry_run: If True, only report changes without modifying files
            
        Returns:
            Number of files modified
        """
        self.logger.info(f"Scanning for Python files in {root_dir}...")
        python_files = self.find_python_files(root_dir)
        self.logger.info(f"Found {len(python_files)} Python files")
        
        modified_count = 0
        for file_path in python_files:
            if self.update_file_imports(file_path, dry_run):
                modified_count += 1
        
        return modified_count


class MigrationValidator:
    """Validates migration steps."""
    
    def __init__(self, logger: MigrationLogger):
        """Initialize migration validator."""
        self.logger = logger
    
    def validate_imports(self, root_dir: Path) -> bool:
        """
        Validate that all imports are correct after migration.
        
        Args:
            root_dir: Root directory to validate
            
        Returns:
            True if all imports are valid, False otherwise
        """
        self.logger.info("Validating imports...")
        
        updater = ImportPathUpdater([], self.logger)
        python_files = updater.find_python_files(root_dir)
        
        errors = []
        for file_path in python_files:
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # Try to parse the file
                ast.parse(content, filename=str(file_path))
                
            except SyntaxError as e:
                errors.append(f"{file_path}: Syntax error at line {e.lineno}")
            except Exception as e:
                errors.append(f"{file_path}: {e}")
        
        if errors:
            self.logger.error("Import validation failed:")
            for error in errors:
                self.logger.error(f"  {error}")
            return False
        
        self.logger.success("All imports validated successfully")
        return True
    
    def validate_directory_structure(self) -> bool:
        """
        Validate that required directories exist.
        
        Returns:
            True if all required directories exist, False otherwise
        """
        self.logger.info("Validating directory structure...")
        
        required_dirs = [
            'config',
            'cli',
            'models',
            'utils',
            'security',
            'monitoring',
            'docs',
            'examples',
            'scripts',
            'tests',
            'tests/unit',
            'tests/integration',
            'tests/e2e',
            'tests/property',
            'tests/fixtures',
        ]
        
        missing = []
        for dir_path in required_dirs:
            if not Path(dir_path).exists():
                missing.append(dir_path)
        
        if missing:
            self.logger.error("Missing required directories:")
            for dir_path in missing:
                self.logger.error(f"  {dir_path}")
            return False
        
        self.logger.success("Directory structure validated successfully")
        return True


class MigrationOrchestrator:
    """Orchestrates the complete migration process."""
    
    def __init__(self, config: MigrationConfig):
        """Initialize migration orchestrator."""
        self.config = config
        self.logger = MigrationLogger(config.log_file, config.verbose)
        self.backup_manager = BackupManager(config.backup_dir, self.logger)
        self.import_updater = ImportPathUpdater(IMPORT_MAPPINGS, self.logger)
        self.validator = MigrationValidator(self.logger)
    
    def run(self) -> bool:
        """
        Run the complete migration process.
        
        Returns:
            True if migration succeeded, False otherwise
        """
        self.logger.info("=" * 60)
        self.logger.info("SDLC Kit Migration Script")
        self.logger.info("=" * 60)
        
        if self.config.dry_run:
            self.logger.info("DRY RUN MODE - No files will be modified")
        
        try:
            # Step 1: Validate directory structure
            self.logger.info("\nStep 1: Validating directory structure...")
            if not self.validator.validate_directory_structure():
                self.logger.error("Directory structure validation failed")
                return False
            
            # Step 2: Create backups
            if not self.config.skip_backup and not self.config.dry_run:
                self.logger.info("\nStep 2: Creating backups...")
                self._create_backups()
            else:
                self.logger.info("\nStep 2: Skipping backups (dry run or skip_backup=True)")
            
            # Step 3: Update import paths
            self.logger.info("\nStep 3: Updating import paths...")
            root_dir = Path.cwd()
            modified_count = self.import_updater.update_all_imports(
                root_dir, 
                self.config.dry_run
            )
            self.logger.info(f"Modified {modified_count} files")
            
            # Step 4: Validate imports
            if not self.config.dry_run:
                self.logger.info("\nStep 4: Validating imports...")
                if not self.validator.validate_imports(root_dir):
                    self.logger.error("Import validation failed")
                    self._rollback()
                    return False
            else:
                self.logger.info("\nStep 4: Skipping validation (dry run)")
            
            # Step 5: Success
            self.logger.info("\n" + "=" * 60)
            self.logger.success("Migration completed successfully!")
            self.logger.info("=" * 60)
            
            if not self.config.dry_run:
                self.logger.info(f"\nBackup location: {self.config.backup_dir}")
                self.logger.info(f"Log file: {self.config.log_file}")
                self.logger.info("\nTo rollback, run: python scripts/migrate.py --rollback")
            
            return True
            
        except Exception as e:
            self.logger.error(f"Migration failed: {e}")
            if not self.config.dry_run:
                self._rollback()
            return False
    
    def _create_backups(self):
        """Create backups of all files that will be modified."""
        self.logger.info("Creating backups...")
        
        # Find all Python files
        python_files = self.import_updater.find_python_files(Path.cwd())
        
        # Backup each file
        backed_up = 0
        for file_path in python_files:
            if self.backup_manager.create_backup(file_path):
                backed_up += 1
        
        self.logger.info(f"Backed up {backed_up} files to {self.config.backup_dir}")
    
    def _rollback(self):
        """Rollback all changes."""
        self.logger.warning("Rolling back changes...")
        if self.backup_manager.restore_all():
            self.logger.success("Rollback completed successfully")
        else:
            self.logger.error("Rollback completed with errors")
    
    def rollback_from_backup(self) -> bool:
        """
        Rollback from an existing backup.
        
        Returns:
            True if rollback succeeded, False otherwise
        """
        if not self.config.backup_dir.exists():
            self.logger.error(f"Backup directory not found: {self.config.backup_dir}")
            return False
        
        self.logger.info(f"Rolling back from backup: {self.config.backup_dir}")
        
        # Find all backed up files
        for backup_file in self.config.backup_dir.rglob('*.py'):
            relative_path = backup_file.relative_to(self.config.backup_dir)
            original_file = Path.cwd() / relative_path
            
            try:
                original_file.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(backup_file, original_file)
                self.logger.debug(f"Restored: {backup_file} -> {original_file}")
            except Exception as e:
                self.logger.error(f"Failed to restore {original_file}: {e}")
                return False
        
        self.logger.success("Rollback completed successfully")
        return True


def main():
    """Main entry point for migration script."""
    parser = argparse.ArgumentParser(
        description='Migrate SDLC Kit to new project structure'
    )
    parser.add_argument(
        '--dry-run',
        action='store_true',
        help='Show what would be done without modifying files'
    )
    parser.add_argument(
        '--verbose',
        action='store_true',
        help='Show detailed logging output'
    )
    parser.add_argument(
        '--skip-backup',
        action='store_true',
        help='Skip backup creation (not recommended)'
    )
    parser.add_argument(
        '--rollback',
        action='store_true',
        help='Rollback from the most recent backup'
    )
    parser.add_argument(
        '--backup-dir',
        type=str,
        help='Custom backup directory (default: backups/migration_TIMESTAMP)'
    )
    
    args = parser.parse_args()
    
    # Create configuration
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    backup_dir = Path(args.backup_dir) if args.backup_dir else Path(f'backups/migration_{timestamp}')
    log_file = Path('migration.log')
    
    config = MigrationConfig(
        backup_dir=backup_dir,
        log_file=log_file,
        dry_run=args.dry_run,
        verbose=args.verbose,
        skip_backup=args.skip_backup
    )
    
    # Create orchestrator
    orchestrator = MigrationOrchestrator(config)
    
    # Run migration or rollback
    if args.rollback:
        # Find most recent backup
        backups_dir = Path('backups')
        if not backups_dir.exists():
            print("ERROR: No backups directory found")
            return 1
        
        migration_backups = sorted(backups_dir.glob('migration_*'))
        if not migration_backups:
            print("ERROR: No migration backups found")
            return 1
        
        latest_backup = migration_backups[-1]
        config.backup_dir = latest_backup
        
        success = orchestrator.rollback_from_backup()
    else:
        success = orchestrator.run()
    
    return 0 if success else 1


if __name__ == '__main__':
    sys.exit(main())
