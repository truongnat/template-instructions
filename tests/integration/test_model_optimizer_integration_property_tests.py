"""
Property-based tests for ModelOptimizer Integration

This module contains property-based tests for the ModelOptimizer integration layer,
validating that the API Model Management system correctly integrates with the
existing ModelOptimizer.

Properties tested:
- Property 54: ModelOptimizer integration
- Property 55: Failover event reporting
- Property 56: Performance data sharing
- Property 57: ModelOptimizer interface compatibility

Requirements: 13.1, 13.2, 13.3, 13.4, 13.5
"""

import pytest
import tempfile
from pathlib import Path
from datetime import datetime, timedelta
from hypothesis import given, settings, strategies as st
from hypothesis import assume

from agentic_sdlc.orchestration.api_model_management.model_optimizer_integration import (
    ModelOptimizerIntegration,
    APIModelAssignment
)
from agentic_sdlc.orchestration.api_model_management.models import (
    ModelMetadata,
    RateLimits,
    ModelSelection,
    SelectionConstraints,
    FailoverReason,
    PerformanceMetrics
)
from agentic_sdlc.orchestration.api_model_management.selector import ModelSelector
from agentic_sdlc.orchestration.api_model_management.failover_manager import FailoverManager
from agentic_sdlc.orchestration.api_model_management.performance_monitor import PerformanceMonitor
from agentic_sdlc.orchestration.api_model_management.cost_tracker import CostTracker
from agentic_sdlc.orchestration.api_model_management.registry import ModelRegistry
from agentic_sdlc.orchestration.api_model_management.health_checker import HealthChecker
from agentic_sdlc.orchestration.api_model_management.rate_limiter import RateLimiter
from agentic_sdlc.orchestration.models import (
    AgentType,
    AgentTask,
    TaskInput,
    TaskContext,
    TaskPriority,
    DataFormat,
    ModelAssignment,
    ModelTier
)


# Hypothesis strategies for generating test data

@st.composite
def agent_type_strategy(draw):
    """Generate valid AgentType values."""
    return draw(st.sampled_from([
        AgentType.PM,
        AgentType.BA,
        AgentType.SA,
        AgentType.IMPLEMENTATION,
        AgentType.RESEARCH,
        AgentType.QUALITY_JUDGE
    ]))


@st.composite
def task_priority_strategy(draw):
    """Generate valid TaskPriority values."""
    return draw(st.sampled_from([
        TaskPriority.LOW,
        TaskPriority.MEDIUM,
        TaskPriority.HIGH,
        TaskPriority.CRITICAL
    ]))


@st.composite
def agent_task_strategy(draw):
    """Generate valid AgentTask instances."""
    task_id = draw(st.text(min_size=1, max_size=20, alphabet=st.characters(whitelist_categories=('Lu', 'Ll', 'Nd'))))
    task_type = draw(st.text(min_size=1, max_size=30, alphabet=st.characters(whitelist_categories=('Lu', 'Ll'))))
    priority = draw(task_priority_strategy())
    
    return AgentTask(
        type=task_type,
        input=TaskInput(
            data={"test": "data"},
            format=DataFormat.JSON
        ),
        context=TaskContext(
            workflow_id=f"workflow_{task_id}",
            phase="test"
        ),
        priority=priority,
        id=task_id
    )


@st.composite
def model_metadata_strategy(draw):
    """Generate valid ModelMetadata instances."""
    model_id = draw(st.text(min_size=1, max_size=30, alphabet=st.characters(whitelist_categories=('Lu', 'Ll', 'Nd', 'Pd'))))
    provider = draw(st.sampled_from(['openai', 'anthropic', 'google', 'ollama']))
    
    # Always include 'text-generation' to match integration requirements
    capabilities = ['text-generation']
    additional_caps = draw(st.lists(st.sampled_from(['code-generation', 'analysis']), max_size=2, unique=True))
    capabilities.extend(additional_caps)
    
    return ModelMetadata(
        id=model_id,
        provider=provider,
        name=f"Model {model_id}",
        capabilities=capabilities,
        cost_per_1k_input_tokens=draw(st.floats(min_value=0.001, max_value=0.1)),
        cost_per_1k_output_tokens=draw(st.floats(min_value=0.001, max_value=0.3)),
        rate_limits=RateLimits(
            requests_per_minute=draw(st.integers(min_value=10, max_value=1000)),
            tokens_per_minute=draw(st.integers(min_value=10000, max_value=200000))
        ),
        context_window=draw(st.integers(min_value=4000, max_value=200000)),
        average_response_time_ms=draw(st.floats(min_value=100.0, max_value=5000.0)),
        enabled=True
    )


