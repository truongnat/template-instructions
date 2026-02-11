"""
Unit tests for V2 Structure Comparison data models.

Tests basic instantiation and field validation for all data model classes.
"""

import pytest
from agentic_sdlc.comparison.models import (
    DirectoryStatus,
    DirectoryInfo,
    LibraryInfo,
    ProjectStructure,
    ProposedDirectory,
    Improvement,
    ProposedStructure,
    ComparisonResult,
    Gap,
    Conflict,
    Task,
)


class TestDirectoryStatus:
    """Tests for DirectoryStatus enum."""
    
    def test_enum_values(self):
        """Test that all expected enum values exist."""
        assert DirectoryStatus.IMPLEMENTED.value == "implemented"
        assert DirectoryStatus.PARTIAL.value == "partial"
        assert DirectoryStatus.MISSING.value == "missing"
        assert DirectoryStatus.CONFLICT.value == "conflict"


class TestDirectoryInfo:
    """Tests for DirectoryInfo dataclass."""
    
    def test_basic_instantiation(self):
        """Test creating a DirectoryInfo instance."""
        dir_info = DirectoryInfo(
            path="src/",
            exists=True,
            subdirectories=["utils", "core"],
            file_count=5
        )
        assert dir_info.path == "src/"
        assert dir_info.exists is True
        assert dir_info.subdirectories == ["utils", "core"]
        assert dir_info.file_count == 5
    
    def test_default_values(self):
        """Test that default values are set correctly."""
        dir_info = DirectoryInfo(path="test/", exists=False)
        assert dir_info.subdirectories == []
        assert dir_info.file_count == 0


class TestLibraryInfo:
    """Tests for LibraryInfo dataclass."""
    
    def test_basic_instantiation(self):
        """Test creating a LibraryInfo instance."""
        lib_info = LibraryInfo(
            exists=True,
            package_count=150,
            total_size_mb=45.2,
            packages=["requests", "numpy", "pandas"]
        )
        assert lib_info.exists is True
        assert lib_info.package_count == 150
        assert lib_info.total_size_mb == 45.2
        assert len(lib_info.packages) == 3
    
    def test_default_values(self):
        """Test that default values are set correctly."""
        lib_info = LibraryInfo(exists=False)
        assert lib_info.package_count == 0
        assert lib_info.total_size_mb == 0.0
        assert lib_info.packages == []


class TestProjectStructure:
    """Tests for ProjectStructure dataclass."""
    
    def test_basic_instantiation(self):
        """Test creating a ProjectStructure instance."""
        dir_info = DirectoryInfo(path="src/", exists=True)
        lib_info = LibraryInfo(exists=True, package_count=10)
        
        project = ProjectStructure(
            root_path="/project",
            directories={"src/": dir_info},
            config_files={"pyproject.toml": True, "requirements.txt": False},
            lib_info=lib_info
        )
        
        assert project.root_path == "/project"
        assert "src/" in project.directories
        assert project.config_files["pyproject.toml"] is True
        assert project.lib_info is not None
    
    def test_default_values(self):
        """Test that default values are set correctly."""
        project = ProjectStructure(root_path="/project")
        assert project.directories == {}
        assert project.config_files == {}
        assert project.lib_info is None


class TestProposedDirectory:
    """Tests for ProposedDirectory dataclass."""
    
    def test_basic_instantiation(self):
        """Test creating a ProposedDirectory instance."""
        proposed = ProposedDirectory(
            path="docs/",
            purpose="Documentation files",
            subdirectories=["api", "guides"],
            required_files=["README.md", "index.md"],
            is_new=True
        )
        
        assert proposed.path == "docs/"
        assert proposed.purpose == "Documentation files"
        assert len(proposed.subdirectories) == 2
        assert len(proposed.required_files) == 2
        assert proposed.is_new is True
    
    def test_default_values(self):
        """Test that default values are set correctly."""
        proposed = ProposedDirectory(path="test/", purpose="Testing")
        assert proposed.subdirectories == []
        assert proposed.required_files == []
        assert proposed.is_new is False


class TestImprovement:
    """Tests for Improvement dataclass."""
    
    def test_basic_instantiation(self):
        """Test creating an Improvement instance."""
        improvement = Improvement(
            category="Documentation",
            title="Add API docs",
            description="Create comprehensive API documentation",
            priority="High",
            estimated_hours=8.0,
            related_directories=["docs/", "docs/api/"]
        )
        
        assert improvement.category == "Documentation"
        assert improvement.title == "Add API docs"
        assert improvement.priority == "High"
        assert improvement.estimated_hours == 8.0
        assert len(improvement.related_directories) == 2
    
    def test_default_values(self):
        """Test that default values are set correctly."""
        improvement = Improvement(
            category="Testing",
            title="Add tests",
            description="Add unit tests",
            priority="Medium",
            estimated_hours=4.0
        )
        assert improvement.related_directories == []


class TestProposedStructure:
    """Tests for ProposedStructure dataclass."""
    
    def test_basic_instantiation(self):
        """Test creating a ProposedStructure instance."""
        proposed_dir = ProposedDirectory(path="docs/", purpose="Documentation")
        improvement = Improvement(
            category="Documentation",
            title="Add docs",
            description="Add documentation",
            priority="High",
            estimated_hours=8.0
        )
        
        proposed = ProposedStructure(
            directories={"docs/": proposed_dir},
            improvements=[improvement]
        )
        
        assert "docs/" in proposed.directories
        assert len(proposed.improvements) == 1
    
    def test_default_values(self):
        """Test that default values are set correctly."""
        proposed = ProposedStructure()
        assert proposed.directories == {}
        assert proposed.improvements == []


