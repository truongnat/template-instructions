#!/usr/bin/env python3
"""
Research Agent - Auto-research before starting any task

Purpose: Query Local Knowledge Graph, GitHub, and Knowledge Base
         to find relevant information before planning/development/bug fixing
"""

import os
import sys
import json
import argparse
from datetime import datetime
from typing import Dict, List, Optional
from pathlib import Path
import requests
from agentic_sdlc.intelligence.reasoning.knowledge_graph.graph_brain import LocalKnowledgeGraph

class ResearchAgent:
    """Agent to research before starting tasks"""
    
    def __init__(self):
        self.kg = LocalKnowledgeGraph()
        self.github_token = os.getenv('GITHUB_TOKEN')
        self.github_repo = os.getenv('GITHUB_REPO')
        self.project_root = Path.cwd()
    
    def research(self, task: str, task_type: str = 'general') -> Dict:
        """Main research method"""
        print(f"\n🔍 RESEARCH AGENT - Starting Research: {task}")
        
        results = {
            'task': task,
            'task_type': task_type,
            'timestamp': datetime.now().isoformat(),
            'sources': {}
        }
        
        # 1. Search Local Knowledge Graph
        print("🧠 Querying Local Knowledge Graph...")
        graph_results = self.kg.find_nodes(query=task, limit=10)
        results['sources']['graph'] = graph_results
        
        # 2. Search GitHub Issues (Simple search via requests)
        if self.github_token and self.github_repo:
            print("🐙 Searching GitHub Issues...")
            github_results = self._search_github(task)
            results['sources']['github'] = github_results
            
        return results
    
    def _search_github(self, query: str) -> List[Dict]:
        url = f'https://api.github.com/search/issues'
        headers = {'Authorization': f'token {self.github_token}'}
        params = {'q': f'{query} repo:{self.github_repo} type:issue'}
        try:
            resp = requests.get(url, headers=headers, params=params)
            if resp.status_code == 200:
                return resp.json().get('items', [])[:5]
        except:
            pass
        return []

    def close(self):
        self.kg.close()

def main():
    parser = argparse.ArgumentParser(description='Research Agent')
    parser.add_argument('--task', required=True, help='Task description')
    parser.add_argument('--type', default='general', help='Task type')
    args = parser.parse_args()
    
    agent = ResearchAgent()
    results = agent.research(args.task, args.type)
    print(f"Research complete. Found {len(results['sources'].get('graph', []))} graph nodes.")
    agent.close()

if __name__ == '__main__':
    main()
