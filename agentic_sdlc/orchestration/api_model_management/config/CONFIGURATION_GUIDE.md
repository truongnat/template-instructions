# API Model Management Configuration Guide

This guide provides comprehensive documentation for configuring the API Model Management system.

## Table of Contents

1. [Overview](#overview)
2. [Configuration Files](#configuration-files)
3. [Model Configuration](#model-configuration)
4. [System Settings](#system-settings)
5. [Environment Variables](#environment-variables)
6. [Configuration Validation](#configuration-validation)
7. [Best Practices](#best-practices)
8. [Troubleshooting](#troubleshooting)

## Overview

The API Model Management system uses JSON-based configuration files to define:
- Available AI models and their metadata
- Health check settings
- Rate limiting behavior
- Caching policies
- Budget constraints
- Quality evaluation thresholds
- Failover strategies
- Concurrency limits

Configuration is validated against a JSON schema and supports environment-specific overrides.

## Configuration Files

### Primary Configuration Files

| File | Purpose | Required |
|------|---------|----------|
| `model_registry.json` | Main configuration with model definitions | Yes |
| `schema.json` | JSON Schema for validation | Yes |
| `config.example.json` | Complete example with all options | No |
| `config.development.json` | Development environment overrides | No |
| `config.staging.json` | Staging environment overrides | No |

### File Locations

All configuration files are located in:
```
agentic_sdlc/orchestration/api_model_management/config/
```

## Model Configuration

### Model Definition Structure

Each model requires the following fields:

```json
{
  "id": "unique-model-identifier",
  "provider": "openai|anthropic|google|ollama",
  "name": "Human-readable model name",
  "capabilities": ["text-generation", "code-generation", "analysis", "reasoning"],
  "cost_per_1k_input_tokens": 0.01,
  "cost_per_1k_output_tokens": 0.03,
  "rate_limits": {
    "requests_per_minute": 500,
    "tokens_per_minute": 150000
  },
  "context_window": 128000,
  "average_response_time_ms": 2000.0,
  "enabled": true
}
```

### Field Descriptions

#### `id` (string, required)
- Unique identifier for the model
- Used in API requests and logging
- Must be unique across all models
- Example: `"gpt-4-turbo"`, `"claude-3.5-sonnet"`

#### `provider` (string, required)
- AI service provider
- Valid values: `"openai"`, `"anthropic"`, `"google"`, `"ollama"`
- Determines which adapter is used for API communication

#### `name` (string, required)
- Human-readable display name
- Used in logs and UI
- Example: `"GPT-4 Turbo"`, `"Claude 3.5 Sonnet"`

#### `capabilities` (array, required)
- List of model capabilities
- Valid values:
  - `"text-generation"` - General text generation
  - `"code-generation"` - Code writing and modification
  - `"analysis"` - Data analysis and reasoning
  - `"reasoning"` - Complex reasoning tasks
- Used for model selection based on task requirements

#### `cost_per_1k_input_tokens` (number, required)
- Cost in USD per 1000 input tokens
- Minimum: 0 (for local models)
- Used for cost tracking and budget management

#### `cost_per_1k_output_tokens` (number, required)
- Cost in USD per 1000 output tokens
- Minimum: 0 (for local models)
- Used for cost tracking and budget management

#### `rate_limits` (object, required)
- Provider-imposed rate limits
- Fields:
  - `requests_per_minute` (integer): Maximum requests per minute
  - `tokens_per_minute` (integer): Maximum tokens per minute
- Used for rate limit detection and failover

#### `context_window` (integer, required)
- Maximum context window size in tokens
- Used for request validation
- Example: 128000 for GPT-4 Turbo

#### `average_response_time_ms` (number, required)
- Expected average response time in milliseconds
- Used for performance monitoring and model selection
- Example: 2000.0 (2 seconds)

#### `enabled` (boolean, optional)
- Whether the model is available for selection
- Default: `true`
- Set to `false` to temporarily disable a model

### Adding a New Model

To add a new model to the registry:

1. Open `config/model_registry.json`
2. Add a new model object to the `models` array
3. Ensure all required fields are present
4. Validate against schema
5. Reload configuration (hot reload supported)

Example:
```json
{
  "id": "gpt-4o",
  "provider": "openai",
  "name": "GPT-4o",
  "capabilities": ["text-generation", "code-generation", "analysis", "reasoning"],
  "cost_per_1k_input_tokens": 0.005,
  "cost_per_1k_output_tokens": 0.015,
  "rate_limits": {
    "requests_per_minute": 1000,
    "tokens_per_minute": 200000
  },
  "context_window": 128000,
  "average_response_time_ms": 1500,
  "enabled": true
}
```

## System Settings

### Health Check Configuration

Controls how the system monitors model availability.

```json
{
  "health_check": {
    "interval_seconds": 60,
    "timeout_seconds": 10,
    "consecutive_failures_threshold": 3
  }
}
```

**Fields:**
- `interval_seconds` (default: 60): Time between health checks
- `timeout_seconds` (default: 10): Maximum time to wait for health check response
- `consecutive_failures_threshold` (default: 3): Number of failures before marking unavailable

**Tuning Guidelines:**
- Increase `interval_seconds` to reduce health check overhead
- Decrease for faster failure detection
- Adjust `consecutive_failures_threshold` based on provider reliability

### Rate Limiting Configuration

Controls rate limit detection and management.

```json
{
  "rate_limiting": {
    "threshold_percent": 90,
    "window_seconds": 60
  }
}
```

**Fields:**
- `threshold_percent` (default: 90): Percentage of limit to trigger rate-limited status
- `window_seconds` (default: 60): Sliding window size for rate tracking

**Tuning Guidelines:**
- Lower `threshold_percent` for more conservative rate limiting
- Increase for more aggressive usage (higher risk of hitting limits)

### Caching Configuration

Controls response caching behavior.

```json
{
  "caching": {
    "enabled": true,
    "max_size_mb": 1000,
    "default_ttl_seconds": 3600
  }
}
```

**Fields:**
- `enabled` (default: true): Enable/disable caching
- `max_size_mb` (default: 1000): Maximum cache size in megabytes
- `default_ttl_seconds` (default: 3600): Default time-to-live for cached responses

**Tuning Guidelines:**
- Increase `max_size_mb` for better cache hit rates
- Adjust `default_ttl_seconds` based on content freshness requirements
- Disable caching for real-time applications

### Budget Configuration

Controls cost tracking and alerting.

```json
{
  "budget": {
    "daily_limit": 100.0,
    "alert_threshold_percent": 80
  }
}
```

**Fields:**
- `daily_limit` (default: 100.0): Daily spending limit in USD
- `alert_threshold_percent` (default: 80): Percentage of budget to trigger alert

**Tuning Guidelines:**
- Set `daily_limit` based on your budget constraints
- Adjust `alert_threshold_percent` for early warning

### Quality Evaluation Configuration

Controls response quality assessment.

```json
{
  "quality_evaluation": {
    "enabled": true,
    "threshold": 0.7,
    "evaluation_window": 10
  }
}
```

**Fields:**
- `enabled` (default: true): Enable/disable quality evaluation
- `threshold` (default: 0.7): Minimum acceptable quality score (0-1)
- `evaluation_window` (default: 10): Number of recent requests for trend analysis

**Tuning Guidelines:**
- Increase `threshold` for stricter quality requirements
- Adjust `evaluation_window` based on workload patterns
- Disable for performance-critical applications

### Failover Configuration

Controls automatic failover behavior.

```json
{
  "failover": {
    "max_retries": 3,
    "base_backoff_seconds": 2,
    "alert_threshold": 3,
    "alert_window_hours": 1
  }
}
```

**Fields:**
- `max_retries` (default: 3): Maximum retry attempts before failover
- `base_backoff_seconds` (default: 2): Base delay for exponential backoff
- `alert_threshold` (default: 3): Number of failovers to trigger alert
- `alert_window_hours` (default: 1): Time window for failover counting

**Tuning Guidelines:**
- Increase `max_retries` for transient error tolerance
- Adjust `base_backoff_seconds` based on provider recovery time
- Lower `alert_threshold` for early problem detection

### Concurrency Configuration

Controls concurrent request processing.

```json
{
  "concurrency": {
    "max_concurrent_requests_per_provider": 10
  }
}
```

**Fields:**
- `max_concurrent_requests_per_provider` (default: 10): Maximum concurrent requests per provider

**Tuning Guidelines:**
- Increase for higher throughput (respect provider limits)
- Decrease to reduce resource usage
- Consider provider rate limits when setting

## Environment Variables

### Required API Keys

The system requires API keys for enabled providers. Set these in your `.env` file:

```bash
# OpenAI (supports multiple keys for load distribution)
OPENAI_API_KEY=sk-...
OPENAI_API_KEY_2=sk-...
OPENAI_API_KEY_3=sk-...

# Anthropic (supports multiple keys for load distribution)
ANTHROPIC_API_KEY=sk-ant-...
ANTHROPIC_API_KEY_2=sk-ant-...

# Google AI
GOOGLE_API_KEY=...
GOOGLE_API_KEY_2=...

# Ollama (local model server)
OLLAMA_BASE_URL=http://localhost:11434
```

### Key Naming Convention

- Primary key: `{PROVIDER}_API_KEY`
- Additional keys: `{PROVIDER}_API_KEY_2`, `{PROVIDER}_API_KEY_3`, etc.
- Keys are rotated using round-robin selection

### Optional Configuration Paths

```bash
# Override default configuration paths
API_MODEL_CONFIG_PATH=./config/model_registry.json
API_MODEL_DB_PATH=./data/api_model_management.db
API_MODEL_LOG_LEVEL=INFO
```

### Log Levels

Valid values for `API_MODEL_LOG_LEVEL`:
- `DEBUG`: Detailed debugging information
- `INFO`: General informational messages (default)
- `WARNING`: Warning messages
- `ERROR`: Error messages only
- `CRITICAL`: Critical errors only

## Configuration Validation

### Automatic Validation

Configuration is automatically validated on:
- System startup
- Configuration reload
- Manual validation request

### Validation Process

1. Load JSON configuration file
2. Parse JSON structure
3. Validate against `schema.json`
4. Check required fields
5. Validate field types and constraints
6. Log validation errors
7. Fall back to defaults for invalid sections

### Manual Validation

```python
from agentic_sdlc.orchestration.api_model_management.config_manager import ConfigManager

manager = ConfigManager("config/model_registry.json")
is_valid = manager.validate_current_config()

if not is_valid:
    errors = manager.get_validation_errors()
    for error in errors:
        print(f"Validation error: {error}")
```

### Common Validation Errors

| Error | Cause | Solution |
|-------|-------|----------|
| Missing required field | Field not present in model definition | Add the required field |
| Invalid type | Field has wrong data type | Correct the data type |
| Invalid enum value | Value not in allowed list | Use a valid enum value |
| Out of range | Number outside min/max bounds | Adjust to valid range |
| Invalid JSON | Syntax error in JSON | Fix JSON syntax |

## Best Practices

### Configuration Management

1. **Version Control**
   - Commit `model_registry.json` and `schema.json`
   - Do NOT commit environment-specific configs with sensitive data
   - Use `.gitignore` for environment files

2. **Environment Separation**
   - Use separate configs for dev/staging/production
   - Override only necessary settings in environment configs
   - Keep base configuration minimal

3. **Security**
   - Never commit API keys to version control
   - Use environment variables for sensitive data
   - Rotate API keys regularly
   - Use separate keys for different environments

4. **Documentation**
   - Document custom configuration values
   - Explain rationale for non-default settings
   - Keep configuration comments up to date

5. **Testing**
   - Validate configuration after manual edits
   - Test configuration changes in development first
   - Monitor logs after configuration updates

### Performance Tuning

1. **Health Checks**
   - Balance between responsiveness and overhead
   - Increase interval for stable providers
   - Decrease for critical applications

2. **Caching**
   - Enable for read-heavy workloads
   - Adjust TTL based on content freshness needs
   - Monitor cache hit rates

3. **Rate Limiting**
   - Set conservative thresholds initially
   - Adjust based on actual usage patterns
   - Monitor rate limit events

4. **Concurrency**
   - Start with default (10 concurrent requests)
   - Increase gradually while monitoring
   - Respect provider rate limits

### Cost Optimization

1. **Model Selection**
   - Use cheaper models for simple tasks
   - Reserve expensive models for complex tasks
   - Monitor cost per task type

2. **Caching**
   - Enable caching to reduce API calls
   - Increase cache size for better hit rates
   - Monitor cache effectiveness

3. **Budget Management**
   - Set realistic daily limits
   - Configure alerts at 80% threshold
   - Review cost reports regularly

## Troubleshooting

### Configuration Not Loading

**Symptoms:**
- System fails to start
- Error messages about missing configuration

**Solutions:**
1. Verify file path is correct
2. Check JSON syntax is valid
3. Ensure file has read permissions
4. Check for file locks

### Validation Errors

**Symptoms:**
- Validation error messages in logs
- System using default values

**Solutions:**
1. Review error logs for specific failures
2. Compare against `schema.json`
3. Use `config.example.json` as reference
4. Validate JSON syntax with a linter

### Models Not Available

**Symptoms:**
- No models selected
- "No available models" errors

**Solutions:**
1. Check `enabled` field is `true`
2. Verify API keys are set
3. Check health check status
4. Review rate limit status

### Hot Reload Not Working

**Symptoms:**
- Configuration changes not applied
- System using old configuration

**Solutions:**
1. Ensure file modification time changed
2. Check file system supports mtime
3. Verify no file locks
4. Restart system if necessary

### High Costs

**Symptoms:**
- Budget alerts triggered
- Unexpected spending

**Solutions:**
1. Review cost reports by model
2. Check for inefficient model usage
3. Enable/optimize caching
4. Adjust model selection strategy
5. Lower daily budget limit

### Poor Performance

**Symptoms:**
- Slow response times
- High latency

**Solutions:**
1. Check health check status
2. Review performance metrics
3. Adjust concurrency limits
4. Consider faster models
5. Optimize health check interval

### Frequent Failovers

**Symptoms:**
- Excessive failover alerts
- Inconsistent model usage

**Solutions:**
1. Check provider availability
2. Review rate limit settings
3. Adjust rate limit threshold
4. Add more API keys for load distribution
5. Consider alternative providers

## Support

For additional help:
- Review system logs at configured log level
- Check provider status pages
- Consult API provider documentation
- Review performance metrics and alerts
