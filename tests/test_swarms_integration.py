#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Tests for Swarms-inspired Intelligence Layer Components
"""

import pytest
import json
import os
import sys
from pathlib import Path
from unittest.mock import patch, MagicMock

# Add project root to path
sys.path.insert(0, str(Path(__file__).parents[1]))

from agentic_sdlc.intelligence.router.workflow_router import WorkflowRouter, ExecutionMode
from agentic_sdlc.intelligence.concurrent_executor import ConcurrentExecutor
from agentic_sdlc.intelligence.synthesizer import OutputSynthesizer
from agentic_sdlc.intelligence.feedback_protocol import FeedbackProtocol
from agentic_sdlc.intelligence.group_chat import GroupChat
from agentic_sdlc.intelligence.auto_skill_builder import AutoSkillBuilder
from agentic_sdlc.intelligence.swarm_router import SwarmRouter

class TestSwarmsIntegration:
    """Tests for the Swarms-inspired components."""

    def test_workflow_router_complexity(self):
        router = WorkflowRouter()
        # Complex task should trigger HEAVY_SWARM
        task = "Design and implement a complex multi-region database sync with security audit and research"
        result = router.route(task)
        assert result.execution_mode == ExecutionMode.HEAVY_SWARM
        assert result.complexity.score >= 7
        assert "SA" in result.complexity.recommended_roles

    def test_concurrent_executor(self):
        executor = ConcurrentExecutor()
        roles = ["SA", "UIUX"]
        task = "Test concurrent execution"
        
        # Mock role execution to avoid sub-processes in tests
        with patch.object(executor, '_execute_role') as mock_exec:
            mock_exec.return_value = MagicMock(role="SA", output="Design done", success=True)
            result = executor.run(roles, task)
            assert result.task == task
            assert len(result.results) == 2
            assert result.success is True

    def test_output_synthesizer(self):
        synthesizer = OutputSynthesizer()
        synthesizer.add_input("SA", "Architecture looks good.", 0.9)
        synthesizer.add_input("SECA", "Security is tight.", 0.9)
        
        result = synthesizer.synthesize(strategy="concatenate")
        assert "SA:" in result.output
        assert "SECA:" in result.output
        assert result.strategy == "concatenate"

    def test_feedback_protocol(self):
        protocol = FeedbackProtocol()
        msg = protocol.send_feedback("BRAIN", "ORCHESTRATOR", "Improve plan", "direction")
        assert msg.sender == "BRAIN"
        assert msg.receiver == "ORCHESTRATOR"
        
        history = protocol.get_messages("ORCHESTRATOR")
        assert len(history) >= 1
        assert history[0].content == "Improve plan"

    def test_group_chat_initialization(self):
        agents = ["SA", "DEV", "TESTER"]
        chat = GroupChat(agents=agents)
        assert chat.agents == agents
        assert len(chat.history) == 0

    def test_auto_skill_builder(self, tmp_path):
        builder = AutoSkillBuilder(skills_dir=tmp_path)
        name = "CloudExpert"
        objective = "Manage AWS resources"
        
        path = builder.build_skill(name, objective)
        assert path.exists()
        assert "CloudExpert" in path.read_text()
        assert name.lower() in str(path)

    def test_swarm_router_mapping(self):
        router = SwarmRouter()
        assert router._map_execution_mode(ExecutionMode.SEQUENTIAL) == "sequential"
        assert router._map_execution_mode(ExecutionMode.PARALLEL) == "concurrent"
        assert router._map_execution_mode(ExecutionMode.HEAVY_SWARM) == "mixture_of_agents"

if __name__ == "__main__":
    pytest.main([__file__, "-v"])
