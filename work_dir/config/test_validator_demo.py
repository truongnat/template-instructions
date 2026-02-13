#!/usr/bin/env python3
"""Demonstration script for configuration validator.

This script demonstrates the ConfigValidator functionality with various
test cases including valid and invalid configurations.
"""

import sys
import tempfile
from pathlib import Path

# Add parent directory to path to import config module
sys.path.insert(0, str(Path(__file__).parent.parent))

from config.validators import ConfigValidator


def main():
    """Run validator demonstration."""
    validator = ConfigValidator()
    
    print("=" * 70)
    print("Configuration Validator Demonstration")
    print("=" * 70)
    print()
    
    # Test 1: Valid workflow configuration
    print("Test 1: Valid workflow configuration")
    print("-" * 70)
    with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
        f.write("""
name: test-workflow
version: 1.0.0
description: A test workflow
agents:
  - agent-1
  - agent-2
tasks:
  - id: task-1
    type: analysis
    config:
      priority: high
      timeout: 300
timeout: 3600
environment: development
""")
        config_file = f.name
    
    result = validator.load_and_validate(config_file, 'config/schemas/workflow.schema.json')
    print(result)
    print()
    Path(config_file).unlink()
    
    # Test 2: Invalid workflow - missing required field
    print("Test 2: Invalid workflow configuration (missing version)")
    print("-" * 70)
    with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
        f.write("""
name: test-workflow
description: Missing version field
""")
        config_file = f.name
    
    result = validator.load_and_validate(config_file, 'config/schemas/workflow.schema.json')
    print(result)
    print()
    Path(config_file).unlink()
    
    # Test 3: Invalid workflow - wrong type
    print("Test 3: Invalid workflow configuration (wrong type)")
    print("-" * 70)
    with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
        f.write("""
name: test-workflow
version: 1.0.0
timeout: "not-a-number"
""")
        config_file = f.name
    
    result = validator.load_and_validate(config_file, 'config/schemas/workflow.schema.json')
    print(result)
    print()
    Path(config_file).unlink()
    
    # Test 4: Valid agent configuration
    print("Test 4: Valid agent configuration")
    print("-" * 70)
    with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
        f.write("""
id: test-agent
type: implementation
name: Test Agent
description: A test agent for demonstration
capabilities:
  - code_generation
  - testing
model: gpt-4
config:
  temperature: 0.7
  max_tokens: 2000
timeout: 300
""")
        config_file = f.name
    
    result = validator.load_and_validate(config_file, 'config/schemas/agent.schema.json')
    print(result)
    print()
    Path(config_file).unlink()
    
    # Test 5: Invalid agent - invalid enum value
    print("Test 5: Invalid agent configuration (invalid type)")
    print("-" * 70)
    with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
        f.write("""
id: test-agent
type: invalid_type
name: Test Agent
""")
        config_file = f.name
    
    result = validator.load_and_validate(config_file, 'config/schemas/agent.schema.json')
    print(result)
    print()
    Path(config_file).unlink()
    
    # Test 6: Using validate_by_type convenience method
    print("Test 6: Using validate_by_type convenience method")
    print("-" * 70)
    with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
        f.write("""
id: test-rule
name: Test Rule
description: A test rule
type: routing
priority: 5
enabled: true
conditions:
  - field: request.text
    operator: contains
    value: urgent
actions:
  - type: route
    target: high-priority-workflow
""")
        config_file = f.name
    
    result = validator.validate_by_type(config_file, 'rule')
    print(result)
    print()
    Path(config_file).unlink()
    
    print("=" * 70)
    print("Demonstration complete!")
    print("=" * 70)


if __name__ == '__main__':
    main()
