"""
Unit tests for ConfigManager class.

This module tests specific scenarios and edge cases for configuration management
including file loading, environment-specific configs, and schema validation.
"""

import unittest
import json
import tempfile
import time
from pathlib import Path

from agentic_sdlc.orchestration.api_model_management.config_manager import ConfigManager
from agentic_sdlc.orchestration.api_model_management.exceptions import ConfigurationError


class TestConfigManager(unittest.TestCase):
    """Unit tests for ConfigManager."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.mkdtemp()
        self.config_path = Path(self.temp_dir) / "config.json"
        self.schema_path = Path(__file__).parent.parent / "agentic_sdlc" / "orchestration" / "api_model_management" / "config" / "schema.json"
        
        # Sample valid configuration
        self.valid_config = {
            "models": [
                {
                    "id": "test-model",
                    "provider": "openai",
                    "name": "Test Model",
                    "capabilities": ["text-generation"],
                    "cost_per_1k_input_tokens": 0.01,
                    "cost_per_1k_output_tokens": 0.03,
                    "rate_limits": {
                        "requests_per_minute": 100,
                        "tokens_per_minute": 10000
                    },
                    "context_window": 4096,
                    "average_response_time_ms": 1000.0,
                    "enabled": True
                }
            ]
        }
    
    def tearDown(self):
        """Clean up test fixtures."""
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_load_valid_configuration(self):
        """Test loading a valid configuration file."""
        # Write valid config
        with open(self.config_path, 'w') as f:
            json.dump(self.valid_config, f)
        
        # Load configuration
        manager = ConfigManager(self.config_path, self.schema_path)
        config = manager.get_config()
        
        # Verify config is loaded
        self.assertIsNotNone(config)
        self.assertIn("models", config)
        self.assertEqual(len(config["models"]), 1)
        self.assertEqual(config["models"][0]["id"], "test-model")
    
    def test_missing_configuration_file(self):
        """Test handling of missing configuration file."""
        non_existent_path = Path(self.temp_dir) / "nonexistent.json"
        
        # Should raise ConfigurationError
        with self.assertRaises(ConfigurationError) as context:
            ConfigManager(non_existent_path, self.schema_path)
        
        self.assertIn("not found", str(context.exception))
    
    def test_invalid_json_format(self):
        """Test handling of invalid JSON format."""
        # Write invalid JSON
        with open(self.config_path, 'w') as f:
            f.write("{ invalid json }")
        
        # Should raise ConfigurationError
        with self.assertRaises(ConfigurationError) as context:
            ConfigManager(self.config_path, self.schema_path)
        
        self.assertIn("Invalid JSON", str(context.exception))
    
    def test_schema_validation_failure(self):
        """Test schema validation with invalid configuration."""
        # Create config with missing required field
        invalid_config = {
            "models": [
                {
                    "id": "test-model",
                    "provider": "openai",
                    # Missing required fields
                }
            ]
        }
        
        with open(self.config_path, 'w') as f:
            json.dump(invalid_config, f)
        
        # Should handle validation error gracefully
        manager = ConfigManager(self.config_path, self.schema_path)
        config = manager.get_config()
        
        # Should use default values
        self.assertIn("health_check", config)
        self.assertIn("rate_limiting", config)
    
    def test_merge_with_defaults(self):
        """Test merging user config with default values."""
        # Config with only models (no other settings)
        minimal_config = {
            "models": [
                {
                    "id": "test-model",
                    "provider": "openai",
                    "name": "Test Model",
                    "capabilities": ["text-generation"],
                    "cost_per_1k_input_tokens": 0.01,
                    "cost_per_1k_output_tokens": 0.03,
                    "rate_limits": {
                        "requests_per_minute": 100,
                        "tokens_per_minute": 10000
                    },
                    "context_window": 4096,
                    "average_response_time_ms": 1000.0
                }
            ]
        }
        
        with open(self.config_path, 'w') as f:
            json.dump(minimal_config, f)
        
        manager = ConfigManager(self.config_path, self.schema_path)
        config = manager.get_config()
        
        # Should have default values for missing sections
        self.assertIn("health_check", config)
        self.assertIn("rate_limiting", config)
        self.assertIn("caching", config)
        self.assertIn("budget", config)
        
        # Default values should be present
        self.assertEqual(config["health_check"]["interval_seconds"], 60)
        self.assertEqual(config["rate_limiting"]["threshold_percent"], 90)
    
    def test_get_configuration_sections(self):
        """Test getting specific configuration sections."""
        with open(self.config_path, 'w') as f:
            json.dump(self.valid_config, f)
        
        manager = ConfigManager(self.config_path, self.schema_path)
        
        # Test getting specific sections
        health_check = manager.get_health_check_config()
        self.assertIsNotNone(health_check)
        self.assertIn("interval_seconds", health_check)
        
        rate_limiting = manager.get_rate_limiting_config()
        self.assertIsNotNone(rate_limiting)
        self.assertIn("threshold_percent", rate_limiting)
        
        caching = manager.get_caching_config()
        self.assertIsNotNone(caching)
        self.assertIn("enabled", caching)
        
        budget = manager.get_budget_config()
        self.assertIsNotNone(budget)
        self.assertIn("daily_limit", budget)
        
        quality = manager.get_quality_evaluation_config()
        self.assertIsNotNone(quality)
        self.assertIn("enabled", quality)
        
        failover = manager.get_failover_config()
        self.assertIsNotNone(failover)
        self.assertIn("max_retries", failover)
        
        concurrency = manager.get_concurrency_config()
        self.assertIsNotNone(concurrency)
        self.assertIn("max_concurrent_requests_per_provider", concurrency)
    
    def test_get_with_dot_notation(self):
        """Test getting configuration values with dot notation."""
        with open(self.config_path, 'w') as f:
            json.dump(self.valid_config, f)
        
        manager = ConfigManager(self.config_path, self.schema_path)
        
        # Test dot notation access
        interval = manager.get("health_check.interval_seconds")
        self.assertEqual(interval, 60)
        
        threshold = manager.get("rate_limiting.threshold_percent")
        self.assertEqual(threshold, 90)
        
        # Test with default value
        nonexistent = manager.get("nonexistent.key", default="default_value")
        self.assertEqual(nonexistent, "default_value")
    
    def test_hot_reload_on_file_change(self):
        """Test hot reload when configuration file is modified."""
        # Write initial config
        with open(self.config_path, 'w') as f:
            json.dump(self.valid_config, f)
        
        manager = ConfigManager(self.config_path, self.schema_path)
        initial_models = manager.get_models()
        self.assertEqual(len(initial_models), 1)
        
        # Wait to ensure file modification time changes
        time.sleep(0.1)
        
        # Modify config
        updated_config = self.valid_config.copy()
        updated_config["models"].append({
            "id": "test-model-2",
            "provider": "anthropic",
            "name": "Test Model 2",
            "capabilities": ["text-generation"],
            "cost_per_1k_input_tokens": 0.005,
            "cost_per_1k_output_tokens": 0.015,
            "rate_limits": {
                "requests_per_minute": 200,
                "tokens_per_minute": 20000
            },
            "context_window": 8192,
            "average_response_time_ms": 1500.0
        })
        
        with open(self.config_path, 'w') as f:
            json.dump(updated_config, f)
        
        # Reload config
        reloaded = manager.reload_config()
        self.assertTrue(reloaded)
        
        # Verify updated config
        updated_models = manager.get_models()
        self.assertEqual(len(updated_models), 2)
    
    def test_reload_no_change(self):
        """Test reload when file hasn't changed."""
        with open(self.config_path, 'w') as f:
            json.dump(self.valid_config, f)
        
        manager = ConfigManager(self.config_path, self.schema_path)
        
        # Reload without changes
        reloaded = manager.reload_config()
        self.assertFalse(reloaded)
    
    def test_environment_specific_config(self):
        """Test loading environment-specific configuration."""
        # Write main config
        with open(self.config_path, 'w') as f:
            json.dump(self.valid_config, f)
        
        # Write development config
        dev_config_path = Path(self.temp_dir) / "config.development.json"
        dev_config = {
            "budget": {
                "daily_limit": 10.0
            }
        }
        with open(dev_config_path, 'w') as f:
            json.dump(dev_config, f)
        
        manager = ConfigManager(self.config_path, self.schema_path, environment="development")
        
        # Get environment-specific config
        env_config = manager.get_environment_config()
        self.assertIsNotNone(env_config)
        self.assertIn("budget", env_config)
        self.assertEqual(env_config["budget"]["daily_limit"], 10.0)
    
    def test_validate_current_config(self):
        """Test validation of current configuration."""
        with open(self.config_path, 'w') as f:
            json.dump(self.valid_config, f)
        
        manager = ConfigManager(self.config_path, self.schema_path)
        
        # Valid config should pass validation
        is_valid = manager.validate_current_config()
        self.assertTrue(is_valid)
    
    def test_get_last_modified(self):
        """Test getting last modification time."""
        with open(self.config_path, 'w') as f:
            json.dump(self.valid_config, f)
        
        manager = ConfigManager(self.config_path, self.schema_path)
        
        last_modified = manager.get_last_modified()
        self.assertIsNotNone(last_modified)
    
    def test_missing_schema_file(self):
        """Test handling when schema file is missing."""
        with open(self.config_path, 'w') as f:
            json.dump(self.valid_config, f)
        
        # Use non-existent schema path
        non_existent_schema = Path(self.temp_dir) / "nonexistent_schema.json"
        
        # Should still work but skip validation
        manager = ConfigManager(self.config_path, non_existent_schema)
        config = manager.get_config()
        
        self.assertIsNotNone(config)
        self.assertIn("models", config)


if __name__ == '__main__':
    unittest.main()
