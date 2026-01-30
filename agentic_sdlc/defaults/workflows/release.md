---
description: Support - Release Management Workflow
---

# /release - Changelog and Version Management

## ⚠️ STRICT EXECUTION PROTOCOL (MANDATORY)
1. **CONVENTIONAL COMMITS:** All commits must follow conventional commit format.
2. **SEMVER:** Version bumps follow semantic versioning.
3. **CHANGELOG:** Update CHANGELOG.md before releasing.

## Quick Commands

```bash
# Preview changes (dry run)
python agentic_sdlc/infrastructure/lifecycle/release/release.py preview

# Generate changelog only
python agentic_sdlc/infrastructure/lifecycle/release/release.py changelog --sprint 6

# Bump version only
python agentic_sdlc/infrastructure/lifecycle/release/release.py version --auto

# Full release cycle
python agentic_sdlc/infrastructure/lifecycle/release/release.py release --commit --tag --push --publish
```

## Conventional Commit Format

```
type(scope): description

feat(landing): add hero section animation
fix(api): resolve timeout issue
docs(kb): update authentication guide
refactor(core): extract utility functions
```

### Types and Changelog Categories

| Type | Changelog Category | Version Bump |
|------|-------------------|--------------|
| `feat` | Added | Minor |
| `fix` | Fixed | Patch |
| `docs` | Documentation | Patch |
| `refactor` | Changed | Patch |
| `perf` | Performance | Patch |
| `test` | Testing | - |
| `chore` | Maintenance | - |
| `BREAKING CHANGE` | Breaking | Major |

### Scopes (Optional)

| Scope | Tag in Changelog |
|-------|------------------|
| `landing` | [Landing Page] |
| `agent` | [Agent System] |
| `workflow` | [Workflows] |
| `kb` | [Knowledge Base] |
| `tools` | [Tools] |
| `ui` | [UI] |
| `api` | [API] |

## Workflow Steps

### 1. Preview Changes
```bash
python agentic_sdlc/infrastructure/lifecycle/release/release.py preview --sprint 6
```
Shows:
- Last git tag
- Current version
- Commits since last release
- Auto-detected bump type
- Preview changelog entry

### 2. Generate Changelog
```bash
python agentic_sdlc/infrastructure/lifecycle/release/release.py changelog --sprint 6 --dry-run
```
- Parses commits since last tag
- Categorizes by type
- Generates markdown section
- Inserts into CHANGELOG.md

### 3. Bump Version
```bash
# Auto-detect based on commits
python agentic_sdlc/infrastructure/lifecycle/release/release.py version --auto

# Explicit bump type
python agentic_sdlc/infrastructure/lifecycle/release/release.py version --bump minor
```
Updates `package.json` version.

### 4. Full Release
```bash
python agentic_sdlc/infrastructure/lifecycle/release/release.py release --sprint 6 --commit --tag --push --publish
```
Executes:
1. Parse commits
2. Detect bump type
3. Generate changelog
4. Update version
5. Commit changes (optional)
6. Create git tag (optional)
7. Push changes (optional)
8. Publish to npm/bun (optional)

### 5. Manual Push (Backup)
```bash
git add CHANGELOG.md package.json
git commit -m "chore(release): v1.2.0"
git push && git push --tags
```

## Example Changelog Output

```markdown
## [1.2.0] - 2026-01-03 (Sprint 6)

### Added
- [Landing Page] Hero section with animations
- [Agent System] New orchestrator workflow

### Fixed
- [API] Timeout issue in authentication
- [KB] Index update race condition

### Documentation
- Updated quick start guide
- Added MCP integration docs
```

## Integration

- **Package Scripts:**
  ```bash
  bun run release:preview    # Preview changes
  bun run release:changelog  # Generate changelog
  bun run release            # Full release
  ```

- **Update Methods:**
  - **NPM Update:** `npm update -g agentic-sdlc`
  - **Source Update:** `python agentic_sdlc/infrastructure/lifecycle/update/updater.py`

- **CI/CD:** Can be triggered in GitHub Actions

- **Publish to NPM:** To publish to NPM, ensure you are logged in using `npm login` then run the release command with the --publish flag.
  ```bash
  python agentic_sdlc/infrastructure/lifecycle/release/release.py release --publish
  ```

#release #versioning #changelog #semver #git-tags

## ⏭️ Next Steps
- **If Release Successful:** Trigger `/housekeeping`
- **If Changelog Updated:** Notify stakeholders via `@REPORTER`

---

## ENFORCEMENT REMINDER
Ensure all tests pass before releasing.
