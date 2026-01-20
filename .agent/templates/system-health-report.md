# System Health Report

**Report ID:** `[AUTO-GENERATED]`  
**Generated:** `[TIMESTAMP]`  
**System Version:** `[VERSION]`

---

## Executive Summary

**Overall Health Score:** `[0-100]` / 100  
**Status:** 🟢 HEALTHY | 🟡 WARNING | 🔴 CRITICAL  
**Issues Found:** `[COUNT]`  
**Components Checked:** `[COUNT]`

---

## Component Health Check

| Component | Status | Score | Last Check |
|-----------|--------|-------|------------|
| Layer 1 (Core) | 🟢 / 🟡 / 🔴 | `[0-100]` | `[TIME]` |
| Layer 2 (Intelligence) | 🟢 / 🟡 / 🔴 | `[0-100]` | `[TIME]` |
| Layer 3 (Infrastructure) | 🟢 / 🟡 / 🔴 | `[0-100]` | `[TIME]` |
| Knowledge Base | 🟢 / 🟡 / 🔴 | `[0-100]` | `[TIME]` |
| Neo4j Graph | 🟢 / 🟡 / 🔴 | `[0-100]` | `[TIME]` |
| MCP Connectors | 🟢 / 🟡 / 🔴 | `[0-100]` | `[TIME]` |

---

## Missing Components

### Documentation Gaps
- **Missing:** `[COUNT]` files without documentation
- **Critical Files:**
  - `[file1.ext]` - No header comments
  - `[file2.ext]` - No README
  - `[file3.ext]` - Missing API docs

**Recommendation:** Add documentation for high-priority files first

### Test Coverage Gaps
- **Overall Coverage:** `[X]%` (Target: 80%+)
- **Files with No Tests:**
  - `[file1.ext]`
  - `[file2.ext]`
  - `[file3.ext]`

**Recommendation:** Focus on core business logic first

### Missing Artifacts
- **Sprint Plan:** Missing for Sprint `[N]`
- **Walkthroughs:** `[COUNT]` completed tasks without walkthrough
- **Architecture Docs:** `[Component]` not documented

**Recommendation:** Document recent completions immediately

---

## Improvements Needed

### Low-Quality Code (Judge Score < 70)

#### File: `[file1.ext]`
- **Quality Score:** `[SCORE]` / 100
- **Issues:**
  - High complexity (cyclomatic: `[VALUE]`)
  - Poor naming
  - No tests
- **Priority:** High | Medium | Low
- **Recommendation:** `[Specific actions]`

#### File: `[file2.ext]`
- **Quality Score:** `[SCORE]` / 100
- **Issues:** `[Description]`
- **Recommendation:** `[Actions]`

### Architecture Debt
- **Issue:** `[Description]`
  - **Location:** `[Component/files]`
  - **Impact:** `[Impact description]`
  - **Recommendation:** `[How to address]`
  - **Effort:** Low | Medium | High

### Performance Bottlenecks
- **Function:** `[function_name]` in `[file.ext]`
  - **Issue:** O(n²) complexity
  - **Impact:** Slow for large datasets
  - **Recommendation:** Use hash map instead of nested loops
  - **Priority:** High | Medium | Low

---

## Obsolete Code

### Unused Files
- `[file1.ext]` - Last used: `[DATE]` (> 90 days ago)
- `[file2.ext]` - No imports/references found
- `[file3.ext]` - Replaced by `[new_file.ext]`

**Recommendation:** Review and delete if confirmed unused

### Deprecated Functions
- `[old_function]` in `[file.ext]`
  - **Deprecated Since:** `[DATE]`
  - **Replacement:** `[new_function]`
  - **Still Used In:** `[X]` files
  - **Recommendation:** Migrate to new function

### Dead Code Paths
- `[code_block]` in `[file.ext:line]`
  - **Reason:** Unreachable code
  - **Recommendation:** Remove

---

## Compliance Trends

### Observer Violation Rate
**Current Period:** `[START]` to `[END]`

| Period | Violations | Compliance % | Trend |
|--------|------------|--------------|-------|
| 2 weeks ago | `[COUNT]` | `[X]%` | - |
| 1 week ago | `[COUNT]` | `[X]%` | ⬆️/⬇️/➡️ |
| This week | `[COUNT]` | `[X]%` | ⬆️/⬇️/➡️ |

**Overall Trend:** ⬆️ Improving | ➡️ Stable | ⬇️ Declining

### Most Common Violations
1. `[Violation type]` - `[COUNT]` occurrences
2. `[Violation type]` - `[COUNT]` occurrences
3. `[Violation type]` - `[COUNT]` occurrences

**Recommendation:** Focus on top 3 violations for maximum impact

---

## Test Coverage Analysis

### Overall Coverage
- **Unit Tests:** `[X]%` (Target: 80%+)
- **Integration Tests:** `[X]%` (Target: 60%+)
- **E2E Tests:** `[X]%` (Target: 40%+)

### Coverage by Component
| Component | Coverage | Status | Priority |
|-----------|----------|--------|----------|
| `[Component 1]` | `[X]%` | 🟢/🟡/🔴 | High/Med/Low |
| `[Component 2]` | `[X]%` | 🟢/🟡/🔴 | High/Med/Low |

