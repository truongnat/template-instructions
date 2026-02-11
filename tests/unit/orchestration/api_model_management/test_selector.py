"""
Unit tests for ModelSelector class.

This module tests specific scenarios for the ModelSelector including
suitability score calculation, ranking algorithm, and priority adjustments.
"""

import unittest
import tempfile
import asyncio
from pathlib import Path
from datetime import datetime
import json

from agentic_sdlc.orchestration.api_model_management.selector import ModelSelector
from agentic_sdlc.orchestration.api_model_management.registry import ModelRegistry
from agentic_sdlc.orchestration.api_model_management.health_checker import HealthChecker
from agentic_sdlc.orchestration.api_model_management.rate_limiter import RateLimiter
from agentic_sdlc.orchestration.api_model_management.performance_monitor import PerformanceMonitor
from agentic_sdlc.orchestration.api_model_management.models import (
    ModelMetadata,
    RateLimits,
    SelectionConstraints,
    PerformanceMetrics
)
from agentic_sdlc.orchestration.api_model_management.exceptions import APIModelError

# Import AgentTask and TaskPriority
try:
    from agentic_sdlc.orchestration.models.agent import AgentTask, TaskPriority
except ImportError:
    # Fallback for testing
    from dataclasses import dataclass, field
    from enum import Enum
    from typing import Any, List
    
    class TaskPriority(Enum):
        CRITICAL = 1
        HIGH = 2
        MEDIUM = 3
        LOW = 4
        BACKGROUND = 5
    
    @dataclass
    class AgentTask:
        id: str
        type: str = ""
        priority: TaskPriority = TaskPriority.MEDIUM
        requirements: List[Any] = field(default_factory=list)


