---
description: Support - Documentation Creation Workflow
---

# /docs - Documentation Workflow

## ⚠️ PURPOSE
Systematic approach to creating and maintaining project documentation.

// turbo-all

## When to Use

- Creating new documentation
- Updating existing docs
- Writing KB entries
- API documentation
- User guides

## Types of Documentation

| Type | Template | Location |
|------|----------|----------|
| API Docs | Inline/OpenAPI | `docs/api/` |
| User Guide | `User-Guide-Template.md` | `docs/guides/` |
| Architecture | `Architecture-Spec-Template.md` | `docs/architecture/` |
| Sprint Report | `Sprint-Review-Template.md` | `docs/sprints/sprint-[N]/` |

## Workflow Steps

### 1. Identify Doc Type
- What are you documenting?
- Who is the audience?
- What template should you use?

### 2. Check Existing Docs
```bash
# Search for related docs
find docs -name "*.md" | xargs grep -l "[topic]"

# Check KB for similar entries
agentic-sdlc kb search "[topic]"
```

### 3. Choose Template
```bash
# List available templates
ls .agent/templates/

# Copy template
cp .agent/templates/[Template].md docs/[appropriate-folder]/[new-doc].md
```

### 4. Write Content

**Structure Guidelines:**
- Start with clear heading
- Add overview/purpose section
- Use code blocks for commands
- Include examples
- Add cross-references

**Style Guidelines:**
- Use active voice
- Keep sentences short
- Use bullet points/tables
- Include visuals when helpful

### 5. Add Metadata (for KB entries)
```yaml
---
category: feature|bug|architecture|security|performance
tags: [relevant, tags]
date: YYYY-MM-DD
author: @ROLE
---
```

### 6. Review & Validate
- [ ] Spelling/grammar check
- [ ] Links work
- [ ] Code examples are correct
- [ ] Follows project conventions

```bash
# Check for broken links
find docs -name "*.md" -exec grep -l "\[.*\](.*)" {} \;
```

### 7. Update Indexes
```bash
# Update KB index
agentic-sdlc kb update-index

# Sync to Neo4j
agentic-sdlc kb compound sync
```

## Documentation Standards

### Naming Convention
```
[Type]-[Topic]-[Sprint]-v[Version].md
Example: Architecture-Auth-Sprint-6-v1.md
```

### Required Sections

**For KB Entries:**
- Problem/Challenge
- Solution
- Implementation
- Learnings

**For User Guides:**
- Overview
- Prerequisites
- Steps
- Troubleshooting

**For API Docs:**
- Endpoint
- Parameters
- Response
- Examples

## Integration

- **@PM** - Project documentation
- **@SA** - Architecture docs
- **@DEV** - Code documentation
- **@REPORTER** - Reports and summaries
- **/release** - Changelog updates

#docs #documentation #writing 

## ⏭️ Next Steps
- **If Docs Created:** Trigger `/review` for feedback
- **If Index Updated:** Trigger `/housekeeping` to verify health

---

## ENFORCEMENT REMINDER
Update KB index after adding new entries.
