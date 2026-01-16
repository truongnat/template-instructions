# Agentic SDLC CLI Usage Guide

All project operations are centralized through the unified `asdlc.py` entry point. For convenience, platform-specific wrappers are provided in the `bin/` directory.

---

## 🚀 Installation & Setup

### 1. Unified Setup
The automated setup script handles virtual environments, dependencies, and brain initialization.

**Windows:**
```powershell
.\bin\setup.ps1
```

**Unix (Linux/macOS):**
```bash
./bin/setup.sh
```

### 2. Configuration
Copy the template and add your API keys:
```bash
cp .env.template .env
```

---

## 🧠 Core CLI Commands (`asdlc.py`)

### 📊 System Dashboard
Monitor all agents, approval gates, execution costs, and learning patterns in real-time.
```bash
python asdlc.py dashboard
```

### 🛡️ Brain & Health
Check the state and integrity of the AI intelligence layer.
```bash
# Check current workflow state and phase
python asdlc.py brain status

# Run a comprehensive system health check
python asdlc.py health

# Sync the knowledge graph (Neo4j)
python asdlc.py brain sync
```

### 🔄 SDLC Workflows
Execute complete task lifecycles or specialized automated processes.
```bash
# Run a complete task cycle (Plan -> Work -> Review -> Learn)
python asdlc.py workflow cycle "Add unit tests to the auth module"

# Run full project orchestration
python asdlc.py workflow orchestrator "Build a new landing page"

# Run maintenance/cleanup
python asdlc.py workflow housekeeping
```

### 📦 Release Management
Automate versioning and changelog generation.
```bash
# Preview upcoming changes
python asdlc.py release preview

# Execute a full release (version bump, tags, changelog)
python asdlc.py release release
```

---

## 🌍 Platform Wrappers

For a shorter syntax, use the wrappers in `bin/`:

**Windows (PowerShell):**
```powershell
.\bin\asdlc.ps1 brain status
.\bin\asdlc.ps1 workflow cycle "Task description"
```

**Unix (Bash):**
```bash
./bin/asdlc.sh brain status
./bin/asdlc.sh workflow cycle "Task description"
```

---

## 🎯 Example Workflows

### Scenario 1: Starting a new feature
1. **Sync Brain:** Ensure the knowledge graph is up to date.
   ```bash
   python asdlc.py brain sync
   ```
2. **Start Cycle:** Launch the automated DEV cycle.
   ```bash
   python asdlc.py workflow cycle "Implement Password Reset"
   ```
3. **Monitor:** Open dashboard to approve planning/security gates.
   ```bash
   python asdlc.py dashboard
   ```

### Scenario 2: Troubleshooting a configuration issue
1. **Health Check:** Identify missing dependencies or misconfigured environment variables.
   ```bash
   python asdlc.py health
   ```
2. **Brain Status:** Verify the current active session state.
   ```bash
   python asdlc.py brain status
   ```

---

## 📖 Related Documentation
- **[GEMINI.md](../../GEMINI.md)** - Deep dive into architecture and Intelligence Sub-Agents.
- **[QUICK-START.md](QUICK-START.md)** - Getting started in under 5 minutes.
- **[AUTO-LEARNING-SYSTEM.md](AUTO-LEARNING-SYSTEM.md)** - How the brain learns from your work.
