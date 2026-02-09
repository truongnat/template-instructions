# API Model Management System

Intelligent model selection, real-time availability checking, automatic failover, response quality evaluation, and comprehensive cost tracking for API-based AI model connections.

## Quick Links

- **[API Documentation](API_DOCUMENTATION.md)** - Complete API reference with usage examples
- **[Configuration Guide](config/CONFIGURATION_GUIDE.md)** - Detailed configuration documentation
- **[ModelOptimizer Integration](MODEL_OPTIMIZER_INTEGRATION_GUIDE.md)** - Integration with existing ModelOptimizer
- **[Error Handling Guide](ERROR_HANDLING_GUIDE.md)** - Comprehensive error handling strategies
- **[Concurrency Guide](CONCURRENCY_GUIDE.md)** - Async/await patterns and best practices
- **[Graceful Degradation Guide](GRACEFUL_DEGRADATION_GUIDE.md)** - Handling component failures

## Overview

The API Model Management system provides:

- **Intelligent Model Selection**: Automatically selects optimal models based on task requirements, cost, and availability
- **Real-Time Health Monitoring**: Continuous health checks ensure models are available before use
- **Automatic Failover**: Seamlessly switches to alternative models when primary is unavailable or rate-limited
- **Response Quality Evaluation**: Assesses response quality and triggers model switching for low-quality outputs
- **Comprehensive Caching**: Reduces API costs by caching identical requests
- **Cost Tracking**: Monitors and reports API usage costs with budget alerts
- **Performance Monitoring**: Tracks latency, success rates, and quality scores
- **Graceful Degradation**: Continues operation even when some components fail

## Supported Providers

- **OpenAI**: GPT-4, GPT-3.5, and other OpenAI models
- **Anthropic**: Claude 3.5 Sonnet and other Claude models
- **Google**: Gemini Pro and other Google AI models
- **Ollama**: Local models (Llama, Mistral, etc.)

## Quick Start

### 1. Installation

The API Model Management system is part of the agentic_sdlc package:

```python
from agentic_sdlc.orchestration.api_model_management import (
    ModelRegistry,
    ModelSelector,
    HealthChecker,
    RateLimiter,
    PerformanceMonitor,
)
```

### 2. Configuration

Set up environment variables in `.env`:

```bash
# API Keys
OPENAI_API_KEY=sk-...
ANTHROPIC_API_KEY=sk-ant-...
GOOGLE_API_KEY=...
OLLAMA_BASE_URL=http://localhost:11434
```

Configure models in `config/model_registry.json`:

```json
{
  "models": [
    {
      "id": "gpt-4-turbo",
      "provider": "openai",
      "name": "GPT-4 Turbo",
      "capabilities": ["text-generation", "code-generation", "analysis"],
      "cost_per_1k_input_tokens": 0.01,
      "cost_per_1k_output_tokens": 0.03,
      "rate_limits": {
        "requests_per_minute": 500,
        "tokens_per_minute": 150000
      },
      "context_window": 128000,
      "average_response_time_ms": 2000,
      "enabled": true
    }
  ]
}
```

### 3. Basic Usage

```python
import asyncio
from pathlib import Path
from agentic_sdlc.orchestration.api_model_management import (
    ModelRegistry,
    ModelSelector,
    HealthChecker,
    RateLimiter,
    PerformanceMonitor,
    ModelRequest,
)

async def main():
    # Initialize components
    registry = ModelRegistry(Path("config/model_registry.json"))
    registry.load_config()
    
    health_checker = HealthChecker(registry)
    await health_checker.start()
    
    rate_limiter = RateLimiter(registry)
    performance_monitor = PerformanceMonitor(Path("data/performance.db"))
    
    selector = ModelSelector(
        registry=registry,
        health_checker=health_checker,
        rate_limiter=rate_limiter,
        performance_monitor=performance_monitor
    )
    
    # Create request
    request = ModelRequest(
        prompt="Explain how async/await works in Python",
        parameters={"temperature": 0.7},
        task_id="task-001",
        agent_type="research",
        max_tokens=500
    )
    
    # Select optimal model
    selection = await selector.select_model(request, "research")
    print(f"Selected: {selection.model_id}")
    print(f"Score: {selection.suitability_score:.2f}")
    print(f"Reason: {selection.selection_reason}")
    
    # Cleanup
    await health_checker.stop()

if __name__ == "__main__":
    asyncio.run(main())
```

