"""
Base provider adapter interface for API Model Management system.

This module defines the abstract base class that all provider-specific adapters
must implement to ensure consistent request/response handling across providers.
"""

from abc import ABC, abstractmethod
from typing import Any, Dict
from ..models import ModelRequest, ModelResponse, TokenUsage
from ..exceptions import ProviderError


class ProviderAdapter(ABC):
    """
    Abstract base class for provider-specific API adapters.
    
    All provider adapters must implement this interface to ensure consistent
    request formatting, response parsing, and error handling across different
    AI model providers.
    """
    
    def __init__(self, provider_name: str):
        """
        Initialize the provider adapter.
        
        Args:
            provider_name: Name of the provider (e.g., "openai", "anthropic")
        """
        self.provider_name = provider_name
    
    @abstractmethod
    async def send_request(
        self,
        model_id: str,
        request: ModelRequest,
        api_key: str
    ) -> ModelResponse:
        """
        Send a request to the provider's API and return a normalized response.
        
        This method handles the complete request/response cycle including:
        - Formatting the request according to provider specifications
        - Sending the HTTP request with authentication
        - Parsing the provider-specific response
        - Normalizing the response to ModelResponse format
        - Extracting token usage and calculating cost
        
        Args:
            model_id: The provider-specific model identifier
            request: The normalized model request
            api_key: API key for authentication
            
        Returns:
            ModelResponse: Normalized response with content, token usage, and cost
            
        Raises:
            ProviderError: If the API request fails
            AuthenticationError: If authentication fails
            RateLimitError: If rate limit is exceeded
            InvalidRequestError: If the request is malformed
        """
        pass
    
    @abstractmethod
    def parse_response(self, raw_response: Any) -> ModelResponse:
        """
        Parse provider-specific response format into normalized ModelResponse.
        
        This method extracts the response content, token usage, and metadata
        from the provider's response format and converts it to the standard
        ModelResponse format used throughout the system.
        
        Args:
            raw_response: The raw response object from the provider's API
            
        Returns:
            ModelResponse: Normalized response object
            
        Raises:
            ProviderError: If response parsing fails
        """
        pass
    
    @abstractmethod
    def extract_token_usage(self, raw_response: Any) -> TokenUsage:
        """
        Extract token usage information from provider-specific response.
        
        Different providers return token usage in different formats. This method
        normalizes the token usage data into the standard TokenUsage format.
        
        Args:
            raw_response: The raw response object from the provider's API
            
        Returns:
            TokenUsage: Normalized token usage with input, output, and total tokens
            
        Raises:
            ProviderError: If token usage extraction fails
        """
        pass
    
    @abstractmethod
    def is_rate_limit_error(self, error: Exception) -> bool:
        """
        Determine if an error indicates rate limiting.
        
        Different providers use different error codes and formats to indicate
        rate limiting. This method checks if a given error represents a rate
        limit condition.
        
        Args:
            error: The exception raised during API request
            
        Returns:
            bool: True if the error indicates rate limiting, False otherwise
        """
        pass
    
    def format_request_body(self, model_id: str, request: ModelRequest) -> Dict[str, Any]:
        """
        Format the request body according to provider specifications.
        
        This is a helper method that can be overridden by subclasses to format
        the request body in the provider-specific format.
        
        Args:
            model_id: The provider-specific model identifier
            request: The normalized model request
            
        Returns:
            Dict[str, Any]: Provider-specific request body
        """
        # Default implementation - subclasses should override
        return {
            "model": model_id,
            "prompt": request.prompt,
            "temperature": request.temperature,
            "max_tokens": request.max_tokens,
            **request.parameters
        }
    
    def get_headers(self, api_key: str) -> Dict[str, str]:
        """
        Get HTTP headers for API request including authentication.
        
        This is a helper method that can be overridden by subclasses to provide
        provider-specific headers.
        
        Args:
            api_key: API key for authentication
            
        Returns:
            Dict[str, str]: HTTP headers
        """
        # Default implementation - subclasses should override
        return {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
    
    def calculate_cost(
        self,
        input_tokens: int,
        output_tokens: int,
        cost_per_1k_input: float,
        cost_per_1k_output: float
    ) -> float:
        """
        Calculate the cost of a request based on token usage.
        
        Args:
            input_tokens: Number of input tokens
            output_tokens: Number of output tokens
            cost_per_1k_input: Cost per 1000 input tokens
            cost_per_1k_output: Cost per 1000 output tokens
            
        Returns:
            float: Total cost in dollars
        """
        input_cost = (input_tokens / 1000.0) * cost_per_1k_input
        output_cost = (output_tokens / 1000.0) * cost_per_1k_output
        return input_cost + output_cost
