"""
Property-based tests for FileCategorizer service.

Feature: project-audit-cleanup
Tests universal properties of file categorization functionality using Hypothesis.
"""

import pytest
from hypothesis import given, strategies as st, settings, assume
from pathlib import Path
import tempfile
from datetime import datetime, timedelta

from scripts.cleanup.categorizer import FileCategorizer
from scripts.cleanup.models import FileInfo, FileCategory


# Strategy for generating critical component paths
@st.composite
def critical_component_paths(draw):
    """Generate paths that should be categorized as critical components."""
    critical_dirs = [
        "agentic_sdlc/core",
        "agentic_sdlc/intelligence",
        "agentic_sdlc/infrastructure",
        "agentic_sdlc/orchestration",
        "agentic_sdlc/defaults",
        "docs",
        ".agent",
        ".kiro",
        "tests",
        "bin",
        "scripts",
    ]
    
    # Choose a critical directory
    base_dir = draw(st.sampled_from(critical_dirs))
    
    # Optionally add subdirectories and filename
    depth = draw(st.integers(min_value=0, max_value=3))
    path_parts = [base_dir]
    
    for _ in range(depth):
        subdir = draw(st.text(min_size=1, max_size=10, alphabet=st.characters(
            whitelist_categories=('Lu', 'Ll', 'Nd'),
            whitelist_characters='_-'
        )))
        if subdir:
            path_parts.append(subdir)
    
    # Add filename
    filename = draw(st.text(min_size=1, max_size=15, alphabet=st.characters(
        whitelist_categories=('Lu', 'Ll', 'Nd'),
        whitelist_characters='_-.'
    )))
    
    if filename and not filename.startswith('.'):
        path_parts.append(filename + ".py")
    else:
        path_parts.append("file.py")
    
    return Path(*path_parts)


@st.composite
def critical_root_files(draw):
    """Generate critical root configuration files."""
    root_files = [
        "pyproject.toml",
        "package.json",
        "docker-compose.yml",
        "Dockerfile",
        ".gitignore",
        ".dockerignore",
        "README.md",
        "LICENSE",
        "SECURITY.md",
        "CONTRIBUTING.md",
        "MANIFEST.in",
    ]
    
    return Path(draw(st.sampled_from(root_files)))


# Feature: project-audit-cleanup, Property 2: Critical Component Preservation
@given(critical_component_paths())
@settings(max_examples=10, deadline=None)
def test_critical_component_preservation_paths(critical_path):
    """
    Property 2: Critical Component Preservation
    
    For any file in the critical components list (core/, intelligence/, 
    infrastructure/, orchestration/, defaults/ excluding projects/, docs/, 
    .agent/, .kiro/, tests/, bin/, scripts/, root configs), that file should 
    never be categorized as REMOVE.
    
    **Validates: Requirements 6.1, 6.2, 6.3, 6.5**
    """
    # Skip if path contains projects/ under defaults/
    path_str = str(critical_path)
    if "agentic_sdlc/defaults/projects" in path_str:
        assume(False)  # Skip this test case
    
    # Create FileInfo for the critical path
    file_info = FileInfo(
        path=critical_path,
        size=1024,
        modified_time=datetime.now()
    )
    
    # Categorize the file
    categorizer = FileCategorizer()
    category = categorizer.categorize(file_info)
    
    # Property: Critical components should NEVER be categorized as REMOVE
    assert category != FileCategory.REMOVE, (
        f"Critical component '{critical_path}' was categorized as REMOVE. "
        f"Category: {category}, Reason: {file_info.reason}"
    )
    
    # Property: Critical components should be marked as critical
    assert file_info.is_critical, (
        f"Critical component '{critical_path}' was not marked as is_critical=True"
    )
    
    # Property: Critical components should be categorized as KEEP
    assert category == FileCategory.KEEP, (
        f"Critical component '{critical_path}' was not categorized as KEEP. "
        f"Got: {category}"
    )


@given(critical_root_files())
@settings(max_examples=10, deadline=None)
def test_critical_root_files_preservation(root_file):
    """
    Property 2: Critical Component Preservation (Root Files)
    
    For any root configuration file (pyproject.toml, package.json, etc.),
    that file should never be categorized as REMOVE.
    
    **Validates: Requirements 6.1, 6.2, 6.3, 6.5**
    """
    # Create FileInfo for the root file
    file_info = FileInfo(
        path=root_file,
        size=512,
        modified_time=datetime.now()
    )
    
    # Categorize the file
    categorizer = FileCategorizer()
    category = categorizer.categorize(file_info)
    
    # Property: Root config files should NEVER be categorized as REMOVE
    assert category != FileCategory.REMOVE, (
        f"Critical root file '{root_file}' was categorized as REMOVE. "
        f"Category: {category}, Reason: {file_info.reason}"
    )
    
    # Property: Root config files should be marked as critical
    assert file_info.is_critical, (
        f"Critical root file '{root_file}' was not marked as is_critical=True"
    )
    
    # Property: Root config files should be categorized as KEEP
    assert category == FileCategory.KEEP, (
        f"Critical root file '{root_file}' was not categorized as KEEP. "
        f"Got: {category}"
    )


@given(
    st.sampled_from([
        "agentic_sdlc/core",
        "agentic_sdlc/intelligence",
        "agentic_sdlc/infrastructure",
        "agentic_sdlc/orchestration",
        "docs",
        ".agent",
        ".kiro",
        "tests",
        "bin",
        "scripts",
    ]),
    st.lists(st.text(min_size=1, max_size=10, alphabet='abcdefghijklmnopqrstuvwxyz_'), 
             min_size=0, max_size=3)
)
@settings(max_examples=10, deadline=None)
def test_critical_paths_never_removed(base_path, subdirs):
    """
    Property 2: Critical Component Preservation (Path Hierarchy)
    
    For any file within a critical directory hierarchy, that file should
    never be categorized as REMOVE, regardless of subdirectory depth.
    
    **Validates: Requirements 6.1, 6.2, 6.3, 6.5**
    """
    # Build path with subdirectories
    path_parts = [base_path] + subdirs + ["test_file.py"]
    file_path = Path(*path_parts)
    
    # Create FileInfo
    file_info = FileInfo(
        path=file_path,
        size=2048,
        modified_time=datetime.now()
    )
    
    # Categorize the file
    categorizer = FileCategorizer()
    category = categorizer.categorize(file_info)
    
    # Property: Files in critical paths should NEVER be REMOVE
    assert category != FileCategory.REMOVE, (
        f"File in critical path '{file_path}' was categorized as REMOVE. "
        f"Category: {category}, Reason: {file_info.reason}"
    )
    
    # Property: Should be marked as critical
    assert file_info.is_critical, (
        f"File in critical path '{file_path}' was not marked as critical"
    )


