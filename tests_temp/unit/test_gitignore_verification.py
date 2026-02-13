"""
Unit tests for .gitignore verification

This test verifies that the .gitignore file properly excludes
the lib/ directory and other generated directories from version control.

Requirements: 1.4
"""

import subprocess
import pytest


class TestGitignoreExclusions:
    """Test that required directories are excluded from version control"""

    def test_lib_directory_excluded(self):
        """Test that lib/ directory is excluded from version control"""
        result = subprocess.run(
            ['git', 'check-ignore', 'lib/'],
            capture_output=True,
            text=True
        )
        assert result.returncode == 0, "lib/ should be excluded by .gitignore"

    def test_agentic_sdlc_lib_excluded(self):
        """Test that agentic_sdlc/lib/ directory is excluded from version control"""
        result = subprocess.run(
            ['git', 'check-ignore', 'agentic_sdlc/lib/'],
            capture_output=True,
            text=True
        )
        assert result.returncode == 0, "agentic_sdlc/lib/ should be excluded by .gitignore"

    def test_venv_directory_excluded(self):
        """Test that .venv/ directory is excluded from version control"""
        result = subprocess.run(
            ['git', 'check-ignore', '.venv/'],
            capture_output=True,
            text=True
        )
        assert result.returncode == 0, ".venv/ should be excluded by .gitignore"

    def test_pycache_excluded(self):
        """Test that __pycache__/ directory is excluded from version control"""
        result = subprocess.run(
            ['git', 'check-ignore', '__pycache__/'],
            capture_output=True,
            text=True
        )
        assert result.returncode == 0, "__pycache__/ should be excluded by .gitignore"

    def test_pytest_cache_excluded(self):
        """Test that .pytest_cache/ directory is excluded from version control"""
        result = subprocess.run(
            ['git', 'check-ignore', '.pytest_cache/'],
            capture_output=True,
            text=True
        )
        assert result.returncode == 0, ".pytest_cache/ should be excluded by .gitignore"

    def test_hypothesis_excluded(self):
        """Test that .hypothesis/ directory is excluded from version control"""
        result = subprocess.run(
            ['git', 'check-ignore', '.hypothesis/'],
            capture_output=True,
            text=True
        )
        assert result.returncode == 0, ".hypothesis/ should be excluded by .gitignore"

    def test_mypy_cache_excluded(self):
        """Test that .mypy_cache/ directory is excluded from version control"""
        result = subprocess.run(
            ['git', 'check-ignore', '.mypy_cache/'],
            capture_output=True,
            text=True
        )
        assert result.returncode == 0, ".mypy_cache/ should be excluded by .gitignore"

    def test_build_directory_excluded(self):
        """Test that build/ directory is excluded from version control"""
        result = subprocess.run(
            ['git', 'check-ignore', 'build/'],
            capture_output=True,
            text=True
        )
        assert result.returncode == 0, "build/ should be excluded by .gitignore"

    def test_dist_directory_excluded(self):
        """Test that dist/ directory is excluded from version control"""
        result = subprocess.run(
            ['git', 'check-ignore', 'dist/'],
            capture_output=True,
            text=True
        )
        assert result.returncode == 0, "dist/ should be excluded by .gitignore"

    def test_egg_info_excluded(self):
        """Test that *.egg-info directories are excluded from version control"""
        result = subprocess.run(
            ['git', 'check-ignore', 'test.egg-info/'],
            capture_output=True,
            text=True
        )
        assert result.returncode == 0, "*.egg-info/ should be excluded by .gitignore"

    def test_no_lib_files_tracked(self):
        """Test that no files from lib/ directories are tracked in git"""
        result = subprocess.run(
            ['git', 'ls-files', 'lib/', 'agentic_sdlc/lib/'],
            capture_output=True,
            text=True
        )
        assert not result.stdout.strip(), "No lib/ files should be tracked in version control"

    def test_gitignore_file_exists(self):
        """Test that .gitignore file exists"""
        import os
        assert os.path.exists('.gitignore'), ".gitignore file should exist"

    def test_gitignore_contains_lib_pattern(self):
        """Test that .gitignore contains lib/ pattern"""
        with open('.gitignore', 'r') as f:
            content = f.read()
        assert 'lib/' in content, ".gitignore should contain lib/ pattern"
        assert 'agentic_sdlc/lib/' in content, ".gitignore should contain agentic_sdlc/lib/ pattern"

    def test_gitignore_contains_venv_patterns(self):
        """Test that .gitignore contains virtual environment patterns"""
        with open('.gitignore', 'r') as f:
            content = f.read()
        assert '.venv/' in content, ".gitignore should contain .venv/ pattern"
        assert 'venv/' in content, ".gitignore should contain venv/ pattern"

    def test_gitignore_contains_python_patterns(self):
        """Test that .gitignore contains Python-specific patterns"""
        with open('.gitignore', 'r') as f:
            content = f.read()
        assert '__pycache__/' in content, ".gitignore should contain __pycache__/ pattern"
        assert '*.pyc' in content, ".gitignore should contain *.pyc pattern"
        assert '.pytest_cache/' in content, ".gitignore should contain .pytest_cache/ pattern"