## Documentation Structure

### Core Documentation

| Document | Description |
|----------|-------------|
| [API Documentation](API_DOCUMENTATION.md) | Complete API reference with all public interfaces, data models, and usage examples |
| [Configuration Guide](config/CONFIGURATION_GUIDE.md) | Detailed configuration options, validation, and best practices |
| [ModelOptimizer Integration](MODEL_OPTIMIZER_INTEGRATION_GUIDE.md) | Integration patterns with existing ModelOptimizer |

### Specialized Guides

| Guide | Description |
|-------|-------------|
| [Error Handling Guide](ERROR_HANDLING_GUIDE.md) | Error categories, handling strategies, and recovery patterns |
| [Concurrency Guide](CONCURRENCY_GUIDE.md) | Async/await patterns, connection pooling, and performance optimization |
| [Graceful Degradation Guide](GRACEFUL_DEGRADATION_GUIDE.md) | Handling component failures and maintaining partial functionality |

## Architecture

```
┌─────────────────────┐
│  ModelOptimizer     │
│  (Existing)         │
└──────────┬──────────┘
           │
           │ Model Assignment
           ▼
┌─────────────────────┐
│  API Model          │
│  Management         │
└──────────┬──────────┘
           │
           │ API Requests
           ▼
┌─────────────────────┐
│  Provider APIs      │
│  (OpenAI, etc.)     │
└─────────────────────┘
```

### Core Components

- **ModelRegistry**: Centralized repository for model metadata and configuration
- **ModelSelector**: Intelligent model selection based on task requirements, cost, and availability
- **HealthChecker**: Real-time availability monitoring for all registered models
- **RateLimiter**: Tracks and enforces rate limits to prevent quota exhaustion
- **FailoverManager**: Automatic failover to alternative models when primary is unavailable
- **APIClientManager**: Manages API connections and routes requests to provider-specific adapters
- **ResponseEvaluator**: Assesses response quality and triggers model switching for low-quality outputs
- **CacheManager**: Caches responses to reduce API calls and costs
- **CostTracker**: Tracks and reports API usage costs
- **PerformanceMonitor**: Tracks and analyzes model performance metrics

## Key Features

### Intelligent Model Selection

The system automatically selects the optimal model for each task based on:
- Task requirements and capabilities
- Real-time model availability
- Historical performance data
- Cost constraints
- Rate limit status

Selection algorithm:
1. Filter models by required capabilities
2. Filter out unavailable or rate-limited models
3. Calculate suitability score (capability: 30%, cost: 25%, performance: 25%, availability: 20%)
4. Apply task priority adjustments
5. Return highest-scoring model

### Automatic Failover

When a model is unavailable or rate-limited, the system automatically:
1. Detects the failure condition
2. Selects an alternative model using the same selection algorithm
3. Retries the request with exponential backoff
4. Logs the failover event
5. Triggers alerts if failover is excessive

### Response Quality Evaluation

Each response is evaluated using three metrics:
- **Completeness** (40%): Response addresses all task requirements
- **Relevance** (35%): Response content is relevant to task
- **Coherence** (25%): Response is well-structured and logical

Low-quality responses trigger model switching recommendations.

### Cost Tracking and Budget Management

The system tracks costs at multiple levels:
- Per request
- Per model
- Per provider
- Per agent type
- Per time period

Budget alerts are triggered when spending exceeds configured thresholds.

### Performance Monitoring

Comprehensive performance metrics include:
- Request latency (average, p50, p95, p99)
- Success/failure rates
- Quality scores
- Token usage
- Cost per request

Performance degradation triggers automatic alerts.

## Integration with ModelOptimizer

The API Model Management system integrates seamlessly with the existing ModelOptimizer:

```python
from agentic_sdlc.orchestration.api_model_management.model_optimizer_integration import (
    ModelOptimizerIntegration,
    APIModelAssignment
)

# Initialize integration
integration = ModelOptimizerIntegration(
    model_selector=selector,
    failover_manager=failover_manager,
    performance_monitor=performance_monitor,
    cost_tracker=cost_tracker
)

# Get base assignment from ModelOptimizer
base_assignment = model_optimizer.select_model_for_agent(
    agent_type=AgentType.SA,
    task=task
)

# Enhance with API selection
api_assignment = await integration.select_model_for_agent(
    agent_type=AgentType.SA,
    task=task,
    base_assignment=base_assignment
)

# Use the selected model
model_id = api_assignment.selected_model_id
```

