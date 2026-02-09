"""
Unit tests for Provider Adapters.

This module tests provider-specific adapters with sample responses,
error handling, and rate limit error detection.

Tests Requirements: 16.1, 16.2, 16.3
"""

import unittest
import json
from unittest.mock import AsyncMock, MagicMock, patch
import httpx

from agentic_sdlc.orchestration.api_model_management.adapters.openai_adapter import OpenAIAdapter
from agentic_sdlc.orchestration.api_model_management.adapters.anthropic_adapter import AnthropicAdapter
from agentic_sdlc.orchestration.api_model_management.adapters.google_adapter import GoogleAdapter
from agentic_sdlc.orchestration.api_model_management.adapters.ollama_adapter import OllamaAdapter
from agentic_sdlc.orchestration.api_model_management.models import (
    ModelRequest,
    ModelResponse,
    TokenUsage
)
from agentic_sdlc.orchestration.api_model_management.exceptions import (
    ProviderError,
    RateLimitError,
    AuthenticationError,
    InvalidRequestError
)


class TestOpenAIAdapter(unittest.IsolatedAsyncioTestCase):
    """Unit tests for OpenAI adapter"""
    
    def setUp(self):
        """Set up test case"""
        self.adapter = OpenAIAdapter()
        self.model_id = "gpt-4-turbo"
        self.api_key = "sk-test-key-123"
        self.request = ModelRequest(
            prompt="Test prompt",
            parameters={},
            task_id="test-task-1",
            agent_type="PM",
            max_tokens=100,
            temperature=0.7
        )
    
    async def asyncTearDown(self):
        """Clean up after test"""
        await self.adapter.close()
    
    def test_parse_response_with_valid_openai_response(self):
        """Test parsing a valid OpenAI API response"""
        raw_response = {
            "id": "chatcmpl-123",
            "model": "gpt-4-turbo",
            "choices": [
                {
                    "message": {"content": "This is a test response"},
                    "finish_reason": "stop"
                }
            ],
            "usage": {
                "prompt_tokens": 10,
                "completion_tokens": 20,
                "total_tokens": 30
            },
            "created": 1234567890
        }
        
        response = self.adapter.parse_response(raw_response)
        
        self.assertIsInstance(response, ModelResponse)
        self.assertEqual(response.content, "This is a test response")
        self.assertEqual(response.token_usage.input_tokens, 10)
        self.assertEqual(response.token_usage.output_tokens, 20)
        self.assertEqual(response.token_usage.total_tokens, 30)
        self.assertEqual(response.metadata["finish_reason"], "stop")
        self.assertEqual(response.metadata["response_id"], "chatcmpl-123")
    
    def test_parse_response_with_missing_fields(self):
        """Test parsing OpenAI response with missing required fields"""
        raw_response = {
            "id": "chatcmpl-123",
            "model": "gpt-4-turbo"
            # Missing choices and usage
        }
        
        with self.assertRaises(ProviderError) as context:
            self.adapter.parse_response(raw_response)
        
        self.assertIn("Failed to parse OpenAI response", str(context.exception))
    
    def test_extract_token_usage_valid(self):
        """Test extracting token usage from valid OpenAI response"""
        raw_response = {
            "usage": {
                "prompt_tokens": 50,
                "completion_tokens": 100,
                "total_tokens": 150
            }
        }
        
        token_usage = self.adapter.extract_token_usage(raw_response)
        
        self.assertIsInstance(token_usage, TokenUsage)
        self.assertEqual(token_usage.input_tokens, 50)
        self.assertEqual(token_usage.output_tokens, 100)
        self.assertEqual(token_usage.total_tokens, 150)
    
    def test_extract_token_usage_missing(self):
        """Test extracting token usage when usage field is missing"""
        raw_response = {"id": "test"}
        
        with self.assertRaises(ProviderError) as context:
            self.adapter.extract_token_usage(raw_response)
        
        self.assertIn("Failed to extract token usage", str(context.exception))
    
    async def test_handle_error_rate_limit(self):
        """Test handling rate limit error (HTTP 429)"""
        mock_response = MagicMock(spec=httpx.Response)
        mock_response.status_code = 429
        mock_response.headers = {"retry-after": "60"}
        mock_response.json.return_value = {
            "error": {
                "message": "Rate limit exceeded",
                "type": "rate_limit_error"
            }
        }
        
        with self.assertRaises(RateLimitError) as context:
            await self.adapter._handle_error(mock_response, self.model_id, "test-task")
        
        self.assertIn("Rate limit exceeded", str(context.exception))
        self.assertEqual(context.exception.retry_after, 60)
    
    async def test_handle_error_authentication(self):
        """Test handling authentication error (HTTP 401)"""
        mock_response = MagicMock(spec=httpx.Response)
        mock_response.status_code = 401
        mock_response.json.return_value = {
            "error": {
                "message": "Invalid API key",
                "type": "invalid_api_key"
            }
        }
        
        with self.assertRaises(AuthenticationError) as context:
            await self.adapter._handle_error(mock_response, self.model_id, "test-task")
        
        self.assertIn("Authentication failed", str(context.exception))
        self.assertEqual(context.exception.provider, "openai")
    
    async def test_handle_error_invalid_request(self):
        """Test handling invalid request error (HTTP 400)"""
        mock_response = MagicMock(spec=httpx.Response)
        mock_response.status_code = 400
        mock_response.json.return_value = {
            "error": {
                "message": "Invalid parameter",
                "type": "invalid_request_error"
            }
        }
        
        with self.assertRaises(InvalidRequestError) as context:
            await self.adapter._handle_error(mock_response, self.model_id, "test-task")
        
        self.assertIn("Invalid request", str(context.exception))
    
    async def test_handle_error_server_error(self):
        """Test handling server error (HTTP 500)"""
        mock_response = MagicMock(spec=httpx.Response)
        mock_response.status_code = 500
        mock_response.json.return_value = {
            "error": {
                "message": "Internal server error",
                "type": "server_error"
            }
        }
        
        with self.assertRaises(ProviderError) as context:
            await self.adapter._handle_error(mock_response, self.model_id, "test-task")
        
        self.assertIn("server error", str(context.exception))
        self.assertTrue(context.exception.is_retryable)
    
    def test_is_rate_limit_error_with_rate_limit_exception(self):
        """Test rate limit error detection with RateLimitError"""
        error = RateLimitError("Rate limit", model_id="test", task_id="test")
        self.assertTrue(self.adapter.is_rate_limit_error(error))
    
    def test_is_rate_limit_error_with_provider_error_429(self):
        """Test rate limit error detection with ProviderError status 429"""
        error = ProviderError(
            "Error",
            provider="openai",
            model_id="test",
            status_code=429,
            task_id="test"
        )
        self.assertTrue(self.adapter.is_rate_limit_error(error))
    
    def test_is_rate_limit_error_with_other_error(self):
        """Test rate limit error detection with non-rate-limit error"""
        error = ValueError("Some error")
        self.assertFalse(self.adapter.is_rate_limit_error(error))


