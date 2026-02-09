"""
Property-based tests for PerformanceMonitor class.

This module tests the correctness properties of the PerformanceMonitor including
performance metric tracking, metric updates, rolling average calculation,
performance degradation alerting, and data persistence.

Feature: api-model-management
"""

import unittest
import asyncio
import tempfile
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, Any, List

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
        def floats(self, **kwargs): return lambda: 1.0
        def booleans(self): return lambda: True
        def lists(self, *args, **kwargs): return lambda: []
        def dictionaries(self, *args, **kwargs): return lambda: {}
        def one_of(self, *args): return lambda: args[0]() if args else lambda: None
        def just(self, value): return lambda: value
        def builds(self, cls, **kwargs): return lambda: cls(**kwargs)
        def sampled_from(self, seq): return lambda: seq[0] if seq else None
    
    st = MockStrategies()
    
    def settings(**kwargs):
        def decorator(func):
            return func
        return decorator

from agentic_sdlc.orchestration.api_model_management.performance_monitor import PerformanceMonitor
from agentic_sdlc.orchestration.api_model_management.database import DatabaseManager
from agentic_sdlc.orchestration.api_model_management.models import PerformanceMetrics, PerformanceDegradation


# Hypothesis strategies for generating test data

def performance_record_strategy():
    """Strategy for generating valid performance records"""
    return st.builds(
        dict,
        model_id=st.sampled_from([
            "gpt-4-turbo", "gpt-3.5-turbo", "claude-3.5-sonnet", 
            "claude-3-opus", "gemini-pro", "ollama-llama2"
        ]),
        agent_type=st.sampled_from([
            "PM", "BA", "SA", "Research", "Quality", "Implementation"
        ]),
        latency_ms=st.floats(min_value=100.0, max_value=10000.0, allow_nan=False, allow_infinity=False),
        success=st.booleans(),
        quality_score=st.floats(min_value=0.0, max_value=1.0, allow_nan=False, allow_infinity=False),
        task_id=st.text(
            min_size=5, 
            max_size=20, 
            alphabet=st.characters(whitelist_categories=('Lu', 'Ll', 'Nd'), whitelist_characters='-_')
        )
    )


