#!/usr/bin/env python3
"""
Auto-sync Knowledge Base Skills to Neo4j Cloud (AuraDB)

This script automatically syncs knowledge base entries to Neo4j graph database,
creating a knowledge graph of skills, technologies, and relationships.

Usage:
    python bin/sync_skills_to_neo4j.py
    python bin/sync_skills_to_neo4j.py --kb-path .agent/knowledge-base
    python bin/sync_skills_to_neo4j.py --dry-run
"""

import os
import re
import json
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional
from dotenv import load_dotenv
from neo4j import GraphDatabase
import argparse

# Load environment variables
load_dotenv()


class Neo4jSkillSync:
    """Sync knowledge base skills to Neo4j Cloud"""
    
    def __init__(self, uri: str, user: str, password: str, database: str = "neo4j"):
        """Initialize Neo4j connection"""
        self.driver = GraphDatabase.driver(
            uri,
            auth=(user, password)
        )
        self.database = database
        print(f"✅ Connected to Neo4j Cloud: {uri}")
    
    def close(self):
        """Close Neo4j connection"""
        self.driver.close()
        print("✅ Neo4j connection closed")
    
    def create_constraints(self):
        """Create unique constraints for nodes"""
        constraints = [
            "CREATE CONSTRAINT skill_id IF NOT EXISTS FOR (s:Skill) REQUIRE s.id IS UNIQUE",
            "CREATE CONSTRAINT kb_entry_id IF NOT EXISTS FOR (k:KBEntry) REQUIRE k.id IS UNIQUE",
            "CREATE CONSTRAINT category_name IF NOT EXISTS FOR (c:Category) REQUIRE c.name IS UNIQUE",
            "CREATE CONSTRAINT technology_name IF NOT EXISTS FOR (t:Technology) REQUIRE t.name IS UNIQUE",
            "CREATE CONSTRAINT person_name IF NOT EXISTS FOR (p:Person) REQUIRE p.name IS UNIQUE",
        ]
        
        with self.driver.session(database=self.database) as session:
            for constraint in constraints:
                try:
                    session.run(constraint)
                    print(f"✅ Created constraint: {constraint.split('FOR')[1].split('REQUIRE')[0].strip()}")
                except Exception as e:
                    if "already exists" not in str(e).lower():
                        print(f"⚠️  Constraint warning: {e}")
    
    def create_indexes(self):
        """Create indexes for better query performance"""
        indexes = [
            "CREATE INDEX skill_name IF NOT EXISTS FOR (s:Skill) ON (s.name)",
            "CREATE INDEX kb_entry_title IF NOT EXISTS FOR (k:KBEntry) ON (k.title)",
            "CREATE INDEX technology_name IF NOT EXISTS FOR (t:Technology) ON (t.name)",
        ]
        
        with self.driver.session(database=self.database) as session:
            for index in indexes:
                try:
                    session.run(index)
                    print(f"✅ Created index: {index.split('FOR')[1].split('ON')[0].strip()}")
                except Exception as e:
                    if "already exists" not in str(e).lower():
                        print(f"⚠️  Index warning: {e}")
    
    def parse_kb_entry(self, file_path: Path) -> Optional[Dict]:
        """Parse knowledge base markdown file"""
        try:
            content = file_path.read_text(encoding='utf-8')
            
            # Extract metadata
            entry_id = file_path.stem
            title_match = re.search(r'^#\s+(.+)$', content, re.MULTILINE)
            title = title_match.group(1) if title_match else file_path.stem
            
            # Extract date
            date_match = re.search(r'\*\*Date:\*\*\s+(\d{4}-\d{2}-\d{2})', content)
            date = date_match.group(1) if date_match else datetime.now().strftime('%Y-%m-%d')
            
            # Extract category
            category_match = re.search(r'\*\*Category:\*\*\s+(.+)', content)
            category = category_match.group(1).strip() if category_match else "General"
            
            # Extract prepared by
            author_match = re.search(r'\*\*Prepared By:\*\*\s+(@\w+)', content)
            author = author_match.group(1) if author_match else "@UNKNOWN"
            
            # Extract tags
            tags_match = re.findall(r'#([\w-]+)', content)
            tags = list(set(tags_match))  # Remove duplicates
            
            # Extract technologies/skills mentioned
            technologies = self._extract_technologies(content)
            skills = self._extract_skills(content, title)
            
            return {
                'id': entry_id,
                'title': title,
                'date': date,
                'category': category,
                'author': author,
                'tags': tags,
                'technologies': technologies,
                'skills': skills,
                'file_path': str(file_path),
                'content_length': len(content)
            }
        except Exception as e:
            print(f"❌ Error parsing {file_path}: {e}")
            return None
    
    def _extract_technologies(self, content: str) -> List[str]:
        """Extract technology names from content"""
        tech_patterns = [
            r'\b(Neo4j|Cypher|AuraDB|Figma|Adobe XD|Sketch|Framer|React|Vue|Angular|Python|JavaScript|TypeScript|Java|Node\.js|HTML|CSS)\b',
            r'\b(GraphQL|REST|API|SQL|NoSQL|MongoDB|PostgreSQL|Redis|Docker|Kubernetes|AWS|Azure|GCP)\b',
            r'\b(Git|GitHub|GitLab|CI/CD|Jenkins|Webpack|Vite|Next\.js|Astro|Tailwind|Bootstrap)\b',
        ]
        
        technologies = set()
        for pattern in tech_patterns:
            matches = re.findall(pattern, content, re.IGNORECASE)
            technologies.update(matches)
        
        return list(technologies)
    
    def _extract_skills(self, content: str, title: str) -> List[Dict]:
        """Extract skills from content"""
        skills = []
        
        # Extract from headers
        skill_headers = re.findall(r'###?\s+\d+\.?\d*\.?\s*(.+)', content)
        for skill in skill_headers[:20]:  # Limit to first 20
            clean_skill = re.sub(r'[#*`]', '', skill).strip()
            if len(clean_skill) > 5 and len(clean_skill) < 100:
                skills.append({
                    'name': clean_skill,
                    'level': 'intermediate',
                    'source': 'header'
                })
        
        # Extract from bullet points with skill indicators
        skill_bullets = re.findall(r'[-*]\s+\*\*(.+?)\*\*', content)
        for skill in skill_bullets[:15]:  # Limit to first 15
            clean_skill = re.sub(r'[:#]', '', skill).strip()
            if len(clean_skill) > 5 and len(clean_skill) < 100:
                skills.append({
                    'name': clean_skill,
                    'level': 'beginner',
                    'source': 'bullet'
                })
        
        return skills
    
    def sync_kb_entry(self, entry: Dict, dry_run: bool = False):
        """Sync single KB entry to Neo4j"""
        if dry_run:
            print(f"\n📝 [DRY RUN] Would sync: {entry['title']}")
            print(f"   - Category: {entry['category']}")
            print(f"   - Technologies: {', '.join(entry['technologies'][:5])}")
            print(f"   - Skills: {len(entry['skills'])} skills")
            return
        
        with self.driver.session(database=self.database) as session:
            # Create KB Entry node
            session.run("""
                MERGE (k:KBEntry {id: $id})
                SET k.title = $title,
                    k.date = date($date),
                    k.category = $category,
                    k.author = $author,
                    k.file_path = $file_path,
                    k.content_length = $content_length,
                    k.updated_at = datetime()
            """, **entry)
            
            # Create Category node and relationship
            session.run("""
                MATCH (k:KBEntry {id: $id})
                MERGE (c:Category {name: $category})
                MERGE (k)-[:BELONGS_TO]->(c)
            """, id=entry['id'], category=entry['category'])
            
            # Create Person node and relationship
            session.run("""
                MATCH (k:KBEntry {id: $id})
                MERGE (p:Person {name: $author})
                MERGE (p)-[:CREATED]->(k)
            """, id=entry['id'], author=entry['author'])
            
            # Create Technology nodes and relationships
            for tech in entry['technologies']:
                session.run("""
                    MATCH (k:KBEntry {id: $id})
                    MERGE (t:Technology {name: $tech})
                    MERGE (k)-[:USES_TECHNOLOGY]->(t)
                """, id=entry['id'], tech=tech)
            
            # Create Skill nodes and relationships
            for skill in entry['skills']:
                session.run("""
                    MATCH (k:KBEntry {id: $kb_id})
                    MERGE (s:Skill {name: $skill_name})
                    SET s.level = $level,
                        s.source = $source
                    MERGE (k)-[:TEACHES]->(s)
                """, 
                    kb_id=entry['id'],
                    skill_name=skill['name'],
                    level=skill['level'],
                    source=skill['source']
                )
            
            # Create Tag relationships
            for tag in entry['tags']:
                session.run("""
                    MATCH (k:KBEntry {id: $id})
                    MERGE (k)-[:TAGGED_WITH {tag: $tag}]->(k)
                """, id=entry['id'], tag=tag)
            
            print(f"✅ Synced: {entry['title']}")
    
    def create_skill_relationships(self):
        """Create relationships between related skills"""
        with self.driver.session(database=self.database) as session:
            # Connect skills that appear in same KB entry
            session.run("""
                MATCH (k:KBEntry)-[:TEACHES]->(s1:Skill)
                MATCH (k)-[:TEACHES]->(s2:Skill)
                WHERE s1 <> s2
                MERGE (s1)-[r:RELATED_TO]-(s2)
                ON CREATE SET r.strength = 1
                ON MATCH SET r.strength = r.strength + 1
            """)
            
            # Connect technologies to skills
            session.run("""
                MATCH (k:KBEntry)-[:USES_TECHNOLOGY]->(t:Technology)
                MATCH (k)-[:TEACHES]->(s:Skill)
                MERGE (t)-[r:REQUIRES_SKILL]->(s)
                ON CREATE SET r.strength = 1
                ON MATCH SET r.strength = r.strength + 1
            """)
            
            print("✅ Created skill relationships")
    
    def get_stats(self) -> Dict:
        """Get knowledge graph statistics"""
        with self.driver.session(database=self.database) as session:
            result = session.run("""
                MATCH (k:KBEntry) WITH count(k) as kb_count
                MATCH (s:Skill) WITH kb_count, count(s) as skill_count
                MATCH (t:Technology) WITH kb_count, skill_count, count(t) as tech_count
                MATCH (c:Category) WITH kb_count, skill_count, tech_count, count(c) as cat_count
                RETURN kb_count, skill_count, tech_count, cat_count
            """)
            
            record = result.single()
            return {
                'kb_entries': record['kb_count'],
                'skills': record['skill_count'],
                'technologies': record['tech_count'],
                'categories': record['cat_count']
            }


