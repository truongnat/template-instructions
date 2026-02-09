"""
Core data models for the Multi-Agent Orchestration System

This module contains all the data models and enums used throughout the orchestration system,
including workflow state management, agent communication, and task execution models.
"""

# Import workflow models first
from .workflow import (
    WorkflowState,
    WorkflowExecution,
    WorkflowPlan,
    OrchestrationPattern,
    ExecutionStatus,
    WorkflowMatch,
    ValidationResult
)

# Import agent models
from .agent import (
    AgentTask,
    AgentResult,
    AgentState,
    AgentType,
    AgentProcess,
    TaskStatus,
    ModelTier,
    AgentConfig,
    AgentAssignment,
    TaskDependency,
    ResourceRequirement,
    PerformanceMetrics,
    InstanceStatus,
    AgentPool,
    LoadBalancer,
    LoadMetrics,
    ModelAssignment,
    ProcessStatus,
    AgentInstance,
    TaskInput,
    TaskOutput,
    DataFormat,
    TaskPriority,
    DEFAULT_MODEL_ASSIGNMENTS
)

# Import communication models
from .communication import (
    UserRequest,
    SharedContext,
    Checkpoint,
    ConversationContext,
    ClarifiedRequest,
    TaskContext,
    TaskRequirement,
    ResultMetadata,
    ResourceUsage,
    OutputMetadata,
    Requirement,
    Constraint,
    Stakeholder,
    Timeline,
    Resource,
    TaskType,
    TaskResult,
    AgentContext,
    ResourceAllocation,
    RecoveryAction,
    AgentError,
    WorkflowResults,
    WorkflowInitiation
)

# Import verification models
from .verification import (
    VerificationGate,
    ApprovalWorkflow,
    ApprovalCriteria,
    ApprovalLevel,
    VerificationStatus,
    UserFeedback,
    PlanModification,
    ModificationType
)

__all__ = [
    # Workflow models
    "WorkflowState",
    "WorkflowExecution",
    "WorkflowPlan", 
    "OrchestrationPattern",
    "ExecutionStatus",
    "WorkflowMatch",
    "ValidationResult",
    
    # Agent models
    "AgentTask",
    "AgentResult",
    "AgentState",
    "AgentType",
    "AgentProcess",
    "TaskStatus",
    "ModelTier",
    "AgentConfig",
    "AgentAssignment",
    "TaskDependency",
    "ResourceRequirement",
    "PerformanceMetrics",
    "InstanceStatus",
    "AgentPool",
    "LoadBalancer",
    "LoadMetrics",
    "ModelAssignment",
    "ProcessStatus",
    "AgentInstance",
    "TaskInput",
    "TaskOutput",
    "DataFormat",
    "TaskPriority",
    "DEFAULT_MODEL_ASSIGNMENTS",
    
    # Communication models
    "UserRequest",
    "SharedContext",
    "Checkpoint",
    "ConversationContext",
    "ClarifiedRequest",
    "TaskContext",
    "TaskRequirement",
    "ResultMetadata",
    "ResourceUsage",
    "OutputMetadata",
    "Requirement",
    "Constraint",
    "Stakeholder",
    "Timeline",
    "Resource",
    "TaskType",
    "TaskResult",
    "AgentContext",
    "ResourceAllocation",
    "RecoveryAction",
    "AgentError",
    "WorkflowResults",
    "WorkflowInitiation",
    
    # Verification models
    "VerificationGate",
    "ApprovalWorkflow",
    "ApprovalCriteria",
    "ApprovalLevel",
    "VerificationStatus",
    "UserFeedback",
    "PlanModification",
    "ModificationType"
]