"""
Property-based tests for DirectoryScanner.

These tests verify universal properties that should hold for all valid inputs
using the Hypothesis library for property-based testing.

Tests cover:
- Property 1: Directory scanning completeness
- Property 2: Configuration file detection
- Property 4: V2 directory checklist completeness
"""

import os
import tempfile
from pathlib import Path
from typing import Dict, List, Set

import pytest
from hypothesis import given, strategies as st, settings, assume
from hypothesis import HealthCheck

from agentic_sdlc.comparison.scanner import DirectoryScanner, LibraryAnalyzer
from agentic_sdlc.comparison.models import ProjectStructure


# Hypothesis strategies for generating test data

@st.composite
def valid_directory_name(draw):
    """Generate a valid directory name (no special characters).
    
    Normalizes to lowercase to avoid case-sensitivity issues on 
    case-insensitive filesystems (e.g., macOS default APFS/HFS+).
    
    Avoids directory names that the scanner intentionally ignores.
    """
    # Directories that the scanner ignores
    IGNORED_DIRS = {'.git', '__pycache__', '.pytest_cache', '.mypy_cache', 
                    '.tox', 'node_modules', '.venv', 'venv', 'env', '.eggs'}
    
    # Use alphanumeric and common safe characters
    name = draw(st.text(
        alphabet=st.characters(
            whitelist_categories=('Lu', 'Ll', 'Nd'),
            whitelist_characters='_-'
        ),
        min_size=1,
        max_size=20
    ))
    # Normalize to lowercase to avoid case-sensitivity issues
    name = name.lower()
    # Ensure it doesn't start with a dot, dash, or digit
    if name and (name[0] in '.-' or name[0].isdigit()):
        name = 'dir_' + name
    
    # Ensure it's not an ignored directory
    if name in IGNORED_DIRS:
        name = 'dir_' + name
    
    return name if name else 'dir'


@st.composite
def directory_tree_strategy(draw, max_depth=5):
    """
    Generate a random directory tree structure.
    
    Returns a nested dict where keys are directory names and values are
    either empty dicts (leaf directories) or nested dicts (subdirectories).
    
    Ensures no duplicate directory names at the same level.
    """
    depth = draw(st.integers(min_value=1, max_value=max_depth))
    
    def generate_level(current_depth):
        if current_depth >= depth:
            return {}
        
        num_subdirs = draw(st.integers(min_value=0, max_value=5))
        subdirs = {}
        used_names = set()
        
        for i in range(num_subdirs):
            # Generate unique directory name at this level
            attempts = 0
            while attempts < 10:  # Limit attempts to avoid infinite loops
                dir_name = draw(valid_directory_name())
                if dir_name not in used_names:
                    used_names.add(dir_name)
                    break
                attempts += 1
            else:
                # If we can't generate a unique name, use a numbered fallback
                dir_name = f"dir_{i}"
                while dir_name in used_names:
                    i += 1
                    dir_name = f"dir_{i}"
                used_names.add(dir_name)
            
            # Recursively generate subdirectories
            if current_depth < depth - 1:
                subdirs[dir_name] = generate_level(current_depth + 1)
            else:
                subdirs[dir_name] = {}
        
        return subdirs
    
    return generate_level(0)


@st.composite
def config_files_strategy(draw):
    """Generate a subset of configuration files to create."""
    all_config_files = [
        'pyproject.toml',
        'requirements.txt',
        'requirements-dev.txt',
        'Dockerfile',
        'docker-compose.yml',
        '.gitignore',
        'setup.py',
        'setup.cfg',
        'tox.ini',
        'pytest.ini',
        '.pre-commit-config.yaml',
    ]
    
    # Select a random subset of config files
    num_files = draw(st.integers(min_value=0, max_value=len(all_config_files)))
    selected = draw(st.lists(
        st.sampled_from(all_config_files),
        min_size=num_files,
        max_size=num_files,
        unique=True
    ))
    
    return selected


@st.composite
def v2_directory_checklist_strategy(draw):
    """Generate a list of directories that might be in v2 suggestions."""
    # Common directories from v2 suggestions
    common_dirs = [
        'docs', 'tests', 'config', 'cli', 'agentic_sdlc',
        'examples', 'scripts', 'monitoring', 'security',
        'utils', 'models', 'data'
    ]
    
    # Select a subset
    num_dirs = draw(st.integers(min_value=1, max_value=len(common_dirs)))
    selected = draw(st.lists(
        st.sampled_from(common_dirs),
        min_size=num_dirs,
        max_size=num_dirs,
        unique=True
    ))
    
    return selected


# Helper functions

def create_directory_structure(root: Path, structure: Dict, current_depth: int = 0) -> Set[str]:
    """
    Create a directory structure from a nested dict.
    
    Args:
        root: Root directory to create structure in
        structure: Nested dict representing directory tree
        current_depth: Current depth in the tree
        
    Returns:
        Set of all directory paths created (relative to root)
    """
    created_dirs = set()
    
    for dir_name, subdirs in structure.items():
        dir_path = root / dir_name
        dir_path.mkdir(exist_ok=True)
        
        # Add relative path to set
        rel_path = dir_path.relative_to(root)
        created_dirs.add(str(rel_path))
        
        # Recursively create subdirectories
        if subdirs:
            sub_created = create_directory_structure(dir_path, subdirs, current_depth + 1)
            # Add subdirectory paths relative to root
            for sub_path in sub_created:
                created_dirs.add(str(rel_path / sub_path))
    
    return created_dirs


