"""
API Client Manager for API Model Management system.

This module provides the APIClientManager class which handles HTTP connections,
request routing to provider adapters, retry logic with exponential backoff,
and error categorization.
"""

import asyncio
import logging
import time
from typing import Dict, Optional, Callable, Any
import httpx

from .models import ModelRequest, ModelResponse, ErrorResponse
from .exceptions import (
    APIModelError,
    ProviderError,
    RateLimitError,
    AuthenticationError,
    InvalidRequestError,
    ModelUnavailableError
)
from .adapters.base import ProviderAdapter
from .api_key_manager import APIKeyManager
from .registry import ModelRegistry


logger = logging.getLogger(__name__)


class APIClientManager:
    """
    Manages API connections and routes requests to provider-specific adapters.
    
    Features:
    - Connection pooling with httpx for efficient HTTP connections
    - Automatic retry logic with exponential backoff for transient errors
    - Error categorization (transient vs permanent)
    - Request routing to appropriate provider adapters
    - Comprehensive error logging and tracking
    
    The APIClientManager serves as the central point for all API communication,
    coordinating between the API Key Manager, Model Registry, and provider adapters.
    """
    
    def __init__(
        self,
        api_key_manager: APIKeyManager,
        registry: ModelRegistry,
        adapters: Dict[str, ProviderAdapter],
        max_retries: int = 3,
        base_backoff_seconds: float = 2.0,
        max_concurrent_requests: int = 100,
        max_concurrent_per_provider: Optional[Dict[str, int]] = None
    ):
        """
        Initialize API Client Manager.
        
        Args:
            api_key_manager: Manager for API keys and rotation
            registry: Model registry for metadata lookup
            adapters: Dictionary mapping provider names to adapter instances
            max_retries: Maximum number of retry attempts for transient errors
            base_backoff_seconds: Base delay for exponential backoff (2^n * base)
            max_concurrent_requests: Maximum concurrent requests across all providers
            max_concurrent_per_provider: Optional dict mapping provider names to their
                                        specific concurrency limits. If not provided,
                                        defaults to 10 per provider.
        """
        self.api_key_manager = api_key_manager
        self.registry = registry
        self.adapters = adapters
        self.max_retries = max_retries
        self.base_backoff_seconds = base_backoff_seconds
        
        # Global semaphore for limiting total concurrent requests
        self._global_semaphore = asyncio.Semaphore(max_concurrent_requests)
        
        # Per-provider semaphores for limiting concurrent requests per provider
        self._provider_semaphores: Dict[str, asyncio.Semaphore] = {}
        self._provider_limits: Dict[str, int] = {}
        
        # Initialize per-provider semaphores
        default_per_provider_limit = 10
        for provider in adapters.keys():
            limit = (max_concurrent_per_provider or {}).get(provider, default_per_provider_limit)
            self._provider_semaphores[provider] = asyncio.Semaphore(limit)
            self._provider_limits[provider] = limit
        
        # Track request statistics
        self._request_count = 0
        self._error_count = 0
        self._provider_request_counts: Dict[str, int] = {provider: 0 for provider in adapters.keys()}
        self._active_requests: Dict[str, int] = {provider: 0 for provider in adapters.keys()}
        
        logger.info(
            f"APIClientManager initialized with {len(adapters)} adapters, "
            f"max_retries={max_retries}, max_concurrent={max_concurrent_requests}, "
            f"per_provider_limits={self._provider_limits}"
        )
    
    async def send_request(
        self,
        model_id: str,
        request: ModelRequest
    ) -> ModelResponse:
        """
        Send request to model API without retry logic.
        
        This method performs a single request attempt without retries.
        Use send_request_with_retry for automatic retry handling.
        
        Implements non-blocking concurrent request processing with both global
        and per-provider concurrency limits. Requests acquire both semaphores
        to ensure neither limit is exceeded.
        
        Args:
            model_id: Model identifier (e.g., "gpt-4-turbo")
            request: Normalized model request
            
        Returns:
            ModelResponse: Normalized response with content, tokens, and cost
            
        Raises:
            ModelUnavailableError: If model metadata not found
            AuthenticationError: If API key is missing or invalid
            ProviderError: If provider API returns an error
            RateLimitError: If rate limit is exceeded
            InvalidRequestError: If request is malformed
        """
        # Get model metadata first to determine provider
        model_metadata = self.registry.get_model(model_id)
        if not model_metadata:
            raise ModelUnavailableError(
                f"Model not found in registry: {model_id}",
                model_id=model_id,
                task_id=request.task_id
            )
        
        provider = model_metadata.provider
        
        # Check if provider adapter exists before acquiring semaphores
        adapter = self.adapters.get(provider)
        if not adapter:
            raise ProviderError(
                f"No adapter found for provider: {provider}",
                provider=provider,
                model_id=model_id,
                is_retryable=False,
                task_id=request.task_id
            )
        
        # Acquire both global and provider-specific semaphores
        # This ensures we respect both total concurrency and per-provider limits
        async with self._global_semaphore:
            async with self._provider_semaphores[provider]:
                # Track active requests
                self._request_count += 1
                self._provider_request_counts[provider] += 1
                self._active_requests[provider] += 1
                
                try:
                    # Get API key
                    api_key = self.api_key_manager.get_key(provider)
                    if not api_key and provider != "ollama":  # Ollama doesn't need API key
                        raise AuthenticationError(
                            f"No API key available for provider: {provider}",
                            provider=provider,
                            model_id=model_id,
                            task_id=request.task_id
                        )
                    
                    # Log request
                    logger.info(
                        f"Sending request to model {model_id} (provider: {provider}, "
                        f"task: {request.task_id}, active_requests: {self._active_requests[provider]})"
                    )
                    
                    # Send request through adapter
                    response = await adapter.send_request(model_id, request, api_key or "")
                    
                    # Calculate cost using model metadata
                    cost = adapter.calculate_cost(
                        response.token_usage.input_tokens,
                        response.token_usage.output_tokens,
                        model_metadata.cost_per_1k_input_tokens,
                        model_metadata.cost_per_1k_output_tokens
                    )
                    response.cost = cost
                    
                    logger.info(
                        f"Request successful: model={model_id}, "
                        f"tokens={response.token_usage.total_tokens}, "
                        f"cost=${cost:.4f}, latency={response.latency_ms:.0f}ms"
                    )
                    
                    return response
                    
                except Exception as e:
                    self._error_count += 1
                    
                    # Log error with context
                    logger.error(
                        f"Request failed: model={model_id}, provider={provider}, "
                        f"task={request.task_id}, error={type(e).__name__}: {str(e)}"
                    )
                    
                    # Re-raise the exception
                    raise
                    
                finally:
                    # Decrement active request count
                    self._active_requests[provider] -= 1
    
    async def send_request_with_retry(
        self,
        model_id: str,
        request: ModelRequest,
        max_retries: Optional[int] = None
    ) -> ModelResponse:
        """
        Send request with automatic retry logic for transient errors.
        
        This method implements exponential backoff retry logic for transient errors
        such as network timeouts, 5xx server errors, and temporary rate limits.
        Permanent errors (4xx except 429, authentication failures) are not retried.
        
        Retry delays follow exponential backoff: 2^n * base_backoff_seconds
        - Attempt 1: immediate
        - Attempt 2: 2 seconds delay
        - Attempt 3: 4 seconds delay
        - Attempt 4: 8 seconds delay
        
        Args:
            model_id: Model identifier
            request: Normalized model request
            max_retries: Maximum retry attempts (overrides default if provided)
            
        Returns:
            ModelResponse: Normalized response
            
        Raises:
            ProviderError: If all retry attempts fail
            AuthenticationError: If authentication fails (not retried)
            InvalidRequestError: If request is invalid (not retried)
            ModelUnavailableError: If model not found (not retried)
        """
        max_attempts = (max_retries if max_retries is not None else self.max_retries) + 1
        last_error: Optional[Exception] = None
        
        for attempt in range(max_attempts):
            try:
                # Attempt request
                response = await self.send_request(model_id, request)
                
                # Log retry success if this wasn't the first attempt
                if attempt > 0:
                    logger.info(
                        f"Request succeeded after {attempt} retries: "
                        f"model={model_id}, task={request.task_id}"
                    )
                
                return response
                
            except Exception as e:
                last_error = e
                
                # Check if error is retryable
                is_retryable = self._is_retryable_error(e)
                
                # Don't retry permanent errors
                if not is_retryable:
                    logger.warning(
                        f"Permanent error, not retrying: model={model_id}, "
                        f"error={type(e).__name__}"
                    )
                    raise
                
                # Check if we have retries left
                if attempt >= max_attempts - 1:
                    logger.error(
                        f"Max retries ({max_retries}) exceeded for model {model_id}, "
                        f"task={request.task_id}"
                    )
                    break
                
                # Calculate backoff delay
                delay = self._calculate_backoff(attempt)
                
                logger.warning(
                    f"Transient error on attempt {attempt + 1}/{max_attempts}, "
                    f"retrying in {delay:.1f}s: model={model_id}, "
                    f"error={type(e).__name__}: {str(e)}"
                )
                
                # Wait before retry
                await asyncio.sleep(delay)
        
        # All retries exhausted, raise final error with details
        error_message = (
            f"Request failed after {max_attempts} attempts for model {model_id}: "
            f"{type(last_error).__name__}: {str(last_error)}"
        )
        
        raise ProviderError(
            error_message,
            provider=self.registry.get_model(model_id).provider if self.registry.get_model(model_id) else "unknown",
            model_id=model_id,
            is_retryable=False,
            task_id=request.task_id
        ) from last_error
    
    def _is_retryable_error(self, error: Exception) -> bool:
        """
        Determine if an error is retryable (transient) or permanent.
        
        Transient errors (retryable):
        - Network timeouts
        - HTTP 5xx errors (server errors)
        - Connection failures
        - Temporary rate limits (some 429 errors)
        
        Permanent errors (not retryable):
        - HTTP 4xx errors (except 429)
        - Authentication failures (401, 403)
        - Invalid request format (400)
        - Model not found (404)
        - Model unavailable (registry lookup failure)
        
        Args:
            error: Exception raised during request
            
        Returns:
            bool: True if error is retryable, False otherwise
        """
        # Check if error has is_retryable attribute
        if isinstance(error, APIModelError):
            # Special case: ModelUnavailableError from registry lookup is not retryable
            # (model doesn't exist in registry), but ModelUnavailableError from health
            # checks might be retryable
            if isinstance(error, ModelUnavailableError):
                # If it's a registry lookup failure, it's not retryable
                return False
            return error.is_retryable
        
        # Authentication errors are not retryable
        if isinstance(error, AuthenticationError):
            return False
        
        # Invalid request errors are not retryable
        if isinstance(error, InvalidRequestError):
            return False
        
        # Rate limit errors are retryable
        if isinstance(error, RateLimitError):
            return True
        
        # Provider errors - check status code
        if isinstance(error, ProviderError):
            # 5xx errors are retryable
            if error.status_code and 500 <= error.status_code < 600:
                return True
            # 429 (rate limit) is retryable
            if error.status_code == 429:
                return True
            # Other errors are not retryable
            return False
        
        # Network errors (httpx exceptions) are retryable
        if isinstance(error, (httpx.TimeoutException, httpx.NetworkError, httpx.ConnectError)):
            return True
        
        # Unknown errors are not retryable by default
        return False
    
    def _calculate_backoff(self, attempt: int) -> float:
        """
        Calculate exponential backoff delay.
        
        Formula: 2^attempt * base_backoff_seconds
        - Attempt 0: 2^0 * 2 = 2 seconds
        - Attempt 1: 2^1 * 2 = 4 seconds
        - Attempt 2: 2^2 * 2 = 8 seconds
        
        Args:
            attempt: Current attempt number (0-indexed)
            
        Returns:
            float: Delay in seconds
        """
        return (2 ** attempt) * self.base_backoff_seconds
    
    def get_statistics(self) -> Dict[str, Any]:
        """
        Get request statistics including concurrency metrics.
        
        Returns:
            Dictionary with request counts, error counts, and concurrency stats
        """
        return {
            "request_count": self._request_count,
            "error_count": self._error_count,
            "success_count": self._request_count - self._error_count,
            "provider_request_counts": self._provider_request_counts.copy(),
            "active_requests_by_provider": self._active_requests.copy(),
            "provider_limits": self._provider_limits.copy()
        }
    
    def get_concurrency_status(self) -> Dict[str, Any]:
        """
        Get current concurrency status for monitoring.
        
        Returns:
            Dictionary with active request counts and limits per provider
        """
        return {
            "global_limit": self._global_semaphore._value,
            "providers": {
                provider: {
                    "active_requests": self._active_requests[provider],
                    "limit": self._provider_limits[provider],
                    "available_slots": self._provider_semaphores[provider]._value
                }
                for provider in self.adapters.keys()
            }
        }
    
    async def close(self):
        """
        Close all adapter connections.
        
        This should be called when shutting down to properly close
        HTTP clients and release resources.
        """
        logger.info("Closing APIClientManager and all adapters")
        
        for provider, adapter in self.adapters.items():
            try:
                if hasattr(adapter, 'close'):
                    await adapter.close()
                    logger.debug(f"Closed adapter for provider: {provider}")
            except Exception as e:
                logger.error(f"Error closing adapter for {provider}: {e}")
