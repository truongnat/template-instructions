"""
Unit tests for the ModelOptimizer class

This module contains comprehensive unit tests for the ModelOptimizer class,
testing hierarchical model assignment, cost optimization, resource allocation,
and performance monitoring capabilities.
"""

import json
import pytest
import tempfile
from datetime import datetime, timedelta
from pathlib import Path
from unittest.mock import Mock, patch

from agentic_sdlc.orchestration.engine.model_optimizer import (
    ModelOptimizer, OptimizationStrategy, ResourceConstraint,
    CostMetrics, ResourceBudget, ModelPerformanceData
)
from agentic_sdlc.orchestration.models import (
    AgentType, ModelTier, ModelAssignment, AgentTask, TaskInput, TaskContext,
    TaskPriority, DataFormat, TaskRequirement, AgentInstance, InstanceStatus
)
from agentic_sdlc.orchestration.exceptions.model import (
    ModelOptimizationError, InsufficientResourcesError, InvalidModelAssignmentError
)


class TestModelOptimizer:
    """Test cases for ModelOptimizer class"""
    
    @pytest.fixture
    def temp_data_file(self):
        """Create a temporary file for testing data persistence"""
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.json') as f:
            temp_path = Path(f.name)
        yield temp_path
        # Cleanup
        if temp_path.exists():
            temp_path.unlink()
    
    @pytest.fixture
    def sample_model_assignments(self):
        """Sample model assignments for testing"""
        return [
            ModelAssignment(
                role_type=AgentType.PM,
                model_tier=ModelTier.STRATEGIC,
                recommended_model="gpt-4-turbo",
                fallback_model="gpt-4",
                max_concurrent_instances=3,
                cost_per_token=0.01
            ),
            ModelAssignment(
                role_type=AgentType.IMPLEMENTATION,
                model_tier=ModelTier.OPERATIONAL,
                recommended_model="gpt-3.5-turbo",
                fallback_model="claude-3-haiku",
                max_concurrent_instances=5,
                cost_per_token=0.002
            ),
            ModelAssignment(
                role_type=AgentType.RESEARCH,
                model_tier=ModelTier.RESEARCH,
                recommended_model="gpt-4-mini",
                fallback_model="claude-3-haiku",
                max_concurrent_instances=4,
                cost_per_token=0.0015
            )
        ]
    
    @pytest.fixture
    def sample_budget(self):
        """Sample resource budget for testing"""
        return ResourceBudget(
            max_daily_cost=50.0,
            max_concurrent_instances=10,
            max_tokens_per_hour=500000
        )
    
    @pytest.fixture
    def sample_task(self):
        """Sample agent task for testing"""
        return AgentTask(
            type="analysis",
            input=TaskInput(data={"requirement": "Analyze user authentication flow"}),
            context=TaskContext(workflow_id="test-workflow", phase="analysis"),
            requirements=[
                TaskRequirement(
                    requirement_id="req-1",
                    description="Must include security considerations"
                )
            ],
            priority=TaskPriority.HIGH
        )
    
    def test_initialization_with_defaults(self, temp_data_file):
        """Test ModelOptimizer initialization with default parameters"""
        optimizer = ModelOptimizer(data_file=temp_data_file)
        
        assert optimizer.strategy == OptimizationStrategy.BALANCED
        assert len(optimizer.model_assignments) == 6  # DEFAULT_MODEL_ASSIGNMENTS
        assert optimizer.budget.max_daily_cost == 100.0
        assert len(optimizer.agent_pools) == 6
        
        # Check that agent pools are initialized for each agent type
        for agent_type in AgentType:
            assert agent_type in optimizer.agent_pools
    
    def test_initialization_with_custom_parameters(self, temp_data_file, sample_model_assignments, sample_budget):
        """Test ModelOptimizer initialization with custom parameters"""
        optimizer = ModelOptimizer(
            model_assignments=sample_model_assignments,
            budget=sample_budget,
            strategy=OptimizationStrategy.COST_OPTIMIZED,
            data_file=temp_data_file
        )
        
        assert optimizer.strategy == OptimizationStrategy.COST_OPTIMIZED
        assert len(optimizer.model_assignments) == 3
        assert optimizer.budget.max_daily_cost == 50.0
        assert len(optimizer.agent_pools) == 3
    
    def test_select_model_for_agent_strategic_tier(self, temp_data_file, sample_task):
        """Test model selection for strategic tier agents (PM, BA, SA)"""
        optimizer = ModelOptimizer(data_file=temp_data_file)
        
        # Test PM agent
        model_name, assignment = optimizer.select_model_for_agent(AgentType.PM, sample_task)
        assert assignment.model_tier == ModelTier.STRATEGIC
        assert model_name in [assignment.recommended_model, assignment.fallback_model]
        
        # Test with high complexity task - should prefer recommended model
        high_complexity_task = AgentTask(
            type="design",
            input=TaskInput(data={"complex_requirement": "Design distributed system architecture"}),
            context=TaskContext(workflow_id="test", phase="design", dependencies=["req1", "req2", "req3"]),
            priority=TaskPriority.CRITICAL,
            requirements=[TaskRequirement(f"req-{i}", f"Requirement {i}") for i in range(5)]
        )
        
        optimizer.strategy = OptimizationStrategy.QUALITY_FIRST
        model_name, assignment = optimizer.select_model_for_agent(AgentType.SA, high_complexity_task)
        assert model_name == assignment.recommended_model
    
    def test_select_model_for_agent_operational_tier(self, temp_data_file, sample_task):
        """Test model selection for operational tier agents (Implementation)"""
        optimizer = ModelOptimizer(data_file=temp_data_file)
        
        # Test Implementation agent
        model_name, assignment = optimizer.select_model_for_agent(AgentType.IMPLEMENTATION, sample_task)
        assert assignment.model_tier == ModelTier.OPERATIONAL
        assert model_name in [assignment.recommended_model, assignment.fallback_model]
        
        # Test cost-optimized strategy - should prefer fallback model
        optimizer.strategy = OptimizationStrategy.COST_OPTIMIZED
        model_name, assignment = optimizer.select_model_for_agent(AgentType.IMPLEMENTATION, sample_task)
        assert model_name == assignment.fallback_model
    
    def test_select_model_for_agent_research_tier(self, temp_data_file, sample_task):
        """Test model selection for research tier agents (Research, Quality Judge)"""
        optimizer = ModelOptimizer(data_file=temp_data_file)
        
        # Test Research agent
        model_name, assignment = optimizer.select_model_for_agent(AgentType.RESEARCH, sample_task)
        assert assignment.model_tier == ModelTier.RESEARCH
        assert model_name in [assignment.recommended_model, assignment.fallback_model]
        
        # Test Quality Judge agent
        model_name, assignment = optimizer.select_model_for_agent(AgentType.QUALITY_JUDGE, sample_task)
        assert assignment.model_tier == ModelTier.RESEARCH
        assert model_name in [assignment.recommended_model, assignment.fallback_model]
    
    def test_select_model_invalid_agent_type(self, temp_data_file, sample_task):
        """Test model selection with invalid agent type"""
        optimizer = ModelOptimizer(data_file=temp_data_file)
        
        # Remove an assignment to simulate missing agent type
        optimizer.model_assignments = [a for a in optimizer.model_assignments if a.role_type != AgentType.PM]
        optimizer._assignment_by_type = {a.role_type: a for a in optimizer.model_assignments}
        
        with pytest.raises(InvalidModelAssignmentError) as exc_info:
            optimizer.select_model_for_agent(AgentType.PM, sample_task)
        
        assert "No model assignment found for agent type: AgentType.PM" in str(exc_info.value)
    
    def test_task_complexity_analysis(self, temp_data_file):
        """Test task complexity analysis algorithm"""
        optimizer = ModelOptimizer(data_file=temp_data_file)
        
        # Simple task
        simple_task = AgentTask(
            type="documentation",
            priority=TaskPriority.LOW,
            context=TaskContext(workflow_id="test", phase="docs")
        )
        complexity = optimizer._analyze_task_complexity(simple_task)
        assert 0.0 <= complexity <= 1.0
        assert complexity < 0.5  # Documentation should be low complexity
        
        # Complex task
        complex_task = AgentTask(
            type="design",
            priority=TaskPriority.CRITICAL,
            context=TaskContext(
                workflow_id="test", 
                phase="architecture",
                dependencies=["req1", "req2", "req3", "req4"]
            ),
            requirements=[TaskRequirement(f"req-{i}", f"Requirement {i}") for i in range(8)]
        )
        complexity = optimizer._analyze_task_complexity(complex_task)
        assert 0.0 <= complexity <= 1.0
        assert complexity > 0.7  # Design with many requirements should be high complexity
    
    def test_resource_constraint_validation(self, temp_data_file, sample_task):
        """Test resource constraint validation"""
        budget = ResourceBudget(max_daily_cost=10.0, max_concurrent_instances=2)
        optimizer = ModelOptimizer(budget=budget, data_file=temp_data_file)
        
        # Simulate exceeding daily budget
        optimizer.cost_metrics.total_cost = 15.0
        optimizer.cost_metrics.last_updated = datetime.now()
        
        assignment = optimizer._assignment_by_type[AgentType.PM]
        
        with pytest.raises(InsufficientResourcesError) as exc_info:
            optimizer._validate_resource_constraints(assignment, [ResourceConstraint.BUDGET])
        
        assert "Daily budget exceeded" in str(exc_info.value)
    
    def test_agent_instance_allocation(self, temp_data_file, sample_task):
        """Test agent instance allocation from pools"""
        optimizer = ModelOptimizer(data_file=temp_data_file)
        
        # Allocate an instance
        instance = optimizer.allocate_agent_instance(AgentType.PM, sample_task)
        assert instance is not None
        assert instance.agent_type == AgentType.PM
        assert instance.status == InstanceStatus.BUSY
        assert instance.current_task == sample_task
        
        # Check that the instance was added to the pool
        pool = optimizer.agent_pools[AgentType.PM]
        assert len(pool.active_instances) == 1
        assert pool.active_instances[0] == instance
    
    def test_agent_instance_allocation_at_capacity(self, temp_data_file, sample_task):
        """Test agent instance allocation when pool is at capacity"""
        # Create optimizer with small pool size
        assignments = [
            ModelAssignment(
                role_type=AgentType.PM,
                model_tier=ModelTier.STRATEGIC,
                recommended_model="gpt-4",
                fallback_model="gpt-3.5-turbo",
                max_concurrent_instances=1,  # Small pool
                cost_per_token=0.01
            )
        ]
        optimizer = ModelOptimizer(model_assignments=assignments, data_file=temp_data_file)
        
        # Allocate first instance (should succeed)
        instance1 = optimizer.allocate_agent_instance(AgentType.PM, sample_task)
        assert instance1 is not None
        
        # Try to allocate second instance (should queue the task)
        task2 = AgentTask(type="analysis", context=TaskContext(workflow_id="test2", phase="analysis"))
        instance2 = optimizer.allocate_agent_instance(AgentType.PM, task2)
        assert instance2 is None  # No instance available
        
        # Check that task was queued
        pool = optimizer.agent_pools[AgentType.PM]
        assert len(pool.queued_tasks) == 1
        assert pool.queued_tasks[0] == task2
    
    def test_agent_instance_release(self, temp_data_file, sample_task):
        """Test releasing agent instances back to the pool"""
        optimizer = ModelOptimizer(data_file=temp_data_file)
        
        # Allocate an instance
        instance = optimizer.allocate_agent_instance(AgentType.PM, sample_task)
        instance_id = instance.instance_id
        
        # Release the instance with performance data
        performance_data = {
            'success': True,
            'latency': 2.5,
            'quality': 0.9,
            'cost': 0.05,
            'tokens': 1000
        }
        
        optimizer.release_agent_instance(AgentType.PM, instance_id, performance_data)
        
        # Check that instance is now idle
        assert instance.status == InstanceStatus.IDLE
        assert instance.current_task is None
        
        # Check that performance data was updated
        model_name = instance.model_assignment.recommended_model
        perf_key = f"{model_name}_{AgentType.PM.value}"
        assert perf_key in optimizer.performance_data
        
        perf = optimizer.performance_data[perf_key]
        assert perf.total_requests == 1
        assert perf.success_rate == 1.0
        assert perf.average_latency == 2.5
        assert perf.quality_score == 0.9
    
    def test_agent_instance_release_with_queued_task(self, temp_data_file, sample_task):
        """Test releasing instance when there are queued tasks"""
        # Create optimizer with small pool
        assignments = [
            ModelAssignment(
                role_type=AgentType.PM,
                model_tier=ModelTier.STRATEGIC,
                recommended_model="gpt-4",
                fallback_model="gpt-3.5-turbo",
                max_concurrent_instances=1,
                cost_per_token=0.01
            )
        ]
        optimizer = ModelOptimizer(model_assignments=assignments, data_file=temp_data_file)
        
        # Allocate instance and queue a task
        instance = optimizer.allocate_agent_instance(AgentType.PM, sample_task)
        task2 = AgentTask(type="analysis", context=TaskContext(workflow_id="test2", phase="analysis"))
        optimizer.allocate_agent_instance(AgentType.PM, task2)  # This will queue task2
        
        # Release the instance
        optimizer.release_agent_instance(AgentType.PM, instance.instance_id)
        
        # Check that queued task was assigned
        assert instance.current_task == task2
        assert instance.status == InstanceStatus.BUSY
        assert len(optimizer.agent_pools[AgentType.PM].queued_tasks) == 0
    
    def test_performance_data_update(self, temp_data_file):
        """Test performance data tracking and updates"""
        optimizer = ModelOptimizer(data_file=temp_data_file)
        
        # Update performance data multiple times
        optimizer._update_performance_data(
            "gpt-4", AgentType.PM, 
            {'success': True, 'latency': 2.0, 'quality': 0.9, 'cost': 0.05, 'tokens': 1000}
        )
        optimizer._update_performance_data(
            "gpt-4", AgentType.PM,
            {'success': False, 'latency': 3.0, 'quality': 0.7, 'cost': 0.06, 'tokens': 1200}
        )
        
        perf_key = f"gpt-4_{AgentType.PM.value}"
        perf = optimizer.performance_data[perf_key]
        
        assert perf.total_requests == 2
        assert perf.success_rate == 0.5  # 1 success out of 2
        assert perf.average_latency == 2.5  # (2.0 + 3.0) / 2
        assert perf.quality_score == 0.8  # (0.9 + 0.7) / 2
        
        # Check cost metrics
        assert optimizer.cost_metrics.total_cost == 0.11  # 0.05 + 0.06
        assert optimizer.cost_metrics.tokens_consumed == 2200  # 1000 + 1200
        assert optimizer.cost_metrics.requests_made == 2
    
    def test_optimization_strategies(self, temp_data_file, sample_task):
        """Test different optimization strategies"""
        optimizer = ModelOptimizer(data_file=temp_data_file)
        
        # Test COST_OPTIMIZED strategy
        optimizer.strategy = OptimizationStrategy.COST_OPTIMIZED
        model_name, assignment = optimizer.select_model_for_agent(AgentType.PM, sample_task)
        assert model_name == assignment.fallback_model
        
        # Test PERFORMANCE_OPTIMIZED strategy
        optimizer.strategy = OptimizationStrategy.PERFORMANCE_OPTIMIZED
        model_name, assignment = optimizer.select_model_for_agent(AgentType.PM, sample_task)
        assert model_name == assignment.recommended_model
        
        # Test QUALITY_FIRST strategy with high complexity
        optimizer.strategy = OptimizationStrategy.QUALITY_FIRST
        high_complexity_task = AgentTask(
            type="design",
            priority=TaskPriority.CRITICAL,
            context=TaskContext(workflow_id="test", phase="design"),
            requirements=[TaskRequirement(f"req-{i}", f"Requirement {i}") for i in range(5)]
        )
        model_name, assignment = optimizer.select_model_for_agent(AgentType.PM, high_complexity_task)
        assert model_name == assignment.recommended_model
    
    def test_optimization_stats(self, temp_data_file):
        """Test optimization statistics generation"""
        optimizer = ModelOptimizer(data_file=temp_data_file)
        
        # Add some performance data
        optimizer._update_performance_data(
            "gpt-4", AgentType.PM,
            {'success': True, 'latency': 2.0, 'quality': 0.9, 'cost': 0.05, 'tokens': 1000}
        )
        
        stats = optimizer.get_optimization_stats()
        
        assert 'strategy' in stats
        assert 'total_cost' in stats
        assert 'total_requests' in stats
        assert 'agent_pools' in stats
        assert 'model_performance' in stats
        
        assert stats['strategy'] == OptimizationStrategy.BALANCED.value
        assert stats['total_cost'] == 0.05
        assert stats['total_requests'] == 1
        
        # Check agent pool stats
        for agent_type in AgentType:
            assert agent_type.value in stats['agent_pools']
            pool_stats = stats['agent_pools'][agent_type.value]
            assert 'max_instances' in pool_stats
            assert 'active_instances' in pool_stats
            assert 'queued_tasks' in pool_stats
    
    def test_resource_optimization_recommendations(self, temp_data_file):
        """Test resource optimization recommendations"""
        optimizer = ModelOptimizer(data_file=temp_data_file)
        
        # Simulate high load on PM agent pool
        pool = optimizer.agent_pools[AgentType.PM]
        pool.load_balancer.metrics.average_load = 0.9
        pool.load_balancer.metrics.total_instances = 1
        
        recommendations = optimizer.optimize_resource_allocation()
        
        assert 'scaling_actions' in recommendations
        assert 'model_switches' in recommendations
        assert 'budget_alerts' in recommendations
        assert 'performance_issues' in recommendations
        
        # Should recommend scaling up due to high load
        scaling_actions = recommendations['scaling_actions']
        assert len(scaling_actions) > 0
        assert any(action['action'] == 'scale_up' for action in scaling_actions)
    
    def test_data_persistence(self, temp_data_file):
        """Test data persistence and loading"""
        # Create optimizer and add some data
        optimizer1 = ModelOptimizer(data_file=temp_data_file)
        optimizer1._update_performance_data(
            "gpt-4", AgentType.PM,
            {'success': True, 'latency': 2.0, 'quality': 0.9, 'cost': 0.05, 'tokens': 1000}
        )
        optimizer1._save_data()
        
        # Create new optimizer with same data file
        optimizer2 = ModelOptimizer(data_file=temp_data_file)
        
        # Check that data was loaded
        perf_key = f"gpt-4_{AgentType.PM.value}"
        assert perf_key in optimizer2.performance_data
        
        perf = optimizer2.performance_data[perf_key]
        assert perf.total_requests == 1
        assert perf.success_rate == 1.0
        assert perf.average_latency == 2.0
        assert perf.quality_score == 0.9
        
        assert optimizer2.cost_metrics.total_cost == 0.05
        assert optimizer2.cost_metrics.tokens_consumed == 1000
    
    def test_strategy_update(self, temp_data_file):
        """Test updating optimization strategy"""
        optimizer = ModelOptimizer(data_file=temp_data_file)
        
        assert optimizer.strategy == OptimizationStrategy.BALANCED
        
        optimizer.update_strategy(OptimizationStrategy.COST_OPTIMIZED)
        assert optimizer.strategy == OptimizationStrategy.COST_OPTIMIZED
    
    def test_add_model_assignment(self, temp_data_file):
        """Test adding new model assignments"""
        optimizer = ModelOptimizer(data_file=temp_data_file)
        
        initial_count = len(optimizer.model_assignments)
        
        # Add a new assignment (this will replace existing PM assignment)
        new_assignment = ModelAssignment(
            role_type=AgentType.PM,
            model_tier=ModelTier.STRATEGIC,
            recommended_model="claude-3.5-sonnet",
            fallback_model="claude-3-sonnet",
            max_concurrent_instances=5,
            cost_per_token=0.015
        )
        
        optimizer.add_model_assignment(new_assignment)
        
        # Should have same number of assignments (replaced existing)
        assert len(optimizer.model_assignments) == initial_count + 1
        
        # Check that the assignment was updated
        pm_assignment = optimizer._assignment_by_type[AgentType.PM]
        assert pm_assignment.recommended_model == "claude-3.5-sonnet"
        assert pm_assignment.max_concurrent_instances == 5
    
    def test_cleanup(self, temp_data_file):
        """Test cleanup functionality"""
        optimizer = ModelOptimizer(data_file=temp_data_file)
        
        # Add some data
        optimizer._update_performance_data(
            "gpt-4", AgentType.PM,
            {'success': True, 'latency': 2.0, 'quality': 0.9, 'cost': 0.05, 'tokens': 1000}
        )
        
        # Cleanup should save data
        optimizer.cleanup()
        
        # Verify data was saved
        assert temp_data_file.exists()
        with open(temp_data_file, 'r') as f:
            data = json.load(f)
        
        assert 'performance_data' in data
        assert 'cost_metrics' in data


