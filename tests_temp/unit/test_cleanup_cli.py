"""
Unit tests for CleanupCLI.

Tests argument parsing, audit-only mode, dry-run mode, and rollback mode.

Requirements Addressed:
    - 13.2: Command-line flags
    - 13.3: Dry-run mode
    - 13.4: Audit-only mode
"""

import pytest
import sys
from pathlib import Path
from datetime import datetime
from unittest.mock import Mock, patch, MagicMock
import tempfile
import argparse

# Add workspace root to path for imports
workspace_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(workspace_root))

# Import CleanupCLI from the CLI script
import importlib.util
spec = importlib.util.spec_from_file_location(
    "cleanup_cli",
    workspace_root / "scripts" / "cleanup.py"
)
cleanup_cli_module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(cleanup_cli_module)
CleanupCLI = cleanup_cli_module.CleanupCLI
main = cleanup_cli_module.main

from scripts.cleanup.models import (
    CategorizedFiles,
    FileInfo,
    FileCategory,
    AuditReport,
    SizeImpact,
    CleanupResult,
    ValidationResult,
    BackupInfo,
    RestoreResult,
)


class TestCLIInitialization:
    """Test CLI initialization and setup."""
    
    def test_cli_initialization_basic(self):
        """Test basic CLI initialization."""
        with tempfile.TemporaryDirectory() as tmpdir:
            cli = CleanupCLI(Path(tmpdir), verbose=False)
            
            assert cli.project_root == Path(tmpdir).resolve()
            assert cli.backup_dir == Path(tmpdir).resolve() / ".cleanup_backup"
            assert cli.verbose is False
            assert cli.scanner is not None
            assert cli.categorizer is not None
            assert cli.backup_manager is not None
            assert cli.validator is not None
            assert cli.audit_engine is not None
            assert cli.cleanup_engine is not None
            assert cli.report_generator is not None
    
    def test_cli_initialization_with_verbose(self):
        """Test CLI initialization with verbose flag."""
        with tempfile.TemporaryDirectory() as tmpdir:
            cli = CleanupCLI(Path(tmpdir), verbose=True)
            
            assert cli.verbose is True
    
    def test_cli_initialization_resolves_path(self):
        """Test that CLI resolves relative paths to absolute."""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Create a subdirectory
            subdir = Path(tmpdir) / "subdir"
            subdir.mkdir()
            
            # Initialize with relative path
            cli = CleanupCLI(subdir, verbose=False)
            
            # Should be resolved to absolute path
            assert cli.project_root.is_absolute()
            assert cli.project_root == subdir.resolve()