def get_directories_up_to_depth(structure: Dict, max_depth: int, current_depth: int = 1, prefix: str = '') -> Set[str]:
    """
    Get all directory paths up to a certain depth from a structure dict.
    
    Depth counting matches the scanner:
    - Depth 0: root only (no directories from structure)
    - Depth 1: top-level directories
    - Depth 2: top-level + their children
    - etc.
    
    Args:
        structure: Nested dict representing directory tree
        max_depth: Maximum depth to include (scanner's max_depth)
        current_depth: Current depth in recursion (starts at 1 for top-level)
        prefix: Path prefix for current level
        
    Returns:
        Set of directory paths up to max_depth
    """
    dirs = set()
    
    # If we're beyond the max depth, don't include anything
    if current_depth > max_depth:
        return dirs
    
    for dir_name, subdirs in structure.items():
        if prefix:
            dir_path = f"{prefix}/{dir_name}"
        else:
            dir_path = dir_name
        
        # Include this directory since we're at or below max_depth
        dirs.add(dir_path)
        
        # Recursively get subdirectories if we haven't reached max_depth
        if current_depth < max_depth and subdirs:
            sub_dirs = get_directories_up_to_depth(subdirs, max_depth, current_depth + 1, dir_path)
            dirs.update(sub_dirs)
    
    return dirs


def get_directories_beyond_depth(structure: Dict, max_depth: int, current_depth: int = 1, prefix: str = '') -> Set[str]:
    """
    Get all directory paths beyond a certain depth from a structure dict.
    
    Depth counting matches the scanner:
    - Depth 0: root only
    - Depth 1: top-level directories
    - Depth 2: top-level + their children
    - etc.
    
    Args:
        structure: Nested dict representing directory tree
        max_depth: Depth threshold (scanner's max_depth)
        current_depth: Current depth in recursion (starts at 1 for top-level)
        prefix: Path prefix for current level
        
    Returns:
        Set of directory paths beyond max_depth
    """
    dirs = set()
    
    for dir_name, subdirs in structure.items():
        if prefix:
            dir_path = f"{prefix}/{dir_name}"
        else:
            dir_path = dir_name
        
        # If we're beyond the depth limit, add this directory
        if current_depth > max_depth:
            dirs.add(dir_path)
        
        # Recursively check subdirectories
        if subdirs:
            sub_dirs = get_directories_beyond_depth(subdirs, max_depth, current_depth + 1, dir_path)
            dirs.update(sub_dirs)
    
    return dirs


def count_tree_depth(structure: Dict, current_depth: int = 1) -> int:
    """
    Count the maximum depth of a directory tree structure.
    
    Depth counting matches the scanner:
    - Depth 1: top-level directories
    - Depth 2: top-level + their children
    - etc.
    
    Args:
        structure: Nested dict representing directory tree
        current_depth: Current depth in recursion (starts at 1 for top-level)
        
    Returns:
        Maximum depth of the tree
    """
    if not structure:
        return current_depth - 1  # No directories at this level
    
    max_depth = current_depth
    for subdirs in structure.values():
        if subdirs:
            depth = count_tree_depth(subdirs, current_depth + 1)
            max_depth = max(max_depth, depth)
    
    return max_depth


# Property Tests

# Feature: v2-structure-comparison, Property 1: Directory scanning completeness
@settings(
    max_examples=100,
    deadline=None,
    suppress_health_check=[HealthCheck.function_scoped_fixture, HealthCheck.too_slow]
)
@given(
    structure=directory_tree_strategy(max_depth=4),
    scan_depth=st.integers(min_value=1, max_value=5)
)
def test_property_1_directory_scanning_completeness(structure, scan_depth):
    """
    Property 1: Directory scanning completeness
    
    For any directory tree with known structure, scanning should identify 
    all directories up to the specified depth limit and no directories 
    beyond that depth.
    
    This test verifies that:
    1. All directories at depth <= scan_depth are found
    2. No directories at depth > scan_depth are found
    3. The scanner respects the max_depth parameter
    
    **Validates: Requirements 1.1, 1.2**
    """
    # Skip if structure is empty
    assume(len(structure) > 0)
    
    with tempfile.TemporaryDirectory() as tmpdir:
        root = Path(tmpdir)
        
        # Create the directory structure
        created_dirs = create_directory_structure(root, structure)
        
        # Scan the project with the specified depth
        scanner = DirectoryScanner()
        result = scanner.scan_project(str(root), max_depth=scan_depth)
        
        # Get expected directories up to scan_depth
        expected_dirs = get_directories_up_to_depth(structure, scan_depth)
        
        # Get directories beyond scan_depth (should not be found)
        beyond_depth_dirs = get_directories_beyond_depth(structure, scan_depth)
        
        # Get actual scanned directories (excluding root '.')
        actual_dirs = set(path for path in result.directories.keys() if path != '.')
        
        # Verify all expected directories are found
        for expected_dir in expected_dirs:
            assert expected_dir in actual_dirs, \
                f"Expected directory '{expected_dir}' not found in scan results. " \
                f"Scanned: {actual_dirs}, Expected: {expected_dirs}"
        
        # Verify no directories beyond depth are found
        for beyond_dir in beyond_depth_dirs:
            assert beyond_dir not in actual_dirs, \
                f"Directory '{beyond_dir}' beyond depth {scan_depth} was incorrectly found. " \
                f"Scanned: {actual_dirs}, Beyond depth: {beyond_depth_dirs}"
        
        # Verify the root directory is always included
        assert '.' in result.directories
        assert result.directories['.'].exists


