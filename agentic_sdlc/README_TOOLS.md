# Tools - Support Scripts

Support scripts for both `bin/` CLI and `.agent/` workflows.

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    TOOLS LAYER                               │
│         Support Scripts for CLI and Workflows                │
└─────────────────────────────────────────────────────────────┘
                              │
        ┌─────────────────────┼─────────────────────┐
        ▼                     ▼                     ▼
   ┌─────────┐          ┌─────────┐          ┌─────────┐
   │  bin/   │          │ agentic_sdlc/  │          │ .agent/ │
   │   CLI   │◄─────────│ Scripts │─────────►│Workflows│
   └─────────┘          └─────────┘          └─────────┘
```

## Purpose

The `agentic_sdlc/` directory contains backend support scripts that:
- ✅ Support `bin/` CLI commands
- ✅ Support `.agent/` workflow automation
- ✅ Provide integration with external services
- ✅ Enable automation and orchestration

**Key Principle:** Tools are called by CLI or workflows, not directly by users.

## Directory Structure

```
agentic_sdlc/
├── agent/                    # Agent item management (NEW)
│   ├── manage.py            # Manage roles, workflows, templates, rules
│   └── README.md
│
├── workflows/                # Workflow automation
│   ├── cycle.py             # Complete task lifecycle
│   ├── housekeeping.py      # Maintenance and cleanup
│   ├── sprint.py            # Sprint management
│   └── emergency.py         # Critical incident response
│
├── kb/                       # Knowledge base management (from .agent/scripts/)
│   ├── search.py            # Search knowledge base
│   ├── update-index.py      # Update KB index
│   └── stats.py             # Generate KB statistics
│
├── validation/               # Health checks (from .agent/scripts/)
│   └── health-check.py      # System health monitoring
│
├── utils/                    # Shared utilities (from .agent/scripts/)
│   ├── common.py            # Common utilities
│   ├── artifact_manager.py  # Artifact management
│   └── kb_manager.py        # KB management utilities
│
├── github/                   # GitHub integration
│   ├── sync_github.py       # Sync artifacts to GitHub
│   └── README.md
│
├── intelligence/knowledge_graph/  # Memgraph brain integration
│   ├── sync_skills_to_memgraph.py
│   ├── query_skills_memgraph.py
│   ├── graph_brain.py
│   ├── test_memgraph_connection.py
│   ├── verify_memgraph.py
│   ├── requirements.txt
│   └── README.md
│
├── research/                 # Research agent system
│   ├── research_agent.py
│   ├── research_mcp.py
│   ├── research_mcp_extended.py
│   └── README.md
│
├── setup/                    # Setup utilities
│   ├── setup_research_hooks.sh
│   ├── standardize_filenames.ps1
│   └── README.md
│
├── run.sh                    # Cross-platform runner (Unix)
├── run.py                    # Cross-platform runner (Python)
├── run.bat                   # Cross-platform runner (Windows)
├── requirements.txt          # Master requirements
└── README.md                 # This file
```

## Tools Overview

### 1. Agent Management (`agent/`)
**Purpose:** Manage items in `.agent/` directory

**Features:**
- Create new roles, workflows, templates, rules
- List all items by type
- Validate item structure
- Show item information
- Template-based generation

**Called by:**
- Manual: Direct script execution
- npm: Package.json scripts
- Kiro IDE: Custom commands

**Usage:**
```bash
# List all roles
python agentic_sdlc/agent/manage.py list role

# Create new role
python agentic_sdlc/agent/manage.py create role architect

# Validate workflow
python agentic_sdlc/agent/manage.py validate workflow cycle

