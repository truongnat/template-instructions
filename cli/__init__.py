"""
CLI package for SDLC Kit.

This package provides a well-organized command-line interface with:
- Command modules for different functionalities
- Output formatting and styling
- CLI utilities
"""

# Import version from centralized version module
try:
    from agentic_sdlc.version import __version__
except ImportError:
    # Fallback if agentic_sdlc is not installed
    __version__ = "unknown"
