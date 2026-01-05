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

## Workflow Steps

### 1. Check Status
```bash
python tools/git/commit.py review
```

### 2. Review Diff
- **If files UNSTAGED:**
  ```bash
  git add .
  ```
- **If files STAGED:**
  - Read `git diff --cached` to understand changes.

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

## ⏭️ Next Steps
- **If Success:** Return to previous workflow (e.g., `/cycle`).
- **If Push Needed:** Ask user or run `git push` if authorized.

---
## ENFORCEMENT REMINDER
Always use Conventional Commits format.
