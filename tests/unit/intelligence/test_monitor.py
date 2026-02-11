"""Unit tests for Monitor and MetricsCollector classes."""

import pytest
import tempfile
from pathlib import Path
from agentic_sdlc.intelligence.monitoring import Monitor, MetricsCollector


class TestMonitor:
    """Tests for Monitor functionality."""

    @pytest.fixture
    def monitor(self):
        """Create a monitor instance."""
        return Monitor()

    def test_monitor_initialization(self, monitor):
        """Test monitor initialization."""
        assert monitor is not None
        assert len(monitor.health_history) == 0
        assert len(monitor.metrics) == 0

    def test_check_health(self, monitor):
        """Test health check."""
        status = monitor.check_health()
        assert status.status == "healthy"
        assert len(monitor.health_history) == 1

    def test_record_metric(self, monitor):
        """Test recording a metric."""
        monitor.record_metric("cpu_usage", 45.5)
        assert monitor.get_metric("cpu_usage") == 45.5

    def test_get_metric(self, monitor):
        """Test getting a metric."""
        monitor.record_metric("memory_usage", 2048)
        value = monitor.get_metric("memory_usage")
        assert value == 2048

    def test_get_nonexistent_metric(self, monitor):
        """Test getting a metric that doesn't exist."""
        value = monitor.get_metric("nonexistent")
        assert value is None

    def test_get_all_metrics(self, monitor):
        """Test getting all metrics."""
        monitor.record_metric("metric1", 10)
        monitor.record_metric("metric2", 20)
        metrics = monitor.get_all_metrics()
        assert len(metrics) == 2
        assert metrics["metric1"] == 10
        assert metrics["metric2"] == 20

    def test_get_health_history(self, monitor):
        """Test getting health history."""
        monitor.check_health()
        monitor.check_health()
        history = monitor.get_health_history()
        assert len(history) == 2


class TestMetricsCollector:
    """Tests for MetricsCollector functionality."""

    @pytest.fixture
    def collector(self):
        """Create a metrics collector with temporary storage."""
        with tempfile.TemporaryDirectory() as tmpdir:
            storage_file = Path(tmpdir) / "metrics.json"
            yield MetricsCollector(storage_file=storage_file)

    def test_collector_initialization(self, collector):
        """Test collector initialization."""
        assert collector is not None
        assert len(collector.metrics) == 0

    def test_collect_metric(self, collector):
        """Test collecting a metric."""
        collector.collect("response_time", 150)
        history = collector.get_metric_history("response_time")
        assert len(history) == 1
        assert history[0]["value"] == 150

    def test_collect_multiple_values(self, collector):
        """Test collecting multiple values for same metric."""
        collector.collect("response_time", 100)
        collector.collect("response_time", 150)
        collector.collect("response_time", 120)
        history = collector.get_metric_history("response_time")
        assert len(history) == 3

    def test_get_metric_summary(self, collector):
        """Test getting metric summary."""
        collector.collect("latency", 100)
        collector.collect("latency", 200)
        collector.collect("latency", 150)
        summary = collector.get_metric_summary("latency")
        assert summary["count"] == 3
        assert summary["min"] == 100
        assert summary["max"] == 200
        assert summary["avg"] == 150

    def test_get_metric_summary_empty(self, collector):
        """Test getting summary for nonexistent metric."""
        summary = collector.get_metric_summary("nonexistent")
        assert summary == {}

    def test_get_all_metrics(self, collector):
        """Test getting all collected metrics."""
        collector.collect("metric1", 10)
        collector.collect("metric2", 20)
        metrics = collector.get_all_metrics()
        assert len(metrics) == 2

    def test_clear_metrics(self, collector):
        """Test clearing all metrics."""
        collector.collect("metric1", 10)
        collector.collect("metric2", 20)
        collector.clear_metrics()
        assert len(collector.get_all_metrics()) == 0

    def test_clear_specific_metric(self, collector):
        """Test clearing a specific metric."""
        collector.collect("metric1", 10)
        collector.collect("metric2", 20)
        collector.clear_metric("metric1")
        metrics = collector.get_all_metrics()
        assert "metric1" not in metrics
        assert "metric2" in metrics

    def test_metrics_persistence(self):
        """Test that metrics are persisted to storage."""
        with tempfile.TemporaryDirectory() as tmpdir:
            storage_file = Path(tmpdir) / "metrics.json"

            # Create collector and add metric
            collector1 = MetricsCollector(storage_file=storage_file)
            collector1.collect("test_metric", 42)

            # Create new collector with same storage
            collector2 = MetricsCollector(storage_file=storage_file)
            history = collector2.get_metric_history("test_metric")
            assert len(history) == 1
            assert history[0]["value"] == 42
