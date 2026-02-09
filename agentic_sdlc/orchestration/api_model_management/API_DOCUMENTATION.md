# API Model Management - API Documentation

## Table of Contents

1. [Overview](#overview)
2. [Quick Start](#quick-start)
3. [Core Components](#core-components)
4. [Data Models](#data-models)
5. [Public Interfaces](#public-interfaces)
6. [Usage Examples](#usage-examples)
7. [Integration with ModelOptimizer](#integration-with-modeloptimizer)
8. [Error Handling](#error-handling)
9. [Best Practices](#best-practices)

## Overview

The API Model Management system provides intelligent model selection, real-time availability checking, automatic failover, response quality evaluation, and comprehensive cost tracking for API-based AI model connections.

### Key Features

- **Intelligent Model Selection**: Automatically selects optimal models based on task requirements, cost, and availability
- **Real-Time Health Monitoring**: Continuous health checks ensure models are available before use
- **Automatic Failover**: Seamlessly switches to alternative models when primary is unavailable or rate-limited
- **Response Quality Evaluation**: Assesses response quality and triggers model switching for low-quality outputs
- **Comprehensive Caching**: Reduces API costs by caching identical requests
- **Cost Tracking**: Monitors and reports API usage costs with budget alerts
- **Performance Monitoring**: Tracks latency, success rates, and quality scores
- **Graceful Degradation**: Continues operation even when some components fail

### Supported Providers

- **OpenAI**: GPT-4, GPT-3.5, and other OpenAI models
- **Anthropic**: Claude 3.5 Sonnet and other Claude models
- **Google**: Gemini Pro and other Google AI models
- **Ollama**: Local models (Llama, Mistral, etc.)

## Quick Start

### Installation

The API Model Management system is part of the agentic_sdlc package:

```python
from agentic_sdlc.orchestration.api_model_management import (
    ModelMetadata,
    ModelRequest,
    ModelResponse,
)
```

### Basic Setup

1. **Configure Environment Variables**

```bash
# Set API keys in .env file
OPENAI_API_KEY=sk-...
ANTHROPIC_API_KEY=sk-ant-...
GOOGLE_API_KEY=...
OLLAMA_BASE_URL=http://localhost:11434
```

2. **Configure Models**

Edit `config/model_registry.json` to define available models (see Configuration Guide).

3. **Initialize Components**

```python
from pathlib import Path
from agentic_sdlc.orchestration.api_model_management.registry import ModelRegistry
from agentic_sdlc.orchestration.api_model_management.selector import ModelSelector
from agentic_sdlc.orchestration.api_model_management.health_checker import HealthChecker
from agentic_sdlc.orchestration.api_model_management.rate_limiter import RateLimiter
from agentic_sdlc.orchestration.api_model_management.performance_monitor import PerformanceMonitor

# Initialize registry
config_path = Path("config/model_registry.json")
registry = ModelRegistry(config_path)

# Initialize health checker
health_checker = HealthChecker(registry)
await health_checker.start()

# Initialize rate limiter
rate_limiter = RateLimiter(registry)

# Initialize performance monitor
db_path = Path("data/api_model_management.db")
performance_monitor = PerformanceMonitor(db_path)

# Initialize model selector
selector = ModelSelector(
    registry=registry,
    health_checker=health_checker,
    rate_limiter=rate_limiter,
    performance_monitor=performance_monitor
)
```

### Simple Example

```python
from agentic_sdlc.orchestration.api_model_management import ModelRequest

# Create a request
request = ModelRequest(
    prompt="Write a Python function to calculate fibonacci numbers",
    parameters={"temperature": 0.7},
    task_id="task-123",
    agent_type="implementation",
    max_tokens=1000
)

# Select optimal model
selection = await selector.select_model(
    task=request,
    agent_type="implementation"
)

print(f"Selected model: {selection.model_id}")
print(f"Suitability score: {selection.suitability_score}")
print(f"Reason: {selection.selection_reason}")
```

## Core Components

### ModelRegistry

Centralized repository for model metadata and configuration.

**Purpose**: Manages model definitions, validates configurations, and provides query interface.

**Key Methods**:
- `load_config()`: Load model configurations from file
- `get_model(model_id)`: Retrieve model metadata by ID
- `get_models_by_provider(provider)`: Get all models for a provider
- `get_models_by_capability(capability)`: Get models with specific capability
- `get_models_by_cost_range(min_cost, max_cost)`: Get models within cost range

**Example**:
```python
from agentic_sdlc.orchestration.api_model_management.registry import ModelRegistry

registry = ModelRegistry(Path("config/model_registry.json"))
registry.load_config()

# Get specific model
model = registry.get_model("gpt-4-turbo")
print(f"Model: {model.name}, Cost: ${model.cost_per_1k_input_tokens}")

# Query by capability
code_models = registry.get_models_by_capability("code-generation")
print(f"Found {len(code_models)} code generation models")
```

### ModelSelector

Intelligent model selection based on task requirements, cost, and availability.

**Purpose**: Evaluates available models and selects the optimal one for each task.

**Selection Algorithm**:
1. Filter models by required capabilities
2. Filter out unavailable or rate-limited models
3. Calculate suitability score (capability: 30%, cost: 25%, performance: 25%, availability: 20%)
4. Apply task priority adjustments
5. Return highest-scoring model

**Key Methods**:
- `select_model(task, agent_type, constraints)`: Select optimal model
- `calculate_suitability_score(model, task, performance_data)`: Calculate model score
- `rank_models(models, task)`: Rank models by suitability

**Example**:
```python
from agentic_sdlc.orchestration.api_model_management.selector import ModelSelector
from agentic_sdlc.orchestration.api_model_management import SelectionConstraints

# Create constraints
constraints = SelectionConstraints(
    max_cost_per_request=0.50,
    required_capabilities=["code-generation"],
    excluded_providers=["ollama"]
)

# Select model
selection = await selector.select_model(
    task=request,
    agent_type="implementation",
    constraints=constraints
)
```

### HealthChecker

Real-time availability monitoring for all registered models.

**Purpose**: Performs periodic health checks and maintains availability status.

**Key Methods**:
- `start()`: Start periodic health checking
- `stop()`: Stop health checking
- `check_model_health(model_id)`: Perform health check on specific model
- `get_model_status(model_id)`: Get current availability status
- `is_model_available(model_id)`: Check if model is available

**Health Check Logic**:
- Sends lightweight test request to model API
- Records response time and success/failure
- Marks unavailable after 3 consecutive failures
- Marks available after 1 successful check
- Uses exponential backoff for failed checks

**Example**:
```python
from agentic_sdlc.orchestration.api_model_management.health_checker import HealthChecker

health_checker = HealthChecker(registry, check_interval_seconds=60)
await health_checker.start()

# Check specific model
status = await health_checker.check_model_health("gpt-4-turbo")
print(f"Available: {status.is_available}, Response time: {status.response_time_ms}ms")

# Get current status
is_available = health_checker.is_model_available("gpt-4-turbo")
```

### RateLimiter

Tracks and enforces rate limits to prevent quota exhaustion.

**Purpose**: Monitors request counts and token usage to detect and prevent rate limiting.

**Key Methods**:
- `check_rate_limit(model_id, estimated_tokens)`: Check if request would exceed limit
- `record_request(model_id, tokens_used, was_rate_limited)`: Record request for tracking
- `is_rate_limited(model_id)`: Check if model is currently rate-limited
- `get_time_until_reset(model_id)`: Get seconds until rate limit resets

**Rate Limit Tracking**:
- Sliding window algorithm for request counting
- Separate tracking for requests/minute and tokens/minute
- 90% threshold triggers rate-limited status
- Automatic reset when window expires

**Example**:
```python
from agentic_sdlc.orchestration.api_model_management.rate_limiter import RateLimiter

rate_limiter = RateLimiter(registry)

# Check before request
status = await rate_limiter.check_rate_limit("gpt-4-turbo", estimated_tokens=1000)
if status.is_limited:
    print(f"Rate limited. Reset in {status.reset_time}")
else:
    # Make request
    await rate_limiter.record_request("gpt-4-turbo", tokens_used=1000)
```

### FailoverManager

Automatic failover to alternative models when primary is unavailable.

**Purpose**: Detects failures and automatically switches to alternative models.

**Key Methods**:
- `execute_with_failover(primary_model, task, request_func)`: Execute with automatic failover
- `select_alternative(failed_model, task, reason)`: Select alternative model
- `record_failover(original_model, alternative_model, reason)`: Record failover event

**Failover Logic**:
1. Detect failure (unavailable, rate-limited, error)
2. Select alternative using ModelSelector
3. Retry with exponential backoff (2s, 4s, 8s)
4. Log failover event with reason
5. Alert if >3 failovers in 1 hour

**Example**:
```python
from agentic_sdlc.orchestration.api_model_management.failover_manager import FailoverManager

failover_manager = FailoverManager(
    model_selector=selector,
    max_retries=3,
    base_backoff_seconds=2
)

# Execute with automatic failover
async def make_request(model_id):
    # Your API request logic
    return await api_client.send_request(model_id, request)

response = await failover_manager.execute_with_failover(
    primary_model="gpt-4-turbo",
    task=request,
    request_func=make_request
)
```

### APIClientManager

Manages API connections and routes requests to provider-specific adapters.

**Purpose**: Handles HTTP connections, authentication, and request routing.

**Key Methods**:
- `send_request(model_id, request)`: Send request to model API
- `send_request_with_retry(model_id, request, max_retries)`: Send with retry logic

**Features**:
- Connection pooling for efficiency
- Automatic retry with exponential backoff
- Provider-specific adapter routing
- Error categorization (transient vs permanent)

**Example**:
```python
from agentic_sdlc.orchestration.api_model_management.api_client import APIClientManager
from agentic_sdlc.orchestration.api_model_management.api_key_manager import APIKeyManager

# Initialize API key manager
key_manager = APIKeyManager()
key_manager.load_keys()

# Initialize API client
api_client = APIClientManager(
    api_key_manager=key_manager,
    adapters=adapters  # Provider adapters
)

# Send request
response = await api_client.send_request_with_retry(
    model_id="gpt-4-turbo",
    request=request,
    max_retries=3
)
```

### ResponseEvaluator

Assesses response quality and triggers model switching for low-quality outputs.

**Purpose**: Evaluates response quality using configurable metrics.

**Quality Metrics**:
- **Completeness** (40%): Response addresses all task requirements
- **Relevance** (35%): Response content is relevant to task
- **Coherence** (25%): Response is well-structured and logical

**Key Methods**:
- `evaluate_response(response, task)`: Evaluate response quality
- `should_switch_model(model_id, recent_scores)`: Determine if model switch needed
- `calculate_completeness(response, task)`: Calculate completeness score
- `calculate_relevance(response, task)`: Calculate relevance score
- `calculate_coherence(response)`: Calculate coherence score

**Example**:
```python
from agentic_sdlc.orchestration.api_model_management.evaluator import ResponseEvaluator

evaluator = ResponseEvaluator(
    quality_threshold=0.7,
    evaluation_window=10
)

# Evaluate response
quality = await evaluator.evaluate_response(response, task)
print(f"Quality score: {quality.overall_score}")
print(f"Completeness: {quality.completeness}")
print(f"Relevance: {quality.relevance}")
print(f"Coherence: {quality.coherence}")

# Check if model switch needed
if evaluator.should_switch_model("gpt-4-turbo", recent_scores):
    print("Model switch recommended due to low quality")
```

### CacheManager

Caches responses to reduce API calls and costs.

**Purpose**: Stores and retrieves previously generated responses.

**Key Methods**:
- `get(cache_key)`: Retrieve cached response
- `set(cache_key, response, ttl_seconds)`: Store response in cache
- `generate_cache_key(request)`: Generate cache key from request
- `evict_expired()`: Evict expired cache entries
- `evict_lru(target_size_mb)`: Evict least recently used entries

**Caching Strategy**:
- Cache key: SHA256 hash of (model_id + request_content + parameters)
- Default TTL: 1 hour
- LRU eviction when cache exceeds max size
- Periodic cleanup of expired entries

**Example**:
```python
from agentic_sdlc.orchestration.api_model_management.cache_manager import CacheManager

cache_manager = CacheManager(
    db_path=Path("data/cache.db"),
    max_size_mb=1000,
    default_ttl_seconds=3600
)

# Generate cache key
cache_key = cache_manager.generate_cache_key(request)

# Check cache
cached = await cache_manager.get(cache_key)
if cached:
    print("Cache hit!")
    return cached.response

# Store in cache
await cache_manager.set(cache_key, response, ttl_seconds=3600)
```

### CostTracker

Tracks and reports API usage costs.

**Purpose**: Monitors costs and provides budget management.

**Key Methods**:
- `record_cost(model_id, agent_type, input_tokens, output_tokens, cost, task_id)`: Record cost
- `get_daily_cost(date)`: Get total cost for specific day
- `get_cost_by_model(start_date, end_date)`: Get costs aggregated by model
- `check_budget()`: Check current budget utilization

**Example**:
```python
from agentic_sdlc.orchestration.api_model_management.cost_tracker import CostTracker

cost_tracker = CostTracker(
    db_path=Path("data/costs.db"),
    daily_budget=100.0
)

# Record cost
await cost_tracker.record_cost(
    model_id="gpt-4-turbo",
    agent_type="implementation",
    input_tokens=1000,
    output_tokens=500,
    cost=0.025,
    task_id="task-123"
)

# Check budget
budget_status = await cost_tracker.check_budget()
print(f"Budget utilization: {budget_status.utilization_percent}%")
if budget_status.is_over_budget:
    print("WARNING: Budget exceeded!")
```

### PerformanceMonitor

Tracks and analyzes model performance metrics.

**Purpose**: Monitors latency, success rates, and quality scores.

**Key Methods**:
- `record_performance(model_id, agent_type, latency_ms, success, quality_score, task_id)`: Record metrics
- `get_model_performance(model_id, window_hours)`: Get performance metrics
- `detect_degradation(model_id, threshold)`: Detect performance degradation

**Example**:
```python
from agentic_sdlc.orchestration.api_model_management.performance_monitor import PerformanceMonitor

performance_monitor = PerformanceMonitor(db_path=Path("data/performance.db"))

# Record performance
await performance_monitor.record_performance(
    model_id="gpt-4-turbo",
    agent_type="implementation",
    latency_ms=2000.0,
    success=True,
    quality_score=0.85,
    task_id="task-123"
)

# Get metrics
metrics = await performance_monitor.get_model_performance(
    model_id="gpt-4-turbo",
    window_hours=24
)
print(f"Success rate: {metrics.success_rate}%")
print(f"Average latency: {metrics.average_latency_ms}ms")
print(f"P95 latency: {metrics.p95_latency_ms}ms")
```

## Data Models

### ModelMetadata

Metadata for an AI model.

```python
@dataclass
class ModelMetadata:
    id: str                          # Unique model identifier
    provider: str                    # Provider name (openai, anthropic, google, ollama)
    name: str                        # Human-readable name
    capabilities: List[str]          # Model capabilities
    cost_per_1k_input_tokens: float  # Cost per 1000 input tokens (USD)
    cost_per_1k_output_tokens: float # Cost per 1000 output tokens (USD)
    rate_limits: RateLimits          # Rate limit configuration
    context_window: int              # Maximum context window size
    average_response_time_ms: float  # Expected response time
    enabled: bool = True             # Whether model is enabled
```

### ModelRequest

Request to an AI model.

```python
@dataclass
class ModelRequest:
    prompt: str                      # Input prompt
    parameters: Dict[str, Any]       # Model parameters
    task_id: str                     # Unique task identifier
    agent_type: str                  # Agent type making request
    max_tokens: Optional[int] = None # Maximum tokens to generate
    temperature: float = 0.7         # Sampling temperature
```

### ModelResponse

Response from an AI model.

```python
@dataclass
class ModelResponse:
    content: str                     # Generated content
    model_id: str                    # Model that generated response
    token_usage: TokenUsage          # Token usage information
    latency_ms: float                # Response latency
    cost: float                      # Request cost (USD)
    metadata: Dict[str, Any]         # Additional metadata
```

### ModelSelection

Result of model selection.

```python
@dataclass
class ModelSelection:
    model_id: str                    # Selected model ID
    model_metadata: ModelMetadata    # Model metadata
    suitability_score: float         # Suitability score (0-1)
    alternatives: List[str]          # Alternative model IDs
    selection_reason: str            # Reason for selection
```

### SelectionConstraints

Constraints for model selection.

```python
@dataclass
class SelectionConstraints:
    max_cost_per_request: Optional[float] = None  # Maximum cost per request
    required_capabilities: List[str] = []         # Required capabilities
    excluded_providers: List[str] = []            # Excluded providers
    max_latency_ms: Optional[float] = None        # Maximum acceptable latency
```

### HealthStatus

Health check result for a model.

```python
@dataclass
class HealthStatus:
    model_id: str                    # Model identifier
    is_available: bool               # Whether model is available
    response_time_ms: float          # Health check response time
    last_check: datetime             # Last check timestamp
    consecutive_failures: int        # Number of consecutive failures
    error_message: Optional[str]     # Error message if unavailable
```

### RateLimitStatus

Rate limit status for a model.

```python
@dataclass
class RateLimitStatus:
    model_id: str                    # Model identifier
    is_limited: bool                 # Whether model is rate-limited
    requests_remaining: int          # Remaining requests in window
    tokens_remaining: int            # Remaining tokens in window
    reset_time: Optional[datetime]   # When rate limit resets
```

### QualityScore

Response quality evaluation metrics.

```python
@dataclass
class QualityScore:
    overall_score: float             # Overall quality score (0-1)
    completeness: float              # Completeness score (0-1)
    relevance: float                 # Relevance score (0-1)
    coherence: float                 # Coherence score (0-1)
    timestamp: datetime              # Evaluation timestamp
```

### BudgetStatus

Budget utilization status.

```python
@dataclass
class BudgetStatus:
    daily_budget: float              # Daily budget limit (USD)
    current_spend: float             # Current spending (USD)
    utilization_percent: float       # Budget utilization percentage
    is_over_budget: bool             # Whether budget is exceeded
    remaining_budget: float          # Remaining budget (USD)
```

### PerformanceMetrics

Performance metrics for a model over a time window.

```python
@dataclass
class PerformanceMetrics:
    model_id: str                    # Model identifier
    window_hours: int                # Time window in hours
    total_requests: int              # Total requests in window
    successful_requests: int         # Successful requests
    failed_requests: int             # Failed requests
    success_rate: float              # Success rate percentage
    average_latency_ms: float        # Average latency
    p50_latency_ms: float            # 50th percentile latency
    p95_latency_ms: float            # 95th percentile latency
    p99_latency_ms: float            # 99th percentile latency
    average_quality_score: float     # Average quality score
```

### ErrorResponse

Standardized error response.

```python
@dataclass
class ErrorResponse:
    error_type: str                  # Error type
    error_message: str               # Error message
    model_id: str                    # Model that failed
    task_id: str                     # Task identifier
    is_retryable: bool               # Whether error is retryable
    attempted_models: List[str]      # Models attempted
    failure_reasons: Dict[str, str]  # Failure reasons per model
    timestamp: datetime              # Error timestamp
```

## Public Interfaces

### Registry Interface

```python
class ModelRegistry:
    def __init__(self, config_path: Path)
    def load_config(self) -> None
    def get_model(self, model_id: str) -> Optional[ModelMetadata]
    def get_models_by_provider(self, provider: str) -> List[ModelMetadata]
    def get_models_by_capability(self, capability: str) -> List[ModelMetadata]
    def get_models_by_cost_range(self, min_cost: float, max_cost: float) -> List[ModelMetadata]
    def update_model(self, model_id: str, metadata: ModelMetadata) -> bool
    def add_model(self, metadata: ModelMetadata) -> bool
```

### Selector Interface

```python
class ModelSelector:
    def __init__(self, registry: ModelRegistry, health_checker: HealthChecker,
                 rate_limiter: RateLimiter, performance_monitor: PerformanceMonitor)
    async def select_model(self, task: ModelRequest, agent_type: str,
                          constraints: Optional[SelectionConstraints] = None) -> ModelSelection
    def calculate_suitability_score(self, model: ModelMetadata, task: ModelRequest,
                                    performance_data: Optional[PerformanceMetrics] = None) -> float
    def rank_models(self, models: List[ModelMetadata], task: ModelRequest) -> List[Tuple[ModelMetadata, float]]
```

### Health Checker Interface

```python
class HealthChecker:
    def __init__(self, registry: ModelRegistry, check_interval_seconds: int = 60)
    async def start(self) -> None
    async def stop(self) -> None
    async def check_model_health(self, model_id: str) -> HealthStatus
    def get_model_status(self, model_id: str) -> ModelAvailability
    def is_model_available(self, model_id: str) -> bool
```

### Rate Limiter Interface

```python
class RateLimiter:
    def __init__(self, registry: ModelRegistry)
    async def check_rate_limit(self, model_id: str, estimated_tokens: int) -> RateLimitStatus
    async def record_request(self, model_id: str, tokens_used: int, was_rate_limited: bool = False) -> None
    def is_rate_limited(self, model_id: str) -> bool
    def get_time_until_reset(self, model_id: str) -> Optional[int]
```

### Failover Manager Interface

```python
class FailoverManager:
    def __init__(self, model_selector: ModelSelector, max_retries: int = 3, base_backoff_seconds: int = 2)
    async def execute_with_failover(self, primary_model: str, task: ModelRequest,
                                    request_func: Callable) -> ModelResponse
    async def select_alternative(self, failed_model: str, task: ModelRequest,
                                reason: FailoverReason) -> Optional[str]
    def record_failover(self, original_model: str, alternative_model: str, reason: FailoverReason) -> None
```

### API Client Interface

```python
class APIClientManager:
    def __init__(self, api_key_manager: APIKeyManager, adapters: Dict[str, ProviderAdapter])
    async def send_request(self, model_id: str, request: ModelRequest) -> ModelResponse
    async def send_request_with_retry(self, model_id: str, request: ModelRequest, max_retries: int = 3) -> ModelResponse
```

### Evaluator Interface

```python
class ResponseEvaluator:
    def __init__(self, quality_threshold: float = 0.7, evaluation_window: int = 10)
    async def evaluate_response(self, response: ModelResponse, task: ModelRequest) -> QualityScore
    def should_switch_model(self, model_id: str, recent_scores: List[float]) -> bool
    def calculate_completeness(self, response: ModelResponse, task: ModelRequest) -> float
    def calculate_relevance(self, response: ModelResponse, task: ModelRequest) -> float
    def calculate_coherence(self, response: ModelResponse) -> float
```

### Cache Manager Interface

```python
class CacheManager:
    def __init__(self, db_path: Path, max_size_mb: int = 1000, default_ttl_seconds: int = 3600)
    async def get(self, cache_key: str) -> Optional[CachedResponse]
    async def set(self, cache_key: str, response: ModelResponse, ttl_seconds: Optional[int] = None) -> None
    def generate_cache_key(self, request: ModelRequest) -> str
    async def evict_expired(self) -> int
    async def evict_lru(self, target_size_mb: int) -> int
```

### Cost Tracker Interface

```python
class CostTracker:
    def __init__(self, db_path: Path, daily_budget: float = 100.0)
    async def record_cost(self, model_id: str, agent_type: str, input_tokens: int,
                         output_tokens: int, cost: float, task_id: str) -> None
    async def get_daily_cost(self, date: Optional[datetime] = None) -> float
    async def get_cost_by_model(self, start_date: datetime, end_date: datetime) -> Dict[str, float]
    async def check_budget(self) -> BudgetStatus
```

### Performance Monitor Interface

```python
class PerformanceMonitor:
    def __init__(self, db_path: Path)
    async def record_performance(self, model_id: str, agent_type: str, latency_ms: float,
                                success: bool, quality_score: float, task_id: str) -> None
    async def get_model_performance(self, model_id: str, window_hours: int = 24) -> PerformanceMetrics
    async def detect_degradation(self, model_id: str, threshold: float = 0.8) -> Optional[PerformanceDegradation]
```

## Usage Examples

### Example 1: Basic Model Selection and Request

```python
import asyncio
from pathlib import Path
from agentic_sdlc.orchestration.api_model_management import (
    ModelRequest,
    ModelRegistry,
    ModelSelector,
    HealthChecker,
    RateLimiter,
    PerformanceMonitor,
)

async def main():
    # Initialize components
    config_path = Path("config/model_registry.json")
    db_path = Path("data/api_model_management.db")
    
    registry = ModelRegistry(config_path)
    registry.load_config()
    
    health_checker = HealthChecker(registry)
    await health_checker.start()
    
    rate_limiter = RateLimiter(registry)
    performance_monitor = PerformanceMonitor(db_path)
    
    selector = ModelSelector(
        registry=registry,
        health_checker=health_checker,
        rate_limiter=rate_limiter,
        performance_monitor=performance_monitor
    )
    
    # Create request
    request = ModelRequest(
        prompt="Explain how async/await works in Python",
        parameters={"temperature": 0.7},
        task_id="task-001",
        agent_type="research",
        max_tokens=500
    )
    
    # Select model
    selection = await selector.select_model(request, "research")
    print(f"Selected: {selection.model_id}")
    print(f"Score: {selection.suitability_score:.2f}")
    print(f"Reason: {selection.selection_reason}")
    
    # Cleanup
    await health_checker.stop()

if __name__ == "__main__":
    asyncio.run(main())
```

### Example 2: Model Selection with Constraints

```python
from agentic_sdlc.orchestration.api_model_management import SelectionConstraints

# Define constraints
constraints = SelectionConstraints(
    max_cost_per_request=0.10,           # Maximum $0.10 per request
    required_capabilities=["code-generation"],  # Must support code generation
    excluded_providers=["ollama"],       # Exclude local models
    max_latency_ms=3000                  # Maximum 3 second response time
)

# Select with constraints
selection = await selector.select_model(
    task=request,
    agent_type="implementation",
    constraints=constraints
)

if selection:
    print(f"Found suitable model: {selection.model_id}")
else:
    print("No models match constraints")
```

### Example 3: Automatic Failover

```python
from agentic_sdlc.orchestration.api_model_management import (
    FailoverManager,
    APIClientManager,
    APIKeyManager,
)

# Initialize failover manager
failover_manager = FailoverManager(
    model_selector=selector,
    max_retries=3,
    base_backoff_seconds=2
)

# Initialize API client
key_manager = APIKeyManager()
key_manager.load_keys()

api_client = APIClientManager(
    api_key_manager=key_manager,
    adapters=adapters
)

# Define request function
async def make_request(model_id: str) -> ModelResponse:
    return await api_client.send_request_with_retry(
        model_id=model_id,
        request=request,
        max_retries=3
    )

# Execute with automatic failover
try:
    response = await failover_manager.execute_with_failover(
        primary_model="gpt-4-turbo",
        task=request,
        request_func=make_request
    )
    print(f"Response: {response.content}")
    print(f"Model used: {response.model_id}")
    print(f"Cost: ${response.cost:.4f}")
except Exception as e:
    print(f"All models failed: {e}")
```

### Example 4: Response Quality Evaluation

```python
from agentic_sdlc.orchestration.api_model_management import ResponseEvaluator

# Initialize evaluator
evaluator = ResponseEvaluator(
    quality_threshold=0.7,
    evaluation_window=10
)

# Make request and get response
response = await api_client.send_request("gpt-4-turbo", request)

# Evaluate quality
quality = await evaluator.evaluate_response(response, request)

print(f"Overall quality: {quality.overall_score:.2f}")
print(f"Completeness: {quality.completeness:.2f}")
print(f"Relevance: {quality.relevance:.2f}")
print(f"Coherence: {quality.coherence:.2f}")

if quality.overall_score < 0.7:
    print("WARNING: Low quality response detected")
    
    # Check if model switch recommended
    recent_scores = [0.65, 0.68, 0.62, 0.70, 0.64]
    if evaluator.should_switch_model("gpt-4-turbo", recent_scores):
        print("Model switch recommended")
```

### Example 5: Cost Tracking and Budget Management

```python
from agentic_sdlc.orchestration.api_model_management import CostTracker

# Initialize cost tracker
cost_tracker = CostTracker(
    db_path=Path("data/costs.db"),
    daily_budget=100.0
)

# Record cost after request
await cost_tracker.record_cost(
    model_id=response.model_id,
    agent_type="implementation",
    input_tokens=response.token_usage.input_tokens,
    output_tokens=response.token_usage.output_tokens,
    cost=response.cost,
    task_id=request.task_id
)

# Check budget status
budget = await cost_tracker.check_budget()
print(f"Daily budget: ${budget.daily_budget:.2f}")
print(f"Current spend: ${budget.current_spend:.2f}")
print(f"Utilization: {budget.utilization_percent:.1f}%")
print(f"Remaining: ${budget.remaining_budget:.2f}")

if budget.is_over_budget:
    print("ALERT: Budget exceeded!")

# Get cost breakdown by model
from datetime import datetime, timedelta
end_date = datetime.now()
start_date = end_date - timedelta(days=7)

costs_by_model = await cost_tracker.get_cost_by_model(start_date, end_date)
for model_id, cost in costs_by_model.items():
    print(f"{model_id}: ${cost:.2f}")
```

### Example 6: Performance Monitoring

```python
from agentic_sdlc.orchestration.api_model_management import PerformanceMonitor

# Initialize performance monitor
performance_monitor = PerformanceMonitor(db_path=Path("data/performance.db"))

# Record performance after request
await performance_monitor.record_performance(
    model_id=response.model_id,
    agent_type="implementation",
    latency_ms=response.latency_ms,
    success=True,
    quality_score=quality.overall_score,
    task_id=request.task_id
)

# Get performance metrics
metrics = await performance_monitor.get_model_performance(
    model_id="gpt-4-turbo",
    window_hours=24
)

print(f"Total requests: {metrics.total_requests}")
print(f"Success rate: {metrics.success_rate:.1f}%")
print(f"Average latency: {metrics.average_latency_ms:.0f}ms")
print(f"P95 latency: {metrics.p95_latency_ms:.0f}ms")
print(f"Average quality: {metrics.average_quality_score:.2f}")

# Detect performance degradation
degradation = await performance_monitor.detect_degradation(
    model_id="gpt-4-turbo",
    threshold=0.8
)

if degradation:
    print(f"ALERT: Performance degradation detected")
    print(f"Metric: {degradation.metric}")
    print(f"Current: {degradation.current_value:.2f}")
    print(f"Threshold: {degradation.threshold:.2f}")
```

### Example 7: Response Caching

```python
from agentic_sdlc.orchestration.api_model_management import CacheManager

# Initialize cache manager
cache_manager = CacheManager(
    db_path=Path("data/cache.db"),
    max_size_mb=1000,
    default_ttl_seconds=3600
)

# Generate cache key
cache_key = cache_manager.generate_cache_key(request)

# Check cache before making request
cached = await cache_manager.get(cache_key)
if cached:
    print("Cache hit! Using cached response")
    response = cached.response
else:
    print("Cache miss. Making API request")
    response = await api_client.send_request("gpt-4-turbo", request)
    
    # Store in cache
    await cache_manager.set(
        cache_key=cache_key,
        response=response,
        ttl_seconds=3600  # Cache for 1 hour
    )

# Periodic cache maintenance
expired_count = await cache_manager.evict_expired()
print(f"Evicted {expired_count} expired entries")

# LRU eviction if cache too large
evicted_count = await cache_manager.evict_lru(target_size_mb=800)
print(f"Evicted {evicted_count} LRU entries")
```

### Example 8: Complete End-to-End Workflow

```python
async def complete_workflow():
    """Complete workflow with all components."""
    
    # 1. Initialize all components
    config_path = Path("config/model_registry.json")
    db_path = Path("data/api_model_management.db")
    
    registry = ModelRegistry(config_path)
    registry.load_config()
    
    health_checker = HealthChecker(registry)
    await health_checker.start()
    
    rate_limiter = RateLimiter(registry)
    performance_monitor = PerformanceMonitor(db_path)
    cost_tracker = CostTracker(db_path, daily_budget=100.0)
    cache_manager = CacheManager(db_path)
    evaluator = ResponseEvaluator(quality_threshold=0.7)
    
    selector = ModelSelector(registry, health_checker, rate_limiter, performance_monitor)
    
    key_manager = APIKeyManager()
    key_manager.load_keys()
    
    api_client = APIClientManager(key_manager, adapters)
    
    failover_manager = FailoverManager(selector)
    
    # 2. Create request
    request = ModelRequest(
        prompt="Write a Python function to sort a list",
        parameters={"temperature": 0.7},
        task_id="task-123",
        agent_type="implementation",
        max_tokens=500
    )
    
    # 3. Check cache
    cache_key = cache_manager.generate_cache_key(request)
    cached = await cache_manager.get(cache_key)
    
    if cached:
        print("Using cached response")
        response = cached.response
    else:
        # 4. Select model
        selection = await selector.select_model(request, "implementation")
        print(f"Selected model: {selection.model_id}")
        
        # 5. Make request with failover
        async def make_request(model_id: str):
            return await api_client.send_request_with_retry(model_id, request)
        
        response = await failover_manager.execute_with_failover(
            primary_model=selection.model_id,
            task=request,
            request_func=make_request
        )
        
        # 6. Cache response
        await cache_manager.set(cache_key, response)
    
    # 7. Evaluate quality
    quality = await evaluator.evaluate_response(response, request)
    print(f"Quality score: {quality.overall_score:.2f}")
    
    # 8. Record metrics
    await cost_tracker.record_cost(
        model_id=response.model_id,
        agent_type="implementation",
        input_tokens=response.token_usage.input_tokens,
        output_tokens=response.token_usage.output_tokens,
        cost=response.cost,
        task_id=request.task_id
    )
    
    await performance_monitor.record_performance(
        model_id=response.model_id,
        agent_type="implementation",
        latency_ms=response.latency_ms,
        success=True,
        quality_score=quality.overall_score,
        task_id=request.task_id
    )
    
    # 9. Check budget
    budget = await cost_tracker.check_budget()
    if budget.utilization_percent > 80:
        print(f"WARNING: Budget at {budget.utilization_percent:.1f}%")
    
    # 10. Cleanup
    await health_checker.stop()
    
    return response

# Run workflow
response = await complete_workflow()
print(f"Final response: {response.content}")
```

## Integration with ModelOptimizer

The API Model Management system integrates seamlessly with the existing ModelOptimizer in `agentic_sdlc/orchestration/engine/`.

### Integration Architecture

```
┌─────────────────────┐
│  ModelOptimizer     │
│  (Existing)         │
└──────────┬──────────┘
           │
           │ Model Assignment
           ▼
┌─────────────────────┐
│  API Model          │
│  Management         │
│  (New)              │
└──────────┬──────────┘
           │
           │ API Requests
           ▼
┌─────────────────────┐
│  Provider APIs      │
│  (OpenAI, etc.)     │
└─────────────────────┘
```

### Integration Points

#### 1. Model Assignment Extension

The system extends `ModelAssignment` with API-specific details:

```python
from agentic_sdlc.orchestration.api_model_management.model_optimizer_integration import (
    APIModelAssignment,
    integrate_with_model_optimizer
)

# Extended assignment with API details
assignment = APIModelAssignment(
    model_id="gpt-4-turbo",
    agent_type="implementation",
    api_model_id="gpt-4-turbo",
    provider="openai",
    api_enabled=True
)
```

#### 2. Performance Feedback

API performance data is reported back to ModelOptimizer:

```python
from agentic_sdlc.orchestration.api_model_management.model_optimizer_integration import (
    report_performance_to_optimizer
)

# Report performance after request
report_performance_to_optimizer(
    model_optimizer=optimizer,
    model_id="gpt-4-turbo",
    agent_type="implementation",
    performance_data={
        "latency_ms": response.latency_ms,
        "success": True,
        "quality_score": quality.overall_score,
        "cost": response.cost
    }
)
```

#### 3. Failover Coordination

Failover events are coordinated with ModelOptimizer:

```python
from agentic_sdlc.orchestration.api_model_management.model_optimizer_integration import (
    coordinate_failover
)

# Coordinate failover with optimizer
alternative = await coordinate_failover(
    model_optimizer=optimizer,
    api_selector=selector,
    failed_model="gpt-4-turbo",
    task=request,
    reason=FailoverReason.RATE_LIMITED
)
```

#### 4. Complete Integration Example

```python
from agentic_sdlc.orchestration.engine.model_optimizer import ModelOptimizer
from agentic_sdlc.orchestration.api_model_management.model_optimizer_integration import (
    integrate_with_model_optimizer,
    select_model_with_optimizer
)

# Initialize ModelOptimizer (existing)
model_optimizer = ModelOptimizer(config_path="config/optimizer.json")

# Initialize API Model Management (new)
api_components = {
    "registry": registry,
    "selector": selector,
    "health_checker": health_checker,
    "rate_limiter": rate_limiter,
    "performance_monitor": performance_monitor,
    "cost_tracker": cost_tracker,
    "cache_manager": cache_manager,
    "evaluator": evaluator,
    "api_client": api_client,
    "failover_manager": failover_manager
}

# Integrate systems
integrate_with_model_optimizer(model_optimizer, api_components)

# Use integrated selection
async def make_request_with_integration(task, agent_type):
    # Select model (considers both optimizer and API availability)
    model_id = await select_model_with_optimizer(
        model_optimizer=model_optimizer,
        api_selector=selector,
        task=task,
        agent_type=agent_type
    )
    
    # Make request with API management
    response = await api_client.send_request(model_id, task)
    
    # Report back to optimizer
    report_performance_to_optimizer(
        model_optimizer=model_optimizer,
        model_id=model_id,
        agent_type=agent_type,
        performance_data={
            "latency_ms": response.latency_ms,
            "success": True,
            "cost": response.cost
        }
    )
    
    return response
```

### Backward Compatibility

The integration maintains full backward compatibility with existing ModelOptimizer interfaces:

- Existing model selection logic continues to work
- API-based models are optional additions
- Non-API models (local, embedded) continue to function
- No breaking changes to existing code

### Migration Guide

To migrate existing code to use API Model Management:

1. **Install and configure** API Model Management
2. **Add API models** to model registry
3. **Initialize components** alongside ModelOptimizer
4. **Integrate systems** using integration utilities
5. **Update request logic** to use API client
6. **Monitor and optimize** using new metrics

Example migration:

```python
# Before (existing code)
model_id, assignment = model_optimizer.select_model_for_agent(
    agent_type="implementation",
    task=task
)
response = await local_model.generate(model_id, task.prompt)

# After (with API management)
model_id = await select_model_with_optimizer(
    model_optimizer=model_optimizer,
    api_selector=selector,
    task=task,
    agent_type="implementation"
)
response = await api_client.send_request_with_retry(model_id, task)
```

## Error Handling

### Exception Hierarchy

```
APIModelError (base exception)
├── RateLimitError
├── FailoverError
├── ModelUnavailableError
├── ConfigurationError
├── AuthenticationError
├── InvalidRequestError
├── ProviderError
├── CacheError
├── BudgetExceededError
└── QualityThresholdError
```

### Error Categories

#### Transient Errors (Retryable)

- Network timeouts
- HTTP 5xx errors (server errors)
- Temporary rate limits (429 with short retry-after)
- Connection failures

#### Permanent Errors (Non-retryable)

- HTTP 4xx errors (except 429)
- Authentication failures (401, 403)
- Invalid request format (400)
- Model not found (404)
- Quota exceeded (permanent)

### Error Handling Examples

#### Example 1: Handling Rate Limit Errors

```python
from agentic_sdlc.orchestration.api_model_management import RateLimitError

try:
    response = await api_client.send_request("gpt-4-turbo", request)
except RateLimitError as e:
    print(f"Rate limited: {e.error_message}")
    print(f"Retry after: {e.retry_after_seconds}s")
    
    # Automatic failover will handle this
    response = await failover_manager.execute_with_failover(
        primary_model="gpt-4-turbo",
        task=request,
        request_func=lambda m: api_client.send_request(m, request)
    )
```

#### Example 2: Handling Model Unavailable

```python
from agentic_sdlc.orchestration.api_model_management import ModelUnavailableError

try:
    response = await api_client.send_request("gpt-4-turbo", request)
except ModelUnavailableError as e:
    print(f"Model unavailable: {e.model_id}")
    print(f"Reason: {e.error_message}")
    
    # Select alternative
    alternative = await failover_manager.select_alternative(
        failed_model="gpt-4-turbo",
        task=request,
        reason=FailoverReason.UNAVAILABLE
    )
    
    if alternative:
        response = await api_client.send_request(alternative, request)
    else:
        raise Exception("No alternative models available")
```

#### Example 3: Handling Budget Exceeded

```python
from agentic_sdlc.orchestration.api_model_management import BudgetExceededError

try:
    # Check budget before request
    budget = await cost_tracker.check_budget()
    if budget.is_over_budget:
        raise BudgetExceededError(
            f"Daily budget of ${budget.daily_budget} exceeded"
        )
    
    response = await api_client.send_request("gpt-4-turbo", request)
    
except BudgetExceededError as e:
    print(f"Budget exceeded: {e.error_message}")
    
    # Use cheaper model
    constraints = SelectionConstraints(
        max_cost_per_request=0.01,  # Very low cost
        required_capabilities=["text-generation"]
    )
    
    selection = await selector.select_model(request, "implementation", constraints)
    response = await api_client.send_request(selection.model_id, request)
```

#### Example 4: Comprehensive Error Handling

```python
from agentic_sdlc.orchestration.api_model_management import (
    APIModelError,
    RateLimitError,
    ModelUnavailableError,
    AuthenticationError,
    BudgetExceededError
)

async def robust_request(request: ModelRequest) -> ModelResponse:
    """Make request with comprehensive error handling."""
    
    max_attempts = 3
    attempt = 0
    
    while attempt < max_attempts:
        try:
            # Check budget
            budget = await cost_tracker.check_budget()
            if budget.is_over_budget:
                # Use cheapest available model
                constraints = SelectionConstraints(max_cost_per_request=0.01)
                selection = await selector.select_model(request, "implementation", constraints)
            else:
                # Normal selection
                selection = await selector.select_model(request, "implementation")
            
            # Make request with failover
            response = await failover_manager.execute_with_failover(
                primary_model=selection.model_id,
                task=request,
                request_func=lambda m: api_client.send_request_with_retry(m, request)
            )
            
            return response
            
        except RateLimitError as e:
            print(f"Rate limited, attempt {attempt + 1}/{max_attempts}")
            await asyncio.sleep(e.retry_after_seconds or 60)
            attempt += 1
            
        except ModelUnavailableError as e:
            print(f"Model unavailable: {e.model_id}, attempt {attempt + 1}/{max_attempts}")
            attempt += 1
            
        except AuthenticationError as e:
            print(f"Authentication failed: {e.error_message}")
            raise  # Don't retry authentication errors
            
        except BudgetExceededError as e:
            print(f"Budget exceeded: {e.error_message}")
            # Continue with cheaper model (handled above)
            attempt += 1
            
        except APIModelError as e:
            print(f"API error: {e.error_message}")
            if not e.is_retryable:
                raise  # Don't retry permanent errors
            attempt += 1
    
    raise Exception(f"Failed after {max_attempts} attempts")
```

## Best Practices

### 1. Component Initialization

Always initialize components in the correct order:

```python
# 1. Registry (no dependencies)
registry = ModelRegistry(config_path)
registry.load_config()

# 2. Health Checker (depends on registry)
health_checker = HealthChecker(registry)
await health_checker.start()

# 3. Rate Limiter (depends on registry)
rate_limiter = RateLimiter(registry)

# 4. Performance Monitor (no dependencies)
performance_monitor = PerformanceMonitor(db_path)

# 5. Selector (depends on all above)
selector = ModelSelector(registry, health_checker, rate_limiter, performance_monitor)

# 6. Other components
cost_tracker = CostTracker(db_path)
cache_manager = CacheManager(db_path)
evaluator = ResponseEvaluator()

# 7. API Client (depends on key manager and adapters)
key_manager = APIKeyManager()
api_client = APIClientManager(key_manager, adapters)

# 8. Failover Manager (depends on selector)
failover_manager = FailoverManager(selector)
```

### 2. Resource Cleanup

Always clean up resources properly:

```python
try:
    # Start health checker
    await health_checker.start()
    
    # Your application logic
    response = await make_request(request)
    
finally:
    # Always stop health checker
    await health_checker.stop()
```

### 3. Caching Strategy

Use caching effectively:

```python
# Cache deterministic requests
if request.temperature == 0:  # Deterministic
    cache_key = cache_manager.generate_cache_key(request)
    cached = await cache_manager.get(cache_key)
    if cached:
        return cached.response

# Don't cache non-deterministic requests
if request.temperature > 0:  # Non-deterministic
    # Skip cache, make fresh request
    response = await api_client.send_request(model_id, request)
```

### 4. Cost Optimization

Monitor and optimize costs:

```python
# Check budget before expensive operations
budget = await cost_tracker.check_budget()
if budget.utilization_percent > 80:
    # Use cheaper models
    constraints = SelectionConstraints(max_cost_per_request=0.05)
    selection = await selector.select_model(request, agent_type, constraints)
else:
    # Normal selection
    selection = await selector.select_model(request, agent_type)
```

### 5. Performance Monitoring

Track performance metrics:

```python
# Record all requests
await performance_monitor.record_performance(
    model_id=response.model_id,
    agent_type=agent_type,
    latency_ms=response.latency_ms,
    success=True,
    quality_score=quality.overall_score,
    task_id=request.task_id
)

# Periodically check for degradation
degradation = await performance_monitor.detect_degradation(
    model_id="gpt-4-turbo",
    threshold=0.8
)
if degradation:
    # Alert or switch models
    print(f"Performance degradation: {degradation.metric}")
```

### 6. Error Handling

Implement robust error handling:

```python
# Always use try-except for API calls
try:
    response = await api_client.send_request(model_id, request)
except APIModelError as e:
    if e.is_retryable:
        # Retry with backoff
        await asyncio.sleep(2)
        response = await api_client.send_request(model_id, request)
    else:
        # Log and raise
        logger.error(f"Permanent error: {e.error_message}")
        raise
```

### 7. Configuration Management

Keep configuration up to date:

```python
# Periodically reload configuration
async def config_reload_loop():
    while True:
        await asyncio.sleep(300)  # Every 5 minutes
        registry.load_config()
        print("Configuration reloaded")

# Start reload loop
asyncio.create_task(config_reload_loop())
```

### 8. Logging

Use appropriate log levels:

```python
import logging

logger = logging.getLogger("api_model_management")
logger.setLevel(logging.INFO)

# INFO: Normal operations
logger.info(f"Selected model: {selection.model_id}")

# WARNING: Potential issues
logger.warning(f"Budget at {budget.utilization_percent}%")

# ERROR: Errors that need attention
logger.error(f"Model unavailable: {model_id}")

# DEBUG: Detailed debugging
logger.debug(f"Cache key: {cache_key}")
```

---

## Advanced Usage Examples

### Example 9: Multi-Provider Setup with Load Balancing

```python
async def setup_multi_provider():
    """Set up system with multiple providers for load balancing."""
    
    # Configure multiple API keys for load distribution
    key_manager = APIKeyManager()
    key_manager.add_key("openai", os.getenv("OPENAI_API_KEY"))
    key_manager.add_key("openai", os.getenv("OPENAI_API_KEY_2"))
    key_manager.add_key("anthropic", os.getenv("ANTHROPIC_API_KEY"))
    key_manager.add_key("google", os.getenv("GOOGLE_API_KEY"))
    
    # Initialize components
    registry = ModelRegistry(Path("config/model_registry.json"))
    registry.load_config()
    
    health_checker = HealthChecker(registry, check_interval_seconds=30)
    await health_checker.start()
    
    rate_limiter = RateLimiter(registry)
    performance_monitor = PerformanceMonitor(Path("data/performance.db"))
    
    selector = ModelSelector(registry, health_checker, rate_limiter, performance_monitor)
    
    # Process multiple requests concurrently
    tasks = [
        create_request(f"task-{i}", f"Explain concept {i}")
        for i in range(10)
    ]
    
    # Select models for all tasks
    selections = await asyncio.gather(*[
        selector.select_model(task, "research")
        for task in tasks
    ])
    
    # Verify load distribution
    providers = [s.model_metadata.provider for s in selections]
    print(f"Provider distribution: {Counter(providers)}")
    
    await health_checker.stop()
```

### Example 10: Custom Selection Strategy

```python
async def custom_selection_strategy():
    """Implement custom model selection logic."""
    
    # Define custom constraints based on task complexity
    def get_constraints_for_task(task: ModelRequest) -> SelectionConstraints:
        # Simple tasks: prioritize cost
        if len(task.prompt) < 100:
            return SelectionConstraints(
                max_cost_per_request=0.01,
                required_capabilities=["text-generation"]
            )
        # Complex tasks: prioritize quality
        elif len(task.prompt) > 1000:
            return SelectionConstraints(
                required_capabilities=["analysis", "reasoning"],
                excluded_providers=["ollama"]
            )
        # Medium tasks: balanced
        else:
            return SelectionConstraints(
                max_cost_per_request=0.10,
                required_capabilities=["text-generation"]
            )
    
    # Apply custom strategy
    task = ModelRequest(
        prompt="Complex analysis task with detailed requirements...",
        parameters={"temperature": 0.7},
        task_id="task-complex",
        agent_type="analysis",
        max_tokens=2000
    )
    
    constraints = get_constraints_for_task(task)
    selection = await selector.select_model(task, "analysis", constraints)
    
    print(f"Selected {selection.model_id} for complex task")
    print(f"Estimated cost: ${selection.model_metadata.cost_per_1k_input_tokens * 2:.4f}")
```

### Example 11: Real-Time Monitoring Dashboard

```python
async def monitoring_dashboard():
    """Create real-time monitoring dashboard."""
    
    while True:
        # Get current status
        budget = await cost_tracker.check_budget()
        
        # Get performance for all models
        models = registry.get_models_by_provider("openai")
        
        print("\n" + "="*60)
        print("API Model Management Dashboard")
        print("="*60)
        
        # Budget status
        print(f"\nBudget Status:")
        print(f"  Daily Limit: ${budget.daily_budget:.2f}")
        print(f"  Current Spend: ${budget.current_spend:.2f}")
        print(f"  Utilization: {budget.utilization_percent:.1f}%")
        print(f"  Remaining: ${budget.remaining_budget:.2f}")
        
        # Model status
        print(f"\nModel Status:")
        for model in models:
            is_available = health_checker.is_model_available(model.id)
            is_rate_limited = rate_limiter.is_rate_limited(model.id)
            
            status = "✓ Available"
            if is_rate_limited:
                status = "⚠ Rate Limited"
            elif not is_available:
                status = "✗ Unavailable"
            
            print(f"  {model.name}: {status}")
        
        # Performance metrics
        print(f"\nPerformance (Last 24h):")
        for model in models:
            metrics = await performance_monitor.get_model_performance(
                model.id,
                window_hours=24
            )
            
            if metrics.total_requests > 0:
                print(f"  {model.name}:")
                print(f"    Requests: {metrics.total_requests}")
                print(f"    Success Rate: {metrics.success_rate:.1f}%")
                print(f"    Avg Latency: {metrics.average_latency_ms:.0f}ms")
                print(f"    Avg Quality: {metrics.average_quality_score:.2f}")
        
        # Wait before next update
        await asyncio.sleep(60)
```

### Example 12: Batch Processing with Cost Optimization

```python
async def batch_process_with_cost_optimization():
    """Process batch of tasks with cost optimization."""
    
    # Load tasks
    tasks = load_tasks_from_file("tasks.json")
    
    # Sort by priority
    high_priority = [t for t in tasks if t.priority == "HIGH"]
    medium_priority = [t for t in tasks if t.priority == "MEDIUM"]
    low_priority = [t for t in tasks if t.priority == "LOW"]
    
    results = []
    
    # Process high priority first (quality over cost)
    for task in high_priority:
        constraints = SelectionConstraints(
            required_capabilities=["analysis", "reasoning"]
        )
        selection = await selector.select_model(task, "analysis", constraints)
        result = await process_task(task, selection.model_id)
        results.append(result)
    
    # Check budget before continuing
    budget = await cost_tracker.check_budget()
    if budget.utilization_percent > 80:
        print("WARNING: Budget at 80%, switching to cost-optimized mode")
        
        # Use cheaper models for remaining tasks
        constraints = SelectionConstraints(
            max_cost_per_request=0.01,
            required_capabilities=["text-generation"]
        )
    else:
        constraints = None
    
    # Process medium and low priority
    for task in medium_priority + low_priority:
        selection = await selector.select_model(task, "analysis", constraints)
        result = await process_task(task, selection.model_id)
        results.append(result)
    
    # Generate report
    total_cost = sum(r.cost for r in results)
    print(f"\nBatch Processing Complete:")
    print(f"  Total Tasks: {len(results)}")
    print(f"  Total Cost: ${total_cost:.2f}")
    print(f"  Average Cost: ${total_cost/len(results):.4f}")
    
    return results
```

### Example 13: A/B Testing Different Models

```python
async def ab_test_models():
    """A/B test different models for the same task."""
    
    # Define test task
    test_prompt = "Explain the concept of recursion in programming"
    
    # Test multiple models
    models_to_test = ["gpt-4-turbo", "claude-3.5-sonnet", "gemini-pro"]
    
    results = {}
    
    for model_id in models_to_test:
        # Create request
        request = ModelRequest(
            prompt=test_prompt,
            parameters={"temperature": 0.7},
            task_id=f"ab-test-{model_id}",
            agent_type="research",
            max_tokens=500
        )
        
        # Make request
        start_time = time.time()
        response = await api_client.send_request(model_id, request)
        end_time = time.time()
        
        # Evaluate quality
        quality = await evaluator.evaluate_response(response, request)
        
        # Store results
        results[model_id] = {
            'response': response.content,
            'latency_ms': (end_time - start_time) * 1000,
            'cost': response.cost,
            'quality_score': quality.overall_score,
            'completeness': quality.completeness,
            'relevance': quality.relevance,
            'coherence': quality.coherence
        }
    
    # Compare results
    print("\nA/B Test Results:")
    print("="*80)
    
    for model_id, result in results.items():
        print(f"\n{model_id}:")
        print(f"  Quality Score: {result['quality_score']:.2f}")
        print(f"  Latency: {result['latency_ms']:.0f}ms")
        print(f"  Cost: ${result['cost']:.4f}")
        print(f"  Completeness: {result['completeness']:.2f}")
        print(f"  Relevance: {result['relevance']:.2f}")
        print(f"  Coherence: {result['coherence']:.2f}")
    
    # Determine winner
    winner = max(results.items(), key=lambda x: x[1]['quality_score'])
    print(f"\nWinner: {winner[0]} (Quality: {winner[1]['quality_score']:.2f})")
    
    return results
```

### Example 14: Graceful Degradation in Production

```python
async def production_request_with_degradation():
    """Handle requests with graceful degradation."""
    
    try:
        # Try primary workflow
        selection = await selector.select_model(request, "implementation")
        response = await api_client.send_request_with_retry(
            selection.model_id,
            request
        )
        
        # Evaluate quality
        quality = await evaluator.evaluate_response(response, request)
        
        # Cache response
        cache_key = cache_manager.generate_cache_key(request)
        await cache_manager.set(cache_key, response)
        
        # Record metrics
        await performance_monitor.record_performance(
            model_id=response.model_id,
            agent_type="implementation",
            latency_ms=response.latency_ms,
            success=True,
            quality_score=quality.overall_score,
            task_id=request.task_id
        )
        
        return response
        
    except CacheError as e:
        # Cache failed, continue without caching
        logger.warning(f"Cache unavailable: {e}")
        
        selection = await selector.select_model(request, "implementation")
        response = await api_client.send_request_with_retry(
            selection.model_id,
            request
        )
        
        return response
        
    except PerformanceMonitorError as e:
        # Performance monitoring failed, continue without metrics
        logger.warning(f"Performance monitoring unavailable: {e}")
        
        selection = await selector.select_model(request, "implementation")
        response = await api_client.send_request_with_retry(
            selection.model_id,
            request
        )
        
        return response
        
    except APIModelError as e:
        # All API models failed, use fallback
        logger.error(f"All API models failed: {e}")
        
        # Use local fallback model
        fallback_response = await local_model.generate(request.prompt)
        
        return fallback_response
```

## Additional Resources

- **[Main README](README.md)**: Overview and quick start guide
- **[Configuration Guide](config/CONFIGURATION_GUIDE.md)**: Detailed configuration documentation
- **[Model Optimizer Integration](MODEL_OPTIMIZER_INTEGRATION_GUIDE.md)**: Integration details
- **[Error Handling Guide](ERROR_HANDLING_GUIDE.md)**: Comprehensive error handling strategies
- **[Concurrency Guide](CONCURRENCY_GUIDE.md)**: Async/await patterns and best practices
- **[Graceful Degradation Guide](GRACEFUL_DEGRADATION_GUIDE.md)**: Handling component failures

## Support

For issues, questions, or contributions:
- Review system logs for detailed error information
- Check configuration validation errors
- Consult provider API documentation
- Review performance metrics and alerts
- See [README](README.md) for troubleshooting guide
