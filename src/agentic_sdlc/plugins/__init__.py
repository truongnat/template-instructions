"""Plugin system for SDK extensibility.

This module provides the plugin architecture for extending the Agentic SDLC SDK
with custom functionality. Plugins can be registered, loaded from entry points,
and managed through the PluginRegistry.

Example:
    >>> from agentic_sdlc.plugins import Plugin, get_plugin_registry
    >>> 
    >>> class MyPlugin(Plugin):
    ...     @property
    ...     def name(self) -> str:
    ...         return "my-plugin"
    ...     
    ...     @property
    ...     def version(self) -> str:
    ...         return "1.0.0"
    ...     
    ...     def initialize(self, config):
    ...         pass
    ...     
    ...     def shutdown(self):
    ...         pass
    >>> 
    >>> registry = get_plugin_registry()
    >>> registry.register(MyPlugin())
    >>> plugin = registry.get("my-plugin")
"""

from .base import Plugin, PluginMetadata
from .registry import PluginRegistry, get_plugin_registry

__all__ = [
    "Plugin",
    "PluginMetadata",
    "PluginRegistry",
    "get_plugin_registry",
]
