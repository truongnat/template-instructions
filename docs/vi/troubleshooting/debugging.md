# Hướng Dẫn Debug

**Phiên bản**: 3.0.0  
**Cập nhật lần cuối**: 11/02/2026


## Giới Thiệu

Tài liệu này cung cấp hướng dẫn chi tiết về cách debug các vấn đề trong Agentic SDLC v3.0.0, bao gồm cấu hình logging, interpretation của log messages, và các kỹ thuật debugging nâng cao.

---

## Cấu Hình Debug Logging

### 1. Enable Debug Mode

**Cách 1: Sử dụng Environment Variable**

```bash
export AGENTIC_SDLC_LOG_LEVEL=DEBUG
export AGENTIC_SDLC_DEBUG=true
```text

**Cách 2: Cấu hình trong config.yaml**

```yaml
logging:
  level: DEBUG
  format: "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
  output:
    console: true
    file: "./logs/agentic_sdlc.log"
  debug_mode: true
```text

**Cách 3: Programmatic Configuration**

```python
import logging
from agentic_sdlc.core.logging import setup_logging

# Setup debug logging
setup_logging(
    level=logging.DEBUG,
    log_file="./logs/debug.log",
    console_output=True,
    include_timestamp=True,
    include_module=True
)
```text

### 2. Logging Levels

Agentic SDLC sử dụng standard Python logging levels:

| Level | Mục Đích | Khi Nào Sử Dụng |
|-------|----------|------------------|
| DEBUG | Chi tiết nhất, mọi thông tin | Development và troubleshooting |
| INFO | Thông tin general về execution | Normal operation monitoring |
| WARNING | Cảnh báo về potential issues | Detect anomalies |
| ERROR | Lỗi không critical | Handle recoverable errors |
| CRITICAL | Lỗi nghiêm trọng | System failures |

### 3. Component-Specific Logging

Enable logging cho specific components:

```python
import logging

# Enable debug cho specific modules
logging.getLogger("agentic_sdlc.orchestration").setLevel(logging.DEBUG)
logging.getLogger("agentic_sdlc.intelligence").setLevel(logging.INFO)
logging.getLogger("agentic_sdlc.plugins").setLevel(logging.WARNING)
```text

**Trong config.yaml:**

```yaml
logging:
  level: INFO  # Default level
  component_levels:
    orchestration: DEBUG
    intelligence: INFO
    plugins: WARNING
    infrastructure: DEBUG
```text

---

## Log Message Interpretation

### 1. Agent Execution Logs

**Example Log:**

```
2024-02-11 10:15:23 - agentic_sdlc.orchestration.agent - INFO - Agent 'code-reviewer' starting execution
2024-02-11 10:15:23 - agentic_sdlc.orchestration.agent - DEBUG - Agent config: {'role': 'REVIEWER', 'model': 'gpt-4', 'max_iterations': 5}
2024-02-11 10:15:24 - agentic_sdlc.orchestration.model_client - DEBUG - Sending request to OpenAI API
2024-02-11 10:15:26 - agentic_sdlc.orchestration.model_client - DEBUG - Received response (tokens: 150)
2024-02-11 10:15:26 - agentic_sdlc.orchestration.agent - INFO - Agent 'code-reviewer' completed successfully
```text

**Interpretation:**
- Agent started execution at 10:15:23
- Configuration loaded successfully
- API request took ~2 seconds
- Response received with 150 tokens
- Total execution time: ~3 seconds

### 2. Workflow Execution Logs

**Example Log:**

```
2024-02-11 10:20:00 - agentic_sdlc.infrastructure.workflow_engine - INFO - Starting workflow 'ci-pipeline'
2024-02-11 10:20:00 - agentic_sdlc.infrastructure.workflow_engine - DEBUG - Workflow has 4 steps: ['build', 'test', 'deploy', 'notify']
2024-02-11 10:20:01 - agentic_sdlc.infrastructure.workflow_engine - INFO - Executing step 'build'
2024-02-11 10:20:05 - agentic_sdlc.infrastructure.workflow_engine - INFO - Step 'build' completed successfully
2024-02-11 10:20:05 - agentic_sdlc.infrastructure.workflow_engine - INFO - Executing step 'test'
2024-02-11 10:20:10 - agentic_sdlc.infrastructure.workflow_engine - ERROR - Step 'test' failed: TestFailure
2024-02-11 10:20:10 - agentic_sdlc.infrastructure.workflow_engine - WARNING - Skipping step 'deploy' due to dependency failure
2024-02-11 10:20:10 - agentic_sdlc.infrastructure.workflow_engine - INFO - Executing step 'notify'
2024-02-11 10:20:11 - agentic_sdlc.infrastructure.workflow_engine - INFO - Workflow 'ci-pipeline' completed with errors
```text

