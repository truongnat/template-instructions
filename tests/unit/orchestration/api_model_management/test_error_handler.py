"""
Unit tests for error handling and logging.

Feature: api-model-management
Tests error categorization, log level configuration, and event logging.
Requirements: 15.2, 15.4, 15.5
"""

import pytest
import logging
from datetime import datetime
from unittest.mock import Mock, patch, MagicMock
from io import StringIO

from agentic_sdlc.orchestration.api_model_management.error_handler import (
    ErrorHandler,
    ErrorCategory,
    EventType,
    ErrorContext,
    EventLog,
    get_error_handler,
    configure_logging
)
from agentic_sdlc.orchestration.api_model_management.exceptions import (
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


class TestErrorCategorization:
    """Test error categorization logic (Requirement 15.2)."""
    
    def test_rate_limit_error_categorization(self):
        """Test that RateLimitError is categorized as RATE_LIMIT."""
        handler = ErrorHandler(log_level="INFO")
        error = RateLimitError(
            message="Rate limit exceeded",
            model_id="gpt-4",
            retry_after=60
        )
        
        category = handler.categorize_error(error)
        assert category == ErrorCategory.RATE_LIMIT
    
    def test_authentication_error_categorization(self):
        """Test that AuthenticationError is categorized as AUTHENTICATION."""
        handler = ErrorHandler(log_level="INFO")
        error = AuthenticationError(
            message="Invalid API key",
            provider="openai",
            model_id="gpt-4"
        )
        
        category = handler.categorize_error(error)
        assert category == ErrorCategory.AUTHENTICATION
    
    def test_configuration_error_categorization(self):
        """Test that ConfigurationError is categorized as CONFIGURATION."""
        handler = ErrorHandler(log_level="INFO")
        error = ConfigurationError(
            message="Invalid configuration",
            config_path="/path/to/config.json"
        )
        
        category = handler.categorize_error(error)
        assert category == ErrorCategory.CONFIGURATION
    
    def test_validation_error_categorization(self):
        """Test that InvalidRequestError is categorized as VALIDATION."""
        handler = ErrorHandler(log_level="INFO")
        error = InvalidRequestError(
            message="Invalid request parameters",
            model_id="gpt-4"
        )
        
        category = handler.categorize_error(error)
        assert category == ErrorCategory.VALIDATION
    
    def test_transient_error_categorization(self):
        """Test that transient errors are categorized as TRANSIENT."""
        handler = ErrorHandler(log_level="INFO")
        
        # Test ModelUnavailableError
        error1 = ModelUnavailableError(
            message="Model temporarily unavailable",
            model_id="gpt-4",
            consecutive_failures=2
        )
        assert handler.categorize_error(error1) == ErrorCategory.TRANSIENT
        
        # Test CacheError
        error2 = CacheError(
            message="Cache connection failed",
            cache_key="test_key"
        )
        assert handler.categorize_error(error2) == ErrorCategory.TRANSIENT
    
    def test_provider_error_5xx_categorization(self):
        """Test that ProviderError with 5xx status is categorized as TRANSIENT."""
        handler = ErrorHandler(log_level="INFO")
        
        for status_code in [500, 502, 503, 504]:
            error = ProviderError(
                message="Server error",
                provider="openai",
                model_id="gpt-4",
                status_code=status_code,
                is_retryable=True
            )
            category = handler.categorize_error(error)
            assert category == ErrorCategory.TRANSIENT, f"Status {status_code} should be TRANSIENT"
    
    def test_provider_error_429_categorization(self):
        """Test that ProviderError with 429 status is categorized as RATE_LIMIT."""
        handler = ErrorHandler(log_level="INFO")
        error = ProviderError(
            message="Too many requests",
            provider="openai",
            model_id="gpt-4",
            status_code=429,
            is_retryable=True
        )
        
        category = handler.categorize_error(error)
        assert category == ErrorCategory.RATE_LIMIT
    
    def test_provider_error_4xx_categorization(self):
        """Test that ProviderError with 4xx status (except 429) is categorized as PERMANENT."""
        handler = ErrorHandler(log_level="INFO")
        
        for status_code in [400, 401, 403, 404]:
            error = ProviderError(
                message="Client error",
                provider="openai",
                model_id="gpt-4",
                status_code=status_code,
                is_retryable=False
            )
            category = handler.categorize_error(error)
            assert category == ErrorCategory.PERMANENT, f"Status {status_code} should be PERMANENT"
    
    def test_unknown_error_categorization(self):
        """Test that unknown errors default to PERMANENT."""
        handler = ErrorHandler(log_level="INFO")
        error = Exception("Unknown error")
        
        category = handler.categorize_error(error)
        assert category == ErrorCategory.PERMANENT
    
    def test_api_model_error_with_is_retryable(self):
        """Test categorization based on is_retryable attribute."""
        handler = ErrorHandler(log_level="INFO")
        
        # Create custom error with is_retryable=True
        error1 = APIModelError(
            message="Retryable error",
            model_id="gpt-4",
            is_retryable=True
        )
        assert handler.categorize_error(error1) == ErrorCategory.TRANSIENT
        
        # Create custom error with is_retryable=False
        error2 = APIModelError(
            message="Non-retryable error",
            model_id="gpt-4",
            is_retryable=False
        )
        assert handler.categorize_error(error2) == ErrorCategory.PERMANENT


class TestLogLevelConfiguration:
    """Test log level configuration (Requirement 15.5)."""
    
    def test_default_log_level(self):
        """Test that default log level is INFO."""
        handler = ErrorHandler()
        assert handler.logger.level == logging.INFO
    
    def test_custom_log_level_initialization(self):
        """Test initialization with custom log level."""
        test_levels = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
        
        for level_str in test_levels:
            handler = ErrorHandler(log_level=level_str)
            expected_level = getattr(logging, level_str)
            assert handler.logger.level == expected_level
    
    def test_set_log_level(self):
        """Test updating log level after initialization."""
        handler = ErrorHandler(log_level="INFO")
        assert handler.logger.level == logging.INFO
        
        # Update to DEBUG
        handler.set_log_level("DEBUG")
        assert handler.logger.level == logging.DEBUG
        
        # Update to ERROR
        handler.set_log_level("ERROR")
        assert handler.logger.level == logging.ERROR
    
    def test_invalid_log_level_defaults_to_info(self):
        """Test that invalid log level defaults to INFO."""
        handler = ErrorHandler(log_level="INVALID")
        assert handler.logger.level == logging.INFO
    
    def test_log_level_case_insensitive(self):
        """Test that log level is case-insensitive."""
        handler1 = ErrorHandler(log_level="debug")
        assert handler1.logger.level == logging.DEBUG
        
        handler2 = ErrorHandler(log_level="Debug")
        assert handler2.logger.level == logging.DEBUG
        
        handler3 = ErrorHandler(log_level="DEBUG")
        assert handler3.logger.level == logging.DEBUG
    
    def test_log_level_affects_handlers(self):
        """Test that log level is applied to all handlers."""
        # Create a handler and clear any existing handlers to start fresh
        handler = ErrorHandler(log_level="WARNING")
        
        # Clear existing handlers and add a new one
        handler.logger.handlers.clear()
        test_handler = logging.StreamHandler()
        handler.logger.addHandler(test_handler)
        
        # Set level and verify it's applied to the handler
        handler.set_log_level("WARNING")
        assert test_handler.level == logging.WARNING
        
        # Update level and verify the handler is updated
        handler.set_log_level("ERROR")
        assert test_handler.level == logging.ERROR
        
        # Clean up
        handler.logger.removeHandler(test_handler)
    
    def test_configure_logging_function(self):
        """Test the configure_logging utility function."""
        # Reset global handler
        import agentic_sdlc.orchestration.api_model_management.error_handler as eh_module
        eh_module._error_handler = None
        
        configure_logging("DEBUG")
        handler = get_error_handler()
        assert handler.logger.level == logging.DEBUG


class TestEventLogging:
    """Test event logging functionality (Requirement 15.4)."""
    
    def test_log_event_basic(self):
        """Test basic event logging."""
        handler = ErrorHandler(log_level="INFO")
        
        with patch.object(handler.logger, 'info') as mock_info:
            handler.log_event(
                event_type=EventType.HEALTH_CHECK,
                message="Health check passed",
                model_id="gpt-4",
                task_id="task-123",
                details={"response_time_ms": 150},
                severity="INFO"
            )
            
            assert mock_info.called
            log_message = mock_info.call_args[0][0]
            assert "health_check" in log_message
            assert "Health check passed" in log_message
            assert "gpt-4" in log_message
    
    def test_log_event_stored_in_recent_events(self):
        """Test that logged events are stored in recent events."""
        handler = ErrorHandler(log_level="INFO")
        
        handler.log_event(
            event_type=EventType.FAILOVER,
            message="Failover occurred",
            model_id="gpt-4",
            task_id="task-123",
            details={"reason": "rate_limited"},
            severity="WARNING"
        )
        
        recent_events = handler.get_recent_events(limit=10)
        assert len(recent_events) > 0
        
        last_event = recent_events[-1]
        assert last_event.event_type == EventType.FAILOVER
        assert last_event.message == "Failover occurred"
        assert last_event.model_id == "gpt-4"
        assert last_event.task_id == "task-123"
        assert last_event.details["reason"] == "rate_limited"
    
    def test_log_event_severity_levels(self):
        """Test that events are logged at correct severity levels."""
        handler = ErrorHandler(log_level="DEBUG")
        
        # Test INFO severity
        with patch.object(handler.logger, 'info') as mock_info:
            handler.log_event(
                event_type=EventType.RECOVERY,
                message="System recovered",
                severity="INFO"
            )
            assert mock_info.called
        
        # Test WARNING severity
        with patch.object(handler.logger, 'warning') as mock_warning:
            handler.log_event(
                event_type=EventType.RATE_LIMIT,
                message="Rate limit reached",
                severity="WARNING"
            )
            assert mock_warning.called
        
        # Test ERROR severity
        with patch.object(handler.logger, 'error') as mock_error:
            handler.log_event(
                event_type=EventType.PERFORMANCE_ALERT,
                message="Performance degraded",
                severity="ERROR"
            )
            assert mock_error.called
    
    def test_log_rate_limit_event(self):
        """Test rate limit event logging."""
        handler = ErrorHandler(log_level="INFO")
        
        with patch.object(handler.logger, 'warning') as mock_warning:
            reset_time = datetime.now()
            handler.log_rate_limit_event(
                model_id="gpt-4",
                reset_time=reset_time,
                retry_after=60,
                task_id="task-123"
            )
            
            assert mock_warning.called
            log_message = mock_warning.call_args[0][0]
            assert "rate limit" in log_message.lower()
            assert "gpt-4" in log_message
        
        # Verify event is stored
        events = handler.get_recent_events(event_type=EventType.RATE_LIMIT, limit=10)
        assert len(events) > 0
        assert events[-1].details.get("retry_after_seconds") == 60
    
    def test_log_failover_event(self):
        """Test failover event logging."""
        handler = ErrorHandler(log_level="INFO")
        
        with patch.object(handler.logger, 'warning') as mock_warning:
            handler.log_failover_event(
                original_model="gpt-4",
                alternative_model="gpt-3.5-turbo",
                reason="rate_limited",
                task_id="task-123"
            )
            
            assert mock_warning.called
            log_message = mock_warning.call_args[0][0]
            assert "failover" in log_message.lower()
            assert "gpt-4" in log_message
            assert "gpt-3.5-turbo" in log_message
        
        # Verify event details
        events = handler.get_recent_events(event_type=EventType.FAILOVER, limit=10)
        assert len(events) > 0
        event = events[-1]
        assert event.details["original_model"] == "gpt-4"
        assert event.details["alternative_model"] == "gpt-3.5-turbo"
        assert event.details["reason"] == "rate_limited"
    
    def test_log_performance_alert(self):
        """Test performance alert logging."""
        handler = ErrorHandler(log_level="INFO")
        
        with patch.object(handler.logger, 'warning') as mock_warning:
            handler.log_performance_alert(
                model_id="gpt-4",
                metric="success_rate",
                current_value=0.75,
                threshold=0.80
            )
            
            assert mock_warning.called
            log_message = mock_warning.call_args[0][0]
            assert "performance" in log_message.lower()
            assert "gpt-4" in log_message
        
        # Verify event details
        events = handler.get_recent_events(event_type=EventType.PERFORMANCE_ALERT, limit=10)
        assert len(events) > 0
        event = events[-1]
        assert event.details["metric"] == "success_rate"
        assert event.details["current_value"] == 0.75
        assert event.details["threshold"] == 0.80
    
    def test_log_budget_alert(self):
        """Test budget alert logging."""
        handler = ErrorHandler(log_level="INFO")
        
        with patch.object(handler.logger, 'warning') as mock_warning:
            handler.log_budget_alert(
                daily_budget=100.0,
                current_spend=95.0,
                utilization_percent=95.0
            )
            
            assert mock_warning.called
            log_message = mock_warning.call_args[0][0]
            assert "budget" in log_message.lower()
            assert "95.0%" in log_message
        
        # Verify event details
        events = handler.get_recent_events(event_type=EventType.BUDGET_ALERT, limit=10)
        assert len(events) > 0
        event = events[-1]
        assert event.details["daily_budget"] == 100.0
        assert event.details["current_spend"] == 95.0
        assert event.details["utilization_percent"] == 95.0
    
    def test_log_health_check(self):
        """Test health check logging."""
        handler = ErrorHandler(log_level="INFO")
        
        # Test successful health check
        with patch.object(handler.logger, 'info') as mock_info:
            handler.log_health_check(
                model_id="gpt-4",
                is_available=True,
                response_time_ms=150.5
            )
            
            assert mock_info.called
            log_message = mock_info.call_args[0][0]
            assert "health check" in log_message.lower()
            assert "available" in log_message.lower()
        
        # Test failed health check
        with patch.object(handler.logger, 'warning') as mock_warning:
            handler.log_health_check(
                model_id="gpt-4",
                is_available=False,
                error_message="Connection timeout"
            )
            
            assert mock_warning.called
            log_message = mock_warning.call_args[0][0]
            assert "unavailable" in log_message.lower()
    
    def test_log_quality_alert(self):
        """Test quality alert logging."""
        handler = ErrorHandler(log_level="INFO")
        
        with patch.object(handler.logger, 'warning') as mock_warning:
            handler.log_quality_alert(
                model_id="gpt-4",
                quality_score=0.65,
                threshold=0.70,
                task_id="task-123"
            )
            
            assert mock_warning.called
            log_message = mock_warning.call_args[0][0]
            assert "quality" in log_message.lower()
            assert "gpt-4" in log_message
        
        # Verify event details
        events = handler.get_recent_events(event_type=EventType.QUALITY_ALERT, limit=10)
        assert len(events) > 0
        event = events[-1]
        assert event.details["quality_score"] == 0.65
        assert event.details["threshold"] == 0.70
    
    def test_log_degraded_mode(self):
        """Test degraded mode logging."""
        handler = ErrorHandler(log_level="INFO")
        
        with patch.object(handler.logger, 'warning') as mock_warning:
            handler.log_degraded_mode(
                component="cache",
                reason="Connection failed",
                details={"error": "Timeout"}
            )
            
            assert mock_warning.called
            log_message = mock_warning.call_args[0][0]
            assert "degraded" in log_message.lower()
            assert "cache" in log_message
        
        # Verify event details
        events = handler.get_recent_events(event_type=EventType.DEGRADED_MODE, limit=10)
        assert len(events) > 0
        event = events[-1]
        assert event.details["component"] == "cache"
        assert event.details["reason"] == "Connection failed"
    
    def test_log_recovery(self):
        """Test recovery logging."""
        handler = ErrorHandler(log_level="INFO")
        
        with patch.object(handler.logger, 'info') as mock_info:
            handler.log_recovery(
                component="cache",
                details={"reconnected": True}
            )
            
            assert mock_info.called
            log_message = mock_info.call_args[0][0]
            assert "recovered" in log_message.lower()
            assert "cache" in log_message
        
        # Verify event details
        events = handler.get_recent_events(event_type=EventType.RECOVERY, limit=10)
        assert len(events) > 0
        event = events[-1]
        assert event.details["component"] == "cache"
    
    def test_get_recent_events_filtering(self):
        """Test filtering recent events by type."""
        handler = ErrorHandler(log_level="INFO")
        
        # Log multiple event types
        handler.log_event(EventType.RATE_LIMIT, "Rate limit 1", severity="WARNING")
        handler.log_event(EventType.FAILOVER, "Failover 1", severity="WARNING")
        handler.log_event(EventType.RATE_LIMIT, "Rate limit 2", severity="WARNING")
        handler.log_event(EventType.PERFORMANCE_ALERT, "Performance 1", severity="WARNING")
        handler.log_event(EventType.RATE_LIMIT, "Rate limit 3", severity="WARNING")
        
        # Get all events
        all_events = handler.get_recent_events(limit=100)
        assert len(all_events) >= 5
        
        # Get only rate limit events
        rate_limit_events = handler.get_recent_events(event_type=EventType.RATE_LIMIT, limit=100)
        assert len(rate_limit_events) >= 3
        assert all(e.event_type == EventType.RATE_LIMIT for e in rate_limit_events)
        
        # Get only failover events
        failover_events = handler.get_recent_events(event_type=EventType.FAILOVER, limit=100)
        assert len(failover_events) >= 1
        assert all(e.event_type == EventType.FAILOVER for e in failover_events)
    
    def test_get_recent_events_limit(self):
        """Test limiting number of returned events."""
        handler = ErrorHandler(log_level="INFO")
        
        # Log many events
        for i in range(20):
            handler.log_event(EventType.HEALTH_CHECK, f"Health check {i}", severity="INFO")
        
        # Get limited events
        events = handler.get_recent_events(limit=5)
        assert len(events) == 5
        
        # Verify we get the most recent ones
        assert "Health check 19" in events[-1].message
    
    def test_recent_events_max_storage(self):
        """Test that recent events storage is limited."""
        handler = ErrorHandler(log_level="INFO")
        max_events = handler._max_recent_events
        
        # Log more than max events
        for i in range(max_events + 100):
            handler.log_event(EventType.HEALTH_CHECK, f"Event {i}", severity="INFO")
        
        # Verify storage doesn't exceed max
        all_events = handler.get_recent_events(limit=max_events + 200)
        assert len(all_events) <= max_events


class TestGlobalErrorHandler:
    """Test global error handler functions."""
    
    def test_get_error_handler_singleton(self):
        """Test that get_error_handler returns singleton instance."""
        # Reset global handler
        import agentic_sdlc.orchestration.api_model_management.error_handler as eh_module
        eh_module._error_handler = None
        
        handler1 = get_error_handler("INFO")
        handler2 = get_error_handler("DEBUG")  # Should return same instance
        
        assert handler1 is handler2
    
    def test_configure_logging_updates_level(self):
        """Test that configure_logging updates the global handler."""
        # Reset global handler
        import agentic_sdlc.orchestration.api_model_management.error_handler as eh_module
        eh_module._error_handler = None
        
        configure_logging("WARNING")
        handler = get_error_handler()
        assert handler.logger.level == logging.WARNING
        
        configure_logging("DEBUG")
        assert handler.logger.level == logging.DEBUG


class TestErrorContextAndResponse:
    """Test error context and response creation."""
    
    def test_error_context_creation(self):
        """Test creating error context with various fields."""
        context = ErrorContext(
            model_id="gpt-4",
            task_id="task-123",
            agent_type="PM",
            provider="openai",
            request_details={"prompt": "test"},
            additional_context={"retry_count": 2}
        )
        
        assert context.model_id == "gpt-4"
        assert context.task_id == "task-123"
        assert context.agent_type == "PM"
        assert context.provider == "openai"
        assert context.request_details["prompt"] == "test"
        assert context.additional_context["retry_count"] == 2
    
    def test_create_error_response(self):
        """Test creating standardized error response."""
        handler = ErrorHandler(log_level="INFO")
        error = InvalidRequestError(
            message="Invalid parameters",
            model_id="gpt-4"
        )
        
        response = handler.create_error_response(
            error=error,
            model_id="gpt-4",
            task_id="task-123",
            attempted_models=["gpt-4", "gpt-3.5-turbo"],
            failure_reasons={"gpt-4": "Invalid parameters", "gpt-3.5-turbo": "Rate limited"}
        )
        
        assert response.error_type == "InvalidRequestError"
        assert response.error_message == "Invalid parameters"
        assert response.model_id == "gpt-4"
        assert response.task_id == "task-123"
        assert not response.is_retryable  # Validation errors are not retryable
        assert len(response.attempted_models) == 2
        assert len(response.failure_reasons) == 2
        assert isinstance(response.timestamp, datetime)
    
    def test_create_error_response_defaults(self):
        """Test error response creation with default values."""
        handler = ErrorHandler(log_level="INFO")
        error = ModelUnavailableError(
            message="Model unavailable",
            model_id="gpt-4",
            consecutive_failures=3
        )
        
        response = handler.create_error_response(
            error=error,
            model_id="gpt-4",
            task_id="task-123"
        )
        
        # Should default to single model
        assert response.attempted_models == ["gpt-4"]
        assert "gpt-4" in response.failure_reasons
        assert response.is_retryable  # Transient errors are retryable
