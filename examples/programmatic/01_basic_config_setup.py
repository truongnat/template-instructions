#!/usr/bin/env python3
"""
Example 1: Basic Configuration and Setup

This example demonstrates:
- Loading configuration from files and environment variables
- Setting up logging
- Accessing configuration values
- Creating a basic SDK instance

Run: python 01_basic_config_setup.py
"""

import os
from pathlib import Path
from agentic_sdlc import Config, setup_logging, get_logger, __version__


def main():
    """Main example function."""
    
    print("=" * 60)
    print("Example 1: Basic Configuration and Setup")
    print("=" * 60)
    print()
    
    # Display SDK version
    print(f"Agentic SDLC Version: {__version__}")
    print()
    
    # Setup logging
    print("Setting up logging...")
    setup_logging(level="INFO")
    logger = get_logger(__name__)
    logger.info("Logging configured successfully")
    print()
    
    # Load configuration
    print("Loading configuration...")
    try:
        # Create a Config instance
        # It will look for configuration in:
        # 1. Environment variables (AGENTIC_* prefix)
        # 2. Configuration file (if specified)
        # 3. Default values
        config = Config()
        logger.info("Configuration loaded successfully")
        print()
    except Exception as e:
        logger.error(f"Failed to load configuration: {e}")
        return
    
    # Access configuration values
    print("Accessing configuration values:")
    print("-" * 40)
    
    # Get log level
    log_level = config.get("log_level", "INFO")
    print(f"  Log Level: {log_level}")
    
    # Get project root
    project_root = config.get("project_root", str(Path.cwd()))
    print(f"  Project Root: {project_root}")
    
    # Get log file
    log_file = config.get("log_file")
    print(f"  Log File: {log_file or 'Not configured'}")
    
    print()
    
    # Set configuration values
    print("Setting configuration values:")
    print("-" * 40)
    
    try:
        # Set a configuration value
        config.set("log_level", "DEBUG")
        print("  ✓ Set log_level to DEBUG")
        
        # Verify the value was set
        new_log_level = config.get("log_level")
        print(f"  ✓ Verified log_level is now: {new_log_level}")
        
        print()
    except Exception as e:
        logger.error(f"Failed to set configuration: {e}")
        return
    
    # Validate configuration
    print("Validating configuration:")
    print("-" * 40)
    
    try:
        config.validate()
        print("  ✓ Configuration is valid")
        print()
    except Exception as e:
        logger.error(f"Configuration validation failed: {e}")
        return
    
    # Display configuration summary
    print("Configuration Summary:")
    print("-" * 40)
    print(f"  Project Root: {config.get('project_root', 'Not set')}")
    print(f"  Log Level: {config.get('log_level', 'Not set')}")
    print(f"  Log File: {config.get('log_file', 'Not set')}")
    print()
    
    # Example: Using configuration in your application
    print("Example: Using configuration in your application:")
    print("-" * 40)
    
    # Get logger with configured level
    app_logger = get_logger("my_app")
    app_logger.debug("This is a debug message")
    app_logger.info("This is an info message")
    app_logger.warning("This is a warning message")
    
    print()
    print("=" * 60)
    print("Example completed successfully!")
    print("=" * 60)


if __name__ == "__main__":
    main()
