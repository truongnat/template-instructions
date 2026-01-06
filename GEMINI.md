# GEMINI.md - Brain System Documentation

> **⚠️ MANDATORY COMPLIANCE:** This document contains RULES that MUST be followed for ALL tasks. Non-compliance is NOT acceptable.

---

## 🚨 MANDATORY ENFORCEMENT RULES

> [!CAUTION]
> **THESE RULES ARE NON-NEGOTIABLE.** Before executing ANY task, you MUST complete the pre-flight checklist below.

### Pre-Flight Checklist (REQUIRED for ALL Tasks)

Before starting ANY work, complete these steps IN ORDER:

1. **READ THE WORKFLOW FILE** - If user mentions `/slash`, read `.agent/workflows/[slash].md` FIRST
2. **IDENTIFY ROLES** - Determine which `@ROLE` agents should be activated
3. **INITIALIZE STATE** - Run `python tools/brain/brain_cli.py status` to check current state
4. **ANNOUNCE START** - Log the task start (conceptually, no actual command needed)

### Slash Command Interpretation

When user types a slash command, you MUST:

| User Input | REQUIRED Action |
|------------|-----------------|
| `/auto` or `/orchestrator` | Read `.agent/workflows/orchestrator.md` and follow ALL phases |
| `/cycle` | Read `.agent/workflows/cycle.md` and follow ALL steps |
| `/brain` | Read `.agent/workflows/brain.md` and execute commands |
| `/explore` | Read `.agent/workflows/explore.md` for deep investigation |
| `/sprint` | Read `.agent/workflows/sprint.md` for sprint management |
| `/emergency` | Read `.agent/workflows/emergency.md` for hotfix |
| `/commit` | Read `.agent/workflows/commit.md` for git commit |
| Any `/command` | Read `.agent/workflows/[command].md` BEFORE doing anything |

### Role Activation Matrix

For ANY task, activate the appropriate roles based on task type:

| Task Type | Required Roles | Workflow |
|-----------|---------------|----------|
| New Feature/Project | @PM → @SA → @UIUX → @DEV → @TESTER | `/orchestrator` |
| Bug Fix | @DEV → @TESTER | `/cycle` |
| Investigation | @SA → @DEV | `/explore` |
| Hotfix/Emergency | @DEV → @DEVOPS | `/emergency` |
| Documentation | @PM → @REPORTER | `/cycle` |

### 🚨 CRITICAL ENFORCEMENT GATES (6 MANDATORY)

> [!CAUTION]
> **ALL 6 GATES ARE NON-NEGOTIABLE.** Skipping any gate is a protocol violation.

#### Gate 1: PRE-TASK (Before Starting)
```bash
# 1. Check brain state
python tools/brain/observer.py --status

# 2. Get model recommendation
python tools/brain/model_optimizer.py --recommend "[task description]"

# 3. For small tasks, consider A/B testing
python tools/brain/ab_tester.py --create "[task]"
```

#### Gate 2: PLANNING (Before Code)
- **MUST create** `implementation_plan.md` for any feature/change
- **MUST get user approval** before writing code
- Simple tasks: At minimum, outline steps in task.md

#### Gate 3: ERROR HANDLING (On Any Failure)
If ANY script or command fails:
```bash
# 1. STOP immediately - do NOT continue
# 2. Halt the system
python tools/brain/observer.py --halt "[error description]"

# 3. Fix the issue
# 4. Resume only after fix verified
python tools/brain/observer.py --resume
```

#### Gate 4: POST-TASK (After Completion)
```bash
# 1. Trigger learning
python tools/brain/learner.py --learn "[task description]"

# 2. Score REPORTS (not code files!)
# Judge is for: walkthroughs, plans, reports in docs/
python tools/brain/judge.py --score "docs/walkthroughs/[date]-[name].md"

# 3. Analyze for improvements
python tools/brain/self_improver.py --analyze

# 4. Create improvement plan (if issues found)
python tools/brain/self_improver.py --plan

# 5. Sync to Neo4j
python tools/neo4j/brain_parallel.py --sync
```

