"""
Unit tests for HealthChecker class.

This module tests specific examples and edge cases for the HealthChecker including
periodic execution timing, consecutive failure threshold, and recovery behavior.
"""

import unittest
import asyncio
import tempfile
import aiosqlite
from pathlib import Path
from datetime import datetime, timedelta
from unittest.mock import Mock, AsyncMock, patch, MagicMock

from agentic_sdlc.orchestration.api_model_management.health_checker import HealthChecker
from agentic_sdlc.orchestration.api_model_management.registry import ModelRegistry
from agentic_sdlc.orchestration.api_model_management.models import (
    ModelMetadata,
    RateLimits,
    HealthStatus,
    ModelAvailability
)


class TestHealthCheckerUnitTests(unittest.TestCase):
    """Unit tests for HealthChecker"""
    
    def setUp(self):
        """Set up test case"""
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
    
    # Test 1: Periodic execution timing
    
    def test_periodic_execution_timing_with_2_second_interval(self):
        """
        Test that health checks occur at the configured interval.
        
        This test verifies that when a 2-second check interval is configured,
        health checks are performed approximately every 2 seconds.
        
        Requirements: 3.1
        """
        async def run_test():
            registry = self._create_registry()
            check_interval = 2  # 2 seconds
            
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
                
                # Wait for 2.5 intervals (5 seconds) to allow for multiple checks
                wait_time = check_interval * 2.5
                await asyncio.sleep(wait_time)
                
                # Stop health checker
                await health_checker.stop()
                
                # Calculate expected number of checks
                # With 3 models and 2.5 intervals, we expect approximately 7-8 checks total
                # (3 models * 2.5 intervals = 7.5 checks)
                expected_min_checks = 6  # Allow some tolerance
                expected_max_checks = 10
                
                actual_checks = mock_check.call_count
                
                self.assertGreaterEqual(
                    actual_checks,
                    expected_min_checks,
                    f"Should have at least {expected_min_checks} health checks, got {actual_checks}"
                )
                self.assertLessEqual(
                    actual_checks,
                    expected_max_checks,
                    f"Should have at most {expected_max_checks} health checks, got {actual_checks}"
                )
        
        asyncio.run(run_test())
    
    def test_periodic_execution_timing_with_1_second_interval(self):
        """
        Test that health checks occur at a faster 1-second interval.
        
        This test verifies that shorter intervals work correctly.
        
        Requirements: 3.1
        """
        async def run_test():
            registry = self._create_registry()
            check_interval = 1  # 1 second
            
            health_checker = HealthChecker(
                registry=registry,
                db_path=self.db_path,
                check_interval_seconds=check_interval,
                consecutive_failures_threshold=3
            )
            
            # Mock the HTTP client
            with patch.object(health_checker, '_perform_health_check', new_callable=AsyncMock) as mock_check:
                mock_check.return_value = 50.0
                
                await health_checker.start()
                
                # Wait for 1.5 intervals
                await asyncio.sleep(1.5)
                
                await health_checker.stop()
                
                # With 3 models and 1.5 intervals, expect 4-5 checks
                actual_checks = mock_check.call_count
                self.assertGreaterEqual(actual_checks, 3)
                self.assertLessEqual(actual_checks, 6)
        
        asyncio.run(run_test())
    
    def test_periodic_execution_stops_when_stopped(self):
        """
        Test that periodic execution stops when stop() is called.
        
        This test verifies that no more health checks occur after stopping.
        
        Requirements: 3.1
        """
        async def run_test():
            registry = self._create_registry()
            
            health_checker = HealthChecker(
                registry=registry,
                db_path=self.db_path,
                check_interval_seconds=1,
                consecutive_failures_threshold=3
            )
            
            with patch.object(health_checker, '_perform_health_check', new_callable=AsyncMock) as mock_check:
                mock_check.return_value = 100.0
                
                await health_checker.start()
                await asyncio.sleep(0.5)  # Let some checks happen
                
                # Record the call count before stopping
                calls_before_stop = mock_check.call_count
                
                # Stop the health checker
                await health_checker.stop()
                
                # Wait a bit more
                await asyncio.sleep(2)
                
                # Call count should not have increased significantly
                calls_after_stop = mock_check.call_count
                
                # Allow at most 1 additional call (for in-flight check)
                self.assertLessEqual(
                    calls_after_stop - calls_before_stop,
                    1,
                    "Health checks should stop after stop() is called"
                )
        
        asyncio.run(run_test())
    
    # Test 2: Consecutive failure threshold
    
    def test_consecutive_failure_threshold_exactly_3_failures(self):
        """
        Test that a model is marked unavailable after exactly 3 consecutive failures.
        
        This test verifies the default threshold of 3 consecutive failures.
        
        Requirements: 3.3
        """
        async def run_test():
            registry = self._create_registry()
            model_id = "gpt-4-turbo"
            
            health_checker = HealthChecker(
                registry=registry,
                db_path=self.db_path,
                check_interval_seconds=60,
                consecutive_failures_threshold=3
            )
            
            with patch.object(health_checker, '_perform_health_check', new_callable=AsyncMock) as mock_check:
                mock_check.side_effect = Exception("Connection timeout")
                
                await health_checker.start()
                
                # First failure - should still be available
                await health_checker.check_model_health(model_id)
                self.assertTrue(health_checker.is_model_available(model_id))
                self.assertEqual(health_checker._consecutive_failures[model_id], 1)
                
                # Second failure - should still be available
                await health_checker.check_model_health(model_id)
                self.assertTrue(health_checker.is_model_available(model_id))
                self.assertEqual(health_checker._consecutive_failures[model_id], 2)
                
                # Third failure - should now be unavailable
                await health_checker.check_model_health(model_id)
                self.assertFalse(health_checker.is_model_available(model_id))
                self.assertEqual(health_checker._consecutive_failures[model_id], 3)
                
                await health_checker.stop()
        
        asyncio.run(run_test())
    
    def test_consecutive_failure_threshold_custom_threshold_5(self):
        """
        Test that a custom threshold of 5 consecutive failures works correctly.
        
        This test verifies that the threshold is configurable.
        
        Requirements: 3.3
        """
        async def run_test():
            registry = self._create_registry()
            model_id = "claude-3.5-sonnet"
            custom_threshold = 5
            
            health_checker = HealthChecker(
                registry=registry,
                db_path=self.db_path,
                check_interval_seconds=60,
                consecutive_failures_threshold=custom_threshold
            )
            
            with patch.object(health_checker, '_perform_health_check', new_callable=AsyncMock) as mock_check:
                mock_check.side_effect = Exception("Service unavailable")
                
                await health_checker.start()
                
                # Perform 4 failures - should still be available
                for i in range(4):
                    await health_checker.check_model_health(model_id)
                    self.assertTrue(
                        health_checker.is_model_available(model_id),
                        f"Model should be available after {i + 1} failures (threshold: {custom_threshold})"
                    )
                
                # Fifth failure - should now be unavailable
                await health_checker.check_model_health(model_id)
                self.assertFalse(health_checker.is_model_available(model_id))
                self.assertEqual(health_checker._consecutive_failures[model_id], custom_threshold)
                
                await health_checker.stop()
        
        asyncio.run(run_test())
    
    def test_consecutive_failure_threshold_with_threshold_1(self):
        """
        Test edge case where threshold is 1 (immediate unavailability).
        
        This test verifies that a threshold of 1 marks the model unavailable
        immediately after the first failure.
        
        Requirements: 3.3
        """
        async def run_test():
            registry = self._create_registry()
            model_id = "gemini-pro"
            
            health_checker = HealthChecker(
                registry=registry,
                db_path=self.db_path,
                check_interval_seconds=60,
                consecutive_failures_threshold=1
            )
            
            with patch.object(health_checker, '_perform_health_check', new_callable=AsyncMock) as mock_check:
                mock_check.side_effect = Exception("Immediate failure")
                
                await health_checker.start()
                
                # First failure - should immediately be unavailable
                await health_checker.check_model_health(model_id)
                self.assertFalse(health_checker.is_model_available(model_id))
                self.assertEqual(health_checker._consecutive_failures[model_id], 1)
                
                await health_checker.stop()
        
        asyncio.run(run_test())
    
    def test_consecutive_failures_reset_on_success(self):
        """
        Test that consecutive failures counter resets on a successful check.
        
        This test verifies that a success between failures resets the counter.
        
        Requirements: 3.3
        """
        async def run_test():
            registry = self._create_registry()
            model_id = "gpt-4-turbo"
            
            health_checker = HealthChecker(
                registry=registry,
                db_path=self.db_path,
                check_interval_seconds=60,
                consecutive_failures_threshold=3
            )
            
            with patch.object(health_checker, '_perform_health_check', new_callable=AsyncMock) as mock_check:
                await health_checker.start()
                
                # Two failures
                mock_check.side_effect = Exception("Failure")
                await health_checker.check_model_health(model_id)
                await health_checker.check_model_health(model_id)
                self.assertEqual(health_checker._consecutive_failures[model_id], 2)
                self.assertTrue(health_checker.is_model_available(model_id))
                
                # One success - should reset counter
                mock_check.side_effect = None
                mock_check.return_value = 100.0
                await health_checker.check_model_health(model_id)
                self.assertEqual(health_checker._consecutive_failures[model_id], 0)
                self.assertTrue(health_checker.is_model_available(model_id))
                
                # Two more failures - should still be available (counter was reset)
                mock_check.side_effect = Exception("Failure again")
                await health_checker.check_model_health(model_id)
                await health_checker.check_model_health(model_id)
                self.assertEqual(health_checker._consecutive_failures[model_id], 2)
                self.assertTrue(health_checker.is_model_available(model_id))
                
                await health_checker.stop()
        
        asyncio.run(run_test())
    
    # Test 3: Recovery behavior
    
    def test_recovery_after_3_failures_with_single_success(self):
        """
        Test that a model recovers (becomes available) after a single successful check.
        
        This test verifies the basic recovery behavior after being marked unavailable.
        
        Requirements: 3.4
        """
        async def run_test():
            registry = self._create_registry()
            model_id = "gpt-4-turbo"
            
            health_checker = HealthChecker(
                registry=registry,
                db_path=self.db_path,
                check_interval_seconds=60,
                consecutive_failures_threshold=3
            )
            
            with patch.object(health_checker, '_perform_health_check', new_callable=AsyncMock) as mock_check:
                await health_checker.start()
                
                # Cause 3 consecutive failures to mark as unavailable
                mock_check.side_effect = Exception("Service down")
                for _ in range(3):
                    await health_checker.check_model_health(model_id)
                
                # Verify model is unavailable
                self.assertFalse(health_checker.is_model_available(model_id))
                self.assertEqual(health_checker._consecutive_failures[model_id], 3)
                
                # Now perform a successful health check
                mock_check.side_effect = None
                mock_check.return_value = 150.0
                await health_checker.check_model_health(model_id)
                
                # Verify model is now available
                self.assertTrue(health_checker.is_model_available(model_id))
                self.assertEqual(health_checker._consecutive_failures[model_id], 0)
                
                # Verify availability status
                availability = health_checker.get_model_status(model_id)
                self.assertTrue(availability.is_available)
                self.assertIsNotNone(availability.last_successful_request)
                
                await health_checker.stop()
        
        asyncio.run(run_test())
    
    def test_recovery_after_10_failures_with_single_success(self):
        """
        Test recovery after many consecutive failures (10).
        
        This test verifies that recovery works even after many failures.
        
        Requirements: 3.4
        """
        async def run_test():
            registry = self._create_registry()
            model_id = "claude-3.5-sonnet"
            
            health_checker = HealthChecker(
                registry=registry,
                db_path=self.db_path,
                check_interval_seconds=60,
                consecutive_failures_threshold=3
            )
            
            with patch.object(health_checker, '_perform_health_check', new_callable=AsyncMock) as mock_check:
                await health_checker.start()
                
                # Cause 10 consecutive failures
                mock_check.side_effect = Exception("Extended outage")
                for _ in range(10):
                    await health_checker.check_model_health(model_id)
                
                # Verify model is unavailable
                self.assertFalse(health_checker.is_model_available(model_id))
                self.assertEqual(health_checker._consecutive_failures[model_id], 10)
                
                # Single successful check
                mock_check.side_effect = None
                mock_check.return_value = 200.0
                await health_checker.check_model_health(model_id)
                
                # Verify full recovery
                self.assertTrue(health_checker.is_model_available(model_id))
                self.assertEqual(health_checker._consecutive_failures[model_id], 0)
                
                await health_checker.stop()
        
        asyncio.run(run_test())
    
    def test_recovery_updates_availability_status_correctly(self):
        """
        Test that recovery properly updates all availability status fields.
        
        This test verifies that ModelAvailability is updated correctly on recovery.
        
        Requirements: 3.4
        """
        async def run_test():
            registry = self._create_registry()
            model_id = "gemini-pro"
            
            health_checker = HealthChecker(
                registry=registry,
                db_path=self.db_path,
                check_interval_seconds=60,
                consecutive_failures_threshold=3
            )
            
            with patch.object(health_checker, '_perform_health_check', new_callable=AsyncMock) as mock_check:
                await health_checker.start()
                
                # Mark as unavailable
                mock_check.side_effect = Exception("Temporary failure")
                for _ in range(3):
                    await health_checker.check_model_health(model_id)
                
                # Check unavailable status
                unavailable_status = health_checker.get_model_status(model_id)
                self.assertFalse(unavailable_status.is_available)
                self.assertIsNotNone(unavailable_status.next_retry_time)
                self.assertIsNone(unavailable_status.last_successful_request)
                
                # Recover
                mock_check.side_effect = None
                mock_check.return_value = 120.0
                await health_checker.check_model_health(model_id)
                
                # Check available status
                available_status = health_checker.get_model_status(model_id)
                self.assertTrue(available_status.is_available)
                self.assertIsNone(available_status.next_retry_time)
                self.assertIsNotNone(available_status.last_successful_request)
                
                await health_checker.stop()
        
        asyncio.run(run_test())
    
    def test_recovery_persists_successful_check_to_database(self):
        """
        Test that recovery health check is persisted to the database.
        
        This test verifies that the successful recovery check is recorded.
        
        Requirements: 3.4
        """
        async def run_test():
            registry = self._create_registry()
            model_id = "gpt-4-turbo"
            
            health_checker = HealthChecker(
                registry=registry,
                db_path=self.db_path,
                check_interval_seconds=60,
                consecutive_failures_threshold=3
            )
            
            with patch.object(health_checker, '_perform_health_check', new_callable=AsyncMock) as mock_check:
                await health_checker.start()
                
                # Mark as unavailable
                mock_check.side_effect = Exception("Down")
                for _ in range(3):
                    await health_checker.check_model_health(model_id)
                
                # Recover
                mock_check.side_effect = None
                mock_check.return_value = 180.0
                await health_checker.check_model_health(model_id)
                
                # Check database for the successful recovery check
                async with aiosqlite.connect(self.db_path) as db:
                    cursor = await db.execute(
                        """
                        SELECT is_available, response_time_ms, error_message 
                        FROM health_checks 
                        WHERE model_id = ? 
                        ORDER BY timestamp DESC 
                        LIMIT 1
                        """,
                        (model_id,)
                    )
                    row = await cursor.fetchone()
                    
                    self.assertIsNotNone(row)
                    self.assertTrue(bool(row[0]))  # is_available
                    self.assertAlmostEqual(float(row[1]), 180.0, places=1)  # response_time_ms
                    self.assertIsNone(row[2])  # error_message should be None
                
                await health_checker.stop()
        
        asyncio.run(run_test())


if __name__ == "__main__":
    unittest.main()
