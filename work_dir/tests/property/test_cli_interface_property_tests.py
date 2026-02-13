"""
Property-based tests for CLIInterface

**Property 4: CLI Process Management and Multi-Instance Support**
**Validates: Requirements 4.1, 4.2, 4.3, 4.4, 4.5**

This module contains property-based tests that validate universal properties
of the CLIInterface's process spawning, lifecycle management, communication,
and multi-instance support capabilities.
"""

import unittest
import tempfile
import time
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, Any, List, Optional
from unittest.mock import Mock, patch, MagicMock

# Import the orchestration models and CLI interface
from agentic_sdlc.orchestration.interfaces.cli_interface import (
    CLIInterface, CommunicationProtocol, HeartbeatConfig, ProcessMetrics
)
from agentic_sdlc.orchestration.models import (
    AgentType, AgentConfig, AgentTask, AgentResult, AgentProcess,
    ProcessStatus, TaskStatus, ModelTier, TaskInput, TaskContext,
    TaskPriority, DataFormat, TaskRequirement, ResultMetadata, ResourceUsage,
    ModelAssignment
)
from agentic_sdlc.orchestration.exceptions.cli import (
    ProcessSpawnError, ProcessCommunicationError, ProcessTerminationError,
    ProcessNotFoundError
)

try:
    from hypothesis import given, strategies as st, settings, assume, HealthCheck
    from hypothesis.strategies import composite
    HYPOTHESIS_AVAILABLE = True
except ImportError:
    HYPOTHESIS_AVAILABLE = False
    # Fallback for when Hypothesis is not available
    def given(*args, **kwargs):
        def decorator(func):
            return func
        return decorator
    
    class MockStrategies:
        def text(self, **kwargs): return lambda: "test"
        def integers(self, **kwargs): return lambda: 1
        def floats(self, **kwargs): return lambda: 1.0
        def booleans(self): return lambda: True
        def lists(self, *args, **kwargs): return lambda: []
        def dictionaries(self, *args, **kwargs): return lambda: {}
        def one_of(self, *args): return lambda: args[0]() if args else lambda: None
        def just(self, value): return lambda: value
        def datetimes(self, **kwargs): return lambda: datetime.now()
    
    st = MockStrategies()
    
    def composite(func):
        return func
    
    def settings(**kwargs):
        def decorator(func):
            return func
        return decorator


# Hypothesis strategies for CLI interface testing

@composite
def agent_type_strategy(draw):
    """Strategy for generating AgentType values"""
    return draw(st.one_of([
        st.just(AgentType.PM),
        st.just(AgentType.BA),
        st.just(AgentType.SA),
        st.just(AgentType.RESEARCH),
        st.just(AgentType.QUALITY_JUDGE),
        st.just(AgentType.IMPLEMENTATION)
    ]))


@composite
def model_tier_strategy(draw):
    """Strategy for generating ModelTier values"""
    return draw(st.one_of([
        st.just(ModelTier.STRATEGIC),
        st.just(ModelTier.OPERATIONAL),
        st.just(ModelTier.RESEARCH)
    ]))


@composite
def process_status_strategy(draw):
    """Strategy for generating ProcessStatus values"""
    return draw(st.one_of([
        st.just(ProcessStatus.STARTING),
        st.just(ProcessStatus.IDLE),
        st.just(ProcessStatus.BUSY),
        st.just(ProcessStatus.ERROR),
        st.just(ProcessStatus.TERMINATED),
        st.just(ProcessStatus.UNRESPONSIVE)
    ]))


@composite
def task_priority_strategy(draw):
    """Strategy for generating TaskPriority values"""
    return draw(st.one_of([
        st.just(TaskPriority.CRITICAL),
        st.just(TaskPriority.HIGH),
        st.just(TaskPriority.MEDIUM),
        st.just(TaskPriority.LOW),
        st.just(TaskPriority.BACKGROUND)
    ]))


