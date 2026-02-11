# Lỗi Phổ Biến và Cách Khắc Phục

**Phiên bản**: 3.0.0  
**Cập nhật lần cuối**: 11/02/2026


## Giới Thiệu

Tài liệu này liệt kê các lỗi phổ biến khi sử dụng Agentic SDLC v3.0.0 và cách khắc phục chúng. Mỗi lỗi bao gồm mô tả, nguyên nhân, và giải pháp chi tiết.

---

## 1. ConfigurationError: Missing API Key

### Mô Tả Lỗi

```text
ConfigurationError: Missing required configuration: 'openai_api_key'
```

### Nguyên Nhân

API key cho LLM provider (OpenAI, Anthropic, etc.) chưa được cấu hình trong file config hoặc environment variables.

### Giải Pháp

**Cách 1: Sử dụng Environment Variables**

```bash
export OPENAI_API_KEY="your-api-key-here"
export ANTHROPIC_API_KEY="your-api-key-here"
```text

**Cách 2: Cấu hình trong config.yaml**

```yaml
model_clients:
  openai:
    api_key: "your-api-key-here"
    model: "gpt-4"
```text

**Cách 3: Cấu hình Programmatically**

```python
from agentic_sdlc.core.config import ConfigurationManager

config = ConfigurationManager()
config.set("model_clients.openai.api_key", "your-api-key-here")
config.save()
```text

### Graceful Degradation

Nếu API key không có sẵn, hệ thống sẽ:
- Hiển thị warning message rõ ràng
- Fallback sang local LLM (Ollama) nếu được cấu hình
- Cho phép tiếp tục với mock mode cho testing

---

## 2. ValidationError: Invalid Workflow Definition

### Mô Tả Lỗi

```
ValidationError: Workflow step 'deploy' has unresolved dependency 'test'
```text

### Nguyên Nhân

Workflow definition có circular dependencies hoặc references đến steps không tồn tại.

### Giải Pháp

**Kiểm tra workflow dependencies:**

```python
from agentic_sdlc.orchestration.workflow import WorkflowBuilder

builder = WorkflowBuilder("my-workflow")

# Đảm bảo dependencies tồn tại trước khi reference
builder.add_step("build", action="build_code")
builder.add_step("test", action="run_tests", dependencies=["build"])
builder.add_step("deploy", action="deploy_app", dependencies=["test"])

# Validate trước khi execute
workflow = builder.build()
validation_result = workflow.validate()
if not validation_result.is_valid:
    print(f"Validation errors: {validation_result.errors}")
```text

### Fallback Mechanism

Hệ thống sẽ:
- Tự động detect circular dependencies
- Suggest correct dependency order
- Cho phép skip optional steps nếu dependencies fail

---

## 3. PluginError: Plugin Initialization Failed

### Mô Tả Lỗi

```
PluginError: Failed to initialize plugin 'custom-analyzer': ModuleNotFoundError
```text

### Nguyên Nhân

Plugin dependencies chưa được cài đặt hoặc plugin code có lỗi syntax.

### Giải Pháp

**Bước 1: Kiểm tra plugin dependencies**

```bash
# Xem plugin requirements
cat plugins/custom-analyzer/requirements.txt

# Cài đặt dependencies
pip install -r plugins/custom-analyzer/requirements.txt
```text

**Bước 2: Validate plugin code**

```python
from agentic_sdlc.plugins.registry import PluginRegistry

registry = PluginRegistry()

# Test load plugin
try:
    plugin = registry.load_plugin("custom-analyzer")
    print(f"Plugin loaded successfully: {plugin.name}")
except Exception as e:
    print(f"Plugin load failed: {e}")
```text

**Bước 3: Check plugin structure**

```python
# Plugin phải implement required methods
class CustomAnalyzer(Plugin):
    @property
    def name(self) -> str:
        return "custom-analyzer"
    
    @property
    def version(self) -> str:
        return "1.0.0"
    
    def initialize(self) -> None:
        # Initialization logic
        pass
    
    def shutdown(self) -> None:
        # Cleanup logic
        pass
```text

### Graceful Degradation

