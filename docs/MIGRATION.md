# Migration Guide: v2.x to v3.x

This guide helps you migrate your code from Agentic SDLC v2.x to v3.x.

## Overview

Version 3.0.0 introduces a major reorganization of the SDK structure to follow Python best practices. The core functionality remains the same, but imports and some APIs have changed.

### Key Changes

1. **New package structure** - Code reorganized into logical modules
2. **Unified public API** - Single entry point for all public exports
3. **Dependency management** - Vendored dependencies moved to pyproject.toml
4. **CLI separation** - CLI is now optional and separate from core SDK
5. **Backward compatibility** - Old imports still work with deprecation warnings

## Breaking Changes

### 1. Import Paths

**v2.x (Old)**:
```python
from agentic_sdlc.infrastructure.autogen.agents import create_agent_by_role
from agentic_sdlc.intelligence.self_learning.learner import Learner
from agentic_sdlc.core.config import Config
```

**v3.x (New)**:
```python
from agentic_sdlc import create_agent, Learner, Config
```

### 2. Configuration API

**v2.x (Old)**:
```python
from agentic_sdlc.core.config import load_config

config = load_config("config.yaml")
value = config["key"]["nested"]
```

**v3.x (New)**:
```python
from agentic_sdlc import Config

config = Config()
value = config.get("key.nested")  # Dot notation support
```

### 3. Agent Creation

**v2.x (Old)**:
```python
from agentic_sdlc.infrastructure.autogen.agents import create_agent_by_role

agent = create_agent_by_role(role="developer")
```

**v3.x (New)**:
```python
from agentic_sdlc import create_agent, ModelConfig

model = ModelConfig(provider="openai", model_name="gpt-4")
agent = create_agent(name="dev-agent", role="developer", model=model)
```

### 4. Workflow Execution

**v2.x (Old)**:
```python
from agentic_sdlc.infrastructure.autogen.workflow import WorkflowEngine

engine = WorkflowEngine()
result = engine.execute("workflow-name")
```

**v3.x (New)**:
```python
from agentic_sdlc import WorkflowEngine, WorkflowBuilder

builder = WorkflowBuilder(name="my-workflow")
builder.add_step(name="step1", action="initialize")
workflow = builder.build()

engine = WorkflowEngine()
# Execute workflow
```

### 5. Plugin System

**v2.x (Old)**:
```python
from agentic_sdlc.plugins.base import BasePlugin

class MyPlugin(BasePlugin):
    def execute(self):
        pass
```

**v3.x (New)**:
```python
from agentic_sdlc import Plugin

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
```

## Migration Steps

### Step 1: Update Imports

Replace old import paths with new public API imports:

```python
# Old
from agentic_sdlc.infrastructure.autogen.agents import create_agent_by_role
from agentic_sdlc.intelligence.self_learning.learner import Learner

# New
from agentic_sdlc import create_agent, Learner
```

### Step 2: Update Configuration

Update configuration loading and access:

```python
# Old
from agentic_sdlc.core.config import load_config
config = load_config("config.yaml")
log_level = config["log_level"]

# New
from agentic_sdlc import Config
config = Config()
log_level = config.get("log_level")
```

### Step 3: Update Agent Creation

Update agent creation to use new API:

```python
# Old
from agentic_sdlc.infrastructure.autogen.agents import create_agent_by_role
agent = create_agent_by_role(role="developer")

# New
from agentic_sdlc import create_agent, ModelConfig
model = ModelConfig(provider="openai", model_name="gpt-4")
agent = create_agent(name="dev-agent", role="developer", model=model)
```

### Step 4: Update Workflow Code

Update workflow creation and execution:

```python
# Old
from agentic_sdlc.infrastructure.autogen.workflow import WorkflowEngine
engine = WorkflowEngine()
result = engine.execute("workflow-name")

# New
from agentic_sdlc import WorkflowEngine, WorkflowBuilder
builder = WorkflowBuilder(name="my-workflow")
builder.add_step(name="step1", action="initialize")
workflow = builder.build()
engine = WorkflowEngine()
```

### Step 5: Update Plugins

Update plugin implementations:

```python
# Old
from agentic_sdlc.plugins.base import BasePlugin

class MyPlugin(BasePlugin):
    def execute(self):
        pass

# New
from agentic_sdlc import Plugin

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
```

### Step 6: Update Error Handling

Update exception handling:

