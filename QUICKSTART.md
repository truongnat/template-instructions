# Agentic SDLC - Quick Start Guide

This guide will help you get started with the Multi-Domain Swarm Agent framework.

## 1. Installation

```bash
# Install core dependencies
pip install agentic-sdlc

# Install with all features (ChromaDB, ML models, etc.)
pip install agentic-sdlc[all]
```

## 2. LLM Configuration

The framework supports Gemini, OpenAI, Anthropic, and Ollama. Set your API keys as environment variables:

```bash
export GEMINI_API_KEY="your-key"
export OPENAI_API_KEY="your-key"
export ANTHROPIC_API_KEY="your-key"
```

## 3. Basic Usage (E2E Pipeline)

The `AgentBridge` is the main entry point that orchestrates domain detection, research, prompt optimization, and execution.

```python
from agentic_sdlc import AgentBridge
from pathlib import Path

# Initialize bridge
bridge = AgentBridge(project_dir=Path("."))

# Process request through full E2E pipeline
response = bridge.process_request_enhanced("Implement a secure login API in Python")

print(f"Detected Domain: {response.metadata['domain']}")
print(f"Optimized Prompt:\n{response.skill_instructions}")
```

## 4. RAG & Knowledge Base

Add your project documents to the Knowledge Base for semantic retrieval.

```python
from agentic_sdlc.knowledge import KnowledgeBase

kb = KnowledgeBase(persist_dir=Path("./.agentic_sdlc/knowledge"))

# Ingest documentation
kb.ingest_directory("./docs")

# Query semantically
results = kb.query("How to handle authentication?", limit=3)
for res in results:
    print(f"Content: {res.content[:100]}... (Score: {res.score})")
```

## 5. Swarm Intelligence

Run a complex task using a team of specialized agents.

```python
from agentic_sdlc.swarm import SwarmOrchestrator, AgentRole

swarm = SwarmOrchestrator()

# Run a sequential pipeline: Researcher -> Developer -> Reviewer -> Tester
result = swarm.run_pipeline(
    task="Create a custom middleware for request logging",
    roles=[
        AgentRole.RESEARCHER,
        AgentRole.DEVELOPER,
        AgentRole.REVIEWER,
        AgentRole.TESTER
    ]
)

print(result.combined_output)
```

## 6. LLM Routing (Auto-Selection)

The `LLMRouter` automatically selects the best available provider (Gemini -> OpenAI -> Anthropic -> Ollama).

```python
from agentic_sdlc.core.llm import get_router

router = get_router()

# This uses whatever provider you have configured
response = router.complete("Explain the singleton pattern")
print(f"Provider: {response.provider}, Model: {response.model}")
```

## 7. Self-Learning Reports

After several runs, generate a report on how the system can improve.

```python
from agentic_sdlc import AgentBridge

bridge = AgentBridge(project_dir=Path("."))

# Generate improvement report
report = bridge.learn_report()
print(report)
```

## Next Steps

1.  **Check out the [Architecture Guide](docs/architecture/README.md)**.
2.  **Explore the [examples/](examples/) directory** for full project templates.
3.  **Use `CONTEXT.md`** when talking to your AI assistant about this framework.

---
Development by **Dao Quang Truong** | Version 3.1.0
