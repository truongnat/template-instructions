# Implementation Plan - Non-NPM Update Support

## Goal
Enable users to update the project and its tools directly from the GitHub repository without relying on `npm update`. This supports users who install via `git clone`.

## Proposed Changes

### 1. New Utility Script
**File:** `tools/infrastructure/update/updater.py`
- Detecting git repository status.
- Checking for updates (fetch + status).
- Pulling updates.
- Suggesting dependency updates.

### 2. Documentation Updates
**File:** `README.md`
- Add "Installation from Source" section.
- Add "Keeping Updated" section with usage instructions for `updater.py`.

**File:** `.agent/workflows/release.md`
- detailed "Update Methods" to include the source update option.

**File:** `.agent/workflows/commit.md`
- Add a "Tool Maintenance" pre-requisite to ensure contributors are on the latest version.

## Verification
- Run `updater.py --check` to verify it detects the git status.
- Verify documentation renders correctly.
