"""
ModelOptimizer Integration Layer for API Model Management

This module provides the integration layer between the API Model Management system
and the existing ModelOptimizer. It extends ModelAssignment with API details,
implements performance feedback, failover coordination, and model selection coordination.

Requirements: 13.1, 13.2, 13.3, 13.4, 13.5
"""

import logging
from typing import Optional, Dict, Any, Tuple
from dataclasses import dataclass, field
from datetime import datetime

from ..models.agent import AgentType, AgentTask, ModelAssignment, TaskPriority
from .models import (
    ModelSelection, SelectionConstraints, ModelResponse, FailoverReason,
    PerformanceMetrics as APIPerformanceMetrics
)
from .selector import ModelSelector
from .failover_manager import FailoverManager
from .performance_monitor import PerformanceMonitor
from .cost_tracker import CostTracker
from .exceptions import APIModelError

logger = logging.getLogger(__name__)


@dataclass
class APIModelAssignment:
    """
    Extended ModelAssignment with API-specific details.
    
    This class extends the base ModelAssignment with API model management
    information including selected model ID, alternatives, and selection metadata.
    
    Validates: Requirement 13.1
    """
    base_assignment: ModelAssignment
    selected_model_id: str
    model_selection: ModelSelection
    api_provider: str
    api_endpoint: Optional[str] = None
    selection_timestamp: datetime = field(default_factory=datetime.now)
    
    def get_effective_model(self, prefer_fallback: bool = False) -> str:
        """
        Get the effective model to use.
        
        Returns the API-selected model ID, maintaining compatibility with
        the base ModelAssignment interface.
        """
        return self.selected_model_id
    
    @property
    def role_type(self) -> AgentType:
        """Get role type from base assignment."""
        return self.base_assignment.role_type
    
    @property
    def model_tier(self):
        """Get model tier from base assignment."""
        return self.base_assignment.model_tier
    
    @property
    def max_concurrent_instances(self) -> int:
        """Get max concurrent instances from base assignment."""
        return self.base_assignment.max_concurrent_instances
    
    @property
    def cost_per_token(self) -> float:
        """Get cost per token from base assignment."""
        return self.base_assignment.cost_per_token


