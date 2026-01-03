---
description: LEANN AI Brain - Automated Project Memory
---

# LEANN AI Brain Workflow

This workflow manages the automated project memory using LEANN, Neo4j, and the self-learning engine.

// turbo-all

---

## ⚡ Parallel Execution (Recommended)

Use these commands for faster, concurrent execution of brain operations:

### Quick Parallel Sync
```bash
python tools/neo4j/brain_parallel.py --sync
```

### Full Sync (All Operations)
```bash
python tools/neo4j/brain_parallel.py --full
```

### View All Statistics
```bash
python tools/neo4j/brain_parallel.py --stats
```

### Get Recommendations
```bash
python tools/neo4j/brain_parallel.py --recommend "your task description"
```

---

## 🚀 Setup & Initialization

1. **First-Time Setup (Sequential)**
   ```bash
   python tools/neo4j/brain_parallel.py --setup
   ```
   
   *Or manually:*
   ```bash
   pip install leann-core leann-backend-hnsw neo4j python-dotenv
   leann index --path .
   python tools/neo4j/learning_engine.py --setup
   ```

---

## 🧠 Memory & Reasoning Management

### Individual Commands (for selective operations)

2. **Update LEANN Index (Vector)**
   ```bash
   leann index --update
   ```

3. **Sync KB Entries to Neo4j**
   ```bash
   python tools/neo4j/sync_skills_to_neo4j.py
   ```

4. **Sync ALL Documents to Neo4j** (Plans, Reports, Artifacts)
   ```bash
   # Sync all document types
   python tools/neo4j/document_sync.py --all
   
   # Sync specific types
   python tools/neo4j/document_sync.py --type plans
   python tools/neo4j/document_sync.py --type reports
   python tools/neo4j/document_sync.py --type artifacts
   
   # Dry run (preview)
   python tools/neo4j/document_sync.py --dry-run
   ```

---

## 🎓 Self-Learning Engine

5. **Record Error Patterns** (After fixing bugs)
   ```bash
   python tools/neo4j/learning_engine.py --record-error "TypeError" "Cannot read property X of undefined" --resolution "Added null check" --approach "defensive_coding"
   ```

6. **Record Success Patterns** (After completing tasks)
   ```bash
   python tools/neo4j/learning_engine.py --record-success "task-123" --task-type "auth_feature" --success-approach "JWT with refresh tokens"
   ```

7. **Get Recommendations** (Before starting new tasks)
   ```bash
   python tools/neo4j/learning_engine.py --recommend "implement user authentication"
   ```

8. **Find Similar Errors**
   ```bash
   python tools/neo4j/learning_engine.py --similar-errors "ConnectionError"
   ```

9. **Find Reasoning Paths**
   ```bash
   python tools/neo4j/learning_engine.py --reasoning-path "TypeError" "null check"
   ```

10. **View Learning Statistics**
    ```bash
    python tools/neo4j/learning_engine.py --stats
    python tools/neo4j/learning_engine.py --patterns
    ```

---

## 🗣️ Role Communication System

11. **Send a Message**
    ```bash
    python tools/communication/cli.py send --channel general --thread "Task Name" --role <ROLE> --content "Message"
    ```

12. **View History**
    ```bash
    python tools/communication/cli.py history --channel general --thread "Task Name" --limit 10
    ```

---

## 📊 Statistics & Reporting

13. **View All Stats (Parallel)**
    ```bash
    python tools/neo4j/brain_parallel.py --stats
    ```

    *Individual stats:*
    ```bash
    python tools/neo4j/sync_skills_to_neo4j.py --stats-only
    python tools/neo4j/document_sync.py --stats-only
    python tools/neo4j/learning_engine.py --stats
    ```

---

## 📋 Best Practices

| When | Action | Command |
|------|--------|---------|
| **Starting Work** | Quick sync + recommendations | `--sync` then `--recommend` |
| **After Bug Fix** | Record error pattern | `--record-error` |
| **After Task** | Record success pattern | `--record-success` |
| **Daily/Weekly** | Full sync | `--full` |
| **Before Tasks** | Get recommendations | `--recommend "task"` |

---

## 🔄 Auto-Learning Triggers

The brain automatically learns when:
- ✅ Bug fixed (priority medium+)
- ✅ Task required 3+ attempts
- ✅ Same error occurred 2+ times
- ✅ Complex feature completed (4+ hours)
- ✅ Security/performance issue resolved

---

## ⚙️ Advanced Options

```bash
# Skip LEANN (Neo4j only)
python tools/neo4j/brain_parallel.py --sync --no-leann

# Custom worker count
python tools/neo4j/brain_parallel.py --sync --workers 8
```

#brain #neo4j #self-learning #knowledge-graph #parallel

