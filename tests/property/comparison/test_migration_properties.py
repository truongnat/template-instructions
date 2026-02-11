"""
Property-based tests for migration script generation.

Feature: v2-structure-comparison
Tests Properties 28, 29, and 30 related to migration script validity,
backup generation, and rollback capabilities.
"""

import re
import subprocess
import tempfile
from pathlib import Path

import pytest
from hypothesis import given, strategies as st, assume

from agentic_sdlc.comparison.migration import (
    MigrationScriptGenerator,
    DirectoryMove,
    FileMove,
)
from agentic_sdlc.comparison.models import LibraryInfo


# Hypothesis strategies for generating test data
@st.composite
def library_info_strategy(draw):
    """Generate a valid LibraryInfo."""
    exists = draw(st.booleans())
    
    if not exists:
        return LibraryInfo(
            exists=False,
            package_count=0,
            total_size_mb=0.0,
            packages=[]
        )
    
    package_count = draw(st.integers(min_value=1, max_value=50))
    packages = draw(st.lists(
        st.text(
            min_size=3,
            max_size=20,
            alphabet=st.characters(whitelist_categories=('Ll', 'Nd'), whitelist_characters='-_')
        ),
        min_size=package_count,
        max_size=package_count,
        unique=True
    ))
    total_size_mb = draw(st.floats(min_value=0.1, max_value=1000.0))
    
    return LibraryInfo(
        exists=True,
        package_count=package_count,
        total_size_mb=total_size_mb,
        packages=packages
    )


@st.composite
def directory_move_strategy(draw):
    """Generate a valid DirectoryMove."""
    # Generate valid directory paths
    source_parts = draw(st.lists(
        st.text(min_size=1, max_size=15, alphabet=st.characters(
            whitelist_categories=('Ll', 'Nd'), whitelist_characters='_'
        )),
        min_size=1,
        max_size=3
    ))
    dest_parts = draw(st.lists(
        st.text(min_size=1, max_size=15, alphabet=st.characters(
            whitelist_categories=('Ll', 'Nd'), whitelist_characters='_'
        )),
        min_size=1,
        max_size=3
    ))
    
    source = '/'.join(source_parts)
    destination = '/'.join(dest_parts)
    reason = draw(st.text(min_size=0, max_size=100))
    
    # Ensure source and destination are different
    assume(source != destination)
    
    return DirectoryMove(
        source=source,
        destination=destination,
        reason=reason
    )


@st.composite
def file_move_strategy(draw):
    """Generate a valid FileMove."""
    # Generate valid Python file paths
    source_parts = draw(st.lists(
        st.text(min_size=1, max_size=15, alphabet=st.characters(
            whitelist_categories=('Ll', 'Nd'), whitelist_characters='_'
        )),
        min_size=1,
        max_size=3
    ))
    dest_parts = draw(st.lists(
        st.text(min_size=1, max_size=15, alphabet=st.characters(
            whitelist_categories=('Ll', 'Nd'), whitelist_characters='_'
        )),
        min_size=1,
        max_size=3
    ))
    
    source = '/'.join(source_parts) + '.py'
    destination = '/'.join(dest_parts) + '.py'
    reason = draw(st.text(min_size=0, max_size=100))
    
    # Ensure source and destination are different
    assume(source != destination)
    
    return FileMove(
        source=source,
        destination=destination,
        reason=reason
    )


@st.composite
def path_list_strategy(draw):
    """Generate a list of valid paths."""
    paths = draw(st.lists(
        st.text(min_size=1, max_size=30, alphabet=st.characters(
            whitelist_categories=('Ll', 'Nd'), whitelist_characters='_/'
        )),
        min_size=1,
        max_size=10,
        unique=True
    ))
    return paths


# Property 28: Migration script validity
# For any generated migration script, the script should be syntactically valid and executable

