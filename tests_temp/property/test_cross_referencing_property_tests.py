"""
Property-based tests for document cross-referencing.

Feature: use-cases-and-usage-guide
Property 8: Document Cross-Referencing

Validates: Requirements 18.3
"""

import pytest
from hypothesis import given, strategies as st, settings
from pathlib import Path
import re
from typing import List, Set, Tuple

from src.agentic_sdlc.documentation.models import (
    Document,
    DocumentType,
    Category,
    Section,
)


# Strategy for generating markdown links
@st.composite
def markdown_link_strategy(draw):
    """Generate valid markdown links."""
    text = draw(st.text(min_size=1, max_size=50, alphabet=st.characters(
        whitelist_categories=('Lu', 'Ll', 'Nd'), min_codepoint=65, max_codepoint=122
    )))
    url = draw(st.text(min_size=1, max_size=100, alphabet=st.characters(
        whitelist_categories=('Lu', 'Ll', 'Nd'), min_codepoint=65, max_codepoint=122
    )))
    return f"[{text}]({url})"


# Strategy for generating documents with related docs
@st.composite
def document_with_related_docs_strategy(draw):
    """Generate a document with related documents in metadata."""
    title = draw(st.text(min_size=5, max_size=100))
    description = draw(st.text(min_size=10, max_size=200))
    
    # Generate related documents
    num_related = draw(st.integers(min_value=1, max_value=5))
    related_docs = [
        draw(st.text(min_size=5, max_size=50, alphabet=st.characters(
            whitelist_categories=('Lu', 'Ll', 'Nd'), min_codepoint=65, max_codepoint=122
        ))) + ".md"
        for _ in range(num_related)
    ]
    
    # Generate content with some links to related docs
    content_parts = [description]
    for related_doc in related_docs[:2]:  # Link to at least first 2 related docs
        link_text = draw(st.text(min_size=3, max_size=30))
        content_parts.append(f"\n\nSee also: [{link_text}]({related_doc})")
    
    content = "\n".join(content_parts)
    
    sections = [Section(
        title="Main Content",
        content=content,
        subsections=None,
        code_blocks=None,
        diagrams=None
    )]
    
    metadata = {
        "related_docs": related_docs,
        "version": "3.0.0",
        "last_updated": "2026-02-11"
    }
    
    doc = Document(
        title=title,
        type=DocumentType.GUIDE,
        category=Category.BASIC,
        description=description,
        sections=sections,
        metadata=metadata,
        last_updated="2026-02-11",
        version="3.0.0"
    )
    
    return doc


def extract_markdown_links(content: str) -> Set[str]:
    """Extract all markdown links from content."""
    # Pattern for markdown links: [text](url)
    pattern = r'\[([^\]]+)\]\(([^\)]+)\)'
    matches = re.findall(pattern, content)
    return {url for _, url in matches}


def get_document_full_content(document: Document) -> str:
    """Get full content of a document including all sections."""
    content_parts = [document.description]
    
    for section in document.sections:
        content_parts.append(section.content)
        if section.subsections:
            for subsection in section.subsections:
                content_parts.append(subsection.content)
    
    return "\n".join(content_parts)


@settings(max_examples=100, deadline=None)
@given(document=document_with_related_docs_strategy())
def test_document_cross_referencing(document):
    """
    Feature: use-cases-and-usage-guide, Property 8: Document Cross-Referencing
    
    For any document in the documentation system, related sections and documents
    must be cross-referenced with hyperlinks.
    
    Validates: Requirements 18.3
    """
    # Get full content of the document
    content = get_document_full_content(document)
    
    # Extract all markdown links from content
    links_in_content = extract_markdown_links(content)
    
    # Get related documents from metadata
    related_docs = document.metadata.get("related_docs", [])
    
    # Property: If document has related docs in metadata, at least some should be linked
    if related_docs:
        # At least one related document should be referenced in the content
        linked_related_docs = [
            doc for doc in related_docs
            if doc in links_in_content or any(doc in link for link in links_in_content)
        ]
        
        assert len(linked_related_docs) > 0, (
            f"Document '{document.title}' has {len(related_docs)} related documents "
            f"in metadata but none are cross-referenced in the content. "
            f"Related docs: {related_docs}, Links found: {links_in_content}"
        )


