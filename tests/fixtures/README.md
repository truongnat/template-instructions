# Test Fixtures and Factories

This directory contains reusable test data, mock objects, and factory functions for creating test instances of various entities in the SDLC Kit.

## Overview

The fixtures module provides:
- **Factories**: Functions for creating test objects with sensible defaults and optional overrides
- **Mock Data**: Pre-defined test data constants for common scenarios
- **Mock Data Generators**: Functions for generating random test data

## Usage

### Importing Fixtures

```python
from tests.fixtures import (
    WorkflowFactory,
    AgentFactory,
    ConfigFactory,
    TaskFactory,
    MockDataGenerator,
    SAMPLE_WORKFLOW,
    COMPLEX_WORKFLOW
)
```

## Factories

### WorkflowFactory

Create workflow configurations for testing.

```python
# Basic workflow
workflow = WorkflowFactory.create_basic_workflow()

# Workflow with custom values
workflow = WorkflowFactory.create_basic_workflow(
    name="my-workflow",
    timeout=7200
)

# Workflow with tasks
workflow = WorkflowFactory.create_workflow_with_tasks(num_tasks=5)

# Workflow with agents
workflow = WorkflowFactory.create_workflow_with_agents(num_agents=3)

# Complex workflow with dependencies
workflow = WorkflowFactory.create_complex_workflow()

# Minimal workflow (only required fields)
workflow = WorkflowFactory.create_minimal_workflow()
```

### AgentFactory

Create agent configurations for testing.

```python
# Basic agent
agent = AgentFactory.create_agent()

# Agent with specific type
agent = AgentFactory.create_agent(agent_type="pm")

# Agent pool
agents = AgentFactory.create_agent_pool(num_agents=5)

# Specialized agents
ba_agent = AgentFactory.create_ba_agent()
pm_agent = AgentFactory.create_pm_agent()
sa_agent = AgentFactory.create_sa_agent()
impl_agent = AgentFactory.create_implementation_agent()
```

### ConfigFactory

Create configuration objects for testing.

```python
# Basic config
config = ConfigFactory.create_config()

# Environment-specific configs
dev_config = ConfigFactory.create_development_config()
prod_config = ConfigFactory.create_production_config()
test_config = ConfigFactory.create_test_config()

# Custom config
config = ConfigFactory.create_config(
    core={"log_level": "DEBUG"}
)
```

### TaskFactory

Create task configurations for testing.

```python
# Basic task
task = TaskFactory.create_task()

# Task with specific type
task = TaskFactory.create_task(task_type="implementation")

# Task chain (with dependencies)
tasks = TaskFactory.create_task_chain(num_tasks=4)
# Results in: task-1 -> task-2 -> task-3 -> task-4

# Parallel tasks (no dependencies)
tasks = TaskFactory.create_parallel_tasks(num_tasks=3)
```

### RuleFactory

Create rule configurations for testing.

```python
# Basic rule
rule = RuleFactory.create_rule()

# Custom rule
rule = RuleFactory.create_rule(
    id="custom-rule",
    name="Custom Rule"
)
```

### SkillFactory

Create skill configurations for testing.

```python
# Basic skill
skill = SkillFactory.create_skill()

# Custom skill
skill = SkillFactory.create_skill(
    id="custom-skill",
    name="Custom Skill"
)
```

## Mock Data Generator

Generate random test data for property-based testing or when you need varied test data.

```python
from tests.fixtures import MockDataGenerator

# Random strings
random_str = MockDataGenerator.random_string(length=10)
random_str_with_prefix = MockDataGenerator.random_string(length=8, prefix="test-")

# Random IDs
random_id = MockDataGenerator.random_id(prefix="workflow")

# Random version
version = MockDataGenerator.random_version()  # e.g., "2.5.13"

# Random timestamp
timestamp = MockDataGenerator.random_timestamp()

# Random workflow
workflow = MockDataGenerator.random_workflow()

# Random agent
agent = MockDataGenerator.random_agent()

# Random config
config = MockDataGenerator.random_config()

# Random task
task = MockDataGenerator.random_task()

# Random API responses
success_response = MockDataGenerator.random_api_response(success=True)
error_response = MockDataGenerator.random_api_response(success=False)
```

## Mock Data Constants

Pre-defined test data for common scenarios.

### Valid Data

