# Implementation Plan: Project Audit and Cleanup System

## Overview

This implementation plan breaks down the project audit and cleanup system into discrete, incremental tasks. The approach follows a bottom-up strategy: building core utilities first, then services, then engines, and finally the CLI interface. Each task includes validation through tests to ensure correctness at every step.

## Tasks

- [x] 1. Set up project structure and core data models
  - Create `scripts/cleanup/` directory structure
  - Define data models in `scripts/cleanup/models.py` (FileInfo, DirectoryInfo, BackupInfo, etc.)
  - Create `scripts/cleanup/__init__.py` with package exports
  - Set up logging configuration in `scripts/cleanup/logger.py`
  - _Requirements: All requirements (foundational)_

- [x] 2. Implement File Scanner service
  - [x] 2.1 Create FileScanner class in `scripts/cleanup/scanner.py`
    - Implement recursive directory scanning
    - Implement file metadata collection (size, mtime)
    - Implement directory size calculation
    - Add exclude pattern support
    - _Requirements: 1.1, 5.1, 5.2, 11.1_
  
  - [x] 2.2 Write property test for file scanning
    - **Property 11: Requirements File Pattern Matching**
    - **Validates: Requirements 4.1**
  
  - [x] 2.3 Write unit tests for FileScanner
    - Test scanning with various directory structures
    - Test exclude patterns
    - Test size calculation accuracy
    - _Requirements: 1.1, 5.1_

- [-] 3. Implement File Categorizer service
  - [x] 3.1 Create FileCategorizer class in `scripts/cleanup/categorizer.py`
    - Implement categorization rules (KEEP/REMOVE/CONSOLIDATE/ARCHIVE)
    - Implement critical component detection
    - Implement corrupt directory detection
    - Implement cache file detection
    - Implement empty directory detection
    - _Requirements: 1.1, 1.2, 6.1, 6.2, 6.3, 8.2, 11.1, 11.2_
  
  - [x] 3.2 Write property test for critical component preservation
    - **Property 2: Critical Component Preservation**
    - **Validates: Requirements 6.1, 6.2, 6.3, 6.5**
  
  - [x] 3.3 Write property test for corrupt directory identification
    - **Property 6: Corrupt Directory Pattern Matching**
    - **Validates: Requirements 1.1, 1.2**
  
  - [x] 3.4 Write property test for empty directory identification
    - **Property 12: Empty Directory Identification**
    - **Validates: Requirements 11.1, 11.2, 11.3**
  
  - [x] 3.5 Write property test for audit categorization completeness
    - **Property 9: Audit Categorization Completeness**
    - **Validates: Requirements 8.2**
  
  - [x] 3.6 Write unit tests for FileCategorizer
    - Test specific file categorizations
    - Test critical component list
    - Test edge cases (symlinks, special files)
    - _Requirements: 6.1, 6.2, 6.3, 6.4_

- [x] 4. Implement Backup Manager service
  - [x] 4.1 Create BackupManager class in `scripts/cleanup/backup.py`
    - Implement backup directory creation
    - Implement tar.gz compression
    - Implement manifest generation (JSON format)
    - Implement backup listing
    - Implement restore functionality
    - _Requirements: 7.1, 7.2, 7.3, 7.4, 7.5_
  
  - [x] 4.2 Write property test for backup and restore round trip
    - **Property 1: Backup and Restore Round Trip**
    - **Validates: Requirements 7.1, 7.2, 7.3, 7.4, 7.5**
  
  - [x] 4.3 Write property test for manifest consistency
    - **Property 8: Manifest and Archive Consistency**
    - **Validates: Requirements 7.3**
  
  - [x] 4.4 Write unit tests for BackupManager
    - Test backup creation with known files
    - Test manifest format
    - Test restore with known backup
    - Test error handling (disk full, permission denied)
    - _Requirements: 7.1, 7.2, 7.3, 7.5_

- [x] 5. Checkpoint - Ensure core services work
  - Ensure all tests pass, ask the user if questions arise.

