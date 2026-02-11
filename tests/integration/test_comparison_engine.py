"""
Integration tests for ComparisonEngine.

These tests verify the full comparison workflow from scanning to report generation,
including error handling and graceful degradation.
"""

import pytest
import tempfile
import shutil
from pathlib import Path

from agentic_sdlc.comparison import (
    ComparisonEngine,
    ComparisonEngineError,
)


class TestComparisonEngineIntegration:
    """Integration tests for ComparisonEngine."""
    
    @pytest.fixture
    def temp_project_dir(self):
        """Create a temporary project directory for testing."""
        temp_dir = tempfile.mkdtemp()
        project_path = Path(temp_dir) / "test_project"
        project_path.mkdir()
        
        # Create some basic structure
        (project_path / "src").mkdir()
        (project_path / "tests").mkdir()
        (project_path / "docs").mkdir()
        (project_path / "pyproject.toml").touch()
        (project_path / ".gitignore").touch()
        
        yield str(project_path)
        
        # Cleanup
        shutil.rmtree(temp_dir)
    
    @pytest.fixture
    def temp_v2_docs_dir(self):
        """Create a temporary v2 docs directory with sample documents."""
        temp_dir = tempfile.mkdtemp()
        v2_path = Path(temp_dir) / "v2"
        v2_path.mkdir()
        
        # Create sample SDLC_Improvement_Suggestions.md
        suggestions_content = """# SDLC Improvement Suggestions

## 1. **Clean Up & Organize lib Directory**

**Issue:** The project has a `lib/` directory with bundled dependencies.

**Recommendation:** Create requirements.txt and remove lib/.

**Priority:** High
**Estimated Time:** 2-3 hours

## 2. **Improve Documentation Structure**

**Issue:** Documentation is scattered.

**Recommendation:** Create docs/ directory with proper structure.

**Priority:** Medium
**Estimated Time:** 4-6 hours
"""
        (v2_path / "SDLC_Improvement_Suggestions.md").write_text(suggestions_content)
        
        # Create sample Proposed_Structure.md
        structure_content = """# Proposed Structure

```
project/
├── docs/           # Documentation hub
│   ├── api/
│   └── guides/
├── src/            # Source code
├── tests/          # Test suite
│   ├── unit/
│   ├── integration/
│   └── e2e/
└── config/         # Configuration files
```
"""
        (v2_path / "Proposed_Structure.md").write_text(structure_content)
        
        yield str(v2_path)
        
        # Cleanup
        shutil.rmtree(temp_dir)
    
    def test_full_comparison_flow(self, temp_project_dir, temp_v2_docs_dir):
        """Test the complete comparison flow from scanning to report generation."""
        # Create engine
        engine = ComparisonEngine(
            project_root=temp_project_dir,
            v2_docs_path=temp_v2_docs_dir
        )
        
        # Run comparison
        result = engine.run_comparison()
        
        # Verify result structure
        assert 'comparison' in result
        assert 'gaps' in result
        assert 'conflicts' in result
        assert 'tasks' in result
        assert 'report' in result
        assert 'current_structure' in result
        assert 'proposed_structure' in result
        
        # Verify comparison result
        comparison = result['comparison']
        assert comparison.completion_percentage >= 0
        assert comparison.completion_percentage <= 100
        
        # Verify report is generated
        report = result['report']
        assert isinstance(report, str)
        assert len(report) > 0
        assert "# V2 Structure Comparison Report" in report
        
        # Verify gaps are identified
        gaps = result['gaps']
        assert isinstance(gaps, list)
        
        # Verify tasks are generated
        tasks = result['tasks']
        assert isinstance(tasks, list)
    
    def test_error_handling_missing_v2_documents(self, temp_project_dir):
        """Test error handling when v2 documents are missing."""
        # Create empty v2 docs directory
        temp_dir = tempfile.mkdtemp()
        v2_path = Path(temp_dir) / "v2"
        v2_path.mkdir()
        
        try:
            # Create engine
            engine = ComparisonEngine(
                project_root=temp_project_dir,
                v2_docs_path=str(v2_path)
            )
            
            # Run comparison should raise error
            with pytest.raises(ComparisonEngineError) as exc_info:
                engine.run_comparison()
            
            # Verify error message
            assert "No v2 documents could be parsed" in str(exc_info.value)
            assert exc_info.value.recovery is not None
            
        finally:
            shutil.rmtree(temp_dir)
    
    def test_error_handling_inaccessible_project_directory(self, temp_v2_docs_dir):
        """Test error handling when project directory is inaccessible."""
        # Use a non-existent directory
        non_existent_dir = "/nonexistent/project/path"
        
        # Create engine
        engine = ComparisonEngine(
            project_root=non_existent_dir,
            v2_docs_path=temp_v2_docs_dir
        )
        
        # Run comparison should raise error
        with pytest.raises(ComparisonEngineError) as exc_info:
            engine.run_comparison()
        
        # Verify error message
        assert "Invalid project directory" in str(exc_info.value) or \
               "Cannot access project directory" in str(exc_info.value)
    
    def test_partial_report_generation_with_missing_data(self, temp_project_dir):
        """Test partial report generation when some data is unavailable."""
        # Create v2 docs with only one document
        temp_dir = tempfile.mkdtemp()
        v2_path = Path(temp_dir) / "v2"
        v2_path.mkdir()
        
        # Only create Proposed_Structure.md (missing SDLC_Improvement_Suggestions.md)
        structure_content = """# Proposed Structure

```
project/
├── docs/
└── src/
```
"""
        (v2_path / "Proposed_Structure.md").write_text(structure_content)
        
        try:
            # Create engine
            engine = ComparisonEngine(
                project_root=temp_project_dir,
                v2_docs_path=str(v2_path)
            )
            
            # Run comparison (should succeed with partial data)
            result = engine.run_comparison()
            
            # Verify result is generated despite missing data
            assert 'comparison' in result
            assert 'report' in result
            
            # Report should be generated
            report = result['report']
            assert isinstance(report, str)
            assert len(report) > 0
            
        finally:
            shutil.rmtree(temp_dir)
    
    def test_comparison_with_migration_scripts(self, temp_project_dir, temp_v2_docs_dir):
        """Test comparison with migration script generation."""
        # Add lib/ directory to project
        lib_path = Path(temp_project_dir) / "lib"
        lib_path.mkdir()
        (lib_path / "package1").mkdir()
        (lib_path / "package2").mkdir()
        
        # Create engine
        engine = ComparisonEngine(
            project_root=temp_project_dir,
            v2_docs_path=temp_v2_docs_dir
        )
        
        # Run comparison with migration scripts
        result = engine.run_comparison(generate_migration_scripts=True)
        
        # Verify migration scripts are generated
        assert 'migration_scripts' in result
        migration_scripts = result['migration_scripts']
        assert migration_scripts is not None
        assert isinstance(migration_scripts, dict)
        
        # Should have at least backup script
        assert 'backup.sh' in migration_scripts
        
        # If lib/ exists, should have lib cleanup script
        if Path(temp_project_dir, "lib").exists():
            assert 'lib_cleanup.sh' in migration_scripts
    
    def test_comparison_with_validation_check(self, temp_project_dir, temp_v2_docs_dir):
        """Test comparison with validation checking."""
        # Create engine
        engine = ComparisonEngine(
            project_root=temp_project_dir,
            v2_docs_path=temp_v2_docs_dir
        )
        
        # Run comparison with validation
        result = engine.run_comparison(check_validation=True)
        
        # Verify validation results are included
        assert 'validation_results' in result
        validation_results = result['validation_results']
        assert validation_results is not None
        assert isinstance(validation_results, dict)
        assert 'superseded' in validation_results
        assert 'inapplicable' in validation_results
    
    def test_save_report(self, temp_project_dir, temp_v2_docs_dir):
        """Test saving report to file."""
        # Create engine
        engine = ComparisonEngine(
            project_root=temp_project_dir,
            v2_docs_path=temp_v2_docs_dir
        )
        
        # Run comparison
        result = engine.run_comparison()
        
        # Save report
        temp_dir = tempfile.mkdtemp()
        try:
            output_path = Path(temp_dir) / "comparison_report.md"
            engine.save_report(result['report'], str(output_path))
            
            # Verify file was created
            assert output_path.exists()
            
            # Verify content
            content = output_path.read_text()
            assert len(content) > 0
            assert "# V2 Structure Comparison Report" in content
            
        finally:
            shutil.rmtree(temp_dir)
    
    def test_save_migration_scripts(self, temp_project_dir, temp_v2_docs_dir):
        """Test saving migration scripts to directory."""
        # Add lib/ directory
        lib_path = Path(temp_project_dir) / "lib"
        lib_path.mkdir()
        (lib_path / "package1").mkdir()
        
        # Create engine
        engine = ComparisonEngine(
            project_root=temp_project_dir,
            v2_docs_path=temp_v2_docs_dir
        )
        
        # Run comparison with migration scripts
        result = engine.run_comparison(generate_migration_scripts=True)
        
        # Save migration scripts
        temp_dir = tempfile.mkdtemp()
        try:
            output_dir = Path(temp_dir) / "migration_scripts"
            engine.save_migration_scripts(result['migration_scripts'], str(output_dir))
            
            # Verify directory was created
            assert output_dir.exists()
            
            # Verify scripts were created
            assert (output_dir / "backup.sh").exists()
            
            # Verify scripts are executable
            backup_script = output_dir / "backup.sh"
            assert backup_script.stat().st_mode & 0o111  # Check execute bit
            
        finally:
            shutil.rmtree(temp_dir)
    
    def test_graceful_degradation_on_scanner_error(self, temp_v2_docs_dir):
        """Test graceful degradation when scanner encounters errors."""
        # Use a directory that will cause scanner issues
        # (e.g., a file instead of directory)
        temp_file = tempfile.NamedTemporaryFile(delete=False)
        temp_file.close()
        
        try:
            # Create engine with file path instead of directory
            engine = ComparisonEngine(
                project_root=temp_file.name,
                v2_docs_path=temp_v2_docs_dir
            )
            
            # Run comparison should raise error
            with pytest.raises(ComparisonEngineError):
                engine.run_comparison()
                
        finally:
            Path(temp_file.name).unlink()
    
    def test_comparison_with_complex_project_structure(self, temp_v2_docs_dir):
        """Test comparison with a more complex project structure."""
        # Create a complex project structure
        temp_dir = tempfile.mkdtemp()
        project_path = Path(temp_dir) / "complex_project"
        project_path.mkdir()
        
        try:
            # Create nested structure
            (project_path / "src" / "core").mkdir(parents=True)
            (project_path / "src" / "utils").mkdir(parents=True)
            (project_path / "tests" / "unit").mkdir(parents=True)
            (project_path / "tests" / "integration").mkdir(parents=True)
            (project_path / "docs" / "api").mkdir(parents=True)
            (project_path / "docs" / "guides").mkdir(parents=True)
            (project_path / "config").mkdir()
            (project_path / "scripts").mkdir()
            
            # Add some files
            (project_path / "pyproject.toml").touch()
            (project_path / "README.md").touch()
            (project_path / ".gitignore").touch()
            (project_path / "src" / "__init__.py").touch()
            (project_path / "tests" / "__init__.py").touch()
            
            # Create engine
            engine = ComparisonEngine(
                project_root=str(project_path),
                v2_docs_path=temp_v2_docs_dir
            )
            
            # Run comparison
            result = engine.run_comparison()
            
            # Verify result
            assert 'comparison' in result
            assert 'report' in result
            
            # Verify current structure was scanned
            current_structure = result['current_structure']
            assert len(current_structure.directories) > 0
            
            # Verify some directories were found
            dir_paths = [d.rstrip('/') for d in current_structure.directories.keys()]
            assert any('src' in path for path in dir_paths)
            assert any('tests' in path for path in dir_paths)
            assert any('docs' in path for path in dir_paths)
            
        finally:
            shutil.rmtree(temp_dir)
    
    def test_comparison_result_consistency(self, temp_project_dir, temp_v2_docs_dir):
        """Test that running comparison multiple times produces consistent results."""
        # Create engine
        engine = ComparisonEngine(
            project_root=temp_project_dir,
            v2_docs_path=temp_v2_docs_dir
        )
        
        # Run comparison twice
        result1 = engine.run_comparison()
        result2 = engine.run_comparison()
        
        # Verify results are consistent
        assert result1['comparison'].completion_percentage == result2['comparison'].completion_percentage
        assert result1['comparison'].implemented_count == result2['comparison'].implemented_count
        assert result1['comparison'].partial_count == result2['comparison'].partial_count
        assert result1['comparison'].missing_count == result2['comparison'].missing_count
        
        # Verify same number of gaps
        assert len(result1['gaps']) == len(result2['gaps'])
        
        # Verify same number of tasks
        assert len(result1['tasks']) == len(result2['tasks'])
