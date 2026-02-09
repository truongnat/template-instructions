"""
Custom exceptions for API Model Management system.

This module defines all custom exceptions used throughout the API Model Management
system for error handling and categorization.
"""

from typing import Optional, List, Dict, Any


class APIModelError(Exception):
    """Base exception for all API Model Management errors."""
    
    def __init__(
        self,
        message: str,
        model_id: Optional[str] = None,
        task_id: Optional[str] = None,
        is_retryable: bool = False,
        details: Optional[Dict[str, Any]] = None
    ):
        super().__init__(message)
        self.message = message
        self.model_id = model_id
        self.task_id = task_id
        self.is_retryable = is_retryable
        self.details = details or {}


class RateLimitError(APIModelError):
    """Raised when a model's rate limit is exceeded."""
    
    def __init__(
        self,
        message: str,
        model_id: str,
        reset_time: Optional[float] = None,
        retry_after: Optional[int] = None,
        **kwargs
    ):
        super().__init__(message, model_id=model_id, is_retryable=True, **kwargs)
        self.reset_time = reset_time
        self.retry_after = retry_after


class FailoverError(APIModelError):
    """Raised when failover to an alternative model fails."""
    
    def __init__(
        self,
        message: str,
        original_model: str,
        attempted_models: List[str],
        failure_reasons: Dict[str, str],
        **kwargs
    ):
        super().__init__(message, model_id=original_model, is_retryable=False, **kwargs)
        self.original_model = original_model
        self.attempted_models = attempted_models
        self.failure_reasons = failure_reasons


class ModelUnavailableError(APIModelError):
    """Raised when a model is unavailable or unhealthy."""
    
    def __init__(
        self,
        message: str,
        model_id: str,
        consecutive_failures: int = 0,
        last_error: Optional[str] = None,
        **kwargs
    ):
        super().__init__(message, model_id=model_id, is_retryable=True, **kwargs)
        self.consecutive_failures = consecutive_failures
        self.last_error = last_error


class ConfigurationError(APIModelError):
    """Raised when configuration is invalid or missing."""
    
    def __init__(
        self,
        message: str,
        config_path: Optional[str] = None,
        validation_errors: Optional[List[str]] = None,
        **kwargs
    ):
        super().__init__(message, is_retryable=False, **kwargs)
        self.config_path = config_path
        self.validation_errors = validation_errors or []


class AuthenticationError(APIModelError):
    """Raised when API authentication fails."""
    
    def __init__(
        self,
        message: str,
        provider: str,
        model_id: Optional[str] = None,
        **kwargs
    ):
        super().__init__(message, model_id=model_id, is_retryable=False, **kwargs)
        self.provider = provider


class InvalidRequestError(APIModelError):
    """Raised when a request is invalid or malformed."""
    
    def __init__(
        self,
        message: str,
        model_id: Optional[str] = None,
        validation_errors: Optional[List[str]] = None,
        **kwargs
    ):
        super().__init__(message, model_id=model_id, is_retryable=False, **kwargs)
        self.validation_errors = validation_errors or []


class ProviderError(APIModelError):
    """Raised when a provider API returns an error."""
    
    def __init__(
        self,
        message: str,
        provider: str,
        model_id: str,
        status_code: Optional[int] = None,
        error_code: Optional[str] = None,
        is_retryable: bool = False,
        **kwargs
    ):
        super().__init__(message, model_id=model_id, is_retryable=is_retryable, **kwargs)
        self.provider = provider
        self.status_code = status_code
        self.error_code = error_code


class CacheError(APIModelError):
    """Raised when cache operations fail."""
    
    def __init__(
        self,
        message: str,
        cache_key: Optional[str] = None,
        operation: Optional[str] = None,
        **kwargs
    ):
        super().__init__(message, is_retryable=True, **kwargs)
        self.cache_key = cache_key
        self.operation = operation


class BudgetExceededError(APIModelError):
    """Raised when budget threshold is exceeded."""
    
    def __init__(
        self,
        message: str,
        daily_budget: float,
        current_spend: float,
        **kwargs
    ):
        super().__init__(message, is_retryable=False, **kwargs)
        self.daily_budget = daily_budget
        self.current_spend = current_spend
        self.utilization_percent = (current_spend / daily_budget * 100) if daily_budget > 0 else 0


class QualityThresholdError(APIModelError):
    """Raised when response quality falls below threshold."""
    
    def __init__(
        self,
        message: str,
        model_id: str,
        quality_score: float,
        threshold: float,
        **kwargs
    ):
        super().__init__(message, model_id=model_id, is_retryable=True, **kwargs)
        self.quality_score = quality_score
        self.threshold = threshold
