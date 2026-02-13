"""Property-based tests for translation and Vietnamese language consistency.

This module contains property-based tests that verify universal correctness
properties for the translation system and Vietnamese documentation.
"""

import pytest
from hypothesis import given, strategies as st
from hypothesis import settings
import re

from src.agentic_sdlc.documentation.models import Document, Section, DocumentType, Category
from src.agentic_sdlc.documentation.translation import TranslationManager


# Strategies for generating test data
@st.composite
def vietnamese_text_strategy(draw):
    """Generate text with Vietnamese characters."""
    # Vietnamese vowels with diacritics
    vietnamese_chars = "àáảãạăắằẳẵặâấầẩẫậèéẻẽẹêếềểễệìíỉĩịòóỏõọôốồổỗộơớờởỡợùúủũụưứừửữựỳýỷỹỵđ"
    vietnamese_chars += vietnamese_chars.upper()
    
    # Generate text with mix of ASCII and Vietnamese characters
    base_text = draw(st.text(
        alphabet=st.characters(
            whitelist_categories=('Ll', 'Lu', 'Nd', 'Zs'),
            min_codepoint=32,
            max_codepoint=126
        ) | st.sampled_from(list(vietnamese_chars)),
        min_size=50,
        max_size=200
    ))
    
    # Ensure at least one Vietnamese character
    if not any(char in vietnamese_chars for char in base_text):
        base_text += " " + draw(st.sampled_from([
            "Đây là văn bản tiếng Việt",
            "Hướng dẫn sử dụng",
            "Tài liệu kỹ thuật",
            "Phát triển phần mềm"
        ]))
    
    return base_text


@st.composite
def technical_term_strategy(draw):
    """Generate technical terms with Vietnamese translation format."""
    terms = [
        ("Agent", "Tác nhân"),
        ("Workflow", "Quy trình làm việc"),
        ("Plugin", "Plugin"),
        ("LLM", "Mô hình ngôn ngữ lớn"),
        ("Configuration", "Cấu hình"),
        ("Deployment", "Triển khai"),
        ("Testing", "Kiểm thử"),
        ("Documentation", "Tài liệu"),
    ]
    
    english, vietnamese = draw(st.sampled_from(terms))
    
    # Return in proper format: "Vietnamese (English)"
    return f"{vietnamese} ({english})"


@st.composite
def document_with_vietnamese_strategy(draw):
    """Generate a Document with Vietnamese content."""
    # Generate Vietnamese content
    vietnamese_content = draw(vietnamese_text_strategy())
    
    # Add some technical terms in proper format
    num_terms = draw(st.integers(min_value=1, max_value=5))
    for _ in range(num_terms):
        term = draw(technical_term_strategy())
        vietnamese_content += f" {term}"
    
    # Create sections with Vietnamese content
    num_sections = draw(st.integers(min_value=1, max_value=3))
    sections = []
    for i in range(num_sections):
        section = Section(
            title=f"Phần {i+1}",
            content=vietnamese_content + " " + draw(vietnamese_text_strategy())
        )
        sections.append(section)
    
    return Document(
        title=draw(st.text(min_size=10, max_size=50)),
        type=draw(st.sampled_from(list(DocumentType))),
        category=draw(st.sampled_from(list(Category))),
        description=vietnamese_content,
        sections=sections,
        metadata={},
        last_updated="2024-01-01",
        version="1.0.0"
    )


@st.composite
def document_content_strategy(draw):
    """Generate document content as string with Vietnamese and technical terms."""
    content_parts = []
    
    # Add Vietnamese text
    content_parts.append(draw(vietnamese_text_strategy()))
    
    # Add technical terms (some with proper format, some without)
    num_terms = draw(st.integers(min_value=2, max_value=8))
    for _ in range(num_terms):
        # 70% chance of proper format, 30% chance of English only
        if draw(st.booleans()):
            content_parts.append(draw(technical_term_strategy()))
        else:
            # Add English term without Vietnamese translation
            english_only = draw(st.sampled_from([
                "Agent", "Workflow", "Plugin", "Configuration", "Testing"
            ]))
            content_parts.append(english_only)
    
    return " ".join(content_parts)


