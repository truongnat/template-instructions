# Graceful Degradation Guide

## Overview

The Graceful Degradation Manager ensures the API Model Management system remains partially functional when components or providers fail. It implements five key degradation strategies:

1. **Provider Failure Isolation** (Requirement 18.1)
2. **Request Queuing on Total Unavailability** (Requirement 18.2)
3. **Cache Failure Fallback** (Requirement 18.3)
4. **Monitoring Failure Fallback** (Requirement 18.4)
5. **Degraded Mode Logging** (Requirement 18.5)

## Quick Start

```python
from agentic_sdlc.orchestration.api_model_management import (
    GracefulDegradationManager,
    DegradationMode,
    ModelRequest
)

# Initialize the manager
degradation_mgr = GracefulDegradationManager(
    retry_interval_seconds=30,
    max_queue_size=1000,
    queue_retry_base_delay=5
)

# Start the background queue processor
await degradation_mgr.start()

try:
    # Your application logic here
    pass
finally:
    # Stop the manager
    await degradation_mgr.stop()
```

## Provider Failure Isolation

When a provider fails, the system automatically isolates it and continues using other providers.

```python
# Mark a provider as failed
degradation_mgr.mark_provider_failure("openai", error=exception)

# Check if a provider is available
if degradation_mgr.is_provider_available("openai"):
    # Use the provider
    pass

# Get list of available providers
all_providers = ["openai", "anthropic", "google"]
available = degradation_mgr.get_available_providers(all_providers)

# Mark provider as recovered
degradation_mgr.mark_provider_success("openai")
```

**Behavior:**
- Provider is marked unavailable after 3 consecutive failures
- Other providers continue to work normally
- Provider can recover with a single successful request

## Request Queuing

When all providers are unavailable, requests are queued and retried periodically.

```python
# Queue a request during total unavailability
request = ModelRequest(
    prompt="Generate code",
    parameters={"temperature": 0.7},
    task_id="task-123",
    agent_type="implementation"
)

queued = await degradation_mgr.queue_request(request, "gpt-4")

if queued:
    print("Request queued successfully")
else:
    print("Queue is full")

# Get requests ready for processing
ready_requests = degradation_mgr.get_queued_requests()

for queued_req in ready_requests:
    try:
        # Process the request
        result = await process_request(queued_req.request)
        
        # Remove from queue on success
        degradation_mgr.remove_from_queue(queued_req)
    except Exception as e:
        # Requeue with exponential backoff on failure
        degradation_mgr.requeue_with_backoff(queued_req)
```

**Behavior:**
- Requests are queued when all providers are unavailable
- Queue has a maximum size (default: 1000)
- Failed retries use exponential backoff (5s, 10s, 20s, 40s, 80s)
- Requests are removed after 5 failed retries

## Cache Failure Fallback

When cache fails, the system continues without caching.

```python
try:
    # Try to use cache
    cached = await cache_manager.get(cache_key)
except CacheError as e:
    # Mark cache as failed
    degradation_mgr.mark_cache_failure(e)
    
    # Continue without cache
    result = await api_client.send_request(request)

# Check if cache is available
if degradation_mgr.is_cache_available():
    # Use cache
    pass
else:
    # Skip caching
    pass

# Mark cache as recovered
degradation_mgr.mark_cache_success()
```

**Behavior:**
- System continues operating without cache
- Degradation mode changes to `CACHE_UNAVAILABLE`
- Cache can be marked as recovered when it's working again

## Monitoring Failure Fallback

When monitoring fails, the system continues without recording metrics.

```python
try:
    # Try to record metrics
    await performance_monitor.record_performance(...)
except Exception as e:
    # Mark monitoring as failed
    degradation_mgr.mark_monitoring_failure(e)
    
    # Continue without monitoring
    pass

# Check if monitoring is available
if degradation_mgr.is_monitoring_available():
    # Record metrics
    pass
else:
    # Skip monitoring
    pass

# Mark monitoring as recovered
degradation_mgr.mark_monitoring_success()
```

**Behavior:**
- System continues operating without metrics
- Degradation mode changes to `MONITORING_UNAVAILABLE`
- Monitoring can be marked as recovered when it's working again

## Degradation Status

Check the current degradation status:

```python
status = degradation_mgr.get_degradation_status()

print(f"Mode: {status.mode.value}")
print(f"Affected components: {status.affected_components}")
print(f"Unavailable providers: {status.unavailable_providers}")
print(f"Message: {status.message}")

if status.degraded_since:
    print(f"Degraded since: {status.degraded_since}")
```