@composite
def communication_protocol_strategy(draw):
    """Strategy for generating CommunicationProtocol values"""
    return draw(st.one_of([
        st.just(CommunicationProtocol.JSON_STDIO),
        st.just(CommunicationProtocol.JSON_SOCKET),
        st.just(CommunicationProtocol.REST_API)
    ]))


@composite
def agent_config_strategy(draw):
    """Strategy for generating AgentConfig instances"""
    agent_type = draw(agent_type_strategy())
    model_tier = draw(model_tier_strategy())
    
    # Create a model assignment for the config
    model_assignment = ModelAssignment(
        role_type=agent_type,
        model_tier=model_tier,
        recommended_model=draw(st.text(min_size=5, max_size=20)),
        fallback_model=draw(st.text(min_size=5, max_size=20)),
        max_concurrent_instances=draw(st.integers(min_value=1, max_value=10)),
        cost_per_token=draw(st.floats(min_value=0.001, max_value=0.02))
    )
    
    return AgentConfig(
        agent_type=agent_type,
        model_assignment=model_assignment,
        max_retries=draw(st.integers(min_value=1, max_value=5)),
        timeout_minutes=draw(st.integers(min_value=5, max_value=60))
    )


@composite
def task_context_strategy(draw):
    """Strategy for generating TaskContext instances"""
    return TaskContext(
        workflow_id=draw(st.text(min_size=5, max_size=20)),
        phase=draw(st.text(min_size=3, max_size=15)),
        dependencies=draw(st.lists(st.text(min_size=3, max_size=10), max_size=5)),
        shared_data=draw(st.dictionaries(st.text(), st.text(), max_size=3)),
        constraints=draw(st.lists(st.text(min_size=3, max_size=20), max_size=3))
    )


@composite
def task_requirement_strategy(draw):
    """Strategy for generating TaskRequirement instances"""
    return TaskRequirement(
        requirement_id=draw(st.text(min_size=3, max_size=10)),
        description=draw(st.text(min_size=10, max_size=100)),
        is_mandatory=draw(st.booleans()),
        validation_criteria=draw(st.lists(st.text(min_size=5, max_size=50), max_size=3))
    )


@composite
def agent_task_strategy(draw):
    """Strategy for generating AgentTask instances"""
    task_types = ["analysis", "design", "implementation", "testing", "research", 
                  "quality_evaluation", "documentation", "architecture"]
    
    return AgentTask(
        type=draw(st.one_of([st.just(t) for t in task_types])),
        input=TaskInput(
            data=draw(st.dictionaries(st.text(), st.text(), max_size=5)),
            format=DataFormat.JSON
        ),
        context=draw(task_context_strategy()),
        requirements=draw(st.lists(task_requirement_strategy(), max_size=8)),
        priority=draw(task_priority_strategy()),
        deadline=draw(st.one_of([
            st.none(),
            st.datetimes(min_value=datetime.now(), max_value=datetime.now() + timedelta(days=30))
        ]))
    )


@composite
def heartbeat_config_strategy(draw):
    """Strategy for generating HeartbeatConfig instances"""
    return HeartbeatConfig(
        interval_seconds=draw(st.integers(min_value=1, max_value=60)),
        timeout_seconds=draw(st.integers(min_value=5, max_value=120)),
        max_missed_heartbeats=draw(st.integers(min_value=1, max_value=10)),
        enabled=draw(st.booleans())
    )


@composite
def agent_result_strategy(draw):
    """Strategy for generating AgentResult instances"""
    return AgentResult(
        task_id=draw(st.text(min_size=5, max_size=20)),
        instance_id=draw(st.text(min_size=5, max_size=20)),
        status=TaskStatus.COMPLETED,
        output=draw(st.dictionaries(st.text(), st.text(), max_size=5)),
        metadata=ResultMetadata(
            execution_time=draw(st.floats(min_value=0.1, max_value=300.0)),
            model_used=draw(st.text(min_size=5, max_size=20)),
            tokens_consumed=draw(st.integers(min_value=10, max_value=5000)),
            cost=draw(st.floats(min_value=0.001, max_value=1.0))
        ),
        confidence=draw(st.floats(min_value=0.0, max_value=1.0)),
        execution_time=draw(st.floats(min_value=0.1, max_value=300.0)),
        resources_used=ResourceUsage(
            cpu_time=draw(st.floats(min_value=0.1, max_value=60.0)),
            memory_peak=draw(st.integers(min_value=10, max_value=1000)),
            network_calls=draw(st.integers(min_value=0, max_value=50))
        )
    )


