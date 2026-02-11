"""
Property-based tests for V2 Structure Comparison reporter module.

These tests verify universal properties that should hold for all valid inputs
using the Hypothesis library for property-based testing.
"""

import pytest
from hypothesis import given, strategies as st
from agentic_sdlc.comparison.models import (
    DirectoryStatus,
    ComparisonResult,
    Gap,
    Conflict,
)
from agentic_sdlc.comparison.reporter import (
    ComparisonReporter,
    ProgressVisualizer,
)


# Hypothesis strategies for generating test data
@st.composite
def gap_strategy(draw):
    """Generate a Gap instance with random but valid data."""
    return Gap(
        category=draw(st.text(min_size=1, max_size=50)),
        description=draw(st.text(min_size=1, max_size=200)),
        priority=draw(st.sampled_from(["High", "Medium", "Low"])),
        effort=draw(st.sampled_from(["Quick Win", "Medium", "Large"])),
        related_requirement=draw(st.text(min_size=1, max_size=20)),
        proposed_action=draw(st.text(min_size=1, max_size=200))
    )


@st.composite
def conflict_strategy(draw):
    """Generate a Conflict instance with random but valid data."""
    return Conflict(
        type=draw(st.sampled_from(["directory_exists", "import_break", "config_conflict"])),
        description=draw(st.text(min_size=1, max_size=200)),
        affected_paths=draw(st.lists(st.text(min_size=1, max_size=50), min_size=1, max_size=10)),
        severity=draw(st.sampled_from(["High", "Medium", "Low"])),
        mitigation=draw(st.text(min_size=0, max_size=200))
    )


@st.composite
def comparison_result_strategy(draw):
    """Generate a ComparisonResult instance with random but valid data."""
    # Generate counts that are consistent
    implemented = draw(st.integers(min_value=0, max_value=100))
    partial = draw(st.integers(min_value=0, max_value=100))
    missing = draw(st.integers(min_value=0, max_value=100))
    
    total = implemented + partial + missing
    completion = (implemented / total * 100) if total > 0 else 0.0
    
    # Generate directory statuses
    num_dirs = draw(st.integers(min_value=0, max_value=20))
    statuses = {}
    for i in range(num_dirs):
        dir_name = f"dir_{i}/"
        status = draw(st.sampled_from(list(DirectoryStatus)))
        statuses[dir_name] = status
    
    return ComparisonResult(
        directory_statuses=statuses,
        completion_percentage=completion,
        implemented_count=implemented,
        partial_count=partial,
        missing_count=missing
    )


# Feature: v2-structure-comparison, Property 11: Report structure completeness
@given(
    comparison_result=comparison_result_strategy(),
    gaps=st.lists(gap_strategy(), min_size=0, max_size=20),
    conflicts=st.lists(conflict_strategy(), min_size=0, max_size=10)
)
def test_property_11_report_structure_completeness(comparison_result, gaps, conflicts):
    """
    Property 11: Report structure completeness
    
    For any generated comparison report, it should contain all required sections:
    - Summary with completion percentage
    - Category breakdown
    - Gaps section
    - Conflicts section
    - Quick wins section
    
    **Validates: Requirements 4.1, 4.2, 4.3, 4.4, 4.5**
    """
    reporter = ComparisonReporter()
    report = reporter.generate_report(comparison_result, gaps, conflicts)
    
    # Verify report is a non-empty string
    assert isinstance(report, str)
    assert len(report) > 0
    
    # Verify all required sections are present
    assert "# V2 Structure Comparison Report" in report
    assert "## Summary" in report
    assert "## Category Breakdown" in report
    assert "## Identified Gaps" in report
    assert "## Potential Conflicts" in report
    assert "## Quick Wins" in report
    
    # Verify summary section contains completion percentage
    assert "Overall Completion:" in report
    assert f"{comparison_result.completion_percentage:.1f}%" in report
    
    # Verify summary section contains counts
    assert f"Implemented: {comparison_result.implemented_count}" in report
    assert f"Partially Implemented: {comparison_result.partial_count}" in report
    assert f"Missing: {comparison_result.missing_count}" in report


