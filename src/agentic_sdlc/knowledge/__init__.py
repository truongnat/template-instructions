"""Knowledge and RAG Layer - Retrieval Augmented Generation for agent intelligence.

This package provides:
- VectorStore: Abstract and concrete vector database implementations
- KnowledgeBase: Document ingestion, embedding, and semantic retrieval
- ResearchAgent: Internet search + RAG orchestration
- Embeddings: Model wrappers for generating embeddings

Usage:
    from agentic_sdlc.knowledge import KnowledgeBase, ResearchAgent

    kb = KnowledgeBase(persist_dir=".agentic_sdlc/knowledge")
    kb.ingest("docs/architecture.md")
    results = kb.query("How does authentication work?")

    researcher = ResearchAgent(knowledge_base=kb)
    context = researcher.research("best practices for REST API security")
"""

from .knowledge_base import KnowledgeBase
from .vector_store import VectorStore, VectorSearchResult, ChromaVectorStore, InMemoryVectorStore
from .research_agent import ResearchAgent
from .embeddings import EmbeddingProvider, get_embedding_provider

__all__ = [
    "KnowledgeBase",
    "VectorStore",
    "VectorSearchResult",
    "ChromaVectorStore",
    "InMemoryVectorStore",
    "ResearchAgent",
    "EmbeddingProvider",
    "get_embedding_provider",
]
