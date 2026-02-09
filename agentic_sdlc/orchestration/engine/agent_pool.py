"""
Agent Pool Management and Load Balancing for Multi-Agent Orchestration System

This module implements enhanced agent pool management with multiple load balancing
strategies, auto-scaling logic, and performance monitoring capabilities.

Requirements: 9.4, 9.5
"""

import asyncio
import logging
import random
import time
from datetime import datetime, timedelta
from enum import Enum
from typing import Dict, List, Optional, Any, Callable
from dataclasses import dataclass, field
from threading import Lock, Thread
from uuid import uuid4

from ..models.agent import (
    AgentType, AgentInstance, AgentTask, LoadMetrics, PerformanceMetrics,
    InstanceStatus, TaskPriority, ModelAssignment
)
from ..exceptions.agent import AgentPoolError, AgentInstanceError
from ..utils.logging import get_logger


class LoadBalancingStrategy(Enum):
    """Load balancing strategies"""
    ROUND_ROBIN = "round_robin"
    LEAST_LOADED = "least_loaded"
    RANDOM = "random"
    WEIGHTED_ROUND_ROBIN = "weighted_round_robin"
    LEAST_CONNECTIONS = "least_connections"
    RESPONSE_TIME = "response_time"


class AutoScalingPolicy(Enum):
    """Auto-scaling policies"""
    REACTIVE = "reactive"      # Scale based on current load
    PREDICTIVE = "predictive"  # Scale based on predicted load
    SCHEDULED = "scheduled"    # Scale based on schedule
    HYBRID = "hybrid"         # Combination of reactive and predictive


@dataclass
class ScalingThresholds:
    """Thresholds for auto-scaling decisions"""
    scale_up_threshold: float = 0.8      # Scale up when load > 80%
    scale_down_threshold: float = 0.3    # Scale down when load < 30%
    min_instances: int = 1               # Minimum instances to maintain
    max_instances: int = 10              # Maximum instances allowed
    scale_up_cooldown: int = 300         # Cooldown period in seconds
    scale_down_cooldown: int = 600       # Cooldown period in seconds
    queue_threshold: int = 5             # Scale up when queue > 5 tasks


@dataclass
class LoadBalancingMetrics:
    """Enhanced load balancing metrics"""
    total_requests: int = 0
    successful_requests: int = 0
    failed_requests: int = 0
    average_response_time: float = 0.0
    peak_response_time: float = 0.0
    current_load: float = 0.0
    peak_load: float = 0.0
    queue_length: int = 0
    active_connections: int = 0
    last_updated: datetime = field(default_factory=datetime.now)
    
    def update_request_metrics(self, success: bool, response_time: float):
        """Update request metrics"""
        self.total_requests += 1
        if success:
            self.successful_requests += 1
        else:
            self.failed_requests += 1
        
        # Update response time metrics
        if self.total_requests == 1:
            self.average_response_time = response_time
        else:
            self.average_response_time = (
                (self.average_response_time * (self.total_requests - 1) + response_time) 
                / self.total_requests
            )
        
        self.peak_response_time = max(self.peak_response_time, response_time)
        self.last_updated = datetime.now()
    
    def get_success_rate(self) -> float:
        """Get success rate"""
        if self.total_requests == 0:
            return 1.0
        return self.successful_requests / self.total_requests