- [x] 6. Implement Dependency Consolidator service
  - [x] 6.1 Create DependencyConsolidator class in `scripts/cleanup/dependencies.py`
    - Implement requirements.txt parser
    - Implement pyproject.toml reader/writer (using toml library)
    - Implement dependency merging logic
    - Implement duplicate detection
    - Implement pyproject.toml validation
    - _Requirements: 4.1, 4.2, 4.3, 4.4, 4.5_
  
  - [x] 6.2 Write property test for dependency consolidation idempotence
    - **Property 4: Dependency Consolidation Idempotence**
    - **Validates: Requirements 4.3, 4.5**
  
  - [x] 6.3 Write property test for configuration update validity
    - **Property 15: Configuration Update Validity**
    - **Validates: Requirements 12.4**
  
  - [x] 6.4 Write unit tests for DependencyConsolidator
    - Test parsing various requirements.txt formats
    - Test merging into pyproject.toml
    - Test duplicate detection
    - Test version conflict detection
    - _Requirements: 4.2, 4.3, 4.5_

- [x] 7. Implement Validator service
  - [x] 7.1 Create Validator class in `scripts/cleanup/validator.py`
    - Implement import validation (subprocess: python -c "import X")
    - Implement CLI entry point validation (subprocess: asdlc --help)
    - Implement test suite execution (subprocess: pytest)
    - Implement package build validation (subprocess: python -m build)
    - Implement size validation
    - _Requirements: 9.1, 9.2, 9.3, 9.4, 9.5, 5.4_
  
  - [x] 7.2 Write property test for validation triggers rollback
    - **Property 5: Validation Triggers Rollback**
    - **Validates: Requirements 9.5**
  
  - [x] 7.3 Write unit tests for Validator
    - Test import validation with mock imports
    - Test CLI validation with mock commands
    - Test validation failure detection
    - _Requirements: 9.1, 9.2, 9.3, 9.4_

- [x] 8. Implement Audit Engine
  - [x] 8.1 Create AuditEngine class in `scripts/cleanup/audit.py`
    - Integrate FileScanner and FileCategorizer
    - Implement project inventory creation
    - Implement size impact calculation
    - Implement audit report generation (markdown format)
    - _Requirements: 8.1, 8.2, 8.3, 8.4, 8.5, 5.1, 5.2, 5.5_
  
  - [x] 8.2 Write unit tests for AuditEngine
    - Test audit report generation with mock data
    - Test size impact calculations
    - Test report markdown formatting
    - _Requirements: 8.1, 8.3, 8.5_

- [x] 9. Implement Cleanup Engine
  - [x] 9.1 Create CleanupEngine class in `scripts/cleanup/cleanup.py`
    - Integrate BackupManager, DependencyConsolidator, and Validator
    - Implement cleanup sequence (backup → remove → consolidate → validate)
    - Implement file removal with backup
    - Implement cache archival
    - Implement empty directory removal
    - Implement automatic rollback on validation failure
    - _Requirements: 1.3, 1.4, 1.5, 2.4, 3.1, 3.2, 3.3, 3.5, 9.5, 11.4_
  
  - [x] 9.2 Write property test for size reduction accuracy
    - **Property 3: Size Reduction Accuracy**
    - **Validates: Requirements 5.1, 5.2, 5.3, 5.5**
  
  - [x] 9.3 Write property test for cache directory structure preservation
    - **Property 7: Cache Directory Structure Preservation**
    - **Validates: Requirements 3.1, 3.4**
  
  - [x] 9.4 Write property test for file age-based archival
    - **Property 13: File Age-Based Archival**
    - **Validates: Requirements 3.2**
  
  - [x] 9.5 Write unit tests for CleanupEngine
    - Test cleanup sequence with mock data
    - Test rollback on validation failure
    - Test error handling during removal
    - _Requirements: 1.5, 9.5_

- [x] 10. Checkpoint - Ensure engines work end-to-end
  - Ensure all tests pass, ask the user if questions arise.

- [x] 11. Implement Report Generator
  - [x] 11.1 Create ReportGenerator class in `scripts/cleanup/reporter.py`
    - Implement audit report markdown generation
    - Implement cleanup summary markdown generation
    - Implement report saving to docs/
    - Add size formatting utilities (bytes to MB)
    - Add timestamp formatting
    - _Requirements: 8.1, 8.2, 8.3, 8.4, 8.5, 14.2_
  
  - [x] 11.2 Write unit tests for ReportGenerator
    - Test report markdown formatting
    - Test file saving
    - Test timestamp formatting
    - _Requirements: 8.1, 8.5_

