"""
Property-based tests for Provider Adapters.

This module tests the correctness properties of provider adapters including
request authentication and formatting, request/response normalization, and
token usage and cost extraction.
"""

import unittest
import json
from typing import Dict, Any
from unittest.mock import AsyncMock, MagicMock, patch

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
        def lists(self, *args, **kwargs): return lambda: []
        def dictionaries(self, *args, **kwargs): return lambda: {}
        def sampled_from(self, seq): return lambda: seq[0] if seq else None
        def builds(self, cls, **kwargs): return lambda: cls(**kwargs)
    
    st = MockStrategies()
    
    def settings(**kwargs):
        def decorator(func):
            return func
        return decorator

from agentic_sdlc.orchestration.api_model_management.adapters.openai_adapter import OpenAIAdapter
from agentic_sdlc.orchestration.api_model_management.adapters.anthropic_adapter import AnthropicAdapter
from agentic_sdlc.orchestration.api_model_management.adapters.google_adapter import GoogleAdapter
from agentic_sdlc.orchestration.api_model_management.adapters.ollama_adapter import OllamaAdapter
from agentic_sdlc.orchestration.api_model_management.models import (
    ModelRequest,
    ModelResponse,
    TokenUsage
)


# Hypothesis strategies for generating test data

def provider_strategy():
    """Strategy for generating provider names"""
    return st.sampled_from(["openai", "anthropic", "google", "ollama"])


def model_id_strategy(provider: str):
    """Strategy for generating model IDs based on provider"""
    model_ids = {
        "openai": ["gpt-4-turbo", "gpt-4", "gpt-3.5-turbo"],
        "anthropic": ["claude-3.5-sonnet", "claude-3-opus", "claude-3-sonnet"],
        "google": ["gemini-pro", "gemini-1.5-pro", "gemini-1.5-flash"],
        "ollama": ["llama2", "mistral", "codellama"]
    }
    return st.sampled_from(model_ids.get(provider, ["test-model"]))


def prompt_strategy():
    """Strategy for generating prompts"""
    return st.text(min_size=10, max_size=500)


def api_key_strategy():
    """Strategy for generating API keys"""
    return st.text(
        min_size=20,
        max_size=100,
        alphabet=st.characters(
            whitelist_categories=('Lu', 'Ll', 'Nd'),
            whitelist_characters='-_'
        )
    )


def temperature_strategy():
    """Strategy for generating temperature values"""
    return st.floats(min_value=0.0, max_value=2.0)


def max_tokens_strategy():
    """Strategy for generating max_tokens values"""
    return st.integers(min_value=100, max_value=4096)


def token_usage_strategy():
    """Strategy for generating token usage"""
    return st.builds(
        TokenUsage,
        input_tokens=st.integers(min_value=1, max_value=10000),
        output_tokens=st.integers(min_value=1, max_value=10000),
        total_tokens=st.integers(min_value=2, max_value=20000)
    )


def model_request_strategy():
    """Strategy for generating ModelRequest objects"""
    return st.builds(
        ModelRequest,
        prompt=prompt_strategy(),
        parameters=st.dictionaries(
            keys=st.text(min_size=1, max_size=20),
            values=st.one_of(
                st.text(min_size=1, max_size=50),
                st.integers(min_value=0, max_value=1000),
                st.floats(min_value=0.0, max_value=2.0),
                st.booleans()
            ),
            max_size=5
        ),
        task_id=st.text(min_size=5, max_size=50),
        agent_type=st.sampled_from(["PM", "BA", "SA", "Research", "Quality", "Implementation"]),
        max_tokens=st.one_of(st.none(), max_tokens_strategy()),
        temperature=temperature_strategy()
    )


def cost_per_1k_strategy():
    """Strategy for generating cost per 1k tokens"""
    return st.floats(min_value=0.0001, max_value=0.1)


