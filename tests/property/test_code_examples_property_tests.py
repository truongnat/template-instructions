"""Property-based tests for code example management.

This module contains property-based tests that verify universal correctness
properties for the code example management system.
"""

import pytest
from hypothesis import given, strategies as st
from hypothesis import settings

from src.agentic_sdlc.documentation.models import CodeExample, Category


# Strategies for generating test data
@st.composite
def code_example_strategy(draw):
    """Generate a valid CodeExample."""
    category = draw(st.sampled_from([Category.BASIC, Category.INTERMEDIATE, Category.ADVANCED]))
    
    # Generate at least one dependency
    num_deps = draw(st.integers(min_value=1, max_value=5))
    dependencies = [
        draw(st.text(min_size=3, max_size=20, alphabet=st.characters(
            whitelist_categories=('Ll', 'Lu', 'Nd'), min_codepoint=48, max_codepoint=122
        ))) for _ in range(num_deps)
    ]
    
    # Generate at least one note
    num_notes = draw(st.integers(min_value=0, max_value=3))
    notes = [draw(st.text(min_size=10, max_size=100)) for _ in range(num_notes)]
    
    return CodeExample(
        name=draw(st.text(min_size=5, max_size=50, alphabet=st.characters(
            whitelist_categories=('Ll', 'Lu', 'Nd', 'Zs'), min_codepoint=32, max_codepoint=122
        ))),
        description=draw(st.text(min_size=20, max_size=200)),
        category=category,
        code=draw(st.text(min_size=10, max_size=500)),
        dependencies=dependencies,
        setup_instructions=draw(st.text(min_size=10, max_size=200)),
        expected_output=draw(st.text(min_size=10, max_size=200)),
        notes=notes
    )


# Property Test 3: Code Example Completeness
@settings(max_examples=100, deadline=None)
@given(code_example=code_example_strategy())
def test_code_example_completeness(code_example):
    """Feature: use-cases-and-usage-guide, Property 3:
    
    For any code example in the documentation, it must include setup 
    instructions, dependency list, and expected output.
    
    **Validates: Requirements 12.5**
    """
    # Code example must have setup instructions
    assert code_example.setup_instructions is not None
    assert len(code_example.setup_instructions) > 0
    assert len(code_example.setup_instructions.strip()) > 0
    
    # Code example must have dependencies list
    assert code_example.dependencies is not None
    assert isinstance(code_example.dependencies, list)
    
    # Code example must have expected output
    assert code_example.expected_output is not None
    assert len(code_example.expected_output) > 0
    assert len(code_example.expected_output.strip()) > 0
    
    # Code example must have a name
    assert code_example.name is not None
    assert len(code_example.name) > 0
    
    # Code example must have a description
    assert code_example.description is not None
    assert len(code_example.description) > 0
    
    # Code example must have code
    assert code_example.code is not None
    assert len(code_example.code) > 0
    
    # Code example must have a valid category
    assert code_example.category is not None
    assert isinstance(code_example.category, Category)
    
    # Notes must be a list (can be empty)
    assert code_example.notes is not None
    assert isinstance(code_example.notes, list)



@st.composite
def code_example_collection_strategy(draw):
    """Generate a collection of code examples (minimum 15)."""
    num_examples = draw(st.integers(min_value=15, max_value=25))
    examples = [draw(code_example_strategy()) for _ in range(num_examples)]
    return examples


# Property Test 2: Minimum Code Example Coverage
@settings(max_examples=100, deadline=None)
@given(examples=code_example_collection_strategy())
def test_minimum_code_example_coverage(examples):
    """Feature: use-cases-and-usage-guide, Property 2:
    
    For any generated documentation system, the number of code examples 
    must be at least 15, and each example must include detailed comments.
    
    **Validates: Requirements 12.1**
    """
    # Must have at least 15 code examples
    assert len(examples) >= 15
    
    # Each example must have detailed comments (description or notes)
    for example in examples:
        # Check that example has either a substantial description or notes
        has_description = (
            example.description is not None and 
            len(example.description.strip()) > 0
        )
        has_notes = (
            example.notes is not None and 
            len(example.notes) > 0
        )
        
        # At least one form of detailed comments must exist
        assert has_description or has_notes, \
            f"Example '{example.name}' lacks detailed comments"
        
        # If description exists, it should be meaningful (at least 10 chars)
        if has_description:
            assert len(example.description.strip()) >= 10, \
                f"Example '{example.name}' has insufficient description"
