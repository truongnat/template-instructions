"""
Tests for the Multi-Agent Orchestration System data models

This module contains unit tests and property-based tests for the core data models
of the orchestration system.
"""

import unittest
from datetime import datetime, timedelta
from uuid import uuid4

# Import the orchestration models
from agentic_sdlc.orchestration.models.workflow import (
    WorkflowPlan, WorkflowState, WorkflowExecution, OrchestrationPattern, ExecutionStatus
)
from agentic_sdlc.orchestration.models.agent import (
    AgentTask, AgentResult, AgentState, AgentType, TaskStatus, ModelTier,
    TaskInput, TaskOutput, DataFormat, TaskPriority
)
from agentic_sdlc.orchestration.models.communication import (
    UserRequest, ConversationContext, SharedContext
)

# Import testing utilities
from agentic_sdlc.orchestration.testing.fixtures import (
    sample_workflow_plan, sample_agent_config, sample_task_input, sample_user_request
)
from agentic_sdlc.orchestration.testing.helpers import (
    create_test_workflow, create_test_agent, create_test_task, assert_workflow_valid
)

try:
    from agentic_sdlc.orchestration.testing.property_testing import (
        OrchestrationTestCase, workflow_strategy, agent_task_strategy, 
        user_request_strategy, given
    )
    HYPOTHESIS_AVAILABLE = True
except ImportError:
    HYPOTHESIS_AVAILABLE = False
    OrchestrationTestCase = unittest.TestCase
    def given(*args, **kwargs):
        def decorator(func):
            return func
        return decorator


class TestWorkflowModels(unittest.TestCase):
    """Test workflow-related data models"""
    
    def test_workflow_plan_creation(self):
        """Test creating a workflow plan"""
        plan = WorkflowPlan(
            pattern=OrchestrationPattern.SEQUENTIAL_HANDOFF,
            estimated_duration=120,
            priority=2
        )
        
        self.assertIsNotNone(plan.id)
        self.assertEqual(plan.pattern, OrchestrationPattern.SEQUENTIAL_HANDOFF)
        self.assertEqual(plan.estimated_duration, 120)
        self.assertEqual(plan.priority, 2)
        self.assertIsInstance(plan.created_at, datetime)
    
    def test_workflow_execution_lifecycle(self):
        """Test workflow execution state transitions"""
        execution = WorkflowExecution()
        
        # Initial state
        self.assertEqual(execution.status, ExecutionStatus.PENDING)
        self.assertIsNone(execution.started_at)
        self.assertIsNone(execution.completed_at)
        self.assertEqual(execution.progress_percentage, 0.0)
        
        # Start execution
        execution.start_execution()
        self.assertEqual(execution.status, ExecutionStatus.RUNNING)
        self.assertIsNotNone(execution.started_at)
        
        # Update progress
        execution.update_progress(50.0)
        self.assertEqual(execution.progress_percentage, 50.0)
        
        # Complete execution
        execution.complete_execution()
        self.assertEqual(execution.status, ExecutionStatus.COMPLETED)
        self.assertIsNotNone(execution.completed_at)
        self.assertEqual(execution.progress_percentage, 100.0)
    
    def test_workflow_execution_failure(self):
        """Test workflow execution failure handling"""
        execution = WorkflowExecution()
        execution.start_execution()
        
        error_message = "Test error"
        execution.fail_execution(error_message)
        
        self.assertEqual(execution.status, ExecutionStatus.FAILED)
        self.assertEqual(execution.error_message, error_message)
        self.assertIsNotNone(execution.completed_at)
    
    def test_workflow_state_management(self):
        """Test workflow state management"""
        from agentic_sdlc.orchestration.models.communication import Checkpoint
        
        state = WorkflowState(
            execution_id="test_exec",
            current_phase="initial"
        )
        
        # Add checkpoint
        checkpoint = Checkpoint(
            phase="checkpoint_1",
            description="Test checkpoint"
        )
        state.add_checkpoint(checkpoint)
        
        self.assertEqual(len(state.checkpoints), 1)
        self.assertEqual(state.get_latest_checkpoint(), checkpoint)
        
        # Complete phase
        state.complete_phase("initial")
        self.assertIn("initial", state.completed_phases)


class TestAgentModels(unittest.TestCase):
    """Test agent-related data models"""
    
    def test_agent_task_creation(self):
        """Test creating an agent task"""
        task_input = TaskInput(
            data={"test": "data"},
            format=DataFormat.JSON,
            source="test"
        )
        
        task = AgentTask(
            type="test_task",
            input=task_input,
            priority=TaskPriority.HIGH
        )
        
        self.assertIsNotNone(task.id)
        self.assertEqual(task.type, "test_task")
        self.assertEqual(task.input, task_input)
        self.assertEqual(task.priority, TaskPriority.HIGH)
        self.assertIsInstance(task.created_at, datetime)
    
    def test_agent_task_lifecycle(self):
        """Test agent task lifecycle"""
        task = AgentTask(type="test_task")
        
        # Initial state
        self.assertIsNone(task.started_at)
        self.assertIsNone(task.completed_at)
        
        # Start task
        task.start_task()
        self.assertIsNotNone(task.started_at)
        
        # Complete task
        task.complete_task()
        self.assertIsNotNone(task.completed_at)
        
        # Check duration
        duration = task.get_duration()
        self.assertIsNotNone(duration)
        self.assertGreaterEqual(duration, 0)
    
    def test_agent_result_validation(self):
        """Test agent result validation"""
        task_output = TaskOutput(
            data={"result": "success"},
            confidence=0.95
        )
        
        result = AgentResult(
            task_id="test_task",
            instance_id="test_instance",
            status=TaskStatus.COMPLETED,
            output=task_output,
            confidence=0.9
        )
        
        self.assertEqual(result.task_id, "test_task")
        self.assertEqual(result.instance_id, "test_instance")
        self.assertEqual(result.status, TaskStatus.COMPLETED)
        self.assertEqual(result.confidence, 0.9)
    
    def test_task_input_format_validation(self):
        """Test task input format validation"""
        # Valid JSON input
        json_input = TaskInput(
            data={"key": "value"},
            format=DataFormat.JSON
        )
        self.assertTrue(json_input.validate_format())
        
        # Valid text input
        text_input = TaskInput(
            data="This is text",
            format=DataFormat.TEXT
        )
        self.assertTrue(text_input.validate_format())
        
        # Invalid format combination
        invalid_input = TaskInput(
            data={"key": "value"},
            format=DataFormat.TEXT
        )
        self.assertFalse(invalid_input.validate_format())


