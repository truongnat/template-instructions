"""
Property-based tests for Internal Module Privacy (SDK Reorganization).

These tests use Hypothesis to verify that internal modules are properly hidden
from the public API and that private implementation details are not exposed.

Feature: sdk-reorganization
Property 2: Internal Module Privacy
Requirements: 3.3
"""

import pytest
import importlib
from hypothesis import given, strategies as st, settings
from typing import Any

import agentic_sdlc


# Strategy for generating module names that should be private (start with underscore)
private_module_names = st.sampled_from([
    "_internal",
])

# Strategy for generating valid public module names
public_module_names = st.sampled_from([
    "core",
    "infrastructure",
    "intelligence",
    "orchestration",
    "plugins",
])


# Feature: sdk-reorganization, Property 2: Internal Module Privacy
def test_private_modules_not_in_all_export():
    """
    Property: For any module prefixed with single underscore in the agentic_sdlc package,
    it SHALL NOT be included in the __all__ export list.
    
    This property ensures that private modules are not exposed through the public API.
    
    **Validates: Requirements 3.3**
    """
    # Get the __all__ list from the main package
    all_exports = agentic_sdlc.__all__
    
    # Verify that no private modules (single underscore prefix, not dunder) are in __all__
    private_modules = [
        name for name in all_exports
        if name.startswith("_") and not name.startswith("__")
    ]
    
    assert len(private_modules) == 0, (
        f"Private modules (starting with single _) should not be in __all__. "
        f"Found: {private_modules}"
    )


# Feature: sdk-reorganization, Property 2: Internal Module Privacy
@given(private_module=private_module_names)
@settings(max_examples=100, deadline=None)
def test_private_modules_not_in_all_list(private_module):
    """
    Property: For any private module (prefixed with underscore),
    it SHALL NOT be in the __all__ list.
    
    This property ensures that private modules are not exposed through __all__.
    
    **Validates: Requirements 3.3**
    """
    all_exports = agentic_sdlc.__all__
    
    # Private module should not be in __all__
    assert private_module not in all_exports, (
        f"Private module {private_module} should not be in __all__"
    )


# Feature: sdk-reorganization, Property 2: Internal Module Privacy
def test_internal_module_has_empty_all():
    """
    Property: For the _internal module, its __all__ list SHALL be empty.
    
    This property ensures that the _internal module doesn't export anything.
    
    **Validates: Requirements 3.3**
    """
    # Import the _internal module
    from agentic_sdlc import _internal
    
    # Verify __all__ is empty
    assert hasattr(_internal, "__all__"), "_internal module should have __all__"
    assert _internal.__all__ == [], (
        f"_internal.__all__ should be empty, but got: {_internal.__all__}"
    )


# Feature: sdk-reorganization, Property 2: Internal Module Privacy
def test_version_string_is_in_public_api():
    """
    Property: For the __version__ string, it SHALL be in the public API's __all__.
    
    This property ensures that version info is properly exposed.
    
    **Validates: Requirements 3.3**
    """
    # __version__ should be in __all__
    assert "__version__" in agentic_sdlc.__all__, (
        "__version__ should be in __all__"
    )
    
    # __version__ should be accessible
    assert hasattr(agentic_sdlc, "__version__"), (
        "__version__ should be accessible from public API"
    )


# Feature: sdk-reorganization, Property 2: Internal Module Privacy
@given(public_module=public_module_names)
@settings(max_examples=100, deadline=None)
def test_public_modules_are_importable(public_module):
    """
    Property: For any public module (not prefixed with underscore),
    it SHALL be importable from the package.
    
    This property ensures that public modules are properly exposed.
    
    **Validates: Requirements 3.3**
    """
    # Public modules should be importable
    try:
        importlib.import_module(f"agentic_sdlc.{public_module}")
    except ImportError as e:
        pytest.fail(f"Public module {public_module} should be importable: {e}")


# Feature: sdk-reorganization, Property 2: Internal Module Privacy
def test_all_exports_are_public_symbols():
    """
    Property: For any symbol in __all__, it SHALL be a public symbol
    (not prefixed with single underscore, excluding dunder names).
    
    This property ensures that __all__ only contains public symbols.
    
    **Validates: Requirements 3.3**
    """
    all_exports = agentic_sdlc.__all__
    
    # Check that all exports are public (don't start with single underscore)
    # Dunder names like __version__ are allowed
    private_exports = [
        name for name in all_exports
        if name.startswith("_") and not name.startswith("__")
    ]
    
    assert len(private_exports) == 0, (
        f"__all__ should only contain public symbols. "
        f"Found private symbols: {private_exports}"
    )


# Feature: sdk-reorganization, Property 2: Internal Module Privacy
def test_all_exports_are_actually_defined():
    """
    Property: For any symbol in __all__, it SHALL be actually defined
    in the module (accessible via getattr).
    
    This property ensures that __all__ doesn't reference undefined symbols.
    
    **Validates: Requirements 3.3**
    """
    all_exports = agentic_sdlc.__all__
    
    # Check that all exports are actually defined
    undefined_exports = []
    for name in all_exports:
        try:
            getattr(agentic_sdlc, name)
        except AttributeError:
            undefined_exports.append(name)
    
    assert len(undefined_exports) == 0, (
        f"All symbols in __all__ should be defined. "
        f"Undefined symbols: {undefined_exports}"
    )


