"""Documentation generation system for Agentic SDLC.

This module provides tools for generating comprehensive Vietnamese documentation
including guides, use cases, API references, and code examples.
"""

from .models import (
    DocumentType,
    Category,
    CodeBlock,
    Diagram,
    Section,
    Document,
    GuideDocument,
    UseCaseDocument,
    APIReferenceDocument,
    Parameter,
    ReturnValue,
    MethodReference,
    PropertyReference,
    ClassReference,
    FunctionReference,
    ConstantReference,
    CodeExample,
)
from .translation import TranslationManager
from .code_examples import CodeExampleManager, CodeValidator, ValidationResult
from .diagrams import (
    DiagramGenerator,
    Component,
    Connection,
    WorkflowStep,
    Agent,
    Interaction,
    DataFlowNode,
    DataFlow,
)
from .api_reference import APIReferenceGenerator
from .use_cases import UseCaseBuilder, Scenario, Implementation, Results

__all__ = [
    "DocumentType",
    "Category",
    "CodeBlock",
    "Diagram",
    "Section",
    "Document",
    "GuideDocument",
    "UseCaseDocument",
    "APIReferenceDocument",
    "Parameter",
    "ReturnValue",
    "MethodReference",
    "PropertyReference",
    "ClassReference",
    "FunctionReference",
    "ConstantReference",
    "CodeExample",
    "TranslationManager",
    "CodeExampleManager",
    "CodeValidator",
    "ValidationResult",
    "DiagramGenerator",
    "Component",
    "Connection",
    "WorkflowStep",
    "Agent",
    "Interaction",
    "DataFlowNode",
    "DataFlow",
    "APIReferenceGenerator",
    "UseCaseBuilder",
    "Scenario",
    "Implementation",
    "Results",
]
