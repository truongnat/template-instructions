"""
CLI Interface for Multi-Agent Orchestration System

This module implements the CLI interface for managing independent agent processes
with support for multiple instances per role, process lifecycle management,
and standardized communication protocols.

Requirements: 4.1, 4.2, 4.3, 4.5
"""

import json
import subprocess
import threading
import time
import signal
import os
from datetime import datetime, timedelta
from enum import Enum
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, field
from uuid import uuid4
from queue import Queue, Empty
from concurrent.futures import ThreadPoolExecutor, Future

from ..models import (
    AgentType, AgentTask, AgentResult, AgentConfig, AgentProcess,
    ProcessStatus, TaskStatus, ModelTier
)
from ..exceptions.cli import (
    ProcessSpawnError, ProcessCommunicationError, ProcessTerminationError,
    ProcessNotFoundError
)
from ..utils.logging import get_logger


class CommunicationProtocol(Enum):
    """Communication protocol types"""
    JSON_STDIO = "json_stdio"
    JSON_SOCKET = "json_socket"
    REST_API = "rest_api"


@dataclass
class ProcessMetrics:
    """Metrics for a running process"""
    cpu_usage: float = 0.0
    memory_usage: float = 0.0
    response_time: float = 0.0
    success_rate: float = 1.0
    error_count: int = 0
    last_heartbeat: datetime = field(default_factory=datetime.now)
    
    def update_response_time(self, response_time: float):
        """Update response time with exponential moving average"""
        alpha = 0.3  # Smoothing factor
        self.response_time = alpha * response_time + (1 - alpha) * self.response_time
    
    def record_error(self):
        """Record an error occurrence"""
        self.error_count += 1
        # Update success rate (simple moving average over last 100 operations)
        total_ops = max(self.error_count + int(self.success_rate * 100), 1)
        self.success_rate = max(0.0, (total_ops - self.error_count) / total_ops)


@dataclass
class HeartbeatConfig:
    """Configuration for process heartbeat monitoring"""
    interval_seconds: int = 30
    timeout_seconds: int = 60
    max_missed_heartbeats: int = 3
    enabled: bool = True


