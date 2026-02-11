"""Property-based tests for DocumentGenerator.

This module contains property-based tests that verify universal correctness
properties for the documentation generator, specifically markdown format compliance.
"""

import pytest
from hypothesis import given, strategies as st
from hypothesis import settings
from pathlib import Path
import tempfile
import shutil
from datetime import datetime

from src.agentic_sdlc.documentation.generator import DocumentGenerator
from src.agentic_sdlc.documentation.models import (
    Section,
    CodeBlock,
    Diagram,
    ClassReference,
    FunctionReference,
    MethodReference,
    Parameter,
    ReturnValue,
    PropertyReference,
)


# Strategies for generating test data
@st.composite
def section_strategy(draw):
    """Generate a valid Section."""
    return Section(
        title=draw(st.text(min_size=5, max_size=50)),
        content=draw(st.text(min_size=20, max_size=200)),
        subsections=None,
        code_blocks=None,
        diagrams=None
    )


@st.composite
def code_block_strategy(draw):
    """Generate a valid CodeBlock."""
    return CodeBlock(
        language=draw(st.sampled_from(['python', 'javascript', 'bash', 'yaml'])),
        code=draw(st.text(min_size=10, max_size=100)),
        caption=draw(st.one_of(st.none(), st.text(min_size=5, max_size=30))),
        line_numbers=draw(st.booleans())
    )


@st.composite
def diagram_strategy(draw):
    """Generate a valid Diagram."""
    diagram_types = ['flowchart', 'sequenceDiagram', 'classDiagram', 'stateDiagram']
    return Diagram(
        type=draw(st.sampled_from(diagram_types)),
        mermaid_code=draw(st.text(min_size=20, max_size=100)),
        caption=draw(st.text(min_size=5, max_size=50))
    )


@st.composite
def guide_content_strategy(draw):
    """Generate valid guide content."""
    num_sections = draw(st.integers(min_value=1, max_value=3))
    
    return {
        'title': draw(st.text(min_size=10, max_size=50)),
        'description': draw(st.text(min_size=20, max_size=200)),
        'sections': [draw(section_strategy()) for _ in range(num_sections)],
        'prerequisites': draw(st.lists(st.text(min_size=10, max_size=50), min_size=0, max_size=3)),
        'learning_objectives': draw(st.lists(st.text(min_size=10, max_size=50), min_size=0, max_size=3)),
        'related_guides': draw(st.lists(st.text(min_size=5, max_size=30), min_size=0, max_size=3)),
        'version': '3.0.0',
        'last_updated': datetime.now().isoformat()
    }


@st.composite
def parameter_strategy(draw):
    """Generate a valid Parameter."""
    return Parameter(
        name=draw(st.text(min_size=1, max_size=20, alphabet=st.characters(
            whitelist_categories=('Ll', 'Lu'), min_codepoint=97, max_codepoint=122
        ))),
        type=draw(st.sampled_from(['str', 'int', 'bool', 'List[str]', 'Dict[str, Any]'])),
        description=draw(st.text(min_size=10, max_size=100)),
        default=draw(st.one_of(st.none(), st.text(), st.integers())),
        required=draw(st.booleans())
    )


@st.composite
def return_value_strategy(draw):
    """Generate a valid ReturnValue."""
    return ReturnValue(
        type=draw(st.sampled_from(['str', 'int', 'bool', 'None', 'List[str]'])),
        description=draw(st.text(min_size=10, max_size=100))
    )


@st.composite
def method_reference_strategy(draw):
    """Generate a valid MethodReference."""
    num_params = draw(st.integers(min_value=0, max_value=3))
    num_examples = draw(st.integers(min_value=1, max_value=2))
    
    return MethodReference(
        name=draw(st.text(min_size=1, max_size=30, alphabet=st.characters(
            whitelist_categories=('Ll', 'Lu'), min_codepoint=97, max_codepoint=122
        ))),
        signature=draw(st.text(min_size=10, max_size=100)),
        description=draw(st.text(min_size=20, max_size=200)),
        parameters=[draw(parameter_strategy()) for _ in range(num_params)],
        returns=draw(return_value_strategy()),
        raises=draw(st.lists(st.text(min_size=5, max_size=30), min_size=0, max_size=2)),
        examples=[draw(code_block_strategy()) for _ in range(num_examples)]
    )


@st.composite
def class_reference_strategy(draw):
    """Generate a valid ClassReference."""
    num_methods = draw(st.integers(min_value=1, max_value=3))
    num_properties = draw(st.integers(min_value=0, max_value=3))
    num_examples = draw(st.integers(min_value=1, max_value=2))
    
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


@st.composite
def function_reference_strategy(draw):
    """Generate a valid FunctionReference."""
    num_params = draw(st.integers(min_value=0, max_value=3))
    num_examples = draw(st.integers(min_value=1, max_value=2))
    
    return FunctionReference(
        name=draw(st.text(min_size=1, max_size=30, alphabet=st.characters(
            whitelist_categories=('Ll', 'Lu'), min_codepoint=97, max_codepoint=122
        ))),
        signature=draw(st.text(min_size=10, max_size=100)),
        description=draw(st.text(min_size=20, max_size=200)),
        parameters=[draw(parameter_strategy()) for _ in range(num_params)],
        returns=draw(return_value_strategy()),
        raises=draw(st.lists(st.text(min_size=5, max_size=30), min_size=0, max_size=2)),
        examples=[draw(code_block_strategy()) for _ in range(num_examples)]
    )


