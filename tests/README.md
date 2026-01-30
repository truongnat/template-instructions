# Agentic SDLC - Test Suite

This directory contains tests for the Agentic SDLC tooling.

## Running Tests

```bash
# Install test dependencies
pip install pytest pytest-cov

# Run all tests
pytest

# Run with coverage
pytest --cov=tools --cov-report=html

# Run specific test file
pytest tests/test_kb_manager.py
```

## Test Structure

```
tests/
├── test_kb_manager.py    # Knowledge Base tests
├── test_common.py        # Common utilities tests
├── test_health_check.py  # Health check tests
└── conftest.py           # Shared test fixtures
```

## Writing Tests

Follow these conventions:
- Test files: `test_*.py`
- Test classes: `Test*`
- Test functions: `test_*`

Example:
```python
def test_get_project_root():
    from agentic_sdlc.utils.common import get_project_root
    root = get_project_root()
    assert root.exists()
    assert (root / '.agent').exists()
```
