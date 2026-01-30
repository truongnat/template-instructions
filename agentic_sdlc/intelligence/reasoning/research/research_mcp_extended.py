#!/usr/bin/env python3
"""
Research Agent with Full MCP Integration

Real API calls to:
- Tavily Search API
- Brave Search API  
- GitHub API
- Stack Overflow API
- Documentation sites
"""

import os
import sys
import json
import requests
from typing import Dict, List, Optional
from pathlib import Path
from datetime import datetime

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


class ResearchAgentMCPExtended(ResearchAgent):
    """Research Agent with full MCP integration"""
    
    def __init__(self):
        super().__init__()
        
        # API Keys
        self.tavily_api_key = os.getenv('TAVILY_API_KEY')
        self.brave_api_key = os.getenv('BRAVE_API_KEY')
        self.stackoverflow_key = os.getenv('STACKOVERFLOW_KEY')
        
        # API Endpoints
        self.tavily_url = 'https://api.tavily.com/search'
        self.brave_url = 'https://api.search.brave.com/res/v1/web/search'
        self.stackoverflow_url = 'https://api.stackexchange.com/2.3/search'
        
        print(f"🔌 MCP Extended Mode")
        print(f"  Tavily: {'✓' if self.tavily_api_key else '✗'}")
        print(f"  Brave: {'✓' if self.brave_api_key else '✗'}")
        print(f"  GitHub: {'✓' if self.github_token else '✗'}")
        print(f"  Stack Overflow: {'✓' if self.stackoverflow_key else '✗'}")
    
    def research(self, task: str, task_type: str = 'general') -> Dict:
        """Enhanced research with real MCP API calls"""
        # Run base research
        results = super().research(task, task_type)
        
        # Add MCP-based research
        print("\n🔌 Querying External APIs via MCP...")
        mcp_results = self._search_mcp_extended(task, task_type)
        results['sources']['mcp_extended'] = mcp_results
        self._print_mcp_extended_results(mcp_results)
        
        # Update summary with MCP findings
        self._update_summary_with_mcp(results, mcp_results)
        
        return results
    
    def _search_mcp_extended(self, task: str, task_type: str) -> Dict:
        """Search using real MCP APIs"""
        results = {
            'tavily_search': {},
            'brave_search': {},
            'stackoverflow': {},
            'github_advanced': {},
            'documentation': {}
        }
        
        keywords = self._extract_keywords(task)
        query = ' '.join(keywords)
        
        # 1. Tavily Search (AI-powered search)
        if self.tavily_api_key:
            results['tavily_search'] = self._tavily_search(query, task_type)
        
        # 2. Brave Search (Privacy-focused)
        if self.brave_api_key:
            results['brave_search'] = self._brave_search(query)
        
        # 3. Stack Overflow API
        results['stackoverflow'] = self._stackoverflow_search(query)
        
        # 4. GitHub Advanced Search
        if self.github_token:
            results['github_advanced'] = self._github_advanced_search(query, task_type)
        
        # 5. Documentation Fetch
        results['documentation'] = self._fetch_documentation(keywords)
        
        return results
    
    def _tavily_search(self, query: str, task_type: str) -> Dict:
        """Tavily AI Search API"""
        results = {
            'found': False,
            'results': [],
            'answer': None
        }
        
        try:
            print(f"  🔍 Tavily Search: {query}")
            
            headers = {
                'Content-Type': 'application/json'
            }
            
            payload = {
                'api_key': self.tavily_api_key,
                'query': query,
                'search_depth': 'advanced',
                'include_answer': True,
                'include_domains': self._get_trusted_domains(task_type),
                'max_results': 5
            }
            
            response = requests.post(
                self.tavily_url,
                headers=headers,
                json=payload,
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                
                # Extract answer
                if 'answer' in data:
                    results['answer'] = data['answer']
                
                # Extract results
                for item in data.get('results', []):
                    results['results'].append({
                        'title': item.get('title', ''),
                        'url': item.get('url', ''),
                        'content': item.get('content', ''),
                        'score': item.get('score', 0)
                    })
                
                results['found'] = len(results['results']) > 0
                print(f"    ✓ Found {len(results['results'])} results")
            else:
                print(f"    ✗ API error: {response.status_code}")
        
        except Exception as e:
            print(f"    ⚠️  Tavily error: {e}")
        
        return results
    
    def _brave_search(self, query: str) -> Dict:
        """Brave Search API"""
        results = {
            'found': False,
            'results': []
        }
        
        try:
            print(f"  🦁 Brave Search: {query}")
            
            headers = {
                'Accept': 'application/json',
                'X-Subscription-Token': self.brave_api_key
            }
            
            params = {
                'q': query,
                'count': 10,
                'search_lang': 'en'
            }
            
            response = requests.get(
                self.brave_url,
                headers=headers,
                params=params,
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                
                for item in data.get('web', {}).get('results', []):
                    results['results'].append({
                        'title': item.get('title', ''),
                        'url': item.get('url', ''),
                        'description': item.get('description', ''),
                        'age': item.get('age', '')
                    })
                
                results['found'] = len(results['results']) > 0
                print(f"    ✓ Found {len(results['results'])} results")
            else:
                print(f"    ✗ API error: {response.status_code}")
        
        except Exception as e:
            print(f"    ⚠️  Brave error: {e}")
        
        return results
    
    def _stackoverflow_search(self, query: str) -> Dict:
        """Stack Overflow API"""
        results = {
            'found': False,
            'questions': []
        }
        
        try:
            print(f"  📚 Stack Overflow: {query}")
            
            params = {
                'order': 'desc',
                'sort': 'relevance',
                'intitle': query,
                'site': 'stackoverflow',
                'filter': 'withbody',
                'pagesize': 5
            }
            
            if self.stackoverflow_key:
                params['key'] = self.stackoverflow_key
            
            response = requests.get(
                self.stackoverflow_url,
                params=params,
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                
                for item in data.get('items', []):
                    results['questions'].append({
                        'question_id': item.get('question_id'),
                        'title': item.get('title', ''),
                        'link': item.get('link', ''),
                        'score': item.get('score', 0),
                        'answer_count': item.get('answer_count', 0),
                        'is_answered': item.get('is_answered', False),
                        'tags': item.get('tags', []),
                        'creation_date': datetime.fromtimestamp(
                            item.get('creation_date', 0)
                        ).strftime('%Y-%m-%d')
                    })
                
                results['found'] = len(results['questions']) > 0
                print(f"    ✓ Found {len(results['questions'])} questions")
            else:
                print(f"    ✗ API error: {response.status_code}")
        
        except Exception as e:
            print(f"    ⚠️  Stack Overflow error: {e}")
        
        return results
    
    def _github_advanced_search(self, query: str, task_type: str) -> Dict:
        """GitHub Advanced Search API"""
        results = {
            'found': False,
            'repositories': [],
            'code': [],
            'discussions': []
        }
        
        if not self.github_token:
            return results
        
        try:
            print(f"  🐙 GitHub Advanced Search: {query}")
            
            headers = {
                'Authorization': f'token {self.github_token}',
                'Accept': 'application/vnd.github.v3+json'
            }
            
            # Search repositories
            repo_params = {
                'q': f'{query} stars:>100',
                'sort': 'stars',
                'order': 'desc',
                'per_page': 5
            }
            
            repo_response = requests.get(
                'https://api.github.com/search/repositories',
                headers=headers,
                params=repo_params,
                timeout=10
            )
            
            if repo_response.status_code == 200:
                repo_data = repo_response.json()
                for item in repo_data.get('items', []):
                    results['repositories'].append({
                        'name': item['full_name'],
                        'description': item.get('description', ''),
                        'url': item['html_url'],
                        'stars': item['stargazers_count'],
                        'language': item.get('language', ''),
                        'topics': item.get('topics', [])
                    })
            
            # Search code
            code_params = {
                'q': f'{query} language:python OR language:javascript',
                'sort': 'indexed',
                'order': 'desc',
                'per_page': 5
            }
            
            code_response = requests.get(
                'https://api.github.com/search/code',
                headers=headers,
                params=code_params,
                timeout=10
            )
            
            if code_response.status_code == 200:
                code_data = code_response.json()
                for item in code_data.get('items', []):
                    results['code'].append({
                        'name': item['name'],
                        'path': item['path'],
                        'repository': item['repository']['full_name'],
                        'url': item['html_url']
                    })
            
            results['found'] = (
                len(results['repositories']) > 0 or 
                len(results['code']) > 0
            )
            
            print(f"    ✓ Found {len(results['repositories'])} repos, {len(results['code'])} code files")
        
        except Exception as e:
            print(f"    ⚠️  GitHub Advanced error: {e}")
        
        return results
    
    def _fetch_documentation(self, keywords: List[str]) -> Dict:
        """Fetch documentation from official sources"""
        results = {
            'found': False,
            'docs': []
        }
        
        doc_urls = self._get_doc_urls(keywords)
        
        for url in doc_urls[:3]:
            try:
                print(f"  📖 Fetching: {url}")
                
                response = requests.get(url, timeout=10)
                
                if response.status_code == 200:
                    results['docs'].append({
                        'url': url,
                        'title': self._extract_title_from_html(response.text),
                        'status': 'available',
                        'size': len(response.text)
                    })
                    results['found'] = True
                    print(f"    ✓ Fetched successfully")
                else:
                    print(f"    ✗ HTTP {response.status_code}")
            
            except Exception as e:
                print(f"    ⚠️  Fetch error: {e}")
        
        return results
    
    def _get_trusted_domains(self, task_type: str) -> List[str]:
        """Get trusted domains for Tavily search"""
        base_domains = [
            'github.com',
            'stackoverflow.com',
            'medium.com',
            'dev.to'
        ]
        
        type_domains = {
            'bug': ['stackoverflow.com', 'github.com/issues'],
            'feature': ['github.com', 'dev.to', 'medium.com'],
            'architecture': ['martinfowler.com', 'microservices.io'],
            'security': ['owasp.org', 'snyk.io', 'security.stackexchange.com'],
            'performance': ['web.dev', 'developers.google.com']
        }
        
        return base_domains + type_domains.get(task_type, [])
    
    def _extract_title_from_html(self, html: str) -> str:
        """Extract title from HTML"""
        try:
            import re
            match = re.search(r'<title>(.*?)</title>', html, re.IGNORECASE)
            if match:
                return match.group(1).strip()
        except:
            pass
        return 'Documentation'
    
    def _print_mcp_extended_results(self, results: Dict):
        """Print MCP extended results"""
        # Tavily
        tavily = results.get('tavily_search', {})
        if tavily.get('found'):
            print(f"\n  🔍 Tavily AI Search:")
            if tavily.get('answer'):
                print(f"    Answer: {tavily['answer'][:200]}...")
            print(f"    Results: {len(tavily['results'])}")
            for r in tavily['results'][:3]:
                print(f"      • {r['title']}")
                print(f"        {r['url']}")
        
        # Brave
        brave = results.get('brave_search', {})
        if brave.get('found'):
            print(f"\n  🦁 Brave Search:")
            print(f"    Results: {len(brave['results'])}")
            for r in brave['results'][:3]:
                print(f"      • {r['title']}")
                print(f"        {r['url']}")
        
        # Stack Overflow
        so = results.get('stackoverflow', {})
        if so.get('found'):
            print(f"\n  📚 Stack Overflow:")
            print(f"    Questions: {len(so['questions'])}")
            for q in so['questions'][:3]:
                print(f"      • {q['title']}")
                print(f"        Score: {q['score']}, Answers: {q['answer_count']}")
                print(f"        {q['link']}")
        
        # GitHub Advanced
        gh = results.get('github_advanced', {})
        if gh.get('found'):
            print(f"\n  🐙 GitHub Advanced:")
            if gh['repositories']:
                print(f"    Repositories: {len(gh['repositories'])}")
                for r in gh['repositories'][:3]:
                    print(f"      • {r['name']} ({r['stars']}⭐)")
                    print(f"        {r['url']}")
            if gh['code']:
                print(f"    Code Examples: {len(gh['code'])}")
                for c in gh['code'][:3]:
                    print(f"      • {c['repository']}/{c['path']}")
        
        # Documentation
        docs = results.get('documentation', {})
        if docs.get('found'):
            print(f"\n  📖 Documentation:")
            for d in docs['docs']:
                print(f"      • {d['title']}")
                print(f"        {d['url']}")
    
    def _update_summary_with_mcp(self, results: Dict, mcp_results: Dict):
        """Update summary with MCP findings"""
        summary = results['summary']
        
        # Count MCP findings
        mcp_count = 0
        if mcp_results.get('tavily_search', {}).get('found'):
            mcp_count += len(mcp_results['tavily_search']['results'])
        if mcp_results.get('brave_search', {}).get('found'):
            mcp_count += len(mcp_results['brave_search']['results'])
        if mcp_results.get('stackoverflow', {}).get('found'):
            mcp_count += len(mcp_results['stackoverflow']['questions'])
        if mcp_results.get('github_advanced', {}).get('found'):
            mcp_count += len(mcp_results['github_advanced']['repositories'])
        
        if mcp_count > 0:
            summary['findings'].append(
                f"Found {mcp_count} external resources via MCP APIs"
            )
            
            # Upgrade confidence if we found external resources
            if summary['confidence'] == 'low' and mcp_count >= 5:
                summary['confidence'] = 'medium'
                summary['recommendations'].append(
                    "💡 External resources available - Review before starting"
                )


def main():
    """Main entry point"""
    import argparse
    
    parser = argparse.ArgumentParser(
        description='Research Agent with Full MCP Integration'
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
    
    # Run research with full MCP
    agent = ResearchAgentMCPExtended()
    try:
        results = agent.research(task, task_type)
        sys.exit(0)
    finally:
        agent.close()


if __name__ == '__main__':
    main()

