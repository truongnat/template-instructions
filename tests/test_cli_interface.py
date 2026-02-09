"""
Unit tests for CLIInterface

Tests the CLI interface for agent process management, including process spawning,
communication, monitoring, and termination capabilities.
"""

import pytest
import tempfile
import time
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime

from agentic_sdlc.orchestration.interfaces.cli_interface import (
    CLIInterface, CommunicationProtocol, HeartbeatConfig, ProcessMetrics
)
from agentic_sdlc.orchestration.models import (
    AgentType, AgentConfig, AgentTask, TaskInput, TaskContext, TaskPriority,
    ModelTier, ProcessStatus, DataFormat
)
from agentic_sdlc.orchestration.exceptions.cli import (
    ProcessSpawnError, ProcessCommunicationError, ProcessTerminationError,
    ProcessNotFoundError
)


class TestCLIInterface:
    """Test cases for CLIInterface"""
    
    @pytest.fixture
    def temp_dir(self):
        """Create temporary directory for testing"""
        with tempfile.TemporaryDirectory() as temp_dir:
            yield Path(temp_dir)
    
    @pytest.fixture
    def cli_interface(self, temp_dir):
        """Create CLIInterface instance for testing"""
        heartbeat_config = HeartbeatConfig(
            interval_seconds=1,
            timeout_seconds=2,
            max_missed_heartbeats=2,
            enabled=False  # Disable for testing
        )
        
        return CLIInterface(
            base_command="python",
            working_directory=temp_dir,
            protocol=CommunicationProtocol.JSON_STDIO,
            heartbeat_config=heartbeat_config,
            max_concurrent_processes=5
        )
    
    @pytest.fixture
    def sample_config(self):
        """Create sample agent configuration"""
        return AgentConfig(
            agent_type=AgentType.PM,
            model_tier=ModelTier.STRATEGIC,
            model_name="gpt-4",
            max_tokens=2000,
            temperature=0.7
        )
    
    @pytest.fixture
    def sample_task(self):
        """Create sample agent task"""
        return AgentTask(
            type="analysis",
            input=TaskInput(
                data={"requirement": "Analyze user authentication flow"},
                format=DataFormat.JSON
            ),
            context=TaskContext(workflow_id="test-workflow", phase="analysis"),
            priority=TaskPriority.HIGH
        )
    
    def test_cli_interface_initialization(self, temp_dir):
        """Test CLIInterface initialization"""
        cli = CLIInterface(working_directory=temp_dir)
        
        assert cli.base_command == "python"
        assert cli.working_directory == temp_dir
        assert cli.protocol == CommunicationProtocol.JSON_STDIO
        assert cli.max_concurrent_processes == 50
        assert len(cli.active_processes) == 0
        assert cli.monitoring_active is True
    
    @patch('subprocess.Popen')
    def test_spawn_agent_instance_success(self, mock_popen, cli_interface, sample_config):
        """Test successful agent process spawning"""
        # Mock subprocess
        mock_process = Mock()
        mock_process.pid = 12345
        mock_process.poll.return_value = None  # Process is running
        mock_process.stdin = Mock()
        mock_process.stdout = Mock()
        mock_process.stderr = Mock()
        mock_popen.return_value = mock_process
        
        # Mock the ready check
        with patch.object(cli_interface, '_wait_for_process_ready', return_value=True):
            agent_process = cli_interface.spawn_agent_instance(
                AgentType.PM,
                "test-instance",
                sample_config
            )
        
        assert agent_process is not None
        assert agent_process.type == AgentType.PM
        assert agent_process.instance_id == "test-instance"
        assert agent_process.status == ProcessStatus.IDLE
        assert agent_process.pid == 12345
        
        # Check that process was added to active processes
        assert len(cli_interface.active_processes) == 1
        assert agent_process.id in cli_interface.active_processes
    
    @patch('subprocess.Popen')
    def test_spawn_agent_instance_failure(self, mock_popen, cli_interface, sample_config):
        """Test agent process spawning failure"""
        # Mock subprocess failure
        mock_popen.side_effect = Exception("Failed to spawn process")
        
        with pytest.raises(ProcessSpawnError):
            cli_interface.spawn_agent_instance(
                AgentType.PM,
                "test-instance",
                sample_config
            )
        
        # Check that no process was added
        assert len(cli_interface.active_processes) == 0
    
    def test_spawn_agent_capacity_limit(self, cli_interface, sample_config):
        """Test spawning beyond capacity limit"""
        # Set low capacity for testing
        cli_interface.max_concurrent_processes = 1
        
        # Mock successful spawn for first process
        with patch('subprocess.Popen') as mock_popen:
            mock_process = Mock()
            mock_process.pid = 12345
            mock_process.poll.return_value = None
            mock_process.stdin = Mock()
            mock_process.stdout = Mock()
            mock_process.stderr = Mock()
            mock_popen.return_value = mock_process
            
            with patch.object(cli_interface, '_wait_for_process_ready', return_value=True):
                # First spawn should succeed
                cli_interface.spawn_agent_instance(AgentType.PM, "instance-1", sample_config)
                
                # Second spawn should fail due to capacity
                with pytest.raises(ProcessSpawnError, match="Maximum concurrent processes reached"):
                    cli_interface.spawn_agent_instance(AgentType.BA, "instance-2", sample_config)
    
    def test_send_task_process_not_found(self, cli_interface, sample_task):
        """Test sending task to non-existent process"""
        with pytest.raises(ProcessNotFoundError):
            cli_interface.send_task("non-existent-process", sample_task)
    
    @patch('subprocess.Popen')
    def test_send_task_success(self, mock_popen, cli_interface, sample_config, sample_task):
        """Test successful task sending"""
        # Setup mock process
        mock_process = Mock()
        mock_process.pid = 12345
        mock_process.poll.return_value = None
        mock_process.stdin = Mock()
        mock_process.stdout = Mock()
        mock_process.stderr = Mock()
        mock_popen.return_value = mock_process
        
        # Spawn agent
        with patch.object(cli_interface, '_wait_for_process_ready', return_value=True):
            agent_process = cli_interface.spawn_agent_instance(
                AgentType.PM, "test-instance", sample_config
            )
        
        # Mock task execution
        with patch.object(cli_interface, '_execute_task_sync') as mock_execute:
            mock_result = Mock()
            mock_execute.return_value = mock_result
            
            # Send task
            future = cli_interface.send_task(agent_process.id, sample_task)
            result = future.result(timeout=1)
            
            assert result == mock_result
            mock_execute.assert_called_once_with(agent_process.id, sample_task)
    
    def test_terminate_agent_not_found(self, cli_interface):
        """Test terminating non-existent process"""
        with pytest.raises(ProcessNotFoundError):
            cli_interface.terminate_agent("non-existent-process")
    
    @patch('subprocess.Popen')
    def test_terminate_agent_success(self, mock_popen, cli_interface, sample_config):
        """Test successful agent termination"""
        # Setup mock process
        mock_process = Mock()
        mock_process.pid = 12345
        mock_process.poll.return_value = None
        mock_process.stdin = Mock()
        mock_process.stdout = Mock()
        mock_process.stderr = Mock()
        mock_process.wait = Mock()
        mock_popen.return_value = mock_process
        
        # Spawn agent
        with patch.object(cli_interface, '_wait_for_process_ready', return_value=True):
            agent_process = cli_interface.spawn_agent_instance(
                AgentType.PM, "test-instance", sample_config
            )
        
        # Terminate agent
        result = cli_interface.terminate_agent(agent_process.id)
        
        assert result is True
        assert len(cli_interface.active_processes) == 0
        mock_process.wait.assert_called()
    
    @patch('subprocess.Popen')
    def test_scale_agent_pool_up(self, mock_popen, cli_interface):
        """Test scaling agent pool up"""
        # Setup mock process
        mock_process = Mock()
        mock_process.pid = 12345
        mock_process.poll.return_value = None
        mock_process.stdin = Mock()
        mock_process.stdout = Mock()
        mock_process.stderr = Mock()
        mock_popen.return_value = mock_process
        
        with patch.object(cli_interface, '_wait_for_process_ready', return_value=True):
            # Scale up to 2 instances
            process_ids = cli_interface.scale_agent_pool(AgentType.PM, 2)
            
            assert len(process_ids) == 2
            assert len(cli_interface.active_processes) == 2
            
            # All processes should be PM type
            for process_id in process_ids:
                assert cli_interface.active_processes[process_id].type == AgentType.PM
    
    @patch('subprocess.Popen')
    def test_scale_agent_pool_down(self, mock_popen, cli_interface, sample_config):
        """Test scaling agent pool down"""
        # Setup mock process
        mock_process = Mock()
        mock_process.pid = 12345
        mock_process.poll.return_value = None
        mock_process.stdin = Mock()
        mock_process.stdout = Mock()
        mock_process.stderr = Mock()
        mock_process.wait = Mock()
        mock_popen.return_value = mock_process
        
        # Spawn 3 agents
        with patch.object(cli_interface, '_wait_for_process_ready', return_value=True):
            for i in range(3):
                cli_interface.spawn_agent_instance(
                    AgentType.PM, f"instance-{i}", sample_config
                )
        
        assert len(cli_interface.active_processes) == 3
        
        # Scale down to 1 instance
        process_ids = cli_interface.scale_agent_pool(AgentType.PM, 1)
        
        assert len(process_ids) == 1
        assert len(cli_interface.active_processes) == 1
    
    @patch('subprocess.Popen')
    def test_get_process_status(self, mock_popen, cli_interface, sample_config):
        """Test getting process status"""
        # Setup mock process
        mock_process = Mock()
        mock_process.pid = 12345
        mock_process.poll.return_value = None
        mock_process.stdin = Mock()
        mock_process.stdout = Mock()
        mock_process.stderr = Mock()
        mock_popen.return_value = mock_process
        
        # Spawn agent
        with patch.object(cli_interface, '_wait_for_process_ready', return_value=True):
            agent_process = cli_interface.spawn_agent_instance(
                AgentType.PM, "test-instance", sample_config
            )
        
        # Get status
        status = cli_interface.get_process_status(agent_process.id)
        
        assert status["process_id"] == agent_process.id
        assert status["instance_id"] == "test-instance"
        assert status["agent_type"] == "product_manager"
        assert status["status"] == "idle"
        assert status["pid"] == 12345
        assert "metrics" in status
        assert "start_time" in status
        assert "last_activity" in status
    
    def test_get_process_status_not_found(self, cli_interface):
        """Test getting status for non-existent process"""
        with pytest.raises(ProcessNotFoundError):
            cli_interface.get_process_status("non-existent-process")
    
    def test_get_all_processes_empty(self, cli_interface):
        """Test getting all processes when none exist"""
        processes = cli_interface.get_all_processes()
        assert processes == []
    
    @patch('subprocess.Popen')
    def test_get_all_processes_with_data(self, mock_popen, cli_interface, sample_config):
        """Test getting all processes with data"""
        # Setup mock process
        mock_process = Mock()
        mock_process.pid = 12345
        mock_process.poll.return_value = None
        mock_process.stdin = Mock()
        mock_process.stdout = Mock()
        mock_process.stderr = Mock()
        mock_popen.return_value = mock_process
        
        # Spawn 2 agents
        with patch.object(cli_interface, '_wait_for_process_ready', return_value=True):
            cli_interface.spawn_agent_instance(AgentType.PM, "instance-1", sample_config)
            cli_interface.spawn_agent_instance(AgentType.BA, "instance-2", sample_config)
        
        # Get all processes
        processes = cli_interface.get_all_processes()
        
        assert len(processes) == 2
        assert all("process_id" in p for p in processes)
        assert all("agent_type" in p for p in processes)
        assert all("status" in p for p in processes)
    
    def test_cleanup(self, cli_interface):
        """Test cleanup functionality"""
        # Add some mock processes
        cli_interface.active_processes["test-1"] = Mock()
        cli_interface.active_processes["test-2"] = Mock()
        
        with patch.object(cli_interface, 'terminate_agent') as mock_terminate:
            cli_interface.cleanup()
            
            # Should have tried to terminate all processes
            assert mock_terminate.call_count == 2
            assert not cli_interface.monitoring_active


