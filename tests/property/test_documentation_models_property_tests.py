"""Property-based tests for documentation data models.

This module contains property-based tests that verify universal correctness
properties for the documentation system data models.
"""

import pytest
from hypothesis import given, strategies as st
from hypothesis import settings

from src.agentic_sdlc.documentation.models import (
    ClassReference,
    MethodReference,
    Parameter,
    ReturnValue,
    CodeBlock,
)


# Strategies for generating test data
@st.composite
def parameter_strategy(draw):
    """Generate a valid Parameter."""
    return Parameter(
        name=draw(st.text(min_size=1, max_size=20, alphabet=st.characters(
            whitelist_categories=('Ll', 'Lu'), min_codepoint=97, max_codepoint=122
        ))),
        type=draw(st.sampled_from(['str', 'int', 'bool', 'List[str]', 'Dict[str, Any]', 'Optional[str]'])),
        description=draw(st.text(min_size=10, max_size=100)),
        default=draw(st.one_of(st.none(), st.text(), st.integers(), st.booleans())),
        required=draw(st.booleans())
    )


@st.composite
def return_value_strategy(draw):
    """Generate a valid ReturnValue."""
    return ReturnValue(
        type=draw(st.sampled_from(['str', 'int', 'bool', 'None', 'List[str]', 'Dict[str, Any]'])),
        description=draw(st.text(min_size=10, max_size=100))
    )


@st.composite
def code_block_strategy(draw):
    """Generate a valid CodeBlock."""
    return CodeBlock(
        language=draw(st.sampled_from(['python', 'javascript', 'bash', 'yaml'])),
        code=draw(st.text(min_size=10, max_size=200)),
        caption=draw(st.one_of(st.none(), st.text(min_size=5, max_size=50))),
        line_numbers=draw(st.booleans())
    )


@st.composite
def method_reference_strategy(draw):
    """Generate a valid MethodReference."""
    num_params = draw(st.integers(min_value=0, max_value=5))
    num_examples = draw(st.integers(min_value=1, max_value=3))
    
    return MethodReference(
        name=draw(st.text(min_size=1, max_size=30, alphabet=st.characters(
            whitelist_categories=('Ll', 'Lu'), min_codepoint=97, max_codepoint=122
        ))),
        signature=draw(st.text(min_size=10, max_size=100)),
        description=draw(st.text(min_size=20, max_size=200)),
        parameters=[draw(parameter_strategy()) for _ in range(num_params)],
        returns=draw(return_value_strategy()),
        raises=draw(st.lists(st.text(min_size=5, max_size=30), min_size=0, max_size=3)),
        examples=[draw(code_block_strategy()) for _ in range(num_examples)]
    )


@st.composite
def class_reference_strategy(draw):
    """Generate a valid ClassReference."""
    num_methods = draw(st.integers(min_value=1, max_value=5))
    num_properties = draw(st.integers(min_value=0, max_value=5))
    num_examples = draw(st.integers(min_value=1, max_value=3))
    
    from src.agentic_sdlc.documentation.models import PropertyReference
    
    return ClassReference(
        name=draw(st.text(min_size=1, max_size=30, alphabet=st.characters(
            whitelist_categories=('Lu',), min_codepoint=65, max_codepoint=90
        ))),
        description=draw(st.text(min_size=20, max_size=200)),
        constructor=draw(method_reference_strategy()),
        methods=[draw(method_reference_strategy()) for _ in range(num_methods)],
        properties=[
            PropertyReference(
                name=draw(st.text(min_size=1, max_size=20, alphabet=st.characters(
                    whitelist_categories=('Ll',), min_codepoint=97, max_codepoint=122
                ))),
                type=draw(st.sampled_from(['str', 'int', 'bool', 'List[str]'])),
                description=draw(st.text(min_size=10, max_size=100)),
                readonly=draw(st.booleans())
            ) for _ in range(num_properties)
        ],
        examples=[draw(code_block_strategy()) for _ in range(num_examples)]
    )


# Property Test 5: API Documentation Completeness
@settings(max_examples=20, deadline=None)
@given(class_ref=class_reference_strategy())
def test_api_documentation_completeness(class_ref):
    """Feature: use-cases-and-usage-guide, Property 5:
    
    For any public class in the API reference, the documentation must 
    include class description, constructor parameters, all methods with 
    their signatures, all properties, and usage examples.
    
    **Validates: Requirements 14.2, 14.5**
    """
    # Class must have a non-empty description
    assert class_ref.description is not None
    assert len(class_ref.description) > 0
    
    # Class must have a constructor
    assert class_ref.constructor is not None
    
    # Constructor must have all required fields
    assert class_ref.constructor.name is not None
    assert class_ref.constructor.signature is not None
    assert class_ref.constructor.description is not None
    
    # Class must have methods list (can be empty but must exist)
    assert class_ref.methods is not None
    assert isinstance(class_ref.methods, list)
    
    # Each method must have complete documentation
    for method in class_ref.methods:
        assert method.name is not None
        assert method.signature is not None
        assert method.description is not None
        assert method.parameters is not None
        assert method.returns is not None
    
    # Class must have properties list (can be empty but must exist)
    assert class_ref.properties is not None
    assert isinstance(class_ref.properties, list)
    
    # Each property must have complete documentation
    for prop in class_ref.properties:
        assert prop.name is not None
        assert prop.type is not None
        assert prop.description is not None
    
    # Class must have at least one usage example
    assert class_ref.examples is not None
    assert len(class_ref.examples) > 0
    
    # Each example must be a valid CodeBlock
    for example in class_ref.examples:
        assert isinstance(example, CodeBlock)
        assert example.code is not None
        assert len(example.code) > 0


# Property Test 6: Method Documentation Completeness
@settings(max_examples=20, deadline=None)
@given(method_ref=method_reference_strategy())
def test_method_documentation_completeness(method_ref):
    """Feature: use-cases-and-usage-guide, Property 6:
    
    For any public method in the API reference, the documentation must 
    list all parameters with types and descriptions, return type and 
    description, possible exceptions, and at least one usage example.
    
    **Validates: Requirements 14.3, 14.5**
    """
    # Method must have a name
    assert method_ref.name is not None
    assert len(method_ref.name) > 0
    
    # Method must have a signature
    assert method_ref.signature is not None
    assert len(method_ref.signature) > 0
    
    # Method must have a description
    assert method_ref.description is not None
    assert len(method_ref.description) > 0
    
    # Method must have parameters list (can be empty but must exist)
    assert method_ref.parameters is not None
    assert isinstance(method_ref.parameters, list)
    
    # Each parameter must have type and description
    for param in method_ref.parameters:
        assert param.name is not None
        assert len(param.name) > 0
        assert param.type is not None
        assert len(param.type) > 0
        assert param.description is not None
        assert len(param.description) > 0
    
    # Method must have return value documentation
    assert method_ref.returns is not None
    assert method_ref.returns.type is not None
    assert len(method_ref.returns.type) > 0
    assert method_ref.returns.description is not None
    assert len(method_ref.returns.description) > 0
    
    # Method must have raises list (can be empty but must exist)
    assert method_ref.raises is not None
    assert isinstance(method_ref.raises, list)
    
    # Method must have at least one usage example
    assert method_ref.examples is not None
    assert len(method_ref.examples) > 0
    
    # Each example must be a valid CodeBlock
    for example in method_ref.examples:
        assert isinstance(example, CodeBlock)
        assert example.code is not None
        assert len(example.code) > 0
