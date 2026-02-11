# User Guides

This directory contains user guides for the Agentic SDLC SDK.

## Available Guides

### Getting Started

- [Getting Started](../GETTING_STARTED.md) - Installation and basic usage
- [Quick Start](quick_start.md) - Quick start guide (coming soon)

### Configuration

- [Configuration Guide](configuration.md) - Configuration management (coming soon)
- [Environment Variables](environment_variables.md) - Using environment variables (coming soon)

### Workflows

- [Workflow Guide](workflows.md) - Creating and executing workflows (coming soon)
- [Workflow Examples](workflow_examples.md) - Workflow examples (coming soon)

### Agents

- [Agent Guide](agents.md) - Creating and managing agents (coming soon)
- [Agent Examples](agent_examples.md) - Agent examples (coming soon)

### Plugins

- [Plugin Development](../PLUGIN_DEVELOPMENT.md) - Developing plugins
- [Plugin Examples](plugin_examples.md) - Plugin examples (coming soon)

### Advanced Topics

- [Architecture](../architecture/) - Architecture and design decisions
- [Migration Guide](../MIGRATION.md) - Migrating from v2.x to v3.x
- [Performance Tuning](performance_tuning.md) - Performance optimization (coming soon)
- [Troubleshooting](troubleshooting.md) - Troubleshooting guide (coming soon)

## Quick Navigation

### By Task

- **I want to get started** → [Getting Started](../GETTING_STARTED.md)
- **I want to configure the SDK** → [Configuration Guide](configuration.md) (coming soon)
- **I want to create a workflow** → [Workflow Guide](workflows.md) (coming soon)
- **I want to create an agent** → [Agent Guide](agents.md) (coming soon)
- **I want to develop a plugin** → [Plugin Development](../PLUGIN_DEVELOPMENT.md)
- **I'm upgrading from v2.x** → [Migration Guide](../MIGRATION.md)

### By Topic

- **Configuration** → [Configuration Guide](configuration.md) (coming soon)
- **Workflows** → [Workflow Guide](workflows.md) (coming soon)
- **Agents** → [Agent Guide](agents.md) (coming soon)
- **Plugins** → [Plugin Development](../PLUGIN_DEVELOPMENT.md)
- **Architecture** → [Architecture Guide](../architecture/)
- **Troubleshooting** → [Troubleshooting Guide](troubleshooting.md) (coming soon)

## Common Tasks

### Installation

```bash
# Basic installation
pip install agentic-sdlc

# With CLI support
pip install agentic-sdlc[cli]

# With development tools
pip install agentic-sdlc[dev]
```

### Basic Configuration

```python
from agentic_sdlc import Config, setup_logging

# Setup logging
setup_logging(level="INFO")

# Load configuration
config = Config()
```

### Create an Agent

```python
from agentic_sdlc import create_agent, ModelConfig

model = ModelConfig(provider="openai", model_name="gpt-4")
agent = create_agent(name="my-agent", role="Assistant", model=model)
```

### Build a Workflow

```python
from agentic_sdlc import WorkflowBuilder

builder = WorkflowBuilder(name="my-workflow")
builder.add_step(name="step1", action="initialize")
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

## FAQ

### Q: How do I install the SDK?

A: Use pip to install:
```bash
pip install agentic-sdlc
```

### Q: How do I configure the SDK?

A: Use the Config class:
```python
from agentic_sdlc import Config
config = Config()
```

### Q: How do I create an agent?

A: Use the create_agent function:
```python
from agentic_sdlc import create_agent, ModelConfig
model = ModelConfig(provider="openai", model_name="gpt-4")
agent = create_agent(name="my-agent", role="Assistant", model=model)
```

### Q: How do I develop a plugin?

A: Implement the Plugin interface and register it:
```python
from agentic_sdlc import Plugin, get_plugin_registry

class MyPlugin(Plugin):
    # Implement required methods
    pass

registry = get_plugin_registry()
registry.register(MyPlugin())
```

### Q: How do I upgrade from v2.x?

A: See the [Migration Guide](../MIGRATION.md) for detailed instructions.

## Getting Help

- Check the [API Documentation](../api/)
- Review [Examples](../../examples/)
- Read the [Getting Started Guide](../GETTING_STARTED.md)
- Check the [Architecture Guide](../architecture/)
- Open an issue on GitHub

## Contributing

We welcome contributions! Please see the contributing guidelines in the repository.
