"""Unit tests for Reasoner and DecisionEngine classes."""

import pytest
from agentic_sdlc.intelligence.reasoning import (
    Reasoner,
    DecisionEngine,
    ExecutionMode,
    TaskComplexity,
)


class TestReasoner:
    """Tests for Reasoner functionality."""

    @pytest.fixture
    def reasoner(self):
        """Create a reasoner instance."""
        return Reasoner()

    def test_reasoner_initialization(self, reasoner):
        """Test reasoner initialization."""
        assert reasoner is not None
        assert len(reasoner.decision_history) == 0

    def test_analyze_task_complexity_simple(self, reasoner):
        """Test analyzing a simple task."""
        complexity = reasoner.analyze_task_complexity("simple task")
        assert complexity.score <= 3
        assert complexity.recommendation == "simple"

    def test_analyze_task_complexity_complex(self, reasoner):
        """Test analyzing a complex task."""
        task = "This is a very long task description that involves parallel execution and error handling with integration requirements"
        complexity = reasoner.analyze_task_complexity(task)
        assert complexity.score >= 5
        assert len(complexity.factors) > 0

    def test_analyze_task_complexity_with_context(self, reasoner):
        """Test analyzing task with context."""
        complexity = reasoner.analyze_task_complexity(
            "task", context={"priority": "high", "deadline": "urgent"}
        )
        assert complexity is not None

    def test_recommend_execution_mode_sequential(self, reasoner):
        """Test recommending sequential execution."""
        mode = reasoner.recommend_execution_mode("simple task")
        assert mode == ExecutionMode.SEQUENTIAL

    def test_recommend_execution_mode_parallel(self, reasoner):
        """Test recommending parallel execution."""
        task = "Complex parallel task with error handling and integration"
        mode = reasoner.recommend_execution_mode(task)
        assert mode in [ExecutionMode.PARALLEL, ExecutionMode.HYBRID]

    def test_route_task(self, reasoner):
        """Test routing a task."""
        workflows = ["workflow_a", "workflow_b", "workflow_c"]
        result = reasoner.route_task("process with workflow_a", workflows)
        assert result.workflow == "workflow_a"
        assert result.confidence > 0

    def test_route_task_no_match(self, reasoner):
        """Test routing when no workflow matches."""
        workflows = ["workflow_a", "workflow_b"]
        result = reasoner.route_task("unknown task", workflows)
        assert result.workflow in workflows

    def test_route_task_empty_workflows(self, reasoner):
        """Test routing with no available workflows."""
        with pytest.raises(ValueError):
            reasoner.route_task("task", [])

    def test_make_decision(self, reasoner):
        """Test making a decision."""
        options = [
            {"name": "option_a", "score": 0.8},
            {"name": "option_b", "score": 0.6},
        ]
        decision = reasoner.make_decision(options)
        assert "selected" in decision
        assert decision["selected"] in options

    def test_make_decision_no_options(self, reasoner):
        """Test making decision with no options."""
        with pytest.raises(ValueError):
            reasoner.make_decision([])

    def test_get_decision_history(self, reasoner):
        """Test getting decision history."""
        options = [{"name": "option_a"}]
        reasoner.make_decision(options)
        reasoner.make_decision(options)
        history = reasoner.get_decision_history()
        assert len(history) == 2

    def test_clear_history(self, reasoner):
        """Test clearing decision history."""
        options = [{"name": "option_a"}]
        reasoner.make_decision(options)
        reasoner.clear_history()
        assert len(reasoner.get_decision_history()) == 0


class TestDecisionEngine:
    """Tests for DecisionEngine functionality."""

    @pytest.fixture
    def engine(self):
        """Create a decision engine instance."""
        return DecisionEngine()

    def test_engine_initialization(self, engine):
        """Test engine initialization."""
        assert engine is not None
        assert len(engine.rules) == 0

    def test_add_rule(self, engine):
        """Test adding a rule."""
        engine.add_rule("rule_a", lambda ctx: ctx.get("value") > 10)
        assert "rule_a" in engine.rules

    def test_evaluate_rule_true(self, engine):
        """Test evaluating a rule that returns true."""
        engine.add_rule("check_value", lambda ctx: ctx.get("value") > 10)
        result = engine.evaluate_rule("check_value", {"value": 15})
        assert result is True

    def test_evaluate_rule_false(self, engine):
        """Test evaluating a rule that returns false."""
        engine.add_rule("check_value", lambda ctx: ctx.get("value") > 10)
        result = engine.evaluate_rule("check_value", {"value": 5})
        assert result is False

    def test_evaluate_nonexistent_rule(self, engine):
        """Test evaluating a rule that doesn't exist."""
        result = engine.evaluate_rule("nonexistent", {})
        assert result is False

    def test_evaluate_all_rules(self, engine):
        """Test evaluating all rules."""
        engine.add_rule("rule_a", lambda ctx: ctx.get("a") > 0)
        engine.add_rule("rule_b", lambda ctx: ctx.get("b") > 0)
        results = engine.evaluate_all_rules({"a": 1, "b": -1})
        assert results["rule_a"] is True
        assert results["rule_b"] is False

    def test_make_decision_with_rules(self, engine):
        """Test making a decision with rules."""
        engine.add_rule("prefer_a", lambda ctx: ctx.get("prefer") == "a")
        options = [{"name": "option_a"}, {"name": "option_b"}]
        decision = engine.make_decision(options, {"prefer": "a"})
        assert "selected" in decision

    def test_get_rules(self, engine):
        """Test getting all rules."""
        engine.add_rule("rule_a", lambda ctx: True)
        engine.add_rule("rule_b", lambda ctx: False)
        rules = engine.get_rules()
        assert len(rules) == 2
        assert "rule_a" in rules
        assert "rule_b" in rules
