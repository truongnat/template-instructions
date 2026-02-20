"""Agentic SDLC - Multi-Domain Swarm Agent Framework.

Next-generation AI Software Development Lifecycle framework with Swarm Intelligence, 
RAG-powered Research, and Multi-Provider LLM orchestration.

The framework provides an E2E pipeline:
Domain Detection -> Research -> Prompt Optimization -> Swarm Execution -> Self-Learning.

Key Features:
- Domain Engine: Automatic task classification (Frontend, Backend, etc.)
- RAG Research: Integrated Knowledge Base with ChromaDB
- Prompt Lab: A/B testing and AI-powered prompt evaluation
- Swarm Intelligence: Role-based agent teams (Developer, Reviewer, Tester)
- Multi-Provider LLM: Unified Gemini, OpenAI, Anthropic, and Ollama support
- Self-Learning: Performance analysis and improvement loop

Usage:
    from agentic_sdlc import AgentBridge
    from pathlib import Path

    bridge = AgentBridge(project_dir=Path("."))
    response = bridge.process_request_enhanced("Implement user login")
"""

from ._version import __version__

# Core - Configuration & Engines
from .core import (
    Config,
    AgenticSDLCError,
    ConfigurationError,
    ValidationError,
    get_logger,
    setup_logging,
    # Domain Engine
    Domain,
    DomainRegistry,
    # LLM Routing
    LLMConfig,
    LLMMessage,
    LLMProvider,
    LLMProviderType,
    LLMResponse,
    LLMRouter,
    get_provider,
    get_router,
    # Artifacts
    ArtifactManager,
    ArtifactType,
)

# Knowledge & RAG
from .knowledge import (
    KnowledgeBase,
    ResearchAgent,
    VectorStore,
    ChromaVectorStore,
    InMemoryVectorStore,
    EmbeddingProvider,
)

# Prompts & Optimization
from .prompts import (
    PromptLab,
    PromptGenerator,
    ContextOptimizer,
    ContextItem,
)

# Swarm Intelligence
from .swarm import (
    SwarmOrchestrator,
    SwarmConfig,
    SwarmResult,
    SwarmAgent,
    AgentRole,
    MessageBus,
    DeveloperAgent,
    ReviewerAgent,
    TesterAgent,
    ResearcherAgent,
)

# SDLC Tracking
from .sdlc import (
    Board,
    Task,
    Issue,
    Sprint,
    TaskStatus,
    SDLCTracker,
)

# Agent Bridge (Main Entry Point)
from .bridge import (
    AgentBridge,
    AgentResponse,
)

# Intelligence & reasoning
from .intelligence.reasoning.reasoner import Reasoner
from .intelligence.learning.self_improvement import SelfImprovementEngine

__all__ = [
    "__version__",
    # Core
    "Config",
    "AgenticSDLCError",
    "ConfigurationError",
    "ValidationError",
    "get_logger",
    "setup_logging",
    "Domain",
    "DomainRegistry",
    "LLMConfig",
    "LLMMessage",
    "LLMProvider",
    "LLMProviderType",
    "LLMResponse",
    "LLMRouter",
    "get_provider",
    "get_router",
    "ArtifactManager",
    "ArtifactType",
    # Knowledge
    "KnowledgeBase",
    "ResearchAgent",
    "VectorStore",
    "ChromaVectorStore",
    "InMemoryVectorStore",
    "EmbeddingProvider",
    # Prompts
    "PromptLab",
    "PromptGenerator",
    "ContextOptimizer",
    "ContextItem",
    # Swarm
    "SwarmOrchestrator",
    "SwarmConfig",
    "SwarmResult",
    "SwarmAgent",
    "AgentRole",
    "MessageBus",
    "DeveloperAgent",
    "ReviewerAgent",
    "TesterAgent",
    "ResearcherAgent",
    # SDLC
    "Board",
    "Task",
    "Issue",
    "Sprint",
    "TaskStatus",
    "SDLCTracker",
    # Bridge
    "AgentBridge",
    "AgentResponse",
    # Intelligence
    "Reasoner",
    "SelfImprovementEngine",
]
