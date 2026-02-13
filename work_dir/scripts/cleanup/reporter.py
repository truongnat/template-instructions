"""
Report Generator for Project Audit and Cleanup System.

This module provides the ReportGenerator class for creating markdown reports
for audit results and cleanup summaries. Reports are saved to the docs/
directory with timestamps.

Key Features:
    - Generate audit reports with file categorization
    - Generate cleanup summaries with statistics
    - Format file sizes (bytes to MB/GB)
    - Format timestamps consistently
    - Save reports to docs/ directory

Requirements Addressed:
    - 8.1: Generate markdown audit report
    - 8.2: Categorize files in report (KEEP/REMOVE/CONSOLIDATE/ARCHIVE)
    - 8.3: Include file sizes and total size impact
    - 8.4: List dependencies to be consolidated
    - 8.5: Save report to docs/ with timestamp
    - 14.2: Create cleanup summary documentation
"""

from pathlib import Path
from datetime import datetime
from typing import Optional

from .models import (
    AuditReport,
    CleanupResult,
    CategorizedFiles,
    SizeImpact,
    FileInfo,
)
from .logger import get_logger


class ReportGenerator:
    """Generate and save markdown reports for audit and cleanup operations.
    
    The ReportGenerator creates human-readable markdown reports for:
    - Audit reports: Complete analysis of project files before cleanup
    - Cleanup summaries: Results and statistics after cleanup operations
    
    Reports include formatted file sizes, timestamps, and categorized file lists.
    All reports are saved to the docs/ directory with timestamps in filenames.
    
    Attributes:
        docs_dir: Directory where reports are saved (default: docs/)
        logger: Logger instance for operation tracking
    
    Example:
        >>> generator = ReportGenerator(docs_dir=Path("docs"))
        >>> report_path = generator.save_audit_report(audit_report)
        >>> print(f"Report saved to: {report_path}")
    """
    
    def __init__(self, docs_dir: Path = Path("docs"), verbose: bool = False):
        """Initialize ReportGenerator.
        
        Args:
            docs_dir: Directory where reports will be saved
            verbose: Enable verbose logging
        """
        self.docs_dir = Path(docs_dir)
        self.logger = get_logger(verbose=verbose)
        
        # Create docs directory if it doesn't exist
        self.docs_dir.mkdir(parents=True, exist_ok=True)
        
        self.logger.info(f"ReportGenerator initialized with docs_dir: {self.docs_dir}")
    
    def generate_audit_report(self, report: AuditReport) -> str:
        """Generate markdown audit report.
        
        Creates a comprehensive markdown report showing:
        - Summary statistics (file counts by category)
        - Size impact analysis
        - Files to remove (grouped by reason)
        - Files to consolidate
        - Files to archive
        - Recommendations
        
        Args:
            report: AuditReport with audit results
        
        Returns:
            Markdown-formatted report string
        
        Example:
            >>> markdown = generator.generate_audit_report(audit_report)
            >>> print(markdown)
        """
        self.logger.info("Generating audit report markdown")
        
        lines = []
        
        # Header
        lines.append("# Cleanup Audit Report")
        lines.append("")
        lines.append(f"**Generated**: {self.format_timestamp(report.timestamp)}")
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
        lines.append(f"- Current Size: {self.format_size(report.size_impact.current_size)}")
        lines.append(f"- After Cleanup: {self.format_size(report.size_impact.projected_size)}")
        lines.append(f"- Reduction: {self.format_size(report.size_impact.reduction)} ({report.size_impact.reduction_percent:.1f}%)")
        lines.append("")
        
        # Files to Remove
        if report.categorized_files.remove:
            lines.append("## Files to Remove")
            lines.append("")
            
            # Group by reason
            remove_by_reason = {}
            for file_info in report.categorized_files.remove:
                reason = file_info.reason or "Unspecified"
                if reason not in remove_by_reason:
                    remove_by_reason[reason] = []
                remove_by_reason[reason].append(file_info)
            
            for reason, files in sorted(remove_by_reason.items()):
                total_size = sum(f.size for f in files)
                lines.append(f"### {reason} ({len(files)} items, {self.format_size(total_size)})")
                lines.append("")
                
                # Show first 10 files, sorted by size (largest first)
                for file_info in sorted(files, key=lambda f: f.size, reverse=True)[:10]:
                    lines.append(f"- `{file_info.path}` ({self.format_size(file_info.size)})")
                
                if len(files) > 10:
                    lines.append(f"- ... and {len(files) - 10} more files")
                
                lines.append("")
        
        # Files to Consolidate
        if report.categorized_files.consolidate:
            lines.append("## Files to Consolidate")
            lines.append("")
            lines.append("The following requirements files will be merged into `pyproject.toml`:")
            lines.append("")
            
            for file_info in report.categorized_files.consolidate:
                reason = file_info.reason or "Dependency consolidation"
                lines.append(f"- `{file_info.path}` - {reason}")
            
            lines.append("")
        
        # Files to Archive
        if report.categorized_files.archive:
            lines.append("## Files to Archive")
            lines.append("")
            
            total_archive_size = sum(f.size for f in report.categorized_files.archive)
            lines.append(f"**Total**: {len(report.categorized_files.archive)} files, {self.format_size(total_archive_size)}")
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
                lines.append(f"### {dir_name}/ ({len(files)} files, {self.format_size(dir_size)})")
                lines.append("")
        
        # Recommendations
        if report.recommendations:
            lines.append("## Recommendations")
            lines.append("")
            
            for i, rec in enumerate(report.recommendations, 1):
                lines.append(f"{i}. {rec}")
            
            lines.append("")
        
        # Footer
        lines.append("---")
        lines.append("")
        lines.append("*This report was generated automatically by the Project Audit and Cleanup System.*")
        lines.append("")
        
        self.logger.info("Audit report markdown generated successfully")
        
        return "\n".join(lines)
    
    def generate_cleanup_summary(self, result: CleanupResult) -> str:
        """Generate markdown cleanup summary.
        
        Creates a summary report showing:
        - Cleanup operation results
        - Files removed and size freed
        - Backup information
        - Validation results
        - Any errors encountered
        
        Args:
            result: CleanupResult with cleanup operation results
        
        Returns:
            Markdown-formatted summary string
        
        Example:
            >>> summary = generator.generate_cleanup_summary(cleanup_result)
            >>> print(summary)
        """
        self.logger.info("Generating cleanup summary markdown")
        
        lines = []
        
        # Header
        lines.append("# Cleanup Summary")
        lines.append("")
        lines.append(f"**Completed**: {self.format_timestamp(datetime.now())}")
        lines.append(f"**Status**: {'✅ Success' if result.success else '❌ Failed'}")
        lines.append("")
        
        # Statistics
        lines.append("## Statistics")
        lines.append("")
        lines.append(f"- Files Removed: {result.files_removed:,}")
        lines.append(f"- Size Freed: {self.format_size(result.size_freed)}")
        lines.append(f"- Backup ID: `{result.backup_id}`")
        lines.append("")
        
        # Validation Results
        if result.validation_result:
            lines.append("## Validation Results")
            lines.append("")
            
            val = result.validation_result
            lines.append(f"- Overall: {'✅ Passed' if val.passed else '❌ Failed'}")
            lines.append(f"- Import Check: {'✅ Passed' if val.import_check else '❌ Failed'}")
            lines.append(f"- CLI Check: {'✅ Passed' if val.cli_check else '❌ Failed'}")
            lines.append(f"- Test Suite: {'✅ Passed' if val.test_check else '❌ Failed'}")
            lines.append(f"- Package Build: {'✅ Passed' if val.build_check else '❌ Failed'}")
            lines.append("")
            
            if val.errors:
                lines.append("### Validation Errors")
                lines.append("")
                for error in val.errors:
                    lines.append(f"- {error}")
                lines.append("")
        
        # Errors
        if result.errors:
            lines.append("## Errors Encountered")
            lines.append("")
            for error in result.errors:
                lines.append(f"- {error}")
            lines.append("")
        
        # Backup Information
        if result.backup_id:
            lines.append("## Backup Information")
            lines.append("")
            lines.append(f"A backup was created before cleanup: `{result.backup_id}`")
            lines.append("")
            lines.append("To restore from this backup, run:")
            lines.append("```bash")
            lines.append(f"python scripts/cleanup.py --rollback {result.backup_id}")
            lines.append("```")
            lines.append("")
        
        # Next Steps
        lines.append("## Next Steps")
        lines.append("")
        
        if result.success:
            lines.append("1. Review the changes and verify package functionality")
            lines.append("2. Run tests to ensure everything works correctly")
            lines.append("3. Commit the changes to version control")
            lines.append("4. Consider removing the backup after verification")
        else:
            lines.append("1. Review the errors above")
            lines.append("2. Fix any issues that caused the cleanup to fail")
            lines.append("3. If needed, restore from backup using the command above")
            lines.append("4. Re-run the cleanup after fixing issues")
        
        lines.append("")
        
        # Footer
        lines.append("---")
        lines.append("")
        lines.append("*This summary was generated automatically by the Project Audit and Cleanup System.*")
        lines.append("")
        
        self.logger.info("Cleanup summary markdown generated successfully")
        
        return "\n".join(lines)
    
    def save_audit_report(self, report: AuditReport) -> Path:
        """Generate and save audit report to docs/ directory.
        
        Args:
            report: AuditReport to save
        
        Returns:
            Path to the saved report file
        
        Example:
            >>> report_path = generator.save_audit_report(audit_report)
            >>> print(f"Report saved to: {report_path}")
        """
        self.logger.info("Saving audit report to docs/")
        
        # Generate markdown
        markdown = self.generate_audit_report(report)
        
        # Create filename with timestamp
        timestamp_str = report.timestamp.strftime("%Y%m%d_%H%M%S")
        filename = f"CLEANUP-AUDIT-REPORT-{timestamp_str}.md"
        report_path = self.docs_dir / filename
        
        # Save to file
        report_path.write_text(markdown, encoding="utf-8")
        
        self.logger.info(f"Audit report saved to: {report_path}")
        
        return report_path
    
    def save_cleanup_summary(self, result: CleanupResult) -> Path:
        """Generate and save cleanup summary to docs/ directory.
        
        Args:
            result: CleanupResult to save
        
        Returns:
            Path to the saved summary file
        
        Example:
            >>> summary_path = generator.save_cleanup_summary(cleanup_result)
            >>> print(f"Summary saved to: {summary_path}")
        """
        self.logger.info("Saving cleanup summary to docs/")
        
        # Generate markdown
        markdown = self.generate_cleanup_summary(result)
        
        # Create filename with timestamp
        timestamp_str = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"CLEANUP-SUMMARY-{timestamp_str}.md"
        summary_path = self.docs_dir / filename
        
        # Save to file
        summary_path.write_text(markdown, encoding="utf-8")
        
        self.logger.info(f"Cleanup summary saved to: {summary_path}")
        
        return summary_path
    
    @staticmethod
    def format_size(size_bytes: int) -> str:
        """Format file size in bytes to human-readable format.
        
        Converts bytes to the most appropriate unit (B, KB, MB, GB, TB)
        with 2 decimal places.
        
        Args:
            size_bytes: Size in bytes
        
        Returns:
            Formatted size string (e.g., "1.23 MB", "456.78 KB")
        
        Example:
            >>> ReportGenerator.format_size(1024)
            '1.00 KB'
            >>> ReportGenerator.format_size(1536000)
            '1.46 MB'
            >>> ReportGenerator.format_size(0)
            '0 B'
        """
        if size_bytes == 0:
            return "0 B"
        
        units = ["B", "KB", "MB", "GB", "TB"]
        unit_index = 0
        size = float(size_bytes)
        
        while size >= 1024.0 and unit_index < len(units) - 1:
            size /= 1024.0
            unit_index += 1
        
        # Format with 2 decimal places, but remove trailing zeros
        if unit_index == 0:
            # Bytes - no decimal places
            return f"{int(size)} {units[unit_index]}"
        else:
            # Other units - 2 decimal places
            return f"{size:.2f} {units[unit_index]}"
    
    @staticmethod
    def format_timestamp(timestamp: datetime) -> str:
        """Format timestamp consistently for reports.
        
        Args:
            timestamp: Datetime object to format
        
        Returns:
            Formatted timestamp string (YYYY-MM-DD HH:MM:SS)
        
        Example:
            >>> dt = datetime(2026, 1, 31, 14, 30, 22)
            >>> ReportGenerator.format_timestamp(dt)
            '2026-01-31 14:30:22'
        """
        return timestamp.strftime("%Y-%m-%d %H:%M:%S")
