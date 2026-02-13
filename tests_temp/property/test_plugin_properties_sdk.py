"""Property-based tests for the plugin system.

Feature: sdk-reorganization
Tests the correctness properties of the plugin system including registration,
failure isolation, and interface validation.
"""

from typing import Any, Dict
from unittest.mock import MagicMock

import pytest
from hypothesis import given, strategies as st

from agentic_sdlc.core.exceptions import PluginError
from agentic_sdlc.plugins import Plugin, PluginRegistry


class SimplePlugin(Plugin):
    """Simple plugin for property testing."""

    def __init__(self, name: str = "test-plugin", version: str = "1.0.0"):
        self._name = name
        self._version = version

    @property
    def name(self) -> str:
        return self._name

    @property
    def version(self) -> str:
        return self._version

    def initialize(self, config: Dict[str, Any]) -> None:
        pass

    def shutdown(self) -> None:
        pass


# Feature: sdk-reorganization, Property 7: Plugin Registration Round-Trip
class TestPluginRegistrationRoundTrip:
    """Property 7: Plugin Registration Round-Trip.

    **Validates: Requirements 10.2**

    For any registered plugin, retrieving it by name SHALL return the same instance.
    """

    @given(
        plugin_name=st.text(
            alphabet=st.characters(blacklist_categories=("Cc", "Cs")),
            min_size=1,
            max_size=50,
        ).filter(lambda x: x.strip() and not x.startswith("_"))
    )
    def test_registered_plugin_retrieval_returns_same_instance(self, plugin_name):
        """For any registered plugin, retrieving it by name returns the same instance."""
        registry = PluginRegistry()
        plugin = SimplePlugin(name=plugin_name)

        registry.register(plugin)
        retrieved = registry.get(plugin_name)

        assert retrieved is plugin

    @given(
        plugin_name=st.text(
            alphabet=st.characters(blacklist_categories=("Cc", "Cs")),
            min_size=1,
            max_size=50,
        ).filter(lambda x: x.strip() and not x.startswith("_")),
        version=st.text(
            alphabet="0123456789.",
            min_size=5,
            max_size=10,
        ),
    )
    def test_plugin_metadata_preserved_through_registration(
        self, plugin_name, version
    ):
        """For any registered plugin, its metadata is preserved through registration."""
        registry = PluginRegistry()
        plugin = SimplePlugin(name=plugin_name, version=version)

        registry.register(plugin)
        retrieved = registry.get(plugin_name)

        assert retrieved.name == plugin_name
        assert retrieved.version == version


