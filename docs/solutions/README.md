# Solutions Directory

This folder stores solutions discovered by any role during task execution. These solutions are synced to Neo4j for future research and learning.

## Purpose

When @SA, @DEV, or any role finds a solution to a problem, save it here for:
- Future reference
- Research agent queries
- Self-learning engine
- Knowledge sharing across sessions

## What Goes Here

| Solution Type | Description | Example |
|---------------|-------------|---------|
| **Architecture** | Design decisions, patterns chosen | `auth-jwt-refresh-pattern.md` |
| **Implementation** | How a feature was implemented | `file-upload-chunking.md` |
| **Bug Fix** | Root cause and fix approach | `memory-leak-react-hooks.md` |
| **Integration** | Third-party integrations | `stripe-webhook-handling.md` |
| **Performance** | Optimization techniques | `database-query-indexing.md` |
| **Security** | Security implementations | `csrf-protection-setup.md` |

## Naming Convention

```
[category]-[topic]-[specifics].md

Examples:
- auth-oauth-google-login.md
- api-rate-limiting-implementation.md
- db-postgres-jsonb-indexing.md
```

## Template

```markdown
---
category: [architecture|implementation|bugfix|integration|performance|security]
role: [@SA|@DEV|@TESTER|@SECA|@DEVOPS]
date: YYYY-MM-DD
sprint: sprint-N
tags: [tag1, tag2, tag3]
---

# [Solution Title]

## Problem/Challenge
[What problem did you face?]

## Context
- **Component:** [component name]
- **Technology:** [tech stack]
- **Related Issues:** [links]

## Solution
[How did you solve it?]

## Implementation
\`\`\`[language]
[code snippets]
\`\`\`

## Why This Approach?
[Reasoning behind the choice]

## Alternatives Considered
1. [Alternative 1] - Why not chosen
2. [Alternative 2] - Why not chosen

## Learnings
- [Key takeaway 1]
- [Key takeaway 2]

## Related Solutions
- [link to related solution]
```

## Sync to Neo4j

After adding solutions:

```bash
sdlc-kit kb compound sync
```

## When to Create

- ✅ Found a non-obvious solution
- ✅ Spent 30+ minutes researching
- ✅ Solution could help future tasks
- ✅ Third-party integration figured out
- ✅ Performance optimization discovered
- ✅ Security measure implemented

#solutions #knowledge #research #learning
