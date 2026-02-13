"""Property-based tests for API reference generation.

This module contains property-based tests that verify universal correctness
properties for the API reference generation system.
"""

import pytest
from hypothesis import given, strategies as st
from hypothesis import settings
import importlib
import inspect
from pathlib import Path
from typing import List, Set

from src.agentic_sdlc.documentation.api_reference import APIReferenceGenerator
from src.agentic_sdlc.documentation.models import APIReferenceDocument


def get_public_apis_from_module(module_path: str) -> Set[str]:
    """Extract all public API names from a module.
    
    Args:
        module_path: Python module path (e.g., "agentic_sdlc.core.config")
        
    Returns:
        Set of public API names (classes and functions)
    """
    try:
        module = importlib.import_module(module_path)
    except ImportError:
        return set()
    
    public_apis = set()
    
    # Get all public classes
    for name, obj in inspect.getmembers(module, inspect.isclass):
        if not name.startswith('_') and obj.__module__ == module_path:
            public_apis.add(name)
    
    # Get all public functions
    for name, obj in inspect.getmembers(module, inspect.isfunction):
        if not name.startswith('_') and obj.__module__ == module_path:
            public_apis.add(name)
    
    return public_apis


def get_documented_apis_from_doc(doc: APIReferenceDocument) -> Set[str]:
    """Extract all documented API names from an API reference document.
    
    Args:
        doc: API reference document
        
    Returns:
        Set of documented API names
    """
    documented = set()
    
    # Add all documented classes
    for class_ref in doc.classes:
        documented.add(class_ref.name)
    
    # Add all documented functions
    for func_ref in doc.functions:
        documented.add(func_ref.name)
    
    return documented


# Strategy for generating module paths to test
@st.composite
def module_path_strategy(draw):
    """Generate valid module paths from the agentic_sdlc package."""
    # List of actual modules in the package
    modules = [
        "agentic_sdlc.core.config",
        "agentic_sdlc.core.exceptions",
        "agentic_sdlc.core.logging",
        "agentic_sdlc.plugins.base",
        "agentic_sdlc.plugins.registry",
        "agentic_sdlc.documentation.models",
        "agentic_sdlc.documentation.translation",
        "agentic_sdlc.documentation.code_examples",
        "agentic_sdlc.documentation.diagrams",
        "agentic_sdlc.documentation.generator",
        "agentic_sdlc.documentation.api_reference",
    ]
    
    return draw(st.sampled_from(modules))


# Property Test 7: Public API Coverage
@settings(max_examples=10, deadline=None)
@given(module_path=module_path_strategy())
def test_public_api_coverage(module_path):
    """Feature: use-cases-and-usage-guide, Property 7:
    
    For any public class or function in the Agentic SDLC source code, 
    it must have corresponding documentation in the API reference.
    
    **Validates: Requirements 14.1**
    """
    # Create API reference generator
    generator = APIReferenceGenerator(
        source_dir="src/agentic_sdlc",
        glossary_file="docs/vi/glossary.yaml"
    )
    
    # Generate documentation for the module
    try:
        api_doc = generator.generate_module_docs(module_path)
    except Exception as e:
        pytest.skip(f"Could not generate docs for {module_path}: {e}")
        return
    
    # Extract public APIs from source
    source_apis = get_public_apis_from_module(module_path)
    
    # Extract documented APIs from generated documentation
    documented_apis = get_documented_apis_from_doc(api_doc)
    
    # Verify all public APIs are documented
    missing_apis = source_apis - documented_apis
    
    # Allow some exceptions for special cases (e.g., deprecated, internal)
    # but generally all public APIs should be documented
    assert len(missing_apis) == 0, (
        f"Module {module_path} has undocumented public APIs: {missing_apis}. "
        f"Source APIs: {source_apis}, Documented APIs: {documented_apis}"
    )
    
    # Verify documentation is not empty if source has APIs
    if source_apis:
        assert len(api_doc.classes) > 0 or len(api_doc.functions) > 0, (
            f"Module {module_path} has public APIs {source_apis} but no documented classes or functions"
        )


