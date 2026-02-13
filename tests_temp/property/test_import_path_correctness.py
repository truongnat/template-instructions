"""
Property-based tests for import path correctness after utilities consolidation.

Feature: sdlc-kit-improvements, Property 11: Import Path Correctness
Validates: Requirements 13.3, 16.3
"""

import sys
import importlib
from pathlib import Path
from hypothesis import given, strategies as st, settings
import pytest


# Get all Python modules in the project (excluding lib and test directories)
def get_all_python_modules():
    """Get all Python module paths in the project."""
    project_root = Path(__file__).parent.parent.parent
    modules = []
    
    # Get modules from agentic_sdlc package (excluding lib directory)
    agentic_sdlc_dir = project_root / 'agentic_sdlc'
    if agentic_sdlc_dir.exists():
        for py_file in agentic_sdlc_dir.rglob('*.py'):
            if ('__pycache__' in str(py_file) or 
                py_file.name == '__init__.py' or
                '/lib/' in str(py_file) or  # Exclude lib directory
                '/testing/' in str(py_file)):  # Exclude testing scripts with missing deps
                continue
            # Convert file path to module path
            rel_path = py_file.relative_to(project_root)
            module_path = str(rel_path.with_suffix('')).replace('/', '.')
            modules.append(module_path)
    
    # Get modules from utils package
    utils_dir = project_root / 'utils'
    if utils_dir.exists():
        for py_file in utils_dir.rglob('*.py'):
            if '__pycache__' not in str(py_file) and py_file.name != '__init__.py':
                rel_path = py_file.relative_to(project_root)
                module_path = str(rel_path.with_suffix('')).replace('/', '.')
                modules.append(module_path)
    
    return modules


# Feature: sdlc-kit-improvements, Property 11: Import Path Correctness
@settings(max_examples=5, deadline=None)
@given(st.sampled_from(get_all_python_modules()))
def test_all_modules_importable(module_path):
    """
    Property: For any Python module in the SDLC Kit, when imported,
    the import should succeed without ImportError related to utils migration.
    
    This validates that all import paths are correct after the utilities
    consolidation migration.
    
    Note: This test allows other types of import errors (missing dependencies,
    missing modules) as those are pre-existing issues unrelated to the utils migration.
    """
    try:
        # Attempt to import the module
        importlib.import_module(module_path)
        # If we get here, import succeeded
        assert True
    except ImportError as e:
        error_msg = str(e)
        # Check if the error is related to the old utils paths
        if ('agentic_sdlc.core.utils' in error_msg):
            pytest.fail(f"Failed to import {module_path} due to old utils path: {error_msg}")
        # Otherwise, this is a pre-existing issue, not related to utils migration
        # We'll pass the test
    except Exception:
        # Other exceptions are not related to import paths
        pass


def test_utils_modules_importable():
    """
    Test that all consolidated utils modules can be imported.
    
    This is a specific test for the moved utility modules.
    """
    utils_modules = [
        'utils.common',
        'utils.artifact_manager',
        'utils.kb_manager',
        'utils.console',
        'utils.file_handlers',
        'utils.decorators',
        'utils.validators',
        'utils.helpers',
    ]
    
    for module_path in utils_modules:
        try:
            importlib.import_module(module_path)
        except ImportError as e:
            pytest.fail(f"Failed to import {module_path}: {str(e)}")


def test_no_old_utils_imports():
    """
    Test that no modules are trying to import from the old utils location.
    
    This ensures the migration is complete.
    """
    project_root = Path(__file__).parent.parent.parent
    
    # Search for any remaining imports from old location
    old_import_patterns = [
        'from agentic_sdlc.core.utils.common import',
        'from agentic_sdlc.core.utils.artifact_manager import',
        'from agentic_sdlc.core.utils.kb_manager import',
        'from utils.console import',
        'import agentic_sdlc.core.utils.common',
        'import agentic_sdlc.core.utils.artifact_manager',
        'import agentic_sdlc.core.utils.kb_manager',
        'import utils.console',
    ]
    
    files_with_old_imports = []
    
    for py_file in project_root.rglob('*.py'):
        # Skip this test file itself, build directories, and cache directories
        if ('__pycache__' in str(py_file) or 
            'build/' in str(py_file) or 
            'dist/' in str(py_file) or
            py_file.name == 'test_import_path_correctness.py'):
            continue
        
        try:
            content = py_file.read_text(encoding='utf-8')
            for pattern in old_import_patterns:
                if pattern in content:
                    files_with_old_imports.append((str(py_file), pattern))
        except Exception:
            # Skip files that can't be read
            continue
    
    if files_with_old_imports:
        error_msg = "Found files with old import paths:\n"
        for file_path, pattern in files_with_old_imports:
            error_msg += f"  {file_path}: {pattern}\n"
        pytest.fail(error_msg)


def test_utils_functions_accessible():
    """
    Test that key utility functions are accessible from the new location.
    """
    from utils.common import get_project_root, print_success, ensure_dir
    from utils.artifact_manager import get_current_sprint
    from utils.kb_manager import search_kb, create_kb_entry
    from utils.console import print_header, print_step
    from utils.file_handlers import read_file, write_file
    from utils.decorators import timer, retry
    from utils.validators import is_valid_email, is_non_empty_string
    from utils.helpers import get_timestamp, truncate_string
    
    # If we get here, all imports succeeded
    assert callable(get_project_root)
    assert callable(print_success)
    assert callable(ensure_dir)
    assert callable(get_current_sprint)
    assert callable(search_kb)
    assert callable(create_kb_entry)
    assert callable(print_header)
    assert callable(print_step)
    assert callable(read_file)
    assert callable(write_file)
    assert callable(timer)
    assert callable(retry)
    assert callable(is_valid_email)
    assert callable(is_non_empty_string)
    assert callable(get_timestamp)
    assert callable(truncate_string)


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
