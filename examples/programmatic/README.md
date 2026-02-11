# Programmatic SDK Examples

This directory contains examples demonstrating how to use the Agentic SDLC SDK programmatically in your Python applications.

## Examples

### 1. Basic Configuration and Setup
**File**: `01_basic_config_setup.py`

Demonstrates:
- Loading configuration from files and environment variables
- Setting up logging
- Accessing configuration values
- Creating a basic SDK instance

**Run**: `python 01_basic_config_setup.py`

### 2. Running Workflows Programmatically
**File**: `02_workflow_execution.py`

Demonstrates:
- Creating workflow configurations
- Executing workflows programmatically
- Monitoring workflow execution
- Handling workflow results

**Run**: `python 02_workflow_execution.py`

### 3. Creating and Using Agents
**File**: `03_agent_creation.py`

Demonstrates:
- Creating agents with specific roles and configurations
- Configuring agent models and parameters
- Executing agent tasks
- Managing agent lifecycle

**Run**: `python 03_agent_creation.py`

### 4. Custom Plugin Development
**File**: `04_custom_plugin.py`

Demonstrates:
- Implementing the Plugin interface
- Registering custom plugins
- Plugin initialization and shutdown
- Using plugins in workflows

**Run**: `python 04_custom_plugin.py`

## Prerequisites

Install the SDK with all dependencies:

```bash
pip install agentic-sdlc
```

For development, install with dev dependencies:

```bash
pip install agentic-sdlc[dev]
```

## Running Examples

Each example is self-contained and can be run independently:

```bash
python 01_basic_config_setup.py
python 02_workflow_execution.py
python 03_agent_creation.py
python 04_custom_plugin.py
```

## Common Patterns

### Configuration Management

```python
from agentic_sdlc import Config, get_logger

# Load configuration
config = Config()

# Access values with dot notation
log_level = config.get("log_level")

# Set values
config.set("log_level", "DEBUG")

# Get logger
logger = get_logger(__name__)
```

### Error Handling

```python
from agentic_sdlc import (
    AgenticSDLCError,
    ConfigurationError,
    ValidationError,
    PluginError
)

try:
    # SDK operations
    pass
except ConfigurationError as e:
    print(f"Configuration error: {e}")
except ValidationError as e:
    print(f"Validation error: {e}")
except AgenticSDLCError as e:
    print(f"SDK error: {e}")
```

### Logging

```python
from agentic_sdlc import setup_logging, get_logger

# Configure logging
setup_logging(level="DEBUG", log_file="app.log")

# Get logger for your module
logger = get_logger(__name__)

logger.debug("Debug message")
logger.info("Info message")
logger.warning("Warning message")
logger.error("Error message")
```

## Troubleshooting

### Import Errors

If you get import errors, ensure the SDK is installed:

```bash
pip install agentic-sdlc
python -c "import agentic_sdlc; print(agentic_sdlc.__version__)"
```

### Configuration Issues

If configuration loading fails:

1. Check that configuration files exist and are valid YAML/JSON
2. Verify environment variables are set correctly
3. Check file permissions

### Plugin Issues

If plugins fail to load:

1. Verify plugin implements the Plugin interface
2. Check plugin dependencies are installed
3. Review plugin initialization code

## Next Steps

- Read the [Getting Started Guide](../../docs/GETTING_STARTED.md)
- Explore the [API Documentation](../../docs/api/)
- Learn about [Plugin Development](../../docs/PLUGIN_DEVELOPMENT.md)
- Check the [Architecture Guide](../../docs/architecture/)
