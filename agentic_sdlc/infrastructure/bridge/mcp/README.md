# MCP (Model Context Protocol) Connectors

> Layer 3: Infrastructure - External integrations and AI model connections.

## Overview

MCP provides standardized connectors for:
- File system access
- Database connections (PostgreSQL, Supabase)
- API integrations (Vercel, Apidog, Firecrawl)
- Web search (Brave, Tavily)
- Custom data sources

## Structure

```
agentic_sdlc/mcp/
├── __init__.py
├── README.md
├── connectors/
│   ├── __init__.py
│   ├── filesystem.py    # File system connector
│   ├── database.py      # Database connector
│   ├── api.py           # REST API connector
│   ├── github.py        # GitHub connector
│   └── research.py      # CUSTOM RESEARCH connector (FREE)
├── protocol.py          # MCP protocol handler
└── config.py            # MCP configuration
```

## Special Connector: Research Connector (Custom Free)

The `ResearchConnector` is a specialized MCP component that operates **without third-party API keys**. It aggregates technical data from:
- **DuckDuckGo**: General web search and documentation.
- **GitHub**: Repository search and pattern discovery.
- **Stack Overflow**: Technical Q&A and error resolutions.

### Usage in Code

```python
from agentic_sdlc.mcp.connectors.research import ResearchConnector

connector = ResearchConnector()
# Perform comprehensive research
results = connector.research_task("thread-safe singleton", "architecture")
```

### Usage via CLI

```bash
# Autonomous research chain
python agentic_sdlc/core/brain/brain_cli.py auto-research "asyncio patterns"
```

## Usage

### Python API

```python
from agentic_sdlc.mcp import MCPClient
from agentic_sdlc.mcp.connectors import FileSystemConnector

# Initialize connector
fs = FileSystemConnector(root_path="/project")

# List resources
resources = fs.list_resources()

# Read resource
content = fs.read_resource("src/main.py")
```

### Database Connector

```python
from agentic_sdlc.mcp.connectors import DatabaseConnector

# Connect to PostgreSQL/Supabase
db = DatabaseConnector(
    connection_string=os.getenv("POSTGRES_CONNECTION_STRING")
)

# Query data
results = db.query("SELECT * FROM users")
```

### API Connector

```python
from agentic_sdlc.mcp.connectors import APIConnector

# Connect to external API
api = APIConnector(
    base_url="https://api.example.com",
    api_key=os.getenv("API_KEY")
)

# Make request
response = api.get("/endpoint")
```

## Configuration

Configure MCP in `.env`:

```bash
# MCP Settings
MCP_ENABLED=true
MCP_LOG_LEVEL=info
MCP_MAX_CONNECTIONS=10

# Database
POSTGRES_CONNECTION_STRING=postgresql://user:pass@host:5432/db
SUPABASE_URL=https://xxx.supabase.co
SUPABASE_KEY=your_key

# APIs
FIRECRAWL_API_KEY=your_key
VERCEL_TOKEN=your_token
APIDOG_API_KEY=your_key

# Search
BRAVE_API_KEY=your_key
TAVILY_API_KEY=your_key
```

## Available Connectors

| Connector | Purpose | Config Required |
|-----------|---------|-----------------|
| **FileSystem** | Local file access | Root path |
| **Database** | PostgreSQL/Supabase | Connection string |
| **API** | REST API calls | Base URL, API key |
| **GitHub** | GitHub integration | GitHub token |

## Integration

MCP connectors are used by:
- Intelligence layer for research and data access
- Infrastructure tools for external integrations
- Brain CLI for resource management
- Workflows for automated tasks

## 🔗 Related

- **Infrastructure Layer**: `../infrastructure/README.md`
- **Intelligence Layer**: `../intelligence/README.md`
- **Environment Config**: `../../.env.template`

---

**Version:** 1.0.0  
**Layer:** 3 (Infrastructure)  
**Location:** `agentic_sdlc/mcp/`
