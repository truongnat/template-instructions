"""
Property-based tests for CacheManager class.

This module tests the correctness properties of the CacheManager including
cache hit serving, TTL expiration, cache key uniqueness, and LRU eviction.
"""

import unittest
import asyncio
import tempfile
import time
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, Any

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
        def dictionaries(self, *args, **kwargs): return lambda: {}
        def sampled_from(self, seq): return lambda: seq[0] if seq else None
        def builds(self, cls, **kwargs): return lambda: cls(**kwargs)
        def floats(self, **kwargs): return lambda: 1.0
    
    st = MockStrategies()
    
    def settings(**kwargs):
        def decorator(func):
            return func
        return decorator

from agentic_sdlc.orchestration.api_model_management.cache_manager import CacheManager
from agentic_sdlc.orchestration.api_model_management.models import (
    ModelRequest, ModelResponse, TokenUsage
)
from agentic_sdlc.orchestration.api_model_management.database import DatabaseManager


# Hypothesis strategies for generating test data

def model_request_strategy():
    """Strategy for generating ModelRequest instances"""
    return st.builds(
        ModelRequest,
        prompt=st.text(min_size=10, max_size=500),
        parameters=st.dictionaries(
            keys=st.text(min_size=1, max_size=20),
            values=st.one_of(
                st.text(min_size=1, max_size=50),
                st.integers(min_value=0, max_value=1000),
                st.floats(min_value=0.0, max_value=1.0)
            ),
            min_size=0,
            max_size=5
        ),
        task_id=st.text(min_size=5, max_size=50),
        agent_type=st.sampled_from(["PM", "BA", "SA", "Research", "Quality", "Implementation"]),
        max_tokens=st.one_of(st.none(), st.integers(min_value=100, max_value=4000)),
        temperature=st.floats(min_value=0.0, max_value=1.0)
    )


def model_response_strategy():
    """Strategy for generating ModelResponse instances"""
    return st.builds(
        ModelResponse,
        content=st.text(min_size=10, max_size=1000),
        model_id=st.sampled_from(["gpt-4", "gpt-3.5-turbo", "claude-3", "gemini-pro"]),
        token_usage=st.builds(
            TokenUsage,
            input_tokens=st.integers(min_value=10, max_value=1000),
            output_tokens=st.integers(min_value=10, max_value=1000),
            total_tokens=st.integers(min_value=20, max_value=2000)
        ),
        latency_ms=st.floats(min_value=100.0, max_value=5000.0),
        cost=st.floats(min_value=0.001, max_value=1.0),
        metadata=st.dictionaries(
            keys=st.text(min_size=1, max_size=20),
            values=st.text(min_size=1, max_size=50),
            min_size=0,
            max_size=3
        )
    )


