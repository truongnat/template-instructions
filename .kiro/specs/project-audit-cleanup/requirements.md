# Requirements Document

## Introduction

This specification defines the requirements for a comprehensive project audit and cleanup system for the Agentic SDLC framework (version 2.7.5). The system will systematically identify, categorize, and safely remove or consolidate duplicate, corrupt, bloated, and unnecessary files and directories while preserving all critical project components. The cleanup will reduce package size from ~120MB to ~5MB, eliminate corrupt directories, consolidate dependency management, and improve overall project structure and maintainability.

## Glossary

- **Cleanup_System**: The automated system that performs audit, categorization, and safe removal of files
- **Corrupt_Directory**: A directory with "_corrupt_" suffix indicating damaged or duplicate build artifacts
- **Bloat_File**: A file or directory that unnecessarily increases package size without providing runtime value
- **Critical_Component**: A file or directory essential for package functionality that must be preserved
- **Safe_Removal**: Deletion process that includes backup, validation, and rollback capability
- **Dependency_Consolidation**: Process of merging multiple requirements files into pyproject.toml
- **Cache_Directory**: A directory containing regenerable data (.brain/, .hypothesis/, __pycache__)
- **Package_Size**: Total size of distributed package excluding development dependencies
- **Audit_Report**: Document listing all files categorized by action (keep/remove/consolidate)
- **Validation_Test**: Automated test ensuring critical functionality remains after cleanup

## Requirements

### Requirement 1: Corrupt Directory Removal

**User Story:** As a project maintainer, I want to safely remove all corrupt and duplicate directories, so that the project structure is clean and build artifacts are not duplicated.

#### Acceptance Criteria

1. WHEN the Cleanup_System scans the project root, THE Cleanup_System SHALL identify all directories with "_corrupt_" suffix
2. WHEN a corrupt directory is identified, THE Cleanup_System SHALL verify it is not referenced by any active code
3. WHEN verification passes, THE Cleanup_System SHALL create a backup archive before removal
4. THE Cleanup_System SHALL remove the following corrupt directories: agentic_sdlc.egg-info_corrupt_20260131/, agentic_sdlc.egg-info.trash_corrupt_20260131/, build_corrupt_20260131/
5. IF removal fails, THEN THE Cleanup_System SHALL restore from backup and log the error

### Requirement 2: Bundled Library Cleanup

**User Story:** As a package maintainer, I want to remove the lib/ directory from the source package, so that dependencies are managed through pip/venv and not bundled in source.

#### Acceptance Criteria

1. WHEN the Cleanup_System scans agentic_sdlc/, THE Cleanup_System SHALL identify the lib/ directory
2. THE Cleanup_System SHALL verify lib/ is listed in .gitignore
3. THE Cleanup_System SHALL verify no import statements reference agentic_sdlc/lib/ directly
4. WHEN verification passes, THE Cleanup_System SHALL remove agentic_sdlc/lib/ directory
5. THE Cleanup_System SHALL update pyproject.toml to exclude lib/ from package distribution if not already excluded

### Requirement 3: Cache Directory Management

**User Story:** As a developer, I want to clean up cache directories while preserving their structure, so that regenerable data is removed but the system can recreate caches as needed.

#### Acceptance Criteria

1. WHEN the Cleanup_System processes .brain/ directories, THE Cleanup_System SHALL preserve the directory structure
2. THE Cleanup_System SHALL archive old learning data older than 30 days to .brain/archive/
3. WHEN the Cleanup_System processes .hypothesis/ directories, THE Cleanup_System SHALL remove all constant files
4. THE Cleanup_System SHALL preserve .hypothesis/examples/ directory structure for regeneration
5. WHEN the Cleanup_System processes __pycache__/ directories, THE Cleanup_System SHALL remove all .pyc and .pyo files

### Requirement 4: Dependency Consolidation

**User Story:** As a package maintainer, I want to consolidate all dependency declarations into pyproject.toml, so that dependency management is centralized and consistent.

#### Acceptance Criteria

1. WHEN the Cleanup_System scans for requirements files, THE Cleanup_System SHALL identify all requirements*.txt files
2. THE Cleanup_System SHALL parse agentic_sdlc/requirements_tools.txt and extract dependencies
3. THE Cleanup_System SHALL merge extracted dependencies into pyproject.toml [project.optional-dependencies] under appropriate groups
4. WHEN all dependencies are merged, THE Cleanup_System SHALL remove redundant requirements*.txt files
5. THE Cleanup_System SHALL validate that no duplicate dependencies exist across dependency groups

### Requirement 5: Package Size Reduction

**User Story:** As a package distributor, I want to reduce the package size from ~120MB to ~5MB, so that installation is faster and storage requirements are minimal.

#### Acceptance Criteria

1. THE Cleanup_System SHALL calculate current package size before cleanup
2. THE Cleanup_System SHALL identify all files contributing to package bloat (lib/, cache, examples)
3. WHEN cleanup is complete, THE Cleanup_System SHALL calculate final package size
4. THE Cleanup_System SHALL verify final package size is less than 10MB
5. THE Cleanup_System SHALL generate a size reduction report showing before/after comparison

### Requirement 6: Critical Component Preservation

**User Story:** As a developer, I want to ensure all critical components are preserved during cleanup, so that the package remains fully functional after cleanup.

#### Acceptance Criteria

1. THE Cleanup_System SHALL preserve all directories in agentic_sdlc/core/, agentic_sdlc/intelligence/, agentic_sdlc/infrastructure/, agentic_sdlc/orchestration/
2. THE Cleanup_System SHALL preserve agentic_sdlc/defaults/ directory excluding projects/ subdirectory
3. THE Cleanup_System SHALL preserve all files in docs/, .agent/, .kiro/, tests/, bin/, scripts/
4. THE Cleanup_System SHALL preserve all root configuration files (pyproject.toml, package.json, docker-compose.yml, Dockerfile, .gitignore, .dockerignore)
5. THE Cleanup_System SHALL verify all preserved files are readable and not corrupted

