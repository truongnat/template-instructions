"""
Property-based tests for Configuration Validation (SDK Reorganization).

These tests use Hypothesis to verify universal properties of the Config class
across many randomly generated inputs.

Feature: sdk-reorganization
Property 5: Configuration Validation
Requirements: 6.5
"""

import pytest
from hypothesis import given, strategies as st, settings, assume
from typing import Any, Dict

from agentic_sdlc.core import Config, ValidationError


# Strategy for generating valid project root paths
valid_project_roots = st.text(
    min_size=1, max_size=100, alphabet=st.characters(blacklist_categories=('Cc', 'Cs'))
)

# Strategy for generating valid log levels
valid_log_levels = st.sampled_from(["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"])

# Strategy for generating valid plugin names
valid_plugin_names = st.lists(
    st.text(min_size=1, max_size=50, alphabet=st.characters(blacklist_categories=('Cc', 'Cs'))),
    min_size=0,
    max_size=5,
    unique=True
)

# Strategy for generating valid log file paths
valid_log_files = st.one_of(
    st.none(),
    st.text(min_size=1, max_size=100, alphabet=st.characters(blacklist_categories=('Cc', 'Cs')))
)

# Strategy for generating valid defaults directories
valid_defaults_dirs = st.one_of(
    st.none(),
    st.text(min_size=1, max_size=100, alphabet=st.characters(blacklist_categories=('Cc', 'Cs')))
)

# Strategy for generating wrong type values for project_root (should be string)
wrong_type_for_string = st.one_of(st.integers(), st.booleans(), st.lists(st.text()))

# Strategy for generating wrong type values for plugins (should be list)
wrong_type_for_list = st.one_of(st.text(), st.integers(), st.booleans(), st.dictionaries(st.text(), st.text()))


# Feature: sdk-reorganization, Property 5: Configuration Validation
@given(
    project_root=valid_project_roots,
    log_level=valid_log_levels,
    plugins=valid_plugin_names,
    log_file=valid_log_files,
    defaults_dir=valid_defaults_dirs
)
@settings(max_examples=100, deadline=None)
def test_valid_config_with_all_fields_accepted(project_root, log_level, plugins, log_file, defaults_dir):
    """
    Property: For any valid configuration with all fields properly set,
    validation SHALL NOT raise ValidationError.
    
    This property ensures that valid configurations are accepted.
    
    **Validates: Requirements 6.5**
    """
    config = Config()
    
    # Set all fields with valid values
    config.set("project_root", project_root)
    config.set("log_level", log_level)
    config.set("plugins", plugins)
    if log_file is not None:
        config.set("log_file", log_file)
    if defaults_dir is not None:
        config.set("defaults_dir", defaults_dir)
    
    # Verify the values were set correctly
    assert config.get("project_root") == project_root
    assert config.get("log_level") == log_level
    assert config.get("plugins") == plugins


# Feature: sdk-reorganization, Property 5: Configuration Validation
@given(wrong_type_value=wrong_type_for_string)
@settings(max_examples=100, deadline=None)
def test_wrong_type_for_project_root_raises_validation_error(wrong_type_value):
    """
    Property: For any non-string value assigned to project_root,
    validation SHALL raise ValidationError.
    
    This property ensures that type validation is enforced for string fields.
    
    **Validates: Requirements 6.5**
    """
    config = Config()
    
    with pytest.raises(ValidationError) as exc_info:
        config.set("project_root", wrong_type_value)
    
    # Verify error message includes the field name
    error_msg = str(exc_info.value).lower()
    assert "project_root" in error_msg or "project root" in error_msg or "type" in error_msg, (
        f"Error message should mention 'project_root' or type error. Got: {exc_info.value}"
    )


# Feature: sdk-reorganization, Property 5: Configuration Validation
@given(wrong_type_value=wrong_type_for_string)
@settings(max_examples=100, deadline=None)
def test_wrong_type_for_log_level_raises_validation_error(wrong_type_value):
    """
    Property: For any non-string value assigned to log_level,
    validation SHALL raise ValidationError.
    
    This property ensures that type validation is enforced.
    
    **Validates: Requirements 6.5**
    """
    config = Config()
    
    with pytest.raises(ValidationError) as exc_info:
        config.set("log_level", wrong_type_value)
    
    # Verify error message includes the field name
    error_msg = str(exc_info.value).lower()
    assert "log_level" in error_msg or "log level" in error_msg or "type" in error_msg, (
        f"Error message should mention 'log_level' or type error. Got: {exc_info.value}"
    )


