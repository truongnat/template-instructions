"""Unit tests for plugin registry."""

from typing import Any, Dict
from unittest.mock import MagicMock, patch

import pytest

from agentic_sdlc.core.exceptions import PluginError
from agentic_sdlc.plugins import Plugin, PluginRegistry, get_plugin_registry


class SimplePlugin(Plugin):
    """Simple plugin implementation for testing."""

    def __init__(self, name: str = "test-plugin", version: str = "1.0.0"):
        self._name = name
        self._version = version
        self.initialize_called = False
        self.shutdown_called = False
        self.init_config = None

    @property
    def name(self) -> str:
        return self._name

    @property
    def version(self) -> str:
        return self._version

    def initialize(self, config: Dict[str, Any]) -> None:
        self.initialize_called = True
        self.init_config = config

    def shutdown(self) -> None:
        self.shutdown_called = True


class FailingPlugin(Plugin):
    """Plugin that fails during initialization."""

    @property
    def name(self) -> str:
        return "failing-plugin"

    @property
    def version(self) -> str:
        return "1.0.0"

    def initialize(self, config: Dict[str, Any]) -> None:
        raise RuntimeError("Initialization failed")

    def shutdown(self) -> None:
        raise RuntimeError("Shutdown failed")


class TestPluginRegistry:
    """Tests for PluginRegistry class."""

    def test_registry_creation(self):
        """Test creating a new registry."""
        registry = PluginRegistry()
        assert registry is not None

    def test_register_plugin(self):
        """Test registering a plugin."""
        registry = PluginRegistry()
        plugin = SimplePlugin()

        registry.register(plugin)

        assert registry.get("test-plugin") is plugin

    def test_register_duplicate_plugin(self):
        """Test that registering duplicate plugin raises error."""
        registry = PluginRegistry()
        plugin1 = SimplePlugin(name="duplicate")
        plugin2 = SimplePlugin(name="duplicate")

        registry.register(plugin1)

        with pytest.raises(PluginError) as exc_info:
            registry.register(plugin2)

        assert "already registered" in str(exc_info.value)
        assert "duplicate" in str(exc_info.value)

    def test_get_plugin(self):
        """Test retrieving a registered plugin."""
        registry = PluginRegistry()
        plugin = SimplePlugin(name="my-plugin")

        registry.register(plugin)
        retrieved = registry.get("my-plugin")

        assert retrieved is plugin

    def test_get_nonexistent_plugin(self):
        """Test retrieving a plugin that doesn't exist."""
        registry = PluginRegistry()

        result = registry.get("nonexistent")

        assert result is None

    def test_unregister_plugin(self):
        """Test unregistering a plugin."""
        registry = PluginRegistry()
        plugin = SimplePlugin()

        registry.register(plugin)
        assert registry.get("test-plugin") is plugin

        registry.unregister("test-plugin")

        assert registry.get("test-plugin") is None
        assert plugin.shutdown_called

    def test_unregister_nonexistent_plugin(self):
        """Test unregistering a plugin that doesn't exist."""
        registry = PluginRegistry()

        with pytest.raises(PluginError) as exc_info:
            registry.unregister("nonexistent")

        assert "not registered" in str(exc_info.value)

    def test_unregister_calls_shutdown(self):
        """Test that unregister calls plugin shutdown."""
        registry = PluginRegistry()
        plugin = SimplePlugin()

        registry.register(plugin)
        assert not plugin.shutdown_called

        registry.unregister("test-plugin")

        assert plugin.shutdown_called

    def test_unregister_continues_on_shutdown_error(self):
        """Test that unregister continues even if shutdown fails."""
        registry = PluginRegistry()
        plugin = FailingPlugin()

        registry.register(plugin)

        # Should not raise even though shutdown fails
        registry.unregister("failing-plugin")

        # Plugin should be removed from registry
        assert registry.get("failing-plugin") is None

    def test_validate_plugin_interface_valid(self):
        """Test validating a valid plugin."""
        registry = PluginRegistry()
        plugin = SimplePlugin()

        # Should not raise
        registry._validate_plugin_interface(plugin)

    def test_validate_plugin_interface_missing_name(self):
        """Test validating plugin missing name property."""

        class BadPlugin:
            @property
            def version(self) -> str:
                return "1.0.0"

            def initialize(self, config: Dict[str, Any]) -> None:
                pass

            def shutdown(self) -> None:
                pass

        registry = PluginRegistry()

        with pytest.raises(PluginError) as exc_info:
            registry._validate_plugin_interface(BadPlugin())  # type: ignore

        assert "does not implement required interface" in str(exc_info.value)
        assert "name" in str(exc_info.value)

    def test_validate_plugin_interface_missing_version(self):
        """Test validating plugin missing version property."""

        class BadPlugin:
            @property
            def name(self) -> str:
                return "bad-plugin"

            def initialize(self, config: Dict[str, Any]) -> None:
                pass

            def shutdown(self) -> None:
                pass

        registry = PluginRegistry()

        with pytest.raises(PluginError) as exc_info:
            registry._validate_plugin_interface(BadPlugin())  # type: ignore

        assert "does not implement required interface" in str(exc_info.value)
        assert "version" in str(exc_info.value)

    def test_validate_plugin_interface_missing_initialize(self):
        """Test validating plugin missing initialize method."""

        class BadPlugin:
            @property
            def name(self) -> str:
                return "bad-plugin"

            @property
            def version(self) -> str:
                return "1.0.0"

            def shutdown(self) -> None:
                pass

        registry = PluginRegistry()

        with pytest.raises(PluginError) as exc_info:
            registry._validate_plugin_interface(BadPlugin())  # type: ignore

        assert "does not implement required interface" in str(exc_info.value)
        assert "initialize" in str(exc_info.value)

    def test_validate_plugin_interface_missing_shutdown(self):
        """Test validating plugin missing shutdown method."""

        class BadPlugin:
            @property
            def name(self) -> str:
                return "bad-plugin"

            @property
            def version(self) -> str:
                return "1.0.0"

            def initialize(self, config: Dict[str, Any]) -> None:
                pass

        registry = PluginRegistry()

        with pytest.raises(PluginError) as exc_info:
            registry._validate_plugin_interface(BadPlugin())  # type: ignore

        assert "does not implement required interface" in str(exc_info.value)
        assert "shutdown" in str(exc_info.value)

    def test_load_from_entry_points_no_plugins(self):
        """Test loading from entry points when none exist."""
        registry = PluginRegistry()

        # Mock entry_points to return empty
        with patch("importlib.metadata.entry_points") as mock_ep:
            mock_ep.return_value = {}
            registry.load_from_entry_points()

        # Should not raise and registry should be empty
        assert registry.get("any-plugin") is None

    def test_load_from_entry_points_with_plugin(self):
        """Test loading plugins from entry points."""
        registry = PluginRegistry()

        # Create a mock entry point
        mock_ep = MagicMock()
        mock_ep.name = "test-plugin"
        mock_ep.value = "tests.unit.plugins.test_plugin_registry:SimplePlugin"
        mock_ep.load.return_value = SimplePlugin

        # Mock entry_points to return our mock
        with patch("importlib.metadata.entry_points") as mock_eps:
            # Handle both Python 3.10+ and earlier versions
            mock_group = MagicMock()
            mock_group.__iter__ = MagicMock(return_value=iter([mock_ep]))
            mock_eps.return_value.select.return_value = [mock_ep]

            registry.load_from_entry_points()

        # Plugin should be registered
        assert registry.get("test-plugin") is not None

    def test_load_from_entry_points_handles_load_error(self):
        """Test that load_from_entry_points handles errors gracefully."""
        registry = PluginRegistry()

        # Create a mock entry point that fails to load
        mock_ep = MagicMock()
        mock_ep.name = "bad-plugin"
        mock_ep.load.side_effect = ImportError("Module not found")

        # Mock entry_points to return our mock
        with patch("importlib.metadata.entry_points") as mock_eps:
            mock_eps.return_value.select.return_value = [mock_ep]

            # Should not raise
            registry.load_from_entry_points()

        # Plugin should not be registered
        assert registry.get("bad-plugin") is None

    def test_load_from_entry_points_handles_instantiation_error(self):
        """Test that load_from_entry_points handles instantiation errors."""
        registry = PluginRegistry()

        # Create a mock entry point that fails to instantiate
        mock_ep = MagicMock()
        mock_ep.name = "bad-plugin"
        mock_plugin_class = MagicMock()
        mock_plugin_class.side_effect = RuntimeError("Instantiation failed")
        mock_ep.load.return_value = mock_plugin_class

        # Mock entry_points to return our mock
        with patch("importlib.metadata.entry_points") as mock_eps:
            mock_eps.return_value.select.return_value = [mock_ep]

            # Should not raise
            registry.load_from_entry_points()

        # Plugin should not be registered
        assert registry.get("bad-plugin") is None

    def test_multiple_plugins_registration(self):
        """Test registering multiple plugins."""
        registry = PluginRegistry()
        plugin1 = SimplePlugin(name="plugin-1")
        plugin2 = SimplePlugin(name="plugin-2")
        plugin3 = SimplePlugin(name="plugin-3")

        registry.register(plugin1)
        registry.register(plugin2)
        registry.register(plugin3)

        assert registry.get("plugin-1") is plugin1
        assert registry.get("plugin-2") is plugin2
        assert registry.get("plugin-3") is plugin3

    def test_plugin_registration_round_trip(self):
        """Test that registered plugin can be retrieved unchanged."""
        registry = PluginRegistry()
        plugin = SimplePlugin(name="roundtrip", version="2.5.0")

        registry.register(plugin)
        retrieved = registry.get("roundtrip")

        assert retrieved is plugin
        assert retrieved.name == "roundtrip"
        assert retrieved.version == "2.5.0"


class TestGetPluginRegistry:
    """Tests for get_plugin_registry singleton function."""

    def test_get_plugin_registry_returns_singleton(self):
        """Test that get_plugin_registry returns the same instance."""
        registry1 = get_plugin_registry()
        registry2 = get_plugin_registry()

        assert registry1 is registry2

    def test_get_plugin_registry_is_plugin_registry(self):
        """Test that get_plugin_registry returns a PluginRegistry."""
        registry = get_plugin_registry()

        assert isinstance(registry, PluginRegistry)
