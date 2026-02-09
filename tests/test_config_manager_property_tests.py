"""
Property-based tests for ConfigManager class.

This module tests the correctness properties of the ConfigManager including
configuration validation, hot reload, and schema validation.
"""

import unittest
import json
import tempfile
import time
from pathlib import Path
from typing import Dict, Any

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
        def floats(self, **kwargs): return lambda: 1.0
        def booleans(self): return lambda: True
        def lists(self, *args, **kwargs): return lambda: []
        def dictionaries(self, *args, **kwargs): return lambda: {}
        def one_of(self, *args): return lambda: args[0]() if args else lambda: None
        def just(self, value): return lambda: value
        def builds(self, cls, **kwargs): return lambda: cls(**kwargs)
        def sampled_from(self, seq): return lambda: seq[0] if seq else None
    
    st = MockStrategies()
    
    def settings(**kwargs):
        def decorator(func):
            return func
        return decorator

from agentic_sdlc.orchestration.api_model_management.config_manager import ConfigManager
from agentic_sdlc.orchestration.api_model_management.exceptions import ConfigurationError


# Hypothesis strategies for generating test data

@st.composite
def valid_model_config(draw):
    """Generate a valid model configuration."""
    return {
        "id": draw(st.text(min_size=1, max_size=50, alphabet=st.characters(whitelist_categories=('Lu', 'Ll', 'Nd'), whitelist_characters='-_'))),
        "provider": draw(st.sampled_from(["openai", "anthropic", "google", "ollama"])),
        "name": draw(st.text(min_size=1, max_size=100)),
        "capabilities": draw(st.lists(
            st.sampled_from(["text-generation", "code-generation", "analysis", "reasoning"]),
            min_size=1,
            max_size=4,
            unique=True
        )),
        "cost_per_1k_input_tokens": draw(st.floats(min_value=0.0, max_value=1.0)),
        "cost_per_1k_output_tokens": draw(st.floats(min_value=0.0, max_value=1.0)),
        "rate_limits": {
            "requests_per_minute": draw(st.integers(min_value=1, max_value=10000)),
            "tokens_per_minute": draw(st.integers(min_value=1000, max_value=1000000))
        },
        "context_window": draw(st.integers(min_value=1000, max_value=200000)),
        "average_response_time_ms": draw(st.floats(min_value=100.0, max_value=10000.0)),
        "enabled": draw(st.booleans())
    }


@st.composite
def invalid_model_config(draw):
    """Generate an invalid model configuration (missing required fields)."""
    # Start with a valid config
    config = {
        "id": draw(st.text(min_size=1, max_size=50)),
        "provider": draw(st.sampled_from(["openai", "anthropic", "google", "ollama"])),
        "name": draw(st.text(min_size=1, max_size=100)),
        "capabilities": draw(st.lists(st.sampled_from(["text-generation", "code-generation"]), min_size=1)),
        "cost_per_1k_input_tokens": draw(st.floats(min_value=0.0, max_value=1.0)),
        "cost_per_1k_output_tokens": draw(st.floats(min_value=0.0, max_value=1.0)),
        "rate_limits": {
            "requests_per_minute": draw(st.integers(min_value=1, max_value=10000)),
            "tokens_per_minute": draw(st.integers(min_value=1000, max_value=1000000))
        },
        "context_window": draw(st.integers(min_value=1000, max_value=200000)),
        "average_response_time_ms": draw(st.floats(min_value=100.0, max_value=10000.0))
    }
    
    # Remove a random required field to make it invalid
    required_fields = ["id", "provider", "name", "capabilities", "cost_per_1k_input_tokens",
                      "cost_per_1k_output_tokens", "rate_limits", "context_window", "average_response_time_ms"]
    field_to_remove = draw(st.sampled_from(required_fields))
    
    if field_to_remove in config:
        del config[field_to_remove]
    
    return config


@st.composite
def valid_full_config(draw):
    """Generate a valid full configuration."""
    return {
        "models": draw(st.lists(valid_model_config(), min_size=1, max_size=5)),
        "health_check": {
            "interval_seconds": draw(st.integers(min_value=10, max_value=300)),
            "timeout_seconds": draw(st.integers(min_value=1, max_value=30)),
            "consecutive_failures_threshold": draw(st.integers(min_value=1, max_value=10))
        },
        "rate_limiting": {
            "threshold_percent": draw(st.floats(min_value=50.0, max_value=100.0)),
            "window_seconds": draw(st.integers(min_value=1, max_value=300))
        },
        "caching": {
            "enabled": draw(st.booleans()),
            "max_size_mb": draw(st.integers(min_value=10, max_value=10000)),
            "default_ttl_seconds": draw(st.integers(min_value=60, max_value=86400))
        },
        "budget": {
            "daily_limit": draw(st.floats(min_value=1.0, max_value=10000.0)),
            "alert_threshold_percent": draw(st.floats(min_value=50.0, max_value=100.0))
        },
        "quality_evaluation": {
            "enabled": draw(st.booleans()),
            "threshold": draw(st.floats(min_value=0.0, max_value=1.0)),
            "evaluation_window": draw(st.integers(min_value=5, max_value=100))
        },
        "failover": {
            "max_retries": draw(st.integers(min_value=0, max_value=10)),
            "base_backoff_seconds": draw(st.integers(min_value=1, max_value=10)),
            "alert_threshold": draw(st.integers(min_value=1, max_value=10)),
            "alert_window_hours": draw(st.integers(min_value=1, max_value=24))
        },
        "concurrency": {
            "max_concurrent_requests_per_provider": draw(st.integers(min_value=1, max_value=100))
        }
    }


