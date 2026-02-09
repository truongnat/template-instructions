"""
Property-based tests for error handling and logging.

Feature: api-model-management
Tests Properties 61, 63, 64 from the design document.
"""

import pytest
from hypothesis import given, settings, strategies as st
from datetime import datetime
from unittest.mock import Mock, patch
import logging

from agentic_sdlc.orchestration.api_model_management.error_handler import (
    ErrorHandler,
    ErrorCategory,
    EventType,
    ErrorContext
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


# Hypothesis strategies for generating test data
@st.composite
def error_context_strategy(draw):
    """Generate random ErrorContext."""
    return ErrorContext(
        model_id=draw(st.one_of(st.none(), st.text(min_size=1, max_size=50))),
        task_id=draw(st.one_of(st.none(), st.text(min_size=1, max_size=50))),
        agent_type=draw(st.one_of(st.none(), st.sampled_from(["PM", "BA", "SA", "Research", "Quality", "Implementation"]))),
        provider=draw(st.one_of(st.none(), st.sampled_from(["openai", "anthropic", "google", "ollama"]))),
        request_details=draw(st.one_of(st.none(), st.dictionaries(st.text(min_size=1, max_size=20), st.text(max_size=50)))),
        additional_context=draw(st.dictionaries(st.text(min_size=1, max_size=20), st.text(max_size=50)))
    )


@st.composite
def api_model_error_strategy(draw):
    """Generate random APIModelError subclass."""
    error_type = draw(st.sampled_from([
        "RateLimitError",
        "ModelUnavailableError",
        "ConfigurationError",
        "AuthenticationError",
        "InvalidRequestError",
        "ProviderError",
        "CacheError"
    ]))
    
    message = draw(st.text(min_size=1, max_size=200))
    model_id = draw(st.text(min_size=1, max_size=50))
    
    if error_type == "RateLimitError":
        return RateLimitError(
            message=message,
            model_id=model_id,
            reset_time=draw(st.one_of(st.none(), st.floats(min_value=0, max_value=3600))),
            retry_after=draw(st.one_of(st.none(), st.integers(min_value=1, max_value=300)))
        )
    elif error_type == "ModelUnavailableError":
        return ModelUnavailableError(
            message=message,
            model_id=model_id,
            consecutive_failures=draw(st.integers(min_value=0, max_value=10))
        )
    elif error_type == "ConfigurationError":
        return ConfigurationError(
            message=message,
            config_path=draw(st.one_of(st.none(), st.text(min_size=1, max_size=100)))
        )
    elif error_type == "AuthenticationError":
        return AuthenticationError(
            message=message,
            provider=draw(st.sampled_from(["openai", "anthropic", "google"])),
            model_id=model_id
        )
    elif error_type == "InvalidRequestError":
        return InvalidRequestError(
            message=message,
            model_id=model_id
        )
    elif error_type == "ProviderError":
        return ProviderError(
            message=message,
            provider=draw(st.sampled_from(["openai", "anthropic", "google", "ollama"])),
            model_id=model_id,
            status_code=draw(st.one_of(st.none(), st.integers(min_value=400, max_value=599))),
            is_retryable=draw(st.booleans())
        )
    else:  # CacheError
        return CacheError(
            message=message,
            cache_key=draw(st.one_of(st.none(), st.text(min_size=1, max_size=64)))
        )


class TestErrorHandlerProperties:
    """Property-based tests for ErrorHandler."""
    
    @settings(max_examples=100)
    @given(
        error=api_model_error_strategy(),
        context=error_context_strategy()
    )
    def test_property_61_error_logging_completeness(self, error, context):
        """
        Feature: api-model-management
        Property 61: Error logging completeness
        
        For any error, the log entry should contain the model ID, request details,
        error type, and timestamp.
        
        Validates: Requirements 15.1
        """
        # Create error handler with captured logs
        handler = ErrorHandler(log_level="DEBUG")
        
        # Capture log output
        with patch.object(handler.logger, 'error') as mock_error, \
             patch.object(handler.logger, 'warning') as mock_warning:
            
            # Log the error
            handler.log_error(error, context, include_traceback=False)
            
            # Get the logged message
            if mock_error.called:
                log_message = mock_error.call_args[0][0]
            elif mock_warning.called:
                log_message = mock_warning.call_args[0][0]
            else:
                pytest.fail("No log message was generated")
            
            # Verify completeness: error message is present
            assert str(error) in log_message or "Error:" in log_message
            
            # Verify error type is logged (via category)
            assert "Category:" in log_message
            
            # If context has model_id, it should be in the log
            if context.model_id:
                assert context.model_id in log_message or "Model:" in log_message
            
            # If context has task_id, it should be in the log
            if context.task_id:
                assert context.task_id in log_message or "Task:" in log_message
            
            # If context has request_details, they should be logged
            if context.request_details:
                assert "Request:" in log_message
    
    @settings(max_examples=100)
    @given(
        error=st.sampled_from([
            ConfigurationError("Config error", config_path="/path/to/config"),
            AuthenticationError("Auth failed", provider="openai", model_id="gpt-4"),
            InvalidRequestError("Invalid request", model_id="gpt-4"),
            ProviderError("Provider error", provider="openai", model_id="gpt-4", status_code=400, is_retryable=False)
        ]),
        model_id=st.text(min_size=1, max_size=50),
        task_id=st.text(min_size=1, max_size=50)
    )
    def test_property_62_error_categorization(self, error, model_id, task_id):
        """
        Feature: api-model-management
        Property 62: Error categorization
        
        For any error, it should be correctly categorized as either transient
        (retryable) or permanent (non-retryable) based on error type.
        
        Validates: Requirements 15.2
        """
        handler = ErrorHandler(log_level="INFO")
        
        # Categorize the error
        category = handler.categorize_error(error)
        
        # Verify categorization matches error characteristics
        if isinstance(error, RateLimitError):
            assert category == ErrorCategory.RATE_LIMIT
        elif isinstance(error, AuthenticationError):
            assert category == ErrorCategory.AUTHENTICATION
        elif isinstance(error, ConfigurationError):
            assert category == ErrorCategory.CONFIGURATION
        elif isinstance(error, InvalidRequestError):
            assert category == ErrorCategory.VALIDATION
        elif isinstance(error, (ModelUnavailableError, CacheError)):
            assert category == ErrorCategory.TRANSIENT
        elif isinstance(error, ProviderError):
            if error.status_code and 500 <= error.status_code < 600:
                assert category == ErrorCategory.TRANSIENT
            elif error.status_code == 429:
                assert category == ErrorCategory.RATE_LIMIT
            else:
                assert category == ErrorCategory.PERMANENT
        
        # Verify is_retryable matches category
        if category in (ErrorCategory.TRANSIENT, ErrorCategory.RATE_LIMIT):
            assert error.is_retryable or isinstance(error, (ModelUnavailableError, CacheError, RateLimitError))
        elif category in (ErrorCategory.PERMANENT, ErrorCategory.AUTHENTICATION, ErrorCategory.CONFIGURATION, ErrorCategory.VALIDATION):
            # Permanent errors should not be retryable
            if hasattr(error, 'is_retryable'):
                assert not error.is_retryable
    
    @settings(max_examples=100)
    @given(
        error=st.sampled_from([
            ConfigurationError("Config error", config_path="/path/to/config", validation_errors=["Missing field"]),
            AuthenticationError("Auth failed", provider="openai", model_id="gpt-4"),
            InvalidRequestError("Invalid request", model_id="gpt-4", validation_errors=["Invalid param"]),
            ProviderError("Provider error", provider="openai", model_id="gpt-4", status_code=400, is_retryable=False)
        ]),
        model_id=st.text(min_size=1, max_size=50),
        task_id=st.text(min_size=1, max_size=50),
        attempted_models=st.lists(st.text(min_size=1, max_size=50), min_size=1, max_size=5)
    )
    def test_property_63_permanent_error_detail_reporting(self, error, model_id, task_id, attempted_models):
        """
        Feature: api-model-management
        Property 63: Permanent error detail reporting
        
        For any permanent error, the returned error response should include
        the error message, error type, and context information.
        
        Validates: Requirements 15.3
        """
        handler = ErrorHandler(log_level="INFO")
        
        # Create error response
        failure_reasons = {m: f"Failed: {str(error)}" for m in attempted_models}
        error_response = handler.create_error_response(
            error=error,
            model_id=model_id,
            task_id=task_id,
            attempted_models=attempted_models,
            failure_reasons=failure_reasons
        )
        
        # Verify error response completeness
        assert error_response.error_type is not None
        assert error_response.error_type == type(error).__name__
        
        assert error_response.error_message is not None
        assert str(error) in error_response.error_message or error_response.error_message == str(error)
        
        assert error_response.model_id == model_id
        assert error_response.task_id == task_id
        
        assert error_response.attempted_models is not None
        assert len(error_response.attempted_models) > 0
        assert model_id in error_response.attempted_models or attempted_models[0] in error_response.attempted_models
        
        assert error_response.failure_reasons is not None
        assert len(error_response.failure_reasons) > 0
        
        assert error_response.timestamp is not None
        assert isinstance(error_response.timestamp, datetime)
        
        # Verify is_retryable matches error category
        category = handler.categorize_error(error)
        if category in (ErrorCategory.PERMANENT, ErrorCategory.AUTHENTICATION, ErrorCategory.CONFIGURATION, ErrorCategory.VALIDATION):
            assert not error_response.is_retryable
    
    @settings(max_examples=100)
    @given(
        event_type=st.sampled_from([EventType.RATE_LIMIT, EventType.FAILOVER, EventType.PERFORMANCE_ALERT]),
        model_id=st.text(min_size=1, max_size=50),
        task_id=st.one_of(st.none(), st.text(min_size=1, max_size=50)),
        details=st.dictionaries(st.text(min_size=1, max_size=20), st.one_of(st.text(max_size=50), st.floats(), st.integers()))
    )
    def test_property_64_event_logging_coverage(self, event_type, model_id, task_id, details):
        """
        Feature: api-model-management
        Property 64: Event logging coverage
        
        For any rate limit event, failover event, or performance alert,
        it should be logged with complete details.
        
        Validates: Requirements 15.4
        """
        handler = ErrorHandler(log_level="INFO")
        
        # Capture log output
        with patch.object(handler.logger, 'info') as mock_info, \
             patch.object(handler.logger, 'warning') as mock_warning, \
             patch.object(handler.logger, 'error') as mock_error:
            
            # Log the event
            message = f"Test event: {event_type.value}"
            handler.log_event(
                event_type=event_type,
                message=message,
                model_id=model_id,
                task_id=task_id,
                details=details,
                severity="INFO"
            )
            
            # Verify event was logged
            assert mock_info.called or mock_warning.called or mock_error.called
            
            # Get the logged message
            if mock_info.called:
                log_message = mock_info.call_args[0][0]
            elif mock_warning.called:
                log_message = mock_warning.call_args[0][0]
            else:
                log_message = mock_error.call_args[0][0]
            
            # Verify completeness
            assert event_type.value in log_message
            assert message in log_message
            
            if model_id:
                assert model_id in log_message or "Model:" in log_message
            
            if task_id:
                assert task_id in log_message or "Task:" in log_message
            
            if details:
                assert "Details:" in log_message
        
        # Verify event is stored in recent events
        recent_events = handler.get_recent_events(event_type=event_type, limit=10)
        assert len(recent_events) > 0
        
        # Find the event we just logged
        logged_event = recent_events[-1]
        assert logged_event.event_type == event_type
        assert logged_event.message == message
        assert logged_event.model_id == model_id
        assert logged_event.task_id == task_id
        assert logged_event.details == details
    
    @settings(max_examples=50)
    @given(
        model_id=st.text(min_size=1, max_size=50),
        reset_time=st.one_of(st.none(), st.datetimes()),
        retry_after=st.one_of(st.none(), st.integers(min_value=1, max_value=300)),
        task_id=st.one_of(st.none(), st.text(min_size=1, max_size=50))
    )
    def test_rate_limit_event_logging(self, model_id, reset_time, retry_after, task_id):
        """Test rate limit event logging includes all details."""
        handler = ErrorHandler(log_level="INFO")
        
        with patch.object(handler.logger, 'warning') as mock_warning:
            handler.log_rate_limit_event(
                model_id=model_id,
                reset_time=reset_time,
                retry_after=retry_after,
                task_id=task_id
            )
            
            assert mock_warning.called
            log_message = mock_warning.call_args[0][0]
            
            # Verify rate limit event details
            assert "rate_limit" in log_message.lower()
            assert model_id in log_message
    
    @settings(max_examples=50)
    @given(
        original_model=st.text(min_size=1, max_size=50),
        alternative_model=st.text(min_size=1, max_size=50),
        reason=st.text(min_size=1, max_size=100),
        task_id=st.text(min_size=1, max_size=50)
    )
    def test_failover_event_logging(self, original_model, alternative_model, reason, task_id):
        """Test failover event logging includes all details."""
        handler = ErrorHandler(log_level="INFO")
        
        with patch.object(handler.logger, 'warning') as mock_warning:
            handler.log_failover_event(
                original_model=original_model,
                alternative_model=alternative_model,
                reason=reason,
                task_id=task_id
            )
            
            assert mock_warning.called
            log_message = mock_warning.call_args[0][0]
            
            # Verify failover event details
            assert "failover" in log_message.lower()
            assert original_model in log_message
            assert alternative_model in log_message
    
    @settings(max_examples=50)
    @given(
        model_id=st.text(min_size=1, max_size=50),
        metric=st.sampled_from(["success_rate", "latency", "quality_score"]),
        current_value=st.floats(min_value=0, max_value=1),
        threshold=st.floats(min_value=0, max_value=1)
    )
    def test_performance_alert_logging(self, model_id, metric, current_value, threshold):
        """Test performance alert logging includes all details."""
        handler = ErrorHandler(log_level="INFO")
        
        with patch.object(handler.logger, 'warning') as mock_warning:
            handler.log_performance_alert(
                model_id=model_id,
                metric=metric,
                current_value=current_value,
                threshold=threshold
            )
            
            assert mock_warning.called
            log_message = mock_warning.call_args[0][0]
            
            # Verify performance alert details
            assert "performance" in log_message.lower()
            assert model_id in log_message
    
    @settings(max_examples=50)
    @given(
        log_level=st.sampled_from(["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"])
    )
    def test_configurable_log_levels(self, log_level):
        """Test that log levels can be configured."""
        handler = ErrorHandler(log_level=log_level)
        
        # Verify log level is set correctly
        expected_level = getattr(logging, log_level.upper())
        assert handler.logger.level == expected_level
        
        # Test updating log level
        new_level = "ERROR" if log_level != "ERROR" else "INFO"
        handler.set_log_level(new_level)
        
        expected_new_level = getattr(logging, new_level.upper())
        assert handler.logger.level == expected_new_level
