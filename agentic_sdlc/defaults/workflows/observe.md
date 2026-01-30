---
description: Intelligence - Observer - Rule Compliance Check
---

# /observe - Rule Compliance Monitor

## ⚠️ PURPOSE
Trigger the Observer agent to check rule compliance for actions, code, or the entire system.

// turbo-all

## Quick Commands

```bash
# Check overall compliance status
python asdlc.py observe

# Check a specific action
python asdlc.py observe --action "create file foo.py"

# Start continuous observation
python asdlc.py observe --start
```

## When to Use

- Before committing code
- After making changes to workflows or rules
- During code review
- When debugging compliance issues

## Workflow Steps

### 1. Check Current Compliance
```bash
python asdlc.py observe
```
Review the compliance score and any violations.

### 2. Check Specific Action
```bash
python asdlc.py observe --action "[action description]"
```
Validates a specific action against the rules.


### 3. Review Violations
If violations are found:
- Review the violation report in `docs/reports/observer/`
- Fix the issues
- Re-run the check

### 4. Self-Learning
```bash
# Record the violation pattern for future reference
python asdlc.py learn "Fixed compliance issue: [description]"
```

## Integration

- **@BRAIN** - Uses Observer for monitoring
- **/cycle** - Compliance check before PR
- **/commit** - Pre-commit validation
- **/housekeeping** - Part of maintenance

## Observer Checks

| Check | Description |
|-------|-------------|
| Code Quality | Naming conventions, style |
| Template Compliance | Correct template usage |
| Workflow Steps | Mandatory steps followed |
| Documentation | Required docs present |

#observe #compliance #monitoring #rules

## ⏭️ Next Steps
- **If Compliant:** Continue with current workflow
- **If Violations Found:** Fix issues and re-run `/observe`

---

## ENFORCEMENT REMINDER
Run Observer before major commits.
