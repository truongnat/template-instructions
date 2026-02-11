"""
Property-based tests for Configuration Validation.

These tests use Hypothesis to verify universal properties of the ConfigValidator
across many randomly generated inputs.

Feature: sdlc-kit-improvements
Property 1: Configuration Schema Validation
Requirements: 3.5, 8.2, 8.4
"""

import pytest
import tempfile
import json
import yaml
from pathlib import Path
from hypothesis import given, strategies as st, settings, assume
from typing import Dict, Any

from config.validators import ConfigValidator, ValidationResult


# Strategy for generating valid workflow names
valid_workflow_names = st.text(
    alphabet=st.characters(whitelist_categories=('Lu', 'Ll', 'Nd'), min_codepoint=45, max_codepoint=122),
    min_size=1,
    max_size=50
).filter(lambda x: x and x[0].isalnum() and all(c.isalnum() or c in '_-' for c in x))

# Strategy for generating valid semantic versions
valid_versions = st.builds(
    lambda major, minor, patch: f"{major}.{minor}.{patch}",
    major=st.integers(min_value=0, max_value=99),
    minor=st.integers(min_value=0, max_value=99),
    patch=st.integers(min_value=0, max_value=99)
)

# Strategy for generating valid agent IDs
valid_agent_ids = st.text(
    alphabet=st.characters(whitelist_categories=('Lu', 'Ll', 'Nd'), min_codepoint=45, max_codepoint=122),
    min_size=1,
    max_size=30
).filter(lambda x: x and x[0].isalnum() and all(c.isalnum() or c in '_-' for c in x))


# Feature: sdlc-kit-improvements, Property 1: Configuration Schema Validation
@given(
    name=valid_workflow_names,
    version=valid_versions,
    description=st.one_of(st.none(), st.text(min_size=0, max_size=200)),
    agents=st.one_of(st.none(), st.lists(valid_agent_ids, min_size=0, max_size=5, unique=True)),
    timeout=st.one_of(st.none(), st.integers(min_value=1, max_value=86400)),
)
@settings(max_examples=5, deadline=None)
def test_valid_workflow_config_passes_validation(name, version, description, agents, timeout):
    """
    Property: For any valid workflow configuration that conforms to the schema,
    the ConfigValidator should accept it and return is_valid=True.
    
    This property ensures that the validator correctly accepts all valid configurations
    according to the workflow schema rules.
    
    **Validates: Requirements 3.5, 8.2, 8.4**
    """
    validator = ConfigValidator()
    
    # Build a valid workflow configuration
    config = {
        "name": name,
        "version": version
    }
    
    # Add optional fields if provided
    if description is not None:
        config["description"] = description
    
    if agents is not None:
        config["agents"] = agents
    
    if timeout is not None:
        config["timeout"] = timeout
    
    # Load the workflow schema
    schema_path = Path("config/schemas/workflow.schema.json")
    schema = validator.load_schema(schema_path)
    
    # Validate the configuration
    result = validator.validate(config, schema)
    
    # Property: Valid configuration should pass validation
    assert result.is_valid, (
        f"Valid workflow configuration should pass validation. "
        f"Config: {config}, Errors: {result.errors}"
    )
    assert len(result.errors) == 0, (
        f"Valid configuration should have no errors. Errors: {result.errors}"
    )


# Feature: sdlc-kit-improvements, Property 1: Configuration Schema Validation
@given(
    config_data=st.dictionaries(
        keys=st.text(min_size=1, max_size=20),
        values=st.one_of(
            st.text(max_size=50),
            st.integers(),
            st.booleans(),
            st.lists(st.text(max_size=20), max_size=3)
        ),
        min_size=0,
        max_size=5
    )
)
@settings(max_examples=5, deadline=None)
def test_invalid_workflow_config_fails_validation(config_data):
    """
    Property: For any configuration that is missing required fields (name, version),
    the ConfigValidator should reject it and return is_valid=False.
    
    This property ensures that the validator correctly rejects invalid configurations
    that don't meet the schema requirements.
    
    **Validates: Requirements 3.5, 8.2, 8.4**
    """
    # Ensure the config is actually invalid by not including required fields
    assume("name" not in config_data or "version" not in config_data)
    
    validator = ConfigValidator()
    
    # Load the workflow schema
    schema_path = Path("config/schemas/workflow.schema.json")
    schema = validator.load_schema(schema_path)
    
    # Validate the configuration
    result = validator.validate(config_data, schema)
    
    # Property: Invalid configuration should fail validation
    assert not result.is_valid, (
        f"Invalid workflow configuration should fail validation. "
        f"Config: {config_data}"
    )
    assert len(result.errors) > 0, (
        "Invalid configuration should have error messages"
    )


