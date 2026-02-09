"""
Error handling and logging utilities for API Model Management system.

This module provides comprehensive error categorization, logging, and event tracking
for all components in the API Model Management system. It implements Requirements 15.1-15.5.
"""

import logging
import traceback
from datetime import datetime
from enum import Enum
from typing import Optional, Dict, Any, List
from dataclasses import dataclass, field

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
    QualityThresholdError
)
from .models import ErrorResponse


class ErrorCategory(Enum):
    """Error categories for classification."""
    TRANSIENT = "transient"  # Retryable errors
    PERMANENT = "permanent"  # Non-retryable errors
    RATE_LIMIT = "rate_limit"  # Rate limiting errors
    AUTHENTICATION = "authentication"  # Auth failures
    CONFIGURATION = "configuration"  # Config errors
    VALIDATION = "validation"  # Input validation errors


class EventType(Enum):
    """Types of events to log."""
    RATE_LIMIT = "rate_limit"
    FAILOVER = "failover"
    PERFORMANCE_ALERT = "performance_alert"
    BUDGET_ALERT = "budget_alert"
    HEALTH_CHECK = "health_check"
    QUALITY_ALERT = "quality_alert"
    DEGRADED_MODE = "degraded_mode"
    RECOVERY = "recovery"


@dataclass
class ErrorContext:
    """Context information for error logging."""
    model_id: Optional[str] = None
    task_id: Optional[str] = None
    agent_type: Optional[str] = None
    provider: Optional[str] = None
    request_details: Optional[Dict[str, Any]] = None
    additional_context: Dict[str, Any] = field(default_factory=dict)


@dataclass
class EventLog:
    """Structured event log entry."""
    event_type: EventType
    timestamp: datetime
    message: str
    model_id: Optional[str] = None
    task_id: Optional[str] = None
    details: Dict[str, Any] = field(default_factory=dict)
    severity: str = "INFO"


