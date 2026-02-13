# External Tools Integration Guide

This guide explains how to use `agentic-sdlc` with various AI tools and CLIs.

## 1. Gemini CLI

To use Gemini CLI with this project, you should feed it the project context.

### Setup
Ensure you have the `scripts/utils/load_context.sh` script (created below).

### Usage
Run Gemini with full project context:

```bash
./scripts/utils/load_context.sh | gemini "Explain the agent architecture in this project"
```

Or for specific tasks:

```bash
./scripts/utils/load_context.sh | gemini "Generate a new Workflow for database migration"
```

## 2. GitHub Copilot CLI

Copilot CLI often needs help understanding the specific framework structure.

### Usage
When using `gh cp` (or `??`), explicitly reference the context file if possible, or rely on the open `CONTEXT.md`.

```bash
# Best practice: Keep CONTEXT.md open in your editor
gh copilot suggest "How do I create a new Agent using the SDK?"
```

## 3. Antigravity & AI IDEs (Cursor/Windsurf)

These tools are configured to automatically detect `.cursorrules` and `CONTEXT.md`.

*   **Antigravity**: Will automatically index `CONTEXT.md`.
*   **Cursor**: Rules in `.cursorrules` force the agent to read `CONTEXT.md`.
*   **Kiro**: The `.kiro` directory contains audit logs. Agents can read `.kiro/FINAL_SUMMARY.md` to understand the implementation status.

## 4. Helper Scripts

### `scripts/utils/load_context.sh`

This script aggregates the most important context files into a single stream for LLM consumption.

It typically includes:
-   `CONTEXT.md`
-   `QUICKSTART.md`
-   `src/agentic_sdlc/core/config.py` (Configuration definition)
-   `src/agentic_sdlc/orchestration/agents/base.py` (Agent definition)