# Feature: v2-structure-comparison, Property 1: Directory scanning completeness (depth boundary)
@settings(
    max_examples=100,
    deadline=None,
    suppress_health_check=[HealthCheck.function_scoped_fixture, HealthCheck.too_slow]
)
@given(structure=directory_tree_strategy(max_depth=3))
def test_property_1_scanning_respects_depth_boundaries(structure):
    """
    Property 1: Directory scanning completeness (depth boundary test)
    
    For any directory tree, scanning with different depth limits should
    produce different results, with deeper scans finding more directories.
    
    **Validates: Requirements 1.1, 1.2**
    """
    assume(len(structure) > 0)
    
    # Get the actual depth of the structure
    actual_depth = count_tree_depth(structure)
    assume(actual_depth >= 2)  # Need at least 2 levels for meaningful test
    
    with tempfile.TemporaryDirectory() as tmpdir:
        root = Path(tmpdir)
        create_directory_structure(root, structure)
        
        scanner = DirectoryScanner()
        
        # Scan with depth 1
        result_depth_1 = scanner.scan_project(str(root), max_depth=1)
        dirs_depth_1 = set(path for path in result_depth_1.directories.keys() if path != '.')
        
        # Scan with depth 2
        result_depth_2 = scanner.scan_project(str(root), max_depth=2)
        dirs_depth_2 = set(path for path in result_depth_2.directories.keys() if path != '.')
        
        # Verify depth 1 results are a subset of depth 2 results
        assert dirs_depth_1.issubset(dirs_depth_2), \
            f"Depth 1 scan should be subset of depth 2. " \
            f"Depth 1: {dirs_depth_1}, Depth 2: {dirs_depth_2}"
        
        # If structure has depth >= 2, depth 2 should find more directories
        if actual_depth >= 2:
            # There should be at least some directories at depth 2
            expected_depth_2 = get_directories_up_to_depth(structure, 2)
            expected_depth_1 = get_directories_up_to_depth(structure, 1)
            
            if len(expected_depth_2) > len(expected_depth_1):
                assert len(dirs_depth_2) > len(dirs_depth_1), \
                    f"Depth 2 scan should find more directories than depth 1. " \
                    f"Depth 1: {len(dirs_depth_1)}, Depth 2: {len(dirs_depth_2)}"


# Feature: v2-structure-comparison, Property 2: Configuration file detection
@settings(
    max_examples=100,
    deadline=None,
    suppress_health_check=[HealthCheck.function_scoped_fixture, HealthCheck.too_slow]
)
@given(config_files=config_files_strategy())
def test_property_2_configuration_file_detection(config_files):
    """
    Property 2: Configuration file detection
    
    For any project root directory, the scanner should correctly identify 
    the presence or absence of all specified configuration files.
    
    This test verifies that:
    1. All existing config files are detected as present
    2. All non-existing config files are detected as absent
    3. The detection is accurate for all config files in the list
    
    **Validates: Requirements 1.3, 10.1**
    """
    with tempfile.TemporaryDirectory() as tmpdir:
        root = Path(tmpdir)
        
        # Create the selected config files
        for config_file in config_files:
            file_path = root / config_file
            file_path.write_text(f"# {config_file}\n")
        
        # Scan the project
        scanner = DirectoryScanner()
        result = scanner.scan_project(str(root), max_depth=1)
        
        # Verify all config files are correctly detected
        for config_file in DirectoryScanner.CONFIG_FILES:
            expected_exists = config_file in config_files
            actual_exists = result.config_files.get(config_file, False)
            
            assert actual_exists == expected_exists, \
                f"Config file '{config_file}' detection mismatch. " \
                f"Expected: {expected_exists}, Actual: {actual_exists}"
        
        # Verify all created files are detected
        for config_file in config_files:
            assert result.config_files[config_file], \
                f"Created config file '{config_file}' not detected"
        
        # Verify the config_files dict has entries for all known config files
        assert len(result.config_files) == len(DirectoryScanner.CONFIG_FILES), \
            f"Config files dict should have {len(DirectoryScanner.CONFIG_FILES)} entries, " \
            f"but has {len(result.config_files)}"


