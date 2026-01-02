#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Universal Document Sync to Neo4j Cloud (AuraDB)

This script syncs ALL generated documents (plans, reports, artifacts, workflows)
to Neo4j graph database, creating a comprehensive project knowledge graph.

Features:
- Syncs all document types (not just KB entries)
- Extracts rich metadata from YAML frontmatter
- Creates versioning relationships (SUPERCEDES)
- Links documents to sprints, tasks, and roles
- Semantic content chunking for large documents

Usage:
    python tools/neo4j/document_sync.py --all
    python tools/neo4j/document_sync.py --type plans
    python tools/neo4j/document_sync.py --type reports
    python tools/neo4j/document_sync.py --dry-run
"""

import os
import re
import sys
import hashlib
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


# Document type configurations
DOCUMENT_TYPES = {
    'plans': {
        'patterns': ['**/Project-Plan*.md', '**/Sprint-Plan*.md', '**/DevOps-Plan*.md'],
        'label': 'Plan',
        'directories': ['docs/sprints', 'docs/plans']
    },
    'reports': {
        'patterns': ['**/Phase-Report*.md', '**/Test-Report*.md', '**/Progress-Report*.md', '**/Metrics-Report*.md'],
        'label': 'Report',
        'directories': ['docs/sprints', 'docs/reports']
    },
    'artifacts': {
        'patterns': ['**/*-Spec*.md', '**/Design-*.md', '**/Architecture-*.md'],
        'label': 'Artifact',
        'directories': ['docs/sprints', 'docs/architecture']
    },
    'workflows': {
        'patterns': ['**/.agent/workflows/*.md'],
        'label': 'Workflow',
        'directories': ['.agent/workflows']
    },
    'knowledge': {
        'patterns': ['**/KB-*.md'],
        'label': 'KBEntry',
        'directories': ['.agent/knowledge-base']
    },
    'conversations': {
        'patterns': ['**/chat-log*.md', '**/conversation*.md'],
        'label': 'Conversation',
        'directories': ['docs/communications']
    }
}


class DocumentSyncNeo4j:
    """Universal document sync to Neo4j Cloud"""
    
    def __init__(self, uri: str, user: str, password: str, database: str = "neo4j"):
        """Initialize Neo4j connection"""
        self.driver = GraphDatabase.driver(uri, auth=(user, password))
        self.database = database
        print(f"✅ Connected to Neo4j Cloud: {uri}")
    
    def close(self):
        """Close Neo4j connection"""
        self.driver.close()
        print("✅ Neo4j connection closed")
    
    def create_document_schema(self):
        """Create schema for document nodes"""
        constraints = [
            "CREATE CONSTRAINT document_id IF NOT EXISTS FOR (d:Document) REQUIRE d.id IS UNIQUE",
            "CREATE CONSTRAINT artifact_id IF NOT EXISTS FOR (a:Artifact) REQUIRE a.id IS UNIQUE",
            "CREATE CONSTRAINT plan_id IF NOT EXISTS FOR (p:Plan) REQUIRE p.id IS UNIQUE",
            "CREATE CONSTRAINT report_id IF NOT EXISTS FOR (r:Report) REQUIRE r.id IS UNIQUE",
            "CREATE CONSTRAINT workflow_id IF NOT EXISTS FOR (w:Workflow) REQUIRE w.id IS UNIQUE",
            "CREATE CONSTRAINT sprint_id IF NOT EXISTS FOR (s:Sprint) REQUIRE s.id IS UNIQUE",
            "CREATE CONSTRAINT task_id IF NOT EXISTS FOR (t:Task) REQUIRE t.id IS UNIQUE",
            "CREATE CONSTRAINT role_name IF NOT EXISTS FOR (r:Role) REQUIRE r.name IS UNIQUE",
            "CREATE CONSTRAINT chunk_id IF NOT EXISTS FOR (c:ContentChunk) REQUIRE c.id IS UNIQUE",
        ]
        
        indexes = [
            "CREATE INDEX document_title IF NOT EXISTS FOR (d:Document) ON (d.title)",
            "CREATE INDEX document_type IF NOT EXISTS FOR (d:Document) ON (d.type)",
            "CREATE INDEX document_date IF NOT EXISTS FOR (d:Document) ON (d.created_date)",
            "CREATE FULLTEXT INDEX document_content IF NOT EXISTS FOR (d:Document) ON EACH [d.content_preview]",
        ]
        
        with self.driver.session(database=self.database) as session:
            print("\n🔧 Setting up document schema...")
            
            for constraint in constraints:
                try:
                    session.run(constraint)
                    node_type = constraint.split('FOR')[1].split('REQUIRE')[0].strip()
                    print(f"  ✅ Constraint: {node_type}")
                except Exception as e:
                    if "already exists" not in str(e).lower():
                        print(f"  ⚠️  Constraint warning: {e}")
            
            for index in indexes:
                try:
                    session.run(index)
                    index_name = index.split('INDEX')[1].split('IF')[0].strip()
                    print(f"  ✅ Index: {index_name}")
                except Exception as e:
                    if "already exists" not in str(e).lower() and "equivalent" not in str(e).lower():
                        print(f"  ⚠️  Index warning: {e}")
    
    def generate_document_id(self, file_path: Path) -> str:
        """Generate unique document ID from file path"""
        path_str = str(file_path.resolve())
        return hashlib.sha256(path_str.encode()).hexdigest()[:16]
    
    def extract_version(self, filename: str) -> Tuple[int, Optional[str]]:
        """Extract version number from filename"""
        # Match patterns like v1, v2, -v1, _v1
        match = re.search(r'[-_]?v(\d+)', filename, re.IGNORECASE)
        if match:
            return int(match.group(1)), match.group(0)
        return 1, None
    
    def extract_sprint(self, file_path: Path) -> Optional[str]:
        """Extract sprint number from file path"""
        path_str = str(file_path)
        # Match sprint-N, sprint_N, sprintN
        match = re.search(r'sprint[-_]?(\d+)', path_str, re.IGNORECASE)
        if match:
            return f"sprint-{match.group(1)}"
        return None
    
    def parse_frontmatter(self, content: str) -> Dict:
        """Parse YAML frontmatter from markdown content"""
        metadata = {}
        match = re.match(r'^---\s*\n(.*?)\n---\s*\n', content, re.DOTALL)
        
        if match:
            frontmatter = match.group(1)
            # Parse YAML-like key: value pairs
            for line in frontmatter.split('\n'):
                if ':' in line:
                    key, value = line.split(':', 1)
                    key = key.strip().lower().replace('-', '_')
                    value = value.strip().strip('"\'')
                    metadata[key] = value
        
        return metadata
    
    def extract_title(self, content: str, filename: str) -> str:
        """Extract document title"""
        # Try first H1 header
        match = re.search(r'^#\s+(.+)$', content, re.MULTILINE)
        if match:
            return match.group(1).strip()
        return filename.replace('.md', '').replace('-', ' ').replace('_', ' ')
    
    def extract_author(self, content: str) -> str:
        """Extract author/role from content"""
        # Try various patterns
        patterns = [
            r'\*\*(?:Prepared By|Author|Created By):\*\*\s*(@?\w+)',
            r'author:\s*(@?\w+)',
            r'created_by:\s*(@?\w+)',
        ]
        for pattern in patterns:
            match = re.search(pattern, content, re.IGNORECASE)
            if match:
                return match.group(1)
        return '@SYSTEM'
    
    def extract_references(self, content: str, base_path: Path) -> List[str]:
        """Extract document references/links"""
        references = []
        # Match markdown links
        link_pattern = r'\[([^\]]+)\]\(([^)]+\.md)\)'
        for match in re.finditer(link_pattern, content):
            ref_path = match.group(2)
            # Convert to absolute path
            if not ref_path.startswith('/') and not ref_path.startswith('file:'):
                ref_path = str((base_path.parent / ref_path).resolve())
            references.append(ref_path)
        return references[:20]  # Limit references
    
    def chunk_content(self, content: str, chunk_size: int = 1000) -> List[Dict]:
        """Split content into semantic chunks for large documents"""
        chunks = []
        
        # Split by headers first
        sections = re.split(r'(^##?\s+.+$)', content, flags=re.MULTILINE)
        
        current_chunk = ""
        current_header = ""
        chunk_index = 0
        
        for section in sections:
            if re.match(r'^##?\s+', section):
                # This is a header
                if current_chunk and len(current_chunk) > 100:
                    chunks.append({
                        'index': chunk_index,
                        'header': current_header,
                        'content': current_chunk[:chunk_size],
                        'length': len(current_chunk)
                    })
                    chunk_index += 1
                current_header = section.strip()
                current_chunk = ""
            else:
                current_chunk += section
        
        # Add last chunk
        if current_chunk and len(current_chunk) > 100:
            chunks.append({
                'index': chunk_index,
                'header': current_header,
                'content': current_chunk[:chunk_size],
                'length': len(current_chunk)
            })
        
        return chunks
    
    def determine_document_type(self, file_path: Path) -> str:
        """Determine document type from file path and name"""
        path_str = str(file_path).lower()
        filename = file_path.name.lower()
        
        if filename.startswith('kb-'):
            return 'KBEntry'
        elif 'plan' in filename:
            return 'Plan'
        elif 'report' in filename or 'metrics' in filename:
            return 'Report'
        elif 'spec' in filename or 'design' in filename or 'architecture' in filename:
            return 'Artifact'
        elif '.agent/workflows' in path_str:
            return 'Workflow'
        elif 'conversation' in filename or 'chat' in filename:
            return 'Conversation'
        else:
            return 'Document'
    
    def parse_document(self, file_path: Path) -> Optional[Dict]:
        """Parse a document file and extract all metadata"""
        try:
            content = file_path.read_text(encoding='utf-8')
            
            # Basic info
            doc_id = self.generate_document_id(file_path)
            version, version_str = self.extract_version(file_path.name)
            sprint = self.extract_sprint(file_path)
            doc_type = self.determine_document_type(file_path)
            
            # Parse frontmatter
            frontmatter = self.parse_frontmatter(content)
            
            # Extract content info
            title = frontmatter.get('title') or self.extract_title(content, file_path.name)
            author = frontmatter.get('author') or self.extract_author(content)
            date = frontmatter.get('date') or datetime.now().strftime('%Y-%m-%d')
            
            # Get statistics
            word_count = len(content.split())
            line_count = len(content.split('\n'))
            
            # Extract references
            references = self.extract_references(content, file_path)
            
            # Chunk large documents
            chunks = []
            if len(content) > 5000:
                chunks = self.chunk_content(content)
            
            # Content preview (first 500 chars without frontmatter)
            content_clean = re.sub(r'^---.*?---\s*', '', content, flags=re.DOTALL)
            content_preview = content_clean[:500].replace('\n', ' ')
            
            return {
                'id': doc_id,
                'title': title,
                'type': doc_type,
                'author': author,
                'date': date,
                'version': version,
                'sprint': sprint,
                'file_path': str(file_path.resolve()),
                'relative_path': str(file_path),
                'word_count': word_count,
                'line_count': line_count,
                'content_length': len(content),
                'content_preview': content_preview,
                'references': references,
                'chunks': chunks,
                'frontmatter': frontmatter
            }
        except Exception as e:
            print(f"  ❌ Error parsing {file_path}: {e}")
            return None
    
    def sync_document(self, doc: Dict, dry_run: bool = False):
        """Sync a single document to Neo4j"""
        if dry_run:
            print(f"  📄 [DRY RUN] {doc['type']}: {doc['title']}")
            print(f"      Version: v{doc['version']} | Sprint: {doc['sprint'] or 'N/A'}")
            return
        
        with self.driver.session(database=self.database) as session:
            # Create main Document node with type label
            labels = f"Document:{doc['type']}"
            session.run(f"""
                MERGE (d:{labels} {{id: $id}})
                SET d.title = $title,
                    d.type = $type,
                    d.author = $author,
                    d.created_date = date($date),
                    d.version = $version,
                    d.file_path = $file_path,
                    d.relative_path = $relative_path,
                    d.word_count = $word_count,
                    d.line_count = $line_count,
                    d.content_length = $content_length,
                    d.content_preview = $content_preview,
                    d.synced_at = datetime()
            """, 
                id=doc['id'],
                title=doc['title'],
                type=doc['type'],
                author=doc['author'],
                date=doc['date'],
                version=doc['version'],
                file_path=doc['file_path'],
                relative_path=doc['relative_path'],
                word_count=doc['word_count'],
                line_count=doc['line_count'],
                content_length=doc['content_length'],
                content_preview=doc['content_preview']
            )
            
            # Create Role node and CREATED_BY relationship
            if doc['author']:
                session.run("""
                    MATCH (d:Document {id: $doc_id})
                    MERGE (r:Role {name: $author})
                    MERGE (d)-[:CREATED_BY]->(r)
                """, doc_id=doc['id'], author=doc['author'])
            
            # Create Sprint node and BELONGS_TO relationship
            if doc['sprint']:
                session.run("""
                    MATCH (d:Document {id: $doc_id})
                    MERGE (s:Sprint {id: $sprint})
                    MERGE (d)-[:BELONGS_TO]->(s)
                """, doc_id=doc['id'], sprint=doc['sprint'])
            
            # Create content chunks for large documents
            for chunk in doc['chunks']:
                chunk_id = f"{doc['id']}_chunk_{chunk['index']}"
                session.run("""
                    MATCH (d:Document {id: $doc_id})
                    MERGE (c:ContentChunk {id: $chunk_id})
                    SET c.index = $index,
                        c.header = $header,
                        c.content = $content,
                        c.length = $length
                    MERGE (d)-[:HAS_CHUNK]->(c)
                """,
                    doc_id=doc['id'],
                    chunk_id=chunk_id,
                    index=chunk['index'],
                    header=chunk['header'],
                    content=chunk['content'],
                    length=chunk['length']
                )
            
            print(f"  ✅ {doc['type']}: {doc['title']}")
    
    def create_reference_relationships(self):
        """Create REFERENCES relationships between documents"""
        print("\n🔗 Creating document references...")
        
        with self.driver.session(database=self.database) as session:
            # Connect documents that reference each other
            result = session.run("""
                MATCH (d1:Document)
                WHERE d1.file_path IS NOT NULL
                MATCH (d2:Document)
                WHERE d2.file_path IS NOT NULL AND d1 <> d2
                AND (d1.content_preview CONTAINS d2.title OR d1.relative_path CONTAINS d2.relative_path)
                MERGE (d1)-[r:REFERENCES]->(d2)
                RETURN count(r) as ref_count
            """)
            record = result.single()
            print(f"  ✅ Created {record['ref_count']} reference relationships")
    
    def create_version_chain(self):
        """Create SUPERCEDES relationships for versioned documents"""
        print("\n🔗 Creating version chains...")
        
        with self.driver.session(database=self.database) as session:
            # Connect versions of same document
            result = session.run("""
                MATCH (d1:Document), (d2:Document)
                WHERE d1 <> d2 
                AND d1.title = d2.title 
                AND d1.version > d2.version
                MERGE (d1)-[r:SUPERCEDES]->(d2)
                RETURN count(r) as chain_count
            """)
            record = result.single()
            print(f"  ✅ Created {record['chain_count']} version chain relationships")
    
    def get_document_stats(self) -> Dict:
        """Get document graph statistics"""
        with self.driver.session(database=self.database) as session:
            result = session.run("""
                MATCH (d:Document) WITH count(d) as doc_count
                OPTIONAL MATCH (p:Plan) WITH doc_count, count(p) as plan_count
                OPTIONAL MATCH (r:Report) WITH doc_count, plan_count, count(r) as report_count
                OPTIONAL MATCH (a:Artifact) WITH doc_count, plan_count, report_count, count(a) as artifact_count
                OPTIONAL MATCH (w:Workflow) WITH doc_count, plan_count, report_count, artifact_count, count(w) as workflow_count
                OPTIONAL MATCH (s:Sprint) WITH doc_count, plan_count, report_count, artifact_count, workflow_count, count(s) as sprint_count
                OPTIONAL MATCH (c:ContentChunk) WITH doc_count, plan_count, report_count, artifact_count, workflow_count, sprint_count, count(c) as chunk_count
                RETURN doc_count, plan_count, report_count, artifact_count, workflow_count, sprint_count, chunk_count
            """)
            record = result.single()
            return {
                'documents': record['doc_count'],
                'plans': record['plan_count'],
                'reports': record['report_count'],
                'artifacts': record['artifact_count'],
                'workflows': record['workflow_count'],
                'sprints': record['sprint_count'],
                'chunks': record['chunk_count']
            }


def find_documents(base_path: Path, doc_types: List[str] = None) -> List[Path]:
    """Find all document files based on type filters"""
    documents = []
    
    if doc_types is None or 'all' in doc_types:
        doc_types = list(DOCUMENT_TYPES.keys())
    
    for doc_type in doc_types:
        if doc_type not in DOCUMENT_TYPES:
            continue
        
        config = DOCUMENT_TYPES[doc_type]
        for directory in config['directories']:
            dir_path = base_path / directory
            if dir_path.exists():
                for pattern in config['patterns']:
                    # Use rglob for recursive search
                    pattern_base = pattern.replace('**/', '')
                    documents.extend(dir_path.rglob(pattern_base))
    
    # Also add any markdown files in docs/sprints
    sprints_dir = base_path / 'docs' / 'sprints'
    if sprints_dir.exists():
        for md_file in sprints_dir.rglob('*.md'):
            if md_file not in documents:
                documents.append(md_file)
    
    # Remove duplicates
    return list(set(documents))


def main():
    """Main execution function"""
    parser = argparse.ArgumentParser(description='Sync all documents to Neo4j')
    parser.add_argument('--all', action='store_true', help='Sync all document types')
    parser.add_argument('--type', nargs='+', choices=list(DOCUMENT_TYPES.keys()) + ['all'], 
                        default=['all'], help='Document types to sync')
    parser.add_argument('--base-path', default='.', help='Base project path')
    parser.add_argument('--dry-run', action='store_true', help='Preview without syncing')
    parser.add_argument('--stats-only', action='store_true', help='Show stats only')
    args = parser.parse_args()
    
    # Get Neo4j credentials
    uri = os.getenv('NEO4J_URI')
    username = os.getenv('NEO4J_USERNAME')
    password = os.getenv('NEO4J_PASSWORD')
    database = os.getenv('NEO4J_DATABASE', 'neo4j')
    
    if not all([uri, username, password]):
        print("❌ Error: Neo4j credentials not found in .env file")
        print("   Required: NEO4J_URI, NEO4J_USERNAME, NEO4J_PASSWORD")
        return
    
    # Initialize sync
    sync = DocumentSyncNeo4j(uri, username, password, database)
    
    try:
        # Stats only mode
        if args.stats_only:
            stats = sync.get_document_stats()
            print("\n📊 Document Graph Statistics:")
            print(f"   Total Documents: {stats['documents']}")
            print(f"   Plans: {stats['plans']}")
            print(f"   Reports: {stats['reports']}")
            print(f"   Artifacts: {stats['artifacts']}")
            print(f"   Workflows: {stats['workflows']}")
            print(f"   Sprints: {stats['sprints']}")
            print(f"   Content Chunks: {stats['chunks']}")
            return
        
        # Create schema
        if not args.dry_run:
            sync.create_document_schema()
        
        # Find documents
        base_path = Path(args.base_path)
        doc_types = ['all'] if args.all else args.type
        documents = find_documents(base_path, doc_types)
        
        print(f"\n📚 Found {len(documents)} documents to sync")
        
        # Parse and sync each document
        synced_count = 0
        for doc_path in documents:
            doc = sync.parse_document(doc_path)
            if doc:
                sync.sync_document(doc, dry_run=args.dry_run)
                synced_count += 1
        
        # Create relationships
        if not args.dry_run and synced_count > 0:
            sync.create_reference_relationships()
            sync.create_version_chain()
        
        # Final stats
        if not args.dry_run:
            print("\n📊 Final Statistics:")
            stats = sync.get_document_stats()
            print(f"   Total Documents: {stats['documents']}")
            print(f"   Plans: {stats['plans']}")
            print(f"   Reports: {stats['reports']}")
            print(f"   Artifacts: {stats['artifacts']}")
            print(f"   Workflows: {stats['workflows']}")
            print(f"   Sprints: {stats['sprints']}")
            print(f"   Content Chunks: {stats['chunks']}")
        
        print(f"\n✅ Successfully synced {synced_count} documents!")
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        sync.close()


if __name__ == "__main__":
    main()
