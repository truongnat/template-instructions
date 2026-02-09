"""
Communication-related data models for the Multi-Agent Orchestration System

This module defines the core data structures for communication between components,
including user requests, task communication, shared context, and checkpoints.
"""

from datetime import datetime
from enum import Enum
from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass, field
from uuid import uuid4


class TaskType(Enum):
    """Types of tasks that can be executed"""
    ANALYSIS = "analysis"
    DESIGN = "design"
    IMPLEMENTATION = "implementation"
    TESTING = "testing"
    REVIEW = "review"
    RESEARCH = "research"
    DOCUMENTATION = "documentation"


class DataFormat(Enum):
    """Data formats for task input/output"""
    JSON = "json"
    TEXT = "text"
    MARKDOWN = "markdown"
    XML = "xml"
    YAML = "yaml"


class TaskPriority(Enum):
    """Priority levels for tasks"""
    CRITICAL = 1
    HIGH = 2
    MEDIUM = 3
    LOW = 4
    BACKGROUND = 5


@dataclass
class ConversationContext:
    """Context for maintaining conversation state"""
    conversation_id: str = field(default_factory=lambda: str(uuid4()))
    user_id: str = ""
    session_start: datetime = field(default_factory=datetime.now)
    last_interaction: datetime = field(default_factory=datetime.now)
    interaction_count: int = 0
    context_data: Dict[str, Any] = field(default_factory=dict)
    preferences: Dict[str, Any] = field(default_factory=dict)
    
    def update_interaction(self):
        """Update interaction tracking"""
        self.last_interaction = datetime.now()
        self.interaction_count += 1
    
    def add_context(self, key: str, value: Any):
        """Add context data"""
        self.context_data[key] = value
        self.update_interaction()


@dataclass
class UserRequest:
    """User request to the main agent"""
    id: str = field(default_factory=lambda: str(uuid4()))
    user_id: str = ""
    content: str = ""
    timestamp: datetime = field(default_factory=datetime.now)
    context: Optional[ConversationContext] = None
    intent: Optional[str] = None
    confidence: float = 0.0
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def __post_init__(self):
        if self.confidence < 0.0 or self.confidence > 1.0:
            raise ValueError("Confidence must be between 0.0 and 1.0")


@dataclass
class TaskContext:
    """Context information for task execution"""
    workflow_id: str
    phase: str
    dependencies: List[str] = field(default_factory=list)
    shared_data: Dict[str, Any] = field(default_factory=dict)
    constraints: List[str] = field(default_factory=list)


@dataclass
class TaskRequirement:
    """Requirements for a specific task"""
    requirement_id: str
    description: str
    is_mandatory: bool = True
    validation_criteria: List[str] = field(default_factory=list)


@dataclass
class ResultMetadata:
    """Metadata for task results"""
    execution_time: float = 0.0
    model_used: str = ""
    tokens_consumed: int = 0
    cost: float = 0.0
    quality_score: float = 0.0
    confidence: float = 0.0


@dataclass
class ResourceUsage:
    """Resource usage tracking"""
    cpu_time: float = 0.0
    memory_peak: float = 0.0  # in MB
    tokens_used: int = 0
    api_calls: int = 0
    cost: float = 0.0


@dataclass
class TaskInput:
    """Input data for agent tasks"""
    data: Any
    format: DataFormat = DataFormat.JSON
    source: str = ""
    dependencies: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def validate_format(self) -> bool:
        """Validate that data matches the specified format"""
        # Basic validation - can be extended
        if self.format == DataFormat.JSON:
            return isinstance(self.data, (dict, list))
        elif self.format == DataFormat.TEXT:
            return isinstance(self.data, str)
        return True


@dataclass
class TaskOutput:
    """Output data from agent tasks"""
    data: Any
    format: DataFormat = DataFormat.JSON
    confidence: float = 1.0
    metadata: ResultMetadata = None
    next_actions: List[str] = field(default_factory=list)
    
    def __post_init__(self):
        if not 0.0 <= self.confidence <= 1.0:
            raise ValueError("Confidence must be between 0.0 and 1.0")
        if self.metadata is None:
            self.metadata = ResultMetadata()