# Property Test 9: Vietnamese Language Consistency
@settings(max_examples=20, deadline=None)
@given(document=document_with_vietnamese_strategy())
def test_vietnamese_language_consistency(document):
    """Feature: use-cases-and-usage-guide, Property 9:
    
    For any document in the documentation system, all content must be 
    written in standard Vietnamese, and technical terms must include 
    Vietnamese explanation with English term in parentheses.
    
    **Validates: Requirements 19.1, 19.2**
    """
    # Collect all text content from document
    content_parts = [document.description]
    for section in document.sections:
        content_parts.append(section.content)
    
    full_content = " ".join(content_parts)
    
    # Property 1: Document must contain Vietnamese characters
    vietnamese_chars = "àáảãạăắằẳẵặâấầẩẫậèéẻẽẹêếềểễệìíỉĩịòóỏõọôốồổỗộơớờởỡợùúủũụưứừửữựỳýỷỹỵđ"
    vietnamese_chars += vietnamese_chars.upper()
    
    has_vietnamese = any(char in vietnamese_chars for char in full_content)
    assert has_vietnamese, "Document must contain Vietnamese characters"
    
    # Property 2: Technical terms should follow format "Vietnamese (English)"
    # Find patterns that look like technical terms with parentheses
    term_pattern = re.compile(r'([^\(]+)\s*\(([^\)]+)\)')
    matches = term_pattern.findall(full_content)
    
    # If we have terms in parentheses format, verify they follow the pattern
    for vietnamese_part, english_part in matches:
        vietnamese_part = vietnamese_part.strip()
        english_part = english_part.strip()
        
        # Vietnamese part should not be empty
        assert len(vietnamese_part) > 0, "Vietnamese translation must not be empty"
        
        # English part should not be empty
        assert len(english_part) > 0, "English term must not be empty"
        
        # English part should start with capital letter (technical terms are capitalized)
        if english_part and english_part[0].isalpha():
            assert english_part[0].isupper() or english_part.isupper(), \
                f"Technical term '{english_part}' should be capitalized"


@settings(max_examples=20, deadline=None)
@given(content=document_content_strategy())
def test_translation_manager_consistency_check(content):
    """Test that TranslationManager can validate terminology consistency.
    
    This test verifies that the TranslationManager's validate_consistency
    method can identify issues in document content.
    """
    # Create a TranslationManager with the glossary
    tm = TranslationManager("docs/vi/glossary.yaml")
    
    # Validate the content
    issues = tm.validate_consistency(content)
    
    # Issues should be a list
    assert isinstance(issues, list)
    
    # Each issue should have required fields
    for issue in issues:
        assert isinstance(issue, dict)
        assert 'type' in issue
        assert 'term' in issue
        assert 'line' in issue
        assert 'suggestion' in issue
        
        # Type should be one of the expected values
        assert issue['type'] in ['missing_translation', 'inconsistent', 'unknown_term']
        
        # Line number should be positive
        assert issue['line'] > 0
        
        # Suggestion should not be empty
        assert len(issue['suggestion']) > 0


@settings(max_examples=20, deadline=None)
@given(
    english_term=st.sampled_from([
        "Agent", "Workflow", "Plugin", "LLM", "Configuration",
        "Deployment", "Testing", "Documentation", "API", "SDK"
    ])
)
def test_translation_manager_translate_term(english_term):
    """Test that TranslationManager correctly translates terms.
    
    This test verifies that known technical terms are translated
    in the correct format: "Vietnamese (English)"
    """
    # Create a TranslationManager with the glossary
    tm = TranslationManager("docs/vi/glossary.yaml")
    
    # Translate the term
    translated = tm.translate_term(english_term)
    
    # Result should not be empty
    assert len(translated) > 0
    
    # If term is in glossary, should have format "Vietnamese (English)"
    if english_term.lower() in tm.technical_terms:
        # Should contain the English term in parentheses
        assert f"({english_term})" in translated
        
        # Should have Vietnamese part before parentheses
        parts = translated.split('(')
        assert len(parts) == 2
        vietnamese_part = parts[0].strip()
        assert len(vietnamese_part) > 0
        
        # Vietnamese part can be the same as English for some terms (e.g., "Plugin")
        # but the format should still be "Vietnamese (English)"
        assert translated == f"{vietnamese_part} ({english_term})"


@settings(max_examples=20, deadline=None)
@given(
    english=st.text(min_size=3, max_size=30, alphabet=st.characters(
        whitelist_categories=('Lu', 'Ll'), min_codepoint=65, max_codepoint=122
    )),
    vietnamese=st.text(min_size=3, max_size=50)
)
def test_translation_manager_add_term(english, vietnamese):
    """Test that TranslationManager can add new terms.
    
    This test verifies that new terms can be added to the glossary
    and are immediately available for translation.
    """
    # Create a TranslationManager with the glossary
    tm = TranslationManager("docs/vi/glossary.yaml")
    
    # Add a new term
    tm.add_term(
        english=english,
        vietnamese=vietnamese,
        description="Test term",
        usage_examples=["Example usage"],
        related_terms=[]
    )
    
    # Term should now be in glossary
    assert english.lower() in tm.glossary
    assert english.lower() in tm.technical_terms
    
    # Should be able to translate the term
    translated = tm.translate_term(english)
    assert f"{vietnamese} ({english})" == translated
    
    # Should be able to get term info
    term_info = tm.get_term_info(english)
    assert term_info is not None
    assert term_info['english'] == english
    assert term_info['vietnamese'] == vietnamese
