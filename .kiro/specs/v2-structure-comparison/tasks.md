# Implementation Plan: V2 Structure Comparison

## Overview

This implementation plan breaks down the V2 Structure Comparison feature into discrete, actionable tasks. The approach follows a bottom-up strategy: first implementing core data models, then building individual modules (scanner, parser, analyzer), and finally integrating them into a complete comparison engine with reporting capabilities.

Each task builds incrementally on previous work, with property-based tests integrated throughout to catch errors early. The plan includes checkpoints to ensure quality and allow for user feedback.

## Tasks

- [x] 1. Set up project structure and core data models
  - Create `agentic_sdlc/comparison/` directory for the comparison feature
  - Create `__init__.py` files for proper package structure
  - Define all data model classes in `models.py` (ProjectStructure, DirectoryInfo, LibraryInfo, ProposedStructure, ProposedDirectory, Improvement, ComparisonResult, Gap, Conflict, DirectoryStatus enum, Task)
  - Add type hints to all data model fields
  - _Requirements: 1.1, 1.2, 1.3, 1.4, 1.5, 2.1, 2.2, 2.3, 3.1, 3.5, 6.1, 7.1, 8.1, 9.1, 12.1_

- [x] 1.1 Write property tests for data models
  - **Property 10: Gap analysis structure** - For any comparison result, the gap analysis should produce a list where each gap has all required fields
  - **Property 33: Status differentiation** - For any suggestion, the system should assign exactly one status
  - _Requirements: 3.5, 12.4_

- [x] 2. Implement Scanner Module
  - [x] 2.1 Implement DirectoryScanner class
    - Write `scan_project()` method with depth-limited recursion
    - Write `check_directory_exists()` method
    - Write `get_subdirectories()` method
    - Write `find_config_files()` method to detect pyproject.toml, requirements.txt, Dockerfile, etc.
    - _Requirements: 1.1, 1.2, 1.3, 1.5_

  - [x] 2.2 Write property tests for DirectoryScanner
    - **Property 1: Directory scanning completeness** - For any directory tree with known structure, scanning should identify all directories up to the specified depth limit
    - **Property 2: Configuration file detection** - For any project root directory, the scanner should correctly identify the presence or absence of all specified configuration files
    - **Property 4: V2 directory checklist completeness** - For any list of directories mentioned in v2 suggestions, the scanner should check and record the status of every directory
    - _Requirements: 1.1, 1.2, 1.3, 1.5_

  - [x] 2.3 Implement LibraryAnalyzer class
    - Write `analyze_lib_directory()` method to count packages and calculate size
    - Write `extract_dependencies()` method to list all packages in lib/
    - Handle case where lib/ doesn't exist
    - _Requirements: 1.4_

  - [x] 2.4 Write property tests for LibraryAnalyzer
    - **Property 3: Lib directory analysis** - For any lib/ directory containing Python packages, the analyzer should correctly determine if it contains bundled dependencies
    - _Requirements: 1.4_

- [x] 3. Implement Parser Module
  - [x] 3.1 Implement MarkdownParser utility class
    - Write `extract_sections()` method to parse markdown headers
    - Write `extract_code_blocks()` method to extract fenced code blocks
    - Write `parse_checklist_items()` method to parse checkbox lists
    - _Requirements: 2.1, 2.2, 2.3_

  - [x] 3.2 Implement V2SuggestionParser class
    - Write `parse_improvement_suggestions()` to extract 15 categories from SDLC_Improvement_Suggestions.md
    - Write `parse_proposed_structure()` to extract directory tree from Proposed_Structure.md
    - Write `parse_checklist()` to extract items with priorities from Quick_Action_Checklist.md
    - Write `extract_directory_tree()` to parse directory structure from code blocks
    - _Requirements: 2.1, 2.2, 2.3_

  - [x] 3.3 Write property tests for Parser
    - **Property 5: Markdown parsing completeness** - For any valid markdown document with code blocks and sections, the parser should extract all sections and code blocks without loss
    - **Property 6: Improvement classification** - For any improvement from v2 suggestions, the system should correctly classify whether it involves directory changes, file changes, or both
    - _Requirements: 2.2, 2.3, 2.4, 2.5_

  - [x] 3.4 Write unit tests for parsing actual v2 documents
    - Test parsing SDLC_Improvement_Suggestions.md returns exactly 15 categories
    - Test parsing Proposed_Structure.md extracts complete directory tree
    - Test parsing Quick_Action_Checklist.md extracts all checklist items
    - _Requirements: 2.1, 2.2, 2.3_

