#!/usr/bin/env python3
"""
Script to migrate existing tests to the new test structure.

This script:
1. Identifies test files in the root tests/ directory
2. Determines their appropriate location based on imports
3. Moves them to the correct subdirectory
4. Updates import paths if necessary
5. Creates a migration report
"""

import os
import re
import shutil
from pathlib import Path
from typing import Dict, List, Tuple, Optional

# Define the mapping of source modules to test directories
MODULE_TO_TEST_DIR = {
    'agentic_sdlc.core': 'tests/unit/core',
    'agentic_sdlc.infrastructure': 'tests/unit/infrastructure',
    'agentic_sdlc.intelligence': 'tests/unit/intelligence',
    'agentic_sdlc.orchestration': 'tests/unit/orchestration',
}

# Tests that should go to integration/
INTEGRATION_TESTS = [
    'test_integration_e2e.py',
    'test_audit_trail_integration.py',
    'test_model_optimizer_integration.py',
    'test_model_optimizer_integration_property_tests.py',
    'test_swarms_integration.py',
    'test_api_model_management_e2e.py',
]

# Tests that should go to e2e/
E2E_TESTS = [
    'test_integration_e2e.py',
    'test_api_model_management_e2e.py',
]

# Tests that are property tests and should go to property/
PROPERTY_TEST_PATTERN = r'_property_tests\.py$'


def analyze_test_file(file_path: Path) -> Tuple[str, List[str]]:
    """
    Analyze a test file to determine which module it tests.
    
    Returns:
        Tuple of (target_directory, list of imported modules)
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
    except Exception as e:
        print(f"Error reading {file_path}: {e}")
        return ('tests/unit', [])
    
    # Find all imports from agentic_sdlc
    import_pattern = r'from agentic_sdlc\.(\w+)(?:\.[\w.]+)? import'
    imports = re.findall(import_pattern, content)
    
    if not imports:
        # No agentic_sdlc imports, keep in unit/
        return ('tests/unit', [])
    
    # Determine the primary module being tested
    # Use the most common import
    from collections import Counter
    module_counts = Counter(imports)
    primary_module = module_counts.most_common(1)[0][0]
    
    # Map to test directory
    module_key = f'agentic_sdlc.{primary_module}'
    target_dir = MODULE_TO_TEST_DIR.get(module_key, 'tests/unit')
    
    return (target_dir, imports)


def determine_target_location(test_file: Path) -> str:
    """
    Determine the target location for a test file.
    
    Returns:
        Target directory path as string
    """
    filename = test_file.name
    
    # Check if it's an integration test
    if filename in INTEGRATION_TESTS:
        return 'tests/integration'
    
    # Check if it's an e2e test
    if filename in E2E_TESTS:
        return 'tests/e2e'
    
    # Check if it's a property test
    if re.search(PROPERTY_TEST_PATTERN, filename):
        return 'tests/property'
    
    # Analyze the file to determine module
    target_dir, imports = analyze_test_file(test_file)
    
    # If it's a property test based on content, move to property/
    if '_property_tests' in filename:
        return 'tests/property'
    
    return target_dir


def get_subdirectory_from_imports(test_file: Path, target_base: str) -> str:
    """
    Determine the subdirectory within the target based on imports.
    
    For example, if testing orchestration.api_model_management,
    return 'tests/unit/orchestration/api_model_management'
    """
    try:
        with open(test_file, 'r', encoding='utf-8') as f:
            content = f.read()
    except Exception:
        return target_base
    
    # Find the most specific import path
    import_pattern = r'from agentic_sdlc\.(\w+)\.([.\w]+) import'
    matches = re.findall(import_pattern, content)
    
    if not matches:
        return target_base
    
    # Get the most common submodule path
    from collections import Counter
    submodule_counts = Counter([match[1].split('.')[0] for match in matches])
    
    if submodule_counts:
        most_common_submodule = submodule_counts.most_common(1)[0][0]
        return os.path.join(target_base, most_common_submodule)
    
    return target_base


def migrate_test_file(test_file: Path, dry_run: bool = False) -> Tuple[bool, str, str]:
    """
    Migrate a single test file to its target location.
    
    Returns:
        Tuple of (success, source_path, target_path)
    """
    target_dir = determine_target_location(test_file)
    
    # For unit tests, determine subdirectory
    if target_dir.startswith('tests/unit/'):
        target_dir = get_subdirectory_from_imports(test_file, target_dir)
    
    # Create target directory
    target_path = Path(target_dir) / test_file.name
    
    if dry_run:
        print(f"Would move: {test_file} -> {target_path}")
        return (True, str(test_file), str(target_path))
    
    try:
        # Create target directory if it doesn't exist
        os.makedirs(target_dir, exist_ok=True)
        
        # Move the file
        shutil.move(str(test_file), str(target_path))
        print(f"Moved: {test_file} -> {target_path}")
        return (True, str(test_file), str(target_path))
    except Exception as e:
        print(f"Error moving {test_file}: {e}")
        return (False, str(test_file), str(target_path))


def main():
    """Main migration function."""
    import argparse
    
    parser = argparse.ArgumentParser(description='Migrate tests to new structure')
    parser.add_argument('--dry-run', action='store_true', 
                       help='Show what would be done without actually moving files')
    parser.add_argument('--verbose', action='store_true',
                       help='Show detailed information')
    args = parser.parse_args()
    
    # Find all test files in the root tests/ directory
    tests_dir = Path('tests')
    test_files = [
        f for f in tests_dir.glob('test_*.py')
        if f.is_file() and f.parent == tests_dir
    ]
    
    print(f"Found {len(test_files)} test files to migrate")
    print("=" * 60)
    
    if args.dry_run:
        print("DRY RUN MODE - No files will be moved")
        print("=" * 60)
    
    # Migrate each file
    results = []
    for test_file in sorted(test_files):
        success, source, target = migrate_test_file(test_file, dry_run=args.dry_run)
        results.append((success, source, target))
    
    # Print summary
    print("\n" + "=" * 60)
    print("MIGRATION SUMMARY")
    print("=" * 60)
    
    successful = sum(1 for r in results if r[0])
    failed = len(results) - successful
    
    print(f"Total files: {len(results)}")
    print(f"Successful: {successful}")
    print(f"Failed: {failed}")
    
    if args.verbose or failed > 0:
        print("\nDetailed results:")
        for success, source, target in results:
            status = "✓" if success else "✗"
            print(f"{status} {source} -> {target}")
    
    # Create migration report
    report_path = Path('tests/MIGRATION_REPORT.md')
    with open(report_path, 'w') as f:
        f.write("# Test Migration Report\n\n")
        f.write(f"Total files migrated: {len(results)}\n")
        f.write(f"Successful: {successful}\n")
        f.write(f"Failed: {failed}\n\n")
        f.write("## File Mappings\n\n")
        for success, source, target in sorted(results, key=lambda x: x[2]):
            status = "✓" if success else "✗"
            f.write(f"- {status} `{source}` → `{target}`\n")
    
    print(f"\nMigration report written to: {report_path}")
    
    return 0 if failed == 0 else 1


if __name__ == '__main__':
    exit(main())
