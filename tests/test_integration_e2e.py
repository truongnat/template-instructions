import unittest
import time
from concurrent.futures import Future
from unittest.mock import MagicMock, patch

from agentic_sdlc.orchestration.interfaces.framework_integration import OrchestrationAdapter
from agentic_sdlc.orchestration.models.workflow import ExecutionStatus
from agentic_sdlc.orchestration.models.agent import TaskStatus

class TestEndToEndWorkflow(unittest.TestCase):
    """
    End-to-end integration tests for the orchestration system.
    """
    
    def setUp(self):
        """Set up the test environment"""
        self.adapter = OrchestrationAdapter()
        self.adapter.initialize()
        
        # Scale up all pools to ensure concurrency
        for pool in self.adapter._orchestrator.agent_pools.values():
            pool.scaling_thresholds.min_instances = 5
            pool.force_scale(5)
        
        # We need to mock the CLI interface's send_task method to avoid actual subprocess spawning
        # while keeping the rest of the logic intact.
        self.original_send_task = self.adapter._orchestrator.cli_interface.send_task
        
        # Mock the send_task method on the specific instance used by the orchestrator
        self.mock_send_task = MagicMock()
        self.adapter._orchestrator.cli_interface.send_task = self.mock_send_task
        
        # Mock MainAgent process_request to avoid NLP ambiguity issues
        self.original_process_request = self.adapter._main_agent.process_request
        self.mock_process_request = MagicMock()
        self.adapter._main_agent.process_request = self.mock_process_request
        
        # Mock WorkflowEngine to return deterministic matches
        self.original_evaluate_request = self.adapter._orchestrator.workflow_engine.evaluate_request
        self.mock_evaluate_request = MagicMock()
        self.adapter._orchestrator.workflow_engine.evaluate_request = self.mock_evaluate_request
        
        # Setup default mock for evaluate_request
        from agentic_sdlc.orchestration.models.workflow import WorkflowMatch, OrchestrationPattern
        from agentic_sdlc.orchestration.models.agent import AgentType
        self.mock_evaluate_request.return_value = [
            WorkflowMatch(
                workflow_id="feature_implementation",
                relevance_score=0.9,
                pattern=OrchestrationPattern.PARALLEL_EXECUTION,
                estimated_duration=60,
                required_agents=[AgentType.IMPLEMENTATION.value], # Simplify to 1 agent for test
                confidence=0.9
            )
        ]
        
    def tearDown(self):
        """Clean up resources"""
        self.adapter._orchestrator.cleanup()
        
    def test_complete_sequential_workflow(self):
        """
        Test a complete sequential workflow execution.
        Flow: Request -> MainAgent -> Orchestrator -> Agent(Mock) -> Result
        """
        # 1. Define the user request
        request_content = "Create a Python script that calculates Fibonacci numbers."
        
        # Mock MainAgent success response
        from agentic_sdlc.orchestration.models.communication import WorkflowInitiation
        self.mock_process_request.return_value = WorkflowInitiation(
            request_id="mock-req-id",
            should_proceed=True,
            workflow_type="feature_implementation",
            estimated_complexity="low",
            clarified_request=None # Optional, uses original
        )
        
        # 2. Setup the mock agent response
        from agentic_sdlc.orchestration.models.agent import AgentResult, TaskOutput, DataFormat, ResultMetadata
        
        # Create result directly
        agent_result = AgentResult(
            task_id="test-task-1",
            instance_id="test-instance-1",
            status=TaskStatus.COMPLETED,
            output=TaskOutput(
                data={"code": "def fib(n): return n if n<=1 else fib(n-1)+fib(n-2)"},
                format=DataFormat.TEXT
            ),
            metadata=ResultMetadata(execution_time=0.1)
        )
        
        # Return a future that is already done
        future = Future()
        future.set_result(agent_result)
        self.mock_send_task.return_value = future
        
        # 3. Execute the workflow via the adapter
        exit_code = self.adapter._run_workflow(request_content)
        self.assertEqual(exit_code, 0)
        
        # 4. Monitor execution until completion
        # Get the execution ID (it's the only active one initially)
        executions = self.adapter._orchestrator.get_active_executions()
        
        # If execution finished very fast, it might already be in history
        if not executions:
             # Check history
             self.assertGreater(len(self.adapter._orchestrator.execution_history), 0)
             execution_id = self.adapter._orchestrator.execution_history[0].context.execution_id
        else:
            execution_id = executions[0]['execution_id']
            # Wait for completion (with timeout)
            max_retries = 20
            for _ in range(max_retries):
                status = self.adapter._orchestrator.get_execution_status(execution_id)
                if status['state'] in ['completed', 'failed', 'cancelled']:
                    break
                time.sleep(0.2)
            
        # 5. Verify results
        final_status = self.adapter._orchestrator.get_execution_status(execution_id)
        self.assertEqual(final_status['state'], 'completed')
        self.assertEqual(final_status['progress_percentage'], 100.0)
        self.assertGreater(final_status['completed_tasks'], 0)
        
        # Verify agent interaction
        self.mock_send_task.assert_called()
        
    def test_concurrent_workflows(self):
        """
        Test handling of multiple concurrent workflows.
        """
        # Configure mock response
        from agentic_sdlc.orchestration.models.agent import AgentResult, TaskOutput, DataFormat, ResultMetadata
        from agentic_sdlc.orchestration.models.communication import WorkflowInitiation
        
        # Mock MainAgent
        self.mock_process_request.return_value = WorkflowInitiation(
            request_id="mock-req-id-concurrent",
            should_proceed=True,
            workflow_type="general_workflow",
            estimated_complexity="low"
        )
        
        # Return a simple result immediately
        result = AgentResult(
            task_id="task-id",
            instance_id="instance-id",
            status=TaskStatus.COMPLETED,
            output=TaskOutput(data="Success"),
            metadata=ResultMetadata(execution_time=0.01)
        )
        future = Future()
        future.set_result(result)
        self.mock_send_task.return_value = future
        
        # Start multiple workflows
        num_workflows = 3
        for i in range(num_workflows):
            self.adapter._run_workflow(f"Task {i}")
            
        # Check executions (active or history)
        active_executions = self.adapter._orchestrator.get_active_executions()
        history_executions = self.adapter._orchestrator.execution_history
        total_executions = len(active_executions) + len(history_executions)
        
        self.assertEqual(total_executions, num_workflows)
        
        # Wait for all to complete if any active
        if active_executions:
            max_retries = 20
            for _ in range(max_retries):
                active = self.adapter._orchestrator.get_active_executions()
                if len(active) == 0:
                    break
                time.sleep(0.2)
            
        # Verify history
        self.assertEqual(len(self.adapter._orchestrator.execution_history), num_workflows)
        for execution in self.adapter._orchestrator.execution_history:
            self.assertEqual(execution.context.state.value, 'completed')

if __name__ == '__main__':
    unittest.main(verbosity=2)
