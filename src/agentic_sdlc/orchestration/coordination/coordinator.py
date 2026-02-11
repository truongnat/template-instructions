"""Coordinator for multi-agent orchestration."""

from typing import Any, Dict, List, Optional

from .execution_plan import ExecutionPlan


class Coordinator:
    """Coordinates execution of workflows across multiple agents.
    
    Manages workflow execution, agent coordination, and state management
    during multi-agent orchestration.
    """
    
    def __init__(self) -> None:
        """Initialize the coordinator."""
        self._execution_plans: Dict[str, ExecutionPlan] = {}
        self._active_executions: Dict[str, Dict[str, Any]] = {}
    
    def create_execution_plan(
        self,
        workflow_id: str,
        steps: List[str],
    ) -> ExecutionPlan:
        """Create an execution plan for a workflow.
        
        Args:
            workflow_id: The ID of the workflow
            steps: The list of steps in the workflow
            
        Returns:
            The created ExecutionPlan
        """
        plan = ExecutionPlan(workflow_id=workflow_id, steps=steps)
        self._execution_plans[plan.id] = plan
        return plan
    
    def get_execution_plan(self, plan_id: str) -> Optional[ExecutionPlan]:
        """Get an execution plan by ID.
        
        Args:
            plan_id: The ID of the execution plan
            
        Returns:
            The ExecutionPlan if found, None otherwise
        """
        return self._execution_plans.get(plan_id)
    
    def start_execution(
        self,
        plan_id: str,
        context: Optional[Dict[str, Any]] = None,
    ) -> str:
        """Start execution of a plan.
        
        Args:
            plan_id: The ID of the execution plan
            context: Optional execution context
            
        Returns:
            The execution ID
            
        Raises:
            ValueError: If the plan is not found
        """
        plan = self.get_execution_plan(plan_id)
        if plan is None:
            raise ValueError(f"Execution plan {plan_id} not found")
        
        execution_id = f"exec_{plan_id}"
        self._active_executions[execution_id] = {
            "plan_id": plan_id,
            "context": context or {},
            "status": "running",
            "results": {},
        }
        return execution_id
    
    def get_execution_status(self, execution_id: str) -> Optional[str]:
        """Get the status of an execution.
        
        Args:
            execution_id: The ID of the execution
            
        Returns:
            The execution status if found, None otherwise
        """
        execution = self._active_executions.get(execution_id)
        if execution is None:
            return None
        return execution.get("status")
    
    def complete_execution(self, execution_id: str) -> None:
        """Mark an execution as complete.
        
        Args:
            execution_id: The ID of the execution
            
        Raises:
            ValueError: If the execution is not found
        """
        if execution_id not in self._active_executions:
            raise ValueError(f"Execution {execution_id} not found")
        self._active_executions[execution_id]["status"] = "completed"
    
    def fail_execution(self, execution_id: str, error: str) -> None:
        """Mark an execution as failed.
        
        Args:
            execution_id: The ID of the execution
            error: The error message
            
        Raises:
            ValueError: If the execution is not found
        """
        if execution_id not in self._active_executions:
            raise ValueError(f"Execution {execution_id} not found")
        self._active_executions[execution_id]["status"] = "failed"
        self._active_executions[execution_id]["error"] = error