class TestCommunicationModels(unittest.TestCase):
    """Test communication-related data models"""
    
    def test_user_request_creation(self):
        """Test creating a user request"""
        context = ConversationContext(
            user_id="test_user",
            interaction_count=1
        )
        
        request = UserRequest(
            user_id="test_user",
            content="Test request",
            context=context,
            confidence=0.8
        )
        
        self.assertIsNotNone(request.id)
        self.assertEqual(request.user_id, "test_user")
        self.assertEqual(request.content, "Test request")
        self.assertEqual(request.context, context)
        self.assertEqual(request.confidence, 0.8)
    
    def test_conversation_context_updates(self):
        """Test conversation context updates"""
        context = ConversationContext(user_id="test_user")
        
        initial_count = context.interaction_count
        initial_time = context.last_interaction
        
        # Update interaction
        context.update_interaction()
        
        self.assertEqual(context.interaction_count, initial_count + 1)
        self.assertGreater(context.last_interaction, initial_time)
        
        # Add context data
        context.add_context("key", "value")
        self.assertEqual(context.context_data["key"], "value")
    
    def test_shared_context_management(self):
        """Test shared context management"""
        from agentic_sdlc.orchestration.models.communication import Requirement
        
        context = SharedContext()
        
        # Add requirement
        requirement = Requirement(
            title="Test Requirement",
            description="Test description"
        )
        context.add_requirement(requirement)
        
        self.assertEqual(len(context.requirements), 1)
        self.assertEqual(context.requirements[0], requirement)
        
        # Update shared data
        context.update_shared_data("test_key", "test_value")
        self.assertEqual(context.shared_data["test_key"], "test_value")


class TestFixtures(unittest.TestCase):
    """Test the testing fixtures"""
    
    def test_sample_workflow_plan(self):
        """Test sample workflow plan fixture"""
        plan = sample_workflow_plan()
        assert_workflow_valid(plan)
    
    def test_sample_agent_config(self):
        """Test sample agent config fixture"""
        config = sample_agent_config()
        self.assertIsInstance(config.agent_type, AgentType)
        self.assertIsNotNone(config.model_assignment)
        self.assertGreater(config.max_retries, 0)
        self.assertGreater(config.timeout_minutes, 0)
    
    def test_sample_task_input(self):
        """Test sample task input fixture"""
        task_input = sample_task_input()
        self.assertIsNotNone(task_input.data)
        self.assertIsInstance(task_input.format, DataFormat)
        self.assertTrue(task_input.validate_format())
    
    def test_sample_user_request(self):
        """Test sample user request fixture"""
        request = sample_user_request()
        self.assertIsNotNone(request.id)
        self.assertIsNotNone(request.user_id)
        self.assertIsNotNone(request.content)
        self.assertIsNotNone(request.context)


# Property-based tests (only run if Hypothesis is available)
if HYPOTHESIS_AVAILABLE:
    class TestOrchestrationProperties(OrchestrationTestCase):
        """Property-based tests for orchestration system"""
        
        @given(workflow_strategy())
        def test_workflow_plan_properties(self, workflow):
            """Test that all generated workflow plans are valid"""
            self.assertWorkflowValid(workflow)
        
        @given(agent_task_strategy())
        def test_agent_task_properties(self, task):
            """Test that all generated agent tasks are valid"""
            self.assertAgentTaskValid(task)
        
        @given(user_request_strategy())
        def test_user_request_properties(self, request):
            """Test that all generated user requests are valid"""
            self.assertUserRequestValid(request)


class TestHelpers(unittest.TestCase):
    """Test the testing helper functions"""
    
    def test_create_test_workflow(self):
        """Test workflow creation helper"""
        workflow = create_test_workflow()
        assert_workflow_valid(workflow)
    
    def test_create_test_agent(self):
        """Test agent creation helper"""
        agent = create_test_agent()
        self.assertIsNotNone(agent.agent_id)
        self.assertIsInstance(agent.status, TaskStatus)
    
    def test_create_test_task(self):
        """Test task creation helper"""
        task = create_test_task()
        self.assertIsNotNone(task.id)
        self.assertIsNotNone(task.type)
        self.assertIsNotNone(task.input)


if __name__ == '__main__':
    unittest.main()