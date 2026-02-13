"""Configuration validation module for SDLC Kit.

This module provides configuration validation functionality using JSON schemas.
It supports loading YAML and JSON configuration files and validating them
against predefined schemas with detailed error reporting.
"""

import json
import yaml
from pathlib import Path
from typing import Dict, Any, List, Optional, Union
from dataclasses import dataclass, field
from jsonschema import validate, ValidationError, Draft7Validator
from jsonschema.exceptions import SchemaError


@dataclass
class ValidationResult:
    """Result of a configuration validation operation.
    
    Attributes:
        is_valid: Whether the configuration is valid
        errors: List of validation error messages
        warnings: List of validation warnings
        config_file: Path to the configuration file that was validated
        schema_file: Path to the schema file used for validation
    """
    is_valid: bool
    errors: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    config_file: Optional[str] = None
    schema_file: Optional[str] = None
    
    def add_error(self, error: str) -> None:
        """Add an error message to the validation result."""
        self.errors.append(error)
        self.is_valid = False
    
    def add_warning(self, warning: str) -> None:
        """Add a warning message to the validation result."""
        self.warnings.append(warning)
    
    def __str__(self) -> str:
        """Return a human-readable string representation of the validation result."""
        if self.is_valid:
            status = "✓ Valid"
        else:
            status = "✗ Invalid"
        
        lines = [f"{status}: {self.config_file or 'configuration'}"]
        
        if self.errors:
            lines.append("\nErrors:")
            for error in self.errors:
                lines.append(f"  - {error}")
        
        if self.warnings:
            lines.append("\nWarnings:")
            for warning in self.warnings:
                lines.append(f"  - {warning}")
        
        return "\n".join(lines)


