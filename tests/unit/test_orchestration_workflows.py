"""Unit tests for orchestration workflows module."""

import pytest

from agentic_sdlc.orchestration import Workflow, WorkflowBuilder, WorkflowStep


class TestWorkflowStep:
    """Tests for WorkflowStep class."""
    
    def test_workflow_step_creation(self) -> None:
        """Test creating a workflow step."""
        step = WorkflowStep(
            name="analyze",
            agent_id="agent-1",
        )
        assert step.name == "analyze"
        assert step.agent_id == "agent-1"
        assert step.description is None
        assert step.input_keys == []
        assert step.output_keys == []
        assert step.metadata == {}
    
    def test_workflow_step_with_all_parameters(self) -> None:
        """Test creating a workflow step with all parameters."""
        step = WorkflowStep(
            name="analyze",
            agent_id="agent-1",
            description="Analyze the data",
            input_keys=["data"],
            output_keys=["result"],
            metadata={"priority": "high"},
        )
        assert step.description == "Analyze the data"
        assert step.input_keys == ["data"]
        assert step.output_keys == ["result"]
        assert step.metadata == {"priority": "high"}


class TestWorkflow:
    """Tests for Workflow class."""
    
    def test_workflow_creation(self) -> None:
        """Test creating a workflow."""
        workflow = Workflow(name="test_workflow")
        assert workflow.name == "test_workflow"
        assert workflow.description is None
        assert workflow.steps == []
        assert workflow.timeout == 300
        assert workflow.id is not None
    
    def test_workflow_with_all_parameters(self) -> None:
        """Test creating a workflow with all parameters."""
        workflow = Workflow(
            name="test_workflow",
            description="A test workflow",
            timeout=600,
        )
        assert workflow.description == "A test workflow"
        assert workflow.timeout == 600
    
    def test_workflow_empty_name_raises_error(self) -> None:
        """Test that empty name raises ValueError."""
        with pytest.raises(ValueError, match="Workflow name cannot be empty"):
            Workflow(name="")
    
    def test_workflow_invalid_timeout_raises_error(self) -> None:
        """Test that invalid timeout raises ValueError."""
        with pytest.raises(ValueError, match="Workflow timeout must be at least 1"):
            Workflow(name="test", timeout=0)
    
    def test_workflow_add_step(self) -> None:
        """Test adding a step to a workflow."""
        workflow = Workflow(name="test_workflow")
        step = WorkflowStep(name="step1", agent_id="agent-1")
        workflow.add_step(step)
        assert len(workflow.steps) == 1
        assert workflow.steps[0] == step
    
    def test_workflow_get_step(self) -> None:
        """Test getting a step by name."""
        workflow = Workflow(name="test_workflow")
        step = WorkflowStep(name="step1", agent_id="agent-1")
        workflow.add_step(step)
        found = workflow.get_step("step1")
        assert found == step
    
    def test_workflow_get_nonexistent_step(self) -> None:
        """Test getting a nonexistent step returns None."""
        workflow = Workflow(name="test_workflow")
        found = workflow.get_step("nonexistent")
        assert found is None
    
    def test_workflow_unique_ids(self) -> None:
        """Test that workflows have unique IDs."""
        workflow1 = Workflow(name="workflow1")
        workflow2 = Workflow(name="workflow2")
        assert workflow1.id != workflow2.id


class TestWorkflowBuilder:
    """Tests for WorkflowBuilder class."""
    
    def test_workflow_builder_creation(self) -> None:
        """Test creating a workflow builder."""
        builder = WorkflowBuilder("test_workflow")
        assert builder._workflow.name == "test_workflow"
    
    def test_workflow_builder_with_description(self) -> None:
        """Test creating a workflow builder with description."""
        builder = WorkflowBuilder("test_workflow", description="A test workflow")
        assert builder._workflow.description == "A test workflow"
    
    def test_workflow_builder_add_step(self) -> None:
        """Test adding a step via builder."""
        builder = WorkflowBuilder("test_workflow")
        result = builder.add_step("step1", "agent-1")
        assert result is builder  # Check method chaining
        assert len(builder._workflow.steps) == 1
    
    def test_workflow_builder_add_step_with_all_parameters(self) -> None:
        """Test adding a step with all parameters."""
        builder = WorkflowBuilder("test_workflow")
        builder.add_step(
            name="step1",
            agent_id="agent-1",
            description="First step",
            input_keys=["input"],
            output_keys=["output"],
            metadata={"priority": "high"},
        )
        step = builder._workflow.steps[0]
        assert step.name == "step1"
        assert step.description == "First step"
        assert step.input_keys == ["input"]
        assert step.output_keys == ["output"]
        assert step.metadata == {"priority": "high"}
    
    def test_workflow_builder_set_timeout(self) -> None:
        """Test setting timeout via builder."""
        builder = WorkflowBuilder("test_workflow")
        result = builder.set_timeout(600)
        assert result is builder  # Check method chaining
        assert builder._workflow.timeout == 600
    
    def test_workflow_builder_set_metadata(self) -> None:
        """Test setting metadata via builder."""
        builder = WorkflowBuilder("test_workflow")
        result = builder.set_metadata("key", "value")
        assert result is builder  # Check method chaining
        assert builder._workflow.metadata["key"] == "value"
    
    def test_workflow_builder_method_chaining(self) -> None:
        """Test method chaining in builder."""
        workflow = (
            WorkflowBuilder("test_workflow")
            .add_step("step1", "agent-1")
            .add_step("step2", "agent-2")
            .set_timeout(600)
            .set_metadata("priority", "high")
            .build()
        )
        assert workflow.name == "test_workflow"
        assert len(workflow.steps) == 2
        assert workflow.timeout == 600
        assert workflow.metadata["priority"] == "high"
    
    def test_workflow_builder_build_without_steps_raises_error(self) -> None:
        """Test that building without steps raises ValueError."""
        builder = WorkflowBuilder("test_workflow")
        with pytest.raises(ValueError, match="Workflow must have at least one step"):
            builder.build()
    
    def test_workflow_builder_build_returns_workflow(self) -> None:
        """Test that build returns a Workflow instance."""
        builder = WorkflowBuilder("test_workflow")
        builder.add_step("step1", "agent-1")
        workflow = builder.build()
        assert isinstance(workflow, Workflow)
        assert workflow.name == "test_workflow"
        assert len(workflow.steps) == 1
