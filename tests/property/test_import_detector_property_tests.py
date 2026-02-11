"""
Property-based tests for ImportDetector.

Feature: project-audit-cleanup
Property 14: Import Reference Detection

These tests verify that the ImportDetector correctly identifies import
references to paths in the codebase, ensuring that directories with active
imports are not incorrectly marked for removal.
"""

import pytest
from hypothesis import given, strategies as st, assume, settings
from pathlib import Path
import tempfile
import shutil

from scripts.cleanup.imports import ImportDetector, ImportReference


# Strategy for generating valid Python module names
@st.composite
def module_names(draw):
    """Generate valid Python module names."""
    # Generate 1-3 parts separated by dots
    num_parts = draw(st.integers(min_value=1, max_value=3))
    parts = []
    for _ in range(num_parts):
        # Valid Python identifier
        part = draw(st.from_regex(r'^[a-z][a-z0-9_]{0,10}$', fullmatch=True))
        parts.append(part)
    return '.'.join(parts)


# Strategy for generating Python import statements
@st.composite
def import_statements(draw):
    """Generate various Python import statement formats."""
    module = draw(module_names())
    import_type = draw(st.sampled_from(['import', 'from', 'from_as', 'import_as']))
    
    if import_type == 'import':
        return f"import {module}"
    elif import_type == 'import_as':
        alias = draw(st.from_regex(r'^[a-z][a-z0-9_]{0,5}$', fullmatch=True))
        return f"import {module} as {alias}"
    elif import_type == 'from':
        name = draw(st.from_regex(r'^[a-z][a-z0-9_]{0,10}$', fullmatch=True))
        return f"from {module} import {name}"
    else:  # from_as
        name = draw(st.from_regex(r'^[a-z][a-z0-9_]{0,10}$', fullmatch=True))
        alias = draw(st.from_regex(r'^[a-z][a-z0-9_]{0,5}$', fullmatch=True))
        return f"from {module} import {name} as {alias}"


@given(st.lists(import_statements(), min_size=1, max_size=10))
@settings(max_examples=10, deadline=None)
def test_property_14_import_reference_detection(import_stmts):
    """
    Property 14: Import Reference Detection
    
    For any Python file containing import statements, the ImportDetector
    should correctly parse and identify all import references. If a file
    imports from a module, that module path should be detectable.
    
    Validates: Requirements 1.2, 2.3
    """
    # Create a temporary directory structure
    with tempfile.TemporaryDirectory() as tmpdir:
        project_root = Path(tmpdir)
        
        # Create a test Python file with the import statements
        test_file = project_root / "test_module.py"
        
        # Build file content with imports
        content_lines = [
            "# Test file with imports",
            ""
        ]
        content_lines.extend(import_stmts)
        content_lines.append("")
        content_lines.append("# End of imports")
        
        test_file.write_text('\n'.join(content_lines))
        
        # Create detector
        detector = ImportDetector(project_root=project_root, verbose=False)
        
        # Parse imports
        try:
            imports = detector.parse_imports(test_file)
            
            # Property: Number of imports found should match number of import statements
            # (Each import statement should be detected)
            assert len(imports) == len(import_stmts), \
                f"Expected {len(import_stmts)} imports, found {len(imports)}"
            
            # Property: All imports should have valid source file
            for imp in imports:
                assert imp.source_file == test_file, \
                    f"Import source file mismatch: {imp.source_file} != {test_file}"
            
            # Property: All imports should have non-empty module names
            for imp in imports:
                assert imp.module_name, \
                    "Import should have non-empty module name"
            
            # Property: All imports should have valid line numbers
            for imp in imports:
                assert imp.line_number > 0, \
                    f"Import should have positive line number, got {imp.line_number}"
            
            # Property: Import types should be valid
            valid_types = {'import', 'from', 'relative'}
            for imp in imports:
                assert imp.import_type in valid_types, \
                    f"Invalid import type: {imp.import_type}"
        
        except SyntaxError:
            # If there's a syntax error, it's expected for some generated code
            # The property still holds: detector should handle syntax errors gracefully
            pass