class ConfigValidator:
    """Configuration validator using JSON schemas.
    
    This class provides methods to load and validate configuration files
    (YAML or JSON) against JSON schemas. It generates descriptive error
    messages that include field names and expected types.
    
    Example:
        >>> validator = ConfigValidator()
        >>> result = validator.load_and_validate(
        ...     "config/defaults.yaml",
        ...     "config/schemas/workflow.schema.json"
        ... )
        >>> if result.is_valid:
        ...     print("Configuration is valid!")
        ... else:
        ...     print(f"Validation failed: {result.errors}")
    """
    
    def __init__(self, schema_dir: Optional[Union[str, Path]] = None):
        """Initialize the configuration validator.
        
        Args:
            schema_dir: Directory containing JSON schema files.
                       Defaults to 'config/schemas' relative to current directory.
        """
        if schema_dir is None:
            self.schema_dir = Path("config/schemas")
        else:
            self.schema_dir = Path(schema_dir)
        
        self._schema_cache: Dict[str, Dict[str, Any]] = {}
    
    def load_config(self, config_path: Union[str, Path]) -> Dict[str, Any]:
        """Load a configuration file (YAML or JSON).
        
        Args:
            config_path: Path to the configuration file
            
        Returns:
            Parsed configuration as a dictionary
            
        Raises:
            FileNotFoundError: If the configuration file doesn't exist
            ValueError: If the file format is not supported or parsing fails
        """
        config_path = Path(config_path)
        
        if not config_path.exists():
            raise FileNotFoundError(f"Configuration file not found: {config_path}")
        
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                content = f.read()
                
                # Determine file format and parse
                if config_path.suffix in ['.yaml', '.yml']:
                    config = yaml.safe_load(content)
                elif config_path.suffix == '.json':
                    config = json.loads(content)
                else:
                    raise ValueError(
                        f"Unsupported file format: {config_path.suffix}. "
                        "Supported formats: .yaml, .yml, .json"
                    )
                
                # Handle empty files
                if config is None:
                    config = {}
                
                return config
                
        except yaml.YAMLError as e:
            raise ValueError(f"Failed to parse YAML file {config_path}: {e}")
        except json.JSONDecodeError as e:
            raise ValueError(f"Failed to parse JSON file {config_path}: {e}")
    
    def load_schema(self, schema_path: Union[str, Path]) -> Dict[str, Any]:
        """Load a JSON schema file.
        
        Args:
            schema_path: Path to the schema file
            
        Returns:
            Parsed schema as a dictionary
            
        Raises:
            FileNotFoundError: If the schema file doesn't exist
            ValueError: If the schema is invalid
        """
        schema_path = Path(schema_path)
        
        # Check cache first
        cache_key = str(schema_path.absolute())
        if cache_key in self._schema_cache:
            return self._schema_cache[cache_key]
        
        if not schema_path.exists():
            raise FileNotFoundError(f"Schema file not found: {schema_path}")
        
        try:
            with open(schema_path, 'r', encoding='utf-8') as f:
                schema = json.load(f)
            
            # Validate that the schema itself is valid
            try:
                Draft7Validator.check_schema(schema)
            except SchemaError as e:
                raise ValueError(f"Invalid JSON schema in {schema_path}: {e}")
            
            # Cache the schema
            self._schema_cache[cache_key] = schema
            
            return schema
            
        except json.JSONDecodeError as e:
            raise ValueError(f"Failed to parse schema file {schema_path}: {e}")
    
    def validate(
        self,
        config: Dict[str, Any],
        schema: Dict[str, Any],
        config_path: Optional[str] = None,
        schema_path: Optional[str] = None
    ) -> ValidationResult:
        """Validate a configuration against a schema.
        
        Args:
            config: Configuration dictionary to validate
            schema: JSON schema dictionary
            config_path: Optional path to config file (for error messages)
            schema_path: Optional path to schema file (for error messages)
            
        Returns:
            ValidationResult with validation status and any errors
        """
        result = ValidationResult(
            is_valid=True,
            config_file=config_path,
            schema_file=schema_path
        )
        
        try:
            # Create validator and validate
            validator = Draft7Validator(schema)
            errors = sorted(validator.iter_errors(config), key=lambda e: e.path)
            
            if errors:
                result.is_valid = False
                for error in errors:
                    error_msg = self._format_validation_error(error)
                    result.add_error(error_msg)
            
        except Exception as e:
            result.add_error(f"Validation error: {str(e)}")
        
        return result
    
    def load_and_validate(
        self,
        config_path: Union[str, Path],
        schema_path: Union[str, Path]
    ) -> ValidationResult:
        """Load a configuration file and validate it against a schema.
        
        This is the main method for validating configuration files. It loads
        both the configuration and schema files, then performs validation.
        
        Args:
            config_path: Path to the configuration file (YAML or JSON)
            schema_path: Path to the JSON schema file
            
        Returns:
            ValidationResult with validation status and any errors
        """
        config_path = Path(config_path)
        schema_path = Path(schema_path)
        
        result = ValidationResult(
            is_valid=True,
            config_file=str(config_path),
            schema_file=str(schema_path)
        )
        
        # Load configuration
        try:
            config = self.load_config(config_path)
        except FileNotFoundError as e:
            result.add_error(str(e))
            return result
        except ValueError as e:
            result.add_error(f"Configuration loading error: {e}")
            return result
        
        # Load schema
        try:
            schema = self.load_schema(schema_path)
        except FileNotFoundError as e:
            result.add_error(str(e))
            return result
        except ValueError as e:
            result.add_error(f"Schema loading error: {e}")
            return result
        
        # Validate
        return self.validate(
            config,
            schema,
            config_path=str(config_path),
            schema_path=str(schema_path)
        )
    
    def validate_by_type(
        self,
        config_path: Union[str, Path],
        config_type: str
    ) -> ValidationResult:
        """Validate a configuration file using a schema based on type.
        
        This is a convenience method that automatically determines the schema
        file based on the configuration type.
        
        Args:
            config_path: Path to the configuration file
            config_type: Type of configuration (workflow, agent, rule, skill)
            
        Returns:
            ValidationResult with validation status and any errors
        """
        # Map config types to schema files
        schema_map = {
            'workflow': 'workflow.schema.json',
            'agent': 'agent.schema.json',
            'rule': 'rule.schema.json',
            'skill': 'skill.schema.json'
        }
        
        if config_type not in schema_map:
            result = ValidationResult(is_valid=False, config_file=str(config_path))
            result.add_error(
                f"Unknown configuration type: {config_type}. "
                f"Valid types: {', '.join(schema_map.keys())}"
            )
            return result
        
        schema_file = self.schema_dir / schema_map[config_type]
        return self.load_and_validate(config_path, schema_file)
    
    def _format_validation_error(self, error: ValidationError) -> str:
        """Format a validation error into a descriptive message.
        
        Args:
            error: ValidationError from jsonschema
            
        Returns:
            Formatted error message with field name and expected type
        """
        # Build the field path
        if error.path:
            field_path = ".".join(str(p) for p in error.path)
        else:
            field_path = "(root)"
        
        # Get the error message
        message = error.message
        
        # Try to extract expected type information
        validator_name = error.validator
        validator_value = error.validator_value
        
        # Format based on validator type
        if validator_name == "type":
            expected_type = validator_value
            if isinstance(error.instance, type(None)):
                actual_type = "null"
            else:
                actual_type = type(error.instance).__name__
            return (
                f"Field '{field_path}': expected type '{expected_type}', "
                f"got '{actual_type}'"
            )
        
        elif validator_name == "required":
            missing_fields = validator_value
            if isinstance(missing_fields, list):
                fields_str = ", ".join(f"'{f}'" for f in missing_fields)
                return f"Field '{field_path}': missing required fields: {fields_str}"
            else:
                return f"Field '{field_path}': missing required field '{missing_fields}'"
        
        elif validator_name == "enum":
            allowed_values = ", ".join(f"'{v}'" for v in validator_value)
            actual_value = error.instance
            return (
                f"Field '{field_path}': value '{actual_value}' is not allowed. "
                f"Allowed values: {allowed_values}"
            )
        
        elif validator_name == "pattern":
            pattern = validator_value
            actual_value = error.instance
            return (
                f"Field '{field_path}': value '{actual_value}' does not match "
                f"required pattern '{pattern}'"
            )
        
        elif validator_name == "minimum":
            minimum = validator_value
            actual_value = error.instance
            return (
                f"Field '{field_path}': value {actual_value} is less than "
                f"minimum {minimum}"
            )
        
        elif validator_name == "maximum":
            maximum = validator_value
            actual_value = error.instance
            return (
                f"Field '{field_path}': value {actual_value} is greater than "
                f"maximum {maximum}"
            )
        
        elif validator_name == "minLength":
            min_length = validator_value
            actual_length = len(error.instance) if error.instance else 0
            return (
                f"Field '{field_path}': length {actual_length} is less than "
                f"minimum length {min_length}"
            )
        
        elif validator_name == "maxLength":
            max_length = validator_value
            actual_length = len(error.instance) if error.instance else 0
            return (
                f"Field '{field_path}': length {actual_length} is greater than "
                f"maximum length {max_length}"
            )
        
        elif validator_name == "minItems":
            min_items = validator_value
            actual_items = len(error.instance) if error.instance else 0
            return (
                f"Field '{field_path}': array has {actual_items} items, "
                f"minimum is {min_items}"
            )
        
        elif validator_name == "additionalProperties":
            # Find which properties are not allowed
            if hasattr(error, 'schema') and 'properties' in error.schema:
                allowed = set(error.schema['properties'].keys())
                actual = set(error.instance.keys()) if isinstance(error.instance, dict) else set()
                extra = actual - allowed
                if extra:
                    extra_str = ", ".join(f"'{p}'" for p in extra)
                    return (
                        f"Field '{field_path}': contains additional properties "
                        f"not allowed by schema: {extra_str}"
                    )
        
        # Default: use the original message with field path
        return f"Field '{field_path}': {message}"
