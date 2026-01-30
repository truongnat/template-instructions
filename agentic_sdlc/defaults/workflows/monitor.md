---
description: Intelligence - Monitor - System Health Check
---

# /monitor - System Health Monitoring

## ⚠️ PURPOSE
Check overall system health, identify missing documentation, detect obsolete code, and get improvement suggestions.

// turbo-all

## Quick Commands

```bash
# Full health check
python asdlc.py health

# Detailed brain/intelligence health
python asdlc.py brain health
```

## When to Use

- Start of each work session
- Before major releases
- During housekeeping
- After major changes

## Workflow Steps

### 1. Run Health Check
```bash
python asdlc.py health
```

### 2. Review Health Status

**Health Indicators:**
| Status | Score | Description |
|--------|-------|-------------|
| 🟢 Healthy | 80-100 | System in good shape |
| 🟡 Warning | 50-79 | Some issues to address |
| 🔴 Critical | 0-49 | Immediate attention needed |

### 3. Review Metrics

The monitor checks:
- **Documentation Coverage** - Are all features documented?
- **Test Coverage Gaps** - Missing tests
- **Obsolete Code** - Unused files, deprecated functions
- **Compliance Trends** - Observer violation rate over time
- **Performance Issues** - Slow functions, memory leaks

### 4. Get Detailed Brain Health
```bash
python asdlc.py brain health
```

### 5. Address Issues
Based on suggestions:
- Add missing documentation
- Create tests for uncovered code
- Remove obsolete files
- Fix compliance issues

### 6. Verify Fix
Re-run health check to confirm improvements.

## Health Check Areas

| Area | What's Checked |
|------|----------------|
| Documentation | `docs/` directory, walkthroughs, plans |
| Brain State | `.agent/` directory integrity |
| Tools | `agentic_sdlc/` directory structure |
| KB Health | Entry count, category distribution |

## Integration

- **@BRAIN** - System oversight
- **/housekeeping** - Maintenance routine
- **/validate** - Tool reference validation
- **/metrics** - Detailed statistics

#monitor #health #system #metrics

## ⏭️ Next Steps
- **If Healthy:** Continue normal work
- **If Warning:** Schedule `/housekeeping`
- **If Critical:** Address issues immediately

---

## ENFORCEMENT REMINDER
Run health check at the start of each session.
