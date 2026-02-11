#!/usr/bin/env python3
"""Configuration validation script for SDLC Kit.

This script validates all configuration files against their corresponding
JSON schemas and reports any validation errors with specific details.

Exit codes:
    0: All configurations are valid
    1: One or more configurations are invalid
"""

import sys
from pathlib import Path
from typing import List, Tuple

# Add parent directory to path to import config module
sys.path.insert(0, str(Path(__file__).parent.parent))

from config.validators import ConfigValidator, ValidationResult


def validate_config_file(
    validator: ConfigValidator,
    config_file: Path,
    schema_file: Path
) -> ValidationResult:
    """Validate a single configuration file.
    
    Args:
        validator: ConfigValidator instance
        config_file: Path to configuration file
        schema_file: Path to schema file
        
    Returns:
        ValidationResult with validation status and errors
    """
    try:
        result = validator.load_and_validate(config_file, schema_file)
        return result
    except Exception as e:
        result = ValidationResult(
            is_valid=False,
            config_file=str(config_file),
            schema_file=str(schema_file)
        )
        result.add_error(f"Unexpected error: {str(e)}")
        return result


def print_result(result: ValidationResult, verbose: bool = True) -> None:
    """Print validation result in a clear format.
    
    Args:
        result: ValidationResult to print
        verbose: Whether to print detailed error messages
    """
    if result.is_valid:
        print(f"✓ {result.config_file}")
    else:
        print(f"✗ {result.config_file}")
        if verbose and result.errors:
            for error in result.errors:
                print(f"    {error}")


def main() -> int:
    """Main function to validate all configuration files.
    
    Returns:
        Exit code (0 for success, 1 for failure)
    """
    print("=" * 60)
    print("SDLC Kit Configuration Validation")
    print("=" * 60)
    print()
    
    # Initialize validator
    validator = ConfigValidator()
    
    # Define configuration-schema mappings
    # Format: (config_file, schema_file, description)
    validations: List[Tuple[str, str, str]] = [
        (
            "config/defaults.yaml",
            "config/schemas/workflow.schema.json",
            "Default configuration"
        ),
        (
            "config/examples/development.yaml",
            "config/schemas/workflow.schema.json",
            "Development configuration"
        ),
        (
            "config/examples/production.yaml",
            "config/schemas/workflow.schema.json",
            "Production configuration"
        ),
        (
            "config/examples/test.yaml",
            "config/schemas/workflow.schema.json",
            "Test configuration"
        ),
    ]
    
    # Track results
    all_valid = True
    total_configs = 0
    valid_configs = 0
    invalid_configs = 0
    
    # Validate each configuration
    for config_path, schema_path, description in validations:
        config_file = Path(config_path)
        schema_file = Path(schema_path)
        
        # Skip if files don't exist
        if not config_file.exists():
            print(f"⚠ {config_path} (not found, skipping)")
            continue
        
        if not schema_file.exists():
            print(f"⚠ {config_path} (schema not found: {schema_path}, skipping)")
            continue
        
        total_configs += 1
        
        # Validate
        result = validate_config_file(validator, config_file, schema_file)
        
        # Print result
        print_result(result, verbose=True)
        
        # Update counters
        if result.is_valid:
            valid_configs += 1
        else:
            invalid_configs += 1
            all_valid = False
        
        print()
    
    # Print summary
    print("=" * 60)
    print("Validation Summary")
    print("=" * 60)
    print(f"Total configurations checked: {total_configs}")
    print(f"Valid: {valid_configs}")
    print(f"Invalid: {invalid_configs}")
    print()
    
    if all_valid:
        print("✓ All configurations are valid!")
        return 0
    else:
        print("✗ Some configurations are invalid")
        print()
        print("Please fix the errors listed above and run validation again.")
        return 1


if __name__ == "__main__":
    sys.exit(main())