**Degradation Modes:**
- `NORMAL`: All components healthy
- `CACHE_UNAVAILABLE`: Cache failed, operating without caching
- `MONITORING_UNAVAILABLE`: Monitoring failed, operating without metrics
- `PROVIDER_UNAVAILABLE`: One provider failed
- `PARTIAL_PROVIDER_UNAVAILABLE`: Some providers failed
- `TOTAL_UNAVAILABILITY`: All providers failed, queuing requests

## Degradation Event Logging

View degradation event history:

```python
# Get all events
events = degradation_mgr.get_degradation_events()

# Get last 10 events
recent_events = degradation_mgr.get_degradation_events(limit=10)

# Get events since a specific time
from datetime import datetime, timedelta
since_time = datetime.now() - timedelta(hours=1)
recent_events = degradation_mgr.get_degradation_events(since=since_time)

# Print events
for event in events:
    print(f"{event['timestamp']}: {event['mode']} - {event['message']}")
    print(f"  Affected: {event['affected_components']}")
```

**Event Structure:**
```python
{
    "timestamp": "2026-02-08T23:00:00.000000",
    "mode": "provider_unavailable",
    "message": "Provider openai marked as unavailable after 3 failures",
    "affected_components": ["openai"]
}
```

## Execute with Fallback Helper

Generic helper for implementing fallback patterns:

```python
async def primary_operation():
    # Try primary approach
    return await cache_manager.get(key)

async def fallback_operation():
    # Fallback approach
    return await api_client.send_request(request)

# Execute with automatic fallback
result = await degradation_mgr.execute_with_fallback(
    primary_operation,
    fallback_operation,
    component_name="cache"
)
```

**Behavior:**
- Tries primary function first
- Falls back to fallback function on error
- Logs warnings for failures
- Raises exception if both fail

## Integration Example

Complete integration with API Model Management:

```python
class APIModelManager:
    def __init__(self):
        self.degradation_mgr = GracefulDegradationManager()
        self.cache_manager = CacheManager()
        self.performance_monitor = PerformanceMonitor()
        
    async def start(self):
        await self.degradation_mgr.start()
        
    async def send_request(self, request: ModelRequest, model_id: str):
        # Check provider availability
        provider = self.get_provider_for_model(model_id)
        
        if not self.degradation_mgr.is_provider_available(provider):
            # Queue request if provider unavailable
            await self.degradation_mgr.queue_request(request, model_id)
            raise ModelUnavailableError(f"Provider {provider} unavailable")
        
        # Try cache if available
        if self.degradation_mgr.is_cache_available():
            try:
                cached = await self.cache_manager.get(request)
                if cached:
                    return cached
            except CacheError as e:
                self.degradation_mgr.mark_cache_failure(e)
        
        # Send request
        try:
            response = await self.api_client.send_request(model_id, request)
            
            # Mark provider success
            self.degradation_mgr.mark_provider_success(provider)
            
            # Record metrics if monitoring available
            if self.degradation_mgr.is_monitoring_available():
                try:
                    await self.performance_monitor.record_performance(...)
                except Exception as e:
                    self.degradation_mgr.mark_monitoring_failure(e)
            
            return response
            
        except ProviderError as e:
            # Mark provider failure
            self.degradation_mgr.mark_provider_failure(provider, e)
            raise
```

## Configuration

```python
degradation_mgr = GracefulDegradationManager(
    # How often to process queued requests (seconds)
    retry_interval_seconds=30,
    
    # Maximum number of requests to queue
    max_queue_size=1000,
    
    # Base delay for exponential backoff (seconds)
    queue_retry_base_delay=5
)
```

## Best Practices

1. **Always start/stop the manager:**
   ```python
   await degradation_mgr.start()
   try:
       # Your code
   finally:
       await degradation_mgr.stop()
   ```

2. **Check availability before operations:**
   ```python
   if degradation_mgr.is_provider_available(provider):
       # Use provider
   ```

3. **Mark successes to enable recovery:**
   ```python
   degradation_mgr.mark_provider_success(provider)
   ```

4. **Monitor degradation status:**
   ```python
   status = degradation_mgr.get_degradation_status()
   if status.mode != DegradationMode.NORMAL:
       logger.warning(f"System degraded: {status.message}")
   ```

5. **Process queued requests when providers recover:**
   ```python
   ready_requests = degradation_mgr.get_queued_requests()
   for queued_req in ready_requests:
       # Process and remove from queue
   ```

## Monitoring and Alerting

Monitor these metrics for operational health:

- **Degradation mode**: Alert when not NORMAL
- **Queue size**: Alert when approaching max_queue_size
- **Provider availability**: Alert when providers are unavailable
- **Degradation events**: Track frequency of degradation events
- **Recovery time**: Track time spent in degraded modes

## See Also

- [Error Handling Guide](ERROR_HANDLING_GUIDE.md)
- [Concurrency Guide](CONCURRENCY_GUIDE.md)
- [Examples](../../examples/graceful_degradation_example.py)