# Feature: v2-structure-comparison, Property 11: Report structure completeness (individual sections)
@given(comparison_result=comparison_result_strategy())
def test_property_11_summary_section_structure(comparison_result):
    """
    Property 11: Report structure completeness (summary section)
    
    For any comparison result, the summary section should contain:
    - Overall completion percentage
    - Implemented count
    - Partial count
    - Missing count
    
    **Validates: Requirements 4.1**
    """
    reporter = ComparisonReporter()
    summary = reporter.generate_summary_section(comparison_result)
    
    # Verify summary is a non-empty string
    assert isinstance(summary, str)
    assert len(summary) > 0
    
    # Verify section header
    assert "## Summary" in summary
    
    # Verify completion percentage is present
    assert "Overall Completion:" in summary
    assert f"{comparison_result.completion_percentage:.1f}%" in summary
    
    # Verify all counts are present
    assert f"Implemented: {comparison_result.implemented_count}" in summary
    assert f"Partially Implemented: {comparison_result.partial_count}" in summary
    assert f"Missing: {comparison_result.missing_count}" in summary


# Feature: v2-structure-comparison, Property 11: Report structure completeness (category breakdown)
@given(comparison_result=comparison_result_strategy())
def test_property_11_category_breakdown_structure(comparison_result):
    """
    Property 11: Report structure completeness (category breakdown)
    
    For any comparison result, the category breakdown should:
    - List all directories with their statuses
    - Use a table format
    - Include status indicators
    
    **Validates: Requirements 4.2**
    """
    reporter = ComparisonReporter()
    breakdown = reporter.generate_category_breakdown(comparison_result)
    
    # Verify breakdown is a non-empty string
    assert isinstance(breakdown, str)
    assert len(breakdown) > 0
    
    # Verify section header
    assert "## Category Breakdown" in breakdown
    
    # Verify table structure
    assert "| Directory | Status |" in breakdown
    assert "|-----------|--------|" in breakdown
    
    # Verify all directories are listed
    for directory in comparison_result.directory_statuses.keys():
        assert directory in breakdown


# Feature: v2-structure-comparison, Property 11: Report structure completeness (gaps section)
@given(gaps=st.lists(gap_strategy(), min_size=0, max_size=20))
def test_property_11_gaps_section_structure(gaps):
    """
    Property 11: Report structure completeness (gaps section)
    
    For any list of gaps, the gaps section should:
    - List all gaps grouped by priority
    - Include gap details (category, description, effort, action)
    - Show total count
    
    **Validates: Requirements 4.3**
    """
    reporter = ComparisonReporter()
    gaps_section = reporter.generate_gaps_section(gaps)
    
    # Verify section is a non-empty string
    assert isinstance(gaps_section, str)
    assert len(gaps_section) > 0
    
    # Verify section header
    assert "## Identified Gaps" in gaps_section
    
    if gaps:
        # If there are gaps, verify they're listed
        assert f"Total gaps identified: {len(gaps)}" in gaps_section
        
        # Verify priority grouping headers appear if relevant
        high_priority_gaps = [g for g in gaps if g.priority == "High"]
        medium_priority_gaps = [g for g in gaps if g.priority == "Medium"]
        low_priority_gaps = [g for g in gaps if g.priority == "Low"]
        
        if high_priority_gaps:
            assert "### High Priority" in gaps_section
        if medium_priority_gaps:
            assert "### Medium Priority" in gaps_section
        if low_priority_gaps:
            assert "### Low Priority" in gaps_section
    else:
        # If no gaps, verify appropriate message
        assert "No gaps identified" in gaps_section


