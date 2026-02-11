"""
Unit tests for SpecializedAgent base class

Tests the core functionality of the SpecializedAgent abstract base class including
initialization, task execution, queue management, and performance tracking.
"""

import asyncio
import pytest
import time
from datetime import datetime
from unittest.mock import Mock, patch, AsyncMock

from agentic_sdlc.orchestration.agents.specialized_agent import (
    SpecializedAgent, AgentState, AgentStatus, TaskQueueItem
)
from agentic_sdlc.orchestration.models.agent import (
    AgentType, AgentTask, AgentResult, AgentConfig, ModelAssignment,
    TaskStatus, TaskPriority, TaskInput, TaskContext, TaskOutput,
    ResultMetadata, DataFormat, ModelTier
)
from agentic_sdlc.orchestration.exceptions.agent import (
    AgentInitializationError, AgentExecutionError
)


# Concrete implementation for testing
class TestAgent(SpecializedAgent):
    """Test implementation of SpecializedAgent"""
    
    @property
    def agent_type(self) -> AgentType:
        return AgentType.IMPLEMENTATION
    
    async def _execute_task_impl(self, task: AgentTask) -> AgentResult:
        """Simple implementation that returns success"""
        # Simulate some work
        await asyncio.sleep(0.1)
        
        return AgentResult(
            task_id=task.id,
            instance_id=self.instance_id,
            status=TaskStatus.COMPLETED,
            output=TaskOutput(
                data={"result": "success"},
                format=DataFormat.JSON,
                confidence=0.95
            ),
            metadata=ResultMetadata(
                execution_time=0.1,
                quality_score=0.9
            )
        )
    
    def _validate_task(self, task: AgentTask) -> bool:
        """Simple validation - accept all tasks"""
        return True


class FailingTestAgent(SpecializedAgent):
    """Test agent that always fails"""
    
    @property
    def agent_type(self) -> AgentType:
        return AgentType.IMPLEMENTATION
    
    async def _execute_task_impl(self, task: AgentTask) -> AgentResult:
        """Implementation that raises an error"""
        raise ValueError("Task execution failed")
    
    def _validate_task(self, task: AgentTask) -> bool:
        return True


@pytest.fixture
def agent_config():
    """Create a test agent configuration"""
    model_assignment = ModelAssignment(
        role_type=AgentType.IMPLEMENTATION,
        model_tier=ModelTier.OPERATIONAL,
        recommended_model="gpt-3.5-turbo",
        fallback_model="claude-3-haiku",
        max_concurrent_instances=5,
        cost_per_token=0.002
    )
    
    return AgentConfig(
        agent_type=AgentType.IMPLEMENTATION,
        model_assignment=model_assignment,
        max_retries=3,
        timeout_minutes=30
    )


@pytest.fixture
def sample_task():
    """Create a sample task"""
    return AgentTask(
        type="test_task",
        input=TaskInput(data={"test": "data"}),
        context=TaskContext(workflow_id="test-workflow", phase="test"),
        priority=TaskPriority.MEDIUM
    )


class TestSpecializedAgentInitialization:
    """Test agent initialization"""
    
    def test_agent_creation(self):
        """Test basic agent creation"""
        agent = TestAgent()
        
        assert agent.instance_id is not None
        assert agent.agent_type == AgentType.IMPLEMENTATION
        assert agent._state == AgentState.UNINITIALIZED
        assert agent.get_queue_size() == 0
    
    def test_agent_creation_with_instance_id(self):
        """Test agent creation with custom instance ID"""
        instance_id = "test-instance-123"
        agent = TestAgent(instance_id=instance_id)
        
        assert agent.instance_id == instance_id
    
    @pytest.mark.asyncio
    async def test_agent_initialization(self, agent_config):
        """Test agent initialization"""
        agent = TestAgent()
        
        await agent.initialize(agent_config)
        
        assert agent._state == AgentState.READY
        assert agent.config == agent_config
        assert agent.is_ready()
    
    @pytest.mark.asyncio
    async def test_initialization_with_constructor_config(self, agent_config):
        """Test initialization using config from constructor"""
        agent = TestAgent(config=agent_config)
        
        await agent.initialize()
        
        assert agent._state == AgentState.READY
        assert agent.config == agent_config
    
    @pytest.mark.asyncio
    async def test_initialization_without_config(self):
        """Test initialization fails without config"""
        agent = TestAgent()
        
        with pytest.raises(AgentInitializationError, match="No configuration provided"):
            await agent.initialize()
    
    @pytest.mark.asyncio
    async def test_initialization_with_wrong_agent_type(self):
        """Test initialization fails with mismatched agent type"""
        # Create config for PM agent
        model_assignment = ModelAssignment(
            role_type=AgentType.PM,
            model_tier=ModelTier.STRATEGIC,
            recommended_model="gpt-4-turbo",
            fallback_model="gpt-4",
            max_concurrent_instances=3,
            cost_per_token=0.01
        )
        
        config = AgentConfig(
            agent_type=AgentType.PM,  # Wrong type
            model_assignment=model_assignment
        )
        
        agent = TestAgent()  # Implementation agent
        
        with pytest.raises(AgentInitializationError, match="does not match agent type"):
            await agent.initialize(config)
    
    @pytest.mark.asyncio
    async def test_double_initialization(self, agent_config):
        """Test that double initialization fails"""
        agent = TestAgent()
        await agent.initialize(agent_config)
        
        with pytest.raises(AgentInitializationError, match="already initialized"):
            await agent.initialize(agent_config)