See [ModelOptimizer Integration Guide](MODEL_OPTIMIZER_INTEGRATION_GUIDE.md) for complete integration patterns.

## Configuration Options

### Model Configuration

Each model requires:
- `id`: Unique identifier
- `provider`: Provider name (openai, anthropic, google, ollama)
- `name`: Human-readable name
- `capabilities`: List of capabilities
- `cost_per_1k_input_tokens`: Input token cost
- `cost_per_1k_output_tokens`: Output token cost
- `rate_limits`: Requests and tokens per minute
- `context_window`: Maximum context size
- `average_response_time_ms`: Expected latency
- `enabled`: Whether model is available

### System Settings

Configure:
- Health check intervals and thresholds
- Rate limit detection thresholds
- Cache size and TTL
- Budget limits and alerts
- Quality evaluation thresholds
- Failover retry logic
- Concurrency limits

See [Configuration Guide](config/CONFIGURATION_GUIDE.md) for complete configuration documentation.

## Error Handling

The system categorizes errors as:

**Transient Errors** (Retryable):
- Network timeouts
- HTTP 5xx errors
- Temporary rate limits
- Connection failures

**Permanent Errors** (Non-retryable):
- HTTP 4xx errors (except 429)
- Authentication failures
- Invalid request format
- Model not found

See [Error Handling Guide](ERROR_HANDLING_GUIDE.md) for comprehensive error handling strategies.

## Best Practices

1. **Initialize Once**: Create component instances once and reuse them
2. **Report Performance**: Always report performance data for optimization
3. **Handle Failovers**: Report failover events to improve future selections
4. **Use Constraints**: Provide selection constraints when you have specific requirements
5. **Monitor Costs**: Regularly check performance summaries to track costs
6. **Clear Cache**: Clear assignment cache when model configurations change
7. **Async All The Way**: Use async/await throughout for best performance
8. **Enable Caching**: Use caching for deterministic requests to reduce costs
9. **Set Budgets**: Configure daily budget limits to prevent overspending
10. **Monitor Health**: Review health check logs to identify provider issues

## Testing

The system includes comprehensive test coverage:

- **Unit Tests**: Specific examples and edge cases
- **Property-Based Tests**: Universal properties with randomized inputs (100+ iterations)
- **Integration Tests**: End-to-end workflows
- **Performance Tests**: Concurrent request handling and throughput

Run tests:
```bash
# All tests
pytest tests/

# Unit tests only
pytest tests/unit/

# Property-based tests only
pytest tests/property/

# Integration tests only
pytest tests/integration/
```

## Monitoring and Observability

### Logging

Configure log levels:
```bash
export API_MODEL_LOG_LEVEL=INFO
```

Valid levels: DEBUG, INFO, WARNING, ERROR, CRITICAL

### Metrics

Access performance metrics:
```python
# Get performance summary
summary = await integration.get_performance_summary(
    agent_type=AgentType.SA,
    window_hours=24
)

# Access specific metrics
print(f"Total requests: {summary['total_requests']}")
print(f"Total cost: ${summary['total_cost']:.2f}")
print(f"Success rate: {summary['average_success_rate']:.1%}")
```

### Alerts

The system triggers alerts for:
- Budget threshold exceeded
- Performance degradation detected
- Excessive failover events
- Rate limit approaching
- Provider unavailability

## Troubleshooting

### Common Issues

| Issue | Solution |
|-------|----------|
| Configuration not loading | Verify file path and JSON syntax |
| Models not available | Check API keys and health status |
| High costs | Enable caching, review model selection |
| Poor performance | Check health status, adjust concurrency |
| Frequent failovers | Review rate limits, add more API keys |

See [Configuration Guide](config/CONFIGURATION_GUIDE.md) for detailed troubleshooting.

## Requirements

- Python 3.10+
- asyncio
- aiohttp / httpx
- aiosqlite
- python-dotenv
- jsonschema

## License

See project LICENSE file.

## Support

For issues, questions, or contributions:
- Review system logs for detailed error information
- Check configuration validation errors
- Consult provider API documentation
- Review performance metrics and alerts

## See Also

- [Design Document](../../.kiro/specs/api-model-management/design.md)
- [Requirements Document](../../.kiro/specs/api-model-management/requirements.md)
- [Implementation Tasks](../../.kiro/specs/api-model-management/tasks.md)
