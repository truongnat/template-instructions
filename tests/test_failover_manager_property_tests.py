"""
Property-based tests for FailoverManager class.

This module tests the correctness properties of the FailoverManager including
automatic failover on unavailability, failover event logging completeness,
exponential backoff retry, original model retry after recovery, and excessive
failover alerting.
"""

import unittest
import asyncio
import tempfile
import aiosqlite
from pathlib import Path
from datetime import datetime, timedelta
from unittest.mock import Mock, AsyncMock, patch, MagicMock
from typing import Dict, List

try:
    from hypothesis import given, strategies as st, settings, assume
    HYPOTHESIS_AVAILABLE = True
except ImportError:
    HYPOTHESIS_AVAILABLE = False
    
    def given(*args, **kwargs):
        def decorator(func):
            return func
        return decorator
    
    class MockStrategies:
        def text(self, **kwargs): return lambda: "test"
        def integers(self, **kwargs): return lambda: 1
        def lists(self, *args, **kwargs): return lambda: []
        def dictionaries(self, *args, **kwargs): return lambda: {}
        def sampled_from(self, seq): return lambda: seq[0] if seq else None
        def builds(self, cls, **kwargs): return lambda: cls(**kwargs)
        def floats(self, **kwargs): return lambda: 1.0
        def booleans(self): return lambda: True
    
    st = MockStrategies()
    
    def settings(**kwargs):
        def decorator(func):
            return func
        return decorator

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
        requirements: List[str] = dc_field(default_factory=list)


# Hypothesis strategies for generating test data

def model_id_strategy():
    """Strategy for generating model IDs"""
    return st.sampled_from([
        "gpt-4-turbo",
        "claude-3.5-sonnet",
        "gemini-pro",
        "llama-3-70b"
    ])


def task_id_strategy():
    """Strategy for generating task IDs"""
    return st.text(min_size=5, max_size=20, alphabet="abcdefghijklmnopqrstuvwxyz0123456789-")


def agent_type_strategy():
    """Strategy for generating agent types"""
    return st.sampled_from(["pm", "ba", "sa", "research", "quality_judge", "implementation"])


def failover_reason_strategy():
    """Strategy for generating failover reasons"""
    return st.sampled_from([
        FailoverReason.UNAVAILABLE,
        FailoverReason.RATE_LIMITED,
        FailoverReason.ERROR,
        FailoverReason.TIMEOUT
    ])


def max_retries_strategy():
    """Strategy for generating max retries"""
    return st.integers(min_value=1, max_value=5)


def base_backoff_strategy():
    """Strategy for generating base backoff seconds"""
    return st.integers(min_value=1, max_value=3)


def num_failovers_strategy():
    """Strategy for generating number of failovers"""
    return st.integers(min_value=1, max_value=10)


