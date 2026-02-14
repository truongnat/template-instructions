"""Bridge module - Agent Bridge for CLI/IDE agent integration.

The bridge is the main interface between the agentic-sdlc core and
external agents (Antigravity, Gemini CLI, Cursor). It orchestrates
skill lookup, prompt generation, and output submission.
"""

from .agent_bridge import AgentBridge, AgentResponse
from .formatters import (
    BaseFormatter,
    AntigravityFormatter,
    GeminiFormatter,
    GenericFormatter,
)

__all__ = [
    "AgentBridge",
    "AgentResponse",
    "BaseFormatter",
    "AntigravityFormatter",
    "GeminiFormatter",
    "GenericFormatter",
]
