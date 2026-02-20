# Setup Guide for Agentic SDLC Projects

This guide helps you set up and run your project built with the Agentic SDLC framework.

## Prerequisites

### Required
- **Python 3.10+**
- **pip**

### Feature-Specific
- **ChromaDB** - Required for RAG / Knowledge Base (Persistent vector store)
- **Ollama** - Optional, for running free local models

## Installation

### 1. Install the Framework

```bash
# Recommended for all features
pip install "agentic-sdlc[all]"
```

## Environment Variables

Create a `.env` file in your project root:

```bash
# LLM Providers (At least one required)
GEMINI_API_KEY=your_key
OPENAI_API_KEY=your_key
ANTHROPIC_API_KEY=your_key

# Research
SERPAPI_API_KEY=your_key # Optional for web search
```

## Configuration

Edit `.agentic_sdlc/domains.yaml` to customize your domain detection keywords:

```yaml
domains:
  backend:
    keywords: ["api", "database", "server", "fastapi"]
    priority: 10
```

## Storage Layout

The framework creates a `.agentic_sdlc/` directory for persistence:
- `knowledge/` - ChromaDB vector store
- `prompts/history/` - A/B test logs
- `learning/` - Execution logs for self-learning
- `artifacts/` - Generated implementation plans and reports

## Verifying Setup

```python
from agentic_sdlc import AgentBridge
from pathlib import Path

bridge = AgentBridge(project_dir=Path("."))
print(f"Available Providers: {bridge.llm_router.get_available_providers()}")
```

---
**Status:** ✅ v3.1.0 Ready
