"""
Metrics Collector - Performance metrics collection.

Part of Layer 2: Intelligence Layer.
"""

import json
import time
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional


@dataclass
class Metric:
    """A single metric."""
    name: str
    value: float
    unit: str
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())
    tags: Dict = field(default_factory=dict)

    def to_dict(self) -> dict:
        return {
            "name": self.name,
            "value": self.value,
            "unit": self.unit,
            "timestamp": self.timestamp,
            "tags": self.tags
        }


class MetricsCollector:
    """
    Collects and analyzes performance metrics.
    
    Features:
    - Collect timing metrics
    - Track counts and rates
    - Calculate aggregations
    - Generate reports
    """

    def __init__(self, storage_file: Optional[Path] = None):
        self.storage_file = storage_file or Path(".brain-metrics.json")
        self.metrics: List[Metric] = []
        self._timers: Dict[str, float] = {}
        self._load_metrics()

    def _load_metrics(self):
        """Load metrics from storage."""
        if self.storage_file.exists():
            try:
                with open(self.storage_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.metrics = [Metric(**m) for m in data.get("metrics", [])[-1000:]]
            except (json.JSONDecodeError, IOError):
                pass

    def _save_metrics(self):
        """Save metrics to storage."""
        data = {
            "metrics": [m.to_dict() for m in self.metrics[-1000:]],
            "updated_at": datetime.now().isoformat()
        }
        with open(self.storage_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

    def record(
        self,
        name: str,
        value: float,
        unit: str = "count",
        tags: Optional[Dict] = None
    ) -> Metric:
        """Record a metric."""
        metric = Metric(
            name=name,
            value=value,
            unit=unit,
            tags=tags or {}
        )
        self.metrics.append(metric)
        
        # Auto-save every 100 metrics
        if len(self.metrics) % 100 == 0:
            self._save_metrics()
        
        return metric

    def start_timer(self, name: str):
        """Start a timer."""
        self._timers[name] = time.time()

    def stop_timer(self, name: str, tags: Optional[Dict] = None) -> Optional[float]:
        """Stop a timer and record the duration."""
        if name not in self._timers:
            return None
        
        duration = time.time() - self._timers[name]
        del self._timers[name]
        
        self.record(f"{name}_duration", duration, "seconds", tags)
        return duration

    def time(self, name: str, tags: Optional[Dict] = None):
        """Context manager for timing."""
        class Timer:
            def __init__(self_timer, collector, metric_name, metric_tags):
                self_timer.collector = collector
                self_timer.name = metric_name
                self_timer.tags = metric_tags
                self_timer.start = None
            
            def __enter__(self_timer):
                self_timer.start = time.time()
                return self_timer
            
            def __exit__(self_timer, *args):
                duration = time.time() - self_timer.start
                self_timer.collector.record(
                    f"{self_timer.name}_duration",
                    duration,
                    "seconds",
                    self_timer.tags
                )
        
        return Timer(self, name, tags)

    def increment(self, name: str, value: int = 1, tags: Optional[Dict] = None):
        """Increment a counter."""
        self.record(name, value, "count", tags)

    def get_metrics(
        self,
        name: Optional[str] = None,
        since: Optional[datetime] = None,
        limit: int = 100
    ) -> List[Metric]:
        """Get metrics with optional filters."""
        metrics = self.metrics
        
        if name:
            metrics = [m for m in metrics if m.name == name]
        
        if since:
            since_str = since.isoformat()
            metrics = [m for m in metrics if m.timestamp >= since_str]
        
        return metrics[-limit:]

    def get_aggregation(
        self,
        name: str,
        aggregation: str = "avg",
        since: Optional[datetime] = None
    ) -> Optional[float]:
        """Get aggregated value for a metric."""
        metrics = self.get_metrics(name=name, since=since, limit=1000)
        
        if not metrics:
            return None
        
        values = [m.value for m in metrics]
        
        if aggregation == "avg":
            return sum(values) / len(values)
        elif aggregation == "sum":
            return sum(values)
        elif aggregation == "min":
            return min(values)
        elif aggregation == "max":
            return max(values)
        elif aggregation == "count":
            return len(values)
        
        return None

    def get_summary(self, name: str) -> Dict:
        """Get summary statistics for a metric."""
        metrics = self.get_metrics(name=name, limit=1000)
        
        if not metrics:
            return {}
        
        values = [m.value for m in metrics]
        
        return {
            "name": name,
            "count": len(values),
            "sum": sum(values),
            "avg": sum(values) / len(values),
            "min": min(values),
            "max": max(values)
        }

    def flush(self):
        """Save all metrics to storage."""
        self._save_metrics()


class FlowOptimizer:
    """
    Optimizes workflow execution flow.
    
    Features:
    - Identify bottlenecks
    - Suggest optimizations
    - Track improvements
    """

    def __init__(self, collector: Optional[MetricsCollector] = None):
        self.collector = collector or MetricsCollector()
        self.optimizations: List[Dict] = []

    def analyze_bottlenecks(self, workflow: str) -> List[Dict]:
        """Analyze workflow for bottlenecks."""
        bottlenecks = []
        
        # Get all duration metrics for workflow
        metrics = self.collector.get_metrics(limit=500)
        workflow_metrics = [m for m in metrics if workflow in m.name and "_duration" in m.name]
        
        if not workflow_metrics:
            return bottlenecks
        
        # Group by step name
        by_step: Dict[str, List[float]] = {}
        for m in workflow_metrics:
            step = m.name.replace("_duration", "")
            by_step.setdefault(step, []).append(m.value)
        
        # Find slow steps
        for step, durations in by_step.items():
            avg = sum(durations) / len(durations)
            if avg > 1.0:  # More than 1 second average
                bottlenecks.append({
                    "step": step,
                    "avg_duration": round(avg, 2),
                    "max_duration": round(max(durations), 2),
                    "samples": len(durations),
                    "suggestion": self._suggest_optimization(step, avg)
                })
        
        return sorted(bottlenecks, key=lambda x: x["avg_duration"], reverse=True)

    def _suggest_optimization(self, step: str, duration: float) -> str:
        """Suggest optimization for a slow step."""
        if duration > 10:
            return "Consider breaking into subtasks or parallelizing"
        elif duration > 5:
            return "Consider caching or precomputation"
        elif duration > 2:
            return "Review for unnecessary operations"
        else:
            return "Minor optimization possible"

    def track_improvement(
        self,
        metric_name: str,
        before: float,
        after: float,
        description: str
    ):
        """Track an improvement."""
        improvement = {
            "metric": metric_name,
            "before": before,
            "after": after,
            "improvement_percent": round((before - after) / before * 100, 1),
            "description": description,
            "timestamp": datetime.now().isoformat()
        }
        self.optimizations.append(improvement)

    def get_improvements(self) -> List[Dict]:
        """Get tracked improvements."""
        return self.optimizations


def main():
    """CLI entry point."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Performance Metrics - Layer 2 Intelligence")
    parser.add_argument("--record", nargs=3, metavar=("NAME", "VALUE", "UNIT"), 
                        help="Record a metric")
    parser.add_argument("--summary", type=str, help="Get summary for metric")
    parser.add_argument("--list", action="store_true", help="List recent metrics")
    parser.add_argument("--analyze", type=str, help="Analyze bottlenecks for workflow")
    
    args = parser.parse_args()
    collector = MetricsCollector()
    
    if args.record:
        name, value, unit = args.record
        collector.record(name, float(value), unit)
        collector.flush()
        print(f"✅ Recorded: {name} = {value} {unit}")
    
    elif args.summary:
        summary = collector.get_summary(args.summary)
        if summary:
            print(json.dumps(summary, indent=2))
        else:
            print(f"No metrics found for: {args.summary}")
    
    elif args.list:
        for m in collector.get_metrics(limit=20):
            print(f"{m.timestamp[:16]} | {m.name}: {m.value} {m.unit}")
    
    elif args.analyze:
        optimizer = FlowOptimizer(collector)
        bottlenecks = optimizer.analyze_bottlenecks(args.analyze)
        print(json.dumps(bottlenecks, indent=2))
    
    else:
        parser.print_help()


if __name__ == "__main__":
    main()

