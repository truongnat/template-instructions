"""Prompt Generator - Create optimized prompts for CLI/IDE agents.

Generates prompts by combining skill definitions with project context,
using Jinja2 templates. Supports skill execution prompts, self-review
prompts, and A/B test variant prompts.
"""

from pathlib import Path
from typing import Any, Dict, List, Optional

from ..core.logging import get_logger
from ..skills.skill import Skill

logger = get_logger(__name__)

# Try to import Jinja2, fall back to simple string formatting
try:
    from jinja2 import Environment, BaseLoader, Template

    HAS_JINJA2 = True
except ImportError:
    HAS_JINJA2 = False
    logger.info("Jinja2 not available, using simple string templates")


class PromptGenerator:
    """Generate optimized prompts for agent consumption.

    Combines skill definitions with project context to create
    focused, token-efficient prompts. Supports multiple output
    formats for different agents.

    Example:
        >>> gen = PromptGenerator()
        >>> prompt = gen.generate(skill, context={"project": "todo-app"})
        >>> review_prompt = gen.generate_review_prompt(output, skill)
    """

    def __init__(self, template_dir: Optional[Path] = None) -> None:
        """Initialize the prompt generator.

        Args:
            template_dir: Directory containing custom Jinja2 templates.
                         Falls back to built-in templates if not provided.
        """
        self._template_dir = template_dir
        if HAS_JINJA2:
            self._env = Environment(loader=BaseLoader(), autoescape=False)

    def generate(
        self,
        skill: Skill,
        context: Optional[Dict[str, Any]] = None,
        agent_type: str = "generic",
    ) -> str:
        """Generate an execution prompt from a skill and context.

        Args:
            skill: Skill to generate prompt for.
            context: Project context dictionary.
            agent_type: Target agent type for formatting.

        Returns:
            Formatted prompt string.
        """
        context = context or {}

        # If skill has a custom prompt template, use it
        if skill.prompt_template and HAS_JINJA2:
            try:
                template = self._env.from_string(skill.prompt_template)
                return template.render(skill=skill, context=context)
            except Exception as e:
                logger.warning("Failed to render skill template: %s", e)

        # Fall back to structured prompt
        return self._build_structured_prompt(skill, context)

    def generate_review_prompt(
        self,
        output: str,
        skill: Skill,
        context: Optional[Dict[str, Any]] = None,
    ) -> str:
        """Generate a self-review prompt for validating agent output.

        Args:
            output: The agent's output to review.
            skill: The skill that produced the output.
            context: Optional additional context.

        Returns:
            Review prompt string.
        """
        criteria_lines = []
        for criterion, weight in skill.score_criteria.items():
            criteria_lines.append(f"- **{criterion}** (weight: {weight:.0%})")

        validation_lines = [f"- {rule}" for rule in skill.validation_rules]

        return (
            f"# Self-Review: {skill.name}\n\n"
            f"You are reviewing the output of a **{skill.role.value}** task.\n\n"
            f"## Original Task\n\n{skill.description}\n\n"
            f"## Output to Review\n\n```\n{output}\n```\n\n"
            f"## Scoring Criteria\n\n"
            + "\n".join(criteria_lines)
            + "\n\n"
            f"## Validation Rules\n\n"
            + "\n".join(validation_lines)
            + "\n\n"
            f"## Instructions\n\n"
            f"1. Score each criterion from 0.0 to 1.0\n"
            f"2. Check each validation rule (pass/fail)\n"
            f"3. Calculate weighted total score\n"
            f"4. Provide specific feedback for improvements\n"
            f"5. Verdict: PASS (score >= 0.7) or FAIL with retry suggestions\n\n"
            f"## Response Format\n\n"
            f"```json\n"
            f'{{\n'
            f'  "scores": {{"criterion": score}},\n'
            f'  "total_score": 0.0,\n'
            f'  "validations": [{{"rule": "...", "pass": true/false}}],\n'
            f'  "feedback": "...",\n'
            f'  "verdict": "PASS/FAIL"\n'
            f'}}\n'
            f"```\n"
        )

    def generate_ab_prompts(
        self,
        skill: Skill,
        context: Optional[Dict[str, Any]] = None,
        variants: int = 2,
    ) -> List[str]:
        """Generate A/B test variant prompts for comparison.

        Creates multiple prompt variants with different approaches:
        - Variant A: Structured, step-by-step approach
        - Variant B: Creative, flexible approach

        Args:
            skill: Skill to generate variants for.
            context: Project context.
            variants: Number of variants (2 or 3).

        Returns:
            List of variant prompt strings.
        """
        context = context or {}
        prompts = []

        # Variant A: Structured approach
        prompt_a = self._build_structured_prompt(skill, context)
        prompt_a = (
            "> **Variant A: Structured Approach**\n"
            "> Follow the steps precisely in order. Focus on completeness.\n\n"
            + prompt_a
        )
        prompts.append(prompt_a)

        # Variant B: Creative approach
        prompt_b = self._build_creative_prompt(skill, context)
        prompts.append(prompt_b)

        if variants >= 3:
            # Variant C: Minimal/lean approach
            prompt_c = self._build_minimal_prompt(skill, context)
            prompts.append(prompt_c)

        return prompts

    def _build_structured_prompt(
        self, skill: Skill, context: Dict[str, Any]
    ) -> str:
        """Build a structured, step-by-step prompt.

        Args:
            skill: Skill definition.
            context: Project context.

        Returns:
            Structured prompt string.
        """
        sections = [
            f"# Task: {skill.name}",
            "",
            f"**Role**: {skill.role.value}",
            f"**Category**: {skill.category}",
            "",
            "## Objective",
            "",
            skill.description,
            "",
        ]

        # Add context
        if context:
            sections.extend(["## Context", ""])
            for key, value in context.items():
                if isinstance(value, str) and len(value) > 200:
                    sections.append(f"### {key}")
                    sections.append(f"\n{value}\n")
                else:
                    sections.append(f"- **{key}**: {value}")
            sections.append("")

        # Add steps
        if skill.workflow_steps:
            sections.extend(["## Steps", ""])
            for i, step in enumerate(skill.workflow_steps, 1):
                sections.append(f"### Step {i}: {step.name}")
                sections.append(f"\n**Action**: {step.action}")
                if step.description:
                    sections.append(f"\n{step.description}")
                if step.expected_output:
                    sections.append(f"\n**Expected Output**: {step.expected_output}")
                sections.append("")

        # Add validation
        if skill.validation_rules:
            sections.extend([
                "## Validation Checklist",
                "",
                *[f"- [ ] {rule}" for rule in skill.validation_rules],
                "",
            ])

        return "\n".join(sections)

    def _build_creative_prompt(
        self, skill: Skill, context: Dict[str, Any]
    ) -> str:
        """Build a more creative, flexible prompt variant.

        Args:
            skill: Skill definition.
            context: Project context.

        Returns:
            Creative prompt string.
        """
        context_summary = ""
        if context:
            context_items = [f"- {k}: {v}" for k, v in context.items()]
            context_summary = "\n".join(context_items)

        return (
            f"> **Variant B: Creative Approach**\n"
            f"> Use your best judgment. Focus on quality over rigid steps.\n\n"
            f"# {skill.name}\n\n"
            f"You are a **{skill.role.value}** working on: {skill.description}\n\n"
            + (f"## Context\n\n{context_summary}\n\n" if context_summary else "")
            + f"## Goal\n\n"
            f"Deliver the best possible result for this task. You may approach it\n"
            f"in any order, but ensure these quality criteria are met:\n\n"
            + "\n".join(
                f"- **{k}** ({v:.0%} importance)"
                for k, v in skill.score_criteria.items()
            )
            + "\n\n"
            + ("## Must Pass\n\n"
               + "\n".join(f"- {r}" for r in skill.validation_rules)
               + "\n"
               if skill.validation_rules
               else "")
        )

    def _build_minimal_prompt(
        self, skill: Skill, context: Dict[str, Any]
    ) -> str:
        """Build a minimal, concise prompt variant.

        Args:
            skill: Skill definition.
            context: Project context.

        Returns:
            Minimal prompt string.
        """
        return (
            f"> **Variant C: Minimal Approach**\n"
            f"> Be concise. Ship the simplest correct solution.\n\n"
            f"**Task**: {skill.description}\n"
            f"**Role**: {skill.role.value}\n\n"
            f"Key requirements:\n"
            + "\n".join(f"- {r}" for r in skill.validation_rules[:3])
            + "\n"
        )