@st.composite
def model_assignment_strategy(draw, agent_type):
    """Generate valid ModelAssignment instances."""
    return ModelAssignment(
        role_type=agent_type,
        model_tier=draw(st.sampled_from([ModelTier.STRATEGIC, ModelTier.OPERATIONAL, ModelTier.RESEARCH])),
        recommended_model=draw(st.text(min_size=1, max_size=20)),
        fallback_model=draw(st.text(min_size=1, max_size=20)),
        max_concurrent_instances=draw(st.integers(min_value=1, max_value=10)),
        cost_per_token=draw(st.floats(min_value=0.00001, max_value=0.001))
    )


@st.composite
def performance_data_strategy(draw):
    """Generate valid performance data dictionaries."""
    return {
        'success': draw(st.booleans()),
        'latency_ms': draw(st.floats(min_value=100.0, max_value=10000.0)),
        'quality_score': draw(st.floats(min_value=0.0, max_value=1.0)),
        'cost': draw(st.floats(min_value=0.001, max_value=1.0)),
        'input_tokens': draw(st.integers(min_value=10, max_value=10000)),
        'output_tokens': draw(st.integers(min_value=10, max_value=10000))
    }


@st.composite
def failover_reason_strategy(draw):
    """Generate valid FailoverReason values."""
    return draw(st.sampled_from([
        FailoverReason.UNAVAILABLE,
        FailoverReason.RATE_LIMITED,
        FailoverReason.ERROR,
        FailoverReason.LOW_QUALITY,
        FailoverReason.TIMEOUT
    ]))


# Helper functions for creating test components

async def create_integration_components():
    """Create integration components for testing (context manager style)."""
    # Create temporary files
    db_file = tempfile.NamedTemporaryFile(suffix='.db', delete=False)
    db_path = Path(db_file.name)
    db_file.close()
    
    config_file = tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False)
    config_file.write('{"models": []}')
    config_path = Path(config_file.name)
    config_file.close()
    
    try:
        # Initialize database tables
        import aiosqlite
        async with aiosqlite.connect(db_path) as db:
            # Create failover_events table
            await db.execute("""
                CREATE TABLE IF NOT EXISTS failover_events (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp DATETIME NOT NULL,
                    original_model TEXT NOT NULL,
                    alternative_model TEXT NOT NULL,
                    reason TEXT NOT NULL,
                    task_id TEXT NOT NULL
                )
            """)
            
            # Create performance_records table
            await db.execute("""
                CREATE TABLE IF NOT EXISTS performance_records (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp DATETIME NOT NULL,
                    model_id TEXT NOT NULL,
                    agent_type TEXT NOT NULL,
                    task_id TEXT NOT NULL,
                    latency_ms REAL NOT NULL,
                    success BOOLEAN NOT NULL,
                    quality_score REAL
                )
            """)
            
            # Create cost_records table
            await db.execute("""
                CREATE TABLE IF NOT EXISTS cost_records (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp DATETIME NOT NULL,
                    model_id TEXT NOT NULL,
                    agent_type TEXT NOT NULL,
                    task_id TEXT NOT NULL,
                    input_tokens INTEGER NOT NULL,
                    output_tokens INTEGER NOT NULL,
                    cost REAL NOT NULL
                )
            """)
            
            await db.commit()
        
        # Create registry
        registry = ModelRegistry(config_path=config_path)
        
        # Create health checker
        health_checker = HealthChecker(
            registry=registry,
            db_path=db_path,
            check_interval_seconds=60
        )
        
        # Create rate limiter
        rate_limiter = RateLimiter(registry=registry)
        
        # Create performance monitor
        performance_monitor = PerformanceMonitor(db_path=db_path)
        
        # Create cost tracker
        cost_tracker = CostTracker(db_path=db_path, daily_budget=100.0)
        
        # Create model selector
        model_selector = ModelSelector(
            registry=registry,
            health_checker=health_checker,
            rate_limiter=rate_limiter,
            performance_monitor=performance_monitor
        )
        
        # Create failover manager
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
        
        components = {
            'integration': integration,
            'registry': registry,
            'model_selector': model_selector,
            'failover_manager': failover_manager,
            'performance_monitor': performance_monitor,
            'cost_tracker': cost_tracker,
            'health_checker': health_checker,
            'rate_limiter': rate_limiter,
            'db_path': db_path,
            'config_path': config_path
        }
        
        return components
        
    except Exception as e:
        # Cleanup on error
        if db_path.exists():
            db_path.unlink()
        if config_path.exists():
            config_path.unlink()
        raise e


