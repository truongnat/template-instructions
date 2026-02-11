"""
End-to-end integration tests for API Model Management system.

This module contains comprehensive integration tests that validate the complete
request flow through the API Model Management system, including:
- Task submission → Model selection → API request → Response evaluation → Caching
- Failover scenarios with unavailable models
- Rate limit detection and handling
- Cost tracking and budget alerts
- Performance monitoring and degradation detection

Validates: Requirements 2.1, 5.1, 4.3, 10.3, 11.4
"""

import pytest
import asyncio
import tempfile
from pathlib import Path
from datetime import datetime, timedelta
from unittest.mock import AsyncMock, MagicMock, patch
from typing import Dict, Any

from agentic_sdlc.orchestration.api_model_management.registry import ModelRegistry
from agentic_sdlc.orchestration.api_model_management.selector import ModelSelector
from agentic_sdlc.orchestration.api_model_management.health_checker import HealthChecker
from agentic_sdlc.orchestration.api_model_management.rate_limiter import RateLimiter
from agentic_sdlc.orchestration.api_model_management.failover_manager import FailoverManager
from agentic_sdlc.orchestration.api_model_management.api_client import APIClientManager
from agentic_sdlc.orchestration.api_model_management.evaluator import ResponseEvaluator
from agentic_sdlc.orchestration.api_model_management.cache_manager import CacheManager
from agentic_sdlc.orchestration.api_model_management.cost_tracker import CostTracker
from agentic_sdlc.orchestration.api_model_management.performance_monitor import PerformanceMonitor
from agentic_sdlc.orchestration.api_model_management.api_key_manager import APIKeyManager
from agentic_sdlc.orchestration.api_model_management.database import initialize_database
from agentic_sdlc.orchestration.api_model_management.models import (
    ModelRequest, ModelResponse, TokenUsage, HealthStatus
)
from agentic_sdlc.orchestration.models.agent import (
    AgentTask, TaskInput, TaskContext, TaskRequirement, TaskPriority, 
    DataFormat, AgentType
)
from agentic_sdlc.orchestration.api_model_management.adapters.base import ProviderAdapter


@pytest.fixture
def temp_db():
    """Create a temporary database for testing."""
    with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as f:
        db_path = Path(f.name)
    
    # Initialize database synchronously
    asyncio.run(initialize_database(db_path))
    
    yield db_path
    
    # Cleanup
    if db_path.exists():
        db_path.unlink()


@pytest.fixture
def mock_registry():
    """Create a mock model registry with test models."""
    registry = MagicMock(spec=ModelRegistry)
    
    # Mock models
    from agentic_sdlc.orchestration.api_model_management.models import (
        ModelMetadata, RateLimits
    )
    
    gpt4_model = ModelMetadata(
        id="gpt-4-turbo",
        provider="openai",
        name="GPT-4 Turbo",
        capabilities=["text-generation", "code-generation"],
        cost_per_1k_input_tokens=0.01,
        cost_per_1k_output_tokens=0.03,
        rate_limits=RateLimits(requests_per_minute=500, tokens_per_minute=150000),
        context_window=128000,
        average_response_time_ms=2000,
        enabled=True
    )
    
    claude_model = ModelMetadata(
        id="claude-3.5-sonnet",
        provider="anthropic",
        name="Claude 3.5 Sonnet",
        capabilities=["text-generation", "code-generation"],
        cost_per_1k_input_tokens=0.003,
        cost_per_1k_output_tokens=0.015,
        rate_limits=RateLimits(requests_per_minute=1000, tokens_per_minute=200000),
        context_window=200000,
        average_response_time_ms=1500,
        enabled=True
    )
    
    gemini_model = ModelMetadata(
        id="gemini-pro",
        provider="google",
        name="Gemini Pro",
        capabilities=["text-generation"],
        cost_per_1k_input_tokens=0.0005,
        cost_per_1k_output_tokens=0.0015,
        rate_limits=RateLimits(requests_per_minute=60, tokens_per_minute=32000),
        context_window=32000,
        average_response_time_ms=1000,
        enabled=True
    )
    
    # Setup mock methods
    def get_model_side_effect(model_id):
        models = {
            "gpt-4-turbo": gpt4_model,
            "claude-3.5-sonnet": claude_model,
            "gemini-pro": gemini_model
        }
        return models.get(model_id)
    
    registry.get_model.side_effect = get_model_side_effect
    registry.get_models_by_capability.return_value = [gpt4_model, claude_model, gemini_model]
    registry._models = {
        "gpt-4-turbo": gpt4_model,
        "claude-3.5-sonnet": claude_model,
        "gemini-pro": gemini_model
    }
    
    return registry


