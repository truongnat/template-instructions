---
description: Support - New Agent Onboarding Workflow
---

# /onboarding - Agent Onboarding

## ⚠️ PURPOSE
Quick ramp-up workflow for new AI agent sessions joining the project. Accelerates context building.

// turbo-all

## When to Use

- Starting a new AI agent session
- Switching context to this project
- After long absence from project

## Quick Commands

```bash
# Check project status
agentic-sdlc brain status

# View recent activity
git log --oneline -20
```

## Workflow Steps

### 1. Read Core Documents
**MANDATORY reading in order:**

1. **GEMINI.md** - Agent instructions and rules
   ```bash
   cat GEMINI.md
   ```

2. **README.md** - Project overview
   ```bash
   cat README.md
   ```

3. **CHANGELOG.md** - Recent changes
   ```bash
   head -100 CHANGELOG.md
   ```

### 2. Understand Project Structure
```bash
# View top-level structure
ls -la

# View .agent structure
ls -la .agent/

# View tools
ls -la tools/
```

### 3. Check Current State
```bash
# Brain status
agentic-sdlc brain status

# Current sprint
ls docs/sprints/

# Active issues
gh issue list --limit 10
```

### 4. Search Knowledge Base
```bash
# Get overview of KB
agentic-sdlc kb list

# Search for recent entries
agentic-sdlc kb search "recent"
```

### 5. Review Active Work
```bash
# Check branches
git branch -a

# Check open PRs
gh pr list

# Check open issues
gh issue list
```

### 6. Context Checklist
By end of onboarding, you should know:

- [ ] Project purpose and goals
- [ ] Current sprint and priorities
- [ ] Active issues/PRs
- [ ] Key technologies used
- [ ] Available tools and workflows
- [ ] Team communication patterns

## Quick Reference Card

| What | Where |
|------|-------|
| Agent rules | `GEMINI.md` |
| Project overview | `README.md` |
| Workflows | `.agent/workflows/` |
| Roles | `.agent/skills/` |
| Templates | `.agent/templates/` |
| Tools | `tools/` |
| Sprint docs | `docs/sprints/sprint-[N]/` |

## Shortcuts for Common Tasks

| Task | Command/Workflow |
|------|------------------|
| New feature | `/orchestrator` |
| Quick fix | `/cycle` |
| Investigation | `/explore` |
| Production issue | `/emergency` |
| Code review | `/review` |
| Debugging | `/debug` |

#onboarding #context #ramp-up #new-session

## ⏭️ Next Steps
- **If Setup Complete:** Trigger `/sprint` to check tasks
- **If Task Assigned:** Trigger `/cycle` to start work

---

## ENFORCEMENT REMINDER
Always read GEMINI.md before starting work.