### Critical Paths Without Tests
1. `[Critical path 1]`
   - **Risk:** High | Medium | Low
   - **Recommendation:** Add tests immediately

2. `[Critical path 2]`
   - **Details:** `[Description]`

---

## Performance Metrics

### Response Times
| Endpoint/Function | Avg | P95 | P99 | Status |
|-------------------|-----|-----|-----|--------|
| `[endpoint1]` | `[X]ms` | `[X]ms` | `[X]ms` | 🟢/🟡/🔴 |
| `[endpoint2]` | `[X]ms` | `[X]ms` | `[X]ms` | 🟢/🟡/🔴 |

**Targets:**
- Avg < 200ms: 🟢
- Avg < 500ms: 🟡  
- Avg > 500ms: 🔴

### Memory Usage
- **Current:** `[X]MB`
- **Peak:** `[X]MB`
- **Trend:** ⬆️ Increasing | ➡️ Stable | ⬇️ Decreasing

**Memory Leaks Detected:** `[COUNT]`
- `[Location 1]` - `[Description]`

### Database Performance
- **Slow Queries:** `[COUNT]`
- **N+1 Queries:** `[COUNT]`
- **Missing Indexes:** `[COUNT]`

**Top Slow Query:**
```sql
[QUERY]
```
**Recommendation:** `[Optimization suggestion]`

---

## Security Health

### Known Vulnerabilities
- **Critical:** `[COUNT]`
- **High:** `[COUNT]`
- **Medium:** `[COUNT]`
- **Low:** `[COUNT]`

### Vulnerabilities Details
1. **CVE-XXXX-XXXXX** in `[dependency]`
   - **Severity:** Critical | High | Medium | Low
   - **Impact:** `[Description]`
   - **Fix:** Update to version `[X.Y.Z]`

### Security Best Practices Compliance
- **Input Validation:** `[X]%` covered
- **SQL Injection Protection:** `[X]%` covered
- **XSS Protection:** `[X]%` covered
- **Authentication:** Implemented | Partial | Missing
- **Authorization:** Implemented | Partial | Missing

---

## Knowledge Base Health

### KB Statistics
- **Total Entries:** `[COUNT]`
- **Entries Added (Last 30 days):** `[COUNT]`
- **Orphan Entries:** `[COUNT]` (not linked from anywhere)
- **Stale Entries:** `[COUNT]` (> 180 days old, no updates)

### KB Quality
- **Well-Documented:** `[X]%`
- **Missing Tags:** `[COUNT]` entries
- **Missing Examples:** `[COUNT]` entries
- **Broken Links:** `[COUNT]`

**Recommendation:** Review and update stale entries

---

## Neo4j Graph Health

### Graph Statistics
- **Total Nodes:** `[COUNT]`
- **Total Relationships:** `[COUNT]`
- **Orphan Nodes:** `[COUNT]` (no relationships)
- **Last Sync:** `[TIMESTAMP]`

### Graph Quality
- **Schema Compliance:** `[X]%`
- **Data Completeness:** `[X]%`
- **Relationship Accuracy:** `[X]%`

**Recommendation:** Sync and cleanup recommended

---

## Improvement Actions

### Critical (Do Immediately)
1. **`[Action 1]`**
   - **Issue:** `[Description]`
   - **Impact:** High | Medium | Low
   - **Effort:** `[TIME]` hours
   - **Owner:** `[Team/Role]`

2. **`[Action 2]`**
   - **Details:** `[Description]`

### High Priority (This Week)
1. `[Action 1]`
2. `[Action 2]`
3. `[Action 3]`

### Medium Priority (This Sprint)
1. `[Action 1]`
2. `[Action 2]`

### Low Priority (Backlog)
1. `[Action 1]`
2. `[Action 2]`

---

## Maintenance Schedule

### Daily
- [ ] Check Observer compliance report
- [ ] Review new violations
- [ ] Monitor performance metrics

### Weekly  
- [ ] Review this health report
- [ ] Address critical issues
- [ ] Update KB with new learnings
- [ ] Sync to Neo4j

### Monthly
- [ ] Comprehensive code quality review
- [ ] Security audit
- [ ] Documentation update sprint
- [ ] Performance optimization sprint

---

## Trend Analysis

### Health Score Trend
| Period | Score | Change |
|--------|-------|--------|
| 3 months ago | `[SCORE]` | - |
| 2 months ago | `[SCORE]` | `[+/-X]` |
| 1 month ago | `[SCORE]` | `[+/-X]` |
| Today | `[SCORE]` | `[+/-X]` |

**Trend:** ⬆️ Improving | ➡️ Stable | ⬇️ Declining

### Issue Resolution Rate
- **New Issues:** `[COUNT]` per week
- **Resolved Issues:** `[COUNT]` per week
- **Net Change:** `[+/-X]` per week

---

## Next Health Check

**Scheduled For:** `[DATE]`  
**Focus Areas:** `[Based on this report's findings]`

---

**Monitor Agent:** v1.0.0  
**Health Check Duration:** `[X]` seconds  
**Report Generated At:** `[TIMESTAMP]`
