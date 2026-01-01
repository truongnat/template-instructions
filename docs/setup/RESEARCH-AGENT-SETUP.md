# Research Agent System - Complete Setup Guide

> Hướng dẫn đầy đủ để setup và sử dụng Research Agent System

## 🎯 Tổng quan

Research Agent System đã được tích hợp hoàn chỉnh vào Agentic SDLC với 3 components chính:

1. ✅ **Role Integration** - PM, DEV, TESTER workflows updated
2. ✅ **Automated Hooks** - Auto-trigger research
3. ✅ **MCP Integration** - Real API calls to external services

---

## 📦 Files Created

### Core Scripts
```
tools/research/
├── research_agent.py              # Core research agent
├── research_mcp.py                # MCP integration (placeholder)
├── research_mcp_extended.py       # Full MCP with real APIs
└── README.md                      # Complete documentation

tools/setup/
└── setup_research_hooks.sh        # Hook setup script
```

### Workflows Updated
```
.agent/workflows/
├── pm.md                          # ✅ Research integration added
├── dev.md                         # ✅ Research integration added
├── tester.md                      # ✅ Research integration added
└── research.md                    # ✅ New research workflow
```

### Hooks Configuration
```
.kiro/hooks/
└── auto-research-hook.json        # ✅ 5 automated hooks
```

### Documentation
```
docs/
├── RESEARCH-AGENT-SETUP.md        # This file
└── research-reports/              # Research output directory
```

---

## 🚀 Installation Steps

### Step 1: Install Python Dependencies

```bash
# Required
pip install neo4j requests

# Verify installation
python3 -c "import neo4j; import requests; print('✓ Dependencies installed')"
```

### Step 2: Configure Environment

```bash
# Copy template
cp .env.template .env

# Edit .env and add your keys:
nano .env
```

**Required for basic functionality:**
```bash
# Optional but recommended
GITHUB_TOKEN=your_github_personal_access_token
GITHUB_REPO=username/repository
```

**Optional for advanced features:**
```bash
# Neo4j (for large projects)
NEO4J_URI=bolt://localhost:7687
NEO4J_USERNAME=neo4j
NEO4J_PASSWORD=your_password

# External APIs (for MCP extended)
TAVILY_API_KEY=your_tavily_api_key
BRAVE_API_KEY=your_brave_api_key
STACKOVERFLOW_KEY=your_stackoverflow_key
```

### Step 3: Make Scripts Executable

```bash
chmod +x tools/research/research_agent.py
chmod +x tools/research/research_mcp.py
chmod +x tools/research/research_mcp_extended.py
chmod +x tools/setup/setup_research_hooks.sh
```

### Step 4: Setup Automated Hooks

```bash
# Run setup script
bash tools/setup/setup_research_hooks.sh

# Verify hooks installed
cat .kiro/hooks/auto-research-hook.json
```

### Step 5: Create Research Reports Directory

```bash
mkdir -p docs/research-reports
```

### Step 6: Test Installation

```bash
# Basic test
python tools/research/research_agent.py --task "test authentication" --type feature

# Check output
ls -la docs/research-reports/

# Should see:
# - research-YYYYMMDD-HHMMSS.json
# - research-YYYYMMDD-HHMMSS.md
```

---

## 🎯 Usage Guide

### 1. Manual Research

#### For Planning (@PM)
```bash
python tools/research/research_agent.py \
  --task "Build todo app with authentication" \
  --type general
```

#### For Development (@DEV)
```bash
python tools/research/research_agent.py \
  --feature "OAuth authentication" \
  --type feature
```

#### For Bug Fixing (@TESTER)
```bash
python tools/research/research_agent.py \
  --bug "Login timeout error" \
  --type bug
```

#### For Architecture (@SA)
```bash
python tools/research/research_agent.py \
  --task "Microservices architecture" \
  --type architecture
```

### 2. Automated Research (via Hooks)

Hooks tự động trigger khi bạn mention roles trong IDE:

```
User: @PM Build a todo app
→ Hook triggers: python tools/research/research_agent.py --task "Build a todo app"

User: @DEV Implement OAuth login
→ Hook triggers: python tools/research/research_agent.py --feature "Implement OAuth login"

User: @TESTER Bug: Login fails
→ Hook triggers: python tools/research/research_agent.py --bug "Login fails"
```

### 3. MCP Extended (with External APIs)

```bash
# Use extended version for external API calls
python tools/research/research_mcp_extended.py \
  --task "OAuth implementation best practices" \
  --type feature

# Searches:
# - Tavily AI Search
# - Brave Search
# - Stack Overflow
# - GitHub Advanced
# - Documentation sites
```

---