#### Gate 5: REPORTING (Mandatory Artifacts)
- **MUST create** `walkthrough.md` documenting:
  - What was done
  - What was tested
  - Validation results
- **MUST save** to `docs/walkthroughs/[date]-[name].md`

#### Gate 6: CLEANUP (After Every Session)
```bash
# Run housekeeping
python tools/workflows/housekeeping.py
```

### 🧠 Brain Protocol (MANDATORY)

The Brain Root Layer components MUST be used during agent sessions:

**Before STARTING any task:**
```bash
# 1. Check system status
python tools/brain/observer.py --status

# 2. Get model recommendation (for complex tasks)
python tools/brain/model_optimizer.py --recommend "[task description]"
```

**After COMPLETING any task:**
```bash
# 1. Trigger learning
python tools/brain/learner.py --learn "[task description]"

# 2. Score artifacts (if reports/docs created)
python tools/brain/judge.py --score "[artifact path]"

# 3. Sync to Neo4j
python tools/neo4j/brain_parallel.py --sync
```

**Periodically (per sprint or weekly):**
```bash
# Analyze patterns and create improvement plans
python tools/brain/self_improver.py --analyze
python tools/brain/self_improver.py --plan
```

---

> [!IMPORTANT]
> **FAILURE TO FOLLOW THESE RULES** means the brain system is not being used correctly. If you find yourself implementing without reading workflows, STOP and restart with the pre-flight checklist.

### 📦 Artifact Persistence Rule (MANDATORY)

> [!CAUTION]
> **ALL task results, reports, and IDE-generated artifacts MUST be persisted to docs and synced to Neo4j.**

After completing ANY task:

1. **Save artifacts to project docs:**
   ```bash
   # Implementation plans → docs/sprints/sprint-[N]/plans/
   # Walkthroughs → docs/walkthroughs/
   # Reports → docs/reports/
   # Analysis → docs/artifacts/
   ```

2. **Sync to Neo4j:**
   ```bash
   agentic-sdlc kb compound sync
   ```

3. **Record in learning engine:**
   ```bash
   agentic-sdlc learn --record-success "[task-id]" --task-type "[type]"
   ```

| Artifact Type | Save Location | Neo4j Sync |
|---------------|---------------|------------|
| Implementation plans | `docs/sprints/sprint-[N]/plans/` | ✅ |
| Walkthroughs | `docs/walkthroughs/` | ✅ |
| Analysis reports | `docs/reports/` | ✅ |
| IDE artifacts | `docs/artifacts/` | ✅ |
| **Solutions** | `docs/solutions/` | ✅ |

**Enforcement:**
- ❌ No silent completion - every task produces a persisted artifact
- ❌ No orphan artifacts - IDE artifacts MUST be copied to project docs
- ❌ No unsynced knowledge - all learnings MUST sync to Neo4j

---

> **Universal Guide:** This document describes the `.agent/` brain system in an IDE-agnostic way. Use this guide with **any AI-powered IDE** (Cursor, Windsurf, Cline, Aider, etc.) or CLI tools.

---

## 🧠 What is the Brain System?

The **Brain** is the core of Agentic SDLC - an intelligent, self-learning knowledge management system. It provides:

1. **3-Layer Concentric Architecture** - Core → Intelligence → Infrastructure (like Clean Architecture)
2. **AI Role System** - 13 specialized agents (PM, BA, SA, Dev, QA, etc.)
3. **Workflow Automation** - 18 predefined workflows accessible via `/slash` commands
4. **Knowledge Base** - Compound learning from every task, bug, and solution
5. **Cross-IDE Compatibility** - Works with any IDE through standard markdown files
6. **Self-Learning Engine** - Automatically improves from project experience
7. **Multi-Agent Teams** - AutoGen-powered autonomous agent collaboration

### 3-Layer Concentric Architecture (v3.0)