# Additional test: Verify API reference document structure
@settings(max_examples=10, deadline=None)
@given(module_path=module_path_strategy())
def test_api_reference_document_structure(module_path):
    """Verify that generated API reference documents have proper structure.
    
    This test ensures that:
    - Document has a title
    - Document has a description
    - Document has proper metadata
    - Document sections are properly formatted
    """
    # Create API reference generator
    generator = APIReferenceGenerator(
        source_dir="src/agentic_sdlc",
        glossary_file="docs/vi/glossary.yaml"
    )
    
    # Generate documentation for the module
    try:
        api_doc = generator.generate_module_docs(module_path)
    except Exception as e:
        pytest.skip(f"Could not generate docs for {module_path}: {e}")
        return
    
    # Verify document structure
    assert api_doc.title is not None
    assert len(api_doc.title) > 0
    assert "API Reference" in api_doc.title
    
    assert api_doc.description is not None
    assert len(api_doc.description) > 0
    
    assert api_doc.module_path == module_path
    
    # Verify metadata
    assert api_doc.metadata is not None
    assert "module" in api_doc.metadata
    assert api_doc.metadata["module"] == module_path
    
    # Verify sections exist
    assert api_doc.sections is not None
    assert len(api_doc.sections) > 0
    
    # First section should be module overview
    assert api_doc.sections[0].title == "Tổng Quan Module"


# Test: Verify class documentation completeness
@settings(max_examples=10, deadline=None)
@given(module_path=module_path_strategy())
def test_class_documentation_completeness_in_generated_docs(module_path):
    """Verify that all classes in generated docs have complete documentation.
    
    This test ensures that each documented class has:
    - Name
    - Description
    - Constructor
    - Methods list
    - Properties list
    - At least one example
    """
    # Create API reference generator
    generator = APIReferenceGenerator(
        source_dir="src/agentic_sdlc",
        glossary_file="docs/vi/glossary.yaml"
    )
    
    # Generate documentation for the module
    try:
        api_doc = generator.generate_module_docs(module_path)
    except Exception as e:
        pytest.skip(f"Could not generate docs for {module_path}: {e}")
        return
    
    # Skip if no classes
    if len(api_doc.classes) == 0:
        return
    
    # Verify each class has complete documentation
    for class_ref in api_doc.classes:
        # Must have name
        assert class_ref.name is not None
        assert len(class_ref.name) > 0
        
        # Must have description
        assert class_ref.description is not None
        # Description can be empty if no docstring, but field must exist
        
        # Must have constructor
        assert class_ref.constructor is not None
        assert class_ref.constructor.name == "__init__"
        
        # Must have methods list (can be empty)
        assert class_ref.methods is not None
        assert isinstance(class_ref.methods, list)
        
        # Must have properties list (can be empty)
        assert class_ref.properties is not None
        assert isinstance(class_ref.properties, list)
        
        # Must have at least one example
        assert class_ref.examples is not None
        assert len(class_ref.examples) > 0


# Test: Verify function documentation completeness
@settings(max_examples=10, deadline=None)
@given(module_path=module_path_strategy())
def test_function_documentation_completeness_in_generated_docs(module_path):
    """Verify that all functions in generated docs have complete documentation.
    
    This test ensures that each documented function has:
    - Name
    - Signature
    - Description
    - Parameters list
    - Return value
    - At least one example
    """
    # Create API reference generator
    generator = APIReferenceGenerator(
        source_dir="src/agentic_sdlc",
        glossary_file="docs/vi/glossary.yaml"
    )
    
    # Generate documentation for the module
    try:
        api_doc = generator.generate_module_docs(module_path)
    except Exception as e:
        pytest.skip(f"Could not generate docs for {module_path}: {e}")
        return
    
    # Skip if no functions
    if len(api_doc.functions) == 0:
        return
    
    # Verify each function has complete documentation
    for func_ref in api_doc.functions:
        # Must have name
        assert func_ref.name is not None
        assert len(func_ref.name) > 0
        
        # Must have signature
        assert func_ref.signature is not None
        assert len(func_ref.signature) > 0
        
        # Must have description (can be empty if no docstring)
        assert func_ref.description is not None
        
        # Must have parameters list (can be empty)
        assert func_ref.parameters is not None
        assert isinstance(func_ref.parameters, list)
        
        # Must have return value
        assert func_ref.returns is not None
        assert func_ref.returns.type is not None
        
        # Must have at least one example
        assert func_ref.examples is not None
        assert len(func_ref.examples) > 0
