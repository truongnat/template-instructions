# Core Workflows Index

> **Role-based workflows for specialized SDLC phases.**

**Last Updated:** 2026-01-03

## Overview

Core workflows define the responsibilities and procedures for each specialized role in the Agentic SDLC system. Each workflow follows the **Strict Execution Protocol** requiring mandatory research, team communication, and self-learning phases.

## Workflows

| Command | Role | Description |
|---------|------|-------------|
| `/pm` | Project Manager | Planning, Task Allocation, and Reporting |
| `/ba` | Business Analyst | Requirements and User Stories |
| `/sa` | System Analyst | Architecture and API Design |
| `/uiux` | UI/UX Designer | Interface Design |
| `/dev` | Developer | Implementation with Git Flow |
| `/tester` | Tester | QA and Testing Execution |
| `/seca` | Security Analyst | Security Assessment |
| `/devops` | DevOps Engineer | Infrastructure and Deployment |

## Workflow Details

### `/pm` - Project Manager
- **File:** `pm.md`
- **Phase:** 1 (Planning), 9-10 (Closure)
- **Key Duties:** Project planning, task breakdown, GitHub issue creation, CHANGELOG updates
- **Templates:** `Project-Plan`, `Final-Review-Report`

### `/ba` - Business Analyst
- **File:** `ba.md`
- **Phase:** 2 (Requirements)
- **Key Duties:** Requirements gathering, user story creation with Gherkin acceptance criteria
- **Templates:** `BRD`, `User-Stories`

### `/sa` - System Analyst
- **File:** `sa.md`
- **Phase:** 3 (Design)
- **Key Duties:** Architecture design, API specifications
- **Templates:** `Backend-Design-Spec`

### `/uiux` - UI/UX Designer
- **File:** `uiux.md`
- **Phase:** 3 (Design)
- **Key Duties:** UI/UX design specifications, WCAG 2.1 AA compliance
- **Templates:** `UIUX-Design-Spec`

### `/dev` - Developer
- **File:** `dev.md`
- **Phase:** 5 (Development), 7 (Bug Fixing)
- **Key Duties:** Feature branch workflow, atomic commits, PRs, GitHub issue linking
- **Git Convention:** `feat/TASK-ID-name`, `fix/TASK-ID-name`

### `/tester` - Tester
- **File:** `tester.md`
- **Phase:** 4 (Design Verification), 6 (Testing)
- **Key Duties:** Design verification, E2E testing, `#testing-passed` approval
- **Templates:** `Design-Verification-Report`

### `/seca` - Security Analyst
- **File:** `seca.md`
- **Phase:** 4 (Design Verification)
- **Key Duties:** Threat modeling (STRIDE), security review, OWASP Top 10 compliance
- **Templates:** `Security-Review-Report`

### `/devops` - DevOps Engineer
- **File:** `devops.md`
- **Phase:** 5 (CI/CD), 8 (Deployment)
- **Key Duties:** CI/CD pipeline, merge authority, staging/production deployment

## Common Protocol

All core workflows share these mandatory steps:

1. **Team Communication First** - Check history and announce start
2. **Research First** - Query knowledge base and research agent
3. **Evidence Required** - Every action produces verifiable output
4. **Self-Learning** - Sync to Neo4j after completion

## Tags

`#core` `#roles` `#sdlc` `#skills-enabled`
