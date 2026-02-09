"""
Google provider adapter for API Model Management system.

This module implements the Google-specific adapter for communicating with
Google's Generative AI API (Gemini models).
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


class GoogleAdapter(ProviderAdapter):
    """
    Adapter for Google Generative AI API.
    
    Handles request formatting, response parsing, and error handling specific
    to Google's API format (Gemini models).
    """
    
    BASE_URL = "https://generativelanguage.googleapis.com/v1beta"
    
    def __init__(self):
        """Initialize Google adapter."""
        super().__init__("google")
        self.client = httpx.AsyncClient(timeout=60.0)
    
    async def send_request(
        self,
        model_id: str,
        request: ModelRequest,
        api_key: str
    ) -> ModelResponse:
        """
        Send request to Google Generative AI API.
        
        Args:
            model_id: Google model identifier (e.g., "gemini-pro")
            request: Normalized model request
            api_key: Google API key
            
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
            
            # Build URL with API key (Google uses query parameter for auth)
            url = f"{self.BASE_URL}/models/{model_id}:generateContent?key={api_key}"
            
            # Get headers
            headers = {"Content-Type": "application/json"}
            
            # Send request
            response = await self.client.post(
                url,
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
        Format request body for Google Generative AI API.
        
        Args:
            model_id: Google model identifier
            request: Normalized model request
            
        Returns:
            Dict[str, Any]: Google-formatted request body
        """
        body = {
            "contents": [
                {
                    "parts": [
                        {"text": request.prompt}
                    ]
                }
            ],
            "generationConfig": {
                "temperature": request.temperature,
            }
        }
        
        # Add max_tokens if specified (Google calls it maxOutputTokens)
        if request.max_tokens:
            body["generationConfig"]["maxOutputTokens"] = request.max_tokens
        
        # Add any additional parameters to generationConfig
        for key, value in request.parameters.items():
            if key not in body["generationConfig"]:
                body["generationConfig"][key] = value
        
        return body
    
    def parse_response(self, raw_response: Any) -> ModelResponse:
        """
        Parse Google Generative AI API response.
        
        Args:
            raw_response: Raw JSON response from Google API
            
        Returns:
            ModelResponse: Normalized response
            
        Raises:
            ProviderError: If response parsing fails
        """
        try:
            # Extract content from first candidate
            candidates = raw_response.get("candidates", [])
            if not candidates:
                raise ProviderError(
                    "No candidates in Google API response",
                    provider=self.provider_name,
                    model_id="",
                    is_retryable=False
                )
            
            candidate = candidates[0]
            content_parts = candidate.get("content", {}).get("parts", [])
            
            # Concatenate all text parts
            content = ""
            for part in content_parts:
                if "text" in part:
                    content += part["text"]
            
            # Extract token usage
            token_usage = self.extract_token_usage(raw_response)
            
            # Create response (cost will be calculated by caller with model metadata)
            return ModelResponse(
                content=content,
                model_id="",  # Will be set by send_request
                token_usage=token_usage,
                latency_ms=0.0,  # Will be set by send_request
                cost=0.0,  # Will be calculated by caller
                metadata={
                    "finish_reason": candidate.get("finishReason"),
                    "safety_ratings": candidate.get("safetyRatings", [])
                }
            )
        except (KeyError, IndexError) as e:
            raise ProviderError(
                f"Failed to parse Google response: {str(e)}",
                provider=self.provider_name,
                model_id="",
                is_retryable=False
            ) from e
    
    def extract_token_usage(self, raw_response: Any) -> TokenUsage:
        """
        Extract token usage from Google response.
        
        Args:
            raw_response: Raw JSON response from Google API
            
        Returns:
            TokenUsage: Token usage information
            
        Raises:
            ProviderError: If token usage extraction fails
        """
        try:
            usage_metadata = raw_response.get("usageMetadata", {})
            
            # Google provides promptTokenCount and candidatesTokenCount
            input_tokens = usage_metadata.get("promptTokenCount", 0)
            output_tokens = usage_metadata.get("candidatesTokenCount", 0)
            total_tokens = usage_metadata.get("totalTokenCount", input_tokens + output_tokens)
            
            return TokenUsage(
                input_tokens=input_tokens,
                output_tokens=output_tokens,
                total_tokens=total_tokens
            )
        except Exception as e:
            # If token usage is not available, return zeros
            # Google API may not always provide token counts
            return TokenUsage(
                input_tokens=0,
                output_tokens=0,
                total_tokens=0
            )
    
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
        Handle error responses from Google API.
        
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
            error_code = error_data.get("error", {}).get("code", "unknown")
        except Exception:
            error_message = response.text
            error_code = "unknown"
        
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
        if status_code in (401, 403):
            raise AuthenticationError(
                f"Authentication failed for Google: {error_message}",
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
                f"Google server error for model {model_id}: {error_message}",
                provider=self.provider_name,
                model_id=model_id,
                status_code=status_code,
                error_code=str(error_code),
                is_retryable=True,
                task_id=task_id
            )
        
        # Other errors
        raise ProviderError(
            f"Google API error for model {model_id}: {error_message}",
            provider=self.provider_name,
            model_id=model_id,
            status_code=status_code,
            error_code=str(error_code),
            is_retryable=False,
            task_id=task_id
        )
    
    async def close(self):
        """Close the HTTP client."""
        await self.client.aclose()
