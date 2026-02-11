"""
Ví Dụ 15: Caching and Performance (Caching và Tối Ưu Performance)

Setup Instructions:
1. Cài đặt: pip install agentic-sdlc redis
2. Cấu hình Redis (optional)
3. Chạy: python 15-caching.py

Dependencies:
- agentic-sdlc>=3.0.0
- redis (optional)

Expected Output:
- In-memory caching
- Redis caching
- Cache invalidation
- Performance improvements
"""

import os
import time
from functools import lru_cache
from dotenv import load_dotenv

load_dotenv()


def in_memory_caching():
    """In-memory caching với LRU cache."""
    
    @lru_cache(maxsize=128)
    def expensive_computation(n: int) -> int:
        """Simulate expensive computation."""
        print(f"  Computing for n={n}...")
        time.sleep(0.5)  # Simulate delay
        return n * n
    
    print("✓ In-memory caching example")
    
    # First call - cache miss
    start = time.time()
    result1 = expensive_computation(10)
    time1 = time.time() - start
    print(f"  First call: {result1} (took {time1:.3f}s)")
    
    # Second call - cache hit
    start = time.time()
    result2 = expensive_computation(10)
    time2 = time.time() - start
    print(f"  Second call: {result2} (took {time2:.3f}s)")
    
    print(f"  Speedup: {time1/time2:.1f}x faster")
    
    # Cache info
    info = expensive_computation.cache_info()
    print(f"  Cache stats: hits={info.hits}, misses={info.misses}")


def redis_caching():
    """Redis-based caching."""
    import redis
    import json
    
    # Connect to Redis
    r = redis.Redis(host='localhost', port=6379, db=0, decode_responses=True)
    
    print("\n✓ Redis caching example")
    
    def get_cached_data(key: str):
        """Get data from cache."""
        cached = r.get(key)
        if cached:
            print(f"  Cache HIT for key: {key}")
            return json.loads(cached)
        print(f"  Cache MISS for key: {key}")
        return None
    
    def set_cached_data(key: str, data: dict, ttl: int = 3600):
        """Set data in cache."""
        r.setex(key, ttl, json.dumps(data))
        print(f"  Cached data for key: {key} (TTL: {ttl}s)")
    
    # Example usage
    key = "user:123"
    
    # First access - cache miss
    data = get_cached_data(key)
    if not data:
        # Fetch from "database"
        data = {"id": 123, "name": "John Doe", "email": "john@example.com"}
        set_cached_data(key, data)
    
    # Second access - cache hit
    data = get_cached_data(key)
    print(f"  Data: {data}")


def cache_decorator():
    """Custom cache decorator."""
    import hashlib
    import pickle
    
    class SimpleCache:
        def __init__(self):
            self.cache = {}
        
        def get_key(self, func, args, kwargs):
            """Generate cache key."""
            key_data = f"{func.__name__}:{args}:{kwargs}"
            return hashlib.md5(key_data.encode()).hexdigest()
        
        def __call__(self, func):
            def wrapper(*args, **kwargs):
                key = self.get_key(func, args, kwargs)
                
                if key in self.cache:
                    print(f"  Cache HIT: {func.__name__}")
                    return self.cache[key]
                
                print(f"  Cache MISS: {func.__name__}")
                result = func(*args, **kwargs)
                self.cache[key] = result
                return result
            
            return wrapper
    
    cache = SimpleCache()
    
    @cache
    def fetch_user_data(user_id: int):
        """Simulate fetching user data."""
        time.sleep(0.3)
        return {"id": user_id, "name": f"User {user_id}"}
    
    print("\n✓ Custom cache decorator")
    
    # First call
    start = time.time()
    data1 = fetch_user_data(1)
    time1 = time.time() - start
    print(f"  First call: {time1:.3f}s")
    
    # Second call (cached)
    start = time.time()
    data2 = fetch_user_data(1)
    time2 = time.time() - start
    print(f"  Second call: {time2:.3f}s")


def cache_invalidation():
    """Cache invalidation strategies."""
    
    class CacheManager:
        def __init__(self):
            self.cache = {}
            self.timestamps = {}
        
        def set(self, key: str, value: any, ttl: int = None):
            """Set cache with optional TTL."""
            self.cache[key] = value
            if ttl:
                self.timestamps[key] = time.time() + ttl
        
        def get(self, key: str):
            """Get from cache with TTL check."""
            if key not in self.cache:
                return None
            
            # Check TTL
            if key in self.timestamps:
                if time.time() > self.timestamps[key]:
                    # Expired
                    del self.cache[key]
                    del self.timestamps[key]
                    return None
            
            return self.cache[key]
        
        def invalidate(self, key: str):
            """Invalidate specific key."""
            if key in self.cache:
                del self.cache[key]
            if key in self.timestamps:
                del self.timestamps[key]
        
        def invalidate_pattern(self, pattern: str):
            """Invalidate keys matching pattern."""
            keys_to_delete = [k for k in self.cache.keys() if pattern in k]
            for key in keys_to_delete:
                self.invalidate(key)
        
        def clear(self):
            """Clear all cache."""
            self.cache.clear()
            self.timestamps.clear()
    
    print("\n✓ Cache invalidation")
    
    manager = CacheManager()
    
    # Set some data
    manager.set("user:1", {"name": "Alice"})
    manager.set("user:2", {"name": "Bob"})
    manager.set("post:1", {"title": "Hello"})
    
    print(f"  Cached items: {len(manager.cache)}")
    
    # Invalidate specific key
    manager.invalidate("user:1")
    print(f"  After invalidating user:1: {len(manager.cache)}")
    
    # Invalidate by pattern
    manager.invalidate_pattern("user:")
    print(f"  After invalidating user:*: {len(manager.cache)}")


def performance_comparison():
    """Compare performance with/without caching."""
    
    def slow_function(n: int) -> int:
        """Slow function without caching."""
        time.sleep(0.1)
        return n * n
    
    @lru_cache(maxsize=128)
    def fast_function(n: int) -> int:
        """Fast function with caching."""
        time.sleep(0.1)
        return n * n
    
    print("\n✓ Performance comparison")
    
    # Without caching
    start = time.time()
    for i in range(10):
        slow_function(5)  # Same input
    time_without_cache = time.time() - start
    
    # With caching
    start = time.time()
    for i in range(10):
        fast_function(5)  # Same input
    time_with_cache = time.time() - start
    
    print(f"  Without cache: {time_without_cache:.3f}s")
    print(f"  With cache: {time_with_cache:.3f}s")
    print(f"  Speedup: {time_without_cache/time_with_cache:.1f}x")


if __name__ == "__main__":
    print("=" * 60)
    print("VÍ DỤ: CACHING AND PERFORMANCE")
    print("=" * 60)
    
    in_memory_caching()
    # redis_caching()  # Uncomment if Redis is available
    cache_decorator()
    cache_invalidation()
    performance_comparison()
    
    print("\n" + "=" * 60)
    print("✓ Hoàn thành!")
    print("=" * 60)