def main():
    """Main execution function"""
    parser = argparse.ArgumentParser(description='Sync Knowledge Base to Neo4j')
    parser.add_argument('--kb-path', default='.agent/knowledge-base', help='Path to knowledge base')
    parser.add_argument('--dry-run', action='store_true', help='Dry run without syncing')
    parser.add_argument('--stats-only', action='store_true', help='Show stats only')
    args = parser.parse_args()
    
    # Get Neo4j credentials from environment
    uri = os.getenv('NEO4J_URI')
    username = os.getenv('NEO4J_USERNAME')
    password = os.getenv('NEO4J_PASSWORD')
    database = os.getenv('NEO4J_DATABASE', 'neo4j')
    
    if not all([uri, username, password]):
        print("❌ Error: Neo4j credentials not found in .env file")
        print("   Required: NEO4J_URI, NEO4J_USERNAME, NEO4J_PASSWORD")
        return
    
    # Initialize Neo4j sync
    sync = Neo4jSkillSync(uri, username, password, database)
    
    try:
        # Show stats if requested
        if args.stats_only:
            stats = sync.get_stats()
            print("\n📊 Knowledge Graph Statistics:")
            print(f"   KB Entries: {stats['kb_entries']}")
            print(f"   Skills: {stats['skills']}")
            print(f"   Technologies: {stats['technologies']}")
            print(f"   Categories: {stats['categories']}")
            return
        
        # Create constraints and indexes
        if not args.dry_run:
            print("\n🔧 Setting up database schema...")
            sync.create_constraints()
            sync.create_indexes()
        
        # Find all KB markdown files
        kb_path = Path(args.kb_path)
        kb_files = list(kb_path.rglob('KB-*.md'))
        
        print(f"\n📚 Found {len(kb_files)} knowledge base entries")
        
        # Parse and sync each entry
        synced_count = 0
        for kb_file in kb_files:
            entry = sync.parse_kb_entry(kb_file)
            if entry:
                sync.sync_kb_entry(entry, dry_run=args.dry_run)
                synced_count += 1
        
        # Create relationships
        if not args.dry_run and synced_count > 0:
            print("\n🔗 Creating skill relationships...")
            sync.create_skill_relationships()
        
        # Show final stats
        if not args.dry_run:
            print("\n📊 Final Statistics:")
            stats = sync.get_stats()
            print(f"   KB Entries: {stats['kb_entries']}")
            print(f"   Skills: {stats['skills']}")
            print(f"   Technologies: {stats['technologies']}")
            print(f"   Categories: {stats['categories']}")
        
        print(f"\n✅ Successfully synced {synced_count} KB entries!")
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        sync.close()


if __name__ == "__main__":
    main()
