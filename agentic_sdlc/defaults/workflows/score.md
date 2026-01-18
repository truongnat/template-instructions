---
description: Intelligence - Score - Quality Scoring with Judge
---

# /score - Quality Scoring Workflow

## ⚠️ PURPOSE
Score code, reports, or artifacts using the Judge agent to assess quality and get improvement suggestions.

// turbo-all

## Quick Commands

```bash
# Score a code file
python tools/intelligence/judge/scorer.py --code src/app.py

# Score a report or document
python tools/intelligence/judge/scorer.py --report docs/walkthroughs/latest.md

# Score via Brain CLI
python tools/core/brain/brain_cli.py score "path/to/file.py"

# Score A/B test alternatives
python tools/intelligence/judge/scorer.py --ab-test docs/reports/ab_tests/YYYY-MM-DD-auth.md
```

## When to Use

- After completing implementation
- Before submitting PR
- During code review
- To validate documentation quality

## Workflow Steps

### 1. Identify Target
Determine what you want to score:
- Code file
- Documentation
- Report
- A/B test result

### 2. Run Scoring
```bash
python tools/intelligence/judge/scorer.py --code [file_path]
```

### 3. Review Score

**Code Scoring (0-100):**
| Dimension | Description |
|-----------|-------------|
| Complexity | Cyclomatic complexity, nesting depth |
| Readability | Naming, comments, structure |
| Security | Vulnerabilities, best practices |
| Performance | Efficiency, optimization |
| Maintainability | Modularity, DRY, SOLID |

**Report Scoring (0-100):**
| Dimension | Description |
|-----------|-------------|
| Completeness | All sections present |
| Clarity | Well-written, understandable |
| Accuracy | Correct information |
| Actionability | Clear next steps |

### 4. Address Issues
If score < 80:
- Review improvement suggestions
- Make necessary changes
- Re-score to verify

### 5. Document Result
```bash
python tools/core/brain/brain_cli.py learn "Improved [file] quality from X to Y"
```

## Score Thresholds

| Score | Status | Action |
|-------|--------|--------|
| 90-100 | ✅ Excellent | Ship it |
| 70-89 | 🟡 Good | Minor improvements optional |
| 50-69 | 🟠 Needs Work | Address issues before PR |
| 0-49 | 🔴 Critical | Major refactoring needed |

## Integration

- **@TESTER** - Quality assurance
- **/cycle** - Pre-PR scoring
- **/review** - Code review support
- **/commit** - Score before commit

#score #quality #judge #metrics

## ⏭️ Next Steps
- **If Score ≥ 80:** Proceed with `/commit` or `/review`
- **If Score < 80:** Fix issues and re-score

---

## ENFORCEMENT REMINDER
Target score of 80+ before committing code.