class ModelOptimizerIntegration:
    """
    Integration layer between API Model Management and ModelOptimizer.
    
    This class coordinates between the existing ModelOptimizer and the new
    API Model Management system, providing:
    - Model selection coordination
    - Performance feedback to ModelOptimizer
    - Failover event reporting
    - Backward compatibility with existing interfaces
    
    Validates: Requirements 13.1, 13.2, 13.3, 13.4, 13.5
    """
    
    def __init__(
        self,
        model_selector: ModelSelector,
        failover_manager: FailoverManager,
        performance_monitor: PerformanceMonitor,
        cost_tracker: CostTracker
    ):
        """
        Initialize the ModelOptimizer integration layer.
        
        Args:
            model_selector: ModelSelector for intelligent model selection
            failover_manager: FailoverManager for handling failovers
            performance_monitor: PerformanceMonitor for tracking performance
            cost_tracker: CostTracker for tracking costs
        """
        self.model_selector = model_selector
        self.failover_manager = failover_manager
        self.performance_monitor = performance_monitor
        self.cost_tracker = cost_tracker
        
        # Cache for model assignments
        self._assignment_cache: Dict[str, APIModelAssignment] = {}
        
        logger.info("ModelOptimizerIntegration initialized")
    
    async def select_model_for_agent(
        self,
        agent_type: AgentType,
        task: AgentTask,
        base_assignment: ModelAssignment,
        constraints: Optional[SelectionConstraints] = None
    ) -> APIModelAssignment:
        """
        Select optimal model for an agent using API Model Management.
        
        This method integrates with ModelOptimizer's model selection logic,
        using the API Model Management system to select the best model based
        on real-time availability, performance, and cost data.
        
        Args:
            agent_type: Type of agent requesting model assignment
            task: Task to be executed
            base_assignment: Base ModelAssignment from ModelOptimizer
            constraints: Optional selection constraints
            
        Returns:
            APIModelAssignment with selected model and metadata
            
        Raises:
            APIModelError: If model selection fails
            
        Validates: Requirements 13.1, 13.2
        """
        logger.info(
            f"Selecting API model for {agent_type.value} agent, task {task.id}"
        )
        
        try:
            # Use API Model Management to select optimal model
            model_selection = await self.model_selector.select_model(
                task=task,
                agent_type=agent_type.value,
                constraints=constraints
            )
            
            # Create extended assignment
            api_assignment = APIModelAssignment(
                base_assignment=base_assignment,
                selected_model_id=model_selection.model_id,
                model_selection=model_selection,
                api_provider=model_selection.model_metadata.provider,
                api_endpoint=None  # Will be set by API client
            )
            
            # Cache the assignment
            cache_key = f"{agent_type.value}_{task.id}"
            self._assignment_cache[cache_key] = api_assignment
            
            logger.info(
                f"Selected model {model_selection.model_id} for {agent_type.value} "
                f"(score={model_selection.suitability_score:.3f})"
            )
            
            return api_assignment
            
        except Exception as e:
            logger.error(
                f"Failed to select API model for {agent_type.value}: {e}"
            )
            # Fall back to base assignment
            return self._create_fallback_assignment(base_assignment, task)
    
    def _create_fallback_assignment(
        self,
        base_assignment: ModelAssignment,
        task: AgentTask
    ) -> APIModelAssignment:
        """
        Create fallback assignment when API selection fails.
        
        Args:
            base_assignment: Base ModelAssignment to use
            task: Task being executed
            
        Returns:
            APIModelAssignment using fallback model
        """
        from .models import ModelMetadata, RateLimits
        
        # Create minimal model selection for fallback
        fallback_metadata = ModelMetadata(
            id=base_assignment.fallback_model,
            provider="unknown",
            name=base_assignment.fallback_model,
            capabilities=["text-generation"],
            cost_per_1k_input_tokens=base_assignment.cost_per_token,
            cost_per_1k_output_tokens=base_assignment.cost_per_token,
            rate_limits=RateLimits(
                requests_per_minute=100,
                tokens_per_minute=100000
            ),
            context_window=8000,
            average_response_time_ms=2000.0,
            enabled=True
        )
        
        fallback_selection = ModelSelection(
            model_id=base_assignment.fallback_model,
            model_metadata=fallback_metadata,
            suitability_score=0.5,
            alternatives=[],
            selection_reason="Fallback due to API selection failure"
        )
        
        return APIModelAssignment(
            base_assignment=base_assignment,
            selected_model_id=base_assignment.fallback_model,
            model_selection=fallback_selection,
            api_provider="unknown"
        )
    
    async def report_performance_to_optimizer(
        self,
        agent_type: AgentType,
        task_id: str,
        model_id: str,
        performance_data: Dict[str, Any]
    ) -> None:
        """
        Report performance data to ModelOptimizer.
        
        This method provides performance feedback from API model execution
        to the ModelOptimizer for optimization decisions.
        
        Args:
            agent_type: Type of agent that executed the task
            task_id: ID of the executed task
            model_id: ID of the model that was used
            performance_data: Performance metrics from execution
            
        Validates: Requirements 13.2, 13.4
        """
        logger.debug(
            f"Reporting performance to optimizer: model={model_id}, "
            f"task={task_id}, agent={agent_type.value}"
        )
        
        try:
            # Extract performance metrics
            success = performance_data.get('success', True)
            latency_ms = performance_data.get('latency_ms', 0.0)
            quality_score = performance_data.get('quality_score', 1.0)
            cost = performance_data.get('cost', 0.0)
            
            # Record performance in API performance monitor
            await self.performance_monitor.record_performance(
                model_id=model_id,
                agent_type=agent_type.value,
                latency_ms=latency_ms,
                success=success,
                quality_score=quality_score,
                task_id=task_id
            )
            
            # Record cost in cost tracker
            if cost > 0:
                input_tokens = performance_data.get('input_tokens', 0)
                output_tokens = performance_data.get('output_tokens', 0)
                
                await self.cost_tracker.record_cost(
                    model_id=model_id,
                    agent_type=agent_type.value,
                    input_tokens=input_tokens,
                    output_tokens=output_tokens,
                    cost=cost,
                    task_id=task_id
                )
            
            logger.info(
                f"Performance reported: model={model_id}, success={success}, "
                f"latency={latency_ms:.2f}ms, quality={quality_score:.2f}"
            )
            
        except Exception as e:
            logger.error(
                f"Failed to report performance to optimizer: {e}"
            )
    
    async def report_failover_event(
        self,
        agent_type: AgentType,
        task_id: str,
        original_model: str,
        alternative_model: str,
        reason: FailoverReason
    ) -> None:
        """
        Report failover event to ModelOptimizer.
        
        This method coordinates failover events with the ModelOptimizer,
        ensuring that the optimizer is aware of model availability issues
        and can adjust its selection strategy accordingly.
        
        Args:
            agent_type: Type of agent experiencing failover
            task_id: ID of the task being executed
            original_model: Original model that failed
            alternative_model: Alternative model selected
            reason: Reason for failover
            
        Validates: Requirements 13.3
        """
        logger.info(
            f"Reporting failover event: {original_model} -> {alternative_model} "
            f"(reason={reason.value}, task={task_id}, agent={agent_type.value})"
        )
        
        try:
            # Record failover event in failover manager
            await self.failover_manager.record_failover(
                original_model=original_model,
                alternative_model=alternative_model,
                reason=reason,
                task_id=task_id
            )
            
            # Log for ModelOptimizer awareness
            logger.warning(
                f"Failover occurred for {agent_type.value}: "
                f"{original_model} -> {alternative_model} ({reason.value})"
            )
            
        except Exception as e:
            logger.error(
                f"Failed to report failover event: {e}"
            )
    
    async def get_performance_summary(
        self,
        agent_type: Optional[AgentType] = None,
        window_hours: int = 24
    ) -> Dict[str, Any]:
        """
        Get performance summary for ModelOptimizer.
        
        Provides aggregated performance data that ModelOptimizer can use
        for optimization decisions.
        
        Args:
            agent_type: Optional agent type to filter by
            window_hours: Time window for performance data
            
        Returns:
            Dictionary containing performance summary
            
        Validates: Requirement 13.4
        """
        try:
            # Get all models from performance monitor
            # This is a simplified implementation - in production, you'd query
            # the performance monitor for all models
            summary = {
                'window_hours': window_hours,
                'agent_type': agent_type.value if agent_type else 'all',
                'models': {},
                'total_requests': 0,
                'total_cost': 0.0,
                'average_success_rate': 0.0
            }
            
            # Get cost summary
            from datetime import datetime, timedelta
            end_date = datetime.now()
            start_date = end_date - timedelta(hours=window_hours)
            
            cost_by_model = await self.cost_tracker.get_cost_by_model(
                start_date=start_date,
                end_date=end_date
            )
            
            summary['cost_by_model'] = cost_by_model
            summary['total_cost'] = sum(cost_by_model.values())
            
            logger.debug(
                f"Generated performance summary: {summary['total_requests']} requests, "
                f"${summary['total_cost']:.2f} cost"
            )
            
            return summary
            
        except Exception as e:
            logger.error(f"Failed to get performance summary: {e}")
            return {
                'error': str(e),
                'window_hours': window_hours,
                'agent_type': agent_type.value if agent_type else 'all'
            }
    
    def get_cached_assignment(
        self,
        agent_type: AgentType,
        task_id: str
    ) -> Optional[APIModelAssignment]:
        """
        Get cached model assignment for a task.
        
        Args:
            agent_type: Type of agent
            task_id: ID of the task
            
        Returns:
            Cached APIModelAssignment or None
        """
        cache_key = f"{agent_type.value}_{task_id}"
        return self._assignment_cache.get(cache_key)
    
    def clear_assignment_cache(self, agent_type: Optional[AgentType] = None):
        """
        Clear assignment cache.
        
        Args:
            agent_type: Optional agent type to clear (clears all if None)
        """
        if agent_type:
            # Clear only for specific agent type
            keys_to_remove = [
                k for k in self._assignment_cache.keys()
                if k.startswith(f"{agent_type.value}_")
            ]
            for key in keys_to_remove:
                del self._assignment_cache[key]
            logger.debug(f"Cleared {len(keys_to_remove)} cached assignments for {agent_type.value}")
        else:
            # Clear all
            count = len(self._assignment_cache)
            self._assignment_cache.clear()
            logger.debug(f"Cleared all {count} cached assignments")
