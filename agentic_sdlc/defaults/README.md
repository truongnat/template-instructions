# Defaults Directory

Default configurations, templates, skills, rules, and workflows for the Agentic SDLC system.

## 📂 Structure

```
defaults/
├── demands/            # Project demand templates
├── ide-integration/    # IDE configuration files
├── projects/           # Sample projects (226 items)
├── rules/              # System rules (8 files)
├── skills/             # AI agent role definitions (17 files)
├── templates/          # Document templates (23 files)
└── workflows/          # Workflow definitions (24 files)
```

## 📋 Contents

### 1. Skills (17 AI Roles)

Agent role definitions with specific responsibilities and workflows:

| Role | File | Purpose |
|------|------|---------|
| **@PM** | `role-pm.md` | Project Manager - Planning, scope, task allocation |
| **@BA** | `role-ba.md` | Business Analyst - Requirements gathering |
| **@PO** | `role-po.md` | Product Owner - Feature prioritization |
| **@SA** | `role-sa.md` | System Analyst - Architecture design |
| **@UIUX** | `role-uiux.md` | UI/UX Designer - Interface design |
| **@DEV** | `role-dev.md` | Developer - Implementation |
| **@TESTER** | `role-tester.md` | Tester - Quality assurance |
| **@SECA** | `role-seca.md` | Security Analyst - Security review |
| **@DEVOPS** | `role-devops.md` | DevOps Engineer - CI/CD, deployment |
| **@MOBILE** | `role-mobile.md` | Mobile Developer - Mobile apps |
| **@GAME** | `role-game.md` | Game Developer - Game development |
| **@CLOUD** | `role-cloud.md` | Cloud Architect - Cloud infrastructure |
| **@ORCHESTRATOR** | `role-orchestrator.md` | Orchestrator - Full automation |
| **@REPORTER** | `role-reporter.md` | Reporter - Documentation |
| **@RESEARCH** | `role-research.md` | Research Agent - Technical research |
| **@STAKEHOLDER** | `role-stakeholder.md` | Stakeholder - Requirements validation |
| **@BRAIN** | `role-brain.md` | Brain - Meta-level system control |

### 2. Rules (8 Rule Files)

System-wide rules and constraints:

| Rule | File | Purpose |
|------|------|---------|
| **Global** | `global.md` | Universal rules for all agents |
| **Artifacts** | `artifacts.md` | Artifact placement and management |
| **Auto-Learning** | `auto-learning.md` | Self-learning protocols |
| **Code Quality** | `code-quality.md` | Code standards and quality gates |
| **Git Workflow** | `git-workflow.md` | Git commit and branching rules |
| **Naming Conventions** | `naming-conventions.md` | File and variable naming |
| **Agent Execution** | `agent-execution.md` | Agent behavior rules |
| **AI Enforcement** | `ai-enforcement.md` | AI-specific constraints |

### 3. Templates (23 Document Templates)

**Planning Templates:**
- `Project-Plan-Template.md`
- `Specification-Template.md`
- `Product-Backlog-Template.md`

**Design Templates:**
- `System-Design-Spec-Template.md`
- `UIUX-Design-Spec-Template.md`

**Development Templates:**
- `Development-Log-Template.md`
- `DevOps-Plan-Template.md`

**Quality Templates:**
- `Test-Report-Template.md`
- `Security-Review-Report-Template.md`
- `Design-Verification-Report-Template.md`

**Delivery Templates:**
- `CHANGELOG-Template.md`
- `Final-Project-Report-Template.md`
- `Final-Approval-Report-Template.md`
- `Master-Documentation-Template.md`

**Intelligence Templates:**
- `observer-report.md` - Observer compliance reports
- `ab-comparison-report.md` - A/B test comparisons
- `quality-score-report.md` - Judge quality scores
- `self-learning-digest.md` - Learning summaries
- `system-health-report.md` - System health status

