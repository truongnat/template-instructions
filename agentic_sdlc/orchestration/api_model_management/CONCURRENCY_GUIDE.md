# Concurrency Control Guide

## Overview

The API Model Management system implements sophisticated concurrency controls to efficiently handle multiple concurrent API requests while respecting provider-specific rate limits and resource constraints.

## Features

### 1. Global Concurrency Limit

A global semaphore limits the total number of concurrent requests across all providers. This prevents resource exhaustion and ensures the system remains responsive.

**Default**: 100 concurrent requests

**Configuration**:
```python
client = APIClientManager(
    api_key_manager=api_key_manager,
    registry=registry,
    adapters=adapters,
    max_concurrent_requests=100  # Global limit
)
```

### 2. Per-Provider Concurrency Limits

Each provider has its own concurrency limit to respect provider-specific rate limits and prevent overwhelming individual APIs.

**Default**: 10 concurrent requests per provider

**Configuration**:
```python
client = APIClientManager(
    api_key_manager=api_key_manager,
    registry=registry,
    adapters=adapters,
    max_concurrent_requests=100,
    max_concurrent_per_provider={
        "openai": 20,      # OpenAI can handle 20 concurrent
        "anthropic": 15,   # Anthropic can handle 15 concurrent
        "google": 10,      # Google can handle 10 concurrent
        "ollama": 5        # Local Ollama limited to 5 concurrent
    }
)
```

### 3. Non-Blocking Request Processing

Requests are processed asynchronously using Python's `asyncio`. Slow requests do not block fast requests, ensuring optimal throughput.

**How it works**:
- Each request acquires both global and provider-specific semaphores
- Requests wait only if limits are reached
- Once a request completes, waiting requests can proceed
- No request blocks other requests from different providers

### 4. Concurrency Monitoring

The system provides real-time visibility into concurrency status for monitoring and debugging.

**Get concurrency status**:
```python
status = client.get_concurrency_status()
print(f"Global available slots: {status['global_limit']}")

for provider, info in status['providers'].items():
    print(f"{provider}:")
    print(f"  Active: {info['active_requests']}")
    print(f"  Limit: {info['limit']}")
    print(f"  Available: {info['available_slots']}")
```

**Get request statistics**:
```python
stats = client.get_statistics()
print(f"Total requests: {stats['request_count']}")
print(f"Successful: {stats['success_count']}")
print(f"Errors: {stats['error_count']}")
print(f"Per-provider counts: {stats['provider_request_counts']}")
```

## Implementation Details

### Semaphore Acquisition

Each request acquires semaphores in this order:

1. **Global semaphore**: Ensures total concurrent requests don't exceed global limit
2. **Provider semaphore**: Ensures provider-specific requests don't exceed provider limit

Both semaphores must be acquired before the request proceeds. This dual-semaphore approach ensures both limits are respected.

```python
async with self._global_semaphore:
    async with self._provider_semaphores[provider]:
        # Process request
        ...
```

### Request Tracking

The system tracks:
- **Total request count**: All requests ever made
- **Error count**: Failed requests
- **Per-provider request counts**: Requests per provider
- **Active requests per provider**: Currently in-flight requests

### Automatic Cleanup

Request counts are automatically updated:
- Incremented when request starts
- Decremented when request completes (success or failure)
- Tracked in a `finally` block to ensure cleanup even on errors

## Usage Examples

### Example 1: Basic Concurrent Requests

```python
import asyncio
from agentic_sdlc.orchestration.api_model_management.api_client import APIClientManager
from agentic_sdlc.orchestration.api_model_management.models import ModelRequest

async def send_multiple_requests():
    # Initialize client
    client = APIClientManager(...)
    
    # Create requests
    requests = [
        ModelRequest(prompt=f"Request {i}", parameters={}, 
                    task_id=f"task_{i}", agent_type="test")
        for i in range(10)
    ]
    
    # Send all concurrently
    tasks = [
        client.send_request_with_retry("gpt-4-turbo", req)
        for req in requests
    ]
    
    # Wait for all to complete
    responses = await asyncio.gather(*tasks, return_exceptions=True)
    
    return responses

# Run
responses = asyncio.run(send_multiple_requests())
```

### Example 2: Mixed Provider Requests

