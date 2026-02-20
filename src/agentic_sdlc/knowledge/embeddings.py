"""Embedding providers for vector representations.

Supports multiple embedding backends:
- SentenceTransformers (local, default)
- OpenAI embeddings API (cloud)
- HuggingFace models (local)
"""

from abc import ABC, abstractmethod
from typing import List, Optional

from ..core.logging import get_logger

logger = get_logger(__name__)


class EmbeddingProvider(ABC):
    """Abstract base class for embedding providers."""

    @abstractmethod
    def embed_text(self, text: str) -> List[float]:
        """Generate embedding for a single text.

        Args:
            text: Input text string.

        Returns:
            List of floats representing the embedding vector.
        """

    @abstractmethod
    def embed_batch(self, texts: List[str]) -> List[List[float]]:
        """Generate embeddings for a batch of texts.

        Args:
            texts: List of input texts.

        Returns:
            List of embedding vectors.
        """

    @property
    @abstractmethod
    def dimension(self) -> int:
        """Embedding vector dimension."""


class SentenceTransformerProvider(EmbeddingProvider):
    """Embedding provider using sentence-transformers (local).

    Uses the 'all-MiniLM-L6-v2' model by default — fast, 384-dim,
    good quality for semantic search.
    """

    def __init__(self, model_name: str = "all-MiniLM-L6-v2"):
        """Initialize with a sentence-transformers model.

        Args:
            model_name: HuggingFace model ID.
        """
        self._model_name = model_name
        self._model = None
        self._dim = 384  # default for MiniLM

    def _load_model(self):
        """Lazy-load the model."""
        if self._model is None:
            try:
                from sentence_transformers import SentenceTransformer

                self._model = SentenceTransformer(self._model_name)
                self._dim = self._model.get_sentence_embedding_dimension()
                logger.info(
                    f"Loaded embedding model: {self._model_name} (dim={self._dim})"
                )
            except ImportError:
                raise ImportError(
                    "sentence-transformers is required for local embeddings. "
                    "Install with: pip install sentence-transformers"
                )

    def embed_text(self, text: str) -> List[float]:
        """Generate embedding for a single text."""
        self._load_model()
        embedding = self._model.encode(text, convert_to_numpy=True)
        return embedding.tolist()

    def embed_batch(self, texts: List[str]) -> List[List[float]]:
        """Generate embeddings for a batch of texts."""
        self._load_model()
        embeddings = self._model.encode(texts, convert_to_numpy=True, batch_size=32)
        return embeddings.tolist()

    @property
    def dimension(self) -> int:
        """Embedding vector dimension."""
        return self._dim


class OpenAIEmbeddingProvider(EmbeddingProvider):
    """Embedding provider using OpenAI's API.

    Uses 'text-embedding-3-small' by default (1536-dim).
    """

    def __init__(
        self,
        model: str = "text-embedding-3-small",
        api_key: Optional[str] = None,
    ):
        """Initialize with OpenAI API.

        Args:
            model: OpenAI embedding model name.
            api_key: Optional API key (falls back to env var).
        """
        self._model = model
        self._api_key = api_key
        self._client = None
        self._dim = 1536  # default for text-embedding-3-small

    def _get_client(self):
        """Lazy-load OpenAI client."""
        if self._client is None:
            try:
                from openai import OpenAI

                kwargs = {}
                if self._api_key:
                    kwargs["api_key"] = self._api_key
                self._client = OpenAI(**kwargs)
            except ImportError:
                raise ImportError(
                    "openai is required for OpenAI embeddings. "
                    "Install with: pip install openai"
                )
        return self._client

    def embed_text(self, text: str) -> List[float]:
        """Generate embedding for a single text."""
        client = self._get_client()
        response = client.embeddings.create(input=[text], model=self._model)
        return response.data[0].embedding

    def embed_batch(self, texts: List[str]) -> List[List[float]]:
        """Generate embeddings for a batch of texts."""
        client = self._get_client()
        response = client.embeddings.create(input=texts, model=self._model)
        return [item.embedding for item in response.data]

    @property
    def dimension(self) -> int:
        """Embedding vector dimension."""
        return self._dim


def get_embedding_provider(
    provider: str = "sentence-transformers",
    model: Optional[str] = None,
    api_key: Optional[str] = None,
) -> EmbeddingProvider:
    """Factory function to get an embedding provider.

    Args:
        provider: Provider name ('sentence-transformers' or 'openai').
        model: Optional model override.
        api_key: Optional API key for cloud providers.

    Returns:
        Configured EmbeddingProvider instance.
    """
    if provider == "openai":
        return OpenAIEmbeddingProvider(
            model=model or "text-embedding-3-small",
            api_key=api_key,
        )
    else:
        return SentenceTransformerProvider(
            model_name=model or "all-MiniLM-L6-v2",
        )
