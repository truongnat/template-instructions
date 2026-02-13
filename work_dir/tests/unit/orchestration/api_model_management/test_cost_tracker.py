"""
Unit tests for CostTracker class.

This module tests specific examples and edge cases for the CostTracker including
budget threshold detection, cost aggregation edge cases, and query filtering.

Feature: api-model-management
"""

import unittest
import asyncio
import tempfile
from pathlib import Path
from datetime import datetime, timedelta
import shutil

from agentic_sdlc.orchestration.api_model_management.cost_tracker import CostTracker
from agentic_sdlc.orchestration.api_model_management.database import DatabaseManager
from agentic_sdlc.orchestration.api_model_management.models import BudgetStatus


class TestCostTrackerUnit(unittest.TestCase):
    """
    Unit tests for CostTracker.
    
    Tests specific examples and edge cases:
    - Budget threshold detection
    - Cost aggregation edge cases
    - Query filtering
    """
    
    def setUp(self):
        """Set up test case with temporary database"""
        # Create unique temp directory for each test
        self.temp_dir = tempfile.mkdtemp()
        import time
        db_name = f"test_cost_tracker_{int(time.time() * 1000000)}.db"
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
    
    def test_budget_threshold_exactly_at_limit(self):
        """
        Test budget threshold detection when cost exactly equals budget.
        
        Edge case: Cost = Budget should not trigger over-budget alert.
        
        **Validates: Requirements 10.3**
        """
        async def test():
            tracker = CostTracker(self.db_path, daily_budget=50.0)
            
            # Record cost exactly at budget
            await tracker.record_cost(
                model_id="gpt-4-turbo",
                agent_type="PM",
                input_tokens=1000,
                output_tokens=1000,
                cost=50.0,
                task_id="test-task-1"
            )
            
            # Check budget status
            budget_status = await tracker.check_budget()
            
            # Verify: exactly at budget should not be over budget
            self.assertEqual(budget_status.daily_budget, 50.0)
            self.assertEqual(budget_status.current_spend, 50.0)
            self.assertEqual(budget_status.utilization_percent, 100.0)
            self.assertFalse(budget_status.is_over_budget)
            self.assertEqual(budget_status.remaining_budget, 0.0)
        
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            loop.run_until_complete(test())
        finally:
            loop.close()
    
    def test_budget_threshold_just_over_limit(self):
        """
        Test budget threshold detection when cost slightly exceeds budget.
        
        Edge case: Cost > Budget by small amount should trigger alert.
        
        **Validates: Requirements 10.3**
        """
        async def test():
            tracker = CostTracker(self.db_path, daily_budget=50.0)
            
            # Record cost slightly over budget
            await tracker.record_cost(
                model_id="gpt-4-turbo",
                agent_type="PM",
                input_tokens=1000,
                output_tokens=1000,
                cost=50.01,
                task_id="test-task-1"
            )
            
            # Check budget status
            budget_status = await tracker.check_budget()
            
            # Verify: over budget should trigger alert
            self.assertEqual(budget_status.daily_budget, 50.0)
            self.assertAlmostEqual(budget_status.current_spend, 50.01, places=2)
            self.assertGreater(budget_status.utilization_percent, 100.0)
            self.assertTrue(budget_status.is_over_budget)
            self.assertEqual(budget_status.remaining_budget, 0.0)
        
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            loop.run_until_complete(test())
        finally:
            loop.close()
    
    def test_budget_threshold_zero_budget(self):
        """
        Test budget threshold detection with zero budget.
        
        Edge case: Zero budget should handle division by zero gracefully.
        
        **Validates: Requirements 10.3**
        """
        async def test():
            tracker = CostTracker(self.db_path, daily_budget=0.0)
            
            # Record any cost
            await tracker.record_cost(
                model_id="gpt-4-turbo",
                agent_type="PM",
                input_tokens=100,
                output_tokens=100,
                cost=1.0,
                task_id="test-task-1"
            )
            
            # Check budget status
            budget_status = await tracker.check_budget()
            
            # Verify: should handle zero budget without error
            self.assertEqual(budget_status.daily_budget, 0.0)
            self.assertEqual(budget_status.current_spend, 1.0)
            self.assertEqual(budget_status.utilization_percent, 0.0)  # Should be 0, not infinity
            self.assertTrue(budget_status.is_over_budget)
            self.assertEqual(budget_status.remaining_budget, 0.0)
        
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            loop.run_until_complete(test())
        finally:
            loop.close()
    
    def test_budget_threshold_multiple_requests(self):
        """
        Test budget threshold detection with multiple requests accumulating cost.
        
        Edge case: Multiple small requests should accumulate to trigger alert.
        
        **Validates: Requirements 10.3**
        """
        async def test():
            tracker = CostTracker(self.db_path, daily_budget=10.0)
            
            # Record multiple small costs that accumulate
            for i in range(5):
                await tracker.record_cost(
                    model_id="gpt-3.5-turbo",
                    agent_type="Implementation",
                    input_tokens=500,
                    output_tokens=500,
                    cost=2.5,
                    task_id=f"test-task-{i}"
                )
            
            # Check budget status
            budget_status = await tracker.check_budget()
            
            # Verify: accumulated cost should exceed budget
            self.assertEqual(budget_status.daily_budget, 10.0)
            self.assertAlmostEqual(budget_status.current_spend, 12.5, places=2)
            self.assertAlmostEqual(budget_status.utilization_percent, 125.0, places=1)
            self.assertTrue(budget_status.is_over_budget)
            self.assertEqual(budget_status.remaining_budget, 0.0)
        
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            loop.run_until_complete(test())
        finally:
            loop.close()
    
    def test_cost_aggregation_empty_results(self):
        """
        Test cost aggregation when no records match the query.
        
        Edge case: Empty result set should return empty dictionary.
        
        **Validates: Requirements 10.5**
        """
        async def test():
            tracker = CostTracker(self.db_path, daily_budget=100.0)
            
            # Query without any records
            start_date = datetime.now() - timedelta(hours=1)
            end_date = datetime.now() + timedelta(hours=1)
            
            cost_by_model = await tracker.get_cost_by_model(start_date, end_date)
            cost_by_agent = await tracker.get_cost_by_agent_type(start_date, end_date)
            
            # Verify: empty results
            self.assertEqual(len(cost_by_model), 0)
            self.assertEqual(len(cost_by_agent), 0)
        
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            loop.run_until_complete(test())
        finally:
            loop.close()
    
    def test_cost_aggregation_single_model_multiple_requests(self):
        """
        Test cost aggregation for single model with multiple requests.
        
        Edge case: Multiple requests to same model should aggregate correctly.
        
        **Validates: Requirements 10.5**
        """
        async def test():
            tracker = CostTracker(self.db_path, daily_budget=100.0)
            
            # Record multiple costs for same model
            costs = [1.5, 2.3, 0.8, 3.2]
            for i, cost in enumerate(costs):
                await tracker.record_cost(
                    model_id="gpt-4-turbo",
                    agent_type="PM",
                    input_tokens=1000,
                    output_tokens=1000,
                    cost=cost,
                    task_id=f"test-task-{i}"
                )
            
            # Query costs
            start_date = datetime.now() - timedelta(hours=1)
            end_date = datetime.now() + timedelta(hours=1)
            cost_by_model = await tracker.get_cost_by_model(start_date, end_date)
            
            # Verify: aggregated cost
            expected_total = sum(costs)
            self.assertEqual(len(cost_by_model), 1)
            self.assertIn("gpt-4-turbo", cost_by_model)
            self.assertAlmostEqual(cost_by_model["gpt-4-turbo"], expected_total, places=6)
        
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            loop.run_until_complete(test())
        finally:
            loop.close()
    
    def test_cost_aggregation_multiple_models(self):
        """
        Test cost aggregation across multiple models.
        
        Edge case: Different models should be aggregated separately.
        
        **Validates: Requirements 10.5**
        """
        async def test():
            tracker = CostTracker(self.db_path, daily_budget=100.0)
            
            # Record costs for different models
            model_costs = {
                "gpt-4-turbo": [1.5, 2.0],
                "gpt-3.5-turbo": [0.3, 0.5, 0.2],
                "claude-3.5-sonnet": [2.5]
            }
            
            for model_id, costs in model_costs.items():
                for i, cost in enumerate(costs):
                    await tracker.record_cost(
                        model_id=model_id,
                        agent_type="PM",
                        input_tokens=1000,
                        output_tokens=1000,
                        cost=cost,
                        task_id=f"test-{model_id}-{i}"
                    )
            
            # Query costs
            start_date = datetime.now() - timedelta(hours=1)
            end_date = datetime.now() + timedelta(hours=1)
            cost_by_model = await tracker.get_cost_by_model(start_date, end_date)
            
            # Verify: each model aggregated correctly
            self.assertEqual(len(cost_by_model), 3)
            self.assertAlmostEqual(cost_by_model["gpt-4-turbo"], 3.5, places=6)
            self.assertAlmostEqual(cost_by_model["gpt-3.5-turbo"], 1.0, places=6)
            self.assertAlmostEqual(cost_by_model["claude-3.5-sonnet"], 2.5, places=6)
        
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            loop.run_until_complete(test())
        finally:
            loop.close()
    
    def test_query_filtering_time_range_boundary(self):
        """
        Test query filtering at time range boundaries.
        
        Edge case: Records at exact boundary times should be handled correctly.
        
        **Validates: Requirements 10.5**
        """
        async def test():
            tracker = CostTracker(self.db_path, daily_budget=100.0)
            
            # Record costs at different times
            base_time = datetime.now()
            
            # Record before range
            await tracker.record_cost(
                model_id="gpt-4-turbo",
                agent_type="PM",
                input_tokens=1000,
                output_tokens=1000,
                cost=1.0,
                task_id="before-range"
            )
            
            # Wait a moment to ensure different timestamps
            import time
            time.sleep(0.1)
            
            # Define query range
            start_date = datetime.now()
            
            # Record within range
            await tracker.record_cost(
                model_id="gpt-4-turbo",
                agent_type="PM",
                input_tokens=1000,
                output_tokens=1000,
                cost=2.0,
                task_id="within-range"
            )
            
            time.sleep(0.1)
            end_date = datetime.now()
            
            # Record after range
            await tracker.record_cost(
                model_id="gpt-4-turbo",
                agent_type="PM",
                input_tokens=1000,
                output_tokens=1000,
                cost=3.0,
                task_id="after-range"
            )
            
            # Query with specific time range
            cost_by_model = await tracker.get_cost_by_model(start_date, end_date)
            
            # Verify: only records within range are included
            self.assertEqual(len(cost_by_model), 1)
            self.assertAlmostEqual(cost_by_model["gpt-4-turbo"], 2.0, places=6)
        
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            loop.run_until_complete(test())
        finally:
            loop.close()
    
    def test_query_filtering_by_agent_type(self):
        """
        Test query filtering by agent type.
        
        Edge case: Different agent types should be filtered correctly.
        
        **Validates: Requirements 10.5**
        """
        async def test():
            tracker = CostTracker(self.db_path, daily_budget=100.0)
            
            # Record costs for different agent types
            agent_costs = {
                "PM": [1.0, 1.5],
                "BA": [2.0, 2.5, 3.0],
                "Implementation": [0.5]
            }
            
            for agent_type, costs in agent_costs.items():
                for i, cost in enumerate(costs):
                    await tracker.record_cost(
                        model_id="gpt-4-turbo",
                        agent_type=agent_type,
                        input_tokens=1000,
                        output_tokens=1000,
                        cost=cost,
                        task_id=f"test-{agent_type}-{i}"
                    )
            
            # Query costs by agent type
            start_date = datetime.now() - timedelta(hours=1)
            end_date = datetime.now() + timedelta(hours=1)
            cost_by_agent = await tracker.get_cost_by_agent_type(start_date, end_date)
            
            # Verify: each agent type aggregated correctly
            self.assertEqual(len(cost_by_agent), 3)
            self.assertAlmostEqual(cost_by_agent["PM"], 2.5, places=6)
            self.assertAlmostEqual(cost_by_agent["BA"], 7.5, places=6)
            self.assertAlmostEqual(cost_by_agent["Implementation"], 0.5, places=6)
        
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            loop.run_until_complete(test())
        finally:
            loop.close()
    
    def test_query_filtering_no_matching_model(self):
        """
        Test query filtering when no records match the model filter.
        
        Edge case: Querying non-existent model should return empty result.
        
        **Validates: Requirements 10.5**
        """
        async def test():
            tracker = CostTracker(self.db_path, daily_budget=100.0)
            
            # Record costs for one model
            await tracker.record_cost(
                model_id="gpt-4-turbo",
                agent_type="PM",
                input_tokens=1000,
                output_tokens=1000,
                cost=5.0,
                task_id="test-task"
            )
            
            # Query costs
            start_date = datetime.now() - timedelta(hours=1)
            end_date = datetime.now() + timedelta(hours=1)
            cost_by_model = await tracker.get_cost_by_model(start_date, end_date)
            
            # Verify: only recorded model is present
            self.assertEqual(len(cost_by_model), 1)
            self.assertIn("gpt-4-turbo", cost_by_model)
            self.assertNotIn("claude-3-opus", cost_by_model)
            
            # Verify: non-existent model returns 0 cost
            self.assertEqual(cost_by_model.get("claude-3-opus", 0.0), 0.0)
        
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            loop.run_until_complete(test())
        finally:
            loop.close()
    
    def test_cost_summary_comprehensive(self):
        """
        Test comprehensive cost summary with multiple dimensions.
        
        Edge case: Summary should include all aggregations correctly.
        
        **Validates: Requirements 10.5**
        """
        async def test():
            tracker = CostTracker(self.db_path, daily_budget=100.0)
            
            # Record diverse costs
            records = [
                ("gpt-4-turbo", "PM", 1000, 500, 1.5),
                ("gpt-4-turbo", "BA", 2000, 1000, 3.0),
                ("gpt-3.5-turbo", "Implementation", 5000, 2000, 0.5),
                ("claude-3.5-sonnet", "PM", 1500, 800, 2.0),
            ]
            
            for model_id, agent_type, input_tokens, output_tokens, cost in records:
                await tracker.record_cost(
                    model_id=model_id,
                    agent_type=agent_type,
                    input_tokens=input_tokens,
                    output_tokens=output_tokens,
                    cost=cost,
                    task_id=f"test-{model_id}-{agent_type}"
                )
            
            # Get comprehensive summary
            start_date = datetime.now() - timedelta(hours=1)
            end_date = datetime.now() + timedelta(hours=1)
            summary = await tracker.get_cost_summary(start_date, end_date)
            
            # Verify summary fields
            self.assertAlmostEqual(summary["total_cost"], 7.0, places=6)
            self.assertEqual(summary["total_requests"], 4)
            self.assertEqual(summary["total_input_tokens"], 9500)
            self.assertEqual(summary["total_output_tokens"], 4300)
            self.assertAlmostEqual(summary["average_cost_per_request"], 1.75, places=6)
            
            # Verify cost by model
            self.assertAlmostEqual(summary["cost_by_model"]["gpt-4-turbo"], 4.5, places=6)
            self.assertAlmostEqual(summary["cost_by_model"]["gpt-3.5-turbo"], 0.5, places=6)
            self.assertAlmostEqual(summary["cost_by_model"]["claude-3.5-sonnet"], 2.0, places=6)
            
            # Verify cost by agent type
            self.assertAlmostEqual(summary["cost_by_agent_type"]["PM"], 3.5, places=6)
            self.assertAlmostEqual(summary["cost_by_agent_type"]["BA"], 3.0, places=6)
            self.assertAlmostEqual(summary["cost_by_agent_type"]["Implementation"], 0.5, places=6)
        
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            loop.run_until_complete(test())
        finally:
            loop.close()


if __name__ == '__main__':
    unittest.main()
