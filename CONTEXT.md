# Agentic SDLC Framework Context

This document is intended for AI Agents (Cursor, Copilot, etc.) to understand the `agentic-sdlc` framework structure and usage.

## 1. Framework Overview

`agentic-sdlc` is a Skills-First AI Software Development Lifecycle framework. It provides:
-   **Skill Engine**: Discovering, executing, and generating structured skills.
-   **SDLC Tracking**: Real-time board, task, and sprint management.
-   **Agent Bridge**: Normalized interface for Antigravity, Gemini, and Cursor.
-   **Optimized Prompts**: Context window optimization and automated prompting.

> [!TIP]
> **INTEGRATIONS**: To use this framework with external tools (Gemini CLI, Copilot CLI, Kiro), see [INTEGRATIONS.md](INTEGRATIONS.md).

## 2. Directory Structure

-   `src/agentic_sdlc/`: Main source code.
    -   `skills/`: Skill models, registry, loading, and generation.
    -   `prompts/`: Prompt generation and context optimization.
    -   `sdlc/`: Board, Task, Issue, and Sprint tracking.
    -   `bridge/`: AgentBridge and agent-specific output formatters.
    -   `core/`: Configuration, logging, exceptions, resources.
    -   `intelligence/`: Self-review, A/B testing, evaluation.
    -   `infrastructure/`: Legacy automation and lifecycle.
-   `examples/`: Sample usage scripts.

## 3. Key Concepts & Usage

### Configuration (`agentic_sdlc.core.config`)

The `Config` class manages settings from files (YAML/JSON) and environment variables.

```python
from agentic_sdlc import Config

config = Config()
log_level = config.get("log_level", "INFO")
```

### Agent Bridge (`agentic_sdlc.bridge`)

The `AgentBridge` is the primary entry point for AI agents.

```python
from agentic_sdlc import AgentBridge
from pathlib import Path

bridge = AgentBridge(project_dir=Path("."))
response = bridge.process_request("Implement user login")
```

### Skills & SDLC (`agentic_sdlc.skills`, `agentic_sdlc.sdlc`)

The framework maps requests to **Skills** and tracks progress on an **SDLC Board**.

```python
from agentic_sdlc import SkillRegistry, SDLCTracker

registry = SkillRegistry()
tracker = SDLCTracker(project_dir=Path("."))

# Discover skills
skills = registry.search("auth")

# View board status
print(tracker.get_board_markdown())
```

## 4. CLI Usage

The framework provides the `asdlc` CLI for common tasks.

```bash
asdlc init --name MyProject
asdlc run "Implement feature X"
asdlc status
asdlc task next
asdlc skill list
```