### Requirement 7: Safe Removal with Backup

**User Story:** As a project maintainer, I want all removals to be backed up before deletion, so that I can recover if something goes wrong.

#### Acceptance Criteria

1. WHEN the Cleanup_System removes any file or directory, THE Cleanup_System SHALL create a timestamped backup in .cleanup_backup/
2. THE Cleanup_System SHALL compress backups using tar.gz format
3. THE Cleanup_System SHALL maintain a manifest file listing all backed up items with original paths
4. THE Cleanup_System SHALL provide a rollback command that restores from backup
5. WHEN rollback is executed, THE Cleanup_System SHALL restore all files to their original locations

### Requirement 8: Audit Report Generation

**User Story:** As a project maintainer, I want a detailed audit report before cleanup, so that I can review what will be kept, removed, or consolidated.

#### Acceptance Criteria

1. WHEN the Cleanup_System performs an audit, THE Cleanup_System SHALL generate a markdown report
2. THE Cleanup_System SHALL categorize all files into: KEEP, REMOVE, CONSOLIDATE, ARCHIVE
3. THE Cleanup_System SHALL include file sizes and total size impact for each category
4. THE Cleanup_System SHALL list all dependencies to be consolidated with source and destination
5. THE Cleanup_System SHALL save the report to docs/CLEANUP-AUDIT-REPORT-{timestamp}.md

### Requirement 9: Validation Testing

**User Story:** As a developer, I want automated validation tests after cleanup, so that I can verify the package still works correctly.

#### Acceptance Criteria

1. WHEN cleanup is complete, THE Cleanup_System SHALL run all existing unit tests
2. THE Cleanup_System SHALL verify all CLI entry points (agentic, agentic-sdlc, asdlc) are executable
3. THE Cleanup_System SHALL verify package can be imported with "import agentic_sdlc"
4. THE Cleanup_System SHALL verify all critical modules can be imported individually
5. IF any validation fails, THEN THE Cleanup_System SHALL halt and recommend rollback

### Requirement 10: Node Modules Management

**User Story:** As a project maintainer, I want to verify node_modules/ is properly excluded from version control and package distribution, so that JavaScript dependencies don't bloat the Python package.

#### Acceptance Criteria

1. THE Cleanup_System SHALL verify node_modules/ is listed in .gitignore
2. THE Cleanup_System SHALL verify node_modules/ is listed in .dockerignore
3. THE Cleanup_System SHALL verify node_modules/ is excluded from package distribution in pyproject.toml
4. WHEN node_modules/ exists, THE Cleanup_System SHALL calculate its size and report it
5. THE Cleanup_System SHALL recommend removing node_modules/ if it exists in the repository

### Requirement 11: Empty Directory Cleanup

**User Story:** As a project maintainer, I want to remove empty or nearly-empty directories, so that the project structure is clean and organized.

#### Acceptance Criteria

1. WHEN the Cleanup_System scans the project, THE Cleanup_System SHALL identify all empty directories
2. THE Cleanup_System SHALL identify directories containing only .DS_Store or .gitkeep files
3. THE Cleanup_System SHALL exclude critical empty directories (logs/, states/, data/) from removal
4. WHEN a non-critical empty directory is found, THE Cleanup_System SHALL remove it
5. THE Cleanup_System SHALL log all removed empty directories in the audit report

### Requirement 12: Package Manifest Update

**User Story:** As a package maintainer, I want pyproject.toml and MANIFEST.in updated to reflect cleanup changes, so that package distribution excludes removed items.

#### Acceptance Criteria

1. WHEN cleanup is complete, THE Cleanup_System SHALL update pyproject.toml [tool.setuptools.package-data] to exclude removed directories
2. THE Cleanup_System SHALL verify MANIFEST.in excludes lib/, cache directories, and example projects
3. THE Cleanup_System SHALL add explicit exclude patterns for __pycache__, *.pyc, *.pyo, .DS_Store
4. THE Cleanup_System SHALL validate pyproject.toml syntax after updates
5. THE Cleanup_System SHALL test package build with "python -m build" to verify exclusions work

### Requirement 13: Cleanup Script Creation

**User Story:** As a developer, I want reusable cleanup scripts, so that I can run cleanup operations safely and repeatedly.

#### Acceptance Criteria

1. THE Cleanup_System SHALL create a Python script scripts/cleanup.py with all cleanup logic
2. THE Cleanup_System SHALL provide command-line flags: --audit-only, --backup, --rollback, --dry-run
3. WHEN --dry-run is used, THE Cleanup_System SHALL report actions without executing them
4. WHEN --audit-only is used, THE Cleanup_System SHALL generate audit report without cleanup
5. THE Cleanup_System SHALL include comprehensive logging with INFO, WARNING, and ERROR levels

### Requirement 14: Documentation Update

**User Story:** As a project maintainer, I want documentation updated to reflect cleanup changes, so that developers understand the new project structure.

#### Acceptance Criteria

1. WHEN cleanup is complete, THE Cleanup_System SHALL update README.md to reflect new package size
2. THE Cleanup_System SHALL create docs/CLEANUP-SUMMARY.md documenting what was removed and why
3. THE Cleanup_System SHALL update CONTRIBUTING.md with dependency management guidelines
4. THE Cleanup_System SHALL document the backup and rollback process in docs/CLEANUP-SUMMARY.md
5. THE Cleanup_System SHALL update .gitignore with any new patterns for excluded files
