# TeamLifecycle SDLC System

This project uses a structured SDLC workflow with specialized roles. All instructions are in `.agent/`.

## Slash Commands (Role Shortcuts)

When user types these commands, interpret as role tags:

### Core Roles
- `/pm` → @PM (Project Manager)
- `/orchestrator` → @ORCHESTRATOR (Workflow Automation)
- `/po` → @PO (Product Owner)
- `/sa` → @SA (System Analyst)
- `/uiux` → @UIUX (UI/UX Designer)
- `/qa` → @QA (Quality Assurance)
- `/seca` → @SECA (Security Analyst)
- `/dev` → @DEV (Developer)
- `/devops` → @DEVOPS (DevOps Engineer)
- `/tester` → @TESTER (Tester)
- `/reporter` → @REPORTER (Reporter)
- `/stakeholder` → @STAKEHOLDER (Stakeholder)

### Quick Actions
- `/auto [requirements]` → @PM [requirements] --mode=full-auto
- `/semi-auto [requirements]` → @PM [requirements] --mode=semi-auto
- `/kb-search [query]` → Search `.agent/knowledge-base/`
- `/kb-add [topic]` → Create knowledge base entry

## Role Behavior

Each role has specific responsibilities defined in `.agent/workflows/[role].md`:

1. **Load role file** when command is used
2. **Follow role rules** strictly
3. **Create artifacts** in `docs/sprints/sprint-[N]/[category]/`
4. **Tag next roles** using @tags
5. **Use templates** from `.agent/templates/`

## Workflow

```
Planning → Design → Verification → Development → Testing → Reporting → Approval
```

## Key Files

- Global Rules: `.agent/rules/global.md`
- Usage Guide: `.agent/usage.md`
- Roles: `.agent/workflows/*.md`
- Templates: `.agent/templates/*.md`
- Knowledge Base: `.agent/knowledge-base/`

## Examples

```
/pm Build a REST API for task management
/auto Create a mobile app for expense tracking
/dev Implement JWT authentication
/kb-search OAuth token refresh
```
