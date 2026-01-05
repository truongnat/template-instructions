# MCP (Model Context Protocol) Connectors

> Layer 3: Infrastructure - External integrations and AI model connections.

## Overview

MCP provides standardized connectors for:
- File system access
- Database connections
- API integrations
- Custom data sources

## Structure

```
mcp/
├── __init__.py
├── README.md
├── connectors/
│   ├── __init__.py
│   ├── filesystem.py    # File system connector
│   ├── database.py      # Database connector
│   ├── api.py           # REST API connector
│   └── github.py        # GitHub connector
├── protocol.py          # MCP protocol handler
└── config.py            # MCP configuration
```

## Usage

```python
from mcp import MCPClient
from mcp.connectors import FileSystemConnector

# Initialize connector
fs = FileSystemConnector(root_path="/project")

# List resources
resources = fs.list_resources()

# Read resource
content = fs.read_resource("src/main.py")
```

## Configuration

Configure MCP in `.env`:

```bash
MCP_ENABLED=true
MCP_LOG_LEVEL=info
MCP_MAX_CONNECTIONS=10
```
