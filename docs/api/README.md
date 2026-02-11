# API Documentation

This directory contains the API documentation for the Agentic SDLC SDK.

## Overview

The Agentic SDLC SDK provides a comprehensive API for building AI-powered software development workflows. The API is organized into several modules:

- **Core**: Configuration, logging, exceptions, and utilities
- **Infrastructure**: Workflow automation, bridging, and lifecycle management
- **Intelligence**: Learning, monitoring, reasoning, and collaboration
- **Orchestration**: Agent management, model configuration, and workflow coordination
- **Plugins**: Plugin system for extensibility

## Quick Links

### Core Module

- [Configuration](core/config.md) - Configuration management
- [Exceptions](core/exceptions.md) - Exception hierarchy
- [Logging](core/logging.md) - Logging configuration
- [Types](core/types.md) - Data types and models

### Infrastructure Module

- [Workflow Engine](infrastructure/workflow_engine.md) - Workflow automation
- [Execution Engine](infrastructure/execution_engine.md) - Task execution
- [Bridge Registry](infrastructure/bridge_registry.md) - Integration bridges
- [Lifecycle Manager](infrastructure/lifecycle_manager.md) - Lifecycle management

### Intelligence Module

- [Learner](intelligence/learner.md) - Self-learning capabilities
- [Monitor](intelligence/monitor.md) - System monitoring
- [Reasoner](intelligence/reasoner.md) - Decision-making logic
- [Collaborator](intelligence/collaborator.md) - Multi-agent collaboration

### Orchestration Module

- [Agent](orchestration/agent.md) - Agent definitions
- [Agent Registry](orchestration/agent_registry.md) - Agent management
- [Model Client](orchestration/model_client.md) - Model configuration
- [Workflow](orchestration/workflow.md) - Workflow definitions
- [Workflow Builder](orchestration/workflow_builder.md) - Workflow construction
- [Coordinator](orchestration/coordinator.md) - Multi-agent coordination

### Plugins Module

- [Plugin Interface](plugins/plugin.md) - Plugin base class
- [Plugin Registry](plugins/plugin_registry.md) - Plugin management

## Usage Examples

### Basic Configuration

```python
from agentic_sdlc import Config, setup_logging, get_logger

# Setup logging
setup_logging(level="INFO")
logger = get_logger(__name__)

# Load configuration
config = Config()
log_level = config.get("log_level")
```

### Create an Agent

```python
from agentic_sdlc import create_agent, ModelConfig

model = ModelConfig(
    provider="openai",
    model_name="gpt-4",
    temperature=0.7
)

agent = create_agent(
    name="my-agent",
    role="Assistant",
    model=model
)
```

### Build a Workflow

```python
from agentic_sdlc import WorkflowBuilder

builder = WorkflowBuilder(name="my-workflow")
builder.add_step(name="step1", action="initialize")
builder.add_step(name="step2", action="process")
workflow = builder.build()
```

### Create a Plugin

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
        pass
    
    def shutdown(self):
        pass

registry = get_plugin_registry()
registry.register(MyPlugin())
```

## API Reference

For detailed API reference, see the individual module documentation files.

## Type Hints

All public API functions and methods include complete type hints. This enables:

- IDE autocompletion
- Static type checking with mypy
- Better documentation
- Improved code quality

## Error Handling

The SDK defines a hierarchy of exceptions for different error types:

```python
from agentic_sdlc import (
    AgenticSDLCError,      # Base exception
    ConfigurationError,    # Configuration errors
    ValidationError,       # Validation errors
    PluginError,          # Plugin errors
    WorkflowError,        # Workflow errors
    AgentError,           # Agent errors
    ModelError            # Model errors
)
```

## Logging

The SDK uses Python's standard logging module:

```python
from agentic_sdlc import setup_logging, get_logger

# Configure logging
setup_logging(level="DEBUG", log_file="app.log")

# Get logger for your module
logger = get_logger(__name__)
logger.info("Message")
```

## Configuration

Configuration can be loaded from files, environment variables, or set programmatically:

```python
from agentic_sdlc import Config

config = Config()

# Get values
value = config.get("key.nested")

# Set values
config.set("key.nested", value)

# Validate
config.validate()
```

## Plugins

Extend the SDK with custom plugins:

```python
from agentic_sdlc import Plugin, get_plugin_registry

class MyPlugin(Plugin):
    # Implement required interface
    pass

registry = get_plugin_registry()
registry.register(MyPlugin())
```

## Next Steps

- Read the [Getting Started Guide](../GETTING_STARTED.md)
- Explore [Examples](../../examples/)
- Learn about [Plugin Development](../PLUGIN_DEVELOPMENT.md)
- Check the [Architecture Guide](../architecture/)
- Review the [Migration Guide](../MIGRATION.md)