class TestCLIInterfaceProcessManagementProperties(unittest.TestCase):
    """
    Property-based tests for CLIInterface process management
    
    **Feature: multi-agent-orchestration, Property 4: CLI Process Management and Multi-Instance Support**
    
    *For any* triggered sub-agent, the CLI interface should spawn an independent process with unique 
    instance ID, enable autonomous operation across multiple concurrent instances, provide standardized 
    output formats, support state persistence and resumption per instance, and return structured 
    results to the orchestrator with proper load balancing.
    """
    
    def setUp(self):
        """Set up test fixtures"""
        if not HYPOTHESIS_AVAILABLE:
            self.skipTest("Hypothesis not available")
        
        # Create temporary directory for each test
        self.temp_dir = tempfile.TemporaryDirectory()
        self.temp_path = Path(self.temp_dir.name)
    
    def tearDown(self):
        """Clean up test fixtures"""
        self.temp_dir.cleanup()
    
    @given(
        agent_type=agent_type_strategy(),
        config=agent_config_strategy(),
        protocol=communication_protocol_strategy(),
        heartbeat_config=heartbeat_config_strategy()
    )
    @settings(max_examples=5, suppress_health_check=[HealthCheck.function_scoped_fixture])
    def test_process_spawning_creates_unique_instances(self, agent_type, config, protocol, heartbeat_config):
        """
        Property: Each spawned process must have a unique instance ID and process ID
        
        For any agent type and configuration, spawning multiple instances should:
        - Create unique process IDs for each instance
        - Create unique instance IDs for each instance
        - Maintain separate process handles
        - Track instances independently
        """
        # Skip unsupported protocols for now
        if protocol != CommunicationProtocol.JSON_STDIO:
            assume(False)
        
        # Disable heartbeat for testing to avoid threading issues
        heartbeat_config.enabled = False
        
        cli_interface = CLIInterface(
            working_directory=self.temp_path,
            protocol=protocol,
            heartbeat_config=heartbeat_config,
            max_concurrent_processes=10
        )
        
        spawned_processes = []
        
        try:
            with patch('subprocess.Popen') as mock_popen:
                # Mock successful process creation
                mock_process = Mock()
                mock_process.pid = 12345  # Will be incremented for each spawn
                mock_process.poll.return_value = None
                mock_process.stdin = Mock()
                mock_process.stdout = Mock()
                mock_process.stderr = Mock()
                mock_popen.return_value = mock_process
                
                with patch.object(cli_interface, '_wait_for_process_ready', return_value=True):
                    # Spawn multiple instances of the same agent type
                    for i in range(3):
                        mock_process.pid = 12345 + i  # Unique PID for each
                        instance_id = f"test-instance-{i}"
                        
                        agent_process = cli_interface.spawn_agent_instance(
                            agent_type, instance_id, config
                        )
                        spawned_processes.append(agent_process)
            
            # Verify uniqueness properties
            process_ids = [p.id for p in spawned_processes]
            instance_ids = [p.instance_id for p in spawned_processes]
            pids = [p.pid for p in spawned_processes]
            
            # All process IDs should be unique
            self.assertEqual(len(process_ids), len(set(process_ids)),
                           "All process IDs should be unique")
            
            # All instance IDs should be unique
            self.assertEqual(len(instance_ids), len(set(instance_ids)),
                           "All instance IDs should be unique")
            
            # All PIDs should be unique (in our mock)
            self.assertEqual(len(pids), len(set(pids)),
                           "All process PIDs should be unique")
            
            # All processes should be tracked in active_processes
            for process in spawned_processes:
                self.assertIn(process.id, cli_interface.active_processes,
                            f"Process {process.id} should be tracked in active_processes")
            
            # All processes should have correct agent type
            for process in spawned_processes:
                self.assertEqual(process.type, agent_type,
                               f"Process should have correct agent type {agent_type}")
        
        finally:
            cli_interface.cleanup()
    
    @given(
        agent_type=agent_type_strategy(),
        config=agent_config_strategy(),
        max_processes=st.integers(min_value=1, max_value=5)
    )
    @settings(max_examples=5, suppress_health_check=[HealthCheck.function_scoped_fixture])
    def test_capacity_limits_enforced(self, agent_type, config, max_processes):
        """
        Property: Process capacity limits must be strictly enforced
        
        For any capacity limit, the CLI interface should:
        - Allow spawning up to the limit
        - Reject spawning beyond the limit with appropriate error
        - Maintain accurate count of active processes
        """
        cli_interface = CLIInterface(
            working_directory=self.temp_path,
            max_concurrent_processes=max_processes,
            heartbeat_config=HeartbeatConfig(enabled=False)
        )
        
        spawned_processes = []
        
        try:
            with patch('subprocess.Popen') as mock_popen:
                mock_process = Mock()
                mock_process.pid = 12345
                mock_process.poll.return_value = None
                mock_process.stdin = Mock()
                mock_process.stdout = Mock()
                mock_process.stderr = Mock()
                mock_popen.return_value = mock_process
                
                with patch.object(cli_interface, '_wait_for_process_ready', return_value=True):
                    # Spawn processes up to the limit
                    for i in range(max_processes):
                        mock_process.pid = 12345 + i
                        instance_id = f"instance-{i}"
                        
                        agent_process = cli_interface.spawn_agent_instance(
                            agent_type, instance_id, config
                        )
                        spawned_processes.append(agent_process)
                    
                    # Verify we can spawn up to the limit
                    self.assertEqual(len(spawned_processes), max_processes,
                                   f"Should be able to spawn {max_processes} processes")
                    
                    # Attempt to spawn beyond the limit should fail
                    with self.assertRaises(ProcessSpawnError, 
                                         msg="Spawning beyond capacity should raise ProcessSpawnError"):
                        cli_interface.spawn_agent_instance(
                            agent_type, "overflow-instance", config
                        )
                    
                    # Active process count should match spawned count
                    self.assertEqual(len(cli_interface.active_processes), max_processes,
                                   f"Active process count should be {max_processes}")
        
        finally:
            cli_interface.cleanup()
    
    @given(
        agent_type=agent_type_strategy(),
        config=agent_config_strategy(),
        task=agent_task_strategy()
    )
    @settings(max_examples=5, suppress_health_check=[HealthCheck.function_scoped_fixture])
    def test_task_communication_maintains_isolation(self, agent_type, config, task):
        """
        Property: Task communication must maintain process isolation
        
        For any task sent to a process, the communication should:
        - Not interfere with other processes
        - Maintain task-to-process mapping
        - Return results from the correct process
        - Handle communication failures gracefully
        """
        cli_interface = CLIInterface(
            working_directory=self.temp_path,
            heartbeat_config=HeartbeatConfig(enabled=False),
            max_concurrent_processes=5
        )
        
        try:
            with patch('subprocess.Popen') as mock_popen:
                mock_process = Mock()
                mock_process.pid = 12345
                mock_process.poll.return_value = None
                mock_process.stdin = Mock()
                mock_process.stdout = Mock()
                mock_process.stderr = Mock()
                mock_popen.return_value = mock_process
                
                with patch.object(cli_interface, '_wait_for_process_ready', return_value=True):
                    # Spawn a process
                    agent_process = cli_interface.spawn_agent_instance(
                        agent_type, "test-instance", config
                    )
                
                # Mock successful task execution
                mock_result = AgentResult(
                    task_id=task.id,
                    instance_id=agent_process.instance_id,
                    status=TaskStatus.COMPLETED,
                    output={"result": "test output"},
                    metadata=ResultMetadata(
                        execution_time=1.0,
                        model_used="test-model",
                        tokens_consumed=100,
                        cost=0.01
                    ),
                    confidence=0.9,
                    execution_time=1.0,
                    resources_used=ResourceUsage(cpu_time=1.0, memory_peak=100, network_calls=1)
                )
                
                with patch.object(cli_interface, '_execute_task_sync', return_value=mock_result):
                    # Send task to the process
                    future = cli_interface.send_task(agent_process.id, task)
                    result = future.result(timeout=1)
                    
                    # Verify result properties
                    self.assertEqual(result.task_id, task.id,
                                   "Result should have correct task ID")
                    self.assertEqual(result.instance_id, agent_process.instance_id,
                                   "Result should have correct instance ID")
                    self.assertEqual(result.status, TaskStatus.COMPLETED,
                                   "Result should have completed status")
                    
                    # Verify process state after task
                    process_status = cli_interface.get_process_status(agent_process.id)
                    self.assertEqual(process_status["status"], ProcessStatus.IDLE.value,
                                   "Process should return to IDLE after task completion")
        
        finally:
            cli_interface.cleanup()
    
    @given(
        agent_type=agent_type_strategy(),
        config=agent_config_strategy(),
        target_instances=st.integers(min_value=1, max_value=5)
    )
    @settings(max_examples=5, suppress_health_check=[HealthCheck.function_scoped_fixture])
    def test_scaling_operations_maintain_consistency(self, agent_type, config, target_instances):
        """
        Property: Scaling operations must maintain system consistency
        
        For any scaling operation, the system should:
        - Accurately track the number of instances
        - Maintain process state consistency
        - Handle scaling up and down correctly
        - Preserve existing processes when possible
        """
        cli_interface = CLIInterface(
            working_directory=self.temp_path,
            heartbeat_config=HeartbeatConfig(enabled=False),
            max_concurrent_processes=10
        )
        
        try:
            with patch('subprocess.Popen') as mock_popen:
                mock_process = Mock()
                mock_process.pid = 12345
                mock_process.poll.return_value = None
                mock_process.stdin = Mock()
                mock_process.stdout = Mock()
                mock_process.stderr = Mock()
                mock_process.wait = Mock()
                mock_popen.return_value = mock_process
                
                with patch.object(cli_interface, '_wait_for_process_ready', return_value=True):
                    # Initial scaling up
                    process_ids = cli_interface.scale_agent_pool(agent_type, target_instances)
                    
                    # Verify scaling up results
                    self.assertEqual(len(process_ids), target_instances,
                                   f"Should have {target_instances} processes after scaling up")
                    
                    # All returned process IDs should exist in active processes
                    for process_id in process_ids:
                        self.assertIn(process_id, cli_interface.active_processes,
                                    f"Process {process_id} should exist in active processes")
                    
                    # All processes should have correct agent type
                    for process_id in process_ids:
                        process = cli_interface.active_processes[process_id]
                        self.assertEqual(process.type, agent_type,
                                       f"Process should have correct agent type {agent_type}")
                    
                    # Test scaling down if we have more than 1 instance
                    if target_instances > 1:
                        new_target = max(1, target_instances - 1)
                        new_process_ids = cli_interface.scale_agent_pool(agent_type, new_target)
                        
                        # Verify scaling down results
                        self.assertEqual(len(new_process_ids), new_target,
                                       f"Should have {new_target} processes after scaling down")
                        
                        # Remaining processes should be a subset of original processes
                        self.assertTrue(set(new_process_ids).issubset(set(process_ids)),
                                      "Remaining processes should be subset of original processes")
                        
                        # Total active processes should match new target
                        agent_processes = [
                            pid for pid, process in cli_interface.active_processes.items()
                            if process.type == agent_type
                        ]
                        self.assertEqual(len(agent_processes), new_target,
                                       f"Should have {new_target} active processes of type {agent_type}")
        
        finally:
            cli_interface.cleanup()
    
    @given(
        agent_type=agent_type_strategy(),
        config=agent_config_strategy()
    )
    @settings(max_examples=5, suppress_health_check=[HealthCheck.function_scoped_fixture])
    def test_process_termination_cleanup_complete(self, agent_type, config):
        """
        Property: Process termination must completely clean up resources
        
        For any terminated process, the system should:
        - Remove process from active processes
        - Clean up all associated resources
        - Handle graceful and forced termination
        - Maintain system stability after termination
        """
        cli_interface = CLIInterface(
            working_directory=self.temp_path,
            heartbeat_config=HeartbeatConfig(enabled=False),
            max_concurrent_processes=5
        )
        
        try:
            with patch('subprocess.Popen') as mock_popen:
                mock_process = Mock()
                mock_process.pid = 12345
                mock_process.poll.return_value = None
                mock_process.stdin = Mock()
                mock_process.stdout = Mock()
                mock_process.stderr = Mock()
                mock_process.wait = Mock()
                mock_popen.return_value = mock_process
                
                with patch.object(cli_interface, '_wait_for_process_ready', return_value=True):
                    # Spawn a process
                    agent_process = cli_interface.spawn_agent_instance(
                        agent_type, "test-instance", config
                    )
                    
                    process_id = agent_process.id
                    
                    # Verify process exists before termination
                    self.assertIn(process_id, cli_interface.active_processes,
                                "Process should exist before termination")
                    self.assertIn(process_id, cli_interface.process_metrics,
                                "Process metrics should exist before termination")
                    self.assertIn(process_id, cli_interface.process_locks,
                                "Process locks should exist before termination")
                    
                    # Terminate the process
                    result = cli_interface.terminate_agent(process_id)
                    
                    # Verify termination success
                    self.assertTrue(result, "Termination should return True on success")
                    
                    # Verify complete cleanup
                    self.assertNotIn(process_id, cli_interface.active_processes,
                                   "Process should be removed from active processes")
                    self.assertNotIn(process_id, cli_interface.process_metrics,
                                   "Process metrics should be cleaned up")
                    self.assertNotIn(process_id, cli_interface.process_locks,
                                   "Process locks should be cleaned up")
                    self.assertNotIn(process_id, cli_interface.task_queues,
                                   "Task queues should be cleaned up")
                    self.assertNotIn(process_id, cli_interface.result_queues,
                                   "Result queues should be cleaned up")
                    
                    # Verify system stability - should be able to spawn new process
                    with patch.object(cli_interface, '_wait_for_process_ready', return_value=True):
                        new_process = cli_interface.spawn_agent_instance(
                            agent_type, "new-instance", config
                        )
                        self.assertIsNotNone(new_process,
                                           "Should be able to spawn new process after termination")
        
        finally:
            cli_interface.cleanup()
    
    @given(
        agent_type=agent_type_strategy(),
        config=agent_config_strategy(),
        tasks=st.lists(agent_task_strategy(), min_size=1, max_size=3)
    )
    @settings(max_examples=10, suppress_health_check=[HealthCheck.function_scoped_fixture])
    def test_concurrent_task_execution_isolation(self, agent_type, config, tasks):
        """
        Property: Concurrent task execution must maintain isolation
        
        For any set of concurrent tasks, the system should:
        - Execute tasks independently across instances
        - Maintain task-to-instance mapping
        - Handle concurrent communication correctly
        - Preserve task ordering per instance
        """
        cli_interface = CLIInterface(
            working_directory=self.temp_path,
            heartbeat_config=HeartbeatConfig(enabled=False),
            max_concurrent_processes=10
        )
        
        try:
            with patch('subprocess.Popen') as mock_popen:
                mock_process = Mock()
                mock_process.pid = 12345
                mock_process.poll.return_value = None
                mock_process.stdin = Mock()
                mock_process.stdout = Mock()
                mock_process.stderr = Mock()
                mock_popen.return_value = mock_process
                
                # Spawn multiple processes
                processes = []
                with patch.object(cli_interface, '_wait_for_process_ready', return_value=True):
                    for i in range(min(len(tasks), 3)):  # Limit to 3 processes
                        mock_process.pid = 12345 + i
                        agent_process = cli_interface.spawn_agent_instance(
                            agent_type, f"instance-{i}", config
                        )
                        processes.append(agent_process)
                
                # Mock task execution results
                def mock_execute_task(process_id, task):
                    return AgentResult(
                        task_id=task.id,
                        instance_id=cli_interface.active_processes[process_id].instance_id,
                        status=TaskStatus.COMPLETED,
                        output={"result": f"output-{task.id}"},
                        metadata=ResultMetadata(
                            execution_time=1.0,
                            model_used="test-model",
                            tokens_consumed=100,
                            cost=0.01
                        ),
                        confidence=0.9,
                        execution_time=1.0,
                        resources_used=ResourceUsage(cpu_time=1.0, memory_peak=100, network_calls=1)
                    )
                
                with patch.object(cli_interface, '_execute_task_sync', side_effect=mock_execute_task):
                    # Send tasks to different processes
                    futures = []
                    task_to_process = {}
                    
                    for i, task in enumerate(tasks):
                        process = processes[i % len(processes)]
                        future = cli_interface.send_task(process.id, task)
                        futures.append(future)
                        task_to_process[task.id] = process.instance_id
                    
                    # Collect results
                    results = []
                    for future in futures:
                        result = future.result(timeout=2)
                        results.append(result)
                    
                    # Verify isolation properties
                    self.assertEqual(len(results), len(tasks),
                                   "Should receive result for each task")
                    
                    # Verify task-to-instance mapping
                    for result in results:
                        expected_instance = task_to_process[result.task_id]
                        self.assertEqual(result.instance_id, expected_instance,
                                       f"Result should come from correct instance for task {result.task_id}")
                    
                    # Verify all tasks completed successfully
                    for result in results:
                        self.assertEqual(result.status, TaskStatus.COMPLETED,
                                       f"Task {result.task_id} should complete successfully")
        
        finally:
            cli_interface.cleanup()