# Feature: v2-structure-comparison, Property 11: Report structure completeness (conflicts section)
@given(conflicts=st.lists(conflict_strategy(), min_size=0, max_size=10))
def test_property_11_conflicts_section_structure(conflicts):
    """
    Property 11: Report structure completeness (conflicts section)
    
    For any list of conflicts, the conflicts section should:
    - List all conflicts grouped by severity
    - Include conflict details
    - Show total count
    
    **Validates: Requirements 4.4**
    """
    reporter = ComparisonReporter()
    conflicts_section = reporter.generate_conflicts_section(conflicts)
    
    # Verify section is a non-empty string
    assert isinstance(conflicts_section, str)
    assert len(conflicts_section) > 0
    
    # Verify section header
    assert "## Potential Conflicts" in conflicts_section
    
    if conflicts:
        # If there are conflicts, verify they're listed
        assert f"Total conflicts detected: {len(conflicts)}" in conflicts_section
        
        # Verify severity grouping headers appear if relevant
        high_severity = [c for c in conflicts if c.severity == "High"]
        medium_severity = [c for c in conflicts if c.severity == "Medium"]
        low_severity = [c for c in conflicts if c.severity == "Low"]
        
        if high_severity:
            assert "### High Severity" in conflicts_section
        if medium_severity:
            assert "### Medium Severity" in conflicts_section
        if low_severity:
            assert "### Low Severity" in conflicts_section
    else:
        # If no conflicts, verify appropriate message
        assert "No conflicts detected" in conflicts_section


# Feature: v2-structure-comparison, Property 11: Report structure completeness (quick wins section)
@given(gaps=st.lists(gap_strategy(), min_size=0, max_size=20))
def test_property_11_quick_wins_section_structure(gaps):
    """
    Property 11: Report structure completeness (quick wins section)
    
    For any list of gaps, the quick wins section should:
    - List gaps with "Quick Win" effort and High/Medium priority
    - Include action items
    - Show count
    
    **Validates: Requirements 4.5**
    """
    reporter = ComparisonReporter()
    quick_wins_section = reporter.generate_quick_wins_section(gaps)
    
    # Verify section is a non-empty string
    assert isinstance(quick_wins_section, str)
    assert len(quick_wins_section) > 0
    
    # Verify section header
    assert "## Quick Wins" in quick_wins_section
    
    # Calculate expected quick wins
    quick_wins = [
        g for g in gaps 
        if g.effort == "Quick Win" and g.priority in ["High", "Medium"]
    ]
    
    if quick_wins:
        # If there are quick wins, verify they're listed
        assert f"{len(quick_wins)} improvements" in quick_wins_section
        
        # Verify each quick win is mentioned
        for qw in quick_wins:
            assert qw.category in quick_wins_section
    else:
        # If no quick wins, verify appropriate message
        assert "No quick wins identified" in quick_wins_section


# Feature: v2-structure-comparison, Property 25: Progress visualization generation
@given(percentage=st.floats(min_value=0.0, max_value=100.0))
def test_property_25_progress_visualization_generation(percentage):
    """
    Property 25: Progress visualization generation
    
    For any completion percentage, the generated visualization should include:
    - A progress bar
    - The percentage value
    
    **Validates: Requirements 9.4**
    """
    visualizer = ProgressVisualizer()
    progress_bar = visualizer.create_progress_bar(percentage)
    
    # Verify progress bar is a non-empty string
    assert isinstance(progress_bar, str)
    assert len(progress_bar) > 0
    
    # Verify progress bar contains the percentage
    assert f"{percentage:.1f}%" in progress_bar
    
    # Verify progress bar has brackets
    assert "[" in progress_bar
    assert "]" in progress_bar
    
    # Verify progress bar contains visual elements
    # Should contain either filled (█) or empty (░) blocks
    assert "█" in progress_bar or "░" in progress_bar


