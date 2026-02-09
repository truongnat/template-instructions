# API Model Management Configuration

This directory contains configuration files for the API Model Management system.

## Files

### `schema.json`
JSON Schema definition for validating configuration files. Defines the structure and constraints for all configuration options.

### `model_registry.json`
Main configuration file containing:
- Model definitions (providers, costs, rate limits, capabilities)
- Health check settings
- Rate limiting configuration
- Caching settings
- Budget limits
- Quality evaluation settings
- Failover configuration
- Concurrency limits

### `config.example.json`
Complete example configuration with all available options and their default values.

### Environment-Specific Configurations

- `config.development.json` - Development environment overrides
- `config.staging.json` - Staging environment overrides
- `config.production.json` - Production environment overrides (if needed)

## Configuration Structure

```json
{
  "models": [...],              // Required: List of AI models
  "health_check": {...},        // Optional: Health check settings
  "rate_limiting": {...},       // Optional: Rate limit settings
  "caching": {...},             // Optional: Cache settings
  "budget": {...},              // Optional: Budget settings
  "quality_evaluation": {...},  // Optional: Quality evaluation settings
  "failover": {...},            // Optional: Failover settings
  "concurrency": {...}          // Optional: Concurrency settings
}
```

## Model Configuration

Each model requires:

```json
{
  "id": "unique-model-id",
  "provider": "openai|anthropic|google|ollama",
  "name": "Human-readable name",
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

## Usage

### Basic Usage

```python
from pathlib import Path
from agentic_sdlc.orchestration.api_model_management.config_manager import ConfigManager

# Load configuration
config_path = Path("config/model_registry.json")
manager = ConfigManager(config_path)

# Get full configuration
config = manager.get_config()

# Get specific sections
health_check = manager.get_health_check_config()
rate_limiting = manager.get_rate_limiting_config()
models = manager.get_models()
```

### Environment-Specific Configuration

```python
# Load with environment
manager = ConfigManager(config_path, environment="development")

# Get environment-specific overrides
env_config = manager.get_environment_config()
```

### Hot Reload

```python
# Check for and reload configuration changes
if manager.reload_config():
    print("Configuration reloaded")
    config = manager.get_config()
```

### Dot Notation Access

```python
# Access nested values with dot notation
interval = manager.get("health_check.interval_seconds", default=60)
threshold = manager.get("rate_limiting.threshold_percent", default=90)
```

## Configuration Validation

The configuration is automatically validated against `schema.json` on load. Invalid configurations will:

1. Log detailed validation errors
2. Fall back to default values
3. Continue operation with safe defaults

To manually validate:

```python
is_valid = manager.validate_current_config()
```

## Default Values

If configuration sections are omitted, the following defaults are used:

- **Health Check**: 60s interval, 10s timeout, 3 consecutive failures threshold
- **Rate Limiting**: 90% threshold, 60s window
- **Caching**: Enabled, 1000MB max size, 3600s TTL
- **Budget**: $100 daily limit, 80% alert threshold
- **Quality Evaluation**: Enabled, 0.7 threshold, 10 request window
- **Failover**: 3 max retries, 2s base backoff, 3 failover alert threshold, 1 hour window
- **Concurrency**: 10 max concurrent requests per provider

## Environment Variables

API keys should be set as environment variables:

```bash
# OpenAI
OPENAI_API_KEY=sk-...
OPENAI_API_KEY_2=sk-...

# Anthropic
ANTHROPIC_API_KEY=sk-ant-...

# Google
GOOGLE_API_KEY=...

# Ollama (local)
OLLAMA_BASE_URL=http://localhost:11434
```

## Best Practices

1. **Version Control**: Commit `model_registry.json` and `schema.json`, but not environment-specific configs with sensitive data
2. **Environment Separation**: Use environment-specific configs for different deployment stages
3. **Hot Reload**: Monitor configuration changes in production for dynamic updates
4. **Validation**: Always validate configuration after manual edits
5. **Defaults**: Rely on defaults for optional settings unless specific tuning is needed
6. **Documentation**: Document any custom configuration values and their rationale

## Troubleshooting

### Configuration Not Loading

- Check file path is correct
- Verify JSON syntax is valid
- Check file permissions

### Validation Errors

- Review error logs for specific validation failures
- Compare against `schema.json` for required fields
- Use `config.example.json` as reference

### Hot Reload Not Working

- Ensure file modification time has changed
- Check file system supports modification time tracking
- Verify no file locks preventing updates
