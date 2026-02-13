"""
Unit tests for Validator.

These tests verify specific examples and edge cases for validation operations,
complementing the property-based tests.

Feature: project-audit-cleanup
Requirements: 9.1, 9.2, 9.3, 9.4
"""

import pytest
import tempfile
import subprocess
from pathlib import Path
from unittest.mock import patch, MagicMock, call
import shutil

from scripts.cleanup.validator import Validator
from scripts.cleanup.models import (
    ValidationResult,
    CleanupTestResult,
    ImportResult,
    CLIResult,
    BuildResult,
)


class TestImportValidation:
    """Tests for import validation functionality."""
    
    def test_import_validation_with_successful_imports(self):
        """Test import validation when all imports succeed."""
        with tempfile.TemporaryDirectory() as tmpdir:
            tmpdir = Path(tmpdir)
            validator = Validator(tmpdir)
            
            # Mock successful subprocess calls
            mock_result = MagicMock()
            mock_result.returncode = 0
            mock_result.stdout = ""
            mock_result.stderr = ""
            
            with patch('subprocess.run', return_value=mock_result):
                result = validator.verify_imports(["test_module"])
                
                assert result.passed
                assert "test_module" in result.successful_imports
                assert len(result.failed_imports) == 0
                assert len(result.errors) == 0
    
    def test_import_validation_with_failed_imports(self):
        """Test import validation when imports fail."""
        with tempfile.TemporaryDirectory() as tmpdir:
            tmpdir = Path(tmpdir)
            validator = Validator(tmpdir)
            
            # Mock failed subprocess call
            mock_result = MagicMock()
            mock_result.returncode = 1
            mock_result.stdout = ""
            mock_result.stderr = "ModuleNotFoundError: No module named 'nonexistent_module'"
            
            with patch('subprocess.run', return_value=mock_result):
                result = validator.verify_imports(["nonexistent_module"])
                
                assert not result.passed
                assert len(result.successful_imports) == 0
                assert "nonexistent_module" in result.failed_imports
                assert len(result.errors) > 0
                assert "nonexistent_module" in result.errors[0]
    
    def test_import_validation_with_mixed_results(self):
        """Test import validation with both successful and failed imports."""
        with tempfile.TemporaryDirectory() as tmpdir:
            tmpdir = Path(tmpdir)
            validator = Validator(tmpdir)
            
            # Mock subprocess to return different results for different modules
            def mock_subprocess_run(cmd, *args, **kwargs):
                result = MagicMock()
                result.stdout = ""
                result.stderr = ""
                
                if "good_module" in cmd[2]:
                    result.returncode = 0
                else:
                    result.returncode = 1
                    result.stderr = "ModuleNotFoundError"
                
                return result
            
            with patch('subprocess.run', side_effect=mock_subprocess_run):
                result = validator.verify_imports(["good_module", "bad_module"])
                
                assert not result.passed  # Overall should fail if any import fails
                assert "good_module" in result.successful_imports
                assert "bad_module" in result.failed_imports
                assert len(result.errors) > 0
    
    def test_import_validation_with_timeout(self):
        """Test import validation when subprocess times out."""
        with tempfile.TemporaryDirectory() as tmpdir:
            tmpdir = Path(tmpdir)
            validator = Validator(tmpdir)
            
            # Mock subprocess timeout
            with patch('subprocess.run', side_effect=subprocess.TimeoutExpired("cmd", 30)):
                result = validator.verify_imports(["slow_module"])
                
                assert not result.passed
                assert "slow_module" in result.failed_imports
                assert any("timeout" in error.lower() for error in result.errors)
    
    def test_import_validation_uses_default_modules(self):
        """Test that import validation uses default critical modules when none specified."""
        with tempfile.TemporaryDirectory() as tmpdir:
            tmpdir = Path(tmpdir)
            validator = Validator(tmpdir)
            
            mock_result = MagicMock()
            mock_result.returncode = 0
            mock_result.stdout = ""
            mock_result.stderr = ""
            
            with patch('subprocess.run', return_value=mock_result) as mock_run:
                result = validator.verify_imports()
                
                # Should test default critical modules
                assert mock_run.call_count >= 5  # At least 5 default modules
                
                # Check that critical modules were tested
                calls = [str(call) for call in mock_run.call_args_list]
                assert any("agentic_sdlc" in str(call) for call in calls)


