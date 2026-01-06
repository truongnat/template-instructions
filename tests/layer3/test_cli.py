
import pytest
import subprocess
import sys
from pathlib import Path

ROOT_DIR = Path(__file__).parents[2]
CLI_PATH = ROOT_DIR / "bin" / "cli.js"

def test_cli_help():
    if not CLI_PATH.exists():
        pytest.skip("CLI entry point not found at bin/cli.js")
    
    # Run node bin/cli.js --help
    # Requires node/bun to be in path
    try:
        result = subprocess.run(["node", str(CLI_PATH), "--help"], capture_output=True, text=True)
        assert result.returncode == 0
        assert "Usage" in result.stdout or "Options" in result.stdout
    except FileNotFoundError:
        pytest.skip("Node.js not found in path")

def test_brain_command_help():
    # Test python tools/brain/brain_cli.py --help
    brain_cli = ROOT_DIR / "tools" / "brain" / "brain_cli.py"
    if not brain_cli.exists():
        pytest.fail("brain_cli.py not found")
        
    result = subprocess.run([sys.executable, str(brain_cli), "--help"], capture_output=True, text=True)
    assert result.returncode == 0
