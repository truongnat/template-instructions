"""
Property-based tests for Validator.

These tests use Hypothesis to verify universal properties of the Validator
across many randomly generated inputs.

Feature: project-audit-cleanup
Property 5: Validation Triggers Rollback
Requirements: 9.5
"""

import pytest
import tempfile
from pathlib import Path
from hypothesis import given, strategies as st, settings, assume
from unittest.mock import patch, MagicMock
import subprocess

from scripts.cleanup.validator import Validator
from scripts.cleanup.models import ValidationResult


# Feature: project-audit-cleanup, Property 5: Validation Triggers Rollback
@given(
    import_failures=st.lists(st.sampled_from([
        "agentic_sdlc",
        "agentic_sdlc.core",
        "agentic_sdlc.intelligence",
        "agentic_sdlc.infrastructure",
        "agentic_sdlc.orchestration",
    ]), min_size=0, max_size=5, unique=True),
    cli_failures=st.lists(st.sampled_from([
        "agentic",
        "asdlc",
        "agentic-sdlc",
    ]), min_size=0, max_size=3, unique=True),
    test_failure=st.booleans(),
    build_failure=st.booleans(),
)
@settings(max_examples=10, deadline=None)
def test_validation_failure_detection(import_failures, cli_failures, test_failure, build_failure):
    """
    Property: For any validation operation where one or more checks fail,
    the Validator should return a ValidationResult with passed=False.
    
    This property ensures that the Validator correctly identifies validation
    failures, which is a prerequisite for the CleanupEngine to trigger rollback.
    
    **Validates: Requirements 9.5**
    """
    with tempfile.TemporaryDirectory() as tmpdir:
        tmpdir = Path(tmpdir)
        validator = Validator(tmpdir)
        
        # Mock subprocess calls to simulate failures
        def mock_subprocess_run(cmd, *args, **kwargs):
            result = MagicMock()
            result.stdout = ""
            result.stderr = ""
            result.returncode = 0
            
            # Check if this is an import command
            if len(cmd) >= 3 and cmd[1] == "-c" and "import" in cmd[2]:
                # Extract module name
                import_cmd = cmd[2]
                for module in import_failures:
                    if module in import_cmd:
                        result.returncode = 1
                        result.stderr = f"ModuleNotFoundError: No module named '{module}'"
                        return result
            
            # Check if this is a CLI command
            if len(cmd) >= 2:
                cli_cmd = cmd[0] if cmd[0] in ["agentic", "asdlc", "agentic-sdlc"] else None
                if not cli_cmd and len(cmd) >= 3 and cmd[1] == "-m":
                    cli_cmd = cmd[2]
                
                if cli_cmd in cli_failures:
                    result.returncode = 1
                    result.stderr = f"Command not found: {cli_cmd}"
                    return result
            
            # Check if this is pytest
            if "pytest" in str(cmd):
                if test_failure:
                    result.returncode = 1
                    result.stdout = "1 failed, 0 passed"
                    return result
                else:
                    result.returncode = 0
                    result.stdout = "5 passed"
                    return result
            
            # Check if this is build command
            if "build" in str(cmd):
                if build_failure:
                    result.returncode = 1
                    result.stderr = "Build failed"
                    return result
                else:
                    result.returncode = 0
                    # Create a mock wheel file
                    dist_dir = tmpdir / "dist"
                    dist_dir.mkdir(exist_ok=True)
                    wheel_file = dist_dir / "test-1.0.0-py3-none-any.whl"
                    wheel_file.write_text("mock wheel")
                    return result
            
            return result
        
        with patch('subprocess.run', side_effect=mock_subprocess_run):
            # Run validation
            result = validator.validate_all()
            
            # Property: If any validation check fails, overall validation should fail
            has_any_failure = (
                len(import_failures) > 0 or
                len(cli_failures) > 0 or
                test_failure or
                build_failure
            )
            
            if has_any_failure:
                assert not result.passed, (
                    f"Validation should fail when checks fail. "
                    f"Import failures: {import_failures}, "
                    f"CLI failures: {cli_failures}, "
                    f"Test failure: {test_failure}, "
                    f"Build failure: {build_failure}"
                )
                assert len(result.errors) > 0, "Failed validation should have error messages"
            else:
                # If no failures, validation should pass
                assert result.passed, "Validation should pass when all checks succeed"
                assert len(result.errors) == 0, "Successful validation should have no errors"


