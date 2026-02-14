"""Agentic SDLC - Skills-First AI Development Lifecycle Framework.

This is the public API. All exports follow semantic versioning.

The Agentic SDLC framework provides a skills-first architecture where
CLI/IDE agents (Antigravity, Gemini CLI, Cursor) discover, execute,
and review structured skills. The framework handles skill management,
prompt generation, context optimization, SDLC tracking, and self-review.

Key Features:
- Skill Engine: Define, discover, search, generate, and load skills
- Prompt Generator: Optimized prompts with context management
- SDLC Board: Task/Sprint/Issue tracking with lifecycle management
- Agent Bridge: Integration layer for CLI/IDE agents
- Self-Review: Automated output quality review and A/B testing
- Remote Registry: Pull skills from GitHub/NPX with security scanning

Usage:
    from agentic_sdlc import AgentBridge, Skill, SkillRegistry
    from pathlib import Path

    # Create bridge (main entry point for agents)
    bridge = AgentBridge(project_dir=Path("."))

    # Process a user request
    response = bridge.process_request("Create a REST API with auth")

    # Or search skills directly
    registry = SkillRegistry()
    skills = registry.search("testing")
"""

from ._version import __version__

# Enable compatibility shims for legacy imports
from ._compat import install_compatibility_shims
install_compatibility_shims()

# Core module exports (kept from original)
from .core import (
    # Configuration
    Config,
    get_config,
    load_config,
    # Configuration types
    AgentConfig,
    ModelConfig,
    SDKConfig,
    WorkflowConfig,
    # Exceptions
    AgenticSDLCError,
    AgentError,
    ConfigurationError,
    ModelError,
    PluginError,
    ValidationError,
    WorkflowError,
    # Logging
    get_logger,
    setup_logging,
    # Resources
    get_resource_path,
    list_resources,
    load_resource_text,
)

# Skills module exports (NEW - Phase 1)
from .skills import (
    Skill,
    SkillStep,
    SkillRole,
    SkillSource,
    ContextSpec,
    SkillMetadata,
    SkillRegistry,
    SkillGenerator,
    SkillLoader,
    RemoteSkillRegistry,
    SecurityScanResult,
)

# Prompts module exports (NEW - Phase 2)
from .prompts import (
    PromptGenerator,
    ContextOptimizer,
    ContextItem,
)

# SDLC module exports (NEW - Phase 3)
from .sdlc import (
    Board,
    Task,
    Issue,
    Sprint,
    TaskStatus,
    SDLCTracker,
)

# Agent Bridge module exports (NEW - Phase 4)
from .bridge import (
    AgentBridge,
    AgentResponse,
    AntigravityFormatter,
    GeminiFormatter,
    GenericFormatter,
)

# Intelligence module exports (kept + NEW review)
from .intelligence import (
    Collaborator,
    DecisionEngine,
    Learner,
    LearningStrategy,
    MetricsCollector,
    Monitor,
    Reasoner,
    TeamCoordinator,
)
from .intelligence.review import (
    SelfReviewEngine,
    ReviewResult,
    ReviewCriteria,
    ABScorer,
    ABTest,
    ABResult,
)

# Infrastructure (kept: lifecycle, automation)
from .infrastructure.lifecycle import LifecycleManager, Phase
from .infrastructure.automation import WorkflowEngine, WorkflowRunner

# Plugins module exports (kept)
from .plugins import (
    Plugin,
    PluginMetadata,
    PluginRegistry,
    get_plugin_registry,
)

__all__ = [
    # Version
    "__version__",
    # Core - Configuration
    "Config",
    "load_config",
    "get_config",
    "AgentConfig",
    "ModelConfig",
    "SDKConfig",
    "WorkflowConfig",
    # Core - Exceptions
    "AgenticSDLCError",
    "ConfigurationError",
    "ValidationError",
    "PluginError",
    "WorkflowError",
    "AgentError",
    "ModelError",
    # Core - Logging
    "setup_logging",
    "get_logger",
    # Core - Resources
    "get_resource_path",
    "load_resource_text",
    "list_resources",
    # Skills (NEW)
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
    # Prompts (NEW)
    "PromptGenerator",
    "ContextOptimizer",
    "ContextItem",
    # SDLC (NEW)
    "Board",
    "Task",
    "Issue",
    "Sprint",
    "TaskStatus",
    "SDLCTracker",
    # Agent Bridge (NEW)
    "AgentBridge",
    "AgentResponse",
    "AntigravityFormatter",
    "GeminiFormatter",
    "GenericFormatter",
    # Intelligence (kept + NEW review)
    "Learner",
    "LearningStrategy",
    "Monitor",
    "MetricsCollector",
    "Reasoner",
    "DecisionEngine",
    "Collaborator",
    "TeamCoordinator",
    "SelfReviewEngine",
    "ReviewResult",
    "ReviewCriteria",
    "ABScorer",
    "ABTest",
    "ABResult",
    # Infrastructure (kept)
    "LifecycleManager",
    "Phase",
    "WorkflowEngine",
    "WorkflowRunner",
    # Plugins (kept)
    "Plugin",
    "PluginMetadata",
    "PluginRegistry",
    "get_plugin_registry",
]
