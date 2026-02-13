"""
Property-based tests for concurrency control in API Client Manager.

Feature: api-model-management
Tests Properties 58, 59, and 60 from the design document.
"""

import pytest
import asyncio
from datetime import datetime
from unittest.mock import AsyncMock, Mock
from hypothesis import given, settings, strategies as st

from agentic_sdlc.orchestration.api_model_management.api_client import APIClientManager
from agentic_sdlc.orchestration.api_model_management.models import (
    ModelRequest,
    ModelResponse,
    TokenUsage,
    ModelMetadata,
    RateLimits
)
from agentic_sdlc.orchestration.api_model_management.api_key_manager import APIKeyManager
from agentic_sdlc.orchestration.api_model_management.registry import ModelRegistry
from agentic_sdlc.orchestration.api_model_management.adapters.base import ProviderAdapter


# Test strategies
@st.composite
def model_request_strategy(draw):
    """Generate random ModelRequest objects."""
    return ModelRequest(
        prompt=draw(st.text(min_size=1, max_size=100)),
        parameters=draw(st.dictionaries(st.text(min_size=1, max_size=10), st.integers())),
        task_id=draw(st.text(min_size=1, max_size=20)),
        agent_type=draw(st.sampled_from(["pm", "ba", "sa", "research", "quality", "implementation"])),
        max_tokens=draw(st.one_of(st.none(), st.integers(min_value=1, max_value=4000))),
        temperature=draw(st.floats(min_value=0.0, max_value=2.0))
    )


# Helper functions to create mocks
def create_mock_registry(provider="test_provider"):
    """Create a mock registry with test model."""
    registry = Mock(spec=ModelRegistry)
    model_metadata = ModelMetadata(
        id="test_model",
        provider=provider,
        name="Test Model",
        capabilities=["text-generation"],
        cost_per_1k_input_tokens=0.01,
        cost_per_1k_output_tokens=0.03,
        rate_limits=RateLimits(requests_per_minute=100, tokens_per_minute=10000),
        context_window=4096,
        average_response_time_ms=1000.0,
        enabled=True
    )
    registry.get_model.return_value = model_metadata
    return registry


def create_mock_api_key_manager():
    """Create a mock API key manager."""
    manager = Mock(spec=APIKeyManager)
    manager.get_key.return_value = "test_api_key"
    return manager


def create_mock_adapter():
    """Create a mock provider adapter."""
    adapter = AsyncMock(spec=ProviderAdapter)
    adapter.calculate_cost.return_value = 0.05
    return adapter


def create_api_client(max_concurrent=100, per_provider_limits=None):
    """Create API client with mocked dependencies."""
    mock_registry = create_mock_registry()
    mock_api_key_manager = create_mock_api_key_manager()
    mock_adapter = create_mock_adapter()
    adapters = {"test_provider": mock_adapter}
    
    client = APIClientManager(
        api_key_manager=mock_api_key_manager,
        registry=mock_registry,
        adapters=adapters,
        max_concurrent_requests=max_concurrent,
        max_concurrent_per_provider=per_provider_limits or {"test_provider": 10}
    )
    return client, mock_adapter