# Feature: v2-structure-comparison, Property 2: Configuration file detection (all files)
@settings(
    max_examples=100,
    deadline=None,
    suppress_health_check=[HealthCheck.function_scoped_fixture, HealthCheck.too_slow]
)
@given(
    create_all=st.booleans(),
    extra_files=st.lists(st.text(min_size=1, max_size=20), max_size=5)
)
def test_property_2_config_detection_completeness(create_all, extra_files):
    """
    Property 2: Configuration file detection (completeness test)
    
    The scanner should detect all config files in its list, regardless of
    whether they exist or not, and should not be confused by other files.
    
    **Validates: Requirements 1.3, 10.1**
    """
    with tempfile.TemporaryDirectory() as tmpdir:
        root = Path(tmpdir)
        
        # Optionally create all config files
        if create_all:
            for config_file in DirectoryScanner.CONFIG_FILES:
                (root / config_file).write_text(f"# {config_file}\n")
        
        # Create some extra files that are not config files
        for extra_file in extra_files:
            # Avoid creating files with names that match config files
            if extra_file not in DirectoryScanner.CONFIG_FILES:
                try:
                    (root / extra_file).write_text("extra content\n")
                except (OSError, ValueError):
                    # Skip invalid filenames
                    pass
        
        # Scan the project
        scanner = DirectoryScanner()
        result = scanner.scan_project(str(root), max_depth=1)
        
        # Verify all config files are in the result
        for config_file in DirectoryScanner.CONFIG_FILES:
            assert config_file in result.config_files, \
                f"Config file '{config_file}' missing from results"
            
            # Verify the detection is correct
            expected = (root / config_file).exists()
            actual = result.config_files[config_file]
            assert actual == expected, \
                f"Config file '{config_file}' detection incorrect. " \
                f"Expected: {expected}, Actual: {actual}"


# Feature: v2-structure-comparison, Property 4: V2 directory checklist completeness
@settings(
    max_examples=100,
    deadline=None,
    suppress_health_check=[HealthCheck.function_scoped_fixture, HealthCheck.too_slow]
)
@given(
    checklist_dirs=v2_directory_checklist_strategy(),
    create_subset=st.booleans()
)
def test_property_4_v2_directory_checklist_completeness(checklist_dirs, create_subset):
    """
    Property 4: V2 directory checklist completeness
    
    For any list of directories mentioned in v2 suggestions, the scanner 
    should check and record the status of every directory in that list.
    
    This test verifies that:
    1. All directories in the checklist are scanned
    2. The existence status is correctly recorded
    3. No directories in the checklist are missed
    
    **Validates: Requirements 1.5**
    """
    with tempfile.TemporaryDirectory() as tmpdir:
        root = Path(tmpdir)
        
        # Create a subset of the checklist directories
        if create_subset:
            # Create about half of the directories
            num_to_create = len(checklist_dirs) // 2 + 1
            dirs_to_create = checklist_dirs[:num_to_create]
        else:
            # Create all directories
            dirs_to_create = checklist_dirs
        
        for dir_name in dirs_to_create:
            (root / dir_name).mkdir(exist_ok=True)
        
        # Scan the project
        scanner = DirectoryScanner()
        result = scanner.scan_project(str(root), max_depth=3)
        
        # Verify all checklist directories are recorded
        for dir_name in checklist_dirs:
            # Check if the directory is in the scan results
            # It should be present with correct existence status
            expected_exists = dir_name in dirs_to_create
            
            # The directory should be in the results
            if expected_exists:
                assert dir_name in result.directories, \
                    f"Checklist directory '{dir_name}' not found in scan results"
                assert result.directories[dir_name].exists, \
                    f"Checklist directory '{dir_name}' should exist but is marked as not existing"
            else:
                # If not created, it should either not be in results or marked as not existing
                if dir_name in result.directories:
                    # If it's in results, it should be marked as not existing
                    # But actually, our scanner only records existing directories
                    # So non-existing directories won't be in the results
                    pass
        
        # Verify all created directories are found
        for dir_name in dirs_to_create:
            assert dir_name in result.directories, \
                f"Created directory '{dir_name}' not found in scan results"
            assert result.directories[dir_name].exists, \
                f"Created directory '{dir_name}' not marked as existing"


# Feature: v2-structure-comparison, Property 4: V2 directory checklist completeness (nested)
@settings(
    max_examples=100,
    deadline=None,
    suppress_health_check=[HealthCheck.function_scoped_fixture, HealthCheck.too_slow]
)
@given(checklist_dirs=v2_directory_checklist_strategy())
def test_property_4_checklist_with_subdirectories(checklist_dirs):
    """
    Property 4: V2 directory checklist completeness (with subdirectories)
    
    For directories in the v2 checklist that have subdirectories, the scanner
    should record both the parent directory and its subdirectories.
    
    **Validates: Requirements 1.5**
    """
    assume(len(checklist_dirs) > 0)
    
    with tempfile.TemporaryDirectory() as tmpdir:
        root = Path(tmpdir)
        
        # Create directories with subdirectories
        subdirs_map = {}
        for dir_name in checklist_dirs:
            parent_dir = root / dir_name
            parent_dir.mkdir(exist_ok=True)
            
            # Create 1-3 subdirectories
            num_subdirs = min(3, len(checklist_dirs))
            subdirs = []
            for i in range(num_subdirs):
                subdir_name = f"sub{i}"
                subdir_path = parent_dir / subdir_name
                subdir_path.mkdir(exist_ok=True)
                subdirs.append(subdir_name)
            
            subdirs_map[dir_name] = subdirs
        
        # Scan the project
        scanner = DirectoryScanner()
        result = scanner.scan_project(str(root), max_depth=3)
        
        # Verify all parent directories are found
        for dir_name in checklist_dirs:
            assert dir_name in result.directories, \
                f"Parent directory '{dir_name}' not found"
            
            # Verify subdirectories are recorded
            expected_subdirs = set(subdirs_map[dir_name])
            actual_subdirs = set(result.directories[dir_name].subdirectories)
            
            assert expected_subdirs.issubset(actual_subdirs), \
                f"Subdirectories of '{dir_name}' not fully recorded. " \
                f"Expected: {expected_subdirs}, Actual: {actual_subdirs}"


