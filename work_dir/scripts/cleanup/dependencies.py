"""
Dependency Consolidator Service

Handles parsing requirements.txt files, merging dependencies into pyproject.toml,
detecting duplicates, and validating TOML syntax.
"""

import re
import sys
from pathlib import Path
from typing import List, Dict, Set, Tuple, Optional

# Use tomllib (built-in Python 3.11+) or tomli (fallback)
if sys.version_info >= (3, 11):
    import tomllib
else:
    try:
        import tomli as tomllib
    except ImportError:
        tomllib = None  # type: ignore

# For writing TOML, we need tomli_w
try:
    import tomli_w
except ImportError:
    tomli_w = None  # type: ignore

from .models import Dependency, ConsolidationResult
from .logger import get_logger


class DependencyConsolidator:
    """
    Consolidates Python dependencies from requirements.txt files into pyproject.toml.
    
    This class handles:
    - Parsing requirements.txt files (with comments, version specs, extras)
    - Reading and writing pyproject.toml files
    - Merging dependencies into appropriate groups
    - Detecting duplicate dependencies
    - Validating pyproject.toml syntax
    
    Example:
        consolidator = DependencyConsolidator(Path("pyproject.toml"))
        deps = consolidator.parse_requirements_file(Path("requirements.txt"))
        result = consolidator.merge_into_pyproject(deps, "tools")
    """
    
    def __init__(self, pyproject_path: Path, logger=None):
        """
        Initialize the DependencyConsolidator.
        
        Args:
            pyproject_path: Path to the pyproject.toml file
            logger: Optional logger instance (creates default if None)
        """
        self.pyproject_path = pyproject_path
        self.logger = logger or get_logger()
        
        # Check if TOML libraries are available
        if tomllib is None:
            self.logger.warning(
                "tomli/tomllib not available. Install tomli for Python < 3.11: pip install tomli"
            )
        if tomli_w is None:
            self.logger.warning(
                "tomli_w not available. Install it to write TOML: pip install tomli-w"
            )
    
    def parse_requirements_file(self, file_path: Path) -> List[Dependency]:
        """
        Parse a requirements.txt file and extract dependencies.
        
        Supports:
        - Simple package names: requests
        - Version specifications: requests>=2.0.0, requests==1.2.3
        - Extras: requests[security]>=2.0.0
        - Comments (ignored): # This is a comment
        - Blank lines (ignored)
        - Environment markers (preserved): requests>=2.0.0; python_version>='3.8'
        
        Args:
            file_path: Path to the requirements.txt file
            
        Returns:
            List of Dependency objects parsed from the file
            
        Raises:
            FileNotFoundError: If the requirements file doesn't exist
        """
        if not file_path.exists():
            raise FileNotFoundError(f"Requirements file not found: {file_path}")
        
        dependencies = []
        
        with open(file_path, 'r', encoding='utf-8') as f:
            for line_num, line in enumerate(f, 1):
                # Strip whitespace
                line = line.strip()
                
                # Skip empty lines and comments
                if not line or line.startswith('#'):
                    continue
                
                # Remove inline comments
                if '#' in line:
                    line = line.split('#')[0].strip()
                
                # Parse the dependency
                dep = self._parse_requirement_line(line, file_path)
                if dep:
                    dependencies.append(dep)
                else:
                    self.logger.warning(
                        f"Could not parse line {line_num} in {file_path}: {line}"
                    )
        
        self.logger.info(f"Parsed {len(dependencies)} dependencies from {file_path}")
        return dependencies
    
    def _parse_requirement_line(self, line: str, source_file: Path) -> Optional[Dependency]:
        """
        Parse a single requirement line.
        
        Args:
            line: The requirement line to parse
            source_file: Source file path for tracking
            
        Returns:
            Dependency object or None if parsing fails
        """
        # Pattern to match package specifications
        # Matches: package, package[extra], package>=1.0.0, package[extra]>=1.0.0
        # Also handles environment markers: package>=1.0.0; python_version>='3.8'
        pattern = r'^([a-zA-Z0-9_-]+)(\[[\w,]+\])?(.*?)(?:;.*)?$'
        match = re.match(pattern, line)
        
        if not match:
            return None
        
        name = match.group(1)
        extras = match.group(2) or ""
        version_spec = match.group(3).strip()
        
        # Combine name with extras if present
        full_name = f"{name}{extras}"
        
        # Default version spec if none provided
        if not version_spec:
            version_spec = ""
        
        # Determine target group based on source file name
        target_group = self._determine_target_group(source_file)
        
        return Dependency(
            name=full_name,
            version_spec=version_spec,
            source_file=source_file,
            target_group=target_group
        )
    
    def _determine_target_group(self, source_file: Path) -> str:
        """
        Determine the target dependency group based on source file name.
        
        Args:
            source_file: Path to the source requirements file
            
        Returns:
            Target group name (e.g., 'tools', 'dev', 'main')
        """
        filename = source_file.name.lower()
        
        if 'tools' in filename:
            return 'tools'
        elif 'dev' in filename or 'development' in filename:
            return 'dev'
        elif 'test' in filename:
            return 'dev'
        elif 'graph' in filename:
            return 'graph'
        elif 'mcp' in filename:
            return 'mcp'
        else:
            return 'main'
    
    def read_pyproject_toml(self) -> Dict:
        """
        Read and parse the pyproject.toml file.
        
        Returns:
            Dictionary containing the parsed TOML data
            
        Raises:
            FileNotFoundError: If pyproject.toml doesn't exist
            ValueError: If TOML parsing fails or tomllib not available
        """
        if tomllib is None:
            raise ValueError("tomli/tomllib not available. Cannot read TOML files.")
        
        if not self.pyproject_path.exists():
            raise FileNotFoundError(f"pyproject.toml not found: {self.pyproject_path}")
        
        with open(self.pyproject_path, 'rb') as f:
            try:
                data = tomllib.load(f)
                self.logger.debug(f"Successfully read {self.pyproject_path}")
                return data
            except Exception as e:
                raise ValueError(f"Failed to parse pyproject.toml: {e}")
    
    def write_pyproject_toml(self, data: Dict) -> None:
        """
        Write data to the pyproject.toml file.
        
        Args:
            data: Dictionary to write as TOML
            
        Raises:
            ValueError: If tomli_w not available or writing fails
        """
        if tomli_w is None:
            raise ValueError("tomli_w not available. Cannot write TOML files.")
        
        try:
            with open(self.pyproject_path, 'wb') as f:
                tomli_w.dump(data, f)
            self.logger.debug(f"Successfully wrote {self.pyproject_path}")
        except Exception as e:
            raise ValueError(f"Failed to write pyproject.toml: {e}")
    
    def merge_into_pyproject(
        self, 
        dependencies: List[Dependency], 
        group: Optional[str] = None
    ) -> ConsolidationResult:
        """
        Merge dependencies into pyproject.toml.
        
        Args:
            dependencies: List of dependencies to merge
            group: Target group name (overrides individual dependency target_group)
                   If None, uses each dependency's target_group attribute
                   
        Returns:
            ConsolidationResult with merge statistics and any conflicts
        """
        try:
            # Read current pyproject.toml
            data = self.read_pyproject_toml()
            
            # Ensure project section exists
            if 'project' not in data:
                data['project'] = {}
            
            # Track statistics
            merged_count = 0
            conflicts = []
            
            # Group dependencies by target group
            deps_by_group: Dict[str, List[Dependency]] = {}
            for dep in dependencies:
                target = group if group else dep.target_group
                if target not in deps_by_group:
                    deps_by_group[target] = []
                deps_by_group[target].append(dep)
            
            # Merge each group
            for target_group, group_deps in deps_by_group.items():
                if target_group == 'main':
                    # Merge into main dependencies
                    if 'dependencies' not in data['project']:
                        data['project']['dependencies'] = []
                    
                    for dep in group_deps:
                        dep_str = self._format_dependency(dep)
                        conflict = self._check_conflict(
                            dep, data['project']['dependencies']
                        )
                        if conflict:
                            conflicts.append(conflict)
                        else:
                            if dep_str not in data['project']['dependencies']:
                                data['project']['dependencies'].append(dep_str)
                                merged_count += 1
                else:
                    # Merge into optional dependencies
                    if 'optional-dependencies' not in data['project']:
                        data['project']['optional-dependencies'] = {}
                    
                    if target_group not in data['project']['optional-dependencies']:
                        data['project']['optional-dependencies'][target_group] = []
                    
                    for dep in group_deps:
                        dep_str = self._format_dependency(dep)
                        conflict = self._check_conflict(
                            dep, 
                            data['project']['optional-dependencies'][target_group]
                        )
                        if conflict:
                            conflicts.append(conflict)
                        else:
                            if dep_str not in data['project']['optional-dependencies'][target_group]:
                                data['project']['optional-dependencies'][target_group].append(dep_str)
                                merged_count += 1
            
            # Write back to file
            self.write_pyproject_toml(data)
            
            # Detect duplicates across all groups
            duplicates_count = self._count_duplicates(data)
            
            return ConsolidationResult(
                success=True,
                dependencies_merged=merged_count,
                files_removed=0,  # Will be set by caller
                duplicates_found=duplicates_count,
                conflicts=conflicts,
                errors=[]
            )
            
        except Exception as e:
            self.logger.error(f"Failed to merge dependencies: {e}")
            return ConsolidationResult(
                success=False,
                dependencies_merged=0,
                files_removed=0,
                duplicates_found=0,
                conflicts=[],
                errors=[str(e)]
            )
    
    def _format_dependency(self, dep: Dependency) -> str:
        """
        Format a Dependency object as a string for pyproject.toml.
        
        Args:
            dep: Dependency to format
            
        Returns:
            Formatted dependency string (e.g., "requests>=2.0.0")
        """
        return f"{dep.name}{dep.version_spec}"
    
    def _check_conflict(self, dep: Dependency, existing_deps: List[str]) -> Optional[str]:
        """
        Check if a dependency conflicts with existing dependencies.
        
        Args:
            dep: Dependency to check
            existing_deps: List of existing dependency strings
            
        Returns:
            Conflict message if conflict found, None otherwise
        """
        # Extract package name (without extras)
        dep_name = dep.name.split('[')[0]
        
        for existing in existing_deps:
            # Extract existing package name
            existing_name = existing.split('[')[0].split('>=')[0].split('==')[0].split('<')[0].split('>')[0].split('!')[0].split('~')[0].strip()
            
            if existing_name.lower() == dep_name.lower():
                # Found same package, check version conflict
                if dep.version_spec and dep.version_spec not in existing:
                    return f"Version conflict: {dep.name}{dep.version_spec} vs {existing}"
        
        return None
    
    def _count_duplicates(self, data: Dict) -> int:
        """
        Count duplicate dependencies across all groups.
        
        Args:
            data: Parsed pyproject.toml data
            
        Returns:
            Number of duplicate package names found
        """
        all_packages: Dict[str, int] = {}
        
        # Count main dependencies
        if 'project' in data and 'dependencies' in data['project']:
            for dep in data['project']['dependencies']:
                pkg_name = dep.split('[')[0].split('>=')[0].split('==')[0].split('<')[0].split('>')[0].split('!')[0].split('~')[0].strip().lower()
                all_packages[pkg_name] = all_packages.get(pkg_name, 0) + 1
        
        # Count optional dependencies
        if 'project' in data and 'optional-dependencies' in data['project']:
            for group, deps in data['project']['optional-dependencies'].items():
                for dep in deps:
                    pkg_name = dep.split('[')[0].split('>=')[0].split('==')[0].split('<')[0].split('>')[0].split('!')[0].split('~')[0].strip().lower()
                    all_packages[pkg_name] = all_packages.get(pkg_name, 0) + 1
        
        # Count packages that appear more than once
        duplicates = sum(1 for count in all_packages.values() if count > 1)
        return duplicates
    
    def detect_duplicates(self) -> List[Dependency]:
        """
        Detect duplicate dependencies in pyproject.toml.
        
        Returns:
            List of Dependency objects representing duplicates
        """
        try:
            data = self.read_pyproject_toml()
            
            # Track all dependencies with their locations
            dep_locations: Dict[str, List[Tuple[str, str]]] = {}
            
            # Scan main dependencies
            if 'project' in data and 'dependencies' in data['project']:
                for dep_str in data['project']['dependencies']:
                    pkg_name = self._extract_package_name(dep_str)
                    if pkg_name not in dep_locations:
                        dep_locations[pkg_name] = []
                    dep_locations[pkg_name].append(('main', dep_str))
            
            # Scan optional dependencies
            if 'project' in data and 'optional-dependencies' in data['project']:
                for group, deps in data['project']['optional-dependencies'].items():
                    for dep_str in deps:
                        pkg_name = self._extract_package_name(dep_str)
                        if pkg_name not in dep_locations:
                            dep_locations[pkg_name] = []
                        dep_locations[pkg_name].append((group, dep_str))
            
            # Find duplicates
            duplicates = []
            for pkg_name, locations in dep_locations.items():
                if len(locations) > 1:
                    # Create Dependency objects for each duplicate
                    for group, dep_str in locations:
                        version_spec = dep_str.replace(pkg_name, '', 1)
                        duplicates.append(Dependency(
                            name=pkg_name,
                            version_spec=version_spec,
                            source_file=self.pyproject_path,
                            target_group=group
                        ))
            
            if duplicates:
                self.logger.warning(f"Found {len(duplicates)} duplicate dependencies")
            
            return duplicates
            
        except Exception as e:
            self.logger.error(f"Failed to detect duplicates: {e}")
            return []
    
    def _extract_package_name(self, dep_str: str) -> str:
        """
        Extract the package name from a dependency string.
        
        Args:
            dep_str: Dependency string (e.g., "requests>=2.0.0")
            
        Returns:
            Package name (e.g., "requests")
        """
        # Remove version specifiers and extras
        name = dep_str.split('[')[0]
        for op in ['>=', '==', '<=', '>', '<', '!=', '~=']:
            name = name.split(op)[0]
        return name.strip().lower()
    
    def validate_pyproject(self) -> Tuple[bool, List[str]]:
        """
        Validate pyproject.toml syntax and structure.
        
        Returns:
            Tuple of (is_valid, error_messages)
        """
        errors = []
        
        try:
            # Try to read the file
            data = self.read_pyproject_toml()
            
            # Check required sections
            if 'project' not in data:
                errors.append("Missing required [project] section")
            else:
                # Check required project fields
                required_fields = ['name', 'version']
                for field in required_fields:
                    if field not in data['project']:
                        errors.append(f"Missing required field: project.{field}")
            
            # Validate dependencies format
            if 'project' in data:
                if 'dependencies' in data['project']:
                    if not isinstance(data['project']['dependencies'], list):
                        errors.append("project.dependencies must be a list")
                
                if 'optional-dependencies' in data['project']:
                    if not isinstance(data['project']['optional-dependencies'], dict):
                        errors.append("project.optional-dependencies must be a dict")
                    else:
                        for group, deps in data['project']['optional-dependencies'].items():
                            if not isinstance(deps, list):
                                errors.append(
                                    f"project.optional-dependencies.{group} must be a list"
                                )
            
            if errors:
                self.logger.error(f"Validation failed with {len(errors)} errors")
                for error in errors:
                    self.logger.error(f"  - {error}")
                return False, errors
            else:
                self.logger.info("pyproject.toml validation passed")
                return True, []
                
        except FileNotFoundError as e:
            errors.append(str(e))
            return False, errors
        except ValueError as e:
            errors.append(str(e))
            return False, errors
        except Exception as e:
            errors.append(f"Unexpected error during validation: {e}")
            return False, errors
