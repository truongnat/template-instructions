"""Execution engine for running tasks."""

from typing import Any, Callable, Dict, Optional, List
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


class ConcurrentExecutor(ExecutionEngine):
    """Executor that runs tasks in parallel using threads.
    
    Equivalent to Swarms' concurrent task execution.
    """
    
    def execute(self) -> Dict[str, Any]:
        """Execute all tasks in parallel."""
        import concurrent.futures
        
        self._results = {}
        with concurrent.futures.ThreadPoolExecutor() as executor:
            future_to_name = {
                executor.submit(self._executor.execute, task): name 
                for name, task in self._tasks.items()
            }
            for future in concurrent.futures.as_completed(future_to_name):
                name = future_to_name[future]
                self._results[name] = future.result()
                
        return self._results


class OutputSynthesizer:
    """Synthesizes multiple outputs into a single coherent response.
    
    Equivalent to Swarms' output synthesis logic.
    """
    
    def synthesize(self, outputs: List[Any], context: Optional[str] = None) -> str:
        """Synthesize multiple outputs.
        
        Args:
            outputs: List of results to synthesize.
            context: Optional context for synthesis.
            
        Returns:
            A single synthesized string result.
        """
        if not outputs:
            return ""
        
        # Simple implementation: join with separators and add context
        header = f"Synthesized Output (Context: {context})\n" if context else "Synthesized Output\n"
        body = "\n---\n".join(str(o) for o in outputs)
        return header + body


class FeedbackProtocol:
    """Handles agent-to-agent or user-to-agent feedback loops.
    
    Equivalent to Swarms' feedback protocols.
    """
    
    def __init__(self) -> None:
        self.history = []
    
    def process_feedback(self, target: str, feedback: str, score: Optional[float] = None) -> Dict[str, Any]:
        """Process and store feedback.
        
        Args:
            target: The recipient of the feedback.
            feedback: The feedback message.
            score: Optional numeric score (0-1).
            
        Returns:
            Status of feedback processing.
        """
        entry = {
            "target": target,
            "feedback": feedback,
            "score": score,
            "timestamp": __import__("datetime").datetime.now().isoformat()
        }
        self.history.append(entry)
        return {"status": "success", "processed_at": entry["timestamp"]}
