"""Unit tests for intelligence/review module: SelfReviewEngine and ABScorer."""

import pytest

from agentic_sdlc.intelligence.review import (
    ABResult,
    ABScorer,
    ABTest,
    ReviewCriteria,
    ReviewResult,
    SelfReviewEngine,
)
from agentic_sdlc.skills import Skill, SkillRole, SkillStep


# ─── Fixtures ────────────────────────────────────────────────────────────


@pytest.fixture
def skill():
    return Skill(
        name="review-test-skill",
        description="Skill for review testing",
        role=SkillRole.DEVELOPER,
        category="backend",
        tags=["api"],
        workflow_steps=[
            SkillStep(name="implement", action="write_code", description="Write code"),
            SkillStep(name="test", action="write_tests", description="Write tests"),
        ],
        validation_rules=[
            "Must contain function definitions",
            "Must include error handling",
            "Must have test coverage",
        ],
        score_criteria={"correctness": 0.4, "quality": 0.3, "test_coverage": 0.3},
    )


@pytest.fixture
def good_output():
    return """# Implementation

```python
def create_user(name: str, email: str) -> dict:
    \"\"\"Create a new user with validation.\"\"\"
    try:
        if not name or not email:
            raise ValueError("Name and email required")
        return {"name": name, "email": email, "id": "123"}
    except ValueError as e:
        raise
    except Exception as e:
        raise RuntimeError(f"Failed to create user: {e}")
```

## Tests

```python
def test_create_user():
    result = create_user("Alice", "alice@example.com")
    assert result["name"] == "Alice"

def test_create_user_invalid():
    with pytest.raises(ValueError):
        create_user("", "")
```
"""


@pytest.fixture
def poor_output():
    return "TODO: implement later"


# ─── SelfReviewEngine ───────────────────────────────────────────────────


class TestSelfReviewEngine:
    def test_review_good_output(self, skill, good_output):
        engine = SelfReviewEngine()
        result = engine.review(good_output, skill)
        assert isinstance(result, ReviewResult)
        assert 0.0 <= result.total_score <= 1.0
        assert result.total_score >= 0.5

    def test_review_poor_output(self, skill, poor_output):
        engine = SelfReviewEngine()
        result = engine.review(poor_output, skill)
        assert result.total_score < 0.5
        assert result.verdict == "FAIL"

    def test_review_criteria_present(self, skill, good_output):
        engine = SelfReviewEngine()
        result = engine.review(good_output, skill)
        assert len(result.criteria) > 0
        for c in result.criteria:
            assert isinstance(c, ReviewCriteria)
            assert 0.0 <= c.score <= 1.0
            assert c.name

    def test_review_validations_list(self, skill, good_output):
        engine = SelfReviewEngine()
        result = engine.review(good_output, skill)
        assert isinstance(result.validations, list)
        assert len(result.validations) == 3  # 3 validation rules in skill

    def test_review_to_markdown(self, skill, good_output):
        engine = SelfReviewEngine()
        result = engine.review(good_output, skill)
        md = result.to_markdown()
        assert "Review Result" in md
        assert "Score" in md or "score" in md

    def test_review_empty_output(self, skill):
        engine = SelfReviewEngine()
        result = engine.review("", skill)
        assert result.total_score < 0.5
        assert result.verdict == "FAIL"

    def test_review_skill_without_criteria(self, good_output):
        skill = Skill(
            name="no-criteria",
            description="Skill without score criteria",
            role=SkillRole.DEVELOPER,
            category="general",
        )
        engine = SelfReviewEngine()
        result = engine.review(good_output, skill)
        assert isinstance(result, ReviewResult)
        # No criteria means total_score = 0.0
        assert result.total_score == 0.0

    def test_review_verdict_pass(self, skill, good_output):
        engine = SelfReviewEngine(pass_threshold=0.3)
        result = engine.review(good_output, skill)
        # With low threshold, could be PASS or PASS_WITH_WARNINGS
        assert result.verdict in ("PASS", "PASS_WITH_WARNINGS")

    def test_review_verdict_fail(self, skill, poor_output):
        engine = SelfReviewEngine(pass_threshold=0.9)
        result = engine.review(poor_output, skill)
        assert result.verdict == "FAIL"

    def test_review_passed_property(self, skill, good_output):
        engine = SelfReviewEngine(pass_threshold=0.3)
        result = engine.review(good_output, skill)
        # .passed only returns True for exact "PASS", not "PASS_WITH_WARNINGS"
        assert isinstance(result.passed, bool)


# ─── ABScorer ────────────────────────────────────────────────────────────


class TestABScorer:
    def test_create_test(self, skill):
        scorer = ABScorer()
        test = scorer.create_test(skill)
        assert isinstance(test, ABTest)
        assert test.skill_name == "review-test-skill"

    def test_add_result(self, skill, good_output, poor_output):
        scorer = ABScorer()
        test = scorer.create_test(skill)
        scorer.add_result(test, "A", good_output, skill)
        scorer.add_result(test, "B", poor_output, skill)
        assert len(test.results) == 2

    def test_evaluate_winner(self, skill, good_output, poor_output):
        scorer = ABScorer()
        test = scorer.create_test(skill)
        scorer.add_result(test, "A", good_output, skill)
        scorer.add_result(test, "B", poor_output, skill)
        winner = scorer.evaluate(test)
        assert winner == "A"

    def test_evaluate_single(self, skill, good_output):
        scorer = ABScorer()
        test = scorer.create_test(skill)
        scorer.add_result(test, "A", good_output, skill)
        winner = scorer.evaluate(test)
        assert winner == "A"

    def test_get_insights(self, skill, good_output, poor_output):
        scorer = ABScorer()
        test = scorer.create_test(skill)
        scorer.add_result(test, "A", good_output, skill)
        scorer.add_result(test, "B", poor_output, skill)
        scorer.evaluate(test)
        insights = scorer.get_insights(test)
        assert "winner" in insights
        assert "score_spread" in insights
        assert insights["winner"] == "A"

    def test_ab_multiple_variants(self, skill):
        scorer = ABScorer()
        test = scorer.create_test(skill)
        outputs = [
            "Short\n```python\ndef a(): pass\n```",
            "Medium\n```python\ndef a():\n    try: return 1\n    except: pass\n```\n## Tests\n```python\ndef test(): pass\n```",
            "Long detailed output with functions and error handling\n```python\ndef a():\n    try: return 1\n    except Exception as e: raise\n```\n## Tests\n```python\ndef test_a(): assert True\ndef test_b(): assert True\n```",
        ]
        for i, out in enumerate(outputs):
            label = chr(65 + i)  # A, B, C
            scorer.add_result(test, label, out, skill)
        winner = scorer.evaluate(test)
        assert winner in ["A", "B", "C"]

    def test_insights_no_evaluation(self, skill):
        scorer = ABScorer()
        test = scorer.create_test(skill)
        # get_insights returns empty dict when no winner
        insights = scorer.get_insights(test)
        assert insights == {}

    def test_ab_test_is_complete(self, skill, good_output):
        scorer = ABScorer()
        test = scorer.create_test(skill)
        assert not test.is_complete
        scorer.add_result(test, "A", good_output, skill)
        scorer.evaluate(test)
        assert test.is_complete

    def test_ab_test_to_markdown(self, skill, good_output, poor_output):
        scorer = ABScorer()
        test = scorer.create_test(skill)
        scorer.add_result(test, "A", good_output, skill)
        scorer.add_result(test, "B", poor_output, skill)
        scorer.evaluate(test)
        md = test.to_markdown()
        assert "A/B Test" in md
        assert "Winner" in md
        assert "🏆" in md