class TestCostMetrics:
    """Test cases for CostMetrics class"""
    
    def test_cost_metrics_initialization(self):
        """Test CostMetrics initialization"""
        metrics = CostMetrics()
        
        assert metrics.total_cost == 0.0
        assert len(metrics.cost_by_model) == 0
        assert len(metrics.cost_by_agent_type) == 0
        assert metrics.tokens_consumed == 0
        assert metrics.requests_made == 0
    
    def test_add_cost(self):
        """Test adding cost data"""
        metrics = CostMetrics()
        
        metrics.add_cost("gpt-4", AgentType.PM, 0.05, 1000)
        metrics.add_cost("gpt-4", AgentType.PM, 0.03, 600)
        metrics.add_cost("gpt-3.5-turbo", AgentType.IMPLEMENTATION, 0.01, 500)
        
        assert metrics.total_cost == 0.09
        assert metrics.cost_by_model["gpt-4"] == 0.08
        assert metrics.cost_by_model["gpt-3.5-turbo"] == 0.01
        assert metrics.cost_by_agent_type[AgentType.PM] == 0.08
        assert metrics.cost_by_agent_type[AgentType.IMPLEMENTATION] == 0.01
        assert metrics.tokens_consumed == 2100
        assert metrics.requests_made == 3


class TestModelPerformanceData:
    """Test cases for ModelPerformanceData class"""
    
    def test_performance_data_initialization(self):
        """Test ModelPerformanceData initialization"""
        perf = ModelPerformanceData("gpt-4", AgentType.PM)
        
        assert perf.model_name == "gpt-4"
        assert perf.agent_type == AgentType.PM
        assert perf.success_rate == 1.0
        assert perf.average_latency == 0.0
        assert perf.quality_score == 1.0
        assert perf.cost_efficiency == 1.0
        assert perf.total_requests == 0
    
    def test_update_performance_single_request(self):
        """Test updating performance with single request"""
        perf = ModelPerformanceData("gpt-4", AgentType.PM)
        
        perf.update_performance(success=True, latency=2.5, quality=0.9, cost=0.05)
        
        assert perf.total_requests == 1
        assert perf.success_rate == 1.0
        assert perf.average_latency == 2.5
        assert perf.quality_score == 0.9
        assert perf.cost_efficiency > 0  # Should be calculated based on success, quality, and cost
    
    def test_update_performance_multiple_requests(self):
        """Test updating performance with multiple requests"""
        perf = ModelPerformanceData("gpt-4", AgentType.PM)
        
        # First request - success
        perf.update_performance(success=True, latency=2.0, quality=0.9, cost=0.05)
        
        # Second request - failure
        perf.update_performance(success=False, latency=3.0, quality=0.7, cost=0.06)
        
        # Third request - success
        perf.update_performance(success=True, latency=1.5, quality=0.95, cost=0.04)
        
        assert perf.total_requests == 3
        assert perf.success_rate == 2/3  # 2 successes out of 3
        assert perf.average_latency == (2.0 + 3.0 + 1.5) / 3
        assert perf.quality_score == (0.9 + 0.7 + 0.95) / 3


