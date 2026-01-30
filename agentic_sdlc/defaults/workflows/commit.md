---
description: Process - Automated Code Review and Commit
---

# /commit - Review and Commit Changes

## ⚠️ PURPOSE
Automates the process of reviewing changes, generating Conventional Commits messages, and saving progress.

// turbo-all

## When to Use
- You have made code changes and want to save them.
- You need to generate a structured commit message.
- You want a quick sanity check (lint/diff) before committing.

## Tool Maintenance
Before starting complex tasks, ensure your tools are up to date:
```bash
python agentic_sdlc/infrastructure/update/updater.py --check
```

## Workflow Steps

### 1. Check Status
```bash
python agentic_sdlc/infrastructure/git/commit.py review
```

### 2. Review Diff
- **If files UNSTAGED:**
  ```bash
  git add .
  ```
- **If files STAGED:**
  - Read `git diff --cached` to understand changes.
```

### 3. Generate Message
- Format: `type(scope): description`
- Types: `feat`, `fix`, `docs`, `style`, `refactor`, `test`, `chore`
- Example: `feat(auth): implement jwt login`

### 4. Commit using Git
```bash
git commit -m "type(scope): description"
```
*Wait for user confirmation if in interactive mode, otherwise proceed if confident.*

### 5. Verify
```bash
git log -1 --oneline
```

### 6. Push Changes
- **If main or feature branch:**
  ```bash
  python agentic_sdlc/infrastructure/git/commit.py push
  ```
  *Or manually:* `git push`

### 7. Cleanup (If Task Done)
- **If this completes the feature/fix:**
  ```bash
  git checkout main
  git pull origin main
  git merge <branch-name>
  git push origin main
  git branch -d <branch-name>
  ```

## ⏭️ Next Steps
- **If Success:** Return to previous workflow (e.g., `/cycle`).

---
## ENFORCEMENT REMINDER
Always use Conventional Commits format.
