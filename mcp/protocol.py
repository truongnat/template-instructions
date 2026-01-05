"""
MCP Protocol Handler

Core protocol implementation for Model Context Protocol.
"""

import json
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Dict, List, Optional, Callable


@dataclass
class MCPResource:
    """Represents an MCP resource."""
    uri: str
    name: str
    description: str = ""
    mime_type: str = "text/plain"
    metadata: Dict = field(default_factory=dict)
    
    def to_dict(self) -> dict:
        return {
            "uri": self.uri,
            "name": self.name,
            "description": self.description,
            "mimeType": self.mime_type,
            "metadata": self.metadata
        }


@dataclass
class MCPTool:
    """Represents an MCP tool/action."""
    name: str
    description: str
    input_schema: Dict
    handler: Optional[Callable] = None
    
    def to_dict(self) -> dict:
        return {
            "name": self.name,
            "description": self.description,
            "inputSchema": self.input_schema
        }


class MCPConnector(ABC):
    """Abstract base class for MCP connectors."""
    
    @property
    @abstractmethod
    def name(self) -> str:
        """Connector name."""
        pass
    
    @abstractmethod
    def list_resources(self) -> List[MCPResource]:
        """List available resources."""
        pass
    
    @abstractmethod
    def read_resource(self, uri: str) -> str:
        """Read a resource by URI."""
        pass
    
    @abstractmethod
    def list_tools(self) -> List[MCPTool]:
        """List available tools."""
        pass
    
    @abstractmethod
    def call_tool(self, name: str, arguments: Dict) -> Any:
        """Call a tool with arguments."""
        pass


class MCPClient:
    """
    MCP Client - Main interface for Model Context Protocol.
    
    Manages connectors and provides unified access to resources and tools.
    """
    
    def __init__(self):
        self.connectors: Dict[str, MCPConnector] = {}
        self._resources_cache: Dict[str, List[MCPResource]] = {}
        self._tools_cache: Dict[str, List[MCPTool]] = {}
    
    def register_connector(self, connector: MCPConnector):
        """Register a connector."""
        self.connectors[connector.name] = connector
        # Clear caches
        self._resources_cache.pop(connector.name, None)
        self._tools_cache.pop(connector.name, None)
    
    def unregister_connector(self, name: str):
        """Unregister a connector."""
        self.connectors.pop(name, None)
        self._resources_cache.pop(name, None)
        self._tools_cache.pop(name, None)
    
    def list_connectors(self) -> List[str]:
        """List registered connectors."""
        return list(self.connectors.keys())
    
    def list_resources(self, connector_name: Optional[str] = None) -> List[MCPResource]:
        """List resources from connectors."""
        if connector_name:
            connector = self.connectors.get(connector_name)
            if connector:
                return connector.list_resources()
            return []
        
        # List from all connectors
        resources = []
        for connector in self.connectors.values():
            resources.extend(connector.list_resources())
        return resources
    
    def read_resource(self, uri: str) -> Optional[str]:
        """Read a resource by URI."""
        # Determine which connector to use based on URI scheme
        for connector in self.connectors.values():
            try:
                content = connector.read_resource(uri)
                if content is not None:
                    return content
            except Exception:
                continue
        return None
    
    def list_tools(self, connector_name: Optional[str] = None) -> List[MCPTool]:
        """List tools from connectors."""
        if connector_name:
            connector = self.connectors.get(connector_name)
            if connector:
                return connector.list_tools()
            return []
        
        # List from all connectors
        tools = []
        for connector in self.connectors.values():
            tools.extend(connector.list_tools())
        return tools
    
    def call_tool(self, name: str, arguments: Dict) -> Any:
        """Call a tool by name."""
        for connector in self.connectors.values():
            tools = connector.list_tools()
            for tool in tools:
                if tool.name == name:
                    return connector.call_tool(name, arguments)
        
        raise ValueError(f"Tool '{name}' not found")
    
    def get_status(self) -> Dict:
        """Get client status."""
        return {
            "connectors": len(self.connectors),
            "connector_names": list(self.connectors.keys()),
            "timestamp": datetime.now().isoformat()
        }


# Global client instance
_client: Optional[MCPClient] = None


def get_client() -> MCPClient:
    """Get the global MCP client."""
    global _client
    if _client is None:
        _client = MCPClient()
    return _client


def main():
    """CLI entry point."""
    import argparse
    
    parser = argparse.ArgumentParser(description="MCP Protocol Handler")
    parser.add_argument("--status", action="store_true", help="Show client status")
    parser.add_argument("--list-connectors", action="store_true", help="List connectors")
    parser.add_argument("--list-resources", type=str, nargs="?", const="all", 
                        help="List resources (optionally for specific connector)")
    parser.add_argument("--list-tools", type=str, nargs="?", const="all",
                        help="List tools (optionally for specific connector)")
    
    args = parser.parse_args()
    client = get_client()
    
    if args.status:
        print(json.dumps(client.get_status(), indent=2))
    
    elif args.list_connectors:
        for name in client.list_connectors():
            print(f"- {name}")
    
    elif args.list_resources:
        connector = None if args.list_resources == "all" else args.list_resources
        for resource in client.list_resources(connector):
            print(f"[{resource.mime_type}] {resource.uri}: {resource.name}")
    
    elif args.list_tools:
        connector = None if args.list_tools == "all" else args.list_tools
        for tool in client.list_tools(connector):
            print(f"- {tool.name}: {tool.description}")
    
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
