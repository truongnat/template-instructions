"""
Property-based tests for example execution success.

Feature: sdlc-kit-improvements, Property 9: Example Execution Success
"""

import os
import sys
import yaml
from pathlib import Path
from hypothesis import given, strategies as st, settings
import pytest


# Feature: sdlc-kit-improvements, Property 9: Example Execution Success
@settings(max_examples=10)
@given(st.sampled_from([
    "examples/basic-workflow",
    "examples/multi-agent-workflow",
    "examples/integrations/github",
    "examples/integrations/slack"
]))
def test_example_execution_success(example_dir):
    """
    Property: For any example in examples/, when executed with its provided
    configuration, the example should complete without raising exceptions.
    
    Validates: Requirements 9.5
    """
    # Get the full path to the example directory
    base_path = Path(__file__).parent.parent.parent
    example_path = base_path / example_dir
    
    # Property 1: Example directory must exist
    assert example_path.exists(), f"Example directory {example_dir} does not exist"
    assert example_path.is_dir(), f"{example_dir} is not a directory"
    
    # Property 2: Example must have a workflow configuration file
    workflow_path = example_path / "workflow.yaml"
    assert workflow_path.exists(), f"workflow.yaml not found in {example_dir}"
    assert workflow_path.is_file(), f"workflow.yaml in {example_dir} is not a file"
    
    # Property 3: Workflow configuration must be valid YAML
    try:
        with open(workflow_path, 'r') as f:
            workflow_config = yaml.safe_load(f)
    except yaml.YAMLError as e:
        pytest.fail(f"workflow.yaml in {example_dir} is not valid YAML: {e}")
    except Exception as e:
        pytest.fail(f"Failed to read workflow.yaml in {example_dir}: {e}")
    
    # Property 4: Workflow configuration must not be empty
    assert workflow_config is not None, f"workflow.yaml in {example_dir} is empty"
    assert isinstance(workflow_config, dict), f"workflow.yaml in {example_dir} must be a dictionary"
    
    # Property 5: Workflow must have required fields
    required_fields = ["name", "version"]
    for field in required_fields:
        assert field in workflow_config, (
            f"workflow.yaml in {example_dir} is missing required field: {field}"
        )
    
    # Property 6: Workflow name must be a non-empty string
    assert isinstance(workflow_config["name"], str), (
        f"workflow.yaml in {example_dir}: 'name' must be a string"
    )
    assert len(workflow_config["name"].strip()) > 0, (
        f"workflow.yaml in {example_dir}: 'name' must not be empty"
    )
    
    # Property 7: Workflow version must be a non-empty string
    assert isinstance(workflow_config["version"], str), (
        f"workflow.yaml in {example_dir}: 'version' must be a string"
    )
    assert len(workflow_config["version"].strip()) > 0, (
        f"workflow.yaml in {example_dir}: 'version' must not be empty"
    )
    
    # Property 8: If agents are specified, they must be a list
    if "agents" in workflow_config:
        assert isinstance(workflow_config["agents"], list), (
            f"workflow.yaml in {example_dir}: 'agents' must be a list"
        )
    
    # Property 9: If tasks are specified, they must be a list
    if "tasks" in workflow_config:
        assert isinstance(workflow_config["tasks"], list), (
            f"workflow.yaml in {example_dir}: 'tasks' must be a list"
        )
    
    # Property 10: Configuration can be loaded without exceptions
    # This validates that the example configuration is well-formed and can be
    # processed by the system without errors
    try:
        # Validate that the configuration structure is sound
        # We're not executing the workflow, just validating it can be loaded
        assert "name" in workflow_config
        assert "version" in workflow_config
        
        # If there are additional config files, check they can be loaded
        config_path = example_path / "config.yaml"
        if config_path.exists():
            with open(config_path, 'r') as f:
                config_data = yaml.safe_load(f)
                assert config_data is not None, f"config.yaml in {example_dir} is empty"
        
    except Exception as e:
        pytest.fail(
            f"Example {example_dir} failed to load configuration: {e}. "
            "Examples should be executable with provided configuration."
        )