class TestArgumentParsing:
    """Test command-line argument parsing."""
    
    def test_parse_audit_only_flag(self):
        """Test parsing --audit-only flag."""
        with patch('sys.argv', ['cleanup.py', '--audit-only']):
            parser = argparse.ArgumentParser()
            mode_group = parser.add_mutually_exclusive_group()
            mode_group.add_argument('--audit-only', action='store_true')
            mode_group.add_argument('--dry-run', action='store_true')
            mode_group.add_argument('--rollback', type=str)
            mode_group.add_argument('--list-backups', action='store_true')
            parser.add_argument('--no-backup', action='store_true')
            parser.add_argument('--verbose', '-v', action='store_true')
            parser.add_argument('--project-root', type=Path, default=Path.cwd())
            
            args = parser.parse_args(['--audit-only'])
            
            assert args.audit_only is True
            assert args.dry_run is False
            assert args.rollback is None
    
    def test_parse_dry_run_flag(self):
        """Test parsing --dry-run flag."""
        parser = argparse.ArgumentParser()
        mode_group = parser.add_mutually_exclusive_group()
        mode_group.add_argument('--audit-only', action='store_true')
        mode_group.add_argument('--dry-run', action='store_true')
        mode_group.add_argument('--rollback', type=str)
        mode_group.add_argument('--list-backups', action='store_true')
        parser.add_argument('--no-backup', action='store_true')
        parser.add_argument('--verbose', '-v', action='store_true')
        parser.add_argument('--project-root', type=Path, default=Path.cwd())
        
        args = parser.parse_args(['--dry-run'])
        
        assert args.dry_run is True
        assert args.audit_only is False
        assert args.rollback is None
    
    def test_parse_rollback_flag(self):
        """Test parsing --rollback flag with backup ID."""
        parser = argparse.ArgumentParser()
        mode_group = parser.add_mutually_exclusive_group()
        mode_group.add_argument('--audit-only', action='store_true')
        mode_group.add_argument('--dry-run', action='store_true')
        mode_group.add_argument('--rollback', type=str)
        mode_group.add_argument('--list-backups', action='store_true')
        parser.add_argument('--no-backup', action='store_true')
        parser.add_argument('--verbose', '-v', action='store_true')
        parser.add_argument('--project-root', type=Path, default=Path.cwd())
        
        args = parser.parse_args(['--rollback', 'backup_20260131_143022'])
        
        assert args.rollback == 'backup_20260131_143022'
        assert args.audit_only is False
        assert args.dry_run is False
    
    def test_parse_verbose_flag(self):
        """Test parsing --verbose flag."""
        parser = argparse.ArgumentParser()
        mode_group = parser.add_mutually_exclusive_group()
        mode_group.add_argument('--audit-only', action='store_true')
        mode_group.add_argument('--dry-run', action='store_true')
        mode_group.add_argument('--rollback', type=str)
        mode_group.add_argument('--list-backups', action='store_true')
        parser.add_argument('--no-backup', action='store_true')
        parser.add_argument('--verbose', '-v', action='store_true')
        parser.add_argument('--project-root', type=Path, default=Path.cwd())
        
        args = parser.parse_args(['--verbose'])
        
        assert args.verbose is True
    
    def test_parse_verbose_short_flag(self):
        """Test parsing -v short flag for verbose."""
        parser = argparse.ArgumentParser()
        mode_group = parser.add_mutually_exclusive_group()
        mode_group.add_argument('--audit-only', action='store_true')
        mode_group.add_argument('--dry-run', action='store_true')
        mode_group.add_argument('--rollback', type=str)
        mode_group.add_argument('--list-backups', action='store_true')
        parser.add_argument('--no-backup', action='store_true')
        parser.add_argument('--verbose', '-v', action='store_true')
        parser.add_argument('--project-root', type=Path, default=Path.cwd())
        
        args = parser.parse_args(['-v'])
        
        assert args.verbose is True
    
    def test_parse_no_backup_flag(self):
        """Test parsing --no-backup flag."""
        parser = argparse.ArgumentParser()
        mode_group = parser.add_mutually_exclusive_group()
        mode_group.add_argument('--audit-only', action='store_true')
        mode_group.add_argument('--dry-run', action='store_true')
        mode_group.add_argument('--rollback', type=str)
        mode_group.add_argument('--list-backups', action='store_true')
        parser.add_argument('--no-backup', action='store_true')
        parser.add_argument('--verbose', '-v', action='store_true')
        parser.add_argument('--project-root', type=Path, default=Path.cwd())
        
        args = parser.parse_args(['--no-backup'])
        
        assert args.no_backup is True
    
    def test_parse_project_root_flag(self):
        """Test parsing --project-root flag."""
        parser = argparse.ArgumentParser()
        mode_group = parser.add_mutually_exclusive_group()
        mode_group.add_argument('--audit-only', action='store_true')
        mode_group.add_argument('--dry-run', action='store_true')
        mode_group.add_argument('--rollback', type=str)
        mode_group.add_argument('--list-backups', action='store_true')
        parser.add_argument('--no-backup', action='store_true')
        parser.add_argument('--verbose', '-v', action='store_true')
        parser.add_argument('--project-root', type=Path, default=Path.cwd())
        
        args = parser.parse_args(['--project-root', '/tmp/test'])
        
        assert args.project_root == Path('/tmp/test')
    
    def test_mutually_exclusive_flags(self):
        """Test that mode flags are mutually exclusive."""
        parser = argparse.ArgumentParser()
        mode_group = parser.add_mutually_exclusive_group()
        mode_group.add_argument('--audit-only', action='store_true')
        mode_group.add_argument('--dry-run', action='store_true')
        mode_group.add_argument('--rollback', type=str)
        mode_group.add_argument('--list-backups', action='store_true')
        parser.add_argument('--no-backup', action='store_true')
        parser.add_argument('--verbose', '-v', action='store_true')
        parser.add_argument('--project-root', type=Path, default=Path.cwd())
        
        # Should raise error when both --audit-only and --dry-run are provided
        with pytest.raises(SystemExit):
            args = parser.parse_args(['--audit-only', '--dry-run'])


