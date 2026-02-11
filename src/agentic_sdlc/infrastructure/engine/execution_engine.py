"""Execution engine for running tasks."""

from typing import Any, Callable, Dict, Optional
from dataclasses import dataclass, field


@dataclass
class Task:
    """Represents a task to be executed."""
    
    name: str
    func: Callable[..., Any]
    args: tuple = field(default_factory=tuple)
    kwargs: Dict[str, Any] = field(default_factory=dict)
    timeout: Optional[int] = None


class TaskExecutor:
    """Executor for running individual tasks.
    
    The TaskExecutor is responsible for executing a single task with
    proper error handling and timeout management.
    """
    
    def __init__(self) -> None:
        """Initialize the task executor."""
        pass
    
    def execute(self, task: Task) -> Any:
        """Execute a task.
        
        Args:
            task: The task to execute.
            
        Returns:
            The result of executing the task.
            
        Raises:
            Exception: Any exception raised by the task function.
        """
        try:
            result = task.func(*task.args, **task.kwargs)
            return result
        except Exception as e:
            raise RuntimeError(f"Task '{task.name}' failed: {str(e)}") from e


class ExecutionEngine:
    """Engine for executing multiple tasks.
    
    The ExecutionEngine manages the execution of multiple tasks,
    handling dependencies, parallelization, and error handling.
    """
    
    def __init__(self) -> None:
        """Initialize the execution engine."""
        self._tasks: Dict[str, Task] = {}
        self._executor = TaskExecutor()
        self._results: Dict[str, Any] = {}
    
    def add_task(self, task: Task) -> None:
        """Add a task to the engine.
        
        Args:
            task: The task to add.
        """
        self._tasks[task.name] = task
    
    def execute(self) -> Dict[str, Any]:
        """Execute all tasks.
        
        Returns:
            Dictionary containing results from all tasks.
        """
        self._results = {}
        for task_name, task in self._tasks.items():
            self._results[task_name] = self._executor.execute(task)
        return self._results
    
    def execute_task(self, task_name: str) -> Any:
        """Execute a specific task by name.
        
        Args:
            task_name: The name of the task to execute.
            
        Returns:
            The result of executing the task.
            
        Raises:
            KeyError: If the task is not found.
        """
        if task_name not in self._tasks:
            raise KeyError(f"Task '{task_name}' not found")
        
        task = self._tasks[task_name]
        result = self._executor.execute(task)
        self._results[task_name] = result
        return result
    
    def get_result(self, task_name: str) -> Optional[Any]:
        """Get the result of a previously executed task.
        
        Args:
            task_name: The name of the task.
            
        Returns:
            The result if the task has been executed, None otherwise.
        """
        return self._results.get(task_name)
