"""
Performance monitoring for API Model Management system.

This module provides performance tracking and analysis for AI models including
latency monitoring, success rate tracking, quality score recording, and
performance degradation detection.
"""

import aiosqlite
import logging
from pathlib import Path
from datetime import datetime, timedelta
from typing import Optional, List, Dict, Any
from statistics import median

from .models import PerformanceMetrics, PerformanceDegradation
from .exceptions import APIModelError


logger = logging.getLogger(__name__)


class PerformanceMonitor:
    """
    Tracks and analyzes model performance metrics.
    
    Responsibilities:
    - Record latency per request
    - Track success/failure rates
    - Record quality scores
    - Calculate rolling averages
    - Detect performance degradation
    - Persist metrics to SQLite
    """
    
    def __init__(self, db_path: Path):
        """
        Initialize performance monitor.
        
        Args:
            db_path: Path to SQLite database file
        """
        self.db_path = db_path
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        logger.info(f"Initialized PerformanceMonitor with database at {db_path}")
    
    async def record_performance(
        self,
        model_id: str,
        agent_type: str,
        latency_ms: float,
        success: bool,
        quality_score: float,
        task_id: str
    ) -> None:
        """
        Record performance metrics for a request.
        
        Args:
            model_id: ID of the model used
            agent_type: Type of agent making the request
            latency_ms: Request latency in milliseconds
            success: Whether the request succeeded
            quality_score: Quality score of the response (0-1)
            task_id: ID of the task
            
        Validates: Requirements 11.1
        """
        try:
            async with aiosqlite.connect(self.db_path) as db:
                await db.execute("""
                    INSERT INTO performance_records 
                    (timestamp, model_id, agent_type, task_id, latency_ms, success, quality_score)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                """, (
                    datetime.now(),
                    model_id,
                    agent_type,
                    task_id,
                    latency_ms,
                    success,
                    quality_score
                ))
                await db.commit()
            
            logger.debug(
                f"Recorded performance for {model_id}: "
                f"latency={latency_ms}ms, success={success}, quality={quality_score}"
            )
        except Exception as e:
            logger.error(f"Failed to record performance for {model_id}: {e}")
            raise APIModelError(
                f"Failed to record performance: {e}",
                model_id=model_id,
                task_id=task_id
            )

    async def get_model_performance(
        self,
        model_id: str,
        window_hours: int = 24
    ) -> PerformanceMetrics:
        """
        Get performance metrics for a model over a time window.
        
        Args:
            model_id: ID of the model
            window_hours: Time window in hours (default: 24)
            
        Returns:
            PerformanceMetrics with aggregated statistics
            
        Validates: Requirements 11.2, 11.3
        """
        try:
            cutoff_time = datetime.now() - timedelta(hours=window_hours)
            
            async with aiosqlite.connect(self.db_path) as db:
                # Get all records within the time window
                cursor = await db.execute("""
                    SELECT latency_ms, success, quality_score
                    FROM performance_records
                    WHERE model_id = ? AND timestamp >= ?
                    ORDER BY timestamp DESC
                """, (model_id, cutoff_time))
                
                records = await cursor.fetchall()
            
            if not records:
                # Return empty metrics if no data
                return PerformanceMetrics(
                    model_id=model_id,
                    window_hours=window_hours,
                    total_requests=0,
                    successful_requests=0,
                    failed_requests=0,
                    success_rate=0.0,
                    average_latency_ms=0.0,
                    p50_latency_ms=0.0,
                    p95_latency_ms=0.0,
                    p99_latency_ms=0.0,
                    average_quality_score=0.0
                )
            
            # Extract data
            latencies = [r[0] for r in records]
            successes = [r[1] for r in records]
            quality_scores = [r[2] for r in records if r[2] is not None]
            
            # Calculate metrics
            total_requests = len(records)
            successful_requests = sum(successes)
            failed_requests = total_requests - successful_requests
            success_rate = successful_requests / total_requests if total_requests > 0 else 0.0
            
            # Calculate latency statistics
            average_latency_ms = sum(latencies) / len(latencies) if latencies else 0.0
            sorted_latencies = sorted(latencies)
            p50_latency_ms = self._calculate_percentile(sorted_latencies, 50)
            p95_latency_ms = self._calculate_percentile(sorted_latencies, 95)
            p99_latency_ms = self._calculate_percentile(sorted_latencies, 99)
            
            # Calculate average quality score
            average_quality_score = (
                sum(quality_scores) / len(quality_scores) 
                if quality_scores else 0.0
            )
            
            metrics = PerformanceMetrics(
                model_id=model_id,
                window_hours=window_hours,
                total_requests=total_requests,
                successful_requests=successful_requests,
                failed_requests=failed_requests,
                success_rate=success_rate,
                average_latency_ms=average_latency_ms,
                p50_latency_ms=p50_latency_ms,
                p95_latency_ms=p95_latency_ms,
                p99_latency_ms=p99_latency_ms,
                average_quality_score=average_quality_score
            )
            
            logger.debug(
                f"Retrieved performance metrics for {model_id}: "
                f"{total_requests} requests, {success_rate:.2%} success rate"
            )
            
            return metrics
            
        except Exception as e:
            logger.error(f"Failed to get performance metrics for {model_id}: {e}")
            raise APIModelError(
                f"Failed to get performance metrics: {e}",
                model_id=model_id
            )
    
    def _calculate_percentile(self, sorted_values: List[float], percentile: int) -> float:
        """
        Calculate percentile from sorted values.
        
        Args:
            sorted_values: List of values sorted in ascending order
            percentile: Percentile to calculate (0-100)
            
        Returns:
            Percentile value
        """
        if not sorted_values:
            return 0.0
        
        if len(sorted_values) == 1:
            return sorted_values[0]
        
        # Calculate index using linear interpolation
        index = (percentile / 100.0) * (len(sorted_values) - 1)
        lower_index = int(index)
        upper_index = min(lower_index + 1, len(sorted_values) - 1)
        
        # Interpolate between values
        weight = index - lower_index
        return sorted_values[lower_index] * (1 - weight) + sorted_values[upper_index] * weight
    
    async def detect_degradation(
        self,
        model_id: str,
        threshold: float = 0.8
    ) -> Optional[PerformanceDegradation]:
        """
        Detect performance degradation for a model.
        
        Checks if the model's success rate has fallen below the threshold
        over the monitoring window (24 hours).
        
        Args:
            model_id: ID of the model to check
            threshold: Success rate threshold (default: 0.8 = 80%)
            
        Returns:
            PerformanceDegradation if degradation detected, None otherwise
            
        Validates: Requirements 11.4
        """
        try:
            # Get performance metrics for the last 24 hours
            metrics = await self.get_model_performance(model_id, window_hours=24)
            
            # Check if success rate is below threshold
            if metrics.total_requests > 0 and metrics.success_rate < threshold:
                degradation = PerformanceDegradation(
                    model_id=model_id,
                    metric="success_rate",
                    current_value=metrics.success_rate,
                    threshold=threshold,
                    detected_at=datetime.now()
                )
                
                logger.warning(
                    f"Performance degradation detected for {model_id}: "
                    f"success_rate={metrics.success_rate:.2%} < threshold={threshold:.2%}"
                )
                
                return degradation
            
            return None
            
        except Exception as e:
            logger.error(f"Failed to detect degradation for {model_id}: {e}")
            # Don't raise exception - degradation detection is non-critical
            return None
    
    async def get_recent_quality_scores(
        self,
        model_id: str,
        limit: int = 10
    ) -> List[float]:
        """
        Get recent quality scores for a model.
        
        Args:
            model_id: ID of the model
            limit: Number of recent scores to retrieve
            
        Returns:
            List of quality scores (most recent first)
        """
        try:
            async with aiosqlite.connect(self.db_path) as db:
                cursor = await db.execute("""
                    SELECT quality_score
                    FROM performance_records
                    WHERE model_id = ? AND quality_score IS NOT NULL
                    ORDER BY timestamp DESC
                    LIMIT ?
                """, (model_id, limit))
                
                records = await cursor.fetchall()
            
            scores = [r[0] for r in records]
            
            logger.debug(f"Retrieved {len(scores)} recent quality scores for {model_id}")
            
            return scores
            
        except Exception as e:
            logger.error(f"Failed to get recent quality scores for {model_id}: {e}")
            return []
    
    async def get_performance_by_agent_type(
        self,
        agent_type: str,
        window_hours: int = 24
    ) -> Dict[str, PerformanceMetrics]:
        """
        Get performance metrics for all models used by a specific agent type.
        
        Args:
            agent_type: Type of agent
            window_hours: Time window in hours
            
        Returns:
            Dictionary mapping model_id to PerformanceMetrics
        """
        try:
            cutoff_time = datetime.now() - timedelta(hours=window_hours)
            
            async with aiosqlite.connect(self.db_path) as db:
                # Get distinct model IDs for this agent type
                cursor = await db.execute("""
                    SELECT DISTINCT model_id
                    FROM performance_records
                    WHERE agent_type = ? AND timestamp >= ?
                """, (agent_type, cutoff_time))
                
                model_ids = [r[0] for r in await cursor.fetchall()]
            
            # Get metrics for each model
            metrics_by_model = {}
            for model_id in model_ids:
                metrics = await self.get_model_performance(model_id, window_hours)
                metrics_by_model[model_id] = metrics
            
            logger.debug(
                f"Retrieved performance metrics for {len(model_ids)} models "
                f"used by agent type {agent_type}"
            )
            
            return metrics_by_model
            
        except Exception as e:
            logger.error(
                f"Failed to get performance by agent type {agent_type}: {e}"
            )
            return {}
    
    async def cleanup_old_records(self, days_to_keep: int = 90) -> int:
        """
        Clean up old performance records.
        
        Args:
            days_to_keep: Number of days of records to keep
            
        Returns:
            Number of records deleted
        """
        try:
            cutoff_time = datetime.now() - timedelta(days=days_to_keep)
            
            async with aiosqlite.connect(self.db_path) as db:
                cursor = await db.execute("""
                    DELETE FROM performance_records
                    WHERE timestamp < ?
                """, (cutoff_time,))
                
                deleted_count = cursor.rowcount
                await db.commit()
            
            logger.info(
                f"Cleaned up {deleted_count} old performance records "
                f"(kept last {days_to_keep} days)"
            )
            
            return deleted_count
            
        except Exception as e:
            logger.error(f"Failed to cleanup old performance records: {e}")
            return 0
