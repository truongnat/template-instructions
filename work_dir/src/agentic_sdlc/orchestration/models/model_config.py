"""Model configuration and management."""

from dataclasses import dataclass
from typing import Any, Dict, Optional


@dataclass
class ModelConfig:
    """Configuration for a language model.
    
    Defines the provider, model name, and parameters for interacting
    with a language model service.
    """
    
    provider: str
    model_name: str
    api_key: Optional[str] = None
    temperature: float = 0.7
    max_tokens: Optional[int] = None
    timeout: int = 30
    metadata: Dict[str, Any] = None
    
    def __post_init__(self) -> None:
        """Validate model configuration."""
        if not self.provider:
            raise ValueError("Model provider cannot be empty")
        if not self.model_name:
            raise ValueError("Model name cannot be empty")
        if not 0.0 <= self.temperature <= 2.0:
            raise ValueError("Temperature must be between 0.0 and 2.0")
        if self.max_tokens is not None and self.max_tokens < 1:
            raise ValueError("max_tokens must be at least 1")
        if self.timeout < 1:
            raise ValueError("timeout must be at least 1")
        if self.metadata is None:
            self.metadata = {}