@unittest.skipIf(not HYPOTHESIS_AVAILABLE, "Hypothesis not available")
class TestPerformanceMonitorProperties(unittest.TestCase):
    """
    Property-based tests for PerformanceMonitor.
    
    Tests Properties 46-50 from the design document:
    - Property 46: Performance metric tracking
    - Property 47: Performance metric updates
    - Property 48: Rolling average calculation
    - Property 49: Performance degradation alerting
    - Property 50: Performance data persistence
    """
    
    def setUp(self):
        """Set up test case with temporary database"""
        if not HYPOTHESIS_AVAILABLE:
            self.skipTest("Hypothesis not available")
        
        # Create unique temp directory for each test
        self.temp_dir = tempfile.mkdtemp()
        # Use a unique database file name with timestamp to avoid conflicts
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
        import shutil
        if hasattr(self, 'temp_dir'):
            shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    @settings(max_examples=50, deadline=None)
    @given(record=performance_record_strategy())
    def test_property_46_performance_metric_tracking(self, record: Dict[str, Any]):
        """
        Feature: api-model-management
        Property 46: Performance metric tracking
        
        For any completed request, latency, success status, and quality score 
        should be recorded in the Performance_Monitor
        
        **Validates: Requirements 11.1**
        """
        async def test_tracking():
            # Create fresh database for this example
            import time
            temp_dir = tempfile.mkdtemp()
            db_path = Path(temp_dir) / f"test_{int(time.time() * 1000000)}.db"
            db_manager = DatabaseManager(db_path)
            await db_manager.initialize()
            
            try:
                monitor = PerformanceMonitor(db_path)
                
                # Record performance
                await monitor.record_performance(
                    model_id=record['model_id'],
                    agent_type=record['agent_type'],
                    latency_ms=record['latency_ms'],
                    success=record['success'],
                    quality_score=record['quality_score'],
                    task_id=record['task_id']
                )
                
                # Retrieve metrics
                metrics = await monitor.get_model_performance(record['model_id'], window_hours=1)
                
                # Verify metrics were recorded
                self.assertIsInstance(metrics, PerformanceMetrics)
                self.assertEqual(metrics.model_id, record['model_id'])
                self.assertEqual(metrics.total_requests, 1)
                
                # Verify latency was recorded
                self.assertAlmostEqual(metrics.average_latency_ms, record['latency_ms'], places=2)
                
                # Verify success status was recorded
                if record['success']:
                    self.assertEqual(metrics.successful_requests, 1)
                    self.assertEqual(metrics.failed_requests, 0)
                    self.assertAlmostEqual(metrics.success_rate, 1.0, places=2)
                else:
                    self.assertEqual(metrics.successful_requests, 0)
                    self.assertEqual(metrics.failed_requests, 1)
                    self.assertAlmostEqual(metrics.success_rate, 0.0, places=2)
                
                # Verify quality score was recorded
                self.assertAlmostEqual(metrics.average_quality_score, record['quality_score'], places=2)
            finally:
                # Clean up
                import shutil
                shutil.rmtree(temp_dir, ignore_errors=True)
        
        # Run async test
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            loop.run_until_complete(test_tracking())
        finally:
            loop.close()

    @settings(max_examples=50, deadline=None)
    @given(records=st.lists(performance_record_strategy(), min_size=2, max_size=10))
    def test_property_47_performance_metric_updates(self, records: List[Dict[str, Any]]):
        """
        Feature: api-model-management
        Property 47: Performance metric updates
        
        For any completed request, the model's performance metrics 
        (average latency, success rate, average quality) should be updated 
        to reflect the new data
        
        **Validates: Requirements 11.2**
        """
        # Use the same model for all records to test metric updates
        model_id = records[0]['model_id']
        for record in records:
            record['model_id'] = model_id
        
        async def test_updates():
            # Create fresh database for this example
            import time
            temp_dir = tempfile.mkdtemp()
            db_path = Path(temp_dir) / f"test_{int(time.time() * 1000000)}.db"
            db_manager = DatabaseManager(db_path)
            await db_manager.initialize()
            
            try:
                monitor = PerformanceMonitor(db_path)
                
                # Record all performance data
                for record in records:
                    await monitor.record_performance(
                        model_id=record['model_id'],
                        agent_type=record['agent_type'],
                        latency_ms=record['latency_ms'],
                        success=record['success'],
                        quality_score=record['quality_score'],
                        task_id=record['task_id']
                    )
                
                # Retrieve updated metrics
                metrics = await monitor.get_model_performance(model_id, window_hours=1)
                
                # Calculate expected metrics
                total_requests = len(records)
                successful_requests = sum(1 for r in records if r['success'])
                expected_success_rate = successful_requests / total_requests
                expected_avg_latency = sum(r['latency_ms'] for r in records) / total_requests
                expected_avg_quality = sum(r['quality_score'] for r in records) / total_requests
                
                # Verify metrics were updated correctly
                self.assertEqual(metrics.total_requests, total_requests)
                self.assertEqual(metrics.successful_requests, successful_requests)
                self.assertEqual(metrics.failed_requests, total_requests - successful_requests)
                self.assertAlmostEqual(metrics.success_rate, expected_success_rate, places=2)
                self.assertAlmostEqual(metrics.average_latency_ms, expected_avg_latency, places=2)
                self.assertAlmostEqual(metrics.average_quality_score, expected_avg_quality, places=2)
            finally:
                # Clean up
                import shutil
                shutil.rmtree(temp_dir, ignore_errors=True)
        
        # Run async test
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            loop.run_until_complete(test_updates())
        finally:
            loop.close()
    
    @settings(max_examples=50, deadline=None)
    @given(
        recent_records=st.lists(performance_record_strategy(), min_size=2, max_size=5),
        old_records=st.lists(performance_record_strategy(), min_size=1, max_size=3),
        window_hours=st.integers(min_value=1, max_value=24)
    )
    def test_property_48_rolling_average_calculation(
        self, 
        recent_records: List[Dict[str, Any]], 
        old_records: List[Dict[str, Any]],
        window_hours: int
    ):
        """
        Feature: api-model-management
        Property 48: Rolling average calculation
        
        For any time window (1 hour, 24 hours, 7 days), the calculated rolling 
        average should include only requests within that window
        
        **Validates: Requirements 11.3**
        """
        # Use the same model for all records
        model_id = recent_records[0]['model_id']
        for record in recent_records + old_records:
            record['model_id'] = model_id
        
        async def test_rolling_average():
            # Create fresh database for this example
            import time
            temp_dir = tempfile.mkdtemp()
            db_path = Path(temp_dir) / f"test_{int(time.time() * 1000000)}.db"
            db_manager = DatabaseManager(db_path)
            await db_manager.initialize()
            
            try:
                monitor = PerformanceMonitor(db_path)
                
                # Record recent data (within window)
                for record in recent_records:
                    await monitor.record_performance(
                        model_id=record['model_id'],
                        agent_type=record['agent_type'],
                        latency_ms=record['latency_ms'],
                        success=record['success'],
                        quality_score=record['quality_score'],
                        task_id=record['task_id']
                    )
                
                # Record old data (outside window) by directly inserting with old timestamp
                cutoff_time = datetime.now() - timedelta(hours=window_hours + 1)
                
                import aiosqlite
                async with aiosqlite.connect(monitor.db_path) as db:
                    for record in old_records:
                        await db.execute("""
                            INSERT INTO performance_records 
                            (timestamp, model_id, agent_type, task_id, latency_ms, success, quality_score)
                            VALUES (?, ?, ?, ?, ?, ?, ?)
                        """, (
                            cutoff_time,
                            record['model_id'],
                            record['agent_type'],
                            record['task_id'],
                            record['latency_ms'],
                            record['success'],
                            record['quality_score']
                        ))
                    await db.commit()
                
                # Retrieve metrics for the specified window
                metrics = await monitor.get_model_performance(model_id, window_hours=window_hours)
                
                # Calculate expected metrics (only from recent records)
                expected_total = len(recent_records)
                expected_successful = sum(1 for r in recent_records if r['success'])
                expected_success_rate = expected_successful / expected_total if expected_total > 0 else 0.0
                expected_avg_latency = (
                    sum(r['latency_ms'] for r in recent_records) / expected_total 
                    if expected_total > 0 else 0.0
                )
                
                # Verify only recent records are included in rolling average
                self.assertEqual(metrics.total_requests, expected_total,
                    msg=f"Expected {expected_total} requests in window, got {metrics.total_requests}")
                self.assertEqual(metrics.successful_requests, expected_successful)
                self.assertAlmostEqual(metrics.success_rate, expected_success_rate, places=2)
                self.assertAlmostEqual(metrics.average_latency_ms, expected_avg_latency, places=2)
            finally:
                # Clean up
                import shutil
                shutil.rmtree(temp_dir, ignore_errors=True)
        
        # Run async test
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            loop.run_until_complete(test_rolling_average())
        finally:
            loop.close()
    
    @settings(max_examples=50, deadline=None)
    @given(
        success_rate=st.floats(min_value=0.0, max_value=1.0, allow_nan=False, allow_infinity=False),
        threshold=st.floats(min_value=0.5, max_value=0.95, allow_nan=False, allow_infinity=False)
    )
    def test_property_49_performance_degradation_alerting(
        self, 
        success_rate: float, 
        threshold: float
    ):
        """
        Feature: api-model-management
        Property 49: Performance degradation alerting
        
        For any model with a success rate below 80% over the monitoring window, 
        a performance alert should be triggered
        
        **Validates: Requirements 11.4**
        """
        # Generate records with the specified success rate
        total_records = 10
        successful_records = round(total_records * success_rate)
        # Recalculate actual success rate based on integer counts
        actual_success_rate = successful_records / total_records
        
        async def test_degradation_alert():
            # Create fresh database for this example
            import time
            temp_dir = tempfile.mkdtemp()
            db_path = Path(temp_dir) / f"test_{int(time.time() * 1000000)}.db"
            db_manager = DatabaseManager(db_path)
            await db_manager.initialize()
            
            try:
                monitor = PerformanceMonitor(db_path)
                model_id = "test-model"
                
                # Record successful requests
                for i in range(successful_records):
                    await monitor.record_performance(
                        model_id=model_id,
                        agent_type="PM",
                        latency_ms=1000.0,
                        success=True,
                        quality_score=0.9,
                        task_id=f"task-success-{i}"
                    )
                
                # Record failed requests
                for i in range(total_records - successful_records):
                    await monitor.record_performance(
                        model_id=model_id,
                        agent_type="PM",
                        latency_ms=1000.0,
                        success=False,
                        quality_score=0.5,
                        task_id=f"task-fail-{i}"
                    )
                
                # Check for degradation
                degradation = await monitor.detect_degradation(model_id, threshold=threshold)
                
                # Verify alert triggering
                if actual_success_rate < threshold:
                    # Success rate below threshold - should trigger alert
                    self.assertIsNotNone(degradation,
                        f"Expected alert when success_rate ({actual_success_rate:.2%}) < threshold ({threshold:.2%})")
                    self.assertIsInstance(degradation, PerformanceDegradation)
                    self.assertEqual(degradation.model_id, model_id)
                    self.assertEqual(degradation.metric, "success_rate")
                    self.assertAlmostEqual(degradation.current_value, actual_success_rate, places=2)
                    self.assertEqual(degradation.threshold, threshold)
                else:
                    # Success rate at or above threshold - no alert
                    self.assertIsNone(degradation,
                        f"No alert expected when success_rate ({actual_success_rate:.2%}) >= threshold ({threshold:.2%})")
            finally:
                # Clean up
                import shutil
                shutil.rmtree(temp_dir, ignore_errors=True)
        
        # Run async test
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            loop.run_until_complete(test_degradation_alert())
        finally:
            loop.close()
    
    @settings(max_examples=50, deadline=None)
    @given(record=performance_record_strategy())
    def test_property_50_performance_data_persistence(self, record: Dict[str, Any]):
        """
        Feature: api-model-management
        Property 50: Performance data persistence
        
        For any performance record, it should be persisted to SQLite and be 
        retrievable with all fields intact
        
        **Validates: Requirements 11.5**
        """
        async def test_persistence():
            # Create fresh database for this example
            import time
            temp_dir = tempfile.mkdtemp()
            db_path = Path(temp_dir) / f"test_{int(time.time() * 1000000)}.db"
            db_manager = DatabaseManager(db_path)
            await db_manager.initialize()
            
            try:
                monitor = PerformanceMonitor(db_path)
                
                # Record performance
                await monitor.record_performance(
                    model_id=record['model_id'],
                    agent_type=record['agent_type'],
                    latency_ms=record['latency_ms'],
                    success=record['success'],
                    quality_score=record['quality_score'],
                    task_id=record['task_id']
                )
                
                # Retrieve metrics to verify persistence
                metrics = await monitor.get_model_performance(record['model_id'], window_hours=1)
                
                # Verify all fields are persisted
                self.assertIsInstance(metrics, PerformanceMetrics)
                self.assertEqual(metrics.model_id, record['model_id'])
                self.assertEqual(metrics.total_requests, 1)
                
                # Verify latency persisted
                self.assertAlmostEqual(metrics.average_latency_ms, record['latency_ms'], places=2)
                self.assertAlmostEqual(metrics.p50_latency_ms, record['latency_ms'], places=2)
                self.assertAlmostEqual(metrics.p95_latency_ms, record['latency_ms'], places=2)
                self.assertAlmostEqual(metrics.p99_latency_ms, record['latency_ms'], places=2)
                
                # Verify success status persisted
                if record['success']:
                    self.assertEqual(metrics.successful_requests, 1)
                    self.assertEqual(metrics.failed_requests, 0)
                    self.assertAlmostEqual(metrics.success_rate, 1.0, places=2)
                else:
                    self.assertEqual(metrics.successful_requests, 0)
                    self.assertEqual(metrics.failed_requests, 1)
                    self.assertAlmostEqual(metrics.success_rate, 0.0, places=2)
                
                # Verify quality score persisted
                self.assertAlmostEqual(metrics.average_quality_score, record['quality_score'], places=2)
                
                # Verify data can be retrieved by agent type
                metrics_by_agent = await monitor.get_performance_by_agent_type(
                    record['agent_type'], 
                    window_hours=1
                )
                self.assertIn(record['model_id'], metrics_by_agent)
                agent_metrics = metrics_by_agent[record['model_id']]
                self.assertEqual(agent_metrics.total_requests, 1)
            finally:
                # Clean up
                import shutil
                shutil.rmtree(temp_dir, ignore_errors=True)
        
        # Run async test
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            loop.run_until_complete(test_persistence())
        finally:
            loop.close()


if __name__ == '__main__':
    # Configure test settings
    if HYPOTHESIS_AVAILABLE:
        settings.register_profile("default", max_examples=50, deadline=None)
        settings.load_profile("default")
    
    unittest.main()
