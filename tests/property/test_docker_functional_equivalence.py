"""
Property-based tests for Docker Functional Equivalence.

These tests verify that the SDLC Kit functions identically when run in a Docker
container versus a local installation, ensuring consistent behavior across
deployment environments.

Feature: sdlc-kit-improvements
Property 15: Docker Functional Equivalence
Requirements: 15.6
"""

import pytest
import subprocess
import tempfile
import json
import os
from pathlib import Path
from hypothesis import given, strategies as st, settings, assume
from typing import Dict, Any, List


# Strategy for generating test commands that should work in both environments
test_commands = st.sampled_from([
    ["python", "-c", "import agentic_sdlc; print('success')"],
    ["python", "-c", "from agentic_sdlc.core import config; print('success')"],
    ["python", "-c", "from agentic_sdlc.orchestration import agents; print('success')"],
    ["python", "-c", "from agentic_sdlc.infrastructure import engine; print('success')"],
    ["python", "-c", "from agentic_sdlc.intelligence import reasoner; print('success')"],
    ["asdlc", "--help"],
    ["asdlc", "--version"],
])


def run_command_locally(command: List[str]) -> Dict[str, Any]:
    """
    Run a command in the local environment and capture results.
    
    Args:
        command: Command to execute as a list of strings
        
    Returns:
        Dictionary with exit_code, stdout, stderr, and success flag
    """
    try:
        result = subprocess.run(
            command,
            capture_output=True,
            text=True,
            timeout=30,
            cwd=Path.cwd()
        )
        return {
            "exit_code": result.returncode,
            "stdout": result.stdout.strip(),
            "stderr": result.stderr.strip(),
            "success": result.returncode == 0
        }
    except subprocess.TimeoutExpired:
        return {
            "exit_code": -1,
            "stdout": "",
            "stderr": "Command timed out",
            "success": False
        }
    except Exception as e:
        return {
            "exit_code": -1,
            "stdout": "",
            "stderr": str(e),
            "success": False
        }


def run_command_in_docker(command: List[str], image: str = "sdlc-kit:latest") -> Dict[str, Any]:
    """
    Run a command in a Docker container and capture results.
    
    Args:
        command: Command to execute as a list of strings
        image: Docker image to use
        
    Returns:
        Dictionary with exit_code, stdout, stderr, and success flag
    """
    # Check if Docker image exists
    check_image = subprocess.run(
        ["docker", "images", "-q", image],
        capture_output=True,
        text=True
    )
    
    if not check_image.stdout.strip():
        # Image doesn't exist, skip this test
        return {
            "exit_code": -2,
            "stdout": "",
            "stderr": f"Docker image {image} not found",
            "success": False,
            "skipped": True
        }
    
    try:
        # Run command in Docker container
        docker_command = [
            "docker", "run", "--rm",
            "-e", "PYTHONPATH=/app",
            image
        ] + command
        
        result = subprocess.run(
            docker_command,
            capture_output=True,
            text=True,
            timeout=60  # Docker commands may take longer
        )
        
        return {
            "exit_code": result.returncode,
            "stdout": result.stdout.strip(),
            "stderr": result.stderr.strip(),
            "success": result.returncode == 0,
            "skipped": False
        }
    except subprocess.TimeoutExpired:
        return {
            "exit_code": -1,
            "stdout": "",
            "stderr": "Docker command timed out",
            "success": False,
            "skipped": False
        }
    except Exception as e:
        return {
            "exit_code": -1,
            "stdout": "",
            "stderr": str(e),
            "success": False,
            "skipped": False
        }


def is_docker_available() -> bool:
    """Check if Docker is available on the system."""
    try:
        result = subprocess.run(
            ["docker", "--version"],
            capture_output=True,
            timeout=5
        )
        return result.returncode == 0
    except (subprocess.TimeoutExpired, FileNotFoundError):
        return False


def is_docker_image_built() -> bool:
    """Check if the SDLC Kit Docker image is built."""
    try:
        result = subprocess.run(
            ["docker", "images", "-q", "sdlc-kit:latest"],
            capture_output=True,
            text=True,
            timeout=5
        )
        return bool(result.stdout.strip())
    except (subprocess.TimeoutExpired, FileNotFoundError):
        return False