@given(
    st.lists(st.text(min_size=1, max_size=10, alphabet='abcdefghijklmnopqrstuvwxyz_'), 
             min_size=1, max_size=3)
)
@settings(max_examples=10, deadline=None)
def test_defaults_projects_exclusion(subdirs):
    """
    Property 2: Critical Component Preservation (Defaults/Projects Exclusion)
    
    For any file in agentic_sdlc/defaults/projects/, that file should NOT
    be treated as critical (it's explicitly excluded from critical defaults).
    
    **Validates: Requirements 6.2**
    """
    # Build path under defaults/projects/
    path_parts = ["agentic_sdlc", "defaults", "projects"] + subdirs + ["test.py"]
    file_path = Path(*path_parts)
    
    # Create FileInfo
    file_info = FileInfo(
        path=file_path,
        size=1024,
        modified_time=datetime.now()
    )
    
    # Categorize the file
    categorizer = FileCategorizer()
    category = categorizer.categorize(file_info)
    
    # Property: Files in defaults/projects/ should NOT be marked as critical
    assert not file_info.is_critical, (
        f"File in defaults/projects/ '{file_path}' was incorrectly marked as critical"
    )
    
    # Property: These files can be REMOVE or other categories (not forced to KEEP)
    # They should not get the critical component reason
    if category == FileCategory.KEEP:
        assert file_info.reason != "Critical component - must be preserved", (
            f"File in defaults/projects/ should not have critical component reason"
        )


@given(
    st.lists(
        st.sampled_from([
            "agentic_sdlc/core/main.py",
            "agentic_sdlc/intelligence/agent.py",
            "docs/README.md",
            "tests/test_main.py",
            "pyproject.toml",
            ".gitignore",
        ]),
        min_size=1,
        max_size=10
    )
)
@settings(max_examples=10, deadline=None)
def test_batch_critical_preservation(file_paths):
    """
    Property 2: Critical Component Preservation (Batch Processing)
    
    For any batch of critical files, ALL of them should be preserved
    (none categorized as REMOVE).
    
    **Validates: Requirements 6.1, 6.2, 6.3, 6.5**
    """
    categorizer = FileCategorizer()
    
    for file_path_str in file_paths:
        file_path = Path(file_path_str)
        
        file_info = FileInfo(
            path=file_path,
            size=1024,
            modified_time=datetime.now()
        )
        
        category = categorizer.categorize(file_info)
        
        # Property: No critical file should be REMOVE
        assert category != FileCategory.REMOVE, (
            f"Critical file '{file_path}' in batch was categorized as REMOVE"
        )
        
        # Property: All should be marked as critical
        assert file_info.is_critical, (
            f"Critical file '{file_path}' in batch was not marked as critical"
        )


@given(
    st.text(min_size=1, max_size=20, alphabet='abcdefghijklmnopqrstuvwxyz_'),
    st.sampled_from([
        "agentic_sdlc/core",
        "agentic_sdlc/intelligence",
        "docs",
        "tests",
    ])
)
@settings(max_examples=10, deadline=None)
def test_is_critical_method_consistency(filename, critical_dir):
    """
    Property 2: Critical Component Preservation (Method Consistency)
    
    For any file path, the is_critical() method should return True if and
    only if the file is in a critical path, and this should be consistent
    with the categorize() method marking it as critical.
    
    **Validates: Requirements 6.1, 6.2, 6.3, 6.5**
    """
    file_path = Path(critical_dir) / f"{filename}.py"
    
    categorizer = FileCategorizer()
    
    # Check is_critical method
    is_critical_result = categorizer.is_critical(file_path)
    
    # Check categorize method
    file_info = FileInfo(
        path=file_path,
        size=1024,
        modified_time=datetime.now()
    )
    category = categorizer.categorize(file_info)
    
    # Property: is_critical() and file_info.is_critical should match
    assert is_critical_result == file_info.is_critical, (
        f"Inconsistency: is_critical()={is_critical_result}, "
        f"but file_info.is_critical={file_info.is_critical} for '{file_path}'"
    )
    
    # Property: If is_critical is True, category should be KEEP
    if is_critical_result:
        assert category == FileCategory.KEEP, (
            f"File marked as critical but not categorized as KEEP: {file_path}"
        )


# Strategy for generating directory information
@st.composite
def directory_info_strategy(draw):
    """Generate DirectoryInfo objects with various properties."""
    # Generate directory name
    dir_name = draw(st.text(min_size=1, max_size=20, alphabet='abcdefghijklmnopqrstuvwxyz_-'))
    
    # Generate path (can be nested)
    depth = draw(st.integers(min_value=0, max_value=3))
    path_parts = []
    for _ in range(depth):
        part = draw(st.text(min_size=1, max_size=10, alphabet='abcdefghijklmnopqrstuvwxyz_'))
        if part:
            path_parts.append(part)
    path_parts.append(dir_name)
    
    dir_path = Path(*path_parts) if path_parts else Path(dir_name)
    
    # Generate directory properties
    is_empty = draw(st.booleans())
    
    # If empty, file_count should be 0 and size should be 0 or very small
    if is_empty:
        file_count = 0
        size = draw(st.integers(min_value=0, max_value=100))  # .DS_Store or .gitkeep size
    else:
        file_count = draw(st.integers(min_value=1, max_value=100))
        size = draw(st.integers(min_value=1024, max_value=1000000))
    
    from scripts.cleanup.models import DirectoryInfo
    return DirectoryInfo(
        path=dir_path,
        size=size,
        file_count=file_count,
        is_empty=is_empty,
        is_critical=False
    )


