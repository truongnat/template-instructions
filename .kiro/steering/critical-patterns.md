---
inclusion: always
---

# Critical Patterns - Antibodies Against Recurring Mistakes

These patterns are "antibodies" - learned defenses against common mistakes that compound over time.

## 🚫 Anti-Patterns to Avoid

### 1. Big Bang Integration
**Problem:** Committing all changes at end of sprint
**Pattern:** Atomic commits per task
**Rule:** Commit immediately after each task completion

### 2. Approval Bypass
**Problem:** Skipping design/security reviews
**Pattern:** Mandatory approval gates
**Rule:** No development without approved design

### 3. Scope Creep
**Problem:** Adding unapproved features
**Pattern:** Strict backlog adherence
**Rule:** All features must be in approved plan

### 4. Knowledge Amnesia
**Problem:** Solving same problem multiple times
**Pattern:** Search-first workflow
**Rule:** Check KB before implementing

### 5. Silent Failures
**Problem:** Bugs discovered late in cycle
**Pattern:** Continuous testing
**Rule:** Test after each implementation

### 6. Documentation Debt
**Problem:** Missing or outdated docs
**Pattern:** Document-as-you-go
**Rule:** Update docs in same commit as code

### 7. Security Afterthought
**Problem:** Security review after implementation
**Pattern:** Security-first design
**Rule:** SECA review before development

### 8. Deployment Surprise
**Problem:** Production issues not caught in staging
**Pattern:** Staging mirrors production
**Rule:** Full staging verification required

## ✅ Positive Patterns to Follow

### 1. Compound Learning
**Pattern:** Every solution becomes searchable knowledge
**Implementation:** YAML frontmatter + structured entries
**Benefit:** Exponential productivity gains

### 2. Parallel Execution
**Pattern:** Independent roles work simultaneously
**Implementation:** SA+UIUX+PO, QA+SECA, DEV+DEVOPS
**Benefit:** 50% faster delivery

### 3. Evidence-Based Progress
**Pattern:** All claims backed by artifacts
**Implementation:** Screenshots, logs, test results
**Benefit:** Trust and transparency

### 4. Atomic Tasks
**Pattern:** Small, verifiable units of work
**Implementation:** Task-level commits with traceability
**Benefit:** Clean history, easy rollback

### 5. Fail-Fast Validation
**Pattern:** Early detection of issues
**Implementation:** Design verification before coding
**Benefit:** Reduced rework

### 6. Automated Handoffs
**Pattern:** Roles auto-notify next steps
**Implementation:** @role tags in artifacts
**Benefit:** No manual coordination needed

### 7. Health Monitoring
**Pattern:** Continuous system health checks
**Implementation:** Metrics dashboard, KB coverage
**Benefit:** Proactive issue detection

### 8. Modular Skills
**Pattern:** Pluggable capabilities
**Implementation:** Skills directory with SKILL.md
**Benefit:** Easy customization

## 🎯 Pattern Application by Role

### @PM
- ✅ Create versioned plans (v1, v2, v3)
- ✅ Wait for explicit approval
- ❌ Never skip approval gates
- ❌ Never add unapproved features

### @SA + @UIUX
- ✅ Work in parallel on designs
- ✅ Reference KB for patterns
- ❌ Never start before plan approval
- ❌ Never skip QA/SECA review

### @DEV
- ✅ Atomic commits per task
- ✅ Search KB before complex work
- ❌ Never commit without testing
- ❌ Never skip documentation

### @TESTER
- ✅ Test immediately after dev
- ✅ Document bug patterns
- ❌ Never approve with critical bugs
- ❌ Never skip regression tests

### @DEVOPS
- ✅ Staging mirrors production
- ✅ Automate everything
- ❌ Never deploy without staging verification
- ❌ Never skip rollback plan

## 📊 Pattern Effectiveness Metrics

Track pattern adoption:
- **Atomic Commit Rate:** % of tasks with immediate commits
- **KB Search Rate:** % of complex tasks that searched KB first
- **Approval Compliance:** % of phases with proper approvals
- **Documentation Coverage:** % of code with updated docs
- **Security Review Rate:** % of features with SECA review

## 🔄 Pattern Evolution

Patterns evolve based on:
1. **Recurring Issues** - New antibodies created
2. **Success Stories** - Positive patterns reinforced
3. **Metrics** - Data-driven pattern refinement
4. **Team Feedback** - User-reported pain points

## Integration with Workflows

All workflows MUST enforce critical patterns:
- `/plan` - Enforces approval gates
- `/work` - Enforces atomic commits
- `/review` - Enforces quality checks
- `/compound` - Enforces knowledge capture
- `/emergency` - Enforces rollback plans

#critical-patterns #best-practices #anti-patterns
