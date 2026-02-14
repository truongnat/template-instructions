"""Skill Registry - Discovery, search, and management of skills.

The registry is the central index of all available skills (built-in,
generated, user-defined). It supports keyword-based search, tag filtering,
score-based ranking, and auto-discovery from filesystem directories.
"""

import json
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

import yaml

from ..core.logging import get_logger
from .skill import Skill, SkillMetadata, SkillRole, SkillSource

logger = get_logger(__name__)


class SkillRegistry:
    """Central registry for skill discovery and management.

    The registry maintains an in-memory index of skills and supports:
    - Keyword-based search across name, description, tags, category
    - Role and category filtering
    - Score-based ranking using execution history
    - Auto-discovery from filesystem directories
    - Persistence of metadata (execution counts, scores)

    Example:
        >>> registry = SkillRegistry()
        >>> registry.discover(Path("skills/builtin"))
        >>> results = registry.search("react webapp frontend")
        >>> best = results[0]  # Highest relevance
    """

    def __init__(self, metadata_path: Optional[Path] = None) -> None:
        """Initialize the registry.

        Args:
            metadata_path: Path to persist skill metadata (JSON).
                          If None, metadata is only kept in memory.
        """
        self._skills: Dict[str, Skill] = {}
        self._metadata_path = metadata_path
        self._load_metadata()

    def register(self, skill: Skill) -> None:
        """Register a skill in the registry.

        If a skill with the same name already exists, it will be
        replaced only if the new version is higher or equal.

        Args:
            skill: Skill to register.
        """
        existing = self._skills.get(skill.name)
        if existing and existing.version > skill.version:
            logger.warning(
                "Skipping registration of %s v%s (existing v%s is newer)",
                skill.name,
                skill.version,
                existing.version,
            )
            return

        self._skills[skill.name] = skill
        logger.info("Registered skill: %s v%s [%s]", skill.name, skill.version, skill.source.value)

    def get(self, name: str) -> Optional[Skill]:
        """Get a skill by exact name.

        Args:
            name: Skill name.

        Returns:
            Skill if found, None otherwise.
        """
        return self._skills.get(name)

    def search(
        self,
        query: str,
        role: Optional[SkillRole] = None,
        category: Optional[str] = None,
        limit: int = 10,
    ) -> List[Skill]:
        """Search skills by keyword relevance.

        Searches across name, description, tags, and category.
        Results are ranked by relevance score, then by success rate.

        Args:
            query: Search query (space-separated keywords).
            role: Optional role filter.
            category: Optional category filter.
            limit: Maximum results to return.

        Returns:
            List of skills sorted by relevance (best first).
        """
        query_tokens = set(query.lower().split())
        scored: List[tuple] = []

        if not query_tokens:
            # If no query tokens, include all matching skills with base score
            for skill in self._skills.values():
                if role and skill.role != role:
                    continue
                if category and skill.category.lower() != category.lower():
                    continue
                scored.append((1.0, skill))
        else:
            for skill in self._skills.values():
                # Apply filters
                if role and skill.role != role:
                    continue
                if category and skill.category.lower() != category.lower():
                    continue

                # Calculate relevance score
                score = self._relevance_score(skill, query_tokens)
                if score > 0:
                    scored.append((score, skill))

        # Sort by relevance (desc), then success_rate (desc)
        scored.sort(key=lambda x: (x[0], x[1].metadata.success_rate), reverse=True)
        return [skill for _, skill in scored[:limit]]

    def list_all(
        self,
        role: Optional[SkillRole] = None,
        category: Optional[str] = None,
        source: Optional[SkillSource] = None,
    ) -> List[Skill]:
        """List all skills with optional filters.

        Args:
            role: Optional role filter.
            category: Optional category filter.
            source: Optional source filter.

        Returns:
            List of matching skills.
        """
        results = []
        for skill in self._skills.values():
            if role and skill.role != role:
                continue
            if category and skill.category.lower() != category.lower():
                continue
            if source and skill.source != source:
                continue
            results.append(skill)
        return results

    def update_metadata(
        self,
        name: str,
        success: bool,
        score: Optional[float] = None,
    ) -> None:
        """Update skill metadata after execution.

        Args:
            name: Skill name.
            success: Whether the execution was successful.
            score: Optional review score (0.0 - 1.0).
        """
        skill = self._skills.get(name)
        if not skill:
            logger.warning("Cannot update metadata: skill '%s' not found", name)
            return

        meta = skill.metadata
        meta.execution_count += 1
        if success:
            meta.success_count += 1
        if score is not None:
            # Running average
            total = meta.avg_score * (meta.execution_count - 1) + score
            meta.avg_score = total / meta.execution_count
        meta.last_used = datetime.now().isoformat()

        self._save_metadata()

    def discover(self, directory: Path) -> int:
        """Auto-discover skills from a directory.

        Loads all .yaml and .yml files as skill definitions.

        Args:
            directory: Directory to scan.

        Returns:
            Number of skills discovered.
        """
        if not directory.exists():
            logger.warning("Skill directory does not exist: %s", directory)
            return 0

        count = 0
        for path in sorted(directory.rglob("*.yaml")):
            try:
                skill = self._load_skill_file(path)
                if skill:
                    self.register(skill)
                    count += 1
            except Exception as e:
                logger.error("Failed to load skill from %s: %s", path, e)

        for path in sorted(directory.rglob("*.yml")):
            try:
                skill = self._load_skill_file(path)
                if skill:
                    self.register(skill)
                    count += 1
            except Exception as e:
                logger.error("Failed to load skill from %s: %s", path, e)

        logger.info("Discovered %d skills from %s", count, directory)
        return count

    @property
    def count(self) -> int:
        """Number of registered skills."""
        return len(self._skills)

    def _relevance_score(self, skill: Skill, query_tokens: set) -> float:
        """Calculate keyword relevance score for a skill.

        Scoring weights:
        - Name match: 3.0 per token
        - Tag match: 2.0 per token
        - Category match: 2.0 per token
        - Description word match: 1.0 per token

        Args:
            skill: Skill to score.
            query_tokens: Set of lowercase query tokens.

        Returns:
            Relevance score (0.0 = no match).
        """
        score = 0.0
        name_tokens = set(skill.name.lower().replace("-", " ").replace("_", " ").split())
        tag_tokens = {t.lower() for t in skill.tags}
        category_tokens = set(skill.category.lower().split())
        desc_tokens = set(skill.description.lower().split())

        for token in query_tokens:
            if token in name_tokens:
                score += 3.0
            if token in tag_tokens:
                score += 2.0
            if token in category_tokens:
                score += 2.0
            if token in desc_tokens:
                score += 1.0

        return score

    def _load_skill_file(self, path: Path) -> Optional[Skill]:
        """Load a skill from a YAML file.

        Args:
            path: Path to YAML file.

        Returns:
            Loaded Skill or None if invalid.
        """
        with open(path, "r", encoding="utf-8") as f:
            data = yaml.safe_load(f)

        if not data or not isinstance(data, dict):
            return None

        # Ensure source is set
        if "source" not in data:
            data["source"] = SkillSource.BUILTIN.value

        return Skill.model_validate(data)

    def _load_metadata(self) -> None:
        """Load persisted metadata from disk."""
        if not self._metadata_path or not self._metadata_path.exists():
            return

        try:
            with open(self._metadata_path, "r", encoding="utf-8") as f:
                data = json.load(f)

            for name, meta_dict in data.items():
                skill = self._skills.get(name)
                if skill:
                    skill.metadata = SkillMetadata.model_validate(meta_dict)
        except Exception as e:
            logger.error("Failed to load skill metadata: %s", e)

    def _save_metadata(self) -> None:
        """Persist metadata to disk."""
        if not self._metadata_path:
            return

        try:
            self._metadata_path.parent.mkdir(parents=True, exist_ok=True)
            data = {
                name: skill.metadata.model_dump()
                for name, skill in self._skills.items()
            }
            with open(self._metadata_path, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2)
        except Exception as e:
            logger.error("Failed to save skill metadata: %s", e)