@st.composite
def empty_directory_info(draw):
    """Generate DirectoryInfo for empty directories."""
    # Generate directory name (not in critical list)
    non_critical_names = draw(st.text(
        min_size=1, 
        max_size=20, 
        alphabet='abcdefghijklmnopqrstuvwxyz_-'
    ).filter(lambda x: x not in ['logs', 'states', 'data']))
    
    # Generate path
    depth = draw(st.integers(min_value=0, max_value=2))
    path_parts = []
    for _ in range(depth):
        part = draw(st.text(min_size=1, max_size=10, alphabet='abcdefghijklmnopqrstuvwxyz_'))
        if part:
            path_parts.append(part)
    path_parts.append(non_critical_names)
    
    dir_path = Path(*path_parts) if path_parts else Path(non_critical_names)
    
    from scripts.cleanup.models import DirectoryInfo
    return DirectoryInfo(
        path=dir_path,
        size=0,
        file_count=0,
        is_empty=True,
        is_critical=False
    )


@st.composite
def critical_empty_directory_info(draw):
    """Generate DirectoryInfo for critical empty directories."""
    critical_names = ['logs', 'states', 'data']
    dir_name = draw(st.sampled_from(critical_names))
    
    # Optionally add parent directories
    depth = draw(st.integers(min_value=0, max_value=2))
    path_parts = []
    for _ in range(depth):
        part = draw(st.text(min_size=1, max_size=10, alphabet='abcdefghijklmnopqrstuvwxyz_'))
        if part:
            path_parts.append(part)
    path_parts.append(dir_name)
    
    dir_path = Path(*path_parts)
    
    from scripts.cleanup.models import DirectoryInfo
    return DirectoryInfo(
        path=dir_path,
        size=0,
        file_count=0,
        is_empty=True,
        is_critical=False
    )


# Feature: project-audit-cleanup, Property 12: Empty Directory Identification
@given(directory_info_strategy())
@settings(max_examples=10, deadline=None)
def test_empty_directory_identification(dir_info):
    """
    Property 12: Empty Directory Identification
    
    For any directory that contains zero files or only contains .DS_Store/.gitkeep 
    files, that directory should be identified as empty unless it is in the 
    critical empty directories list (logs/, states/, data/).
    
    **Validates: Requirements 11.1, 11.2, 11.3**
    """
    categorizer = FileCategorizer()
    
    # Property: is_empty_directory should return True only if:
    # 1. dir_info.is_empty is True
    # 2. AND directory name is NOT in critical_empty_dirs
    
    result = categorizer.is_empty_directory(dir_info)
    
    # If directory is not marked as empty, should return False
    if not dir_info.is_empty:
        assert not result, (
            f"Directory '{dir_info.path}' with is_empty=False was identified as empty"
        )
    else:
        # Directory is marked as empty
        dir_name = dir_info.path.name
        is_critical_empty = dir_name in categorizer.critical_empty_dirs
        
        if is_critical_empty:
            # Critical empty directories should NOT be identified for removal
            assert not result, (
                f"Critical empty directory '{dir_info.path}' (name: {dir_name}) "
                f"was incorrectly identified as removable empty directory"
            )
        else:
            # Non-critical empty directories should be identified for removal
            assert result, (
                f"Empty directory '{dir_info.path}' (name: {dir_name}) "
                f"was not identified as empty for removal"
            )


@given(empty_directory_info())
@settings(max_examples=10, deadline=None)
def test_non_critical_empty_directories_identified(dir_info):
    """
    Property 12: Empty Directory Identification (Non-Critical)
    
    For any empty directory that is NOT in the critical list (logs/, states/, 
    data/), that directory should be identified as empty and eligible for removal.
    
    **Validates: Requirements 11.1, 11.2, 11.3**
    """
    categorizer = FileCategorizer()
    
    # Verify directory name is not in critical list
    dir_name = dir_info.path.name
    assume(dir_name not in categorizer.critical_empty_dirs)
    
    # Property: Non-critical empty directories should be identified
    result = categorizer.is_empty_directory(dir_info)
    
    assert result, (
        f"Non-critical empty directory '{dir_info.path}' was not identified as empty. "
        f"is_empty={dir_info.is_empty}, file_count={dir_info.file_count}"
    )


@given(critical_empty_directory_info())
@settings(max_examples=10, deadline=None)
def test_critical_empty_directories_preserved(dir_info):
    """
    Property 12: Empty Directory Identification (Critical Preservation)
    
    For any directory named 'logs', 'states', or 'data', even if empty,
    that directory should NOT be identified as removable.
    
    **Validates: Requirements 11.3**
    """
    categorizer = FileCategorizer()
    
    # Verify directory name is in critical list
    dir_name = dir_info.path.name
    assert dir_name in categorizer.critical_empty_dirs, (
        f"Test setup error: {dir_name} should be in critical_empty_dirs"
    )
    
    # Property: Critical empty directories should NOT be identified for removal
    result = categorizer.is_empty_directory(dir_info)
    
    assert not result, (
        f"Critical empty directory '{dir_info.path}' (name: {dir_name}) "
        f"was incorrectly identified as removable"
    )


@given(
    st.sampled_from(['logs', 'states', 'data']),
    st.integers(min_value=0, max_value=1000),
    st.integers(min_value=0, max_value=100)
)
@settings(max_examples=10, deadline=None)
def test_critical_empty_dirs_always_preserved(dir_name, size, file_count):
    """
    Property 12: Empty Directory Identification (Critical Names)
    
    For any directory with name 'logs', 'states', or 'data', regardless of
    size or file count, if marked as empty it should be preserved.
    
    **Validates: Requirements 11.3**
    """
    from scripts.cleanup.models import DirectoryInfo
    
    dir_info = DirectoryInfo(
        path=Path(dir_name),
        size=size,
        file_count=file_count,
        is_empty=True,  # Marked as empty
        is_critical=False
    )
    
    categorizer = FileCategorizer()
    result = categorizer.is_empty_directory(dir_info)
    
    # Property: Should NOT be identified for removal
    assert not result, (
        f"Critical empty directory '{dir_name}' was identified for removal"
    )


