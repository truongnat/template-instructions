"""
Agent-related data models for the Multi-Agent Orchestration System

This module defines the core data structures for agent management, including
agent tasks, results, states, and multi-instance process management.
"""

from datetime import datetime
from enum import Enum
from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass, field
from uuid import uuid4

# Import shared classes from communication module to avoid circular imports
# These will be imported when needed


class AgentType(Enum):
    """Types of specialized agents in the system"""
    PM = "product_manager"
    BA = "business_analyst"
    SA = "solution_architect"
    RESEARCH = "research"
    QUALITY_JUDGE = "quality_judge"
    IMPLEMENTATION = "implementation"


class TaskStatus(Enum):
    """Status of individual tasks"""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class ModelTier(Enum):
    """Model tiers for hierarchical model assignment"""
    STRATEGIC = "strategic"      # PM, BA, SA roles - use advanced models
    OPERATIONAL = "operational"  # Implementation, Testing - use lightweight models
    RESEARCH = "research"        # Research, Quality Judge - use medium models


class ProcessStatus(Enum):
    """Status of CLI agent processes"""
    STARTING = "starting"
    RUNNING = "running"
    IDLE = "idle"
    BUSY = "busy"
    ERROR = "error"
    FAILED = "failed"
    TERMINATED = "terminated"
    UNRESPONSIVE = "unresponsive"


class InstanceStatus(Enum):
    """Status of agent instances in the pool"""
    IDLE = "idle"
    BUSY = "busy"
    FAILED = "failed"
    SCALING_UP = "scaling_up"
    SCALING_DOWN = "scaling_down"


class TaskPriority(Enum):
    """Priority levels for tasks"""
    CRITICAL = 1
    HIGH = 2
    MEDIUM = 3
    LOW = 4
    BACKGROUND = 5


class DataFormat(Enum):
    """Data formats for task input/output"""
    JSON = "json"
    TEXT = "text"
    MARKDOWN = "markdown"
    XML = "xml"
    YAML = "yaml"


@dataclass
class ModelAssignment:
    """Model assignment configuration for agent types"""
    role_type: AgentType
    model_tier: ModelTier
    recommended_model: str
    fallback_model: str
    max_concurrent_instances: int
    cost_per_token: float
    
    def get_effective_model(self, prefer_fallback: bool = False) -> str:
        """Get the effective model to use"""
        return self.fallback_model if prefer_fallback else self.recommended_model


@dataclass
class ResourceRequirement:
    """Resource requirements for tasks or workflows"""
    resource_type: str
    amount: float
    unit: str
    estimated_cost: float = 0.0
    is_critical: bool = False


@dataclass
class TaskDependency:
    """Dependency between tasks"""
    dependent_task_id: str
    prerequisite_task_id: str
    dependency_type: str = "completion"  # completion, data, resource
    is_blocking: bool = True


@dataclass
class AgentAssignment:
    """Assignment of an agent to a workflow"""
    agent_type: AgentType
    instance_id: Optional[str] = None
    model_assignment: Optional[ModelAssignment] = None
    priority: int = 3
    estimated_duration: int = 0  # in minutes
    required_resources: List[ResourceRequirement] = field(default_factory=list)


@dataclass
class TaskRequirement:
    """Requirements for a specific task"""
    requirement_id: str
    description: str
    is_mandatory: bool = True
    validation_criteria: List[str] = field(default_factory=list)


@dataclass
class TaskContext:
    """Context information for task execution"""
    workflow_id: str
    phase: str
    dependencies: List[str] = field(default_factory=list)
    shared_data: Dict[str, Any] = field(default_factory=dict)
    constraints: List[str] = field(default_factory=list)


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
    network_calls: int = 0
    cost: float = 0.0


@dataclass
class TaskOutput:
    """Output data from agent tasks"""
    data: Any
    format: DataFormat = DataFormat.JSON
    confidence: float = 1.0
    metadata: ResultMetadata = field(default_factory=ResultMetadata)
    next_actions: List[str] = field(default_factory=list)
    
    def __post_init__(self):
        if not 0.0 <= self.confidence <= 1.0:
            raise ValueError("Confidence must be between 0.0 and 1.0")


