# Migration Guide

This guide helps you upgrade between major versions of the Agentic SDLC Kit.

## Overview

The Agentic SDLC Kit follows [Semantic Versioning](https://semver.org/):
- **MAJOR** version (X.0.0): Breaking changes that require migration
- **MINOR** version (0.X.0): New features, backward compatible
- **PATCH** version (0.0.X): Bug fixes, backward compatible

## Current Version: 2.7.5

### Checking Your Version

```bash
# Using CLI
asdlc --version

# Using Python
python -c "from agentic_sdlc import __version__; print(__version__)"
```

## Migration Paths

### From 2.x to 3.x (Future)

**Status:** Not yet released

When version 3.0 is released, this section will document:
- Breaking changes introduced
- Required code modifications
- Configuration updates
- Deprecated features removed
- Step-by-step upgrade instructions

### From 1.x to 2.x

**Released:** 2026-01-16

#### Breaking Changes

1. **CLI Restructure**
   - **Old:** Multiple CLI entry points scattered across the project
   - **New:** Unified CLI with `asdlc` command
   - **Migration:** Update all scripts to use `asdlc` instead of direct Python script calls

2. **Module Reorganization**
   - **Old:** `tools/` directory with scattered utilities
   - **New:** `agentic_sdlc/` package structure
   - **Migration:** Update imports from `tools.*` to `agentic_sdlc.*`

3. **Knowledge Base System**
   - **Old:** File-based knowledge base
   - **New:** Neo4j graph database integration
   - **Migration:** Run migration script to transfer KB data to Neo4j

#### Upgrade Steps

1. **Backup your project:**
   ```bash
   # Create a backup of your current project
   cp -r your-project your-project-backup
   ```

2. **Update installation:**
   ```bash
   # Uninstall old version
   pip uninstall agentic-sdlc
   
   # Install new version
   pip install git+https://github.com/truongnat/agentic-sdlc.git
   ```

3. **Update CLI commands:**
   ```bash
   # Old
   python tools/workflows/cycle.py
   
   # New
   asdlc workflow cycle
   ```

4. **Update imports in custom scripts:**
   ```python
   # Old
   from tools.kb.search import search_kb
   
   # New
   from agentic_sdlc.infrastructure.kb import search_kb
   ```

5. **Migrate knowledge base (if using):**
   ```bash
   # Run KB migration script
   asdlc brain migrate-kb
   ```

6. **Test your workflows:**
   ```bash
   # Run health check
   asdlc health
   
   # Test a simple workflow
   asdlc workflow cycle "Test migration"
   ```

#### Deprecated Features

- File-based knowledge base (removed in 2.0)
- Direct Python script execution for workflows (use CLI instead)
- Legacy `tools/` directory structure (moved to `agentic_sdlc/`)

### From 0.x to 1.x

**Released:** 2026-01-01

This was the initial public release. No migration path available from pre-1.0 versions.

## Rollback Instructions

If you encounter issues after upgrading, you can rollback to a previous version:

```bash
# Rollback to specific version
pip install git+https://github.com/truongnat/agentic-sdlc.git@v2.7.5

# Or restore from backup
rm -rf your-project
cp -r your-project-backup your-project
```

## Getting Help

If you encounter migration issues:

1. **Check the documentation:** [docs/](docs/)
2. **Search existing issues:** [GitHub Issues](https://github.com/truongnat/agentic-sdlc/issues)
3. **Create a new issue:** Include:
   - Current version
   - Target version
   - Error messages
   - Steps to reproduce

## Version History

| Version | Release Date | Type | Notes |
|---------|-------------|------|-------|
| 2.7.5 | 2026-02-10 | Patch | Current version |
| 2.7.3 | 2026-01-31 | Patch | Module import standardization |
| 2.7.1 | 2026-01-31 | Patch | Project rename to sdlc-kit |
| 2.7.0 | 2026-01-31 | Minor | PyPI publishing support |
| 2.0.0 | 2026-01-16 | Major | Unified CLI and package structure |
| 1.0.0 | 2026-01-01 | Major | Initial public release |

## Best Practices

1. **Always backup before upgrading** to a major version
2. **Read the CHANGELOG** for detailed changes
3. **Test in a development environment** before upgrading production
4. **Update dependencies** after upgrading
5. **Run health checks** after migration
6. **Review deprecated features** and plan replacements

## Future Breaking Changes

This section will be updated as breaking changes are planned for future releases.

Currently, no breaking changes are planned for the next minor version (2.8.0).
