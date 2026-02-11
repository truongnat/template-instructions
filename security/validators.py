"""
Input validation and sanitization utilities for SDLC Kit.

Provides protection against common injection attacks and validates input formats.
"""

import re
from typing import Optional, List
from html import escape


class ValidationError(Exception):
    """Raised when input validation fails."""
    pass


def sanitize_sql(input_str: str) -> str:
    """
    Sanitize input to prevent SQL injection attacks.
    
    Args:
        input_str: Input string to sanitize
        
    Returns:
        Sanitized string safe for SQL queries
        
    Note:
        This is a basic sanitizer. Always use parameterized queries
        for database operations when possible.
    """
    if not isinstance(input_str, str):
        raise ValidationError(f"Expected string, got {type(input_str).__name__}")
    
    # Remove or escape dangerous SQL characters and keywords
    dangerous_patterns = [
        r"--",  # SQL comments
        r";",   # Statement separator
        r"'",   # String delimiter
        r'"',   # String delimiter
        r"\\",  # Escape character
    ]
    
    sanitized = input_str
    for pattern in dangerous_patterns:
        sanitized = sanitized.replace(pattern, "")
    
    # Remove common SQL injection keywords
    sql_keywords = [
        "DROP", "DELETE", "INSERT", "UPDATE", "EXEC", "EXECUTE",
        "UNION", "SELECT", "CREATE", "ALTER", "TRUNCATE"
    ]
    
    for keyword in sql_keywords:
        # Case-insensitive replacement
        sanitized = re.sub(
            rf"\b{keyword}\b",
            "",
            sanitized,
            flags=re.IGNORECASE
        )
    
    return sanitized.strip()


def sanitize_xss(input_str: str) -> str:
    """
    Sanitize input to prevent XSS (Cross-Site Scripting) attacks.
    
    Args:
        input_str: Input string to sanitize
        
    Returns:
        Sanitized string safe for HTML output
    """
    if not isinstance(input_str, str):
        raise ValidationError(f"Expected string, got {type(input_str).__name__}")
    
    # Escape HTML special characters
    sanitized = escape(input_str)
    
    # Remove script tags and event handlers
    dangerous_patterns = [
        r"<script[^>]*>.*?</script>",
        r"javascript:",
        r"on\w+\s*=",  # Event handlers like onclick, onload, etc.
    ]
    
    for pattern in dangerous_patterns:
        sanitized = re.sub(pattern, "", sanitized, flags=re.IGNORECASE | re.DOTALL)
    
    return sanitized


def sanitize_command(input_str: str) -> str:
    """
    Sanitize input to prevent command injection attacks.
    
    Args:
        input_str: Input string to sanitize
        
    Returns:
        Sanitized string safe for shell commands
        
    Note:
        This is a basic sanitizer. Always use subprocess with
        argument lists instead of shell=True when possible.
    """
    if not isinstance(input_str, str):
        raise ValidationError(f"Expected string, got {type(input_str).__name__}")
    
    # Remove dangerous shell characters
    dangerous_chars = [
        ";", "&", "|", ">", "<", "`", "$", "(", ")", "{", "}",
        "[", "]", "\\", "\n", "\r"
    ]
    
    sanitized = input_str
    for char in dangerous_chars:
        sanitized = sanitized.replace(char, "")
    
    return sanitized.strip()


def validate_email(email: str) -> bool:
    """
    Validate email address format.
    
    Args:
        email: Email address to validate
        
    Returns:
        True if valid, False otherwise
    """
    if not isinstance(email, str):
        return False
    
    # Basic email regex pattern
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return bool(re.match(pattern, email))


def validate_url(url: str, allowed_schemes: Optional[List[str]] = None) -> bool:
    """
    Validate URL format and scheme.
    
    Args:
        url: URL to validate
        allowed_schemes: List of allowed URL schemes (default: ["http", "https"])
        
    Returns:
        True if valid, False otherwise
    """
    if not isinstance(url, str):
        return False
    
    if allowed_schemes is None:
        allowed_schemes = ["http", "https"]
    
    # Basic URL pattern
    pattern = r'^(https?|ftp)://[^\s/$.?#].[^\s]*$'
    
    if not re.match(pattern, url, re.IGNORECASE):
        return False
    
    # Check scheme
    scheme = url.split("://")[0].lower()
    return scheme in allowed_schemes


