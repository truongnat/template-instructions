#!/usr/bin/env python3
"""
CLI Entry Point for Project Audit and Cleanup System.

This script provides a command-line interface for auditing and cleaning up
the Agentic SDLC project. It supports various modes including audit-only,
dry-run, backup, and rollback operations.

Usage:
    python scripts/cleanup.py --audit-only
    python scripts/cleanup.py --dry-run
    python scripts/cleanup.py --backup
    python scripts/cleanup.py --rollback <backup_id>
    python scripts/cleanup.py --verbose

Requirements Addressed:
    - 13.1: Create reusable cleanup script
    - 13.2: Provide command-line flags
    - 13.3: Support dry-run mode
    - 13.4: Support audit-only mode
    - 13.5: Include comprehensive logging
"""

import sys
import argparse
from pathlib import Path
from typing import Optional

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from scripts.cleanup.audit import AuditEngine
from scripts.cleanup.cleanup import CleanupEngine
from scripts.cleanup.backup import BackupManager
from scripts.cleanup.scanner import FileScanner
from scripts.cleanup.categorizer import FileCategorizer
from scripts.cleanup.validator import Validator
from scripts.cleanup.reporter import ReportGenerator
from scripts.cleanup.logger import get_logger


class CleanupCLI:
    """Command-line interface for the cleanup system.
    
    Provides a user-friendly interface for all cleanup operations including
    audit, cleanup, backup, and rollback functionality.
    
    Attributes:
        project_root: Root directory of the project
        backup_dir: Directory for storing backups
        verbose: Enable verbose logging
        logger: Logger instance
    """
    
    def __init__(self, project_root: Path, verbose: bool = False):
        """Initialize the CLI.
        
        Args:
            project_root: Root directory of the project
            verbose: Enable verbose logging
        """
        self.project_root = Path(project_root).resolve()
        self.backup_dir = self.project_root / ".cleanup_backup"
        self.verbose = verbose
        self.logger = get_logger(verbose=verbose)
        
        # Initialize components
        self.scanner = FileScanner(verbose=verbose)
        self.categorizer = FileCategorizer(verbose=verbose)
        self.backup_manager = BackupManager(self.backup_dir, verbose=verbose)
        self.validator = Validator(self.project_root)
        self.audit_engine = AuditEngine(self.scanner, self.categorizer, verbose=verbose)
        self.cleanup_engine = CleanupEngine(
            self.project_root,
            self.backup_manager,
            self.validator,
            verbose=verbose
        )
        self.report_generator = ReportGenerator(
            docs_dir=self.project_root / "docs",
            verbose=verbose
        )
    
    def run_audit_only(self) -> int:
        """Generate audit report without performing cleanup.
        
        Returns:
            Exit code (0 for success, 1 for failure)
        """
        self.logger.info("=== AUDIT MODE ===")
        self.logger.info(f"Project root: {self.project_root}")
        
        try:
            # Generate audit report
            report = self.audit_engine.generate_report(self.project_root)
            
            # Save report
            report_path = self.report_generator.save_audit_report(report)
            
            self.logger.info(f"Audit report saved to: {report_path}")
            
            # Print summary to console
            print("\n" + "=" * 80)
            print("AUDIT SUMMARY")
            print("=" * 80)
            print(f"Total files scanned: {report.total_files:,}")
            print(f"Files to keep: {len(report.categorized_files.keep):,}")
            print(f"Files to remove: {len(report.categorized_files.remove):,}")
            print(f"Files to consolidate: {len(report.categorized_files.consolidate):,}")
            print(f"Files to archive: {len(report.categorized_files.archive):,}")
            print()
            print(f"Current size: {report.size_impact.current_size / (1024*1024):.2f} MB")
            print(f"Projected size: {report.size_impact.projected_size / (1024*1024):.2f} MB")
            print(f"Reduction: {report.size_impact.reduction / (1024*1024):.2f} MB ({report.size_impact.reduction_percent:.1f}%)")
            print()
            print(f"Full report: {report_path}")
            print("=" * 80)
            
            return 0
            
        except Exception as e:
            self.logger.error(f"Audit failed: {e}")
            return 1
    
    def run_cleanup(self, dry_run: bool = False, create_backup: bool = True) -> int:
        """Execute cleanup with optional dry-run mode.
        
        Args:
            dry_run: If True, show what would be done without executing
            create_backup: If True, create backup before cleanup
        
        Returns:
            Exit code (0 for success, 1 for failure)
        """
        mode = "DRY RUN" if dry_run else "CLEANUP"
        self.logger.info(f"=== {mode} MODE ===")
        self.logger.info(f"Project root: {self.project_root}")
        self.logger.info(f"Backup: {'enabled' if create_backup else 'disabled'}")
        
        try:
            # First, run audit to categorize files
            self.logger.info("Running audit...")
            report = self.audit_engine.generate_report(self.project_root)
            
            # Save audit report
            audit_report_path = self.report_generator.save_audit_report(report)
            self.logger.info(f"Audit report saved to: {audit_report_path}")
            
            # Execute cleanup
            self.logger.info("Starting cleanup...")
            result = self.cleanup_engine.cleanup(
                report.categorized_files,
                dry_run=dry_run,
                skip_validation=dry_run  # Skip validation in dry-run mode
            )
            
            # Print results
            print("\n" + "=" * 80)
            print(f"{mode} RESULTS")
            print("=" * 80)
            
            if dry_run:
                print("DRY RUN - No changes were made")
                print()
                print(f"Would remove: {result.files_removed} files")
                print(f"Would free: {result.size_freed / (1024*1024):.2f} MB")
            else:
                if result.success:
                    print("Cleanup completed successfully!")
                    print()
                    print(f"Files removed: {result.files_removed}")
                    print(f"Size freed: {result.size_freed / (1024*1024):.2f} MB")
                    print(f"Backup ID: {result.backup_id}")
                    
                    if result.validation_result:
                        print()
                        print("Validation Results:")
                        print(f"  Import check: {'PASS' if result.validation_result.import_check else 'FAIL'}")
                        print(f"  CLI check: {'PASS' if result.validation_result.cli_check else 'FAIL'}")
                        print(f"  Test check: {'PASS' if result.validation_result.test_check else 'FAIL'}")
                        print(f"  Build check: {'PASS' if result.validation_result.build_check else 'FAIL'}")
                    
                    # Generate and save cleanup summary
                    summary_path = self.report_generator.save_cleanup_summary(result)
                    print()
                    print(f"Cleanup summary: {summary_path}")
                else:
                    print("Cleanup failed!")
                    print()
                    if result.errors:
                        print("Errors:")
                        for error in result.errors:
                            print(f"  - {error}")
                    
                    if result.validation_result and not result.validation_result.passed:
                        print()
                        print("Validation failed - cleanup was rolled back")
            
            print("=" * 80)
            
            return 0 if result.success else 1
            
        except Exception as e:
            self.logger.error(f"Cleanup failed: {e}")
            import traceback
            traceback.print_exc()
            return 1
    
    def run_rollback(self, backup_id: str) -> int:
        """Restore from a specific backup.
        
        Args:
            backup_id: ID of the backup to restore
        
        Returns:
            Exit code (0 for success, 1 for failure)
        """
        self.logger.info("=== ROLLBACK MODE ===")
        self.logger.info(f"Backup ID: {backup_id}")
        
        try:
            # Verify backup exists
            backup_info = self.backup_manager.get_backup_info(backup_id)
            if not backup_info:
                self.logger.error(f"Backup not found: {backup_id}")
                print(f"Error: Backup '{backup_id}' does not exist")
                print()
                print("Available backups:")
                self.list_backups()
                return 1
            
            # Confirm rollback
            print(f"Backup: {backup_id}")
            print(f"Created: {backup_info.timestamp}")
            print(f"Files: {backup_info.file_count}")
            print(f"Size: {backup_info.total_size / (1024*1024):.2f} MB")
            print()
            
            response = input("Restore this backup? This will overwrite existing files. (yes/no): ")
            if response.lower() not in ['yes', 'y']:
                print("Rollback cancelled")
                return 0
            
            # Perform rollback
            self.logger.info("Restoring backup...")
            result = self.backup_manager.restore_backup(backup_id)
            
            # Print results
            print("\n" + "=" * 80)
            print("ROLLBACK RESULTS")
            print("=" * 80)
            
            if result.success:
                print("Rollback completed successfully!")
                print()
                print(f"Files restored: {result.files_restored}")
            else:
                print("Rollback failed!")
                print()
                print(f"Files restored: {result.files_restored}")
                print(f"Files failed: {result.files_failed}")
                print()
                if result.errors:
                    print("Errors:")
                    for error in result.errors:
                        print(f"  - {error}")
            
            print("=" * 80)
            
            return 0 if result.success else 1
            
        except Exception as e:
            self.logger.error(f"Rollback failed: {e}")
            import traceback
            traceback.print_exc()
            return 1
    
    def list_backups(self) -> int:
        """List all available backups.
        
        Returns:
            Exit code (0 for success, 1 for failure)
        """
        try:
            backups = self.backup_manager.list_backups()
            
            if not backups:
                print("No backups found")
                return 0
            
            print("\n" + "=" * 80)
            print("AVAILABLE BACKUPS")
            print("=" * 80)
            
            for backup in backups:
                print(f"ID: {backup.backup_id}")
                print(f"  Created: {backup.timestamp}")
                print(f"  Files: {backup.file_count}")
                print(f"  Size: {backup.total_size / (1024*1024):.2f} MB")
                print()
            
            print("=" * 80)
            
            return 0
            
        except Exception as e:
            self.logger.error(f"Failed to list backups: {e}")
            return 1