```
            ┌─────────────────────────────────────────────────────────────────────┐
            │                        LAYER 3: INFRASTRUCTURE                       │
            │   ┌──────────────────────────────────────────────────────────────┐  │
            │   │                    LAYER 2: INTELLIGENCE                      │  │
            │   │   ┌──────────────────────────────────────────────────────┐   │  │
            │   │   │                  LAYER 1: CORE                        │   │  │
            │   │   │                                                       │   │  │
            │   │   │   ╔═══════════════════════════════════════════════╗  │   │  │
            │   │   │   ║  GEMINI.md   ║  skills/  ║  rules/  ║ templates  │   │  │
            │   │   │   ║  (SoT)       ║ (13 roles)║(5 files) ║ (17 files) │   │  │
            │   │   │   ╚═══════════════════════════════════════════════╝  │   │  │
            │   │   │                                                       │   │  │
            │   │   └───────────────────────────────────────────────────────┘   │  │
            │   │                              ↑                                │  │
            │   │   ╔═══════════════════════════════════════════════════════╗  │  │
            │   │   ║ scorer │ ab_test │ self_learning │ artifact_gen      ║  │  │
            │   │   ║ router │ proxy   │ task_manager  │ monitor   │ judge ║  │  │
            │   │   ║ performance                                           ║  │  │
            │   │   ╚═══════════════════════════════════════════════════════╝  │  │
            │   │                                                               │  │
            │   └───────────────────────────────────────────────────────────────┘  │
            │                                  ↑                                   │
            │   ╔═══════════════════════════════════════════════════════════════╗ │
            │   ║  tools/  │  docs/  │  workflows/  │  projects/  │ mcp/ │ cli/ ║ │
            │   ╚═══════════════════════════════════════════════════════════════╝ │
            │                                                                      │
            └──────────────────────────────────────────────────────────────────────┘
```

### Layer Details

| Layer | Content | Purpose |
|-------|---------|---------|
| **Layer 1: Core** | GEMINI.md, skills/, rules/, templates/ | Stable foundation, rarely changes |
| **Layer 2: Intelligence** | scorer, ab_test, self_learning, artifact_gen, router, proxy, task_manager, monitor, performance, judge | Brain intelligence, self-improvement |
| **Layer 3: Infrastructure** | tools/, docs/, workflows/, projects/, mcp/, cli/ | External interfaces, storage |

### Dependency Rule
```
Layer 3 → Layer 2 → Layer 1 (dependencies flow inward only)
```

---

## 📁 Directory Structure

```
.agent/                          # 🧠 LAYER 1: CORE
│
├── skills/                      # 13 AI role definitions
│   ├── role-pm.md              # Project Manager
│   ├── role-dev.md             # Developer
│   └── ...                     # + 11 more roles
│
├── rules/                       # 5 rule files
│   ├── global.md               # Core SDLC flow
│   └── ...
│
├── templates/                   # 17 document templates
│
└── workflows/                   # 18 workflow definitions
    ├── brain.md, cycle.md, orchestrator.md, etc.

tools/layer2/                    # 🧠 LAYER 2: INTELLIGENCE
├── scorer/                      # Input/output quality scoring
├── ab_test/                     # A/B testing engine
├── self_learning/               # Pattern recognition
├── artifact_gen/                # Artifact generation
├── router/                      # Workflow/agent routing
├── proxy/                       # Model cost optimization
├── task_manager/                # Kanban-style management
├── monitor/                     # Compliance monitoring
└── performance/                 # Flow optimization

mcp/                             # 🌐 LAYER 3: MCP CONNECTORS
├── connectors/                  # filesystem, github, api
└── protocol.py                  # MCP protocol handler
```

---


## 🎯 Core Components

### 1. Workflows (`.agent/workflows/`)

**What:** Step-by-step automation for SDLC tasks
**How to use:** Reference workflows in your IDE or use `/slash` commands

**Key Workflows (12 total):**

