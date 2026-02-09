# Error Handling and Logging Guide

## Overview

The API Model Management system includes comprehensive error handling and logging capabilities through the `ErrorHandler` class. This guide explains how to use the error handling system effectively.

## Features

- **Error Categorization**: Automatic classification of errors as transient (retryable) or permanent (non-retryable)
- **Detailed Logging**: Structured logging with context including model ID, task ID, agent type, and request details
- **Event Logging**: Specialized logging for system events (rate limits, failover, alerts)
- **Configurable Log Levels**: Support for DEBUG, INFO, WARNING, ERROR, CRITICAL
- **Structured Error Responses**: Standardized error responses with complete failure information

## Quick Start

### Initialize Error Handler

```python
from agentic_sdlc.orchestration.api_model_management.error_handler import (
    get_error_handler,
    ErrorContext
)

# Get global error handler instance
error_handler = get_error_handler(log_level="INFO")
```

### Log Errors with Context

```python
from agentic_sdlc.orchestration.api_model_management.exceptions import ProviderError

try:
    # Your code that might raise an error
    response = await api_client.send_request(model_id, request)
except ProviderError as e:
    # Create context for detailed logging
    context = ErrorContext(
        model_id=model_id,
        task_id=request.task_id,
        agent_type=request.agent_type,
        provider="openai",
        request_details={"prompt_length": len(request.prompt)}
    )
    
    # Log the error with context
    error_handler.log_error(e, context)
    
    # Create standardized error response
    error_response = error_handler.create_error_response(
        error=e,
        model_id=model_id,
        task_id=request.task_id
    )
    
    # Handle based on error category
    category = error_handler.categorize_error(e)
    if category == ErrorCategory.TRANSIENT:
        # Retry logic
        pass
    else:
        # Return error to caller
        return error_response
```

## Error Categories

The error handler automatically categorizes errors:

### Transient Errors (Retryable)
- Network timeouts
- HTTP 5xx errors
- Model unavailability
- Cache errors
- Connection failures

### Permanent Errors (Non-retryable)
- HTTP 4xx errors (except 429)
- Authentication failures (401, 403)
- Invalid request format (400)
- Configuration errors
- Budget exceeded

### Rate Limit Errors
- HTTP 429 responses
- Rate limit exceeded errors

### Authentication Errors
- Missing API keys
- Invalid API keys
- Permission denied

### Configuration Errors
- Invalid configuration files
- Missing required settings
- Schema validation failures

### Validation Errors
- Invalid request parameters
- Malformed input data

## Event Logging

### Rate Limit Events

```python
error_handler.log_rate_limit_event(
    model_id="gpt-4-turbo",
    reset_time=datetime.now() + timedelta(seconds=60),
    retry_after=60,
    task_id="task-123"
)
```

### Failover Events

```python
error_handler.log_failover_event(
    original_model="gpt-4-turbo",
    alternative_model="claude-3.5-sonnet",
    reason="rate_limited",
    task_id="task-123"
)
```

### Performance Alerts

```python
error_handler.log_performance_alert(
    model_id="gpt-4-turbo",
    metric="success_rate",
    current_value=0.75,
    threshold=0.80
)
```

### Budget Alerts

```python
error_handler.log_budget_alert(
    daily_budget=100.0,
    current_spend=85.0,
    utilization_percent=85.0
)
```

### Health Check Events

```python
error_handler.log_health_check(
    model_id="gpt-4-turbo",
    is_available=True,
    response_time_ms=150.5
)
```

### Quality Alerts

```python
error_handler.log_quality_alert(
    model_id="gpt-4-turbo",
    quality_score=0.65,
    threshold=0.70,
    task_id="task-123"
)
```

### Degraded Mode

```python
# Log when entering degraded mode
error_handler.log_degraded_mode(
    component="cache",
    reason="SQLite connection failed",
    details={"error": str(e)}
)

# Log when recovering
error_handler.log_recovery(
    component="cache",
    details={"reconnected": True}
)
```

## Configuring Log Levels

### At Initialization

```python
from agentic_sdlc.orchestration.api_model_management.error_handler import configure_logging

# Configure global logging
configure_logging(log_level="DEBUG")
```

### Runtime Configuration

```python
error_handler = get_error_handler()
error_handler.set_log_level("WARNING")
```

### Available Log Levels

