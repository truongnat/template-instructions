"""Base classes and interfaces for the plugin system.

This module defines the plugin interface that all plugins must implement,
as well as metadata structures for plugin discovery and configuration.
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


class PluginMetadata(BaseModel):
    """Metadata describing a plugin.

    This model contains information about a plugin including its identity,
    version, dependencies, and configuration schema. It's used for plugin
    discovery, validation, and documentation.

    Attributes:
        name: Unique identifier for the plugin
        version: Plugin version following semantic versioning
        author: Plugin author or organization
        description: Human-readable description of plugin functionality
        dependencies: List of required Python packages
        entry_point: Fully qualified class name for plugin entry point
        config_schema: JSON schema for plugin configuration validation
    """

    name: str = Field(..., description="Unique plugin identifier")
    version: str = Field(..., description="Plugin version (semver format)")
    author: str = Field(..., description="Plugin author or organization")
    description: str = Field(..., description="Plugin description")
    dependencies: List[str] = Field(
        default_factory=list,
        description="Required Python packages",
    )
    entry_point: str = Field(..., description="Fully qualified class name")
    config_schema: Dict[str, Any] = Field(
        default_factory=dict,
        description="JSON schema for configuration validation",
    )


class Plugin(ABC):
    """Abstract base class for all plugins.

    All plugins must inherit from this class and implement the required
    abstract properties and methods. The plugin lifecycle consists of:

    1. Instantiation: Plugin object is created
    2. Initialization: initialize() is called with configuration
    3. Operation: Plugin provides its functionality
    4. Shutdown: shutdown() is called for cleanup

    Example:
        >>> class MyPlugin(Plugin):
        ...     @property
        ...     def name(self) -> str:
        ...         return "my-plugin"
        ...
        ...     @property
        ...     def version(self) -> str:
        ...         return "1.0.0"
        ...
        ...     def initialize(self, config: Dict[str, Any]) -> None:
        ...         # Setup plugin with configuration
        ...         pass
        ...
        ...     def shutdown(self) -> None:
        ...         # Cleanup resources
        ...         pass
    """

    @property
    @abstractmethod
    def name(self) -> str:
        """Get the plugin name.

        Returns:
            Unique identifier for this plugin. Should be lowercase with hyphens
            (e.g., "my-plugin"). Must be consistent across plugin versions.
        """
        pass

    @property
    @abstractmethod
    def version(self) -> str:
        """Get the plugin version.

        Returns:
            Version string following semantic versioning (e.g., "1.0.0").
            Used for compatibility checking and dependency resolution.
        """
        pass

    @abstractmethod
    def initialize(self, config: Dict[str, Any]) -> None:
        """Initialize the plugin with configuration.

        This method is called once when the plugin is loaded. It should
        perform any setup required for the plugin to function, such as:
        - Validating configuration
        - Initializing resources (connections, files, etc.)
        - Registering handlers or callbacks
        - Loading dependencies

        Args:
            config: Configuration dictionary for this plugin. The structure
                   depends on the plugin's requirements.

        Raises:
            PluginError: If initialization fails for any reason. The error
                        should include context about what failed and why.
        """
        pass

    @abstractmethod
    def shutdown(self) -> None:
        """Shut down the plugin and clean up resources.

        This method is called when the plugin is being unloaded. It should
        perform cleanup such as:
        - Closing connections
        - Releasing file handles
        - Unregistering handlers
        - Freeing memory

        This method should not raise exceptions. If cleanup fails, it should
        log the error but not propagate it.
        """
        pass
