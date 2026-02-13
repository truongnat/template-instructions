"""
Unit tests for DependencyConsolidator service.

Tests parsing various requirements.txt formats, merging into pyproject.toml,
duplicate detection, and version conflict detection.

Requirements: 4.2, 4.3, 4.5
"""

import pytest
import tempfile
import shutil
from pathlib import Path

from scripts.cleanup.dependencies import DependencyConsolidator
from scripts.cleanup.models import Dependency


class TestDependencyConsolidator:
    """Test suite for DependencyConsolidator class."""
    
    @pytest.fixture
    def temp_dir(self):
        """Create a temporary directory for test files."""
        temp_path = Path(tempfile.mkdtemp())
        yield temp_path
        shutil.rmtree(temp_path)
    
    @pytest.fixture
    def sample_pyproject(self, temp_dir):
        """Create a sample pyproject.toml file."""
        pyproject_path = temp_dir / "pyproject.toml"
        content = """[project]
name = "test-project"
version = "1.0.0"
dependencies = [
    "click>=8.0.0",
    "requests>=2.28.0",
]

[project.optional-dependencies]
dev = [
    "pytest>=7.0.0",
]
"""
        pyproject_path.write_text(content)
        return pyproject_path
    
    @pytest.fixture
    def sample_requirements(self, temp_dir):
        """Create a sample requirements.txt file."""
        req_path = temp_dir / "requirements_tools.txt"
        content = """# Test requirements file
requests>=2.31.0
python-dotenv>=1.0.0
PyGithub>=2.1.1

# Optional dependencies
# tavily-python>=0.3.0

neo4j>=5.14.0
pyyaml==6.0.2
"""
        req_path.write_text(content)
        return req_path


class TestRequirementsFileParsing:
    """Test parsing requirements.txt files (Requirement 4.2)."""
    
    @pytest.fixture
    def temp_dir(self):
        """Create a temporary directory for test files."""
        temp_path = Path(tempfile.mkdtemp())
        yield temp_path
        shutil.rmtree(temp_path)
    
    @pytest.fixture
    def sample_pyproject(self, temp_dir):
        """Create a minimal pyproject.toml."""
        pyproject_path = temp_dir / "pyproject.toml"
        content = """[project]
name = "test"
version = "1.0.0"
"""
        pyproject_path.write_text(content)
        return pyproject_path
    
    def test_parse_simple_requirements(self, temp_dir, sample_pyproject):
        """Test parsing simple package names."""
        req_file = temp_dir / "requirements.txt"
        req_file.write_text("requests\npytest\nclick\n")
        
        consolidator = DependencyConsolidator(sample_pyproject)
        deps = consolidator.parse_requirements_file(req_file)
        
        assert len(deps) == 3
        assert deps[0].name == "requests"
        assert deps[1].name == "pytest"
        assert deps[2].name == "click"
    
    def test_parse_version_specifications(self, temp_dir, sample_pyproject):
        """Test parsing various version specifications."""
        req_file = temp_dir / "requirements.txt"
        req_file.write_text("""requests>=2.0.0
pytest==7.4.0
click~=8.0
numpy<2.0.0
pandas!=1.5.0
""")
        
        consolidator = DependencyConsolidator(sample_pyproject)
        deps = consolidator.parse_requirements_file(req_file)
        
        assert len(deps) == 5
        assert deps[0].version_spec == ">=2.0.0"
        assert deps[1].version_spec == "==7.4.0"
        assert deps[2].version_spec == "~=8.0"
        assert deps[3].version_spec == "<2.0.0"
        assert deps[4].version_spec == "!=1.5.0"
    
    def test_parse_extras(self, temp_dir, sample_pyproject):
        """Test parsing packages with extras."""
        req_file = temp_dir / "requirements.txt"
        req_file.write_text("""requests[security]>=2.0.0
autogen-ext[openai]>=0.4.0
""")
        
        consolidator = DependencyConsolidator(sample_pyproject)
        deps = consolidator.parse_requirements_file(req_file)
        
        assert len(deps) == 2
        assert deps[0].name == "requests[security]"
        assert deps[0].version_spec == ">=2.0.0"
        assert deps[1].name == "autogen-ext[openai]"
    
    def test_parse_with_comments(self, temp_dir, sample_pyproject):
        """Test parsing file with comments."""
        req_file = temp_dir / "requirements.txt"
        req_file.write_text("""# This is a comment
requests>=2.0.0  # Inline comment
# Another comment
pytest>=7.0.0
""")
        
        consolidator = DependencyConsolidator(sample_pyproject)
        deps = consolidator.parse_requirements_file(req_file)
        
        assert len(deps) == 2
        assert deps[0].name == "requests"
        assert deps[1].name == "pytest"
    
    def test_parse_empty_lines(self, temp_dir, sample_pyproject):
        """Test parsing file with empty lines."""
        req_file = temp_dir / "requirements.txt"
        req_file.write_text("""requests>=2.0.0

pytest>=7.0.0

click>=8.0.0
""")
        
        consolidator = DependencyConsolidator(sample_pyproject)
        deps = consolidator.parse_requirements_file(req_file)
        
        assert len(deps) == 3
    
    def test_parse_nonexistent_file(self, temp_dir, sample_pyproject):
        """Test parsing nonexistent file raises error."""
        consolidator = DependencyConsolidator(sample_pyproject)
        
        with pytest.raises(FileNotFoundError):
            consolidator.parse_requirements_file(temp_dir / "nonexistent.txt")