- **DEBUG**: Detailed information for debugging (includes tracebacks)
- **INFO**: General informational messages
- **WARNING**: Warning messages for potential issues
- **ERROR**: Error messages for failures
- **CRITICAL**: Critical errors requiring immediate attention

## Retrieving Recent Events

```python
# Get all recent events
recent_events = error_handler.get_recent_events(limit=100)

# Get specific event type
rate_limit_events = error_handler.get_recent_events(
    event_type=EventType.RATE_LIMIT,
    limit=50
)

# Process events
for event in recent_events:
    print(f"{event.timestamp}: {event.event_type.value} - {event.message}")
    if event.model_id:
        print(f"  Model: {event.model_id}")
    if event.details:
        print(f"  Details: {event.details}")
```

## Integration Examples

### In API Client Manager

```python
class APIClientManager:
    def __init__(self, ...):
        self.error_handler = get_error_handler()
    
    async def send_request_with_retry(self, model_id, request):
        for attempt in range(self.max_retries):
            try:
                return await self.send_request(model_id, request)
            except Exception as e:
                context = ErrorContext(
                    model_id=model_id,
                    task_id=request.task_id,
                    agent_type=request.agent_type,
                    request_details={"attempt": attempt + 1}
                )
                
                self.error_handler.log_error(e, context)
                
                category = self.error_handler.categorize_error(e)
                if category != ErrorCategory.TRANSIENT:
                    # Don't retry permanent errors
                    raise
                
                if attempt < self.max_retries - 1:
                    await asyncio.sleep(self.base_backoff_seconds * (2 ** attempt))
        
        # All retries failed
        return self.error_handler.create_error_response(
            error=e,
            model_id=model_id,
            task_id=request.task_id
        )
```

### In Failover Manager

```python
class FailoverManager:
    def __init__(self, ...):
        self.error_handler = get_error_handler()
    
    async def execute_with_failover(self, primary_model, task, request_func):
        try:
            return await request_func(primary_model)
        except Exception as e:
            # Log the error
            context = ErrorContext(
                model_id=primary_model,
                task_id=task.task_id
            )
            self.error_handler.log_error(e, context)
            
            # Select alternative
            alternative = await self.select_alternative(primary_model, task, reason)
            
            # Log failover event
            self.error_handler.log_failover_event(
                original_model=primary_model,
                alternative_model=alternative,
                reason=str(e),
                task_id=task.task_id
            )
            
            # Try alternative
            return await request_func(alternative)
```

### In Health Checker

```python
class HealthChecker:
    def __init__(self, ...):
        self.error_handler = get_error_handler()
    
    async def check_model_health(self, model_id):
        try:
            start_time = time.time()
            # Perform health check
            response = await self._send_health_check(model_id)
            response_time_ms = (time.time() - start_time) * 1000
            
            # Log successful check
            self.error_handler.log_health_check(
                model_id=model_id,
                is_available=True,
                response_time_ms=response_time_ms
            )
            
            return HealthStatus(...)
        except Exception as e:
            # Log failed check
            self.error_handler.log_health_check(
                model_id=model_id,
                is_available=False,
                error_message=str(e)
            )
            
            raise
```

## Best Practices

1. **Always Provide Context**: Include model_id, task_id, and other relevant context when logging errors
2. **Use Appropriate Log Levels**: Use ERROR for failures, WARNING for potential issues, INFO for normal events
3. **Log Events Consistently**: Use the specialized event logging methods for rate limits, failover, etc.
4. **Check Error Categories**: Use error categorization to determine retry logic
5. **Include Traceback for Debugging**: Enable DEBUG level to see full tracebacks
6. **Monitor Recent Events**: Periodically check recent events for patterns or issues
7. **Handle Degraded Mode**: Log when components enter degraded mode and when they recover

## Requirements Mapping

The error handling system implements the following requirements:

- **Requirement 15.1**: Error logging with context (model ID, request details, error type, timestamp)
- **Requirement 15.2**: Error categorization (transient vs permanent)
- **Requirement 15.3**: Permanent error detail reporting
- **Requirement 15.4**: Event logging coverage (rate limits, failover, alerts)
- **Requirement 15.5**: Configurable log levels

## Testing

Property-based tests verify:
- **Property 61**: Error logging completeness
- **Property 62**: Error categorization correctness
- **Property 63**: Permanent error detail reporting
- **Property 64**: Event logging coverage

See `tests/test_error_handler_property_tests.py` for comprehensive test coverage.
