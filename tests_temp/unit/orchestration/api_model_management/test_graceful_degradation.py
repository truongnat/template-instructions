"""
Unit tests for Graceful Degradation Manager.

Tests graceful degradation handling including provider failure isolation,
request queuing, cache failure fallback, and monitoring failure fallback.
"""

import pytest
import asyncio
from datetime import datetime, timedelta
from unittest.mock import Mock, AsyncMock, patch

from agentic_sdlc.orchestration.api_model_management.graceful_degradation import (
    GracefulDegradationManager,
    DegradationMode,
    DegradationStatus,
    QueuedRequest
)
from agentic_sdlc.orchestration.api_model_management.models import (
    ModelRequest,
    ModelResponse,
    TokenUsage
)
from agentic_sdlc.orchestration.api_model_management.exceptions import (
    CacheError,
    ProviderError
)


@pytest.fixture
def degradation_manager():
    """Create a graceful degradation manager for testing."""
    return GracefulDegradationManager(
        retry_interval_seconds=1,
        max_queue_size=10,
        queue_retry_base_delay=2
    )


@pytest.fixture
def sample_request():
    """Create a sample model request."""
    return ModelRequest(
        prompt="Test prompt",
        parameters={"temperature": 0.7},
        task_id="test-task-1",
        agent_type="test-agent"
    )


class TestProviderFailureIsolation:
    """Test provider failure isolation (Requirement 18.1)."""
    
    def test_mark_provider_failure_tracks_failures(self, degradation_manager):
        """Test that provider failures are tracked."""
        degradation_manager.mark_provider_failure("openai")
        
        assert degradation_manager.provider_failure_counts["openai"] == 1
        assert "openai" in degradation_manager.provider_last_failure
        
    def test_provider_marked_unavailable_after_threshold(self, degradation_manager):
        """Test that provider is marked unavailable after 3 failures."""
        # First two failures - should still be available
        degradation_manager.mark_provider_failure("openai")
        degradation_manager.mark_provider_failure("openai")
        assert degradation_manager.is_provider_available("openai") is True
        
        # Third failure - should be marked unavailable
        degradation_manager.mark_provider_failure("openai")
        assert degradation_manager.is_provider_available("openai") is False
        
    def test_provider_success_resets_failure_count(self, degradation_manager):
        """Test that successful request resets failure count."""
        degradation_manager.mark_provider_failure("openai")
        degradation_manager.mark_provider_failure("openai")
        
        degradation_manager.mark_provider_success("openai")
        
        assert degradation_manager.provider_failure_counts["openai"] == 0
        assert degradation_manager.is_provider_available("openai") is True
        
    def test_provider_recovery_after_unavailable(self, degradation_manager):
        """Test that provider can recover after being marked unavailable."""
        # Mark unavailable
        for _ in range(3):
            degradation_manager.mark_provider_failure("openai")
        assert degradation_manager.is_provider_available("openai") is False
        
        # Mark success - should recover
        degradation_manager.mark_provider_success("openai")
        assert degradation_manager.is_provider_available("openai") is True
        
    def test_get_available_providers_filters_unavailable(self, degradation_manager):
        """Test that get_available_providers returns only available providers."""
        all_providers = ["openai", "anthropic", "google"]
        
        # Mark openai as unavailable
        for _ in range(3):
            degradation_manager.mark_provider_failure("openai")
            
        available = degradation_manager.get_available_providers(all_providers)
        
        assert "openai" not in available
        assert "anthropic" in available
        assert "google" in available
        
    def test_multiple_providers_can_fail_independently(self, degradation_manager):
        """Test that multiple providers can fail independently."""
        # Fail openai
        for _ in range(3):
            degradation_manager.mark_provider_failure("openai")
            
        # Fail anthropic
        for _ in range(3):
            degradation_manager.mark_provider_failure("anthropic")
            
        assert degradation_manager.is_provider_available("openai") is False
        assert degradation_manager.is_provider_available("anthropic") is False
        assert degradation_manager.is_provider_available("google") is True


