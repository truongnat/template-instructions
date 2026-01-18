---
description: Artifact and Naming Conventions
---
# Artifact & Naming Conventions
## ⚠️ DOCUMENTATION LOCATION RULE (PROJECT-SPECIFIC)
Documentation MUST be located within each project's directory, NOT in the root docs/ folder (except for global guides).
### Correct Structure
`
root/
├── docs/ (Global System Docs ONLY)
│   ├── ARCHITECTURE.md
│   └── BRAIN-GUIDE.md
│
└── projects/
    └── [project-name]/
        └── docs/ (Project Specific Docs)
            └── sprints/
                └── sprint-[N]/
                    ├── plans/
                    ├── requirements/
                    ├── designs/
                    └── logs/
`
## Artifact Naming Convention
Use versioned names attached to the current Sprint:
| Artifact | Owner |
|----------|-------|
| Project-Plan-Sprint-[N]-v*.md | PM |
| Product-Backlog-Sprint-[N]-v*.md | PO |
| UIUX-Design-Spec-Sprint-[N]-v*.md | UIUX |
| System-Design-Spec-Sprint-[N]-v*.md | SA |
| Design-Verification-Report-Sprint-[N]-v*.md | QA |
| Security-Review-Report-Sprint-[N]-v*.md | SecA |
| Development-Log-Sprint-[N]-v*.md | DEV |
| DevOps-Plan-and-Log-Sprint-[N]-v*.md | DevOps |
| Test-Report-Sprint-[N]-v*.md | TESTER |
| Phase-Report-Sprint-[N]-v*.md | REPORTER |
| Master-Documentation.md | REPORTER |
| Final-Project-Report.md | REPORTER |
| Final-Approval-Report.md | STAKEHOLDER |
## ⚠️ CRITICAL LOCATION RULE (SPRINT FOLDERS)
ALL project artifacts MUST be created in the **PROJECT'S** workspace with organized structure based on **Sprint**:
**Base Directory:** projects/[project-name]/docs/sprints/sprint-[N]/
| Category | Folder Path | Content Example | Owner |
|----------|-------------|-----------------|-------|
| Plans | .../plans/ | Project-Plan-Sprint-[N]-v*.md, Product-Backlog-Sprint-[N]-v*.md | PM, PO |
| Designs | .../designs/ | System-Design-Spec-Sprint-[N]-v*.md, UIUX-Design-Spec-Sprint-[N]-v*.md | SA, UIUX |
| Reviews | .../reviews/ | Design-Verification-Report-Sprint-[N]-v*.md, Security-Review-Report-Sprint-[N]-v*.md | QA, SecA |
| Logs | .../logs/ | Development-Log-Sprint-[N]-v*.md, DevOps-Plan-and-Log-Sprint-[N]-v*.md | DEV, DevOps |
| Tests | .../tests/ | Test-Report-Sprint-[N]-v*.md | TESTER |
| Reports | .../reports/ | Phase-Report-Sprint-[N]-v*.md | REPORTER |
| Global | .../global/reports/ | Final-Project-Report.md, Final-Approval-Report.md | REPORTER, STAKEHOLDER |
| Global | projects/[project-name]/docs/global/ | Master-Documentation.md | REPORTER |
**FORBIDDEN LOCATIONS:**
- .agent/ directory (reserved for instructions only)
- Global docs/ folder for project-specific artifacts.
## ⚠️ CHANGELOG RULE (UPDATED 2026-01-04)
**Repository vs Project:**
1. **Root CHANGELOG.md:** ALLOWED for **Repository versioning only**.
   - MUST be managed AUTOMATICALLY by `release.py`.
   - Manual edits are FORBIDDEN except for fixing formatting.
2. **Project Reports:**
   - Detailed project changes must still be documented in sprint reports.
   - Use Phase-Report-Sprint-[N]-v*.md for detailed tracking.
## Mandatory Documentation Tags
Every action must be tagged with appropriate hashtags:
| Category | Tags |
|----------|------|
| **Planning** | #planning, #product-owner, #backlog |
| **Design** | #designing, #uiux-design |
| **Verification** | #verify-design, #security-review |
| **Development** | #development, #devops |
| **Testing** | #testing |
| **Bug Fixes** | #fixbug-critical, #fixbug-high, #fixbug-medium, #fixbug-low |
| **Status** | #blocked, #hotfix, #rollback |
| **Deployment** | #deployed-staging, #deployed-production |
| **Research** | #searching |
| **Reporting** | #reporting, #stakeholder-review |

