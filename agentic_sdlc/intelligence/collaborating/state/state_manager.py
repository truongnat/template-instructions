"""
State Manager - Persistent workflow state and checkpointing.

Part of Layer 2: Intelligence Layer.
Enables crash recovery and session resumption for long-running SDLC workflows.
"""

import json
import sqlite3
import sys
import uuid
from contextlib import contextmanager
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

# Set UTF-8 encoding for Windows console
if sys.platform == 'win32':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
        sys.stderr.reconfigure(encoding='utf-8')
    except:
        pass


@dataclass
class Checkpoint:
    """Represents a workflow checkpoint for recovery."""
    id: str
    session_id: str
    phase: str
    data: Dict[str, Any]
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())
    
    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "session_id": self.session_id,
            "phase": self.phase,
            "data": self.data,
            "created_at": self.created_at
        }


@dataclass
class WorkflowSession:
    """Represents a persistent workflow session."""
    id: str
    workflow_name: str
    current_phase: str
    status: str  # active, paused, completed, failed
    completed_phases: List[str]
    artifacts: Dict[str, str]  # name -> path mapping
    metadata: Dict[str, Any]
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())
    updated_at: str = field(default_factory=lambda: datetime.now().isoformat())
    
    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "workflow_name": self.workflow_name,
            "current_phase": self.current_phase,
            "status": self.status,
            "completed_phases": self.completed_phases,
            "artifacts": self.artifacts,
            "metadata": self.metadata,
            "created_at": self.created_at,
            "updated_at": self.updated_at
        }