## 📊 Understanding Output

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

🧠 Querying Neo4j Knowledge Graph...
  ✓ Found 5 entries
  Related Technologies:
    • Passport.js (used 5x)
    • JWT (used 8x)

🐙 Searching GitHub Issues...
  ✓ Found 2 issues
    • #123: Implement OAuth authentication (closed)

🔌 Querying External APIs via MCP...
  🔍 Tavily Search: OAuth implementation
    ✓ Found 5 results
  📚 Stack Overflow: OAuth implementation
    ✓ Found 3 questions

============================================================
📊 RESEARCH SUMMARY
============================================================
Confidence Level: HIGH
Related Entries: 13

Findings:
  • Found 3 related entries in Knowledge Base
  • Found 5 related entries in Neo4j
  • Related technologies: Passport.js, JWT, OAuth2
  • Found 2 related GitHub issues
  • Found 13 external resources via MCP APIs

Recommendations:
  ✓ Strong knowledge base available - Review existing solutions before starting
============================================================

💾 Research report saved: docs/research-reports/research-20260101-100000.json
```

### Confidence Levels

**HIGH (5+ entries):**
- ✅ Strong knowledge available
- ✅ Review existing solutions
- ✅ Reuse proven patterns
- ⏱️ Normal timeline

**MEDIUM (2-4 entries):**
- ⚠️ Some knowledge available
- ⚠️ Review and adapt
- ⚠️ Document differences
- ⏱️ Normal + buffer

**LOW (0-1 entries):**
- ⚠️ New territory
- ⚠️ Plan extra time
- ⚠️ Prototype first
- ⚠️ Document thoroughly
- ⏱️ Extended timeline

---

## 🔄 Workflow Integration

### PM Workflow (Updated)

```markdown
## Before Creating Project Plan

1. User provides requirements
2. **RESEARCH FIRST (MANDATORY):**
   ```bash
   python tools/research/research_agent.py --task "[project description]" --type general
   ```
3. Review research report in `docs/research-reports/`
4. Check confidence level
5. Review similar projects in Knowledge Base
6. Identify reusable patterns and known challenges
7. **Include research findings in project plan:**
   ```markdown
   ## Research Findings
   - Research Date: [date]
   - Confidence Level: [high/medium/low]
   - Related KB Entries: [count]
   - Key Insights: [list]
   - Referenced Entries: [list]
   ```
8. Create project plan with adjusted timeline
9. Wait for user approval
```

### DEV Workflow (Updated)

```markdown
## Before Implementation

1. Receive feature assignment
2. **RESEARCH FIRST (MANDATORY):**
   ```bash
   python tools/research/research_agent.py --feature "[feature description]" --type feature
   ```
3. Review similar implementations
4. Identify proven code patterns
5. Note known pitfalls and edge cases
6. **Document in code:**
   ```javascript
   /**
    * Feature: User Authentication
    * Research: KB-2025-12-15-001 (OAuth Implementation Guide)
    * Pattern: Passport.js + JWT (proven in 5 implementations)
    * Known Issues: Token refresh race condition (KB-2025-12-20-002)
    */
   ```
7. Implement with research insights
8. If LOW confidence, create KB entry after completion
```

### TESTER Workflow (Updated)

```markdown
## Before Bug Fixing

1. Bug discovered
2. **RESEARCH FIRST (MANDATORY):**
   ```bash
   python tools/research/research_agent.py --bug "[bug description]" --type bug
   ```
3. Review similar bugs and their solutions
4. Verify if root cause matches known patterns
5. **Create bug report with research:**
   ```markdown
   ## Bug Report
   
   ### Research Findings
   - Confidence Level: [high/medium/low]
   - Similar Bugs: [count]
   - Related KB Entries: [list]
   
   ### Root Cause Analysis
   - Known Pattern: [Yes/No]
   - Previous Solution: [If applicable]
   
   ### Proposed Solution
   [Based on research findings]
   ```
6. Apply proven solution if available
7. If LOW confidence, create KB entry after fix
```

---

## 🔧 Configuration

### Hook Configuration

Edit `.kiro/hooks/auto-research-hook.json`:

```json
{
  "hooks": [
    {
      "id": "research-before-planning",
      "enabled": true,  // ← Enable/disable
      "trigger": {
        "pattern": "(@PM|/pm|project manager)"  // ← Customize pattern
      }
    }
  ],
  "settings": {
    "autoApprove": false,  // ← Require approval
    "showNotifications": true,  // ← Show notifications
    "logLevel": "info"  // ← Log level
  }
}
```

### Research Agent Configuration

Edit `tools/research/research_agent.py` to customize:

```python
# Relevance threshold
MIN_RELEVANCE = 0.3  # 30%