```python
async def send_mixed_requests():
    client = APIClientManager(
        max_concurrent_per_provider={
            "openai": 5,
            "anthropic": 3
        }
    )
    
    # Mix of OpenAI and Anthropic requests
    tasks = []
    
    # 10 OpenAI requests (limited to 5 concurrent)
    for i in range(10):
        req = ModelRequest(prompt=f"OpenAI {i}", ...)
        tasks.append(client.send_request("gpt-4-turbo", req))
    
    # 6 Anthropic requests (limited to 3 concurrent)
    for i in range(6):
        req = ModelRequest(prompt=f"Anthropic {i}", ...)
        tasks.append(client.send_request("claude-3.5-sonnet", req))
    
    # All 16 requests submitted, but only 5 OpenAI + 3 Anthropic
    # will run concurrently at any time
    responses = await asyncio.gather(*tasks, return_exceptions=True)
    
    return responses
```

### Example 3: Monitoring Concurrency

```python
async def monitor_concurrency():
    client = APIClientManager(...)
    
    # Start background monitoring
    async def monitor():
        while True:
            status = client.get_concurrency_status()
            print(f"Active requests: {sum(p['active_requests'] for p in status['providers'].values())}")
            await asyncio.sleep(1)
    
    monitor_task = asyncio.create_task(monitor())
    
    # Send requests
    tasks = [client.send_request(...) for _ in range(20)]
    await asyncio.gather(*tasks)
    
    # Stop monitoring
    monitor_task.cancel()
```

## Configuration Best Practices

### 1. Set Global Limit Based on System Resources

Consider:
- Available memory
- Network bandwidth
- CPU cores
- Database connection pool size

**Recommendation**: Start with 100 and adjust based on monitoring.

### 2. Set Per-Provider Limits Based on Rate Limits

Consider:
- Provider's requests-per-minute limit
- Provider's tokens-per-minute limit
- Provider's documented concurrency recommendations

**Example calculations**:
- OpenAI: 500 RPM → ~8 RPS → 20 concurrent (assuming 2.5s avg latency)
- Anthropic: 1000 RPM → ~16 RPS → 30 concurrent (assuming 2s avg latency)

### 3. Leave Headroom for Rate Limits

Don't set concurrency limits equal to rate limits. Leave 20-30% headroom to account for:
- Retry attempts
- Burst traffic
- Other applications using the same API keys

### 4. Monitor and Adjust

Regularly review:
- Concurrency utilization (are limits being hit?)
- Error rates (are we overwhelming providers?)
- Latency (are requests queuing too long?)
- Cost (are we spending efficiently?)

## Performance Characteristics

### Throughput

With proper configuration, the system can handle:
- **100+ requests/second** across all providers
- **20-30 requests/second** per provider
- **1000+ concurrent requests** in queue

### Latency

- **Semaphore acquisition**: < 1ms (when slots available)
- **Queue wait time**: Depends on request rate and limits
- **No blocking overhead**: Async processing adds minimal overhead

### Resource Usage

- **Memory**: ~1KB per queued request
- **CPU**: Minimal (async I/O bound)
- **Network**: Depends on request/response sizes

## Troubleshooting

### Problem: Requests are slow

**Possible causes**:
1. Concurrency limits too low
2. Provider API is slow
3. Network issues

**Solutions**:
- Check concurrency status: `client.get_concurrency_status()`
- Increase per-provider limits if slots are always full
- Monitor provider latency
- Check network connectivity

### Problem: Rate limit errors

**Possible causes**:
1. Concurrency limits too high
2. Multiple applications using same API keys
3. Burst traffic

**Solutions**:
- Reduce per-provider limits
- Implement request throttling
- Use multiple API keys with rotation
- Enable rate limit detection and failover

### Problem: High memory usage

**Possible causes**:
1. Too many queued requests
2. Large request/response payloads
3. Memory leaks

**Solutions**:
- Reduce global concurrency limit
- Implement request queue size limits
- Monitor memory usage over time
- Check for proper cleanup in error cases

## Integration with Other Components

### Rate Limiter

The concurrency controls work alongside the Rate Limiter:
- **Concurrency limits**: Prevent too many simultaneous requests
- **Rate limits**: Prevent exceeding provider quotas over time

Both are necessary for optimal operation.

### Failover Manager

When failover occurs:
- Original provider's semaphore is released
- Alternative provider's semaphore is acquired
- Concurrency limits are respected for both providers

### Health Checker

Health checks count toward concurrency limits but use minimal resources:
- Lightweight test requests
- Short timeouts
- Periodic execution (not continuous)

## Future Enhancements

Potential improvements:
1. **Dynamic limit adjustment**: Automatically adjust limits based on error rates
2. **Priority queuing**: High-priority requests jump the queue
3. **Adaptive concurrency**: Learn optimal limits from historical data
4. **Circuit breaker**: Temporarily reduce limits when errors spike
5. **Request batching**: Combine multiple requests into single API call

## References

- **Requirements**: 14.2, 14.4, 14.5
- **Properties**: 58, 59, 60
- **Design Document**: Section on Async Request Processing