@dataclass
class AgentContext:
    """Context information for agent execution"""
    workflow_id: str
    agent_id: str
    shared_data: Dict[str, Any] = field(default_factory=dict)
    constraints: List[str] = field(default_factory=list)
    preferences: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ResourceAllocation:
    """Resource allocation for an agent"""
    cpu_cores: float = 1.0
    memory_mb: float = 512.0
    disk_mb: float = 1024.0
    network_bandwidth: float = 100.0  # Mbps
    gpu_memory_mb: float = 0.0


@dataclass
class AgentError:
    """Error information from agent execution"""
    agent_id: str
    error_type: str
    error_message: str
    timestamp: datetime = field(default_factory=datetime.now)
    stack_trace: Optional[str] = None
    context: Dict[str, Any] = field(default_factory=dict)
    is_recoverable: bool = True
    retry_count: int = 0


@dataclass
class RecoveryAction:
    """Action to take for error recovery"""
    action_type: str  # retry, reassign, skip, abort
    target_agent: Optional[str] = None
    parameters: Dict[str, Any] = field(default_factory=dict)
    max_attempts: int = 3
    delay_seconds: int = 0


@dataclass
class ClarifiedRequest:
    """Clarified user request after processing"""
    original_request: UserRequest
    clarified_content: str
    extracted_requirements: List[str] = field(default_factory=list)
    identified_constraints: List[str] = field(default_factory=list)
    suggested_approach: str = ""
    confidence: float = 0.0
    
    def __post_init__(self):
        if self.confidence < 0.0 or self.confidence > 1.0:
            raise ValueError("Confidence must be between 0.0 and 1.0")


@dataclass
class WorkflowInitiation:
    """Result of request processing for workflow initiation"""
    request_id: str
    should_proceed: bool
    workflow_type: Optional[str] = None
    estimated_complexity: str = "medium"  # low, medium, high
    required_clarifications: List[str] = field(default_factory=list)
    suggested_next_steps: List[str] = field(default_factory=list)
    clarified_request: Optional['ClarifiedRequest'] = None


@dataclass
class Requirement:
    """Business or technical requirement"""
    id: str = field(default_factory=lambda: str(uuid4()))
    title: str = ""
    description: str = ""
    type: str = "functional"  # functional, non-functional, constraint
    priority: str = "medium"  # low, medium, high, critical
    source: str = ""
    acceptance_criteria: List[str] = field(default_factory=list)
    
    def add_acceptance_criterion(self, criterion: str):
        """Add an acceptance criterion"""
        if criterion not in self.acceptance_criteria:
            self.acceptance_criteria.append(criterion)


@dataclass
class Constraint:
    """System or business constraint"""
    id: str = field(default_factory=lambda: str(uuid4()))
    name: str = ""
    description: str = ""
    type: str = "technical"  # technical, business, regulatory, resource
    impact: str = "medium"  # low, medium, high
    is_negotiable: bool = True


@dataclass
class Stakeholder:
    """Project stakeholder information"""
    id: str = field(default_factory=lambda: str(uuid4()))
    name: str = ""
    role: str = ""
    influence: str = "medium"  # low, medium, high
    interest: str = "medium"  # low, medium, high
    contact_info: Dict[str, str] = field(default_factory=dict)
    expectations: List[str] = field(default_factory=list)


@dataclass
class Timeline:
    """Project timeline information"""
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    milestones: List[Dict[str, Any]] = field(default_factory=list)
    critical_path: List[str] = field(default_factory=list)
    buffer_days: int = 0
    
    def add_milestone(self, name: str, date: datetime, description: str = ""):
        """Add a milestone to the timeline"""
        milestone = {
            "name": name,
            "date": date,
            "description": description,
            "id": str(uuid4())
        }
        self.milestones.append(milestone)