async def cleanup_integration_components(components):
    """Cleanup integration components."""
    # Remove temporary files
    try:
        if components['db_path'].exists():
            components['db_path'].unlink()
    except Exception:
        pass
    
    try:
        if components['config_path'].exists():
            components['config_path'].unlink()
    except Exception:
        pass


# Property-based tests

@pytest.mark.asyncio
@settings(max_examples=20, deadline=5000)
@given(
    agent_type=agent_type_strategy(),
    task=agent_task_strategy(),
    model_metadata=model_metadata_strategy()
)
async def test_property_54_model_optimizer_integration(agent_type, task, model_metadata):
    """
    Feature: api-model-management
    Property 54: ModelOptimizer integration
    
    For any model assignment from ModelOptimizer, the API_Client should use
    that model for subsequent API requests.
    
    Validates: Requirements 13.1, 13.2
    """
    components = await create_integration_components()
    try:
        integration = components['integration']
        registry = components['registry']
        
        # Add model to registry
        registry.add_model(model_metadata)
        
        # Create base assignment from ModelOptimizer
        base_assignment = ModelAssignment(
            role_type=agent_type,
            model_tier=ModelTier.STRATEGIC,
            recommended_model=model_metadata.id,
            fallback_model=model_metadata.id,
            max_concurrent_instances=5,
            cost_per_token=0.0001
        )
        
        # Select model through integration layer
        api_assignment = await integration.select_model_for_agent(
            agent_type=agent_type,
            task=task,
            base_assignment=base_assignment
        )
        
        # Property: The API assignment should use a model from the registry
        assert api_assignment is not None
        assert isinstance(api_assignment, APIModelAssignment)
        
        # Property: The selected model should be accessible
        assert api_assignment.selected_model_id is not None
        assert len(api_assignment.selected_model_id) > 0
        
        # Property: The assignment should maintain base assignment properties
        assert api_assignment.role_type == agent_type
        assert api_assignment.base_assignment == base_assignment
        
        # Property: The assignment should have API-specific metadata
        assert api_assignment.api_provider is not None
        assert api_assignment.model_selection is not None
        
        # Property: The assignment should be cached for reuse
        cached = integration.get_cached_assignment(agent_type, task.id)
        assert cached is not None
        assert cached.selected_model_id == api_assignment.selected_model_id
        
    finally:
        await cleanup_integration_components(components)


