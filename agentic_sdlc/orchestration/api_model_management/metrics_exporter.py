"""
Metrics export interface for API Model Management system.

This module provides a comprehensive metrics export interface that aggregates
data from CostTracker, PerformanceMonitor, and other components to provide
real-time metrics in JSON format with filtering capabilities.
"""

import json
import logging
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, Any, Optional, List

from .cost_tracker import CostTracker
from .performance_monitor import PerformanceMonitor
from .exceptions import APIModelError


logger = logging.getLogger(__name__)


class MetricsExporter:
    """
    Exports comprehensive metrics from the API Model Management system.
    
    Responsibilities:
    - Query metrics from CostTracker and PerformanceMonitor
    - Format metrics as JSON
    - Filter metrics by time range, model, provider, agent type
    - Calculate derived metrics (e.g., cost per successful request)
    - Provide real-time metric updates
    
    Validates: Requirements 17.1, 17.2, 17.3, 17.4, 17.5
    """
    
    def __init__(
        self,
        cost_tracker: CostTracker,
        performance_monitor: PerformanceMonitor,
        model_registry: Optional[Dict[str, str]] = None
    ):
        """
        Initialize metrics exporter.
        
        Args:
            cost_tracker: CostTracker instance for cost metrics
            performance_monitor: PerformanceMonitor instance for performance metrics
            model_registry: Optional mapping of model_id to provider
        """
        self.cost_tracker = cost_tracker
        self.performance_monitor = performance_monitor
        self.model_registry = model_registry or {}
        logger.info("Initialized MetricsExporter")
    
    async def export_metrics(
        self,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        model_id: Optional[str] = None,
        provider: Optional[str] = None,
        agent_type: Optional[str] = None,
        window_hours: int = 24
    ) -> str:
        """
        Export comprehensive metrics in JSON format.
        
        Args:
            start_date: Start of time period (default: 24 hours ago)
            end_date: End of time period (default: now)
            model_id: Filter by specific model ID
            provider: Filter by provider
            agent_type: Filter by agent type
            window_hours: Time window for rolling metrics (default: 24)
            
        Returns:
            JSON string with all requested metrics
            
        Validates: Requirements 17.1, 17.2, 17.3
        """
        try:
            # Set default time range
            if end_date is None:
                end_date = datetime.now()
            if start_date is None:
                start_date = end_date - timedelta(hours=window_hours)
            
            # Gather all metrics
            metrics = await self._gather_metrics(
                start_date=start_date,
                end_date=end_date,
                model_id=model_id,
                provider=provider,
                agent_type=agent_type,
                window_hours=window_hours
            )
            
            # Convert to JSON
            json_output = json.dumps(metrics, indent=2, default=str)
            
            logger.info(
                f"Exported metrics for period {start_date} to {end_date}"
            )
            
            return json_output
            
        except Exception as e:
            logger.error(f"Failed to export metrics: {e}")
            raise APIModelError(f"Failed to export metrics: {e}")
    
    async def get_metrics_dict(
        self,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        model_id: Optional[str] = None,
        provider: Optional[str] = None,
        agent_type: Optional[str] = None,
        window_hours: int = 24
    ) -> Dict[str, Any]:
        """
        Get comprehensive metrics as a dictionary.
        
        Args:
            start_date: Start of time period (default: 24 hours ago)
            end_date: End of time period (default: now)
            model_id: Filter by specific model ID
            provider: Filter by provider
            agent_type: Filter by agent type
            window_hours: Time window for rolling metrics (default: 24)
            
        Returns:
            Dictionary with all requested metrics
            
        Validates: Requirements 17.1, 17.2, 17.3
        """
        # Set default time range
        if end_date is None:
            end_date = datetime.now()
        if start_date is None:
            start_date = end_date - timedelta(hours=window_hours)
        
        return await self._gather_metrics(
            start_date=start_date,
            end_date=end_date,
            model_id=model_id,
            provider=provider,
            agent_type=agent_type,
            window_hours=window_hours
        )
    
    async def _gather_metrics(
        self,
        start_date: datetime,
        end_date: datetime,
        model_id: Optional[str],
        provider: Optional[str],
        agent_type: Optional[str],
        window_hours: int
    ) -> Dict[str, Any]:
        """
        Gather all metrics from various sources.
        
        Args:
            start_date: Start of time period
            end_date: End of time period
            model_id: Filter by specific model ID
            provider: Filter by provider
            agent_type: Filter by agent type
            window_hours: Time window for rolling metrics
            
        Returns:
            Dictionary with all metrics
        """
        metrics = {
            "metadata": {
                "start_date": start_date.isoformat(),
                "end_date": end_date.isoformat(),
                "window_hours": window_hours,
                "generated_at": datetime.now().isoformat(),
                "filters": {
                    "model_id": model_id,
                    "provider": provider,
                    "agent_type": agent_type
                }
            }
        }
        
        # Get cost metrics
        cost_metrics = await self._get_cost_metrics(
            start_date, end_date, model_id, provider, agent_type
        )
        metrics["cost"] = cost_metrics
        
        # Get performance metrics
        performance_metrics = await self._get_performance_metrics(
            model_id, agent_type, window_hours
        )
        metrics["performance"] = performance_metrics
        
        # Calculate derived metrics
        derived_metrics = self._calculate_derived_metrics(
            cost_metrics, performance_metrics
        )
        metrics["derived"] = derived_metrics
        
        return metrics
    
    async def _get_cost_metrics(
        self,
        start_date: datetime,
        end_date: datetime,
        model_id: Optional[str],
        provider: Optional[str],
        agent_type: Optional[str]
    ) -> Dict[str, Any]:
        """
        Get cost metrics with filtering.
        
        Validates: Requirements 17.2, 17.3
        """
        # Get cost summary
        cost_summary = await self.cost_tracker.get_cost_summary(start_date, end_date)
        
        # Apply filters
        if model_id:
            cost_summary["cost_by_model"] = {
                k: v for k, v in cost_summary["cost_by_model"].items()
                if k == model_id
            }
        
        if agent_type:
            cost_summary["cost_by_agent_type"] = {
                k: v for k, v in cost_summary["cost_by_agent_type"].items()
                if k == agent_type
            }
        
        # Get cost by provider
        cost_by_provider = await self.cost_tracker.get_cost_by_provider(
            start_date, end_date, self.model_registry
        )
        
        if provider:
            cost_by_provider = {
                k: v for k, v in cost_by_provider.items()
                if k == provider
            }
        
        cost_summary["cost_by_provider"] = cost_by_provider
        
        # Get hourly breakdown
        try:
            hourly_costs = await self.cost_tracker.get_hourly_costs(start_date, end_date)
            cost_summary["hourly_breakdown"] = [
                {
                    "hour": hour.isoformat() if isinstance(hour, datetime) else str(hour),
                    "cost": cost
                }
                for hour, cost in hourly_costs
            ]
        except Exception as e:
            logger.warning(f"Failed to get hourly costs: {e}")
            cost_summary["hourly_breakdown"] = []
        
        # Get top expensive tasks
        top_tasks = await self.cost_tracker.get_top_expensive_tasks(
            start_date, end_date, limit=10
        )
        cost_summary["top_expensive_tasks"] = [
            {"task_id": task_id, "model_id": mid, "cost": cost}
            for task_id, mid, cost in top_tasks
        ]
        
        # Get budget status
        budget_status = await self.cost_tracker.check_budget()
        cost_summary["budget_status"] = {
            "daily_budget": budget_status.daily_budget,
            "current_spend": budget_status.current_spend,
            "utilization_percent": budget_status.utilization_percent,
            "is_over_budget": budget_status.is_over_budget,
            "remaining_budget": budget_status.remaining_budget
        }
        
        return cost_summary
    
    async def _get_performance_metrics(
        self,
        model_id: Optional[str],
        agent_type: Optional[str],
        window_hours: int
    ) -> Dict[str, Any]:
        """
        Get performance metrics with filtering.
        
        Validates: Requirements 17.2, 17.3
        """
        performance_data = {}
        
        if model_id:
            # Get metrics for specific model
            metrics = await self.performance_monitor.get_model_performance(
                model_id, window_hours
            )
            performance_data["models"] = {
                model_id: self._format_performance_metrics(metrics)
            }
        elif agent_type:
            # Get metrics for all models used by agent type
            metrics_by_model = await self.performance_monitor.get_performance_by_agent_type(
                agent_type, window_hours
            )
            performance_data["models"] = {
                mid: self._format_performance_metrics(metrics)
                for mid, metrics in metrics_by_model.items()
            }
        else:
            # No specific filter - would need to get all models
            # For now, return empty dict (can be enhanced to get all models from registry)
            performance_data["models"] = {}
        
        return performance_data
    
    def _format_performance_metrics(self, metrics) -> Dict[str, Any]:
        """Format PerformanceMetrics as dictionary."""
        return {
            "window_hours": metrics.window_hours,
            "total_requests": metrics.total_requests,
            "successful_requests": metrics.successful_requests,
            "failed_requests": metrics.failed_requests,
            "success_rate": metrics.success_rate,
            "error_rate": 1.0 - metrics.success_rate,
            "latency": {
                "average_ms": metrics.average_latency_ms,
                "p50_ms": metrics.p50_latency_ms,
                "p95_ms": metrics.p95_latency_ms,
                "p99_ms": metrics.p99_latency_ms
            },
            "average_quality_score": metrics.average_quality_score
        }
    
    def _calculate_derived_metrics(
        self,
        cost_metrics: Dict[str, Any],
        performance_metrics: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Calculate derived metrics from base metrics.
        
        Validates: Requirements 17.4
        """
        derived = {}
        
        # Cost per successful request
        total_cost = cost_metrics.get("total_cost", 0.0)
        total_requests = cost_metrics.get("total_requests", 0)
        
        # Calculate success count from performance metrics
        total_successful = 0
        for model_metrics in performance_metrics.get("models", {}).values():
            total_successful += model_metrics.get("successful_requests", 0)
        
        # If we don't have performance data, estimate from cost data
        if total_successful == 0 and total_requests > 0:
            # Assume 90% success rate as default
            total_successful = int(total_requests * 0.9)
        
        derived["cost_per_successful_request"] = (
            total_cost / total_successful if total_successful > 0 else 0.0
        )
        
        # Cost per request (including failures)
        derived["cost_per_request"] = (
            total_cost / total_requests if total_requests > 0 else 0.0
        )
        
        # Average tokens per request
        total_input_tokens = cost_metrics.get("total_input_tokens", 0)
        total_output_tokens = cost_metrics.get("total_output_tokens", 0)
        
        derived["average_input_tokens_per_request"] = (
            total_input_tokens / total_requests if total_requests > 0 else 0.0
        )
        derived["average_output_tokens_per_request"] = (
            total_output_tokens / total_requests if total_requests > 0 else 0.0
        )
        derived["average_total_tokens_per_request"] = (
            (total_input_tokens + total_output_tokens) / total_requests 
            if total_requests > 0 else 0.0
        )
        
        # Cost efficiency by model (cost per successful request)
        cost_by_model = cost_metrics.get("cost_by_model", {})
        cost_efficiency_by_model = {}
        
        for model_id, model_cost in cost_by_model.items():
            model_perf = performance_metrics.get("models", {}).get(model_id)
            if model_perf:
                successful = model_perf.get("successful_requests", 0)
                cost_efficiency_by_model[model_id] = (
                    model_cost / successful if successful > 0 else 0.0
                )
        
        derived["cost_efficiency_by_model"] = cost_efficiency_by_model
        
        # Overall success rate (if we have performance data)
        if performance_metrics.get("models"):
            total_perf_requests = sum(
                m.get("total_requests", 0) 
                for m in performance_metrics["models"].values()
            )
            total_perf_successful = sum(
                m.get("successful_requests", 0)
                for m in performance_metrics["models"].values()
            )
            derived["overall_success_rate"] = (
                total_perf_successful / total_perf_requests 
                if total_perf_requests > 0 else 0.0
            )
            derived["overall_error_rate"] = 1.0 - derived["overall_success_rate"]
        
        return derived
    
    async def get_real_time_metrics(
        self,
        model_id: Optional[str] = None,
        window_minutes: int = 5
    ) -> Dict[str, Any]:
        """
        Get real-time metrics for the last N minutes.
        
        Args:
            model_id: Optional model ID to filter by
            window_minutes: Time window in minutes (default: 5)
            
        Returns:
            Dictionary with real-time metrics
            
        Validates: Requirements 17.5
        """
        end_date = datetime.now()
        start_date = end_date - timedelta(minutes=window_minutes)
        
        metrics = await self.get_metrics_dict(
            start_date=start_date,
            end_date=end_date,
            model_id=model_id,
            window_hours=window_minutes / 60.0
        )
        
        # Add real-time specific metadata
        metrics["metadata"]["real_time"] = True
        metrics["metadata"]["window_minutes"] = window_minutes
        
        logger.debug(
            f"Retrieved real-time metrics for last {window_minutes} minutes"
        )
        
        return metrics
    
    async def get_metrics_summary(self) -> Dict[str, Any]:
        """
        Get a high-level summary of current metrics.
        
        Returns:
            Dictionary with summary metrics
        """
        # Get last 24 hours
        end_date = datetime.now()
        start_date = end_date - timedelta(hours=24)
        
        # Get cost summary
        cost_summary = await self.cost_tracker.get_cost_summary(start_date, end_date)
        
        # Get budget status
        budget_status = await self.cost_tracker.check_budget()
        
        summary = {
            "period": "last_24_hours",
            "generated_at": datetime.now().isoformat(),
            "total_requests": cost_summary["total_requests"],
            "total_cost": cost_summary["total_cost"],
            "average_cost_per_request": cost_summary["average_cost_per_request"],
            "budget_utilization_percent": budget_status.utilization_percent,
            "is_over_budget": budget_status.is_over_budget,
            "top_models_by_cost": dict(
                sorted(
                    cost_summary["cost_by_model"].items(),
                    key=lambda x: x[1],
                    reverse=True
                )[:5]
            ),
            "top_agent_types_by_cost": dict(
                sorted(
                    cost_summary["cost_by_agent_type"].items(),
                    key=lambda x: x[1],
                    reverse=True
                )[:5]
            )
        }
        
        logger.info("Generated metrics summary")
        
        return summary
