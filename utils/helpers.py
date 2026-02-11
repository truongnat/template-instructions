"""
General helper utilities for SDLC Kit.

Provides miscellaneous utility functions for common operations.
"""

import hashlib
import json
from datetime import datetime
from typing import Any, Dict, List, Optional, Union
from pathlib import Path


def get_timestamp(format: str = "%Y-%m-%d %H:%M:%S") -> str:
    """
    Get current timestamp as formatted string.
    
    Args:
        format: Datetime format string (default: YYYY-MM-DD HH:MM:SS)
        
    Returns:
        Formatted timestamp string
    """
    return datetime.now().strftime(format)


def get_iso_timestamp() -> str:
    """
    Get current timestamp in ISO format.
    
    Returns:
        ISO formatted timestamp string
    """
    return datetime.now().isoformat()


def format_duration(seconds: float) -> str:
    """
    Format duration in seconds to human-readable string.
    
    Args:
        seconds: Duration in seconds
        
    Returns:
        Formatted duration string (e.g., "2h 30m", "45s")
    """
    if seconds < 60:
        return f"{int(seconds)}s"
    elif seconds < 3600:
        minutes = int(seconds // 60)
        secs = int(seconds % 60)
        return f"{minutes}m {secs}s" if secs > 0 else f"{minutes}m"
    else:
        hours = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)
        return f"{hours}h {minutes}m" if minutes > 0 else f"{hours}h"


def truncate_string(text: str, max_length: int = 80, suffix: str = "...") -> str:
    """
    Truncate string to maximum length with suffix.
    
    Args:
        text: String to truncate
        max_length: Maximum length (default: 80)
        suffix: Suffix to append (default: "...")
        
    Returns:
        Truncated string
    """
    if len(text) <= max_length:
        return text
    return text[:max_length - len(suffix)] + suffix


def calculate_hash(data: Union[str, bytes], algorithm: str = "sha256") -> str:
    """
    Calculate hash of data.
    
    Args:
        data: Data to hash (string or bytes)
        algorithm: Hash algorithm (default: sha256)
        
    Returns:
        Hex digest of hash
    """
    if isinstance(data, str):
        data = data.encode('utf-8')
    
    hash_obj = hashlib.new(algorithm)
    hash_obj.update(data)
    return hash_obj.hexdigest()


def deep_merge(dict1: Dict, dict2: Dict) -> Dict:
    """
    Deep merge two dictionaries.
    
    Args:
        dict1: First dictionary
        dict2: Second dictionary (takes precedence)
        
    Returns:
        Merged dictionary
    """
    result = dict1.copy()
    
    for key, value in dict2.items():
        if key in result and isinstance(result[key], dict) and isinstance(value, dict):
            result[key] = deep_merge(result[key], value)
        else:
            result[key] = value
    
    return result


def flatten_dict(d: Dict, parent_key: str = '', sep: str = '.') -> Dict:
    """
    Flatten nested dictionary.
    
    Args:
        d: Dictionary to flatten
        parent_key: Parent key prefix (default: '')
        sep: Separator for keys (default: '.')
        
    Returns:
        Flattened dictionary
    """
    items = []
    for k, v in d.items():
        new_key = f"{parent_key}{sep}{k}" if parent_key else k
        if isinstance(v, dict):
            items.extend(flatten_dict(v, new_key, sep=sep).items())
        else:
            items.append((new_key, v))
    return dict(items)


def chunk_list(lst: List, chunk_size: int) -> List[List]:
    """
    Split list into chunks of specified size.
    
    Args:
        lst: List to chunk
        chunk_size: Size of each chunk
        
    Returns:
        List of chunks
    """
    return [lst[i:i + chunk_size] for i in range(0, len(lst), chunk_size)]


def safe_json_loads(json_str: str, default: Any = None) -> Any:
    """
    Safely parse JSON string with fallback.
    
    Args:
        json_str: JSON string to parse
        default: Default value if parsing fails
        
    Returns:
        Parsed JSON or default value
    """
    try:
        return json.loads(json_str)
    except (json.JSONDecodeError, TypeError):
        return default


def safe_json_dumps(obj: Any, default: str = "{}") -> str:
    """
    Safely serialize object to JSON with fallback.
    
    Args:
        obj: Object to serialize
        default: Default value if serialization fails
        
    Returns:
        JSON string or default value
    """
    try:
        return json.dumps(obj, indent=2)
    except (TypeError, ValueError):
        return default


def ensure_list(value: Any) -> List:
    """
    Ensure value is a list.
    
    Args:
        value: Value to convert
        
    Returns:
        List containing value, or value if already a list
    """
    if value is None:
        return []
    if isinstance(value, list):
        return value
    return [value]


def remove_duplicates(lst: List, key: Optional[callable] = None) -> List:
    """
    Remove duplicates from list while preserving order.
    
    Args:
        lst: List to deduplicate
        key: Optional function to extract comparison key
        
    Returns:
        List with duplicates removed
    """
    seen = set()
    result = []
    
    for item in lst:
        item_key = key(item) if key else item
        if item_key not in seen:
            seen.add(item_key)
            result.append(item)
    
    return result


def safe_divide(numerator: float, denominator: float, default: float = 0.0) -> float:
    """
    Safely divide with fallback for division by zero.
    
    Args:
        numerator: Numerator
        denominator: Denominator
        default: Default value if division by zero (default: 0.0)
        
    Returns:
        Result of division or default value
    """
    try:
        return numerator / denominator
    except ZeroDivisionError:
        return default


__all__ = [
    'get_timestamp',
    'get_iso_timestamp',
    'format_duration',
    'truncate_string',
    'calculate_hash',
    'deep_merge',
    'flatten_dict',
    'chunk_list',
    'safe_json_loads',
    'safe_json_dumps',
    'ensure_list',
    'remove_duplicates',
    'safe_divide',
]
