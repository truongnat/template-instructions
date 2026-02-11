"""
Unit tests for FileCategorizer service.

Tests specific file categorizations, critical component list,
and edge cases (symlinks, special files).

Requirements: 6.1, 6.2, 6.3, 6.4
"""

import pytest
from pathlib import Path
from datetime import datetime, timedelta

from scripts.cleanup.categorizer import FileCategorizer
from scripts.cleanup.models import FileInfo, DirectoryInfo, FileCategory


class TestFileCategorizer:
    """Test suite for FileCategorizer class."""
    
    def test_categorizer_initialization(self):
        """Test FileCategorizer initializes with correct defaults."""
        categorizer = FileCategorizer()
        
        assert categorizer.cache_age_threshold == 30
        assert len(categorizer.critical_paths) > 0
        assert len(categorizer.critical_empty_dirs) > 0
    
    def test_categorizer_custom_cache_threshold(self):
        """Test FileCategorizer accepts custom cache age threshold."""
        categorizer = FileCategorizer(cache_age_threshold=60)
        
        assert categorizer.cache_age_threshold == 60


class TestCriticalComponentIdentification:
    """Test critical component identification (Requirements 6.1, 6.2, 6.3)."""
    
    def test_core_directory_is_critical(self):
        """Test files in agentic_sdlc/core/ are identified as critical."""
        categorizer = FileCategorizer()
        
        test_paths = [
            Path("agentic_sdlc/core/main.py"),
            Path("agentic_sdlc/core/utils/helper.py"),
            Path("agentic_sdlc/core/models/base.py"),
        ]
        
        for path in test_paths:
            assert categorizer.is_critical(path), f"{path} should be critical"
    
    def test_intelligence_directory_is_critical(self):
        """Test files in agentic_sdlc/intelligence/ are identified as critical."""
        categorizer = FileCategorizer()
        
        test_paths = [
            Path("agentic_sdlc/intelligence/agent.py"),
            Path("agentic_sdlc/intelligence/reasoning/logic.py"),
        ]
        
        for path in test_paths:
            assert categorizer.is_critical(path), f"{path} should be critical"
    
    def test_infrastructure_directory_is_critical(self):
        """Test files in agentic_sdlc/infrastructure/ are identified as critical."""
        categorizer = FileCategorizer()
        
        path = Path("agentic_sdlc/infrastructure/database.py")
        assert categorizer.is_critical(path)
    
    def test_orchestration_directory_is_critical(self):
        """Test files in agentic_sdlc/orchestration/ are identified as critical."""
        categorizer = FileCategorizer()
        
        path = Path("agentic_sdlc/orchestration/workflow.py")
        assert categorizer.is_critical(path)
    
    def test_defaults_directory_is_critical(self):
        """Test files in agentic_sdlc/defaults/ are identified as critical."""
        categorizer = FileCategorizer()
        
        path = Path("agentic_sdlc/defaults/config.py")
        assert categorizer.is_critical(path)
    
    def test_defaults_projects_excluded(self):
        """Test files in agentic_sdlc/defaults/projects/ are NOT critical."""
        categorizer = FileCategorizer()
        
        test_paths = [
            Path("agentic_sdlc/defaults/projects/example.py"),
            Path("agentic_sdlc/defaults/projects/demo/main.py"),
        ]
        
        for path in test_paths:
            assert not categorizer.is_critical(path), f"{path} should not be critical"
    
    def test_docs_directory_is_critical(self):
        """Test files in docs/ are identified as critical."""
        categorizer = FileCategorizer()
        
        test_paths = [
            Path("docs/README.md"),
            Path("docs/api/reference.md"),
        ]
        
        for path in test_paths:
            assert categorizer.is_critical(path), f"{path} should be critical"
    
    def test_agent_directory_is_critical(self):
        """Test files in .agent/ are identified as critical."""
        categorizer = FileCategorizer()
        
        path = Path(".agent/config.json")
        assert categorizer.is_critical(path)
    
    def test_kiro_directory_is_critical(self):
        """Test files in .kiro/ are identified as critical."""
        categorizer = FileCategorizer()
        
        path = Path(".kiro/settings.json")
        assert categorizer.is_critical(path)
    
    def test_tests_directory_is_critical(self):
        """Test files in tests/ are identified as critical."""
        categorizer = FileCategorizer()
        
        test_paths = [
            Path("tests/test_main.py"),
            Path("tests/unit/test_helper.py"),
        ]
        
        for path in test_paths:
            assert categorizer.is_critical(path), f"{path} should be critical"
    
    def test_bin_directory_is_critical(self):
        """Test files in bin/ are identified as critical."""
        categorizer = FileCategorizer()
        
        path = Path("bin/startup.sh")
        assert categorizer.is_critical(path)
    
    def test_scripts_directory_is_critical(self):
        """Test files in scripts/ are identified as critical."""
        categorizer = FileCategorizer()
        
        test_paths = [
            Path("scripts/cleanup.py"),
            Path("scripts/cleanup/categorizer.py"),
        ]
        
        for path in test_paths:
            assert categorizer.is_critical(path), f"{path} should be critical"
    
    def test_root_config_files_are_critical(self):
        """Test root configuration files are identified as critical."""
        categorizer = FileCategorizer()
        
        root_files = [
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
        ]
        
        for filename in root_files:
            path = Path(filename)
            assert categorizer.is_critical(path), f"{filename} should be critical"
    
    def test_nested_root_files_not_critical(self):
        """Test root config files in subdirectories are NOT critical."""
        categorizer = FileCategorizer()
        
        # pyproject.toml in subdirectory should not be critical
        path = Path("subdir/pyproject.toml")
        assert not categorizer.is_critical(path)
    
    def test_non_critical_paths(self):
        """Test files outside critical paths are not identified as critical."""
        categorizer = FileCategorizer()
        
        non_critical_paths = [
            Path("agentic_sdlc/lib/vendor.py"),
            Path("random_file.py"),
            Path("temp/data.json"),
        ]
        
        for path in non_critical_paths:
            assert not categorizer.is_critical(path), f"{path} should not be critical"