class TestAnthropicAdapter(unittest.IsolatedAsyncioTestCase):
    """Unit tests for Anthropic adapter"""
    
    def setUp(self):
        """Set up test case"""
        self.adapter = AnthropicAdapter()
        self.model_id = "claude-3.5-sonnet"
        self.api_key = "sk-ant-test-key"
        self.request = ModelRequest(
            prompt="Test prompt",
            parameters={},
            task_id="test-task-1",
            agent_type="BA",
            max_tokens=200,
            temperature=0.8
        )
    
    async def asyncTearDown(self):
        """Clean up after test"""
        await self.adapter.close()
    
    def test_parse_response_with_valid_anthropic_response(self):
        """Test parsing a valid Anthropic API response"""
        raw_response = {
            "id": "msg_123",
            "type": "message",
            "model": "claude-3.5-sonnet",
            "content": [
                {"type": "text", "text": "First part"},
                {"type": "text", "text": " Second part"}
            ],
            "usage": {
                "input_tokens": 15,
                "output_tokens": 25
            },
            "stop_reason": "end_turn"
        }
        
        response = self.adapter.parse_response(raw_response)
        
        self.assertIsInstance(response, ModelResponse)
        self.assertEqual(response.content, "First part Second part")
        self.assertEqual(response.token_usage.input_tokens, 15)
        self.assertEqual(response.token_usage.output_tokens, 25)
        self.assertEqual(response.token_usage.total_tokens, 40)
        self.assertEqual(response.metadata["stop_reason"], "end_turn")
    
    def test_parse_response_with_missing_content(self):
        """Test parsing Anthropic response with missing content"""
        raw_response = {
            "id": "msg_123",
            "type": "message",
            "model": "claude-3.5-sonnet"
            # Missing content and usage
        }
        
        with self.assertRaises(ProviderError) as context:
            self.adapter.parse_response(raw_response)
        
        self.assertIn("Failed to parse Anthropic response", str(context.exception))
    
    def test_extract_token_usage_valid(self):
        """Test extracting token usage from valid Anthropic response"""
        raw_response = {
            "usage": {
                "input_tokens": 30,
                "output_tokens": 70
            }
        }
        
        token_usage = self.adapter.extract_token_usage(raw_response)
        
        self.assertIsInstance(token_usage, TokenUsage)
        self.assertEqual(token_usage.input_tokens, 30)
        self.assertEqual(token_usage.output_tokens, 70)
        self.assertEqual(token_usage.total_tokens, 100)
    
    async def test_handle_error_rate_limit(self):
        """Test handling rate limit error for Anthropic"""
        mock_response = MagicMock(spec=httpx.Response)
        mock_response.status_code = 429
        mock_response.headers = {"retry-after": "30"}
        mock_response.json.return_value = {
            "error": {
                "message": "Rate limit exceeded",
                "type": "rate_limit_error"
            }
        }
        
        with self.assertRaises(RateLimitError) as context:
            await self.adapter._handle_error(mock_response, self.model_id, "test-task")
        
        self.assertIn("Rate limit exceeded", str(context.exception))
        self.assertEqual(context.exception.retry_after, 30)


