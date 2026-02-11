"""Unit tests for the configuration system.

Tests the Config class, configuration loading, validation, and merging.
"""

import json
import os
import tempfile
from pathlib import Path
from typing import Any, Dict

import pytest
import yaml

from agentic_sdlc.core.config import Config, get_config, load_config
from agentic_sdlc.core.exceptions import ConfigurationError, ValidationError
from agentic_sdlc.core.types import AgentConfig, ModelConfig, SDKConfig, WorkflowConfig


class TestConfigDefaults:
    """Tests for default configuration values."""

    def test_config_has_default_values(self) -> None:
        """Test that Config initializes with default values."""
        config = Config()
        assert config.get("project_root") == "."
        assert config.get("log_level") == "INFO"
        assert config.get("log_file") is None
        assert config.get("models") == {}
        assert config.get("workflows") == {}
        assert config.get("plugins") == []
        assert config.get("defaults_dir") is None

    def test_config_to_dict_returns_all_defaults(self) -> None:
        """Test that to_dict returns all default values."""
        config = Config()
        config_dict = config.to_dict()
        assert "project_root" in config_dict
        assert "log_level" in config_dict
        assert "log_file" in config_dict
        assert "models" in config_dict
        assert "workflows" in config_dict
        assert "plugins" in config_dict
        assert "defaults_dir" in config_dict


class TestConfigGet:
    """Tests for Config.get() method."""

    def test_get_top_level_value(self) -> None:
        """Test getting a top-level configuration value."""
        config = Config()
        assert config.get("log_level") == "INFO"

    def test_get_with_default_value(self) -> None:
        """Test get() returns default when key not found."""
        config = Config()
        assert config.get("nonexistent", "default_value") == "default_value"

    def test_get_nested_value_with_dot_notation(self) -> None:
        """Test getting nested values using dot notation."""
        config = Config()
        config.set("models.openai.provider", "openai")
        config.set("models.openai.model_name", "gpt-4")
        assert config.get("models.openai.provider") == "openai"
        assert config.get("models.openai.model_name") == "gpt-4"

    def test_get_nonexistent_nested_key_returns_default(self) -> None:
        """Test get() returns default for nonexistent nested keys."""
        config = Config()
        assert config.get("models.nonexistent.value", "default") == "default"

    def test_get_returns_none_when_no_default_provided(self) -> None:
        """Test get() returns None when key not found and no default provided."""
        config = Config()
        assert config.get("nonexistent") is None


class TestConfigSet:
    """Tests for Config.set() method."""

    def test_set_top_level_value(self) -> None:
        """Test setting a top-level configuration value."""
        config = Config()
        config.set("log_level", "DEBUG")
        assert config.get("log_level") == "DEBUG"

    def test_set_nested_value_with_dot_notation(self) -> None:
        """Test setting nested values using dot notation."""
        config = Config()
        config.set("models.openai.provider", "openai")
        config.set("models.openai.model_name", "gpt-4")
        assert config.get("models.openai.provider") == "openai"
        assert config.get("models.openai.model_name") == "gpt-4"

    def test_set_creates_intermediate_dicts(self) -> None:
        """Test that set() creates intermediate dictionaries."""
        config = Config()
        config.set("models.openai.api_key", "test-key")
        config.set("models.openai.provider", "openai")
        config.set("models.openai.model_name", "gpt-4")
        assert isinstance(config.get("models"), dict)
        assert isinstance(config.get("models.openai"), dict)
        assert config.get("models.openai.api_key") == "test-key"

    def test_set_wrong_type_raises_validation_error(self) -> None:
        """Test that set() raises ValidationError for wrong types."""
        config = Config()
        with pytest.raises(ValidationError):
            config.set("project_root", 12345)  # Should be string


class TestConfigValidation:
    """Tests for Config.validate() method."""

    def test_validate_passes_with_valid_config(self) -> None:
        """Test that validate() passes with valid configuration."""
        config = Config()
        config.validate()  # Should not raise

    def test_validate_fails_with_missing_required_field(self) -> None:
        """Test that validate() fails when required field is missing."""
        config = Config()
        del config._config["project_root"]
        with pytest.raises(ValidationError):
            config.validate()

    def test_validate_fails_with_extra_fields(self) -> None:
        """Test that validate() fails with extra fields not in schema."""
        config = Config()
        config._config["invalid_field"] = "value"
        with pytest.raises(ValidationError):
            config.validate()

    def test_validate_error_includes_context(self) -> None:
        """Test that ValidationError includes context information."""
        config = Config()
        del config._config["project_root"]
        with pytest.raises(ValidationError) as exc_info:
            config.validate()
        assert exc_info.value.context is not None
        assert "errors" in exc_info.value.context


