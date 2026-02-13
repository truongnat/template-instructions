"""
Import Reference Detector for the Project Audit and Cleanup System.

This module provides functionality to parse Python import statements using the
ast module, detect path references in code, and check if directories are
referenced by any imports in the codebase.
"""

import ast
from pathlib import Path
from typing import List, Set, Optional, Dict
from dataclasses import dataclass

from .logger import get_logger


@dataclass
class ImportReference:
    """Represents an import reference found in a Python file.
    
    Attributes:
        source_file: Path to the file containing the import
        module_name: Name of the imported module (e.g., 'agentic_sdlc.core')
        import_type: Type of import ('import', 'from', 'relative')
        line_number: Line number where import appears
        resolved_path: Resolved file system path (if determinable)
    """
    source_file: Path
    module_name: str
    import_type: str
    line_number: int
    resolved_path: Optional[Path] = None


class ImportDetector:
    """Detect and analyze Python import statements in the codebase.
    
    The ImportDetector uses Python's ast module to parse Python files and
    extract import statements. It can detect various import formats including:
    - Standard imports: import module
    - From imports: from module import name
    - Relative imports: from . import name, from .. import name
    
    It also provides functionality to check if a directory is referenced by
    any imports in the codebase, which is useful for determining if a directory
    can be safely removed.
    
    Attributes:
        logger: Logger instance for operation logging
        project_root: Root directory of the project
        import_cache: Cache of parsed imports by file
    
    Example:
        >>> detector = ImportDetector(project_root=Path("."))
        >>> imports = detector.parse_imports(Path("src/main.py"))
        >>> for imp in imports:
        ...     print(f"{imp.module_name} at line {imp.line_number}")
    """
    
    def __init__(self, project_root: Path, verbose: bool = False):
        """Initialize the ImportDetector.
        
        Args:
            project_root: Root directory of the project
            verbose: Enable verbose logging
        """
        self.logger = get_logger(verbose=verbose)
        self.project_root = project_root.resolve()
        self.import_cache: Dict[Path, List[ImportReference]] = {}
    
    def parse_imports(self, file_path: Path) -> List[ImportReference]:
        """Parse Python file and extract all import statements.
        
        This method uses Python's ast module to parse the file and extract
        import statements. It handles:
        - import statements: import os, import sys
        - from imports: from pathlib import Path
        - relative imports: from . import module, from .. import module
        - aliased imports: import numpy as np
        
        Args:
            file_path: Path to Python file to parse
            
        Returns:
            List of ImportReference objects for all imports found
            
        Raises:
            FileNotFoundError: If file does not exist
            SyntaxError: If file contains invalid Python syntax
            
        Example:
            >>> detector = ImportDetector(project_root=Path("."))
            >>> imports = detector.parse_imports(Path("src/main.py"))
            >>> print(f"Found {len(imports)} imports")
        """
        if not file_path.exists():
            raise FileNotFoundError(f"File does not exist: {file_path}")
        
        # Check cache first
        if file_path in self.import_cache:
            return self.import_cache[file_path]
        
        imports: List[ImportReference] = []
        
        try:
            # Read and parse the file
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Parse AST
            tree = ast.parse(content, filename=str(file_path))
            
            # Walk through AST nodes
            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    # Handle: import module, import module as alias
                    for alias in node.names:
                        import_ref = ImportReference(
                            source_file=file_path,
                            module_name=alias.name,
                            import_type='import',
                            line_number=node.lineno,
                            resolved_path=self._resolve_module_path(alias.name, file_path)
                        )
                        imports.append(import_ref)
                        self.logger.debug(f"Found import: {alias.name} at line {node.lineno}")
                
                elif isinstance(node, ast.ImportFrom):
                    # Handle: from module import name, from . import name
                    module_name = node.module or ''
                    level = node.level  # 0 = absolute, 1 = ., 2 = .., etc.
                    
                    if level > 0:
                        # Relative import
                        import_type = 'relative'
                        # Construct full module name from relative import
                        full_module = self._resolve_relative_import(module_name, level, file_path)
                    else:
                        # Absolute import
                        import_type = 'from'
                        full_module = module_name
                    
                    import_ref = ImportReference(
                        source_file=file_path,
                        module_name=full_module,
                        import_type=import_type,
                        line_number=node.lineno,
                        resolved_path=self._resolve_module_path(full_module, file_path)
                    )
                    imports.append(import_ref)
                    self.logger.debug(f"Found from import: {full_module} at line {node.lineno}")
        
        except SyntaxError as e:
            self.logger.warning(f"Syntax error parsing {file_path}: {e}")
            raise
        except Exception as e:
            self.logger.warning(f"Error parsing {file_path}: {e}")
            # Return empty list on parse errors
            return []
        
        # Cache the results
        self.import_cache[file_path] = imports
        
        return imports
    
    def _resolve_relative_import(self, module_name: str, level: int, source_file: Path) -> str:
        """Resolve relative import to absolute module name.
        
        Args:
            module_name: Module name from import statement (may be empty)
            level: Import level (1 = ., 2 = .., etc.)
            source_file: File containing the import
            
        Returns:
            Resolved absolute module name
        """
        # Get the directory containing the source file
        current_dir = source_file.parent
        
        # Go up 'level' directories
        for _ in range(level):
            current_dir = current_dir.parent
        
        # Convert directory path to module path
        try:
            relative_to_root = current_dir.relative_to(self.project_root)
            base_module = str(relative_to_root).replace('/', '.').replace('\\', '.')
        except ValueError:
            # If we can't make it relative to project root, use the directory name
            base_module = current_dir.name
        
        # Combine with module_name if provided
        if module_name:
            full_module = f"{base_module}.{module_name}"
        else:
            full_module = base_module
        
        return full_module
    
    def _resolve_module_path(self, module_name: str, source_file: Path) -> Optional[Path]:
        """Resolve module name to file system path.
        
        This method attempts to resolve a module name to an actual file or
        directory path in the project. It handles:
        - Package imports (module.submodule)
        - Single module imports
        - Relative paths from project root
        
        Args:
            module_name: Module name to resolve (e.g., 'agentic_sdlc.core')
            source_file: File containing the import (for context)
            
        Returns:
            Resolved Path object, or None if path cannot be determined
        """
        if not module_name:
            return None
        
        # Convert module name to path (replace dots with slashes)
        module_path = module_name.replace('.', '/')
        
        # Try to resolve from project root
        potential_paths = [
            self.project_root / module_path,  # Directory
            self.project_root / f"{module_path}.py",  # Python file
            self.project_root / module_path / "__init__.py",  # Package
        ]
        
        for path in potential_paths:
            if path.exists():
                return path
        
        return None
    
    def detect_path_references(self, target_path: Path, search_root: Optional[Path] = None) -> List[ImportReference]:
        """Detect all import references to a specific path in the codebase.
        
        This method searches through all Python files in the codebase and
        identifies imports that reference the target path. This is useful
        for determining if a directory or module is actively used.
        
        Args:
            target_path: Path to search for references to
            search_root: Root directory to search (defaults to project_root)
            
        Returns:
            List of ImportReference objects that reference the target path
            
        Example:
            >>> detector = ImportDetector(project_root=Path("."))
            >>> refs = detector.detect_path_references(Path("agentic_sdlc/lib"))
            >>> if refs:
            ...     print(f"Found {len(refs)} references to lib/")
            ... else:
            ...     print("No references found - safe to remove")
        """
        if search_root is None:
            search_root = self.project_root
        
        target_path = target_path.resolve()
        references: List[ImportReference] = []
        
        self.logger.info(f"Searching for references to: {target_path}")
        
        # Find all Python files in search root
        python_files = list(search_root.rglob("*.py"))
        self.logger.debug(f"Scanning {len(python_files)} Python files")
        
        for py_file in python_files:
            try:
                # Parse imports from file
                imports = self.parse_imports(py_file)
                
                # Check if any import references the target path
                for import_ref in imports:
                    if self._references_path(import_ref, target_path):
                        references.append(import_ref)
                        self.logger.debug(f"Found reference in {py_file}: {import_ref.module_name}")
            
            except Exception as e:
                self.logger.debug(f"Error processing {py_file}: {e}")
                continue
        
        self.logger.info(f"Found {len(references)} references to {target_path}")
        
        return references
    
    def _references_path(self, import_ref: ImportReference, target_path: Path) -> bool:
        """Check if an import reference refers to a target path.
        
        Args:
            import_ref: ImportReference to check
            target_path: Target path to match against
            
        Returns:
            True if import references the target path, False otherwise
        """
        # Check if resolved path matches
        if import_ref.resolved_path:
            try:
                # Check if resolved path is the target or a child of target
                resolved = import_ref.resolved_path.resolve()
                if resolved == target_path:
                    return True
                if target_path in resolved.parents:
                    return True
            except Exception:
                pass
        
        # Check if module name matches target path
        # Convert target path to module name format
        try:
            relative_path = target_path.relative_to(self.project_root)
            module_pattern = str(relative_path).replace('/', '.').replace('\\', '.')
            
            # Check if import module name starts with the pattern
            if import_ref.module_name.startswith(module_pattern):
                return True
        except ValueError:
            pass
        
        return False
    
    def is_directory_referenced(self, dir_path: Path, search_root: Optional[Path] = None) -> bool:
        """Check if a directory is referenced by any imports in the codebase.
        
        This is a convenience method that returns a boolean indicating whether
        any imports reference the given directory. Useful for determining if
        a directory can be safely removed.
        
        Args:
            dir_path: Directory path to check
            search_root: Root directory to search (defaults to project_root)
            
        Returns:
            True if directory is referenced, False otherwise
            
        Example:
            >>> detector = ImportDetector(project_root=Path("."))
            >>> if detector.is_directory_referenced(Path("agentic_sdlc/lib")):
            ...     print("Directory is in use - cannot remove")
            ... else:
            ...     print("Directory is not referenced - safe to remove")
        """
        references = self.detect_path_references(dir_path, search_root)
        return len(references) > 0
    
    def get_all_imports(self, search_root: Optional[Path] = None) -> Dict[Path, List[ImportReference]]:
        """Get all imports from all Python files in the codebase.
        
        This method scans all Python files and returns a dictionary mapping
        file paths to their import statements. Useful for comprehensive
        dependency analysis.
        
        Args:
            search_root: Root directory to search (defaults to project_root)
            
        Returns:
            Dictionary mapping file paths to lists of ImportReference objects
            
        Example:
            >>> detector = ImportDetector(project_root=Path("."))
            >>> all_imports = detector.get_all_imports()
            >>> for file_path, imports in all_imports.items():
            ...     print(f"{file_path}: {len(imports)} imports")
        """
        if search_root is None:
            search_root = self.project_root
        
        all_imports: Dict[Path, List[ImportReference]] = {}
        
        # Find all Python files
        python_files = list(search_root.rglob("*.py"))
        self.logger.info(f"Parsing imports from {len(python_files)} Python files")
        
        for py_file in python_files:
            try:
                imports = self.parse_imports(py_file)
                if imports:
                    all_imports[py_file] = imports
            except Exception as e:
                self.logger.debug(f"Error processing {py_file}: {e}")
                continue
        
        self.logger.info(f"Parsed imports from {len(all_imports)} files")
        
        return all_imports
    
    def clear_cache(self) -> None:
        """Clear the import cache.
        
        This method clears the internal cache of parsed imports. Useful if
        files have been modified and need to be re-parsed.
        """
        self.import_cache.clear()
        self.logger.debug("Import cache cleared")
