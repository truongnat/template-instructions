# Neo4j Compound Integration - Complete Guide

## Overview

The TeamLifecycle framework uses **Neo4j as the "brain"** of the compound learning system. While the file system stores knowledge entries, Neo4j creates an intelligent knowledge graph that maps relationships between skills, technologies, KB entries, and people.

```
┌─────────────────────────────────────────────────────────────┐
│                  COMPOUND LEARNING SYSTEM                    │
└─────────────────────────────────────────────────────────────┘
                              │
                ┌─────────────┴─────────────┐
                ▼                           ▼
    ┌───────────────────┐       ┌───────────────────┐
    │   FILE SYSTEM     │       │   NEO4J BRAIN     │
    │   (.agent/kb/)    │◄─────►│   (Graph DB)      │
    └───────────────────┘       └───────────────────┘
    │                           │
    │ • Markdown files          │ • Skills graph
    │ • YAML frontmatter        │ • Technology map
    │ • Category folders        │ • Relationships
    │ • Full content            │ • Smart queries
    └───────────────────────────┘

         COMPOUND SCRIPTS (bin/)
         ├── kb.ps1              - Main interface
         ├── kb-compound.ps1     - Compound operations
         ├── kb-search.ps1       - File search
         ├── kb-add.ps1          - Add entries
         ├── kb-index.ps1        - Update index
         └── kb-stats.ps1        - Statistics
```

## Why Neo4j as the Brain?

### Traditional File System
- ✅ Simple storage
- ✅ Easy to browse
- ❌ No relationships
- ❌ Limited search
- ❌ No context

### Neo4j Knowledge Graph
- ✅ Relationship mapping
- ✅ Contextual queries
- ✅ Pattern discovery
- ✅ Learning paths
- ✅ Skill prerequisites

### Compound System (Both)
- ✅ **Best of both worlds**
- ✅ File system for content
- ✅ Neo4j for intelligence
- ✅ Automatic sync
- ✅ Compound learning

## Architecture

### Knowledge Graph Schema

```cypher
// Nodes
(KBEntry)      - Knowledge base entries
(Skill)        - Skills extracted from entries
(Technology)   - Technologies mentioned
(Category)     - Entry categories
(Person)       - Authors (@DEV, @UIUX, etc.)

// Relationships
(KBEntry)-[:BELONGS_TO]->(Category)
(KBEntry)-[:USES_TECHNOLOGY]->(Technology)
(KBEntry)-[:TEACHES]->(Skill)
(Person)-[:CREATED]->(KBEntry)
(Skill)-[:RELATED_TO]-(Skill)
(Technology)-[:REQUIRES_SKILL]->(Skill)
```

### Example Graph

```
    (@UIUX)
       │
       │ CREATED
       ▼
  [KB-2026-01-02-001]
       │
       ├─ BELONGS_TO ──► (UI/UX)
       │
       ├─ USES_TECHNOLOGY ──► (Figma)
       │                      (React)
       │
       └─ TEACHES ──► (User Research)
                      (Wireframing)
                      (Prototyping)
                           │
                           │ RELATED_TO
                           ▼
                      (Usability Testing)
```

## Setup

### 1. Neo4j Cloud (AuraDB)

Create a free Neo4j AuraDB instance:
1. Go to https://neo4j.com/cloud/aura/
2. Sign up for free tier
3. Create new instance
4. Save credentials

### 2. Environment Configuration

Create/update `.env` file:

```env
# Neo4j Cloud (AuraDB) Configuration
NEO4J_URI=neo4j+s://xxxxx.databases.neo4j.io
NEO4J_USERNAME=neo4j
NEO4J_PASSWORD=your-password-here
NEO4J_DATABASE=neo4j
```

### 3. Install Dependencies

```powershell
# Install Python dependencies
pip install neo4j python-dotenv

# Or using requirements.txt
pip install -r tools/neo4j/requirements.txt
```

### 4. Initial Sync

```powershell
# Sync all existing KB entries to Neo4j
python tools/neo4j/sync_skills_to_neo4j.py

# Or using compound script
.\bin\kb.ps1 compound sync
```

## Usage

### Compound Commands

The compound system provides enhanced commands that use both file system and Neo4j:

#### 1. Compound Search
Search both file system and Neo4j brain:

```powershell
# Search using main interface
.\bin\kb.ps1 compound search "authentication"

# Or directly
.\bin\kb-compound.ps1 search -SearchTerm "authentication"
```

**What it does:**
1. Queries Neo4j for related skills and technologies
2. Searches file system for matching entries
3. Shows combined results with context

#### 2. Compound Add
Add entry and automatically sync to Neo4j:

```powershell
# Interactive add with auto-sync
.\bin\kb.ps1 compound add

# Or directly
.\bin\kb-compound.ps1 add
```

**What it does:**
1. Creates new KB entry (interactive wizard)
2. Updates INDEX.md
3. Syncs to Neo4j brain
4. Extracts skills and relationships

#### 3. Compound Sync
Full synchronization to Neo4j:

```powershell
# Full sync
.\bin\kb.ps1 compound sync

# Or directly
.\bin\kb-compound.ps1 sync
```

**What it does:**
1. Updates INDEX.md
2. Syncs all entries to Neo4j
3. Creates relationships
4. Shows statistics

#### 4. Compound Query
Intelligent Neo4j queries:

```powershell
# Query Neo4j brain
.\bin\kb.ps1 compound query "React"

# Or directly
.\bin\kb-compound.ps1 query -SearchTerm "React"
```

**What it does:**
1. Searches skills by keyword
2. Finds related skills
3. Shows learning paths
4. Maps technology relationships

#### 5. Compound Stats
System health and statistics:

```powershell
# Show compound stats
.\bin\kb.ps1 compound stats

# Or directly
.\bin\kb-compound.ps1 stats
```

**What it does:**
1. File system statistics
2. Neo4j brain statistics
3. Connection status
4. Compound metrics

### Direct Neo4j Queries

For advanced queries, use the Python scripts directly:

```powershell
# List all skills
python tools/neo4j/query_skills_neo4j.py --all-skills

# Skills for specific technology
python tools/neo4j/query_skills_neo4j.py --tech "React"

# Related skills
python tools/neo4j/query_skills_neo4j.py --skill "Authentication"

# Learning path for category
python tools/neo4j/query_skills_neo4j.py --learning-path "Architecture"

# Search by keyword
python tools/neo4j/query_skills_neo4j.py --search "performance"

# Skills by author
python tools/neo4j/query_skills_neo4j.py --author "@UIUX"

# Skill prerequisites
python tools/neo4j/query_skills_neo4j.py --prerequisites "Advanced React"

# List all technologies
python tools/neo4j/query_skills_neo4j.py --technologies
```

## Workflow Integration

### Search-First Workflow

**Before solving any problem:**

```powershell
# 1. Compound search (file + Neo4j)
.\bin\kb.ps1 compound search "your problem"

# 2. If found, review solutions
# 3. If not found, solve and document
# 4. Add to KB with compound add
.\bin\kb.ps1 compound add
```

### Automatic Sync

The compound system automatically syncs when:
- New entry added via `compound add`
- Manual sync via `compound sync`
- Auto-compound detects new entries (last 24h)

### Auto-Compound Mode

```powershell
# Intelligent auto mode
.\bin\kb-compound.ps1 auto

# With search term
.\bin\kb-compound.ps1 auto -SearchTerm "oauth"
```

**Auto mode logic:**
1. If search term provided → Compound search
2. If new entries (24h) → Compound sync
3. Otherwise → Show compound stats

## Knowledge Extraction

### What Gets Extracted?

From each KB entry, the system extracts:

#### 1. Metadata
- Title
- Category
- Priority
- Date
- Author
- Tags

#### 2. Technologies
Automatically detected:
- Programming languages (React, Python, Java, etc.)
- Frameworks (Next.js, Vue, Angular, etc.)
- Databases (PostgreSQL, MongoDB, Neo4j, etc.)
- Tools (Docker, Git, Figma, etc.)

