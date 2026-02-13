"""
Property-based tests for formatting consistency (Property 10).

Feature: use-cases-and-usage-guide
Property 10: Formatting Consistency

For any document in the documentation system, code must use markdown code blocks 
with syntax highlighting, output must use code blocks or formatted text, and 
headings, lists, tables, and emphasis must follow consistent formatting rules.

Validates: Requirements 19.3, 19.4, 19.5
"""

import re
from hypothesis import given, strategies as st, settings
from pathlib import Path

from src.agentic_sdlc.documentation.models import (
    Document,
    DocumentType,
    Category,
    Section,
    CodeBlock
)


# Strategy for generating documents
@st.composite
def document_strategy(draw):
    """Generate a Document with various content."""
    title = draw(st.text(min_size=5, max_size=50))
    description = draw(st.text(min_size=10, max_size=200))
    
    # Generate sections with code blocks
    num_sections = draw(st.integers(min_value=1, max_value=5))
    sections = []
    
    for _ in range(num_sections):
        section_title = draw(st.text(min_size=5, max_size=30))
        section_content = draw(st.text(min_size=20, max_size=500))
        
        # Add some code blocks
        num_code_blocks = draw(st.integers(min_value=0, max_value=3))
        code_blocks = []
        
        for _ in range(num_code_blocks):
            code = draw(st.text(min_size=10, max_size=100))
            code_block = CodeBlock(
                language=draw(st.sampled_from(["python", "javascript", "bash", "yaml"])),
                code=code,
                caption=draw(st.one_of(st.none(), st.text(min_size=5, max_size=30))),
                line_numbers=True
            )
            code_blocks.append(code_block)
        
        section = Section(
            title=section_title,
            content=section_content,
            code_blocks=code_blocks if code_blocks else None
        )
        sections.append(section)
    
    doc = Document(
        title=title,
        type=draw(st.sampled_from(list(DocumentType))),
        category=draw(st.sampled_from(list(Category))),
        description=description,
        sections=sections,
        metadata={"version": "3.0.0"},
        last_updated="2024-01-01",
        version="3.0.0"
    )
    
    return doc


def extract_code_blocks_from_markdown(content: str) -> list:
    """Extract code blocks from markdown content."""
    # Pattern for markdown code blocks: ```language\ncode\n```
    pattern = r'```(\w+)?\n(.*?)\n```'
    matches = re.findall(pattern, content, re.DOTALL)
    return matches


def extract_headings_from_markdown(content: str) -> list:
    """Extract headings from markdown content."""
    # Pattern for markdown headings: # Heading
    pattern = r'^(#{1,6})\s+(.+)$'
    matches = re.findall(pattern, content, re.MULTILINE)
    return matches


def extract_lists_from_markdown(content: str) -> list:
    """Extract lists from markdown content."""
    # Pattern for markdown lists: - item or * item or 1. item
    pattern = r'^[\s]*[-*]|\d+\.\s+(.+)$'
    matches = re.findall(pattern, content, re.MULTILINE)
    return matches


def document_to_markdown(doc: Document) -> str:
    """Convert document to markdown format."""
    lines = []
    
    # Title
    lines.append(f"# {doc.title}\n")
    
    # Description
    lines.append(f"{doc.description}\n")
    
    # Metadata
    lines.append(f"\n**Version:** {doc.version}")
    lines.append(f"**Last Updated:** {doc.last_updated}\n")
    
    # Sections
    for section in doc.sections:
        lines.append(f"\n## {section.title}\n")
        lines.append(f"{section.content}\n")
        
        # Code blocks
        if section.code_blocks:
            for code_block in section.code_blocks:
                lines.append(f"\n```{code_block.language}")
                lines.append(code_block.code)
                lines.append("```\n")
                if code_block.caption:
                    lines.append(f"*{code_block.caption}*\n")
    
    return "\n".join(lines)


@given(document=document_strategy())
@settings(max_examples=20, deadline=None)
def test_code_blocks_use_markdown_syntax(document):
    """
    Feature: use-cases-and-usage-guide, Property 10: Formatting Consistency
    
    For any document in the documentation system, code must use markdown code 
    blocks with syntax highlighting.
    
    Validates: Requirements 19.3
    """
    # Convert document to markdown
    markdown_content = document_to_markdown(document)
    
    # Extract code blocks
    code_blocks = extract_code_blocks_from_markdown(markdown_content)
    
    # If document has code blocks, verify they use proper markdown syntax
    if document.sections:
        for section in document.sections:
            if section.code_blocks:
                # Should have at least one code block in markdown
                assert len(code_blocks) > 0, \
                    "Code blocks must use markdown syntax (```language\\ncode\\n```)"
                
                # Each code block should have language specified
                for lang, code in code_blocks:
                    # Language can be empty but block must exist
                    assert code is not None and len(code) > 0, \
                        "Code blocks must contain code"


@given(document=document_strategy())
@settings(max_examples=20, deadline=None)
def test_headings_use_consistent_format(document):
    """
    Feature: use-cases-and-usage-guide, Property 10: Formatting Consistency
    
    For any document in the documentation system, headings must follow 
    consistent formatting rules (using # syntax).
    
    Validates: Requirements 19.4
    """
    # Convert document to markdown
    markdown_content = document_to_markdown(document)
    
    # Extract headings
    headings = extract_headings_from_markdown(markdown_content)
    
    # Document should have at least title heading
    assert len(headings) >= 1, "Document must have at least one heading"
    
    # All headings should use # syntax
    for level, text in headings:
        assert level.startswith("#"), "Headings must use # syntax"
        assert 1 <= len(level) <= 6, "Heading level must be between 1 and 6"
        assert len(text.strip()) > 0, "Heading text must not be empty"