class ErrorHandler:
    """
    Centralized error handling and logging for API Model Management.
    
    Features:
    - Error categorization (transient vs permanent)
    - Detailed error logging with context
    - Event logging (rate limits, failover, alerts)
    - Configurable log levels
    - Structured error responses
    
    Requirements:
    - 15.1: Error logging with context
    - 15.2: Error categorization
    - 15.3: Permanent error detail reporting
    - 15.4: Event logging coverage
    - 15.5: Configurable log levels
    """
    
    def __init__(self, log_level: str = "INFO"):
        """
        Initialize error handler.
        
        Args:
            log_level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        """
        self.logger = logging.getLogger("api_model_management")
        self._configure_logging(log_level)
        
        # Event log storage (in-memory for recent events)
        self._recent_events: List[EventLog] = []
        self._max_recent_events = 1000
        
        self.logger.info(f"ErrorHandler initialized with log level: {log_level}")
    
    def _configure_logging(self, log_level: str) -> None:
        """
        Configure logging with specified level.
        
        Args:
            log_level: Logging level string
        """
        # Convert string to logging level
        level = getattr(logging, log_level.upper(), logging.INFO)
        self.logger.setLevel(level)
        
        # Create console handler if not already configured
        if not self.logger.handlers:
            handler = logging.StreamHandler()
            handler.setLevel(level)
            
            # Create formatter with detailed information
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                datefmt='%Y-%m-%d %H:%M:%S'
            )
            handler.setFormatter(formatter)
            self.logger.addHandler(handler)
    
    def categorize_error(self, error: Exception) -> ErrorCategory:
        """
        Categorize error as transient or permanent.
        
        Implements Requirement 15.2: Error categorization
        
        Transient errors (retryable):
        - Network timeouts
        - HTTP 5xx errors
        - Temporary rate limits
        - Connection failures
        - Model unavailability
        - Cache errors
        
        Permanent errors (non-retryable):
        - HTTP 4xx errors (except 429)
        - Authentication failures
        - Invalid request format
        - Configuration errors
        - Budget exceeded
        
        Args:
            error: Exception to categorize
            
        Returns:
            ErrorCategory indicating if error is retryable
        """
        # Rate limit errors
        if isinstance(error, RateLimitError):
            return ErrorCategory.RATE_LIMIT
        
        # Authentication errors
        if isinstance(error, AuthenticationError):
            return ErrorCategory.AUTHENTICATION
        
        # Configuration errors
        if isinstance(error, ConfigurationError):
            return ErrorCategory.CONFIGURATION
        
        # Validation errors
        if isinstance(error, InvalidRequestError):
            return ErrorCategory.VALIDATION
        
        # Transient errors (retryable)
        if isinstance(error, (ModelUnavailableError, CacheError)):
            return ErrorCategory.TRANSIENT
        
        # Provider errors - check if retryable
        if isinstance(error, ProviderError):
            # 5xx errors are transient
            if error.status_code and 500 <= error.status_code < 600:
                return ErrorCategory.TRANSIENT
            # 429 is rate limit
            if error.status_code == 429:
                return ErrorCategory.RATE_LIMIT
            # Other 4xx are permanent
            return ErrorCategory.PERMANENT
        
        # Check if error has is_retryable attribute
        if isinstance(error, APIModelError):
            return ErrorCategory.TRANSIENT if error.is_retryable else ErrorCategory.PERMANENT
        
        # Default to permanent for unknown errors
        return ErrorCategory.PERMANENT
    
    def log_error(
        self,
        error: Exception,
        context: Optional[ErrorContext] = None,
        include_traceback: bool = True
    ) -> None:
        """
        Log error with detailed context.
        
        Implements Requirement 15.1: Error logging with context
        
        Args:
            error: Exception to log
            context: Additional context information
            include_traceback: Whether to include full traceback
        """
        context = context or ErrorContext()
        category = self.categorize_error(error)
        
        # Build log message
        log_parts = [f"Error: {str(error)}"]
        
        if context.model_id:
            log_parts.append(f"Model: {context.model_id}")
        if context.task_id:
            log_parts.append(f"Task: {context.task_id}")
        if context.agent_type:
            log_parts.append(f"Agent: {context.agent_type}")
        if context.provider:
            log_parts.append(f"Provider: {context.provider}")
        
        log_parts.append(f"Category: {category.value}")
        
        # Add error-specific details
        if isinstance(error, APIModelError):
            if error.details:
                log_parts.append(f"Details: {error.details}")
        
        if isinstance(error, RateLimitError):
            if error.retry_after:
                log_parts.append(f"Retry after: {error.retry_after}s")
        
        if isinstance(error, FailoverError):
            log_parts.append(f"Attempted models: {error.attempted_models}")
            log_parts.append(f"Failure reasons: {error.failure_reasons}")
        
        if isinstance(error, ProviderError):
            if error.status_code:
                log_parts.append(f"Status code: {error.status_code}")
            if error.error_code:
                log_parts.append(f"Error code: {error.error_code}")
        
        # Add request details if available
        if context.request_details:
            log_parts.append(f"Request: {context.request_details}")
        
        # Add additional context
        if context.additional_context:
            log_parts.append(f"Context: {context.additional_context}")
        
        log_message = " | ".join(log_parts)
        
        # Log at appropriate level
        if category in (ErrorCategory.PERMANENT, ErrorCategory.AUTHENTICATION, ErrorCategory.CONFIGURATION):
            self.logger.error(log_message)
        elif category == ErrorCategory.RATE_LIMIT:
            self.logger.warning(log_message)
        else:
            self.logger.warning(log_message)
        
        # Include traceback for debugging
        if include_traceback and self.logger.isEnabledFor(logging.DEBUG):
            self.logger.debug(f"Traceback: {traceback.format_exc()}")
    
    def create_error_response(
        self,
        error: Exception,
        model_id: str,
        task_id: str,
        attempted_models: Optional[List[str]] = None,
        failure_reasons: Optional[Dict[str, str]] = None
    ) -> ErrorResponse:
        """
        Create standardized error response.
        
        Implements Requirement 15.3: Permanent error detail reporting
        
        Args:
            error: Exception that occurred
            model_id: Model ID where error occurred
            task_id: Task ID for the request
            attempted_models: List of models attempted (for failover)
            failure_reasons: Reasons for each model failure
            
        Returns:
            Structured error response
        """
        category = self.categorize_error(error)
        
        # Extract error details
        error_type = type(error).__name__
        error_message = str(error)
        
        # Build attempted models list
        if attempted_models is None:
            attempted_models = [model_id]
        
        # Build failure reasons
        if failure_reasons is None:
            failure_reasons = {model_id: error_message}
        
        return ErrorResponse(
            error_type=error_type,
            error_message=error_message,
            model_id=model_id,
            task_id=task_id,
            is_retryable=(category == ErrorCategory.TRANSIENT or category == ErrorCategory.RATE_LIMIT),
            attempted_models=attempted_models,
            failure_reasons=failure_reasons,
            timestamp=datetime.now()
        )
    
    def log_event(
        self,
        event_type: EventType,
        message: str,
        model_id: Optional[str] = None,
        task_id: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None,
        severity: str = "INFO"
    ) -> None:
        """
        Log system events (rate limits, failover, alerts).
        
        Implements Requirement 15.4: Event logging coverage
        
        Args:
            event_type: Type of event
            message: Event message
            model_id: Model ID if applicable
            task_id: Task ID if applicable
            details: Additional event details
            severity: Log severity (INFO, WARNING, ERROR)
        """
        event = EventLog(
            event_type=event_type,
            timestamp=datetime.now(),
            message=message,
            model_id=model_id,
            task_id=task_id,
            details=details or {},
            severity=severity
        )
        
        # Store in recent events
        self._recent_events.append(event)
        if len(self._recent_events) > self._max_recent_events:
            self._recent_events.pop(0)
        
        # Build log message
        log_parts = [f"Event: {event_type.value}", message]
        
        if model_id:
            log_parts.append(f"Model: {model_id}")
        if task_id:
            log_parts.append(f"Task: {task_id}")
        if details:
            log_parts.append(f"Details: {details}")
        
        log_message = " | ".join(log_parts)
        
        # Log at appropriate level
        if severity == "ERROR":
            self.logger.error(log_message)
        elif severity == "WARNING":
            self.logger.warning(log_message)
        else:
            self.logger.info(log_message)
    
    def log_rate_limit_event(
        self,
        model_id: str,
        reset_time: Optional[datetime] = None,
        retry_after: Optional[int] = None,
        task_id: Optional[str] = None
    ) -> None:
        """
        Log rate limit event.
        
        Args:
            model_id: Model that hit rate limit
            reset_time: When rate limit resets
            retry_after: Seconds until retry
            task_id: Task ID if applicable
        """
        details = {}
        if reset_time:
            details["reset_time"] = reset_time.isoformat()
        if retry_after:
            details["retry_after_seconds"] = retry_after
        
        self.log_event(
            event_type=EventType.RATE_LIMIT,
            message=f"Rate limit reached for model {model_id}",
            model_id=model_id,
            task_id=task_id,
            details=details,
            severity="WARNING"
        )
    
    def log_failover_event(
        self,
        original_model: str,
        alternative_model: str,
        reason: str,
        task_id: str
    ) -> None:
        """
        Log failover event.
        
        Args:
            original_model: Original model that failed
            alternative_model: Alternative model selected
            reason: Reason for failover
            task_id: Task ID
        """
        self.log_event(
            event_type=EventType.FAILOVER,
            message=f"Failover from {original_model} to {alternative_model}",
            model_id=original_model,
            task_id=task_id,
            details={
                "original_model": original_model,
                "alternative_model": alternative_model,
                "reason": reason
            },
            severity="WARNING"
        )
    
    def log_performance_alert(
        self,
        model_id: str,
        metric: str,
        current_value: float,
        threshold: float
    ) -> None:
        """
        Log performance degradation alert.
        
        Args:
            model_id: Model with performance issue
            metric: Performance metric (e.g., "success_rate")
            current_value: Current metric value
            threshold: Threshold that was breached
        """
        self.log_event(
            event_type=EventType.PERFORMANCE_ALERT,
            message=f"Performance degradation detected for {model_id}",
            model_id=model_id,
            details={
                "metric": metric,
                "current_value": current_value,
                "threshold": threshold
            },
            severity="WARNING"
        )
    
    def log_budget_alert(
        self,
        daily_budget: float,
        current_spend: float,
        utilization_percent: float
    ) -> None:
        """
        Log budget threshold alert.
        
        Args:
            daily_budget: Configured daily budget
            current_spend: Current spending
            utilization_percent: Budget utilization percentage
        """
        self.log_event(
            event_type=EventType.BUDGET_ALERT,
            message=f"Budget threshold exceeded: {utilization_percent:.1f}% of daily budget",
            details={
                "daily_budget": daily_budget,
                "current_spend": current_spend,
                "utilization_percent": utilization_percent
            },
            severity="WARNING"
        )
    
    def log_health_check(
        self,
        model_id: str,
        is_available: bool,
        response_time_ms: Optional[float] = None,
        error_message: Optional[str] = None
    ) -> None:
        """
        Log health check result.
        
        Args:
            model_id: Model checked
            is_available: Whether model is available
            response_time_ms: Response time in milliseconds
            error_message: Error message if check failed
        """
        details = {
            "is_available": is_available
        }
        if response_time_ms is not None:
            details["response_time_ms"] = response_time_ms
        if error_message:
            details["error_message"] = error_message
        
        severity = "INFO" if is_available else "WARNING"
        message = f"Health check for {model_id}: {'available' if is_available else 'unavailable'}"
        
        self.log_event(
            event_type=EventType.HEALTH_CHECK,
            message=message,
            model_id=model_id,
            details=details,
            severity=severity
        )
    
    def log_quality_alert(
        self,
        model_id: str,
        quality_score: float,
        threshold: float,
        task_id: str
    ) -> None:
        """
        Log quality threshold alert.
        
        Args:
            model_id: Model with low quality
            quality_score: Quality score
            threshold: Quality threshold
            task_id: Task ID
        """
        self.log_event(
            event_type=EventType.QUALITY_ALERT,
            message=f"Low quality response from {model_id}",
            model_id=model_id,
            task_id=task_id,
            details={
                "quality_score": quality_score,
                "threshold": threshold
            },
            severity="WARNING"
        )
    
    def log_degraded_mode(
        self,
        component: str,
        reason: str,
        details: Optional[Dict[str, Any]] = None
    ) -> None:
        """
        Log degraded operation mode.
        
        Args:
            component: Component in degraded mode (e.g., "cache", "monitoring")
            reason: Reason for degradation
            details: Additional details
        """
        self.log_event(
            event_type=EventType.DEGRADED_MODE,
            message=f"System operating in degraded mode: {component}",
            details={
                "component": component,
                "reason": reason,
                **(details or {})
            },
            severity="WARNING"
        )
    
    def log_recovery(
        self,
        component: str,
        details: Optional[Dict[str, Any]] = None
    ) -> None:
        """
        Log recovery from degraded mode.
        
        Args:
            component: Component that recovered
            details: Additional details
        """
        self.log_event(
            event_type=EventType.RECOVERY,
            message=f"System recovered: {component}",
            details={
                "component": component,
                **(details or {})
            },
            severity="INFO"
        )
    
    def get_recent_events(
        self,
        event_type: Optional[EventType] = None,
        limit: int = 100
    ) -> List[EventLog]:
        """
        Get recent event logs.
        
        Args:
            event_type: Filter by event type (optional)
            limit: Maximum number of events to return
            
        Returns:
            List of recent event logs
        """
        events = self._recent_events
        
        if event_type:
            events = [e for e in events if e.event_type == event_type]
        
        return events[-limit:]
    
    def set_log_level(self, log_level: str) -> None:
        """
        Update logging level.
        
        Implements Requirement 15.5: Configurable log levels
        
        Args:
            log_level: New logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        """
        level = getattr(logging, log_level.upper(), logging.INFO)
        self.logger.setLevel(level)
        
        for handler in self.logger.handlers:
            handler.setLevel(level)
        
        self.logger.info(f"Log level updated to: {log_level}")


# Global error handler instance
_error_handler: Optional[ErrorHandler] = None


def get_error_handler(log_level: str = "INFO") -> ErrorHandler:
    """
    Get or create global error handler instance.
    
    Args:
        log_level: Logging level (only used on first call)
        
    Returns:
        Global ErrorHandler instance
    """
    global _error_handler
    if _error_handler is None:
        _error_handler = ErrorHandler(log_level)
    return _error_handler


def configure_logging(log_level: str = "INFO") -> None:
    """
    Configure global logging for API Model Management.
    
    Args:
        log_level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
    """
    handler = get_error_handler(log_level)
    handler.set_log_level(log_level)