class TestGoogleAdapter(unittest.IsolatedAsyncioTestCase):
    """Unit tests for Google adapter"""
    
    def setUp(self):
        """Set up test case"""
        self.adapter = GoogleAdapter()
        self.model_id = "gemini-pro"
        self.api_key = "AIza-test-key"
        self.request = ModelRequest(
            prompt="Test prompt",
            parameters={},
            task_id="test-task-1",
            agent_type="SA",
            max_tokens=150,
            temperature=0.5
        )
    
    async def asyncTearDown(self):
        """Clean up after test"""
        await self.adapter.close()
    
    def test_parse_response_with_valid_google_response(self):
        """Test parsing a valid Google API response"""
        raw_response = {
            "candidates": [
                {
                    "content": {
                        "parts": [
                            {"text": "Response part 1"},
                            {"text": " Response part 2"}
                        ]
                    },
                    "finishReason": "STOP",
                    "safetyRatings": []
                }
            ],
            "usageMetadata": {
                "promptTokenCount": 20,
                "candidatesTokenCount": 40,
                "totalTokenCount": 60
            }
        }
        
        response = self.adapter.parse_response(raw_response)
        
        self.assertIsInstance(response, ModelResponse)
        self.assertEqual(response.content, "Response part 1 Response part 2")
        self.assertEqual(response.token_usage.input_tokens, 20)
        self.assertEqual(response.token_usage.output_tokens, 40)
        self.assertEqual(response.token_usage.total_tokens, 60)
        self.assertEqual(response.metadata["finish_reason"], "STOP")
    
    def test_parse_response_with_no_candidates(self):
        """Test parsing Google response with no candidates"""
        raw_response = {
            "candidates": [],
            "usageMetadata": {}
        }
        
        with self.assertRaises(ProviderError) as context:
            self.adapter.parse_response(raw_response)
        
        self.assertIn("No candidates", str(context.exception))
    
    def test_extract_token_usage_valid(self):
        """Test extracting token usage from valid Google response"""
        raw_response = {
            "usageMetadata": {
                "promptTokenCount": 25,
                "candidatesTokenCount": 35,
                "totalTokenCount": 60
            }
        }
        
        token_usage = self.adapter.extract_token_usage(raw_response)
        
        self.assertIsInstance(token_usage, TokenUsage)
        self.assertEqual(token_usage.input_tokens, 25)
        self.assertEqual(token_usage.output_tokens, 35)
        self.assertEqual(token_usage.total_tokens, 60)
    
    def test_extract_token_usage_missing(self):
        """Test extracting token usage when metadata is missing (returns zeros)"""
        raw_response = {}
        
        # Google adapter returns zeros when token usage is not available
        token_usage = self.adapter.extract_token_usage(raw_response)
        
        self.assertIsInstance(token_usage, TokenUsage)
        self.assertEqual(token_usage.input_tokens, 0)
        self.assertEqual(token_usage.output_tokens, 0)
        self.assertEqual(token_usage.total_tokens, 0)
    
    async def test_handle_error_authentication(self):
        """Test handling authentication error for Google (403)"""
        mock_response = MagicMock(spec=httpx.Response)
        mock_response.status_code = 403
        mock_response.json.return_value = {
            "error": {
                "message": "API key not valid",
                "code": 403
            }
        }
        
        with self.assertRaises(AuthenticationError) as context:
            await self.adapter._handle_error(mock_response, self.model_id, "test-task")
        
        self.assertIn("Authentication failed", str(context.exception))
        self.assertEqual(context.exception.provider, "google")


