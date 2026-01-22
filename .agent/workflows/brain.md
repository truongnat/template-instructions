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
python asdlc.py observe --action "create file" --context '{"file": "test.py"}'

# Show compliance stats
python asdlc.py observe
```

### Judge (Quality Scorer)
```bash
# Score a file
python asdlc.py score "path/to/file.py"

# Score a report
python asdlc.py score "docs/reports/latest.md"
```

### Learner (Auto-Learning)
```bash
# Record learning
python asdlc.py learn "Fixed bug in auth module by updating token expiry"

# Get recommendations
python asdlc.py recommend "implement oauth"
```

### A/B Tester (Decision Making)
```bash
# Run A/B test
python asdlc.py ab-test "Should we use JWT or Session Auth?"
```

### Router (Model Selection)
```bash
# Route request to optimal AI model
python asdlc.py route "Generate complex architectural diagram"
```

### Artifact Generator
```bash
# Generate document from template
python asdlc.py gen --template "project-plan" --context '{"project": "New App"}' --output "plan.md"
```

### Health Monitor
```bash
# Check system health
python asdlc.py health

# Get improvement suggestions
python asdlc.py health --suggest
```

## State Management (Layer 1: Core)
```bash
python asdlc.py init 1          # Initialize sprint
python asdlc.py status          # Check status
python asdlc.py transition STATE --reason "Reason"
python asdlc.py validate        # Validate state
python asdlc.py rollback        # Rollback
```

## Sync Commands
```bash
python asdlc.py sync      # Quick sync
python asdlc.py full-sync # Full sync
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
