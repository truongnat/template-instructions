"""
Property-based tests for CleanupCLI.

These tests use Hypothesis to verify universal properties that should hold
across all valid inputs and execution scenarios for the CLI interface.

Feature: project-audit-cleanup
"""

import pytest
import sys
from pathlib import Path
from datetime import datetime
from hypothesis import given, strategies as st, settings, HealthCheck
from unittest.mock import Mock, patch
import hashlib
import json
import uuid

# Add workspace root to path for imports
workspace_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(workspace_root))

# Import CleanupCLI from the CLI script
import importlib.util
spec = importlib.util.spec_from_file_location(
    "cleanup_cli",
    workspace_root / "scripts" / "cleanup.py"
)
cleanup_cli_module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(cleanup_cli_module)
CleanupCLI = cleanup_cli_module.CleanupCLI

from scripts.cleanup.models import (
    CategorizedFiles,
    FileInfo,
    FileCategory,
    AuditReport,
    SizeImpact,
)


def calculate_directory_hash(directory: Path) -> dict:
    """Calculate hash of all files in a directory for comparison.
    
    Returns a dictionary mapping relative paths to file hashes.
    This allows us to detect any changes to the filesystem.
    """
    file_hashes = {}
    
    if not directory.exists():
        return file_hashes
    
    for item in directory.rglob("*"):
        if item.is_file():
            try:
                # Calculate relative path
                rel_path = item.relative_to(directory)
                
                # Calculate file hash
                hasher = hashlib.sha256()
                with open(item, 'rb') as f:
                    hasher.update(f.read())
                
                file_hashes[str(rel_path)] = {
                    'hash': hasher.hexdigest(),
                    'size': item.stat().st_size,
                    'exists': True
                }
            except (PermissionError, OSError):
                # Skip files we can't read
                pass
    
    return file_hashes


def compare_filesystem_state(before: dict, after: dict) -> tuple[bool, list[str]]:
    """Compare two filesystem states and return if they're identical.
    
    Returns:
        Tuple of (is_identical, list_of_differences)
    """
    differences = []
    
    # Check for new files
    new_files = set(after.keys()) - set(before.keys())
    if new_files:
        differences.extend([f"New file created: {f}" for f in new_files])
    
    # Check for deleted files
    deleted_files = set(before.keys()) - set(after.keys())
    if deleted_files:
        differences.extend([f"File deleted: {f}" for f in deleted_files])
    
    # Check for modified files
    common_files = set(before.keys()) & set(after.keys())
    for file_path in common_files:
        if before[file_path]['hash'] != after[file_path]['hash']:
            differences.append(f"File modified: {file_path}")
        if before[file_path]['size'] != after[file_path]['size']:
            differences.append(f"File size changed: {file_path}")
    
    is_identical = len(differences) == 0
    return is_identical, differences


# Strategy for generating file counts (1 to 50 files)
file_count_strategy = st.integers(min_value=1, max_value=50)

# Strategy for generating file sizes (0 to 1MB)
file_size_strategy = st.integers(min_value=0, max_value=1024 * 1024)


# Feature: project-audit-cleanup, Property 10: Dry Run Makes No Changes
@given(
    remove_count=file_count_strategy,
    consolidate_count=st.integers(min_value=0, max_value=5),
    archive_count=st.integers(min_value=0, max_value=20),
    file_sizes=st.lists(file_size_strategy, min_size=1, max_size=50)
)
@settings(
    max_examples=10,
    deadline=None,
    suppress_health_check=[HealthCheck.function_scoped_fixture]
)
def test_property_dry_run_makes_no_changes(
    tmp_path,
    remove_count,
    consolidate_count,
    archive_count,
    file_sizes
):
    """
    Property 10: Dry Run Makes No Changes
    
    For any cleanup operation with dry_run=True, no files should be created,
    modified, or removed on the file system, and no backups should be created.
    
    **Validates: Requirements 13.3**
    """
    # Create a test project structure with unique name per run
    project_root = tmp_path / f"test_project_{uuid.uuid4().hex[:8]}"
    project_root.mkdir(exist_ok=True)
    
    # Create pyproject.toml (required for CLI)
    pyproject = project_root / "pyproject.toml"
    pyproject.write_text("""
[project]
name = "test-project"
version = "1.0.0"
dependencies = []
""")
    
    # Create docs directory (required for report generation)
    docs_dir = project_root / "docs"
    docs_dir.mkdir()
    
    # Create test files to be removed
    remove_files = []
    for i in range(min(remove_count, len(file_sizes))):
        file_path = project_root / f"remove_{i}.txt"
        size = file_sizes[i] if i < len(file_sizes) else 100
        file_path.write_bytes(b'x' * size)
        remove_files.append(file_path)
    
    # Create test files to be consolidated
    consolidate_files = []
    for i in range(consolidate_count):
        file_path = project_root / f"requirements_{i}.txt"
        file_path.write_text("requests>=2.0.0\n")
        consolidate_files.append(file_path)
    
    # Create test files to be archived
    archive_files = []
    brain_dir = project_root / ".brain"
    brain_dir.mkdir()
    for i in range(archive_count):
        file_path = brain_dir / f"cache_{i}.json"
        file_path.write_text("{}")
        archive_files.append(file_path)
    
    # Capture filesystem state BEFORE dry run
    fs_state_before = calculate_directory_hash(project_root)
    backup_dir = project_root / ".cleanup_backup"
    backup_state_before = calculate_directory_hash(backup_dir)
    
    # Initialize CLI
    cli = CleanupCLI(project_root, verbose=False)
    
    # Run cleanup in dry-run mode
    exit_code = cli.run_cleanup(dry_run=True, create_backup=True)
    
    # Capture filesystem state AFTER dry run
    fs_state_after = calculate_directory_hash(project_root)
    backup_state_after = calculate_directory_hash(backup_dir)
    
    # Property 1: Exit code should be 0 (success)
    assert exit_code == 0, f"Dry run should succeed, got exit code {exit_code}"
    
    # Property 2: No files should be created, modified, or deleted
    fs_identical, fs_differences = compare_filesystem_state(
        fs_state_before,
        fs_state_after
    )
    
    # Filter out audit report files (these are expected in dry-run)
    fs_differences_filtered = [
        diff for diff in fs_differences
        if "CLEANUP-AUDIT-REPORT" not in diff
    ]
    
    assert fs_identical or len(fs_differences_filtered) == 0, (
        f"Dry run should not modify filesystem, but found changes:\n" +
        "\n".join(fs_differences_filtered)
    )
    
    # Property 3: All original files should still exist
    for file_path in remove_files:
        assert file_path.exists(), (
            f"File {file_path} should still exist after dry run"
        )
    
    for file_path in consolidate_files:
        assert file_path.exists(), (
            f"File {file_path} should still exist after dry run"
        )
    
    for file_path in archive_files:
        assert file_path.exists(), (
            f"File {file_path} should still exist after dry run"
        )
    
    # Property 4: No backup should be created
    # (backup directory might exist but should be empty or unchanged)
    backup_identical, backup_differences = compare_filesystem_state(
        backup_state_before,
        backup_state_after
    )
    
    assert backup_identical, (
        f"Dry run should not create backups, but found changes:\n" +
        "\n".join(backup_differences)
    )
    
    # Property 5: File contents should be unchanged
    for file_path in remove_files:
        if file_path.exists():
            # Verify file hash matches original
            original_hash = fs_state_before.get(
                str(file_path.relative_to(project_root))
            )
            if original_hash:
                hasher = hashlib.sha256()
                with open(file_path, 'rb') as f:
                    hasher.update(f.read())
                current_hash = hasher.hexdigest()
                
                assert current_hash == original_hash['hash'], (
                    f"File {file_path} content changed during dry run"
                )


