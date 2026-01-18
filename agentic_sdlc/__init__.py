"""
Agentic SDLC - AI-powered Software Development Lifecycle Framework
"""

__version__ = "2.1.0"
__author__ = "Dao Quang Truong"
__email__ = "truongnat@gmail.com"

# Core CLI
from .cli import main

# Infrastructure
try:
    from .infrastructure.autogen.agents import create_agent_by_role
    from .infrastructure.autogen.config import get_model_client
except ImportError:
    # Allow import without autogen if dependencies missing
    create_agent_by_role = None
    get_model_client = None

# Intelligence
try:
    from .intelligence.self_learning.learner import Learner
    from .intelligence.task_manager.sprint_manager import SprintManager
except ImportError:
    Learner = None
    SprintManager = None

# Utils
from .core.utils.common import get_project_root, load_config

__all__ = [
    "main", 
    "create_agent_by_role", 
    "get_model_client",
    "Learner",
    "SprintManager", 
    "get_project_root",
    "load_config",
    "__version__"
]