# Show info
python agentic_sdlc/agent/manage.py info template project-plan
```

**Documentation:** [agent/README.md](agent/README.md)

---

### 2. Workflow Automation (`workflows/`)
**Purpose:** Execute TeamLifecycle workflow commands

**Features:**
- Complete task lifecycle (`/cycle`)
- Maintenance and cleanup (`/housekeeping`)
- Critical incident response (`/emergency`)
- Workflow orchestration

**Called by:**
- Kiro IDE: `/cycle`, `/housekeeping`, `/emergency` commands
- `.agent/` workflows: All workflow commands
- `bin/` CLI: Workflow execution

**Usage:**
```bash
python agentic_sdlc/workflows/cycle.py --task "Add user avatar"
python agentic_sdlc/workflows/housekeeping.py --sprint 3
```

---

### 2. Knowledge Base Management (`kb/`)
**Purpose:** Manage compound learning system

**Features:**
- Search knowledge base
- Update searchable index
- Generate statistics
- Validate entries

**Called by:**
- Kiro IDE: `/compound` command
- `.agent/` workflows: All roles (knowledge search)
- `bin/` CLI: `kb` commands

**Usage:**
```bash
python agentic_sdlc/kb/search.py --query "authentication"
python agentic_sdlc/kb/update-index.py
python agentic_sdlc/kb/stats.py
```

---

### 3. Validation & Health Checks (`validation/`)
**Purpose:** System health monitoring

**Features:**
- Verify artifact placement
- Check documentation drift
- Validate YAML frontmatter
- Monitor system health

**Called by:**
- Kiro IDE: `/housekeeping` command
- `.agent/` workflows: Automated health checks
- `bin/` CLI: Health monitoring

**Usage:**
```bash
python agentic_sdlc/validation/health-check.py
```

---

### 4. Shared Utilities (`utils/`)
**Purpose:** Common utilities for all tools

**Features:**
- Artifact management
- KB management helpers
- Common functions
- Cross-tool utilities

**Called by:**
- All other tools
- Workflows
- CLI commands

**Usage:**
```python
from tools.utils.common import load_config
from tools.utils.kb_manager import search_kb
from tools.utils.artifact_manager import create_artifact
```

---

### 5. GitHub Integration (`github/`)
**Purpose:** Sync TeamLifecycle artifacts with GitHub

**Features:**
- Create issues from sprint tasks
- Manage milestones
- Apply labels
- Track progress

**Called by:**
- `bin/` CLI: `agentic-sdlc sync-github`
- `.agent/` workflows: PM, REPORTER

**Usage:**
```bash
python agentic_sdlc/github/sync_github.py --sprint 3
```

**Documentation:** [github/README.md](github/README.md)

---

### 2. Memgraph Integration (`intelligence/knowledge_graph/`)
**Purpose:** Knowledge graph and brain integration

**Features:**
- Sync KB entries to Memgraph
- Query knowledge graph
- Map relationships
- Track skills and technologies

**Called by:**
- `bin/` CLI: `kb compound` commands
- `.agent/` workflows: All roles (knowledge search)

**Usage:**
```bash
python agentic_sdlc/intelligence/knowledge_graph/sync_skills_to_memgraph.py
python agentic_sdlc/intelligence/knowledge_graph/query_skills_memgraph.py --all-skills
```

**Documentation:** [intelligence/knowledge_graph/README.md](intelligence/knowledge_graph/README.md)

---

### 3. Research Agent (`research/`)
**Purpose:** Automated knowledge research before tasks

**Features:**
- Search knowledge base
- Query Neo4j graph
- Search GitHub issues
- External API integration

**Called by:**
- `bin/` CLI: `agentic-sdlc research`
- `.agent/` workflows: PM, DEV, TESTER (before work)
- Kiro hooks: Auto-trigger on @role mentions

**Usage:**
```bash
python agentic_sdlc/research/research_agent.py --task "authentication" --type feature
```

**Documentation:** [research/README.md](research/README.md)

---

### 4. Setup Utilities (`setup/`)
**Purpose:** System setup and configuration

**Features:**
- Setup research hooks
- Standardize filenames
- Configure integrations

**Called by:**
- `bin/` CLI: `agentic-sdlc install`
- Manual setup: Initial project configuration

**Usage:**
```bash
bash agentic_sdlc/setup/setup_research_hooks.sh
.\tools\setup\standardize_filenames.ps1
```

**Documentation:** [setup/README.md](setup/README.md)

---

## Installation

### Install All Dependencies

```bash
# Install all tool dependencies
pip install -r agentic_sdlc/requirements.txt
```

### Install Specific Tool Dependencies

```bash
# GitHub integration
pip install PyGithub python-dotenv