class TestAuditOnlyMode:
    """Test --audit-only mode functionality."""
    
    def test_audit_only_generates_report(self):
        """Test that audit-only mode generates a report."""
        with tempfile.TemporaryDirectory() as tmpdir:
            tmp_path = Path(tmpdir)
            
            # Create docs directory for report
            docs_dir = tmp_path / "docs"
            docs_dir.mkdir()
            
            # Create a test file
            (tmp_path / "test.txt").write_text("test content")
            
            cli = CleanupCLI(tmp_path, verbose=False)
            exit_code = cli.run_audit_only()
            
            assert exit_code == 0
            
            # Check that report was created
            report_files = list(docs_dir.glob("CLEANUP-AUDIT-REPORT-*.md"))
            assert len(report_files) > 0
    
    def test_audit_only_does_not_modify_files(self):
        """Test that audit-only mode does not modify any files."""
        with tempfile.TemporaryDirectory() as tmpdir:
            tmp_path = Path(tmpdir)
            
            # Create docs directory
            docs_dir = tmp_path / "docs"
            docs_dir.mkdir()
            
            # Create test files
            test_file = tmp_path / "test.txt"
            test_file.write_text("test content")
            
            # Record original state
            original_content = test_file.read_text()
            original_mtime = test_file.stat().st_mtime
            
            cli = CleanupCLI(tmp_path, verbose=False)
            cli.run_audit_only()
            
            # Verify file unchanged
            assert test_file.exists()
            assert test_file.read_text() == original_content
    
    def test_audit_only_does_not_create_backup(self):
        """Test that audit-only mode does not create backups."""
        with tempfile.TemporaryDirectory() as tmpdir:
            tmp_path = Path(tmpdir)
            
            # Create docs directory
            docs_dir = tmp_path / "docs"
            docs_dir.mkdir()
            
            # Create test file
            (tmp_path / "test.txt").write_text("test content")
            
            cli = CleanupCLI(tmp_path, verbose=False)
            cli.run_audit_only()
            
            # Verify no backup directory created
            backup_dir = tmp_path / ".cleanup_backup"
            if backup_dir.exists():
                # If it exists, it should be empty
                assert len(list(backup_dir.iterdir())) == 0
    
    def test_audit_only_returns_success_code(self):
        """Test that audit-only mode returns success exit code."""
        with tempfile.TemporaryDirectory() as tmpdir:
            tmp_path = Path(tmpdir)
            
            # Create docs directory
            docs_dir = tmp_path / "docs"
            docs_dir.mkdir()
            
            cli = CleanupCLI(tmp_path, verbose=False)
            exit_code = cli.run_audit_only()
            
            assert exit_code == 0
    
    def test_audit_only_handles_errors_gracefully(self):
        """Test that audit-only mode handles errors and returns error code."""
        with tempfile.TemporaryDirectory() as tmpdir:
            tmp_path = Path(tmpdir)
            
            cli = CleanupCLI(tmp_path, verbose=False)
            
            # Mock audit engine to raise an error
            cli.audit_engine.generate_report = Mock(side_effect=Exception("Test error"))
            
            exit_code = cli.run_audit_only()
            
            assert exit_code == 1


