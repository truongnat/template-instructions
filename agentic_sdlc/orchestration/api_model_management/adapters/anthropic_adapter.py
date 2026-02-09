"""
Anthropic provider adapter for API Model Management system.

This module implements the Anthropic-specific adapter for communicating with
Anthropic's API (Claude models).
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


class AnthropicAdapter(ProviderAdapter):
    """
    Adapter for Anthropic API.
    
    Handles request formatting, response parsing, and error handling specific
    to Anthropic's API format (Claude models).
    """
    
    BASE_URL = "https://api.anthropic.com/v1"
    API_VERSION = "2023-06-01"
    
    def __init__(self):
        """Initialize Anthropic adapter."""
        super().__init__("anthropic")
        self.client = httpx.AsyncClient(timeout=60.0)
    
    async def send_request(
        self,
        model_id: str,
        request: ModelRequest,
        api_key: str
    ) -> ModelResponse:
        """
        Send request to Anthropic API.
        
        Args:
            model_id: Anthropic model identifier (e.g., "claude-3.5-sonnet")
            request: Normalized model request
            api_key: Anthropic API key
            
        Returns:
            ModelResponse: Normalized response
            
        Raises:
            ProviderError: If API request fails
            RateLimitError: If rate limit is exceeded
            AuthenticationError: If authentication fails
        """
        start_time = time.time()
        
        try:
            # Format request body
            body = self.format_request_body(model_id, request)
            
            # Get headers with authentication
            headers = self.get_headers(api_key)
            
            # Send request
            response = await self.client.post(
                f"{self.BASE_URL}/messages",
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
        Format request body for Anthropic API.
        
        Args:
            model_id: Anthropic model identifier
            request: Normalized model request
            
        Returns:
            Dict[str, Any]: Anthropic-formatted request body
        """
        body = {
            "model": model_id,
            "messages": [
                {"role": "user", "content": request.prompt}
            ],
            "max_tokens": request.max_tokens or 4096,  # Anthropic requires max_tokens
            "temperature": request.temperature,
        }
        
        # Add any additional parameters
        for key, value in request.parameters.items():
            if key not in body:
                body[key] = value
        
        return body
    
    def get_headers(self, api_key: str) -> Dict[str, str]:
        """
        Get headers for Anthropic API request.
        
        Args:
            api_key: Anthropic API key
            
        Returns:
            Dict[str, str]: HTTP headers
        """
        return {
            "x-api-key": api_key,
            "anthropic-version": self.API_VERSION,
            "Content-Type": "application/json"
        }
    
    def parse_response(self, raw_response: Any) -> ModelResponse:
        """
        Parse Anthropic API response.
        
        Args:
            raw_response: Raw JSON response from Anthropic API
            
        Returns:
            ModelResponse: Normalized response
            
        Raises:
            ProviderError: If response parsing fails
        """
        try:
            # Extract content from first content block
            content_blocks = raw_response["content"]
            content = ""
            
            # Concatenate all text content blocks
            for block in content_blocks:
                if block["type"] == "text":
                    content += block["text"]
            
            # Extract token usage
            token_usage = self.extract_token_usage(raw_response)
            
            # Create response (cost will be calculated by caller with model metadata)
            return ModelResponse(
                content=content,
                model_id=raw_response.get("model", ""),
                token_usage=token_usage,
                latency_ms=0.0,  # Will be set by send_request
                cost=0.0,  # Will be calculated by caller
                metadata={
                    "stop_reason": raw_response.get("stop_reason"),
                    "response_id": raw_response.get("id"),
                    "type": raw_response.get("type")
                }
            )
        except (KeyError, IndexError) as e:
            raise ProviderError(
                f"Failed to parse Anthropic response: {str(e)}",
                provider=self.provider_name,
                model_id="",
                is_retryable=False
            ) from e
    
    def extract_token_usage(self, raw_response: Any) -> TokenUsage:
        """
        Extract token usage from Anthropic response.
        
        Args:
            raw_response: Raw JSON response from Anthropic API
            
        Returns:
            TokenUsage: Token usage information
            
        Raises:
            ProviderError: If token usage extraction fails
        """
        try:
            usage = raw_response["usage"]
            input_tokens = usage["input_tokens"]
            output_tokens = usage["output_tokens"]
            
            return TokenUsage(
                input_tokens=input_tokens,
                output_tokens=output_tokens,
                total_tokens=input_tokens + output_tokens
            )
        except KeyError as e:
            raise ProviderError(
                f"Failed to extract token usage from Anthropic response: {str(e)}",
                provider=self.provider_name,
                model_id="",
                is_retryable=False
            ) from e
    
    def is_rate_limit_error(self, error: Exception) -> bool:
        """
        Check if error indicates rate limiting.
        
        Args:
            error: Exception from API request
            
        Returns:
            bool: True if error indicates rate limiting
        """
        if isinstance(error, RateLimitError):
            return True
        
        if isinstance(error, ProviderError):
            return error.status_code == 429
        
        return False
    
    async def _handle_error(
        self,
        response: httpx.Response,
        model_id: str,
        task_id: str
    ) -> None:
        """
        Handle error responses from Anthropic API.
        
        Args:
            response: HTTP response object
            model_id: Model identifier
            task_id: Task identifier
            
        Raises:
            RateLimitError: If rate limit is exceeded
            AuthenticationError: If authentication fails
            InvalidRequestError: If request is invalid
            ProviderError: For other errors
        """
        status_code = response.status_code
        
        try:
            error_data = response.json()
            error_message = error_data.get("error", {}).get("message", "Unknown error")
            error_type = error_data.get("error", {}).get("type", "unknown")
        except Exception:
            error_message = response.text
            error_type = "unknown"
        
        # Rate limit error
        if status_code == 429:
            retry_after = response.headers.get("retry-after")
            raise RateLimitError(
                f"Rate limit exceeded for model {model_id}: {error_message}",
                model_id=model_id,
                retry_after=int(retry_after) if retry_after else None,
                task_id=task_id
            )
        
        # Authentication error
        if status_code == 401:
            raise AuthenticationError(
                f"Authentication failed for Anthropic: {error_message}",
                provider=self.provider_name,
                model_id=model_id,
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
                f"Anthropic server error for model {model_id}: {error_message}",
                provider=self.provider_name,
                model_id=model_id,
                status_code=status_code,
                error_code=error_type,
                is_retryable=True,
                task_id=task_id
            )
        
        # Other errors
        raise ProviderError(
            f"Anthropic API error for model {model_id}: {error_message}",
            provider=self.provider_name,
            model_id=model_id,
            status_code=status_code,
            error_code=error_type,
            is_retryable=False,
            task_id=task_id
        )
    
    async def close(self):
        """Close the HTTP client."""
        await self.client.aclose()
