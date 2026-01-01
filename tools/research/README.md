# Research Agent System

> Tự động research và explore knowledge trước khi bắt đầu bất kỳ task nào (planning, development, bug fixing)

## 📋 Tổng quan

Research Agent System là một hệ thống tự động tìm kiếm và phân tích knowledge từ nhiều nguồn trước khi bắt đầu công việc. Giúp team tránh reinvent the wheel và tận dụng kinh nghiệm có sẵn.

### Mục đích
- ✅ **Tìm kiếm knowledge có sẵn** trước khi bắt đầu
- ✅ **Tránh lặp lại lỗi** đã biết
- ✅ **Tái sử dụng patterns** đã được chứng minh
- ✅ **Tiết kiệm thời gian** development
- ✅ **Nâng cao chất lượng** code

---

## 🎯 Components

### 1. Core Research Agent (`tools/research/research_agent.py`)

**Chức năng chính:**
- Search Knowledge Base (file system)
- Query Neo4j knowledge graph (optional)
- Search GitHub issues/PRs
- Calculate confidence level
- Generate research reports

**Usage:**
```bash
# General task
python tools/research/research_agent.py --task "Build authentication system"

# Bug research
python tools/research/research_agent.py --bug "Login fails with OAuth"

# Feature research
python tools/research/research_agent.py --feature "Real-time notifications"

# With specific type
python tools/research/research_agent.py --task "API design" --type architecture
```

**Output:**
- Console output với findings
- JSON report: `docs/research-reports/research-YYYYMMDD-HHMMSS.json`
- Markdown summary: `docs/research-reports/research-YYYYMMDD-HHMMSS.md`

### 2. MCP Integration (`tools/research/research_mcp.py`)

**Extends research_agent.py với MCP tools:**
- Web search placeholder
- Documentation fetch
- Stack Overflow search
- Ready for full MCP integration

**Usage:**
```bash
python tools/research/research_mcp.py --task "Build authentication" --type feature
```

### 3. Extended MCP (`tools/research/research_mcp_extended.py`)

**Full MCP integration với real API calls:**
- ✅ Tavily AI Search API
- ✅ Brave Search API
- ✅ Stack Overflow API
- ✅ GitHub Advanced Search API
- ✅ Documentation fetching

**Required API Keys:**
```bash
# .env
TAVILY_API_KEY=your_key
BRAVE_API_KEY=your_key
STACKOVERFLOW_KEY=your_key (optional)
GITHUB_TOKEN=your_token
```

**Usage:**
```bash
python tools/research/research_mcp_extended.py --task "OAuth implementation" --type feature
```

### 4. Workflow Integration

**Updated workflows:**
- `.agent/workflows/pm.md` - PM với research integration
- `.agent/workflows/dev.md` - DEV với research integration
- `.agent/workflows/tester.md` - TESTER với research integration
- `.agent/workflows/research.md` - Research workflow documentation

**Mỗi role giờ có:**
- ✅ Mandatory research step (Step 0)
- ✅ Research checklist
- ✅ Decision making based on confidence
- ✅ Knowledge contribution guidelines

### 5. Automated Hooks

**Hook configuration:** `.kiro/hooks/auto-research-hook.json`

**Available hooks:**
- `research-before-planning` - Trigger khi @PM
- `research-before-development` - Trigger khi @DEV
- `research-before-bug-fix` - Trigger khi @TESTER
- `research-before-architecture` - Trigger khi @SA
- `research-on-demand` - Trigger khi /research

**Setup:**
```bash
bash tools/setup/setup_research_hooks.sh
```

---

## 🚀 Quick Start

### 1. Install Dependencies

```bash
# Python dependencies
pip install neo4j requests

# Make scripts executable
chmod +x tools/research/research_agent.py
chmod +x tools/research/research_mcp.py
chmod +x tools/research/research_mcp_extended.py
chmod +x tools/setup/setup_research_hooks.sh
```

### 2. Configure Environment

```bash
# Copy .env.template to .env
cp .env.template .env

# Edit .env and add:
NEO4J_URI=bolt://localhost:7687          # Optional
NEO4J_USERNAME=neo4j                     # Optional
NEO4J_PASSWORD=your_password             # Optional
GITHUB_TOKEN=your_github_token           # Optional
GITHUB_REPO=username/repo                # Optional
TAVILY_API_KEY=your_tavily_key          # Optional
BRAVE_API_KEY=your_brave_key            # Optional
```

### 3. Setup Hooks (Optional)

```bash
bash tools/setup/setup_research_hooks.sh
```

### 4. Test Research Agent

```bash
# Basic test
python tools/research/research_agent.py --task "test authentication" --type feature

# Check output
ls -la docs/research-reports/
```

---

## 📊 Workflow Integration

### Before Planning (@PM)