**Interpretation:**
- Workflow started with 4 steps
- Build step succeeded (4 seconds)
- Test step failed after 5 seconds
- Deploy step skipped due to test failure
- Notify step executed regardless
- Workflow completed but with errors

### 3. Error Logs

**Example Log:**

```
2024-02-11 10:25:00 - agentic_sdlc.orchestration.model_client - ERROR - API request failed: RateLimitError
2024-02-11 10:25:00 - agentic_sdlc.orchestration.model_client - DEBUG - Error details: {'error': 'rate_limit_exceeded', 'retry_after': 60}
2024-02-11 10:25:00 - agentic_sdlc.orchestration.model_client - INFO - Retrying in 60 seconds (attempt 1/3)
```text

**Interpretation:**
- API rate limit exceeded
- System will retry after 60 seconds
- This is attempt 1 of 3 max retries

### 4. Intelligence Layer Logs

**Example Log:**

```
2024-02-11 10:30:00 - agentic_sdlc.intelligence.learner - INFO - Learning from successful execution
2024-02-11 10:30:00 - agentic_sdlc.intelligence.learner - DEBUG - Task type: 'code_review', Approach: 'static_analysis'
2024-02-11 10:30:01 - agentic_sdlc.intelligence.learner - DEBUG - Updated pattern database (total patterns: 47)
2024-02-11 10:30:01 - agentic_sdlc.intelligence.reasoner - INFO - Analyzing task complexity
2024-02-11 10:30:01 - agentic_sdlc.intelligence.reasoner - DEBUG - Complexity score: 0.75 (high)
2024-02-11 10:30:01 - agentic_sdlc.intelligence.reasoner - INFO - Recommended execution mode: 'parallel'
```text

**Interpretation:**
- System learning from successful execution
- Pattern database updated with new example
- Task complexity analyzed as high (0.75)
- Parallel execution recommended

---

## Debug Techniques

### 1. Trace Agent Execution

Enable detailed tracing cho agent execution:

```python
from agentic_sdlc.orchestration.agent import create_agent
from agentic_sdlc.core.logging import enable_trace

# Enable tracing
enable_trace()

agent = create_agent(
    name="debugger",
    role="DEVELOPER",
    debug_mode=True  # Enable agent-level debugging
)

# Execute với detailed logging
result = agent.execute("Analyze code", trace=True)

# Print execution trace
print(result.trace)
```text

**Output:**

```
Execution Trace:
  Step 1: Parse task (0.1s)
  Step 2: Generate plan (1.2s)
  Step 3: Execute plan (3.5s)
    - Sub-step 3.1: Load code (0.5s)
    - Sub-step 3.2: Analyze (2.8s)
    - Sub-step 3.3: Generate report (0.2s)
  Step 4: Validate results (0.3s)
Total: 5.1s
```text

### 2. Inspect Workflow State

Debug workflow execution bằng cách inspect state:

```python
from agentic_sdlc.infrastructure.workflow_engine import WorkflowEngine

engine = WorkflowEngine(debug_mode=True)

# Execute workflow
result = engine.execute(workflow)

# Inspect state sau mỗi step
for step_name, step_result in result.step_results.items():
    print(f"\nStep: {step_name}")
    print(f"  Status: {step_result.status}")
    print(f"  Duration: {step_result.duration}s")
    print(f"  Output: {step_result.output}")
    if step_result.error:
        print(f"  Error: {step_result.error}")
```text

### 3. Monitor API Calls

Track tất cả API calls đến LLM providers:

```python
from agentic_sdlc.orchestration.model_client import create_model_client, ModelConfig
from agentic_sdlc.intelligence.monitor import Monitor

monitor = Monitor()

config = ModelConfig(
    provider="openai",
    model="gpt-4",
    monitor=monitor  # Attach monitor
)

client = create_model_client(config)

# Execute requests
response = client.generate("Analyze code")

# Check metrics
stats = monitor.get_statistics()
print(f"Total API calls: {stats['total_calls']}")
print(f"Total tokens: {stats['total_tokens']}")
print(f"Average latency: {stats['avg_latency']}s")
print(f"Error rate: {stats['error_rate']}%")
```text

### 4. Debug Plugin Issues

