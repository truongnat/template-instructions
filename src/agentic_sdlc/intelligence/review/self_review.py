"""Self-Review Engine - Automated output quality review.

Validates agent outputs against skill criteria without needing
a separate reviewer agent. Produces structured review results
with per-criterion scores and actionable feedback.
"""

import re
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

from ...core.logging import get_logger
from ...skills.skill import Skill

logger = get_logger(__name__)


@dataclass
class ReviewCriteria:
    """A single review criterion with its score."""

    name: str
    weight: float
    score: float = 0.0
    feedback: str = ""


@dataclass
class ReviewResult:
    """Result of a self-review evaluation.

    Attributes:
        total_score: Weighted average score (0.0-1.0).
        criteria: Per-criterion scores.
        validations: Validation rule pass/fail results.
        verdict: PASS or FAIL.
        feedback: Aggregated feedback.
    """

    total_score: float = 0.0
    criteria: List[ReviewCriteria] = field(default_factory=list)
    validations: List[Dict[str, Any]] = field(default_factory=list)
    verdict: str = "PENDING"
    feedback: str = ""
    pass_threshold: float = 0.7

    @property
    def passed(self) -> bool:
        return self.verdict == "PASS"

    def to_markdown(self) -> str:
        """Render review result as markdown."""
        lines = [
            f"# Review Result: {self.verdict}",
            f"**Score**: {self.total_score:.2f} / 1.00",
            "",
            "## Criteria Scores",
            "",
        ]
        for c in self.criteria:
            bar = "█" * int(c.score * 10) + "░" * (10 - int(c.score * 10))
            lines.append(f"- **{c.name}** ({c.weight:.0%}): `{bar}` {c.score:.2f}")
            if c.feedback:
                lines.append(f"  - {c.feedback}")

        if self.validations:
            lines.extend(["", "## Validation Rules", ""])
            for v in self.validations:
                icon = "✅" if v.get("pass") else "❌"
                lines.append(f"- {icon} {v.get('rule', '')}")

        if self.feedback:
            lines.extend(["", "## Summary", "", self.feedback])

        return "\n".join(lines)


