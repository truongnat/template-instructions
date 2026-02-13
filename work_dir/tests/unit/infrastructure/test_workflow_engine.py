"""Unit tests for workflow engine components."""

import pytest
from agentic_sdlc.infrastructure.automation import WorkflowEngine, WorkflowRunner
from agentic_sdlc.infrastructure.automation.workflow_engine import WorkflowStep


class TestWorkflowEngine:
    """Tests for WorkflowEngine class."""
    
    def test_workflow_engine_initialization(self):
        """Test that WorkflowEngine initializes correctly."""
        engine = WorkflowEngine()
        assert engine is not None
    
    def test_add_step(self):
        """Test adding a step to the workflow engine."""
        engine = WorkflowEngine()
        step = WorkflowStep(
            name="test_step",
            action="test_action",
            parameters={"key": "value"}
        )
        engine.add_step(step)
        # Verify step was added by executing
        results = engine.execute()
        assert "test_step" in results
    
    def test_execute_workflow(self):
        """Test executing a workflow."""
        engine = WorkflowEngine()
        step1 = WorkflowStep(
            name="step1",
            action="action1",
            parameters={"param1": "value1"}
        )
        step2 = WorkflowStep(
            name="step2",
            action="action2",
            parameters={"param2": "value2"}
        )
        engine.add_step(step1)
        engine.add_step(step2)
        
        results = engine.execute()
        assert len(results) == 2
        assert "step1" in results
        assert "step2" in results
        assert results["step1"]["status"] == "completed"
        assert results["step2"]["status"] == "completed"
    
    def test_execute_with_dependencies(self):
        """Test executing workflow with step dependencies."""
        engine = WorkflowEngine()
        step1 = WorkflowStep(
            name="step1",
            action="action1",
            parameters={}
        )
        step2 = WorkflowStep(
            name="step2",
            action="action2",
            parameters={},
            depends_on=["step1"]
        )
        engine.add_step(step1)
        engine.add_step(step2)
        
        results = engine.execute()
        assert len(results) == 2
        assert results["step1"]["status"] == "completed"
        assert results["step2"]["status"] == "completed"
    
    def test_execute_with_missing_dependency(self):
        """Test that executing with missing dependency raises error."""
        engine = WorkflowEngine()
        step = WorkflowStep(
            name="step1",
            action="action1",
            parameters={},
            depends_on=["nonexistent"]
        )
        engine.add_step(step)
        
        with pytest.raises(RuntimeError, match="Dependency nonexistent not executed yet"):
            engine.execute()


class TestWorkflowRunner:
    """Tests for WorkflowRunner class."""
    
    def test_workflow_runner_initialization(self):
        """Test that WorkflowRunner initializes correctly."""
        runner = WorkflowRunner()
        assert runner is not None
        assert not runner.is_running()
    
    def test_workflow_runner_with_custom_engine(self):
        """Test WorkflowRunner with custom engine."""
        engine = WorkflowEngine()
        runner = WorkflowRunner(engine=engine)
        assert runner.engine is engine
    
    def test_run_workflow(self):
        """Test running a workflow."""
        runner = WorkflowRunner()
        steps = [
            WorkflowStep(
                name="step1",
                action="action1",
                parameters={"key": "value"}
            ),
            WorkflowStep(
                name="step2",
                action="action2",
                parameters={"key": "value"}
            )
        ]
        
        results = runner.run(steps)
        assert len(results) == 2
        assert "step1" in results
        assert "step2" in results
        assert not runner.is_running()
    
    def test_is_running_flag(self):
        """Test that is_running flag is set correctly."""
        runner = WorkflowRunner()
        assert not runner.is_running()
        
        # Create a step that we can track
        steps = [
            WorkflowStep(
                name="test",
                action="test",
                parameters={}
            )
        ]
        
        # After run completes, should not be running
        runner.run(steps)
        assert not runner.is_running()
