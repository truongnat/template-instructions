"""
Example demonstrating error handling and logging in API Model Management.

This example shows how to use the ErrorHandler for comprehensive error
handling, logging, and event tracking.
"""

import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

import asyncio
from datetime import datetime, timedelta

from agentic_sdlc.orchestration.api_model_management.error_handler import (
    get_error_handler,
    ErrorContext,
    ErrorCategory,
    EventType,
    configure_logging
)
from agentic_sdlc.orchestration.api_model_management.exceptions import (
    RateLimitError,
    ModelUnavailableError,
    ProviderError,
    AuthenticationError,
    ConfigurationError
)


def example_error_categorization():
    """Demonstrate error categorization."""
    print("\n=== Error Categorization Example ===\n")
    
    error_handler = get_error_handler(log_level="INFO")
    
    # Test different error types
    errors = [
        RateLimitError("Rate limit exceeded", model_id="gpt-4", retry_after=60),
        ModelUnavailableError("Model unavailable", model_id="gpt-4", consecutive_failures=3),
        ProviderError("Server error", provider="openai", model_id="gpt-4", status_code=500, is_retryable=True),
        ProviderError("Bad request", provider="openai", model_id="gpt-4", status_code=400, is_retryable=False),
        AuthenticationError("Invalid API key", provider="openai", model_id="gpt-4"),
        ConfigurationError("Invalid config", config_path="/path/to/config")
    ]
    
    for error in errors:
        category = error_handler.categorize_error(error)
        print(f"{type(error).__name__}: {category.value} (retryable: {error.is_retryable})")


def example_error_logging():
    """Demonstrate error logging with context."""
    print("\n=== Error Logging Example ===\n")
    
    error_handler = get_error_handler(log_level="INFO")
    
    # Create an error
    error = ProviderError(
        "API request failed",
        provider="openai",
        model_id="gpt-4-turbo",
        status_code=503,
        is_retryable=True
    )
    
    # Create context
    context = ErrorContext(
        model_id="gpt-4-turbo",
        task_id="task-12345",
        agent_type="Implementation",
        provider="openai",
        request_details={
            "prompt_length": 1500,
            "max_tokens": 2000,
            "temperature": 0.7
        },
        additional_context={
            "attempt": 2,
            "total_attempts": 3
        }
    )
    
    # Log the error
    error_handler.log_error(error, context, include_traceback=False)
    
    # Create error response
    error_response = error_handler.create_error_response(
        error=error,
        model_id="gpt-4-turbo",
        task_id="task-12345",
        attempted_models=["gpt-4-turbo", "claude-3.5-sonnet"],
        failure_reasons={
            "gpt-4-turbo": "503 Service Unavailable",
            "claude-3.5-sonnet": "Rate limit exceeded"
        }
    )
    
    print(f"\nError Response:")
    print(f"  Type: {error_response.error_type}")
    print(f"  Message: {error_response.error_message}")
    print(f"  Retryable: {error_response.is_retryable}")
    print(f"  Attempted Models: {error_response.attempted_models}")
    print(f"  Failure Reasons: {error_response.failure_reasons}")


def example_event_logging():
    """Demonstrate event logging."""
    print("\n=== Event Logging Example ===\n")
    
    error_handler = get_error_handler(log_level="INFO")
    
    # Log rate limit event
    print("Logging rate limit event...")
    error_handler.log_rate_limit_event(
        model_id="gpt-4-turbo",
        reset_time=datetime.now() + timedelta(seconds=60),
        retry_after=60,
        task_id="task-12345"
    )
    
    # Log failover event
    print("\nLogging failover event...")
    error_handler.log_failover_event(
        original_model="gpt-4-turbo",
        alternative_model="claude-3.5-sonnet",
        reason="rate_limited",
        task_id="task-12345"
    )
    
    # Log performance alert
    print("\nLogging performance alert...")
    error_handler.log_performance_alert(
        model_id="gpt-4-turbo",
        metric="success_rate",
        current_value=0.75,
        threshold=0.80
    )
    
    # Log budget alert
    print("\nLogging budget alert...")
    error_handler.log_budget_alert(
        daily_budget=100.0,
        current_spend=85.0,
        utilization_percent=85.0
    )
    
    # Log health check
    print("\nLogging health check...")
    error_handler.log_health_check(
        model_id="gpt-4-turbo",
        is_available=True,
        response_time_ms=150.5
    )
    
    # Log quality alert
    print("\nLogging quality alert...")
    error_handler.log_quality_alert(
        model_id="gpt-4-turbo",
        quality_score=0.65,
        threshold=0.70,
        task_id="task-12345"
    )
    
    # Log degraded mode
    print("\nLogging degraded mode...")
    error_handler.log_degraded_mode(
        component="cache",
        reason="SQLite connection failed",
        details={"error": "Connection timeout"}
    )
    
    # Log recovery
    print("\nLogging recovery...")
    error_handler.log_recovery(
        component="cache",
        details={"reconnected": True}
    )


