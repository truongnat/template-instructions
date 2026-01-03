# Implementation Plan: Workflow Optimization
**Project:** Agentic SDLC Workflow Consolidation  
**Date:** 2026-01-03  
**Owner:** @PM + @ORCHESTRATOR  
**Timeline:** 4 weeks  
**Priority:** P1 (Important, not urgent)

---

## Executive Summary

**Goal:** Reduce workflows from 33 to 20 files (39% reduction) while improving quality and SDLC compliance.

**Why:** Current structure has too many overlapping workflows, causing confusion and maintenance burden.

**How:** Merge overlapping roles, consolidate duplicate processes, reorganize into clear hierarchy.

**Success Metric:** ≤ 20 workflows, 95% system health, 4-tier hierarchy, zero duplicate functionality.

---

## Phase 1: Preparation & Analysis (Week 1)

### Day 1-2: Documentation Review
```bash
# Create analysis workspace
mkdir -p docs/analysis/workflow-optimization/

# Inventory current state
ls -lh .agent/workflows/*.md > docs/analysis/workflow-optimization/current-inventory.txt

# Run validation
python tools/workflows/validate.py --full-report > docs/analysis/workflow-optimization/validation-before.txt
```

**Deliverables:**
- [x] Current inventory documented
- [x] Validation baseline established
- [x] Analysis reports created (done above)

### Day 3-4: Stakeholder Alignment
**Actions:**
- [ ] Present analysis to project team
- [ ] Get approval for consolidation plan
- [ ] Identify any custom workflows to preserve
- [ ] Set success criteria

**Stakeholders:**
- Project Owner
- Development Team
- Documentation Team

### Day 5: Backup & Safety
```bash
# Full backup
cp -r .agent/workflows .agent/workflows.backup-$(date +%Y%m%d)
tar -czf backups/workflows-pre-optimization-2026-01-03.tar.gz .agent/workflows/

# Git commit current state
git add .agent/workflows/
git commit -m "chore: backup workflows before optimization"
git tag workflow-optimization-baseline-2026-01-03
```

**Deliverables:**
- [ ] Backup created (local + git tag)
- [ ] Recovery plan documented
- [ ] Rollback procedure tested

---

## Phase 2: Consolidation (Week 2)

### Monday: Role Merging (Part 1)

#### Task 2.1: Merge PO → PM
```bash
# Working file
code .agent/workflows/pm.md
```

**Steps:**
1. Open both pm.md and po.md
2. Add new section in pm.md:
   ```markdown
   ## Product Owner Duties
   
   ### Backlog Management
   [Copy from po.md]
   
   ### User Story Prioritization
   [Copy from po.md]
   
   ### Business Value Assessment
   [Copy from po.md]
   ```
3. Integrate PO templates into PM templates
4. Update MCP integration section
5. Add PO skills to Neo4j integration
6. Update tags: add `#product-owner`

**Acceptance Criteria:**
- [ ] All PO functionality in pm.md
- [ ] No duplicate content
- [ ] Templates merged cleanly
- [ ] References updated
- [ ] Tags updated

#### Task 2.2: Merge Reporter → PM
```bash
code .agent/workflows/pm.md
```

**Steps:**
1. Add reporting section in pm.md:
   ```markdown
   ## Reporting Duties
   
   ### Progress Reports
   ### CHANGELOG Updates
   ### Documentation Generation
   ```
2. Integrate reporter templates
3. Add reporting workflow to handoff section

**Acceptance Criteria:**
- [ ] Reporting duties integrated
- [ ] Templates merged
- [ ] No functionality lost

#### Task 2.3: Merge Stakeholder → PM
```bash
code .agent/workflows/pm.md
```

**Steps:**
1. Update approval gates section:
   ```markdown
   ## Approval Gates (Stakeholder Role)
   
   ### Project Plan Approval
   ### Design Review Approval
   ### Final Delivery Approval
   ```
2. Add stakeholder communication patterns
3. Update handoff templates

**Acceptance Criteria:**
- [ ] Approval process documented
- [ ] Communication templates added
- [ ] PM workflow now end-to-end

---

### Tuesday: Role Merging (Part 2)

