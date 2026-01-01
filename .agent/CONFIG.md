# Agent Configuration Guide

## Directory Structure

```
.agent/
├── CONFIG.md                    # This file
├── USAGE.md                     # User-facing usage guide
├── workflows/                   # Workflow definitions
│   ├── pm.md                    # Project Manager
│   ├── dev.md                   # Developer
│   ├── sa.md                    # System Analyst
│   ├── uiux.md                  # UI/UX Designer
│   ├── qa.md                    # Quality Assurance
│   ├── seca.md                  # Security Analyst
│   ├── devops.md                # DevOps Engineer
│   ├── tester.md                # Tester
│   ├── reporter.md              # Reporter
│   ├── stakeholder.md           # Stakeholder
│   ├── po.md                    # Product Owner
│   ├── auto.md                  # Orchestrator
│   ├── cycle.md                 # ⭐ Complete task lifecycle
│   ├── explore.md               # ⭐ Deep investigation
│   ├── compound.md              # ⭐ Knowledge capture
│   ├── emergency.md             # ⭐ Incident response
│   ├── housekeeping.md          # ⭐ Maintenance
│   ├── kb-search.md             # Knowledge base search
│   ├── research.md              # Research agent
│   └── brain.md                 # Project brain
├── templates/                   # Document templates
├── knowledge-base/              # Compound learning system
│   ├── INDEX.md                 # Searchable index
│   ├── README.md                # KB guide
│   ├── bugs/                    # Bug patterns
│   ├── features/                # Feature implementations
│   ├── architecture/            # Architecture decisions
│   ├── security/                # Security fixes
│   ├── performance/             # Optimizations
│   └── platform-specific/       # Platform issues
├── rules/                       # Global rules
│   ├── GLOBAL.md                # Core rules
│   ├── GIT-WORKFLOW.md          # Git conventions
│   ├── KNOWLEDGE-BASE.md        # KB management
│   ├── AUTO-LEARNING.md         # Auto-learning system
│   └── ARTIFACTS.md             # Artifact placement
└── ide-integration/             # IDE configurations
    ├── CURSOR-RULES.md
    ├── WINDSURF-CASCADE.md
    ├── GITHUB-COPILOT-INSTRUCTIONS.md
    └── cline-config.json
```

## Workflow System

### Standard Role Workflows
Traditional SDLC roles with defined responsibilities:
- `@PM` - Project planning and scope management
- `@SA` - System architecture and design
- `@UIUX` - Interface design
- `@DEV` - Implementation
- `@DEVOPS` - Infrastructure and deployment
- `@TESTER` - Testing and quality assurance
- `@QA` - Design verification
- `@SECA` - Security assessment
- `@REPORTER` - Documentation and reporting
- `@STAKEHOLDER` - Final approval
- `@PO` - Product backlog management

### Enhanced Compound Workflows ⭐
Inspired by Antigravity Compound Engineering:

#### `/cycle` - Complete Task Lifecycle
- **Purpose:** Small tasks (< 4 hours) with automatic knowledge capture
- **Flow:** Research → Plan → Work → Review → Compound
- **Output:** Code + KB entry
- **Usage:** `@DEV /cycle - Add user avatar upload`

#### `/explore` - Deep Investigation
- **Purpose:** Complex features requiring multi-order analysis
- **Flow:** 1st/2nd/3rd order analysis → Research → Recommendations
- **Output:** Investigation report
- **Usage:** `@SA /explore - Real-time notification architecture`

#### `/compound` - Capture Knowledge
- **Purpose:** Document solved problems as searchable knowledge
- **Flow:** Document → Categorize → Index → Verify
- **Output:** YAML-based KB entry
- **Usage:** `@DEV /compound - Document React hydration fix`

#### `/emergency` - Critical Incident Response
- **Purpose:** Production outages and critical bugs
- **Flow:** Assess → Hotfix → Deploy → Postmortem → Compound
- **Output:** Hotfix + incident report + KB entry
- **Usage:** `@DEV /emergency - P0: Payment gateway down`