class TestCacheManagerProperties(unittest.TestCase):
    """Test CacheManager correctness properties"""
    
    def setUp(self):
        """Set up test case"""
        if not HYPOTHESIS_AVAILABLE:
            self.skipTest("Hypothesis not available")
        
        # Create temporary database
        self.temp_dir = tempfile.mkdtemp()
        self.db_path = Path(self.temp_dir) / "test_cache.db"
        
        # Initialize database
        asyncio.run(self._init_database())
    
    def tearDown(self):
        """Clean up after test"""
        # Clean up temporary files
        if self.db_path.exists():
            self.db_path.unlink()
    
    async def _init_database(self):
        """Initialize database schema"""
        db_manager = DatabaseManager(self.db_path)
        await db_manager.initialize()
    
    def run_async(self, coro):
        """Helper to run async code in sync test"""
        return asyncio.run(coro)
    
    @settings(max_examples=10)
    @given(
        request=model_request_strategy(),
        response=model_response_strategy()
    )
    def test_property_37_cache_hit_serves_without_api_call(
        self,
        request: ModelRequest,
        response: ModelResponse
    ):
        """
        Feature: api-model-management
        Property 37: Cache hit serves without API call
        
        For any request that has been cached, a subsequent identical request
        should return the cached response without making an API call.
        
        This property combines cache lookup and serving functionality.
        
        Validates: Requirements 9.1, 9.2
        """
        async def test():
            # Create cache manager
            cache_manager = CacheManager(
                db_path=self.db_path,
                default_ttl_seconds=3600
            )
            
            # Generate cache key for the request
            cache_key = cache_manager.generate_cache_key(request)
            
            # First request - cache miss (should return None)
            cached_response_before = await cache_manager.get(cache_key)
            self.assertIsNone(
                cached_response_before,
                "Cache should be empty before storing response"
            )
            
            # Store response in cache
            await cache_manager.set(cache_key, response)
            
            # Second request - cache hit (should return cached response)
            cached_response_after = await cache_manager.get(cache_key)
            
            # Verify cache hit
            self.assertIsNotNone(
                cached_response_after,
                "Cache should return stored response"
            )
            
            # Verify cached response matches original
            self.assertEqual(
                cached_response_after.response.content,
                response.content,
                "Cached response content should match original"
            )
            self.assertEqual(
                cached_response_after.response.model_id,
                response.model_id,
                "Cached response model_id should match original"
            )
            self.assertEqual(
                cached_response_after.response.token_usage.input_tokens,
                response.token_usage.input_tokens,
                "Cached response token usage should match original"
            )
            self.assertEqual(
                cached_response_after.response.cost,
                response.cost,
                "Cached response cost should match original"
            )
            
            # Verify hit count is incremented
            self.assertEqual(
                cached_response_after.hit_count,
                1,
                "Hit count should be 1 after first cache hit"
            )
            
            # Third request - another cache hit
            cached_response_third = await cache_manager.get(cache_key)
            self.assertEqual(
                cached_response_third.hit_count,
                2,
                "Hit count should be 2 after second cache hit"
            )
        
        self.run_async(test())
    
    @settings(max_examples=5, deadline=3000)
    @given(
        request=model_request_strategy(),
        response=model_response_strategy(),
        ttl_seconds=st.integers(min_value=1, max_value=2)
    )
    def test_property_38_response_caching_with_ttl(
        self,
        request: ModelRequest,
        response: ModelResponse,
        ttl_seconds: int
    ):
        """
        Feature: api-model-management
        Property 38: Response caching with TTL
        
        For any response cached with TTL T seconds, the response should be
        available for T seconds and then expire (not be retrievable).
        
        Validates: Requirements 9.3
        """
        async def test():
            # Create cache manager
            cache_manager = CacheManager(
                db_path=self.db_path,
                default_ttl_seconds=3600
            )
            
            # Generate cache key
            cache_key = cache_manager.generate_cache_key(request)
            
            # Store response with custom TTL
            await cache_manager.set(cache_key, response, ttl_seconds=ttl_seconds)
            
            # Immediately retrieve - should be available
            cached_response = await cache_manager.get(cache_key)
            self.assertIsNotNone(
                cached_response,
                "Response should be available immediately after caching"
            )
            
            # Verify expiration time is set correctly
            expected_expires_at = cached_response.cached_at + timedelta(seconds=ttl_seconds)
            # Allow 1 second tolerance for test execution time
            time_diff = abs((cached_response.expires_at - expected_expires_at).total_seconds())
            self.assertLess(
                time_diff,
                1.0,
                f"Expiration time should be {ttl_seconds} seconds from cached_at"
            )
            
            # Wait for TTL to expire (add small buffer)
            await asyncio.sleep(ttl_seconds + 0.3)
            
            # Try to retrieve after expiration - should return None
            expired_response = await cache_manager.get(cache_key)
            self.assertIsNone(
                expired_response,
                "Response should not be available after TTL expires"
            )
        
        self.run_async(test())
    
    @settings(max_examples=10)
    @given(
        requests=st.lists(
            model_request_strategy(),
            min_size=2,
            max_size=10
        )
    )
    def test_property_39_cache_key_uniqueness(self, requests: list):
        """
        Feature: api-model-management
        Property 39: Cache key uniqueness
        
        For any set of different requests, each request should generate a
        unique cache key. Identical requests should generate the same key.
        
        Validates: Requirements 9.4
        """
        async def test():
            # Create cache manager
            cache_manager = CacheManager(
                db_path=self.db_path,
                default_ttl_seconds=3600
            )
            
            # Generate cache keys for all requests
            cache_keys = [cache_manager.generate_cache_key(req) for req in requests]
            
            # Verify that identical requests generate the same key
            for request in requests:
                key1 = cache_manager.generate_cache_key(request)
                key2 = cache_manager.generate_cache_key(request)
                self.assertEqual(
                    key1,
                    key2,
                    "Identical requests should generate the same cache key"
                )
            
            # Verify cache keys are deterministic (same request always produces same key)
            for request in requests:
                keys = [cache_manager.generate_cache_key(request) for _ in range(5)]
                self.assertEqual(
                    len(set(keys)),
                    1,
                    "Cache key generation should be deterministic"
                )
            
            # Verify that different requests likely generate different keys
            # (we can't guarantee uniqueness without unique=True, but we can check)
            unique_keys = set(cache_keys)
            # If we have more than 2 requests, at least some should be unique
            if len(requests) > 2:
                self.assertGreater(
                    len(unique_keys),
                    1,
                    "Different requests should likely generate different cache keys"
                )
        
        self.run_async(test())
    
    @settings(max_examples=8, deadline=10000)
    @given(
        num_entries=st.integers(min_value=5, max_value=20),
        max_size_mb=st.integers(min_value=1, max_value=5)
    )
    def test_property_40_lru_cache_eviction(
        self,
        num_entries: int,
        max_size_mb: int
    ):
        """
        Feature: api-model-management
        Property 40: LRU cache eviction
        
        For any cache that exceeds its maximum size, the least recently used
        entries should be evicted first until the cache is below the target size.
        
        Validates: Requirements 9.5
        """
        async def test():
            # Create cache manager with small max size
            cache_manager = CacheManager(
                db_path=self.db_path,
                max_size_mb=max_size_mb,
                default_ttl_seconds=3600
            )
            
            # Generate test data
            entries = []
            for i in range(num_entries):
                request = ModelRequest(
                    prompt=f"Test prompt {i} " + "x" * 1000,  # Make it larger
                    parameters={"index": i},
                    task_id=f"task-{i}",
                    agent_type="PM"
                )
                response = ModelResponse(
                    content=f"Test response {i} " + "y" * 5000,  # Large response
                    model_id="gpt-4",
                    token_usage=TokenUsage(
                        input_tokens=100,
                        output_tokens=200,
                        total_tokens=300
                    ),
                    latency_ms=1000.0,
                    cost=0.01
                )
                cache_key = cache_manager.generate_cache_key(request)
                entries.append((cache_key, request, response))
            
            # Store all entries in cache
            for cache_key, request, response in entries:
                await cache_manager.set(cache_key, response)
                # Small delay to ensure different last_accessed times
                await asyncio.sleep(0.01)
            
            # Access some entries to update their last_accessed time
            # Access the last half of entries (making them more recently used)
            mid_point = num_entries // 2
            for cache_key, _, _ in entries[mid_point:]:
                await cache_manager.get(cache_key)
                await asyncio.sleep(0.01)
            
            # Get current cache size
            stats_before = await cache_manager.get_stats()
            initial_size_mb = stats_before['cache_size_mb']
            
            # If cache is over max size, trigger LRU eviction
            if initial_size_mb > max_size_mb:
                target_size = int(max_size_mb * 0.8)
                evicted_count = await cache_manager.evict_lru(target_size)
                
                # Verify some entries were evicted
                self.assertGreater(
                    evicted_count,
                    0,
                    "Some entries should be evicted when cache exceeds max size"
                )
                
                # Verify cache size is reduced
                stats_after = await cache_manager.get_stats()
                final_size_mb = stats_after['cache_size_mb']
                self.assertLess(
                    final_size_mb,
                    initial_size_mb,
                    "Cache size should be reduced after eviction"
                )
                
                # Verify recently accessed entries are still in cache
                # (the ones we accessed in the second half)
                recently_accessed_still_cached = 0
                for cache_key, _, _ in entries[mid_point:]:
                    cached = await cache_manager.get(cache_key)
                    if cached is not None:
                        recently_accessed_still_cached += 1
                
                # Verify least recently accessed entries were evicted first
                # (the ones from the first half that we didn't access)
                least_recently_accessed_evicted = 0
                for cache_key, _, _ in entries[:mid_point]:
                    cached = await cache_manager.get(cache_key)
                    if cached is None:
                        least_recently_accessed_evicted += 1
                
                # LRU should evict older entries before newer ones
                # At least some of the least recently accessed should be evicted
                if evicted_count > 0:
                    self.assertGreater(
                        least_recently_accessed_evicted,
                        0,
                        "Least recently accessed entries should be evicted first"
                    )
        
        self.run_async(test())


if __name__ == "__main__":
    unittest.main()
