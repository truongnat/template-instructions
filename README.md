# 📦 Agentic SDLC - Multi-Domain Swarm Agent SDK

![Version](https://img.shields.io/badge/version-3.1.0-blue.svg)
![Build](https://img.shields.io/badge/build-passing-brightgreen.svg)
![License](https://img.shields.io/badge/license-MIT-green.svg)

> Next-generation AI Software Development Lifecycle framework with Swarm Intelligence, RAG-powered Research, and Multi-Provider LLM orchestration.

**Agentic SDLC** is a modular Python SDK for building autonomous development agents. It moves beyond simple prompt generation into a full E2E pipeline: **Domain Detection → Research → Prompt Optimization → Swarm Execution → Self-Learning**.

---

## 🚀 Key Features

- 🧠 **Swarm Intelligence**: Multi-agent coordination (Developer, Reviewer, Tester, Researcher) with async message bus.
- 🔍 **RAG Research**: Integrated Knowledge Base using ChromaDB and web-research capabilities.
- 🎯 **Domain Engine**: Automatic task classification into 7+ technical domains (Frontend, Backend, DevOps, etc.).
- 🧪 **Prompt Lab**: A/B testing for prompts with structured strategies and AI-powered evaluation.
- 🤖 **Multi-Provider LLM**: Unified support for **Gemini (primary)**, OpenAI, Anthropic, and **Ollama** (local).
- 📈 **Self-Learning**: Continuous improvement engine that analyzes execution patterns and proposes enhancements.

---

## 📦 quick start

### installation

```bash
pip install agentic-sdlc[all]  # Includes ChromaDB and ML dependencies
```

### Basic E2E Pipeline

```python
from agentic_sdlc import AgentBridge
from pathlib import Path

# Initialize bridge with preferred LLM
bridge = AgentBridge(
    project_dir=Path("."),
    llm_provider="gemini",
    llm_model="gemini-2.0-flash"
)

# Run full E2E pipeline
response = bridge.process_request_enhanced("Implement JWT auth in FastAPI")

print(f"Detected Domain: {response.metadata['domain']}")
print(f"Optimized Prompt: {response.skill_instructions[:100]}...")
```

---

## 🏗 Architecture

```
agentic_sdlc/
├── bridge/          # Primary E2E Pipeline (AgentBridge)
├── swarm/           # Swarm Intelligence (Orchestrator, MessageBus, Agents)
├── knowledge/       # RAG Layer (KnowledgeBase, VectorStore, Embeddings)
├── core/            # Config, Domain Engine, LLM Routing, Artifacts
├── prompts/         # Prompt Lab, Generator, Optimization
├── intelligence/    # Self-Learning, Reasoner
├── skills/          # Skill Registry & Generation
└── sdlc/            # Board & Task Tracking
```

---

## 📚 Documentation

- **[Quick Start Guide](QUICKSTART.md)** - Get up and running in 5 minutes.
- **[Architecture Deep-Dive](docs/architecture/README.md)** - How the swarm and RAG layers work.
- **[LLM Setup](docs/LLM_PROVIDERS.md)** - Configuring Gemini, OpenAI, and local Ollama.
- **[Context for Agents](CONTEXT.md)** - For AI agents like Cursor or Antigravity to understand this framework.

---

## 🔌 Supported LLM Providers

| Provider | Model | Tier |
|----------|-------|------|
| **Google Gemini** | `gemini-2.0-flash` | Free/Paid |
| **OpenAI** | `gpt-4o`, `gpt-4o-mini` | Paid |
| **Anthropic** | `claude-3-5-sonnet` | Paid |
| **Ollama** | `llama3.2`, `mistral` | **FREE / Local** |

---

## 🧪 Testing

```bash
pytest tests/unit/swarm  # Test swarm multi-agent logic
pytest tests/unit/knowledge # Test RAG retrieval
```

---

## 📄 License
MIT License. Developed by **Dao Quang Truong** | [GitHub](https://github.com/truongnat/agentic-sdlc)