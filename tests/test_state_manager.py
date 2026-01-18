#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Tests for State Manager

Tests for: Session persistence, Checkpointing, Recovery, Cleanup
"""

import pytest
import json
import sys
import sqlite3
from pathlib import Path
from unittest.mock import patch, MagicMock

# Add tools to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from agentic_sdlc.intelligence.state.state_manager import StateManager, WorkflowSession, Checkpoint

class TestStateManager:
    """Tests for State Manager component."""
    
    @pytest.fixture
    def state_manager(self, tmp_path):
        """Create a StateManager with a temporary database."""
        db_path = tmp_path / "test_state.db"
        return StateManager(db_path=db_path)

    def test_create_session(self, state_manager):
        """Test creating a new session."""
        session = state_manager.create_session("test-workflow", {"user": "test"})
        
        assert session.workflow_name == "test-workflow"
        assert session.status == "active"
        assert session.metadata["user"] == "test"
        assert session.current_phase == "init"
        
        # Verify persistence
        loaded = state_manager.get_session(session.id)
        assert loaded.id == session.id
        assert loaded.workflow_name == "test-workflow"

    def test_update_session(self, state_manager):
        """Test updating session fields."""
        session = state_manager.create_session("update-workflow")
        
        updated = state_manager.update_session(
            session.id,
            current_phase="phase-1",
            status="paused",
            completed_phases=["init"],
            artifacts={"log": "log.txt"}
        )
        
        assert updated.current_phase == "phase-1"
        assert updated.status == "paused"
        assert "init" in updated.completed_phases
        assert updated.artifacts["log"] == "log.txt"

    def test_checkpointing(self, state_manager):
        """Test saving and restoring checkpoints."""
        session = state_manager.create_session("checkpoint-workflow")
        
        # Save checkpoint
        data = {"count": 1, "step": "A"}
        cp = state_manager.save_checkpoint(session.id, "step-A", data)
        
        assert cp.phase == "step-A"
        assert cp.data == data
        
        # Verify session phase updated
        loaded_session = state_manager.get_session(session.id)
        assert loaded_session.current_phase == "step-A"
        
        # Get checkpoints
        checkpoints = state_manager.get_checkpoints(session.id)
        assert len(checkpoints) == 1
        assert checkpoints[0].id == cp.id
        
        # Restore
        restored_data = state_manager.restore_checkpoint(cp.id)
        assert restored_data == data

    def test_recover_session(self, state_manager):
        """Test recovering a session from last checkpoint."""
        session = state_manager.create_session("recover-workflow")
        state_manager.save_checkpoint(session.id, "phase-1", {"val": 1})
        state_manager.save_checkpoint(session.id, "phase-2", {"val": 2})
        
        # Mark as failed to simulate crash
        state_manager.update_session(session.id, status="failed")
        
        # Recover
        recovery = state_manager.recover_session(session.id)
        
        assert recovery["session"]["status"] == "active" # Should auto-activate
        assert recovery["resume_from"] == "phase-2"
        assert recovery["checkpoint"]["data"]["val"] == 2

    def test_cleanup(self, state_manager):
        """Test cleaning up old sessions."""
        # Create session
        s1 = state_manager.create_session("old-workflow")
        
        # Manually update updated_at to be old
        with state_manager._get_connection() as conn:
            conn.execute(
                "UPDATE workflow_sessions SET updated_at = '2020-01-01T00:00:00', status = 'completed' WHERE id = ?",
                (s1.id,)
            )
            
        # Create new session
        s2 = state_manager.create_session("new-workflow")
        state_manager.update_session(s2.id, status="completed")
        
        # Cleanup > 30 days
        deleted = state_manager.delete_old_sessions(days=30)
        
        assert deleted >= 1
        assert state_manager.get_session(s1.id) is None
        assert state_manager.get_session(s2.id) is not None

if __name__ == "__main__":
    pytest.main([__file__, "-v"])
