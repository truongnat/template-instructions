# ModelOptimizer Integration Guide

This guide explains how to integrate the API Model Management system with the existing ModelOptimizer for intelligent model selection, performance tracking, and failover coordination.

## Overview

The ModelOptimizer Integration layer provides a bridge between:
- **ModelOptimizer**: Existing hierarchical model assignment and resource management
- **API Model Management**: New intelligent model selection with real-time availability, performance tracking, and cost optimization

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                     ModelOptimizer                          │
│  (Hierarchical assignment, resource management)             │
└────────────────────┬────────────────────────────────────────┘
                     │
                     │ Base ModelAssignment
                     ▼
┌─────────────────────────────────────────────────────────────┐
│            ModelOptimizerIntegration                        │
│  (Coordination layer)                                       │
└────────────────────┬────────────────────────────────────────┘
                     │
                     │ APIModelAssignment
                     ▼
┌─────────────────────────────────────────────────────────────┐
│              API Model Management                           │
│  (Real-time selection, monitoring, failover)                │
└─────────────────────────────────────────────────────────────┘
```

## Key Components

### 1. APIModelAssignment

Extended ModelAssignment with API-specific details:

```python
@dataclass
class APIModelAssignment:
    base_assignment: ModelAssignment      # Original assignment from ModelOptimizer
    selected_model_id: str                # API-selected model ID
    model_selection: ModelSelection       # Full selection details
    api_provider: str                     # Provider (openai, anthropic, etc.)
    api_endpoint: Optional[str]           # API endpoint URL
    selection_timestamp: datetime         # When selection was made
```

**Key Features:**
- Maintains backward compatibility with ModelAssignment interface
- Adds API-specific metadata
- Provides access to selection reasoning and alternatives

### 2. ModelOptimizerIntegration

Main integration class that coordinates between systems:

```python
class ModelOptimizerIntegration:
    def __init__(
        self,
        model_selector: ModelSelector,
        failover_manager: FailoverManager,
        performance_monitor: PerformanceMonitor,
        cost_tracker: CostTracker
    )
```

**Core Methods:**

#### Model Selection
```python
async def select_model_for_agent(
    self,
    agent_type: AgentType,
    task: AgentTask,
    base_assignment: ModelAssignment,
    constraints: Optional[SelectionConstraints] = None
) -> APIModelAssignment
```

Selects optimal model using API Model Management while respecting ModelOptimizer's base assignment.

#### Performance Reporting
```python
async def report_performance_to_optimizer(
    self,
    agent_type: AgentType,
    task_id: str,
    model_id: str,
    performance_data: Dict[str, Any]
) -> None
```

Reports execution performance back to both systems for optimization.

#### Failover Coordination
```python
async def report_failover_event(
    self,
    agent_type: AgentType,
    task_id: str,
    original_model: str,
    alternative_model: str,
    reason: FailoverReason
) -> None
```

Coordinates failover events between ModelOptimizer and API Model Management.

## Usage Patterns

### Pattern 1: Basic Integration

```python
# Initialize components
integration = ModelOptimizerIntegration(
    model_selector=model_selector,
    failover_manager=failover_manager,
    performance_monitor=performance_monitor,
    cost_tracker=cost_tracker
)

# Get base assignment from ModelOptimizer
base_assignment = model_optimizer.select_model_for_agent(
    agent_type=AgentType.SA,
    task=task
)

# Enhance with API selection
api_assignment = await integration.select_model_for_agent(
    agent_type=AgentType.SA,
    task=task,
    base_assignment=base_assignment
)

# Use the selected model
model_id = api_assignment.selected_model_id
```

### Pattern 2: With Constraints

```python
# Define selection constraints
constraints = SelectionConstraints(
    required_capabilities=["analysis", "code-generation"],
    max_cost_per_request=1.0,
    excluded_providers=["ollama"],
    max_latency_ms=3000.0
)

