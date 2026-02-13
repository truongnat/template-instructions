"""
Property-based tests for test directory structure mirroring.

This module tests that the test directory structure properly mirrors
the source code structure in agentic_sdlc/.
"""

import unittest
from pathlib import Path
from typing import List, Set

try:
    from hypothesis import given, strategies as st, settings, assume
    HYPOTHESIS_AVAILABLE = True
except ImportError:
    HYPOTHESIS_AVAILABLE = False
    
    def given(*args, **kwargs):
        def decorator(func):
            return func
        return decorator
    
    class MockStrategies:
        def sampled_from(self, seq): 
            return lambda: seq[0] if seq else None
    
    st = MockStrategies()
    
    def settings(**kwargs):
        def decorator(func):
            return func
        return decorator


def get_source_directories(base_path: Path) -> Set[Path]:
    """
    Get all directories in the source code tree.
    
    Args:
        base_path: The base path to search from (agentic_sdlc/)
        
    Returns:
        Set of relative directory paths
    """
    directories = set()
    
    # Exclude certain directories that shouldn't be mirrored
    exclude_dirs = {'.brain', '__pycache__', 'lib', 'defaults', 'testing'}
    
    if not base_path.exists():
        return directories
    
    for item in base_path.rglob('*'):
        if item.is_dir():
            # Skip excluded directories
            if any(excluded in item.parts for excluded in exclude_dirs):
                continue
            
            # Get relative path from base
            rel_path = item.relative_to(base_path)
            directories.add(rel_path)
    
    return directories


def get_test_directories(base_path: Path) -> Set[Path]:
    """
    Get all directories in the test tree.
    
    Args:
        base_path: The base path to search from (tests/unit/)
        
    Returns:
        Set of relative directory paths
    """
    directories = set()
    
    # Exclude __pycache__ directories
    exclude_dirs = {'__pycache__'}
    
    if not base_path.exists():
        return directories
    
    for item in base_path.rglob('*'):
        if item.is_dir():
            # Skip excluded directories
            if any(excluded in item.parts for excluded in exclude_dirs):
                continue
            
            # Get relative path from base
            rel_path = item.relative_to(base_path)
            directories.add(rel_path)
    
    return directories


def check_directory_mirroring(source_dir: Path, test_dir: Path) -> tuple[bool, List[str]]:
    """
    Check if test directory structure mirrors source directory structure.
    
    Args:
        source_dir: Path to source directory (agentic_sdlc/)
        test_dir: Path to test directory (tests/unit/)
        
    Returns:
        Tuple of (is_mirrored, missing_directories)
    """
    source_dirs = get_source_directories(source_dir)
    test_dirs = get_test_directories(test_dir)
    
    # Find directories that exist in source but not in tests
    missing_dirs = []
    for src_dir in sorted(source_dirs):
        if src_dir not in test_dirs:
            missing_dirs.append(str(src_dir))
    
    is_mirrored = len(missing_dirs) == 0
    return is_mirrored, missing_dirs


