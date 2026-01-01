# 🧠 LEANN AI Brain: Automated Project Memory

Welcome to the future of project knowledge management. By integrating **LEANN**, we've shifted from a manual, file-based knowledge base to a high-performance, automated "Project Brain."

## 🚀 Why LEANN?

- **97% Storage Savings:** Massive vector indices now fit in megabytes, not gigabytes.
- **AST-Aware:** The brain understands code structure (functions, classes, logic) rather than just raw text.
- **RAG on Everything:** Not just docs, but your code, git history, and even browser research can be indexed.
- **Privacy First:** 100% local operation. No data leaves your machine.

## 🛠️ How to Use

### 1. The `/brain` Command
Use `/brain [query]` in your IDE chat to ask the project anything.
> Example: `/brain how did we handle OAuth in previous sprints?`

### 2. Updating the Index
When you finish a major feature or a sprint, update the memory:
```bash
leann index --update
```

### 3. MCP Integration
For the best experience, ensure the LEANN MCP server is running. This allows agents to "query" the brain during their standard workflows without you providing explicit files.

## 📁 Migration from Legacy KB
Your existing manual entries in `.agent/knowledge-base/` are still valuable and are automatically indexed by LEANN. You can still use `/kb-search` for traditional manual searches, but `/brain` is now the recommended primary method.

---
*Powered by [LEANN](https://github.com/yichuan-w/LEANN)*
