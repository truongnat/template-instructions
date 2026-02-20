# Agentic SDLC Framework - AI Agent Configuration

> [!IMPORTANT]
> This file is the primary configuration for **Gemini CLI** and **Antigravity**. All AI agents reading this project MUST read this file first.

## What is Agentic SDLC?

A CLI tool (`asdlc`) that helps AI agents understand your project better. It provides:
-   **Domain Detection**: Automatically classifies tasks (Frontend, Backend, DevOps, etc.)
-   **RAG Research**: Searches your codebase semantically before generating code
-   **Swarm Agents**: Coordinates Developer, Reviewer, and Tester agents
-   **Multi-LLM**: Works with Gemini, OpenAI, Anthropic, or local Ollama

## CLI Commands

```bash
# Process a task request
asdlc run "Implement user authentication"

# Check SDLC board status
asdlc status

# Get next task
asdlc task next
```

## Quick API Usage

```python
from agentic_sdlc import AgentBridge
from pathlib import Path

bridge = AgentBridge(project_dir=Path("."))
response = bridge.process_request_enhanced("Add pagination to the API")
```

## Key Files

| File | Purpose |
|------|---------|
| `CONTEXT.md` | Project architecture overview for AI agents |
| `.agentic_sdlc/config.yaml` | Project configuration |
| `.agent/workflows/` | Antigravity workflow definitions |

## Mandatory Rules

> [!CAUTION]
> **ALWAYS** read `CONTEXT.md` before making changes to this project.

> [!TIP]
> Use the public API: `from agentic_sdlc import AgentBridge, LLMRouter, KnowledgeBase`
