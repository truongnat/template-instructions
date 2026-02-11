# Getting Started with Agentic SDLC

Welcome to the Agentic SDLC Kit! This guide will help you get started with the SDK.

## Installation

### Basic Installation

Install the SDK with core functionality:

```bash
pip install agentic-sdlc
```

### With CLI Support

To use the command-line interface, install with the `cli` extra:

```bash
pip install agentic-sdlc[cli]
```

### With Development Tools

For development and testing, install with the `dev` extra:

```bash
pip install agentic-sdlc[dev]
```

### From Source

To install from source for development:

```bash
git clone https://github.com/yourusername/agentic-sdlc.git
cd agentic-sdlc
pip install -e .
```

## Verify Installation

Verify that the SDK is installed correctly:

```bash
python -c "import agentic_sdlc; print(agentic_sdlc.__version__)"
```

You should see the version number printed.

## Quick Start

### 1. Basic Configuration

```python
from agentic_sdlc import Config, setup_logging, get_logger

# Setup logging
setup_logging(level="INFO")
logger = get_logger(__name__)

# Load configuration
config = Config()

# Access configuration values
log_level = config.get("log_level")
print(f"Log level: {log_level}")
```

### 2. Create an Agent

```python
from agentic_sdlc import create_agent, ModelConfig

# Create a model configuration
model = ModelConfig(
    provider="openai",
    model_name="gpt-4",
    temperature=0.7,
    max_tokens=2000
)

# Create an agent
agent = create_agent(
    name="my-agent",
    role="Assistant",
    model=model,
    system_prompt="You are a helpful assistant."
)

print(f"Created agent: {agent.name}")
```

### 3. Build a Workflow

```python
from agentic_sdlc import WorkflowBuilder

# Create a workflow
builder = WorkflowBuilder(name="my-workflow")
builder.set_description("My first workflow")

# Add steps
builder.add_step(
    name="step1",
    description="First step",
    action="initialize"
)

builder.add_step(
    name="step2",
    description="Second step",
    action="process"
)

# Build the workflow
workflow = builder.build()
print(f"Created workflow: {workflow.name}")
```

### 4. Create a Plugin

```python
from agentic_sdlc import Plugin, get_plugin_registry

class MyPlugin(Plugin):
    @property
    def name(self) -> str:
        return "my-plugin"
    
    @property
    def version(self) -> str:
        return "1.0.0"
    
    def initialize(self, config):
        print(f"Initializing {self.name}")
    
    def shutdown(self):
        print(f"Shutting down {self.name}")

# Register the plugin
registry = get_plugin_registry()
plugin = MyPlugin()
registry.register(plugin)

print(f"Registered plugin: {plugin.name}")
```

## Common Tasks

### Configure Logging

```python
from agentic_sdlc import setup_logging, get_logger

# Setup logging with custom level and file
setup_logging(
    level="DEBUG",
    log_file="app.log"
)

# Get a logger for your module
logger = get_logger(__name__)

logger.debug("Debug message")
logger.info("Info message")
logger.warning("Warning message")
logger.error("Error message")
```

### Handle Errors

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
except PluginError as e:
    print(f"Plugin error: {e}")
except AgenticSDLCError as e:
    print(f"SDK error: {e}")
```

### Use Environment Variables

Configuration can be set via environment variables with the `AGENTIC_` prefix:

```bash
export AGENTIC_LOG_LEVEL=DEBUG
export AGENTIC_PROJECT_ROOT=/path/to/project
export AGENTIC_MODELS_OPENAI_TEMPERATURE=0.9
```

Then in your code:

```python
from agentic_sdlc import Config

config = Config()
log_level = config.get("log_level")  # Will be "DEBUG" from environment
```

## Using the CLI

If you installed with CLI support, you can use the command-line interface:

```bash
# Initialize a project
agentic init

# View configuration
agentic config show

# Set a configuration value
agentic config set log_level DEBUG

# List workflows
agentic workflow list

# Run a workflow
agentic workflow run workflow-name
```

## Next Steps

- Read the [API Documentation](api/) for detailed API reference
- Explore [Examples](../examples/) for working code samples
- Learn about [Plugin Development](PLUGIN_DEVELOPMENT.md)
- Check the [Architecture Guide](architecture/) for design details
- Review the [Migration Guide](MIGRATION.md) if upgrading from v2.x

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

## Getting Help

- Check the [API Documentation](api/)
- Review [Examples](../examples/)
- Read the [Architecture Guide](architecture/)
- Check the [FAQ](guides/faq.md) (if available)

## Contributing

We welcome contributions! Please see the contributing guidelines in the repository.

## License

Agentic SDLC is licensed under the MIT License. See LICENSE file for details.