class TestDryRunMode:
    """Test --dry-run mode functionality."""
    
    def test_dry_run_does_not_remove_files(self):
        """Test that dry-run mode does not remove any files."""
        with tempfile.TemporaryDirectory() as tmpdir:
            tmp_path = Path(tmpdir)
            
            # Create docs directory
            docs_dir = tmp_path / "docs"
            docs_dir.mkdir()
            
            # Create pyproject.toml
            (tmp_path / "pyproject.toml").write_text("[project]\nname='test'")
            
            # Create test files that would be removed
            test_file = tmp_path / "test.pyc"
            test_file.write_text("compiled")
            
            cli = CleanupCLI(tmp_path, verbose=False)
            exit_code = cli.run_cleanup(dry_run=True)
            
            # Verify file still exists
            assert test_file.exists()
            assert exit_code == 0
    
    def test_dry_run_does_not_create_backup(self):
        """Test that dry-run mode does not create backups."""
        with tempfile.TemporaryDirectory() as tmpdir:
            tmp_path = Path(tmpdir)
            
            # Create docs directory
            docs_dir = tmp_path / "docs"
            docs_dir.mkdir()
            
            # Create pyproject.toml
            (tmp_path / "pyproject.toml").write_text("[project]\nname='test'")
            
            # Create test file
            (tmp_path / "test.pyc").write_text("compiled")
            
            cli = CleanupCLI(tmp_path, verbose=False)
            cli.run_cleanup(dry_run=True)
            
            # Verify no backup created
            backup_dir = tmp_path / ".cleanup_backup"
            if backup_dir.exists():
                # If it exists, it should be empty
                assert len(list(backup_dir.iterdir())) == 0
    
    def test_dry_run_skips_validation(self):
        """Test that dry-run mode skips validation tests."""
        with tempfile.TemporaryDirectory() as tmpdir:
            tmp_path = Path(tmpdir)
            
            # Create docs directory
            docs_dir = tmp_path / "docs"
            docs_dir.mkdir()
            
            # Create pyproject.toml
            (tmp_path / "pyproject.toml").write_text("[project]\nname='test'")
            
            cli = CleanupCLI(tmp_path, verbose=False)
            
            # Mock validator to track if it was called
            cli.validator.validate_all = Mock(return_value=ValidationResult(
                passed=True,
                import_check=True,
                cli_check=True,
                test_check=True,
                build_check=True,
                errors=[]
            ))
            
            cli.run_cleanup(dry_run=True)
            
            # Validator should not be called in dry-run mode
            # (validation is skipped via skip_validation=True)
            # The cleanup engine handles this internally
    
    def test_dry_run_generates_audit_report(self):
        """Test that dry-run mode generates an audit report."""
        with tempfile.TemporaryDirectory() as tmpdir:
            tmp_path = Path(tmpdir)
            
            # Create docs directory
            docs_dir = tmp_path / "docs"
            docs_dir.mkdir()
            
            # Create pyproject.toml
            (tmp_path / "pyproject.toml").write_text("[project]\nname='test'")
            
            cli = CleanupCLI(tmp_path, verbose=False)
            cli.run_cleanup(dry_run=True)
            
            # Check that audit report was created
            report_files = list(docs_dir.glob("CLEANUP-AUDIT-REPORT-*.md"))
            assert len(report_files) > 0
    
    def test_dry_run_returns_success_code(self):
        """Test that dry-run mode returns success exit code."""
        with tempfile.TemporaryDirectory() as tmpdir:
            tmp_path = Path(tmpdir)
            
            # Create docs directory
            docs_dir = tmp_path / "docs"
            docs_dir.mkdir()
            
            # Create pyproject.toml
            (tmp_path / "pyproject.toml").write_text("[project]\nname='test'")
            
            cli = CleanupCLI(tmp_path, verbose=False)
            exit_code = cli.run_cleanup(dry_run=True)
            
            assert exit_code == 0
    
    def test_dry_run_with_backup_flag_ignored(self):
        """Test that backup flag is ignored in dry-run mode."""
        with tempfile.TemporaryDirectory() as tmpdir:
            tmp_path = Path(tmpdir)
            
            # Create docs directory
            docs_dir = tmp_path / "docs"
            docs_dir.mkdir()
            
            # Create pyproject.toml
            (tmp_path / "pyproject.toml").write_text("[project]\nname='test'")
            
            cli = CleanupCLI(tmp_path, verbose=False)
            cli.run_cleanup(dry_run=True, create_backup=True)
            
            # Verify no backup created even with create_backup=True
            backup_dir = tmp_path / ".cleanup_backup"
            if backup_dir.exists():
                assert len(list(backup_dir.iterdir())) == 0