class TestCLIValidation:
    """Tests for CLI entry point validation functionality."""
    
    def test_cli_validation_with_successful_commands(self):
        """Test CLI validation when all commands succeed."""
        with tempfile.TemporaryDirectory() as tmpdir:
            tmpdir = Path(tmpdir)
            validator = Validator(tmpdir)
            
            mock_result = MagicMock()
            mock_result.returncode = 0
            mock_result.stdout = "Usage: test_command [OPTIONS]"
            mock_result.stderr = ""
            
            with patch('subprocess.run', return_value=mock_result):
                with patch('shutil.which', return_value="/usr/bin/test_command"):
                    result = validator.verify_cli_entry_points(["test_command"])
                    
                    assert result.passed
                    assert "test_command" in result.successful_commands
                    assert len(result.failed_commands) == 0
                    assert len(result.errors) == 0
    
    def test_cli_validation_with_failed_commands(self):
        """Test CLI validation when commands fail."""
        with tempfile.TemporaryDirectory() as tmpdir:
            tmpdir = Path(tmpdir)
            validator = Validator(tmpdir)
            
            mock_result = MagicMock()
            mock_result.returncode = 1
            mock_result.stdout = ""
            mock_result.stderr = "Command not found"
            
            with patch('subprocess.run', return_value=mock_result):
                with patch('shutil.which', return_value=None):
                    result = validator.verify_cli_entry_points(["nonexistent_command"])
                    
                    assert not result.passed
                    assert len(result.successful_commands) == 0
                    assert "nonexistent_command" in result.failed_commands
                    assert len(result.errors) > 0
    
    def test_cli_validation_uses_default_commands(self):
        """Test that CLI validation uses default commands when none specified."""
        with tempfile.TemporaryDirectory() as tmpdir:
            tmpdir = Path(tmpdir)
            validator = Validator(tmpdir)
            
            mock_result = MagicMock()
            mock_result.returncode = 0
            mock_result.stdout = "Usage: command [OPTIONS]"
            mock_result.stderr = ""
            
            with patch('subprocess.run', return_value=mock_result) as mock_run:
                with patch('shutil.which', return_value=None):
                    result = validator.verify_cli_entry_points()
                    
                    # Should test default CLI commands
                    assert mock_run.call_count >= 3  # At least 3 default commands
                    
                    # Check that default commands were tested
                    calls = [str(call) for call in mock_run.call_args_list]
                    assert any("agentic" in str(call) or "asdlc" in str(call) for call in calls)


class TestTestSuiteExecution:
    """Tests for test suite execution functionality."""
    
    def test_run_tests_with_passing_suite(self):
        """Test running test suite when all tests pass."""
        with tempfile.TemporaryDirectory() as tmpdir:
            tmpdir = Path(tmpdir)
            validator = Validator(tmpdir)
            
            mock_result = MagicMock()
            mock_result.returncode = 0
            mock_result.stdout = "5 passed in 1.23s"
            mock_result.stderr = ""
            
            with patch('subprocess.run', return_value=mock_result):
                result = validator.run_tests()
                
                assert result.passed
                assert result.tests_run >= 0
                assert result.tests_failed == 0
    
    def test_run_tests_with_failing_suite(self):
        """Test running test suite when tests fail."""
        with tempfile.TemporaryDirectory() as tmpdir:
            tmpdir = Path(tmpdir)
            validator = Validator(tmpdir)
            
            mock_result = MagicMock()
            mock_result.returncode = 1
            mock_result.stdout = "3 failed, 2 passed in 1.23s"
            mock_result.stderr = ""
            
            with patch('subprocess.run', return_value=mock_result):
                result = validator.run_tests()
                
                assert not result.passed
                assert result.tests_failed > 0
    
    def test_run_tests_with_timeout(self):
        """Test running test suite when execution times out."""
        with tempfile.TemporaryDirectory() as tmpdir:
            tmpdir = Path(tmpdir)
            validator = Validator(tmpdir)
            
            with patch('subprocess.run', side_effect=subprocess.TimeoutExpired("pytest", 300)):
                result = validator.run_tests()
                
                assert not result.passed
                assert "timed out" in result.output.lower()


