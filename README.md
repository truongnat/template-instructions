# 📦 Agentic SDLC - AI-Powered Software Development Kit
![Version](https://img.shields.io/badge/version-3.0.0-blue.svg)
![Build](https://img.shields.io/badge/build-passing-brightgreen.svg)
![License](https://img.shields.io/badge/license-MIT-green.svg)

> Professional SDK for AI-powered software development. Clean architecture, extensible design, and production-ready.

**Agentic SDLC** is a Python SDK that provides a comprehensive framework for building AI-powered development tools. It features a clean public API, modular architecture, and support for custom extensions through plugins.

---

## 🚀 Quick Start

### Installation

**Core SDK** (without CLI):
```bash
pip install agentic-sdlc
```

**With CLI tools**:
```bash
pip install agentic-sdlc[cli]
```

**Development**:
```bash
pip install -e ".[dev]"
```

### Basic Usage

```python
from agentic_sdlc import AgentBridge
from pathlib import Path

# Create bridge (main entry point for agents)
bridge = AgentBridge(project_dir=Path("."))

# Process a natural language request
response = bridge.process_request("Create a FastAPI hello world")

if response.success:
    print(f"Task ID: {response.task_id}")
    print(f"Instructions: {response.skill_instructions}")
```

### CLI Usage

```bash
# Initialize a Skills-First project
asdlc init --name MyProject

# Run a task request
asdlc run "Add unit tests for the auth module"

# View SDLC board status
asdlc status

# Manage skills
asdlc skill list
asdlc skill generate "A skill to deploy to AWS"
```

---

## 📚 Architecture

### Package Structure

```
agentic_sdlc/
├── core/              # Config, exceptions, logging, resources
├── skills/            # Skill engine (Registry, Generator, Loader)
├── prompts/           # Prompt generation and context optimization
├── sdlc/              # SDLC tracking (Board, Task, Sprint)
├── bridge/            # Agent integration (AgentBridge, Formatters)
├── intelligence/      # Self-review, A/B testing, reasoning
├── plugins/           # Plugin system and registry
└── cli/               # asdlc command-line interface
```

### Public API

The SDK exposes a clean public API through the top-level `agentic_sdlc` module:

```python
# Core
from agentic_sdlc import (
    Config, load_config, get_config,
    AgenticSDLCError, ConfigurationError, ValidationError,
    setup_logging, get_logger
)

# Skills & Prompts (New)
from agentic_sdlc import (
    Skill, SkillRegistry, SkillGenerator,
    PromptGenerator, ContextOptimizer
)

# SDLC & Bridge (New)
from agentic_sdlc import (
    Board, SDLCTracker, Task, Sprint,
    AgentBridge, AgentResponse
)

# Intelligence & Plugins
from agentic_sdlc import (
    SelfReviewEngine, ABScorer,
    Plugin, PluginRegistry, get_plugin_registry
)
```

---

## 🔧 Configuration

Configuration can be loaded from files, environment variables, or set programmatically:

```python
from agentic_sdlc import Config

# Load from file
config = Config("config.yaml")

# Get values with dot notation
log_level = config.get("log_level")
model_name = config.get("models.openai.model_name")

# Set values
config.set("log_level", "DEBUG")

# Validate configuration
config.validate()
```

---

## 🔌 Plugin System

Extend the SDK with custom plugins:

```python
from agentic_sdlc import Plugin, get_plugin_registry

class MyPlugin(Plugin):
    @property
    def name(self) -> str:
        return "my-plugin"
    
    @property
    def version(self) -> str:
        return "1.0.0"
    
    def initialize(self, config: dict) -> None:
        print(f"Initializing {self.name}")
    
    def shutdown(self) -> None:
        print(f"Shutting down {self.name}")

# Register plugin
registry = get_plugin_registry()
registry.register(MyPlugin())
```

---

## 📖 Documentation

- **[Getting Started](docs/GETTING_STARTED.md)** - Installation and basic usage
- **[Migration Guide](docs/MIGRATION.md)** - Upgrading from v2.x to v3.x
- **[Plugin Development](docs/PLUGIN_DEVELOPMENT.md)** - Creating custom plugins
- **[API Reference](docs/api/)** - Complete API documentation
- **[Architecture](docs/architecture/)** - Design and architecture decisions

---

## 💡 Examples

See the `examples/` directory for complete working examples:

- **Programmatic SDK usage**: `examples/programmatic/`
- **CLI usage**: `examples/cli/`
- **Plugin development**: `examples/plugins/`

---

## 🧪 Testing

Run the test suite:

```bash
# All tests
pytest

# Unit tests only
pytest tests/unit/

# Property-based tests
pytest tests/property/

# With coverage
pytest --cov=agentic_sdlc --cov-report=html
```

---

## 🔄 What's New in v3.0.0

### Breaking Changes
- Reorganized package structure (moved to `src/` layout)
- Removed vendored dependencies from `lib/` directory
- CLI is now optional (install with `[cli]` extra)
- Old import paths are deprecated (use new public API)

### New Features
- Clean public API with explicit exports
- Plugin system for extensibility
- Comprehensive configuration management
- Type hints throughout the codebase
- Property-based testing for correctness validation

### Migration
See [MIGRATION.md](docs/MIGRATION.md) for detailed migration instructions from v2.x.

---

## 📄 License
MIT License. See [LICENSE](LICENSE) for details.

---
Developed by **Dao Quang Truong** | [GitHub](https://github.com/truongnat/agentic-sdlc)