# Migration từ v2.x sang v3.0.0

**Phiên bản**: 3.0.0  
**Cập nhật lần cuối**: 11/02/2026


## Tổng Quan

Tài liệu này hướng dẫn chi tiết việc nâng cấp từ Agentic SDLC v2.x lên v3.0.0. Phiên bản v3.0.0 mang đến nhiều cải tiến về kiến trúc, hiệu năng và tính năng mới, nhưng cũng có một số breaking changes cần lưu ý.

## Breaking Changes

### 1. Thay Đổi Cấu Trúc Package

**v2.x:**
```python
from agentic_sdlc import Agent, Workflow
from agentic_sdlc.core import Config
from agentic_sdlc.utils import Logger
```text

**v3.0.0:**
```python
from agentic_sdlc.orchestration import Agent, Workflow
from agentic_sdlc.core.config import Config
from agentic_sdlc.core.logging import Logger
```text

### 2. Agent Creation API

**v2.x:**
```python
agent = Agent(
    name="developer",
    role="DEV",
    model="gpt-4"
)
```text

**v3.0.0:**
```python
from agentic_sdlc.orchestration.agent import create_agent

agent = create_agent(
    agent_id="developer",
    agent_type="DEV",
    model_name="gpt-4",
    system_prompt="You are a developer agent"
)
```text

**Thay đổi:**
- `name` → `agent_id`
- `role` → `agent_type`
- `model` → `model_name`
- Thêm tham số bắt buộc `system_prompt`

### 3. Workflow Builder API

**v2.x:**
```python
workflow = Workflow("my-workflow")
workflow.add_step("step1", agent1, "task description")
workflow.add_step("step2", agent2, "task description", depends_on=["step1"])
```text

**v3.0.0:**
```python
from agentic_sdlc.orchestration.workflow import WorkflowBuilder, WorkflowStep

builder = WorkflowBuilder("my-workflow")
builder.add_step(WorkflowStep(
    name="step1",
    action="execute_task",
    parameters={"agent": agent1, "task": "task description"}
))
builder.add_step(WorkflowStep(
    name="step2",
    action="execute_task",
    parameters={"agent": agent2, "task": "task description"},
    dependencies=["step1"]
))
workflow = builder.build()
```text

**Thay đổi:**
- Sử dụng `WorkflowBuilder` thay vì khởi tạo trực tiếp
- Steps được định nghĩa bằng `WorkflowStep` dataclass
- `depends_on` → `dependencies`
- Cần gọi `build()` để tạo workflow

### 4. Configuration Structure

**v2.x (config.yaml):**
```yaml
model:
  provider: openai
  name: gpt-4
  api_key: ${OPENAI_API_KEY}

logging:
  level: INFO
```text

**v3.0.0 (config.yaml):**
```yaml
models:
  default:
    provider: openai
    model_name: gpt-4
    api_key: ${OPENAI_API_KEY}
    temperature: 0.7
    max_tokens: 2000

logging:
  level: INFO
  format: "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
  handlers:
    - type: console
    - type: file
      filename: agentic_sdlc.log
```text

**Thay đổi:**
- `model` → `models` (hỗ trợ multiple models)
- `name` → `model_name`
- Thêm cấu hình chi tiết cho logging handlers

### 5. Model Client API

**v2.x:**
```python
from agentic_sdlc import ModelClient

client = ModelClient(provider="openai", model="gpt-4")
response = client.generate(prompt="Hello")
```text

**v3.0.0:**
```python
from agentic_sdlc.orchestration.model_client import create_model_client, ModelConfig

config = ModelConfig(
    provider="openai",
    model_name="gpt-4",
    api_key="your-api-key"
)
client = create_model_client(config)
response = client.generate(messages=[{"role": "user", "content": "Hello"}])
```text

**Thay đổi:**
- Sử dụng `ModelConfig` để cấu hình
- `generate()` nhận `messages` thay vì `prompt`
- Messages theo format chat completion API

### 6. Plugin System

**v2.x:**
```python
class MyPlugin:
    def execute(self, context):
        pass

registry.register(MyPlugin())
```text

**v3.0.0:**
```python
from agentic_sdlc.plugins.base import Plugin

class MyPlugin(Plugin):
    @property
    def name(self) -> str:
        return "my-plugin"
    
    @property
    def version(self) -> str:
        return "1.0.0"
    
    def initialize(self) -> None:
        pass
    
    def shutdown(self) -> None:
        pass
    
    def execute(self, context):
        pass

from agentic_sdlc.plugins.registry import PluginRegistry
registry = PluginRegistry()
registry.register(MyPlugin())
```text

**Thay đổi:**
- Plugin phải kế thừa từ `Plugin` base class
- Bắt buộc implement `name`, `version`, `initialize`, `shutdown`

## Deprecated Features

### 1. Legacy Agent Types

**Deprecated trong v2.x, removed trong v3.0.0:**
- `GENERIC` agent type → Sử dụng `DEV` hoặc agent type cụ thể
- `HELPER` agent type → Sử dụng `ASSISTANT`

### 2. Synchronous Execution Mode

**Deprecated:**
```python
workflow.run_sync()  # Không còn được hỗ trợ
```text

**Thay thế:**
```python
import asyncio
asyncio.run(workflow.run())
```text

