"""
Shared test fixtures for Agentic SDLC tests.
"""

import pytest
import sys
import os
from pathlib import Path

# Add project root to path
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))
sys.path.insert(0, str(PROJECT_ROOT / "tools"))


@pytest.fixture
def project_root():
    """Return project root path."""
    return PROJECT_ROOT


@pytest.fixture
def agent_dir(project_root):
    """Return .agent directory path."""
    return project_root / ".agent"


@pytest.fixture
def kb_dir(agent_dir):
    """Return knowledge-base directory path."""
    return agent_dir / "knowledge-base"


@pytest.fixture
def tools_dir(project_root):
    """Return tools directory path."""
    return project_root / "tools"
