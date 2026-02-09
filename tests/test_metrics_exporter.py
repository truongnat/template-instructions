"""
Unit tests for MetricsExporter class.

This module tests specific examples and edge cases for the MetricsExporter including
JSON formatting, metric filtering, and derived metric calculations.

Feature: api-model-management
"""

import unittest
import asyncio
import tempfile
import json
from pathlib import Path
from datetime import datetime, timedelta
import shutil

from agentic_sdlc.orchestration.api_model_management.metrics_exporter import MetricsExporter
from agentic_sdlc.orchestration.api_model_management.cost_tracker import CostTracker
from agentic_sdlc.orchestration.api_model_management.performance_monitor import PerformanceMonitor
from agentic_sdlc.orchestration.api_model_management.database import DatabaseManager


class TestMetricsExporterUnit(unittest.TestCase):
    """
    Unit tests for MetricsExporter.
    
    Tests specific examples and edge cases:
    - JSON formatting
    - Metric filtering
    - Derived metric calculations
    """
    
    def setUp(self):
        """Set up test case with temporary database"""
        # Create unique temp directory for each test
        self.temp_dir = tempfile.mkdtemp()
        import time
        db_name = f"test_metrics_{int(time.time() * 1000000)}.db"
        self.db_path = Path(self.temp_dir) / db_name
        
        # Initialize database synchronously
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        self.db_manager = DatabaseManager(self.db_path)
        loop.run_until_complete(self.db_manager.initialize())
        loop.close()
        
        # Create components
        self.cost_tracker = CostTracker(self.db_path, daily_budget=100.0)
        self.performance_monitor = PerformanceMonitor(self.db_path)
        
        # Model registry for provider mapping
        self.model_registry = {
            "gpt-4-turbo": "openai",
            "claude-3.5-sonnet": "anthropic",
            "gemini-pro": "google"
        }
    
    def tearDown(self):
        """Clean up test database"""
        if hasattr(self, 'temp_dir'):
            shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_json_formatting_valid(self):
        """
        Test that exported metrics are valid JSON.
        
        **Validates: Requirements 17.1**
        """
        async def test():
            exporter = MetricsExporter(
                self.cost_tracker,
                self.performance_monitor,
                self.model_registry
            )
            
            # Export metrics
            json_output = await exporter.export_metrics()
            
            # Verify valid JSON
            parsed = json.loads(json_output)
            self.assertIsInstance(parsed, dict)
            self.assertIn("metadata", parsed)
            self.assertIn("cost", parsed)
            self.assertIn("performance", parsed)
            self.assertIn("derived", parsed)
        
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            loop.run_until_complete(test())
        finally:
            loop.close()
    
    def test_metrics_completeness(self):
        """
        Test that all required metric types are included.
        
        **Validates: Requirements 17.2**
        """
        async def test():
            exporter = MetricsExporter(
                self.cost_tracker,
                self.performance_monitor,
                self.model_registry
            )
            
            # Record some data
            await self.cost_tracker.record_cost(
                model_id="gpt-4-turbo",
                agent_type="PM",
                input_tokens=1000,
                output_tokens=500,
                cost=0.025,
                task_id="test-1"
            )
            
            await self.performance_monitor.record_performance(
                model_id="gpt-4-turbo",
                agent_type="PM",
                latency_ms=1500.0,
                success=True,
                quality_score=0.85,
                task_id="test-1"
            )
            
            # Get metrics
            metrics = await exporter.get_metrics_dict()
            
            # Verify completeness
            cost = metrics["cost"]
            self.assertIn("total_cost", cost)
            self.assertIn("total_requests", cost)
            self.assertIn("cost_by_model", cost)
            self.assertIn("cost_by_agent_type", cost)
            self.assertIn("cost_by_provider", cost)
            self.assertIn("budget_status", cost)
            
            # Verify derived metrics
            derived = metrics["derived"]
            self.assertIn("cost_per_request", derived)
            self.assertIn("cost_per_successful_request", derived)
            self.assertIn("average_input_tokens_per_request", derived)
            self.assertIn("average_output_tokens_per_request", derived)
        
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            loop.run_until_complete(test())
        finally:
            loop.close()
    
    def test_model_id_filtering(self):
        """
        Test filtering metrics by model ID.
        
        **Validates: Requirements 17.3**
        """
        async def test():
            exporter = MetricsExporter(
                self.cost_tracker,
                self.performance_monitor,
                self.model_registry
            )
            
            # Record data for multiple models
            await self.cost_tracker.record_cost(
                model_id="gpt-4-turbo",
                agent_type="PM",
                input_tokens=1000,
                output_tokens=500,
                cost=0.025,
                task_id="test-1"
            )
            
            await self.cost_tracker.record_cost(
                model_id="claude-3.5-sonnet",
                agent_type="BA",
                input_tokens=2000,
                output_tokens=1000,
                cost=0.045,
                task_id="test-2"
            )
            
            # Get metrics filtered by model
            metrics = await exporter.get_metrics_dict(model_id="gpt-4-turbo")
            
            # Verify only gpt-4-turbo data is included
            cost_by_model = metrics["cost"]["cost_by_model"]
            self.assertIn("gpt-4-turbo", cost_by_model)
            self.assertNotIn("claude-3.5-sonnet", cost_by_model)
        
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            loop.run_until_complete(test())
        finally:
            loop.close()
    
    def test_agent_type_filtering(self):
        """
        Test filtering metrics by agent type.
        
        **Validates: Requirements 17.3**
        """
        async def test():
            exporter = MetricsExporter(
                self.cost_tracker,
                self.performance_monitor,
                self.model_registry
            )
            
            # Record data for multiple agent types
            await self.cost_tracker.record_cost(
                model_id="gpt-4-turbo",
                agent_type="PM",
                input_tokens=1000,
                output_tokens=500,
                cost=0.025,
                task_id="test-1"
            )
            
            await self.cost_tracker.record_cost(
                model_id="gpt-4-turbo",
                agent_type="BA",
                input_tokens=2000,
                output_tokens=1000,
                cost=0.045,
                task_id="test-2"
            )
            
            # Get metrics filtered by agent type
            metrics = await exporter.get_metrics_dict(agent_type="PM")
            
            # Verify only PM data is included
            cost_by_agent = metrics["cost"]["cost_by_agent_type"]
            self.assertIn("PM", cost_by_agent)
            self.assertNotIn("BA", cost_by_agent)
        
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            loop.run_until_complete(test())
        finally:
            loop.close()
    
    def test_derived_metric_cost_per_request(self):
        """
        Test derived metric: cost per request calculation.
        
        **Validates: Requirements 17.4**
        """
        async def test():
            exporter = MetricsExporter(
                self.cost_tracker,
                self.performance_monitor,
                self.model_registry
            )
            
            # Record 3 requests with known costs
            for i in range(3):
                await self.cost_tracker.record_cost(
                    model_id="gpt-4-turbo",
                    agent_type="PM",
                    input_tokens=1000,
                    output_tokens=500,
                    cost=0.025,
                    task_id=f"test-{i}"
                )
            
            # Get metrics
            metrics = await exporter.get_metrics_dict()
            
            # Verify derived metric
            derived = metrics["derived"]
            expected_cost_per_request = 0.075 / 3  # total cost / total requests
            self.assertAlmostEqual(
                derived["cost_per_request"],
                expected_cost_per_request,
                places=6
            )
        
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            loop.run_until_complete(test())
        finally:
            loop.close()
    
    def test_derived_metric_average_tokens(self):
        """
        Test derived metric: average tokens per request.
        
        **Validates: Requirements 17.4**
        """
        async def test():
            exporter = MetricsExporter(
                self.cost_tracker,
                self.performance_monitor,
                self.model_registry
            )
            
            # Record requests with different token counts
            await self.cost_tracker.record_cost(
                model_id="gpt-4-turbo",
                agent_type="PM",
                input_tokens=1000,
                output_tokens=500,
                cost=0.025,
                task_id="test-1"
            )
            
            await self.cost_tracker.record_cost(
                model_id="gpt-4-turbo",
                agent_type="PM",
                input_tokens=2000,
                output_tokens=1000,
                cost=0.050,
                task_id="test-2"
            )
            
            # Get metrics
            metrics = await exporter.get_metrics_dict()
            
            # Verify derived metrics
            derived = metrics["derived"]
            self.assertAlmostEqual(
                derived["average_input_tokens_per_request"],
                1500.0,  # (1000 + 2000) / 2
                places=1
            )
            self.assertAlmostEqual(
                derived["average_output_tokens_per_request"],
                750.0,  # (500 + 1000) / 2
                places=1
            )
            self.assertAlmostEqual(
                derived["average_total_tokens_per_request"],
                2250.0,  # (1500 + 1500) / 2
                places=1
            )
        
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            loop.run_until_complete(test())
        finally:
            loop.close()
    
    def test_real_time_metrics_recent_window(self):
        """
        Test real-time metrics for recent time window.
        
        **Validates: Requirements 17.5**
        """
        async def test():
            exporter = MetricsExporter(
                self.cost_tracker,
                self.performance_monitor,
                self.model_registry
            )
            
            # Record recent data
            await self.cost_tracker.record_cost(
                model_id="gpt-4-turbo",
                agent_type="PM",
                input_tokens=1000,
                output_tokens=500,
                cost=0.025,
                task_id="test-1"
            )
            
            # Get real-time metrics (last 5 minutes)
            metrics = await exporter.get_real_time_metrics(window_minutes=5)
            
            # Verify metadata indicates real-time
            self.assertTrue(metrics["metadata"]["real_time"])
            self.assertEqual(metrics["metadata"]["window_minutes"], 5)
            
            # Verify recent data is included
            self.assertGreater(metrics["cost"]["total_requests"], 0)
        
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            loop.run_until_complete(test())
        finally:
            loop.close()
    
    def test_metrics_summary_format(self):
        """
        Test metrics summary format and content.
        
        **Validates: Requirements 17.1, 17.2**
        """
        async def test():
            exporter = MetricsExporter(
                self.cost_tracker,
                self.performance_monitor,
                self.model_registry
            )
            
            # Record some data
            await self.cost_tracker.record_cost(
                model_id="gpt-4-turbo",
                agent_type="PM",
                input_tokens=1000,
                output_tokens=500,
                cost=0.025,
                task_id="test-1"
            )
            
            # Get summary
            summary = await exporter.get_metrics_summary()
            
            # Verify summary structure
            self.assertIn("period", summary)
            self.assertIn("generated_at", summary)
            self.assertIn("total_requests", summary)
            self.assertIn("total_cost", summary)
            self.assertIn("average_cost_per_request", summary)
            self.assertIn("budget_utilization_percent", summary)
            self.assertIn("top_models_by_cost", summary)
            self.assertIn("top_agent_types_by_cost", summary)
        
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            loop.run_until_complete(test())
        finally:
            loop.close()
    
    def test_empty_metrics_handling(self):
        """
        Test handling of empty metrics (no data recorded).
        
        Edge case: Should return valid structure with zero values.
        
        **Validates: Requirements 17.1**
        """
        async def test():
            exporter = MetricsExporter(
                self.cost_tracker,
                self.performance_monitor,
                self.model_registry
            )
            
            # Get metrics without recording any data
            metrics = await exporter.get_metrics_dict()
            
            # Verify structure exists with zero values
            self.assertEqual(metrics["cost"]["total_cost"], 0.0)
            self.assertEqual(metrics["cost"]["total_requests"], 0)
            self.assertEqual(metrics["derived"]["cost_per_request"], 0.0)
        
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            loop.run_until_complete(test())
        finally:
            loop.close()


if __name__ == '__main__':
    unittest.main()
