"""
Unit tests for FailoverManager class.

This module tests specific scenarios and edge cases for the FailoverManager
including failover triggering conditions, alternative selection, and excessive
failover detection.
"""

import unittest
import asyncio
import tempfile
import aiosqlite
from pathlib import Path
from datetime import datetime, timedelta
from unittest.mock import Mock, AsyncMock, patch, MagicMock

from agentic_sdlc.orchestration.api_model_management.failover_manager import FailoverManager
from agentic_sdlc.orchestration.api_model_management.selector import ModelSelector
from agentic_sdlc.orchestration.api_model_management.registry import ModelRegistry
from agentic_sdlc.orchestration.api_model_management.health_checker import HealthChecker
from agentic_sdlc.orchestration.api_model_management.rate_limiter import RateLimiter
from agentic_sdlc.orchestration.api_model_management.performance_monitor import PerformanceMonitor
from agentic_sdlc.orchestration.api_model_management.models import (
    ModelMetadata,
    RateLimits,
    FailoverReason,
    ModelResponse,
    TokenUsage,
    ModelSelection,
)
from agentic_sdlc.orchestration.api_model_management.exceptions import (
    FailoverError,
    ModelUnavailableError,
    RateLimitError,
    APIModelError,
)

# Import AgentTask
try:
    from agentic_sdlc.orchestration.models.agent import AgentTask, TaskPriority
except ImportError:
    from dataclasses import dataclass, field as dc_field
    from enum import Enum
    from typing import List, Any
    
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
        requirements: List[Any] = dc_field(default_factory=list)