@given(
    st.text(min_size=1, max_size=20, alphabet='abcdefghijklmnopqrstuvwxyz_-')
        .filter(lambda x: x not in ['logs', 'states', 'data']),
    st.booleans()
)
@settings(max_examples=10, deadline=None)
def test_is_empty_flag_determines_identification(dir_name, is_empty):
    """
    Property 12: Empty Directory Identification (is_empty Flag)
    
    For any directory, the is_empty flag should be the primary determinant
    of whether it's identified as empty (along with critical name check).
    
    **Validates: Requirements 11.1, 11.2**
    """
    from scripts.cleanup.models import DirectoryInfo
    
    dir_info = DirectoryInfo(
        path=Path(dir_name),
        size=0 if is_empty else 1024,
        file_count=0 if is_empty else 5,
        is_empty=is_empty,
        is_critical=False
    )
    
    categorizer = FileCategorizer()
    result = categorizer.is_empty_directory(dir_info)
    
    # Property: If is_empty is False, should never be identified
    if not is_empty:
        assert not result, (
            f"Directory '{dir_name}' with is_empty=False was identified as empty"
        )
    else:
        # If is_empty is True and not critical, should be identified
        assert result, (
            f"Empty directory '{dir_name}' was not identified for removal"
        )


@given(
    st.lists(
        st.tuples(
            st.text(min_size=1, max_size=15, alphabet='abcdefghijklmnopqrstuvwxyz_-'),
            st.booleans()
        ),
        min_size=1,
        max_size=20
    )
)
@settings(max_examples=10, deadline=None)
def test_batch_empty_directory_identification(dir_list):
    """
    Property 12: Empty Directory Identification (Batch Processing)
    
    For any batch of directories, the identification should be consistent
    for each directory based on its properties and name.
    
    **Validates: Requirements 11.1, 11.2, 11.3**
    """
    from scripts.cleanup.models import DirectoryInfo
    
    categorizer = FileCategorizer()
    
    for dir_name, is_empty in dir_list:
        dir_info = DirectoryInfo(
            path=Path(dir_name),
            size=0 if is_empty else 2048,
            file_count=0 if is_empty else 10,
            is_empty=is_empty,
            is_critical=False
        )
        
        result = categorizer.is_empty_directory(dir_info)
        
        # Property: Consistent identification based on rules
        is_critical_name = dir_name in categorizer.critical_empty_dirs
        
        if not is_empty:
            assert not result, (
                f"Non-empty directory '{dir_name}' was identified as empty"
            )
        elif is_critical_name:
            assert not result, (
                f"Critical empty directory '{dir_name}' was identified for removal"
            )
        else:
            assert result, (
                f"Empty directory '{dir_name}' was not identified for removal"
            )


@given(
    st.lists(st.text(min_size=1, max_size=10, alphabet='abcdefghijklmnopqrstuvwxyz_'), 
             min_size=1, max_size=3),
    st.sampled_from(['logs', 'states', 'data'])
)
@settings(max_examples=10, deadline=None)
def test_critical_empty_dirs_in_nested_paths(parent_dirs, critical_name):
    """
    Property 12: Empty Directory Identification (Nested Critical Dirs)
    
    For any directory with a critical name (logs/states/data), even if nested
    in parent directories, it should be preserved if empty.
    
    **Validates: Requirements 11.3**
    """
    from scripts.cleanup.models import DirectoryInfo
    
    # Build nested path with critical name at the end
    path_parts = parent_dirs + [critical_name]
    dir_path = Path(*path_parts)
    
    dir_info = DirectoryInfo(
        path=dir_path,
        size=0,
        file_count=0,
        is_empty=True,
        is_critical=False
    )
    
    categorizer = FileCategorizer()
    result = categorizer.is_empty_directory(dir_info)
    
    # Property: Should be preserved (not identified for removal)
    assert not result, (
        f"Critical empty directory '{dir_path}' (name: {critical_name}) "
        f"in nested path was identified for removal"
    )


@given(directory_info_strategy())
@settings(max_examples=10, deadline=None)
def test_categorize_directory_respects_empty_identification(dir_info):
    """
    Property 12: Empty Directory Identification (Integration with Categorization)
    
    For any directory, if is_empty_directory() returns True, then
    categorize_directory() should categorize it as REMOVE (unless it's
    critical or corrupt).
    
    **Validates: Requirements 11.1, 11.2, 11.4**
    """
    categorizer = FileCategorizer()
    
    # Check if directory is identified as empty
    is_empty_result = categorizer.is_empty_directory(dir_info)
    
    # Categorize the directory
    category = categorizer.categorize_directory(dir_info)
    
    # Property: If identified as empty (and not critical/corrupt), should be REMOVE
    if is_empty_result:
        # Check if it's critical or corrupt
        is_critical = categorizer.is_critical(dir_info.path)
        is_corrupt = categorizer.is_corrupt_directory(dir_info.path)
        
        if not is_critical and not is_corrupt:
            assert category == FileCategory.REMOVE, (
                f"Empty directory '{dir_info.path}' was identified as empty "
                f"but not categorized as REMOVE. Got: {category}"
            )


