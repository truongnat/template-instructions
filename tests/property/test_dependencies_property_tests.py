"""
Property-based tests for DependencyConsolidator service.

Tests universal properties using Hypothesis for dependency consolidation.

Feature: project-audit-cleanup
"""

import pytest
import tempfile
import shutil
from pathlib import Path
from hypothesis import given, strategies as st, settings

from scripts.cleanup.dependencies import DependencyConsolidator
from scripts.cleanup.models import Dependency


# Strategy for generating valid package names
package_names = st.text(
    alphabet=st.characters(whitelist_categories=('Ll', 'Lu', 'Nd'), whitelist_characters='-_'),
    min_size=2,
    max_size=20
).filter(lambda x: x[0].isalpha())

# Strategy for generating version specs
version_specs = st.sampled_from([
    '',
    '>=1.0.0',
    '==2.0.0',
    '~=1.5.0',
    '<3.0.0',
    '!=1.2.3',
])

# Strategy for generating dependency groups
dependency_groups = st.sampled_from(['main', 'dev', 'tools', 'graph', 'mcp'])


@st.composite
def dependency_strategy(draw):
    """Generate a valid Dependency object."""
    name = draw(package_names)
    version_spec = draw(version_specs)
    group = draw(dependency_groups)
    
    return Dependency(
        name=name,
        version_spec=version_spec,
        source_file=Path("requirements.txt"),
        target_group=group
    )


class TestDependencyConsolidationIdempotence:
    """
    Property 4: Dependency Consolidation Idempotence
    
    For any set of requirements files, consolidating them into pyproject.toml
    then consolidating again should produce the same result (no duplicate
    dependencies added).
    
    Validates: Requirements 4.3, 4.5
    """
    
    @given(st.lists(dependency_strategy(), min_size=1, max_size=10, unique_by=lambda d: d.name))
    @settings(max_examples=10, deadline=None)
    def test_consolidation_idempotence(self, dependencies):
        """
        Property 4: Dependency Consolidation Idempotence
        
        For any set of dependencies, consolidating them twice should produce
        the same result. The second consolidation should not add any new
        dependencies.
        
        **Validates: Requirements 4.3, 4.5**
        """
        # Create temp directory and pyproject.toml
        temp_path = Path(tempfile.mkdtemp())
        try:
            pyproject_path = temp_path / "pyproject.toml"
            content = """[project]
name = "test"
version = "1.0.0"
"""
            pyproject_path.write_text(content)
            
            consolidator = DependencyConsolidator(pyproject_path)
            
            # First consolidation
            result1 = consolidator.merge_into_pyproject(dependencies)
            assert result1.success, f"First merge failed: {result1.errors}"
            
            # Read the state after first consolidation
            data_after_first = consolidator.read_pyproject_toml()
            
            # Count dependencies after first merge
            count_after_first = 0
            if 'dependencies' in data_after_first.get('project', {}):
                count_after_first += len(data_after_first['project']['dependencies'])
            if 'optional-dependencies' in data_after_first.get('project', {}):
                for group_deps in data_after_first['project']['optional-dependencies'].values():
                    count_after_first += len(group_deps)
            
            # Second consolidation with same dependencies
            result2 = consolidator.merge_into_pyproject(dependencies)
            assert result2.success, f"Second merge failed: {result2.errors}"
            
            # Read the state after second consolidation
            data_after_second = consolidator.read_pyproject_toml()
            
            # Count dependencies after second merge
            count_after_second = 0
            if 'dependencies' in data_after_second.get('project', {}):
                count_after_second += len(data_after_second['project']['dependencies'])
            if 'optional-dependencies' in data_after_second.get('project', {}):
                for group_deps in data_after_second['project']['optional-dependencies'].values():
                    count_after_second += len(group_deps)
            
            # Property: Second consolidation should not add any new dependencies
            assert count_after_second == count_after_first, (
                f"Idempotence violated: First merge resulted in {count_after_first} dependencies, "
                f"second merge resulted in {count_after_second} dependencies. "
                f"Second merge should not add duplicates."
            )
            
            # Property: Second merge should report 0 dependencies merged
            assert result2.dependencies_merged == 0, (
                f"Second merge reported {result2.dependencies_merged} dependencies merged, "
                f"but should be 0 (all dependencies already exist)"
            )
        finally:
            shutil.rmtree(temp_path)
    
    @given(st.lists(dependency_strategy(), min_size=1, max_size=5, unique_by=lambda d: d.name))
    @settings(max_examples=10, deadline=None)
    def test_consolidation_multiple_rounds(self, dependencies):
        """
        Property 4 (Extended): Multiple consolidation rounds are idempotent.
        
        Consolidating the same dependencies N times should produce the same
        result as consolidating once.
        
        **Validates: Requirements 4.3, 4.5**
        """
        # Create temp directory and pyproject.toml
        temp_path = Path(tempfile.mkdtemp())
        try:
            pyproject_path = temp_path / "pyproject.toml"
            content = """[project]
name = "test"
version = "1.0.0"
"""
            pyproject_path.write_text(content)
            
            consolidator = DependencyConsolidator(pyproject_path)
            
            # Consolidate multiple times
            for round_num in range(3):
                result = consolidator.merge_into_pyproject(dependencies)
                assert result.success, f"Round {round_num + 1} failed: {result.errors}"
                
                if round_num == 0:
                    # First round should merge dependencies
                    assert result.dependencies_merged > 0, "First round should merge dependencies"
                else:
                    # Subsequent rounds should not merge anything
                    assert result.dependencies_merged == 0, (
                        f"Round {round_num + 1} should not merge any dependencies "
                        f"(already merged in round 1), but merged {result.dependencies_merged}"
                    )
            
            # Verify final state
            data = consolidator.read_pyproject_toml()
            
            # Count total dependencies
            total_deps = 0
            if 'dependencies' in data.get('project', {}):
                total_deps += len(data['project']['dependencies'])
            if 'optional-dependencies' in data.get('project', {}):
                for group_deps in data['project']['optional-dependencies'].values():
                    total_deps += len(group_deps)
            
            # Should have exactly the number of unique dependencies we started with
            assert total_deps == len(dependencies), (
                f"Expected {len(dependencies)} total dependencies after multiple rounds, "
                f"but found {total_deps}"
            )
        finally:
            shutil.rmtree(temp_path)