def example_recent_events():
    """Demonstrate retrieving recent events."""
    print("\n=== Recent Events Example ===\n")
    
    error_handler = get_error_handler(log_level="INFO")
    
    # Log some events
    error_handler.log_rate_limit_event(
        model_id="gpt-4-turbo",
        retry_after=60,
        task_id="task-1"
    )
    
    error_handler.log_failover_event(
        original_model="gpt-4-turbo",
        alternative_model="claude-3.5-sonnet",
        reason="rate_limited",
        task_id="task-1"
    )
    
    error_handler.log_performance_alert(
        model_id="gpt-4-turbo",
        metric="success_rate",
        current_value=0.75,
        threshold=0.80
    )
    
    # Get all recent events
    print("\nAll recent events:")
    recent_events = error_handler.get_recent_events(limit=10)
    for event in recent_events:
        print(f"  {event.timestamp.strftime('%H:%M:%S')} - {event.event_type.value}: {event.message}")
    
    # Get specific event type
    print("\nRate limit events only:")
    rate_limit_events = error_handler.get_recent_events(
        event_type=EventType.RATE_LIMIT,
        limit=5
    )
    for event in rate_limit_events:
        print(f"  {event.timestamp.strftime('%H:%M:%S')} - {event.message}")
        if event.details:
            print(f"    Details: {event.details}")


def example_log_level_configuration():
    """Demonstrate log level configuration."""
    print("\n=== Log Level Configuration Example ===\n")
    
    # Configure at initialization
    configure_logging(log_level="DEBUG")
    error_handler = get_error_handler()
    
    print("Current log level: DEBUG")
    
    # Log an error with traceback (only visible at DEBUG level)
    error = ProviderError(
        "Test error",
        provider="openai",
        model_id="gpt-4",
        status_code=500,
        is_retryable=True
    )
    error_handler.log_error(error, include_traceback=True)
    
    # Change log level at runtime
    print("\nChanging log level to WARNING...")
    error_handler.set_log_level("WARNING")
    
    # This INFO message won't be logged
    error_handler.log_event(
        event_type=EventType.HEALTH_CHECK,
        message="This won't be logged (INFO level)",
        severity="INFO"
    )
    
    # This WARNING message will be logged
    error_handler.log_event(
        event_type=EventType.PERFORMANCE_ALERT,
        message="This will be logged (WARNING level)",
        severity="WARNING"
    )


async def example_retry_with_error_handler():
    """Demonstrate retry logic with error handler."""
    print("\n=== Retry Logic Example ===\n")
    
    error_handler = get_error_handler(log_level="INFO")
    
    async def simulate_api_call(attempt: int):
        """Simulate an API call that might fail."""
        if attempt < 2:
            raise ProviderError(
                "Temporary server error",
                provider="openai",
                model_id="gpt-4-turbo",
                status_code=503,
                is_retryable=True
            )
        return "Success!"
    
    max_retries = 3
    model_id = "gpt-4-turbo"
    task_id = "task-12345"
    
    for attempt in range(max_retries):
        try:
            print(f"\nAttempt {attempt + 1}/{max_retries}...")
            result = await simulate_api_call(attempt)
            print(f"Success: {result}")
            break
        except Exception as e:
            # Log the error
            context = ErrorContext(
                model_id=model_id,
                task_id=task_id,
                additional_context={"attempt": attempt + 1, "max_retries": max_retries}
            )
            error_handler.log_error(e, context, include_traceback=False)
            
            # Check if error is retryable
            category = error_handler.categorize_error(e)
            if category != ErrorCategory.TRANSIENT:
                print("Permanent error - not retrying")
                break
            
            if attempt < max_retries - 1:
                backoff = 2 ** attempt
                print(f"Retrying in {backoff} seconds...")
                await asyncio.sleep(backoff)
            else:
                print("Max retries reached")
                # Create final error response
                error_response = error_handler.create_error_response(
                    error=e,
                    model_id=model_id,
                    task_id=task_id
                )
                print(f"Final error: {error_response.error_message}")


def main():
    """Run all examples."""
    print("=" * 70)
    print("API Model Management - Error Handling Examples")
    print("=" * 70)
    
    # Run synchronous examples
    example_error_categorization()
    example_error_logging()
    example_event_logging()
    example_recent_events()
    example_log_level_configuration()
    
    # Run async example
    asyncio.run(example_retry_with_error_handler())
    
    print("\n" + "=" * 70)
    print("Examples completed!")
    print("=" * 70)


if __name__ == "__main__":
    main()