class TestOllamaAdapter(unittest.IsolatedAsyncioTestCase):
    """Unit tests for Ollama adapter"""
    
    def setUp(self):
        """Set up test case"""
        self.adapter = OllamaAdapter()
        self.model_id = "llama2"
        self.api_key = ""  # Ollama doesn't use API keys
        self.request = ModelRequest(
            prompt="Test prompt",
            parameters={},
            task_id="test-task-1",
            agent_type="Implementation",
            max_tokens=100,
            temperature=0.7
        )
    
    async def asyncTearDown(self):
        """Clean up after test"""
        await self.adapter.close()
    
    def test_parse_response_with_valid_ollama_response(self):
        """Test parsing a valid Ollama API response"""
        raw_response = {
            "model": "llama2",
            "response": "This is the generated response",
            "done": True,
            "prompt_eval_count": 12,
            "eval_count": 28,
            "total_duration": 1234567890,
            "load_duration": 123456,
            "context": [1, 2, 3]
        }
        
        response = self.adapter.parse_response(raw_response)
        
        self.assertIsInstance(response, ModelResponse)
        self.assertEqual(response.content, "This is the generated response")
        self.assertEqual(response.token_usage.input_tokens, 12)
        self.assertEqual(response.token_usage.output_tokens, 28)
        self.assertEqual(response.token_usage.total_tokens, 40)
        self.assertEqual(response.cost, 0.0)  # Local models have no cost
        self.assertTrue(response.metadata["done"])
    
    def test_parse_response_with_missing_token_counts(self):
        """Test parsing Ollama response with missing token counts (returns zeros)"""
        raw_response = {
            "model": "llama2",
            "response": "Short response",
            "done": True
        }
        
        response = self.adapter.parse_response(raw_response)
        
        self.assertIsInstance(response, ModelResponse)
        self.assertEqual(response.content, "Short response")
        # When token counts are missing, Ollama adapter returns 0
        self.assertEqual(response.token_usage.input_tokens, 0)
        self.assertEqual(response.token_usage.output_tokens, 0)
        self.assertEqual(response.token_usage.total_tokens, 0)
    
    def test_extract_token_usage_valid(self):
        """Test extracting token usage from valid Ollama response"""
        raw_response = {
            "prompt_eval_count": 18,
            "eval_count": 42
        }
        
        token_usage = self.adapter.extract_token_usage(raw_response)
        
        self.assertIsInstance(token_usage, TokenUsage)
        self.assertEqual(token_usage.input_tokens, 18)
        self.assertEqual(token_usage.output_tokens, 42)
        self.assertEqual(token_usage.total_tokens, 60)
    
    def test_extract_token_usage_with_missing_counts(self):
        """Test token usage when counts are missing (returns zeros)"""
        raw_response = {
            "model": "llama2",
            "response": "This is a test response"
        }
        
        token_usage = self.adapter.extract_token_usage(raw_response)
        
        self.assertIsInstance(token_usage, TokenUsage)
        # When counts are missing, returns 0 (uses .get() with default 0)
        self.assertEqual(token_usage.input_tokens, 0)
        self.assertEqual(token_usage.output_tokens, 0)
        self.assertEqual(token_usage.total_tokens, 0)
    
    def test_is_rate_limit_error_always_false(self):
        """Test that Ollama never has rate limit errors (local service)"""
        error1 = RateLimitError("Rate limit", model_id="test", task_id="test")
        error2 = ProviderError("Error", provider="ollama", model_id="test", status_code=429, task_id="test")
        error3 = ValueError("Some error")
        
        # Ollama doesn't have rate limits
        self.assertFalse(self.adapter.is_rate_limit_error(error1))
        self.assertFalse(self.adapter.is_rate_limit_error(error2))
        self.assertFalse(self.adapter.is_rate_limit_error(error3))
    
    async def test_handle_error_model_not_found(self):
        """Test handling model not found error (HTTP 404)"""
        mock_response = MagicMock(spec=httpx.Response)
        mock_response.status_code = 404
        mock_response.json.return_value = {
            "error": "model not found"
        }
        
        with self.assertRaises(ProviderError) as context:
            await self.adapter._handle_error(mock_response, self.model_id, "test-task")
        
        self.assertIn("not found", str(context.exception))
        self.assertFalse(context.exception.is_retryable)


