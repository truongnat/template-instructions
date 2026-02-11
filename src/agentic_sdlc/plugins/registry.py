"""Plugin registry for managing plugin lifecycle and discovery.

This module provides the PluginRegistry class which handles plugin registration,
validation, loading, and lifecycle management. It ensures plugins implement
the required interface and isolates plugin failures from SDK operation.
"""

import logging
from typing import Any, Dict, Optional

from agentic_sdlc.core.exceptions import PluginError

from .base import Plugin

logger = logging.getLogger(__name__)

# Global plugin registry singleton
_plugin_registry: Optional["PluginRegistry"] = None


class PluginRegistry:
    """Registry for managing plugins.

    The PluginRegistry maintains a collection of loaded plugins and provides
    methods for registration, retrieval, and lifecycle management. It validates
    that plugins implement the required interface and isolates plugin failures
    to prevent them from crashing the SDK.

    Features:
    - Plugin registration with interface validation
    - Plugin retrieval by name
    - Plugin unregistration
    - Loading plugins from setuptools entry points
    - Error isolation to prevent plugin failures from crashing SDK
    - Comprehensive logging of plugin operations

    Example:
        >>> registry = PluginRegistry()
        >>> registry.register(my_plugin)
        >>> plugin = registry.get("my-plugin")
        >>> registry.unregister("my-plugin")
    """

    def __init__(self) -> None:
        """Initialize an empty plugin registry."""
        self._plugins: Dict[str, Plugin] = {}
        logger.debug("PluginRegistry initialized")

    def register(self, plugin: Plugin) -> None:
        """Register a plugin with the registry.

        Validates that the plugin implements the required Plugin interface
        before registration. If validation fails, raises PluginError with
        details about missing methods or properties.

        Args:
            plugin: Plugin instance to register

        Raises:
            PluginError: If plugin doesn't implement required interface or
                        if a plugin with the same name is already registered
        """
        # Validate plugin interface
        self._validate_plugin_interface(plugin)

        plugin_name = plugin.name

        # Check for duplicate registration
        if plugin_name in self._plugins:
            raise PluginError(
                f"Plugin '{plugin_name}' is already registered",
                context={"plugin": plugin_name},
            )

        self._plugins[plugin_name] = plugin
        logger.info(
            f"Plugin '{plugin_name}' (v{plugin.version}) registered successfully"
        )

    def unregister(self, name: str) -> None:
        """Unregister a plugin from the registry.

        Calls the plugin's shutdown() method before removing it from the registry.
        If shutdown fails, logs the error but continues with unregistration.

        Args:
            name: Name of the plugin to unregister

        Raises:
            PluginError: If plugin is not found in registry
        """
        if name not in self._plugins:
            raise PluginError(
                f"Plugin '{name}' is not registered",
                context={"plugin": name},
            )

        plugin = self._plugins[name]

        # Call shutdown with error isolation
        try:
            plugin.shutdown()
            logger.debug(f"Plugin '{name}' shutdown completed")
        except Exception as e:
            logger.error(
                f"Error during plugin '{name}' shutdown: {e}",
                exc_info=True,
            )

        del self._plugins[name]
        logger.info(f"Plugin '{name}' unregistered")

    def get(self, name: str) -> Optional[Plugin]:
        """Get a registered plugin by name.

        Args:
            name: Name of the plugin to retrieve

        Returns:
            Plugin instance if found, None otherwise
        """
        return self._plugins.get(name)

    def load_from_entry_points(self) -> None:
        """Load plugins from setuptools entry points.

        Discovers and loads plugins registered via setuptools entry points
        under the 'agentic_sdlc.plugins' group. Each plugin is loaded with
        error isolation - if one plugin fails to load, others continue loading.

        Entry point format in setup.py or pyproject.toml:
            [project.entry-points."agentic_sdlc.plugins"]
            my-plugin = "my_package.plugins:MyPlugin"

        Logs information about each plugin loaded and any errors encountered.
        """
        try:
            import importlib.metadata as importlib_metadata
        except ImportError:
            # Python < 3.8
            import importlib_metadata  # type: ignore

        entry_point_group = "agentic_sdlc.plugins"
        logger.debug(f"Loading plugins from entry point group '{entry_point_group}'")

        try:
            entry_points = importlib_metadata.entry_points()

            # Handle different return types from entry_points()
            # Python 3.10+ returns SelectableGroups, earlier versions return dict
            if hasattr(entry_points, "select"):
                # Python 3.10+ API
                group_eps = entry_points.select(group=entry_point_group)
            elif isinstance(entry_points, dict):
                # Python 3.9 and earlier API
                group_eps = entry_points.get(entry_point_group, [])
            else:
                # Fallback for other versions
                group_eps = entry_points.get(entry_point_group, [])

            for ep in group_eps:
                self._load_entry_point(ep)

        except Exception as e:
            logger.error(
                f"Error loading plugins from entry points: {e}",
                exc_info=True,
            )

    def _load_entry_point(self, entry_point: Any) -> None:
        """Load a single entry point with error isolation.

        Args:
            entry_point: Entry point object to load
        """
        ep_name = entry_point.name
        ep_value = entry_point.value

        try:
            logger.debug(f"Loading plugin from entry point '{ep_name}': {ep_value}")

            # Load the plugin class
            plugin_class = entry_point.load()

            # Instantiate the plugin
            plugin = plugin_class()

            # Register the plugin
            self.register(plugin)

            logger.info(f"Successfully loaded plugin '{ep_name}' from entry point")

        except Exception as e:
            logger.error(
                f"Failed to load plugin from entry point '{ep_name}': {e}",
                exc_info=True,
            )

    def _validate_plugin_interface(self, plugin: Plugin) -> None:
        """Validate that a plugin implements the required interface.

        Checks that the plugin has all required properties and methods.

        Args:
            plugin: Plugin instance to validate

        Raises:
            PluginError: If plugin is missing required interface elements
        """
        required_properties = ["name", "version"]
        required_methods = ["initialize", "shutdown"]

        missing_properties = []
        for prop in required_properties:
            try:
                getattr(plugin, prop)
            except AttributeError:
                missing_properties.append(prop)

        missing_methods = []
        for method in required_methods:
            if not hasattr(plugin, method) or not callable(getattr(plugin, method)):
                missing_methods.append(method)

        if missing_properties or missing_methods:
            missing = missing_properties + missing_methods
            raise PluginError(
                f"Plugin does not implement required interface",
                context={
                    "plugin_class": plugin.__class__.__name__,
                    "missing": missing,
                },
            )


def get_plugin_registry() -> PluginRegistry:
    """Get the global plugin registry singleton.

    Returns:
        The global PluginRegistry instance, creating it if necessary
    """
    global _plugin_registry
    if _plugin_registry is None:
        _plugin_registry = PluginRegistry()
    return _plugin_registry
