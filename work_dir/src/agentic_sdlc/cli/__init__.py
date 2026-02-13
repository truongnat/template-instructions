"""Command-line interface for Agentic SDLC.

This module provides the CLI interface for the Agentic SDLC framework.
The CLI is a consumer of the SDK public API and is optional (install with [cli] extra).
"""

from .main import cli, main

__all__ = ["cli", "main"]