class TestAdapterRequestFormatting(unittest.TestCase):
    """Test request body formatting for all adapters"""
    
    def setUp(self):
        """Set up test case"""
        self.openai_adapter = OpenAIAdapter()
        self.anthropic_adapter = AnthropicAdapter()
        self.google_adapter = GoogleAdapter()
        self.ollama_adapter = OllamaAdapter()
        
        self.request = ModelRequest(
            prompt="Test prompt for formatting",
            parameters={"top_p": 0.9},
            task_id="test-task-1",
            agent_type="PM",
            max_tokens=200,
            temperature=0.7
        )
    
    def test_openai_request_formatting(self):
        """Test OpenAI request body formatting"""
        body = self.openai_adapter.format_request_body("gpt-4-turbo", self.request)
        
        self.assertIn("model", body)
        self.assertEqual(body["model"], "gpt-4-turbo")
        self.assertIn("messages", body)
        self.assertIsInstance(body["messages"], list)
        self.assertEqual(body["messages"][0]["role"], "user")
        self.assertEqual(body["messages"][0]["content"], "Test prompt for formatting")
        self.assertEqual(body["temperature"], 0.7)
        self.assertEqual(body["max_tokens"], 200)
        self.assertEqual(body["top_p"], 0.9)
    
    def test_anthropic_request_formatting(self):
        """Test Anthropic request body formatting"""
        body = self.anthropic_adapter.format_request_body("claude-3.5-sonnet", self.request)
        
        self.assertIn("model", body)
        self.assertEqual(body["model"], "claude-3.5-sonnet")
        self.assertIn("messages", body)
        self.assertIsInstance(body["messages"], list)
        self.assertEqual(body["messages"][0]["role"], "user")
        self.assertEqual(body["messages"][0]["content"], "Test prompt for formatting")
        self.assertEqual(body["temperature"], 0.7)
        self.assertEqual(body["max_tokens"], 200)
        self.assertEqual(body["top_p"], 0.9)
    
    def test_google_request_formatting(self):
        """Test Google request body formatting"""
        body = self.google_adapter.format_request_body("gemini-pro", self.request)
        
        self.assertIn("contents", body)
        self.assertIsInstance(body["contents"], list)
        self.assertIn("parts", body["contents"][0])
        self.assertEqual(body["contents"][0]["parts"][0]["text"], "Test prompt for formatting")
        self.assertIn("generationConfig", body)
        self.assertEqual(body["generationConfig"]["temperature"], 0.7)
        self.assertEqual(body["generationConfig"]["maxOutputTokens"], 200)
        self.assertEqual(body["generationConfig"]["top_p"], 0.9)
    
    def test_ollama_request_formatting(self):
        """Test Ollama request body formatting"""
        body = self.ollama_adapter.format_request_body("llama2", self.request)
        
        self.assertIn("model", body)
        self.assertEqual(body["model"], "llama2")
        self.assertIn("prompt", body)
        self.assertEqual(body["prompt"], "Test prompt for formatting")
        self.assertFalse(body["stream"])
        self.assertIn("options", body)
        self.assertEqual(body["options"]["temperature"], 0.7)
        self.assertEqual(body["options"]["num_predict"], 200)
        self.assertEqual(body["options"]["top_p"], 0.9)


