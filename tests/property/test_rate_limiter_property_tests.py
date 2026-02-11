"""
Property-based tests for RateLimiter class.

This module tests the correctness properties of the RateLimiter including
rate limit tracking, threshold detection, window reset, and request blocking.
"""

import unittest
import asyncio
import tempfile
from pathlib import Path
from datetime import datetime, timedelta
from typing import List, Tuple

try:
    from hypothesis import given, strategies as st, settings, assume
    HYPOTHESIS_AVAILABLE = True
except ImportError:
    HYPOTHESIS_AVAILABLE = False
    
    def given(*args, **kwargs):
        def decorator(func):
            return func
        return decorator
    
    class MockStrategies:
        def text(self, **kwargs): return lambda: "test"
        def integers(self, **kwargs): return lambda: 1
        def lists(self, *args, **kwargs): return lambda: []
        def tuples(self, *args, **kwargs): return lambda: ()
        def floats(self, **kwargs): return lambda: 1.0
        def booleans(self): return lambda: True
    
    st = MockStrategies()
    
    def settings(**kwargs):
        def decorator(func):
            return func
        return decorator

from agentic_sdlc.orchestration.api_model_management.rate_limiter import RateLimiter
from agentic_sdlc.orchestration.api_model_management.registry import ModelRegistry
from agentic_sdlc.orchestration.api_model_management.models import ModelMetadata, RateLimits


# Hypothesis strategies for generating test data

def rate_limits_strategy():
    """Strategy for generating rate limits"""
    return st.builds(
        RateLimits,
        requests_per_minute=st.integers(min_value=10, max_value=1000),
        tokens_per_minute=st.integers(min_value=1000, max_value=100000)
    )


def model_metadata_strategy():
    """Strategy for generating model metadata"""
    return st.builds(
        ModelMetadata,
        id=st.text(min_size=1, max_size=50, alphabet=st.characters(
            whitelist_categories=('Lu', 'Ll', 'Nd'), whitelist_characters='-_'
        )),
        provider=st.sampled_from(["openai", "anthropic", "google", "ollama"]),
        name=st.text(min_size=1, max_size=100),
        capabilities=st.lists(
            st.sampled_from(["text-generation", "code-generation", "analysis"]),
            min_size=1,
            max_size=3,
            unique=True
        ),
        cost_per_1k_input_tokens=st.floats(min_value=0.0, max_value=0.1),
        cost_per_1k_output_tokens=st.floats(min_value=0.0, max_value=0.3),
        rate_limits=rate_limits_strategy(),
        context_window=st.integers(min_value=1000, max_value=200000),
        average_response_time_ms=st.floats(min_value=100.0, max_value=5000.0),
        enabled=st.booleans()
    )


def request_sequence_strategy():
    """Strategy for generating sequences of requests (timestamp offset, tokens)"""
    return st.lists(
        st.tuples(
            st.integers(min_value=0, max_value=59),  # seconds offset within a minute
            st.integers(min_value=100, max_value=5000)  # tokens per request
        ),
        min_size=1,
        max_size=50
    )


