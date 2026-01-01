---
inclusion: always
---

# Enhanced Workflow Commands

Inspired by compound engineering principles, these workflows create a self-improving system.

## Core Workflows

### `/cycle` - Complete Task Lifecycle
**When:** Small, complete tasks (< 4 hours)
**Flow:** Plan → Work → Review → Compound
**Output:** Code + Knowledge Entry

```
@DEV /cycle - Add user profile avatar upload
```

### `/explore` - Deep Investigation
**When:** Before planning complex features
**Flow:** Multi-order analysis → Research → Recommendations
**Output:** Investigation Report

```
@SA /explore - Real-time notification system architecture
```

### `/specs` - Large Multi-Session Work
**When:** Features requiring multiple sprints
**Flow:** Requirements → Design → Phased Tasks
**Output:** Specification Document + Task Breakdown

```
@PM /specs - Complete authentication system with OAuth
```

### `/compound` - Capture Knowledge
**When:** After solving non-obvious problems
**Flow:** Document → Categorize → Index → Verify
**Output:** Searchable Knowledge Entry

```
@DEV /compound - Document the React hydration fix for SSR
```

### `/route` - Intelligent Workflow Selection
**When:** Unsure which workflow to use
**Flow:** Analyze intent → Recommend workflow → Execute
**Output:** Workflow recommendation + execution

```
@ORCHESTRATOR /route - Need to add payment processing
```

### `/emergency` - Critical Incident Response
**When:** Production outages, critical bugs
**Flow:** Assess → Hotfix → Deploy → Postmortem
**Output:** Hotfix + Incident Report + KB Entry

```
@DEV /emergency - Payment gateway returning 500 errors
```

### `/audit-security` - Proactive Security Review
**When:** Before/after security-sensitive work
**Flow:** Threat model → Code audit → Recommendations
**Output:** Security Audit Report

```
@SECA /audit-security - Review authentication flow
```

### `/refactor` - Safe Structural Improvement
**When:** Code needs restructuring
**Flow:** Analyze → Plan → Incremental changes → Verify
**Output:** Refactored code + migration guide

```
@DEV /refactor - Extract shared components from pages
```

### `/release` - Unified Release Pipeline
**When:** Ready to publish/deploy
**Flow:** Version → Changelog → Docs → Deploy
**Output:** Release package + documentation

```
@DEVOPS /release - Prepare v2.0.0 release
```

### `/housekeeping` - Cleanup and Maintenance
**When:** Before git push, end of sprint
**Flow:** Archive → Fix drift → Update index
**Output:** Clean workspace

```
@ORCHESTRATOR /housekeeping
```

### `/onboard` - Session Context Establishment
**When:** Start of new session
**Flow:** Load context → Resume state → Prime agent
**Output:** Session context summary

```
@ORCHESTRATOR /onboard
```

### `/help` - Unified Help System
**When:** Need guidance on workflows
**Flow:** Show available commands → Usage examples
**Output:** Help documentation

```
@ORCHESTRATOR /help
```

## Workflow Composition

Workflows can be chained:

```
@ORCHESTRATOR /explore → /specs → /cycle → /compound
```

## Workflow Metrics

Track workflow effectiveness:
- **Cycle Time:** Average time per workflow
- **Success Rate:** % of workflows completed successfully
- **Compound Rate:** % of workflows that generated KB entries
- **Reuse Rate:** % of workflows that referenced KB

## Workflow Templates

Each workflow has a template in `.agent/workflows/`:
- Input requirements
- Expected outputs
- Success criteria
- Handoff instructions

## Integration with Roles

Workflows are role-aware:
- `/cycle` → @DEV, @TESTER
- `/explore` → @SA, @UIUX
- `/specs` → @PM, @PO
- `/compound` → All roles
- `/emergency` → @DEV, @DEVOPS
- `/audit-security` → @SECA
- `/release` → @DEVOPS, @REPORTER

## Workflow Automation

Orchestrator can auto-select workflows:
```
@ORCHESTRATOR --mode=full-auto
Build a payment system with Stripe integration
```

Orchestrator will:
1. Analyze requirements
2. Select appropriate workflows
3. Execute in optimal order
4. Compound learnings

#workflows #automation #compound-engineering
