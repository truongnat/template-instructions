"""Unit tests for plugin base class and metadata."""

from typing import Any, Dict

import pytest

from agentic_sdlc.plugins import Plugin, PluginMetadata


class ConcretePlugin(Plugin):
    """Concrete implementation of Plugin for testing."""

    def __init__(self, name: str = "test-plugin", version: str = "1.0.0"):
        self._name = name
        self._version = version
        self.initialized = False
        self.shutdown_called = False

    @property
    def name(self) -> str:
        return self._name

    @property
    def version(self) -> str:
        return self._version

    def initialize(self, config: Dict[str, Any]) -> None:
        self.initialized = True
        self.config = config

    def shutdown(self) -> None:
        self.shutdown_called = True


class TestPluginMetadata:
    """Tests for PluginMetadata model."""

    def test_plugin_metadata_creation(self):
        """Test creating a PluginMetadata instance."""
        metadata = PluginMetadata(
            name="test-plugin",
            version="1.0.0",
            author="Test Author",
            description="A test plugin",
            entry_point="test_module:TestPlugin",
        )

        assert metadata.name == "test-plugin"
        assert metadata.version == "1.0.0"
        assert metadata.author == "Test Author"
        assert metadata.description == "A test plugin"
        assert metadata.entry_point == "test_module:TestPlugin"
        assert metadata.dependencies == []
        assert metadata.config_schema == {}

    def test_plugin_metadata_with_dependencies(self):
        """Test PluginMetadata with dependencies."""
        metadata = PluginMetadata(
            name="test-plugin",
            version="1.0.0",
            author="Test Author",
            description="A test plugin",
            entry_point="test_module:TestPlugin",
            dependencies=["requests>=2.28.0", "pydantic>=2.0.0"],
        )

        assert metadata.dependencies == ["requests>=2.28.0", "pydantic>=2.0.0"]

    def test_plugin_metadata_with_config_schema(self):
        """Test PluginMetadata with configuration schema."""
        schema = {
            "type": "object",
            "properties": {
                "api_key": {"type": "string"},
                "timeout": {"type": "integer", "minimum": 1},
            },
            "required": ["api_key"],
        }

        metadata = PluginMetadata(
            name="test-plugin",
            version="1.0.0",
            author="Test Author",
            description="A test plugin",
            entry_point="test_module:TestPlugin",
            config_schema=schema,
        )

        assert metadata.config_schema == schema

    def test_plugin_metadata_required_fields(self):
        """Test that PluginMetadata requires all necessary fields."""
        with pytest.raises(Exception):  # Pydantic validation error
            PluginMetadata(
                name="test-plugin",
                # Missing required fields
            )


class TestPluginInterface:
    """Tests for Plugin abstract base class."""

    def test_plugin_cannot_be_instantiated_directly(self):
        """Test that Plugin cannot be instantiated directly."""
        with pytest.raises(TypeError):
            Plugin()  # type: ignore

    def test_concrete_plugin_implementation(self):
        """Test creating a concrete plugin implementation."""
        plugin = ConcretePlugin()

        assert plugin.name == "test-plugin"
        assert plugin.version == "1.0.0"
        assert not plugin.initialized
        assert not plugin.shutdown_called

    def test_plugin_initialization(self):
        """Test plugin initialization."""
        plugin = ConcretePlugin()
        config = {"key": "value"}

        plugin.initialize(config)

        assert plugin.initialized
        assert plugin.config == config

    def test_plugin_shutdown(self):
        """Test plugin shutdown."""
        plugin = ConcretePlugin()

        plugin.shutdown()

        assert plugin.shutdown_called

    def test_plugin_lifecycle(self):
        """Test complete plugin lifecycle."""
        plugin = ConcretePlugin(name="lifecycle-test", version="2.0.0")

        # Initial state
        assert not plugin.initialized
        assert not plugin.shutdown_called

        # Initialize
        config = {"setting": "value"}
        plugin.initialize(config)
        assert plugin.initialized
        assert plugin.config == config

        # Shutdown
        plugin.shutdown()
        assert plugin.shutdown_called

    def test_plugin_with_custom_name_and_version(self):
        """Test plugin with custom name and version."""
        plugin = ConcretePlugin(name="custom-plugin", version="3.5.2")

        assert plugin.name == "custom-plugin"
        assert plugin.version == "3.5.2"

    def test_plugin_properties_are_abstract(self):
        """Test that plugin properties are abstract."""

        class IncompletePlugin(Plugin):
            """Plugin missing required properties."""

            def initialize(self, config: Dict[str, Any]) -> None:
                pass

            def shutdown(self) -> None:
                pass

        # Should not be able to instantiate without implementing properties
        with pytest.raises(TypeError):
            IncompletePlugin()  # type: ignore

    def test_plugin_methods_are_abstract(self):
        """Test that plugin methods are abstract."""

        class IncompletePlugin(Plugin):
            """Plugin missing required methods."""

            @property
            def name(self) -> str:
                return "incomplete"

            @property
            def version(self) -> str:
                return "1.0.0"

        # Should not be able to instantiate without implementing methods
        with pytest.raises(TypeError):
            IncompletePlugin()  # type: ignore
