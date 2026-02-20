# Agentic SDLC Framework Context

This document is intended for AI Agents (Cursor, Copilot, Antigravity, etc.) to understand the `agentic-sdlc` framework structure and usage.

## 1. Framework Overview

`agentic-sdlc` is a modular SDK for building AI-powered development agents. It features a sophisticated E2E pipeline:
-   **Domain Detection**: Classifies tasks (Frontend, Backend, DevOps, etc.).
-   **RAG Research**: Semantic search using ChromaDB + web research.
-   **Prompt Lab**: A/B optimization for tasks.
-   **Swarm Intelligence**: Multi-agent coordination (Developer, Reviewer, Tester).
-   **Self-Learning**: Analyzes outcomes to improve future runs.

## 2. Directory Structure

-   `src/agentic_sdlc/`: Main source code.
    -   `bridge/`: `AgentBridge` - Primary E2E entry point.
    -   `swarm/`: Multi-agent orchestrator, message bus, and agent roles.
    -   `knowledge/`: RAG implementation (KnowledgeBase, VectorStore, Embeddings).
    -   `core/`: **Config**, **Domain Engine**, **LLM Routing**, and **Artifacts**.
    -   `prompts/`: `PromptLab` and prompt generation logic.
    -   `intelligence/`: `SelfImprovementEngine` and `Reasoner`.
    -   `skills/`: Skill registry and generation.
-   `examples/`: Working implementation patterns.

## 3. Key Entry Points

### Agent Bridge (Primary)
The `AgentBridge` orchestrates all components. Use `process_request_enhanced` for the full pipeline.

```python
from agentic_sdlc import AgentBridge
from pathlib import Path

bridge = AgentBridge(project_dir=Path("."))
response = bridge.process_request_enhanced("Add unit tests for auth module")
```

### LLM Routing
The `LLMRouter` handles multiple providers with auto-selection (Gemini → OpenAI → Anthropic → Ollama).

```python
from agentic_sdlc.core.llm import get_router

router = get_router()
response = router.complete("Explain the codebase structure")
```

### Swarm Orchestration
Manages specialized agent teams for complex tasks.

```python
from agentic_sdlc.swarm import SwarmOrchestrator, AgentRole

swarm = SwarmOrchestrator()
result = swarm.run_pipeline("Implement user login", roles=[AgentRole.DEVELOPER, AgentRole.REVIEWER])
```

## 4. AI Agent Tips
-   **Always use `process_request_enhanced`** for complex coding tasks.
-   **Check `artifacts/`** after a run to see implementation plans and reports.
-   **Use the `DomainRegistry`** to scope your work to specific technical pillars.
