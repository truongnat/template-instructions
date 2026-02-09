#!/usr/bin/env python3
"""
Tests for Orchestrator

This module tests the orchestrator functionality for workflow execution,
agent coordination, and task distribution.
"""

import unittest
import tempfile
from pathlib import Path
from datetime import datetime
from unittest.mock import Mock, patch, MagicMock

from agentic_sdlc.orchestration.engine.orchestrator import (
    Orchestrator, ExecutionState, TaskPriorityLevel, ExecutionContext,
    TaskExecution, WorkflowExecution
)
from agentic_sdlc.orchestration.interfaces.cli_interface import (
    CLIInterface, CommunicationProtocol, HeartbeatConfig
)
from agentic_sdlc.orchestration.engine.workflow_engine import WorkflowEngine
from agentic_sdlc.orchestration.engine.agent_pool import EnhancedAgentPool
from agentic_sdlc.orchestration.models import (
    AgentType, AgentConfig, AgentTask, AgentResult, AgentProcess,
    WorkflowPlan, AgentAssignment, ClarifiedRequest, UserRequest, OrchestrationPattern,
    ModelTier, ModelAssignment, TaskInput, TaskContext, DataFormat,
    TaskStatus, ProcessStatus, TaskPriority
)


class TestOrchestrator(unittest.TestCase):
    """Test orchestrator functionality"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.temp_dir = tempfile.TemporaryDirectory()
        self.temp_path = Path(self.temp_dir.name)
        
        # Create mock dependencies
        self.cli_interface = Mock(spec=CLIInterface)
        self.workflow_engine = Mock(spec=WorkflowEngine)
        self.agent_pool = Mock(spec=EnhancedAgentPool)
        
        # Create orchestrator
        self.orchestrator = Orchestrator(
            cli_interface=self.cli_interface,
            workflow_engine=self.workflow_engine,
            agent_pool=self.agent_pool,
            max_concurrent_workflows=3,
            task_timeout_minutes=5,
            heartbeat_interval_seconds=10
        )
        
        # Create test data
        self.test_user_request = UserRequest(
            content="Create a new feature",
            user_id="user-1"
        )
        
        self.test_request = ClarifiedRequest(
            original_request=self.test_user_request,
            clarified_content="Create a user authentication feature",
            extracted_requirements=["authentication", "security"],
            identified_constraints=["budget", "timeline"],
            suggested_approach="JWT-based authentication",
            confidence=0.9
        )
        
        self.test_task = AgentTask(
            id="task-1",
            type="implementation",
            input=TaskInput(
                data={"requirements": "JWT authentication"},
                format=DataFormat.JSON
            ),
            context=TaskContext(
                workflow_id="workflow-1",
                phase="implementation"
            ),
            priority=TaskPriority.MEDIUM
        )
        
        self.test_assignment = AgentAssignment(
            agent_type=AgentType.IMPLEMENTATION,
            priority=1,
            estimated_duration=60
        )
        
        self.test_workflow_plan = WorkflowPlan(
            id="workflow-1",
            pattern=OrchestrationPattern.SEQUENTIAL_HANDOFF,
            agents=[self.test_assignment],
            estimated_duration=60,
            priority=1
        )
    
    def tearDown(self):
        """Clean up test fixtures"""
        self.orchestrator.cleanup()
        self.temp_dir.cleanup()
    
    def _execute_workflow_with_mock(self, request=None, workflow_plan=None):
        """Helper method to execute workflow with mocked async execution"""
        with patch.object(self.orchestrator.executor, 'submit') as mock_submit:
            mock_future = Mock()
            mock_submit.return_value = mock_future
            
            execution_id = self.orchestrator.execute_workflow(
                request=request or self.test_request,
                workflow_plan=workflow_plan or self.test_workflow_plan
            )
            return execution_id
    
    def test_orchestrator_initialization(self):
        """Test orchestrator initialization"""
        self.assertIsNotNone(self.orchestrator.cli_interface)
        self.assertIsNotNone(self.orchestrator.workflow_engine)
        self.assertIsNotNone(self.orchestrator.agent_pool)
        self.assertEqual(self.orchestrator.max_concurrent_workflows, 3)
        self.assertEqual(self.orchestrator.task_timeout_minutes, 5)
        self.assertEqual(len(self.orchestrator.active_executions), 0)
    
    def test_execute_workflow_with_plan(self):
        """Test executing workflow with existing plan"""
        # Mock workflow engine validation
        self.workflow_engine.evaluate_request.return_value = []
        
        # Mock the async execution to prevent hanging
        with patch.object(self.orchestrator.executor, 'submit') as mock_submit:
            mock_future = Mock()
            mock_submit.return_value = mock_future
            
            # Execute workflow
            execution_id = self.orchestrator.execute_workflow(
                request=self.test_request,
                workflow_plan=self.test_workflow_plan
            )
            
            # Verify execution was created
            self.assertIsNotNone(execution_id)
            self.assertIn(execution_id, self.orchestrator.active_executions)
            
            # Verify execution context
            execution = self.orchestrator.active_executions[execution_id]
            self.assertEqual(execution.workflow_plan, self.test_workflow_plan)
            self.assertEqual(execution.context.workflow_id, "workflow-1")
            self.assertEqual(execution.context.total_steps, 1)
            
            # Verify async execution was started
            mock_submit.assert_called_once()
        self.assertEqual(execution.context.total_steps, 1)
    
    def test_execute_workflow_without_plan(self):
        """Test executing workflow without existing plan"""
        # Mock workflow engine to return matches and generate plan
        mock_match = Mock()
        mock_match.confidence_score = 0.9
        mock_match.workflow_template = Mock()
        
        # Configure the mock methods
        self.workflow_engine.evaluate_request.return_value = [mock_match]
        self.workflow_engine.generate_execution_plan = Mock(return_value=self.test_workflow_plan)
        
        # Mock the async execution to prevent hanging
        with patch.object(self.orchestrator.executor, 'submit') as mock_submit:
            mock_future = Mock()
            mock_submit.return_value = mock_future
            
            # Execute workflow
            execution_id = self.orchestrator.execute_workflow(request=self.test_request)
            
            # Verify workflow engine was called
            self.workflow_engine.evaluate_request.assert_called_once_with(self.test_request)
            self.workflow_engine.generate_execution_plan.assert_called_once()
            
            # Verify execution was created
            self.assertIsNotNone(execution_id)
            self.assertIn(execution_id, self.orchestrator.active_executions)
            
            # Verify async execution was started
            mock_submit.assert_called_once()
    
    def test_get_execution_status(self):
        """Test getting execution status"""
        # Create execution
        execution_id = self._execute_workflow_with_mock()
        
        # Get status
        status = self.orchestrator.get_execution_status(execution_id)
        
        # Verify status
        self.assertIsNotNone(status)
        self.assertEqual(status["execution_id"], execution_id)
        self.assertEqual(status["workflow_id"], "workflow-1")
        self.assertIn("state", status)
        self.assertIn("progress_percentage", status)
        self.assertIn("current_step", status)
        self.assertIn("total_steps", status)
    
    def test_pause_and_resume_execution(self):
        """Test pausing and resuming execution"""
        # Create execution
        execution_id = self._execute_workflow_with_mock()
        
        # Set state to running for testing
        execution = self.orchestrator.active_executions[execution_id]
        execution.context.state = ExecutionState.RUNNING
        
        # Pause execution
        result = self.orchestrator.pause_execution(execution_id)
        self.assertTrue(result)
        self.assertEqual(execution.context.state, ExecutionState.PAUSED)
        
        # Resume execution
        result = self.orchestrator.resume_execution(execution_id)
        self.assertTrue(result)
        self.assertEqual(execution.context.state, ExecutionState.RUNNING)
    
    def test_cancel_execution(self):
        """Test cancelling execution"""
        # Create execution
        execution_id = self._execute_workflow_with_mock()
        
        # Cancel execution
        result = self.orchestrator.cancel_execution(execution_id)
        self.assertTrue(result)
        
        # Verify execution was moved to history
        self.assertNotIn(execution_id, self.orchestrator.active_executions)
        self.assertEqual(len(self.orchestrator.execution_history), 1)
        self.assertEqual(self.orchestrator.execution_history[0].context.state, ExecutionState.CANCELLED)
    
    def test_get_active_executions(self):
        """Test getting all active executions"""
        # Create multiple executions
        execution_id1 = self._execute_workflow_with_mock()
        execution_id2 = self._execute_workflow_with_mock()
        
        # Get active executions
        active_executions = self.orchestrator.get_active_executions()
        
        # Verify results
        self.assertEqual(len(active_executions), 2)
        execution_ids = [exec["execution_id"] for exec in active_executions]
        self.assertIn(execution_id1, execution_ids)
        self.assertIn(execution_id2, execution_ids)
    
    def test_get_execution_metrics(self):
        """Test getting execution metrics"""
        metrics = self.orchestrator.get_execution_metrics()
        
        # Verify metrics structure
        self.assertIn("total_executions", metrics)
        self.assertIn("successful_executions", metrics)
        self.assertIn("failed_executions", metrics)
        self.assertIn("average_execution_time", metrics)
        self.assertIn("task_success_rate", metrics)
        
        # Verify initial values
        self.assertEqual(metrics["total_executions"], 0)
        self.assertEqual(metrics["successful_executions"], 0)
        self.assertEqual(metrics["failed_executions"], 0)
    
    def test_task_priority_determination(self):
        """Test task priority determination"""
        # Test critical priority
        critical_task = AgentTask(
            id="critical-task",
            type="critical_security_fix",
            input=TaskInput(data={}),
            context=TaskContext(workflow_id="test", phase="test"),
            priority=TaskPriority.CRITICAL
        )
        
        priority = self.orchestrator._determine_task_priority(critical_task)
        self.assertEqual(priority, TaskPriorityLevel.CRITICAL)
        
        # Test high priority
        high_task = AgentTask(
            id="high-task",
            type="important_feature",
            input=TaskInput(data={}),
            context=TaskContext(workflow_id="test", phase="test"),
            priority=TaskPriority.HIGH
        )
        
        priority = self.orchestrator._determine_task_priority(high_task)
        self.assertEqual(priority, TaskPriorityLevel.HIGH)
        
        # Test normal priority
        normal_task = AgentTask(
            id="normal-task",
            type="regular_feature",
            input=TaskInput(data={}),
            context=TaskContext(workflow_id="test", phase="test"),
            priority=TaskPriority.MEDIUM
        )
        
        priority = self.orchestrator._determine_task_priority(normal_task)
        self.assertEqual(priority, TaskPriorityLevel.NORMAL)
    
    def test_workflow_plan_validation(self):
        """Test workflow plan validation"""
        # Test valid plan
        result = self.orchestrator._validate_workflow_plan(self.test_workflow_plan)
        self.assertTrue(result.is_valid)
        
        # Test invalid plan - missing workflow ID
        invalid_plan = WorkflowPlan(
            id="",  # Empty ID
            pattern=OrchestrationPattern.SEQUENTIAL_HANDOFF,
            agents=[],
            estimated_duration=60,
            priority=1
        )
        
        result = self.orchestrator._validate_workflow_plan(invalid_plan)
        self.assertFalse(result.is_valid)
        self.assertIn("Missing workflow ID", result.error_message)
        
        # Test invalid plan - no agent assignments
        invalid_plan.id = "test-id"
        result = self.orchestrator._validate_workflow_plan(invalid_plan)
        self.assertFalse(result.is_valid)
        self.assertIn("No agent assignments found", result.error_message)


if __name__ == '__main__':
    unittest.main()