class TestTargetGroupDetermination:
    """Test determining target dependency groups."""
    
    @pytest.fixture
    def temp_dir(self):
        """Create a temporary directory for test files."""
        temp_path = Path(tempfile.mkdtemp())
        yield temp_path
        shutil.rmtree(temp_path)
    
    @pytest.fixture
    def sample_pyproject(self, temp_dir):
        """Create a minimal pyproject.toml."""
        pyproject_path = temp_dir / "pyproject.toml"
        content = """[project]
name = "test"
version = "1.0.0"
"""
        pyproject_path.write_text(content)
        return pyproject_path
    
    def test_tools_requirements_to_tools_group(self, temp_dir, sample_pyproject):
        """Test requirements_tools.txt maps to 'tools' group."""
        req_file = temp_dir / "requirements_tools.txt"
        req_file.write_text("requests>=2.0.0\n")
        
        consolidator = DependencyConsolidator(sample_pyproject)
        deps = consolidator.parse_requirements_file(req_file)
        
        assert deps[0].target_group == "tools"
    
    def test_dev_requirements_to_dev_group(self, temp_dir, sample_pyproject):
        """Test requirements-dev.txt maps to 'dev' group."""
        req_file = temp_dir / "requirements-dev.txt"
        req_file.write_text("pytest>=7.0.0\n")
        
        consolidator = DependencyConsolidator(sample_pyproject)
        deps = consolidator.parse_requirements_file(req_file)
        
        assert deps[0].target_group == "dev"
    
    def test_generic_requirements_to_main_group(self, temp_dir, sample_pyproject):
        """Test requirements.txt maps to 'main' group."""
        req_file = temp_dir / "requirements.txt"
        req_file.write_text("requests>=2.0.0\n")
        
        consolidator = DependencyConsolidator(sample_pyproject)
        deps = consolidator.parse_requirements_file(req_file)
        
        assert deps[0].target_group == "main"


