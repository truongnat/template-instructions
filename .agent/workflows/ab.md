---
description: Intelligence - A/B Test - Generate Alternatives
---

# /ab - A/B Testing for Decisions

## ⚠️ PURPOSE
Generate and compare alternative approaches for any decision, architecture choice, or implementation strategy.

// turbo-all

## Quick Commands

```bash
# Generate A/B alternatives for a decision
python tools/intelligence/ab_test/ab_tester.py --prompt "implement user authentication"

# Compare two specific options
python tools/intelligence/ab_test/ab_tester.py --compare "JWT tokens" "Session cookies"

# Get recommendation based on context
python tools/core/brain/brain_cli.py ab-test "Should we use JWT or Session Auth?"
```

## When to Use

- Before major architectural decisions
- When choosing between technologies
- For implementation strategy choices
- During design phase

## Workflow Steps

### 1. Define the Decision
Clearly state the decision or choice you need to make.

### 2. Generate Alternatives
```bash
python tools/intelligence/ab_test/ab_tester.py --prompt "[your decision]"
```
This will:
- Generate 2 alternative approaches
- Search KB for past similar solutions
- Score each option

### 3. Review Comparison Report
Check the generated report at `docs/reports/ab_tests/YYYY-MM-DD-[topic].md`

### 4. Make Decision
Based on:
- Time estimate
- Complexity score
- Reliability rating
- Maintainability score

### 5. Document Choice
```bash
# Record the decision
python tools/core/brain/brain_cli.py learn "Chose [Option] for [Decision] because [Reason]"
```

## Output

The A/B test generates a comparison report:

```markdown
# A/B Test: [Decision]

## Option A: [Name]
- **Pros:** ...
- **Cons:** ...
- **Time Estimate:** ...
- **Complexity:** X/10

## Option B: [Name]
- **Pros:** ...
- **Cons:** ...
- **Time Estimate:** ...
- **Complexity:** X/10

## Recommendation
[Based on scoring...]
```

## Integration

- **@SA** - Architecture decisions
- **@PM** - Technology choices
- **/explore** - Deep investigation
- **/planning** - Planning phase decisions

#ab-test #decisions #alternatives #comparison

## ⏭️ Next Steps
- **If Decision Made:** Proceed with `/cycle` or `/orchestrator`
- **If More Research Needed:** Trigger `/explore`

---

## ENFORCEMENT REMINDER
Document A/B test results for future reference.