# Strategy for generating corrupt directory paths
@st.composite
def corrupt_directory_paths(draw):
    """Generate directory paths with '_corrupt_' in the name."""
    # Generate base directory name with _corrupt_ pattern
    prefix = draw(st.text(min_size=1, max_size=15, alphabet='abcdefghijklmnopqrstuvwxyz_-'))
    suffix = draw(st.text(min_size=1, max_size=15, alphabet='abcdefghijklmnopqrstuvwxyz_0123456789'))
    
    # Create corrupt directory name
    corrupt_name = f"{prefix}_corrupt_{suffix}"
    
    # Optionally add parent directories
    depth = draw(st.integers(min_value=0, max_value=2))
    path_parts = []
    for _ in range(depth):
        part = draw(st.text(min_size=1, max_size=10, alphabet='abcdefghijklmnopqrstuvwxyz_'))
        if part:
            path_parts.append(part)
    
    path_parts.append(corrupt_name)
    
    # Optionally add a file inside the corrupt directory
    add_file = draw(st.booleans())
    if add_file:
        filename = draw(st.text(min_size=1, max_size=15, alphabet='abcdefghijklmnopqrstuvwxyz_'))
        path_parts.append(f"{filename}.py")
    
    return Path(*path_parts)


# Feature: project-audit-cleanup, Property 6: Corrupt Directory Pattern Matching
@given(corrupt_directory_paths())
@settings(max_examples=10, deadline=None)
def test_corrupt_directory_pattern_matching(corrupt_path):
    """
    Property 6: Corrupt Directory Pattern Matching
    
    For any directory with "_corrupt_" in its name, that directory should be 
    categorized as REMOVE unless it is explicitly in the critical components list.
    
    **Validates: Requirements 1.1, 1.2**
    """
    categorizer = FileCategorizer()
    
    # Verify the path contains _corrupt_
    path_str = str(corrupt_path)
    assert "_corrupt_" in path_str, f"Test setup error: path should contain '_corrupt_': {corrupt_path}"
    
    # Check if the path is in a critical component
    is_critical = categorizer.is_critical(corrupt_path)
    
    # Check if it's identified as corrupt
    is_corrupt = categorizer.is_corrupt_directory(corrupt_path)
    
    # Property: Paths with _corrupt_ should be identified as corrupt
    assert is_corrupt, (
        f"Directory with '_corrupt_' in path '{corrupt_path}' was not identified as corrupt"
    )
    
    # Create FileInfo for the corrupt path
    file_info = FileInfo(
        path=corrupt_path,
        size=1024,
        modified_time=datetime.now()
    )
    
    # Categorize the file
    category = categorizer.categorize(file_info)
    
    # Property: If not critical, corrupt directories should be categorized as REMOVE
    if not is_critical:
        assert category == FileCategory.REMOVE, (
            f"Corrupt directory '{corrupt_path}' was not categorized as REMOVE. "
            f"Got: {category}, Reason: {file_info.reason}"
        )
    else:
        # If it's critical, it should be KEEP (critical takes precedence)
        assert category == FileCategory.KEEP, (
            f"Critical corrupt directory '{corrupt_path}' was not categorized as KEEP. "
            f"Got: {category}"
        )


@given(
    st.sampled_from([
        "build_corrupt_20260131",
        "agentic_sdlc.egg-info_corrupt_20260131",
        "agentic_sdlc.egg-info.trash_corrupt_20260131",
        "dist_corrupt_backup",
        "old_corrupt_files",
    ])
)
@settings(max_examples=10, deadline=None)
def test_specific_corrupt_directories_removed(corrupt_dir_name):
    """
    Property 6: Corrupt Directory Pattern Matching (Specific Examples)
    
    For specific known corrupt directory names from the requirements,
    they should be categorized as REMOVE.
    
    **Validates: Requirements 1.1, 1.4**
    """
    categorizer = FileCategorizer()
    
    # Create path for corrupt directory
    corrupt_path = Path(corrupt_dir_name)
    
    # Verify it's identified as corrupt
    is_corrupt = categorizer.is_corrupt_directory(corrupt_path)
    assert is_corrupt, (
        f"Known corrupt directory '{corrupt_dir_name}' was not identified as corrupt"
    )
    
    # Create FileInfo
    file_info = FileInfo(
        path=corrupt_path,
        size=15000000,  # 15MB
        modified_time=datetime.now()
    )
    
    # Categorize
    category = categorizer.categorize(file_info)
    
    # Property: Should be REMOVE
    assert category == FileCategory.REMOVE, (
        f"Known corrupt directory '{corrupt_dir_name}' was not categorized as REMOVE. "
        f"Got: {category}"
    )


@given(
    st.text(min_size=1, max_size=20, alphabet='abcdefghijklmnopqrstuvwxyz_-'),
    st.integers(min_value=0, max_value=3)
)
@settings(max_examples=10, deadline=None)
def test_corrupt_pattern_in_any_path_part(base_name, depth):
    """
    Property 6: Corrupt Directory Pattern Matching (Nested Paths)
    
    For any path where "_corrupt_" appears in ANY part of the path
    (not just the final component), that path should be identified as corrupt.
    
    **Validates: Requirements 1.1**
    """
    categorizer = FileCategorizer()
    
    # Build path with _corrupt_ in one of the parts
    path_parts = []
    for i in range(depth):
        if i == depth // 2:
            # Add corrupt part in the middle
            path_parts.append(f"{base_name}_corrupt_20260131")
        else:
            path_parts.append(f"dir{i}")
    
    # If no depth, just use corrupt name
    if depth == 0:
        path_parts.append(f"{base_name}_corrupt_20260131")
    
    # Add a file at the end
    path_parts.append("file.py")
    
    corrupt_path = Path(*path_parts)
    
    # Property: Should be identified as corrupt
    is_corrupt = categorizer.is_corrupt_directory(corrupt_path)
    assert is_corrupt, (
        f"Path with '_corrupt_' in any part '{corrupt_path}' was not identified as corrupt"
    )
    
    # Create FileInfo and categorize
    file_info = FileInfo(
        path=corrupt_path,
        size=1024,
        modified_time=datetime.now()
    )
    
    category = categorizer.categorize(file_info)
    
    # Property: Should be REMOVE (assuming not critical)
    if not categorizer.is_critical(corrupt_path):
        assert category == FileCategory.REMOVE, (
            f"Corrupt path '{corrupt_path}' was not categorized as REMOVE. Got: {category}"
        )


