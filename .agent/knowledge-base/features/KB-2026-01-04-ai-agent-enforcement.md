---
category: feature-implementation
subcategory: brain-system
tags: [enforcement, workflows, compliance, ai-agent, gemini]
difficulty: medium
date: 2026-01-04
author: @DEV
sprint: sprint-6
---
# AI Agent Brain System Enforcement Implementation
## Problem/Challenge
AI agents (Gemini, Cursor, etc.) were not following brain system workflows, roles, and skills when executing tasks. They would directly implement solutions without:
- Reading workflow files
- Following SDLC phases
- Activating appropriate roles
- Recording learnings
## Solution
Implemented multi-layer enforcement system:
1. **GEMINI.md Enforcement Section** - Added mandatory pre-flight checklist at top of file
2. **ai-enforcement.md** - Created dedicated enforcement rules in .agent/rules/
3. **preflight.md Workflow** - New workflow for pre-task checks
4. **Workflow Reminders** - Added enforcement reminders to all 12 workflows
## Implementation Details
### Pre-Flight Checklist (5 Steps)
1. Read workflow file FIRST
2. Search knowledge base
3. Identify required roles
4. Check brain state
5. Announce task start
### Slash Command Mapping
Maps user /commands to workflow files automatically:
- /auto -> orchestrator.md
- /cycle -> cycle.md
- /brain -> brain.md
### Role Activation Matrix
Defines which roles activate for which task type.
## Learnings
- AI agents need explicit, prominent rules at top of context files
- Enforcement must be visible in EVERY workflow file
- Pre-flight workflow concept ensures compliance before execution
## Related Files
- GEMINI.md (mandatory enforcement section)
- .agent/rules/ai-enforcement.md
- .agent/workflows/preflight.md
- All workflow files (enforcement reminders added)
#brain-system #enforcement #ai-agent #compliance
