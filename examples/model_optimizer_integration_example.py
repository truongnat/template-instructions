"""
Example: ModelOptimizer Integration with API Model Management

This example demonstrates how to integrate the API Model Management system
with the existing ModelOptimizer for intelligent model selection and
performance tracking.
"""

import asyncio
from pathlib import Path
from datetime import datetime

from agentic_sdlc.orchestration.models.agent import (
    AgentType, AgentTask, ModelAssignment, ModelTier, TaskPriority,
    TaskContext, TaskInput, DataFormat
)
from agentic_sdlc.orchestration.api_model_management.registry import ModelRegistry
from agentic_sdlc.orchestration.api_model_management.health_checker import HealthChecker
from agentic_sdlc.orchestration.api_model_management.rate_limiter import RateLimiter
from agentic_sdlc.orchestration.api_model_management.performance_monitor import PerformanceMonitor
from agentic_sdlc.orchestration.api_model_management.cost_tracker import CostTracker
from agentic_sdlc.orchestration.api_model_management.selector import ModelSelector
from agentic_sdlc.orchestration.api_model_management.failover_manager import FailoverManager
from agentic_sdlc.orchestration.api_model_management.model_optimizer_integration import (
    ModelOptimizerIntegration, APIModelAssignment
)
from agentic_sdlc.orchestration.api_model_management.models import (
    SelectionConstraints, FailoverReason
)


