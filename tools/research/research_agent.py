#!/usr/bin/env python3
"""
Research Agent - Auto-research before starting any task

Purpose: Query Neo4j, GitHub, Knowledge Base, and external tools
         to find relevant information before planning/development/bug fixing

Usage:
    python tools/research/research_agent.py --task "Build authentication system"
    python tools/research/research_agent.py --bug "Login fails with OAuth"
    python tools/research/research_agent.py --feature "Real-time notifications"
"""

import os
import sys
import json
import argparse
from datetime import datetime
from typing import Dict, List, Optional
from pathlib import Path

# Neo4j
try:
    from neo4j import GraphDatabase
    NEO4J_AVAILABLE = True
except ImportError:
    NEO4J_AVAILABLE = False
    print("⚠️  Neo4j driver not installed. Run: pip install neo4j")

# GitHub API
try:
    import requests
    REQUESTS_AVAILABLE = True
except ImportError:
    REQUESTS_AVAILABLE = False
    print("⚠️  Requests not installed. Run: pip install requests")


class ResearchAgent:
    """Agent to research before starting tasks"""
    
    def __init__(self):
        self.neo4j_driver = None
        self.github_token = os.getenv('GITHUB_TOKEN')
        self.github_repo = os.getenv('GITHUB_REPO')
        self.project_root = Path(__file__).parent.parent.parent

        
        # Initialize Neo4j if available
        if NEO4J_AVAILABLE:
            self._init_neo4j()
    
    def _init_neo4j(self):
        """Initialize Neo4j connection"""
        uri = os.getenv('NEO4J_URI')
        username = os.getenv('NEO4J_USERNAME')
        password = os.getenv('NEO4J_PASSWORD')
        
        if uri and username and password:
            try:
                self.neo4j_driver = GraphDatabase.driver(
                    uri, 
                    auth=(username, password)
                )
                print("✓ Connected to Neo4j")
            except Exception as e:
                print(f"⚠️  Neo4j connection failed: {e}")
        else:
            print("⚠️  Neo4j credentials not found in .env")
    
    def research(self, task: str, task_type: str = 'general') -> Dict:
        """
        Main research method
        
        Args:
            task: Task description
            task_type: 'general', 'bug', 'feature', 'architecture'
        
        Returns:
            Research results from all sources
        """
        print(f"\n{'='*60}")
        print(f"🔍 RESEARCH AGENT - Starting Research")
        print(f"{'='*60}")
        print(f"Task: {task}")
        print(f"Type: {task_type}")
        print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"{'='*60}\n")
        
        results = {
            'task': task,
            'task_type': task_type,
            'timestamp': datetime.now().isoformat(),
            'sources': {}
        }
        
        # 1. Search Knowledge Base (File System)
        print("📚 Searching Knowledge Base...")
        kb_results = self._search_knowledge_base(task, task_type)
        results['sources']['knowledge_base'] = kb_results
        self._print_kb_results(kb_results)
        
        # 2. Search Neo4j (if available)
        if self.neo4j_driver:
            print("\n🧠 Querying Neo4j Knowledge Graph...")
            neo4j_results = self._search_neo4j(task, task_type)
            results['sources']['neo4j'] = neo4j_results
            self._print_neo4j_results(neo4j_results)
        
        # 3. Search GitHub Issues
        if self.github_token and REQUESTS_AVAILABLE:
            print("\n🐙 Searching GitHub Issues...")
            github_results = self._search_github(task, task_type)
            results['sources']['github'] = github_results
            self._print_github_results(github_results)
        
        # 4. Generate Research Summary
        print("\n" + "="*60)
        summary = self._generate_summary(results)
        results['summary'] = summary
        self._print_summary(summary)
        
        # 5. Save Research Report
        report_path = self._save_report(results)
        print(f"\n💾 Research report saved: {report_path}")
        
        return results
    
    def _search_knowledge_base(self, task: str, task_type: str) -> Dict:
        """Search file-based knowledge base"""
        results = {
            'found': False,
            'entries': [],
            'categories': []
        }
        
        if not self.kb_path.exists():
            return results
        
        # Extract keywords from task
        keywords = self._extract_keywords(task)
        
        # Search in relevant categories
        categories = self._get_relevant_categories(task_type)
        
        for category in categories:
            category_path = self.kb_path / category
            if not category_path.exists():
                continue
            
            # Search markdown files
            for md_file in category_path.rglob('*.md'):
                if md_file.name in ['README.md', 'index.md']:
                    continue
                
                try:
                    content = md_file.read_text(encoding='utf-8')
                    
                    # Check if any keyword matches
                    if any(kw.lower() in content.lower() for kw in keywords):
                        results['entries'].append({
                            'file': str(md_file.relative_to(self.project_root)),
                            'category': category,
                            'title': self._extract_title(content),
                            'relevance': self._calculate_relevance(content, keywords)
                        })
                        results['found'] = True
                except Exception as e:
                    print(f"⚠️  Error reading {md_file}: {e}")
        
        # Sort by relevance
        results['entries'].sort(key=lambda x: x['relevance'], reverse=True)
        results['categories'] = list(set([e['category'] for e in results['entries']]))
        
        return results
    
    def _search_neo4j(self, task: str, task_type: str) -> Dict:
        """Search Neo4j knowledge graph"""
        results = {
            'found': False,
            'entries': [],
            'related_technologies': [],
            'similar_tasks': []
        }
        
        if not self.neo4j_driver:
            return results
        
        keywords = self._extract_keywords(task)
        
        try:
            with self.neo4j_driver.session() as session:
                # Search knowledge entries
                query = """
                MATCH (k:KnowledgeEntry)
                WHERE ANY(keyword IN $keywords WHERE 
                    toLower(k.title) CONTAINS toLower(keyword) OR
                    toLower(k.problem) CONTAINS toLower(keyword) OR
                    toLower(k.solution) CONTAINS toLower(keyword)
                )
                OPTIONAL MATCH (k)-[:USES]->(t:Technology)
                RETURN k, collect(t.name) as technologies
                ORDER BY k.created_at DESC
                LIMIT 10
                """
                
                result = session.run(query, keywords=keywords)
                
                for record in result:
                    k = record['k']
                    results['entries'].append({
                        'id': k['id'],
                        'title': k['title'],
                        'category': k['category'],
                        'severity': k.get('severity', 'N/A'),
                        'technologies': record['technologies']
                    })
                    results['found'] = True
                
                # Find related technologies
                tech_query = """
                MATCH (k:KnowledgeEntry)-[:USES]->(t:Technology)
                WHERE ANY(keyword IN $keywords WHERE 
                    toLower(k.title) CONTAINS toLower(keyword)
                )
                RETURN t.name as technology, count(*) as usage_count
                ORDER BY usage_count DESC
                LIMIT 5
                """
                
                tech_result = session.run(tech_query, keywords=keywords)
                results['related_technologies'] = [
                    {'name': r['technology'], 'count': r['usage_count']}
                    for r in tech_result
                ]
                
        except Exception as e:
            print(f"⚠️  Neo4j query error: {e}")
        
        return results
    
    def _search_github(self, task: str, task_type: str) -> Dict:
        """Search GitHub issues"""
        results = {
            'found': False,
            'issues': [],
            'pull_requests': []
        }
        
        if not self.github_token or not self.github_repo:
            return results
        
        keywords = self._extract_keywords(task)
        query = ' '.join(keywords)
        
        headers = {
            'Authorization': f'token {self.github_token}',
            'Accept': 'application/vnd.github.v3+json'
        }
        
        try:
            # Search issues
            url = f'https://api.github.com/search/issues'
            params = {
                'q': f'{query} repo:{self.github_repo} type:issue',
                'sort': 'updated',
                'order': 'desc',
                'per_page': 10
            }
            
            response = requests.get(url, headers=headers, params=params)
            
            if response.status_code == 200:
                data = response.json()
                for item in data.get('items', []):
                    results['issues'].append({
                        'number': item['number'],
                        'title': item['title'],
                        'state': item['state'],
                        'url': item['html_url'],
                        'labels': [l['name'] for l in item.get('labels', [])]
                    })
                    results['found'] = True
            
            # Search pull requests
            params['q'] = f'{query} repo:{self.github_repo} type:pr'
            response = requests.get(url, headers=headers, params=params)
            
            if response.status_code == 200:
                data = response.json()
                for item in data.get('items', []):
                    results['pull_requests'].append({
                        'number': item['number'],
                        'title': item['title'],
                        'state': item['state'],
                        'url': item['html_url']
                    })
        
        except Exception as e:
            print(f"⚠️  GitHub API error: {e}")
        
        return results
    
    def _extract_keywords(self, text: str) -> List[str]:
        """Extract keywords from text"""
        # Remove common words
        stop_words = {'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 
                     'to', 'for', 'of', 'with', 'by', 'from', 'as', 'is', 'was'}
        
        words = text.lower().split()
        keywords = [w for w in words if w not in stop_words and len(w) > 2]
        
        return keywords[:10]  # Top 10 keywords
    
    def _get_relevant_categories(self, task_type: str) -> List[str]:
        """Get relevant KB categories based on task type"""
        category_map = {
            'bug': ['bugs', 'features', 'architecture'],
            'feature': ['features', 'architecture', 'performance'],
            'architecture': ['architecture', 'features', 'security'],
            'security': ['security', 'architecture', 'bugs'],
            'performance': ['performance', 'architecture', 'features'],
            'general': ['bugs', 'features', 'architecture', 'security', 'performance']
        }
        
        return category_map.get(task_type, category_map['general'])
    
    def _extract_title(self, content: str) -> str:
        """Extract title from markdown content"""
        lines = content.split('\n')
        for line in lines:
            if line.startswith('# '):
                return line[2:].strip()
        return 'Untitled'
    
    def _calculate_relevance(self, content: str, keywords: List[str]) -> float:
        """Calculate relevance score"""
        content_lower = content.lower()
        score = sum(1 for kw in keywords if kw.lower() in content_lower)
        return score / len(keywords) if keywords else 0
    
    def _generate_summary(self, results: Dict) -> Dict:
        """Generate research summary"""
        summary = {
            'total_sources': len(results['sources']),
            'findings': [],
            'recommendations': [],
            'related_entries': 0,
            'confidence': 'low'
        }
        
        # Count findings
        kb = results['sources'].get('knowledge_base', {})
        neo4j = results['sources'].get('neo4j', {})
        github = results['sources'].get('github', {})
        
        total_entries = len(kb.get('entries', [])) + len(neo4j.get('entries', []))
        summary['related_entries'] = total_entries
        
        # Determine confidence
        if total_entries >= 5:
            summary['confidence'] = 'high'
        elif total_entries >= 2:
            summary['confidence'] = 'medium'
        
        # Generate findings
        if kb.get('found'):
            summary['findings'].append(
                f"Found {len(kb['entries'])} related entries in Knowledge Base"
            )
        
        if neo4j.get('found'):
            summary['findings'].append(
                f"Found {len(neo4j['entries'])} related entries in Neo4j"
            )
            if neo4j.get('related_technologies'):
                techs = ', '.join([t['name'] for t in neo4j['related_technologies'][:3]])
                summary['findings'].append(f"Related technologies: {techs}")
        
        if github.get('found'):
            summary['findings'].append(
                f"Found {len(github['issues'])} related GitHub issues"
            )
        
        # Generate recommendations
        if summary['confidence'] == 'high':
            summary['recommendations'].append(
                "✓ Strong knowledge base available - Review existing solutions before starting"
            )
        elif summary['confidence'] == 'medium':
            summary['recommendations'].append(
                "⚠️  Some knowledge available - Review and consider similar approaches"
            )
        else:
            summary['recommendations'].append(
                "⚠️  Limited knowledge - This may be a new challenge, document thoroughly"
            )
        
        if not kb.get('found') and not neo4j.get('found'):
            summary['recommendations'].append(
                "💡 No similar entries found - Consider creating detailed documentation"
            )
        
        return summary
    
    def _print_kb_results(self, results: Dict):
        """Print knowledge base results"""
        if results['found']:
            print(f"  ✓ Found {len(results['entries'])} entries")
            for entry in results['entries'][:5]:
                print(f"    • {entry['title']}")
                print(f"      File: {entry['file']}")
                print(f"      Relevance: {entry['relevance']:.0%}")
        else:
            print("  ✗ No entries found")
    
    def _print_neo4j_results(self, results: Dict):
        """Print Neo4j results"""
        if results['found']:
            print(f"  ✓ Found {len(results['entries'])} entries")
            for entry in results['entries'][:5]:
                print(f"    • {entry['title']}")
                print(f"      ID: {entry['id']}")
                print(f"      Category: {entry['category']}")
                if entry['technologies']:
                    print(f"      Technologies: {', '.join(entry['technologies'])}")
            
            if results['related_technologies']:
                print(f"\n  Related Technologies:")
                for tech in results['related_technologies']:
                    print(f"    • {tech['name']} (used {tech['count']}x)")
        else:
            print("  ✗ No entries found")
    
    def _print_github_results(self, results: Dict):
        """Print GitHub results"""
        if results['found']:
            if results['issues']:
                print(f"  ✓ Found {len(results['issues'])} issues")
                for issue in results['issues'][:5]:
                    print(f"    • #{issue['number']}: {issue['title']}")
                    print(f"      State: {issue['state']}")
                    print(f"      URL: {issue['url']}")
            
            if results['pull_requests']:
                print(f"  ✓ Found {len(results['pull_requests'])} pull requests")
                for pr in results['pull_requests'][:3]:
                    print(f"    • #{pr['number']}: {pr['title']}")
        else:
            print("  ✗ No issues/PRs found")
    
    def _print_summary(self, summary: Dict):
        """Print research summary"""
        print("📊 RESEARCH SUMMARY")
        print("="*60)
        print(f"Confidence Level: {summary['confidence'].upper()}")
        print(f"Related Entries: {summary['related_entries']}")
        print(f"\nFindings:")
        for finding in summary['findings']:
            print(f"  • {finding}")
        print(f"\nRecommendations:")
        for rec in summary['recommendations']:
            print(f"  {rec}")
        print("="*60)
    
    def _save_report(self, results: Dict) -> Path:
        """Save research report"""
        reports_dir = self.project_root / 'docs' / 'research-reports'
        reports_dir.mkdir(parents=True, exist_ok=True)
        
        timestamp = datetime.now().strftime('%Y%m%d-%H%M%S')
        filename = f"research-{timestamp}.json"
        report_path = reports_dir / filename
        
        with open(report_path, 'w', encoding='utf-8') as f:
            json.dump(results, f, indent=2, ensure_ascii=False)
        
        # Also create markdown summary
        md_filename = f"research-{timestamp}.md"
        md_path = reports_dir / md_filename
        self._save_markdown_report(md_path, results)
        
        return report_path
    
    def _save_markdown_report(self, path: Path, results: Dict):
        """Save markdown research report"""
        with open(path, 'w', encoding='utf-8') as f:
            f.write(f"# Research Report\n\n")
            f.write(f"**Task:** {results['task']}\n")
            f.write(f"**Type:** {results['task_type']}\n")
            f.write(f"**Date:** {results['timestamp']}\n\n")
            
            f.write(f"## Summary\n\n")
            summary = results['summary']
            f.write(f"- **Confidence:** {summary['confidence']}\n")
            f.write(f"- **Related Entries:** {summary['related_entries']}\n\n")
            
            f.write(f"### Findings\n\n")
            for finding in summary['findings']:
                f.write(f"- {finding}\n")
            
            f.write(f"\n### Recommendations\n\n")
            for rec in summary['recommendations']:
                f.write(f"- {rec}\n")
            
            f.write(f"\n## Detailed Results\n\n")
            
            # Knowledge Base
            kb = results['sources'].get('knowledge_base', {})
            if kb.get('found'):
                f.write(f"### Knowledge Base ({len(kb['entries'])} entries)\n\n")
                for entry in kb['entries']:
                    f.write(f"#### {entry['title']}\n")
                    f.write(f"- File: `{entry['file']}`\n")
                    f.write(f"- Category: {entry['category']}\n")
                    f.write(f"- Relevance: {entry['relevance']:.0%}\n\n")
            
            # Neo4j
            neo4j = results['sources'].get('neo4j', {})
            if neo4j.get('found'):
                f.write(f"### Neo4j Knowledge Graph ({len(neo4j['entries'])} entries)\n\n")
                for entry in neo4j['entries']:
                    f.write(f"#### {entry['title']}\n")
                    f.write(f"- ID: {entry['id']}\n")
                    f.write(f"- Category: {entry['category']}\n")
                    if entry['technologies']:
                        f.write(f"- Technologies: {', '.join(entry['technologies'])}\n")
                    f.write(f"\n")
            
            # GitHub
            github = results['sources'].get('github', {})
            if github.get('found'):
                f.write(f"### GitHub Issues ({len(github['issues'])} issues)\n\n")
                for issue in github['issues']:
                    f.write(f"- [#{issue['number']}]({issue['url']}): {issue['title']}\n")
    
    def close(self):
        """Close connections"""
        if self.neo4j_driver:
            self.neo4j_driver.close()


def main():
    parser = argparse.ArgumentParser(
        description='Research Agent - Auto-research before starting tasks'
    )
    parser.add_argument(
        '--task',
        type=str,
        help='Task description'
    )
    parser.add_argument(
        '--bug',
        type=str,
        help='Bug description (shortcut for --task with type=bug)'
    )
    parser.add_argument(
        '--feature',
        type=str,
        help='Feature description (shortcut for --task with type=feature)'
    )
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
    
    # Run research
    agent = ResearchAgent()
    try:
        results = agent.research(task, task_type)
        
        # Exit with appropriate code
        confidence = results['summary']['confidence']
        if confidence == 'high':
            sys.exit(0)  # Success - strong knowledge available
        elif confidence == 'medium':
            sys.exit(0)  # Success - some knowledge available
        else:
            sys.exit(0)  # Success - but limited knowledge
    
    finally:
        agent.close()


if __name__ == '__main__':
    main()