class TestConfigMerge:
    """Tests for Config.merge() method."""

    def test_merge_overrides_defaults(self) -> None:
        """Test that merge() overrides default values."""
        config = Config()
        config.merge({"log_level": "DEBUG"})
        assert config.get("log_level") == "DEBUG"

    def test_merge_preserves_unspecified_defaults(self) -> None:
        """Test that merge() preserves defaults for unspecified keys."""
        config = Config()
        original_project_root = config.get("project_root")
        config.merge({"log_level": "DEBUG"})
        assert config.get("project_root") == original_project_root

    def test_merge_nested_dicts(self) -> None:
        """Test that merge() properly merges nested dictionaries."""
        config = Config()
        config.merge({
            "models": {
                "openai": {
                    "provider": "openai",
                    "model_name": "gpt-4",
                }
            }
        })
        assert config.get("models.openai.provider") == "openai"
        assert config.get("models.openai.model_name") == "gpt-4"

    def test_merge_is_idempotent(self) -> None:
        """Test that merging the same config multiple times is idempotent."""
        config = Config()
        merge_data = {"log_level": "DEBUG"}
        config.merge(merge_data)
        first_result = config.to_dict()
        config.merge(merge_data)
        second_result = config.to_dict()
        assert first_result == second_result

    def test_merge_validates_after_merge(self) -> None:
        """Test that merge() validates configuration after merging."""
        config = Config()
        with pytest.raises(ValidationError):
            config.merge({"invalid_field": "value"})


class TestConfigLoadFromFile:
    """Tests for loading configuration from files."""

    def test_load_from_yaml_file(self) -> None:
        """Test loading configuration from YAML file."""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".yaml", delete=False) as f:
            yaml.dump({
                "project_root": "/test/project",
                "log_level": "DEBUG",
            }, f)
            f.flush()
            
            try:
                config = Config(f.name)
                assert config.get("project_root") == "/test/project"
                assert config.get("log_level") == "DEBUG"
            finally:
                os.unlink(f.name)

    def test_load_from_json_file(self) -> None:
        """Test loading configuration from JSON file."""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
            json.dump({
                "project_root": "/test/project",
                "log_level": "WARNING",
            }, f)
            f.flush()
            
            try:
                config = Config(f.name)
                assert config.get("project_root") == "/test/project"
                assert config.get("log_level") == "WARNING"
            finally:
                os.unlink(f.name)

    def test_load_from_yml_file(self) -> None:
        """Test loading configuration from .yml file."""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".yml", delete=False) as f:
            yaml.dump({"log_level": "ERROR"}, f)
            f.flush()
            
            try:
                config = Config(f.name)
                assert config.get("log_level") == "ERROR"
            finally:
                os.unlink(f.name)

    def test_load_from_nonexistent_file_raises_error(self) -> None:
        """Test that loading from nonexistent file raises ConfigurationError."""
        with pytest.raises(ConfigurationError) as exc_info:
            Config("/nonexistent/path/config.yaml")
        assert "not found" in str(exc_info.value).lower()

    def test_load_from_invalid_yaml_raises_error(self) -> None:
        """Test that loading invalid YAML raises ConfigurationError."""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".yaml", delete=False) as f:
            f.write("invalid: yaml: content: [")
            f.flush()
            
            try:
                with pytest.raises(ConfigurationError):
                    Config(f.name)
            finally:
                os.unlink(f.name)

    def test_load_from_invalid_json_raises_error(self) -> None:
        """Test that loading invalid JSON raises ConfigurationError."""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
            f.write("{invalid json}")
            f.flush()
            
            try:
                with pytest.raises(ConfigurationError):
                    Config(f.name)
            finally:
                os.unlink(f.name)

    def test_load_from_unsupported_file_format_raises_error(self) -> None:
        """Test that loading unsupported file format raises ConfigurationError."""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".txt", delete=False) as f:
            f.write("some content")
            f.flush()
            
            try:
                with pytest.raises(ConfigurationError) as exc_info:
                    Config(f.name)
                assert "unsupported" in str(exc_info.value).lower()
            finally:
                os.unlink(f.name)

    def test_load_from_empty_yaml_file(self) -> None:
        """Test loading from empty YAML file uses defaults."""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".yaml", delete=False) as f:
            f.write("")
            f.flush()
            
            try:
                config = Config(f.name)
                assert config.get("log_level") == "INFO"
            finally:
                os.unlink(f.name)