class TestFailoverManagerProperties(unittest.TestCase):
    """Test FailoverManager correctness properties"""
    
    def setUp(self):
        """Set up test case"""
        if not HYPOTHESIS_AVAILABLE:
            self.skipTest("Hypothesis not available")
        
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
        # Clean up temp files
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
                },
                {
                    "id": "llama-3-70b",
                    "provider": "ollama",
                    "name": "Llama 3 70B",
                    "capabilities": ["text-generation", "code-generation"],
                    "cost_per_1k_input_tokens": 0.0,
                    "cost_per_1k_output_tokens": 0.0,
                    "rate_limits": {
                        "requests_per_minute": 100,
                        "tokens_per_minute": 50000
                    },
                    "context_window": 8192,
                    "average_response_time_ms": 3000,
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
            
            # Health checks table (needed for HealthChecker)
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
            
            # Performance records table (needed for PerformanceMonitor)
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
    
    @settings(max_examples=20, deadline=5000)
    @given(
        primary_model=model_id_strategy(),
        alternative_model=model_id_strategy(),
        task_id=task_id_strategy(),
        agent_type=agent_type_strategy(),
        failover_reason=failover_reason_strategy()
    )
    def test_property_18_automatic_failover_on_unavailability(
        self,
        primary_model: str,
        alternative_model: str,
        task_id: str,
        agent_type: str,
        failover_reason: FailoverReason
    ):
        """
        Feature: api-model-management
        Property 18: Automatic failover on unavailability
        
        For any request to an unavailable or rate-limited model, an alternative
        model should be automatically selected and used.
        
        Validates: Requirements 5.1
        """
        # Skip if primary and alternative are the same
        assume(primary_model != alternative_model)
        
        async def run_test():
            # Create components
            registry, health_checker, rate_limiter, performance_monitor, selector = self._create_components()
            
            # Create failover manager
            failover_manager = FailoverManager(
                model_selector=selector,
                db_path=self.db_path,
                max_retries=3,
                base_backoff_seconds=1
            )
            
            # Create task
            task = AgentTask(
                id=task_id,
                type="test_task",
                priority=TaskPriority.MEDIUM
            )
            
            # Mock the request function to fail for primary, succeed for alternative
            call_count = {'count': 0}
            
            async def mock_request_func(model_id: str):
                call_count['count'] += 1
                
                if model_id == primary_model:
                    # Primary model fails based on failover reason
                    if failover_reason == FailoverReason.UNAVAILABLE:
                        raise ModelUnavailableError(f"Model {model_id} is unavailable", model_id=model_id)
                    elif failover_reason == FailoverReason.RATE_LIMITED:
                        raise RateLimitError(f"Model {model_id} is rate limited", model_id=model_id)
                    else:
                        raise APIModelError(f"Model {model_id} error", model_id=model_id)
                else:
                    # Alternative model succeeds
                    return ModelResponse(
                        content="Success with alternative model",
                        model_id=model_id,
                        token_usage=TokenUsage(input_tokens=10, output_tokens=20, total_tokens=30),
                        latency_ms=100.0,
                        cost=0.001
                    )
            
            # Mock the selector to return alternative model
            with patch.object(selector, 'select_model', new_callable=AsyncMock) as mock_select:
                # First call returns primary (which will fail)
                # Subsequent calls return alternative
                def select_side_effect(task, agent_type):
                    model_metadata = registry.get_model(alternative_model)
                    return ModelSelection(
                        model_id=alternative_model,
                        model_metadata=model_metadata,
                        suitability_score=0.8,
                        alternatives=[],
                        selection_reason="Alternative model"
                    )
                
                mock_select.side_effect = select_side_effect
                
                # Execute with failover
                response = await failover_manager.execute_with_failover(
                    primary_model=primary_model,
                    task=task,
                    agent_type=agent_type,
                    request_func=mock_request_func
                )
                
                # Verify that failover occurred
                self.assertIsNotNone(response, "Should receive a response")
                self.assertEqual(
                    response.model_id,
                    alternative_model,
                    "Response should be from alternative model"
                )
                
                # Verify that multiple attempts were made
                self.assertGreaterEqual(
                    call_count['count'],
                    2,
                    "Should have attempted primary and then alternative"
                )
                
                # Verify that selector was called to find alternative
                self.assertGreaterEqual(
                    mock_select.call_count,
                    1,
                    "Selector should be called to find alternative"
                )
        
        asyncio.run(run_test())
    
    @settings(max_examples=20, deadline=5000)
    @given(
        original_model=model_id_strategy(),
        alternative_model=model_id_strategy(),
        task_id=task_id_strategy(),
        agent_type=agent_type_strategy(),
        failover_reason=failover_reason_strategy()
    )
    def test_property_19_failover_event_logging_completeness(
        self,
        original_model: str,
        alternative_model: str,
        task_id: str,
        agent_type: str,
        failover_reason: FailoverReason
    ):
        """
        Feature: api-model-management
        Property 19: Failover event logging completeness
        
        For any failover event, the logged event should include the original
        model, alternative model, reason, and task ID.
        
        Validates: Requirements 5.2
        """
        # Skip if models are the same
        assume(original_model != alternative_model)
        
        async def run_test():
            # Create components
            registry, health_checker, rate_limiter, performance_monitor, selector = self._create_components()
            
            # Create failover manager
            failover_manager = FailoverManager(
                model_selector=selector,
                db_path=self.db_path,
                max_retries=3,
                base_backoff_seconds=1
            )
            
            # Create task
            task = AgentTask(
                id=task_id,
                type="test_task",
                priority=TaskPriority.MEDIUM
            )
            
            # Record failover event
            await failover_manager.record_failover(
                original_model=original_model,
                alternative_model=alternative_model,
                reason=failover_reason,
                task_id=task_id
            )
            
            # Verify event was logged to database
            async with aiosqlite.connect(self.db_path) as db:
                cursor = await db.execute(
                    """
                    SELECT timestamp, original_model, alternative_model, reason, task_id
                    FROM failover_events
                    WHERE original_model = ? AND alternative_model = ? AND task_id = ?
                    ORDER BY timestamp DESC LIMIT 1
                    """,
                    (original_model, alternative_model, task_id)
                )
                row = await cursor.fetchone()
                
                self.assertIsNotNone(row, "Failover event should be logged")
                
                # Verify all required fields are present and correct
                self.assertIsNotNone(row[0], "Timestamp should be present")
                self.assertEqual(row[1], original_model, "Original model should match")
                self.assertEqual(row[2], alternative_model, "Alternative model should match")
                self.assertEqual(row[3], failover_reason.value, "Reason should match")
                self.assertEqual(row[4], task_id, "Task ID should match")
                
                # Verify timestamp is recent (within last minute)
                timestamp = datetime.fromisoformat(row[0])
                time_diff = datetime.now() - timestamp
                self.assertLess(
                    time_diff.total_seconds(),
                    60,
                    "Timestamp should be recent"
                )
        
        asyncio.run(run_test())
    
    @settings(max_examples=15, deadline=None)
    @given(
        primary_model=model_id_strategy(),
        task_id=task_id_strategy(),
        agent_type=agent_type_strategy(),
        max_retries=max_retries_strategy(),
        base_backoff=base_backoff_strategy()
    )
    def test_property_20_exponential_backoff_retry(
        self,
        primary_model: str,
        task_id: str,
        agent_type: str,
        max_retries: int,
        base_backoff: int
    ):
        """
        Feature: api-model-management
        Property 20: Exponential backoff retry
        
        For any request that fails when no alternatives are available, retries
        should occur with exponentially increasing delays (2^n * base_delay).
        
        Validates: Requirements 5.3
        """
        async def run_test():
            # Create components
            registry, health_checker, rate_limiter, performance_monitor, selector = self._create_components()
            
            # Create failover manager with configurable parameters
            failover_manager = FailoverManager(
                model_selector=selector,
                db_path=self.db_path,
                max_retries=max_retries,
                base_backoff_seconds=base_backoff
            )
            
            # Create task
            task = AgentTask(
                id=task_id,
                type="test_task",
                priority=TaskPriority.MEDIUM
            )
            
            # Track retry timings
            retry_times = []
            
            async def mock_request_func(model_id: str):
                retry_times.append(datetime.now())
                raise ModelUnavailableError(f"Model {model_id} is unavailable", model_id=model_id)
            
            # Mock selector to return None (no alternatives available)
            with patch.object(selector, 'select_model', new_callable=AsyncMock) as mock_select:
                mock_select.return_value = None
                
                # Execute with failover (should fail after retries)
                try:
                    await failover_manager.execute_with_failover(
                        primary_model=primary_model,
                        task=task,
                        agent_type=agent_type,
                        request_func=mock_request_func
                    )
                    self.fail("Should have raised FailoverError")
                except FailoverError:
                    pass  # Expected
                
                # Verify number of retries
                self.assertEqual(
                    len(retry_times),
                    max_retries,
                    f"Should have attempted {max_retries} times"
                )
                
                # Verify exponential backoff delays
                for i in range(1, len(retry_times)):
                    delay = (retry_times[i] - retry_times[i-1]).total_seconds()
                    expected_delay = base_backoff * (2 ** (i-1))
                    
                    # Allow 30% tolerance for timing variations
                    tolerance = 0.3
                    self.assertGreaterEqual(
                        delay,
                        expected_delay * (1 - tolerance),
                        f"Delay {i} should be at least {expected_delay * (1 - tolerance)}s"
                    )
                    self.assertLessEqual(
                        delay,
                        expected_delay * (1 + tolerance) + 0.5,  # Extra tolerance for async overhead
                        f"Delay {i} should be at most {expected_delay * (1 + tolerance) + 0.5}s"
                    )
        
        asyncio.run(run_test())
    
    @settings(max_examples=20, deadline=5000)
    @given(
        original_model=model_id_strategy(),
        alternative_model=model_id_strategy(),
        task_id=task_id_strategy(),
        agent_type=agent_type_strategy()
    )
    def test_property_21_original_model_retry_after_recovery(
        self,
        original_model: str,
        alternative_model: str,
        task_id: str,
        agent_type: str
    ):
        """
        Feature: api-model-management
        Property 21: Original model retry after recovery
        
        For any model that was rate-limited, after the rate limit window expires,
        the next request should attempt to use the original model.
        
        Validates: Requirements 5.4
        """
        # Skip if models are the same
        assume(original_model != alternative_model)
        
        async def run_test():
            # Create components
            registry, health_checker, rate_limiter, performance_monitor, selector = self._create_components()
            
            # Create failover manager
            failover_manager = FailoverManager(
                model_selector=selector,
                db_path=self.db_path,
                max_retries=3,
                base_backoff_seconds=1
            )
            
            # Create task
            task = AgentTask(
                id=task_id,
                type="test_task",
                priority=TaskPriority.MEDIUM
            )
            
            # Track which models were attempted
            attempted_models = []
            
            async def mock_request_func(model_id: str):
                attempted_models.append(model_id)
                
                # First attempt with original model fails (rate limited)
                if len(attempted_models) == 1 and model_id == original_model:
                    raise RateLimitError(f"Model {model_id} is rate limited", model_id=model_id)
                
                # Subsequent attempts succeed
                return ModelResponse(
                    content=f"Success with {model_id}",
                    model_id=model_id,
                    token_usage=TokenUsage(input_tokens=10, output_tokens=20, total_tokens=30),
                    latency_ms=100.0,
                    cost=0.001
                )
            
            # Mock selector to return alternative model on first call
            with patch.object(selector, 'select_model', new_callable=AsyncMock) as mock_select:
                def select_side_effect(task, agent_type):
                    # Return alternative model
                    model_metadata = registry.get_model(alternative_model)
                    return ModelSelection(
                        model_id=alternative_model,
                        model_metadata=model_metadata,
                        suitability_score=0.8,
                        alternatives=[],
                        selection_reason="Alternative model"
                    )
                
                mock_select.side_effect = select_side_effect
                
                # First request - should failover to alternative
                response1 = await failover_manager.execute_with_failover(
                    primary_model=original_model,
                    task=task,
                    agent_type=agent_type,
                    request_func=mock_request_func
                )
                
                self.assertEqual(
                    response1.model_id,
                    alternative_model,
                    "First request should use alternative model"
                )
                
                # Verify that original model was attempted first
                self.assertEqual(
                    attempted_models[0],
                    original_model,
                    "Should have attempted original model first"
                )
                
                # Verify that alternative was used after failover
                self.assertEqual(
                    attempted_models[1],
                    alternative_model,
                    "Should have used alternative model after failover"
                )
                
                # Simulate rate limit window expiring by mocking selector to return original model
                attempted_models.clear()
                
                def select_original_side_effect(task, agent_type):
                    # Return original model (now recovered)
                    model_metadata = registry.get_model(original_model)
                    return ModelSelection(
                        model_id=original_model,
                        model_metadata=model_metadata,
                        suitability_score=0.9,
                        alternatives=[alternative_model],
                        selection_reason="Original model recovered"
                    )
                
                mock_select.side_effect = select_original_side_effect
                
                # Second request - should attempt original model again
                response2 = await failover_manager.execute_with_failover(
                    primary_model=original_model,
                    task=task,
                    agent_type=agent_type,
                    request_func=mock_request_func
                )
                
                # Verify that original model was attempted (and succeeded this time)
                self.assertIn(
                    original_model,
                    attempted_models,
                    "Should have attempted original model after recovery"
                )
        
        asyncio.run(run_test())
    
    @settings(max_examples=20, deadline=5000)
    @given(
        model_id=model_id_strategy(),
        num_failovers=num_failovers_strategy(),
        alert_threshold=st.integers(min_value=2, max_value=5),
        alert_window_hours=st.integers(min_value=1, max_value=2)
    )
    def test_property_22_excessive_failover_alerting(
        self,
        model_id: str,
        num_failovers: int,
        alert_threshold: int,
        alert_window_hours: int
    ):
        """
        Feature: api-model-management
        Property 22: Excessive failover alerting
        
        For any model that experiences more than 3 failover events within a
        1-hour window, an alert should be triggered.
        
        Validates: Requirements 5.5
        """
        async def run_test():
            # Create components
            registry, health_checker, rate_limiter, performance_monitor, selector = self._create_components()
            
            # Create failover manager with configurable alert threshold
            failover_manager = FailoverManager(
                model_selector=selector,
                db_path=self.db_path,
                max_retries=3,
                base_backoff_seconds=1,
                alert_threshold=alert_threshold,
                alert_window_hours=alert_window_hours
            )
            
            # Clear any existing failover events for this model
            async with aiosqlite.connect(self.db_path) as db:
                await db.execute("DELETE FROM failover_events WHERE original_model = ?", (model_id,))
                await db.commit()
            
            # Track alerts
            alerts_triggered = []
            
            # Patch the logger to capture alerts
            with patch('agentic_sdlc.orchestration.api_model_management.failover_manager.logger') as mock_logger:
                # Record failover events
                for i in range(num_failovers):
                    await failover_manager.record_failover(
                        original_model=model_id,
                        alternative_model="alternative-model",
                        reason=FailoverReason.UNAVAILABLE,
                        task_id=f"task-{i}"
                    )
                    
                    # Check for excessive failover after each event
                    await failover_manager._check_excessive_failover(model_id)
                
                # Count warning calls that mention "ALERT" and "Excessive failover"
                for call in mock_logger.warning.call_args_list:
                    message = str(call[0][0])
                    if "ALERT" in message and "Excessive failover" in message and model_id in message:
                        alerts_triggered.append(message)
                
                # Verify alert behavior
                if num_failovers >= alert_threshold:
                    self.assertGreater(
                        len(alerts_triggered),
                        0,
                        f"Alert should be triggered when failovers ({num_failovers}) >= threshold ({alert_threshold})"
                    )
                    
                    # Verify alert message contains required information
                    alert_message = alerts_triggered[0]
                    self.assertIn(model_id, alert_message, "Alert should mention model ID")
                    self.assertIn(str(alert_threshold), alert_message, "Alert should mention threshold")
                else:
                    self.assertEqual(
                        len(alerts_triggered),
                        0,
                        f"Alert should not be triggered when failovers ({num_failovers}) < threshold ({alert_threshold})"
                    )
                
                # Verify failover count is tracked correctly
                failover_count = await failover_manager.get_failover_count(
                    model_id=model_id,
                    hours=alert_window_hours
                )
                
                self.assertEqual(
                    failover_count,
                    num_failovers,
                    "Failover count should match number of recorded events"
                )
        
        asyncio.run(run_test())


if __name__ == "__main__":
    unittest.main()
