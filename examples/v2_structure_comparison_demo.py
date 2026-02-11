#!/usr/bin/env python3
"""
V2 Structure Comparison Demo

This script demonstrates how to use the V2 Structure Comparison feature
programmatically. It shows various ways to run comparisons, access results,
and generate custom reports.

Usage:
    python examples/v2_structure_comparison_demo.py
"""

import sys
from pathlib import Path

# Add project root to path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from agentic_sdlc.comparison.engine import ComparisonEngine, ComparisonEngineError
from agentic_sdlc.comparison.models import DirectoryStatus


def example_1_basic_comparison():
    """
    Example 1: Basic comparison with default settings.
    
    This is the simplest way to run a comparison - just provide the paths
    and let the engine handle everything.
    """
    print("=" * 70)
    print("Example 1: Basic Comparison")
    print("=" * 70)
    
    try:
        # Initialize the comparison engine
        engine = ComparisonEngine(
            project_root=".",
            v2_docs_path="claude_suggestion/v2"
        )
        
        # Run the comparison
        result = engine.run_comparison()
        
        # Access the comparison results
        comparison = result['comparison']
        print(f"\nCompletion: {comparison.completion_percentage:.1f}%")
        print(f"Implemented: {comparison.implemented_count}")
        print(f"Partial: {comparison.partial_count}")
        print(f"Missing: {comparison.missing_count}")
        
        # Save the report
        engine.save_report(result['report'], "comparison_report.md")
        print("\nReport saved to: comparison_report.md")
        
    except ComparisonEngineError as e:
        print(f"Error: {e}")
        if e.recovery:
            print(f"Suggestion: {e.recovery}")


def example_2_with_migration_scripts():
    """
    Example 2: Generate migration scripts along with the comparison.
    
    This example shows how to generate migration scripts that can help
    automate structural changes.
    """
    print("\n" + "=" * 70)
    print("Example 2: Comparison with Migration Scripts")
    print("=" * 70)
    
    try:
        engine = ComparisonEngine(
            project_root=".",
            v2_docs_path="claude_suggestion/v2"
        )
        
        # Run comparison with migration script generation enabled
        result = engine.run_comparison(generate_migration_scripts=True)
        
        # Check if migration scripts were generated
        if result.get('migration_scripts'):
            print(f"\nGenerated {len(result['migration_scripts'])} migration scripts:")
            for script_name in result['migration_scripts'].keys():
                print(f"  - {script_name}")
            
            # Save migration scripts to a directory
            engine.save_migration_scripts(
                result['migration_scripts'],
                "migration_scripts"
            )
            print("\nMigration scripts saved to: migration_scripts/")
        else:
            print("\nNo migration scripts needed")
        
    except ComparisonEngineError as e:
        print(f"Error: {e}")


def example_3_access_detailed_results():
    """
    Example 3: Access detailed comparison results.
    
    This example shows how to access and work with the detailed results
    from the comparison, including gaps, conflicts, and tasks.
    """
    print("\n" + "=" * 70)
    print("Example 3: Access Detailed Results")
    print("=" * 70)
    
    try:
        engine = ComparisonEngine(
            project_root=".",
            v2_docs_path="claude_suggestion/v2"
        )
        
        result = engine.run_comparison()
        
        # Access gaps
        gaps = result['gaps']
        print(f"\nIdentified {len(gaps)} gaps:")
        
        # Show high priority gaps
        high_priority_gaps = [g for g in gaps if g.priority == "High"]
        if high_priority_gaps:
            print(f"\nHigh Priority Gaps ({len(high_priority_gaps)}):")
            for gap in high_priority_gaps[:5]:  # Show first 5
                print(f"  - {gap.description}")
                print(f"    Effort: {gap.effort}, Action: {gap.proposed_action}")
        
        # Access conflicts
        conflicts = result['conflicts']
        if conflicts:
            print(f"\nFound {len(conflicts)} conflicts:")
            for conflict in conflicts[:3]:  # Show first 3
                print(f"  - {conflict.type}: {conflict.description}")
                print(f"    Severity: {conflict.severity}")
                if conflict.mitigation:
                    print(f"    Mitigation: {conflict.mitigation}")
        
        # Access generated tasks
        tasks = result['tasks']
        print(f"\nGenerated {len(tasks)} tasks:")
        
        # Show quick wins
        quick_wins = [t for t in tasks if "Quick Win" in t.category or t.effort_hours < 4]
        if quick_wins:
            print(f"\nQuick Wins ({len(quick_wins)}):")
            for task in quick_wins[:5]:  # Show first 5
                print(f"  - {task.title} ({task.effort_hours:.1f}h)")
        
    except ComparisonEngineError as e:
        print(f"Error: {e}")