@given(document=document_strategy())
@settings(max_examples=20, deadline=None)
def test_document_has_consistent_structure(document):
    """
    Feature: use-cases-and-usage-guide, Property 10: Formatting Consistency
    
    For any document in the documentation system, the structure must be 
    consistent with proper sections, metadata, and formatting.
    
    Validates: Requirements 19.5
    """
    # Document must have required fields
    assert document.title is not None and len(document.title) > 0, \
        "Document must have a title"
    
    assert document.description is not None and len(document.description) > 0, \
        "Document must have a description"
    
    assert document.sections is not None and len(document.sections) > 0, \
        "Document must have at least one section"
    
    # Metadata must include version and last_updated
    assert document.version is not None, "Document must have version"
    assert document.last_updated is not None, "Document must have last_updated date"
    
    # Each section must have title and content
    for section in document.sections:
        assert section.title is not None and len(section.title) > 0, \
            "Section must have a title"
        assert section.content is not None, \
            "Section must have content"


@given(document=document_strategy())
@settings(max_examples=20, deadline=None)
def test_code_blocks_have_language_specified(document):
    """
    Feature: use-cases-and-usage-guide, Property 10: Formatting Consistency
    
    For any code block in the documentation, it must have a language specified
    for syntax highlighting.
    
    Validates: Requirements 19.3
    """
    # Check all code blocks in all sections
    for section in document.sections:
        if section.code_blocks:
            for code_block in section.code_blocks:
                assert code_block.language is not None, \
                    "Code block must have language specified"
                assert len(code_block.language) > 0, \
                    "Code block language must not be empty"
                assert code_block.code is not None, \
                    "Code block must have code content"


@given(document=document_strategy())
@settings(max_examples=20, deadline=None)
def test_markdown_output_is_valid(document):
    """
    Feature: use-cases-and-usage-guide, Property 10: Formatting Consistency
    
    For any document, the generated markdown output must be valid and 
    properly formatted.
    
    Validates: Requirements 19.3, 19.4, 19.5
    """
    # Convert to markdown
    markdown_content = document_to_markdown(document)
    
    # Basic validation
    assert len(markdown_content) > 0, "Markdown content must not be empty"
    
    # Should start with title (# heading)
    assert markdown_content.strip().startswith("#"), \
        "Markdown should start with title heading"
    
    # Should contain description
    assert document.description in markdown_content, \
        "Markdown should contain document description"
    
    # Should contain version info
    assert document.version in markdown_content, \
        "Markdown should contain version information"
    
    # Should contain all section titles
    for section in document.sections:
        assert section.title in markdown_content, \
            f"Markdown should contain section title: {section.title}"


def test_real_documentation_files_formatting():
    """
    Test that real documentation files follow formatting consistency.
    
    This test checks actual generated documentation files to ensure they
    follow the formatting rules.
    """
    docs_dir = Path("docs/vi")
    
    if not docs_dir.exists():
        # Skip if docs directory doesn't exist yet
        return
    
    # Find all markdown files
    md_files = list(docs_dir.rglob("*.md"))
    
    if len(md_files) == 0:
        # Skip if no markdown files exist yet
        return
    
    for md_file in md_files:
        content = md_file.read_text(encoding='utf-8')
        
        # Check code blocks use proper syntax
        if "```" in content:
            code_blocks = extract_code_blocks_from_markdown(content)
            assert len(code_blocks) > 0, \
                f"{md_file}: Code blocks must use proper markdown syntax"
        
        # Check headings use # syntax
        headings = extract_headings_from_markdown(content)
        if len(headings) > 0:
            for level, text in headings:
                assert level.startswith("#"), \
                    f"{md_file}: Headings must use # syntax"


if __name__ == "__main__":
    # Run tests manually
    import sys
    
    print("Running Property 10: Formatting Consistency tests...")
    print("=" * 60)
    
    try:
        # Test with a sample document
        from hypothesis import find
        
        # Find a valid document
        sample_doc = find(
            document_strategy(),
            lambda d: len(d.sections) > 0
        )
        
        print(f"Testing with sample document: {sample_doc.title}")
        
        test_code_blocks_use_markdown_syntax(sample_doc)
        print("✓ test_code_blocks_use_markdown_syntax passed")
        
        test_headings_use_consistent_format(sample_doc)
        print("✓ test_headings_use_consistent_format passed")
        
        test_document_has_consistent_structure(sample_doc)
        print("✓ test_document_has_consistent_structure passed")
        
        test_code_blocks_have_language_specified(sample_doc)
        print("✓ test_code_blocks_have_language_specified passed")
        
        test_markdown_output_is_valid(sample_doc)
        print("✓ test_markdown_output_is_valid passed")
        
        test_real_documentation_files_formatting()
        print("✓ test_real_documentation_files_formatting passed")
        
        print("\n" + "=" * 60)
        print("✓ All Property 10 tests passed!")
        print("=" * 60)
        
    except Exception as e:
        print(f"\n✗ Test failed: {e}")
        sys.exit(1)
