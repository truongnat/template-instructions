## ⚠️ AI AGENT ENFORCEMENT (MANDATORY)
> **CRITICAL:** AI agents (Gemini, Claude, Cursor, etc.) MUST follow these rules BEFORE starting any task.
### Pre-Task Requirements
1. **Read Workflow File First** - When user types /command, READ .agent/workflows/[command].md before any action
2. **Check AGENTS.md** - Periodically review `AGENTS.md` to see available capabilities. Use `python asdlc.py brain skills read <name>` to load specialized instructions.
3. **Activate Appropriate Roles** - Check the Role Activation Matrix in GEMINI.md
4. **Follow State Machine** - Run `python asdlc.py brain status` to check current state
5. **Search Brain** - Before implementing, run `asdlc brain learn --search "[keywords]"`
6. **Create Specification** - For new features, create `specification.md` BEFORE `implementation_plan.md`
7. **Document Learnings** - After task completion, consider KB entry if solution was non-obvious
### Violation = System Failure
If an AI agent implements without following workflows, the brain system is NOT being used.
---