class TestConfigurationUpdateValidity:
    """
    Property 15: Configuration Update Validity
    
    For any pyproject.toml file, after the system updates it (adding dependencies
    or exclusions), the file should remain syntactically valid and parseable.
    
    Validates: Requirements 12.4
    """
    
    @given(st.lists(dependency_strategy(), min_size=1, max_size=10, unique_by=lambda d: d.name))
    @settings(max_examples=10, deadline=None)
    def test_pyproject_remains_valid_after_update(self, dependencies):
        """
        Property 15: Configuration Update Validity
        
        For any set of dependencies, after merging them into pyproject.toml,
        the file should remain syntactically valid and parseable.
        
        **Validates: Requirements 12.4**
        """
        # Create temp directory and pyproject.toml
        temp_path = Path(tempfile.mkdtemp())
        try:
            pyproject_path = temp_path / "pyproject.toml"
            content = """[project]
name = "test"
version = "1.0.0"
"""
            pyproject_path.write_text(content)
            
            consolidator = DependencyConsolidator(pyproject_path)
            
            # Merge dependencies
            result = consolidator.merge_into_pyproject(dependencies)
            assert result.success, f"Merge failed: {result.errors}"
            
            # Property: File should be readable after update
            try:
                data = consolidator.read_pyproject_toml()
            except Exception as e:
                pytest.fail(f"pyproject.toml became unparseable after update: {e}")
            
            # Property: File should pass validation
            is_valid, errors = consolidator.validate_pyproject()
            assert is_valid, (
                f"pyproject.toml failed validation after update. Errors: {errors}"
            )
            
            # Property: Required sections should exist
            assert 'project' in data, "Missing [project] section after update"
            assert 'name' in data['project'], "Missing project.name after update"
            assert 'version' in data['project'], "Missing project.version after update"
            
            # Property: Dependencies should be in correct format
            if 'dependencies' in data.get('project', {}):
                assert isinstance(data['project']['dependencies'], list), (
                    "project.dependencies should be a list"
                )
            
            if 'optional-dependencies' in data.get('project', {}):
                assert isinstance(data['project']['optional-dependencies'], dict), (
                    "project.optional-dependencies should be a dict"
                )
                for group, deps in data['project']['optional-dependencies'].items():
                    assert isinstance(deps, list), (
                        f"project.optional-dependencies.{group} should be a list"
                    )
        finally:
            shutil.rmtree(temp_path)
    
    @given(st.lists(dependency_strategy(), min_size=1, max_size=5))
    @settings(max_examples=10, deadline=None)
    def test_pyproject_structure_preserved(self, dependencies):
        """
        Property 15 (Extended): Existing structure is preserved after update.
        
        After updating pyproject.toml, existing sections and fields should
        remain intact.
        
        **Validates: Requirements 12.4**
        """
        # Create temp directory and pyproject.toml
        temp_path = Path(tempfile.mkdtemp())
        try:
            pyproject_path = temp_path / "pyproject.toml"
            content = """[project]
name = "test"
version = "1.0.0"
"""
            pyproject_path.write_text(content)
            
            # Add some existing content to pyproject.toml
            consolidator = DependencyConsolidator(pyproject_path)
            data = consolidator.read_pyproject_toml()
            data['project']['description'] = "Test project"
            data['project']['authors'] = [{"name": "Test Author"}]
            data['build-system'] = {
                "requires": ["setuptools>=61.0"],
                "build-backend": "setuptools.build_meta"
            }
            consolidator.write_pyproject_toml(data)
            
            # Merge dependencies
            result = consolidator.merge_into_pyproject(dependencies)
            assert result.success, f"Merge failed: {result.errors}"
            
            # Read updated data
            updated_data = consolidator.read_pyproject_toml()
            
            # Property: Existing fields should be preserved
            assert updated_data['project']['description'] == "Test project", (
                "Existing description was lost"
            )
            assert updated_data['project']['authors'] == [{"name": "Test Author"}], (
                "Existing authors were lost"
            )
            assert 'build-system' in updated_data, "Existing build-system section was lost"
            assert updated_data['build-system']['requires'] == ["setuptools>=61.0"], (
                "Existing build-system.requires was modified"
            )
        finally:
            shutil.rmtree(temp_path)
