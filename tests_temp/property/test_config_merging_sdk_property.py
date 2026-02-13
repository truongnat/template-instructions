"""
Property-based tests for Configuration Merging (SDK Reorganization).

These tests use Hypothesis to verify universal properties of the Config.merge()
method across many randomly generated inputs, specifically testing that:
1. Merged config contains all defaults for unspecified keys
2. User-specified keys override defaults
3. Merging multiple times is idempotent

Feature: sdk-reorganization
Property 6: Configuration Merging
Requirements: 6.6
"""

import pytest
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

# Strategy for generating partial config dictionaries (user overrides)
# Only generate valid values that won't cause validation errors
@st.composite
def partial_config_strategy(draw):
    """Generate a partial config with only valid values."""
    config = {}
    
    # Randomly decide which keys to include
    if draw(st.booleans()):
        config["log_level"] = draw(valid_log_levels)
    if draw(st.booleans()):
        config["project_root"] = draw(valid_project_roots)
    if draw(st.booleans()):
        config["log_file"] = draw(valid_log_files)
    if draw(st.booleans()):
        config["plugins"] = draw(valid_plugin_names)
    
    return config

partial_config_dicts = partial_config_strategy()


# Feature: sdk-reorganization, Property 6: Configuration Merging
@given(user_config=partial_config_dicts)
@settings(max_examples=100, deadline=None)
def test_merged_config_contains_all_defaults_for_unspecified_keys(user_config):
    """
    Property: For any user-provided configuration, after merging with defaults,
    the resulting configuration SHALL contain all default values for keys that
    were not specified in the user configuration.
    
    This ensures that defaults are preserved when merging partial configurations.
    
    **Validates: Requirements 6.6**
    """
    config = Config()
    config.merge(user_config)
    
    # All default keys should be present in the config dict
    default_keys = {"log_level", "project_root", "models", "workflows", "plugins", "log_file", "defaults_dir"}
    config_dict = config.to_dict()
    for key in default_keys:
        assert key in config_dict, (
            f"Default key '{key}' is missing after merge"
        )
    
    # For keys not in user_config, they should have their default values
    for key in default_keys:
        if key not in user_config:
            # These keys should have their defaults
            if key == "log_level":
                assert config.get(key) == "INFO", f"Default log_level not preserved"
            elif key == "project_root":
                assert config.get(key) == ".", f"Default project_root not preserved"
            elif key in ["models", "workflows"]:
                assert config.get(key) == {}, f"Default {key} not preserved"
            elif key == "plugins":
                assert config.get(key) == [], f"Default plugins not preserved"


# Feature: sdk-reorganization, Property 6: Configuration Merging
@given(user_config=partial_config_dicts)
@settings(max_examples=100, deadline=None)
def test_user_specified_keys_override_defaults(user_config):
    """
    Property: For any user-provided configuration, after merging, the values
    for keys specified in the user configuration SHALL match the user-provided
    values, overriding any defaults.
    
    This ensures that user values take precedence over defaults.
    
    **Validates: Requirements 6.6**
    """
    config = Config()
    config.merge(user_config)
    
    # User-specified keys should have user values
    for key, value in user_config.items():
        retrieved_value = config.get(key)
        assert retrieved_value == value, (
            f"User-specified key '{key}' was not overridden: "
            f"expected={value}, got={retrieved_value}"
        )


# Feature: sdk-reorganization, Property 6: Configuration Merging
@given(
    first_merge=partial_config_dicts,
    second_merge=partial_config_dicts
)
@settings(max_examples=100, deadline=None)
def test_merging_multiple_times_is_idempotent(first_merge, second_merge):
    """
    Property: For any sequence of merge operations, merging the same
    configuration twice SHALL produce the same result as merging it once.
    
    This ensures that the merge operation is idempotent and predictable.
    
    **Validates: Requirements 6.6**
    """
    # First approach: merge twice with same config
    config1 = Config()
    config1.merge(first_merge)
    config1.merge(first_merge)
    result1 = config1.to_dict()
    
    # Second approach: merge once with same config
    config2 = Config()
    config2.merge(first_merge)
    result2 = config2.to_dict()
    
    # Results should be identical
    assert result1 == result2, (
        f"Merging twice produced different result than merging once: "
        f"twice={result1}, once={result2}"
    )


# Feature: sdk-reorganization, Property 6: Configuration Merging
@given(
    first_merge=partial_config_dicts,
    second_merge=partial_config_dicts
)
@settings(max_examples=100, deadline=None)
def test_merge_order_respects_precedence(first_merge, second_merge):
    """
    Property: For any sequence of merge operations, later merges SHALL override
    earlier merges for the same keys, establishing clear precedence.
    
    This ensures that merge order is predictable and follows expected precedence.
    
    **Validates: Requirements 6.6**
    """
    config = Config()
    config.merge(first_merge)
    config.merge(second_merge)
    
    # For keys in second_merge, values should match second_merge
    for key, value in second_merge.items():
        retrieved_value = config.get(key)
        assert retrieved_value == value, (
            f"Later merge did not override earlier merge for key '{key}': "
            f"expected={value}, got={retrieved_value}"
        )
    
    # For keys only in first_merge, values should match first_merge
    for key, value in first_merge.items():
        if key not in second_merge:
            retrieved_value = config.get(key)
            assert retrieved_value == value, (
                f"First merge value was lost for key '{key}': "
                f"expected={value}, got={retrieved_value}"
            )


# Feature: sdk-reorganization, Property 6: Configuration Merging
@given(user_config=partial_config_dicts)
@settings(max_examples=100, deadline=None)
def test_merge_preserves_nested_defaults(user_config):
    """
    Property: For any user-provided configuration, after merging, nested
    default structures (like empty dicts for models and workflows) SHALL be
    preserved even when not specified in the user configuration.
    
    This ensures that nested defaults are not lost during merge.
    
    **Validates: Requirements 6.6**
    """
    config = Config()
    config.merge(user_config)
    
    # Nested defaults should be preserved
    models = config.get("models")
    workflows = config.get("workflows")
    
    assert isinstance(models, dict), (
        f"'models' should be a dict after merge, got {type(models)}"
    )
    assert isinstance(workflows, dict), (
        f"'workflows' should be a dict after merge, got {type(workflows)}"
    )
