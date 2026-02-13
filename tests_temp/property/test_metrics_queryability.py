"""
Property-based tests for Metrics Queryability.

These tests use Hypothesis to verify that metrics can be queried by name,
timestamp, and value across many randomly generated inputs.

Feature: sdlc-kit-improvements
Property 5: Metrics Queryability
Requirements: 5.6
"""

import pytest
import tempfile
from pathlib import Path
from datetime import datetime, timedelta
from hypothesis import given, strategies as st, settings, assume

from monitoring.metrics import MetricsCollector, Metric


# Strategy for generating metric names
metric_names = st.text(
    alphabet=st.characters(min_codepoint=97, max_codepoint=122),  # a-z
    min_size=5,
    max_size=30
).map(lambda x: f"test.{x}")

# Strategy for generating numeric metric values
metric_values = st.floats(
    min_value=-1000000.0,
    max_value=1000000.0,
    allow_nan=False,
    allow_infinity=False
)

# Strategy for generating timestamps
def generate_timestamp():
    """Generate a timestamp within a reasonable range."""
    base = datetime(2024, 1, 1)
    delta = timedelta(days=st.integers(min_value=0, max_value=365).example())
    return base + delta

timestamps = st.datetimes(
    min_value=datetime(2024, 1, 1),
    max_value=datetime(2024, 12, 31)
)


# Feature: sdlc-kit-improvements, Property 5: Metrics Queryability
@given(
    name=metric_names,
    value=metric_values,
)
@settings(max_examples=5, deadline=None)
def test_metric_queryable_by_name(name, value):
    """
    Property: For any metric collected by the Monitoring_System, the metric
    should be stored in a format that allows querying by metric name.
    
    This property ensures that metrics can be retrieved by their name.
    
    **Validates: Requirements 5.6**
    """
    with tempfile.TemporaryDirectory() as tmpdir:
        storage_path = Path(tmpdir) / "metrics.json"
        collector = MetricsCollector(storage_path=storage_path)
        
        # Collect a metric
        collector.collect(name=name, value=value)
        
        # Property: Metric should be queryable by name
        results = collector.query_by_name(name)
        
        assert len(results) > 0, f"Should find at least one metric with name '{name}'"
        assert all(m.name == name for m in results), "All results should have the queried name"
        assert any(m.value == value for m in results), f"Should find metric with value {value}"


# Feature: sdlc-kit-improvements, Property 5: Metrics Queryability
@given(
    metrics_data=st.lists(
        st.tuples(metric_names, metric_values),
        min_size=1,
        max_size=20
    )
)
@settings(max_examples=5, deadline=None)
def test_multiple_metrics_queryable_by_name(metrics_data):
    """
    Property: For any set of metrics with different names, each metric
    should be independently queryable by its name.
    
    This property ensures that name-based queries return only metrics
    with the exact name match.
    
    **Validates: Requirements 5.6**
    """
    with tempfile.TemporaryDirectory() as tmpdir:
        storage_path = Path(tmpdir) / "metrics.json"
        collector = MetricsCollector(storage_path=storage_path)
        
        # Collect all metrics
        for name, value in metrics_data:
            collector.collect(name=name, value=value)
        
        # Get unique names
        unique_names = list(set(name for name, _ in metrics_data))
        
        # Property: Each unique name should be queryable
        for unique_name in unique_names:
            results = collector.query_by_name(unique_name)
            
            # Count expected occurrences
            expected_count = sum(1 for name, _ in metrics_data if name == unique_name)
            
            assert len(results) == expected_count, (
                f"Should find {expected_count} metrics with name '{unique_name}', "
                f"found {len(results)}"
            )
            assert all(m.name == unique_name for m in results), (
                "All results should have the queried name"
            )


