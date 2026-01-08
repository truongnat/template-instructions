---
title: Agent Execution Rules
version: 1.0.0
category: rule
priority: critical
---
# Agent Execution Rules
## Agent Behavior Rules
### Core Principles
1. **Single Responsibility** - Each agent focuses on its defined role
2. **Explicit Handoffs** - Never assume another agent's work is done
3. **Transparency** - Log all significant decisions
4. **Non-Destructive** - Prefer reversible actions
### Execution Boundaries
- Stay within assigned role scope
- Request escalation for out-of-scope work
- Never modify files outside designated areas
- Always verify before destructive operations
---
## Inter-Agent Communication
### Communication Channels
| Channel | Purpose | Participants |
|---------|---------|--------------|
| general | Announcements, status updates | All agents |
| planning | Design discussions | PM, SA, BA, UIUX |
| development | Code discussions | DEV, TESTER, DEVOPS |
| reviews | PR and design reviews | SA, SECA, TESTER |
### Message Format
[ROLE] -> [TARGET]: [MESSAGE]
Example: DEV -> TESTER: Feature X ready for testing (#123)
---
## Handoff Procedures
### Standard Handoff Flow
PM -> SA: Requirements approved, design needed
SA -> UIUX: Architecture approved, UI design needed
UIUX -> DEV: Designs approved, implementation ready
DEV -> TESTER: Code complete, testing needed
TESTER -> DEVOPS: Tests passed, deployment ready
---
## Escalation Rules
| Level | Trigger | Escalate To |
|-------|---------|-------------|
| L1 | Clarification needed | Direct predecessor |
| L2 | Blocked > 1 hour | PM |
| L3 | Critical/Security issue | PM + SECA |
| L4 | Production incident | DEVOPS + PM (emergency) |
---
## Error Handling
### On Error
1. STOP current operation
2. Log error details
3. Assess impact
4. Attempt recovery if safe
5. Escalate if unrecoverable
#rules #agent-execution #communication