# Feature: sdlc-kit-improvements, Property 1: Configuration Schema Validation
@given(
    id=valid_agent_ids,
    agent_type=st.sampled_from(["ba", "pm", "sa", "implementation", "research", "quality_judge", "security_analyst", "devops"]),
    name=st.one_of(st.none(), st.text(min_size=1, max_size=100)),
    capabilities=st.one_of(st.none(), st.lists(st.text(min_size=1, max_size=30), min_size=0, max_size=5, unique=True)),
    model=st.one_of(st.none(), st.sampled_from(["gpt-4", "gpt-3.5-turbo", "claude-3", "claude-2"])),
)
@settings(max_examples=5, deadline=None)
def test_valid_agent_config_passes_validation(id, agent_type, name, capabilities, model):
    """
    Property: For any valid agent configuration that conforms to the schema,
    the ConfigValidator should accept it and return is_valid=True.
    
    **Validates: Requirements 3.5, 8.2, 8.4**
    """
    validator = ConfigValidator()
    
    # Build a valid agent configuration
    config = {
        "id": id,
        "type": agent_type
    }
    
    # Add optional fields if provided
    if name is not None:
        config["name"] = name
    
    if capabilities is not None:
        config["capabilities"] = capabilities
    
    if model is not None:
        config["model"] = model
    
    # Load the agent schema
    schema_path = Path("config/schemas/agent.schema.json")
    schema = validator.load_schema(schema_path)
    
    # Validate the configuration
    result = validator.validate(config, schema)
    
    # Property: Valid configuration should pass validation
    assert result.is_valid, (
        f"Valid agent configuration should pass validation. "
        f"Config: {config}, Errors: {result.errors}"
    )
    assert len(result.errors) == 0, (
        f"Valid configuration should have no errors. Errors: {result.errors}"
    )


# Feature: sdlc-kit-improvements, Property 1: Configuration Schema Validation
@given(
    name=valid_workflow_names,
    version=st.text(min_size=1, max_size=20).filter(
        lambda x: not (len(x.split('.')) == 3 and all(p.isdigit() for p in x.split('.')))
    ),  # Generate invalid version strings
)
@settings(max_examples=5, deadline=None)
def test_invalid_version_format_fails_validation(name, version):
    """
    Property: For any workflow configuration with an invalid version format
    (not matching semantic versioning pattern), the ConfigValidator should
    reject it and return is_valid=False.
    
    **Validates: Requirements 3.5, 8.2, 8.4**
    """
    validator = ConfigValidator()
    
    # Build a workflow configuration with invalid version
    config = {
        "name": name,
        "version": version
    }
    
    # Load the workflow schema
    schema_path = Path("config/schemas/workflow.schema.json")
    schema = validator.load_schema(schema_path)
    
    # Validate the configuration
    result = validator.validate(config, schema)
    
    # Property: Configuration with invalid version should fail validation
    assert not result.is_valid, (
        f"Configuration with invalid version '{version}' should fail validation. "
        f"Config: {config}"
    )
    assert len(result.errors) > 0, (
        "Invalid configuration should have error messages"
    )


