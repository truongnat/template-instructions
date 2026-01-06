#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Self-Learning Engine for Neo4j Knowledge Graph

This script provides pattern recognition, error tracking, and recommendation
capabilities to enable the AI brain to learn from past experiences.

Features:
- Error pattern detection and linking
- Success pattern recognition
- Recommendation engine for similar tasks
- Reasoning path discovery from past fixes
- Learning weights and confidence scoring

Usage:
    python tools/neo4j/learning_engine.py --record-error "TypeError" --resolution "Added null check"
    python tools/neo4j/learning_engine.py --record-success "auth-feature" --approach "JWT tokens"
    python tools/neo4j/learning_engine.py --recommend "implement user authentication"
    python tools/neo4j/learning_engine.py --similar-errors "ConnectionError"
    python tools/neo4j/learning_engine.py --reasoning-path "TypeError" "null check"
"""

import os
import re
import sys
import json
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional, Tuple
from dotenv import load_dotenv
from neo4j import GraphDatabase
import argparse

# Set UTF-8 encoding for Windows console
if sys.platform == 'win32':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
        sys.stderr.reconfigure(encoding='utf-8')
    except:
        pass

# Load environment variables
load_dotenv()


class LearningEngine:
    """Self-learning engine using Neo4j knowledge graph"""
    
    def __init__(self, uri: str, user: str, password: str, database: str = "neo4j"):
        """Initialize Neo4j connection"""
        self.driver = GraphDatabase.driver(uri, auth=(user, password))
        self.database = database
        print(f"✅ Learning engine connected to Neo4j: {uri}")
    
    def close(self):
        """Close Neo4j connection"""
        self.driver.close()
    
    def create_learning_schema(self):
        """Create schema for learning nodes"""
        constraints = [
            "CREATE CONSTRAINT error_id IF NOT EXISTS FOR (e:Error) REQUIRE e.id IS UNIQUE",
            "CREATE CONSTRAINT resolution_id IF NOT EXISTS FOR (r:Resolution) REQUIRE r.id IS UNIQUE",
            "CREATE CONSTRAINT pattern_id IF NOT EXISTS FOR (p:Pattern) REQUIRE p.id IS UNIQUE",
            "CREATE CONSTRAINT learning_id IF NOT EXISTS FOR (l:Learning) REQUIRE l.id IS UNIQUE",
        ]
        
        indexes = [
            "CREATE INDEX error_type IF NOT EXISTS FOR (e:Error) ON (e.type)",
            "CREATE INDEX error_message IF NOT EXISTS FOR (e:Error) ON (e.message)",
            "CREATE INDEX pattern_type IF NOT EXISTS FOR (p:Pattern) ON (p.type)",
            "CREATE INDEX resolution_approach IF NOT EXISTS FOR (r:Resolution) ON (r.approach)",
            "CREATE FULLTEXT INDEX error_search IF NOT EXISTS FOR (e:Error) ON EACH [e.message, e.context]",
        ]
        
        with self.driver.session(database=self.database) as session:
            print("🔧 Setting up learning schema...")
            
            for constraint in constraints:
                try:
                    session.run(constraint)
                except Exception as e:
                    if "already exists" not in str(e).lower():
                        print(f"  ⚠️  {e}")
            
            for index in indexes:
                try:
                    session.run(index)
                except Exception as e:
                    if "already exists" not in str(e).lower() and "equivalent" not in str(e).lower():
                        print(f"  ⚠️  {e}")
            
            print("  ✅ Learning schema ready")
    
    def generate_id(self, prefix: str, content: str) -> str:
        """Generate unique ID for learning nodes"""
        import hashlib
        hash_str = hashlib.sha256(f"{prefix}_{content}_{datetime.now().isoformat()}".encode()).hexdigest()[:12]
        return f"{prefix}_{hash_str}"
    
    # ==================== ERROR TRACKING ====================
    
    def record_error(self, error_type: str, message: str, context: Dict = None, 
                    resolution: str = None, resolution_approach: str = None) -> str:
        """Record an error and optionally its resolution"""
        error_id = self.generate_id("ERR", f"{error_type}_{message[:50]}")
        context_str = json.dumps(context) if context else "{}"
        
        with self.driver.session(database=self.database) as session:
            # Create or update Error node
            session.run("""
                MERGE (e:Error {id: $error_id})
                SET e.type = $error_type,
                    e.message = $message,
                    e.context = $context,
                    e.first_seen = coalesce(e.first_seen, datetime()),
                    e.last_seen = datetime(),
                    e.occurrence_count = coalesce(e.occurrence_count, 0) + 1
            """, 
                error_id=error_id,
                error_type=error_type,
                message=message,
                context=context_str
            )
            
            # If resolution provided, create Resolution and link
            if resolution:
                resolution_id = self.generate_id("RES", resolution[:50])
                session.run("""
                    MATCH (e:Error {id: $error_id})
                    MERGE (r:Resolution {id: $resolution_id})
                    SET r.description = $resolution,
                        r.approach = $approach,
                        r.created_at = datetime(),
                        r.success_count = coalesce(r.success_count, 0) + 1
                    MERGE (e)-[rel:RESOLVED_BY]->(r)
                    SET rel.last_used = datetime(),
                        rel.use_count = coalesce(rel.use_count, 0) + 1
                """,
                    error_id=error_id,
                    resolution_id=resolution_id,
                    resolution=resolution,
                    approach=resolution_approach or "manual fix"
                )
                
                print(f"✅ Recorded error '{error_type}' with resolution")
                return resolution_id
            
            print(f"✅ Recorded error '{error_type}'")
            return error_id
    
    def find_similar_errors(self, error_message: str, limit: int = 5) -> List[Dict]:
        """Find similar errors and their resolutions"""
        with self.driver.session(database=self.database) as session:
            # Try fulltext search first
            try:
                result = session.run("""
                    CALL db.index.fulltext.queryNodes("error_search", $search_query) 
                    YIELD node as e, score
                    WHERE score > 0.5
                    OPTIONAL MATCH (e)-[rel:RESOLVED_BY]->(r:Resolution)
                    RETURN e.id as error_id, 
                           e.type as error_type,
                           e.message as message,
                           e.occurrence_count as occurrences,
                           collect({
                               resolution: r.description,
                               approach: r.approach,
                               success_count: r.success_count,
                               use_count: rel.use_count
                           }) as resolutions,
                           score
                    ORDER BY score DESC
                    LIMIT $limit
                """, search_query=error_message, limit=limit)
                
                return [dict(record) for record in result]
            except Exception:
                # Fallback to CONTAINS search
                result = session.run("""
                    MATCH (e:Error)
                    WHERE e.message CONTAINS $search_query OR e.type CONTAINS $search_query
                    OPTIONAL MATCH (e)-[rel:RESOLVED_BY]->(r:Resolution)
                    RETURN e.id as error_id,
                           e.type as error_type,
                           e.message as message,
                           e.occurrence_count as occurrences,
                           collect({
                               resolution: r.description,
                               approach: r.approach,
                               success_count: r.success_count
                           }) as resolutions
                    LIMIT $limit
                """, search_query=error_message, limit=limit)
                
                return [dict(record) for record in result]
    
    # ==================== SUCCESS PATTERN TRACKING ====================
    
    def record_success(self, task_id: str, task_type: str, approach: str, 
                      outcome: str = "completed", confidence: float = 1.0) -> str:
        """Record a successful task completion pattern"""
        pattern_id = self.generate_id("PAT", f"{task_type}_{approach[:30]}")
        
        with self.driver.session(database=self.database) as session:
            # Create Task node
            session.run("""
                MERGE (t:Task {id: $task_id})
                SET t.type = $task_type,
                    t.status = $outcome,
                    t.completed_at = datetime()
            """, task_id=task_id, task_type=task_type, outcome=outcome)
            
            # Create or update Pattern node
            session.run("""
                MERGE (p:Pattern {id: $pattern_id})
                SET p.type = $task_type,
                    p.approach = $approach,
                    p.last_success = datetime(),
                    p.success_count = coalesce(p.success_count, 0) + 1,
                    p.total_confidence = coalesce(p.total_confidence, 0) + $confidence
            """, 
                pattern_id=pattern_id,
                task_type=task_type,
                approach=approach,
                confidence=confidence
            )
            
            # Link Task to Pattern
            session.run("""
                MATCH (t:Task {id: $task_id}), (p:Pattern {id: $pattern_id})
                MERGE (t)-[:USED_PATTERN]->(p)
            """, task_id=task_id, pattern_id=pattern_id)
            
            print(f"✅ Recorded success pattern: {approach} for {task_type}")
            return pattern_id
    
    def get_successful_patterns(self, task_type: str = None, limit: int = 10) -> List[Dict]:
        """Get most successful patterns for a task type"""
        with self.driver.session(database=self.database) as session:
            if task_type:
                result = session.run("""
                    MATCH (p:Pattern)
                    WHERE p.type = $task_type
                    RETURN p.id as pattern_id,
                           p.type as task_type,
                           p.approach as approach,
                           p.success_count as success_count,
                           p.total_confidence / p.success_count as avg_confidence,
                           p.last_success as last_used
                    ORDER BY p.success_count DESC, avg_confidence DESC
                    LIMIT $limit
                """, task_type=task_type, limit=limit)
            else:
                result = session.run("""
                    MATCH (p:Pattern)
                    RETURN p.id as pattern_id,
                           p.type as task_type,
                           p.approach as approach,
                           p.success_count as success_count,
                           p.total_confidence / p.success_count as avg_confidence,
                           p.last_success as last_used
                    ORDER BY p.success_count DESC
                    LIMIT $limit
                """, limit=limit)
            
            return [dict(record) for record in result]
    
    # ==================== RECOMMENDATION ENGINE ====================
    
    def get_recommendations(self, task_description: str, limit: int = 5) -> List[Dict]:
        """Get recommendations based on task description"""
        recommendations = []
        
        # Extract keywords from task description
        keywords = self._extract_keywords(task_description)
        
        with self.driver.session(database=self.database) as session:
            # Search for relevant patterns
            for keyword in keywords[:5]:  # Limit keyword search
                result = session.run("""
                    MATCH (p:Pattern)
                    WHERE toLower(p.approach) CONTAINS toLower($keyword)
                       OR toLower(p.type) CONTAINS toLower($keyword)
                    RETURN p.id as pattern_id,
                           p.type as task_type,
                           p.approach as approach,
                           p.success_count as success_count,
                           p.total_confidence / p.success_count as confidence
                    ORDER BY p.success_count DESC
                    LIMIT 3
                """, keyword=keyword)
                
                for record in result:
                    rec = dict(record)
                    rec['matched_keyword'] = keyword
                    rec['source'] = 'pattern'
                    recommendations.append(rec)
            
            # Search for relevant KB entries
            for keyword in keywords[:3]:
                result = session.run("""
                    MATCH (k:KBEntry)
                    WHERE toLower(k.title) CONTAINS toLower($keyword)
                       OR toLower(k.content_preview) CONTAINS toLower($keyword)
                    OPTIONAL MATCH (k)-[:TEACHES]->(s:Skill)
                    RETURN k.id as kb_id,
                           k.title as title,
                           k.category as category,
                           collect(s.name)[..3] as skills
                    LIMIT 3
                """, keyword=keyword)
                
                for record in result:
                    rec = dict(record)
                    rec['matched_keyword'] = keyword
                    rec['source'] = 'knowledge_base'
                    recommendations.append(rec)
            
            # Search for relevant documents
            for keyword in keywords[:3]:
                result = session.run("""
                    MATCH (d:Document)
                    WHERE toLower(d.title) CONTAINS toLower($keyword)
                       OR toLower(d.content_preview) CONTAINS toLower($keyword)
                    RETURN d.id as doc_id,
                           d.title as title,
                           d.type as doc_type,
                           d.author as author
                    LIMIT 3
                """, keyword=keyword)
                
                for record in result:
                    rec = dict(record)
                    rec['matched_keyword'] = keyword
                    rec['source'] = 'document'
                    recommendations.append(rec)
        
        # Deduplicate and rank
        seen = set()
        unique_recs = []
        for rec in recommendations:
            key = rec.get('pattern_id') or rec.get('kb_id') or rec.get('doc_id')
            if key not in seen:
                seen.add(key)
                unique_recs.append(rec)
        
        return unique_recs[:limit]
    
    def _extract_keywords(self, text: str) -> List[str]:
        """Extract meaningful keywords from text"""
        # Remove common words
        stopwords = {'the', 'a', 'an', 'is', 'are', 'was', 'were', 'be', 'been', 
                    'being', 'have', 'has', 'had', 'do', 'does', 'did', 'will',
                    'would', 'could', 'should', 'may', 'might', 'can', 'for',
                    'to', 'of', 'in', 'on', 'at', 'by', 'with', 'from', 'as',
                    'and', 'or', 'but', 'if', 'then', 'else', 'when', 'where',
                    'how', 'what', 'which', 'who', 'this', 'that', 'these',
                    'implement', 'create', 'add', 'fix', 'update', 'make'}
        
        # Extract words
        words = re.findall(r'\b[a-zA-Z]{3,}\b', text.lower())
        
        # Filter and prioritize
        keywords = [w for w in words if w not in stopwords]
        
        # Keep unique, preserve order
        seen = set()
        unique = []
        for w in keywords:
            if w not in seen:
                seen.add(w)
                unique.append(w)
        
        return unique
    
    # ==================== REASONING PATH ====================
    
    def find_reasoning_path(self, from_error: str, to_resolution: str) -> List[Dict]:
        """Find the reasoning path from an error to a resolution"""
        with self.driver.session(database=self.database) as session:
            # Find shortest path between error and resolution
            result = session.run("""
                MATCH (e:Error), (r:Resolution)
                WHERE e.message CONTAINS $from_error OR e.type CONTAINS $from_error
                AND (r.description CONTAINS $to_resolution OR r.approach CONTAINS $to_resolution)
                MATCH path = shortestPath((e)-[*..5]-(r))
                RETURN nodes(path) as nodes,
                       relationships(path) as rels,
                       length(path) as path_length
                LIMIT 3
            """, from_error=from_error, to_resolution=to_resolution)
            
            paths = []
            for record in result:
                path_info = {
                    'length': record['path_length'],
                    'steps': []
                }
                
                nodes = record['nodes']
                for i, node in enumerate(nodes):
                    step = {
                        'index': i,
                        'labels': list(node.labels),
                        'properties': dict(node)
                    }
                    path_info['steps'].append(step)
                
                paths.append(path_info)
            
            return paths
    
    # ==================== LEARNING CREATION ====================
    
    def create_learning(self, title: str, category: str, insight: str, 
                       source_type: str = "manual", related_ids: List[str] = None) -> str:
        """Create a new learning entry"""
        learning_id = self.generate_id("LRN", title[:50])
        
        with self.driver.session(database=self.database) as session:
            session.run("""
                CREATE (l:Learning {
                    id: $learning_id,
                    title: $title,
                    category: $category,
                    insight: $insight,
                    source_type: $source_type,
                    created_at: datetime(),
                    confidence: 1.0,
                    applied_count: 0
                })
            """,
                learning_id=learning_id,
                title=title,
                category=category,
                insight=insight,
                source_type=source_type
            )
            
            # Link to related nodes
            if related_ids:
                for related_id in related_ids:
                    session.run("""
                        MATCH (l:Learning {id: $learning_id})
                        OPTIONAL MATCH (n) WHERE n.id = $related_id
                        FOREACH (x IN CASE WHEN n IS NOT NULL THEN [1] ELSE [] END |
                            MERGE (l)-[:DERIVED_FROM]->(n)
                        )
                    """, learning_id=learning_id, related_id=related_id)
            
            print(f"✅ Created learning: {title}")
            return learning_id
    
    # ==================== STATISTICS ====================
    
    def get_learning_stats(self) -> Dict:
        """Get learning statistics"""
        with self.driver.session(database=self.database) as session:
            result = session.run("""
                OPTIONAL MATCH (e:Error) WITH count(e) as error_count
                OPTIONAL MATCH (r:Resolution) WITH error_count, count(r) as resolution_count
                OPTIONAL MATCH (p:Pattern) WITH error_count, resolution_count, count(p) as pattern_count
                OPTIONAL MATCH (l:Learning) WITH error_count, resolution_count, pattern_count, count(l) as learning_count
                OPTIONAL MATCH (:Error)-[rel:RESOLVED_BY]->(:Resolution) 
                WITH error_count, resolution_count, pattern_count, learning_count, count(rel) as link_count
                RETURN error_count, resolution_count, pattern_count, learning_count, link_count
            """)
            
            record = result.single()
            return {
                'errors_tracked': record['error_count'],
                'resolutions': record['resolution_count'],
                'patterns': record['pattern_count'],
                'learnings': record['learning_count'],
                'error_resolution_links': record['link_count']
            }


def print_recommendations(recommendations: List[Dict]):
    """Pretty print recommendations"""
    if not recommendations:
        print("\n📭 No recommendations found")
        return
    
    print(f"\n🎯 Found {len(recommendations)} recommendations:\n")
    
    for i, rec in enumerate(recommendations, 1):
        source = rec.get('source', 'unknown')
        
        if source == 'pattern':
            print(f"  {i}. [PATTERN] {rec['approach']}")
            print(f"     Task Type: {rec['task_type']}")
            print(f"     Success Count: {rec['success_count']}")
            print(f"     Confidence: {rec.get('confidence', 'N/A'):.2f}")
            
        elif source == 'knowledge_base':
            print(f"  {i}. [KB] {rec['title']}")
            print(f"     Category: {rec['category']}")
            print(f"     Skills: {', '.join(rec.get('skills', []))}")
            
        elif source == 'document':
            print(f"  {i}. [DOC] {rec['title']}")
            print(f"     Type: {rec['doc_type']}")
            print(f"     Author: {rec['author']}")
        
        print(f"     Matched: '{rec.get('matched_keyword', 'N/A')}'")
        print()


def print_similar_errors(errors: List[Dict]):
    """Pretty print similar errors"""
    if not errors:
        print("\n📭 No similar errors found")
        return
    
    print(f"\n🔍 Found {len(errors)} similar errors:\n")
    
    for i, err in enumerate(errors, 1):
        print(f"  {i}. [{err['error_type']}] {err['message'][:60]}...")
        print(f"     Occurrences: {err['occurrences']}")
        
        resolutions = err.get('resolutions', [])
        if resolutions and resolutions[0].get('resolution'):
            print(f"     Resolutions:")
            for res in resolutions[:3]:
                if res.get('resolution'):
                    print(f"       - {res['resolution'][:50]}...")
                    print(f"         Approach: {res.get('approach', 'N/A')}")
        print()


def main():
    """Main execution function"""
    parser = argparse.ArgumentParser(description='Self-Learning Engine for Neo4j')
    
    # Error tracking
    parser.add_argument('--record-error', nargs=2, metavar=('TYPE', 'MESSAGE'),
                        help='Record an error (type and message)')
    parser.add_argument('--resolution', help='Resolution for the error')
    parser.add_argument('--approach', help='Approach used for resolution')
    parser.add_argument('--similar-errors', help='Find similar errors by message')
    
    # Success patterns
    parser.add_argument('--record-success', metavar='TASK_ID', help='Record successful task')
    parser.add_argument('--task-type', default='general', help='Type of task')
    parser.add_argument('--success-approach', help='Approach used for success')
    parser.add_argument('--outcome', default='completed', help='Outcome of task')
    
    # Recommendations
    parser.add_argument('--recommend', help='Get recommendations for task description')
    
    # Reasoning path
    parser.add_argument('--reasoning-path', nargs=2, metavar=('FROM', 'TO'),
                        help='Find reasoning path from error to resolution')
    
    # Learning
    parser.add_argument('--create-learning', nargs=3, metavar=('TITLE', 'CATEGORY', 'INSIGHT'),
                        help='Create a new learning entry')
    
    # Stats
    parser.add_argument('--stats', action='store_true', help='Show learning statistics')
    parser.add_argument('--patterns', action='store_true', help='Show successful patterns')
    parser.add_argument('--setup', action='store_true', help='Setup learning schema')
    
    args = parser.parse_args()
    
    # Get Neo4j credentials
    uri = os.getenv('NEO4J_URI')
    username = os.getenv('NEO4J_USERNAME')
    password = os.getenv('NEO4J_PASSWORD')
    database = os.getenv('NEO4J_DATABASE', 'neo4j')
    
    if not all([uri, username, password]):
        print("❌ Error: Neo4j credentials not found in .env file")
        return
    
    engine = LearningEngine(uri, username, password, database)
    
    try:
        # Setup schema
        if args.setup:
            engine.create_learning_schema()
            print("✅ Learning schema setup complete")
            return
        
        # Record error
        if args.record_error:
            error_type, message = args.record_error
            engine.record_error(
                error_type=error_type,
                message=message,
                resolution=args.resolution,
                resolution_approach=args.approach
            )
        
        # Find similar errors
        elif args.similar_errors:
            errors = engine.find_similar_errors(args.similar_errors)
            print_similar_errors(errors)
        
        # Record success
        elif args.record_success:
            if not args.success_approach:
                print("❌ Error: --success-approach is required")
                return
            engine.record_success(
                task_id=args.record_success,
                task_type=args.task_type,
                approach=args.success_approach,
                outcome=args.outcome
            )
        
        # Get recommendations
        elif args.recommend:
            recommendations = engine.get_recommendations(args.recommend)
            print_recommendations(recommendations)
        
        # Find reasoning path
        elif args.reasoning_path:
            from_error, to_resolution = args.reasoning_path
            paths = engine.find_reasoning_path(from_error, to_resolution)
            if paths:
                print(f"\n🧠 Found {len(paths)} reasoning paths:\n")
                for i, path in enumerate(paths, 1):
                    print(f"  Path {i} (length: {path['length']}):")
                    for step in path['steps']:
                        labels = ', '.join(step['labels'])
                        print(f"    [{labels}] {step['properties'].get('id', 'N/A')}")
            else:
                print("\n📭 No reasoning paths found")
        
        # Create learning
        elif args.create_learning:
            title, category, insight = args.create_learning
            engine.create_learning(title, category, insight)
        
        # Show stats
        elif args.stats:
            stats = engine.get_learning_stats()
            print("\n📊 Learning Statistics:")
            print(f"   Errors Tracked: {stats['errors_tracked']}")
            print(f"   Resolutions: {stats['resolutions']}")
            print(f"   Patterns: {stats['patterns']}")
            print(f"   Learnings: {stats['learnings']}")
            print(f"   Error→Resolution Links: {stats['error_resolution_links']}")
        
        # Show patterns
        elif args.patterns:
            patterns = engine.get_successful_patterns()
            if patterns:
                print("\n🏆 Successful Patterns:\n")
                for p in patterns:
                    print(f"  - {p['approach']}")
                    print(f"    Type: {p['task_type']} | Success: {p['success_count']}")
            else:
                print("\n📭 No patterns recorded yet")
        
        else:
            parser.print_help()
    
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        engine.close()


if __name__ == "__main__":
    main()
