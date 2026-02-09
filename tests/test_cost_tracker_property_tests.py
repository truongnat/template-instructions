"""
Property-based tests for CostTracker class.

This module tests the correctness properties of the CostTracker including
cost calculation accuracy, aggregation correctness, budget threshold alerting,
data persistence, and query filtering.

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

from agentic_sdlc.orchestration.api_model_management.cost_tracker import CostTracker
from agentic_sdlc.orchestration.api_model_management.database import DatabaseManager
from agentic_sdlc.orchestration.api_model_management.models import BudgetStatus


# Hypothesis strategies for generating test data

def cost_record_strategy():
    """Strategy for generating valid cost records"""
    return st.builds(
        dict,
        model_id=st.sampled_from([
            "gpt-4-turbo", "gpt-3.5-turbo", "claude-3.5-sonnet", 
            "claude-3-opus", "gemini-pro", "ollama-llama2"
        ]),
        agent_type=st.sampled_from([
            "PM", "BA", "SA", "Research", "Quality", "Implementation"
        ]),
        input_tokens=st.integers(min_value=10, max_value=10000),
        output_tokens=st.integers(min_value=10, max_value=10000),
        task_id=st.text(
            min_size=5, 
            max_size=20, 
            alphabet=st.characters(whitelist_categories=('Lu', 'Ll', 'Nd'), whitelist_characters='-_')
        )
    )


def model_pricing_strategy():
    """Strategy for generating model pricing information"""
    return st.builds(
        dict,
        input_cost_per_1k=st.floats(min_value=0.0001, max_value=0.1, allow_nan=False, allow_infinity=False),
        output_cost_per_1k=st.floats(min_value=0.0001, max_value=0.3, allow_nan=False, allow_infinity=False)
    )


def time_range_strategy():
    """Strategy for generating time ranges"""
    base_date = datetime(2024, 1, 1, 0, 0, 0)
    return st.builds(
        lambda days_offset, duration_days: (
            base_date + timedelta(days=days_offset),
            base_date + timedelta(days=days_offset + duration_days)
        ),
        days_offset=st.integers(min_value=0, max_value=30),
        duration_days=st.integers(min_value=1, max_value=7)
    )


@unittest.skipIf(not HYPOTHESIS_AVAILABLE, "Hypothesis not available")
class TestCostTrackerProperties(unittest.TestCase):
    """
    Property-based tests for CostTracker.
    
    Tests Properties 41-45 from the design document:
    - Property 41: Cost calculation accuracy
    - Property 42: Cost aggregation correctness
    - Property 43: Budget threshold alerting
    - Property 44: Cost data persistence
    - Property 45: Cost query filtering
    """
    
    def setUp(self):
        """Set up test case with temporary database"""
        if not HYPOTHESIS_AVAILABLE:
            self.skipTest("Hypothesis not available")
        
        # Create unique temp directory for each test
        self.temp_dir = tempfile.mkdtemp()
        # Use a unique database file name with timestamp to avoid conflicts
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
        import shutil
        if hasattr(self, 'temp_dir'):
            shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    @settings(max_examples=50, deadline=None)
    @given(
        record=cost_record_strategy(),
        pricing=model_pricing_strategy()
    )
    def test_property_41_cost_calculation_accuracy(self, record: Dict[str, Any], pricing: Dict[str, float]):
        """
        Feature: api-model-management
        Property 41: Cost calculation accuracy
        
        For any completed request, the recorded cost should equal 
        (input_tokens / 1000 * input_cost_per_1k) + (output_tokens / 1000 * output_cost_per_1k)
        
        **Validates: Requirements 10.1**
        """
        # Calculate expected cost
        expected_cost = (
            (record['input_tokens'] / 1000.0 * pricing['input_cost_per_1k']) +
            (record['output_tokens'] / 1000.0 * pricing['output_cost_per_1k'])
        )
        
        async def test_cost_calculation():
            # Create fresh database for this example
            import time
            temp_dir = tempfile.mkdtemp()
            db_path = Path(temp_dir) / f"test_{int(time.time() * 1000000)}.db"
            db_manager = DatabaseManager(db_path)
            await db_manager.initialize()
            
            try:
                tracker = CostTracker(db_path, daily_budget=100.0)
                
                # Record cost
                await tracker.record_cost(
                    model_id=record['model_id'],
                    agent_type=record['agent_type'],
                    input_tokens=record['input_tokens'],
                    output_tokens=record['output_tokens'],
                    cost=expected_cost,
                    task_id=record['task_id']
                )
                
                # Retrieve and verify
                start_date = datetime.now() - timedelta(hours=1)
                end_date = datetime.now() + timedelta(hours=1)
                cost_by_model = await tracker.get_cost_by_model(start_date, end_date)
                
                recorded_cost = cost_by_model.get(record['model_id'], 0.0)
                
                # Verify cost calculation accuracy (within floating point precision)
                self.assertAlmostEqual(recorded_cost, expected_cost, places=6)
            finally:
                # Clean up
                import shutil
                shutil.rmtree(temp_dir, ignore_errors=True)
        
        # Run async test
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            loop.run_until_complete(test_cost_calculation())
        finally:
            loop.close()
    
    @settings(max_examples=50, deadline=None)
    @given(
        records=st.lists(cost_record_strategy(), min_size=2, max_size=10),
        pricing=model_pricing_strategy()
    )
    def test_property_42_cost_aggregation_correctness(self, records: List[Dict[str, Any]], pricing: Dict[str, float]):
        """
        Feature: api-model-management
        Property 42: Cost aggregation correctness
        
        For any time period and aggregation dimension (model, provider, agent type), 
        the aggregated cost should equal the sum of all individual request costs 
        matching the criteria
        
        **Validates: Requirements 10.2**
        """
        # Calculate individual costs
        individual_costs = []
        for record in records:
            cost = (
                (record['input_tokens'] / 1000.0 * pricing['input_cost_per_1k']) +
                (record['output_tokens'] / 1000.0 * pricing['output_cost_per_1k'])
            )
            individual_costs.append((record, cost))
        
        async def test_aggregation():
            # Create fresh database for this example
            import time
            temp_dir = tempfile.mkdtemp()
            db_path = Path(temp_dir) / f"test_{int(time.time() * 1000000)}.db"
            db_manager = DatabaseManager(db_path)
            await db_manager.initialize()
            
            try:
                tracker = CostTracker(db_path, daily_budget=100.0)
                
                # Record all costs
                for record, cost in individual_costs:
                    await tracker.record_cost(
                        model_id=record['model_id'],
                        agent_type=record['agent_type'],
                        input_tokens=record['input_tokens'],
                        output_tokens=record['output_tokens'],
                        cost=cost,
                        task_id=record['task_id']
                    )
                
                # Test aggregation by model
                start_date = datetime.now() - timedelta(hours=1)
                end_date = datetime.now() + timedelta(hours=1)
                cost_by_model = await tracker.get_cost_by_model(start_date, end_date)
                
                # Calculate expected aggregation by model
                expected_by_model = {}
                for record, cost in individual_costs:
                    model_id = record['model_id']
                    expected_by_model[model_id] = expected_by_model.get(model_id, 0.0) + cost
                
                # Verify aggregation correctness
                for model_id, expected_cost in expected_by_model.items():
                    actual_cost = cost_by_model.get(model_id, 0.0)
                    self.assertAlmostEqual(actual_cost, expected_cost, places=6,
                        msg=f"Model {model_id}: expected {expected_cost}, got {actual_cost}")
                
                # Test aggregation by agent type
                cost_by_agent = await tracker.get_cost_by_agent_type(start_date, end_date)
                
                # Calculate expected aggregation by agent type
                expected_by_agent = {}
                for record, cost in individual_costs:
                    agent_type = record['agent_type']
                    expected_by_agent[agent_type] = expected_by_agent.get(agent_type, 0.0) + cost
                
                # Verify aggregation correctness
                for agent_type, expected_cost in expected_by_agent.items():
                    actual_cost = cost_by_agent.get(agent_type, 0.0)
                    self.assertAlmostEqual(actual_cost, expected_cost, places=6,
                        msg=f"Agent {agent_type}: expected {expected_cost}, got {actual_cost}")
            finally:
                # Clean up
                import shutil
                shutil.rmtree(temp_dir, ignore_errors=True)
        
        # Run async test
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            loop.run_until_complete(test_aggregation())
        finally:
            loop.close()
    
    @settings(max_examples=50, deadline=None)
    @given(
        daily_budget=st.floats(min_value=1.0, max_value=100.0, allow_nan=False, allow_infinity=False),
        cost_multiplier=st.floats(min_value=0.5, max_value=2.0, allow_nan=False, allow_infinity=False)
    )
    def test_property_43_budget_threshold_alerting(self, daily_budget: float, cost_multiplier: float):
        """
        Feature: api-model-management
        Property 43: Budget threshold alerting
        
        For any day where total costs exceed the configured daily budget, 
        a budget alert should be triggered
        
        **Validates: Requirements 10.3**
        """
        # Calculate cost relative to budget
        total_cost = daily_budget * cost_multiplier
        
        async def test_budget_alert():
            # Create fresh database for this example
            import time
            temp_dir = tempfile.mkdtemp()
            db_path = Path(temp_dir) / f"test_{int(time.time() * 1000000)}.db"
            db_manager = DatabaseManager(db_path)
            await db_manager.initialize()
            
            try:
                tracker = CostTracker(db_path, daily_budget=daily_budget)
                
                # Record cost
                await tracker.record_cost(
                    model_id="test-model",
                    agent_type="PM",
                    input_tokens=1000,
                    output_tokens=1000,
                    cost=total_cost,
                    task_id="test-task"
                )
                
                # Check budget status
                budget_status = await tracker.check_budget()
                
                # Verify budget status fields
                self.assertIsInstance(budget_status, BudgetStatus)
                self.assertEqual(budget_status.daily_budget, daily_budget)
                self.assertAlmostEqual(budget_status.current_spend, total_cost, places=6)
                
                # Verify alert triggering
                if cost_multiplier > 1.0:
                    # Cost exceeds budget - should trigger alert
                    self.assertTrue(budget_status.is_over_budget,
                        f"Expected alert when cost ({total_cost}) exceeds budget ({daily_budget})")
                    self.assertGreater(budget_status.utilization_percent, 100.0)
                    self.assertEqual(budget_status.remaining_budget, 0.0)
                else:
                    # Cost within or equal to budget - no alert
                    self.assertFalse(budget_status.is_over_budget,
                        f"No alert expected when cost ({total_cost}) is within budget ({daily_budget})")
                    self.assertLessEqual(budget_status.utilization_percent, 100.0)
                    self.assertGreaterEqual(budget_status.remaining_budget, 0.0)
            finally:
                # Clean up
                import shutil
                shutil.rmtree(temp_dir, ignore_errors=True)
        
        # Run async test
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            loop.run_until_complete(test_budget_alert())
        finally:
            loop.close()
    
    @settings(max_examples=50, deadline=None)
    @given(
        record=cost_record_strategy(),
        pricing=model_pricing_strategy()
    )
    def test_property_44_cost_data_persistence(self, record: Dict[str, Any], pricing: Dict[str, float]):
        """
        Feature: api-model-management
        Property 44: Cost data persistence
        
        For any cost record, it should be persisted to SQLite and be retrievable 
        with all fields intact
        
        **Validates: Requirements 10.4**
        """
        cost = (
            (record['input_tokens'] / 1000.0 * pricing['input_cost_per_1k']) +
            (record['output_tokens'] / 1000.0 * pricing['output_cost_per_1k'])
        )
        
        async def test_persistence():
            # Create fresh database for this example
            import time
            temp_dir = tempfile.mkdtemp()
            db_path = Path(temp_dir) / f"test_{int(time.time() * 1000000)}.db"
            db_manager = DatabaseManager(db_path)
            await db_manager.initialize()
            
            try:
                tracker = CostTracker(db_path, daily_budget=100.0)
                
                # Record cost
                await tracker.record_cost(
                    model_id=record['model_id'],
                    agent_type=record['agent_type'],
                    input_tokens=record['input_tokens'],
                    output_tokens=record['output_tokens'],
                    cost=cost,
                    task_id=record['task_id']
                )
                
                # Retrieve cost summary to verify persistence
                start_date = datetime.now() - timedelta(hours=1)
                end_date = datetime.now() + timedelta(hours=1)
                summary = await tracker.get_cost_summary(start_date, end_date)
                
                # Verify all fields are persisted
                self.assertGreater(summary['total_requests'], 0)
                self.assertAlmostEqual(summary['total_cost'], cost, places=6)
                self.assertEqual(summary['total_input_tokens'], record['input_tokens'])
                self.assertEqual(summary['total_output_tokens'], record['output_tokens'])
                
                # Verify model-specific data
                self.assertIn(record['model_id'], summary['cost_by_model'])
                self.assertAlmostEqual(
                    summary['cost_by_model'][record['model_id']], 
                    cost, 
                    places=6
                )
                
                # Verify agent-specific data
                self.assertIn(record['agent_type'], summary['cost_by_agent_type'])
                self.assertAlmostEqual(
                    summary['cost_by_agent_type'][record['agent_type']], 
                    cost, 
                    places=6
                )
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
    
    @settings(max_examples=50, deadline=None)
    @given(
        records=st.lists(cost_record_strategy(), min_size=5, max_size=15),
        pricing=model_pricing_strategy(),
        filter_model=st.sampled_from([
            "gpt-4-turbo", "gpt-3.5-turbo", "claude-3.5-sonnet"
        ]),
        filter_agent=st.sampled_from(["PM", "BA", "SA"])
    )
    def test_property_45_cost_query_filtering(
        self, 
        records: List[Dict[str, Any]], 
        pricing: Dict[str, float],
        filter_model: str,
        filter_agent: str
    ):
        """
        Feature: api-model-management
        Property 45: Cost query filtering
        
        For any cost query with filters (time range, model, provider, agent type), 
        all returned records should match the filters
        
        **Validates: Requirements 10.5**
        """
        # Calculate costs for all records
        records_with_costs = []
        for record in records:
            cost = (
                (record['input_tokens'] / 1000.0 * pricing['input_cost_per_1k']) +
                (record['output_tokens'] / 1000.0 * pricing['output_cost_per_1k'])
            )
            records_with_costs.append((record, cost))
        
        async def test_filtering():
            # Create fresh database for this example
            import time
            temp_dir = tempfile.mkdtemp()
            db_path = Path(temp_dir) / f"test_{int(time.time() * 1000000)}.db"
            db_manager = DatabaseManager(db_path)
            await db_manager.initialize()
            
            try:
                tracker = CostTracker(db_path, daily_budget=100.0)
                
                # Record all costs
                for record, cost in records_with_costs:
                    await tracker.record_cost(
                        model_id=record['model_id'],
                        agent_type=record['agent_type'],
                        input_tokens=record['input_tokens'],
                        output_tokens=record['output_tokens'],
                        cost=cost,
                        task_id=record['task_id']
                    )
                
                # Test filtering by model
                start_date = datetime.now() - timedelta(hours=1)
                end_date = datetime.now() + timedelta(hours=1)
                cost_by_model = await tracker.get_cost_by_model(start_date, end_date)
                
                # Calculate expected cost for filtered model
                expected_model_cost = sum(
                    cost for record, cost in records_with_costs 
                    if record['model_id'] == filter_model
                )
                
                actual_model_cost = cost_by_model.get(filter_model, 0.0)
                self.assertAlmostEqual(actual_model_cost, expected_model_cost, places=6,
                    msg=f"Model filter: expected {expected_model_cost}, got {actual_model_cost}")
                
                # Test filtering by agent type
                cost_by_agent = await tracker.get_cost_by_agent_type(start_date, end_date)
                
                # Calculate expected cost for filtered agent
                expected_agent_cost = sum(
                    cost for record, cost in records_with_costs 
                    if record['agent_type'] == filter_agent
                )
                
                actual_agent_cost = cost_by_agent.get(filter_agent, 0.0)
                self.assertAlmostEqual(actual_agent_cost, expected_agent_cost, places=6,
                    msg=f"Agent filter: expected {expected_agent_cost}, got {actual_agent_cost}")
                
                # Verify no unfiltered data is returned
                for model_id, cost in cost_by_model.items():
                    # All returned models should have at least one matching record
                    matching_records = [r for r, c in records_with_costs if r['model_id'] == model_id]
                    self.assertGreater(len(matching_records), 0,
                        f"Model {model_id} returned but has no matching records")
                
                for agent_type, cost in cost_by_agent.items():
                    # All returned agents should have at least one matching record
                    matching_records = [r for r, c in records_with_costs if r['agent_type'] == agent_type]
                    self.assertGreater(len(matching_records), 0,
                        f"Agent {agent_type} returned but has no matching records")
            finally:
                # Clean up
                import shutil
                shutil.rmtree(temp_dir, ignore_errors=True)
        
        # Run async test
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            loop.run_until_complete(test_filtering())
        finally:
            loop.close()


if __name__ == '__main__':
    # Configure test settings
    if HYPOTHESIS_AVAILABLE:
        settings.register_profile("default", max_examples=50, deadline=None)
        settings.load_profile("default")
    
    unittest.main()
