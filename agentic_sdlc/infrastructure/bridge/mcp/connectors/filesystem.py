"""
File System Connector

MCP connector for local file system access.
"""

import os
from pathlib import Path
from typing import Any, Dict, List, Optional

# Import from parent
import sys
sys.path.insert(0, str(Path(__file__).parent.parent))
from protocol import MCPConnector, MCPResource, MCPTool


class FileSystemConnector(MCPConnector):
    """
    Connector for local file system access.
    
    Provides read/write access to files within a root directory.
    """
    
    def __init__(self, root_path: Optional[Path] = None):
        self.root_path = Path(root_path) if root_path else Path.cwd()
        self._ensure_root_exists()
    
    @property
    def name(self) -> str:
        return "filesystem"
    
    def _ensure_root_exists(self):
        """Ensure root directory exists."""
        if not self.root_path.exists():
            raise ValueError(f"Root path does not exist: {self.root_path}")
    
    def _is_safe_path(self, path: Path) -> bool:
        """Check if path is within root (prevent directory traversal)."""
        try:
            path.resolve().relative_to(self.root_path.resolve())
            return True
        except ValueError:
            return False
    
    def _path_to_uri(self, path: Path) -> str:
        """Convert path to file URI."""
        return f"file://{path.as_posix()}"
    
    def _uri_to_path(self, uri: str) -> Path:
        """Convert file URI to path."""
        if uri.startswith("file://"):
            return Path(uri[7:])
        return Path(uri)
    
    def list_resources(self, pattern: str = "**/*", max_depth: int = 3) -> List[MCPResource]:
        """List files as resources."""
        resources = []
        
        for path in self.root_path.glob(pattern):
            if path.is_file():
                # Limit depth
                try:
                    relative = path.relative_to(self.root_path)
                    if len(relative.parts) <= max_depth:
                        resources.append(MCPResource(
                            uri=self._path_to_uri(path),
                            name=path.name,
                            description=f"File: {relative}",
                            mime_type=self._get_mime_type(path),
                            metadata={
                                "size": path.stat().st_size,
                                "modified": path.stat().st_mtime
                            }
                        ))
                except ValueError:
                    continue
        
        return resources[:100]  # Limit to 100 resources
    
    def read_resource(self, uri: str) -> Optional[str]:
        """Read file content."""
        path = self._uri_to_path(uri)
        
        if not path.is_absolute():
            path = self.root_path / path
        
        if not self._is_safe_path(path):
            raise ValueError("Path outside root directory")
        
        if not path.exists():
            return None
        
        try:
            with open(path, 'r', encoding='utf-8') as f:
                return f.read()
        except (IOError, UnicodeDecodeError):
            return None
    
    def list_tools(self) -> List[MCPTool]:
        """List available file system tools."""
        return [
            MCPTool(
                name="fs_read",
                description="Read a file",
                input_schema={
                    "type": "object",
                    "properties": {
                        "path": {"type": "string", "description": "File path"}
                    },
                    "required": ["path"]
                }
            ),
            MCPTool(
                name="fs_write",
                description="Write to a file",
                input_schema={
                    "type": "object",
                    "properties": {
                        "path": {"type": "string", "description": "File path"},
                        "content": {"type": "string", "description": "Content to write"}
                    },
                    "required": ["path", "content"]
                }
            ),
            MCPTool(
                name="fs_list",
                description="List directory contents",
                input_schema={
                    "type": "object",
                    "properties": {
                        "path": {"type": "string", "description": "Directory path"},
                        "pattern": {"type": "string", "description": "Glob pattern"}
                    },
                    "required": ["path"]
                }
            ),
            MCPTool(
                name="fs_search",
                description="Search for files",
                input_schema={
                    "type": "object",
                    "properties": {
                        "pattern": {"type": "string", "description": "Search pattern"},
                        "content": {"type": "string", "description": "Content to search for"}
                    },
                    "required": ["pattern"]
                }
            )
        ]
    
    def call_tool(self, name: str, arguments: Dict) -> Any:
        """Execute a file system tool."""
        if name == "fs_read":
            return self.read_resource(arguments["path"])
        
        elif name == "fs_write":
            path = Path(arguments["path"])
            if not path.is_absolute():
                path = self.root_path / path
            
            if not self._is_safe_path(path):
                raise ValueError("Path outside root directory")
            
            path.parent.mkdir(parents=True, exist_ok=True)
            with open(path, 'w', encoding='utf-8') as f:
                f.write(arguments["content"])
            return {"success": True, "path": str(path)}
        
        elif name == "fs_list":
            path = Path(arguments["path"])
            if not path.is_absolute():
                path = self.root_path / path
            
            pattern = arguments.get("pattern", "*")
            items = []
            for item in path.glob(pattern):
                items.append({
                    "name": item.name,
                    "type": "directory" if item.is_dir() else "file",
                    "size": item.stat().st_size if item.is_file() else None
                })
            return items
        
        elif name == "fs_search":
            pattern = arguments["pattern"]
            content = arguments.get("content")
            
            results = []
            for path in self.root_path.glob(pattern):
                if path.is_file():
                    if content:
                        try:
                            with open(path, 'r', encoding='utf-8') as f:
                                if content in f.read():
                                    results.append(str(path))
                        except:
                            pass
                    else:
                        results.append(str(path))
            return results[:50]
        
        raise ValueError(f"Unknown tool: {name}")
    
    def _get_mime_type(self, path: Path) -> str:
        """Get MIME type based on file extension."""
        ext = path.suffix.lower()
        mime_types = {
            ".py": "text/x-python",
            ".js": "application/javascript",
            ".ts": "application/typescript",
            ".json": "application/json",
            ".md": "text/markdown",
            ".html": "text/html",
            ".css": "text/css",
            ".yaml": "text/yaml",
            ".yml": "text/yaml",
            ".txt": "text/plain",
            ".xml": "application/xml",
        }
        return mime_types.get(ext, "text/plain")