# Feature: project-audit-cleanup, Property 10: Dry Run Makes No Changes (Variant)
@given(
    file_count=st.integers(min_value=5, max_value=30),
    create_corrupt_dirs=st.booleans(),
    create_lib_dir=st.booleans()
)
@settings(
    max_examples=10,
    deadline=None,
    suppress_health_check=[HealthCheck.function_scoped_fixture]
)
def test_property_dry_run_preserves_all_file_types(
    tmp_path,
    file_count,
    create_corrupt_dirs,
    create_lib_dir
):
    """
    Property 10: Dry Run Makes No Changes (Variant)
    
    For any project structure including corrupt directories, lib/ directories,
    and cache files, dry run should preserve all files regardless of their
    categorization.
    
    **Validates: Requirements 13.3**
    """
    # Create a test project structure with unique name per run
    project_root = tmp_path / f"test_project_{uuid.uuid4().hex[:8]}"
    project_root.mkdir(exist_ok=True)
    
    # Create pyproject.toml
    pyproject = project_root / "pyproject.toml"
    pyproject.write_text("""
[project]
name = "test-project"
version = "1.0.0"
dependencies = []
""")
    
    # Create docs directory
    docs_dir = project_root / "docs"
    docs_dir.mkdir()
    
    # Create various file types
    created_paths = []
    
    # Create corrupt directories if requested
    if create_corrupt_dirs:
        corrupt_dir = project_root / "build_corrupt_20260131"
        corrupt_dir.mkdir()
        (corrupt_dir / "file.txt").write_text("corrupt")
        created_paths.append(corrupt_dir)
    
    # Create lib directory if requested
    if create_lib_dir:
        lib_dir = project_root / "agentic_sdlc" / "lib"
        lib_dir.mkdir(parents=True)
        (lib_dir / "bundled.py").write_text("# bundled")
        created_paths.append(lib_dir)
    
    # Create cache files
    brain_dir = project_root / ".brain"
    brain_dir.mkdir()
    for i in range(min(file_count, 10)):
        cache_file = brain_dir / f"cache_{i}.json"
        cache_file.write_text("{}")
        created_paths.append(cache_file)
    
    # Create __pycache__ directories
    pycache_dir = project_root / "__pycache__"
    pycache_dir.mkdir()
    for i in range(min(file_count // 2, 5)):
        pyc_file = pycache_dir / f"module_{i}.pyc"
        pyc_file.write_bytes(b'\x00' * 100)
        created_paths.append(pyc_file)
    
    # Capture filesystem state before dry run
    fs_state_before = calculate_directory_hash(project_root)
    
    # Initialize CLI and run dry run
    cli = CleanupCLI(project_root, verbose=False)
    exit_code = cli.run_cleanup(dry_run=True, create_backup=True)
    
    # Capture filesystem state after dry run
    fs_state_after = calculate_directory_hash(project_root)
    
    # Property: All created paths should still exist
    for path in created_paths:
        assert path.exists(), (
            f"Path {path} should still exist after dry run"
        )
    
    # Property: Filesystem should be unchanged (except audit reports)
    fs_identical, fs_differences = compare_filesystem_state(
        fs_state_before,
        fs_state_after
    )
    
    # Filter out audit report files
    fs_differences_filtered = [
        diff for diff in fs_differences
        if "CLEANUP-AUDIT-REPORT" not in diff
    ]
    
    assert len(fs_differences_filtered) == 0, (
        f"Dry run should not modify filesystem, but found changes:\n" +
        "\n".join(fs_differences_filtered)
    )


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