Troubleshoot plugin loading và execution:

```python
from agentic_sdlc.plugins.registry import PluginRegistry
import logging

# Enable plugin debug logging
logging.getLogger("agentic_sdlc.plugins").setLevel(logging.DEBUG)

registry = PluginRegistry()

# Try load plugin với error handling
try:
    plugin = registry.load_plugin("custom-analyzer")
    print(f"Plugin loaded: {plugin.name} v{plugin.version}")
    
    # Test plugin initialization
    plugin.initialize()
    print("Plugin initialized successfully")
    
    # Test plugin methods
    result = plugin.analyze("test data")
    print(f"Plugin result: {result}")
    
except Exception as e:
    print(f"Plugin error: {e}")
    import traceback
    traceback.print_exc()
```text

### 5. Memory Profiling

Profile memory usage để detect leaks:

```python
import tracemalloc
from agentic_sdlc.orchestration.agent import create_agent

# Start memory tracking
tracemalloc.start()

# Execute agent
agent = create_agent("profiler", "DEVELOPER")
result = agent.execute("Process large dataset")

# Get memory snapshot
snapshot = tracemalloc.take_snapshot()
top_stats = snapshot.statistics('lineno')

print("Top 10 memory allocations:")
for stat in top_stats[:10]:
    print(stat)

tracemalloc.stop()
```text

### 6. Performance Profiling

Profile execution time:

```python
import cProfile
import pstats
from agentic_sdlc.orchestration.workflow import WorkflowBuilder

# Create profiler
profiler = cProfile.Profile()

# Profile workflow execution
profiler.enable()

builder = WorkflowBuilder("performance-test")
builder.add_step("step1", action="action1")
builder.add_step("step2", action="action2")
workflow = builder.build()
result = workflow.execute()

profiler.disable()

# Print stats
stats = pstats.Stats(profiler)
stats.sort_stats('cumulative')
stats.print_stats(20)  # Top 20 slowest functions
```text

---

## Common Debug Scenarios

### Scenario 1: Agent Not Responding

**Symptoms:**
- Agent execution hangs
- No log output
- Timeout errors

**Debug Steps:**

```python
import logging
from agentic_sdlc.orchestration.agent import create_agent

# Enable verbose logging
logging.basicConfig(level=logging.DEBUG)

agent = create_agent(
    name="test-agent",
    role="DEVELOPER",
    timeout=30,  # Add timeout
    debug_mode=True
)

try:
    result = agent.execute("task", timeout=30)
except TimeoutError as e:
    print(f"Agent timed out: {e}")
    # Check agent state
    print(f"Agent state: {agent.get_state()}")
    print(f"Last activity: {agent.get_last_activity()}")
```text

### Scenario 2: Workflow Steps Failing

**Symptoms:**
- Steps fail without clear error
- Inconsistent failures
- Dependency issues

**Debug Steps:**

```python
from agentic_sdlc.infrastructure.workflow_engine import WorkflowEngine

engine = WorkflowEngine(debug_mode=True)

# Add error handlers
def on_step_start(step_name):
    print(f"Starting step: {step_name}")

def on_step_complete(step_name, result):
    print(f"Completed step: {step_name}, success: {result.success}")

def on_step_error(step_name, error):
    print(f"Step {step_name} failed: {error}")
    import traceback
    traceback.print_exc()

engine.on_step_start = on_step_start
engine.on_step_complete = on_step_complete
engine.on_step_error = on_step_error

# Execute với callbacks
result = engine.execute(workflow)
```text

### Scenario 3: Memory Leaks

**Symptoms:**
- Memory usage tăng liên tục
- Out of memory errors
- Slow performance over time

**Debug Steps:**

```python
import gc
import sys
from agentic_sdlc.orchestration.agent import create_agent

# Monitor memory before
import psutil
process = psutil.Process()
mem_before = process.memory_info().rss / 1024 / 1024  # MB

# Execute agent multiple times
agent = create_agent("memory-test", "DEVELOPER")
for i in range(100):
    result = agent.execute(f"Task {i}")
    
    # Force garbage collection
    gc.collect()
    
    # Check memory every 10 iterations
    if i % 10 == 0:
        mem_current = process.memory_info().rss / 1024 / 1024
        print(f"Iteration {i}: Memory = {mem_current:.2f} MB")

# Memory after
mem_after = process.memory_info().rss / 1024 / 1024
print(f"Memory increase: {mem_after - mem_before:.2f} MB")

# Find memory leaks
import objgraph
objgraph.show_most_common_types(limit=20)
```text

