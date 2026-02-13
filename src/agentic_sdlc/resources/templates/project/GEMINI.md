# Agentic SDLC Framework - AI Agent Configuration

> [!IMPORTANT]
> This file is the primary configuration for **Gemini CLI** and **Antigravity**. All AI agents reading this project MUST understand the framework structure defined below.

## Framework Overview

`agentic-sdlc` is an AI-powered Software Development Lifecycle framework providing:
-   **Agent Orchestration**: Multi-agent coordination (Developer, Reviewer, Tester)
-   **Workflow Automation**: Define and execute complex development workflows
-   **Intelligence Layer**: Learning, monitoring, and reasoning capabilities

## Key APIs

### Configuration
```python
from agentic_sdlc import Config

config = Config()
log_level = config.get("log_level", "INFO")
```

### Agent Creation
```python
from agentic_sdlc import create_agent

developer = create_agent(
    name="developer",
    role="software_developer",
    model_name="gpt-4"
)
```

### Workflow Execution
```python
from agentic_sdlc import WorkflowRunner
from agentic_sdlc.infrastructure.automation.workflow_engine import WorkflowStep

steps = [
    WorkflowStep(name="init", action="initialize", parameters={}),
    WorkflowStep(name="build", action="build", parameters={}, depends_on=["init"])
]

runner = WorkflowRunner()
results = runner.run(steps)
```

## CLI Commands

```bash
# Initialize project
python3 -m agentic_sdlc.cli init --name MyProject

# Create agent
python3 -m agentic_sdlc.cli agent create --name dev --role developer

# Run workflow
python3 -m agentic_sdlc.cli run my-workflow
```

## Important Files for AI Agents

1.  **CONTEXT.md** - Quick framework reference
2.  **.cursorrules** - IDE agent rules (if using Cursor)

## Mandatory Rules for AI Agents

> [!CAUTION]
> **ALWAYS** read `CONTEXT.md` before answering questions about this framework.

> [!TIP]
> When generating code, use the SDK's public API from `agentic_sdlc` package, not internal modules.
