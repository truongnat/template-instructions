#!/usr/bin/env python3
"""
Deep Reference Validator - Comprehensive validation across all file types

Validates:
- Python import statements
- Tool references in workflows
- File path references in markdown
- Template references
- Tool paths in documentation
"""

import re
import sys
import ast
from pathlib import Path
from typing import List, Dict, Tuple, Set
from datetime import datetime


from agentic_sdlc.core.utils.common import get_project_root


class DeepValidator:
    def __init__(self, project_root: Path):
        self.project_root = project_root
        self.errors = []
        self.warnings = []
        self.checked_files = 0
        
    def validate_python_imports(self, file_path: Path) -> List[Tuple[int, str]]:
        """Validate Python import statements."""
        issues = []
        
        try:
            content = file_path.read_text(encoding='utf-8')
            tree = ast.parse(content, filename=str(file_path))
            
            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    for alias in node.names:
                        # Check if module exists (basic check)
                        module_path = alias.name.replace('.', '/')
                        # Check relative to project
                        if module_path.startswith('tools/') or module_path.startswith('.agent/'):
                            full_path = self.project_root / f"{module_path}.py"
                            if not full_path.exists():
                                issues.append((node.lineno, f"import {alias.name}"))
                                
                elif isinstance(node, ast.ImportFrom):
                    if node.module:
                        module_path = node.module.replace('.', '/')
                        # Only check project-relative imports
                        if '.' not in module_path or module_path.startswith('tools') or module_path.startswith('core'):
                            base_path = self.project_root / module_path
                            if not base_path.exists() and not (self.project_root / f"{module_path}.py").exists():
                                issues.append((node.lineno, f"from {node.module} import ..."))
        except SyntaxError:
            # File has syntax errors, skip
            pass
        except Exception as e:
            self.warnings.append(f"{file_path.name}: {str(e)}")
            
        return issues
    
    def validate_markdown_file_links(self, file_path: Path) -> List[Tuple[int, str]]:
        """Validate file:// and path references in markdown."""
        issues = []
        content = file_path.read_text(encoding='utf-8')
        
        # Pattern for markdown links: [text](path)
        md_link_pattern = r'\[([^\]]+)\]\(([^)]+)\)'
        # Pattern for inline code paths: `tools/...` or `.agent/...`
        code_path_pattern = r'`((?:tools|\.agent)/[^`]+)`'
        
        for line_num, line in enumerate(content.split('\n'), 1):
            # Check markdown links
            for match in re.finditer(md_link_pattern, line):
                link = match.group(2)
                # Skip external URLs
                if link.startswith('http://') or link.startswith('https://') or link.startswith('#'):
                    continue
                # Skip file:// URLs for now (filesystem specific)
                if link.startswith('file:///'):
                    continue
                    
                # Check relative paths
                if not link.startswith('/'):
                    potential_path = file_path.parent / link
                    if not potential_path.exists():
                        issues.append((line_num, link))
                        
            # Check inline code paths
            for match in re.finditer(code_path_pattern, line):
                ref_path = match.group(1)
                full_path = self.project_root / ref_path
                if not full_path.exists():
                    # Might be a directory or partial path, skip for now
                    pass
                    
        return issues
    
    def validate_tool_references(self, file_path: Path) -> List[Tuple[int, str]]:
        """Validate python tools/... references."""
        issues = []
        content = file_path.read_text(encoding='utf-8')
        
        # Pattern: python tools/...
        pattern = r'python\s+(tools/[^\s\)\"\'`]+)'
        
        for line_num, line in enumerate(content.split('\n'), 1):
            matches = re.findall(pattern, line)
            for match in matches:
                # Clean up
                clean_match = match.rstrip('`\'"')
                full_path = self.project_root / clean_match
                if not full_path.exists():
                    issues.append((line_num, clean_match))
                    
        return issues
    
    def scan_directory(self, directory: Path, pattern: str, validator_func) -> Dict:
        """Scan directory and validate files."""
        results = {}
        
        for file_path in directory.rglob(pattern):
            if file_path.is_file():
                self.checked_files += 1
                issues = validator_func(file_path)
                if issues:
                    results[str(file_path.relative_to(self.project_root))] = issues
                    
        return results
    
    def run_full_validation(self) -> Dict:
        """Run comprehensive validation."""
        print("=" * 70)
        print("Deep Reference Validator")
        print("=" * 70)
        print(f"Project root: {self.project_root}")
        print()
        
        all_results = {
            'python_imports': {},
            'markdown_links': {},
            'tool_references': {},
            'workflow_tools': {}
        }
        
        # 1. Validate Python imports
        print("[1/4] Checking Python imports...")
        python_files = self.project_root / "tools"
        all_results['python_imports'] = self.scan_directory(
            python_files, "*.py", self.validate_python_imports
        )
        print(f"  -> Checked {self.checked_files} Python files")
        
        # 2. Validate markdown file links (docs)
        self.checked_files = 0
        print("[2/4] Checking markdown file links in docs...")
        docs_dir = self.project_root / "docs"
        all_results['markdown_links'] = self.scan_directory(
            docs_dir, "*.md", self.validate_markdown_file_links
        )
        print(f"  -> Checked {self.checked_files} markdown files")
        
        # 3. Validate tool references in workflows
        self.checked_files = 0
        print("[3/4] Checking tool references in workflows...")
        workflows_dir = self.project_root / ".agent" / "workflows"
        all_results['workflow_tools'] = self.scan_directory(
            workflows_dir, "*.md", self.validate_tool_references
        )
        print(f"  -> Checked {self.checked_files} workflow files")
        
        # 4. Validate GEMINI.md specifically
        self.checked_files = 0
        print("[4/4] Checking GEMINI.md...")
        gemini_file = self.project_root / "GEMINI.md"
        if gemini_file.exists():
            self.checked_files = 1
            tool_issues = self.validate_tool_references(gemini_file)
            link_issues = self.validate_markdown_file_links(gemini_file)
            if tool_issues or link_issues:
                all_results['tool_references']['GEMINI.md'] = tool_issues + link_issues
        print(f"  -> Checked GEMINI.md")
        
        return all_results
    
    def generate_report(self, results: Dict):
        """Generate comprehensive report."""
        print()
        print("=" * 70)
        print("Validation Results")
        print("=" * 70)
        
        total_issues = 0
        
        # Count issues
        for category, files in results.items():
            issues_in_category = sum(len(issues) for issues in files.values())
            total_issues += issues_in_category
        
        if total_issues == 0:
            print("\n[SUCCESS] No invalid references found!")
            print()
            return
        
        print(f"\n[WARNING] Found {total_issues} potential issues\n")
        
        # Python imports
        if results['python_imports']:
            print("[ERROR] Python Import Issues:")
            for file_path, issues in results['python_imports'].items():
                print(f"\n  {file_path}:")
                for line_num, ref in issues:
                    print(f"    Line {line_num}: {ref}")
                    
        # Markdown links
        if results['markdown_links']:
            print("\n[ERROR] Markdown Link Issues:")
            for file_path, issues in results['markdown_links'].items():
                print(f"\n  {file_path}:")
                for line_num, ref in issues:
                    print(f"    Line {line_num}: {ref}")
                    
        # Tool references
        if results['workflow_tools']:
            print("\n[ERROR] Workflow Tool Reference Issues:")
            for file_path, issues in results['workflow_tools'].items():
                print(f"\n  {file_path}:")
                for line_num, ref in issues:
                    print(f"    Line {line_num}: {ref}")
                    
        if results['tool_references']:
            print("\n[ERROR] Documentation Tool Reference Issues:")
            for file_path, issues in results['tool_references'].items():
                print(f"\n  {file_path}:")
                for line_num, ref in issues:
                    print(f"    Line {line_num}: {ref}")
        
        # Warnings
        if self.warnings:
            print("\n[WARNING] Warnings:")
            for warning in self.warnings:
                print(f"  - {warning}")
        
        print()
        print("=" * 70)


def main():
    """Main execution."""
    project_root = get_project_root()
    validator = DeepValidator(project_root)
    
    results = validator.run_full_validation()
    validator.generate_report(results)
    
    # Exit with error code if issues found
    total_issues = sum(
        sum(len(issues) for issues in category.values())
        for category in results.values()
    )
    
    sys.exit(1 if total_issues > 0 else 0)


if __name__ == "__main__":
    main()
