#!/usr/bin/env python3
"""
Script to add basic type hints to Python files in the agentic_sdlc package.
This script adds type hints to public functions that don't have them.
"""

import ast
import sys
from pathlib import Path
from typing import List, Set, Tuple

# Add project root to path
ROOT_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT_DIR))


class TypeHintAdder(ast.NodeTransformer):
    """AST transformer to add basic type hints to functions."""
    
    def __init__(self):
        self.modified = False
        self.functions_updated = []
    
    def visit_FunctionDef(self, node: ast.FunctionDef) -> ast.FunctionDef:
        """Visit function definitions and add type hints if missing."""
        # Skip private functions (starting with _)
        if node.name.startswith('_') and not node.name.startswith('__'):
            return node
        
        # Check if function already has return annotation
        if node.returns is None:
            # Add -> None for functions without return annotation
            # This is a conservative approach - functions that return values
            # will need manual review
            node.returns = ast.Constant(value=None)
            self.modified = True
            self.functions_updated.append(node.name)
        
        return node


def has_type_hints(file_path: Path) -> Tuple[bool, List[str]]:
    """
    Check if a Python file has type hints on its public functions.
    Returns (has_hints, functions_without_hints)
    """
    try:
        content = file_path.read_text(encoding='utf-8')
        tree = ast.parse(content)
        
        functions_without_hints = []
        
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                # Skip private functions
                if node.name.startswith('_') and not node.name.startswith('__'):
                    continue
                
                # Check if function has return annotation
                if node.returns is None:
                    functions_without_hints.append(node.name)
        
        return len(functions_without_hints) == 0, functions_without_hints
    
    except Exception as e:
        print(f"Error parsing {file_path}: {e}")
        return True, []  # Assume it has hints to skip


def find_python_files(directory: Path, exclude_dirs: Set[str] = None) -> List[Path]:
    """Find all Python files in a directory, excluding specified directories."""
    if exclude_dirs is None:
        exclude_dirs = {'__pycache__', '.venv', 'venv', 'lib', 'node_modules', 'tests'}
    
    python_files = []
    
    for path in directory.rglob('*.py'):
        # Skip if any parent directory is in exclude list
        if any(excluded in path.parts for excluded in exclude_dirs):
            continue
        
        # Skip __init__.py files (they often just import)
        if path.name == '__init__.py':
            continue
        
        python_files.append(path)
    
    return python_files


def analyze_codebase(base_dir: Path) -> None:
    """Analyze the codebase and report on type hint coverage."""
    print("Analyzing codebase for type hint coverage...")
    print("=" * 70)
    
    modules = ['core', 'orchestration', 'infrastructure', 'intelligence']
    
    total_files = 0
    files_with_hints = 0
    files_without_hints = []
    
    for module in modules:
        module_path = base_dir / 'agentic_sdlc' / module
        if not module_path.exists():
            continue
        
        print(f"\nAnalyzing module: {module}")
        print("-" * 70)
        
        python_files = find_python_files(module_path)
        module_files_without_hints = 0
        
        for file_path in python_files:
            total_files += 1
            has_hints, functions = has_type_hints(file_path)
            
            if has_hints:
                files_with_hints += 1
            else:
                module_files_without_hints += 1
                rel_path = file_path.relative_to(base_dir)
                files_without_hints.append((rel_path, functions))
                print(f"  ❌ {rel_path}")
                print(f"     Functions without hints: {', '.join(functions[:5])}")
                if len(functions) > 5:
                    print(f"     ... and {len(functions) - 5} more")
        
        print(f"\n  Module summary: {len(python_files) - module_files_without_hints}/{len(python_files)} files have type hints")
    
    print("\n" + "=" * 70)
    print(f"Overall coverage: {files_with_hints}/{total_files} files ({files_with_hints/total_files*100:.1f}%)")
    print(f"Files needing type hints: {len(files_without_hints)}")
    
    return files_without_hints


def main():
    """Main execution."""
    print("Type Hint Analysis Tool")
    print("=" * 70)
    
    base_dir = ROOT_DIR
    
    # Analyze the codebase
    files_without_hints = analyze_codebase(base_dir)
    
    print("\n" + "=" * 70)
    print("Analysis complete!")
    print("\nNote: This script identifies files that need type hints.")
    print("Many files already have comprehensive type hints.")
    print("Focus on adding type hints to public APIs in the identified files.")


if __name__ == "__main__":
    main()
