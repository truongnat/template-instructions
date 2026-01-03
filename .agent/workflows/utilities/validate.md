---
description: System Validation - Verify Tool References and Paths
---

# /validate - System Validation Workflow

**When to Use:** After documentation updates, before sprint start, weekly health check
**Flow:** Scan → Verify → Report → Repair
**Output:** Validation Report

## Overview
The `/validate` workflow ensures that all tool references, file paths, and scripts mentioned in workflows actually exist and are executable. It prevents "workflow rot" where documentation points to dead links.

## Workflow Steps

### 1. Scan Workflows
**Action:** Parse all files in `.agent/workflows/*.md`
**Target:** Identify all:
- `python tools/...` commands
- File path references
- Script calls

```bash
# Example scan command
grep -r "python tools/" .agent/workflows/
```

### 2. Verify References
**Action:** Check existence and executability
- [ ] Does the file exist?
- [ ] Is it executable?
- [ ] Does it run with `--help` (if script)?
- [ ] Are relative paths correct?

### 3. Report Issues
**Output:** `Validation-Report-YYYY-MM-DD.md`

**Template:**
```markdown
# Validation Report

## Broken References
| Workflow | Line | Reference | Issue |
|----------|------|-----------|-------|
| sa.md | 45 | python tools/bad/path.py | File not found |

## Path Issues
- Hardcoded path detected in `pm.md`
- Absolute path detected in `auto.md`

## Health Score: [Score]/100
```

### 4. Auto-Repair (Optional)
**Action:** Attempt to fix common issues
- Update known moved paths
- Fix standard relative path issues

## Usage Examples

### Manual Validation
```
@ORCHESTRATOR /validate
```

### Specific Check
```
@ORCHESTRATOR /validate --workflow sa.md
```

## Integration with Roles

### @ORCHESTRATOR
- Owns system health
- Runs validation weekly

### @DEVOPS
- Validates infrastructure scripts
- Fixes broken tool paths

#workflow #validation #maintenance #health-check
