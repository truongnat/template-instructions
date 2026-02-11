"""
Validation utilities for SDLC Kit.

Provides common validation functions for data types, formats, and constraints.
"""

import re
from typing import Any, List, Dict, Optional
from pathlib import Path


def is_valid_email(email: str) -> bool:
    """
    Validate email address format.
    
    Args:
        email: Email address to validate
        
    Returns:
        True if valid email format, False otherwise
    """
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return bool(re.match(pattern, email))


def is_valid_url(url: str) -> bool:
    """
    Validate URL format.
    
    Args:
        url: URL to validate
        
    Returns:
        True if valid URL format, False otherwise
    """
    pattern = r'^https?://[^\s/$.?#].[^\s]*$'
    return bool(re.match(pattern, url))


def is_valid_semver(version: str) -> bool:
    """
    Validate semantic version format (e.g., 1.0.0).
    
    Args:
        version: Version string to validate
        
    Returns:
        True if valid semver format, False otherwise
    """
    pattern = r'^\d+\.\d+\.\d+$'
    return bool(re.match(pattern, version))


def is_valid_path(path: str) -> bool:
    """
    Validate file/directory path.
    
    Args:
        path: Path to validate
        
    Returns:
        True if path exists, False otherwise
    """
    return Path(path).exists()


def is_non_empty_string(value: Any) -> bool:
    """
    Check if value is a non-empty string.
    
    Args:
        value: Value to check
        
    Returns:
        True if non-empty string, False otherwise
    """
    return isinstance(value, str) and len(value.strip()) > 0


def is_positive_integer(value: Any) -> bool:
    """
    Check if value is a positive integer.
    
    Args:
        value: Value to check
        
    Returns:
        True if positive integer, False otherwise
    """
    return isinstance(value, int) and value > 0


def is_valid_dict(value: Any, required_keys: Optional[List[str]] = None) -> bool:
    """
    Check if value is a valid dictionary with required keys.
    
    Args:
        value: Value to check
        required_keys: List of required keys (optional)
        
    Returns:
        True if valid dictionary with required keys, False otherwise
    """
    if not isinstance(value, dict):
        return False
    
    if required_keys:
        return all(key in value for key in required_keys)
    
    return True


def is_valid_list(value: Any, min_length: int = 0, max_length: Optional[int] = None) -> bool:
    """
    Check if value is a valid list with length constraints.
    
    Args:
        value: Value to check
        min_length: Minimum list length (default: 0)
        max_length: Maximum list length (optional)
        
    Returns:
        True if valid list within length constraints, False otherwise
    """
    if not isinstance(value, list):
        return False
    
    if len(value) < min_length:
        return False
    
    if max_length is not None and len(value) > max_length:
        return False
    
    return True


def validate_required_fields(data: Dict[str, Any], required_fields: List[str]) -> tuple[bool, List[str]]:
    """
    Validate that all required fields are present in data.
    
    Args:
        data: Dictionary to validate
        required_fields: List of required field names
        
    Returns:
        Tuple of (is_valid, missing_fields)
    """
    missing_fields = [field for field in required_fields if field not in data]
    return len(missing_fields) == 0, missing_fields


def validate_field_types(data: Dict[str, Any], type_map: Dict[str, type]) -> tuple[bool, List[str]]:
    """
    Validate that fields have correct types.
    
    Args:
        data: Dictionary to validate
        type_map: Dictionary mapping field names to expected types
        
    Returns:
        Tuple of (is_valid, invalid_fields)
    """
    invalid_fields = []
    
    for field, expected_type in type_map.items():
        if field in data and not isinstance(data[field], expected_type):
            invalid_fields.append(f"{field} (expected {expected_type.__name__}, got {type(data[field]).__name__})")
    
    return len(invalid_fields) == 0, invalid_fields


def sanitize_string(value: str, max_length: Optional[int] = None) -> str:
    """
    Sanitize string by removing dangerous characters.
    
    Args:
        value: String to sanitize
        max_length: Maximum length (optional)
        
    Returns:
        Sanitized string
    """
    # Remove null bytes and control characters
    sanitized = ''.join(char for char in value if ord(char) >= 32 or char in '\n\r\t')
    
    # Truncate if max_length specified
    if max_length and len(sanitized) > max_length:
        sanitized = sanitized[:max_length]
    
    return sanitized


def validate_range(value: Any, min_value: Optional[Any] = None, max_value: Optional[Any] = None) -> bool:
    """
    Validate that value is within specified range.
    
    Args:
        value: Value to validate
        min_value: Minimum value (optional)
        max_value: Maximum value (optional)
        
    Returns:
        True if value is within range, False otherwise
    """
    if min_value is not None and value < min_value:
        return False
    
    if max_value is not None and value > max_value:
        return False
    
    return True


__all__ = [
    'is_valid_email',
    'is_valid_url',
    'is_valid_semver',
    'is_valid_path',
    'is_non_empty_string',
    'is_positive_integer',
    'is_valid_dict',
    'is_valid_list',
    'validate_required_fields',
    'validate_field_types',
    'sanitize_string',
    'validate_range',
]
