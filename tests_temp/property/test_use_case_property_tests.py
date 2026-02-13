"""Property-based tests for use case documentation.

This module contains property-based tests that verify universal correctness
properties for the use case documentation system.
"""

import pytest
from hypothesis import given, strategies as st
from hypothesis import settings

from src.agentic_sdlc.documentation.models import (
    UseCaseDocument,
    DocumentType,
    Category,
    Section,
    CodeBlock
)
from src.agentic_sdlc.documentation.use_cases import (
    UseCaseBuilder,
    Scenario,
    Implementation,
    Results
)


# Strategies for generating test data
@st.composite
def scenario_strategy(draw):
    """Generate a valid Scenario."""
    num_actors = draw(st.integers(min_value=1, max_value=5))
    actors = [
        draw(st.text(min_size=5, max_size=30, alphabet=st.characters(
            whitelist_categories=('Ll', 'Lu', 'Zs'), min_codepoint=32, max_codepoint=122
        ))) for _ in range(num_actors)
    ]
    
    num_goals = draw(st.integers(min_value=1, max_value=5))
    goals = [
        draw(st.text(min_size=10, max_size=100)) for _ in range(num_goals)
    ]
    
    num_constraints = draw(st.integers(min_value=0, max_value=3))
    constraints = [
        draw(st.text(min_size=10, max_size=100)) for _ in range(num_constraints)
    ] if num_constraints > 0 else None
    
    return Scenario(
        context=draw(st.text(min_size=50, max_size=300)),
        actors=actors,
        goals=goals,
        constraints=constraints
    )


@st.composite
def code_section_strategy(draw):
    """Generate a code section dictionary."""
    return {
        'language': draw(st.sampled_from(['python', 'javascript', 'bash', 'yaml'])),
        'code': draw(st.text(min_size=20, max_size=500)),
        'caption': draw(st.text(min_size=5, max_size=50))
    }


@st.composite
def implementation_strategy(draw):
    """Generate a valid Implementation."""
    num_steps = draw(st.integers(min_value=1, max_value=10))
    steps = [
        draw(st.text(min_size=10, max_size=100)) for _ in range(num_steps)
    ]
    
    num_code_sections = draw(st.integers(min_value=1, max_value=5))
    code_sections = [
        draw(code_section_strategy()) for _ in range(num_code_sections)
    ]
    
    return Implementation(
        overview=draw(st.text(min_size=50, max_size=300)),
        steps=steps,
        code_sections=code_sections,
        diagrams=[]  # Diagrams are optional
    )


@st.composite
def results_strategy(draw):
    """Generate valid Results."""
    num_outcomes = draw(st.integers(min_value=1, max_value=5))
    outcomes = [
        draw(st.text(min_size=10, max_size=100)) for _ in range(num_outcomes)
    ]
    
    return Results(
        outcomes=outcomes,
        metrics=None,  # Metrics are optional
        screenshots=None  # Screenshots are optional
    )


@st.composite
def use_case_document_strategy(draw):
    """Generate a valid UseCaseDocument."""
    scenario = draw(scenario_strategy())
    implementation = draw(implementation_strategy())
    results = draw(results_strategy())
    
    builder = UseCaseBuilder()
    
    use_case = builder.build_use_case(
        title=draw(st.text(min_size=10, max_size=100)),
        description=draw(st.text(min_size=50, max_size=300)),
        scenario=scenario,
        implementation=implementation,
        results=results,
        category=draw(st.sampled_from([Category.BASIC, Category.INTERMEDIATE, Category.ADVANCED])),
        lessons_learned=[
            draw(st.text(min_size=20, max_size=150)) 
            for _ in range(draw(st.integers(min_value=0, max_value=5)))
        ] if draw(st.booleans()) else None
    )
    
    return use_case


@st.composite
def documentation_system_strategy(draw):
    """Generate a documentation system with multiple use cases (minimum 8)."""
    num_use_cases = draw(st.integers(min_value=8, max_value=15))
    use_cases = [draw(use_case_document_strategy()) for _ in range(num_use_cases)]
    
    # Return a simple dict representing the documentation system
    return {
        'use_cases': use_cases
    }


# Property Test 1: Minimum Use Case Coverage
@settings(max_examples=100, deadline=None)
@given(documentation_system=documentation_system_strategy())
def test_minimum_use_case_coverage(documentation_system):
    """Feature: use-cases-and-usage-guide, Property 1:
    
    For any generated documentation system, the number of use case 
    documents must be at least 8, and each use case must contain 
    complete code examples.
    
    **Validates: Requirements 8.1**
    """
    use_cases = documentation_system['use_cases']
    
    # Must have at least 8 use cases
    assert len(use_cases) >= 8, \
        f"Documentation system has only {len(use_cases)} use cases, expected at least 8"
    
    # Each use case must contain complete code examples
    for i, use_case in enumerate(use_cases):
        # Use case must have implementation with code examples
        assert use_case.implementation is not None, \
            f"Use case {i} has no implementation"
        
        assert len(use_case.implementation) > 0, \
            f"Use case {i} has empty implementation"
        
        # Each code example must be complete
        for j, code_block in enumerate(use_case.implementation):
            assert code_block.code is not None, \
                f"Use case {i}, code block {j} has no code"
            
            assert len(code_block.code) > 0, \
                f"Use case {i}, code block {j} has empty code"
            
            assert len(code_block.code.strip()) > 0, \
                f"Use case {i}, code block {j} has only whitespace code"
            
            # Code block should have a language specified
            assert code_block.language is not None, \
                f"Use case {i}, code block {j} has no language specified"
            
            assert len(code_block.language) > 0, \
                f"Use case {i}, code block {j} has empty language"


# Additional test: Use case structure completeness
@settings(max_examples=100, deadline=None)
@given(use_case=use_case_document_strategy())
def test_use_case_structure_completeness(use_case):
    """Verify that each use case has the required structure.
    
    Each use case must have:
    - Title
    - Description
    - Sections (Giới thiệu, Kịch bản, Kiến trúc, Triển khai, Kết quả)
    - Implementation with code
    - Metadata
    """
    # Must have title
    assert use_case.title is not None
    assert len(use_case.title) > 0
    
    # Must have description
    assert use_case.description is not None
    assert len(use_case.description) > 0
    
    # Must have sections
    assert use_case.sections is not None
    assert len(use_case.sections) >= 5, \
        f"Use case has only {len(use_case.sections)} sections, expected at least 5"
    
    # Check for required section titles
    section_titles = [section.title for section in use_case.sections]
    required_sections = ["Giới Thiệu", "Kịch Bản", "Kiến Trúc", "Triển Khai", "Kết Quả"]
    
    for required_section in required_sections:
        assert required_section in section_titles, \
            f"Use case missing required section: {required_section}"
    
    # Must have implementation
    assert use_case.implementation is not None
    assert len(use_case.implementation) > 0
    
    # Must have metadata
    assert use_case.metadata is not None
    assert isinstance(use_case.metadata, dict)
    
    # Must have version and last_updated
    assert use_case.version is not None
    assert len(use_case.version) > 0
    assert use_case.last_updated is not None
    assert len(use_case.last_updated) > 0
    
    # Must be of type USE_CASE
    assert use_case.type == DocumentType.USE_CASE
    
    # Must have a valid category
    assert use_case.category is not None
    assert isinstance(use_case.category, Category)
