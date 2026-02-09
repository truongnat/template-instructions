"""
Unit tests for API Client Manager.

Tests specific examples, edge cases, and integration points for the
APIClientManager class.
"""

import pytest
import asyncio
from unittest.mock import AsyncMock, Mock, patch
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


@pytest.fixture
def mock_registry():
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


@pytest.fixture
def mock_api_key_manager():
    """Create a mock API key manager."""
    manager = Mock(spec=APIKeyManager)
    manager.get_key.return_value = "test_api_key"
    return manager


@pytest.fixture
def mock_adapter():
    """Create a mock provider adapter."""
    adapter = AsyncMock(spec=ProviderAdapter)
    adapter.calculate_cost.return_value = 0.05
    return adapter


@pytest.fixture
def api_client(mock_registry, mock_api_key_manager, mock_adapter):
    """Create API client with mocked dependencies."""
    adapters = {"test_provider": mock_adapter}
    return APIClientManager(
        api_key_manager=mock_api_key_manager,
        registry=mock_registry,
        adapters=adapters,
        max_retries=3,
        base_backoff_seconds=0.1  # Short backoff for tests
    )


@pytest.fixture
def sample_request():
    """Create a sample model request."""
    return ModelRequest(
        prompt="Test prompt",
        parameters={},
        task_id="test_task_123",
        agent_type="test"
    )


@pytest.fixture
def sample_response():
    """Create a sample model response."""
    return ModelResponse(
        content="Test response",
        model_id="test_model",
        token_usage=TokenUsage(input_tokens=10, output_tokens=20, total_tokens=30),
        latency_ms=100.0,
        cost=0.0
    )


class TestAPIClientManagerBasics:
    """Test basic API client functionality."""
    
    def test_initialization(self, mock_registry, mock_api_key_manager, mock_adapter):
        """Test API client initialization."""
        adapters = {"test_provider": mock_adapter}
        client = APIClientManager(
            api_key_manager=mock_api_key_manager,
            registry=mock_registry,
            adapters=adapters,
            max_retries=5,
            base_backoff_seconds=2.0,
            max_concurrent_requests=50
        )
        
        assert client.max_retries == 5
        assert client.base_backoff_seconds == 2.0
        assert client._request_count == 0
        assert client._error_count == 0
    
    def test_get_statistics(self, api_client):
        """Test statistics retrieval."""
        stats = api_client.get_statistics()
        
        assert "request_count" in stats
        assert "error_count" in stats
        assert "success_count" in stats
        assert stats["request_count"] == 0
        assert stats["error_count"] == 0


