"""Metrics collection for SDLC Kit.

This module provides functionality for collecting, storing, and querying
system metrics in a structured format.
"""

import json
from dataclasses import dataclass, asdict
from datetime import datetime
from pathlib import Path
from typing import List, Optional, Dict, Any


@dataclass
class Metric:
    """Represents a single metric data point.
    
    Attributes:
        name: Metric name (e.g., 'workflow.execution_time')
        value: Metric value (numeric or string)
        timestamp: When the metric was recorded
        tags: Optional metadata tags for filtering
    """
    name: str
    value: Any
    timestamp: datetime
    tags: Optional[Dict[str, str]] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert metric to dictionary format."""
        data = asdict(self)
        data['timestamp'] = self.timestamp.isoformat()
        return data
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Metric':
        """Create metric from dictionary format."""
        data['timestamp'] = datetime.fromisoformat(data['timestamp'])
        return cls(**data)


class MetricsCollector:
    """Collects and stores system metrics in queryable format.
    
    Metrics are stored in JSON format for easy querying and analysis.
    """
    
    def __init__(self, storage_path: Optional[Path] = None):
        """Initialize metrics collector.
        
        Args:
            storage_path: Path to metrics storage file. Defaults to 'data/metrics.json'
        """
        self.storage_path = storage_path or Path("data/metrics.json")
        self.storage_path.parent.mkdir(parents=True, exist_ok=True)
        self._metrics: List[Metric] = []
        self._load_metrics()
    
    def _load_metrics(self) -> None:
        """Load existing metrics from storage."""
        if self.storage_path.exists():
            try:
                with open(self.storage_path, 'r') as f:
                    data = json.load(f)
                    self._metrics = [Metric.from_dict(m) for m in data]
            except (json.JSONDecodeError, KeyError):
                # If file is corrupted, start fresh
                self._metrics = []
    
    def _save_metrics(self) -> None:
        """Save metrics to storage."""
        with open(self.storage_path, 'w') as f:
            data = [m.to_dict() for m in self._metrics]
            json.dump(data, f, indent=2)
    
    def collect(self, name: str, value: Any, tags: Optional[Dict[str, str]] = None) -> None:
        """Collect a metric data point.
        
        Args:
            name: Metric name (e.g., 'workflow.execution_time')
            value: Metric value
            tags: Optional metadata tags for filtering
        
        Example:
            >>> collector = MetricsCollector()
            >>> collector.collect('workflow.execution_time', 45.2, {'workflow': 'test'})
        """
        metric = Metric(
            name=name,
            value=value,
            timestamp=datetime.now(),
            tags=tags
        )
        self._metrics.append(metric)
        self._save_metrics()
    
    def query_by_name(self, name: str) -> List[Metric]:
        """Query metrics by name.
        
        Args:
            name: Metric name to search for
        
        Returns:
            List of matching metrics
        """
        return [m for m in self._metrics if m.name == name]
    
    def query_by_time_range(
        self,
        start: datetime,
        end: Optional[datetime] = None
    ) -> List[Metric]:
        """Query metrics by time range.
        
        Args:
            start: Start of time range
            end: End of time range (defaults to now)
        
        Returns:
            List of metrics within the time range
        """
        end = end or datetime.now()
        return [
            m for m in self._metrics
            if start <= m.timestamp <= end
        ]
    
    def query_by_value(
        self,
        min_value: Optional[float] = None,
        max_value: Optional[float] = None
    ) -> List[Metric]:
        """Query metrics by value range.
        
        Args:
            min_value: Minimum value (inclusive)
            max_value: Maximum value (inclusive)
        
        Returns:
            List of metrics within the value range
        """
        results = []
        for m in self._metrics:
            try:
                value = float(m.value)
                if min_value is not None and value < min_value:
                    continue
                if max_value is not None and value > max_value:
                    continue
                results.append(m)
            except (ValueError, TypeError):
                # Skip non-numeric values
                continue
        return results
    
    def query(
        self,
        name: Optional[str] = None,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None,
        min_value: Optional[float] = None,
        max_value: Optional[float] = None,
        tags: Optional[Dict[str, str]] = None
    ) -> List[Metric]:
        """Query metrics with multiple filters.
        
        Args:
            name: Filter by metric name
            start_time: Filter by start time
            end_time: Filter by end time
            min_value: Filter by minimum value
            max_value: Filter by maximum value
            tags: Filter by tags (all tags must match)
        
        Returns:
            List of metrics matching all filters
        """
        results = self._metrics
        
        if name:
            results = [m for m in results if m.name == name]
        
        if start_time:
            results = [m for m in results if m.timestamp >= start_time]
        
        if end_time:
            results = [m for m in results if m.timestamp <= end_time]
        
        if min_value is not None or max_value is not None:
            filtered = []
            for m in results:
                try:
                    value = float(m.value)
                    if min_value is not None and value < min_value:
                        continue
                    if max_value is not None and value > max_value:
                        continue
                    filtered.append(m)
                except (ValueError, TypeError):
                    continue
            results = filtered
        
        if tags:
            results = [
                m for m in results
                if m.tags and all(m.tags.get(k) == v for k, v in tags.items())
            ]
        
        return results
    
    def get_all_metrics(self) -> List[Metric]:
        """Get all collected metrics.
        
        Returns:
            List of all metrics
        """
        return self._metrics.copy()
    
    def clear_metrics(self) -> None:
        """Clear all metrics. Useful for testing."""
        self._metrics = []
        self._save_metrics()