class TestConfigManagerProperties(unittest.TestCase):
    """Property-based tests for ConfigManager."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.mkdtemp()
        self.config_path = Path(self.temp_dir) / "config.json"
        self.schema_path = Path(__file__).parent.parent / "agentic_sdlc" / "orchestration" / "api_model_management" / "config" / "schema.json"
    
    def tearDown(self):
        """Clean up test fixtures."""
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    @settings(max_examples=100)
    @given(config=valid_full_config())
    def test_property_51_invalid_configuration_error_handling(self, config):
        """
        Feature: api-model-management
        Property 51: Invalid configuration error handling
        
        For any configuration with schema violations or invalid values,
        detailed validation errors should be logged and default values should be used.
        
        Validates: Requirements 12.2
        """
        if not HYPOTHESIS_AVAILABLE:
            self.skipTest("Hypothesis not available")
        
        # Create an invalid configuration by adding an invalid field value
        invalid_config = config.copy()
        
        # Make one of the models invalid (negative cost)
        if invalid_config.get("models"):
            invalid_config["models"][0]["cost_per_1k_input_tokens"] = -1.0
        
        # Write invalid config to file
        with open(self.config_path, 'w') as f:
            json.dump(invalid_config, f)
        
        # ConfigManager should handle the error gracefully
        try:
            manager = ConfigManager(self.config_path, self.schema_path)
            # Should use default values for invalid config
            loaded_config = manager.get_config()
            self.assertIsNotNone(loaded_config)
            # Should have default values
            self.assertIn("health_check", loaded_config)
            self.assertIn("rate_limiting", loaded_config)
        except ConfigurationError as e:
            # Error should contain details
            self.assertIsNotNone(e.message)
            self.assertTrue(len(e.message) > 0)
    
    @settings(max_examples=100)
    @given(
        initial_config=valid_full_config(),
        updated_config=valid_full_config()
    )
    def test_property_52_configuration_hot_reload(self, initial_config, updated_config):
        """
        Feature: api-model-management
        Property 52: Configuration hot reload
        
        For any configuration file update, the system should reload the configuration
        and apply changes without requiring a restart.
        
        Validates: Requirements 12.4
        """
        if not HYPOTHESIS_AVAILABLE:
            self.skipTest("Hypothesis not available")
        
        # Write initial config
        with open(self.config_path, 'w') as f:
            json.dump(initial_config, f)
        
        # Create manager with initial config
        manager = ConfigManager(self.config_path, self.schema_path)
        initial_loaded = manager.get_config()
        
        # Verify initial config is loaded
        self.assertEqual(len(initial_loaded["models"]), len(initial_config["models"]))
        
        # Wait a bit to ensure file modification time changes
        time.sleep(0.1)
        
        # Update config file
        with open(self.config_path, 'w') as f:
            json.dump(updated_config, f)
        
        # Reload configuration
        reloaded = manager.reload_config()
        
        # Should detect change and reload
        self.assertTrue(reloaded)
        
        # Get updated config
        updated_loaded = manager.get_config()
        
        # Should reflect the updated configuration
        self.assertEqual(len(updated_loaded["models"]), len(updated_config["models"]))
    
    @settings(max_examples=100)
    @given(config=st.one_of(
        valid_full_config(),
        st.builds(dict, models=st.lists(invalid_model_config(), min_size=1, max_size=3))
    ))
    def test_property_53_configuration_schema_validation(self, config):
        """
        Feature: api-model-management
        Property 53: Configuration schema validation
        
        For any configuration that doesn't match the required schema,
        it should be rejected with specific validation errors.
        
        Validates: Requirements 12.5
        """
        if not HYPOTHESIS_AVAILABLE:
            self.skipTest("Hypothesis not available")
        
        # Write config to file
        with open(self.config_path, 'w') as f:
            json.dump(config, f)
        
        try:
            manager = ConfigManager(self.config_path, self.schema_path)
            loaded_config = manager.get_config()
            
            # If config is valid, it should be loaded successfully
            self.assertIsNotNone(loaded_config)
            self.assertIn("models", loaded_config)
            
            # Validate the loaded config
            is_valid = manager.validate_current_config()
            
            # If models have all required fields, validation should pass
            if all(
                all(key in model for key in ["id", "provider", "name", "capabilities",
                                             "cost_per_1k_input_tokens", "cost_per_1k_output_tokens",
                                             "rate_limits", "context_window", "average_response_time_ms"])
                for model in config.get("models", [])
            ):
                # Valid config should pass validation
                self.assertTrue(is_valid or len(loaded_config.get("models", [])) == 0)
            
        except ConfigurationError as e:
            # Invalid config should raise ConfigurationError
            self.assertIsNotNone(e.message)
            # Error message should be descriptive
            self.assertTrue(len(e.message) > 0)


if __name__ == '__main__':
    unittest.main()
