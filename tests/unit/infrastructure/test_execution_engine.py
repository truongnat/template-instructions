"""Unit tests for execution engine components."""

import pytest
from agentic_sdlc.infrastructure.engine import ExecutionEngine, TaskExecutor
from agentic_sdlc.infrastructure.engine.execution_engine import Task


class TestTaskExecutor:
    """Tests for TaskExecutor class."""
    
    def test_task_executor_initialization(self):
        """Test that TaskExecutor initializes correctly."""
        executor = TaskExecutor()
        assert executor is not None
    
    def test_execute_simple_task(self):
        """Test executing a simple task."""
        executor = TaskExecutor()
        
        def simple_func(x, y):
            return x + y
        
        task = Task(
            name="add",
            func=simple_func,
            args=(2, 3)
        )
        
        result = executor.execute(task)
        assert result == 5
    
    def test_execute_task_with_kwargs(self):
        """Test executing a task with keyword arguments."""
        executor = TaskExecutor()
        
        def func_with_kwargs(a, b=10):
            return a * b
        
        task = Task(
            name="multiply",
            func=func_with_kwargs,
            args=(5,),
            kwargs={"b": 3}
        )
        
        result = executor.execute(task)
        assert result == 15
    
    def test_execute_task_with_exception(self):
        """Test that task exceptions are wrapped."""
        executor = TaskExecutor()
        
        def failing_func():
            raise ValueError("Test error")
        
        task = Task(
            name="failing",
            func=failing_func
        )
        
        with pytest.raises(RuntimeError, match="Task 'failing' failed"):
            executor.execute(task)
    
    def test_execute_task_no_args(self):
        """Test executing a task with no arguments."""
        executor = TaskExecutor()
        
        def no_args_func():
            return "success"
        
        task = Task(
            name="no_args",
            func=no_args_func
        )
        
        result = executor.execute(task)
        assert result == "success"


class TestExecutionEngine:
    """Tests for ExecutionEngine class."""
    
    def test_execution_engine_initialization(self):
        """Test that ExecutionEngine initializes correctly."""
        engine = ExecutionEngine()
        assert engine is not None
    
    def test_add_task(self):
        """Test adding a task to the engine."""
        engine = ExecutionEngine()
        
        def test_func():
            return "result"
        
        task = Task(
            name="test_task",
            func=test_func
        )
        
        engine.add_task(task)
        # Verify task was added by executing
        results = engine.execute()
        assert "test_task" in results
    
    def test_execute_multiple_tasks(self):
        """Test executing multiple tasks."""
        engine = ExecutionEngine()
        
        def task1_func():
            return "result1"
        
        def task2_func():
            return "result2"
        
        task1 = Task(name="task1", func=task1_func)
        task2 = Task(name="task2", func=task2_func)
        
        engine.add_task(task1)
        engine.add_task(task2)
        
        results = engine.execute()
        assert len(results) == 2
        assert results["task1"] == "result1"
        assert results["task2"] == "result2"
    
    def test_execute_single_task(self):
        """Test executing a single task by name."""
        engine = ExecutionEngine()
        
        def test_func():
            return "single_result"
        
        task = Task(name="single", func=test_func)
        engine.add_task(task)
        
        result = engine.execute_task("single")
        assert result == "single_result"
    
    def test_execute_nonexistent_task(self):
        """Test executing nonexistent task raises error."""
        engine = ExecutionEngine()
        
        with pytest.raises(KeyError, match="Task 'nonexistent' not found"):
            engine.execute_task("nonexistent")
    
    def test_get_result(self):
        """Test getting result of executed task."""
        engine = ExecutionEngine()
        
        def test_func():
            return "test_result"
        
        task = Task(name="test", func=test_func)
        engine.add_task(task)
        engine.execute()
        
        result = engine.get_result("test")
        assert result == "test_result"
    
    def test_get_result_not_executed(self):
        """Test getting result of non-executed task returns None."""
        engine = ExecutionEngine()
        
        def test_func():
            return "result"
        
        task = Task(name="test", func=test_func)
        engine.add_task(task)
        
        result = engine.get_result("test")
        assert result is None
    
    def test_execute_task_with_args(self):
        """Test executing task with arguments."""
        engine = ExecutionEngine()
        
        def add_func(a, b):
            return a + b
        
        task = Task(
            name="add",
            func=add_func,
            args=(10, 20)
        )
        
        engine.add_task(task)
        result = engine.execute_task("add")
        assert result == 30
    
    def test_task_execution_order(self):
        """Test that tasks are executed in order."""
        engine = ExecutionEngine()
        execution_order = []
        
        def task1():
            execution_order.append(1)
            return 1
        
        def task2():
            execution_order.append(2)
            return 2
        
        def task3():
            execution_order.append(3)
            return 3
        
        engine.add_task(Task(name="task1", func=task1))
        engine.add_task(Task(name="task2", func=task2))
        engine.add_task(Task(name="task3", func=task3))
        
        engine.execute()
        assert execution_order == [1, 2, 3]
