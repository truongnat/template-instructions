---
inclusion: manual
keywords: update documentation, update docs, refresh documentation, update paths, update references
---

# Documentation Updates Steering Guide

When the user asks to update documentation, follow this comprehensive guide to ensure all references are updated consistently.

## When to Use This Guide

Activate when user mentions:
- "update documentation"
- "update docs"
- "refresh documentation"
- "update paths"
- "update references"
- "update all to [topic]"
- "standardize documentation"

---

## Documentation Update Checklist

### Phase 1: Identify Scope

**Questions to Ask:**
1. What topic/component needs updating? (e.g., Neo4j, Research Agent, etc.)
2. What changed? (paths, structure, naming, features)
3. Which files are affected?
4. Are there cross-references to update?

### Phase 2: Search for References

**Use grep search to find all references:**
```bash
# Search for topic references
grepSearch --query "topic-name|TopicName|TOPIC_NAME" --includePattern "**/*.md"

# Search for old paths
grepSearch --query "old/path" --includePattern "**/*.md"

# Search for specific commands
grepSearch --query "old-command" --includePattern "**/*.md"
```

**Key locations to check:**
- `README.md` - Main project documentation
- `docs/` - All documentation files
- `.agent/knowledge-base/` - Knowledge base entries
- `.agent/workflows/` - Workflow files
- `.agent/rules/` - Rule files
- `.kiro/steering/` - Steering files
- `tools/*/README.md` - Tool documentation

### Phase 3: Update Documentation Files

**Priority Order:**

1. **Tool Documentation** (`tools/[tool]/README.md`)
   - Update command paths
   - Update usage examples
   - Update configuration examples
   - Update integration instructions

2. **Knowledge Base Entries** (`.agent/knowledge-base/`)
   - Update related documentation links
   - Add integration sections
   - Update command examples
   - Add workflow documentation

3. **Main Documentation** (`docs/`)
   - Update guides
   - Update setup instructions
   - Update architecture docs
   - Update sprint documentation

4. **Project Documentation** (Root level)
   - Update README.md
   - Update PROJECT-STRUCTURE.md
   - Update documentation indexes

5. **Workflow Files** (`.agent/workflows/`)
   - Update command references
   - Update file paths
   - Update integration steps

6. **Steering Files** (`.kiro/steering/`)
   - Update relevant steering guides
   - Add new steering if needed

### Phase 4: Update Cross-References

**Common cross-reference patterns:**

**In Knowledge Base Entries:**
```markdown
## Related Knowledge Base Entries
- See: `.agent/knowledge-base/[category]/` for related entries
- See: `tools/[tool]/README.md` for tool documentation
- See: `docs/[section]/[FILE].md` for detailed guide
- See: `docs/sprints/SPRINT-[TOPIC].md` for sprint details

## Integration with Agentic SDLC

### Tool Location
**Location:** `tools/[tool]/[script].py`

### Usage Examples
```bash
python tools/[tool]/[script].py --option value
```

### Configuration
**Location:** `.env` or `.kiro/settings/[config].json`

### Related Documentation
- **Tool Documentation:** `tools/[tool]/README.md`
- **Architecture:** `docs/architecture/[TOPIC].md`
- **Setup Guide:** `docs/setup/[TOPIC]-SETUP.md`
```

**In Tool Documentation:**
```markdown
## Integration

See also:
- [Knowledge Base Entry](.agent/knowledge-base/[category]/KB-YYYY-MM-DD-NNN-[topic].md)
- [Architecture Documentation](docs/architecture/[TOPIC].md)
- [Setup Guide](docs/setup/[TOPIC]-SETUP.md)
```

**In Main Documentation:**
```markdown
## Related Documentation
- **[Topic] Tools:** `tools/[topic]/README.md`
- **[Topic] KB Entry:** `.agent/knowledge-base/[category]/KB-[ID]-[topic].md`
- **[Topic] Architecture:** `docs/architecture/[TOPIC].md`
```

### Phase 5: Update Command Examples

**Ensure all commands use new paths:**

**Old Pattern:**
```bash
python bin/script.py
```

**New Pattern:**
```bash
python tools/[category]/script.py
```

**Update in:**
- README files
- Knowledge base entries
- Setup guides
- Workflow files
- Hook configurations

### Phase 6: Update Hook Configurations

**If hooks reference the updated component:**

**Location:** `.kiro/hooks/[hook-name].json`

**Update:**
```json
{
  "action": {
    "type": "command",
    "command": "python tools/[category]/[script].py"
  }
}
```

### Phase 7: Sync to Neo4j

**Automatically sync all changes to Neo4j Knowledge Graph:**

```bash
# Sync all KB entries and documentation to Neo4j
python tools/neo4j/sync_skills_to_neo4j.py

# Verify sync
python tools/neo4j/query_skills_neo4j.py --all-skills
```

**What gets synced:**
- All updated KB entries
- Documentation relationships
- Cross-references between files
- Tool locations and usage patterns
- Integration points

**No need to create summary documents** - Neo4j graph serves as the living documentation index.

---

## Documentation Standards

### File Naming Conventions

**Documentation Files:** `UPPERCASE-WITH-HYPHENS.md`
- Examples: `README.md`, `QUICK-START.md`, `NEO4J-UPDATE-COMPLETE.md`

**Code Files:** `lowercase_with_underscores.py`
- Examples: `research_agent.py`, `sync_skills_to_neo4j.py`

**Config Files:** `lowercase-with-hyphens.json`
- Examples: `auto-research-hook.json`, `mcp.json`

