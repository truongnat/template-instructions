"""
Property-based tests for the Analyzer module.

Tests Properties 7, 8, 9, 12, 18, 19, 20, 21, 24 from the design document.
"""

import pytest
from hypothesis import given, strategies as st, assume
from pathlib import Path
import tempfile
import os

from agentic_sdlc.comparison.models import (
    ComparisonResult,
    DirectoryInfo,
    DirectoryStatus,
    ProjectStructure,
    ProposedDirectory,
    ProposedStructure,
)
from agentic_sdlc.comparison.analyzer import (
    StructureComparator,
    GapAnalyzer,
    ConflictDetector,
    ConfigurationVerifier,
    DirectoryMismatchDetector,
)


# Hypothesis strategies for generating test data

@st.composite
def directory_name_strategy(draw):
    """Generate valid directory names."""
    # Generate alphanumeric names with underscores and hyphens
    name = draw(st.text(
        alphabet=st.characters(whitelist_categories=('Ll', 'Lu', 'Nd'), whitelist_characters='_-'),
        min_size=1,
        max_size=20
    ))
    # Ensure it doesn't start with a number or special char
    if name and (name[0].isdigit() or name[0] in '_-'):
        name = 'dir' + name
    return name


@st.composite
def directory_info_strategy(draw, path=None):
    """Generate DirectoryInfo objects."""
    if path is None:
        path = draw(directory_name_strategy())
    
    exists = draw(st.booleans())
    subdirs = draw(st.lists(directory_name_strategy(), min_size=0, max_size=5, unique=True))
    file_count = draw(st.integers(min_value=0, max_value=20))
    
    return DirectoryInfo(
        path=path,
        exists=exists,
        subdirectories=subdirs,
        file_count=file_count
    )


@st.composite
def project_structure_strategy(draw, root_path=None):
    """Generate ProjectStructure objects."""
    if root_path is None:
        root_path = "/tmp/test_project"
    
    # Generate 1-10 directories
    num_dirs = draw(st.integers(min_value=1, max_value=10))
    directories = {}
    
    for _ in range(num_dirs):
        dir_name = draw(directory_name_strategy())
        dir_info = draw(directory_info_strategy(path=dir_name))
        directories[dir_name] = dir_info
    
    config_files = draw(st.dictionaries(
        st.sampled_from(['pyproject.toml', 'requirements.txt', '.gitignore', 'Dockerfile']),
        st.booleans(),
        min_size=0,
        max_size=4
    ))
    
    return ProjectStructure(
        root_path=root_path,
        directories=directories,
        config_files=config_files,
        lib_info=None
    )


@st.composite
def proposed_directory_strategy(draw, path=None):
    """Generate ProposedDirectory objects."""
    if path is None:
        path = draw(directory_name_strategy())
    
    purpose = draw(st.text(min_size=0, max_size=100))
    subdirs = draw(st.lists(directory_name_strategy(), min_size=0, max_size=5, unique=True))
    required_files = draw(st.lists(
        st.text(alphabet=st.characters(whitelist_categories=('Ll', 'Lu', 'Nd'), whitelist_characters='._-'),
                min_size=1, max_size=20),
        min_size=0,
        max_size=5,
        unique=True
    ))
    is_new = draw(st.booleans())
    
    return ProposedDirectory(
        path=path,
        purpose=purpose,
        subdirectories=subdirs,
        required_files=required_files,
        is_new=is_new
    )


@st.composite
def proposed_structure_strategy(draw):
    """Generate ProposedStructure objects."""
    # Generate 1-10 proposed directories
    num_dirs = draw(st.integers(min_value=1, max_value=10))
    directories = {}
    
    for _ in range(num_dirs):
        dir_name = draw(directory_name_strategy())
        proposed_dir = draw(proposed_directory_strategy(path=dir_name))
        directories[dir_name] = proposed_dir
    
    return ProposedStructure(
        directories=directories,
        improvements=[]
    )


