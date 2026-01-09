# Walkthrough - Non-NPM Update Support

## Overview
Implemented a self-update mechanism using a Python script to allow updating the project directly from GitHub source. This decouples the update process from NPM for source installs.

## Changes

### 1. Update Script
Created `tools/infrastructure/update/updater.py`:
- Implements `ProjectUpdater` class.
- Uses `git` commands (`fetch`, `status`, `pull`) to manage state.
- Provides `--check` flag for non-destructive status checks.

### 2. Documentation
- **README.md:** Added "Installation from Source" and "Keeping Updated" sections.
- **Release Workflow:** Added "Update Methods" section to `.agent/workflows/release.md`.
- **Commit Workflow:** Added "Tool Maintenance" section to `.agent/workflows/commit.md`.

## Verification Results
- Script created successfully.
- Manual verification of script logic (checking git status).
- Documentation reflects the new capabilities.

## Usage
```bash
# Check for updates
python tools/infrastructure/update/updater.py --check

# Perform update
python tools/infrastructure/update/updater.py
```
