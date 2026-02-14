"""
Unit tests for dependency installation verification

This test verifies that the project's dependency configuration is valid
and that all core imports work after installation.

Requirements: 1.5
Task: 1.4
"""

import subprocess
import sys
import pytest
import importlib
import os
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent


class TestDependencyConfiguration:
    """Test that dependency configuration files exist and are valid"""

    def test_pyproject_toml_exists(self):
        """Test that pyproject.toml exists"""
        assert (PROJECT_ROOT / 'pyproject.toml').exists(), "pyproject.toml should exist"

    def test_pyproject_toml_valid(self):
        """Test that pyproject.toml has valid syntax"""
        try:
            if sys.version_info >= (3, 11):
                import tomllib
            else:
                import tomli as tomllib
        except ImportError:
            pytest.skip("tomllib/tomli not available")

        with open(PROJECT_ROOT / 'pyproject.toml', 'rb') as f:
            data = tomllib.load(f)

        assert 'project' in data, "pyproject.toml should have [project] section"
        assert 'name' in data['project'], "pyproject.toml should specify project name"

    def test_pyproject_has_dependencies(self):
        """Test that pyproject.toml specifies dependencies"""
        try:
            if sys.version_info >= (3, 11):
                import tomllib
            else:
                import tomli as tomllib
        except ImportError:
            pytest.skip("tomllib/tomli not available")

        with open(PROJECT_ROOT / 'pyproject.toml', 'rb') as f:
            data = tomllib.load(f)

        assert 'dependencies' in data.get('project', {}), \
            "pyproject.toml should specify dependencies"


class TestCoreImports:
    """Test that core dependencies can be imported"""

    def test_import_click(self):
        """Test that click can be imported"""
        import click
        assert click is not None

    def test_import_rich(self):
        """Test that rich can be imported"""
        import rich
        assert rich is not None

    def test_import_dotenv(self):
        """Test that python-dotenv can be imported"""
        import dotenv
        assert dotenv is not None

    def test_import_yaml(self):
        """Test that PyYAML can be imported"""
        import yaml
        assert yaml is not None

    def test_import_pydantic(self):
        """Test that pydantic can be imported"""
        import pydantic
        assert pydantic is not None

    def test_import_requests(self):
        """Test that requests can be imported"""
        import requests
        assert requests is not None

    def test_import_aiohttp(self):
        """Test that aiohttp can be imported"""
        import aiohttp
        assert aiohttp is not None

    def test_import_jinja2(self):
        """Test that jinja2 can be imported"""
        import jinja2
        assert jinja2 is not None


class TestDevImports:
    """Test that development dependencies can be imported"""

    def test_import_pytest(self):
        """Test that pytest can be imported"""
        import pytest
        assert pytest is not None

    def test_import_pytest_cov(self):
        """Test that pytest-cov can be imported"""
        import pytest_cov
        assert pytest_cov is not None

    def test_import_pytest_asyncio(self):
        """Test that pytest-asyncio can be imported"""
        try:
            import pytest_asyncio
            assert pytest_asyncio is not None
        except ImportError:
            pytest.skip("pytest-asyncio not available")

    def test_import_hypothesis(self):
        """Test that hypothesis can be imported"""
        import hypothesis
        assert hypothesis is not None

    def test_import_coverage(self):
        """Test that coverage can be imported"""
        import coverage
        assert coverage is not None


class TestProjectImports:
    """Test that project modules can be imported after dependency installation"""

    def test_import_agentic_sdlc(self):
        """Test that agentic_sdlc package can be imported"""
        import agentic_sdlc
        assert agentic_sdlc is not None

    def test_import_agentic_sdlc_core(self):
        """Test that agentic_sdlc.core can be imported"""
        import agentic_sdlc.core
        assert agentic_sdlc.core is not None

    def test_import_agentic_sdlc_infrastructure(self):
        """Test that agentic_sdlc.infrastructure can be imported"""
        import agentic_sdlc.infrastructure
        assert agentic_sdlc.infrastructure is not None

    def test_import_agentic_sdlc_intelligence(self):
        """Test that agentic_sdlc.intelligence can be imported"""
        import agentic_sdlc.intelligence
        assert agentic_sdlc.intelligence is not None