class TestAdapterHeaders(unittest.TestCase):
    """Test header generation for all adapters"""
    
    def setUp(self):
        """Set up test case"""
        self.openai_adapter = OpenAIAdapter()
        self.anthropic_adapter = AnthropicAdapter()
        self.google_adapter = GoogleAdapter()
        self.ollama_adapter = OllamaAdapter()
    
    def test_openai_headers(self):
        """Test OpenAI header generation"""
        headers = self.openai_adapter.get_headers("sk-test-key")
        
        self.assertIn("Authorization", headers)
        self.assertEqual(headers["Authorization"], "Bearer sk-test-key")
        self.assertIn("Content-Type", headers)
        self.assertEqual(headers["Content-Type"], "application/json")
    
    def test_anthropic_headers(self):
        """Test Anthropic header generation"""
        headers = self.anthropic_adapter.get_headers("sk-ant-test-key")
        
        self.assertIn("x-api-key", headers)
        self.assertEqual(headers["x-api-key"], "sk-ant-test-key")
        self.assertIn("anthropic-version", headers)
        self.assertEqual(headers["anthropic-version"], "2023-06-01")
        self.assertIn("Content-Type", headers)
        self.assertEqual(headers["Content-Type"], "application/json")
    
    def test_google_headers(self):
        """Test Google header generation (API key in URL, not header)"""
        headers = self.google_adapter.get_headers("AIza-test-key")
        
        # Google uses API key in URL, not in headers
        self.assertIn("Content-Type", headers)
        self.assertEqual(headers["Content-Type"], "application/json")
    
    def test_ollama_headers(self):
        """Test Ollama header generation (no authentication)"""
        headers = self.ollama_adapter.get_headers("")
        
        # Ollama doesn't require authentication
        self.assertIn("Content-Type", headers)
        self.assertEqual(headers["Content-Type"], "application/json")


if __name__ == "__main__":
    unittest.main()