| Command | Purpose | What It Does |
|---------|---------|--------------|
| `/brain` | Brain Management | Sync knowledge, get stats, state control |
| `/cycle` | Task Lifecycle | Plan → Work → Review → Document |
| `/explore` | Deep Investigation | Multi-order analysis before planning |
| `/orchestrator` | Full Automation | Complete SDLC from planning to deployment |
| `/sprint` | Sprint Management | Sprint planning and tracking |
| `/emergency` | Hotfix Response | Critical incidents & production fixes |
| `/validate` | System Validation | Check system health and configuration |
| `/metrics` | Metrics Dashboard | View project metrics and statistics |
| `/release` | Release Management | Version bumping and changelog generation |
| `/route` | Workflow Routing | Intelligently route requests to workflows |
| `/compound` | Knowledge Capture | Document solutions for future reuse |
| `/housekeeping` | Maintenance | Cleanup and file organization |
| `/commit` | Smart Commit | Review, message generation, commit, and push |
| `/autogen` | Multi-Agent Teams | AutoGen-powered task execution |

**Workflow Structure:**

```markdown
---
description: Brief workflow description
---

# Workflow Title

## Step 1: [Action]
[Detailed instructions]

## Step 2: [Action]
[Detailed instructions]

### Decision Point:
- If [condition] → Go to Step X
- Otherwise → Continue

#workflow-tag #skill-tag
```

### 2. Skills (`.agent/skills/`)

**What:** Specialized AI agent definitions for each SDLC phase
**How to use:** Reference with `@ROLE` mentions in your IDE

**Available Roles:**

```
📋 Planning & Requirements
  ├── @PM          - Project Manager (planning, backlog, reporting)
  └── @BA          - Business Analyst (requirements)

🎨 Design & Architecture
  ├── @SA          - System Analyst (architecture)
  └── @UIUX        - UI/UX Designer (interface design)

✅ Review & Quality
  ├── @SECA        - Security Analyst (security review)
  └── @TESTER      - Quality Assurance & Testing

💻 Development & Operations
  ├── @DEV         - Developer (implementation)
  └── @DEVOPS      - DevOps Engineer (CI/CD, deployment)

🤖 Automation
  └── @ORCHESTRATOR - Workflow orchestrator
```

**Role Definition Structure:**

```markdown
# @ROLE - Role Title

## Identity
[Who this role is, responsibilities]

## Commands
[Available commands and workflows]

## Integration
[How this role works with others]

## Templates Used
[Document templates this role creates]

#role-tag #skills-enabled
```



### 4. Templates (`.agent/templates/`)

**What:** Standardized document templates for consistency
**How to use:** Roles use templates to create project artifacts

**Available Templates:**

```
Planning & Requirements:
  ├── project-plan.md
  ├── requirements-spec.md
  └── user-stories.md

Design & Architecture:
  ├── architecture-spec.md
  ├── backend-design-spec.md
  ├── uiux-design-spec.md
  └── api-design.md

Quality & Security:
  ├── design-verification-report.md
  ├── security-review-report.md
  └── test-report.md

Development & Delivery:
  ├── implementation-log.md
  ├── deployment-plan.md
  ├── final-report.md
  └── changelog-entry.md

Documentation:
  ├── technical-documentation.md
  └── user-guide.md
```

### 5. Rules (`.agent/rules/`)

**What:** Global conventions that all agents must follow
**Why:** Ensures consistency, quality, and traceability

**Rule Files:**

| File | Purpose |
|------|---------|
| `global.md` | Core SDLC flow, role dependencies, approval gates |
| `artifacts.md` | File naming, folder structure, sprint-based organization |
| `git-workflow.md` | Task tracking, atomic commits, branching strategy |
| `auto-learning.md` | Automatic knowledge capture triggers |

---

## 🔧 How to Use with Any IDE

### Option 1: Cursor IDE

1. **Install Agentic SDLC:**
   ```bash
   agentic-sdlc install
   agentic-sdlc ide cursor
   ```

2. **Use in Chat:**
   ```
   @pm Build a todo app
   /cycle Implement user authentication
   ```

3. **Access Brain:**
   ```
   /brain
   /kb-search authentication
   ```

### Option 2: Windsurf IDE