@given(
    st.lists(
        st.text(min_size=1, max_size=15, alphabet='abcdefghijklmnopqrstuvwxyz_0123456789'),
        min_size=1,
        max_size=5,
        unique=True
    )
)
@settings(max_examples=10, deadline=None)
def test_batch_corrupt_directory_identification(suffixes):
    """
    Property 6: Corrupt Directory Pattern Matching (Batch Processing)
    
    For any batch of directories with "_corrupt_" in their names,
    ALL of them should be identified as corrupt and categorized as REMOVE
    (unless critical).
    
    **Validates: Requirements 1.1, 1.2**
    """
    categorizer = FileCategorizer()
    
    for suffix in suffixes:
        corrupt_name = f"dir_corrupt_{suffix}"
        corrupt_path = Path(corrupt_name)
        
        # Property: Should be identified as corrupt
        is_corrupt = categorizer.is_corrupt_directory(corrupt_path)
        assert is_corrupt, (
            f"Corrupt directory '{corrupt_name}' was not identified as corrupt"
        )
        
        # Create FileInfo and categorize
        file_info = FileInfo(
            path=corrupt_path,
            size=1024,
            modified_time=datetime.now()
        )
        
        category = categorizer.categorize(file_info)
        
        # Property: Should be REMOVE
        assert category == FileCategory.REMOVE, (
            f"Corrupt directory '{corrupt_name}' was not categorized as REMOVE. "
            f"Got: {category}"
        )


@given(
    st.text(min_size=1, max_size=20, alphabet='abcdefghijklmnopqrstuvwxyz_-')
        .filter(lambda x: "_corrupt_" not in x)
)
@settings(max_examples=10, deadline=None)
def test_non_corrupt_directories_not_identified(dir_name):
    """
    Property 6: Corrupt Directory Pattern Matching (Negative Test)
    
    For any directory WITHOUT "_corrupt_" in its name, that directory
    should NOT be identified as corrupt.
    
    **Validates: Requirements 1.1**
    """
    categorizer = FileCategorizer()
    
    # Verify the name doesn't contain _corrupt_
    assert "_corrupt_" not in dir_name, f"Test setup error: {dir_name} should not contain '_corrupt_'"
    
    dir_path = Path(dir_name)
    
    # Property: Should NOT be identified as corrupt
    is_corrupt = categorizer.is_corrupt_directory(dir_path)
    assert not is_corrupt, (
        f"Non-corrupt directory '{dir_name}' was incorrectly identified as corrupt"
    )


@given(
    st.sampled_from([
        "agentic_sdlc/core",
        "agentic_sdlc/intelligence",
        "docs",
        "tests",
    ]),
    st.text(min_size=1, max_size=15, alphabet='abcdefghijklmnopqrstuvwxyz_0123456789')
)
@settings(max_examples=10, deadline=None)
def test_critical_corrupt_directories_preserved(critical_base, suffix):
    """
    Property 6: Corrupt Directory Pattern Matching (Critical Override)
    
    For any directory with "_corrupt_" in its name that is also in a critical
    component path, the critical status should take precedence and the
    directory should be categorized as KEEP.
    
    **Validates: Requirements 1.2, 6.1**
    """
    categorizer = FileCategorizer()
    
    # Create a path that is both critical and corrupt
    corrupt_name = f"module_corrupt_{suffix}.py"
    critical_corrupt_path = Path(critical_base) / corrupt_name
    
    # Verify it's identified as corrupt
    is_corrupt = categorizer.is_corrupt_directory(critical_corrupt_path)
    assert is_corrupt, (
        f"Path with '_corrupt_' should be identified as corrupt: {critical_corrupt_path}"
    )
    
    # Verify it's identified as critical
    is_critical = categorizer.is_critical(critical_corrupt_path)
    assert is_critical, (
        f"Path in critical directory should be identified as critical: {critical_corrupt_path}"
    )
    
    # Create FileInfo and categorize
    file_info = FileInfo(
        path=critical_corrupt_path,
        size=1024,
        modified_time=datetime.now()
    )
    
    category = categorizer.categorize(file_info)
    
    # Property: Critical status takes precedence - should be KEEP
    assert category == FileCategory.KEEP, (
        f"Critical corrupt path '{critical_corrupt_path}' was not categorized as KEEP. "
        f"Got: {category}. Critical components must be preserved even if corrupt."
    )


@given(
    st.text(min_size=1, max_size=15, alphabet='abcdefghijklmnopqrstuvwxyz_'),
    st.text(min_size=1, max_size=15, alphabet='0123456789')
)
@settings(max_examples=10, deadline=None)
def test_is_corrupt_directory_method_consistency(prefix, timestamp):
    """
    Property 6: Corrupt Directory Pattern Matching (Method Consistency)
    
    For any path, the is_corrupt_directory() method should return True
    if and only if "_corrupt_" appears in the path, and this should be
    consistent with the categorize() method.
    
    **Validates: Requirements 1.1, 1.2**
    """
    categorizer = FileCategorizer()
    
    # Create corrupt directory path
    corrupt_name = f"{prefix}_corrupt_{timestamp}"
    corrupt_path = Path(corrupt_name) / "file.py"
    
    # Check is_corrupt_directory method
    is_corrupt_result = categorizer.is_corrupt_directory(corrupt_path)
    
    # Property: Should be identified as corrupt
    assert is_corrupt_result, (
        f"Path with '_corrupt_' was not identified by is_corrupt_directory(): {corrupt_path}"
    )
    
    # Check categorize method
    file_info = FileInfo(
        path=corrupt_path,
        size=1024,
        modified_time=datetime.now()
    )
    category = categorizer.categorize(file_info)
    
    # Property: If corrupt and not critical, should be REMOVE
    if not categorizer.is_critical(corrupt_path):
        assert category == FileCategory.REMOVE, (
            f"Corrupt path identified by is_corrupt_directory() but not categorized as REMOVE: "
            f"{corrupt_path}, category: {category}"
        )
    
    # Now test non-corrupt path
    non_corrupt_path = Path(prefix) / "file.py"
    is_corrupt_result2 = categorizer.is_corrupt_directory(non_corrupt_path)
    
    # Property: Should NOT be identified as corrupt
    assert not is_corrupt_result2, (
        f"Path without '_corrupt_' was incorrectly identified as corrupt: {non_corrupt_path}"
    )


