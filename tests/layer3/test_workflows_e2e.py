
import pytest
import subprocess
import sys
from pathlib import Path

ROOT_DIR = Path(__file__).parents[2]

def test_health_check_dry_run():
    script = ROOT_DIR / "tools" / "validation" / "health-check.py"
    if not script.exists():
        pytest.fail("health-check.py not found")
    
    # The script might exit with 1 if checks fail, which is expected behavior
    # We just want to ensure it runs without crashing (traceback)
    result = subprocess.run([sys.executable, str(script), "--help"], capture_output=True, text=True)
    assert result.returncode in [0, 1]
    assert "Health Check Summary" in result.stdout

def test_cycle_workflow_exists():
    script = ROOT_DIR / "tools" / "workflows" / "cycle.py"
    assert script.exists()