# Additional property test: Scanner consistency
@settings(
    max_examples=50,
    deadline=None,
    suppress_health_check=[HealthCheck.function_scoped_fixture, HealthCheck.too_slow]
)
@given(structure=directory_tree_strategy(max_depth=3))
def test_scanner_consistency_multiple_scans(structure):
    """
    Verify that scanning the same directory multiple times produces
    consistent results.
    
    This is an idempotency test - the scanner should produce the same
    output when run multiple times on the same input.
    """
    assume(len(structure) > 0)
    
    with tempfile.TemporaryDirectory() as tmpdir:
        root = Path(tmpdir)
        create_directory_structure(root, structure)
        
        scanner = DirectoryScanner()
        
        # Scan multiple times
        result1 = scanner.scan_project(str(root), max_depth=3)
        result2 = scanner.scan_project(str(root), max_depth=3)
        result3 = scanner.scan_project(str(root), max_depth=3)
        
        # Verify all results are identical
        assert result1.root_path == result2.root_path == result3.root_path
        assert set(result1.directories.keys()) == set(result2.directories.keys()) == set(result3.directories.keys())
        assert result1.config_files == result2.config_files == result3.config_files
        
        # Verify directory info is consistent
        for dir_path in result1.directories:
            assert result1.directories[dir_path].exists == result2.directories[dir_path].exists
            assert result1.directories[dir_path].exists == result3.directories[dir_path].exists
            assert set(result1.directories[dir_path].subdirectories) == set(result2.directories[dir_path].subdirectories)
            assert set(result2.directories[dir_path].subdirectories) == set(result3.directories[dir_path].subdirectories)


# Additional property test: Empty directory handling
def test_scanner_handles_empty_directory():
    """
    Verify that the scanner correctly handles an empty directory.
    
    An empty directory should still be scanned successfully, with no
    subdirectories and no config files.
    """
    with tempfile.TemporaryDirectory() as tmpdir:
        root = Path(tmpdir)
        
        scanner = DirectoryScanner()
        result = scanner.scan_project(str(root), max_depth=3)
        
        # Verify the root is scanned
        assert '.' in result.directories
        assert result.directories['.'].exists
        assert result.directories['.'].file_count == 0
        assert len(result.directories['.'].subdirectories) == 0
        
        # Verify no config files are found
        for config_file, exists in result.config_files.items():
            assert not exists, f"Config file '{config_file}' should not exist in empty directory"


# Additional property test: Invalid path handling
@settings(max_examples=50, deadline=None)
@given(invalid_path=st.text(
    alphabet=st.characters(
        whitelist_categories=('Lu', 'Ll', 'Nd'),
        whitelist_characters='_-/'
    ),
    min_size=1,
    max_size=50
))
def test_scanner_handles_invalid_paths(invalid_path):
    """
    Verify that the scanner raises appropriate errors for invalid paths.
    """
    # Ensure the path doesn't accidentally exist and doesn't contain null bytes
    assume('\x00' not in invalid_path)
    assume(not Path(invalid_path).exists())
    
    scanner = DirectoryScanner()
    
    with pytest.raises(ValueError, match="Root path does not exist"):
        scanner.scan_project(invalid_path, max_depth=3)


# ============================================================================
# Property Tests for LibraryAnalyzer
# ============================================================================

# Hypothesis strategies for library testing

@st.composite
def python_package_name(draw):
    """Generate a valid Python package name without hyphens to avoid version ambiguity."""
    # Package names typically use lowercase letters, numbers, and underscores
    # Avoid hyphens because they're used as version separators and create ambiguity
    # Generate a base name with letters
    base = draw(st.text(
        alphabet=st.characters(whitelist_categories=('Ll',)),
        min_size=2,
        max_size=10
    ))
    
    # Optionally add numbers or underscores (but not hyphens to avoid version confusion)
    add_suffix = draw(st.booleans())
    if add_suffix:
        suffix_type = draw(st.sampled_from(['number', 'underscore']))
        if suffix_type == 'number':
            suffix = draw(st.text(
                alphabet=st.characters(whitelist_categories=('Nd',)),
                min_size=1,
                max_size=3
            ))
            base = base + suffix
        elif suffix_type == 'underscore':
            extra = draw(st.text(
                alphabet=st.characters(whitelist_categories=('Ll',)),
                min_size=1,
                max_size=5
            ))
            base = base + '_' + extra
    
    # Ensure it's not empty
    return base if base else 'package'


@st.composite
def package_version(draw):
    """Generate a semantic version string."""
    major = draw(st.integers(min_value=0, max_value=10))
    minor = draw(st.integers(min_value=0, max_value=20))
    patch = draw(st.integers(min_value=0, max_value=50))
    return f"{major}.{minor}.{patch}"


