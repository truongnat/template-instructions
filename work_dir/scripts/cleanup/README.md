# Project Audit and Cleanup System

A comprehensive Python-based tool for auditing and safely cleaning up the Agentic SDLC project. This system systematically identifies, categorizes, and removes unnecessary files while preserving all critical components.

## Table of Contents

- [Overview](#overview)
- [Installation](#installation)
- [Quick Start](#quick-start)
- [CLI Reference](#cli-reference)
- [Usage Examples](#usage-examples)
- [Backup and Rollback](#backup-and-rollback)
- [Troubleshooting](#troubleshooting)
- [Safety Features](#safety-features)

## Overview

The cleanup system performs the following operations:

- **Audit**: Scans the project and categorizes files into KEEP, REMOVE, CONSOLIDATE, or ARCHIVE
- **Cleanup**: Safely removes unnecessary files with automatic backup
- **Validation**: Verifies package integrity after cleanup (imports, CLI, tests, build)
- **Rollback**: Restores files from backup if needed

### What Gets Cleaned Up

- **Corrupt directories**: Directories with `_corrupt_` suffix
- **Bundled libraries**: `agentic_sdlc/lib/` directory
- **Cache files**: `.brain/`, `.hypothesis/`, `__pycache__/`
- **Duplicate dependencies**: Consolidates `requirements*.txt` into `pyproject.toml`
- **Empty directories**: Removes empty or nearly-empty directories

### What Gets Preserved

All critical components are preserved:
- Core modules: `agentic_sdlc/core/`, `intelligence/`, `infrastructure/`, `orchestration/`
- Configuration: `pyproject.toml`, `package.json`, `Dockerfile`, etc.
- Documentation: `docs/`, `README.md`, `LICENSE`
- Tests: `tests/`, `.kiro/`, `.agent/`
- Scripts: `bin/`, `scripts/`

## Installation

No additional installation required. The cleanup system uses only Python standard library and existing project dependencies.

### Requirements

- Python 3.10+
- Existing Agentic SDLC project

## Quick Start

### 1. Generate Audit Report (Recommended First Step)

```bash
python scripts/cleanup.py --audit-only
```

This generates a detailed report showing what will be kept, removed, consolidated, or archived. Review the report in `docs/CLEANUP-AUDIT-REPORT-{timestamp}.md` before proceeding.

### 2. Dry Run (See What Would Happen)

```bash
python scripts/cleanup.py --dry-run
```

Shows exactly what would be done without making any changes.

### 3. Perform Cleanup

```bash
python scripts/cleanup.py
```

Executes the cleanup with automatic backup. If validation fails, changes are automatically rolled back.

## CLI Reference

### Command Syntax

```bash
python scripts/cleanup.py [OPTIONS]
```

### Options

#### Mode Selection (Mutually Exclusive)

| Flag | Description |
|------|-------------|
| `--audit-only` | Generate audit report without performing cleanup |
| `--dry-run` | Show what would be done without executing changes |
| `--rollback BACKUP_ID` | Restore from a specific backup |
| `--list-backups` | List all available backups |
| *(none)* | Perform cleanup with backup (default mode) |

#### Additional Options

| Flag | Description |
|------|-------------|
| `--no-backup` | Skip backup creation (NOT RECOMMENDED) |
| `--verbose`, `-v` | Enable verbose logging |
| `--project-root PATH` | Specify project root directory (default: current directory) |

### Exit Codes

- `0`: Success
- `1`: Failure (error occurred)
- `130`: Cancelled by user (Ctrl+C)

## Usage Examples

### Example 1: First-Time Audit

```bash
# Generate audit report to see what will be cleaned
python scripts/cleanup.py --audit-only

# Review the report
cat docs/CLEANUP-AUDIT-REPORT-*.md
```

**Output:**
```
=== AUDIT MODE ===
Project root: /path/to/agentic-sdlc

================================================================================
AUDIT SUMMARY
================================================================================
Total files scanned: 5,234
Files to keep: 3,456
Files to remove: 1,523
Files to consolidate: 3
Files to archive: 252

Current size: 120.50 MB
Projected size: 4.80 MB
Reduction: 115.70 MB (96.0%)

Full report: docs/CLEANUP-AUDIT-REPORT-20260131_143022.md
================================================================================
```

### Example 2: Dry Run Before Cleanup

```bash
# See what would happen without making changes
python scripts/cleanup.py --dry-run --verbose
```

**Output:**
```
=== DRY RUN MODE ===
Project root: /path/to/agentic-sdlc
Backup: enabled

Running audit...
Starting cleanup...

================================================================================
DRY RUN RESULTS
================================================================================
DRY RUN - No changes were made

Would remove: 1,523 files
Would free: 115.70 MB
================================================================================
```

### Example 3: Perform Cleanup with Backup

```bash
# Execute cleanup (backup created automatically)
python scripts/cleanup.py
```

**Output:**
```
=== CLEANUP MODE ===
Project root: /path/to/agentic-sdlc
Backup: enabled

Running audit...
Audit report saved to: docs/CLEANUP-AUDIT-REPORT-20260131_143022.md
Starting cleanup...
Creating backup...
Removing files...
Validating...

================================================================================
CLEANUP RESULTS
================================================================================
Cleanup completed successfully!

Files removed: 1,523
Size freed: 115.70 MB
Backup ID: backup_20260131_143022

Validation Results:
  Import check: PASS
  CLI check: PASS
  Test check: PASS
  Build check: PASS

Cleanup summary: docs/CLEANUP-SUMMARY-20260131_143022.md
================================================================================
```

### Example 4: List Available Backups

```bash
python scripts/cleanup.py --list-backups
```

**Output:**
```
================================================================================
AVAILABLE BACKUPS
================================================================================
ID: backup_20260131_143022
  Created: 2026-01-31 14:30:22
  Files: 1,523
  Size: 115.70 MB

ID: backup_20260131_150315
  Created: 2026-01-31 15:03:15
  Files: 1,200
  Size: 98.50 MB

================================================================================
```

### Example 5: Rollback to Previous State

```bash
python scripts/cleanup.py --rollback backup_20260131_143022
```

**Output:**
```
=== ROLLBACK MODE ===
Backup ID: backup_20260131_143022

Backup: backup_20260131_143022
Created: 2026-01-31 14:30:22
Files: 1,523
Size: 115.70 MB

Restore this backup? This will overwrite existing files. (yes/no): yes

Restoring backup...

================================================================================
ROLLBACK RESULTS
================================================================================
Rollback completed successfully!

Files restored: 1,523
================================================================================
```

### Example 6: Cleanup Without Backup (Not Recommended)

```bash
# Only use if you're absolutely sure
python scripts/cleanup.py --no-backup
```

⚠️ **Warning**: This skips backup creation. Only use if you have external backups or are testing in a disposable environment.

### Example 7: Verbose Logging

```bash
# Get detailed logging output
python scripts/cleanup.py --verbose --audit-only
```

Useful for debugging or understanding exactly what the system is doing.

## Backup and Rollback

### How Backups Work

1. **Automatic Creation**: Backups are created automatically before any file removal
2. **Compression**: Files are compressed using tar.gz format
3. **Manifest**: Each backup includes a JSON manifest with file paths and checksums
4. **Storage**: Backups are stored in `.cleanup_backup/` directory

### Backup Structure

```
.cleanup_backup/
├── backup_20260131_143022/
│   ├── manifest.json          # List of all backed up files
│   ├── files.tar.gz           # Compressed archive of files
│   └── metadata.json          # Backup metadata
└── backup_20260131_150315/
    ├── manifest.json
    ├── files.tar.gz
    └── metadata.json
```

### Manifest Format

```json
{
  "backup_id": "backup_20260131_143022",
  "timestamp": "2026-01-31T14:30:22Z",
  "files": [
    {
      "original_path": "agentic_sdlc/lib/some_file.py",
      "backup_path": "files.tar.gz:agentic_sdlc/lib/some_file.py",
      "size": 1024,
      "checksum": "sha256:abc123..."
    }
  ],
  "total_size": 125829120,
  "total_files": 1523
}
```

### When to Rollback

Rollback if:
- Validation fails (automatic rollback)
- Package doesn't work as expected after cleanup
- You need to recover specific files
- You want to undo the cleanup for any reason

### Rollback Process

1. **List backups**: `python scripts/cleanup.py --list-backups`
2. **Choose backup**: Identify the backup ID you want to restore
3. **Execute rollback**: `python scripts/cleanup.py --rollback <backup_id>`
4. **Confirm**: Type 'yes' when prompted
5. **Verify**: Check that files are restored correctly

### Automatic Rollback

The system automatically rolls back if validation fails:

```
Validation failed - cleanup was rolled back
```

This ensures your project remains functional even if something goes wrong.

## Troubleshooting

### Issue: "Backup not found"

**Problem**: Trying to rollback to a non-existent backup

**Solution**:
```bash
# List available backups
python scripts/cleanup.py --list-backups

# Use correct backup ID
python scripts/cleanup.py --rollback backup_20260131_143022
```

### Issue: "Permission denied" errors

**Problem**: Insufficient permissions to read/write files

**Solution**:
```bash
# Check file permissions
ls -la agentic_sdlc/

# Run with appropriate permissions
sudo python scripts/cleanup.py  # Use with caution
```

### Issue: Validation fails after cleanup

**Problem**: Import, CLI, test, or build validation fails

**What happens**: System automatically rolls back changes

**Solution**:
1. Check the error messages in the output
2. Review the audit report to see what was removed
3. If a critical file was incorrectly categorized, report it as a bug
4. The rollback ensures your project is still functional

### Issue: "Disk full" during backup

**Problem**: Not enough disk space for backup

**Solution**:
```bash
# Check available disk space
df -h

# Free up space or use external storage
# Then retry cleanup
python scripts/cleanup.py
```

### Issue: Cleanup is too slow

**Problem**: Large project takes a long time to scan

**Solution**:
```bash
# Use --verbose to see progress
python scripts/cleanup.py --verbose

# Or run audit first to see scope
python scripts/cleanup.py --audit-only
```

### Issue: Want to exclude specific files from removal

**Problem**: A file is being removed that you want to keep

**Solution**:
1. Run `--audit-only` to see what will be removed
2. If a file is incorrectly categorized, modify the categorization rules in `scripts/cleanup/categorizer.py`
3. Add the file/directory to the CRITICAL_COMPONENTS list

### Issue: Rollback fails for some files

**Problem**: Some files cannot be restored

**What happens**: System reports which files failed

**Solution**:
```bash
# Check the error messages
# Manually restore from backup if needed
cd .cleanup_backup/backup_20260131_143022/
tar -xzf files.tar.gz
# Copy specific files manually
```

### Issue: Need to recover a single file

**Problem**: Don't want to rollback everything, just one file

**Solution**:
```bash
# Extract specific file from backup
cd .cleanup_backup/backup_20260131_143022/
tar -xzf files.tar.gz path/to/specific/file.py
cp path/to/specific/file.py ../../path/to/specific/file.py
```

### Issue: Cleanup removes too much or too little

**Problem**: Categorization rules don't match your needs

**Solution**:
1. Review `scripts/cleanup/categorizer.py`
2. Modify the categorization rules:
   - Add to `CRITICAL_COMPONENTS` to preserve files
   - Add to `REMOVE_PATTERNS` to remove files
   - Adjust `CACHE_PATTERNS` for cache handling
3. Run `--audit-only` to verify changes
4. Run `--dry-run` to test without making changes

### Getting Help

If you encounter issues not covered here:

1. **Check logs**: Use `--verbose` flag for detailed logging
2. **Review reports**: Check audit and cleanup reports in `docs/`
3. **Verify backups**: Ensure backups exist before cleanup
4. **Test in isolation**: Use `--dry-run` to test safely
5. **Report bugs**: If you find a bug, report it with:
   - Command used
   - Error messages
   - Relevant log output
   - Project state (before/after)

## Safety Features

The cleanup system includes multiple safety mechanisms:

### 1. Mandatory Backup

- Backups are created automatically before any removal
- Can only be disabled with explicit `--no-backup` flag
- Backups include checksums for integrity verification

### 2. Dry Run Mode

- Test cleanup without making changes
- See exactly what would be removed
- Verify size reduction estimates

### 3. Critical Component Protection

- Hardcoded list of critical files/directories
- Never removes core functionality
- Preserves all configuration and documentation

### 4. Validation Testing

After cleanup, the system validates:
- **Imports**: All critical modules can be imported
- **CLI**: All entry points are executable
- **Tests**: Test suite passes
- **Build**: Package can be built successfully

### 5. Automatic Rollback

- If validation fails, changes are automatically rolled back
- Ensures project remains functional
- No manual intervention required

### 6. Audit Reports

- Detailed reports before cleanup
- Shows exactly what will be done
- Includes size impact calculations

### 7. Comprehensive Logging

- All operations are logged
- Errors are captured and reported
- Verbose mode for debugging

## Best Practices

1. **Always audit first**: Run `--audit-only` before cleanup
2. **Use dry run**: Test with `--dry-run` before actual cleanup
3. **Keep backups**: Don't use `--no-backup` unless absolutely necessary
4. **Review reports**: Check audit reports carefully
5. **Test after cleanup**: Verify your project works after cleanup
6. **Keep backup directory**: Don't delete `.cleanup_backup/` immediately
7. **Version control**: Commit changes before running cleanup
8. **Document changes**: Keep cleanup reports for reference

## Advanced Usage

### Custom Project Root

```bash
# Cleanup a different project
python scripts/cleanup.py --project-root /path/to/other/project
```

### Scripted Cleanup

```bash
#!/bin/bash
# Automated cleanup script

# Audit
python scripts/cleanup.py --audit-only

# Dry run
python scripts/cleanup.py --dry-run

# Cleanup if dry run looks good
python scripts/cleanup.py

# Verify
python -c "import agentic_sdlc"
asdlc --help
pytest tests/
```

### Integration with CI/CD

```yaml
# Example GitHub Actions workflow
- name: Audit project size
  run: python scripts/cleanup.py --audit-only

- name: Check cleanup impact
  run: python scripts/cleanup.py --dry-run
```

## Files and Directories

### Generated Files

- `docs/CLEANUP-AUDIT-REPORT-{timestamp}.md`: Audit report
- `docs/CLEANUP-SUMMARY-{timestamp}.md`: Cleanup summary
- `.cleanup_backup/`: Backup storage directory

### Source Files

- `scripts/cleanup.py`: CLI entry point
- `scripts/cleanup/`: Cleanup system modules
  - `audit.py`: Audit engine
  - `backup.py`: Backup manager
  - `categorizer.py`: File categorizer
  - `cleanup.py`: Cleanup engine
  - `scanner.py`: File scanner
  - `validator.py`: Validation engine
  - `reporter.py`: Report generator
  - `models.py`: Data models
  - `logger.py`: Logging configuration

## Requirements Addressed

This cleanup system addresses the following requirements:

- **13.1**: Reusable cleanup script with comprehensive functionality
- **13.2**: Command-line flags for all operations
- **13.3**: Dry-run mode for safe testing
- **13.4**: Audit-only mode for analysis
- **13.5**: Comprehensive logging with multiple levels

## License

This cleanup system is part of the Agentic SDLC project and follows the same license.