class TestPyprojectMerging:
    """Test merging dependencies into pyproject.toml (Requirement 4.3)."""
    
    @pytest.fixture
    def temp_dir(self):
        """Create a temporary directory for test files."""
        temp_path = Path(tempfile.mkdtemp())
        yield temp_path
        shutil.rmtree(temp_path)
    
    @pytest.fixture
    def sample_pyproject(self, temp_dir):
        """Create a sample pyproject.toml."""
        pyproject_path = temp_dir / "pyproject.toml"
        content = """[project]
name = "test-project"
version = "1.0.0"
dependencies = [
    "click>=8.0.0",
]
"""
        pyproject_path.write_text(content)
        return pyproject_path
    
    def test_merge_to_main_dependencies(self, temp_dir, sample_pyproject):
        """Test merging dependencies to main dependencies list."""
        consolidator = DependencyConsolidator(sample_pyproject)
        
        deps = [
            Dependency("requests", ">=2.0.0", Path("req.txt"), "main"),
            Dependency("pytest", ">=7.0.0", Path("req.txt"), "main"),
        ]
        
        result = consolidator.merge_into_pyproject(deps)
        
        assert result.success
        assert result.dependencies_merged == 2
        
        # Verify merged
        data = consolidator.read_pyproject_toml()
        assert "requests>=2.0.0" in data['project']['dependencies']
        assert "pytest>=7.0.0" in data['project']['dependencies']
    
    def test_merge_to_optional_dependencies(self, temp_dir, sample_pyproject):
        """Test merging to optional dependencies group."""
        consolidator = DependencyConsolidator(sample_pyproject)
        
        deps = [
            Dependency("pytest", ">=7.0.0", Path("req.txt"), "dev"),
            Dependency("black", ">=23.0.0", Path("req.txt"), "dev"),
        ]
        
        result = consolidator.merge_into_pyproject(deps)
        
        assert result.success
        assert result.dependencies_merged == 2
        
        # Verify merged
        data = consolidator.read_pyproject_toml()
        assert 'optional-dependencies' in data['project']
        assert 'dev' in data['project']['optional-dependencies']
        assert "pytest>=7.0.0" in data['project']['optional-dependencies']['dev']
    
    def test_merge_creates_new_group(self, temp_dir, sample_pyproject):
        """Test merging creates new optional dependency group if needed."""
        consolidator = DependencyConsolidator(sample_pyproject)
        
        deps = [
            Dependency("neo4j", ">=5.0.0", Path("req.txt"), "graph"),
        ]
        
        result = consolidator.merge_into_pyproject(deps)
        
        assert result.success
        
        # Verify new group created
        data = consolidator.read_pyproject_toml()
        assert 'graph' in data['project']['optional-dependencies']
        assert "neo4j>=5.0.0" in data['project']['optional-dependencies']['graph']
    
    def test_merge_skips_duplicates(self, temp_dir, sample_pyproject):
        """Test merging skips dependencies that already exist."""
        consolidator = DependencyConsolidator(sample_pyproject)
        
        # click>=8.0.0 already exists in sample_pyproject
        deps = [
            Dependency("click", ">=8.0.0", Path("req.txt"), "main"),
        ]
        
        result = consolidator.merge_into_pyproject(deps)
        
        assert result.success
        assert result.dependencies_merged == 0  # Already exists
    
    def test_merge_with_group_override(self, temp_dir, sample_pyproject):
        """Test merging with explicit group override."""
        consolidator = DependencyConsolidator(sample_pyproject)
        
        deps = [
            Dependency("requests", ">=2.0.0", Path("req.txt"), "main"),
        ]
        
        # Override to put in 'tools' group
        result = consolidator.merge_into_pyproject(deps, group="tools")
        
        assert result.success
        
        # Verify in tools group, not main
        data = consolidator.read_pyproject_toml()
        assert "requests>=2.0.0" not in data['project']['dependencies']
        assert "requests>=2.0.0" in data['project']['optional-dependencies']['tools']


class TestDuplicateDetection:
    """Test duplicate dependency detection (Requirement 4.5)."""
    
    @pytest.fixture
    def temp_dir(self):
        """Create a temporary directory for test files."""
        temp_path = Path(tempfile.mkdtemp())
        yield temp_path
        shutil.rmtree(temp_path)
    
    @pytest.fixture
    def pyproject_with_duplicates(self, temp_dir):
        """Create pyproject.toml with duplicate dependencies."""
        pyproject_path = temp_dir / "pyproject.toml"
        content = """[project]
name = "test"
version = "1.0.0"
dependencies = [
    "requests>=2.0.0",
    "pytest>=7.0.0",
]

[project.optional-dependencies]
dev = [
    "pytest>=7.4.0",
    "black>=23.0.0",
]
tools = [
    "requests>=2.31.0",
]
"""
        pyproject_path.write_text(content)
        return pyproject_path
    
    def test_detect_duplicates(self, pyproject_with_duplicates):
        """Test detecting duplicate dependencies across groups."""
        consolidator = DependencyConsolidator(pyproject_with_duplicates)
        
        duplicates = consolidator.detect_duplicates()
        
        # Should find requests and pytest duplicated
        assert len(duplicates) >= 2
        
        dup_names = [d.name for d in duplicates]
        assert "requests" in dup_names
        assert "pytest" in dup_names
    
    def test_no_duplicates(self, temp_dir):
        """Test no duplicates found in clean pyproject.toml."""
        pyproject_path = temp_dir / "pyproject.toml"
        content = """[project]
name = "test"
version = "1.0.0"
dependencies = [
    "requests>=2.0.0",
]

[project.optional-dependencies]
dev = [
    "pytest>=7.0.0",
]
"""
        pyproject_path.write_text(content)
        
        consolidator = DependencyConsolidator(pyproject_path)
        duplicates = consolidator.detect_duplicates()
        
        assert len(duplicates) == 0