# Feature: sdlc-kit-improvements, Property 5: Metrics Queryability
@given(
    name=metric_names,
    value=metric_values,
    timestamp=timestamps,
)
@settings(max_examples=5, deadline=None)
def test_metric_queryable_by_timestamp(name, value, timestamp):
    """
    Property: For any metric collected by the Monitoring_System, the metric
    should be stored in a format that allows querying by timestamp.
    
    This property ensures that metrics can be retrieved by time range.
    
    **Validates: Requirements 5.6**
    """
    with tempfile.TemporaryDirectory() as tmpdir:
        storage_path = Path(tmpdir) / "metrics.json"
        collector = MetricsCollector(storage_path=storage_path)
        
        # Create a metric with specific timestamp
        metric = Metric(name=name, value=value, timestamp=timestamp)
        collector._metrics.append(metric)
        collector._save_metrics()
        
        # Property: Metric should be queryable by time range
        start_time = timestamp - timedelta(seconds=1)
        end_time = timestamp + timedelta(seconds=1)
        
        results = collector.query_by_time_range(start=start_time, end=end_time)
        
        assert len(results) > 0, "Should find at least one metric in time range"
        assert any(
            m.name == name and m.value == value and m.timestamp == timestamp
            for m in results
        ), "Should find the exact metric in time range"


# Feature: sdlc-kit-improvements, Property 5: Metrics Queryability
@given(
    name=metric_names,
    value=metric_values,
)
@settings(max_examples=5, deadline=None)
def test_metric_queryable_by_value(name, value):
    """
    Property: For any metric collected by the Monitoring_System, the metric
    should be stored in a format that allows querying by value.
    
    This property ensures that metrics can be retrieved by value range.
    
    **Validates: Requirements 5.6**
    """
    with tempfile.TemporaryDirectory() as tmpdir:
        storage_path = Path(tmpdir) / "metrics.json"
        collector = MetricsCollector(storage_path=storage_path)
        
        # Collect a metric
        collector.collect(name=name, value=value)
        
        # Property: Metric should be queryable by value range
        min_value = value - 1.0
        max_value = value + 1.0
        
        results = collector.query_by_value(min_value=min_value, max_value=max_value)
        
        assert len(results) > 0, "Should find at least one metric in value range"
        assert any(
            m.name == name and float(m.value) == pytest.approx(value, rel=1e-9)
            for m in results
        ), f"Should find metric with value {value} in range [{min_value}, {max_value}]"


