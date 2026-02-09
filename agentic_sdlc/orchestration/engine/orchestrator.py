"""
Orchestrator for Multi-Agent Workflow Execution

This module implements the Orchestrator class that manages workflow execution,
agent coordination, and task distribution across multiple agent instances.

Requirements: 3.1, 3.2, 3.3, 3.5
"""

import asyncio
import threading
import time
from datetime import datetime, timedelta
from enum import Enum
from typing import Dict, List, Optional, Any, Set, Tuple, Callable
from dataclasses import dataclass, field
from uuid import uuid4
from concurrent.futures import ThreadPoolExecutor, Future, as_completed
from queue import Queue, Empty, PriorityQueue

from ..models import (
    WorkflowPlan, AgentType, AgentTask, AgentResult, AgentAssignment,
    TaskDependency, OrchestrationPattern, TaskStatus, ProcessStatus,
    ClarifiedRequest, WorkflowMatch, ValidationResult, TaskInput, TaskContext,
    TaskPriority, Checkpoint, WorkflowState, AgentError, RecoveryAction
)
from ..interfaces.cli_interface import CLIInterface
from ..engine.workflow_engine import WorkflowEngine
from ..engine.agent_pool import EnhancedAgentPool
from ..exceptions.orchestration import (
    OrchestrationError, WorkflowExecutionError, AgentCoordinationError,
    TaskDistributionError, ExecutionTimeoutError
)
from ..utils.logging import get_logger


class ExecutionState(Enum):
    """States of workflow execution"""
    PENDING = "pending"
    INITIALIZING = "initializing"
    RUNNING = "running"
    PAUSED = "paused"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class TaskPriorityLevel(Enum):
    """Task priority levels for orchestrator"""
    LOW = 1
    NORMAL = 2
    HIGH = 3
    CRITICAL = 4


@dataclass
class SimpleValidationResult:
    """Simple validation result for orchestrator"""
    is_valid: bool
    error_message: str = ""


@dataclass
class ExecutionContext:
    """Context for workflow execution"""
    workflow_id: str
    execution_id: str = field(default_factory=lambda: str(uuid4()))
    state: ExecutionState = ExecutionState.PENDING
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    current_step: int = 0
    total_steps: int = 0
    progress_percentage: float = 0.0
    error_message: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class TaskExecution:
    """Represents a task being executed"""
    task_id: str
    agent_id: str
    agent_type: AgentType
    task: AgentTask
    dependencies: Set[str] = field(default_factory=set)
    priority: TaskPriorityLevel = TaskPriorityLevel.NORMAL
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    status: TaskStatus = TaskStatus.PENDING
    result: Optional[AgentResult] = None
    retry_count: int = 0
    max_retries: int = 3
    
    def __lt__(self, other):
        """For priority queue ordering"""
        return self.priority.value > other.priority.value


@dataclass
class WorkflowExecution:
    """Represents a complete workflow execution"""
    workflow_plan: WorkflowPlan
    context: ExecutionContext
    task_executions: Dict[str, TaskExecution] = field(default_factory=dict)
    completed_tasks: Set[str] = field(default_factory=set)
    failed_tasks: Set[str] = field(default_factory=set)
    active_tasks: Set[str] = field(default_factory=set)
    pending_tasks: Set[str] = field(default_factory=set)
    task_results: Dict[str, AgentResult] = field(default_factory=dict)


