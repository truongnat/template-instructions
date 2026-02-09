"""
Model-related exception classes for the Multi-Agent Orchestration System
"""

from typing import Optional, Dict, Any
from .base import OrchestrationError


class ModelError(OrchestrationError):
    """Base class for model-related errors"""
    
    def __init__(
        self,
        message: str,
        model_name: Optional[str] = None,
        model_tier: Optional[str] = None,
        **kwargs
    ):
        context = kwargs.get("context", {})
        context.update({
            "model_name": model_name,
            "model_tier": model_tier
        })
        kwargs["context"] = context
        super().__init__(message, **kwargs)
        self.model_name = model_name
        self.model_tier = model_tier


class ModelConfigurationError(ModelError):
    """Raised when model configuration is invalid"""
    
    def __init__(
        self,
        message: str,
        configuration_issues: Optional[Dict[str, str]] = None,
        **kwargs
    ):
        context = kwargs.get("context", {})
        context.update({"configuration_issues": configuration_issues or {}})
        kwargs["context"] = context
        super().__init__(message, **kwargs)
        self.configuration_issues = configuration_issues or {}


class ModelAPIError(ModelError):
    """Raised when model API calls fail"""
    
    def __init__(
        self,
        message: str,
        api_provider: Optional[str] = None,
        status_code: Optional[int] = None,
        api_error_code: Optional[str] = None,
        **kwargs
    ):
        context = kwargs.get("context", {})
        context.update({
            "api_provider": api_provider,
            "status_code": status_code,
            "api_error_code": api_error_code
        })
        kwargs["context"] = context
        super().__init__(message, **kwargs)
        self.api_provider = api_provider
        self.status_code = status_code
        self.api_error_code = api_error_code


class ModelRateLimitError(ModelError):
    """Raised when model API rate limits are exceeded"""
    
    def __init__(
        self,
        message: str,
        retry_after_seconds: Optional[int] = None,
        requests_per_minute: Optional[int] = None,
        **kwargs
    ):
        context = kwargs.get("context", {})
        context.update({
            "retry_after_seconds": retry_after_seconds,
            "requests_per_minute": requests_per_minute
        })
        kwargs["context"] = context
        super().__init__(message, **kwargs)
        self.retry_after_seconds = retry_after_seconds
        self.requests_per_minute = requests_per_minute


class ModelTimeoutError(ModelError):
    """Raised when model API calls time out"""
    
    def __init__(
        self,
        message: str,
        timeout_seconds: Optional[int] = None,
        **kwargs
    ):
        context = kwargs.get("context", {})
        context.update({"timeout_seconds": timeout_seconds})
        kwargs["context"] = context
        super().__init__(message, **kwargs)
        self.timeout_seconds = timeout_seconds


class ModelNotAvailableError(ModelError):
    """Raised when a requested model is not available"""
    
    def __init__(
        self,
        message: str,
        available_models: Optional[list] = None,
        **kwargs
    ):
        context = kwargs.get("context", {})
        context.update({"available_models": available_models or []})
        kwargs["context"] = context
        super().__init__(message, **kwargs)
        self.available_models = available_models or []


class ModelResponseError(ModelError):
    """Raised when model response is invalid or malformed"""
    
    def __init__(
        self,
        message: str,
        response_data: Optional[str] = None,
        expected_format: Optional[str] = None,
        **kwargs
    ):
        context = kwargs.get("context", {})
        context.update({
            "response_data": response_data,
            "expected_format": expected_format
        })
        kwargs["context"] = context
        super().__init__(message, **kwargs)
        self.response_data = response_data
        self.expected_format = expected_format


class ModelOptimizationError(ModelError):
    """Raised when model optimization fails"""
    
    def __init__(
        self,
        message: str,
        optimization_strategy: Optional[str] = None,
        failed_constraints: Optional[list] = None,
        **kwargs
    ):
        context = kwargs.get("context", {})
        context.update({
            "optimization_strategy": optimization_strategy,
            "failed_constraints": failed_constraints or []
        })
        kwargs["context"] = context
        super().__init__(message, **kwargs)
        self.optimization_strategy = optimization_strategy
        self.failed_constraints = failed_constraints or []


class InsufficientResourcesError(ModelError):
    """Raised when insufficient resources are available for model execution"""
    
    def __init__(
        self,
        message: str,
        required_resources: Optional[Dict[str, Any]] = None,
        available_resources: Optional[Dict[str, Any]] = None,
        **kwargs
    ):
        context = kwargs.get("context", {})
        context.update({
            "required_resources": required_resources or {},
            "available_resources": available_resources or {}
        })
        kwargs["context"] = context
        super().__init__(message, **kwargs)
        self.required_resources = required_resources or {}
        self.available_resources = available_resources or {}


class InvalidModelAssignmentError(ModelError):
    """Raised when model assignment is invalid or not found"""
    
    def __init__(
        self,
        message: str,
        agent_type: Optional[str] = None,
        available_assignments: Optional[list] = None,
        **kwargs
    ):
        context = kwargs.get("context", {})
        context.update({
            "agent_type": agent_type,
            "available_assignments": available_assignments or []
        })
        kwargs["context"] = context
        super().__init__(message, **kwargs)
        self.agent_type = agent_type
        self.available_assignments = available_assignments or []