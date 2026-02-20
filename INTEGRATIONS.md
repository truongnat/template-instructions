# External Integrations Guide

The Agentic SDLC framework is designed to integrate seamlessly with modern AI development environments.

## 1. IDE Integrations

### Cursor / VS Code
The framework provides a `.cursorrules` file in the project root. This ensures that the AI assistant inside Cursor understands the multi-domain swarm architecture.

### Antigravity
Antigravity automatically detects the `CONTEXT.md` and `.agentic_sdlc/` directory to facilitate E2E pipeline execution.

## 2. LLM Providers

| Provider | Method | Recommendation |
|----------|--------|----------------|
| **Gemini** | `google-genai` | **Primary** — Use for domain detection and reasoning. |
| **OpenAI** | `openai` | Use for complex code generation. |
| **Anthropic** | `anthropic` | Use for detailed code reviews. |
| **Ollama** | Local API | Use for sensitive code or model-free offline dev. |

## 3. Tool Integrations (MCP)

The framework supports the **Model Context Protocol (MCP)** for connecting to external tools like:
- Supabase (Database management)
- GitHub (PR management)
- Slack (Team notifications)

## 4. Vector Stores

### ChromaDB (Standard)
Persistent, embedded vector store. No additional server required. Installed via `pip install chromadb`.

### LanceDB (Performance)
High-performance vector store for massive codebases.

---
**Last Updated:** February 20, 2026
