# Implementation Plan: Strengthen Brain Protocol Enforcement

**Date:** 2026-01-05  
**Issue:** Brain tools exist but not being called during agent sessions

---

## 🔴 User Identified Gaps

| # | Gap | Current State | Required State |
|---|-----|---------------|----------------|
| 1 | **Observer** | Not halting on errors | MUST halt, fix, resume |
| 2 | **A/B Testing** | Not used | Use for small tasks |
| 3 | **Planning** | Jump to implementation | MUST plan first |
| 4 | **Self-Improve** | Not running | Run after each session |
| 5 | **Reports** | No artifacts | MUST create walkthrough |
| 6 | **Housekeeping** | Not triggered | Run after task completion |

---

## Proposed Changes

### [MODIFY] [GEMINI.md](file:///d:/dev/sdlc-kit/GEMINI.md)

Add **CRITICAL ENFORCEMENT GATES** section with mandatory checkpoints:

```markdown
## 🚨 CRITICAL ENFORCEMENT GATES

### Gate 1: Pre-Task (BEFORE ANYTHING)
```bash
python tools/brain/observer.py --status
python tools/brain/model_optimizer.py --recommend "[task]"
```
Decision: If task is small, consider A/B testing.

### Gate 2: Planning (BEFORE CODE)
- Create implementation_plan.md
- Get user approval before execution

### Gate 3: Error Handling
If ANY script fails:
1. STOP immediately
2. Call: `python tools/brain/observer.py --halt "[error]"`
3. Fix the issue
4. Call: `python tools/brain/observer.py --resume`

### Gate 4: Post-Task (AFTER COMPLETION)
```bash
python tools/brain/learner.py --learn "[task]"
python tools/brain/judge.py --score "[artifact]"
python tools/brain/self_improver.py --analyze
python bin/kb_cli.py compound sync
```

### Gate 5: Reporting
- Create walkthrough.md
- Save to docs/walkthroughs/

### Gate 6: Cleanup
```bash
python tools/workflows/housekeeping.py
```
```

---

## Verification Plan

After implementation:
1. Test a small task with A/B testing
2. Intentionally cause an error to test halt
3. Verify planning step is enforced
4. Check report generation

---

## ❓ Awaiting Approval

Proceed with strengthening GEMINI.md enforcement?
