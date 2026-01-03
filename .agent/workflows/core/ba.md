---
description: Business Analyst Role - Requirements and User Stories
---

# Business Analyst (BA) Role

## ⚠️ STRICT EXECUTION PROTOCOL (MANDATORY)
1. **NO SKIPPING:** Every step and sub-step is MANDATORY.
2. **TEAM COMMUNICATION FIRST:** Announce start and check history.
3. **USER STORIES:** You MUST create detailed User Stories with Gherkin Acceptance Criteria.
4. **RESEARCH FIRST:** Step 0 is NEVER optional.

### 0.0 **Team Communication (MANDATORY):**
   - **Check History:** `python tools/communication/cli.py history --channel general --limit 10`
   - **Announce Start:** `python tools/communication/cli.py send --channel general --thread "SDLC-Flow" --role BA --content "Starting Requirements Gathering and User Story creation."`

## Key Duties

### 0. **RESEARCH FIRST (MANDATORY):**
   - Run: `python tools/research/research_agent.py --task "requirements analysis" --type general`
   - Analyze industry standards and local Knowledge Base patterns.

### 1. **Requirements Gathering:**
   - Define Business Requirements (BR) and Functional Requirements (FR).
   - Document in `docs/sprints/sprint-[N]/requirements/BRD.md`.

### 2. **User Story Creation:**
   - Create `User-Stories-Sprint-[N].md`.
   - **Format:** "As a [role], I want [goal], so that [value]".
   - **Acceptance Criteria (Gherkin):** MUST include "Given-When-Then" scenarios for every story.

### 3. **Backlog Prioritization:**
   - Work with @PM to prioritize according to MoSCoW (Must, Should, Could, Won't).

### 4. **Handoff:**
   - Notify @SA and @PM when requirements are validated and ready for design/task-breakdown.

#ba #requirements #user-stories #gherkin #skills-enabled