#### Task 2.4: Merge QA → Tester
```bash
code .agent/workflows/tester.md
```

**Steps:**
1. Add design verification section:
   ```markdown
   ## Design Verification (QA Phase)
   
   ### Review Design Specs
   ### Testability Assessment
   ### Test Strategy Creation
   ```
2. Reorganize workflow:
   - Phase 1: QA (before development)
   - Phase 2: Testing (after development)
3. Merge templates
4. Update MCP integrations

**Acceptance Criteria:**
- [ ] QA + Testing unified
- [ ] Clear phase separation
- [ ] All templates merged

---

### Wednesday: Process Consolidation

#### Task 2.5: Merge auto.md → orchestrator.md
```bash
code .agent/workflows/orchestrator.md
```

**Steps:**
1. Integrate auto.md content into orchestrator.md
2. Add automation modes section
3. Merge workflow coordination logic
4. Update templates

**Acceptance Criteria:**
- [ ] Single orchestrator workflow
- [ ] All automation features present
- [ ] No duplicate logic

#### Task 2.6: Merge auto-learning → brain.md
```bash
code .agent/workflows/brain.md
```

**Steps:**
1. Integrate automated learning triggers
2. Add LEANN + Neo4j + Learning Engine sections
3. Document parallel execution
4. Add statistics and insights

**Acceptance Criteria:**
- [ ] Comprehensive brain workflow
- [ ] All learning features present
- [ ] Clear automation triggers

---

### Thursday: Support Consolidation

#### Task 2.7: Merge cleanup → housekeeping.md
```bash
code .agent/workflows/housekeeping.md
```

**Steps:**
1. Integrate cleanup workflow steps
2. Add quick reference to header
3. Merge archival procedures
4. Update index maintenance

**Acceptance Criteria:**
- [ ] Single maintenance workflow
- [ ] All cleanup features present
- [ ] Quick reference integrated

#### Task 2.8: Merge docs-updates → release.md
```bash
code .agent/workflows/release.md
```

**Steps:**
1. Add documentation update section
2. Integrate changelog generation
3. Add versioning procedures
4. Merge templates

**Acceptance Criteria:**
- [ ] Documentation updates in release flow
- [ ] Changelog automation complete
- [ ] Version bumping automated

---

### Friday: Quality Enhancement

#### Task 2.9: Expand sprint.md
```bash
code .agent/workflows/sprint.md
```

**Target:** 88 lines → 300+ lines

**Add Sections:**
- Sprint ceremonies (daily standup, review, retro)
- Burndown chart generation
- Velocity tracking
- Blocker management
- Sprint metrics

**Acceptance Criteria:**
- [ ] Comprehensive sprint workflow
- [ ] All agile ceremonies covered
- [ ] Metrics and analytics included

#### Task 2.10: Standardize All Roles
**Target:** All role workflows to BA quality level (250+ lines)

**For each:** dev.md, devops.md, sa.md, uiux.md, seca.md

**Add:**
- Comprehensive duties section
- Detailed templates
- MCP integration
- Neo4j skills
- Research mandate
- Handoff templates

**Acceptance Criteria:**
- [ ] All roles standardized
- [ ] 250+ lines minimum
- [ ] All sections present

---

## Phase 3: Reorganization (Week 3)

### Monday: Directory Structure

#### Task 3.1: Create New Directories
```bash
cd .agent/workflows/

# Create hierarchy
mkdir -p core process support utilities

# Verify
tree .agent/workflows/
```

**Acceptance Criteria:**
- [ ] 4 directories created
- [ ] Structure matches design

---

### Tuesday-Wednesday: File Migration

#### Task 3.2: Move Core Roles
```bash
# Move role workflows
mv pm.md ba.md sa.md uiux.md dev.md devops.md tester.md seca.md core/

# Verify
ls -l core/
```

**Expected:** 8 files in core/

#### Task 3.3: Move Processes
```bash
# Move process workflows
mv orchestrator.md cycle.md explore.md emergency.md sprint.md process/

# Verify
ls -l process/
```

**Expected:** 5 files in process/