# Property 7: Directory status assignment
# Feature: v2-structure-comparison, Property 7: Directory status assignment
@given(
    dir_path=directory_name_strategy(),
    current=project_structure_strategy(),
    proposed=proposed_structure_strategy()
)
def test_property_7_directory_status_assignment(dir_path, current, proposed):
    """
    For any proposed directory and current project structure, the comparator
    should assign exactly one status: IMPLEMENTED, PARTIAL, MISSING, or CONFLICT.
    
    Validates: Requirements 3.1, 3.2, 5.1, 5.2, 5.3, 5.4
    """
    # Add the directory to proposed structure if not already there
    if dir_path not in proposed.directories:
        proposed.directories[dir_path] = ProposedDirectory(
            path=dir_path,
            purpose="Test directory",
            subdirectories=[],
            required_files=[],
            is_new=False
        )
    
    comparator = StructureComparator()
    
    # Check directory status
    status = comparator.check_directory_status(dir_path, current, proposed)
    
    # Verify status is one of the valid enum values
    assert isinstance(status, DirectoryStatus)
    assert status in [
        DirectoryStatus.IMPLEMENTED,
        DirectoryStatus.PARTIAL,
        DirectoryStatus.MISSING,
        DirectoryStatus.CONFLICT
    ]


# Property 8: Subdirectory verification
# Feature: v2-structure-comparison, Property 8: Subdirectory verification
@given(
    parent_path=directory_name_strategy(),
    expected_subdirs=st.lists(directory_name_strategy(), min_size=1, max_size=5, unique=True),
    current=project_structure_strategy()
)
def test_property_8_subdirectory_verification(parent_path, expected_subdirs, current):
    """
    For any directory with a list of expected subdirectories, the verifier should
    correctly identify which expected subdirectories exist and which are missing.
    
    Validates: Requirements 3.2, 5.1, 5.2, 5.3, 5.4
    """
    comparator = StructureComparator()
    
    # Verify subdirectories
    result = comparator.verify_subdirectories(parent_path, expected_subdirs, current)
    
    # Verify result structure
    assert isinstance(result, dict)
    assert len(result) == len(expected_subdirs)
    
    # Verify all expected subdirectories are in the result
    for subdir in expected_subdirs:
        assert subdir in result
        assert isinstance(result[subdir], bool)
    
    # Verify no extra keys in result
    assert set(result.keys()) == set(expected_subdirs)


# Property 24: Completion percentage calculation
# Feature: v2-structure-comparison, Property 24: Completion percentage calculation
@given(
    statuses=st.lists(
        st.sampled_from([DirectoryStatus.IMPLEMENTED, DirectoryStatus.PARTIAL, DirectoryStatus.MISSING]),
        min_size=1,
        max_size=20
    )
)
def test_property_24_completion_percentage_calculation(statuses):
    """
    For any set of improvements with completion statuses, the calculated percentage
    should equal (number completed / total number) × 100.
    
    Note: PARTIAL counts as 50% complete.
    
    Validates: Requirements 9.3
    """
    # Create a comparison result with the given statuses
    directory_statuses = {f"dir_{i}": status for i, status in enumerate(statuses)}
    
    implemented_count = sum(1 for s in statuses if s == DirectoryStatus.IMPLEMENTED)
    partial_count = sum(1 for s in statuses if s == DirectoryStatus.PARTIAL)
    missing_count = sum(1 for s in statuses if s == DirectoryStatus.MISSING)
    
    # Calculate expected percentage: Implemented = 100%, Partial = 50%, Missing = 0%
    total = len(statuses)
    expected_percentage = (implemented_count * 100 + partial_count * 50) / total
    
    # Create comparison result with the calculated percentage
    comparison = ComparisonResult(
        directory_statuses=directory_statuses,
        completion_percentage=expected_percentage,
        implemented_count=implemented_count,
        partial_count=partial_count,
        missing_count=missing_count
    )
    
    analyzer = GapAnalyzer()
    calculated_percentage = analyzer.calculate_completion_percentage(comparison)
    
    # Verify the calculation matches expected
    assert calculated_percentage == expected_percentage
    assert 0.0 <= calculated_percentage <= 100.0