class TestPackageBuild:
    """Tests for package build validation functionality."""
    
    def test_verify_package_build_success(self):
        """Test package build validation when build succeeds."""
        with tempfile.TemporaryDirectory() as tmpdir:
            tmpdir = Path(tmpdir)
            validator = Validator(tmpdir)
            
            # Mock subprocess to create dist directory and wheel file
            def mock_subprocess_run(cmd, *args, **kwargs):
                result = MagicMock()
                result.returncode = 0
                result.stdout = "Successfully built test-1.0.0-py3-none-any.whl"
                result.stderr = ""
                
                # Create dist directory and wheel file after build
                dist_dir = tmpdir / "dist"
                dist_dir.mkdir(exist_ok=True)
                wheel_file = dist_dir / "test-1.0.0-py3-none-any.whl"
                wheel_file.write_bytes(b"0" * 1024)  # 1KB file
                
                return result
            
            with patch('subprocess.run', side_effect=mock_subprocess_run):
                result = validator.verify_package_build()
                
                assert result.passed
                assert result.package_size == 1024
                assert len(result.errors) == 0
    
    def test_verify_package_build_failure(self):
        """Test package build validation when build fails."""
        with tempfile.TemporaryDirectory() as tmpdir:
            tmpdir = Path(tmpdir)
            validator = Validator(tmpdir)
            
            mock_result = MagicMock()
            mock_result.returncode = 1
            mock_result.stdout = ""
            mock_result.stderr = "Build failed: missing setup.py"
            
            with patch('subprocess.run', return_value=mock_result):
                result = validator.verify_package_build()
                
                assert not result.passed
                assert len(result.errors) > 0
                assert "Build command failed" in result.errors[0]
    
    def test_verify_package_build_no_wheel_file(self):
        """Test package build validation when no wheel file is produced."""
        with tempfile.TemporaryDirectory() as tmpdir:
            tmpdir = Path(tmpdir)
            validator = Validator(tmpdir)
            
            # Mock subprocess to create dist directory but no wheel file
            def mock_subprocess_run(cmd, *args, **kwargs):
                result = MagicMock()
                result.returncode = 0
                result.stdout = "Build completed"
                result.stderr = ""
                
                # Create empty dist directory
                dist_dir = tmpdir / "dist"
                dist_dir.mkdir(exist_ok=True)
                
                return result
            
            with patch('subprocess.run', side_effect=mock_subprocess_run):
                result = validator.verify_package_build()
                
                assert not result.passed
                assert any("no wheel file" in error.lower() for error in result.errors)
    
    def test_verify_package_build_cleans_existing_dist(self):
        """Test that package build cleans existing dist directory."""
        with tempfile.TemporaryDirectory() as tmpdir:
            tmpdir = Path(tmpdir)
            validator = Validator(tmpdir)
            
            # Create existing dist directory with old files
            dist_dir = tmpdir / "dist"
            dist_dir.mkdir()
            old_file = dist_dir / "old-1.0.0-py3-none-any.whl"
            old_file.write_text("old content")
            
            # Mock subprocess to create new wheel file after build
            def mock_subprocess_run(cmd, *args, **kwargs):
                result = MagicMock()
                result.returncode = 0
                result.stdout = "Build completed"
                result.stderr = ""
                
                # Create new wheel file (dist directory will be recreated by validator)
                dist_dir = tmpdir / "dist"
                dist_dir.mkdir(exist_ok=True)
                new_wheel = dist_dir / "new-1.0.0-py3-none-any.whl"
                new_wheel.write_bytes(b"0" * 2048)
                
                return result
            
            with patch('subprocess.run', side_effect=mock_subprocess_run):
                result = validator.verify_package_build()
                
                # Old file should be gone (dist was cleaned)
                assert not old_file.exists()
                assert result.passed


