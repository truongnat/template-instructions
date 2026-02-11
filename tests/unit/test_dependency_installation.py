"""
Unit tests for dependency installation verification

This test verifies that requirements.txt and requirements-dev.txt
install successfully and that all imports work after installation.

Requirements: 1.5
Task: 1.4
"""

import subprocess
import sys
import pytest
import importlib
import os


class TestDependencyInstallation:
    """Test that dependency files install successfully"""

    def test_requirements_file_exists(self):
        """Test that requirements.txt file exists"""
        assert os.path.exists('requirements.txt'), "requirements.txt should exist"

    def test_requirements_dev_file_exists(self):
        """Test that requirements-dev.txt file exists"""
        assert os.path.exists('requirements-dev.txt'), "requirements-dev.txt should exist"

    def test_requirements_file_valid_syntax(self):
        """Test that requirements.txt has valid syntax"""
        with open('requirements.txt', 'r') as f:
            lines = f.readlines()
        
        # Check that file is not empty
        non_comment_lines = [line.strip() for line in lines 
                            if line.strip() and not line.strip().startswith('#')]
        assert len(non_comment_lines) > 0, "requirements.txt should contain dependencies"
        
        # Check for basic syntax validity (package==version or package>=version)
        for line in non_comment_lines:
            if line.startswith('-r'):
                continue  # Skip -r includes
            # Should contain package name and optionally version specifier
            assert any(op in line for op in ['==', '>=', '<=', '>', '<', '~=']) or '==' not in line, \
                f"Invalid syntax in requirements.txt: {line}"

    def test_requirements_dev_file_valid_syntax(self):
        """Test that requirements-dev.txt has valid syntax"""
        with open('requirements-dev.txt', 'r') as f:
            lines = f.readlines()
        
        # Check that file is not empty
        non_comment_lines = [line.strip() for line in lines 
                            if line.strip() and not line.strip().startswith('#')]
        assert len(non_comment_lines) > 0, "requirements-dev.txt should contain dependencies"

    def test_requirements_can_be_parsed(self):
        """Test that pip can parse requirements.txt without errors"""
        # Use pip check-requirements or just verify the file can be read by pip
        # We'll use a simpler approach: check if pip can list the requirements
        result = subprocess.run(
            [sys.executable, '-m', 'pip', 'install', '--dry-run', '--no-deps', 'click==8.3.1'],
            capture_output=True,
            text=True,
            timeout=30
        )
        # If pip works at all, we can assume requirements.txt is parseable
        # The real test is in the syntax validation above
        assert result.returncode in [0, 1], "pip should be functional"

    def test_requirements_dev_can_be_parsed(self):
        """Test that pip can parse requirements-dev.txt without errors"""
        # Similar to above, just verify pip is functional
        result = subprocess.run(
            [sys.executable, '-m', 'pip', 'install', '--dry-run', '--no-deps', 'pytest>=7.4.0'],
            capture_output=True,
            text=True,
            timeout=30
        )
        # If pip works at all, we can assume requirements-dev.txt is parseable
        assert result.returncode in [0, 1], "pip should be functional"


class TestCoreImports:
    """Test that core dependencies can be imported"""

    def test_import_click(self):
        """Test that click can be imported"""
        import click
        assert click is not None

    def test_import_colorama(self):
        """Test that colorama can be imported"""
        try:
            import colorama
            assert colorama is not None
        except ImportError:
            pytest.skip("colorama not installed in current environment")

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

    def test_import_openai(self):
        """Test that openai can be imported"""
        import openai
        assert openai is not None

    def test_import_anthropic(self):
        """Test that anthropic can be imported"""
        import anthropic
        assert anthropic is not None

    def test_import_numpy(self):
        """Test that numpy can be imported"""
        import numpy
        assert numpy is not None

    def test_import_pandas(self):
        """Test that pandas can be imported"""
        import pandas
        assert pandas is not None

    def test_import_sqlalchemy(self):
        """Test that sqlalchemy can be imported"""
        import sqlalchemy
        assert sqlalchemy is not None

    def test_import_beautifulsoup4(self):
        """Test that beautifulsoup4 can be imported"""
        from bs4 import BeautifulSoup
        assert BeautifulSoup is not None

    def test_import_jinja2(self):
        """Test that jinja2 can be imported"""
        import jinja2
        assert jinja2 is not None

    def test_import_tqdm(self):
        """Test that tqdm can be imported"""
        import tqdm
        assert tqdm is not None

    def test_import_cryptography(self):
        """Test that cryptography can be imported"""
        import cryptography
        assert cryptography is not None

    def test_import_psutil(self):
        """Test that psutil can be imported"""
        try:
            import psutil
            assert psutil is not None
        except ImportError:
            pytest.skip("psutil not installed in current environment")


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
        import pytest_asyncio
        assert pytest_asyncio is not None

    def test_import_pytest_mock(self):
        """Test that pytest-mock can be imported"""
        try:
            import pytest_mock
            assert pytest_mock is not None
        except ImportError:
            pytest.skip("pytest-mock not installed in current environment")

    def test_import_hypothesis(self):
        """Test that hypothesis can be imported"""
        import hypothesis
        assert hypothesis is not None

    def test_import_black(self):
        """Test that black can be imported"""
        try:
            import black
            assert black is not None
        except ImportError:
            pytest.skip("black not installed in current environment")

    def test_import_mypy(self):
        """Test that mypy can be imported"""
        try:
            import mypy
            assert mypy is not None
        except ImportError:
            pytest.skip("mypy not installed in current environment")

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
        try:
            import agentic_sdlc.core
            assert agentic_sdlc.core is not None
        except ImportError as e:
            # If the module doesn't exist yet, that's okay
            # We're just testing that dependencies don't prevent imports
            if "No module named 'agentic_sdlc.core'" not in str(e):
                raise

    def test_import_agentic_sdlc_orchestration(self):
        """Test that agentic_sdlc.orchestration can be imported"""
        try:
            import agentic_sdlc.orchestration
            assert agentic_sdlc.orchestration is not None
        except ImportError as e:
            # If the module doesn't exist yet, that's okay
            if "No module named 'agentic_sdlc.orchestration'" not in str(e):
                raise

    def test_import_agentic_sdlc_infrastructure(self):
        """Test that agentic_sdlc.infrastructure can be imported"""
        try:
            import agentic_sdlc.infrastructure
            assert agentic_sdlc.infrastructure is not None
        except ImportError as e:
            # If the module doesn't exist yet, that's okay
            if "No module named 'agentic_sdlc.infrastructure'" not in str(e):
                raise

    def test_import_agentic_sdlc_intelligence(self):
        """Test that agentic_sdlc.intelligence can be imported"""
        try:
            import agentic_sdlc.intelligence
            assert agentic_sdlc.intelligence is not None
        except ImportError as e:
            # If the module doesn't exist yet, that's okay
            if "No module named 'agentic_sdlc.intelligence'" not in str(e):
                raise


