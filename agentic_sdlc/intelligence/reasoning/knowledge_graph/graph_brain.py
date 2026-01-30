import os
import sqlite3
import json
import hashlib
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def get_db_path():
    root = Path.cwd()
    dot_brain = root / ".brain"
    dot_brain.mkdir(parents=True, exist_ok=True)
    return dot_brain / "knowledge_graph.db"

class LocalKnowledgeGraph:
    """A unified local Knowledge Graph implementation using SQLite."""
    
    def __init__(self, db_path=None):
        self.db_path = db_path or get_db_path()
        self.conn = sqlite3.connect(self.db_path)
        self.conn.row_factory = sqlite3.Row
        self.initialize_schema()

    def close(self):
        self.conn.close()

    def initialize_schema(self):
        cursor = self.conn.cursor()
        # General Nodes Table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS nodes (
                id TEXT PRIMARY KEY,
                label TEXT,
                properties TEXT,
                last_updated TEXT
            )
        """)
        # Relationships Table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS relationships (
                source TEXT,
                target TEXT,
                type TEXT,
                properties TEXT,
                PRIMARY KEY (source, target, type),
                FOREIGN KEY (source) REFERENCES nodes(id),
                FOREIGN KEY (target) REFERENCES nodes(id)
            )
        """)
        # FTS Table for search
        cursor.execute("CREATE VIRTUAL TABLE IF NOT EXISTS node_search USING fts5(id, label, content)")
        self.conn.commit()
        print(f"[SUCCESS] Local Knowledge Graph initialized at {self.db_path}")

    def upsert_node(self, node_id: str, label: str, properties: Dict):
        cursor = self.conn.cursor()
        props_json = json.dumps(properties)
        now = datetime.now().isoformat()
        cursor.execute("""
            INSERT INTO nodes (id, label, properties, last_updated)
            VALUES (?, ?, ?, ?)
            ON CONFLICT(id) DO UPDATE SET
                properties = excluded.properties,
                last_updated = excluded.last_updated
        """, (node_id, label, props_json, now))
        
        # Update FTS
        search_content = f"{node_id} {label} {properties.get('title', '')} {properties.get('content_preview', '')}"
        cursor.execute("DELETE FROM node_search WHERE id = ?", (node_id,))
        cursor.execute("INSERT INTO node_search (id, label, content) VALUES (?, ?, ?)", 
                       (node_id, label, search_content))
        
        self.conn.commit()

    def create_relationship(self, source_id: str, target_id: str, rel_type: str, properties: Dict = None):
        cursor = self.conn.cursor()
        props_json = json.dumps(properties or {})
        cursor.execute("""
            INSERT INTO relationships (source, target, type, properties)
            VALUES (?, ?, ?, ?)
            ON CONFLICT(source, target, type) DO UPDATE SET
                properties = excluded.properties
        """, (source_id, target_id, rel_type, props_json))
        self.conn.commit()

    def find_nodes(self, label: str = None, query: str = None, limit: int = 10) -> List[Dict]:
        cursor = self.conn.cursor()
        if query:
            # Sanitize query for FTS5 (handle hyphens and special chars)
            # Wrap in double quotes to treat as a single phrase/safe string
            clean_query = query.replace('"', ' ')
            sanitized_query = f'"{clean_query}"'
            cursor.execute("""
                SELECT n.* FROM nodes n
                JOIN node_search s ON n.id = s.id
                WHERE s.content MATCH ?
                LIMIT ?
            """, (sanitized_query, limit))
        elif label:
            cursor.execute("SELECT * FROM nodes WHERE label = ? LIMIT ?", (label, limit))
        else:
            cursor.execute("SELECT * FROM nodes LIMIT ?", (limit,))
        
        results = []
        for row in cursor.fetchall():
            node = dict(row)
            node['properties'] = json.loads(node['properties'])
            results.append(node)
        return results

    def get_related(self, node_id: str, rel_type: str = None) -> List[Dict]:
        cursor = self.conn.cursor()
        if rel_type:
            cursor.execute("""
                SELECT n.* FROM nodes n
                JOIN relationships r ON n.id = r.target
                WHERE r.source = ? AND r.type = ?
            """, (node_id, rel_type))
        else:
            cursor.execute("""
                SELECT n.*, r.type as rel_type FROM nodes n
                JOIN relationships r ON n.id = r.target
                WHERE r.source = ?
            """, (node_id,))
        
        results = []
        for row in cursor.fetchall():
            node = dict(row)
            node['properties'] = json.loads(node['properties'])
            results.append(node)
        return results

if __name__ == "__main__":
    kg = LocalKnowledgeGraph()
    kg.upsert_node("test", "TestNode", {"title": "Hello World"})
    print("Nodes:", kg.find_nodes(query="Hello"))
    kg.close()



