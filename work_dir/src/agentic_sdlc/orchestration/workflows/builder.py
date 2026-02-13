"""Workflow builder for constructing workflows programmatically."""

from typing import Any, Dict, List, Optional

from .workflow import Workflow, WorkflowStep


class WorkflowBuilder:
    """Builder for constructing workflows programmatically.
    
    Provides a fluent interface for building workflows step by step.
    """
    
    def __init__(self, name: str, description: Optional[str] = None) -> None:
        """Initialize the workflow builder.
        
        Args:
            name: The name of the workflow
            description: Optional description of the workflow
        """
        self._workflow = Workflow(name=name, description=description)
    
    def add_step(
        self,
        name: str,
        agent_id: str,
        description: Optional[str] = None,
        input_keys: Optional[List[str]] = None,
        output_keys: Optional[List[str]] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> "WorkflowBuilder":
        """Add a step to the workflow.
        
        Args:
            name: The name of the step
            agent_id: The ID of the agent to execute this step
            description: Optional description of the step
            input_keys: Optional list of input keys
            output_keys: Optional list of output keys
            metadata: Optional metadata for the step
            
        Returns:
            Self for method chaining
        """
        step = WorkflowStep(
            name=name,
            agent_id=agent_id,
            description=description,
            input_keys=input_keys or [],
            output_keys=output_keys or [],
            metadata=metadata or {},
        )
        self._workflow.add_step(step)
        return self
    
    def set_timeout(self, timeout: int) -> "WorkflowBuilder":
        """Set the workflow timeout.
        
        Args:
            timeout: The timeout in seconds
            
        Returns:
            Self for method chaining
        """
        self._workflow.timeout = timeout
        return self
    
    def set_metadata(self, key: str, value: Any) -> "WorkflowBuilder":
        """Set metadata for the workflow.
        
        Args:
            key: The metadata key
            value: The metadata value
            
        Returns:
            Self for method chaining
        """
        self._workflow.metadata[key] = value
        return self
    
    def build(self) -> Workflow:
        """Build and return the workflow.
        
        Returns:
            The constructed Workflow instance
            
        Raises:
            ValueError: If the workflow has no steps
        """
        if not self._workflow.steps:
            raise ValueError("Workflow must have at least one step")
        return self._workflow