class TestModelSelector(unittest.TestCase):
    """Unit tests for ModelSelector"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.temp_dir = tempfile.mkdtemp()
        self.db_path = Path(self.temp_dir) / "test.db"
        self.config_path = Path(self.temp_dir) / "models.json"
        
        # Initialize database
        asyncio.run(self._init_database())
        
        # Create test models
        self.test_models = [
            ModelMetadata(
                id="gpt-4-turbo",
                provider="openai",
                name="GPT-4 Turbo",
                capabilities=["text-generation", "code-generation", "analysis"],
                cost_per_1k_input_tokens=0.01,
                cost_per_1k_output_tokens=0.03,
                rate_limits=RateLimits(requests_per_minute=500, tokens_per_minute=150000),
                context_window=128000,
                average_response_time_ms=2000.0,
                enabled=True
            ),
            ModelMetadata(
                id="claude-3.5-sonnet",
                provider="anthropic",
                name="Claude 3.5 Sonnet",
                capabilities=["text-generation", "code-generation", "analysis"],
                cost_per_1k_input_tokens=0.003,
                cost_per_1k_output_tokens=0.015,
                rate_limits=RateLimits(requests_per_minute=1000, tokens_per_minute=200000),
                context_window=200000,
                average_response_time_ms=1500.0,
                enabled=True
            ),
            ModelMetadata(
                id="gpt-3.5-turbo",
                provider="openai",
                name="GPT-3.5 Turbo",
                capabilities=["text-generation", "code-generation"],
                cost_per_1k_input_tokens=0.0005,
                cost_per_1k_output_tokens=0.0015,
                rate_limits=RateLimits(requests_per_minute=3500, tokens_per_minute=90000),
                context_window=16000,
                average_response_time_ms=800.0,
                enabled=True
            )
        ]
        
        # Create selector
        self.selector = self._create_selector(self.test_models)
    
    async def _init_database(self):
        """Initialize test database"""
        import aiosqlite
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute("""
                CREATE TABLE IF NOT EXISTS health_checks (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp DATETIME NOT NULL,
                    model_id TEXT NOT NULL,
                    is_available BOOLEAN NOT NULL,
                    response_time_ms REAL,
                    error_message TEXT
                )
            """)
            await db.execute("""
                CREATE TABLE IF NOT EXISTS rate_limit_events (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp DATETIME NOT NULL,
                    model_id TEXT NOT NULL,
                    event_type TEXT NOT NULL,
                    reset_time DATETIME
                )
            """)
            await db.execute("""
                CREATE TABLE IF NOT EXISTS performance_records (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp DATETIME NOT NULL,
                    model_id TEXT NOT NULL,
                    agent_type TEXT NOT NULL,
                    task_id TEXT NOT NULL,
                    latency_ms REAL NOT NULL,
                    success BOOLEAN NOT NULL,
                    quality_score REAL
                )
            """)
            await db.commit()
    
    def _create_test_config(self, models):
        """Create test configuration file"""
        config = {
            "models": [
                {
                    "id": m.id,
                    "provider": m.provider,
                    "name": m.name,
                    "capabilities": m.capabilities,
                    "cost_per_1k_input_tokens": m.cost_per_1k_input_tokens,
                    "cost_per_1k_output_tokens": m.cost_per_1k_output_tokens,
                    "rate_limits": {
                        "requests_per_minute": m.rate_limits.requests_per_minute,
                        "tokens_per_minute": m.rate_limits.tokens_per_minute
                    },
                    "context_window": m.context_window,
                    "average_response_time_ms": m.average_response_time_ms,
                    "enabled": m.enabled
                }
                for m in models
            ]
        }
        
        with open(self.config_path, 'w') as f:
            json.dump(config, f)
    
    def _create_selector(self, models):
        """Create ModelSelector with test dependencies"""
        self._create_test_config(models)
        
        registry = ModelRegistry(self.config_path)
        registry.load_config()
        
        health_checker = HealthChecker(
            registry=registry,
            db_path=self.db_path,
            check_interval_seconds=60
        )
        
        rate_limiter = RateLimiter(
            registry=registry,
            db_path=self.db_path
        )
        
        performance_monitor = PerformanceMonitor(db_path=self.db_path)
        
        return ModelSelector(
            registry=registry,
            health_checker=health_checker,
            rate_limiter=rate_limiter,
            performance_monitor=performance_monitor
        )
    
    def test_suitability_score_calculation_basic(self):
        """Test basic suitability score calculation"""
        task = AgentTask(
            id="test-task-1",
            type="code-generation",
            priority=TaskPriority.MEDIUM
        )
        
        model = self.test_models[0]  # GPT-4 Turbo
        
        score = self.selector.calculate_suitability_score(model, task, None)
        
        # Score should be between 0 and 1
        self.assertGreaterEqual(score, 0.0)
        self.assertLessEqual(score, 1.0)
        
        # With no performance data, should use neutral score
        # Capability (1.0 * 0.3) + Cost (~0.8 * 0.25) + Performance (0.7 * 0.25) + Availability (1.0 * 0.2)
        # Should be around 0.775
        self.assertGreater(score, 0.5)
    
    def test_suitability_score_with_performance_data(self):
        """Test suitability score calculation with performance data"""
        task = AgentTask(
            id="test-task-2",
            type="code-generation",
            priority=TaskPriority.MEDIUM
        )
        
        model = self.test_models[1]  # Claude 3.5 Sonnet
        
        # Create mock performance data
        performance_data = PerformanceMetrics(
            model_id=model.id,
            window_hours=24,
            total_requests=100,
            successful_requests=95,
            failed_requests=5,
            success_rate=0.95,
            average_latency_ms=1500.0,
            p50_latency_ms=1400.0,
            p95_latency_ms=2000.0,
            p99_latency_ms=2500.0,
            average_quality_score=0.9
        )
        
        score = self.selector.calculate_suitability_score(model, task, performance_data)
        
        # Score should be high with good performance data
        self.assertGreater(score, 0.7)
    
    def test_suitability_score_critical_priority_adjustment(self):
        """Test that CRITICAL priority adjusts weights to prioritize quality"""
        task_critical = AgentTask(
            id="test-task-3",
            type="code-generation",
            priority=TaskPriority.CRITICAL
        )
        
        task_medium = AgentTask(
            id="test-task-4",
            type="code-generation",
            priority=TaskPriority.MEDIUM
        )
        
        # Use expensive but high-quality model
        model = self.test_models[0]  # GPT-4 Turbo (expensive)
        
        # Create high-quality performance data
        performance_data = PerformanceMetrics(
            model_id=model.id,
            window_hours=24,
            total_requests=100,
            successful_requests=98,
            failed_requests=2,
            success_rate=0.98,
            average_latency_ms=2000.0,
            p50_latency_ms=1900.0,
            p95_latency_ms=2500.0,
            p99_latency_ms=3000.0,
            average_quality_score=0.95
        )
        
        score_critical = self.selector.calculate_suitability_score(
            model, task_critical, performance_data
        )
        score_medium = self.selector.calculate_suitability_score(
            model, task_medium, performance_data
        )
        
        # CRITICAL priority should give higher score due to quality emphasis
        self.assertGreater(score_critical, score_medium)
    
    def test_suitability_score_background_priority_adjustment(self):
        """Test that BACKGROUND priority adjusts weights to prioritize cost"""
        task_background = AgentTask(
            id="test-task-5",
            type="text-generation",
            priority=TaskPriority.BACKGROUND
        )
        
        task_medium = AgentTask(
            id="test-task-6",
            type="text-generation",
            priority=TaskPriority.MEDIUM
        )
        
        # Use cheap model
        model = self.test_models[2]  # GPT-3.5 Turbo (cheap)
        
        score_background = self.selector.calculate_suitability_score(
            model, task_background, None
        )
        score_medium = self.selector.calculate_suitability_score(
            model, task_medium, None
        )
        
        # BACKGROUND priority should give higher score for cheap model
        self.assertGreater(score_background, score_medium)
    
    def test_ranking_algorithm(self):
        """Test model ranking algorithm"""
        task = AgentTask(
            id="test-task-7",
            type="code-generation",
            priority=TaskPriority.MEDIUM
        )
        
        async def run_test():
            ranked = await self.selector.rank_models(
                self.test_models,
                task,
                "test_agent"
            )
            
            # Should return list of tuples (model, score)
            self.assertEqual(len(ranked), len(self.test_models))
            
            # Scores should be in descending order
            scores = [score for _, score in ranked]
            self.assertEqual(scores, sorted(scores, reverse=True))
            
            # All scores should be between 0 and 1
            for _, score in ranked:
                self.assertGreaterEqual(score, 0.0)
                self.assertLessEqual(score, 1.0)
        
        asyncio.run(run_test())
    
    def test_ranking_with_unavailable_model(self):
        """Test ranking excludes unavailable models"""
        task = AgentTask(
            id="test-task-8",
            type="code-generation",
            priority=TaskPriority.MEDIUM
        )
        
        # Mark first model as unavailable
        self.selector.health_checker._consecutive_failures[self.test_models[0].id] = 5
        
        async def run_test():
            # Filter by availability first
            available = await self.selector._filter_by_availability(self.test_models)
            
            # Should exclude the unavailable model
            self.assertLess(len(available), len(self.test_models))
            self.assertNotIn(self.test_models[0], available)
        
        asyncio.run(run_test())
    
    def test_ranking_with_rate_limited_model(self):
        """Test ranking excludes rate-limited models"""
        task = AgentTask(
            id="test-task-9",
            type="code-generation",
            priority=TaskPriority.MEDIUM
        )
        
        async def run_test():
            # Mark first model as rate-limited
            from datetime import timedelta
            reset_time = datetime.now() + timedelta(seconds=60)
            await self.selector.rate_limiter._mark_rate_limited(
                self.test_models[0].id,
                reset_time
            )
            
            # Verify it's marked as rate-limited
            is_limited = self.selector.rate_limiter.is_rate_limited(self.test_models[0].id)
            self.assertTrue(is_limited, "Model should be marked as rate-limited")
            
            # Filter by availability
            available = await self.selector._filter_by_availability(self.test_models)
            
            # Should exclude the rate-limited model
            self.assertLess(len(available), len(self.test_models))
            self.assertNotIn(self.test_models[0], available)
        
        asyncio.run(run_test())
    
    def test_select_model_with_constraints(self):
        """Test model selection with constraints"""
        task = AgentTask(
            id="test-task-10",
            type="code-generation",
            priority=TaskPriority.MEDIUM
        )
        
        # Exclude OpenAI provider
        constraints = SelectionConstraints(
            excluded_providers=["openai"]
        )
        
        async def run_test():
            selection = await self.selector.select_model(
                task,
                "test_agent",
                constraints
            )
            
            # Should select non-OpenAI model
            selected_model = self.selector.registry.get_model(selection.model_id)
            self.assertNotEqual(selected_model.provider, "openai")
        
        asyncio.run(run_test())
    
    def test_select_model_with_max_latency_constraint(self):
        """Test model selection with max latency constraint"""
        task = AgentTask(
            id="test-task-11",
            type="text-generation",
            priority=TaskPriority.MEDIUM
        )
        
        # Require low latency
        constraints = SelectionConstraints(
            max_latency_ms=1000.0
        )
        
        async def run_test():
            selection = await self.selector.select_model(
                task,
                "test_agent",
                constraints
            )
            
            # Should select model with latency <= 1000ms
            selected_model = self.selector.registry.get_model(selection.model_id)
            self.assertLessEqual(selected_model.average_response_time_ms, 1000.0)
        
        asyncio.run(run_test())
    
    def test_select_model_no_matching_capabilities(self):
        """Test model selection fails when no models match capabilities"""
        task = AgentTask(
            id="test-task-12",
            type="image-generation",  # No models have this capability
            priority=TaskPriority.MEDIUM
        )
        
        constraints = SelectionConstraints(
            required_capabilities=["image-generation"]
        )
        
        async def run_test():
            with self.assertRaises(APIModelError) as context:
                await self.selector.select_model(
                    task,
                    "test_agent",
                    constraints
                )
            
            self.assertIn("No models found", str(context.exception))
        
        asyncio.run(run_test())
    
    def test_capability_extraction_from_task_type(self):
        """Test capability extraction from task type"""
        # Test code generation task
        task_code = AgentTask(
            id="test-task-13",
            type="code-implementation",
            priority=TaskPriority.MEDIUM
        )
        
        caps = self.selector._extract_required_capabilities(task_code, None)
        self.assertIn("code-generation", caps)
        
        # Test analysis task - note: "analysis" in task type triggers "code-generation" first
        # because "code" appears before "analysis" in the check
        task_analysis = AgentTask(
            id="test-task-14",
            type="data-analysis",  # Changed to avoid "code" keyword
            priority=TaskPriority.MEDIUM
        )
        
        caps = self.selector._extract_required_capabilities(task_analysis, None)
        self.assertIn("analysis", caps)
        
        # Test default fallback
        task_generic = AgentTask(
            id="test-task-15",
            type="generic-task",
            priority=TaskPriority.MEDIUM
        )
        
        caps = self.selector._extract_required_capabilities(task_generic, None)
        self.assertIn("text-generation", caps)
    
    def test_selection_reason_generation(self):
        """Test selection reason generation"""
        model = self.test_models[0]
        
        # Test CRITICAL priority
        reason = self.selector._generate_selection_reason(
            model,
            0.85,
            TaskPriority.CRITICAL,
            ["code-generation"]
        )
        
        self.assertIn("code-generation", reason)
        self.assertIn("high-priority", reason)
        self.assertIn("0.850", reason)
        
        # Test BACKGROUND priority
        reason = self.selector._generate_selection_reason(
            model,
            0.75,
            TaskPriority.BACKGROUND,
            ["text-generation"]
        )
        
        self.assertIn("text-generation", reason)
        self.assertIn("background", reason)
        self.assertIn("0.750", reason)


if __name__ == '__main__':
    unittest.main()