# Feature: sdlc-kit-improvements, Property 1: Configuration Schema Validation
@given(
    id=valid_agent_ids,
    invalid_type=st.text(min_size=1, max_size=30).filter(
        lambda x: x not in ["ba", "pm", "sa", "implementation", "research", "quality_judge", "security_analyst", "devops"]
    ),
)
@settings(max_examples=5, deadline=None)
def test_invalid_agent_type_fails_validation(id, invalid_type):
    """
    Property: For any agent configuration with an invalid type (not in the enum),
    the ConfigValidator should reject it and return is_valid=False.
    
    **Validates: Requirements 3.5, 8.2, 8.4**
    """
    validator = ConfigValidator()
    
    # Build an agent configuration with invalid type
    config = {
        "id": id,
        "type": invalid_type
    }
    
    # Load the agent schema
    schema_path = Path("config/schemas/agent.schema.json")
    schema = validator.load_schema(schema_path)
    
    # Validate the configuration
    result = validator.validate(config, schema)
    
    # Property: Configuration with invalid type should fail validation
    assert not result.is_valid, (
        f"Configuration with invalid type '{invalid_type}' should fail validation. "
        f"Config: {config}"
    )
    assert len(result.errors) > 0, (
        "Invalid configuration should have error messages"
    )


# Feature: sdlc-kit-improvements, Property 1: Configuration Schema Validation
@given(
    name=valid_workflow_names,
    version=valid_versions,
    timeout=st.integers(max_value=0),  # Invalid: must be >= 1
)
@settings(max_examples=5, deadline=None)
def test_invalid_timeout_value_fails_validation(name, version, timeout):
    """
    Property: For any workflow configuration with a timeout value less than 1,
    the ConfigValidator should reject it and return is_valid=False.
    
    **Validates: Requirements 3.5, 8.2, 8.4**
    """
    validator = ConfigValidator()
    
    # Build a workflow configuration with invalid timeout
    config = {
        "name": name,
        "version": version,
        "timeout": timeout
    }
    
    # Load the workflow schema
    schema_path = Path("config/schemas/workflow.schema.json")
    schema = validator.load_schema(schema_path)
    
    # Validate the configuration
    result = validator.validate(config, schema)
    
    # Property: Configuration with invalid timeout should fail validation
    assert not result.is_valid, (
        f"Configuration with invalid timeout {timeout} should fail validation. "
        f"Config: {config}"
    )
    assert len(result.errors) > 0, (
        "Invalid configuration should have error messages"
    )


# Feature: sdlc-kit-improvements, Property 1: Configuration Schema Validation
@given(
    name=valid_workflow_names,
    version=valid_versions,
    extra_field_name=st.text(min_size=1, max_size=20).filter(
        lambda x: x not in ["name", "version", "description", "agents", "tasks", "timeout", 
                           "retry_policy", "environment", "metadata"]
    ),
    extra_field_value=st.one_of(st.text(), st.integers(), st.booleans()),
)
@settings(max_examples=5, deadline=None)
def test_additional_properties_fail_validation(name, version, extra_field_name, extra_field_value):
    """
    Property: For any workflow configuration with additional properties not defined
    in the schema, the ConfigValidator should reject it (since additionalProperties: false).
    
    **Validates: Requirements 3.5, 8.2, 8.4**
    """
    validator = ConfigValidator()
    
    # Build a workflow configuration with an extra field
    config = {
        "name": name,
        "version": version,
        extra_field_name: extra_field_value
    }
    
    # Load the workflow schema
    schema_path = Path("config/schemas/workflow.schema.json")
    schema = validator.load_schema(schema_path)
    
    # Validate the configuration
    result = validator.validate(config, schema)
    
    # Property: Configuration with additional properties should fail validation
    assert not result.is_valid, (
        f"Configuration with additional property '{extra_field_name}' should fail validation. "
        f"Config: {config}"
    )
    assert len(result.errors) > 0, (
        "Invalid configuration should have error messages"
    )


