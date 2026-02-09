"""
Property-based tests for ModelRegistry class.

This module tests the correctness properties of the ModelRegistry including
configuration validation and query filtering.
"""

import unittest
import json
import tempfile
from pathlib import Path
from typing import Dict, Any, List

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

from agentic_sdlc.orchestration.api_model_management.registry import ModelRegistry
from agentic_sdlc.orchestration.api_model_management.models import ModelMetadata, RateLimits
from agentic_sdlc.orchestration.api_model_management.exceptions import ConfigurationError


# Hypothesis strategies for generating test data

def valid_model_config_strategy():
    """Strategy for generating valid model configurations"""
    return st.builds(
        dict,
        id=st.text(min_size=1, max_size=50, alphabet=st.characters(blacklist_categories=('Cs',))),
        provider=st.sampled_from(["openai", "anthropic", "google", "ollama"]),
        name=st.text(min_size=1, max_size=100, alphabet=st.characters(blacklist_categories=('Cs',))),
        capabilities=st.lists(
            st.sampled_from(["text-generation", "code-generation", "analysis", "reasoning"]),
            min_size=1,
            max_size=5,
            unique=True
        ),
        cost_per_1k_input_tokens=st.floats(min_value=0.0, max_value=1.0, allow_nan=False, allow_infinity=False),
        cost_per_1k_output_tokens=st.floats(min_value=0.0, max_value=1.0, allow_nan=False, allow_infinity=False),
        rate_limits=st.builds(
            dict,
            requests_per_minute=st.integers(min_value=1, max_value=10000),
            tokens_per_minute=st.integers(min_value=1000, max_value=1000000)
        ),
        context_window=st.integers(min_value=1000, max_value=200000),
        average_response_time_ms=st.floats(min_value=100.0, max_value=10000.0, allow_nan=False, allow_infinity=False),
        enabled=st.booleans()
    )


def invalid_model_config_strategy():
    """Strategy for generating invalid model configurations"""
    return st.one_of(
        # Missing required field 'id'
        st.builds(
            dict,
            provider=st.sampled_from(["openai", "anthropic"]),
            name=st.text(min_size=1, max_size=100),
            capabilities=st.lists(st.sampled_from(["text-generation"]), min_size=1),
            cost_per_1k_input_tokens=st.floats(min_value=0.0, max_value=1.0),
            cost_per_1k_output_tokens=st.floats(min_value=0.0, max_value=1.0),
            rate_limits=st.builds(
                dict,
                requests_per_minute=st.integers(min_value=1, max_value=10000),
                tokens_per_minute=st.integers(min_value=1000, max_value=1000000)
            ),
            context_window=st.integers(min_value=1000, max_value=200000),
            average_response_time_ms=st.floats(min_value=100.0, max_value=10000.0)
        ),
        # Empty capabilities list
        st.builds(
            dict,
            id=st.text(min_size=1, max_size=50),
            provider=st.sampled_from(["openai", "anthropic"]),
            name=st.text(min_size=1, max_size=100),
            capabilities=st.just([]),  # Invalid: empty list
            cost_per_1k_input_tokens=st.floats(min_value=0.0, max_value=1.0),
            cost_per_1k_output_tokens=st.floats(min_value=0.0, max_value=1.0),
            rate_limits=st.builds(
                dict,
                requests_per_minute=st.integers(min_value=1, max_value=10000),
                tokens_per_minute=st.integers(min_value=1000, max_value=1000000)
            ),
            context_window=st.integers(min_value=1000, max_value=200000),
            average_response_time_ms=st.floats(min_value=100.0, max_value=10000.0)
        ),
        # Invalid cost type (string instead of number)
        st.builds(
            dict,
            id=st.text(min_size=1, max_size=50),
            provider=st.sampled_from(["openai", "anthropic"]),
            name=st.text(min_size=1, max_size=100),
            capabilities=st.lists(st.sampled_from(["text-generation"]), min_size=1),
            cost_per_1k_input_tokens=st.just("invalid"),  # Invalid: string instead of number
            cost_per_1k_output_tokens=st.floats(min_value=0.0, max_value=1.0),
            rate_limits=st.builds(
                dict,
                requests_per_minute=st.integers(min_value=1, max_value=10000),
                tokens_per_minute=st.integers(min_value=1000, max_value=1000000)
            ),
            context_window=st.integers(min_value=1000, max_value=200000),
            average_response_time_ms=st.floats(min_value=100.0, max_value=10000.0)
        ),
        # Negative rate limit
        st.builds(
            dict,
            id=st.text(min_size=1, max_size=50),
            provider=st.sampled_from(["openai", "anthropic"]),
            name=st.text(min_size=1, max_size=100),
            capabilities=st.lists(st.sampled_from(["text-generation"]), min_size=1),
            cost_per_1k_input_tokens=st.floats(min_value=0.0, max_value=1.0),
            cost_per_1k_output_tokens=st.floats(min_value=0.0, max_value=1.0),
            rate_limits=st.builds(
                dict,
                requests_per_minute=st.just(-1),  # Invalid: negative value
                tokens_per_minute=st.integers(min_value=1000, max_value=1000000)
            ),
            context_window=st.integers(min_value=1000, max_value=200000),
            average_response_time_ms=st.floats(min_value=100.0, max_value=10000.0)
        )
    )