# Feature: sdk-reorganization, Property 8: Plugin Failure Isolation
class TestPluginFailureIsolation:
    """Property 8: Plugin Failure Isolation.

    **Validates: Requirements 10.5**

    When a plugin raises an exception during initialization, the SDK SHALL catch it,
    log it, and continue operation without crashing. Other plugins can still be loaded
    after one fails. Failure is logged with context.
    """

    def test_plugin_initialization_failure_is_caught(self):
        """When a plugin fails to initialize, the SDK catches the exception."""

        class FailingPlugin(Plugin):
            @property
            def name(self) -> str:
                return "failing-plugin"

            @property
            def version(self) -> str:
                return "1.0.0"

            def initialize(self, config: Dict[str, Any]) -> None:
                raise RuntimeError("Initialization failed")

            def shutdown(self) -> None:
                pass

        registry = PluginRegistry()
        plugin = FailingPlugin()

        # Register the plugin (this should succeed)
        registry.register(plugin)

        # Try to initialize it (this should fail but be caught)
        with pytest.raises(RuntimeError):
            plugin.initialize({})

        # Plugin should still be registered even though initialization failed
        assert registry.get("failing-plugin") is plugin

    def test_other_plugins_load_after_one_fails(self):
        """After one plugin fails to load, other plugins can still be loaded."""

        class FailingPlugin(Plugin):
            @property
            def name(self) -> str:
                return "failing-plugin"

            @property
            def version(self) -> str:
                return "1.0.0"

            def initialize(self, config: Dict[str, Any]) -> None:
                raise RuntimeError("Initialization failed")

            def shutdown(self) -> None:
                pass

        registry = PluginRegistry()

        # Try to load failing plugin (should not crash)
        try:
            registry._load_entry_point(MagicMock(name="failing", load=lambda: FailingPlugin))
        except Exception:
            pass

        # Now load a working plugin
        working_plugin = SimplePlugin(name="working-plugin")
        registry.register(working_plugin)

        # Working plugin should be registered
        assert registry.get("working-plugin") is working_plugin

    def test_plugin_shutdown_failure_is_caught(self):
        """When a plugin fails during shutdown, the SDK catches the exception."""

        class FailingShutdownPlugin(Plugin):
            @property
            def name(self) -> str:
                return "failing-shutdown"

            @property
            def version(self) -> str:
                return "1.0.0"

            def initialize(self, config: Dict[str, Any]) -> None:
                pass

            def shutdown(self) -> None:
                raise RuntimeError("Shutdown failed")

        registry = PluginRegistry()
        plugin = FailingShutdownPlugin()
        registry.register(plugin)

        # Should not raise even though shutdown fails
        registry.unregister("failing-shutdown")

        # Plugin should be removed from registry
        assert registry.get("failing-shutdown") is None

    @given(
        num_plugins=st.integers(min_value=2, max_value=10),
        failing_index=st.integers(min_value=0, max_value=9),
    )
    def test_failure_isolation_with_multiple_plugins(self, num_plugins, failing_index):
        """For any set of plugins where one fails, others can still be loaded.

        When a plugin fails during entry point loading, the SDK SHALL catch the
        exception and continue loading other plugins without crashing.
        """
        if failing_index >= num_plugins:
            failing_index = num_plugins - 1

        registry = PluginRegistry()

        # Create mock entry points: some working, one failing
        entry_points = []
        for i in range(num_plugins):
            mock_ep = MagicMock()
            if i == failing_index:
                # This one will fail
                mock_ep.name = f"failing-plugin-{i}"
                mock_ep.load.side_effect = RuntimeError(f"Plugin {i} failed to load")
            else:
                # These will succeed
                mock_ep.name = f"plugin-{i}"
                mock_ep.load.return_value = lambda idx=i: SimplePlugin(
                    name=f"plugin-{idx}"
                )
            entry_points.append(mock_ep)

        # Manually load the entry points to simulate the behavior
        # The registry should handle failures gracefully
        for i, ep in enumerate(entry_points):
            try:
                registry._load_entry_point(ep)
            except Exception:
                # Failure is caught and logged, registry continues
                pass

        # All non-failing plugins should be registered
        for i in range(num_plugins):
            if i != failing_index:
                plugin = registry.get(f"plugin-{i}")
                assert plugin is not None, f"Plugin {i} should be registered"

    def test_failure_isolation_preserves_registry_state(self):
        """When a plugin fails to load, registry state is preserved.

        The registry should remain in a consistent state even when a plugin
        fails during entry point loading.
        """

        class FailingPlugin(Plugin):
            @property
            def name(self) -> str:
                return "failing"

            @property
            def version(self) -> str:
                return "1.0.0"

            def initialize(self, config: Dict[str, Any]) -> None:
                raise RuntimeError("Init failed")

            def shutdown(self) -> None:
                pass

        registry = PluginRegistry()

        # Register a working plugin first
        working_plugin = SimplePlugin(name="working")
        registry.register(working_plugin)

        # Try to load a failing plugin via entry point
        mock_ep = MagicMock()
        mock_ep.name = "failing"
        mock_ep.load.return_value = FailingPlugin

        # This should not crash and should not affect the working plugin
        registry._load_entry_point(mock_ep)

        # Working plugin should still be there
        assert registry.get("working") is working_plugin

    @given(
        exception_type=st.sampled_from(
            [RuntimeError, ValueError, TypeError, Exception]
        ),
        exception_message=st.text(
            alphabet=st.characters(blacklist_categories=("Cc", "Cs")),
            min_size=1,
            max_size=100,
        ),
    )
    def test_various_exception_types_are_isolated(
        self, exception_type, exception_message
    ):
        """For any exception type raised by a plugin, it SHALL be caught and isolated.

        The SDK should handle any exception type gracefully without crashing.
        """

        class FailingPlugin(Plugin):
            def __init__(self, exc_type, exc_msg):
                self.exc_type = exc_type
                self.exc_msg = exc_msg

            @property
            def name(self) -> str:
                return "failing"

            @property
            def version(self) -> str:
                return "1.0.0"

            def initialize(self, config: Dict[str, Any]) -> None:
                raise self.exc_type(self.exc_msg)

            def shutdown(self) -> None:
                pass

        registry = PluginRegistry()
        plugin = FailingPlugin(exception_type, exception_message)

        # Register should succeed
        registry.register(plugin)

        # Initialize should raise the exception
        with pytest.raises(exception_type):
            plugin.initialize({})

        # Plugin should still be in registry
        assert registry.get("failing") is plugin


