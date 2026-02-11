# Plugin Development Guide

This guide explains how to develop plugins for the Agentic SDLC SDK.

## Overview

Plugins allow you to extend the SDK with custom functionality without modifying core code. The plugin system provides:

- **Plugin Interface**: Standard interface all plugins must implement
- **Plugin Registry**: Central registry for managing plugins
- **Lifecycle Management**: Initialize and shutdown hooks
- **Error Isolation**: Plugin failures don't crash the SDK
- **Configuration**: Pass configuration to plugins during initialization

## Plugin Interface

All plugins must implement the `Plugin` interface:

```python
from agentic_sdlc import Plugin

class MyPlugin(Plugin):
    @property
    def name(self) -> str:
        """Return plugin name."""
        return "my-plugin"
    
    @property
    def version(self) -> str:
        """Return plugin version."""
        return "1.0.0"
    
    def initialize(self, config: dict) -> None:
        """Initialize plugin with configuration."""
        pass
    
    def shutdown(self) -> None:
        """Clean up plugin resources."""
        pass
```

### Required Properties

- **name**: Unique plugin identifier (string)
- **version**: Plugin version following semantic versioning (string)

### Required Methods

- **initialize(config)**: Called when plugin is loaded
  - Receives configuration dictionary
  - Should validate configuration
  - Should raise PluginError if initialization fails

- **shutdown()**: Called when plugin is unloaded
  - Should clean up resources
  - Should handle errors gracefully

## Basic Plugin Example

```python
from agentic_sdlc import Plugin, get_logger

class LoggingPlugin(Plugin):
    """Simple logging plugin."""
    
    def __init__(self):
        self.logger = get_logger(__name__)
        self.config = {}
    
    @property
    def name(self) -> str:
        return "logging-plugin"
    
    @property
    def version(self) -> str:
        return "1.0.0"
    
    def initialize(self, config: dict) -> None:
        """Initialize the plugin."""
        self.logger.info(f"Initializing {self.name}")
        self.config = config
        self.logger.info(f"Plugin {self.name} initialized")
    
    def shutdown(self) -> None:
        """Shutdown the plugin."""
        self.logger.info(f"Shutting down {self.name}")
```

## Plugin Registration

### Programmatic Registration

```python
from agentic_sdlc import get_plugin_registry
from my_plugin import MyPlugin

# Get the plugin registry
registry = get_plugin_registry()

# Create and register plugin
plugin = MyPlugin()
registry.register(plugin)

# Use plugin
my_plugin = registry.get("my-plugin")
```

### Entry Point Registration

Plugins can be registered via setuptools entry points in `pyproject.toml`:

```toml
[project.entry-points."agentic_sdlc.plugins"]
my-plugin = "my_plugin:MyPlugin"
```

Then install the plugin package:

```bash
pip install my-plugin-package
```

The plugin will be automatically discovered and loaded.

## Advanced Plugin Features

### Configuration Validation

```python
from agentic_sdlc import Plugin, PluginError, ValidationError

class ConfigurablePlugin(Plugin):
    def initialize(self, config: dict) -> None:
        # Validate required fields
        if "api_key" not in config:
            raise PluginError("api_key is required")
        
        # Validate field types
        if not isinstance(config.get("timeout"), int):
            raise ValidationError("timeout must be an integer")
        
        # Validate field values
        if config.get("timeout", 0) <= 0:
            raise ValidationError("timeout must be positive")
        
        self.config = config
```

### Error Handling

```python
from agentic_sdlc import Plugin, PluginError, get_logger

class RobustPlugin(Plugin):
    def __init__(self):
        self.logger = get_logger(__name__)
    
    def initialize(self, config: dict) -> None:
        try:
            # Plugin initialization
            self.logger.info(f"Initializing {self.name}")
            # ... initialization code ...
        except Exception as e:
            self.logger.error(f"Failed to initialize: {e}")
            raise PluginError(f"Initialization failed: {e}") from e
    
    def shutdown(self) -> None:
        try:
            # Cleanup
            self.logger.info(f"Shutting down {self.name}")
            # ... cleanup code ...
        except Exception as e:
            self.logger.error(f"Error during shutdown: {e}")
```

### Logging

```python
from agentic_sdlc import Plugin, get_logger

class LoggingPlugin(Plugin):
    def __init__(self):
        self.logger = get_logger(__name__)
    
    def initialize(self, config: dict) -> None:
        self.logger.debug(f"Initializing with config: {config}")
        self.logger.info(f"Plugin {self.name} v{self.version} initialized")
    
    def shutdown(self) -> None:
        self.logger.info(f"Plugin {self.name} shutting down")
```

### State Management

```python
from datetime import datetime
from agentic_sdlc import Plugin

class StatefulPlugin(Plugin):
    def __init__(self):
        self.state = {}
        self.initialized = False
    
    def initialize(self, config: dict) -> None:
        self.state = {
            "config": config,
            "created_at": datetime.now(),
            "status": "initialized"
        }
        self.initialized = True
    
    def shutdown(self) -> None:
        self.state["status"] = "shutdown"
        self.initialized = False
    
    def get_state(self) -> dict:
        return self.state.copy()
```

### Plugin Communication

```python
from agentic_sdlc import Plugin, get_plugin_registry

class CommunicatingPlugin(Plugin):
    def initialize(self, config: dict) -> None:
        # Get other plugins
        registry = get_plugin_registry()
        other_plugin = registry.get("other-plugin")
        
        if other_plugin:
            # Communicate with other plugin
            pass
```