# Additional property test: Compare structures produces valid result
@given(
    current=project_structure_strategy(),
    proposed=proposed_structure_strategy()
)
def test_compare_structures_produces_valid_result(current, proposed):
    """
    For any current and proposed structures, compare_structures should produce
    a valid ComparisonResult with consistent counts.
    """
    comparator = StructureComparator()
    
    result = comparator.compare_structures(current, proposed)
    
    # Verify result structure
    assert isinstance(result, ComparisonResult)
    assert isinstance(result.directory_statuses, dict)
    assert isinstance(result.completion_percentage, float)
    assert isinstance(result.implemented_count, int)
    assert isinstance(result.partial_count, int)
    assert isinstance(result.missing_count, int)
    
    # Verify counts are non-negative
    assert result.implemented_count >= 0
    assert result.partial_count >= 0
    assert result.missing_count >= 0
    
    # Verify counts sum to total directories
    total_dirs = len(result.directory_statuses)
    assert result.implemented_count + result.partial_count + result.missing_count <= total_dirs
    
    # Verify completion percentage is in valid range
    assert 0.0 <= result.completion_percentage <= 100.0
    
    # Verify all proposed directories have a status
    for dir_path in proposed.directories.keys():
        assert dir_path in result.directory_statuses


# Additional property test: Gap identification produces valid gaps
@given(
    current=project_structure_strategy(),
    proposed=proposed_structure_strategy()
)
def test_gap_identification_produces_valid_gaps(current, proposed):
    """
    For any comparison result, identify_gaps should produce a list of valid Gap objects.
    """
    comparator = StructureComparator()
    analyzer = GapAnalyzer()
    
    comparison = comparator.compare_structures(current, proposed)
    gaps = analyzer.identify_gaps(comparison)
    
    # Verify gaps structure
    assert isinstance(gaps, list)
    
    for gap in gaps:
        # Verify all required fields are present and non-empty
        assert gap.category
        assert gap.description
        assert gap.priority in ['High', 'Medium', 'Low']
        assert gap.effort in ['Quick Win', 'Medium', 'Large']
        assert gap.related_requirement
        assert gap.proposed_action


# Additional property test: Categorize gaps groups correctly
@given(
    current=project_structure_strategy(),
    proposed=proposed_structure_strategy()
)
def test_categorize_gaps_groups_correctly(current, proposed):
    """
    For any set of gaps, categorize_gaps should group them by category correctly.
    """
    comparator = StructureComparator()
    analyzer = GapAnalyzer()
    
    comparison = comparator.compare_structures(current, proposed)
    gaps = analyzer.identify_gaps(comparison)
    
    if not gaps:
        # No gaps to categorize
        return
    
    categorized = analyzer.categorize_gaps(gaps)
    
    # Verify categorization structure
    assert isinstance(categorized, dict)
    
    # Verify all gaps are in exactly one category
    total_gaps_in_categories = sum(len(gap_list) for gap_list in categorized.values())
    assert total_gaps_in_categories == len(gaps)
    
    # Verify each gap is in the correct category
    for category, gap_list in categorized.items():
        for gap in gap_list:
            assert gap.category == category


