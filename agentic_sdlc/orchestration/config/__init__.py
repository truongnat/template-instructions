"""
Configuration management for the Multi-Agent Orchestration System

This module provides configuration management, environment variable handling,
and system settings for the orchestration system.
"""

from .settings import (
    OrchestrationConfig,
    AgentPoolConfig,
    ModelConfig,
    LoggingConfig,
    load_config,
    get_default_config
)

from .environment import (
    Environment,
    get_environment,
    is_development,
    is_production,
    is_testing
)

__all__ = [
    "OrchestrationConfig",
    "AgentPoolConfig", 
    "ModelConfig",
    "LoggingConfig",
    "load_config",
    "get_default_config",
    "Environment",
    "get_environment",
    "is_development",
    "is_production",
    "is_testing"
]