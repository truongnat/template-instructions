"""
Tests for Enhanced Agent Pool Management and Load Balancing

This module tests the enhanced agent pool management functionality including
load balancing algorithms, auto-scaling logic, and performance monitoring.
"""

import pytest
import time
from datetime import datetime, timedelta
from unittest.mock import Mock, patch

from agentic_sdlc.orchestration.engine.agent_pool import (
    EnhancedAgentPool, EnhancedLoadBalancer, LoadBalancingStrategy,
    AutoScalingPolicy, ScalingThresholds, LoadBalancingMetrics
)
from agentic_sdlc.orchestration.models.agent import (
    AgentType, ModelTier, ModelAssignment, AgentTask, AgentInstance,
    TaskPriority, TaskInput, TaskContext, InstanceStatus
)
from agentic_sdlc.orchestration.engine.model_optimizer import ModelOptimizer


class TestEnhancedLoadBalancer:
    """Test cases for EnhancedLoadBalancer"""
    
    def test_load_balancer_initialization(self):
        """Test load balancer initialization"""
        lb = EnhancedLoadBalancer(
            strategy=LoadBalancingStrategy.LEAST_LOADED,
            enable_health_checks=True,
            health_check_interval=30
        )
        
        assert lb.strategy == LoadBalancingStrategy.LEAST_LOADED
        assert lb.enable_health_checks is True
        assert lb.health_check_interval == 30
        assert isinstance(lb.metrics, LoadBalancingMetrics)
    
    def test_round_robin_selection(self):
        """Test round robin load balancing strategy"""
        lb = EnhancedLoadBalancer(strategy=LoadBalancingStrategy.ROUND_ROBIN)
        
        # Create test instances
        instances = [
            AgentInstance(agent_type=AgentType.IMPLEMENTATION),
            AgentInstance(agent_type=AgentType.IMPLEMENTATION),
            AgentInstance(agent_type=AgentType.IMPLEMENTATION)
        ]
        
        # Test round robin selection
        selected_instances = []
        for _ in range(6):  # Two full rounds
            selected = lb.select_instance(instances)
            selected_instances.append(selected.instance_id)
        
        # Should cycle through instances
        assert selected_instances[0] == selected_instances[3]  # First and fourth should be same
        assert selected_instances[1] == selected_instances[4]  # Second and fifth should be same
        assert selected_instances[2] == selected_instances[5]  # Third and sixth should be same
    
    def test_least_loaded_selection(self):
        """Test least loaded load balancing strategy"""
        lb = EnhancedLoadBalancer(strategy=LoadBalancingStrategy.LEAST_LOADED)
        
        # Create instances with different loads
        instance1 = AgentInstance(agent_type=AgentType.IMPLEMENTATION)
        instance2 = AgentInstance(agent_type=AgentType.IMPLEMENTATION)
        instance3 = AgentInstance(agent_type=AgentType.IMPLEMENTATION)
        
        # Add tasks to create different loads
        task1 = AgentTask(type="test", input=TaskInput(data={}), context=TaskContext(workflow_id="test", phase="test"))
        task2 = AgentTask(type="test", input=TaskInput(data={}), context=TaskContext(workflow_id="test", phase="test"))
        
        instance2.assign_task(task1)  # Instance2 has 1 task
        instance3.assign_task(task2)  # Instance3 has 1 task
        instance3.task_queue.append(task1)  # Instance3 has 1 more in queue
        
        instances = [instance1, instance2, instance3]
        
        # Should select instance1 (least loaded)
        selected = lb.select_instance(instances)
        assert selected.instance_id == instance1.instance_id
    
    def test_random_selection(self):
        """Test random load balancing strategy"""
        lb = EnhancedLoadBalancer(strategy=LoadBalancingStrategy.RANDOM)
        
        instances = [
            AgentInstance(agent_type=AgentType.IMPLEMENTATION),
            AgentInstance(agent_type=AgentType.IMPLEMENTATION),
            AgentInstance(agent_type=AgentType.IMPLEMENTATION)
        ]
        
        # Test multiple selections
        selected_ids = set()
        for _ in range(20):  # Multiple attempts to get different instances
            selected = lb.select_instance(instances)
            selected_ids.add(selected.instance_id)
        
        # Should have selected different instances (with high probability)
        assert len(selected_ids) > 1
    
    def test_metrics_update(self):
        """Test metrics updating"""
        lb = EnhancedLoadBalancer()
        
        # Update metrics
        lb.update_metrics(success=True, response_time=1.5)
        lb.update_metrics(success=False, response_time=2.0)
        lb.update_metrics(success=True, response_time=1.0)
        
        metrics = lb.get_metrics()
        assert metrics.total_requests == 3
        assert metrics.successful_requests == 2
        assert metrics.failed_requests == 1
        assert metrics.get_success_rate() == 2/3
        assert metrics.average_response_time == (1.5 + 2.0 + 1.0) / 3
        assert metrics.peak_response_time == 2.0