class TestRequestQueuing:
    """Test request queuing on total unavailability (Requirement 18.2)."""
    
    @pytest.mark.asyncio
    async def test_queue_request_adds_to_queue(self, degradation_manager, sample_request):
        """Test that requests can be queued."""
        result = await degradation_manager.queue_request(sample_request, "gpt-4")
        
        assert result is True
        assert len(degradation_manager.request_queue) == 1
        assert degradation_manager.request_queue[0].request == sample_request
        assert degradation_manager.request_queue[0].model_id == "gpt-4"
        
    @pytest.mark.asyncio
    async def test_queue_request_respects_max_size(self, degradation_manager, sample_request):
        """Test that queue respects maximum size."""
        # Fill queue to max
        for i in range(10):
            request = ModelRequest(
                prompt=f"Test {i}",
                parameters={},
                task_id=f"task-{i}",
                agent_type="test"
            )
            await degradation_manager.queue_request(request, "gpt-4")
            
        # Try to add one more - should fail
        result = await degradation_manager.queue_request(sample_request, "gpt-4")
        
        assert result is False
        assert len(degradation_manager.request_queue) == 10
        
    @pytest.mark.asyncio
    async def test_get_queued_requests_returns_ready_requests(
        self, degradation_manager, sample_request
    ):
        """Test that get_queued_requests returns requests ready for retry."""
        await degradation_manager.queue_request(sample_request, "gpt-4")
        
        ready = degradation_manager.get_queued_requests()
        
        assert len(ready) == 1
        assert ready[0].request == sample_request
        
    @pytest.mark.asyncio
    async def test_remove_from_queue_removes_request(
        self, degradation_manager, sample_request
    ):
        """Test that requests can be removed from queue."""
        await degradation_manager.queue_request(sample_request, "gpt-4")
        queued_req = degradation_manager.request_queue[0]
        
        degradation_manager.remove_from_queue(queued_req)
        
        assert len(degradation_manager.request_queue) == 0
        
    @pytest.mark.asyncio
    async def test_requeue_with_backoff_increments_retry_count(
        self, degradation_manager, sample_request
    ):
        """Test that requeuing increments retry count and sets next retry time."""
        await degradation_manager.queue_request(sample_request, "gpt-4")
        queued_req = degradation_manager.request_queue[0]
        
        degradation_manager.requeue_with_backoff(queued_req)
        
        assert queued_req.retry_count == 1
        assert queued_req.next_retry_at is not None
        assert queued_req.next_retry_at > datetime.now()
        
    @pytest.mark.asyncio
    async def test_requeue_removes_after_max_retries(
        self, degradation_manager, sample_request
    ):
        """Test that requests are removed after max retries."""
        await degradation_manager.queue_request(sample_request, "gpt-4")
        queued_req = degradation_manager.request_queue[0]
        
        # Retry until max retries
        for _ in range(5):
            degradation_manager.requeue_with_backoff(queued_req)
            
        assert len(degradation_manager.request_queue) == 0
        
    @pytest.mark.asyncio
    async def test_exponential_backoff_increases_delay(
        self, degradation_manager, sample_request
    ):
        """Test that exponential backoff increases delay."""
        await degradation_manager.queue_request(sample_request, "gpt-4")
        queued_req = degradation_manager.request_queue[0]
        
        # First retry - 2 * 2^1 = 4 seconds
        degradation_manager.requeue_with_backoff(queued_req)
        first_delay = (queued_req.next_retry_at - datetime.now()).total_seconds()
        
        # Second retry - 2 * 2^2 = 8 seconds
        queued_req.next_retry_at = None  # Reset for testing
        degradation_manager.requeue_with_backoff(queued_req)
        second_delay = (queued_req.next_retry_at - datetime.now()).total_seconds()
        
        assert second_delay > first_delay


class TestCacheFailureFallback:
    """Test cache failure fallback (Requirement 18.3)."""
    
    def test_mark_cache_failure_sets_unavailable(self, degradation_manager):
        """Test that cache can be marked as unavailable."""
        error = CacheError("Cache connection failed")
        
        degradation_manager.mark_cache_failure(error)
        
        assert degradation_manager.is_cache_available() is False
        
    def test_mark_cache_success_sets_available(self, degradation_manager):
        """Test that cache can be marked as available."""
        error = CacheError("Cache connection failed")
        degradation_manager.mark_cache_failure(error)
        
        degradation_manager.mark_cache_success()
        
        assert degradation_manager.is_cache_available() is True
        
    def test_cache_failure_logs_degradation(self, degradation_manager):
        """Test that cache failure logs degradation event."""
        error = CacheError("Cache connection failed")
        
        degradation_manager.mark_cache_failure(error)
        
        events = degradation_manager.get_degradation_events()
        assert len(events) > 0
        assert any("cache" in e["affected_components"] for e in events)
        
    def test_cache_failure_updates_degradation_status(self, degradation_manager):
        """Test that cache failure updates degradation status."""
        error = CacheError("Cache connection failed")
        
        degradation_manager.mark_cache_failure(error)
        
        status = degradation_manager.get_degradation_status()
        assert status.mode == DegradationMode.CACHE_UNAVAILABLE
        assert "cache" in status.affected_components


