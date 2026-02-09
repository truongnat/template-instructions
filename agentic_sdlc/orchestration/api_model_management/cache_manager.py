"""
Cache Manager for API Model Management system.

This module provides response caching functionality to reduce API calls and costs.
It implements TTL-based expiration and LRU eviction strategies using SQLite storage.
"""

import aiosqlite
import hashlib
import json
import logging
from pathlib import Path
from datetime import datetime, timedelta
from typing import Optional, Dict, Any

from .models import ModelRequest, ModelResponse, CachedResponse, TokenUsage


logger = logging.getLogger(__name__)


class CacheManager:
    """
    Manages response caching with TTL and LRU eviction.
    
    Responsibilities:
    - Generate cache keys from requests
    - Check cache for existing responses
    - Store responses with TTL
    - Implement LRU eviction
    - Track cache hit rate
    """
    
    def __init__(
        self,
        db_path: Path,
        max_size_mb: int = 1000,
        default_ttl_seconds: int = 3600
    ):
        """
        Initialize cache manager.
        
        Args:
            db_path: Path to SQLite database file
            max_size_mb: Maximum cache size in megabytes
            default_ttl_seconds: Default time-to-live for cached responses
        """
        self.db_path = db_path
        self.max_size_mb = max_size_mb
        self.default_ttl_seconds = default_ttl_seconds
        
        logger.info(
            f"Initialized CacheManager with max_size={max_size_mb}MB, "
            f"default_ttl={default_ttl_seconds}s"
        )
    
    async def get(self, cache_key: str) -> Optional[CachedResponse]:
        """
        Retrieve cached response if it exists and hasn't expired.
        
        Args:
            cache_key: Cache key to lookup
            
        Returns:
            CachedResponse if found and valid, None otherwise
        """
        async with aiosqlite.connect(self.db_path) as db:
            cursor = await db.execute("""
                SELECT cache_key, model_id, request_hash, response_data,
                       cached_at, expires_at, hit_count, last_accessed
                FROM cached_responses
                WHERE cache_key = ? AND expires_at > ?
            """, (cache_key, datetime.now()))
            
            row = await cursor.fetchone()
            
            if row is None:
                logger.debug(f"Cache miss for key: {cache_key[:16]}...")
                return None
            
            # Parse the cached response
            cache_key_db, model_id, request_hash, response_data_json, \
                cached_at_str, expires_at_str, hit_count, last_accessed_str = row
            
            # Deserialize response data
            response_data = json.loads(response_data_json)
            
            # Reconstruct ModelResponse
            response = ModelResponse(
                content=response_data['content'],
                model_id=response_data['model_id'],
                token_usage=TokenUsage(**response_data['token_usage']),
                latency_ms=response_data['latency_ms'],
                cost=response_data['cost'],
                metadata=response_data.get('metadata', {})
            )
            
            # Update hit count and last accessed time
            await db.execute("""
                UPDATE cached_responses
                SET hit_count = hit_count + 1,
                    last_accessed = ?
                WHERE cache_key = ?
            """, (datetime.now(), cache_key))
            
            await db.commit()
            
            cached_response = CachedResponse(
                cache_key=cache_key_db,
                response=response,
                cached_at=datetime.fromisoformat(cached_at_str),
                expires_at=datetime.fromisoformat(expires_at_str),
                hit_count=hit_count + 1
            )
            
            logger.debug(
                f"Cache hit for key: {cache_key[:16]}... "
                f"(hit_count={hit_count + 1})"
            )
            
            return cached_response
    
    async def set(
        self,
        cache_key: str,
        response: ModelResponse,
        ttl_seconds: Optional[int] = None
    ) -> None:
        """
        Store response in cache with TTL.
        
        Args:
            cache_key: Cache key for the response
            response: ModelResponse to cache
            ttl_seconds: Time-to-live in seconds (uses default if None)
        """
        ttl = ttl_seconds if ttl_seconds is not None else self.default_ttl_seconds
        
        cached_at = datetime.now()
        expires_at = cached_at + timedelta(seconds=ttl)
        
        # Serialize response data
        response_data = {
            'content': response.content,
            'model_id': response.model_id,
            'token_usage': {
                'input_tokens': response.token_usage.input_tokens,
                'output_tokens': response.token_usage.output_tokens,
                'total_tokens': response.token_usage.total_tokens
            },
            'latency_ms': response.latency_ms,
            'cost': response.cost,
            'metadata': response.metadata
        }
        response_data_json = json.dumps(response_data)
        
        # Generate request hash (simplified - just use cache_key)
        request_hash = cache_key[:32]
        
        async with aiosqlite.connect(self.db_path) as db:
            # Insert or replace cached response
            await db.execute("""
                INSERT OR REPLACE INTO cached_responses
                (cache_key, model_id, request_hash, response_data, 
                 cached_at, expires_at, hit_count, last_accessed)
                VALUES (?, ?, ?, ?, ?, ?, 0, ?)
            """, (
                cache_key,
                response.model_id,
                request_hash,
                response_data_json,
                cached_at,
                expires_at,
                cached_at
            ))
            
            await db.commit()
        
        logger.debug(
            f"Cached response for key: {cache_key[:16]}... "
            f"(ttl={ttl}s, expires_at={expires_at})"
        )
        
        # Check if we need to evict entries
        await self._check_and_evict_if_needed()
    
    def generate_cache_key(self, request: ModelRequest) -> str:
        """
        Generate cache key from request.
        
        The cache key is a SHA256 hash of the model ID, prompt, and parameters.
        
        Args:
            request: ModelRequest to generate key for
            
        Returns:
            Cache key as hex string
        """
        # Create a deterministic string representation of the request
        key_components = {
            'model_id': request.task_id,  # Note: Using task_id as model context
            'prompt': request.prompt,
            'parameters': request.parameters,
            'max_tokens': request.max_tokens,
            'temperature': request.temperature
        }
        
        # Sort parameters to ensure consistent ordering
        key_string = json.dumps(key_components, sort_keys=True)
        
        # Generate SHA256 hash
        cache_key = hashlib.sha256(key_string.encode('utf-8')).hexdigest()
        
        return cache_key
    
    async def evict_expired(self) -> int:
        """
        Evict expired cache entries.
        
        Returns:
            Number of entries evicted
        """
        async with aiosqlite.connect(self.db_path) as db:
            cursor = await db.execute("""
                DELETE FROM cached_responses
                WHERE expires_at <= ?
            """, (datetime.now(),))
            
            evicted_count = cursor.rowcount
            await db.commit()
        
        if evicted_count > 0:
            logger.info(f"Evicted {evicted_count} expired cache entries")
        
        return evicted_count
    
    async def evict_lru(self, target_size_mb: int) -> int:
        """
        Evict least recently used entries until cache is below target size.
        
        Args:
            target_size_mb: Target cache size in megabytes
            
        Returns:
            Number of entries evicted
        """
        current_size_mb = await self._get_cache_size_mb()
        
        if current_size_mb <= target_size_mb:
            logger.debug(
                f"Cache size ({current_size_mb:.2f}MB) is below target "
                f"({target_size_mb}MB), no eviction needed"
            )
            return 0
        
        # Calculate how many entries to evict (rough estimate)
        # We'll evict entries until we're below target
        evicted_count = 0
        
        async with aiosqlite.connect(self.db_path) as db:
            while current_size_mb > target_size_mb:
                # Delete the least recently accessed entry
                cursor = await db.execute("""
                    DELETE FROM cached_responses
                    WHERE cache_key IN (
                        SELECT cache_key FROM cached_responses
                        ORDER BY last_accessed ASC
                        LIMIT 100
                    )
                """)
                
                deleted = cursor.rowcount
                if deleted == 0:
                    break
                
                evicted_count += deleted
                await db.commit()
                
                # Recalculate size
                current_size_mb = await self._get_cache_size_mb()
        
        logger.info(
            f"Evicted {evicted_count} LRU cache entries "
            f"(new size: {current_size_mb:.2f}MB)"
        )
        
        return evicted_count
    
    async def _get_cache_size_mb(self) -> float:
        """
        Get current cache size in megabytes.
        
        Returns:
            Cache size in MB
        """
        async with aiosqlite.connect(self.db_path) as db:
            cursor = await db.execute("""
                SELECT SUM(LENGTH(response_data)) as total_size
                FROM cached_responses
            """)
            
            row = await cursor.fetchone()
            total_bytes = row[0] if row[0] is not None else 0
            
            return total_bytes / (1024 * 1024)
    
    async def _check_and_evict_if_needed(self) -> None:
        """Check cache size and evict if needed."""
        current_size_mb = await self._get_cache_size_mb()
        
        if current_size_mb > self.max_size_mb:
            logger.info(
                f"Cache size ({current_size_mb:.2f}MB) exceeds max "
                f"({self.max_size_mb}MB), triggering LRU eviction"
            )
            await self.evict_lru(int(self.max_size_mb * 0.9))  # Evict to 90% of max
    
    async def get_stats(self) -> Dict[str, Any]:
        """
        Get cache statistics.
        
        Returns:
            Dictionary with cache statistics
        """
        async with aiosqlite.connect(self.db_path) as db:
            # Get total entries
            cursor = await db.execute("SELECT COUNT(*) FROM cached_responses")
            total_entries = (await cursor.fetchone())[0]
            
            # Get total hits
            cursor = await db.execute("SELECT SUM(hit_count) FROM cached_responses")
            total_hits = (await cursor.fetchone())[0] or 0
            
            # Get cache size
            cache_size_mb = await self._get_cache_size_mb()
            
            # Get expired entries count
            cursor = await db.execute("""
                SELECT COUNT(*) FROM cached_responses
                WHERE expires_at <= ?
            """, (datetime.now(),))
            expired_entries = (await cursor.fetchone())[0]
        
        return {
            'total_entries': total_entries,
            'total_hits': total_hits,
            'cache_size_mb': round(cache_size_mb, 2),
            'max_size_mb': self.max_size_mb,
            'utilization_percent': round((cache_size_mb / self.max_size_mb) * 100, 2),
            'expired_entries': expired_entries
        }
    
    async def clear(self) -> int:
        """
        Clear all cache entries.
        
        Returns:
            Number of entries cleared
        """
        async with aiosqlite.connect(self.db_path) as db:
            cursor = await db.execute("DELETE FROM cached_responses")
            cleared_count = cursor.rowcount
            await db.commit()
        
        logger.info(f"Cleared {cleared_count} cache entries")
        return cleared_count
