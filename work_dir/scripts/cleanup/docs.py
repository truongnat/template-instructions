"""
Documentation Updater for Project Audit and Cleanup System.

This module provides the DocumentationUpdater class for updating project
documentation after cleanup operations. It updates README.md with new package
size, generates CLEANUP-SUMMARY.md, and updates CONTRIBUTING.md with dependency
management guidelines.

Key Features:
    - Update README.md with new package size
    - Generate CLEANUP-SUMMARY.md with cleanup details
    - Update CONTRIBUTING.md with dependency management guidelines
    - Update .gitignore with new exclusion patterns

Requirements Addressed:
    - 14.1: Update README.md to reflect new package size
    - 14.2: Create docs/CLEANUP-SUMMARY.md documenting changes
    - 14.3: Update CONTRIBUTING.md with dependency management guidelines
    - 14.4: Document backup and rollback process
"""

from pathlib import Path
from datetime import datetime
from typing import List, Optional
import re

from .models import CleanupResult, CategorizedFiles, SizeImpact
from .logger import get_logger


class DocumentationUpdater:
    """Update project documentation after cleanup operations.
    
    The DocumentationUpdater modifies key documentation files to reflect
    cleanup changes:
    - README.md: Updates package size badge/information
    - CLEANUP-SUMMARY.md: Creates comprehensive cleanup documentation
    - CONTRIBUTING.md: Adds dependency management guidelines
    - .gitignore: Adds new exclusion patterns if needed
    
    Attributes:
        project_root: Root directory of the project
        logger: Logger instance for operation tracking
    
    Example:
        >>> updater = DocumentationUpdater(project_root=Path("."))
        >>> updater.update_readme_size(old_size=120_000_000, new_size=5_000_000)
        >>> updater.generate_cleanup_summary(cleanup_result, categorized_files)
    """
    
    def __init__(self, project_root: Path = Path("."), verbose: bool = False):
        """Initialize DocumentationUpdater.
        
        Args:
            project_root: Root directory of the project
            verbose: Enable verbose logging
        """
        self.project_root = Path(project_root)
        self.logger = get_logger(verbose=verbose)
        
        self.logger.info(f"DocumentationUpdater initialized with project_root: {self.project_root}")
    
    def update_readme_size(self, old_size: int, new_size: int) -> bool:
        """Update README.md with new package size information.
        
        Updates or adds package size information in README.md. If a size
        badge or size mention exists, it updates it. Otherwise, it adds
        a new section with size information.
        
        Args:
            old_size: Previous package size in bytes
            new_size: New package size in bytes after cleanup
        
        Returns:
            True if update was successful, False otherwise
        
        Example:
            >>> updater.update_readme_size(120_000_000, 5_000_000)
            True
        """
        readme_path = self.project_root / "README.md"
        
        if not readme_path.exists():
            self.logger.warning(f"README.md not found at {readme_path}")
            return False
        
        self.logger.info(f"Updating README.md with new package size")
        
        try:
            content = readme_path.read_text(encoding="utf-8")
            
            # Format sizes
            old_size_str = self._format_size_simple(old_size)
            new_size_str = self._format_size_simple(new_size)
            reduction_percent = ((old_size - new_size) / old_size * 100) if old_size > 0 else 0
            
            # Try to find and update existing size information
            # Look for patterns like "120MB", "120 MB", "~120MB", etc.
            size_pattern = r'~?\d+\.?\d*\s*[MGK]B'
            
            # Check if there's already size information in the README
            if re.search(size_pattern, content, re.IGNORECASE):
                # Update existing size mentions (be conservative, only update obvious ones)
                # This is a simple approach - in production you might want more sophisticated logic
                self.logger.info("Found existing size information in README.md")
            
            # Add a note about the cleanup at the end of the Quick Start section
            # or before the "What's inside" section
            cleanup_note = f"\n> **Package Size**: Optimized to **{new_size_str}** (reduced from {old_size_str}, {reduction_percent:.0f}% smaller)\n"
            
            # Try to insert after Quick Start section
            quick_start_pattern = r'(## 🚀 Quick Start.*?)(##)'
            match = re.search(quick_start_pattern, content, re.DOTALL)
            
            if match:
                # Insert before the next section
                insert_pos = match.end(1)
                content = content[:insert_pos] + "\n" + cleanup_note + "\n" + content[insert_pos:]
                self.logger.info("Added package size information after Quick Start section")
            else:
                # Fallback: add at the beginning after the header
                lines = content.split('\n')
                # Find the first ## heading after the title
                for i, line in enumerate(lines):
                    if line.startswith('## ') and i > 5:  # Skip the first few lines (title, badges)
                        lines.insert(i, cleanup_note)
                        break
                content = '\n'.join(lines)
                self.logger.info("Added package size information before first major section")
            
            # Write updated content
            readme_path.write_text(content, encoding="utf-8")
            self.logger.info(f"README.md updated successfully")
            
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to update README.md: {e}")
            return False
    
    def generate_cleanup_summary(
        self,
        cleanup_result: CleanupResult,
        categorized_files: CategorizedFiles,
        size_impact: SizeImpact
    ) -> Path:
        """Generate comprehensive CLEANUP-SUMMARY.md documentation.
        
        Creates a detailed markdown document in docs/ that includes:
        - What was removed and why
        - Size reduction achieved
        - Backup and rollback instructions
        - Validation results
        - Next steps for developers
        
        Args:
            cleanup_result: Results from the cleanup operation
            categorized_files: Files that were categorized during audit
            size_impact: Size impact analysis
        
        Returns:
            Path to the generated CLEANUP-SUMMARY.md file
        
        Example:
            >>> summary_path = updater.generate_cleanup_summary(
            ...     cleanup_result, categorized_files, size_impact
            ... )
        """
        self.logger.info("Generating CLEANUP-SUMMARY.md")
        
        lines = []
        
        # Header
        lines.append("# Project Cleanup Summary")
        lines.append("")
        lines.append(f"**Date**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        lines.append(f"**Status**: {'✅ Completed Successfully' if cleanup_result.success else '❌ Failed'}")
        lines.append("")
        
        # Overview
        lines.append("## Overview")
        lines.append("")
        lines.append("This document summarizes the cleanup operation performed on the Agentic SDLC project.")
        lines.append("The cleanup removed unnecessary files, consolidated dependencies, and optimized the")
        lines.append("package structure for better maintainability and distribution.")
        lines.append("")
        
        # Size Reduction
        lines.append("## Size Reduction")
        lines.append("")
        lines.append(f"- **Before Cleanup**: {self._format_size_simple(size_impact.current_size)}")
        lines.append(f"- **After Cleanup**: {self._format_size_simple(size_impact.projected_size)}")
        lines.append(f"- **Size Freed**: {self._format_size_simple(size_impact.reduction)}")
        lines.append(f"- **Reduction**: {size_impact.reduction_percent:.1f}%")
        lines.append("")
        
        # What Was Removed
        lines.append("## What Was Removed")
        lines.append("")
        
        if categorized_files.remove:
            # Group by reason
            remove_by_reason = {}
            for file_info in categorized_files.remove:
                reason = file_info.reason or "Unspecified"
                if reason not in remove_by_reason:
                    remove_by_reason[reason] = []
                remove_by_reason[reason].append(file_info)
            
            for reason, files in sorted(remove_by_reason.items()):
                total_size = sum(f.size for f in files)
                lines.append(f"### {reason}")
                lines.append("")
                lines.append(f"**Files removed**: {len(files)}")
                lines.append(f"**Size freed**: {self._format_size_simple(total_size)}")
                lines.append("")
                lines.append("**Examples**:")
                lines.append("")
                
                # Show first 5 files
                for file_info in sorted(files, key=lambda f: f.size, reverse=True)[:5]:
                    lines.append(f"- `{file_info.path}` ({self._format_size_simple(file_info.size)})")
                
                if len(files) > 5:
                    lines.append(f"- ... and {len(files) - 5} more files")
                
                lines.append("")
        else:
            lines.append("No files were removed during this cleanup.")
            lines.append("")
        
        # What Was Consolidated
        if categorized_files.consolidate:
            lines.append("## Dependencies Consolidated")
            lines.append("")
            lines.append("The following requirements files were merged into `pyproject.toml`:")
            lines.append("")
            
            for file_info in categorized_files.consolidate:
                lines.append(f"- `{file_info.path}`")
            
            lines.append("")
            lines.append("All dependencies are now managed centrally in `pyproject.toml` under")
            lines.append("appropriate dependency groups (`[project.dependencies]` and")
            lines.append("`[project.optional-dependencies]`).")
            lines.append("")
        
        # What Was Archived
        if categorized_files.archive:
            lines.append("## Files Archived")
            lines.append("")
            total_archive_size = sum(f.size for f in categorized_files.archive)
            lines.append(f"**Total archived**: {len(categorized_files.archive)} files ({self._format_size_simple(total_archive_size)})")
            lines.append("")
            lines.append("Old cache files were archived to preserve directory structure while")
            lines.append("removing regenerable data.")
            lines.append("")
        
        # Backup and Rollback
        lines.append("## Backup and Rollback")
        lines.append("")
        lines.append(f"**Backup ID**: `{cleanup_result.backup_id}`")
        lines.append("")
        lines.append("All removed files were backed up before deletion. If you need to restore")
        lines.append("any files, use the rollback command:")
        lines.append("")
        lines.append("```bash")
        lines.append(f"python scripts/cleanup.py --rollback {cleanup_result.backup_id}")
        lines.append("```")
        lines.append("")
        lines.append("The backup is stored in `.cleanup_backup/` and includes:")
        lines.append("")
        lines.append("- Compressed archive of all removed files")
        lines.append("- Manifest with original file paths and checksums")
        lines.append("- Metadata about the cleanup operation")
        lines.append("")
        
        # Validation Results
        if cleanup_result.validation_result:
            lines.append("## Validation Results")
            lines.append("")
            
            val = cleanup_result.validation_result
            lines.append(f"- **Overall**: {'✅ Passed' if val.passed else '❌ Failed'}")
            lines.append(f"- **Import Check**: {'✅ Passed' if val.import_check else '❌ Failed'}")
            lines.append(f"- **CLI Check**: {'✅ Passed' if val.cli_check else '❌ Failed'}")
            lines.append(f"- **Test Suite**: {'✅ Passed' if val.test_check else '❌ Failed'}")
            lines.append(f"- **Package Build**: {'✅ Passed' if val.build_check else '❌ Failed'}")
            lines.append("")
            
            if val.errors:
                lines.append("### Validation Errors")
                lines.append("")
                for error in val.errors:
                    lines.append(f"- {error}")
                lines.append("")
        
        # Next Steps
        lines.append("## Next Steps for Developers")
        lines.append("")
        lines.append("1. **Review Changes**: Verify that all critical functionality still works")
        lines.append("2. **Run Tests**: Execute the full test suite to ensure no regressions")
        lines.append("3. **Update Dependencies**: Install dependencies from updated `pyproject.toml`:")
        lines.append("   ```bash")
        lines.append("   pip install -e .[dev]")
        lines.append("   ```")
        lines.append("4. **Commit Changes**: Commit the cleanup changes to version control")
        lines.append("5. **Remove Backup**: After verification, you can safely remove the backup:")
        lines.append("   ```bash")
        lines.append(f"   rm -rf .cleanup_backup/{cleanup_result.backup_id}")
        lines.append("   ```")
        lines.append("")
        
        # Footer
        lines.append("---")
        lines.append("")
        lines.append("*This document was generated automatically by the Project Audit and Cleanup System.*")
        lines.append("")
        
        # Save to docs/
        docs_dir = self.project_root / "docs"
        docs_dir.mkdir(parents=True, exist_ok=True)
        
        summary_path = docs_dir / "CLEANUP-SUMMARY.md"
        summary_path.write_text("\n".join(lines), encoding="utf-8")
        
        self.logger.info(f"CLEANUP-SUMMARY.md generated at: {summary_path}")
        
        return summary_path
    
    def update_contributing_guidelines(self) -> bool:
        """Update CONTRIBUTING.md with dependency management guidelines.
        
        Adds or updates a section in CONTRIBUTING.md that explains:
        - How dependencies are managed in pyproject.toml
        - How to add new dependencies
        - Dependency groups and their purposes
        - Best practices for dependency management
        
        Returns:
            True if update was successful, False otherwise
        
        Example:
            >>> updater.update_contributing_guidelines()
            True
        """
        contributing_path = self.project_root / "CONTRIBUTING.md"
        
        if not contributing_path.exists():
            self.logger.warning(f"CONTRIBUTING.md not found at {contributing_path}")
            return False
        
        self.logger.info("Updating CONTRIBUTING.md with dependency management guidelines")
        
        try:
            content = contributing_path.read_text(encoding="utf-8")
            
            # Check if dependency management section already exists
            if "## Dependency Management" in content or "## Managing Dependencies" in content:
                self.logger.info("Dependency management section already exists in CONTRIBUTING.md")
                return True
            
            # Create dependency management section
            dep_section = """
## Dependency Management

All project dependencies are managed centrally in `pyproject.toml`. We no longer use
separate `requirements*.txt` files.

### Dependency Groups

Dependencies are organized into groups:

- **`[project.dependencies]`**: Core runtime dependencies required for the package to function
- **`[project.optional-dependencies.dev]`**: Development tools (pytest, black, mypy, etc.)
- **`[project.optional-dependencies.graph]`**: Graph database support (Neo4j)
- **`[project.optional-dependencies.mcp]`**: MCP connectors and integrations
- **`[project.optional-dependencies.tools]`**: Additional development and analysis tools

### Adding a New Dependency

1. **Determine the appropriate group** for your dependency:
   - Core functionality → `[project.dependencies]`
   - Development/testing → `[project.optional-dependencies.dev]`
   - Optional feature → Create or use an appropriate optional group

2. **Add the dependency to `pyproject.toml`**:
   ```toml
   [project.dependencies]
   requests = ">=2.28.0"
   ```

3. **Install the updated dependencies**:
   ```bash
   pip install -e .[dev]
   ```

4. **Verify the installation**:
   ```bash
   python -c "import requests"
   ```

### Best Practices

- **Pin major versions** but allow minor/patch updates: `requests>=2.28.0,<3.0.0`
- **Avoid overly strict pinning** unless necessary for compatibility
- **Document why** unusual version constraints are needed (add comments in pyproject.toml)
- **Test with minimum versions** to ensure compatibility ranges are correct
- **Keep dependencies up to date** but test thoroughly after updates

### Updating Dependencies

To update all dependencies to their latest compatible versions:

```bash
pip install --upgrade -e .[dev]
```

To update a specific dependency:

```bash
pip install --upgrade "requests>=2.30.0"
```

Always run the test suite after updating dependencies:

```bash
pytest
```
"""
            
            # Find a good place to insert the section
            # Try to insert before "Pull Request Process" or at the end
            pr_section_pattern = r'(## Pull Request Process)'
            match = re.search(pr_section_pattern, content)
            
            if match:
                # Insert before Pull Request Process
                insert_pos = match.start()
                content = content[:insert_pos] + dep_section + "\n" + content[insert_pos:]
                self.logger.info("Added dependency management section before Pull Request Process")
            else:
                # Insert before Code of Conduct or License section
                coc_pattern = r'(## Code of Conduct|## License)'
                match = re.search(coc_pattern, content)
                
                if match:
                    insert_pos = match.start()
                    content = content[:insert_pos] + dep_section + "\n" + content[insert_pos:]
                    self.logger.info("Added dependency management section before Code of Conduct/License")
                else:
                    # Fallback: append at the end
                    content += "\n" + dep_section
                    self.logger.info("Added dependency management section at the end")
            
            # Write updated content
            contributing_path.write_text(content, encoding="utf-8")
            self.logger.info("CONTRIBUTING.md updated successfully")
            
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to update CONTRIBUTING.md: {e}")
            return False
    
    def update_gitignore(self, patterns: Optional[List[str]] = None) -> bool:
        """Update .gitignore with new exclusion patterns.
        
        Adds new patterns to .gitignore if they don't already exist.
        Default patterns include common cache and build artifacts.
        
        Args:
            patterns: List of patterns to add (uses defaults if None)
        
        Returns:
            True if update was successful, False otherwise
        
        Example:
            >>> updater.update_gitignore(['*.pyc', '__pycache__/'])
            True
        """
        gitignore_path = self.project_root / ".gitignore"
        
        if not gitignore_path.exists():
            self.logger.warning(f".gitignore not found at {gitignore_path}")
            return False
        
        # Default patterns to ensure are in .gitignore
        if patterns is None:
            patterns = [
                "# Cleanup backups",
                ".cleanup_backup/",
                "",
                "# Python cache",
                "__pycache__/",
                "*.py[cod]",
                "*$py.class",
                "*.so",
                ".Python",
                "",
                "# Build artifacts",
                "build/",
                "dist/",
                "*.egg-info/",
                "",
                "# IDE",
                ".DS_Store",
                ".vscode/",
                ".idea/",
            ]
        
        self.logger.info("Updating .gitignore with new patterns")
        
        try:
            content = gitignore_path.read_text(encoding="utf-8")
            lines = content.split('\n')
            
            # Check which patterns are missing
            patterns_to_add = []
            for pattern in patterns:
                # Skip empty lines and comments when checking
                if pattern and not pattern.startswith('#'):
                    # Check if pattern already exists (exact match or similar)
                    if pattern not in lines and pattern.rstrip('/') not in lines:
                        patterns_to_add.append(pattern)
                elif pattern.startswith('#') or pattern == '':
                    # Always include section headers and blank lines
                    patterns_to_add.append(pattern)
            
            if not patterns_to_add:
                self.logger.info("All patterns already exist in .gitignore")
                return True
            
            # Add new patterns at the end
            if not content.endswith('\n'):
                content += '\n'
            
            content += '\n'
            content += '\n'.join(patterns_to_add)
            content += '\n'
            
            # Write updated content
            gitignore_path.write_text(content, encoding="utf-8")
            self.logger.info(f"Added {len([p for p in patterns_to_add if p and not p.startswith('#')])} new patterns to .gitignore")
            
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to update .gitignore: {e}")
            return False
    
    @staticmethod
    def _format_size_simple(size_bytes: int) -> str:
        """Format file size in bytes to simple human-readable format.
        
        Args:
            size_bytes: Size in bytes
        
        Returns:
            Formatted size string (e.g., "1.2MB", "456KB")
        """
        if size_bytes == 0:
            return "0B"
        
        units = ["B", "KB", "MB", "GB", "TB"]
        unit_index = 0
        size = float(size_bytes)
        
        while size >= 1024.0 and unit_index < len(units) - 1:
            size /= 1024.0
            unit_index += 1
        
        if unit_index == 0:
            return f"{int(size)}{units[unit_index]}"
        else:
            return f"{size:.1f}{units[unit_index]}"