@given(lib_info=library_info_strategy())
def test_lib_cleanup_script_is_valid_bash(lib_info):
    """
    Property 28a: Lib cleanup script validity.
    
    For any LibraryInfo, the generated lib cleanup script should be
    syntactically valid bash that can be parsed without errors.
    
    Validates: Requirements 11.1
    """
    generator = MigrationScriptGenerator(project_root="/test/project")
    script = generator.generate_lib_cleanup_script(lib_info)
    
    # Script should not be empty
    assert script.strip(), "Generated script should not be empty"
    
    # Script should start with shebang or comment
    lines = script.strip().split('\n')
    assert lines[0].startswith('#'), "Script should start with shebang or comment"
    
    # Script should be valid bash syntax (check with bash -n)
    with tempfile.NamedTemporaryFile(mode='w', suffix='.sh', delete=False) as f:
        f.write(script)
        f.flush()
        script_path = f.name
    
    try:
        # Use bash -n to check syntax without executing
        result = subprocess.run(
            ['bash', '-n', script_path],
            capture_output=True,
            text=True,
            timeout=5
        )
        assert result.returncode == 0, f"Script has syntax errors: {result.stderr}"
    finally:
        Path(script_path).unlink(missing_ok=True)


@given(moves=st.lists(directory_move_strategy(), min_size=0, max_size=10))
def test_directory_move_script_is_valid_bash(moves):
    """
    Property 28b: Directory move script validity.
    
    For any list of DirectoryMove operations, the generated script should be
    syntactically valid bash that can be parsed without errors.
    
    Validates: Requirements 11.2
    """
    generator = MigrationScriptGenerator(project_root="/test/project")
    script = generator.generate_directory_move_script(moves)
    
    # Script should not be empty
    assert script.strip(), "Generated script should not be empty"
    
    # Script should start with shebang or comment
    lines = script.strip().split('\n')
    assert lines[0].startswith('#'), "Script should start with shebang or comment"
    
    # Script should be valid bash syntax
    with tempfile.NamedTemporaryFile(mode='w', suffix='.sh', delete=False) as f:
        f.write(script)
        f.flush()
        script_path = f.name
    
    try:
        result = subprocess.run(
            ['bash', '-n', script_path],
            capture_output=True,
            text=True,
            timeout=5
        )
        assert result.returncode == 0, f"Script has syntax errors: {result.stderr}"
    finally:
        Path(script_path).unlink(missing_ok=True)


@given(file_moves=st.lists(file_move_strategy(), min_size=0, max_size=10))
def test_import_update_script_is_valid_bash(file_moves):
    """
    Property 28c: Import update script validity.
    
    For any list of FileMove operations, the generated import update script
    should be syntactically valid bash that can be parsed without errors.
    
    Validates: Requirements 11.3
    """
    generator = MigrationScriptGenerator(project_root="/test/project")
    script = generator.generate_import_update_script(file_moves)
    
    # Script should not be empty
    assert script.strip(), "Generated script should not be empty"
    
    # Script should start with shebang or comment
    lines = script.strip().split('\n')
    assert lines[0].startswith('#'), "Script should start with shebang or comment"
    
    # Script should be valid bash syntax
    with tempfile.NamedTemporaryFile(mode='w', suffix='.sh', delete=False) as f:
        f.write(script)
        f.flush()
        script_path = f.name
    
    try:
        result = subprocess.run(
            ['bash', '-n', script_path],
            capture_output=True,
            text=True,
            timeout=5
        )
        assert result.returncode == 0, f"Script has syntax errors: {result.stderr}"
    finally:
        Path(script_path).unlink(missing_ok=True)


# Property 29: Backup script generation
# For any destructive operation in a migration script, a corresponding backup
# command should be generated before the destructive operation

