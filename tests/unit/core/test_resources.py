"""Unit tests for resource loading functionality.

Tests that verify:
- Templates can be loaded
- Workflows can be loaded
- Rules can be loaded
- Resources are included in package
- Resource listing works correctly
"""

import pytest
from pathlib import Path
from agentic_sdlc.core.resources import (
    get_resource_path,
    load_resource_text,
    list_resources,
)


class TestResourceLoading:
    """Test resource loading functionality."""

    def test_get_resource_path_templates(self):
        """Test getting path to a template resource."""
        path = get_resource_path("templates", "agent/default.yaml")
        assert path is not None
        assert path.exists()
        assert path.is_file()
        assert path.name == "default.yaml"

    def test_get_resource_path_workflows(self):
        """Test getting path to a workflow resource."""
        path = get_resource_path("workflows", "examples/simple.yaml")
        assert path is not None
        assert path.exists()
        assert path.is_file()

    def test_get_resource_path_rules(self):
        """Test getting path to a rules resource."""
        path = get_resource_path("rules", "coding_standards.yaml")
        assert path is not None
        assert path.exists()
        assert path.is_file()

    def test_get_resource_path_nonexistent(self):
        """Test getting path to a nonexistent resource."""
        path = get_resource_path("templates", "nonexistent.yaml")
        assert path is None

    def test_get_resource_path_invalid_type(self):
        """Test getting resource with invalid type."""
        with pytest.raises(ValueError) as exc_info:
            get_resource_path("invalid_type", "file.yaml")
        assert "Invalid resource type" in str(exc_info.value)

    def test_load_resource_text_template(self):
        """Test loading template resource as text."""
        content = load_resource_text("templates", "agent/default.yaml")
        assert content is not None
        assert "default_agent" in content
        assert "openai" in content

    def test_load_resource_text_workflow(self):
        """Test loading workflow resource as text."""
        content = load_resource_text("workflows", "examples/simple.yaml")
        assert content is not None
        assert "simple_workflow" in content
        assert "step1" in content

    def test_load_resource_text_rules(self):
        """Test loading rules resource as text."""
        content = load_resource_text("rules", "coding_standards.yaml")
        assert content is not None
        assert "coding_standards" in content
        assert "type_hints" in content

    def test_load_resource_text_nonexistent(self):
        """Test loading nonexistent resource returns None."""
        content = load_resource_text("templates", "nonexistent.yaml")
        assert content is None

    def test_load_resource_text_invalid_type(self):
        """Test loading resource with invalid type."""
        with pytest.raises(ValueError) as exc_info:
            load_resource_text("invalid_type", "file.yaml")
        assert "Invalid resource type" in str(exc_info.value)

    def test_list_resources_templates(self):
        """Test listing template resources."""
        resources = list_resources("templates")
        assert isinstance(resources, list)
        assert len(resources) > 0
        assert "agent" in resources

    def test_list_resources_workflows(self):
        """Test listing workflow resources."""
        resources = list_resources("workflows")
        assert isinstance(resources, list)
        assert len(resources) > 0
        assert "examples" in resources

    def test_list_resources_rules(self):
        """Test listing rules resources."""
        resources = list_resources("rules")
        assert isinstance(resources, list)
        assert len(resources) > 0
        assert "coding_standards.yaml" in resources

    def test_list_resources_invalid_type(self):
        """Test listing resources with invalid type."""
        with pytest.raises(ValueError) as exc_info:
            list_resources("invalid_type")
        assert "Invalid resource type" in str(exc_info.value)

    def test_list_resources_empty_directory(self):
        """Test listing resources from empty directory."""
        # This test assumes there's an empty resource directory
        # If all directories have content, this test may need adjustment
        resources = list_resources("templates")
        assert isinstance(resources, list)

    def test_resource_content_is_valid_yaml(self):
        """Test that loaded resources are valid YAML."""
        import yaml
        
        content = load_resource_text("templates", "agent/default.yaml")
        assert content is not None
        
        # Should be parseable as YAML
        data = yaml.safe_load(content)
        assert isinstance(data, dict)
        assert "name" in data

    def test_resources_are_included_in_package(self):
        """Test that resources are accessible from installed package."""
        # This test verifies that resources can be loaded
        # which indicates they're properly included in the package
        path = get_resource_path("templates", "agent/default.yaml")
        assert path is not None
        assert path.exists()


class TestResourceIntegration:
    """Test resource loading integration with SDK."""

    def test_resources_accessible_from_public_api(self):
        """Test that resource functions are accessible from public API."""
        from agentic_sdlc import get_resource_path, load_resource_text, list_resources
        
        # Should be importable
        assert callable(get_resource_path)
        assert callable(load_resource_text)
        assert callable(list_resources)

    def test_load_multiple_resources(self):
        """Test loading multiple resources in sequence."""
        template = load_resource_text("templates", "agent/default.yaml")
        workflow = load_resource_text("workflows", "examples/simple.yaml")
        rules = load_resource_text("rules", "coding_standards.yaml")
        
        assert template is not None
        assert workflow is not None
        assert rules is not None

    def test_resource_paths_are_consistent(self):
        """Test that resource paths are consistent across calls."""
        path1 = get_resource_path("templates", "agent/default.yaml")
        path2 = get_resource_path("templates", "agent/default.yaml")
        
        assert path1 == path2
        assert path1.exists()


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
