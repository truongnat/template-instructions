# Neo4j Skills Auto-Sync Scripts

Automatically sync knowledge base entries to Neo4j Cloud (AuraDB) and create a knowledge graph of skills, technologies, and relationships.

## Prerequisites

```bash
pip install neo4j python-dotenv
```

## Configuration

Your `.env` file already contains the Neo4j connection details:
```
NEO4J_URI=neo4j+s://5994f6db.databases.neo4j.io
NEO4J_USERNAME=neo4j
NEO4J_PASSWORD=mmWKltHRIEaEM8PSDNdve9z3lwc8_frsLRMVjvh2NMY
NEO4J_DATABASE=neo4j
```

## Scripts

### 1. sync_skills_to_neo4j.py

Automatically syncs knowledge base entries to Neo4j, creating nodes and relationships.

**Usage:**
```bash
# Sync all KB entries
python tools/neo4j/sync_skills_to_neo4j.py

# Dry run (preview without syncing)
python tools/neo4j/sync_skills_to_neo4j.py --dry-run

# Show statistics only
python tools/neo4j/sync_skills_to_neo4j.py --stats-only

# Custom KB path
python tools/neo4j/sync_skills_to_neo4j.py --kb-path .agent/knowledge-base
```

**What it creates:**
- `KBEntry` nodes (knowledge base entries)
- `Skill` nodes (extracted skills)
- `Technology` nodes (technologies mentioned)
- `Category` nodes (entry categories)
- `Person` nodes (authors)
- Relationships between all nodes

**Graph Structure:**
```
(Person)-[:CREATED]->(KBEntry)-[:TEACHES]->(Skill)
(KBEntry)-[:BELONGS_TO]->(Category)
(KBEntry)-[:USES_TECHNOLOGY]->(Technology)
(Technology)-[:REQUIRES_SKILL]->(Skill)
(Skill)-[:RELATED_TO]-(Skill)
```

---

### 2. query_skills_neo4j.py

Query and explore the skills knowledge graph.

**Usage:**

```bash
# List all skills
python tools/neo4j/query_skills_neo4j.py --all-skills

# Skills for specific technology
python tools/neo4j/query_skills_neo4j.py --tech "Neo4j"
python tools/neo4j/query_skills_neo4j.py --tech "Figma"

# Related skills
python tools/neo4j/query_skills_neo4j.py --skill "User Research"

# Learning path for category
python tools/neo4j/query_skills_neo4j.py --learning-path "UI/UX Design"

# List all technologies
python tools/neo4j/query_skills_neo4j.py --technologies

# Search skills
python tools/neo4j/query_skills_neo4j.py --search "design"

# Skills by author
python tools/neo4j/query_skills_neo4j.py --author "@UIUX"

# Prerequisites for a skill
python tools/neo4j/query_skills_neo4j.py --prerequisites "Advanced Prototyping"
```

---

## Workflow: Auto-Update After Learning

### Step 1: Learn New Skills
When you add new knowledge base entries:
```bash
# New KB entry created at:
.agent/knowledge-base/features/KB-2026-01-01-005-new-skill.md
```

### Step 2: Auto-Sync to Neo4j
```bash
# Sync new entries
python tools/neo4j/sync_skills_to_neo4j.py
```

### Step 3: Query Your Skills
```bash
# See all your skills
python tools/neo4j/query_skills_neo4j.py --all-skills

# Find related skills
python tools/neo4j/query_skills_neo4j.py --skill "Your New Skill"
```

---

## Example Queries in Neo4j Browser

Access your Neo4j Browser at: https://workspace-preview.neo4j.io/workspace/query

### View All Skills
```cypher
MATCH (s:Skill)<-[:TEACHES]-(k:KBEntry)
RETURN s, k
LIMIT 50
```

### Skills by Technology
```cypher
MATCH (t:Technology {name: "Neo4j"})<-[:USES_TECHNOLOGY]-(k:KBEntry)-[:TEACHES]->(s:Skill)
RETURN t, k, s
```

### Learning Path
```cypher
MATCH path = (p:Person)-[:CREATED]->(k:KBEntry)-[:TEACHES]->(s:Skill)
WHERE p.name = "@UIUX"
RETURN path
```

### Skill Relationships
```cypher
MATCH (s1:Skill)-[r:RELATED_TO]-(s2:Skill)
WHERE r.strength > 2
RETURN s1, r, s2
```