- [x] 4. Checkpoint - Ensure scanner and parser tests pass
  - Ensure all tests pass, ask the user if questions arise.

- [x] 5. Implement Analyzer Module
  - [x] 5.1 Implement StructureComparator class
    - Write `compare_structures()` method to compare current vs proposed
    - Write `check_directory_status()` to assign IMPLEMENTED/PARTIAL/MISSING status
    - Write `verify_subdirectories()` to check expected subdirectories exist
    - _Requirements: 3.1, 3.2, 5.1, 5.2, 5.3, 5.4_

  - [x] 5.2 Write property tests for StructureComparator
    - **Property 7: Directory status assignment** - For any proposed directory and current project structure, the comparator should assign exactly one status
    - **Property 8: Subdirectory verification** - For any directory with a list of expected subdirectories, the verifier should correctly identify which exist and which are missing
    - _Requirements: 3.1, 3.2, 5.1, 5.2, 5.3, 5.4_

  - [x] 5.3 Implement GapAnalyzer class
    - Write `identify_gaps()` to find all missing or incomplete items
    - Write `categorize_gaps()` to group gaps by improvement category
    - Write `calculate_completion_percentage()` to compute overall progress
    - _Requirements: 3.5, 4.1, 9.3_

  - [x] 5.4 Write property tests for GapAnalyzer
    - **Property 24: Completion percentage calculation** - For any set of improvements with completion statuses, the calculated percentage should equal (number completed / total number) × 100
    - _Requirements: 9.3_

  - [x] 5.5 Implement ConflictDetector class
    - Write `detect_conflicts()` to find potential issues
    - Write `check_import_impacts()` to identify broken imports from file moves
    - _Requirements: 8.1, 8.3, 8.4, 8.5_

  - [x] 5.6 Write property tests for ConflictDetector
    - **Property 18: Conflict detection** - For any proposed directory that exists with different contents than proposed, the conflict detector should flag it
    - **Property 19: Import impact analysis** - For any file move operation, the analyzer should identify all import statements that reference the moved file
    - **Property 20: Gitignore validation** - For any directory that should be excluded, the validator should verify that .gitignore contains a pattern matching that directory
    - **Property 21: CI/CD compatibility check** - For any proposed structural change, the validator should verify it doesn't break paths referenced in CI/CD workflow files
    - _Requirements: 8.1, 8.3, 8.4, 8.5_

  - [x] 5.7 Add configuration content verification
    - Write method to check if pyproject.toml contains recommended sections
    - Write method to check if .gitignore excludes recommended directories
    - _Requirements: 3.3, 10.2, 10.3_

  - [x] 5.8 Write property tests for configuration verification
    - **Property 9: Configuration content verification** - For any configuration file with expected sections, the analyzer should correctly identify which sections are present and which are missing
    - _Requirements: 3.3, 10.2_

  - [x] 5.9 Implement directory mismatch detection
    - Write method to flag existing directories that don't match proposed organization
    - _Requirements: 5.5_

  - [x] 5.10 Write property tests for mismatch detection
    - **Property 12: Directory mismatch detection** - For any existing directory that doesn't match the proposed organization, the system should flag it as a mismatch
    - _Requirements: 5.5_

