"""Research Agent - Orchestrates internet search and RAG retrieval.

Combines internet search results with local knowledge base retrieval
to provide comprehensive research context for agent tasks.
"""

from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

from ..core.logging import get_logger
from .knowledge_base import KnowledgeBase

logger = get_logger(__name__)


@dataclass
class ResearchResult:
    """Result from a research operation.

    Attributes:
        query: Original research query.
        rag_results: Results from knowledge base (RAG).
        web_results: Results from internet search.
        combined_context: Merged context string for prompt injection.
        timestamp: When the research was conducted.
        metadata: Additional metadata.
    """

    query: str
    rag_results: List[Dict[str, Any]] = field(default_factory=list)
    web_results: List[Dict[str, Any]] = field(default_factory=list)
    combined_context: str = ""
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())
    metadata: Dict[str, Any] = field(default_factory=dict)

    @property
    def has_results(self) -> bool:
        """Whether any results were found."""
        return bool(self.rag_results or self.web_results)

    @property
    def total_sources(self) -> int:
        """Total number of sources found."""
        return len(self.rag_results) + len(self.web_results)


class ResearchAgent:
    """Orchestrates research across multiple sources.

    Combines:
    1. Local knowledge base (RAG) for project-specific context
    2. Internet search for broader knowledge
    3. Context assembly for prompt injection

    Example:
        >>> kb = KnowledgeBase(persist_dir=Path(".agentic_sdlc/knowledge"))
        >>> researcher = ResearchAgent(knowledge_base=kb)
        >>> result = researcher.research("REST API authentication best practices")
        >>> print(result.combined_context)
    """

    def __init__(
        self,
        knowledge_base: Optional[KnowledgeBase] = None,
        enable_web_search: bool = True,
        max_web_results: int = 5,
        max_rag_results: int = 5,
        max_context_tokens: int = 4000,
    ):
        """Initialize the research agent.

        Args:
            knowledge_base: Optional pre-configured knowledge base.
            enable_web_search: Whether to enable internet search.
            max_web_results: Maximum web search results.
            max_rag_results: Maximum RAG results.
            max_context_tokens: Token budget for combined context.
        """
        self._kb = knowledge_base
        self._enable_web_search = enable_web_search
        self._max_web_results = max_web_results
        self._max_rag_results = max_rag_results
        self._max_context_tokens = max_context_tokens
        self._search_history: List[ResearchResult] = []

    def research(
        self,
        query: str,
        context: Optional[Dict[str, Any]] = None,
        include_web: Optional[bool] = None,
        include_rag: bool = True,
    ) -> ResearchResult:
        """Conduct research on a query.

        Searches both the local knowledge base and the internet,
        then assembles the results into a combined context.

        Args:
            query: Research query.
            context: Optional additional context.
            include_web: Override web search setting.
            include_rag: Whether to include RAG results.

        Returns:
            ResearchResult with all findings.
        """
        result = ResearchResult(query=query, metadata=context or {})

        # 1. RAG retrieval from knowledge base
        if include_rag and self._kb:
            try:
                rag_hits = self._kb.query(query, top_k=self._max_rag_results)
                result.rag_results = [
                    {
                        "content": hit.content,
                        "score": hit.score,
                        "source": hit.metadata.get("source", "knowledge_base"),
                        "type": "rag",
                    }
                    for hit in rag_hits
                ]
                logger.info(f"RAG returned {len(result.rag_results)} results for: {query[:50]}")
            except Exception as e:
                logger.error(f"RAG query failed: {e}")

        # 2. Internet search
        do_web = include_web if include_web is not None else self._enable_web_search
        if do_web:
            try:
                web_hits = self._web_search(query)
                result.web_results = web_hits
                logger.info(f"Web search returned {len(result.web_results)} results")
            except Exception as e:
                logger.error(f"Web search failed: {e}")

        # 3. Assemble combined context
        result.combined_context = self._assemble_context(result)

        # Record history
        self._search_history.append(result)
        return result

    def ingest_research(self, result: ResearchResult) -> int:
        """Ingest research results back into the knowledge base.

        Stores web search results in the KB for future RAG retrieval.

        Args:
            result: ResearchResult to ingest.

        Returns:
            Number of chunks added.
        """
        if not self._kb:
            logger.warning("No knowledge base configured for ingestion")
            return 0

        total = 0
        for web_result in result.web_results:
            content = web_result.get("content", "")
            if content and len(content) > 50:
                chunks = self._kb.ingest_text(
                    text=content,
                    source=web_result.get("url", web_result.get("source", "web")),
                    metadata={
                        "type": "web_research",
                        "query": result.query,
                        "title": web_result.get("title", ""),
                    },
                )
                total += chunks

        return total

    def get_history(self) -> List[ResearchResult]:
        """Get research history.

        Returns:
            List of past research results.
        """
        return self._search_history.copy()

    def _web_search(self, query: str) -> List[Dict[str, Any]]:
        """Perform internet search.

        Uses googlesearch-python for lightweight search.

        Args:
            query: Search query.

        Returns:
            List of result dictionaries.
        """
        results = []
        try:
            from googlesearch import search as google_search

            urls = list(google_search(query, num_results=self._max_web_results))
            for url in urls:
                results.append({
                    "url": url,
                    "source": url,
                    "type": "web",
                    "content": f"Web result: {url}",  # Content fetched separately
                    "title": url.split("/")[-1] if "/" in url else url,
                })
        except ImportError:
            logger.warning(
                "googlesearch-python not available for web search. "
                "Install with: pip install googlesearch-python"
            )
        except Exception as e:
            logger.error(f"Web search error: {e}")

        return results

    def _assemble_context(self, result: ResearchResult) -> str:
        """Assemble research results into a combined context string.

        Prioritizes RAG results (project-specific) over web results.

        Args:
            result: ResearchResult to assemble.

        Returns:
            Formatted context string.
        """
        parts = []
        char_budget = self._max_context_tokens * 4  # rough tokens-to-chars
        used = 0

        # RAG results first (higher priority)
        if result.rag_results:
            parts.append("## Knowledge Base Results\n")
            for i, hit in enumerate(result.rag_results):
                entry = f"### [{i+1}] Source: {hit.get('source', 'unknown')} (score: {hit.get('score', 0):.2f})\n{hit.get('content', '')}\n"
                if used + len(entry) > char_budget:
                    break
                parts.append(entry)
                used += len(entry)

        # Web results second
        if result.web_results and used < char_budget:
            parts.append("\n## Web Search Results\n")
            for i, hit in enumerate(result.web_results):
                entry = f"### [{i+1}] {hit.get('title', 'Untitled')} ({hit.get('url', '')})\n{hit.get('content', '')}\n"
                if used + len(entry) > char_budget:
                    break
                parts.append(entry)
                used += len(entry)

        return "\n".join(parts)