# Feature: sdlc-kit-improvements, Property 1: Configuration Schema Validation
@given(
    config_type=st.sampled_from(["workflow", "agent", "rule", "skill"]),
)
@settings(max_examples=5, deadline=None)
def test_validate_by_type_with_empty_config(config_type):
    """
    Property: For any configuration type, when validating an empty configuration,
    the validator should fail because required fields are missing.
    
    **Validates: Requirements 3.5, 8.2, 8.4**
    """
    with tempfile.TemporaryDirectory() as tmpdir:
        tmpdir = Path(tmpdir)
        
        # Create an empty config file
        config_file = tmpdir / f"test_{config_type}.yaml"
        with open(config_file, 'w') as f:
            yaml.dump({}, f)
        
        validator = ConfigValidator()
        
        # Validate using the validate_by_type method
        result = validator.validate_by_type(config_file, config_type)
        
        # Property: Empty configuration should fail validation
        assert not result.is_valid, (
            f"Empty {config_type} configuration should fail validation"
        )
        assert len(result.errors) > 0, (
            "Invalid configuration should have error messages"
        )


# Feature: sdlc-kit-improvements, Property 1: Configuration Schema Validation
@given(
    name=valid_workflow_names,
    version=valid_versions,
    file_format=st.sampled_from(["yaml", "json"]),
)
@settings(max_examples=5, deadline=None)
def test_load_and_validate_with_file_formats(name, version, file_format):
    """
    Property: For any valid configuration, the ConfigValidator should successfully
    validate it regardless of whether it's stored in YAML or JSON format.
    
    **Validates: Requirements 3.5, 8.2, 8.4**
    """
    with tempfile.TemporaryDirectory() as tmpdir:
        tmpdir = Path(tmpdir)
        
        # Create a valid workflow configuration
        config = {
            "name": name,
            "version": version
        }
        
        # Write config in the specified format
        if file_format == "yaml":
            config_file = tmpdir / "workflow.yaml"
            with open(config_file, 'w') as f:
                yaml.dump(config, f)
        else:
            config_file = tmpdir / "workflow.json"
            with open(config_file, 'w') as f:
                json.dump(config, f)
        
        validator = ConfigValidator()
        schema_path = Path("config/schemas/workflow.schema.json")
        
        # Validate using load_and_validate
        result = validator.load_and_validate(config_file, schema_path)
        
        # Property: Valid configuration should pass validation in any format
        assert result.is_valid, (
            f"Valid {file_format} configuration should pass validation. "
            f"Config: {config}, Errors: {result.errors}"
        )
        assert len(result.errors) == 0, (
            f"Valid configuration should have no errors. Errors: {result.errors}"
        )


# Feature: sdlc-kit-improvements, Property 1: Configuration Schema Validation
@given(
    id=valid_agent_ids,
    agent_type=st.sampled_from(["ba", "pm", "sa", "implementation", "research", "quality_judge"]),
    temperature=st.one_of(st.none(), st.floats(min_value=0.0, max_value=2.0)),
    max_tokens=st.one_of(st.none(), st.integers(min_value=1, max_value=32000)),
)
@settings(max_examples=5, deadline=None)
def test_agent_config_with_nested_properties(id, agent_type, temperature, max_tokens):
    """
    Property: For any agent configuration with valid nested config properties,
    the ConfigValidator should accept it and return is_valid=True.
    
    **Validates: Requirements 3.5, 8.2, 8.4**
    """
    validator = ConfigValidator()
    
    # Build an agent configuration with nested config
    config = {
        "id": id,
        "type": agent_type
    }
    
    # Add nested config if any values are provided
    if temperature is not None or max_tokens is not None:
        config["config"] = {}
        if temperature is not None:
            config["config"]["temperature"] = temperature
        if max_tokens is not None:
            config["config"]["max_tokens"] = max_tokens
    
    # Load the agent schema
    schema_path = Path("config/schemas/agent.schema.json")
    schema = validator.load_schema(schema_path)
    
    # Validate the configuration
    result = validator.validate(config, schema)
    
    # Property: Valid configuration with nested properties should pass validation
    assert result.is_valid, (
        f"Valid agent configuration with nested properties should pass validation. "
        f"Config: {config}, Errors: {result.errors}"
    )
    assert len(result.errors) == 0, (
        f"Valid configuration should have no errors. Errors: {result.errors}"
    )


# ============================================================================
# Property 2: Validation Error Specificity
# ============================================================================

