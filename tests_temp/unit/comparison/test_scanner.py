"""
Unit tests for the Scanner module.

Tests the DirectoryScanner and LibraryAnalyzer classes.
"""

import os
import tempfile
from pathlib import Path

import pytest

from agentic_sdlc.comparison.scanner import DirectoryScanner, LibraryAnalyzer
from agentic_sdlc.comparison.models import ProjectStructure, LibraryInfo


class TestDirectoryScanner:
    """Unit tests for DirectoryScanner class."""
    
    def test_scan_project_basic(self, tmp_path):
        """Test basic project scanning."""
        # Create a simple directory structure
        (tmp_path / "src").mkdir()
        (tmp_path / "tests").mkdir()
        (tmp_path / "README.md").touch()
        
        scanner = DirectoryScanner()
        result = scanner.scan_project(str(tmp_path))
        
        assert isinstance(result, ProjectStructure)
        assert result.root_path == str(tmp_path)
        assert "." in result.directories
        assert "src" in result.directories
        assert "tests" in result.directories
    
    def test_scan_project_with_depth_limit(self, tmp_path):
        """Test scanning respects depth limit."""
        # Create nested structure: root/level1/level2/level3/level4
        level1 = tmp_path / "level1"
        level2 = level1 / "level2"
        level3 = level2 / "level3"
        level4 = level3 / "level4"
        
        level1.mkdir()
        level2.mkdir()
        level3.mkdir()
        level4.mkdir()
        
        scanner = DirectoryScanner()
        
        # Scan with depth 2
        result = scanner.scan_project(str(tmp_path), max_depth=2)
        
        # Should find root, level1, and level2
        assert "." in result.directories
        assert "level1" in result.directories
        assert "level1/level2" in result.directories
        
        # Should NOT find level3 or level4
        assert "level1/level2/level3" not in result.directories
        assert "level1/level2/level3/level4" not in result.directories
    
    def test_scan_project_nonexistent_path(self):
        """Test scanning nonexistent path raises error."""
        scanner = DirectoryScanner()
        
        with pytest.raises(ValueError, match="Root path does not exist"):
            scanner.scan_project("/nonexistent/path")
    
    def test_scan_project_file_not_directory(self, tmp_path):
        """Test scanning a file (not directory) raises error."""
        file_path = tmp_path / "file.txt"
        file_path.touch()
        
        scanner = DirectoryScanner()
        
        with pytest.raises(ValueError, match="not a directory"):
            scanner.scan_project(str(file_path))
    
    def test_check_directory_exists(self, tmp_path):
        """Test check_directory_exists method."""
        scanner = DirectoryScanner()
        
        # Create a directory
        test_dir = tmp_path / "test_dir"
        test_dir.mkdir()
        
        # Create a file
        test_file = tmp_path / "test_file.txt"
        test_file.touch()
        
        # Test existing directory
        assert scanner.check_directory_exists(str(test_dir)) is True
        
        # Test file (not directory)
        assert scanner.check_directory_exists(str(test_file)) is False
        
        # Test nonexistent path
        assert scanner.check_directory_exists(str(tmp_path / "nonexistent")) is False
    
    def test_get_subdirectories(self, tmp_path):
        """Test get_subdirectories method."""
        scanner = DirectoryScanner()
        
        # Create subdirectories
        (tmp_path / "dir1").mkdir()
        (tmp_path / "dir2").mkdir()
        (tmp_path / "dir3").mkdir()
        (tmp_path / ".hidden").mkdir()  # Hidden directory
        (tmp_path / "file.txt").touch()  # File (not directory)
        
        subdirs = scanner.get_subdirectories(str(tmp_path))
        
        # Should include visible directories only
        assert "dir1" in subdirs
        assert "dir2" in subdirs
        assert "dir3" in subdirs
        
        # Should NOT include hidden directories or files
        assert ".hidden" not in subdirs
        assert "file.txt" not in subdirs
        
        # Should be sorted
        assert subdirs == sorted(subdirs)
    
    def test_get_subdirectories_nonexistent(self):
        """Test get_subdirectories on nonexistent path."""
        scanner = DirectoryScanner()
        
        subdirs = scanner.get_subdirectories("/nonexistent/path")
        assert subdirs == []
    
    def test_get_subdirectories_file(self, tmp_path):
        """Test get_subdirectories on a file."""
        scanner = DirectoryScanner()
        
        file_path = tmp_path / "file.txt"
        file_path.touch()
        
        subdirs = scanner.get_subdirectories(str(file_path))
        assert subdirs == []
    
    def test_find_config_files(self, tmp_path):
        """Test find_config_files method."""
        scanner = DirectoryScanner()
        
        # Create some config files
        (tmp_path / "pyproject.toml").touch()
        (tmp_path / "requirements.txt").touch()
        (tmp_path / "Dockerfile").touch()
        
        config_files = scanner.find_config_files(str(tmp_path))
        
        # Should detect existing files
        assert config_files["pyproject.toml"] is True
        assert config_files["requirements.txt"] is True
        assert config_files["Dockerfile"] is True
        
        # Should detect missing files
        assert config_files["requirements-dev.txt"] is False
        assert config_files["docker-compose.yml"] is False
    
    def test_find_config_files_all_present(self, tmp_path):
        """Test find_config_files when all config files are present."""
        scanner = DirectoryScanner()
        
        # Create all config files
        for config_file in scanner.CONFIG_FILES:
            (tmp_path / config_file).touch()
        
        config_files = scanner.find_config_files(str(tmp_path))
        
        # All should be True
        for config_file in scanner.CONFIG_FILES:
            assert config_files[config_file] is True
    
    def test_find_config_files_none_present(self, tmp_path):
        """Test find_config_files when no config files are present."""
        scanner = DirectoryScanner()
        
        config_files = scanner.find_config_files(str(tmp_path))
        
        # All should be False
        for config_file in scanner.CONFIG_FILES:
            assert config_files[config_file] is False
    
    def test_scan_project_with_lib_directory(self, tmp_path):
        """Test scanning project with lib/ directory."""
        # Create lib/ directory with some packages
        lib_dir = tmp_path / "lib"
        lib_dir.mkdir()
        (lib_dir / "package1").mkdir()
        (lib_dir / "package2").mkdir()
        
        scanner = DirectoryScanner()
        result = scanner.scan_project(str(tmp_path))
        
        # Should have lib_info
        assert result.lib_info is not None
        assert result.lib_info.exists is True
        assert result.lib_info.package_count > 0
    
    def test_scan_project_without_lib_directory(self, tmp_path):
        """Test scanning project without lib/ directory."""
        scanner = DirectoryScanner()
        result = scanner.scan_project(str(tmp_path))
        
        # Should not have lib_info
        assert result.lib_info is None
    
    def test_scan_ignores_common_directories(self, tmp_path):
        """Test that scanning ignores common directories like .git, __pycache__, etc."""
        # Create directories that should be ignored
        (tmp_path / ".git").mkdir()
        (tmp_path / "__pycache__").mkdir()
        (tmp_path / ".pytest_cache").mkdir()
        (tmp_path / "node_modules").mkdir()
        (tmp_path / ".venv").mkdir()
        
        # Create a normal directory
        (tmp_path / "src").mkdir()
        
        scanner = DirectoryScanner()
        result = scanner.scan_project(str(tmp_path))
        
        # Should include src
        assert "src" in result.directories
        
        # Should NOT include ignored directories
        assert ".git" not in result.directories
        assert "__pycache__" not in result.directories
        assert ".pytest_cache" not in result.directories
        assert "node_modules" not in result.directories
        assert ".venv" not in result.directories
    
    def test_scan_counts_files_correctly(self, tmp_path):
        """Test that file counting works correctly."""
        # Create files in root
        (tmp_path / "file1.txt").touch()
        (tmp_path / "file2.py").touch()
        
        # Create subdirectory with files
        subdir = tmp_path / "subdir"
        subdir.mkdir()
        (subdir / "file3.txt").touch()
        (subdir / "file4.py").touch()
        
        scanner = DirectoryScanner()
        result = scanner.scan_project(str(tmp_path))
        
        # Root should have 2 files
        assert result.directories["."].file_count == 2
        
        # Subdir should have 2 files
        assert result.directories["subdir"].file_count == 2


