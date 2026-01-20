---
description: Process - Code Review Workflow for PRs
---

# /review - Code Review Workflow

## ⚠️ PURPOSE
Systematic code review process for Pull Requests. Ensures code quality, security, and consistency.

// turbo-all

## Quick Commands

```bash
# Review a specific PR
agentic-sdlc review --pr 123

# Review current branch changes
git diff main...HEAD --stat
```

## Workflow Steps

### 1. Context Gathering
```bash
# Search KB for similar implementations
agentic-sdlc kb search "[feature/module]"

# View PR diff
git diff main...HEAD
```

### 2. Code Quality Checklist
- [ ] **Readability:** Clear naming, comments where needed
- [ ] **Structure:** Follows project patterns
- [ ] **DRY:** No unnecessary duplication
- [ ] **SOLID:** Single responsibility, clean interfaces

### 3. Security Review (@SECA)
- [ ] No hardcoded secrets
- [ ] Input validation present
- [ ] No SQL injection vulnerabilities
- [ ] Proper error handling (no sensitive data in errors)

### 4. Test Coverage (@TESTER)
- [ ] Unit tests added for new code
- [ ] Edge cases covered
- [ ] Integration tests if needed
- [ ] All tests passing

### 5. Documentation
- [ ] Code comments for complex logic
- [ ] API docs updated if applicable
- [ ] README updated if needed

### 6. Provide Feedback
```bash
# Comment on PR (via GitHub CLI)
gh pr comment 123 --body "LGTM with suggestions: ..."

# Request changes
gh pr review 123 --request-changes --body "Please fix: ..."

# Approve
gh pr review 123 --approve
```

### 7. Self-Learning
```bash
# Record review patterns for future reference
agentic-sdlc kb compound sync
```

## Review Severity Levels

| Level | Action | Examples |
|-------|--------|----------|
| 🔴 Blocker | Must fix before merge | Security issue, breaks build |
| 🟠 Major | Should fix | Performance issue, wrong pattern |
| 🟡 Minor | Nice to fix | Naming, style inconsistency |
| 🟢 Nitpick | Optional | Personal preference |

## Integration

- **@TESTER** - Test coverage review
- **@SECA** - Security review
- **@DEV** - Code implementation review
- **/cycle** - Part of standard task lifecycle

#review #pr #code-quality #security

## ⏭️ Next Steps
- **If Approved:** Trigger `/release` (if ready) or Merger
- **If Changes Requested:** Return to `@DEV` for fixes

---

## ENFORCEMENT REMINDER
Search KB for similar patterns before commenting.