class TestMonitoringFailureFallback:
    """Test monitoring failure fallback (Requirement 18.4)."""
    
    def test_mark_monitoring_failure_sets_unavailable(self, degradation_manager):
        """Test that monitoring can be marked as unavailable."""
        error = Exception("Monitoring database connection failed")
        
        degradation_manager.mark_monitoring_failure(error)
        
        assert degradation_manager.is_monitoring_available() is False
        
    def test_mark_monitoring_success_sets_available(self, degradation_manager):
        """Test that monitoring can be marked as available."""
        error = Exception("Monitoring database connection failed")
        degradation_manager.mark_monitoring_failure(error)
        
        degradation_manager.mark_monitoring_success()
        
        assert degradation_manager.is_monitoring_available() is True
        
    def test_monitoring_failure_logs_degradation(self, degradation_manager):
        """Test that monitoring failure logs degradation event."""
        error = Exception("Monitoring database connection failed")
        
        degradation_manager.mark_monitoring_failure(error)
        
        events = degradation_manager.get_degradation_events()
        assert len(events) > 0
        assert any("monitoring" in e["affected_components"] for e in events)
        
    def test_monitoring_failure_updates_degradation_status(self, degradation_manager):
        """Test that monitoring failure updates degradation status."""
        error = Exception("Monitoring database connection failed")
        
        degradation_manager.mark_monitoring_failure(error)
        
        status = degradation_manager.get_degradation_status()
        assert status.mode == DegradationMode.MONITORING_UNAVAILABLE
        assert "monitoring" in status.affected_components


class TestDegradedModeLogging:
    """Test degraded mode logging (Requirement 18.5)."""
    
    def test_degradation_events_are_logged(self, degradation_manager):
        """Test that degradation events are logged."""
        error = CacheError("Cache failed")
        degradation_manager.mark_cache_failure(error)
        
        events = degradation_manager.get_degradation_events()
        
        assert len(events) > 0
        assert events[-1]["mode"] == DegradationMode.CACHE_UNAVAILABLE.value
        assert "cache" in events[-1]["affected_components"]
        
    def test_degradation_events_include_timestamp(self, degradation_manager):
        """Test that degradation events include timestamp."""
        error = CacheError("Cache failed")
        degradation_manager.mark_cache_failure(error)
        
        events = degradation_manager.get_degradation_events()
        
        assert "timestamp" in events[-1]
        # Should be parseable as ISO format
        datetime.fromisoformat(events[-1]["timestamp"])
        
    def test_degradation_events_limited_to_1000(self, degradation_manager):
        """Test that degradation events are limited to 1000."""
        # Generate many events
        for i in range(1500):
            if i % 2 == 0:
                degradation_manager.mark_cache_failure(CacheError("Test"))
            else:
                degradation_manager.mark_cache_success()
                
        events = degradation_manager.get_degradation_events()
        
        assert len(events) <= 1000
        
    def test_get_degradation_events_with_limit(self, degradation_manager):
        """Test that get_degradation_events respects limit parameter."""
        for _ in range(10):
            degradation_manager.mark_cache_failure(CacheError("Test"))
            degradation_manager.mark_cache_success()
            
        events = degradation_manager.get_degradation_events(limit=5)
        
        assert len(events) == 5
        
    def test_get_degradation_events_with_since_filter(self, degradation_manager):
        """Test that get_degradation_events filters by timestamp."""
        # Create some events
        degradation_manager.mark_cache_failure(CacheError("Test"))
        
        # Wait a bit
        import time
        time.sleep(0.1)
        
        since_time = datetime.now()
        
        # Create more events
        degradation_manager.mark_cache_success()
        degradation_manager.mark_monitoring_failure(Exception("Test"))
        
        events = degradation_manager.get_degradation_events(since=since_time)
        
        # Should only get events after since_time
        assert len(events) >= 2


