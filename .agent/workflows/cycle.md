---
description: Complete Task Lifecycle - Plan → Work → Review → Compound
---

# /cycle - Complete Task Lifecycle

**When to Use:** Small, complete tasks (< 4 hours)
**Flow:** Plan → Work → Review → Compound
**Output:** Code + Knowledge Entry

## Overview
The `/cycle` workflow is designed for small, self-contained tasks that can be completed in a single session. It enforces the compound learning loop by automatically capturing knowledge after completion.

## Workflow Steps

### 1. Research Phase (MANDATORY)
```bash
# Search knowledge base first
python tools/research/research_agent.py --feature "[task description]" --type feature
```

**Checklist:**
- [ ] Search KB for similar implementations
- [ ] Review related patterns in Neo4j
- [ ] Check GitHub issues for context
- [ ] Identify reusable code patterns

### 2. Plan Phase
- Break down task into atomic steps
- Estimate time (must be < 4 hours)
- Identify dependencies
- Define success criteria

**Output:** Task plan in Development-Log

### 3. Work Phase
- Implement following atomic commit pattern
- Reference KB entries in code comments
- Test locally after each commit
- Document non-obvious decisions

**Pattern:**
```javascript
/**
 * Task: [Task-ID] - [Description]
 * KB Reference: KB-YYYY-MM-DD-### (if applicable)
 * Commit: [commit-hash]
 */
```

### 4. Review Phase
- Self-review code quality
- Run automated tests
- Verify against success criteria
- Check for security issues

**Checklist:**
- [ ] Code follows project standards
- [ ] Tests pass locally
- [ ] No console errors/warnings
- [ ] Documentation updated

### 5. Compound Phase (AUTO-TRIGGERED)
**Triggers:**
- Task took > 2 hours (document why)
- Solution was non-obvious
- New pattern discovered
- Bug fixed (any priority)

**Action:** Create KB entry using template

## Usage Examples

### Example 1: Feature Implementation
```
@DEV /cycle - Add user profile avatar upload with image compression
```

**Expected Flow:**
1. Search KB for image upload patterns
2. Plan: Upload → Compress → Store → Display
3. Implement with atomic commits
4. Test with various image formats
5. Document compression algorithm choice

### Example 2: Bug Fix
```
@DEV /cycle - Fix #123: Countdown timer not displaying on mobile
```

**Expected Flow:**
1. Search KB for mobile rendering issues
2. Plan: Reproduce → Debug → Fix → Verify
3. Fix with single atomic commit
4. Test on multiple devices
5. Document root cause in KB

### Example 3: Refactoring
```
@DEV /cycle - Extract shared validation logic into utils
```

**Expected Flow:**
1. Search KB for refactoring patterns
2. Plan: Identify duplicates → Extract → Test
3. Refactor with incremental commits
4. Verify all tests pass
5. Document new utility pattern

## Integration with Roles

### @DEV
- Primary user of /cycle
- Implements code changes
- Creates KB entries

### @TESTER
- Uses /cycle for test creation
- Documents test patterns
- Reports bugs for /cycle fixes

### @DEVOPS
- Uses /cycle for infrastructure tasks
- Documents deployment patterns
- Automates repetitive tasks

## Success Criteria

**Task Complete When:**
- [ ] Code committed with proper message
- [ ] Tests passing
- [ ] Documentation updated
- [ ] KB entry created (if triggered)
- [ ] Task marked "Done" in Development-Log
- [ ] Commit hash linked in log

## Metrics

Track cycle effectiveness:
- **Cycle Time:** Average time per task
- **First-Time Success:** % completed without rework
- **KB Contribution:** % that generated KB entries
- **Pattern Reuse:** % that referenced existing KB

## Anti-Patterns to Avoid

❌ **Don't:**
- Skip KB search before starting
- Commit all changes at once
- Skip testing phase
- Forget to document learnings

✅ **Do:**
- Search KB first
- Atomic commits per logical change
- Test continuously
- Compound knowledge automatically

## Handoff Template

```markdown
### /cycle Complete: [Task-ID]
- **Duration:** [X hours]
- **Commits:** [commit-hash-1], [commit-hash-2]
- **KB Entry:** KB-YYYY-MM-DD-### (if created)
- **Tests:** ✅ All passing
- **Next Step:** @TESTER - Verify [specific aspect]

#cycle #development #compound
```

#workflow #cycle #compound-engineering
