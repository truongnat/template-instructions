---
description: LEANN AI Brain - Automated Project Memory
---

# LEANN AI Brain Workflow

This workflow manages the automated project memory using the LEANN (Lean and Efficient AI Near-memory) framework.

## 🚀 Setup & Initialization

1. **Install LEANN Core**
   If not already installed, run:
   ```bash
   pip install leann-core leann-backend-hnsw
   ```

2. **Initialize Project Index**
   Index the current workspace with AST-aware chunking:
   ```bash
   leann index --path .
   ```

## 🧠 Memory & Reasoning Management

3. **Update LEANN Index (Vector)**
   Run this for semantic code search:
   ```bash
   leann index --update
   ```

4. **Update Neo4j Graph (Reasoning)**
   Run this to sync project structure and GitHub issues to the cloud:
   ```bash
   # Sync file structure
   python tools/github/graph_brain.py
   
   # Sync GitHub issues
   python tools/github/sync_github.py
   ```

5. **Search Project Brain**
   - **Semantic Search:** `leann search "{{query}}"`
   - **Reasoning Query:** Use the Neo4j console or custom scripts to find relationships between issues and code.

## 🔌 IDE Integration (MCP)

6. **Start LEANN MCP Server**
   ```bash
   bunx --bun @yichuan-w/leann-mcp
   ```
   *Note: Add this to your `claude_desktop_config.json` or Cursor MCP settings.*

## 📋 Best Practices
- Use `/brain <query>` in chat to trigger this workflow.
- Indexing is AST-aware; it understands functions, classes, and logic flow better than standard grep.
- Keep the index updated to ensure agents have the latest context.
