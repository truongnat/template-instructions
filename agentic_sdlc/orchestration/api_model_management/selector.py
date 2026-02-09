"""
Model Selector for API Model Management system.

This module provides intelligent model selection based on task requirements,
cost constraints, real-time availability, and historical performance data.
"""

import logging
from typing import Optional, List, Tuple

from .models import (
    ModelMetadata,
    ModelSelection,
    SelectionConstraints,
)
from .registry import ModelRegistry
from .health_checker import HealthChecker
from .rate_limiter import RateLimiter
from .performance_monitor import PerformanceMonitor
from .exceptions import APIModelError

# Import AgentTask and TaskPriority from orchestration models
try:
    from agentic_sdlc.orchestration.models.agent import AgentTask, TaskPriority
except ImportError:
    # Fallback for testing or standalone usage
    from dataclasses import dataclass, field
    from enum import Enum
    from typing import Any
    from datetime import datetime
    
    class TaskPriority(Enum):
        CRITICAL = 1
        HIGH = 2
        MEDIUM = 3
        LOW = 4
        BACKGROUND = 5
    
    @dataclass
    class AgentTask:
        id: str
        type: str = ""
        priority: TaskPriority = TaskPriority.MEDIUM
        requirements: List[Any] = field(default_factory=list)


logger = logging.getLogger(__name__)


