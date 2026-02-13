# Git Hooks for Automatic Versioning

This directory contains git hook templates for automatic version management.

## Installation

Run the installation script from the project root:

```bash
./scripts/install_hooks.sh
```

## Available Hooks

### post-commit

Automatically bumps version and creates tags based on commit message format.

**Supported formats:**
- `feat: ...` → minor bump (3.0.0 → 3.1.0)
- `fix: ...` → patch bump (3.0.0 → 3.0.1)  
- `BREAKING CHANGE: ...` → major bump (3.0.0 → 4.0.0)

**What it does:**
1. Analyzes your commit message
2. Bumps version in `VERSION` and `pyproject.toml`
3. Amends the commit to include version changes
4. Creates a git tag (e.g., `v3.1.0`)

**After commit:**
```bash
git push && git push --tags
```

## Disabling Hooks

To temporarily disable the hook:

```bash
mv .git/hooks/post-commit .git/hooks/post-commit.disabled
```

To re-enable:

```bash
mv .git/hooks/post-commit.disabled .git/hooks/post-commit
```

## Manual Version Bump

You can also run the version bump script manually:

```bash
python3 scripts/version_bump.py "feat: add new feature"
```
