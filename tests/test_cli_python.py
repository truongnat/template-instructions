import subprocess
import sys
from pathlib import Path

def test_asdlc_help():
    """Test that asdlc.py help works."""
    result = subprocess.run(
        [sys.executable, "asdlc.py", "--help"],
        capture_output=True,
        text=True
    )
    assert result.returncode == 0
    assert "Agentic SDLC - Unified CLI" in result.stdout

def test_asdlc_brain_status():
    """Test that asdlc.py brain status works."""
    result = subprocess.run(
        [sys.executable, "asdlc.py", "brain", "status"],
        capture_output=True,
        text=True
    )
    # Even if it fails due to missing state, it should run the script
    assert "BRAIN" in result.stdout.upper()

def test_asdlc_workflow_list():
    """Test that asdlc.py workflow help works."""
    result = subprocess.run(
        [sys.executable, "asdlc.py", "workflow"],
        capture_output=True,
        text=True
    )
    assert "Available workflows" in result.stdout
