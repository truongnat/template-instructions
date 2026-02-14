"""Skill Loader - Load skills from various file formats.

Supports loading skills from:
- YAML files (.yaml, .yml)
- SKILL.md files (markdown with frontmatter)
- Directories (auto-discover)
"""

from pathlib import Path
from typing import Dict, List, Optional

import yaml

from ..core.logging import get_logger
from .skill import (
    ContextSpec,
    Skill,
    SkillRole,
    SkillSource,
    SkillStep,
)

logger = get_logger(__name__)


class SkillLoader:
    """Load skills from filesystem in various formats.

    The loader handles:
    - YAML skill definitions (structured data)
    - SKILL.md files (agent-readable markdown with YAML frontmatter)
    - Directory scanning for auto-discovery

    Example:
        >>> loader = SkillLoader()
        >>> skill = loader.load_yaml(Path("skills/code_review.yaml"))
        >>> skills = loader.load_directory(Path("skills/builtin"))
    """

    def load_yaml(self, path: Path) -> Optional[Skill]:
        """Load a skill from a YAML file.

        Args:
            path: Path to YAML file.

        Returns:
            Loaded Skill or None if file is invalid.
        """
        if not path.exists():
            logger.warning("Skill file not found: %s", path)
            return None

        try:
            with open(path, "r", encoding="utf-8") as f:
                data = yaml.safe_load(f)

            if not data or not isinstance(data, dict):
                logger.warning("Invalid skill file (empty or not a dict): %s", path)
                return None

            return Skill.model_validate(data)
        except Exception as e:
            logger.error("Failed to load skill from %s: %s", path, e)
            return None

    def load_skill_md(self, path: Path) -> Optional[Skill]:
        """Load a skill from a SKILL.md file with YAML frontmatter.

        The file should have YAML frontmatter between --- delimiters,
        followed by the skill description in markdown.

        Args:
            path: Path to SKILL.md file.

        Returns:
            Loaded Skill or None if file is invalid.
        """
        if not path.exists():
            logger.warning("Skill MD file not found: %s", path)
            return None

        try:
            content = path.read_text(encoding="utf-8")
            frontmatter, body = self._parse_frontmatter(content)

            if not frontmatter:
                logger.warning("No frontmatter found in %s", path)
                return None

            # Use body as description if not in frontmatter
            if "description" not in frontmatter and body.strip():
                frontmatter["description"] = body.strip()

            return Skill.model_validate(frontmatter)
        except Exception as e:
            logger.error("Failed to load SKILL.md from %s: %s", path, e)
            return None

    def load_directory(
        self,
        directory: Path,
        source: SkillSource = SkillSource.BUILTIN,
    ) -> List[Skill]:
        """Load all skills from a directory.

        Scans for .yaml, .yml, and SKILL.md files.

        Args:
            directory: Directory to scan.
            source: Source to assign to loaded skills.

        Returns:
            List of loaded skills.
        """
        if not directory.exists():
            logger.warning("Skill directory not found: %s", directory)
            return []

        skills = []

        # Load YAML files
        for ext in ("*.yaml", "*.yml"):
            for path in sorted(directory.rglob(ext)):
                skill = self.load_yaml(path)
                if skill:
                    skill.source = source
                    skills.append(skill)

        # Load SKILL.md files
        for path in sorted(directory.rglob("SKILL.md")):
            skill = self.load_skill_md(path)
            if skill:
                skill.source = source
                skills.append(skill)

        logger.info("Loaded %d skills from %s", len(skills), directory)
        return skills

    def _parse_frontmatter(self, content: str) -> tuple:
        """Parse YAML frontmatter from markdown content.

        Args:
            content: Full file content.

        Returns:
            Tuple of (frontmatter_dict, body_string).
        """
        if not content.startswith("---"):
            return None, content

        parts = content.split("---", 2)
        if len(parts) < 3:
            return None, content

        try:
            frontmatter = yaml.safe_load(parts[1])
            body = parts[2].strip()
            return frontmatter, body
        except yaml.YAMLError as e:
            logger.error("Failed to parse frontmatter: %s", e)
            return None, content
