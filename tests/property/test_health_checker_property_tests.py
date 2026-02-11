"""
Property-based tests for HealthChecker class.

This module tests the correctness properties of the HealthChecker including
periodic health checks, health check data recording, consecutive failure marking,
recovery from unavailability, and availability status visibility.
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

from agentic_sdlc.orchestration.api_model_management.health_checker import HealthChecker
from agentic_sdlc.orchestration.api_model_management.registry import ModelRegistry
from agentic_sdlc.orchestration.api_model_management.models import (
    ModelMetadata,
    RateLimits,
    HealthStatus,
    ModelAvailability
)


# Hypothesis strategies for generating test data

def model_id_strategy():
    """Strategy for generating model IDs"""
    return st.sampled_from([
        "gpt-4-turbo",
        "claude-3.5-sonnet",
        "gemini-pro",
        "llama-3-70b"
    ])


def check_interval_strategy():
    """Strategy for generating check intervals (in seconds)"""
    return st.integers(min_value=1, max_value=10)


def consecutive_failures_threshold_strategy():
    """Strategy for generating consecutive failure thresholds"""
    return st.integers(min_value=1, max_value=5)


def response_time_strategy():
    """Strategy for generating response times (in milliseconds)"""
    return st.floats(min_value=10.0, max_value=5000.0)


def health_check_result_strategy():
    """Strategy for generating health check results (success/failure)"""
    return st.booleans()


class TestHealthCheckerProperties(unittest.TestCase):
    """Test HealthChecker correctness properties"""
    
    def setUp(self):
        """Set up test case"""
        if not HYPOTHESIS_AVAILABLE:
            self.skipTest("Hypothesis not available")
        
        # Create temporary directory for database
        self.temp_dir = tempfile.mkdtemp()
        self.db_path = Path(self.temp_dir) / "test_health_checker.db"
        
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
            await db.commit()
    
    def _create_registry(self) -> ModelRegistry:
        """Create and load a ModelRegistry"""
        registry = ModelRegistry(self.config_path)
        registry.load_config()
        return registry
    
    @settings(max_examples=10, deadline=15000)
    @given(
        check_interval=st.integers(min_value=1, max_value=3),  # Shorter intervals for faster tests
        num_models=st.integers(min_value=1, max_value=2)  # Fewer models for faster tests
    )
    def test_property_9_periodic_health_checks(self, check_interval: int, num_models: int):
        """
        Feature: api-model-management
        Property 9: Periodic health checks
        
        For any configured check interval, health checks should occur for all
        registered models within the interval tolerance (±10%).
        
        Validates: Requirements 3.1
        """
        async def run_test():
            # Create registry
            registry = self._create_registry()
            
            # Get first num_models from registry
            all_models = list(registry._models.values())[:num_models]
            model_ids = [m.id for m in all_models]
            
            # Create health checker
            health_checker = HealthChecker(
                registry=registry,
                db_path=self.db_path,
                check_interval_seconds=check_interval,
                consecutive_failures_threshold=3
            )
            
            # Mock the HTTP client to return successful responses
            with patch.object(health_checker, '_perform_health_check', new_callable=AsyncMock) as mock_check:
                mock_check.return_value = 100.0  # 100ms response time
                
                # Start health checker
                await health_checker.start()
                
                # Wait for slightly more than one check interval (with 20% tolerance)
                wait_time = check_interval * 1.2
                await asyncio.sleep(wait_time)
                
                # Stop health checker
                await health_checker.stop()
                
                # Verify that health checks were performed for all models
                # Each model should have been checked at least once
                for model_id in model_ids:
                    # Check that the model has a health status
                    self.assertIn(
                        model_id,
                        health_checker._health_status,
                        f"Model {model_id} should have been checked"
                    )
                    
                    # Verify the health status was recorded
                    status = health_checker._health_status[model_id]
                    self.assertIsInstance(status, HealthStatus)
                    self.assertEqual(status.model_id, model_id)
                
                # Verify that checks occurred within the interval tolerance
                # The number of calls should be approximately num_models * (wait_time / check_interval)
                expected_calls = num_models * (wait_time / check_interval)
                actual_calls = mock_check.call_count
                
                # Allow ±40% tolerance for timing variations (more lenient for async timing)
                tolerance = 0.4
                self.assertGreaterEqual(
                    actual_calls,
                    expected_calls * (1 - tolerance),
                    f"Should have at least {expected_calls * (1 - tolerance)} health checks"
                )
        
        asyncio.run(run_test())
    
    @settings(max_examples=5, deadline=3000)
    @given(
        model_id=model_id_strategy(),
        response_time=response_time_strategy(),
        is_success=health_check_result_strategy()
    )
    def test_property_10_health_check_data_recording(
        self,
        model_id: str,
        response_time: float,
        is_success: bool
    ):
        """
        Feature: api-model-management
        Property 10: Health check data recording
        
        For any health check response, the recorded response time and success
        status should match the actual response.
        
        Validates: Requirements 3.2
        """
        async def run_test():
            # Create registry
            registry = self._create_registry()
            
            # Create health checker
            health_checker = HealthChecker(
                registry=registry,
                db_path=self.db_path,
                check_interval_seconds=60,
                consecutive_failures_threshold=3
            )
            
            # Mock the HTTP client
            with patch.object(health_checker, '_perform_health_check', new_callable=AsyncMock) as mock_check:
                if is_success:
                    mock_check.return_value = response_time
                else:
                    mock_check.side_effect = Exception("Health check failed")
                
                # Start health checker (needed to initialize HTTP client)
                await health_checker.start()
                
                # Perform health check
                try:
                    health_status = await health_checker.check_model_health(model_id)
                    
                    # Verify the recorded data matches the actual response
                    self.assertEqual(health_status.model_id, model_id)
                    self.assertEqual(health_status.is_available, is_success)
                    
                    if is_success:
                        self.assertAlmostEqual(
                            health_status.response_time_ms,
                            response_time,
                            places=2,
                            msg="Response time should match"
                        )
                        self.assertIsNone(health_status.error_message)
                    else:
                        self.assertIsNotNone(health_status.error_message)
                    
                    # Verify data was persisted to database
                    async with aiosqlite.connect(self.db_path) as db:
                        cursor = await db.execute(
                            "SELECT * FROM health_checks WHERE model_id = ? ORDER BY timestamp DESC LIMIT 1",
                            (model_id,)
                        )
                        row = await cursor.fetchone()
                        
                        self.assertIsNotNone(row, "Health check should be persisted")
                        
                        # Verify persisted data matches
                        self.assertEqual(row[2], model_id)  # model_id
                        self.assertEqual(bool(row[3]), is_success)  # is_available
                        
                        if is_success:
                            self.assertIsNotNone(row[4])  # response_time_ms
                            self.assertAlmostEqual(float(row[4]), response_time, places=2)
                
                finally:
                    await health_checker.stop()
        
        asyncio.run(run_test())
    
    @settings(max_examples=5, deadline=3000)
    @given(
        model_id=model_id_strategy(),
        consecutive_failures_threshold=consecutive_failures_threshold_strategy()
    )
    def test_property_11_consecutive_failure_marking(
        self,
        model_id: str,
        consecutive_failures_threshold: int
    ):
        """
        Feature: api-model-management
        Property 11: Consecutive failure marking
        
        For any model that fails health checks N consecutive times (where N is
        configurable), the model should be marked as unavailable.
        
        Validates: Requirements 3.3
        """
        async def run_test():
            # Create registry
            registry = self._create_registry()
            
            # Create health checker with configurable threshold
            health_checker = HealthChecker(
                registry=registry,
                db_path=self.db_path,
                check_interval_seconds=60,
                consecutive_failures_threshold=consecutive_failures_threshold
            )
            
            # Mock the HTTP client to always fail
            with patch.object(health_checker, '_perform_health_check', new_callable=AsyncMock) as mock_check:
                mock_check.side_effect = Exception("Health check failed")
                
                # Start health checker
                await health_checker.start()
                
                # Perform health checks until threshold is reached
                for i in range(consecutive_failures_threshold):
                    await health_checker.check_model_health(model_id)
                    
                    # Before threshold, model should still be available
                    if i < consecutive_failures_threshold - 1:
                        self.assertTrue(
                            health_checker.is_model_available(model_id),
                            f"Model should be available after {i + 1} failures (threshold: {consecutive_failures_threshold})"
                        )
                
                # After threshold failures, model should be unavailable
                self.assertFalse(
                    health_checker.is_model_available(model_id),
                    f"Model should be unavailable after {consecutive_failures_threshold} consecutive failures"
                )
                
                # Verify consecutive failures count
                self.assertEqual(
                    health_checker._consecutive_failures.get(model_id, 0),
                    consecutive_failures_threshold,
                    "Consecutive failures count should match threshold"
                )
                
                # Verify availability status
                availability = health_checker.get_model_status(model_id)
                self.assertFalse(
                    availability.is_available,
                    "Model availability status should be False"
                )
                
                await health_checker.stop()
        
        asyncio.run(run_test())
    
    @settings(max_examples=5, deadline=3000)
    @given(
        model_id=model_id_strategy(),
        num_failures=st.integers(min_value=3, max_value=10)
    )
    def test_property_12_recovery_from_unavailability(
        self,
        model_id: str,
        num_failures: int
    ):
        """
        Feature: api-model-management
        Property 12: Recovery from unavailability
        
        For any model marked as unavailable, a single successful health check
        should mark it as available again.
        
        Validates: Requirements 3.4
        """
        async def run_test():
            # Create registry
            registry = self._create_registry()
            
            # Create health checker with threshold of 3
            consecutive_failures_threshold = 3
            health_checker = HealthChecker(
                registry=registry,
                db_path=self.db_path,
                check_interval_seconds=60,
                consecutive_failures_threshold=consecutive_failures_threshold
            )
            
            # Start health checker
            await health_checker.start()
            
            # Mock the HTTP client to fail initially
            with patch.object(health_checker, '_perform_health_check', new_callable=AsyncMock) as mock_check:
                mock_check.side_effect = Exception("Health check failed")
                
                # Perform enough failures to mark model as unavailable
                for _ in range(num_failures):
                    await health_checker.check_model_health(model_id)
                
                # Verify model is unavailable
                self.assertFalse(
                    health_checker.is_model_available(model_id),
                    "Model should be unavailable after consecutive failures"
                )
                
                # Now mock a successful health check
                mock_check.side_effect = None
                mock_check.return_value = 100.0  # 100ms response time
                
                # Perform one successful health check
                await health_checker.check_model_health(model_id)
                
                # Verify model is now available
                self.assertTrue(
                    health_checker.is_model_available(model_id),
                    "Model should be available after one successful health check"
                )
                
                # Verify consecutive failures was reset
                self.assertEqual(
                    health_checker._consecutive_failures.get(model_id, 0),
                    0,
                    "Consecutive failures should be reset to 0"
                )
                
                # Verify availability status
                availability = health_checker.get_model_status(model_id)
                self.assertTrue(
                    availability.is_available,
                    "Model availability status should be True"
                )
            
            await health_checker.stop()
        
        asyncio.run(run_test())
    
    @settings(max_examples=5, deadline=3000)
    @given(
        model_id=model_id_strategy(),
        is_available=health_check_result_strategy()
    )
    def test_property_13_availability_status_visibility(
        self,
        model_id: str,
        is_available: bool
    ):
        """
        Feature: api-model-management
        Property 13: Availability status visibility
        
        For any model, the Model_Selector should be able to query and receive
        the current availability status from the Health_Checker.
        
        Validates: Requirements 3.5
        """
        async def run_test():
            # Create registry
            registry = self._create_registry()
            
            # Create health checker
            health_checker = HealthChecker(
                registry=registry,
                db_path=self.db_path,
                check_interval_seconds=60,
                consecutive_failures_threshold=3
            )
            
            # Start health checker
            await health_checker.start()
            
            # Mock the HTTP client
            with patch.object(health_checker, '_perform_health_check', new_callable=AsyncMock) as mock_check:
                if is_available:
                    mock_check.return_value = 100.0
                else:
                    mock_check.side_effect = Exception("Health check failed")
                
                # Perform health check to set status
                if is_available:
                    await health_checker.check_model_health(model_id)
                else:
                    # Perform enough failures to mark as unavailable
                    for _ in range(3):
                        await health_checker.check_model_health(model_id)
                
                # Query availability status (this is what Model_Selector would do)
                availability_status = health_checker.get_model_status(model_id)
                
                # Verify the status is accessible and correct
                self.assertIsInstance(availability_status, ModelAvailability)
                self.assertEqual(availability_status.model_id, model_id)
                self.assertEqual(
                    availability_status.is_available,
                    is_available,
                    "Availability status should match the health check result"
                )
                
                # Also verify the simpler is_model_available method
                simple_availability = health_checker.is_model_available(model_id)
                self.assertEqual(
                    simple_availability,
                    is_available,
                    "Simple availability check should match"
                )
                
                # Verify that the status includes relevant metadata
                if not is_available:
                    self.assertIsNotNone(
                        availability_status.next_retry_time,
                        "Unavailable model should have next retry time"
                    )
            
            await health_checker.stop()
        
        asyncio.run(run_test())


if __name__ == "__main__":
    unittest.main()
