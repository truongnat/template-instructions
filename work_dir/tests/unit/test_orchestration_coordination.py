"""Unit tests for orchestration coordination module."""

import pytest

from agentic_sdlc.orchestration import Coordinator, ExecutionPlan


class TestExecutionPlan:
    """Tests for ExecutionPlan class."""
    
    def test_execution_plan_creation(self) -> None:
        """Test creating an execution plan."""
        plan = ExecutionPlan(workflow_id="workflow-1")
        assert plan.workflow_id == "workflow-1"
        assert plan.steps == []
        assert plan.agent_assignments == {}
        assert plan.resource_allocation == {}
        assert plan.id is not None
    
    def test_execution_plan_with_steps(self) -> None:
        """Test creating an execution plan with steps."""
        plan = ExecutionPlan(
            workflow_id="workflow-1",
            steps=["step1", "step2"],
        )
        assert plan.steps == ["step1", "step2"]
    
    def test_execution_plan_empty_workflow_id_raises_error(self) -> None:
        """Test that empty workflow_id raises ValueError."""
        with pytest.raises(ValueError, match="Workflow ID cannot be empty"):
            ExecutionPlan(workflow_id="")
    
    def test_execution_plan_add_step(self) -> None:
        """Test adding a step to execution plan."""
        plan = ExecutionPlan(workflow_id="workflow-1")
        plan.add_step("step1")
        assert "step1" in plan.steps
    
    def test_execution_plan_add_duplicate_step(self) -> None:
        """Test that adding duplicate step doesn't create duplicates."""
        plan = ExecutionPlan(workflow_id="workflow-1")
        plan.add_step("step1")
        plan.add_step("step1")
        assert plan.steps.count("step1") == 1
    
    def test_execution_plan_assign_agent(self) -> None:
        """Test assigning an agent to a step."""
        plan = ExecutionPlan(workflow_id="workflow-1")
        plan.assign_agent("step1", "agent-1")
        assert plan.agent_assignments["step1"] == "agent-1"
    
    def test_execution_plan_allocate_resource(self) -> None:
        """Test allocating a resource."""
        plan = ExecutionPlan(workflow_id="workflow-1")
        plan.allocate_resource("memory", 1024)
        assert plan.resource_allocation["memory"] == 1024
    
    def test_execution_plan_unique_ids(self) -> None:
        """Test that execution plans have unique IDs."""
        plan1 = ExecutionPlan(workflow_id="workflow-1")
        plan2 = ExecutionPlan(workflow_id="workflow-2")
        assert plan1.id != plan2.id


class TestCoordinator:
    """Tests for Coordinator class."""
    
    def test_coordinator_creation(self) -> None:
        """Test creating a coordinator."""
        coordinator = Coordinator()
        assert coordinator._execution_plans == {}
        assert coordinator._active_executions == {}
    
    def test_coordinator_create_execution_plan(self) -> None:
        """Test creating an execution plan."""
        coordinator = Coordinator()
        plan = coordinator.create_execution_plan(
            workflow_id="workflow-1",
            steps=["step1", "step2"],
        )
        assert plan.workflow_id == "workflow-1"
        assert plan.steps == ["step1", "step2"]
        assert plan.id in coordinator._execution_plans
    
    def test_coordinator_get_execution_plan(self) -> None:
        """Test getting an execution plan."""
        coordinator = Coordinator()
        plan = coordinator.create_execution_plan(
            workflow_id="workflow-1",
            steps=["step1"],
        )
        retrieved = coordinator.get_execution_plan(plan.id)
        assert retrieved == plan
    
    def test_coordinator_get_nonexistent_execution_plan(self) -> None:
        """Test getting a nonexistent execution plan returns None."""
        coordinator = Coordinator()
        retrieved = coordinator.get_execution_plan("nonexistent")
        assert retrieved is None
    
    def test_coordinator_start_execution(self) -> None:
        """Test starting an execution."""
        coordinator = Coordinator()
        plan = coordinator.create_execution_plan(
            workflow_id="workflow-1",
            steps=["step1"],
        )
        execution_id = coordinator.start_execution(plan.id)
        assert execution_id is not None
        assert execution_id.startswith("exec_")
    
    def test_coordinator_start_execution_with_context(self) -> None:
        """Test starting an execution with context."""
        coordinator = Coordinator()
        plan = coordinator.create_execution_plan(
            workflow_id="workflow-1",
            steps=["step1"],
        )
        context = {"key": "value"}
        execution_id = coordinator.start_execution(plan.id, context)
        execution = coordinator._active_executions[execution_id]
        assert execution["context"] == context
    
    def test_coordinator_start_execution_nonexistent_plan_raises_error(self) -> None:
        """Test that starting execution with nonexistent plan raises error."""
        coordinator = Coordinator()
        with pytest.raises(ValueError, match="not found"):
            coordinator.start_execution("nonexistent")
    
    def test_coordinator_get_execution_status(self) -> None:
        """Test getting execution status."""
        coordinator = Coordinator()
        plan = coordinator.create_execution_plan(
            workflow_id="workflow-1",
            steps=["step1"],
        )
        execution_id = coordinator.start_execution(plan.id)
        status = coordinator.get_execution_status(execution_id)
        assert status == "running"
    
    def test_coordinator_get_nonexistent_execution_status(self) -> None:
        """Test getting status of nonexistent execution returns None."""
        coordinator = Coordinator()
        status = coordinator.get_execution_status("nonexistent")
        assert status is None
    
    def test_coordinator_complete_execution(self) -> None:
        """Test completing an execution."""
        coordinator = Coordinator()
        plan = coordinator.create_execution_plan(
            workflow_id="workflow-1",
            steps=["step1"],
        )
        execution_id = coordinator.start_execution(plan.id)
        coordinator.complete_execution(execution_id)
        status = coordinator.get_execution_status(execution_id)
        assert status == "completed"
    
    def test_coordinator_complete_nonexistent_execution_raises_error(self) -> None:
        """Test that completing nonexistent execution raises error."""
        coordinator = Coordinator()
        with pytest.raises(ValueError, match="not found"):
            coordinator.complete_execution("nonexistent")
    
    def test_coordinator_fail_execution(self) -> None:
        """Test failing an execution."""
        coordinator = Coordinator()
        plan = coordinator.create_execution_plan(
            workflow_id="workflow-1",
            steps=["step1"],
        )
        execution_id = coordinator.start_execution(plan.id)
        coordinator.fail_execution(execution_id, "Test error")
        status = coordinator.get_execution_status(execution_id)
        assert status == "failed"
        execution = coordinator._active_executions[execution_id]
        assert execution["error"] == "Test error"
    
    def test_coordinator_fail_nonexistent_execution_raises_error(self) -> None:
        """Test that failing nonexistent execution raises error."""
        coordinator = Coordinator()
        with pytest.raises(ValueError, match="not found"):
            coordinator.fail_execution("nonexistent", "error")
