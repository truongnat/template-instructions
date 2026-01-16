"""
Local LLM - Privacy-focused LLM Gateway

Part of Layer 3: Infrastructure Layer.
"""

from .ollama_client import OllamaClient, OllamaResponse

__all__ = ["OllamaClient", "OllamaResponse"]
