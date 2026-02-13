"""Execution plan for workflow coordination."""

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional
from uuid import uuid4


@dataclass
class ExecutionPlan:
    """Represents an execution plan for a workflow.
    
    An execution plan defines how a workflow will be executed,
    including the order of steps and resource allocation.
    """
    
    workflow_id: str
    steps: List[str] = field(default_factory=list)
    agent_assignments: Dict[str, str] = field(default_factory=dict)
    resource_allocation: Dict[str, Any] = field(default_factory=dict)
    id: str = field(default_factory=lambda: str(uuid4()))
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def __post_init__(self) -> None:
        """Validate execution plan."""
        if not self.workflow_id:
            raise ValueError("Workflow ID cannot be empty")
    
    def add_step(self, step_name: str) -> None:
        """Add a step to the execution plan.
        
        Args:
            step_name: The name of the step
        """
        if step_name not in self.steps:
            self.steps.append(step_name)
    
    def assign_agent(self, step_name: str, agent_id: str) -> None:
        """Assign an agent to a step.
        
        Args:
            step_name: The name of the step
            agent_id: The ID of the agent
        """
        self.agent_assignments[step_name] = agent_id
    
    def allocate_resource(self, resource_name: str, amount: Any) -> None:
        """Allocate a resource for the execution.
        
        Args:
            resource_name: The name of the resource
            amount: The amount to allocate
        """
        self.resource_allocation[resource_name] = amount