class SelfReviewEngine:
    """Engine for automated self-review of agent outputs.

    Analyzes outputs against skill-defined criteria and validation
    rules using heuristic checks. Does not require LLM calls.

    Example:
        >>> engine = SelfReviewEngine()
        >>> result = engine.review(output_text, skill)
        >>> print(f"Score: {result.total_score}, Verdict: {result.verdict}")
    """

    def __init__(self, pass_threshold: float = 0.7) -> None:
        self._pass_threshold = pass_threshold

    def review(
        self,
        output: str,
        skill: Skill,
        context: Optional[Dict[str, Any]] = None,
    ) -> ReviewResult:
        """Review an output against skill criteria.

        Args:
            output: Agent's output text.
            skill: Skill that generated the output.
            context: Optional additional context.

        Returns:
            ReviewResult with scores and verdict.
        """
        criteria = []

        for name, weight in skill.score_criteria.items():
            score = self._evaluate_criterion(name, output, skill, context)
            criteria.append(ReviewCriteria(
                name=name,
                weight=weight,
                score=score,
                feedback=self._get_criterion_feedback(name, score),
            ))

        # Calculate weighted score
        total = sum(c.score * c.weight for c in criteria)
        weight_sum = sum(c.weight for c in criteria)
        total_score = total / weight_sum if weight_sum > 0 else 0.0

        # Run validation checks
        validations = self._run_validations(output, skill)
        all_valid = all(v.get("pass", False) for v in validations) if validations else True

        # Determine verdict
        if total_score >= self._pass_threshold and all_valid:
            verdict = "PASS"
        elif total_score >= self._pass_threshold and not all_valid:
            verdict = "PASS_WITH_WARNINGS"
        else:
            verdict = "FAIL"

        feedback = self._generate_summary(total_score, criteria, validations)

        return ReviewResult(
            total_score=total_score,
            criteria=criteria,
            validations=validations,
            verdict=verdict,
            feedback=feedback,
            pass_threshold=self._pass_threshold,
        )

    def _evaluate_criterion(
        self,
        criterion: str,
        output: str,
        skill: Skill,
        context: Optional[Dict[str, Any]] = None,
    ) -> float:
        """Evaluate a single criterion heuristically.

        Uses content analysis heuristics based on the criterion name.
        """
        output_lower = output.lower()
        output_len = len(output)

        # Completeness: Does the output address all steps?
        if criterion in ("completeness", "coverage"):
            step_count = len(skill.workflow_steps)
            mentioned = sum(
                1 for step in skill.workflow_steps
                if step.name.lower() in output_lower or step.action.lower() in output_lower
            )
            return min(mentioned / max(step_count, 1), 1.0)

        # Code quality: Check for code blocks, functions, error handling
        if criterion in ("code_quality", "quality"):
            score = 0.3  # base
            if "```" in output:
                score += 0.2
            if "def " in output or "function " in output or "class " in output:
                score += 0.2
            if "try" in output_lower or "catch" in output_lower or "except" in output_lower:
                score += 0.15
            if "return" in output_lower:
                score += 0.15
            return min(score, 1.0)

        # Correctness: Check structure and content presence
        if criterion in ("correctness", "accuracy"):
            score = 0.4  # base for having content
            if output_len > 200:
                score += 0.2
            if output_len > 500:
                score += 0.1
            # Check for markdown structure
            if "#" in output:
                score += 0.15
            if any(c in output for c in ["-", "*", "1."]):
                score += 0.15
            return min(score, 1.0)

        # Clarity: Readability indicators
        if criterion in ("clarity", "readability"):
            score = 0.3
            # Has headings
            if re.search(r"^#+\s", output, re.MULTILINE):
                score += 0.2
            # Has paragraphs (multiple line breaks)
            if output.count("\n\n") >= 2:
                score += 0.15
            # Not too dense (reasonable line lengths)
            lines = output.split("\n")
            short_lines = sum(1 for l in lines if len(l) < 120)
            if lines and short_lines / len(lines) > 0.7:
                score += 0.15
            if output_len > 100:
                score += 0.2
            return min(score, 1.0)

        # Documentation/examples
        if criterion in ("documentation", "examples"):
            score = 0.3
            if "example" in output_lower or "```" in output:
                score += 0.3
            if "usage" in output_lower or "how to" in output_lower:
                score += 0.2
            if "param" in output_lower or "return" in output_lower:
                score += 0.2
            return min(score, 1.0)

        # Thoroughness
        if criterion in ("thoroughness",):
            word_count = len(output.split())
            score = min(word_count / 300, 0.5) + 0.2
            if "however" in output_lower or "note" in output_lower:
                score += 0.1
            if "edge case" in output_lower or "limitation" in output_lower:
                score += 0.2
            return min(score, 1.0)

        # Actionability
        if criterion in ("actionability",):
            score = 0.3
            if "```" in output:
                score += 0.2
            if "fix" in output_lower or "change" in output_lower or "update" in output_lower:
                score += 0.2
            if "recommend" in output_lower or "suggest" in output_lower:
                score += 0.15
            if re.search(r"line \d+", output_lower):
                score += 0.15
            return min(score, 1.0)

        # Generic: length-based
        if criterion in ("structure", "efficiency", "performance",
                         "scalability", "maintainability", "technical_soundness",
                         "test_coverage", "testability", "edge_cases"):
            base = min(output_len / 1000, 0.5) + 0.3
            return min(base, 0.85)

        # Default
        return 0.5

    def _run_validations(
        self, output: str, skill: Skill
    ) -> List[Dict[str, Any]]:
        """Run validation rules against output."""
        results = []
        for rule in skill.validation_rules:
            passed = self._check_rule(rule, output)
            results.append({"rule": rule, "pass": passed})
        return results

    def _check_rule(self, rule: str, output: str) -> bool:
        """Heuristically check a validation rule."""
        rule_lower = rule.lower()
        output_lower = output.lower()

        # "Must include X"
        if "must include" in rule_lower:
            subject = rule_lower.split("must include")[-1].strip()
            return subject[:20] in output_lower

        # "No placeholder" rules
        if "placeholder" in rule_lower or "todo" in rule_lower:
            return "todo" not in output_lower and "placeholder" not in output_lower

        # "Must have/provide"
        if "must" in rule_lower:
            return len(output) > 100  # generous pass

        # Default: pass with content
        return len(output) > 50

    def _get_criterion_feedback(self, name: str, score: float) -> str:
        """Generate feedback for a criterion score."""
        if score >= 0.8:
            return "Excellent"
        elif score >= 0.6:
            return "Good, minor improvements possible"
        elif score >= 0.4:
            return "Needs improvement"
        else:
            return "Significant work needed"

    def _generate_summary(
        self,
        total_score: float,
        criteria: List[ReviewCriteria],
        validations: List[Dict[str, Any]],
    ) -> str:
        """Generate a summary feedback message."""
        weak = [c for c in criteria if c.score < 0.6]
        failed_validations = [v for v in validations if not v.get("pass")]

        parts = []
        if total_score >= 0.8:
            parts.append("High quality output.")
        elif total_score >= 0.6:
            parts.append("Acceptable output with room for improvement.")
        else:
            parts.append("Output needs significant improvement.")

        if weak:
            names = ", ".join(c.name for c in weak)
            parts.append(f"Weak areas: {names}.")

        if failed_validations:
            rules = "; ".join(v["rule"][:50] for v in failed_validations)
            parts.append(f"Failed validations: {rules}.")

        return " ".join(parts)
