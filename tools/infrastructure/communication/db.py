import sqlite3
import os
from datetime import datetime
import json

DB_PATH = os.path.join(os.path.dirname(__file__), "chat.db")

def get_db_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db_connection()
    c = conn.cursor()
    
    # Enable foreign keys
    c.execute("PRAGMA foreign_keys = ON;")
    
    # Roles table
    c.execute('''
        CREATE TABLE IF NOT EXISTS roles (
            id TEXT PRIMARY KEY,
            description TEXT
        )
    ''')
    
    # Channels table
    c.execute('''
        CREATE TABLE IF NOT EXISTS channels (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT UNIQUE NOT NULL,
            description TEXT,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Threads table
    c.execute('''
        CREATE TABLE IF NOT EXISTS threads (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            channel_id INTEGER NOT NULL,
            title TEXT,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (channel_id) REFERENCES channels (id)
        )
    ''')
    
    # Messages table
    c.execute('''
        CREATE TABLE IF NOT EXISTS messages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            thread_id INTEGER NOT NULL,
            role_id TEXT NOT NULL,
            content TEXT NOT NULL,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
            metadata TEXT,
            FOREIGN KEY (thread_id) REFERENCES threads (id),
            FOREIGN KEY (role_id) REFERENCES roles (id)
        )
    ''')
    
    # Seed default roles
    default_roles = [
        ('PM', 'Project Manager'),
        ('DEV', 'Developer'),
        ('QA', 'Quality Assurance'),
        ('SA', 'System Architect'),
        ('DEVOPS', 'DevOps Engineer'),
        ('UIUX', 'UI/UX Designer'),
        ('USER', 'The User'),
        ('BRAIN', 'The LEANN Brain')
    ]
    
    c.executemany('INSERT OR IGNORE INTO roles (id, description) VALUES (?, ?)', default_roles)
    
    # Seed default channel
    c.execute("INSERT OR IGNORE INTO channels (name, description) VALUES ('general', 'General Project Discussion')")
    
    conn.commit()
    conn.close()

if __name__ == "__main__":
    init_db()
    print(f"Database initialized at {DB_PATH}")
