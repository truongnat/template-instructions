"""
Property-based tests for Configuration Override Consistency (SDK Reorganization).

These tests use Hypothesis to verify universal properties of the Config class
across many randomly generated inputs, specifically testing that configuration
values set through different methods (environment variables, files, API calls)
produce consistent results.

Feature: sdk-reorganization
Property 4: Configuration Override Consistency
Requirements: 6.4
"""

import json
import os
import tempfile
from pathlib import Path
from typing import Any, Dict

import pytest
import yaml
from hypothesis import given, strategies as st, settings, assume

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


# Feature: sdk-reorganization, Property 4: Configuration Override Consistency
@given(
    project_root=valid_project_roots,
    log_level=valid_log_levels
)
@settings(max_examples=100, deadline=None)
def test_api_call_and_environment_variable_produce_same_result(project_root, log_level):
    """
    Property: For any configuration key, setting it through environment variables
    and through API calls SHALL produce the same effective configuration value
    when retrieved via Config.get().
    
    This property ensures that different configuration methods are consistent.
    
    **Validates: Requirements 6.4**
    """
    # Set via environment variable
    os.environ["AGENTIC_SDLC_LOG_LEVEL"] = log_level
    
    try:
        config_from_env = Config()
        env_value = config_from_env.get("log_level")
        
        # Set via API call
        config_from_api = Config()
        config_from_api.set("log_level", log_level)
        api_value = config_from_api.get("log_level")
        
        # Both should produce the same result
        assert env_value == api_value, (
            f"Environment variable and API call produced different results: "
            f"env={env_value}, api={api_value}"
        )
        assert env_value == log_level, (
            f"Environment variable value doesn't match set value: "
            f"env={env_value}, expected={log_level}"
        )
    finally:
        if "AGENTIC_SDLC_LOG_LEVEL" in os.environ:
            del os.environ["AGENTIC_SDLC_LOG_LEVEL"]


# Feature: sdk-reorganization, Property 4: Configuration Override Consistency
@given(
    project_root=valid_project_roots,
    log_level=valid_log_levels
)
@settings(max_examples=100, deadline=None)
def test_file_and_api_call_produce_same_result(project_root, log_level):
    """
    Property: For any configuration key, setting it through a configuration file
    and through API calls SHALL produce the same effective configuration value
    when retrieved via Config.get().
    
    This property ensures that file-based and API-based configuration are consistent.
    
    **Validates: Requirements 6.4**
    """
    # Create a temporary YAML file with configuration
    with tempfile.NamedTemporaryFile(mode="w", suffix=".yaml", delete=False) as f:
        yaml.dump({
            "project_root": project_root,
            "log_level": log_level,
        }, f)
        f.flush()
        config_file = f.name
    
    try:
        # Load from file
        config_from_file = Config(config_file)
        file_value = config_from_file.get("log_level")
        
        # Set via API call
        config_from_api = Config()
        config_from_api.set("log_level", log_level)
        api_value = config_from_api.get("log_level")
        
        # Both should produce the same result
        assert file_value == api_value, (
            f"File-based and API call produced different results: "
            f"file={file_value}, api={api_value}"
        )
        assert file_value == log_level, (
            f"File-based value doesn't match set value: "
            f"file={file_value}, expected={log_level}"
        )
    finally:
        os.unlink(config_file)


# Feature: sdk-reorganization, Property 4: Configuration Override Consistency
@given(
    project_root=valid_project_roots,
    log_level=valid_log_levels
)
@settings(max_examples=100, deadline=None)
def test_environment_variable_overrides_file_config(project_root, log_level):
    """
    Property: For any configuration key, when set through both a file and
    environment variables, the environment variable value SHALL take precedence
    and be returned by Config.get().
    
    This property ensures that override precedence is consistent.
    
    **Validates: Requirements 6.4**
    """
    # Create a temporary YAML file with one value
    with tempfile.NamedTemporaryFile(mode="w", suffix=".yaml", delete=False) as f:
        yaml.dump({
            "project_root": project_root,
            "log_level": "INFO",  # File has INFO
        }, f)
        f.flush()
        config_file = f.name
    
    # Set environment variable to different value
    os.environ["AGENTIC_SDLC_LOG_LEVEL"] = log_level  # Env has different value
    
    try:
        # Load config with both file and environment variable
        config = Config(config_file)
        result = config.get("log_level")
        
        # Environment variable should take precedence
        assert result == log_level, (
            f"Environment variable should override file config: "
            f"expected={log_level}, got={result}"
        )
    finally:
        if "AGENTIC_SDLC_LOG_LEVEL" in os.environ:
            del os.environ["AGENTIC_SDLC_LOG_LEVEL"]
        os.unlink(config_file)


