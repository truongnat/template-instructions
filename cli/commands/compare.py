"""
Comparison commands.

Provides CLI commands for comparing current project structure against v2 suggestions.
"""

import argparse
import sys
from pathlib import Path
from typing import Optional

# Add project root to path
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from cli.output.formatters import (
    format_success, format_error, format_warning, format_info,
    format_header, format_subheader
)


def run_comparison(args: argparse.Namespace) -> int:
    """
    Run V2 structure comparison.
    
    Args:
        args: Command arguments with project root, v2 docs path, and options
        
    Returns:
        Exit code (0 for success, 1 for error)
    """
    try:
        from agentic_sdlc.comparison.engine import ComparisonEngine, ComparisonEngineError
        
        # Get paths
        project_root = args.project_root or "."
        v2_docs_path = args.v2_docs or "claude_suggestion/v2"
        output_file = args.output or "comparison_report.md"
        status_file = args.status_file
        generate_scripts = args.generate_scripts
        no_validation = args.no_validation
        
        # Display configuration
        if args.verbose:
            print(format_header("V2 Structure Comparison"))
            print(format_info(f"Project root: {project_root}"))
            print(format_info(f"V2 docs path: {v2_docs_path}"))
            print(format_info(f"Output file: {output_file}"))
            if status_file:
                print(format_info(f"Status file: {status_file}"))
            if generate_scripts:
                print(format_info("Migration scripts: enabled"))
            print()
        
        # Initialize engine
        if args.verbose:
            print("Initializing comparison engine...")
        
        engine = ComparisonEngine(
            project_root=project_root,
            v2_docs_path=v2_docs_path,
            status_file_path=status_file
        )
        
        # Run comparison
        if args.verbose:
            print("Running comparison analysis...")
        
        result = engine.run_comparison(
            generate_migration_scripts=generate_scripts,
            check_validation=not no_validation
        )
        
        # Save report
        if args.verbose:
            print(f"Saving report to {output_file}...")
        
        engine.save_report(result['report'], output_file)
        
        # Save migration scripts if generated
        if generate_scripts and result.get('migration_scripts'):
            scripts_dir = args.scripts_output or "migration_scripts"
            if args.verbose:
                print(f"Saving migration scripts to {scripts_dir}/...")
            
            engine.save_migration_scripts(result['migration_scripts'], scripts_dir)
            print(format_success(f"Migration scripts saved to {scripts_dir}/"))
        
        # Display summary
        comparison = result['comparison']
        print()
        print(format_header("Comparison Summary"))
        print(f"Overall completion: {comparison.completion_percentage:.1f}%")
        print(f"  {format_success(f'Implemented: {comparison.implemented_count}')}")
        print(f"  {format_warning(f'Partial: {comparison.partial_count}')}")
        print(f"  {format_error(f'Missing: {comparison.missing_count}')}")
        
        # Display gaps summary
        gaps = result['gaps']
        if gaps:
            print()
            print(format_subheader(f"Identified {len(gaps)} gaps"))
            
            # Count by priority
            high_priority = sum(1 for g in gaps if g.priority == "High")
            medium_priority = sum(1 for g in gaps if g.priority == "Medium")
            low_priority = sum(1 for g in gaps if g.priority == "Low")
            
            if high_priority > 0:
                print(f"  {format_error(f'High priority: {high_priority}')}")
            if medium_priority > 0:
                print(f"  {format_warning(f'Medium priority: {medium_priority}')}")
            if low_priority > 0:
                print(f"  {format_info(f'Low priority: {low_priority}')}")
        
        # Display conflicts summary
        conflicts = result['conflicts']
        if conflicts:
            print()
            print(format_warning(f"Found {len(conflicts)} potential conflicts"))
            
            # Count by severity
            high_severity = sum(1 for c in conflicts if c.severity == "High")
            medium_severity = sum(1 for c in conflicts if c.severity == "Medium")
            low_severity = sum(1 for c in conflicts if c.severity == "Low")
            
            if high_severity > 0:
                print(f"  {format_error(f'High severity: {high_severity}')}")
            if medium_severity > 0:
                print(f"  {format_warning(f'Medium severity: {medium_severity}')}")
            if low_severity > 0:
                print(f"  {format_info(f'Low severity: {low_severity}')}")
        
        # Display validation results if available
        if result.get('validation_results'):
            validation = result['validation_results']
            if validation.get('superseded'):
                print()
                print(format_info(f"Found {len(validation['superseded'])} superseded suggestions"))
            if validation.get('inapplicable'):
                print()
                print(format_warning(f"Found {len(validation['inapplicable'])} potentially inapplicable suggestions"))
        
        print()
        print(format_success(f"Comparison report saved to {output_file}"))
        
        if args.verbose:
            print()
            print(format_info("Review the report for detailed analysis and recommendations"))
        
        return 0
        
    except ComparisonEngineError as e:
        print(format_error(f"Comparison failed: {e}"))
        if e.recovery:
            print(format_info(f"Suggestion: {e.recovery}"))
        return 1
    except FileNotFoundError as e:
        print(format_error(f"File not found: {e}"))
        print(format_info("Check that project root and v2 docs path are correct"))
        return 1
    except Exception as e:
        print(format_error(f"Unexpected error: {e}"))
        if args.verbose:
            import traceback
            traceback.print_exc()
        return 1