#### `/housekeeping` - Cleanup and Maintenance
- **Purpose:** Regular system maintenance
- **Flow:** Archive → Fix drift → Update index → Verify
- **Output:** Clean workspace, updated indexes
- **Usage:** `@ORCHESTRATOR /housekeeping`

#### `/route` - Intelligent Workflow Selection
- **Purpose:** Auto-select appropriate workflow
- **Flow:** Analyze → Recommend → Execute
- **Output:** Workflow recommendation
- **Usage:** `@ORCHESTRATOR /route - Add payment processing`

## Knowledge Base System

### Structure
```
.agent/knowledge-base/
├── INDEX.md                     # Master index with YAML search
├── bugs/                        # Bug fixes by priority
│   ├── critical/
│   ├── high/
│   ├── medium/
│   └── low/
├── features/                    # Feature implementations
│   ├── authentication/
│   ├── performance/
│   └── integration/
├── architecture/                # Architecture decisions
├── security/                    # Security fixes
├── performance/                 # Optimizations
└── platform-specific/           # Platform issues
```

### Entry Format
All KB entries use YAML frontmatter for searchability:

```yaml
---
title: "Brief descriptive title"
category: bug|feature|architecture|security|performance|platform
priority: critical|high|medium|low
sprint: sprint-N
date: YYYY-MM-DD
tags: [tag1, tag2, tag3]
related_files: [path/to/file1, path/to/file2]
attempts: 3
time_saved: "2 hours"
---

## Problem
[Description]

## Root Cause
[Analysis]

## Solution
[Step-by-step]

## Prevention
[How to avoid]

## Related Patterns
[Links]
```

### Search-First Workflow
**Before ANY complex work:**
1. Search `.agent/knowledge-base/INDEX.md`
2. Check related categories
3. Review similar patterns
4. Apply learned solutions
5. Document new insights

## Compound Learning Loop

```
Problem → Solution → Document → Search → Reuse → Compound
```

### When to Compound
**ALWAYS document when:**
- Bug required 3+ attempts to fix
- Solution was non-obvious
- Issue likely to recur
- Pattern applies to multiple features
- Security vulnerability discovered
- Performance optimization achieved

### Auto-Compounding Triggers
System automatically creates entries when:
- Bug marked `#fixbug-critical` or `#fixbug-high`
- Security review finds vulnerabilities
- Performance improvement > 20%
- Architecture decision documented
- Platform-specific issue resolved

## Critical Patterns (Antibodies)

### Anti-Patterns to Avoid
1. **Big Bang Integration** - Commit immediately per task
2. **Approval Bypass** - Never skip design/security reviews
3. **Scope Creep** - Only implement approved features
4. **Knowledge Amnesia** - Search KB before implementing
5. **Silent Failures** - Test after each implementation
6. **Documentation Debt** - Update docs in same commit
7. **Security Afterthought** - SECA review before development
8. **Deployment Surprise** - Full staging verification required

### Positive Patterns to Follow
1. **Compound Learning** - Every solution becomes knowledge
2. **Parallel Execution** - Independent roles work simultaneously
3. **Evidence-Based Progress** - All claims backed by artifacts
4. **Atomic Tasks** - Small, verifiable units of work
5. **Fail-Fast Validation** - Early detection of issues
6. **Automated Handoffs** - Roles auto-notify next steps
7. **Health Monitoring** - Continuous system health checks
8. **Modular Skills** - Pluggable capabilities

## Integration with Kiro IDE

### Steering Files Location
`.kiro/steering/` contains Kiro-specific configurations:
- `00-teamlifecycle-overview.md` - Workflow overview
- `global-rules.md` - Core rules
- `critical-patterns.md` - Antibody patterns
- `compound-learning.md` - Learning system
- `workflow-enhancements.md` - Enhanced workflows
- `workflow-routing.md` - Workflow selection guide
- `role-*.md` - Individual role configurations

### Dual Configuration
- **`.agent/`** - Detailed workflow implementations
- **`.kiro/steering/`** - Kiro IDE integration layer

Both directories work together:
- Kiro steering files reference `.agent/workflows/`
- Workflows reference Kiro steering for context
- Knowledge base shared between both