class ModelSelector:
    """
    Intelligent model selection based on task requirements and constraints.
    
    The ModelSelector evaluates available models using multiple factors:
    - Task requirements and required capabilities
    - Cost efficiency
    - Real-time availability (via HealthChecker)
    - Rate limit status (via RateLimiter)
    - Historical performance data (via PerformanceMonitor)
    
    Selection Algorithm:
    1. Filter models by required capabilities
    2. Filter out unavailable or rate-limited models
    3. Calculate suitability score for each model:
       - Capability match: 30%
       - Cost efficiency: 25%
       - Historical performance: 25%
       - Availability: 20%
    4. Apply task priority adjustments (CRITICAL/HIGH prioritize quality)
    5. Return highest-scoring model
    """
    
    def __init__(
        self,
        registry: ModelRegistry,
        health_checker: HealthChecker,
        rate_limiter: RateLimiter,
        performance_monitor: PerformanceMonitor
    ):
        """
        Initialize the Model Selector.
        
        Args:
            registry: ModelRegistry for accessing model metadata
            health_checker: HealthChecker for checking model availability
            rate_limiter: RateLimiter for checking rate limit status
            performance_monitor: PerformanceMonitor for accessing performance data
        """
        self.registry = registry
        self.health_checker = health_checker
        self.rate_limiter = rate_limiter
        self.performance_monitor = performance_monitor
        
        logger.info("ModelSelector initialized")
    
    async def select_model(
        self,
        task: AgentTask,
        agent_type: str,
        constraints: Optional[SelectionConstraints] = None
    ) -> ModelSelection:
        """
        Select optimal model for a task.
        
        Evaluates all available models based on task requirements, constraints,
        availability, and performance data, then returns the best match.
        
        Args:
            task: AgentTask containing task details and requirements
            agent_type: Type of agent requesting the model
            constraints: Optional SelectionConstraints for filtering models
            
        Returns:
            ModelSelection with selected model and alternatives
            
        Raises:
            APIModelError: If no suitable model is found
            
        Validates: Requirements 2.1, 2.2, 2.3, 2.4, 2.5
        """
        logger.info(
            f"Selecting model for task {task.id} (agent_type={agent_type}, "
            f"priority={task.priority.name})"
        )
        
        # Get all models from registry
        all_models = list(self.registry._models.values())
        
        # Filter by enabled status
        enabled_models = [m for m in all_models if m.enabled]
        
        if not enabled_models:
            raise APIModelError(
                "No enabled models available in registry",
                task_id=task.id
            )
        
        # Apply constraints if provided
        if constraints:
            enabled_models = self._apply_constraints(enabled_models, constraints)
        
        # Filter by required capabilities
        required_capabilities = self._extract_required_capabilities(task, constraints)
        capable_models = self._filter_by_capabilities(
            enabled_models,
            required_capabilities
        )
        
        if not capable_models:
            raise APIModelError(
                f"No models found with required capabilities: {required_capabilities}",
                task_id=task.id
            )
        
        # Filter out unavailable or rate-limited models
        available_models = await self._filter_by_availability(capable_models)
        
        if not available_models:
            # No models available - try to find alternatives from capable models
            logger.warning(
                f"No available models for task {task.id}, "
                f"attempting to find alternatives"
            )
            # Return the first capable model even if unavailable
            # (failover manager will handle this)
            fallback_model = capable_models[0]
            return ModelSelection(
                model_id=fallback_model.id,
                model_metadata=fallback_model,
                suitability_score=0.0,
                alternatives=[m.id for m in capable_models[1:3]],
                selection_reason="No available models - using fallback"
            )
        
        # Rank models by suitability score
        ranked_models = await self.rank_models(available_models, task, agent_type)
        
        if not ranked_models:
            raise APIModelError(
                "Failed to rank models - no suitable models found",
                task_id=task.id
            )
        
        # Select the highest-scoring model
        best_model, best_score = ranked_models[0]
        alternatives = [m.id for m, _ in ranked_models[1:3]]
        
        selection_reason = self._generate_selection_reason(
            best_model,
            best_score,
            task.priority,
            required_capabilities
        )
        
        logger.info(
            f"Selected model {best_model.id} for task {task.id} "
            f"(score={best_score:.3f}, reason={selection_reason})"
        )
        
        return ModelSelection(
            model_id=best_model.id,
            model_metadata=best_model,
            suitability_score=best_score,
            alternatives=alternatives,
            selection_reason=selection_reason
        )
    
    def _extract_required_capabilities(
        self,
        task: AgentTask,
        constraints: Optional[SelectionConstraints]
    ) -> List[str]:
        """
        Extract required capabilities from task and constraints.
        
        Args:
            task: AgentTask to analyze
            constraints: Optional SelectionConstraints
            
        Returns:
            List of required capability strings
        """
        capabilities = []
        
        # Add capabilities from constraints
        if constraints and constraints.required_capabilities:
            capabilities.extend(constraints.required_capabilities)
        
        # If no explicit capabilities, infer from task type
        if not capabilities and task.type:
            # Map task types to capabilities
            task_type_lower = task.type.lower()
            if "code" in task_type_lower or "implement" in task_type_lower:
                capabilities.append("code-generation")
            elif "analysis" in task_type_lower or "review" in task_type_lower:
                capabilities.append("analysis")
            else:
                # Default to text generation
                capabilities.append("text-generation")
        
        # If still no capabilities, default to text-generation
        if not capabilities:
            capabilities.append("text-generation")
        
        return capabilities
    
    def _apply_constraints(
        self,
        models: List[ModelMetadata],
        constraints: SelectionConstraints
    ) -> List[ModelMetadata]:
        """
        Apply selection constraints to filter models.
        
        Args:
            models: List of models to filter
            constraints: SelectionConstraints to apply
            
        Returns:
            Filtered list of models
        """
        filtered = models
        
        # Filter by excluded providers
        if constraints.excluded_providers:
            filtered = [
                m for m in filtered
                if m.provider not in constraints.excluded_providers
            ]
        
        # Filter by max latency
        if constraints.max_latency_ms is not None:
            filtered = [
                m for m in filtered
                if m.average_response_time_ms <= constraints.max_latency_ms
            ]
        
        return filtered
    
    def _filter_by_capabilities(
        self,
        models: List[ModelMetadata],
        required_capabilities: List[str]
    ) -> List[ModelMetadata]:
        """
        Filter models by required capabilities.
        
        Args:
            models: List of models to filter
            required_capabilities: List of required capability strings
            
        Returns:
            Models that support all required capabilities
        """
        if not required_capabilities:
            return models
        
        capable_models = []
        for model in models:
            # Check if model has all required capabilities
            has_all_capabilities = all(
                cap in model.capabilities
                for cap in required_capabilities
            )
            if has_all_capabilities:
                capable_models.append(model)
        
        return capable_models
    
    async def _filter_by_availability(
        self,
        models: List[ModelMetadata]
    ) -> List[ModelMetadata]:
        """
        Filter out unavailable or rate-limited models.
        
        Args:
            models: List of models to filter
            
        Returns:
            Models that are available and not rate-limited
        """
        available_models = []
        
        for model in models:
            # Check health status
            is_healthy = self.health_checker.is_model_available(model.id)
            
            # Check rate limit status
            is_rate_limited = self.rate_limiter.is_rate_limited(model.id)
            
            if is_healthy and not is_rate_limited:
                available_models.append(model)
            else:
                logger.debug(
                    f"Model {model.id} filtered out: "
                    f"healthy={is_healthy}, rate_limited={is_rate_limited}"
                )
        
        return available_models
    
    async def rank_models(
        self,
        models: List[ModelMetadata],
        task: AgentTask,
        agent_type: str
    ) -> List[Tuple[ModelMetadata, float]]:
        """
        Rank models by suitability score.
        
        Calculates a suitability score for each model based on:
        - Capability match: 30%
        - Cost efficiency: 25%
        - Historical performance: 25%
        - Availability: 20%
        
        Applies priority-based adjustments for CRITICAL/HIGH priority tasks.
        
        Args:
            models: List of models to rank
            task: AgentTask for context
            agent_type: Type of agent requesting the model
            
        Returns:
            List of (ModelMetadata, score) tuples sorted by score (highest first)
        """
        scored_models = []
        
        for model in models:
            # Get performance data for this model
            try:
                performance_data = await self.performance_monitor.get_model_performance(
                    model.id,
                    window_hours=24
                )
            except Exception as e:
                logger.warning(
                    f"Failed to get performance data for {model.id}: {e}"
                )
                performance_data = None
            
            # Calculate suitability score
            score = self.calculate_suitability_score(
                model,
                task,
                performance_data
            )
            
            scored_models.append((model, score))
        
        # Sort by score (highest first)
        scored_models.sort(key=lambda x: x[1], reverse=True)
        
        return scored_models
    
    def calculate_suitability_score(
        self,
        model: ModelMetadata,
        task: AgentTask,
        performance_data: Optional[any] = None
    ) -> float:
        """
        Calculate suitability score for a model.
        
        Scoring breakdown:
        - Capability match: 30% (1.0 if all capabilities match)
        - Cost efficiency: 25% (normalized inverse cost)
        - Historical performance: 25% (success rate + quality score)
        - Availability: 20% (1.0 if available, 0.0 if not)
        
        Priority adjustments:
        - CRITICAL/HIGH: Increase performance weight, decrease cost weight
        - MEDIUM/LOW: Balanced weights
        - BACKGROUND: Increase cost weight, decrease performance weight
        
        Args:
            model: ModelMetadata to score
            task: AgentTask for context
            performance_data: Optional PerformanceMetrics from PerformanceMonitor
            
        Returns:
            Suitability score (0.0 to 1.0)
        """
        # Base weights
        capability_weight = 0.30
        cost_weight = 0.25
        performance_weight = 0.25
        availability_weight = 0.20
        
        # Adjust weights based on task priority
        if task.priority in (TaskPriority.CRITICAL, TaskPriority.HIGH):
            # Prioritize quality over cost
            performance_weight = 0.35
            cost_weight = 0.15
        elif task.priority == TaskPriority.BACKGROUND:
            # Prioritize cost over quality
            cost_weight = 0.35
            performance_weight = 0.15
        
        # Calculate component scores
        
        # 1. Capability score (always 1.0 if we got here, since we filtered)
        capability_score = 1.0
        
        # 2. Cost efficiency score (inverse normalized cost)
        # Lower cost = higher score
        avg_cost = (
            model.cost_per_1k_input_tokens + model.cost_per_1k_output_tokens
        ) / 2
        # Normalize to 0-1 range (assuming max cost of $0.10 per 1k tokens)
        max_cost = 0.10
        cost_score = max(0.0, 1.0 - (avg_cost / max_cost))
        
        # 3. Performance score (from historical data)
        if performance_data and performance_data.total_requests > 0:
            # Combine success rate and quality score
            success_component = performance_data.success_rate
            quality_component = performance_data.average_quality_score
            performance_score = (success_component + quality_component) / 2
        else:
            # No performance data - use neutral score
            performance_score = 0.7
        
        # 4. Availability score
        is_available = self.health_checker.is_model_available(model.id)
        is_rate_limited = self.rate_limiter.is_rate_limited(model.id)
        
        if is_available and not is_rate_limited:
            availability_score = 1.0
        elif is_available:
            # Available but rate-limited
            availability_score = 0.3
        else:
            # Not available
            availability_score = 0.0
        
        # Calculate weighted total
        total_score = (
            capability_score * capability_weight +
            cost_score * cost_weight +
            performance_score * performance_weight +
            availability_score * availability_weight
        )
        
        logger.debug(
            f"Suitability score for {model.id}: {total_score:.3f} "
            f"(capability={capability_score:.2f}, cost={cost_score:.2f}, "
            f"performance={performance_score:.2f}, availability={availability_score:.2f})"
        )
        
        return total_score
    
    def _generate_selection_reason(
        self,
        model: ModelMetadata,
        score: float,
        priority: TaskPriority,
        required_capabilities: List[str]
    ) -> str:
        """
        Generate human-readable selection reason.
        
        Args:
            model: Selected ModelMetadata
            score: Suitability score
            priority: Task priority
            required_capabilities: Required capabilities
            
        Returns:
            Selection reason string
        """
        reasons = []
        
        # Add capability match
        reasons.append(f"matches capabilities {required_capabilities}")
        
        # Add priority consideration
        if priority in (TaskPriority.CRITICAL, TaskPriority.HIGH):
            reasons.append("prioritizes quality for high-priority task")
        elif priority == TaskPriority.BACKGROUND:
            reasons.append("optimizes cost for background task")
        
        # Add score
        reasons.append(f"suitability score {score:.3f}")
        
        return ", ".join(reasons)