- [x] 6. Implement Priority and Task Generation
  - [x] 6.1 Implement priority matrix logic
    - Write method to categorize gaps as High/Medium/Low priority
    - Write method to estimate effort as Quick Win/Medium/Large
    - Write method to identify task dependencies
    - _Requirements: 6.1, 6.2, 6.3_

  - [x] 6.2 Write property tests for priority matrix
    - **Property 13: Priority categorization** - For any identified gap, the priority matrix should assign exactly one priority level and exactly one effort level
    - **Property 14: Task dependency ordering** - For any list of tasks with dependencies, the generated implementation order should ensure no task appears before any of its dependencies
    - **Property 15: Quick wins identification** - For any set of gaps, the quick wins should be exactly those gaps with effort level "Quick Win" and priority "High" or "Medium"
    - _Requirements: 6.1, 6.2, 6.3, 6.4, 6.5_

  - [x] 6.2 Implement TaskGenerator class
    - Write `generate_tasks()` to create tasks from gaps
    - Write `prioritize_tasks()` to sort by priority and dependencies
    - Write `group_related_tasks()` to create work packages
    - Write `estimate_task_effort()` to calculate time estimates
    - _Requirements: 7.1, 7.2, 7.3, 7.4, 7.5_

  - [x] 6.3 Write property tests for TaskGenerator
    - **Property 16: Task generation completeness** - For any identified gap, the task generator should create a task that includes all required fields
    - **Property 17: Task grouping coherence** - For any set of related tasks, the grouping function should place them in the same work package
    - _Requirements: 7.1, 7.2, 7.3, 7.4, 7.5_

- [x] 7. Checkpoint - Ensure analyzer and task generation tests pass
  - Ensure all tests pass, ask the user if questions arise.

- [x] 8. Implement Reporter Module
  - [x] 8.1 Implement ComparisonReporter class
    - Write `generate_report()` to create complete markdown report
    - Write `generate_summary_section()` with completion percentage
    - Write `generate_category_breakdown()` showing status by category
    - Write `generate_gaps_section()` listing all gaps
    - Write `generate_conflicts_section()` listing conflicts
    - Write `generate_quick_wins_section()` highlighting easy improvements
    - _Requirements: 4.1, 4.2, 4.3, 4.4, 4.5_

  - [x] 8.2 Write property tests for ComparisonReporter
    - **Property 11: Report structure completeness** - For any generated comparison report, it should contain all required sections
    - _Requirements: 4.1, 4.2, 4.3, 4.4, 4.5_

  - [x] 8.3 Implement ProgressVisualizer class
    - Write `create_progress_bar()` to generate ASCII progress bar
    - Write `create_category_chart()` to show category statuses
    - _Requirements: 9.4_

  - [x] 8.4 Write property tests for ProgressVisualizer
    - **Property 25: Progress visualization generation** - For any completion percentage, the generated visualization should include a progress bar and category breakdown
    - _Requirements: 9.4_

- [x] 9. Implement Status Tracking
  - [x] 9.1 Implement status file persistence
    - Write method to save status to JSON file
    - Write method to load status from JSON file
    - Write method to update individual improvement status
    - Add completion date recording when marking items complete
    - _Requirements: 9.1, 9.2, 9.5_

  - [x] 9.2 Write property tests for status tracking
    - **Property 22: Status tracking persistence** - For any status update operation, writing to the status file and then reading it back should return the same status information
    - **Property 23: Completion date recording** - For any improvement marked as complete, the status file should contain a completion date field with a valid ISO 8601 timestamp
    - _Requirements: 9.1, 9.2, 9.5_

  - [x] 9.3 Implement deviation tracking
    - Write method to mark suggestions as "Intentionally Skipped" with required reason
    - Write method to update deviation reasons
    - Add validation to require reason when skipping
    - _Requirements: 12.1, 12.2, 12.5_

  - [x] 9.4 Write property tests for deviation tracking
    - **Property 31: Skip status validation** - For any attempt to mark a suggestion as "Intentionally Skipped", the operation should fail if no reason is provided
    - **Property 32: Deviation reporting** - For any comparison report, the deviations section should list all suggestions marked as "Intentionally Skipped" with their reasons
    - **Property 34: Deviation reason updates** - For any suggestion marked as "Intentionally Skipped", updating its reason should preserve the skip status while changing only the reason text
    - _Requirements: 12.1, 12.2, 12.3, 12.5_