@pytest.fixture
def sample_task():
    """Create a sample task for testing."""
    return AgentTask(
        type="code_generation",
        input=TaskInput(
            data={"prompt": "Write a Python function to calculate factorial"},
            format=DataFormat.TEXT
        ),
        context=TaskContext(
            workflow_id="test-workflow",
            phase="implementation",
            dependencies=[]
        ),
        requirements=[
            TaskRequirement("req-1", "Must handle edge cases"),
            TaskRequirement("req-2", "Must include docstring")
        ],
        priority=TaskPriority.MEDIUM
    )


@pytest.fixture
def mock_adapter():
    """Create a mock provider adapter."""
    adapter = AsyncMock(spec=ProviderAdapter)
    
    # Default successful response
    adapter.send_request.return_value = ModelResponse(
        content="def factorial(n):\n    '''Calculate factorial of n'''\n    return 1 if n <= 1 else n * factorial(n-1)",
        model_id="gpt-4-turbo",
        token_usage=TokenUsage(input_tokens=50, output_tokens=100, total_tokens=150),
        latency_ms=1500.0,
        cost=0.0035,
        metadata={}
    )
    
    # Mock calculate_cost method
    def calculate_cost(input_tokens, output_tokens, input_cost_per_1k, output_cost_per_1k):
        return (input_tokens / 1000 * input_cost_per_1k) + (output_tokens / 1000 * output_cost_per_1k)
    
    adapter.calculate_cost = calculate_cost
    
    return adapter


class TestCompleteRequestFlow:
    """
    Test complete request flow: Task → Selection → API → Evaluation → Caching
    
    Validates: Requirement 2.1
    """
    
    @pytest.mark.asyncio
    async def test_end_to_end_request_flow(self, temp_db, mock_registry, sample_task, mock_adapter):
        """
        Test the complete flow from task submission to cached response.
        
        Flow:
        1. Task submitted
        2. Model selected based on requirements
        3. API request sent
        4. Response evaluated for quality
        5. Response cached
        6. Subsequent identical request served from cache
        """
        # Initialize components
        health_checker = HealthChecker(mock_registry, temp_db, check_interval_seconds=300)
        rate_limiter = RateLimiter(mock_registry)
        performance_monitor = PerformanceMonitor(temp_db)
        cost_tracker = CostTracker(temp_db, daily_budget=100.0)
        cache_manager = CacheManager(temp_db, max_size_mb=100, default_ttl_seconds=3600)
        evaluator = ResponseEvaluator(quality_threshold=0.7, evaluation_window=10)
        
        model_selector = ModelSelector(
            registry=mock_registry,
            health_checker=health_checker,
            rate_limiter=rate_limiter,
            performance_monitor=performance_monitor
        )
        
        # Mock API key manager
        api_key_manager = MagicMock(spec=APIKeyManager)
        api_key_manager.get_key.return_value = "test-api-key"
        
        # Create API client with mock adapter
        api_client = APIClientManager(
            api_key_manager=api_key_manager,
            registry=mock_registry,
            adapters={"openai": mock_adapter, "anthropic": mock_adapter, "google": mock_adapter}
        )
        
        # Step 1: Select model
        selection = await model_selector.select_model(
            task=sample_task,
            agent_type=AgentType.IMPLEMENTATION
        )
        
        assert selection.model_id is not None
        assert selection.suitability_score > 0
        
        # Step 2: Create request
        request = ModelRequest(
            prompt=sample_task.input.data["prompt"],
            parameters={"temperature": 0.7, "max_tokens": 1000},
            task_id="test-task-1",
            agent_type=AgentType.IMPLEMENTATION.value  # Use string value
        )
        
        # Step 3: Check cache (should miss)
        cache_key = cache_manager.generate_cache_key(request)
        cached_response = await cache_manager.get(cache_key)
        assert cached_response is None
        
        # Step 4: Send API request
        response = await api_client.send_request(selection.model_id, request)
        
        assert response.content is not None
        assert response.token_usage.total_tokens > 0
        assert response.cost > 0
        
        # Step 5: Evaluate response quality
        quality_score = await evaluator.evaluate_response(response, sample_task)
        
        assert quality_score.overall_score >= 0
        assert quality_score.overall_score <= 1.0
        
        # Step 6: Cache response
        await cache_manager.set(cache_key, response, ttl_seconds=3600)
        
        # Step 7: Record cost and performance
        await cost_tracker.record_cost(
            model_id=response.model_id,
            agent_type=AgentType.IMPLEMENTATION.value,
            input_tokens=response.token_usage.input_tokens,
            output_tokens=response.token_usage.output_tokens,
            cost=response.cost,
            task_id="test-task-1"
        )
        
        await performance_monitor.record_performance(
            model_id=response.model_id,
            agent_type=AgentType.IMPLEMENTATION.value,
            latency_ms=response.latency_ms,
            success=True,
            quality_score=quality_score.overall_score,
            task_id="test-task-1"
        )
        
        # Step 8: Verify cache hit on second request
        cached_response = await cache_manager.get(cache_key)
        assert cached_response is not None
        assert cached_response.response.content == response.content
        
        # Step 9: Verify cost tracking
        daily_cost = await cost_tracker.get_daily_cost()
        assert daily_cost == response.cost
        
        # Step 10: Verify performance tracking
        perf_metrics = await performance_monitor.get_model_performance(
            model_id=response.model_id,
            window_hours=24
        )
        assert perf_metrics.total_requests == 1
        assert perf_metrics.successful_requests == 1


