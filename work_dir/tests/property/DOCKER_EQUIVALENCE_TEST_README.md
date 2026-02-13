# Docker Functional Equivalence Property Tests

## Overview

This document describes the property-based tests for Docker functional equivalence (Property 15) in the SDLC Kit improvements specification.

## Property Definition

**Property 15: Docker Functional Equivalence**

*For any* test in the test suite, when run in a Docker container versus a local installation, the test results should be identical.

**Validates: Requirements 15.6**

## Test Implementation

The property tests are implemented in `test_docker_functional_equivalence.py` and verify that:

1. **Command Execution Equivalence**: Commands that work locally produce the same results in Docker
2. **Import Equivalence**: Python module imports work identically in both environments
3. **Test Execution Equivalence**: pytest runs produce the same results
4. **Configuration Validation Equivalence**: Config validation works consistently
5. **CLI Help Equivalence**: CLI commands produce identical output
6. **Python Version Equivalence**: Both environments use compatible Python versions (3.9+)
7. **Dependency Availability Equivalence**: All required dependencies are available in both environments

## Test Strategy

The tests use Hypothesis to generate various test scenarios and compare:
- Exit codes
- Success/failure status
- Output content
- Error messages

## Running the Tests

### Prerequisites

1. **Docker must be installed and running**
   ```bash
   docker --version
   ```

2. **Docker image must be built**
   ```bash
   docker build -t sdlc-kit:latest -f Dockerfile .
   ```

### Execute Tests

```bash
# Run all Docker equivalence property tests
pytest tests/property/test_docker_functional_equivalence.py -v

# Run with more examples (default is limited by hypothesis profile)
pytest tests/property/test_docker_functional_equivalence.py -v --hypothesis-profile=default

# Run specific test
pytest tests/property/test_docker_functional_equivalence.py::test_import_equivalence -v
```

## Test Behavior

### When Docker is Not Available

Tests will be **skipped** with the message:
```
SKIPPED [reason: Docker not available]
```

### When Docker Image is Not Built

Tests will be **skipped** with the message:
```
SKIPPED [reason: Docker image not built]
```

### When Tests Run Successfully

Tests will verify that:
- Commands execute with the same exit codes
- Imports succeed or fail identically
- Output is consistent between environments
- All dependencies are available

## Known Issues

### Platform-Specific Dependencies

The current `requirements.txt` includes platform-specific dependencies (e.g., `mlx-metal` for macOS) that prevent the Docker image from building on Linux-based Docker containers.

**Solution**: The requirements.txt should be updated to use platform-specific dependency specifications:

```python
# requirements.txt
mlx-metal==0.30.4; sys_platform == 'darwin'
```

Or use separate requirements files:
- `requirements-base.txt` - Cross-platform dependencies
- `requirements-macos.txt` - macOS-specific dependencies
- `requirements-linux.txt` - Linux-specific dependencies

### Docker Build Context

The Docker build requires the entire project context, including:
- All source code
- Configuration files
- Schema definitions
- Requirements files

Ensure `.dockerignore` is properly configured to exclude unnecessary files.

## Test Coverage

The property tests cover:

| Test | Description | Validates |
|------|-------------|-----------|
| `test_command_execution_equivalence` | Basic command execution | Exit codes, success status |
| `test_import_equivalence` | Python module imports | Import success across environments |
| `test_pytest_execution_equivalence` | Test suite execution | Test results consistency |
| `test_config_validation_equivalence` | Configuration validation | Validation logic consistency |
| `test_cli_help_equivalence` | CLI help output | CLI configuration |
| `test_python_version_equivalence` | Python version compatibility | Version requirements (3.9+) |
| `test_dependency_availability_equivalence` | Dependency installation | All deps available |

## Maintenance

### Adding New Tests

To add new equivalence tests:

1. Define the test scenario (what should be equivalent)
2. Implement `run_command_locally()` execution
3. Implement `run_command_in_docker()` execution
4. Compare results and assert equivalence
5. Add appropriate skip conditions

### Updating Test Commands

The `test_commands` strategy can be extended with new commands:

```python
test_commands = st.sampled_from([
    ["python", "-c", "import new_module; print('success')"],
    ["asdlc", "new-command", "--help"],
    # Add more commands here
])
```

## Integration with CI/CD

These tests should be integrated into the CI/CD pipeline:

```yaml
# .github/workflows/docker-tests.yml
- name: Build Docker Image
  run: docker build -t sdlc-kit:latest .

- name: Run Docker Equivalence Tests
  run: pytest tests/property/test_docker_functional_equivalence.py -v
```

## References

- Design Document: `.kiro/specs/sdlc-kit-improvements/design.md`
- Requirements: `.kiro/specs/sdlc-kit-improvements/requirements.md`
- Task List: `.kiro/specs/sdlc-kit-improvements/tasks.md`
- Dockerfile: `Dockerfile`
- Docker Compose: `docker-compose.yml`
