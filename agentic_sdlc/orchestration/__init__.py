"""
Multi-Agent Orchestration System

A sophisticated workflow management platform that enables intelligent routing and execution 
of complex tasks through specialized sub-agents. The system evaluates user requests, 
matches them to appropriate workflows, and orchestrates multiple specialized agents to 
execute tasks independently while maintaining coordination and state management.

Key Components:
- Main Agent: Primary interface for user interaction and request processing
- Workflow Engine: Evaluates requests and matches them to appropriate workflow patterns
- Orchestrator: Central coordination hub that manages agent execution and workflow state
- CLI Interface: Manages independent CLI-based agent processes
- Specialized Agents: PM, BA, SA, Research, Quality Judge, Implementation agents
- State Manager: Persists and manages workflow execution state
- Model Optimizer: Selects appropriate model strength based on task complexity
"""

__version__ = "1.0.0"

# Core data models
from .models.workflow import (
    WorkflowState,
    WorkflowExecution,
    WorkflowPlan,
    OrchestrationPattern,
    ExecutionStatus
)

from .models.agent import (
    AgentTask,
    AgentResult,
    AgentState,
    AgentType,
    AgentProcess,
    TaskStatus,
    ModelTier
)

from .models.communication import (
    UserRequest,
    TaskInput,
    TaskOutput,
    SharedContext,
    Checkpoint
)

# Core components
from .agents.main_agent import MainAgent
from .engine.model_optimizer import ModelOptimizer
from .interfaces.cli_interface import CLIInterface

__all__ = [
    # Data models
    "WorkflowState",
    "WorkflowExecution", 
    "WorkflowPlan",
    "OrchestrationPattern",
    "ExecutionStatus",
    "AgentTask",
    "AgentResult",
    "AgentState",
    "AgentType",
    "AgentProcess",
    "TaskStatus",
    "ModelTier",
    "UserRequest",
    "TaskInput",
    "TaskOutput",
    "SharedContext",
    "Checkpoint",
    # Core components
    "MainAgent",
    "CLIInterface",
    # Future components (commented out until implemented)
    # "WorkflowEngine", 
    # "Orchestrator",
    # "StateManager",
    "ModelOptimizer",
]