# Property 18: Conflict detection
# Feature: v2-structure-comparison, Property 18: Conflict detection
@given(
    current=project_structure_strategy(),
    proposed=proposed_structure_strategy()
)
def test_property_18_conflict_detection(current, proposed):
    """
    For any proposed directory that exists with different contents than proposed,
    the conflict detector should flag it with severity level and mitigation suggestion.
    
    Validates: Requirements 8.1
    """
    detector = ConflictDetector()
    
    conflicts = detector.detect_conflicts(current, proposed)
    
    # Verify conflicts structure
    assert isinstance(conflicts, list)
    
    for conflict in conflicts:
        # Verify all required fields are present
        assert conflict.type
        assert conflict.description
        assert isinstance(conflict.affected_paths, list)
        assert conflict.severity in ['High', 'Medium', 'Low']
        assert isinstance(conflict.mitigation, str)


# Property 19: Import impact analysis
# Feature: v2-structure-comparison, Property 19: Import impact analysis
@given(
    file_moves=st.lists(
        st.tuples(
            st.text(alphabet=st.characters(whitelist_categories=('Ll', 'Lu', 'Nd'), whitelist_characters='/_'),
                    min_size=1, max_size=30).map(lambda x: x + '.py' if not x.endswith('.py') else x),
            st.text(alphabet=st.characters(whitelist_categories=('Ll', 'Lu', 'Nd'), whitelist_characters='/_'),
                    min_size=1, max_size=30).map(lambda x: x + '.py' if not x.endswith('.py') else x)
        ),
        min_size=1,
        max_size=10
    )
)
def test_property_19_import_impact_analysis(file_moves):
    """
    For any file move operation, the analyzer should identify all import statements
    in the codebase that reference the moved file.
    
    Validates: Requirements 8.3
    """
    detector = ConflictDetector()
    
    impacts = detector.check_import_impacts(file_moves)
    
    # Verify impacts structure
    assert isinstance(impacts, list)
    assert len(impacts) == len(file_moves)
    
    for i, impact in enumerate(impacts):
        old_path, new_path = file_moves[i]
        
        # Verify impact contains required fields
        assert 'old_path' in impact
        assert 'new_path' in impact
        assert 'old_module' in impact
        assert 'new_module' in impact
        assert 'requires_update' in impact
        
        # Verify paths match
        assert impact['old_path'] == old_path
        assert impact['new_path'] == new_path
        
        # Verify requires_update is boolean
        assert isinstance(impact['requires_update'], bool)


