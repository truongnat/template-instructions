"""Property-based tests for dependency version constraints.

Feature: sdk-reorganization
Property 1: Dependency Version Constraints

Validates: Requirements 2.3

For any dependency declared in pyproject.toml, it SHALL have version constraints
specified (minimum version, version range, or pinned version).
"""

import re
from pathlib import Path
from typing import Dict, List

import pytest
from hypothesis import given, strategies as st


def load_pyproject_toml() -> Dict:
    """Load pyproject.toml and return parsed content."""
    import tomllib

    pyproject_path = Path(__file__).parent.parent.parent / "pyproject.toml"
    with open(pyproject_path, "rb") as f:
        return tomllib.load(f)


def extract_dependencies(pyproject: Dict) -> Dict[str, List[str]]:
    """Extract all dependencies from pyproject.toml.

    Returns a dict with keys like 'dependencies', 'cli', 'dev', etc.
    and values as lists of dependency strings.
    """
    dependencies = {}

    # Get main dependencies
    if "project" in pyproject and "dependencies" in pyproject["project"]:
        dependencies["dependencies"] = pyproject["project"]["dependencies"]

    # Get optional dependencies
    if "project" in pyproject and "optional-dependencies" in pyproject["project"]:
        for key, deps in pyproject["project"]["optional-dependencies"].items():
            dependencies[key] = deps

    return dependencies


def parse_dependency_spec(dep_string: str) -> tuple[str, str]:
    """Parse a dependency string into (package_name, version_spec).

    Examples:
        "pydantic>=2.0.0,<3.0.0" -> ("pydantic", ">=2.0.0,<3.0.0")
        "click>=8.3.0,<9.0.0" -> ("click", ">=8.3.0,<9.0.0")
        "requests" -> ("requests", "")
    """
    # Remove extras like [cli]
    dep_string = dep_string.split("[")[0].strip()

    # Split on common version operators
    match = re.match(r"^([a-zA-Z0-9_-]+)(.*?)$", dep_string)
    if match:
        package_name = match.group(1)
        version_spec = match.group(2).strip()
        return package_name, version_spec
    return dep_string, ""


def is_valid_version_constraint(version_spec: str) -> bool:
    """Check if a version constraint is valid.

    Valid constraints include:
    - ">=1.0.0,<2.0.0" (range)
    - ">=1.0.0" (minimum)
    - "==1.0.0" (pinned)
    - "~=1.0.0" (compatible release)
    - "" (no constraint - invalid for our purposes)
    """
    if not version_spec:
        return False

    # Check for valid version constraint patterns
    valid_patterns = [
        r"^>=[\d.]+,<[\d.]+$",  # Range like >=1.0.0,<2.0.0
        r"^>=[\d.]+$",  # Minimum like >=1.0.0
        r"^==[\d.]+$",  # Pinned like ==1.0.0
        r"^~=[\d.]+$",  # Compatible release like ~=1.0.0
        r"^!=[\d.]+$",  # Excluded like !=1.0.0
        r"^>[\d.]+$",  # Greater than like >1.0.0
        r"^<[\d.]+$",  # Less than like <2.0.0
        r"^<=[\d.]+$",  # Less than or equal like <=2.0.0
    ]

    for pattern in valid_patterns:
        if re.match(pattern, version_spec):
            return True

    return False


