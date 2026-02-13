# Agentic SDLC Framework - Gemini & Antigravity Configuration

> [!IMPORTANT]
> This file is the primary configuration for **Gemini CLI** and **Antigravity**. All AI agents reading this project MUST understand the framework structure defined below.

## Framework Overview

`agentic-sdlc` is an AI-powered Software Development Lifecycle framework providing:
-   **Agent Orchestration**: Multi-agent coordination (Developer, Reviewer, Tester)
-   **Workflow Automation**: Define and execute complex development workflows
-   **Intelligence Layer**: Learning, monitoring, and reasoning capabilities

## Project Structure

```
agentic-sdlc/
├── src/agentic_sdlc/          # Main SDK
│   ├── core/                  # Config, logging, exceptions
│   ├── orchestration/         # Agents, models, workflows
│   ├── intelligence/          # Learning, monitoring, reasoning
│   └── infrastructure/        # Execution engine, automation
├── examples/                  # Usage examples
├── .kiro/                     # Audit & implementation docs
├── CONTEXT.md                 # Quick reference for agents
└── INTEGRATIONS.md            # External tools integration guide
```

## Key APIs

### Configuration
```python
from agentic_sdlc import Config

config = Config()  # Auto-loads from .agentic_sdlc/config.yaml
log_level = config.get("log_level", "INFO")
config.set("custom_key", "value")
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
python3 asdlc.py init --name MyProject

# Create agent
python3 asdlc.py agent create --name dev --role developer

# Run workflow
python3 asdlc.py run my-workflow

# Check status
python3 asdlc.py status
```

## Integration with External Tools

### Gemini CLI
Use the context loader script:
```bash
./scripts/utils/load_context.sh | gemini "Explain the workflow system"
```

### Antigravity
Automatically reads this file and `CONTEXT.md`. No additional configuration needed.

### Kiro
Audit reports are in `.kiro/`. Key files:
-   `.kiro/FINAL_SUMMARY.md` - Implementation status
-   `.kiro/QUICK_REFERENCE.md` - API quick reference

## Important Files for AI Agents

1.  **CONTEXT.md** - Quick framework reference
2.  **INTEGRATIONS.md** - External tool integration guide
3.  **QUICKSTART.md** - Getting started guide
4.  **.cursorrules** - IDE agent rules
5.  **.kiro/** - Audit and implementation documentation

## Mandatory Rules for AI Agents

> [!CAUTION]
> **ALWAYS** read `CONTEXT.md` before answering questions about this framework.

> [!TIP]
> When generating code, use the SDK's public API from `agentic_sdlc` package, not internal modules.

## Support

-   **Documentation**: See `CONTEXT.md` and `.kiro/` directory
-   **Examples**: See `examples/` directory
-   **Integration**: See `INTEGRATIONS.md`
