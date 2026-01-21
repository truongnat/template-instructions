---
description: Support - BRAIN Meta-Level System Controller
---

# Brain Workflow

> **Skill Definition:** [View Skill](../../skills/brain/SKILL.md)

## Identity
@BRAIN is the **Meta-Level Controller** that supervises ALL workflows in the system.
Brain is NOT an executor—it monitors, detects issues, routes to handlers, scores quality, and creates self-improvement plans.

// turbo-all

## Root Components (Layer 2: Intelligence)

### Observer (Compliance Monitor)
```bash
# Check compliance of an action
python tools/core/brain/brain_cli.py observe --action "create file" --context '{"file": "test.py"}'

# Show compliance stats
python tools/core/brain/brain_cli.py observe
```

### Judge (Quality Scorer)
```bash
# Score a file
python tools/core/brain/brain_cli.py score "path/to/file.py"

# Score a report
python tools/core/brain/brain_cli.py score "docs/reports/latest.md"
```

### Learner (Auto-Learning)
```bash
# Record learning
python tools/core/brain/brain_cli.py learn "Fixed bug in auth module by updating token expiry"

# Get recommendations
python tools/core/brain/brain_cli.py recommend "implement oauth"
```

### A/B Tester (Decision Making)
```bash
# Run A/B test
python tools/core/brain/brain_cli.py ab-test "Should we use JWT or Session Auth?"
```

### Router (Model Selection)
```bash
# Route request to optimal AI model
python tools/core/brain/brain_cli.py route "Generate complex architectural diagram"
```

### Artifact Generator
```bash
# Generate document from template
python tools/core/brain/brain_cli.py gen --template "project-plan" --context '{"project": "New App"}' --output "plan.md"
```

### Health Monitor
```bash
# Check system health
python tools/core/brain/brain_cli.py health

# Get improvement suggestions
python tools/core/brain/brain_cli.py health --suggest
```

## State Management (Layer 1: Core)
```bash
python tools/core/brain/brain_cli.py init 1          # Initialize sprint
python tools/core/brain/brain_cli.py status          # Check status
python tools/core/brain/brain_cli.py transition STATE --reason "Reason"
python tools/core/brain/brain_cli.py validate        # Validate state
python tools/core/brain/brain_cli.py rollback        # Rollback
```

## Sync Commands
```bash
python tools/core/brain/brain_cli.py sync      # Quick sync
python tools/core/brain/brain_cli.py full-sync # Full sync
```

#brain #root-layer #meta-controller

## ⏭️ Next Steps
- **If State == IDLE:** Wait for user requirements (Active Listening)
- **If State == PLANNING:** Monitor @PM and validate Project Plan
- **If Critical Error:** Trigger `/emergency` workflow
- **If Task Complete:** Trigger `/compound` for learning

---

## ENFORCEMENT REMINDER
Ensure KB is synced before major operations.