class TestFailoverScenario:
    """
    Test failover scenario: Unavailable → Alternative → Success
    
    Validates: Requirement 5.1
    """
    
    @pytest.mark.asyncio
    async def test_automatic_failover_on_unavailability(self, temp_db, mock_registry, sample_task):
        """
        Test automatic failover when primary model is unavailable.
        
        Flow:
        1. Primary model selected
        2. Primary model marked as unavailable
        3. Failover triggered automatically
        4. Alternative model selected
        5. Request succeeds with alternative
        6. Failover event logged
        """
        # Initialize components
        health_checker = HealthChecker(mock_registry, temp_db, check_interval_seconds=300)
        rate_limiter = RateLimiter(mock_registry)
        performance_monitor = PerformanceMonitor(temp_db)
        
        model_selector = ModelSelector(
            registry=mock_registry,
            health_checker=health_checker,
            rate_limiter=rate_limiter,
            performance_monitor=performance_monitor
        )
        
        failover_manager = FailoverManager(
            model_selector=model_selector,
            db_path=temp_db,
            max_retries=3,
            base_backoff_seconds=1
        )
        
        # Mark primary model as unavailable
        primary_model = "gpt-4-turbo"
        health_checker._health_status[primary_model] = HealthStatus(
            model_id=primary_model,
            is_available=False,
            response_time_ms=0.0,
            last_check=datetime.now(),
            consecutive_failures=3,
            error_message="Model unavailable"
        )
        
        # Create mock request function that fails for primary, succeeds for alternative
        async def mock_request_func(model_id: str, request: ModelRequest) -> ModelResponse:
            if model_id == primary_model:
                from agentic_sdlc.orchestration.api_model_management.exceptions import ModelUnavailableError
                raise ModelUnavailableError(
                    f"Model {model_id} is unavailable",
                    model_id=model_id
                )
            
            return ModelResponse(
                content="Alternative model response",
                model_id=model_id,
                token_usage=TokenUsage(input_tokens=50, output_tokens=100, total_tokens=150),
                latency_ms=1200.0,
                cost=0.0025,
                metadata={}
            )
        
        # Execute with failover
        request = ModelRequest(
            prompt="Test prompt",
            parameters={},
            task_id="test-task-failover",
            agent_type=AgentType.IMPLEMENTATION.value
        )
        
        response = await failover_manager.execute_with_failover(
            primary_model=primary_model,
            task=sample_task,
            agent_type=AgentType.IMPLEMENTATION.value,
            request_func=lambda model_id: mock_request_func(model_id, request)
        )
        
        # Verify failover occurred
        assert response.model_id != primary_model
        assert response.content == "Alternative model response"
        
        # Verify failover event was logged
        import aiosqlite
        async with aiosqlite.connect(temp_db) as db:
            async with db.execute(
                "SELECT COUNT(*) FROM failover_events WHERE original_model = ?",
                (primary_model,)
            ) as cursor:
                count = await cursor.fetchone()
                assert count[0] >= 1