# Select with constraints
api_assignment = await integration.select_model_for_agent(
    agent_type=AgentType.SA,
    task=task,
    base_assignment=base_assignment,
    constraints=constraints
)
```

### Pattern 3: Performance Feedback Loop

```python
# Execute task
result = await execute_task(task, api_assignment.selected_model_id)

# Report performance
performance_data = {
    'success': result.success,
    'latency_ms': result.execution_time,
    'quality_score': result.quality_score,
    'cost': result.cost,
    'input_tokens': result.input_tokens,
    'output_tokens': result.output_tokens
}

await integration.report_performance_to_optimizer(
    agent_type=AgentType.SA,
    task_id=task.id,
    model_id=api_assignment.selected_model_id,
    performance_data=performance_data
)
```

### Pattern 4: Failover Handling

```python
try:
    # Attempt with primary model
    result = await execute_task(task, primary_model)
except RateLimitError:
    # Report failover
    await integration.report_failover_event(
        agent_type=AgentType.SA,
        task_id=task.id,
        original_model=primary_model,
        alternative_model=alternative_model,
        reason=FailoverReason.RATE_LIMITED
    )
    
    # Retry with alternative
    result = await execute_task(task, alternative_model)
```

### Pattern 5: Performance Monitoring

```python
# Get performance summary
summary = await integration.get_performance_summary(
    agent_type=AgentType.SA,
    window_hours=24
)

print(f"Total requests: {summary['total_requests']}")
print(f"Total cost: ${summary['total_cost']:.2f}")
print(f"Average success rate: {summary['average_success_rate']:.2%}")
```

## Integration with ModelOptimizer

### Extending ModelOptimizer

To integrate with an existing ModelOptimizer instance:

```python
class EnhancedModelOptimizer(ModelOptimizer):
    """ModelOptimizer with API Model Management integration."""
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Initialize API components
        self.api_integration = self._initialize_api_integration()
    
    def _initialize_api_integration(self) -> ModelOptimizerIntegration:
        """Initialize API Model Management integration."""
        # Initialize registry, health checker, etc.
        registry = ModelRegistry(config_path=Path("config/model_registry.json"))
        health_checker = HealthChecker(registry=registry)
        rate_limiter = RateLimiter(registry=registry)
        performance_monitor = PerformanceMonitor(db_path=Path("data/performance.db"))
        cost_tracker = CostTracker(db_path=Path("data/costs.db"))
        
        model_selector = ModelSelector(
            registry=registry,
            health_checker=health_checker,
            rate_limiter=rate_limiter,
            performance_monitor=performance_monitor
        )
        
        failover_manager = FailoverManager(
            model_selector=model_selector,
            max_retries=3
        )
        
        return ModelOptimizerIntegration(
            model_selector=model_selector,
            failover_manager=failover_manager,
            performance_monitor=performance_monitor,
            cost_tracker=cost_tracker
        )
    
    async def select_model_for_agent_enhanced(
        self,
        agent_type: AgentType,
        task: AgentTask,
        constraints: Optional[List[ResourceConstraint]] = None
    ) -> Tuple[str, APIModelAssignment]:
        """Enhanced model selection with API integration."""
        
        # Get base assignment from parent
        model_name, base_assignment = self.select_model_for_agent(
            agent_type=agent_type,
            task=task,
            constraints=constraints
        )
        
        # Enhance with API selection
        api_assignment = await self.api_integration.select_model_for_agent(
            agent_type=agent_type,
            task=task,
            base_assignment=base_assignment
        )
        
        return api_assignment.selected_model_id, api_assignment
```

### Backward Compatibility

The integration maintains full backward compatibility:

```python
# Old code still works
model_name, assignment = optimizer.select_model_for_agent(
    agent_type=AgentType.SA,
    task=task
)

# New code uses enhanced version
model_id, api_assignment = await optimizer.select_model_for_agent_enhanced(
    agent_type=AgentType.SA,
    task=task
)