def example_4_custom_report():
    """
    Example 4: Generate a custom report.
    
    This example shows how to access the raw data and create your own
    custom report format.
    """
    print("\n" + "=" * 70)
    print("Example 4: Generate Custom Report")
    print("=" * 70)
    
    try:
        engine = ComparisonEngine(
            project_root=".",
            v2_docs_path="claude_suggestion/v2"
        )
        
        result = engine.run_comparison()
        
        # Create a custom report
        custom_report = []
        custom_report.append("# Custom V2 Comparison Report")
        custom_report.append("")
        
        # Add executive summary
        comparison = result['comparison']
        custom_report.append("## Executive Summary")
        custom_report.append("")
        custom_report.append(f"Project completion: **{comparison.completion_percentage:.1f}%**")
        custom_report.append("")
        
        # Add directory status breakdown
        custom_report.append("## Directory Status")
        custom_report.append("")
        
        status_counts = {
            DirectoryStatus.IMPLEMENTED: 0,
            DirectoryStatus.PARTIAL: 0,
            DirectoryStatus.MISSING: 0,
            DirectoryStatus.CONFLICT: 0
        }
        
        for status in comparison.directory_statuses.values():
            status_counts[status] += 1
        
        for status, count in status_counts.items():
            if count > 0:
                custom_report.append(f"- {status.value.title()}: {count}")
        
        custom_report.append("")
        
        # Add top priorities
        gaps = result['gaps']
        high_priority = [g for g in gaps if g.priority == "High"]
        
        if high_priority:
            custom_report.append("## Top Priorities")
            custom_report.append("")
            for i, gap in enumerate(high_priority[:10], 1):
                custom_report.append(f"{i}. **{gap.category}**: {gap.description}")
                custom_report.append(f"   - Effort: {gap.effort}")
                custom_report.append(f"   - Action: {gap.proposed_action}")
                custom_report.append("")
        
        # Save custom report
        custom_report_text = "\n".join(custom_report)
        Path("custom_comparison_report.md").write_text(custom_report_text, encoding='utf-8')
        
        print("\nCustom report generated!")
        print("Saved to: custom_comparison_report.md")
        print(f"\nReport includes:")
        print(f"  - Executive summary")
        print(f"  - Directory status breakdown")
        print(f"  - Top {min(10, len(high_priority))} priorities")
        
    except ComparisonEngineError as e:
        print(f"Error: {e}")


def example_5_with_status_tracking():
    """
    Example 5: Use status tracking to monitor progress over time.
    
    This example shows how to use the status tracking feature to
    maintain a record of implementation progress.
    """
    print("\n" + "=" * 70)
    print("Example 5: Status Tracking")
    print("=" * 70)
    
    try:
        # Initialize engine with status file
        engine = ComparisonEngine(
            project_root=".",
            v2_docs_path="claude_suggestion/v2",
            status_file_path=".comparison_status.json"
        )
        
        result = engine.run_comparison()
        
        # The status tracker is automatically used if provided
        if engine.status_tracker:
            print("\nStatus tracking enabled")
            print("Status file: .comparison_status.json")
            print("\nYou can now:")
            print("  - Track progress over time")
            print("  - Mark improvements as complete")
            print("  - Document intentional deviations")
            print("  - View completion history")
        
        # Save report
        engine.save_report(result['report'], "comparison_report_with_status.md")
        print("\nReport saved to: comparison_report_with_status.md")
        
    except ComparisonEngineError as e:
        print(f"Error: {e}")


def example_6_validation_checks():
    """
    Example 6: Check for superseded and inapplicable suggestions.
    
    This example shows how to identify v2 suggestions that may no longer
    be relevant or have been superseded by actual implementation.
    """
    print("\n" + "=" * 70)
    print("Example 6: Validation Checks")
    print("=" * 70)
    
    try:
        engine = ComparisonEngine(
            project_root=".",
            v2_docs_path="claude_suggestion/v2"
        )
        
        # Run comparison with validation checks enabled (default)
        result = engine.run_comparison(check_validation=True)
        
        # Access validation results
        validation = result.get('validation_results')
        
        if validation:
            superseded = validation.get('superseded', [])
            inapplicable = validation.get('inapplicable', [])
            
            if superseded:
                print(f"\nFound {len(superseded)} superseded suggestions:")
                for item in superseded[:3]:  # Show first 3
                    print(f"  - {item}")
            
            if inapplicable:
                print(f"\nFound {len(inapplicable)} potentially inapplicable suggestions:")
                for item in inapplicable[:3]:  # Show first 3
                    print(f"  - {item}")
            
            if not superseded and not inapplicable:
                print("\nNo superseded or inapplicable suggestions found")
        
    except ComparisonEngineError as e:
        print(f"Error: {e}")


def main():
    """Run all examples."""
    print("\n" + "=" * 70)
    print("V2 Structure Comparison - Programmatic Usage Examples")
    print("=" * 70)
    print("\nThis demo shows various ways to use the comparison feature.")
    print("Each example demonstrates different capabilities and use cases.")
    
    # Run examples
    example_1_basic_comparison()
    example_2_with_migration_scripts()
    example_3_access_detailed_results()
    example_4_custom_report()
    example_5_with_status_tracking()
    example_6_validation_checks()
    
    print("\n" + "=" * 70)
    print("Demo Complete!")
    print("=" * 70)
    print("\nCheck the generated files:")
    print("  - comparison_report.md")
    print("  - custom_comparison_report.md")
    print("  - comparison_report_with_status.md")
    print("  - migration_scripts/ (if applicable)")
    print("  - .comparison_status.json (if applicable)")
    print("\nFor more information, see docs/V2_STRUCTURE_COMPARISON.md")


if __name__ == "__main__":
    main()
