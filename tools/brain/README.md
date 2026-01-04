# Brain Tools

This directory contains tools for the Brain orchestrator system.

## Files

| File | Description |
|------|-------------|
| `state_manager.py` | State machine persistence for `.brain-state.json` |
| `brain_cli.py` | CLI interface for @BRAIN commands |

## Usage

### Initialize Brain State for a Sprint
```bash
python tools/brain/brain_cli.py init 1
```

### Check Status
```bash
python tools/brain/brain_cli.py status
```

### Transition to New State
```bash
python tools/brain/brain_cli.py transition DESIGNING --reason "Design phase started"
```

### Validate Current State
```bash
python tools/brain/brain_cli.py validate
```

### Rollback to Previous State
```bash
python tools/brain/brain_cli.py rollback
```

### Quick Brain Sync
```bash
python tools/brain/brain_cli.py sync
```

### Get Recommendations
```bash
python tools/brain/brain_cli.py recommend "implement user authentication"
```

## State Machine

The Brain follows this state flow:

```
IDLE → PLANNING → PLAN_APPROVAL → DESIGNING → DESIGN_REVIEW → 
DEVELOPMENT → TESTING → BUG_FIXING → DEPLOYMENT → REPORTING → 
FINAL_REVIEW → FINAL_APPROVAL → COMPLETE
```

State is persisted in `docs/sprints/sprint-N/.brain-state.json`.

## Integration

- See `.agent/skills/role-brain.md` for full documentation
- See `.agent/workflows/support/brain.md` for sync workflows
