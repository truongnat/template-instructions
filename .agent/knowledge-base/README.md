# Knowledge Base - Project Memory

## Purpose
This knowledge base stores lessons learned, bug patterns, difficult features, and solutions that required multiple attempts. Use this as a reference when encountering similar issues in the future.

---

## 📁 Structure

```
knowledge-base/
├── README.md                    # This file
├── index.md                     # Searchable index of all entries
├── bugs/                        # Bug patterns and fixes
│   ├── critical/
│   ├── high/
│   ├── medium/
│   └── low/
├── features/                    # Complex feature implementations
│   ├── authentication/
│   ├── performance/
│   ├── integration/
│   └── ui-ux/
├── architecture/                # Architecture decisions and patterns
├── security/                    # Security issues and solutions
├── performance/                 # Performance optimizations
└── platform-specific/           # Platform-specific issues
    ├── web/
    ├── mobile/
    ├── desktop/
    ├── cli/
    └── embedded/
```

---

## 🔍 How to Use

### When to Create an Entry
Create a knowledge entry when:
- ✅ Bug required multiple attempts to fix (3+ attempts)
- ✅ Feature implementation was particularly challenging
- ✅ Solution was non-obvious or counter-intuitive
- ✅ Issue is likely to recur in similar projects
- ✅ Root cause analysis revealed important insights
- ✅ Performance issue required deep investigation
- ✅ Security vulnerability was discovered and fixed

### When to Search
Search the knowledge base when:
- 🔍 Encountering a new bug or error
- 🔍 Starting a complex feature implementation
- 🔍 Facing performance issues
- 🔍 Dealing with platform-specific problems
- 🔍 Making architecture decisions
- 🔍 Reviewing security concerns

### How to Search

**1. File-Based Search:**
- **By Category:** Browse folders by type (bugs, features, etc.)
- **By Severity:** Check critical/high priority entries first
- **By Keywords:** Search for error messages, technology names, component names
- **By Index:** Check `INDEX.md` for quick reference

**2. Neo4j Knowledge Graph:**
```bash
# Search all skills
python tools/neo4j/query_skills_neo4j.py --all-skills

# Find skills for specific technology
python tools/neo4j/query_skills_neo4j.py --tech "React"

# Find related skills
python tools/neo4j/query_skills_neo4j.py --skill "Authentication"

# Get learning path
python tools/neo4j/query_skills_neo4j.py --learning-path "Architecture"

# Search by keyword
python tools/neo4j/query_skills_neo4j.py --search "performance"
```

**3. Research Agent (Automated):**
```bash
# Automatically searches both file system and Neo4j
python tools/research/research_agent.py --task "authentication" --type feature
```

**See [Neo4j Tools Documentation](../../tools/neo4j/README.md) for complete guide.**

---

## 📝 Creating an Entry

### Step 1: Use the Template
Copy `.agent/templates/Knowledge-Entry-Template.md`

### Step 2: Fill in Details
- Provide clear problem description
- Include code snippets
- Document root cause
- Explain solution step-by-step
- Add prevention measures
- **Use YAML frontmatter** for metadata (required for Neo4j sync)

### Step 3: Choose Location
Place entry in appropriate folder:
- **Bugs:** `knowledge-base/bugs/[severity]/KB-[date]-[id].md`
- **Features:** `knowledge-base/features/[category]/KB-[date]-[id].md`
- **Architecture:** `knowledge-base/architecture/KB-[date]-[id].md`
- **Security:** `knowledge-base/security/KB-[date]-[id].md`
- **Performance:** `knowledge-base/performance/KB-[date]-[id].md`
- **Platform:** `knowledge-base/platform-specific/[platform]/KB-[date]-[id].md`

### Step 4: Sync to Neo4j
```bash
# Sync your new entry to Neo4j knowledge graph
python tools/neo4j/sync_skills_to_neo4j.py

# Verify it was synced
python tools/neo4j/query_skills_neo4j.py --all-skills
```

### Step 5: Update Index
Add entry to `INDEX.md` with:
- ID, Title, Category, Tags, Date

**Note:** Neo4j sync automatically extracts skills, technologies, and relationships from your entry.

---

## 🏷️ Tagging System

### Category Tags
- `#bug-pattern` - Recurring bug patterns
- `#feature-solution` - Complex feature implementations
- `#performance` - Performance optimizations
- `#security` - Security issues
- `#architecture` - Architecture decisions
- `#integration` - Third-party integrations
- `#platform-specific` - Platform-specific issues

### Technology Tags
- `#react`, `#nodejs`, `#python`, `#flutter`, etc.
- `#postgresql`, `#mongodb`, `#redis`, etc.
- `#aws`, `#docker`, `#kubernetes`, etc.

### Severity Tags
- `#critical` - System breaking, data loss
- `#high` - Major functionality affected
- `#medium` - Moderate impact
- `#low` - Minor issues

---

## 📊 Entry Naming Convention

**Format:** `KB-[YYYY-MM-DD]-[###]-[short-title].md`

**Examples:**
- `KB-2025-12-29-001-react-hydration-error.md`
- `KB-2025-12-29-002-oauth-token-refresh.md`
- `KB-2025-12-29-003-mobile-memory-leak.md`

---

## 🔄 Maintenance

### Regular Reviews
- **Monthly:** Review and update entries
- **Quarterly:** Archive outdated entries
- **Yearly:** Consolidate similar entries

### Quality Standards
- ✅ Clear problem description
- ✅ Reproducible steps
- ✅ Working solution
- ✅ Prevention measures
- ✅ Proper tagging

### Archiving
Move outdated entries to `knowledge-base/archive/[year]/`

---

## 📈 Metrics to Track

Track these metrics in `index.md`:
- Total entries by category
- Most referenced entries
- Average resolution time
- Recurrence rate

---

## 🎯 Best Practices

### Writing Entries
1. **Be Specific:** Include exact error messages, versions, configurations
2. **Be Complete:** Document all attempts, not just the final solution
3. **Be Searchable:** Use clear keywords and tags
4. **Be Visual:** Include screenshots, diagrams, code snippets
5. **Be Preventive:** Focus on how to avoid the issue

### Using Entries
1. **Search First:** Always check knowledge base before starting
2. **Adapt Solutions:** Don't copy-paste blindly, understand the context
3. **Update Entries:** Add notes if you find better solutions
4. **Cross-Reference:** Link related entries together

---

## 🤝 Contributing

### Who Can Add Entries
- @DEV - Bug fixes, feature implementations
- @DEVOPS - Infrastructure, deployment issues
- @TESTER - Test patterns, edge cases
- @SECA - Security vulnerabilities
- @SA - Architecture decisions
- @UIUX - UI/UX patterns

### Review Process
1. Create entry using template
2. Tag @REPORTER for review
3. @REPORTER verifies completeness
4. Entry added to index
5. Team notified

---

## 📞 Questions?

If unsure about:
- **What to document:** Ask @PM or @REPORTER
- **Where to place entry:** Check this README or ask @REPORTER
- **How to search:** Use index.md or ask @REPORTER

---

#knowledge-base #documentation #lessons-learned
