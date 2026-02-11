# Configuration Validator Usage Guide

The `ConfigValidator` class provides comprehensive validation of configuration files against JSON schemas.

## Quick Start

```python
from config.validators import ConfigValidator

# Create validator instance
validator = ConfigValidator()

# Validate a configuration file
result = validator.load_and_validate(
    "config/my-workflow.yaml",
    "config/schemas/workflow.schema.json"
)

# Check result
if result.is_valid:
    print("✓ Configuration is valid!")
else:
    print("✗ Validation failed:")
    for error in result.errors:
        print(f"  - {error}")
```

## Features

### 1. Load and Validate Configuration Files

Supports both YAML and JSON configuration files:

```python
# YAML file
result = validator.load_and_validate("config.yaml", "schema.json")

# JSON file
result = validator.load_and_validate("config.json", "schema.json")
```

### 2. Validate by Configuration Type

Use the convenience method to automatically select the correct schema:

```python
# Automatically uses config/schemas/workflow.schema.json
result = validator.validate_by_type("my-workflow.yaml", "workflow")

# Supported types: workflow, agent, rule, skill
result = validator.validate_by_type("my-agent.yaml", "agent")
```

### 3. Descriptive Error Messages

The validator provides detailed error messages that include:
- Field names (including nested fields)
- Expected types or values
- Actual values received

Example error messages:
```
Field 'timeout': expected type 'integer', got 'str'
Field 'type': value 'invalid' is not allowed. Allowed values: 'ba', 'pm', 'sa'
Field '(root)': missing required fields: 'name', 'version'
Field 'metadata.version': expected type 'string', got 'int'
```

### 4. Validation Result Object

The `ValidationResult` object provides:
- `is_valid`: Boolean indicating if validation passed
- `errors`: List of error messages
- `warnings`: List of warning messages
- `config_file`: Path to the configuration file
- `schema_file`: Path to the schema file

```python
result = validator.load_and_validate("config.yaml", "schema.json")

print(f"Valid: {result.is_valid}")
print(f"Errors: {len(result.errors)}")
print(f"Config: {result.config_file}")

# String representation
print(result)  # Formatted output with ✓ or ✗
```

## Advanced Usage

### Custom Schema Directory

```python
validator = ConfigValidator(schema_dir="custom/schemas")
```

### Direct Validation (without loading files)

```python
config = {"name": "test", "version": "1.0.0"}
schema = {
    "type": "object",
    "required": ["name", "version"],
    "properties": {
        "name": {"type": "string"},
        "version": {"type": "string"}
    }
}

result = validator.validate(config, schema)
```

### Load Configuration Only

```python
config = validator.load_config("config.yaml")
# Returns parsed dictionary
```

### Load Schema Only

```python
schema = validator.load_schema("schema.json")
# Returns parsed schema dictionary
# Schemas are cached for performance
```

## Error Handling

The validator handles various error conditions gracefully:

```python
try:
    result = validator.load_and_validate("config.yaml", "schema.json")
    if not result.is_valid:
        # Handle validation errors
        for error in result.errors:
            print(f"Error: {error}")
except FileNotFoundError as e:
    print(f"File not found: {e}")
except ValueError as e:
    print(f"Invalid file format: {e}")
```

## Supported Validation Rules

The validator supports all JSON Schema Draft 7 validation rules:

- **Type validation**: `type`, `enum`
- **Numeric validation**: `minimum`, `maximum`, `multipleOf`
- **String validation**: `minLength`, `maxLength`, `pattern`
- **Array validation**: `minItems`, `maxItems`, `uniqueItems`
- **Object validation**: `required`, `properties`, `additionalProperties`
- **Conditional validation**: `if`, `then`, `else`
- **Schema composition**: `allOf`, `anyOf`, `oneOf`, `not`

## Example: Validating Multiple Files

```python
from pathlib import Path
from config.validators import ConfigValidator

validator = ConfigValidator()

# Validate all workflow files in a directory
workflow_dir = Path("workflows")
for workflow_file in workflow_dir.glob("*.yaml"):
    result = validator.validate_by_type(workflow_file, "workflow")
    if result.is_valid:
        print(f"✓ {workflow_file.name}")
    else:
        print(f"✗ {workflow_file.name}")
        for error in result.errors:
            print(f"    {error}")
```

## Testing

Run the unit tests:

```bash
pytest tests/unit/test_config_validator.py -v
```

Run the demonstration script:

```bash
python config/test_validator_demo.py
```

## Integration with Scripts

The validator can be used in validation scripts:

```python
#!/usr/bin/env python3
import sys
from pathlib import Path
from config.validators import ConfigValidator

def main():
    validator = ConfigValidator()
    
    # Validate all configuration files
    configs = [
        ("config/defaults.yaml", "workflow"),
        ("config/examples/development.yaml", "workflow"),
        ("config/examples/production.yaml", "workflow"),
    ]
    
    all_valid = True
    for config_file, config_type in configs:
        result = validator.validate_by_type(config_file, config_type)
        print(result)
        if not result.is_valid:
            all_valid = False
    
    sys.exit(0 if all_valid else 1)

if __name__ == "__main__":
    main()
```

## See Also

- JSON Schema specification: https://json-schema.org/
- jsonschema library documentation: https://python-jsonschema.readthedocs.io/
- Configuration schemas: `config/schemas/`
- Example configurations: `config/examples/`
