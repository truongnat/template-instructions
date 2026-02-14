"""Agent-specific output formatters.

Format prompts and skill instructions for different CLI/IDE agents,
respecting their conventions and file formats.
"""

from abc import ABC, abstractmethod
from typing import Any, Dict

from ..skills.skill import Skill


class BaseFormatter(ABC):
    """Base formatter for agent-specific output."""

    @abstractmethod
    def format_skill(self, skill: Skill) -> str:
        """Format a skill for agent consumption."""
        ...

    @abstractmethod
    def format_workflow(self, tasks: list, skills: list) -> str:
        """Format a workflow for agent consumption."""
        ...

    @property
    @abstractmethod
    def agent_name(self) -> str:
        """Return the agent name."""
        ...


class AntigravityFormatter(BaseFormatter):
    """Format output for Antigravity IDE agent.

    Antigravity reads SKILL.md files and .agent/workflows/ markdown.
    This formatter produces output compatible with those conventions.
    """

    @property
    def agent_name(self) -> str:
        return "antigravity"

    def format_skill(self, skill: Skill) -> str:
        """Format as SKILL.md with YAML frontmatter."""
        frontmatter = (
            "---\n"
            f"name: {skill.name}\n"
            f"description: {skill.description[:100]}\n"
            "---\n\n"
        )
        return frontmatter + skill.to_skill_md()

    def format_workflow(self, tasks: list, skills: list) -> str:
        """Format as .agent/workflows/ markdown."""
        lines = [
            "---",
            f"description: Workflow for {len(tasks)} tasks",
            "---",
            "",
        ]

        for i, (task, skill) in enumerate(zip(tasks, skills), 1):
            lines.extend([
                f"## Step {i}: {task.title}",
                "",
                f"**Skill**: {skill.name}",
                f"**Role**: {skill.role.value}",
                "",
            ])
            for j, step in enumerate(skill.workflow_steps, 1):
                lines.append(f"{i}.{j}. {step.action}: {step.description.split(chr(10))[0]}")
            lines.append("")

        return "\n".join(lines)


class GeminiFormatter(BaseFormatter):
    """Format output for Gemini CLI.

    Gemini CLI consumes piped context and inline prompts.
    This formatter produces concise, pipe-friendly output.
    """

    @property
    def agent_name(self) -> str:
        return "gemini"

    def format_skill(self, skill: Skill) -> str:
        """Format as concise inline instructions for Gemini CLI."""
        lines = [
            f"TASK: {skill.name}",
            f"ROLE: {skill.role.value}",
            f"DESCRIPTION: {skill.description}",
            "",
            "STEPS:",
        ]
        for i, step in enumerate(skill.workflow_steps, 1):
            lines.append(f"  {i}. [{step.action}] {step.description.split(chr(10))[0]}")

        if skill.validation_rules:
            lines.extend(["", "VALIDATION:"])
            for rule in skill.validation_rules:
                lines.append(f"  - {rule}")

        return "\n".join(lines)

    def format_workflow(self, tasks: list, skills: list) -> str:
        """Format as pipe-friendly workflow."""
        lines = ["WORKFLOW:"]
        for i, (task, skill) in enumerate(zip(tasks, skills), 1):
            lines.append(f"  {i}. {task.title} (skill: {skill.name})")
        return "\n".join(lines)


class GenericFormatter(BaseFormatter):
    """Generic markdown formatter for any agent."""

    @property
    def agent_name(self) -> str:
        return "generic"

    def format_skill(self, skill: Skill) -> str:
        """Format as standard SKILL.md."""
        return skill.to_skill_md()

    def format_workflow(self, tasks: list, skills: list) -> str:
        """Format as standard markdown workflow."""
        lines = ["# Workflow", ""]
        for i, (task, skill) in enumerate(zip(tasks, skills), 1):
            lines.append(f"## {i}. {task.title}")
            lines.append(f"\nSkill: `{skill.name}` | Role: `{skill.role.value}`\n")
        return "\n".join(lines)
