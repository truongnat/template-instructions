"""
GitHub Connector

MCP connector for GitHub API access.
"""

import os
from pathlib import Path
from typing import Any, Dict, List, Optional
from urllib.request import urlopen, Request
from urllib.error import HTTPError
import json

# Import from parent
import sys
sys.path.insert(0, str(Path(__file__).parent.parent))
from protocol import MCPConnector, MCPResource, MCPTool


class GitHubConnector(MCPConnector):
    """
    Connector for GitHub API access.
    
    Provides access to repositories, issues, PRs, and more.
    """
    
    API_BASE = "https://api.github.com"
    
    def __init__(self, token: Optional[str] = None, owner: Optional[str] = None, repo: Optional[str] = None):
        self.token = token or os.getenv("GITHUB_TOKEN")
        self.owner = owner
        self.repo = repo
    
    @property
    def name(self) -> str:
        return "github"
    
    def _make_request(self, endpoint: str, method: str = "GET", data: Optional[Dict] = None) -> Dict:
        """Make an authenticated request to GitHub API."""
        url = f"{self.API_BASE}{endpoint}"
        headers = {
            "Accept": "application/vnd.github.v3+json",
            "User-Agent": "Agentic-SDLC-MCP"
        }
        
        if self.token:
            headers["Authorization"] = f"token {self.token}"
        
        request_data = json.dumps(data).encode() if data else None
        req = Request(url, data=request_data, headers=headers, method=method)
        
        try:
            with urlopen(req, timeout=30) as response:
                return json.loads(response.read().decode())
        except HTTPError as e:
            if e.code == 404:
                return {"error": "Not found"}
            raise
    
    def list_resources(self) -> List[MCPResource]:
        """List GitHub resources."""
        resources = []
        
        if self.owner and self.repo:
            # List repository contents
            try:
                contents = self._make_request(f"/repos/{self.owner}/{self.repo}/contents")
                if isinstance(contents, list):
                    for item in contents[:20]:
                        resources.append(MCPResource(
                            uri=f"github://{self.owner}/{self.repo}/{item['path']}",
                            name=item['name'],
                            description=f"GitHub: {item['type']}",
                            mime_type="text/plain" if item['type'] == 'file' else "application/directory",
                            metadata={
                                "type": item['type'],
                                "sha": item.get('sha'),
                                "size": item.get('size', 0)
                            }
                        ))
            except Exception:
                pass
        
        return resources
    
    def read_resource(self, uri: str) -> Optional[str]:
        """Read a GitHub resource."""
        if not uri.startswith("github://"):
            return None
        
        parts = uri[9:].split("/")
        if len(parts) < 3:
            return None
        
        owner = parts[0]
        repo = parts[1]
        path = "/".join(parts[2:])
        
        try:
            content = self._make_request(f"/repos/{owner}/{repo}/contents/{path}")
            if content.get("encoding") == "base64":
                import base64
                return base64.b64decode(content["content"]).decode('utf-8')
        except Exception:
            pass
        
        return None
    
    def list_tools(self) -> List[MCPTool]:
        """List available GitHub tools."""
        return [
            MCPTool(
                name="gh_list_repos",
                description="List repositories for a user/org",
                input_schema={
                    "type": "object",
                    "properties": {
                        "owner": {"type": "string", "description": "Owner (user or org)"},
                        "type": {"type": "string", "description": "Type: all, owner, member"}
                    },
                    "required": ["owner"]
                }
            ),
            MCPTool(
                name="gh_list_issues",
                description="List issues for a repository",
                input_schema={
                    "type": "object",
                    "properties": {
                        "owner": {"type": "string"},
                        "repo": {"type": "string"},
                        "state": {"type": "string", "description": "open, closed, all"}
                    },
                    "required": ["owner", "repo"]
                }
            ),
            MCPTool(
                name="gh_get_issue",
                description="Get a specific issue",
                input_schema={
                    "type": "object",
                    "properties": {
                        "owner": {"type": "string"},
                        "repo": {"type": "string"},
                        "issue_number": {"type": "integer"}
                    },
                    "required": ["owner", "repo", "issue_number"]
                }
            ),
            MCPTool(
                name="gh_list_prs",
                description="List pull requests",
                input_schema={
                    "type": "object",
                    "properties": {
                        "owner": {"type": "string"},
                        "repo": {"type": "string"},
                        "state": {"type": "string"}
                    },
                    "required": ["owner", "repo"]
                }
            ),
            MCPTool(
                name="gh_search_code",
                description="Search code in GitHub",
                input_schema={
                    "type": "object",
                    "properties": {
                        "query": {"type": "string", "description": "Search query"},
                        "repo": {"type": "string", "description": "Optional: limit to repo"}
                    },
                    "required": ["query"]
                }
            )
        ]
    
    def call_tool(self, name: str, arguments: Dict) -> Any:
        """Execute a GitHub tool."""
        if name == "gh_list_repos":
            owner = arguments["owner"]
            return self._make_request(f"/users/{owner}/repos?per_page=20")
        
        elif name == "gh_list_issues":
            owner = arguments["owner"]
            repo = arguments["repo"]
            state = arguments.get("state", "open")
            return self._make_request(f"/repos/{owner}/{repo}/issues?state={state}&per_page=20")
        
        elif name == "gh_get_issue":
            owner = arguments["owner"]
            repo = arguments["repo"]
            issue_number = arguments["issue_number"]
            return self._make_request(f"/repos/{owner}/{repo}/issues/{issue_number}")
        
        elif name == "gh_list_prs":
            owner = arguments["owner"]
            repo = arguments["repo"]
            state = arguments.get("state", "open")
            return self._make_request(f"/repos/{owner}/{repo}/pulls?state={state}&per_page=20")
        
        elif name == "gh_search_code":
            query = arguments["query"]
            repo = arguments.get("repo")
            search_query = f"{query}+repo:{repo}" if repo else query
            return self._make_request(f"/search/code?q={search_query}")
        
        raise ValueError(f"Unknown tool: {name}")
