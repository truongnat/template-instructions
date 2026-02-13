# Configuration Schemas

This directory contains JSON schemas for validating SDLC Kit configuration files.

## Available Schemas

The following schemas are available for configuration validation:

- **workflow.schema.json** - Schema for workflow configurations
  - Validates workflow name, version, agents, tasks, timeout, and retry policies
  - Ensures semantic versioning and task dependencies are properly defined
  
- **agent.schema.json** - Schema for agent configurations
  - Validates agent ID, type, capabilities, model settings, and configuration parameters
  - Supports agent types: ba, pm, sa, implementation, research, quality_judge, security_analyst, devops
  
- **rule.schema.json** - Schema for rule configurations
  - Validates routing and policy rules with conditions and actions
  - Supports priority-based rule evaluation and multiple condition operators
  
- **skill.schema.json** - Schema for skill configurations
  - Validates skill definitions with parameters, return types, and dependencies
  - Supports both project-level and global skills with categorization

## Schema Structure

Each schema defines:
- **Required fields** - Fields that must be present
- **Field types** - Expected data types for each field
- **Validation constraints** - Rules for valid values (min/max, patterns, enums)
- **Default values** - Default values when fields are omitted
- **Documentation** - Descriptions of each field's purpose

## Usage

Schemas are used by the ConfigValidator to ensure configuration files are valid:

```python
from config.validators import ConfigValidator

validator = ConfigValidator()
result = validator.validate_file("my-workflow.yaml", "config/schemas/workflow.schema.json")

if not result.is_valid:
    print(f"Validation errors: {result.errors}")
```

## Schema Format

All schemas follow JSON Schema Draft 7 specification:

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "title": "Configuration Name",
  "type": "object",
  "required": ["field1", "field2"],
  "properties": {
    "field1": {
      "type": "string",
      "description": "Field description"
    }
  }
}
```

## Requirements

This directory satisfies:
- Requirement 3.3: JSON schemas for all configuration types
- Requirement 3.7: Configuration schemas for workflows, agents, rules, and skills
