"""Prompt Lab - A/B testing and optimization engine for prompts.

Generates multiple prompt variants, evaluates them via sub-agent
scoring, and selects the best variant. Tracks all prompt versions,
scores, and lineage for continuous improvement.
"""

import hashlib
import json
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import TYPE_CHECKING, Any, Dict, List, Optional, Tuple

from ..core.logging import get_logger

if TYPE_CHECKING:
    from ..core.llm import LLMRouter

logger = get_logger(__name__)


@dataclass
class PromptVariant:
    """A single prompt variant in an A/B test.

    Attributes:
        id: Unique identifier for this variant.
        content: The prompt text.
        metadata: Generation metadata (strategy, model, etc.).
        score: Evaluation score (0.0 - 1.0).
        feedback: Evaluator feedback text.
        created_at: Timestamp of creation.
    """

    id: str
    content: str
    metadata: Dict[str, Any] = field(default_factory=dict)
    score: float = 0.0
    feedback: str = ""
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())


@dataclass
class PromptTestResult:
    """Result of a prompt A/B test.

    Attributes:
        test_id: Unique test identifier.
        query: Original user query.
        variants: All tested variants.
        winner: The winning variant.
        improvement: Score improvement over baseline.
        timestamp: When the test was conducted.
    """

    test_id: str
    query: str
    variants: List[PromptVariant]
    winner: Optional[PromptVariant] = None
    improvement: float = 0.0
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())


