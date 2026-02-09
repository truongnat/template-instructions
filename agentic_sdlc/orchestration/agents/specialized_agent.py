"""
Specialized Agent Base Class for Multi-Agent Orchestration System

This module implements the SpecializedAgent abstract base class that all specialized
agents (PM, BA, SA, Research, Quality Judge, Implementation) will extend.

Requirements: 5.7, 9.4
"""

import asyncio
import json
import time
from abc import ABC, abstractmethod
from datetime import datetime
from enum import Enum
from typing import Dict, List, Optional, Any, Callable
from dataclasses import dataclass, field
from uuid import uuid4
from queue import PriorityQueue, Empty
from threading import Lock, Thread

from ..models.agent import (
    AgentType, AgentTask, AgentResult, AgentConfig, PerformanceMetrics,
    TaskStatus, TaskPriority, TaskOutput, ResultMetadata, ResourceUsage,
    DataFormat, InstanceStatus
)
from ..exceptions.agent import (
    AgentInitializationError, AgentExecutionError, AgentConfigurationError
)
from ..utils.logging import get_logger


class AgentState(Enum):
    """States of a specialized agent"""
    UNINITIALIZED = "uninitialized"
    INITIALIZING = "initializing"
    READY = "ready"
    BUSY = "busy"
    ERROR = "error"
    SHUTTING_DOWN = "shutting_down"
    TERMINATED = "terminated"


@dataclass
class TaskQueueItem:
    """Item in the task queue with priority"""
    priority: int  # Lower number = higher priority
    timestamp: datetime
    task: AgentTask
    
    def __lt__(self, other):
        """For priority queue ordering"""
        if self.priority != other.priority:
            return self.priority < other.priority
        return self.timestamp < other.timestamp