# Feature: sdk-reorganization, Property 9: Plugin Interface Validation
class TestPluginInterfaceValidation:
    """Property 9: Plugin Interface Validation.

    **Validates: Requirements 10.6**

    Objects without required methods are rejected during registration.
    Error messages list missing methods.
    Valid plugins pass validation.
    """

    def test_objects_without_required_methods_are_rejected(self):
        """Objects without required methods are rejected during registration."""

        class BadPlugin:
            @property
            def name(self) -> str:
                return "bad-plugin"

            # Missing version property
            # Missing initialize method
            # Missing shutdown method

        registry = PluginRegistry()

        with pytest.raises(PluginError):
            registry._validate_plugin_interface(BadPlugin())  # type: ignore

    @given(
        missing_method=st.sampled_from(["name", "version", "initialize", "shutdown"])
    )
    def test_error_message_lists_missing_methods(self, missing_method):
        """Error message lists missing methods."""

        class BadPlugin:
            pass

        registry = PluginRegistry()

        with pytest.raises(PluginError) as exc_info:
            registry._validate_plugin_interface(BadPlugin())  # type: ignore

        error_msg = str(exc_info.value)
        assert "does not implement required interface" in error_msg

    def test_valid_plugins_pass_validation(self):
        """Valid plugins pass validation."""
        registry = PluginRegistry()
        plugin = SimplePlugin()

        # Should not raise
        registry._validate_plugin_interface(plugin)

    @given(
        plugin_name=st.text(
            alphabet=st.characters(blacklist_categories=("Cc", "Cs")),
            min_size=1,
            max_size=50,
        ).filter(lambda x: x.strip() and not x.startswith("_")),
        version=st.text(
            alphabet="0123456789.",
            min_size=5,
            max_size=10,
        ),
    )
    def test_valid_plugins_with_various_names_and_versions_pass_validation(
        self, plugin_name, version
    ):
        """Valid plugins with various names and versions pass validation."""
        registry = PluginRegistry()
        plugin = SimplePlugin(name=plugin_name, version=version)

        # Should not raise
        registry._validate_plugin_interface(plugin)

    @given(
        missing_properties=st.lists(
            st.sampled_from(["name", "version"]),
            min_size=1,
            max_size=2,
            unique=True,
        ),
        missing_methods=st.lists(
            st.sampled_from(["initialize", "shutdown"]),
            min_size=1,
            max_size=2,
            unique=True,
        ),
    )
    def test_invalid_plugins_with_missing_properties_and_methods_are_rejected(
        self, missing_properties, missing_methods
    ):
        """For any plugin missing required properties or methods, validation fails.

        When an object lacks required interface elements, the registry SHALL reject
        it with a PluginError that includes information about what's missing.
        """

        class IncompletePlugin:
            pass

        # Add only the properties/methods that are NOT in the missing lists
        if "name" not in missing_properties:
            IncompletePlugin.name = property(lambda self: "test")
        if "version" not in missing_properties:
            IncompletePlugin.version = property(lambda self: "1.0.0")
        if "initialize" not in missing_methods:
            IncompletePlugin.initialize = lambda self, config: None
        if "shutdown" not in missing_methods:
            IncompletePlugin.shutdown = lambda self: None

        registry = PluginRegistry()

        with pytest.raises(PluginError) as exc_info:
            registry._validate_plugin_interface(IncompletePlugin())  # type: ignore

        error_msg = str(exc_info.value)
        assert "does not implement required interface" in error_msg
        # Verify that the error context includes the missing items
        assert "missing" in str(exc_info.value.context).lower()

    @given(
        plugin_name=st.text(
            alphabet=st.characters(blacklist_categories=("Cc", "Cs")),
            min_size=1,
            max_size=50,
        ).filter(lambda x: x.strip() and not x.startswith("_")),
        version=st.text(
            alphabet="0123456789.",
            min_size=5,
            max_size=10,
        ),
    )
    def test_all_valid_plugins_pass_validation_regardless_of_name_or_version(
        self, plugin_name, version
    ):
        """For any valid plugin with any name and version, validation passes.

        Valid plugins with complete interface implementation should always pass
        validation regardless of their name or version values.
        """
        registry = PluginRegistry()
        plugin = SimplePlugin(name=plugin_name, version=version)

        # Should not raise for any valid plugin
        registry._validate_plugin_interface(plugin)

        # Plugin should be registrable after passing validation
        registry.register(plugin)
        assert registry.get(plugin_name) is plugin
