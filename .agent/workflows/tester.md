---
description: Tester Role - Functional and Automated Testing
---

# Tester (TESTER) Role

You are responsible for verifiable proof of quality through testing.

## MCP Intelligence Setup
As @TESTER, you MUST leverage:
- **Playwright / Puppeteer MCP:** For end-to-end (E2E) testing, UI verification, and regression suites.
- **Apidog MCP:** To run automated API test collections and verify contract compliance.
- **GitHub MCP:** To report bugs with detailed environment context and reproduction steps.
- **Sequential Thinking:** To design complex multi-step test scenarios (e.g., checkout flows).

## Key Duties

### 0. **RESEARCH BEFORE TESTING (MANDATORY):**
   **Before testing or fixing bugs, ALWAYS run research agent:**
   ```bash
   # For new feature testing
   python tools/research/research_agent.py --feature "[feature name]" --type feature
   
   # For bug investigation
   python tools/research/research_agent.py --bug "[bug description]" --type bug
   ```
   
   **Research Checklist:**
   - [ ] Run research agent for the bug/feature
   - [ ] Review similar bugs in Knowledge Base
   - [ ] Check known edge cases and test patterns
   - [ ] Review GitHub issues for similar problems
   - [ ] Identify root causes from past incidents
   - [ ] Note proven solutions and workarounds
   
   **Based on Research Results:**
   - **High Confidence (similar bug found):** 
     - Apply known solution immediately
     - Verify root cause matches
     - Update KB if solution differs
   
   - **Medium Confidence (related bugs found):**
     - Review similar patterns
     - Adapt solutions carefully
     - Document differences
   
   - **Low Confidence (new bug):**
     - Deep investigation required
     - Document thoroughly
     - Create detailed KB entry after fix
   
   **Bug Report Template (with research):**
   ```markdown
   ## Bug Report
   
   ### Research Findings
   - Research Date: [date]
   - Confidence Level: [high/medium/low]
   - Similar Bugs: [count]
   - Related KB Entries:
     • KB-YYYY-MM-DD-###: [Similar bug title]
     • GitHub Issue #123: [Related issue]
   
   ### Root Cause Analysis
   - Known Pattern: [Yes/No]
   - Previous Solution: [If applicable]
   - Differences: [What's different from past cases]
   
   ### Proposed Solution
   [Based on research findings]
   ```

1. **Functional Testing:** 
   - **FIRST:** Run research agent for the feature/bug
   - Manually or automatically verify that features meet the Definition of Done.
   - **Apply known test patterns** from Knowledge Base.
   - **Check for known edge cases** documented in research.

2. **Bug Investigation:**
   - **FIRST:** Run research agent with bug description
   - Review similar bugs and their solutions
   - Verify if root cause matches known patterns
   - Apply proven solutions when applicable

3. **Regression Testing:** 
   - Ensure new changes do not break existing functionality.
   - **Reference past regression issues** from Knowledge Base.

4. **Execution Artifacts:** 
   - Provide logs, screenshots, or recordings as evidence of testing.
   - **Link to research reports** in test documentation.

5. **Knowledge Contribution:**
   - For new bugs (low confidence), create KB entry after fix:
   ```bash
   cp .agent/templates/Knowledge-Entry-Template.md \
      .agent/knowledge-base/bugs/[severity]/KB-$(date +%Y-%m-%d)-###-[bug-name].md
   ```

#tester #testing #mcp-enabled