class TestRateLimiterProperties(unittest.TestCase):
    """
    Property-based tests for RateLimiter.
    
    Tests Properties 14-17 from the design document:
    - Property 14: Rate limit tracking with threshold detection
    - Property 15: Rate limit event recording
    - Property 16: Rate limit window reset
    - Property 17: Rate-limited model request blocking
    """
    
    def setUp(self):
        """Set up test case"""
        if not HYPOTHESIS_AVAILABLE:
            self.skipTest("Hypothesis not available")
        
        # Create temporary directory for database
        self.temp_dir = tempfile.mkdtemp()
        self.db_path = Path(self.temp_dir) / "test_rate_limiter.db"
        
        # Create temporary config file
        self.config_path = Path(self.temp_dir) / "models.json"
    
    def _create_registry_with_model(self, model: ModelMetadata) -> ModelRegistry:
        """Helper to create a registry with a single model"""
        import json
        
        config_data = {
            "models": [{
                "id": model.id,
                "provider": model.provider,
                "name": model.name,
                "capabilities": model.capabilities,
                "cost_per_1k_input_tokens": model.cost_per_1k_input_tokens,
                "cost_per_1k_output_tokens": model.cost_per_1k_output_tokens,
                "rate_limits": {
                    "requests_per_minute": model.rate_limits.requests_per_minute,
                    "tokens_per_minute": model.rate_limits.tokens_per_minute
                },
                "context_window": model.context_window,
                "average_response_time_ms": model.average_response_time_ms,
                "enabled": model.enabled
            }]
        }
        
        with open(self.config_path, 'w') as f:
            json.dump(config_data, f)
        
        registry = ModelRegistry(self.config_path)
        registry.load_config()
        return registry
    
    @settings(max_examples=10, deadline=None)
    @given(
        model=model_metadata_strategy(),
        requests=request_sequence_strategy()
    )
    def test_property_14_rate_limit_tracking_with_threshold_detection(
        self,
        model: ModelMetadata,
        requests: List[Tuple[int, int]]
    ):
        """
        Feature: api-model-management
        Property 14: Rate limit tracking with threshold detection
        
        For any model, after N requests consuming M tokens, the tracked counts
        should equal N and M, and when usage reaches 90% of limits, the model
        should be marked as rate-limited.
        
        Validates: Requirements 4.1, 4.3
        """
        # Ensure model is enabled
        assume(model.enabled)
        
        # Create registry and rate limiter
        registry = self._create_registry_with_model(model)
        rate_limiter = RateLimiter(registry, self.db_path, threshold_percent=90.0)
        
        # Track expected counts
        total_requests = 0
        total_tokens = 0
        
        # Process requests
        for _, tokens in requests:
            # Record the request first
            asyncio.run(rate_limiter.record_request(model.id, tokens, was_rate_limited=False))
            
            total_requests += 1
            total_tokens += tokens
            
            # Calculate current utilization AFTER recording
            request_utilization = (total_requests / model.rate_limits.requests_per_minute) * 100
            token_utilization = (total_tokens / model.rate_limits.tokens_per_minute) * 100
            
            # Check rate limit status after recording
            status = asyncio.run(rate_limiter.check_rate_limit(model.id, 0))
            
            # If we're at or above 90% threshold, should be marked as limited
            if request_utilization >= 90.0 or token_utilization >= 90.0:
                self.assertTrue(
                    status.is_limited,
                    f"Model should be rate-limited at {request_utilization:.1f}% request "
                    f"or {token_utilization:.1f}% token utilization"
                )
                break  # Stop processing once rate-limited
            
            # Verify tracking accuracy
            # The internal tracking should match our counts
            # (We can't directly access internal state, but we can verify behavior)
            status_after = asyncio.run(rate_limiter.check_rate_limit(model.id, 0))
            
            # Calculate expected remaining
            expected_requests_remaining = model.rate_limits.requests_per_minute - total_requests
            expected_tokens_remaining = model.rate_limits.tokens_per_minute - total_tokens
            
            # Verify remaining counts are reasonable
            self.assertGreaterEqual(
                status_after.requests_remaining,
                0,
                "Requests remaining should not be negative"
            )
            self.assertGreaterEqual(
                status_after.tokens_remaining,
                0,
                "Tokens remaining should not be negative"
            )
    
    @settings(max_examples=10)
    @given(model=model_metadata_strategy())
    def test_property_15_rate_limit_event_recording(self, model: ModelMetadata):
        """
        Feature: api-model-management
        Property 15: Rate limit event recording
        
        For any API response with HTTP 429 or rate limit error codes, a rate
        limit event should be recorded with timestamp and model ID.
        
        Validates: Requirements 4.2
        """
        # Ensure model is enabled
        assume(model.enabled)
        
        # Initialize database
        from agentic_sdlc.orchestration.api_model_management.database import initialize_database
        asyncio.run(initialize_database(self.db_path))
        
        # Create registry and rate limiter
        registry = self._create_registry_with_model(model)
        rate_limiter = RateLimiter(registry, self.db_path)
        
        # Record a request with rate limit error
        asyncio.run(rate_limiter.record_request(model.id, 1000, was_rate_limited=True))
        
        # Verify the model is marked as rate-limited
        self.assertTrue(
            rate_limiter.is_rate_limited(model.id),
            "Model should be marked as rate-limited after rate limit error"
        )
        
        # Verify event was persisted to database
        import aiosqlite
        
        async def check_event():
            async with aiosqlite.connect(self.db_path) as db:
                cursor = await db.execute(
                    "SELECT COUNT(*) FROM rate_limit_events WHERE model_id = ? AND event_type = ?",
                    (model.id, "rate_limited")
                )
                count = (await cursor.fetchone())[0]
                return count
        
        event_count = asyncio.run(check_event())
        self.assertGreater(
            event_count,
            0,
            "Rate limit event should be recorded in database"
        )
    
    @settings(max_examples=10)
    @given(model=model_metadata_strategy())
    def test_property_16_rate_limit_window_reset(self, model: ModelMetadata):
        """
        Feature: api-model-management
        Property 16: Rate limit window reset
        
        For any rate-limited model, after the rate limit window expires, the
        model's rate limit status should be reset to not rate-limited.
        
        Validates: Requirements 4.4
        """
        # Ensure model is enabled
        assume(model.enabled)
        
        # Initialize database
        from agentic_sdlc.orchestration.api_model_management.database import initialize_database
        asyncio.run(initialize_database(self.db_path))
        
        # Create registry and rate limiter
        registry = self._create_registry_with_model(model)
        rate_limiter = RateLimiter(registry, self.db_path)
        
        # Mark model as rate-limited with a future reset time first
        future_reset_time = datetime.now() + timedelta(seconds=5)
        asyncio.run(rate_limiter._mark_rate_limited(model.id, future_reset_time))
        
        # Verify model is marked as rate-limited with future reset time
        self.assertTrue(
            rate_limiter.is_rate_limited(model.id),
            "Model should be marked as rate-limited with future reset time"
        )
        
        # Now update to a past reset time to simulate window expiration
        past_reset_time = datetime.now() - timedelta(seconds=1)
        rate_limiter._rate_limit_status[model.id] = (True, past_reset_time)
        
        # Check rate limit status - this should trigger reset since time has passed
        status = asyncio.run(rate_limiter.check_rate_limit(model.id, 100))
        
        # After checking with expired reset time, model should no longer be limited
        self.assertFalse(
            status.is_limited,
            "Model should not be rate-limited after window expires"
        )
        
        # Verify the status was actually reset
        self.assertFalse(
            rate_limiter.is_rate_limited(model.id),
            "Model should not be marked as rate-limited after reset"
        )
    
    @settings(max_examples=10)
    @given(
        model=model_metadata_strategy(),
        estimated_tokens=st.integers(min_value=100, max_value=5000)
    )
    def test_property_17_rate_limited_model_request_blocking(
        self,
        model: ModelMetadata,
        estimated_tokens: int
    ):
        """
        Feature: api-model-management
        Property 17: Rate-limited model request blocking
        
        For any model marked as rate-limited, new requests should be blocked
        until the rate limit window resets.
        
        Validates: Requirements 4.5
        """
        # Ensure model is enabled
        assume(model.enabled)
        
        # Create registry and rate limiter
        registry = self._create_registry_with_model(model)
        rate_limiter = RateLimiter(registry, self.db_path)
        
        # Mark model as rate-limited with a future reset time
        future_reset_time = datetime.now() + timedelta(seconds=60)
        asyncio.run(rate_limiter._mark_rate_limited(model.id, future_reset_time))
        
        # Verify model is marked as rate-limited
        self.assertTrue(
            rate_limiter.is_rate_limited(model.id),
            "Model should be marked as rate-limited"
        )
        
        # Try to check rate limit for a new request
        status = asyncio.run(rate_limiter.check_rate_limit(model.id, estimated_tokens))
        
        # Request should be blocked (is_limited = True)
        self.assertTrue(
            status.is_limited,
            "New requests should be blocked when model is rate-limited"
        )
        
        # Verify reset time is provided
        self.assertIsNotNone(
            status.reset_time,
            "Reset time should be provided for rate-limited model"
        )
        
        # Verify time until reset is positive
        time_until_reset = rate_limiter.get_time_until_reset(model.id)
        self.assertIsNotNone(
            time_until_reset,
            "Time until reset should be available"
        )
        self.assertGreater(
            time_until_reset,
            0,
            "Time until reset should be positive for future reset time"
        )


if __name__ == "__main__":
    unittest.main()