```python
# Old
from agentic_sdlc.core.exceptions import SDLCError

try:
    # code
except SDLCError as e:
    pass

# New
from agentic_sdlc import AgenticSDLCError, ConfigurationError, ValidationError

try:
    # code
except ConfigurationError as e:
    pass
except ValidationError as e:
    pass
except AgenticSDLCError as e:
    pass
```

## Deprecation Warnings

During the migration period, old imports still work but emit deprecation warnings:

```python
# This still works but emits a warning
from agentic_sdlc.infrastructure.autogen.agents import create_agent_by_role

# Warning: Importing create_agent_by_role from agentic_sdlc.infrastructure.autogen.agents 
# is deprecated. Use 'from agentic_sdlc import create_agent' instead.
```

To suppress warnings during testing:

```python
import warnings
warnings.filterwarnings("ignore", category=DeprecationWarning)
```

## Installation Changes

### CLI Dependencies

In v3.x, CLI dependencies are optional:

```bash
# Core SDK only
pip install agentic-sdlc

# With CLI support
pip install agentic-sdlc[cli]

# With development tools
pip install agentic-sdlc[dev]
```

### Vendored Dependencies

In v2.x, dependencies were vendored in `lib/`. In v3.x, they're declared in `pyproject.toml`:

```bash
# v2.x - dependencies in lib/
pip install agentic-sdlc

# v3.x - dependencies from PyPI
pip install agentic-sdlc
```

## Configuration File Changes

Configuration file format remains the same, but loading has changed:

```yaml
# config.yaml - format unchanged
project_root: /path/to/project
log_level: INFO
log_file: agentic.log

models:
  openai:
    provider: openai
    model_name: gpt-4
    temperature: 0.7
```

Loading code:

```python
# v2.x
from agentic_sdlc.core.config import load_config
config = load_config("config.yaml")

# v3.x
from agentic_sdlc import Config
config = Config()  # Automatically loads from default locations
```

## API Changes Summary

| v2.x | v3.x | Notes |
|------|------|-------|
| `from agentic_sdlc.infrastructure.autogen.agents import create_agent_by_role` | `from agentic_sdlc import create_agent` | New API requires model config |
| `from agentic_sdlc.core.config import Config` | `from agentic_sdlc import Config` | Same class, new import path |
| `config["key"]["nested"]` | `config.get("key.nested")` | Dot notation support |
| `BasePlugin` | `Plugin` | New interface with initialize/shutdown |
| `SDLCError` | `AgenticSDLCError` | Renamed base exception |
| `from agentic_sdlc.plugins.base import BasePlugin` | `from agentic_sdlc import Plugin` | New import path |

## Testing Migration

Update your tests to use new imports:

```python
# Old
from agentic_sdlc.infrastructure.autogen.agents import create_agent_by_role
from agentic_sdlc.core.config import Config

# New
from agentic_sdlc import create_agent, Config, ModelConfig

def test_agent_creation():
    model = ModelConfig(provider="openai", model_name="gpt-4")
    agent = create_agent(name="test-agent", role="tester", model=model)
    assert agent.name == "test-agent"
```

## Troubleshooting

### Import Errors

If you get import errors after upgrading:

1. Check that you're using the new import paths
2. Verify the SDK is installed: `pip install --upgrade agentic-sdlc`
3. Check for typos in import statements

### Configuration Issues

If configuration loading fails:

1. Verify configuration file exists and is valid YAML/JSON
2. Check file permissions
3. Use `config.validate()` to check configuration

### Plugin Issues

If plugins fail to load:

1. Verify plugin implements the new `Plugin` interface
2. Check that `initialize()` and `shutdown()` methods are implemented
3. Review plugin dependencies

## Getting Help

- Check the [API Documentation](api/)
- Review [Examples](../examples/)
- Read the [Getting Started Guide](GETTING_STARTED.md)
- Check the [Architecture Guide](architecture/)

## Rollback

If you need to rollback to v2.x:

```bash
pip install agentic-sdlc==2.7.5
```

Note: v2.x and v3.x have different APIs, so code changes will be needed.

## Support

For issues or questions about migration, please:

1. Check the documentation
2. Review the examples
3. Open an issue on GitHub
4. Contact the maintainers

## Timeline

- **v3.0.0** (Current): New structure, old imports deprecated
- **v3.1.0+**: Continued support for old imports with warnings
- **v4.0.0** (Future): Old imports removed

During the deprecation period (v3.x), old imports continue to work with warnings. Plan your migration accordingly.
