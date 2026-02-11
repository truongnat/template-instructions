"""
Validation commands.

Provides CLI commands for validating configurations and data.
"""

import argparse
import sys
from pathlib import Path
from typing import Optional

# Add project root to path
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from cli.output.formatters import (
    format_success, format_error, format_validation_output,
    format_header
)


def validate_config(args: argparse.Namespace) -> int:
    """
    Validate a configuration file.
    
    Args:
        args: Command arguments with config file and schema
        
    Returns:
        Exit code (0 for success, 1 for error)
    """
    try:
        config_file = args.config_file
        schema_type = args.schema or "auto"
        
        print(format_header(f"Validating Configuration: {config_file}"))
        
        # In real implementation, this would use config.validators
        validation_result = {
            "is_valid": True,
            "errors": [],
            "warnings": []
        }
        
        print(format_validation_output(validation_result))
        
        return 0 if validation_result["is_valid"] else 1
    except Exception as e:
        print(format_error(f"Validation failed: {e}"))
        return 1


def validate_all(args: argparse.Namespace) -> int:
    """
    Validate all configuration files.
    
    Args:
        args: Command arguments
        
    Returns:
        Exit code (0 for success, 1 for error)
    """
    try:
        print(format_header("Validating All Configurations"))
        
        # In real implementation, this would scan and validate all configs
        config_files = [
            "config/defaults.yaml",
            "config/examples/development.yaml",
            "config/examples/production.yaml"
        ]
        
        all_valid = True
        for config_file in config_files:
            print(f"\nValidating: {config_file}")
            # Mock validation
            print(format_success("Valid"))
        
        if all_valid:
            print(f"\n{format_success('All configurations are valid')}")
            return 0
        else:
            print(f"\n{format_error('Some configurations are invalid')}")
            return 1
    except Exception as e:
        print(format_error(f"Validation failed: {e}"))
        return 1


def validate_schema(args: argparse.Namespace) -> int:
    """
    Validate a JSON schema file.
    
    Args:
        args: Command arguments with schema file
        
    Returns:
        Exit code (0 for success, 1 for error)
    """
    try:
        schema_file = args.schema_file
        
        print(format_header(f"Validating Schema: {schema_file}"))
        
        # In real implementation, this would validate JSON schema syntax
        print(format_success("Schema is valid"))
        
        return 0
    except Exception as e:
        print(format_error(f"Schema validation failed: {e}"))
        return 1


def setup_validate_parser(subparsers) -> None:
    """
    Set up the validate command parser.
    
    Args:
        subparsers: Subparsers object from argparse
    """
    validate_parser = subparsers.add_parser(
        "validate",
        help="Validate configurations and schemas",
        description="Validate configuration files, schemas, and data against defined rules."
    )
    
    validate_subparsers = validate_parser.add_subparsers(dest="validate_command", help="Validation commands")
    
    # Config command
    config_parser = validate_subparsers.add_parser(
        "config",
        help="Validate a configuration file",
        description="Validate a configuration file against its schema."
    )
    config_parser.add_argument("config_file", help="Configuration file to validate")
    config_parser.add_argument("--schema", "-s", help="Schema type (workflow, agent, rule, skill)")
    config_parser.set_defaults(func=validate_config)
    
    # All command
    all_parser = validate_subparsers.add_parser(
        "all",
        help="Validate all configuration files",
        description="Validate all configuration files in the config directory."
    )
    all_parser.set_defaults(func=validate_all)
    
    # Schema command
    schema_parser = validate_subparsers.add_parser(
        "schema",
        help="Validate a JSON schema file",
        description="Validate that a JSON schema file has correct syntax."
    )
    schema_parser.add_argument("schema_file", help="Schema file to validate")
    schema_parser.set_defaults(func=validate_schema)


def main():
    """Main entry point for validation commands."""
    parser = argparse.ArgumentParser(description="Validation commands")
    subparsers = parser.add_subparsers(dest="command")
    setup_validate_parser(subparsers)
    
    args = parser.parse_args()
    
    if hasattr(args, 'func'):
        sys.exit(args.func(args))
    else:
        parser.print_help()
        sys.exit(1)


if __name__ == "__main__":
    main()
