"""Enum definitions for SDLC Kit constants."""

from enum import Enum


class WorkflowStatus(Enum):
    """Workflow execution status."""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class AgentType(Enum):
    """Agent type definitions."""
    BA = "ba"  # Business Analyst
    PM = "pm"  # Project Manager
    SA = "sa"  # Software Architect
    IMPLEMENTATION = "implementation"
    RESEARCH = "research"
    QUALITY_JUDGE = "quality_judge"
    CUSTOM = "custom"


class TaskStatus(Enum):
    """Task execution status."""
    NOT_STARTED = "not_started"
    QUEUED = "queued"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    SKIPPED = "skipped"


class RuleType(Enum):
    """Rule type definitions."""
    VALIDATION = "validation"
    TRANSFORMATION = "transformation"
    CONSTRAINT = "constraint"
    TRIGGER = "trigger"


class SkillType(Enum):
    """Skill type definitions."""
    CODE_GENERATION = "code_generation"
    CODE_REVIEW = "code_review"
    TESTING = "testing"
    DOCUMENTATION = "documentation"
    ANALYSIS = "analysis"
    CUSTOM = "custom"