#### Task 3.4: Move Support
```bash
# Move support workflows
mv compound.md brain.md route.md release.md housekeeping.md support/

# Verify
ls -l support/
```

**Expected:** 5 files in support/

#### Task 3.5: Move Utilities
```bash
# Move utilities
mv validate.md metrics.md utilities/

# Verify
ls -l utilities/
```

**Expected:** 2 files in utilities/

**Total Check:** 8 + 5 + 5 + 2 = 20 files ✅

---

### Thursday: Archive Old Files

#### Task 3.6: Archive Deleted Workflows
```bash
# Create archive
mkdir -p .agent/archive/workflows-consolidated-2026-01-03/

# Move deleted files
mv po.md qa.md reporter.md stakeholder.md \
   auto.md auto-learning-workflow.md \
   cleanup.md cleanup-quick-reference.md \
   documentation-updates.md research.md kb-search.md \
   .agent/archive/workflows-consolidated-2026-01-03/

# Document archive
echo "# Archived Workflows (2026-01-03)

These workflows were consolidated or deleted during optimization.

## Merged into Other Workflows:
- po.md → pm.md
- qa.md → tester.md
- reporter.md → pm.md
- stakeholder.md → pm.md
- auto.md → orchestrator.md
- auto-learning-workflow.md → brain.md
- cleanup.md → housekeeping.md
- documentation-updates.md → release.md

## Deleted (functionality moved elsewhere):
- research.md → embedded in role workflows
- kb-search.md → trivial wrapper, examples in compound.md
- cleanup-quick-reference.md → merged into housekeeping.md

See: docs/analysis/Workflows-Deep-Analysis-2026-01-03.md
" > .agent/archive/workflows-consolidated-2026-01-03/README.md
```

#### Task 3.7: Move Setup Guides
```bash
# Create setup directory
mkdir -p docs/setup/

# Move setup guides
mv git-kb-integration.md kb-hooks-setup.md docs/setup/

# Add README
echo "# Setup Guides

One-time setup instructions for Agentic SDLC components.

## Available Guides:
- git-kb-integration.md - Integrate Git with Knowledge Base
- kb-hooks-setup.md - Setup Git hooks for KB automation
" > docs/setup/README.md
```

---

### Friday: Create Index Files

#### Task 3.8: Core Index
```bash
cat > .agent/workflows/core/INDEX.md << 'EOF'
# Core SDLC Role Workflows

**Purpose:** One workflow per SDLC phase/role  
**Count:** 8 workflows

## Planning & Requirements
1. **pm.md** - Project Manager (Planning, Backlog, Reporting, Stakeholder)
2. **ba.md** - Business Analyst (Requirements, Specifications, User Stories)

## Design
3. **sa.md** - System Analyst (Architecture, API Design)
4. **uiux.md** - UI/UX Designer (Interface Design, Prototyping)

## Verification
5. **tester.md** - Tester (QA + Testing, Design Verification)
6. **seca.md** - Security Analyst (Security Review, Threat Modeling)

## Implementation & Deployment
7. **dev.md** - Developer (Implementation, Code Review)
8. **devops.md** - DevOps Engineer (Infrastructure, CI/CD, Deployment)

---

**Usage:** `@ROLE` in prompts/commands
**Standard:** All workflows 250+ lines, comprehensive templates
EOF
```

#### Task 3.9: Process Index
```bash
cat > .agent/workflows/process/INDEX.md << 'EOF'
# Core Process Workflows

**Purpose:** Key SDLC processes and automation  
**Count:** 5 workflows

## Orchestration & Automation
1. **orchestrator.md** - Workflow Automation (full-auto, semi-auto modes)

## Development Processes
2. **cycle.md** - Task Lifecycle (Plan → Work → Review → Compound)
3. **explore.md** - Deep Investigation (Multi-order analysis before planning)

## Incident & Sprint Management
4. **emergency.md** - Incident Response (P0/P1/P2 handling)
5. **sprint.md** - Sprint Management (Start → Daily → Review → Retro)

---

**Usage:** `/workflow-name` in prompts
**Standard:** All workflows 200+ lines, clear step-by-step instructions
EOF
```

