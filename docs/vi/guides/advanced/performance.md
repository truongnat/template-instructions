# Tối Ưu Hóa Hiệu Suất (Performance Optimization)

**Phiên bản**: 3.0.0  
**Cập nhật lần cuối**: 11/02/2026


## Giới Thiệu

Tài liệu này cung cấp hướng dẫn chi tiết về cách tối ưu hóa hiệu suất của hệ thống Agentic SDLC, bao gồm performance tuning, benchmarking, caching strategies, và parallel execution.

## Mục Tiêu Học Tập

Sau khi đọc tài liệu này, bạn sẽ có thể:
- Đo lường và phân tích hiệu suất của hệ thống
- Áp dụng các kỹ thuật caching để giảm latency
- Tối ưu hóa parallel execution cho workflows
- Sử dụng benchmarking tools để đánh giá performance
- Xác định và giải quyết các bottlenecks

## Performance Tuning

### 1. Model Client Optimization

Tối ưu hóa việc gọi LLM để giảm latency và chi phí:

```python
from agentic_sdlc.orchestration.model_client import ModelConfig, create_model_client

# Cấu hình model với timeout và retry hợp lý
config = ModelConfig(
    provider="openai",
    model_name="gpt-4",
    api_key="your-api-key",
    temperature=0.7,
    max_tokens=2000,
    timeout=30,  # Timeout 30 giây
    max_retries=3,  # Retry tối đa 3 lần
    retry_delay=1.0  # Delay 1 giây giữa các retry
)

client = create_model_client(config)

# Sử dụng streaming để giảm perceived latency
response = client.generate(
    prompt="Analyze this code...",
    stream=True  # Enable streaming
)

for chunk in response:
    print(chunk, end="", flush=True)
```text

### 2. Agent Configuration Tuning

Tối ưu hóa cấu hình agent để cân bằng giữa quality và speed:

```python
from agentic_sdlc.orchestration.agent import create_agent, AgentType

# Agent với cấu hình tối ưu cho performance
fast_agent = create_agent(
    name="fast-developer",
    agent_type=AgentType.DEVELOPER,
    model_name="gpt-3.5-turbo",  # Model nhanh hơn
    max_iterations=3,  # Giới hạn iterations
    timeout=60,  # Timeout 60 giây
    system_prompt="You are a fast code generator. Provide concise solutions."
)

# Agent với cấu hình tối ưu cho quality
quality_agent = create_agent(
    name="quality-developer",
    agent_type=AgentType.DEVELOPER,
    model_name="gpt-4",  # Model chất lượng cao
    max_iterations=10,  # Nhiều iterations hơn
    timeout=300,  # Timeout dài hơn
    system_prompt="You are a thorough code generator. Provide detailed solutions."
)
```text

### 3. Workflow Optimization

Tối ưu hóa workflow execution:

```python
from agentic_sdlc.orchestration.workflow import WorkflowBuilder, WorkflowStep

# Workflow với parallel execution
builder = WorkflowBuilder("optimized-workflow")

# Các tasks độc lập chạy song song
builder.add_step(WorkflowStep(
    name="lint-code",
    action="run_linter",
    parameters={"files": "src/"},
    parallel_group="validation"  # Nhóm parallel
))

builder.add_step(WorkflowStep(
    name="type-check",
    action="run_type_checker",
    parameters={"files": "src/"},
    parallel_group="validation"  # Cùng nhóm parallel
))

builder.add_step(WorkflowStep(
    name="run-tests",
    action="run_tests",
    parameters={"test_dir": "tests/"},
    dependencies=["lint-code", "type-check"]  # Chạy sau validation
))

workflow = builder.build()
```text

## Caching Strategies

### 1. Response Caching

Cache LLM responses để tránh gọi API lặp lại:

```python
from agentic_sdlc.intelligence.cache import ResponseCache
from functools import lru_cache
import hashlib

class CachedModelClient:
    """Model client với response caching."""
    
    def __init__(self, client, cache_size=1000):
        self.client = client
        self.cache = ResponseCache(max_size=cache_size)
    
    def generate(self, prompt: str, **kwargs) -> str:
        """Generate với caching."""
        # Tạo cache key từ prompt và parameters
        cache_key = self._create_cache_key(prompt, kwargs)
        
        # Check cache
        cached_response = self.cache.get(cache_key)
        if cached_response:
            return cached_response
        
        # Generate nếu không có trong cache
        response = self.client.generate(prompt, **kwargs)
        
        # Lưu vào cache
        self.cache.set(cache_key, response)
        
        return response
    
    def _create_cache_key(self, prompt: str, kwargs: dict) -> str:
        """Tạo cache key từ prompt và parameters."""
        key_data = f"{prompt}:{sorted(kwargs.items())}"
        return hashlib.sha256(key_data.encode()).hexdigest()

# Sử dụng cached client
from agentic_sdlc.orchestration.model_client import create_model_client

base_client = create_model_client(config)
cached_client = CachedModelClient(base_client, cache_size=1000)

# Lần gọi đầu tiên - gọi API
response1 = cached_client.generate("Write a function to sort a list")

# Lần gọi thứ hai với cùng prompt - lấy từ cache
response2 = cached_client.generate("Write a function to sort a list")
```text