@dataclass
class Resource:
    """Project resource information"""
    id: str = field(default_factory=lambda: str(uuid4()))
    name: str = ""
    type: str = "human"  # human, technical, financial, material
    availability: float = 1.0  # 0.0 to 1.0
    cost_per_unit: float = 0.0
    unit: str = "hour"
    skills: List[str] = field(default_factory=list)


@dataclass
class SharedContext:
    """Shared context across all agents in a workflow"""
    project_id: str = field(default_factory=lambda: str(uuid4()))
    requirements: List[Requirement] = field(default_factory=list)
    constraints: List[Constraint] = field(default_factory=list)
    stakeholders: List[Stakeholder] = field(default_factory=list)
    timeline: Optional[Timeline] = None
    resources: List[Resource] = field(default_factory=list)
    shared_data: Dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.now)
    last_updated: datetime = field(default_factory=datetime.now)
    
    def add_requirement(self, requirement: Requirement):
        """Add a requirement to the shared context"""
        self.requirements.append(requirement)
        self.last_updated = datetime.now()
    
    def add_constraint(self, constraint: Constraint):
        """Add a constraint to the shared context"""
        self.constraints.append(constraint)
        self.last_updated = datetime.now()
    
    def update_shared_data(self, key: str, value: Any):
        """Update shared data"""
        self.shared_data[key] = value
        self.last_updated = datetime.now()


@dataclass
class OutputMetadata:
    """Metadata for task outputs"""
    created_at: datetime = field(default_factory=datetime.now)
    created_by: str = ""
    version: str = "1.0"
    format_version: str = "1.0"
    checksum: Optional[str] = None
    size_bytes: int = 0
    encoding: str = "utf-8"


@dataclass
class TaskResult:
    """Result of a completed task"""
    task_id: str
    agent_id: str
    status: str  # Will be TaskStatus enum, but using string to avoid circular import
    output: Any
    metadata: OutputMetadata = field(default_factory=OutputMetadata)
    execution_time: float = 0.0
    quality_score: float = 1.0
    confidence: float = 1.0
    created_at: datetime = field(default_factory=datetime.now)
    
    def __post_init__(self):
        if not 0.0 <= self.quality_score <= 1.0:
            raise ValueError("Quality score must be between 0.0 and 1.0")
        if not 0.0 <= self.confidence <= 1.0:
            raise ValueError("Confidence must be between 0.0 and 1.0")


@dataclass
class Checkpoint:
    """Workflow checkpoint for state persistence"""
    id: str = field(default_factory=lambda: str(uuid4()))
    timestamp: datetime = field(default_factory=datetime.now)
    phase: str = ""
    state: Optional['WorkflowState'] = None
    description: str = ""
    recoverable: bool = True
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def is_recent(self, minutes: int = 30) -> bool:
        """Check if checkpoint is recent"""
        time_diff = datetime.now() - self.timestamp
        return time_diff.total_seconds() < (minutes * 60)


@dataclass
class WorkflowResults:
    """Final results of workflow execution"""
    workflow_id: str
    execution_id: str
    status: str  # ExecutionStatus enum as string
    results: List[TaskResult] = field(default_factory=list)
    summary: str = ""
    recommendations: List[str] = field(default_factory=list)
    quality_metrics: Dict[str, float] = field(default_factory=dict)
    resource_usage: Dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.now)
    
    def add_result(self, result: TaskResult):
        """Add a task result to the workflow results"""
        self.results.append(result)
    
    def calculate_overall_quality(self) -> float:
        """Calculate overall quality score from all results"""
        if not self.results:
            return 0.0
        
        total_quality = sum(result.quality_score for result in self.results)
        return total_quality / len(self.results)
    
    def get_failed_tasks(self) -> List[TaskResult]:
        """Get all failed task results"""
        return [result for result in self.results if result.status == "failed"]