# Strategy for generating diverse file paths for audit completeness testing
@st.composite
def diverse_file_paths(draw):
    """Generate a diverse set of file paths for audit testing."""
    file_types = [
        # Critical files
        ("agentic_sdlc/core", "main.py"),
        ("agentic_sdlc/intelligence", "agent.py"),
        ("docs", "README.md"),
        ("tests", "test_main.py"),
        ("", "pyproject.toml"),
        
        # Corrupt files
        ("build_corrupt_20260131", "setup.py"),
        ("dist_corrupt_backup", "package.whl"),
        
        # Requirements files
        ("", "requirements.txt"),
        ("", "requirements-dev.txt"),
        
        # Cache files
        ("__pycache__", "main.cpython-310.pyc"),
        (".hypothesis", "data.db"),
        (".brain", "old_data.json"),
        
        # Regular files
        ("src", "utils.py"),
        ("lib", "helper.py"),
    ]
    
    # Select a random subset of file types
    num_files = draw(st.integers(min_value=1, max_value=len(file_types)))
    selected_indices = draw(st.lists(
        st.integers(min_value=0, max_value=len(file_types)-1),
        min_size=num_files,
        max_size=num_files,
        unique=True
    ))
    
    file_paths = []
    for idx in selected_indices:
        dir_path, filename = file_types[idx]
        if dir_path:
            file_paths.append(Path(dir_path) / filename)
        else:
            file_paths.append(Path(filename))
    
    return file_paths


# Feature: project-audit-cleanup, Property 9: Audit Categorization Completeness
@given(diverse_file_paths())
@settings(max_examples=10, deadline=None)
def test_audit_categorization_completeness(file_paths):
    """
    Property 9: Audit Categorization Completeness
    
    For any project scan, every scanned file should be assigned exactly one 
    category (KEEP, REMOVE, CONSOLIDATE, or ARCHIVE), and the sum of files 
    in all categories should equal the total number of files scanned.
    
    **Validates: Requirements 8.2**
    """
    from scripts.cleanup.models import CategorizedFiles
    
    categorizer = FileCategorizer()
    
    # Create FileInfo objects for all paths
    file_infos = []
    for file_path in file_paths:
        file_info = FileInfo(
            path=file_path,
            size=1024,
            modified_time=datetime.now()
        )
        file_infos.append(file_info)
    
    # Categorize all files
    categorized = CategorizedFiles()
    
    for file_info in file_infos:
        category = categorizer.categorize(file_info)
        file_info.category = category
        
        # Add to appropriate list
        if category == FileCategory.KEEP:
            categorized.keep.append(file_info)
        elif category == FileCategory.REMOVE:
            categorized.remove.append(file_info)
        elif category == FileCategory.CONSOLIDATE:
            categorized.consolidate.append(file_info)
        elif category == FileCategory.ARCHIVE:
            categorized.archive.append(file_info)
    
    # Property 1: Every file should be assigned a category
    for file_info in file_infos:
        assert file_info.category is not None, (
            f"File '{file_info.path}' was not assigned a category"
        )
        assert isinstance(file_info.category, FileCategory), (
            f"File '{file_info.path}' has invalid category type: {type(file_info.category)}"
        )
    
    # Property 2: Sum of files in all categories should equal total files scanned
    total_categorized = (
        len(categorized.keep) +
        len(categorized.remove) +
        len(categorized.consolidate) +
        len(categorized.archive)
    )
    
    assert total_categorized == len(file_infos), (
        f"Categorization completeness violated: "
        f"Total files scanned: {len(file_infos)}, "
        f"Total categorized: {total_categorized} "
        f"(KEEP={len(categorized.keep)}, REMOVE={len(categorized.remove)}, "
        f"CONSOLIDATE={len(categorized.consolidate)}, ARCHIVE={len(categorized.archive)})"
    )
    
    # Property 3: Each file should appear in exactly one category
    all_categorized_files = (
        categorized.keep +
        categorized.remove +
        categorized.consolidate +
        categorized.archive
    )
    
    # Check for duplicates
    categorized_paths = [f.path for f in all_categorized_files]
    unique_paths = set(categorized_paths)
    
    assert len(categorized_paths) == len(unique_paths), (
        f"Some files appear in multiple categories. "
        f"Total categorized: {len(categorized_paths)}, "
        f"Unique files: {len(unique_paths)}"
    )
    
    # Property 4: All original files should be in the categorized lists
    original_paths = {f.path for f in file_infos}
    categorized_path_set = set(categorized_paths)
    
    assert original_paths == categorized_path_set, (
        f"Mismatch between scanned and categorized files. "
        f"Missing: {original_paths - categorized_path_set}, "
        f"Extra: {categorized_path_set - original_paths}"
    )