#### Task 3.10: Support Index
```bash
cat > .agent/workflows/support/INDEX.md << 'EOF'
# Support Workflows

**Purpose:** Learning, routing, release, maintenance  
**Count:** 5 workflows

## Knowledge & Learning
1. **compound.md** - Knowledge Capture (Manual learning system)
2. **brain.md** - AI Learning System (LEANN + Neo4j automation)

## Process Support
3. **route.md** - Workflow Selection Intelligence (Analyze → Recommend → Execute)
4. **release.md** - Release Management (Changelog + Versioning + Docs)
5. **housekeeping.md** - Maintenance (Archive + Cleanup + Index Updates)

---

**Usage:** `/workflow-name` in prompts
**Standard:** All workflows 150+ lines, helpful for productivity
EOF
```

#### Task 3.11: Utilities Index
```bash
cat > .agent/workflows/utilities/INDEX.md << 'EOF'
# Utility Workflows

**Purpose:** System health and analytics  
**Count:** 2 workflows

1. **validate.md** - System Health Check (Path verification, tool validation)
2. **metrics.md** - Analytics & Reporting (Performance tracking, statistics)

---

**Usage:** `/workflow-name` for maintenance tasks
**Standard:** 100+ lines, automated where possible
EOF
```

---

## Phase 4: Validation & Documentation (Week 4)

### Monday: Update References

#### Task 4.1: Update global.md
```bash
code .agent/rules/global.md
```

**Changes:**
- Update available roles list (remove PO, QA, Reporter, Stakeholder, Orchestrator)
- Update workflow paths to new structure
- Add workflow hierarchy diagram
- Update examples

**Acceptance Criteria:**
- [ ] Role list accurate (8 roles)
- [ ] Paths updated
- [ ] Examples working

#### Task 4.2: Update .cursorrules
```bash
code .cursorrules
```

**Changes:**
- Reference new workflow paths
- Update role mentions
- Add hierarchy note

#### Task 4.3: Update .windsurfrules
```bash
code .windsurfrules
```

**Changes:**
- Same as .cursorrules

#### Task 4.4: Update GEMINI.md
```bash
code GEMINI.md
```

**Changes:**
- Update workflow count (33 → 20)
- Update directory structure
- Add new hierarchy diagram
- Update quick reference

---

### Tuesday: Create Decision Tools

#### Task 4.5: Workflow Decision Tree
```bash
cat > .agent/workflows/DECISION-TREE.md << 'EOF'
# Which Workflow Should I Use?

## Quick Decision Tree

1. **Is this a production emergency?**
   - YES → `/emergency`
   - NO → Continue to 2

2. **Are you unsure which workflow to use?**
   - YES → `/route` (it will analyze and recommend)
   - NO → Continue to 3

3. **What are you trying to do?**

   **Start a new project:**
   - Complex/unknown → `/explore` first, then `@PM`
   - Clear requirements → `@PM` directly

   **Execute a small task (< 4 hours):**
   - `/cycle`

   **Document a solution:**
   - `/compound`

   **Investigate a complex feature:**
   - `/explore`

   **Handle a production incident:**
   - `/emergency`

   **Manage sprints:**
   - Start: `/sprint start [N]`
   - Review: `/sprint review`
   - Retro: `/sprint retro`
   - Close: `/sprint close [N]`

   **Release a version:**
   - `/release`

   **Clean up project:**
   - `/housekeeping`

   **Check system health:**
   - `/validate`

   **View analytics:**
   - `/metrics`

   **Run full SDLC:**
   - `@PM` → `@BA` → `@SA` + `@UIUX` → `@TESTER` + `@SECA` → `@DEV` + `@DEVOPS` → `@TESTER` → `@DEVOPS` → `@PM`

## Role-Specific

**I need to:**
- Plan a project → `@PM`
- Gather requirements → `@BA`
- Design architecture → `@SA`
- Design UI/UX → `@UIUX`
- Implement code → `@DEV`
- Setup infrastructure → `@DEVOPS`
- Test/verify → `@TESTER`
- Security review → `@SECA`

---

Still confused? Use `/route` - it's smart! 🧠
EOF
```

