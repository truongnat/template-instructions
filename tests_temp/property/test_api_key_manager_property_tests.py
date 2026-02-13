"""
Property-based tests for APIKeyManager class.

This module tests the correctness properties of the APIKeyManager including
API key loading, validation, multiple key support, and round-robin rotation.
"""

import unittest
import os
import tempfile
from pathlib import Path
from typing import Dict, List

try:
    from hypothesis import given, strategies as st, settings, assume
    HYPOTHESIS_AVAILABLE = True
except ImportError:
    HYPOTHESIS_AVAILABLE = False
    
    def given(*args, **kwargs):
        def decorator(func):
            return func
        return decorator
    
    class MockStrategies:
        def text(self, **kwargs): return lambda: "test"
        def integers(self, **kwargs): return lambda: 1
        def lists(self, *args, **kwargs): return lambda: []
        def dictionaries(self, *args, **kwargs): return lambda: {}
        def sampled_from(self, seq): return lambda: seq[0] if seq else None
        def builds(self, cls, **kwargs): return lambda: cls(**kwargs)
    
    st = MockStrategies()
    
    def settings(**kwargs):
        def decorator(func):
            return func
        return decorator

from agentic_sdlc.orchestration.api_model_management.api_key_manager import APIKeyManager


# Hypothesis strategies for generating test data

def provider_strategy():
    """Strategy for generating provider names"""
    return st.sampled_from(["openai", "anthropic", "google", "ollama"])


def provider_strategy_no_ollama():
    """Strategy for generating provider names (excluding ollama which only supports single URL)"""
    return st.sampled_from(["openai", "anthropic", "google"])


def api_key_strategy():
    """Strategy for generating API keys"""
    return st.text(
        min_size=10,
        max_size=100,
        alphabet=st.characters(
            whitelist_categories=('Lu', 'Ll', 'Nd'),
            whitelist_characters='-_'
        )
    )


def provider_keys_strategy():
    """Strategy for generating provider-key mappings"""
    return st.dictionaries(
        keys=provider_strategy(),
        values=st.lists(api_key_strategy(), min_size=1, max_size=5),
        min_size=1,
        max_size=4
    )