```python
from tests.fixtures import (
    SAMPLE_WORKFLOW,
    SAMPLE_AGENT,
    SAMPLE_TASK,
    SAMPLE_CONFIG,
    COMPLEX_WORKFLOW,
    AGENT_POOL
)

# Use in tests
def test_workflow_processing():
    result = process_workflow(SAMPLE_WORKFLOW)
    assert result.is_valid
```

### Environment Configs

```python
from tests.fixtures import (
    DEVELOPMENT_CONFIG,
    PRODUCTION_CONFIG,
    TEST_CONFIG
)

def test_config_loading():
    config = load_config(DEVELOPMENT_CONFIG)
    assert config["core"]["environment"] == "development"
```

### Invalid Data (for validation testing)

```python
from tests.fixtures import (
    INVALID_WORKFLOW_MISSING_NAME,
    INVALID_WORKFLOW_MISSING_VERSION,
    INVALID_WORKFLOW_WRONG_TYPE,
    INVALID_AGENT_MISSING_ID,
    INVALID_AGENT_WRONG_TYPE
)

def test_workflow_validation():
    with pytest.raises(ValidationError):
        validate_workflow(INVALID_WORKFLOW_MISSING_NAME)
```

### Edge Cases

```python
from tests.fixtures import (
    MINIMAL_WORKFLOW,
    EMPTY_WORKFLOW,
    WORKFLOW_WITH_CIRCULAR_DEPS,
    LARGE_WORKFLOW
)

def test_minimal_workflow():
    result = process_workflow(MINIMAL_WORKFLOW)
    assert result.is_valid

def test_circular_dependency_detection():
    with pytest.raises(CircularDependencyError):
        validate_workflow(WORKFLOW_WITH_CIRCULAR_DEPS)
```

## Best Practices

### 1. Use Factories for Test Data Creation

Instead of manually creating dictionaries in each test:

```python
# ❌ Don't do this
def test_workflow():
    workflow = {
        "name": "test",
        "version": "1.0.0",
        "agents": [],
        "tasks": []
    }
    # ...

# ✅ Do this
def test_workflow():
    workflow = WorkflowFactory.create_basic_workflow()
    # ...
```

### 2. Use Overrides for Test-Specific Values

```python
def test_workflow_timeout():
    workflow = WorkflowFactory.create_basic_workflow(timeout=1800)
    assert workflow["timeout"] == 1800
```

### 3. Use Mock Data Constants for Common Scenarios

```python
from tests.fixtures import SAMPLE_WORKFLOW, COMPLEX_WORKFLOW

def test_simple_workflow():
    result = process_workflow(SAMPLE_WORKFLOW)
    # ...

def test_complex_workflow():
    result = process_workflow(COMPLEX_WORKFLOW)
    # ...
```

### 4. Use MockDataGenerator for Property-Based Tests

```python
from hypothesis import given, strategies as st
from tests.fixtures import MockDataGenerator

@given(st.integers(min_value=1, max_value=10))
def test_workflow_with_random_tasks(num_tasks):
    workflow = MockDataGenerator.random_workflow()
    # Property test logic
```

### 5. Combine Factories for Integration Tests

```python
def test_complete_workflow_system():
    # Create agents
    agents = AgentFactory.create_agent_pool(num_agents=3)
    agent_ids = [agent["id"] for agent in agents]
    
    # Create tasks
    tasks = TaskFactory.create_task_chain(num_tasks=4)
    
    # Create workflow
    workflow = WorkflowFactory.create_basic_workflow(
        agents=agent_ids,
        tasks=tasks
    )
    
    # Test the complete system
    result = execute_workflow(workflow)
    assert result.is_successful
```

## Adding New Factories

When adding new factories, follow this pattern:

```python
class NewEntityFactory:
    """Factory for creating test NewEntity configurations."""
    
    @staticmethod
    def create_basic(**overrides) -> Dict[str, Any]:
        """Create a basic entity with optional overrides.
        
        Args:
            **overrides: Key-value pairs to override default values
            
        Returns:
            Dict containing entity configuration
        """
        entity = {
            "id": "test-entity",
            "name": "Test Entity",
            # ... other default fields
        }
        entity.update(overrides)
        return entity
```

## Testing the Fixtures

The fixtures themselves are tested in `tests/unit/test_fixtures_factories.py`. Run these tests to verify all factories work correctly:

```bash
pytest tests/unit/test_fixtures_factories.py -v
```

## Related Documentation

- [Test Structure Documentation](../README.md)
- [Testing Guidelines](../../docs/TESTING.md)
- [Configuration Guide](../../docs/CONFIGURATION.md)
