"""
Helper utilities for the Multi-Agent Orchestration System

This module provides common utility functions used throughout the system.
"""

import json
import time
import asyncio
import functools
from datetime import datetime, timedelta
from typing import Any, Callable, Dict, Optional, TypeVar, Union
from uuid import uuid4
import signal

T = TypeVar('T')


def generate_id() -> str:
    """Generate a unique identifier"""
    return str(uuid4())


def format_duration(seconds: float) -> str:
    """Format duration in seconds to human-readable string"""
    if seconds < 60:
        return f"{seconds:.1f}s"
    elif seconds < 3600:
        minutes = seconds / 60
        return f"{minutes:.1f}m"
    else:
        hours = seconds / 3600
        return f"{hours:.1f}h"


def safe_json_serialize(obj: Any) -> str:
    """Safely serialize object to JSON, handling non-serializable types"""
    def default_serializer(o):
        if isinstance(o, datetime):
            return o.isoformat()
        elif hasattr(o, '__dict__'):
            return o.__dict__
        elif hasattr(o, '_asdict'):  # namedtuple
            return o._asdict()
        else:
            return str(o)
    
    try:
        return json.dumps(obj, default=default_serializer, indent=2)
    except Exception as e:
        return f"<Serialization Error: {str(e)}>"


def retry_with_backoff(
    max_retries: int = 3,
    base_delay: float = 1.0,
    max_delay: float = 60.0,
    backoff_factor: float = 2.0,
    exceptions: tuple = (Exception,)
):
    """Decorator for retrying functions with exponential backoff"""
    def decorator(func: Callable[..., T]) -> Callable[..., T]:
        @functools.wraps(func)
        def wrapper(*args, **kwargs) -> T:
            last_exception = None
            
            for attempt in range(max_retries + 1):
                try:
                    return func(*args, **kwargs)
                except exceptions as e:
                    last_exception = e
                    
                    if attempt == max_retries:
                        break
                    
                    # Calculate delay with exponential backoff
                    delay = min(base_delay * (backoff_factor ** attempt), max_delay)
                    time.sleep(delay)
            
            # Re-raise the last exception if all retries failed
            raise last_exception
        
        return wrapper
    return decorator


def timeout_after(seconds: float):
    """Decorator to add timeout to function execution"""
    def decorator(func: Callable[..., T]) -> Callable[..., T]:
        @functools.wraps(func)
        def wrapper(*args, **kwargs) -> T:
            # For async functions
            if asyncio.iscoroutinefunction(func):
                async def async_wrapper():
                    return await asyncio.wait_for(func(*args, **kwargs), timeout=seconds)
                return async_wrapper()
            
            # For sync functions using signal (Unix only)
            def timeout_handler(signum, frame):
                raise TimeoutError(f"Function {func.__name__} timed out after {seconds} seconds")
            
            # Set up signal handler
            old_handler = signal.signal(signal.SIGALRM, timeout_handler)
            signal.alarm(int(seconds))
            
            try:
                result = func(*args, **kwargs)
                signal.alarm(0)  # Cancel the alarm
                return result
            finally:
                signal.signal(signal.SIGALRM, old_handler)
        
        return wrapper
    return decorator


def calculate_similarity(text1: str, text2: str) -> float:
    """Calculate simple similarity between two texts (0.0 to 1.0)"""
    if not text1 or not text2:
        return 0.0
    
    # Simple word-based similarity
    words1 = set(text1.lower().split())
    words2 = set(text2.lower().split())
    
    if not words1 or not words2:
        return 0.0
    
    intersection = words1.intersection(words2)
    union = words1.union(words2)
    
    return len(intersection) / len(union)


def truncate_string(text: str, max_length: int = 100, suffix: str = "...") -> str:
    """Truncate string to maximum length with suffix"""
    if len(text) <= max_length:
        return text
    
    return text[:max_length - len(suffix)] + suffix


def deep_merge_dicts(dict1: Dict[str, Any], dict2: Dict[str, Any]) -> Dict[str, Any]:
    """Deep merge two dictionaries"""
    result = dict1.copy()
    
    for key, value in dict2.items():
        if key in result and isinstance(result[key], dict) and isinstance(value, dict):
            result[key] = deep_merge_dicts(result[key], value)
        else:
            result[key] = value
    
    return result


def validate_email(email: str) -> bool:
    """Simple email validation"""
    import re
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None


def sanitize_filename(filename: str) -> str:
    """Sanitize filename by removing invalid characters"""
    import re
    # Remove invalid characters
    sanitized = re.sub(r'[<>:"/\\|?*]', '_', filename)
    # Remove leading/trailing spaces and dots
    sanitized = sanitized.strip(' .')
    # Limit length
    return sanitized[:255]


def get_memory_usage() -> Dict[str, float]:
    """Get current memory usage information"""
    try:
        import psutil
        process = psutil.Process()
        memory_info = process.memory_info()
        
        return {
            "rss_mb": memory_info.rss / 1024 / 1024,  # Resident Set Size
            "vms_mb": memory_info.vms / 1024 / 1024,  # Virtual Memory Size
            "percent": process.memory_percent()
        }
    except ImportError:
        return {"error": "psutil not available"}


def get_cpu_usage() -> float:
    """Get current CPU usage percentage"""
    try:
        import psutil
        return psutil.cpu_percent(interval=1)
    except ImportError:
        return 0.0


class Timer:
    """Context manager for timing operations"""
    
    def __init__(self, name: str = "Operation"):
        self.name = name
        self.start_time = None
        self.end_time = None
        self.duration = None
    
    def __enter__(self):
        self.start_time = time.time()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.end_time = time.time()
        self.duration = self.end_time - self.start_time
    
    def __str__(self):
        if self.duration is not None:
            return f"{self.name}: {format_duration(self.duration)}"
        return f"{self.name}: Not completed"


class RateLimiter:
    """Simple rate limiter implementation"""
    
    def __init__(self, max_calls: int, time_window: float):
        self.max_calls = max_calls
        self.time_window = time_window
        self.calls = []
    
    def can_proceed(self) -> bool:
        """Check if a call can proceed without exceeding rate limit"""
        now = time.time()
        
        # Remove old calls outside the time window
        self.calls = [call_time for call_time in self.calls if now - call_time < self.time_window]
        
        return len(self.calls) < self.max_calls
    
    def record_call(self):
        """Record a call"""
        self.calls.append(time.time())
    
    def wait_time(self) -> float:
        """Get time to wait before next call can proceed"""
        if self.can_proceed():
            return 0.0
        
        # Time until the oldest call expires
        oldest_call = min(self.calls)
        return self.time_window - (time.time() - oldest_call)


def chunk_list(lst: list, chunk_size: int) -> list:
    """Split a list into chunks of specified size"""
    return [lst[i:i + chunk_size] for i in range(0, len(lst), chunk_size)]


def flatten_dict(d: Dict[str, Any], parent_key: str = '', sep: str = '.') -> Dict[str, Any]:
    """Flatten a nested dictionary"""
    items = []
    for k, v in d.items():
        new_key = f"{parent_key}{sep}{k}" if parent_key else k
        if isinstance(v, dict):
            items.extend(flatten_dict(v, new_key, sep=sep).items())
        else:
            items.append((new_key, v))
    return dict(items)


def unflatten_dict(d: Dict[str, Any], sep: str = '.') -> Dict[str, Any]:
    """Unflatten a dictionary with dot-separated keys"""
    result = {}
    for key, value in d.items():
        keys = key.split(sep)
        current = result
        for k in keys[:-1]:
            if k not in current:
                current[k] = {}
            current = current[k]
        current[keys[-1]] = value
    return result