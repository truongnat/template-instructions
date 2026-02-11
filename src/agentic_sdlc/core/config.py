"""Configuration management for the SDK.

This module provides the Config class for loading, managing, and validating
SDK configuration from multiple sources (files, environment variables, defaults).
"""

import json
import os
from pathlib import Path
from typing import Any, Dict, Optional, Union

import yaml
from pydantic import ValidationError as PydanticValidationError

from .exceptions import ConfigurationError, ValidationError
from .types import SDKConfig


class Config:
    """Central configuration management for the SDK.
    
    Loads configuration from multiple sources with proper precedence:
    1. Defaults (lowest priority)
    2. Configuration file (YAML or JSON)
    3. Environment variables
    4. Programmatic API calls (highest priority)
    
    Supports dot notation for accessing nested values (e.g., "models.openai.temperature").
    """

    def __init__(self, config_path: Optional[Union[str, Path]] = None) -> None:
        """Initialize configuration.
        
        Args:
            config_path: Optional path to configuration file (YAML or JSON)
            
        Raises:
            ConfigurationError: If configuration file cannot be loaded
            ValidationError: If configuration is invalid
        """
        self._config: Dict[str, Any] = self._get_defaults()
        
        if config_path:
            file_config = self._load_from_file(config_path)
            self._config = self._merge_dicts(self._config, file_config)
        
        env_config = self._load_from_env()
        self._config = self._merge_dicts(self._config, env_config)
        
        self.validate()

    def get(self, key: str, default: Any = None) -> Any:
        """Get configuration value with dot notation support.
        
        Args:
            key: Configuration key (supports dot notation, e.g., "models.openai.temperature")
            default: Default value if key not found
            
        Returns:
            Configuration value or default
        """
        keys = key.split(".")
        value = self._config
        
        for k in keys:
            if isinstance(value, dict):
                value = value.get(k)
                if value is None:
                    return default
            else:
                return default
        
        return value

    def set(self, key: str, value: Any) -> None:
        """Set configuration value with validation.
        
        Args:
            key: Configuration key (supports dot notation)
            value: Value to set
            
        Raises:
            ValidationError: If value is invalid
        """
        keys = key.split(".")
        
        # Navigate to the parent dict
        current = self._config
        for k in keys[:-1]:
            if k not in current:
                current[k] = {}
            current = current[k]
        
        # Set the value
        current[keys[-1]] = value
        
        # Validate the entire configuration
        self.validate()

    def validate(self) -> None:
        """Validate entire configuration against schema.
        
        Raises:
            ValidationError: If configuration is invalid
        """
        try:
            # Use model_validate with validation_context to allow partial configs
            SDKConfig.model_validate(self._config)
        except PydanticValidationError as e:
            # Convert Pydantic validation errors to SDK ValidationError
            error_details = []
            for error in e.errors():
                field = ".".join(str(x) for x in error["loc"])
                msg = error["msg"]
                error_details.append(f"{field}: {msg}")
            
            raise ValidationError(
                "Configuration validation failed",
                context={
                    "errors": error_details,
                    "config": self._config,
                },
            ) from e

    def merge(self, other: Dict[str, Any]) -> None:
        """Merge additional configuration with proper precedence.
        
        User-provided values override defaults. Merging is idempotent.
        
        Args:
            other: Configuration dictionary to merge
            
        Raises:
            ValidationError: If merged configuration is invalid
        """
        self._config = self._merge_dicts(self._config, other)
        self.validate()

    def to_dict(self) -> Dict[str, Any]:
        """Get configuration as dictionary.
        
        Returns:
            Configuration dictionary
        """
        return self._config.copy()

    @staticmethod
    def _get_defaults() -> Dict[str, Any]:
        """Get default configuration.
        
        Returns:
            Default configuration dictionary
        """
        return {
            "project_root": ".",
            "log_level": "INFO",
            "log_file": None,
            "models": {},
            "workflows": {},
            "plugins": [],
            "defaults_dir": None,
        }

    @staticmethod
    def _load_from_file(config_path: Union[str, Path]) -> Dict[str, Any]:
        """Load configuration from file.
        
        Args:
            config_path: Path to configuration file (YAML or JSON)
            
        Returns:
            Configuration dictionary
            
        Raises:
            ConfigurationError: If file cannot be loaded or parsed
        """
        path = Path(config_path)
        
        if not path.exists():
            raise ConfigurationError(
                f"Configuration file not found: {path}",
                context={"path": str(path)},
            )
        
        try:
            if path.suffix in [".yaml", ".yml"]:
                with open(path, "r") as f:
                    config = yaml.safe_load(f) or {}
            elif path.suffix == ".json":
                with open(path, "r") as f:
                    config = json.load(f)
            else:
                raise ConfigurationError(
                    f"Unsupported configuration file format: {path.suffix}",
                    context={"path": str(path), "supported": [".yaml", ".yml", ".json"]},
                )
            
            return config if isinstance(config, dict) else {}
        except (yaml.YAMLError, json.JSONDecodeError) as e:
            raise ConfigurationError(
                f"Failed to parse configuration file: {path}",
                context={"path": str(path), "error": str(e)},
            ) from e

    @staticmethod
    def _load_from_env() -> Dict[str, Any]:
        """Load configuration from environment variables.
        
        Environment variables should be prefixed with AGENTIC_SDLC_ and use
        underscores for nested keys (e.g., AGENTIC_SDLC_LOG_LEVEL).
        
        Returns:
            Configuration dictionary from environment
        """
        config: Dict[str, Any] = {}
        prefix = "AGENTIC_SDLC_"
        
        for key, value in os.environ.items():
            if key.startswith(prefix):
                config_key = key[len(prefix):].lower()
                config[config_key] = value
        
        return config

    @staticmethod
    def _merge_dicts(base: Dict[str, Any], override: Dict[str, Any]) -> Dict[str, Any]:
        """Merge two dictionaries with override taking precedence.
        
        Args:
            base: Base dictionary
            override: Override dictionary
            
        Returns:
            Merged dictionary
        """
        result = base.copy()
        
        for key, value in override.items():
            if key in result and isinstance(result[key], dict) and isinstance(value, dict):
                result[key] = Config._merge_dicts(result[key], value)
            else:
                result[key] = value
        
        return result


def load_config(config_path: Optional[Union[str, Path]] = None) -> Config:
    """Load configuration from file or defaults.
    
    Args:
        config_path: Optional path to configuration file
        
    Returns:
        Loaded Config instance
        
    Raises:
        ConfigurationError: If configuration cannot be loaded
        ValidationError: If configuration is invalid
    """
    return Config(config_path)


def get_config(config_path: Optional[Union[str, Path]] = None) -> Config:
    """Get configuration instance (alias for load_config).
    
    Args:
        config_path: Optional path to configuration file
        
    Returns:
        Config instance
    """
    return load_config(config_path)