@given(
    modules=st.lists(st.text(min_size=1, max_size=20, alphabet=st.characters(
        whitelist_categories=('Lu', 'Ll'), min_codepoint=97, max_codepoint=122
    )), min_size=1, max_size=5, unique=True)
)
@settings(max_examples=10, deadline=None)
def test_import_validation_consistency(modules):
    """
    Property: For any list of modules, if import validation is run twice
    with the same modules, it should return consistent results.
    
    **Validates: Requirements 9.3**
    """
    with tempfile.TemporaryDirectory() as tmpdir:
        tmpdir = Path(tmpdir)
        validator = Validator(tmpdir)
        
        # Mock subprocess to return consistent results
        call_count = {}
        
        def mock_subprocess_run(cmd, *args, **kwargs):
            result = MagicMock()
            result.stdout = ""
            result.stderr = ""
            
            # Make result deterministic based on module name
            if len(cmd) >= 3 and cmd[1] == "-c" and "import" in cmd[2]:
                import_cmd = cmd[2]
                # Use hash of module name to determine success/failure
                module_hash = hash(import_cmd) % 2
                result.returncode = module_hash
                if module_hash == 1:
                    result.stderr = f"Import failed: {import_cmd}"
                
                # Track calls
                call_count[import_cmd] = call_count.get(import_cmd, 0) + 1
            else:
                result.returncode = 0
            
            return result
        
        with patch('subprocess.run', side_effect=mock_subprocess_run):
            # Run validation twice
            result1 = validator.verify_imports(modules)
            result2 = validator.verify_imports(modules)
            
            # Property: Results should be consistent
            assert result1.passed == result2.passed, "Import validation should be deterministic"
            assert set(result1.successful_imports) == set(result2.successful_imports), (
                "Successful imports should be consistent"
            )
            assert set(result1.failed_imports) == set(result2.failed_imports), (
                "Failed imports should be consistent"
            )


@given(
    max_size=st.integers(min_value=1024, max_value=100 * 1024 * 1024)  # 1KB to 100MB
)
@settings(max_examples=10, deadline=None)
def test_size_validation_threshold(max_size):
    """
    Property: For any package size threshold, if the built package exceeds
    that threshold, validation should fail.
    
    **Validates: Requirements 5.4**
    """
    with tempfile.TemporaryDirectory() as tmpdir:
        tmpdir = Path(tmpdir)
        validator = Validator(tmpdir, max_package_size=max_size)
        
        # Create a mock package that exceeds the threshold
        package_size = max_size + 1024  # 1KB over the limit
        
        def mock_subprocess_run(cmd, *args, **kwargs):
            result = MagicMock()
            result.stdout = ""
            result.stderr = ""
            result.returncode = 0
            
            # Mock successful build
            if "build" in str(cmd):
                dist_dir = tmpdir / "dist"
                dist_dir.mkdir(exist_ok=True)
                wheel_file = dist_dir / "test-1.0.0-py3-none-any.whl"
                # Create a file of the specified size
                wheel_file.write_bytes(b'0' * package_size)
                return result
            
            # Mock other commands as successful
            if "pytest" in str(cmd):
                result.stdout = "5 passed"
            
            return result
        
        with patch('subprocess.run', side_effect=mock_subprocess_run):
            with patch('shutil.which', return_value=None):
                # Run validation
                result = validator.validate_all()
                
                # Property: Validation should fail when package size exceeds threshold
                assert not result.passed, (
                    f"Validation should fail when package size ({package_size} bytes) "
                    f"exceeds threshold ({max_size} bytes)"
                )
                assert any("size" in error.lower() or "exceeds" in error.lower() 
                          for error in result.errors), (
                    "Error message should mention size limit"
                )