class TestSendRequest:
    """Test send_request method."""
    
    @pytest.mark.asyncio
    async def test_successful_request(
        self,
        api_client,
        mock_adapter,
        sample_request,
        sample_response
    ):
        """Test successful API request."""
        mock_adapter.send_request.return_value = sample_response
        
        result = await api_client.send_request("test_model", sample_request)
        
        assert result.content == "Test response"
        assert result.cost == 0.05  # From mock adapter calculate_cost
        mock_adapter.send_request.assert_called_once()
        mock_adapter.calculate_cost.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_model_not_found(self, api_client, mock_registry, sample_request):
        """Test request with model not in registry."""
        mock_registry.get_model.return_value = None
        
        with pytest.raises(ModelUnavailableError) as exc_info:
            await api_client.send_request("unknown_model", sample_request)
        
        assert "not found in registry" in str(exc_info.value)
        assert exc_info.value.model_id == "unknown_model"
    
    @pytest.mark.asyncio
    async def test_adapter_not_found(
        self,
        mock_registry,
        mock_api_key_manager,
        sample_request
    ):
        """Test request with no adapter for provider."""
        # Create client with empty adapters
        client = APIClientManager(
            api_key_manager=mock_api_key_manager,
            registry=mock_registry,
            adapters={},  # No adapters
            max_retries=3
        )
        
        with pytest.raises(ProviderError) as exc_info:
            await client.send_request("test_model", sample_request)
        
        assert "No adapter found" in str(exc_info.value)
    
    @pytest.mark.asyncio
    async def test_missing_api_key(
        self,
        api_client,
        mock_api_key_manager,
        sample_request
    ):
        """Test request with missing API key."""
        mock_api_key_manager.get_key.return_value = None
        
        with pytest.raises(AuthenticationError) as exc_info:
            await api_client.send_request("test_model", sample_request)
        
        assert "No API key available" in str(exc_info.value)
    
    @pytest.mark.asyncio
    async def test_ollama_no_api_key_required(
        self,
        mock_registry,
        mock_api_key_manager,
        sample_request,
        sample_response
    ):
        """Test that Ollama doesn't require API key."""
        # Setup Ollama model
        ollama_model = ModelMetadata(
            id="llama2",
            provider="ollama",
            name="Llama 2",
            capabilities=["text-generation"],
            cost_per_1k_input_tokens=0.0,
            cost_per_1k_output_tokens=0.0,
            rate_limits=RateLimits(requests_per_minute=100, tokens_per_minute=10000),
            context_window=4096,
            average_response_time_ms=1000.0,
            enabled=True
        )
        mock_registry.get_model.return_value = ollama_model
        
        # Mock adapter for Ollama
        ollama_adapter = AsyncMock(spec=ProviderAdapter)
        ollama_adapter.send_request.return_value = sample_response
        ollama_adapter.calculate_cost.return_value = 0.0
        
        # Create client with Ollama adapter
        client = APIClientManager(
            api_key_manager=mock_api_key_manager,
            registry=mock_registry,
            adapters={"ollama": ollama_adapter},
            max_retries=3
        )
        
        # Should not raise even with no API key
        mock_api_key_manager.get_key.return_value = None
        result = await client.send_request("llama2", sample_request)
        
        assert result.content == "Test response"


class TestRetryLogic:
    """Test retry logic with mock failures."""
    
    @pytest.mark.asyncio
    async def test_retry_on_timeout(
        self,
        api_client,
        mock_adapter,
        sample_request,
        sample_response
    ):
        """Test retry on timeout error."""
        # Fail twice, then succeed
        mock_adapter.send_request.side_effect = [
            httpx.TimeoutException("Timeout"),
            httpx.TimeoutException("Timeout"),
            sample_response
        ]
        
        result = await api_client.send_request_with_retry("test_model", sample_request)
        
        assert result.content == "Test response"
        assert mock_adapter.send_request.call_count == 3
    
    @pytest.mark.asyncio
    async def test_retry_on_5xx_error(
        self,
        api_client,
        mock_adapter,
        sample_request,
        sample_response
    ):
        """Test retry on 5xx server error."""
        # Fail once with 500, then succeed
        error = ProviderError(
            "Server error",
            provider="test_provider",
            model_id="test_model",
            status_code=500,
            is_retryable=True,
            task_id="test_task_123"
        )
        mock_adapter.send_request.side_effect = [error, sample_response]
        
        result = await api_client.send_request_with_retry("test_model", sample_request)
        
        assert result.content == "Test response"
        assert mock_adapter.send_request.call_count == 2
    
    @pytest.mark.asyncio
    async def test_no_retry_on_auth_error(
        self,
        api_client,
        mock_adapter,
        sample_request
    ):
        """Test no retry on authentication error."""
        error = AuthenticationError(
            "Auth failed",
            provider="test_provider",
            model_id="test_model",
            task_id="test_task_123"
        )
        mock_adapter.send_request.side_effect = error
        
        with pytest.raises(AuthenticationError):
            await api_client.send_request_with_retry("test_model", sample_request)
        
        # Should only try once (no retries)
        assert mock_adapter.send_request.call_count == 1
    
    @pytest.mark.asyncio
    async def test_max_retries_exceeded(
        self,
        api_client,
        mock_adapter,
        sample_request
    ):
        """Test max retries exceeded."""
        # Always fail with retryable error
        error = httpx.TimeoutException("Timeout")
        mock_adapter.send_request.side_effect = error
        
        with pytest.raises(ProviderError) as exc_info:
            await api_client.send_request_with_retry("test_model", sample_request)
        
        # Should try max_retries + 1 times (initial + 3 retries = 4 total)
        assert mock_adapter.send_request.call_count == 4
        assert "failed after 4 attempts" in str(exc_info.value)
    
    @pytest.mark.asyncio
    async def test_exponential_backoff_timing(
        self,
        api_client,
        mock_adapter,
        sample_request,
        sample_response
    ):
        """Test exponential backoff timing."""
        # Fail twice, then succeed
        mock_adapter.send_request.side_effect = [
            httpx.TimeoutException("Timeout"),
            httpx.TimeoutException("Timeout"),
            sample_response
        ]
        
        start_time = asyncio.get_event_loop().time()
        result = await api_client.send_request_with_retry("test_model", sample_request)
        elapsed = asyncio.get_event_loop().time() - start_time
        
        # Expected delays: 0.1 * 2^0 + 0.1 * 2^1 = 0.1 + 0.2 = 0.3 seconds
        assert elapsed >= 0.25  # Allow some tolerance
        assert result.content == "Test response"