class CLIInterface:
    """
    CLI Interface for managing independent agent processes
    
    This class provides process lifecycle management, communication protocols,
    and monitoring capabilities for CLI-based agent execution.
    """
    
    def __init__(
        self,
        base_command: str = "python",
        working_directory: Optional[Path] = None,
        protocol: CommunicationProtocol = CommunicationProtocol.JSON_STDIO,
        heartbeat_config: Optional[HeartbeatConfig] = None,
        max_concurrent_processes: int = 50
    ):
        """
        Initialize the CLI interface
        
        Args:
            base_command: Base command to spawn agent processes
            working_directory: Working directory for agent processes
            protocol: Communication protocol to use
            heartbeat_config: Heartbeat monitoring configuration
            max_concurrent_processes: Maximum number of concurrent processes
        """
        self.logger = get_logger(__name__)
        self.base_command = base_command
        self.working_directory = working_directory or Path.cwd()
        self.protocol = protocol
        self.heartbeat_config = heartbeat_config or HeartbeatConfig()
        self.max_concurrent_processes = max_concurrent_processes
        
        # Process management
        self.active_processes: Dict[str, AgentProcess] = {}
        self.process_metrics: Dict[str, ProcessMetrics] = {}
        self.process_locks: Dict[str, threading.Lock] = {}
        
        # Communication queues
        self.task_queues: Dict[str, Queue] = {}
        self.result_queues: Dict[str, Queue] = {}
        
        # Monitoring
        self.heartbeat_threads: Dict[str, threading.Thread] = {}
        self.monitoring_active = True
        self.executor = ThreadPoolExecutor(max_workers=max_concurrent_processes)
        
        # Start global monitoring
        self._start_global_monitoring()
        
        # Initialize state management
        self._initialize_state_management()
        
        self.logger.info(f"CLIInterface initialized with protocol {protocol.value}")
    
    def spawn_agent_instance(
        self,
        agent_type: AgentType,
        instance_id: str,
        config: AgentConfig
    ) -> AgentProcess:
        """
        Spawn a new agent process instance
        
        Args:
            agent_type: Type of agent to spawn
            instance_id: Unique identifier for this instance
            config: Configuration for the agent
            
        Returns:
            AgentProcess representing the spawned process
            
        Raises:
            ProcessSpawnError: If process spawning fails
        """
        if len(self.active_processes) >= self.max_concurrent_processes:
            raise ProcessSpawnError(
                f"Maximum concurrent processes reached: {self.max_concurrent_processes}"
            )
        
        process_id = f"{agent_type.value}_{instance_id}_{uuid4().hex[:8]}"
        
        try:
            # Build command arguments
            command_args = self._build_command_args(agent_type, instance_id, config)
            
            # Spawn the process
            popen = subprocess.Popen(
                command_args,
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                cwd=self.working_directory,
                text=True,
                bufsize=1,  # Line buffered
                universal_newlines=True
            )
            
            # Create agent process object
            agent_process = AgentProcess(
                id=process_id,
                instance_id=instance_id,
                type=agent_type,
                model_tier=config.model_assignment.model_tier,
                status=ProcessStatus.STARTING,
                pid=popen.pid,
                start_time=datetime.now(),
                last_activity=datetime.now(),
                current_load=0.0,
                subprocess_handle=popen,
                config=config
            )
            
            # Initialize process management structures
            self.active_processes[process_id] = agent_process
            self.process_metrics[process_id] = ProcessMetrics()
            self.process_locks[process_id] = threading.Lock()
            self.task_queues[process_id] = Queue()
            self.result_queues[process_id] = Queue()
            
            # Start process monitoring
            self._start_process_monitoring(process_id)
            
            # Wait for process to be ready
            if not self._wait_for_process_ready(process_id, timeout=30):
                self.terminate_agent(process_id)
                raise ProcessSpawnError(f"Process {process_id} failed to become ready")
            
            agent_process.status = ProcessStatus.IDLE
            
            self.logger.info(f"Spawned agent process {process_id} (PID: {popen.pid})")
            return agent_process
            
        except Exception as e:
            self.logger.error(f"Failed to spawn agent process: {e}")
            # Cleanup on failure
            if process_id in self.active_processes:
                self._cleanup_process(process_id)
            raise ProcessSpawnError(f"Failed to spawn agent process: {str(e)}") from e
    
    def send_task(self, process_id: str, task: AgentTask) -> Future:
        """
        Send a task to an agent process asynchronously
        
        Args:
            process_id: ID of the target process
            task: Task to send
            
        Returns:
            Future that will contain the task result
            
        Raises:
            ProcessNotFoundError: If process not found
            ProcessCommunicationError: If communication fails
        """
        if process_id not in self.active_processes:
            raise ProcessNotFoundError(f"Process {process_id} not found")
        
        agent_process = self.active_processes[process_id]
        
        if agent_process.status not in [ProcessStatus.IDLE, ProcessStatus.BUSY]:
            raise ProcessCommunicationError(
                f"Process {process_id} is not ready (status: {agent_process.status})"
            )
        
        # Submit task execution to thread pool
        future = self.executor.submit(self._execute_task_sync, process_id, task)
        
        self.logger.debug(f"Submitted task {task.id} to process {process_id}")
        return future
    
    def _execute_task_sync(self, process_id: str, task: AgentTask) -> AgentResult:
        """
        Execute a task synchronously (called by thread pool)
        
        Args:
            process_id: ID of the target process
            task: Task to execute
            
        Returns:
            Task result
        """
        start_time = datetime.now()
        agent_process = self.active_processes[process_id]
        
        try:
            with self.process_locks[process_id]:
                # Update process status
                agent_process.status = ProcessStatus.BUSY
                agent_process.current_task = task
                agent_process.last_activity = datetime.now()
                
                # Send task via the configured protocol
                self._send_message(process_id, {
                    "type": "task",
                    "task_id": task.id,
                    "task_data": task.to_dict()
                })
                
                # Wait for result
                result = self._receive_result(process_id, timeout=300)  # 5 minute timeout
                
                # Update metrics
                response_time = (datetime.now() - start_time).total_seconds()
                self.process_metrics[process_id].update_response_time(response_time)
                
                # Update process status
                agent_process.status = ProcessStatus.IDLE
                agent_process.current_task = None
                agent_process.last_activity = datetime.now()
                
                self.logger.debug(f"Task {task.id} completed by process {process_id}")
                return result
                
        except Exception as e:
            # Record error and update process status
            self.process_metrics[process_id].record_error()
            agent_process.status = ProcessStatus.ERROR
            agent_process.current_task = None
            
            self.logger.error(f"Task execution failed for process {process_id}: {e}")
            raise ProcessCommunicationError(f"Task execution failed: {str(e)}") from e
    
    def receive_results(self, process_id: str, timeout: float = 60.0) -> Optional[AgentResult]:
        """
        Receive results from an agent process
        
        Args:
            process_id: ID of the source process
            timeout: Timeout in seconds
            
        Returns:
            Agent result or None if timeout
            
        Raises:
            ProcessNotFoundError: If process not found
        """
        if process_id not in self.active_processes:
            raise ProcessNotFoundError(f"Process {process_id} not found")
        
        try:
            result_queue = self.result_queues[process_id]
            result_data = result_queue.get(timeout=timeout)
            
            # Parse result
            result = AgentResult.from_dict(result_data)
            self.logger.debug(f"Received result from process {process_id}")
            return result
            
        except Empty:
            self.logger.warning(f"Timeout waiting for result from process {process_id}")
            return None
        except Exception as e:
            self.logger.error(f"Failed to receive result from process {process_id}: {e}")
            raise ProcessCommunicationError(f"Failed to receive result: {str(e)}") from e
    
    def terminate_agent(self, process_id: str) -> bool:
        """
        Terminate an agent process
        
        Args:
            process_id: ID of the process to terminate
            
        Returns:
            True if termination successful, False otherwise
            
        Raises:
            ProcessNotFoundError: If process not found
        """
        if process_id not in self.active_processes:
            raise ProcessNotFoundError(f"Process {process_id} not found")
        
        agent_process = self.active_processes[process_id]
        
        try:
            # Send termination signal
            if agent_process.subprocess_handle and agent_process.subprocess_handle.poll() is None:
                # Try graceful shutdown first
                self._send_message(process_id, {"type": "shutdown"})
                
                # Wait for graceful shutdown
                try:
                    agent_process.subprocess_handle.wait(timeout=10)
                except subprocess.TimeoutExpired:
                    # Force termination
                    agent_process.subprocess_handle.terminate()
                    try:
                        agent_process.subprocess_handle.wait(timeout=5)
                    except subprocess.TimeoutExpired:
                        agent_process.subprocess_handle.kill()
                        agent_process.subprocess_handle.wait()
            
            # Cleanup
            self._cleanup_process(process_id)
            
            self.logger.info(f"Terminated agent process {process_id}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to terminate process {process_id}: {e}")
            # Force cleanup even if termination failed
            self._cleanup_process(process_id)
            raise ProcessTerminationError(f"Failed to terminate process: {str(e)}") from e
    
    def scale_agent_pool(self, agent_type: AgentType, target_instances: int) -> List[str]:
        """
        Scale the number of agent instances for a specific type
        
        Args:
            agent_type: Type of agent to scale
            target_instances: Target number of instances
            
        Returns:
            List of process IDs for the agent type
        """
        current_processes = [
            pid for pid, process in self.active_processes.items()
            if process.type == agent_type
        ]
        
        current_count = len(current_processes)
        
        if target_instances > current_count:
            # Scale up
            for i in range(target_instances - current_count):
                try:
                    instance_id = f"auto_{i}_{uuid4().hex[:8]}"
                    config = AgentConfig(
                        agent_type=agent_type,
                        model_tier=ModelTier.OPERATIONAL  # Default tier
                    )
                    self.spawn_agent_instance(agent_type, instance_id, config)
                except Exception as e:
                    self.logger.error(f"Failed to scale up {agent_type.value}: {e}")
                    break
        
        elif target_instances < current_count:
            # Scale down
            processes_to_terminate = current_processes[target_instances:]
            for process_id in processes_to_terminate:
                try:
                    self.terminate_agent(process_id)
                except Exception as e:
                    self.logger.error(f"Failed to scale down {agent_type.value}: {e}")
        
        # Return updated list
        return [
            pid for pid, process in self.active_processes.items()
            if process.type == agent_type
        ]
    
    def get_process_status(self, process_id: str) -> Dict[str, Any]:
        """
        Get detailed status information for a process
        
        Args:
            process_id: ID of the process
            
        Returns:
            Dictionary containing process status information
            
        Raises:
            ProcessNotFoundError: If process not found
        """
        if process_id not in self.active_processes:
            raise ProcessNotFoundError(f"Process {process_id} not found")
        
        agent_process = self.active_processes[process_id]
        metrics = self.process_metrics[process_id]
        
        return {
            "process_id": process_id,
            "instance_id": agent_process.instance_id,
            "agent_type": agent_process.type.value,
            "status": agent_process.status.value,
            "pid": agent_process.pid,
            "start_time": agent_process.start_time.isoformat(),
            "last_activity": agent_process.last_activity.isoformat(),
            "current_load": agent_process.current_load,
            "current_task": agent_process.current_task.id if agent_process.current_task else None,
            "metrics": {
                "cpu_usage": metrics.cpu_usage,
                "memory_usage": metrics.memory_usage,
                "response_time": metrics.response_time,
                "success_rate": metrics.success_rate,
                "error_count": metrics.error_count,
                "last_heartbeat": metrics.last_heartbeat.isoformat()
            }
        }
    
    def get_all_processes(self) -> List[Dict[str, Any]]:
        """
        Get status information for all active processes
        
        Returns:
            List of process status dictionaries
        """
        return [
            self.get_process_status(process_id)
            for process_id in self.active_processes.keys()
        ]
    
    def cleanup(self):
        """Clean up all resources and terminate all processes"""
        self.monitoring_active = False
        
        # Save state for all active processes before termination
        for process_id in list(self.active_processes.keys()):
            try:
                self.save_process_state(process_id)
            except Exception as e:
                self.logger.warning(f"Failed to save state for process {process_id}: {e}")
        
        # Terminate all processes
        process_ids = list(self.active_processes.keys())
        for process_id in process_ids:
            try:
                self.terminate_agent(process_id)
            except Exception as e:
                self.logger.error(f"Error during cleanup of process {process_id}: {e}")
        
        # Clean up old state files
        try:
            self.cleanup_old_states(max_age_days=30)  # Keep states for 30 days
        except Exception as e:
            self.logger.warning(f"Failed to cleanup old states: {e}")
        
        # Shutdown executor
        self.executor.shutdown(wait=True)
        
        self.logger.info("CLIInterface cleanup completed")
    
    def _build_command_args(
        self,
        agent_type: AgentType,
        instance_id: str,
        config: AgentConfig
    ) -> List[str]:
        """Build command arguments for spawning an agent process"""
        # This would be customized based on your agent implementation
        # For now, we'll use a generic Python module approach
        
        args = [
            self.base_command,
            "-m", f"agentic_sdlc.orchestration.agents.{agent_type.value}_agent",
            "--instance-id", instance_id,
            "--protocol", self.protocol.value
        ]
        
        # Add configuration as JSON
        if config:
            args.extend(["--config", json.dumps(config.to_dict())])
        
        return args
    
    def _send_message(self, process_id: str, message: Dict[str, Any]):
        """Send a message to a process via the configured protocol"""
        agent_process = self.active_processes[process_id]
        
        if self.protocol == CommunicationProtocol.JSON_STDIO:
            # Send via stdin
            message_json = json.dumps(message) + "\n"
            agent_process.subprocess_handle.stdin.write(message_json)
            agent_process.subprocess_handle.stdin.flush()
        else:
            raise NotImplementedError(f"Protocol {self.protocol} not implemented")
    
    def _receive_result(self, process_id: str, timeout: float) -> AgentResult:
        """Receive a result from a process"""
        agent_process = self.active_processes[process_id]
        
        if self.protocol == CommunicationProtocol.JSON_STDIO:
            # Read from stdout with timeout
            start_time = time.time()
            while time.time() - start_time < timeout:
                if agent_process.subprocess_handle.stdout.readable():
                    line = agent_process.subprocess_handle.stdout.readline()
                    if line:
                        try:
                            result_data = json.loads(line.strip())
                            return AgentResult.from_dict(result_data)
                        except json.JSONDecodeError:
                            continue
                time.sleep(0.1)
            
            raise ProcessCommunicationError(f"Timeout waiting for result from {process_id}")
        else:
            raise NotImplementedError(f"Protocol {self.protocol} not implemented")
    
    def _wait_for_process_ready(self, process_id: str, timeout: float) -> bool:
        """Wait for a process to signal that it's ready"""
        start_time = time.time()
        agent_process = self.active_processes[process_id]
        
        while time.time() - start_time < timeout:
            if agent_process.subprocess_handle.poll() is not None:
                # Process has terminated
                return False
            
            # Check for ready signal (implementation specific)
            # For now, just wait a bit and assume ready
            time.sleep(1)
            return True
        
        return False
    
    def _start_process_monitoring(self, process_id: str):
        """Start monitoring threads for a process"""
        if self.heartbeat_config.enabled:
            heartbeat_thread = threading.Thread(
                target=self._heartbeat_monitor,
                args=(process_id,),
                daemon=True
            )
            heartbeat_thread.start()
            self.heartbeat_threads[process_id] = heartbeat_thread
    
    def _heartbeat_monitor(self, process_id: str):
        """Monitor process heartbeat"""
        missed_heartbeats = 0
        
        while self.monitoring_active and process_id in self.active_processes:
            try:
                agent_process = self.active_processes[process_id]
                
                # Check if process is still alive
                if agent_process.subprocess_handle.poll() is not None:
                    # Process has terminated
                    agent_process.status = ProcessStatus.TERMINATED
                    break
                
                # Send heartbeat request
                try:
                    self._send_message(process_id, {"type": "heartbeat"})
                    # In a real implementation, you'd wait for a heartbeat response
                    # For now, just update the timestamp
                    self.process_metrics[process_id].last_heartbeat = datetime.now()
                    missed_heartbeats = 0
                except Exception:
                    missed_heartbeats += 1
                
                # Check for missed heartbeats
                if missed_heartbeats >= self.heartbeat_config.max_missed_heartbeats:
                    self.logger.warning(f"Process {process_id} missed {missed_heartbeats} heartbeats")
                    agent_process.status = ProcessStatus.UNRESPONSIVE
                    break
                
                time.sleep(self.heartbeat_config.interval_seconds)
                
            except Exception as e:
                self.logger.error(f"Heartbeat monitor error for {process_id}: {e}")
                break
    
    def _start_global_monitoring(self):
        """Start global monitoring thread"""
        def global_monitor():
            while self.monitoring_active:
                try:
                    # Clean up terminated processes
                    terminated_processes = []
                    for process_id, agent_process in self.active_processes.items():
                        if (agent_process.subprocess_handle and 
                            agent_process.subprocess_handle.poll() is not None):
                            terminated_processes.append(process_id)
                    
                    for process_id in terminated_processes:
                        self.logger.info(f"Cleaning up terminated process {process_id}")
                        self._cleanup_process(process_id)
                    
                    time.sleep(10)  # Check every 10 seconds
                    
                except Exception as e:
                    self.logger.error(f"Global monitor error: {e}")
        
        monitor_thread = threading.Thread(target=global_monitor, daemon=True)
        monitor_thread.start()
    
    def _cleanup_process(self, process_id: str):
        """Clean up all resources for a process"""
        try:
            # Remove from active processes
            if process_id in self.active_processes:
                del self.active_processes[process_id]
            
            # Clean up monitoring structures
            if process_id in self.process_metrics:
                del self.process_metrics[process_id]
            
            if process_id in self.process_locks:
                del self.process_locks[process_id]
            
            if process_id in self.task_queues:
                del self.task_queues[process_id]
            
            if process_id in self.result_queues:
                del self.result_queues[process_id]
            
            if process_id in self.heartbeat_threads:
                # Thread will stop when monitoring_active is False or process is removed
                del self.heartbeat_threads[process_id]
            
        except Exception as e:
            self.logger.error(f"Error during process cleanup for {process_id}: {e}")
    
    # State Management Methods
    
    def _initialize_state_management(self):
        """Initialize state management directories and recovery"""
        try:
            # Create states directory
            states_dir = self.working_directory / "states"
            states_dir.mkdir(parents=True, exist_ok=True)
            
            # Create logs directory for process logs
            logs_dir = self.working_directory / "logs"
            logs_dir.mkdir(parents=True, exist_ok=True)
            
            self.logger.info("State management initialized")
            
        except Exception as e:
            self.logger.error(f"Failed to initialize state management: {e}")
    
    def save_process_state(self, process_id: str) -> bool:
        """Save process state to file"""
        try:
            if process_id not in self.active_processes:
                self.logger.warning(f"Process {process_id} not found for state saving")
                return False
            
            process = self.active_processes[process_id]
            state_file = self.working_directory / "states" / f"{process_id}.json"
            state_file.parent.mkdir(parents=True, exist_ok=True)
            
            # Prepare state data
            state_data = {
                "process_id": process.id,
                "instance_id": process.instance_id,
                "agent_type": process.type.value,
                "model_tier": process.model_tier.value,
                "status": process.status.value,
                "pid": process.pid,
                "start_time": process.start_time.isoformat(),
                "last_activity": process.last_activity.isoformat(),
                "current_load": process.current_load,
                "config": process.config.to_dict() if process.config else None,
                "current_task": process.current_task.to_dict() if process.current_task else None,
                "metrics": {
                    "cpu_usage": self.process_metrics[process_id].cpu_usage,
                    "memory_usage": self.process_metrics[process_id].memory_usage,
                    "response_time": self.process_metrics[process_id].response_time,
                    "success_rate": self.process_metrics[process_id].success_rate,
                    "error_count": self.process_metrics[process_id].error_count,
                    "last_heartbeat": self.process_metrics[process_id].last_heartbeat.isoformat() if self.process_metrics[process_id].last_heartbeat else None
                },
                "saved_at": datetime.now().isoformat()
            }
            
            # Write state to file
            with open(state_file, 'w') as f:
                json.dump(state_data, f, indent=2)
            
            self.logger.info(f"Process state saved for {process_id}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to save process state for {process_id}: {e}")
            return False
    
    def load_process_state(self, process_id: str) -> Optional[Dict[str, Any]]:
        """Load process state from file"""
        try:
            state_file = self.working_directory / "states" / f"{process_id}.json"
            
            if not state_file.exists():
                self.logger.warning(f"No state file found for process {process_id}")
                return None
            
            with open(state_file, 'r') as f:
                state_data = json.load(f)
            
            self.logger.info(f"Process state loaded for {process_id}")
            return state_data
            
        except Exception as e:
            self.logger.error(f"Failed to load process state for {process_id}: {e}")
            return None
    
    def recover_process_state(self, process_id: str) -> bool:
        """Recover process from saved state"""
        try:
            state_data = self.load_process_state(process_id)
            if not state_data:
                return False
            
            # Check if process is already running
            if process_id in self.active_processes:
                self.logger.warning(f"Process {process_id} is already active, cannot recover")
                return False
            
            # Recreate agent config from state
            config_data = state_data.get("config")
            if not config_data:
                self.logger.error(f"No config data found in state for {process_id}")
                return False
            
            config = AgentConfig.from_dict(config_data)
            agent_type = AgentType(state_data["agent_type"])
            instance_id = state_data["instance_id"]
            
            # Attempt to respawn the process
            try:
                recovered_process = self.spawn_agent_instance(agent_type, instance_id, config)
                
                # Restore additional state information
                recovered_process.current_load = state_data.get("current_load", 0.0)
                
                # Restore current task if it exists
                current_task_data = state_data.get("current_task")
                if current_task_data:
                    recovered_process.current_task = AgentTask.from_dict(current_task_data)
                
                # Restore metrics
                metrics_data = state_data.get("metrics", {})
                if process_id in self.process_metrics:
                    metrics = self.process_metrics[process_id]
                    metrics.cpu_usage = metrics_data.get("cpu_usage", 0.0)
                    metrics.memory_usage = metrics_data.get("memory_usage", 0.0)
                    metrics.response_time = metrics_data.get("response_time", 0.0)
                    metrics.success_rate = metrics_data.get("success_rate", 1.0)
                    metrics.error_count = metrics_data.get("error_count", 0)
                    if metrics_data.get("last_heartbeat"):
                        metrics.last_heartbeat = datetime.fromisoformat(metrics_data["last_heartbeat"])
                
                self.logger.info(f"Process {process_id} recovered successfully")
                return True
                
            except Exception as spawn_error:
                self.logger.error(f"Failed to respawn process {process_id}: {spawn_error}")
                return False
            
        except Exception as e:
            self.logger.error(f"Failed to recover process state for {process_id}: {e}")
            return False
    
    def get_saved_states(self) -> List[str]:
        """Get list of all saved process states"""
        try:
            states_dir = self.working_directory / "states"
            if not states_dir.exists():
                return []
            
            state_files = list(states_dir.glob("*.json"))
            process_ids = [f.stem for f in state_files]
            
            return process_ids
            
        except Exception as e:
            self.logger.error(f"Failed to get saved states: {e}")
            return []
    
    def recover_all_saved_processes(self) -> Dict[str, bool]:
        """Attempt to recover all saved process states"""
        recovery_results = {}
        saved_states = self.get_saved_states()
        
        self.logger.info(f"Attempting to recover {len(saved_states)} saved processes")
        
        for process_id in saved_states:
            try:
                success = self.recover_process_state(process_id)
                recovery_results[process_id] = success
                
                if success:
                    self.logger.info(f"Successfully recovered process {process_id}")
                else:
                    self.logger.warning(f"Failed to recover process {process_id}")
                    
            except Exception as e:
                self.logger.error(f"Error recovering process {process_id}: {e}")
                recovery_results[process_id] = False
        
        successful_recoveries = sum(1 for success in recovery_results.values() if success)
        self.logger.info(f"Recovery complete: {successful_recoveries}/{len(saved_states)} processes recovered")
        
        return recovery_results
    
    def delete_process_state(self, process_id: str) -> bool:
        """Delete saved state for a process"""
        try:
            state_file = self.working_directory / "states" / f"{process_id}.json"
            
            if state_file.exists():
                state_file.unlink()
                self.logger.info(f"Deleted state file for process {process_id}")
                return True
            else:
                self.logger.warning(f"No state file found for process {process_id}")
                return False
                
        except Exception as e:
            self.logger.error(f"Failed to delete state file for process {process_id}: {e}")
            return False
    
    def cleanup_old_states(self, max_age_days: int = 7) -> int:
        """Clean up old state files"""
        try:
            states_dir = self.working_directory / "states"
            if not states_dir.exists():
                return 0
            
            cutoff_time = datetime.now() - timedelta(days=max_age_days)
            cleaned_count = 0
            
            for state_file in states_dir.glob("*.json"):
                try:
                    # Check file modification time
                    file_mtime = datetime.fromtimestamp(state_file.stat().st_mtime)
                    
                    if file_mtime < cutoff_time:
                        # Also check if the process is currently active
                        process_id = state_file.stem
                        if process_id not in self.active_processes:
                            state_file.unlink()
                            cleaned_count += 1
                            self.logger.debug(f"Cleaned up old state file: {state_file.name}")
                        
                except Exception as file_error:
                    self.logger.warning(f"Error processing state file {state_file.name}: {file_error}")
            
            self.logger.info(f"Cleaned up {cleaned_count} old state files")
            return cleaned_count
            
        except Exception as e:
            self.logger.error(f"Failed to cleanup old states: {e}")
            return 0
    
    def get_process_state_info(self, process_id: str) -> Optional[Dict[str, Any]]:
        """Get information about a saved process state without loading it"""
        try:
            state_file = self.working_directory / "states" / f"{process_id}.json"
            
            if not state_file.exists():
                return None
            
            # Get file stats
            stat = state_file.stat()
            
            # Read minimal info from state file
            with open(state_file, 'r') as f:
                state_data = json.load(f)
            
            return {
                "process_id": process_id,
                "file_size": stat.st_size,
                "created_at": datetime.fromtimestamp(stat.st_ctime).isoformat(),
                "modified_at": datetime.fromtimestamp(stat.st_mtime).isoformat(),
                "agent_type": state_data.get("agent_type"),
                "instance_id": state_data.get("instance_id"),
                "last_status": state_data.get("status"),
                "saved_at": state_data.get("saved_at")
            }
            
        except Exception as e:
            self.logger.error(f"Failed to get state info for process {process_id}: {e}")
            return None
    
    def cleanup_terminated_processes(self) -> int:
        """Clean up resources for terminated processes"""
        cleaned_count = 0
        terminated_processes = []
        
        try:
            # Find terminated processes
            for process_id, process in list(self.active_processes.items()):
                if process.subprocess_handle and process.subprocess_handle.poll() is not None:
                    # Process has terminated
                    terminated_processes.append(process_id)
                elif process.status == ProcessStatus.TERMINATED:
                    terminated_processes.append(process_id)
            
            # Clean up each terminated process
            for process_id in terminated_processes:
                if self._cleanup_process_resources(process_id):
                    cleaned_count += 1
            
            self.logger.info(f"Cleaned up {cleaned_count} terminated processes")
            return cleaned_count
            
        except Exception as e:
            self.logger.error(f"Error during cleanup of terminated processes: {e}")
            return cleaned_count
    
    def _cleanup_process_resources(self, process_id: str) -> bool:
        """Clean up all resources for a specific process"""
        try:
            # Save state before cleanup
            self.save_process_state(process_id)
            
            # Remove from active processes
            if process_id in self.active_processes:
                process = self.active_processes[process_id]
                
                # Ensure subprocess is terminated
                if process.subprocess_handle:
                    try:
                        if process.subprocess_handle.poll() is None:
                            process.subprocess_handle.terminate()
                            # Wait briefly for graceful termination
                            try:
                                process.subprocess_handle.wait(timeout=5)
                            except subprocess.TimeoutExpired:
                                process.subprocess_handle.kill()
                                process.subprocess_handle.wait()
                    except Exception as subprocess_error:
                        self.logger.warning(f"Error terminating subprocess for {process_id}: {subprocess_error}")
                
                del self.active_processes[process_id]
            
            # Clean up metrics
            if process_id in self.process_metrics:
                del self.process_metrics[process_id]
            
            # Clean up locks
            if process_id in self.process_locks:
                del self.process_locks[process_id]
            
            # Clean up queues
            if process_id in self.task_queues:
                del self.task_queues[process_id]
            
            if process_id in self.result_queues:
                del self.result_queues[process_id]
            
            # Clean up any heartbeat threads
            if hasattr(self, 'heartbeat_threads') and process_id in self.heartbeat_threads:
                thread = self.heartbeat_threads[process_id]
                if thread.is_alive():
                    # Signal thread to stop (implementation would depend on thread design)
                    pass
                del self.heartbeat_threads[process_id]
            
            self.logger.debug(f"Successfully cleaned up resources for process {process_id}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to cleanup resources for process {process_id}: {e}")
            return False


# Convenience functions for common operations

def create_cli_interface(
    max_processes: int = 20,
    heartbeat_interval: int = 30
) -> CLIInterface:
    """
    Create a CLI interface with common configuration
    
    Args:
        max_processes: Maximum number of concurrent processes
        heartbeat_interval: Heartbeat interval in seconds
        
    Returns:
        Configured CLIInterface instance
    """
    heartbeat_config = HeartbeatConfig(
        interval_seconds=heartbeat_interval,
        timeout_seconds=heartbeat_interval * 2,
        max_missed_heartbeats=3,
        enabled=True
    )
    
    return CLIInterface(
        max_concurrent_processes=max_processes,
        heartbeat_config=heartbeat_config
    )