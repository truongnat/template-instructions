"""
Quality Metrics - Definitions and utilities for scoring metrics.

Part of Layer 2: Intelligence Layer.
"""

from dataclasses import dataclass
from enum import Enum
from typing import Dict, List


class MetricType(Enum):
    """Types of metrics."""
    INPUT = "input"
    OUTPUT = "output"
    PROCESS = "process"
    PERFORMANCE = "performance"


@dataclass
class MetricDefinition:
    """Definition of a quality metric."""
    name: str
    description: str
    metric_type: MetricType
    weight: float
    min_threshold: float = 0.0
    max_threshold: float = 1.0


class QualityMetrics:
    """Central registry of quality metrics."""

    # Input quality metrics
    INPUT_METRICS = [
        MetricDefinition("completeness", "Information completeness", MetricType.INPUT, 0.25),
        MetricDefinition("clarity", "Language clarity", MetricType.INPUT, 0.30),
        MetricDefinition("specificity", "Detail level", MetricType.INPUT, 0.25),
        MetricDefinition("actionability", "Action orientation", MetricType.INPUT, 0.20),
    ]

    # Output quality metrics
    OUTPUT_METRICS = [
        MetricDefinition("completeness", "Response completeness", MetricType.OUTPUT, 0.30),
        MetricDefinition("correctness", "Accuracy and error-free", MetricType.OUTPUT, 0.25),
        MetricDefinition("formatting", "Structure and readability", MetricType.OUTPUT, 0.20),
        MetricDefinition("usefulness", "Direct applicability", MetricType.OUTPUT, 0.25),
    ]

    # Process quality metrics  
    PROCESS_METRICS = [
        MetricDefinition("compliance", "Rule compliance", MetricType.PROCESS, 0.30),
        MetricDefinition("efficiency", "Process efficiency", MetricType.PROCESS, 0.25),
        MetricDefinition("documentation", "Documentation quality", MetricType.PROCESS, 0.25),
        MetricDefinition("traceability", "Audit trail completeness", MetricType.PROCESS, 0.20),
    ]

    @classmethod
    def get_metrics(cls, metric_type: MetricType) -> List[MetricDefinition]:
        """Get metrics by type."""
        if metric_type == MetricType.INPUT:
            return cls.INPUT_METRICS
        elif metric_type == MetricType.OUTPUT:
            return cls.OUTPUT_METRICS
        elif metric_type == MetricType.PROCESS:
            return cls.PROCESS_METRICS
        else:
            return []

    @classmethod
    def calculate_weighted_score(cls, scores: Dict[str, float], metric_type: MetricType) -> float:
        """Calculate weighted score from individual metric scores."""
        metrics = cls.get_metrics(metric_type)
        total_weight = sum(m.weight for m in metrics)
        
        weighted_sum = 0.0
        for metric in metrics:
            if metric.name in scores:
                weighted_sum += scores[metric.name] * metric.weight
        
        return weighted_sum / total_weight if total_weight > 0 else 0.0

    @classmethod
    def get_quality_grade(cls, score: float) -> str:
        """Convert score to letter grade."""
        if score >= 0.90:
            return "A+"
        elif score >= 0.85:
            return "A"
        elif score >= 0.80:
            return "A-"
        elif score >= 0.75:
            return "B+"
        elif score >= 0.70:
            return "B"
        elif score >= 0.65:
            return "B-"
        elif score >= 0.60:
            return "C+"
        elif score >= 0.55:
            return "C"
        elif score >= 0.50:
            return "C-"
        elif score >= 0.40:
            return "D"
        else:
            return "F"