## Metrics and Health Monitoring

### Compound System Health
Track weekly:
```
📊 Compound System Health
- Total Entries: [N]
- Entries This Week: [N]
- Time Saved: [N hours]
- Reuse Rate: [N%]
- Coverage: [N%]
```

### Workflow Metrics
- **Cycle Time:** Average duration per workflow
- **Success Rate:** % completed successfully
- **Compound Rate:** % that generated KB entries
- **Reuse Rate:** % that referenced existing KB

### Pattern Effectiveness
- **Atomic Commit Rate:** % of tasks with immediate commits
- **KB Search Rate:** % of complex tasks that searched KB first
- **Approval Compliance:** % of phases with proper approvals
- **Documentation Coverage:** % of code with updated docs
- **Security Review Rate:** % of features with SECA review

## Automation Scripts

### KB Index Generator
```bash
tools/housekeeping/update-kb-index.sh
```

### Documentation Drift Checker
```bash
tools/housekeeping/check-drift.sh
```

### YAML Validator
```bash
tools/housekeeping/validate-yaml.sh
```

### Research Agent
```bash
python tools/research/research_agent.py --feature "[description]" --type feature
```

## Best Practices

### For Developers
1. **Search KB first** before implementing complex features
2. **Atomic commits** per task with proper messages
3. **Document immediately** after solving non-obvious problems
4. **Reference KB entries** in code comments
5. **Use `/cycle`** for small tasks to enforce compound loop

### For Architects
1. **Use `/explore`** for complex features
2. **Document decisions** in KB architecture category
3. **Reference patterns** from previous projects
4. **Update KB** when patterns evolve

### For Security
1. **Document all fixes** in KB security category
2. **Create prevention patterns** for vulnerabilities
3. **Maintain security checklist** in KB
4. **Use `/emergency`** for active breaches

### For DevOps
1. **Use `/emergency`** for production outages
2. **Use `/housekeeping`** for regular maintenance
3. **Document infrastructure patterns** in KB
4. **Automate repetitive tasks** and document in KB

## Quick Reference

### Workflow Selection
```
Small task (< 4h)           → /cycle
Complex investigation       → /explore
Large project              → /specs (via @PM)
Production emergency       → /emergency
Maintenance               → /housekeeping
Document solution         → /compound
Unsure                    → /route
```

### KB Categories
```
bugs/                     → Bug fixes and root causes
features/                 → Feature implementations
architecture/             → Architecture decisions
security/                 → Security fixes
performance/              → Optimizations
platform-specific/        → Platform issues
```

### Priority Levels
```
critical → Breaks core functionality, data loss, security exploit
high     → Major feature broken, serious UX issue
medium   → Works but with wrong behavior or poor UX
low      → Cosmetic, minor inconsistency
```

## Getting Started

### For New Projects
1. Initialize KB: `cp -r .agent/knowledge-base/ [project]/.agent/`
2. Configure Kiro: Copy `.kiro/steering/` files
3. Review workflows: Read `.agent/workflows/README.md`
4. Start with `/cycle`: Small tasks to learn the system

### For Existing Projects
1. Install workflows: Copy `.agent/workflows/` to project
2. Create KB structure: `mkdir -p .agent/knowledge-base/{bugs,features,architecture,security,performance}`
3. Migrate existing docs: Convert to YAML format
4. Start compounding: Use `/compound` to document existing knowledge

## Support and Documentation

- **Usage Guide:** `.agent/USAGE.md`
- **Workflow Details:** `.agent/workflows/[workflow].md`
- **KB Guide:** `.agent/knowledge-base/README.md`
- **Kiro Integration:** `.kiro/steering/README.md`

## Philosophy

> "Each unit of engineering work should make subsequent units of work easier—not harder."

The compound engineering system transforms AI agents from session-to-session amnesiacs into learning partners that compound their capabilities over time. Every bug fixed, pattern discovered, and solution documented becomes permanent knowledge that makes future work faster and better.

#configuration #compound-engineering #knowledge-base