Nếu plugin fail:
- Hệ thống log warning nhưng tiếp tục
- Disable plugin và sử dụng default behavior
- Cho phép retry plugin initialization sau

---

## 4. AgentExecutionError: Agent Timeout

### Mô Tả Lỗi

```
AgentExecutionError: Agent 'code-reviewer' exceeded maximum execution time (300s)
```text

### Nguyên Nhân

Agent task quá phức tạp hoặc LLM response chậm, vượt quá timeout threshold.

### Giải Pháp

**Cách 1: Tăng timeout**

```python
from agentic_sdlc.orchestration.agent import create_agent

agent = create_agent(
    name="code-reviewer",
    role="REVIEWER",
    max_execution_time=600,  # Tăng lên 10 phút
)
```text

**Cách 2: Break down task thành smaller chunks**

```python
# Thay vì review toàn bộ codebase
agent.execute("Review all code")

# Chia nhỏ task
for file in code_files:
    agent.execute(f"Review {file}")
```text

**Cách 3: Sử dụng async execution**

```python
import asyncio
from agentic_sdlc.orchestration.agent import create_agent

async def review_code_async():
    agent = create_agent("reviewer", "REVIEWER")
    result = await agent.execute_async("Review code")
    return result

result = asyncio.run(review_code_async())
```text

### Fallback Mechanism

Khi timeout xảy ra:
- Hệ thống save partial results
- Cho phép resume từ checkpoint
- Suggest task decomposition

---

## 5. ModelClientError: Rate Limit Exceeded

### Mô Tả Lỗi

```
ModelClientError: OpenAI API rate limit exceeded. Retry after 60 seconds.
```text

### Nguyên Nhân

Quá nhiều requests đến LLM API trong thời gian ngắn, vượt quá rate limit.

### Giải Pháp

**Cách 1: Implement exponential backoff**

```python
from agentic_sdlc.orchestration.model_client import create_model_client, ModelConfig

config = ModelConfig(
    provider="openai",
    model="gpt-4",
    max_retries=3,
    retry_delay=2,  # seconds
    exponential_backoff=True
)

client = create_model_client(config)
```text

**Cách 2: Sử dụng request batching**

```python
from agentic_sdlc.intelligence.monitor import Monitor

monitor = Monitor()

# Batch multiple requests
requests = [
    "Analyze function A",
    "Analyze function B",
    "Analyze function C"
]

# Execute with rate limiting
for req in requests:
    if monitor.check_rate_limit("openai"):
        result = client.generate(req)
    else:
        # Wait before retry
        time.sleep(monitor.get_retry_delay("openai"))
```text

**Cách 3: Fallback sang alternative model**

```python
from agentic_sdlc.orchestration.model_client import ModelClientRegistry

registry = ModelClientRegistry()

# Register multiple providers
registry.register("openai", openai_client)
registry.register("anthropic", anthropic_client)
registry.register("ollama", ollama_client)

# Auto fallback khi rate limit
try:
    result = registry.get("openai").generate(prompt)
except RateLimitError:
    result = registry.get("anthropic").generate(prompt)
```text

### Graceful Degradation

Hệ thống tự động:
- Queue requests khi hit rate limit
- Fallback sang cheaper/faster models
- Cache responses để reduce API calls

---

## 6. WorkflowExecutionError: Step Failed

### Mô Tả Lỗi

```
WorkflowExecutionError: Step 'test' failed with error: TestFailure
```text

### Nguyên Nhân

Một step trong workflow failed, causing toàn bộ workflow dừng lại.

### Giải Pháp

**Cách 1: Implement error handling trong workflow**

```python
from agentic_sdlc.orchestration.workflow import WorkflowBuilder

builder = WorkflowBuilder("ci-pipeline")

builder.add_step(
    "test",
    action="run_tests",
    on_error="continue",  # Continue thay vì stop
    max_retries=3
)

builder.add_step(
    "deploy",
    action="deploy_app",
    dependencies=["test"],
    skip_if_dependency_failed=False  # Deploy ngay cả khi test fail
)
```text

**Cách 2: Sử dụng conditional execution**