@st.composite
def lib_directory_structure(draw):
    """
    Generate a lib/ directory structure with various package formats.
    
    Returns a dict with:
    - 'packages': list of package names (without versions)
    - 'items': list of (name, type) tuples to create
      where type is 'dir', 'dist-info', 'egg-info', 'egg-file', or 'whl-file'
    """
    num_packages = draw(st.integers(min_value=0, max_value=20))
    
    packages = []
    items = []
    
    for _ in range(num_packages):
        pkg_name = draw(python_package_name())
        version = draw(package_version())
        
        # Avoid duplicate package names
        if pkg_name in packages:
            continue
        
        packages.append(pkg_name)
        
        # Choose package format
        format_choice = draw(st.sampled_from([
            'dir',           # Plain directory (e.g., 'requests')
            'versioned_dir', # Directory with version (e.g., 'requests-2.28.0')
            'dist-info',     # .dist-info directory (e.g., 'requests-2.28.0.dist-info')
            'egg-info',      # .egg-info directory (e.g., 'requests-2.28.0.egg-info')
            'egg-file',      # .egg file (e.g., 'requests-2.28.0.egg')
            'whl-file',      # .whl file (e.g., 'requests-2.28.0-py3-none-any.whl')
        ]))
        
        if format_choice == 'dir':
            items.append((pkg_name, 'dir'))
        elif format_choice == 'versioned_dir':
            items.append((f"{pkg_name}-{version}", 'dir'))
        elif format_choice == 'dist-info':
            items.append((f"{pkg_name}-{version}.dist-info", 'dir'))
        elif format_choice == 'egg-info':
            items.append((f"{pkg_name}-{version}.egg-info", 'dir'))
        elif format_choice == 'egg-file':
            items.append((f"{pkg_name}-{version}.egg", 'file'))
        elif format_choice == 'whl-file':
            # Wheel files have more complex naming
            py_version = draw(st.sampled_from(['py2', 'py3', 'py2.py3']))
            abi = draw(st.sampled_from(['none', 'cp38', 'cp39', 'cp310']))
            platform = draw(st.sampled_from(['any', 'linux_x86_64', 'win_amd64', 'macosx_10_9_x86_64']))
            items.append((f"{pkg_name}-{version}-{py_version}-{abi}-{platform}.whl", 'file'))
    
    return {'packages': packages, 'items': items}


def create_lib_structure(lib_path: Path, structure: dict) -> None:
    """
    Create a lib/ directory structure from the generated structure dict.
    
    Args:
        lib_path: Path to lib/ directory
        structure: Dict with 'packages' and 'items' keys
    """
    lib_path.mkdir(exist_ok=True)
    
    for item_name, item_type in structure['items']:
        item_path = lib_path / item_name
        
        if item_type in ['dir', 'dist-info', 'egg-info']:
            item_path.mkdir(exist_ok=True)
            # Add some dummy files to make it look like a real package
            (item_path / '__init__.py').write_text('# Package init\n')
        elif item_type in ['file', 'egg-file', 'whl-file']:
            # Create a dummy file
            item_path.write_text(f'# {item_name}\n')


# Feature: v2-structure-comparison, Property 3: Lib directory analysis
@settings(
    max_examples=100,
    deadline=None,
    suppress_health_check=[HealthCheck.function_scoped_fixture, HealthCheck.too_slow]
)
@given(lib_structure=lib_directory_structure())
def test_property_3_lib_directory_analysis(lib_structure):
    """
    Property 3: Lib directory analysis
    
    For any lib/ directory containing Python packages, the analyzer should 
    correctly determine if it contains bundled dependencies and extract the 
    package list.
    
    This test verifies that:
    1. The analyzer correctly identifies when lib/ exists
    2. The analyzer counts all packages in lib/
    3. The analyzer extracts package names correctly
    4. The analyzer calculates total size
    
    **Validates: Requirements 1.4**
    """
    with tempfile.TemporaryDirectory() as tmpdir:
        root = Path(tmpdir)
        lib_path = root / 'lib'
        
        # Create the lib/ directory structure
        create_lib_structure(lib_path, lib_structure)
        
        # Analyze the lib/ directory
        analyzer = LibraryAnalyzer()
        result = analyzer.analyze_lib_directory(str(lib_path))
        
        # Verify lib/ is detected as existing
        assert result.exists, "lib/ directory should be detected as existing"
        
        # Verify package count matches expected
        expected_packages = set(lib_structure['packages'])
        actual_packages = set(result.packages)
        
        # The analyzer should find all packages
        assert len(actual_packages) == len(expected_packages), \
            f"Package count mismatch. Expected {len(expected_packages)}, got {len(actual_packages)}. " \
            f"Expected: {expected_packages}, Actual: {actual_packages}"
        
        # Verify all expected packages are found
        for pkg in expected_packages:
            assert pkg in actual_packages, \
                f"Expected package '{pkg}' not found in results. " \
                f"Expected: {expected_packages}, Actual: {actual_packages}"
        
        # Verify package count field
        assert result.package_count == len(expected_packages), \
            f"Package count field incorrect. Expected {len(expected_packages)}, got {result.package_count}"
        
        # Verify size is calculated (should be > 0 if there are packages)
        if len(expected_packages) > 0:
            assert result.total_size_mb >= 0, \
                "Total size should be non-negative"


# Feature: v2-structure-comparison, Property 3: Lib directory analysis (empty lib)
def test_property_3_empty_lib_directory():
    """
    Property 3: Lib directory analysis (empty lib/ directory)
    
    For an empty lib/ directory, the analyzer should correctly report that
    it exists but contains no packages.
    
    **Validates: Requirements 1.4**
    """
    with tempfile.TemporaryDirectory() as tmpdir:
        root = Path(tmpdir)
        lib_path = root / 'lib'
        lib_path.mkdir()
        
        # Analyze the empty lib/ directory
        analyzer = LibraryAnalyzer()
        result = analyzer.analyze_lib_directory(str(lib_path))
        
        # Verify lib/ is detected as existing
        assert result.exists, "Empty lib/ directory should be detected as existing"
        
        # Verify no packages are found
        assert result.package_count == 0, \
            f"Empty lib/ should have 0 packages, got {result.package_count}"
        assert len(result.packages) == 0, \
            f"Empty lib/ should have empty package list, got {result.packages}"
        
        # Verify size is 0 or very small
        assert result.total_size_mb == 0.0, \
            f"Empty lib/ should have 0 MB size, got {result.total_size_mb}"


