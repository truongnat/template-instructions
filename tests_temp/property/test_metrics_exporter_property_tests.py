"""
Property-based tests for MetricsExporter class.

This module tests universal properties that should hold for all valid inputs
to the MetricsExporter using hypothesis for property-based testing.

Feature: api-model-management
"""

import unittest
import asyncio
import tempfile
import json
from pathlib import Path
from datetime import datetime, timedelta
import shutil

from hypothesis import given, settings, strategies as st

from agentic_sdlc.orchestration.api_model_management.metrics_exporter import MetricsExporter
from agentic_sdlc.orchestration.api_model_management.cost_tracker import CostTracker
from agentic_sdlc.orchestration.api_model_management.performance_monitor import PerformanceMonitor
from agentic_sdlc.orchestration.api_model_management.database import DatabaseManager


# Hypothesis strategies
model_ids = st.sampled_from(["gpt-4-turbo", "claude-3.5-sonnet", "gemini-pro", "llama-3-70b"])
agent_types = st.sampled_from(["PM", "BA", "SA", "Research", "Quality", "Implementation"])
providers = st.sampled_from(["openai", "anthropic", "google", "ollama"])


class TestMetricsExporterProperties(unittest.TestCase):
    """
    Property-based tests for MetricsExporter.
    
    Tests universal properties using hypothesis for comprehensive input coverage.
    """
    
    def setUp(self):
        """Set up test case with temporary database"""
        # Create unique temp directory for each test
        self.temp_dir = tempfile.mkdtemp()
        import time
        db_name = f"test_metrics_prop_{int(time.time() * 1000000)}.db"
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
            "gemini-pro": "google",
            "llama-3-70b": "ollama"
        }
    
    def tearDown(self):
        """Clean up test database"""
        if hasattr(self, 'temp_dir'):
            shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    @settings(max_examples=10, deadline=5000)
    @given(
        model_id=model_ids,
        agent_type=agent_types,
        input_tokens=st.integers(min_value=100, max_value=10000),
        output_tokens=st.integers(min_value=50, max_value=5000)
    )
    def test_property_65_metrics_export_format(
        self,
        model_id: str,
        agent_type: str,
        input_tokens: int,
        output_tokens: int
    ):
        """
        Feature: api-model-management
        Property 65: Metrics export format
        
        For any metrics query, the returned data should be in valid JSON format
        and include all requested metric types.
        
        **Validates: Requirements 17.1**
        """
        async def test():
            exporter = MetricsExporter(
                self.cost_tracker,
                self.performance_monitor,
                self.model_registry
            )
            
            # Record some data
            cost = (input_tokens / 1000 * 0.01) + (output_tokens / 1000 * 0.03)
            await self.cost_tracker.record_cost(
                model_id=model_id,
                agent_type=agent_type,
                input_tokens=input_tokens,
                output_tokens=output_tokens,
                cost=cost,
                task_id=f"test-{model_id}-{agent_type}"
            )
            
            # Export metrics
            json_output = await exporter.export_metrics()
            
            # Verify valid JSON
            parsed = json.loads(json_output)
            
            # Verify structure
            self.assertIsInstance(parsed, dict)
            self.assertIn("metadata", parsed)
            self.assertIn("cost", parsed)
            self.assertIn("performance", parsed)
            self.assertIn("derived", parsed)
            
            # Verify metadata structure
            self.assertIn("start_date", parsed["metadata"])
            self.assertIn("end_date", parsed["metadata"])
            self.assertIn("generated_at", parsed["metadata"])
        
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            loop.run_until_complete(test())
        finally:
            loop.close()
    
    @settings(max_examples=10, deadline=5000)
    @given(
        num_requests=st.integers(min_value=1, max_value=10),
        model_id=model_ids,
        agent_type=agent_types
    )
    def test_property_66_metrics_completeness(
        self,
        num_requests: int,
        model_id: str,
        agent_type: str
    ):
        """
        Feature: api-model-management
        Property 66: Metrics completeness
        
        For any metrics query, the response should include request counts,
        error rates, latency percentiles (p50, p95, p99), and cost totals.
        
        **Validates: Requirements 17.2**
        """
        async def test():
            exporter = MetricsExporter(
                self.cost_tracker,
                self.performance_monitor,
                self.model_registry
            )
            
            # Record multiple requests
            for i in range(num_requests):
                cost = 0.025
                await self.cost_tracker.record_cost(
                    model_id=model_id,
                    agent_type=agent_type,
                    input_tokens=1000,
                    output_tokens=500,
                    cost=cost,
                    task_id=f"test-{i}"
                )
                
                await self.performance_monitor.record_performance(
                    model_id=model_id,
                    agent_type=agent_type,
                    latency_ms=1500.0 + i * 100,
                    success=True,
                    quality_score=0.85,
                    task_id=f"test-{i}"
                )
            
            # Get metrics
            metrics = await exporter.get_metrics_dict(model_id=model_id)
            
            # Verify cost metrics completeness
            cost = metrics["cost"]
            self.assertIn("total_cost", cost)
            self.assertIn("total_requests", cost)
            self.assertIn("cost_by_model", cost)
            self.assertIn("cost_by_agent_type", cost)
            self.assertIn("cost_by_provider", cost)
            
            # Verify performance metrics completeness (if data exists)
            if metrics["performance"]["models"]:
                perf = metrics["performance"]["models"][model_id]
                self.assertIn("total_requests", perf)
                self.assertIn("success_rate", perf)
                self.assertIn("error_rate", perf)
                self.assertIn("latency", perf)
                
                # Verify latency percentiles
                latency = perf["latency"]
                self.assertIn("p50_ms", latency)
                self.assertIn("p95_ms", latency)
                self.assertIn("p99_ms", latency)
            
            # Verify derived metrics
            derived = metrics["derived"]
            self.assertIn("cost_per_request", derived)
            self.assertIn("cost_per_successful_request", derived)
        
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            loop.run_until_complete(test())
        finally:
            loop.close()
    
    @settings(max_examples=10, deadline=5000)
    @given(
        filter_model=model_ids,
        other_model=model_ids,
        filter_agent=agent_types,
        other_agent=agent_types
    )
    def test_property_67_metrics_filtering(
        self,
        filter_model: str,
        other_model: str,
        filter_agent: str,
        other_agent: str
    ):
        """
        Feature: api-model-management
        Property 67: Metrics filtering
        
        For any metrics query with filters (time range, model, provider, agent type),
        all returned metrics should match the filter criteria.
        
        **Validates: Requirements 17.3**
        """
        # Skip if models or agents are the same
        if filter_model == other_model or filter_agent == other_agent:
            return
        
        async def test():
            exporter = MetricsExporter(
                self.cost_tracker,
                self.performance_monitor,
                self.model_registry
            )
            
            # Record data for filter_model and filter_agent
            await self.cost_tracker.record_cost(
                model_id=filter_model,
                agent_type=filter_agent,
                input_tokens=1000,
                output_tokens=500,
                cost=0.025,
                task_id="test-filter"
            )
            
            # Record data for other_model and other_agent
            await self.cost_tracker.record_cost(
                model_id=other_model,
                agent_type=other_agent,
                input_tokens=2000,
                output_tokens=1000,
                cost=0.050,
                task_id="test-other"
            )
            
            # Get metrics filtered by model
            metrics_by_model = await exporter.get_metrics_dict(model_id=filter_model)
            
            # Verify only filter_model data is included
            cost_by_model = metrics_by_model["cost"]["cost_by_model"]
            self.assertIn(filter_model, cost_by_model)
            self.assertNotIn(other_model, cost_by_model)
            
            # Get metrics filtered by agent type
            metrics_by_agent = await exporter.get_metrics_dict(agent_type=filter_agent)
            
            # Verify only filter_agent data is included
            cost_by_agent = metrics_by_agent["cost"]["cost_by_agent_type"]
            self.assertIn(filter_agent, cost_by_agent)
            self.assertNotIn(other_agent, cost_by_agent)
        
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            loop.run_until_complete(test())
        finally:
            loop.close()
    
    @settings(max_examples=10, deadline=5000)
    @given(
        num_requests=st.integers(min_value=1, max_value=20),
        input_tokens=st.integers(min_value=100, max_value=5000),
        output_tokens=st.integers(min_value=50, max_value=2500)
    )
    def test_property_68_derived_metrics_calculation(
        self,
        num_requests: int,
        input_tokens: int,
        output_tokens: int
    ):
        """
        Feature: api-model-management
        Property 68: Derived metrics calculation
        
        For any metrics query, derived metrics (e.g., cost per successful request)
        should be correctly calculated from base metrics.
        
        **Validates: Requirements 17.4**
        """
        async def test():
            # Create fresh database for this hypothesis example
            import time
            temp_dir = tempfile.mkdtemp()
            db_name = f"test_metrics_prop_{int(time.time() * 1000000)}.db"
            db_path = Path(temp_dir) / db_name
            
            # Initialize database
            db_manager = DatabaseManager(db_path)
            await db_manager.initialize()
            
            # Create fresh components for this example
            cost_tracker = CostTracker(db_path, daily_budget=100.0)
            performance_monitor = PerformanceMonitor(db_path)
            
            exporter = MetricsExporter(
                cost_tracker,
                performance_monitor,
                self.model_registry
            )
            
            # Record multiple requests with known values
            total_cost = 0.0
            for i in range(num_requests):
                cost = (input_tokens / 1000 * 0.01) + (output_tokens / 1000 * 0.03)
                total_cost += cost
                
                await cost_tracker.record_cost(
                    model_id="gpt-4-turbo",
                    agent_type="PM",
                    input_tokens=input_tokens,
                    output_tokens=output_tokens,
                    cost=cost,
                    task_id=f"test-{i}"
                )
                
                # Also record performance data so actual success count is used
                await performance_monitor.record_performance(
                    model_id="gpt-4-turbo",
                    agent_type="PM",
                    latency_ms=1500.0,
                    success=True,
                    quality_score=0.85,
                    task_id=f"test-{i}"
                )
            
            # Get metrics
            metrics = await exporter.get_metrics_dict(model_id="gpt-4-turbo")
            
            # Verify derived metrics
            derived = metrics["derived"]
            
            # Cost per request should equal total_cost / num_requests
            expected_cost_per_request = total_cost / num_requests
            self.assertAlmostEqual(
                derived["cost_per_request"],
                expected_cost_per_request,
                places=6
            )
            
            # Cost per successful request should also equal total_cost / num_requests
            # since all requests were successful
            self.assertAlmostEqual(
                derived["cost_per_successful_request"],
                expected_cost_per_request,
                places=6
            )
            
            # Average tokens should match input values
            self.assertAlmostEqual(
                derived["average_input_tokens_per_request"],
                float(input_tokens),
                places=1
            )
            self.assertAlmostEqual(
                derived["average_output_tokens_per_request"],
                float(output_tokens),
                places=1
            )
            
            # Total tokens should be sum of input and output
            expected_total_tokens = input_tokens + output_tokens
            self.assertAlmostEqual(
                derived["average_total_tokens_per_request"],
                float(expected_total_tokens),
                places=1
            )
            
            # Cleanup
            shutil.rmtree(temp_dir, ignore_errors=True)
        
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            loop.run_until_complete(test())
        finally:
            loop.close()
    
    @settings(max_examples=5, deadline=5000)
    @given(
        model_id=model_ids,
        agent_type=agent_types
    )
    def test_property_69_real_time_metrics_updates(
        self,
        model_id: str,
        agent_type: str
    ):
        """
        Feature: api-model-management
        Property 69: Real-time metrics updates
        
        For any completed request, the metrics should be updated immediately
        and reflect in subsequent queries.
        
        **Validates: Requirements 17.5**
        """
        async def test():
            exporter = MetricsExporter(
                self.cost_tracker,
                self.performance_monitor,
                self.model_registry
            )
            
            # Get initial metrics
            initial_metrics = await exporter.get_metrics_dict()
            initial_requests = initial_metrics["cost"]["total_requests"]
            
            # Record a new request
            await self.cost_tracker.record_cost(
                model_id=model_id,
                agent_type=agent_type,
                input_tokens=1000,
                output_tokens=500,
                cost=0.025,
                task_id="test-realtime"
            )
            
            # Get updated metrics immediately
            updated_metrics = await exporter.get_metrics_dict()
            updated_requests = updated_metrics["cost"]["total_requests"]
            
            # Verify metrics were updated
            self.assertEqual(updated_requests, initial_requests + 1)
            
            # Verify the new request is reflected in cost
            self.assertGreater(
                updated_metrics["cost"]["total_cost"],
                initial_metrics["cost"]["total_cost"]
            )
        
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            loop.run_until_complete(test())
        finally:
            loop.close()


if __name__ == '__main__':
    unittest.main()