@pytest.mark.asyncio
@settings(max_examples=20, deadline=5000)
@given(
    agent_type=agent_type_strategy(),
    task_id=st.text(min_size=1, max_size=20, alphabet=st.characters(whitelist_categories=('Lu', 'Ll', 'Nd'))),
    original_model=st.text(min_size=1, max_size=30, alphabet=st.characters(whitelist_categories=('Lu', 'Ll', 'Nd', 'Pd'))),
    alternative_model=st.text(min_size=1, max_size=30, alphabet=st.characters(whitelist_categories=('Lu', 'Ll', 'Nd', 'Pd'))),
    reason=failover_reason_strategy()
)
async def test_property_55_failover_event_reporting(
    agent_type, task_id, original_model, alternative_model, reason
):
    """
    Feature: api-model-management
    Property 55: Failover event reporting
    
    For any API-based failover event, the event details should be reported
    to ModelOptimizer for performance tracking.
    
    Validates: Requirements 13.3
    """
    # Ensure models are different
    assume(original_model != alternative_model)
    
    components = await create_integration_components()
    try:
        integration = components['integration']
        failover_manager = components['failover_manager']
        
        # Report failover event
        await integration.report_failover_event(
            agent_type=agent_type,
            task_id=task_id,
            original_model=original_model,
            alternative_model=alternative_model,
            reason=reason
        )
        
        # Property: Failover event should be recorded in the failover manager
        # Query the database to verify the event was recorded
        import aiosqlite
        async with aiosqlite.connect(failover_manager.db_path) as db:
            cursor = await db.execute(
                """
                SELECT original_model, alternative_model, reason, task_id
                FROM failover_events
                WHERE original_model = ? AND alternative_model = ? AND task_id = ?
                ORDER BY timestamp DESC
                LIMIT 1
                """,
                (original_model, alternative_model, task_id)
            )
            row = await cursor.fetchone()
        
        # Property: The failover event should be persisted with all details
        assert row is not None, "Failover event should be recorded in database"
        assert row[0] == original_model, "Original model should match"
        assert row[1] == alternative_model, "Alternative model should match"
        assert row[2] == reason.value, "Reason should match"
        assert row[3] == task_id, "Task ID should match"
        
    finally:
        await cleanup_integration_components(components)


@pytest.mark.asyncio
@settings(max_examples=20, deadline=5000)
@given(
    agent_type=agent_type_strategy(),
    task_id=st.text(min_size=1, max_size=20, alphabet=st.characters(whitelist_categories=('Lu', 'Ll', 'Nd'))),
    model_id=st.text(min_size=1, max_size=30, alphabet=st.characters(whitelist_categories=('Lu', 'Ll', 'Nd', 'Pd'))),
    performance_data=performance_data_strategy()
)
async def test_property_56_performance_data_sharing(
    agent_type, task_id, model_id, performance_data
):
    """
    Feature: api-model-management
    Property 56: Performance data sharing
    
    For any completed request, performance data (latency, success, quality, cost)
    should be provided to ModelOptimizer.
    
    Validates: Requirements 13.4
    """
    components = await create_integration_components()
    try:
        integration = components['integration']
        performance_monitor = components['performance_monitor']
        cost_tracker = components['cost_tracker']
        
        # Report performance to optimizer
        await integration.report_performance_to_optimizer(
            agent_type=agent_type,
            task_id=task_id,
            model_id=model_id,
            performance_data=performance_data
        )
        
        # Property: Performance data should be recorded in performance monitor
        import aiosqlite
        async with aiosqlite.connect(performance_monitor.db_path) as db:
            cursor = await db.execute(
                """
                SELECT model_id, agent_type, latency_ms, success, quality_score, task_id
                FROM performance_records
                WHERE model_id = ? AND task_id = ?
                ORDER BY timestamp DESC
                LIMIT 1
                """,
                (model_id, task_id)
            )
            perf_row = await cursor.fetchone()
        
        # Property: Performance record should exist with correct data
        assert perf_row is not None, "Performance record should be created"
        assert perf_row[0] == model_id, "Model ID should match"
        assert perf_row[1] == agent_type.value, "Agent type should match"
        assert abs(perf_row[2] - performance_data['latency_ms']) < 0.01, "Latency should match"
        assert perf_row[3] == (1 if performance_data['success'] else 0), "Success status should match"
        assert abs(perf_row[4] - performance_data['quality_score']) < 0.01, "Quality score should match"
        assert perf_row[5] == task_id, "Task ID should match"
        
        # Property: Cost data should be recorded if cost > 0
        if performance_data['cost'] > 0:
            async with aiosqlite.connect(cost_tracker.db_path) as db:
                cursor = await db.execute(
                    """
                    SELECT model_id, agent_type, input_tokens, output_tokens, cost, task_id
                    FROM cost_records
                    WHERE model_id = ? AND task_id = ?
                    ORDER BY timestamp DESC
                    LIMIT 1
                    """,
                    (model_id, task_id)
                )
                cost_row = await cursor.fetchone()
            
            # Property: Cost record should exist with correct data
            assert cost_row is not None, "Cost record should be created when cost > 0"
            assert cost_row[0] == model_id, "Model ID should match"
            assert cost_row[1] == agent_type.value, "Agent type should match"
            assert cost_row[2] == performance_data['input_tokens'], "Input tokens should match"
            assert cost_row[3] == performance_data['output_tokens'], "Output tokens should match"
            assert abs(cost_row[4] - performance_data['cost']) < 0.0001, "Cost should match"
            assert cost_row[5] == task_id, "Task ID should match"
    
    finally:
        await cleanup_integration_components(components)