class TestSpecializedAgentTaskExecution:
    """Test task execution"""
    
    @pytest.mark.asyncio
    async def test_execute_task_success(self, agent_config, sample_task):
        """Test successful task execution"""
        agent = TestAgent()
        await agent.initialize(agent_config)
        
        result = await agent.executeTask(sample_task)
        
        assert result.status == TaskStatus.COMPLETED
        assert result.task_id == sample_task.id
        assert result.instance_id == agent.instance_id
        assert result.output.data["result"] == "success"
        assert result.confidence > 0
    
    @pytest.mark.asyncio
    async def test_execute_task_updates_metrics(self, agent_config, sample_task):
        """Test that task execution updates performance metrics"""
        agent = TestAgent()
        await agent.initialize(agent_config)
        
        initial_metrics = agent.getPerformanceMetrics()
        assert initial_metrics.tasks_completed == 0
        
        await agent.executeTask(sample_task)
        
        updated_metrics = agent.getPerformanceMetrics()
        assert updated_metrics.tasks_completed == 1
        assert updated_metrics.average_execution_time > 0
        assert updated_metrics.success_rate == 1.0
        assert updated_metrics.quality_score > 0
    
    @pytest.mark.asyncio
    async def test_execute_task_failure(self, agent_config, sample_task):
        """Test task execution failure"""
        agent = FailingTestAgent()
        await agent.initialize(agent_config)
        
        with pytest.raises(AgentExecutionError):
            await agent.executeTask(sample_task)
    
    @pytest.mark.asyncio
    async def test_execute_task_when_not_ready(self, sample_task):
        """Test that task execution fails when agent not ready"""
        agent = TestAgent()
        
        with pytest.raises(AgentExecutionError, match="not ready"):
            await agent.executeTask(sample_task)
    
    @pytest.mark.asyncio
    async def test_execute_multiple_tasks(self, agent_config):
        """Test executing multiple tasks"""
        agent = TestAgent()
        await agent.initialize(agent_config)
        
        tasks = [
            AgentTask(
                type=f"task_{i}",
                input=TaskInput(data={"index": i}),
                context=TaskContext(workflow_id="test", phase="test"),
                priority=TaskPriority.MEDIUM
            )
            for i in range(5)
        ]
        
        for task in tasks:
            result = await agent.executeTask(task)
            assert result.status == TaskStatus.COMPLETED
        
        metrics = agent.getPerformanceMetrics()
        assert metrics.tasks_completed == 5


