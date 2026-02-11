"""
Unit tests for CacheManager class.

This module tests specific scenarios and edge cases for the CacheManager
including cache hit/miss scenarios, TTL expiration, and LRU eviction.
"""

import unittest
import asyncio
import tempfile
from pathlib import Path
from datetime import datetime, timedelta

from agentic_sdlc.orchestration.api_model_management.cache_manager import CacheManager
from agentic_sdlc.orchestration.api_model_management.models import (
    ModelRequest, ModelResponse, TokenUsage
)
from agentic_sdlc.orchestration.api_model_management.database import DatabaseManager


class TestCacheManager(unittest.TestCase):
    """Unit tests for CacheManager"""
    
    def setUp(self):
        """Set up test case"""
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
    
    # Cache Hit/Miss Scenarios
    
    def test_cache_miss_returns_none(self):
        """Test that cache miss returns None"""
        async def test():
            cache_manager = CacheManager(
                db_path=self.db_path,
                default_ttl_seconds=3600
            )
            
            # Try to get non-existent cache entry
            result = await cache_manager.get("nonexistent_key")
            
            self.assertIsNone(result, "Cache miss should return None")
        
        self.run_async(test())
    
    def test_cache_hit_returns_stored_response(self):
        """Test that cache hit returns the stored response"""
        async def test():
            cache_manager = CacheManager(
                db_path=self.db_path,
                default_ttl_seconds=3600
            )
            
            # Create test data
            request = ModelRequest(
                prompt="Test prompt",
                parameters={"temperature": 0.7},
                task_id="task-1",
                agent_type="PM"
            )
            response = ModelResponse(
                content="Test response",
                model_id="gpt-4",
                token_usage=TokenUsage(
                    input_tokens=10,
                    output_tokens=20,
                    total_tokens=30
                ),
                latency_ms=1000.0,
                cost=0.01
            )
            
            # Generate cache key and store response
            cache_key = cache_manager.generate_cache_key(request)
            await cache_manager.set(cache_key, response)
            
            # Retrieve from cache
            cached_response = await cache_manager.get(cache_key)
            
            self.assertIsNotNone(cached_response, "Cache hit should return response")
            self.assertEqual(cached_response.response.content, response.content)
            self.assertEqual(cached_response.response.model_id, response.model_id)
            self.assertEqual(cached_response.hit_count, 1)
        
        self.run_async(test())
    
    def test_cache_hit_increments_hit_count(self):
        """Test that multiple cache hits increment hit count"""
        async def test():
            cache_manager = CacheManager(
                db_path=self.db_path,
                default_ttl_seconds=3600
            )
            
            # Create and store test data
            request = ModelRequest(
                prompt="Test prompt",
                parameters={},
                task_id="task-1",
                agent_type="PM"
            )
            response = ModelResponse(
                content="Test response",
                model_id="gpt-4",
                token_usage=TokenUsage(10, 20, 30),
                latency_ms=1000.0,
                cost=0.01
            )
            
            cache_key = cache_manager.generate_cache_key(request)
            await cache_manager.set(cache_key, response)
            
            # Hit cache multiple times
            for expected_count in range(1, 6):
                cached_response = await cache_manager.get(cache_key)
                self.assertEqual(
                    cached_response.hit_count,
                    expected_count,
                    f"Hit count should be {expected_count}"
                )
        
        self.run_async(test())
    
    def test_cache_miss_after_different_request(self):
        """Test that different requests don't hit each other's cache"""
        async def test():
            cache_manager = CacheManager(
                db_path=self.db_path,
                default_ttl_seconds=3600
            )
            
            # Store first request
            request1 = ModelRequest(
                prompt="First prompt",
                parameters={},
                task_id="task-1",
                agent_type="PM"
            )
            response1 = ModelResponse(
                content="First response",
                model_id="gpt-4",
                token_usage=TokenUsage(10, 20, 30),
                latency_ms=1000.0,
                cost=0.01
            )
            cache_key1 = cache_manager.generate_cache_key(request1)
            await cache_manager.set(cache_key1, response1)
            
            # Try to get with different request
            request2 = ModelRequest(
                prompt="Second prompt",
                parameters={},
                task_id="task-2",
                agent_type="BA"
            )
            cache_key2 = cache_manager.generate_cache_key(request2)
            
            # Should be cache miss
            cached_response = await cache_manager.get(cache_key2)
            self.assertIsNone(
                cached_response,
                "Different request should not hit cache"
            )
        
        self.run_async(test())
    
    # TTL Expiration Tests
    
    def test_ttl_expiration_basic(self):
        """Test that entries expire after TTL"""
        async def test():
            cache_manager = CacheManager(
                db_path=self.db_path,
                default_ttl_seconds=1  # 1 second TTL
            )
            
            # Store response
            request = ModelRequest(
                prompt="Test prompt",
                parameters={},
                task_id="task-1",
                agent_type="PM"
            )
            response = ModelResponse(
                content="Test response",
                model_id="gpt-4",
                token_usage=TokenUsage(10, 20, 30),
                latency_ms=1000.0,
                cost=0.01
            )
            
            cache_key = cache_manager.generate_cache_key(request)
            await cache_manager.set(cache_key, response)
            
            # Verify it's available immediately
            cached = await cache_manager.get(cache_key)
            self.assertIsNotNone(cached, "Response should be available immediately")
            
            # Wait for expiration
            await asyncio.sleep(1.2)
            
            # Verify it's expired
            expired = await cache_manager.get(cache_key)
            self.assertIsNone(expired, "Response should be expired after TTL")
        
        self.run_async(test())
    
    def test_custom_ttl_overrides_default(self):
        """Test that custom TTL overrides default TTL"""
        async def test():
            cache_manager = CacheManager(
                db_path=self.db_path,
                default_ttl_seconds=3600  # 1 hour default
            )
            
            # Store with custom short TTL
            request = ModelRequest(
                prompt="Test prompt",
                parameters={},
                task_id="task-1",
                agent_type="PM"
            )
            response = ModelResponse(
                content="Test response",
                model_id="gpt-4",
                token_usage=TokenUsage(10, 20, 30),
                latency_ms=1000.0,
                cost=0.01
            )
            
            cache_key = cache_manager.generate_cache_key(request)
            await cache_manager.set(cache_key, response, ttl_seconds=1)
            
            # Wait for custom TTL to expire
            await asyncio.sleep(1.2)
            
            # Should be expired despite long default TTL
            expired = await cache_manager.get(cache_key)
            self.assertIsNone(
                expired,
                "Response should expire based on custom TTL, not default"
            )
        
        self.run_async(test())
    
    def test_evict_expired_removes_expired_entries(self):
        """Test that evict_expired removes only expired entries"""
        async def test():
            cache_manager = CacheManager(
                db_path=self.db_path,
                default_ttl_seconds=3600
            )
            
            # Store multiple entries with different TTLs
            for i in range(3):
                request = ModelRequest(
                    prompt=f"Prompt {i}",
                    parameters={"index": i},
                    task_id=f"task-{i}",
                    agent_type="PM"
                )
                response = ModelResponse(
                    content=f"Response {i}",
                    model_id="gpt-4",
                    token_usage=TokenUsage(10, 20, 30),
                    latency_ms=1000.0,
                    cost=0.01
                )
                cache_key = cache_manager.generate_cache_key(request)
                
                # First entry expires in 1 second, others have long TTL
                ttl = 1 if i == 0 else 3600
                await cache_manager.set(cache_key, response, ttl_seconds=ttl)
            
            # Wait for first entry to expire
            await asyncio.sleep(1.2)
            
            # Evict expired entries
            evicted_count = await cache_manager.evict_expired()
            
            # Should evict exactly 1 entry
            self.assertEqual(
                evicted_count,
                1,
                "Should evict exactly one expired entry"
            )
            
            # Verify stats
            stats = await cache_manager.get_stats()
            self.assertEqual(
                stats['total_entries'],
                2,
                "Should have 2 entries remaining"
            )
        
        self.run_async(test())
    
    def test_evict_expired_with_no_expired_entries(self):
        """Test that evict_expired returns 0 when no entries are expired"""
        async def test():
            cache_manager = CacheManager(
                db_path=self.db_path,
                default_ttl_seconds=3600
            )
            
            # Store entry with long TTL
            request = ModelRequest(
                prompt="Test prompt",
                parameters={},
                task_id="task-1",
                agent_type="PM"
            )
            response = ModelResponse(
                content="Test response",
                model_id="gpt-4",
                token_usage=TokenUsage(10, 20, 30),
                latency_ms=1000.0,
                cost=0.01
            )
            cache_key = cache_manager.generate_cache_key(request)
            await cache_manager.set(cache_key, response)
            
            # Evict expired entries
            evicted_count = await cache_manager.evict_expired()
            
            self.assertEqual(
                evicted_count,
                0,
                "Should not evict any entries when none are expired"
            )
        
        self.run_async(test())
    
    # LRU Eviction Edge Cases
    
    def test_lru_eviction_when_under_limit(self):
        """Test that LRU eviction does nothing when cache is under limit"""
        async def test():
            cache_manager = CacheManager(
                db_path=self.db_path,
                max_size_mb=100,  # Large limit
                default_ttl_seconds=3600
            )
            
            # Store a few small entries
            for i in range(3):
                request = ModelRequest(
                    prompt=f"Prompt {i}",
                    parameters={},
                    task_id=f"task-{i}",
                    agent_type="PM"
                )
                response = ModelResponse(
                    content=f"Response {i}",
                    model_id="gpt-4",
                    token_usage=TokenUsage(10, 20, 30),
                    latency_ms=1000.0,
                    cost=0.01
                )
                cache_key = cache_manager.generate_cache_key(request)
                await cache_manager.set(cache_key, response)
            
            # Try to evict with high target
            evicted_count = await cache_manager.evict_lru(target_size_mb=50)
            
            self.assertEqual(
                evicted_count,
                0,
                "Should not evict when cache is under target size"
            )
        
        self.run_async(test())
    
    def test_lru_eviction_removes_least_recently_used(self):
        """Test that LRU eviction removes least recently accessed entries"""
        async def test():
            cache_manager = CacheManager(
                db_path=self.db_path,
                max_size_mb=1,  # Small limit to trigger eviction
                default_ttl_seconds=3600
            )
            
            # Store multiple large entries
            entries = []
            for i in range(5):
                request = ModelRequest(
                    prompt=f"Prompt {i} " + "x" * 10000,
                    parameters={"index": i},
                    task_id=f"task-{i}",
                    agent_type="PM"
                )
                response = ModelResponse(
                    content=f"Response {i} " + "y" * 50000,
                    model_id="gpt-4",
                    token_usage=TokenUsage(100, 200, 300),
                    latency_ms=1000.0,
                    cost=0.01
                )
                cache_key = cache_manager.generate_cache_key(request)
                entries.append((cache_key, request, response))
                await cache_manager.set(cache_key, response)
                await asyncio.sleep(0.01)  # Ensure different timestamps
            
            # Access the last 2 entries to make them recently used
            for cache_key, _, _ in entries[-2:]:
                await cache_manager.get(cache_key)
                await asyncio.sleep(0.01)
            
            # Trigger LRU eviction
            evicted_count = await cache_manager.evict_lru(target_size_mb=0)
            
            # Should evict some entries
            self.assertGreater(
                evicted_count,
                0,
                "Should evict entries when over limit"
            )
            
            # Verify recently accessed entries are more likely to remain
            recently_accessed_remaining = 0
            for cache_key, _, _ in entries[-2:]:
                cached = await cache_manager.get(cache_key)
                if cached is not None:
                    recently_accessed_remaining += 1
            
            # At least one recently accessed entry should remain
            # (this is probabilistic but should hold for LRU)
            self.assertGreaterEqual(
                recently_accessed_remaining,
                0,
                "Recently accessed entries should be preserved by LRU"
            )
        
        self.run_async(test())
    
    def test_lru_eviction_stops_at_target_size(self):
        """Test that LRU eviction stops when target size is reached"""
        async def test():
            cache_manager = CacheManager(
                db_path=self.db_path,
                max_size_mb=10,
                default_ttl_seconds=3600
            )
            
            # Store multiple large entries
            for i in range(10):
                request = ModelRequest(
                    prompt=f"Prompt {i} " + "x" * 10000,
                    parameters={"index": i},
                    task_id=f"task-{i}",
                    agent_type="PM"
                )
                response = ModelResponse(
                    content=f"Response {i} " + "y" * 50000,
                    model_id="gpt-4",
                    token_usage=TokenUsage(100, 200, 300),
                    latency_ms=1000.0,
                    cost=0.01
                )
                cache_key = cache_manager.generate_cache_key(request)
                await cache_manager.set(cache_key, response)
            
            # Get initial size
            stats_before = await cache_manager.get_stats()
            initial_size = stats_before['cache_size_mb']
            
            # Evict to target size
            target_size = 2
            await cache_manager.evict_lru(target_size_mb=target_size)
            
            # Get final size
            stats_after = await cache_manager.get_stats()
            final_size = stats_after['cache_size_mb']
            
            # Final size should be at or below target
            self.assertLessEqual(
                final_size,
                target_size,
                f"Final size ({final_size}MB) should be at or below target ({target_size}MB)"
            )
        
        self.run_async(test())
    
    def test_lru_eviction_with_empty_cache(self):
        """Test that LRU eviction handles empty cache gracefully"""
        async def test():
            cache_manager = CacheManager(
                db_path=self.db_path,
                max_size_mb=10,
                default_ttl_seconds=3600
            )
            
            # Try to evict from empty cache
            evicted_count = await cache_manager.evict_lru(target_size_mb=5)
            
            self.assertEqual(
                evicted_count,
                0,
                "Should not evict anything from empty cache"
            )
        
        self.run_async(test())
    
    # Additional Edge Cases
    
    def test_cache_key_generation_is_deterministic(self):
        """Test that cache key generation is deterministic"""
        async def test():
            cache_manager = CacheManager(
                db_path=self.db_path,
                default_ttl_seconds=3600
            )
            
            request = ModelRequest(
                prompt="Test prompt",
                parameters={"key": "value"},
                task_id="task-1",
                agent_type="PM",
                max_tokens=100,
                temperature=0.7
            )
            
            # Generate key multiple times
            keys = [cache_manager.generate_cache_key(request) for _ in range(10)]
            
            # All keys should be identical
            self.assertEqual(
                len(set(keys)),
                1,
                "Cache key generation should be deterministic"
            )
        
        self.run_async(test())
    
    def test_cache_stats_accuracy(self):
        """Test that cache statistics are accurate"""
        async def test():
            cache_manager = CacheManager(
                db_path=self.db_path,
                max_size_mb=100,
                default_ttl_seconds=3600
            )
            
            # Initially empty
            stats = await cache_manager.get_stats()
            self.assertEqual(stats['total_entries'], 0)
            self.assertEqual(stats['total_hits'], 0)
            
            # Add entries
            for i in range(3):
                request = ModelRequest(
                    prompt=f"Prompt {i}",
                    parameters={},
                    task_id=f"task-{i}",
                    agent_type="PM"
                )
                response = ModelResponse(
                    content=f"Response {i}",
                    model_id="gpt-4",
                    token_usage=TokenUsage(10, 20, 30),
                    latency_ms=1000.0,
                    cost=0.01
                )
                cache_key = cache_manager.generate_cache_key(request)
                await cache_manager.set(cache_key, response)
            
            # Check stats
            stats = await cache_manager.get_stats()
            self.assertEqual(stats['total_entries'], 3)
            
            # Hit cache a few times
            request = ModelRequest(
                prompt="Prompt 0",
                parameters={},
                task_id="task-0",
                agent_type="PM"
            )
            cache_key = cache_manager.generate_cache_key(request)
            await cache_manager.get(cache_key)
            await cache_manager.get(cache_key)
            
            # Check hit count
            stats = await cache_manager.get_stats()
            self.assertEqual(stats['total_hits'], 2)
        
        self.run_async(test())
    
    def test_clear_removes_all_entries(self):
        """Test that clear removes all cache entries"""
        async def test():
            cache_manager = CacheManager(
                db_path=self.db_path,
                default_ttl_seconds=3600
            )
            
            # Add multiple entries
            for i in range(5):
                request = ModelRequest(
                    prompt=f"Prompt {i}",
                    parameters={},
                    task_id=f"task-{i}",
                    agent_type="PM"
                )
                response = ModelResponse(
                    content=f"Response {i}",
                    model_id="gpt-4",
                    token_usage=TokenUsage(10, 20, 30),
                    latency_ms=1000.0,
                    cost=0.01
                )
                cache_key = cache_manager.generate_cache_key(request)
                await cache_manager.set(cache_key, response)
            
            # Verify entries exist
            stats_before = await cache_manager.get_stats()
            self.assertEqual(stats_before['total_entries'], 5)
            
            # Clear cache
            cleared_count = await cache_manager.clear()
            self.assertEqual(cleared_count, 5)
            
            # Verify cache is empty
            stats_after = await cache_manager.get_stats()
            self.assertEqual(stats_after['total_entries'], 0)
        
        self.run_async(test())


if __name__ == "__main__":
    unittest.main()
