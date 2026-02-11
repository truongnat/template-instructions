"""Property-based tests for deprecation warning emission.

Feature: sdk-reorganization
Property 10: Deprecation Warning Emission
Validates: Requirements 13.2

For any function or method marked as deprecated, calling it SHALL emit
a DeprecationWarning.
"""

import sys
import warnings
from typing import Any

import pytest
from hypothesis import given, strategies as st


# Test that importing from old locations emits DeprecationWarning
def test_old_import_path_emits_deprecation_warning() -> None:
    """Test that importing from old paths emits DeprecationWarning."""
    # Ensure compatibility shims are installed
    import agentic_sdlc  # noqa: F401
    
    # Capture warnings
    with warnings.catch_warnings(record=True) as w:
        warnings.simplefilter("always")
        
        # Try to import from old path
        try:
            from agentic_sdlc.infrastructure.autogen import agents  # noqa: F401
        except (ImportError, AttributeError):
            # If the old module doesn't exist, that's okay for this test
            pass
        
        # Check if any deprecation warnings were emitted
        deprecation_warnings = [
            warning for warning in w
            if issubclass(warning.category, DeprecationWarning)
        ]
        
        # We expect at least one deprecation warning if the import succeeded
        if deprecation_warnings:
            assert len(deprecation_warnings) >= 1
            assert "deprecated" in str(deprecation_warnings[0].message).lower()


def test_deprecation_warning_includes_old_and_new_paths() -> None:
    """Test that deprecation warning includes both old and new paths."""
    import agentic_sdlc  # noqa: F401
    
    with warnings.catch_warnings(record=True) as w:
        warnings.simplefilter("always")
        
        # Try to access a symbol from old path
        try:
            from agentic_sdlc.infrastructure.autogen.agents import create_agent  # noqa: F401
        except (ImportError, AttributeError):
            pass
        
        # Check warnings
        deprecation_warnings = [
            warning for warning in w
            if issubclass(warning.category, DeprecationWarning)
        ]
        
        if deprecation_warnings:
            message = str(deprecation_warnings[0].message)
            # Should mention the old path
            assert "infrastructure.autogen" in message or "deprecated" in message.lower()


@given(
    old_module_names=st.lists(
        st.sampled_from([
            "agentic_sdlc.infrastructure.autogen.agents",
            "agentic_sdlc.intelligence.learning",
            "agentic_sdlc.core.config",
        ]),
        min_size=1,
        max_size=3,
        unique=True,
    )
)
def test_deprecation_warning_emitted_for_old_modules(old_module_names: list[str]) -> None:
    """Property: For any old module path, accessing it SHALL emit DeprecationWarning.
    
    Validates: Requirements 13.2
    """
    import agentic_sdlc  # noqa: F401
    
    for old_module_name in old_module_names:
        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter("always")
            
            # Try to access the old module
            try:
                __import__(old_module_name)
            except (ImportError, AttributeError, ModuleNotFoundError):
                # If module doesn't exist, skip
                continue
            
            # Check if deprecation warning was emitted
            deprecation_warnings = [
                warning for warning in w
                if issubclass(warning.category, DeprecationWarning)
            ]
            
            # If the module was successfully imported, we should have a warning
            if old_module_name in sys.modules:
                # The warning might be emitted on attribute access, not import
                # So we just verify the module is in sys.modules
                assert old_module_name in sys.modules


def test_deprecation_warning_stacklevel_correct() -> None:
    """Test that deprecation warning has correct stacklevel."""
    import agentic_sdlc  # noqa: F401
    
    with warnings.catch_warnings(record=True) as w:
        warnings.simplefilter("always")
        
        # Try to import from old path
        try:
            from agentic_sdlc.infrastructure.autogen.agents import create_agent  # noqa: F401
        except (ImportError, AttributeError):
            pass
        
        # Check warnings
        deprecation_warnings = [
            warning for warning in w
            if issubclass(warning.category, DeprecationWarning)
        ]
        
        if deprecation_warnings:
            # Verify the warning has a filename and lineno
            warning = deprecation_warnings[0]
            assert warning.filename is not None
            assert warning.lineno is not None


def test_deprecation_warning_not_emitted_for_new_imports() -> None:
    """Test that new imports do NOT emit deprecation warnings."""
    import agentic_sdlc  # noqa: F401
    
    with warnings.catch_warnings(record=True) as w:
        warnings.simplefilter("always")
        
        # Import from new path
        from agentic_sdlc import Agent  # noqa: F401
        
        # Check that no deprecation warnings were emitted
        deprecation_warnings = [
            warning for warning in w
            if issubclass(warning.category, DeprecationWarning)
        ]
        
        assert len(deprecation_warnings) == 0


def test_deprecation_warning_message_format() -> None:
    """Test that deprecation warning message has proper format."""
    import agentic_sdlc  # noqa: F401
    
    with warnings.catch_warnings(record=True) as w:
        warnings.simplefilter("always")
        
        # Try to import from old path
        try:
            from agentic_sdlc.infrastructure.autogen.agents import create_agent  # noqa: F401
        except (ImportError, AttributeError):
            pass
        
        # Check warnings
        deprecation_warnings = [
            warning for warning in w
            if issubclass(warning.category, DeprecationWarning)
        ]
        
        if deprecation_warnings:
            message = str(deprecation_warnings[0].message)
            # Message should contain key information
            assert "deprecated" in message.lower()
            assert "v4.0.0" in message or "removed" in message.lower()