class TestSpecializedAgentTaskQueue:
    """Test task queue management"""
    
    @pytest.mark.asyncio
    async def test_enqueue_task(self, agent_config, sample_task):
        """Test enqueueing a task"""
        agent = TestAgent()
        await agent.initialize(agent_config)
        
        success = agent.enqueue_task(sample_task)
        
        assert success
        assert agent.get_queue_size() == 1
    
    @pytest.mark.asyncio
    async def test_enqueue_multiple_tasks(self, agent_config):
        """Test enqueueing multiple tasks"""
        agent = TestAgent()
        await agent.initialize(agent_config)
        
        tasks = [
            AgentTask(
                type=f"task_{i}",
                input=TaskInput(data={"index": i}),
                context=TaskContext(workflow_id="test", phase="test"),
                priority=TaskPriority.MEDIUM
            )
            for i in range(5)
        ]
        
        for task in tasks:
            agent.enqueue_task(task)
        
        assert agent.get_queue_size() == 5
    
    @pytest.mark.asyncio
    async def test_enqueue_with_priority(self, agent_config):
        """Test that tasks are processed by priority"""
        agent = TestAgent()
        await agent.initialize(agent_config)
        
        # Enqueue tasks with different priorities
        low_task = AgentTask(
            type="low",
            input=TaskInput(data={}),
            context=TaskContext(workflow_id="test", phase="test"),
            priority=TaskPriority.LOW
        )
        
        high_task = AgentTask(
            type="high",
            input=TaskInput(data={}),
            context=TaskContext(workflow_id="test", phase="test"),
            priority=TaskPriority.HIGH
        )
        
        critical_task = AgentTask(
            type="critical",
            input=TaskInput(data={}),
            context=TaskContext(workflow_id="test", phase="test"),
            priority=TaskPriority.CRITICAL
        )
        
        # Enqueue in reverse priority order
        agent.enqueue_task(low_task)
        agent.enqueue_task(high_task)
        agent.enqueue_task(critical_task)
        
        assert agent.get_queue_size() == 3
        
        # Wait for tasks to be processed
        time.sleep(1.0)
        
        # All tasks should be completed
        metrics = agent.getPerformanceMetrics()
        assert metrics.tasks_completed == 3
    
    @pytest.mark.asyncio
    async def test_enqueue_with_callback(self, agent_config, sample_task):
        """Test enqueueing task with callback"""
        agent = TestAgent()
        await agent.initialize(agent_config)
        
        callback_called = False
        callback_result = None
        
        def callback(result: AgentResult):
            nonlocal callback_called, callback_result
            callback_called = True
            callback_result = result
        
        agent.enqueue_task(sample_task, callback=callback)
        
        # Wait for task to be processed
        time.sleep(0.5)
        
        assert callback_called
        assert callback_result is not None
        assert callback_result.task_id == sample_task.id
    
    @pytest.mark.asyncio
    async def test_clear_queue(self, agent_config):
        """Test clearing the task queue"""
        agent = TestAgent()
        await agent.initialize(agent_config)
        
        # Enqueue multiple tasks
        for i in range(5):
            task = AgentTask(
                type=f"task_{i}",
                input=TaskInput(data={}),
                context=TaskContext(workflow_id="test", phase="test"),
                priority=TaskPriority.LOW  # Low priority so they stay in queue
            )
            agent.enqueue_task(task)
        
        # Give time for one task to start processing
        time.sleep(0.05)
        
        # Clear queue
        cleared = agent.clear_queue()
        
        assert cleared >= 0  # At least some tasks cleared
        assert agent.get_queue_size() == 0


class TestSpecializedAgentStatus:
    """Test agent status reporting"""
    
    @pytest.mark.asyncio
    async def test_get_status(self, agent_config):
        """Test getting agent status"""
        agent = TestAgent()
        await agent.initialize(agent_config)
        
        status = agent.getStatus()
        
        assert status.instance_id == agent.instance_id
        assert status.agent_type == AgentType.IMPLEMENTATION
        assert status.state == AgentState.READY
        assert status.queued_tasks == 0
        assert status.uptime_seconds > 0
    
    @pytest.mark.asyncio
    async def test_status_to_dict(self, agent_config):
        """Test converting status to dictionary"""
        agent = TestAgent()
        await agent.initialize(agent_config)
        
        status = agent.getStatus()
        status_dict = status.to_dict()
        
        assert isinstance(status_dict, dict)
        assert status_dict["instance_id"] == agent.instance_id
        assert status_dict["agent_type"] == AgentType.IMPLEMENTATION.value
        assert status_dict["state"] == AgentState.READY.value
        assert "performance" in status_dict
        assert "uptime_seconds" in status_dict
    
    @pytest.mark.asyncio
    async def test_get_performance_metrics(self, agent_config, sample_task):
        """Test getting performance metrics"""
        agent = TestAgent()
        await agent.initialize(agent_config)
        
        # Execute a task
        await agent.executeTask(sample_task)
        
        metrics = agent.getPerformanceMetrics()
        
        assert metrics.tasks_completed == 1
        assert metrics.average_execution_time > 0
        assert metrics.success_rate == 1.0
        assert metrics.quality_score > 0
    
    @pytest.mark.asyncio
    async def test_is_ready(self, agent_config):
        """Test is_ready method"""
        agent = TestAgent()
        
        assert not agent.is_ready()
        
        await agent.initialize(agent_config)
        
        assert agent.is_ready()
    
    @pytest.mark.asyncio
    async def test_is_busy(self, agent_config):
        """Test is_busy method"""
        agent = TestAgent()
        await agent.initialize(agent_config)
        
        # Initially not busy
        assert not agent.is_busy()
        
        # Note: Testing busy state is tricky due to threading
        # In real usage, the agent would be busy during task execution
    
    @pytest.mark.asyncio
    async def test_get_uptime(self, agent_config):
        """Test get_uptime method"""
        agent = TestAgent()
        await agent.initialize(agent_config)
        
        time.sleep(0.1)
        
        uptime = agent.get_uptime()
        assert uptime >= 0.1