### 2. Workflow Result Caching

Cache kết quả workflow để tránh re-execution:

```python
from agentic_sdlc.infrastructure.workflow_engine import WorkflowEngine
from agentic_sdlc.intelligence.cache import WorkflowCache

class CachedWorkflowEngine(WorkflowEngine):
    """Workflow engine với result caching."""
    
    def __init__(self, cache_ttl=3600):
        super().__init__()
        self.cache = WorkflowCache(ttl=cache_ttl)
    
    def execute(self, workflow, context=None):
        """Execute workflow với caching."""
        # Tạo cache key từ workflow và context
        cache_key = self._create_workflow_key(workflow, context)
        
        # Check cache
        cached_result = self.cache.get(cache_key)
        if cached_result:
            return cached_result
        
        # Execute workflow
        result = super().execute(workflow, context)
        
        # Cache result
        self.cache.set(cache_key, result)
        
        return result
    
    def _create_workflow_key(self, workflow, context):
        """Tạo cache key cho workflow."""
        workflow_hash = workflow.get_hash()
        context_hash = hash(frozenset(context.items())) if context else 0
        return f"{workflow_hash}:{context_hash}"
```text

### 3. Learning Data Caching

Cache learning data để tăng tốc similarity search:

```python
from agentic_sdlc.intelligence.learner import Learner

# Learner với in-memory cache
learner = Learner(
    storage_backend="memory",  # In-memory cache
    cache_size=10000
)

# Pre-load frequently accessed patterns
learner.preload_patterns([
    "common_errors",
    "successful_solutions",
    "best_practices"
])

# Find similar với caching
similar = learner.find_similar(
    task_description="implement authentication",
    limit=5,
    use_cache=True  # Sử dụng cache
)
```text

## Parallel Execution

### 1. Parallel Agent Execution

Chạy nhiều agents song song:

```python
from agentic_sdlc.orchestration.agent import create_agent
from concurrent.futures import ThreadPoolExecutor, as_completed

def execute_agents_parallel(agents, tasks):
    """Execute nhiều agents song song."""
    results = {}
    
    with ThreadPoolExecutor(max_workers=len(agents)) as executor:
        # Submit tất cả tasks
        future_to_agent = {
            executor.submit(agent.execute, task): (agent.name, task)
            for agent, task in zip(agents, tasks)
        }
        
        # Collect results khi hoàn thành
        for future in as_completed(future_to_agent):
            agent_name, task = future_to_agent[future]
            try:
                result = future.result()
                results[agent_name] = result
            except Exception as e:
                results[agent_name] = {"error": str(e)}
    
    return results

# Tạo agents
agents = [
    create_agent("dev-1", AgentType.DEVELOPER),
    create_agent("dev-2", AgentType.DEVELOPER),
    create_agent("tester-1", AgentType.TESTER)
]

# Tasks
tasks = [
    {"action": "implement_feature", "feature": "auth"},
    {"action": "implement_feature", "feature": "api"},
    {"action": "write_tests", "module": "auth"}
]

# Execute parallel
results = execute_agents_parallel(agents, tasks)
```text

### 2. Parallel Workflow Steps

Chạy workflow steps song song:

```python
from agentic_sdlc.infrastructure.workflow_engine import WorkflowEngine

class ParallelWorkflowEngine(WorkflowEngine):
    """Workflow engine với parallel execution."""
    
    def __init__(self, max_workers=4):
        super().__init__()
        self.max_workers = max_workers
    
    def execute(self, workflow, context=None):
        """Execute workflow với parallel steps."""
        # Group steps theo parallel groups
        parallel_groups = self._group_parallel_steps(workflow)
        
        results = {}
        
        for group in parallel_groups:
            if len(group) == 1:
                # Single step - execute normally
                step = group[0]
                results[step.name] = self._execute_step(step, context)
            else:
                # Multiple steps - execute parallel
                group_results = self._execute_parallel(group, context)
                results.update(group_results)
        
        return results
    
    def _execute_parallel(self, steps, context):
        """Execute steps song song."""
        results = {}
        
        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            future_to_step = {
                executor.submit(self._execute_step, step, context): step
                for step in steps
            }
            
            for future in as_completed(future_to_step):
                step = future_to_step[future]
                results[step.name] = future.result()
        
        return results
```text

### 3. Async Agent Communication