class TestErrorCategorization:
    """Test error categorization logic."""
    
    def test_transient_errors(self, api_client):
        """Test transient error identification."""
        transient_errors = [
            httpx.TimeoutException("Timeout"),
            httpx.NetworkError("Network error"),
            httpx.ConnectError("Connection failed"),
            ProviderError("Server error", provider="test", model_id="test", status_code=500, is_retryable=True),
            ProviderError("Rate limit", provider="test", model_id="test", status_code=429, is_retryable=True),
            RateLimitError("Rate limit", model_id="test", task_id="test")
        ]
        
        for error in transient_errors:
            assert api_client._is_retryable_error(error), \
                f"{type(error).__name__} should be retryable"
    
    def test_permanent_errors(self, api_client):
        """Test permanent error identification."""
        permanent_errors = [
            AuthenticationError("Auth failed", provider="test", model_id="test", task_id="test"),
            InvalidRequestError("Invalid", model_id="test", task_id="test"),
            ModelUnavailableError("Unavailable", model_id="test", task_id="test"),
            ProviderError("Bad request", provider="test", model_id="test", status_code=400, is_retryable=False),
            ProviderError("Not found", provider="test", model_id="test", status_code=404, is_retryable=False)
        ]
        
        for error in permanent_errors:
            assert not api_client._is_retryable_error(error), \
                f"{type(error).__name__} should not be retryable"
    
    def test_backoff_calculation(self, api_client):
        """Test exponential backoff calculation."""
        assert api_client._calculate_backoff(0) == 0.1  # 2^0 * 0.1
        assert api_client._calculate_backoff(1) == 0.2  # 2^1 * 0.1
        assert api_client._calculate_backoff(2) == 0.4  # 2^2 * 0.1
        assert api_client._calculate_backoff(3) == 0.8  # 2^3 * 0.1


class TestAdapterRouting:
    """Test adapter routing logic."""
    
    @pytest.mark.asyncio
    async def test_correct_adapter_selected(
        self,
        mock_registry,
        mock_api_key_manager,
        sample_request,
        sample_response
    ):
        """Test that correct adapter is selected based on provider."""
        # Create multiple adapters
        openai_adapter = AsyncMock(spec=ProviderAdapter)
        anthropic_adapter = AsyncMock(spec=ProviderAdapter)
        
        openai_adapter.send_request.return_value = sample_response
        openai_adapter.calculate_cost.return_value = 0.05
        
        # Setup OpenAI model
        openai_model = ModelMetadata(
            id="gpt-4",
            provider="openai",
            name="GPT-4",
            capabilities=["text-generation"],
            cost_per_1k_input_tokens=0.03,
            cost_per_1k_output_tokens=0.06,
            rate_limits=RateLimits(requests_per_minute=100, tokens_per_minute=10000),
            context_window=8192,
            average_response_time_ms=2000.0,
            enabled=True
        )
        mock_registry.get_model.return_value = openai_model
        
        # Create client with multiple adapters
        client = APIClientManager(
            api_key_manager=mock_api_key_manager,
            registry=mock_registry,
            adapters={
                "openai": openai_adapter,
                "anthropic": anthropic_adapter
            },
            max_retries=3
        )
        
        result = await client.send_request("gpt-4", sample_request)
        
        # Verify OpenAI adapter was called, not Anthropic
        openai_adapter.send_request.assert_called_once()
        anthropic_adapter.send_request.assert_not_called()
        assert result.content == "Test response"


