#!/usr/bin/env python3
"""
Example 4: Custom Plugin Development

This example demonstrates:
- Implementing the Plugin interface
- Registering custom plugins
- Plugin initialization and shutdown
- Using plugins in workflows

Run: python 04_custom_plugin.py
"""

from typing import Dict, Any
from agentic_sdlc import (
    Plugin,
    get_plugin_registry,
    setup_logging,
    get_logger,
    PluginError,
)


class AnalyticsPlugin(Plugin):
    """Example plugin that provides analytics capabilities."""
    
    def __init__(self):
        """Initialize the plugin."""
        self.logger = get_logger(__name__)
        self.config: Dict[str, Any] = {}
        self.metrics: Dict[str, Any] = {}
        self.initialized = False
    
    @property
    def name(self) -> str:
        """Return plugin name."""
        return "analytics-plugin"
    
    @property
    def version(self) -> str:
        """Return plugin version."""
        return "1.0.0"
    
    def initialize(self, config: Dict[str, Any]) -> None:
        """Initialize plugin with configuration.
        
        Args:
            config: Plugin configuration dictionary
            
        Raises:
            PluginError: If initialization fails
        """
        try:
            self.logger.info(f"Initializing {self.name} v{self.version}")
            
            # Validate configuration
            if not isinstance(config, dict):
                raise PluginError("Configuration must be a dictionary")
            
            # Store configuration
            self.config = config
            
            # Initialize metrics
            self.metrics = {
                "events_tracked": 0,
                "errors_logged": 0,
                "status": "active"
            }
            
            self.initialized = True
            self.logger.info(f"Plugin {self.name} initialized successfully")
            
        except Exception as e:
            self.logger.error(f"Failed to initialize plugin: {e}")
            raise PluginError(f"Initialization failed: {e}") from e
    
    def shutdown(self) -> None:
        """Clean up plugin resources."""
        try:
            self.logger.info(f"Shutting down {self.name}")
            
            # Log final metrics
            self.logger.info(f"Final metrics: {self.metrics}")
            
            # Cleanup
            self.metrics["status"] = "shutdown"
            self.initialized = False
            
            self.logger.info(f"Plugin {self.name} shutdown complete")
            
        except Exception as e:
            self.logger.error(f"Error during shutdown: {e}")
    
    def track_event(self, event_name: str, data: Dict[str, Any]) -> None:
        """Track an event.
        
        Args:
            event_name: Name of the event
            data: Event data
        """
        if not self.initialized:
            raise PluginError("Plugin not initialized")
        
        self.logger.debug(f"Tracking event: {event_name}")
        self.metrics["events_tracked"] += 1
    
    def log_error(self, error_message: str) -> None:
        """Log an error.
        
        Args:
            error_message: Error message to log
        """
        if not self.initialized:
            raise PluginError("Plugin not initialized")
        
        self.logger.error(f"Plugin error: {error_message}")
        self.metrics["errors_logged"] += 1
    
    def get_metrics(self) -> Dict[str, Any]:
        """Get plugin metrics.
        
        Returns:
            Dictionary of metrics
        """
        return self.metrics.copy()


class LoggingPlugin(Plugin):
    """Example plugin that provides enhanced logging capabilities."""
    
    def __init__(self):
        """Initialize the plugin."""
        self.logger = get_logger(__name__)
        self.config: Dict[str, Any] = {}
        self.initialized = False
    
    @property
    def name(self) -> str:
        """Return plugin name."""
        return "logging-plugin"
    
    @property
    def version(self) -> str:
        """Return plugin version."""
        return "1.0.0"
    
    def initialize(self, config: Dict[str, Any]) -> None:
        """Initialize plugin with configuration.
        
        Args:
            config: Plugin configuration dictionary
        """
        self.logger.info(f"Initializing {self.name} v{self.version}")
        self.config = config
        self.initialized = True
        self.logger.info(f"Plugin {self.name} initialized successfully")
    
    def shutdown(self) -> None:
        """Clean up plugin resources."""
        self.logger.info(f"Shutting down {self.name}")
        self.initialized = False
        self.logger.info(f"Plugin {self.name} shutdown complete")


def main():
    """Main example function."""
    
    print("=" * 60)
    print("Example 4: Custom Plugin Development")
    print("=" * 60)
    print()
    
    # Setup logging
    setup_logging(level="INFO")
    logger = get_logger(__name__)
    
    # Get plugin registry
    print("Getting plugin registry...")
    print("-" * 40)
    
    registry = get_plugin_registry()
    print("  ✓ Plugin registry obtained")
    print()
    
    # Create plugins
    print("Creating plugins...")
    print("-" * 40)
    
    try:
        analytics_plugin = AnalyticsPlugin()
        logging_plugin = LoggingPlugin()
        
        print(f"  ✓ Created: {analytics_plugin.name} v{analytics_plugin.version}")
        print(f"  ✓ Created: {logging_plugin.name} v{logging_plugin.version}")
        print()
        
    except Exception as e:
        logger.error(f"Failed to create plugins: {e}")
        return
    
    # Initialize plugins
    print("Initializing plugins...")
    print("-" * 40)
    
    try:
        # Initialize analytics plugin
        analytics_config = {
            "track_events": True,
            "log_errors": True,
            "buffer_size": 1000
        }
        analytics_plugin.initialize(analytics_config)
        print(f"  ✓ Initialized: {analytics_plugin.name}")
        
        # Initialize logging plugin
        logging_config = {
            "log_level": "DEBUG",
            "format": "detailed"
        }
        logging_plugin.initialize(logging_config)
        print(f"  ✓ Initialized: {logging_plugin.name}")
        print()
        
    except Exception as e:
        logger.error(f"Failed to initialize plugins: {e}")
        return
    
    # Register plugins
    print("Registering plugins...")
    print("-" * 40)
    
    try:
        registry.register(analytics_plugin)
        print(f"  ✓ Registered: {analytics_plugin.name}")
        
        registry.register(logging_plugin)
        print(f"  ✓ Registered: {logging_plugin.name}")
        print()
        
    except Exception as e:
        logger.error(f"Failed to register plugins: {e}")
        return
    
    # Use plugins
    print("Using plugins...")
    print("-" * 40)
    
    try:
        # Get plugin from registry
        analytics = registry.get("analytics-plugin")
        
        if analytics:
            # Track events
            analytics.track_event("workflow_started", {"workflow": "example"})
            analytics.track_event("task_completed", {"task": "analysis"})
            
            # Get metrics
            metrics = analytics.get_metrics()
            print(f"  ✓ Analytics metrics: {metrics}")
        
        print()
        
    except Exception as e:
        logger.error(f"Failed to use plugins: {e}")
        return
    
    # Display plugin information
    print("Plugin Information:")
    print("-" * 40)
    
    for plugin in [analytics_plugin, logging_plugin]:
        print(f"  Plugin: {plugin.name}")
        print(f"    Version: {plugin.version}")
        print(f"    Status: {'Initialized' if plugin.initialized else 'Not initialized'}")
        print()
    
    # Shutdown plugins
    print("Shutting down plugins...")
    print("-" * 40)
    
    try:
        analytics_plugin.shutdown()
        print(f"  ✓ Shutdown: {analytics_plugin.name}")
        
        logging_plugin.shutdown()
        print(f"  ✓ Shutdown: {logging_plugin.name}")
        print()
        
    except Exception as e:
        logger.error(f"Error during shutdown: {e}")
        return
    
    print("=" * 60)
    print("Example completed successfully!")
    print("=" * 60)


if __name__ == "__main__":
    main()
