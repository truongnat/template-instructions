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
python tools/brain/brain_cli.py status

# 2. Get model recommendation
python tools/knowledge_graph/brain_parallel.py --recommend "[task description]"
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
# (Conceptual halt, or use brain_cli if implemented)

# 3. Fix the issue
# 4. Resume only after fix verified
```

#### Gate 4: POST-TASK (After Completion)
```bash
# 1. Trigger learning
python tools/knowledge_graph/learning_engine.py --record-success ...

# 2. Sync to Neo4j
python tools/knowledge_graph/brain_parallel.py --sync
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
python tools/brain/brain_cli.py status

# 2. Get model recommendation (for complex tasks)
python tools/knowledge_graph/brain_parallel.py --recommend "[task description]"
```

**After COMPLETING any task:**
```bash
# 1. Trigger learning
python tools/knowledge_graph/learning_engine.py --record-success ...

# 2. Sync to Neo4j
python tools/knowledge_graph/brain_parallel.py --sync
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
   python tools/knowledge_graph/brain_parallel.py --sync
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
└── workflows/                   # 16 workflow definitions
    ├── brain.md, cycle.md, orchestrator.md, etc.

tools/                           # 🧠 LAYER 3: INFRASTRUCTURE (Tools)
├── brain/                       # Brain CLI and State Manager
├── knowledge_graph/             # Neo4j and Learning Engine
├── workflows/                   # Workflow scripts
└── ...
```