## Testing Plugins

### Unit Testing

```python
import pytest
from agentic_sdlc import get_plugin_registry
from my_plugin import MyPlugin

def test_plugin_initialization():
    plugin = MyPlugin()
    config = {"key": "value"}
    
    plugin.initialize(config)
    
    assert plugin.name == "my-plugin"
    assert plugin.version == "1.0.0"

def test_plugin_registration():
    registry = get_plugin_registry()
    plugin = MyPlugin()
    
    registry.register(plugin)
    
    retrieved = registry.get("my-plugin")
    assert retrieved is plugin

def test_plugin_shutdown():
    plugin = MyPlugin()
    plugin.initialize({})
    
    plugin.shutdown()
    
    # Verify cleanup
    assert not plugin.initialized
```

### Integration Testing

```python
def test_plugin_in_workflow():
    from agentic_sdlc import WorkflowEngine
    
    # Create workflow with plugin
    engine = WorkflowEngine()
    plugin = MyPlugin()
    
    # Register plugin
    registry = get_plugin_registry()
    registry.register(plugin)
    
    # Execute workflow
    result = engine.run("test-workflow")
    
    assert result.success
```

### Error Testing

```python
import pytest
from agentic_sdlc import PluginError
from my_plugin import MyPlugin

def test_plugin_initialization_error():
    plugin = MyPlugin()
    invalid_config = {"invalid": "config"}
    
    with pytest.raises(PluginError):
        plugin.initialize(invalid_config)
```

## Plugin Package Structure

```
my-plugin/
├── src/
│   └── my_plugin/
│       ├── __init__.py
│       ├── plugin.py
│       └── utils.py
├── tests/
│   ├── test_plugin.py
│   └── test_integration.py
├── pyproject.toml
├── README.md
└── LICENSE
```

## pyproject.toml Configuration

```toml
[project]
name = "agentic-sdlc-my-plugin"
version = "1.0.0"
description = "My custom plugin for Agentic SDLC"
authors = [{name = "Your Name", email = "your.email@example.com"}]
license = {text = "MIT"}

[project.dependencies]
agentic-sdlc = ">=3.0.0"

[project.optional-dependencies]
dev = [
    "pytest>=7.0.0",
    "pytest-cov>=4.0.0",
]

[project.entry-points."agentic_sdlc.plugins"]
my-plugin = "my_plugin:MyPlugin"

[build-system]
requires = ["setuptools>=69.0.0", "wheel>=0.42.0"]
build-backend = "setuptools.build_meta"
```

## Publishing Plugins

### Build Distribution

```bash
python -m build
```

This creates:
- `dist/agentic-sdlc-my-plugin-1.0.0.tar.gz` (source distribution)
- `dist/agentic-sdlc_my_plugin-1.0.0-py3-none-any.whl` (wheel)

### Upload to PyPI

```bash
python -m twine upload dist/*
```

### Install from PyPI

```bash
pip install agentic-sdlc-my-plugin
```

## Best Practices

### 1. Error Handling

Always handle errors gracefully:

```python
def initialize(self, config: dict) -> None:
    try:
        # initialization code
    except Exception as e:
        raise PluginError(f"Initialization failed: {e}") from e
```

### 2. Logging

Use the SDK's logging system:

```python
from agentic_sdlc import get_logger

logger = get_logger(__name__)
logger.info("Plugin initialized")
```

### 3. Configuration Validation

Validate configuration early:

```python
def initialize(self, config: dict) -> None:
    if not isinstance(config, dict):
        raise PluginError("Configuration must be a dictionary")
    
    required_keys = ["api_key", "timeout"]
    for key in required_keys:
        if key not in config:
            raise PluginError(f"Missing required config: {key}")
```

### 4. Resource Cleanup

Always clean up resources in shutdown:

```python
def shutdown(self) -> None:
    if hasattr(self, "connection"):
        self.connection.close()
    if hasattr(self, "thread"):
        self.thread.join()
```

### 5. Documentation

Document your plugin:

```python
class MyPlugin(Plugin):
    """My custom plugin for Agentic SDLC.
    
    This plugin provides [description of functionality].
    
    Configuration:
        api_key (str): API key for authentication
        timeout (int): Request timeout in seconds
    
    Example:
        >>> plugin = MyPlugin()
        >>> plugin.initialize({"api_key": "...", "timeout": 30})
    """
```

## Common Issues

### Plugin Not Loading

If your plugin isn't loading:

1. Check entry point is correctly configured in `pyproject.toml`
2. Verify plugin class implements `Plugin` interface
3. Check plugin dependencies are installed
4. Review plugin initialization code

### Configuration Errors

If configuration validation fails:

1. Verify all required fields are provided
2. Check field types match expectations
3. Review validation error messages
4. Test with minimal configuration first

### Dependency Issues

If plugin dependencies conflict:

1. Check dependency versions in `pyproject.toml`
2. Use virtual environments to isolate dependencies
3. Review dependency resolution order
4. Consider using optional dependencies

## Examples

See the [examples/plugins/](../examples/plugins/) directory for complete plugin examples:

- `01_basic_plugin.py` - Basic plugin implementation
- `02_plugin_with_config.py` - Plugin with configuration
- `03_plugin_with_dependencies.py` - Plugin with dependencies
- `04_advanced_plugin.py` - Advanced plugin features

## Next Steps

- Review the [API Documentation](api/)
- Check the [Getting Started Guide](GETTING_STARTED.md)
- Explore the [Architecture Guide](architecture/)
- Review [Examples](../examples/plugins/)