```python
builder.add_step(
    "deploy-staging",
    action="deploy",
    condition=lambda ctx: ctx.get_step_result("test").success
)

builder.add_step(
    "notify-failure",
    action="send_notification",
    condition=lambda ctx: not ctx.get_step_result("test").success
)
```text

**Cách 3: Implement retry logic**

```python
from agentic_sdlc.infrastructure.workflow_engine import WorkflowEngine

engine = WorkflowEngine()

result = engine.execute(
    workflow,
    retry_failed_steps=True,
    max_step_retries=3,
    retry_delay=5
)
```text

### Fallback Mechanism

Workflow engine sẽ:
- Save workflow state trước khi fail
- Cho phép resume từ failed step
- Execute cleanup steps ngay cả khi fail

---

## 7. LearnerError: Insufficient Training Data

### Mô Tả Lỗi

```
LearnerError: Cannot learn from success: insufficient historical data (minimum 5 required)
```text

### Nguyên Nhân

Intelligence layer cần minimum số lượng examples để learn patterns.

### Giải Pháp

**Cách 1: Seed với initial data**

```python
from agentic_sdlc.intelligence.learner import Learner

learner = Learner()

# Seed với example data
initial_examples = [
    {"task": "code_review", "approach": "static_analysis", "success": True},
    {"task": "code_review", "approach": "manual_review", "success": True},
    {"task": "testing", "approach": "unit_tests", "success": True},
    {"task": "testing", "approach": "integration_tests", "success": True},
    {"task": "deployment", "approach": "blue_green", "success": True},
]

for example in initial_examples:
    learner.learn_success(
        task_type=example["task"],
        approach=example["approach"],
        context={}
    )
```text

**Cách 2: Disable learning cho cold start**

```python
from agentic_sdlc.intelligence.reasoner import Reasoner

reasoner = Reasoner()

# Sử dụng rule-based reasoning thay vì learning
result = reasoner.recommend_execution_mode(
    task_complexity="high",
    use_learning=False  # Disable learning-based recommendations
)
```text

### Graceful Degradation

Khi insufficient data:
- Fallback sang rule-based decision making
- Use default strategies
- Continue collecting data for future learning

---

## 8. MonitorError: Metrics Collection Failed

### Mô Tả Lỗi

```
MonitorError: Failed to record metric 'execution_time': Storage backend unavailable
```text

### Nguyên Nhân

Metrics storage backend (database, file system) không available hoặc full.

### Giải Pháp

**Cách 1: Configure fallback storage**

```python
from agentic_sdlc.intelligence.monitor import Monitor, MetricsConfig

config = MetricsConfig(
    primary_backend="database",
    fallback_backend="file",
    file_path="./metrics/fallback.json"
)

monitor = Monitor(config)
```text

**Cách 2: Implement in-memory buffer**

```python
monitor = Monitor()

# Metrics được buffer trong memory
monitor.record_metric("execution_time", 1.5, buffer=True)

# Flush khi backend available
try:
    monitor.flush_buffer()
except Exception as e:
    print(f"Failed to flush metrics: {e}")
```text

**Cách 3: Disable metrics collection**

```python
# Trong config.yaml
monitoring:
  enabled: false  # Disable nếu không critical
  fail_silently: true  # Không throw error nếu fail
```text

### Graceful Degradation

Monitor sẽ:
- Buffer metrics trong memory
- Log warning nhưng không block execution
- Retry flush periodically

---

## 9. CollaborationError: Agent Communication Failed

### Mô Tả Lỗi

```
CollaborationError: Failed to send message from 'dev-agent' to 'test-agent': Connection timeout
```text

### Nguyên Nhân

Network issues hoặc target agent không available.

### Giải Pháp

**Cách 1: Implement message queue**

```python
from agentic_sdlc.intelligence.collaborator import TeamCoordinator

coordinator = TeamCoordinator()

# Sử dụng async messaging với queue
coordinator.send_message(
    from_agent="dev-agent",
    to_agent="test-agent",
    message="Code ready for testing",
    async_mode=True,  # Queue message nếu agent unavailable
    timeout=30
)
```text

**Cách 2: Implement retry logic**

```python
from agentic_sdlc.intelligence.collaborator import MessageConfig

config = MessageConfig(
    max_retries=3,
    retry_delay=5,
    exponential_backoff=True
)

coordinator = TeamCoordinator(message_config=config)
```text

