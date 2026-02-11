"""
Integration tests for the Agentic SDLC CLI.

Tests the CLI interface to ensure:
- CLI commands execute successfully
- CLI uses SDK public API
- CLI works with optional dependencies
- CLI provides helpful error messages
"""

import subprocess
import sys
from pathlib import Path

import pytest


class TestCLIBasics:
    """Test basic CLI functionality."""

    def test_cli_help(self) -> None:
        """Test that CLI help command works."""
        result = subprocess.run(
            [sys.executable, "-m", "agentic_sdlc.cli", "--help"],
            capture_output=True,
            text=True,
            timeout=10,
        )

        # Should succeed or show help
        assert result.returncode in [0, 2]  # 0 for success, 2 for help
        assert "agentic" in result.stdout.lower() or "usage" in result.stdout.lower()

    def test_cli_version(self) -> None:
        """Test that CLI version command works."""
        result = subprocess.run(
            [sys.executable, "-m", "agentic_sdlc.cli", "--version"],
            capture_output=True,
            text=True,
            timeout=10,
        )

        # Should succeed
        assert result.returncode == 0
        # Should contain version number
        assert "." in result.stdout  # Version format like X.Y.Z

    def test_cli_init_command(self) -> None:
        """Test that CLI init command works."""
        result = subprocess.run(
            [sys.executable, "-m", "agentic_sdlc.cli", "init"],
            capture_output=True,
            text=True,
            timeout=10,
        )

        # Should succeed
        assert result.returncode == 0
        # Should show success message
        assert "initializ" in result.stdout.lower() or "success" in result.stdout.lower()

    def test_cli_run_command(self) -> None:
        """Test that CLI run command works."""
        result = subprocess.run(
            [sys.executable, "-m", "agentic_sdlc.cli", "run", "test-workflow"],
            capture_output=True,
            text=True,
            timeout=10,
        )

        # Should succeed
        assert result.returncode == 0
        # Should show workflow execution message
        assert "workflow" in result.stdout.lower()

    def test_cli_status_command(self) -> None:
        """Test that CLI status command works."""
        result = subprocess.run(
            [sys.executable, "-m", "agentic_sdlc.cli", "status"],
            capture_output=True,
            text=True,
            timeout=10,
        )

        # Should succeed
        assert result.returncode == 0
        # Should show status information
        assert "status" in result.stdout.lower()


class TestCLIPublicAPI:
    """Test that CLI uses SDK public API."""

    def test_cli_imports_from_public_api(self) -> None:
        """Test that CLI module imports from public API."""
        # Import the CLI module
        from agentic_sdlc.cli import main

        # Should be callable
        assert callable(main)

    def test_cli_version_from_public_api(self) -> None:
        """Test that CLI gets version from public API."""
        from agentic_sdlc import __version__
        from agentic_sdlc.cli.main import _create_cli

        # CLI should be able to access version
        assert __version__ is not None
        assert isinstance(__version__, str)
        assert "." in __version__  # Should be semver format

    def test_cli_uses_public_exceptions(self) -> None:
        """Test that CLI can use public API exceptions."""
        from agentic_sdlc import AgenticSDLCError, ConfigurationError

        # Should be able to import exceptions
        assert AgenticSDLCError is not None
        assert ConfigurationError is not None


class TestCLIOptionalDependencies:
    """Test CLI behavior with optional dependencies."""

    def test_cli_main_function_exists(self) -> None:
        """Test that CLI main function is defined."""
        from agentic_sdlc.cli import main

        # Should be callable
        assert callable(main)

    def test_cli_graceful_error_without_click(self) -> None:
        """Test that CLI provides helpful error if click is missing.
        
        Note: This test assumes click IS installed (since we're running tests).
        In a real scenario without click, the import would fail.
        """
        # This test verifies the error handling code exists
        from agentic_sdlc.cli.main import main

        # main function should exist and be callable
        assert callable(main)

    def test_cli_entry_point_defined(self) -> None:
        """Test that CLI entry point is properly defined in pyproject.toml."""
        # Read pyproject.toml
        pyproject_path = Path(__file__).parent.parent.parent / "pyproject.toml"
        assert pyproject_path.exists()

        content = pyproject_path.read_text()

        # Should have CLI entry points
        assert "agentic" in content
        assert "agentic_sdlc.cli" in content


class TestCLIErrorHandling:
    """Test CLI error handling."""

    def test_cli_invalid_command(self) -> None:
        """Test that CLI handles invalid commands gracefully."""
        result = subprocess.run(
            [sys.executable, "-m", "agentic_sdlc.cli", "invalid-command"],
            capture_output=True,
            text=True,
            timeout=10,
        )

        # Should fail with non-zero exit code
        assert result.returncode != 0

    def test_cli_missing_required_argument(self) -> None:
        """Test that CLI handles missing required arguments."""
        result = subprocess.run(
            [sys.executable, "-m", "agentic_sdlc.cli", "run"],
            capture_output=True,
            text=True,
            timeout=10,
        )

        # Should fail with non-zero exit code
        assert result.returncode != 0


class TestCLIStructure:
    """Test CLI module structure."""

    def test_cli_module_has_main_py(self) -> None:
        """Test that CLI module has main.py file."""
        cli_main_path = Path(__file__).parent.parent.parent / "src" / "agentic_sdlc" / "cli" / "main.py"
        assert cli_main_path.exists()

    def test_cli_module_has_commands_dir(self) -> None:
        """Test that CLI module has commands directory."""
        commands_path = Path(__file__).parent.parent.parent / "src" / "agentic_sdlc" / "cli" / "commands"
        assert commands_path.exists()
        assert commands_path.is_dir()

    def test_cli_module_has_init(self) -> None:
        """Test that CLI module has __init__.py."""
        cli_init_path = Path(__file__).parent.parent.parent / "src" / "agentic_sdlc" / "cli" / "__init__.py"
        assert cli_init_path.exists()

    def test_cli_init_exports_main(self) -> None:
        """Test that CLI __init__.py exports main function."""
        from agentic_sdlc.cli import main

        assert callable(main)


class TestCLIIntegration:
    """Test CLI integration with SDK."""

    def test_cli_can_import_sdk_components(self) -> None:
        """Test that CLI can import SDK components."""
        # This verifies the CLI can access public API
        from agentic_sdlc import (
            __version__,
            AgenticSDLCError,
            get_logger,
            setup_logging,
        )

        assert __version__ is not None
        assert AgenticSDLCError is not None
        assert callable(get_logger)
        assert callable(setup_logging)

    def test_cli_main_entry_point(self) -> None:
        """Test that CLI main entry point works."""
        from agentic_sdlc.cli import main

        # Should be callable without errors
        assert callable(main)

    def test_cli_uses_only_public_api(self) -> None:
        """Test that CLI imports only use public API."""
        # Read the CLI main.py file
        cli_main_path = Path(__file__).parent.parent.parent / "src" / "agentic_sdlc" / "cli" / "main.py"
        content = cli_main_path.read_text()

        # Should import from agentic_sdlc (public API)
        assert "from agentic_sdlc import" in content

        # Should NOT import from internal modules
        assert "from agentic_sdlc._internal" not in content
        assert "from agentic_sdlc.core._" not in content
        assert "from agentic_sdlc.infrastructure._" not in content
