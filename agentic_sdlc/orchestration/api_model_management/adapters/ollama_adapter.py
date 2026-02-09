"""
Ollama provider adapter for API Model Management system.

This module implements the Ollama-specific adapter for communicating with
local Ollama models.
"""

import httpx
import time
from typing import Any, Dict
from .base import ProviderAdapter
from ..models import ModelRequest, ModelResponse, TokenUsage
from ..exceptions import (
    ProviderError,
    RateLimitError,
    AuthenticationError,
    InvalidRequestError
)


class OllamaAdapter(ProviderAdapter):
    """
    Adapter for Ollama local models.
    
    Handles request formatting, response parsing, and error handling specific
    to Ollama's API format. Note that Ollama runs locally and doesn't require
    API keys or have rate limits.
    """
    
    def __init__(self, base_url: str = "http://localhost:11434"):
        """
        Initialize Ollama adapter.
        
        Args:
            base_url: Base URL for Ollama API (default: http://localhost:11434)
        """
        super().__init__("ollama")
        self.base_url = base_url.rstrip("/")
        self.client = httpx.AsyncClient(timeout=120.0)  # Longer timeout for local models
    
    async def send_request(
        self,
        model_id: str,
        request: ModelRequest,
        api_key: str
    ) -> ModelResponse:
        """
        Send request to Ollama API.
        
        Args:
            model_id: Ollama model identifier (e.g., "llama2", "mistral")
            request: Normalized model request
            api_key: Not used for Ollama (local models don't require auth)
            
        Returns:
            ModelResponse: Normalized response
            
        Raises:
            ProviderError: If API request fails
        """
        start_time = time.time()
        
        try:
            # Format request body
            body = self.format_request_body(model_id, request)
            
            # Get headers (no authentication needed for local Ollama)
            headers = {"Content-Type": "application/json"}
            
            # Send request
            response = await self.client.post(
                f"{self.base_url}/api/generate",
                json=body,
                headers=headers
            )
            
            # Calculate latency
            latency_ms = (time.time() - start_time) * 1000
            
            # Handle errors
            if response.status_code != 200:
                await self._handle_error(response, model_id, request.task_id)
            
            # Parse response
            raw_response = response.json()
            model_response = self.parse_response(raw_response)
            
            # Update latency
            model_response.latency_ms = latency_ms
            model_response.model_id = model_id
            
            return model_response
            
        except httpx.TimeoutException as e:
            raise ProviderError(
                f"Request timeout for model {model_id}",
                provider=self.provider_name,
                model_id=model_id,
                is_retryable=True,
                task_id=request.task_id
            ) from e
        except httpx.RequestError as e:
            raise ProviderError(
                f"Network error for model {model_id}: {str(e)}",
                provider=self.provider_name,
                model_id=model_id,
                is_retryable=True,
                task_id=request.task_id
            ) from e
    
    def format_request_body(self, model_id: str, request: ModelRequest) -> Dict[str, Any]:
        """
        Format request body for Ollama API.
        
        Args:
            model_id: Ollama model identifier
            request: Normalized model request
            
        Returns:
            Dict[str, Any]: Ollama-formatted request body
        """
        body = {
            "model": model_id,
            "prompt": request.prompt,
            "stream": False,  # We want the complete response, not streaming
            "options": {
                "temperature": request.temperature,
            }
        }
        
        # Add max_tokens if specified (Ollama calls it num_predict)
        if request.max_tokens:
            body["options"]["num_predict"] = request.max_tokens
        
        # Add any additional parameters to options
        for key, value in request.parameters.items():
            if key not in body["options"]:
                body["options"][key] = value
        
        return body
    
    def parse_response(self, raw_response: Any) -> ModelResponse:
        """
        Parse Ollama API response.
        
        Args:
            raw_response: Raw JSON response from Ollama API
            
        Returns:
            ModelResponse: Normalized response
            
        Raises:
            ProviderError: If response parsing fails
        """
        try:
            # Extract content
            content = raw_response.get("response", "")
            
            # Extract token usage (estimated for local models)
            token_usage = self.extract_token_usage(raw_response)
            
            # Create response (cost will be 0 for local models)
            return ModelResponse(
                content=content,
                model_id=raw_response.get("model", ""),
                token_usage=token_usage,
                latency_ms=0.0,  # Will be set by send_request
                cost=0.0,  # Local models have no cost
                metadata={
                    "done": raw_response.get("done"),
                    "context": raw_response.get("context", []),
                    "total_duration": raw_response.get("total_duration"),
                    "load_duration": raw_response.get("load_duration"),
                    "prompt_eval_count": raw_response.get("prompt_eval_count"),
                    "eval_count": raw_response.get("eval_count")
                }
            )
        except (KeyError, IndexError) as e:
            raise ProviderError(
                f"Failed to parse Ollama response: {str(e)}",
                provider=self.provider_name,
                model_id="",
                is_retryable=False
            ) from e
    
    def extract_token_usage(self, raw_response: Any) -> TokenUsage:
        """
        Extract token usage from Ollama response.
        
        Note: Ollama provides token counts but they are estimates.
        The API returns prompt_eval_count and eval_count.
        
        Args:
            raw_response: Raw JSON response from Ollama API
            
        Returns:
            TokenUsage: Token usage information (estimated)
        """
        try:
            # Ollama provides prompt_eval_count (input) and eval_count (output)
            input_tokens = raw_response.get("prompt_eval_count", 0)
            output_tokens = raw_response.get("eval_count", 0)
            
            return TokenUsage(
                input_tokens=input_tokens,
                output_tokens=output_tokens,
                total_tokens=input_tokens + output_tokens
            )
        except Exception:
            # If token counts are not available, estimate based on text length
            # Rough estimate: 1 token ≈ 4 characters
            prompt_length = len(raw_response.get("prompt", ""))
            response_length = len(raw_response.get("response", ""))
            
            input_tokens = prompt_length // 4
            output_tokens = response_length // 4
            
            return TokenUsage(
                input_tokens=input_tokens,
                output_tokens=output_tokens,
                total_tokens=input_tokens + output_tokens
            )
    
    def is_rate_limit_error(self, error: Exception) -> bool:
        """
        Check if error indicates rate limiting.
        
        Note: Ollama is a local service and doesn't have rate limits.
        
        Args:
            error: Exception from API request
            
        Returns:
            bool: Always False for Ollama (no rate limits)
        """
        # Ollama doesn't have rate limits since it's local
        return False
    
    async def _handle_error(
        self,
        response: httpx.Response,
        model_id: str,
        task_id: str
    ) -> None:
        """
        Handle error responses from Ollama API.
        
        Args:
            response: HTTP response object
            model_id: Model identifier
            task_id: Task identifier
            
        Raises:
            InvalidRequestError: If request is invalid
            ProviderError: For other errors
        """
        status_code = response.status_code
        
        try:
            error_data = response.json()
            error_message = error_data.get("error", "Unknown error")
        except Exception:
            error_message = response.text
        
        # Model not found
        if status_code == 404:
            raise ProviderError(
                f"Model {model_id} not found in Ollama. Make sure the model is pulled.",
                provider=self.provider_name,
                model_id=model_id,
                status_code=status_code,
                is_retryable=False,
                task_id=task_id
            )
        
        # Invalid request error
        if status_code == 400:
            raise InvalidRequestError(
                f"Invalid request for model {model_id}: {error_message}",
                model_id=model_id,
                task_id=task_id
            )
        
        # Server error (retryable)
        if 500 <= status_code < 600:
            raise ProviderError(
                f"Ollama server error for model {model_id}: {error_message}",
                provider=self.provider_name,
                model_id=model_id,
                status_code=status_code,
                is_retryable=True,
                task_id=task_id
            )
        
        # Other errors
        raise ProviderError(
            f"Ollama API error for model {model_id}: {error_message}",
            provider=self.provider_name,
            model_id=model_id,
            status_code=status_code,
            is_retryable=False,
            task_id=task_id
        )
    
    async def close(self):
        """Close the HTTP client."""
        await self.client.aclose()