#### 3. Skills
Extracted from:
- Section headers (### Skill Name)
- Bold bullet points (**Skill Name**)
- Content analysis

#### 4. Relationships
Automatically created:
- Skills appearing in same entry → RELATED_TO
- Technologies used with skills → REQUIRES_SKILL
- Entries in same category → Implicit grouping

### Entry Format for Best Extraction

Use YAML frontmatter for metadata:

```yaml
---
title: "Clear descriptive title"
category: bug|feature|architecture|security|performance|platform
priority: critical|high|medium|low
sprint: sprint-N
date: YYYY-MM-DD
tags: [tag1, tag2, tag3]
related_files: [path/to/file1, path/to/file2]
attempts: 3
time_saved: "2 hours"
---

## Problem
Clear description

## Skills Required
- **Skill 1** - Description
- **Skill 2** - Description

## Technologies Used
- React
- Neo4j
- Docker

## Solution
Step-by-step solution

### 1. First Step
Details...

### 2. Second Step
Details...
```

## Query Examples

### Find Learning Path

```cypher
// Find learning path for UI/UX
MATCH (c:Category {name: "UI/UX"})<-[:BELONGS_TO]-(k:KBEntry)-[:TEACHES]->(s:Skill)
RETURN k.title, k.date, collect(s.name) as skills
ORDER BY k.date
```

### Find Related Skills

```cypher
// Find skills related to "Authentication"
MATCH (s1:Skill {name: "Authentication"})-[r:RELATED_TO]-(s2:Skill)
RETURN s2.name, r.strength
ORDER BY r.strength DESC
```

### Find Technology Stack

```cypher
// Find all technologies used with React
MATCH (t1:Technology {name: "React"})<-[:USES_TECHNOLOGY]-(k:KBEntry)-[:USES_TECHNOLOGY]->(t2:Technology)
WHERE t1 <> t2
RETURN t2.name, count(k) as usage_count
ORDER BY usage_count DESC
```

### Find Expert Authors

```cypher
// Find who knows most about a topic
MATCH (p:Person)-[:CREATED]->(k:KBEntry)-[:TEACHES]->(s:Skill)
WHERE toLower(s.name) CONTAINS "react"
RETURN p.name, count(DISTINCT s) as skill_count, collect(DISTINCT s.name) as skills
ORDER BY skill_count DESC
```

## Metrics & Monitoring

### Compound System Health

```powershell
.\bin\kb.ps1 compound stats
```

Shows:
- **File System Stats**
  - Total entries
  - By category
  - By priority
  - Recent activity
  - Growth trend

- **Neo4j Brain Stats**
  - Total skills
  - Total technologies
  - Total categories
  - Connection status

- **Compound Metrics**
  - Time saved
  - Reuse rate
  - Coverage percentage
  - Sync status

### Growth Tracking

Track compound effectiveness:
- **Week 1:** 10 entries, 50 skills
- **Week 2:** 15 entries, 75 skills (+50%)
- **Week 3:** 18 entries, 90 skills (+20%)
- **Time Saved:** 5 hours → 12 hours → 20 hours

## Troubleshooting

### Neo4j Connection Issues

```powershell
# Test connection
python tools/neo4j/sync_skills_to_neo4j.py --stats-only

# Check credentials
cat .env | Select-String "NEO4J"
```

### Sync Issues

```powershell
# Dry run to test
python tools/neo4j/sync_skills_to_neo4j.py --dry-run

# Full sync
python tools/neo4j/sync_skills_to_neo4j.py
```

### Query Issues

```powershell
# Verify data exists
python tools/neo4j/query_skills_neo4j.py --all-skills

# Check specific entry
python tools/neo4j/query_skills_neo4j.py --search "KB-2026-01-02"
```

## Best Practices

### 1. Always Search First
```powershell
# Before solving any problem
.\bin\kb.ps1 compound search "problem description"
```

### 2. Document Hard Problems
- Required 3+ attempts
- Non-obvious solution
- Likely to recur

### 3. Use YAML Frontmatter
- Enables automatic extraction
- Better Neo4j integration
- Searchable metadata

### 4. Regular Sync
```powershell
# Weekly sync
.\bin\kb.ps1 compound sync
```

### 5. Review Relationships
```powershell
# Check what's related
python tools/neo4j/query_skills_neo4j.py --skill "Your Skill"
```

## Advanced Features

### Custom Cypher Queries

Access Neo4j Browser:
1. Go to your AuraDB instance
2. Click "Open with Neo4j Browser"
3. Run custom queries

Example queries:
```cypher
// Find skill clusters
MATCH (s1:Skill)-[:RELATED_TO]-(s2:Skill)
RETURN s1, s2
LIMIT 50

// Find most valuable entries
MATCH (k:KBEntry)-[:TEACHES]->(s:Skill)
WITH k, count(s) as skill_count
ORDER BY skill_count DESC
LIMIT 10
RETURN k.title, skill_count

// Find technology dependencies
MATCH (t:Technology)-[:REQUIRES_SKILL]->(s:Skill)
RETURN t.name, collect(s.name) as required_skills
```

### Batch Operations

```powershell
# Sync specific category
python tools/neo4j/sync_skills_to_neo4j.py --kb-path .agent/knowledge-base/bugs

# Export graph data
# (Use Neo4j Browser export feature)
```

## Integration with Workflows

### `/cycle` Workflow
1. Search KB (compound search)
2. Implement solution
3. Document (compound add)
4. Auto-sync to Neo4j

### `/compound` Workflow
1. Document solution
2. Categorize
3. Sync to Neo4j
4. Verify relationships

### `/explore` Workflow
1. Query Neo4j for related patterns
2. Review learning paths
3. Document findings
4. Update knowledge graph

## Future Enhancements

### Planned Features
- [ ] Visual graph explorer
- [ ] AI-powered skill recommendations
- [ ] Automatic prerequisite detection
- [ ] Learning path generator
- [ ] Skill gap analysis
- [ ] Team expertise mapping

### Experimental
- [ ] Graph embeddings for similarity
- [ ] Predictive skill requirements
- [ ] Automated relationship discovery
- [ ] Cross-project knowledge sharing

## Summary

The Neo4j compound integration transforms the knowledge base from a simple file storage into an intelligent learning system:

✅ **File System** - Stores full content
✅ **Neo4j Brain** - Maps relationships
✅ **Compound Scripts** - Seamless integration
✅ **Automatic Sync** - No manual work
✅ **Smart Queries** - Contextual search
✅ **Learning Paths** - Skill progression
✅ **Pattern Discovery** - Hidden connections

**Philosophy:** Each unit of engineering work should make subsequent units easier. Neo4j is the brain that remembers and connects everything.

---

**Version:** 1.0.0
**Created:** 2026-01-02
**Status:** Active
**Integration:** File System + Neo4j + PowerShell Scripts

#neo4j #compound-learning #knowledge-graph #brain
