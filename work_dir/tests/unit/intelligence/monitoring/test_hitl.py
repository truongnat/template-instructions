#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Tests for HITL (Human-in-the-Loop) Manager

Tests for: Approval Gates, Request Lifecycle, Persistence
"""

import pytest
import json
import sys
import shutil
from pathlib import Path
from unittest.mock import patch, MagicMock

# imports should work via conftest path setup

from agentic_sdlc.intelligence.monitoring.hitl.hitl_manager import HITLManager, ApprovalGate, ApprovalStatus, ApprovalRequest

class TestHITLManager:
    """Tests for HITL Manager component."""
    
    @pytest.fixture
    def hitl_manager(self, tmp_path):
        """Create a HITLManager with a temporary storage directory."""
        storage_dir = tmp_path / ".hitl"
        return HITLManager(storage_dir=storage_dir)

    def test_request_approval(self, hitl_manager):
        """Test creating an approval request."""
        req = hitl_manager.request_approval(
            gate=ApprovalGate.CODE_REVIEW,
            session_id="test-session-123",
            artifact_paths=["src/main.py"],
            context={"author": "AI"}
        )
        
        assert req.gate == ApprovalGate.CODE_REVIEW
        assert req.status == ApprovalStatus.PENDING
        assert req.session_id == "test-session-123"
        assert req.artifact_paths == ["src/main.py"]
        
        # Verify it's in pending list
        pending = hitl_manager.list_pending()
        assert len(pending) == 1
        assert pending[0].id == req.id

    def test_approve_request(self, hitl_manager):
        """Test approving a request."""
        req = hitl_manager.request_approval(
            gate=ApprovalGate.DEPLOYMENT,
            session_id="deploy-1",
            artifact_paths=[]
        )
        
        result = hitl_manager.approve(
            request_id=req.id,
            reviewer="Admin",
            reason="Looks good"
        )
        
        assert result.approved is True
        assert result.reviewer == "Admin"
        
        # Verify status update
        updated_req = hitl_manager.check_status(req.id)
        assert updated_req.status == ApprovalStatus.APPROVED
        assert updated_req.reviewer == "Admin"
        
        # Verify removed from pending
        assert len(hitl_manager.list_pending()) == 0

    def test_reject_request(self, hitl_manager):
        """Test rejecting a request."""
        req = hitl_manager.request_approval(
            gate=ApprovalGate.SECURITY_REVIEW,
            session_id="sec-1",
            artifact_paths=[]
        )
        
        result = hitl_manager.reject(
            request_id=req.id,
            reviewer="SecOps",
            reason="Vulnerability found"
        )
        
        assert result.approved is False
        
        # Verify status update
        updated_req = hitl_manager.check_status(req.id)
        assert updated_req.status == ApprovalStatus.REJECTED
        assert updated_req.decision_reason == "Vulnerability found"

    def test_persistence(self, tmp_path):
        """Test that requests persist across manager instances."""
        storage_dir = tmp_path / ".hitl"
        
        # Instance 1: Create request
        manager1 = HITLManager(storage_dir=storage_dir)
        req = manager1.request_approval(ApprovalGate.PLANNING, "s1", [])
        
        # Instance 2: Load request
        manager2 = HITLManager(storage_dir=storage_dir)
        loaded_req = manager2.check_status(req.id)
        
        assert loaded_req is not None
        assert loaded_req.id == req.id
        assert len(manager2.list_pending()) == 1

    def test_unknown_request_error(self, hitl_manager):
        """Test operations on non-existent requests raise error."""
        with pytest.raises(ValueError):
            hitl_manager.approve("fake-id")
            
        with pytest.raises(ValueError):
            hitl_manager.reject("fake-id", reason="bad")

    def test_wait_for_approval_timeout(self, hitl_manager):
        """Test the wait_for_approval timeout logic."""
        req = hitl_manager.request_approval(ApprovalGate.CUSTOM, "s2", [])
        
        # We mock time.sleep to avoid actual waiting and time.time to simulate passage of time
        # But for a simple unit test, we can just set a very short timeout and let it expire naturally
        # or mock the status check.
        
        # Method 1: Let it expire (requires real time wait, so we set timeout=0.1s)
        success = hitl_manager.wait_for_approval(req.id, check_interval=0.1, timeout=0.2)
        assert success is False
        
        # Check that it marked as expired
        updated_req = hitl_manager.check_status(req.id)
        assert updated_req.status == ApprovalStatus.EXPIRED

if __name__ == "__main__":
    pytest.main([__file__, "-v"])