# Feature: sdlc-kit-improvements, Property 15: Docker Functional Equivalence
@pytest.mark.skipif(not is_docker_available(), reason="Docker not available")
@pytest.mark.skipif(not is_docker_image_built(), reason="Docker image not built")
@given(command=test_commands)
@settings(max_examples=5, deadline=None)
def test_command_execution_equivalence(command):
    """
    Property: For any command that executes successfully in the local environment,
    when run in a Docker container, it should produce the same exit code and
    similar output, ensuring functional equivalence.
    
    This property ensures that the Docker container provides the same functionality
    as a local installation, with all dependencies and imports working correctly.
    
    **Validates: Requirements 15.6**
    """
    # Run command locally
    local_result = run_command_locally(command)
    
    # Run command in Docker
    docker_result = run_command_in_docker(command)
    
    # Skip if Docker image not available
    if docker_result.get("skipped", False):
        pytest.skip("Docker image not available")
    
    # Property: Exit codes should match
    assert local_result["exit_code"] == docker_result["exit_code"], (
        f"Exit codes differ for command {' '.join(command)}. "
        f"Local: {local_result['exit_code']}, Docker: {docker_result['exit_code']}. "
        f"Local stderr: {local_result['stderr']}, Docker stderr: {docker_result['stderr']}"
    )
    
    # Property: Success status should match
    assert local_result["success"] == docker_result["success"], (
        f"Success status differs for command {' '.join(command)}. "
        f"Local: {local_result['success']}, Docker: {docker_result['success']}"
    )
    
    # Property: If successful, both should produce output
    if local_result["success"]:
        assert docker_result["success"], (
            f"Command succeeded locally but failed in Docker: {' '.join(command)}. "
            f"Docker stderr: {docker_result['stderr']}"
        )


# Feature: sdlc-kit-improvements, Property 15: Docker Functional Equivalence
@pytest.mark.skipif(not is_docker_available(), reason="Docker not available")
@pytest.mark.skipif(not is_docker_image_built(), reason="Docker image not built")
@given(
    module_name=st.sampled_from([
        "agentic_sdlc",
        "agentic_sdlc.core",
        "agentic_sdlc.infrastructure",
        "agentic_sdlc.intelligence",
        "agentic_sdlc.orchestration",
        "agentic_sdlc.plugins",
        "agentic_sdlc.documentation",
        "agentic_sdlc.core.config",
        "agentic_sdlc.core.exceptions",
        "agentic_sdlc.core.logging",
    ])
)
@settings(max_examples=5, deadline=None)
def test_import_equivalence(module_name):
    """
    Property: For any Python module in the SDLC Kit, when imported in a Docker
    container versus locally, both imports should succeed or fail identically.
    
    This ensures that all dependencies are correctly installed in the Docker
    image and the Python path is configured correctly.
    
    **Validates: Requirements 15.6**
    """
    # Test import locally
    local_command = ["python", "-c", f"import {module_name}; print('success')"]
    local_result = run_command_locally(local_command)
    
    # Test import in Docker
    docker_result = run_command_in_docker(local_command)
    
    # Skip if Docker image not available
    if docker_result.get("skipped", False):
        pytest.skip("Docker image not available")
    
    # Property: Import success should match
    assert local_result["success"] == docker_result["success"], (
        f"Import of {module_name} differs between environments. "
        f"Local success: {local_result['success']}, Docker success: {docker_result['success']}. "
        f"Local stderr: {local_result['stderr']}, Docker stderr: {docker_result['stderr']}"
    )
    
    # Property: If import succeeds locally, it should succeed in Docker
    if local_result["success"]:
        assert docker_result["success"], (
            f"Module {module_name} imports locally but fails in Docker. "
            f"Docker stderr: {docker_result['stderr']}"
        )


