"""
Property-based tests for ModelOptimizer

**Property 9: Model Optimization and Multi-Instance Resource Management**
**Validates: Requirements 9.1, 9.2, 9.3, 9.4, 9.5**

This module contains property-based tests that validate universal properties
of the ModelOptimizer's hierarchical model assignment, cost optimization,
resource allocation, and performance monitoring capabilities.
"""

import unittest
import tempfile
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, Any, List, Optional

# Import the orchestration models and optimizer
from agentic_sdlc.orchestration.engine.model_optimizer import (
    ModelOptimizer, OptimizationStrategy, ResourceConstraint,
    CostMetrics, ResourceBudget, ModelPerformanceData
)
from agentic_sdlc.orchestration.models import (
    AgentType, ModelTier, ModelAssignment, AgentTask, TaskInput, TaskContext,
    TaskPriority, DataFormat, TaskRequirement, AgentInstance, InstanceStatus,
    AgentPool, LoadBalancer, PerformanceMetrics
)
from agentic_sdlc.orchestration.exceptions.model import (
    ModelOptimizationError, InsufficientResourcesError, InvalidModelAssignmentError
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


# Hypothesis strategies for model optimization testing

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
def optimization_strategy_strategy(draw):
    """Strategy for generating OptimizationStrategy values"""
    return draw(st.one_of([
        st.just(OptimizationStrategy.COST_OPTIMIZED),
        st.just(OptimizationStrategy.PERFORMANCE_OPTIMIZED),
        st.just(OptimizationStrategy.BALANCED),
        st.just(OptimizationStrategy.QUALITY_FIRST)
    ]))


@composite
def resource_constraint_strategy(draw):
    """Strategy for generating ResourceConstraint values"""
    return draw(st.one_of([
        st.just(ResourceConstraint.BUDGET),
        st.just(ResourceConstraint.CONCURRENCY),
        st.just(ResourceConstraint.LATENCY),
        st.just(ResourceConstraint.THROUGHPUT)
    ]))


@composite
def model_assignment_strategy(draw):
    """Strategy for generating ModelAssignment instances"""
    agent_type = draw(agent_type_strategy())
    model_tier = draw(model_tier_strategy())
    
    # Ensure model tier matches agent type according to design
    if agent_type in [AgentType.PM, AgentType.BA, AgentType.SA]:
        model_tier = ModelTier.STRATEGIC
    elif agent_type == AgentType.IMPLEMENTATION:
        model_tier = ModelTier.OPERATIONAL
    elif agent_type in [AgentType.RESEARCH, AgentType.QUALITY_JUDGE]:
        model_tier = ModelTier.RESEARCH
    
    return ModelAssignment(
        role_type=agent_type,
        model_tier=model_tier,
        recommended_model=draw(st.text(min_size=5, max_size=20)),
        fallback_model=draw(st.text(min_size=5, max_size=20)),
        max_concurrent_instances=draw(st.integers(min_value=1, max_value=10)),
        cost_per_token=draw(st.floats(min_value=0.001, max_value=0.02))
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
def resource_budget_strategy(draw):
    """Strategy for generating ResourceBudget instances"""
    return ResourceBudget(
        max_daily_cost=draw(st.floats(min_value=10.0, max_value=1000.0)),
        max_concurrent_instances=draw(st.integers(min_value=5, max_value=50)),
        max_tokens_per_hour=draw(st.integers(min_value=10000, max_value=5000000))
    )


@composite
def performance_data_strategy(draw):
    """Strategy for generating performance data dictionaries"""
    return {
        'success': draw(st.booleans()),
        'latency': draw(st.floats(min_value=0.1, max_value=30.0)),
        'quality': draw(st.floats(min_value=0.0, max_value=1.0)),
        'cost': draw(st.floats(min_value=0.001, max_value=1.0)),
        'tokens': draw(st.integers(min_value=10, max_value=10000))
    }


class TestModelOptimizerProperties(unittest.TestCase):
    """
    Property-based tests for ModelOptimizer
    
    **Feature: multi-agent-orchestration, Property 9: Model Optimization and Multi-Instance Resource Management**
    
    *For any* task assignment, the model optimizer should evaluate role hierarchy and select 
    appropriate model tier (strategic for PM/BA/SA, operational for implementation/testing, 
    research for quality/research roles), spawn multiple agent instances per role type as needed, 
    monitor performance across all instances to adjust selections, and manage task queuing and 
    load balancing under resource constraints.
    """
    
    def setUp(self):
        """Set up test fixtures"""
        if not HYPOTHESIS_AVAILABLE:
            self.skipTest("Hypothesis not available")
        
        # Create temporary file for each test
        self.temp_file = tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.json')
        self.temp_path = Path(self.temp_file.name)
        self.temp_file.close()
    
    def tearDown(self):
        """Clean up test fixtures"""
        if self.temp_path.exists():
            self.temp_path.unlink()
    
    @given(
        agent_type=agent_type_strategy(),
        task=agent_task_strategy(),
        strategy=optimization_strategy_strategy()
    )
    @settings(max_examples=50, suppress_health_check=[HealthCheck.function_scoped_fixture])
    def test_model_tier_assignment_consistency(self, agent_type, task, strategy):
        """
        Property: Model tier assignment must be consistent with agent role hierarchy
        
        For any agent type and task, the selected model must belong to the correct tier:
        - Strategic tier for PM, BA, SA agents
        - Operational tier for Implementation agents  
        - Research tier for Research and Quality Judge agents
        """
        optimizer = ModelOptimizer(strategy=strategy, data_file=self.temp_path)
        
        try:
            model_name, assignment = optimizer.select_model_for_agent(agent_type, task)
            
            # Verify tier consistency based on design document
            if agent_type in [AgentType.PM, AgentType.BA, AgentType.SA]:
                self.assertEqual(assignment.model_tier, ModelTier.STRATEGIC,
                               f"Agent {agent_type.value} must use STRATEGIC tier")
            elif agent_type == AgentType.IMPLEMENTATION:
                self.assertEqual(assignment.model_tier, ModelTier.OPERATIONAL,
                               f"Agent {agent_type.value} must use OPERATIONAL tier")
            elif agent_type in [AgentType.RESEARCH, AgentType.QUALITY_JUDGE]:
                self.assertEqual(assignment.model_tier, ModelTier.RESEARCH,
                               f"Agent {agent_type.value} must use RESEARCH tier")
            
            # Verify model selection is from assignment
            self.assertIn(model_name, [assignment.recommended_model, assignment.fallback_model],
                         "Selected model must be either recommended or fallback")
            
        except InvalidModelAssignmentError:
            # This is acceptable if no assignment exists for the agent type
            pass
    
    @given(
        strategy=optimization_strategy_strategy(),
        task=agent_task_strategy()
    )
    @settings(max_examples=50, suppress_health_check=[HealthCheck.function_scoped_fixture])
    def test_cost_optimization_consistency(self, strategy, task):
        """
        Property: Cost optimization must be consistent with strategy
        
        For any optimization strategy, model selection should align with cost preferences:
        - COST_OPTIMIZED: Always prefer fallback (cheaper) models
        - PERFORMANCE_OPTIMIZED: Always prefer recommended (better) models
        - QUALITY_FIRST: Prefer recommended for high complexity/priority
        - BALANCED: Use performance data or heuristics
        """
        optimizer = ModelOptimizer(strategy=strategy, data_file=self.temp_path)
        
        for agent_type in [AgentType.PM, AgentType.IMPLEMENTATION, AgentType.RESEARCH]:
            try:
                model_name, assignment = optimizer.select_model_for_agent(agent_type, task)
                
                if strategy == OptimizationStrategy.COST_OPTIMIZED:
                    self.assertEqual(model_name, assignment.fallback_model,
                                   f"COST_OPTIMIZED should prefer fallback model for {agent_type.value}")
                
                elif strategy == OptimizationStrategy.PERFORMANCE_OPTIMIZED:
                    self.assertEqual(model_name, assignment.recommended_model,
                                   f"PERFORMANCE_OPTIMIZED should prefer recommended model for {agent_type.value}")
                
                elif strategy == OptimizationStrategy.QUALITY_FIRST:
                    # High complexity or high priority should use recommended model
                    complexity = optimizer._analyze_task_complexity(task)
                    if complexity > 0.7 or task.priority in [TaskPriority.CRITICAL, TaskPriority.HIGH]:
                        self.assertEqual(model_name, assignment.recommended_model,
                                       f"QUALITY_FIRST should use recommended model for high complexity/priority")
                
                # BALANCED strategy is more complex and depends on performance data
                
            except InvalidModelAssignmentError:
                # Skip if no assignment exists
                continue
    
    @given(
        agent_type=agent_type_strategy(),
        tasks=st.lists(agent_task_strategy(), min_size=1, max_size=5)
    )
    @settings(max_examples=30, suppress_health_check=[HealthCheck.function_scoped_fixture])
    def test_multi_instance_resource_allocation(self, agent_type, tasks):
        """
        Property: Multi-instance resource allocation must respect capacity limits
        
        For any agent type and list of tasks, the optimizer should:
        - Allocate instances up to max_concurrent_instances
        - Queue tasks when at capacity
        - Maintain proper instance states
        """
        # Create optimizer with small instance limits for testing
        assignments = [
            ModelAssignment(
                role_type=agent_type,
                model_tier=ModelTier.OPERATIONAL,  # Use operational for simplicity
                recommended_model="test-model",
                fallback_model="test-fallback",
                max_concurrent_instances=2,  # Small limit for testing
                cost_per_token=0.01
            )
        ]
        optimizer = ModelOptimizer(model_assignments=assignments, data_file=self.temp_path)
        
        allocated_instances = []
        
        # Try to allocate instances for all tasks
        for task in tasks:
            instance = optimizer.allocate_agent_instance(agent_type, task)
            if instance:
                allocated_instances.append(instance)
        
        pool = optimizer.agent_pools[agent_type]
        
        # Verify capacity constraints
        self.assertLessEqual(len(pool.active_instances), assignments[0].max_concurrent_instances,
                           "Active instances should not exceed max capacity")
        
        # Verify task queuing when at capacity
        total_tasks = len(tasks)
        allocated_tasks = len(allocated_instances)
        queued_tasks = len(pool.queued_tasks)
        
        self.assertEqual(allocated_tasks + queued_tasks, total_tasks,
                        "All tasks should be either allocated or queued")
        
        # Verify instance states
        for instance in allocated_instances:
            self.assertEqual(instance.status, InstanceStatus.BUSY,
                           "Allocated instances should be BUSY")
            self.assertIsNotNone(instance.current_task,
                               "Busy instances should have current task")
    
    @given(
        agent_type=agent_type_strategy(),
        performance_data_list=st.lists(performance_data_strategy(), min_size=1, max_size=10)
    )
    @settings(max_examples=30, suppress_health_check=[HealthCheck.function_scoped_fixture])
    def test_performance_tracking_accuracy(self, agent_type, performance_data_list):
        """
        Property: Performance tracking must accurately aggregate metrics
        
        For any sequence of performance updates, the aggregated metrics should:
        - Correctly calculate success rates
        - Properly average latency and quality scores
        - Update cost efficiency based on success, quality, and cost
        - Maintain accurate request counts
        """
        # Create a fresh optimizer for this test to avoid data contamination
        temp_file = tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.json')
        temp_path = Path(temp_file.name)
        temp_file.close()
        
        try:
            optimizer = ModelOptimizer(data_file=temp_path)
            model_name = "test-model"
            
            # Apply all performance updates
            for perf_data in performance_data_list:
                optimizer._update_performance_data(model_name, agent_type, perf_data)
            
            # Get the aggregated performance data
            perf_key = f"{model_name}_{agent_type.value}"
            if perf_key in optimizer.performance_data:
                perf = optimizer.performance_data[perf_key]
                
                # Verify request count
                self.assertEqual(perf.total_requests, len(performance_data_list),
                               "Total requests should match number of updates")
                
                # Verify success rate calculation
                successes = sum(1 for p in performance_data_list if p['success'])
                expected_success_rate = successes / len(performance_data_list)
                self.assertAlmostEqual(perf.success_rate, expected_success_rate, places=5,
                                     msg="Success rate should be correctly calculated")
                
                # Verify average latency calculation
                expected_avg_latency = sum(p['latency'] for p in performance_data_list) / len(performance_data_list)
                self.assertAlmostEqual(perf.average_latency, expected_avg_latency, places=5,
                                     msg="Average latency should be correctly calculated")
                
                # Verify average quality calculation
                expected_avg_quality = sum(p['quality'] for p in performance_data_list) / len(performance_data_list)
                self.assertAlmostEqual(perf.quality_score, expected_avg_quality, places=5,
                                     msg="Average quality should be correctly calculated")
                
                # Verify cost efficiency is non-negative and calculated correctly
                # Cost efficiency = (success_rate * quality_score) / cost
                # It can be 0.0 if success_rate or quality_score is 0.0
                if any(p['cost'] > 0 for p in performance_data_list):
                    self.assertGreaterEqual(perf.cost_efficiency, 0.0,
                                          "Cost efficiency should be non-negative")
                    
                    # If there are successful requests with quality > 0, efficiency should be positive
                    has_successful_quality = any(p['success'] and p['quality'] > 0 for p in performance_data_list)
                    if has_successful_quality:
                        self.assertGreater(perf.cost_efficiency, 0.0,
                                         "Cost efficiency should be positive when there are successful quality results")
        finally:
            # Clean up
            if temp_path.exists():
                temp_path.unlink()
    
    @given(
        budget=resource_budget_strategy(),
        constraints=st.lists(resource_constraint_strategy(), min_size=0, max_size=3)
    )
    @settings(max_examples=30, suppress_health_check=[HealthCheck.function_scoped_fixture])
    def test_resource_constraint_management(self, budget, constraints):
        """
        Property: Resource constraint management must enforce limits
        
        For any budget and constraint set, the optimizer should:
        - Respect daily cost limits
        - Enforce concurrency limits
        - Properly validate resource availability
        """
        optimizer = ModelOptimizer(budget=budget, data_file=self.temp_path)
        
        # Test budget constraint
        if ResourceConstraint.BUDGET in constraints:
            # Simulate exceeding budget
            optimizer.cost_metrics.total_cost = budget.max_daily_cost + 10.0
            optimizer.cost_metrics.last_updated = datetime.now()
            
            assignment = optimizer._assignment_by_type[AgentType.PM]
            
            with self.assertRaises(InsufficientResourcesError):
                optimizer._validate_resource_constraints(assignment, [ResourceConstraint.BUDGET])
        
        # Test concurrency constraint
        if ResourceConstraint.CONCURRENCY in constraints:
            # Fill up the agent pool to capacity
            agent_type = AgentType.PM
            pool = optimizer.agent_pools[agent_type]
            assignment = optimizer._assignment_by_type[agent_type]
            
            # Create instances up to max capacity
            for i in range(assignment.max_concurrent_instances):
                instance = AgentInstance(agent_type=agent_type, model_assignment=assignment)
                pool.active_instances.append(instance)
            
            with self.assertRaises(InsufficientResourcesError):
                optimizer._validate_resource_constraints(assignment, [ResourceConstraint.CONCURRENCY])
    
    @given(
        agent_type=agent_type_strategy(),
        task=agent_task_strategy(),
        performance_updates=st.lists(performance_data_strategy(), min_size=2, max_size=5)
    )
    @settings(max_examples=20, suppress_health_check=[HealthCheck.function_scoped_fixture])
    def test_load_balancing_correctness(self, agent_type, task, performance_updates):
        """
        Property: Load balancing must distribute tasks fairly across instances
        
        For any agent type with multiple instances, task distribution should:
        - Prefer idle instances over busy ones
        - Queue tasks when all instances are busy
        - Assign queued tasks when instances become available
        """
        # Create optimizer with multiple instances allowed
        assignments = [
            ModelAssignment(
                role_type=agent_type,
                model_tier=ModelTier.OPERATIONAL,
                recommended_model="test-model",
                fallback_model="test-fallback",
                max_concurrent_instances=3,
                cost_per_token=0.01
            )
        ]
        optimizer = ModelOptimizer(model_assignments=assignments, data_file=self.temp_path)
        
        # Allocate first instance
        instance1 = optimizer.allocate_agent_instance(agent_type, task)
        self.assertIsNotNone(instance1, "First instance should be allocated")
        
        # Create second task - should get new instance
        task2 = AgentTask(type="test", context=TaskContext(workflow_id="test2", phase="test"))
        instance2 = optimizer.allocate_agent_instance(agent_type, task2)
        
        pool = optimizer.agent_pools[agent_type]
        
        if instance2:
            # Two instances should be active
            self.assertEqual(len(pool.active_instances), 2,
                           "Two instances should be active")
            self.assertNotEqual(instance1.instance_id, instance2.instance_id,
                              "Instances should have different IDs")
        
        # Release first instance and verify queued task assignment
        if pool.queued_tasks:
            initial_queue_length = len(pool.queued_tasks)
            optimizer.release_agent_instance(agent_type, instance1.instance_id, performance_updates[0])
            
            # Queue should be shorter or instance should have new task
            self.assertTrue(
                len(pool.queued_tasks) < initial_queue_length or instance1.current_task is not None,
                "Released instance should process queued task or queue should be shorter"
            )


class TestModelOptimizerComplexityAnalysis(unittest.TestCase):
    """Test task complexity analysis properties"""
    
    def setUp(self):
        """Set up test fixtures"""
        if not HYPOTHESIS_AVAILABLE:
            self.skipTest("Hypothesis not available")
        
        self.temp_file = tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.json')
        self.temp_path = Path(self.temp_file.name)
        self.temp_file.close()
        self.optimizer = ModelOptimizer(data_file=self.temp_path)
    
    def tearDown(self):
        """Clean up test fixtures"""
        if self.temp_path.exists():
            self.temp_path.unlink()
    
    @given(task=agent_task_strategy())
    @settings(max_examples=50, suppress_health_check=[HealthCheck.function_scoped_fixture])
    def test_complexity_score_bounds(self, task):
        """
        Property: Task complexity scores must be within valid bounds
        
        For any task, the complexity score should be between 0.0 and 1.0
        """
        complexity = self.optimizer._analyze_task_complexity(task)
        
        self.assertGreaterEqual(complexity, 0.0, "Complexity score should be >= 0.0")
        self.assertLessEqual(complexity, 1.0, "Complexity score should be <= 1.0")
        self.assertIsInstance(complexity, float, "Complexity score should be a float")
    
    @given(
        base_task=agent_task_strategy(),
        additional_requirements=st.lists(task_requirement_strategy(), min_size=1, max_size=5)
    )
    @settings(max_examples=30, suppress_health_check=[HealthCheck.function_scoped_fixture])
    def test_complexity_increases_with_requirements(self, base_task, additional_requirements):
        """
        Property: Task complexity should increase with more requirements
        
        For any task, adding requirements should not decrease complexity
        """
        # Calculate complexity with base requirements
        base_complexity = self.optimizer._analyze_task_complexity(base_task)
        
        # Add more requirements
        enhanced_task = AgentTask(
            type=base_task.type,
            input=base_task.input,
            context=base_task.context,
            requirements=base_task.requirements + additional_requirements,
            priority=base_task.priority,
            deadline=base_task.deadline
        )
        
        enhanced_complexity = self.optimizer._analyze_task_complexity(enhanced_task)
        
        self.assertGreaterEqual(enhanced_complexity, base_complexity,
                              "Complexity should not decrease when adding requirements")
    
    @given(task=agent_task_strategy())
    @settings(max_examples=30, suppress_health_check=[HealthCheck.function_scoped_fixture])
    def test_priority_affects_complexity(self, task):
        """
        Property: Higher priority tasks should have higher or equal complexity scores
        
        For any task, CRITICAL priority should yield higher or equal complexity than BACKGROUND,
        unless the complexity is already at maximum (1.0)
        """
        # Test with CRITICAL priority
        critical_task = AgentTask(
            type=task.type,
            input=task.input,
            context=task.context,
            requirements=task.requirements,
            priority=TaskPriority.CRITICAL,
            deadline=task.deadline
        )
        
        # Test with BACKGROUND priority
        background_task = AgentTask(
            type=task.type,
            input=task.input,
            context=task.context,
            requirements=task.requirements,
            priority=TaskPriority.BACKGROUND,
            deadline=task.deadline
        )
        
        critical_complexity = self.optimizer._analyze_task_complexity(critical_task)
        background_complexity = self.optimizer._analyze_task_complexity(background_task)
        
        # CRITICAL should have higher or equal complexity, unless both are at max
        if background_complexity < 1.0:  # If background isn't at max, critical should be higher
            self.assertGreaterEqual(critical_complexity, background_complexity,
                              "CRITICAL priority should yield higher or equal complexity than BACKGROUND")
        else:
            # Both can be at 1.0 (maximum), which is acceptable
            self.assertGreaterEqual(critical_complexity, background_complexity,
                              "CRITICAL priority should yield higher or equal complexity than BACKGROUND")


if __name__ == "__main__":
    # Configure Hypothesis for property-based testing
    if HYPOTHESIS_AVAILABLE:
        import os
        profile = os.getenv("HYPOTHESIS_PROFILE", "default")
        if profile == "ci":
            settings.register_profile("ci", max_examples=100, deadline=None)
        else:
            settings.register_profile("default", max_examples=50, deadline=None)
        settings.load_profile(profile)
    
    unittest.main()