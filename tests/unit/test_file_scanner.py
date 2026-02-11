"""
Unit tests for FileScanner service.

Tests specific examples, edge cases, and error conditions for file scanning.
"""

import pytest
from pathlib import Path
import tempfile
import os

from scripts.cleanup.scanner import FileScanner
from scripts.cleanup.models import FileInfo, DirectoryInfo


class TestFileScannerBasics:
    """Test basic FileScanner functionality."""
    
    def test_scanner_initialization(self):
        """Test FileScanner can be initialized with and without patterns."""
        scanner1 = FileScanner()
        assert scanner1.exclude_patterns == []
        
        scanner2 = FileScanner(exclude_patterns=["*.pyc", "__pycache__"])
        assert scanner2.exclude_patterns == ["*.pyc", "__pycache__"]
    
    def test_get_file_info_basic(self):
        """Test getting file info for a single file."""
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.txt') as f:
            f.write("test content")
            temp_path = Path(f.name)
        
        try:
            scanner = FileScanner()
            file_info = scanner.get_file_info(temp_path)
            
            assert isinstance(file_info, FileInfo)
            assert file_info.path == temp_path
            assert file_info.size > 0
            assert file_info.modified_time is not None
            assert file_info.category is None
            assert file_info.is_critical is False
        finally:
            temp_path.unlink()
    
    def test_get_file_info_nonexistent(self):
        """Test getting file info for nonexistent file raises error."""
        scanner = FileScanner()
        with pytest.raises(FileNotFoundError):
            scanner.get_file_info(Path("/nonexistent/file.txt"))


class TestDirectoryScanning:
    """Test directory scanning with various structures."""
    
    def test_scan_empty_directory(self):
        """Test scanning an empty directory."""
        with tempfile.TemporaryDirectory() as tmpdir:
            scanner = FileScanner()
            files = scanner.scan(Path(tmpdir))
            assert files == []
    
    def test_scan_flat_directory(self):
        """Test scanning a directory with only files (no subdirectories)."""
        with tempfile.TemporaryDirectory() as tmpdir:
            tmp_path = Path(tmpdir)
            
            # Create test files
            (tmp_path / "file1.txt").write_text("content1")
            (tmp_path / "file2.py").write_text("content2")
            (tmp_path / "file3.md").write_text("content3")
            
            scanner = FileScanner()
            files = scanner.scan(tmp_path)
            
            assert len(files) == 3
            filenames = {f.path.name for f in files}
            assert filenames == {"file1.txt", "file2.py", "file3.md"}
    
    def test_scan_nested_directory(self):
        """Test scanning a directory with nested subdirectories."""
        with tempfile.TemporaryDirectory() as tmpdir:
            tmp_path = Path(tmpdir)
            
            # Create nested structure
            (tmp_path / "dir1").mkdir()
            (tmp_path / "dir1" / "file1.txt").write_text("content1")
            (tmp_path / "dir1" / "dir2").mkdir()
            (tmp_path / "dir1" / "dir2" / "file2.txt").write_text("content2")
            (tmp_path / "file3.txt").write_text("content3")
            
            scanner = FileScanner()
            files = scanner.scan(tmp_path)
            
            assert len(files) == 3
            filenames = {f.path.name for f in files}
            assert filenames == {"file1.txt", "file2.txt", "file3.txt"}
    
    def test_scan_nonexistent_directory(self):
        """Test scanning nonexistent directory raises error."""
        scanner = FileScanner()
        with pytest.raises(FileNotFoundError):
            scanner.scan(Path("/nonexistent/directory"))


