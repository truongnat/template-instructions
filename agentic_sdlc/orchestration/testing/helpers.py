"""
Testing helper functions for the Multi-Agent Orchestration System

This module provides utility functions to help with testing orchestration components.
"""

from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from unittest.mock import Mock, MagicMock

from ..models.workflow import WorkflowPlan, WorkflowState, WorkflowExecution, OrchestrationPattern
from ..models.agent import (
    AgentTask, AgentResult, AgentState, AgentType, TaskStatus, 
    AgentConfig, AgentInstance, AgentPool
)
from ..models.communication import UserRequest, SharedContext
from ..utils.validation import ValidationResult


def create_test_workflow(
    pattern: OrchestrationPattern = OrchestrationPattern.SEQUENTIAL_HANDOFF,
    duration: int = 60,
    priority: int = 3
) -> WorkflowPlan:
    """Create a test workflow with specified parameters"""
    return WorkflowPlan(
        pattern=pattern,
        estimated_duration=duration,
        priority=priority
    )


def create_test_agent(
    agent_type: AgentType = AgentType.IMPLEMENTATION,
    status: TaskStatus = TaskStatus.PENDING
) -> AgentState:
    """Create a test agent state"""
    from ..models.communication import AgentContext
    from ..models.agent import ResourceAllocation
    
    return AgentState(
        agent_id=f"agent_{agent_type.value}",
        status=status,
        context=AgentContext(
            workflow_id="test_workflow",
            agent_id=f"agent_{agent_type.value}"
        ),
        resources=ResourceAllocation()
    )


def create_test_task(
    task_type: str = "test_task",
    priority: int = 3
) -> AgentTask:
    """Create a test agent task"""
    from ..models.agent import TaskInput, TaskContext, DataFormat, TaskPriority
    
    task_input = TaskInput(
        data={"test": "data"},
        format=DataFormat.JSON,
        source="test_suite"
    )
    
    task_context = TaskContext(
        workflow_id="test_workflow",
        phase="test_phase"
    )
    
    return AgentTask(
        type=task_type,
        input=task_input,
        context=task_context,
        priority=TaskPriority(priority)
    )


def create_test_user_request(content: str = "Test request") -> UserRequest:
    """Create a test user request"""
    return UserRequest(
        user_id="test_user",
        content=content,
        confidence=0.8
    )


def create_mock_agent_pool(agent_type: AgentType, instance_count: int = 2) -> AgentPool:
    """Create a mock agent pool for testing"""
    pool = AgentPool(
        role_type=agent_type,
        max_instances=instance_count + 2
    )
    
    # Add mock instances
    for i in range(instance_count):
        instance = AgentInstance(
            agent_type=agent_type
        )
        pool.add_instance(instance)
    
    return pool


def create_mock_workflow_execution(
    workflow_id: str = "test_workflow",
    status: str = "running"
) -> WorkflowExecution:
    """Create a mock workflow execution"""
    from ..models.workflow import ExecutionStatus
    
    execution = WorkflowExecution(
        plan_id=workflow_id,
        status=ExecutionStatus(status),
        current_phase="test_phase"
    )
    execution.start_execution()
    return execution


def assert_workflow_valid(workflow: WorkflowPlan) -> None:
    """Assert that a workflow plan is valid"""
    assert workflow.id is not None, "Workflow must have an ID"
    assert isinstance(workflow.pattern, OrchestrationPattern), "Workflow must have a valid pattern"
    assert workflow.estimated_duration >= 0, "Workflow duration must be non-negative"
    assert 1 <= workflow.priority <= 5, "Workflow priority must be between 1 and 5"


def assert_agent_state_consistent(agent_state: AgentState) -> None:
    """Assert that an agent state is consistent"""
    assert agent_state.agent_id is not None, "Agent must have an ID"
    assert isinstance(agent_state.status, TaskStatus), "Agent must have a valid status"
    assert agent_state.context is not None, "Agent must have context"
    assert agent_state.resources is not None, "Agent must have resource allocation"


def assert_task_valid(task: AgentTask) -> None:
    """Assert that a task is valid"""
    assert task.id is not None, "Task must have an ID"
    assert task.type is not None, "Task must have a type"
    assert task.input is not None, "Task must have input"
    assert task.context is not None, "Task must have context"


def assert_validation_result_valid(result: ValidationResult) -> None:
    """Assert that a validation result is properly formed"""
    assert isinstance(result.is_valid, bool), "Validation result must have boolean is_valid"
    assert isinstance(result.errors, list), "Validation result must have errors list"
    assert isinstance(result.warnings, list), "Validation result must have warnings list"
    
    # If there are errors, is_valid should be False
    if result.errors:
        assert not result.is_valid, "Validation result with errors must be invalid"