class TestCorruptDirectoryIdentification:
    """Test corrupt directory identification (Requirement 1.1, 1.2)."""
    
    def test_corrupt_suffix_identified(self):
        """Test directories with _corrupt_ suffix are identified."""
        categorizer = FileCategorizer()
        
        corrupt_paths = [
            Path("build_corrupt_20260131"),
            Path("agentic_sdlc.egg-info_corrupt_20260131"),
            Path("dist_corrupt_backup"),
        ]
        
        for path in corrupt_paths:
            assert categorizer.is_corrupt_directory(path), f"{path} should be corrupt"
    
    def test_nested_corrupt_directory(self):
        """Test nested paths with _corrupt_ are identified."""
        categorizer = FileCategorizer()
        
        path = Path("build_corrupt_20260131/lib/module.py")
        assert categorizer.is_corrupt_directory(path)
    
    def test_normal_directories_not_corrupt(self):
        """Test normal directories are not identified as corrupt."""
        categorizer = FileCategorizer()
        
        normal_paths = [
            Path("build"),
            Path("dist"),
            Path("agentic_sdlc.egg-info"),
        ]
        
        for path in normal_paths:
            assert not categorizer.is_corrupt_directory(path), f"{path} should not be corrupt"


class TestCacheFileIdentification:
    """Test cache file identification (Requirement 3.1, 3.4)."""
    
    def test_pycache_identified(self):
        """Test __pycache__ files are identified as cache."""
        categorizer = FileCategorizer()
        
        cache_paths = [
            Path("__pycache__/main.cpython-310.pyc"),
            Path("src/__pycache__/utils.cpython-311.pyc"),
        ]
        
        for path in cache_paths:
            assert categorizer.is_cache_file(path), f"{path} should be cache"
    
    def test_hypothesis_cache_identified(self):
        """Test .hypothesis files are identified as cache."""
        categorizer = FileCategorizer()
        
        cache_paths = [
            Path(".hypothesis/examples/test.py"),
            Path(".hypothesis/constants/data"),
        ]
        
        for path in cache_paths:
            assert categorizer.is_cache_file(path), f"{path} should be cache"
    
    def test_brain_cache_identified(self):
        """Test .brain files are identified as cache."""
        categorizer = FileCategorizer()
        
        cache_paths = [
            Path(".brain/sessions/session.json"),
            Path(".brain/cache/data.db"),
        ]
        
        for path in cache_paths:
            assert categorizer.is_cache_file(path), f"{path} should be cache"
    
    def test_pytest_cache_identified(self):
        """Test .pytest_cache files are identified as cache."""
        categorizer = FileCategorizer()
        
        path = Path(".pytest_cache/v/cache/nodeids")
        assert categorizer.is_cache_file(path)
    
    def test_mypy_cache_identified(self):
        """Test .mypy_cache files are identified as cache."""
        categorizer = FileCategorizer()
        
        path = Path(".mypy_cache/3.10/main.data.json")
        assert categorizer.is_cache_file(path)
    
    def test_ruff_cache_identified(self):
        """Test .ruff_cache files are identified as cache."""
        categorizer = FileCategorizer()
        
        path = Path(".ruff_cache/content/abc123")
        assert categorizer.is_cache_file(path)
    
    def test_non_cache_files(self):
        """Test normal files are not identified as cache."""
        categorizer = FileCategorizer()
        
        non_cache_paths = [
            Path("src/main.py"),
            Path("tests/test_main.py"),
            Path("README.md"),
        ]
        
        for path in non_cache_paths:
            assert not categorizer.is_cache_file(path), f"{path} should not be cache"


