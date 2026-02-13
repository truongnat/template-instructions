"""System monitoring and metrics collection."""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Dict, List, Optional, Any
import json
from pathlib import Path


@dataclass
class HealthStatus:
    """System health status."""
    status: str  # healthy, warning, critical
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())
    metrics: Dict[str, Any] = field(default_factory=dict)
    message: str = ""


class Monitor:
    """Monitors system health and project metrics."""

    def __init__(self):
        """Initialize the monitor."""
        self.health_history: List[HealthStatus] = []
        self.metrics: Dict[str, Any] = {}

    def check_health(self) -> HealthStatus:
        """Check system health.

        Returns:
            HealthStatus object
        """
        status = HealthStatus(
            status="healthy",
            metrics=self.metrics.copy(),
        )
        self.health_history.append(status)
        return status

    def record_metric(self, name: str, value: Any) -> None:
        """Record a metric.

        Args:
            name: Metric name
            value: Metric value
        """
        self.metrics[name] = value

    def get_metric(self, name: str) -> Optional[Any]:
        """Get a metric value.

        Args:
            name: Metric name

        Returns:
            Metric value or None
        """
        return self.metrics.get(name)

    def get_all_metrics(self) -> Dict[str, Any]:
        """Get all metrics.

        Returns:
            Dictionary of all metrics
        """
        return self.metrics.copy()

    def get_health_history(self) -> List[HealthStatus]:
        """Get health check history.

        Returns:
            List of health statuses
        """
        return self.health_history.copy()


class MetricsCollector:
    """Collects and aggregates metrics."""

    def __init__(self, storage_file: Optional[Path] = None):
        """Initialize the metrics collector.

        Args:
            storage_file: Optional path to store metrics
        """
        self.storage_file = storage_file or Path.home() / ".agentic_sdlc" / "metrics.json"
        self.metrics: Dict[str, List[Any]] = {}
        self._load_metrics()

    def _load_metrics(self):
        """Load previously collected metrics from storage."""
        if self.storage_file.exists():
            try:
                with open(self.storage_file, "r") as f:
                    self.metrics = json.load(f)
            except Exception:
                pass

    def _save_metrics(self):
        """Save collected metrics to storage."""
        self.storage_file.parent.mkdir(parents=True, exist_ok=True)
        with open(self.storage_file, "w") as f:
            json.dump(self.metrics, f, indent=2)

    def collect(self, metric_name: str, value: Any) -> None:
        """Collect a metric value.

        Args:
            metric_name: Name of the metric
            value: Value to collect
        """
        if metric_name not in self.metrics:
            self.metrics[metric_name] = []
        self.metrics[metric_name].append(
            {
                "value": value,
                "timestamp": datetime.now().isoformat(),
            }
        )
        self._save_metrics()

    def get_metric_history(self, metric_name: str) -> List[Dict]:
        """Get history of a metric.

        Args:
            metric_name: Name of the metric

        Returns:
            List of metric values with timestamps
        """
        return self.metrics.get(metric_name, [])

    def get_metric_summary(self, metric_name: str) -> Dict[str, Any]:
        """Get summary statistics for a metric.

        Args:
            metric_name: Name of the metric

        Returns:
            Dictionary with summary statistics
        """
        history = self.get_metric_history(metric_name)
        if not history:
            return {}

        values = [h["value"] for h in history if isinstance(h.get("value"), (int, float))]
        if not values:
            return {"count": len(history)}

        return {
            "count": len(values),
            "min": min(values),
            "max": max(values),
            "avg": sum(values) / len(values),
            "latest": values[-1],
        }

    def get_all_metrics(self) -> Dict[str, List[Dict]]:
        """Get all collected metrics.

        Returns:
            Dictionary of all metrics
        """
        return self.metrics.copy()

    def clear_metrics(self) -> None:
        """Clear all collected metrics."""
        self.metrics = {}
        self._save_metrics()

    def clear_metric(self, metric_name: str) -> None:
        """Clear a specific metric.

        Args:
            metric_name: Name of the metric to clear
        """
        if metric_name in self.metrics:
            del self.metrics[metric_name]
            self._save_metrics()
