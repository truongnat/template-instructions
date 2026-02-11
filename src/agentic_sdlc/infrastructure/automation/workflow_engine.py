"""Workflow engine for executing workflows."""

from typing import Any, Dict, List, Optional
from dataclasses import dataclass


@dataclass
class WorkflowStep:
    """Represents a single step in a workflow."""
    
    name: str
    action: str
    parameters: Dict[str, Any]
    depends_on: Optional[List[str]] = None


class WorkflowEngine:
    """Engine for executing workflows.
    
    The WorkflowEngine is responsible for orchestrating the execution of
    workflow steps, managing dependencies, and handling errors.
    """
    
    def __init__(self) -> None:
        """Initialize the workflow engine."""
        self._steps: Dict[str, WorkflowStep] = {}
        self._results: Dict[str, Any] = {}
    
    def add_step(self, step: WorkflowStep) -> None:
        """Add a step to the workflow.
        
        Args:
            step: The workflow step to add.
        """
        self._steps[step.name] = step
    
    def execute(self) -> Dict[str, Any]:
        """Execute the workflow.
        
        Returns:
            Dictionary containing results from all steps.
        """
        self._results = {}
        for step_name, step in self._steps.items():
            self._results[step_name] = self._execute_step(step)
        return self._results
    
    def _execute_step(self, step: WorkflowStep) -> Any:
        """Execute a single workflow step.
        
        Args:
            step: The step to execute.
            
        Returns:
            The result of executing the step.
        """
        # Check dependencies
        if step.depends_on:
            for dep in step.depends_on:
                if dep not in self._results:
                    raise RuntimeError(f"Dependency {dep} not executed yet")
        
        # Execute the step (simplified implementation)
        return {"step": step.name, "action": step.action, "status": "completed"}


class WorkflowRunner:
    """Runner for executing workflows with lifecycle management.
    
    The WorkflowRunner provides a higher-level interface for running
    workflows with setup, execution, and cleanup phases.
    """
    
    def __init__(self, engine: Optional[WorkflowEngine] = None) -> None:
        """Initialize the workflow runner.
        
        Args:
            engine: Optional workflow engine instance. If not provided, creates a new one.
        """
        self.engine = engine or WorkflowEngine()
        self._is_running = False
    
    def run(self, steps: List[WorkflowStep]) -> Dict[str, Any]:
        """Run a workflow with the given steps.
        
        Args:
            steps: List of workflow steps to execute.
            
        Returns:
            Dictionary containing results from all steps.
        """
        self._is_running = True
        try:
            for step in steps:
                self.engine.add_step(step)
            return self.engine.execute()
        finally:
            self._is_running = False
    
    def is_running(self) -> bool:
        """Check if a workflow is currently running.
        
        Returns:
            True if a workflow is running, False otherwise.
        """
        return self._is_running
