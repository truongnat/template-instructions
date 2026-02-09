"""
Model Optimizer for Multi-Agent Orchestration System

This module implements hierarchical model assignment logic based on agent roles and task complexity.
It provides cost optimization algorithms, resource allocation management, and performance monitoring
for the multi-agent orchestration system.

Requirements: 9.1, 9.2, 9.3, 9.4, 9.5
"""

import json
import logging
from datetime import datetime, timedelta
from enum import Enum
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass, field
from uuid import uuid4

from ..models import (
    AgentType, ModelTier, ModelAssignment, AgentTask, AgentInstance, 
    AgentPool, LoadBalancer, LoadMetrics, PerformanceMetrics,
    TaskPriority, DEFAULT_MODEL_ASSIGNMENTS
)
from .agent_pool import (
    EnhancedAgentPool, EnhancedLoadBalancer, LoadBalancingStrategy,
    AutoScalingPolicy, ScalingThresholds
)
from ..exceptions.model import (
    ModelOptimizationError, InsufficientResourcesError, 
    InvalidModelAssignmentError
)
from ..utils.logging import get_logger


class OptimizationStrategy(Enum):
    """Optimization strategies for model selection"""
    COST_OPTIMIZED = "cost_optimized"
    PERFORMANCE_OPTIMIZED = "performance_optimized"
    BALANCED = "balanced"
    QUALITY_FIRST = "quality_first"


class ResourceConstraint(Enum):
    """Types of resource constraints"""
    BUDGET = "budget"
    CONCURRENCY = "concurrency"
    LATENCY = "latency"
    THROUGHPUT = "throughput"


@dataclass
class CostMetrics:
    """Cost tracking metrics"""
    total_cost: float = 0.0
    cost_by_model: Dict[str, float] = field(default_factory=dict)
    cost_by_agent_type: Dict[AgentType, float] = field(default_factory=dict)
    tokens_consumed: int = 0
    requests_made: int = 0
    last_updated: datetime = field(default_factory=datetime.now)
    
    def add_cost(self, model: str, agent_type: AgentType, cost: float, tokens: int = 0):
        """Add cost data"""
        self.total_cost += cost
        self.cost_by_model[model] = self.cost_by_model.get(model, 0.0) + cost
        self.cost_by_agent_type[agent_type] = self.cost_by_agent_type.get(agent_type, 0.0) + cost
        self.tokens_consumed += tokens
        self.requests_made += 1
        self.last_updated = datetime.now()


@dataclass
class ResourceBudget:
    """Resource budget constraints"""
    max_daily_cost: float = 100.0
    max_concurrent_instances: int = 20
    max_tokens_per_hour: int = 1000000
    priority_allocation: Dict[TaskPriority, float] = field(default_factory=lambda: {
        TaskPriority.CRITICAL: 0.4,
        TaskPriority.HIGH: 0.3,
        TaskPriority.MEDIUM: 0.2,
        TaskPriority.LOW: 0.1,
        TaskPriority.BACKGROUND: 0.05
    })


@dataclass
class ModelPerformanceData:
    """Performance data for a specific model"""
    model_name: str
    agent_type: AgentType
    success_rate: float = 1.0
    average_latency: float = 0.0
    quality_score: float = 1.0
    cost_efficiency: float = 1.0
    total_requests: int = 0
    last_updated: datetime = field(default_factory=datetime.now)
    
    def update_performance(self, success: bool, latency: float, quality: float, cost: float):
        """Update performance metrics"""
        self.total_requests += 1
        
        # Update success rate
        if self.total_requests == 1:
            self.success_rate = 1.0 if success else 0.0
        else:
            self.success_rate = (
                (self.success_rate * (self.total_requests - 1) + (1.0 if success else 0.0)) 
                / self.total_requests
            )
        
        # Update average latency
        if self.total_requests == 1:
            self.average_latency = latency
        else:
            self.average_latency = (
                (self.average_latency * (self.total_requests - 1) + latency) 
                / self.total_requests
            )
        
        # Update quality score
        if self.total_requests == 1:
            self.quality_score = quality
        else:
            self.quality_score = (
                (self.quality_score * (self.total_requests - 1) + quality) 
                / self.total_requests
            )
        
        # Update cost efficiency (higher is better)
        if cost > 0:
            efficiency = (self.success_rate * self.quality_score) / cost
            if self.total_requests == 1:
                self.cost_efficiency = efficiency
            else:
                self.cost_efficiency = (
                    (self.cost_efficiency * (self.total_requests - 1) + efficiency) 
                    / self.total_requests
                )
        
        self.last_updated = datetime.now()