class TestLibraryAnalyzer:
    """Unit tests for LibraryAnalyzer class."""
    
    def test_analyze_lib_directory_exists(self, tmp_path):
        """Test analyzing an existing lib/ directory."""
        lib_dir = tmp_path / "lib"
        lib_dir.mkdir()
        
        # Create some package directories
        (lib_dir / "package1").mkdir()
        (lib_dir / "package2-1.0.0").mkdir()
        (lib_dir / "package3.dist-info").mkdir()
        
        # Create some files
        (lib_dir / "file1.txt").write_text("test content")
        (lib_dir / "file2.py").write_text("print('hello')")
        
        analyzer = LibraryAnalyzer()
        result = analyzer.analyze_lib_directory(str(lib_dir))
        
        assert isinstance(result, LibraryInfo)
        assert result.exists is True
        assert result.package_count > 0
        assert result.total_size_mb > 0
        assert len(result.packages) > 0
    
    def test_analyze_lib_directory_not_exists(self, tmp_path):
        """Test analyzing a nonexistent lib/ directory."""
        lib_dir = tmp_path / "lib"
        
        analyzer = LibraryAnalyzer()
        result = analyzer.analyze_lib_directory(str(lib_dir))
        
        assert isinstance(result, LibraryInfo)
        assert result.exists is False
        assert result.package_count == 0
        assert result.total_size_mb == 0.0
        assert result.packages == []
    
    def test_extract_dependencies(self, tmp_path):
        """Test extracting dependencies from lib/."""
        lib_dir = tmp_path / "lib"
        lib_dir.mkdir()
        
        # Create package directories with various naming patterns
        (lib_dir / "requests").mkdir()
        (lib_dir / "numpy-1.21.0").mkdir()
        (lib_dir / "pandas.dist-info").mkdir()
        (lib_dir / "scipy.egg-info").mkdir()
        (lib_dir / ".hidden").mkdir()  # Should be ignored
        (lib_dir / "__pycache__").mkdir()  # Should be ignored
        
        analyzer = LibraryAnalyzer()
        packages = analyzer.extract_dependencies(str(lib_dir))
        
        # Should extract package names
        assert "requests" in packages
        assert "numpy" in packages
        assert "pandas" in packages
        assert "scipy" in packages
        
        # Should NOT include hidden or special directories
        assert ".hidden" not in packages
        assert "__pycache__" not in packages
        
        # Should be sorted
        assert packages == sorted(packages)
    
    def test_extract_dependencies_with_egg_files(self, tmp_path):
        """Test extracting dependencies from .egg files."""
        lib_dir = tmp_path / "lib"
        lib_dir.mkdir()
        
        # Create .egg files
        (lib_dir / "package1-1.0.0.egg").touch()
        (lib_dir / "package2-2.0.0.egg").touch()
        
        analyzer = LibraryAnalyzer()
        packages = analyzer.extract_dependencies(str(lib_dir))
        
        # Should extract package names from .egg files
        assert "package1" in packages
        assert "package2" in packages
    
    def test_extract_dependencies_with_whl_files(self, tmp_path):
        """Test extracting dependencies from .whl files."""
        lib_dir = tmp_path / "lib"
        lib_dir.mkdir()
        
        # Create .whl files
        (lib_dir / "package1-1.0.0-py3-none-any.whl").touch()
        (lib_dir / "package2-2.0.0-py3-none-any.whl").touch()
        
        analyzer = LibraryAnalyzer()
        packages = analyzer.extract_dependencies(str(lib_dir))
        
        # Should extract package names from .whl files
        assert "package1" in packages
        assert "package2" in packages
    
    def test_extract_dependencies_removes_duplicates(self, tmp_path):
        """Test that duplicate package names are removed."""
        lib_dir = tmp_path / "lib"
        lib_dir.mkdir()
        
        # Create multiple entries for the same package
        (lib_dir / "requests").mkdir()
        (lib_dir / "requests-2.26.0").mkdir()
        (lib_dir / "requests.dist-info").mkdir()
        
        analyzer = LibraryAnalyzer()
        packages = analyzer.extract_dependencies(str(lib_dir))
        
        # Should only have one entry for requests
        assert packages.count("requests") == 1
    
    def test_extract_dependencies_nonexistent(self, tmp_path):
        """Test extracting dependencies from nonexistent directory."""
        lib_dir = tmp_path / "lib"
        
        analyzer = LibraryAnalyzer()
        packages = analyzer.extract_dependencies(str(lib_dir))
        
        assert packages == []
    
    def test_analyze_calculates_size_correctly(self, tmp_path):
        """Test that size calculation works correctly."""
        lib_dir = tmp_path / "lib"
        lib_dir.mkdir()
        
        # Create a file with known size (1 KB)
        file1 = lib_dir / "file1.txt"
        file1.write_text("x" * 1024)
        
        # Create another file (2 KB)
        file2 = lib_dir / "file2.txt"
        file2.write_text("y" * 2048)
        
        analyzer = LibraryAnalyzer()
        result = analyzer.analyze_lib_directory(str(lib_dir))
        
        # Total should be approximately 3 KB = 0.003 MB
        # Allow some tolerance for file system overhead
        assert 0.002 <= result.total_size_mb <= 0.004
    
    def test_analyze_handles_nested_files(self, tmp_path):
        """Test that analyzer handles nested files in packages."""
        lib_dir = tmp_path / "lib"
        lib_dir.mkdir()
        
        # Create nested structure
        package_dir = lib_dir / "mypackage"
        package_dir.mkdir()
        subdir = package_dir / "subdir"
        subdir.mkdir()
        
        # Create files at different levels
        (package_dir / "file1.py").write_text("x" * 1024)
        (subdir / "file2.py").write_text("y" * 1024)
        
        analyzer = LibraryAnalyzer()
        result = analyzer.analyze_lib_directory(str(lib_dir))
        
        # Should count all files recursively
        assert result.total_size_mb > 0
        assert "mypackage" in result.packages
