---
inclusion: always
---

# Compound Learning System

## Philosophy
**Each unit of engineering work should make subsequent units of work easier—not harder.**

Every bug fixed, pattern discovered, and solution documented becomes permanent knowledge that compounds over time.

## The Compound Loop

```
Problem → Solution → Document → Search → Reuse → Compound
```

### When to Compound Knowledge

**ALWAYS document when:**
- Bug required 3+ attempts to fix
- Solution was non-obvious or creative
- Issue likely to recur across sprints
- Pattern applies to multiple features
- Security vulnerability discovered
- Performance optimization achieved

**NEVER skip documentation for:**
- Critical/High priority bugs
- Architecture decisions
- Security fixes
- Cross-cutting concerns

## Knowledge Entry Structure

All entries MUST use YAML frontmatter for searchability:

```yaml
---
title: "Brief descriptive title"
category: bug|feature|architecture|security|performance|platform
priority: critical|high|medium|low
sprint: sprint-N
date: YYYY-MM-DD
tags: [tag1, tag2, tag3]
related_files: [path/to/file1, path/to/file2]
attempts: 3
time_saved: "2 hours"
---

## Problem
Clear description of the issue

## Root Cause
What actually caused the problem

## Solution
Step-by-step solution

## Prevention
How to avoid this in the future

## Related Patterns
Links to similar issues
```

## Knowledge Categories

```
.agent/knowledge-base/
├── bugs/
│   ├── critical/
│   ├── high/
│   ├── medium/
│   └── low/
├── features/
│   ├── authentication/
│   ├── performance/
│   └── integration/
├── architecture/
├── security/
├── performance/
└── platform-specific/
```

## Search-First Workflow

**Before starting ANY complex work:**

1. Search knowledge base index
2. Check related categories
3. Review similar patterns
4. Apply learned solutions
5. Document new insights

## Metrics That Matter

Track compound effectiveness:
- **Time Saved** - Hours saved by reusing solutions
- **Attempts Reduced** - First-time fix rate improvement
- **Pattern Reuse** - How often entries are referenced
- **Knowledge Coverage** - % of bugs with documented solutions

## Auto-Compounding Triggers

System automatically creates entries when:
- Bug marked `#fixbug-critical` or `#fixbug-high`
- Security review finds vulnerabilities
- Performance improvement > 20%
- Architecture decision documented
- Platform-specific issue resolved

## Integration with Roles

### @DEV
- Search KB before implementing complex features
- Document non-obvious solutions immediately
- Tag commits with KB entry references

### @TESTER
- Search KB for known bug patterns
- Document new test strategies
- Link test failures to KB entries

### @SA
- Document architecture decisions
- Reference KB patterns in designs
- Update KB when patterns evolve

### @SECA
- Document all security fixes
- Create prevention patterns
- Maintain security checklist

## Compound Metrics Dashboard

Generate weekly:
```
📊 Compound System Health
- Total Entries: [N]
- Entries This Week: [N]
- Time Saved: [N hours]
- Reuse Rate: [N%]
- Coverage: [N%]
```

#compound-learning #knowledge-base #continuous-improvement
