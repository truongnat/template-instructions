"""Task schema definition."""

from dataclasses import dataclass, field
from typing import Optional, Dict, Any, List
from models.enums import TaskStatus


@dataclass
class TaskSchema:
    """Schema for task configuration.
    
    Attributes:
        id: Unique task identifier (required)
        type: Task type (required)
        name: Human-readable task name
        description: Optional task description
        agent_id: ID of the agent assigned to this task
        dependencies: List of task IDs that must complete before this task
        timeout: Task timeout in seconds
        status: Current task execution status
        config: Task-specific configuration
        inputs: Task input parameters
        outputs: Task output results
        metadata: Additional task metadata
    """
    id: str
    type: str
    name: Optional[str] = None
    description: Optional[str] = None
    agent_id: Optional[str] = None
    dependencies: List[str] = field(default_factory=list)
    timeout: int = 3600
    status: TaskStatus = TaskStatus.NOT_STARTED
    config: Dict[str, Any] = field(default_factory=dict)
    inputs: Dict[str, Any] = field(default_factory=dict)
    outputs: Dict[str, Any] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def __post_init__(self):
        """Validate task schema after initialization."""
        if not self.id:
            raise ValueError("Task id is required")
        if not self.type:
            raise ValueError("Task type is required")
        if self.timeout < 1:
            raise ValueError("Task timeout must be at least 1 second")
        
        # Convert status to enum if it's a string
        if isinstance(self.status, str):
            self.status = TaskStatus(self.status)
        
        # Set default name if not provided
        if not self.name:
            self.name = self.id
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert task schema to dictionary."""
        return {
            'id': self.id,
            'type': self.type,
            'name': self.name,
            'description': self.description,
            'agent_id': self.agent_id,
            'dependencies': self.dependencies,
            'timeout': self.timeout,
            'status': self.status.value,
            'config': self.config,
            'inputs': self.inputs,
            'outputs': self.outputs,
            'metadata': self.metadata,
        }
