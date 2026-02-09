#!/usr/bin/env python3
"""
Tests for CLI Interface State Persistence

This module tests the state persistence and recovery functionality
of the CLIInterface class.
"""

import unittest
import tempfile
import json
from pathlib import Path
from datetime import datetime
from unittest.mock import Mock, patch, MagicMock

from agentic_sdlc.orchestration.interfaces.cli_interface import (
    CLIInterface, CommunicationProtocol, HeartbeatConfig
)
from agentic_sdlc.orchestration.models import (
    AgentType, AgentConfig, AgentTask, AgentProcess, ProcessStatus,
    ModelTier, ModelAssignment, TaskInput, TaskContext, DataFormat
)


class TestCLIStateManagement(unittest.TestCase):
    """Test CLI interface state management functionality"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.temp_dir = tempfile.TemporaryDirectory()
        self.temp_path = Path(self.temp_dir.name)
        
        self.cli_interface = CLIInterface(
            working_directory=self.temp_path,
            protocol=CommunicationProtocol.JSON_STDIO,
            heartbeat_config=HeartbeatConfig(enabled=False),
            max_concurrent_processes=5
        )
        
        # Create test agent config
        self.test_config = AgentConfig(
            agent_type=AgentType.IMPLEMENTATION,
            model_assignment=ModelAssignment(
                role_type=AgentType.IMPLEMENTATION,
                model_tier=ModelTier.OPERATIONAL,
                recommended_model="test-model",
                fallback_model="fallback-model",
                max_concurrent_instances=3,
                cost_per_token=0.001
            ),
            max_retries=3,
            timeout_minutes=30
        )
    
    def tearDown(self):
        """Clean up test fixtures"""
        self.cli_interface.cleanup()
        self.temp_dir.cleanup()
    
    def test_state_directory_initialization(self):
        """Test that state directories are created properly"""
        states_dir = self.temp_path / "states"
        logs_dir = self.temp_path / "logs"
        
        self.assertTrue(states_dir.exists(), "States directory should be created")
        self.assertTrue(logs_dir.exists(), "Logs directory should be created")
        self.assertTrue(states_dir.is_dir(), "States path should be a directory")
        self.assertTrue(logs_dir.is_dir(), "Logs path should be a directory")
    
    def test_save_process_state_success(self):
        """Test successful process state saving"""
        with patch('subprocess.Popen') as mock_popen:
            # Mock successful process creation
            mock_process = Mock()
            mock_process.pid = 12345
            mock_process.poll.return_value = None
            mock_process.stdin = Mock()
            mock_process.stdout = Mock()
            mock_process.stderr = Mock()
            mock_popen.return_value = mock_process
            
            with patch.object(self.cli_interface, '_wait_for_process_ready', return_value=True):
                # Spawn a process
                agent_process = self.cli_interface.spawn_agent_instance(
                    AgentType.IMPLEMENTATION, "test-instance", self.test_config
                )
                
                # Save the process state
                result = self.cli_interface.save_process_state(agent_process.id)
                
                # Verify save was successful
                self.assertTrue(result, "State save should succeed")
                
                # Verify state file was created
                state_file = self.temp_path / "states" / f"{agent_process.id}.json"
                self.assertTrue(state_file.exists(), "State file should be created")
                
                # Verify state file content
                with open(state_file, 'r') as f:
                    state_data = json.load(f)
                
                self.assertEqual(state_data["process_id"], agent_process.id)
                self.assertEqual(state_data["instance_id"], "test-instance")
                self.assertEqual(state_data["agent_type"], AgentType.IMPLEMENTATION.value)
                self.assertEqual(state_data["pid"], 12345)
                self.assertIn("saved_at", state_data)
                self.assertIn("config", state_data)
                self.assertIn("metrics", state_data)
    
    def test_save_process_state_nonexistent_process(self):
        """Test saving state for non-existent process"""
        result = self.cli_interface.save_process_state("nonexistent-process")
        self.assertFalse(result, "Save should fail for non-existent process")
    
    def test_load_process_state_success(self):
        """Test successful process state loading"""
        with patch('subprocess.Popen') as mock_popen:
            mock_process = Mock()
            mock_process.pid = 12345
            mock_process.poll.return_value = None
            mock_process.stdin = Mock()
            mock_process.stdout = Mock()
            mock_process.stderr = Mock()
            mock_popen.return_value = mock_process
            
            with patch.object(self.cli_interface, '_wait_for_process_ready', return_value=True):
                # Spawn and save a process
                agent_process = self.cli_interface.spawn_agent_instance(
                    AgentType.IMPLEMENTATION, "test-instance", self.test_config
                )
                
                self.cli_interface.save_process_state(agent_process.id)
                
                # Load the state
                loaded_state = self.cli_interface.load_process_state(agent_process.id)
                
                # Verify loaded state
                self.assertIsNotNone(loaded_state, "State should be loaded successfully")
                self.assertEqual(loaded_state["process_id"], agent_process.id)
                self.assertEqual(loaded_state["instance_id"], "test-instance")
                self.assertEqual(loaded_state["agent_type"], AgentType.IMPLEMENTATION.value)
    
    def test_load_process_state_nonexistent_file(self):
        """Test loading state for non-existent file"""
        loaded_state = self.cli_interface.load_process_state("nonexistent-process")
        self.assertIsNone(loaded_state, "Load should return None for non-existent file")
    
    def test_get_saved_states(self):
        """Test getting list of saved states"""
        with patch('subprocess.Popen') as mock_popen:
            mock_process = Mock()
            mock_process.pid = 12345
            mock_process.poll.return_value = None
            mock_process.stdin = Mock()
            mock_process.stdout = Mock()
            mock_process.stderr = Mock()
            mock_popen.return_value = mock_process
            
            with patch.object(self.cli_interface, '_wait_for_process_ready', return_value=True):
                # Spawn and save multiple processes
                processes = []
                for i in range(3):
                    mock_process.pid = 12345 + i
                    agent_process = self.cli_interface.spawn_agent_instance(
                        AgentType.IMPLEMENTATION, f"test-instance-{i}", self.test_config
                    )
                    processes.append(agent_process)
                    self.cli_interface.save_process_state(agent_process.id)
                
                # Get saved states
                saved_states = self.cli_interface.get_saved_states()
                
                # Verify results
                self.assertEqual(len(saved_states), 3, "Should find 3 saved states")
                
                for process in processes:
                    self.assertIn(process.id, saved_states, 
                                f"Process {process.id} should be in saved states")
    
    def test_delete_process_state(self):
        """Test deleting process state"""
        with patch('subprocess.Popen') as mock_popen:
            mock_process = Mock()
            mock_process.pid = 12345
            mock_process.poll.return_value = None
            mock_process.stdin = Mock()
            mock_process.stdout = Mock()
            mock_process.stderr = Mock()
            mock_popen.return_value = mock_process
            
            with patch.object(self.cli_interface, '_wait_for_process_ready', return_value=True):
                # Spawn and save a process
                agent_process = self.cli_interface.spawn_agent_instance(
                    AgentType.IMPLEMENTATION, "test-instance", self.test_config
                )
                
                self.cli_interface.save_process_state(agent_process.id)
                
                # Verify state file exists
                state_file = self.temp_path / "states" / f"{agent_process.id}.json"
                self.assertTrue(state_file.exists(), "State file should exist before deletion")
                
                # Delete the state
                result = self.cli_interface.delete_process_state(agent_process.id)
                
                # Verify deletion
                self.assertTrue(result, "Delete should succeed")
                self.assertFalse(state_file.exists(), "State file should be deleted")
    
    def test_get_process_state_info(self):
        """Test getting process state information"""
        with patch('subprocess.Popen') as mock_popen:
            mock_process = Mock()
            mock_process.pid = 12345
            mock_process.poll.return_value = None
            mock_process.stdin = Mock()
            mock_process.stdout = Mock()
            mock_process.stderr = Mock()
            mock_popen.return_value = mock_process
            
            with patch.object(self.cli_interface, '_wait_for_process_ready', return_value=True):
                # Spawn and save a process
                agent_process = self.cli_interface.spawn_agent_instance(
                    AgentType.IMPLEMENTATION, "test-instance", self.test_config
                )
                
                self.cli_interface.save_process_state(agent_process.id)
                
                # Get state info
                state_info = self.cli_interface.get_process_state_info(agent_process.id)
                
                # Verify state info
                self.assertIsNotNone(state_info, "State info should be returned")
                self.assertEqual(state_info["process_id"], agent_process.id)
                self.assertEqual(state_info["instance_id"], "test-instance")
                self.assertEqual(state_info["agent_type"], AgentType.IMPLEMENTATION.value)
                self.assertIn("file_size", state_info)
                self.assertIn("created_at", state_info)
                self.assertIn("modified_at", state_info)
                self.assertIn("saved_at", state_info)
    
    def test_cleanup_terminated_processes(self):
        """Test cleanup of terminated processes"""
        with patch('subprocess.Popen') as mock_popen:
            mock_process = Mock()
            mock_process.pid = 12345
            mock_process.poll.return_value = None  # Initially running
            mock_process.stdin = Mock()
            mock_process.stdout = Mock()
            mock_process.stderr = Mock()
            mock_popen.return_value = mock_process
            
            with patch.object(self.cli_interface, '_wait_for_process_ready', return_value=True):
                # Spawn a process
                agent_process = self.cli_interface.spawn_agent_instance(
                    AgentType.IMPLEMENTATION, "test-instance", self.test_config
                )
                
                # Verify process is active
                self.assertIn(agent_process.id, self.cli_interface.active_processes)
                
                # Simulate process termination
                mock_process.poll.return_value = 0  # Process terminated
                
                # Run cleanup
                cleaned_count = self.cli_interface.cleanup_terminated_processes()
                
                # Verify cleanup
                self.assertEqual(cleaned_count, 1, "Should clean up 1 terminated process")
                self.assertNotIn(agent_process.id, self.cli_interface.active_processes,
                               "Process should be removed from active processes")
                
                # Verify state was saved
                state_file = self.temp_path / "states" / f"{agent_process.id}.json"
                self.assertTrue(state_file.exists(), "State should be saved during cleanup")


if __name__ == '__main__':
    unittest.main()