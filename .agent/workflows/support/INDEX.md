# Support Workflows Index

> **Background operations, maintenance, and intelligence workflows.**

**Last Updated:** 2026-01-03

## Overview

Support workflows handle cross-cutting concerns like knowledge management, release automation, and system maintenance. These workflows are typically invoked after primary work is complete.

## Workflows

| Command | Description | Status |
|---------|-------------|--------|
| `/brain` | LEANN AI Brain - Automated Project Memory | ✅ Active |
| `/compound` | Compound Learning - Knowledge Capture After Tasks | ✅ Active |
| `/release` | Release Management - Changelog and versioning | ⚠️ Stub |
| `/housekeeping` | Cleanup & Maintenance - Legacy file management | ⚠️ Stub |
| `/route` | Request Routing - Direct tasks to appropriate roles | ⚠️ Stub |

## Workflow Details

### `/brain` - AI Brain Management
- **File:** `brain.md`
- **Purpose:** Synchronize and manage project intelligence
- **Turbo Mode:** `// turbo-all` enabled for auto-execution
- **Operations:**
  - Quick Sync: `python tools/neo4j/brain_parallel.py --sync`
  - Full Sync: `python tools/neo4j/brain_parallel.py --full`
  - LEANN indexing
  - Neo4j synchronization
  - KB index update
  - Recommendations

### `/compound` - Compound Learning
- **File:** `compound.md`
- **Purpose:** Capture knowledge after completing tasks
- **Triggers:**
  - Bug fixed (medium+ priority)
  - Feature completed
  - Complex problem solved (3+ hours)
- **Steps:**
  1. Create KB entry from template
  2. Fill problem/solution/learnings
  3. Sync to Neo4j
  4. Update KB index
  5. Record success in learning engine

### `/release` - Release Management ⚠️
- **File:** `release.md`
- **Status:** Stub - needs implementation
- **Purpose:** Automate versioning and changelog updates
- **Features:** Semantic versioning, changelog generation, git tagging

### `/housekeeping` - Cleanup & Maintenance ⚠️
- **File:** `housekeeping.md`
- **Status:** Stub - needs implementation
- **Purpose:** Clean up legacy files, organize project structure
- **Use Case:** Sprint transitions, major releases

### `/route` - Request Routing ⚠️
- **File:** `route.md`
- **Status:** Stub - needs implementation
- **Purpose:** Analyze requests and delegate to appropriate roles
- **Use Case:** Automated task assignment

## Usage Examples

```bash
# Sync project brain
/brain

# Capture knowledge after task completion
/compound

# Get recommendations
python tools/neo4j/brain_parallel.py --recommend "implement caching"
```

## Intelligence Stack

```
┌─────────────────────────────────────┐
│           /brain Workflow           │
├─────────────────────────────────────┤
│  LEANN Vector Search (Local Index)  │
├─────────────────────────────────────┤
│  Neo4j Knowledge Graph (Cloud)      │
├─────────────────────────────────────┤
│  File-based KB (.agent/knowledge-base) │
└─────────────────────────────────────┘
```

## Tags

`#support` `#brain` `#learning` `#maintenance` `#intelligence`
