#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Tests for Intelligence Layer Components (Refactored)

Tests for: Observer, Judge, Learner
"""

import pytest
import json
import sys
from pathlib import Path
from unittest.mock import patch, MagicMock

# Add project root to path so we can import 'tools'
sys.path.insert(0, str(Path(__file__).parents[1])) 

# Current file is tests/test_brain_components.py (level 1)
# Root is parents[1] -> D:\dev\agentic-sdlc

from agentic_sdlc.intelligence.monitoring.observer.observer import Observer, Violation
from agentic_sdlc.intelligence.monitoring.judge.scorer import Judge, ScoreResult
from agentic_sdlc.intelligence.learning.self_learning.learner import Learner, PatternType

class TestObserver:
    """Tests for Observer component."""
    
    def test_observe_action(self):
        observer = Observer()
        # Test code quality check
        context = {
            "file_path": "test.py",
            "content": "def complex():\n" + " if x: pass\n" * 12 # High complexity
        }
        observer.observe_action("DEV", "file_create", context)
        
        assert len(observer.violations) > 0
        assert observer.violations[0].type == "code_quality"
        assert "complexity" in observer.violations[0].description

    def test_naming_convention(self):
        observer = Observer()
        context = {
            "file_path": "CamelCase.py",
            "content": "pass"
        }
        observer.observe_action("DEV", "file_create", context)
        
        assert len(observer.violations) > 0
        assert observer.violations[0].type == "naming"
        assert "snake_case" in observer.violations[0].rule

    def test_compliance_score(self):
        observer = Observer()
        assert observer.get_compliance_score() == 100.0
        
        # Simulate an action so score calculation kicks in
        observer.actions_monitored = 1
        
        # Add critical violation
        observer.report_violation(Violation(
            type="security",
            severity="CRITICAL",
            rule="No secrets",
            location="file.py",
            description="Found secret",
            recommendation="Remove it"
        ))
        
        score = observer.get_compliance_score()
        assert score < 100.0


class TestJudge:
    """Tests for Judge component."""
    
    @pytest.fixture
    def judge(self, tmp_path):
        scores_file = tmp_path / "scores.json"
        return Judge(scores_file=scores_file)
    
    def test_score_code_quality(self, judge, tmp_path):
        # Create a good quality file
        code_file = tmp_path / "good.py"
        code_file.write_text("import os\n\ndef my_func():\n    '''Docstring'''\n    try:\n        pass\n    except:\n        pass\n", encoding='utf-8')
        
        result = judge.score(str(code_file))
        
        assert result.file_type == "code"
        assert result.passed is True
        assert result.scores["structure"] > 0
        assert result.scores["quality"] > 0

    def test_score_report_completeness(self, judge, tmp_path):
        # Create a generic report
        report_file = tmp_path / "report.md"
        report_file.write_text("# Title\n\n## Problem\n...\n## Solution\n...", encoding='utf-8')
        
        result = judge.score(str(report_file))
        
        assert result.file_type == "report"
        assert result.scores["completeness"] > 0


class TestLearner:
    """Tests for Learner component."""
    
    @pytest.fixture
    def learner(self, tmp_path):
        log_file = tmp_path / "learner.json"
        return Learner(storage_file=log_file)
    
    def test_learn_record(self, learner):
        result = learner.learn("Implemented new feature")
        assert result["recorded"] is True
        assert len(learner.events) == 1
        
    def test_learn_error_pattern(self, learner):
        result = learner.learn_error("Connection refused", "Retry with backoff")
        
        assert result["recorded"] is True
        assert len(learner.patterns) == 1
        
        pattern = list(learner.patterns.values())[0]
        assert pattern.type == PatternType.ERROR
        assert pattern.trigger == "Connection refused"

    def test_get_recommendation(self, learner):
        # Seed a success pattern
        learner.learn_success("Optimize query", "Use index")
        
        rec = learner.get_recommendation("Optimize query")
        assert rec is not None
        assert rec["recommendation"] == "Use index"

if __name__ == "__main__":
    pytest.main([__file__, "-v"])