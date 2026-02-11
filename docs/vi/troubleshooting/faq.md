# Câu Hỏi Thường Gặp (FAQ)

**Phiên bản**: 3.0.0  
**Cập nhật lần cuối**: 11/02/2026


## Giới Thiệu

Tài liệu này tổng hợp các câu hỏi thường gặp về Agentic SDLC v3.0.0, bao gồm installation, configuration, usage, và troubleshooting.

---

## Cài Đặt và Thiết Lập

### Q1: Làm thế nào để cài đặt Agentic SDLC?

**A:** Có nhiều cách cài đặt tùy theo nhu cầu:

```bash
# Cài đặt core package
pip install agentic-sdlc

# Cài đặt với CLI tools
pip install agentic-sdlc[cli]

# Cài đặt full với tất cả dependencies
pip install agentic-sdlc[all]

# Cài đặt cho development
pip install agentic-sdlc[dev]
```text

Xem chi tiết tại [Installation Guide](../getting-started/installation.md).

### Q2: Python version nào được support?

**A:** Agentic SDLC v3.0.0 requires Python 3.8 trở lên. Recommended Python 3.10+ cho best performance.

```bash
# Check Python version
python --version

# Nếu cần upgrade
# macOS/Linux
brew install python@3.10

# Windows
# Download từ python.org
```text

### Q3: Làm thế nào để verify installation thành công?

**A:** Chạy các commands sau:

```bash
# Check package installed
pip show agentic-sdlc

# Test import
python -c "from agentic_sdlc import __version__; print(__version__)"

# Check CLI (nếu installed)
agentic --version
```text

### Q4: Có cần API key không?

**A:** Có, bạn cần API key cho ít nhất một LLM provider:

- **OpenAI**: Đăng ký tại https://platform.openai.com/
- **Anthropic**: Đăng ký tại https://console.anthropic.com/
- **Ollama**: Không cần API key, chạy local

```bash
# Set API key
export OPENAI_API_KEY="your-key-here"
export ANTHROPIC_API_KEY="your-key-here"
```text

---

## Cấu Hình

### Q5: File config.yaml nên đặt ở đâu?

**A:** Agentic SDLC tìm config file theo thứ tự:

1. `./config.yaml` (current directory)
2. `~/.agentic_sdlc/config.yaml` (user home)
3. `/etc/agentic_sdlc/config.yaml` (system-wide)

```bash
# Tạo config directory
mkdir -p ~/.agentic_sdlc

# Copy template
cp config.yaml.template ~/.agentic_sdlc/config.yaml

# Edit config
nano ~/.agentic_sdlc/config.yaml
```text

### Q6: Làm thế nào để switch giữa các LLM providers?

**A:** Configure multiple providers và switch programmatically:

```python
from agentic_sdlc.orchestration.model_client import create_model_client, ModelConfig

# OpenAI
openai_config = ModelConfig(provider="openai", model="gpt-4")
openai_client = create_model_client(openai_config)

# Anthropic
anthropic_config = ModelConfig(provider="anthropic", model="claude-3-opus")
anthropic_client = create_model_client(anthropic_config)

# Sử dụng client tùy theo nhu cầu
response = openai_client.generate("prompt")
```text

### Q7: Có thể sử dụng local LLM không?

**A:** Có, sử dụng Ollama:

```bash
# Install Ollama
curl -fsSL https://ollama.ai/install.sh | sh

# Pull model
ollama pull llama2

# Configure trong code
from agentic_sdlc.orchestration.model_client import create_model_client, ModelConfig

config = ModelConfig(
    provider="ollama",
    model="llama2",
    base_url="http://localhost:11434"
)
client = create_model_client(config)
```text

### Q8: Làm thế nào để configure logging?

**A:** Configure trong config.yaml hoặc programmatically:

```yaml
# config.yaml
logging:
  level: INFO
  format: "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
  output:
    console: true
    file: "./logs/agentic_sdlc.log"
```text

```python
# Programmatic
from agentic_sdlc.core.logging import setup_logging
import logging

setup_logging(
    level=logging.INFO,
    log_file="./logs/app.log",
    console_output=True
)
```javascript

---

## Agents