**Workflow Files:** `lowercase.md` or `lowercase-with-hyphens.md`
- Examples: `pm.md`, `auto-learning-workflow.md`

**Steering Files:** `lowercase-with-hyphens.md`
- Examples: `global-rules.md`, `documentation-updates.md`

### Path References

**Always use relative paths from project root:**
```markdown
✅ GOOD: `tools/research/research_agent.py`
✅ GOOD: `.agent/knowledge-base/architecture/`
✅ GOOD: `docs/setup/RESEARCH-AGENT-SETUP.md`

❌ BAD: `/absolute/path/to/file`
❌ BAD: `../../../relative/path`
```

### Command Examples

**Always show full path:**
```bash
✅ GOOD: python tools/research/research_agent.py --task "..." --type feature
✅ GOOD: bash tools/setup/setup_research_hooks.sh

❌ BAD: python research_agent.py
❌ BAD: ./setup_hooks.sh
```

### Cross-References

**Use descriptive link text:**
```markdown
✅ GOOD: See [Research Agent Setup](docs/setup/RESEARCH-AGENT-SETUP.md)
✅ GOOD: See [Neo4j Tools Documentation](tools/neo4j/README.md)

❌ BAD: See [here](docs/setup/RESEARCH-AGENT-SETUP.md)
❌ BAD: Click [this link](tools/neo4j/README.md)
```

---

## Common Update Scenarios

### Scenario 1: Tool Reorganization

**When:** Files moved from `bin/` to `tools/[category]/`

**Update:**
1. Tool README (`tools/[category]/README.md`)
2. Knowledge base entries referencing the tool
3. Main README.md
4. Setup guides
5. Workflow files
6. Hook configurations
7. Documentation index

### Scenario 2: File Naming Standardization

**When:** Files renamed to follow conventions

**Update:**
1. All references to old filename
2. Import statements in code
3. Documentation links
4. Cross-references
5. Index files

### Scenario 3: New Feature Addition

**When:** New feature or component added

**Create:**
1. Tool documentation (`tools/[tool]/README.md`)
2. Knowledge base entry (`.agent/knowledge-base/[category]/KB-[ID]-[topic].md`)
3. Setup guide (`docs/setup/[TOPIC]-SETUP.md`)
4. Update main README.md
5. Update documentation index
6. Add to relevant workflows

### Scenario 4: Integration Documentation

**When:** Documenting how components integrate

**Add to Knowledge Base Entry:**
```markdown
## Integration with Agentic SDLC

### [Component] Integration
**Location:** `tools/[component]/[script].py`

**Usage:**
```bash
python tools/[component]/[script].py
```

### Automated Workflow
**Hook Configuration:** `.kiro/hooks/[hook].json`

### Related Tools
- **[Tool 1]:** `tools/[tool1]/README.md`
- **[Tool 2]:** `tools/[tool2]/README.md`
```

---

## Verification Steps

### 1. Test All Commands
```bash
# Test each updated command
python tools/[category]/[script].py --help

# Verify paths exist
ls -la tools/[category]/
```

### 2. Check All Links
- Open each documentation file
- Verify all internal links work
- Check external references

### 3. Verify Cross-References
- Ensure bidirectional links
- Check knowledge base references
- Verify tool documentation links

### 4. Review Documentation Index
- Ensure all files listed
- Verify paths are correct
- Check categorization

### 5. Test Integration
- Run integration workflows
- Test hook configurations
- Verify automated processes

---

## Example: Complete Update Process

### User Request: "update all to neo4j"

**Step 1: Search for References**
```bash
grepSearch --query "neo4j|Neo4j|NEO4J" --includePattern "**/*.md"
```

**Step 2: Identify Files to Update**
- `tools/neo4j/README.md`
- `.agent/knowledge-base/architecture/KB-2026-01-01-003-neo4j-graph-database-skills.md`
- `tools/research/README.md`
- `docs/PROJECT-DOCUMENTATION-INDEX.md`
- Any workflow files referencing Neo4j

**Step 3: Update Each File**
- Update command paths
- Add integration sections
- Update cross-references
- Add workflow documentation

**Step 4: Sync to Neo4j**
- Run `python tools/neo4j/sync_skills_to_neo4j.py`
- Verify with `python tools/neo4j/query_skills_neo4j.py --all-skills`

**Step 5: Verify**
- Test all commands
- Check all links
- Verify integration
- Update documentation index

---

## Best Practices

### DO ✅
- Search comprehensively for all references
- Update all related documentation
- Maintain consistent formatting
- Use relative paths
- Provide complete examples
- **Sync to Neo4j immediately after updates**
- Verify all changes

### DON'T ❌
- Skip cross-references
- Leave broken links
- Use absolute paths
- Forget to sync to Neo4j
- Skip verification
- Leave incomplete examples
- **Create unnecessary summary documents**

---

## Documentation Maintenance

### Regular Updates
- After file reorganization
- After feature additions
- After path changes
- After naming standardization
- After integration changes

### Quarterly Review
- Check for broken links
- Verify all paths
- Update outdated examples
- Refresh screenshots
- Update version numbers

### On Major Changes
- Create update summary document
- Update all affected documentation
- Notify team of changes
- Update documentation index
- Create migration guide if needed

---

## Related Steering Files
- `global-rules.md` - Global documentation rules
- `knowledge-base.md` - Knowledge base management
- `git-workflow.md` - Git commit conventions

---

#documentation #updates #maintenance #standards #best-practices