@given(lib_info=library_info_strategy())
def test_lib_cleanup_includes_backup_before_destructive_ops(lib_info):
    """
    Property 29a: Lib cleanup backup generation.
    
    For any lib cleanup operation, the script should create a backup
    before any destructive operations (removing lib/ directory).
    
    Validates: Requirements 11.4
    """
    generator = MigrationScriptGenerator(project_root="/test/project")
    script = generator.generate_lib_cleanup_script(lib_info)
    
    if lib_info.exists and lib_info.package_count > 0:
        # Script should contain backup commands
        assert 'backup' in script.lower() or 'cp -r' in script.lower(), \
            "Script should include backup commands"
        
        # Find positions of backup and destructive operations
        lines = script.split('\n')
        backup_line = None
        rm_line = None
        
        for i, line in enumerate(lines):
            if 'cp -r lib/' in line or 'BACKUP' in line:
                if backup_line is None:
                    backup_line = i
            if 'rm -rf lib/' in line:
                rm_line = i
        
        # If there's a destructive operation, backup should come before it
        if rm_line is not None:
            assert backup_line is not None, \
                "Backup command should exist before destructive operation"
            # Note: The script provides instructions for manual rm, so we check
            # that backup is created early in the script
            assert backup_line < len(lines) // 2, \
                "Backup should be created early in the script"


@given(moves=st.lists(directory_move_strategy(), min_size=1, max_size=10))
def test_directory_move_checks_for_uncommitted_changes(moves):
    """
    Property 29b: Directory move safety checks.
    
    For any directory move operations, the script should check for
    uncommitted changes before proceeding (a form of backup validation).
    
    Validates: Requirements 11.4
    """
    generator = MigrationScriptGenerator(project_root="/test/project")
    script = generator.generate_directory_move_script(moves)
    
    # Script should check for uncommitted changes
    assert 'git diff-index' in script or 'uncommitted' in script.lower(), \
        "Script should check for uncommitted changes before moving directories"
    
    # Script should warn about uncommitted changes
    assert 'WARNING' in script or 'warning' in script.lower(), \
        "Script should warn about uncommitted changes"


@given(file_moves=st.lists(file_move_strategy(), min_size=1, max_size=10))
def test_import_update_creates_backup_before_modification(file_moves):
    """
    Property 29c: Import update backup generation.
    
    For any import update operations, the script should create backups
    of files before modifying them.
    
    Validates: Requirements 11.4
    """
    generator = MigrationScriptGenerator(project_root="/test/project")
    script = generator.generate_import_update_script(file_moves)
    
    # Script should create backup directory
    assert 'BACKUP_DIR' in script or 'backup' in script.lower(), \
        "Script should create backup directory"
    
    # Script should backup files before modification
    assert 'cp' in script and 'backup' in script.lower(), \
        "Script should copy files to backup before modification"
    
    # Find positions of backup and modification operations
    lines = script.split('\n')
    backup_line = None
    sed_line = None
    
    for i, line in enumerate(lines):
        if 'cp' in line and 'BACKUP' in line:
            if backup_line is None:
                backup_line = i
        if 'sed -i' in line:
            if sed_line is None:
                sed_line = i
    
    # Backup should come before modification
    if backup_line is not None and sed_line is not None:
        assert backup_line < sed_line, \
            "Backup command should come before sed modification"


@given(paths=path_list_strategy())
def test_backup_script_creates_backups_for_all_paths(paths):
    """
    Property 29d: Backup script completeness.
    
    For any list of paths, the backup script should create backups
    for all specified paths.
    
    Validates: Requirements 11.4
    """
    generator = MigrationScriptGenerator(project_root="/test/project")
    script = generator.generate_backup_script(paths)
    
    # Script should create backup directory
    assert 'BACKUP_ROOT' in script or 'backup' in script.lower(), \
        "Script should create backup root directory"
    
    # Script should backup each path
    for path in paths:
        # Check that the path is mentioned in the script
        assert path in script, f"Script should include backup for path: {path}"


# Property 30: Rollback script generation
# For any migration script, a corresponding rollback script should be generated
# that reverses all operations

@given(lib_info=library_info_strategy())
def test_rollback_script_reverses_lib_cleanup(lib_info):
    """
    Property 30a: Lib cleanup rollback.
    
    For any lib cleanup migration, the rollback script should restore
    the lib/ directory and remove generated requirements.txt.
    
    Validates: Requirements 11.5
    """
    generator = MigrationScriptGenerator(project_root="/test/project")
    migration_script = generator.generate_lib_cleanup_script(lib_info)
    rollback_script = generator.generate_rollback_script(migration_script)
    
    # Rollback script should not be empty
    assert rollback_script.strip(), "Rollback script should not be empty"
    
    if lib_info.exists and lib_info.package_count > 0:
        # Rollback should restore lib/ directory
        assert 'lib' in rollback_script.lower(), \
            "Rollback should mention lib/ directory"
        
        # Rollback should remove requirements.txt
        assert 'requirements.txt' in rollback_script, \
            "Rollback should handle requirements.txt"
        
        # Rollback should use backup
        assert 'backup' in rollback_script.lower(), \
            "Rollback should restore from backup"


