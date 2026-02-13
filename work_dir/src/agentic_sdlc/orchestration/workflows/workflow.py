"""Workflow definitions and execution."""

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional
from uuid import uuid4


@dataclass
class WorkflowStep:
    """Represents a single step in a workflow."""
    
    name: str
    agent_id: str
    description: Optional[str] = None
    input_keys: List[str] = field(default_factory=list)
    output_keys: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class Workflow:
    """Represents a workflow definition.
    
    A workflow is a sequence of steps executed by agents to accomplish
    a specific goal or task.
    """
    
    name: str
    description: Optional[str] = None
    steps: List[WorkflowStep] = field(default_factory=list)
    timeout: int = 300
    id: str = field(default_factory=lambda: str(uuid4()))
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def __post_init__(self) -> None:
        """Validate workflow configuration."""
        if not self.name:
            raise ValueError("Workflow name cannot be empty")
        if self.timeout < 1:
            raise ValueError("Workflow timeout must be at least 1")
    
    def add_step(self, step: WorkflowStep) -> None:
        """Add a step to the workflow.
        
        Args:
            step: The step to add
        """
        self.steps.append(step)
    
    def get_step(self, name: str) -> Optional[WorkflowStep]:
        """Get a step by name.
        
        Args:
            name: The name of the step
            
        Returns:
            The step if found, None otherwise
        """
        for step in self.steps:
            if step.name == name:
                return step
        return None