### Technology Stack
```cypher
MATCH (t:Technology)<-[:USES_TECHNOLOGY]-(k:KBEntry)
RETURN t.name as technology, count(k) as usage_count
ORDER BY usage_count DESC
```

### Find Skill Prerequisites
```cypher
MATCH (s1:Skill {name: "Advanced UI Design"})<-[:TEACHES]-(k:KBEntry)-[:TEACHES]->(s2:Skill)
WHERE s2.level = 'beginner'
RETURN DISTINCT s2.name as prerequisite
```

---

## Automation with Hooks

Create a Kiro hook to auto-sync after KB updates:

**Hook Configuration:**
```json
{
  "name": "kb-auto-sync-neo4j",
  "trigger": "on_file_save",
  "condition": "file_path contains '.agent/knowledge-base/KB-'",
  "action": {
    "type": "command",
    "command": "python tools/neo4j/sync_skills_to_neo4j.py"
  }
}
```

---

## Graph Schema

### Nodes

**KBEntry**
- `id`: Unique identifier (KB-YYYY-MM-DD-NNN)
- `title`: Entry title
- `date`: Creation date
- `category`: Category name
- `author`: Author name
- `file_path`: File location
- `content_length`: Content size
- `updated_at`: Last update timestamp

**Skill**
- `name`: Skill name
- `level`: beginner | intermediate | advanced
- `source`: header | bullet | content

**Technology**
- `name`: Technology name

**Category**
- `name`: Category name

**Person**
- `name`: Author name (e.g., @UIUX)

### Relationships

- `(Person)-[:CREATED]->(KBEntry)` - Author created entry
- `(KBEntry)-[:BELONGS_TO]->(Category)` - Entry belongs to category
- `(KBEntry)-[:TEACHES]->(Skill)` - Entry teaches skill
- `(KBEntry)-[:USES_TECHNOLOGY]->(Technology)` - Entry uses technology
- `(Technology)-[:REQUIRES_SKILL]->(Skill)` - Technology requires skill
- `(Skill)-[:RELATED_TO]-(Skill)` - Skills are related (with strength property)

---

## Troubleshooting

### Connection Issues
```bash
# Test connection
python -c "from neo4j import GraphDatabase; driver = GraphDatabase.driver('neo4j+s://5994f6db.databases.neo4j.io', auth=('neo4j', 'your-password')); driver.verify_connectivity(); print('✅ Connected')"
```

### Clear All Data (Reset)
```cypher
// In Neo4j Browser
MATCH (n) DETACH DELETE n
```

### View Constraints
```cypher
SHOW CONSTRAINTS
```

### View Indexes
```cypher
SHOW INDEXES
```

---

## Benefits of Skills in Neo4j

1. **Skill Discovery**: Find related skills you should learn
2. **Learning Paths**: See progression from beginner to advanced
3. **Technology Mapping**: Understand which skills are needed for technologies
4. **Knowledge Gaps**: Identify missing skills in your knowledge base
5. **Team Expertise**: Track who knows what
6. **Skill Relationships**: Discover connections between skills
7. **Query Flexibility**: Ask complex questions about your knowledge

---

## Next Steps

1. **Run initial sync**: `python tools/neo4j/sync_skills_to_neo4j.py`
2. **Explore your skills**: `python tools/neo4j/query_skills_neo4j.py --all-skills`
3. **Set up auto-sync hook** (optional)
4. **Query in Neo4j Browser** for visual exploration
5. **Add more KB entries** and watch your knowledge graph grow!

---

## Example Output

```bash
$ python tools/neo4j/sync_skills_to_neo4j.py

✅ Connected to Neo4j Cloud: neo4j+s://5994f6db.databases.neo4j.io
🔧 Setting up database schema...
✅ Created constraint: (s:Skill)
✅ Created constraint: (k:KBEntry)
✅ Created index: (s:Skill)
✅ Created index: (k:KBEntry)

📚 Found 4 knowledge base entries

✅ Synced: React Hydration Mismatch in Astro
✅ Synced: Landing Page Design Trends 2026
✅ Synced: Neo4j Graph Database Skills
✅ Synced: Essential UI/UX Design Skills 2026

🔗 Creating skill relationships...
✅ Created skill relationships

📊 Final Statistics:
   KB Entries: 4
   Skills: 127
   Technologies: 23
   Categories: 3

✅ Successfully synced 4 KB entries!
```

---

#neo4j #knowledge-graph #skills #automation #learning
