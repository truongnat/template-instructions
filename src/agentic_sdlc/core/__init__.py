"""Core SDK functionality.

This module provides fundamental SDK components including configuration management,
exception handling, logging setup, and resource loading.
"""

from .config import Config, get_config, load_config
from .exceptions import (
    AgenticSDLCError,
    AgentError,
    ConfigurationError,
    ModelError,
    PluginError,
    ValidationError,
    WorkflowError,
)
from .logging import get_logger, setup_logging
from .resources import get_resource_path, list_resources, load_resource_text
from .types import AgentConfig, ModelConfig, SDKConfig, WorkflowConfig

__all__ = [
    # Configuration
    "Config",
    "load_config",
    "get_config",
    # Configuration types
    "ModelConfig",
    "AgentConfig",
    "WorkflowConfig",
    "SDKConfig",
    # Exceptions
    "AgenticSDLCError",
    "ConfigurationError",
    "ValidationError",
    "PluginError",
    "WorkflowError",
    "AgentError",
    "ModelError",
    # Logging
    "setup_logging",
    "get_logger",
    # Resources
    "get_resource_path",
    "load_resource_text",
    "list_resources",
]
