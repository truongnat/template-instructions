"""
Property-based tests for troubleshooting documentation.

Feature: use-cases-and-usage-guide
Property 12: Minimum Troubleshooting Coverage
Validates: Requirements 10.4
"""

import pytest
from hypothesis import given, strategies as st, settings
from pathlib import Path
import re


# Strategy for generating troubleshooting documentation paths
@st.composite
def troubleshooting_docs(draw):
    """Generate troubleshooting documentation structure."""
    base_path = Path("docs/vi/troubleshooting")
    
    # Common errors document
    common_errors_path = base_path / "common-errors.md"
    
    return {
        "base_path": base_path,
        "common_errors": common_errors_path,
        "exists": common_errors_path.exists()
    }


def count_error_sections(content: str) -> int:
    """
    Count the number of error sections in troubleshooting documentation.
    
    Error sections are identified by:
    - Numbered headings (## 1., ## 2., etc.)
    - Or headings with "Error" in the title
    """
    # Pattern for numbered sections (## 1. Title, ## 2. Title, etc.)
    numbered_pattern = r'^##\s+\d+\.'
    
    # Pattern for error-related headings
    error_pattern = r'^##\s+.*(?:Error|Lỗi)'
    
    lines = content.split('\n')
    error_count = 0
    
    for line in lines:
        if re.match(numbered_pattern, line, re.MULTILINE):
            error_count += 1
        elif re.match(error_pattern, line, re.MULTILINE | re.IGNORECASE):
            # Only count if not already counted by numbered pattern
            if not re.match(numbered_pattern, line, re.MULTILINE):
                error_count += 1
    
    return error_count


def has_solution_section(error_section: str) -> bool:
    """
    Check if an error section has a solution.
    
    Solutions are identified by:
    - "Giải Pháp" heading
    - "Solution" heading
    - Code blocks with solutions
    """
    solution_patterns = [
        r'###\s+Giải Pháp',
        r'###\s+Solution',
        r'###\s+Cách\s+\d+:',  # Cách 1:, Cách 2:, etc.
    ]
    
    for pattern in solution_patterns:
        if re.search(pattern, error_section, re.IGNORECASE):
            return True
    
    return False


def extract_error_sections(content: str) -> list:
    """
    Extract individual error sections from the document.
    
    Returns a list of error section contents.
    """
    # Split by ## headings
    sections = re.split(r'^##\s+', content, flags=re.MULTILINE)
    
    # Filter to only numbered error sections
    error_sections = []
    for section in sections:
        if re.match(r'\d+\.', section):
            error_sections.append(section)
    
    return error_sections


@settings(max_examples=100, deadline=None)
@given(docs=troubleshooting_docs())
def test_minimum_troubleshooting_coverage(docs):
    """
    Feature: use-cases-and-usage-guide, Property 12: Minimum Troubleshooting Coverage
    
    For any generated documentation system, the troubleshooting guide must 
    document at least 10 common errors with their solutions.
    
    Validates: Requirements 10.4
    """
    # Check that troubleshooting directory exists
    assert docs["base_path"].exists(), \
        f"Troubleshooting directory must exist at {docs['base_path']}"
    
    # Check that common-errors.md exists
    assert docs["common_errors"].exists(), \
        f"Common errors document must exist at {docs['common_errors']}"
    
    # Read the common errors document
    content = docs["common_errors"].read_text(encoding='utf-8')
    
    # Count error sections
    error_count = count_error_sections(content)
    
    # Property: Must have at least 10 documented errors
    assert error_count >= 10, \
        f"Troubleshooting guide must document at least 10 common errors, found {error_count}"
    
    # Extract error sections
    error_sections = extract_error_sections(content)
    
    # Property: Each error must have a solution
    errors_without_solutions = []
    for i, section in enumerate(error_sections, 1):
        if not has_solution_section(section):
            errors_without_solutions.append(i)
    
    assert len(errors_without_solutions) == 0, \
        f"All errors must have solutions. Errors without solutions: {errors_without_solutions}"


