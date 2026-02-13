"""
Property-based tests for API Client Manager.

Feature: api-model-management
Tests Properties 28, 29, and 62 from the design document.
"""

import pytest
import asyncio
from datetime import datetime
from unittest.mock import AsyncMock, Mock, patch
from hypothesis import given, settings, strategies as st
import httpx

from agentic_sdlc.orchestration.api_model_management.api_client import APIClientManager
from agentic_sdlc.orchestration.api_model_management.models import (
    ModelRequest,
    ModelResponse,
    TokenUsage,
    ModelMetadata,
    RateLimits
)
from agentic_sdlc.orchestration.api_model_management.exceptions import (
    ProviderError,
    RateLimitError,
    AuthenticationError,
    InvalidRequestError,
    ModelUnavailableError
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


@st.composite
def transient_error_strategy(draw):
    """Generate transient (retryable) errors."""
    error_type = draw(st.sampled_from([
        "timeout",
        "5xx_error",
        "rate_limit",
        "network_error"
    ]))
    
    if error_type == "timeout":
        return httpx.TimeoutException("Request timeout")
    elif error_type == "5xx_error":
        return ProviderError(
            "Server error",
            provider="test_provider",
            model_id="test_model",
            status_code=draw(st.integers(min_value=500, max_value=599)),
            is_retryable=True,
            task_id="test_task"
        )
    elif error_type == "rate_limit":
        return RateLimitError(
            "Rate limit exceeded",
            model_id="test_model",
            retry_after=draw(st.integers(min_value=1, max_value=60)),
            task_id="test_task"
        )
    else:  # network_error
        return httpx.NetworkError("Network error")


@st.composite
def permanent_error_strategy(draw):
    """Generate permanent (non-retryable) errors."""
    error_type = draw(st.sampled_from([
        "auth_error",
        "invalid_request",
        "4xx_error",
        "model_unavailable"
    ]))
    
    if error_type == "auth_error":
        return AuthenticationError(
            "Authentication failed",
            provider="test_provider",
            model_id="test_model",
            task_id="test_task"
        )
    elif error_type == "invalid_request":
        return InvalidRequestError(
            "Invalid request",
            model_id="test_model",
            task_id="test_task"
        )
    elif error_type == "4xx_error":
        return ProviderError(
            "Client error",
            provider="test_provider",
            model_id="test_model",
            status_code=draw(st.integers(min_value=400, max_value=499).filter(lambda x: x != 429)),
            is_retryable=False,
            task_id="test_task"
        )
    else:  # model_unavailable
        return ModelUnavailableError(
            "Model unavailable",
            model_id="test_model",
            task_id="test_task"
        )


# Helper functions to create mocks (not fixtures to avoid hypothesis issues)
def create_mock_registry():
    """Create a mock registry with test model."""
    registry = Mock(spec=ModelRegistry)
    model_metadata = ModelMetadata(
        id="test_model",
        provider="test_provider",
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


def create_api_client():
    """Create API client with mocked dependencies."""
    mock_registry = create_mock_registry()
    mock_api_key_manager = create_mock_api_key_manager()
    mock_adapter = create_mock_adapter()
    adapters = {"test_provider": mock_adapter}
    client = APIClientManager(
        api_key_manager=mock_api_key_manager,
        registry=mock_registry,
        adapters=adapters,
        max_retries=3,
        base_backoff_seconds=0.1  # Short backoff for tests
    )
    return client, mock_adapter


# Property 28: Transient error retry with backoff
@settings(max_examples=5, deadline=5000)
@given(
    request=model_request_strategy(),
    error=transient_error_strategy(),
    num_failures=st.integers(min_value=1, max_value=3)
)
@pytest.mark.asyncio
async def test_property_28_transient_error_retry_with_backoff(request, error, num_failures):
    """
    Feature: api-model-management
    Property 28: Transient error retry with backoff
    
    For any request that fails with a transient error (timeout, 5xx),
    retries should occur with exponentially increasing delays up to max retries.
    
    Validates: Requirements 7.2
    """
    # Create fresh mocks for each test
    api_client, mock_adapter = create_api_client()
    
    # Setup: Mock adapter to fail num_failures times, then succeed
    success_response = ModelResponse(
        content="Success",
        model_id="test_model",
        token_usage=TokenUsage(input_tokens=10, output_tokens=20, total_tokens=30),
        latency_ms=100.0,
        cost=0.0
    )
    
    call_count = 0
    async def side_effect(*args, **kwargs):
        nonlocal call_count
        call_count += 1
        if call_count <= num_failures:
            raise error
        return success_response
    
    mock_adapter.send_request.side_effect = side_effect
    
    # Record start time
    start_time = asyncio.get_event_loop().time()
    
    # Execute
    try:
        result = await api_client.send_request_with_retry("test_model", request)
        
        # Verify: Should succeed after retries
        assert result.content == "Success"
        assert call_count == num_failures + 1
        
        # Verify: Exponential backoff occurred
        elapsed_time = asyncio.get_event_loop().time() - start_time
        # Expected minimum delay: sum of 2^0 * 0.1 + 2^1 * 0.1 + ... for num_failures attempts
        expected_min_delay = sum(0.1 * (2 ** i) for i in range(num_failures))
        assert elapsed_time >= expected_min_delay * 0.8  # Allow 20% tolerance
        
    except ProviderError:
        # If max retries exceeded, verify we tried the right number of times
        assert call_count == api_client.max_retries + 1


# Property 29: Final failure error details
@settings(max_examples=5, deadline=5000)
@given(
    request=model_request_strategy(),
    error=transient_error_strategy()
)
@pytest.mark.asyncio
async def test_property_29_final_failure_error_details(request, error):
    """
    Feature: api-model-management
    Property 29: Final failure error details
    
    For any request that fails after all retry attempts, the returned error
    should include the error type, all attempted models, and failure reasons.
    
    Validates: Requirements 7.3
    """
    # Create fresh mocks for each test
    api_client, mock_adapter = create_api_client()
    
    # Setup: Mock adapter to always fail
    mock_adapter.send_request.side_effect = error
    
    # Execute and verify
    with pytest.raises(ProviderError) as exc_info:
        await api_client.send_request_with_retry("test_model", request)
    
    # Verify error details
    final_error = exc_info.value
    assert final_error.model_id == "test_model"
    assert final_error.task_id == request.task_id
    assert "failed after" in str(final_error).lower()
    assert not final_error.is_retryable  # Final error should not be retryable


# Property 62: Error categorization
@settings(max_examples=5, deadline=2000)
@given(
    error_type=st.sampled_from(["transient", "permanent"])
)
@pytest.mark.asyncio
async def test_property_62_error_categorization(error_type):
    """
    Feature: api-model-management
    Property 62: Error categorization
    
    For any error, it should be correctly categorized as either transient
    (retryable) or permanent (non-retryable) based on error type.
    
    Validates: Requirements 15.2
    """
    # Create fresh client for each test
    api_client, _ = create_api_client()
    
    if error_type == "transient":
        # Test transient errors
        transient_errors = [
            httpx.TimeoutException("Timeout"),
            httpx.NetworkError("Network error"),
            ProviderError("Server error", provider="test", model_id="test", status_code=500, is_retryable=True),
            ProviderError("Rate limit", provider="test", model_id="test", status_code=429, is_retryable=True),
            RateLimitError("Rate limit", model_id="test", task_id="test")
        ]
        
        for error in transient_errors:
            is_retryable = api_client._is_retryable_error(error)
            assert is_retryable, f"Error {type(error).__name__} should be retryable"
    
    else:  # permanent
        # Test permanent errors
        permanent_errors = [
            AuthenticationError("Auth failed", provider="test", model_id="test", task_id="test"),
            InvalidRequestError("Invalid", model_id="test", task_id="test"),
            ModelUnavailableError("Unavailable", model_id="test", task_id="test"),
            ProviderError("Bad request", provider="test", model_id="test", status_code=400, is_retryable=False)
        ]
        
        for error in permanent_errors:
            is_retryable = api_client._is_retryable_error(error)
            assert not is_retryable, f"Error {type(error).__name__} should not be retryable"


# Additional property test: Exponential backoff calculation
@settings(max_examples=5)
@given(attempt=st.integers(min_value=0, max_value=10))
def test_exponential_backoff_calculation(attempt):
    """
    Verify exponential backoff calculation follows 2^n * base formula.
    """
    api_client, _ = create_api_client()
    delay = api_client._calculate_backoff(attempt)
    expected_delay = (2 ** attempt) * api_client.base_backoff_seconds
    assert delay == expected_delay


# Additional property test: Concurrent request limiting
@settings(max_examples=10, deadline=10000)
@given(num_requests=st.integers(min_value=1, max_value=20))
@pytest.mark.asyncio
async def test_concurrent_request_limiting(num_requests):
    """
    Verify that concurrent requests are limited by semaphore.
    """
    # Create client with low concurrency limit
    mock_registry = create_mock_registry()
    mock_api_key_manager = create_mock_api_key_manager()
    mock_adapter = create_mock_adapter()
    
    api_client = APIClientManager(
        api_key_manager=mock_api_key_manager,
        registry=mock_registry,
        adapters={"test_provider": mock_adapter},
        max_concurrent_requests=5
    )
    
    # Track concurrent executions
    concurrent_count = 0
    max_concurrent = 0
    
    async def slow_request(*args, **kwargs):
        nonlocal concurrent_count, max_concurrent
        concurrent_count += 1
        max_concurrent = max(max_concurrent, concurrent_count)
        await asyncio.sleep(0.01)  # Simulate slow request
        concurrent_count -= 1
        return ModelResponse(
            content="Success",
            model_id="test_model",
            token_usage=TokenUsage(input_tokens=10, output_tokens=20, total_tokens=30),
            latency_ms=100.0,
            cost=0.0
        )
    
    mock_adapter.send_request.side_effect = slow_request
    
    # Execute concurrent requests
    requests = [
        ModelRequest(
            prompt=f"Test {i}",
            parameters={},
            task_id=f"task_{i}",
            agent_type="test"
        )
        for i in range(num_requests)
    ]
    
    tasks = [api_client.send_request("test_model", req) for req in requests]
    await asyncio.gather(*tasks)
    
    # Verify: Max concurrent should not exceed limit
    assert max_concurrent <= 5
