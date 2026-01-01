---
role: Research Agent
activation: @RESEARCH, /research, "research", "explore", "find similar"
priority: CRITICAL - Run BEFORE any planning/development/bug fixing
---

# Research Agent Workflow

## Purpose
**ALWAYS research before starting ANY task** to find existing knowledge, similar solutions, and avoid reinventing the wheel.

## When to Activate

### Automatic Triggers (MUST run before):
1. **Before Planning** (@PM starts) → Research similar projects
2. **Before Development** (@DEV starts) → Research similar features
3. **Before Bug Fixing** (@TESTER finds bug) → Research similar bugs
4. **Before Architecture** (@SA designs) → Research similar architectures
5. **Before Security Review** (@SECA reviews) → Research similar vulnerabilities

### Manual Activation:
- User types: `/research <task>`
- User mentions: "research", "explore", "find similar", "check knowledge base"
- Any role tags: @RESEARCH

## Research Process

### Step 1: Understand the Task
```markdown
**Task:** [Clear description]
**Type:** [general|bug|feature|architecture|security|performance]
**Keywords:** [Extract key terms]
```

### Step 2: Run Research Agent

```bash
# For general tasks
python tools/research/research_agent.py --task "Build authentication system"

# For bugs
python tools/research/research_agent.py --bug "Login fails with OAuth"

# For features
python tools/research/research_agent.py --feature "Real-time notifications"

# With specific type
python tools/research/research_agent.py --task "API design" --type architecture
```

### Step 3: Analyze Results

The agent will search:
1. **Knowledge Base** (File System)
   - `.agent/knowledge-base/bugs/`
   - `.agent/knowledge-base/features/`
   - `.agent/knowledge-base/architecture/`
   - `.agent/knowledge-base/security/`
   - `.agent/knowledge-base/performance/`

2. **Neo4j Knowledge Graph** (if configured)
   - Related knowledge entries
   - Technology patterns
   - Similar tasks
   - Solution patterns

3. **GitHub Issues** (if configured)
   - Related issues
   - Pull requests
   - Discussions

4. **MCP Tools** (if available)
   - Web search for best practices
   - Documentation lookup
   - Stack Overflow search

### Step 4: Review Research Report

Agent generates:
- `docs/research-reports/research-YYYYMMDD-HHMMSS.json` (detailed)
- `docs/research-reports/research-YYYYMMDD-HHMMSS.md` (summary)

**Report Structure:**
```markdown
# Research Report

**Task:** [Task description]
**Confidence:** [high|medium|low]
**Related Entries:** [count]

## Findings
- Found X entries in Knowledge Base
- Found Y entries in Neo4j
- Found Z GitHub issues
- Related technologies: [list]

## Recommendations
- ✓ Strong knowledge available - Review before starting
- ⚠️  Some knowledge available - Consider similar approaches
- ⚠️  Limited knowledge - Document thoroughly

## Detailed Results
[Links to relevant entries]
```

### Step 5: Make Decision

Based on confidence level:

#### High Confidence (5+ related entries)
```markdown
✓ **Strong knowledge available**

Action:
1. Review top 3-5 related entries
2. Extract successful patterns
3. Avoid known pitfalls
4. Reuse proven solutions
5. Update existing knowledge if needed

Proceed with: Informed implementation
```

#### Medium Confidence (2-4 related entries)
```markdown
⚠️  **Some knowledge available**

Action:
1. Review available entries
2. Identify gaps in knowledge
3. Consider similar approaches
4. Plan to document new learnings

Proceed with: Cautious implementation
```

#### Low Confidence (0-1 related entries)
```markdown
⚠️  **Limited knowledge - New territory**

Action:
1. This is likely a new challenge
2. Plan extra time for exploration
3. Document thoroughly for future
4. Consider prototyping first
5. Create detailed knowledge entry after

Proceed with: Exploratory implementation
```

## Integration with Roles

### @PM (Project Manager)
```markdown
## Before Creating Project Plan

1. Run research:
   python tools/research/research_agent.py --task "[project description]"

2. Review findings:
   - Similar projects in KB
   - Common challenges
   - Estimated complexity

3. Incorporate into plan:
   - Reference related KB entries
   - Adjust timeline based on knowledge
   - Plan for knowledge gaps
```

### @DEV (Developer)
```markdown
## Before Implementation

1. Run research:
   python tools/research/research_agent.py --feature "[feature description]"

2. Review findings:
   - Similar implementations
   - Code patterns
   - Known issues

3. Implementation strategy:
   - Reuse proven patterns
   - Avoid known pitfalls
   - Document new approaches
```

### @TESTER (Tester)
```markdown
## Before Bug Fixing

1. Run research:
   python tools/research/research_agent.py --bug "[bug description]"

2. Review findings:
   - Similar bugs
   - Root causes
   - Solutions

3. Fix strategy:
   - Apply known solutions
   - Verify root cause
   - Update KB if new pattern
```

