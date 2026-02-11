"""Unit tests for the Learner class."""

import pytest
import tempfile
from pathlib import Path
from agentic_sdlc.intelligence.learning import Learner, PatternType, Pattern


class TestLearner:
    """Tests for Learner functionality."""

    @pytest.fixture
    def learner(self):
        """Create a learner instance with temporary storage."""
        with tempfile.TemporaryDirectory() as tmpdir:
            storage_file = Path(tmpdir) / "learner.json"
            yield Learner(storage_file=storage_file)

    def test_learner_initialization(self, learner):
        """Test learner initialization."""
        assert learner is not None
        assert len(learner.patterns) == 0
        assert len(learner.events) == 0

    def test_learn_general_pattern(self, learner):
        """Test learning a general pattern."""
        result = learner.learn("test pattern", context={"key": "value"})
        assert result["status"] == "learned"
        assert len(learner.patterns) == 1
        assert learner.patterns[0].description == "test pattern"

    def test_learn_error(self, learner):
        """Test learning from an error."""
        result = learner.learn_error("test error", "fixed by restarting", context={"code": 500})
        assert result["status"] == "error_learned"
        assert len(learner.patterns) == 1
        assert learner.patterns[0].pattern_type == PatternType.ERROR

    def test_learn_success(self, learner):
        """Test learning from a success."""
        result = learner.learn_success("completed task", "used approach X", context={"time": 5})
        assert result["status"] == "success_learned"
        assert len(learner.patterns) == 1
        assert learner.patterns[0].pattern_type == PatternType.SUCCESS

    def test_find_similar_patterns(self, learner):
        """Test finding similar patterns."""
        learner.learn("database connection error", context={})
        learner.learn("network timeout", context={})
        learner.learn("database query failed", context={})

        similar = learner.find_similar("database")
        assert len(similar) == 2

    def test_find_similar_by_type(self, learner):
        """Test finding similar patterns filtered by type."""
        learner.learn_error("error 1", "fix 1")
        learner.learn_success("success 1", "approach 1")
        learner.learn_error("error 2", "fix 2")

        errors = learner.find_similar("error", PatternType.ERROR)
        assert len(errors) == 2

    def test_get_recommendation(self, learner):
        """Test getting a recommendation."""
        learner.learn_success("deploy application", "use CI/CD pipeline")
        learner.learn_success("deploy application", "use CI/CD pipeline")

        recommendation = learner.get_recommendation("deploy application")
        assert recommendation is not None
        assert recommendation["recommendation"] == "use CI/CD pipeline"

    def test_get_recommendation_not_found(self, learner):
        """Test getting recommendation when no similar pattern exists."""
        recommendation = learner.get_recommendation("unknown task")
        assert recommendation is None

    def test_learn_from_observer(self, learner):
        """Test learning from observer violations."""
        violations = [
            {"type": "code_quality", "severity": "high"},
            {"type": "naming", "severity": "low"},
        ]
        result = learner.learn_from_observer(violations)
        assert result["status"] == "learned_from_observer"
        assert result["violations_processed"] == 2

    def test_learn_from_judge(self, learner):
        """Test learning from judge scoring."""
        score_result = {"score": 0.85, "file": "test.py"}
        result = learner.learn_from_judge(score_result)
        assert result["status"] == "learned_from_judge"

    def test_learn_from_ab_test(self, learner):
        """Test learning from A/B test results."""
        test_result = {"winner": "approach_a", "score_a": 0.9, "score_b": 0.7}
        result = learner.learn_from_ab_test(test_result)
        assert result["status"] == "learned_from_ab_test"

    def test_get_stats(self, learner):
        """Test getting learner statistics."""
        learner.learn("pattern 1")
        learner.learn_error("error 1", "fix 1")
        learner.learn_success("success 1", "approach 1")

        stats = learner.get_stats()
        assert stats["total_patterns"] == 3
        assert stats["error_patterns"] == 1
        assert stats["success_patterns"] == 1
        assert stats["task_patterns"] == 1

    def test_list_patterns(self, learner):
        """Test listing patterns."""
        learner.learn("pattern 1")
        learner.learn_error("error 1", "fix 1")

        all_patterns = learner.list_patterns()
        assert len(all_patterns) == 2

        error_patterns = learner.list_patterns(PatternType.ERROR)
        assert len(error_patterns) == 1

    def test_pattern_persistence(self):
        """Test that patterns are persisted to storage."""
        with tempfile.TemporaryDirectory() as tmpdir:
            storage_file = Path(tmpdir) / "learner.json"

            # Create learner and add pattern
            learner1 = Learner(storage_file=storage_file)
            learner1.learn("test pattern")

            # Create new learner with same storage
            learner2 = Learner(storage_file=storage_file)
            assert len(learner2.patterns) == 1
            assert learner2.patterns[0].description == "test pattern"