Sử dụng async communication cho multi-agent systems:

```python
import asyncio
from agentic_sdlc.intelligence.collaborator import TeamCoordinator

async def async_agent_workflow():
    """Async workflow với multiple agents."""
    coordinator = TeamCoordinator()
    
    # Register agents
    agents = [
        create_agent("pm", AgentType.PROJECT_MANAGER),
        create_agent("dev", AgentType.DEVELOPER),
        create_agent("tester", AgentType.TESTER)
    ]
    
    for agent in agents:
        coordinator.register_agent(agent)
    
    # Start session
    session_id = coordinator.start_session("feature-development")
    
    # Execute tasks async
    tasks = [
        coordinator.send_message_async(session_id, "pm", "dev", 
                                      {"action": "plan_feature"}),
        coordinator.send_message_async(session_id, "dev", "tester",
                                      {"action": "implement_feature"}),
        coordinator.send_message_async(session_id, "tester", "pm",
                                      {"action": "test_feature"})
    ]
    
    # Wait for all tasks
    results = await asyncio.gather(*tasks)
    
    return results

# Run async workflow
results = asyncio.run(async_agent_workflow())
```text

## Benchmarking

### 1. Performance Metrics

Đo lường performance metrics:

```python
from agentic_sdlc.intelligence.monitor import Monitor
import time

class PerformanceBenchmark:
    """Benchmark performance của hệ thống."""
    
    def __init__(self):
        self.monitor = Monitor()
    
    def benchmark_agent(self, agent, task, iterations=10):
        """Benchmark agent execution."""
        execution_times = []
        
        for i in range(iterations):
            start_time = time.time()
            result = agent.execute(task)
            end_time = time.time()
            
            execution_time = end_time - start_time
            execution_times.append(execution_time)
            
            # Record metric
            self.monitor.record_metric(
                "agent_execution_time",
                execution_time,
                {"agent": agent.name, "iteration": i}
            )
        
        # Calculate statistics
        avg_time = sum(execution_times) / len(execution_times)
        min_time = min(execution_times)
        max_time = max(execution_times)
        
        return {
            "average": avg_time,
            "min": min_time,
            "max": max_time,
            "iterations": iterations
        }
    
    def benchmark_workflow(self, workflow, iterations=5):
        """Benchmark workflow execution."""
        engine = WorkflowEngine()
        execution_times = []
        
        for i in range(iterations):
            start_time = time.time()
            result = engine.execute(workflow)
            end_time = time.time()
            
            execution_time = end_time - start_time
            execution_times.append(execution_time)
        
        return {
            "average": sum(execution_times) / len(execution_times),
            "min": min(execution_times),
            "max": max(execution_times)
        }

# Sử dụng benchmark
benchmark = PerformanceBenchmark()

agent = create_agent("test-agent", AgentType.DEVELOPER)
task = {"action": "write_function", "description": "Sort a list"}

results = benchmark.benchmark_agent(agent, task, iterations=10)
print(f"Average execution time: {results['average']:.2f}s")
```text

### 2. Load Testing

Test performance dưới load cao:

```python
from concurrent.futures import ThreadPoolExecutor
import time

class LoadTester:
    """Load testing cho hệ thống."""
    
    def __init__(self, max_workers=10):
        self.max_workers = max_workers
    
    def load_test(self, target_func, num_requests=100):
        """Thực hiện load test."""
        start_time = time.time()
        
        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            futures = [
                executor.submit(target_func)
                for _ in range(num_requests)
            ]
            
            # Wait for all requests
            results = [f.result() for f in futures]
        
        end_time = time.time()
        total_time = end_time - start_time
        
        return {
            "total_requests": num_requests,
            "total_time": total_time,
            "requests_per_second": num_requests / total_time,
            "avg_response_time": total_time / num_requests
        }

# Load test agent execution
def test_agent_execution():
    agent = create_agent("load-test-agent", AgentType.DEVELOPER)
    return agent.execute({"action": "simple_task"})

tester = LoadTester(max_workers=10)
results = tester.load_test(test_agent_execution, num_requests=100)

print(f"Requests per second: {results['requests_per_second']:.2f}")
print(f"Average response time: {results['avg_response_time']:.3f}s")
```text

### 3. Memory Profiling

Profile memory usage:

```python
import tracemalloc
from agentic_sdlc.orchestration.agent import create_agent

def profile_memory(func):
    """Decorator để profile memory usage."""
    def wrapper(*args, **kwargs):
        # Start tracing
        tracemalloc.start()
        
        # Execute function
        result = func(*args, **kwargs)
        
        # Get memory stats
        current, peak = tracemalloc.get_traced_memory()
        tracemalloc.stop()
        
        print(f"Current memory: {current / 1024 / 1024:.2f} MB")
        print(f"Peak memory: {peak / 1024 / 1024:.2f} MB")
        
        return result
    
    return wrapper

@profile_memory
def create_and_execute_agent():
    """Test function với memory profiling."""
    agent = create_agent("memory-test", AgentType.DEVELOPER)
    return agent.execute({"action": "complex_task"})

# Run với memory profiling
result = create_and_execute_agent()
```text