```markdown
## PM Workflow

1. User provides requirements
2. **RESEARCH FIRST:**
   ```bash
   python tools/research/research_agent.py --task "[project description]" --type general
   ```
3. Review research report
4. Check confidence level
5. Incorporate findings into project plan
6. Create project plan with research insights
```

### Before Development (@DEV)

```markdown
## DEV Workflow

1. Receive feature assignment
2. **RESEARCH FIRST:**
   ```bash
   python tools/research/research_agent.py --feature "[feature description]" --type feature
   ```
3. Review similar implementations
4. Identify proven patterns
5. Note known pitfalls
6. Implement with research insights
7. Document new patterns if needed
```

### Before Bug Fixing (@TESTER)

```markdown
## TESTER Workflow

1. Bug discovered
2. **RESEARCH FIRST:**
   ```bash
   python tools/research/research_agent.py --bug "[bug description]" --type bug
   ```
3. Review similar bugs
4. Check known solutions
5. Verify root cause
6. Apply proven fix
7. Update KB if new pattern
```

---

## 📈 Confidence Levels

### High Confidence (5+ entries)
```
✓ Strong knowledge available

Actions:
- Review top 3-5 related entries
- Extract successful patterns
- Avoid known pitfalls
- Reuse proven solutions
- Update existing knowledge if needed

Timeline: Normal (knowledge available)
```

### Medium Confidence (2-4 entries)
```
⚠️  Some knowledge available

Actions:
- Review available entries
- Identify gaps in knowledge
- Consider similar approaches
- Plan to document new learnings

Timeline: Normal + buffer (some unknowns)
```

### Low Confidence (0-1 entries)
```
⚠️  Limited knowledge - New territory

Actions:
- Plan extra time for exploration
- Document thoroughly for future
- Consider prototyping first
- Create detailed KB entry after

Timeline: Extended (new challenge)
```

---

## 🔍 Search Sources

### 1. Knowledge Base (File System)
**Location:** `.agent/knowledge-base/`

**Categories:**
- `bugs/` - Bug patterns and fixes
- `features/` - Feature implementations
- `architecture/` - Design decisions
- `security/` - Security issues
- `performance/` - Performance optimizations
- `platform-specific/` - Platform issues

**Search method:** Keyword matching + relevance scoring

### 2. Neo4j Knowledge Graph (Optional)
**When to use:**
- Large projects (> 1000 entries)
- Need pattern recognition
- Complex relationships
- Team collaboration

**Queries:**
- Related knowledge entries
- Technology patterns
- Similar tasks
- Solution patterns

### 3. GitHub Issues/PRs
**Searches:**
- Related issues
- Pull requests
- Discussions
- Code examples

**Requires:** `GITHUB_TOKEN` in `.env`

### 4. External APIs (MCP Extended)
**Tavily AI Search:**
- AI-powered search
- Trusted domains
- Answer extraction

**Brave Search:**
- Privacy-focused
- Recent results
- Web search

**Stack Overflow:**
- Technical Q&A
- Code examples
- Community solutions

**GitHub Advanced:**
- Repository search
- Code search
- Stars/topics filtering

---

## 📝 Research Report Format

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
    • OAuth Implementation Guide (80% relevance)
    • JWT Token Management (60% relevance)

🧠 Querying Neo4j Knowledge Graph...
  ✓ Found 5 entries
  Related Technologies:
    • Passport.js (used 5x)
    • JWT (used 8x)

🐙 Searching GitHub Issues...
  ✓ Found 2 issues

🔌 Querying External APIs via MCP...
  ✓ Tavily: 5 results
  ✓ Stack Overflow: 3 questions

============================================================
📊 RESEARCH SUMMARY
============================================================
Confidence Level: HIGH
Related Entries: 13

Recommendations:
  ✓ Strong knowledge base available - Review before starting
============================================================

💾 Research report saved: docs/research-reports/research-20260101-100000.json
```

### JSON Report Structure
```json
{
  "task": "Build authentication system",
  "task_type": "feature",
  "timestamp": "2026-01-01T10:00:00",
  "sources": {
    "knowledge_base": {
      "found": true,
      "entries": [...]
    },
    "neo4j": {
      "found": true,
      "entries": [...],
      "related_technologies": [...]
    },
    "github": {
      "found": true,
      "issues": [...],
      "pull_requests": [...]
    },
    "mcp_extended": {
      "tavily_search": {...},
      "brave_search": {...},
      "stackoverflow": {...}
    }
  },
  "summary": {
    "confidence": "high",
    "related_entries": 13,
    "findings": [...],
    "recommendations": [...]
  }
}
```

### Markdown Report
```markdown
# Research Report

**Task:** Build authentication system
**Type:** feature
**Date:** 2026-01-01T10:00:00

## Summary
- **Confidence:** high
- **Related Entries:** 13

### Findings
- Found 3 related entries in Knowledge Base
- Found 5 related entries in Neo4j
- Related technologies: Passport.js, JWT, OAuth2