# APIModelAssignment is compatible with ModelAssignment
assert api_assignment.role_type == assignment.role_type
assert api_assignment.model_tier == assignment.model_tier
```

## Performance Considerations

### Caching

The integration layer caches model assignments to reduce selection overhead:

```python
# First call - performs full selection
api_assignment = await integration.select_model_for_agent(...)

# Subsequent calls - uses cache
cached = integration.get_cached_assignment(agent_type, task_id)
```

Clear cache when needed:

```python
# Clear for specific agent type
integration.clear_assignment_cache(agent_type=AgentType.SA)

# Clear all
integration.clear_assignment_cache()
```

### Async Operations

All integration methods are async to support non-blocking operations:

```python
# Run multiple selections concurrently
assignments = await asyncio.gather(
    integration.select_model_for_agent(AgentType.SA, task1, base1),
    integration.select_model_for_agent(AgentType.PM, task2, base2),
    integration.select_model_for_agent(AgentType.BA, task3, base3)
)
```

## Error Handling

The integration provides graceful fallback:

```python
try:
    api_assignment = await integration.select_model_for_agent(
        agent_type=agent_type,
        task=task,
        base_assignment=base_assignment
    )
except APIModelError as e:
    # Falls back to base assignment automatically
    logger.warning(f"API selection failed, using fallback: {e}")
    # api_assignment will use base_assignment.fallback_model
```

## Monitoring and Observability

### Logging

The integration provides comprehensive logging:

```python
import logging

# Enable debug logging
logging.getLogger('agentic_sdlc.orchestration.api_model_management').setLevel(logging.DEBUG)
```

### Metrics

Access performance metrics:

```python
# Get detailed performance summary
summary = await integration.get_performance_summary(
    agent_type=AgentType.SA,
    window_hours=24
)

# Access specific metrics
for model_id, cost in summary['cost_by_model'].items():
    print(f"{model_id}: ${cost:.2f}")
```

## Best Practices

1. **Initialize Once**: Create a single ModelOptimizerIntegration instance and reuse it
2. **Report Performance**: Always report performance data for optimization
3. **Handle Failovers**: Report failover events to improve future selections
4. **Use Constraints**: Provide selection constraints when you have specific requirements
5. **Monitor Costs**: Regularly check performance summaries to track costs
6. **Clear Cache**: Clear assignment cache when model configurations change
7. **Async All The Way**: Use async/await throughout for best performance

## Troubleshooting

### Issue: Model selection fails

**Solution**: Check that model registry is properly configured and models are enabled.

```python
# Verify registry
models = list(integration.model_selector.registry._models.values())
enabled = [m for m in models if m.enabled]
print(f"Enabled models: {len(enabled)}")
```

### Issue: Performance not being tracked

**Solution**: Ensure performance data is being reported correctly.

```python
# Verify performance data structure
performance_data = {
    'success': True,  # Required
    'latency_ms': 1500.0,  # Required
    'quality_score': 0.9,  # Required
    'cost': 0.15,  # Required for cost tracking
    'input_tokens': 500,  # Required for cost tracking
    'output_tokens': 1000  # Required for cost tracking
}
```

### Issue: Failover not working

**Solution**: Check health checker and rate limiter status.

```python
# Check model availability
is_available = integration.model_selector.health_checker.is_model_available(model_id)
is_rate_limited = integration.model_selector.rate_limiter.is_rate_limited(model_id)

print(f"Available: {is_available}, Rate Limited: {is_rate_limited}")
```

## See Also

- [API Model Management Design Document](../../.kiro/specs/api-model-management/design.md)
- [Model Selector Documentation](selector.py)
- [Failover Manager Documentation](failover_manager.py)
- [Performance Monitor Documentation](performance_monitor.py)
- [Cost Tracker Documentation](cost_tracker.py)
