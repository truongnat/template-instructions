"""
Deep Search MCP Connector

Custom MCP connector for deep web search focused on technical research.
Uses free APIs without requiring third-party AI services:
- DuckDuckGo (no API key required)
- GitHub API (optional token for higher rate limits)
- Stack Overflow API (public, no key required)
- Custom web scraping for documentation sites
"""

import os
import sys
import json
import hashlib
import html
import re
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple
from datetime import datetime, timedelta
from urllib.request import urlopen, Request
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode, quote_plus

# Import from parent
sys.path.insert(0, str(Path(__file__).parent.parent))
from protocol import MCPConnector, MCPResource, MCPTool


class DeepSearchConnector(MCPConnector):
    """
    Deep web search connector for technical research.
    
    Provides tools for:
    - DuckDuckGo web search (no API key)
    - GitHub code/repo search
    - Stack Overflow Q&A search
    - Documentation site scraping
    - Aggregated multi-source search
    """
    
    # Technical domains for focused search
    TECHNICAL_DOMAINS = [
        "github.com",
        "stackoverflow.com", 
        "dev.to",
        "medium.com",
        "docs.python.org",
        "developer.mozilla.org",
        "react.dev",
        "nextjs.org",
        "kubernetes.io",
        "docker.com"
    ]
    
    # User agent for requests
    USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
    
    def __init__(
        self,
        github_token: Optional[str] = None,
        cache_enabled: bool = True,
        cache_ttl_hours: int = 24
    ):
        self.github_token = github_token or os.getenv("GITHUB_TOKEN")
        self.cache_enabled = cache_enabled
        self.cache_ttl_hours = cache_ttl_hours
        self._cache: Dict[str, Dict] = {}
        
        # API endpoints
        self.ddg_url = "https://html.duckduckgo.com/html/"
        self.github_api = "https://api.github.com"
        self.stackoverflow_api = "https://api.stackexchange.com/2.3"
    
    @property
    def name(self) -> str:
        return "deep_search"
    
    def _get_cache_key(self, query: str, source: str) -> str:
        """Generate cache key for a query."""
        return hashlib.md5(f"{source}:{query}".encode()).hexdigest()
    
    def _get_cached(self, key: str) -> Optional[Dict]:
        """Get cached result if valid."""
        if not self.cache_enabled:
            return None
        
        if key in self._cache:
            cached = self._cache[key]
            expires = cached.get("expires")
            if expires and datetime.fromisoformat(expires) > datetime.now():
                return cached.get("data")
        return None
    
    def _set_cache(self, key: str, data: Dict):
        """Cache a result."""
        if self.cache_enabled:
            self._cache[key] = {
                "data": data,
                "expires": (datetime.now() + timedelta(hours=self.cache_ttl_hours)).isoformat()
            }
    
    def _make_request(
        self,
        url: str,
        method: str = "GET",
        data: Optional[Dict] = None,
        headers: Optional[Dict] = None,
        timeout: int = 30,
        is_form: bool = False
    ) -> Tuple[int, str]:
        """Make an HTTP request and return (status_code, content)."""
        full_headers = {"User-Agent": self.USER_AGENT}
        if headers:
            full_headers.update(headers)
        
        if is_form and data:
            full_headers["Content-Type"] = "application/x-www-form-urlencoded"
            request_data = urlencode(data).encode()
        elif data:
            full_headers["Content-Type"] = "application/json"
            request_data = json.dumps(data).encode()
        else:
            request_data = None
        
        req = Request(url, data=request_data, headers=full_headers, method=method)
        
        try:
            with urlopen(req, timeout=timeout) as response:
                return response.status, response.read().decode("utf-8", errors="ignore")
        except HTTPError as e:
            return e.code, str(e)
        except URLError as e:
            return 0, str(e.reason)
        except Exception as e:
            return 0, str(e)
    
    # --- Resource Methods ---
    
    def list_resources(self) -> List[MCPResource]:
        """List available research resources."""
        return [
            MCPResource(
                uri="deep://duckduckgo/search",
                name="DuckDuckGo Search",
                description="Web search via DuckDuckGo (no API key required)",
                mime_type="application/json"
            ),
            MCPResource(
                uri="deep://github/search",
                name="GitHub Search",
                description="Code and repository search via GitHub API",
                mime_type="application/json"
            ),
            MCPResource(
                uri="deep://stackoverflow/search",
                name="Stack Overflow Search",
                description="Q&A search via Stack Exchange API",
                mime_type="application/json"
            )
        ]
    
    def read_resource(self, uri: str) -> Optional[str]:
        """Read resource info."""
        if not uri.startswith("deep://"):
            return None
        
        return json.dumps({
            "uri": uri,
            "status": "available",
            "github_configured": bool(self.github_token)
        })
    
    # --- Tool Methods ---
    
    def list_tools(self) -> List[MCPTool]:
        """List available deep search tools."""
        return [
            MCPTool(
                name="deep_search",
                description="Aggregated search across DuckDuckGo, GitHub, and Stack Overflow",
                input_schema={
                    "type": "object",
                    "properties": {
                        "query": {"type": "string", "description": "Search query"},
                        "num_results": {"type": "integer", "description": "Max results per source (default: 5)"},
                        "sources": {
                            "type": "array",
                            "items": {"type": "string", "enum": ["ddg", "github", "stackoverflow"]},
                            "description": "Sources to search (default: all)"
                        }
                    },
                    "required": ["query"]
                }
            ),
            MCPTool(
                name="ddg_search",
                description="Search the web via DuckDuckGo",
                input_schema={
                    "type": "object",
                    "properties": {
                        "query": {"type": "string", "description": "Search query"},
                        "num_results": {"type": "integer", "description": "Max results (default: 10)"},
                        "region": {"type": "string", "description": "Region code (default: wt-wt for worldwide)"}
                    },
                    "required": ["query"]
                }
            ),
            MCPTool(
                name="github_search",
                description="Search GitHub repositories and code",
                input_schema={
                    "type": "object",
                    "properties": {
                        "query": {"type": "string", "description": "Search query"},
                        "search_type": {"type": "string", "enum": ["repositories", "code", "issues"], "description": "Type (default: repositories)"},
                        "num_results": {"type": "integer", "description": "Max results (default: 10)"},
                        "language": {"type": "string", "description": "Filter by programming language"},
                        "sort": {"type": "string", "enum": ["stars", "forks", "updated", "best-match"]}
                    },
                    "required": ["query"]
                }
            ),
            MCPTool(
                name="stackoverflow_search",
                description="Search Stack Overflow questions and answers",
                input_schema={
                    "type": "object",
                    "properties": {
                        "query": {"type": "string", "description": "Search query"},
                        "num_results": {"type": "integer", "description": "Max results (default: 10)"},
                        "tags": {"type": "array", "items": {"type": "string"}, "description": "Filter by tags"},
                        "sort": {"type": "string", "enum": ["relevance", "votes", "creation", "activity"]}
                    },
                    "required": ["query"]
                }
            ),
            MCPTool(
                name="fetch_content",
                description="Fetch and extract content from a URL",
                input_schema={
                    "type": "object",
                    "properties": {
                        "url": {"type": "string", "description": "URL to fetch"},
                        "extract_code": {"type": "boolean", "description": "Extract code blocks (default: true)"}
                    },
                    "required": ["url"]
                }
            )
        ]
    
    def call_tool(self, name: str, arguments: Dict) -> Any:
        """Execute a deep search tool."""
        if name == "deep_search":
            return self._deep_search(arguments)
        elif name == "ddg_search":
            return self._ddg_search(arguments)
        elif name == "github_search":
            return self._github_search(arguments)
        elif name == "stackoverflow_search":
            return self._stackoverflow_search(arguments)
        elif name == "fetch_content":
            return self._fetch_content(arguments)
        else:
            raise ValueError(f"Unknown tool: {name}")
    
    # --- Search Implementations ---
    
    def _deep_search(self, args: Dict) -> Dict:
        """Aggregated search across all sources."""
        query = args["query"]
        num_results = args.get("num_results", 5)
        sources = args.get("sources", ["ddg", "github", "stackoverflow"])
        
        results = {
            "query": query,
            "timestamp": datetime.now().isoformat(),
            "sources": {}
        }
        
        if "ddg" in sources:
            results["sources"]["duckduckgo"] = self._ddg_search({
                "query": query,
                "num_results": num_results
            })
        
        if "github" in sources:
            results["sources"]["github"] = self._github_search({
                "query": query,
                "num_results": num_results
            })
        
        if "stackoverflow" in sources:
            results["sources"]["stackoverflow"] = self._stackoverflow_search({
                "query": query,
                "num_results": num_results
            })
        
        # Summary
        total = sum(len(s.get("results", [])) for s in results["sources"].values())
        results["summary"] = {
            "total_results": total,
            "sources_queried": list(results["sources"].keys())
        }
        
        return results
    
    def _ddg_search(self, args: Dict) -> Dict:
        """DuckDuckGo web search (HTML scraping - no API key needed)."""
        query = args["query"]
        num_results = args.get("num_results", 10)
        
        cache_key = self._get_cache_key(query, "ddg")
        cached = self._get_cached(cache_key)
        if cached:
            cached["from_cache"] = True
            return cached
        
        # POST to DuckDuckGo HTML endpoint
        data = {"q": query, "b": ""}
        status, content = self._make_request(self.ddg_url, "POST", data, is_form=True)
        
        if status != 200:
            return {"error": f"DuckDuckGo error: {status}", "results": []}
        
        # Parse HTML results
        results = self._parse_ddg_html(content, num_results)
        
        result = {
            "query": query,
            "results": results,
            "count": len(results),
            "from_cache": False
        }
        
        self._set_cache(cache_key, result)
        return result
    
    def _parse_ddg_html(self, html_content: str, max_results: int) -> List[Dict]:
        """Parse DuckDuckGo HTML results."""
        results = []
        
        # Extract result blocks using regex (no external libs)
        # Pattern matches: <a class="result__a" href="...">title</a>
        link_pattern = r'<a[^>]+class="result__a"[^>]+href="([^"]+)"[^>]*>(.+?)</a>'
        snippet_pattern = r'<a[^>]+class="result__snippet"[^>]*>(.+?)</a>'
        
        links = re.findall(link_pattern, html_content, re.DOTALL)
        snippets = re.findall(snippet_pattern, html_content, re.DOTALL)
        
        for i, (url, title) in enumerate(links[:max_results]):
            # Clean HTML entities
            clean_title = html.unescape(re.sub(r'<[^>]+>', '', title)).strip()
            clean_snippet = ""
            if i < len(snippets):
                clean_snippet = html.unescape(re.sub(r'<[^>]+>', '', snippets[i])).strip()
            
            # Skip ads and internal DDG links
            if "duckduckgo.com" in url or not url.startswith("http"):
                continue
            
            results.append({
                "title": clean_title,
                "url": url,
                "snippet": clean_snippet
            })
        
        return results[:max_results]
    
    def _github_search(self, args: Dict) -> Dict:
        """GitHub repository/code search."""
        query = args["query"]
        search_type = args.get("search_type", "repositories")
        num_results = args.get("num_results", 10)
        language = args.get("language")
        sort = args.get("sort", "best-match")
        
        cache_key = self._get_cache_key(f"{query}:{search_type}:{language}", "github")
        cached = self._get_cached(cache_key)
        if cached:
            cached["from_cache"] = True
            return cached
        
        # Build query
        search_query = query
        if language:
            search_query += f" language:{language}"
        
        params = {
            "q": search_query,
            "per_page": min(num_results, 30),
            "sort": sort if sort != "best-match" else ""
        }
        
        url = f"{self.github_api}/search/{search_type}?{urlencode({k: v for k, v in params.items() if v})}"
        
        headers = {"Accept": "application/vnd.github.v3+json"}
        if self.github_token:
            headers["Authorization"] = f"token {self.github_token}"
        
        status, content = self._make_request(url, headers=headers)
        
        if status != 200:
            return {"error": f"GitHub API error: {status}", "results": []}
        
        try:
            data = json.loads(content)
        except json.JSONDecodeError:
            return {"error": "Invalid JSON response", "results": []}
        
        # Parse results based on type
        results = []
        for item in data.get("items", [])[:num_results]:
            if search_type == "repositories":
                results.append({
                    "name": item.get("full_name"),
                    "description": item.get("description", ""),
                    "url": item.get("html_url"),
                    "stars": item.get("stargazers_count", 0),
                    "language": item.get("language"),
                    "topics": item.get("topics", [])
                })
            elif search_type == "code":
                results.append({
                    "name": item.get("name"),
                    "path": item.get("path"),
                    "repository": item.get("repository", {}).get("full_name"),
                    "url": item.get("html_url")
                })
            elif search_type == "issues":
                results.append({
                    "title": item.get("title"),
                    "url": item.get("html_url"),
                    "state": item.get("state"),
                    "comments": item.get("comments", 0)
                })
        
        result = {
            "query": query,
            "search_type": search_type,
            "results": results,
            "total_count": data.get("total_count", 0),
            "from_cache": False
        }
        
        self._set_cache(cache_key, result)
        return result
    
    def _stackoverflow_search(self, args: Dict) -> Dict:
        """Stack Overflow Q&A search."""
        query = args["query"]
        num_results = args.get("num_results", 10)
        tags = args.get("tags", [])
        sort = args.get("sort", "relevance")
        
        cache_key = self._get_cache_key(f"{query}:{','.join(tags)}", "stackoverflow")
        cached = self._get_cached(cache_key)
        if cached:
            cached["from_cache"] = True
            return cached
        
        params = {
            "order": "desc",
            "sort": sort,
            "intitle": query,
            "site": "stackoverflow",
            "pagesize": min(num_results, 30),
            "filter": "withbody"
        }
        
        if tags:
            params["tagged"] = ";".join(tags)
        
        url = f"{self.stackoverflow_api}/search?{urlencode(params)}"
        status, content = self._make_request(url)
        
        if status != 200:
            return {"error": f"Stack Overflow API error: {status}", "results": []}
        
        try:
            data = json.loads(content)
        except json.JSONDecodeError:
            return {"error": "Invalid JSON response", "results": []}
        
        results = []
        for item in data.get("items", [])[:num_results]:
            results.append({
                "title": html.unescape(item.get("title", "")),
                "url": item.get("link"),
                "score": item.get("score", 0),
                "answer_count": item.get("answer_count", 0),
                "is_answered": item.get("is_answered", False),
                "tags": item.get("tags", []),
                "view_count": item.get("view_count", 0)
            })
        
        result = {
            "query": query,
            "results": results,
            "has_more": data.get("has_more", False),
            "quota_remaining": data.get("quota_remaining"),
            "from_cache": False
        }
        
        self._set_cache(cache_key, result)
        return result
    
    def _fetch_content(self, args: Dict) -> Dict:
        """Fetch and extract content from a URL."""
        url = args["url"]
        extract_code = args.get("extract_code", True)
        
        status, content = self._make_request(url, timeout=15)
        
        if status != 200:
            return {"error": f"Fetch error: {status}", "url": url}
        
        # Extract title
        title_match = re.search(r'<title[^>]*>(.+?)</title>', content, re.IGNORECASE | re.DOTALL)
        title = html.unescape(title_match.group(1).strip()) if title_match else ""
        
        # Extract main text content (basic extraction)
        # Remove scripts, styles, and HTML tags
        clean = re.sub(r'<script[^>]*>.*?</script>', '', content, flags=re.DOTALL | re.IGNORECASE)
        clean = re.sub(r'<style[^>]*>.*?</style>', '', clean, flags=re.DOTALL | re.IGNORECASE)
        clean = re.sub(r'<[^>]+>', ' ', clean)
        clean = html.unescape(clean)
        clean = re.sub(r'\s+', ' ', clean).strip()
        
        result = {
            "url": url,
            "title": title,
            "content": clean[:5000],  # Limit content length
            "content_length": len(clean)
        }
        
        # Extract code blocks if requested
        if extract_code:
            code_blocks = []
            # Match <pre><code>...</code></pre> or <code>...</code>
            code_pattern = r'<(?:pre[^>]*>)?<code[^>]*>(.+?)</code>(?:</pre>)?'
            for match in re.findall(code_pattern, content, re.DOTALL | re.IGNORECASE):
                code = html.unescape(re.sub(r'<[^>]+>', '', match)).strip()
                if len(code) > 20:  # Skip tiny snippets
                    code_blocks.append(code[:1000])  # Limit each block
            result["code_blocks"] = code_blocks[:10]  # Max 10 blocks
        
        return result
    
    def get_status(self) -> Dict:
        """Get connector status."""
        return {
            "name": self.name,
            "github_configured": bool(self.github_token),
            "cache_enabled": self.cache_enabled,
            "cache_entries": len(self._cache),
            "tools_available": len(self.list_tools()),
            "sources": ["DuckDuckGo", "GitHub", "Stack Overflow"]
        }


