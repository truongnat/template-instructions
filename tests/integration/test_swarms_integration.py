
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Tests for Swarms-inspired Intelligence Layer Components
"""

import pytest
import sys
from pathlib import Path
from unittest.mock import patch, MagicMock

# Add project root to path
sys.path.insert(0, str(Path(__file__).parents[1]))

# Attempt to import available components
try:
    from agentic_sdlc.infrastructure.engine.execution_engine import (
        ConcurrentExecutor, Task, OutputSynthesizer, FeedbackProtocol
    )
    from agentic_sdlc.orchestration.agents import GroupChat, Agent
    from agentic_sdlc.intelligence.reasoning.reasoner import Reasoner, ExecutionMode, TaskComplexity
    from agentic_sdlc.intelligence.learning.learner import Learner
    engine_components_available = True
except ImportError:
    engine_components_available = False

class TestSwarmsIntegration:
    """Tests for the Swarms-inspired components."""

    @pytest.mark.skipif(not engine_components_available, reason="ExecutionEngine components not available")
    def test_workflow_router_complexity(self):
        """Test routing logic using Reasoner (replaces WorkflowRouter)"""
        router = Reasoner()
        # Complex task should trigger PARALLEL (equivalent to HEAVY_SWARM in complexity)
        # Ensure task triggers complexity: >100 chars, "parallel", "integration"
        task = "Design and implement a complex multi-region database sync system that requires parallel execution and deep integration with existing security audits and research components to ensure data integrity."
        
        # Test complexity analysis
        complexity = router.analyze_task_complexity(task)
        # Score calculation: 
        # Base: 1
        # > 100 chars: +2
        # "parallel": +2
        # "integration": +2
        # Total: 7
        assert complexity.score >= 5
        
        # Test execution mode recommendation
        mode = router.recommend_execution_mode(task)
        assert mode == ExecutionMode.PARALLEL

        # Verify simpler task
        simple_task = "Write a simple function."
        complexity_simple = router.analyze_task_complexity(simple_task)
        assert complexity_simple.score < 5
        assert router.recommend_execution_mode(simple_task) == ExecutionMode.SEQUENTIAL

    @pytest.mark.skipif(not engine_components_available, reason="ConcurrentExecutor not available")
    def test_concurrent_executor(self):
        """Test parallel task execution."""
        executor = ConcurrentExecutor()
        
        # Define some simple tasks
        def task_func(x): return x * 2
        
        executor.add_task(Task(name="task1", func=task_func, args=(10,)))
        executor.add_task(Task(name="task2", func=task_func, args=(20,)))
        
        results = executor.execute()
        
        assert results["task1"] == 20
        assert results["task2"] == 40
        assert len(results) == 2

    @pytest.mark.skipif(not engine_components_available, reason="OutputSynthesizer not available")
    def test_output_synthesizer(self):
        """Test synthesizing multiple outputs."""
        synthesizer = OutputSynthesizer()
        outputs = ["Result from agent A", "Result from agent B"]
        
        synthesized = synthesizer.synthesize(outputs, context="Test Project")
        
        assert "Result from agent A" in synthesized
        assert "Result from agent B" in synthesized
        assert "Test Project" in synthesized

    @pytest.mark.skipif(not engine_components_available, reason="FeedbackProtocol not available")
    def test_feedback_protocol(self):
        """Test feedback processing."""
        protocol = FeedbackProtocol()
        result = protocol.process_feedback(target="AgentX", feedback="Great job!", score=0.9)
        
        assert result["status"] == "success"
        assert len(protocol.history) == 1
        assert protocol.history[0]["target"] == "AgentX"
        assert protocol.history[0]["score"] == 0.9

    @pytest.mark.skipif(not engine_components_available, reason="GroupChat not available")
    def test_group_chat_initialization(self):
        """Test group chat functionality."""
        agent1 = Agent(name="Agent1", role="Researcher", model_name="test-model")
        agent2 = Agent(name="Agent2", role="Coder", model_name="test-model")
        
        chat = GroupChat(agents=[agent1, agent2], name="Project Room")
        chat.broadcast(sender="Agent1", content="Hello everyone")
        
        history = chat.get_history()
        assert len(history) == 1
        assert history[0]["sender"] == "Agent1"
        assert history[0]["content"] == "Hello everyone"
        assert chat.name == "Project Room"

    @pytest.mark.skipif(not engine_components_available, reason="Learner not available")
    def test_auto_skill_builder(self, tmp_path):
        """Test skill/pattern learning using Learner (replaces AutoSkillBuilder)"""
        # Learner persists to file, use tmp_path
        storage = tmp_path / "learner.json"
        builder = Learner(storage_file=storage)
        
        name = "CloudExpert"
        objective = "Manage AWS resources"
        
        # Use learn() method to simulate building a skill pattern
        result = builder.learn(f"Skill: {name} - {objective}", context={"role": name, "objective": objective})
        
        assert result['status'] == "learned"
        assert storage.exists()
        
        # Verify persistence
        with open(storage, 'r') as f:
            data = f.read()
            assert name in data
            assert objective in data

    @pytest.mark.skipif(not engine_components_available, reason="Reasoner not available")
    def test_swarm_router_mapping(self):
        """Test execution mode mapping"""
        # Reasoner uses ExecutionMode enum directly
        assert ExecutionMode.SEQUENTIAL.value == "sequential"
        assert ExecutionMode.PARALLEL.value == "parallel"
        assert ExecutionMode.HYBRID.value == "hybrid"

if __name__ == "__main__":
    pytest.main([__file__, "-v"])
