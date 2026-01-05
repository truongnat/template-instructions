"""
API Connector

MCP connector for generic REST API access.
"""

from pathlib import Path
from typing import Any, Dict, List, Optional
from urllib.request import urlopen, Request
from urllib.error import HTTPError
import json

# Import from parent
import sys
sys.path.insert(0, str(Path(__file__).parent.parent))
from protocol import MCPConnector, MCPResource, MCPTool


class APIConnector(MCPConnector):
    """
    Connector for generic REST API access.
    
    Provides configurable access to any REST API.
    """
    
    def __init__(self, base_url: str = "", headers: Optional[Dict[str, str]] = None):
        self.base_url = base_url.rstrip("/")
        self.headers = headers or {}
        self._endpoints: List[Dict] = []
    
    @property
    def name(self) -> str:
        return "api"
    
    def add_endpoint(self, path: str, method: str = "GET", description: str = ""):
        """Register an API endpoint."""
        self._endpoints.append({
            "path": path,
            "method": method,
            "description": description
        })
    
    def _make_request(self, url: str, method: str = "GET", 
                      data: Optional[Dict] = None, 
                      headers: Optional[Dict] = None) -> Any:
        """Make an HTTP request."""
        full_headers = {**self.headers, **(headers or {})}
        full_headers.setdefault("Content-Type", "application/json")
        
        request_data = json.dumps(data).encode() if data else None
        req = Request(url, data=request_data, headers=full_headers, method=method)
        
        try:
            with urlopen(req, timeout=30) as response:
                content = response.read().decode()
                try:
                    return json.loads(content)
                except json.JSONDecodeError:
                    return content
        except HTTPError as e:
            return {"error": str(e), "code": e.code}
    
    def list_resources(self) -> List[MCPResource]:
        """List API endpoints as resources."""
        return [
            MCPResource(
                uri=f"api://{self.base_url}{ep['path']}",
                name=ep['path'],
                description=ep['description'],
                mime_type="application/json",
                metadata={"method": ep['method']}
            )
            for ep in self._endpoints
        ]
    
    def read_resource(self, uri: str) -> Optional[str]:
        """Read from an API endpoint."""
        if not uri.startswith("api://"):
            return None
        
        url = uri[6:]  # Remove "api://" prefix
        try:
            result = self._make_request(url)
            return json.dumps(result) if isinstance(result, (dict, list)) else result
        except Exception:
            return None
    
    def list_tools(self) -> List[MCPTool]:
        """List available API tools."""
        return [
            MCPTool(
                name="api_get",
                description="Make a GET request",
                input_schema={
                    "type": "object",
                    "properties": {
                        "url": {"type": "string", "description": "Full URL or path"},
                        "headers": {"type": "object", "description": "Additional headers"}
                    },
                    "required": ["url"]
                }
            ),
            MCPTool(
                name="api_post",
                description="Make a POST request",
                input_schema={
                    "type": "object",
                    "properties": {
                        "url": {"type": "string"},
                        "data": {"type": "object", "description": "Request body"},
                        "headers": {"type": "object"}
                    },
                    "required": ["url"]
                }
            ),
            MCPTool(
                name="api_put",
                description="Make a PUT request",
                input_schema={
                    "type": "object",
                    "properties": {
                        "url": {"type": "string"},
                        "data": {"type": "object"},
                        "headers": {"type": "object"}
                    },
                    "required": ["url"]
                }
            ),
            MCPTool(
                name="api_delete",
                description="Make a DELETE request",
                input_schema={
                    "type": "object",
                    "properties": {
                        "url": {"type": "string"},
                        "headers": {"type": "object"}
                    },
                    "required": ["url"]
                }
            )
        ]
    
    def call_tool(self, name: str, arguments: Dict) -> Any:
        """Execute an API tool."""
        url = arguments["url"]
        if not url.startswith("http"):
            url = f"{self.base_url}/{url.lstrip('/')}"
        
        headers = arguments.get("headers")
        data = arguments.get("data")
        
        if name == "api_get":
            return self._make_request(url, "GET", headers=headers)
        
        elif name == "api_post":
            return self._make_request(url, "POST", data=data, headers=headers)
        
        elif name == "api_put":
            return self._make_request(url, "PUT", data=data, headers=headers)
        
        elif name == "api_delete":
            return self._make_request(url, "DELETE", headers=headers)
        
        raise ValueError(f"Unknown tool: {name}")
