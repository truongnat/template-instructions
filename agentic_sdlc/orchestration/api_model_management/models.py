"""
Data models for API Model Management system.

This module defines all data structures used throughout the API Model Management
system including model metadata, requests, responses, and monitoring data.
"""

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Optional, List, Dict, Any


@dataclass
class RateLimits:
    """Rate limit configuration for a model."""
    requests_per_minute: int
    tokens_per_minute: int


@dataclass
class ModelMetadata:
    """Metadata for an AI model."""
    id: str
    provider: str
    name: str
    capabilities: List[str]
    cost_per_1k_input_tokens: float
    cost_per_1k_output_tokens: float
    rate_limits: RateLimits
    context_window: int
    average_response_time_ms: float
    enabled: bool = True


@dataclass
class SelectionConstraints:
    """Constraints for model selection."""
    max_cost_per_request: Optional[float] = None
    required_capabilities: List[str] = field(default_factory=list)
    excluded_providers: List[str] = field(default_factory=list)
    max_latency_ms: Optional[float] = None


@dataclass
class ModelSelection:
    """Result of model selection."""
    model_id: str
    model_metadata: ModelMetadata
    suitability_score: float
    alternatives: List[str]
    selection_reason: str


@dataclass
class HealthStatus:
    """Health check result for a model."""
    model_id: str
    is_available: bool
    response_time_ms: float
    last_check: datetime
    consecutive_failures: int
    error_message: Optional[str] = None


@dataclass
class ModelAvailability:
    """Model availability status."""
    model_id: str
    is_available: bool
    is_rate_limited: bool
    last_successful_request: Optional[datetime]
    next_retry_time: Optional[datetime]


@dataclass
class RateLimitStatus:
    """Rate limit status for a model."""
    model_id: str
    is_limited: bool
    requests_remaining: int
    tokens_remaining: int
    reset_time: Optional[datetime]


class FailoverReason(Enum):
    """Reasons for failover to alternative model."""
    UNAVAILABLE = "unavailable"
    RATE_LIMITED = "rate_limited"
    ERROR = "error"
    LOW_QUALITY = "low_quality"
    TIMEOUT = "timeout"


@dataclass
class ModelRequest:
    """Request to AI model."""
    prompt: str
    parameters: Dict[str, Any]
    task_id: str
    agent_type: str
    max_tokens: Optional[int] = None
    temperature: float = 0.7


@dataclass
class TokenUsage:
    """Token usage information from API response."""
    input_tokens: int
    output_tokens: int
    total_tokens: int


@dataclass
class ModelResponse:
    """Response from AI model."""
    content: str
    model_id: str
    token_usage: TokenUsage
    latency_ms: float
    cost: float
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class QualityScore:
    """Response quality evaluation metrics."""
    overall_score: float
    completeness: float
    relevance: float
    coherence: float
    timestamp: datetime = field(default_factory=datetime.now)


@dataclass
class CachedResponse:
    """Cached model response with metadata."""
    cache_key: str
    response: ModelResponse
    cached_at: datetime
    expires_at: datetime
    hit_count: int = 0


@dataclass
class BudgetStatus:
    """Budget utilization status."""
    daily_budget: float
    current_spend: float
    utilization_percent: float
    is_over_budget: bool
    remaining_budget: float


@dataclass
class PerformanceMetrics:
    """Performance metrics for a model over a time window."""
    model_id: str
    window_hours: int
    total_requests: int
    successful_requests: int
    failed_requests: int
    success_rate: float
    average_latency_ms: float
    p50_latency_ms: float
    p95_latency_ms: float
    p99_latency_ms: float
    average_quality_score: float


@dataclass
class PerformanceDegradation:
    """Performance degradation alert."""
    model_id: str
    metric: str
    current_value: float
    threshold: float
    detected_at: datetime


@dataclass
class ErrorResponse:
    """Standardized error response."""
    error_type: str
    error_message: str
    model_id: str
    task_id: str
    is_retryable: bool
    attempted_models: List[str]
    failure_reasons: Dict[str, str]
    timestamp: datetime
