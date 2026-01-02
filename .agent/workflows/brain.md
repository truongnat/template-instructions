---
description: LEANN AI Brain - Automated Project Memory
---

# LEANN AI Brain Workflow

This workflow manages the automated project memory using LEANN, Neo4j, and the self-learning engine.

## 🚀 Setup & Initialization

1. **Install Dependencies**
   ```bash
   pip install leann-core leann-backend-hnsw neo4j python-dotenv
   ```

2. **Initialize Project Index**
   ```bash
   leann index --path .
   ```

3. **Setup Neo4j Learning Schema**
   ```bash
   python tools/neo4j/learning_engine.py --setup
   ```

## 🧠 Memory & Reasoning Management

4. **Update LEANN Index (Vector)**
   ```bash
   leann index --update
   ```

5. **Sync KB Entries to Neo4j**
   ```bash
   python tools/neo4j/sync_skills_to_neo4j.py
   ```

6. **Sync ALL Documents to Neo4j** (Plans, Reports, Artifacts)
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

## 🎓 Self-Learning Engine

7. **Record Error Patterns** (After fixing bugs)
   ```bash
   python tools/neo4j/learning_engine.py --record-error "TypeError" "Cannot read property X of undefined" --resolution "Added null check" --approach "defensive_coding"
   ```

8. **Record Success Patterns** (After completing tasks)
   ```bash
   python tools/neo4j/learning_engine.py --record-success "task-123" --task-type "auth_feature" --success-approach "JWT with refresh tokens"
   ```

9. **Get Recommendations** (Before starting new tasks)
   ```bash
   python tools/neo4j/learning_engine.py --recommend "implement user authentication"
   ```

10. **Find Similar Errors**
    ```bash
    python tools/neo4j/learning_engine.py --similar-errors "ConnectionError"
    ```

11. **Find Reasoning Paths**
    ```bash
    python tools/neo4j/learning_engine.py --reasoning-path "TypeError" "null check"
    ```

12. **View Learning Statistics**
    ```bash
    python tools/neo4j/learning_engine.py --stats
    python tools/neo4j/learning_engine.py --patterns
    ```

## 🗣️ Role Communication System

13. **Send a Message**
    ```bash
    python tools/communication/cli.py send --channel general --thread "Task Name" --role <ROLE> --content "Message"
    ```

14. **View History**
    ```bash
    python tools/communication/cli.py history --channel general --thread "Task Name" --limit 10
    ```

## 📊 Statistics & Reporting

15. **View KB Stats**
    ```bash
    python tools/neo4j/sync_skills_to_neo4j.py --stats-only
    ```

16. **View Document Stats**
    ```bash
    python tools/neo4j/document_sync.py --stats-only
    ```

## 📋 Best Practices

- **Before Tasks:** Search KB and get recommendations
- **After Bug Fixes:** Record error patterns
- **After Task Completion:** Record success patterns
- **Weekly:** Sync all documents to Neo4j
- **Use `/brain <query>`** to trigger this workflow

## 🔄 Auto-Learning Triggers

The brain automatically learns when:
- Bug fixed (priority medium+)
- Task required 3+ attempts
- Same error occurred 2+ times
- Complex feature completed (4+ hours)
- Security/performance issue resolved

#brain #neo4j #self-learning #knowledge-graph