@pytest.mark.asyncio
@settings(max_examples=10, deadline=5000)
@given(
    agent_type=agent_type_strategy(),
    task=agent_task_strategy(),
    model_metadata=model_metadata_strategy()
)
async def test_property_57_model_optimizer_interface_compatibility(
    agent_type, task, model_metadata
):
    """
    Feature: api-model-management
    Property 57: ModelOptimizer interface compatibility
    
    For any existing ModelOptimizer method call, the API Model Management
    system should support it without requiring code changes.
    
    Validates: Requirements 13.5
    """
    components = await create_integration_components()
    try:
        integration = components['integration']
        registry = components['registry']
        
        # Add model to registry
        registry.add_model(model_metadata)
        
        # Create base assignment (simulating ModelOptimizer output)
        base_assignment = ModelAssignment(
            role_type=agent_type,
            model_tier=ModelTier.STRATEGIC,
            recommended_model=model_metadata.id,
            fallback_model=model_metadata.id,
            max_concurrent_instances=5,
            cost_per_token=0.0001
        )
        
        # Select model through integration
        api_assignment = await integration.select_model_for_agent(
            agent_type=agent_type,
            task=task,
            base_assignment=base_assignment
        )
        
        # Property: API assignment should support all base assignment properties
        assert hasattr(api_assignment, 'role_type'), "Should have role_type property"
        assert hasattr(api_assignment, 'model_tier'), "Should have model_tier property"
        assert hasattr(api_assignment, 'max_concurrent_instances'), "Should have max_concurrent_instances property"
        assert hasattr(api_assignment, 'cost_per_token'), "Should have cost_per_token property"
        
        # Property: Properties should return correct values
        assert api_assignment.role_type == agent_type
        assert api_assignment.model_tier == base_assignment.model_tier
        assert api_assignment.max_concurrent_instances == base_assignment.max_concurrent_instances
        assert api_assignment.cost_per_token == base_assignment.cost_per_token
        
        # Property: Should support get_effective_model method
        assert hasattr(api_assignment, 'get_effective_model'), "Should have get_effective_model method"
        effective_model = api_assignment.get_effective_model()
        assert effective_model is not None
        assert isinstance(effective_model, str)
        assert len(effective_model) > 0
        
        # Property: Should maintain backward compatibility with base assignment
        assert api_assignment.base_assignment == base_assignment
        
        # Property: Cache operations should work
        cached = integration.get_cached_assignment(agent_type, task.id)
        assert cached is not None
        assert cached.selected_model_id == api_assignment.selected_model_id
        
        # Property: Cache clearing should work
        integration.clear_assignment_cache(agent_type)
        cleared_cache = integration.get_cached_assignment(agent_type, task.id)
        assert cleared_cache is None, "Cache should be cleared for specific agent type"
        
    finally:
        await cleanup_integration_components(components)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
