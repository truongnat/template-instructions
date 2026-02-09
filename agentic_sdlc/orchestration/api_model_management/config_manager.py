"""Configuration management for API Model Management system."""

import json
import logging
from pathlib import Path
from typing import Any, Dict, Optional
from datetime import datetime
import jsonschema
from jsonschema import ValidationError

from .exceptions import ConfigurationError

logger = logging.getLogger(__name__)


class ConfigManager:
    """Manages configuration loading, validation, and hot reload."""
    
    # Default configuration values
    DEFAULT_CONFIG = {
        "health_check": {
            "interval_seconds": 60,
            "timeout_seconds": 10,
            "consecutive_failures_threshold": 3
        },
        "rate_limiting": {
            "threshold_percent": 90,
            "window_seconds": 60
        },
        "caching": {
            "enabled": True,
            "max_size_mb": 1000,
            "default_ttl_seconds": 3600
        },
        "budget": {
            "daily_limit": 100.0,
            "alert_threshold_percent": 80
        },
        "quality_evaluation": {
            "enabled": True,
            "threshold": 0.7,
            "evaluation_window": 10
        },
        "failover": {
            "max_retries": 3,
            "base_backoff_seconds": 2,
            "alert_threshold": 3,
            "alert_window_hours": 1
        },
        "concurrency": {
            "max_concurrent_requests_per_provider": 10
        }
    }
    
    def __init__(
        self,
        config_path: Path,
        schema_path: Optional[Path] = None,
        environment: str = "production"
    ):
        """
        Initialize configuration manager.
        
        Args:
            config_path: Path to configuration file
            schema_path: Path to JSON schema file (optional)
            environment: Environment name (development, staging, production)
        """
        self.config_path = Path(config_path)
        self.environment = environment
        
        # Default schema path if not provided
        if schema_path is None:
            schema_path = self.config_path.parent / "schema.json"
        self.schema_path = Path(schema_path)
        
        self._config: Dict[str, Any] = {}
        self._schema: Optional[Dict[str, Any]] = None
        self._last_modified: Optional[float] = None
        
        # Load schema and configuration
        self._load_schema()
        self.load_config()
    
    def _load_schema(self) -> None:
        """Load JSON schema for validation."""
        try:
            if self.schema_path.exists():
                with open(self.schema_path, 'r') as f:
                    self._schema = json.load(f)
                logger.info(f"Loaded configuration schema from {self.schema_path}")
            else:
                logger.warning(f"Schema file not found at {self.schema_path}, validation will be skipped")
                self._schema = None
        except Exception as e:
            logger.error(f"Failed to load schema from {self.schema_path}: {e}")
            self._schema = None
    
    def load_config(self) -> None:
        """
        Load configuration from file.
        
        Raises:
            ConfigurationError: If configuration is invalid or cannot be loaded
        """
        try:
            if not self.config_path.exists():
                raise ConfigurationError(
                    f"Configuration file not found: {self.config_path}"
                )
            
            with open(self.config_path, 'r') as f:
                config = json.load(f)
            
            # Validate configuration
            self._validate_config(config)
            
            # Merge with defaults
            self._config = self._merge_with_defaults(config)
            
            # Update last modified timestamp
            self._last_modified = self.config_path.stat().st_mtime
            
            logger.info(
                f"Loaded configuration from {self.config_path} "
                f"(environment: {self.environment})"
            )
            
        except json.JSONDecodeError as e:
            error_msg = f"Invalid JSON in configuration file: {e}"
            logger.error(error_msg)
            raise ConfigurationError(error_msg)
        except ValidationError as e:
            error_msg = f"Configuration validation failed: {e.message}"
            logger.error(error_msg)
            logger.error(f"Validation error at path: {'.'.join(str(p) for p in e.path)}")
            # Use default configuration on validation error
            logger.warning("Using default configuration values")
            self._config = self.DEFAULT_CONFIG.copy()
            self._config["models"] = []
        except Exception as e:
            error_msg = f"Failed to load configuration: {e}"
            logger.error(error_msg)
            raise ConfigurationError(error_msg)
    
    def _validate_config(self, config: Dict[str, Any]) -> None:
        """
        Validate configuration against schema.
        
        Args:
            config: Configuration dictionary to validate
            
        Raises:
            ValidationError: If configuration doesn't match schema
        """
        if self._schema is None:
            logger.warning("No schema available, skipping validation")
            return
        
        try:
            jsonschema.validate(instance=config, schema=self._schema)
            logger.debug("Configuration validation successful")
        except ValidationError as e:
            # Log detailed validation errors
            logger.error(f"Configuration validation failed: {e.message}")
            if e.path:
                logger.error(f"Error location: {'.'.join(str(p) for p in e.path)}")
            if e.schema_path:
                logger.error(f"Schema path: {'.'.join(str(p) for p in e.schema_path)}")
            raise
    
    def _merge_with_defaults(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """
        Merge configuration with default values.
        
        Args:
            config: User configuration
            
        Returns:
            Merged configuration with defaults
        """
        merged = self.DEFAULT_CONFIG.copy()
        
        # Deep merge for nested dictionaries
        for key, value in config.items():
            if key in merged and isinstance(merged[key], dict) and isinstance(value, dict):
                merged[key] = {**merged[key], **value}
            else:
                merged[key] = value
        
        return merged
    
    def reload_config(self) -> bool:
        """
        Reload configuration if file has been modified.
        
        Returns:
            True if configuration was reloaded, False otherwise
        """
        try:
            if not self.config_path.exists():
                logger.warning(f"Configuration file not found: {self.config_path}")
                return False
            
            current_mtime = self.config_path.stat().st_mtime
            
            if self._last_modified is None or current_mtime > self._last_modified:
                logger.info("Configuration file modified, reloading...")
                self.load_config()
                return True
            
            return False
            
        except Exception as e:
            logger.error(f"Failed to reload configuration: {e}")
            return False
    
    def get_config(self) -> Dict[str, Any]:
        """
        Get current configuration.
        
        Returns:
            Configuration dictionary
        """
        return self._config.copy()
    
    def get(self, key: str, default: Any = None) -> Any:
        """
        Get configuration value by key.
        
        Args:
            key: Configuration key (supports dot notation for nested keys)
            default: Default value if key not found
            
        Returns:
            Configuration value or default
        """
        keys = key.split('.')
        value = self._config
        
        for k in keys:
            if isinstance(value, dict) and k in value:
                value = value[k]
            else:
                return default
        
        return value
    
    def get_models(self) -> list:
        """
        Get list of configured models.
        
        Returns:
            List of model configurations
        """
        return self._config.get("models", [])
    
    def get_health_check_config(self) -> Dict[str, Any]:
        """Get health check configuration."""
        return self._config.get("health_check", self.DEFAULT_CONFIG["health_check"])
    
    def get_rate_limiting_config(self) -> Dict[str, Any]:
        """Get rate limiting configuration."""
        return self._config.get("rate_limiting", self.DEFAULT_CONFIG["rate_limiting"])
    
    def get_caching_config(self) -> Dict[str, Any]:
        """Get caching configuration."""
        return self._config.get("caching", self.DEFAULT_CONFIG["caching"])
    
    def get_budget_config(self) -> Dict[str, Any]:
        """Get budget configuration."""
        return self._config.get("budget", self.DEFAULT_CONFIG["budget"])
    
    def get_quality_evaluation_config(self) -> Dict[str, Any]:
        """Get quality evaluation configuration."""
        return self._config.get("quality_evaluation", self.DEFAULT_CONFIG["quality_evaluation"])
    
    def get_failover_config(self) -> Dict[str, Any]:
        """Get failover configuration."""
        return self._config.get("failover", self.DEFAULT_CONFIG["failover"])
    
    def get_concurrency_config(self) -> Dict[str, Any]:
        """Get concurrency configuration."""
        return self._config.get("concurrency", self.DEFAULT_CONFIG["concurrency"])
    
    def get_environment_config(self, env: Optional[str] = None) -> Dict[str, Any]:
        """
        Get environment-specific configuration.
        
        Args:
            env: Environment name (uses self.environment if not provided)
            
        Returns:
            Environment-specific configuration or empty dict
        """
        env = env or self.environment
        env_config_path = self.config_path.parent / f"config.{env}.json"
        
        if not env_config_path.exists():
            return {}
        
        try:
            with open(env_config_path, 'r') as f:
                env_config = json.load(f)
            logger.info(f"Loaded environment-specific config from {env_config_path}")
            return env_config
        except Exception as e:
            logger.error(f"Failed to load environment config: {e}")
            return {}
    
    def validate_current_config(self) -> bool:
        """
        Validate current configuration.
        
        Returns:
            True if valid, False otherwise
        """
        try:
            self._validate_config(self._config)
            return True
        except ValidationError:
            return False
    
    def get_last_modified(self) -> Optional[datetime]:
        """
        Get last modification time of configuration file.
        
        Returns:
            Last modification datetime or None
        """
        if self._last_modified is None:
            return None
        return datetime.fromtimestamp(self._last_modified)
