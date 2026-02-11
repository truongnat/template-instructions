"""Workflow schema definition."""

from dataclasses import dataclass, field
from typing import List, Optional, Dict, Any
from models.enums import WorkflowStatus


@dataclass
class WorkflowSchema:
    """Schema for workflow configuration.
    
    Attributes:
        name: Workflow name (required)
        version: Semantic version string (required)
        description: Optional workflow description
        agents: List of agent IDs to use in the workflow
        tasks: List of task configurations
        timeout: Workflow timeout in seconds (default: 3600)
        status: Current workflow execution status
        config: Additional workflow-specific configuration
    """
    name: str
    version: str
    description: Optional[str] = None
    agents: List[str] = field(default_factory=list)
    tasks: List[Dict[str, Any]] = field(default_factory=list)
    timeout: int = 3600
    status: WorkflowStatus = WorkflowStatus.PENDING
    config: Dict[str, Any] = field(default_factory=dict)
    
    def __post_init__(self):
        """Validate workflow schema after initialization."""
        if not self.name:
            raise ValueError("Workflow name is required")
        if not self.version:
            raise ValueError("Workflow version is required")
        if self.timeout < 1:
            raise ValueError("Workflow timeout must be at least 1 second")
        
        # Convert status to enum if it's a string
        if isinstance(self.status, str):
            self.status = WorkflowStatus(self.status)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert workflow schema to dictionary."""
        return {
            'name': self.name,
            'version': self.version,
            'description': self.description,
            'agents': self.agents,
            'tasks': self.tasks,
            'timeout': self.timeout,
            'status': self.status.value,
            'config': self.config,
        }