class TestConcurrency:
    """Test concurrent request handling."""
    
    @pytest.mark.asyncio
    async def test_concurrent_requests(
        self,
        mock_registry,
        mock_api_key_manager,
        mock_adapter,
        sample_response
    ):
        """Test multiple concurrent requests."""
        mock_adapter.send_request.return_value = sample_response
        
        client = APIClientManager(
            api_key_manager=mock_api_key_manager,
            registry=mock_registry,
            adapters={"test_provider": mock_adapter},
            max_concurrent_requests=10
        )
        
        # Create 5 concurrent requests
        requests = [
            ModelRequest(
                prompt=f"Test {i}",
                parameters={},
                task_id=f"task_{i}",
                agent_type="test"
            )
            for i in range(5)
        ]
        
        # Execute concurrently
        results = await asyncio.gather(*[
            client.send_request("test_model", req)
            for req in requests
        ])
        
        assert len(results) == 5
        assert all(r.content == "Test response" for r in results)
        assert mock_adapter.send_request.call_count == 5
    
    @pytest.mark.asyncio
    async def test_concurrent_request_timing(
        self,
        mock_registry,
        mock_api_key_manager,
        sample_response
    ):
        """Test that concurrent requests execute in parallel, not sequentially."""
        # Create adapter with delay to simulate API latency
        mock_adapter = AsyncMock(spec=ProviderAdapter)
        
        async def delayed_request(*args, **kwargs):
            await asyncio.sleep(0.1)  # 100ms delay
            return sample_response
        
        mock_adapter.send_request.side_effect = delayed_request
        mock_adapter.calculate_cost.return_value = 0.05
        
        client = APIClientManager(
            api_key_manager=mock_api_key_manager,
            registry=mock_registry,
            adapters={"test_provider": mock_adapter},
            max_concurrent_requests=10
        )
        
        # Create 5 concurrent requests
        requests = [
            ModelRequest(
                prompt=f"Test {i}",
                parameters={},
                task_id=f"task_{i}",
                agent_type="test"
            )
            for i in range(5)
        ]
        
        # Execute concurrently and measure time
        start_time = asyncio.get_event_loop().time()
        results = await asyncio.gather(*[
            client.send_request("test_model", req)
            for req in requests
        ])
        elapsed = asyncio.get_event_loop().time() - start_time
        
        # Verify all completed
        assert len(results) == 5
        
        # If truly parallel, should take ~0.1s (not 0.5s sequential)
        # Allow some overhead for scheduling
        assert elapsed < 0.25, (
            f"Requests should run in parallel. Expected ~0.1s, got {elapsed:.3f}s"
        )
    
    @pytest.mark.asyncio
    async def test_concurrency_limit_enforcement(
        self,
        mock_registry,
        mock_api_key_manager,
        sample_response
    ):
        """Test that concurrency limit is enforced per provider."""
        # Track concurrent executions
        concurrent_count = 0
        max_concurrent = 0
        
        mock_adapter = AsyncMock(spec=ProviderAdapter)
        
        async def track_concurrent_request(*args, **kwargs):
            nonlocal concurrent_count, max_concurrent
            concurrent_count += 1
            max_concurrent = max(max_concurrent, concurrent_count)
            
            await asyncio.sleep(0.05)  # Simulate processing
            
            concurrent_count -= 1
            return sample_response
        
        mock_adapter.send_request.side_effect = track_concurrent_request
        mock_adapter.calculate_cost.return_value = 0.05
        
        # Create client with low concurrency limit
        provider_limit = 3
        client = APIClientManager(
            api_key_manager=mock_api_key_manager,
            registry=mock_registry,
            adapters={"test_provider": mock_adapter},
            max_concurrent_requests=100,  # High global limit
            max_concurrent_per_provider={"test_provider": provider_limit}
        )
        
        # Create more requests than the limit
        requests = [
            ModelRequest(
                prompt=f"Test {i}",
                parameters={},
                task_id=f"task_{i}",
                agent_type="test"
            )
            for i in range(10)
        ]
        
        # Execute concurrently
        results = await asyncio.gather(*[
            client.send_request("test_model", req)
            for req in requests
        ])
        
        # Verify all completed
        assert len(results) == 10
        
        # Verify concurrency limit was enforced
        assert max_concurrent <= provider_limit, (
            f"Concurrency limit violated: max_concurrent={max_concurrent}, "
            f"limit={provider_limit}"
        )
    
    @pytest.mark.asyncio
    async def test_global_concurrency_limit(
        self,
        mock_registry,
        mock_api_key_manager,
        sample_response
    ):
        """Test that global concurrency limit is enforced across all providers."""
        # Track concurrent executions across all providers
        total_concurrent = 0
        max_total_concurrent = 0
        
        # Create two adapters
        adapter1 = AsyncMock(spec=ProviderAdapter)
        adapter2 = AsyncMock(spec=ProviderAdapter)
        
        async def track_concurrent_request(*args, **kwargs):
            nonlocal total_concurrent, max_total_concurrent
            total_concurrent += 1
            max_total_concurrent = max(max_total_concurrent, total_concurrent)
            
            await asyncio.sleep(0.05)
            
            total_concurrent -= 1
            return sample_response
        
        adapter1.send_request.side_effect = track_concurrent_request
        adapter1.calculate_cost.return_value = 0.05
        adapter2.send_request.side_effect = track_concurrent_request
        adapter2.calculate_cost.return_value = 0.05
        
        # Setup two models with different providers
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
        
        mock_registry.get_model.side_effect = get_model_side_effect
        
        # Create client with low global limit
        global_limit = 5
        client = APIClientManager(
            api_key_manager=mock_api_key_manager,
            registry=mock_registry,
            adapters={"provider1": adapter1, "provider2": adapter2},
            max_concurrent_requests=global_limit,
            max_concurrent_per_provider={"provider1": 10, "provider2": 10}  # High per-provider limits
        )
        
        # Create requests for both providers
        requests = []
        for i in range(5):
            requests.append(("model1", ModelRequest(
                prompt=f"Test {i}",
                parameters={},
                task_id=f"task1_{i}",
                agent_type="test"
            )))
        for i in range(5):
            requests.append(("model2", ModelRequest(
                prompt=f"Test {i}",
                parameters={},
                task_id=f"task2_{i}",
                agent_type="test"
            )))
        
        # Execute concurrently
        results = await asyncio.gather(*[
            client.send_request(model_id, req)
            for model_id, req in requests
        ])
        
        # Verify all completed
        assert len(results) == 10
        
        # Verify global limit was enforced
        assert max_total_concurrent <= global_limit, (
            f"Global concurrency limit violated: max_concurrent={max_total_concurrent}, "
            f"limit={global_limit}"
        )
    
    @pytest.mark.asyncio
    async def test_non_blocking_behavior(
        self,
        mock_registry,
        mock_api_key_manager,
        sample_response
    ):
        """Test that slow requests don't block fast requests."""
        completion_order = []
        
        mock_adapter = AsyncMock(spec=ProviderAdapter)
        
        async def variable_speed_request(model_id, request, api_key):
            # Slow requests have "slow" in task_id
            if "slow" in request.task_id:
                await asyncio.sleep(0.2)
            else:
                await asyncio.sleep(0.02)
            
            completion_order.append(request.task_id)
            return sample_response
        
        mock_adapter.send_request.side_effect = variable_speed_request
        mock_adapter.calculate_cost.return_value = 0.05
        
        client = APIClientManager(
            api_key_manager=mock_api_key_manager,
            registry=mock_registry,
            adapters={"test_provider": mock_adapter},
            max_concurrent_requests=10
        )
        
        # Create mix of slow and fast requests
        # Submit slow requests first
        slow_requests = [
            ModelRequest(
                prompt=f"Slow {i}",
                parameters={},
                task_id=f"slow_task_{i}",
                agent_type="test"
            )
            for i in range(2)
        ]
        
        fast_requests = [
            ModelRequest(
                prompt=f"Fast {i}",
                parameters={},
                task_id=f"fast_task_{i}",
                agent_type="test"
            )
            for i in range(5)
        ]
        
        # Submit slow requests first, then fast requests
        tasks = []
        for req in slow_requests:
            tasks.append(client.send_request("test_model", req))
        
        # Small delay to ensure slow requests start first
        await asyncio.sleep(0.01)
        
        for req in fast_requests:
            tasks.append(client.send_request("test_model", req))
        
        # Wait for all to complete
        results = await asyncio.gather(*tasks)
        
        # Verify all completed
        assert len(results) == 7
        
        # Verify fast requests completed before slow requests
        fast_completions = [i for i, task_id in enumerate(completion_order) if "fast" in task_id]
        slow_completions = [i for i, task_id in enumerate(completion_order) if "slow" in task_id]
        
        # At least one fast request should complete before the last slow request
        if fast_completions and slow_completions:
            first_fast_completion = min(fast_completions)
            last_slow_completion = max(slow_completions)
            assert first_fast_completion < last_slow_completion, (
                "Fast requests should complete before slow requests, indicating non-blocking behavior"
            )
    
    @pytest.mark.asyncio
    async def test_concurrency_status_reporting(
        self,
        mock_registry,
        mock_api_key_manager,
        mock_adapter
    ):
        """Test that concurrency status is accurately reported."""
        client = APIClientManager(
            api_key_manager=mock_api_key_manager,
            registry=mock_registry,
            adapters={"test_provider": mock_adapter},
            max_concurrent_requests=50,
            max_concurrent_per_provider={"test_provider": 10}
        )
        
        # Get initial status
        status = client.get_concurrency_status()
        
        # Verify structure
        assert "global_limit" in status
        assert "providers" in status
        assert "test_provider" in status["providers"]
        
        # Verify provider status
        provider_status = status["providers"]["test_provider"]
        assert "active_requests" in provider_status
        assert "limit" in provider_status
        assert "available_slots" in provider_status
        
        # Verify initial values
        assert provider_status["active_requests"] == 0
        assert provider_status["limit"] == 10
        assert provider_status["available_slots"] == 10
    
    @pytest.mark.asyncio
    async def test_independent_provider_limits(
        self,
        mock_registry,
        mock_api_key_manager,
        sample_response
    ):
        """Test that different providers have independent concurrency limits."""
        # Track concurrent executions per provider
        provider1_concurrent = 0
        provider1_max = 0
        provider2_concurrent = 0
        provider2_max = 0
        
        adapter1 = AsyncMock(spec=ProviderAdapter)
        adapter2 = AsyncMock(spec=ProviderAdapter)
        
        async def track_provider1_request(*args, **kwargs):
            nonlocal provider1_concurrent, provider1_max
            provider1_concurrent += 1
            provider1_max = max(provider1_max, provider1_concurrent)
            await asyncio.sleep(0.05)
            provider1_concurrent -= 1
            return sample_response
        
        async def track_provider2_request(*args, **kwargs):
            nonlocal provider2_concurrent, provider2_max
            provider2_concurrent += 1
            provider2_max = max(provider2_max, provider2_concurrent)
            await asyncio.sleep(0.05)
            provider2_concurrent -= 1
            return sample_response
        
        adapter1.send_request.side_effect = track_provider1_request
        adapter1.calculate_cost.return_value = 0.05
        adapter2.send_request.side_effect = track_provider2_request
        adapter2.calculate_cost.return_value = 0.05
        
        # Setup two models
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
        
        mock_registry.get_model.side_effect = get_model_side_effect
        
        # Create client with different limits per provider
        provider1_limit = 3
        provider2_limit = 5
        client = APIClientManager(
            api_key_manager=mock_api_key_manager,
            registry=mock_registry,
            adapters={"provider1": adapter1, "provider2": adapter2},
            max_concurrent_requests=100,
            max_concurrent_per_provider={
                "provider1": provider1_limit,
                "provider2": provider2_limit
            }
        )
        
        # Create requests for both providers
        requests = []
        for i in range(8):
            requests.append(("model1", ModelRequest(
                prompt=f"Test {i}",
                parameters={},
                task_id=f"task1_{i}",
                agent_type="test"
            )))
        for i in range(8):
            requests.append(("model2", ModelRequest(
                prompt=f"Test {i}",
                parameters={},
                task_id=f"task2_{i}",
                agent_type="test"
            )))
        
        # Execute concurrently
        results = await asyncio.gather(*[
            client.send_request(model_id, req)
            for model_id, req in requests
        ])
        
        # Verify all completed
        assert len(results) == 16
        
        # Verify each provider respected its own limit
        assert provider1_max <= provider1_limit, (
            f"Provider1 limit violated: max={provider1_max}, limit={provider1_limit}"
        )
        assert provider2_max <= provider2_limit, (
            f"Provider2 limit violated: max={provider2_max}, limit={provider2_limit}"
        )
    
    @pytest.mark.asyncio
    async def test_concurrency_with_errors(
        self,
        mock_registry,
        mock_api_key_manager,
        sample_response
    ):
        """Test that errors in some requests don't block other concurrent requests."""
        mock_adapter = AsyncMock(spec=ProviderAdapter)
        
        # Create a list to track which requests should fail
        # Make requests with task_id containing "fail" raise errors
        async def mixed_results(model_id, request, api_key):
            await asyncio.sleep(0.05)
            
            # Requests with "fail" in task_id will fail
            if "fail" in request.task_id:
                raise ProviderError(
                    "Simulated error",
                    provider="test_provider",
                    model_id="test_model",
                    status_code=500,
                    is_retryable=False,
                    task_id=request.task_id
                )
            
            return sample_response
        
        mock_adapter.send_request.side_effect = mixed_results
        mock_adapter.calculate_cost.return_value = 0.05
        
        client = APIClientManager(
            api_key_manager=mock_api_key_manager,
            registry=mock_registry,
            adapters={"test_provider": mock_adapter},
            max_concurrent_requests=10
        )
        
        # Create 9 concurrent requests - 3 will fail, 6 will succeed
        requests = []
        for i in range(9):
            task_id = f"task_fail_{i}" if i % 3 == 0 else f"task_{i}"
            requests.append(ModelRequest(
                prompt=f"Test {i}",
                parameters={},
                task_id=task_id,
                agent_type="test"
            ))
        
        # Execute concurrently with gather(return_exceptions=True)
        results = await asyncio.gather(*[
            client.send_request("test_model", req)
            for req in requests
        ], return_exceptions=True)
        
        # Verify all completed (some with errors)
        assert len(results) == 9
        
        # Count successes and failures
        successes = [r for r in results if isinstance(r, ModelResponse)]
        failures = [r for r in results if isinstance(r, Exception)]
        
        # Should have 6 successes and 3 failures
        assert len(successes) == 6
        assert len(failures) == 3
        assert all(isinstance(f, ProviderError) for f in failures)


class TestCleanup:
    """Test cleanup and resource management."""
    
    @pytest.mark.asyncio
    async def test_close_adapters(
        self,
        mock_registry,
        mock_api_key_manager
    ):
        """Test closing all adapters."""
        # Create mock adapter with close method
        mock_adapter = AsyncMock(spec=ProviderAdapter)
        mock_adapter.close = AsyncMock()
        
        client = APIClientManager(
            api_key_manager=mock_api_key_manager,
            registry=mock_registry,
            adapters={"test_provider": mock_adapter},
            max_retries=3
        )
        
        await client.close()
        
        # Verify adapter close was called
        mock_adapter.close.assert_called_once()