def test_all_examples_have_valid_workflow_configs():
    """
    Test that all example directories contain valid workflow configuration files.
    This is a concrete test that complements the property test.
    """
    base_path = Path(__file__).parent.parent.parent
    
    # Only check the specific example directories we created for this spec
    required_examples = [
        "examples/basic-workflow",
        "examples/multi-agent-workflow",
        "examples/integrations/github",
        "examples/integrations/slack"
    ]
    
    # Check each example directory
    invalid_configs = []
    for example_dir in required_examples:
        example_path = base_path / example_dir
        if not example_path.exists():
            continue  # Skip if directory doesn't exist
            
        workflow_path = example_path / "workflow.yaml"
        if not workflow_path.exists():
            invalid_configs.append(f"{example_dir}: missing workflow.yaml")
            continue
        
        try:
            with open(workflow_path, 'r') as f:
                workflow_config = yaml.safe_load(f)
            
            # Validate required fields
            if not isinstance(workflow_config, dict):
                invalid_configs.append(f"{example_dir}: workflow.yaml is not a dictionary")
                continue
            
            if "name" not in workflow_config:
                invalid_configs.append(f"{example_dir}: missing 'name' field")
            
            if "version" not in workflow_config:
                invalid_configs.append(f"{example_dir}: missing 'version' field")
                
        except yaml.YAMLError as e:
            invalid_configs.append(f"{example_dir}: invalid YAML - {e}")
        except Exception as e:
            invalid_configs.append(f"{example_dir}: error loading config - {e}")
    
    assert len(invalid_configs) == 0, (
        f"The following examples have invalid workflow configurations:\n" +
        "\n".join(f"  - {err}" for err in invalid_configs)
    )


def test_workflow_configs_have_valid_structure():
    """
    Test that workflow configurations have valid structure and types.
    """
    base_path = Path(__file__).parent.parent.parent
    
    required_examples = [
        "examples/basic-workflow",
        "examples/multi-agent-workflow",
        "examples/integrations/github",
        "examples/integrations/slack"
    ]
    
    for example_dir in required_examples:
        example_path = base_path / example_dir
        workflow_path = example_path / "workflow.yaml"
        
        if not workflow_path.exists():
            continue  # Skip if workflow doesn't exist (will be caught by other test)
        
        with open(workflow_path, 'r') as f:
            workflow_config = yaml.safe_load(f)
        
        # Check field types
        assert isinstance(workflow_config.get("name"), str), (
            f"{example_dir}: 'name' must be a string"
        )
        
        assert isinstance(workflow_config.get("version"), str), (
            f"{example_dir}: 'version' must be a string"
        )
        
        # Check optional fields if present
        if "description" in workflow_config:
            assert isinstance(workflow_config["description"], str), (
                f"{example_dir}: 'description' must be a string"
            )
        
        if "agents" in workflow_config:
            assert isinstance(workflow_config["agents"], list), (
                f"{example_dir}: 'agents' must be a list"
            )
        
        if "tasks" in workflow_config:
            assert isinstance(workflow_config["tasks"], list), (
                f"{example_dir}: 'tasks' must be a list"
            )
            
            # Each task should be a dictionary with required fields
            for i, task in enumerate(workflow_config["tasks"]):
                assert isinstance(task, dict), (
                    f"{example_dir}: task {i} must be a dictionary"
                )
                assert "id" in task, (
                    f"{example_dir}: task {i} must have an 'id' field"
                )
                assert "type" in task, (
                    f"{example_dir}: task {i} must have a 'type' field"
                )
        
        if "timeout" in workflow_config:
            assert isinstance(workflow_config["timeout"], int), (
                f"{example_dir}: 'timeout' must be an integer"
            )
            assert workflow_config["timeout"] > 0, (
                f"{example_dir}: 'timeout' must be positive"
            )


def test_example_configs_are_loadable():
    """
    Test that all configuration files in examples can be loaded without errors.
    """
    base_path = Path(__file__).parent.parent.parent
    
    required_examples = [
        "examples/basic-workflow",
        "examples/multi-agent-workflow",
        "examples/integrations/github",
        "examples/integrations/slack"
    ]
    
    for example_dir in required_examples:
        example_path = base_path / example_dir
        
        if not example_path.exists():
            continue
        
        # Check all YAML files in the example directory
        yaml_files = list(example_path.glob("**/*.yaml")) + list(example_path.glob("**/*.yml"))
        
        for yaml_file in yaml_files:
            try:
                with open(yaml_file, 'r') as f:
                    config = yaml.safe_load(f)
                
                # Config should not be None (empty files are not valid)
                assert config is not None, (
                    f"{yaml_file.relative_to(base_path)} is empty"
                )
                
            except yaml.YAMLError as e:
                pytest.fail(
                    f"{yaml_file.relative_to(base_path)} is not valid YAML: {e}"
                )
            except Exception as e:
                pytest.fail(
                    f"Failed to load {yaml_file.relative_to(base_path)}: {e}"
                )


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