1. **Install:**
   ```bash
   agentic-sdlc install
   agentic-sdlc ide windsurf
   ```

2. **Reference in Cascade:**
   - Windsurf automatically reads `.agent/` files
   - Use `@` mentions for roles
   - Use `/` commands for workflows

### Option 3: Cline / Aider / Other IDEs

1. **Install:**
   ```bash
   agentic-sdlc install
   ```

2. **Manual Integration:**
   - Point your IDE to `.agent/workflows/` directory
   - Reference skill files in `.agent/skills/`
   - Use workflows as instruction templates

3. **In Chat:**
   ```
   Read .agent/workflows/pm.md and help me plan a new feature
   Act as @DEV and follow .agent/workflows/dev.md
   ```

### Option 4: CLI / Command Line

```bash
# Universal JS CLI (Bridge to Python tools)
agentic-sdlc release --help
agentic-sdlc workflow cycle

# View workflows
ls .agent/workflows/

# Read a workflow
cat .agent/workflows/pm.md

# Use brain system
python tools/neo4j/brain_parallel.py --recommend "OAuth implementation"
```

---

## 🧠 Brain Intelligence System

The brain consists of **three interconnected layers:**

### Layer 1: LEANN (Vector Search)

**What:** High-performance vector database for semantic search
**Location:** `.leann/` directory (auto-generated)

```bash
# Index project
leann index --path .

# Update index
leann index --update

# Search (used by Research Agent)
leann search "authentication patterns"
```

### Layer 2: Neo4j (Knowledge Graph)

**What:** Graph database mapping skills, technologies, and relationships
**Location:** Cloud-hosted (configured in `.env`)

**Capabilities:**
- Visualize skill relationships
- Find learning paths
- Discover related technologies
- Track team expertise
- Reason about solutions

**Configuration (`.env`):**

```bash
NEO4J_URI=neo4j+s://xxxxx.databases.neo4j.io
NEO4J_USERNAME=neo4j
NEO4J_PASSWORD=your-password
NEO4J_DATABASE=neo4j
```

**Usage:**

```bash
# Sync KB to Neo4j
python tools/neo4j/sync_skills_to_neo4j.py

# Sync documents (plans, reports, artifacts)
python tools/neo4j/document_sync.py --all

# Query skills
python tools/neo4j/query_skills_neo4j.py --all-skills

# Get learning path
python tools/neo4j/query_skills_neo4j.py --learning-path "Authentication"
```



### Brain Workflows (Parallel Execution)

**Quick Sync (Recommended):**

```bash
# Sync all brain systems in parallel
python tools/neo4j/brain_parallel.py --sync
```

**Full Operations:**

```bash
# Complete sync (LEANN + Neo4j + Learning Engine)
python tools/neo4j/brain_parallel.py --full

# Get statistics
python tools/neo4j/brain_parallel.py --stats

# Get recommendations
python tools/neo4j/brain_parallel.py --recommend "implement caching"
```

**Self-Learning Commands:**

```bash
# Record error pattern
python tools/neo4j/learning_engine.py --record-error "TypeError" \
  "Cannot read property X of undefined" \
  --resolution "Added null check" \
  --approach "defensive_coding"

# Record success pattern
python tools/neo4j/learning_engine.py --record-success "task-123" \
  --task-type "auth_feature" \
  --success-approach "JWT with refresh tokens"

# Find similar errors
python tools/neo4j/learning_engine.py --similar-errors "ConnectionError"

# Get recommendations
python tools/neo4j/learning_engine.py --recommend \
  "implement user authentication"
```

**Statistics & Insights:**

```bash
# Learning statistics
python tools/neo4j/learning_engine.py --stats

# View learned patterns
python tools/neo4j/learning_engine.py --patterns

# View reasoning paths
python tools/neo4j/learning_engine.py --reasoning-path "TypeError" "null check"
```

---

## 🔄 Self-Learning Triggers

The brain **automatically learns** when these events occur:

| Trigger | What Gets Learned |
|---------|-------------------|
| Bug fixed (medium+ priority) | Error pattern, resolution, similar issues |
| Task required 3+ attempts | Complexity patterns, better approaches |
| Same error occurred 2+ times | Root cause, prevention strategy |
| Complex feature completed (4+ hours) | Implementation approach, best practices |
| Security/performance issue resolved | Vulnerability patterns, optimization techniques |

**How it works:**

1. **Detection** - Agent detects qualifying event
2. **Capture** - Automatically extracts:
   - Problem description
   - Solution approach
   - Code patterns
   - Related technologies
3. **Storage** - Saves to:
   - Neo4j graph (relationships)
   - LEANN index (semantic search)
4. **Indexing** - Updates:
   - Neo4j relationships
   - LEANN vectors
5. **Future Use** - Available for:
   - Recommendations
   - Similar problem detection
   - Learning path suggestions

---

## 📊 Best Practices

### Daily Workflow

```bash
# Morning: Sync brain
python tools/neo4j/brain_parallel.py --sync

# Before new task: Get recommendations
python tools/neo4j/brain_parallel.py --recommend "your task description"

# During work: Use workflows
/pm plan feature
/dev implement
/qa review

# After work: Check what was learned
python tools/neo4j/learning_engine.py --stats
```

### Weekly Maintenance

```bash
# Full brain sync
python tools/neo4j/brain_parallel.py --full

# Check learning patterns
python tools/neo4j/learning_engine.py --patterns
```

### Team Collaboration

```bash
# Share brain via Git
git add .agent/knowledge-base/
git commit -m "docs: add OAuth implementation knowledge"
git push

# Pull team knowledge
git pull

# Re-sync brain
python tools/neo4j/brain_parallel.py --sync
```

---

## 🎨 IDE-Specific Integration

### For Cursor

**Setup:**
```bash
agentic-sdlc ide cursor
```

**Created files:**
- `.cursorrules` - References `.agent/` workflows
- Automatic role recognition with `@` mentions
- `/slash` command integration

**Usage:**
```
@pm Build a REST API
/dev implement authentication
/brain sync and recommend
```

### For Windsurf

**Setup:**
```bash
agentic-sdlc ide windsurf
```

**Created files:**
- `.windsurfrules` - References `.agent/` workflows
- Cascade integration
- Memory persistence

**Usage:**
```
@sa design the architecture
/cycle complete this feature
```

### For Cline

**Setup:**
```bash
agentic-sdlc ide cline
```

**Created files:**
- `.clinerules` - References `.agent/` workflows
- Custom instructions

**Usage:**
```
Read .agent/workflows/dev.md and implement this feature
Act as @QA and review the implementation
```

### For Aider

**Setup:**
```bash
agentic-sdlc ide aider
```

**Created files:**
- `.aider.conf.yml` - References `.agent/` workflows

**Usage:**
```bash
# In terminal
aider --read .agent/workflows/dev.md
aider --message "Act as @DEV and implement authentication"
```

---

## 🔧 Tools & Utilities

All executable tools are located in `tools/` directory:

```
tools/
├── neo4j/                   # Knowledge graph tools
│   ├── brain_parallel.py   # Parallel brain operations
│   ├── learning_engine.py  # Self-learning engine
│   ├── document_sync.py    # Document synchronization
│   └── sync_skills_to_neo4j.py
│
├── research/                # Research agent
│   ├── research_agent.py   # Automated research
│   └── research_mcp.py     # MCP integration
│
├── kb/                      # Knowledge base management
│   ├── kb_manager.py       # KB operations
│   └── update_index.py     # Index generation
│
├── github/                  # GitHub integration
│   └── sync_issues.py      # Issue synchronization
│
└── workflows/               # Workflow automation
    └── [workflow scripts]
```

**See `tools/README.md` for complete tool documentation.**

---

## 💡 Advanced Usage

### Research Agent Integration

The Research Agent automatically queries the brain when researching:

```bash
python tools/research/research_agent.py \
  --task "authentication" \
  --type feature

# Output includes:
# - LEANN semantic search results
# - Neo4j graph relationships
# - File-based KB entries
# - Confidence level
```