### 3. Global Configuration

**Deprecated:**
```python
from agentic_sdlc import set_global_config
set_global_config(config)  # Không còn được hỗ trợ
```text

**Thay thế:**
```python
from agentic_sdlc.core.config import ConfigManager
config_manager = ConfigManager()
config_manager.load_config("config.yaml")
```text

### 4. Direct Database Access

**Deprecated:**
```python
from agentic_sdlc.storage import Database
db = Database.get_instance()  # Không còn được hỗ trợ
```text

**Thay thế:**
Sử dụng Intelligence Layer APIs:
```python
from agentic_sdlc.intelligence.learner import Learner
learner = Learner()
learner.learn_success(task_id, result)
```text

## New Features trong v3.0.0

### 1. Intelligence Layer

Tính năng hoàn toàn mới cung cấp khả năng học tập và suy luận:

```python
from agentic_sdlc.intelligence import Learner, Monitor, Reasoner, TeamCoordinator

# Learning từ execution history
learner = Learner()
learner.learn_success(task_id="task-1", result={"output": "success"})

# Monitoring và metrics
monitor = Monitor()
monitor.record_metric("execution_time", 1.5)

# Reasoning và decision making
reasoner = Reasoner()
complexity = reasoner.analyze_task_complexity(task_description)

# Team collaboration
coordinator = TeamCoordinator()
coordinator.register_agent(agent_id="dev-1", capabilities=["coding"])
```text

### 2. Enhanced Workflow Engine

Workflow engine mới với nhiều tính năng nâng cao:

```python
from agentic_sdlc.infrastructure.workflow_engine import WorkflowEngine

engine = WorkflowEngine()

# Conditional execution
builder.add_step(WorkflowStep(
    name="conditional-step",
    action="execute_task",
    parameters={"task": "deploy"},
    condition=lambda ctx: ctx.get("tests_passed") == True
))

# Retry logic
builder.add_step(WorkflowStep(
    name="retry-step",
    action="execute_task",
    parameters={"task": "api_call"},
    retry_policy={"max_attempts": 3, "backoff": "exponential"}
))

# Parallel execution
builder.add_parallel_steps([step1, step2, step3])
```text

### 3. Multi-Model Support

Hỗ trợ sử dụng nhiều models trong cùng một workflow:

```python
from agentic_sdlc.orchestration.model_client import ModelRegistry

registry = ModelRegistry()

# Register multiple models
registry.register_model_client("gpt-4", gpt4_client)
registry.register_model_client("claude-3", claude_client)
registry.register_model_client("ollama", ollama_client)

# Agents có thể sử dụng models khác nhau
dev_agent = create_agent(agent_id="dev", agent_type="DEV", model_name="gpt-4")
reviewer_agent = create_agent(agent_id="reviewer", agent_type="REVIEWER", model_name="claude-3")
```text

### 4. Enhanced CLI

CLI mới với nhiều commands và options:

```bash
# Initialize project với template
agentic init --template=microservice

# Run workflow với parameters
agentic run workflow.yaml --param env=production

# Agent management
agentic agent list
agentic agent create --type=DEV --name=developer-1
agentic agent status developer-1

# Configuration management
agentic config get models.default.provider
agentic config set models.default.temperature 0.8
```text

### 5. Plugin Lifecycle Management

Plugin system mới với lifecycle hooks:

```python
class MyPlugin(Plugin):
    def initialize(self) -> None:
        """Called when plugin is loaded"""
        self.setup_resources()
    
    def shutdown(self) -> None:
        """Called when plugin is unloaded"""
        self.cleanup_resources()
    
    def on_workflow_start(self, workflow_id: str) -> None:
        """Called when workflow starts"""
        pass
    
    def on_workflow_complete(self, workflow_id: str, result: Any) -> None:
        """Called when workflow completes"""
        pass
```text

## Performance Improvements

### 1. Async-First Architecture

v3.0.0 được thiết kế với async/await từ đầu:

- Tất cả I/O operations đều async
- Parallel execution mặc định cho independent steps
- Giảm latency lên đến 60% so với v2.x

### 2. Caching Layer

Built-in caching cho LLM responses:

```python
from agentic_sdlc.core.cache import CacheManager

cache = CacheManager()
cache.enable_llm_cache(ttl=3600)  # Cache responses for 1 hour
```

### 3. Connection Pooling

Tự động quản lý connection pools cho external services:

- Database connections
- HTTP connections
- LLM API connections

## Migration Checklist

Xem [upgrade-guide.md](./upgrade-guide.md) để có checklist chi tiết và migration scripts.

## Hỗ Trợ

Nếu gặp vấn đề trong quá trình migration:

1. Kiểm tra [Troubleshooting Guide](../troubleshooting/common-errors.md)
2. Xem [FAQ](../troubleshooting/faq.md)
3. Tạo issue trên GitHub repository
4. Liên hệ support team

## Tài Liệu Liên Quan

- [Upgrade Guide](./upgrade-guide.md) - Hướng dẫn nâng cấp chi tiết
- [Configuration Guide](../getting-started/configuration.md) - Cấu hình v3.0.0
- [API Reference](../api-reference/README.md) - API documentation đầy đủ
- [Examples](../examples/README.md) - Code examples cho v3.0.0