# Feature: sdlc-kit-improvements, Property 2: Validation Error Specificity
@given(
    config_data=st.dictionaries(
        keys=st.text(min_size=1, max_size=20),
        values=st.one_of(
            st.text(max_size=50),
            st.integers(),
            st.booleans(),
            st.lists(st.text(max_size=20), max_size=3)
        ),
        min_size=0,
        max_size=5
    )
)
@settings(max_examples=10, deadline=None)
def test_validation_error_contains_field_name(config_data):
    """
    Property: For any invalid configuration or data, when validation fails,
    the error message should contain the specific field name that caused
    the validation failure.
    
    This property ensures that validation errors are specific and actionable,
    helping developers quickly identify and fix configuration issues.
    
    **Validates: Requirements 3.6, 8.5**
    """
    # Ensure the config is actually invalid by not including required fields
    assume("name" not in config_data or "version" not in config_data)
    
    validator = ConfigValidator()
    
    # Load the workflow schema
    schema_path = Path("config/schemas/workflow.schema.json")
    schema = validator.load_schema(schema_path)
    
    # Validate the configuration
    result = validator.validate(config_data, schema)
    
    # Property: Invalid configuration should fail validation
    assert not result.is_valid, (
        f"Invalid workflow configuration should fail validation. "
        f"Config: {config_data}"
    )
    
    # Property: Error messages should contain field names
    assert len(result.errors) > 0, "Invalid configuration should have error messages"
    
    # Check that at least one error message contains a field reference
    # Error messages should mention specific fields like 'name', 'version', etc.
    has_field_reference = False
    for error in result.errors:
        # Error messages should contain "Field" or "field" and a field name
        if "Field" in error or "field" in error:
            has_field_reference = True
            break
        # Or they should mention specific field names
        if any(field in error for field in ["name", "version", "timeout", "agents", "tasks", "(root)"]):
            has_field_reference = True
            break
    
    assert has_field_reference, (
        f"At least one error message should contain a specific field reference. "
        f"Errors: {result.errors}"
    )


# Feature: sdlc-kit-improvements, Property 2: Validation Error Specificity
@given(
    name=valid_workflow_names,
    invalid_version=st.text(min_size=1, max_size=20).filter(
        lambda x: not (len(x.split('.')) == 3 and all(p.isdigit() for p in x.split('.')))
    ),
)
@settings(max_examples=10, deadline=None)
def test_validation_error_specifies_version_field(name, invalid_version):
    """
    Property: When a workflow configuration has an invalid version format,
    the error message should specifically mention the 'version' field.
    
    **Validates: Requirements 3.6, 8.5**
    """
    validator = ConfigValidator()
    
    # Build a workflow configuration with invalid version
    config = {
        "name": name,
        "version": invalid_version
    }
    
    # Load the workflow schema
    schema_path = Path("config/schemas/workflow.schema.json")
    schema = validator.load_schema(schema_path)
    
    # Validate the configuration
    result = validator.validate(config, schema)
    
    # Property: Configuration with invalid version should fail validation
    assert not result.is_valid, (
        f"Configuration with invalid version '{invalid_version}' should fail validation"
    )
    
    # Property: Error message should mention the 'version' field
    error_text = " ".join(result.errors).lower()
    assert "version" in error_text, (
        f"Error message should mention the 'version' field. "
        f"Errors: {result.errors}"
    )


# Feature: sdlc-kit-improvements, Property 2: Validation Error Specificity
@given(
    name=valid_workflow_names,
    version=valid_versions,
    invalid_timeout=st.integers(max_value=0),
)
@settings(max_examples=10, deadline=None)
def test_validation_error_specifies_timeout_field(name, version, invalid_timeout):
    """
    Property: When a workflow configuration has an invalid timeout value,
    the error message should specifically mention the 'timeout' field.
    
    **Validates: Requirements 3.6, 8.5**
    """
    validator = ConfigValidator()
    
    # Build a workflow configuration with invalid timeout
    config = {
        "name": name,
        "version": version,
        "timeout": invalid_timeout
    }
    
    # Load the workflow schema
    schema_path = Path("config/schemas/workflow.schema.json")
    schema = validator.load_schema(schema_path)
    
    # Validate the configuration
    result = validator.validate(config, schema)
    
    # Property: Configuration with invalid timeout should fail validation
    assert not result.is_valid, (
        f"Configuration with invalid timeout {invalid_timeout} should fail validation"
    )
    
    # Property: Error message should mention the 'timeout' field
    error_text = " ".join(result.errors).lower()
    assert "timeout" in error_text, (
        f"Error message should mention the 'timeout' field. "
        f"Errors: {result.errors}"
    )