# Feature: sdlc-kit-improvements, Property 5: Metrics Queryability
@given(
    metrics_data=st.lists(
        st.tuples(metric_names, metric_values),
        min_size=3,
        max_size=20
    )
)
@settings(max_examples=5, deadline=None)
def test_metrics_queryable_by_value_range(metrics_data):
    """
    Property: For any set of metrics with different values, querying by
    value range should return only metrics within that range.
    
    This property ensures that value-based queries correctly filter metrics.
    
    **Validates: Requirements 5.6**
    """
    assume(len(metrics_data) >= 3)  # Need at least 3 metrics for meaningful test
    
    with tempfile.TemporaryDirectory() as tmpdir:
        storage_path = Path(tmpdir) / "metrics.json"
        collector = MetricsCollector(storage_path=storage_path)
        
        # Collect all metrics
        for name, value in metrics_data:
            collector.collect(name=name, value=value)
        
        # Get all values and sort them
        all_values = sorted([value for _, value in metrics_data])
        
        # Query for middle range
        if len(all_values) >= 3:
            min_value = all_values[len(all_values) // 3]
            max_value = all_values[2 * len(all_values) // 3]
            
            results = collector.query_by_value(min_value=min_value, max_value=max_value)
            
            # Property: All results should be within range
            for result in results:
                result_value = float(result.value)
                assert min_value <= result_value <= max_value, (
                    f"Result value {result_value} should be in range [{min_value}, {max_value}]"
                )
            
            # Property: All metrics in range should be in results
            expected_in_range = [
                (name, value) for name, value in metrics_data
                if min_value <= value <= max_value
            ]
            
            assert len(results) == len(expected_in_range), (
                f"Should find {len(expected_in_range)} metrics in range, found {len(results)}"
            )


# Feature: sdlc-kit-improvements, Property 5: Metrics Queryability
@given(
    name=metric_names,
    value=metric_values,
    timestamp=timestamps,
)
@settings(max_examples=5, deadline=None)
def test_metric_queryable_by_combined_filters(name, value, timestamp):
    """
    Property: For any metric collected by the Monitoring_System, the metric
    should be queryable using multiple filters simultaneously (name, timestamp, value).
    
    This property ensures that combined queries work correctly.
    
    **Validates: Requirements 5.6**
    """
    with tempfile.TemporaryDirectory() as tmpdir:
        storage_path = Path(tmpdir) / "metrics.json"
        collector = MetricsCollector(storage_path=storage_path)
        
        # Create a metric with specific properties
        metric = Metric(name=name, value=value, timestamp=timestamp)
        collector._metrics.append(metric)
        collector._save_metrics()
        
        # Property: Metric should be queryable with combined filters
        start_time = timestamp - timedelta(seconds=1)
        end_time = timestamp + timedelta(seconds=1)
        min_value = value - 1.0
        max_value = value + 1.0
        
        results = collector.query(
            name=name,
            start_time=start_time,
            end_time=end_time,
            min_value=min_value,
            max_value=max_value
        )
        
        assert len(results) > 0, "Should find at least one metric with combined filters"
        assert any(
            m.name == name and 
            m.value == value and 
            m.timestamp == timestamp
            for m in results
        ), "Should find the exact metric with all filters applied"


# Feature: sdlc-kit-improvements, Property 5: Metrics Queryability
@given(
    metrics_data=st.lists(
        st.tuples(metric_names, metric_values, timestamps),
        min_size=1,
        max_size=20
    )
)
@settings(max_examples=5, deadline=None)
def test_metrics_persist_and_reload(metrics_data):
    """
    Property: For any set of metrics collected and stored, when the collector
    is reloaded from storage, all metrics should still be queryable.
    
    This property ensures that metrics persistence maintains queryability.
    
    **Validates: Requirements 5.6**
    """
    with tempfile.TemporaryDirectory() as tmpdir:
        storage_path = Path(tmpdir) / "metrics.json"
        
        # First collector: collect metrics
        collector1 = MetricsCollector(storage_path=storage_path)
        for name, value, timestamp in metrics_data:
            metric = Metric(name=name, value=value, timestamp=timestamp)
            collector1._metrics.append(metric)
        collector1._save_metrics()
        
        # Second collector: reload from storage
        collector2 = MetricsCollector(storage_path=storage_path)
        
        # Property: All metrics should be queryable after reload
        assert len(collector2.get_all_metrics()) == len(metrics_data), (
            "Reloaded collector should have same number of metrics"
        )
        
        # Verify each metric is queryable by name
        unique_names = list(set(name for name, _, _ in metrics_data))
        for unique_name in unique_names:
            results = collector2.query_by_name(unique_name)
            expected_count = sum(1 for name, _, _ in metrics_data if name == unique_name)
            assert len(results) == expected_count, (
                f"Should find {expected_count} metrics with name '{unique_name}' after reload"
            )


# Feature: sdlc-kit-improvements, Property 5: Metrics Queryability
@given(
    name=metric_names,
    values=st.lists(metric_values, min_size=1, max_size=10)
)
@settings(max_examples=5, deadline=None)
def test_metrics_with_same_name_all_queryable(name, values):
    """
    Property: For any set of metrics with the same name but different values,
    all metrics should be queryable and retrievable.
    
    This property ensures that multiple metrics with the same name are all stored
    and queryable.
    
    **Validates: Requirements 5.6**
    """
    with tempfile.TemporaryDirectory() as tmpdir:
        storage_path = Path(tmpdir) / "metrics.json"
        collector = MetricsCollector(storage_path=storage_path)
        
        # Collect multiple metrics with same name
        for value in values:
            collector.collect(name=name, value=value)
        
        # Property: All metrics should be queryable by name
        results = collector.query_by_name(name)
        
        assert len(results) == len(values), (
            f"Should find {len(values)} metrics with name '{name}', found {len(results)}"
        )
        
        # Property: All values should be present
        result_values = [float(m.value) for m in results]
        for expected_value in values:
            assert any(
                pytest.approx(v, rel=1e-9) == expected_value for v in result_values
            ), f"Should find metric with value {expected_value}"