class TestRequirementsFileIdentification:
    """Test requirements file identification (Requirement 4.1)."""
    
    def test_requirements_txt_identified(self):
        """Test requirements.txt files are identified for consolidation."""
        categorizer = FileCategorizer()
        
        file_info = FileInfo(
            path=Path("requirements.txt"),
            size=1024,
            modified_time=datetime.now()
        )
        
        category = categorizer.categorize(file_info)
        assert category == FileCategory.CONSOLIDATE
    
    def test_requirements_variants_identified(self):
        """Test various requirements*.txt patterns are identified."""
        categorizer = FileCategorizer()
        
        requirements_files = [
            "requirements.txt",
            "requirements-dev.txt",
            "requirements_tools.txt",
            "requirements_test.txt",
        ]
        
        for filename in requirements_files:
            file_info = FileInfo(
                path=Path(filename),
                size=512,
                modified_time=datetime.now()
            )
            
            category = categorizer.categorize(file_info)
            assert category == FileCategory.CONSOLIDATE, f"{filename} should be CONSOLIDATE"


class TestRemovePatterns:
    """Test file removal patterns (Requirement 1.3)."""
    
    def test_pyc_files_removed(self):
        """Test .pyc files are categorized as REMOVE."""
        categorizer = FileCategorizer()
        
        file_info = FileInfo(
            path=Path("module.pyc"),
            size=2048,
            modified_time=datetime.now()
        )
        
        category = categorizer.categorize(file_info)
        assert category == FileCategory.REMOVE
    
    def test_pyo_files_removed(self):
        """Test .pyo files are categorized as REMOVE."""
        categorizer = FileCategorizer()
        
        file_info = FileInfo(
            path=Path("module.pyo"),
            size=2048,
            modified_time=datetime.now()
        )
        
        category = categorizer.categorize(file_info)
        assert category == FileCategory.REMOVE
    
    def test_ds_store_removed(self):
        """Test .DS_Store files are categorized as REMOVE."""
        categorizer = FileCategorizer()
        
        file_info = FileInfo(
            path=Path(".DS_Store"),
            size=4096,
            modified_time=datetime.now()
        )
        
        category = categorizer.categorize(file_info)
        assert category == FileCategory.REMOVE
    
    def test_vim_swap_files_removed(self):
        """Test vim swap files are categorized as REMOVE."""
        categorizer = FileCategorizer()
        
        swap_files = [
            Path("file.swp"),
            Path("file.swo"),
            Path("file~"),
        ]
        
        for path in swap_files:
            file_info = FileInfo(
                path=path,
                size=1024,
                modified_time=datetime.now()
            )
            
            category = categorizer.categorize(file_info)
            assert category == FileCategory.REMOVE, f"{path} should be REMOVE"


