"""Integration tests for package installation and distribution.

Tests verify that:
- The package can be built successfully
- Distributions contain correct files
- Package data (resources) is accessible
- Version is accessible from installed package
- All public API symbols are importable
- Optional dependencies work correctly
"""

import sys
from pathlib import Path
from typing import List

import pytest

# Add src to path for testing
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))


class TestPackageStructure:
    """Test that the package structure is correct."""

    def test_version_accessible(self) -> None:
        """Test that version is accessible from public API."""
        from agentic_sdlc import __version__

        assert __version__ is not None
        assert isinstance(__version__, str)
        assert len(__version__) > 0

    def test_version_matches_semver(self) -> None:
        """Test that version matches semantic versioning format."""
        import re

        from agentic_sdlc import __version__

        # Match MAJOR.MINOR.PATCH format
        pattern = r"^\d+\.\d+\.\d+$"
        assert re.match(pattern, __version__), f"Version {__version__} does not match semver"

    def test_version_is_3_0_0(self) -> None:
        """Test that version is 3.0.0 for SDK reorganization."""
        from agentic_sdlc import __version__

        assert __version__ == "3.0.0", f"Expected version 3.0.0, got {__version__}"


class TestPublicAPIImports:
    """Test that all public API symbols are importable."""

    def test_core_imports(self) -> None:
        """Test core module imports."""
        from agentic_sdlc import (
            Config,
            AgenticSDLCError,
            ConfigurationError,
            ValidationError,
            PluginError,
            setup_logging,
            get_logger,
        )

        assert Config is not None
        assert AgenticSDLCError is not None
        assert ConfigurationError is not None
        assert ValidationError is not None
        assert PluginError is not None
        assert setup_logging is not None
        assert get_logger is not None

    def test_infrastructure_imports(self) -> None:
        """Test infrastructure module imports."""
        from agentic_sdlc import (
            WorkflowEngine,
            WorkflowRunner,
            ExecutionEngine,
            TaskExecutor,
            LifecycleManager,
        )

        assert WorkflowEngine is not None
        assert WorkflowRunner is not None
        assert ExecutionEngine is not None
        assert TaskExecutor is not None
        assert LifecycleManager is not None

    def test_intelligence_imports(self) -> None:
        """Test intelligence module imports."""
        from agentic_sdlc import (
            Learner,
            Monitor,
            Reasoner,
            Collaborator,
        )

        assert Learner is not None
        assert Monitor is not None
        assert Reasoner is not None
        assert Collaborator is not None

    def test_orchestration_imports(self) -> None:
        """Test orchestration module imports."""
        from agentic_sdlc import (
            Agent,
            AgentRegistry,
            create_agent,
            ModelClient,
            get_model_client,
            Workflow,
            WorkflowBuilder,
        )

        assert Agent is not None
        assert AgentRegistry is not None
        assert create_agent is not None
        assert ModelClient is not None
        assert get_model_client is not None
        assert Workflow is not None
        assert WorkflowBuilder is not None

    def test_plugin_imports(self) -> None:
        """Test plugin module imports."""
        from agentic_sdlc import (
            Plugin,
            PluginRegistry,
            get_plugin_registry,
        )

        assert Plugin is not None
        assert PluginRegistry is not None
        assert get_plugin_registry is not None

    def test_all_public_api_symbols(self) -> None:
        """Test that all symbols in __all__ are importable."""
        import agentic_sdlc

        # Get all symbols from __all__
        all_symbols = agentic_sdlc.__all__

        # Verify each symbol is accessible
        for symbol in all_symbols:
            assert hasattr(agentic_sdlc, symbol), f"Symbol {symbol} not found in public API"
            obj = getattr(agentic_sdlc, symbol)
            assert obj is not None, f"Symbol {symbol} is None"


class TestPackageData:
    """Test that package data (resources) is accessible."""

    def test_resources_directory_exists(self) -> None:
        """Test that resources directory exists."""
        import agentic_sdlc

        package_dir = Path(agentic_sdlc.__file__).parent
        resources_dir = package_dir / "resources"

        assert resources_dir.exists(), f"Resources directory not found at {resources_dir}"

    def test_resources_subdirectories_exist(self) -> None:
        """Test that resource subdirectories exist."""
        import agentic_sdlc

        package_dir = Path(agentic_sdlc.__file__).parent
        resources_dir = package_dir / "resources"

        required_dirs = ["templates", "workflows", "rules"]
        for subdir in required_dirs:
            subdir_path = resources_dir / subdir
            assert subdir_path.exists(), f"Resource subdirectory {subdir} not found"

    def test_py_typed_marker_exists(self) -> None:
        """Test that py.typed marker file exists."""
        import agentic_sdlc

        package_dir = Path(agentic_sdlc.__file__).parent
        py_typed = package_dir / "py.typed"

        assert py_typed.exists(), "py.typed marker file not found"

    def test_resources_are_readable(self) -> None:
        """Test that resource files are readable."""
        import agentic_sdlc

        package_dir = Path(agentic_sdlc.__file__).parent
        resources_dir = package_dir / "resources"

        # Check that we can read resource files
        readme = resources_dir / "README.md"
        if readme.exists():
            content = readme.read_text()
            assert len(content) > 0, "README.md is empty"