# Max results per source
MAX_KB_RESULTS = 10
MAX_NEO4J_RESULTS = 10
MAX_GITHUB_RESULTS = 10

# Confidence thresholds
HIGH_CONFIDENCE_THRESHOLD = 5
MEDIUM_CONFIDENCE_THRESHOLD = 2
```

---

## 🎓 Best Practices

### 1. Always Research First
```
❌ BAD: @PM Create plan → Start immediately
✓ GOOD: @PM Create plan → Research → Review → Plan with insights
```

### 2. Include Research in Artifacts
```markdown
## Project Plan

### Research Findings
- Confidence: HIGH
- Related entries: 8
- Key insights:
  • OAuth2 flow well-documented
  • JWT best practices available
  • Known token refresh issue

### Timeline Adjustment
- Original estimate: 2 weeks
- With research: 1.5 weeks (reusing patterns)
```

### 3. Document New Patterns
```
If confidence is LOW:
1. Complete implementation
2. Create KB entry:
   cp .agent/templates/Knowledge-Entry-Template.md \
      .agent/knowledge-base/features/KB-$(date +%Y-%m-%d)-###-[name].md
3. Fill in details
4. Update index
```

### 4. Cross-Reference in Code
```javascript
/**
 * Research: KB-2025-12-15-001
 * Pattern: Proven in 5 implementations
 * Known Issues: See KB-2025-12-20-002
 */
function authenticateUser() {
  // Implementation
}
```

### 5. Update Existing Knowledge
```
If you find better solution:
1. Open existing KB entry
2. Add "Updated" section
3. Link to new implementation
4. Update index
```

---

## 🐛 Troubleshooting

### Issue: Neo4j Connection Failed
```bash
⚠️  Neo4j connection failed: Connection refused

Solution:
1. Check Neo4j is running: systemctl status neo4j
2. Verify credentials in .env
3. Test connection: python tools/neo4j/test_neo4j_connection.py
4. Or use file-based KB only (works without Neo4j)
```

### Issue: GitHub Rate Limit
```bash
⚠️  GitHub API error: Rate limit exceeded

Solution:
1. Wait 1 hour for rate limit reset
2. Use authenticated token (higher limit)
3. Or disable GitHub search temporarily
```

### Issue: No Results Found
```bash
✗ No entries found in Knowledge Base
✗ No entries found in Neo4j
✗ No issues found in GitHub

Action:
- This is NEW TERRITORY
- Plan extra time for exploration
- Document thoroughly
- Create KB entry after completion
```

### Issue: Hook Not Triggering
```bash
Solution:
1. Check hook enabled: cat .kiro/hooks/auto-research-hook.json
2. Verify pattern matches: Test with exact trigger phrase
3. Restart Kiro IDE
4. Check logs for errors
```

---

## 📚 Additional Resources

### Documentation
- **Complete Guide:** `tools/research/README.md`
- **Workflow Details:** `.agent/workflows/research.md`
- **PM Integration:** `.agent/workflows/pm.md`
- **DEV Integration:** `.agent/workflows/dev.md`
- **TESTER Integration:** `.agent/workflows/tester.md`

### Scripts
- **Core Agent:** `tools/research/research_agent.py`
- **MCP Basic:** `tools/research/research_mcp.py`
- **MCP Extended:** `tools/research/research_mcp_extended.py`
- **Setup Hooks:** `tools/setup/setup_research_hooks.sh`

### Configuration
- **Hooks:** `.kiro/hooks/auto-research-hook.json`
- **Environment:** `.env`
- **MCP Servers:** `.kiro/settings/mcp.json`

---

## ✅ Verification Checklist

After setup, verify everything works:

- [ ] Python dependencies installed (`neo4j`, `requests`)
- [ ] Scripts are executable (`chmod +x`)
- [ ] `.env` configured with API keys
- [ ] Hooks installed (`.kiro/hooks/auto-research-hook.json`)
- [ ] Research reports directory created (`docs/research-reports/`)
- [ ] Test run successful (`python tools/research/research_agent.py --task "test"`)
- [ ] Workflows updated (PM, DEV, TESTER have research steps)
- [ ] Hooks trigger correctly (test with @PM, @DEV, @TESTER)

---

## 🎉 You're Ready!

Research Agent System is now fully integrated. Start using it:

```bash
# Test it
python tools/research/research_agent.py --task "Build authentication system" --type feature

# Or use in IDE
@PM Build a todo app with authentication
# → Research runs automatically
# → Review findings
# → Create plan with insights
```

**Remember: Always research first, code second!** 🚀

---

#research-agent #setup-guide #integration #automation