# CLI for testing
def main():
    """CLI entry point for testing."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Deep Search MCP Connector")
    parser.add_argument("--status", action="store_true", help="Show connector status")
    parser.add_argument("--list-tools", action="store_true", help="List available tools")
    parser.add_argument("--search", type=str, help="Run aggregated deep search")
    parser.add_argument("--ddg", type=str, help="Search DuckDuckGo")
    parser.add_argument("--github", type=str, help="Search GitHub")
    parser.add_argument("--stackoverflow", type=str, help="Search Stack Overflow")
    parser.add_argument("--fetch", type=str, help="Fetch URL content")
    
    args = parser.parse_args()
    connector = DeepSearchConnector()
    
    if args.status:
        print(json.dumps(connector.get_status(), indent=2))
    
    elif args.list_tools:
        for tool in connector.list_tools():
            print(f"- {tool.name}: {tool.description}")
    
    elif args.search:
        result = connector.call_tool("deep_search", {"query": args.search})
        print(json.dumps(result, indent=2))
    
    elif args.ddg:
        result = connector.call_tool("ddg_search", {"query": args.ddg})
        print(json.dumps(result, indent=2))
    
    elif args.github:
        result = connector.call_tool("github_search", {"query": args.github})
        print(json.dumps(result, indent=2))
    
    elif args.stackoverflow:
        result = connector.call_tool("stackoverflow_search", {"query": args.stackoverflow})
        print(json.dumps(result, indent=2))
    
    elif args.fetch:
        result = connector.call_tool("fetch_content", {"url": args.fetch})
        print(json.dumps(result, indent=2))
    
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