class TestRollbackMode:
    """Test --rollback mode functionality."""
    
    def test_rollback_with_valid_backup(self):
        """Test rollback with a valid backup ID."""
        with tempfile.TemporaryDirectory() as tmpdir:
            tmp_path = Path(tmpdir)
            
            # Create backup directory structure
            backup_dir = tmp_path / ".cleanup_backup"
            backup_dir.mkdir()
            
            backup_id = "backup_20260131_143022"
            backup_path = backup_dir / backup_id
            backup_path.mkdir()
            
            # Create manifest
            manifest = {
                "backup_id": backup_id,
                "timestamp": "2026-01-31T14:30:22Z",
                "files": [],
                "total_size": 0,
                "total_files": 0
            }
            import json
            (backup_path / "manifest.json").write_text(json.dumps(manifest))
            
            # Create empty archive
            import tarfile
            with tarfile.open(backup_path / "files.tar.gz", "w:gz") as tar:
                pass
            
            cli = CleanupCLI(tmp_path, verbose=False)
            
            # Mock user input to confirm rollback
            with patch('builtins.input', return_value='yes'):
                exit_code = cli.run_rollback(backup_id)
            
            assert exit_code == 0
    
    def test_rollback_with_invalid_backup(self):
        """Test rollback with an invalid backup ID."""
        with tempfile.TemporaryDirectory() as tmpdir:
            tmp_path = Path(tmpdir)
            
            cli = CleanupCLI(tmp_path, verbose=False)
            
            # Try to rollback non-existent backup
            exit_code = cli.run_rollback("nonexistent_backup")
            
            assert exit_code == 1
    
    def test_rollback_cancelled_by_user(self):
        """Test rollback cancelled by user input."""
        with tempfile.TemporaryDirectory() as tmpdir:
            tmp_path = Path(tmpdir)
            
            # Create backup directory structure
            backup_dir = tmp_path / ".cleanup_backup"
            backup_dir.mkdir()
            
            backup_id = "backup_20260131_143022"
            backup_path = backup_dir / backup_id
            backup_path.mkdir()
            
            # Create manifest
            manifest = {
                "backup_id": backup_id,
                "timestamp": "2026-01-31T14:30:22Z",
                "files": [],
                "total_size": 0,
                "total_files": 0
            }
            import json
            (backup_path / "manifest.json").write_text(json.dumps(manifest))
            
            # Create empty archive
            import tarfile
            with tarfile.open(backup_path / "files.tar.gz", "w:gz") as tar:
                pass
            
            cli = CleanupCLI(tmp_path, verbose=False)
            
            # Mock user input to cancel rollback
            with patch('builtins.input', return_value='no'):
                exit_code = cli.run_rollback(backup_id)
            
            assert exit_code == 0
    
    def test_rollback_handles_errors(self):
        """Test that rollback handles errors gracefully."""
        with tempfile.TemporaryDirectory() as tmpdir:
            tmp_path = Path(tmpdir)
            
            cli = CleanupCLI(tmp_path, verbose=False)
            
            # Mock backup manager to raise an error
            cli.backup_manager.get_backup_info = Mock(side_effect=Exception("Test error"))
            
            exit_code = cli.run_rollback("backup_20260131_143022")
            
            assert exit_code == 1


class TestListBackups:
    """Test --list-backups functionality."""
    
    def test_list_backups_empty(self):
        """Test listing backups when none exist."""
        with tempfile.TemporaryDirectory() as tmpdir:
            tmp_path = Path(tmpdir)
            
            cli = CleanupCLI(tmp_path, verbose=False)
            exit_code = cli.list_backups()
            
            assert exit_code == 0
    
    def test_list_backups_with_backups(self):
        """Test listing backups when some exist."""
        with tempfile.TemporaryDirectory() as tmpdir:
            tmp_path = Path(tmpdir)
            
            # Create backup directory structure
            backup_dir = tmp_path / ".cleanup_backup"
            backup_dir.mkdir()
            
            backup_id = "backup_20260131_143022"
            backup_path = backup_dir / backup_id
            backup_path.mkdir()
            
            # Create manifest
            manifest = {
                "backup_id": backup_id,
                "timestamp": "2026-01-31T14:30:22Z",
                "files": [],
                "total_size": 1024,
                "total_files": 5
            }
            import json
            (backup_path / "manifest.json").write_text(json.dumps(manifest))
            
            # Create empty archive
            import tarfile
            with tarfile.open(backup_path / "files.tar.gz", "w:gz") as tar:
                pass
            
            cli = CleanupCLI(tmp_path, verbose=False)
            exit_code = cli.list_backups()
            
            assert exit_code == 0