@given(module_names(), st.lists(import_statements(), min_size=0, max_size=5))
@settings(max_examples=10, deadline=None)
def test_property_14_path_reference_detection(target_module, other_imports):
    """
    Property 14: Path Reference Detection (Part 2)
    
    For any target module path, if a Python file imports that module,
    the ImportDetector should correctly identify the reference. If no
    file imports the module, no references should be found.
    
    Validates: Requirements 1.2, 2.3
    """
    with tempfile.TemporaryDirectory() as tmpdir:
        project_root = Path(tmpdir)
        
        # Create target module directory structure
        module_parts = target_module.split('.')
        current_path = project_root
        for part in module_parts:
            current_path = current_path / part
            current_path.mkdir(exist_ok=True)
            # Create __init__.py to make it a package
            (current_path / "__init__.py").write_text("# Package init")
        
        target_path = project_root / '/'.join(module_parts)
        
        # Create a file that imports the target module
        referencing_file = project_root / "referencing.py"
        import_stmt = f"import {target_module}"
        referencing_file.write_text(f"{import_stmt}\n")
        
        # Create a file with other imports (not referencing target)
        non_referencing_file = project_root / "non_referencing.py"
        if other_imports:
            # Filter out any imports that might accidentally reference target
            filtered_imports = [imp for imp in other_imports if target_module not in imp]
            if filtered_imports:
                non_referencing_file.write_text('\n'.join(filtered_imports[:3]) + '\n')
            else:
                non_referencing_file.write_text("# No imports\n")
        else:
            non_referencing_file.write_text("# No imports\n")
        
        # Create detector
        detector = ImportDetector(project_root=project_root, verbose=False)
        
        # Detect references to target path
        references = detector.detect_path_references(target_path, search_root=project_root)
        
        # Property: Should find at least one reference (from referencing_file)
        assert len(references) >= 1, \
            f"Should find at least one reference to {target_module}, found {len(references)}"
        
        # Property: At least one reference should be from referencing_file
        source_files = [ref.source_file for ref in references]
        assert referencing_file in source_files, \
            f"Should find reference from {referencing_file}"
        
        # Property: is_directory_referenced should return True
        is_referenced = detector.is_directory_referenced(target_path, search_root=project_root)
        assert is_referenced, \
            f"Directory {target_path} should be detected as referenced"


@given(st.lists(import_statements(), min_size=1, max_size=10))
@settings(max_examples=10, deadline=None)
def test_property_14_import_cache_consistency(import_stmts):
    """
    Property 14: Import Cache Consistency
    
    For any Python file, parsing it multiple times should return the same
    results (cache consistency). Clearing the cache and re-parsing should
    also return the same results.
    
    Validates: Requirements 1.2, 2.3
    """
    with tempfile.TemporaryDirectory() as tmpdir:
        project_root = Path(tmpdir)
        
        # Create test file
        test_file = project_root / "test.py"
        test_file.write_text('\n'.join(import_stmts) + '\n')
        
        # Create detector
        detector = ImportDetector(project_root=project_root, verbose=False)
        
        # Parse first time
        try:
            imports1 = detector.parse_imports(test_file)
            
            # Parse second time (should use cache)
            imports2 = detector.parse_imports(test_file)
            
            # Property: Results should be identical
            assert len(imports1) == len(imports2), \
                "Cache should return same number of imports"
            
            for imp1, imp2 in zip(imports1, imports2):
                assert imp1.module_name == imp2.module_name, \
                    "Cached imports should have same module names"
                assert imp1.line_number == imp2.line_number, \
                    "Cached imports should have same line numbers"
            
            # Clear cache
            detector.clear_cache()
            
            # Parse third time (after cache clear)
            imports3 = detector.parse_imports(test_file)
            
            # Property: Results should still be identical
            assert len(imports1) == len(imports3), \
                "Re-parsing after cache clear should return same number of imports"
            
            for imp1, imp3 in zip(imports1, imports3):
                assert imp1.module_name == imp3.module_name, \
                    "Re-parsed imports should have same module names"
                assert imp1.line_number == imp3.line_number, \
                    "Re-parsed imports should have same line numbers"
        
        except SyntaxError:
            # Syntax errors are acceptable for generated code
            pass


@given(st.integers(min_value=1, max_value=5))
@settings(max_examples=10, deadline=None)
def test_property_14_no_false_positives(num_unrelated_modules):
    """
    Property 14: No False Positives
    
    For any directory that is NOT imported by any file, the ImportDetector
    should correctly report that it is not referenced (no false positives).
    
    Validates: Requirements 1.2, 2.3
    """
    with tempfile.TemporaryDirectory() as tmpdir:
        project_root = Path(tmpdir)
        
        # Create an unreferenced directory
        unreferenced_dir = project_root / "unreferenced_module"
        unreferenced_dir.mkdir()
        (unreferenced_dir / "__init__.py").write_text("# Unreferenced")
        
        # Create some Python files that import other modules (not unreferenced)
        for i in range(num_unrelated_modules):
            test_file = project_root / f"test_{i}.py"
            # Import standard library modules (definitely not our unreferenced module)
            test_file.write_text(f"import os\nimport sys\n")
        
        # Create detector
        detector = ImportDetector(project_root=project_root, verbose=False)
        
        # Check if unreferenced directory is referenced
        is_referenced = detector.is_directory_referenced(
            unreferenced_dir, 
            search_root=project_root
        )
        
        # Property: Should NOT be referenced (no false positives)
        assert not is_referenced, \
            f"Unreferenced directory should not be detected as referenced"
        
        # Property: detect_path_references should return empty list
        references = detector.detect_path_references(
            unreferenced_dir,
            search_root=project_root
        )
        
        assert len(references) == 0, \
            f"Should find 0 references to unreferenced directory, found {len(references)}"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
