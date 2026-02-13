"""Unit tests for orchestration models module."""

import pytest

from agentic_sdlc.orchestration import (
    ModelClient,
    ModelConfig,
    create_model_client,
    get_model_client,
    register_model_client,
)


class TestModelConfig:
    """Tests for ModelConfig class."""
    
    def test_model_config_creation(self) -> None:
        """Test creating a model configuration."""
        config = ModelConfig(
            provider="openai",
            model_name="gpt-4",
        )
        assert config.provider == "openai"
        assert config.model_name == "gpt-4"
        assert config.temperature == 0.7
        assert config.timeout == 30
    
    def test_model_config_with_all_parameters(self) -> None:
        """Test creating a model configuration with all parameters."""
        config = ModelConfig(
            provider="openai",
            model_name="gpt-4",
            api_key="test-key",
            temperature=0.5,
            max_tokens=1000,
            timeout=60,
        )
        assert config.api_key == "test-key"
        assert config.temperature == 0.5
        assert config.max_tokens == 1000
        assert config.timeout == 60
    
    def test_model_config_empty_provider_raises_error(self) -> None:
        """Test that empty provider raises ValueError."""
        with pytest.raises(ValueError, match="Model provider cannot be empty"):
            ModelConfig(provider="", model_name="gpt-4")
    
    def test_model_config_empty_model_name_raises_error(self) -> None:
        """Test that empty model_name raises ValueError."""
        with pytest.raises(ValueError, match="Model name cannot be empty"):
            ModelConfig(provider="openai", model_name="")
    
    def test_model_config_invalid_temperature_raises_error(self) -> None:
        """Test that invalid temperature raises ValueError."""
        with pytest.raises(ValueError, match="Temperature must be between"):
            ModelConfig(provider="openai", model_name="gpt-4", temperature=3.0)
    
    def test_model_config_negative_temperature_raises_error(self) -> None:
        """Test that negative temperature raises ValueError."""
        with pytest.raises(ValueError, match="Temperature must be between"):
            ModelConfig(provider="openai", model_name="gpt-4", temperature=-0.5)
    
    def test_model_config_invalid_max_tokens_raises_error(self) -> None:
        """Test that invalid max_tokens raises ValueError."""
        with pytest.raises(ValueError, match="max_tokens must be at least 1"):
            ModelConfig(provider="openai", model_name="gpt-4", max_tokens=0)
    
    def test_model_config_invalid_timeout_raises_error(self) -> None:
        """Test that invalid timeout raises ValueError."""
        with pytest.raises(ValueError, match="timeout must be at least 1"):
            ModelConfig(provider="openai", model_name="gpt-4", timeout=0)
    
    def test_model_config_metadata_initialization(self) -> None:
        """Test that metadata is initialized as empty dict."""
        config = ModelConfig(provider="openai", model_name="gpt-4")
        assert config.metadata == {}


class TestModelClient:
    """Tests for ModelClient class."""
    
    def test_model_client_creation(self) -> None:
        """Test creating a model client."""
        config = ModelConfig(provider="openai", model_name="gpt-4")
        client = ModelClient(config)
        assert client.config == config
    
    def test_model_client_generate_not_implemented(self) -> None:
        """Test that generate raises NotImplementedError."""
        config = ModelConfig(provider="openai", model_name="gpt-4")
        client = ModelClient(config)
        with pytest.raises(NotImplementedError):
            client.generate("test prompt")
    
    def test_model_client_generate_with_context_not_implemented(self) -> None:
        """Test that generate_with_context raises NotImplementedError."""
        config = ModelConfig(provider="openai", model_name="gpt-4")
        client = ModelClient(config)
        with pytest.raises(NotImplementedError):
            client.generate_with_context("test prompt", {})


class TestCreateModelClient:
    """Tests for create_model_client function."""
    
    def test_create_model_client(self) -> None:
        """Test creating a model client from config."""
        config = ModelConfig(provider="openai", model_name="gpt-4")
        client = create_model_client(config)
        assert isinstance(client, ModelClient)
        assert client.config == config


class TestModelClientRegistry:
    """Tests for model client registry functions."""
    
    def test_register_and_get_model_client(self) -> None:
        """Test registering and retrieving a model client."""
        config = ModelConfig(provider="openai", model_name="gpt-4")
        client = ModelClient(config)
        
        register_model_client("openai", "gpt-4", client)
        retrieved = get_model_client("openai", "gpt-4")
        
        assert retrieved == client
    
    def test_get_nonexistent_model_client(self) -> None:
        """Test getting a nonexistent model client returns None."""
        client = get_model_client("nonexistent", "model")
        assert client is None
    
    def test_register_multiple_model_clients(self) -> None:
        """Test registering multiple model clients."""
        config1 = ModelConfig(provider="openai", model_name="gpt-4")
        config2 = ModelConfig(provider="anthropic", model_name="claude-3")
        
        client1 = ModelClient(config1)
        client2 = ModelClient(config2)
        
        register_model_client("openai", "gpt-4", client1)
        register_model_client("anthropic", "claude-3", client2)
        
        assert get_model_client("openai", "gpt-4") == client1
        assert get_model_client("anthropic", "claude-3") == client2