# Feature: sdk-reorganization, Property 4: Configuration Override Consistency
@given(
    project_root=valid_project_roots,
    log_level=valid_log_levels
)
@settings(max_examples=100, deadline=None)
def test_api_call_overrides_file_and_environment(project_root, log_level):
    """
    Property: For any configuration key, when set through file, environment variable,
    and API call, the API call value SHALL take precedence and be returned by Config.get().
    
    This property ensures that API calls have the highest precedence.
    
    **Validates: Requirements 6.4**
    """
    # Create a temporary YAML file with one value
    with tempfile.NamedTemporaryFile(mode="w", suffix=".yaml", delete=False) as f:
        yaml.dump({
            "project_root": project_root,
            "log_level": "INFO",  # File has INFO
        }, f)
        f.flush()
        config_file = f.name
    
    # Set environment variable to different value
    os.environ["AGENTIC_SDLC_LOG_LEVEL"] = "WARNING"  # Env has WARNING
    
    try:
        # Load config with file and environment variable
        config = Config(config_file)
        
        # Now override with API call
        config.set("log_level", log_level)  # API call has different value
        result = config.get("log_level")
        
        # API call should take precedence
        assert result == log_level, (
            f"API call should override file and environment: "
            f"expected={log_level}, got={result}"
        )
    finally:
        if "AGENTIC_SDLC_LOG_LEVEL" in os.environ:
            del os.environ["AGENTIC_SDLC_LOG_LEVEL"]
        os.unlink(config_file)


# Feature: sdk-reorganization, Property 4: Configuration Override Consistency
@given(
    project_root=valid_project_roots,
    log_level=valid_log_levels
)
@settings(max_examples=100, deadline=None)
def test_multiple_api_calls_produce_consistent_result(project_root, log_level):
    """
    Property: For any configuration key, calling set() multiple times with the same
    value SHALL produce the same result when retrieved via Config.get().
    
    This property ensures that repeated API calls are idempotent.
    
    **Validates: Requirements 6.4**
    """
    config = Config()
    
    # Set the value multiple times
    config.set("log_level", log_level)
    first_result = config.get("log_level")
    
    config.set("log_level", log_level)
    second_result = config.get("log_level")
    
    config.set("log_level", log_level)
    third_result = config.get("log_level")
    
    # All results should be identical
    assert first_result == second_result == third_result == log_level, (
        f"Multiple API calls should produce consistent results: "
        f"first={first_result}, second={second_result}, third={third_result}"
    )


# Feature: sdk-reorganization, Property 4: Configuration Override Consistency
@given(
    project_root=valid_project_roots,
    log_level=valid_log_levels
)
@settings(max_examples=100, deadline=None)
def test_get_returns_consistent_value_across_calls(project_root, log_level):
    """
    Property: For any configuration key that has been set, calling Config.get()
    multiple times SHALL return the same value each time.
    
    This property ensures that get() is consistent and doesn't have side effects.
    
    **Validates: Requirements 6.4**
    """
    config = Config()
    config.set("log_level", log_level)
    
    # Get the value multiple times
    first_get = config.get("log_level")
    second_get = config.get("log_level")
    third_get = config.get("log_level")
    
    # All gets should return the same value
    assert first_get == second_get == third_get == log_level, (
        f"Config.get() should return consistent values: "
        f"first={first_get}, second={second_get}, third={third_get}"
    )


# Feature: sdk-reorganization, Property 4: Configuration Override Consistency
@given(
    project_root=valid_project_roots,
    log_level=valid_log_levels
)
@settings(max_examples=100, deadline=None)
def test_merge_and_api_call_produce_same_result(project_root, log_level):
    """
    Property: For any configuration key, setting it through merge() and through
    set() API calls SHALL produce the same effective configuration value
    when retrieved via Config.get().
    
    This property ensures that merge() and set() are consistent.
    
    **Validates: Requirements 6.4**
    """
    # Set via merge()
    config_from_merge = Config()
    config_from_merge.merge({"log_level": log_level})
    merge_value = config_from_merge.get("log_level")
    
    # Set via set()
    config_from_set = Config()
    config_from_set.set("log_level", log_level)
    set_value = config_from_set.get("log_level")
    
    # Both should produce the same result
    assert merge_value == set_value, (
        f"merge() and set() should produce same result: "
        f"merge={merge_value}, set={set_value}"
    )
    assert merge_value == log_level, (
        f"merge() value doesn't match set value: "
        f"merge={merge_value}, expected={log_level}"
    )


