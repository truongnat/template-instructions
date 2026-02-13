# Agentic SDLC Framework Context

This document is intended for AI Agents (Cursor, Copilot, etc.) to understand the `agentic-sdlc` framework structure and usage.

## 1. Framework Overview

`agentic-sdlc` is an AI-powered Software Development Lifecycle framework. It provides tools for:
-   **Orchestration**: Managing multiple AI agents (Developer, Reviewer, Tester).
-   **Workflows**: Defining and executing development processes.
-   **Intelligence**: Learning from execution history and providing reasoning capabilities.

> [!TIP]
> **INTEGRATIONS**: To use this framework with external tools (Gemini CLI, Copilot CLI, Kiro), see [INTEGRATIONS.md](INTEGRATIONS.md).

## 2. Directory Structure

-   `src/agentic_sdlc/`: Main source code.
    -   `core/`: Configuration, logging, exceptions.
    -   `orchestration/`: Agents, Models, Workflows.
    -   `intelligence/`: Learner, Monitor, Reasoner.
    -   `infrastructure/`: Execution engine, Automation.
-   `examples/`: Sample usage scripts.

## 3. Key Concepts & Usage

### Configuration (`agentic_sdlc.core.config`)

The `Config` class manages settings from files (YAML/JSON) and environment variables.

```python
from agentic_sdlc import Config

config = Config()
log_level = config.get("log_level", "INFO")
```

### Agents (`agentic_sdlc.orchestration.agents`)

Agents are autonomous entities with specific roles.

```python
from agentic_sdlc import create_agent

developer = create_agent(
    name="developer",
    role="software_developer",
    model_name="gpt-4"
)
```

### Workflows (`agentic_sdlc.infrastructure.automation`)

Workflows define a sequence of steps.

```python
from agentic_sdlc import WorkflowRunner
from agentic_sdlc.infrastructure.automation.workflow_engine import WorkflowStep

steps = [
    WorkflowStep(name="init", action="initialize", parameters={}),
    WorkflowStep(name="build", action="build_project", parameters={}, depends_on=["init"])
]

runner = WorkflowRunner()
results = runner.run(steps)
```

## 4. CLI Usage

The framework provides a CLI `asdlc` for common tasks.

```bash
python3 asdlc.py init --name MyProject
python3 asdlc.py agent create --name dev --role developer
python3 asdlc.py run my-workflow
```