class TestCacheAgeBasedArchival:
    """Test cache file archival based on age (Requirement 3.2)."""
    
    def test_old_brain_files_archived(self):
        """Test .brain files older than threshold are archived."""
        categorizer = FileCategorizer(cache_age_threshold=30)
        
        # File older than 30 days
        old_date = datetime.now() - timedelta(days=35)
        
        file_info = FileInfo(
            path=Path(".brain/sessions/old_session.json"),
            size=1024,
            modified_time=old_date
        )
        
        category = categorizer.categorize(file_info)
        assert category == FileCategory.ARCHIVE
    
    def test_recent_brain_files_removed(self):
        """Test recent .brain files are removed (not archived)."""
        categorizer = FileCategorizer(cache_age_threshold=30)
        
        # File less than 30 days old
        recent_date = datetime.now() - timedelta(days=10)
        
        file_info = FileInfo(
            path=Path(".brain/sessions/recent_session.json"),
            size=1024,
            modified_time=recent_date
        )
        
        category = categorizer.categorize(file_info)
        assert category == FileCategory.REMOVE
    
    def test_non_brain_cache_always_removed(self):
        """Test non-.brain cache files are removed regardless of age."""
        categorizer = FileCategorizer(cache_age_threshold=30)
        
        # Old file in __pycache__
        old_date = datetime.now() - timedelta(days=100)
        
        file_info = FileInfo(
            path=Path("__pycache__/old_module.pyc"),
            size=2048,
            modified_time=old_date
        )
        
        category = categorizer.categorize(file_info)
        assert category == FileCategory.REMOVE  # Not archived


class TestEmptyDirectoryIdentification:
    """Test empty directory identification (Requirement 11.1, 11.2, 11.3)."""
    
    def test_empty_directory_identified(self):
        """Test truly empty directories are identified."""
        categorizer = FileCategorizer()
        
        dir_info = DirectoryInfo(
            path=Path("empty_dir"),
            size=0,
            file_count=0,
            is_empty=True
        )
        
        assert categorizer.is_empty_directory(dir_info)
    
    def test_non_empty_directory_not_identified(self):
        """Test non-empty directories are not identified as empty."""
        categorizer = FileCategorizer()
        
        dir_info = DirectoryInfo(
            path=Path("full_dir"),
            size=10240,
            file_count=5,
            is_empty=False
        )
        
        assert not categorizer.is_empty_directory(dir_info)
    
    def test_critical_empty_dirs_preserved(self):
        """Test critical empty directories (logs, states, data) are preserved."""
        categorizer = FileCategorizer()
        
        critical_dirs = ["logs", "states", "data"]
        
        for dir_name in critical_dirs:
            dir_info = DirectoryInfo(
                path=Path(dir_name),
                size=0,
                file_count=0,
                is_empty=True
            )
            
            assert not categorizer.is_empty_directory(dir_info), \
                f"{dir_name} should be preserved"


class TestCategorizationPriority:
    """Test categorization rule priority (Requirements 6.1, 6.2, 6.3, 6.4)."""
    
    def test_critical_overrides_corrupt(self):
        """Test critical components are kept even if they match corrupt pattern."""
        categorizer = FileCategorizer()
        
        # Hypothetical: critical file with corrupt in name (edge case)
        file_info = FileInfo(
            path=Path("agentic_sdlc/core/backup_corrupt_handler.py"),
            size=2048,
            modified_time=datetime.now()
        )
        
        category = categorizer.categorize(file_info)
        # Critical path should take priority
        assert category == FileCategory.KEEP
        assert file_info.is_critical
    
    def test_critical_overrides_cache_pattern(self):
        """Test critical components are kept even if in cache-like directory."""
        categorizer = FileCategorizer()
        
        # File in critical path that happens to be named like cache
        file_info = FileInfo(
            path=Path("agentic_sdlc/core/__pycache__/important.py"),
            size=1024,
            modified_time=datetime.now()
        )
        
        category = categorizer.categorize(file_info)
        # Critical path should take priority over cache pattern
        assert category == FileCategory.KEEP
        assert file_info.is_critical
    
    def test_corrupt_overrides_requirements(self):
        """Test corrupt directories are removed even if they contain requirements files."""
        categorizer = FileCategorizer()
        
        file_info = FileInfo(
            path=Path("build_corrupt_20260131/requirements.txt"),
            size=512,
            modified_time=datetime.now()
        )
        
        category = categorizer.categorize(file_info)
        # Corrupt should take priority over consolidate
        assert category == FileCategory.REMOVE