# Property 58: Concurrent request processing
@settings(max_examples=5, deadline=10000)
@given(
    num_requests=st.integers(min_value=2, max_value=15),
    concurrency_limit=st.integers(min_value=5, max_value=20)
)
@pytest.mark.asyncio
async def test_property_58_concurrent_request_processing(num_requests, concurrency_limit):
    """
    Feature: api-model-management
    Property 58: Concurrent request processing
    
    For any N concurrent requests where N is less than the concurrency limit,
    all N requests should be processed in parallel.
    
    Validates: Requirements 14.2
    """
    # Only test when num_requests < concurrency_limit
    if num_requests >= concurrency_limit:
        num_requests = concurrency_limit - 1
    
    # Create client with specified concurrency limit
    api_client, mock_adapter = create_api_client(
        max_concurrent=concurrency_limit,
        per_provider_limits={"test_provider": concurrency_limit}
    )
    
    # Track concurrent executions
    concurrent_count = 0
    max_concurrent = 0
    execution_times = []
    
    async def track_concurrent_request(*args, **kwargs):
        nonlocal concurrent_count, max_concurrent
        concurrent_count += 1
        max_concurrent = max(max_concurrent, concurrent_count)
        start_time = asyncio.get_event_loop().time()
        
        # Simulate request processing
        await asyncio.sleep(0.05)
        
        concurrent_count -= 1
        end_time = asyncio.get_event_loop().time()
        execution_times.append((start_time, end_time))
        
        return ModelResponse(
            content="Success",
            model_id="test_model",
            token_usage=TokenUsage(input_tokens=10, output_tokens=20, total_tokens=30),
            latency_ms=50.0,
            cost=0.0
        )
    
    mock_adapter.send_request.side_effect = track_concurrent_request
    
    # Create requests
    requests = [
        ModelRequest(
            prompt=f"Test {i}",
            parameters={},
            task_id=f"task_{i}",
            agent_type="test"
        )
        for i in range(num_requests)
    ]
    
    # Execute all requests concurrently
    start_time = asyncio.get_event_loop().time()
    tasks = [api_client.send_request("test_model", req) for req in requests]
    results = await asyncio.gather(*tasks)
    total_time = asyncio.get_event_loop().time() - start_time
    
    # Verify: All requests completed successfully
    assert len(results) == num_requests
    assert all(r.content == "Success" for r in results)
    
    # Verify: All requests ran in parallel (max_concurrent should equal num_requests)
    # Since num_requests < concurrency_limit, all should run concurrently
    assert max_concurrent == num_requests, (
        f"Expected {num_requests} concurrent requests, but got {max_concurrent}"
    )
    
    # Verify: Total time should be close to single request time (not sum of all)
    # If truly parallel, total time ≈ single request time (0.05s)
    # Allow some overhead for scheduling
    assert total_time < 0.15, (
        f"Requests should run in parallel. Expected ~0.05s, got {total_time:.3f}s"
    )


# Property 59: Non-blocking request handling
@settings(max_examples=5, deadline=10000)
@given(
    num_fast_requests=st.integers(min_value=3, max_value=10),
    num_slow_requests=st.integers(min_value=1, max_value=3)
)
@pytest.mark.asyncio
async def test_property_59_non_blocking_request_handling(num_fast_requests, num_slow_requests):
    """
    Feature: api-model-management
    Property 59: Non-blocking request handling
    
    For any slow request, other pending requests should continue processing
    without being blocked.
    
    Validates: Requirements 14.4
    """
    # Create client with sufficient concurrency
    api_client, mock_adapter = create_api_client(
        max_concurrent=20,
        per_provider_limits={"test_provider": 20}
    )
    
    # Track request completion order
    completion_order = []
    
    async def variable_speed_request(model_id, request, api_key):
        # Slow requests have "slow" in task_id
        if "slow" in request.task_id:
            await asyncio.sleep(0.2)  # Slow request
        else:
            await asyncio.sleep(0.02)  # Fast request
        
        completion_order.append(request.task_id)
        
        return ModelResponse(
            content="Success",
            model_id="test_model",
            token_usage=TokenUsage(input_tokens=10, output_tokens=20, total_tokens=30),
            latency_ms=100.0,
            cost=0.0
        )
    
    mock_adapter.send_request.side_effect = variable_speed_request
    
    # Create mix of slow and fast requests
    # Submit slow requests first, then fast requests
    slow_requests = [
        ModelRequest(
            prompt=f"Slow {i}",
            parameters={},
            task_id=f"slow_task_{i}",
            agent_type="test"
        )
        for i in range(num_slow_requests)
    ]
    
    fast_requests = [
        ModelRequest(
            prompt=f"Fast {i}",
            parameters={},
            task_id=f"fast_task_{i}",
            agent_type="test"
        )
        for i in range(num_fast_requests)
    ]
    
    # Submit slow requests first, then fast requests immediately after
    tasks = []
    for req in slow_requests:
        tasks.append(api_client.send_request("test_model", req))
    
    # Small delay to ensure slow requests start first
    await asyncio.sleep(0.01)
    
    for req in fast_requests:
        tasks.append(api_client.send_request("test_model", req))
    
    # Wait for all to complete
    results = await asyncio.gather(*tasks)
    
    # Verify: All requests completed
    assert len(results) == num_slow_requests + num_fast_requests
    
    # Verify: Fast requests completed before slow requests
    # At least some fast requests should complete before slow requests finish
    fast_completions = [i for i, task_id in enumerate(completion_order) if "fast" in task_id]
    slow_completions = [i for i, task_id in enumerate(completion_order) if "slow" in task_id]
    
    # At least one fast request should complete before the last slow request
    if fast_completions and slow_completions:
        first_fast_completion = min(fast_completions)
        last_slow_completion = max(slow_completions)
        assert first_fast_completion < last_slow_completion, (
            "Fast requests should complete before slow requests, indicating non-blocking behavior"
        )