class TestConfigLoadFromEnvironment:
    """Tests for loading configuration from environment variables."""

    def test_load_from_environment_variables(self) -> None:
        """Test loading configuration from environment variables."""
        os.environ["AGENTIC_SDLC_LOG_LEVEL"] = "DEBUG"
        os.environ["AGENTIC_SDLC_PROJECT_ROOT"] = "/env/project"
        
        try:
            config = Config()
            assert config.get("log_level") == "DEBUG"
            assert config.get("project_root") == "/env/project"
        finally:
            del os.environ["AGENTIC_SDLC_LOG_LEVEL"]
            del os.environ["AGENTIC_SDLC_PROJECT_ROOT"]

    def test_environment_variables_override_file_config(self) -> None:
        """Test that environment variables override file configuration."""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".yaml", delete=False) as f:
            yaml.dump({"log_level": "INFO"}, f)
            f.flush()
            
            os.environ["AGENTIC_SDLC_LOG_LEVEL"] = "ERROR"
            
            try:
                config = Config(f.name)
                assert config.get("log_level") == "ERROR"
            finally:
                del os.environ["AGENTIC_SDLC_LOG_LEVEL"]
                os.unlink(f.name)

    def test_environment_variables_case_insensitive(self) -> None:
        """Test that environment variable keys are converted to lowercase."""
        os.environ["AGENTIC_SDLC_LOG_LEVEL"] = "WARNING"
        
        try:
            config = Config()
            assert config.get("log_level") == "WARNING"
        finally:
            del os.environ["AGENTIC_SDLC_LOG_LEVEL"]


class TestConfigModuleFunctions:
    """Tests for module-level configuration functions."""

    def test_load_config_function(self) -> None:
        """Test load_config() function."""
        config = load_config()
        assert isinstance(config, Config)
        assert config.get("log_level") == "INFO"

    def test_get_config_function(self) -> None:
        """Test get_config() function."""
        config = get_config()
        assert isinstance(config, Config)
        assert config.get("log_level") == "INFO"

    def test_load_config_with_file(self) -> None:
        """Test load_config() with configuration file."""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".yaml", delete=False) as f:
            yaml.dump({"log_level": "DEBUG"}, f)
            f.flush()
            
            try:
                config = load_config(f.name)
                assert config.get("log_level") == "DEBUG"
            finally:
                os.unlink(f.name)


class TestConfigWithComplexModels:
    """Tests for configuration with complex nested models."""

    def test_config_with_model_config(self) -> None:
        """Test configuration with ModelConfig."""
        config = Config()
        config.set("models.openai.provider", "openai")
        config.set("models.openai.model_name", "gpt-4")
        config.set("models.openai.temperature", 0.7)
        config.set("models.openai.max_tokens", 2000)
        config.set("models.openai.timeout", 30)
        
        assert config.get("models.openai.provider") == "openai"
        assert config.get("models.openai.temperature") == 0.7

    def test_config_with_agent_config(self) -> None:
        """Test configuration with AgentConfig."""
        config = Config()
        config.set("models.default.provider", "openai")
        config.set("models.default.model_name", "gpt-4")
        
        # Note: Full AgentConfig validation happens at SDKConfig level
        config.validate()
        assert config.get("models.default.provider") == "openai"

    def test_config_preserves_types(self) -> None:
        """Test that configuration preserves value types."""
        config = Config()
        config.set("models.test.temperature", 0.5)
        config.set("models.test.max_tokens", 1000)
        config.set("models.test.provider", "openai")
        config.set("models.test.model_name", "gpt-4")
        
        assert isinstance(config.get("models.test.temperature"), float)
        assert isinstance(config.get("models.test.max_tokens"), int)


class TestConfigEdgeCases:
    """Tests for edge cases and error conditions."""

    def test_config_with_none_values(self) -> None:
        """Test configuration with None values."""
        config = Config()
        config.set("log_file", None)
        assert config.get("log_file") is None

    def test_config_with_empty_lists(self) -> None:
        """Test configuration with empty lists."""
        config = Config()
        config.set("plugins", [])
        assert config.get("plugins") == []

    def test_config_with_empty_dicts(self) -> None:
        """Test configuration with empty dictionaries."""
        config = Config()
        config.set("models", {})
        assert config.get("models") == {}

    def test_multiple_config_instances_are_independent(self) -> None:
        """Test that multiple Config instances are independent."""
        config1 = Config()
        config2 = Config()
        
        config1.set("log_level", "DEBUG")
        assert config2.get("log_level") == "INFO"

    def test_config_get_with_deeply_nested_key(self) -> None:
        """Test get() with deeply nested keys in valid config."""
        config = Config()
        # Set valid top-level config first
        config.set("models.test.provider", "openai")
        config.set("models.test.model_name", "gpt-4")
        # Then set deeply nested value
        config.set("models.test.nested.deep.value", "test")
        assert config.get("models.test.nested.deep.value") == "test"

    def test_config_merge_with_empty_dict(self) -> None:
        """Test merge() with empty dictionary."""
        config = Config()
        original = config.to_dict()
        config.merge({})
        assert config.to_dict() == original
