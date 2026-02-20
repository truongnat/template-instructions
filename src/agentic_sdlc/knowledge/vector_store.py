"""Vector Store - Abstract and concrete vector database implementations.

Provides a unified interface over vector databases (ChromaDB, LanceDB)
for storing and querying document embeddings.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional

from ..core.logging import get_logger

logger = get_logger(__name__)


@dataclass
class VectorSearchResult:
    """Result from a vector similarity search.

    Attributes:
        id: Document chunk identifier.
        content: Text content of the chunk.
        score: Similarity score (higher = more similar).
        metadata: Associated metadata (source file, chunk index, etc.).
    """

    id: str
    content: str
    score: float
    metadata: Dict[str, Any] = field(default_factory=dict)


class VectorStore(ABC):
    """Abstract vector store interface.

    Implementations must provide add, query, and delete operations
    over document embeddings.
    """

    @abstractmethod
    def add(
        self,
        ids: List[str],
        embeddings: List[List[float]],
        documents: List[str],
        metadatas: Optional[List[Dict[str, Any]]] = None,
    ) -> None:
        """Add documents with their embeddings to the store.

        Args:
            ids: Unique identifiers for each document.
            embeddings: Embedding vectors.
            documents: Original text content.
            metadatas: Optional metadata dicts per document.
        """

    @abstractmethod
    def query(
        self,
        query_embedding: List[float],
        top_k: int = 5,
        filter_metadata: Optional[Dict[str, Any]] = None,
    ) -> List[VectorSearchResult]:
        """Query the store for similar documents.

        Args:
            query_embedding: Query vector.
            top_k: Number of results to return.
            filter_metadata: Optional metadata filters.

        Returns:
            List of VectorSearchResult ordered by similarity.
        """

    @abstractmethod
    def delete(self, ids: List[str]) -> None:
        """Delete documents by their IDs.

        Args:
            ids: List of document IDs to delete.
        """

    @abstractmethod
    def count(self) -> int:
        """Return the total number of documents in the store."""

    @abstractmethod
    def clear(self) -> None:
        """Remove all documents from the store."""


class ChromaVectorStore(VectorStore):
    """Vector store backed by ChromaDB (embedded, zero-config).

    ChromaDB provides fast local vector search with persistence,
    metadata filtering, and automatic index management.
    """

    def __init__(
        self,
        persist_dir: Optional[Path] = None,
        collection_name: str = "agentic_sdlc",
    ):
        """Initialize ChromaDB vector store.

        Args:
            persist_dir: Directory for persistent storage.
                        If None, uses in-memory storage.
            collection_name: Name of the ChromaDB collection.
        """
        self._persist_dir = persist_dir
        self._collection_name = collection_name
        self._client = None
        self._collection = None

    def _ensure_initialized(self):
        """Lazy-initialize ChromaDB client and collection."""
        if self._collection is not None:
            return

        try:
            import chromadb

            if self._persist_dir:
                self._persist_dir.mkdir(parents=True, exist_ok=True)
                self._client = chromadb.PersistentClient(
                    path=str(self._persist_dir)
                )
            else:
                self._client = chromadb.Client()

            self._collection = self._client.get_or_create_collection(
                name=self._collection_name,
                metadata={"hnsw:space": "cosine"},
            )
            logger.info(
                f"ChromaDB initialized: collection='{self._collection_name}', "
                f"docs={self._collection.count()}"
            )
        except ImportError:
            raise ImportError(
                "chromadb is required for vector storage. "
                "Install with: pip install chromadb"
            )

    def add(
        self,
        ids: List[str],
        embeddings: List[List[float]],
        documents: List[str],
        metadatas: Optional[List[Dict[str, Any]]] = None,
    ) -> None:
        """Add documents with embeddings to ChromaDB."""
        self._ensure_initialized()

        # ChromaDB metadata values must be str, int, float, or bool
        clean_metadatas = None
        if metadatas:
            clean_metadatas = []
            for meta in metadatas:
                clean = {}
                for k, v in meta.items():
                    if isinstance(v, (str, int, float, bool)):
                        clean[k] = v
                    else:
                        clean[k] = str(v)
                clean_metadatas.append(clean)

        self._collection.upsert(
            ids=ids,
            embeddings=embeddings,
            documents=documents,
            metadatas=clean_metadatas,
        )
        logger.debug(f"Added {len(ids)} documents to ChromaDB")

    def query(
        self,
        query_embedding: List[float],
        top_k: int = 5,
        filter_metadata: Optional[Dict[str, Any]] = None,
    ) -> List[VectorSearchResult]:
        """Query ChromaDB for similar documents."""
        self._ensure_initialized()

        kwargs = {
            "query_embeddings": [query_embedding],
            "n_results": min(top_k, self._collection.count() or 1),
            "include": ["documents", "distances", "metadatas"],
        }
        if filter_metadata:
            kwargs["where"] = filter_metadata

        results = self._collection.query(**kwargs)

        search_results = []
        if results and results["ids"] and results["ids"][0]:
            for i, doc_id in enumerate(results["ids"][0]):
                # ChromaDB returns distances; convert to similarity
                distance = results["distances"][0][i] if results["distances"] else 0
                score = 1.0 - distance  # cosine distance → similarity

                search_results.append(
                    VectorSearchResult(
                        id=doc_id,
                        content=results["documents"][0][i] if results["documents"] else "",
                        score=score,
                        metadata=results["metadatas"][0][i] if results["metadatas"] else {},
                    )
                )

        return search_results

    def delete(self, ids: List[str]) -> None:
        """Delete documents from ChromaDB."""
        self._ensure_initialized()
        self._collection.delete(ids=ids)

    def count(self) -> int:
        """Return document count."""
        self._ensure_initialized()
        return self._collection.count()

    def clear(self) -> None:
        """Clear all documents."""
        self._ensure_initialized()
        # Re-create the collection
        self._client.delete_collection(self._collection_name)
        self._collection = self._client.get_or_create_collection(
            name=self._collection_name,
            metadata={"hnsw:space": "cosine"},
        )


class InMemoryVectorStore(VectorStore):
    """Simple in-memory vector store for testing and small datasets.

    Uses brute-force cosine similarity search. No external dependencies.
    """

    def __init__(self):
        """Initialize in-memory store."""
        self._documents: Dict[str, Dict[str, Any]] = {}

    def add(
        self,
        ids: List[str],
        embeddings: List[List[float]],
        documents: List[str],
        metadatas: Optional[List[Dict[str, Any]]] = None,
    ) -> None:
        """Add documents to in-memory store."""
        for i, doc_id in enumerate(ids):
            self._documents[doc_id] = {
                "embedding": embeddings[i],
                "content": documents[i],
                "metadata": metadatas[i] if metadatas else {},
            }

    def query(
        self,
        query_embedding: List[float],
        top_k: int = 5,
        filter_metadata: Optional[Dict[str, Any]] = None,
    ) -> List[VectorSearchResult]:
        """Query using brute-force cosine similarity."""
        import math

        def cosine_sim(a: List[float], b: List[float]) -> float:
            dot = sum(x * y for x, y in zip(a, b))
            norm_a = math.sqrt(sum(x * x for x in a))
            norm_b = math.sqrt(sum(x * x for x in b))
            if norm_a == 0 or norm_b == 0:
                return 0.0
            return dot / (norm_a * norm_b)

        scored = []
        for doc_id, doc in self._documents.items():
            # Apply metadata filter
            if filter_metadata:
                match = all(
                    doc.get("metadata", {}).get(k) == v
                    for k, v in filter_metadata.items()
                )
                if not match:
                    continue

            score = cosine_sim(query_embedding, doc["embedding"])
            scored.append(
                VectorSearchResult(
                    id=doc_id,
                    content=doc["content"],
                    score=score,
                    metadata=doc.get("metadata", {}),
                )
            )

        scored.sort(key=lambda x: x.score, reverse=True)
        return scored[:top_k]

    def delete(self, ids: List[str]) -> None:
        """Delete documents by ID."""
        for doc_id in ids:
            self._documents.pop(doc_id, None)

    def count(self) -> int:
        """Return document count."""
        return len(self._documents)

    def clear(self) -> None:
        """Clear all documents."""
        self._documents.clear()
