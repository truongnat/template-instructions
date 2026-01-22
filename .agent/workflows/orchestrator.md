---
description: Process - Orchestrator - Full Automation Workflow
---

# Orchestrator Workflow

> **Master Controller:** [View @BRAIN Skill](../../skills/brain/SKILL.md)
> 
> **⚠️ Supervised by @BRAIN.** Report status on each phase transition.

## ⚠️ STRICT EXECUTION PROTOCOL (MANDATORY)
All phases must be executed in order. No skipping.

## State Machine Integration
This workflow follows the state machine defined in `@BRAIN`. Before each phase transition:
1. Run `agentic-sdlc brain validate` to check prerequisites
2. Run `agentic-sdlc brain transition <NEW_STATE>` to update state
3. Artifacts required per state are validated automatically

### 0.0 **Team Communication (MANDATORY):**
   - **Announce:** `agentic-sdlc brain comm send --channel general --thread "SDLC-Flow" --role ORCHESTRATOR --content "Starting Full SDLC Automation using Swarms Protocol."`
   - **Sync:** `agentic-sdlc brain feedback send --sender ORCHESTRATOR --receiver TEAM --content "Orchestrator ready for Phase 1." --type status`

### 0.1 **Initialize State (If New Sprint):**
```bash
agentic-sdlc brain init <SPRINT_NUMBER>
```

## SDLC Flow (State Transitions)

### Phase 1: Planning (@PM)
- Research, create Project Plan, wait for User approval.
- **Checkpoint:** `python tools/intelligence/state/state_manager.py checkpoint $SESSION_ID planning`

### Phase 2: Requirements (@BA)
- Create User Stories with Gherkin acceptance criteria.

### Phase 3: Design (@SA + @UIUX + @PO)
- **Parallel Execution:**
  ```bash
  agentic-sdlc brain concurrent --phase design --task "Project Design"
  ```
- **Synthesis (MoA):** 
  ```bash
  agentic-sdlc brain synthesize --concurrent-result latest --strategy llm
  ```
- **Checkpoint:** `agentic-sdlc brain transition designing --reason "Design phase started"`

### 🛑 Phase 3.5: Design Approval Gate (HITL)
> **MANDATORY:** Human approval required before development.
```bash
agentic-sdlc brain gate request \
  --gate design_review \
  --session $SESSION_ID \
  --artifacts docs/architecture.md docs/ui-design.md
```
- Wait for approval: `agentic-sdlc brain gate status $REQUEST_ID`
- Proceed only after `#design-approved`

### Phase 4: Design Verification (@TESTER + @SECA)
- **Parallel Review:**
  ```bash
  agentic-sdlc brain concurrent --phase review --task "Design Verification"
  ```
- **Consensus Synthesis:**
  ```bash
  agentic-sdlc brain synthesize --concurrent-result latest --strategy consensus
  ```
- Review designs for quality and security.

### Phase 5: Development (@DEV + @DEVOPS)
- Feature branch, atomic commits, PRs, GitHub issues.
- **Checkpoint:** `python tools/intelligence/state/state_manager.py checkpoint $SESSION_ID development`

### 🛑 Phase 5.5: Code Review Gate (HITL)
> **MANDATORY:** Human approval required before testing.
```bash
agentic-sdlc brain gate request \
  --gate code_review \
  --session $SESSION_ID \
  --artifacts src/
```
- Wait for PR review and approval
- Proceed only after PR merged

### Phase 6: Testing (@TESTER)
- E2E testing, provide `#testing-passed`.
- **Self-Healing:** If tests fail, trigger feedback loop:
  ```bash
  agentic-sdlc brain heal --code src/ --requirements docs/requirements.md
  ```

### Phase 7: Bug Fixing (@DEV)
- Fix bugs, update KB.

### Phase 8: Deployment (@DEVOPS)
- **Merge to main and cleanup:**
  ```bash
  git checkout main
  git pull origin main
  git merge <feature-branch>
  git push origin main
  ```
- Deploy to staging/production.
- **Checkpoint:** `python tools/intelligence/state/state_manager.py checkpoint $SESSION_ID deployment`

### 🛑 Phase 8.5: Deployment Approval Gate (HITL)
> **MANDATORY for Production:** Human approval required.
```bash
agentic-sdlc brain gate request \
  --gate deployment_approval \
  --session $SESSION_ID
```

### Phase 9-10: Reporting & Closure (@PM)
- Update CHANGELOG, Final Review.
- **Track Costs:** `python tools/intelligence/cost/cost_tracker.py report --period daily`

### Phase 11: Self-Learning
- Run: `agentic-sdlc kb compound sync`
- Run: `agentic-sdlc learn --record-success`
- **Archive Session:** `python tools/intelligence/state/state_manager.py archive $SESSION_ID`

#orchestrator #automation #sdlc

## ⏭️ Next Steps
- **If Setup Complete:** Trigger @PM for Phase 1 (Planning)
- **If Planning Complete:** Trigger @SA + @UIUX for Phase 3 (Design)
- **If Design Complete:** Trigger @TESTER + @SECA for Phase 4 (Verification)
- **If Dev Complete:** Trigger @TESTER for Phase 6 (Testing)
- **If Deployment Complete:** Trigger @REPORTER for Phase 9 (Reporting)

---
## ⚠️ ENFORCEMENT REMINDER
Before executing this workflow, agent MUST:
1. Search knowledge base for similar tasks
2. Check current brain state
3. Run /onboarding if new to project