### @SA (System Analyst)
```markdown
## Before Architecture Design

1. Run research:
   python tools/research/research_agent.py --task "[architecture need]" --type architecture

2. Review findings:
   - Similar architectures
   - Design patterns
   - Technology choices

3. Design strategy:
   - Leverage proven patterns
   - Learn from past decisions
   - Document new patterns
```

## MCP Integration

### Using MCP Tools for Research

```javascript
// Example: Search web for best practices
{
  "tool": "web_search",
  "query": "authentication best practices 2026"
}

// Example: Fetch documentation
{
  "tool": "fetch",
  "url": "https://docs.example.com/auth"
}

// Example: Query GitHub
{
  "tool": "github_search",
  "query": "authentication implementation",
  "repo": "user/repo"
}
```

### Research Agent with MCP

The research agent can be extended to use MCP tools:

```python
# In research_agent.py
def _search_web(self, task: str) -> Dict:
    """Search web using MCP"""
    # Call MCP web search tool
    pass

def _fetch_docs(self, url: str) -> Dict:
    """Fetch documentation using MCP"""
    # Call MCP fetch tool
    pass
```

## Output Format

### Console Output
```
============================================================
🔍 RESEARCH AGENT - Starting Research
============================================================
Task: Build authentication system
Type: feature
Time: 2026-01-01 10:00:00
============================================================

📚 Searching Knowledge Base...
  ✓ Found 3 entries
    • OAuth Implementation Guide
      File: .agent/knowledge-base/features/authentication/KB-2025-12-15-001.md
      Relevance: 80%
    • JWT Token Management
      File: .agent/knowledge-base/features/authentication/KB-2025-12-20-002.md
      Relevance: 60%

🧠 Querying Neo4j Knowledge Graph...
  ✓ Found 5 entries
    • OAuth2 Flow Implementation
      ID: KB-2025-12-15-001
      Category: feature
      Technologies: Node.js, Passport.js, JWT

  Related Technologies:
    • Passport.js (used 5x)
    • JWT (used 8x)
    • OAuth2 (used 3x)

🐙 Searching GitHub Issues...
  ✓ Found 2 issues
    • #123: Implement OAuth authentication
      State: closed
      URL: https://github.com/user/repo/issues/123

============================================================
📊 RESEARCH SUMMARY
============================================================
Confidence Level: HIGH
Related Entries: 8

Findings:
  • Found 3 related entries in Knowledge Base
  • Found 5 related entries in Neo4j
  • Related technologies: Passport.js, JWT, OAuth2
  • Found 2 related GitHub issues

Recommendations:
  ✓ Strong knowledge base available - Review existing solutions before starting
============================================================

💾 Research report saved: docs/research-reports/research-20260101-100000.json
```

### Markdown Report
```markdown
# Research Report

**Task:** Build authentication system
**Type:** feature
**Date:** 2026-01-01T10:00:00

## Summary

- **Confidence:** high
- **Related Entries:** 8

### Findings

- Found 3 related entries in Knowledge Base
- Found 5 related entries in Neo4j
- Related technologies: Passport.js, JWT, OAuth2
- Found 2 related GitHub issues

### Recommendations

- ✓ Strong knowledge base available - Review existing solutions before starting

## Detailed Results

### Knowledge Base (3 entries)

#### OAuth Implementation Guide
- File: `.agent/knowledge-base/features/authentication/KB-2025-12-15-001.md`
- Category: features/authentication
- Relevance: 80%

[... more entries ...]
```

## Best Practices

### 1. Always Research First
```markdown
❌ BAD: Start coding immediately
✓ GOOD: Research → Review → Plan → Code
```

### 2. Document New Findings
```markdown
If confidence is LOW:
→ This is new territory
→ Document thoroughly
→ Create KB entry after completion
```

### 3. Update Existing Knowledge
```markdown
If you find better solution:
→ Update existing KB entry
→ Add "Updated" section
→ Link to new implementation
```

### 4. Cross-Reference
```markdown
In your artifacts, reference research:

## Research Findings
- Reviewed KB-2025-12-15-001: OAuth Implementation
- Applied pattern from KB-2025-12-20-002: JWT Management
- Avoided issue from GitHub #123
```

## Troubleshooting

### Neo4j Not Available
```bash
⚠️  Neo4j driver not installed. Run: pip install neo4j
⚠️  Neo4j credentials not found in .env
```

**Solution:** Install driver or use file-based KB only

### GitHub API Rate Limit
```bash
⚠️  GitHub API error: Rate limit exceeded
```

**Solution:** Wait or use authenticated token

### No Results Found
```bash
✗ No entries found
```

**Action:** This is new territory - document thoroughly!

## Next Steps

After research:
1. **High Confidence** → Proceed with implementation, reference KB entries
2. **Medium Confidence** → Proceed cautiously, plan to document
3. **Low Confidence** → Plan extra time, prototype first, document thoroughly

**Always tag next role:**
```markdown
### Research Complete
- Confidence: [level]
- Related entries: [count]
- Recommendations: [list]

@PM - Ready for planning with research insights
@DEV - Ready for implementation with patterns
@TESTER - Ready for bug fixing with known solutions
```

---

#research #knowledge-base #exploration #best-practices