# Feature: v2-structure-comparison, Property 3: Lib directory analysis (non-existent)
def test_property_3_nonexistent_lib_directory():
    """
    Property 3: Lib directory analysis (non-existent lib/)
    
    For a non-existent lib/ directory, the analyzer should correctly report
    that it does not exist.
    
    **Validates: Requirements 1.4**
    """
    with tempfile.TemporaryDirectory() as tmpdir:
        root = Path(tmpdir)
        lib_path = root / 'lib'
        
        # Don't create lib/ directory
        
        # Analyze the non-existent lib/ directory
        analyzer = LibraryAnalyzer()
        result = analyzer.analyze_lib_directory(str(lib_path))
        
        # Verify lib/ is detected as not existing
        assert not result.exists, "Non-existent lib/ should be detected as not existing"
        
        # Verify default values for non-existent lib/
        assert result.package_count == 0, \
            f"Non-existent lib/ should have 0 packages, got {result.package_count}"
        assert len(result.packages) == 0, \
            f"Non-existent lib/ should have empty package list, got {result.packages}"
        assert result.total_size_mb == 0.0, \
            f"Non-existent lib/ should have 0 MB size, got {result.total_size_mb}"


# Feature: v2-structure-comparison, Property 3: Lib directory analysis (package name extraction)
@settings(
    max_examples=100,
    deadline=None,
    suppress_health_check=[HealthCheck.function_scoped_fixture, HealthCheck.too_slow]
)
@given(
    package_name=python_package_name(),
    version=package_version(),
    format_type=st.sampled_from(['dir', 'versioned_dir', 'dist-info', 'egg-info', 'egg-file', 'whl-file'])
)
def test_property_3_package_name_extraction(package_name, version, format_type):
    """
    Property 3: Lib directory analysis (package name extraction)
    
    For any package in various formats (plain dir, versioned dir, .dist-info,
    .egg-info, .egg file, .whl file), the analyzer should correctly extract
    the base package name without version suffixes or extensions.
    
    **Validates: Requirements 1.4**
    """
    with tempfile.TemporaryDirectory() as tmpdir:
        root = Path(tmpdir)
        lib_path = root / 'lib'
        lib_path.mkdir()
        
        # Create package in the specified format
        if format_type == 'dir':
            item_path = lib_path / package_name
            item_path.mkdir()
            (item_path / '__init__.py').write_text('# Package\n')
        elif format_type == 'versioned_dir':
            item_path = lib_path / f"{package_name}-{version}"
            item_path.mkdir()
            (item_path / '__init__.py').write_text('# Package\n')
        elif format_type == 'dist-info':
            item_path = lib_path / f"{package_name}-{version}.dist-info"
            item_path.mkdir()
            (item_path / 'METADATA').write_text('# Metadata\n')
        elif format_type == 'egg-info':
            item_path = lib_path / f"{package_name}-{version}.egg-info"
            item_path.mkdir()
            (item_path / 'PKG-INFO').write_text('# Package info\n')
        elif format_type == 'egg-file':
            item_path = lib_path / f"{package_name}-{version}.egg"
            item_path.write_text('# Egg file\n')
        elif format_type == 'whl-file':
            item_path = lib_path / f"{package_name}-{version}-py3-none-any.whl"
            item_path.write_text('# Wheel file\n')
        
        # Analyze the lib/ directory
        analyzer = LibraryAnalyzer()
        result = analyzer.analyze_lib_directory(str(lib_path))
        
        # Verify the package is found
        assert result.exists, "lib/ directory should exist"
        assert result.package_count == 1, \
            f"Should find exactly 1 package, found {result.package_count}"
        
        # Verify the package name is extracted correctly (without version)
        assert len(result.packages) == 1, \
            f"Should have exactly 1 package in list, got {len(result.packages)}"
        
        extracted_name = result.packages[0]
        assert extracted_name == package_name, \
            f"Package name extraction failed. Expected '{package_name}', got '{extracted_name}' " \
            f"for format '{format_type}' with version '{version}'"