# Property 60: Concurrency limit enforcement
@settings(max_examples=5, deadline=10000)
@given(
    num_requests=st.integers(min_value=10, max_value=30),
    provider_limit=st.integers(min_value=3, max_value=8)
)
@pytest.mark.asyncio
async def test_property_60_concurrency_limit_enforcement(num_requests, provider_limit):
    """
    Feature: api-model-management
    Property 60: Concurrency limit enforcement
    
    For any provider with a configured concurrency limit of N, no more than N
    requests should be in-flight simultaneously.
    
    Validates: Requirements 14.5
    """
    # Create client with specific provider limit
    api_client, mock_adapter = create_api_client(
        max_concurrent=100,  # High global limit
        per_provider_limits={"test_provider": provider_limit}
    )
    
    # Track concurrent executions
    concurrent_count = 0
    max_concurrent = 0
    concurrent_samples = []
    
    async def track_concurrent_request(*args, **kwargs):
        nonlocal concurrent_count, max_concurrent
        concurrent_count += 1
        max_concurrent = max(max_concurrent, concurrent_count)
        concurrent_samples.append(concurrent_count)
        
        # Simulate request processing
        await asyncio.sleep(0.05)
        
        concurrent_count -= 1
        
        return ModelResponse(
            content="Success",
            model_id="test_model",
            token_usage=TokenUsage(input_tokens=10, output_tokens=20, total_tokens=30),
            latency_ms=50.0,
            cost=0.0
        )
    
    mock_adapter.send_request.side_effect = track_concurrent_request
    
    # Create more requests than the limit
    requests = [
        ModelRequest(
            prompt=f"Test {i}",
            parameters={},
            task_id=f"task_{i}",
            agent_type="test"
        )
        for i in range(num_requests)
    ]
    
    # Execute all requests concurrently
    tasks = [api_client.send_request("test_model", req) for req in requests]
    results = await asyncio.gather(*tasks)
    
    # Verify: All requests completed successfully
    assert len(results) == num_requests
    assert all(r.content == "Success" for r in results)
    
    # Verify: Max concurrent never exceeded provider limit
    assert max_concurrent <= provider_limit, (
        f"Concurrency limit violated: max_concurrent={max_concurrent}, "
        f"limit={provider_limit}"
    )
    
    # Verify: All concurrent samples respect the limit
    assert all(count <= provider_limit for count in concurrent_samples), (
        f"Some concurrent counts exceeded limit: {concurrent_samples}"
    )
    
    # Verify: Concurrency status reflects the limit
    status = api_client.get_concurrency_status()
    assert status["providers"]["test_provider"]["limit"] == provider_limit