@dataclass
class AgentTask:
    """Task assigned to an agent"""
    id: str = field(default_factory=lambda: str(uuid4()))
    type: str = ""
    input: TaskInput = field(default_factory=lambda: TaskInput(data={}))
    context: TaskContext = field(default_factory=lambda: TaskContext(workflow_id="", phase=""))
    requirements: List[TaskRequirement] = field(default_factory=list)
    priority: TaskPriority = TaskPriority.MEDIUM
    deadline: Optional[datetime] = None
    assigned_instance_id: Optional[str] = None
    created_at: datetime = field(default_factory=datetime.now)
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    
    def start_task(self):
        """Mark the task as started"""
        self.started_at = datetime.now()
    
    def complete_task(self):
        """Mark the task as completed"""
        self.completed_at = datetime.now()
    
    def get_duration(self) -> Optional[int]:
        """Get task duration in seconds"""
        if self.started_at is None:
            return None
        end_time = self.completed_at or datetime.now()
        return int((end_time - self.started_at).total_seconds())
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization"""
        return {
            "id": self.id,
            "type": self.type,
            "input": {
                "data": self.input.data,
                "format": self.input.format.value,
                "source": self.input.source,
                "dependencies": self.input.dependencies,
                "metadata": self.input.metadata
            },
            "context": {
                "workflow_id": self.context.workflow_id,
                "phase": self.context.phase,
                "dependencies": self.context.dependencies,
                "shared_data": self.context.shared_data,
                "constraints": self.context.constraints
            },
            "requirements": [
                {
                    "requirement_id": req.requirement_id,
                    "description": req.description,
                    "is_mandatory": req.is_mandatory,
                    "validation_criteria": req.validation_criteria
                } for req in self.requirements
            ],
            "priority": self.priority.value,
            "deadline": self.deadline.isoformat() if self.deadline else None,
            "assigned_instance_id": self.assigned_instance_id,
            "created_at": self.created_at.isoformat(),
            "started_at": self.started_at.isoformat() if self.started_at else None,
            "completed_at": self.completed_at.isoformat() if self.completed_at else None
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'AgentTask':
        """Create from dictionary"""
        task = cls(
            id=data.get("id", str(uuid4())),
            type=data.get("type", ""),
            priority=TaskPriority(data.get("priority", TaskPriority.MEDIUM.value)),
            assigned_instance_id=data.get("assigned_instance_id")
        )
        
        # Parse input
        input_data = data.get("input", {})
        task.input = TaskInput(
            data=input_data.get("data", {}),
            format=DataFormat(input_data.get("format", DataFormat.JSON.value)),
            source=input_data.get("source", ""),
            dependencies=input_data.get("dependencies", []),
            metadata=input_data.get("metadata", {})
        )
        
        # Parse context
        context_data = data.get("context", {})
        task.context = TaskContext(
            workflow_id=context_data.get("workflow_id", ""),
            phase=context_data.get("phase", ""),
            dependencies=context_data.get("dependencies", []),
            shared_data=context_data.get("shared_data", {}),
            constraints=context_data.get("constraints", [])
        )
        
        # Parse requirements
        req_data = data.get("requirements", [])
        task.requirements = [
            TaskRequirement(
                requirement_id=req.get("requirement_id", ""),
                description=req.get("description", ""),
                is_mandatory=req.get("is_mandatory", True),
                validation_criteria=req.get("validation_criteria", [])
            ) for req in req_data
        ]
        
        # Parse dates
        if data.get("deadline"):
            task.deadline = datetime.fromisoformat(data["deadline"])
        if data.get("created_at"):
            task.created_at = datetime.fromisoformat(data["created_at"])
        if data.get("started_at"):
            task.started_at = datetime.fromisoformat(data["started_at"])
        if data.get("completed_at"):
            task.completed_at = datetime.fromisoformat(data["completed_at"])
        
        return task


@dataclass
class AgentResult:
    """Result from agent task execution"""
    task_id: str
    instance_id: str
    status: TaskStatus
    output: TaskOutput = field(default_factory=lambda: TaskOutput(data={}))
    metadata: ResultMetadata = field(default_factory=ResultMetadata)
    confidence: float = 1.0
    execution_time: float = 0.0
    resources_used: ResourceUsage = field(default_factory=ResourceUsage)
    recommendations: List[str] = field(default_factory=list)
    created_at: datetime = field(default_factory=datetime.now)
    
    def __post_init__(self):
        if not 0.0 <= self.confidence <= 1.0:
            raise ValueError("Confidence must be between 0.0 and 1.0")
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization"""
        return {
            "task_id": self.task_id,
            "instance_id": self.instance_id,
            "status": self.status.value,
            "output": {
                "data": self.output.data,
                "format": self.output.format.value,
                "confidence": self.output.confidence,
                "metadata": {
                    "execution_time": self.output.metadata.execution_time,
                    "model_used": self.output.metadata.model_used,
                    "tokens_consumed": self.output.metadata.tokens_consumed,
                    "cost": self.output.metadata.cost,
                    "quality_score": self.output.metadata.quality_score,
                    "confidence": self.output.metadata.confidence
                },
                "next_actions": self.output.next_actions
            },
            "metadata": {
                "execution_time": self.metadata.execution_time,
                "model_used": self.metadata.model_used,
                "tokens_consumed": self.metadata.tokens_consumed,
                "cost": self.metadata.cost,
                "quality_score": self.metadata.quality_score,
                "confidence": self.metadata.confidence
            },
            "confidence": self.confidence,
            "execution_time": self.execution_time,
            "resources_used": {
                "cpu_time": self.resources_used.cpu_time,
                "memory_peak": self.resources_used.memory_peak,
                "tokens_used": self.resources_used.tokens_used,
                "api_calls": self.resources_used.api_calls,
                "network_calls": self.resources_used.network_calls,
                "cost": self.resources_used.cost
            },
            "recommendations": self.recommendations,
            "created_at": self.created_at.isoformat()
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'AgentResult':
        """Create from dictionary"""
        # Parse output
        output_data = data.get("output", {})
        output_metadata = output_data.get("metadata", {})
        output = TaskOutput(
            data=output_data.get("data", {}),
            format=DataFormat(output_data.get("format", DataFormat.JSON.value)),
            confidence=output_data.get("confidence", 1.0),
            metadata=ResultMetadata(
                execution_time=output_metadata.get("execution_time", 0.0),
                model_used=output_metadata.get("model_used", ""),
                tokens_consumed=output_metadata.get("tokens_consumed", 0),
                cost=output_metadata.get("cost", 0.0),
                quality_score=output_metadata.get("quality_score", 0.0),
                confidence=output_metadata.get("confidence", 0.0)
            ),
            next_actions=output_data.get("next_actions", [])
        )
        
        # Parse metadata
        metadata_data = data.get("metadata", {})
        metadata = ResultMetadata(
            execution_time=metadata_data.get("execution_time", 0.0),
            model_used=metadata_data.get("model_used", ""),
            tokens_consumed=metadata_data.get("tokens_consumed", 0),
            cost=metadata_data.get("cost", 0.0),
            quality_score=metadata_data.get("quality_score", 0.0),
            confidence=metadata_data.get("confidence", 0.0)
        )
        
        # Parse resources
        resources_data = data.get("resources_used", {})
        resources = ResourceUsage(
            cpu_time=resources_data.get("cpu_time", 0.0),
            memory_peak=resources_data.get("memory_peak", 0.0),
            tokens_used=resources_data.get("tokens_used", 0),
            api_calls=resources_data.get("api_calls", 0),
            network_calls=resources_data.get("network_calls", 0),
            cost=resources_data.get("cost", 0.0)
        )
        
        result = cls(
            task_id=data.get("task_id", ""),
            instance_id=data.get("instance_id", ""),
            status=TaskStatus(data.get("status", TaskStatus.COMPLETED.value)),
            output=output,
            metadata=metadata,
            confidence=data.get("confidence", 1.0),
            execution_time=data.get("execution_time", 0.0),
            resources_used=resources,
            recommendations=data.get("recommendations", [])
        )
        
        if data.get("created_at"):
            result.created_at = datetime.fromisoformat(data["created_at"])
        
        return result


@dataclass
class PerformanceMetrics:
    """Performance metrics for agent instances"""
    tasks_completed: int = 0
    average_execution_time: float = 0.0
    success_rate: float = 1.0
    quality_score: float = 1.0
    resource_utilization: float = 0.0
    last_updated: datetime = field(default_factory=datetime.now)
    
    def update_metrics(self, execution_time: float, success: bool, quality: float):
        """Update performance metrics with new data"""
        self.tasks_completed += 1
        
        # Update average execution time
        if self.tasks_completed == 1:
            self.average_execution_time = execution_time
        else:
            self.average_execution_time = (
                (self.average_execution_time * (self.tasks_completed - 1) + execution_time) 
                / self.tasks_completed
            )
        
        # Update success rate
        if success:
            self.success_rate = (
                (self.success_rate * (self.tasks_completed - 1) + 1.0) 
                / self.tasks_completed
            )
        else:
            self.success_rate = (
                (self.success_rate * (self.tasks_completed - 1)) 
                / self.tasks_completed
            )
        
        # Update quality score
        self.quality_score = (
            (self.quality_score * (self.tasks_completed - 1) + quality) 
            / self.tasks_completed
        )
        
        self.last_updated = datetime.now()


@dataclass
class AgentProcess:
    """CLI process information for an agent instance"""
    id: str = field(default_factory=lambda: str(uuid4()))
    instance_id: str = ""
    type: AgentType = AgentType.IMPLEMENTATION
    model_tier: ModelTier = ModelTier.OPERATIONAL
    status: ProcessStatus = ProcessStatus.STARTING
    pid: Optional[int] = None
    start_time: datetime = field(default_factory=datetime.now)
    last_activity: datetime = field(default_factory=datetime.now)
    current_load: float = 0.0
    subprocess_handle: Optional[Any] = None  # subprocess.Popen handle
    config: Optional['AgentConfig'] = None
    current_task: Optional[AgentTask] = None
    
    def update_activity(self):
        """Update the last activity timestamp"""
        self.last_activity = datetime.now()
    
    def is_responsive(self, timeout_minutes: int = 5) -> bool:
        """Check if the process is responsive based on last activity"""
        time_since_activity = datetime.now() - self.last_activity
        return time_since_activity.total_seconds() < (timeout_minutes * 60)


@dataclass
class LoadMetrics:
    """Load balancing metrics"""
    total_instances: int = 0
    active_instances: int = 0
    average_load: float = 0.0
    peak_load: float = 0.0
    queue_length: int = 0
    
    def calculate_load_factor(self) -> float:
        """Calculate overall load factor"""
        if self.total_instances == 0:
            return 0.0
        return self.average_load / self.total_instances


@dataclass
class LoadBalancer:
    """Load balancer for agent instances"""
    strategy: str = "round_robin"  # round_robin, least_loaded, random
    metrics: LoadMetrics = field(default_factory=LoadMetrics)
    
    def should_scale_up(self, threshold: float = 0.8) -> bool:
        """Determine if scaling up is needed"""
        return self.metrics.calculate_load_factor() > threshold
    
    def should_scale_down(self, threshold: float = 0.3) -> bool:
        """Determine if scaling down is possible"""
        return (self.metrics.calculate_load_factor() < threshold and 
                self.metrics.active_instances > 1)


@dataclass
class AgentInstance:
    """Individual agent instance in a pool"""
    instance_id: str = field(default_factory=lambda: str(uuid4()))
    agent_type: AgentType = AgentType.IMPLEMENTATION
    model_assignment: Optional[ModelAssignment] = None
    current_task: Optional[AgentTask] = None
    task_queue: List[AgentTask] = field(default_factory=list)
    performance: PerformanceMetrics = field(default_factory=PerformanceMetrics)
    status: InstanceStatus = InstanceStatus.IDLE
    created_at: datetime = field(default_factory=datetime.now)
    
    def assign_task(self, task: AgentTask):
        """Assign a task to this instance"""
        if self.status == InstanceStatus.IDLE:
            self.current_task = task
            self.status = InstanceStatus.BUSY
            task.assigned_instance_id = self.instance_id
        else:
            self.task_queue.append(task)
    
    def complete_current_task(self) -> Optional[AgentTask]:
        """Complete the current task and return it"""
        completed_task = self.current_task
        self.current_task = None
        
        # Start next task if available
        if self.task_queue:
            self.current_task = self.task_queue.pop(0)
        else:
            self.status = InstanceStatus.IDLE
            
        return completed_task


@dataclass
class AgentPool:
    """Pool of agent instances for a specific role type"""
    role_type: AgentType
    max_instances: int
    active_instances: List[AgentInstance] = field(default_factory=list)
    queued_tasks: List[AgentTask] = field(default_factory=list)
    load_balancer: LoadBalancer = field(default_factory=LoadBalancer)
    
    def get_available_instance(self) -> Optional[AgentInstance]:
        """Get an available instance for task assignment"""
        idle_instances = [i for i in self.active_instances if i.status == InstanceStatus.IDLE]
        if idle_instances:
            return idle_instances[0]
        return None
    
    def add_instance(self, instance: AgentInstance):
        """Add a new instance to the pool"""
        if len(self.active_instances) < self.max_instances:
            self.active_instances.append(instance)
        else:
            raise ValueError(f"Pool already at maximum capacity ({self.max_instances})")
    
    def remove_instance(self, instance_id: str) -> bool:
        """Remove an instance from the pool"""
        for i, instance in enumerate(self.active_instances):
            if instance.instance_id == instance_id:
                if instance.status == InstanceStatus.IDLE:
                    self.active_instances.pop(i)
                    return True
                else:
                    instance.status = InstanceStatus.SCALING_DOWN
                    return True
        return False


@dataclass
class AgentConfig:
    """Configuration for agent initialization"""
    agent_type: AgentType
    model_assignment: ModelAssignment
    max_retries: int = 3
    timeout_minutes: int = 30
    resource_limits: Dict[str, Any] = field(default_factory=dict)
    environment_variables: Dict[str, str] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization"""
        return {
            "agent_type": self.agent_type.value,
            "model_assignment": {
                "role_type": self.model_assignment.role_type.value,
                "model_tier": self.model_assignment.model_tier.value,
                "recommended_model": self.model_assignment.recommended_model,
                "fallback_model": self.model_assignment.fallback_model,
                "max_concurrent_instances": self.model_assignment.max_concurrent_instances,
                "cost_per_token": self.model_assignment.cost_per_token
            },
            "max_retries": self.max_retries,
            "timeout_minutes": self.timeout_minutes,
            "resource_limits": self.resource_limits,
            "environment_variables": self.environment_variables
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'AgentConfig':
        """Create from dictionary"""
        # Parse model assignment
        ma_data = data.get("model_assignment", {})
        model_assignment = ModelAssignment(
            role_type=AgentType(ma_data.get("role_type", AgentType.IMPLEMENTATION.value)),
            model_tier=ModelTier(ma_data.get("model_tier", ModelTier.OPERATIONAL.value)),
            recommended_model=ma_data.get("recommended_model", ""),
            fallback_model=ma_data.get("fallback_model", ""),
            max_concurrent_instances=ma_data.get("max_concurrent_instances", 1),
            cost_per_token=ma_data.get("cost_per_token", 0.001)
        )
        
        return cls(
            agent_type=AgentType(data.get("agent_type", AgentType.IMPLEMENTATION.value)),
            model_assignment=model_assignment,
            max_retries=data.get("max_retries", 3),
            timeout_minutes=data.get("timeout_minutes", 30),
            resource_limits=data.get("resource_limits", {}),
            environment_variables=data.get("environment_variables", {})
        )


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
class AgentState:
    """State of an individual agent"""
    agent_id: str
    status: TaskStatus = TaskStatus.PENDING
    current_task: Optional[AgentTask] = None
    completed_tasks: List['TaskResult'] = field(default_factory=list)
    context: AgentContext = field(default_factory=lambda: AgentContext(workflow_id="", agent_id=""))
    resources: ResourceAllocation = field(default_factory=ResourceAllocation)
    last_updated: datetime = field(default_factory=datetime.now)
    
    def update_status(self, status: TaskStatus):
        """Update agent status"""
        self.status = status
        self.last_updated = datetime.now()
    
    def add_completed_task(self, task_result: 'TaskResult'):
        """Add a completed task result"""
        self.completed_tasks.append(task_result)
        self.last_updated = datetime.now()


# Default model assignments based on the design document
DEFAULT_MODEL_ASSIGNMENTS = [
    ModelAssignment(
        role_type=AgentType.PM,
        model_tier=ModelTier.STRATEGIC,
        recommended_model="gpt-4-turbo",
        fallback_model="gpt-4",
        max_concurrent_instances=3,
        cost_per_token=0.01
    ),
    ModelAssignment(
        role_type=AgentType.BA,
        model_tier=ModelTier.STRATEGIC,
        recommended_model="claude-3.5-sonnet",
        fallback_model="claude-3-sonnet",
        max_concurrent_instances=3,
        cost_per_token=0.015
    ),
    ModelAssignment(
        role_type=AgentType.SA,
        model_tier=ModelTier.STRATEGIC,
        recommended_model="gpt-4-turbo",
        fallback_model="gpt-4",
        max_concurrent_instances=2,
        cost_per_token=0.01
    ),
    ModelAssignment(
        role_type=AgentType.IMPLEMENTATION,
        model_tier=ModelTier.OPERATIONAL,
        recommended_model="gpt-3.5-turbo",
        fallback_model="claude-3-haiku",
        max_concurrent_instances=5,
        cost_per_token=0.002
    ),
    ModelAssignment(
        role_type=AgentType.RESEARCH,
        model_tier=ModelTier.RESEARCH,
        recommended_model="gpt-4-mini",
        fallback_model="claude-3-haiku",
        max_concurrent_instances=4,
        cost_per_token=0.0015
    ),
    ModelAssignment(
        role_type=AgentType.QUALITY_JUDGE,
        model_tier=ModelTier.RESEARCH,
        recommended_model="claude-3-sonnet",
        fallback_model="gpt-4-mini",
        max_concurrent_instances=2,
        cost_per_token=0.003
    )
]