class PromptLab:
    """Prompt optimization engine with A/B testing.

    Generates multiple prompt variants using different strategies,
    evaluates each variant, and selects the best one.

    Strategies:
    1. Direct: Use the task description as-is
    2. Structured: Add role, context, constraints
    3. Chain-of-thought: Add reasoning steps
    4. Few-shot: Include examples

    Example:
        >>> lab = PromptLab(history_dir=Path(".agentic_sdlc/prompts"))
        >>> result = lab.optimize(
        ...     query="Build a REST API with auth",
        ...     context={"domain": "backend", "language": "python"},
        ... )
        >>> print(result.winner.content)
    """

    def __init__(
        self,
        history_dir: Optional[Path] = None,
        max_variants: int = 3,
        llm: Optional["LLMRouter"] = None,
    ):
        """Initialize the prompt lab.

        Args:
            history_dir: Directory to persist prompt history.
            max_variants: Maximum variants to generate per test.
            llm: Optional LLM router for AI-powered evaluation.
                 Falls back to heuristic scoring if not provided.
        """
        self._history_dir = history_dir
        self._max_variants = max_variants
        self._llm = llm
        self._test_history: List[PromptTestResult] = []

        if history_dir:
            history_dir.mkdir(parents=True, exist_ok=True)

    def optimize(
        self,
        query: str,
        context: Optional[Dict[str, Any]] = None,
        research_context: str = "",
        strategies: Optional[List[str]] = None,
    ) -> PromptTestResult:
        """Generate and evaluate prompt variants.

        Args:
            query: User's original query.
            context: Additional context (domain, language, etc.).
            research_context: Research results to incorporate.
            strategies: Override default strategies.

        Returns:
            PromptTestResult with all variants and the winner.
        """
        context = context or {}
        test_id = hashlib.md5(
            f"{query}:{datetime.now().isoformat()}".encode()
        ).hexdigest()[:12]

        strategies = strategies or ["direct", "structured", "chain_of_thought"]

        # Generate variants
        variants = []
        for strategy in strategies[:self._max_variants]:
            variant = self._generate_variant(
                query=query,
                context=context,
                research_context=research_context,
                strategy=strategy,
            )
            variants.append(variant)

        # Score variants
        for variant in variants:
            variant.score = self._evaluate_variant(variant, query, context)

        # Select winner
        variants.sort(key=lambda v: v.score, reverse=True)
        winner = variants[0] if variants else None

        # Calculate improvement
        baseline_score = variants[-1].score if len(variants) > 1 else 0.0
        improvement = (winner.score - baseline_score) if winner else 0.0

        result = PromptTestResult(
            test_id=test_id,
            query=query,
            variants=variants,
            winner=winner,
            improvement=improvement,
        )

        # Record history
        self._test_history.append(result)
        self._persist_result(result)

        logger.info(
            f"Prompt optimization complete: winner={winner.id if winner else 'none'}, "
            f"score={winner.score if winner else 0:.2f}"
        )
        return result

    def get_best_prompt(
        self,
        query: str,
        context: Optional[Dict[str, Any]] = None,
        research_context: str = "",
    ) -> str:
        """Convenience method to get the best optimized prompt.

        Args:
            query: User's query.
            context: Optional context.
            research_context: Research results.

        Returns:
            Best prompt string.
        """
        result = self.optimize(query, context, research_context)
        return result.winner.content if result.winner else query

    def get_history(self) -> List[PromptTestResult]:
        """Get prompt test history."""
        return self._test_history.copy()

    def _generate_variant(
        self,
        query: str,
        context: Dict[str, Any],
        research_context: str,
        strategy: str,
    ) -> PromptVariant:
        """Generate a prompt variant using a specific strategy.

        Args:
            query: User query.
            context: Context dict.
            research_context: Research context string.
            strategy: Generation strategy name.

        Returns:
            Generated PromptVariant.
        """
        variant_id = hashlib.md5(
            f"{strategy}:{query}:{datetime.now().isoformat()}".encode()
        ).hexdigest()[:10]

        if strategy == "structured":
            content = self._structured_prompt(query, context, research_context)
        elif strategy == "chain_of_thought":
            content = self._cot_prompt(query, context, research_context)
        else:  # "direct"
            content = self._direct_prompt(query, context, research_context)

        return PromptVariant(
            id=f"{strategy}_{variant_id}",
            content=content,
            metadata={"strategy": strategy, "context": context},
        )

    def _direct_prompt(
        self, query: str, context: Dict[str, Any], research: str
    ) -> str:
        """Generate a direct prompt."""
        parts = [query]
        if research:
            parts.append(f"\n\n## Research Context\n{research}")
        if context:
            parts.append(f"\n\n## Context\n{json.dumps(context, indent=2)}")
        return "\n".join(parts)

    def _structured_prompt(
        self, query: str, context: Dict[str, Any], research: str
    ) -> str:
        """Generate a structured prompt with role/context/constraints."""
        domain = context.get("domain", "general")
        language = context.get("language", "")

        sections = [
            f"# Task\n{query}",
            f"\n## Role\nYou are an expert {domain} developer.",
        ]

        if language:
            sections.append(f"\n## Language/Stack\n{language}")

        if research:
            sections.append(f"\n## Research Context\n{research}")

        sections.extend([
            "\n## Requirements",
            "1. Follow best practices and design patterns",
            "2. Include proper error handling",
            "3. Write clean, maintainable code",
            "4. Add documentation and comments",
            "\n## Output Format",
            "- Provide the implementation with file paths",
            "- Include any necessary configuration",
            "- List any dependencies required",
        ])

        return "\n".join(sections)

    def _cot_prompt(
        self, query: str, context: Dict[str, Any], research: str
    ) -> str:
        """Generate a chain-of-thought prompt."""
        domain = context.get("domain", "general")

        sections = [
            f"# Task\n{query}",
            f"\n## Domain: {domain}",
            "\n## Approach — Think Step by Step",
            "Before implementing, reason through the following:",
            "1. **Understand**: What exactly is being asked?",
            "2. **Research**: What existing patterns or solutions apply?",
            "3. **Design**: What architecture and components are needed?",
            "4. **Plan**: What is the implementation order?",
            "5. **Implement**: Write the code following the plan.",
            "6. **Verify**: How to validate correctness?",
        ]

        if research:
            sections.append(f"\n## Research Context\n{research}")

        sections.append(
            "\n## Output\n"
            "Show your reasoning process, then provide the implementation."
        )

        return "\n".join(sections)

    def _evaluate_variant(
        self,
        variant: PromptVariant,
        query: str,
        context: Dict[str, Any],
    ) -> float:
        """Evaluate a prompt variant quality.

        Uses LLM-powered evaluation if an LLM router is configured,
        otherwise falls back to heuristic scoring.

        Args:
            variant: Variant to evaluate.
            query: Original query.
            context: Context dict.

        Returns:
            Score between 0.0 and 1.0.
        """
        # Try LLM-based evaluation first
        if self._llm:
            try:
                return self._evaluate_with_llm(variant, query, context)
            except Exception as e:
                logger.debug(f"LLM evaluation failed, using heuristic: {e}")

        # Heuristic fallback
        return self._evaluate_heuristic(variant, query, context)

    def _evaluate_with_llm(
        self,
        variant: PromptVariant,
        query: str,
        context: Dict[str, Any],
    ) -> float:
        """Evaluate variant quality using LLM."""
        from ..core.llm import LLMMessage

        eval_prompt = (
            "Rate the following prompt on a scale from 0.0 to 1.0 based on:\n"
            "- Clarity (is the task clearly defined?)\n"
            "- Completeness (does it include role, context, constraints?)\n"
            "- Structure (is it well-organized with sections?)\n"
            "- Actionability (can an AI agent execute this directly?)\n\n"
            f"Original user query: {query}\n\n"
            f"Prompt to evaluate:\n---\n{variant.content[:2000]}\n---\n\n"
            "Respond with ONLY a JSON object: {\"score\": 0.X, \"feedback\": \"...\"}"
        )

        response = self._llm.chat([
            LLMMessage(role="system", content="You are a prompt quality evaluator. Respond only with JSON."),
            LLMMessage(role="user", content=eval_prompt),
        ], temperature=0.1, max_tokens=200)

        # Parse score from response
        try:
            # Try to extract JSON from the response
            text = response.content.strip()
            if "{" in text:
                json_str = text[text.index("{"):text.rindex("}") + 1]
                data = json.loads(json_str)
                score = float(data.get("score", 0.5))
                variant.feedback = data.get("feedback", "")
                return min(max(score, 0.0), 1.0)
        except (json.JSONDecodeError, ValueError):
            pass

        return 0.5  # Default if parsing fails

    def _evaluate_heuristic(
        self,
        variant: PromptVariant,
        query: str,
        context: Dict[str, Any],
    ) -> float:
        """Evaluate variant using rule-based heuristics."""
        score = 0.5  # base score
        content = variant.content

        # Reward structure
        if "##" in content:
            score += 0.1  # Has sections
        if "role" in content.lower() or "expert" in content.lower():
            score += 0.05  # Has role definition
        if "step" in content.lower() or "plan" in content.lower():
            score += 0.1  # Has planning guidance
        if "error" in content.lower() or "handling" in content.lower():
            score += 0.05  # Mentions error handling
        if "test" in content.lower() or "verify" in content.lower():
            score += 0.05  # Mentions testing

        # Reward contextual richness
        if context.get("domain"):
            if context["domain"] in content.lower():
                score += 0.05

        # Penalize too-short or too-long
        word_count = len(content.split())
        if word_count < 20:
            score -= 0.1
        elif word_count > 500:
            score -= 0.05

        # Reward research inclusion
        if "research" in content.lower() and "context" in content.lower():
            score += 0.05

        return min(max(score, 0.0), 1.0)

    def _persist_result(self, result: PromptTestResult) -> None:
        """Persist test result to disk."""
        if not self._history_dir:
            return

        try:
            result_file = self._history_dir / f"test_{result.test_id}.json"
            data = {
                "test_id": result.test_id,
                "query": result.query,
                "timestamp": result.timestamp,
                "improvement": result.improvement,
                "winner_id": result.winner.id if result.winner else None,
                "winner_score": result.winner.score if result.winner else 0,
                "variants": [
                    {
                        "id": v.id,
                        "strategy": v.metadata.get("strategy", "unknown"),
                        "score": v.score,
                        "content_length": len(v.content),
                    }
                    for v in result.variants
                ],
            }
            with open(result_file, "w") as f:
                json.dump(data, f, indent=2)
        except Exception as e:
            logger.error(f"Failed to persist prompt test result: {e}")