**Cách 3: Fallback sang alternative communication**

```python
try:
    coordinator.send_message("dev-agent", "test-agent", "message")
except CollaborationError:
    # Fallback sang shared state
    coordinator.set_shared_state("pending_tests", ["test1", "test2"])
```text

### Fallback Mechanism

Collaboration layer sẽ:
- Queue messages cho offline agents
- Use shared state thay vì direct messaging
- Notify sender về delivery status

---

## 10. ResourceError: Memory Limit Exceeded

### Mô Tả Lỗi

```
ResourceError: Agent execution exceeded memory limit (2GB)
```text

### Nguyên Nhân

Agent processing quá nhiều data hoặc có memory leak.

### Giải Pháp

**Cách 1: Configure resource limits**

```python
from agentic_sdlc.orchestration.agent import create_agent, ResourceLimits

limits = ResourceLimits(
    max_memory_mb=4096,  # Tăng limit
    max_cpu_percent=80,
    max_execution_time=600
)

agent = create_agent(
    name="data-processor",
    role="DEVELOPER",
    resource_limits=limits
)
```text

**Cách 2: Process data trong chunks**

```python
# Thay vì load toàn bộ data
data = load_all_data()  # Memory intensive

# Process từng chunk
for chunk in load_data_chunks(chunk_size=1000):
    agent.process(chunk)
    # Memory được free sau mỗi chunk
```text

**Cách 3: Enable streaming mode**

```python
agent = create_agent(
    name="analyzer",
    role="DEVELOPER",
    streaming_mode=True  # Process data as stream
)

# Stream results thay vì accumulate
for result in agent.execute_stream("Analyze large dataset"):
    handle_result(result)
```text

### Graceful Degradation

Khi memory limit exceeded:
- Hệ thống checkpoint progress
- Clear caches và temporary data
- Suggest chunking strategy
- Fallback sang disk-based processing

---

## 11. ImportError: Module Not Found

### Mô Tả Lỗi

```
ImportError: No module named 'agentic_sdlc.orchestration'
```text

### Nguyên Nhân

Package chưa được cài đặt đúng hoặc Python path không correct.

### Giải Pháp

**Cách 1: Reinstall package**

```bash
pip uninstall agentic-sdlc
pip install agentic-sdlc[all]
```text

**Cách 2: Verify installation**

```python
import sys
print(sys.path)

# Check if package installed
import pkg_resources
version = pkg_resources.get_distribution("agentic-sdlc").version
print(f"Installed version: {version}")
```text

**Cách 3: Use virtual environment**

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install agentic-sdlc[all]
```text

---

## 12. SerializationError: Cannot Serialize Workflow State

### Mô Tả Lỗi

```
SerializationError: Cannot serialize workflow state: Object of type 'function' is not JSON serializable
```javascript

### Nguyên Nhân

Workflow state chứa non-serializable objects (functions, lambdas, etc.).

### Giải Pháp

**Cách 1: Use serializable data types**

```python
# Tránh
builder.add_step(
    "process",
    action=lambda x: x * 2  # Lambda không serializable
)

# Sử dụng
def process_data(x):
    return x * 2

builder.add_step(
    "process",
    action="process_data",  # String reference
    action_func=process_data
)
```text

**Cách 2: Implement custom serialization**

```python
from agentic_sdlc.orchestration.workflow import WorkflowSerializer

serializer = WorkflowSerializer()

# Custom serialization cho complex objects
workflow_dict = serializer.serialize(
    workflow,
    include_functions=False,
    serialize_results=True
)
```

---

## Tổng Kết

Tài liệu này cover 12 lỗi phổ biến nhất khi sử dụng Agentic SDLC. Mỗi lỗi đều có:
- Mô tả rõ ràng
- Nguyên nhân root cause
- Multiple solutions
- Graceful degradation strategies
- Fallback mechanisms

Để biết thêm chi tiết về debugging và troubleshooting, xem:
- [Debugging Guide](debugging.md)
- [FAQ](faq.md)
- [Best Practices](../guides/advanced/performance.md)
