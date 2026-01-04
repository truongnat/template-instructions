---
description: [Support] @BRAIN Meta-Level System Controller
---

# Brain Workflow

> **Skill Definition:** [View Skill](../../skills/role-brain.md)

## Identity
@BRAIN is the **Meta-Level Controller** that supervises ALL workflows in the system.
Brain is NOT an executor—it monitors, detects issues, and routes to appropriate handlers.

## ⚠️ STRICT EXECUTION PROTOCOL (MANDATORY)
All steps are mandatory for proper brain synchronization.

// turbo-all

## Supervisor Commands (Meta-Level)
```bash
# Watch all active workflows (monitoring mode)
python tools/brain/brain_cli.py watch

# Route a request to appropriate workflow
python tools/brain/brain_cli.py route "add user authentication"

# Check system health
python tools/brain/brain_cli.py health
```

## State Management (NEW)
```bash
# Initialize state for a sprint
python tools/brain/brain_cli.py init 1

# Check status
python tools/brain/brain_cli.py status

# Transition to new state
python tools/brain/brain_cli.py transition DESIGNING --reason "Design phase started"

# Validate current state
python tools/brain/brain_cli.py validate

# Rollback to previous state
python tools/brain/brain_cli.py rollback
```

## Quick Sync
```bash
python tools/neo4j/brain_parallel.py --sync
```

## Full Sync (All Operations)
```bash
python tools/neo4j/brain_parallel.py --full
```

## Manual Steps

### 1. Index Project (LEANN)
```bash
leann index --path . --update
```

### 2. Sync to Neo4j
```bash
python tools/neo4j/sync_skills_to_neo4j.py
python tools/neo4j/document_sync.py --all
```

### 3. Update KB Index
```bash
python bin/kb_cli.py update-index
```

### 4. Get Recommendations
```bash
python tools/neo4j/brain_parallel.py --recommend "[task description]"
```

#brain #leann #neo4j #self-learning
