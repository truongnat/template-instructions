---
description: Unified Git and Task Workflow (Branching, Committing, Merging)
---

# Git & Task Management Workflow

**Requirement:** All tasks must follow the **Feature Branch Workflow** with atomic commits and explicit merge gates.

## A. Branching Strategy (MANDATORY)
- ❌ **NEVER** commit directly to `main` or `master`.
- **Naming Convention:**
  - Feature: `feat/TASK-ID-short-name`
  - Bugfix: `fix/TASK-ID-short-name`
  - Hotfix: `hotfix/short-name`
- **Workflow:**
  1. Pick task from `Development-Log`.
  2. Create branch: `git checkout -b feat/TASK-ID-name`.
  3. Push branch immediately: `git push -u origin feat/TASK-ID-name`.

## B. Atomic Commit Rule
- **Frequency:** Commit for every logical sub-task or unit of work.
- **Message Format:** `[TASK-ID] <type>: <description>`
  - Types: `feat`, `fix`, `refactor`, `docs`, `test`, `chore`.
  - Example: `[T-101] feat: implement oauth2 login flow`.
- **Update Log:** Link every commit hash to the corresponding task in `Development-Log`.

## C. Pull Request & Merging (The Quality Gate)
- **Initiation:** After completing a feature/fix building and local testing.
- **PR Description:** Must list changes, link to issues, and provide evidence (screenshots/logs).
- **Review Gate:** 
  - **Code Review:** Must be reviewed by another `@DEV` or `@SA`.
  - **QA Review:** Must be verified by `@TESTER` (Phase 6).
- **Merging Rule:**
  - ❌ **NEVER** self-merge without approval.
  - Merging is done by `@DEVOPS` or `@SA` only after `@TESTER` provides `#testing-passed` tag.
  - Use `Squash and Merge` to keep `main` history clean.

## D. Definition of Done (DoD)
A task is "Done" ONLY when:
1. [ ] Code implemented and branch created.
2. [ ] Atomic commits linked in `Development-Log`.
3. [ ] Pull Request created and reviewed.
4. [ ] **TESTER verified** on the feature branch.
5. [ ] Merged into `main`.
6. [ ] CHANGELOG.md updated.

## E. Automated Changelog Updates
- **Requirement:** Every merge to `main` MUST trigger a `CHANGELOG.md` update.
- **Format:** `[YYYY-MM-DD] [Version] [Type]: [Summary] (@Author)`

---

#git-workflow #branching #atomic-commits #merging #dod