class TestComparisonResult:
    """Tests for ComparisonResult dataclass."""
    
    def test_basic_instantiation(self):
        """Test creating a ComparisonResult instance."""
        result = ComparisonResult(
            directory_statuses={"docs/": DirectoryStatus.IMPLEMENTED},
            completion_percentage=75.0,
            implemented_count=3,
            partial_count=1,
            missing_count=1
        )
        
        assert result.directory_statuses["docs/"] == DirectoryStatus.IMPLEMENTED
        assert result.completion_percentage == 75.0
        assert result.implemented_count == 3
        assert result.partial_count == 1
        assert result.missing_count == 1
    
    def test_default_values(self):
        """Test that default values are set correctly."""
        result = ComparisonResult()
        assert result.directory_statuses == {}
        assert result.completion_percentage == 0.0
        assert result.implemented_count == 0
        assert result.partial_count == 0
        assert result.missing_count == 0


class TestGap:
    """Tests for Gap dataclass."""
    
    def test_basic_instantiation(self):
        """Test creating a Gap instance."""
        gap = Gap(
            category="Documentation",
            description="Missing API documentation",
            priority="High",
            effort="Medium",
            related_requirement="4.1",
            proposed_action="Create docs/api/ directory and add API docs"
        )
        
        assert gap.category == "Documentation"
        assert gap.description == "Missing API documentation"
        assert gap.priority == "High"
        assert gap.effort == "Medium"
        assert gap.related_requirement == "4.1"
        assert "Create docs/api/" in gap.proposed_action


class TestConflict:
    """Tests for Conflict dataclass."""
    
    def test_basic_instantiation(self):
        """Test creating a Conflict instance."""
        conflict = Conflict(
            type="directory_exists",
            description="docs/ exists but lacks required subdirectories",
            affected_paths=["docs/", "docs/api/"],
            severity="Medium",
            mitigation="Create missing subdirectories"
        )
        
        assert conflict.type == "directory_exists"
        assert "docs/" in conflict.description
        assert len(conflict.affected_paths) == 2
        assert conflict.severity == "Medium"
        assert conflict.mitigation == "Create missing subdirectories"
    
    def test_default_values(self):
        """Test that default values are set correctly."""
        conflict = Conflict(
            type="config_conflict",
            description="Missing config section"
        )
        assert conflict.affected_paths == []
        assert conflict.severity == "Medium"
        assert conflict.mitigation == ""


class TestTask:
    """Tests for Task dataclass."""
    
    def test_basic_instantiation(self):
        """Test creating a Task instance."""
        task = Task(
            id="task-001",
            title="Create API documentation",
            description="Add comprehensive API documentation",
            priority="High",
            effort_hours=8.0,
            category="Documentation",
            files_to_create=["docs/api/README.md", "docs/api/endpoints.md"],
            files_to_modify=["docs/index.md"],
            dependencies=["task-000"],
            reference="Section 4.1 of v2 suggestions"
        )
        
        assert task.id == "task-001"
        assert task.title == "Create API documentation"
        assert task.priority == "High"
        assert task.effort_hours == 8.0
        assert task.category == "Documentation"
        assert len(task.files_to_create) == 2
        assert len(task.files_to_modify) == 1
        assert len(task.dependencies) == 1
        assert "Section 4.1" in task.reference
    
    def test_default_values(self):
        """Test that default values are set correctly."""
        task = Task(
            id="task-002",
            title="Simple task",
            description="A simple task",
            priority="Low",
            effort_hours=2.0,
            category="Misc"
        )
        assert task.files_to_create == []
        assert task.files_to_modify == []
        assert task.dependencies == []
        assert task.reference == ""


class TestModelIntegration:
    """Integration tests for model interactions."""
    
    def test_complete_workflow(self):
        """Test a complete workflow using all models together."""
        # Create current project structure
        dir_info = DirectoryInfo(path="docs/", exists=True, subdirectories=["guides"])
        lib_info = LibraryInfo(exists=True, package_count=200)
        current = ProjectStructure(
            root_path="/project",
            directories={"docs/": dir_info},
            config_files={"pyproject.toml": True},
            lib_info=lib_info
        )
        
        # Create proposed structure
        proposed_dir = ProposedDirectory(
            path="docs/",
            purpose="Documentation",
            subdirectories=["guides", "api"],
            required_files=["README.md"]
        )
        improvement = Improvement(
            category="Documentation",
            title="Add API docs",
            description="Add API documentation",
            priority="High",
            estimated_hours=8.0,
            related_directories=["docs/api/"]
        )
        proposed = ProposedStructure(
            directories={"docs/": proposed_dir},
            improvements=[improvement]
        )
        
        # Create comparison result
        result = ComparisonResult(
            directory_statuses={"docs/": DirectoryStatus.PARTIAL},
            completion_percentage=50.0,
            implemented_count=1,
            partial_count=1,
            missing_count=0
        )
        
        # Create gap
        gap = Gap(
            category="Documentation",
            description="Missing docs/api/ subdirectory",
            priority="High",
            effort="Quick Win",
            related_requirement="5.1",
            proposed_action="Create docs/api/ directory"
        )
        
        # Create task
        task = Task(
            id="task-001",
            title="Create API docs directory",
            description="Create docs/api/ directory and add initial files",
            priority="High",
            effort_hours=2.0,
            category="Documentation",
            files_to_create=["docs/api/README.md"]
        )
        
        # Verify all models work together
        assert current.root_path == "/project"
        assert proposed.directories["docs/"].path == "docs/"
        assert result.directory_statuses["docs/"] == DirectoryStatus.PARTIAL
        assert gap.priority == "High"
        assert task.category == "Documentation"