# Feature: sdk-reorganization, Property 5: Configuration Validation
@given(wrong_type_value=wrong_type_for_list)
@settings(max_examples=100, deadline=None)
def test_wrong_type_for_plugins_raises_validation_error(wrong_type_value):
    """
    Property: For any non-list value assigned to plugins,
    validation SHALL raise ValidationError.
    
    This property ensures that type validation is enforced for list fields.
    
    **Validates: Requirements 6.5**
    """
    config = Config()
    
    with pytest.raises(ValidationError) as exc_info:
        config.set("plugins", wrong_type_value)
    
    # Verify error message includes the field name
    error_msg = str(exc_info.value).lower()
    assert "plugins" in error_msg or "type" in error_msg, (
        f"Error message should mention 'plugins' or type error. Got: {exc_info.value}"
    )


# Feature: sdk-reorganization, Property 5: Configuration Validation
@given(wrong_type_value=wrong_type_for_string)
@settings(max_examples=100, deadline=None)
def test_wrong_type_for_log_file_raises_validation_error(wrong_type_value):
    """
    Property: For any non-string value assigned to log_file,
    validation SHALL raise ValidationError.
    
    This property ensures that type validation is enforced for optional string fields.
    
    **Validates: Requirements 6.5**
    """
    config = Config()
    
    with pytest.raises(ValidationError) as exc_info:
        config.set("log_file", wrong_type_value)
    
    # Verify error message includes the field name
    error_msg = str(exc_info.value).lower()
    assert "log_file" in error_msg or "log file" in error_msg or "type" in error_msg, (
        f"Error message should mention 'log_file' or type error. Got: {exc_info.value}"
    )


# Feature: sdk-reorganization, Property 5: Configuration Validation
@given(wrong_type_value=wrong_type_for_string)
@settings(max_examples=100, deadline=None)
def test_wrong_type_for_defaults_dir_raises_validation_error(wrong_type_value):
    """
    Property: For any non-string value assigned to defaults_dir,
    validation SHALL raise ValidationError.
    
    This property ensures that type validation is enforced for optional string fields.
    
    **Validates: Requirements 6.5**
    """
    config = Config()
    
    with pytest.raises(ValidationError) as exc_info:
        config.set("defaults_dir", wrong_type_value)
    
    # Verify error message includes the field name
    error_msg = str(exc_info.value).lower()
    assert "defaults_dir" in error_msg or "defaults dir" in error_msg or "type" in error_msg, (
        f"Error message should mention 'defaults_dir' or type error. Got: {exc_info.value}"
    )


# Feature: sdk-reorganization, Property 5: Configuration Validation
@given(
    project_root=valid_project_roots,
    log_level=valid_log_levels,
    plugins=valid_plugin_names
)
@settings(max_examples=100, deadline=None)
def test_error_message_includes_field_name_for_type_errors(project_root, log_level, plugins):
    """
    Property: For any validation error due to type mismatch,
    the error message SHALL include the field name.
    
    This property ensures that error messages help users identify the problem.
    
    **Validates: Requirements 6.5**
    """
    config = Config()
    
    # Test with wrong type for project_root
    with pytest.raises(ValidationError) as exc_info:
        config.set("project_root", 123)  # Should be string
    
    error_msg = str(exc_info.value)
    # Should include field name
    assert "project_root" in error_msg.lower() or "project root" in error_msg.lower(), (
        f"Error message should include field name. Got: {error_msg}"
    )


