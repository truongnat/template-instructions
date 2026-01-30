# 🔬 Workflow Analysis Report: Add/Remove Recommendations

**Date:** 2026-01-05  
**Purpose:** Deep analysis of `.agent/workflows/` to recommend additions and removals

---

## 📊 Current Workflow Inventory (13 workflows)

| Workflow | Type | Size | Purpose |
|----------|------|------|---------|
| `brain.md` | Support | 2.6KB | Meta-level controller, sync, learning |
| `compound.md` | Support | 1.0KB | Knowledge capture after tasks |
| `cycle.md` | Process | 2.0KB | Task lifecycle (plan→work→review) |
| `emergency.md` | Process | 3.3KB | Hotfix/incident response |
| `explore.md` | Process | 3.5KB | Deep investigation |
| `housekeeping.md` | Support | 2.9KB | Cleanup and maintenance |
| `metrics.md` | Utility | 3.9KB | Project statistics |
| `orchestrator.md` | Process | 2.2KB | Full SDLC automation |
| `preflight.md` | Support | 1.0KB | Pre-task checks |
| `release.md` | Support | 3.5KB | Changelog & versioning |
| `route.md` | Support | 3.5KB | Workflow selection helper |
| `sprint.md` | Process | 3.3KB | Sprint lifecycle |
| `validate.md` | Utility | 3.7KB | Workflow compliance check |

---

## 🔴 RECOMMEND REMOVAL (3 workflows)

### 1. ❌ REMOVE: `preflight.md`

**Reason:**
- **Redundancy:** This workflow duplicates the "Enforcement Reminder" that already exists at the bottom of EVERY workflow file
- **Not automated:** Contains manual steps that AI agents already follow naturally
- **Low value:** The GEMINI.md already enforces pre-flight checks via the "Pre-Flight Checklist" section
- **Confusion:** Having both `preflight.md` AND enforcement reminders in each workflow creates duplication

**Evidence:**
```markdown
# Every workflow ends with:
## ENFORCEMENT REMINDER
Before executing, complete /preflight checks.
```

**Alternative:** The enforcement is already embedded. Remove this standalone workflow.

---

### 2. ❌ REMOVE: `route.md`

**Reason:**
- **Redundancy with GEMINI.md:** The routing logic is already documented in `GEMINI.md` under "Role Activation Matrix" and "Slash Command Interpretation"
- **Static content:** Contains no executable commands - it's purely reference documentation
- **Better placement:** This should be reference documentation in `.agent/rules/` or `GEMINI.md`, not a workflow
- **No /route command exists:** The routing happens automatically via `/orchestrator` and brain

**Evidence:**
- GEMINI.md already has:
  ```markdown
  ### Role Activation Matrix
  | Task Type | Required Roles | Workflow |
  |-----------|---------------|----------|
  | New Feature/Project | @PM → @SA → @UIUX → @DEV → @TESTER | /orchestrator |
  ```

**Alternative:** Merge key content into `GEMINI.md` or `.agent/rules/global.md`

---

### 3. ❌ CONSIDER REMOVING: `compound.md`

**Reason:**
- **Already embedded in other workflows:** Both `/cycle` and `/emergency` already include compound learning steps (Step 7 in cycle, Step 7 in emergency)
- **Very short (1KB):** Not enough value as standalone workflow
- **Rarely invoked directly:** Users should use `/cycle` or `/emergency` which include compound learning

**Evidence from cycle.md:**
```markdown
### 7. Self-Learning (MANDATORY)
agentic-sdlc kb compound sync
agentic-sdlc learn --record-success "TASK-ID" --task-type "feature"
```

**Alternative:** Keep as reference but mark as "called automatically by other workflows"

---

## 🟢 RECOMMEND ADDING (5 new workflows)

### 1. ✅ ADD: `/review.md` - Code Review Workflow

**Rationale:**
- **Gap identified:** No dedicated workflow for PR reviews
- **Current state:** `@TESTER` does design verification but no code review workflow
- **High frequency task:** Code reviews happen daily

