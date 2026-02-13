# Agentic SDLC - Test Suite

This directory contains all tests for the SDLC Kit project.

## Directory Structure

The tests are organized into the following categories:

### `unit/`
Unit tests for individual functions, classes, and modules. The directory structure mirrors the source code structure in `agentic_sdlc/` for easy navigation.

- `unit/core/` - Tests for core functionality (brain, CLI, utils)
- `unit/infrastructure/` - Tests for infrastructure components (automation, bridge, engine, lifecycle)
- `unit/intelligence/` - Tests for intelligence modules (collaborating, learning, monitoring, reasoning)
- `unit/orchestration/` - Tests for orchestration components (agents, API management, CLI, config, engine, etc.)

### `integration/`
Integration tests that verify interactions between multiple components.

### `e2e/`
End-to-end tests that validate complete workflow scenarios from start to finish.

- `e2e/workflow_scenarios/` - Complete workflow execution tests

### `fixtures/`
Reusable test data, mock objects, and factory functions.

- `fixtures/factories.py` - Factory functions for creating test objects (WorkflowFactory, AgentFactory, etc.)
- `fixtures/mock_data.py` - Sample data for testing

### `property/`
Property-based tests using Hypothesis that validate universal properties across all valid inputs.

### Legacy Test Directories
- `layer1/` - Legacy layer 1 tests (rules, skills, workflows, worktree)
- `layer2/` - Legacy layer 2 tests (autogen, brain, learning, neo4j)
- `layer3/` - Legacy layer 3 tests (CLI, tools, workflows e2e)

## Running Tests

```bash
# Install test dependencies
pip install pytest pytest-cov hypothesis

# Run all tests
pytest

# Run with coverage
pytest --cov=agentic_sdlc --cov-report=html

# Run specific test categories
pytest tests/unit/          # Unit tests only
pytest tests/integration/   # Integration tests only
pytest tests/e2e/          # End-to-end tests only
pytest tests/property/     # Property-based tests only

# Run tests for a specific module
pytest tests/unit/core/     # All core unit tests
pytest tests/unit/orchestration/agents/  # Agent-specific tests

# Run specific test file
pytest tests/test_kb_manager.py
```

## Test Configuration

Test configuration is managed in:
- `conftest.py` - Pytest fixtures and configuration
- `pytest.ini` - Pytest settings (in project root)

## Writing Tests

Follow these conventions:
- Test files: `test_*.py`
- Test classes: `Test*`
- Test functions: `test_*`

### Unit Tests
- Test individual functions and classes in isolation
- Use descriptive test names: `test_<function>_<scenario>_<expected_result>`
- Mock external dependencies
- Keep tests focused and fast

Example:
```python
def test_get_project_root():
    from agentic_sdlc.utils.common import get_project_root
    root = get_project_root()
    assert root.exists()
    assert (root / '.agent').exists()
```

### Integration Tests
- Test interactions between components
- Use real implementations where possible
- Test error handling and edge cases

### End-to-End Tests
- Test complete workflows
- Validate system behavior from user perspective
- Use realistic test data

### Property-Based Tests
- Define universal properties that should hold for all inputs
- Use Hypothesis strategies to generate test data
- Reference design document properties in test docstrings
- Minimum 100 iterations per property test

Example:
```python
from hypothesis import given, strategies as st

@given(st.text(min_size=1))
def test_property_example(input_text):
    """Property: Function should handle all non-empty strings."""
    result = process_text(input_text)
    assert result is not None
```

## Using Test Fixtures

The `fixtures/` directory provides factory functions for creating test objects:

```python
from tests.fixtures.factories import WorkflowFactory, AgentFactory

def test_workflow_creation():
    # Create a basic workflow
    workflow = WorkflowFactory.create_basic_workflow()
    assert workflow["name"] == "test-workflow"
    
    # Create with overrides
    custom_workflow = WorkflowFactory.create_basic_workflow(
        name="custom-workflow",
        timeout=7200
    )
    assert custom_workflow["name"] == "custom-workflow"
    assert custom_workflow["timeout"] == 7200
```
