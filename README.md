# Agentic SDLC

> Transform your IDE into a complete Software Development Lifecycle team with AI-powered agents, automated workflows, and intelligent knowledge management.

## 🎯 What is Agentic SDLC?

**Agentic SDLC** is an AI-powered development framework that simulates a complete software development team within your IDE. It provides:

- **17 Specialized AI Roles** - PM, BA, SA, UI/UX, QA, Security, Dev, DevOps, Tester, Reporter, and more
- **23 Automated Workflows** - From planning to deployment with `/slash` commands
- **Reinforced Brain System** - 21 Intelligence sub-agents including HITL, Sandbox, and Self-Healing
- **Multi-Agent Teams** - AutoGen-powered autonomous agent collaboration
- **Cross-IDE Compatibility** - Works with Cursor, Windsurf, Cline, Aider, Gemini, and any AI-powered IDE
- **Monorepo Architecture** - Shared brain system across multiple projects

## 🧠 The Brain System

At the core of Agentic SDLC is the **Brain** - an intelligent knowledge management system that:

- **Learns from every task** - Automatically captures patterns from bugs, features, and solutions
- **Provides recommendations** - Suggests approaches based on past successes
- **Builds knowledge graphs** - Maps relationships between skills, technologies, and solutions
- **Enables compound intelligence** - Each project's knowledge benefits all others

→ See **[GEMINI.md](GEMINI.md)** for complete Brain documentation

## ✨ Quick Start

### Installation

The project provides automated setup scripts for both Windows and Unix-based systems. These scripts handle Python virtual environments, dependency installation (Python & JS), and brain system initialization.

#### Windows (PowerShell)
```powershell
.\bin\setup.ps1
```

#### Linux / macOS (Bash)
```bash
chmod +x ./bin/setup.sh
./bin/setup.sh
```

### Configuration

Copy `.env.template` to `.env` and configure your API keys:
```bash
cp .env.template .env
```

### 🧠 System Commands
All operations are centralized through the `asdlc` script.

#### Windows (PowerShell)
```powershell
.\bin\asdlc.ps1 <command>
```

#### Linux / macOS (Bash)
```bash
./bin/asdlc.sh <command>
```

### 📊 System Dashboard
Monitor agents, costs, and approvals via the real-time dashboard:
```bash
python asdlc.py dashboard
```

## 🚀 Reinforced Intelligence Features

The system has been enhanced with enterprise-grade reliability:

- **🛡️ Sandboxing:** Securely execute agent-generated code in isolated Docker containers.
- **🛑 HITL (Human-in-the-Loop):** Mandatory approval gates for critical phases (Deploy, Security, Code Review).
- **🔄 Persistence & Recovery:** Workflow session state management with SQLite-based checkpointing.
- **🩹 Self-Healing:** Automated QA→DEV feedback loops that learn from error patterns.
- **💰 Cost Monitoring:** Real-time token tracking and budget alerts per model/task.
- **🏆 Evaluation:** Robust benchmarking framework to measure and improve agent performance.
- **🏠 Local LLM Support:** Privacy-first execution using Ollama for local model hosting.

## 🚀 Core Features

### 1. AI Role System (17 Roles)

Specialized AI agents for every SDLC phase:

```
Planning    → @PM, @BA, @PO
Design      → @SA, @UIUX
Review      → @QA, @SECA
Development → @DEV, @DEVOPS
Testing     → @TESTER
Delivery    → @REPORTER, @STAKEHOLDER
Meta        → @BRAIN, @ORCHESTRATOR
```

### 2. Slash Commands (23 Workflows)

Execute complete workflows with simple commands (mapped to `asdlc workflow <name>`):

```bash
/brain           # Brain system management (asdlc brain status)
/cycle           # Complete task lifecycle
/explore         # Deep investigation
/orchestrator    # Full SDLC automation
/sprint          # Sprint management
/monitor         # System dashboard
/validate        # System validation
/metrics         # View metrics dashboard
/release         # Release management
/emergency       # Critical incident response
/housekeeping    # Cleanup & maintenance
```

