# Plugin Development Examples

This directory contains examples demonstrating how to develop custom plugins for the Agentic SDLC SDK.

## Examples

### 1. Basic Plugin Implementation
**File**: `01_basic_plugin.py`

Demonstrates:
- Implementing the Plugin interface
- Defining plugin metadata
- Implementing initialize() and shutdown() methods
- Registering a plugin with the registry

**Run**: `python 01_basic_plugin.py`

### 2. Plugin with Configuration
**File**: `02_plugin_with_config.py`

Demonstrates:
- Accepting configuration in plugin initialization
- Validating plugin configuration
- Using configuration in plugin methods
- Handling configuration errors

**Run**: `python 02_plugin_with_config.py`

### 3. Plugin with Dependencies
**File**: `03_plugin_with_dependencies.py`

Demonstrates:
- Declaring plugin dependencies
- Loading dependent plugins
- Handling missing dependencies
- Plugin dependency resolution

**Run**: `python 03_plugin_with_dependencies.py`

### 4. Advanced Plugin Features
**File**: `04_advanced_plugin.py`

Demonstrates:
- Plugin lifecycle hooks
- Error handling and recovery
- Logging in plugins
- Plugin state management
- Plugin communication

**Run**: `python 04_advanced_plugin.py`

## Prerequisites

Install the SDK with dev dependencies:

```bash
pip install agentic-sdlc[dev]
```

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

## Plugin Development Patterns

### Configuration Validation

```python
from agentic_sdlc import Plugin, ValidationError

class ConfigurablePlugin(Plugin):
    def initialize(self, config: dict) -> None:
        # Validate required fields
        if "api_key" not in config:
            raise ValidationError("api_key is required")
        
        # Validate field types
        if not isinstance(config.get("timeout"), int):
            raise ValidationError("timeout must be an integer")
        
        # Store configuration
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
        except Exception as e:
            self.logger.error(f"Failed to initialize: {e}")
            raise PluginError(f"Initialization failed: {e}") from e
    
    def shutdown(self) -> None:
        try:
            # Cleanup
            self.logger.info(f"Shutting down {self.name}")
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

## Publishing Plugins

### Package Structure

```
my-plugin/
├── src/
│   └── my_plugin/
│       ├── __init__.py
│       └── plugin.py
├── tests/
│   └── test_plugin.py
├── pyproject.toml
└── README.md
```

### pyproject.toml

```toml
[project]
name = "agentic-sdlc-my-plugin"
version = "1.0.0"
description = "My custom plugin for Agentic SDLC"

[project.entry-points."agentic_sdlc.plugins"]
my-plugin = "my_plugin:MyPlugin"

[project.dependencies]
agentic-sdlc = ">=3.0.0"
```

### Publishing to PyPI

```bash
# Build distribution
python -m build

# Upload to PyPI
python -m twine upload dist/*
```

## Common Issues

### Plugin Not Loading

If your plugin isn't loading:

1. Check entry point is correctly configured
2. Verify plugin class implements Plugin interface
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

1. Check dependency versions in pyproject.toml
2. Use virtual environments to isolate dependencies
3. Review dependency resolution order
4. Consider using optional dependencies

## Next Steps

- Read the [Plugin Development Guide](../../docs/PLUGIN_DEVELOPMENT.md)
- Explore the [API Documentation](../../docs/api/)
- Check the [Architecture Guide](../../docs/architecture/)
- Review [Getting Started Guide](../../docs/GETTING_STARTED.md)
