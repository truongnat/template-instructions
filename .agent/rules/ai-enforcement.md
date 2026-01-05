## ⚠️ AI AGENT ENFORCEMENT (MANDATORY)
> **CRITICAL:** AI agents (Gemini, Claude, Cursor, etc.) MUST follow these rules BEFORE starting any task.
### Pre-Task Requirements
1. **Read Workflow File First** - When user types /command, READ .agent/workflows/[command].md before any action
2. **Activate Appropriate Roles** - Check the Role Activation Matrix in GEMINI.md
3. **Follow State Machine** - Run python tools/brain/brain_cli.py status to check current state  
4. **Search Brain** - Before implementing, run `agentic-sdlc learn --search "[keywords]"`
5. **Document Learnings** - After task completion, consider KB entry if solution was non-obvious
### Violation = System Failure
If an AI agent implements without following workflows, the brain system is NOT being used.
---
