#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Tests for Self-Healing

Tests for: Feedback Loop, Pattern Learning, Escalation
"""

import pytest
import json
import sys
from pathlib import Path
from unittest.mock import patch, MagicMock

# Add tools to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from agentic_sdlc.intelligence.self_healing.self_healer import (
    FeedbackLoop, HealingResult, Issue, IssueSeverity, FixStatus
)

class TestSelfHealing:
    """Tests for Self-Healing component."""
    
    @pytest.fixture
    def feedback_loop(self, tmp_path):
        """Create a FeedbackLoop with temporary storage."""
        storage_dir = tmp_path / ".self-healing"
        return FeedbackLoop(max_iterations=3, storage_dir=storage_dir)

    def test_clean_code_pass(self, feedback_loop):
        """Test that code with no issues passes immediately."""
        # Mock QA to return empty list (no issues)
        feedback_loop.set_qa_agent(lambda code, req: [])
        
        result = feedback_loop.run("print('hello')", "requirements")
        
        assert result.success is True
        assert result.iterations == 1
        assert result.issues_found == 0
        assert result.final_code == "print('hello')"

    def test_fix_success(self, feedback_loop):
        """Test successful fix in one iteration."""
        # Mock QA to return issue first time, then none
        qa_calls = 0
        def mock_qa(code, req):
            nonlocal qa_calls
            qa_calls += 1
            if qa_calls == 1:
                return [Issue("1", "lint", IssueSeverity.LOW, "Missing semi-colon")]
            return []
            
        # Mock DEV to fix the code
        def mock_dev(code, issues):
            return code + ";"
            
        feedback_loop.set_qa_agent(mock_qa)
        feedback_loop.set_dev_agent(mock_dev)
        
        result = feedback_loop.run("x=1", "req")
        
        assert result.success is True
        assert result.iterations == 2 # 1st fail, 2nd pass
        assert result.issues_fixed == 1
        assert result.final_code == "x=1;"

    def test_escalation(self, feedback_loop):
        """Test escalation when max iterations reached."""
        # QA always finds issues
        feedback_loop.set_qa_agent(lambda code, req: [
            Issue("1", "bug", IssueSeverity.HIGH, "Bug persists")
        ])
        
        # DEV tries but fails to fix (returns same code or slightly diff but still buggy)
        feedback_loop.set_dev_agent(lambda code, issues: code + " (tried)")
        
        result = feedback_loop.run("buggy", "req")
        
        assert result.success is False
        assert result.iterations == 3 # max_iterations
        assert result.escalated is True
        assert "Could not resolve" in result.escalation_reason

    def test_pattern_learning(self, feedback_loop):
        """Test that successful fixes are learned."""
        # Setup a success scenario
        feedback_loop.set_qa_agent(lambda c, r: [] if ";" in c else [
            Issue("1", "syntax", IssueSeverity.MEDIUM, "Missing ;", suggested_fix="Add ;")
        ])
        feedback_loop.set_dev_agent(lambda c, i: c + ";")
        
        feedback_loop.run("x=1", "req")
        
        # Verify pattern file
        assert feedback_loop.patterns_file.exists()
        patterns = json.loads(feedback_loop.patterns_file.read_text(encoding='utf-8'))
        assert len(patterns) == 1
        assert patterns[0]["type"] == "syntax"
        assert patterns[0]["fix"] == "Add ;"

    def test_check_patterns(self, feedback_loop):
        """Test that known patterns are detected."""
        # Pre-seed a pattern
        pattern = {
            "type": "test_pattern",
            "severity": "low",
            "description_match": "Always fail",
            "fix": "Do not fail",
            "learned_at": "2023-01-01"
        }
        feedback_loop.patterns_file.write_text(json.dumps([pattern]), encoding='utf-8')
        
        # QA returns matching issue
        issue = Issue("1", "test_pattern", IssueSeverity.LOW, "Always fail here")
        matches = feedback_loop._check_patterns([issue])
        
        assert len(matches) == 1
        assert matches[0]["suggested_fix"] == "Do not fail"

if __name__ == "__main__":
    pytest.main([__file__, "-v"])
