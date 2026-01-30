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
        from agentic_sdlc.intelligence.reasoning.research.research_agent import ResearchAgent
    except ImportError:
        print("⚠️  Cannot import research_agent.py")
        print("    Make sure you're running from project root or tools/research/ directory")
        sys.exit(1)


class ResearchAgentMCP(ResearchAgent):
    """Research Agent with MCP integration (Custom, no third-party API keys)"""
    
    def __init__(self):
        super().__init__()
        from agentic_sdlc.infrastructure.bridge.mcp.connectors.research import ResearchConnector
        self.research_mcp = ResearchConnector()
        print("🔌 Custom MCP Research Mode (No API Keys required)")
    
    def research(self, task: str, task_type: str = 'general') -> Dict:
        """Enhanced research with DeepSearch MCP tools"""
        # Run base research (Graph + GitHub)
        results = super().research(task, task_type)
        
        # Add Custom MCP-based research
        print("\n🔌 Querying Custom MCP Tools (DeepSearch)...")
        mcp_results = self._search_mcp(task, task_type)
        results['sources']['mcp_custom'] = mcp_results
        self._print_mcp_results(mcp_results)
        
        return results
    
    def _search_mcp(self, task: str, task_type: str) -> Dict:
        """Search using ResearchConnector (Custom MCP)"""
        try:
            # Use the high-level research_task method from ResearchConnector
            results = self.research_mcp.research_task(task, task_type)
            
            # Map results to expected keys for _print_mcp_results
            mapped_results = {"sources": {}}
            for finding in results.get("findings", []):
                source = finding.get("source")
                if source == "web_search":
                    # Rename snippet to snippet if needed, but DDG scraper uses snippet
                    # mapped_results["sources"]["duckduckgo"] = {"results": finding.get("results", [])}
                    # Actually _print_mcp_results expects duckduckgo
                    mapped_results["sources"]["duckduckgo"] = {"results": finding.get("results", [])}
                elif source == "github":
                    mapped_results["sources"]["github"] = {"results": finding.get("results", [])}
                elif source == "stackoverflow":
                    mapped_results["sources"]["stackoverflow"] = {"results": finding.get("results", [])}
            
            return mapped_results
        except Exception as e:
            print(f"  ⚠️  Research MCP error: {e}")
            return {"error": str(e)}
    
    def _extract_keywords(self, task: str) -> List[str]:
        """Extract keywords from task description"""
        # Simple keyword extraction (can be improved)
        stop_words = {'a', 'an', 'the', 'is', 'are', 'to', 'for', 'in', 'of', 'with', 'on', 'at', 'by'}
        words = task.lower().split()
        return [w for w in words if w.isalnum() and w not in stop_words]
    
    def _print_mcp_results(self, results: Dict):
        """Print DeepSearch results"""
        if "error" in results:
            print(f"  ❌ Error: {results['error']}")
            return

        sources = results.get('sources', {})
        
        # DuckDuckGo
        ddg = sources.get('duckduckgo', {})
        if ddg.get('results'):
            print(f"  ✓ Web Search (DDG): Found {len(ddg['results'])} results")
            for r in ddg['results'][:3]:
                print(f"    • {r['title']}")
                print(f"      {r['url']}")
        
        # GitHub
        gh = sources.get('github', {})
        if gh.get('results'):
            print(f"  ✓ GitHub: Found {len(gh['results'])} results")
            for r in gh['results'][:3]:
                print(f"    • {r.get('name') or r.get('title')}")
                print(f"      {r['url']}")
        
        # Stack Overflow
        so = sources.get('stackoverflow', {})
        if so.get('results'):
            print(f"  ✓ Stack Overflow: Found {len(so['results'])} questions")
            for q in so['results'][:3]:
                print(f"    • {q['title']}")
                print(f"      {q['url']} (Score: {q['score']})")



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