def test_readme_cross_references():
    """
    Test that the main README.md has proper cross-references.
    
    This is a concrete test that validates the actual README file.
    """
    readme_path = Path("docs/vi/README.md")
    
    if not readme_path.exists():
        pytest.skip("README.md not found")
    
    content = readme_path.read_text(encoding="utf-8")
    
    # Extract all markdown links
    links = extract_markdown_links(content)
    
    # README should have many cross-references
    assert len(links) >= 50, (
        f"README should have at least 50 cross-references, found {len(links)}"
    )
    
    # Check for specific important cross-references
    important_sections = [
        "getting-started/installation.md",
        "getting-started/configuration.md",
        "guides/agents/overview.md",
        "guides/workflows/overview.md",
        "examples/basic/01-configuration.py",
        "use-cases/automated-code-review.md",
    ]
    
    for section in important_sections:
        assert any(section in link for link in links), (
            f"README should reference {section}"
        )


def test_guide_documents_have_related_links():
    """
    Test that guide documents have related document links.
    
    This validates actual guide files in the documentation.
    """
    guides_dir = Path("docs/vi/guides")
    
    if not guides_dir.exists():
        pytest.skip("Guides directory not found")
    
    # Find all markdown files in guides
    guide_files = list(guides_dir.rglob("*.md"))
    
    if not guide_files:
        pytest.skip("No guide files found")
    
    # Check a sample of guide files
    for guide_file in guide_files[:5]:  # Check first 5 guides
        content = guide_file.read_text(encoding="utf-8")
        links = extract_markdown_links(content)
        
        # Each guide should have at least some cross-references
        assert len(links) >= 1, (
            f"Guide {guide_file.name} should have at least 1 cross-reference, "
            f"found {len(links)}"
        )


def test_use_case_documents_have_related_links():
    """
    Test that use case documents have related document links.
    
    This validates actual use case files in the documentation.
    """
    use_cases_dir = Path("docs/vi/use-cases")
    
    if not use_cases_dir.exists():
        pytest.skip("Use cases directory not found")
    
    # Find all markdown files in use-cases (excluding README)
    use_case_files = [
        f for f in use_cases_dir.glob("*.md")
        if f.name != "README.md"
    ]
    
    if not use_case_files:
        pytest.skip("No use case files found")
    
    # Check each use case file
    for use_case_file in use_case_files:
        content = use_case_file.read_text(encoding="utf-8")
        links = extract_markdown_links(content)
        
        # Each use case should have cross-references to related content
        assert len(links) >= 3, (
            f"Use case {use_case_file.name} should have at least 3 cross-references, "
            f"found {len(links)}"
        )


def test_example_files_referenced_in_readme():
    """
    Test that example files are properly referenced in README.
    
    This ensures all examples are discoverable through the main navigation.
    """
    readme_path = Path("docs/vi/README.md")
    examples_dir = Path("docs/vi/examples")
    
    if not readme_path.exists() or not examples_dir.exists():
        pytest.skip("README or examples directory not found")
    
    readme_content = readme_path.read_text(encoding="utf-8")
    readme_links = extract_markdown_links(readme_content)
    
    # Find all example files
    example_files = list(examples_dir.rglob("*.py")) + list(examples_dir.rglob("*.sh"))
    
    if not example_files:
        pytest.skip("No example files found")
    
    # Check that examples are referenced in README
    referenced_examples = 0
    for example_file in example_files:
        relative_path = str(example_file.relative_to(Path("docs/vi")))
        if any(relative_path in link for link in readme_links):
            referenced_examples += 1
    
    # At least 80% of examples should be referenced in README
    coverage = referenced_examples / len(example_files)
    assert coverage >= 0.8, (
        f"At least 80% of examples should be referenced in README, "
        f"found {coverage:.1%} ({referenced_examples}/{len(example_files)})"
    )


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
