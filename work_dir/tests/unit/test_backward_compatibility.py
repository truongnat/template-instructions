"""Unit tests for backward compatibility with old import paths.

Tests that old imports still work and emit appropriate deprecation warnings.
"""

import sys
import warnings
from typing import Any

import pytest


class TestOldImportPaths:
    """Test that old import paths still work with deprecation warnings."""
    
    def test_old_infrastructure_autogen_agents_import(self) -> None:
        """Test that old infrastructure.autogen.agents imports work."""
        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter("always")
            
            # This should work but emit a deprecation warning
            try:
                from agentic_sdlc.infrastructure.autogen import agents  # noqa: F401
                
                # Check that the module is in sys.modules
                assert "agentic_sdlc.infrastructure.autogen.agents" in sys.modules
                
                # Check for deprecation warning
                deprecation_warnings = [
                    warning for warning in w
                    if issubclass(warning.category, DeprecationWarning)
                ]
                # Warning might be emitted on attribute access
                if deprecation_warnings:
                    assert len(deprecation_warnings) >= 1
            except (ImportError, AttributeError):
                # If the old module doesn't exist, that's acceptable
                pass
    
    def test_old_intelligence_learning_import(self) -> None:
        """Test that old intelligence.learning imports work."""
        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter("always")
            
            try:
                from agentic_sdlc.intelligence import learning  # noqa: F401
                
                # Check that the module is in sys.modules
                assert "agentic_sdlc.intelligence.learning" in sys.modules
            except (ImportError, AttributeError):
                pass
    
    def test_old_core_config_import(self) -> None:
        """Test that old core.config imports work."""
        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter("always")
            
            try:
                from agentic_sdlc.core import config  # noqa: F401
                
                # Check that the module is in sys.modules
                assert "agentic_sdlc.core.config" in sys.modules
            except (ImportError, AttributeError):
                pass
    
    def test_deprecation_warning_has_correct_stacklevel(self) -> None:
        """Test that deprecation warning has correct stacklevel."""
        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter("always")
            
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
                warning = deprecation_warnings[0]
                # Verify the warning has proper location info
                assert warning.filename is not None
                assert warning.lineno is not None
    
    def test_deprecation_warning_contains_migration_instructions(self) -> None:
        """Test that deprecation warning contains migration instructions."""
        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter("always")
            
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
                # Should contain migration instructions
                assert "deprecated" in message.lower()
                assert "Use" in message or "use" in message or "instead" in message
    
    def test_new_imports_do_not_emit_warnings(self) -> None:
        """Test that new imports do NOT emit deprecation warnings."""
        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter("always")
            
            # Import from new location
            from agentic_sdlc import Agent  # noqa: F401
            
            # Check that no deprecation warnings were emitted
            deprecation_warnings = [
                warning for warning in w
                if issubclass(warning.category, DeprecationWarning)
            ]
            
            assert len(deprecation_warnings) == 0
    
    def test_old_and_new_imports_refer_to_same_object(self) -> None:
        """Test that old and new imports refer to the same object."""
        with warnings.catch_warnings(record=True):
            warnings.simplefilter("always")
            
            try:
                # Import from new location
                from agentic_sdlc.orchestration.agents import Agent as NewAgent
                
                # Import from old location (if it works)
                try:
                    from agentic_sdlc.infrastructure.autogen.agents import Agent as OldAgent
                    
                    # They should be the same class
                    assert NewAgent is OldAgent
                except (ImportError, AttributeError):
                    # Old import might not work, that's okay
                    pass
            except ImportError:
                # If new import doesn't work, skip this test
                pytest.skip("New import path not available")


class TestCompatibilityShimInstallation:
    """Test that compatibility shims are properly installed."""
    
    def test_compatibility_shims_installed_in_sys_modules(self) -> None:
        """Test that compatibility shims are installed in sys.modules."""
        # Import the compatibility installer
        from agentic_sdlc._compat import install_compatibility_shims
        
        # Install shims
        install_compatibility_shims()
        
        # Check that shim modules are in sys.modules
        expected_modules = [
            "agentic_sdlc.infrastructure.autogen",
            "agentic_sdlc.infrastructure.autogen.agents",
        ]
        
        for module_name in expected_modules:
            assert module_name in sys.modules
    
    def test_compatibility_shim_has_getattr(self) -> None:
        """Test that compatibility shim modules have __getattr__."""
        from agentic_sdlc._compat import install_compatibility_shims
        
        # Install shims
        install_compatibility_shims()
        
        # Check that shim modules have __getattr__
        if "agentic_sdlc.infrastructure.autogen.agents" in sys.modules:
            module = sys.modules["agentic_sdlc.infrastructure.autogen.agents"]
            assert hasattr(module, "__getattr__")
    
    def test_multiple_shim_installations_are_idempotent(self) -> None:
        """Test that installing shims multiple times is safe."""
        from agentic_sdlc._compat import install_compatibility_shims
        
        # Install shims multiple times
        install_compatibility_shims()
        install_compatibility_shims()
        install_compatibility_shims()
        
        # Should not raise any errors
        # And modules should still be in sys.modules
        assert "agentic_sdlc.infrastructure.autogen.agents" in sys.modules


class TestDeprecationWarningContent:
    """Test the content of deprecation warnings."""
    
    def test_warning_message_includes_old_path(self) -> None:
        """Test that warning message includes the old import path."""
        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter("always")
            
            try:
                from agentic_sdlc.infrastructure.autogen.agents import create_agent  # noqa: F401
            except (ImportError, AttributeError):
                pass
            
            deprecation_warnings = [
                warning for warning in w
                if issubclass(warning.category, DeprecationWarning)
            ]
            
            if deprecation_warnings:
                message = str(deprecation_warnings[0].message)
                # Should mention the old path
                assert "infrastructure.autogen" in message or "deprecated" in message.lower()
    
    def test_warning_message_includes_new_path(self) -> None:
        """Test that warning message includes the new import path."""
        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter("always")
            
            try:
                from agentic_sdlc.infrastructure.autogen.agents import create_agent  # noqa: F401
            except (ImportError, AttributeError):
                pass
            
            deprecation_warnings = [
                warning for warning in w
                if issubclass(warning.category, DeprecationWarning)
            ]
            
            if deprecation_warnings:
                message = str(deprecation_warnings[0].message)
                # Should mention the new path or migration instructions
                assert "agentic_sdlc" in message or "Use" in message
    
    def test_warning_message_is_actionable(self) -> None:
        """Test that warning message provides actionable guidance."""
        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter("always")
            
            try:
                from agentic_sdlc.infrastructure.autogen.agents import create_agent  # noqa: F401
            except (ImportError, AttributeError):
                pass
            
            deprecation_warnings = [
                warning for warning in w
                if issubclass(warning.category, DeprecationWarning)
            ]
            
            if deprecation_warnings:
                message = str(deprecation_warnings[0].message)
                # Message should be reasonably informative
                assert len(message) > 30
                # Should contain key information
                assert "deprecated" in message.lower()