#### Task 4.6: Workflow Catalog
```bash
cat > .agent/workflows/README.md << 'EOF'
# Workflows Directory

**Total:** 20 workflows organized in 4 tiers

## 📁 Structure

```
workflows/
├── core/        (8) - SDLC Role Workflows
├── process/     (5) - Core Processes
├── support/     (5) - Learning & Tools
└── utilities/   (2) - Health & Analytics
```

## 📚 Quick Links

- [Decision Tree](DECISION-TREE.md) - Which workflow to use?
- [Core Roles](core/INDEX.md)
- [Processes](process/INDEX.md)
- [Support](support/INDEX.md)
- [Utilities](utilities/INDEX.md)

## 🎯 Most Common Workflows

1. **`@PM`** - Start new projects, manage sprints
2. **`@DEV`** - Implement features
3. **`/cycle`** - Execute small tasks (< 4h)
4. **`/compound`** - Capture learnings
5. **`/emergency`** - Handle incidents

## 📖 Documentation

- [Workflow Analysis](../../docs/analysis/Workflows-Deep-Analysis-2026-01-03.md)
- [Optimization Plan](../../docs/analysis/Workflow-Optimization-Diagram.md)
- [Implementation Plan](../../docs/sprints/sprint-X/plans/Workflow-Optimization-Plan.md)

---

**Last Updated:** 2026-01-03  
**Version:** 2.0 (Optimized)
EOF
```

---

### Wednesday: Run Validation

#### Task 4.7: Automated Validation
```bash
# Run full validation
python tools/workflows/validate.py --full-report > docs/analysis/workflow-optimization/validation-after.txt

# Compare before/after
diff docs/analysis/workflow-optimization/validation-before.txt \
     docs/analysis/workflow-optimization/validation-after.txt
```

**Expected Results:**
- [ ] All workflow paths valid
- [ ] No broken references
- [ ] All tools referenced exist
- [ ] Health score ≥ 95%

#### Task 4.8: Manual Testing
```bash
# Test each workflow command
@PM /help
@BA /help
/cycle --help
/compound --help
/emergency --help
/route --help
```

**Test Checklist:**
- [ ] All role mentions work
- [ ] All /slash commands work
- [ ] Templates accessible
- [ ] MCPs referenced correctly
- [ ] Neo4j integration works

---

### Thursday: Documentation

#### Task 4.9: Migration Guide
```bash
cat > docs/guides/WORKFLOW-MIGRATION-GUIDE.md << 'EOF'
# Workflow Migration Guide (v1 → v2)

## What Changed?

**Old Structure (33 workflows):**
- Mixed roles, processes, utilities in single directory
- Many overlapping workflows
- No clear hierarchy

**New Structure (20 workflows):**
- 4-tier hierarchy (core/process/support/utilities)
- Consolidated overlapping workflows
- Standardized quality

## Workflow Mapping

### Deleted (Merged into Others)

| Old Workflow | New Location | Notes |
|--------------|--------------|-------|
| po.md | pm.md | Product Owner duties in PM workflow |
| qa.md | tester.md | QA merged into Testing workflow |
| reporter.md | pm.md | Reporting is PM duty |
| stakeholder.md | pm.md | Stakeholder approval in PM workflow |
| orchestrator.md | process/orchestrator.md | Merged with auto.md |
| auto.md | process/orchestrator.md | Now the primary orchestrator |
| auto-learning-workflow.md | support/brain.md | Automated learning in Brain |
| cleanup.md | support/housekeeping.md | Cleanup in Housekeeping |
| documentation-updates.md | support/release.md | Docs in Release workflow |
| research.md | (embedded) | Research step in all role workflows |
| kb-search.md | (deleted) | Examples in compound.md |
| cleanup-quick-reference.md | support/housekeeping.md | Reference in header |

### Moved (New Paths)

| Old Path | New Path | Category |
|----------|----------|----------|
| pm.md | core/pm.md | Role |
| ba.md | core/ba.md | Role |
| sa.md | core/sa.md | Role |
| uiux.md | core/uiux.md | Role |
| dev.md | core/dev.md | Role |
| devops.md | core/devops.md | Role |
| tester.md | core/tester.md | Role |
| seca.md | core/seca.md | Role |
| cycle.md | process/cycle.md | Process |
| explore.md | process/explore.md | Process |
| emergency.md | process/emergency.md | Process |
| sprint.md | process/sprint.md | Process |
| compound.md | support/compound.md | Support |
| brain.md | support/brain.md | Support |
| route.md | support/route.md | Support |
| release.md | support/release.md | Support |
| housekeeping.md | support/housekeeping.md | Support |
| validate.md | utilities/validate.md | Utility |
| metrics.md | utilities/metrics.md | Utility |

## Usage Changes

### Before:
```
@PM /help
@PO /help
@QA /help
@REPORTER /help
```

### After:
```
@PM /help     # Now includes PO, Reporter, Stakeholder duties
@TESTER /help # Now includes QA duties
```

### Before:
```
/auto
/orchestrator
```

### After:
```
/orchestrator  # Unified automation
```

## Backward Compatibility

We've added redirects for old workflow names. If you use:
- `@PO` → redirects to `@PM`
- `@QA` → redirects to `@TESTER`
- `/auto` → redirects to `/orchestrator`

However, please update your usage to new names.

## Benefits

- **39% fewer files** (33 → 20)
- **Clearer organization** (4-tier hierarchy)
- **Higher quality** (all workflows standardized)
- **Easier discovery** (index files, decision tree)
- **Better SDLC compliance** (strict phase mapping)

## Getting Help

- Unsure which workflow? → Use `/route`
- See decision tree: `.agent/workflows/DECISION-TREE.md`
- See catalog: `.agent/workflows/README.md`

EOF
```