# Property Test 11: Markdown Format Compliance
@settings(max_examples=20, deadline=None)
@given(
    guide_content=guide_content_strategy(),
    topic=st.text(min_size=5, max_size=30, alphabet=st.characters(
        whitelist_categories=('Ll', 'Lu'), min_codepoint=97, max_codepoint=122
    ))
)
def test_markdown_format_compliance_guide(guide_content, topic):
    """Feature: use-cases-and-usage-guide, Property 11:
    
    For any documentation file in the system, it must be in markdown format 
    (.md extension) and include version information and last updated date 
    in metadata.
    
    **Validates: Requirements 20.1, 20.4**
    """
    # Create temporary directory for output
    with tempfile.TemporaryDirectory() as temp_dir:
        generator = DocumentGenerator(output_dir=temp_dir, language="vi")
        
        # Generate guide document
        output_path = generator.generate_guide(
            topic=topic,
            content=guide_content
        )
        
        # Verify file exists and has .md extension
        assert output_path.exists()
        assert output_path.suffix == '.md', f"File must have .md extension, got {output_path.suffix}"
        
        # Read generated content
        content = output_path.read_text(encoding='utf-8')
        
        # Verify version information is present
        assert 'version' in guide_content or '3.0.0' in content, \
            "Document must include version information"
        
        # Verify last_updated date is present
        assert 'last_updated' in guide_content or 'Cập nhật lần cuối' in content, \
            "Document must include last updated date"
        
        # Verify markdown format - should have headers
        assert '#' in content, "Markdown document must contain headers"
        
        # Verify title is present (normalize whitespace)
        # The title should appear in the content, but whitespace may differ
        # Check that the title appears as a header (after # symbol)
        title_in_content = guide_content['title'].strip()
        # Normalize multiple spaces to single space for comparison
        title_normalized = ' '.join(title_in_content.split())
        content_normalized = ' '.join(content.split())
        assert title_normalized in content_normalized, \
            f"Document must contain the title. Expected '{title_normalized}' in content"


@settings(max_examples=20, deadline=None)
@given(
    name=st.text(min_size=5, max_size=30, alphabet=st.characters(
        whitelist_categories=('Ll', 'Lu'), min_codepoint=97, max_codepoint=122
    )),
    description=st.text(min_size=20, max_size=200),
    code_examples=st.lists(code_block_strategy(), min_size=1, max_size=3),
    diagrams=st.lists(diagram_strategy(), min_size=0, max_size=2)
)
def test_markdown_format_compliance_use_case(name, description, code_examples, diagrams):
    """Feature: use-cases-and-usage-guide, Property 11:
    
    For any use case documentation file, it must be in markdown format 
    (.md extension) and include version information and last updated date.
    
    **Validates: Requirements 20.1, 20.4**
    """
    # Create temporary directory for output
    with tempfile.TemporaryDirectory() as temp_dir:
        generator = DocumentGenerator(output_dir=temp_dir, language="vi")
        
        # Generate use case document
        output_path = generator.generate_use_case(
            name=name,
            description=description,
            code_examples=code_examples,
            diagrams=diagrams,
            scenario="Test scenario",
            problem="Test problem",
            solution="Test solution"
        )
        
        # Verify file exists and has .md extension
        assert output_path.exists()
        assert output_path.suffix == '.md', f"File must have .md extension, got {output_path.suffix}"
        
        # Read generated content
        content = output_path.read_text(encoding='utf-8')
        
        # Verify version information is present
        assert '3.0.0' in content or 'Phiên bản' in content, \
            "Document must include version information"
        
        # Verify last_updated date is present
        assert 'Cập nhật lần cuối' in content, \
            "Document must include last updated date"
        
        # Verify markdown format - should have headers
        assert '#' in content, "Markdown document must contain headers"
        
        # Verify code blocks are properly formatted
        assert '```' in content, "Use case must contain code blocks"


@settings(max_examples=20, deadline=None)
@given(
    module=st.text(min_size=5, max_size=50, alphabet=st.characters(
        whitelist_categories=('Ll', 'Lu'), min_codepoint=97, max_codepoint=122
    )).map(lambda x: f"agentic_sdlc.{x}"),
    classes=st.lists(class_reference_strategy(), min_size=0, max_size=2),
    functions=st.lists(function_reference_strategy(), min_size=0, max_size=2)
)
def test_markdown_format_compliance_api_reference(module, classes, functions):
    """Feature: use-cases-and-usage-guide, Property 11:
    
    For any API reference documentation file, it must be in markdown format 
    (.md extension) and include version information and last updated date.
    
    **Validates: Requirements 20.1, 20.4**
    """
    # Skip if both classes and functions are empty
    if not classes and not functions:
        return
    
    # Create temporary directory for output
    with tempfile.TemporaryDirectory() as temp_dir:
        generator = DocumentGenerator(output_dir=temp_dir, language="vi")
        
        # Generate API reference document
        output_path = generator.generate_api_reference(
            module=module,
            classes=classes,
            functions=functions,
            description="Test API reference"
        )
        
        # Verify file exists and has .md extension
        assert output_path.exists()
        assert output_path.suffix == '.md', f"File must have .md extension, got {output_path.suffix}"
        
        # Read generated content
        content = output_path.read_text(encoding='utf-8')
        
        # Verify version information is present
        assert '3.0.0' in content or 'Phiên bản' in content, \
            "Document must include version information"
        
        # Verify last_updated date is present
        assert 'Cập nhật lần cuối' in content, \
            "Document must include last updated date"
        
        # Verify markdown format - should have headers
        assert '#' in content, "Markdown document must contain headers"
        
        # Verify module path is present
        assert module in content, "API reference must contain module path"
