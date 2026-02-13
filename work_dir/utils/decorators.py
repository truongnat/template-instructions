"""
Common decorators for SDLC Kit.

Provides reusable decorators for timing, caching, retry logic, and more.
"""

import time
import functools
from typing import Callable, Any, Optional


def timer(func: Callable) -> Callable:
    """
    Decorator to measure function execution time.
    
    Usage:
        @timer
        def my_function():
            pass
    """
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        start_time = time.time()
        result = func(*args, **kwargs)
        end_time = time.time()
        duration = end_time - start_time
        print(f"{func.__name__} took {duration:.4f} seconds")
        return result
    return wrapper


def retry(max_attempts: int = 3, delay: float = 1.0, exceptions: tuple = (Exception,)):
    """
    Decorator to retry function on failure.
    
    Args:
        max_attempts: Maximum number of retry attempts
        delay: Delay between retries in seconds
        exceptions: Tuple of exceptions to catch
        
    Usage:
        @retry(max_attempts=3, delay=2.0)
        def my_function():
            pass
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            last_exception = None
            for attempt in range(max_attempts):
                try:
                    return func(*args, **kwargs)
                except exceptions as e:
                    last_exception = e
                    if attempt < max_attempts - 1:
                        time.sleep(delay)
                        print(f"Retry {attempt + 1}/{max_attempts} for {func.__name__}")
            raise last_exception
        return wrapper
    return decorator


def deprecated(message: Optional[str] = None):
    """
    Decorator to mark functions as deprecated.
    
    Args:
        message: Optional deprecation message
        
    Usage:
        @deprecated("Use new_function instead")
        def old_function():
            pass
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            warning_msg = f"{func.__name__} is deprecated"
            if message:
                warning_msg += f": {message}"
            print(f"Warning: {warning_msg}")
            return func(*args, **kwargs)
        return wrapper
    return decorator


def memoize(func: Callable) -> Callable:
    """
    Decorator to cache function results.
    
    Usage:
        @memoize
        def expensive_function(x):
            return x ** 2
    """
    cache = {}
    
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        # Create cache key from args and kwargs
        key = str(args) + str(sorted(kwargs.items()))
        
        if key not in cache:
            cache[key] = func(*args, **kwargs)
        
        return cache[key]
    
    return wrapper


def validate_args(**validators):
    """
    Decorator to validate function arguments.
    
    Args:
        validators: Keyword arguments mapping parameter names to validation functions
        
    Usage:
        @validate_args(x=lambda x: x > 0, y=lambda y: isinstance(y, str))
        def my_function(x, y):
            pass
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            # Get function signature
            import inspect
            sig = inspect.signature(func)
            bound_args = sig.bind(*args, **kwargs)
            bound_args.apply_defaults()
            
            # Validate arguments
            for param_name, validator in validators.items():
                if param_name in bound_args.arguments:
                    value = bound_args.arguments[param_name]
                    if not validator(value):
                        raise ValueError(f"Validation failed for parameter '{param_name}' with value {value}")
            
            return func(*args, **kwargs)
        return wrapper
    return decorator


def singleton(cls):
    """
    Decorator to make a class a singleton.
    
    Usage:
        @singleton
        class MyClass:
            pass
    """
    instances = {}
    
    @functools.wraps(cls)
    def get_instance(*args, **kwargs):
        if cls not in instances:
            instances[cls] = cls(*args, **kwargs)
        return instances[cls]
    
    return get_instance


__all__ = [
    'timer',
    'retry',
    'deprecated',
    'memoize',
    'validate_args',
    'singleton',
]