class TestCategorizationReasons:
    """Test that categorization provides clear reasons."""
    
    def test_critical_component_reason(self):
        """Test critical components have appropriate reason."""
        categorizer = FileCategorizer()
        
        file_info = FileInfo(
            path=Path("agentic_sdlc/core/main.py"),
            size=1024,
            modified_time=datetime.now()
        )
        
        categorizer.categorize(file_info)
        assert "Critical component" in file_info.reason
    
    def test_corrupt_directory_reason(self):
        """Test corrupt directories have appropriate reason."""
        categorizer = FileCategorizer()
        
        file_info = FileInfo(
            path=Path("build_corrupt_20260131/file.py"),
            size=1024,
            modified_time=datetime.now()
        )
        
        categorizer.categorize(file_info)
        assert "Corrupt directory" in file_info.reason
    
    def test_requirements_consolidation_reason(self):
        """Test requirements files have appropriate reason."""
        categorizer = FileCategorizer()
        
        file_info = FileInfo(
            path=Path("requirements.txt"),
            size=512,
            modified_time=datetime.now()
        )
        
        categorizer.categorize(file_info)
        assert "consolidate" in file_info.reason.lower()
    
    def test_cache_file_reason(self):
        """Test cache files have appropriate reason."""
        categorizer = FileCategorizer()
        
        file_info = FileInfo(
            path=Path("__pycache__/module.pyc"),
            size=2048,
            modified_time=datetime.now()
        )
        
        categorizer.categorize(file_info)
        assert "cache" in file_info.reason.lower()


class TestDirectoryCategorization:
    """Test directory categorization method."""
    
    def test_critical_directory_kept(self):
        """Test critical directories are categorized as KEEP."""
        categorizer = FileCategorizer()
        
        dir_info = DirectoryInfo(
            path=Path("agentic_sdlc/core"),
            size=102400,
            file_count=50,
            is_empty=False
        )
        
        category = categorizer.categorize_directory(dir_info)
        assert category == FileCategory.KEEP
        assert dir_info.is_critical
    
    def test_corrupt_directory_removed(self):
        """Test corrupt directories are categorized as REMOVE."""
        categorizer = FileCategorizer()
        
        dir_info = DirectoryInfo(
            path=Path("build_corrupt_20260131"),
            size=51200,
            file_count=25,
            is_empty=False
        )
        
        category = categorizer.categorize_directory(dir_info)
        assert category == FileCategory.REMOVE
    
    def test_empty_directory_removed(self):
        """Test empty non-critical directories are categorized as REMOVE."""
        categorizer = FileCategorizer()
        
        dir_info = DirectoryInfo(
            path=Path("temp_empty"),
            size=0,
            file_count=0,
            is_empty=True
        )
        
        category = categorizer.categorize_directory(dir_info)
        assert category == FileCategory.REMOVE
    
    def test_cache_directory_archived(self):
        """Test cache directories are categorized as ARCHIVE."""
        categorizer = FileCategorizer()
        
        dir_info = DirectoryInfo(
            path=Path(".hypothesis"),
            size=20480,
            file_count=100,
            is_empty=False
        )
        
        category = categorizer.categorize_directory(dir_info)
        assert category == FileCategory.ARCHIVE


