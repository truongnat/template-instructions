# Root Directory Organization

## Overview
This document describes the organization of files in the project root and `.kiro/` directories.

## Root Level Files

### Core Project Files
- `README.md` - Project overview and quick start
- `LICENSE` - MIT License
- `pyproject.toml` - Python project configuration
- `setup.py` - Package setup (if needed)
- `MANIFEST.in` - Package manifest

### Configuration Files
- `.env` - Environment variables (local)
- `.env.template` - Environment variables template
- `.gitignore` - Git ignore rules
- `.dockerignore` - Docker ignore rules
- `agentic.yaml` - Application configuration
- `pytest.ini` - Pytest configuration
- `turbo.json` - Turbo configuration (if using)

### Docker Files
- `Dockerfile` - Production Docker image
- `Dockerfile.dev` - Development Docker image
- `docker-compose.yml` - Docker Compose configuration

### Package Files
- `requirements.txt` - Python dependencies
- `requirements-dev.txt` - Development dependencies
- `package.json` - Node.js dependencies (if applicable)
- `bun.lock` - Bun lock file (if using Bun)

### Build & Distribution
- `agentic_sdlc.egg-info/` - Package metadata
- `build/` - Build artifacts
- `dist/` - Distribution packages

### Version & Release
- `VERSION` - Version file
- `RELEASE_v*.md` - Release notes (archived in `.kiro/docs/verification/`)

### Development Tools
- `.venv/` - Virtual environment
- `.vscode/` - VS Code settings
- `.mypy_cache/` - MyPy cache
- `.pytest_cache/` - Pytest cache
- `.kiro/` - Kiro IDE configuration

### Temporary/Generated
- `.coverage` - Coverage report
- `.cursorrules` - Cursor rules
- `.agent` - Agent configuration (symlink)
- `.brain-improvements.json` - Brain improvements

## `.kiro/` Directory Structure

### `.kiro/docs/`
Organized documentation and reports:

#### `.kiro/docs/verification/`
- Verification reports
- Validation reports
- Test summaries
- Checkpoint reports
- Release summaries

#### `.kiro/docs/guides/`
- Contributing guidelines
- Docker guide
- Migration guides
- Security documentation

#### `.kiro/docs/reports/`
- Analysis reports
- Performance reports
- Dependency reports

## Source Code Structure

### `src/agentic_sdlc/`
Main package source code

### `tests/`
Test suite

### `docs/`
Project documentation
- `docs/diagrams/` - Architecture diagrams
- `docs/ARCHITECTURE.md` - Architecture documentation

### `examples/`
Example scripts and usage

### `scripts/`
Utility scripts

### `config/`
Configuration templates

### `models/`
Data models and schemas

### `monitoring/`
Monitoring and logging

### `security/`
Security utilities

### `utils/`
Shared utilities

### `resources/`
Resource files

### `data/`
Data files and datasets

### `logs/`
Application logs

### `states/`
State files

## Cleanup Guidelines

### Files to Keep in Root
- Core project files (README, LICENSE, pyproject.toml)
- Configuration files (.env, .gitignore, etc.)
- Docker files (Dockerfile, docker-compose.yml)
- Package files (requirements.txt, package.json)

### Files to Archive
- Verification reports → `.kiro/docs/verification/`
- Guides and documentation → `.kiro/docs/guides/`
- Analysis reports → `.kiro/docs/reports/`

### Files to Remove
- Temporary test outputs
- Build artifacts (after distribution)
- Cache files (auto-generated)
- Old migration logs
- Comparison reports

## Best Practices

1. **Keep root clean** - Only essential files
2. **Archive reports** - Move to `.kiro/docs/`
3. **Use directories** - Group related files
4. **Document structure** - Update this file when changing
5. **Ignore generated** - Add to `.gitignore`

## Related Files

- `.gitignore` - Files to ignore in version control
- `.dockerignore` - Files to ignore in Docker builds
- `MANIFEST.in` - Files to include in distribution
