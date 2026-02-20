"""Swarm Intelligence - Multi-agent orchestration with AutoGen integration.

This package provides:
- SwarmOrchestrator: Manages agent teams and task distribution
- Agent types: Specialized agents for different roles
- MessageBus: Async inter-agent communication
- SupervisorAgent: Quality control and coordination

Uses AutoGen 0.4's swarm patterns when available, with a fallback
to a lightweight built-in implementation.
"""

from .orchestrator import SwarmOrchestrator, SwarmConfig, SwarmResult
from .agents import (
    AgentRole,
    SwarmAgent,
    DeveloperAgent,
    ReviewerAgent,
    TesterAgent,
    ResearcherAgent,
)
from .message_bus import MessageBus, SwarmMessage

__all__ = [
    "SwarmOrchestrator",
    "SwarmConfig",
    "SwarmResult",
    "AgentRole",
    "SwarmAgent",
    "DeveloperAgent",
    "ReviewerAgent",
    "TesterAgent",
    "ResearcherAgent",
    "MessageBus",
    "SwarmMessage",
]