def main():
    """Main entry point for the CLI."""
    parser = argparse.ArgumentParser(
        description="Project Audit and Cleanup System for Agentic SDLC",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Generate audit report only
  python scripts/cleanup.py --audit-only
  
  # Perform cleanup with backup (default)
  python scripts/cleanup.py
  
  # Dry run - show what would be done
  python scripts/cleanup.py --dry-run
  
  # Cleanup without backup (not recommended)
  python scripts/cleanup.py --no-backup
  
  # List available backups
  python scripts/cleanup.py --list-backups
  
  # Rollback to a specific backup
  python scripts/cleanup.py --rollback backup_20260131_143022
  
  # Verbose output
  python scripts/cleanup.py --verbose --audit-only
        """
    )
    
    # Mode selection flags
    mode_group = parser.add_mutually_exclusive_group()
    mode_group.add_argument(
        "--audit-only",
        action="store_true",
        help="Generate audit report without performing cleanup"
    )
    mode_group.add_argument(
        "--dry-run",
        action="store_true",
        help="Show what would be done without executing changes"
    )
    mode_group.add_argument(
        "--rollback",
        metavar="BACKUP_ID",
        type=str,
        help="Restore from a specific backup"
    )
    mode_group.add_argument(
        "--list-backups",
        action="store_true",
        help="List all available backups"
    )
    
    # Backup control
    parser.add_argument(
        "--no-backup",
        action="store_true",
        help="Skip backup creation (not recommended)"
    )
    
    # Logging control
    parser.add_argument(
        "--verbose",
        "-v",
        action="store_true",
        help="Enable verbose logging"
    )
    
    # Project root
    parser.add_argument(
        "--project-root",
        type=Path,
        default=Path.cwd(),
        help="Root directory of the project (default: current directory)"
    )
    
    args = parser.parse_args()
    
    # Initialize CLI
    cli = CleanupCLI(args.project_root, verbose=args.verbose)
    
    # Execute requested operation
    try:
        if args.audit_only:
            return cli.run_audit_only()
        elif args.dry_run:
            return cli.run_cleanup(dry_run=True)
        elif args.rollback:
            return cli.run_rollback(args.rollback)
        elif args.list_backups:
            return cli.list_backups()
        else:
            # Default: run cleanup with backup
            create_backup = not args.no_backup
            return cli.run_cleanup(dry_run=False, create_backup=create_backup)
    
    except KeyboardInterrupt:
        print("\n\nOperation cancelled by user")
        return 130  # Standard exit code for SIGINT
    except Exception as e:
        print(f"\nFatal error: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
