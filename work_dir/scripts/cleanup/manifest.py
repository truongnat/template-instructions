"""
Package Manifest Updater

This module handles updating package manifest files (pyproject.toml, MANIFEST.in, .gitignore)
to reflect cleanup changes and ensure proper package distribution exclusions.
"""

import re
import subprocess
from pathlib import Path
from typing import List, Set, Tuple, Optional
from .logger import get_logger
from .models import ValidationResult

logger = get_logger()


class ManifestUpdater:
    """Updates package manifest files to reflect cleanup changes.
    
    This class handles:
    - Updating pyproject.toml exclusions
    - Updating MANIFEST.in exclusions
    - Updating .gitignore patterns
    - Validating updated files
    """
    
    def __init__(self, project_root: Path):
        """Initialize ManifestUpdater.
        
        Args:
            project_root: Root directory of the project
        """
        self.project_root = Path(project_root)
        self.pyproject_path = self.project_root / "pyproject.toml"
        self.manifest_path = self.project_root / "MANIFEST.in"
        self.gitignore_path = self.project_root / ".gitignore"
        
    def update_pyproject_exclusions(self, exclude_patterns: List[str]) -> bool:
        """Update pyproject.toml to exclude specified patterns from package.
        
        Args:
            exclude_patterns: List of patterns to exclude (e.g., ['lib/', '*.pyc'])
            
        Returns:
            True if update successful, False otherwise
        """
        try:
            if not self.pyproject_path.exists():
                logger.error(f"pyproject.toml not found at {self.pyproject_path}")
                return False
                
            content = self.pyproject_path.read_text()
            
            # Check if [tool.setuptools.packages.find] section exists
            if "[tool.setuptools.packages.find]" not in content:
                logger.warning("No [tool.setuptools.packages.find] section found")
                # Add the section if it doesn't exist
                if "[tool.setuptools]" in content:
                    content = content.replace(
                        "[tool.setuptools]",
                        "[tool.setuptools]\n\n[tool.setuptools.packages.find]"
                    )
                else:
                    # Add both sections at the end
                    content += "\n\n[tool.setuptools]\n\n[tool.setuptools.packages.find]\n"
            
            # Parse existing exclude patterns
            existing_excludes = self._parse_pyproject_excludes(content)
            
            # Merge with new patterns (avoid duplicates)
            all_excludes = sorted(set(existing_excludes + exclude_patterns))
            
            # Update or add exclude line
            if "exclude = [" in content:
                # Replace existing exclude line
                content = self._replace_pyproject_excludes(content, all_excludes)
            else:
                # Add exclude line to [tool.setuptools.packages.find]
                content = self._add_pyproject_excludes(content, all_excludes)
            
            # Write updated content
            self.pyproject_path.write_text(content)
            logger.info(f"Updated pyproject.toml with {len(all_excludes)} exclusion patterns")
            return True
            
        except Exception as e:
            logger.error(f"Failed to update pyproject.toml: {e}")
            return False
    
    def update_manifest_in(self, exclude_patterns: List[str]) -> bool:
        """Update MANIFEST.in to exclude specified patterns.
        
        Args:
            exclude_patterns: List of patterns to exclude
            
        Returns:
            True if update successful, False otherwise
        """
        try:
            # Read existing content or create new
            if self.manifest_path.exists():
                lines = self.manifest_path.read_text().splitlines()
            else:
                lines = []
            
            # Parse existing exclude patterns
            existing_excludes = set()
            for line in lines:
                if line.strip().startswith("exclude ") or line.strip().startswith("global-exclude "):
                    existing_excludes.add(line.strip())
            
            # Add new exclude patterns
            new_lines = []
            for line in lines:
                # Keep non-exclude lines
                if not (line.strip().startswith("exclude ") or 
                       line.strip().startswith("global-exclude ")):
                    new_lines.append(line)
            
            # Add all exclude patterns (existing + new)
            exclude_section = []
            for pattern in sorted(exclude_patterns):
                # Use global-exclude for patterns that should apply everywhere
                if pattern in ["*.pyc", "*.pyo", ".DS_Store", "__pycache__"]:
                    exclude_line = f"global-exclude {pattern}"
                else:
                    exclude_line = f"exclude {pattern}"
                    
                if exclude_line not in existing_excludes:
                    exclude_section.append(exclude_line)
            
            # Combine: keep existing includes, add new excludes
            if new_lines and not new_lines[-1].strip():
                # Remove trailing empty line
                new_lines = new_lines[:-1]
            
            if exclude_section:
                new_lines.append("")  # Empty line before excludes
                new_lines.extend(exclude_section)
            
            # Write updated content
            content = "\n".join(new_lines)
            if content and not content.endswith("\n"):
                content += "\n"
                
            self.manifest_path.write_text(content)
            logger.info(f"Updated MANIFEST.in with {len(exclude_section)} new exclusion patterns")
            return True
            
        except Exception as e:
            logger.error(f"Failed to update MANIFEST.in: {e}")
            return False
    
    def update_gitignore(self, patterns: List[str]) -> bool:
        """Update .gitignore with specified patterns.
        
        Args:
            patterns: List of patterns to add to .gitignore
            
        Returns:
            True if update successful, False otherwise
        """
        try:
            # Read existing content or create new
            if self.gitignore_path.exists():
                content = self.gitignore_path.read_text()
                existing_patterns = set(line.strip() for line in content.splitlines() 
                                       if line.strip() and not line.strip().startswith("#"))
            else:
                content = ""
                existing_patterns = set()
            
            # Add new patterns that don't already exist
            new_patterns = []
            for pattern in patterns:
                if pattern not in existing_patterns:
                    new_patterns.append(pattern)
            
            if new_patterns:
                # Add a section header if adding patterns
                if content and not content.endswith("\n\n"):
                    content += "\n"
                if content and not content.endswith("\n"):
                    content += "\n"
                    
                content += "# Cleanup exclusions\n"
                for pattern in sorted(new_patterns):
                    content += f"{pattern}\n"
                
                self.gitignore_path.write_text(content)
                logger.info(f"Updated .gitignore with {len(new_patterns)} new patterns")
            else:
                logger.info("No new patterns to add to .gitignore")
                
            return True
            
        except Exception as e:
            logger.error(f"Failed to update .gitignore: {e}")
            return False
    
    def validate_pyproject(self) -> ValidationResult:
        """Validate pyproject.toml syntax and structure.
        
        Returns:
            ValidationResult with validation status
        """
        errors = []
        
        try:
            # Check file exists
            if not self.pyproject_path.exists():
                errors.append("pyproject.toml not found")
                return ValidationResult(passed=False, errors=errors)
            
            # Try to parse as TOML
            try:
                import tomli
                content = self.pyproject_path.read_text()
                tomli.loads(content)
            except ImportError:
                # Try with tomllib (Python 3.11+)
                try:
                    import tomllib
                    content = self.pyproject_path.read_text()
                    tomllib.loads(content)
                except ImportError:
                    logger.warning("Neither tomli nor tomllib available, skipping TOML validation")
            except Exception as e:
                errors.append(f"Invalid TOML syntax: {e}")
                return ValidationResult(passed=False, errors=errors)
            
            # Validate required sections exist
            content = self.pyproject_path.read_text()
            required_sections = ["[project]", "[build-system]"]
            for section in required_sections:
                if section not in content:
                    errors.append(f"Missing required section: {section}")
            
            # Validate package name exists
            if 'name = "' not in content and "name = '" not in content:
                errors.append("Missing project name in [project] section")
            
            if errors:
                return ValidationResult(passed=False, errors=errors)
            
            logger.info("pyproject.toml validation passed")
            return ValidationResult(passed=True)
            
        except Exception as e:
            errors.append(f"Validation error: {e}")
            return ValidationResult(passed=False, errors=errors)
    
    def validate_manifest_in(self) -> ValidationResult:
        """Validate MANIFEST.in syntax.
        
        Returns:
            ValidationResult with validation status
        """
        errors = []
        
        try:
            if not self.manifest_path.exists():
                # MANIFEST.in is optional
                logger.info("MANIFEST.in not found (optional)")
                return ValidationResult(passed=True)
            
            content = self.manifest_path.read_text()
            lines = content.splitlines()
            
            # Validate each line
            valid_commands = ["include", "exclude", "recursive-include", "recursive-exclude",
                            "global-include", "global-exclude", "graft", "prune"]
            
            for i, line in enumerate(lines, 1):
                line = line.strip()
                if not line or line.startswith("#"):
                    continue
                    
                # Check if line starts with valid command
                if not any(line.startswith(cmd + " ") for cmd in valid_commands):
                    errors.append(f"Line {i}: Invalid command or syntax: {line}")
            
            if errors:
                return ValidationResult(passed=False, errors=errors)
            
            logger.info("MANIFEST.in validation passed")
            return ValidationResult(passed=True)
            
        except Exception as e:
            errors.append(f"Validation error: {e}")
            return ValidationResult(passed=False, errors=errors)
    
    def validate_gitignore(self) -> ValidationResult:
        """Validate .gitignore syntax.
        
        Returns:
            ValidationResult with validation status
        """
        try:
            if not self.gitignore_path.exists():
                logger.warning(".gitignore not found")
                return ValidationResult(passed=True)  # Optional file
            
            # .gitignore has very flexible syntax, just check it's readable
            content = self.gitignore_path.read_text()
            
            # Basic validation: check for common issues
            errors = []
            lines = content.splitlines()
            
            for i, line in enumerate(lines, 1):
                # Check for invalid characters (very basic check)
                if '\x00' in line:
                    errors.append(f"Line {i}: Contains null character")
            
            if errors:
                return ValidationResult(passed=False, errors=errors)
            
            logger.info(".gitignore validation passed")
            return ValidationResult(passed=True)
            
        except Exception as e:
            return ValidationResult(passed=False, errors=[f"Validation error: {e}"])
    
    def validate_all(self) -> ValidationResult:
        """Validate all manifest files.
        
        Returns:
            ValidationResult with combined validation status
        """
        results = [
            self.validate_pyproject(),
            self.validate_manifest_in(),
            self.validate_gitignore()
        ]
        
        all_errors = []
        for result in results:
            all_errors.extend(result.errors)
        
        passed = all(r.passed for r in results)
        
        if passed:
            logger.info("All manifest files validated successfully")
        else:
            logger.error(f"Manifest validation failed with {len(all_errors)} errors")
        
        return ValidationResult(passed=passed, errors=all_errors)
    
    def update_all_manifests(
        self,
        removed_dirs: List[str],
        cache_patterns: List[str]
    ) -> Tuple[bool, List[str]]:
        """Update all manifest files with cleanup changes.
        
        Args:
            removed_dirs: List of directories that were removed (e.g., ['lib/', 'build/'])
            cache_patterns: List of cache patterns to exclude (e.g., ['*.pyc', '__pycache__'])
            
        Returns:
            Tuple of (success, errors)
        """
        errors = []
        
        # Combine all patterns
        all_patterns = removed_dirs + cache_patterns
        
        # Update pyproject.toml
        if not self.update_pyproject_exclusions(removed_dirs):
            errors.append("Failed to update pyproject.toml")
        
        # Update MANIFEST.in
        if not self.update_manifest_in(all_patterns):
            errors.append("Failed to update MANIFEST.in")
        
        # Update .gitignore
        gitignore_patterns = removed_dirs + cache_patterns
        if not self.update_gitignore(gitignore_patterns):
            errors.append("Failed to update .gitignore")
        
        # Validate all files
        validation = self.validate_all()
        if not validation.passed:
            errors.extend(validation.errors)
        
        success = len(errors) == 0
        
        if success:
            logger.info("Successfully updated all manifest files")
        else:
            logger.error(f"Manifest update completed with {len(errors)} errors")
        
        return success, errors
    
    # Helper methods
    
    def _parse_pyproject_excludes(self, content: str) -> List[str]:
        """Parse existing exclude patterns from pyproject.toml.
        
        Args:
            content: Content of pyproject.toml
            
        Returns:
            List of existing exclude patterns
        """
        excludes = []
        
        # Look for exclude = [...] pattern
        match = re.search(r'exclude\s*=\s*\[(.*?)\]', content, re.DOTALL)
        if match:
            exclude_str = match.group(1)
            # Extract quoted strings
            patterns = re.findall(r'["\']([^"\']+)["\']', exclude_str)
            excludes.extend(patterns)
        
        return excludes
    
    def _replace_pyproject_excludes(self, content: str, excludes: List[str]) -> str:
        """Replace existing exclude patterns in pyproject.toml.
        
        Args:
            content: Content of pyproject.toml
            excludes: New list of exclude patterns
            
        Returns:
            Updated content
        """
        # Format exclude list
        if excludes:
            exclude_str = ", ".join(f'"{p}"' for p in excludes)
            new_exclude = f"exclude = [{exclude_str}]"
        else:
            new_exclude = "exclude = []"
        
        # Replace existing exclude line
        content = re.sub(
            r'exclude\s*=\s*\[.*?\]',
            new_exclude,
            content,
            flags=re.DOTALL
        )
        
        return content
    
    def _add_pyproject_excludes(self, content: str, excludes: List[str]) -> str:
        """Add exclude patterns to pyproject.toml.
        
        Args:
            content: Content of pyproject.toml
            excludes: List of exclude patterns to add
            
        Returns:
            Updated content
        """
        if not excludes:
            return content
        
        # Format exclude list
        exclude_str = ", ".join(f'"{p}"' for p in excludes)
        new_exclude = f"exclude = [{exclude_str}]"
        
        # Find [tool.setuptools.packages.find] section and add exclude
        pattern = r'(\[tool\.setuptools\.packages\.find\])'
        replacement = f'\\1\n{new_exclude}'
        
        content = re.sub(pattern, replacement, content)
        
        return content