async def main():
    """Demonstrate ModelOptimizer integration."""
    
    print("=" * 80)
    print("ModelOptimizer Integration Example")
    print("=" * 80)
    print()
    
    # Initialize API Model Management components
    print("1. Initializing API Model Management components...")
    
    # Model Registry
    config_path = Path("agentic_sdlc/orchestration/api_model_management/config/model_registry.json")
    registry = ModelRegistry(config_path=config_path)
    
    # Database path for persistence
    db_path = Path("test_integration.db")
    
    # Health Checker
    health_checker = HealthChecker(
        registry=registry,
        db_path=db_path,
        check_interval_seconds=60
    )
    
    # Rate Limiter
    rate_limiter = RateLimiter(registry=registry)
    
    # Performance Monitor
    performance_monitor = PerformanceMonitor(db_path=db_path)
    
    # Cost Tracker
    cost_tracker = CostTracker(
        db_path=db_path,
        daily_budget=100.0
    )
    
    # Model Selector
    model_selector = ModelSelector(
        registry=registry,
        health_checker=health_checker,
        rate_limiter=rate_limiter,
        performance_monitor=performance_monitor
    )
    
    # Failover Manager
    failover_manager = FailoverManager(
        model_selector=model_selector,
        db_path=db_path,
        max_retries=3,
        base_backoff_seconds=2
    )
    
    # Integration Layer
    integration = ModelOptimizerIntegration(
        model_selector=model_selector,
        failover_manager=failover_manager,
        performance_monitor=performance_monitor,
        cost_tracker=cost_tracker
    )
    
    print("✓ Components initialized")
    print()
    
    # Create a base ModelAssignment (from ModelOptimizer)
    print("2. Creating base ModelAssignment from ModelOptimizer...")
    
    base_assignment = ModelAssignment(
        role_type=AgentType.SA,
        model_tier=ModelTier.STRATEGIC,
        recommended_model="gpt-4-turbo",
        fallback_model="gpt-3.5-turbo",
        max_concurrent_instances=5,
        cost_per_token=0.01
    )
    
    print(f"✓ Base assignment created for {base_assignment.role_type.value}")
    print(f"  - Recommended: {base_assignment.recommended_model}")
    print(f"  - Fallback: {base_assignment.fallback_model}")
    print()
    
    # Create a sample task
    print("3. Creating sample task...")
    
    task = AgentTask(
        id="task-001",
        type="analysis",
        priority=TaskPriority.HIGH,
        context=TaskContext(
            workflow_id="workflow-001",
            phase="analysis",
            dependencies=[]
        ),
        input=TaskInput(
            data="System architecture document...",
            format=DataFormat.TEXT,
            metadata={}
        )
    )
    
    print(f"✓ Task created: {task.id}")
    print(f"  - Type: {task.type}")
    print(f"  - Priority: {task.priority.name}")
    print()
    
    # Select model using integration layer
    print("4. Selecting model using API Model Management...")
    
    constraints = SelectionConstraints(
        required_capabilities=["analysis", "code-generation"],
        max_cost_per_request=1.0
    )
    
    api_assignment = await integration.select_model_for_agent(
        agent_type=AgentType.SA,
        task=task,
        base_assignment=base_assignment,
        constraints=constraints
    )
    
    print(f"✓ Model selected: {api_assignment.selected_model_id}")
    print(f"  - Provider: {api_assignment.api_provider}")
    print(f"  - Suitability score: {api_assignment.model_selection.suitability_score:.3f}")
    print(f"  - Selection reason: {api_assignment.model_selection.selection_reason}")
    print(f"  - Alternatives: {', '.join(api_assignment.model_selection.alternatives)}")
    print()
    
    # Simulate task execution and report performance
    print("5. Simulating task execution and reporting performance...")
    
    performance_data = {
        'success': True,
        'latency_ms': 1500.0,
        'quality_score': 0.92,
        'cost': 0.15,
        'input_tokens': 500,
        'output_tokens': 1000
    }
    
    await integration.report_performance_to_optimizer(
        agent_type=AgentType.SA,
        task_id=task.id,
        model_id=api_assignment.selected_model_id,
        performance_data=performance_data
    )
    
    print(f"✓ Performance reported")
    print(f"  - Success: {performance_data['success']}")
    print(f"  - Latency: {performance_data['latency_ms']:.2f}ms")
    print(f"  - Quality: {performance_data['quality_score']:.2f}")
    print(f"  - Cost: ${performance_data['cost']:.2f}")
    print()
    
    # Simulate a failover event
    print("6. Simulating failover event...")
    
    await integration.report_failover_event(
        agent_type=AgentType.SA,
        task_id=task.id,
        original_model="gpt-4-turbo",
        alternative_model="gpt-3.5-turbo",
        reason=FailoverReason.RATE_LIMITED
    )
    
    print(f"✓ Failover event reported")
    print(f"  - Original: gpt-4-turbo")
    print(f"  - Alternative: gpt-3.5-turbo")
    print(f"  - Reason: RATE_LIMITED")
    print()
    
    # Get performance summary
    print("7. Getting performance summary...")
    
    summary = await integration.get_performance_summary(
        agent_type=AgentType.SA,
        window_hours=24
    )
    
    print(f"✓ Performance summary retrieved")
    print(f"  - Window: {summary['window_hours']} hours")
    print(f"  - Agent type: {summary['agent_type']}")
    if 'error' in summary:
        print(f"  - Error: {summary['error']}")
    else:
        print(f"  - Total cost: ${summary.get('total_cost', 0.0):.2f}")
    print()
    
    # Test cached assignment retrieval
    print("8. Testing cached assignment retrieval...")
    
    cached = integration.get_cached_assignment(
        agent_type=AgentType.SA,
        task_id=task.id
    )
    
    if cached:
        print(f"✓ Cached assignment found")
        print(f"  - Model: {cached.selected_model_id}")
        print(f"  - Cached at: {cached.selection_timestamp.isoformat()}")
    else:
        print("✗ No cached assignment found")
    print()
    
    # Clear cache
    print("9. Clearing assignment cache...")
    
    integration.clear_assignment_cache(agent_type=AgentType.SA)
    
    print(f"✓ Cache cleared for {AgentType.SA.value}")
    print()
    
    # Verify cache is cleared
    cached_after_clear = integration.get_cached_assignment(
        agent_type=AgentType.SA,
        task_id=task.id
    )
    
    if cached_after_clear is None:
        print("✓ Cache successfully cleared")
    else:
        print("✗ Cache still contains data")
    print()
    
    # Cleanup
    print("10. Cleaning up...")
    
    await health_checker.stop()
    
    # Remove test database
    if db_path.exists():
        db_path.unlink()
    
    print("✓ Cleanup complete")
    print()
    
    print("=" * 80)
    print("Integration Example Complete")
    print("=" * 80)
    print()
    print("Key Features Demonstrated:")
    print("  ✓ Model selection coordination with ModelOptimizer")
    print("  ✓ Performance feedback reporting")
    print("  ✓ Failover event coordination")
    print("  ✓ Performance summary retrieval")
    print("  ✓ Assignment caching")
    print("  ✓ Backward compatibility with ModelAssignment interface")


if __name__ == "__main__":
    asyncio.run(main())