## Best Practices

### 1. Connection Pooling

Sử dụng connection pooling cho external services:

```python
from agentic_sdlc.plugins.base import Plugin
import requests
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry

class OptimizedAPIPlugin(Plugin):
    """Plugin với connection pooling."""
    
    def initialize(self):
        """Initialize với connection pool."""
        # Configure retry strategy
        retry_strategy = Retry(
            total=3,
            backoff_factor=1,
            status_forcelist=[429, 500, 502, 503, 504]
        )
        
        # Create session với connection pooling
        self.session = requests.Session()
        adapter = HTTPAdapter(
            pool_connections=10,
            pool_maxsize=20,
            max_retries=retry_strategy
        )
        self.session.mount("http://", adapter)
        self.session.mount("https://", adapter)
    
    def call_api(self, url, data):
        """Call API với connection pooling."""
        return self.session.post(url, json=data)
```text

### 2. Lazy Loading

Lazy load resources khi cần:

```python
from agentic_sdlc.orchestration.agent import Agent

class LazyAgent(Agent):
    """Agent với lazy loading."""
    
    def __init__(self, name, agent_type):
        super().__init__(name, agent_type)
        self._model_client = None
        self._tools = None
    
    @property
    def model_client(self):
        """Lazy load model client."""
        if self._model_client is None:
            self._model_client = self._create_model_client()
        return self._model_client
    
    @property
    def tools(self):
        """Lazy load tools."""
        if self._tools is None:
            self._tools = self._load_tools()
        return self._tools
```text

### 3. Resource Cleanup

Cleanup resources sau khi sử dụng:

```python
from contextlib import contextmanager

@contextmanager
def agent_context(agent_name, agent_type):
    """Context manager cho agent lifecycle."""
    agent = create_agent(agent_name, agent_type)
    try:
        yield agent
    finally:
        # Cleanup resources
        agent.cleanup()

# Sử dụng context manager
with agent_context("temp-agent", AgentType.DEVELOPER) as agent:
    result = agent.execute(task)
    # Agent tự động cleanup khi exit context
```text

## Anti-Patterns

### ❌ Anti-Pattern 1: Synchronous Blocking Calls

```python
# BAD: Blocking calls trong loop
for task in tasks:
    result = agent.execute(task)  # Blocks cho mỗi task
    results.append(result)
```text

```python
# GOOD: Parallel execution
with ThreadPoolExecutor() as executor:
    results = list(executor.map(agent.execute, tasks))
```text

### ❌ Anti-Pattern 2: No Caching

```python
# BAD: Gọi API lặp lại với cùng input
for i in range(10):
    response = client.generate("same prompt")
```text

```python
# GOOD: Cache responses
cache = {}
prompt = "same prompt"
if prompt not in cache:
    cache[prompt] = client.generate(prompt)
response = cache[prompt]
```text

### ❌ Anti-Pattern 3: Unbounded Resource Usage

```python
# BAD: Không giới hạn concurrent requests
futures = [executor.submit(task) for task in huge_task_list]
```text

```python
# GOOD: Giới hạn concurrent workers
with ThreadPoolExecutor(max_workers=10) as executor:
    futures = [executor.submit(task) for task in huge_task_list]
```

## Troubleshooting

### Issue: Slow Agent Execution

**Triệu chứng**: Agent mất nhiều thời gian để complete tasks

**Giải pháp**:
1. Giảm `max_iterations` trong agent config
2. Sử dụng faster model (gpt-3.5-turbo thay vì gpt-4)
3. Enable response caching
4. Optimize system prompt để ngắn gọn hơn

### Issue: High Memory Usage

**Triệu chứng**: Memory usage tăng cao theo thời gian

**Giải pháp**:
1. Implement cache eviction policies
2. Cleanup agents sau khi sử dụng
3. Sử dụng lazy loading cho resources
4. Profile memory để tìm leaks

### Issue: API Rate Limiting

**Triệu chứng**: Nhận 429 errors từ LLM provider

**Giải pháp**:
1. Implement exponential backoff
2. Sử dụng connection pooling
3. Enable request caching
4. Distribute load across multiple API keys

## Tài Liệu Liên Quan

- [Scalability Guide](scalability.md) - Scaling strategies
- [Deployment Guide](deployment.md) - Production deployment
- [Monitoring Guide](../intelligence/monitoring.md) - Performance monitoring
- [Caching Examples](../../examples/intermediate/15-caching.py) - Caching implementation