### Scenario 4: API Rate Limiting

**Symptoms:**
- Frequent rate limit errors
- Slow execution
- Retry loops

**Debug Steps:**

```python
from agentic_sdlc.intelligence.monitor import Monitor
from agentic_sdlc.orchestration.model_client import create_model_client

monitor = Monitor()

# Track API calls
client = create_model_client(config, monitor=monitor)

# Execute với monitoring
for i in range(10):
    try:
        result = client.generate(f"Request {i}")
        
        # Check rate limit status
        rate_info = monitor.get_rate_limit_info("openai")
        print(f"Request {i}:")
        print(f"  Remaining: {rate_info['remaining']}")
        print(f"  Reset in: {rate_info['reset_in']}s")
        
    except RateLimitError as e:
        print(f"Rate limited: {e}")
        print(f"Retry after: {e.retry_after}s")
```text

---

## Advanced Debugging

### 1. Remote Debugging

Setup remote debugging cho distributed systems:

```python
import debugpy

# Enable remote debugging
debugpy.listen(("0.0.0.0", 5678))
print("Waiting for debugger attach...")
debugpy.wait_for_client()

# Your code here
from agentic_sdlc.orchestration.agent import create_agent
agent = create_agent("remote-debug", "DEVELOPER")
result = agent.execute("task")
```text

### 2. Log Aggregation

Aggregate logs từ multiple components:

```python
from agentic_sdlc.core.logging import LogAggregator

aggregator = LogAggregator()

# Collect logs từ multiple sources
aggregator.add_source("agent-1", "./logs/agent1.log")
aggregator.add_source("agent-2", "./logs/agent2.log")
aggregator.add_source("workflow", "./logs/workflow.log")

# Query logs
errors = aggregator.query(level="ERROR", time_range="last_hour")
for error in errors:
    print(f"{error.timestamp} - {error.source} - {error.message}")
```text

### 3. Distributed Tracing

Trace requests across distributed agents:

```python
from agentic_sdlc.intelligence.collaborator import TeamCoordinator
from agentic_sdlc.core.tracing import enable_distributed_tracing

# Enable tracing
enable_distributed_tracing()

coordinator = TeamCoordinator()

# Trace message flow
trace_id = coordinator.send_message(
    from_agent="agent-1",
    to_agent="agent-2",
    message="Process data",
    trace=True
)

# View trace
trace = coordinator.get_trace(trace_id)
print(f"Trace {trace_id}:")
for span in trace.spans:
    print(f"  {span.name}: {span.duration}ms")
```text

---

## Best Practices

### 1. Structured Logging

Sử dụng structured logging cho easier parsing:

```python
import logging
import json

class StructuredLogger:
    def __init__(self, name):
        self.logger = logging.getLogger(name)
    
    def log(self, level, message, **kwargs):
        log_data = {
            "message": message,
            "timestamp": datetime.now().isoformat(),
            **kwargs
        }
        self.logger.log(level, json.dumps(log_data))

# Usage
logger = StructuredLogger("agentic_sdlc.custom")
logger.log(logging.INFO, "Agent executed", 
           agent_name="reviewer", 
           duration=3.5, 
           success=True)
```text

### 2. Context Managers cho Debugging

```python
from contextlib import contextmanager
import time

@contextmanager
def debug_context(name):
    print(f"[DEBUG] Entering {name}")
    start = time.time()
    try:
        yield
    finally:
        duration = time.time() - start
        print(f"[DEBUG] Exiting {name} (took {duration:.2f}s)")

# Usage
with debug_context("agent_execution"):
    agent = create_agent("test", "DEVELOPER")
    result = agent.execute("task")
```text

### 3. Conditional Debugging

```python
import os

DEBUG = os.getenv("DEBUG", "false").lower() == "true"

def debug_print(*args, **kwargs):
    if DEBUG:
        print("[DEBUG]", *args, **kwargs)

# Usage
debug_print("Agent state:", agent.get_state())
debug_print("Workflow steps:", workflow.steps)
```

---

## Tổng Kết

Debug hiệu quả trong Agentic SDLC yêu cầu:
- Proper logging configuration
- Understanding log message patterns
- Using appropriate debug techniques
- Monitoring system metrics
- Profiling performance và memory

Để biết thêm chi tiết, xem:
- [Common Errors](common-errors.md)
- [FAQ](faq.md)
- [Performance Guide](../guides/advanced/performance.md)