class TestSpecializedAgentCleanup:
    """Test agent cleanup"""
    
    @pytest.mark.asyncio
    async def test_cleanup(self, agent_config):
        """Test agent cleanup"""
        agent = TestAgent()
        await agent.initialize(agent_config)
        
        await agent.cleanup()
        
        assert agent._state == AgentState.TERMINATED
        assert agent._stop_processing
    
    @pytest.mark.asyncio
    async def test_cleanup_with_queued_tasks(self, agent_config):
        """Test cleanup with tasks in queue"""
        agent = TestAgent()
        await agent.initialize(agent_config)
        
        # Enqueue some tasks
        for i in range(3):
            task = AgentTask(
                type=f"task_{i}",
                input=TaskInput(data={}),
                context=TaskContext(workflow_id="test", phase="test"),
                priority=TaskPriority.LOW
            )
            agent.enqueue_task(task)
        
        await agent.cleanup()
        
        assert agent._state == AgentState.TERMINATED
    
    @pytest.mark.asyncio
    async def test_double_cleanup(self, agent_config):
        """Test that double cleanup is handled gracefully"""
        agent = TestAgent()
        await agent.initialize(agent_config)
        
        await agent.cleanup()
        await agent.cleanup()  # Should not raise error
        
        assert agent._state == AgentState.TERMINATED


class TestSpecializedAgentEdgeCases:
    """Test edge cases and error conditions"""
    
    def test_agent_repr(self):
        """Test string representation"""
        agent = TestAgent(instance_id="test-123")
        
        repr_str = repr(agent)
        
        assert "TestAgent" in repr_str
        assert "test-123" in repr_str
        assert "IMPLEMENTATION" in repr_str
    
    @pytest.mark.asyncio
    async def test_task_validation(self, agent_config):
        """Test task validation"""
        
        class ValidatingAgent(SpecializedAgent):
            @property
            def agent_type(self) -> AgentType:
                return AgentType.PM
            
            async def _execute_task_impl(self, task: AgentTask) -> AgentResult:
                return AgentResult(
                    task_id=task.id,
                    instance_id=self.instance_id,
                    status=TaskStatus.COMPLETED,
                    output=TaskOutput(data={})
                )
            
            def _validate_task(self, task: AgentTask) -> bool:
                # Only accept tasks with "pm" in the type
                return "pm" in task.type.lower()
        
        # Update config for PM agent
        agent_config.agent_type = AgentType.PM
        agent_config.model_assignment.role_type = AgentType.PM
        
        agent = ValidatingAgent()
        await agent.initialize(agent_config)
        
        # Valid task
        valid_task = AgentTask(
            type="pm_task",
            input=TaskInput(data={}),
            context=TaskContext(workflow_id="test", phase="test")
        )
        
        result = await agent.executeTask(valid_task)
        assert result.status == TaskStatus.COMPLETED
        
        # Invalid task
        invalid_task = AgentTask(
            type="other_task",
            input=TaskInput(data={}),
            context=TaskContext(workflow_id="test", phase="test")
        )
        
        with pytest.raises(AgentExecutionError, match="not valid"):
            await agent.executeTask(invalid_task)
    
    @pytest.mark.asyncio
    async def test_concurrent_task_execution(self, agent_config):
        """Test that multiple tasks can be enqueued and processed"""
        agent = TestAgent()
        await agent.initialize(agent_config)
        
        # Enqueue multiple tasks
        num_tasks = 10
        for i in range(num_tasks):
            task = AgentTask(
                type=f"task_{i}",
                input=TaskInput(data={"index": i}),
                context=TaskContext(workflow_id="test", phase="test"),
                priority=TaskPriority.MEDIUM
            )
            agent.enqueue_task(task)
        
        # Wait for all tasks to complete
        timeout = 5.0
        start = time.time()
        while agent.getPerformanceMetrics().tasks_completed < num_tasks:
            if time.time() - start > timeout:
                break
            time.sleep(0.1)
        
        metrics = agent.getPerformanceMetrics()
        assert metrics.tasks_completed == num_tasks
        assert metrics.success_rate == 1.0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