class TestResourceBudget:
    """Test cases for ResourceBudget class"""
    
    def test_resource_budget_initialization(self):
        """Test ResourceBudget initialization with defaults"""
        budget = ResourceBudget()
        
        assert budget.max_daily_cost == 100.0
        assert budget.max_concurrent_instances == 20
        assert budget.max_tokens_per_hour == 1000000
        
        # Check priority allocation
        assert budget.priority_allocation[TaskPriority.CRITICAL] == 0.4
        assert budget.priority_allocation[TaskPriority.HIGH] == 0.3
        assert budget.priority_allocation[TaskPriority.MEDIUM] == 0.2
        assert budget.priority_allocation[TaskPriority.LOW] == 0.1
        assert budget.priority_allocation[TaskPriority.BACKGROUND] == 0.05
    
    def test_resource_budget_custom_values(self):
        """Test ResourceBudget with custom values"""
        custom_allocation = {
            TaskPriority.CRITICAL: 0.5,
            TaskPriority.HIGH: 0.3,
            TaskPriority.MEDIUM: 0.15,
            TaskPriority.LOW: 0.05,
            TaskPriority.BACKGROUND: 0.0
        }
        
        budget = ResourceBudget(
            max_daily_cost=200.0,
            max_concurrent_instances=50,
            max_tokens_per_hour=2000000,
            priority_allocation=custom_allocation
        )
        
        assert budget.max_daily_cost == 200.0
        assert budget.max_concurrent_instances == 50
        assert budget.max_tokens_per_hour == 2000000
        assert budget.priority_allocation[TaskPriority.CRITICAL] == 0.5
        assert budget.priority_allocation[TaskPriority.BACKGROUND] == 0.0


if __name__ == "__main__":
    pytest.main([__file__])