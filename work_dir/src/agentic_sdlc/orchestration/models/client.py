"""Model client for interacting with language models."""

from typing import Any, Dict, Optional

from .model_config import ModelConfig


class ModelClient:
    """Client for interacting with language models.
    
    Provides a unified interface for communicating with different
    language model providers.
    """
    
    def __init__(self, config: ModelConfig) -> None:
        """Initialize the model client.
        
        Args:
            config: The model configuration
        """
        self.config = config
    
    def generate(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        **kwargs: Any,
    ) -> str:
        """Generate a response from the model.
        
        Args:
            prompt: The user prompt
            system_prompt: Optional system prompt
            **kwargs: Additional parameters for the model
            
        Returns:
            The model's response
            
        Raises:
            NotImplementedError: This is a base implementation
        """
        raise NotImplementedError("Subclasses must implement generate()")
    
    def generate_with_context(
        self,
        prompt: str,
        context: Dict[str, Any],
        system_prompt: Optional[str] = None,
        **kwargs: Any,
    ) -> str:
        """Generate a response with additional context.
        
        Args:
            prompt: The user prompt
            context: Additional context information
            system_prompt: Optional system prompt
            **kwargs: Additional parameters for the model
            
        Returns:
            The model's response
        """
        raise NotImplementedError("Subclasses must implement generate_with_context()")


# Global model client registry
_model_clients: Dict[str, ModelClient] = {}


def get_model_client(provider: str, model_name: str) -> Optional[ModelClient]:
    """Get a model client by provider and model name.
    
    Args:
        provider: The model provider
        model_name: The model name
        
    Returns:
        The ModelClient if found, None otherwise
    """
    key = f"{provider}:{model_name}"
    return _model_clients.get(key)


def register_model_client(
    provider: str,
    model_name: str,
    client: ModelClient,
) -> None:
    """Register a model client.
    
    Args:
        provider: The model provider
        model_name: The model name
        client: The ModelClient instance
    """
    key = f"{provider}:{model_name}"
    _model_clients[key] = client


def create_model_client(config: ModelConfig) -> ModelClient:
    """Create a model client from configuration.
    
    Args:
        config: The model configuration
        
    Returns:
        A new ModelClient instance
    """
    return ModelClient(config)