---

### Friday: Final Review & Release

#### Task 4.10: Code Review
**Reviewers:** @PM, @BA, @SA, @SECA

**Review Checklist:**
- [ ] All merged workflows complete
- [ ] No functionality lost
- [ ] Quality standardized
- [ ] References updated
- [ ] Documentation complete

#### Task 4.11: Git Commit
```bash
# Stage changes
git add .agent/workflows/
git add .agent/archive/
git add docs/setup/
git add docs/analysis/
git add docs/guides/

# Commit
git commit -m "refactor(workflows): optimize structure from 33 to 20 workflows

BREAKING CHANGE: Workflow structure reorganized

- Merged overlapping roles (PO→PM, QA→Tester, etc.)
- Reorganized into 4-tier hierarchy (core/process/support/utilities)
- Consolidated duplicate processes
- Standardized quality across all workflows
- Added comprehensive documentation and decision tools

Migration guide: docs/guides/WORKFLOW-MIGRATION-GUIDE.md
Analysis: docs/analysis/Workflows-Deep-Analysis-2026-01-03.md

Closes #[issue-number]
"

# Tag release
git tag -a v2.0.0-workflows -m "Workflow Optimization Release

- 33 → 20 workflows (39% reduction)
- 4-tier hierarchy
- Standardized quality
- Complete documentation
"

# Push
git push origin main
git push origin v2.0.0-workflows
```

#### Task 4.12: Announcement
```markdown
# 🎉 Workflow Optimization Complete!

We've streamlined our workflows from 33 to 20 files (39% reduction!)

## What's New?

✅ **Clearer Organization**
- 📁 core/ - 8 SDLC roles
- 📁 process/ - 5 core processes
- 📁 support/ - 5 support tools
- 📁 utilities/ - 2 system utils

✅ **Easier to Use**
- Decision tree to find right workflow
- Comprehensive index files
- Slash command help

✅ **Higher Quality**
- All workflows standardized
- Comprehensive templates
- Better examples

## Migration

See: [Migration Guide](docs/guides/WORKFLOW-MIGRATION-GUIDE.md)

## Help

- Use `/route` if unsure which workflow
- See decision tree: `.agent/workflows/DECISION-TREE.md`
- Read analysis: `docs/analysis/Workflows-Deep-Analysis-2026-01-03.md`

---

Questions? Tag @PM or @ORCHESTRATOR
```

---

## Success Metrics

### Quantitative
- [x] Reduce workflows: 33 → 20 ✅
- [ ] System health: ≥ 95%
- [ ] Validation passing: 100%
- [ ] Average quality: ≥ 250 lines per workflow
- [ ] Documentation coverage: ≥ 95%