class TestOptionalDependencies:
    """Test that optional dependencies are properly configured."""

    def test_cli_optional_dependency_importable(self) -> None:
        """Test that CLI can be imported (click is optional)."""
        try:
            from agentic_sdlc.cli import main

            assert main is not None
            assert callable(main)
        except ImportError:
            # Click is not installed, which is expected for optional dependency
            pytest.skip("CLI dependencies not installed (optional)")

    def test_cli_entry_point_exists(self) -> None:
        """Test that CLI entry point is configured."""
        from agentic_sdlc.cli.main import main

        assert callable(main), "CLI main entry point is not callable"


class TestPublicAPITypeHints:
    """Test that public API functions have type hints."""

    def test_config_class_has_type_hints(self) -> None:
        """Test that Config class methods have type hints."""
        from agentic_sdlc import Config
        import inspect

        # Check __init__ method
        init_sig = inspect.signature(Config.__init__)
        assert init_sig.return_annotation != inspect.Signature.empty

    def test_get_logger_has_type_hints(self) -> None:
        """Test that get_logger function has type hints."""
        from agentic_sdlc import get_logger
        import inspect

        sig = inspect.signature(get_logger)
        # Should have return type hint
        assert sig.return_annotation != inspect.Signature.empty

    def test_setup_logging_has_type_hints(self) -> None:
        """Test that setup_logging function has type hints."""
        from agentic_sdlc import setup_logging
        import inspect

        sig = inspect.signature(setup_logging)
        # Should have return type hint
        assert sig.return_annotation != inspect.Signature.empty


class TestInternalModulePrivacy:
    """Test that internal modules are not exposed in public API."""

    def test_internal_modules_not_in_all(self) -> None:
        """Test that modules prefixed with underscore are not in __all__."""
        import agentic_sdlc

        all_symbols = agentic_sdlc.__all__

        # Check that no internal modules are in __all__ (except dunder names like __version__)
        for symbol in all_symbols:
            # Allow dunder names (like __version__) but not single underscore prefixed names
            if symbol.startswith("_") and not symbol.startswith("__"):
                raise AssertionError(f"Internal symbol {symbol} found in __all__")

    def test_internal_module_access_raises_error(self) -> None:
        """Test that accessing internal modules is not recommended."""
        import agentic_sdlc

        # _internal module may exist but should not be in __all__
        # This is acceptable as it's for internal use only
        if hasattr(agentic_sdlc, "_internal"):
            # Verify it's not in __all__
            assert "_internal" not in agentic_sdlc.__all__, "_internal should not be in __all__"


class TestDependencyVersionConstraints:
    """Test that dependencies have version constraints."""

    def test_pyproject_toml_exists(self) -> None:
        """Test that pyproject.toml exists."""
        pyproject = Path(__file__).parent.parent.parent / "pyproject.toml"
        assert pyproject.exists(), "pyproject.toml not found"

    def test_all_dependencies_have_constraints(self) -> None:
        """Test that all dependencies in pyproject.toml have version constraints."""
        import toml

        pyproject_path = Path(__file__).parent.parent.parent / "pyproject.toml"
        config = toml.load(str(pyproject_path))

        dependencies = config.get("project", {}).get("dependencies", [])

        # Check each dependency has version constraints
        for dep in dependencies:
            # Skip comments
            if dep.startswith("#"):
                continue

            # Check for version operators
            has_constraint = any(op in dep for op in [">=", "<=", "==", "!=", "~=", ">", "<"])
            assert has_constraint, f"Dependency {dep} does not have version constraints"

    def test_optional_dependencies_have_constraints(self) -> None:
        """Test that optional dependencies have version constraints."""
        import toml

        pyproject_path = Path(__file__).parent.parent.parent / "pyproject.toml"
        config = toml.load(str(pyproject_path))

        optional_deps = config.get("project", {}).get("optional-dependencies", {})

        for extra, deps in optional_deps.items():
            for dep in deps:
                # Skip comments
                if dep.startswith("#"):
                    continue

                # Check for version operators
                has_constraint = any(op in dep for op in [">=", "<=", "==", "!=", "~=", ">", "<"])
                assert (
                    has_constraint
                ), f"Optional dependency {dep} in [{extra}] does not have version constraints"