- [x] 10. Implement Migration Script Generation
  - [x] 10.1 Implement MigrationScriptGenerator class
    - Write `generate_lib_cleanup_script()` to create requirements.txt from lib/
    - Write `generate_directory_move_script()` to create git mv commands
    - Write `generate_import_update_script()` to update import statements
    - Write `generate_backup_script()` to backup before destructive operations
    - Write `generate_rollback_script()` to reverse migrations
    - _Requirements: 11.1, 11.2, 11.3, 11.4, 11.5_

  - [x] 10.2 Write property tests for script generation
    - **Property 28: Migration script validity** - For any generated migration script, the script should be syntactically valid and executable
    - **Property 29: Backup script generation** - For any destructive operation in a migration script, a corresponding backup command should be generated before the destructive operation
    - **Property 30: Rollback script generation** - For any migration script, a corresponding rollback script should be generated that reverses all operations
    - _Requirements: 11.1, 11.2, 11.3, 11.4, 11.5_

- [x] 11. Implement Validation and Applicability Checking
  - [x] 11.1 Implement supersession detection
    - Write method to identify v2 suggestions that have been superseded by actual implementation
    - Write method to flag v2 suggestions that may no longer be applicable
    - _Requirements: 10.4, 10.5_

  - [x] 11.2 Write property tests for validation
    - **Property 26: Supersession detection** - For any v2 suggestion where the actual implementation achieves the same goal through different means, the system should identify it as superseded
    - **Property 27: Applicability checking** - For any v2 suggestion that conflicts with current project decisions or is outdated, the system should flag it as potentially not applicable
    - _Requirements: 10.4, 10.5_

- [x] 12. Checkpoint - Ensure all module tests pass
  - Ensure all tests pass, ask the user if questions arise.

- [x] 13. Integrate components into ComparisonEngine
  - [x] 13.1 Create ComparisonEngine class
    - Wire together Scanner, Parser, Analyzer, Reporter, and TaskGenerator
    - Implement `run_comparison()` method as main entry point
    - Add error handling with graceful degradation
    - Add logging throughout the comparison process
    - _Requirements: All requirements_

  - [x] 13.2 Write integration tests for ComparisonEngine
    - Test full comparison flow from scanning to report generation
    - Test error handling when v2 documents are missing
    - Test error handling when project directory is inaccessible
    - Test partial report generation when some data is unavailable
    - _Requirements: All requirements_

- [x] 14. Create CLI interface
  - [x] 14.1 Add comparison command to CLI
    - Create `agentic_sdlc/cli/commands/compare.py`
    - Add `compare` subcommand to main CLI
    - Add options for output file path, verbosity, status file path
    - Add option to generate migration scripts
    - _Requirements: All requirements_

  - [x] 14.2 Write CLI integration tests
    - Test running comparison command with various options
    - Test output file generation
    - Test error messages for invalid inputs
    - _Requirements: All requirements_

- [x] 15. Create example usage and documentation
  - [x] 15.1 Add example script
    - Create `examples/v2_structure_comparison_demo.py`
    - Show how to run comparison programmatically
    - Show how to access comparison results
    - Show how to generate custom reports
    - _Requirements: All requirements_

  - [x] 15.2 Add documentation
    - Create `docs/V2_STRUCTURE_COMPARISON.md` explaining the feature
    - Document CLI usage with examples
    - Document programmatic API
    - Add troubleshooting section
    - _Requirements: All requirements_

- [x] 16. Final checkpoint - Run full test suite and generate initial comparison report
  - Run all unit tests, property tests, and integration tests
  - Generate actual comparison report for agentic-sdlc project
  - Review report for accuracy
  - Ensure all tests pass, ask the user if questions arise.

## Notes

- Tasks marked with `*` are optional property-based tests that can be skipped for faster MVP
- Each property test should run minimum 100 iterations
- Property tests use the `hypothesis` library for Python
- Each task references specific requirements for traceability
- Checkpoints ensure incremental validation and allow for user feedback
- The implementation follows a bottom-up approach: data models → modules → integration
- Error handling is integrated throughout with graceful degradation
- The final output is both a programmatic API and a CLI tool