class TestVersionConflictDetection:
    """Test version conflict detection (Requirement 4.5)."""
    
    @pytest.fixture
    def temp_dir(self):
        """Create a temporary directory for test files."""
        temp_path = Path(tempfile.mkdtemp())
        yield temp_path
        shutil.rmtree(temp_path)
    
    @pytest.fixture
    def sample_pyproject(self, temp_dir):
        """Create pyproject.toml with existing dependencies."""
        pyproject_path = temp_dir / "pyproject.toml"
        content = """[project]
name = "test"
version = "1.0.0"
dependencies = [
    "requests>=2.28.0",
]
"""
        pyproject_path.write_text(content)
        return pyproject_path
    
    def test_detect_version_conflict(self, sample_pyproject):
        """Test detecting version conflicts when merging."""
        consolidator = DependencyConsolidator(sample_pyproject)
        
        # Try to merge conflicting version
        deps = [
            Dependency("requests", ">=2.31.0", Path("req.txt"), "main"),
        ]
        
        result = consolidator.merge_into_pyproject(deps)
        
        # Should detect conflict
        assert len(result.conflicts) > 0
        assert "requests" in result.conflicts[0].lower()


class TestPyprojectValidation:
    """Test pyproject.toml validation (Requirement 4.4)."""
    
    @pytest.fixture
    def temp_dir(self):
        """Create a temporary directory for test files."""
        temp_path = Path(tempfile.mkdtemp())
        yield temp_path
        shutil.rmtree(temp_path)
    
    def test_validate_valid_pyproject(self, temp_dir):
        """Test validation passes for valid pyproject.toml."""
        pyproject_path = temp_dir / "pyproject.toml"
        content = """[project]
name = "test"
version = "1.0.0"
dependencies = [
    "requests>=2.0.0",
]
"""
        pyproject_path.write_text(content)
        
        consolidator = DependencyConsolidator(pyproject_path)
        is_valid, errors = consolidator.validate_pyproject()
        
        assert is_valid
        assert len(errors) == 0
    
    def test_validate_missing_project_section(self, temp_dir):
        """Test validation fails for missing [project] section."""
        pyproject_path = temp_dir / "pyproject.toml"
        content = """[build-system]
requires = ["setuptools"]
"""
        pyproject_path.write_text(content)
        
        consolidator = DependencyConsolidator(pyproject_path)
        is_valid, errors = consolidator.validate_pyproject()
        
        assert not is_valid
        assert any("project" in e.lower() for e in errors)
    
    def test_validate_missing_required_fields(self, temp_dir):
        """Test validation fails for missing required fields."""
        pyproject_path = temp_dir / "pyproject.toml"
        content = """[project]
description = "test"
"""
        pyproject_path.write_text(content)
        
        consolidator = DependencyConsolidator(pyproject_path)
        is_valid, errors = consolidator.validate_pyproject()
        
        assert not is_valid
        assert any("name" in e.lower() for e in errors)
        assert any("version" in e.lower() for e in errors)
    
    def test_validate_invalid_dependencies_format(self, temp_dir):
        """Test validation fails for invalid dependencies format."""
        pyproject_path = temp_dir / "pyproject.toml"
        content = """[project]
name = "test"
version = "1.0.0"
dependencies = "not-a-list"
"""
        pyproject_path.write_text(content)
        
        consolidator = DependencyConsolidator(pyproject_path)
        is_valid, errors = consolidator.validate_pyproject()
        
        assert not is_valid
        assert any("dependencies" in e.lower() and "list" in e.lower() for e in errors)
    
    def test_validate_nonexistent_file(self, temp_dir):
        """Test validation fails for nonexistent file."""
        pyproject_path = temp_dir / "nonexistent.toml"
        
        consolidator = DependencyConsolidator(pyproject_path)
        is_valid, errors = consolidator.validate_pyproject()
        
        assert not is_valid
        assert len(errors) > 0
