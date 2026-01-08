---
description: Process - Planning Phase Workflow
---

# /planning - Task Planning Workflow

## ⚠️ PURPOSE
Standardize the planning phase for tasks and sprints. Ensures proper requirements gathering, design, and user approval before implementation.

// turbo-all

## Quick Commands

```bash
# Generate project plan from template
python tools/intelligence/artifact_gen/generator.py --template project-plan --context "[project name]"

# Check brain state
python tools/core/brain/brain_cli.py status

# Transition to planning state
python tools/core/brain/brain_cli.py transition PLANNING --reason "Starting new task"
```

## When to Use

- Starting a new feature or project
- Beginning a new sprint
- Before any significant implementation
- After receiving new requirements

## Workflow Steps

### 1. Initialize Planning State
```bash
python tools/core/brain/brain_cli.py transition PLANNING --reason "New task: [description]"
```

### 2. Gather Requirements
- Review user request
- Search KB for similar implementations
- Identify stakeholders

```bash
python tools/intelligence/research/research_agent.py --task "[feature]" --type general
```

### 3. Create Implementation Plan

Create `implementation_plan.md` with:
- **Goal Description** - What are we building?
- **Proposed Changes** - File-by-file breakdown
- **Verification Plan** - How to test

```bash
python tools/intelligence/artifact_gen/generator.py --template project-plan --context "[description]"
```

### 4. Request User Approval
Present the plan to the user for review.

**Approval Checklist:**
- [ ] Requirements understood
- [ ] Scope is clear
- [ ] Risks identified
- [ ] User approved

### 5. Transition to Execution
Once approved:
```bash
python tools/core/brain/brain_cli.py transition EXECUTION --reason "Plan approved"
```

## Planning Checklist

| Item | Required |
|------|----------|
| Requirements documented | ✅ |
| KB searched | ✅ |
| Implementation plan created | ✅ |
| User approval obtained | ✅ |
| Risks identified | ✅ |

## Artifacts

- `implementation_plan.md` - Detailed plan
- `task.md` - Task checklist
- Sprint folder structure (if new sprint)

## Integration

- **@PM** - Primary owner
- **@BA** - Requirements
- **@SA** - Technical design
- **/orchestrator** - Full SDLC flow
- **/cycle** - Task lifecycle

#planning #requirements #design #approval

## ⏭️ Next Steps
- **If Approved:** Trigger `/cycle` for implementation
- **If Rejected:** Revise plan based on feedback
- **If Complex:** Trigger `/explore` for deeper analysis

---

## ENFORCEMENT REMINDER
Never start coding without an approved plan.