class StateManager:
    """
    Manages persistent workflow state with SQLite checkpointing.
    
    Features:
    - Create and manage workflow sessions
    - Save checkpoints at each phase
    - Restore from last checkpoint on crash
    - Track artifacts per session
    - Support multi-day workflows
    """
    
    SCHEMA = """
    CREATE TABLE IF NOT EXISTS workflow_sessions (
        id TEXT PRIMARY KEY,
        workflow_name TEXT NOT NULL,
        current_phase TEXT,
        status TEXT DEFAULT 'active',
        completed_phases TEXT DEFAULT '[]',
        artifacts TEXT DEFAULT '{}',
        metadata TEXT DEFAULT '{}',
        created_at TEXT,
        updated_at TEXT
    );
    
    CREATE TABLE IF NOT EXISTS checkpoints (
        id TEXT PRIMARY KEY,
        session_id TEXT NOT NULL,
        phase TEXT NOT NULL,
        data TEXT DEFAULT '{}',
        created_at TEXT,
        FOREIGN KEY (session_id) REFERENCES workflow_sessions(id)
    );
    
    CREATE TABLE IF NOT EXISTS session_artifacts (
        id TEXT PRIMARY KEY,
        session_id TEXT NOT NULL,
        name TEXT NOT NULL,
        path TEXT NOT NULL,
        checksum TEXT,
        created_at TEXT,
        FOREIGN KEY (session_id) REFERENCES workflow_sessions(id)
    );
    
    CREATE INDEX IF NOT EXISTS idx_checkpoints_session ON checkpoints(session_id);
    CREATE INDEX IF NOT EXISTS idx_artifacts_session ON session_artifacts(session_id);
    """
    
    def __init__(self, db_path: Optional[Path] = None):
        self.db_path = db_path or Path(__file__).resolve().parent.parent.parent.parent / "docs" / ".brain-state.db"
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._init_db()
        
    def _init_db(self):
        """Initialize the SQLite database with schema."""
        with self._get_connection() as conn:
            conn.executescript(self.SCHEMA)
            
    @contextmanager
    def _get_connection(self):
        """Get a database connection with context management."""
        conn = sqlite3.connect(str(self.db_path))
        conn.row_factory = sqlite3.Row
        try:
            yield conn
            conn.commit()
        finally:
            conn.close()
            
    # ==================== Session Management ====================
    
    def create_session(
        self,
        workflow_name: str,
        metadata: Optional[Dict] = None
    ) -> WorkflowSession:
        """
        Create a new workflow session.
        
        Args:
            workflow_name: Name of the workflow (e.g., 'orchestrator', 'cycle')
            metadata: Additional metadata for the session
            
        Returns:
            WorkflowSession object
        """
        session = WorkflowSession(
            id=str(uuid.uuid4())[:12],
            workflow_name=workflow_name,
            current_phase="init",
            status="active",
            completed_phases=[],
            artifacts={},
            metadata=metadata or {}
        )
        
        with self._get_connection() as conn:
            conn.execute("""
                INSERT INTO workflow_sessions 
                (id, workflow_name, current_phase, status, completed_phases, artifacts, metadata, created_at, updated_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                session.id,
                session.workflow_name,
                session.current_phase,
                session.status,
                json.dumps(session.completed_phases),
                json.dumps(session.artifacts),
                json.dumps(session.metadata),
                session.created_at,
                session.updated_at
            ))
            
        print(f"📝 Created session: {session.id} for workflow '{workflow_name}'")
        return session
        
    def get_session(self, session_id: str) -> Optional[WorkflowSession]:
        """Get a session by ID."""
        with self._get_connection() as conn:
            row = conn.execute(
                "SELECT * FROM workflow_sessions WHERE id = ?",
                (session_id,)
            ).fetchone()
            
            if row:
                return WorkflowSession(
                    id=row["id"],
                    workflow_name=row["workflow_name"],
                    current_phase=row["current_phase"],
                    status=row["status"],
                    completed_phases=json.loads(row["completed_phases"]),
                    artifacts=json.loads(row["artifacts"]),
                    metadata=json.loads(row["metadata"]),
                    created_at=row["created_at"],
                    updated_at=row["updated_at"]
                )
        return None
        
    def update_session(
        self,
        session_id: str,
        current_phase: Optional[str] = None,
        status: Optional[str] = None,
        completed_phases: Optional[List[str]] = None,
        artifacts: Optional[Dict[str, str]] = None,
        metadata: Optional[Dict] = None
    ) -> Optional[WorkflowSession]:
        """Update session fields."""
        session = self.get_session(session_id)
        if not session:
            return None
            
        updates = []
        params = []
        
        if current_phase:
            updates.append("current_phase = ?")
            params.append(current_phase)
            
        if status:
            updates.append("status = ?")
            params.append(status)
            
        if completed_phases is not None:
            updates.append("completed_phases = ?")
            params.append(json.dumps(completed_phases))
            
        if artifacts is not None:
            # Merge with existing artifacts
            merged = {**session.artifacts, **artifacts}
            updates.append("artifacts = ?")
            params.append(json.dumps(merged))
            
        if metadata is not None:
            # Merge with existing metadata
            merged = {**session.metadata, **metadata}
            updates.append("metadata = ?")
            params.append(json.dumps(merged))
            
        if updates:
            updates.append("updated_at = ?")
            params.append(datetime.now().isoformat())
            params.append(session_id)
            
            with self._get_connection() as conn:
                conn.execute(
                    f"UPDATE workflow_sessions SET {', '.join(updates)} WHERE id = ?",
                    params
                )
                
        return self.get_session(session_id)
        
    def complete_phase(self, session_id: str, phase: str) -> Optional[WorkflowSession]:
        """Mark a phase as completed and move to next."""
        session = self.get_session(session_id)
        if not session:
            return None
            
        completed = session.completed_phases + [phase]
        return self.update_session(
            session_id,
            completed_phases=completed
        )
        
    def list_sessions(self, status: Optional[str] = None) -> List[WorkflowSession]:
        """List all sessions, optionally filtered by status."""
        with self._get_connection() as conn:
            if status:
                rows = conn.execute(
                    "SELECT * FROM workflow_sessions WHERE status = ? ORDER BY updated_at DESC",
                    (status,)
                ).fetchall()
            else:
                rows = conn.execute(
                    "SELECT * FROM workflow_sessions ORDER BY updated_at DESC"
                ).fetchall()
                
            return [
                WorkflowSession(
                    id=row["id"],
                    workflow_name=row["workflow_name"],
                    current_phase=row["current_phase"],
                    status=row["status"],
                    completed_phases=json.loads(row["completed_phases"]),
                    artifacts=json.loads(row["artifacts"]),
                    metadata=json.loads(row["metadata"]),
                    created_at=row["created_at"],
                    updated_at=row["updated_at"]
                )
                for row in rows
            ]
            
    # ==================== Checkpoint Management ====================
    
    def save_checkpoint(
        self,
        session_id: str,
        phase: str,
        data: Dict[str, Any]
    ) -> Checkpoint:
        """
        Save a checkpoint for the current phase.
        
        Args:
            session_id: Session ID
            phase: Current phase name
            data: State data to save
            
        Returns:
            Checkpoint object
        """
        checkpoint = Checkpoint(
            id=str(uuid.uuid4())[:8],
            session_id=session_id,
            phase=phase,
            data=data
        )
        
        with self._get_connection() as conn:
            conn.execute("""
                INSERT INTO checkpoints (id, session_id, phase, data, created_at)
                VALUES (?, ?, ?, ?, ?)
            """, (
                checkpoint.id,
                checkpoint.session_id,
                checkpoint.phase,
                json.dumps(data),
                checkpoint.created_at
            ))
            
        # Update session current phase
        self.update_session(session_id, current_phase=phase)
        
        print(f"💾 Checkpoint saved: {checkpoint.id} at phase '{phase}'")
        return checkpoint
        
    def get_last_checkpoint(self, session_id: str) -> Optional[Checkpoint]:
        """Get the most recent checkpoint for a session."""
        with self._get_connection() as conn:
            row = conn.execute("""
                SELECT * FROM checkpoints 
                WHERE session_id = ? 
                ORDER BY created_at DESC 
                LIMIT 1
            """, (session_id,)).fetchone()
            
            if row:
                return Checkpoint(
                    id=row["id"],
                    session_id=row["session_id"],
                    phase=row["phase"],
                    data=json.loads(row["data"]),
                    created_at=row["created_at"]
                )
        return None
        
    def get_checkpoints(self, session_id: str) -> List[Checkpoint]:
        """Get all checkpoints for a session."""
        with self._get_connection() as conn:
            rows = conn.execute("""
                SELECT * FROM checkpoints 
                WHERE session_id = ? 
                ORDER BY created_at ASC
            """, (session_id,)).fetchall()
            
            return [
                Checkpoint(
                    id=row["id"],
                    session_id=row["session_id"],
                    phase=row["phase"],
                    data=json.loads(row["data"]),
                    created_at=row["created_at"]
                )
                for row in rows
            ]
            
    def restore_checkpoint(self, checkpoint_id: str) -> Optional[Dict]:
        """
        Restore from a specific checkpoint.
        
        Returns the checkpoint data for the caller to use.
        """
        with self._get_connection() as conn:
            row = conn.execute(
                "SELECT * FROM checkpoints WHERE id = ?",
                (checkpoint_id,)
            ).fetchone()
            
            if row:
                # Update session to reflect restored state
                self.update_session(
                    row["session_id"],
                    current_phase=row["phase"],
                    status="active"
                )
                
                print(f"🔄 Restored checkpoint: {checkpoint_id} at phase '{row['phase']}'")
                return json.loads(row["data"])
                
        return None
        
    # ==================== Recovery ====================
    
    def recover_session(self, session_id: str) -> Optional[Dict]:
        """
        Recover a session from its last checkpoint.
        
        Returns:
            Dict with session info and checkpoint data, or None if not found
        """
        session = self.get_session(session_id)
        if not session:
            print(f"❌ Session {session_id} not found")
            return None
            
        checkpoint = self.get_last_checkpoint(session_id)
        if not checkpoint:
            print(f"⚠️ No checkpoints found for session {session_id}")
            return {"session": session.to_dict(), "checkpoint": None}
            
        # Reactivate session if it was paused/failed
        if session.status in ["paused", "failed"]:
            session = self.update_session(session_id, status="active")
            
        print(f"🔄 Recovered session {session_id} at phase '{checkpoint.phase}'")
        
        return {
            "session": session.to_dict(),
            "checkpoint": checkpoint.to_dict(),
            "resume_from": checkpoint.phase
        }
        
    def get_active_sessions(self) -> List[WorkflowSession]:
        """Get all active sessions that may need recovery."""
        return self.list_sessions(status="active")
        
    # ==================== Cleanup ====================
    
    def archive_session(self, session_id: str) -> bool:
        """Mark a session as completed and archive it."""
        session = self.get_session(session_id)
        if session:
            self.update_session(session_id, status="completed")
            print(f"📦 Session {session_id} archived")
            return True
        return False
        
    def delete_old_sessions(self, days: int = 30) -> int:
        """Delete sessions older than specified days."""
        from datetime import timedelta
        
        cutoff = (datetime.now() - timedelta(days=days)).isoformat()
        
        with self._get_connection() as conn:
            # Delete checkpoints first
            conn.execute("""
                DELETE FROM checkpoints 
                WHERE session_id IN (
                    SELECT id FROM workflow_sessions 
                    WHERE status = 'completed' AND updated_at < ?
                )
            """, (cutoff,))
            
            # Delete sessions
            cursor = conn.execute("""
                DELETE FROM workflow_sessions 
                WHERE status = 'completed' AND updated_at < ?
            """, (cutoff,))
            
            deleted = cursor.rowcount
            print(f"🗑️ Deleted {deleted} old sessions")
            return deleted


def main():
    """CLI entry point."""
    import argparse
    
    parser = argparse.ArgumentParser(description="State Manager - Workflow State and Checkpointing")
    subparsers = parser.add_subparsers(dest="command", help="Available commands")
    
    # Create session
    create_parser = subparsers.add_parser("create", help="Create a new session")
    create_parser.add_argument("workflow", help="Workflow name")
    
    # List sessions
    list_parser = subparsers.add_parser("list", help="List sessions")
    list_parser.add_argument("--status", choices=["active", "paused", "completed", "failed"], help="Filter by status")
    
    # Get session
    get_parser = subparsers.add_parser("get", help="Get session details")
    get_parser.add_argument("session_id", help="Session ID")
    
    # Save checkpoint
    checkpoint_parser = subparsers.add_parser("checkpoint", help="Save checkpoint")
    checkpoint_parser.add_argument("session_id", help="Session ID")
    checkpoint_parser.add_argument("phase", help="Phase name")
    checkpoint_parser.add_argument("--data", default="{}", help="JSON data to save")
    
    # Recover session
    recover_parser = subparsers.add_parser("recover", help="Recover session from last checkpoint")
    recover_parser.add_argument("session_id", help="Session ID")
    
    # Archive session
    archive_parser = subparsers.add_parser("archive", help="Archive completed session")
    archive_parser.add_argument("session_id", help="Session ID")
    
    # Cleanup
    cleanup_parser = subparsers.add_parser("cleanup", help="Delete old completed sessions")
    cleanup_parser.add_argument("--days", type=int, default=30, help="Delete sessions older than X days")
    
    args = parser.parse_args()
    manager = StateManager()
    
    if args.command == "create":
        session = manager.create_session(args.workflow)
        print(f"  ID: {session.id}")
        
    elif args.command == "list":
        sessions = manager.list_sessions(args.status)
        if not sessions:
            print("📭 No sessions found")
        else:
            print(f"📋 Sessions ({len(sessions)}):\n")
            for s in sessions:
                print(f"  [{s.id}] {s.workflow_name} - {s.status}")
                print(f"      Phase: {s.current_phase}")
                print(f"      Updated: {s.updated_at}")
                print()
                
    elif args.command == "get":
        session = manager.get_session(args.session_id)
        if session:
            print(json.dumps(session.to_dict(), indent=2))
        else:
            print(f"Session {args.session_id} not found")
            
    elif args.command == "checkpoint":
        data = json.loads(args.data)
        manager.save_checkpoint(args.session_id, args.phase, data)
        
    elif args.command == "recover":
        result = manager.recover_session(args.session_id)
        if result:
            print(json.dumps(result, indent=2))
            
    elif args.command == "archive":
        manager.archive_session(args.session_id)
        
    elif args.command == "cleanup":
        manager.delete_old_sessions(args.days)
        
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
