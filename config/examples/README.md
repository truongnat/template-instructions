# Configuration Examples

This directory contains example configurations for different environments and use cases.

## Available Examples

The following example configurations are available:

- **development.yaml** - Configuration optimized for local development with debugging enabled, verbose logging, and relaxed security settings
- **production.yaml** - Configuration optimized for production deployment with security hardening, performance optimization, and comprehensive monitoring
- **test.yaml** - Configuration optimized for automated testing with fast execution, minimal external dependencies, and deterministic behavior

## Purpose

These examples demonstrate:
- How to structure configuration files
- Environment-specific settings
- Best practices for different deployment scenarios
- Common configuration patterns

## Usage

Copy an example configuration and customize it for your needs:

```bash
# Copy development example
cp config/examples/development.yaml config/my-config.yaml

# Edit the configuration
vim config/my-config.yaml

# Validate the configuration
python scripts/validate-config.py config/my-config.yaml
```

## Configuration Sections

Each example configuration includes sections for:

- **Core Settings** - Basic system configuration
- **Agent Configuration** - Agent-specific settings
- **Model Configuration** - LLM model settings
- **Workflow Configuration** - Workflow execution settings
- **Logging Configuration** - Logging and monitoring settings
- **Security Configuration** - Security and secrets management

## Environment-Specific Settings

### Development
- Verbose logging enabled
- Debug mode enabled
- Local file storage
- Relaxed timeouts

### Production
- Optimized logging
- Production-grade security
- Cloud storage integration
- Strict timeouts and limits

### Test
- Test-specific fixtures
- Mock external services
- Fast execution settings
- Comprehensive logging for debugging

## Requirements

This directory satisfies:
- Requirement 3.4: Example configurations for different environments
