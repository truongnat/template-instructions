"""
Shared test fixtures for Agentic SDLC tests.

This module provides pytest configuration and fixtures for the test suite.
It includes:
- Path fixtures for common directories
- Test data fixtures
- Configuration fixtures
- Temporary directory fixtures
"""

import pytest
import sys
import os
import tempfile
import shutil
import yaml
from pathlib import Path
from typing import Dict, Any

# Add project root and src to path
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT / "src"))
sys.path.insert(0, str(PROJECT_ROOT))

# Install compatibility shims for old import paths
from agentic_sdlc._compat import install_compatibility_shims
install_compatibility_shims()


# ============================================================================
# Pytest Configuration
# ============================================================================

def pytest_configure(config):
    """Configure pytest with custom markers and settings."""
    # Register custom markers
    config.addinivalue_line(
        "markers", "unit: Unit tests for individual components"
    )
    config.addinivalue_line(
        "markers", "integration: Integration tests for component interactions"
    )
    config.addinivalue_line(
        "markers", "e2e: End-to-end tests for complete workflows"
    )
    config.addinivalue_line(
        "markers", "property: Property-based tests using Hypothesis"
    )
    config.addinivalue_line(
        "markers", "slow: Tests that take significant time to run"
    )
    config.addinivalue_line(
        "markers", "requires_api: Tests that require external API access"
    )
    config.addinivalue_line(
        "markers", "requires_db: Tests that require database access"
    )


def pytest_collection_modifyitems(config, items):
    """Modify test collection to add markers based on test location."""
    for item in items:
        # Add markers based on test file location
        test_path = Path(item.fspath).relative_to(PROJECT_ROOT)
        
        if "unit" in test_path.parts:
            item.add_marker(pytest.mark.unit)
        elif "integration" in test_path.parts:
            item.add_marker(pytest.mark.integration)
        elif "e2e" in test_path.parts:
            item.add_marker(pytest.mark.e2e)
        elif "property" in test_path.parts:
            item.add_marker(pytest.mark.property)
        
        # Add slow marker for property tests (they run many iterations)
        if "property" in str(test_path) or "property_tests" in str(test_path):
            item.add_marker(pytest.mark.slow)


# ============================================================================
# Path Fixtures
# ============================================================================

@pytest.fixture
def project_root():
    """Return project root path."""
    return PROJECT_ROOT


@pytest.fixture
def agent_dir(project_root):
    """Return defaults directory path."""
    return project_root / "agentic_sdlc" / "defaults"


@pytest.fixture
def kb_dir(agent_dir):
    """Return knowledge-base directory path."""
    return agent_dir / "knowledge-base"


@pytest.fixture
def tools_dir(project_root):
    """Return agentic_sdlc directory path (formerly tools)."""
    return project_root / "src" / "agentic_sdlc"


@pytest.fixture
def tests_dir(project_root):
    """Return tests directory path."""
    return project_root / "tests"


@pytest.fixture
def fixtures_dir(tests_dir):
    """Return test fixtures directory path."""
    return tests_dir / "fixtures"


@pytest.fixture
def test_data_dir(fixtures_dir):
    """Return test data directory path."""
    return fixtures_dir


# ============================================================================
# Temporary Directory Fixtures
# ============================================================================

@pytest.fixture
def temp_dir():
    """Create a temporary directory for test use."""
    temp_path = Path(tempfile.mkdtemp())
    yield temp_path
    # Cleanup after test
    if temp_path.exists():
        shutil.rmtree(temp_path)


# Environment Fixtures
# ============================================================================

@pytest.fixture
def clean_env(monkeypatch):
    """Provide a clean environment without API keys or sensitive data."""
    # Remove sensitive environment variables
    sensitive_vars = [
        "OPENAI_API_KEY",
        "ANTHROPIC_API_KEY",
        "GOOGLE_API_KEY",
        "API_KEY",
        "SECRET_KEY"
    ]
    for var in sensitive_vars:
        monkeypatch.delenv(var, raising=False)
    return monkeypatch


@pytest.fixture
def test_env(monkeypatch):
    """Set up test environment variables."""
    monkeypatch.setenv("ENVIRONMENT", "test")
    monkeypatch.setenv("LOG_LEVEL", "DEBUG")
    monkeypatch.setenv("TEST_MODE", "true")
    return monkeypatch


# ============================================================================
# Hypothesis Configuration for Property-Based Testing
# ============================================================================

# Configure Hypothesis settings for property-based tests
from hypothesis import settings, Verbosity

# Register custom Hypothesis profile for CI/CD
# Reduced max_examples for faster test execution
settings.register_profile("ci", max_examples=20, verbosity=Verbosity.normal)
settings.register_profile("dev", max_examples=5, verbosity=Verbosity.normal)
settings.register_profile("thorough", max_examples=100, verbosity=Verbosity.verbose)
settings.register_profile("fast", max_examples=3, verbosity=Verbosity.quiet)

# Load profile from environment or use default (fast for quick iterations)
profile = os.getenv("HYPOTHESIS_PROFILE", "fast")
settings.load_profile(profile)