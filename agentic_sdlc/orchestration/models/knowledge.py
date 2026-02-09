"""
Knowledge Base Data Models

This module defines the data structures for the Knowledge Base system,
including knowledge items, sources, versions, and search results.

Requirements: 6.2, 6.4
"""

from datetime import datetime
from enum import Enum
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field
from uuid import uuid4


class KnowledgeType(Enum):
    """Types of knowledge items"""
    DOCUMENT = "document"
    CODE_SNIPPET = "code_snippet"
    BEST_PRACTICE = "best_practice"
    LESSON_LEARNED = "lesson_learned"
    ARCHITECTURAL_PATTERN = "architectural_pattern"
    ERROR_SOLUTION = "error_solution"
    EXTERNAL_REFERENCE = "external_reference"


class SourceType(Enum):
    """Types of knowledge sources"""
    INTERNAL_REPO = "internal_repo"
    DOCUMENTATION = "documentation"
    USER_INPUT = "user_input"
    EXTERNAL_WEB = "external_web"
    AGENT_GENERATED = "agent_generated"


class ValidationStatus(Enum):
    """Validation status of knowledge items"""
    PENDING = "pending"
    VALIDATED = "validated"
    DEPRECATED = "deprecated"
    REJECTED = "rejected"


@dataclass
class KnowledgeSource:
    """Source of a knowledge item"""
    id: str = field(default_factory=lambda: str(uuid4()))
    name: str = ""
    type: SourceType = SourceType.INTERNAL_REPO
    url: Optional[str] = None
    author: Optional[str] = None
    created_at: datetime = field(default_factory=datetime.now)
    reliability_score: float = 1.0


@dataclass
class KnowledgeVersion:
    """Version information for a knowledge item"""
    version_id: str = field(default_factory=lambda: str(uuid4()))
    item_id: str = ""
    content: Any = None
    updated_by: str = ""
    updated_at: datetime = field(default_factory=datetime.now)
    change_description: str = ""
    previous_version_id: Optional[str] = None


@dataclass
class KnowledgeItem:
    """Individual item in the knowledge base"""
    id: str = field(default_factory=lambda: str(uuid4()))
    title: str = ""
    content: Any = None
    type: KnowledgeType = KnowledgeType.DOCUMENT
    tags: List[str] = field(default_factory=list)
    source: Optional[KnowledgeSource] = None
    versions: List[KnowledgeVersion] = field(default_factory=list)
    status: ValidationStatus = ValidationStatus.PENDING
    confidence_score: float = 1.0
    access_count: int = 0
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def add_version(self, content: Any, updated_by: str, description: str):
        """Add a new version of the content"""
        # Save current content as previous version if it exists
        previous_id = self.versions[-1].version_id if self.versions else None
        
        new_version = KnowledgeVersion(
            item_id=self.id,
            content=content,
            updated_by=updated_by,
            change_description=description,
            previous_version_id=previous_id
        )
        
        self.versions.append(new_version)
        self.content = content
        self.updated_at = datetime.now()


@dataclass
class SearchResult:
    """Result from knowledge base search"""
    item: KnowledgeItem
    relevance_score: float
    snippet: str = ""
    rank: int = 0
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            "id": self.item.id,
            "title": self.item.title,
            "type": self.item.type.value,
            "relevance": self.relevance_score,
            "snippet": self.snippet,
            "source": self.item.source.name if self.item.source else "Unknown",
            "url": self.item.source.url if self.item.source else None
        }


@dataclass
class KnowledgeQuery:
    """Query parameters for searching the knowledge base"""
    query_text: str
    filters: Dict[str, Any] = field(default_factory=dict)
    types: List[KnowledgeType] = field(default_factory=list)
    min_confidence: float = 0.0
    limit: int = 10
    include_deprecated: bool = False