class TestDegradationStatusUpdates:
    """Test degradation status updates."""
    
    def test_normal_mode_when_all_healthy(self, degradation_manager):
        """Test that status is NORMAL when all components are healthy."""
        status = degradation_manager.get_degradation_status()
        
        assert status.mode == DegradationMode.NORMAL
        assert len(status.affected_components) == 0
        
    def test_partial_provider_unavailable_mode(self, degradation_manager):
        """Test PARTIAL_PROVIDER_UNAVAILABLE mode."""
        # Mark one provider as unavailable
        for _ in range(3):
            degradation_manager.mark_provider_failure("openai")
            
        # Mark another as available
        degradation_manager.mark_provider_success("anthropic")
        
        status = degradation_manager.get_degradation_status()
        
        assert status.mode == DegradationMode.PARTIAL_PROVIDER_UNAVAILABLE
        assert "openai" in status.unavailable_providers
        
    def test_total_unavailability_mode(self, degradation_manager):
        """Test TOTAL_UNAVAILABILITY mode when all providers fail."""
        # Mark all providers as unavailable
        for provider in ["openai", "anthropic", "google"]:
            for _ in range(3):
                degradation_manager.mark_provider_failure(provider)
                
        status = degradation_manager.get_degradation_status()
        
        assert status.mode == DegradationMode.TOTAL_UNAVAILABILITY
        assert len(status.unavailable_providers) == 3
        
    def test_recovery_to_normal_mode(self, degradation_manager):
        """Test recovery to NORMAL mode."""
        # Enter degraded mode
        degradation_manager.mark_cache_failure(CacheError("Test"))
        assert degradation_manager.get_degradation_status().mode != DegradationMode.NORMAL
        
        # Recover
        degradation_manager.mark_cache_success()
        
        status = degradation_manager.get_degradation_status()
        assert status.mode == DegradationMode.NORMAL
        assert status.degraded_since is None


class TestExecuteWithFallback:
    """Test execute_with_fallback helper."""
    
    @pytest.mark.asyncio
    async def test_execute_with_fallback_returns_primary_result(self, degradation_manager):
        """Test that primary function result is returned on success."""
        async def primary():
            return "primary_result"
            
        async def fallback():
            return "fallback_result"
            
        result = await degradation_manager.execute_with_fallback(
            primary, fallback, "test_component"
        )
        
        assert result == "primary_result"
        
    @pytest.mark.asyncio
    async def test_execute_with_fallback_uses_fallback_on_failure(self, degradation_manager):
        """Test that fallback is used when primary fails."""
        async def primary():
            raise Exception("Primary failed")
            
        async def fallback():
            return "fallback_result"
            
        result = await degradation_manager.execute_with_fallback(
            primary, fallback, "test_component"
        )
        
        assert result == "fallback_result"
        
    @pytest.mark.asyncio
    async def test_execute_with_fallback_raises_if_both_fail(self, degradation_manager):
        """Test that exception is raised if both primary and fallback fail."""
        async def primary():
            raise Exception("Primary failed")
            
        async def fallback():
            raise Exception("Fallback failed")
            
        with pytest.raises(Exception, match="Fallback failed"):
            await degradation_manager.execute_with_fallback(
                primary, fallback, "test_component"
            )
            
    @pytest.mark.asyncio
    async def test_execute_with_fallback_raises_if_no_fallback(self, degradation_manager):
        """Test that exception is raised if primary fails and no fallback."""
        async def primary():
            raise Exception("Primary failed")
            
        with pytest.raises(Exception, match="Primary failed"):
            await degradation_manager.execute_with_fallback(
                primary, None, "test_component"
            )
            
    @pytest.mark.asyncio
    async def test_execute_with_fallback_works_with_sync_functions(self, degradation_manager):
        """Test that execute_with_fallback works with synchronous functions."""
        def primary():
            return "primary_result"
            
        def fallback():
            return "fallback_result"
            
        result = await degradation_manager.execute_with_fallback(
            primary, fallback, "test_component"
        )
        
        assert result == "primary_result"


class TestQueueProcessing:
    """Test queue processing loop."""
    
    @pytest.mark.asyncio
    async def test_start_and_stop(self, degradation_manager):
        """Test that manager can be started and stopped."""
        await degradation_manager.start()
        assert degradation_manager.queue_processing_task is not None
        
        await degradation_manager.stop()
        assert degradation_manager.queue_processing_task.cancelled()
        
    @pytest.mark.asyncio
    async def test_queue_processing_skips_during_total_unavailability(
        self, degradation_manager, sample_request
    ):
        """Test that queue processing is skipped during total unavailability."""
        # Mark all providers unavailable
        for provider in ["openai", "anthropic"]:
            for _ in range(3):
                degradation_manager.mark_provider_failure(provider)
                
        # Queue a request
        await degradation_manager.queue_request(sample_request, "gpt-4")
        
        # Process queue - should skip
        await degradation_manager._process_queued_requests()
        
        # Request should still be in queue
        assert len(degradation_manager.request_queue) == 1
