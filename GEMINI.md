# Agentic SDLC Framework - Gemini & Antigravity Configuration

> [!IMPORTANT]
> This file is the primary configuration for **Gemini CLI** and **Antigravity**. All AI agents reading this project MUST understand the framework structure defined below.

## Framework Overview

`agentic-sdlc` is a Skills-First AI Software Development Lifecycle framework providing:
-   **Skill Engine**: Discover, execute, and generate structured development skills.
-   **SDLC Board**: Real-time tracking of tasks, issues, and sprints.
-   **Agent Bridge**: Optimized integration for Gemini, Antigravity, and Cursor.
-   **Prompt Optimization**: Automated context management and prompt generation.

## Project Structure

```
agentic-sdlc/
├── src/agentic_sdlc/          # Main SDK
│   ├── skills/                # Skill Registry & Generation
│   ├── prompts/               # Prompt & Context Optimization
│   ├── sdlc/                  # Board & Task Tracking
│   ├── bridge/                # AgentBridge Integration
│   ├── core/                  # Config, resources, exceptions
│   └── intelligence/          # Self-review & AB Testing
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

### Agent Bridge
```python
from agentic_sdlc import AgentBridge

bridge = AgentBridge(project_dir=".")
response = bridge.process_request("Create unit tests")
print(response.skill_instructions)
```

### SDLC Tracking
```python
from agentic_sdlc import SDLCTracker

tracker = SDLCTracker(project_dir=".")
print(tracker.get_board_markdown())
```

## CLI Commands

```bash
# Initialize project
asdlc init --name MyProject

# Run a natural language request
asdlc run "Improve documentation"

# Check SDLC status
asdlc status

# Get next task to work on
asdlc task next
```

## Agent Swarm Workflow (New)

The framework now supports a "Swarm" workflow inspired by `claude-agentic-framework`. Agents should use this pattern for complex tasks.

### 1. Swarm Roles

-   **Explorer (Researcher)**: Maps the codebase, finds relevant files, and gathers context.
-   **Architect**: Designs the solution, makes high-level decisions, and creates a plan.
-   **Builder (Developer)**: Implements the solution based on the plan.
-   **Reviewer**: Reviews code for quality, security, and performance.
-   **Tester**: Writes and runs tests.

### 2. Standard Swarm Process

When handling a complex request:

1.  **Research**: Activate `Explorer` to map dependencies.
2.  **Plan**: Activate `Architect` to create a step-by-step implementation plan.
    -   *Reference `TECH_STRATEGY.md` for architectural guidelines.*
3.  **Execute**: Activate `Builder` to implement changes iteratively.
4.  **Review**: Activate `Reviewer` to check changes before finalizing.

### 3. Usage Strategy

-   **Small Fixes**: Use standard `Builder` directly.
-   **New Features**: Use `Architect -> Builder -> Reviewer`.
-   **Refactoring**: Use `Explorer -> Architect -> Builder -> Tester`.

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