class TestEdgeCases:
    """Test edge cases and special file types (Requirement 6.4)."""
    
    def test_empty_path(self):
        """Test handling of empty path."""
        categorizer = FileCategorizer()
        
        file_info = FileInfo(
            path=Path(""),
            size=0,
            modified_time=datetime.now()
        )
        
        # Should not crash, should default to KEEP
        category = categorizer.categorize(file_info)
        assert category == FileCategory.KEEP
    
    def test_single_character_filename(self):
        """Test handling of single character filenames."""
        categorizer = FileCategorizer()
        
        file_info = FileInfo(
            path=Path("a"),
            size=10,
            modified_time=datetime.now()
        )
        
        category = categorizer.categorize(file_info)
        assert category == FileCategory.KEEP
    
    def test_very_long_path(self):
        """Test handling of very long paths."""
        categorizer = FileCategorizer()
        
        # Create a very long path
        long_path_parts = ["dir"] * 50 + ["file.py"]
        long_path = Path(*long_path_parts)
        
        file_info = FileInfo(
            path=long_path,
            size=1024,
            modified_time=datetime.now()
        )
        
        # Should not crash
        category = categorizer.categorize(file_info)
        assert category in [FileCategory.KEEP, FileCategory.REMOVE, 
                           FileCategory.CONSOLIDATE, FileCategory.ARCHIVE]
    
    def test_path_with_dots(self):
        """Test handling of paths with dots (., ..)."""
        categorizer = FileCategorizer()
        
        file_info = FileInfo(
            path=Path("./agentic_sdlc/core/main.py"),
            size=1024,
            modified_time=datetime.now()
        )
        
        # Should still recognize as critical
        assert categorizer.is_critical(file_info.path)
    
    def test_hidden_files(self):
        """Test handling of hidden files (starting with .)."""
        categorizer = FileCategorizer()
        
        # Hidden file that's not in critical list
        file_info = FileInfo(
            path=Path(".hidden_file"),
            size=512,
            modified_time=datetime.now()
        )
        
        category = categorizer.categorize(file_info)
        # Should default to KEEP (not matching any remove pattern)
        assert category == FileCategory.KEEP
    
    def test_file_with_no_extension(self):
        """Test handling of files without extensions."""
        categorizer = FileCategorizer()
        
        file_info = FileInfo(
            path=Path("Makefile"),
            size=1024,
            modified_time=datetime.now()
        )
        
        category = categorizer.categorize(file_info)
        assert category == FileCategory.KEEP
    
    def test_file_with_multiple_dots(self):
        """Test handling of files with multiple dots in name."""
        categorizer = FileCategorizer()
        
        file_info = FileInfo(
            path=Path("file.test.backup.py"),
            size=1024,
            modified_time=datetime.now()
        )
        
        category = categorizer.categorize(file_info)
        assert category == FileCategory.KEEP
    
    def test_unicode_in_path(self):
        """Test handling of unicode characters in paths."""
        categorizer = FileCategorizer()
        
        file_info = FileInfo(
            path=Path("测试/файл.py"),
            size=1024,
            modified_time=datetime.now()
        )
        
        # Should not crash
        category = categorizer.categorize(file_info)
        assert category in [FileCategory.KEEP, FileCategory.REMOVE, 
                           FileCategory.CONSOLIDATE, FileCategory.ARCHIVE]
    
    def test_spaces_in_path(self):
        """Test handling of spaces in paths."""
        categorizer = FileCategorizer()
        
        file_info = FileInfo(
            path=Path("my folder/my file.py"),
            size=1024,
            modified_time=datetime.now()
        )
        
        category = categorizer.categorize(file_info)
        assert category == FileCategory.KEEP
    
    def test_special_characters_in_filename(self):
        """Test handling of special characters in filenames."""
        categorizer = FileCategorizer()
        
        special_files = [
            Path("file@2024.py"),
            Path("file#backup.py"),
            Path("file$temp.py"),
        ]
        
        for path in special_files:
            file_info = FileInfo(
                path=path,
                size=1024,
                modified_time=datetime.now()
            )
            
            # Should not crash
            category = categorizer.categorize(file_info)
            assert category in [FileCategory.KEEP, FileCategory.REMOVE, 
                               FileCategory.CONSOLIDATE, FileCategory.ARCHIVE]


class TestDefaultBehavior:
    """Test default categorization behavior."""
    
    def test_unknown_file_defaults_to_keep(self):
        """Test files that don't match any rule default to KEEP."""
        categorizer = FileCategorizer()
        
        file_info = FileInfo(
            path=Path("random/unknown/file.xyz"),
            size=1024,
            modified_time=datetime.now()
        )
        
        category = categorizer.categorize(file_info)
        assert category == FileCategory.KEEP
        assert "No removal rule matched" in file_info.reason
    
    def test_unknown_directory_defaults_to_keep(self):
        """Test directories that don't match any rule default to KEEP."""
        categorizer = FileCategorizer()
        
        dir_info = DirectoryInfo(
            path=Path("random_directory"),
            size=10240,
            file_count=10,
            is_empty=False
        )
        
        category = categorizer.categorize_directory(dir_info)
        assert category == FileCategory.KEEP
