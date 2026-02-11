"""Compatibility shim for agentic_sdlc.core.config (old path).

This module provides backward compatibility for old imports from
agentic_sdlc.core.config, redirecting to the new location.
"""

from .._internal.deprecation import create_module_deprecation_handler

__getattr__ = create_module_deprecation_handler(
    old_module_path="agentic_sdlc.core.config",
    new_module_path="agentic_sdlc.core.config",
)
