"""
Property-based tests for example documentation completeness.

Feature: sdlc-kit-improvements, Property 8: Example Documentation Completeness
"""

import os
from pathlib import Path
from hypothesis import given, strategies as st, settings
import pytest


# Feature: sdlc-kit-improvements, Property 8: Example Documentation Completeness
@settings(max_examples=10)
@given(st.sampled_from([
    "examples/basic-workflow",
    "examples/multi-agent-workflow",
    "examples/integrations/github",
    "examples/integrations/slack"
]))
def test_example_documentation_completeness(example_dir):
    """
    Property: For any example directory in examples/, the directory should contain
    a README file that explains the example and includes instructions for running it.
    
    Validates: Requirements 9.4
    """
    # Get the full path to the example directory
    base_path = Path(__file__).parent.parent.parent
    example_path = base_path / example_dir
    
    # Property 1: Example directory must exist
    assert example_path.exists(), f"Example directory {example_dir} does not exist"
    assert example_path.is_dir(), f"{example_dir} is not a directory"
    
    # Property 2: README file must exist
    readme_path = example_path / "README.md"
    assert readme_path.exists(), f"README.md not found in {example_dir}"
    assert readme_path.is_file(), f"README.md in {example_dir} is not a file"
    
    # Property 3: README must not be empty
    readme_content = readme_path.read_text()
    assert len(readme_content.strip()) > 0, f"README.md in {example_dir} is empty"
    
    # Property 4: README must contain explanation (header or overview section)
    readme_lower = readme_content.lower()
    has_explanation = (
        "# " in readme_content or  # Has a header
        "overview" in readme_lower or
        "description" in readme_lower or
        "about" in readme_lower
    )
    assert has_explanation, f"README.md in {example_dir} does not contain an explanation section"
    
    # Property 5: README must contain running instructions
    has_instructions = (
        "running" in readme_lower or
        "run" in readme_lower or
        "execute" in readme_lower or
        "usage" in readme_lower or
        "how to" in readme_lower or
        "getting started" in readme_lower or
        "prerequisites" in readme_lower
    )
    assert has_instructions, f"README.md in {example_dir} does not contain running instructions"
    
    # Property 6: README should have reasonable length (at least 500 characters for meaningful content)
    assert len(readme_content) >= 500, (
        f"README.md in {example_dir} is too short ({len(readme_content)} chars). "
        "It should contain comprehensive documentation."
    )


def test_all_example_directories_have_readme():
    """
    Test that all example directories contain README files.
    This is a concrete test that complements the property test.
    """
    base_path = Path(__file__).parent.parent.parent
    
    # Only check the specific example directories we created for this spec
    required_examples = [
        "examples/basic-workflow",
        "examples/multi-agent-workflow",
        "examples/integrations/github",
        "examples/integrations/slack"
    ]
    
    # Check each example directory
    missing_readme = []
    for example_dir in required_examples:
        example_path = base_path / example_dir
        if not example_path.exists():
            continue  # Skip if directory doesn't exist
            
        readme_path = example_path / "README.md"
        if not readme_path.exists():
            missing_readme.append(example_dir)
    
    assert len(missing_readme) == 0, (
        f"The following example directories are missing README.md files: {missing_readme}"
    )


def test_readme_contains_required_sections():
    """
    Test that README files contain required sections for completeness.
    """
    base_path = Path(__file__).parent.parent.parent
    
    required_examples = [
        "examples/basic-workflow",
        "examples/multi-agent-workflow",
        "examples/integrations/github",
        "examples/integrations/slack"
    ]
    
    for example_dir in required_examples:
        example_path = base_path / example_dir
        readme_path = example_path / "README.md"
        
        if not readme_path.exists():
            continue  # Skip if README doesn't exist (will be caught by other test)
        
        readme_content = readme_path.read_text()
        readme_lower = readme_content.lower()
        
        # Check for essential sections
        sections_found = {
            "overview": "overview" in readme_lower or "description" in readme_lower,
            "prerequisites": "prerequisite" in readme_lower or "requirement" in readme_lower,
            "running": "running" in readme_lower or "usage" in readme_lower or "execute" in readme_lower,
            "example": "example" in readme_lower or "usage" in readme_lower
        }
        
        missing_sections = [section for section, found in sections_found.items() if not found]
        
        # At least 3 out of 4 essential sections should be present
        assert len(missing_sections) <= 1, (
            f"README.md in {example_dir} is missing essential sections: {missing_sections}"
        )


def test_readme_has_code_examples():
    """
    Test that README files contain code examples or command examples.
    """
    base_path = Path(__file__).parent.parent.parent
    
    required_examples = [
        "examples/basic-workflow",
        "examples/multi-agent-workflow",
        "examples/integrations/github",
        "examples/integrations/slack"
    ]
    
    for example_dir in required_examples:
        example_path = base_path / example_dir
        readme_path = example_path / "README.md"
        
        if not readme_path.exists():
            continue
        
        readme_content = readme_path.read_text()
        
        # Check for code blocks (markdown code fences)
        has_code_blocks = "```" in readme_content
        
        # Check for command examples
        has_commands = (
            "python" in readme_content.lower() or
            "pip" in readme_content.lower() or
            "bash" in readme_content.lower() or
            "$" in readme_content  # Shell prompt
        )
        
        assert has_code_blocks or has_commands, (
            f"README.md in {example_dir} should contain code examples or command examples"
        )


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