class Orchestrator:
    """
    Orchestrator for managing multi-agent workflow execution
    
    This class coordinates the execution of workflows across multiple agent instances,
    manages task distribution, monitors progress, and handles failure recovery.
    """
    
    def __init__(
        self,
        cli_interface: CLIInterface,
        workflow_engine: WorkflowEngine,
        agent_pool: Any,  # EnhancedAgentPool or List[EnhancedAgentPool]
        max_concurrent_workflows: int = 10,
        task_timeout_minutes: int = 30,
        heartbeat_interval_seconds: int = 30
    ):
        """
        Initialize the Orchestrator
        
        Args:
            cli_interface: CLI interface for agent process management
            workflow_engine: Workflow engine for plan generation
            agent_pool: Agent pool(s) for resource management
            max_concurrent_workflows: Maximum concurrent workflow executions
            task_timeout_minutes: Default task timeout in minutes
            heartbeat_interval_seconds: Heartbeat interval for monitoring
        """
        self.logger = get_logger(__name__)
        self.cli_interface = cli_interface
        self.workflow_engine = workflow_engine
        
        # Handle single or multiple agent pools
        self.agent_pools: Dict[AgentType, EnhancedAgentPool] = {}
        if isinstance(agent_pool, list):
            for pool in agent_pool:
                self.agent_pools[pool.role_type] = pool
        elif hasattr(agent_pool, 'role_type'):
            self.agent_pools[agent_pool.role_type] = agent_pool
        elif isinstance(agent_pool, dict):
            self.agent_pools = agent_pool
        
        # Keep a reference to a default pool if needed (e.g. implementation)
        self.agent_pool = self.agent_pools.get(AgentType.IMPLEMENTATION) or next(iter(self.agent_pools.values())) if self.agent_pools else None
        
        self.max_concurrent_workflows = max_concurrent_workflows
        self.task_timeout_minutes = task_timeout_minutes
        self.heartbeat_interval_seconds = heartbeat_interval_seconds
        
        # Execution management
        self.active_executions: Dict[str, WorkflowExecution] = {}
        self.execution_history: List[WorkflowExecution] = []
        self.task_queue: PriorityQueue = PriorityQueue()
        self.result_callbacks: Dict[str, List[Callable]] = {}
        
        # Monitoring and coordination
        self.executor = ThreadPoolExecutor(max_workers=max_concurrent_workflows * 2)
        self.monitoring_active = True
        self.coordination_lock = threading.RLock()
        
        # Performance metrics
        self.execution_metrics: Dict[str, Any] = {
            "total_executions": 0,
            "successful_executions": 0,
            "failed_executions": 0,
            "average_execution_time": 0.0,
            "task_success_rate": 0.0
        }
        
        # Start monitoring threads
        self._start_monitoring()
        
        self.logger.info("Orchestrator initialized successfully")
    
    def execute_workflow(
        self,
        request: ClarifiedRequest,
        workflow_plan: Optional[WorkflowPlan] = None,
        execution_callbacks: Optional[List[Callable]] = None
    ) -> str:
        """
        Execute a workflow based on a request or existing plan
        
        Args:
            request: Clarified user request
            workflow_plan: Pre-generated workflow plan (optional)
            execution_callbacks: Callbacks for execution events
            
        Returns:
            Execution ID for tracking
            
        Raises:
            OrchestrationError: If execution cannot be started
        """
        try:
            # Generate workflow plan if not provided
            if workflow_plan is None:
                workflow_matches = self.workflow_engine.evaluate_request(request)
                if not workflow_matches:
                    raise OrchestrationError("No suitable workflow found for request")
                
                # Select optimal workflow
                workflow_plan = self.workflow_engine.select_optimal_workflow(workflow_matches)
            
            # Validate workflow plan
            validation_result = self._validate_workflow_plan(workflow_plan)
            if not validation_result.is_valid:
                raise OrchestrationError(f"Invalid workflow plan: {validation_result.error_message}")
            
            # Check capacity
            if len(self.active_executions) >= self.max_concurrent_workflows:
                raise OrchestrationError("Maximum concurrent workflows reached")
            
            # Create execution context
            execution_context = ExecutionContext(
                workflow_id=workflow_plan.id,
                state=ExecutionState.INITIALIZING,
                total_steps=len(workflow_plan.agents)
            )
            
            # Create workflow execution
            workflow_execution = WorkflowExecution(
                workflow_plan=workflow_plan,
                context=execution_context
            )
            
            # Initialize task executions
            self._initialize_task_executions(workflow_execution)
            
            # Register execution
            with self.coordination_lock:
                self.active_executions[execution_context.execution_id] = workflow_execution
            
            # Register callbacks
            if execution_callbacks:
                self.result_callbacks[execution_context.execution_id] = execution_callbacks
            
            # Start execution asynchronously
            self.executor.submit(self._execute_workflow_async, workflow_execution)
            
            self.logger.info(f"Started workflow execution {execution_context.execution_id}")
            return execution_context.execution_id
            
        except Exception as e:
            self.logger.error(f"Failed to start workflow execution: {e}")
            raise OrchestrationError(f"Failed to start workflow execution: {str(e)}") from e
    
    def get_execution_status(self, execution_id: str) -> Optional[Dict[str, Any]]:
        """
        Get the current status of a workflow execution
        
        Args:
            execution_id: ID of the execution to check
            
        Returns:
            Status information dictionary or None if not found
        """
        with self.coordination_lock:
            if execution_id in self.active_executions:
                execution = self.active_executions[execution_id]
                return self._build_status_dict(execution)
            
            # Check execution history
            for execution in self.execution_history:
                if execution.context.execution_id == execution_id:
                    return self._build_status_dict(execution)
        
        return None
    
    def pause_execution(self, execution_id: str) -> bool:
        """
        Pause a running workflow execution
        
        Args:
            execution_id: ID of the execution to pause
            
        Returns:
            True if paused successfully, False otherwise
        """
        with self.coordination_lock:
            if execution_id not in self.active_executions:
                return False
            
            execution = self.active_executions[execution_id]
            if execution.context.state == ExecutionState.RUNNING:
                execution.context.state = ExecutionState.PAUSED
                self.logger.info(f"Paused workflow execution {execution_id}")
                return True
        
        return False
    
    def resume_execution(self, execution_id: str) -> bool:
        """
        Resume a paused workflow execution
        
        Args:
            execution_id: ID of the execution to resume
            
        Returns:
            True if resumed successfully, False otherwise
        """
        with self.coordination_lock:
            if execution_id not in self.active_executions:
                return False
            
            execution = self.active_executions[execution_id]
            if execution.context.state == ExecutionState.PAUSED:
                execution.context.state = ExecutionState.RUNNING
                self.logger.info(f"Resumed workflow execution {execution_id}")
                return True
        
        return False
    
    def cancel_execution(self, execution_id: str) -> bool:
        """
        Cancel a workflow execution
        
        Args:
            execution_id: ID of the execution to cancel
            
        Returns:
            True if cancelled successfully, False otherwise
        """
        with self.coordination_lock:
            if execution_id not in self.active_executions:
                return False
            
            execution = self.active_executions[execution_id]
            execution.context.state = ExecutionState.CANCELLED
            execution.context.end_time = datetime.now()
            
            # Cancel active tasks
            for task_id in execution.active_tasks.copy():
                self._cancel_task(execution, task_id)
            
            # Move to history
            self.execution_history.append(execution)
            del self.active_executions[execution_id]
            
            self.logger.info(f"Cancelled workflow execution {execution_id}")
            return True
    
    def get_active_executions(self) -> List[Dict[str, Any]]:
        """
        Get status of all active workflow executions
        
        Returns:
            List of execution status dictionaries
        """
        with self.coordination_lock:
            return [
                self._build_status_dict(execution)
                for execution in self.active_executions.values()
            ]
    
    def get_execution_metrics(self) -> Dict[str, Any]:
        """
        Get orchestrator performance metrics
        
        Returns:
            Dictionary containing performance metrics
        """
        return self.execution_metrics.copy()
    
    def rollback_execution(
        self,
        execution_id: str,
        checkpoint_id: Optional[str] = None
    ) -> bool:
        """
        Rollback a workflow execution to a previous checkpoint
        
        Args:
            execution_id: ID of the execution to rollback
            checkpoint_id: ID of checkpoint to rollback to (None for latest)
            
        Returns:
            True if rollback succeeded, False otherwise
        """
        with self.coordination_lock:
            if execution_id not in self.active_executions:
                self.logger.error(f"Execution {execution_id} not found")
                return False
            
            execution = self.active_executions[execution_id]
            
            # Pause execution during rollback
            original_state = execution.context.state
            execution.context.state = ExecutionState.PAUSED
            
            try:
                success = self._rollback_to_checkpoint(execution, checkpoint_id)
                
                if success:
                    # Resume execution
                    execution.context.state = ExecutionState.RUNNING
                    self.logger.info(f"Execution {execution_id} rolled back and resumed")
                else:
                    # Restore original state
                    execution.context.state = original_state
                    self.logger.error(f"Rollback failed for execution {execution_id}")
                
                return success
                
            except Exception as e:
                self.logger.error(f"Rollback error: {e}")
                execution.context.state = original_state
                return False
    
    def get_execution_checkpoints(self, execution_id: str) -> List[Dict[str, Any]]:
        """
        Get all checkpoints for a workflow execution
        
        Args:
            execution_id: ID of the execution
            
        Returns:
            List of checkpoint information dictionaries
        """
        with self.coordination_lock:
            if execution_id in self.active_executions:
                execution = self.active_executions[execution_id]
                return execution.context.metadata.get("checkpoints", [])
            
            # Check execution history
            for execution in self.execution_history:
                if execution.context.execution_id == execution_id:
                    return execution.context.metadata.get("checkpoints", [])
        
        return []
    
    def get_critical_failures(self, execution_id: str) -> List[Dict[str, Any]]:
        """
        Get all critical failures for a workflow execution
        
        Args:
            execution_id: ID of the execution
            
        Returns:
            List of critical failure notifications
        """
        with self.coordination_lock:
            if execution_id in self.active_executions:
                execution = self.active_executions[execution_id]
                return execution.context.metadata.get("critical_failures", [])
            
            # Check execution history
            for execution in self.execution_history:
                if execution.context.execution_id == execution_id:
                    return execution.context.metadata.get("critical_failures", [])
        
        return []
    
    def get_partial_results(self, execution_id: str) -> Dict[str, Any]:
        """
        Get preserved partial results for a workflow execution
        
        Args:
            execution_id: ID of the execution
            
        Returns:
            Dictionary of partial results by task ID
        """
        with self.coordination_lock:
            if execution_id in self.active_executions:
                execution = self.active_executions[execution_id]
                return execution.context.metadata.get("partial_results", {})
            
            # Check execution history
            for execution in self.execution_history:
                if execution.context.execution_id == execution_id:
                    return execution.context.metadata.get("partial_results", {})
        
        return {}
    
    def cleanup(self):
        """Clean up orchestrator resources"""
        self.monitoring_active = False
        
        # Cancel all active executions
        execution_ids = list(self.active_executions.keys())
        for execution_id in execution_ids:
            self.cancel_execution(execution_id)
        
        # Shutdown executor
        self.executor.shutdown(wait=True)
        
        self.logger.info("Orchestrator cleanup completed")
    
    # Private methods
    
    def _validate_workflow_plan(self, workflow_plan: WorkflowPlan) -> SimpleValidationResult:
        """Validate a workflow plan before execution"""
        try:
            # Check required fields
            if not workflow_plan.id:
                return SimpleValidationResult(False, "Missing workflow ID")
            
            if not workflow_plan.agents:
                return SimpleValidationResult(False, "No agent assignments found")
            
            # Validate agent assignments
            for assignment in workflow_plan.agents:
                if not assignment.agent_type:
                    return SimpleValidationResult(False, "Missing agent type in assignment")
            
            return SimpleValidationResult(True, "Workflow plan is valid")
            
        except Exception as e:
            return SimpleValidationResult(False, f"Validation error: {str(e)}")
    
    def _initialize_task_executions(self, workflow_execution: WorkflowExecution):
        """Initialize task executions from workflow plan"""
        # For now, create a simple task for each agent assignment
        # This can be enhanced when the task structure is more defined
        for i, assignment in enumerate(workflow_execution.workflow_plan.agents):
            task_id = f"task-{assignment.agent_type.value}-{i}"
            task = AgentTask(
                id=task_id,
                type=assignment.agent_type.value,
                input=TaskInput(data={}),
                context=TaskContext(
                    workflow_id=workflow_execution.workflow_plan.id,
                    phase="execution"
                ),
                priority=TaskPriority.MEDIUM
            )
            
            task_execution = TaskExecution(
                task_id=task.id,
                agent_id="",  # Will be assigned during execution
                agent_type=assignment.agent_type,
                task=task,
                priority=self._determine_task_priority(task),
                dependencies=set()  # No dependencies for now
            )
            
            workflow_execution.task_executions[task.id] = task_execution
            workflow_execution.pending_tasks.add(task.id)
    
    def _determine_task_priority(self, task: AgentTask) -> TaskPriorityLevel:
        """Determine task priority based on task characteristics"""
        # Simple priority logic - can be enhanced
        if task.type and ("critical" in task.type.lower() or "urgent" in task.type.lower()):
            return TaskPriorityLevel.CRITICAL
        elif task.type and ("important" in task.type.lower() or "high" in task.type.lower()):
            return TaskPriorityLevel.HIGH
        else:
            return TaskPriorityLevel.NORMAL
    
    def _execute_workflow_async(self, workflow_execution: WorkflowExecution):
        """Execute workflow asynchronously"""
        try:
            execution_id = workflow_execution.context.execution_id
            self.logger.info(f"Starting async execution of workflow {execution_id}")
            
            # Update state
            workflow_execution.context.state = ExecutionState.RUNNING
            workflow_execution.context.start_time = datetime.now()
            
            # Create initial checkpoint
            self._create_checkpoint(
                workflow_execution,
                "workflow_started",
                "Initial checkpoint at workflow start"
            )
            
            # Execute based on orchestration pattern
            pattern = workflow_execution.workflow_plan.pattern
            
            if pattern == OrchestrationPattern.SEQUENTIAL_HANDOFF:
                self._execute_sequential_workflow(workflow_execution)
            elif pattern == OrchestrationPattern.PARALLEL_EXECUTION:
                self._execute_parallel_workflow(workflow_execution)
            elif pattern == OrchestrationPattern.DYNAMIC_ROUTING:
                self._execute_dynamic_workflow(workflow_execution)
            else:
                raise WorkflowExecutionError(f"Unsupported orchestration pattern: {pattern}")
            
            # Create final checkpoint
            self._create_checkpoint(
                workflow_execution,
                "workflow_completed",
                "Final checkpoint at workflow completion"
            )
            
            # Mark as completed
            workflow_execution.context.state = ExecutionState.COMPLETED
            workflow_execution.context.end_time = datetime.now()
            workflow_execution.context.progress_percentage = 100.0
            
            self._update_metrics(workflow_execution, success=True)
            self._notify_callbacks(workflow_execution)
            
            self.logger.info(f"Completed workflow execution {execution_id}")
            
        except Exception as e:
            self.logger.error(f"Workflow execution failed: {e}")
            workflow_execution.context.state = ExecutionState.FAILED
            workflow_execution.context.end_time = datetime.now()
            workflow_execution.context.error_message = str(e)
            
            # Create failure checkpoint
            try:
                self._create_checkpoint(
                    workflow_execution,
                    "workflow_failed",
                    f"Checkpoint at workflow failure: {str(e)}"
                )
            except Exception as checkpoint_error:
                self.logger.error(f"Failed to create failure checkpoint: {checkpoint_error}")
            
            self._update_metrics(workflow_execution, success=False)
            self._notify_callbacks(workflow_execution)
        
        finally:
            # Move to history
            with self.coordination_lock:
                if execution_id in self.active_executions:
                    self.execution_history.append(workflow_execution)
                    del self.active_executions[execution_id]
    
    def _execute_sequential_workflow(self, workflow_execution: WorkflowExecution):
        """Execute workflow with sequential handoff pattern"""
        while workflow_execution.pending_tasks:
            # Find tasks with no pending dependencies
            ready_tasks = []
            for task_id in workflow_execution.pending_tasks:
                task_execution = workflow_execution.task_executions[task_id]
                if not task_execution.dependencies or task_execution.dependencies.issubset(workflow_execution.completed_tasks):
                    ready_tasks.append(task_id)
            
            if not ready_tasks:
                # Check for circular dependencies or other issues
                if workflow_execution.active_tasks:
                    # Wait for active tasks to complete
                    time.sleep(1)
                    continue
                else:
                    raise WorkflowExecutionError("No ready tasks found - possible circular dependency")
            
            # Execute one task at a time for sequential pattern
            task_id = ready_tasks[0]
            self._execute_task(workflow_execution, task_id)
            
            # Update progress
            self._update_progress(workflow_execution)
    
    def _execute_parallel_workflow(self, workflow_execution: WorkflowExecution):
        """Execute workflow with parallel execution pattern"""
        futures = []
        
        while workflow_execution.pending_tasks or workflow_execution.active_tasks:
            # Find tasks with no pending dependencies
            ready_tasks = []
            for task_id in workflow_execution.pending_tasks:
                task_execution = workflow_execution.task_executions[task_id]
                if not task_execution.dependencies or task_execution.dependencies.issubset(workflow_execution.completed_tasks):
                    ready_tasks.append(task_id)
            
            # Start ready tasks in parallel
            for task_id in ready_tasks:
                future = self.executor.submit(self._execute_task, workflow_execution, task_id)
                futures.append(future)
                workflow_execution.pending_tasks.remove(task_id)
                workflow_execution.active_tasks.add(task_id)
            
            # Wait for some tasks to complete
            if futures:
                # Wait for at least one task to complete
                completed_futures = []
                for future in as_completed(futures, timeout=1):
                    completed_futures.append(future)
                    break
                
                # Remove completed futures
                for future in completed_futures:
                    futures.remove(future)
            
            # Update progress
            self._update_progress(workflow_execution)
            
            # Small delay to prevent busy waiting
            time.sleep(0.1)
    
    def _execute_dynamic_workflow(self, workflow_execution: WorkflowExecution):
        """Execute workflow with dynamic routing pattern"""
        # For now, use parallel execution with dynamic task selection
        # This can be enhanced with more sophisticated routing logic
        self._execute_parallel_workflow(workflow_execution)
    
    def _execute_task(self, workflow_execution: WorkflowExecution, task_id: str):
        """Execute a single task"""
        task_execution = workflow_execution.task_executions[task_id]
        
        try:
            # Check if execution is paused or cancelled
            if workflow_execution.context.state in [ExecutionState.PAUSED, ExecutionState.CANCELLED]:
                return
            
            # Get available agent from correct pool
            pool = self.agent_pools.get(task_execution.agent_type)
            if not pool:
                raise TaskDistributionError(f"No agent pool found for type {task_execution.agent_type}")
                
            agent_instance = pool.assign_task(task_execution.task)
            if not agent_instance:
                raise TaskDistributionError(f"No available agent for type {task_execution.agent_type}")
            
            task_execution.agent_id = agent_instance.instance_id
            task_execution.start_time = datetime.now()
            task_execution.status = TaskStatus.IN_PROGRESS
            
            # Send task to agent
            future = self.cli_interface.send_task(agent_instance.instance_id, task_execution.task)
            
            # Wait for result with timeout
            timeout_seconds = self.task_timeout_minutes * 60
            result = future.result(timeout=timeout_seconds)
            
            # Process result
            task_execution.result = result
            task_execution.end_time = datetime.now()
            task_execution.status = TaskStatus.COMPLETED
            
            # Update workflow state
            with self.coordination_lock:
                workflow_execution.active_tasks.discard(task_id)
                workflow_execution.completed_tasks.add(task_id)
                workflow_execution.task_results[task_id] = result
            
            # Release agent back to pool
            pool.complete_task(
                agent_instance.instance_id, 
                success=True,
                execution_time=(task_execution.end_time - task_execution.start_time).total_seconds(),
                quality_score=getattr(result, 'quality_score', 1.0)
            )
            
            # Create checkpoint after task completion
            if len(workflow_execution.completed_tasks) % 3 == 0:  # Checkpoint every 3 tasks
                self._create_checkpoint(
                    workflow_execution,
                    f"task_{task_id}_completed",
                    f"Checkpoint after completing task {task_id}"
                )
            
            self.logger.debug(f"Task {task_id} completed successfully")
            
        except Exception as e:
            self.logger.error(f"Task {task_id} failed: {e}, type: {type(e)}")
            import traceback
            self.logger.error(traceback.format_exc())
            
            task_execution.end_time = datetime.now()
            task_execution.status = TaskStatus.FAILED
            
            # Handle failure with recovery logic
            recovery_action = self._handle_task_failure(workflow_execution, task_id, e)
            
            # Apply recovery action
            self._apply_recovery_action(workflow_execution, task_id, recovery_action)
            
            # If recovery action is abort, raise exception to stop workflow
            if recovery_action.action_type == "abort":
                raise WorkflowExecutionError(
                    f"Task {task_id} failed after {task_execution.max_retries} retries "
                    f"and could not be recovered: {str(e)}"
                )
    
    def _cancel_task(self, workflow_execution: WorkflowExecution, task_id: str):
        """Cancel a specific task"""
        task_execution = workflow_execution.task_executions[task_id]
        task_execution.status = TaskStatus.CANCELLED
        task_execution.end_time = datetime.now()
        
        # Release agent if assigned
        if task_execution.agent_id:
            try:
                pool = self.agent_pools.get(task_execution.agent_type)
                if pool:
                    pool.complete_task(
                        instance_id=task_execution.agent_id, 
                        success=False
                    )
            except Exception:
                pass
        
        # Update workflow state
        workflow_execution.active_tasks.discard(task_id)
        workflow_execution.pending_tasks.discard(task_id)
    
    def _update_progress(self, workflow_execution: WorkflowExecution):
        """Update workflow execution progress"""
        total_tasks = len(workflow_execution.task_executions)
        completed_tasks = len(workflow_execution.completed_tasks)
        
        if total_tasks > 0:
            workflow_execution.context.progress_percentage = (completed_tasks / total_tasks) * 100.0
            workflow_execution.context.current_step = completed_tasks
    
    def _build_status_dict(self, workflow_execution: WorkflowExecution) -> Dict[str, Any]:
        """Build status dictionary for a workflow execution"""
        return {
            "execution_id": workflow_execution.context.execution_id,
            "workflow_id": workflow_execution.context.workflow_id,
            "state": workflow_execution.context.state.value,
            "start_time": workflow_execution.context.start_time.isoformat() if workflow_execution.context.start_time else None,
            "end_time": workflow_execution.context.end_time.isoformat() if workflow_execution.context.end_time else None,
            "progress_percentage": workflow_execution.context.progress_percentage,
            "current_step": workflow_execution.context.current_step,
            "total_steps": workflow_execution.context.total_steps,
            "completed_tasks": len(workflow_execution.completed_tasks),
            "active_tasks": len(workflow_execution.active_tasks),
            "pending_tasks": len(workflow_execution.pending_tasks),
            "failed_tasks": len(workflow_execution.failed_tasks),
            "error_message": workflow_execution.context.error_message,
            "metadata": workflow_execution.context.metadata
        }
    
    def _update_metrics(self, workflow_execution: WorkflowExecution, success: bool):
        """Update orchestrator performance metrics"""
        self.execution_metrics["total_executions"] += 1
        
        if success:
            self.execution_metrics["successful_executions"] += 1
        else:
            self.execution_metrics["failed_executions"] += 1
        
        # Update average execution time
        if workflow_execution.context.start_time and workflow_execution.context.end_time:
            execution_time = (workflow_execution.context.end_time - workflow_execution.context.start_time).total_seconds()
            current_avg = self.execution_metrics["average_execution_time"]
            total_executions = self.execution_metrics["total_executions"]
            
            # Calculate new average
            self.execution_metrics["average_execution_time"] = (
                (current_avg * (total_executions - 1) + execution_time) / total_executions
            )
        
        # Update task success rate
        total_tasks = len(workflow_execution.task_executions)
        successful_tasks = len(workflow_execution.completed_tasks)
        
        if total_tasks > 0:
            task_success_rate = successful_tasks / total_tasks
            current_rate = self.execution_metrics["task_success_rate"]
            
            # Update with exponential moving average
            alpha = 0.1
            self.execution_metrics["task_success_rate"] = (
                alpha * task_success_rate + (1 - alpha) * current_rate
            )
    
    def _notify_callbacks(self, workflow_execution: WorkflowExecution):
        """Notify registered callbacks about execution completion"""
        execution_id = workflow_execution.context.execution_id
        
        if execution_id in self.result_callbacks:
            for callback in self.result_callbacks[execution_id]:
                try:
                    callback(workflow_execution)
                except Exception as e:
                    self.logger.error(f"Callback error for execution {execution_id}: {e}")
            
            # Clean up callbacks
            del self.result_callbacks[execution_id]
    
    # Failure Handling and Recovery Methods (Requirement 3.4, 10.5)
    
    def _handle_task_failure(
        self,
        workflow_execution: WorkflowExecution,
        task_id: str,
        error: Exception
    ) -> RecoveryAction:
        """
        Handle task failure with exponential backoff retry logic
        
        Requirements: 3.4, 10.5
        
        Args:
            workflow_execution: The workflow execution context
            task_id: ID of the failed task
            error: The exception that caused the failure
            
        Returns:
            RecoveryAction indicating how to proceed
        """
        task_execution = workflow_execution.task_executions[task_id]
        
        self.logger.warning(
            f"Task {task_id} failed (attempt {task_execution.retry_count + 1}/{task_execution.max_retries}): {error}"
        )
        
        # Create agent error record
        agent_error = AgentError(
            agent_id=task_execution.agent_id or "unknown",
            error_type=type(error).__name__,
            error_message=str(error),
            timestamp=datetime.now(),
            context={
                "task_id": task_id,
                "workflow_id": workflow_execution.workflow_plan.id,
                "execution_id": workflow_execution.context.execution_id,
                "retry_count": task_execution.retry_count
            },
            is_recoverable=task_execution.retry_count < task_execution.max_retries,
            retry_count=task_execution.retry_count
        )
        
        # Preserve partial results if available
        if task_execution.result:
            self._preserve_partial_result(workflow_execution, task_id, task_execution.result)
        
        # Determine recovery action
        if task_execution.retry_count < task_execution.max_retries:
            # Retry with exponential backoff
            delay_seconds = self._calculate_backoff_delay(task_execution.retry_count)
            
            recovery_action = RecoveryAction(
                action_type="retry",
                target_agent=None,  # Will try same agent type
                parameters={
                    "delay_seconds": delay_seconds,
                    "retry_count": task_execution.retry_count + 1
                },
                max_attempts=task_execution.max_retries,
                delay_seconds=delay_seconds
            )
            
            self.logger.info(
                f"Will retry task {task_id} after {delay_seconds} seconds "
                f"(attempt {task_execution.retry_count + 1}/{task_execution.max_retries})"
            )
            
            return recovery_action
        else:
            # Try reassignment to backup agent
            if self._can_reassign_task(workflow_execution, task_id):
                recovery_action = RecoveryAction(
                    action_type="reassign",
                    target_agent=None,  # Will be determined by agent pool
                    parameters={
                        "original_agent": task_execution.agent_id,
                        "task_id": task_id
                    },
                    max_attempts=1,
                    delay_seconds=0
                )
                
                self.logger.info(f"Will reassign task {task_id} to backup agent")
                return recovery_action
            else:
                # Critical failure - notify user
                self._notify_critical_failure(workflow_execution, task_id, agent_error)
                
                recovery_action = RecoveryAction(
                    action_type="abort",
                    target_agent=None,
                    parameters={
                        "error": str(error),
                        "task_id": task_id
                    },
                    max_attempts=0,
                    delay_seconds=0
                )
                
                return recovery_action
    
    def _calculate_backoff_delay(self, retry_count: int) -> int:
        """
        Calculate exponential backoff delay in seconds
        
        Args:
            retry_count: Current retry attempt number
            
        Returns:
            Delay in seconds
        """
        # Exponential backoff: 2^retry_count seconds, capped at 60 seconds
        base_delay = 2
        max_delay = 60
        delay = min(base_delay ** retry_count, max_delay)
        return delay
    
    def _can_reassign_task(self, workflow_execution: WorkflowExecution, task_id: str) -> bool:
        """
        Check if a task can be reassigned to a backup agent
        
        Args:
            workflow_execution: The workflow execution context
            task_id: ID of the task to check
            
        Returns:
            True if reassignment is possible, False otherwise
        """
        task_execution = workflow_execution.task_executions[task_id]
        
        # Check if agent pool has available instances of the same type
        try:
            pool = self.agent_pools.get(task_execution.agent_type)
            if not pool:
                return False
                
            # Get pool status to check for available instances
            pool_status = pool.get_pool_status()
            idle_instances = pool_status.get("idle_instances", 0)
            
            # Need at least one idle instance (excluding the failed one)
            return idle_instances > 0
        except Exception as e:
            self.logger.error(f"Error checking agent availability: {e}")
            return False
    
    def _reassign_task(
        self,
        workflow_execution: WorkflowExecution,
        task_id: str
    ) -> bool:
        """
        Reassign a failed task to a backup agent
        
        Args:
            workflow_execution: The workflow execution context
            task_id: ID of the task to reassign
            
        Returns:
            True if reassignment succeeded, False otherwise
        """
        task_execution = workflow_execution.task_executions[task_id]
        original_agent_id = task_execution.agent_id
        
        try:
            self.logger.info(f"Reassigning task {task_id} from agent {original_agent_id}")
            
            pool = self.agent_pools.get(task_execution.agent_type)
            if not pool:
                self.logger.error(f"No agent pool for type {task_execution.agent_type}")
                return False
            
            # Release the failed agent
            if original_agent_id:
                try:
                    pool.complete_task(
                        instance_id=original_agent_id,
                        success=False
                    )
                except Exception as e:
                    self.logger.warning(f"Error releasing failed agent: {e}")
            
            # Get a new agent instance
            agent_instance = pool.assign_task(task_execution.task)
            if not agent_instance:
                self.logger.error(f"No backup agent available for task {task_id}")
                return False
            
            # Update task execution
            task_execution.agent_id = agent_instance.instance_id
            task_execution.status = TaskStatus.PENDING
            task_execution.start_time = None
            task_execution.end_time = None
            task_execution.retry_count = 0  # Reset retry count for new agent
            
            # Add back to pending tasks
            with self.coordination_lock:
                workflow_execution.active_tasks.discard(task_id)
                workflow_execution.pending_tasks.add(task_id)
            
            self.logger.info(f"Task {task_id} reassigned to agent {agent_instance.instance_id}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to reassign task {task_id}: {e}")
            return False
    
    def _preserve_partial_result(
        self,
        workflow_execution: WorkflowExecution,
        task_id: str,
        partial_result: AgentResult
    ):
        """
        Preserve partial results from a failed task
        
        Args:
            workflow_execution: The workflow execution context
            task_id: ID of the task
            partial_result: Partial result to preserve
        """
        # Store partial result in workflow metadata
        if "partial_results" not in workflow_execution.context.metadata:
            workflow_execution.context.metadata["partial_results"] = {}
        
        workflow_execution.context.metadata["partial_results"][task_id] = {
            "result": partial_result.to_dict(),
            "preserved_at": datetime.now().isoformat(),
            "reason": "task_failure"
        }
        
        self.logger.info(f"Preserved partial result for task {task_id}")
    
    def _notify_critical_failure(
        self,
        workflow_execution: WorkflowExecution,
        task_id: str,
        error: AgentError
    ):
        """
        Notify user of critical failure that cannot be automatically recovered
        
        Args:
            workflow_execution: The workflow execution context
            task_id: ID of the failed task
            error: The agent error information
        """
        notification = {
            "type": "critical_failure",
            "execution_id": workflow_execution.context.execution_id,
            "workflow_id": workflow_execution.workflow_plan.id,
            "task_id": task_id,
            "error_type": error.error_type,
            "error_message": error.error_message,
            "timestamp": error.timestamp.isoformat(),
            "retry_count": error.retry_count,
            "options": [
                "abort_workflow",
                "skip_task",
                "manual_intervention"
            ]
        }
        
        # Store notification in workflow metadata
        if "critical_failures" not in workflow_execution.context.metadata:
            workflow_execution.context.metadata["critical_failures"] = []
        
        workflow_execution.context.metadata["critical_failures"].append(notification)
        
        self.logger.critical(
            f"Critical failure in workflow {workflow_execution.context.execution_id}: "
            f"Task {task_id} failed after {error.retry_count} retries. "
            f"Error: {error.error_message}"
        )
    
    def _create_checkpoint(
        self,
        workflow_execution: WorkflowExecution,
        phase: str,
        description: str = ""
    ) -> Checkpoint:
        """
        Create a checkpoint for workflow state
        
        Args:
            workflow_execution: The workflow execution context
            phase: Current phase name
            description: Optional description
            
        Returns:
            Created checkpoint
        """
        # Create workflow state snapshot
        workflow_state = WorkflowState(
            execution_id=workflow_execution.context.execution_id,
            current_phase=phase,
            completed_phases=workflow_execution.context.metadata.get("completed_phases", []),
            agent_states={},  # Would be populated with actual agent states
            shared_context=None,  # Would be populated with shared context
            checkpoints=[],  # Previous checkpoints
            last_updated=datetime.now(),
            metadata={
                "progress": workflow_execution.context.progress_percentage,
                "completed_tasks": len(workflow_execution.completed_tasks),
                "active_tasks": len(workflow_execution.active_tasks),
                "pending_tasks": len(workflow_execution.pending_tasks)
            }
        )
        
        checkpoint = Checkpoint(
            timestamp=datetime.now(),
            phase=phase,
            state=workflow_state,
            description=description or f"Checkpoint at phase: {phase}",
            recoverable=True,
            metadata={
                "execution_id": workflow_execution.context.execution_id,
                "workflow_id": workflow_execution.workflow_plan.id
            }
        )
        
        # Store checkpoint in workflow metadata
        if "checkpoints" not in workflow_execution.context.metadata:
            workflow_execution.context.metadata["checkpoints"] = []
        
        workflow_execution.context.metadata["checkpoints"].append({
            "id": checkpoint.id,
            "timestamp": checkpoint.timestamp.isoformat(),
            "phase": checkpoint.phase,
            "description": checkpoint.description
        })
        
        self.logger.info(
            f"Created checkpoint {checkpoint.id} for workflow "
            f"{workflow_execution.context.execution_id} at phase {phase}"
        )
        
        return checkpoint
    
    def _rollback_to_checkpoint(
        self,
        workflow_execution: WorkflowExecution,
        checkpoint_id: Optional[str] = None
    ) -> bool:
        """
        Rollback workflow to a previous checkpoint
        
        Args:
            workflow_execution: The workflow execution context
            checkpoint_id: ID of checkpoint to rollback to (None for latest)
            
        Returns:
            True if rollback succeeded, False otherwise
        """
        try:
            checkpoints = workflow_execution.context.metadata.get("checkpoints", [])
            
            if not checkpoints:
                self.logger.error("No checkpoints available for rollback")
                return False
            
            # Find target checkpoint
            target_checkpoint = None
            if checkpoint_id:
                target_checkpoint = next(
                    (cp for cp in checkpoints if cp["id"] == checkpoint_id),
                    None
                )
            else:
                # Use latest checkpoint
                target_checkpoint = checkpoints[-1]
            
            if not target_checkpoint:
                self.logger.error(f"Checkpoint {checkpoint_id} not found")
                return False
            
            self.logger.info(
                f"Rolling back workflow {workflow_execution.context.execution_id} "
                f"to checkpoint {target_checkpoint['id']} at phase {target_checkpoint['phase']}"
            )
            
            # Cancel all active tasks
            for task_id in list(workflow_execution.active_tasks):
                self._cancel_task(workflow_execution, task_id)
            
            # Reset workflow state to checkpoint
            workflow_execution.context.current_step = target_checkpoint.get("completed_tasks", 0)
            workflow_execution.context.progress_percentage = target_checkpoint.get("progress", 0.0)
            
            # Mark tasks after checkpoint as pending again
            # This is a simplified version - full implementation would restore exact state
            checkpoint_phase = target_checkpoint["phase"]
            workflow_execution.context.metadata["rollback_info"] = {
                "checkpoint_id": target_checkpoint["id"],
                "rollback_time": datetime.now().isoformat(),
                "target_phase": checkpoint_phase
            }
            
            self.logger.info(f"Rollback to checkpoint {target_checkpoint['id']} completed")
            return True
            
        except Exception as e:
            self.logger.error(f"Rollback failed: {e}")
            return False
    
    def _apply_recovery_action(
        self,
        workflow_execution: WorkflowExecution,
        task_id: str,
        recovery_action: RecoveryAction
    ):
        """
        Apply a recovery action to a failed task
        
        Args:
            workflow_execution: The workflow execution context
            task_id: ID of the task
            recovery_action: Recovery action to apply
        """
        action_type = recovery_action.action_type
        
        if action_type == "retry":
            # Wait for backoff delay
            delay = recovery_action.delay_seconds
            if delay > 0:
                self.logger.info(f"Waiting {delay} seconds before retry")
                time.sleep(delay)
            
            # Task will be retried in the execution loop
            task_execution = workflow_execution.task_executions[task_id]
            task_execution.retry_count += 1
            task_execution.status = TaskStatus.PENDING
            task_execution.start_time = None
            task_execution.end_time = None
            
            with self.coordination_lock:
                workflow_execution.active_tasks.discard(task_id)
                workflow_execution.pending_tasks.add(task_id)
        
        elif action_type == "reassign":
            # Reassign to backup agent
            success = self._reassign_task(workflow_execution, task_id)
            if not success:
                # Reassignment failed, abort
                self.logger.error(f"Task reassignment failed for {task_id}")
                with self.coordination_lock:
                    workflow_execution.failed_tasks.add(task_id)
                    workflow_execution.active_tasks.discard(task_id)
        
        elif action_type == "skip":
            # Skip the failed task
            self.logger.warning(f"Skipping failed task {task_id}")
            with self.coordination_lock:
                workflow_execution.active_tasks.discard(task_id)
                workflow_execution.failed_tasks.add(task_id)
        
        elif action_type == "abort":
            # Abort the entire workflow
            self.logger.error(f"Aborting workflow due to task {task_id} failure")
            workflow_execution.context.state = ExecutionState.FAILED
            workflow_execution.context.error_message = f"Task {task_id} failed and could not be recovered"
            
            # Cancel all remaining tasks
            for tid in list(workflow_execution.active_tasks):
                self._cancel_task(workflow_execution, tid)
            for tid in list(workflow_execution.pending_tasks):
                workflow_execution.pending_tasks.remove(tid)
    
    def _start_monitoring(self):
        """Start monitoring threads"""
        def monitor_executions():
            """Monitor active executions for timeouts and health"""
            while self.monitoring_active:
                try:
                    current_time = datetime.now()
                    
                    with self.coordination_lock:
                        for execution in list(self.active_executions.values()):
                            # Check for execution timeout
                            if execution.context.start_time:
                                execution_duration = current_time - execution.context.start_time
                                max_duration = timedelta(hours=2)  # 2 hour max execution time
                                
                                if execution_duration > max_duration:
                                    self.logger.warning(f"Execution {execution.context.execution_id} timed out")
                                    execution.context.state = ExecutionState.FAILED
                                    execution.context.error_message = "Execution timeout"
                                    execution.context.end_time = current_time
                            
                            # Check task health
                            for task_id in list(execution.active_tasks):
                                task_execution = execution.task_executions[task_id]
                                if task_execution.start_time:
                                    task_duration = current_time - task_execution.start_time
                                    max_task_duration = timedelta(minutes=self.task_timeout_minutes)
                                    
                                    if task_duration > max_task_duration:
                                        self.logger.warning(f"Task {task_id} timed out")
                                        self._cancel_task(execution, task_id)
                    
                    time.sleep(self.heartbeat_interval_seconds)
                    
                except Exception as e:
                    self.logger.error(f"Monitoring error: {e}")
                    time.sleep(5)
        
        monitor_thread = threading.Thread(target=monitor_executions, daemon=True)
        monitor_thread.start()


# Convenience functions

def create_orchestrator(
    cli_interface: CLIInterface,
    workflow_engine: WorkflowEngine,
    agent_pool: EnhancedAgentPool,
    max_workflows: int = 5
) -> Orchestrator:
    """
    Create an orchestrator with common configuration
    
    Args:
        cli_interface: CLI interface for agent management
        workflow_engine: Workflow engine for plan generation
        agent_pool: Agent pool for resource management
        max_workflows: Maximum concurrent workflows
        
    Returns:
        Configured Orchestrator instance
    """
    return Orchestrator(
        cli_interface=cli_interface,
        workflow_engine=workflow_engine,
        agent_pool=agent_pool,
        max_concurrent_workflows=max_workflows,
        task_timeout_minutes=30,
        heartbeat_interval_seconds=30
    )