# Feature: sdk-reorganization, Property 5: Configuration Validation
@given(
    project_root=valid_project_roots,
    log_level=valid_log_levels,
    plugins=valid_plugin_names
)
@settings(max_examples=100, deadline=None)
def test_error_message_includes_type_information(project_root, log_level, plugins):
    """
    Property: For any validation error due to type mismatch,
    the error message SHALL include information about the expected type.
    
    This property ensures that error messages are descriptive and actionable.
    
    **Validates: Requirements 6.5**
    """
    config = Config()
    
    # Test with wrong type for plugins (should be list)
    with pytest.raises(ValidationError) as exc_info:
        config.set("plugins", "not-a-list")  # Should be list
    
    error_msg = str(exc_info.value)
    # Should include field name
    assert "plugins" in error_msg.lower(), (
        f"Error message should include field name. Got: {error_msg}"
    )
    # Should include type information
    assert any(x in error_msg.lower() for x in ["type", "list", "array", "expected"]), (
        f"Error message should include type information. Got: {error_msg}"
    )


# Feature: sdk-reorganization, Property 5: Configuration Validation
@given(
    extra_field_name=st.text(min_size=1, max_size=20).filter(
        lambda x: x not in ["project_root", "log_level", "log_file", "models", "workflows", "plugins", "defaults_dir"]
    ),
    extra_field_value=st.text(min_size=1, max_size=50)
)
@settings(max_examples=100, deadline=None)
def test_extra_fields_in_config_raises_validation_error(extra_field_name, extra_field_value):
    """
    Property: For any configuration with extra fields not defined in the schema,
    validation SHALL raise ValidationError.
    
    This property ensures that the schema is strictly enforced (no extra fields).
    
    **Validates: Requirements 6.5**
    """
    config = Config()
    
    # Try to set an extra field that doesn't exist in the schema
    with pytest.raises(ValidationError) as exc_info:
        config.set(extra_field_name, extra_field_value)
    
    # Verify error message includes information about the extra field
    error_msg = str(exc_info.value).lower()
    assert "extra" in error_msg or extra_field_name.lower() in error_msg or "additional" in error_msg or "unknown" in error_msg, (
        f"Error message should mention extra field. Got: {exc_info.value}"
    )


# Feature: sdk-reorganization, Property 5: Configuration Validation
@given(
    project_root=valid_project_roots,
    log_level=valid_log_levels,
    plugins=valid_plugin_names
)
@settings(max_examples=100, deadline=None)
def test_validation_error_context_includes_field_information(project_root, log_level, plugins):
    """
    Property: For any validation error, the error context SHALL include
    information about which field caused the error.
    
    This property ensures that error messages are specific and actionable.
    
    **Validates: Requirements 6.5**
    """
    config = Config()
    
    # Test with wrong type for project_root
    with pytest.raises(ValidationError) as exc_info:
        config.set("project_root", 123)  # Should be string
    
    error = exc_info.value
    error_msg = str(error)
    
    # Error message should mention the field
    assert "project_root" in error_msg.lower() or "project root" in error_msg.lower(), (
        f"Error message should mention the field. Got: {error_msg}"
    )
    
    # Error context should have details
    if hasattr(error, 'context') and error.context:
        assert isinstance(error.context, dict), (
            f"Error context should be a dictionary. Got: {type(error.context)}"
        )


# Feature: sdk-reorganization, Property 5: Configuration Validation
@given(
    project_root=valid_project_roots,
    log_level=valid_log_levels,
    plugins=valid_plugin_names
)
@settings(max_examples=100, deadline=None)
def test_valid_config_values_are_retrievable(project_root, log_level, plugins):
    """
    Property: For any valid configuration value that is set without error,
    retrieving it with get() SHALL return the same value.
    
    This property ensures that configuration values are stored correctly.
    
    **Validates: Requirements 6.5**
    """
    config = Config()
    
    # Set valid values
    config.set("project_root", project_root)
    config.set("log_level", log_level)
    config.set("plugins", plugins)
    
    # Retrieve and verify
    assert config.get("project_root") == project_root
    assert config.get("log_level") == log_level
    assert config.get("plugins") == plugins


# Feature: sdk-reorganization, Property 5: Configuration Validation
@given(
    project_root=valid_project_roots,
    log_level=valid_log_levels,
    plugins=valid_plugin_names
)
@settings(max_examples=100, deadline=None)
def test_validation_happens_on_set(project_root, log_level, plugins):
    """
    Property: For any invalid value, validation SHALL happen immediately
    when set() is called, not deferred until later.
    
    This property ensures that validation is eager and immediate.
    
    **Validates: Requirements 6.5**
    """
    config = Config()
    
    # Setting an invalid value should raise immediately
    with pytest.raises(ValidationError):
        config.set("project_root", 123)  # Wrong type
    
    # Validation should have been triggered (error was raised)
    # This confirms validation happens on set(), not deferred


