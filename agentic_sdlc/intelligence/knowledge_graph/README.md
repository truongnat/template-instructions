# Neo4j Brain - Universal Document Storage & Self-Learning

Sync ALL project documents to Neo4j Cloud (AuraDB) and enable AI self-learning through pattern recognition.

## Overview

This module provides:
1. **Knowledge Base Sync** - Sync KB entries with skills extraction
2. **Document Sync** - Sync ALL documents (plans, reports, artifacts)
3. **Learning Engine** - Error tracking, pattern recognition, recommendations

## Prerequisites

```bash
pip install neo4j python-dotenv
```

## Configuration

Your `.env` file should contain:
```
NEO4J_URI=neo4j+s://your-instance.databases.neo4j.io
NEO4J_USERNAME=neo4j
NEO4J_PASSWORD=your-password
NEO4J_DATABASE=neo4j
```

---

## Scripts

### 1. sync_skills_to_neo4j.py
Syncs knowledge base entries with skills and technology extraction.

```bash
python agentic_sdlc/neo4j/sync_skills_to_neo4j.py
python agentic_sdlc/neo4j/sync_skills_to_neo4j.py --dry-run
python agentic_sdlc/neo4j/sync_skills_to_neo4j.py --stats-only
```

### 2. document_sync.py
Syncs ALL document types to Neo4j.

```bash
# Sync all documents
python agentic_sdlc/neo4j/document_sync.py --all

# Sync specific types
python agentic_sdlc/neo4j/document_sync.py --type plans
python agentic_sdlc/neo4j/document_sync.py --type reports
python agentic_sdlc/neo4j/document_sync.py --type artifacts
python agentic_sdlc/neo4j/document_sync.py --type workflows

# Preview without syncing
python agentic_sdlc/neo4j/document_sync.py --dry-run

# View statistics
python agentic_sdlc/neo4j/document_sync.py --stats-only
```

**Document Types:**
- `plans` - Project plans, sprint plans
- `reports` - Phase reports, test reports, metrics
- `artifacts` - Specs, designs, architecture docs
- `workflows` - Workflow definitions
- `knowledge` - Knowledge base entries
- `conversations` - Chat logs

### 3. learning_engine.py
Self-learning engine for pattern recognition and recommendations.

```bash
# Setup learning schema
python agentic_sdlc/neo4j/learning_engine.py --setup

# Record error patterns
python agentic_sdlc/neo4j/learning_engine.py --record-error "TypeError" "Cannot read X of undefined" \
    --resolution "Added null check" --approach "defensive_coding"

# Record success patterns
python agentic_sdlc/neo4j/learning_engine.py --record-success "task-123" \
    --task-type "auth_feature" --success-approach "JWT with refresh tokens"

# Get recommendations
python agentic_sdlc/neo4j/learning_engine.py --recommend "implement user authentication"

# Find similar errors
python agentic_sdlc/neo4j/learning_engine.py --similar-errors "ConnectionError"

# Find reasoning paths
python agentic_sdlc/neo4j/learning_engine.py --reasoning-path "TypeError" "null check"

# View statistics
python agentic_sdlc/neo4j/learning_engine.py --stats
python agentic_sdlc/neo4j/learning_engine.py --patterns
```

---

## Graph Schema

### Node Types

| Node | Properties | Description |
|------|------------|-------------|
| `Document` | id, title, type, author, version | Base document node |
| `Plan` | + sprint, approved_by | Project/sprint plans |
| `Report` | + phase, findings | Reports and metrics |
| `Artifact` | + status | Design specs |
| `KBEntry` | + category, skills | Knowledge base |
| `Error` | type, message, occurrence_count | Tracked errors |
| `Resolution` | description, approach, success_count | Error solutions |
| `Pattern` | type, approach, success_count | Success patterns |
| `Learning` | title, insight, confidence | Captured learnings |

### Relationships

```
(Document)-[:CREATED_BY]->(Role)
(Document)-[:BELONGS_TO]->(Sprint)
(Document)-[:REFERENCES]->(Document)
(Document)-[:SUPERCEDES]->(Document)
(Document)-[:HAS_CHUNK]->(ContentChunk)

(Error)-[:RESOLVED_BY]->(Resolution)
(Task)-[:USED_PATTERN]->(Pattern)
(Learning)-[:DERIVED_FROM]->(Error|Pattern)
```

---

## Cypher Queries

### Find Related Documents
```cypher
MATCH (d:Document {title: "Project Plan"})
-[:REFERENCES]->(related)
RETURN d, related
```

### View Error Resolution History
```cypher
MATCH (e:Error)-[r:RESOLVED_BY]->(res:Resolution)
RETURN e.type, e.message, res.description, r.use_count
ORDER BY r.use_count DESC
```

### Get Success Patterns
```cypher
MATCH (p:Pattern)
RETURN p.type, p.approach, p.success_count
ORDER BY p.success_count DESC
LIMIT 10
```

### Find Learning Path
```cypher
MATCH path = (e:Error)-[:RESOLVED_BY*..3]->(r:Resolution)
RETURN path
```

---

## Workflow Integration

### Before Starting Task
```bash
# Get recommendations
python agentic_sdlc/neo4j/learning_engine.py --recommend "your task description"
```

### After Bug Fix
```bash
# Record error pattern
python agentic_sdlc/neo4j/learning_engine.py --record-error "ErrorType" "Error message" \
    --resolution "What fixed it" --approach "approach_name"
```

### After Task Completion
```bash
# Record success pattern
python agentic_sdlc/neo4j/learning_engine.py --record-success "task-id" \
    --task-type "task_category" --success-approach "what worked"
```

### Weekly Sync
```bash
# Sync all documents
python agentic_sdlc/neo4j/document_sync.py --all
python agentic_sdlc/neo4j/sync_skills_to_neo4j.py
```

---

## Testing

```bash
# Run all Neo4j tests
pytest tests/test_document_sync.py tests/test_learning_engine.py -v

# Run integration tests (requires Neo4j connection)
pytest tests/test_document_sync.py tests/test_learning_engine.py -v -m integration
```

---

## Benefits

1. **Full Traceability** - All documents linked with relationships
2. **Version History** - Track document evolution
3. **Error Learning** - Never solve the same problem twice
4. **Pattern Recognition** - Know what approaches work best
5. **Smart Recommendations** - Get context-aware suggestions
6. **Sprint Context** - Documents organized by sprint

---

#neo4j #knowledge-graph #self-learning #documents

