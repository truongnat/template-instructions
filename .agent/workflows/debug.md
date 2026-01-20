---
description: Process - Systematic Debugging Workflow
---

# /debug - Debugging Workflow

## ⚠️ PURPOSE
Systematic approach to debugging issues in development. Different from `/emergency` which is for production incidents.

// turbo-all

## When to Use

- Local development bugs
- Test failures
- Unexpected behavior
- Performance issues (dev environment)

## Quick Commands

```bash
# Search KB for similar bugs
agentic-sdlc kb search "error type" --category bugs

# Check learning engine for similar errors
agentic-sdlc learn --similar-errors "ErrorType"
```

## Workflow Steps

### 1. Reproduce the Issue
- [ ] Identify exact steps to reproduce
- [ ] Note environment (OS, versions, config)
- [ ] Capture error message/stack trace

```bash
# Run failing test in isolation
bun test --watch [test-file]
```

### 2. Search Knowledge Base
```bash
# Check if similar bug was fixed before
agentic-sdlc kb search "[error message]"

# Check neo4j for patterns
agentic-sdlc learn --similar-errors "[ErrorType]"
```

### 3. Isolate the Problem
- [ ] Binary search: Comment out code to find the culprit
- [ ] Check recent changes: `git log --oneline -10`
- [ ] Review git blame: `git blame [file]`

### 4. Identify Root Cause
- [ ] Add logging/breakpoints
- [ ] Check input data
- [ ] Verify assumptions
- [ ] Review dependencies

```bash
# Debug with verbose output
DEBUG=* bun run [script]
```

### 5. Implement Fix
- [ ] Write failing test first (TDD)
- [ ] Implement minimal fix
- [ ] Verify fix works

```bash
git commit -m "fix: [description of fix]"
```

### 6. Verify No Regression
```bash
# Run full test suite
bun test

# Run type check
bun run typecheck
```

### 7. Document & Learn (MANDATORY)

```bash
# Record error pattern for future reference
agentic-sdlc learn --record-error "ErrorType" "[description]" \
  --resolution "[how it was fixed]" \
  --approach "[debugging approach used]"

# Sync KB
agentic-sdlc kb compound sync
```

## Common Debug Strategies

| Strategy | When to Use | Command |
|----------|-------------|---------|
| **Binary Search** | Large codebase, unknown location | Comment out half |
| **Git Bisect** | Regression, worked before | `git bisect start` |
| **Logging** | Runtime issues | Add console.log/print |
| **Breakpoints** | Complex state | Use debugger |
| **Rubber Duck** | Stuck, need fresh perspective | Explain to "duck" |

## Integration

- **@DEV** - Primary debugger
- **@TESTER** - Verify fix with tests
- **/emergency** - Escalate if production issue
- **/compound** - Document solution (embedded)

#debug #troubleshooting #bugs #development

## ⏭️ Next Steps
- **If Fixed:** Trigger `/cycle` to resume normal work
- **If Root Cause Unknown:** Trigger `/explore` for deeper analysis
- **If Hotfix Needed:** Trigger `/emergency` or `/release`

---

## ENFORCEMENT REMINDER
Always record error patterns after fixing bugs.