# Additional property test: Multiple providers with different limits
@settings(max_examples=5, deadline=10000)
@given(
    num_requests_per_provider=st.integers(min_value=5, max_value=15),
    provider1_limit=st.integers(min_value=3, max_value=8),
    provider2_limit=st.integers(min_value=3, max_value=8)
)
@pytest.mark.asyncio
async def test_multiple_providers_independent_limits(
    num_requests_per_provider,
    provider1_limit,
    provider2_limit
):
    """
    Verify that different providers have independent concurrency limits.
    """
    # Create registries for two providers
    registry = Mock(spec=ModelRegistry)
    
    model1 = ModelMetadata(
        id="model1",
        provider="provider1",
        name="Model 1",
        capabilities=["text-generation"],
        cost_per_1k_input_tokens=0.01,
        cost_per_1k_output_tokens=0.03,
        rate_limits=RateLimits(requests_per_minute=100, tokens_per_minute=10000),
        context_window=4096,
        average_response_time_ms=1000.0,
        enabled=True
    )
    
    model2 = ModelMetadata(
        id="model2",
        provider="provider2",
        name="Model 2",
        capabilities=["text-generation"],
        cost_per_1k_input_tokens=0.01,
        cost_per_1k_output_tokens=0.03,
        rate_limits=RateLimits(requests_per_minute=100, tokens_per_minute=10000),
        context_window=4096,
        average_response_time_ms=1000.0,
        enabled=True
    )
    
    def get_model_side_effect(model_id):
        if model_id == "model1":
            return model1
        elif model_id == "model2":
            return model2
        return None
    
    registry.get_model.side_effect = get_model_side_effect
    
    # Create adapters for both providers
    adapter1 = create_mock_adapter()
    adapter2 = create_mock_adapter()
    
    # Track concurrent executions per provider
    provider1_concurrent = 0
    provider1_max = 0
    provider2_concurrent = 0
    provider2_max = 0
    
    async def track_provider1_request(*args, **kwargs):
        nonlocal provider1_concurrent, provider1_max
        provider1_concurrent += 1
        provider1_max = max(provider1_max, provider1_concurrent)
        await asyncio.sleep(0.05)
        provider1_concurrent -= 1
        return ModelResponse(
            content="Success",
            model_id="model1",
            token_usage=TokenUsage(input_tokens=10, output_tokens=20, total_tokens=30),
            latency_ms=50.0,
            cost=0.0
        )
    
    async def track_provider2_request(*args, **kwargs):
        nonlocal provider2_concurrent, provider2_max
        provider2_concurrent += 1
        provider2_max = max(provider2_max, provider2_concurrent)
        await asyncio.sleep(0.05)
        provider2_concurrent -= 1
        return ModelResponse(
            content="Success",
            model_id="model2",
            token_usage=TokenUsage(input_tokens=10, output_tokens=20, total_tokens=30),
            latency_ms=50.0,
            cost=0.0
        )
    
    adapter1.send_request.side_effect = track_provider1_request
    adapter2.send_request.side_effect = track_provider2_request
    
    # Create client with different limits per provider
    api_client = APIClientManager(
        api_key_manager=create_mock_api_key_manager(),
        registry=registry,
        adapters={"provider1": adapter1, "provider2": adapter2},
        max_concurrent_requests=100,
        max_concurrent_per_provider={
            "provider1": provider1_limit,
            "provider2": provider2_limit
        }
    )
    
    # Create requests for both providers
    requests1 = [
        ModelRequest(
            prompt=f"Test {i}",
            parameters={},
            task_id=f"task1_{i}",
            agent_type="test"
        )
        for i in range(num_requests_per_provider)
    ]
    
    requests2 = [
        ModelRequest(
            prompt=f"Test {i}",
            parameters={},
            task_id=f"task2_{i}",
            agent_type="test"
        )
        for i in range(num_requests_per_provider)
    ]
    
    # Execute all requests concurrently
    tasks = []
    for req in requests1:
        tasks.append(api_client.send_request("model1", req))
    for req in requests2:
        tasks.append(api_client.send_request("model2", req))
    
    results = await asyncio.gather(*tasks)
    
    # Verify: All requests completed
    assert len(results) == num_requests_per_provider * 2
    
    # Verify: Each provider respected its own limit
    assert provider1_max <= provider1_limit, (
        f"Provider1 limit violated: max={provider1_max}, limit={provider1_limit}"
    )
    assert provider2_max <= provider2_limit, (
        f"Provider2 limit violated: max={provider2_max}, limit={provider2_limit}"
    )
