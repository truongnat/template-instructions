"""Knowledge Base - Document ingestion, embedding, and semantic retrieval.

Provides a high-level interface for building and querying a knowledge base
backed by a vector store. Supports ingestion of markdown, text, and code files.
"""

import hashlib
import re
from pathlib import Path
from typing import Any, Dict, List, Optional

from ..core.logging import get_logger
from .embeddings import EmbeddingProvider, get_embedding_provider
from .vector_store import ChromaVectorStore, InMemoryVectorStore, VectorSearchResult, VectorStore

logger = get_logger(__name__)

# Default chunk size and overlap in characters
DEFAULT_CHUNK_SIZE = 1500
DEFAULT_CHUNK_OVERLAP = 200

# Supported file extensions for ingestion
SUPPORTED_EXTENSIONS = {
    ".md", ".txt", ".py", ".js", ".ts", ".jsx", ".tsx",
    ".yaml", ".yml", ".json", ".toml", ".cfg", ".ini",
    ".html", ".css", ".sql", ".sh", ".bash", ".zsh",
    ".go", ".rs", ".java", ".kt", ".swift", ".dart",
    ".c", ".cpp", ".h", ".hpp", ".rb", ".php",
}


class KnowledgeBase:
    """High-level knowledge base with ingestion and semantic retrieval.

    Manages document chunking, embedding, storage, and retrieval
    using a vector store backend.

    Example:
        >>> kb = KnowledgeBase(persist_dir=Path(".agentic_sdlc/knowledge"))
        >>> kb.ingest_file(Path("docs/architecture.md"))
        >>> results = kb.query("How does authentication work?", top_k=5)
        >>> for r in results:
        ...     print(r.content[:100])
    """

    def __init__(
        self,
        persist_dir: Optional[Path] = None,
        vector_store: Optional[VectorStore] = None,
        embedding_provider: Optional[EmbeddingProvider] = None,
        chunk_size: int = DEFAULT_CHUNK_SIZE,
        chunk_overlap: int = DEFAULT_CHUNK_OVERLAP,
    ):
        """Initialize the knowledge base.

        Args:
            persist_dir: Directory for persistent storage. If None, uses in-memory.
            vector_store: Optional pre-configured vector store.
            embedding_provider: Optional embedding provider override.
            chunk_size: Target characters per chunk.
            chunk_overlap: Characters of overlap between chunks.
        """
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap

        # Set up embedding provider
        self._embeddings = embedding_provider or get_embedding_provider()

        # Set up vector store
        if vector_store:
            self._store = vector_store
        elif persist_dir:
            vectors_dir = persist_dir / "vectors"
            self._store = ChromaVectorStore(
                persist_dir=vectors_dir,
                collection_name="knowledge",
            )
        else:
            self._store = InMemoryVectorStore()

        self._persist_dir = persist_dir
        logger.info(f"KnowledgeBase initialized (store={type(self._store).__name__})")

    def ingest_file(self, path: Path, metadata: Optional[Dict[str, Any]] = None) -> int:
        """Ingest a file into the knowledge base.

        Reads the file, chunks it, generates embeddings, and stores
        in the vector store.

        Args:
            path: Path to file to ingest.
            metadata: Optional additional metadata.

        Returns:
            Number of chunks added.
        """
        if not path.exists():
            logger.warning(f"File not found: {path}")
            return 0

        if path.suffix.lower() not in SUPPORTED_EXTENSIONS:
            logger.warning(f"Unsupported file type: {path.suffix}")
            return 0

        try:
            content = path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            logger.warning(f"Cannot read file as text: {path}")
            return 0

        if not content.strip():
            return 0

        return self.ingest_text(
            content,
            source=str(path),
            metadata=metadata,
        )

    def ingest_text(
        self,
        text: str,
        source: str = "unknown",
        metadata: Optional[Dict[str, Any]] = None,
    ) -> int:
        """Ingest raw text into the knowledge base.

        Args:
            text: Text content to ingest.
            source: Source identifier (filename, URL, etc.).
            metadata: Optional additional metadata.

        Returns:
            Number of chunks added.
        """
        if not text.strip():
            return 0

        # Chunk the text
        chunks = self._chunk_text(text)
        if not chunks:
            return 0

        # Generate IDs, embeddings, and metadata
        ids = []
        documents = []
        metadatas = []
        base_meta = metadata or {}
        base_meta["source"] = source

        for i, chunk in enumerate(chunks):
            # Create deterministic ID from content hash
            chunk_hash = hashlib.md5(chunk.encode()).hexdigest()[:12]
            doc_id = f"{source}::chunk_{i}::{chunk_hash}"

            ids.append(doc_id)
            documents.append(chunk)
            metadatas.append({
                **base_meta,
                "chunk_index": i,
                "total_chunks": len(chunks),
            })

        # Generate embeddings
        embeddings = self._embeddings.embed_batch(documents)

        # Store in vector store
        self._store.add(
            ids=ids,
            embeddings=embeddings,
            documents=documents,
            metadatas=metadatas,
        )

        logger.info(f"Ingested {len(chunks)} chunks from {source}")
        return len(chunks)

    def ingest_directory(
        self,
        directory: Path,
        recursive: bool = True,
        extensions: Optional[set] = None,
    ) -> int:
        """Ingest all supported files from a directory.

        Args:
            directory: Directory to scan.
            recursive: Whether to scan subdirectories.
            extensions: Optional set of file extensions to include.

        Returns:
            Total number of chunks added.
        """
        if not directory.exists():
            logger.warning(f"Directory not found: {directory}")
            return 0

        allowed_ext = extensions or SUPPORTED_EXTENSIONS
        total = 0
        pattern = "**/*" if recursive else "*"

        for path in sorted(directory.glob(pattern)):
            if path.is_file() and path.suffix.lower() in allowed_ext:
                total += self.ingest_file(path)

        logger.info(f"Ingested {total} total chunks from {directory}")
        return total

    def query(
        self,
        query: str,
        top_k: int = 5,
        filter_metadata: Optional[Dict[str, Any]] = None,
    ) -> List[VectorSearchResult]:
        """Query the knowledge base for relevant documents.

        Args:
            query: Natural language query.
            top_k: Number of results to return.
            filter_metadata: Optional metadata filters.

        Returns:
            List of VectorSearchResult ordered by relevance.
        """
        if not query.strip():
            return []

        # Generate query embedding
        query_embedding = self._embeddings.embed_text(query)

        # Search vector store
        results = self._store.query(
            query_embedding=query_embedding,
            top_k=top_k,
            filter_metadata=filter_metadata,
        )

        return results

    def query_with_context(
        self,
        query: str,
        top_k: int = 5,
        max_tokens: int = 4000,
    ) -> str:
        """Query and return formatted context string.

        Convenience method that queries and formats results into a
        single context string suitable for prompt injection.

        Args:
            query: Natural language query.
            top_k: Number of results.
            max_tokens: Approximate token budget.

        Returns:
            Formatted context string.
        """
        results = self.query(query, top_k=top_k)
        if not results:
            return ""

        parts = []
        total_chars = 0
        char_budget = max_tokens * 4  # rough tokens-to-chars

        for r in results:
            if total_chars + len(r.content) > char_budget:
                remaining = char_budget - total_chars
                if remaining > 100:
                    parts.append(f"[Source: {r.metadata.get('source', 'unknown')}]\n{r.content[:remaining]}...")
                break
            source = r.metadata.get("source", "unknown")
            parts.append(f"[Source: {source} | Relevance: {r.score:.2f}]\n{r.content}")
            total_chars += len(r.content)

        return "\n\n---\n\n".join(parts)

    @property
    def document_count(self) -> int:
        """Total number of document chunks in the knowledge base."""
        return self._store.count()

    def clear(self) -> None:
        """Clear all documents from the knowledge base."""
        self._store.clear()
        logger.info("Knowledge base cleared")

    def _chunk_text(self, text: str) -> List[str]:
        """Split text into overlapping chunks.

        Uses paragraph boundaries when possible, falling back to
        sentence boundaries, then character-based splitting.

        Args:
            text: Text to chunk.

        Returns:
            List of text chunks.
        """
        if len(text) <= self.chunk_size:
            return [text.strip()] if text.strip() else []

        # Split by paragraphs first
        paragraphs = re.split(r"\n\s*\n", text)
        chunks = []
        current_chunk = ""

        for para in paragraphs:
            para = para.strip()
            if not para:
                continue

            # If adding this paragraph exceeds chunk size
            if len(current_chunk) + len(para) + 2 > self.chunk_size:
                if current_chunk:
                    chunks.append(current_chunk.strip())
                    # Keep overlap from end of last chunk
                    overlap_start = max(0, len(current_chunk) - self.chunk_overlap)
                    current_chunk = current_chunk[overlap_start:] + "\n\n" + para
                else:
                    # Single paragraph too large — split by sentences
                    if len(para) > self.chunk_size:
                        sub_chunks = self._split_large_paragraph(para)
                        chunks.extend(sub_chunks[:-1])
                        current_chunk = sub_chunks[-1] if sub_chunks else ""
                    else:
                        current_chunk = para
            else:
                if current_chunk:
                    current_chunk += "\n\n" + para
                else:
                    current_chunk = para

        if current_chunk.strip():
            chunks.append(current_chunk.strip())

        return chunks

    def _split_large_paragraph(self, text: str) -> List[str]:
        """Split a large paragraph into chunks by sentences.

        Args:
            text: Large text block.

        Returns:
            List of chunks.
        """
        # Simple sentence splitting
        sentences = re.split(r"(?<=[.!?])\s+", text)
        chunks = []
        current = ""

        for sentence in sentences:
            if len(current) + len(sentence) + 1 > self.chunk_size:
                if current:
                    chunks.append(current.strip())
                current = sentence
            else:
                current = f"{current} {sentence}" if current else sentence

        if current.strip():
            chunks.append(current.strip())

        return chunks