class TestRateLimitScenario:
    """
    Test rate limit scenario: Approach limit → Failover → Reset → Recovery
    
    Validates: Requirement 4.3
    """
    
    @pytest.mark.asyncio
    async def test_rate_limit_detection_and_recovery(self, temp_db, mock_registry, sample_task):
        """
        Test rate limit detection, failover, and recovery after reset.
        
        Flow:
        1. Multiple requests approach rate limit (90% threshold)
        2. Model marked as rate-limited
        3. Subsequent requests trigger failover
        4. Rate limit window expires
        5. Model becomes available again
        6. Requests resume to original model
        """
        # Initialize components
        health_checker = HealthChecker(mock_registry, temp_db, check_interval_seconds=300)
        rate_limiter = RateLimiter(mock_registry)
        performance_monitor = PerformanceMonitor(temp_db)
        
        model_selector = ModelSelector(
            registry=mock_registry,
            health_checker=health_checker,
            rate_limiter=rate_limiter,
            performance_monitor=performance_monitor
        )
        
        model_id = "gemini-pro"
        model_metadata = mock_registry.get_model(model_id)
        
        # Simulate approaching rate limit (90% of 60 requests/minute = 54 requests)
        for i in range(54):
            await rate_limiter.record_request(
                model_id=model_id,
                tokens_used=100,
                was_rate_limited=False
            )
        
        # Check rate limit status
        status = await rate_limiter.check_rate_limit(model_id, estimated_tokens=100)
        assert status.is_limited is True
        
        # Verify model is excluded from selection
        selection = await model_selector.select_model(
            task=sample_task,
            agent_type=AgentType.IMPLEMENTATION
        )
        assert selection.model_id != model_id  # Should select alternative
        
        # Simulate rate limit window reset
        rate_limiter._request_history[model_id] = []
        rate_limiter._rate_limit_status.pop(model_id, None)
        
        # Verify model is available again
        status = await rate_limiter.check_rate_limit(model_id, estimated_tokens=100)
        assert status.is_limited is False
        
        # Verify model can be selected again
        # (May or may not be selected depending on suitability score, but should be available)
        is_available = not rate_limiter.is_rate_limited(model_id)
        assert is_available is True


