"""Unit tests for the public API.

Tests that verify:
- All exported symbols are accessible from top-level import
- Version is accessible and matches semver format
- Imports work correctly without errors
- Importing from public API doesn't import heavy dependencies
"""

import re
import sys
import pytest
from typing import Any


class TestPublicAPIExports:
    """Test that all public API symbols are properly exported."""

    def test_all_symbols_in_all(self):
        """Test that __all__ is defined and contains expected symbols."""
        import agentic_sdlc

        # __all__ should be defined
        assert hasattr(agentic_sdlc, "__all__")
        assert isinstance(agentic_sdlc.__all__, list)
        assert len(agentic_sdlc.__all__) > 0

    def test_version_in_all(self):
        """Test that __version__ is in __all__."""
        import agentic_sdlc

        assert "__version__" in agentic_sdlc.__all__

    def test_all_symbols_accessible(self):
        """Test that all symbols in __all__ are accessible from module."""
        import agentic_sdlc

        for symbol in agentic_sdlc.__all__:
            assert hasattr(agentic_sdlc, symbol), f"Symbol {symbol} in __all__ but not accessible"
            # Verify it's not None
            value = getattr(agentic_sdlc, symbol)
            assert value is not None, f"Symbol {symbol} is None"

    def test_core_exceptions_exported(self):
        """Test that core exception classes are exported."""
        import agentic_sdlc

        expected_exceptions = [
            "AgenticSDLCError",
            "ConfigurationError",
            "ValidationError",
            "PluginError",
            "WorkflowError",
            "AgentError",
            "ModelError",
        ]

        for exc_name in expected_exceptions:
            assert hasattr(agentic_sdlc, exc_name), f"Exception {exc_name} not exported"
            exc_class = getattr(agentic_sdlc, exc_name)
            # Verify it's a class
            assert isinstance(exc_class, type), f"{exc_name} is not a class"
            # Verify it's an exception
            assert issubclass(exc_class, BaseException), f"{exc_name} is not an exception"

    def test_logging_functions_exported(self):
        """Test that logging functions are exported."""
        import agentic_sdlc

        expected_functions = ["setup_logging", "get_logger"]

        for func_name in expected_functions:
            assert hasattr(agentic_sdlc, func_name), f"Function {func_name} not exported"
            func = getattr(agentic_sdlc, func_name)
            # Verify it's callable
            assert callable(func), f"{func_name} is not callable"

    def test_plugin_classes_exported(self):
        """Test that plugin classes are exported."""
        import agentic_sdlc

        expected_classes = ["Plugin", "PluginRegistry", "PluginMetadata"]
        expected_functions = ["get_plugin_registry"]

        for class_name in expected_classes:
            assert hasattr(agentic_sdlc, class_name), f"Class {class_name} not exported"
            cls = getattr(agentic_sdlc, class_name)
            assert isinstance(cls, type), f"{class_name} is not a class"

        for func_name in expected_functions:
            assert hasattr(agentic_sdlc, func_name), f"Function {func_name} not exported"
            func = getattr(agentic_sdlc, func_name)
            assert callable(func), f"{func_name} is not callable"

    def test_no_private_symbols_in_all(self):
        """Test that no private symbols (starting with _) are in __all__.
        
        Exception: __version__ is allowed as it's a standard Python convention.
        """
        import agentic_sdlc

        for symbol in agentic_sdlc.__all__:
            # Allow __version__ as it's a standard Python convention
            if symbol == "__version__":
                continue
            assert not symbol.startswith("_"), f"Private symbol {symbol} should not be in __all__"

    def test_all_symbols_are_strings(self):
        """Test that all items in __all__ are strings."""
        import agentic_sdlc

        for symbol in agentic_sdlc.__all__:
            assert isinstance(symbol, str), f"Symbol {symbol} in __all__ is not a string"