# Feature: sdlc-kit-improvements, Property 15: Docker Functional Equivalence
@pytest.mark.skipif(not is_docker_available(), reason="Docker not available")
@pytest.mark.skipif(not is_docker_image_built(), reason="Docker image not built")
def test_pytest_execution_equivalence():
    """
    Property: When running a subset of the test suite in Docker versus locally,
    the test results (pass/fail counts) should be identical, ensuring that
    the testing environment is consistent.
    
    This property validates that the Docker container can run tests with the
    same results as a local installation.
    
    **Validates: Requirements 15.6**
    """
    # Run a simple unit test locally
    local_command = [
        "pytest",
        "tests/unit/test_dependency_installation.py",
        "-v",
        "--tb=short",
        "-x"  # Stop on first failure
    ]
    local_result = run_command_locally(local_command)
    
    # Check if pytest is available in Docker
    pytest_check = run_command_in_docker(["pytest", "--version"])
    if pytest_check.get("exit_code") == 127:
        pytest.skip("pytest not available in Docker image")
    
    # Run the same test in Docker
    docker_result = run_command_in_docker(local_command)
    
    # Skip if Docker image not available
    if docker_result.get("skipped", False):
        pytest.skip("Docker image not available")
    
    # Property: Test execution should succeed in both environments
    # (or fail in both if there are actual test failures)
    assert local_result["exit_code"] == docker_result["exit_code"], (
        f"Test execution exit codes differ. "
        f"Local: {local_result['exit_code']}, Docker: {docker_result['exit_code']}. "
        f"Local output: {local_result['stdout']}, Docker output: {docker_result['stdout']}"
    )


# Feature: sdlc-kit-improvements, Property 15: Docker Functional Equivalence
@pytest.mark.skipif(not is_docker_available(), reason="Docker not available")
@pytest.mark.skipif(not is_docker_image_built(), reason="Docker image not built")
@given(
    config_type=st.sampled_from(["workflow", "agent", "rule"])
)
@settings(max_examples=5, deadline=None)
def test_config_validation_equivalence(config_type):
    """
    Property: For any configuration validation operation, when performed in
    Docker versus locally, the validation results should be identical.
    
    This ensures that configuration validation works consistently across
    deployment environments.
    
    **Validates: Requirements 15.6**
    """
    # Create a simple validation test
    validation_code = f"""
from config.validators import ConfigValidator
from pathlib import Path

validator = ConfigValidator()
schema_path = Path("config/schemas/{config_type}.schema.json")
schema = validator.load_schema(schema_path)
print(f"Schema loaded: {{bool(schema)}}")
"""
    
    # Test locally
    local_command = ["python", "-c", validation_code]
    local_result = run_command_locally(local_command)
    
    # Test in Docker
    docker_result = run_command_in_docker(local_command)
    
    # Skip if Docker image not available
    if docker_result.get("skipped", False):
        pytest.skip("Docker image not available")
    
    # Property: Validation should work in both environments
    assert local_result["success"] == docker_result["success"], (
        f"Config validation for {config_type} differs between environments. "
        f"Local success: {local_result['success']}, Docker success: {docker_result['success']}. "
        f"Local stderr: {local_result['stderr']}, Docker stderr: {docker_result['stderr']}"
    )
    
    # Property: Output should be similar
    if local_result["success"] and docker_result["success"]:
        assert local_result["stdout"] == docker_result["stdout"], (
            f"Config validation output differs for {config_type}. "
            f"Local: {local_result['stdout']}, Docker: {docker_result['stdout']}"
        )


# Feature: sdlc-kit-improvements, Property 15: Docker Functional Equivalence
@pytest.mark.skipif(not is_docker_available(), reason="Docker not available")
@pytest.mark.skipif(not is_docker_image_built(), reason="Docker image not built")
def test_cli_help_equivalence():
    """
    Property: The CLI help output should be identical when run in Docker
    versus locally, ensuring that the CLI is properly configured in both
    environments.
    
    **Validates: Requirements 15.6**
    """
    # Test CLI help locally
    local_result = run_command_locally(["asdlc", "--help"])
    
    # Test CLI help in Docker
    docker_result = run_command_in_docker(["asdlc", "--help"])
    
    # Skip if Docker image not available
    if docker_result.get("skipped", False):
        pytest.skip("Docker image not available")
    
    # Property: Both should succeed
    assert local_result["success"], f"CLI help failed locally: {local_result['stderr']}"
    assert docker_result["success"], f"CLI help failed in Docker: {docker_result['stderr']}"
    
    # Property: Help output should be identical (or very similar)
    # We check for key sections that should be present in both
    local_help = local_result["stdout"].lower()
    docker_help = docker_result["stdout"].lower()
    
    key_sections = ["usage", "options", "commands"]
    for section in key_sections:
        assert section in local_help, f"Local help missing '{section}' section"
        assert section in docker_help, f"Docker help missing '{section}' section"


