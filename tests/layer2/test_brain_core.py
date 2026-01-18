
import pytest
import sys
from pathlib import Path
from unittest.mock import MagicMock, patch

# imports should work via conftest path setup

# Minimal test to verify imports and basic brain CLI structure
# detailed logic tests would require mocking Neo4j and other dependencies


def test_brain_cli_import():
    try:
        from agentic_sdlc.core.brain import brain_cli
        assert brain_cli is not None
    except ImportError as e:
        pytest.fail(f"Failed to import brain_cli: {e}")

@patch('agentic_sdlc.core.brain.brain_cli.state_manager')
def test_brain_status_command(mock_state_manager):
    from agentic_sdlc.core.brain.brain_cli import cmd_status
    
    # Run status
    cmd_status([])
    
    # Verify state_manager.main was called with proper args
    mock_state_manager.main.assert_called_with(["--status"])