# Feature: sdlc-kit-improvements, Property 2: Validation Error Specificity
@given(
    id=valid_agent_ids,
    invalid_type=st.text(min_size=1, max_size=30).filter(
        lambda x: x not in ["ba", "pm", "sa", "implementation", "research", "quality_judge", "security_analyst", "devops"]
    ),
)
@settings(max_examples=10, deadline=None)
def test_validation_error_specifies_type_field(id, invalid_type):
    """
    Property: When an agent configuration has an invalid type value,
    the error message should specifically mention the 'type' field.
    
    **Validates: Requirements 3.6, 8.5**
    """
    validator = ConfigValidator()
    
    # Build an agent configuration with invalid type
    config = {
        "id": id,
        "type": invalid_type
    }
    
    # Load the agent schema
    schema_path = Path("config/schemas/agent.schema.json")
    schema = validator.load_schema(schema_path)
    
    # Validate the configuration
    result = validator.validate(config, schema)
    
    # Property: Configuration with invalid type should fail validation
    assert not result.is_valid, (
        f"Configuration with invalid type '{invalid_type}' should fail validation"
    )
    
    # Property: Error message should mention the 'type' field
    error_text = " ".join(result.errors).lower()
    assert "type" in error_text, (
        f"Error message should mention the 'type' field. "
        f"Errors: {result.errors}"
    )


# Feature: sdlc-kit-improvements, Property 2: Validation Error Specificity
@given(
    name=valid_workflow_names,
    version=valid_versions,
    extra_field_name=st.text(min_size=1, max_size=20).filter(
        lambda x: x not in ["name", "version", "description", "agents", "tasks", "timeout", 
                           "retry_policy", "environment", "metadata"]
    ),
    extra_field_value=st.one_of(st.text(), st.integers(), st.booleans()),
)
@settings(max_examples=10, deadline=None)
def test_validation_error_specifies_additional_property_name(name, version, extra_field_name, extra_field_value):
    """
    Property: When a configuration contains additional properties not allowed
    by the schema, the error message should specifically mention which
    additional property caused the error.
    
    **Validates: Requirements 3.6, 8.5**
    """
    validator = ConfigValidator()
    
    # Build a workflow configuration with an extra field
    config = {
        "name": name,
        "version": version,
        extra_field_name: extra_field_value
    }
    
    # Load the workflow schema
    schema_path = Path("config/schemas/workflow.schema.json")
    schema = validator.load_schema(schema_path)
    
    # Validate the configuration
    result = validator.validate(config, schema)
    
    # Property: Configuration with additional properties should fail validation
    assert not result.is_valid, (
        f"Configuration with additional property '{extra_field_name}' should fail validation"
    )
    
    # Property: Error message should mention the specific additional property name
    error_text = " ".join(result.errors)
    # The error should either mention the field name directly or mention "additional properties"
    assert extra_field_name in error_text or "additional" in error_text.lower(), (
        f"Error message should mention the additional property '{extra_field_name}' "
        f"or indicate additional properties. Errors: {result.errors}"
    )