def simulate_workflow_execution(
    workflow: WorkflowPlan,
    duration_seconds: float = 1.0
) -> WorkflowExecution:
    """Simulate a workflow execution for testing"""
    execution = WorkflowExecution(plan_id=workflow.id)
    execution.start_execution()
    
    # Simulate some progress
    import time
    time.sleep(duration_seconds)
    
    execution.update_progress(50.0)
    execution.current_phase = "middle_phase"
    
    return execution


def create_test_environment() -> Dict[str, Any]:
    """Create a complete test environment with all necessary components"""
    workflow = create_test_workflow()
    user_request = create_test_user_request()
    agents = {
        agent_type: create_test_agent(agent_type) 
        for agent_type in AgentType
    }
    tasks = [create_test_task(f"task_{i}") for i in range(3)]
    
    return {
        "workflow": workflow,
        "user_request": user_request,
        "agents": agents,
        "tasks": tasks,
        "shared_context": SharedContext()
    }


def mock_external_dependencies() -> Dict[str, Mock]:
    """Create mocks for external dependencies"""
    mocks = {
        "model_client": Mock(),
        "database": Mock(),
        "file_system": Mock(),
        "network": Mock(),
        "subprocess": Mock()
    }
    
    # Configure model client mock
    mocks["model_client"].generate_response.return_value = {
        "content": "Mock response",
        "confidence": 0.9,
        "tokens_used": 100
    }
    
    # Configure database mock
    mocks["database"].save.return_value = True
    mocks["database"].load.return_value = {"status": "success"}
    
    # Configure subprocess mock
    mocks["subprocess"].run.return_value = Mock(
        returncode=0,
        stdout="Mock output",
        stderr=""
    )
    
    return mocks


def generate_test_data_variations() -> List[Dict[str, Any]]:
    """Generate various test data combinations for comprehensive testing"""
    variations = []
    
    # Different workflow patterns
    for pattern in OrchestrationPattern:
        variations.append({
            "workflow": create_test_workflow(pattern=pattern),
            "description": f"Workflow with {pattern.value} pattern"
        })
    
    # Different agent types
    for agent_type in AgentType:
        variations.append({
            "agent": create_test_agent(agent_type=agent_type),
            "description": f"Agent of type {agent_type.value}"
        })
    
    # Different task statuses
    for status in TaskStatus:
        variations.append({
            "agent": create_test_agent(status=status),
            "description": f"Agent with status {status.value}"
        })
    
    return variations


def measure_performance(func, *args, **kwargs) -> Dict[str, Any]:
    """Measure performance of a function call"""
    import time
    import tracemalloc
    
    # Start memory tracking
    tracemalloc.start()
    start_time = time.time()
    
    try:
        result = func(*args, **kwargs)
        success = True
        error = None
    except Exception as e:
        result = None
        success = False
        error = str(e)
    
    end_time = time.time()
    current, peak = tracemalloc.get_traced_memory()
    tracemalloc.stop()
    
    return {
        "result": result,
        "success": success,
        "error": error,
        "execution_time": end_time - start_time,
        "memory_current": current,
        "memory_peak": peak
    }


def create_stress_test_data(count: int = 100) -> List[Dict[str, Any]]:
    """Create large amounts of test data for stress testing"""
    data = []
    
    for i in range(count):
        data.append({
            "workflow": create_test_workflow(
                duration=60 + (i % 300),  # Vary duration
                priority=(i % 5) + 1      # Vary priority
            ),
            "user_request": create_test_user_request(f"Test request {i}"),
            "tasks": [create_test_task(f"task_{i}_{j}") for j in range(3)]
        })
    
    return data


class TestTimer:
    """Context manager for timing test operations"""
    
    def __init__(self, name: str = "Test Operation"):
        self.name = name
        self.start_time = None
        self.end_time = None
    
    def __enter__(self):
        self.start_time = datetime.now()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.end_time = datetime.now()
        duration = (self.end_time - self.start_time).total_seconds()
        print(f"{self.name} took {duration:.3f} seconds")


def cleanup_test_data(test_data: Dict[str, Any]) -> None:
    """Clean up test data and resources"""
    # Close any open resources
    for key, value in test_data.items():
        if hasattr(value, 'close'):
            try:
                value.close()
            except:
                pass
        elif hasattr(value, 'cleanup'):
            try:
                value.cleanup()
            except:
                pass
    
    # Clear the dictionary
    test_data.clear()