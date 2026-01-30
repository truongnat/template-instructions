import os
import re
import sys
import json
import sqlite3
import hashlib
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional, Tuple
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def get_db_path():
    root = Path.cwd()
    dot_brain = root / ".brain"
    dot_brain.mkdir(parents=True, exist_ok=True)
    return dot_brain / "learning_engine.db"

class LearningEngine:
    """Self-learning engine using local SQLite instead of Memgraph."""
    
    def __init__(self, db_path=None):
        self.db_path = db_path or get_db_path()
        self.conn = sqlite3.connect(self.db_path)
        self.conn.row_factory = sqlite3.Row
        self.create_learning_schema()
    
    def close(self):
        self.conn.close()
    
    def create_learning_schema(self):
        cursor = self.conn.cursor()
        # Errors table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS errors (
                id TEXT PRIMARY KEY,
                type TEXT,
                message TEXT,
                context TEXT,
                first_seen TEXT,
                last_seen TEXT,
                occurrence_count INTEGER DEFAULT 0
            )
        """)
        # Resolutions table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS resolutions (
                id TEXT PRIMARY KEY,
                description TEXT,
                approach TEXT,
                created_at TEXT,
                success_count INTEGER DEFAULT 0
            )
        """)
        # Error-Resolution links
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS error_resolutions (
                error_id TEXT,
                resolution_id TEXT,
                last_used TEXT,
                use_count INTEGER DEFAULT 0,
                PRIMARY KEY (error_id, resolution_id),
                FOREIGN KEY (error_id) REFERENCES errors(id),
                FOREIGN KEY (resolution_id) REFERENCES resolutions(id)
            )
        """)
        # Patterns table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS patterns (
                id TEXT PRIMARY KEY,
                type TEXT,
                approach TEXT,
                last_success TEXT,
                success_count INTEGER DEFAULT 0,
                total_confidence REAL DEFAULT 0
            )
        """)
        # Learnings table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS learnings (
                id TEXT PRIMARY KEY,
                title TEXT,
                category TEXT,
                insight TEXT,
                source_type TEXT,
                created_at TEXT,
                confidence REAL DEFAULT 1.0,
                applied_count INTEGER DEFAULT 0
            )
        """)
        self.conn.commit()
    
    def generate_id(self, prefix: str, content: str) -> str:
        hash_str = hashlib.sha256(f"{prefix}_{content}".encode()).hexdigest()[:12]
        return f"{prefix}_{hash_str}"
    
    def record_error(self, error_type: str, message: str, context: Dict = None, 
                    resolution: str = None, resolution_approach: str = None) -> str:
        cursor = self.conn.cursor()
        error_id = self.generate_id("ERR", f"{error_type}_{message[:50]}")
        now = datetime.now().isoformat()
        
        cursor.execute("""
            INSERT INTO errors (id, type, message, context, first_seen, last_seen, occurrence_count)
            VALUES (?, ?, ?, ?, ?, ?, 1)
            ON CONFLICT(id) DO UPDATE SET
                last_seen = excluded.last_seen,
                occurrence_count = occurrence_count + 1
        """, (error_id, error_type, message, json.dumps(context or {}), now, now))
        
        if resolution:
            resolution_id = self.generate_id("RES", resolution[:50])
            cursor.execute("""
                INSERT INTO resolutions (id, description, approach, created_at, success_count)
                VALUES (?, ?, ?, ?, 1)
                ON CONFLICT(id) DO UPDATE SET
                    success_count = success_count + 1
            """, (resolution_id, resolution, resolution_approach or "manual fix", now))
            
            cursor.execute("""
                INSERT INTO error_resolutions (error_id, resolution_id, last_used, use_count)
                VALUES (?, ?, ?, 1)
                ON CONFLICT(error_id, resolution_id) DO UPDATE SET
                    last_used = excluded.last_used,
                    use_count = use_count + 1
            """, (error_id, resolution_id, now))
            
        self.conn.commit()
        return error_id

    def find_similar_errors(self, error_message: str, limit: int = 5) -> List[Dict]:
        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT e.* FROM errors e
            WHERE message LIKE ? OR type LIKE ?
            ORDER BY occurrence_count DESC
            LIMIT ?
        """, (f"%{error_message}%", f"%{error_message}%", limit))
        
        errors = [dict(row) for row in cursor.fetchall()]
        for err in errors:
            cursor.execute("""
                SELECT r.* FROM resolutions r
                JOIN error_resolutions er ON r.id = er.resolution_id
                WHERE er.error_id = ?
            """, (err['id'],))
            err['resolutions'] = [dict(r) for r in cursor.fetchall()]
            
        return errors

    def record_success(self, task_id: str, task_type: str, approach: str, 
                      outcome: str = "completed", confidence: float = 1.0) -> str:
        cursor = self.conn.cursor()
        pattern_id = self.generate_id("PAT", f"{task_type}_{approach[:30]}")
        now = datetime.now().isoformat()
        
        cursor.execute("""
            INSERT INTO patterns (id, type, approach, last_success, success_count, total_confidence)
            VALUES (?, ?, ?, ?, 1, ?)
            ON CONFLICT(id) DO UPDATE SET
                last_success = excluded.last_success,
                success_count = success_count + 1,
                total_confidence = total_confidence + excluded.total_confidence
        """, (pattern_id, task_type, approach, now, confidence))
        
        self.conn.commit()
        return pattern_id

    def get_recommendations(self, task_description: str, limit: int = 5) -> List[Dict]:
        keywords = self._extract_keywords(task_description)
        recommendations = []
        cursor = self.conn.cursor()
        
        for keyword in keywords[:5]:
            cursor.execute("""
                SELECT * FROM patterns 
                WHERE approach LIKE ? OR type LIKE ?
                ORDER BY success_count DESC LIMIT 3
            """, (f"%{keyword}%", f"%{keyword}%"))
            for row in cursor.fetchall():
                rec = dict(row)
                rec['source'] = 'pattern'
                recommendations.append(rec)
        
        # Deduplicate
        seen = set()
        unique = []
        for rec in recommendations:
            if rec['id'] not in seen:
                seen.add(rec['id'])
                unique.append(rec)
        return unique[:limit]

    def _extract_keywords(self, text: str) -> List[str]:
        stopwords = {'the', 'a', 'an', 'is', 'are', 'was', 'were', 'be', 'been', 'have', 'has', 'had'}
        words = re.findall(r'\b[a-zA-Z]{3,}\b', text.lower())
        return [w for w in words if w not in stopwords]

    def get_learning_stats(self) -> Dict:
        cursor = self.conn.cursor()
        stats = {}
        cursor.execute("SELECT count(*) FROM errors")
        stats['errors_tracked'] = cursor.fetchone()[0]
        cursor.execute("SELECT count(*) FROM resolutions")
        stats['resolutions'] = cursor.fetchone()[0]
        cursor.execute("SELECT count(*) FROM patterns")
        stats['patterns'] = cursor.fetchone()[0]
        cursor.execute("SELECT count(*) FROM learnings")
        stats['learnings'] = cursor.fetchone()[0]
        return stats

def main():
    parser = argparse.ArgumentParser(description='Local Learning Engine (SQLite)')
    parser.add_argument('--stats', action='store_true', help='Show statistics')
    parser.add_argument('--recommend', help='Get recommendations')
    args = parser.parse_args()
    
    engine = LearningEngine()
    if args.stats:
        print(json.dumps(engine.get_learning_stats(), indent=2))
    elif args.recommend:
        recs = engine.get_recommendations(args.recommend)
        for r in recs:
            print(f"- {r['approach']} (Success: {r['success_count']})")
    engine.close()

if __name__ == "__main__":
    import argparse
    main()


