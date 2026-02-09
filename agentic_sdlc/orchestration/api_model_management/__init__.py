"""
API-Based Model Selection & Rate Limit Management

This package provides intelligent model selection, real-time availability checking,
automatic failover, response quality evaluation, and comprehensive cost tracking
for API-based AI model connections.
"""

from .models import (
    ModelMetadata,
    RateLimits,
    ModelSelection,
    SelectionConstraints,
    HealthStatus,
    ModelAvailability,
    RateLimitStatus,
    FailoverReason,
    ModelRequest,
    TokenUsage,
    ModelResponse,
    QualityScore,
    CachedResponse,
    BudgetStatus,
    PerformanceMetrics,
    PerformanceDegradation,
    ErrorResponse,
)

from .exceptions import (
    APIModelError,
    RateLimitError,
    FailoverError,
    ModelUnavailableError,
    ConfigurationError,
    AuthenticationError,
    InvalidRequestError,
    ProviderError,
    CacheError,
    BudgetExceededError,
    QualityThresholdError,
)

from .failover_manager import FailoverManager
from .graceful_degradation import (
    GracefulDegradationManager,
    DegradationMode,
    DegradationStatus,
    QueuedRequest,
)

__all__ = [
    # Data Models
    "ModelMetadata",
    "RateLimits",
    "ModelSelection",
    "SelectionConstraints",
    "HealthStatus",
    "ModelAvailability",
    "RateLimitStatus",
    "FailoverReason",
    "ModelRequest",
    "TokenUsage",
    "ModelResponse",
    "QualityScore",
    "CachedResponse",
    "BudgetStatus",
    "PerformanceMetrics",
    "PerformanceDegradation",
    "ErrorResponse",
    # Exceptions
    "APIModelError",
    "RateLimitError",
    "FailoverError",
    "ModelUnavailableError",
    "ConfigurationError",
    "AuthenticationError",
    "InvalidRequestError",
    "ProviderError",
    "CacheError",
    "BudgetExceededError",
    "QualityThresholdError",
    # Components
    "FailoverManager",
    "GracefulDegradationManager",
    "DegradationMode",
    "DegradationStatus",
    "QueuedRequest",
]