### Q9: Có bao nhiêu loại agents?

**A:** Agentic SDLC có 18 loại agents chuyên biệt:

- PM (Product Manager)
- SA (System Architect)
- DEV (Developer)
- TESTER (QA Tester)
- REVIEWER (Code Reviewer)
- DEVOPS (DevOps Engineer)
- SECURITY (Security Analyst)
- DATA (Data Scientist)
- ML (ML Engineer)
- FRONTEND (Frontend Developer)
- BACKEND (Backend Developer)
- MOBILE (Mobile Developer)
- DESIGNER (UI/UX Designer)
- WRITER (Technical Writer)
- ANALYST (Business Analyst)
- RESEARCHER (Research Scientist)
- COORDINATOR (Team Coordinator)
- CUSTOM (Custom Agent)

Xem chi tiết tại [Agent Types](../guides/agents/agent-types.md).

### Q10: Làm thế nào để tạo custom agent?

**A:** Sử dụng `create_agent` function:

```python
from agentic_sdlc.orchestration.agent import create_agent

agent = create_agent(
    name="my-custom-agent",
    role="CUSTOM",
    system_prompt="You are a specialized agent for...",
    model_name="gpt-4",
    tools=["code_analyzer", "file_reader"],
    max_iterations=10
)

result = agent.execute("Perform custom task")
```text

### Q11: Agents có thể communicate với nhau không?

**A:** Có, sử dụng TeamCoordinator:

```python
from agentic_sdlc.intelligence.collaborator import TeamCoordinator

coordinator = TeamCoordinator()

# Register agents
coordinator.register_agent("dev-agent", dev_agent)
coordinator.register_agent("test-agent", test_agent)

# Send message
coordinator.send_message(
    from_agent="dev-agent",
    to_agent="test-agent",
    message="Code ready for testing"
)

# Receive message
messages = coordinator.get_messages("test-agent")
```text

### Q12: Làm thế nào để limit agent execution time?

**A:** Set timeout parameters:

```python
agent = create_agent(
    name="time-limited",
    role="DEVELOPER",
    max_execution_time=300,  # 5 minutes
    timeout_action="abort"  # hoặc "save_partial"
)

try:
    result = agent.execute("Long task", timeout=300)
except TimeoutError:
    print("Agent execution timed out")
```text

---

## Workflows

### Q13: Workflow khác gì với Agent?

**A:** 
- **Agent**: Thực hiện một task cụ thể
- **Workflow**: Orchestrate nhiều tasks/agents theo sequence hoặc parallel

```python
# Agent - single task
agent = create_agent("reviewer", "REVIEWER")
result = agent.execute("Review code")

# Workflow - multiple tasks
from agentic_sdlc.orchestration.workflow import WorkflowBuilder

builder = WorkflowBuilder("ci-pipeline")
builder.add_step("build", action="build_code")
builder.add_step("test", action="run_tests", dependencies=["build"])
builder.add_step("deploy", action="deploy_app", dependencies=["test"])
workflow = builder.build()
result = workflow.execute()
```text

### Q14: Có thể run workflow steps parallel không?

**A:** Có, không specify dependencies:

```python
builder = WorkflowBuilder("parallel-workflow")

# Các steps này sẽ run parallel
builder.add_step("task1", action="action1")
builder.add_step("task2", action="action2")
builder.add_step("task3", action="action3")

# Step này chờ tất cả parallel steps complete
builder.add_step("final", action="finalize", 
                 dependencies=["task1", "task2", "task3"])
```text

### Q15: Làm thế nào để handle workflow errors?

**A:** Configure error handling strategies:

```python
builder.add_step(
    "risky-step",
    action="risky_action",
    on_error="continue",  # continue, abort, retry
    max_retries=3,
    retry_delay=5
)

# Hoặc sử dụng try-catch trong workflow
result = workflow.execute()
if not result.success:
    print(f"Workflow failed: {result.error}")
    print(f"Failed step: {result.failed_step}")
```text

### Q16: Có thể save và resume workflow không?

**A:** Có, sử dụng workflow checkpointing:

```python
from agentic_sdlc.infrastructure.workflow_engine import WorkflowEngine

engine = WorkflowEngine(checkpoint_enabled=True)

# Execute với checkpointing
result = engine.execute(workflow, checkpoint_dir="./checkpoints")

# Resume từ checkpoint
if result.status == "failed":
    result = engine.resume(
        checkpoint_file="./checkpoints/workflow_123.json",
        from_step="failed_step"
    )
```text

---

## Intelligence Features

### Q17: Intelligence layer là gì?

**A:** Intelligence layer cung cấp khả năng học tập, monitoring, reasoning, và collaboration:

- **Learner**: Học từ successes và failures
- **Monitor**: Track metrics và health
- **Reasoner**: Analyze complexity và recommend strategies
- **Collaborator**: Coordinate multi-agent collaboration

Xem [Intelligence Guide](../guides/intelligence/learning.md).

### Q18: Làm thế nào để enable learning?

**A:** Sử dụng Learner component:

```python
from agentic_sdlc.intelligence.learner import Learner

learner = Learner()

# Learn từ success
learner.learn_success(
    task_type="code_review",
    approach="static_analysis",
    context={"language": "python", "complexity": "medium"}
)

# Learn từ error
learner.learn_error(
    task_type="deployment",
    error_type="timeout",
    context={"environment": "production"}
)

# Find similar cases
similar = learner.find_similar(
    task_type="code_review",
    context={"language": "python"}
)
```text

### Q19: Có thể monitor agent performance không?

**A:** Có, sử dụng Monitor:

```python
from agentic_sdlc.intelligence.monitor import Monitor

monitor = Monitor()

# Record metrics
monitor.record_metric("execution_time", 3.5)
monitor.record_metric("tokens_used", 150)
monitor.record_metric("success_rate", 0.95)

# Check health
health = monitor.check_health()
print(f"System health: {health.status}")

# Get statistics
stats = monitor.get_statistics()
print(f"Average execution time: {stats['avg_execution_time']}")
```text

### Q20: Reasoner giúp gì?

**A:** Reasoner analyze tasks và recommend execution strategies:

```python
from agentic_sdlc.intelligence.reasoner import Reasoner

reasoner = Reasoner()

# Analyze complexity
complexity = reasoner.analyze_task_complexity(
    task_description="Refactor legacy codebase",
    context={"lines_of_code": 50000, "dependencies": 30}
)
print(f"Complexity: {complexity.level}")  # low, medium, high

# Recommend execution mode
mode = reasoner.recommend_execution_mode(
    task_complexity="high",
    available_resources={"agents": 5, "memory": "16GB"}
)
print(f"Recommended mode: {mode}")  # sequential, parallel, distributed

# Route task to appropriate agent
agent_type = reasoner.route_task(
    task_description="Fix security vulnerability",
    available_agents=["dev-agent", "security-agent"]
)
print(f"Route to: {agent_type}")
```text

---

## Plugins

### Q21: Làm thế nào để tạo plugin?

**A:** Implement Plugin base class:

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
        # Setup logic
        self.config = self.load_config()
    
    def shutdown(self) -> None:
        # Cleanup logic
        self.save_state()
    
    def process(self, data):
        # Plugin logic
        return processed_data
```text

Xem [Plugin Development Guide](../guides/plugins/creating-plugins.md).

### Q22: Làm thế nào để load plugin?

**A:** Sử dụng PluginRegistry:

```python
from agentic_sdlc.plugins.registry import PluginRegistry

registry = PluginRegistry()

# Load plugin
plugin = registry.load_plugin("my-plugin")

# Initialize
plugin.initialize()

# Use plugin
result = plugin.process(data)

# Cleanup
plugin.shutdown()
```text

### Q23: Plugin có thể có dependencies không?

**A:** Có, declare trong plugin metadata:

```python
class MyPlugin(Plugin):
    @property
    def dependencies(self) -> List[str]:
        return ["requests", "pandas", "numpy"]
    
    def initialize(self) -> None:
        # Check dependencies
        self.check_dependencies()
        # Import dependencies
        import requests
        import pandas as pd
```text

---

## Performance và Scaling

### Q24: Làm thế nào để optimize performance?

**A:** Một số strategies:

1. **Caching**: Cache LLM responses
```python
from agentic_sdlc.core.cache import enable_cache

