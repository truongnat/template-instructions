"""
Model Registry for API Model Management system.

This module provides the ModelRegistry class which manages model metadata,
configuration loading, and query interfaces for model lookup.
"""

import json
import logging
from pathlib import Path
from typing import Optional, List, Dict, Any
from jsonschema import validate, ValidationError as JsonSchemaValidationError

from .models import ModelMetadata, RateLimits
from .exceptions import ConfigurationError

logger = logging.getLogger(__name__)


# JSON Schema for model configuration validation
MODEL_CONFIG_SCHEMA = {
    "type": "object",
    "properties": {
        "models": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "id": {"type": "string", "minLength": 1},
                    "provider": {"type": "string", "minLength": 1},
                    "name": {"type": "string", "minLength": 1},
                    "capabilities": {
                        "type": "array",
                        "items": {"type": "string"},
                        "minItems": 1
                    },
                    "cost_per_1k_input_tokens": {"type": "number", "minimum": 0},
                    "cost_per_1k_output_tokens": {"type": "number", "minimum": 0},
                    "rate_limits": {
                        "type": "object",
                        "properties": {
                            "requests_per_minute": {"type": "integer", "minimum": 1},
                            "tokens_per_minute": {"type": "integer", "minimum": 1}
                        },
                        "required": ["requests_per_minute", "tokens_per_minute"]
                    },
                    "context_window": {"type": "integer", "minimum": 1},
                    "average_response_time_ms": {"type": "number", "minimum": 0},
                    "enabled": {"type": "boolean"}
                },
                "required": [
                    "id", "provider", "name", "capabilities",
                    "cost_per_1k_input_tokens", "cost_per_1k_output_tokens",
                    "rate_limits", "context_window", "average_response_time_ms"
                ]
            }
        }
    },
    "required": ["models"]
}


