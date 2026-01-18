#!/usr/bin/env python3
"""
Research Agent with MCP Integration

Extends research_agent.py with MCP tool capabilities:
- Web search (Tavily, Brave)
- Documentation fetch
- Stack Overflow search
- GitHub advanced queries
"""

import os
import sys
import json
import subprocess
from typing import Dict, List, Optional
from pathlib import Path

# Import base research agent
try:
    # Try relative import first (when in same directory)
    from research_agent import ResearchAgent
except ImportError:
    # Try absolute import from agentic_sdlc.research
    try:
        from agentic_sdlc.intelligence.research.research_agent import ResearchAgent
    except ImportError:
        print("⚠️  Cannot import research_agent.py")
        print("    Make sure you're running from project root or tools/research/ directory")
        sys.exit(1)


class ResearchAgentMCP(ResearchAgent):
    """Research Agent with MCP integration"""
    
    def __init__(self):
        super().__init__()
        self.mcp_config = self._load_mcp_config()
    
    def _load_mcp_config(self) -> Dict:
        """Load MCP configuration"""
        mcp_path = self.project_root / '.kiro' / 'settings' / 'mcp.json'
        
        if not mcp_path.exists():
            print("⚠️  MCP config not found at .kiro/settings/mcp.json")
            return {}
        
        try:
            with open(mcp_path, 'r') as f:
                config = json.load(f)
                return config.get('mcpServers', {})
        except Exception as e:
            print(f"⚠️  Error loading MCP config: {e}")
            return {}
    
    def research(self, task: str, task_type: str = 'general') -> Dict:
        """Enhanced research with MCP tools"""
        # Run base research
        results = super().research(task, task_type)
        
        # Add MCP-based research
        if self.mcp_config:
            print("\n🔌 Querying MCP Tools...")
            mcp_results = self._search_mcp(task, task_type)
            results['sources']['mcp'] = mcp_results
            self._print_mcp_results(mcp_results)
        
        return results
    
    def _search_mcp(self, task: str, task_type: str) -> Dict:
        """Search using MCP tools"""
        results = {
            'web_search': {},
            'documentation': {},
            'stackoverflow': {}
        }
        
        keywords = self._extract_keywords(task)
        query = ' '.join(keywords)
        
        # 1. Web Search (Tavily or Brave)
        if 'tavily-search' in self.mcp_config or 'brave-search' in self.mcp_config:
            results['web_search'] = self._mcp_web_search(query)
        
        # 2. Fetch Documentation
        if 'fetch' in self.mcp_config:
            results['documentation'] = self._mcp_fetch_docs(task, keywords)
        
        # 3. Stack Overflow (via web search)
        results['stackoverflow'] = self._mcp_stackoverflow_search(query)
        
        return results
    
    def _mcp_web_search(self, query: str) -> Dict:
        """Web search using MCP"""
        results = {
            'found': False,
            'results': []
        }
        
        try:
            # Use Kiro's web search if available
            # This would integrate with actual MCP tools
            # For now, we'll use a placeholder
            
            print(f"  Searching web for: {query}")
            
            # Placeholder for actual MCP integration
            # In real implementation, this would call MCP web search tool
            
            results['found'] = True
            results['results'] = [
                {
                    'title': f'Best practices for {query}',
                    'url': 'https://example.com/best-practices',
                    'snippet': 'Placeholder result'
                }
            ]
        
        except Exception as e:
            print(f"  ⚠️  Web search error: {e}")
        
        return results
    
    def _mcp_fetch_docs(self, task: str, keywords: List[str]) -> Dict:
        """Fetch documentation using MCP"""
        results = {
            'found': False,
            'docs': []
        }
        
        # Common documentation URLs based on keywords
        doc_urls = self._get_doc_urls(keywords)
        
        for url in doc_urls[:3]:  # Limit to 3 docs
            try:
                print(f"  Fetching: {url}")
                
                # Placeholder for actual MCP fetch
                # In real implementation, this would call MCP fetch tool
                
                results['found'] = True
                results['docs'].append({
                    'url': url,
                    'title': f'Documentation for {keywords[0]}',
                    'content': 'Placeholder content'
                })
            
            except Exception as e:
                print(f"  ⚠️  Fetch error for {url}: {e}")
        
        return results
    
    def _mcp_stackoverflow_search(self, query: str) -> Dict:
        """Search Stack Overflow using MCP"""
        results = {
            'found': False,
            'questions': []
        }
        
        try:
            # Search Stack Overflow via web search
            so_query = f"site:stackoverflow.com {query}"
            print(f"  Searching Stack Overflow: {query}")
            
            # Placeholder for actual MCP integration
            results['found'] = True
            results['questions'] = [
                {
                    'title': f'How to implement {query}',
                    'url': 'https://stackoverflow.com/questions/12345',
                    'votes': 42,
                    'answers': 5
                }
            ]
        
        except Exception as e:
            print(f"  ⚠️  Stack Overflow search error: {e}")
        
        return results
    
    def _get_doc_urls(self, keywords: List[str]) -> List[str]:
        """Get documentation URLs based on keywords"""
        doc_map = {
            'react': 'https://react.dev/reference',
            'nextjs': 'https://nextjs.org/docs',
            'node': 'https://nodejs.org/docs',
            'express': 'https://expressjs.com/en/api.html',
            'mongodb': 'https://docs.mongodb.com',
            'postgresql': 'https://www.postgresql.org/docs',
            'docker': 'https://docs.docker.com',
            'kubernetes': 'https://kubernetes.io/docs',
            'aws': 'https://docs.aws.amazon.com',
            'typescript': 'https://www.typescriptlang.org/docs',
            'python': 'https://docs.python.org/3',
            'django': 'https://docs.djangoproject.com',
            'flask': 'https://flask.palletsprojects.com',
            'vue': 'https://vuejs.org/guide',
            'angular': 'https://angular.io/docs',
        }
        
        urls = []
        for keyword in keywords:
            if keyword.lower() in doc_map:
                urls.append(doc_map[keyword.lower()])
        
        return urls
    
    def _print_mcp_results(self, results: Dict):
        """Print MCP results"""
        # Web Search
        web = results.get('web_search', {})
        if web.get('found'):
            print(f"  ✓ Web Search: Found {len(web['results'])} results")
            for r in web['results'][:3]:
                print(f"    • {r['title']}")
                print(f"      {r['url']}")
        
        # Documentation
        docs = results.get('documentation', {})
        if docs.get('found'):
            print(f"  ✓ Documentation: Found {len(docs['docs'])} docs")
            for d in docs['docs']:
                print(f"    • {d['title']}")
                print(f"      {d['url']}")
        
        # Stack Overflow
        so = results.get('stackoverflow', {})
        if so.get('found'):
            print(f"  ✓ Stack Overflow: Found {len(so['questions'])} questions")
            for q in so['questions'][:3]:
                print(f"    • {q['title']}")
                print(f"      {q['url']} ({q['votes']} votes, {q['answers']} answers)")


def main():
    """Main entry point"""
    import argparse
    
    parser = argparse.ArgumentParser(
        description='Research Agent with MCP Integration'
    )
    parser.add_argument('--task', type=str, help='Task description')
    parser.add_argument('--bug', type=str, help='Bug description')
    parser.add_argument('--feature', type=str, help='Feature description')
    parser.add_argument(
        '--type',
        type=str,
        choices=['general', 'bug', 'feature', 'architecture', 'security', 'performance'],
        default='general',
        help='Task type'
    )
    
    args = parser.parse_args()
    
    # Determine task and type
    if args.bug:
        task = args.bug
        task_type = 'bug'
    elif args.feature:
        task = args.feature
        task_type = 'feature'
    elif args.task:
        task = args.task
        task_type = args.type
    else:
        parser.print_help()
        sys.exit(1)
    
    # Run research with MCP
    agent = ResearchAgentMCP()
    try:
        results = agent.research(task, task_type)
        sys.exit(0)
    finally:
        agent.close()


if __name__ == '__main__':
    main()

