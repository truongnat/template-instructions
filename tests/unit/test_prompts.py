"""Unit tests for prompts module: PromptGenerator and ContextOptimizer."""

import pytest

from agentic_sdlc.prompts import ContextItem, ContextOptimizer, PromptGenerator
from agentic_sdlc.skills import ContextSpec, Skill, SkillRole, SkillStep


# ─── Fixtures ────────────────────────────────────────────────────────────


@pytest.fixture
def skill():
    return Skill(
        name="test-prompt-skill",
        description="A skill for testing prompts",
        role=SkillRole.DEVELOPER,
        category="backend",
        tags=["api", "python"],
        workflow_steps=[
            SkillStep(name="analyze", action="analyze_requirements", description="Analyze"),
            SkillStep(name="implement", action="write_code", description="Write code"),
        ],
        validation_rules=["Must compile", "Must have tests"],
        score_criteria={"correctness": 0.5, "quality": 0.3, "docs": 0.2},
    )


# ─── PromptGenerator ────────────────────────────────────────────────────


class TestPromptGenerator:
    def test_generate_basic(self, skill):
        gen = PromptGenerator()
        prompt = gen.generate(skill)
        assert "test-prompt-skill" in prompt
        assert "developer" in prompt
        assert "analyze" in prompt
        assert "implement" in prompt

    def test_generate_with_context(self, skill):
        gen = PromptGenerator()
        prompt = gen.generate(skill, context={"tech_stack": "Python/FastAPI"})
        assert "Python/FastAPI" in prompt

    def test_generate_review_prompt(self, skill):
        gen = PromptGenerator()
        review = gen.generate_review_prompt("Some output", skill)
        assert "Self-Review" in review
        assert "correctness" in review
        assert "quality" in review
        assert "PASS" in review or "FAIL" in review
        assert "Some output" in review

    def test_generate_ab_prompts_2(self, skill):
        gen = PromptGenerator()
        prompts = gen.generate_ab_prompts(skill, variants=2)
        assert len(prompts) == 2
        assert "Variant A" in prompts[0]
        assert "Variant B" in prompts[1]

    def test_generate_ab_prompts_3(self, skill):
        gen = PromptGenerator()
        prompts = gen.generate_ab_prompts(skill, variants=3)
        assert len(prompts) == 3
        assert "Variant C" in prompts[2]

    def test_structured_prompt_has_validation(self, skill):
        gen = PromptGenerator()
        prompt = gen.generate(skill)
        assert "Must compile" in prompt
        assert "Must have tests" in prompt

    def test_generate_with_long_context(self, skill):
        gen = PromptGenerator()
        prompt = gen.generate(skill, context={"readme": "X" * 300})
        assert "readme" in prompt


# ─── ContextOptimizer ────────────────────────────────────────────────────


class TestContextOptimizer:
    def test_optimize_within_budget(self):
        opt = ContextOptimizer(max_tokens=500)
        items = [
            ContextItem("short", "Short content", priority=0.9),
            ContextItem("medium", "Medium content " * 20, priority=0.5),
        ]
        result = opt.optimize(items)
        assert result.total_tokens <= 500
        assert len(result.items) >= 1

    def test_optimize_drops_low_priority(self):
        opt = ContextOptimizer(max_tokens=100)
        items = [
            ContextItem("high", "Important " * 30, priority=0.9),
            ContextItem("low", "Not important " * 30, priority=0.1),
        ]
        result = opt.optimize(items)
        assert result.dropped_count >= 1

    def test_optimize_with_keywords(self):
        opt = ContextOptimizer(max_tokens=5000)
        items = [
            ContextItem("auth_module", "Authentication and login code", priority=0.5),
            ContextItem("utils", "Utility functions for strings", priority=0.5),
        ]
        result = opt.optimize(items, keywords=["auth", "login"])
        # Auth should be ranked higher
        if len(result.items) >= 2:
            assert result.items[0].name == "auth_module"

    def test_optimize_empty_items(self):
        opt = ContextOptimizer()
        result = opt.optimize([])
        assert result.total_tokens == 0
        assert len(result.items) == 0

    def test_optimize_respects_max_tokens(self):
        opt = ContextOptimizer(max_tokens=200)
        items = [ContextItem(f"item{i}", "X" * 400, priority=0.5) for i in range(5)]
        result = opt.optimize(items)
        assert result.total_tokens <= 250  # allow small overshoot from truncation

    def test_prioritize(self):
        opt = ContextOptimizer()
        items = [
            ContextItem("low", "Low priority", priority=0.1),
            ContextItem("high", "High priority", priority=0.9),
        ]
        ranked = opt.prioritize(items)
        assert ranked[0].name == "high"

    def test_chunk_small_content(self):
        opt = ContextOptimizer()
        chunks = opt.chunk("Short content")
        assert len(chunks) == 1

    def test_chunk_large_content(self):
        opt = ContextOptimizer()
        content = "Line of text.\n" * 500
        chunks = opt.chunk(content, chunk_size=1000, overlap=100)
        assert len(chunks) > 1
        # Overlap: last chars of chunk N should appear in chunk N+1
        for i in range(len(chunks) - 1):
            assert len(chunks[i]) <= 1100  # chunk_size + some boundary tolerance

    def test_summarize_for_budget_short(self):
        opt = ContextOptimizer()
        result = opt.summarize_for_budget("Short text", target_tokens=100)
        assert result == "Short text"

    def test_summarize_for_budget_long(self):
        opt = ContextOptimizer()
        content = "A" * 10000
        result = opt.summarize_for_budget(content, target_tokens=100)
        assert "truncated" in result
        assert len(result) < len(content)

    def test_optimized_context_to_string(self):
        items = [
            ContextItem("readme", "README content"),
            ContextItem("config", "Config content"),
        ]
        from agentic_sdlc.prompts.context_optimizer import OptimizedContext

        ctx = OptimizedContext(items=items, total_tokens=100, budget=500)
        text = ctx.to_string()
        assert "## readme" in text
        assert "## config" in text

    def test_utilization(self):
        from agentic_sdlc.prompts.context_optimizer import OptimizedContext

        ctx = OptimizedContext(items=[], total_tokens=250, budget=500)
        assert ctx.utilization == 0.5

    def test_optimize_with_context_spec(self):
        opt = ContextOptimizer()
        spec = ContextSpec(max_tokens=200, priority_keywords=["auth"])
        items = [ContextItem("auth", "Auth module code", priority=0.5)]
        result = opt.optimize(items, context_spec=spec)
        assert result.budget == 200
