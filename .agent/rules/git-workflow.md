---
description: Unified Git and Task Workflow (Branching, Committing, Merging)
---
# Git & Task Management Workflow
**Requirement:** All tasks and artifacts must follow the **Branch-Based Workflow**.
## A. Branching Strategy (MANDATORY)
❌ **NEVER** commit directly to main or master.
### Branch Naming Convention
| Type | Prefix | Use Case |
|------|--------|----------|
| **Planning** | plan/ | Project plans, product backlogs |
| **Design** | design/ | Architecture schematics, UI specs |
| **Feature** | feat/ | New functionality |
| **Fix** | fix/ | Bug fixes |
| **Docs** | docs/ | General documentation |
**Format:** prefix/TASK-ID-short-name (e.g., plan/SPRINT-2-setup)
### Workflow
1. **Start:** git checkout -b prefix/TASK-ID-name from main.
2. **Work:** Create artifacts or code.
3. **Push:** git push -u origin prefix/TASK-ID-name.
4. **Docs-as-Code:** Treat documentation exactly like code.
## B. Definition of Done (DoD)
1. Branch created.
2. Artifacts implemented.
3. Pull Request created & merged.
## C. Release Workflow (AUTOMATED)
Releases are managed by the Release Agent (`release.py`).
1. **Trigger:** Human or CI runs `/release`.
2. **Commit:** Agent creates `chore(release): vX.Y.Z` commit.
3. **Tag:** Agent creates `vX.Y.Z` tag.
4. **Push:** Agent pushes commit and tags.
## D. Commit Conventions (MANDATORY)
We follow [Conventional Commits](https://www.conventionalcommits.org/) to enable automated semantic versioning.
**Format:** `type(scope): description`
**Types:**
- `feat`: New feature (MINOR bump)
- `fix`: Bug fix (PATCH bump)
- `docs`: Documentation only
- `style`: Formatting, missing semi-colons, etc.
- `refactor`: Code change that neither fixes a bug nor adds a feature
- `perf`: Code change that improves performance
- `test`: Adding missing tests or correcting existing tests
- `chore`: Build process, auxiliary tools, libraries updates
**Breaking Changes:**
Append `!` after type/scope (e.g., `feat!: drop support for Node 12`) for MAJOR bump.
## E. Post-Task Completion (MANDATORY)
After a task is completed, committed, and pushed:
1. **Checkout Main:** `git checkout main`
2. **Pull Latest:** `git pull origin main`
3. **Merge Feature:** `git merge prefix/TASK-ID-name`
4. **Push Main:** `git push origin main`
5. **Delete Local Branch:** `git branch -d prefix/TASK-ID-name`
6. **Delete Remote Branch (Optional):** `git push origin --delete prefix/TASK-ID-name`
