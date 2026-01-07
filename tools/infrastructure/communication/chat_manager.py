import sqlite3
import json
from .db import get_db_connection, init_db

class ChatManager:
    def __init__(self):
        # Ensure DB is initialized
        init_db()

    def create_channel(self, name, description=""):
        conn = get_db_connection()
        c = conn.cursor()
        try:
            c.execute("INSERT INTO channels (name, description) VALUES (?, ?)", (name, description))
            conn.commit()
            return c.lastrowid
        except sqlite3.IntegrityError:
            # Check if it exists to return id
            c.execute("SELECT id FROM channels WHERE name = ?", (name,))
            res = c.fetchone()
            return res['id'] if res else None
        finally:
            conn.close()

    def create_thread(self, channel_name, title):
        conn = get_db_connection()
        c = conn.cursor()
        try:
            # Get channel ID
            c.execute("SELECT id FROM channels WHERE name = ?", (channel_name,))
            channel = c.fetchone()
            if not channel:
                raise ValueError(f"Channel '{channel_name}' not found")
            
            c.execute("INSERT INTO threads (channel_id, title) VALUES (?, ?)", (channel['id'], title))
            conn.commit()
            return c.lastrowid
        finally:
            conn.close()

    def send_message(self, channel_name, thread_title, role_id, content, metadata=None):
        conn = get_db_connection()
        c = conn.cursor()
        try:
            # Get Channel ID
            c.execute("SELECT id FROM channels WHERE name = ?", (channel_name,))
            channel = c.fetchone()
            if not channel:
                raise ValueError(f"Channel '{channel_name}' not found")
            channel_id = channel['id']

            # Get or Create Thread ID
            c.execute("SELECT id FROM threads WHERE channel_id = ? AND title = ?", (channel_id, thread_title))
            thread = c.fetchone()
            if thread:
                thread_id = thread['id']
            else:
                c.execute("INSERT INTO threads (channel_id, title) VALUES (?, ?)", (channel_id, thread_title))
                thread_id = c.lastrowid

            # Insert Message
            meta_json = json.dumps(metadata) if metadata else None
            c.execute("INSERT INTO messages (thread_id, role_id, content, metadata) VALUES (?, ?, ?, ?)", 
                      (thread_id, role_id, content, meta_json))
            conn.commit()
            return c.lastrowid
        finally:
            conn.close()

    def get_history(self, channel_name=None, thread_title=None, limit=50):
        # ... implementation for retrieval ...
        conn = get_db_connection()
        c = conn.cursor()
        query = '''
            SELECT m.id, m.timestamp, m.role_id, m.content, t.title as thread_title, c.name as channel_name
            FROM messages m
            JOIN threads t ON m.thread_id = t.id
            JOIN channels c ON t.channel_id = c.id
            WHERE 1=1
        '''
        params = []
        if channel_name:
            query += " AND c.name = ?"
            params.append(channel_name)
        if thread_title:
            query += " AND t.title = ?"
            params.append(thread_title)
        
        query += " ORDER BY m.timestamp DESC LIMIT ?"
        params.append(limit)
        
        c.execute(query, params)
        rows = c.fetchall()
        conn.close()
        
        # Return reversed to show chronological order
        return [dict(row) for row in rows][::-1]

    def list_channels(self):
        conn = get_db_connection()
        c = conn.cursor()
        c.execute("SELECT * FROM channels")
        rows = c.fetchall()
        conn.close()
        return [dict(row) for row in rows]
    
    def list_threads(self, channel_name):
        conn = get_db_connection()
        c = conn.cursor()
        c.execute('''
            SELECT t.* FROM threads t
            JOIN channels c ON t.channel_id = c.id
            WHERE c.name = ?
        ''', (channel_name,))
        rows = c.fetchall()
        conn.close()
        return [dict(row) for row in rows]