# Feature: sdk-reorganization, Property 4: Configuration Override Consistency
@given(
    project_root=valid_project_roots,
    log_level=valid_log_levels
)
@settings(max_examples=100, deadline=None)
def test_nested_config_override_consistency(project_root, log_level):
    """
    Property: For any nested configuration key, setting it through different methods
    SHALL produce the same effective configuration value when retrieved via Config.get()
    with dot notation.
    
    This property ensures that nested configuration override is consistent.
    
    **Validates: Requirements 6.4**
    """
    # Set nested value via API call
    config_from_api = Config()
    config_from_api.set("models.openai.provider", "openai")
    config_from_api.set("models.openai.model_name", "gpt-4")
    api_provider = config_from_api.get("models.openai.provider")
    api_model = config_from_api.get("models.openai.model_name")
    
    # Set nested value via merge()
    config_from_merge = Config()
    config_from_merge.merge({
        "models": {
            "openai": {
                "provider": "openai",
                "model_name": "gpt-4",
            }
        }
    })
    merge_provider = config_from_merge.get("models.openai.provider")
    merge_model = config_from_merge.get("models.openai.model_name")
    
    # Both should produce the same result
    assert api_provider == merge_provider == "openai", (
        f"Nested config override inconsistent for provider: "
        f"api={api_provider}, merge={merge_provider}"
    )
    assert api_model == merge_model == "gpt-4", (
        f"Nested config override inconsistent for model: "
        f"api={api_model}, merge={merge_model}"
    )


# Feature: sdk-reorganization, Property 4: Configuration Override Consistency
@given(
    project_root=valid_project_roots,
    log_level=valid_log_levels
)
@settings(max_examples=100, deadline=None)
def test_to_dict_reflects_all_overrides(project_root, log_level):
    """
    Property: For any configuration that has been set through various methods,
    calling to_dict() SHALL return a dictionary that reflects all the overrides
    and matches what Config.get() would return for each key.
    
    This property ensures that to_dict() is consistent with get().
    
    **Validates: Requirements 6.4**
    """
    config = Config()
    config.set("log_level", log_level)
    config.set("project_root", project_root)
    
    # Get values via get()
    get_log_level = config.get("log_level")
    get_project_root = config.get("project_root")
    
    # Get values via to_dict()
    config_dict = config.to_dict()
    dict_log_level = config_dict.get("log_level")
    dict_project_root = config_dict.get("project_root")
    
    # Both should match
    assert get_log_level == dict_log_level == log_level, (
        f"to_dict() and get() inconsistent for log_level: "
        f"get={get_log_level}, dict={dict_log_level}"
    )
    assert get_project_root == dict_project_root == project_root, (
        f"to_dict() and get() inconsistent for project_root: "
        f"get={get_project_root}, dict={dict_project_root}"
    )


# Feature: sdk-reorganization, Property 4: Configuration Override Consistency
@given(
    log_level=valid_log_levels
)
@settings(max_examples=100, deadline=None)
def test_environment_variable_format_consistency(log_level):
    """
    Property: For any configuration key, setting it through environment variable
    with the AGENTIC_SDLC_ prefix SHALL be correctly parsed and accessible via
    Config.get() with the lowercase key name.
    
    This property ensures that environment variable parsing is consistent.
    
    **Validates: Requirements 6.4**
    """
    # Set environment variable with prefix
    os.environ["AGENTIC_SDLC_LOG_LEVEL"] = log_level
    
    try:
        config = Config()
        result = config.get("log_level")
        
        # Should be accessible with lowercase key
        assert result == log_level, (
            f"Environment variable not parsed correctly: "
            f"expected={log_level}, got={result}"
        )
    finally:
        if "AGENTIC_SDLC_LOG_LEVEL" in os.environ:
            del os.environ["AGENTIC_SDLC_LOG_LEVEL"]


# Feature: sdk-reorganization, Property 4: Configuration Override Consistency
@given(
    project_root=valid_project_roots,
    log_level=valid_log_levels
)
@settings(max_examples=100, deadline=None)
def test_json_file_and_yaml_file_produce_same_result(project_root, log_level):
    """
    Property: For any configuration, loading from a JSON file and loading from
    a YAML file with the same content SHALL produce the same effective configuration
    values when retrieved via Config.get().
    
    This property ensures that file format doesn't affect configuration values.
    
    **Validates: Requirements 6.4**
    """
    config_data = {
        "project_root": project_root,
        "log_level": log_level,
    }
    
    # Create YAML file
    with tempfile.NamedTemporaryFile(mode="w", suffix=".yaml", delete=False) as f:
        yaml.dump(config_data, f)
        f.flush()
        yaml_file = f.name
    
    # Create JSON file
    with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
        json.dump(config_data, f)
        f.flush()
        json_file = f.name
    
    try:
        # Load from YAML
        config_from_yaml = Config(yaml_file)
        yaml_log_level = config_from_yaml.get("log_level")
        yaml_project_root = config_from_yaml.get("project_root")
        
        # Load from JSON
        config_from_json = Config(json_file)
        json_log_level = config_from_json.get("log_level")
        json_project_root = config_from_json.get("project_root")
        
        # Both should produce the same result
        assert yaml_log_level == json_log_level == log_level, (
            f"YAML and JSON files produced different log_level: "
            f"yaml={yaml_log_level}, json={json_log_level}"
        )
        assert yaml_project_root == json_project_root == project_root, (
            f"YAML and JSON files produced different project_root: "
            f"yaml={yaml_project_root}, json={json_project_root}"
        )
    finally:
        os.unlink(yaml_file)
        os.unlink(json_file)