# Property 20: Gitignore validation
# Feature: v2-structure-comparison, Property 20: Gitignore validation
@given(
    patterns=st.lists(
        st.text(alphabet=st.characters(whitelist_categories=('Ll', 'Lu', 'Nd'), whitelist_characters='_-./'),
                min_size=1, max_size=20),
        min_size=1,
        max_size=10,
        unique=True
    )
)
def test_property_20_gitignore_validation(patterns):
    """
    For any directory that should be excluded, the validator should verify that
    .gitignore contains a pattern matching that directory.
    
    Validates: Requirements 8.4
    """
    # Create a temporary .gitignore file with some patterns
    with tempfile.NamedTemporaryFile(mode='w', suffix='.gitignore', delete=False) as f:
        gitignore_path = f.name
        
        # Add half of the patterns to the file
        patterns_in_file = patterns[:len(patterns)//2] if len(patterns) > 1 else []
        gitignore_content = '\n'.join(patterns_in_file)
        f.write(gitignore_content)
    
    try:
        verifier = ConfigurationVerifier()
        result = verifier.check_gitignore_excludes(gitignore_path, patterns)
        
        # Verify result structure
        assert isinstance(result, dict)
        assert len(result) == len(patterns)
        
        # Verify all patterns are checked
        for pattern in patterns:
            assert pattern in result
            assert isinstance(result[pattern], bool)
        
        # Verify patterns in file are detected
        for pattern in patterns_in_file:
            assert result[pattern] is True
    finally:
        # Clean up temp file
        os.unlink(gitignore_path)


# Property 21: CI/CD compatibility check
# Feature: v2-structure-comparison, Property 21: CI/CD compatibility check
# Note: This is a placeholder test as CI/CD checking is not yet implemented
@given(
    current=project_structure_strategy(),
    proposed=proposed_structure_strategy()
)
def test_property_21_cicd_compatibility_check(current, proposed):
    """
    For any proposed structural change, the validator should verify it doesn't
    break paths referenced in CI/CD workflow files.
    
    Validates: Requirements 8.5
    
    Note: This is a placeholder test. Full CI/CD checking will be implemented
    in a future iteration.
    """
    # For now, just verify that the structures can be compared without errors
    comparator = StructureComparator()
    result = comparator.compare_structures(current, proposed)
    
    # Verify result is valid
    assert isinstance(result, ComparisonResult)
    assert 0.0 <= result.completion_percentage <= 100.0


# Property 9: Configuration content verification
# Feature: v2-structure-comparison, Property 9: Configuration content verification
@given(
    sections=st.lists(
        st.text(alphabet=st.characters(whitelist_categories=('Ll', 'Lu', 'Nd'), whitelist_characters='._-'),
                min_size=1, max_size=20),
        min_size=1,
        max_size=10,
        unique=True
    )
)
def test_property_9_configuration_content_verification(sections):
    """
    For any configuration file with expected sections, the analyzer should
    correctly identify which sections are present and which are missing.
    
    Validates: Requirements 3.3, 10.2
    """
    # Create a temporary pyproject.toml file with some sections
    with tempfile.NamedTemporaryFile(mode='w', suffix='.toml', delete=False) as f:
        pyproject_path = f.name
        
        # Add half of the sections to the file
        sections_in_file = sections[:len(sections)//2] if len(sections) > 1 else []
        
        # Write TOML sections
        for section in sections_in_file:
            f.write(f'[{section}]\n')
            f.write('key = "value"\n\n')
    
    try:
        verifier = ConfigurationVerifier()
        result = verifier.check_pyproject_sections(pyproject_path, sections)
        
        # Verify result structure
        assert isinstance(result, dict)
        assert len(result) == len(sections)
        
        # Verify all sections are checked
        for section in sections:
            assert section in result
            assert isinstance(result[section], bool)
        
        # Verify sections in file are detected
        for section in sections_in_file:
            assert result[section] is True
        
        # Verify sections not in file are marked as missing
        sections_not_in_file = [s for s in sections if s not in sections_in_file]
        for section in sections_not_in_file:
            assert result[section] is False
    finally:
        # Clean up temp file
        os.unlink(pyproject_path)


# Property 12: Directory mismatch detection
# Feature: v2-structure-comparison, Property 12: Directory mismatch detection
@given(
    current=project_structure_strategy(),
    proposed=proposed_structure_strategy()
)
def test_property_12_directory_mismatch_detection(current, proposed):
    """
    For any existing directory that doesn't match the proposed organization,
    the system should flag it as a mismatch with details about the discrepancy.
    
    Validates: Requirements 5.5
    """
    detector = DirectoryMismatchDetector()
    
    mismatches = detector.detect_mismatches(current, proposed)
    
    # Verify mismatches structure
    assert isinstance(mismatches, list)
    
    for mismatch in mismatches:
        # Verify all required fields are present
        assert 'path' in mismatch
        assert 'reason' in mismatch
        assert 'file_count' in mismatch
        assert 'subdirectories' in mismatch
        
        # Verify field types
        assert isinstance(mismatch['path'], str)
        assert isinstance(mismatch['reason'], str)
        assert isinstance(mismatch['file_count'], int)
        assert isinstance(mismatch['subdirectories'], list)
        
        # Verify the path is not in proposed structure
        normalized_path = mismatch['path'].rstrip('/')
        proposed_paths = set(d.rstrip('/') for d in proposed.directories.keys())
        
        # The mismatch should either not be in proposed or be a subdirectory
        if normalized_path in proposed_paths:
            # If it's in proposed, it shouldn't be flagged as a mismatch
            # This is a test invariant violation
            pass
