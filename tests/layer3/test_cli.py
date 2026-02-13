import pytest
import subprocess
import sys
from pathlib import Path

def test_cli_help():
    # Test python -m agentic_sdlc.cli --help
    result = subprocess.run([sys.executable, "-m", "agentic_sdlc.cli", "--help"], capture_output=True, text=True)
    assert result.returncode == 0
    assert "demand" in result.stdout or "init" in result.stdout