# Memgraph integration
pip install neo4j python-dotenv

# Research agent
pip install requests python-dotenv pyyaml
```

### Virtual Environment (Recommended)

```bash
# Create virtual environment
python -m venv venv

# Activate (Linux/macOS)
source venv/bin/activate

# Activate (Windows)
venv\Scripts\activate

# Install dependencies
pip install -r agentic_sdlc/requirements.txt
```

## Configuration

### Environment Variables

Create `.env` file in project root:

```bash
# GitHub Integration (optional)
GITHUB_TOKEN=ghp_your_personal_access_token
GITHUB_REPO=username/repository

# Memgraph Integration (optional)
MEMGRAPH_URI=bolt://instance.databases.memgraph.io
MEMGRAPH_USERNAME=memgraph
MEMGRAPH_PASSWORD=your_password
MEMGRAPH_DATABASE=memgraph

# Research Agent APIs (optional)
TAVILY_API_KEY=your_tavily_key
BRAVE_API_KEY=your_brave_key
STACKOVERFLOW_KEY=your_stackoverflow_key
```

### Tool-Specific Configuration

Each tool may have additional configuration:
- See individual README files for details
- Check `requirements.txt` in each subdirectory
- Review example configurations

## Usage Patterns

### Pattern 1: Called by CLI

```javascript
// bin/agentic-sdlc/commands/sync.js
import { execSync } from 'child_process';

export async function syncGitHub(sprint) {
  execSync(`python agentic_sdlc/github/sync_github.py --sprint ${sprint}`);
}
```

### Pattern 2: Called by Workflows

```markdown
## @PM Workflow

### Step 0: Research
```bash
python agentic_sdlc/research/research_agent.py --task "${task}" --type general
```

### Step 5: Sync to GitHub
```bash
python agentic_sdlc/github/sync_github.py --sprint ${sprint_number}
```
```

### Pattern 3: Called by Hooks

```json
{
  "name": "research-before-planning",
  "trigger": "on_message",
  "condition": "message contains '@PM'",
  "action": {
    "type": "command",
    "command": "python agentic_sdlc/research/research_agent.py --task \"${message}\""
  }
}
```

## Integration Examples

### Example 1: KB CLI with Memgraph

```bash
# User runs KB CLI
./bin/kb/kb compound search "authentication"

# KB CLI calls agentic_sdlc/intelligence/knowledge_graph/
# → agentic_sdlc/intelligence/knowledge_graph/query_skills_memgraph.py
# → Returns results to CLI
# → CLI displays to user
```

### Example 2: PM Workflow with Research

```bash
# User: @PM Build todo app

# PM workflow calls agentic_sdlc/research/
# → agentic_sdlc/research/research_agent.py --task "todo app"
# → Searches KB, Memgraph, GitHub
# → Returns research report
# → PM uses findings in project plan
```

### Example 3: Automated GitHub Sync

```bash
# REPORTER workflow completes

# Workflow calls agentic_sdlc/github/
# → agentic_sdlc/github/sync_github.py --sprint 3
# → Creates GitHub issues
# → Applies labels
# → Links artifacts
```

## Development

### Adding New Tools

1. Create subdirectory: `agentic_sdlc/newtool/`
2. Add scripts: `agentic_sdlc/newtool/script.py`
3. Add README: `agentic_sdlc/newtool/README.md`
4. Add requirements: `agentic_sdlc/newtool/requirements.txt`
5. Update master requirements: `agentic_sdlc/requirements.txt`
6. Update this README

### Tool Template

```python
#!/usr/bin/env python3
"""
Tool: New Tool
Purpose: Brief description
Called by: bin/ CLI, .agent/ workflows
"""