class ModelRegistry:
    """
    Centralized repository for model metadata and configuration.
    
    The ModelRegistry loads model configurations from a JSON file, validates them,
    and provides query interfaces for model lookup by various criteria.
    """
    
    def __init__(self, config_path: Path):
        """
        Initialize the Model Registry.
        
        Args:
            config_path: Path to the JSON configuration file containing model metadata
        """
        self.config_path = Path(config_path)
        self._models: Dict[str, ModelMetadata] = {}
        self._config_data: Dict[str, Any] = {}
        
    def load_config(self) -> None:
        """
        Load model configurations from the JSON file.
        
        Validates the configuration against the schema and loads valid models
        into the registry. Invalid models are logged and excluded.
        
        Raises:
            ConfigurationError: If the configuration file cannot be read or is invalid
        """
        try:
            if not self.config_path.exists():
                raise ConfigurationError(
                    f"Configuration file not found: {self.config_path}",
                    config_path=str(self.config_path)
                )
            
            with open(self.config_path, 'r') as f:
                self._config_data = json.load(f)
            
            # Validate against schema
            try:
                validate(instance=self._config_data, schema=MODEL_CONFIG_SCHEMA)
            except JsonSchemaValidationError as e:
                raise ConfigurationError(
                    f"Configuration validation failed: {e.message}",
                    config_path=str(self.config_path),
                    validation_errors=[e.message]
                )
            
            # Load models
            loaded_count = 0
            error_count = 0
            
            for model_data in self._config_data.get("models", []):
                try:
                    model = self._parse_model(model_data)
                    self._models[model.id] = model
                    loaded_count += 1
                    logger.info(f"Loaded model: {model.id} ({model.provider})")
                except Exception as e:
                    error_count += 1
                    logger.error(
                        f"Failed to load model {model_data.get('id', 'unknown')}: {e}"
                    )
            
            logger.info(
                f"Model registry loaded: {loaded_count} models loaded, "
                f"{error_count} models failed"
            )
            
        except ConfigurationError:
            raise
        except Exception as e:
            raise ConfigurationError(
                f"Failed to load configuration: {e}",
                config_path=str(self.config_path)
            )
    
    def _parse_model(self, model_data: Dict[str, Any]) -> ModelMetadata:
        """
        Parse model data from configuration into ModelMetadata object.
        
        Args:
            model_data: Dictionary containing model configuration
            
        Returns:
            ModelMetadata object
            
        Raises:
            ValueError: If model data is invalid
        """
        rate_limits_data = model_data["rate_limits"]
        rate_limits = RateLimits(
            requests_per_minute=rate_limits_data["requests_per_minute"],
            tokens_per_minute=rate_limits_data["tokens_per_minute"]
        )
        
        return ModelMetadata(
            id=model_data["id"],
            provider=model_data["provider"],
            name=model_data["name"],
            capabilities=model_data["capabilities"],
            cost_per_1k_input_tokens=model_data["cost_per_1k_input_tokens"],
            cost_per_1k_output_tokens=model_data["cost_per_1k_output_tokens"],
            rate_limits=rate_limits,
            context_window=model_data["context_window"],
            average_response_time_ms=model_data["average_response_time_ms"],
            enabled=model_data.get("enabled", True)
        )
    
    def get_model(self, model_id: str) -> Optional[ModelMetadata]:
        """
        Retrieve model metadata by ID.
        
        Args:
            model_id: Unique identifier for the model
            
        Returns:
            ModelMetadata if found, None otherwise
        """
        return self._models.get(model_id)
    
    def get_models_by_provider(self, provider: str) -> List[ModelMetadata]:
        """
        Get all models for a specific provider.
        
        Args:
            provider: Provider name (e.g., "openai", "anthropic")
            
        Returns:
            List of ModelMetadata objects for the specified provider
        """
        return [
            model for model in self._models.values()
            if model.provider == provider
        ]
    
    def get_models_by_capability(self, capability: str) -> List[ModelMetadata]:
        """
        Get models that support a specific capability.
        
        Args:
            capability: Capability name (e.g., "text-generation", "code-generation")
            
        Returns:
            List of ModelMetadata objects that support the capability
        """
        return [
            model for model in self._models.values()
            if capability in model.capabilities
        ]
    
    def get_models_by_cost_range(
        self,
        min_cost: float,
        max_cost: float
    ) -> List[ModelMetadata]:
        """
        Get models within a cost range.
        
        Cost is calculated as the average of input and output token costs.
        
        Args:
            min_cost: Minimum cost per 1k tokens
            max_cost: Maximum cost per 1k tokens
            
        Returns:
            List of ModelMetadata objects within the cost range
        """
        result = []
        for model in self._models.values():
            avg_cost = (
                model.cost_per_1k_input_tokens + model.cost_per_1k_output_tokens
            ) / 2
            if min_cost <= avg_cost <= max_cost:
                result.append(model)
        return result
    
    def update_model(self, model_id: str, metadata: ModelMetadata) -> bool:
        """
        Update model metadata in the registry.
        
        Args:
            model_id: ID of the model to update
            metadata: New ModelMetadata object
            
        Returns:
            True if update was successful, False if model not found
        """
        if model_id not in self._models:
            logger.warning(f"Cannot update non-existent model: {model_id}")
            return False
        
        self._models[model_id] = metadata
        logger.info(f"Updated model: {model_id}")
        
        # Update config data for persistence
        self._update_config_data(metadata)
        self._persist_config()
        
        return True
    
    def add_model(self, metadata: ModelMetadata) -> bool:
        """
        Add a new model to the registry.
        
        Args:
            metadata: ModelMetadata object for the new model
            
        Returns:
            True if model was added, False if model already exists
        """
        if metadata.id in self._models:
            logger.warning(f"Model already exists: {metadata.id}")
            return False
        
        self._models[metadata.id] = metadata
        logger.info(f"Added new model: {metadata.id}")
        
        # Update config data for persistence
        self._add_to_config_data(metadata)
        self._persist_config()
        
        return True
    
    def _update_config_data(self, metadata: ModelMetadata) -> None:
        """Update the config data dictionary with model metadata."""
        models_list = self._config_data.get("models", [])
        
        for i, model_data in enumerate(models_list):
            if model_data["id"] == metadata.id:
                models_list[i] = self._model_to_dict(metadata)
                break
    
    def _add_to_config_data(self, metadata: ModelMetadata) -> None:
        """Add model metadata to the config data dictionary."""
        if "models" not in self._config_data:
            self._config_data["models"] = []
        
        self._config_data["models"].append(self._model_to_dict(metadata))
    
    def _model_to_dict(self, metadata: ModelMetadata) -> Dict[str, Any]:
        """Convert ModelMetadata to dictionary for JSON serialization."""
        return {
            "id": metadata.id,
            "provider": metadata.provider,
            "name": metadata.name,
            "capabilities": metadata.capabilities,
            "cost_per_1k_input_tokens": metadata.cost_per_1k_input_tokens,
            "cost_per_1k_output_tokens": metadata.cost_per_1k_output_tokens,
            "rate_limits": {
                "requests_per_minute": metadata.rate_limits.requests_per_minute,
                "tokens_per_minute": metadata.rate_limits.tokens_per_minute
            },
            "context_window": metadata.context_window,
            "average_response_time_ms": metadata.average_response_time_ms,
            "enabled": metadata.enabled
        }
    
    def _persist_config(self) -> None:
        """Persist the current configuration to the JSON file."""
        try:
            with open(self.config_path, 'w') as f:
                json.dump(self._config_data, f, indent=2)
            logger.debug(f"Configuration persisted to {self.config_path}")
        except Exception as e:
            logger.error(f"Failed to persist configuration: {e}")
