"""
API Key Manager for API Model Management system.

This module provides secure management and rotation of API keys for multiple
AI model providers. It supports loading keys from environment variables,
validation, and round-robin rotation for load distribution.
"""

import os
import logging
from pathlib import Path
from typing import Optional, Dict, List
from dotenv import load_dotenv

from .exceptions import AuthenticationError, ConfigurationError


logger = logging.getLogger(__name__)


class APIKeyManager:
    """
    Manages API keys for multiple providers with support for key rotation.
    
    Features:
    - Load API keys from environment variables
    - Support multiple keys per provider for load distribution
    - Round-robin key rotation
    - Startup validation of required keys
    - Secure key handling (keys never logged)
    
    Environment Variable Convention:
    - Primary key: {PROVIDER}_API_KEY (e.g., OPENAI_API_KEY)
    - Additional keys: {PROVIDER}_API_KEY_2, {PROVIDER}_API_KEY_3, etc.
    - Ollama: OLLAMA_BASE_URL (no key required for local)
    """
    
    def __init__(self, env_file: Optional[Path] = None):
        """
        Initialize API key manager.
        
        Args:
            env_file: Optional path to .env file for loading environment variables
        """
        self.env_file = env_file
        self._keys: Dict[str, List[str]] = {}
        self._key_indices: Dict[str, int] = {}
        self._disabled_providers: List[str] = []
        
        # Load environment variables if env_file is provided
        if env_file and env_file.exists():
            load_dotenv(env_file)
        
        logger.info("APIKeyManager initialized")
    
    def load_keys(self) -> None:
        """
        Load API keys from environment variables.
        
        Loads keys for all supported providers following the naming convention:
        - OPENAI_API_KEY, OPENAI_API_KEY_2, OPENAI_API_KEY_3, ...
        - ANTHROPIC_API_KEY, ANTHROPIC_API_KEY_2, ...
        - GOOGLE_API_KEY, GOOGLE_API_KEY_2, ...
        - OLLAMA_BASE_URL (special case for local Ollama)
        
        Keys are stored internally and never logged for security.
        """
        providers = ["OPENAI", "ANTHROPIC", "GOOGLE"]
        
        for provider in providers:
            provider_keys = []
            
            # Load primary key
            primary_key = os.getenv(f"{provider}_API_KEY")
            if primary_key:
                provider_keys.append(primary_key)
            
            # Load additional keys (KEY_2, KEY_3, etc.)
            key_index = 2
            while True:
                additional_key = os.getenv(f"{provider}_API_KEY_{key_index}")
                if additional_key:
                    provider_keys.append(additional_key)
                    key_index += 1
                else:
                    break
            
            if provider_keys:
                self._keys[provider.lower()] = provider_keys
                self._key_indices[provider.lower()] = 0
                logger.info(
                    f"Loaded {len(provider_keys)} API key(s) for provider: {provider.lower()}"
                )
            else:
                logger.debug(f"No API keys found for provider: {provider.lower()}")
        
        # Special handling for Ollama (uses base URL, not API key)
        ollama_url = os.getenv("OLLAMA_BASE_URL")
        if ollama_url:
            self._keys["ollama"] = [ollama_url]
            self._key_indices["ollama"] = 0
            logger.info(f"Loaded Ollama base URL")
        else:
            logger.debug("No Ollama base URL found")
    
    def get_key(self, provider: str) -> Optional[str]:
        """
        Get API key for provider with round-robin rotation.
        
        When multiple keys are available for a provider, this method rotates
        through them using round-robin selection to distribute load.
        
        Args:
            provider: Provider name (e.g., "openai", "anthropic", "google", "ollama")
        
        Returns:
            API key for the provider, or None if no key is available
        
        Example:
            >>> manager = APIKeyManager()
            >>> manager.load_keys()
            >>> key1 = manager.get_key("openai")  # Returns key 1
            >>> key2 = manager.get_key("openai")  # Returns key 2
            >>> key3 = manager.get_key("openai")  # Returns key 1 (rotated)
        """
        provider = provider.lower()
        
        if provider not in self._keys or not self._keys[provider]:
            logger.warning(f"No API key available for provider: {provider}")
            return None
        
        keys = self._keys[provider]
        current_index = self._key_indices[provider]
        
        # Get current key
        key = keys[current_index]
        
        # Rotate to next key (round-robin)
        self._key_indices[provider] = (current_index + 1) % len(keys)
        
        logger.debug(
            f"Retrieved API key for provider: {provider} "
            f"(key {current_index + 1} of {len(keys)})"
        )
        
        return key
    
    def validate_keys(self, required_providers: List[str]) -> Dict[str, bool]:
        """
        Validate that required API keys are present.
        
        Checks if API keys are available for all required providers.
        Logs warnings for missing keys and tracks disabled providers.
        
        Args:
            required_providers: List of provider names that require API keys
        
        Returns:
            Dictionary mapping provider names to validation status (True if valid)
        
        Example:
            >>> manager = APIKeyManager()
            >>> manager.load_keys()
            >>> status = manager.validate_keys(["openai", "anthropic"])
            >>> print(status)
            {'openai': True, 'anthropic': False}
        """
        validation_results = {}
        
        for provider in required_providers:
            provider_lower = provider.lower()
            has_key = provider_lower in self._keys and len(self._keys[provider_lower]) > 0
            
            validation_results[provider_lower] = has_key
            
            if not has_key:
                logger.warning(
                    f"Missing API key for enabled provider: {provider_lower}. "
                    f"Provider will be disabled."
                )
                if provider_lower not in self._disabled_providers:
                    self._disabled_providers.append(provider_lower)
            else:
                logger.info(f"API key validation passed for provider: {provider_lower}")
        
        return validation_results
    
    def add_key(self, provider: str, key: str) -> None:
        """
        Add API key for a provider.
        
        This method allows programmatic addition of API keys, useful for
        testing or dynamic configuration.
        
        Args:
            provider: Provider name (e.g., "openai", "anthropic")
            key: API key to add
        
        Raises:
            ValueError: If provider or key is empty
        
        Example:
            >>> manager = APIKeyManager()
            >>> manager.add_key("openai", "sk-test123")
            >>> manager.add_key("openai", "sk-test456")  # Adds second key
        """
        if not provider:
            raise ValueError("Provider name cannot be empty")
        if not key:
            raise ValueError("API key cannot be empty")
        
        provider = provider.lower()
        
        if provider not in self._keys:
            self._keys[provider] = []
            self._key_indices[provider] = 0
        
        self._keys[provider].append(key)
        
        # Remove from disabled providers if it was disabled
        if provider in self._disabled_providers:
            self._disabled_providers.remove(provider)
        
        logger.info(
            f"Added API key for provider: {provider} "
            f"(total keys: {len(self._keys[provider])})"
        )
    
    def get_available_providers(self) -> List[str]:
        """
        Get list of providers with valid API keys.
        
        Returns:
            List of provider names that have at least one API key configured
        """
        return [
            provider for provider in self._keys.keys()
            if self._keys[provider] and provider not in self._disabled_providers
        ]
    
    def get_key_count(self, provider: str) -> int:
        """
        Get number of API keys configured for a provider.
        
        Args:
            provider: Provider name
        
        Returns:
            Number of keys configured for the provider
        """
        provider = provider.lower()
        return len(self._keys.get(provider, []))
    
    def is_provider_enabled(self, provider: str) -> bool:
        """
        Check if a provider is enabled (has valid API keys).
        
        Args:
            provider: Provider name
        
        Returns:
            True if provider has API keys and is not disabled
        """
        provider = provider.lower()
        return (
            provider in self._keys and
            len(self._keys[provider]) > 0 and
            provider not in self._disabled_providers
        )
