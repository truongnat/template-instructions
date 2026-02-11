"""
Unit tests for APIKeyManager class.

This module tests the APIKeyManager functionality including startup validation,
missing key warnings, and environment variable loading.
"""

import unittest
import os
import tempfile
import logging
from pathlib import Path
from io import StringIO

from agentic_sdlc.orchestration.api_model_management.api_key_manager import APIKeyManager


class TestAPIKeyManager(unittest.TestCase):
    """Test APIKeyManager functionality"""
    
    def setUp(self):
        """Set up test fixtures"""
        # Store original environment
        self.original_env = os.environ.copy()
        
        # Create temporary directory for .env files
        self.temp_dir = tempfile.mkdtemp()
        self.env_file = Path(self.temp_dir) / ".env"
        
        # Set up logging capture
        self.log_capture = StringIO()
        self.log_handler = logging.StreamHandler(self.log_capture)
        self.log_handler.setLevel(logging.DEBUG)
        
        # Get logger and add handler
        self.logger = logging.getLogger("agentic_sdlc.orchestration.api_model_management.api_key_manager")
        self.original_level = self.logger.level
        self.logger.setLevel(logging.DEBUG)
        self.logger.addHandler(self.log_handler)
    
    def tearDown(self):
        """Clean up after test"""
        # Restore original environment
        os.environ.clear()
        os.environ.update(self.original_env)
        
        # Remove log handler
        self.logger.removeHandler(self.log_handler)
        self.logger.setLevel(self.original_level)
    
    def _clear_api_keys_from_env(self):
        """Helper to clear all API key environment variables"""
        for key in list(os.environ.keys()):
            if 'API_KEY' in key or 'OLLAMA_BASE_URL' in key:
                del os.environ[key]
    
    def _get_log_output(self) -> str:
        """Get captured log output"""
        return self.log_capture.getvalue()
    
    # Test startup validation (Requirement 6.2)
    
    def test_startup_validation_all_keys_present(self):
        """Test startup validation when all required keys are present"""
        # Set up environment with all keys
        os.environ["OPENAI_API_KEY"] = "sk-test-openai"
        os.environ["ANTHROPIC_API_KEY"] = "sk-test-anthropic"
        os.environ["GOOGLE_API_KEY"] = "test-google"
        
        manager = APIKeyManager()
        manager.load_keys()
        
        # Validate all providers
        validation_results = manager.validate_keys(["openai", "anthropic", "google"])
        
        # All should be valid
        self.assertTrue(validation_results["openai"])
        self.assertTrue(validation_results["anthropic"])
        self.assertTrue(validation_results["google"])
        
        # Check log for success messages
        log_output = self._get_log_output()
        self.assertIn("API key validation passed for provider: openai", log_output)
        self.assertIn("API key validation passed for provider: anthropic", log_output)
        self.assertIn("API key validation passed for provider: google", log_output)
    
    def test_startup_validation_some_keys_missing(self):
        """Test startup validation when some required keys are missing"""
        # Set up environment with only some keys
        os.environ["OPENAI_API_KEY"] = "sk-test-openai"
        # Missing ANTHROPIC_API_KEY and GOOGLE_API_KEY
        
        manager = APIKeyManager()
        manager.load_keys()
        
        # Validate all providers
        validation_results = manager.validate_keys(["openai", "anthropic", "google"])
        
        # Only OpenAI should be valid
        self.assertTrue(validation_results["openai"])
        self.assertFalse(validation_results["anthropic"])
        self.assertFalse(validation_results["google"])
        
        # Check providers are disabled
        self.assertTrue(manager.is_provider_enabled("openai"))
        self.assertFalse(manager.is_provider_enabled("anthropic"))
        self.assertFalse(manager.is_provider_enabled("google"))
    
    def test_startup_validation_no_keys_present(self):
        """Test startup validation when no keys are present"""
        self._clear_api_keys_from_env()
        
        manager = APIKeyManager()
        manager.load_keys()
        
        # Validate all providers
        validation_results = manager.validate_keys(["openai", "anthropic", "google"])
        
        # All should be invalid
        self.assertFalse(validation_results["openai"])
        self.assertFalse(validation_results["anthropic"])
        self.assertFalse(validation_results["google"])
        
        # All providers should be disabled
        self.assertFalse(manager.is_provider_enabled("openai"))
        self.assertFalse(manager.is_provider_enabled("anthropic"))
        self.assertFalse(manager.is_provider_enabled("google"))
    
    def test_startup_validation_ollama_special_case(self):
        """Test startup validation for Ollama which uses base URL instead of API key"""
        os.environ["OLLAMA_BASE_URL"] = "http://localhost:11434"
        
        manager = APIKeyManager()
        manager.load_keys()
        
        # Validate Ollama
        validation_results = manager.validate_keys(["ollama"])
        
        # Should be valid
        self.assertTrue(validation_results["ollama"])
        self.assertTrue(manager.is_provider_enabled("ollama"))
        
        # Should be able to get the base URL
        base_url = manager.get_key("ollama")
        self.assertEqual(base_url, "http://localhost:11434")
    
    # Test missing key warnings (Requirement 6.2)
    
    def test_missing_key_warning_logged(self):
        """Test that missing keys generate warning logs"""
        self._clear_api_keys_from_env()
        
        manager = APIKeyManager()
        manager.load_keys()
        
        # Validate providers with missing keys
        manager.validate_keys(["openai", "anthropic"])
        
        # Check log for warning messages
        log_output = self._get_log_output()
        self.assertIn("Missing API key for enabled provider: openai", log_output)
        self.assertIn("Missing API key for enabled provider: anthropic", log_output)
        self.assertIn("Provider will be disabled", log_output)
    
    def test_missing_key_provider_disabled(self):
        """Test that providers with missing keys are disabled"""
        self._clear_api_keys_from_env()
        
        # Set only OpenAI key
        os.environ["OPENAI_API_KEY"] = "sk-test-openai"
        
        manager = APIKeyManager()
        manager.load_keys()
        
        # Validate all providers
        manager.validate_keys(["openai", "anthropic", "google"])
        
        # Check that missing providers are in disabled list
        self.assertFalse(manager.is_provider_enabled("anthropic"))
        self.assertFalse(manager.is_provider_enabled("google"))
        
        # OpenAI should still be enabled
        self.assertTrue(manager.is_provider_enabled("openai"))
    
    def test_no_warning_for_present_keys(self):
        """Test that no warnings are logged for present keys"""
        os.environ["OPENAI_API_KEY"] = "sk-test-openai"
        
        manager = APIKeyManager()
        manager.load_keys()
        
        # Clear previous logs
        self.log_capture.truncate(0)
        self.log_capture.seek(0)
        
        # Validate only OpenAI
        manager.validate_keys(["openai"])
        
        # Check log - should have success message, not warning
        log_output = self._get_log_output()
        self.assertIn("API key validation passed for provider: openai", log_output)
        self.assertNotIn("Missing API key", log_output)
    
    # Test environment variable loading (Requirement 6.2)
    
    def test_load_keys_from_environment_single_key(self):
        """Test loading single API key from environment"""
        os.environ["OPENAI_API_KEY"] = "sk-test-openai-123"
        
        manager = APIKeyManager()
        manager.load_keys()
        
        # Should be able to retrieve the key
        key = manager.get_key("openai")
        self.assertEqual(key, "sk-test-openai-123")
        
        # Check log for load message
        log_output = self._get_log_output()
        self.assertIn("Loaded 1 API key(s) for provider: openai", log_output)
    
    def test_load_keys_from_environment_multiple_keys(self):
        """Test loading multiple API keys from environment"""
        os.environ["OPENAI_API_KEY"] = "sk-test-openai-1"
        os.environ["OPENAI_API_KEY_2"] = "sk-test-openai-2"
        os.environ["OPENAI_API_KEY_3"] = "sk-test-openai-3"
        
        manager = APIKeyManager()
        manager.load_keys()
        
        # Should load all 3 keys
        self.assertEqual(manager.get_key_count("openai"), 3)
        
        # Check log for load message
        log_output = self._get_log_output()
        self.assertIn("Loaded 3 API key(s) for provider: openai", log_output)
    
    def test_load_keys_from_environment_all_providers(self):
        """Test loading keys for all supported providers"""
        os.environ["OPENAI_API_KEY"] = "sk-test-openai"
        os.environ["ANTHROPIC_API_KEY"] = "sk-test-anthropic"
        os.environ["GOOGLE_API_KEY"] = "test-google"
        os.environ["OLLAMA_BASE_URL"] = "http://localhost:11434"
        
        manager = APIKeyManager()
        manager.load_keys()
        
        # All providers should have keys
        self.assertIsNotNone(manager.get_key("openai"))
        self.assertIsNotNone(manager.get_key("anthropic"))
        self.assertIsNotNone(manager.get_key("google"))
        self.assertIsNotNone(manager.get_key("ollama"))
        
        # Check available providers
        available = manager.get_available_providers()
        self.assertIn("openai", available)
        self.assertIn("anthropic", available)
        self.assertIn("google", available)
        self.assertIn("ollama", available)
    
    def test_load_keys_from_env_file(self):
        """Test loading keys from .env file"""
        # Create .env file
        with open(self.env_file, 'w') as f:
            f.write("OPENAI_API_KEY=sk-test-from-file\n")
            f.write("ANTHROPIC_API_KEY=sk-anthropic-from-file\n")
        
        # Clear environment
        self._clear_api_keys_from_env()
        
        # Create manager with env file
        manager = APIKeyManager(env_file=self.env_file)
        manager.load_keys()
        
        # Keys should be loaded from file
        self.assertEqual(manager.get_key("openai"), "sk-test-from-file")
        self.assertEqual(manager.get_key("anthropic"), "sk-anthropic-from-file")
    
    def test_load_keys_no_keys_in_environment(self):
        """Test loading keys when none are present in environment"""
        self._clear_api_keys_from_env()
        
        manager = APIKeyManager()
        manager.load_keys()
        
        # No keys should be loaded
        self.assertIsNone(manager.get_key("openai"))
        self.assertIsNone(manager.get_key("anthropic"))
        self.assertIsNone(manager.get_key("google"))
        
        # Check log for debug messages
        log_output = self._get_log_output()
        self.assertIn("No API keys found for provider: openai", log_output)
        self.assertIn("No API keys found for provider: anthropic", log_output)
        self.assertIn("No API keys found for provider: google", log_output)
    
    def test_load_keys_with_gaps_in_numbering(self):
        """Test loading keys when there are gaps in numbering (KEY_2 missing, KEY_3 present)"""
        os.environ["OPENAI_API_KEY"] = "sk-test-openai-1"
        # Skip KEY_2
        os.environ["OPENAI_API_KEY_3"] = "sk-test-openai-3"
        
        manager = APIKeyManager()
        manager.load_keys()
        
        # Should only load KEY and stop at the gap
        self.assertEqual(manager.get_key_count("openai"), 1)
        
        # Only the first key should be loaded
        key = manager.get_key("openai")
        self.assertEqual(key, "sk-test-openai-1")
    
    def test_load_keys_case_sensitivity(self):
        """Test that environment variable names are case-sensitive"""
        # Set lowercase (incorrect)
        os.environ["openai_api_key"] = "sk-test-lowercase"
        
        manager = APIKeyManager()
        manager.load_keys()
        
        # Should not load the key (wrong case)
        self.assertIsNone(manager.get_key("openai"))
        
        # Now set correct case
        os.environ["OPENAI_API_KEY"] = "sk-test-correct"
        
        manager2 = APIKeyManager()
        manager2.load_keys()
        
        # Should load the key
        self.assertEqual(manager2.get_key("openai"), "sk-test-correct")
    
    def test_load_keys_empty_string_values(self):
        """Test loading keys when environment variables are empty strings"""
        os.environ["OPENAI_API_KEY"] = ""
        os.environ["ANTHROPIC_API_KEY"] = "   "  # Whitespace only
        
        manager = APIKeyManager()
        manager.load_keys()
        
        # Empty strings are treated as falsy and not loaded
        # This is the expected behavior - empty keys are not valid
        key1 = manager.get_key("openai")
        key2 = manager.get_key("anthropic")
        
        # Empty strings should not be loaded (treated as missing keys)
        self.assertIsNone(key1)
        # Whitespace-only strings are still loaded (they're truthy)
        self.assertEqual(key2, "   ")
    
    def test_environment_override_priority(self):
        """Test that environment variables override .env file"""
        # Create .env file
        with open(self.env_file, 'w') as f:
            f.write("OPENAI_API_KEY=sk-from-file\n")
        
        # Set environment variable (should take precedence)
        os.environ["OPENAI_API_KEY"] = "sk-from-env"
        
        manager = APIKeyManager(env_file=self.env_file)
        manager.load_keys()
        
        # Environment variable should take precedence
        key = manager.get_key("openai")
        self.assertEqual(key, "sk-from-env")
    
    def test_load_keys_nonexistent_env_file(self):
        """Test loading keys when .env file doesn't exist"""
        nonexistent_file = Path(self.temp_dir) / "nonexistent.env"
        
        # Should not raise error
        manager = APIKeyManager(env_file=nonexistent_file)
        manager.load_keys()
        
        # Should still work with environment variables
        os.environ["OPENAI_API_KEY"] = "sk-test"
        manager2 = APIKeyManager(env_file=nonexistent_file)
        manager2.load_keys()
        
        self.assertEqual(manager2.get_key("openai"), "sk-test")
    
    def test_get_key_returns_none_for_missing_provider(self):
        """Test that get_key returns None for providers without keys"""
        self._clear_api_keys_from_env()
        
        manager = APIKeyManager()
        manager.load_keys()
        
        # Should return None and log warning
        key = manager.get_key("openai")
        self.assertIsNone(key)
        
        # Check log for warning
        log_output = self._get_log_output()
        self.assertIn("No API key available for provider: openai", log_output)
    
    def test_get_key_case_insensitive_provider_name(self):
        """Test that get_key handles provider names case-insensitively"""
        os.environ["OPENAI_API_KEY"] = "sk-test-openai"
        
        manager = APIKeyManager()
        manager.load_keys()
        
        # Should work with different cases
        key1 = manager.get_key("openai")
        key2 = manager.get_key("OPENAI")
        key3 = manager.get_key("OpenAI")
        
        self.assertEqual(key1, "sk-test-openai")
        self.assertEqual(key2, "sk-test-openai")
        self.assertEqual(key3, "sk-test-openai")
    
    def test_add_key_enables_disabled_provider(self):
        """Test that adding a key re-enables a previously disabled provider"""
        self._clear_api_keys_from_env()
        
        manager = APIKeyManager()
        manager.load_keys()
        
        # Validate and disable OpenAI
        manager.validate_keys(["openai"])
        self.assertFalse(manager.is_provider_enabled("openai"))
        
        # Add key programmatically
        manager.add_key("openai", "sk-test-added")
        
        # Provider should now be enabled
        self.assertTrue(manager.is_provider_enabled("openai"))
        self.assertEqual(manager.get_key("openai"), "sk-test-added")
    
    def test_get_available_providers_excludes_disabled(self):
        """Test that get_available_providers excludes disabled providers"""
        os.environ["OPENAI_API_KEY"] = "sk-test-openai"
        os.environ["ANTHROPIC_API_KEY"] = "sk-test-anthropic"
        
        manager = APIKeyManager()
        manager.load_keys()
        
        # Initially both should be available
        available = manager.get_available_providers()
        self.assertIn("openai", available)
        self.assertIn("anthropic", available)
        
        # Validate and disable Anthropic
        manager.validate_keys(["anthropic"])
        # Actually, validation passes, so let's manually test the disabled scenario
        # by validating a provider that doesn't have a key
        manager.validate_keys(["google"])
        
        # Google should not be in available providers
        available = manager.get_available_providers()
        self.assertNotIn("google", available)


if __name__ == "__main__":
    unittest.main()
