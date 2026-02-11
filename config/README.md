# Configuration Directory

This directory contains centralized configuration management for the SDLC Kit.

## Structure

- **schemas/** - JSON schemas for configuration validation
- **examples/** - Example configurations for different environments
- **defaults.yaml** - Default configuration values (to be created in task 5.2)

## Purpose

The configuration management system provides:
- Centralized configuration with schema validation
- Environment-specific configuration examples
- Type-safe configuration loading and validation
- Clear documentation of all configuration options

## Usage

```python
from config.validators import ConfigValidator

# Load and validate configuration
validator = ConfigValidator()
config = validator.load_and_validate("config/defaults.yaml", "config/schemas/workflow.schema.json")
```

## Requirements

This configuration system satisfies:
- Requirement 3.1: Centralized config directory
- Requirement 3.2: Default configuration in YAML format
- Requirement 3.3: JSON schemas for all configuration types
- Requirement 3.4: Example configurations for different environments
- Requirement 3.5: Schema validation for configuration files
- Requirement 3.6: Descriptive error messages for validation failures
- Requirement 3.7: Configuration schemas for workflows, agents, rules, and skills