class EnhancedLoadBalancer:
    """
    Enhanced load balancer with multiple strategies and performance monitoring
    """
    
    def __init__(
        self,
        strategy: LoadBalancingStrategy = LoadBalancingStrategy.LEAST_LOADED,
        enable_health_checks: bool = True,
        health_check_interval: int = 30
    ):
        """
        Initialize the enhanced load balancer
        
        Args:
            strategy: Load balancing strategy to use
            enable_health_checks: Whether to enable health checks
            health_check_interval: Health check interval in seconds
        """
        self.logger = get_logger(__name__)
        self.strategy = strategy
        self.enable_health_checks = enable_health_checks
        self.health_check_interval = health_check_interval
        
        self.metrics = LoadBalancingMetrics()
        self._round_robin_index = 0
        self._lock = Lock()
        
        # Health check thread
        self._health_check_thread: Optional[Thread] = None
        self._stop_health_checks = False
        
        if self.enable_health_checks:
            self._start_health_checks()
    
    def _start_health_checks(self):
        """Start health check monitoring"""
        def health_check_loop():
            while not self._stop_health_checks:
                try:
                    time.sleep(self.health_check_interval)
                    # Health checks will be implemented by the pool
                except Exception as e:
                    self.logger.error(f"Health check error: {e}")
        
        self._health_check_thread = Thread(target=health_check_loop, daemon=True)
        self._health_check_thread.start()
        self.logger.info("Started health check monitoring")
    
    def select_instance(
        self,
        instances: List[AgentInstance],
        task: Optional[AgentTask] = None
    ) -> Optional[AgentInstance]:
        """
        Select an instance based on the load balancing strategy
        
        Args:
            instances: Available instances
            task: Task to be assigned (optional, used for weighted selection)
            
        Returns:
            Selected instance or None if no suitable instance found
        """
        if not instances:
            return None
        
        # Filter healthy instances
        healthy_instances = [
            instance for instance in instances 
            if instance.status in [InstanceStatus.IDLE, InstanceStatus.BUSY]
        ]
        
        if not healthy_instances:
            return None
        
        with self._lock:
            if self.strategy == LoadBalancingStrategy.ROUND_ROBIN:
                return self._round_robin_selection(healthy_instances)
            
            elif self.strategy == LoadBalancingStrategy.LEAST_LOADED:
                return self._least_loaded_selection(healthy_instances)
            
            elif self.strategy == LoadBalancingStrategy.RANDOM:
                return random.choice(healthy_instances)
            
            elif self.strategy == LoadBalancingStrategy.WEIGHTED_ROUND_ROBIN:
                return self._weighted_round_robin_selection(healthy_instances, task)
            
            elif self.strategy == LoadBalancingStrategy.LEAST_CONNECTIONS:
                return self._least_connections_selection(healthy_instances)
            
            elif self.strategy == LoadBalancingStrategy.RESPONSE_TIME:
                return self._response_time_selection(healthy_instances)
            
            else:
                # Default to round robin
                return self._round_robin_selection(healthy_instances)
    
    def _round_robin_selection(self, instances: List[AgentInstance]) -> AgentInstance:
        """Round robin selection"""
        instance = instances[self._round_robin_index % len(instances)]
        self._round_robin_index = (self._round_robin_index + 1) % len(instances)
        return instance
    
    def _least_loaded_selection(self, instances: List[AgentInstance]) -> AgentInstance:
        """Select instance with least load"""
        return min(instances, key=lambda i: self._calculate_instance_load(i))
    
    def _weighted_round_robin_selection(
        self,
        instances: List[AgentInstance],
        task: Optional[AgentTask]
    ) -> AgentInstance:
        """Weighted round robin based on instance performance"""
        if not task:
            return self._round_robin_selection(instances)
        
        # Calculate weights based on performance metrics
        weights = []
        for instance in instances:
            # Higher performance = higher weight
            weight = (
                instance.performance.success_rate * 0.4 +
                instance.performance.quality_score * 0.3 +
                (1.0 - instance.performance.resource_utilization) * 0.3
            )
            weights.append(max(weight, 0.1))  # Minimum weight of 0.1
        
        # Weighted random selection
        total_weight = sum(weights)
        if total_weight == 0:
            return self._round_robin_selection(instances)
        
        r = random.uniform(0, total_weight)
        cumulative_weight = 0
        
        for i, weight in enumerate(weights):
            cumulative_weight += weight
            if r <= cumulative_weight:
                return instances[i]
        
        return instances[-1]  # Fallback
    
    def _least_connections_selection(self, instances: List[AgentInstance]) -> AgentInstance:
        """Select instance with least active connections"""
        return min(instances, key=lambda i: len(i.task_queue) + (1 if i.current_task else 0))
    
    def _response_time_selection(self, instances: List[AgentInstance]) -> AgentInstance:
        """Select instance with best response time"""
        return min(instances, key=lambda i: i.performance.average_execution_time)
    
    def _calculate_instance_load(self, instance: AgentInstance) -> float:
        """Calculate load for an instance"""
        base_load = 0.0
        
        # Current task load
        if instance.current_task:
            base_load += 1.0
        
        # Queue load
        base_load += len(instance.task_queue) * 0.5
        
        # Resource utilization
        base_load += instance.performance.resource_utilization
        
        return base_load
    
    def update_metrics(self, success: bool, response_time: float):
        """Update load balancer metrics"""
        with self._lock:
            self.metrics.update_request_metrics(success, response_time)
    
    def get_metrics(self) -> LoadBalancingMetrics:
        """Get current metrics"""
        with self._lock:
            return self.metrics
    
    def cleanup(self):
        """Cleanup resources"""
        self._stop_health_checks = True
        if self._health_check_thread:
            self._health_check_thread.join(timeout=5)
        self.logger.info("Load balancer cleanup completed")


