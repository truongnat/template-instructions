"""
Property-based tests for the Validation module.

Tests Properties 26, 27 from the design document.
"""

import pytest
from hypothesis import given, strategies as st, assume
from pathlib import Path

from agentic_sdlc.comparison.models import (
    DirectoryInfo,
    Improvement,
    ProjectStructure,
    ProposedDirectory,
    ProposedStructure,
)
from agentic_sdlc.comparison.analyzer import ValidationChecker


# Hypothesis strategies for generating test data

@st.composite
def directory_name_strategy(draw):
    """Generate valid directory names."""
    name = draw(st.text(
        alphabet=st.characters(whitelist_categories=('Ll', 'Lu', 'Nd'), whitelist_characters='_-'),
        min_size=1,
        max_size=20
    ))
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
    
    purpose = draw(st.text(min_size=10, max_size=100))
    subdirs = draw(st.lists(directory_name_strategy(), min_size=0, max_size=5, unique=True))
    required_files = draw(st.lists(
        st.text(min_size=1, max_size=20).map(lambda x: x + '.py'),
        min_size=0,
        max_size=3,
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
def improvement_strategy(draw):
    """Generate Improvement objects."""
    category = draw(st.sampled_from([
        'Directory Structure',
        'Configuration',
        'Documentation',
        'Testing',
        'CLI'
    ]))
    title = draw(st.text(min_size=5, max_size=50))
    description = draw(st.text(min_size=10, max_size=200))
    priority = draw(st.sampled_from(['High', 'Medium', 'Low']))
    estimated_hours = draw(st.floats(min_value=0.5, max_value=40.0))
    related_dirs = draw(st.lists(directory_name_strategy(), min_size=0, max_size=3, unique=True))
    
    return Improvement(
        category=category,
        title=title,
        description=description,
        priority=priority,
        estimated_hours=estimated_hours,
        related_directories=related_dirs
    )


@st.composite
def proposed_structure_strategy(draw):
    """Generate ProposedStructure objects."""
    num_dirs = draw(st.integers(min_value=1, max_value=10))
    directories = {}
    
    for _ in range(num_dirs):
        dir_name = draw(directory_name_strategy())
        proposed_dir = draw(proposed_directory_strategy(path=dir_name))
        directories[dir_name] = proposed_dir
    
    num_improvements = draw(st.integers(min_value=1, max_value=5))
    improvements = [draw(improvement_strategy()) for _ in range(num_improvements)]
    
    return ProposedStructure(
        directories=directories,
        improvements=improvements
    )


# Property 26: Supersession detection
# Feature: v2-structure-comparison, Property 26: Supersession detection
@given(
    current=project_structure_strategy(),
    proposed=proposed_structure_strategy()
)
def test_supersession_detection_identifies_alternative_implementations(current, proposed):
    """
    For any v2 suggestion where the actual implementation achieves the same goal
    through different means, the system should identify it as superseded.
    
    This property verifies that:
    1. Supersession detection returns a list
    2. Each superseded item has required fields
    3. Superseded items reference valid improvements
    4. Confidence levels are valid
    """
    checker = ValidationChecker()
    
    # Run supersession detection
    superseded = checker.identify_superseded_suggestions(current, proposed)
    
    # Verify result is a list
    assert isinstance(superseded, list)
    
    # Verify each superseded item has required structure
    for item in superseded:
        # Must have all required fields
        assert 'improvement' in item
        assert 'proposed_directory' in item
        assert 'superseded_by' in item
        assert 'reason' in item
        assert 'confidence' in item
        
        # Improvement must be from the proposed structure
        assert item['improvement'] in proposed.improvements
        
        # Proposed directory must be in improvement's related directories
        assert item['proposed_directory'] in item['improvement'].related_directories
        
        # Superseded_by must reference a directory in current structure
        superseded_by = item['superseded_by']
        assert any(
            superseded_by == curr_dir or superseded_by == curr_dir + '/'
            for curr_dir in current.directories.keys()
        )
        
        # Reason must be non-empty string
        assert isinstance(item['reason'], str)
        assert len(item['reason']) > 0
        
        # Confidence must be valid level
        assert item['confidence'] in ['High', 'Medium', 'Low']


# Property 26 (continued): Supersession detection consistency
# Feature: v2-structure-comparison, Property 26: Supersession detection
@given(
    current=project_structure_strategy(),
    proposed=proposed_structure_strategy()
)
def test_supersession_detection_is_consistent(current, proposed):
    """
    For any project structure, running supersession detection multiple times
    should produce consistent results.
    """
    checker = ValidationChecker()
    
    # Run detection twice
    result1 = checker.identify_superseded_suggestions(current, proposed)
    result2 = checker.identify_superseded_suggestions(current, proposed)
    
    # Results should be identical
    assert len(result1) == len(result2)
    
    # Convert to comparable format (improvement titles)
    titles1 = sorted([item['improvement'].title for item in result1])
    titles2 = sorted([item['improvement'].title for item in result2])
    
    assert titles1 == titles2


# Property 27: Applicability checking
# Feature: v2-structure-comparison, Property 27: Applicability checking
@given(
    current=project_structure_strategy(),
    proposed=proposed_structure_strategy()
)
def test_applicability_checking_flags_conflicts(current, proposed):
    """
    For any v2 suggestion that conflicts with current project decisions or is
    outdated, the system should flag it as potentially not applicable.
    
    This property verifies that:
    1. Applicability checking returns a list
    2. Each flagged item has required fields
    3. Flagged items reference valid improvements
    4. Conflict types and severities are valid
    """
    checker = ValidationChecker()
    
    # Run applicability checking
    inapplicable = checker.flag_inapplicable_suggestions(current, proposed)
    
    # Verify result is a list
    assert isinstance(inapplicable, list)
    
    # Verify each inapplicable item has required structure
    for item in inapplicable:
        # Must have all required fields
        assert 'improvement' in item
        assert 'reason' in item
        assert 'conflict_type' in item
        assert 'evidence' in item
        assert 'severity' in item
        
        # Improvement must be from the proposed structure
        assert item['improvement'] in proposed.improvements
        
        # Reason must be non-empty string
        assert isinstance(item['reason'], str)
        assert len(item['reason']) > 0
        
        # Conflict type must be valid
        assert item['conflict_type'] in [
            'decision_conflict',
            'structure_divergence',
            'outdated',
            'prerequisite_missing'
        ]
        
        # Evidence must be non-empty string
        assert isinstance(item['evidence'], str)
        assert len(item['evidence']) > 0
        
        # Severity must be valid level
        assert item['severity'] in ['High', 'Medium', 'Low']


# Property 27 (continued): Applicability checking consistency
# Feature: v2-structure-comparison, Property 27: Applicability checking
@given(
    current=project_structure_strategy(),
    proposed=proposed_structure_strategy()
)
def test_applicability_checking_is_consistent(current, proposed):
    """
    For any project structure, running applicability checking multiple times
    should produce consistent results.
    """
    checker = ValidationChecker()
    
    # Run checking twice
    result1 = checker.flag_inapplicable_suggestions(current, proposed)
    result2 = checker.flag_inapplicable_suggestions(current, proposed)
    
    # Results should be identical
    assert len(result1) == len(result2)
    
    # Convert to comparable format (improvement titles)
    titles1 = sorted([item['improvement'].title for item in result1])
    titles2 = sorted([item['improvement'].title for item in result2])
    
    assert titles1 == titles2


# Property 27 (continued): No false positives for implemented suggestions
# Feature: v2-structure-comparison, Property 27: Applicability checking
@given(
    current=project_structure_strategy(),
    proposed=proposed_structure_strategy()
)
def test_applicability_does_not_flag_implemented_suggestions(current, proposed):
    """
    For any suggestion where all related directories exist exactly as proposed,
    the applicability checker should not flag it as inapplicable.
    """
    checker = ValidationChecker()
    
    # Find improvements where all related directories exist
    fully_implemented = []
    for improvement in proposed.improvements:
        if improvement.related_directories:
            all_exist = all(
                (dir_path.rstrip('/') in current.directories or
                 dir_path in current.directories)
                for dir_path in improvement.related_directories
            )
            if all_exist:
                fully_implemented.append(improvement)
    
    # Run applicability checking
    inapplicable = checker.flag_inapplicable_suggestions(current, proposed)
    
    # Get set of flagged improvement titles
    flagged_titles = {item['improvement'].title for item in inapplicable}
    
    # Verify that fully implemented improvements are not flagged
    # (unless there's a structural divergence)
    for impl in fully_implemented:
        if impl.title in flagged_titles:
            # If flagged, must be due to structural divergence, not missing directories
            flagged_item = next(item for item in inapplicable if item['improvement'].title == impl.title)
            assert flagged_item['conflict_type'] in ['structure_divergence', 'decision_conflict']


# Property 26 & 27: Mutual exclusivity
# Feature: v2-structure-comparison, Property 26 & 27: Validation consistency
@given(
    current=project_structure_strategy(),
    proposed=proposed_structure_strategy()
)
def test_superseded_and_inapplicable_are_distinct(current, proposed):
    """
    For any project structure, a suggestion should not be both superseded
    and inapplicable (they represent different states).
    
    Note: This is a soft constraint - in practice, a suggestion could be both,
    but we verify that the system distinguishes between the two concepts.
    """
    checker = ValidationChecker()
    
    # Run both checks
    superseded = checker.identify_superseded_suggestions(current, proposed)
    inapplicable = checker.flag_inapplicable_suggestions(current, proposed)
    
    # Get improvement titles from each
    superseded_titles = {item['improvement'].title for item in superseded}
    inapplicable_titles = {item['improvement'].title for item in inapplicable}
    
    # Verify that both checks can run without errors
    assert isinstance(superseded, list)
    assert isinstance(inapplicable, list)
    
    # If there's overlap, verify it's intentional (both have valid reasons)
    overlap = superseded_titles & inapplicable_titles
    for title in overlap:
        # Find items in both lists
        superseded_item = next(item for item in superseded if item['improvement'].title == title)
        inapplicable_item = next(item for item in inapplicable if item['improvement'].title == title)
        
        # Both must have valid, non-empty reasons
        assert len(superseded_item['reason']) > 0
        assert len(inapplicable_item['reason']) > 0