- [-] 12. Implement CLI interface
  - [x] 12.1 Create CLI entry point in `scripts/cleanup.py`
    - Implement argument parsing (argparse)
    - Implement --audit-only flag
    - Implement --dry-run flag
    - Implement --backup flag
    - Implement --rollback flag
    - Implement --verbose flag
    - Wire up AuditEngine, CleanupEngine, and BackupManager
    - _Requirements: 13.1, 13.2, 13.3, 13.4, 13.5_
  
  - [x] 12.2 Write property test for dry run safety
    - **Property 10: Dry Run Makes No Changes**
    - **Validates: Requirements 13.3**
  
  - [x] 12.3 Write unit tests for CLI
    - Test argument parsing
    - Test --audit-only mode
    - Test --dry-run mode
    - Test --rollback mode
    - _Requirements: 13.2, 13.3, 13.4_

- [x] 13. Implement package manifest updates
  - [x] 13.1 Create ManifestUpdater class in `scripts/cleanup/manifest.py`
    - Implement pyproject.toml exclusion updates
    - Implement MANIFEST.in updates
    - Implement .gitignore updates
    - Implement validation of updated files
    - _Requirements: 2.5, 12.1, 12.2, 12.3, 12.4, 14.5_
  
  - [x] 13.2 Write unit tests for ManifestUpdater
    - Test pyproject.toml updates
    - Test MANIFEST.in updates
    - Test .gitignore updates
    - _Requirements: 12.1, 12.2, 12.3_

- [x] 14. Implement documentation updater
  - [x] 14.1 Create DocumentationUpdater class in `scripts/cleanup/docs.py`
    - Implement README.md size update
    - Implement CLEANUP-SUMMARY.md generation
    - Implement CONTRIBUTING.md updates
    - _Requirements: 14.1, 14.2, 14.3, 14.4_
  
  - [x] 14.2 Write unit tests for DocumentationUpdater
    - Test README.md updates
    - Test CLEANUP-SUMMARY.md generation
    - Test CONTRIBUTING.md updates
    - _Requirements: 14.1, 14.2, 14.3_

- [x] 15. Implement import reference detector
  - [x] 15.1 Create ImportDetector class in `scripts/cleanup/imports.py`
    - Implement Python import statement parser (using ast module)
    - Implement path reference detection
    - Implement reference checking for directories
    - _Requirements: 1.2, 2.3_
  
  - [x] 15.2 Write property test for import reference detection
    - **Property 14: Import Reference Detection**
    - **Validates: Requirements 1.2, 2.3**
  
  - [x] 15.3 Write unit tests for ImportDetector
    - Test various import statement formats
    - Test path reference detection
    - Test false positive handling
    - _Requirements: 1.2, 2.3_

- [-] 16. Integration and end-to-end testing
  - [x] 16.1 Create integration test suite in `tests/integration/test_cleanup_integration.py`
    - Test full audit → cleanup → validate cycle
    - Test rollback scenario
    - Test dry-run scenario
    - Test dependency consolidation scenario
    - _Requirements: All requirements_
  
  - [x] 16.2 Write end-to-end property tests
    - Test complete cleanup workflow with generated project structures
    - Test various failure scenarios and recovery
    - _Requirements: All requirements_

- [x] 17. Final checkpoint and validation
  - Run full test suite with coverage report
  - Verify all 15 correctness properties pass
  - Test CLI with real project structure (in safe test environment)
  - Generate final audit report
  - Ensure all tests pass, ask the user if questions arise.

- [x] 18. Documentation and cleanup script finalization
  - [x] 18.1 Add comprehensive docstrings to all classes and methods
    - Follow Google-style docstrings
    - Include examples in docstrings
    - _Requirements: 13.1_
  
  - [x] 18.2 Create usage documentation in `scripts/cleanup/README.md`
    - Document all CLI flags
    - Provide usage examples
    - Document backup and rollback process
    - Include troubleshooting guide
    - _Requirements: 13.1, 13.2_
  
  - [x] 18.3 Make cleanup.py executable
    - Add shebang line
    - Set executable permissions
    - Test execution from command line
    - _Requirements: 13.1_

## Notes

- Tasks marked with `*` are optional property-based and unit tests that can be skipped for faster MVP
- Each task references specific requirements for traceability
- Checkpoints ensure incremental validation at key milestones
- Property tests validate universal correctness properties using Hypothesis
- Unit tests validate specific examples and edge cases
- Integration tests validate end-to-end workflows
- The implementation uses Python 3.10+ with type hints throughout
- All file operations use pathlib.Path for cross-platform compatibility
- Backup operations use tarfile module for compression
- Dependency parsing uses tomli/tomli_w for TOML handling
- Import detection uses ast module for Python parsing