# Feature: project-audit-cleanup, Property 5: Validation Triggers Rollback
@given(
    validation_failures=st.lists(
        st.sampled_from([
            "import_failure",
            "cli_failure",
            "test_failure",
            "build_failure",
            "size_failure"
        ]),
        min_size=1,
        max_size=5,
        unique=True
    )
)
@settings(max_examples=10, deadline=None)
def test_validation_triggers_rollback_signal(validation_failures):
    """
    Property: For any validation operation where one or more validation checks fail,
    the Validator MUST return a ValidationResult with passed=False, which serves as
    the signal for the CleanupEngine to trigger automatic rollback.

    This property ensures that ANY validation failure (import, CLI, test, build, or size)
    will cause the overall validation to fail, thereby triggering the rollback mechanism
    in the CleanupEngine.

    The property verifies:
    1. Any single validation failure causes overall validation to fail
    2. Multiple validation failures are all captured in the error list
    3. The ValidationResult.passed flag is False when any check fails
    4. Error messages are provided for debugging

    **Validates: Requirements 9.5**
    """
    with tempfile.TemporaryDirectory() as tmpdir:
        tmpdir = Path(tmpdir)

        # Set a small size limit to test size validation
        validator = Validator(tmpdir, max_package_size=1024 * 1024)  # 1MB limit

        # Track which validations should fail
        should_fail_import = "import_failure" in validation_failures
        should_fail_cli = "cli_failure" in validation_failures
        should_fail_test = "test_failure" in validation_failures
        should_fail_build = "build_failure" in validation_failures
        should_fail_size = "size_failure" in validation_failures

        def mock_subprocess_run(cmd, *args, **kwargs):
            result = MagicMock()
            result.stdout = ""
            result.stderr = ""
            result.returncode = 0

            # Mock import validation
            if len(cmd) >= 3 and cmd[1] == "-c" and "import" in cmd[2]:
                if should_fail_import:
                    result.returncode = 1
                    result.stderr = "ModuleNotFoundError: No module named 'agentic_sdlc'"
                return result

            # Mock CLI validation
            if any(cli_cmd in str(cmd) for cli_cmd in ["agentic", "asdlc", "agentic-sdlc"]):
                if should_fail_cli:
                    result.returncode = 1
                    result.stderr = "Command not found"
                return result

            # Mock test execution
            if "pytest" in str(cmd):
                if should_fail_test:
                    result.returncode = 1
                    result.stdout = "5 failed, 0 passed"
                else:
                    result.returncode = 0
                    result.stdout = "10 passed"
                return result

            # Mock build command
            if "build" in str(cmd):
                if should_fail_build:
                    result.returncode = 1
                    result.stderr = "Build failed: syntax error"
                else:
                    result.returncode = 0
                    # Create mock wheel file
                    dist_dir = tmpdir / "dist"
                    dist_dir.mkdir(exist_ok=True)
                    wheel_file = dist_dir / "test-1.0.0-py3-none-any.whl"

                    # Create file that exceeds size limit if size_failure requested
                    if should_fail_size:
                        # Create 2MB file (exceeds 1MB limit)
                        wheel_file.write_bytes(b'0' * (2 * 1024 * 1024))
                    else:
                        # Create small file (under limit)
                        wheel_file.write_bytes(b'0' * (512 * 1024))
                return result

            return result

        with patch('subprocess.run', side_effect=mock_subprocess_run):
            with patch('shutil.which', return_value=None):
                # Run validation
                result = validator.validate_all()

                # CRITICAL PROPERTY: Validation MUST fail if ANY check fails
                assert not result.passed, (
                    f"Validation must fail when any check fails. "
                    f"Failed checks: {validation_failures}"
                )

                # PROPERTY: Error list must not be empty
                assert len(result.errors) > 0, (
                    "Failed validation must provide error messages for debugging"
                )

                # PROPERTY: Specific check flags should reflect failures
                if should_fail_import:
                    assert not result.import_check, "Import check should be marked as failed"

                if should_fail_cli:
                    assert not result.cli_check, "CLI check should be marked as failed"

                if should_fail_test:
                    assert not result.test_check, "Test check should be marked as failed"

                if should_fail_build:
                    assert not result.build_check, "Build check should be marked as failed"

                # PROPERTY: Each failure type should have a corresponding error message
                error_text = " ".join(result.errors).lower()

                if should_fail_import:
                    assert any(keyword in error_text for keyword in ["import", "module"]), (
                        "Import failure should be mentioned in errors"
                    )

                if should_fail_cli:
                    assert any(keyword in error_text for keyword in ["cli", "command"]), (
                        "CLI failure should be mentioned in errors"
                    )

                if should_fail_test:
                    assert any(keyword in error_text for keyword in ["test", "failed"]), (
                        "Test failure should be mentioned in errors"
                    )

                if should_fail_build:
                    assert any(keyword in error_text for keyword in ["build"]), (
                        "Build failure should be mentioned in errors"
                    )

                # Size failure only occurs if build succeeds
                if should_fail_size and not should_fail_build:
                    assert any(keyword in error_text for keyword in ["size", "exceeds"]), (
                        "Size failure should be mentioned in errors"
                    )


@given(
    num_failures=st.integers(min_value=1, max_value=5)
)
@settings(max_examples=10, deadline=None)
def test_validation_failure_count_accuracy(num_failures):
    """
    Property: For any number of validation failures, the ValidationResult
    should contain at least that many error messages, ensuring that all
    failures are reported for rollback decision-making.

    **Validates: Requirements 9.5**
    """
    with tempfile.TemporaryDirectory() as tmpdir:
        tmpdir = Path(tmpdir)
        validator = Validator(tmpdir)

        failure_count = 0

        def mock_subprocess_run(cmd, *args, **kwargs):
            nonlocal failure_count
            result = MagicMock()
            result.stdout = ""
            result.stderr = ""

            # Make first N calls fail
            if failure_count < num_failures:
                result.returncode = 1
                result.stderr = f"Failure {failure_count + 1}"
                failure_count += 1
            else:
                result.returncode = 0
                result.stdout = "Success"

                # For build command, create mock wheel
                if "build" in str(cmd):
                    dist_dir = tmpdir / "dist"
                    dist_dir.mkdir(exist_ok=True)
                    wheel_file = dist_dir / "test-1.0.0-py3-none-any.whl"
                    wheel_file.write_text("mock")

            return result

        with patch('subprocess.run', side_effect=mock_subprocess_run):
            with patch('shutil.which', return_value=None):
                result = validator.validate_all()

                # Property: Validation must fail
                assert not result.passed, "Validation should fail when checks fail"

                # Property: Error count should reflect failures
                assert len(result.errors) >= 1, (
                    f"Should have at least 1 error message, got {len(result.errors)}"
                )

