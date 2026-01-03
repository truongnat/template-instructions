---
description: Analytics & Metrics - Measure System Health and Performance
---

# /metrics - Analytics & Metrics Workflow

**When to Use:** Weekly, End of Sprint, On Demand
**Flow:** Collect → Analyze → Visualize → Report
**Output:** Metrics Dashboard

## Overview
The `/metrics` workflow gathers data from the project workflow, Knowledge Base, and Git history to provide insights into team performance, code quality, and learning velocity.

## Workflow Steps

### 1. Knowledge Base Metrics
**Source:** `.agent/knowledge-base/`
**Metrics:**
- Total Entries (Growth trend)
- Category Breakdown (Bugs vs Features)
- Reuse Rate (References in code/commits)
- "Gold" Entries (Highly referenced)

```bash
# Example: Count KB entries
find .agent/knowledge-base -name "*.md" | wc -l
```

### 2. Workflow Metrics
**Source:** `docs/sprints/*/logs/`
**Metrics:**
- Cycle Time (Start to Finish)
- Workflow Frequency (Most used workflows)
- Error Rate (Failed workflows)
- Approval Time (Time in review)

### 3. Code & Quality Metrics
**Source:** Git & CI/CD
**Metrics:**
- Bug Rate (Bugs per sprint)
- Test Coverage
- Documentation Coverage
- Technical Debt Ratio

### 4. Generate Report
**Output:** `docs/reports/Metrics-Dashboard-YYYY-MM-DD.md`

**Dashboard Sections:**
1. **Executive Summary:** High-level health (Green/Yellow/Red)
2. **Learning Velocity:** Are we getting smarter? (KB growth)
3. **Delivery Velocity:** Are we faster? (Cycle time)
4. **Quality Index:** Are we breaking less? (Bug rate)

## Usage Examples

### Weekly Health Check
```
@REPORTER /metrics --period weekly
```

### Sprint Analysis
```
@REPORTER /metrics --sprint 5
```

### Deep Dive: Quality
```
@REPORTER /metrics --type quality --period monthly
```

## Integration with Roles

### @REPORTER
- Owns metrics generation
- Distributes reports

### @PM
- Uses metrics for planning and adjustments

### @ORCHESTRATOR
- Auto-generates weekly dashboard

## Metric Definitions

| Metric | Definition | Good | Bad |
|--------|------------|------|-----|
| **KB Reuse** | % of tasks referencing KB | > 50% | < 10% |
| **Cycle Time** | Avg hours per task | < 4h | > 8h |
| **First-Time Fix** | % bugs fixed in 1 attempt | > 80% | < 50% |

#workflow #metrics #analytics #reporting