### 3. Monorepo Architecture

```
agentic-sdlc/              # 🧠 Brain (Root)
├── .agent/                # AI workflows, skills, KB
├── tools/                 # Neo4j, research, utilities
├── docs/                  # Documentation
└── projects/              # Your projects
    ├── project-1/
    ├── project-2/
    └── [add-yours]/
```

**Benefits:**
- ✅ Shared brain across all projects
- ✅ Compound learning from every solution
- ✅ Consistent workflows and quality
- ✅ Centralized knowledge management

### 4. Knowledge Management

**Automated Learning:**
- Records error patterns and solutions
- Captures successful implementation approaches
- Builds skill and technology graphs
- Provides context-aware recommendations

**Three-Layer System:**
1. **LEANN** - Vector-based semantic search
2. **Neo4j** - Knowledge graph with relationships
3. **File-based KB** - Categorized markdown entries

## 📖 Documentation

### Getting Started
- **[GEMINI.md](GEMINI.md)** - Complete brain system guide (IDE-agnostic)
- **[Quick Start](docs/guides/QUICK-START.md)** - 5-minute setup guide
- **[CLI Examples](docs/guides/CLI-EXAMPLES.md)** - Command usage examples

### Architecture
- **[Monorepo Architecture](docs/MONOREPO-ARCHITECTURE.md)** - System design
- **[Project Structure](PROJECT-STRUCTURE.md)** - Directory organization
- **[Documentation Index](docs/PROJECT-DOCUMENTATION-INDEX.md)** - All docs

### Tools & Setup
- **[Neo4j Tools](tools/neo4j/README.md)** - Knowledge graph system
- **[Research Agent](tools/research/README.md)** - Automated research
- **[MCP Setup](docs/guides/MCP-SETUP.md)** - Model Context Protocol

## 🎯 Use Cases

### Solo Developer
```bash
/auto Create a SaaS platform with authentication and billing
# Complete automation from planning to deployment
```

### Team Development
```bash
# Each team member uses the same brain
python asdlc.py brain sync
git pull  # Share knowledge base
/pm Start Sprint 3
```

### Existing Large Project
```bash
python asdlc.py setup
/brain  # Index and analyze codebase
/pm Migrate authentication to OAuth2
```

## 🔧 Available Commands

```bash
# System Dashboard
python asdlc.py dashboard       # Start the UI monitoring

# Brain & Intelligence
python asdlc.py brain status    # Check system state
python asdlc.py brain health    # Full health check
python asdlc.py brain sync      # Sync knowledge graph

# Workflows
python asdlc.py workflow cycle  # Run task lifecycle
python asdlc.py workflow orchestrator  # Full automation

# Release Management
python asdlc.py release preview # Preview changes
python asdlc.py release release # Full release cycle
```

## 🌟 Why Agentic SDLC?

| Traditional Development | With Agentic SDLC |
|------------------------|-------------------|
| Manual planning | Automated with @PM |
| Ad-hoc architecture | Structured with @SA, @UIUX |
| Inconsistent code quality | Enforced by @QA, @SECA |
| Lost knowledge | Compound learning brain |
| Repetitive tasks | Automated with @AUTO |
| Single-agent limits | Multi-agent teams with AutoGen |
| Solo problem-solving | 17+ AI experts available |

## 🔗 Links

- **Repository:** https://github.com/truongnat/agentic-sdlc
- **NPM Package:** https://www.npmjs.com/package/agentic-sdlc
- **Issues:** https://github.com/truongnat/agentic-sdlc/issues
- **Documentation:** [docs/](docs/)

## 📄 License

MIT License - See [LICENSE](LICENSE) for details

---

**Next Steps:**
1. Read [GEMINI.md](GEMINI.md) to understand the brain system
2. Follow [Quick Start](docs/guides/QUICK-START.md) to get started
3. Explore [workflows](.agent/workflows/) to see available automations

**Questions?** Check the [documentation](docs/) or [open an issue](https://github.com/truongnat/agentic-sdlc/issues).
