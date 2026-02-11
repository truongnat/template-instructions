"""Data models for the documentation system.

This module defines the core data structures used throughout the documentation
generation system, including documents, code examples, diagrams, and API references.
"""

from dataclasses import dataclass, field
from typing import List, Dict, Optional, Any
from enum import Enum


class DocumentType(Enum):
    """Types of documentation."""
    GUIDE = "guide"
    USE_CASE = "use_case"
    API_REFERENCE = "api_reference"
    EXAMPLE = "example"
    DIAGRAM = "diagram"


class Category(Enum):
    """Documentation categories."""
    BASIC = "basic"
    INTERMEDIATE = "intermediate"
    ADVANCED = "advanced"


@dataclass
class CodeBlock:
    """A code block with syntax highlighting."""
    language: str
    code: str
    caption: Optional[str] = None
    line_numbers: bool = True


@dataclass
class Diagram:
    """A Mermaid diagram."""
    type: str  # flowchart, sequence, class, etc.
    mermaid_code: str
    caption: str


@dataclass
class Section:
    """A section within a document."""
    title: str
    content: str
    subsections: Optional[List['Section']] = None
    code_blocks: Optional[List[CodeBlock]] = None
    diagrams: Optional[List[Diagram]] = None


@dataclass
class Document:
    """Base document structure."""
    title: str
    type: DocumentType
    category: Category
    description: str
    sections: List[Section]
    metadata: Dict[str, Any]
    last_updated: str
    version: str


@dataclass
class GuideDocument(Document):
    """Guide documentation."""
    prerequisites: List[str] = field(default_factory=list)
    learning_objectives: List[str] = field(default_factory=list)
    related_guides: List[str] = field(default_factory=list)


@dataclass
class UseCaseDocument(Document):
    """Use case documentation."""
    scenario: str = ""
    problem: str = ""
    solution: str = ""
    architecture: Optional[Diagram] = None
    implementation: List[CodeBlock] = field(default_factory=list)
    results: str = ""
    lessons_learned: List[str] = field(default_factory=list)


@dataclass
class Parameter:
    """Method parameter."""
    name: str
    type: str
    description: str
    default: Optional[Any] = None
    required: bool = True


@dataclass
class ReturnValue:
    """Method return value."""
    type: str
    description: str


@dataclass
class MethodReference:
    """Method API reference."""
    name: str
    signature: str
    description: str
    parameters: List[Parameter]
    returns: ReturnValue
    raises: List[str] = field(default_factory=list)
    examples: List[CodeBlock] = field(default_factory=list)


@dataclass
class PropertyReference:
    """Property API reference."""
    name: str
    type: str
    description: str
    readonly: bool = False


@dataclass
class ClassReference:
    """Class API reference."""
    name: str
    description: str
    constructor: MethodReference
    methods: List[MethodReference]
    properties: List[PropertyReference]
    examples: List[CodeBlock]


@dataclass
class FunctionReference:
    """Function API reference."""
    name: str
    signature: str
    description: str
    parameters: List[Parameter]
    returns: ReturnValue
    raises: List[str] = field(default_factory=list)
    examples: List[CodeBlock] = field(default_factory=list)


@dataclass
class ConstantReference:
    """Constant API reference."""
    name: str
    type: str
    value: str
    description: str


@dataclass
class APIReferenceDocument(Document):
    """API reference documentation."""
    module_path: str = ""
    classes: List[ClassReference] = field(default_factory=list)
    functions: List[FunctionReference] = field(default_factory=list)
    constants: List[ConstantReference] = field(default_factory=list)


@dataclass
class CodeExample:
    """Runnable code example."""
    name: str
    description: str
    category: Category
    code: str
    dependencies: List[str]
    setup_instructions: str
    expected_output: str
    notes: List[str] = field(default_factory=list)