### Recommendations
- ✓ Strong knowledge base available - Review before starting

## Detailed Results
[Links to all entries...]
```

---

## 🎯 Best Practices

### 1. Always Research First
```
❌ BAD: Start coding immediately
✓ GOOD: Research → Review → Plan → Code
```

### 2. Document New Findings
```
If confidence is LOW:
→ This is new territory
→ Document thoroughly
→ Create KB entry after completion
```

### 3. Update Existing Knowledge
```
If you find better solution:
→ Update existing KB entry
→ Add "Updated" section
→ Link to new implementation
```

### 4. Cross-Reference in Code
```javascript
/**
 * Feature: User Authentication
 * Research: KB-2025-12-15-001 (OAuth Implementation Guide)
 * Pattern: Passport.js + JWT (proven in 5 implementations)
 * Known Issues: Token refresh race condition (KB-2025-12-20-002)
 */
```

### 5. Include in Artifacts
```markdown
## Research Findings
- Research Date: 2026-01-01
- Confidence Level: high
- Related KB Entries: 3
- Key Insights:
  • OAuth2 flow well-documented
  • JWT best practices available
  • Known token refresh issue
- Referenced Entries:
  • KB-2025-12-15-001: OAuth Implementation
  • KB-2025-12-20-002: JWT Token Management
```

---

## 🔧 Troubleshooting

### Neo4j Not Available
```bash
⚠️  Neo4j driver not installed
Solution: pip install neo4j

⚠️  Neo4j credentials not found
Solution: Add to .env file
```

### GitHub API Rate Limit
```bash
⚠️  GitHub API error: Rate limit exceeded
Solution: Wait or use authenticated token
```

### No Results Found
```bash
✗ No entries found
Action: This is new territory - document thoroughly!
```

### MCP API Errors
```bash
⚠️  Tavily API error
Solution: Check API key in .env

⚠️  Brave API error
Solution: Verify API key and quota
```

---

## 📚 Examples

### Example 1: Planning New Feature
```bash
# User: @PM Build a todo app with authentication

# PM runs research:
python tools/research/research_agent.py --task "todo app with authentication" --type general

# Output:
# Confidence: HIGH
# Found: 8 related entries
# Recommendation: Review existing solutions

# PM creates plan referencing:
# - KB-2025-12-10-001: Todo App Architecture
# - KB-2025-12-15-001: OAuth Implementation
# - GitHub Issue #123: Similar project
```

### Example 2: Implementing Feature
```bash
# User: @DEV Implement OAuth login

# DEV runs research:
python tools/research/research_agent.py --feature "OAuth login" --type feature

# Output:
# Confidence: HIGH
# Found: 5 implementations
# Technologies: Passport.js, JWT, OAuth2

# DEV implements using proven pattern:
# - Reuses Passport.js setup from KB-2025-12-15-001
# - Avoids token refresh issue from KB-2025-12-20-002
# - References research in code comments
```

### Example 3: Fixing Bug
```bash
# User: @TESTER Login fails with "Token expired" error

# TESTER runs research:
python tools/research/research_agent.py --bug "Token expired error" --type bug

# Output:
# Confidence: HIGH
# Found: 3 similar bugs
# Solution: Token refresh race condition

# TESTER applies known fix:
# - Reviews KB-2025-12-20-002
# - Applies mutex lock solution
# - Verifies fix works
# - Updates KB with confirmation
```

---

## 🎓 Advanced Usage

### Custom Search Patterns
```python
# Extend research_agent.py
def _custom_search(self, task: str) -> Dict:
    # Add custom search logic
    pass
```

### Integration with CI/CD
```yaml
# .github/workflows/research.yml
name: Auto Research
on: [pull_request]
jobs:
  research:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Run Research
        run: |
          python tools/research/research_agent.py --task "${{ github.event.pull_request.title }}"
```

### Slack/Discord Notifications
```python
# Add to research_agent.py
def _send_notification(self, results: Dict):
    # Send to Slack/Discord
    pass
```

---

## 📞 Support

### Questions?
- Check: `.agent/workflows/research.md`
- Review: `tools/research/research_agent.py` comments
- Ask: @REPORTER for help

### Issues?
- Check logs in `docs/research-reports/`
- Verify API keys in `.env`
- Test with: `python tools/research/research_agent.py --task "test"`

### Contributions?
- Add new search sources
- Improve relevance scoring
- Extend MCP integration
- Add new confidence metrics

---

## 🎉 Summary

Research Agent System giúp team:
- ✅ Tìm kiếm knowledge tự động
- ✅ Tránh lặp lại lỗi
- ✅ Tái sử dụng patterns
- ✅ Tiết kiệm thời gian
- ✅ Nâng cao chất lượng

**Always research first, code second!** 🚀

---

#research-agent #knowledge-base #automation #best-practices
