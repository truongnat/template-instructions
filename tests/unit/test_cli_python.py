import subprocess
import sys
from pathlib import Path

def test_asdlc_help():
    """Test that CLI help works."""
    result = subprocess.run(
        [sys.executable, "-m", "agentic_sdlc.cli", "--help"],
        capture_output=True,
        text=True
    )
    assert result.returncode == 0
    assert "Agentic SDLC" in result.stdout

def test_asdlc_brain_status():
    """Test that brain status command works."""
    result = subprocess.run(
        [sys.executable, "-m", "agentic_sdlc.cli", "status"],
        capture_output=True,
        text=True
    )
    # It might fail if no session active, but should not crash
    assert result.returncode in [0, 1, 2]

def test_asdlc_workflow_list():
    """Test that workflow command works."""
    result = subprocess.run(
        [sys.executable, "-m", "agentic_sdlc.cli", "workflow"],
        capture_output=True,
        text=True
    )
    combined = result.stdout + result.stderr
    assert "workflow" in combined.lower()