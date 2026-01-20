---
description: Process - Complete Task Lifecycle - Plan, Work, Review, Compound
---

# /cycle - Complete Task Lifecycle

Complete Task Lifecycle workflow for small to medium tasks. This workflow guides you through planning, implementation, testing, and knowledge capture.

## ⚠️ STRICT EXECUTION PROTOCOL (MANDATORY)
1. **NO SKIPPING:** Every step is MANDATORY.
2. **TEAM COMMUNICATION FIRST:** Announce start and check history.
3. **GIT FLOW:** Feature branch, atomic commits, PR.
4. **SELF-LEARNING:** After completion, update Neo4j.
5. **QUALITY CHECKS:** Run Observer and Judge before PR.

### 0.0 **Team Communication (MANDATORY):**
   - **Check History:** `agentic-sdlc run tools/infrastructure/communication/cli.py history --channel general --limit 10`
   - **Announce Start:** `agentic-sdlc run tools/infrastructure/communication/cli.py send --channel general --thread "SDLC-Flow" --role AGENT --content "Starting /cycle for [Task]."`

## Workflow Steps

### 1. Research Phase (MANDATORY)
```bash
agentic-sdlc research --feature "[task]" --type feature
```
- [ ] Search KB for similar implementations.
- [ ] Check GitHub issues for context.

### 2. Planning
- Define acceptance criteria.
- Add task to `Development-Log.md`.
- **Observer Check:**
  ```bash
  python tools/core/brain/brain_cli.py observe --action "planning" --context '{"task": "[task]"}'
  ```

### 3. Feature Branch
```bash
git checkout -b feat/TASK-ID-name
git push -u origin feat/TASK-ID-name
```

### 4. Implementation
- Code according to plan.
- Atomic commits: `git commit -m "[TASK-ID] feat: description"`

### 5. Verification & Quality Assurance (MANDATORY)
- Run local tests.
- **Judge Score (Target > 8/10):**
  ```bash
  python tools/core/brain/brain_cli.py score "path/to/main_file.py"
  ```
- **Compliance Check:**
  ```bash
  python tools/core/brain/brain_cli.py observe
  ```

### 6. Merge & Cleanup (MANDATORY)
- Create PR, tag @TESTER.
- Wait for `#testing-passed`.
- **Merge locally and cleanup:**
  ```bash
  git checkout main
  git pull origin main
  git merge feat/TASK-ID-name
  git push origin main
  git branch -d feat/TASK-ID-name
  ```
- Notify Team: `agentic-sdlc run tools/infrastructure/communication/cli.py send --channel general --content "Merged [task] to main and cleaned up branches."`

### 7. Self-Learning (MANDATORY)
```bash
agentic-sdlc kb compound sync
python tools/core/brain/brain_cli.py learn "Completed [task] using [approach]"
```
- Update `CHANGELOG.md`.

#cycle #workflow #git-flow #self-learning

## ⏭️ Next Steps
- **If Compound Complete:** Workflow finished, ready for next task
- **If Issues Found:** Repeat `/cycle` or escalate to `/explore`
- **If Blocked:** Notify user via `notify_user`

---
## ⚠️ ENFORCEMENT REMINDER
Before executing this workflow, agent MUST:
1. Search knowledge base for similar tasks
2. Check current brain state
3. Run /onboarding if new to project
