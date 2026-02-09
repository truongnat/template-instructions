"""
Workflow-related data models for the Multi-Agent Orchestration System

This module defines the core data structures for workflow management, including
workflow state, execution plans, orchestration patterns, and validation results.
"""

from datetime import datetime
from enum import Enum
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field
from uuid import uuid4


class OrchestrationPattern(Enum):
    """Orchestration patterns supported by the system"""
    SEQUENTIAL_HANDOFF = "sequential_handoff"
    PARALLEL_EXECUTION = "parallel_execution"
    DYNAMIC_ROUTING = "dynamic_routing"
    HIERARCHICAL_DELEGATION = "hierarchical_delegation"


class ExecutionStatus(Enum):
    """Status of workflow execution"""
    PENDING = "pending"
    RUNNING = "running"
    PAUSED = "paused"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


@dataclass
class WorkflowMatch:
    """Represents a potential workflow match for a user request"""
    workflow_id: str
    relevance_score: float
    pattern: OrchestrationPattern
    estimated_duration: int  # in minutes
    required_agents: List[str]
    confidence: float
    prerequisites: List[str] = field(default_factory=list)
    
    def __post_init__(self):
        if not 0.0 <= self.relevance_score <= 1.0:
            raise ValueError("Relevance score must be between 0.0 and 1.0")
        if not 0.0 <= self.confidence <= 1.0:
            raise ValueError("Confidence must be between 0.0 and 1.0")


@dataclass
class ValidationResult:
    """Result of workflow prerequisite validation"""
    is_valid: bool
    missing_prerequisites: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    estimated_setup_time: int = 0  # in minutes
    
    def add_missing_prerequisite(self, prerequisite: str):
        """Add a missing prerequisite"""
        if prerequisite not in self.missing_prerequisites:
            self.missing_prerequisites.append(prerequisite)
            self.is_valid = False
    
    def add_warning(self, warning: str):
        """Add a validation warning"""
        if warning not in self.warnings:
            self.warnings.append(warning)


@dataclass
class WorkflowPlan:
    """Execution plan for a workflow"""
    id: str = field(default_factory=lambda: str(uuid4()))
    pattern: OrchestrationPattern = OrchestrationPattern.SEQUENTIAL_HANDOFF
    agents: List['AgentAssignment'] = field(default_factory=list)
    dependencies: List['TaskDependency'] = field(default_factory=list)
    estimated_duration: int = 0  # in minutes
    required_resources: List['ResourceRequirement'] = field(default_factory=list)
    created_at: datetime = field(default_factory=datetime.now)
    priority: int = 1  # 1 = highest, 5 = lowest
    
    def add_agent_assignment(self, assignment: 'AgentAssignment'):
        """Add an agent assignment to the plan"""
        self.agents.append(assignment)
    
    def add_dependency(self, dependency: 'TaskDependency'):
        """Add a task dependency to the plan"""
        self.dependencies.append(dependency)
    
    def get_total_estimated_cost(self) -> float:
        """Calculate total estimated cost for the workflow"""
        return sum(resource.estimated_cost for resource in self.required_resources)


@dataclass
class WorkflowExecution:
    """Runtime state of workflow execution"""
    id: str = field(default_factory=lambda: str(uuid4()))
    plan_id: str = ""
    status: ExecutionStatus = ExecutionStatus.PENDING
    current_phase: str = ""
    active_agents: List[str] = field(default_factory=list)
    completed_tasks: List['TaskResult'] = field(default_factory=list)
    next_actions: List[str] = field(default_factory=list)
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    error_message: Optional[str] = None
    progress_percentage: float = 0.0
    
    def start_execution(self):
        """Mark the execution as started"""
        self.status = ExecutionStatus.RUNNING
        self.started_at = datetime.now()
    
    def complete_execution(self):
        """Mark the execution as completed"""
        self.status = ExecutionStatus.COMPLETED
        self.completed_at = datetime.now()
        self.progress_percentage = 100.0
    
    def fail_execution(self, error_message: str):
        """Mark the execution as failed"""
        self.status = ExecutionStatus.FAILED
        self.completed_at = datetime.now()
        self.error_message = error_message
    
    def update_progress(self, percentage: float):
        """Update execution progress"""
        if not 0.0 <= percentage <= 100.0:
            raise ValueError("Progress percentage must be between 0.0 and 100.0")
        self.progress_percentage = percentage
    
    def get_duration(self) -> Optional[int]:
        """Get execution duration in minutes"""
        if self.started_at is None:
            return None
        end_time = self.completed_at or datetime.now()
        return int((end_time - self.started_at).total_seconds() / 60)


@dataclass
class WorkflowState:
    """Complete state of a workflow including execution and agent states"""
    execution_id: str
    current_phase: str
    completed_phases: List[str] = field(default_factory=list)
    agent_states: Dict[str, 'AgentState'] = field(default_factory=dict)
    shared_context: 'SharedContext' = None
    checkpoints: List['Checkpoint'] = field(default_factory=list)
    last_updated: datetime = field(default_factory=datetime.now)
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def add_checkpoint(self, checkpoint: 'Checkpoint'):
        """Add a checkpoint to the workflow state"""
        self.checkpoints.append(checkpoint)
        self.last_updated = datetime.now()
    
    def update_agent_state(self, agent_id: str, state: 'AgentState'):
        """Update the state of a specific agent"""
        self.agent_states[agent_id] = state
        self.last_updated = datetime.now()
    
    def complete_phase(self, phase: str):
        """Mark a phase as completed"""
        if phase not in self.completed_phases:
            self.completed_phases.append(phase)
            self.last_updated = datetime.now()
    
    def get_latest_checkpoint(self) -> Optional['Checkpoint']:
        """Get the most recent checkpoint"""
        if not self.checkpoints:
            return None
        return max(self.checkpoints, key=lambda c: c.timestamp)
    
    def is_recoverable(self) -> bool:
        """Check if the workflow state is recoverable"""
        latest_checkpoint = self.get_latest_checkpoint()
        return latest_checkpoint is not None and latest_checkpoint.recoverable