**Proposed content:**
- Quick PR review checklist
- Integration with GitHub PR comments
- Calling `@TESTER` and `@SECA` for specialized reviews
- Link to KB for similar code patterns

---

### 2. ✅ ADD: `/debug.md` - Debugging Workflow

**Rationale:**
- **Gap identified:** No workflow for systematic debugging
- **Different from /emergency:** Emergency is for production issues; debug is for local development
- **High complexity task:** Debugging often takes 3+ hours, needs structure

**Proposed content:**
- Systematic debug steps (reproduce → isolate → identify → fix → verify)
- Log analysis commands
- Common debugging tools
- KB search for similar bugs
- Integration with `/compound` for learning

---

### 3. ✅ ADD: `/refactor.md` - Refactoring Workflow

**Rationale:**
- **Gap identified:** No workflow for safe refactoring
- **High-risk activity:** Refactoring can break existing functionality
- **Quality focus:** Needs verification steps

**Proposed content:**
- Scope definition (what's being refactored)
- Test verification before/after
- Atomic commits
- Code review integration
- **Key:** Run tests before AND after refactoring

---

### 4. ✅ ADD: `/onboarding.md` - New Agent Onboarding

**Rationale:**
- **Gap identified:** No workflow for new AI agents joining project
- **Context needed:** New agents need to understand project structure
- **Accelerate productivity:** Quick ramp-up for new sessions

**Proposed content:**
- Project structure overview
- Key files to read first (`GEMINI.md`, `README.md`)
- Current sprint status
- KB search for relevant context
- Active issues/tasks

---

### 5. ✅ ADD: `/docs.md` - Documentation Workflow

**Rationale:**
- **Gap identified:** No dedicated documentation workflow
- **Current state:** `/cycle` mentions docs but no structure
- **Quality:** Documentation often neglected

**Proposed content:**
- Types of docs (API, user guide, KB entry)
- Template selection
- Review process
- Integration with `/release` for changelog

---

## 🟡 RECOMMEND IMPROVEMENTS (Existing workflows)

### 1. 🔧 IMPROVE: `orchestrator.md`

**Current issues:**
- Very lightweight (2.2KB) for "Full SDLC Automation"
- Missing detailed phase transitions
- No artifact checklists per phase

**Recommendation:**
- Expand with detailed steps per phase
- Add artifact requirements per phase
- Add time estimates

---

### 2. 🔧 IMPROVE: `brain.md`

**Current issues:**
- References non-existent tools: `tools/brain/observer.py`, `tools/brain/judge.py`, etc.
- Only `tools/brain/brain_cli.py` exists

**Recommendation:**
- Update to match actual tool inventory
- Either create missing tools or remove references

---

### 3. 🔧 IMPROVE: `cycle.md`

**Current issues:**
- Team Communication step references tool that may not exist: `tools/communication/cli.py`
- Missing explicit test requirements

**Recommendation:**
- Verify tool existence
- Add explicit "run tests" step

---

## 📋 Summary

| Action | Count | Workflows |
|--------|-------|-----------|
| **Remove** | 2-3 | `preflight.md`, `route.md`, (optionally `compound.md`) |
| **Add** | 5 | `review.md`, `debug.md`, `refactor.md`, `onboarding.md`, `docs.md` |
| **Improve** | 3 | `orchestrator.md`, `brain.md`, `cycle.md` |

---

## 🎯 Priority Order

1. **P0 - Critical:** Add `/review.md` and `/debug.md` (most common use cases)
2. **P1 - Important:** Remove `preflight.md` and `route.md` (reduce confusion)
3. **P2 - Nice to have:** Add `/refactor.md`, `/onboarding.md`, `/docs.md`
4. **P3 - Backlog:** Improve `orchestrator.md`, fix tool references

---

## ❓ Open Questions for User

1. **Compound workflow:** Keep as standalone or merge into cycle/emergency?
2. **Tool references:** Should we create missing brain tools or remove references?
3. **Priority:** Which new workflows should we implement first?