class TestScalingThresholds:
    """Test cases for ScalingThresholds"""
    
    def test_default_thresholds(self):
        """Test default scaling thresholds"""
        thresholds = ScalingThresholds()
        
        assert thresholds.scale_up_threshold == 0.8
        assert thresholds.scale_down_threshold == 0.3
        assert thresholds.min_instances == 1
        assert thresholds.max_instances == 10
        assert thresholds.scale_up_cooldown == 300
        assert thresholds.scale_down_cooldown == 600
        assert thresholds.queue_threshold == 5
    
    def test_custom_thresholds(self):
        """Test custom scaling thresholds"""
        thresholds = ScalingThresholds(
            scale_up_threshold=0.7,
            scale_down_threshold=0.2,
            min_instances=2,
            max_instances=5,
            scale_up_cooldown=120,
            scale_down_cooldown=300,
            queue_threshold=3
        )
        
        assert thresholds.scale_up_threshold == 0.7
        assert thresholds.scale_down_threshold == 0.2
        assert thresholds.min_instances == 2
        assert thresholds.max_instances == 5
        assert thresholds.scale_up_cooldown == 120
        assert thresholds.scale_down_cooldown == 300
        assert thresholds.queue_threshold == 3


class TestEnhancedAgentPool:
    """Test cases for EnhancedAgentPool"""
    
    @pytest.fixture
    def model_assignment(self):
        """Create a test model assignment"""
        return ModelAssignment(
            role_type=AgentType.IMPLEMENTATION,
            model_tier=ModelTier.OPERATIONAL,
            recommended_model="gpt-3.5-turbo",
            fallback_model="claude-3-haiku",
            max_concurrent_instances=5,
            cost_per_token=0.002
        )
    
    @pytest.fixture
    def scaling_thresholds(self):
        """Create test scaling thresholds"""
        return ScalingThresholds(
            scale_up_threshold=0.8,
            scale_down_threshold=0.3,
            min_instances=1,
            max_instances=3,
            scale_up_cooldown=1,  # Short cooldown for testing
            scale_down_cooldown=1,
            queue_threshold=2
        )
    
    def test_pool_initialization(self, model_assignment, scaling_thresholds):
        """Test agent pool initialization"""
        pool = EnhancedAgentPool(
            role_type=AgentType.IMPLEMENTATION,
            model_assignment=model_assignment,
            scaling_thresholds=scaling_thresholds,
            auto_scaling_policy=AutoScalingPolicy.REACTIVE
        )
        
        assert pool.role_type == AgentType.IMPLEMENTATION
        assert pool.model_assignment == model_assignment
        assert pool.scaling_thresholds == scaling_thresholds
        assert pool.auto_scaling_policy == AutoScalingPolicy.REACTIVE
        assert len(pool.active_instances) == scaling_thresholds.min_instances
        assert len(pool.queued_tasks) == 0
    
    def test_task_assignment_to_idle_instance(self, model_assignment, scaling_thresholds):
        """Test task assignment to idle instance"""
        pool = EnhancedAgentPool(
            role_type=AgentType.IMPLEMENTATION,
            model_assignment=model_assignment,
            scaling_thresholds=scaling_thresholds
        )
        
        task = AgentTask(
            type="test",
            input=TaskInput(data={}),
            context=TaskContext(workflow_id="test", phase="test")
        )
        
        # Assign task
        instance = pool.assign_task(task)
        
        assert instance is not None
        assert instance.current_task == task
        assert instance.status == InstanceStatus.BUSY
        assert task.assigned_instance_id == instance.instance_id
    
    def test_task_queuing_when_no_idle_instances(self, model_assignment, scaling_thresholds):
        """Test task queuing when no idle instances available"""
        # Set min instances to 1 and max to 1 to force queuing
        scaling_thresholds.min_instances = 1
        scaling_thresholds.max_instances = 1
        
        pool = EnhancedAgentPool(
            role_type=AgentType.IMPLEMENTATION,
            model_assignment=model_assignment,
            scaling_thresholds=scaling_thresholds
        )
        
        # Assign first task (should succeed)
        task1 = AgentTask(type="test1", input=TaskInput(data={}), context=TaskContext(workflow_id="test", phase="test"))
        instance1 = pool.assign_task(task1)
        assert instance1 is not None
        
        # Assign second task (should be queued)
        task2 = AgentTask(type="test2", input=TaskInput(data={}), context=TaskContext(workflow_id="test", phase="test"))
        instance2 = pool.assign_task(task2)
        assert instance2 is None
        assert len(pool.queued_tasks) == 1
        assert pool.queued_tasks[0] == task2
    
    def test_task_completion_and_next_assignment(self, model_assignment, scaling_thresholds):
        """Test task completion and assignment of next queued task"""
        pool = EnhancedAgentPool(
            role_type=AgentType.IMPLEMENTATION,
            model_assignment=model_assignment,
            scaling_thresholds=scaling_thresholds
        )
        
        # Get the initial instance
        instance = pool.active_instances[0]
        instance_id = instance.instance_id
        
        # Assign first task
        task1 = AgentTask(type="test1", input=TaskInput(data={}), context=TaskContext(workflow_id="test", phase="test"))
        pool.assign_task(task1)
        
        # Queue second task
        task2 = AgentTask(type="test2", input=TaskInput(data={}), context=TaskContext(workflow_id="test", phase="test"))
        pool.queued_tasks.append(task2)
        
        # Complete first task
        next_task = pool.complete_task(
            instance_id=instance_id,
            success=True,
            execution_time=1.5,
            quality_score=0.9
        )
        
        # Should return the queued task
        assert next_task == task2
        assert len(pool.queued_tasks) == 0
        assert instance.current_task == task2
    
    @patch('time.sleep')  # Mock sleep to speed up test
    def test_auto_scaling_up(self, mock_sleep, model_assignment, scaling_thresholds):
        """Test automatic scaling up based on load"""
        pool = EnhancedAgentPool(
            role_type=AgentType.IMPLEMENTATION,
            model_assignment=model_assignment,
            scaling_thresholds=scaling_thresholds
        )
        
        # Create high load by queuing many tasks
        for i in range(5):  # More than queue_threshold
            task = AgentTask(
                type=f"test{i}",
                input=TaskInput(data={}),
                context=TaskContext(workflow_id="test", phase="test")
            )
            pool.queued_tasks.append(task)
        
        # Manually trigger scaling evaluation
        pool._evaluate_scaling()
        
        # Should have scaled up
        assert len(pool.active_instances) > scaling_thresholds.min_instances
    
    def test_pool_status(self, model_assignment, scaling_thresholds):
        """Test getting pool status"""
        pool = EnhancedAgentPool(
            role_type=AgentType.IMPLEMENTATION,
            model_assignment=model_assignment,
            scaling_thresholds=scaling_thresholds
        )
        
        status = pool.get_pool_status()
        
        assert 'role_type' in status
        assert 'total_instances' in status
        assert 'idle_instances' in status
        assert 'busy_instances' in status
        assert 'failed_instances' in status
        assert 'queued_tasks' in status
        assert 'current_load' in status
        assert 'scaling_thresholds' in status
        assert 'load_balancer_strategy' in status
        
        assert status['role_type'] == AgentType.IMPLEMENTATION.value
        assert status['total_instances'] == scaling_thresholds.min_instances
        assert status['queued_tasks'] == 0
    
    def test_instance_details(self, model_assignment, scaling_thresholds):
        """Test getting instance details"""
        pool = EnhancedAgentPool(
            role_type=AgentType.IMPLEMENTATION,
            model_assignment=model_assignment,
            scaling_thresholds=scaling_thresholds
        )
        
        details = pool.get_instance_details()
        
        assert len(details) == scaling_thresholds.min_instances
        
        for detail in details:
            assert 'instance_id' in detail
            assert 'status' in detail
            assert 'current_task_id' in detail
            assert 'queued_tasks' in detail
            assert 'tasks_completed' in detail
            assert 'success_rate' in detail
            assert 'average_execution_time' in detail
            assert 'quality_score' in detail
            assert 'resource_utilization' in detail
            assert 'created_at' in detail
    
    def test_force_scaling(self, model_assignment, scaling_thresholds):
        """Test force scaling functionality"""
        pool = EnhancedAgentPool(
            role_type=AgentType.IMPLEMENTATION,
            model_assignment=model_assignment,
            scaling_thresholds=scaling_thresholds
        )
        
        initial_instances = len(pool.active_instances)
        
        # Force scale up
        success = pool.force_scale(target_instances=2)
        assert success is True
        assert len(pool.active_instances) == 2
        
        # Force scale down
        success = pool.force_scale(target_instances=1)
        assert success is True
        assert len(pool.active_instances) == 1