class TestProviderAdapterProperties(unittest.TestCase):
    """Test Provider Adapter correctness properties"""
    
    def setUp(self):
        """Set up test case"""
        if not HYPOTHESIS_AVAILABLE:
            self.skipTest("Hypothesis not available")
        
        # Create adapter instances
        self.openai_adapter = OpenAIAdapter()
        self.anthropic_adapter = AnthropicAdapter()
        self.google_adapter = GoogleAdapter()
        self.ollama_adapter = OllamaAdapter()
        
        self.adapters = {
            "openai": self.openai_adapter,
            "anthropic": self.anthropic_adapter,
            "google": self.google_adapter,
            "ollama": self.ollama_adapter
        }
    
    def _create_mock_response(
        self,
        provider: str,
        model_id: str,
        content: str,
        input_tokens: int,
        output_tokens: int
    ) -> Dict[str, Any]:
        """Create a mock API response for a given provider"""
        if provider == "openai":
            return {
                "id": "chatcmpl-test",
                "model": model_id,
                "choices": [
                    {
                        "message": {"content": content},
                        "finish_reason": "stop"
                    }
                ],
                "usage": {
                    "prompt_tokens": input_tokens,
                    "completion_tokens": output_tokens,
                    "total_tokens": input_tokens + output_tokens
                },
                "created": 1234567890
            }
        elif provider == "anthropic":
            return {
                "id": "msg_test",
                "type": "message",
                "model": model_id,
                "content": [
                    {"type": "text", "text": content}
                ],
                "usage": {
                    "input_tokens": input_tokens,
                    "output_tokens": output_tokens
                },
                "stop_reason": "end_turn"
            }
        elif provider == "google":
            return {
                "candidates": [
                    {
                        "content": {
                            "parts": [{"text": content}]
                        },
                        "finishReason": "STOP"
                    }
                ],
                "usageMetadata": {
                    "promptTokenCount": input_tokens,
                    "candidatesTokenCount": output_tokens,
                    "totalTokenCount": input_tokens + output_tokens
                }
            }
        elif provider == "ollama":
            return {
                "model": model_id,
                "response": content,
                "done": True,
                "prompt_eval_count": input_tokens,
                "eval_count": output_tokens
            }
        else:
            raise ValueError(f"Unknown provider: {provider}")
    
    @settings(max_examples=10)
    @given(
        provider=provider_strategy(),
        request=model_request_strategy(),
        api_key=api_key_strategy()
    )
    def test_property_27_request_authentication_and_formatting(
        self,
        provider: str,
        request: ModelRequest,
        api_key: str
    ):
        """
        Feature: api-model-management
        Property 27: Request authentication and formatting
        
        For any request to a model, the generated HTTP request should include
        authentication headers and be formatted according to the provider's
        API specification.
        
        Validates: Requirements 7.1
        """
        adapter = self.adapters[provider]
        
        # Generate model ID for this provider
        model_ids = {
            "openai": "gpt-4-turbo",
            "anthropic": "claude-3.5-sonnet",
            "google": "gemini-pro",
            "ollama": "llama2"
        }
        model_id = model_ids[provider]
        
        # Test header generation
        headers = adapter.get_headers(api_key)
        
        # Verify headers contain authentication
        self.assertIsInstance(headers, dict, "Headers should be a dictionary")
        self.assertGreater(len(headers), 0, "Headers should not be empty")
        
        # Verify provider-specific authentication
        if provider == "openai":
            self.assertIn("Authorization", headers, "OpenAI should have Authorization header")
            self.assertTrue(
                headers["Authorization"].startswith("Bearer "),
                "OpenAI should use Bearer token authentication"
            )
            self.assertIn(api_key, headers["Authorization"], "API key should be in Authorization header")
        elif provider == "anthropic":
            self.assertIn("x-api-key", headers, "Anthropic should have x-api-key header")
            self.assertEqual(headers["x-api-key"], api_key, "Anthropic API key should match")
            self.assertIn("anthropic-version", headers, "Anthropic should have version header")
        elif provider == "google":
            # Google uses API key in URL or header
            self.assertIn("Content-Type", headers, "Google should have Content-Type header")
        elif provider == "ollama":
            # Ollama doesn't require authentication for local instances
            self.assertIn("Content-Type", headers, "Ollama should have Content-Type header")
        
        # Test request body formatting
        body = adapter.format_request_body(model_id, request)
        
        # Verify body is a dictionary
        self.assertIsInstance(body, dict, "Request body should be a dictionary")
        
        # Verify required fields based on provider
        if provider == "openai":
            self.assertIn("model", body, "OpenAI request should have model field")
            self.assertEqual(body["model"], model_id, "Model ID should match")
            self.assertIn("messages", body, "OpenAI request should have messages field")
            self.assertIsInstance(body["messages"], list, "Messages should be a list")
            self.assertGreater(len(body["messages"]), 0, "Messages should not be empty")
            self.assertIn("temperature", body, "OpenAI request should have temperature")
        elif provider == "anthropic":
            self.assertIn("model", body, "Anthropic request should have model field")
            self.assertEqual(body["model"], model_id, "Model ID should match")
            self.assertIn("messages", body, "Anthropic request should have messages field")
            self.assertIn("max_tokens", body, "Anthropic request should have max_tokens")
            self.assertIn("temperature", body, "Anthropic request should have temperature")
        elif provider == "google":
            self.assertIn("contents", body, "Google request should have contents field")
            self.assertIsInstance(body["contents"], list, "Contents should be a list")
        elif provider == "ollama":
            self.assertIn("model", body, "Ollama request should have model field")
            self.assertIn("prompt", body, "Ollama request should have prompt field")
    
    @settings(max_examples=10)
    @given(
        provider=provider_strategy(),
        content=st.text(min_size=10, max_size=500),
        input_tokens=st.integers(min_value=10, max_value=5000),
        output_tokens=st.integers(min_value=10, max_value=5000)
    )
    def test_property_30_provider_adapter_request_response_normalization(
        self,
        provider: str,
        content: str,
        input_tokens: int,
        output_tokens: int
    ):
        """
        Feature: api-model-management
        Property 30: Provider adapter request/response normalization
        
        For any request to a provider, the provider-specific adapter should
        format the request, parse the response, and normalize it to the common
        ModelResponse format.
        
        Validates: Requirements 16.2, 16.3, 16.4
        """
        adapter = self.adapters[provider]
        
        # Generate model ID for this provider
        model_ids = {
            "openai": "gpt-4-turbo",
            "anthropic": "claude-3.5-sonnet",
            "google": "gemini-pro",
            "ollama": "llama2"
        }
        model_id = model_ids[provider]
        
        # Create mock provider-specific response
        raw_response = self._create_mock_response(
            provider,
            model_id,
            content,
            input_tokens,
            output_tokens
        )
        
        # Parse response using adapter
        normalized_response = adapter.parse_response(raw_response)
        
        # Verify normalized response is ModelResponse
        self.assertIsInstance(
            normalized_response,
            ModelResponse,
            "Parsed response should be ModelResponse instance"
        )
        
        # Verify content is extracted correctly
        self.assertEqual(
            normalized_response.content,
            content,
            "Response content should match original content"
        )
        
        # Verify token usage is extracted
        self.assertIsInstance(
            normalized_response.token_usage,
            TokenUsage,
            "Token usage should be TokenUsage instance"
        )
        
        # Verify token counts match
        self.assertEqual(
            normalized_response.token_usage.input_tokens,
            input_tokens,
            "Input tokens should match"
        )
        self.assertEqual(
            normalized_response.token_usage.output_tokens,
            output_tokens,
            "Output tokens should match"
        )
        self.assertEqual(
            normalized_response.token_usage.total_tokens,
            input_tokens + output_tokens,
            "Total tokens should be sum of input and output"
        )
        
        # Verify metadata is present
        self.assertIsInstance(
            normalized_response.metadata,
            dict,
            "Metadata should be a dictionary"
        )
    
    @settings(max_examples=10)
    @given(
        provider=provider_strategy(),
        input_tokens=st.integers(min_value=10, max_value=10000),
        output_tokens=st.integers(min_value=10, max_value=10000),
        cost_per_1k_input=cost_per_1k_strategy(),
        cost_per_1k_output=cost_per_1k_strategy()
    )
    def test_property_31_token_usage_and_cost_extraction(
        self,
        provider: str,
        input_tokens: int,
        output_tokens: int,
        cost_per_1k_input: float,
        cost_per_1k_output: float
    ):
        """
        Feature: api-model-management
        Property 31: Token usage and cost extraction
        
        For any successful API response, the extracted token usage (input and
        output tokens) and calculated cost should match the provider's response
        data.
        
        Validates: Requirements 7.5
        """
        adapter = self.adapters[provider]
        
        # Generate model ID for this provider
        model_ids = {
            "openai": "gpt-4-turbo",
            "anthropic": "claude-3.5-sonnet",
            "google": "gemini-pro",
            "ollama": "llama2"
        }
        model_id = model_ids[provider]
        
        # Create mock provider-specific response
        raw_response = self._create_mock_response(
            provider,
            model_id,
            "Test response content",
            input_tokens,
            output_tokens
        )
        
        # Extract token usage using adapter
        token_usage = adapter.extract_token_usage(raw_response)
        
        # Verify token usage is TokenUsage instance
        self.assertIsInstance(
            token_usage,
            TokenUsage,
            "Extracted token usage should be TokenUsage instance"
        )
        
        # Verify input tokens match
        self.assertEqual(
            token_usage.input_tokens,
            input_tokens,
            "Extracted input tokens should match provider response"
        )
        
        # Verify output tokens match
        self.assertEqual(
            token_usage.output_tokens,
            output_tokens,
            "Extracted output tokens should match provider response"
        )
        
        # Verify total tokens is sum of input and output
        self.assertEqual(
            token_usage.total_tokens,
            input_tokens + output_tokens,
            "Total tokens should be sum of input and output tokens"
        )
        
        # Calculate cost using adapter's cost calculation method
        calculated_cost = adapter.calculate_cost(
            input_tokens,
            output_tokens,
            cost_per_1k_input,
            cost_per_1k_output
        )
        
        # Verify cost calculation is correct
        expected_cost = (
            (input_tokens / 1000.0) * cost_per_1k_input +
            (output_tokens / 1000.0) * cost_per_1k_output
        )
        
        # Allow small floating point differences
        self.assertAlmostEqual(
            calculated_cost,
            expected_cost,
            places=6,
            msg="Calculated cost should match expected cost formula"
        )
        
        # Verify cost is non-negative
        self.assertGreaterEqual(
            calculated_cost,
            0.0,
            "Cost should be non-negative"
        )
        
        # Verify cost is reasonable (not NaN or infinity)
        self.assertFalse(
            calculated_cost != calculated_cost,  # NaN check
            "Cost should not be NaN"
        )
        self.assertTrue(
            calculated_cost < float('inf'),
            "Cost should not be infinity"
        )


if __name__ == "__main__":
    unittest.main()
