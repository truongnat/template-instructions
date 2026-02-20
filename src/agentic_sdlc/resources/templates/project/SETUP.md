# Setup Guide

## Prerequisites
- **Python 3.10+**
- **pip**

## Installation

```bash
pip install "agentic-sdlc[all]"
```

## Environment Variables

Create a `.env` file:

```bash
# LLM Provider (at least one recommended)
GEMINI_API_KEY=your_key        # Free tier available
# OPENAI_API_KEY=your_key      # Optional
# ANTHROPIC_API_KEY=your_key   # Optional

# Local Models (alternative to cloud)
# OLLAMA_BASE_URL=http://localhost:11434
```

## Initialize Project

```bash
asdlc init
```

This creates:
- `GEMINI.md` — AI agent configuration
- `CONTEXT.md` — Project context for agents
- `.agentic_sdlc/config.yaml` — Framework config
- `.agent/workflows/` — Antigravity workflows

## Verify

```bash
asdlc health
asdlc run "Check project setup"
```

## Troubleshooting

```bash
# Verify installation
python3 -c "import agentic_sdlc; print(agentic_sdlc.__version__)"

# Reinstall
pip install --upgrade agentic-sdlc
```
