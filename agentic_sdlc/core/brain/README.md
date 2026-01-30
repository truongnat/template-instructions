# Brain CLI

Command-line interface for Brain operations and state management.

## Files

| File | Purpose |
|------|---------|
| `brain_cli.py` | CLI entry point for brain commands |
| `state_manager.py` | Global state tracking for SDLC phases |

## Usage

```bash
# Check status
python agentic_sdlc/core/brain/brain_cli.py status

# Transition state
python agentic_sdlc/core/brain/brain_cli.py transition DESIGNING

# Sync brain
python agentic_sdlc/core/brain/brain_cli.py sync

# Get recommendations
python agentic_sdlc/core/brain/brain_cli.py recommend "implement feature"
```

## Note

Intelligence components (Observer, Judge, Learner, etc.) have been moved to `agentic_sdlc/intelligence/`.

See [Intelligence README](../../intelligence/README.md) for details.
