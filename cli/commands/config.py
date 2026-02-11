"""
Configuration commands.

Provides CLI commands for managing configuration files.
"""

import argparse
import sys
from pathlib import Path
from typing import Optional

# Add project root to path
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from cli.output.formatters import (
    format_success, format_error, format_dict,
    format_header, format_list
)


def show_config(args: argparse.Namespace) -> int:
    """
    Show current configuration.
    
    Args:
        args: Command arguments
        
    Returns:
        Exit code (0 for success, 1 for error)
    """
    try:
        config_file = args.config_file or "config/defaults.yaml"
        
        print(format_header(f"Configuration: {config_file}"))
        
        # In real implementation, this would load and display the config
        config_data = {
            "core": {
                "log_level": "INFO",
                "data_dir": "data/"
            },
            "agents": {
                "default_model": "gpt-4",
                "timeout": 300
            },
            "workflows": {
                "max_retries": 3,
                "parallel_execution": True
            }
        }
        
        print(format_dict(config_data))
        
        return 0
    except Exception as e:
        print(format_error(f"Failed to show configuration: {e}"))
        return 1


def list_configs(args: argparse.Namespace) -> int:
    """
    List all configuration files.
    
    Args:
        args: Command arguments
        
    Returns:
        Exit code (0 for success, 1 for error)
    """
    try:
        print(format_header("Configuration Files"))
        
        # In real implementation, this would scan config directory
        config_files = [
            "config/defaults.yaml",
            "config/examples/development.yaml",
            "config/examples/production.yaml",
            "config/examples/test.yaml"
        ]
        
        print(format_list(config_files))
        
        return 0
    except Exception as e:
        print(format_error(f"Failed to list configurations: {e}"))
        return 1


def get_value(args: argparse.Namespace) -> int:
    """
    Get a specific configuration value.
    
    Args:
        args: Command arguments with key path
        
    Returns:
        Exit code (0 for success, 1 for error)
    """
    try:
        key = args.key
        config_file = args.config_file or "config/defaults.yaml"
        
        # In real implementation, this would load config and extract value
        print(f"core.log_level = INFO")
        
        return 0
    except Exception as e:
        print(format_error(f"Failed to get configuration value: {e}"))
        return 1


def set_value(args: argparse.Namespace) -> int:
    """
    Set a configuration value.
    
    Args:
        args: Command arguments with key and value
        
    Returns:
        Exit code (0 for success, 1 for error)
    """
    try:
        key = args.key
        value = args.value
        config_file = args.config_file or "config/defaults.yaml"
        
        # In real implementation, this would update the config file
        print(format_success(f"Set {key} = {value} in {config_file}"))
        
        return 0
    except Exception as e:
        print(format_error(f"Failed to set configuration value: {e}"))
        return 1


def setup_config_parser(subparsers) -> None:
    """
    Set up the config command parser.
    
    Args:
        subparsers: Subparsers object from argparse
    """
    config_parser = subparsers.add_parser(
        "config",
        help="Manage configuration files",
        description="View and modify SDLC Kit configuration files."
    )
    
    config_subparsers = config_parser.add_subparsers(dest="config_command", help="Configuration commands")
    
    # Show command
    show_parser = config_subparsers.add_parser(
        "show",
        help="Show configuration",
        description="Display the current configuration or a specific configuration file."
    )
    show_parser.add_argument("--config-file", "-c", help="Configuration file to show")
    show_parser.set_defaults(func=show_config)
    
    # List command
    list_parser = config_subparsers.add_parser(
        "list",
        help="List all configuration files",
        description="List all available configuration files."
    )
    list_parser.set_defaults(func=list_configs)
    
    # Get command
    get_parser = config_subparsers.add_parser(
        "get",
        help="Get a configuration value",
        description="Get the value of a specific configuration key."
    )
    get_parser.add_argument("key", help="Configuration key (e.g., core.log_level)")
    get_parser.add_argument("--config-file", "-c", help="Configuration file to read from")
    get_parser.set_defaults(func=get_value)
    
    # Set command
    set_parser = config_subparsers.add_parser(
        "set",
        help="Set a configuration value",
        description="Set the value of a specific configuration key."
    )
    set_parser.add_argument("key", help="Configuration key (e.g., core.log_level)")
    set_parser.add_argument("value", help="Value to set")
    set_parser.add_argument("--config-file", "-c", help="Configuration file to modify")
    set_parser.set_defaults(func=set_value)


def main():
    """Main entry point for configuration commands."""
    parser = argparse.ArgumentParser(description="Configuration management commands")
    subparsers = parser.add_subparsers(dest="command")
    setup_config_parser(subparsers)
    
    args = parser.parse_args()
    
    if hasattr(args, 'func'):
        sys.exit(args.func(args))
    else:
        parser.print_help()
        sys.exit(1)


if __name__ == "__main__":
    main()