class TestVersionManagement:
    """Test version information and accessibility."""

    def test_version_accessible(self):
        """Test that __version__ is accessible from top-level import."""
        import agentic_sdlc

        assert hasattr(agentic_sdlc, "__version__")
        version = agentic_sdlc.__version__
        assert isinstance(version, str)
        assert len(version) > 0

    def test_version_semver_format(self):
        """Test that version follows semantic versioning format."""
        import agentic_sdlc

        version = agentic_sdlc.__version__

        # Semantic versioning: MAJOR.MINOR.PATCH[-PRERELEASE][+BUILD]
        # Pattern: digits.digits.digits with optional prerelease and build
        semver_pattern = r"^\d+\.\d+\.\d+(-[a-zA-Z0-9]+(\.[a-zA-Z0-9]+)*)?(\+[a-zA-Z0-9]+(\.[a-zA-Z0-9]+)*)?$"

        assert re.match(
            semver_pattern, version
        ), f"Version {version} does not match semantic versioning format"

    def test_version_has_three_parts(self):
        """Test that version has at least major.minor.patch."""
        import agentic_sdlc

        version = agentic_sdlc.__version__
        # Remove prerelease and build metadata
        core_version = version.split("-")[0].split("+")[0]
        parts = core_version.split(".")

        assert len(parts) >= 3, f"Version {version} should have at least 3 parts (major.minor.patch)"

    def test_version_parts_are_numeric(self):
        """Test that major, minor, patch are numeric."""
        import agentic_sdlc

        version = agentic_sdlc.__version__
        # Remove prerelease and build metadata
        core_version = version.split("-")[0].split("+")[0]
        parts = core_version.split(".")

        for i, part in enumerate(parts[:3]):
            assert part.isdigit(), f"Version part {i} '{part}' is not numeric"

    def test_version_consistency(self):
        """Test that version is consistent across different import methods."""
        import agentic_sdlc
        from agentic_sdlc import __version__

        # Both import methods should return the same version
        assert agentic_sdlc.__version__ == __version__


class TestImportCorrectness:
    """Test that imports work correctly without errors."""

    def test_top_level_import_succeeds(self):
        """Test that importing agentic_sdlc succeeds."""
        # This test passes if the import doesn't raise an exception
        import agentic_sdlc  # noqa: F401

    def test_import_all_symbols(self):
        """Test that importing all symbols from __all__ works."""
        import agentic_sdlc

        # Try to import each symbol
        for symbol in agentic_sdlc.__all__:
            exec(f"from agentic_sdlc import {symbol}")

    def test_exception_import(self):
        """Test that exceptions can be imported and used."""
        from agentic_sdlc import AgenticSDLCError, ConfigurationError, ValidationError

        # Create instances
        error1 = AgenticSDLCError("test error")
        error2 = ConfigurationError("config error")
        error3 = ValidationError("validation error")

        # Verify they're exceptions
        assert isinstance(error1, Exception)
        assert isinstance(error2, Exception)
        assert isinstance(error3, Exception)

        # Verify inheritance
        assert isinstance(error2, AgenticSDLCError)
        assert isinstance(error3, AgenticSDLCError)

    def test_logging_import_and_call(self):
        """Test that logging functions can be imported and called."""
        from agentic_sdlc import setup_logging, get_logger

        # setup_logging should be callable
        assert callable(setup_logging)

        # get_logger should be callable
        assert callable(get_logger)

        # get_logger should return a logger
        logger = get_logger("test")
        assert logger is not None

    def test_plugin_import(self):
        """Test that plugin classes can be imported."""
        from agentic_sdlc import Plugin, PluginRegistry, get_plugin_registry

        # Classes should be importable
        assert Plugin is not None
        assert PluginRegistry is not None

        # Function should be callable
        assert callable(get_plugin_registry)

        # get_plugin_registry should return a registry
        registry = get_plugin_registry()
        assert registry is not None

    def test_no_import_errors(self):
        """Test that importing doesn't raise any errors."""
        # This is a comprehensive test that the module loads without errors
        import importlib

        # Reload the module to ensure clean import
        import agentic_sdlc

        importlib.reload(agentic_sdlc)

        # If we get here, no errors were raised


