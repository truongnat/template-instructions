---
description: Process - Safe Refactoring Workflow
---

# /refactor - Safe Refactoring Workflow

## ⚠️ PURPOSE
Systematic approach to refactoring code safely without breaking existing functionality.

// turbo-all

## When to Use

- Improving code structure
- Reducing technical debt
- Extracting reusable components
- Renaming/reorganizing files

## Golden Rule
> **Tests MUST pass before AND after refactoring.**

## Quick Commands

```bash
# Run tests before starting
bun test

# Check current coverage
bun test --coverage
```

## Workflow Steps

### 1. Define Scope
- [ ] What exactly will be refactored?
- [ ] What will NOT be touched?
- [ ] Expected outcome (cleaner code, better performance, etc.)

### 2. Verify Test Coverage
```bash
# Ensure code is covered by tests
bun test --coverage

# If coverage is low, add tests FIRST
```

**Critical:** If no tests exist for the code being refactored, write tests first!

### 3. Create Feature Branch
```bash
git checkout -b refactor/[description]
```

### 4. Run Tests (Baseline)
```bash
# All tests must pass before refactoring
bun test
```

### 5. Refactor in Small Steps
- [ ] Make ONE small change
- [ ] Run tests
- [ ] Commit if green
- [ ] Repeat

```bash
# Atomic commits
git commit -m "refactor: extract [function] from [module]"
```

### 6. Run Full Test Suite
```bash
# Verify no regressions
bun test

# Check types
bun run typecheck

# Lint check
bun run lint
```

### 7. Code Review
```bash
# Create PR for review
gh pr create --title "refactor: [description]"
```

Invoke `/review` workflow for PR.

### 8. Self-Learning
```bash
# Document refactoring pattern
agentic-sdlc kb compound sync
```

## Refactoring Patterns

| Pattern | Description | Risk |
|---------|-------------|------|
| **Extract Function** | Move code to reusable function | Low |
| **Rename** | Improve naming | Low |
| **Move File** | Reorganize structure | Medium |
| **Extract Module** | Split large file | Medium |
| **Change Signature** | Update function parameters | High |
| **Replace Algorithm** | New implementation | High |

## Anti-Patterns (Don't Do)

- ❌ Refactor AND add features at same time
- ❌ Refactor without tests
- ❌ Large refactoring without incremental commits
- ❌ Skip code review for "safe" refactoring

## Integration

- **@DEV** - Primary refactorer
- **@TESTER** - Verify test coverage
- **/review** - Code review after refactoring
- **/cycle** - Standard task lifecycle

#refactor #code-quality #technical-debt #cleanup

## ⏭️ Next Steps
- **If Tests Pass:** Trigger `/review` for code review
- **If Tests Fail:** Fix regressions (do not merge)
- **If Verified:** Trigger `/release` (if applicable)

---

## ENFORCEMENT REMINDER
Tests MUST pass before AND after refactoring.
