"""
MCP (Model Context Protocol) Package

Layer 3: Infrastructure - External integrations and AI model connections.
"""

from .protocol import MCPClient, MCPResource, MCPTool
from .config import MCPConfig

__all__ = ['MCPClient', 'MCPResource', 'MCPTool', 'MCPConfig']

__version__ = "1.0.0"