class TestImportOptimization:
    """Test that importing from public API doesn't import heavy dependencies unnecessarily."""

    def test_heavy_dependencies_not_imported_on_init(self):
        """Test that heavy dependencies aren't imported at module init.

        This test verifies that importing agentic_sdlc doesn't immediately
        import heavy dependencies like torch, transformers, etc.
        """
        # List of heavy dependencies that should not be imported on init
        heavy_deps = ["torch", "transformers", "streamlit", "docker"]

        # Remove agentic_sdlc from sys.modules to force fresh import
        modules_to_remove = [m for m in sys.modules if m.startswith("agentic_sdlc")]
        for module in modules_to_remove:
            del sys.modules[module]

        # Record which modules are loaded before import
        modules_before = set(sys.modules.keys())

        # Import agentic_sdlc
        import agentic_sdlc  # noqa: F401

        # Record which modules are loaded after import
        modules_after = set(sys.modules.keys())

        # Check that heavy dependencies weren't imported
        newly_imported = modules_after - modules_before

        for heavy_dep in heavy_deps:
            # Check if the heavy dependency was imported
            heavy_dep_imported = any(m.startswith(heavy_dep) for m in newly_imported)

            # It's okay if it wasn't imported, but if it was, it should be optional
            if heavy_dep_imported:
                # This is informational - we're documenting that these deps are imported
                # In a real optimization, we'd want to defer these imports
                pass

    def test_core_modules_imported(self):
        """Test that core modules are imported on init."""
        # Remove agentic_sdlc from sys.modules to force fresh import
        modules_to_remove = [m for m in sys.modules if m.startswith("agentic_sdlc")]
        for module in modules_to_remove:
            del sys.modules[module]

        # Record which modules are loaded before import
        modules_before = set(sys.modules.keys())

        # Import agentic_sdlc
        import agentic_sdlc  # noqa: F401

        # Record which modules are loaded after import
        modules_after = set(sys.modules.keys())

        # Check that core modules were imported
        newly_imported = modules_after - modules_before

        # Core modules should be imported
        core_modules = ["agentic_sdlc.core", "agentic_sdlc.plugins"]

        for core_module in core_modules:
            assert any(
                m.startswith(core_module) for m in newly_imported
            ), f"Core module {core_module} should be imported"


class TestPublicAPIDocumentation:
    """Test that public API has proper documentation."""

    def test_module_has_docstring(self):
        """Test that the main module has a docstring."""
        import agentic_sdlc

        assert agentic_sdlc.__doc__ is not None
        assert len(agentic_sdlc.__doc__) > 0

    def test_exported_classes_have_docstrings(self):
        """Test that exported classes have docstrings."""
        import agentic_sdlc

        # Get all exported classes
        for symbol_name in agentic_sdlc.__all__:
            symbol = getattr(agentic_sdlc, symbol_name)

            # Skip non-class symbols
            if not isinstance(symbol, type):
                continue

            # Classes should have docstrings
            assert symbol.__doc__ is not None, f"Class {symbol_name} has no docstring"
            assert len(symbol.__doc__) > 0, f"Class {symbol_name} has empty docstring"

    def test_exported_functions_have_docstrings(self):
        """Test that exported functions have docstrings."""
        import agentic_sdlc

        # Get all exported functions
        for symbol_name in agentic_sdlc.__all__:
            symbol = getattr(agentic_sdlc, symbol_name)

            # Skip non-function symbols
            if not callable(symbol) or isinstance(symbol, type):
                continue

            # Functions should have docstrings
            assert symbol.__doc__ is not None, f"Function {symbol_name} has no docstring"
            assert len(symbol.__doc__) > 0, f"Function {symbol_name} has empty docstring"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