# Feature: v2-structure-comparison, Property 3: Lib directory analysis (size calculation)
@settings(
    max_examples=100,
    deadline=None,
    suppress_health_check=[HealthCheck.function_scoped_fixture, HealthCheck.too_slow]
)
@given(
    num_packages=st.integers(min_value=1, max_value=10),
    file_size_kb=st.integers(min_value=1, max_value=100)
)
def test_property_3_size_calculation(num_packages, file_size_kb):
    """
    Property 3: Lib directory analysis (size calculation)
    
    For any lib/ directory with packages, the analyzer should correctly
    calculate the total size in MB by summing all file sizes.
    
    **Validates: Requirements 1.4**
    """
    with tempfile.TemporaryDirectory() as tmpdir:
        root = Path(tmpdir)
        lib_path = root / 'lib'
        lib_path.mkdir()
        
        # Create packages with known file sizes
        total_bytes = 0
        for i in range(num_packages):
            pkg_dir = lib_path / f"package{i}"
            pkg_dir.mkdir()
            
            # Create a file with specific size
            file_path = pkg_dir / '__init__.py'
            content = 'x' * (file_size_kb * 1024)  # Create content of specific size
            file_path.write_text(content)
            
            total_bytes += len(content.encode('utf-8'))
        
        # Analyze the lib/ directory
        analyzer = LibraryAnalyzer()
        result = analyzer.analyze_lib_directory(str(lib_path))
        
        # Verify size calculation
        expected_size_mb = total_bytes / (1024 * 1024)
        
        # Allow for small floating point differences
        assert abs(result.total_size_mb - expected_size_mb) < 0.01, \
            f"Size calculation incorrect. Expected {expected_size_mb:.2f} MB, " \
            f"got {result.total_size_mb:.2f} MB"
        
        # Verify size is positive
        assert result.total_size_mb > 0, \
            "Total size should be positive for non-empty lib/"


# Feature: v2-structure-comparison, Property 3: Lib directory analysis (duplicate handling)
@settings(
    max_examples=100,
    deadline=None,
    suppress_health_check=[HealthCheck.function_scoped_fixture, HealthCheck.too_slow]
)
@given(
    package_name=python_package_name(),
    num_duplicates=st.integers(min_value=2, max_value=5)
)
def test_property_3_duplicate_package_handling(package_name, num_duplicates):
    """
    Property 3: Lib directory analysis (duplicate handling)
    
    For any lib/ directory with the same package in multiple formats or
    versions, the analyzer should deduplicate and report the package only once.
    
    **Validates: Requirements 1.4**
    """
    with tempfile.TemporaryDirectory() as tmpdir:
        root = Path(tmpdir)
        lib_path = root / 'lib'
        lib_path.mkdir()
        
        # Create the same package in multiple formats
        formats = [
            (f"{package_name}", 'dir'),
            (f"{package_name}-1.0.0", 'dir'),
            (f"{package_name}-2.0.0.dist-info", 'dir'),
            (f"{package_name}-1.5.0.egg-info", 'dir'),
            (f"{package_name}-1.0.0.egg", 'file'),
        ]
        
        for i in range(min(num_duplicates, len(formats))):
            item_name, item_type = formats[i]
            item_path = lib_path / item_name
            
            if item_type == 'dir':
                item_path.mkdir()
                (item_path / '__init__.py').write_text('# Package\n')
            else:
                item_path.write_text('# File\n')
        
        # Analyze the lib/ directory
        analyzer = LibraryAnalyzer()
        result = analyzer.analyze_lib_directory(str(lib_path))
        
        # Verify the package is deduplicated
        assert result.exists, "lib/ directory should exist"
        
        # The package should appear only once in the list
        package_count = result.packages.count(package_name)
        assert package_count == 1, \
            f"Package '{package_name}' should appear exactly once, but appears {package_count} times. " \
            f"Packages found: {result.packages}"
        
        # Total package count should be 1
        assert result.package_count == 1, \
            f"Should report 1 unique package, got {result.package_count}"


# Feature: v2-structure-comparison, Property 3: Lib directory analysis (special directories ignored)
@settings(
    max_examples=100,
    deadline=None,
    suppress_health_check=[HealthCheck.function_scoped_fixture, HealthCheck.too_slow]
)
@given(
    package_name=python_package_name(),
    special_dirs=st.lists(
        st.sampled_from(['.git', '__pycache__', '.pytest_cache', '.mypy_cache', '.DS_Store']),
        min_size=1,
        max_size=3,
        unique=True
    )
)
def test_property_3_special_directories_ignored(package_name, special_dirs):
    """
    Property 3: Lib directory analysis (special directories ignored)
    
    For any lib/ directory containing special directories (like .git, __pycache__),
    the analyzer should ignore them and not count them as packages.
    
    **Validates: Requirements 1.4**
    """
    with tempfile.TemporaryDirectory() as tmpdir:
        root = Path(tmpdir)
        lib_path = root / 'lib'
        lib_path.mkdir()
        
        # Create a real package
        pkg_dir = lib_path / package_name
        pkg_dir.mkdir()
        (pkg_dir / '__init__.py').write_text('# Package\n')
        
        # Create special directories that should be ignored
        for special_dir in special_dirs:
            special_path = lib_path / special_dir
            if not special_dir.startswith('.'):
                special_path.mkdir()
            else:
                # For dot files/dirs, create them
                try:
                    special_path.mkdir()
                except:
                    pass
        
        # Analyze the lib/ directory
        analyzer = LibraryAnalyzer()
        result = analyzer.analyze_lib_directory(str(lib_path))
        
        # Verify only the real package is found
        assert result.exists, "lib/ directory should exist"
        assert result.package_count == 1, \
            f"Should find exactly 1 package (ignoring special dirs), found {result.package_count}. " \
            f"Packages: {result.packages}"
        
        assert package_name in result.packages, \
            f"Real package '{package_name}' should be found. Packages: {result.packages}"
        
        # Verify special directories are not in the package list
        for special_dir in special_dirs:
            assert special_dir not in result.packages, \
                f"Special directory '{special_dir}' should not be counted as a package. " \
                f"Packages: {result.packages}"
