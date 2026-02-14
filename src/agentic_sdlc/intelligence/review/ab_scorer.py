"""A/B Scorer - Compare prompt/output variants.

Runs multiple prompt variants through review, scores them,
and selects the best performing approach for learning.
"""

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

from ...core.logging import get_logger
from ...skills.skill import Skill
from .self_review import ReviewResult, SelfReviewEngine

logger = get_logger(__name__)


@dataclass
class ABResult:
    """Result of an A/B comparison."""

    variant_label: str
    output: str
    review: ReviewResult
    generation_meta: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ABTest:
    """An A/B test with multiple variants and results.

    Attributes:
        skill_name: Skill being tested.
        results: Per-variant results.
        winner: Label of the winning variant.
    """

    skill_name: str
    results: List[ABResult] = field(default_factory=list)
    winner: Optional[str] = None

    @property
    def is_complete(self) -> bool:
        return self.winner is not None

    def to_markdown(self) -> str:
        """Render A/B test results as markdown."""
        lines = [
            f"# A/B Test: {self.skill_name}",
            "",
            f"**Winner**: {self.winner or 'TBD'}",
            "",
            "## Variant Scores",
            "",
        ]

        for r in sorted(self.results, key=lambda x: x.review.total_score, reverse=True):
            icon = "🏆" if r.variant_label == self.winner else "  "
            lines.append(
                f"{icon} **{r.variant_label}**: "
                f"{r.review.total_score:.2f} [{r.review.verdict}]"
            )
            for c in r.review.criteria:
                lines.append(f"    - {c.name}: {c.score:.2f}")
            lines.append("")

        return "\n".join(lines)


class ABScorer:
    """Compare multiple output variants and pick the best.

    Used with PromptGenerator.generate_ab_prompts() to test
    different prompt strategies and learn which works best.

    Example:
        >>> scorer = ABScorer()
        >>> test = scorer.create_test(skill)
        >>> scorer.add_result(test, "Variant A", output_a)
        >>> scorer.add_result(test, "Variant B", output_b)
        >>> winner = scorer.evaluate(test)
    """

    def __init__(
        self,
        review_engine: Optional[SelfReviewEngine] = None,
        pass_threshold: float = 0.7,
    ) -> None:
        """Initialize the A/B scorer.

        Args:
            review_engine: Custom review engine. Uses default if None.
            pass_threshold: Min score to pass.
        """
        self._engine = review_engine or SelfReviewEngine(pass_threshold)
        self._tests: Dict[str, ABTest] = {}

    def create_test(self, skill: Skill) -> ABTest:
        """Create a new A/B test for a skill.

        Args:
            skill: Skill being tested.

        Returns:
            New ABTest instance.
        """
        test = ABTest(skill_name=skill.name)
        self._tests[skill.name] = test
        logger.info("Created A/B test for skill: %s", skill.name)
        return test

    def add_result(
        self,
        test: ABTest,
        variant_label: str,
        output: str,
        skill: Skill,
        meta: Optional[Dict[str, Any]] = None,
    ) -> ABResult:
        """Add a variant result to the test.

        Args:
            test: The A/B test.
            variant_label: Label for this variant (e.g. "A", "B").
            output: The variant's output.
            skill: Skill for review scoring.
            meta: Optional metadata about generation.

        Returns:
            ABResult with review scores.
        """
        review = self._engine.review(output, skill)
        result = ABResult(
            variant_label=variant_label,
            output=output,
            review=review,
            generation_meta=meta or {},
        )
        test.results.append(result)

        logger.info(
            "A/B variant '%s': score=%.2f, verdict=%s",
            variant_label,
            review.total_score,
            review.verdict,
        )
        return result

    def evaluate(self, test: ABTest) -> str:
        """Evaluate the test and select a winner.

        Winner is selected by highest total_score. In case of tie,
        the first variant wins.

        Args:
            test: The A/B test to evaluate.

        Returns:
            Label of the winning variant.
        """
        if not test.results:
            raise ValueError("No results to evaluate")

        best = max(test.results, key=lambda r: r.review.total_score)
        test.winner = best.variant_label

        logger.info(
            "A/B test winner for '%s': %s (score: %.2f)",
            test.skill_name,
            best.variant_label,
            best.review.total_score,
        )
        return best.variant_label

    def get_insights(self, test: ABTest) -> Dict[str, Any]:
        """Get analytical insights from the test.

        Args:
            test: Completed test.

        Returns:
            Dictionary of insights including criterion-level comparisons.
        """
        if not test.results or not test.winner:
            return {}

        # Compare criteria across variants
        criterion_comparison = {}
        for result in test.results:
            for c in result.review.criteria:
                if c.name not in criterion_comparison:
                    criterion_comparison[c.name] = {}
                criterion_comparison[c.name][result.variant_label] = c.score

        return {
            "winner": test.winner,
            "score_spread": max(r.review.total_score for r in test.results) -
                           min(r.review.total_score for r in test.results),
            "criterion_comparison": criterion_comparison,
            "all_passed": all(r.review.passed for r in test.results),
        }