def test_troubleshooting_document_structure():
    """
    Test that troubleshooting documents have proper structure.
    
    This is a unit test that complements the property test.
    """
    base_path = Path("docs/vi/troubleshooting")
    
    # Check required files exist
    required_files = [
        "common-errors.md",
        "debugging.md",
        "faq.md"
    ]
    
    for filename in required_files:
        file_path = base_path / filename
        assert file_path.exists(), f"Required file {filename} must exist"
        
        # Check file is not empty
        content = file_path.read_text(encoding='utf-8')
        assert len(content) > 0, f"File {filename} must not be empty"
        
        # Check has title
        assert content.startswith('#'), f"File {filename} must start with a title"


def test_common_errors_content():
    """
    Test that common-errors.md has expected content structure.
    """
    file_path = Path("docs/vi/troubleshooting/common-errors.md")
    
    if not file_path.exists():
        pytest.skip("common-errors.md not yet generated")
    
    content = file_path.read_text(encoding='utf-8')
    
    # Check for key sections
    assert "Giới Thiệu" in content or "Introduction" in content, \
        "Document must have introduction section"
    
    # Check for error descriptions
    assert "Mô Tả Lỗi" in content or "Error Description" in content, \
        "Errors must have descriptions"
    
    # Check for solutions
    assert "Giải Pháp" in content or "Solution" in content, \
        "Errors must have solutions"
    
    # Check for graceful degradation mentions
    assert "Graceful Degradation" in content or "degradation" in content.lower(), \
        "Document must discuss graceful degradation"
    
    # Check for fallback mechanisms
    assert "Fallback" in content or "fallback" in content.lower(), \
        "Document must discuss fallback mechanisms"


def test_debugging_guide_content():
    """
    Test that debugging.md has expected content.
    """
    file_path = Path("docs/vi/troubleshooting/debugging.md")
    
    if not file_path.exists():
        pytest.skip("debugging.md not yet generated")
    
    content = file_path.read_text(encoding='utf-8')
    
    # Check for logging configuration
    assert "logging" in content.lower() or "log" in content.lower(), \
        "Debugging guide must cover logging"
    
    # Check for debug mode
    assert "debug" in content.lower(), \
        "Debugging guide must cover debug mode"
    
    # Check for log interpretation
    assert "interpretation" in content.lower() or "interpret" in content.lower(), \
        "Debugging guide must cover log interpretation"


def test_faq_content():
    """
    Test that faq.md has expected content.
    """
    file_path = Path("docs/vi/troubleshooting/faq.md")
    
    if not file_path.exists():
        pytest.skip("faq.md not yet generated")
    
    content = file_path.read_text(encoding='utf-8')
    
    # Check for Q&A format
    assert "Q" in content or "?" in content, \
        "FAQ must have questions"
    
    assert "A" in content or ":" in content, \
        "FAQ must have answers"
    
    # Count questions (lines starting with Q or ###)
    question_pattern = r'^(Q\d+:|###\s+Q\d+:)'
    questions = re.findall(question_pattern, content, re.MULTILINE)
    
    # Should have multiple questions
    assert len(questions) >= 5, \
        f"FAQ should have at least 5 questions, found {len(questions)}"


def test_error_coverage_categories():
    """
    Test that common errors cover different categories.
    """
    file_path = Path("docs/vi/troubleshooting/common-errors.md")
    
    if not file_path.exists():
        pytest.skip("common-errors.md not yet generated")
    
    content = file_path.read_text(encoding='utf-8')
    
    # Check for different error categories
    expected_categories = [
        "ConfigurationError",
        "ValidationError",
        "PluginError",
        "AgentExecutionError",
        "ModelClientError",
        "WorkflowExecutionError"
    ]
    
    found_categories = []
    for category in expected_categories:
        if category in content:
            found_categories.append(category)
    
    # Should cover at least 4 different error categories
    assert len(found_categories) >= 4, \
        f"Should cover at least 4 error categories, found {len(found_categories)}: {found_categories}"


def test_solutions_have_code_examples():
    """
    Test that solutions include code examples.
    """
    file_path = Path("docs/vi/troubleshooting/common-errors.md")
    
    if not file_path.exists():
        pytest.skip("common-errors.md not yet generated")
    
    content = file_path.read_text(encoding='utf-8')
    
    # Count code blocks
    code_blocks = re.findall(r'```[\w]*\n', content)
    
    # Should have multiple code examples
    assert len(code_blocks) >= 10, \
        f"Solutions should include code examples, found {len(code_blocks)} code blocks"


if __name__ == "__main__":
    # Run tests
    pytest.main([__file__, "-v"])
