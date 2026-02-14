"""Context Optimizer - Token-efficient context management for agents.

The context optimizer ensures agents receive the most relevant information
within their token budget. It scores, ranks, deduplicates, and chunks
context items to maximize information density.
"""

import re
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Tuple

from ..core.logging import get_logger
from ..skills.skill import ContextSpec

logger = get_logger(__name__)

# Approximate tokens per character (rough estimate for English text)
CHARS_PER_TOKEN = 4


@dataclass
class ContextItem:
    """A single piece of context to include in a prompt.

    Attributes:
        name: Identifier for this context item (e.g. "project_structure").
        content: The actual content string.
        priority: Base priority (higher = more important, 0.0-1.0).
        category: Category for grouping (e.g. "code", "docs", "config").
        token_estimate: Estimated token count.
    """

    name: str
    content: str
    priority: float = 0.5
    category: str = "general"
    token_estimate: int = 0

    def __post_init__(self) -> None:
        if self.token_estimate == 0:
            self.token_estimate = len(self.content) // CHARS_PER_TOKEN


class ContextOptimizer:
    """Optimize context for agent token budgets.

    Strategies:
    1. **Relevance scoring**: Score items by keywords and priority
    2. **Token budgeting**: Allocate budget across categories
    3. **Progressive disclosure**: High-level first, detail on demand
    4. **Deduplication**: Remove redundant information

    Example:
        >>> optimizer = ContextOptimizer(max_tokens=4000)
        >>> items = [
        ...     ContextItem("readme", readme_text, priority=0.8),
        ...     ContextItem("source", source_code, priority=0.6),
        ... ]
        >>> optimized = optimizer.optimize(items, keywords=["auth", "login"])
        >>> print(f"Using {optimized.total_tokens} tokens")
    """

    def __init__(self, max_tokens: int = 4000) -> None:
        """Initialize the optimizer.

        Args:
            max_tokens: Default maximum token budget.
        """
        self._max_tokens = max_tokens

    def optimize(
        self,
        items: List[ContextItem],
        keywords: Optional[List[str]] = None,
        max_tokens: Optional[int] = None,
        context_spec: Optional[ContextSpec] = None,
    ) -> "OptimizedContext":
        """Optimize a set of context items to fit token budget.

        Args:
            items: Context items to optimize.
            keywords: Priority keywords for relevance scoring.
            max_tokens: Override default max tokens.
            context_spec: Skill's context specification.

        Returns:
            OptimizedContext with selected items and metadata.
        """
        budget = max_tokens or (context_spec.max_tokens if context_spec else self._max_tokens)
        keywords = keywords or []

        if context_spec and context_spec.priority_keywords:
            keywords.extend(context_spec.priority_keywords)

        # Step 1: Score items
        scored = self._score_items(items, keywords)

        # Step 2: Deduplicate
        scored = self._deduplicate(scored)

        # Step 3: Select items within budget
        selected, total_tokens = self._select_within_budget(scored, budget)

        # Step 4: Truncate last item if over budget
        if total_tokens > budget and selected:
            selected, total_tokens = self._truncate_to_fit(selected, budget)

        return OptimizedContext(
            items=selected,
            total_tokens=total_tokens,
            budget=budget,
            dropped_count=len(items) - len(selected),
        )

    def prioritize(
        self,
        items: List[ContextItem],
        keywords: Optional[List[str]] = None,
    ) -> List[ContextItem]:
        """Rank context items by relevance without budget constraints.

        Args:
            items: Context items to rank.
            keywords: Priority keywords.

        Returns:
            Items sorted by relevance (highest first).
        """
        scored = self._score_items(items, keywords or [])
        return [item for _, item in scored]

    def chunk(
        self,
        content: str,
        chunk_size: int = 2000,
        overlap: int = 200,
    ) -> List[str]:
        """Split large content into overlapping chunks.

        Args:
            content: Content to split.
            chunk_size: Target characters per chunk.
            overlap: Characters of overlap between chunks.

        Returns:
            List of content chunks.
        """
        if len(content) <= chunk_size:
            return [content]

        chunks = []
        start = 0
        while start < len(content):
            end = start + chunk_size

            # Try to break at a natural boundary (newline, period)
            if end < len(content):
                # Look for newline near the end
                nl_pos = content.rfind("\n", start + chunk_size - 200, end)
                if nl_pos > start:
                    end = nl_pos + 1
                else:
                    # Look for period
                    dot_pos = content.rfind(". ", start + chunk_size - 200, end)
                    if dot_pos > start:
                        end = dot_pos + 2

            chunks.append(content[start:end])
            start = end - overlap

        return chunks

    def summarize_for_budget(
        self,
        content: str,
        target_tokens: int,
    ) -> str:
        """Truncate content to fit a token budget with indication.

        Args:
            content: Content to summarize.
            target_tokens: Target token count.

        Returns:
            Truncated content with ellipsis if cut.
        """
        target_chars = target_tokens * CHARS_PER_TOKEN
        if len(content) <= target_chars:
            return content

        # Truncate at a natural boundary
        truncated = content[:target_chars]
        nl_pos = truncated.rfind("\n")
        if nl_pos > target_chars * 0.8:
            truncated = truncated[:nl_pos]

        return truncated + "\n\n... [truncated to fit context budget]"

    def _score_items(
        self,
        items: List[ContextItem],
        keywords: List[str],
    ) -> List[Tuple[float, ContextItem]]:
        """Score and sort items by relevance.

        Scoring:
        - Base priority contributes 40%
        - Keyword matches contribute 40%
        - Content length penalty 20% (prefer concise)

        Args:
            items: Items to score.
            keywords: Priority keywords.

        Returns:
            List of (score, item) tuples, sorted descending.
        """
        scored = []
        for item in items:
            # Base priority (40%)
            base_score = item.priority * 0.4

            # Keyword relevance (40%)
            if keywords:
                content_lower = item.content.lower()
                name_lower = item.name.lower()
                matches = sum(
                    1 for kw in keywords
                    if kw.lower() in content_lower or kw.lower() in name_lower
                )
                keyword_score = min(matches / len(keywords), 1.0) * 0.4
            else:
                keyword_score = 0.2  # Neutral when no keywords

            # Conciseness bonus (20%) — prefer items under 1000 tokens
            if item.token_estimate <= 500:
                length_score = 0.2
            elif item.token_estimate <= 1000:
                length_score = 0.15
            elif item.token_estimate <= 2000:
                length_score = 0.1
            else:
                length_score = 0.05

            total_score = base_score + keyword_score + length_score
            scored.append((total_score, item))

        scored.sort(key=lambda x: x[0], reverse=True)
        return scored

    def _deduplicate(
        self, scored: List[Tuple[float, ContextItem]]
    ) -> List[Tuple[float, ContextItem]]:
        """Remove items with highly similar content.

        Uses a simple approach: skip items whose name or first 100 chars
        match an already-seen item.

        Args:
            scored: Scored items (already sorted).

        Returns:
            Deduplicated list.
        """
        seen_keys = set()
        result = []

        for score, item in scored:
            # Create dedup key from name + content prefix
            key = f"{item.name}:{item.content[:100]}"
            if key not in seen_keys:
                seen_keys.add(key)
                result.append((score, item))

        return result

    def _select_within_budget(
        self,
        scored: List[Tuple[float, ContextItem]],
        budget: int,
    ) -> Tuple[List[ContextItem], int]:
        """Select highest-scored items that fit within token budget.

        Args:
            scored: Scored and sorted items.
            budget: Token budget.

        Returns:
            Tuple of (selected items, total tokens).
        """
        selected = []
        total_tokens = 0

        for _, item in scored:
            if total_tokens + item.token_estimate <= budget:
                selected.append(item)
                total_tokens += item.token_estimate
            elif total_tokens < budget * 0.9:
                # Still room — try to fit a truncated version
                remaining = budget - total_tokens
                if remaining >= 100:  # Minimum useful chunk
                    truncated_content = self.summarize_for_budget(
                        item.content, remaining
                    )
                    truncated_item = ContextItem(
                        name=item.name,
                        content=truncated_content,
                        priority=item.priority,
                        category=item.category,
                    )
                    selected.append(truncated_item)
                    total_tokens += truncated_item.token_estimate
                break

        return selected, total_tokens

    def _truncate_to_fit(
        self,
        items: List[ContextItem],
        budget: int,
    ) -> Tuple[List[ContextItem], int]:
        """Truncate the last item to fit exactly within budget.

        Args:
            items: Selected items (last one may be over budget).
            budget: Token budget.

        Returns:
            Tuple of (adjusted items, total tokens).
        """
        total = sum(item.token_estimate for item in items[:-1])
        remaining = budget - total

        if remaining <= 0:
            return items[:-1], total

        last = items[-1]
        truncated = self.summarize_for_budget(last.content, remaining)
        items[-1] = ContextItem(
            name=last.name,
            content=truncated,
            priority=last.priority,
            category=last.category,
        )

        total = sum(item.token_estimate for item in items)
        return items, total


@dataclass
class OptimizedContext:
    """Result of context optimization.

    Attributes:
        items: Selected context items.
        total_tokens: Total estimated tokens used.
        budget: Token budget that was applied.
        dropped_count: Number of items dropped to fit budget.
    """

    items: List[ContextItem]
    total_tokens: int
    budget: int
    dropped_count: int = 0

    def to_string(self, separator: str = "\n\n---\n\n") -> str:
        """Render all items as a single context string.

        Args:
            separator: Separator between items.

        Returns:
            Combined context string.
        """
        parts = []
        for item in self.items:
            parts.append(f"## {item.name}\n\n{item.content}")
        return separator.join(parts)

    @property
    def utilization(self) -> float:
        """Token budget utilization percentage."""
        if self.budget == 0:
            return 0.0
        return self.total_tokens / self.budget