### Custom Workflows

Create your own workflows in `.agent/workflows/`:

```markdown
---
description: My Custom Workflow
---

# Custom Workflow

## Step 1: [Action]
[Instructions]

## Step 2: [Action]
[Instructions]

#custom #workflow
```

### Knowledge Base Search

```bash
# CLI search
python bin/kb_cli.py search "authentication"

# In IDE
/kb-search authentication

# Advanced search
python bin/kb_cli.py search "JWT" --category security --tags oauth
```

### Compound Learning

**Concept:** Knowledge from one project benefits all projects in the monorepo.

**How it works:**
1. Project A solves OAuth authentication
2. Knowledge saved to `.agent/knowledge-base/`
3. Project B needs authentication
4. Brain recommends OAuth approach from Project A
5. Project B adapts and improves solution
6. Updated knowledge benefits Projects C, D, E...

```bash
# Trigger compound learning
python tools/neo4j/brain_parallel.py --full

# View cross-project knowledge
python bin/kb_cli.py list --all-projects
```

---

## 🌟 Why This Structure?

### Single Source of Truth

✅ All knowledge in `.agent/`
✅ IDE integrations are just references
✅ Update once, available everywhere

### IDE Agnostic

✅ Works with any IDE
✅ Markdown-based (human-readable)
✅ CLI-accessible
✅ Git-friendly

### Scalable

✅ Add new roles easily
✅ Create custom workflows
✅ Extend knowledge categories
✅ Cross-project learning

### Maintainable

✅ Clear structure
✅ YAML metadata for automation
✅ Version-controllable
✅ Documentable

---

## 🚀 Quick Reference

### Most Used Commands

```bash
# Brain sync
python tools/neo4j/brain_parallel.py --sync

# Get recommendations
python tools/neo4j/brain_parallel.py --recommend "task description"

# Search KB
python bin/kb_cli.py search "query"

# View stats
python tools/neo4j/brain_parallel.py --stats
```

### Most Used Workflows

```
/brain        - Brain management (sync, status, route)
/cycle        - Complete task lifecycle
/orchestrator - Full SDLC automation
/explore      - Deep investigation
/sprint       - Sprint management
/release      - Release & changelog
```

### Most Used Roles

```
@PM    - Planning
@SA    - Architecture
@DEV   - Implementation
@QA    - Review
@SECA  - Security
```

---

## 📚 Additional Resources

- **Project Documentation:** [docs/](docs/)
- **Tools README:** [tools/README.md](tools/README.md)
- **Monorepo Architecture:** [docs/MONOREPO-ARCHITECTURE.md](docs/MONOREPO-ARCHITECTURE.md)
- **Quick Start Guide:** [docs/guides/QUICK-START.md](docs/guides/QUICK-START.md)
- **MCP Setup:** [docs/guides/MCP-SETUP.md](docs/guides/MCP-SETUP.md)

---

## ❓ FAQ

**Q: Can I use this without Neo4j?**
A: Yes! The file-based KB and LEANN work independently. Neo4j adds graph intelligence but is optional.

**Q: Does this work offline?**
A: Partially. File-based KB and LEANN work offline. Neo4j requires internet connection.

**Q: Can I customize workflows?**
A: Absolutely! Add your own workflows to `.agent/workflows/` following the existing format.

**Q: How do I share knowledge with my team?**
A: Commit `.agent/knowledge-base/` to Git. Team members sync brain after pulling.

**Q: What if my IDE isn't supported?**
A: All IDEs can reference `.agent/` files. Create custom integration or use CLI tools.

**Q: How do I migrate from another system?**
A: Run `agentic-sdlc install` in your project. It preserves existing code and adds the brain system.

---

**Version:** 2.0.0
**Last Updated:** 2026-01-03
**Philosophy:** IDE-agnostic, compound learning, single source of truth

**Next:** Read [Quick Start Guide](docs/guides/QUICK-START.md) or explore [workflows](.agent/workflows/)
