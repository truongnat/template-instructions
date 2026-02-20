---
name: debugging
description: >
  Systematic root-cause analysis and resolution for bugs, errors, and unexpected behavior.
  Follows a structured diagnostic process instead of random trial-and-error. Use when the user
  encounters an error, a failing test, unexpected behavior, or a stack trace.
compatibility: Works with any language and framework
metadata:
  author: agentic-sdlc
  version: "2.0"
  category: quality
---

# Debugging Skill

You are a **Senior Debugger** who approaches problems methodically. Never guess randomly — follow the diagnostic process to identify the root cause before attempting a fix.

## Debugging Process

### Step 1: Reproduce and Isolate

Before attempting any fix:
1. **Reproduce the error** with the exact steps or command that triggered it
2. **Read the full error output** — not just the last line, but the entire stack trace
3. **Identify the error type**:

| Error Type | Approach |
|-----------|----------|
| **Compile/Build Error** | Read the error message carefully. Usually a typo, missing import, or type mismatch. |
| **Runtime Error** | Find the exact line in the stack trace. Check the state of variables at that point. |
| **Logic Error** | No crash, but wrong output. Add logging/breakpoints to trace the data flow. |
| **Intermittent/Flaky** | Usually a race condition, timing issue, or external dependency. |
| **Environment Error** | Missing dependency, wrong version, permission issue. Check `package.json`/`requirements.txt`. |

### Step 2: Read the Stack Trace

Stack traces are read **bottom-up** (the root cause is usually at the bottom, the crash site at the top):

```
Traceback (most recent call last):
  File "app.py", line 45, in handle_request     ← 3. Where it crashed
    result = service.process(data)
  File "service.py", line 22, in process         ← 2. Called from here
    return self.repo.find(data.id)
  File "repo.py", line 10, in find               ← 1. ROOT CAUSE: Start here
    return self.db.query(Model).filter_by(id=id).one()
sqlalchemy.exc.NoResultFound: No row was found   ← The actual error
```

**Action**: Start reading from the bottom. The `NoResultFound` tells you the query returned no results. Check why `data.id` might be invalid.

### Step 3: Form a Hypothesis

Based on the stack trace and error type, form exactly ONE hypothesis:

```markdown
**Hypothesis**: The `data.id` passed to `repo.find()` is None because 
the request body parser didn't extract the `id` field correctly.

**Evidence needed**: Log the value of `data.id` before the query.
**Quick test**: Add `assert data.id is not None` before `repo.find()`.
```

### Step 4: Verify the Hypothesis

Use the **minimal investigation** to confirm or reject:

1. **Add targeted logging** at the suspected point (not everywhere)
2. **Check the input** that triggered the error
3. **Compare with a working case** — what's different?

```python
# Targeted debugging — add BEFORE the failing line
import logging
logger = logging.getLogger(__name__)

def find(self, id):
    logger.debug(f"Finding record with id={id!r} (type={type(id).__name__})")
    # ... original code
```

### Step 5: Apply the Fix

Rules for fixes:
- Fix the **root cause**, not the symptom
- Every fix must include a **guard** against the same error recurring (validation, type check, etc.)
- If the fix changes behavior, update or add tests

```python
# ❌ BAD: Silencing the error (fixing the symptom)
try:
    return self.repo.find(data.id)
except NoResultFound:
    return None  # This hides the real problem!

# ✅ GOOD: Validating input (fixing the root cause)
def process(self, data):
    if not data.id:
        raise ValidationError("Missing required field: id")
    return self.repo.find(data.id)
```

### Step 6: Verify the Fix

1. Reproduce the original error — it should no longer occur
2. Run the full test suite — the fix must not break anything else
3. Test edge cases around the fix (empty input, null, boundary values)

## Common Debug Patterns

### Pattern: "It works locally but fails in CI/production"
1. Check environment variables and secrets
2. Check Node/Python/Dart version differences
3. Check for OS-specific path separators (`/` vs `\`)
4. Check for timezone differences

### Pattern: "It worked yesterday but broke today"
1. Check `git log` for recent changes
2. Check if dependencies were updated (lockfile changes)
3. Check if external APIs changed their contract

### Pattern: "It fails intermittently"
1. Race condition: Multiple async operations accessing shared state
2. Timeout: External service sometimes slow
3. Memory: Gradual leak causing OOM after many requests
4. Order-dependent tests sharing state

## Anti-Patterns

1. ❌ "Shotgun debugging" — changing random things hoping it fixes
2. ❌ Adding `try/except: pass` to silence errors
3. ❌ Fixing without understanding — if you can't explain WHY it works, you haven't fixed it
4. ❌ Debugging in production without reproducing locally first
5. ❌ Removing tests that "fail for no reason" — they're telling you something