enable_cache(backend="redis", ttl=3600)
```text

2. **Parallel execution**: Run independent tasks parallel
```python
workflow.execute(parallel=True, max_workers=5)
```text

3. **Batch processing**: Process multiple items together
```python
results = agent.execute_batch(tasks, batch_size=10)
```text

4. **Resource limits**: Set appropriate limits
```python
agent = create_agent("optimized", "DEVELOPER",
                    max_memory_mb=2048,
                    max_execution_time=300)
```text

### Q25: Có thể scale horizontally không?

**A:** Có, deploy multiple instances:

```python
from agentic_sdlc.infrastructure.distributed import DistributedCoordinator

coordinator = DistributedCoordinator(
    nodes=["node1:8000", "node2:8000", "node3:8000"]
)

# Distribute workflow across nodes
result = coordinator.execute_distributed(workflow)
```text

### Q26: Làm thế nào để reduce API costs?

**A:** Một số tips:

1. **Use cheaper models** cho simple tasks
2. **Enable caching** để avoid duplicate calls
3. **Batch requests** khi có thể
4. **Set token limits** để control costs
5. **Fallback to local models** cho non-critical tasks

```python
config = ModelConfig(
    provider="openai",
    model="gpt-3.5-turbo",  # Cheaper than gpt-4
    max_tokens=500,  # Limit tokens
    cache_enabled=True
)
```text

---

## Troubleshooting

### Q27: Agent không respond, làm gì?

**A:** Check các điểm sau:

1. API key valid không?
2. Network connection OK không?
3. Rate limit exceeded không?
4. Timeout setting có reasonable không?

```python
# Enable debug logging
import logging
logging.basicConfig(level=logging.DEBUG)

# Test với timeout
try:
    result = agent.execute("task", timeout=30)
except TimeoutError:
    print("Agent timed out")
except Exception as e:
    print(f"Error: {e}")
```text

Xem [Debugging Guide](debugging.md).

### Q28: Workflow bị stuck, làm sao?

**A:** Check workflow state:

```python
# Get workflow status
status = workflow.get_status()
print(f"Current step: {status.current_step}")
print(f"Completed steps: {status.completed_steps}")
print(f"Pending steps: {status.pending_steps}")

# Check for circular dependencies
validation = workflow.validate()
if not validation.is_valid:
    print(f"Validation errors: {validation.errors}")
```text

### Q29: Memory usage cao, làm gì?

**A:** Profile và optimize:

```python
import tracemalloc

tracemalloc.start()

# Execute code
agent.execute("task")

# Check memory
snapshot = tracemalloc.take_snapshot()
top_stats = snapshot.statistics('lineno')

for stat in top_stats[:10]:
    print(stat)
```text

Xem [Performance Guide](../guides/advanced/performance.md).

### Q30: Làm thế nào để report bugs?

**A:** Report bugs tại GitHub Issues:

1. Describe the problem clearly
2. Include code to reproduce
3. Provide error messages và logs
4. Specify environment (OS, Python version, package version)

```bash
# Collect environment info
python -c "import sys; print(sys.version)"
pip show agentic-sdlc
uname -a  # On Linux/macOS
```

---

## Migration và Upgrade

### Q31: Làm thế nào để upgrade từ v2.x?

**A:** Follow migration guide:

1. Backup current code
2. Update package: `pip install --upgrade agentic-sdlc`
3. Update imports (v3 có new structure)
4. Update config format
5. Test thoroughly

Xem [Migration Guide](../migration/from-v2.md).

### Q32: Breaking changes trong v3.0.0?

**A:** Major changes:

- New module structure
- Updated API signatures
- New configuration format
- Enhanced intelligence layer
- Improved plugin system

Check [Upgrade Guide](../migration/upgrade-guide.md) cho details.

---

## Tổng Kết

FAQ này cover các câu hỏi phổ biến nhất. Nếu câu hỏi của bạn không có ở đây:

- Check [Documentation](../README.md)
- Read [Common Errors](common-errors.md)
- See [Debugging Guide](debugging.md)
- Ask on GitHub Discussions
- Contact support

Happy coding với Agentic SDLC! 🚀