@given(
    st.lists(
        st.sampled_from([
            "agentic_sdlc/core/main.py",
            "agentic_sdlc/lib/helper.py",
            "build_corrupt_20260131/setup.py",
            "requirements.txt",
            "__pycache__/main.pyc",
            ".brain/old_data.json",
            "docs/README.md",
            "pyproject.toml",
        ]),
        min_size=1,
        max_size=20,
        unique=True  # Ensure unique file paths
    )
)
@settings(max_examples=10, deadline=None)
def test_audit_categorization_no_duplicates(file_path_strs):
    """
    Property 9: Audit Categorization Completeness (No Duplicates)
    
    For any set of files, each file should appear in exactly one category
    after categorization. No file should be duplicated across categories.
    
    **Validates: Requirements 8.2**
    """
    from scripts.cleanup.models import CategorizedFiles
    
    categorizer = FileCategorizer()
    
    # Create FileInfo objects
    file_infos = []
    for file_path_str in file_path_strs:
        file_info = FileInfo(
            path=Path(file_path_str),
            size=1024,
            modified_time=datetime.now()
        )
        file_infos.append(file_info)
    
    # Categorize all files
    categorized = CategorizedFiles()
    
    for file_info in file_infos:
        category = categorizer.categorize(file_info)
        file_info.category = category
        
        if category == FileCategory.KEEP:
            categorized.keep.append(file_info)
        elif category == FileCategory.REMOVE:
            categorized.remove.append(file_info)
        elif category == FileCategory.CONSOLIDATE:
            categorized.consolidate.append(file_info)
        elif category == FileCategory.ARCHIVE:
            categorized.archive.append(file_info)
    
    # Collect all categorized file paths
    all_paths = []
    all_paths.extend([f.path for f in categorized.keep])
    all_paths.extend([f.path for f in categorized.remove])
    all_paths.extend([f.path for f in categorized.consolidate])
    all_paths.extend([f.path for f in categorized.archive])
    
    # Property: No duplicates across categories
    assert len(all_paths) == len(set(all_paths)), (
        f"Files appear in multiple categories. "
        f"Total: {len(all_paths)}, Unique: {len(set(all_paths))}"
    )
    
    # Property: All original files are categorized
    original_paths = {f.path for f in file_infos}
    categorized_paths = set(all_paths)
    
    assert original_paths == categorized_paths, (
        f"Not all files were categorized. "
        f"Missing: {original_paths - categorized_paths}"
    )


@given(st.integers(min_value=1, max_value=100))
@settings(max_examples=10, deadline=None)
def test_audit_categorization_count_consistency(num_files):
    """
    Property 9: Audit Categorization Completeness (Count Consistency)
    
    For any number of files scanned, the sum of files in all categories
    should exactly equal the number of files scanned.
    
    **Validates: Requirements 8.2**
    """
    from scripts.cleanup.models import CategorizedFiles
    
    categorizer = FileCategorizer()
    
    # Generate diverse file paths
    file_paths = []
    for i in range(num_files):
        # Create a mix of different file types
        if i % 5 == 0:
            file_paths.append(Path(f"agentic_sdlc/core/file_{i}.py"))
        elif i % 5 == 1:
            file_paths.append(Path(f"build_corrupt_{i}/file.py"))
        elif i % 5 == 2:
            file_paths.append(Path(f"requirements_{i}.txt"))
        elif i % 5 == 3:
            file_paths.append(Path(f"__pycache__/file_{i}.pyc"))
        else:
            file_paths.append(Path(f"src/file_{i}.py"))
    
    # Create FileInfo objects
    file_infos = []
    for file_path in file_paths:
        file_info = FileInfo(
            path=file_path,
            size=1024,
            modified_time=datetime.now()
        )
        file_infos.append(file_info)
    
    # Categorize all files
    categorized = CategorizedFiles()
    
    for file_info in file_infos:
        category = categorizer.categorize(file_info)
        file_info.category = category
        
        if category == FileCategory.KEEP:
            categorized.keep.append(file_info)
        elif category == FileCategory.REMOVE:
            categorized.remove.append(file_info)
        elif category == FileCategory.CONSOLIDATE:
            categorized.consolidate.append(file_info)
        elif category == FileCategory.ARCHIVE:
            categorized.archive.append(file_info)
    
    # Property: Count consistency
    total_categorized = (
        len(categorized.keep) +
        len(categorized.remove) +
        len(categorized.consolidate) +
        len(categorized.archive)
    )
    
    assert total_categorized == num_files, (
        f"Count mismatch: Expected {num_files} files, "
        f"but got {total_categorized} categorized files"
    )


@given(
    st.lists(
        st.tuples(
            st.text(min_size=1, max_size=20, alphabet='abcdefghijklmnopqrstuvwxyz_/'),
            st.text(min_size=1, max_size=15, alphabet='abcdefghijklmnopqrstuvwxyz_.')
        ),
        min_size=1,
        max_size=50
    )
)
@settings(max_examples=10, deadline=None)
def test_audit_categorization_with_random_paths(path_tuples):
    """
    Property 9: Audit Categorization Completeness (Random Paths)
    
    For any set of randomly generated file paths, every file should be
    assigned exactly one category, and the total should match.
    
    **Validates: Requirements 8.2**
    """
    from scripts.cleanup.models import CategorizedFiles
    
    categorizer = FileCategorizer()
    
    # Create file paths from tuples
    file_paths = []
    for dir_part, file_part in path_tuples:
        # Clean up the parts
        dir_clean = dir_part.strip('/').replace('//', '/')
        file_clean = file_part.strip('.')
        
        if not file_clean:
            file_clean = "file.py"
        
        if dir_clean:
            file_paths.append(Path(dir_clean) / file_clean)
        else:
            file_paths.append(Path(file_clean))
    
    # Remove duplicates
    file_paths = list(dict.fromkeys(file_paths))
    
    if not file_paths:
        return  # Skip empty test case
    
    # Create FileInfo objects
    file_infos = []
    for file_path in file_paths:
        file_info = FileInfo(
            path=file_path,
            size=1024,
            modified_time=datetime.now()
        )
        file_infos.append(file_info)
    
    # Categorize all files
    categorized = CategorizedFiles()
    
    for file_info in file_infos:
        category = categorizer.categorize(file_info)
        file_info.category = category
        
        if category == FileCategory.KEEP:
            categorized.keep.append(file_info)
        elif category == FileCategory.REMOVE:
            categorized.remove.append(file_info)
        elif category == FileCategory.CONSOLIDATE:
            categorized.consolidate.append(file_info)
        elif category == FileCategory.ARCHIVE:
            categorized.archive.append(file_info)
    
    # Property: Every file has a category
    for file_info in file_infos:
        assert file_info.category is not None, (
            f"File '{file_info.path}' was not assigned a category"
        )
    
    # Property: Total count matches
    total_categorized = (
        len(categorized.keep) +
        len(categorized.remove) +
        len(categorized.consolidate) +
        len(categorized.archive)
    )
    
    assert total_categorized == len(file_infos), (
        f"Categorization count mismatch: "
        f"Scanned {len(file_infos)} files, categorized {total_categorized}"
    )
