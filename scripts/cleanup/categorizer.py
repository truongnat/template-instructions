"""
File Categorizer service for the Project Audit and Cleanup System.

This module provides functionality to categorize files into KEEP, REMOVE,
CONSOLIDATE, or ARCHIVE categories based on predefined rules. It identifies
critical components, corrupt directories, cache files, and empty directories.
"""

from pathlib import Path
from typing import List, Set, Optional
from datetime import datetime, timedelta

from .models import FileInfo, DirectoryInfo, FileCategory
from .logger import get_logger


class FileCategorizer:
    """Categorize files based on project cleanup rules.
    
    The FileCategorizer applies a comprehensive set of rules to determine
    whether files should be kept, removed, consolidated, or archived. It
    identifies critical components that must be preserved, corrupt directories
    that should be removed, cache files that can be archived, and empty
    directories that can be cleaned up.
    
    Attributes:
        logger: Logger instance for operation logging
        critical_paths: Set of path patterns for critical components
        critical_empty_dirs: Set of directory names that should remain even if empty
        cache_age_threshold: Age in days for cache files to be archived
    
    Example:
        >>> categorizer = FileCategorizer()
        >>> file_info = FileInfo(path=Path("agentic_sdlc/core/main.py"), ...)
        >>> category = categorizer.categorize(file_info)
        >>> print(category)  # FileCategory.KEEP
    """
    
    # Critical component path patterns (must be preserved)
    CRITICAL_PATHS = {
        "agentic_sdlc/core",
        "agentic_sdlc/intelligence",
        "agentic_sdlc/infrastructure",
        "agentic_sdlc/orchestration",
        "agentic_sdlc/defaults",
        "docs",
        ".agent",
        ".kiro",
        "tests",
        "bin",
        "scripts",
    }
    
    # Critical root configuration files
    CRITICAL_ROOT_FILES = {
        "pyproject.toml",
        "package.json",
        "docker-compose.yml",
        "Dockerfile",
        ".gitignore",
        ".dockerignore",
        "README.md",
        "LICENSE",
        "SECURITY.md",
        "CONTRIBUTING.md",
        "MANIFEST.in",
    }
    
    # Directories to exclude from critical defaults path
    DEFAULTS_EXCLUDE = {
        "projects",
    }
    
    # Empty directories that should be preserved
    CRITICAL_EMPTY_DIRS = {
        "logs",
        "states",
        "data",
        ".brain",
        ".hypothesis",
        "__pycache__",
    }
    
    # Cache directory patterns
    CACHE_PATTERNS = {
        "__pycache__",
        ".hypothesis",
        ".brain",
        ".pytest_cache",
        ".mypy_cache",
        ".ruff_cache",
    }
    
    # File patterns to remove
    REMOVE_PATTERNS = {
        "*.pyc",
        "*.pyo",
        ".DS_Store",
        "*.swp",
        "*.swo",
        "*~",
    }
    
    def __init__(self, cache_age_threshold: int = 30, verbose: bool = False):
        """Initialize the FileCategorizer.
        
        Args:
            cache_age_threshold: Age in days for cache files to be archived (default: 30)
            verbose: Enable verbose logging
        """
        self.logger = get_logger(verbose=verbose)
        self.cache_age_threshold = cache_age_threshold
        self.critical_paths = self.CRITICAL_PATHS.copy()
        self.critical_empty_dirs = self.CRITICAL_EMPTY_DIRS.copy()
    
    def categorize(self, file_info: FileInfo) -> FileCategory:
        """Determine category for a file based on categorization rules.
        
        This method applies a series of rules to determine the appropriate
        category for a file. Rules are checked in priority order:
        1. Critical components (KEEP)
        2. Corrupt directories (REMOVE)
        3. Requirements files (CONSOLIDATE)
        4. Cache files (ARCHIVE or REMOVE based on age)
        5. Remove patterns (REMOVE)
        6. Default to KEEP
        
        Args:
            file_info: FileInfo object to categorize
            
        Returns:
            FileCategory enum value (KEEP/REMOVE/CONSOLIDATE/ARCHIVE)
            
        Example:
            >>> categorizer = FileCategorizer()
            >>> file_info = FileInfo(path=Path("agentic_sdlc/lib/test.py"), ...)
            >>> category = categorizer.categorize(file_info)
            >>> print(category)  # FileCategory.REMOVE
        """
        path = file_info.path
        
        # Check if file is in a critical component path
        if self.is_critical(path):
            file_info.is_critical = True
            file_info.reason = "Critical component - must be preserved"
            return FileCategory.KEEP
        
        # Check if file is in a corrupt directory
        if self.is_corrupt_directory(path):
            file_info.reason = "Corrupt directory - should be removed"
            return FileCategory.REMOVE
        
        # Check if file is a requirements file to consolidate
        if self._is_requirements_file(path):
            file_info.reason = "Requirements file - consolidate into pyproject.toml"
            return FileCategory.CONSOLIDATE
        
        # Check if file is in a cache directory
        if self.is_cache_file(path):
            # Check age for archival
            if self._should_archive_by_age(file_info):
                file_info.reason = f"Cache file older than {self.cache_age_threshold} days - archive"
                return FileCategory.ARCHIVE
            else:
                file_info.reason = "Cache file - remove"
                return FileCategory.REMOVE
        
        # Check if file matches remove patterns
        if self._matches_remove_pattern(path):
            file_info.reason = f"Matches remove pattern - {path.name}"
            return FileCategory.REMOVE
        
        # Default to KEEP
        file_info.reason = "No removal rule matched - keep by default"
        return FileCategory.KEEP
    
    def is_critical(self, file_path: Path) -> bool:
        """Check if file is a critical component that must be preserved.
        
        Critical components include:
        - Files in core/, intelligence/, infrastructure/, orchestration/
        - Files in defaults/ (excluding projects/ subdirectory)
        - Files in docs/, .agent/, .kiro/, tests/, bin/, scripts/
        - Root configuration files (pyproject.toml, package.json, etc.)
        
        Args:
            file_path: Path to check
            
        Returns:
            True if file is critical, False otherwise
            
        Example:
            >>> categorizer = FileCategorizer()
            >>> categorizer.is_critical(Path("agentic_sdlc/core/main.py"))
            True
            >>> categorizer.is_critical(Path("agentic_sdlc/lib/test.py"))
            False
        """
        # Convert to string for easier matching
        path_str = str(file_path)
        path_parts = file_path.parts
        
        # Check if it's a critical root file
        if file_path.name in self.CRITICAL_ROOT_FILES:
            # Only if it's in the root (not nested)
            if len(path_parts) == 1 or (len(path_parts) == 2 and path_parts[0] in [".", ".."]):
                return True
        
        # Check if path starts with any critical path pattern
        for critical_path in self.critical_paths:
            critical_parts = Path(critical_path).parts
            
            # Check if file path starts with critical path
            if len(path_parts) >= len(critical_parts):
                if path_parts[:len(critical_parts)] == critical_parts:
                    # Special handling for defaults/ - exclude projects/
                    if critical_path == "agentic_sdlc/defaults":
                        # Check if path contains projects/ subdirectory
                        if len(path_parts) > len(critical_parts):
                            next_part = path_parts[len(critical_parts)]
                            if next_part in self.DEFAULTS_EXCLUDE:
                                return False
                    return True
        
        return False
    
    def is_corrupt_directory(self, dir_path: Path) -> bool:
        """Check if directory is corrupt (has _corrupt_ suffix).
        
        Corrupt directories are identified by the presence of "_corrupt_"
        in any part of the path. These are typically damaged or duplicate
        build artifacts that should be removed.
        
        Args:
            dir_path: Path to check
            
        Returns:
            True if directory is corrupt, False otherwise
            
        Example:
            >>> categorizer = FileCategorizer()
            >>> categorizer.is_corrupt_directory(Path("build_corrupt_20260131"))
            True
            >>> categorizer.is_corrupt_directory(Path("build"))
            False
        """
        path_str = str(dir_path)
        
        # Check if any part of the path contains "_corrupt_"
        for part in dir_path.parts:
            if "_corrupt_" in part:
                return True
        
        return False
    
    def is_cache_file(self, file_path: Path) -> bool:
        """Check if file is a cache file.
        
        Cache files are identified by being in cache directories like:
        - __pycache__/
        - .hypothesis/
        - .brain/
        - .pytest_cache/
        - .mypy_cache/
        - .ruff_cache/
        
        Args:
            file_path: Path to check
            
        Returns:
            True if file is a cache file, False otherwise
            
        Example:
            >>> categorizer = FileCategorizer()
            >>> categorizer.is_cache_file(Path("__pycache__/main.cpython-310.pyc"))
            True
            >>> categorizer.is_cache_file(Path("src/main.py"))
            False
        """
        path_parts = file_path.parts
        
        # Check if any part of the path matches cache patterns
        for part in path_parts:
            if part in self.CACHE_PATTERNS:
                return True
        
        return False
    
    def is_empty_directory(self, dir_info: DirectoryInfo) -> bool:
        """Check if directory is empty or contains only .DS_Store/.gitkeep files.
        
        Empty directories are candidates for removal unless they are in the
        critical empty directories list (logs/, states/, data/).
        
        Args:
            dir_info: DirectoryInfo object to check
            
        Returns:
            True if directory is empty and not critical, False otherwise
            
        Example:
            >>> categorizer = FileCategorizer()
            >>> dir_info = DirectoryInfo(path=Path("empty_dir"), size=0, file_count=0, is_empty=True)
            >>> categorizer.is_empty_directory(dir_info)
            True
        """
        # If directory is not marked as empty, return False
        if not dir_info.is_empty:
            return False
        
        # Check if directory is in critical empty dirs list
        dir_name = dir_info.path.name
        if dir_name in self.critical_empty_dirs:
            return False
        
        return True
    
    def _is_requirements_file(self, file_path: Path) -> bool:
        """Check if file is a requirements file that should be consolidated.
        
        Args:
            file_path: Path to check
            
        Returns:
            True if file is a requirements file, False otherwise
        """
        filename = file_path.name
        
        # Match requirements*.txt pattern
        if filename.startswith("requirements") and filename.endswith(".txt"):
            return True
        
        return False
    
    def _should_archive_by_age(self, file_info: FileInfo) -> bool:
        """Check if cache file should be archived based on age.
        
        Files in .brain/ older than cache_age_threshold days should be archived.
        Other cache files should be removed regardless of age.
        
        Args:
            file_info: FileInfo object to check
            
        Returns:
            True if file should be archived, False if it should be removed
        """
        # Only .brain/ files are archived by age
        if ".brain" not in str(file_info.path):
            return False
        
        # Check if file is older than threshold
        age_threshold = datetime.now() - timedelta(days=self.cache_age_threshold)
        
        if file_info.modified_time < age_threshold:
            return True
        
        return False
    
    def _matches_remove_pattern(self, file_path: Path) -> bool:
        """Check if file matches any remove pattern.
        
        Args:
            file_path: Path to check
            
        Returns:
            True if file matches a remove pattern, False otherwise
        """
        import fnmatch
        
        filename = file_path.name
        
        for pattern in self.REMOVE_PATTERNS:
            if fnmatch.fnmatch(filename, pattern):
                return True
        
        return False
    
    def categorize_directory(self, dir_info: DirectoryInfo) -> FileCategory:
        """Categorize a directory based on its properties.
        
        Args:
            dir_info: DirectoryInfo object to categorize
            
        Returns:
            FileCategory enum value
        """
        path = dir_info.path
        
        # Check if directory is critical
        if self.is_critical(path):
            dir_info.is_critical = True
            return FileCategory.KEEP
        
        # Check if directory is corrupt
        if self.is_corrupt_directory(path):
            return FileCategory.REMOVE
        
        # Check if directory is empty and should be removed
        if self.is_empty_directory(dir_info):
            return FileCategory.REMOVE
        
        # Check if directory is a cache directory
        if path.name in self.CACHE_PATTERNS:
            return FileCategory.ARCHIVE
        
        # Default to KEEP
        return FileCategory.KEEP