import os
import sys
from pathlib import Path
from dotenv import load_dotenv

# Load environment
load_dotenv()

def main():
    """Main function"""
    print("🔧 Running New Tool...")
    
    # Tool logic here
    
    print("✅ Complete!")

if __name__ == '__main__':
    main()
```

### Best Practices

1. **Idempotent** - Safe to run multiple times
2. **Error handling** - Graceful failures
3. **Logging** - Clear progress messages
4. **Configuration** - Use environment variables
5. **Documentation** - Comprehensive README
6. **Testing** - Include test scripts
7. **Cross-platform** - Support Windows, Linux, macOS

## Testing

### Test Individual Tools

```bash
# GitHub integration
python agentic_sdlc/github/sync_github.py --dry-run

# Neo4j integration
python agentic_sdlc/neo4j/test_neo4j_connection.py

# Research agent
python agentic_sdlc/research/research_agent.py --task "test" --type general

# Setup utilities
bash agentic_sdlc/setup/setup_research_hooks.sh
```

### Test Integration

```bash
# Test CLI → Tools
./bin/kb/kb compound search "test"

# Test Workflow → Tools
# Run @PM workflow and verify research runs
```

## Troubleshooting

### Import Errors

```bash
# Ensure dependencies installed
pip install -r agentic_sdlc/requirements.txt

# Check Python path
which python3
python3 --version
```

### Permission Errors

```bash
# Make scripts executable (Linux/macOS)
chmod +x agentic_sdlc/setup/*.sh
chmod +x agentic_sdlc/research/*.py
```

### Configuration Errors

```bash
# Check .env file exists
ls -la .env

# Verify environment variables
cat .env | grep GITHUB_TOKEN
cat .env | grep MEMGRAPH_URI
```

### API Errors

```bash
# Test GitHub connection
python -c "from github import Github; g = Github('token'); print(g.get_user().login)"

# Test Memgraph connection
python agentic_sdlc/intelligence/knowledge_graph/test_memgraph_connection.py
```

## Performance

### Optimization Tips

1. **Cache results** - Avoid redundant API calls
2. **Batch operations** - Process multiple items together
3. **Async operations** - Use async/await for I/O
4. **Connection pooling** - Reuse database connections
5. **Rate limiting** - Respect API limits

### Benchmarks

- **GitHub sync:** ~2-5 seconds per sprint
- **Memgraph sync:** ~5-10 seconds for 100 entries
- **Research agent:** ~3-8 seconds per query
- **Setup scripts:** ~1-2 seconds

## Security

### Best Practices

1. **Never commit secrets** - Use .env files
2. **Use environment variables** - Not hardcoded values
3. **Validate inputs** - Sanitize user input
4. **Secure connections** - Use HTTPS/TLS
5. **Minimal permissions** - Least privilege principle

### API Token Security

```bash
# .env file (never commit!)
GITHUB_TOKEN=ghp_...
MEMGRAPH_PASSWORD=...

# .gitignore
.env
*.env
```

## Related Documentation

- **CLI Guide:** `../docs/CLI-GUIDE.md`
- **Architecture:** `../docs/ARCHITECTURE.md`
- **Workflows:** `../.agent/workflows/README.md`


## Support

### Questions?
- Check individual tool README files
- Review example configurations
- Test with dry-run mode first

### Issues?
- Check error logs
- Verify configuration
- Test dependencies
- Review API quotas

### Contributions?
- Follow tool template
- Add comprehensive README
- Include tests
- Update this overview

---

**Version:** 1.0.0  
**Created:** 2026-01-02  
**Purpose:** Support scripts for bin/ CLI and .agent/ workflows
