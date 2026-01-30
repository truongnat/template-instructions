import os
import re
import sys
import hashlib
import json
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional, Tuple
from dotenv import load_dotenv
import argparse

# Add project root to path for imports
ROOT_DIR = Path(__file__).resolve().parents[4]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from agentic_sdlc.intelligence.reasoning.knowledge_graph.graph_brain import LocalKnowledgeGraph

# Load environment variables
load_dotenv()

class DocumentSyncLocal:
    """Universal document sync to Local SQLite Knowledge Graph."""
    
    def __init__(self):
        self.kg = LocalKnowledgeGraph()
        print("✅ DocumentSync connected to Local Knowledge Graph")

    def close(self):
        self.kg.close()

    def generate_document_id(self, file_path: Path) -> str:
        """Generate unique document ID from file path"""
        path_str = str(file_path.resolve())
        return hashlib.sha256(path_str.encode()).hexdigest()[:16]

    def determine_document_type(self, file_path: Path) -> str:
        """Determine document type from file path and name"""
        filename = file_path.name.lower()
        if filename.startswith('kb-'): return 'Knowledge'
        elif 'plan' in filename: return 'Plan'
        elif 'report' in filename: return 'Report'
        elif 'spec' in filename or 'design' in filename: return 'Artifact'
        elif '.agent/workflows' in str(file_path): return 'Workflow'
        return 'Document'

    def parse_document(self, file_path: Path) -> Optional[Dict]:
        """Parse a document file and extract metadata"""
        try:
            content = file_path.read_text(encoding='utf-8')
            doc_id = self.generate_document_id(file_path)
            doc_type = self.determine_document_type(file_path)
            
            # Simple title extraction
            title_match = re.search(r'^#\s+(.+)$', content, re.MULTILINE)
            title = title_match.group(1).strip() if title_match else file_path.name
            
            # Extract author
            author_match = re.search(r'author:\s*(@?\w+)', content, re.IGNORECASE)
            author = author_match.group(1) if author_match else '@SYSTEM'
            
            return {
                'id': doc_id,
                'title': title,
                'type': doc_type,
                'author': author,
                'file_path': str(file_path.resolve()),
                'content_preview': content[:500].replace('\n', ' '),
                'date': datetime.now().strftime('%Y-%m-%d')
            }
        except Exception as e:
            print(f"  ❌ Error parsing {file_path}: {e}")
            return None

    def sync_document(self, doc: Dict):
        """Sync a single document to the local graph"""
        self.kg.upsert_node(doc['id'], doc['type'], doc)
        # Link to author
        author_id = f"ROLE-{doc['author'].upper()}"
        self.kg.upsert_node(author_id, "Role", {"name": doc['author']})
        self.kg.create_relationship(doc['id'], author_id, "CREATED_BY")
        print(f"  ✅ {doc['type']}: {doc['title']}")

def main():
    parser = argparse.ArgumentParser(description='Sync documents to Local Knowledge Graph')
    parser.add_argument('--base-path', default='.', help='Base project path')
    args = parser.parse_args()
    
    sync = DocumentSyncLocal()
    base_path = Path(args.base_path)
    
    # Find all markdown files (excluding some dirs)
    md_files = []
    ignore_dirs = {'.git', 'node_modules', '__pycache__'}
    
    for root, dirs, files in os.walk(base_path):
        dirs[:] = [d for d in dirs if d not in ignore_dirs]
        for file in files:
            if file.endswith('.md'):
                md_files.append(Path(root) / file)
                
    print(f"\n📚 Found {len(md_files)} documents to sync")
    
    synced_count = 0
    for doc_path in md_files:
        doc = sync.parse_document(doc_path)
        if doc:
            sync.sync_document(doc)
            synced_count += 1
            
    print(f"\n✅ Successfully synced {synced_count} documents to local graph!")
    sync.close()

if __name__ == "__main__":
    main()