### Qualitative
- [ ] User satisfaction survey: ≥ 4/5
- [ ] Reduced confusion reports
- [ ] Easier onboarding
- [ ] Better SDLC compliance
- [ ] Professional appearance

---

## Risk Mitigation

### Risk 1: Breaking Existing Usage
**Mitigation:**
- Add redirects for old workflow names
- Provide comprehensive migration guide
- Gradual rollout with announcement
- Backward compatibility period (4 weeks)

### Risk 2: Lost Functionality
**Mitigation:**
- Careful content merge (no deletion without review)
- QA review of all merged workflows
- Test all features before/after
- Keep backups for 90 days

### Risk 3: User Resistance
**Mitigation:**
- Clear communication of benefits
- Provide decision tools (/route, decision tree)
- Offer migration support
- Document all changes

### Risk 4: Validation Failures
**Mitigation:**
- Run validate.py before each commit
- Test all slash commands
- Check all role mentions
- Verify all tool references

---

## Rollback Plan

If major issues occur:

```bash
# Emergency rollback
cd .agent/
rm -rf workflows/
cp -r workflows.backup-20260103 workflows/

# Or restore from git
git checkout workflow-optimization-baseline-2026-01-03 -- .agent/workflows/

# Notify team
echo "Workflow optimization rolled back due to [reason]"
echo "Re-evaluating approach"
```

---

## Communication Plan

### Week 1 (Preparation)
- [ ] Analysis shared with team
- [ ] Feedback collected
- [ ] Plan approved

### Week 2 (Consolidation)
- [ ] Daily updates on progress
- [ ] Preview of merged workflows
- [ ] Early access for testing

### Week 3 (Reorganization)
- [ ] New structure demo
- [ ] Migration guide draft
- [ ] User testing

### Week 4 (Launch)
- [ ] Final announcement
- [ ] Migration guide published
- [ ] Support available for questions
- [ ] Monitor usage and feedback

---

## Post-Launch (Week 5+)

### Week 5: Monitoring
- [ ] Collect usage analytics
- [ ] Monitor validation scores
- [ ] Gather user feedback
- [ ] Fix any issues

### Week 6-8: Optimization
- [ ] Refine workflows based on feedback
- [ ] Improve documentation
- [ ] Enhance decision tools
- [ ] Update examples

### Week 12: Review
- [ ] Measure success metrics
- [ ] User satisfaction survey
- [ ] Document lessons learned
- [ ] Plan next optimization

---

## Appendix

### File Checklist

**Week 2 (Merge):**
- [ ] pm.md (merged: po, reporter, stakeholder)
- [ ] tester.md (merged: qa)
- [ ] orchestrator.md (merged: auto)
- [ ] brain.md (merged: auto-learning-workflow)
- [ ] housekeeping.md (merged: cleanup, cleanup-quick-ref)
- [ ] release.md (merged: documentation-updates)
- [ ] sprint.md (expanded)

**Week 3 (Reorganize):**
- [ ] core/ created with 8 files
- [ ] process/ created with 5 files
- [ ] support/ created with 5 files
- [ ] utilities/ created with 2 files
- [ ] Archive created
- [ ] Setup guides moved

**Week 4 (Document):**
- [ ] global.md updated
- [ ] .cursorrules updated
- [ ] .windsurfrules updated
- [ ] GEMINI.md updated
- [ ] DECISION-TREE.md created
- [ ] README.md created
- [ ] INDEX.md × 4 created
- [ ] Migration guide created

### Command Reference

```bash
# Validate workflows
python tools/workflows/validate.py --full-report

# Count workflows
find .agent/workflows -name "*.md" -type f | wc -l

# Measure quality
wc -l .agent/workflows/*/*.md

# Test workflow
@PM /help

# Search workflow
grep -r "specific term" .agent/workflows/
```

---

**Owner:** @PM + @ORCHESTRATOR  
**Status:** Draft → In Progress → Complete  
**Last Updated:** 2026-01-03

#implementation-plan #workflow-optimization #project-management
