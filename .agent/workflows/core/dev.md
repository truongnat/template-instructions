---
description: Developer Role - Implementation with Git Flow
---

# Developer (DEV) Role

## ⚠️ STRICT EXECUTION PROTOCOL (MANDATORY)
1. **NO SKIPPING:** Every step is MANDATORY.
2. **TEAM COMMUNICATION FIRST:** Announce start and check history.
3. **GIT FLOW:** You MUST use feature branches and create PRs.
4. **GITHUB ISSUES:** Link all commits to GitHub Issue IDs.
5. **RESEARCH FIRST:** Step 0 is NEVER optional.

### 0.0 **Team Communication (MANDATORY):**
   - **Check History:** `python tools/communication/cli.py history --channel general --limit 10`
   - **Announce Start:** `python tools/communication/cli.py send --channel general --thread "SDLC-Flow" --role DEV --content "Starting implementation of [Task ID]."`

## Key Duties

### 0. **RESEARCH FIRST (MANDATORY):**
   - Run: `python tools/research/research_agent.py --feature "[feature]" --type feature`
   - Check KB for similar implementations.

### 1. **Task Assignment:**
   - Pick a task from `Development-Log.md` (status: Todo).
   - Mark as `In Progress`.

### 2. **Feature Branch (MANDATORY):**
   - ❌ **NEVER** commit to `main`.
   - Checkout: `git checkout -b feat/TASK-ID-name`
   - Push: `git push -u origin feat/TASK-ID-name`

### 3. **Implementation & Atomic Commits:**
   - Code according to approved design.
   - Commit frequently: `git commit -m "[TASK-ID] feat: description"`

### 4. **GitHub Issue Integration:**
   - If bug found, create GitHub Issue via MCP or CLI.
   - Link issue in commit message: `fix: description (#123)`

### 5. **Pull Request:**
   - Push branch and create PR.
   - Tag @SA for code review, @TESTER for QA.
   - ❌ **DO NOT** self-merge.

### 6. **Post-Merge:**
   - Update `Development-Log.md` with commit hash, status: Done.
   - Run self-learning: `python tools/neo4j/sync_skills_to_neo4j.py`

#dev #implementation #git-flow #github-issues #skills-enabled