# Feature: sdlc-kit-improvements, Property 15: Docker Functional Equivalence
@pytest.mark.skipif(not is_docker_available(), reason="Docker not available")
@pytest.mark.skipif(not is_docker_image_built(), reason="Docker image not built")
def test_python_version_equivalence():
    """
    Property: The Python version in the Docker container should match or be
    compatible with the local Python version (both should be 3.9+).
    
    **Validates: Requirements 15.6**
    """
    # Get local Python version
    local_command = ["python", "--version"]
    local_result = run_command_locally(local_command)
    
    # Get Docker Python version
    docker_result = run_command_in_docker(local_command)
    
    # Skip if Docker image not available
    if docker_result.get("skipped", False):
        pytest.skip("Docker image not available")
    
    # Property: Both should report Python version successfully
    assert local_result["success"], f"Failed to get local Python version: {local_result['stderr']}"
    assert docker_result["success"], f"Failed to get Docker Python version: {docker_result['stderr']}"
    
    # Extract version numbers
    local_version = local_result["stdout"]
    docker_version = docker_result["stdout"]
    
    # Property: Both should be Python 3.9+
    assert "Python 3." in local_version, f"Unexpected local Python version: {local_version}"
    assert "Python 3." in docker_version, f"Unexpected Docker Python version: {docker_version}"
    
    # Extract major.minor version
    import re
    local_match = re.search(r'Python (\d+)\.(\d+)', local_version)
    docker_match = re.search(r'Python (\d+)\.(\d+)', docker_version)
    
    if local_match and docker_match:
        local_major, local_minor = int(local_match.group(1)), int(local_match.group(2))
        docker_major, docker_minor = int(docker_match.group(1)), int(docker_match.group(2))
        
        # Both should be Python 3.9+
        assert local_major == 3 and local_minor >= 9, (
            f"Local Python version {local_major}.{local_minor} is below 3.9"
        )
        assert docker_major == 3 and docker_minor >= 9, (
            f"Docker Python version {docker_major}.{docker_minor} is below 3.9"
        )


# Feature: sdlc-kit-improvements, Property 15: Docker Functional Equivalence
@pytest.mark.skipif(not is_docker_available(), reason="Docker not available")
@pytest.mark.skipif(not is_docker_image_built(), reason="Docker image not built")
@given(
    dependency=st.sampled_from([
        "click",
        "yaml",
        "pydantic",
        "openai",
        "anthropic",
        "google.generativeai",
        "torch",
        "transformers",
        "numpy",
        "pandas",
        "sqlalchemy",
        "neo4j",
        "PIL",
        "jsonschema",
        "cryptography",
        "psutil",
        "requests",
        "aiohttp",
    ])
)
@settings(max_examples=5, deadline=None)
def test_dependency_availability_equivalence(dependency):
    """
    Property: For any core dependency, it should be available in both the
    local environment and the Docker container.
    
    This ensures that all required dependencies are properly installed in
    the Docker image.
    
    **Validates: Requirements 15.6**
    """
    # Test dependency locally
    local_command = ["python", "-c", f"import {dependency}; print('success')"]
    local_result = run_command_locally(local_command)
    
    # Test dependency in Docker
    docker_result = run_command_in_docker(local_command)
    
    # Skip if Docker image not available
    if docker_result.get("skipped", False):
        pytest.skip("Docker image not available")
    
    # Property: Dependency availability should match
    assert local_result["success"] == docker_result["success"], (
        f"Dependency {dependency} availability differs. "
        f"Local: {local_result['success']}, Docker: {docker_result['success']}. "
        f"Local stderr: {local_result['stderr']}, Docker stderr: {docker_result['stderr']}"
    )
    
    # Property: If available locally, should be available in Docker
    if local_result["success"]:
        assert docker_result["success"], (
            f"Dependency {dependency} available locally but not in Docker. "
            f"Docker stderr: {docker_result['stderr']}"
        )