class TestAPIKeyManagerProperties(unittest.TestCase):
    """Test APIKeyManager correctness properties"""
    
    def setUp(self):
        """Set up test case"""
        if not HYPOTHESIS_AVAILABLE:
            self.skipTest("Hypothesis not available")
        
        # Store original environment
        self.original_env = os.environ.copy()
        
        # Create temporary directory for .env files
        self.temp_dir = tempfile.mkdtemp()
        self.env_file = Path(self.temp_dir) / ".env"
    
    def tearDown(self):
        """Clean up after test"""
        # Restore original environment
        os.environ.clear()
        os.environ.update(self.original_env)
    
    def _set_env_keys(self, provider_keys: Dict[str, List[str]]) -> None:
        """Helper to set environment variables for API keys"""
        # Clear existing API key environment variables
        for key in list(os.environ.keys()):
            if 'API_KEY' in key or 'OLLAMA_BASE_URL' in key:
                del os.environ[key]
        
        # Set new keys
        for provider, keys in provider_keys.items():
            provider_upper = provider.upper()
            
            if provider == "ollama":
                # Ollama uses OLLAMA_BASE_URL instead of API_KEY
                if keys:
                    os.environ["OLLAMA_BASE_URL"] = keys[0]
            else:
                # Set primary key
                if keys:
                    os.environ[f"{provider_upper}_API_KEY"] = keys[0]
                
                # Set additional keys
                for i, key in enumerate(keys[1:], start=2):
                    os.environ[f"{provider_upper}_API_KEY_{i}"] = key
    
    @settings(max_examples=5)
    @given(provider_keys=provider_keys_strategy())
    def test_property_23_api_key_loading_from_environment(self, provider_keys: Dict[str, List[str]]):
        """
        Feature: api-model-management
        Property 23: API key loading from environment
        
        For any provider with API keys in environment variables following the
        naming convention, all keys should be loaded and accessible.
        
        Note: Ollama only loads a single base URL (OLLAMA_BASE_URL), not multiple keys.
        
        Validates: Requirements 6.1
        """
        # Set environment variables
        self._set_env_keys(provider_keys)
        
        # Create manager and load keys
        manager = APIKeyManager()
        manager.load_keys()
        
        # Verify all keys are loaded
        for provider, expected_keys in provider_keys.items():
            # Special handling for Ollama - it only loads one base URL
            if provider == "ollama":
                expected_keys = expected_keys[:1]  # Only first URL is loaded
            
            # Check that all keys are accessible
            retrieved_keys = []
            for _ in range(len(expected_keys)):
                key = manager.get_key(provider)
                self.assertIsNotNone(key, f"Key should be available for provider: {provider}")
                retrieved_keys.append(key)
            
            # Verify all expected keys were retrieved (may be in different order due to rotation)
            self.assertEqual(
                set(retrieved_keys),
                set(expected_keys),
                f"All keys should be loaded for provider: {provider}"
            )
            
            # Verify key count
            self.assertEqual(
                manager.get_key_count(provider),
                len(expected_keys),
                f"Key count should match for provider: {provider}"
            )
    
    @settings(max_examples=5)
    @given(
        enabled_providers=st.lists(
            provider_strategy(),
            min_size=1,
            max_size=4,
            unique=True
        ),
        available_providers=st.lists(
            provider_strategy(),
            min_size=0,
            max_size=3,
            unique=True
        )
    )
    def test_property_24_missing_key_handling(
        self,
        enabled_providers: List[str],
        available_providers: List[str]
    ):
        """
        Feature: api-model-management
        Property 24: Missing key handling
        
        For any enabled provider with missing API keys, a warning should be
        logged and the provider should be disabled.
        
        Validates: Requirements 6.3
        """
        # Set up environment with only some providers having keys
        provider_keys = {}
        for provider in available_providers:
            provider_keys[provider] = [f"test-key-{provider}"]
        
        self._set_env_keys(provider_keys)
        
        # Create manager and load keys
        manager = APIKeyManager()
        manager.load_keys()
        
        # Validate keys for enabled providers
        validation_results = manager.validate_keys(enabled_providers)
        
        # Verify validation results
        for provider in enabled_providers:
            has_key = provider in available_providers
            
            # Check validation result
            self.assertEqual(
                validation_results[provider],
                has_key,
                f"Validation result should be {has_key} for provider: {provider}"
            )
            
            # Check provider enabled status
            if has_key:
                self.assertTrue(
                    manager.is_provider_enabled(provider),
                    f"Provider with key should be enabled: {provider}"
                )
            else:
                self.assertFalse(
                    manager.is_provider_enabled(provider),
                    f"Provider without key should be disabled: {provider}"
                )
    
    @settings(max_examples=5)
    @given(
        provider=provider_strategy_no_ollama(),
        num_keys=st.integers(min_value=1, max_value=10)
    )
    def test_property_25_multiple_key_support(self, provider: str, num_keys: int):
        """
        Feature: api-model-management
        Property 25: Multiple key support
        
        For any provider with N API keys configured, all N keys should be
        stored and retrievable.
        
        Note: Ollama is excluded as it only supports a single base URL.
        
        Validates: Requirements 6.4
        """
        # Generate N unique keys
        keys = [f"test-key-{provider}-{i}" for i in range(num_keys)]
        
        # Set environment variables
        self._set_env_keys({provider: keys})
        
        # Create manager and load keys
        manager = APIKeyManager()
        manager.load_keys()
        
        # Verify key count
        self.assertEqual(
            manager.get_key_count(provider),
            num_keys,
            f"Should have {num_keys} keys for provider: {provider}"
        )
        
        # Retrieve all keys and verify they match
        retrieved_keys = []
        for _ in range(num_keys):
            key = manager.get_key(provider)
            self.assertIsNotNone(key, f"Key should be available for provider: {provider}")
            retrieved_keys.append(key)
        
        # All expected keys should be retrieved (order may vary due to rotation)
        self.assertEqual(
            set(retrieved_keys),
            set(keys),
            f"All {num_keys} keys should be retrievable for provider: {provider}"
        )
    
    @settings(max_examples=5)
    @given(
        provider=provider_strategy_no_ollama(),
        num_keys=st.integers(min_value=2, max_value=10),
        num_requests=st.integers(min_value=2, max_value=50)
    )
    def test_property_26_round_robin_key_rotation(
        self,
        provider: str,
        num_keys: int,
        num_requests: int
    ):
        """
        Feature: api-model-management
        Property 26: Round-robin key rotation
        
        For any provider with multiple API keys, consecutive requests should
        use keys in round-robin order (key1, key2, key3, key1, ...).
        
        Note: Ollama is excluded as it only supports a single base URL.
        
        Validates: Requirements 6.5
        """
        # Assume we have at least 2 keys for meaningful rotation testing
        assume(num_keys >= 2)
        
        # Generate N unique keys
        keys = [f"test-key-{provider}-{i}" for i in range(num_keys)]
        
        # Set environment variables
        self._set_env_keys({provider: keys})
        
        # Create manager and load keys
        manager = APIKeyManager()
        manager.load_keys()
        
        # Make multiple requests and track key order
        retrieved_keys = []
        for _ in range(num_requests):
            key = manager.get_key(provider)
            self.assertIsNotNone(key, f"Key should be available for provider: {provider}")
            retrieved_keys.append(key)
        
        # Verify round-robin pattern
        # The pattern should repeat every num_keys requests
        for i in range(num_requests):
            expected_key = keys[i % num_keys]
            actual_key = retrieved_keys[i]
            self.assertEqual(
                actual_key,
                expected_key,
                f"Request {i} should use key {i % num_keys} in round-robin order"
            )
        
        # Verify that all keys are used if num_requests >= num_keys
        if num_requests >= num_keys:
            unique_keys_used = set(retrieved_keys[:num_keys])
            self.assertEqual(
                unique_keys_used,
                set(keys),
                "All keys should be used in the first rotation cycle"
            )


if __name__ == "__main__":
    unittest.main()
