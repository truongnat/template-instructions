---
description: Intelligence - Deep Search MCP for Technical Research
---

# /deep-search - Technical Research Workflow

Deep web search using DuckDuckGo, GitHub, and StackOverflow APIs.
**No third-party AI services** - fully manual implementation.

// turbo-all

## Quick Commands

```bash
# Aggregated search (all sources)
python mcp/connectors/deep_search.py --search "query"

# DuckDuckGo only
python mcp/connectors/deep_search.py --ddg "query"

# GitHub repos/code
python mcp/connectors/deep_search.py --github "query"

# StackOverflow Q&A
python mcp/connectors/deep_search.py --stackoverflow "query"

# Check status
python mcp/connectors/deep_search.py --status
```

## Available Tools

| Tool | Description | API Key |
|------|-------------|---------|
| `deep_search` | Aggregated multi-source search | None |
| `ddg_search` | DuckDuckGo web search | None |
| `github_search` | GitHub repos/code/issues | Optional |
| `stackoverflow_search` | Stack Overflow Q&A | None |
| `fetch_content` | Extract content from URL | None |

## Python Usage

```python
from mcp.connectors.deep_search import DeepSearchConnector
import json

connector = DeepSearchConnector()

# Aggregated search
result = connector.call_tool("deep_search", {"query": "Python async await"})
print(json.dumps(result, indent=2))

# GitHub with filters
result = connector.call_tool("github_search", {
    "query": "MCP connector",
    "search_type": "repositories",
    "language": "python",
    "sort": "stars"
})

# StackOverflow with tags
result = connector.call_tool("stackoverflow_search", {
    "query": "async programming",
    "tags": ["python", "asyncio"],
    "sort": "votes"
})
```

## Integration

- **@RESEARCH** - Primary user for investigations
- **@SA** - Architecture decision research
- **@DEV** - Solution lookup
- **/explore** - Deep investigation workflow
- **/planning** - Requirements research

#deep-search #research #mcp #technical

## ⏭️ Next Steps
- **If Found Solution:** Apply to implementation
- **If Need More Info:** Use `fetch_content` to extract URL details
- **If GitHub Rate Limited:** Set `GITHUB_TOKEN` env var