@dataclass
class AgentStatus:
    """Status information for an agent"""
    instance_id: str
    agent_type: AgentType
    state: AgentState
    current_task: Optional[AgentTask] = None
    queued_tasks: int = 0
    performance: PerformanceMetrics = field(default_factory=PerformanceMetrics)
    last_activity: datetime = field(default_factory=datetime.now)
    error_message: Optional[str] = None
    uptime_seconds: float = 0.0
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization"""
        return {
            "instance_id": self.instance_id,
            "agent_type": self.agent_type.value,
            "state": self.state.value,
            "current_task_id": self.current_task.id if self.current_task else None,
            "queued_tasks": self.queued_tasks,
            "performance": {
                "tasks_completed": self.performance.tasks_completed,
                "average_execution_time": self.performance.average_execution_time,
                "success_rate": self.performance.success_rate,
                "quality_score": self.performance.quality_score,
                "resource_utilization": self.performance.resource_utilization,
                "last_updated": self.performance.last_updated.isoformat()
            },
            "last_activity": self.last_activity.isoformat(),
            "error_message": self.error_message,
            "uptime_seconds": self.uptime_seconds
        }


class SpecializedAgent(ABC):
    """
    Abstract base class for all specialized agents in the orchestration system.
    
    All specialized agents (PM, BA, SA, Research, Quality Judge, Implementation)
    must extend this class and implement the abstract methods.
    
    This class provides:
    - Task queue management with priority handling
    - Performance metrics tracking
    - Lifecycle management (initialize, execute, cleanup)
    - Status reporting
    - Error handling and recovery
    """
    
    def __init__(
        self,
        instance_id: Optional[str] = None,
        config: Optional[AgentConfig] = None
    ):
        """
        Initialize the specialized agent
        
        Args:
            instance_id: Unique identifier for this agent instance
            config: Configuration for the agent
        """
        self.instance_id = instance_id or str(uuid4())
        self.config = config
        self.logger = get_logger(f"{self.__class__.__name__}[{self.instance_id[:8]}]")
        
        # Agent state
        self._state = AgentState.UNINITIALIZED
        self._state_lock = Lock()
        
        # Task management
        self._task_queue: PriorityQueue = PriorityQueue()
        self._current_task: Optional[AgentTask] = None
        self._task_lock = Lock()
        
        # Performance tracking
        self._performance = PerformanceMetrics()
        self._start_time = datetime.now()
        
        # Task processing thread
        self._processing_thread: Optional[Thread] = None
        self._stop_processing = False
        
        # Callbacks
        self._task_callbacks: Dict[str, List[Callable]] = {}
        
        self.logger.info(f"Created {self.agent_type.value} agent instance {self.instance_id}")
    
    @property
    @abstractmethod
    def agent_type(self) -> AgentType:
        """Return the type of this agent"""
        pass
    
    @abstractmethod
    async def _execute_task_impl(self, task: AgentTask) -> AgentResult:
        """
        Execute a task - must be implemented by subclasses
        
        Args:
            task: Task to execute
            
        Returns:
            Result of task execution
            
        Raises:
            AgentExecutionError: If task execution fails
        """
        pass
    
    @abstractmethod
    def _validate_task(self, task: AgentTask) -> bool:
        """
        Validate that a task is appropriate for this agent
        
        Args:
            task: Task to validate
            
        Returns:
            True if task is valid for this agent
        """
        pass
    
    async def initialize(self, config: Optional[AgentConfig] = None) -> None:
        """
        Initialize the agent with configuration
        
        Args:
            config: Configuration for the agent (optional, uses constructor config if not provided)
            
        Raises:
            AgentInitializationError: If initialization fails
        """
        try:
            with self._state_lock:
                if self._state != AgentState.UNINITIALIZED:
                    raise AgentInitializationError(
                        f"Agent already initialized (state: {self._state.value})"
                    )
                
                self._state = AgentState.INITIALIZING
            
            # Update config if provided
            if config:
                self.config = config
            
            # Validate configuration
            if not self.config:
                raise AgentInitializationError("No configuration provided")
            
            if self.config.agent_type != self.agent_type:
                raise AgentInitializationError(
                    f"Config agent type {self.config.agent_type.value} "
                    f"does not match agent type {self.agent_type.value}"
                )
            
            # Perform agent-specific initialization
            await self._initialize_impl()
            
            # Start task processing thread
            self._start_task_processing()
            
            with self._state_lock:
                self._state = AgentState.READY
            
            self.logger.info(f"Agent {self.instance_id} initialized successfully")
            
        except Exception as e:
            with self._state_lock:
                self._state = AgentState.ERROR
            self.logger.error(f"Agent initialization failed: {e}")
            raise AgentInitializationError(f"Failed to initialize agent: {str(e)}") from e
    
    async def _initialize_impl(self) -> None:
        """
        Agent-specific initialization logic - can be overridden by subclasses
        
        Default implementation does nothing.
        """
        pass
    
    def _start_task_processing(self):
        """Start the task processing thread"""
        def process_tasks():
            """Task processing loop"""
            while not self._stop_processing:
                try:
                    # Get next task from queue (with timeout to allow checking stop flag)
                    try:
                        queue_item = self._task_queue.get(timeout=1.0)
                    except Empty:
                        continue
                    
                    # Process the task
                    task = queue_item.task
                    self._process_task(task)
                    
                except Exception as e:
                    self.logger.error(f"Error in task processing loop: {e}")
        
        self._processing_thread = Thread(target=process_tasks, daemon=True)
        self._processing_thread.start()
        self.logger.debug("Started task processing thread")
    
    def _process_task(self, task: AgentTask):
        """
        Process a single task
        
        Args:
            task: Task to process
        """
        try:
            with self._task_lock:
                self._current_task = task
            
            with self._state_lock:
                self._state = AgentState.BUSY
            
            # Mark task as started
            task.start_task()
            
            # Execute the task (run async method in sync context)
            start_time = time.time()
            result = asyncio.run(self._execute_task_impl(task))
            execution_time = time.time() - start_time
            
            # Mark task as completed
            task.complete_task()
            
            # Update performance metrics
            success = result.status == TaskStatus.COMPLETED
            quality = result.metadata.quality_score if result.metadata else 0.0
            self._performance.update_metrics(execution_time, success, quality)
            
            # Invoke callbacks
            self._invoke_callbacks(task.id, result)
            
            self.logger.info(f"Task {task.id} completed in {execution_time:.2f}s")
            
        except Exception as e:
            self.logger.error(f"Task {task.id} failed: {e}")
            
            # Create error result
            result = AgentResult(
                task_id=task.id,
                instance_id=self.instance_id,
                status=TaskStatus.FAILED,
                output=TaskOutput(
                    data={"error": str(e)},
                    format=DataFormat.JSON,
                    confidence=0.0
                ),
                metadata=ResultMetadata(
                    execution_time=time.time() - start_time if 'start_time' in locals() else 0.0
                )
            )
            
            # Update performance metrics
            execution_time = result.metadata.execution_time
            self._performance.update_metrics(execution_time, False, 0.0)
            
            # Invoke callbacks with error result
            self._invoke_callbacks(task.id, result)
            
        finally:
            with self._task_lock:
                self._current_task = None
            
            with self._state_lock:
                self._state = AgentState.READY
    
    async def executeTask(self, task: AgentTask) -> AgentResult:
        """
        Execute a task immediately (synchronous execution)
        
        Args:
            task: Task to execute
            
        Returns:
            Result of task execution
            
        Raises:
            AgentExecutionError: If task execution fails
        """
        try:
            # Validate agent state
            with self._state_lock:
                if self._state not in [AgentState.READY, AgentState.BUSY]:
                    raise AgentExecutionError(
                        f"Agent not ready for task execution (state: {self._state.value})"
                    )
            
            # Validate task
            if not self._validate_task(task):
                raise AgentExecutionError(
                    f"Task {task.id} is not valid for agent type {self.agent_type.value}"
                )
            
            # Mark task as started
            task.start_task()
            
            # Execute the task
            start_time = time.time()
            result = await self._execute_task_impl(task)
            execution_time = time.time() - start_time
            
            # Mark task as completed
            task.complete_task()
            
            # Update performance metrics
            success = result.status == TaskStatus.COMPLETED
            quality = result.metadata.quality_score if result.metadata else 0.0
            self._performance.update_metrics(execution_time, success, quality)
            
            self.logger.info(f"Task {task.id} executed successfully in {execution_time:.2f}s")
            return result
            
        except Exception as e:
            self.logger.error(f"Task execution failed: {e}")
            raise AgentExecutionError(f"Failed to execute task: {str(e)}") from e
    
    def enqueue_task(
        self,
        task: AgentTask,
        callback: Optional[Callable[[AgentResult], None]] = None
    ) -> bool:
        """
        Add a task to the queue for asynchronous execution
        
        Args:
            task: Task to enqueue
            callback: Optional callback to invoke when task completes
            
        Returns:
            True if task was enqueued successfully
            
        Raises:
            AgentExecutionError: If agent is not ready
        """
        try:
            # Validate agent state
            with self._state_lock:
                if self._state not in [AgentState.READY, AgentState.BUSY]:
                    raise AgentExecutionError(
                        f"Agent not ready for task execution (state: {self._state.value})"
                    )
            
            # Validate task
            if not self._validate_task(task):
                raise AgentExecutionError(
                    f"Task {task.id} is not valid for agent type {self.agent_type.value}"
                )
            
            # Register callback if provided
            if callback:
                if task.id not in self._task_callbacks:
                    self._task_callbacks[task.id] = []
                self._task_callbacks[task.id].append(callback)
            
            # Convert task priority to queue priority
            priority = self._get_queue_priority(task.priority)
            
            # Create queue item
            queue_item = TaskQueueItem(
                priority=priority,
                timestamp=datetime.now(),
                task=task
            )
            
            # Add to queue
            self._task_queue.put(queue_item)
            
            self.logger.info(f"Task {task.id} enqueued with priority {task.priority.value}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to enqueue task: {e}")
            raise AgentExecutionError(f"Failed to enqueue task: {str(e)}") from e
    
    def _get_queue_priority(self, task_priority: TaskPriority) -> int:
        """
        Convert TaskPriority to queue priority (lower number = higher priority)
        
        Args:
            task_priority: Task priority enum
            
        Returns:
            Queue priority value
        """
        priority_map = {
            TaskPriority.CRITICAL: 1,
            TaskPriority.HIGH: 2,
            TaskPriority.MEDIUM: 3,
            TaskPriority.LOW: 4,
            TaskPriority.BACKGROUND: 5
        }
        return priority_map.get(task_priority, 3)
    
    def _invoke_callbacks(self, task_id: str, result: AgentResult):
        """
        Invoke callbacks for a completed task
        
        Args:
            task_id: ID of completed task
            result: Task result
        """
        if task_id in self._task_callbacks:
            callbacks = self._task_callbacks[task_id]
            for callback in callbacks:
                try:
                    callback(result)
                except Exception as e:
                    self.logger.error(f"Callback error for task {task_id}: {e}")
            
            # Clean up callbacks
            del self._task_callbacks[task_id]
    
    def getStatus(self) -> AgentStatus:
        """
        Get current status of the agent
        
        Returns:
            Current agent status
        """
        with self._state_lock:
            state = self._state
        
        with self._task_lock:
            current_task = self._current_task
        
        uptime = (datetime.now() - self._start_time).total_seconds()
        
        return AgentStatus(
            instance_id=self.instance_id,
            agent_type=self.agent_type,
            state=state,
            current_task=current_task,
            queued_tasks=self._task_queue.qsize(),
            performance=self._performance,
            last_activity=self._performance.last_updated,
            uptime_seconds=uptime
        )
    
    def getPerformanceMetrics(self) -> PerformanceMetrics:
        """
        Get performance metrics for this agent
        
        Returns:
            Performance metrics
        """
        return self._performance
    
    async def cleanup(self) -> None:
        """
        Clean up agent resources and shut down gracefully
        """
        try:
            with self._state_lock:
                if self._state == AgentState.TERMINATED:
                    self.logger.warning("Agent already terminated")
                    return
                
                self._state = AgentState.SHUTTING_DOWN
            
            # Stop task processing
            self._stop_processing = True
            
            # Wait for processing thread to finish
            if self._processing_thread and self._processing_thread.is_alive():
                self._processing_thread.join(timeout=5.0)
            
            # Wait for current task to complete (with timeout)
            timeout = 30.0  # 30 seconds
            start_wait = time.time()
            while self._current_task and (time.time() - start_wait) < timeout:
                time.sleep(0.5)
            
            if self._current_task:
                self.logger.warning(f"Current task {self._current_task.id} did not complete in time")
            
            # Perform agent-specific cleanup
            await self._cleanup_impl()
            
            with self._state_lock:
                self._state = AgentState.TERMINATED
            
            self.logger.info(f"Agent {self.instance_id} cleaned up successfully")
            
        except Exception as e:
            self.logger.error(f"Error during cleanup: {e}")
            with self._state_lock:
                self._state = AgentState.ERROR
    
    async def _cleanup_impl(self) -> None:
        """
        Agent-specific cleanup logic - can be overridden by subclasses
        
        Default implementation does nothing.
        """
        pass
    
    def get_queue_size(self) -> int:
        """
        Get the number of tasks in the queue
        
        Returns:
            Number of queued tasks
        """
        return self._task_queue.qsize()
    
    def clear_queue(self) -> int:
        """
        Clear all tasks from the queue
        
        Returns:
            Number of tasks cleared
        """
        count = 0
        while not self._task_queue.empty():
            try:
                self._task_queue.get_nowait()
                count += 1
            except Empty:
                break
        
        self.logger.info(f"Cleared {count} tasks from queue")
        return count
    
    def is_ready(self) -> bool:
        """
        Check if agent is ready to accept tasks
        
        Returns:
            True if agent is ready
        """
        with self._state_lock:
            return self._state in [AgentState.READY, AgentState.BUSY]
    
    def is_busy(self) -> bool:
        """
        Check if agent is currently processing a task
        
        Returns:
            True if agent is busy
        """
        with self._state_lock:
            return self._state == AgentState.BUSY
    
    def get_uptime(self) -> float:
        """
        Get agent uptime in seconds
        
        Returns:
            Uptime in seconds
        """
        return (datetime.now() - self._start_time).total_seconds()
    
    def __repr__(self) -> str:
        """String representation of the agent"""
        return (
            f"{self.__class__.__name__}("
            f"instance_id={self.instance_id[:8]}..., "
            f"type={self.agent_type.value}, "
            f"state={self._state.value})"
        )