class ModelOptimizer:
    """
    Model Optimizer for hierarchical model assignment and resource management
    
    This class implements intelligent model selection based on:
    - Agent role hierarchy (Strategic/Operational/Research tiers)
    - Task complexity analysis
    - Cost optimization algorithms
    - Resource allocation management
    - Performance monitoring and adjustment
    """
    
    def __init__(
        self,
        model_assignments: Optional[List[ModelAssignment]] = None,
        budget: Optional[ResourceBudget] = None,
        strategy: OptimizationStrategy = OptimizationStrategy.BALANCED,
        data_file: Optional[Path] = None
    ):
        """
        Initialize the ModelOptimizer
        
        Args:
            model_assignments: Custom model assignments (uses defaults if None)
            budget: Resource budget constraints
            strategy: Optimization strategy
            data_file: File to persist optimization data
        """
        self.logger = get_logger(__name__)
        self.model_assignments = model_assignments or DEFAULT_MODEL_ASSIGNMENTS.copy()
        self.budget = budget or ResourceBudget()
        self.strategy = strategy
        self.data_file = data_file or Path(".model_optimizer_data.json")
        
        # Create lookup maps for efficient access
        self._assignment_by_type: Dict[AgentType, ModelAssignment] = {
            assignment.role_type: assignment for assignment in self.model_assignments
        }
        
        # Performance tracking
        self.performance_data: Dict[str, ModelPerformanceData] = {}
        self.cost_metrics = CostMetrics()
        
        # Agent pools for multi-instance management (enhanced)
        self.agent_pools: Dict[AgentType, EnhancedAgentPool] = {}
        
        # Load persisted data
        self._load_data()
        
        # Initialize agent pools
        self._initialize_agent_pools()
        
        self.logger.info(f"ModelOptimizer initialized with {len(self.model_assignments)} model assignments")
    
    def _initialize_agent_pools(self):
        """Initialize enhanced agent pools for each agent type"""
        for assignment in self.model_assignments:
            # Create enhanced load balancer with appropriate strategy
            load_balancer = EnhancedLoadBalancer(
                strategy=self._get_optimal_load_balancing_strategy(assignment.role_type),
                enable_health_checks=True,
                health_check_interval=30
            )
            
            # Create scaling thresholds based on role type
            scaling_thresholds = self._create_scaling_thresholds(assignment)
            
            # Create enhanced agent pool
            pool = EnhancedAgentPool(
                role_type=assignment.role_type,
                model_assignment=assignment,
                scaling_thresholds=scaling_thresholds,
                load_balancer=load_balancer,
                auto_scaling_policy=AutoScalingPolicy.REACTIVE
            )
            
            self.agent_pools[assignment.role_type] = pool
            
            self.logger.debug(f"Initialized enhanced agent pool for {assignment.role_type.value} "
                            f"with max {assignment.max_concurrent_instances} instances")
    
    def _get_optimal_load_balancing_strategy(self, agent_type: AgentType) -> LoadBalancingStrategy:
        """Get optimal load balancing strategy for agent type"""
        # Strategic agents benefit from response time optimization
        if agent_type in [AgentType.PM, AgentType.BA, AgentType.SA]:
            return LoadBalancingStrategy.RESPONSE_TIME
        
        # Research agents benefit from least loaded strategy
        elif agent_type in [AgentType.RESEARCH, AgentType.QUALITY_JUDGE]:
            return LoadBalancingStrategy.LEAST_LOADED
        
        # Implementation agents can use round robin for simplicity
        else:
            return LoadBalancingStrategy.ROUND_ROBIN
    
    def _create_scaling_thresholds(self, assignment: ModelAssignment) -> ScalingThresholds:
        """Create scaling thresholds based on model assignment"""
        # Strategic agents need more conservative scaling
        if assignment.model_tier == ModelTier.STRATEGIC:
            return ScalingThresholds(
                scale_up_threshold=0.7,
                scale_down_threshold=0.2,
                min_instances=1,
                max_instances=assignment.max_concurrent_instances,
                scale_up_cooldown=180,  # 3 minutes
                scale_down_cooldown=600,  # 10 minutes
                queue_threshold=3
            )
        
        # Operational agents can scale more aggressively
        elif assignment.model_tier == ModelTier.OPERATIONAL:
            return ScalingThresholds(
                scale_up_threshold=0.8,
                scale_down_threshold=0.3,
                min_instances=1,
                max_instances=assignment.max_concurrent_instances,
                scale_up_cooldown=120,  # 2 minutes
                scale_down_cooldown=300,  # 5 minutes
                queue_threshold=5
            )
        
        # Research agents use balanced scaling
        else:
            return ScalingThresholds(
                scale_up_threshold=0.75,
                scale_down_threshold=0.25,
                min_instances=1,
                max_instances=assignment.max_concurrent_instances,
                scale_up_cooldown=150,  # 2.5 minutes
                scale_down_cooldown=450,  # 7.5 minutes
                queue_threshold=4
            )
    
    def _load_data(self):
        """Load persisted optimization data"""
        if self.data_file.exists():
            try:
                with open(self.data_file, 'r') as f:
                    data = json.load(f)
                
                # Load performance data
                if 'performance_data' in data:
                    for key, perf_data in data['performance_data'].items():
                        self.performance_data[key] = ModelPerformanceData(
                            model_name=perf_data['model_name'],
                            agent_type=AgentType(perf_data['agent_type']),
                            success_rate=perf_data.get('success_rate', 1.0),
                            average_latency=perf_data.get('average_latency', 0.0),
                            quality_score=perf_data.get('quality_score', 1.0),
                            cost_efficiency=perf_data.get('cost_efficiency', 1.0),
                            total_requests=perf_data.get('total_requests', 0),
                            last_updated=datetime.fromisoformat(perf_data.get('last_updated', datetime.now().isoformat()))
                        )
                
                # Load cost metrics
                if 'cost_metrics' in data:
                    cm = data['cost_metrics']
                    self.cost_metrics = CostMetrics(
                        total_cost=cm.get('total_cost', 0.0),
                        cost_by_model=cm.get('cost_by_model', {}),
                        cost_by_agent_type={
                            AgentType(k): v for k, v in cm.get('cost_by_agent_type', {}).items()
                        },
                        tokens_consumed=cm.get('tokens_consumed', 0),
                        requests_made=cm.get('requests_made', 0),
                        last_updated=datetime.fromisoformat(cm.get('last_updated', datetime.now().isoformat()))
                    )
                
                self.logger.info("Loaded optimization data from file")
                
            except (json.JSONDecodeError, KeyError, ValueError) as e:
                self.logger.warning(f"Failed to load optimization data: {e}")
                # Initialize with empty data
                self.performance_data = {}
                self.cost_metrics = CostMetrics()
    
    def _save_data(self):
        """Save optimization data to file"""
        try:
            data = {
                'performance_data': {
                    key: {
                        'model_name': perf.model_name,
                        'agent_type': perf.agent_type.value,
                        'success_rate': perf.success_rate,
                        'average_latency': perf.average_latency,
                        'quality_score': perf.quality_score,
                        'cost_efficiency': perf.cost_efficiency,
                        'total_requests': perf.total_requests,
                        'last_updated': perf.last_updated.isoformat()
                    }
                    for key, perf in self.performance_data.items()
                },
                'cost_metrics': {
                    'total_cost': self.cost_metrics.total_cost,
                    'cost_by_model': self.cost_metrics.cost_by_model,
                    'cost_by_agent_type': {
                        k.value: v for k, v in self.cost_metrics.cost_by_agent_type.items()
                    },
                    'tokens_consumed': self.cost_metrics.tokens_consumed,
                    'requests_made': self.cost_metrics.requests_made,
                    'last_updated': self.cost_metrics.last_updated.isoformat()
                }
            }
            
            with open(self.data_file, 'w') as f:
                json.dump(data, f, indent=2)
                
            self.logger.debug("Saved optimization data to file")
            
        except Exception as e:
            self.logger.error(f"Failed to save optimization data: {e}")
    
    def select_model_for_agent(
        self,
        agent_type: AgentType,
        task: AgentTask,
        constraints: Optional[List[ResourceConstraint]] = None
    ) -> Tuple[str, ModelAssignment]:
        """
        Select the optimal model for an agent based on role hierarchy and task complexity
        
        Args:
            agent_type: Type of agent requesting model assignment
            task: Task to be executed
            constraints: Optional resource constraints
            
        Returns:
            Tuple of (selected_model_name, model_assignment)
            
        Raises:
            InvalidModelAssignmentError: If no suitable model assignment found
            InsufficientResourcesError: If resource constraints cannot be met
        """
        if agent_type not in self._assignment_by_type:
            raise InvalidModelAssignmentError(f"No model assignment found for agent type: {agent_type}")
        
        assignment = self._assignment_by_type[agent_type]
        constraints = constraints or []
        
        # Analyze task complexity
        complexity_score = self._analyze_task_complexity(task)
        
        # Check resource constraints
        self._validate_resource_constraints(assignment, constraints)
        
        # Select model based on strategy and performance data
        selected_model = self._select_optimal_model(assignment, complexity_score, task.priority)
        
        self.logger.info(f"Selected model {selected_model} for {agent_type.value} "
                        f"(complexity: {complexity_score:.2f}, priority: {task.priority.name})")
        
        return selected_model, assignment
    
    def _analyze_task_complexity(self, task: AgentTask) -> float:
        """
        Analyze task complexity to inform model selection
        
        Args:
            task: Task to analyze
            
        Returns:
            Complexity score between 0.0 and 1.0
        """
        complexity_score = 0.0
        
        # Base complexity from task type
        type_complexity = {
            "analysis": 0.7,
            "design": 0.8,
            "implementation": 0.5,
            "testing": 0.4,
            "research": 0.6,
            "quality_evaluation": 0.7,
            "documentation": 0.3
        }
        complexity_score += type_complexity.get(task.type, 0.5)
        
        # Adjust for priority
        priority_multiplier = {
            TaskPriority.CRITICAL: 1.2,
            TaskPriority.HIGH: 1.1,
            TaskPriority.MEDIUM: 1.0,
            TaskPriority.LOW: 0.9,
            TaskPriority.BACKGROUND: 0.8
        }
        complexity_score *= priority_multiplier.get(task.priority, 1.0)
        
        # Adjust for requirements count
        if task.requirements:
            complexity_score += min(len(task.requirements) * 0.1, 0.3)
        
        # Adjust for dependencies
        if task.context.dependencies:
            complexity_score += min(len(task.context.dependencies) * 0.05, 0.2)
        
        # Ensure score is within bounds
        return min(max(complexity_score, 0.0), 1.0)
    
    def _validate_resource_constraints(
        self,
        assignment: ModelAssignment,
        constraints: List[ResourceConstraint]
    ):
        """
        Validate that resource constraints can be met
        
        Args:
            assignment: Model assignment to validate
            constraints: Resource constraints to check
            
        Raises:
            InsufficientResourcesError: If constraints cannot be met
        """
        for constraint in constraints:
            if constraint == ResourceConstraint.BUDGET:
                # Check if we're within daily budget
                today_cost = self._get_daily_cost()
                if today_cost >= self.budget.max_daily_cost:
                    raise InsufficientResourcesError(
                        f"Daily budget exceeded: ${today_cost:.2f} >= ${self.budget.max_daily_cost:.2f}"
                    )
            
            elif constraint == ResourceConstraint.CONCURRENCY:
                # Check if we can spawn more instances
                pool = self.agent_pools.get(assignment.role_type)
                if pool and len(pool.active_instances) >= assignment.max_concurrent_instances:
                    raise InsufficientResourcesError(
                        f"Maximum concurrent instances reached for {assignment.role_type.value}: "
                        f"{len(pool.active_instances)} >= {assignment.max_concurrent_instances}"
                    )
    
    def _select_optimal_model(
        self,
        assignment: ModelAssignment,
        complexity_score: float,
        priority: TaskPriority
    ) -> str:
        """
        Select the optimal model based on assignment, complexity, and strategy
        
        Args:
            assignment: Model assignment configuration
            complexity_score: Task complexity score (0.0-1.0)
            priority: Task priority
            
        Returns:
            Selected model name
        """
        # Get performance data for both models
        recommended_key = f"{assignment.recommended_model}_{assignment.role_type.value}"
        fallback_key = f"{assignment.fallback_model}_{assignment.role_type.value}"
        
        recommended_perf = self.performance_data.get(recommended_key)
        fallback_perf = self.performance_data.get(fallback_key)
        
        # Decision logic based on strategy
        if self.strategy == OptimizationStrategy.COST_OPTIMIZED:
            # Always prefer the cheaper option (fallback)
            return assignment.fallback_model
        
        elif self.strategy == OptimizationStrategy.PERFORMANCE_OPTIMIZED:
            # Always prefer the recommended (higher performance) option
            return assignment.recommended_model
        
        elif self.strategy == OptimizationStrategy.QUALITY_FIRST:
            # Use recommended model for high complexity or high priority tasks
            if complexity_score > 0.7 or priority in [TaskPriority.CRITICAL, TaskPriority.HIGH]:
                return assignment.recommended_model
            return assignment.fallback_model
        
        else:  # BALANCED strategy
            # Use performance data to make informed decision
            if recommended_perf and fallback_perf:
                # Calculate weighted scores
                recommended_score = (
                    recommended_perf.success_rate * 0.3 +
                    recommended_perf.quality_score * 0.3 +
                    recommended_perf.cost_efficiency * 0.4
                )
                fallback_score = (
                    fallback_perf.success_rate * 0.3 +
                    fallback_perf.quality_score * 0.3 +
                    fallback_perf.cost_efficiency * 0.4
                )
                
                # Adjust for complexity and priority
                if complexity_score > 0.6:
                    recommended_score *= 1.2
                if priority in [TaskPriority.CRITICAL, TaskPriority.HIGH]:
                    recommended_score *= 1.1
                
                return assignment.recommended_model if recommended_score > fallback_score else assignment.fallback_model
            
            else:
                # No performance data, use heuristics
                if complexity_score > 0.6 or priority in [TaskPriority.CRITICAL, TaskPriority.HIGH]:
                    return assignment.recommended_model
                return assignment.fallback_model
    
    def allocate_agent_instance(
        self,
        agent_type: AgentType,
        task: AgentTask
    ) -> Optional[AgentInstance]:
        """
        Allocate an agent instance from the enhanced pool for task execution
        
        Args:
            agent_type: Type of agent needed
            task: Task to be assigned
            
        Returns:
            Allocated agent instance or None if task was queued
        """
        pool = self.agent_pools.get(agent_type)
        if not pool:
            self.logger.error(f"No agent pool found for type: {agent_type}")
            return None
        
        # Use enhanced pool's assignment logic
        instance = pool.assign_task(task)
        
        if instance:
            self.logger.info(f"Allocated instance {instance.instance_id} for task {task.id}")
        else:
            self.logger.info(f"Task {task.id} queued for {agent_type.value} pool")
        
        return instance
    
    def release_agent_instance(
        self,
        agent_type: AgentType,
        instance_id: str,
        performance_data: Optional[Dict[str, Any]] = None
    ) -> Optional[AgentTask]:
        """
        Release an agent instance back to the pool and get next task
        
        Args:
            agent_type: Type of agent
            instance_id: ID of instance to release
            performance_data: Optional performance data from task execution
            
        Returns:
            Next task assigned to the instance or None
        """
        pool = self.agent_pools.get(agent_type)
        if not pool:
            self.logger.error(f"No agent pool found for type: {agent_type}")
            return None
        
        # Extract performance metrics
        success = performance_data.get('success', True) if performance_data else True
        execution_time = performance_data.get('execution_time', 0.0) if performance_data else 0.0
        quality_score = performance_data.get('quality', 1.0) if performance_data else 1.0
        
        # Complete task using enhanced pool
        next_task = pool.complete_task(
            instance_id=instance_id,
            success=success,
            execution_time=execution_time,
            quality_score=quality_score
        )
        
        # Update model performance data if provided
        if performance_data:
            # Find the instance to get model info
            for instance in pool.active_instances:
                if instance.instance_id == instance_id and instance.model_assignment:
                    self._update_performance_data(
                        instance.model_assignment.recommended_model,
                        agent_type,
                        performance_data
                    )
                    break
        
        if next_task:
            self.logger.info(f"Assigned next task {next_task.id} to instance {instance_id}")
        else:
            self.logger.debug(f"Released instance {instance_id} for {agent_type.value}")
        
        return next_task
    
    def _update_performance_data(
        self,
        model_name: str,
        agent_type: AgentType,
        performance_data: Dict[str, Any]
    ):
        """
        Update performance data for a model
        
        Args:
            model_name: Name of the model
            agent_type: Type of agent that used the model
            performance_data: Performance metrics from task execution
        """
        key = f"{model_name}_{agent_type.value}"
        
        if key not in self.performance_data:
            self.performance_data[key] = ModelPerformanceData(
                model_name=model_name,
                agent_type=agent_type
            )
        
        perf = self.performance_data[key]
        perf.update_performance(
            success=performance_data.get('success', True),
            latency=performance_data.get('latency', 0.0),
            quality=performance_data.get('quality', 1.0),
            cost=performance_data.get('cost', 0.0)
        )
        
        # Update cost metrics
        if 'cost' in performance_data:
            self.cost_metrics.add_cost(
                model_name,
                agent_type,
                performance_data['cost'],
                performance_data.get('tokens', 0)
            )
        
        # Save data periodically
        if self.cost_metrics.requests_made % 10 == 0:
            self._save_data()
    
    def _get_daily_cost(self) -> float:
        """Get total cost for today"""
        today = datetime.now().date()
        daily_cost = 0.0
        
        # Sum costs from cost metrics if they're from today
        if self.cost_metrics.last_updated.date() == today:
            daily_cost = self.cost_metrics.total_cost
        
        return daily_cost
    
    def get_optimization_stats(self) -> Dict[str, Any]:
        """
        Get comprehensive optimization statistics
        
        Returns:
            Dictionary containing optimization statistics
        """
        stats = {
            'strategy': self.strategy.value,
            'total_cost': self.cost_metrics.total_cost,
            'total_requests': self.cost_metrics.requests_made,
            'total_tokens': self.cost_metrics.tokens_consumed,
            'daily_cost': self._get_daily_cost(),
            'budget_utilization': self._get_daily_cost() / self.budget.max_daily_cost,
            'cost_by_model': self.cost_metrics.cost_by_model,
            'cost_by_agent_type': {
                k.value: v for k, v in self.cost_metrics.cost_by_agent_type.items()
            },
            'agent_pools': {},
            'model_performance': {}
        }
        
        # Add agent pool statistics
        for agent_type, pool in self.agent_pools.items():
            pool_status = pool.get_pool_status()
            stats['agent_pools'][agent_type.value] = pool_status
        
        # Add model performance data
        for key, perf in self.performance_data.items():
            stats['model_performance'][key] = {
                'model_name': perf.model_name,
                'agent_type': perf.agent_type.value,
                'success_rate': perf.success_rate,
                'average_latency': perf.average_latency,
                'quality_score': perf.quality_score,
                'cost_efficiency': perf.cost_efficiency,
                'total_requests': perf.total_requests
            }
        
        return stats
    
    def optimize_resource_allocation(self) -> Dict[str, Any]:
        """
        Optimize resource allocation across agent pools
        
        Returns:
            Dictionary containing optimization recommendations
        """
        recommendations = {
            'scaling_actions': [],
            'model_switches': [],
            'budget_alerts': [],
            'performance_issues': []
        }
        
        # Check each agent pool for optimization opportunities
        for agent_type, pool in self.agent_pools.items():
            pool_status = pool.get_pool_status()
            load_factor = pool_status['current_load']
            
            # Scaling recommendations
            if load_factor > pool.scaling_thresholds.scale_up_threshold:
                recommendations['scaling_actions'].append({
                    'action': 'scale_up',
                    'agent_type': agent_type.value,
                    'current_instances': pool_status['total_instances'],
                    'recommended_instances': min(
                        pool_status['total_instances'] + 1, 
                        pool.scaling_thresholds.max_instances
                    ),
                    'reason': f'High load factor: {load_factor:.2f}'
                })
            
            elif (load_factor < pool.scaling_thresholds.scale_down_threshold and
                  pool_status['queued_tasks'] == 0):
                recommendations['scaling_actions'].append({
                    'action': 'scale_down',
                    'agent_type': agent_type.value,
                    'current_instances': pool_status['total_instances'],
                    'recommended_instances': max(
                        pool_status['total_instances'] - 1, 
                        pool.scaling_thresholds.min_instances
                    ),
                    'reason': f'Low load factor: {load_factor:.2f}'
                })
        
        # Check for model performance issues
        for key, perf in self.performance_data.items():
            if perf.success_rate < 0.8:
                recommendations['performance_issues'].append({
                    'model': perf.model_name,
                    'agent_type': perf.agent_type.value,
                    'issue': 'low_success_rate',
                    'value': perf.success_rate,
                    'recommendation': 'Consider switching to fallback model or investigating failures'
                })
            
            if perf.cost_efficiency < 0.5:
                recommendations['model_switches'].append({
                    'model': perf.model_name,
                    'agent_type': perf.agent_type.value,
                    'issue': 'low_cost_efficiency',
                    'value': perf.cost_efficiency,
                    'recommendation': 'Consider switching to more cost-effective model'
                })
        
        # Budget alerts
        daily_cost = self._get_daily_cost()
        budget_utilization = daily_cost / self.budget.max_daily_cost
        
        if budget_utilization > 0.8:
            recommendations['budget_alerts'].append({
                'type': 'high_utilization',
                'utilization': budget_utilization,
                'daily_cost': daily_cost,
                'budget': self.budget.max_daily_cost,
                'recommendation': 'Consider switching to more cost-effective models'
            })
        
        return recommendations
    
    def update_strategy(self, new_strategy: OptimizationStrategy):
        """
        Update the optimization strategy
        
        Args:
            new_strategy: New optimization strategy to use
        """
        old_strategy = self.strategy
        self.strategy = new_strategy
        
        self.logger.info(f"Updated optimization strategy from {old_strategy.value} to {new_strategy.value}")
        
        # Save the change
        self._save_data()
    
    def add_model_assignment(self, assignment: ModelAssignment):
        """
        Add a new model assignment
        
        Args:
            assignment: Model assignment to add
        """
        # Check if assignment already exists
        existing = self._assignment_by_type.get(assignment.role_type)
        if existing:
            self.logger.warning(f"Replacing existing assignment for {assignment.role_type.value}")
        
        # Add to assignments
        self.model_assignments.append(assignment)
        self._assignment_by_type[assignment.role_type] = assignment
        
        # Initialize agent pool if needed
        if assignment.role_type not in self.agent_pools:
            # Create enhanced load balancer
            load_balancer = EnhancedLoadBalancer(
                strategy=self._get_optimal_load_balancing_strategy(assignment.role_type),
                enable_health_checks=True,
                health_check_interval=30
            )
            
            # Create scaling thresholds
            scaling_thresholds = self._create_scaling_thresholds(assignment)
            
            # Create enhanced agent pool
            pool = EnhancedAgentPool(
                role_type=assignment.role_type,
                model_assignment=assignment,
                scaling_thresholds=scaling_thresholds,
                load_balancer=load_balancer,
                auto_scaling_policy=AutoScalingPolicy.REACTIVE
            )
            
            self.agent_pools[assignment.role_type] = pool
        
        self.logger.info(f"Added model assignment for {assignment.role_type.value}")
    
    def get_pool_status(self, agent_type: Optional[AgentType] = None) -> Dict[str, Any]:
        """
        Get detailed status of agent pools
        
        Args:
            agent_type: Specific agent type to get status for (all if None)
            
        Returns:
            Dictionary containing pool status information
        """
        if agent_type:
            pool = self.agent_pools.get(agent_type)
            if pool:
                return {agent_type.value: pool.get_pool_status()}
            else:
                return {}
        
        # Return status for all pools
        return {
            agent_type.value: pool.get_pool_status()
            for agent_type, pool in self.agent_pools.items()
        }
    
    def get_instance_details(self, agent_type: Optional[AgentType] = None) -> Dict[str, List[Dict[str, Any]]]:
        """
        Get detailed information about agent instances
        
        Args:
            agent_type: Specific agent type to get details for (all if None)
            
        Returns:
            Dictionary containing instance details
        """
        if agent_type:
            pool = self.agent_pools.get(agent_type)
            if pool:
                return {agent_type.value: pool.get_instance_details()}
            else:
                return {}
        
        # Return details for all pools
        return {
            agent_type.value: pool.get_instance_details()
            for agent_type, pool in self.agent_pools.items()
        }
    
    def update_load_balancing_strategy(
        self,
        agent_type: AgentType,
        strategy: LoadBalancingStrategy
    ) -> bool:
        """
        Update load balancing strategy for a specific agent type
        
        Args:
            agent_type: Agent type to update
            strategy: New load balancing strategy
            
        Returns:
            True if update was successful
        """
        pool = self.agent_pools.get(agent_type)
        if not pool:
            self.logger.error(f"No pool found for agent type: {agent_type}")
            return False
        
        old_strategy = pool.load_balancer.strategy
        pool.load_balancer.strategy = strategy
        
        self.logger.info(f"Updated load balancing strategy for {agent_type.value} "
                        f"from {old_strategy.value} to {strategy.value}")
        return True
    
    def update_scaling_thresholds(
        self,
        agent_type: AgentType,
        thresholds: ScalingThresholds
    ) -> bool:
        """
        Update scaling thresholds for a specific agent type
        
        Args:
            agent_type: Agent type to update
            thresholds: New scaling thresholds
            
        Returns:
            True if update was successful
        """
        pool = self.agent_pools.get(agent_type)
        if not pool:
            self.logger.error(f"No pool found for agent type: {agent_type}")
            return False
        
        pool.update_scaling_thresholds(thresholds)
        self.logger.info(f"Updated scaling thresholds for {agent_type.value}")
        return True
    
    def force_scale_pool(
        self,
        agent_type: AgentType,
        target_instances: int
    ) -> bool:
        """
        Force scaling of a specific agent pool
        
        Args:
            agent_type: Agent type to scale
            target_instances: Target number of instances
            
        Returns:
            True if scaling was successful
        """
        pool = self.agent_pools.get(agent_type)
        if not pool:
            self.logger.error(f"No pool found for agent type: {agent_type}")
            return False
        
        return pool.force_scale(target_instances)
    
    def get_load_balancing_metrics(self, agent_type: Optional[AgentType] = None) -> Dict[str, Any]:
        """
        Get load balancing metrics for agent pools
        
        Args:
            agent_type: Specific agent type to get metrics for (all if None)
            
        Returns:
            Dictionary containing load balancing metrics
        """
        if agent_type:
            pool = self.agent_pools.get(agent_type)
            if pool:
                metrics = pool.load_balancer.get_metrics()
                return {
                    agent_type.value: {
                        'strategy': pool.load_balancer.strategy.value,
                        'total_requests': metrics.total_requests,
                        'successful_requests': metrics.successful_requests,
                        'failed_requests': metrics.failed_requests,
                        'success_rate': metrics.get_success_rate(),
                        'average_response_time': metrics.average_response_time,
                        'peak_response_time': metrics.peak_response_time,
                        'current_load': metrics.current_load,
                        'peak_load': metrics.peak_load,
                        'queue_length': metrics.queue_length,
                        'active_connections': metrics.active_connections,
                        'last_updated': metrics.last_updated.isoformat()
                    }
                }
            else:
                return {}
        
        # Return metrics for all pools
        result = {}
        for agent_type, pool in self.agent_pools.items():
            metrics = pool.load_balancer.get_metrics()
            result[agent_type.value] = {
                'strategy': pool.load_balancer.strategy.value,
                'total_requests': metrics.total_requests,
                'successful_requests': metrics.successful_requests,
                'failed_requests': metrics.failed_requests,
                'success_rate': metrics.get_success_rate(),
                'average_response_time': metrics.average_response_time,
                'peak_response_time': metrics.peak_response_time,
                'current_load': metrics.current_load,
                'peak_load': metrics.peak_load,
                'queue_length': metrics.queue_length,
                'active_connections': metrics.active_connections,
                'last_updated': metrics.last_updated.isoformat()
            }
        
        return result
    
    def get_auto_scaling_recommendations(self) -> Dict[str, List[Dict[str, Any]]]:
        """
        Get auto-scaling recommendations for all pools
        
        Returns:
            Dictionary containing scaling recommendations
        """
        recommendations = {
            'immediate_actions': [],
            'suggested_optimizations': [],
            'performance_alerts': []
        }
        
        for agent_type, pool in self.agent_pools.items():
            pool_status = pool.get_pool_status()
            
            # Check for immediate scaling needs
            if pool_status['queued_tasks'] > pool.scaling_thresholds.queue_threshold:
                recommendations['immediate_actions'].append({
                    'action': 'scale_up',
                    'agent_type': agent_type.value,
                    'reason': f"Queue length ({pool_status['queued_tasks']}) exceeds threshold ({pool.scaling_thresholds.queue_threshold})",
                    'priority': 'high',
                    'recommended_instances': min(
                        pool_status['total_instances'] + 1,
                        pool.scaling_thresholds.max_instances
                    )
                })
            
            # Check for performance issues
            if pool_status['success_rate'] < 0.9:
                recommendations['performance_alerts'].append({
                    'agent_type': agent_type.value,
                    'issue': 'low_success_rate',
                    'value': pool_status['success_rate'],
                    'recommendation': 'Investigate task failures and consider scaling up'
                })
            
            if pool_status['average_response_time'] > 300:  # 5 minutes
                recommendations['performance_alerts'].append({
                    'agent_type': agent_type.value,
                    'issue': 'high_response_time',
                    'value': pool_status['average_response_time'],
                    'recommendation': 'Consider scaling up or optimizing task processing'
                })
            
            # Check for optimization opportunities
            if (pool_status['current_load'] < 0.2 and 
                pool_status['total_instances'] > pool.scaling_thresholds.min_instances):
                recommendations['suggested_optimizations'].append({
                    'action': 'scale_down',
                    'agent_type': agent_type.value,
                    'reason': f"Low utilization ({pool_status['current_load']:.2f})",
                    'priority': 'low',
                    'recommended_instances': max(
                        pool_status['total_instances'] - 1,
                        pool.scaling_thresholds.min_instances
                    )
                })
        
        return recommendations
    
    def cleanup(self):
        """Cleanup resources and save data"""
        # Cleanup all agent pools
        for pool in self.agent_pools.values():
            pool.cleanup()
        
        self._save_data()
        self.logger.info("ModelOptimizer cleanup completed")