class TestProcessMetrics:
    """Test cases for ProcessMetrics"""
    
    def test_process_metrics_initialization(self):
        """Test ProcessMetrics initialization"""
        metrics = ProcessMetrics()
        
        assert metrics.cpu_usage == 0.0
        assert metrics.memory_usage == 0.0
        assert metrics.response_time == 0.0
        assert metrics.success_rate == 1.0
        assert metrics.error_count == 0
        assert isinstance(metrics.last_heartbeat, datetime)
    
    def test_update_response_time(self):
        """Test response time update with exponential moving average"""
        metrics = ProcessMetrics()
        
        # First update
        metrics.update_response_time(2.0)
        assert metrics.response_time == 0.6  # 0.3 * 2.0 + 0.7 * 0.0
        
        # Second update
        metrics.update_response_time(4.0)
        expected = 0.3 * 4.0 + 0.7 * 0.6  # 1.2 + 0.42 = 1.62
        assert abs(metrics.response_time - expected) < 0.001
    
    def test_record_error(self):
        """Test error recording and success rate calculation"""
        metrics = ProcessMetrics()
        
        # Record first error
        metrics.record_error()
        assert metrics.error_count == 1
        assert metrics.success_rate < 1.0
        
        # Record second error
        metrics.record_error()
        assert metrics.error_count == 2
        assert metrics.success_rate < 0.99


class TestHeartbeatConfig:
    """Test cases for HeartbeatConfig"""
    
    def test_heartbeat_config_defaults(self):
        """Test HeartbeatConfig default values"""
        config = HeartbeatConfig()
        
        assert config.interval_seconds == 30
        assert config.timeout_seconds == 60
        assert config.max_missed_heartbeats == 3
        assert config.enabled is True
    
    def test_heartbeat_config_custom(self):
        """Test HeartbeatConfig with custom values"""
        config = HeartbeatConfig(
            interval_seconds=10,
            timeout_seconds=20,
            max_missed_heartbeats=2,
            enabled=False
        )
        
        assert config.interval_seconds == 10
        assert config.timeout_seconds == 20
        assert config.max_missed_heartbeats == 2
        assert config.enabled is False


if __name__ == "__main__":
    pytest.main([__file__])