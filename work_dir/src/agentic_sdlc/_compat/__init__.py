"""Compatibility layer for old import paths.

This module provides backward compatibility for old import paths,
emitting deprecation warnings to guide users to the new locations.

Old imports will continue to work but will emit DeprecationWarning messages.

To enable compatibility shims, call install_compatibility_shims():
    from agentic_sdlc._compat import install_compatibility_shims
    install_compatibility_shims()
"""

from .installer import install_compatibility_shims  # noqa: F401

__all__ = ["install_compatibility_shims"]