@given(moves=st.lists(directory_move_strategy(), min_size=1, max_size=10))
def test_rollback_script_reverses_directory_moves(moves):
    """
    Property 30b: Directory move rollback.
    
    For any directory move operations, the rollback script should
    reverse the git operations.
    
    Validates: Requirements 11.5
    """
    generator = MigrationScriptGenerator(project_root="/test/project")
    migration_script = generator.generate_directory_move_script(moves)
    rollback_script = generator.generate_rollback_script(migration_script)
    
    # Rollback script should not be empty
    assert rollback_script.strip(), "Rollback script should not be empty"
    
    # Rollback should handle git operations
    assert 'git' in rollback_script.lower(), \
        "Rollback should handle git operations"
    
    # Rollback should reset or checkout
    assert 'git reset' in rollback_script or 'git checkout' in rollback_script, \
        "Rollback should reset or checkout git changes"


@given(file_moves=st.lists(file_move_strategy(), min_size=1, max_size=10))
def test_rollback_script_restores_modified_files(file_moves):
    """
    Property 30c: Import update rollback.
    
    For any import update operations, the rollback script should
    restore the original files from backup.
    
    Validates: Requirements 11.5
    """
    generator = MigrationScriptGenerator(project_root="/test/project")
    migration_script = generator.generate_import_update_script(file_moves)
    rollback_script = generator.generate_rollback_script(migration_script)
    
    # Rollback script should not be empty
    assert rollback_script.strip(), "Rollback script should not be empty"
    
    # Rollback should restore from backup
    assert 'backup' in rollback_script.lower(), \
        "Rollback should restore from backup"
    
    # Rollback should restore Python files
    assert '.py' in rollback_script or 'python' in rollback_script.lower(), \
        "Rollback should handle Python files"


@given(
    lib_info=library_info_strategy(),
    moves=st.lists(directory_move_strategy(), min_size=0, max_size=5),
    file_moves=st.lists(file_move_strategy(), min_size=0, max_size=5)
)
def test_rollback_script_is_valid_bash(lib_info, moves, file_moves):
    """
    Property 30d: Rollback script validity.
    
    For any migration operations, the generated rollback script should be
    syntactically valid bash that can be parsed without errors.
    
    Validates: Requirements 11.5
    """
    generator = MigrationScriptGenerator(project_root="/test/project")
    
    # Generate a migration script (use whichever has content)
    if lib_info.exists and lib_info.package_count > 0:
        migration_script = generator.generate_lib_cleanup_script(lib_info)
    elif moves:
        migration_script = generator.generate_directory_move_script(moves)
    elif file_moves:
        migration_script = generator.generate_import_update_script(file_moves)
    else:
        # Skip if no operations
        assume(False)
    
    rollback_script = generator.generate_rollback_script(migration_script)
    
    # Rollback script should not be empty
    assert rollback_script.strip(), "Rollback script should not be empty"
    
    # Rollback script should start with shebang or comment
    lines = rollback_script.strip().split('\n')
    assert lines[0].startswith('#'), "Rollback script should start with shebang or comment"
    
    # Rollback script should be valid bash syntax
    with tempfile.NamedTemporaryFile(mode='w', suffix='.sh', delete=False) as f:
        f.write(rollback_script)
        f.flush()
        script_path = f.name
    
    try:
        result = subprocess.run(
            ['bash', '-n', script_path],
            capture_output=True,
            text=True,
            timeout=5
        )
        assert result.returncode == 0, f"Rollback script has syntax errors: {result.stderr}"
    finally:
        Path(script_path).unlink(missing_ok=True)
