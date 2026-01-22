"""
AutoSkillBuilder - Dynamically generate agent skills from task descriptions.

Part of Layer 2: Intelligence Layer.

Inspired by Swarms AutoSwarmBuilder/Agent customization.
Enables dynamic agent specialization by generating SKILL.md files on the fly.
"""

import json
import sys
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional




@dataclass
class SkillTemplate:
    """Template for a new skill."""
    name: str
    description: str
    instructions: str
    responsibilities: List[str]
    artifacts: List[str]
    examples: List[str]


class AutoSkillBuilder:
    """
    Dynamically generates SKILL.md files based on requirements.
    
    Use cases:
    - Creating ad-hoc experts for niche tasks.
    - Automating agent onboarding for new technologies.
    - Standardizing agent behavior through generated instructions.
    """

    def __init__(
        self,
        skills_dir: Optional[Path] = None,
        llm_callback: Optional[Callable[[str], str]] = None
    ):
        """
        Initialize the AutoSkillBuilder.
        
        Args:
            skills_dir: Directory to save generated skills.
            llm_callback: Callable to use an LLM for generation.
        """
        self.skills_dir = skills_dir or Path(".agent/skills")
        self.llm_callback = llm_callback
        
        # Default prompt for skill generation
        self.system_prompt = """You are an Agentic SDLC Architect. Your task is to generate a professional, 
comprehensive SKILL.md file for a new specialized AI agent role.

The SKILL.md should follow this format:
---
name: [role-name]
description: [brief description]
---
# [Role Name] Skill

## Identity
[Who is this agent?]

## Core Responsibilities
[What are the primary tasks? List at least 5]

## Rules & Constraints
[What MUST they follow? What must they NEVER do?]

## Artifacts
[What files do they produce?]

## Examples
[Provide 2-3 concrete examples of how they work]

Target Role/Objective: {OBJECTIVE}

GENERATE THE SKILL.MD CONTENT NOW:"""

    def generate_skill(self, name: str, objective: str) -> str:
        """
        Generate skill content using LLM.
        """
        if not self.llm_callback:
            return self._generate_static_template(name, objective)
        
        prompt = self.system_prompt.replace("{OBJECTIVE}", objective)
        return self.llm_callback(prompt)

    def _generate_static_template(self, name: str, objective: str) -> str:
        """Fallback static template if no LLM provided."""
        return f"""---
name: {name.lower().replace(' ', '-')}
description: Specialized agent for {objective}
---

# {name} Skill

## Identity
You are a specialized agent designed to handle: {objective}

## Core Responsibilities
- Implement requirements for {name}
- Validate outputs related to {objective}
- Ensure compliance with project standards
- Document decisions in the logs
- Report progress to @BRAIN

## Rules & Constraints
- NEVER deviate from the core objective: {objective}
- ALWAYS report status transitions to @BRAIN
- Follow standard SDLC flow

## Artifacts
- docs/sprints/sprint-[N]/artifacts/{name}-Spec.md
- {name}-Log.md

## Examples
- "Analyze the {objective} requirements for the new feature"
- "Generate the implementation plan for {name}"
"""

    def save_skill(self, name: str, content: str) -> Path:
        """
        Save the generated skill to the skills directory.
        """
        role_dir = self.skills_dir / name.lower().replace(' ', '-')
        role_dir.mkdir(parents=True, exist_ok=True)
        
        skill_file = role_dir / "SKILL.md"
        with open(skill_file, 'w', encoding='utf-8') as f:
            f.write(content)
        
        return skill_file

    def build_skill(self, name: str, objective: str) -> Path:
        """
        Generate and save a skill in one go.
        """
        print(f"🛠️ Building skill: {name}...")
        content = self.generate_skill(name, objective)
        path = self.save_skill(name, content)
        print(f"✅ Skill built successfully at: {path}")
        return path


def main():
    """CLI entry point."""
    import argparse
    
    parser = argparse.ArgumentParser(description="AutoSkillBuilder - Build SKILL.md templates")
    parser.add_argument("--name", required=True, help="Name of the new skill/role")
    parser.add_argument("--objective", required=True, help="Determine the objective of the role")
    parser.add_argument("--save", action="store_true", default=True, help="Save to .agent/skills/")
    
    args = parser.parse_args()
    
    builder = AutoSkillBuilder()
    builder.build_skill(args.name, args.objective)


if __name__ == "__main__":
    main()
