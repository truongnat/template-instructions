"""
Unit tests for RateLimiter class.

This module tests specific examples and edge cases for the RateLimiter including
sliding window algorithm, threshold detection edge cases, and window reset timing.
"""

import unittest
import asyncio
import tempfile
import aiosqlite
import json
from pathlib import Path
from datetime import datetime, timedelta
from unittest.mock import Mock, AsyncMock, patch

from agentic_sdlc.orchestration.api_model_management.rate_limiter import RateLimiter
from agentic_sdlc.orchestration.api_model_management.registry import ModelRegistry
from agentic_sdlc.orchestration.api_model_management.models import (
    ModelMetadata,
    RateLimits,
    RateLimitStatus
)


class TestRateLimiterUnitTests(unittest.TestCase):
    """Unit tests for RateLimiter"""
    
    def setUp(self):
        """Set up test case"""
        # Create temporary directory for database
        self.temp_dir = tempfile.mkdtemp()
        self.db_path = Path(self.temp_dir) / "test_rate_limiter.db"
        
        # Create temporary config file
        self.config_path = Path(self.temp_dir) / "model_registry.json"
        
        # Create a sample configuration
        self._create_sample_config()
        
        # Initialize database schema
        asyncio.run(self._init_database())
        
        # Create registry
        self.registry = ModelRegistry(self.config_path)
        self.registry.load_config()
    
    def tearDown(self):
        """Clean up after test"""
        # Clean up temp files
        import shutil
        if Path(self.temp_dir).exists():
            shutil.rmtree(self.temp_dir)
    
    def _create_sample_config(self):
        """Create a sample model registry configuration"""
        config = {
            "models": [
                {
                    "id": "gpt-4-turbo",
                    "provider": "openai",
                    "name": "GPT-4 Turbo",
                    "capabilities": ["text-generation", "code-generation"],
                    "cost_per_1k_input_tokens": 0.01,
                    "cost_per_1k_output_tokens": 0.03,
                    "rate_limits": {
                        "requests_per_minute": 100,
                        "tokens_per_minute": 10000
                    },
                    "context_window": 128000,
                    "average_response_time_ms": 2000,
                    "enabled": True
                },
                {
                    "id": "claude-3.5-sonnet",
                    "provider": "anthropic",
                    "name": "Claude 3.5 Sonnet",
                    "capabilities": ["text-generation", "code-generation"],
                    "cost_per_1k_input_tokens": 0.003,
                    "cost_per_1k_output_tokens": 0.015,
                    "rate_limits": {
                        "requests_per_minute": 50,
                        "tokens_per_minute": 5000
                    },
                    "context_window": 200000,
                    "average_response_time_ms": 1500,
                    "enabled": True
                }
            ]
        }
        
        with open(self.config_path, 'w') as f:
            json.dump(config, f)
    
    async def _init_database(self):
        """Initialize database schema"""
        from agentic_sdlc.orchestration.api_model_management.database import initialize_database
        await initialize_database(self.db_path)
    
    def test_sliding_window_algorithm_basic(self):
        """Test basic sliding window algorithm functionality"""
        rate_limiter = RateLimiter(self.registry, self.db_path)
        model_id = "gpt-4-turbo"
        
        # Record 5 requests
        for i in range(5):
            asyncio.run(rate_limiter.record_request(model_id, 100))
        
        # Check rate limit status
        status = asyncio.run(rate_limiter.check_rate_limit(model_id, 100))
        
        # Should not be rate-limited yet (5 out of 100 requests)
        self.assertFalse(status.is_limited)
        self.assertEqual(status.requests_remaining, 95)
        self.assertEqual(status.tokens_remaining, 9500)
    
    def test_sliding_window_cleanup(self):
        """Test that old entries are cleaned up from sliding window"""
        rate_limiter = RateLimiter(self.registry, self.db_path)
        model_id = "gpt-4-turbo"
        
        # Manually add old entries to the history (older than 1 minute)
        # Use 5 minutes to ensure it's definitely outside the window
        old_timestamp = datetime.now() - timedelta(minutes=5)
        rate_limiter._request_history[model_id].append((old_timestamp, 1000))
        
        # Verify we have 1 old entry
        self.assertEqual(len(rate_limiter._request_history[model_id]), 1)
        
        # Manually trigger cleanup
        rate_limiter._cleanup_old_entries(model_id)
        
        # Old entry should be cleaned up
        self.assertEqual(len(rate_limiter._request_history[model_id]), 0)
        
        # Now add a recent entry
        recent_timestamp = datetime.now()
        rate_limiter._request_history[model_id].append((recent_timestamp, 100))
        
        # Cleanup should not remove recent entry
        rate_limiter._cleanup_old_entries(model_id)
        self.assertEqual(len(rate_limiter._request_history[model_id]), 1)
        
        # Verify the remaining entry is the recent one
        remaining_tokens = sum(tokens for _, tokens in rate_limiter._request_history[model_id])
        self.assertEqual(remaining_tokens, 100)
    
    def test_threshold_detection_at_exactly_90_percent(self):
        """Test threshold detection at exactly 90% utilization"""
        rate_limiter = RateLimiter(self.registry, self.db_path, threshold_percent=90.0)
        model_id = "gpt-4-turbo"
        
        # Record 89 requests (89% of 100)
        for i in range(89):
            asyncio.run(rate_limiter.record_request(model_id, 100))
        
        # Should not be rate-limited yet
        status = asyncio.run(rate_limiter.check_rate_limit(model_id, 100))
        self.assertFalse(status.is_limited)
        
        # Record one more request to reach 90%
        asyncio.run(rate_limiter.record_request(model_id, 100))
        
        # Now should be rate-limited
        status = asyncio.run(rate_limiter.check_rate_limit(model_id, 100))
        self.assertTrue(status.is_limited)
    
    def test_threshold_detection_token_based(self):
        """Test threshold detection based on token usage"""
        rate_limiter = RateLimiter(self.registry, self.db_path, threshold_percent=90.0)
        model_id = "gpt-4-turbo"
        
        # Record requests with high token usage (9000 tokens = 90% of 10000)
        asyncio.run(rate_limiter.record_request(model_id, 9000))
        
        # Should be rate-limited due to token threshold
        status = asyncio.run(rate_limiter.check_rate_limit(model_id, 100))
        self.assertTrue(status.is_limited)
    
    def test_threshold_detection_edge_case_just_below(self):
        """Test threshold detection just below 90%"""
        rate_limiter = RateLimiter(self.registry, self.db_path, threshold_percent=90.0)
        model_id = "gpt-4-turbo"
        
        # Record 89 requests (89% of 100)
        for i in range(89):
            asyncio.run(rate_limiter.record_request(model_id, 100))
        
        # Should not be rate-limited at 89%
        status = asyncio.run(rate_limiter.check_rate_limit(model_id, 100))
        self.assertFalse(status.is_limited)
        self.assertEqual(status.requests_remaining, 11)
    
    def test_window_reset_timing_immediate(self):
        """Test that window reset happens immediately when time expires"""
        rate_limiter = RateLimiter(self.registry, self.db_path)
        model_id = "gpt-4-turbo"
        
        # Mark as rate-limited with past reset time
        past_reset_time = datetime.now() - timedelta(seconds=1)
        rate_limiter._rate_limit_status[model_id] = (True, past_reset_time)
        
        # Check rate limit - should trigger immediate reset
        status = asyncio.run(rate_limiter.check_rate_limit(model_id, 100))
        
        # Should not be limited after reset
        self.assertFalse(status.is_limited)
        self.assertFalse(rate_limiter.is_rate_limited(model_id))
    
    def test_window_reset_timing_future(self):
        """Test that window does not reset before time expires"""
        rate_limiter = RateLimiter(self.registry, self.db_path)
        model_id = "gpt-4-turbo"
        
        # Mark as rate-limited with future reset time
        future_reset_time = datetime.now() + timedelta(seconds=60)
        asyncio.run(rate_limiter._mark_rate_limited(model_id, future_reset_time))
        
        # Check rate limit - should still be limited
        status = asyncio.run(rate_limiter.check_rate_limit(model_id, 100))
        
        # Should still be limited
        self.assertTrue(status.is_limited)
        self.assertTrue(rate_limiter.is_rate_limited(model_id))
    
    def test_get_time_until_reset_positive(self):
        """Test get_time_until_reset returns positive value for future reset"""
        rate_limiter = RateLimiter(self.registry, self.db_path)
        model_id = "gpt-4-turbo"
        
        # Mark as rate-limited with future reset time
        future_reset_time = datetime.now() + timedelta(seconds=30)
        asyncio.run(rate_limiter._mark_rate_limited(model_id, future_reset_time))
        
        # Get time until reset
        time_until_reset = rate_limiter.get_time_until_reset(model_id)
        
        # Should be positive and approximately 30 seconds
        self.assertIsNotNone(time_until_reset)
        self.assertGreater(time_until_reset, 0)
        self.assertLessEqual(time_until_reset, 30)
    
    def test_get_time_until_reset_zero_for_past(self):
        """Test get_time_until_reset returns 0 for past reset time"""
        rate_limiter = RateLimiter(self.registry, self.db_path)
        model_id = "gpt-4-turbo"
        
        # Mark as rate-limited with past reset time
        past_reset_time = datetime.now() - timedelta(seconds=10)
        rate_limiter._rate_limit_status[model_id] = (True, past_reset_time)
        
        # Get time until reset
        time_until_reset = rate_limiter.get_time_until_reset(model_id)
        
        # Should be 0 for past reset time
        self.assertEqual(time_until_reset, 0)
    
    def test_get_time_until_reset_none_for_not_limited(self):
        """Test get_time_until_reset returns None for non-limited model"""
        rate_limiter = RateLimiter(self.registry, self.db_path)
        model_id = "gpt-4-turbo"
        
        # Get time until reset for non-limited model
        time_until_reset = rate_limiter.get_time_until_reset(model_id)
        
        # Should be None
        self.assertIsNone(time_until_reset)
    
    def test_explicit_rate_limit_error_marking(self):
        """Test that explicit rate limit errors mark model as limited"""
        rate_limiter = RateLimiter(self.registry, self.db_path)
        model_id = "gpt-4-turbo"
        
        # Record request with rate limit error
        asyncio.run(rate_limiter.record_request(model_id, 100, was_rate_limited=True))
        
        # Model should be marked as rate-limited
        self.assertTrue(rate_limiter.is_rate_limited(model_id))
        
        # Check rate limit status
        status = asyncio.run(rate_limiter.check_rate_limit(model_id, 100))
        self.assertTrue(status.is_limited)
    
    def test_rate_limit_event_persistence(self):
        """Test that rate limit events are persisted to database"""
        rate_limiter = RateLimiter(self.registry, self.db_path)
        model_id = "gpt-4-turbo"
        
        # Mark as rate-limited
        reset_time = datetime.now() + timedelta(seconds=60)
        asyncio.run(rate_limiter._mark_rate_limited(model_id, reset_time))
        
        # Check database for event
        async def check_event():
            async with aiosqlite.connect(self.db_path) as db:
                cursor = await db.execute(
                    "SELECT COUNT(*) FROM rate_limit_events WHERE model_id = ? AND event_type = ?",
                    (model_id, "rate_limited")
                )
                count = (await cursor.fetchone())[0]
                return count
        
        event_count = asyncio.run(check_event())
        self.assertGreater(event_count, 0)
    
    def test_rate_limit_reset_event_persistence(self):
        """Test that rate limit reset events are persisted to database"""
        rate_limiter = RateLimiter(self.registry, self.db_path)
        model_id = "gpt-4-turbo"
        
        # Mark as rate-limited first
        reset_time = datetime.now() + timedelta(seconds=60)
        asyncio.run(rate_limiter._mark_rate_limited(model_id, reset_time))
        
        # Reset rate limit
        asyncio.run(rate_limiter._reset_rate_limit(model_id))
        
        # Check database for reset event
        async def check_event():
            async with aiosqlite.connect(self.db_path) as db:
                cursor = await db.execute(
                    "SELECT COUNT(*) FROM rate_limit_events WHERE model_id = ? AND event_type = ?",
                    (model_id, "reset")
                )
                count = (await cursor.fetchone())[0]
                return count
        
        event_count = asyncio.run(check_event())
        self.assertGreater(event_count, 0)
    
    def test_multiple_models_independent_tracking(self):
        """Test that multiple models are tracked independently"""
        rate_limiter = RateLimiter(self.registry, self.db_path)
        model1 = "gpt-4-turbo"
        model2 = "claude-3.5-sonnet"
        
        # Record requests for model1
        for i in range(45):  # 90% of 50 for claude
            asyncio.run(rate_limiter.record_request(model1, 100))
        
        # Record requests for model2 to hit threshold
        for i in range(45):  # 90% of 50
            asyncio.run(rate_limiter.record_request(model2, 100))
        
        # Check both models
        status1 = asyncio.run(rate_limiter.check_rate_limit(model1, 100))
        status2 = asyncio.run(rate_limiter.check_rate_limit(model2, 100))
        
        # Model1 should not be limited (45 out of 100)
        self.assertFalse(status1.is_limited)
        
        # Model2 should be limited (45 out of 50 = 90%)
        self.assertTrue(status2.is_limited)
    
    def test_unknown_model_handling(self):
        """Test handling of unknown model ID"""
        rate_limiter = RateLimiter(self.registry, self.db_path)
        unknown_model = "unknown-model"
        
        # Should raise ValueError for unknown model
        with self.assertRaises(ValueError):
            asyncio.run(rate_limiter.check_rate_limit(unknown_model, 100))
    
    def test_record_request_unknown_model_warning(self):
        """Test that recording request for unknown model logs warning"""
        rate_limiter = RateLimiter(self.registry, self.db_path)
        unknown_model = "unknown-model"
        
        # Should not raise error, but log warning
        # This should complete without exception
        asyncio.run(rate_limiter.record_request(unknown_model, 100))
        
        # Verify no history was recorded
        self.assertEqual(len(rate_limiter._request_history[unknown_model]), 0)


if __name__ == "__main__":
    unittest.main()