# Feature: v2-structure-comparison, Property 25: Progress visualization generation (category chart)
@given(
    num_dirs=st.integers(min_value=0, max_value=20),
    statuses=st.lists(st.sampled_from(list(DirectoryStatus)), min_size=0, max_size=20)
)
def test_property_25_category_chart_generation(num_dirs, statuses):
    """
    Property 25: Progress visualization generation (category chart)
    
    For any set of directory statuses, the category chart should include:
    - Status distribution
    - Visual bars
    - Counts and percentages
    
    **Validates: Requirements 9.4**
    """
    # Create categories dictionary
    categories = {}
    for i, status in enumerate(statuses[:num_dirs]):
        categories[f"dir_{i}/"] = status
    
    visualizer = ProgressVisualizer()
    chart = visualizer.create_category_chart(categories)
    
    # Verify chart is a non-empty string
    assert isinstance(chart, str)
    assert len(chart) > 0
    
    if categories:
        # Verify chart contains distribution header
        assert "Category Status Distribution:" in chart
        
        # Count each status type
        status_counts = {}
        for status in categories.values():
            status_counts[status] = status_counts.get(status, 0) + 1
        
        # Verify each status with count > 0 appears in the chart
        for status, count in status_counts.items():
            if count > 0:
                assert status.value.title() in chart
    else:
        # If no categories, verify appropriate message
        assert "No categories to display" in chart


# Additional property test: Progress bar bounds
@given(percentage=st.floats(min_value=-100.0, max_value=200.0))
def test_progress_bar_handles_out_of_bounds_percentage(percentage):
    """
    Verify that progress bar handles out-of-bounds percentages gracefully.
    
    The progress bar should clamp percentages to the 0-100 range.
    """
    visualizer = ProgressVisualizer()
    progress_bar = visualizer.create_progress_bar(percentage)
    
    # Extract the percentage from the progress bar
    # Format is "[...] XX.X%"
    assert isinstance(progress_bar, str)
    assert "%" in progress_bar
    
    # The displayed percentage should be clamped to 0-100
    if percentage < 0:
        assert "0.0%" in progress_bar
    elif percentage > 100:
        assert "100.0%" in progress_bar
    else:
        assert f"{percentage:.1f}%" in progress_bar


# Additional property test: Progress bar width consistency
@given(
    percentage=st.floats(min_value=0.0, max_value=100.0),
    width=st.integers(min_value=10, max_value=100)
)
def test_progress_bar_width_consistency(percentage, width):
    """
    Verify that progress bar respects the specified width.
    
    The progress bar should have exactly the specified width in characters
    (excluding brackets and percentage text).
    """
    visualizer = ProgressVisualizer()
    progress_bar = visualizer.create_progress_bar(percentage, width=width)
    
    # Extract the bar portion (between brackets)
    start = progress_bar.index("[") + 1
    end = progress_bar.index("]")
    bar_content = progress_bar[start:end]
    
    # Verify the bar has exactly the specified width
    assert len(bar_content) == width


# Additional property test: Report sections are non-overlapping
@given(
    comparison_result=comparison_result_strategy(),
    gaps=st.lists(gap_strategy(), min_size=0, max_size=20),
    conflicts=st.lists(conflict_strategy(), min_size=0, max_size=10)
)
def test_report_sections_are_distinct(comparison_result, gaps, conflicts):
    """
    Verify that report sections are distinct and don't overlap.
    
    Each section should appear exactly once in the report.
    """
    reporter = ComparisonReporter()
    report = reporter.generate_report(comparison_result, gaps, conflicts)
    
    # Count occurrences of each section header
    assert report.count("# V2 Structure Comparison Report") == 1
    assert report.count("## Summary") == 1
    assert report.count("## Category Breakdown") == 1
    assert report.count("## Identified Gaps") == 1
    assert report.count("## Potential Conflicts") == 1
    assert report.count("## Quick Wins") == 1


# Additional property test: Empty report handling
def test_empty_report_generation():
    """
    Verify that report generation handles empty inputs gracefully.
    """
    reporter = ComparisonReporter()
    
    # Create empty comparison result
    empty_comparison = ComparisonResult()
    empty_gaps = []
    empty_conflicts = []
    
    report = reporter.generate_report(empty_comparison, empty_gaps, empty_conflicts)
    
    # Verify report is still generated with all sections
    assert isinstance(report, str)
    assert len(report) > 0
    assert "# V2 Structure Comparison Report" in report
    assert "## Summary" in report
    assert "## Category Breakdown" in report
    assert "## Identified Gaps" in report
    assert "## Potential Conflicts" in report
    assert "## Quick Wins" in report