def validate_length(
    input_str: str,
    min_length: Optional[int] = None,
    max_length: Optional[int] = None
) -> bool:
    """
    Validate string length.
    
    Args:
        input_str: String to validate
        min_length: Minimum allowed length
        max_length: Maximum allowed length
        
    Returns:
        True if valid, False otherwise
        
    Raises:
        ValidationError: If validation fails with specific reason
    """
    if not isinstance(input_str, str):
        raise ValidationError(f"Expected string, got {type(input_str).__name__}")
    
    length = len(input_str)
    
    if min_length is not None and length < min_length:
        raise ValidationError(
            f"Input too short: {length} characters (minimum: {min_length})"
        )
    
    if max_length is not None and length > max_length:
        raise ValidationError(
            f"Input too long: {length} characters (maximum: {max_length})"
        )
    
    return True


def validate_alphanumeric(input_str: str, allow_spaces: bool = False) -> bool:
    """
    Validate that input contains only alphanumeric characters.
    
    Args:
        input_str: String to validate
        allow_spaces: Whether to allow spaces
        
    Returns:
        True if valid, False otherwise
        
    Raises:
        ValidationError: If validation fails
    """
    if not isinstance(input_str, str):
        raise ValidationError(f"Expected string, got {type(input_str).__name__}")
    
    if allow_spaces:
        pattern = r'^[a-zA-Z0-9\s]+$'
    else:
        pattern = r'^[a-zA-Z0-9]+$'
    
    if not re.match(pattern, input_str):
        raise ValidationError(
            "Input contains invalid characters (only alphanumeric allowed)"
        )
    
    return True


def validate_filename(filename: str) -> bool:
    """
    Validate filename to prevent directory traversal attacks.
    
    Args:
        filename: Filename to validate
        
    Returns:
        True if valid, False otherwise
        
    Raises:
        ValidationError: If validation fails
    """
    if not isinstance(filename, str):
        raise ValidationError(f"Expected string, got {type(filename).__name__}")
    
    # Check for directory traversal patterns
    dangerous_patterns = ["..", "/", "\\", "\x00"]
    
    for pattern in dangerous_patterns:
        if pattern in filename:
            raise ValidationError(
                f"Invalid filename: contains dangerous pattern '{pattern}'"
            )
    
    # Check for valid filename characters
    if not re.match(r'^[a-zA-Z0-9._-]+$', filename):
        raise ValidationError(
            "Invalid filename: contains invalid characters"
        )
    
    return True


def validate_integer(
    value: str,
    min_value: Optional[int] = None,
    max_value: Optional[int] = None
) -> int:
    """
    Validate and convert string to integer.
    
    Args:
        value: String value to validate and convert
        min_value: Minimum allowed value
        max_value: Maximum allowed value
        
    Returns:
        Validated integer value
        
    Raises:
        ValidationError: If validation fails
    """
    try:
        int_value = int(value)
    except (ValueError, TypeError):
        raise ValidationError(f"Invalid integer: '{value}'")
    
    if min_value is not None and int_value < min_value:
        raise ValidationError(
            f"Value too small: {int_value} (minimum: {min_value})"
        )
    
    if max_value is not None and int_value > max_value:
        raise ValidationError(
            f"Value too large: {int_value} (maximum: {max_value})"
        )
    
    return int_value


def sanitize_input(
    input_str: str,
    sanitize_sql_injection: bool = True,
    sanitize_xss_attack: bool = True,
    sanitize_command_injection: bool = True
) -> str:
    """
    Apply multiple sanitization methods to input.
    
    Args:
        input_str: Input string to sanitize
        sanitize_sql_injection: Apply SQL injection sanitization
        sanitize_xss_attack: Apply XSS sanitization
        sanitize_command_injection: Apply command injection sanitization
        
    Returns:
        Sanitized string
    """
    sanitized = input_str
    
    if sanitize_sql_injection:
        sanitized = sanitize_sql(sanitized)
    
    if sanitize_xss_attack:
        sanitized = sanitize_xss(sanitized)
    
    if sanitize_command_injection:
        sanitized = sanitize_command(sanitized)
    
    return sanitized