class TestExcludePatterns:
    """Test exclude pattern functionality."""
    
    def test_exclude_by_extension(self):
        """Test excluding files by extension pattern."""
        with tempfile.TemporaryDirectory() as tmpdir:
            tmp_path = Path(tmpdir)
            
            # Create files with different extensions
            (tmp_path / "file1.txt").write_text("content")
            (tmp_path / "file2.pyc").write_text("content")
            (tmp_path / "file3.py").write_text("content")
            (tmp_path / "file4.pyc").write_text("content")
            
            scanner = FileScanner(exclude_patterns=["*.pyc"])
            files = scanner.scan(tmp_path)
            
            filenames = {f.path.name for f in files}
            assert "file1.txt" in filenames
            assert "file3.py" in filenames
            assert "file2.pyc" not in filenames
            assert "file4.pyc" not in filenames
    
    def test_exclude_by_directory_name(self):
        """Test excluding entire directories by name."""
        with tempfile.TemporaryDirectory() as tmpdir:
            tmp_path = Path(tmpdir)
            
            # Create directory structure
            (tmp_path / "__pycache__").mkdir()
            (tmp_path / "__pycache__" / "file1.pyc").write_text("content")
            (tmp_path / "src").mkdir()
            (tmp_path / "src" / "file2.py").write_text("content")
            (tmp_path / "file3.txt").write_text("content")
            
            scanner = FileScanner(exclude_patterns=["__pycache__"])
            files = scanner.scan(tmp_path)
            
            filenames = {f.path.name for f in files}
            assert "file2.py" in filenames
            assert "file3.txt" in filenames
            assert "file1.pyc" not in filenames
    
    def test_exclude_multiple_patterns(self):
        """Test excluding with multiple patterns."""
        with tempfile.TemporaryDirectory() as tmpdir:
            tmp_path = Path(tmpdir)
            
            # Create various files
            (tmp_path / "file1.txt").write_text("content")
            (tmp_path / "file2.pyc").write_text("content")
            (tmp_path / "file3.log").write_text("content")
            (tmp_path / ".DS_Store").write_text("content")
            (tmp_path / "file4.py").write_text("content")
            
            scanner = FileScanner(exclude_patterns=["*.pyc", "*.log", ".DS_Store"])
            files = scanner.scan(tmp_path)
            
            filenames = {f.path.name for f in files}
            assert filenames == {"file1.txt", "file4.py"}
    
    def test_scan_with_additional_patterns(self):
        """Test providing additional exclude patterns to scan method."""
        with tempfile.TemporaryDirectory() as tmpdir:
            tmp_path = Path(tmpdir)
            
            (tmp_path / "file1.txt").write_text("content")
            (tmp_path / "file2.pyc").write_text("content")
            (tmp_path / "file3.log").write_text("content")
            
            # Scanner has one pattern, scan adds another
            scanner = FileScanner(exclude_patterns=["*.pyc"])
            files = scanner.scan(tmp_path, exclude_patterns=["*.log"])
            
            filenames = {f.path.name for f in files}
            assert filenames == {"file1.txt"}


class TestSizeCalculation:
    """Test directory size calculation."""
    
    def test_calculate_directory_size_empty(self):
        """Test calculating size of empty directory."""
        with tempfile.TemporaryDirectory() as tmpdir:
            scanner = FileScanner()
            size = scanner.calculate_directory_size(Path(tmpdir))
            assert size == 0
    
    def test_calculate_directory_size_single_file(self):
        """Test calculating size with single file."""
        with tempfile.TemporaryDirectory() as tmpdir:
            tmp_path = Path(tmpdir)
            content = "x" * 1000
            (tmp_path / "file.txt").write_text(content)
            
            scanner = FileScanner()
            size = scanner.calculate_directory_size(tmp_path)
            assert size == 1000
    
    def test_calculate_directory_size_multiple_files(self):
        """Test calculating size with multiple files."""
        with tempfile.TemporaryDirectory() as tmpdir:
            tmp_path = Path(tmpdir)
            
            (tmp_path / "file1.txt").write_text("x" * 100)
            (tmp_path / "file2.txt").write_text("x" * 200)
            (tmp_path / "file3.txt").write_text("x" * 300)
            
            scanner = FileScanner()
            size = scanner.calculate_directory_size(tmp_path)
            assert size == 600
    
    def test_calculate_directory_size_nested(self):
        """Test calculating size with nested directories."""
        with tempfile.TemporaryDirectory() as tmpdir:
            tmp_path = Path(tmpdir)
            
            (tmp_path / "dir1").mkdir()
            (tmp_path / "dir1" / "file1.txt").write_text("x" * 100)
            (tmp_path / "dir1" / "dir2").mkdir()
            (tmp_path / "dir1" / "dir2" / "file2.txt").write_text("x" * 200)
            (tmp_path / "file3.txt").write_text("x" * 300)
            
            scanner = FileScanner()
            size = scanner.calculate_directory_size(tmp_path)
            assert size == 600
    
    def test_calculate_directory_size_nonexistent(self):
        """Test calculating size of nonexistent directory raises error."""
        scanner = FileScanner()
        with pytest.raises(FileNotFoundError):
            scanner.calculate_directory_size(Path("/nonexistent"))
    
    def test_calculate_directory_size_file_not_directory(self):
        """Test calculating size of file (not directory) raises error."""
        with tempfile.NamedTemporaryFile(delete=False) as f:
            temp_path = Path(f.name)
        
        try:
            scanner = FileScanner()
            with pytest.raises(NotADirectoryError):
                scanner.calculate_directory_size(temp_path)
        finally:
            temp_path.unlink()