def setup_compare_parser(subparsers) -> None:
    """
    Set up the compare command parser.
    
    Args:
        subparsers: Subparsers object from argparse
    """
    compare_parser = subparsers.add_parser(
        "compare",
        help="Compare current structure against v2 suggestions",
        description="""
Compare the current project structure against v2 improvement suggestions.

This command analyzes the current project structure, parses v2 suggestion documents,
identifies gaps and conflicts, and generates a comprehensive comparison report with
actionable recommendations.
        """,
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Basic comparison with default paths
  sdlc-kit compare
  
  # Specify custom paths
  sdlc-kit compare --project-root /path/to/project --v2-docs /path/to/v2/docs
  
  # Generate migration scripts
  sdlc-kit compare --generate-scripts
  
  # Use status tracking file
  sdlc-kit compare --status-file .comparison_status.json
  
  # Verbose output with custom output file
  sdlc-kit compare --verbose --output detailed_report.md
  
  # Generate scripts to custom directory
  sdlc-kit compare --generate-scripts --scripts-output ./scripts
        """
    )
    
    # Positional arguments (none for compare)
    
    # Path options
    compare_parser.add_argument(
        "--project-root",
        "-p",
        help="Path to project root directory (default: current directory)",
        default=None
    )
    
    compare_parser.add_argument(
        "--v2-docs",
        "-d",
        help="Path to v2 suggestion documents directory (default: claude_suggestion/v2)",
        default=None
    )
    
    # Output options
    compare_parser.add_argument(
        "--output",
        "-o",
        help="Output file path for comparison report (default: comparison_report.md)",
        default=None
    )
    
    compare_parser.add_argument(
        "--status-file",
        "-s",
        help="Path to status tracking file (optional)",
        default=None
    )
    
    # Feature flags
    compare_parser.add_argument(
        "--generate-scripts",
        "-g",
        action="store_true",
        help="Generate migration scripts for structural changes"
    )
    
    compare_parser.add_argument(
        "--scripts-output",
        help="Output directory for migration scripts (default: migration_scripts)",
        default=None
    )
    
    compare_parser.add_argument(
        "--no-validation",
        action="store_true",
        help="Skip validation checks for superseded/inapplicable suggestions"
    )
    
    # Verbosity
    compare_parser.add_argument(
        "--verbose",
        "-v",
        action="store_true",
        help="Enable verbose output"
    )
    
    compare_parser.set_defaults(func=run_comparison)


def main():
    """Main entry point for comparison commands."""
    parser = argparse.ArgumentParser(description="Comparison commands")
    subparsers = parser.add_subparsers(dest="command")
    setup_compare_parser(subparsers)
    
    args = parser.parse_args()
    
    if hasattr(args, 'func'):
        sys.exit(args.func(args))
    else:
        parser.print_help()
        sys.exit(1)


if __name__ == "__main__":
    main()