class EnhancedAgentPool:
    """
    Enhanced agent pool with auto-scaling and advanced load balancing
    """
    
    def __init__(
        self,
        role_type: AgentType,
        model_assignment: ModelAssignment,
        scaling_thresholds: Optional[ScalingThresholds] = None,
        load_balancer: Optional[EnhancedLoadBalancer] = None,
        auto_scaling_policy: AutoScalingPolicy = AutoScalingPolicy.REACTIVE
    ):
        """
        Initialize the enhanced agent pool
        
        Args:
            role_type: Type of agents in this pool
            model_assignment: Model assignment for agents
            scaling_thresholds: Auto-scaling thresholds
            load_balancer: Load balancer instance
            auto_scaling_policy: Auto-scaling policy
        """
        self.logger = get_logger(__name__)
        self.role_type = role_type
        self.model_assignment = model_assignment
        self.scaling_thresholds = scaling_thresholds or ScalingThresholds()
        self.auto_scaling_policy = auto_scaling_policy
        
        # Override max instances from model assignment
        self.scaling_thresholds.max_instances = model_assignment.max_concurrent_instances
        
        self.load_balancer = load_balancer or EnhancedLoadBalancer()
        
        # Pool state
        self.active_instances: List[AgentInstance] = []
        self.queued_tasks: List[AgentTask] = []
        self._lock = Lock()
        
        # Auto-scaling state
        self._last_scale_up = datetime.min
        self._last_scale_down = datetime.min
        self._scaling_in_progress = False
        
        # Monitoring thread
        self._monitor_thread: Optional[Thread] = None
        self._stop_monitoring = False
        
        # Performance tracking
        self.pool_metrics = LoadBalancingMetrics()
        
        # Initialize with minimum instances
        self._initialize_pool()
        
        # Start monitoring
        self._start_monitoring()
        
        self.logger.info(f"Initialized enhanced agent pool for {role_type.value} "
                        f"with {len(self.active_instances)} instances")
    
    def _initialize_pool(self):
        """Initialize pool with minimum instances"""
        for _ in range(self.scaling_thresholds.min_instances):
            instance = self._create_instance()
            self.active_instances.append(instance)
    
    def _create_instance(self) -> AgentInstance:
        """Create a new agent instance"""
        instance = AgentInstance(
            agent_type=self.role_type,
            model_assignment=self.model_assignment
        )
        self.logger.debug(f"Created new instance {instance.instance_id} for {self.role_type.value}")
        return instance
    
    def _start_monitoring(self):
        """Start pool monitoring thread"""
        def monitor_loop():
            while not self._stop_monitoring:
                try:
                    time.sleep(30)  # Monitor every 30 seconds
                    self._monitor_pool_health()
                    self._evaluate_scaling()
                except Exception as e:
                    self.logger.error(f"Pool monitoring error: {e}")
        
        self._monitor_thread = Thread(target=monitor_loop, daemon=True)
        self._monitor_thread.start()
        self.logger.info("Started pool monitoring")
    
    def _monitor_pool_health(self):
        """Monitor pool health and performance"""
        with self._lock:
            # Update pool metrics
            total_instances = len(self.active_instances)
            idle_instances = len([i for i in self.active_instances if i.status == InstanceStatus.IDLE])
            busy_instances = total_instances - idle_instances
            
            # Calculate current load
            if total_instances > 0:
                current_load = busy_instances / total_instances
                self.pool_metrics.current_load = current_load
                self.pool_metrics.peak_load = max(self.pool_metrics.peak_load, current_load)
            
            self.pool_metrics.queue_length = len(self.queued_tasks)
            self.pool_metrics.active_connections = busy_instances
            self.pool_metrics.last_updated = datetime.now()
            
            # Check for failed instances
            failed_instances = [i for i in self.active_instances if i.status == InstanceStatus.FAILED]
            for instance in failed_instances:
                self._handle_failed_instance(instance)
    
    def _handle_failed_instance(self, instance: AgentInstance):
        """Handle a failed instance"""
        self.logger.warning(f"Handling failed instance {instance.instance_id}")
        
        # Move current task back to queue if exists
        if instance.current_task:
            self.queued_tasks.insert(0, instance.current_task)
        
        # Move queued tasks back to main queue
        self.queued_tasks.extend(instance.task_queue)
        
        # Remove failed instance
        self.active_instances.remove(instance)
        
        # Create replacement if needed
        if len(self.active_instances) < self.scaling_thresholds.min_instances:
            replacement = self._create_instance()
            self.active_instances.append(replacement)
            self.logger.info(f"Created replacement instance {replacement.instance_id}")
    
    def _evaluate_scaling(self):
        """Evaluate if scaling is needed"""
        if self._scaling_in_progress:
            return
        
        current_time = datetime.now()
        current_load = self.pool_metrics.current_load
        queue_length = len(self.queued_tasks)
        
        # Check scale up conditions
        should_scale_up = (
            (current_load > self.scaling_thresholds.scale_up_threshold or
             queue_length > self.scaling_thresholds.queue_threshold) and
            len(self.active_instances) < self.scaling_thresholds.max_instances and
            (current_time - self._last_scale_up).total_seconds() > self.scaling_thresholds.scale_up_cooldown
        )
        
        # Check scale down conditions
        should_scale_down = (
            current_load < self.scaling_thresholds.scale_down_threshold and
            queue_length == 0 and
            len(self.active_instances) > self.scaling_thresholds.min_instances and
            (current_time - self._last_scale_down).total_seconds() > self.scaling_thresholds.scale_down_cooldown
        )
        
        if should_scale_up:
            self._scale_up()
        elif should_scale_down:
            self._scale_down()
    
    def _scale_up(self):
        """Scale up the pool"""
        with self._lock:
            if len(self.active_instances) >= self.scaling_thresholds.max_instances:
                return
            
            self._scaling_in_progress = True
            try:
                new_instance = self._create_instance()
                self.active_instances.append(new_instance)
                self._last_scale_up = datetime.now()
                
                self.logger.info(f"Scaled up {self.role_type.value} pool to {len(self.active_instances)} instances")
                
                # Assign queued tasks to new instance
                if self.queued_tasks:
                    task = self.queued_tasks.pop(0)
                    new_instance.assign_task(task)
                    
            finally:
                self._scaling_in_progress = False
    
    def _scale_down(self):
        """Scale down the pool"""
        with self._lock:
            if len(self.active_instances) <= self.scaling_thresholds.min_instances:
                return
            
            # Find idle instance to remove
            idle_instances = [i for i in self.active_instances if i.status == InstanceStatus.IDLE]
            if not idle_instances:
                return
            
            self._scaling_in_progress = True
            try:
                instance_to_remove = idle_instances[0]
                instance_to_remove.status = InstanceStatus.SCALING_DOWN
                self.active_instances.remove(instance_to_remove)
                self._last_scale_down = datetime.now()
                
                self.logger.info(f"Scaled down {self.role_type.value} pool to {len(self.active_instances)} instances")
                
            finally:
                self._scaling_in_progress = False
    
    def assign_task(self, task: AgentTask) -> Optional[AgentInstance]:
        """
        Assign a task to an available instance
        
        Args:
            task: Task to assign
            
        Returns:
            Assigned instance or None if task was queued
        """
        with self._lock:
            # Get available instances
            available_instances = [
                i for i in self.active_instances 
                if i.status == InstanceStatus.IDLE
            ]
            
            if available_instances:
                # Use load balancer to select instance
                selected_instance = self.load_balancer.select_instance(available_instances, task)
                
                if selected_instance:
                    selected_instance.assign_task(task)
                    self.logger.info(f"Assigned task {task.id} to instance {selected_instance.instance_id}")
                    return selected_instance
            
            # No available instances, queue the task
            self.queued_tasks.append(task)
            self.logger.info(f"Queued task {task.id} for {self.role_type.value} pool")
            
            # Trigger scaling evaluation
            self._evaluate_scaling()
            
            return None
    
    def complete_task(
        self,
        instance_id: str,
        success: bool = True,
        execution_time: float = 0.0,
        quality_score: float = 1.0
    ) -> Optional[AgentTask]:
        """
        Complete a task and update metrics
        
        Args:
            instance_id: ID of instance that completed the task
            success: Whether the task was successful
            execution_time: Task execution time
            quality_score: Quality score of the result
            
        Returns:
            Next task assigned to the instance or None
        """
        with self._lock:
            # Find the instance
            instance = None
            for inst in self.active_instances:
                if inst.instance_id == instance_id:
                    instance = inst
                    break
            
            if not instance:
                self.logger.error(f"Instance {instance_id} not found in pool")
                return None
            
            # Complete current task
            completed_task = instance.complete_current_task()
            
            if completed_task:
                # Update instance performance metrics
                instance.performance.update_metrics(execution_time, success, quality_score)
                
                # Update pool metrics
                self.pool_metrics.update_request_metrics(success, execution_time)
                
                # Update load balancer metrics
                self.load_balancer.update_metrics(success, execution_time)
                
                self.logger.debug(f"Completed task {completed_task.id} on instance {instance_id}")
            
            # Assign next queued task if available
            if self.queued_tasks and instance.status == InstanceStatus.IDLE:
                next_task = self.queued_tasks.pop(0)
                instance.assign_task(next_task)
                self.logger.info(f"Assigned queued task {next_task.id} to instance {instance_id}")
                return next_task
            
            return None
    
    def get_pool_status(self) -> Dict[str, Any]:
        """Get comprehensive pool status"""
        with self._lock:
            idle_instances = [i for i in self.active_instances if i.status == InstanceStatus.IDLE]
            busy_instances = [i for i in self.active_instances if i.status == InstanceStatus.BUSY]
            failed_instances = [i for i in self.active_instances if i.status == InstanceStatus.FAILED]
            
            return {
                'role_type': self.role_type.value,
                'total_instances': len(self.active_instances),
                'idle_instances': len(idle_instances),
                'busy_instances': len(busy_instances),
                'failed_instances': len(failed_instances),
                'queued_tasks': len(self.queued_tasks),
                'current_load': self.pool_metrics.current_load,
                'peak_load': self.pool_metrics.peak_load,
                'success_rate': self.pool_metrics.get_success_rate(),
                'average_response_time': self.pool_metrics.average_response_time,
                'scaling_thresholds': {
                    'min_instances': self.scaling_thresholds.min_instances,
                    'max_instances': self.scaling_thresholds.max_instances,
                    'scale_up_threshold': self.scaling_thresholds.scale_up_threshold,
                    'scale_down_threshold': self.scaling_thresholds.scale_down_threshold
                },
                'load_balancer_strategy': self.load_balancer.strategy.value,
                'last_updated': self.pool_metrics.last_updated.isoformat()
            }
    
    def get_instance_details(self) -> List[Dict[str, Any]]:
        """Get detailed information about all instances"""
        with self._lock:
            return [
                {
                    'instance_id': instance.instance_id,
                    'status': instance.status.value,
                    'current_task_id': instance.current_task.id if instance.current_task else None,
                    'queued_tasks': len(instance.task_queue),
                    'tasks_completed': instance.performance.tasks_completed,
                    'success_rate': instance.performance.success_rate,
                    'average_execution_time': instance.performance.average_execution_time,
                    'quality_score': instance.performance.quality_score,
                    'resource_utilization': instance.performance.resource_utilization,
                    'created_at': instance.created_at.isoformat()
                }
                for instance in self.active_instances
            ]
    
    def update_scaling_thresholds(self, thresholds: ScalingThresholds):
        """Update scaling thresholds"""
        with self._lock:
            self.scaling_thresholds = thresholds
            # Ensure max instances doesn't exceed model assignment limit
            self.scaling_thresholds.max_instances = min(
                thresholds.max_instances,
                self.model_assignment.max_concurrent_instances
            )
            self.logger.info(f"Updated scaling thresholds for {self.role_type.value} pool")
    
    def force_scale(self, target_instances: int) -> bool:
        """
        Force scaling to a specific number of instances
        
        Args:
            target_instances: Target number of instances
            
        Returns:
            True if scaling was successful
        """
        with self._lock:
            if target_instances < self.scaling_thresholds.min_instances:
                target_instances = self.scaling_thresholds.min_instances
            elif target_instances > self.scaling_thresholds.max_instances:
                target_instances = self.scaling_thresholds.max_instances
            
            current_instances = len(self.active_instances)
            
            if target_instances > current_instances:
                # Scale up
                for _ in range(target_instances - current_instances):
                    new_instance = self._create_instance()
                    self.active_instances.append(new_instance)
                
                self.logger.info(f"Force scaled up {self.role_type.value} pool to {target_instances} instances")
                
            elif target_instances < current_instances:
                # Scale down
                idle_instances = [i for i in self.active_instances if i.status == InstanceStatus.IDLE]
                instances_to_remove = min(len(idle_instances), current_instances - target_instances)
                
                for i in range(instances_to_remove):
                    instance = idle_instances[i]
                    instance.status = InstanceStatus.SCALING_DOWN
                    self.active_instances.remove(instance)
                
                self.logger.info(f"Force scaled down {self.role_type.value} pool to {len(self.active_instances)} instances")
            
            return True
    
    def cleanup(self):
        """Cleanup pool resources"""
        self._stop_monitoring = True
        if self._monitor_thread:
            self._monitor_thread.join(timeout=5)
        
        self.load_balancer.cleanup()
        
        with self._lock:
            # Mark all instances for cleanup
            for instance in self.active_instances:
                instance.status = InstanceStatus.SCALING_DOWN
        
        self.logger.info(f"Cleaned up {self.role_type.value} pool")