class TestModelOptimizerIntegration:
    """Test integration of enhanced agent pools with ModelOptimizer"""
    
    def test_model_optimizer_with_enhanced_pools(self):
        """Test ModelOptimizer initialization with enhanced pools"""
        optimizer = ModelOptimizer()
        
        # Check that enhanced pools were created
        assert len(optimizer.agent_pools) > 0
        
        for agent_type, pool in optimizer.agent_pools.items():
            assert isinstance(pool, EnhancedAgentPool)
            assert pool.role_type == agent_type
            assert isinstance(pool.load_balancer, EnhancedLoadBalancer)
    
    def test_task_allocation_with_enhanced_pools(self):
        """Test task allocation using enhanced pools"""
        optimizer = ModelOptimizer()
        
        task = AgentTask(
            type="implementation",
            input=TaskInput(data={"code": "print('hello')"}),
            context=TaskContext(workflow_id="test", phase="implementation"),
            priority=TaskPriority.MEDIUM
        )
        
        # Allocate instance
        instance = optimizer.allocate_agent_instance(AgentType.IMPLEMENTATION, task)
        
        # Should get an instance or task should be queued
        if instance:
            assert instance.agent_type == AgentType.IMPLEMENTATION
            assert instance.current_task == task
        else:
            # Task was queued
            pool = optimizer.agent_pools[AgentType.IMPLEMENTATION]
            assert len(pool.queued_tasks) > 0
    
    def test_instance_release_with_performance_data(self):
        """Test instance release with performance data"""
        optimizer = ModelOptimizer()
        
        task = AgentTask(
            type="implementation",
            input=TaskInput(data={"code": "print('hello')"}),
            context=TaskContext(workflow_id="test", phase="implementation"),
            priority=TaskPriority.MEDIUM
        )
        
        # Allocate instance
        instance = optimizer.allocate_agent_instance(AgentType.IMPLEMENTATION, task)
        
        if instance:
            # Release with performance data
            performance_data = {
                'success': True,
                'execution_time': 2.5,
                'quality': 0.95,
                'cost': 0.01,
                'tokens': 100
            }
            
            next_task = optimizer.release_agent_instance(
                AgentType.IMPLEMENTATION,
                instance.instance_id,
                performance_data
            )
            
            # Should complete successfully
            assert instance.performance.tasks_completed > 0
    
    def test_pool_status_retrieval(self):
        """Test retrieving pool status from ModelOptimizer"""
        optimizer = ModelOptimizer()
        
        # Get status for all pools
        all_status = optimizer.get_pool_status()
        assert len(all_status) > 0
        
        # Get status for specific pool
        impl_status = optimizer.get_pool_status(AgentType.IMPLEMENTATION)
        assert AgentType.IMPLEMENTATION.value in impl_status
    
    def test_load_balancing_strategy_update(self):
        """Test updating load balancing strategy"""
        optimizer = ModelOptimizer()
        
        # Update strategy
        success = optimizer.update_load_balancing_strategy(
            AgentType.IMPLEMENTATION,
            LoadBalancingStrategy.ROUND_ROBIN
        )
        
        assert success is True
        
        pool = optimizer.agent_pools[AgentType.IMPLEMENTATION]
        assert pool.load_balancer.strategy == LoadBalancingStrategy.ROUND_ROBIN
    
    def test_scaling_thresholds_update(self):
        """Test updating scaling thresholds"""
        optimizer = ModelOptimizer()
        
        new_thresholds = ScalingThresholds(
            scale_up_threshold=0.9,
            scale_down_threshold=0.1,
            min_instances=2,
            max_instances=4
        )
        
        success = optimizer.update_scaling_thresholds(
            AgentType.IMPLEMENTATION,
            new_thresholds
        )
        
        assert success is True
        
        pool = optimizer.agent_pools[AgentType.IMPLEMENTATION]
        assert pool.scaling_thresholds.scale_up_threshold == 0.9
        assert pool.scaling_thresholds.scale_down_threshold == 0.1
    
    def test_auto_scaling_recommendations(self):
        """Test getting auto-scaling recommendations"""
        optimizer = ModelOptimizer()
        
        recommendations = optimizer.get_auto_scaling_recommendations()
        
        assert 'immediate_actions' in recommendations
        assert 'suggested_optimizations' in recommendations
        assert 'performance_alerts' in recommendations
        
        assert isinstance(recommendations['immediate_actions'], list)
        assert isinstance(recommendations['suggested_optimizations'], list)
        assert isinstance(recommendations['performance_alerts'], list)


if __name__ == "__main__":
    pytest.main([__file__])