class TestFailoverManager(unittest.TestCase):
    """Unit tests for FailoverManager"""
    
    def setUp(self):
        """Set up test case"""
        # Create temporary directory for database
        self.temp_dir = tempfile.mkdtemp()
        self.db_path = Path(self.temp_dir) / "test_failover_manager.db"
        
        # Create temporary config file
        self.config_path = Path(self.temp_dir) / "model_registry.json"
        
        # Create a sample configuration
        self._create_sample_config()
        
        # Initialize database schema
        asyncio.run(self._init_database())
    
    def tearDown(self):
        """Clean up after test"""
        import shutil
        if Path(self.temp_dir).exists():
            shutil.rmtree(self.temp_dir)
    
    def _create_sample_config(self):
        """Create a sample model registry configuration"""
        import json
        
        config = {
            "models": [
                {
                    "id": "gpt-4-turbo",
                    "provider": "openai",
                    "name": "GPT-4 Turbo",
                    "capabilities": ["text-generation", "code-generation"],
                    "cost_per_1k_input_tokens": 0.01,
                    "cost_per_1k_output_tokens": 0.03,
                    "rate_limits": {
                        "requests_per_minute": 500,
                        "tokens_per_minute": 150000
                    },
                    "context_window": 128000,
                    "average_response_time_ms": 2000,
                    "enabled": True
                },
                {
                    "id": "claude-3.5-sonnet",
                    "provider": "anthropic",
                    "name": "Claude 3.5 Sonnet",
                    "capabilities": ["text-generation", "code-generation"],
                    "cost_per_1k_input_tokens": 0.003,
                    "cost_per_1k_output_tokens": 0.015,
                    "rate_limits": {
                        "requests_per_minute": 1000,
                        "tokens_per_minute": 200000
                    },
                    "context_window": 200000,
                    "average_response_time_ms": 1500,
                    "enabled": True
                },
                {
                    "id": "gemini-pro",
                    "provider": "google",
                    "name": "Gemini Pro",
                    "capabilities": ["text-generation"],
                    "cost_per_1k_input_tokens": 0.0005,
                    "cost_per_1k_output_tokens": 0.0015,
                    "rate_limits": {
                        "requests_per_minute": 60,
                        "tokens_per_minute": 32000
                    },
                    "context_window": 32000,
                    "average_response_time_ms": 1000,
                    "enabled": True
                }
            ]
        }
        
        with open(self.config_path, 'w') as f:
            json.dump(config, f)
    
    async def _init_database(self):
        """Initialize database schema"""
        async with aiosqlite.connect(self.db_path) as db:
            # Failover events table
            await db.execute("""
                CREATE TABLE IF NOT EXISTS failover_events (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp DATETIME NOT NULL,
                    original_model TEXT NOT NULL,
                    alternative_model TEXT NOT NULL,
                    reason TEXT NOT NULL,
                    task_id TEXT NOT NULL
                )
            """)
            
            # Health checks table
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
            
            # Performance records table
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
    
    def _create_components(self):
        """Create registry, health checker, rate limiter, performance monitor, and selector"""
        registry = ModelRegistry(self.config_path)
        registry.load_config()
        
        health_checker = HealthChecker(
            registry=registry,
            db_path=self.db_path,
            check_interval_seconds=60,
            consecutive_failures_threshold=3
        )
        
        rate_limiter = RateLimiter(registry=registry)
        
        performance_monitor = PerformanceMonitor(db_path=self.db_path)
        
        selector = ModelSelector(
            registry=registry,
            health_checker=health_checker,
            rate_limiter=rate_limiter,
            performance_monitor=performance_monitor
        )
        
        return registry, health_checker, rate_limiter, performance_monitor, selector
    
    def run_async(self, coro):
        """Helper to run async code in sync test"""
        return asyncio.run(coro)
    
    # Failover Triggering Conditions
    
    def test_failover_on_model_unavailable_error(self):
        """Test that failover is triggered when model is unavailable"""
        async def test():
            registry, health_checker, rate_limiter, performance_monitor, selector = self._create_components()
            
            failover_manager = FailoverManager(
                model_selector=selector,
                db_path=self.db_path,
                max_retries=3,
                base_backoff_seconds=1
            )
            
            task = AgentTask(id="task-1", type="test", priority=TaskPriority.MEDIUM)
            
            # Mock request function that fails with unavailable error
            async def mock_request_func(model_id: str):
                if model_id == "gpt-4-turbo":
                    raise ModelUnavailableError("Model unavailable", model_id=model_id)
                return ModelResponse(
                    content="Success",
                    model_id=model_id,
                    token_usage=TokenUsage(10, 20, 30),
                    latency_ms=100.0,
                    cost=0.001
                )
            
            # Mock selector to return alternative
            with patch.object(selector, 'select_model', new_callable=AsyncMock) as mock_select:
                mock_select.return_value = ModelSelection(
                    model_id="claude-3.5-sonnet",
                    model_metadata=registry.get_model("claude-3.5-sonnet"),
                    suitability_score=0.8,
                    alternatives=[],
                    selection_reason="Alternative"
                )
                
                response = await failover_manager.execute_with_failover(
                    primary_model="gpt-4-turbo",
                    task=task,
                    agent_type="pm",
                    request_func=mock_request_func
                )
                
                self.assertEqual(response.model_id, "claude-3.5-sonnet")
                self.assertGreaterEqual(mock_select.call_count, 1)
        
        self.run_async(test())
    
    def test_failover_on_rate_limit_error(self):
        """Test that failover is triggered when model is rate limited"""
        async def test():
            registry, health_checker, rate_limiter, performance_monitor, selector = self._create_components()
            
            failover_manager = FailoverManager(
                model_selector=selector,
                db_path=self.db_path,
                max_retries=3,
                base_backoff_seconds=1
            )
            
            task = AgentTask(id="task-1", type="test", priority=TaskPriority.MEDIUM)
            
            # Mock request function that fails with rate limit error
            async def mock_request_func(model_id: str):
                if model_id == "gpt-4-turbo":
                    raise RateLimitError("Rate limited", model_id=model_id)
                return ModelResponse(
                    content="Success",
                    model_id=model_id,
                    token_usage=TokenUsage(10, 20, 30),
                    latency_ms=100.0,
                    cost=0.001
                )
            
            # Mock selector to return alternative
            with patch.object(selector, 'select_model', new_callable=AsyncMock) as mock_select:
                mock_select.return_value = ModelSelection(
                    model_id="claude-3.5-sonnet",
                    model_metadata=registry.get_model("claude-3.5-sonnet"),
                    suitability_score=0.8,
                    alternatives=[],
                    selection_reason="Alternative"
                )
                
                response = await failover_manager.execute_with_failover(
                    primary_model="gpt-4-turbo",
                    task=task,
                    agent_type="pm",
                    request_func=mock_request_func
                )
                
                self.assertEqual(response.model_id, "claude-3.5-sonnet")
        
        self.run_async(test())
    
    def test_failover_on_api_model_error(self):
        """Test that failover is triggered on generic API errors"""
        async def test():
            registry, health_checker, rate_limiter, performance_monitor, selector = self._create_components()
            
            failover_manager = FailoverManager(
                model_selector=selector,
                db_path=self.db_path,
                max_retries=3,
                base_backoff_seconds=1
            )
            
            task = AgentTask(id="task-1", type="test", priority=TaskPriority.MEDIUM)
            
            # Mock request function that fails with API error
            async def mock_request_func(model_id: str):
                if model_id == "gpt-4-turbo":
                    raise APIModelError("API error", model_id=model_id)
                return ModelResponse(
                    content="Success",
                    model_id=model_id,
                    token_usage=TokenUsage(10, 20, 30),
                    latency_ms=100.0,
                    cost=0.001
                )
            
            # Mock selector to return alternative
            with patch.object(selector, 'select_model', new_callable=AsyncMock) as mock_select:
                mock_select.return_value = ModelSelection(
                    model_id="claude-3.5-sonnet",
                    model_metadata=registry.get_model("claude-3.5-sonnet"),
                    suitability_score=0.8,
                    alternatives=[],
                    selection_reason="Alternative"
                )
                
                response = await failover_manager.execute_with_failover(
                    primary_model="gpt-4-turbo",
                    task=task,
                    agent_type="pm",
                    request_func=mock_request_func
                )
                
                self.assertEqual(response.model_id, "claude-3.5-sonnet")
        
        self.run_async(test())
    
    def test_no_failover_on_success(self):
        """Test that no failover occurs when request succeeds"""
        async def test():
            registry, health_checker, rate_limiter, performance_monitor, selector = self._create_components()
            
            failover_manager = FailoverManager(
                model_selector=selector,
                db_path=self.db_path,
                max_retries=3,
                base_backoff_seconds=1
            )
            
            task = AgentTask(id="task-1", type="test", priority=TaskPriority.MEDIUM)
            
            # Mock request function that succeeds
            async def mock_request_func(model_id: str):
                return ModelResponse(
                    content="Success",
                    model_id=model_id,
                    token_usage=TokenUsage(10, 20, 30),
                    latency_ms=100.0,
                    cost=0.001
                )
            
            # Mock selector
            with patch.object(selector, 'select_model', new_callable=AsyncMock) as mock_select:
                response = await failover_manager.execute_with_failover(
                    primary_model="gpt-4-turbo",
                    task=task,
                    agent_type="pm",
                    request_func=mock_request_func
                )
                
                self.assertEqual(response.model_id, "gpt-4-turbo")
                # Selector should not be called if primary succeeds
                self.assertEqual(mock_select.call_count, 0)
        
        self.run_async(test())
    
    def test_failover_error_after_max_retries(self):
        """Test that FailoverError is raised after max retries"""
        async def test():
            registry, health_checker, rate_limiter, performance_monitor, selector = self._create_components()
            
            failover_manager = FailoverManager(
                model_selector=selector,
                db_path=self.db_path,
                max_retries=3,
                base_backoff_seconds=1
            )
            
            task = AgentTask(id="task-1", type="test", priority=TaskPriority.MEDIUM)
            
            # Mock request function that always fails
            async def mock_request_func(model_id: str):
                raise ModelUnavailableError(f"Model {model_id} unavailable", model_id=model_id)
            
            # Mock selector to raise error (simulating no alternatives available)
            with patch.object(selector, 'select_model', new_callable=AsyncMock) as mock_select:
                mock_select.side_effect = APIModelError("No models available", model_id="unknown")
                
                with self.assertRaises(FailoverError) as context:
                    await failover_manager.execute_with_failover(
                        primary_model="gpt-4-turbo",
                        task=task,
                        agent_type="pm",
                        request_func=mock_request_func
                    )
                
                error = context.exception
                self.assertEqual(error.original_model, "gpt-4-turbo")
                self.assertEqual(error.task_id, "task-1")
                self.assertIn("gpt-4-turbo", error.attempted_models)
        
        self.run_async(test())
    
    # Alternative Selection
    
    def test_select_alternative_returns_different_model(self):
        """Test that select_alternative returns a different model than the failed one"""
        async def test():
            registry, health_checker, rate_limiter, performance_monitor, selector = self._create_components()
            
            failover_manager = FailoverManager(
                model_selector=selector,
                db_path=self.db_path
            )
            
            task = AgentTask(id="task-1", type="test", priority=TaskPriority.MEDIUM)
            
            # Mock selector to return different model
            with patch.object(selector, 'select_model', new_callable=AsyncMock) as mock_select:
                mock_select.return_value = ModelSelection(
                    model_id="claude-3.5-sonnet",
                    model_metadata=registry.get_model("claude-3.5-sonnet"),
                    suitability_score=0.8,
                    alternatives=[],
                    selection_reason="Alternative"
                )
                
                alternative = await failover_manager.select_alternative(
                    failed_model="gpt-4-turbo",
                    task=task,
                    agent_type="pm",
                    reason=FailoverReason.UNAVAILABLE
                )
                
                self.assertIsNotNone(alternative)
                self.assertEqual(alternative, "claude-3.5-sonnet")
                self.assertNotEqual(alternative, "gpt-4-turbo")
        
        self.run_async(test())
    
    def test_select_alternative_uses_alternatives_list(self):
        """Test that select_alternative uses alternatives list when primary matches failed model"""
        async def test():
            registry, health_checker, rate_limiter, performance_monitor, selector = self._create_components()
            
            failover_manager = FailoverManager(
                model_selector=selector,
                db_path=self.db_path
            )
            
            task = AgentTask(id="task-1", type="test", priority=TaskPriority.MEDIUM)
            
            # Mock selector to return same model but with alternatives
            with patch.object(selector, 'select_model', new_callable=AsyncMock) as mock_select:
                mock_select.return_value = ModelSelection(
                    model_id="gpt-4-turbo",  # Same as failed
                    model_metadata=registry.get_model("gpt-4-turbo"),
                    suitability_score=0.9,
                    alternatives=["claude-3.5-sonnet", "gemini-pro"],
                    selection_reason="Primary"
                )
                
                alternative = await failover_manager.select_alternative(
                    failed_model="gpt-4-turbo",
                    task=task,
                    agent_type="pm",
                    reason=FailoverReason.UNAVAILABLE
                )
                
                self.assertIsNotNone(alternative)
                self.assertEqual(alternative, "claude-3.5-sonnet")
        
        self.run_async(test())
    
    def test_select_alternative_returns_none_when_no_alternatives(self):
        """Test that select_alternative returns None when no alternatives available"""
        async def test():
            registry, health_checker, rate_limiter, performance_monitor, selector = self._create_components()
            
            failover_manager = FailoverManager(
                model_selector=selector,
                db_path=self.db_path
            )
            
            task = AgentTask(id="task-1", type="test", priority=TaskPriority.MEDIUM)
            
            # Mock selector to return same model with no alternatives
            with patch.object(selector, 'select_model', new_callable=AsyncMock) as mock_select:
                mock_select.return_value = ModelSelection(
                    model_id="gpt-4-turbo",  # Same as failed
                    model_metadata=registry.get_model("gpt-4-turbo"),
                    suitability_score=0.9,
                    alternatives=[],
                    selection_reason="Primary"
                )
                
                alternative = await failover_manager.select_alternative(
                    failed_model="gpt-4-turbo",
                    task=task,
                    agent_type="pm",
                    reason=FailoverReason.UNAVAILABLE
                )
                
                self.assertIsNone(alternative)
        
        self.run_async(test())
    
    def test_select_alternative_handles_selector_error(self):
        """Test that select_alternative handles errors from selector gracefully"""
        async def test():
            registry, health_checker, rate_limiter, performance_monitor, selector = self._create_components()
            
            failover_manager = FailoverManager(
                model_selector=selector,
                db_path=self.db_path
            )
            
            task = AgentTask(id="task-1", type="test", priority=TaskPriority.MEDIUM)
            
            # Mock selector to raise error
            with patch.object(selector, 'select_model', new_callable=AsyncMock) as mock_select:
                mock_select.side_effect = APIModelError("Selector error", model_id="unknown")
                
                alternative = await failover_manager.select_alternative(
                    failed_model="gpt-4-turbo",
                    task=task,
                    agent_type="pm",
                    reason=FailoverReason.UNAVAILABLE
                )
                
                self.assertIsNone(alternative)
        
        self.run_async(test())
    
    # Excessive Failover Detection
    
    def test_excessive_failover_alert_triggered(self):
        """Test that alert is triggered when failover threshold is exceeded"""
        async def test():
            registry, health_checker, rate_limiter, performance_monitor, selector = self._create_components()
            
            failover_manager = FailoverManager(
                model_selector=selector,
                db_path=self.db_path,
                alert_threshold=3,
                alert_window_hours=1
            )
            
            model_id = "gpt-4-turbo"
            
            # Patch logger to capture alerts
            with patch('agentic_sdlc.orchestration.api_model_management.failover_manager.logger') as mock_logger:
                # Record multiple failover events
                for i in range(4):
                    await failover_manager.record_failover(
                        original_model=model_id,
                        alternative_model="claude-3.5-sonnet",
                        reason=FailoverReason.UNAVAILABLE,
                        task_id=f"task-{i}"
                    )
                    await failover_manager._check_excessive_failover(model_id)
                
                # Check that warning was called with alert message
                warning_calls = [str(call[0][0]) for call in mock_logger.warning.call_args_list]
                alert_found = any("ALERT" in msg and "Excessive failover" in msg for msg in warning_calls)
                
                self.assertTrue(alert_found, "Alert should be triggered after threshold exceeded")
        
        self.run_async(test())
    
    def test_excessive_failover_alert_not_triggered_below_threshold(self):
        """Test that alert is not triggered when below threshold"""
        async def test():
            registry, health_checker, rate_limiter, performance_monitor, selector = self._create_components()
            
            failover_manager = FailoverManager(
                model_selector=selector,
                db_path=self.db_path,
                alert_threshold=5,
                alert_window_hours=1
            )
            
            model_id = "gpt-4-turbo"
            
            # Patch logger to capture alerts
            with patch('agentic_sdlc.orchestration.api_model_management.failover_manager.logger') as mock_logger:
                # Record failovers below threshold
                for i in range(3):
                    await failover_manager.record_failover(
                        original_model=model_id,
                        alternative_model="claude-3.5-sonnet",
                        reason=FailoverReason.UNAVAILABLE,
                        task_id=f"task-{i}"
                    )
                    await failover_manager._check_excessive_failover(model_id)
                
                # Check that no alert was triggered
                warning_calls = [str(call[0][0]) for call in mock_logger.warning.call_args_list]
                alert_found = any("ALERT" in msg and "Excessive failover" in msg for msg in warning_calls)
                
                self.assertFalse(alert_found, "Alert should not be triggered below threshold")
        
        self.run_async(test())
    
    def test_excessive_failover_respects_time_window(self):
        """Test that excessive failover detection respects the time window"""
        async def test():
            registry, health_checker, rate_limiter, performance_monitor, selector = self._create_components()
            
            failover_manager = FailoverManager(
                model_selector=selector,
                db_path=self.db_path,
                alert_threshold=3,
                alert_window_hours=1
            )
            
            model_id = "gpt-4-turbo"
            
            # Record old failover events (outside window)
            old_timestamp = datetime.now() - timedelta(hours=2)
            async with aiosqlite.connect(self.db_path) as db:
                for i in range(5):
                    await db.execute(
                        """
                        INSERT INTO failover_events 
                        (timestamp, original_model, alternative_model, reason, task_id)
                        VALUES (?, ?, ?, ?, ?)
                        """,
                        (old_timestamp, model_id, "claude-3.5-sonnet", "unavailable", f"old-task-{i}")
                    )
                await db.commit()
            
            # Patch logger to capture alerts
            with patch('agentic_sdlc.orchestration.api_model_management.failover_manager.logger') as mock_logger:
                # Record new failover events (within window, but below threshold)
                for i in range(2):
                    await failover_manager.record_failover(
                        original_model=model_id,
                        alternative_model="claude-3.5-sonnet",
                        reason=FailoverReason.UNAVAILABLE,
                        task_id=f"task-{i}"
                    )
                    await failover_manager._check_excessive_failover(model_id)
                
                # Check that no alert was triggered (only 2 recent failovers)
                warning_calls = [str(call[0][0]) for call in mock_logger.warning.call_args_list]
                alert_found = any("ALERT" in msg and "Excessive failover" in msg for msg in warning_calls)
                
                self.assertFalse(alert_found, "Alert should not be triggered for old events outside window")
        
        self.run_async(test())
    
    def test_get_failover_count(self):
        """Test getting failover count for a model"""
        async def test():
            registry, health_checker, rate_limiter, performance_monitor, selector = self._create_components()
            
            failover_manager = FailoverManager(
                model_selector=selector,
                db_path=self.db_path
            )
            
            model_id = "gpt-4-turbo"
            
            # Record failover events
            for i in range(5):
                await failover_manager.record_failover(
                    original_model=model_id,
                    alternative_model="claude-3.5-sonnet",
                    reason=FailoverReason.UNAVAILABLE,
                    task_id=f"task-{i}"
                )
            
            # Get failover count
            count = await failover_manager.get_failover_count(model_id, hours=1)
            
            self.assertEqual(count, 5)
        
        self.run_async(test())
    
    def test_get_failover_history(self):
        """Test retrieving failover history"""
        async def test():
            registry, health_checker, rate_limiter, performance_monitor, selector = self._create_components()
            
            failover_manager = FailoverManager(
                model_selector=selector,
                db_path=self.db_path
            )
            
            model_id = "gpt-4-turbo"
            
            # Record failover events
            for i in range(3):
                await failover_manager.record_failover(
                    original_model=model_id,
                    alternative_model="claude-3.5-sonnet",
                    reason=FailoverReason.UNAVAILABLE,
                    task_id=f"task-{i}"
                )
            
            # Get failover history
            history = await failover_manager.get_failover_history(model_id=model_id, hours=24)
            
            self.assertEqual(len(history), 3)
            for event in history:
                self.assertEqual(event['original_model'], model_id)
                self.assertEqual(event['alternative_model'], "claude-3.5-sonnet")
                self.assertIn('timestamp', event)
                self.assertIn('reason', event)
                self.assertIn('task_id', event)
        
        self.run_async(test())
    
    def test_get_failover_history_all_models(self):
        """Test retrieving failover history for all models"""
        async def test():
            registry, health_checker, rate_limiter, performance_monitor, selector = self._create_components()
            
            failover_manager = FailoverManager(
                model_selector=selector,
                db_path=self.db_path
            )
            
            # Record failover events for multiple models
            for model_id in ["gpt-4-turbo", "claude-3.5-sonnet"]:
                for i in range(2):
                    await failover_manager.record_failover(
                        original_model=model_id,
                        alternative_model="gemini-pro",
                        reason=FailoverReason.RATE_LIMITED,
                        task_id=f"task-{model_id}-{i}"
                    )
            
            # Get all failover history
            history = await failover_manager.get_failover_history(hours=24)
            
            self.assertEqual(len(history), 4)
        
        self.run_async(test())


if __name__ == '__main__':
    unittest.main()