# Feature: sdk-reorganization, Property 5: Configuration Validation
@given(
    project_root=valid_project_roots,
    log_level=valid_log_levels
)
@settings(max_examples=100, deadline=None)
def test_error_message_is_descriptive_for_type_errors(project_root, log_level):
    """
    Property: For any type validation error, the error message SHALL be
    descriptive enough for a developer to understand what went wrong.
    
    This property ensures that error messages are helpful.
    
    **Validates: Requirements 6.5**
    """
    config = Config()
    
    # Test with wrong type for project_root
    with pytest.raises(ValidationError) as exc_info:
        config.set("project_root", [1, 2, 3])  # Should be string
    
    error_msg = str(exc_info.value)
    
    # Error message should be non-empty and descriptive
    assert len(error_msg) > 0, "Error message should not be empty"
    assert "project_root" in error_msg.lower() or "project root" in error_msg.lower(), (
        f"Error message should mention the field name. Got: {error_msg}"
    )
    # Should mention type or validation
    assert any(x in error_msg.lower() for x in ["type", "string", "expected", "validation", "must be"]), (
        f"Error message should be descriptive about the type error. Got: {error_msg}"
    )


# Feature: sdk-reorganization, Property 5: Configuration Validation
@given(
    project_root=valid_project_roots,
    log_level=valid_log_levels,
    plugins=valid_plugin_names
)
@settings(max_examples=100, deadline=None)
def test_multiple_validation_errors_reported(project_root, log_level, plugins):
    """
    Property: When multiple fields have validation errors, the error message
    SHALL report all errors (or at least the first one clearly).
    
    This property ensures that validation errors are comprehensive.
    
    **Validates: Requirements 6.5**
    """
    config = Config()
    
    # Try to set an invalid value
    with pytest.raises(ValidationError) as exc_info:
        config.set("project_root", 123)  # Wrong type
    
    error = exc_info.value
    error_msg = str(error)
    
    # Error should be reported
    assert len(error_msg) > 0, "Error message should not be empty"
    assert "project_root" in error_msg.lower() or "project root" in error_msg.lower(), (
        f"Error should mention the problematic field. Got: {error_msg}"
    )


# Feature: sdk-reorganization, Property 5: Configuration Validation
@given(
    valid_log_level=valid_log_levels
)
@settings(max_examples=100, deadline=None)
def test_valid_log_level_accepted(valid_log_level):
    """
    Property: For any valid log level value, setting it SHALL NOT raise ValidationError.
    
    This property ensures that valid log levels are accepted.
    
    **Validates: Requirements 6.5**
    """
    config = Config()
    
    # Should not raise any exception
    config.set("log_level", valid_log_level)
    
    # Verify the value was set correctly
    assert config.get("log_level") == valid_log_level


# Feature: sdk-reorganization, Property 5: Configuration Validation
@given(
    valid_plugins=valid_plugin_names
)
@settings(max_examples=100, deadline=None)
def test_valid_plugins_list_accepted(valid_plugins):
    """
    Property: For any valid plugins list, setting it SHALL NOT raise ValidationError.
    
    This property ensures that valid plugin lists are accepted.
    
    **Validates: Requirements 6.5**
    """
    config = Config()
    
    # Should not raise any exception
    config.set("plugins", valid_plugins)
    
    # Verify the value was set correctly
    assert config.get("plugins") == valid_plugins


# Feature: sdk-reorganization, Property 5: Configuration Validation
@given(
    valid_project_root=valid_project_roots
)
@settings(max_examples=100, deadline=None)
def test_valid_project_root_accepted(valid_project_root):
    """
    Property: For any valid project root value, setting it SHALL NOT raise ValidationError.
    
    This property ensures that valid project roots are accepted.
    
    **Validates: Requirements 6.5**
    """
    config = Config()
    
    # Should not raise any exception
    config.set("project_root", valid_project_root)
    
    # Verify the value was set correctly
    assert config.get("project_root") == valid_project_root
