"""Skills module - Heart of the Skills-First architecture.

This module provides the Skill Engine for defining, discovering,
generating, and managing skills that CLI/IDE agents read and execute.
"""

from .skill import (
    Skill,
    SkillStep,
    SkillRole,
    SkillSource,
    ContextSpec,
    SkillMetadata,
)
from .registry import SkillRegistry
from .generator import SkillGenerator
from .loader import SkillLoader
from .remote import RemoteSkillRegistry, SecurityScanResult

__all__ = [
    "Skill",
    "SkillStep",
    "SkillRole",
    "SkillSource",
    "ContextSpec",
    "SkillMetadata",
    "SkillRegistry",
    "SkillGenerator",
    "SkillLoader",
    "RemoteSkillRegistry",
    "SecurityScanResult",
]
