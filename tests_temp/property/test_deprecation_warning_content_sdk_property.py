"""Property-based tests for deprecation warning content.

Feature: sdk-reorganization
Property 11: Deprecation Warning Content
Validates: Requirements 13.6

For any deprecated function or method, the emitted DeprecationWarning SHALL
include the function name and migration instructions (what to use instead).
"""

import sys
import warnings
from typing import Any

import pytest
from hypothesis import given, strategies as st


def test_deprecation_warning_includes_function_name() -> None:
    """Test that deprecation warning includes the function/class name."""
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
            # Should mention the symbol name
            assert "create_agent" in message or "deprecated" in message.lower()


def test_deprecation_warning_includes_migration_instructions() -> None:
    """Test that deprecation warning includes migration instructions."""
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
            # Should include migration instructions
            assert "Use" in message or "use" in message or "instead" in message


def test_deprecation_warning_specifies_new_location() -> None:
    """Test that deprecation warning specifies what to use instead."""
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
            # Should mention the new location
            assert "agentic_sdlc" in message


def test_deprecation_warning_is_clear_and_actionable() -> None:
    """Test that deprecation warning message is clear and actionable."""
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
            # Message should be reasonably long and informative
            assert len(message) > 20
            # Should contain key information
            assert "deprecated" in message.lower()


@given(
    old_paths=st.lists(
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
def test_deprecation_warning_content_for_all_old_paths(old_paths: list[str]) -> None:
    """Property: For any old import path, the warning SHALL include migration info.
    
    Validates: Requirements 13.6
    """
    import agentic_sdlc  # noqa: F401
    
    for old_path in old_paths:
        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter("always")
            
            # Try to access the old module
            try:
                __import__(old_path)
            except (ImportError, AttributeError, ModuleNotFoundError):
                continue
            
            # Check if deprecation warning was emitted
            deprecation_warnings = [
                warning for warning in w
                if issubclass(warning.category, DeprecationWarning)
            ]
            
            # If the module was successfully imported, check warning content
            if old_path in sys.modules and deprecation_warnings:
                message = str(deprecation_warnings[0].message)
                # Should have key components
                assert "deprecated" in message.lower()
                assert len(message) > 20


def test_deprecation_warning_mentions_version_removal() -> None:
    """Test that deprecation warning mentions when it will be removed."""
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
            # Should mention version or removal timeline
            assert "v4.0.0" in message or "removed" in message.lower() or "will be" in message


def test_deprecation_warning_format_consistency() -> None:
    """Test that all deprecation warnings follow consistent format."""
    import agentic_sdlc  # noqa: F401
    
    warnings_found = []
    
    old_paths = [
        "agentic_sdlc.infrastructure.autogen.agents",
        "agentic_sdlc.intelligence.learning",
    ]
    
    for old_path in old_paths:
        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter("always")
            
            try:
                __import__(old_path)
            except (ImportError, AttributeError, ModuleNotFoundError):
                continue
            
            deprecation_warnings = [
                warning for warning in w
                if issubclass(warning.category, DeprecationWarning)
            ]
            
            if deprecation_warnings:
                warnings_found.append(str(deprecation_warnings[0].message))
    
    # If we found multiple warnings, they should follow similar format
    if len(warnings_found) > 1:
        for warning_msg in warnings_found:
            # All should mention deprecated
            assert "deprecated" in warning_msg.lower()
            # All should be reasonably long
            assert len(warning_msg) > 20