class TestCostTrackingScenario:
    """
    Test cost tracking: Multiple requests → Aggregation → Budget alert
    
    Validates: Requirement 10.3
    """
    
    @pytest.mark.asyncio
    async def test_cost_tracking_and_budget_alert(self, temp_db, mock_registry):
        """
        Test cost tracking across multiple requests and budget alert triggering.
        
        Flow:
        1. Multiple requests with varying costs
        2. Costs aggregated by model and time period
        3. Daily budget threshold exceeded
        4. Budget alert triggered
        5. Cost queries return accurate aggregations
        """
        cost_tracker = CostTracker(temp_db, daily_budget=10.0)
        
        # Simulate multiple requests with costs
        requests = [
            ("gpt-4-turbo", AgentType.IMPLEMENTATION.value, 1000, 2000, 0.07),  # $0.07
            ("gpt-4-turbo", AgentType.SA.value, 500, 1500, 0.05),  # $0.05
            ("claude-3.5-sonnet", AgentType.BA.value, 2000, 3000, 0.051),  # $0.051
            ("claude-3.5-sonnet", AgentType.IMPLEMENTATION.value, 1500, 2500, 0.0495),  # $0.0495
            ("gpt-4-turbo", AgentType.PM.value, 3000, 5000, 0.18),  # $0.18
        ]
        
        for i, (model_id, agent_type, input_tokens, output_tokens, cost) in enumerate(requests):
            await cost_tracker.record_cost(
                model_id=model_id,
                agent_type=agent_type,
                input_tokens=input_tokens,
                output_tokens=output_tokens,
                cost=cost,
                task_id=f"task-{i}"
            )
        
        # Verify daily cost aggregation
        daily_cost = await cost_tracker.get_daily_cost()
        expected_total = sum(req[4] for req in requests)
        assert abs(daily_cost - expected_total) < 0.001
        
        # Verify cost by model aggregation
        start_date = datetime.now() - timedelta(hours=1)
        end_date = datetime.now() + timedelta(hours=1)
        cost_by_model = await cost_tracker.get_cost_by_model(start_date, end_date)
        
        assert "gpt-4-turbo" in cost_by_model
        assert "claude-3.5-sonnet" in cost_by_model
        
        gpt4_cost = sum(req[4] for req in requests if req[0] == "gpt-4-turbo")
        claude_cost = sum(req[4] for req in requests if req[0] == "claude-3.5-sonnet")
        
        assert abs(cost_by_model["gpt-4-turbo"] - gpt4_cost) < 0.001
        assert abs(cost_by_model["claude-3.5-sonnet"] - claude_cost) < 0.001
        
        # Add more requests to exceed budget ($10 limit)
        # Current total is ~$0.40, need to add ~$10 more
        for i in range(30):  # 30 * $0.35 = $10.50
            await cost_tracker.record_cost(
                model_id="gpt-4-turbo",
                agent_type=AgentType.IMPLEMENTATION.value,
                input_tokens=5000,
                output_tokens=10000,
                cost=0.35,  # $0.35 per request
                task_id=f"task-budget-{i}"
            )
        
        # Check budget status
        budget_status = await cost_tracker.check_budget()
        
        assert budget_status.is_over_budget is True
        assert budget_status.utilization_percent > 100.0
        assert budget_status.remaining_budget <= 0  # Should be 0 or negative when over budget


class TestPerformanceMonitoringScenario:
    """
    Test performance monitoring: Multiple requests → Metrics → Degradation detection
    
    Validates: Requirement 11.4
    """
    
    @pytest.mark.asyncio
    async def test_performance_monitoring_and_degradation_detection(self, temp_db):
        """
        Test performance monitoring and degradation detection.
        
        Flow:
        1. Multiple successful requests with good performance
        2. Performance metrics calculated (latency, success rate, quality)
        3. Series of failed requests
        4. Success rate drops below threshold
        5. Performance degradation alert triggered
        """
        performance_monitor = PerformanceMonitor(temp_db)
        
        model_id = "gpt-4-turbo"
        
        # Record successful requests with good performance
        for i in range(10):
            await performance_monitor.record_performance(
                model_id=model_id,
                agent_type=AgentType.IMPLEMENTATION.value,
                latency_ms=1500.0 + (i * 100),  # Varying latency
                success=True,
                quality_score=0.85,
                task_id=f"task-success-{i}"
            )
        
        # Get performance metrics
        metrics = await performance_monitor.get_model_performance(
            model_id=model_id,
            window_hours=24
        )
        
        assert metrics.total_requests == 10
        assert metrics.successful_requests == 10
        assert metrics.success_rate == 1.0
        assert abs(metrics.average_quality_score - 0.85) < 0.01  # Allow small floating point error
        
        # Record failed requests to trigger degradation
        for i in range(15):
            await performance_monitor.record_performance(
                model_id=model_id,
                agent_type=AgentType.IMPLEMENTATION.value,
                latency_ms=5000.0,  # High latency
                success=False,
                quality_score=0.0,
                task_id=f"task-fail-{i}"
            )
        
        # Get updated metrics
        metrics = await performance_monitor.get_model_performance(
            model_id=model_id,
            window_hours=24
        )
        
        assert metrics.total_requests == 25
        assert metrics.successful_requests == 10
        assert metrics.failed_requests == 15
        assert metrics.success_rate == 0.4  # 10/25 = 40%
        
        # Detect degradation (threshold is 80%)
        degradation = await performance_monitor.detect_degradation(
            model_id=model_id,
            threshold=0.8
        )
        
        assert degradation is not None
        assert degradation.metric == "success_rate"
        assert degradation.current_value < degradation.threshold


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])
