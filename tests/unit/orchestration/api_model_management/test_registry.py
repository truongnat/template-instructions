"""
Unit tests for ModelRegistry class.

This module tests the ModelRegistry functionality including configuration loading,
validation, and query methods.
"""

import unittest
import json
import tempfile
from pathlib import Path

from agentic_sdlc.orchestration.api_model_management.registry import ModelRegistry
from agentic_sdlc.orchestration.api_model_management.models import ModelMetadata, RateLimits
from agentic_sdlc.orchestration.api_model_management.exceptions import ConfigurationError


class TestModelRegistry(unittest.TestCase):
    """Test ModelRegistry functionality"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.temp_dir = tempfile.mkdtemp()
        self.config_path = Path(self.temp_dir) / "test_config.json"
        
        # Sample valid configuration
        self.valid_config = {
            "models": [
                {
                    "id": "gpt-4-turbo",
                    "provider": "openai",
                    "name": "GPT-4 Turbo",
                    "capabilities": ["text-generation", "code-generation"],
                    "cost_per_1k_input_tokens": 0.01,
                    "cost_per_1k_output_tokens": 0.03,
                    "rate_limits": {
                        "requests_per_minute": 500,
                        "tokens_per_minute": 150000
                    },
                    "context_window": 128000,
                    "average_response_time_ms": 2000.0,
                    "enabled": True
                },
                {
                    "id": "claude-3.5-sonnet",
                    "provider": "anthropic",
                    "name": "Claude 3.5 Sonnet",
                    "capabilities": ["text-generation", "analysis"],
                    "cost_per_1k_input_tokens": 0.003,
                    "cost_per_1k_output_tokens": 0.015,
                    "rate_limits": {
                        "requests_per_minute": 1000,
                        "tokens_per_minute": 200000
                    },
                    "context_window": 200000,
                    "average_response_time_ms": 1500.0,
                    "enabled": True
                },
                {
                    "id": "gemini-pro",
                    "provider": "google",
                    "name": "Gemini Pro",
                    "capabilities": ["text-generation"],
                    "cost_per_1k_input_tokens": 0.00025,
                    "cost_per_1k_output_tokens": 0.0005,
                    "rate_limits": {
                        "requests_per_minute": 60,
                        "tokens_per_minute": 32000
                    },
                    "context_window": 32768,
                    "average_response_time_ms": 1800.0,
                    "enabled": False
                }
            ]
        }
    
    def _write_config(self, config_data):
        """Helper to write configuration to file"""
        with open(self.config_path, 'w') as f:
            json.dump(config_data, f)
    
    def test_load_valid_configuration(self):
        """Test loading a valid configuration file"""
        self._write_config(self.valid_config)
        
        registry = ModelRegistry(self.config_path)
        registry.load_config()
        
        # Verify models were loaded
        model = registry.get_model("gpt-4-turbo")
        self.assertIsNotNone(model)
        self.assertEqual(model.id, "gpt-4-turbo")
        self.assertEqual(model.provider, "openai")
        self.assertEqual(model.name, "GPT-4 Turbo")
        self.assertEqual(model.capabilities, ["text-generation", "code-generation"])
        self.assertEqual(model.cost_per_1k_input_tokens, 0.01)
        self.assertEqual(model.cost_per_1k_output_tokens, 0.03)
        self.assertEqual(model.rate_limits.requests_per_minute, 500)
        self.assertEqual(model.rate_limits.tokens_per_minute, 150000)
        self.assertEqual(model.context_window, 128000)
        self.assertEqual(model.average_response_time_ms, 2000.0)
        self.assertTrue(model.enabled)
    
    def test_load_config_file_not_found(self):
        """Test loading configuration when file doesn't exist"""
        registry = ModelRegistry(Path("/nonexistent/path/config.json"))
        
        with self.assertRaises(ConfigurationError) as context:
            registry.load_config()
        
        self.assertIn("not found", str(context.exception))
    
    def test_load_invalid_json(self):
        """Test loading configuration with invalid JSON"""
        with open(self.config_path, 'w') as f:
            f.write("{ invalid json }")
        
        registry = ModelRegistry(self.config_path)
        
        with self.assertRaises(ConfigurationError):
            registry.load_config()
    
    def test_load_config_missing_required_field(self):
        """Test loading configuration with missing required fields"""
        invalid_config = {
            "models": [
                {
                    "id": "test-model",
                    "provider": "openai",
                    # Missing required fields
                }
            ]
        }
        self._write_config(invalid_config)
        
        registry = ModelRegistry(self.config_path)
        
        with self.assertRaises(ConfigurationError):
            registry.load_config()
    
    def test_load_config_invalid_field_type(self):
        """Test loading configuration with invalid field types"""
        invalid_config = {
            "models": [
                {
                    "id": "test-model",
                    "provider": "openai",
                    "name": "Test Model",
                    "capabilities": ["text-generation"],
                    "cost_per_1k_input_tokens": "invalid",  # Should be number
                    "cost_per_1k_output_tokens": 0.03,
                    "rate_limits": {
                        "requests_per_minute": 500,
                        "tokens_per_minute": 150000
                    },
                    "context_window": 128000,
                    "average_response_time_ms": 2000.0
                }
            ]
        }
        self._write_config(invalid_config)
        
        registry = ModelRegistry(self.config_path)
        
        with self.assertRaises(ConfigurationError):
            registry.load_config()
    
    def test_get_model_by_id(self):
        """Test retrieving a model by ID"""
        self._write_config(self.valid_config)
        
        registry = ModelRegistry(self.config_path)
        registry.load_config()
        
        model = registry.get_model("claude-3.5-sonnet")
        self.assertIsNotNone(model)
        self.assertEqual(model.id, "claude-3.5-sonnet")
        self.assertEqual(model.provider, "anthropic")
    
    def test_get_model_not_found(self):
        """Test retrieving a non-existent model"""
        self._write_config(self.valid_config)
        
        registry = ModelRegistry(self.config_path)
        registry.load_config()
        
        model = registry.get_model("nonexistent-model")
        self.assertIsNone(model)
    
    def test_get_models_by_provider(self):
        """Test retrieving models by provider"""
        self._write_config(self.valid_config)
        
        registry = ModelRegistry(self.config_path)
        registry.load_config()
        
        openai_models = registry.get_models_by_provider("openai")
        self.assertEqual(len(openai_models), 1)
        self.assertEqual(openai_models[0].id, "gpt-4-turbo")
        
        anthropic_models = registry.get_models_by_provider("anthropic")
        self.assertEqual(len(anthropic_models), 1)
        self.assertEqual(anthropic_models[0].id, "claude-3.5-sonnet")
        
        nonexistent_models = registry.get_models_by_provider("nonexistent")
        self.assertEqual(len(nonexistent_models), 0)
    
    def test_get_models_by_capability(self):
        """Test retrieving models by capability"""
        self._write_config(self.valid_config)
        
        registry = ModelRegistry(self.config_path)
        registry.load_config()
        
        text_gen_models = registry.get_models_by_capability("text-generation")
        self.assertEqual(len(text_gen_models), 3)
        
        code_gen_models = registry.get_models_by_capability("code-generation")
        self.assertEqual(len(code_gen_models), 1)
        self.assertEqual(code_gen_models[0].id, "gpt-4-turbo")
        
        analysis_models = registry.get_models_by_capability("analysis")
        self.assertEqual(len(analysis_models), 1)
        self.assertEqual(analysis_models[0].id, "claude-3.5-sonnet")
        
        nonexistent_models = registry.get_models_by_capability("nonexistent")
        self.assertEqual(len(nonexistent_models), 0)
    
    def test_get_models_by_cost_range(self):
        """Test retrieving models by cost range"""
        self._write_config(self.valid_config)
        
        registry = ModelRegistry(self.config_path)
        registry.load_config()
        
        # Low cost models (average < 0.001)
        low_cost_models = registry.get_models_by_cost_range(0.0, 0.001)
        self.assertEqual(len(low_cost_models), 1)
        self.assertEqual(low_cost_models[0].id, "gemini-pro")
        
        # Medium cost models (average 0.001 - 0.01)
        medium_cost_models = registry.get_models_by_cost_range(0.001, 0.01)
        self.assertEqual(len(medium_cost_models), 1)
        self.assertEqual(medium_cost_models[0].id, "claude-3.5-sonnet")
        
        # High cost models (average > 0.01)
        high_cost_models = registry.get_models_by_cost_range(0.01, 1.0)
        self.assertEqual(len(high_cost_models), 1)
        self.assertEqual(high_cost_models[0].id, "gpt-4-turbo")
        
        # All models
        all_models = registry.get_models_by_cost_range(0.0, 1.0)
        self.assertEqual(len(all_models), 3)
    
    def test_update_model(self):
        """Test updating model metadata"""
        self._write_config(self.valid_config)
        
        registry = ModelRegistry(self.config_path)
        registry.load_config()
        
        # Get original model
        original_model = registry.get_model("gpt-4-turbo")
        self.assertEqual(original_model.cost_per_1k_input_tokens, 0.01)
        
        # Update model
        updated_metadata = ModelMetadata(
            id="gpt-4-turbo",
            provider="openai",
            name="GPT-4 Turbo Updated",
            capabilities=["text-generation", "code-generation", "analysis"],
            cost_per_1k_input_tokens=0.02,  # Updated cost
            cost_per_1k_output_tokens=0.04,
            rate_limits=RateLimits(requests_per_minute=600, tokens_per_minute=160000),
            context_window=128000,
            average_response_time_ms=1800.0,
            enabled=True
        )
        
        result = registry.update_model("gpt-4-turbo", updated_metadata)
        self.assertTrue(result)
        
        # Verify update
        updated_model = registry.get_model("gpt-4-turbo")
        self.assertEqual(updated_model.name, "GPT-4 Turbo Updated")
        self.assertEqual(updated_model.cost_per_1k_input_tokens, 0.02)
        self.assertEqual(updated_model.cost_per_1k_output_tokens, 0.04)
        self.assertEqual(updated_model.rate_limits.requests_per_minute, 600)
    
    def test_update_nonexistent_model(self):
        """Test updating a non-existent model"""
        self._write_config(self.valid_config)
        
        registry = ModelRegistry(self.config_path)
        registry.load_config()
        
        new_metadata = ModelMetadata(
            id="nonexistent-model",
            provider="openai",
            name="Nonexistent",
            capabilities=["text-generation"],
            cost_per_1k_input_tokens=0.01,
            cost_per_1k_output_tokens=0.03,
            rate_limits=RateLimits(requests_per_minute=500, tokens_per_minute=150000),
            context_window=128000,
            average_response_time_ms=2000.0,
            enabled=True
        )
        
        result = registry.update_model("nonexistent-model", new_metadata)
        self.assertFalse(result)
    
    def test_add_model(self):
        """Test adding a new model"""
        self._write_config(self.valid_config)
        
        registry = ModelRegistry(self.config_path)
        registry.load_config()
        
        # Verify model doesn't exist
        self.assertIsNone(registry.get_model("new-model"))
        
        # Add new model
        new_metadata = ModelMetadata(
            id="new-model",
            provider="openai",
            name="New Model",
            capabilities=["text-generation"],
            cost_per_1k_input_tokens=0.005,
            cost_per_1k_output_tokens=0.015,
            rate_limits=RateLimits(requests_per_minute=1000, tokens_per_minute=100000),
            context_window=64000,
            average_response_time_ms=1500.0,
            enabled=True
        )
        
        result = registry.add_model(new_metadata)
        self.assertTrue(result)
        
        # Verify model was added
        added_model = registry.get_model("new-model")
        self.assertIsNotNone(added_model)
        self.assertEqual(added_model.id, "new-model")
        self.assertEqual(added_model.name, "New Model")
    
    def test_add_duplicate_model(self):
        """Test adding a model that already exists"""
        self._write_config(self.valid_config)
        
        registry = ModelRegistry(self.config_path)
        registry.load_config()
        
        # Try to add existing model
        duplicate_metadata = ModelMetadata(
            id="gpt-4-turbo",  # Already exists
            provider="openai",
            name="Duplicate",
            capabilities=["text-generation"],
            cost_per_1k_input_tokens=0.01,
            cost_per_1k_output_tokens=0.03,
            rate_limits=RateLimits(requests_per_minute=500, tokens_per_minute=150000),
            context_window=128000,
            average_response_time_ms=2000.0,
            enabled=True
        )
        
        result = registry.add_model(duplicate_metadata)
        self.assertFalse(result)
        
        # Verify original model wasn't changed
        original_model = registry.get_model("gpt-4-turbo")
        self.assertEqual(original_model.name, "GPT-4 Turbo")
    
    def test_load_config_with_partial_invalid_models(self):
        """Test loading configuration with some invalid models"""
        config_with_invalid = {
            "models": [
                {
                    "id": "valid-model",
                    "provider": "openai",
                    "name": "Valid Model",
                    "capabilities": ["text-generation"],
                    "cost_per_1k_input_tokens": 0.01,
                    "cost_per_1k_output_tokens": 0.03,
                    "rate_limits": {
                        "requests_per_minute": 500,
                        "tokens_per_minute": 150000
                    },
                    "context_window": 128000,
                    "average_response_time_ms": 2000.0,
                    "enabled": True
                },
                {
                    "id": "invalid-model",
                    "provider": "openai",
                    "name": "Invalid Model",
                    "capabilities": [],  # Empty capabilities - invalid
                    "cost_per_1k_input_tokens": 0.01,
                    "cost_per_1k_output_tokens": 0.03,
                    "rate_limits": {
                        "requests_per_minute": 500,
                        "tokens_per_minute": 150000
                    },
                    "context_window": 128000,
                    "average_response_time_ms": 2000.0,
                    "enabled": True
                }
            ]
        }
        self._write_config(config_with_invalid)
        
        registry = ModelRegistry(self.config_path)
        
        # Should raise error due to schema validation
        with self.assertRaises(ConfigurationError):
            registry.load_config()
    
    def test_get_models_by_cost_range_edge_cases(self):
        """Test cost range query with edge cases"""
        self._write_config(self.valid_config)
        
        registry = ModelRegistry(self.config_path)
        registry.load_config()
        
        # Test with zero range
        zero_range_models = registry.get_models_by_cost_range(0.0, 0.0)
        self.assertEqual(len(zero_range_models), 0)
        
        # Test with inverted range (min > max)
        inverted_models = registry.get_models_by_cost_range(1.0, 0.0)
        self.assertEqual(len(inverted_models), 0)
        
        # Test with exact match on boundary
        gemini_avg_cost = (0.00025 + 0.0005) / 2  # 0.000375
        exact_models = registry.get_models_by_cost_range(gemini_avg_cost, gemini_avg_cost)
        self.assertEqual(len(exact_models), 1)
        self.assertEqual(exact_models[0].id, "gemini-pro")
    
    def test_get_models_by_provider_case_sensitivity(self):
        """Test provider query is case-sensitive"""
        self._write_config(self.valid_config)
        
        registry = ModelRegistry(self.config_path)
        registry.load_config()
        
        # Correct case
        openai_models = registry.get_models_by_provider("openai")
        self.assertEqual(len(openai_models), 1)
        
        # Wrong case
        wrong_case_models = registry.get_models_by_provider("OpenAI")
        self.assertEqual(len(wrong_case_models), 0)
    
    def test_get_models_by_capability_case_sensitivity(self):
        """Test capability query is case-sensitive"""
        self._write_config(self.valid_config)
        
        registry = ModelRegistry(self.config_path)
        registry.load_config()
        
        # Correct case
        text_gen_models = registry.get_models_by_capability("text-generation")
        self.assertEqual(len(text_gen_models), 3)
        
        # Wrong case
        wrong_case_models = registry.get_models_by_capability("Text-Generation")
        self.assertEqual(len(wrong_case_models), 0)
    
    def test_load_empty_models_list(self):
        """Test loading configuration with empty models list"""
        empty_config = {"models": []}
        self._write_config(empty_config)
        
        registry = ModelRegistry(self.config_path)
        registry.load_config()
        
        # Should load successfully but have no models
        self.assertIsNone(registry.get_model("any-model"))
        self.assertEqual(len(registry.get_models_by_provider("openai")), 0)
    
    def test_load_config_missing_models_key(self):
        """Test loading configuration without 'models' key"""
        invalid_config = {"other_key": "value"}
        self._write_config(invalid_config)
        
        registry = ModelRegistry(self.config_path)
        
        with self.assertRaises(ConfigurationError):
            registry.load_config()
    
    def test_load_config_with_negative_costs(self):
        """Test loading configuration with negative cost values"""
        invalid_config = {
            "models": [
                {
                    "id": "test-model",
                    "provider": "openai",
                    "name": "Test Model",
                    "capabilities": ["text-generation"],
                    "cost_per_1k_input_tokens": -0.01,  # Negative cost
                    "cost_per_1k_output_tokens": 0.03,
                    "rate_limits": {
                        "requests_per_minute": 500,
                        "tokens_per_minute": 150000
                    },
                    "context_window": 128000,
                    "average_response_time_ms": 2000.0
                }
            ]
        }
        self._write_config(invalid_config)
        
        registry = ModelRegistry(self.config_path)
        
        with self.assertRaises(ConfigurationError):
            registry.load_config()
    
    def test_load_config_with_zero_rate_limits(self):
        """Test loading configuration with zero rate limits"""
        invalid_config = {
            "models": [
                {
                    "id": "test-model",
                    "provider": "openai",
                    "name": "Test Model",
                    "capabilities": ["text-generation"],
                    "cost_per_1k_input_tokens": 0.01,
                    "cost_per_1k_output_tokens": 0.03,
                    "rate_limits": {
                        "requests_per_minute": 0,  # Zero rate limit
                        "tokens_per_minute": 150000
                    },
                    "context_window": 128000,
                    "average_response_time_ms": 2000.0
                }
            ]
        }
        self._write_config(invalid_config)
        
        registry = ModelRegistry(self.config_path)
        
        with self.assertRaises(ConfigurationError):
            registry.load_config()
    
    def test_query_methods_on_empty_registry(self):
        """Test query methods on registry with no models loaded"""
        empty_config = {"models": []}
        self._write_config(empty_config)
        
        registry = ModelRegistry(self.config_path)
        registry.load_config()
        
        # All queries should return empty results
        self.assertIsNone(registry.get_model("any-model"))
        self.assertEqual(len(registry.get_models_by_provider("openai")), 0)
        self.assertEqual(len(registry.get_models_by_capability("text-generation")), 0)
        self.assertEqual(len(registry.get_models_by_cost_range(0.0, 1.0)), 0)
    
    def test_get_models_by_cost_range_with_large_range(self):
        """Test cost range query with very large range"""
        self._write_config(self.valid_config)
        
        registry = ModelRegistry(self.config_path)
        registry.load_config()
        
        # Very large range should include all models
        all_models = registry.get_models_by_cost_range(0.0, 1000000.0)
        self.assertEqual(len(all_models), 3)
    
    def test_update_model_with_different_id(self):
        """Test updating model with metadata that has different ID"""
        self._write_config(self.valid_config)
        
        registry = ModelRegistry(self.config_path)
        registry.load_config()
        
        # Try to update with mismatched ID
        mismatched_metadata = ModelMetadata(
            id="different-id",  # Different from target
            provider="openai",
            name="Updated Model",
            capabilities=["text-generation"],
            cost_per_1k_input_tokens=0.02,
            cost_per_1k_output_tokens=0.04,
            rate_limits=RateLimits(requests_per_minute=600, tokens_per_minute=160000),
            context_window=128000,
            average_response_time_ms=1800.0,
            enabled=True
        )
        
        result = registry.update_model("gpt-4-turbo", mismatched_metadata)
        self.assertTrue(result)
        
        # The model should be updated with the new metadata
        updated_model = registry.get_model("gpt-4-turbo")
        self.assertEqual(updated_model.id, "different-id")
    
    def test_get_models_by_multiple_capabilities(self):
        """Test that models with multiple capabilities are found correctly"""
        self._write_config(self.valid_config)
        
        registry = ModelRegistry(self.config_path)
        registry.load_config()
        
        # GPT-4 has both text-generation and code-generation
        text_gen = registry.get_models_by_capability("text-generation")
        code_gen = registry.get_models_by_capability("code-generation")
        
        # GPT-4 should be in both lists
        gpt4_in_text = any(m.id == "gpt-4-turbo" for m in text_gen)
        gpt4_in_code = any(m.id == "gpt-4-turbo" for m in code_gen)
        
        self.assertTrue(gpt4_in_text)
        self.assertTrue(gpt4_in_code)


if __name__ == "__main__":
    unittest.main()

