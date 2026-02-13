"""
Property-based tests for V2 Structure Comparison data models.

These tests verify universal properties that should hold for all valid inputs
using the Hypothesis library for property-based testing.
"""

import pytest
from hypothesis import given, strategies as st
from agentic_sdlc.comparison.models import (
    DirectoryStatus,
    DirectoryInfo,
    LibraryInfo,
    ProjectStructure,
    ProposedDirectory,
    Improvement,
    ProposedStructure,
    ComparisonResult,
    Gap,
    Conflict,
    Task,
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


@st.composite
def improvement_strategy(draw):
    """Generate an Improvement instance with random but valid data."""
    return Improvement(
        category=draw(st.text(min_size=1, max_size=50)),
        title=draw(st.text(min_size=1, max_size=100)),
        description=draw(st.text(min_size=1, max_size=200)),
        priority=draw(st.sampled_from(["High", "Medium", "Low"])),
        estimated_hours=draw(st.floats(min_value=0.5, max_value=100.0)),
        related_directories=draw(st.lists(st.text(min_size=1, max_size=50), max_size=10))
    )


# Feature: v2-structure-comparison, Property 10: Gap analysis structure
@given(comparison_result=comparison_result_strategy())
def test_property_10_gap_analysis_structure(comparison_result):
    """
    Property 10: Gap analysis structure
    
    For any comparison result, the gap analysis should produce a list where 
    each gap has all required fields (category, description, priority, effort, 
    related_requirement, proposed_action).
    
    This test verifies that Gap objects can be created with all required fields
    and that those fields are accessible and have the correct types.
    
    **Validates: Requirements 3.5**
    """
    # Generate a list of gaps based on the comparison result
    gaps = []
    
    # For each missing or partial directory, create a gap
    for dir_path, status in comparison_result.directory_statuses.items():
        if status in [DirectoryStatus.MISSING, DirectoryStatus.PARTIAL]:
            gap = Gap(
                category="Directory Structure",
                description=f"Directory {dir_path} is {status.value}",
                priority="High" if status == DirectoryStatus.MISSING else "Medium",
                effort="Quick Win",
                related_requirement="3.5",
                proposed_action=f"Create or complete {dir_path}"
            )
            gaps.append(gap)
    
    # Verify each gap has all required fields
    for gap in gaps:
        # All fields must be present and non-None
        assert gap.category is not None
        assert gap.description is not None
        assert gap.priority is not None
        assert gap.effort is not None
        assert gap.related_requirement is not None
        assert gap.proposed_action is not None
        
        # Fields must have correct types
        assert isinstance(gap.category, str)
        assert isinstance(gap.description, str)
        assert isinstance(gap.priority, str)
        assert isinstance(gap.effort, str)
        assert isinstance(gap.related_requirement, str)
        assert isinstance(gap.proposed_action, str)
        
        # Priority must be one of the valid values
        assert gap.priority in ["High", "Medium", "Low"]
        
        # Effort must be one of the valid values
        assert gap.effort in ["Quick Win", "Medium", "Large"]


# Feature: v2-structure-comparison, Property 10: Gap analysis structure (extended)
@given(gap=gap_strategy())
def test_property_10_gap_has_all_required_fields(gap):
    """
    Property 10: Gap analysis structure (extended test)
    
    For any Gap instance, all required fields must be present and accessible.
    This is a more direct test of the Gap dataclass structure.
    
    **Validates: Requirements 3.5**
    """
    # Verify all required fields exist and are accessible
    assert hasattr(gap, 'category')
    assert hasattr(gap, 'description')
    assert hasattr(gap, 'priority')
    assert hasattr(gap, 'effort')
    assert hasattr(gap, 'related_requirement')
    assert hasattr(gap, 'proposed_action')
    
    # Verify fields are not None
    assert gap.category is not None
    assert gap.description is not None
    assert gap.priority is not None
    assert gap.effort is not None
    assert gap.related_requirement is not None
    assert gap.proposed_action is not None
    
    # Verify field types
    assert isinstance(gap.category, str)
    assert isinstance(gap.description, str)
    assert isinstance(gap.priority, str)
    assert isinstance(gap.effort, str)
    assert isinstance(gap.related_requirement, str)
    assert isinstance(gap.proposed_action, str)


# Feature: v2-structure-comparison, Property 33: Status differentiation
@given(
    dir_path=st.text(min_size=1, max_size=50),
    status=st.sampled_from(list(DirectoryStatus))
)
def test_property_33_status_differentiation(dir_path, status):
    """
    Property 33: Status differentiation
    
    For any suggestion (directory), the system should assign exactly one status:
    IMPLEMENTED, PARTIAL, MISSING, or CONFLICT.
    
    This test verifies that:
    1. A directory can only have one status at a time
    2. The status is one of the four valid values
    3. Status assignment is unambiguous
    
    **Validates: Requirements 12.4**
    """
    # Create a comparison result with a single directory status
    result = ComparisonResult(
        directory_statuses={dir_path: status}
    )
    
    # Verify the directory has exactly one status
    assert dir_path in result.directory_statuses
    assigned_status = result.directory_statuses[dir_path]
    
    # Verify the status is one of the four valid values
    assert assigned_status in [
        DirectoryStatus.IMPLEMENTED,
        DirectoryStatus.PARTIAL,
        DirectoryStatus.MISSING,
        DirectoryStatus.CONFLICT
    ]
    
    # Verify the status is exactly what we assigned
    assert assigned_status == status
    
    # Verify the status is unambiguous (it's an enum, so it can only be one value)
    assert isinstance(assigned_status, DirectoryStatus)


# Feature: v2-structure-comparison, Property 33: Status differentiation (extended)
@given(comparison_result=comparison_result_strategy())
def test_property_33_all_directories_have_single_status(comparison_result):
    """
    Property 33: Status differentiation (extended test)
    
    For any comparison result with multiple directories, each directory
    should have exactly one status assigned.
    
    **Validates: Requirements 12.4**
    """
    # Verify each directory has exactly one status
    for dir_path, status in comparison_result.directory_statuses.items():
        # Status must be a DirectoryStatus enum value
        assert isinstance(status, DirectoryStatus)
        
        # Status must be one of the four valid values
        assert status in [
            DirectoryStatus.IMPLEMENTED,
            DirectoryStatus.PARTIAL,
            DirectoryStatus.MISSING,
            DirectoryStatus.CONFLICT
        ]
        
        # Verify we can't have multiple statuses (this is guaranteed by dict structure)
        # but we verify the value is singular
        assert comparison_result.directory_statuses[dir_path] == status


# Feature: v2-structure-comparison, Property 33: Status differentiation (improvement status)
@given(improvement=improvement_strategy())
def test_property_33_improvement_has_single_priority(improvement):
    """
    Property 33: Status differentiation (for improvements)
    
    For any improvement suggestion, it should have exactly one priority level
    assigned: High, Medium, or Low.
    
    **Validates: Requirements 12.4**
    """
    # Verify the improvement has a priority
    assert hasattr(improvement, 'priority')
    assert improvement.priority is not None
    
    # Verify the priority is one of the three valid values
    assert improvement.priority in ["High", "Medium", "Low"]
    
    # Verify the priority is a string (not a list or multiple values)
    assert isinstance(improvement.priority, str)


# Additional property test: Gap list consistency
@given(gaps=st.lists(gap_strategy(), min_size=0, max_size=20))
def test_gap_list_consistency(gaps):
    """
    Verify that a list of gaps maintains consistency.
    
    All gaps in a list should have the required structure, and the list
    should be iterable and countable.
    """
    # Verify the list is iterable
    gap_count = 0
    for gap in gaps:
        gap_count += 1
        # Each gap should have all required fields
        assert isinstance(gap.category, str)
        assert isinstance(gap.priority, str)
        assert isinstance(gap.effort, str)
    
    # Verify the count matches the list length
    assert gap_count == len(gaps)


# Additional property test: ComparisonResult counts consistency
@given(comparison_result=comparison_result_strategy())
def test_comparison_result_counts_consistency(comparison_result):
    """
    Verify that ComparisonResult counts are consistent.
    
    The sum of implemented, partial, and missing counts should be non-negative,
    and the completion percentage should be between 0 and 100.
    """
    # Verify counts are non-negative
    assert comparison_result.implemented_count >= 0
    assert comparison_result.partial_count >= 0
    assert comparison_result.missing_count >= 0
    
    # Verify completion percentage is valid
    assert 0.0 <= comparison_result.completion_percentage <= 100.0
    
    # Verify total count consistency
    total = (comparison_result.implemented_count + 
             comparison_result.partial_count + 
             comparison_result.missing_count)
    
    if total > 0:
        # If there are items, completion percentage should be based on implemented count
        expected_percentage = (comparison_result.implemented_count / total) * 100
        # Allow for floating point precision differences
        assert abs(comparison_result.completion_percentage - expected_percentage) < 0.01
    else:
        # If no items, completion percentage should be 0
        assert comparison_result.completion_percentage == 0.0


# Additional property test: DirectoryStatus enum values are unique
def test_directory_status_enum_uniqueness():
    """
    Verify that DirectoryStatus enum values are unique and well-defined.
    """
    statuses = list(DirectoryStatus)
    
    # Verify we have exactly 4 statuses
    assert len(statuses) == 4
    
    # Verify all statuses are unique
    assert len(set(statuses)) == 4
    
    # Verify the expected statuses exist
    assert DirectoryStatus.IMPLEMENTED in statuses
    assert DirectoryStatus.PARTIAL in statuses
    assert DirectoryStatus.MISSING in statuses
    assert DirectoryStatus.CONFLICT in statuses
    
    # Verify the string values are unique
    values = [s.value for s in statuses]
    assert len(set(values)) == 4