class TestValidateAll:
    """Tests for comprehensive validation functionality."""
    
    def test_validate_all_with_all_checks_passing(self):
        """Test validate_all when all checks pass."""
        with tempfile.TemporaryDirectory() as tmpdir:
            tmpdir = Path(tmpdir)
            validator = Validator(tmpdir, max_package_size=10 * 1024 * 1024)
            
            # Mock all subprocess calls to succeed
            def mock_subprocess_run(cmd, *args, **kwargs):
                result = MagicMock()
                result.returncode = 0
                result.stdout = "Success"
                result.stderr = ""
                
                # Create wheel file for build command
                if "build" in str(cmd):
                    dist_dir = tmpdir / "dist"
                    dist_dir.mkdir(exist_ok=True)
                    wheel_file = dist_dir / "test-1.0.0-py3-none-any.whl"
                    wheel_file.write_bytes(b"0" * (5 * 1024 * 1024))  # 5MB
                
                return result
            
            with patch('subprocess.run', side_effect=mock_subprocess_run):
                with patch('shutil.which', return_value="/usr/bin/command"):
                    result = validator.validate_all()
                    
                    assert result.passed
                    assert result.import_check
                    assert result.cli_check
                    assert result.test_check
                    assert result.build_check
                    assert len(result.errors) == 0
    
    def test_validate_all_with_import_failure(self):
        """Test validate_all when import check fails."""
        with tempfile.TemporaryDirectory() as tmpdir:
            tmpdir = Path(tmpdir)
            validator = Validator(tmpdir)
            
            # Mock import to fail, others to succeed
            def mock_subprocess_run(cmd, *args, **kwargs):
                result = MagicMock()
                result.stderr = ""
                
                if len(cmd) >= 3 and cmd[1] == "-c" and "import" in cmd[2]:
                    result.returncode = 1
                    result.stdout = ""
                    result.stderr = "ModuleNotFoundError"
                else:
                    result.returncode = 0
                    result.stdout = "Success"
                    
                    # Create wheel file for build command
                    if "build" in str(cmd):
                        dist_dir = tmpdir / "dist"
                        dist_dir.mkdir(exist_ok=True)
                        wheel_file = dist_dir / "test-1.0.0-py3-none-any.whl"
                        wheel_file.write_bytes(b"0" * 1024)
                
                return result
            
            with patch('subprocess.run', side_effect=mock_subprocess_run):
                with patch('shutil.which', return_value="/usr/bin/command"):
                    result = validator.validate_all()
                    
                    assert not result.passed
                    assert not result.import_check
                    assert len(result.errors) > 0
    
    def test_validate_all_with_size_limit_exceeded(self):
        """Test validate_all when package size exceeds limit."""
        with tempfile.TemporaryDirectory() as tmpdir:
            tmpdir = Path(tmpdir)
            validator = Validator(tmpdir, max_package_size=1024)  # 1KB limit
            
            # Mock all checks to succeed but create large package
            def mock_subprocess_run(cmd, *args, **kwargs):
                result = MagicMock()
                result.returncode = 0
                result.stdout = "Success"
                result.stderr = ""
                
                # Create large wheel file
                if "build" in str(cmd):
                    dist_dir = tmpdir / "dist"
                    dist_dir.mkdir(exist_ok=True)
                    wheel_file = dist_dir / "test-1.0.0-py3-none-any.whl"
                    wheel_file.write_bytes(b"0" * (2 * 1024))  # 2KB (exceeds 1KB limit)
                
                return result
            
            with patch('subprocess.run', side_effect=mock_subprocess_run):
                with patch('shutil.which', return_value="/usr/bin/command"):
                    result = validator.validate_all()
                    
                    assert not result.passed
                    assert any("size" in error.lower() or "exceeds" in error.lower() 
                              for error in result.errors)
    
    def test_validate_all_with_multiple_failures(self):
        """Test validate_all when multiple checks fail."""
        with tempfile.TemporaryDirectory() as tmpdir:
            tmpdir = Path(tmpdir)
            validator = Validator(tmpdir)
            
            # Mock all checks to fail
            mock_result = MagicMock()
            mock_result.returncode = 1
            mock_result.stdout = ""
            mock_result.stderr = "Error"
            
            with patch('subprocess.run', return_value=mock_result):
                with patch('shutil.which', return_value=None):
                    result = validator.validate_all()
                    
                    assert not result.passed
                    assert not result.import_check
                    assert not result.cli_check
                    assert not result.test_check
                    assert not result.build_check
                    assert len(result.errors) > 0
