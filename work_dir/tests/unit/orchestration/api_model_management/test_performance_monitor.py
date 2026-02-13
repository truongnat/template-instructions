"""
Unit tests for PerformanceMonitor class.

This module tests specific examples and edge cases for the PerformanceMonitor including
rolling average edge cases, degradation detection thresholds, and metric persistence.

Feature: api-model-management
"""

import unittest
import asyncio
import tempfile
from pathlib import Path
from datetime import datetime, timedelta
import shutil

from agentic_sdlc.orchestration.api_model_management.performance_monitor import PerformanceMonitor
from agentic_sdlc.orchestration.api_model_management.database import DatabaseManager
from agentic_sdlc.orchestration.api_model_management.models import PerformanceMetrics, PerformanceDegradation


class TestPerformanceMonitorUnit(unittest.TestCase):
    """
    Unit tests for PerformanceMonitor.
    
    Tests specific examples and edge cases:
    - Rolling average edge cases
    - Degradation detection thresholds
    - Metric persistence
    """
    
    def setUp(self):
        """Set up test case with temporary database"""
        # Create unique temp directory for each test
        self.temp_dir = tempfile.mkdtemp()
        import time
        db_name = f"test_performance_monitor_{int(time.time() * 1000000)}.db"
        self.db_path = Path(self.temp_dir) / db_name
        
        # Initialize database synchronously
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        self.db_manager = DatabaseManager(self.db_path)
        loop.run_until_complete(self.db_manager.initialize())
        loop.close()
    
    def tearDown(self):
        """Clean up test database"""
        if hasattr(self, 'temp_dir'):
            shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_rolling_average_empty_window(self):
        """
        Test rolling average calculation with no data in window.
        
        Edge case: Empty window should return zero metrics.
        
        **Validates: Requirements 11.3**
        """
        async def test():
            monitor = PerformanceMonitor(self.db_path)
            
            # Get metrics for model with no data
            metrics = await monitor.get_model_performance("nonexistent-model", window_hours=24)
            
            # Verify empty metrics
            self.assertEqual(metrics.model_id, "nonexistent-model")
            self.assertEqual(metrics.window_hours, 24)
            self.assertEqual(metrics.total_requests, 0)
            self.assertEqual(metrics.successful_requests, 0)
            self.assertEqual(metrics.failed_requests, 0)
            self.assertEqual(metrics.success_rate, 0.0)
            self.assertEqual(metrics.average_latency_ms, 0.0)
            self.assertEqual(metrics.p50_latency_ms, 0.0)
            self.assertEqual(metrics.p95_latency_ms, 0.0)
            self.assertEqual(metrics.p99_latency_ms, 0.0)
            self.assertEqual(metrics.average_quality_score, 0.0)
        
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            loop.run_until_complete(test())
        finally:
            loop.close()
    
    def test_rolling_average_single_data_point(self):
        """
        Test rolling average calculation with single data point.
        
        Edge case: Single data point should have all percentiles equal.
        
        **Validates: Requirements 11.3**
        """
        async def test():
            monitor = PerformanceMonitor(self.db_path)
            model_id = "test-model"
            
            # Record single performance data point
            await monitor.record_performance(
                model_id=model_id,
                agent_type="PM",
                latency_ms=1500.0,
                success=True,
                quality_score=0.85,
                task_id="test-task-1"
            )
            
            # Get metrics
            metrics = await monitor.get_model_performance(model_id, window_hours=1)
            
            # Verify single data point metrics
            self.assertEqual(metrics.total_requests, 1)
            self.assertEqual(metrics.successful_requests, 1)
            self.assertEqual(metrics.success_rate, 1.0)
            self.assertEqual(metrics.average_latency_ms, 1500.0)
            # All percentiles should equal the single value
            self.assertEqual(metrics.p50_latency_ms, 1500.0)
            self.assertEqual(metrics.p95_latency_ms, 1500.0)
            self.assertEqual(metrics.p99_latency_ms, 1500.0)
            self.assertEqual(metrics.average_quality_score, 0.85)
        
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            loop.run_until_complete(test())
        finally:
            loop.close()
    
    def test_rolling_average_excludes_old_data(self):
        """
        Test that rolling average excludes data outside the time window.
        
        Edge case: Old data should not affect current window metrics.
        
        **Validates: Requirements 11.3**
        """
        async def test():
            monitor = PerformanceMonitor(self.db_path)
            model_id = "test-model"
            
            # Record recent data (within 1 hour window)
            await monitor.record_performance(
                model_id=model_id,
                agent_type="PM",
                latency_ms=1000.0,
                success=True,
                quality_score=0.9,
                task_id="recent-task-1"
            )
            await monitor.record_performance(
                model_id=model_id,
                agent_type="PM",
                latency_ms=1200.0,
                success=True,
                quality_score=0.85,
                task_id="recent-task-2"
            )
            
            # Insert old data (outside 1 hour window) directly into database
            old_timestamp = datetime.now() - timedelta(hours=2)
            import aiosqlite
            async with aiosqlite.connect(self.db_path) as db:
                await db.execute("""
                    INSERT INTO performance_records 
                    (timestamp, model_id, agent_type, task_id, latency_ms, success, quality_score)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                """, (old_timestamp, model_id, "PM", "old-task", 5000.0, False, 0.3))
                await db.commit()
            
            # Get metrics for 1 hour window
            metrics = await monitor.get_model_performance(model_id, window_hours=1)
            
            # Verify only recent data is included
            self.assertEqual(metrics.total_requests, 2)
            self.assertEqual(metrics.successful_requests, 2)
            self.assertEqual(metrics.success_rate, 1.0)
            # Average should be (1000 + 1200) / 2 = 1100, not including 5000
            self.assertAlmostEqual(metrics.average_latency_ms, 1100.0, places=1)
            # Quality should be (0.9 + 0.85) / 2 = 0.875, not including 0.3
            self.assertAlmostEqual(metrics.average_quality_score, 0.875, places=2)
        
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            loop.run_until_complete(test())
        finally:
            loop.close()
    
    def test_degradation_detection_exactly_at_threshold(self):
        """
        Test degradation detection when success rate exactly equals threshold.
        
        Edge case: Success rate = threshold should not trigger alert.
        
        **Validates: Requirements 11.4**
        """
        async def test():
            monitor = PerformanceMonitor(self.db_path)
            model_id = "test-model"
            threshold = 0.8
            
            # Record 8 successful and 2 failed requests (80% success rate)
            for i in range(8):
                await monitor.record_performance(
                    model_id=model_id,
                    agent_type="PM",
                    latency_ms=1000.0,
                    success=True,
                    quality_score=0.9,
                    task_id=f"success-task-{i}"
                )
            
            for i in range(2):
                await monitor.record_performance(
                    model_id=model_id,
                    agent_type="PM",
                    latency_ms=1000.0,
                    success=False,
                    quality_score=0.5,
                    task_id=f"fail-task-{i}"
                )
            
            # Check for degradation
            degradation = await monitor.detect_degradation(model_id, threshold=threshold)
            
            # Verify: exactly at threshold should not trigger alert
            self.assertIsNone(degradation)
        
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            loop.run_until_complete(test())
        finally:
            loop.close()
    
    def test_degradation_detection_just_below_threshold(self):
        """
        Test degradation detection when success rate is just below threshold.
        
        Edge case: Success rate < threshold by small amount should trigger alert.
        
        **Validates: Requirements 11.4**
        """
        async def test():
            monitor = PerformanceMonitor(self.db_path)
            model_id = "test-model"
            threshold = 0.8
            
            # Record 7 successful and 3 failed requests (70% success rate)
            for i in range(7):
                await monitor.record_performance(
                    model_id=model_id,
                    agent_type="PM",
                    latency_ms=1000.0,
                    success=True,
                    quality_score=0.9,
                    task_id=f"success-task-{i}"
                )
            
            for i in range(3):
                await monitor.record_performance(
                    model_id=model_id,
                    agent_type="PM",
                    latency_ms=1000.0,
                    success=False,
                    quality_score=0.5,
                    task_id=f"fail-task-{i}"
                )
            
            # Check for degradation
            degradation = await monitor.detect_degradation(model_id, threshold=threshold)
            
            # Verify: below threshold should trigger alert
            self.assertIsNotNone(degradation)
            self.assertIsInstance(degradation, PerformanceDegradation)
            self.assertEqual(degradation.model_id, model_id)
            self.assertEqual(degradation.metric, "success_rate")
            self.assertAlmostEqual(degradation.current_value, 0.7, places=2)
            self.assertEqual(degradation.threshold, threshold)
        
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            loop.run_until_complete(test())
        finally:
            loop.close()
    
    def test_degradation_detection_no_requests(self):
        """
        Test degradation detection with no requests in window.
        
        Edge case: No requests should not trigger degradation alert.
        
        **Validates: Requirements 11.4**
        """
        async def test():
            monitor = PerformanceMonitor(self.db_path)
            model_id = "test-model"
            
            # Check for degradation with no data
            degradation = await monitor.detect_degradation(model_id, threshold=0.8)
            
            # Verify: no data should not trigger alert
            self.assertIsNone(degradation)
        
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            loop.run_until_complete(test())
        finally:
            loop.close()
    
    def test_metric_persistence_with_null_quality_score(self):
        """
        Test metric persistence when quality score is None.
        
        Edge case: Null quality scores should be handled gracefully.
        
        **Validates: Requirements 11.5**
        """
        async def test():
            monitor = PerformanceMonitor(self.db_path)
            model_id = "test-model"
            
            # Record performance with quality score
            await monitor.record_performance(
                model_id=model_id,
                agent_type="PM",
                latency_ms=1000.0,
                success=True,
                quality_score=0.9,
                task_id="task-with-quality"
            )
            
            # Manually insert record with NULL quality score
            import aiosqlite
            async with aiosqlite.connect(self.db_path) as db:
                await db.execute("""
                    INSERT INTO performance_records 
                    (timestamp, model_id, agent_type, task_id, latency_ms, success, quality_score)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                """, (datetime.now(), model_id, "PM", "task-no-quality", 1200.0, True, None))
                await db.commit()
            
            # Get metrics
            metrics = await monitor.get_model_performance(model_id, window_hours=1)
            
            # Verify metrics handle null quality scores
            self.assertEqual(metrics.total_requests, 2)
            self.assertEqual(metrics.successful_requests, 2)
            # Average quality should only include non-null values
            self.assertAlmostEqual(metrics.average_quality_score, 0.9, places=2)
        
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            loop.run_until_complete(test())
        finally:
            loop.close()
    
    def test_percentile_calculation_with_even_count(self):
        """
        Test percentile calculation with even number of data points.
        
        Edge case: Percentile interpolation with even count.
        
        **Validates: Requirements 11.3**
        """
        async def test():
            monitor = PerformanceMonitor(self.db_path)
            model_id = "test-model"
            
            # Record 4 requests with different latencies
            latencies = [1000.0, 2000.0, 3000.0, 4000.0]
            for i, latency in enumerate(latencies):
                await monitor.record_performance(
                    model_id=model_id,
                    agent_type="PM",
                    latency_ms=latency,
                    success=True,
                    quality_score=0.9,
                    task_id=f"task-{i}"
                )
            
            # Get metrics
            metrics = await monitor.get_model_performance(model_id, window_hours=1)
            
            # Verify percentile calculations
            self.assertEqual(metrics.total_requests, 4)
            self.assertAlmostEqual(metrics.average_latency_ms, 2500.0, places=1)
            # P50 should be between 2nd and 3rd values: (2000 + 3000) / 2 = 2500
            self.assertAlmostEqual(metrics.p50_latency_ms, 2500.0, places=1)
            # P95 should be close to 4000
            self.assertGreater(metrics.p95_latency_ms, 3500.0)
            # P99 should be close to 4000
            self.assertGreater(metrics.p99_latency_ms, 3900.0)
        
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            loop.run_until_complete(test())
        finally:
            loop.close()
    
    def test_get_recent_quality_scores(self):
        """
        Test retrieving recent quality scores.
        
        **Validates: Requirements 11.5**
        """
        async def test():
            monitor = PerformanceMonitor(self.db_path)
            model_id = "test-model"
            
            # Record multiple requests with different quality scores
            quality_scores = [0.9, 0.85, 0.8, 0.75, 0.7]
            for i, score in enumerate(quality_scores):
                await monitor.record_performance(
                    model_id=model_id,
                    agent_type="PM",
                    latency_ms=1000.0,
                    success=True,
                    quality_score=score,
                    task_id=f"task-{i}"
                )
            
            # Get recent quality scores
            recent_scores = await monitor.get_recent_quality_scores(model_id, limit=3)
            
            # Verify most recent 3 scores (in reverse order)
            self.assertEqual(len(recent_scores), 3)
            self.assertAlmostEqual(recent_scores[0], 0.7, places=2)
            self.assertAlmostEqual(recent_scores[1], 0.75, places=2)
            self.assertAlmostEqual(recent_scores[2], 0.8, places=2)
        
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            loop.run_until_complete(test())
        finally:
            loop.close()
    
    def test_get_performance_by_agent_type(self):
        """
        Test retrieving performance metrics by agent type.
        
        **Validates: Requirements 11.2**
        """
        async def test():
            monitor = PerformanceMonitor(self.db_path)
            
            # Record performance for different models and agent types
            await monitor.record_performance(
                model_id="gpt-4-turbo",
                agent_type="PM",
                latency_ms=1000.0,
                success=True,
                quality_score=0.9,
                task_id="pm-task-1"
            )
            await monitor.record_performance(
                model_id="claude-3.5-sonnet",
                agent_type="PM",
                latency_ms=1200.0,
                success=True,
                quality_score=0.85,
                task_id="pm-task-2"
            )
            await monitor.record_performance(
                model_id="gpt-4-turbo",
                agent_type="BA",
                latency_ms=1500.0,
                success=False,
                quality_score=0.6,
                task_id="ba-task-1"
            )
            
            # Get performance by agent type
            pm_metrics = await monitor.get_performance_by_agent_type("PM", window_hours=1)
            ba_metrics = await monitor.get_performance_by_agent_type("BA", window_hours=1)
            
            # Verify PM metrics
            self.assertEqual(len(pm_metrics), 2)
            self.assertIn("gpt-4-turbo", pm_metrics)
            self.assertIn("claude-3.5-sonnet", pm_metrics)
            
            # Verify BA metrics
            self.assertEqual(len(ba_metrics), 1)
            self.assertIn("gpt-4-turbo", ba_metrics)
            # Note: get_performance_by_agent_type returns all metrics for models used by that agent,
            # not filtered by agent type. So gpt-4-turbo will show 2 total requests (1 PM + 1 BA)
            self.assertEqual(ba_metrics["gpt-4-turbo"].total_requests, 2)
            # Success rate will be 50% (1 success from PM, 1 failure from BA)
            self.assertAlmostEqual(ba_metrics["gpt-4-turbo"].success_rate, 0.5, places=2)
        
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            loop.run_until_complete(test())
        finally:
            loop.close()


if __name__ == '__main__':
    unittest.main()