# Feature: sdk-reorganization, Property 2: Internal Module Privacy
def test_internal_module_docstring_indicates_private():
    """
    Property: For the _internal module, its docstring SHALL indicate
    that it is private and should not be imported by external code.
    
    This property ensures that the module is clearly marked as private.
    
    **Validates: Requirements 3.3**
    """
    from agentic_sdlc import _internal
    
    # Check that docstring exists and mentions private/internal
    assert _internal.__doc__ is not None, "_internal module should have a docstring"
    
    docstring_lower = _internal.__doc__.lower()
    assert any(word in docstring_lower for word in ["private", "internal", "should not"]), (
        f"_internal module docstring should indicate it's private. "
        f"Got: {_internal.__doc__}"
    )


# Feature: sdk-reorganization, Property 2: Internal Module Privacy
def test_private_modules_not_in_all_exports():
    """
    Property: For the __all__ list, it SHALL NOT contain any private modules
    (modules prefixed with single underscore, excluding dunder names).
    
    This property ensures that private modules are not exposed.
    
    **Validates: Requirements 3.3**
    """
    all_exports = agentic_sdlc.__all__
    
    # Check that no private modules (single underscore prefix) are in __all__
    private_exports = [
        name for name in all_exports
        if name.startswith("_") and not name.startswith("__")
    ]
    
    assert len(private_exports) == 0, (
        f"__all__ should not contain private modules. "
        f"Found: {private_exports}"
    )


# Feature: sdk-reorganization, Property 2: Internal Module Privacy
def test_importing_from_internal_module_is_discouraged():
    """
    Property: For the _internal module, importing from it directly
    SHALL be possible (Python allows it) but the module's __all__ being empty
    indicates it should not be used.
    
    This property ensures that the _internal module is marked as not for public use.
    
    **Validates: Requirements 3.3**
    """
    # The _internal module can be imported (Python allows it)
    from agentic_sdlc import _internal
    
    # But its __all__ is empty, indicating nothing should be imported from it
    assert _internal.__all__ == [], (
        "_internal.__all__ should be empty to discourage imports"
    )
    
    # And it should not be in the parent's __all__
    assert "_internal" not in agentic_sdlc.__all__, (
        "_internal should not be in parent's __all__"
    )


# Feature: sdk-reorganization, Property 2: Internal Module Privacy
def test_cli_module_is_not_in_public_api():
    """
    Property: For the cli module, it SHALL NOT be in the public API's __all__
    (CLI is optional and should be imported separately if needed).
    
    This property ensures that CLI is not part of the core public API.
    
    **Validates: Requirements 3.3**
    """
    # cli should not be in __all__
    assert "cli" not in agentic_sdlc.__all__, (
        "cli should not be in public API's __all__"
    )


# Feature: sdk-reorganization, Property 2: Internal Module Privacy
def test_all_list_is_comprehensive():
    """
    Property: For the public API, the __all__ list SHALL include all
    intended public symbols (classes, functions, exceptions, etc.).
    
    This property ensures that __all__ list is complete.
    
    **Validates: Requirements 3.3**
    """
    all_exports = agentic_sdlc.__all__
    
    # Should have a reasonable number of exports (at least 10)
    assert len(all_exports) >= 10, (
        f"__all__ should have at least 10 public exports, got {len(all_exports)}"
    )
    
    # Should include version
    assert "__version__" in all_exports, (
        "__version__ should be in __all__"
    )
    
    # Should include at least one exception
    exception_exports = [
        name for name in all_exports
        if "Error" in name or "Exception" in name
    ]
    assert len(exception_exports) > 0, (
        "__all__ should include at least one exception class"
    )


# Feature: sdk-reorganization, Property 2: Internal Module Privacy
def test_no_duplicate_exports_in_all():
    """
    Property: For the __all__ list, it SHALL NOT contain duplicate entries.
    
    This property ensures that __all__ is well-formed.
    
    **Validates: Requirements 3.3**
    """
    all_exports = agentic_sdlc.__all__
    
    # Check for duplicates
    duplicates = [name for name in all_exports if all_exports.count(name) > 1]
    
    assert len(duplicates) == 0, (
        f"__all__ should not contain duplicates. Found: {set(duplicates)}"
    )


# Feature: sdk-reorganization, Property 2: Internal Module Privacy
def test_all_exports_are_strings():
    """
    Property: For the __all__ list, all entries SHALL be strings.
    
    This property ensures that __all__ is properly formatted.
    
    **Validates: Requirements 3.3**
    """
    all_exports = agentic_sdlc.__all__
    
    # Check that all entries are strings
    non_string_exports = [name for name in all_exports if not isinstance(name, str)]
    
    assert len(non_string_exports) == 0, (
        f"All entries in __all__ should be strings. "
        f"Found non-strings: {non_string_exports}"
    )


# Feature: sdk-reorganization, Property 2: Internal Module Privacy
def test_all_exports_are_valid_identifiers():
    """
    Property: For the __all__ list, all entries SHALL be valid Python identifiers.
    
    This property ensures that __all__ contains valid symbol names.
    
    **Validates: Requirements 3.3**
    """
    all_exports = agentic_sdlc.__all__
    
    # Check that all entries are valid identifiers
    invalid_identifiers = [
        name for name in all_exports
        if not name.isidentifier()
    ]
    
    assert len(invalid_identifiers) == 0, (
        f"All entries in __all__ should be valid identifiers. "
        f"Found invalid: {invalid_identifiers}"
    )