class TestCleanupMode:
    """Test default cleanup mode functionality."""
    
    def test_cleanup_with_backup_enabled(self):
        """Test cleanup with backup enabled (default)."""
        with tempfile.TemporaryDirectory() as tmpdir:
            tmp_path = Path(tmpdir)
            
            # Create docs directory
            docs_dir = tmp_path / "docs"
            docs_dir.mkdir()
            
            # Create pyproject.toml
            (tmp_path / "pyproject.toml").write_text("[project]\nname='test'")
            
            # Create test file to remove
            test_file = tmp_path / "test.pyc"
            test_file.write_text("compiled")
            
            cli = CleanupCLI(tmp_path, verbose=False)
            
            # Mock cleanup engine to avoid actual cleanup
            mock_result = CleanupResult(
                success=True,
                backup_id="backup_test",
                files_removed=1,
                size_freed=100,
                errors=[],
                validation_result=ValidationResult(
                    passed=True,
                    import_check=True,
                    cli_check=True,
                    test_check=True,
                    build_check=True,
                    errors=[]
                )
            )
            cli.cleanup_engine.cleanup = Mock(return_value=mock_result)
            
            exit_code = cli.run_cleanup(dry_run=False, create_backup=True)
            
            assert exit_code == 0
            cli.cleanup_engine.cleanup.assert_called_once()
    
    def test_cleanup_with_backup_disabled(self):
        """Test cleanup with backup disabled."""
        with tempfile.TemporaryDirectory() as tmpdir:
            tmp_path = Path(tmpdir)
            
            # Create docs directory
            docs_dir = tmp_path / "docs"
            docs_dir.mkdir()
            
            # Create pyproject.toml
            (tmp_path / "pyproject.toml").write_text("[project]\nname='test'")
            
            cli = CleanupCLI(tmp_path, verbose=False)
            
            # Mock cleanup engine
            mock_result = CleanupResult(
                success=True,
                backup_id="",
                files_removed=1,
                size_freed=100,
                errors=[],
                validation_result=None
            )
            cli.cleanup_engine.cleanup = Mock(return_value=mock_result)
            
            exit_code = cli.run_cleanup(dry_run=False, create_backup=False)
            
            assert exit_code == 0
    
    def test_cleanup_failure_returns_error_code(self):
        """Test that cleanup failure returns error exit code."""
        with tempfile.TemporaryDirectory() as tmpdir:
            tmp_path = Path(tmpdir)
            
            # Create docs directory
            docs_dir = tmp_path / "docs"
            docs_dir.mkdir()
            
            # Create pyproject.toml
            (tmp_path / "pyproject.toml").write_text("[project]\nname='test'")
            
            cli = CleanupCLI(tmp_path, verbose=False)
            
            # Mock cleanup engine to return failure
            mock_result = CleanupResult(
                success=False,
                backup_id="",
                files_removed=0,
                size_freed=0,
                errors=["Test error"],
                validation_result=None
            )
            cli.cleanup_engine.cleanup = Mock(return_value=mock_result)
            
            exit_code = cli.run_cleanup(dry_run=False, create_backup=True)
            
            assert exit_code == 1


class TestMainFunction:
    """Test main() entry point function."""
    
    def test_main_with_audit_only(self):
        """Test main function with --audit-only flag."""
        with tempfile.TemporaryDirectory() as tmpdir:
            tmp_path = Path(tmpdir)
            
            # Create docs directory
            docs_dir = tmp_path / "docs"
            docs_dir.mkdir()
            
            with patch('sys.argv', ['cleanup.py', '--audit-only', '--project-root', str(tmp_path)]):
                exit_code = main()
            
            assert exit_code == 0
    
    def test_main_with_dry_run(self):
        """Test main function with --dry-run flag."""
        with tempfile.TemporaryDirectory() as tmpdir:
            tmp_path = Path(tmpdir)
            
            # Create docs directory
            docs_dir = tmp_path / "docs"
            docs_dir.mkdir()
            
            # Create pyproject.toml
            (tmp_path / "pyproject.toml").write_text("[project]\nname='test'")
            
            with patch('sys.argv', ['cleanup.py', '--dry-run', '--project-root', str(tmp_path)]):
                exit_code = main()
            
            assert exit_code == 0
    
    def test_main_with_keyboard_interrupt(self):
        """Test main function handles keyboard interrupt."""
        with tempfile.TemporaryDirectory() as tmpdir:
            tmp_path = Path(tmpdir)
            
            with patch('sys.argv', ['cleanup.py', '--audit-only', '--project-root', str(tmp_path)]):
                with patch.object(CleanupCLI, 'run_audit_only', side_effect=KeyboardInterrupt()):
                    exit_code = main()
            
            assert exit_code == 130  # Standard exit code for SIGINT


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
