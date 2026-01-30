#!/usr/bin/env python3
"""
Research MCP Connector
Provides research capabilities through MCP protocol for the SDLC system.
Custom version: No third-party API keys required.
"""

import os
import json
from typing import Dict, List, Optional, Any
from datetime import datetime
from pathlib import Path


class ResearchConnector:
    """
    MCP connector for technical research and knowledge discovery.
    Uses free sources (DuckDuckGo, GitHub, Stack Overflow) via DeepSearch.
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        Initialize Research connector.
        
        Args:
            config: Optional configuration dict
        """
        # NO API KEYS REQUIRED
        self.config = config or {}
        
        # Import DeepSearch for free tools
        from agentic_sdlc.infrastructure.bridge.mcp.connectors.deep_search import DeepSearchConnector
        self.deep_search = DeepSearchConnector()
        
        # Research cache (using local project path)
        self.cache_dir = Path('.brain') / 'research_cache'
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        
    def list_resources(self) -> List[Dict[str, str]]:
        """List available research resources."""
        resources = [
            {
                "uri": "research://web/search",
                "name": "Web Search (Free)",
                "description": "Search the web using DuckDuckGo",
                "mimeType": "application/json"
            },
            {
                "uri": "research://kb/search",
                "name": "Knowledge Base Search",
                "description": "Search local knowledge base",
                "mimeType": "application/json"
            },
            {
                "uri": "research://technical/docs",
                "name": "Technical Documentation",
                "description": "Search technical documentation",
                "mimeType": "application/json"
            },
            {
                "uri": "research://patterns/best-practices",
                "name": "Best Practices",
                "description": "Find best practices and patterns",
                "mimeType": "application/json"
            }
        ]
        return resources
    
    def read_resource(self, uri: str, params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Read a research resource.
        """
        params = params or {}
        
        if uri.startswith("research://web/search"):
            return self._web_search(params.get('query', ''), params)
        elif uri.startswith("research://kb/search"):
            return self._kb_search(params.get('query', ''))
        elif uri.startswith("research://technical/docs"):
            return self._search_docs(params.get('query', ''), params.get('language'))
        elif uri.startswith("research://patterns/best-practices"):
            return self._search_patterns(params.get('topic', ''))
        else:
            return {"error": f"Unknown resource: {uri}"}
    
    def _web_search(self, query: str, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Perform web search using free DuckDuckGo tool.
        """
        if not query:
            return {"error": "Query is required"}
        
        # Check cache first
        cache_key = self._get_cache_key(f"free_web_{query}")
        cached = self._get_cached(cache_key)
        if cached:
            return cached
        
        print(f"  🔍 Querying Free Web Search (DDG) for: {query}")
        
        # Use DeepSearch DDG tool
        search_args = {
            "query": query,
            "num_results": params.get('count', 10)
        }
        
        try:
            ddg_results = self.deep_search.call_tool("ddg_search", search_args)
            
            results = {
                "query": query,
                "sources": ddg_results.get("results", []),
                "timestamp": datetime.now().isoformat(),
                "source_type": "duckduckgo"
            }
            
            # Cache results
            if results["sources"]:
                self._cache_results(cache_key, results)
                
            return results
        except Exception as e:
            return {"error": f"DDG Search failed: {str(e)}", "sources": []}
    
    def _kb_search(self, query: str) -> Dict[str, Any]:
        """Search local knowledge base."""
        # Integration with system KB would happen here
        return {
            "query": query,
            "results": [],
            "message": "Local KB search integrated via brain_cli"
        }
    
    def _search_docs(self, query: str, language: Optional[str] = None) -> Dict[str, Any]:
        """Search technical documentation using free DDG."""
        doc_query = f"{query} documentation"
        if language:
            doc_query += f" {language}"
        
        return self._web_search(doc_query, {"count": 5})
    
    def _search_patterns(self, topic: str) -> Dict[str, Any]:
        """Search for best practices and patterns."""
        pattern_query = f"{topic} best practices design patterns"
        
        # Also try Stack Overflow
        print(f"  🔍 Querying Stack Overflow for patterns: {topic}")
        so_results = self.deep_search.call_tool("stackoverflow_search", {
            "query": f"{topic} best practices",
            "num_results": 5
        })
        
        web_results = self._web_search(pattern_query, {"count": 5})
        
        return {
            "topic": topic,
            "web_findings": web_results.get("sources", []),
            "stackoverflow_findings": so_results.get("results", [])
        }
    
    def _get_cache_key(self, query: str) -> str:
        """Generate cache key from query."""
        import hashlib
        return hashlib.md5(query.encode()).hexdigest()
    
    def _get_cached(self, cache_key: str, max_age_hours: int = 24) -> Optional[Dict[str, Any]]:
        """Get cached results if fresh enough."""
        cache_file = self.cache_dir / f"{cache_key}.json"
        
        if not cache_file.exists():
            return None
        
        # Check age
        age_hours = (datetime.now().timestamp() - cache_file.stat().st_mtime) / 3600
        if age_hours > max_age_hours:
            return None
        
        try:
            with open(cache_file, 'r') as f:
                return json.load(f)
        except Exception:
            return None
    
    def _cache_results(self, cache_key: str, results: Dict[str, Any]) -> None:
        """Cache search results."""
        cache_file = self.cache_dir / f"{cache_key}.json"
        try:
            with open(cache_file, 'w') as f:
                json.dump(results, f, indent=2)
        except Exception:
            pass
    
    def research_task(self, task: str, task_type: str = "general") -> Dict[str, Any]:
        """
        Perform comprehensive research for a task (FREE ONLY).
        """
        results = {
            "task": task,
            "type": task_type,
            "timestamp": datetime.now().isoformat(),
            "findings": []
        }
        
        # 1. Web Search
        web_results = self._web_search(task, {"count": 5})
        if web_results.get("sources"):
            results["findings"].append({
                "source": "web_search",
                "results": web_results["sources"]
            })
        
        # 2. GitHub Search (if relevant)
        if task_type in ["feature", "architecture"]:
            print(f"  🔍 Querying GitHub for role models/patterns: {task}")
            gh_results = self.deep_search.call_tool("github_search", {
                "query": task,
                "search_type": "repositories",
                "num_results": 5
            })
            if gh_results.get("results"):
                results["findings"].append({
                    "source": "github",
                    "results": gh_results["results"]
                })
        
        # 3. Stack Overflow (if relevant)
        if task_type in ["bug", "feature"]:
            print(f"  🔍 Querying Stack Overflow for issues/fixes: {task}")
            so_results = self.deep_search.call_tool("stackoverflow_search", {
                "query": task,
                "num_results": 5
            })
            if so_results.get("results"):
                results["findings"].append({
                    "source": "stackoverflow",
                    "results": so_results["results"]
                })
        
        return results


# MCP Protocol Methods
def list_resources() -> List[Dict[str, str]]:
    """MCP: List available research resources."""
    connector = ResearchConnector()
    return connector.list_resources()


def read_resource(uri: str, params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """MCP: Read a research resource."""
    connector = ResearchConnector()
    return connector.read_resource(uri, params)


def research(task: str, task_type: str = "general") -> Dict[str, Any]:
    """MCP: Perform research for a task."""
    connector = ResearchConnector()
    return connector.research_task(task, task_type)