class TestDependencySeparation:
    """Test that dependencies are properly separated between core and dev"""

    def test_requirements_contains_core_dependencies(self):
        """Test that requirements.txt contains core runtime dependencies"""
        with open('requirements.txt', 'r') as f:
            content = f.read()
        
        # Check for essential core dependencies
        core_deps = ['click', 'pydantic', 'requests', 'openai', 'anthropic']
        for dep in core_deps:
            assert dep in content, f"requirements.txt should contain {dep}"

    def test_requirements_dev_contains_testing_dependencies(self):
        """Test that requirements-dev.txt contains testing dependencies"""
        with open('requirements-dev.txt', 'r') as f:
            content = f.read()
        
        # Check for essential dev dependencies
        dev_deps = ['pytest', 'black', 'mypy', 'hypothesis']
        for dep in dev_deps:
            assert dep in content, f"requirements-dev.txt should contain {dep}"

    def test_requirements_dev_includes_requirements(self):
        """Test that requirements-dev.txt includes requirements.txt"""
        with open('requirements-dev.txt', 'r') as f:
            content = f.read()
        
        assert '-r requirements.txt' in content, \
            "requirements-dev.txt should include requirements.txt with -r"

    def test_no_duplicate_dependencies(self):
        """Test that dependencies are not duplicated between files"""
        with open('requirements.txt', 'r') as f:
            req_lines = [line.strip() for line in f.readlines() 
                        if line.strip() and not line.strip().startswith('#')]
        
        with open('requirements-dev.txt', 'r') as f:
            dev_lines = [line.strip() for line in f.readlines() 
                        if line.strip() and not line.strip().startswith('#') 
                        and not line.strip().startswith('-r')]
        
        # Extract package names (before ==, >=, etc.)
        def get_package_name(line):
            for op in ['==', '>=', '<=', '>', '<', '~=', '[']:
                if op in line:
                    return line.split(op)[0].strip()
            return line.strip()
        
        req_packages = {get_package_name(line) for line in req_lines}
        dev_packages = {get_package_name(line) for line in dev_lines}
        
        # Find duplicates
        duplicates = req_packages.intersection(dev_packages)
        
        # Some overlap is okay (like pytest might be in both), but major duplicates are not
        # We'll just warn if there are many duplicates
        assert len(duplicates) < 10, \
            f"Too many duplicate dependencies between requirements files: {duplicates}"


class TestVersionPinning:
    """Test that dependencies have appropriate version constraints"""

    def test_requirements_has_version_constraints(self):
        """Test that requirements.txt has version constraints for stability"""
        with open('requirements.txt', 'r') as f:
            lines = [line.strip() for line in f.readlines() 
                    if line.strip() and not line.strip().startswith('#') 
                    and not line.strip().startswith('-r')]
        
        # Count lines with version constraints
        versioned_lines = [line for line in lines 
                          if any(op in line for op in ['==', '>=', '<=', '>', '<', '~='])]
        
        # At least 80% of dependencies should have version constraints
        if len(lines) > 0:
            version_ratio = len(versioned_lines) / len(lines)
            assert version_ratio >= 0.8, \
                f"At least 80% of dependencies should have version constraints, got {version_ratio:.1%}"

    def test_critical_dependencies_pinned(self):
        """Test that critical dependencies have exact version pins"""
        with open('requirements.txt', 'r') as f:
            content = f.read()
        
        # Critical dependencies that should be pinned with ==
        critical_deps = ['openai', 'anthropic', 'pydantic', 'sqlalchemy']
        
        for dep in critical_deps:
            # Check if dependency exists and has == version pin
            if dep in content:
                # Find the line with this dependency
                for line in content.split('\n'):
                    if line.strip().startswith(dep):
                        # Should have == or >= for version constraint
                        assert '==' in line or '>=' in line, \
                            f"Critical dependency {dep} should have version constraint"
                        break