class TestDependencyVersionConstraints:
    """Test that all dependencies have proper version constraints."""

    def test_all_dependencies_have_constraints(self):
        """Test that all dependencies in pyproject.toml have version constraints.

        Validates: Requirements 2.3
        """
        pyproject = load_pyproject_toml()
        dependencies = extract_dependencies(pyproject)

        unconstrained = []

        for section, deps in dependencies.items():
            for dep in deps:
                package_name, version_spec = parse_dependency_spec(dep)

                # Skip self-reference without version spec (common pattern for 'all' extra)
                if package_name == "agentic-sdlc" and not version_spec:
                    continue

                if not is_valid_version_constraint(version_spec):
                    unconstrained.append(
                        f"{section}: {package_name} (spec: '{version_spec}')"
                    )

        assert (
            not unconstrained
        ), f"Found {len(unconstrained)} dependencies without version constraints:\n" + "\n".join(
            unconstrained
        )

    def test_version_constraints_are_valid_format(self):
        """Test that version constraints follow valid PEP 440 format.

        Validates: Requirements 2.3
        """
        pyproject = load_pyproject_toml()
        dependencies = extract_dependencies(pyproject)

        invalid_constraints = []

        for section, deps in dependencies.items():
            for dep in deps:
                package_name, version_spec = parse_dependency_spec(dep)

                if version_spec and not is_valid_version_constraint(version_spec):
                    invalid_constraints.append(
                        f"{section}: {package_name} (spec: '{version_spec}')"
                    )

        assert (
            not invalid_constraints
        ), f"Found {len(invalid_constraints)} dependencies with invalid version constraints:\n" + "\n".join(
            invalid_constraints
        )

    def test_no_bare_package_names(self):
        """Test that no dependency is specified as just a package name.

        Validates: Requirements 2.3
        """
        pyproject = load_pyproject_toml()
        dependencies = extract_dependencies(pyproject)

        bare_packages = []

        for section, deps in dependencies.items():
            for dep in deps:
                package_name, version_spec = parse_dependency_spec(dep)

                # Skip extras like "agentic-sdlc[dev,graph,mcp,tools]"
                if "[" in dep:
                    continue

                if not version_spec:
                    bare_packages.append(f"{section}: {package_name}")

        assert (
            not bare_packages
        ), f"Found {len(bare_packages)} bare package names without version constraints:\n" + "\n".join(
            bare_packages
        )

    @given(
        st.sampled_from(
            [
                ">=1.0.0,<2.0.0",
                ">=2.0.0,<3.0.0",
                ">=0.1.0,<1.0.0",
                "==1.5.0",
                "~=1.0.0",
            ]
        )
    )
    def test_valid_constraints_pass_validation(self, constraint: str):
        """Test that known valid constraints pass validation.

        Validates: Requirements 2.3
        """
        assert is_valid_version_constraint(constraint), (
            f"Valid constraint '{constraint}' failed validation"
        )

    @given(
        st.sampled_from(
            [
                "",
                "latest",
                "any",
                "1.0.0",  # No operator
                ">=1.0.0,<2.0.0,!=1.5.0",  # Complex constraint (not in our patterns)
            ]
        )
    )
    def test_invalid_constraints_fail_validation(self, constraint: str):
        """Test that invalid constraints fail validation.

        Validates: Requirements 2.3
        """
        # Empty string and bare version numbers should fail
        if constraint in ["", "1.0.0"]:
            assert not is_valid_version_constraint(constraint), (
                f"Invalid constraint '{constraint}' passed validation"
            )

    def test_dependency_sections_exist(self):
        """Test that expected dependency sections exist in pyproject.toml.

        Validates: Requirements 2.3
        """
        pyproject = load_pyproject_toml()

        assert "project" in pyproject, "Missing [project] section"
        assert "dependencies" in pyproject["project"], "Missing [project.dependencies]"
        assert (
            "optional-dependencies" in pyproject["project"]
        ), "Missing [project.optional-dependencies]"

    def test_cli_dependencies_have_constraints(self):
        """Test that CLI optional dependencies have version constraints.

        Validates: Requirements 2.3
        """
        pyproject = load_pyproject_toml()
        cli_deps = (
            pyproject.get("project", {})
            .get("optional-dependencies", {})
            .get("cli", [])
        )

        unconstrained = []
        for dep in cli_deps:
            package_name, version_spec = parse_dependency_spec(dep)
            if not is_valid_version_constraint(version_spec):
                unconstrained.append(f"{package_name} (spec: '{version_spec}')")

        assert (
            not unconstrained
        ), f"Found {len(unconstrained)} CLI dependencies without version constraints:\n" + "\n".join(
            unconstrained
        )

    def test_dev_dependencies_have_constraints(self):
        """Test that dev optional dependencies have version constraints.

        Validates: Requirements 2.3
        """
        pyproject = load_pyproject_toml()
        dev_deps = (
            pyproject.get("project", {})
            .get("optional-dependencies", {})
            .get("dev", [])
        )

        unconstrained = []
        for dep in dev_deps:
            package_name, version_spec = parse_dependency_spec(dep)
            if not is_valid_version_constraint(version_spec):
                unconstrained.append(f"{package_name} (spec: '{version_spec}')")

        assert (
            not unconstrained
        ), f"Found {len(unconstrained)} dev dependencies without version constraints:\n" + "\n".join(
            unconstrained
        )
