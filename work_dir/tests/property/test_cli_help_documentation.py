"""
Property-based test for CLI help documentation.

Feature: sdlc-kit-improvements, Property 7: CLI Help Documentation

Tests that all CLI commands provide comprehensive help documentation
when executed with the --help flag.
"""

import subprocess
import sys
from pathlib import Path
from hypothesis import given, strategies as st, settings
import pytest

# Add project root to path
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))


# Define all CLI commands and subcommands
CLI_COMMANDS = [
    ["--help"],
    ["agent", "--help"],
    ["agent", "list", "--help"],
    ["agent", "show", "--help"],
    ["agent", "create", "--help"],
    ["agent", "delete", "--help"],
    ["workflow", "--help"],
    ["workflow", "list", "--help"],
    ["workflow", "run", "--help"],
    ["workflow", "show", "--help"],
    ["workflow", "validate", "--help"],
    ["validate", "--help"],
    ["validate", "config", "--help"],
    ["validate", "all", "--help"],
    ["validate", "schema", "--help"],
    ["health", "--help"],
    ["health", "all", "--help"],
    ["health", "component", "--help"],
    ["config", "--help"],
    ["config", "show", "--help"],
    ["config", "list", "--help"],
    ["config", "get", "--help"],
    ["config", "set", "--help"],
]


def run_cli_command(args):
    """
    Run a CLI command and return the output.
    
    Args:
        args: List of command arguments
        
    Returns:
        Tuple of (stdout, stderr, returncode)
    """
    cli_path = PROJECT_ROOT / "cli" / "main.py"
    cmd = [sys.executable, str(cli_path)] + args
    
    result = subprocess.run(
        cmd,
        capture_output=True,
        text=True,
        timeout=5
    )
    
    return result.stdout, result.stderr, result.returncode


def test_cli_help_contains_required_elements():
    """
    Test that all CLI commands have help documentation with required elements.
    
    Property: For any CLI command, when executed with the --help flag,
    the output should contain usage information, command description,
    and available options.
    """
    for command_args in CLI_COMMANDS:
        stdout, stderr, returncode = run_cli_command(command_args)
        
        # Help should exit with code 0
        assert returncode == 0, f"Command {' '.join(command_args)} failed with code {returncode}"
        
        # Help output should be in stdout
        output = stdout.lower()
        
        # Check for usage information
        assert "usage:" in output, f"Command {' '.join(command_args)} missing usage information"
        
        # Check for options section (all commands should have at least -h/--help)
        assert "options:" in output or "optional arguments:" in output, \
            f"Command {' '.join(command_args)} missing options section"
        
        # Check for help option
        assert "--help" in output or "-h" in output, \
            f"Command {' '.join(command_args)} missing help option"


@given(st.sampled_from(CLI_COMMANDS))
@settings(max_examples=len(CLI_COMMANDS), deadline=5000)
def test_cli_help_property(command_args):
    """
    Property test: All CLI commands provide comprehensive help documentation.
    
    Property: For any CLI command, when executed with the --help flag,
    the output should contain usage information, command description,
    and available options.
    
    Validates: Requirements 7.4
    """
    stdout, stderr, returncode = run_cli_command(command_args)
    
    # Property 1: Help command should succeed
    assert returncode == 0, \
        f"Help command failed: {' '.join(command_args)}"
    
    # Property 2: Output should not be empty
    assert stdout.strip(), \
        f"Help output is empty for: {' '.join(command_args)}"
    
    output = stdout.lower()
    
    # Property 3: Must contain usage information
    assert "usage:" in output, \
        f"Missing usage information for: {' '.join(command_args)}"
    
    # Property 4: Must contain options/arguments section
    has_options = "options:" in output or "optional arguments:" in output
    has_positional = "positional arguments:" in output
    assert has_options or has_positional, \
        f"Missing options/arguments section for: {' '.join(command_args)}"
    
    # Property 5: Must document the help flag itself
    assert "--help" in output or "-h" in output, \
        f"Help flag not documented for: {' '.join(command_args)}"


def test_main_cli_help_has_examples():
    """
    Test that the main CLI help includes usage examples.
    """
    stdout, stderr, returncode = run_cli_command(["--help"])
    
    assert returncode == 0
    output = stdout.lower()
    
    # Main help should include examples section
    assert "examples:" in output, "Main CLI help missing examples section"


def test_main_cli_help_lists_all_commands():
    """
    Test that the main CLI help lists all available commands.
    """
    stdout, stderr, returncode = run_cli_command(["--help"])
    
    assert returncode == 0
    output = stdout.lower()
    
    # Check that all main commands are listed
    expected_commands = ["agent", "workflow", "validate", "health", "config"]
    for cmd in expected_commands:
        assert cmd in output, f"Command '{cmd}' not listed in main help"


def test_subcommand_help_has_description():
    """
    Test that subcommands have descriptions in their help output.
    """
    # Test a few representative subcommands
    test_commands = [
        ["agent", "list", "--help"],
        ["workflow", "run", "--help"],
        ["validate", "config", "--help"],
        ["health", "all", "--help"],
        ["config", "show", "--help"]
    ]
    
    for command_args in test_commands:
        stdout, stderr, returncode = run_cli_command(command_args)
        
        assert returncode == 0
        # Output should have more than just usage line (indicates description present)
        lines = [line for line in stdout.split('\n') if line.strip()]
        assert len(lines) > 2, \
            f"Command {' '.join(command_args)} appears to lack description"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
