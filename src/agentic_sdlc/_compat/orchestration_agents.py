"""Compatibility shim for agentic_sdlc.orchestration.agents (old path).

This module provides backward compatibility for old imports from
agentic_sdlc.orchestration.agents, redirecting to the new location.
"""

from .._internal.deprecation import create_module_deprecation_handler

__getattr__ = create_module_deprecation_handler(
    old_module_path="agentic_sdlc.orchestration.agents",
    new_module_path="agentic_sdlc.orchestration.agents",
)