class TestModelRegistryProperties(unittest.TestCase):
    """Test ModelRegistry correctness properties"""
    
    def setUp(self):
        """Set up test case"""
        if not HYPOTHESIS_AVAILABLE:
            self.skipTest("Hypothesis not available")
        
        self.temp_dir = tempfile.mkdtemp()
        self.config_path = Path(self.temp_dir) / "test_config.json"
    
    def _write_config(self, config_data: Dict[str, Any]) -> None:
        """Helper to write configuration to file"""
        with open(self.config_path, 'w') as f:
            json.dump(config_data, f)
    
    @settings(max_examples=100)
    @given(invalid_model=invalid_model_config_strategy())
    def test_property_2_invalid_model_configuration_rejection(self, invalid_model: Dict[str, Any]):
        """
        Feature: api-model-management
        Property 2: Invalid model configuration rejection
        
        For any model configuration with missing required fields or invalid values,
        the registry should reject it and exclude it from available models.
        
        Validates: Requirements 1.3
        """
        # Create configuration with invalid model
        config = {"models": [invalid_model]}
        self._write_config(config)
        
        # Attempt to load configuration
        registry = ModelRegistry(self.config_path)
        
        # Should raise ConfigurationError
        with self.assertRaises(ConfigurationError) as context:
            registry.load_config()
        
        # Verify error contains useful information
        self.assertIsNotNone(context.exception.message)
        
        # Verify no models were loaded
        # (Registry should be empty or raise error before loading)
        self.assertEqual(len(registry._models), 0)
    
    @settings(max_examples=100)
    @given(
        models=st.lists(valid_model_config_strategy(), min_size=3, max_size=10, unique_by=lambda x: x['id']),
        query_provider=st.sampled_from(["openai", "anthropic", "google", "ollama"]),
        query_capability=st.sampled_from(["text-generation", "code-generation", "analysis", "reasoning"]),
        min_cost=st.floats(min_value=0.0, max_value=0.5, allow_nan=False, allow_infinity=False),
        max_cost=st.floats(min_value=0.5, max_value=1.0, allow_nan=False, allow_infinity=False)
    )
    def test_property_3_model_query_filtering(
        self,
        models: List[Dict[str, Any]],
        query_provider: str,
        query_capability: str,
        min_cost: float,
        max_cost: float
    ):
        """
        Feature: api-model-management
        Property 3: Model query filtering
        
        For any query criteria (provider, capability, or cost range), all returned
        models should match the criteria and no matching models should be excluded.
        
        Validates: Requirements 1.4
        """
        # Ensure min_cost <= max_cost
        if min_cost > max_cost:
            min_cost, max_cost = max_cost, min_cost
        
        # Create configuration with models
        config = {"models": models}
        self._write_config(config)
        
        # Load configuration
        registry = ModelRegistry(self.config_path)
        registry.load_config()
        
        # Test 1: Query by provider
        provider_results = registry.get_models_by_provider(query_provider)
        
        # All returned models should match the provider
        for model in provider_results:
            self.assertEqual(model.provider, query_provider)
        
        # No matching models should be excluded
        expected_provider_count = sum(1 for m in models if m['provider'] == query_provider)
        self.assertEqual(len(provider_results), expected_provider_count)
        
        # Test 2: Query by capability
        capability_results = registry.get_models_by_capability(query_capability)
        
        # All returned models should have the capability
        for model in capability_results:
            self.assertIn(query_capability, model.capabilities)
        
        # No matching models should be excluded
        expected_capability_count = sum(
            1 for m in models if query_capability in m['capabilities']
        )
        self.assertEqual(len(capability_results), expected_capability_count)
        
        # Test 3: Query by cost range
        cost_results = registry.get_models_by_cost_range(min_cost, max_cost)
        
        # All returned models should be within the cost range
        for model in cost_results:
            avg_cost = (model.cost_per_1k_input_tokens + model.cost_per_1k_output_tokens) / 2
            self.assertGreaterEqual(avg_cost, min_cost)
            self.assertLessEqual(avg_cost, max_cost)
        
        # No matching models should be excluded
        expected_cost_count = 0
        for m in models:
            avg_cost = (m['cost_per_1k_input_tokens'] + m['cost_per_1k_output_tokens']) / 2
            if min_cost <= avg_cost <= max_cost:
                expected_cost_count += 1
        
        self.assertEqual(len(cost_results), expected_cost_count)


if __name__ == "__main__":
    unittest.main()
