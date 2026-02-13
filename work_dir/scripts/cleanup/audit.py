"""
Audit Engine for the Project Audit and Cleanup System.

This module provides the AuditEngine class that orchestrates the audit process
by integrating FileScanner and FileCategorizer to scan the project, categorize
files, calculate size impact, and generate comprehensive audit reports.
"""

from pathlib import Path
from datetime import datetime
from typing import List, Optional

from .models import (
    ProjectInventory,
    CategorizedFiles,
    SizeImpact,
    AuditReport,
    FileInfo,
    DirectoryInfo,
    FileCategory,
)
from .scanner import FileScanner
from .categorizer import FileCategorizer
from .logger import get_logger


class AuditEngine:
    """Orchestrate project audit by scanning, categorizing, and reporting.
    
    The AuditEngine integrates FileScanner and FileCategorizer to perform
    a complete audit of the project. It scans all files, categorizes them
    into KEEP/REMOVE/CONSOLIDATE/ARCHIVE, calculates the size impact of
    cleanup operations, and generates a comprehensive markdown report.
    
    Attributes:
        scanner: FileScanner instance for directory scanning
        categorizer: FileCategorizer instance for file categorization
        logger: Logger instance for operation logging
    
    Example:
        >>> scanner = FileScanner()
        >>> categorizer = FileCategorizer()
        >>> engine = AuditEngine(scanner, categorizer)
        >>> report = engine.generate_report(Path("."))
        >>> print(f"Total files: {report.total_files}")
        >>> print(f"Size reduction: {report.size_impact.reduction_percent:.1f}%")
    """
    
    def __init__(
        self,
        scanner: FileScanner,
        categorizer: FileCategorizer,
        verbose: bool = False
    ):
        """Initialize the AuditEngine.
        
        Args:
            scanner: FileScanner instance for scanning directories
            categorizer: FileCategorizer instance for categorizing files
            verbose: Enable verbose logging
        """
        self.scanner = scanner
        self.categorizer = categorizer
        self.logger = get_logger(verbose=verbose)
        self._inventory: Optional[ProjectInventory] = None
        self._categorized: Optional[CategorizedFiles] = None
    
    def scan_project(self, root_path: Path) -> ProjectInventory:
        """Scan entire project structure and create inventory.
        
        This method uses the FileScanner to recursively scan the project
        directory and collect metadata for all files and directories.
        
        Args:
            root_path: Root directory of the project to scan
            
        Returns:
            ProjectInventory containing all files and directories
            
        Raises:
            FileNotFoundError: If root_path does not exist
            PermissionError: If root_path is not accessible
            
        Example:
            >>> engine = AuditEngine(scanner, categorizer)
            >>> inventory = engine.scan_project(Path("."))
            >>> print(f"Found {len(inventory.all_files)} files")
            >>> print(f"Total size: {inventory.total_size / (1024*1024):.2f} MB")
        """
        self.logger.info(f"Scanning project at: {root_path}")
        
        # Scan all files
        all_files = self.scanner.scan(root_path)
        
        # Calculate total size
        total_size = sum(f.size for f in all_files)
        
        # Get unique directories from file paths
        dir_paths = set()
        for file_info in all_files:
            # Add all parent directories
            current = file_info.path.parent
            while current != root_path and current != current.parent:
                dir_paths.add(current)
                current = current.parent
        
        # Create DirectoryInfo objects for each directory
        all_directories = []
        for dir_path in sorted(dir_paths):
            try:
                dir_info = self.scanner.get_directory_info(dir_path)
                all_directories.append(dir_info)
            except (FileNotFoundError, NotADirectoryError, PermissionError) as e:
                self.logger.warning(f"Could not get info for directory {dir_path}: {e}")
                continue
        
        self._inventory = ProjectInventory(
            all_files=all_files,
            all_directories=all_directories,
            total_size=total_size
        )
        
        self.logger.info(
            f"Scan complete: {len(all_files)} files, "
            f"{len(all_directories)} directories, "
            f"{total_size / (1024*1024):.2f} MB"
        )
        
        return self._inventory
    
    def categorize_files(self, inventory: ProjectInventory) -> CategorizedFiles:
        """Categorize files into KEEP/REMOVE/CONSOLIDATE/ARCHIVE.
        
        This method applies categorization rules to all files in the inventory
        and organizes them by their assigned category.
        
        Args:
            inventory: ProjectInventory from scan_project()
            
        Returns:
            CategorizedFiles with files organized by category
            
        Example:
            >>> engine = AuditEngine(scanner, categorizer)
            >>> inventory = engine.scan_project(Path("."))
            >>> categorized = engine.categorize_files(inventory)
            >>> print(f"Files to keep: {len(categorized.keep)}")
            >>> print(f"Files to remove: {len(categorized.remove)}")
        """
        self.logger.info("Categorizing files...")
        
        categorized = CategorizedFiles()
        
        for file_info in inventory.all_files:
            # Categorize the file
            category = self.categorizer.categorize(file_info)
            file_info.category = category
            
            # Add to appropriate list
            if category == FileCategory.KEEP:
                categorized.keep.append(file_info)
            elif category == FileCategory.REMOVE:
                categorized.remove.append(file_info)
            elif category == FileCategory.CONSOLIDATE:
                categorized.consolidate.append(file_info)
            elif category == FileCategory.ARCHIVE:
                categorized.archive.append(file_info)
        
        self._categorized = categorized
        
        self.logger.info(
            f"Categorization complete: "
            f"KEEP={len(categorized.keep)}, "
            f"REMOVE={len(categorized.remove)}, "
            f"CONSOLIDATE={len(categorized.consolidate)}, "
            f"ARCHIVE={len(categorized.archive)}"
        )
        
        return categorized
    
    def calculate_impact(self) -> SizeImpact:
        """Calculate size impact of cleanup operations.
        
        This method calculates the current size, projected size after cleanup,
        and the reduction in both absolute and percentage terms.
        
        Returns:
            SizeImpact with size calculations
            
        Raises:
            RuntimeError: If scan_project() and categorize_files() haven't been called
            
        Example:
            >>> engine = AuditEngine(scanner, categorizer)
            >>> inventory = engine.scan_project(Path("."))
            >>> categorized = engine.categorize_files(inventory)
            >>> impact = engine.calculate_impact()
            >>> print(f"Will free {impact.reduction / (1024*1024):.2f} MB")
            >>> print(f"Reduction: {impact.reduction_percent:.1f}%")
        """
        if self._inventory is None or self._categorized is None:
            raise RuntimeError(
                "Must call scan_project() and categorize_files() before calculate_impact()"
            )
        
        self.logger.info("Calculating size impact...")
        
        current_size = self._inventory.total_size
        
        # Calculate size to be removed (remove + archive categories)
        size_to_remove = sum(f.size for f in self._categorized.remove)
        size_to_archive = sum(f.size for f in self._categorized.archive)
        total_reduction = size_to_remove + size_to_archive
        
        projected_size = current_size - total_reduction
        
        # Calculate percentage reduction
        if current_size > 0:
            reduction_percent = (total_reduction / current_size) * 100
        else:
            reduction_percent = 0.0
        
        impact = SizeImpact(
            current_size=current_size,
            projected_size=projected_size,
            reduction=total_reduction,
            reduction_percent=reduction_percent
        )
        
        self.logger.info(
            f"Size impact: {current_size / (1024*1024):.2f} MB -> "
            f"{projected_size / (1024*1024):.2f} MB "
            f"({reduction_percent:.1f}% reduction)"
        )
        
        return impact
    
    def generate_report(self, root_path: Path) -> AuditReport:
        """Generate comprehensive audit report.
        
        This method performs a complete audit: scanning, categorizing,
        calculating impact, and generating recommendations.
        
        Args:
            root_path: Root directory of the project to audit
            
        Returns:
            AuditReport with complete audit information
            
        Example:
            >>> engine = AuditEngine(scanner, categorizer)
            >>> report = engine.generate_report(Path("."))
            >>> markdown = engine.format_report_markdown(report)
            >>> Path("audit-report.md").write_text(markdown)
        """
        self.logger.info("Generating audit report...")
        
        # Perform scan
        inventory = self.scan_project(root_path)
        
        # Categorize files
        categorized = self.categorize_files(inventory)
        
        # Calculate impact
        impact = self.calculate_impact()
        
        # Generate recommendations
        recommendations = self._generate_recommendations(categorized, impact)
        
        report = AuditReport(
            timestamp=datetime.now(),
            total_files=len(inventory.all_files),
            categorized_files=categorized,
            size_impact=impact,
            recommendations=recommendations
        )
        
        self.logger.info("Audit report generated successfully")
        
        return report
    
    def _generate_recommendations(
        self,
        categorized: CategorizedFiles,
        impact: SizeImpact
    ) -> List[str]:
        """Generate recommendations based on audit results.
        
        Args:
            categorized: Categorized files
            impact: Size impact calculation
            
        Returns:
            List of recommendation strings
        """
        recommendations = []
        
        # Recommendation based on size reduction
        if impact.reduction_percent > 50:
            recommendations.append(
                f"Significant size reduction possible: {impact.reduction_percent:.1f}% "
                f"({impact.reduction / (1024*1024):.2f} MB)"
            )
        elif impact.reduction_percent > 10:
            recommendations.append(
                f"Moderate size reduction possible: {impact.reduction_percent:.1f}% "
                f"({impact.reduction / (1024*1024):.2f} MB)"
            )
        else:
            recommendations.append(
                f"Minimal size reduction: {impact.reduction_percent:.1f}% "
                f"({impact.reduction / (1024*1024):.2f} MB)"
            )
        
        # Recommendation for corrupt directories
        corrupt_files = [
            f for f in categorized.remove
            if "_corrupt_" in str(f.path)
        ]
        if corrupt_files:
            corrupt_size = sum(f.size for f in corrupt_files)
            recommendations.append(
                f"Found {len(corrupt_files)} files in corrupt directories "
                f"({corrupt_size / (1024*1024):.2f} MB) - safe to remove"
            )
        
        # Recommendation for cache files
        if categorized.remove or categorized.archive:
            cache_count = len(categorized.remove) + len(categorized.archive)
            cache_size = sum(f.size for f in categorized.remove) + sum(f.size for f in categorized.archive)
            recommendations.append(
                f"Found {cache_count} cache files "
                f"({cache_size / (1024*1024):.2f} MB) - can be regenerated"
            )
        
        # Recommendation for dependency consolidation
        if categorized.consolidate:
            recommendations.append(
                f"Found {len(categorized.consolidate)} requirements files to consolidate "
                "into pyproject.toml"
            )
        
        # Recommendation for backup
        if categorized.remove or categorized.archive:
            recommendations.append(
                "Create backup before cleanup to enable rollback if needed"
            )
        
        # Recommendation for validation
        recommendations.append(
            "Run validation tests after cleanup to ensure package integrity"
        )
        
        return recommendations
    
    def format_report_markdown(self, report: AuditReport) -> str:
        """Format audit report as markdown.
        
        Args:
            report: AuditReport to format
            
        Returns:
            Markdown-formatted report string
            
        Example:
            >>> engine = AuditEngine(scanner, categorizer)
            >>> report = engine.generate_report(Path("."))
            >>> markdown = engine.format_report_markdown(report)
            >>> print(markdown)
        """
        lines = []
        
        # Header
        lines.append("# Cleanup Audit Report")
        lines.append("")
        lines.append(f"**Generated**: {report.timestamp.strftime('%Y-%m-%d %H:%M:%S')}")
        lines.append(f"**Project**: Agentic SDLC")
        lines.append("")
        
        # Summary
        lines.append("## Summary")
        lines.append("")
        lines.append(f"- Total Files Scanned: {report.total_files:,}")
        lines.append(f"- Files to Keep: {len(report.categorized_files.keep):,}")
        lines.append(f"- Files to Remove: {len(report.categorized_files.remove):,}")
        lines.append(f"- Files to Consolidate: {len(report.categorized_files.consolidate):,}")
        lines.append(f"- Files to Archive: {len(report.categorized_files.archive):,}")
        lines.append("")
        
        # Size Impact
        lines.append("## Size Impact")
        lines.append("")
        lines.append(f"- Current Size: {report.size_impact.current_size / (1024*1024):.2f} MB")
        lines.append(f"- After Cleanup: {report.size_impact.projected_size / (1024*1024):.2f} MB")
        lines.append(f"- Reduction: {report.size_impact.reduction / (1024*1024):.2f} MB ({report.size_impact.reduction_percent:.1f}%)")
        lines.append("")
        
        # Files to Remove
        if report.categorized_files.remove:
            lines.append("## Files to Remove")
            lines.append("")
            
            # Group by reason
            remove_by_reason = {}
            for file_info in report.categorized_files.remove:
                reason = file_info.reason
                if reason not in remove_by_reason:
                    remove_by_reason[reason] = []
                remove_by_reason[reason].append(file_info)
            
            for reason, files in sorted(remove_by_reason.items()):
                total_size = sum(f.size for f in files)
                lines.append(f"### {reason} ({len(files)} items, {total_size / (1024*1024):.2f} MB)")
                lines.append("")
                
                # Show first 10 files
                for file_info in sorted(files, key=lambda f: f.size, reverse=True)[:10]:
                    lines.append(f"- `{file_info.path}` ({file_info.size / (1024*1024):.2f} MB)")
                
                if len(files) > 10:
                    lines.append(f"- ... and {len(files) - 10} more files")
                
                lines.append("")
        
        # Files to Consolidate
        if report.categorized_files.consolidate:
            lines.append("## Files to Consolidate")
            lines.append("")
            
            for file_info in report.categorized_files.consolidate:
                lines.append(f"- `{file_info.path}` - {file_info.reason}")
            
            lines.append("")
        
        # Files to Archive
        if report.categorized_files.archive:
            lines.append("## Files to Archive")
            lines.append("")
            
            total_archive_size = sum(f.size for f in report.categorized_files.archive)
            lines.append(f"**Total**: {len(report.categorized_files.archive)} files, {total_archive_size / (1024*1024):.2f} MB")
            lines.append("")
            
            # Group by directory
            archive_by_dir = {}
            for file_info in report.categorized_files.archive:
                dir_name = file_info.path.parts[0] if file_info.path.parts else "root"
                if dir_name not in archive_by_dir:
                    archive_by_dir[dir_name] = []
                archive_by_dir[dir_name].append(file_info)
            
            for dir_name, files in sorted(archive_by_dir.items()):
                dir_size = sum(f.size for f in files)
                lines.append(f"### {dir_name}/ ({len(files)} files, {dir_size / (1024*1024):.2f} MB)")
                lines.append("")
        
        # Recommendations
        if report.recommendations:
            lines.append("## Recommendations")
            lines.append("")
            
            for i, rec in enumerate(report.recommendations, 1):
                lines.append(f"{i}. {rec}")
            
            lines.append("")
        
        return "\n".join(lines)