class TestDirectoryStructureMirroring(unittest.TestCase):
    """Property-based tests for directory structure mirroring."""
    
    def setUp(self):
        """Set up test fixtures."""
        # Get the project root (assuming tests/ is at project root)
        self.project_root = Path(__file__).parent.parent.parent
        self.source_dir = self.project_root / "agentic_sdlc"
        self.test_dir = self.project_root / "tests" / "unit"
    
    def test_property_3_test_directory_structure_mirroring(self):
        """
        Feature: sdlc-kit-improvements
        Property 3: Test Directory Structure Mirroring
        
        For any source code directory in agentic_sdlc/, there should exist
        a corresponding test directory in tests/unit/ with the same relative
        path structure.
        
        **Validates: Requirements 4.2**
        """
        # Check that source and test directories exist
        self.assertTrue(
            self.source_dir.exists(),
            f"Source directory does not exist: {self.source_dir}"
        )
        self.assertTrue(
            self.test_dir.exists(),
            f"Test directory does not exist: {self.test_dir}"
        )
        
        # Check directory mirroring
        is_mirrored, missing_dirs = check_directory_mirroring(
            self.source_dir,
            self.test_dir
        )
        
        # Assert that all source directories have corresponding test directories
        self.assertTrue(
            is_mirrored,
            f"Test directory structure does not mirror source structure. "
            f"Missing test directories for: {', '.join(missing_dirs)}"
        )
    
    @settings(max_examples=10)
    @given(st.sampled_from([
        Path("core"),
        Path("core/brain"),
        Path("core/cli"),
        Path("core/utils"),
        Path("infrastructure"),
        Path("infrastructure/automation"),
        Path("infrastructure/bridge"),
        Path("infrastructure/engine"),
        Path("infrastructure/lifecycle"),
        Path("intelligence"),
        Path("intelligence/collaborating"),
        Path("intelligence/learning"),
        Path("intelligence/monitoring"),
        Path("intelligence/reasoning"),
        Path("orchestration"),
        Path("orchestration/agents"),
        Path("orchestration/api_model_management"),
        Path("orchestration/cli"),
        Path("orchestration/config"),
        Path("orchestration/engine"),
        Path("orchestration/exceptions"),
        Path("orchestration/interfaces"),
        Path("orchestration/models"),
        Path("orchestration/testing"),
        Path("orchestration/utils"),
    ]))
    def test_property_3_specific_directory_mirroring(self, rel_path):
        """
        Feature: sdlc-kit-improvements
        Property 3: Test Directory Structure Mirroring (Specific Directories)
        
        For any specific source code directory in agentic_sdlc/, verify that
        a corresponding test directory exists in tests/unit/.
        
        **Validates: Requirements 4.2**
        """
        if not HYPOTHESIS_AVAILABLE:
            self.skipTest("Hypothesis not available")
        
        source_path = self.source_dir / rel_path
        test_path = self.test_dir / rel_path
        
        # If source directory exists, test directory should also exist
        if source_path.exists() and source_path.is_dir():
            self.assertTrue(
                test_path.exists(),
                f"Test directory does not exist for source directory: {rel_path}"
            )
            self.assertTrue(
                test_path.is_dir(),
                f"Test path exists but is not a directory: {rel_path}"
            )
    
    def test_all_major_directories_mirrored(self):
        """
        Test that all major source directories have corresponding test directories.
        
        This is a specific test that checks the main structural directories.
        """
        major_dirs = [
            "core",
            "infrastructure",
            "intelligence",
            "orchestration",
        ]
        
        for dir_name in major_dirs:
            source_path = self.source_dir / dir_name
            test_path = self.test_dir / dir_name
            
            if source_path.exists():
                self.assertTrue(
                    test_path.exists(),
                    f"Major test directory missing: tests/unit/{dir_name}"
                )
    
    def test_subdirectories_mirrored(self):
        """
        Test that subdirectories within major directories are also mirrored.
        """
        # Check orchestration subdirectories
        orchestration_subdirs = [
            "agents",
            "api_model_management",
            "cli",
            "config",
            "engine",
            "exceptions",
            "interfaces",
            "models",
            "testing",
            "utils",
        ]
        
        for subdir in orchestration_subdirs:
            source_path = self.source_dir / "orchestration" / subdir
            test_path = self.test_dir / "orchestration" / subdir
            
            if source_path.exists():
                self.assertTrue(
                    test_path.exists(),
                    f"Orchestration subdirectory not mirrored: {subdir}"
                )
        
        # Check intelligence subdirectories
        intelligence_subdirs = [
            "collaborating",
            "learning",
            "monitoring",
            "reasoning",
        ]
        
        for subdir in intelligence_subdirs:
            source_path = self.source_dir / "intelligence" / subdir
            test_path = self.test_dir / "intelligence" / subdir
            
            if source_path.exists():
                self.assertTrue(
                    test_path.exists(),
                    f"Intelligence subdirectory not mirrored: {subdir}"
                )
        
        # Check infrastructure subdirectories
        infrastructure_subdirs = [
            "automation",
            "bridge",
            "engine",
            "lifecycle",
        ]
        
        for subdir in infrastructure_subdirs:
            source_path = self.source_dir / "infrastructure" / subdir
            test_path = self.test_dir / "infrastructure" / subdir
            
            if source_path.exists():
                self.assertTrue(
                    test_path.exists(),
                    f"Infrastructure subdirectory not mirrored: {subdir}"
                )
        
        # Check core subdirectories
        core_subdirs = [
            "brain",
            "cli",
            "utils",
        ]
        
        for subdir in core_subdirs:
            source_path = self.source_dir / "core" / subdir
            test_path = self.test_dir / "core" / subdir
            
            if source_path.exists():
                self.assertTrue(
                    test_path.exists(),
                    f"Core subdirectory not mirrored: {subdir}"
                )


if __name__ == '__main__':
    unittest.main()
