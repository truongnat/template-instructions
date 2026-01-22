# 📦 Agentic SDLC Kit

> The Intelligence Layer for your Software Development Lifecycle. Installable, scalable, and self-learning.

**Agentic SDLC** is a portable AI-powered development framework that transforms any repository into an intelligent development ecosystem. It provides specialized AI experts, automated workflows, and a "Brain" that learns from every line of code you write.

---

## 🚀 Quick Start

### 1. Install the Kit (via Bun or Pip)
```bash
# Recommended
bun install agentic-sdlc

# Alternative
pip install agentic-sdlc
```

### 2. Initialize your Project
Navigate to your project root and run:
```bash
agentic init
```
This scaffolds the following in your project:
- `.agent/` - AI Expert roles, rules, and workflows.
- `docs/` - Project documentation and SDLC artifacts.
- `agentic.yaml` - Runtime configuration.

### 3. Start your first Sprint
```bash
agentic sprint start 1
```

---

## 🧠 What's inside the Kit?

### 👥 18 Specialized AI Roles
Assign tasks to specific experts directly in your IDE:
- `@PM` (Project Manager) - Planning & Tracking
- `@SA` (System Architect) - Design & Architecture
- `@DEV` (Developer) - Implementation
- `@TESTER` (QA) - Verification & Self-Healing
- `@SECA` (Security) - Audits & Safety
- `@RESEARCH` (Specialist) - Technical Research & Swarms

### ⚡ 23 Automated Workflows
Execute complete SDLC phases with simple slash commands:
- `/cycle` - Research → Plan → Code → Review in one go.
- `/orchestrator` - Full automation of complex features.
- `/swarm` - Intelligent multi-agent routing.
- `/concurrent` - Execute multiple roles (SA, UIUX, PO) in parallel.
- `/synthesize` - Mixture of Agents (MoA) synthesis.
- `/heal` - Automated bug detection and auto-fixing.
- `/ab` - Generate and compare architectural alternatives.

### 3-Layer Architecture
The system follows a concentric design ensuring safety and consistency:
- **Layer 1: Core** - GEMINI.md, Rules, and Workflows.
- **Layer 2: Intelligence** - 26 Sub-Agents (Brain, SwarmRouter, Self-Learning).
- **Layer 3: Infrastructure** - CLI, SDK, AOP (Agent Orchestration Protocol).

---

## 🛠️ Usage

### CLI Commands
The kit provides a unified entry point:
```bash
agentic status              # View current SDLC state
agentic init-state --sprint 1  # Initialize brain state for a sprint
agentic heal --code src/main.py # Run self-healing on a file
agentic gate list           # View pending human-in-the-loop approvals
```

### IDE Integration (Slash Commands)
If you use an AI-powered IDE (Cursor, Windsurf, etc.), simply reference the workflows:
```text
@DEV /cycle Implement user authentication
@PM /planning Create a plan for the next feature
```

---

## 🐍 SDK Usage (Python)
Integrate the Agentic Brain directly into your own scripts:

```python
from agentic_sdlc import Learner, SprintManager, get_project_root

# Get the current project context
root = get_project_root()

# Record a learning event
learner = Learner()
learner.learn("Refactored database layer for performance")

# Manage sprints
sm = SprintManager()
sm.create_sprint("Feature Alpha", "Deliver MVP")
```

---

## 🏗️ Enterprise Features
- **🛡️ Sandboxing:** Execute agent code in isolated Docker containers.
- **🩹 Self-Healing:** Automated feedback loops that learn from test failures.
- **🌊 Swarms Orchestration:** Universal routing, parallel execution, and expert synthesis.
- **📡 AOP Protocol:** Distributed Agent Orchestration Protocol for distributed AI.
- **Knowledge Graph:** Optional Neo4j integration for cross-project intelligence.
- **Local LLM Support:** Full compatibility with Ollama for privacy-first development.

---

## 📄 License
MIT License. See [LICENSE](LICENSE) for details.

---
Developed by **Dao Quang Truong** | [GitHub](https://github.com/truongnat/agentic-sdlc)