"""
File Scanner service for the Project Audit and Cleanup System.

This module provides functionality to recursively scan project directories,
collect file metadata, calculate directory sizes, and support exclude patterns.
"""

import os
from pathlib import Path
from datetime import datetime
from typing import List, Set, Optional
import fnmatch

from .models import FileInfo, DirectoryInfo
from .logger import get_logger


class FileScanner:
    """Recursively scan project directories and collect file metadata.
    
    The FileScanner walks through directory trees, collecting information about
    files and directories while respecting exclude patterns. It calculates file
    sizes, modification times, and directory statistics.
    
    Attributes:
        logger: Logger instance for operation logging
        exclude_patterns: List of glob patterns to exclude from scanning
    
    Example:
        >>> scanner = FileScanner(exclude_patterns=["*.pyc", "__pycache__"])
        >>> files = scanner.scan(Path("/path/to/project"))
        >>> print(f"Found {len(files)} files")
    """
    
    def __init__(self, exclude_patterns: Optional[List[str]] = None, verbose: bool = False):
        """Initialize the FileScanner.
        
        Args:
            exclude_patterns: List of glob patterns to exclude (e.g., ["*.pyc", "node_modules"])
            verbose: Enable verbose logging
        """
        self.logger = get_logger(verbose=verbose)
        self.exclude_patterns = exclude_patterns or []
        self._scanned_files: List[FileInfo] = []
        self._scanned_dirs: List[DirectoryInfo] = []
    
    def scan(self, root_path: Path, exclude_patterns: Optional[List[str]] = None) -> List[FileInfo]:
        """Scan directory recursively and return list of files with metadata.
        
        This method walks through the directory tree starting at root_path,
        collecting metadata for all files while respecting exclude patterns.
        
        Args:
            root_path: Root directory to start scanning from
            exclude_patterns: Additional exclude patterns for this scan (merged with instance patterns)
            
        Returns:
            List of FileInfo objects for all discovered files
            
        Raises:
            FileNotFoundError: If root_path does not exist
            PermissionError: If root_path is not accessible
            
        Example:
            >>> scanner = FileScanner()
            >>> files = scanner.scan(Path("."), exclude_patterns=["*.log"])
            >>> for file in files:
            ...     print(f"{file.path}: {file.size} bytes")
        """
        if not root_path.exists():
            raise FileNotFoundError(f"Path does not exist: {root_path}")
        
        if not os.access(root_path, os.R_OK):
            raise PermissionError(f"Permission denied: {root_path}")
        
        # Merge exclude patterns
        all_patterns = self.exclude_patterns.copy()
        if exclude_patterns:
            all_patterns.extend(exclude_patterns)
        
        self.logger.info(f"Starting scan of: {root_path}")
        self.logger.debug(f"Exclude patterns: {all_patterns}")
        
        self._scanned_files = []
        self._scanned_dirs = []
        
        # Perform recursive scan
        self._scan_recursive(root_path, all_patterns)
        
        self.logger.info(f"Scan complete. Found {len(self._scanned_files)} files in {len(self._scanned_dirs)} directories")
        
        return self._scanned_files
    
    def _scan_recursive(self, current_path: Path, exclude_patterns: List[str]) -> None:
        """Recursively scan directory and collect file information.
        
        Args:
            current_path: Current directory being scanned
            exclude_patterns: Patterns to exclude from scanning
        """
        try:
            # Get all entries in current directory
            entries = list(current_path.iterdir())
        except PermissionError:
            self.logger.warning(f"Permission denied, skipping: {current_path}")
            return
        except OSError as e:
            self.logger.warning(f"Error accessing {current_path}: {e}")
            return
        
        for entry in entries:
            # Check if entry should be excluded
            if self._should_exclude(entry, exclude_patterns):
                self.logger.debug(f"Excluding: {entry}")
                continue
            
            try:
                if entry.is_file():
                    # Collect file metadata
                    file_info = self.get_file_info(entry)
                    self._scanned_files.append(file_info)
                    
                elif entry.is_dir():
                    # Recursively scan subdirectory
                    self._scan_recursive(entry, exclude_patterns)
                    
            except (PermissionError, OSError) as e:
                self.logger.warning(f"Error processing {entry}: {e}")
                continue
    
    def _should_exclude(self, path: Path, exclude_patterns: List[str]) -> bool:
        """Check if path matches any exclude pattern.
        
        Args:
            path: Path to check
            exclude_patterns: List of glob patterns
            
        Returns:
            True if path should be excluded, False otherwise
        """
        path_str = str(path)
        path_name = path.name
        
        for pattern in exclude_patterns:
            # Match against full path
            if fnmatch.fnmatch(path_str, pattern):
                return True
            # Match against just the name
            if fnmatch.fnmatch(path_name, pattern):
                return True
            # Match against path with wildcards
            if fnmatch.fnmatch(path_str, f"*/{pattern}"):
                return True
            if fnmatch.fnmatch(path_str, f"*/{pattern}/*"):
                return True
        
        return False
    
    def get_file_info(self, file_path: Path) -> FileInfo:
        """Get metadata for a single file.
        
        Args:
            file_path: Path to the file
            
        Returns:
            FileInfo object with file metadata
            
        Raises:
            FileNotFoundError: If file does not exist
            
        Example:
            >>> scanner = FileScanner()
            >>> info = scanner.get_file_info(Path("README.md"))
            >>> print(f"Size: {info.size}, Modified: {info.modified_time}")
        """
        if not file_path.exists():
            raise FileNotFoundError(f"File does not exist: {file_path}")
        
        stat = file_path.stat()
        
        return FileInfo(
            path=file_path,
            size=stat.st_size,
            modified_time=datetime.fromtimestamp(stat.st_mtime),
            category=None,
            is_critical=False,
            reason=""
        )
    
    def calculate_directory_size(self, dir_path: Path) -> int:
        """Calculate total size of all files in directory (recursive).
        
        This method walks through the directory tree and sums up the sizes
        of all files contained within.
        
        Args:
            dir_path: Path to the directory
            
        Returns:
            Total size in bytes
            
        Raises:
            FileNotFoundError: If directory does not exist
            NotADirectoryError: If path is not a directory
            
        Example:
            >>> scanner = FileScanner()
            >>> size = scanner.calculate_directory_size(Path("./src"))
            >>> print(f"Directory size: {size / (1024*1024):.2f} MB")
        """
        if not dir_path.exists():
            raise FileNotFoundError(f"Directory does not exist: {dir_path}")
        
        if not dir_path.is_dir():
            raise NotADirectoryError(f"Path is not a directory: {dir_path}")
        
        total_size = 0
        
        try:
            for entry in dir_path.rglob("*"):
                if entry.is_file():
                    try:
                        total_size += entry.stat().st_size
                    except (PermissionError, OSError) as e:
                        self.logger.debug(f"Cannot stat {entry}: {e}")
                        continue
        except (PermissionError, OSError) as e:
            self.logger.warning(f"Error calculating size for {dir_path}: {e}")
        
        return total_size
    
    def get_directory_info(self, dir_path: Path) -> DirectoryInfo:
        """Get metadata for a directory including size and file count.
        
        Args:
            dir_path: Path to the directory
            
        Returns:
            DirectoryInfo object with directory metadata
            
        Raises:
            FileNotFoundError: If directory does not exist
            NotADirectoryError: If path is not a directory
            
        Example:
            >>> scanner = FileScanner()
            >>> info = scanner.get_directory_info(Path("./tests"))
            >>> print(f"Files: {info.file_count}, Size: {info.size}")
        """
        if not dir_path.exists():
            raise FileNotFoundError(f"Directory does not exist: {dir_path}")
        
        if not dir_path.is_dir():
            raise NotADirectoryError(f"Path is not a directory: {dir_path}")
        
        # Calculate size and count files
        total_size = 0
        file_count = 0
        
        try:
            for entry in dir_path.rglob("*"):
                if entry.is_file():
                    try:
                        total_size += entry.stat().st_size
                        file_count += 1
                    except (PermissionError, OSError):
                        continue
        except (PermissionError, OSError) as e:
            self.logger.warning(f"Error scanning directory {dir_path}: {e}")
        
        # Check if directory is empty (no files or only .DS_Store/.gitkeep)
        is_empty = self._is_directory_empty(dir_path)
        
        return DirectoryInfo(
            path=dir_path,
            size=total_size,
            file_count=file_count,
            is_empty=is_empty,
            is_critical=False
        )
    
    def _is_directory_empty(self, dir_path: Path) -> bool:
        """Check if directory is empty or contains only .DS_Store/.gitkeep files.
        
        Args:
            dir_path: Path to check
            
        Returns:
            True if directory is effectively empty, False otherwise
        """
        try:
            entries = list(dir_path.rglob("*"))
            
            # No entries means empty
            if not entries:
                return True
            
            # Check if all entries are .DS_Store or .gitkeep
            for entry in entries:
                if entry.is_file():
                    if entry.name not in [".DS_Store", ".gitkeep"]:
                        return False
            
            return True
            
        except (PermissionError, OSError):
            return False
    
    def get_scanned_directories(self) -> List[DirectoryInfo]:
        """Get list of all directories discovered during last scan.
        
        Returns:
            List of DirectoryInfo objects for all scanned directories
            
        Note:
            This method returns cached results from the last scan() call.
            Call scan() first to populate the directory list.
        """
        return self._scanned_dirs