class TestDirectoryInfo:
    """Test getting directory information."""
    
    def test_get_directory_info_empty(self):
        """Test getting info for empty directory."""
        with tempfile.TemporaryDirectory() as tmpdir:
            scanner = FileScanner()
            info = scanner.get_directory_info(Path(tmpdir))
            
            assert isinstance(info, DirectoryInfo)
            assert info.size == 0
            assert info.file_count == 0
            assert info.is_empty is True
    
    def test_get_directory_info_with_files(self):
        """Test getting info for directory with files."""
        with tempfile.TemporaryDirectory() as tmpdir:
            tmp_path = Path(tmpdir)
            
            (tmp_path / "file1.txt").write_text("x" * 100)
            (tmp_path / "file2.txt").write_text("x" * 200)
            
            scanner = FileScanner()
            info = scanner.get_directory_info(tmp_path)
            
            assert info.size == 300
            assert info.file_count == 2
            assert info.is_empty is False
    
    def test_get_directory_info_only_ds_store(self):
        """Test directory with only .DS_Store is considered empty."""
        with tempfile.TemporaryDirectory() as tmpdir:
            tmp_path = Path(tmpdir)
            (tmp_path / ".DS_Store").write_text("content")
            
            scanner = FileScanner()
            info = scanner.get_directory_info(tmp_path)
            
            assert info.is_empty is True
    
    def test_get_directory_info_only_gitkeep(self):
        """Test directory with only .gitkeep is considered empty."""
        with tempfile.TemporaryDirectory() as tmpdir:
            tmp_path = Path(tmpdir)
            (tmp_path / ".gitkeep").write_text("")
            
            scanner = FileScanner()
            info = scanner.get_directory_info(tmp_path)
            
            assert info.is_empty is True
    
    def test_get_directory_info_ds_store_and_real_file(self):
        """Test directory with .DS_Store and real file is not empty."""
        with tempfile.TemporaryDirectory() as tmpdir:
            tmp_path = Path(tmpdir)
            (tmp_path / ".DS_Store").write_text("content")
            (tmp_path / "real_file.txt").write_text("content")
            
            scanner = FileScanner()
            info = scanner.get_directory_info(tmp_path)
            
            assert info.is_empty is False


class TestEdgeCases:
    """Test edge cases and error conditions."""
    
    def test_scan_with_permission_error(self):
        """Test scanning continues when permission denied on subdirectory."""
        with tempfile.TemporaryDirectory() as tmpdir:
            tmp_path = Path(tmpdir)
            
            # Create accessible file
            (tmp_path / "accessible.txt").write_text("content")
            
            # Create directory and make it inaccessible
            restricted_dir = tmp_path / "restricted"
            restricted_dir.mkdir()
            (restricted_dir / "file.txt").write_text("content")
            
            try:
                os.chmod(restricted_dir, 0o000)
                
                scanner = FileScanner()
                files = scanner.scan(tmp_path)
                
                # Should find the accessible file, skip restricted directory
                filenames = {f.path.name for f in files}
                assert "accessible.txt" in filenames
                assert "file.txt" not in filenames
            finally:
                # Restore permissions for cleanup
                os.chmod(restricted_dir, 0o755)
    
    def test_scan_symlinks(self):
        """Test scanning handles symlinks appropriately."""
        with tempfile.TemporaryDirectory() as tmpdir:
            tmp_path = Path(tmpdir)
            
            # Create real file
            real_file = tmp_path / "real.txt"
            real_file.write_text("content")
            
            # Create symlink
            symlink = tmp_path / "link.txt"
            try:
                symlink.symlink_to(real_file)
                
                scanner = FileScanner()
                files = scanner.scan(tmp_path)
                
                # Should find both real file and symlink
                assert len(files) >= 1
            except OSError:
                # Symlinks might not be supported on all systems
                pytest.skip("Symlinks not supported on this system")
