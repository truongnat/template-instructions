"""
Integration tests for ModelOptimizer with the orchestration system

This module tests the integration of ModelOptimizer with other orchestration components
to ensure proper hierarchical model assignment and resource management in realistic scenarios.
"""

import pytest
import tempfile
from pathlib import Path
from datetime import datetime, timedelta

from agentic_sdlc.orchestration import ModelOptimizer
from agentic_sdlc.orchestration.models import (
    AgentType, ModelTier, AgentTask, TaskInput, TaskContext, TaskPriority,
    DataFormat, TaskRequirement, WorkflowPlan, OrchestrationPattern,
    AgentAssignment, ResourceRequirement, ModelAssignment
)
from agentic_sdlc.orchestration.engine.model_optimizer import (
    OptimizationStrategy, ResourceConstraint, ResourceBudget
)


class TestModelOptimizerIntegration:
    """Integration tests for ModelOptimizer"""
    
    @pytest.fixture
    def temp_data_file(self):
        """Create a temporary file for testing"""
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.json') as f:
            temp_path = Path(f.name)
        yield temp_path
        if temp_path.exists():
            temp_path.unlink()
    
    @pytest.fixture
    def model_optimizer(self, temp_data_file):
        """Create a ModelOptimizer instance for testing"""
        budget = ResourceBudget(
            max_daily_cost=100.0,
            max_concurrent_instances=15,
            max_tokens_per_hour=800000
        )
        return ModelOptimizer(
            budget=budget,
            strategy=OptimizationStrategy.BALANCED,
            data_file=temp_data_file
        )
    
    def test_workflow_model_assignment_scenario(self, model_optimizer):
        """Test a complete workflow scenario with model assignments"""
        
        # Simulate a software development workflow with different agent types
        tasks = [
            # PM Agent - Strategic tier task
            AgentTask(
                type="requirements_analysis",
                input=TaskInput(
                    data={"project": "User Authentication System", "stakeholders": ["users", "admins"]},
                    format=DataFormat.JSON
                ),
                context=TaskContext(workflow_id="auth-system", phase="planning"),
                requirements=[
                    TaskRequirement("req-1", "Must include security requirements"),
                    TaskRequirement("req-2", "Must define user stories")
                ],
                priority=TaskPriority.HIGH
            ),
            
            # BA Agent - Strategic tier task
            AgentTask(
                type="business_analysis",
                input=TaskInput(
                    data={"requirements": "User authentication with role-based access"},
                    format=DataFormat.TEXT
                ),
                context=TaskContext(workflow_id="auth-system", phase="analysis"),
                requirements=[
                    TaskRequirement("req-3", "Must analyze business impact"),
                    TaskRequirement("req-4", "Must define process flows")
                ],
                priority=TaskPriority.HIGH
            ),
            
            # SA Agent - Strategic tier task
            AgentTask(
                type="architecture_design",
                input=TaskInput(
                    data={"system": "Authentication service with JWT tokens"},
                    format=DataFormat.TEXT
                ),
                context=TaskContext(
                    workflow_id="auth-system", 
                    phase="design",
                    dependencies=["requirements_analysis", "business_analysis"]
                ),
                requirements=[
                    TaskRequirement("req-5", "Must design scalable architecture"),
                    TaskRequirement("req-6", "Must include security patterns"),
                    TaskRequirement("req-7", "Must define API contracts")
                ],
                priority=TaskPriority.CRITICAL
            ),
            
            # Implementation Agent - Operational tier task
            AgentTask(
                type="code_implementation",
                input=TaskInput(
                    data={"specification": "JWT authentication service"},
                    format=DataFormat.TEXT
                ),
                context=TaskContext(
                    workflow_id="auth-system",
                    phase="implementation",
                    dependencies=["architecture_design"]
                ),
                requirements=[
                    TaskRequirement("req-8", "Must implement JWT handling"),
                    TaskRequirement("req-9", "Must include error handling")
                ],
                priority=TaskPriority.MEDIUM
            ),
            
            # Research Agent - Research tier task
            AgentTask(
                type="security_research",
                input=TaskInput(
                    data={"topic": "JWT security best practices"},
                    format=DataFormat.TEXT
                ),
                context=TaskContext(workflow_id="auth-system", phase="research"),
                requirements=[
                    TaskRequirement("req-10", "Must research latest security standards")
                ],
                priority=TaskPriority.MEDIUM
            ),
            
            # Quality Judge Agent - Research tier task
            AgentTask(
                type="quality_evaluation",
                input=TaskInput(
                    data={"code": "Authentication implementation", "criteria": ["security", "performance"]},
                    format=DataFormat.JSON
                ),
                context=TaskContext(
                    workflow_id="auth-system",
                    phase="quality_assurance",
                    dependencies=["code_implementation"]
                ),
                requirements=[
                    TaskRequirement("req-11", "Must evaluate security compliance"),
                    TaskRequirement("req-12", "Must assess performance impact")
                ],
                priority=TaskPriority.HIGH
            )
        ]
        
        # Test model selection for each agent type
        model_assignments = {}
        allocated_instances = {}
        
        for task in tasks:
            # Determine agent type based on task type
            agent_type_mapping = {
                "requirements_analysis": AgentType.PM,
                "business_analysis": AgentType.BA,
                "architecture_design": AgentType.SA,
                "code_implementation": AgentType.IMPLEMENTATION,
                "security_research": AgentType.RESEARCH,
                "quality_evaluation": AgentType.QUALITY_JUDGE
            }
            
            agent_type = agent_type_mapping[task.type]
            
            # Select model for the agent
            model_name, assignment = model_optimizer.select_model_for_agent(agent_type, task)
            model_assignments[task.type] = {
                'agent_type': agent_type,
                'model_name': model_name,
                'model_tier': assignment.model_tier,
                'task_complexity': model_optimizer._analyze_task_complexity(task)
            }
            
            # Allocate agent instance
            instance = model_optimizer.allocate_agent_instance(agent_type, task)
            if instance:
                allocated_instances[task.type] = instance
        
        # Verify model tier assignments
        assert model_assignments["requirements_analysis"]["model_tier"] == ModelTier.STRATEGIC
        assert model_assignments["business_analysis"]["model_tier"] == ModelTier.STRATEGIC
        assert model_assignments["architecture_design"]["model_tier"] == ModelTier.STRATEGIC
        assert model_assignments["code_implementation"]["model_tier"] == ModelTier.OPERATIONAL
        assert model_assignments["security_research"]["model_tier"] == ModelTier.RESEARCH
        assert model_assignments["quality_evaluation"]["model_tier"] == ModelTier.RESEARCH
        
        # Verify that high complexity/priority tasks get appropriate models
        arch_task = model_assignments["architecture_design"]
        assert arch_task["task_complexity"] > 0.7  # Should be high complexity
        
        # Verify instance allocation
        assert len(allocated_instances) == 6  # All tasks should get instances
        
        # Simulate task completion and performance tracking
        for task_type, instance in allocated_instances.items():
            # Simulate different performance characteristics
            performance_data = {
                'success': True,
                'latency': 2.0 + (0.5 if 'strategic' in str(model_assignments[task_type]['model_tier']) else 0),
                'quality': 0.9 if model_assignments[task_type]['model_tier'] == ModelTier.STRATEGIC else 0.8,
                'cost': 0.05 if model_assignments[task_type]['model_tier'] == ModelTier.STRATEGIC else 0.02,
                'tokens': 1500 if model_assignments[task_type]['model_tier'] == ModelTier.STRATEGIC else 800
            }
            
            model_optimizer.release_agent_instance(
                instance.agent_type,
                instance.instance_id,
                performance_data
            )
        
        # Verify performance tracking
        stats = model_optimizer.get_optimization_stats()
        assert stats['total_requests'] == 6
        assert stats['total_cost'] > 0
        assert len(stats['model_performance']) > 0
        
        # Check that strategic tier models have higher costs
        strategic_costs = sum(
            v for k, v in stats['cost_by_agent_type'].items()
            if k in ['product_manager', 'business_analyst', 'solution_architect']
        )
        operational_costs = sum(
            v for k, v in stats['cost_by_agent_type'].items()
            if k in ['implementation']
        )
        research_costs = sum(
            v for k, v in stats['cost_by_agent_type'].items()
            if k in ['research', 'quality_judge']
        )
        
        # Strategic tier should have higher per-task costs
        assert strategic_costs > operational_costs
        assert strategic_costs > research_costs
    
    def test_resource_constraint_handling(self, model_optimizer):
        """Test resource constraint handling in realistic scenarios"""
        
        # Set a low budget to trigger constraints
        model_optimizer.budget.max_daily_cost = 0.10
        model_optimizer.cost_metrics.total_cost = 0.08  # Close to limit
        model_optimizer.cost_metrics.last_updated = datetime.now()
        
        # Create a high-priority task
        task = AgentTask(
            type="critical_analysis",
            priority=TaskPriority.CRITICAL,
            context=TaskContext(workflow_id="test", phase="analysis")
        )
        
        # Should still work for critical tasks, but might trigger warnings
        model_name, assignment = model_optimizer.select_model_for_agent(
            AgentType.PM, 
            task, 
            constraints=[ResourceConstraint.BUDGET]
        )
        
        # Should get a model assignment despite budget constraints
        assert model_name is not None
        assert assignment is not None
        
        # Exceed budget
        model_optimizer.cost_metrics.total_cost = 0.12
        
        # Now should raise exception
        with pytest.raises(Exception):  # Should be InsufficientResourcesError
            model_optimizer.select_model_for_agent(
                AgentType.PM,
                task,
                constraints=[ResourceConstraint.BUDGET]
            )
    
    def test_load_balancing_scenario(self, model_optimizer):
        """Test load balancing with multiple concurrent tasks"""
        
        # Create multiple tasks for the same agent type
        tasks = []
        for i in range(5):
            task = AgentTask(
                type=f"analysis_{i}",
                context=TaskContext(workflow_id=f"workflow_{i}", phase="analysis"),
                priority=TaskPriority.MEDIUM
            )
            tasks.append(task)
        
        # Allocate instances for all tasks
        allocated_instances = []
        queued_tasks = []
        
        for task in tasks:
            instance = model_optimizer.allocate_agent_instance(AgentType.PM, task)
            if instance:
                allocated_instances.append(instance)
            else:
                queued_tasks.append(task)
        
        # Check that we allocated up to the maximum instances
        pm_pool = model_optimizer.agent_pools[AgentType.PM]
        max_instances = next(
            a.max_concurrent_instances for a in model_optimizer.model_assignments 
            if a.role_type == AgentType.PM
        )
        
        assert len(allocated_instances) <= max_instances
        assert len(pm_pool.active_instances) == len(allocated_instances)
        
        # If we have more tasks than instances, some should be queued
        if len(tasks) > max_instances:
            assert len(pm_pool.queued_tasks) == len(tasks) - max_instances
        
        # Release an instance and check that queued task gets assigned
        if allocated_instances and pm_pool.queued_tasks:
            first_instance = allocated_instances[0]
            model_optimizer.release_agent_instance(AgentType.PM, first_instance.instance_id)
            
            # Should have assigned a queued task
            assert len(pm_pool.queued_tasks) < len(queued_tasks)
    
    def test_optimization_recommendations(self, model_optimizer):
        """Test optimization recommendations in realistic scenarios"""
        
        # Simulate poor performance for a specific model
        model_optimizer._update_performance_data(
            "gpt-4", AgentType.PM,
            {'success': False, 'latency': 10.0, 'quality': 0.3, 'cost': 0.10, 'tokens': 2000}
        )
        model_optimizer._update_performance_data(
            "gpt-4", AgentType.PM,
            {'success': False, 'latency': 12.0, 'quality': 0.4, 'cost': 0.12, 'tokens': 2200}
        )
        
        # Simulate high load
        pm_pool = model_optimizer.agent_pools[AgentType.PM]
        pm_pool.load_balancer.metrics.average_load = 2.0  # High load
        pm_pool.load_balancer.metrics.total_instances = 2
        pm_pool.load_balancer.metrics.active_instances = 2
        
        recommendations = model_optimizer.optimize_resource_allocation()
        
        # Should recommend performance improvements
        assert len(recommendations['performance_issues']) > 0
        performance_issue = recommendations['performance_issues'][0]
        assert performance_issue['issue'] == 'low_success_rate'
        assert performance_issue['model'] == 'gpt-4'
        
        # Should recommend scaling up due to high load
        assert len(recommendations['scaling_actions']) > 0
        scaling_action = recommendations['scaling_actions'][0]
        assert scaling_action['action'] == 'scale_up'
        assert scaling_action['agent_type'] == 'product_manager'
    
    def test_strategy_impact_on_model_selection(self, model_optimizer):
        """Test how different strategies impact model selection"""
        
        # Create a medium complexity task
        task = AgentTask(
            type="analysis",
            priority=TaskPriority.MEDIUM,
            context=TaskContext(workflow_id="test", phase="analysis"),
            requirements=[
                TaskRequirement("req-1", "Basic analysis requirement")
            ]
        )
        
        # Test different strategies
        strategies_and_expected_models = []
        
        for strategy in OptimizationStrategy:
            model_optimizer.update_strategy(strategy)
            model_name, assignment = model_optimizer.select_model_for_agent(AgentType.PM, task)
            strategies_and_expected_models.append((strategy, model_name, assignment))
        
        # Verify strategy differences
        cost_optimized = next(
            (model for strategy, model, _ in strategies_and_expected_models 
             if strategy == OptimizationStrategy.COST_OPTIMIZED), None
        )
        performance_optimized = next(
            (model for strategy, model, _ in strategies_and_expected_models 
             if strategy == OptimizationStrategy.PERFORMANCE_OPTIMIZED), None
        )
        
        # Cost optimized should prefer fallback model
        pm_assignment = next(a for a in model_optimizer.model_assignments if a.role_type == AgentType.PM)
        assert cost_optimized == pm_assignment.fallback_model
        
        # Performance optimized should prefer recommended model
        assert performance_optimized == pm_assignment.recommended_model
    
    def test_end_to_end_api_model_management_integration(self, model_optimizer):
        """
        Test end-to-end integration with API Model Management system.
        
        This test validates the complete flow from task submission through
        model selection, API request, response evaluation, and performance tracking.
        
        Validates: Requirements 13.1, 13.5
        """
        from agentic_sdlc.orchestration.api_model_management.model_optimizer_integration import (
            ModelOptimizerIntegration, APIModelAssignment
        )
        from agentic_sdlc.orchestration.api_model_management.selector import ModelSelector
        from agentic_sdlc.orchestration.api_model_management.failover_manager import FailoverManager
        from agentic_sdlc.orchestration.api_model_management.performance_monitor import PerformanceMonitor
        from agentic_sdlc.orchestration.api_model_management.cost_tracker import CostTracker
        from agentic_sdlc.orchestration.api_model_management.registry import ModelRegistry
        from agentic_sdlc.orchestration.api_model_management.health_checker import HealthChecker
        from agentic_sdlc.orchestration.api_model_management.rate_limiter import RateLimiter
        from agentic_sdlc.orchestration.api_model_management.database import initialize_database
        from pathlib import Path
        import tempfile
        import asyncio
        
        # Create temporary database for testing
        with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as f:
            db_path = Path(f.name)
        
        try:
            # Initialize database schema
            asyncio.run(initialize_database(db_path))
            
            # Initialize API Model Management components
            registry = ModelRegistry(Path("agentic_sdlc/orchestration/api_model_management/config/model_registry.json"))
            health_checker = HealthChecker(registry, db_path, check_interval_seconds=300)
            rate_limiter = RateLimiter(registry)
            performance_monitor = PerformanceMonitor(db_path)
            cost_tracker = CostTracker(db_path, daily_budget=100.0)
            
            model_selector = ModelSelector(
                registry=registry,
                health_checker=health_checker,
                rate_limiter=rate_limiter,
                performance_monitor=performance_monitor
            )
            
            failover_manager = FailoverManager(
                model_selector=model_selector,
                db_path=db_path,
                max_retries=3,
                base_backoff_seconds=2
            )
            
            # Create integration layer
            integration = ModelOptimizerIntegration(
                model_selector=model_selector,
                failover_manager=failover_manager,
                performance_monitor=performance_monitor,
                cost_tracker=cost_tracker
            )
            
            # Create a test task
            task = AgentTask(
                type="architecture_design",
                input=TaskInput(
                    data={"system": "Microservices architecture for e-commerce platform"},
                    format=DataFormat.TEXT
                ),
                context=TaskContext(
                    workflow_id="ecommerce-project",
                    phase="design",
                    dependencies=["requirements_analysis"]
                ),
                requirements=[
                    TaskRequirement("req-1", "Must design scalable architecture"),
                    TaskRequirement("req-2", "Must include API gateway pattern"),
                    TaskRequirement("req-3", "Must support high availability")
                ],
                priority=TaskPriority.HIGH
            )
            
            # Get base assignment from ModelOptimizer
            base_model, base_assignment = model_optimizer.select_model_for_agent(
                AgentType.SA,
                task
            )
            
            # Use integration layer to select API model
            import asyncio
            api_assignment = asyncio.run(
                integration.select_model_for_agent(
                    agent_type=AgentType.SA,
                    task=task,
                    base_assignment=base_assignment
                )
            )
            
            # Verify API assignment
            assert isinstance(api_assignment, APIModelAssignment)
            assert api_assignment.base_assignment == base_assignment
            assert api_assignment.selected_model_id is not None
            assert api_assignment.api_provider in ["openai", "anthropic", "google", "ollama"]
            assert api_assignment.role_type == AgentType.SA
            
            # Verify backward compatibility - should have same interface as base assignment
            assert hasattr(api_assignment, 'role_type')
            assert hasattr(api_assignment, 'model_tier')
            assert hasattr(api_assignment, 'max_concurrent_instances')
            assert hasattr(api_assignment, 'cost_per_token')
            
            # Simulate task execution and report performance
            performance_data = {
                'success': True,
                'latency_ms': 2500.0,
                'quality_score': 0.92,
                'cost': 0.08,
                'input_tokens': 1200,
                'output_tokens': 800
            }
            
            asyncio.run(
                integration.report_performance_to_optimizer(
                    agent_type=AgentType.SA,
                    task_id=task.id,
                    model_id=api_assignment.selected_model_id,
                    performance_data=performance_data
                )
            )
            
            # Verify performance was recorded
            perf_metrics = asyncio.run(
                performance_monitor.get_model_performance(
                    model_id=api_assignment.selected_model_id,
                    window_hours=1
                )
            )
            assert perf_metrics.total_requests >= 1
            
            # Verify cost was tracked
            daily_cost = asyncio.run(cost_tracker.get_daily_cost())
            assert daily_cost >= 0.08
            
            # Get performance summary
            summary = asyncio.run(
                integration.get_performance_summary(
                    agent_type=AgentType.SA,
                    window_hours=24
                )
            )
            assert 'cost_by_model' in summary
            assert 'total_cost' in summary
            assert summary['total_cost'] >= 0.08
            
        finally:
            # Cleanup
            if db_path.exists():
                db_path.unlink()
    
    def test_backward_compatibility_with_existing_interfaces(self, model_optimizer):
        """
        Test backward compatibility with existing ModelOptimizer interfaces.
        
        Ensures that the API Model Management system doesn't break existing
        code that uses ModelOptimizer.
        
        Validates: Requirement 13.5
        """
        # Test that all existing ModelOptimizer methods still work
        task = AgentTask(
            type="implementation",
            input=TaskInput(data={"feature": "User login"}),
            context=TaskContext(workflow_id="test", phase="implementation"),
            priority=TaskPriority.MEDIUM
        )
        
        # Test select_model_for_agent (existing interface)
        model_name, assignment = model_optimizer.select_model_for_agent(
            AgentType.IMPLEMENTATION,
            task
        )
        assert model_name is not None
        assert assignment is not None
        assert isinstance(assignment, ModelAssignment)
        
        # Test allocate_agent_instance (existing interface)
        instance = model_optimizer.allocate_agent_instance(AgentType.IMPLEMENTATION, task)
        assert instance is not None
        
        # Test release_agent_instance (existing interface)
        performance_data = {
            'success': True,
            'latency': 1.5,
            'quality': 0.85,
            'cost': 0.02,
            'tokens': 500
        }
        next_task = model_optimizer.release_agent_instance(
            AgentType.IMPLEMENTATION,
            instance.instance_id,
            performance_data
        )
        # next_task can be None if no queued tasks
        
        # Test get_optimization_stats (existing interface)
        stats = model_optimizer.get_optimization_stats()
        assert 'strategy' in stats
        assert 'total_cost' in stats
        assert 'agent_pools' in stats
        
        # Test optimize_resource_allocation (existing interface)
        recommendations = model_optimizer.optimize_resource_allocation()
        assert 'scaling_actions' in recommendations
        assert 'model_switches' in recommendations
        
        # Verify that all existing data structures are still accessible
        assert hasattr(model_optimizer, 'model_assignments')
        assert hasattr(model_optimizer, 'budget')
        assert hasattr(model_optimizer, 'strategy')
        assert hasattr(model_optimizer, 'agent_pools')
        assert hasattr(model_optimizer, 'performance_data')
        assert hasattr(model_optimizer, 'cost_metrics')
    
    def test_performance_data_flow_between_systems(self, model_optimizer):
        """
        Test performance data flow between API Model Management and ModelOptimizer.
        
        Validates that performance data from API requests flows correctly
        into ModelOptimizer's performance tracking system.
        
        Validates: Requirements 13.2, 13.4
        """
        from agentic_sdlc.orchestration.api_model_management.model_optimizer_integration import (
            ModelOptimizerIntegration
        )
        from agentic_sdlc.orchestration.api_model_management.selector import ModelSelector
        from agentic_sdlc.orchestration.api_model_management.failover_manager import FailoverManager
        from agentic_sdlc.orchestration.api_model_management.performance_monitor import PerformanceMonitor
        from agentic_sdlc.orchestration.api_model_management.cost_tracker import CostTracker
        from agentic_sdlc.orchestration.api_model_management.registry import ModelRegistry
        from agentic_sdlc.orchestration.api_model_management.health_checker import HealthChecker
        from agentic_sdlc.orchestration.api_model_management.rate_limiter import RateLimiter
        from agentic_sdlc.orchestration.api_model_management.database import initialize_database
        from pathlib import Path
        import tempfile
        import asyncio
        
        # Create temporary database
        with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as f:
            db_path = Path(f.name)
        
        try:
            # Initialize database schema
            asyncio.run(initialize_database(db_path))
            
            # Initialize components
            registry = ModelRegistry(Path("agentic_sdlc/orchestration/api_model_management/config/model_registry.json"))
            health_checker = HealthChecker(registry, db_path, check_interval_seconds=300)
            rate_limiter = RateLimiter(registry)
            performance_monitor = PerformanceMonitor(db_path)
            cost_tracker = CostTracker(db_path, daily_budget=100.0)
            
            model_selector = ModelSelector(
                registry=registry,
                health_checker=health_checker,
                rate_limiter=rate_limiter,
                performance_monitor=performance_monitor
            )
            
            failover_manager = FailoverManager(
                model_selector=model_selector,
                db_path=db_path,
                max_retries=3,
                base_backoff_seconds=2
            )
            
            integration = ModelOptimizerIntegration(
                model_selector=model_selector,
                failover_manager=failover_manager,
                performance_monitor=performance_monitor,
                cost_tracker=cost_tracker
            )
            
            # Simulate multiple API requests with varying performance
            test_scenarios = [
                {
                    'agent_type': AgentType.PM,
                    'model_id': 'gpt-4-turbo',
                    'performance': {
                        'success': True,
                        'latency_ms': 2000.0,
                        'quality_score': 0.95,
                        'cost': 0.10,
                        'input_tokens': 1500,
                        'output_tokens': 1000
                    }
                },
                {
                    'agent_type': AgentType.PM,
                    'model_id': 'gpt-4-turbo',
                    'performance': {
                        'success': True,
                        'latency_ms': 2200.0,
                        'quality_score': 0.92,
                        'cost': 0.11,
                        'input_tokens': 1600,
                        'output_tokens': 1100
                    }
                },
                {
                    'agent_type': AgentType.IMPLEMENTATION,
                    'model_id': 'gpt-3.5-turbo',
                    'performance': {
                        'success': True,
                        'latency_ms': 1500.0,
                        'quality_score': 0.85,
                        'cost': 0.03,
                        'input_tokens': 800,
                        'output_tokens': 600
                    }
                },
                {
                    'agent_type': AgentType.IMPLEMENTATION,
                    'model_id': 'gpt-3.5-turbo',
                    'performance': {
                        'success': False,  # Failure case
                        'latency_ms': 3000.0,
                        'quality_score': 0.60,
                        'cost': 0.04,
                        'input_tokens': 900,
                        'output_tokens': 700
                    }
                }
            ]
            
            # Report performance for each scenario
            for i, scenario in enumerate(test_scenarios):
                asyncio.run(
                    integration.report_performance_to_optimizer(
                        agent_type=scenario['agent_type'],
                        task_id=f"task-{i}",
                        model_id=scenario['model_id'],
                        performance_data=scenario['performance']
                    )
                )
            
            # Verify performance data in API performance monitor
            gpt4_perf = asyncio.run(
                performance_monitor.get_model_performance('gpt-4-turbo', window_hours=1)
            )
            assert gpt4_perf.total_requests == 2
            assert gpt4_perf.success_rate == 1.0  # Both succeeded
            assert 2000.0 <= gpt4_perf.average_latency_ms <= 2200.0
            
            gpt35_perf = asyncio.run(
                performance_monitor.get_model_performance('gpt-3.5-turbo', window_hours=1)
            )
            assert gpt35_perf.total_requests == 2
            assert gpt35_perf.success_rate == 0.5  # One success, one failure
            
            # Verify cost tracking
            cost_by_model = asyncio.run(
                cost_tracker.get_cost_by_model(
                    start_date=datetime.now() - timedelta(hours=1),
                    end_date=datetime.now()
                )
            )
            assert 'gpt-4-turbo' in cost_by_model
            assert 'gpt-3.5-turbo' in cost_by_model
            assert cost_by_model['gpt-4-turbo'] >= 0.21  # 0.10 + 0.11
            assert cost_by_model['gpt-3.5-turbo'] >= 0.07  # 0.03 + 0.04
            
            # Verify performance summary
            summary = asyncio.run(
                integration.get_performance_summary(window_hours=1)
            )
            assert summary['total_cost'] >= 0.28  # Sum of all costs
            assert 'cost_by_model' in summary
            
        finally:
            # Cleanup
            if db_path.exists():
                db_path.unlink()
    
    def test_failover_event_reporting_to_optimizer(self, model_optimizer):
        """
        Test failover event reporting from API Model Management to ModelOptimizer.
        
        Validates that failover events are properly reported and tracked.
        
        Validates: Requirement 13.3
        """
        from agentic_sdlc.orchestration.api_model_management.model_optimizer_integration import (
            ModelOptimizerIntegration
        )
        from agentic_sdlc.orchestration.api_model_management.selector import ModelSelector
        from agentic_sdlc.orchestration.api_model_management.failover_manager import FailoverManager
        from agentic_sdlc.orchestration.api_model_management.performance_monitor import PerformanceMonitor
        from agentic_sdlc.orchestration.api_model_management.cost_tracker import CostTracker
        from agentic_sdlc.orchestration.api_model_management.registry import ModelRegistry
        from agentic_sdlc.orchestration.api_model_management.health_checker import HealthChecker
        from agentic_sdlc.orchestration.api_model_management.rate_limiter import RateLimiter
        from agentic_sdlc.orchestration.api_model_management.models import FailoverReason
        from agentic_sdlc.orchestration.api_model_management.database import initialize_database
        from pathlib import Path
        import tempfile
        import asyncio
        
        # Create temporary database
        with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as f:
            db_path = Path(f.name)
        
        try:
            # Initialize database schema
            asyncio.run(initialize_database(db_path))
            
            # Initialize components
            registry = ModelRegistry(Path("agentic_sdlc/orchestration/api_model_management/config/model_registry.json"))
            health_checker = HealthChecker(registry, db_path, check_interval_seconds=300)
            rate_limiter = RateLimiter(registry)
            performance_monitor = PerformanceMonitor(db_path)
            cost_tracker = CostTracker(db_path, daily_budget=100.0)
            
            model_selector = ModelSelector(
                registry=registry,
                health_checker=health_checker,
                rate_limiter=rate_limiter,
                performance_monitor=performance_monitor
            )
            
            failover_manager = FailoverManager(
                model_selector=model_selector,
                db_path=db_path,
                max_retries=3,
                base_backoff_seconds=2
            )
            
            integration = ModelOptimizerIntegration(
                model_selector=model_selector,
                failover_manager=failover_manager,
                performance_monitor=performance_monitor,
                cost_tracker=cost_tracker
            )
            
            # Report various failover events
            failover_scenarios = [
                {
                    'agent_type': AgentType.PM,
                    'task_id': 'task-1',
                    'original_model': 'gpt-4-turbo',
                    'alternative_model': 'gpt-4',
                    'reason': FailoverReason.RATE_LIMITED
                },
                {
                    'agent_type': AgentType.SA,
                    'task_id': 'task-2',
                    'original_model': 'claude-3.5-sonnet',
                    'alternative_model': 'claude-3-sonnet',
                    'reason': FailoverReason.UNAVAILABLE
                },
                {
                    'agent_type': AgentType.IMPLEMENTATION,
                    'task_id': 'task-3',
                    'original_model': 'gpt-3.5-turbo',
                    'alternative_model': 'claude-3-haiku',
                    'reason': FailoverReason.ERROR
                }
            ]
            
            # Report each failover event
            for scenario in failover_scenarios:
                asyncio.run(
                    integration.report_failover_event(
                        agent_type=scenario['agent_type'],
                        task_id=scenario['task_id'],
                        original_model=scenario['original_model'],
                        alternative_model=scenario['alternative_model'],
                        reason=scenario['reason']
                    )
                )
            
            # Verify failover events were recorded
            # Query the failover manager's database to check events
            import aiosqlite
            
            async def check_failover_events():
                async with aiosqlite.connect(db_path) as db:
                    cursor = await db.execute(
                        "SELECT COUNT(*) FROM failover_events"
                    )
                    count = await cursor.fetchone()
                    return count[0]
            
            event_count = asyncio.run(check_failover_events())
            assert event_count == 3, f"Expected 3 failover events, got {event_count}"
            
            # Verify that failover events are tracked by reason
            async def check_failover_by_reason():
                async with aiosqlite.connect(db_path) as db:
                    cursor = await db.execute(
                        "SELECT reason, COUNT(*) FROM failover_events GROUP BY reason"
                    )
                    results = await cursor.fetchall()
                    return {row[0]: row[1] for row in results}
            
            events_by_reason = asyncio.run(check_failover_by_reason())
            assert events_by_reason.get('rate_limited', 0) == 1
            assert events_by_reason.get('unavailable', 0) == 1
            assert events_by_reason.get('error', 0) == 1
            
        finally:
            # Cleanup
            if db_path.exists():
                db_path.unlink()
    
    def test_api_assignment_caching(self, model_optimizer):
        """
        Test caching of API model assignments for performance optimization.
        
        Validates: Requirement 13.1
        """
        from agentic_sdlc.orchestration.api_model_management.model_optimizer_integration import (
            ModelOptimizerIntegration
        )
        from agentic_sdlc.orchestration.api_model_management.selector import ModelSelector
        from agentic_sdlc.orchestration.api_model_management.failover_manager import FailoverManager
        from agentic_sdlc.orchestration.api_model_management.performance_monitor import PerformanceMonitor
        from agentic_sdlc.orchestration.api_model_management.cost_tracker import CostTracker
        from agentic_sdlc.orchestration.api_model_management.registry import ModelRegistry
        from agentic_sdlc.orchestration.api_model_management.health_checker import HealthChecker
        from agentic_sdlc.orchestration.api_model_management.rate_limiter import RateLimiter
        from agentic_sdlc.orchestration.api_model_management.database import initialize_database
        from pathlib import Path
        import tempfile
        import asyncio
        
        # Create temporary database
        with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as f:
            db_path = Path(f.name)
        
        try:
            # Initialize database schema
            asyncio.run(initialize_database(db_path))
            
            # Initialize components
            registry = ModelRegistry(Path("agentic_sdlc/orchestration/api_model_management/config/model_registry.json"))
            health_checker = HealthChecker(registry, db_path, check_interval_seconds=300)
            rate_limiter = RateLimiter(registry)
            performance_monitor = PerformanceMonitor(db_path)
            cost_tracker = CostTracker(db_path, daily_budget=100.0)
            
            model_selector = ModelSelector(
                registry=registry,
                health_checker=health_checker,
                rate_limiter=rate_limiter,
                performance_monitor=performance_monitor
            )
            
            failover_manager = FailoverManager(
                model_selector=model_selector,
                db_path=db_path,
                max_retries=3,
                base_backoff_seconds=2
            )
            
            integration = ModelOptimizerIntegration(
                model_selector=model_selector,
                failover_manager=failover_manager,
                performance_monitor=performance_monitor,
                cost_tracker=cost_tracker
            )
            
            # Create a task
            task = AgentTask(
                type="analysis",
                input=TaskInput(data={"requirement": "Test requirement"}),
                context=TaskContext(workflow_id="test", phase="analysis"),
                priority=TaskPriority.MEDIUM
            )
            
            # Get base assignment
            base_model, base_assignment = model_optimizer.select_model_for_agent(
                AgentType.PM,
                task
            )
            
            # Select API model (should cache the assignment)
            api_assignment = asyncio.run(
                integration.select_model_for_agent(
                    agent_type=AgentType.PM,
                    task=task,
                    base_assignment=base_assignment
                )
            )
            
            # Retrieve cached assignment
            cached_assignment = integration.get_cached_assignment(AgentType.PM, task.id)
            assert cached_assignment is not None
            assert cached_assignment.selected_model_id == api_assignment.selected_model_id
            assert cached_assignment.api_provider == api_assignment.api_provider
            
            # Clear cache for specific agent type
            integration.clear_assignment_cache(AgentType.PM)
            cached_assignment = integration.get_cached_assignment(AgentType.PM, task.id)
            assert cached_assignment is None
            
            # Select again and verify new cache entry
            api_assignment2 = asyncio.run(
                integration.select_model_for_agent(
                    agent_type=AgentType.PM,
                    task=task,
                    base_assignment=base_assignment
                )
            )
            cached_assignment = integration.get_cached_assignment(AgentType.PM, task.id)
            assert cached_assignment is not None
            
            # Clear all cache
            integration.clear_assignment_cache()
            cached_assignment = integration.get_cached_assignment(AgentType.PM, task.id)
            assert cached_assignment is None
            
        finally:
            # Cleanup
            if db_path.exists():
                db_path.unlink()


if __name__ == "__main__":
    pytest.main([__file__])
