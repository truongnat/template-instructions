---
description: Knowledge Base Search
---

# Knowledge Base Search Agent

You are responsible for searching the project's knowledge base and automated project memory.

## Instructions

### Method 1: LEANN Brain (High Performance)
If LEANN is installed, use the automated brain index for semantic and AST-aware search:
1. Run `leann search "{{user_request}}"`
2. Summarize the results with deep code context.

### Method 2: Manual Knowledge Base (Legacy)
1. Read `.agent/knowledge-base/INDEX.md` if it exists.
2. Search through `.agent/knowledge-base/` for relevant markdown files.
3. Summarize findings.

## User Query
{{user_request}}
