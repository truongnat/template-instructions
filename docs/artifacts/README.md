# Artifacts Directory

This folder stores IDE-generated artifacts that must be persisted for self-learning.

## What Goes Here

| Artifact Type | Example |
|---------------|---------|
| Analysis reports | `2026-01-05-workflow-analysis.md` |
| Task summaries | `2026-01-05-task-refactoring.md` |
| Investigation reports | `2026-01-05-explore-auth.md` |
| Gap analysis | `2026-01-05-gap-analysis.md` |

## Naming Convention

```
[YYYY-MM-DD]-[task-name].md
```

## Sync to Neo4j

After adding artifacts:

```bash
agentic-sdlc kb compound sync
```