**Process Templates:**
- `Phase-Report-Template.md`
- `Knowledge-Entry-Template.md`
- `definition-of-done.md`
- `incident-response.md`

### 4. Workflows (24 Workflow Files)

Automated workflow definitions:

**Core Workflows:**
- `/orchestrator` - Full automation workflow
- `/cycle` - Complete task lifecycle
- `/planning` - Planning phase
- `/brain` - Brain system control

**Intelligence Workflows:**
- `/ab` - A/B test generation
- `/observe` - Rule compliance check
- `/score` - Quality scoring
- `/monitor` - System health check

**Process Workflows:**
- `/sprint` - Sprint management
- `/commit` - Automated commit
- `/review` - Code review
- `/refactor` - Safe refactoring
- `/debug` - Systematic debugging
- `/emergency` - Hotfix response

**Support Workflows:**
- `/docs` - Documentation creation
- `/housekeeping` - Cleanup and maintenance
- `/release` - Release management
- `/validate` - Workflow compliance
- `/explore` - Deep investigation

**Advanced Workflows:**
- `/autogen` - Multi-agent task execution
- `/concurrent` - Parallel execution
- `/swarm` - Intelligent routing
- `/synthesize` - MoA synthesis
- `/chat` - Multi-agent chat

### 5. IDE Integration

Configuration files for IDE integration:
- Cursor
- Windsurf
- Other AI-powered IDEs

### 6. Projects

Sample projects demonstrating the system:
- Todo App (full-stack)
- Landing Page
- Telegram File Manager
- FFmpeg Editor
- And 222 more examples

## 🔧 Usage

### Using Skills

Activate a role by mentioning it:
```
@PM create a project plan for a todo app
@DEV implement authentication
@TESTER run integration tests
```

### Using Templates

Generate documents from templates:
```bash
python agentic_sdlc/intelligence/artifact_gen/generator.py \
  --template project-plan \
  --data '{"title": "Todo App"}'
```

### Using Workflows

Execute workflows via slash commands:
```
/orchestrator - Full automation
/cycle - Complete task lifecycle
/planning - Planning phase
```

## 📝 Path Migration (2026-01-29)

All paths have been updated from old `tools/` structure to new `agentic_sdlc/` structure:

**Old → New Mappings:**
- `tools/core/brain/` → `agentic_sdlc/core/brain/`
- `tools/intelligence/` → `agentic_sdlc/intelligence/`
- `tools/infrastructure/` → `agentic_sdlc/infrastructure/`
- `tools/neo4j/` → **DEPRECATED** (use SQLite KB instead)
- `kb compound` commands → `python agentic_sdlc/core/brain/brain_cli.py`

**Migration Stats:**
- Files processed: 72
- Total changes: 162
- Affected: skills (9), rules (1), workflows (14)

## 🚨 Important Notes

### Neo4j/Memgraph References

Neo4j integration has been **deprecated**. The system now uses SQLite for the knowledge graph.

**Old (Deprecated):**
```bash
python tools/neo4j/sync_skills_to_neo4j.py
python tools/neo4j/query_skills_neo4j.py --search "topic"
```

**New (Current):**
```bash
python agentic_sdlc/core/brain/brain_cli.py sync
python agentic_sdlc/core/brain/brain_cli.py search "topic"
```

### KB Commands

**Old:**
```bash
kb compound search "topic"
kb compound add
kb compound sync
```

**New:**
```bash
python agentic_sdlc/core/brain/brain_cli.py search "topic"
python agentic_sdlc/core/brain/brain_cli.py learn
python agentic_sdlc/core/brain/brain_cli.py sync
```

## 🔗 Related

- **Skills**: `.agent/skills/` (active skills copied from defaults)
- **Workflows**: `.agent/workflows/` (active workflows copied from defaults)
- **Templates**: Used by artifact generator
- **Rules**: Enforced by Observer

---

**Version:** 2.0.0  
**Last Updated:** 2026-01-29  
**Migration:** tools/ → agentic_sdlc/ complete
