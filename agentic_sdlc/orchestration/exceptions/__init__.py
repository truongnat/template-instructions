"""
Exception classes for the Multi-Agent Orchestration System

This module defines custom exception classes for different types of errors
that can occur in the orchestration system.
"""

from .base import (
    OrchestrationError,
    OrchestrationWarning
)

from .workflow import (
    WorkflowError,
    WorkflowValidationError,
    WorkflowExecutionError,
    WorkflowTimeoutError,
    WorkflowStateError
)

from .agent import (
    AgentError,
    AgentInitializationError,
    AgentExecutionError,
    AgentCommunicationError,
    AgentTimeoutError,
    AgentPoolError
)

from .model import (
    ModelError,
    ModelConfigurationError,
    ModelAPIError,
    ModelRateLimitError,
    ModelTimeoutError
)

from .cli import (
    CLIError,
    CLIProcessError,
    CLITimeoutError,
    CLICommunicationError
)

from .state import (
    StateError,
    StateCorruptionError,
    StatePersistenceError,
    StateRecoveryError
)

__all__ = [
    # Base exceptions
    "OrchestrationError",
    "OrchestrationWarning",
    
    # Workflow exceptions
    "WorkflowError",
    "WorkflowValidationError",
    "WorkflowExecutionError",
    "WorkflowTimeoutError",
    "WorkflowStateError",
    
    # Agent exceptions
    "AgentError",
    "AgentInitializationError",
    "AgentExecutionError",
    "AgentCommunicationError",
    "AgentTimeoutError",
    "AgentPoolError",
    
    # Model exceptions
    "ModelError",
    "ModelConfigurationError",
    "ModelAPIError",
    "ModelRateLimitError",
    "ModelTimeoutError",
    
    # CLI exceptions
    "CLIError",
    "CLIProcessError",
    "CLITimeoutError",
    "CLICommunicationError",
    
    # State exceptions
    "StateError",
    "StateCorruptionError",
    "StatePersistenceError",
    "StateRecoveryError"
]