class TestCLIInterfaceStateManagementProperties(unittest.TestCase):
    """Test state management properties of CLI interface"""
    
    def setUp(self):
        """Set up test fixtures"""
        if not HYPOTHESIS_AVAILABLE:
            self.skipTest("Hypothesis not available")
        
        self.temp_dir = tempfile.TemporaryDirectory()
        self.temp_path = Path(self.temp_dir.name)
    
    def tearDown(self):
        """Clean up test fixtures"""
        self.temp_dir.cleanup()
    
    @given(
        agent_type=agent_type_strategy(),
        config=agent_config_strategy()
    )
    @settings(max_examples=5, suppress_health_check=[HealthCheck.function_scoped_fixture])
    def test_process_status_accuracy(self, agent_type, config):
        """
        Property: Process status information must be accurate and consistent
        
        For any process, the status information should:
        - Reflect the actual process state
        - Include all required metadata
        - Be consistent across multiple queries
        - Update correctly with state changes
        """
        cli_interface = CLIInterface(
            working_directory=self.temp_path,
            heartbeat_config=HeartbeatConfig(enabled=False)
        )
        
        try:
            with patch('subprocess.Popen') as mock_popen:
                mock_process = Mock()
                mock_process.pid = 12345
                mock_process.poll.return_value = None
                mock_process.stdin = Mock()
                mock_process.stdout = Mock()
                mock_process.stderr = Mock()
                mock_popen.return_value = mock_process
                
                with patch.object(cli_interface, '_wait_for_process_ready', return_value=True):
                    # Spawn process
                    agent_process = cli_interface.spawn_agent_instance(
                        agent_type, "test-instance", config
                    )
                    
                    # Get initial status
                    status1 = cli_interface.get_process_status(agent_process.id)
                    
                    # Verify required fields exist
                    required_fields = [
                        "process_id", "instance_id", "agent_type", "status", 
                        "pid", "start_time", "last_activity", "current_load", 
                        "current_task", "metrics"
                    ]
                    
                    for field in required_fields:
                        self.assertIn(field, status1, f"Status should include {field}")
                    
                    # Verify field types and values
                    self.assertEqual(status1["process_id"], agent_process.id)
                    self.assertEqual(status1["instance_id"], agent_process.instance_id)
                    self.assertEqual(status1["agent_type"], agent_type.value)
                    self.assertEqual(status1["status"], ProcessStatus.IDLE.value)
                    self.assertEqual(status1["pid"], 12345)
                    self.assertIsNone(status1["current_task"])
                    
                    # Verify metrics structure
                    metrics = status1["metrics"]
                    metric_fields = [
                        "cpu_usage", "memory_usage", "response_time", 
                        "success_rate", "error_count", "last_heartbeat"
                    ]
                    
                    for field in metric_fields:
                        self.assertIn(field, metrics, f"Metrics should include {field}")
                    
                    # Get status again - should be consistent
                    status2 = cli_interface.get_process_status(agent_process.id)
                    
                    # Core fields should remain the same
                    self.assertEqual(status1["process_id"], status2["process_id"])
                    self.assertEqual(status1["instance_id"], status2["instance_id"])
                    self.assertEqual(status1["agent_type"], status2["agent_type"])
                    self.assertEqual(status1["pid"], status2["pid"])
        
        finally:
            cli_interface.cleanup()
    
    @given(
        processes_data=st.lists(
            st.tuples(agent_type_strategy(), agent_config_strategy()),
            min_size=1, max_size=3
        )
    )
    @settings(max_examples=10, suppress_health_check=[HealthCheck.function_scoped_fixture])
    def test_bulk_operations_consistency(self, processes_data):
        """
        Property: Bulk operations must maintain consistency across all processes
        
        For any set of processes, bulk operations should:
        - Return accurate information for all processes
        - Maintain consistency during concurrent operations
        - Handle mixed process states correctly
        """
        cli_interface = CLIInterface(
            working_directory=self.temp_path,
            heartbeat_config=HeartbeatConfig(enabled=False),
            max_concurrent_processes=10
        )
        
        try:
            with patch('subprocess.Popen') as mock_popen:
                mock_process = Mock()
                mock_process.pid = 12345
                mock_process.poll.return_value = None
                mock_process.stdin = Mock()
                mock_process.stdout = Mock()
                mock_process.stderr = Mock()
                mock_popen.return_value = mock_process
                
                # Spawn multiple processes
                spawned_processes = []
                with patch.object(cli_interface, '_wait_for_process_ready', return_value=True):
                    for i, (agent_type, config) in enumerate(processes_data):
                        mock_process.pid = 12345 + i
                        agent_process = cli_interface.spawn_agent_instance(
                            agent_type, f"instance-{i}", config
                        )
                        spawned_processes.append(agent_process)
                
                # Get all processes status
                all_statuses = cli_interface.get_all_processes()
                
                # Verify bulk operation results
                self.assertEqual(len(all_statuses), len(spawned_processes),
                               "Should return status for all spawned processes")
                
                # Verify each status contains required information
                process_ids_from_status = {status["process_id"] for status in all_statuses}
                expected_process_ids = {process.id for process in spawned_processes}
                
                self.assertEqual(process_ids_from_status, expected_process_ids,
                               "Bulk status should include all spawned process IDs")
                
                # Verify individual status consistency
                for status in all_statuses:
                    individual_status = cli_interface.get_process_status(status["process_id"])
                    
                    # Key fields should match
                    self.assertEqual(status["process_id"], individual_status["process_id"])
                    self.assertEqual(status["instance_id"], individual_status["instance_id"])
                    self.assertEqual(status["agent_type"], individual_status["agent_type"])
                    self.assertEqual(status["status"], individual_status["status"])
        
        finally:
            cli_interface.cleanup()


if __name__ == "__main__":
    # Configure Hypothesis for property-based testing
    if HYPOTHESIS_AVAILABLE:
        import os
        profile = os.getenv("HYPOTHESIS_PROFILE", "default")
        if profile == "ci":
            settings.register_profile("ci", max_examples=100, deadline=None)
        else:
            settings.register_profile("default", max_examples=30, deadline=None)
        settings.load_profile(profile)
    
    unittest.main()