# Feature: sdlc-kit-improvements, Property 2: Validation Error Specificity
@given(
    id=valid_agent_ids,
    agent_type=st.sampled_from(["ba", "pm", "sa", "implementation", "research", "quality_judge"]),
    invalid_temperature=st.floats(min_value=-10.0, max_value=-0.1) | st.floats(min_value=2.1, max_value=10.0),
)
@settings(max_examples=10, deadline=None)
def test_validation_error_specifies_nested_field(id, agent_type, invalid_temperature):
    """
    Property: When a nested configuration field is invalid, the error message
    should specify the full path to the nested field (e.g., 'config.temperature').
    
    **Validates: Requirements 3.6, 8.5**
    """
    validator = ConfigValidator()
    
    # Build an agent configuration with invalid nested config
    config = {
        "id": id,
        "type": agent_type,
        "config": {
            "temperature": invalid_temperature
        }
    }
    
    # Load the agent schema
    schema_path = Path("config/schemas/agent.schema.json")
    schema = validator.load_schema(schema_path)
    
    # Validate the configuration
    result = validator.validate(config, schema)
    
    # Property: Configuration with invalid nested field should fail validation
    assert not result.is_valid, (
        f"Configuration with invalid temperature {invalid_temperature} should fail validation"
    )
    
    # Property: Error message should mention the nested field path
    error_text = " ".join(result.errors).lower()
    # Should mention both 'config' and 'temperature' or the path 'config.temperature'
    assert ("config" in error_text and "temperature" in error_text), (
        f"Error message should mention the nested field path 'config.temperature'. "
        f"Errors: {result.errors}"
    )


# Feature: sdlc-kit-improvements, Property 2: Validation Error Specificity
@given(
    name=valid_workflow_names,
    version=valid_versions,
    task_id=st.text(min_size=1, max_size=20),
    invalid_task_type=st.text(min_size=1, max_size=30).filter(
        lambda x: x not in ["analysis", "implementation", "validation", "testing", "deployment", "research"]
    ),
)
@settings(max_examples=10, deadline=None)
def test_validation_error_specifies_array_item_field(name, version, task_id, invalid_task_type):
    """
    Property: When an array item contains an invalid field, the error message
    should specify both the array field and the item index or field within the item.
    
    **Validates: Requirements 3.6, 8.5**
    """
    validator = ConfigValidator()
    
    # Build a workflow configuration with invalid task type
    config = {
        "name": name,
        "version": version,
        "tasks": [
            {
                "id": task_id,
                "type": invalid_task_type
            }
        ]
    }
    
    # Load the workflow schema
    schema_path = Path("config/schemas/workflow.schema.json")
    schema = validator.load_schema(schema_path)
    
    # Validate the configuration
    result = validator.validate(config, schema)
    
    # Property: Configuration with invalid task type should fail validation
    assert not result.is_valid, (
        f"Configuration with invalid task type '{invalid_task_type}' should fail validation"
    )
    
    # Property: Error message should mention the tasks array and the type field
    error_text = " ".join(result.errors).lower()
    assert "tasks" in error_text and "type" in error_text, (
        f"Error message should mention both 'tasks' array and 'type' field. "
        f"Errors: {result.errors}"
    )


# Feature: sdlc-kit-improvements, Property 2: Validation Error Specificity
@given(
    missing_field=st.sampled_from(["name", "version"]),
)
@settings(max_examples=10, deadline=None)
def test_validation_error_specifies_missing_required_field(missing_field):
    """
    Property: When a required field is missing from a configuration,
    the error message should specifically name the missing field.
    
    **Validates: Requirements 3.6, 8.5**
    """
    validator = ConfigValidator()
    
    # Build a workflow configuration missing one required field
    config = {}
    if missing_field == "version":
        config["name"] = "test-workflow"
    else:
        config["version"] = "1.0.0"
    
    # Load the workflow schema
    schema_path = Path("config/schemas/workflow.schema.json")
    schema = validator.load_schema(schema_path)
    
    # Validate the configuration
    result = validator.validate(config, schema)
    
    # Property: Configuration missing required field should fail validation
    assert not result.is_valid, (
        f"Configuration missing required field '{missing_field}' should fail validation"
    )
    
    # Property: Error message should mention the specific missing field
    error_text = " ".join(result.errors).lower()
    assert missing_field.lower() in error_text, (
        f"Error message should mention the missing field '{missing_field}'. "
        f"Errors: {result.errors}"
    )
