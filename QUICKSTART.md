# Agentic SDLC - Quick Start Guide

## Installation

```bash
# Install in development mode
pip install -e .

# Or with CLI dependencies
pip install -e ".[cli]"
```

## Verify Installation

```bash
python3 verify_implementation.py
```

Expected output:
```
🎉 ALL TESTS PASSED - System is fully functional!
```

## Basic Usage

### 1. Configuration

```python
from agentic_sdlc import Config

# Load default configuration
config = Config()

# Or load from file
config = Config(config_path="config.yaml")

# Get configuration values
log_level = config.get("log_level", "INFO")

# Set configuration values
config.set("log_level", "DEBUG")
```

### 2. Create Agents

```python
from agentic_sdlc import create_agent, get_agent_registry

# Create an agent
agent = create_agent(
    name="developer",
    role="software_developer",
    model_name="gpt-4",
    system_prompt="You are a helpful software developer",
    tools=["code_analyzer", "test_runner"],
    max_iterations=10
)

# Get the agent registry
registry = get_agent_registry()

# List all agents
agents = registry.list_agents()
```

### 3. Learning & Monitoring

```python
from agentic_sdlc import Learner, Monitor, MetricsCollector

# Initialize learner
learner = Learner()

# Learn from success
learner.learn_success(
    task="API integration",
    approach="REST with retry logic",
    context={"duration": 5.2, "complexity": "medium"}
)

# Learn from errors
learner.learn_error(
    error="Connection timeout",
    resolution="Added retry with exponential backoff",
    context={"attempts": 3}
)

# Find similar patterns
similar = learner.find_similar("API integration")

# Initialize monitor
monitor = Monitor()

# Record metrics
monitor.record_metric("task_duration", 5.2)
monitor.record_metric("success_rate", 0.95)

# Check health
health = monitor.check_health()
print(f"System status: {health.status}")

# Collect metrics over time
collector = MetricsCollector()
collector.collect("response_time", 120)
collector.collect("response_time", 95)

# Get metric summary
summary = collector.get_metric_summary("response_time")
print(f"Average response time: {summary['avg']}ms")
```

### 4. Reasoning & Decision Making

```python
from agentic_sdlc import Reasoner, DecisionEngine

# Initialize reasoner
reasoner = Reasoner()

# Analyze task complexity
complexity = reasoner.analyze_task_complexity(
    task="Build microservices architecture with 5 services",
    context={"team_size": 3, "deadline": "2 weeks"}
)
print(f"Complexity score: {complexity.score}/10")
print(f"Recommendation: {complexity.recommendation}")

# Recommend execution mode
mode = reasoner.recommend_execution_mode(
    task="Process 1000 files",
    context={"cpu_cores": 8}
)
print(f"Recommended mode: {mode.value}")

# Route tasks to workflows
result = reasoner.route_task(
    task="Deploy to production",
    available_workflows=["ci_cd", "manual_deploy", "canary_deploy"]
)
print(f"Route to: {result.workflow} (confidence: {result.confidence})")

# Use decision engine
engine = DecisionEngine()

# Add decision rules
engine.add_rule("high_priority", lambda ctx: ctx.get("priority") == "high")
engine.add_rule("has_tests", lambda ctx: ctx.get("test_coverage", 0) > 0.8)

# Make decisions
decision = engine.make_decision(
    options=[
        {"name": "option_a", "cost": 100},
        {"name": "option_b", "cost": 200}
    ],
    context={"priority": "high", "test_coverage": 0.9}
)
```

### 5. Team Collaboration

```python
from agentic_sdlc import TeamCoordinator, MessageType

# Initialize coordinator
coordinator = TeamCoordinator()

# Register agents
coordinator.register_agent("developer")
coordinator.register_agent("reviewer")
coordinator.register_agent("tester")

# Send messages between agents
coordinator.send_message(
    sender="developer",
    recipient="reviewer",
    message_type=MessageType.REQUEST,
    content="Please review PR #123",
    metadata={"pr_id": 123}
)

# Start collaboration session
session = coordinator.start_session(
    task="Implement user authentication",
    participants=["developer", "reviewer", "tester"]
)

# Get team statistics
stats = coordinator.get_team_stats()
print(f"Team size: {stats['total_agents']}")
print(f"Total messages: {stats['total_messages']}")
```

### 6. Workflow Execution

```python
from agentic_sdlc import WorkflowRunner
from agentic_sdlc.infrastructure.automation.workflow_engine import WorkflowStep

# Create workflow steps
steps = [
    WorkflowStep(
        name="analyze",
        action="analyze_code",
        parameters={"path": "src/"}
    ),
    WorkflowStep(
        name="test",
        action="run_tests",
        parameters={"suite": "unit"},
        depends_on=["analyze"]
    ),
    WorkflowStep(
        name="deploy",
        action="deploy_app",
        parameters={"environment": "staging"},
        depends_on=["test"]
    )
]

# Run workflow
runner = WorkflowRunner()
results = runner.run(steps)

# Check results
for step_name, result in results.items():
    print(f"{step_name}: {result['status']}")
```

### 7. Model Clients

```python
from agentic_sdlc import create_model_client, register_model_client, get_model_client
from agentic_sdlc import ModelConfig

# Create model configuration
config = ModelConfig(
    provider="openai",
    model_name="gpt-4",
    api_key="your-api-key",
    temperature=0.7,
    max_tokens=1000
)

# Create model client
client = create_model_client(config)

# Register for later use
register_model_client("openai", "gpt-4", client)

# Retrieve registered client
client = get_model_client("openai", "gpt-4")
```

### 8. Plugin System

```python
from agentic_sdlc import Plugin, get_plugin_registry

# Create a custom plugin
class MyPlugin(Plugin):
    @property
    def name(self) -> str:
        return "my-plugin"
    
    @property
    def version(self) -> str:
        return "1.0.0"
    
    def initialize(self, config):
        print(f"Initializing {self.name}")
    
    def shutdown(self):
        print(f"Shutting down {self.name}")

# Register plugin
registry = get_plugin_registry()
plugin = MyPlugin()
registry.register(plugin)

# Get plugin
my_plugin = registry.get("my-plugin")
```

## Complete Example

```python
from agentic_sdlc import (
    Config, create_agent, Learner, Monitor,
    Reasoner, TeamCoordinator, WorkflowRunner
)
from agentic_sdlc.infrastructure.automation.workflow_engine import WorkflowStep

# 1. Setup
config = Config()
learner = Learner()
monitor = Monitor()
reasoner = Reasoner()
coordinator = TeamCoordinator()

# 2. Create agents
dev_agent = create_agent(
    name="developer",
    role="software_developer",
    model_name="gpt-4"
)

test_agent = create_agent(
    name="tester",
    role="qa_engineer",
    model_name="gpt-4"
)

# 3. Register with coordinator
coordinator.register_agent("developer")
coordinator.register_agent("tester")

# 4. Analyze task
task = "Build REST API with authentication"
complexity = reasoner.analyze_task_complexity(task)
print(f"Task complexity: {complexity.score}/10")

# 5. Create workflow
steps = [
    WorkflowStep(name="design", action="design_api", parameters={}),
    WorkflowStep(name="implement", action="code_api", parameters={}, depends_on=["design"]),
    WorkflowStep(name="test", action="test_api", parameters={}, depends_on=["implement"])
]

# 6. Execute workflow
runner = WorkflowRunner()
results = runner.run(steps)

# 7. Monitor and learn
monitor.record_metric("workflow_duration", 120)
learner.learn_success(
    task=task,
    approach="REST with JWT authentication",
    context={"duration": 120, "complexity": complexity.score}
)

# 8. Check health
health = monitor.check_health()
print(f"System health: {health.status}")

print("✓ Workflow completed successfully!")
```

## CLI Usage (Basic)

```bash
# Show version
python3 asdlc.py --version

# Initialize project (stub)
python3 asdlc.py init

# Run workflow (stub)
python3 asdlc.py run my-workflow

# Check status (stub)
python3 asdlc.py status
```

## Documentation

- **System Audit**: `.kiro/SYSTEM_AUDIT_REPORT.md`
- **Quick Reference**: `.kiro/QUICK_REFERENCE.md`
- **Implementation Guide**: `.kiro/IMPLEMENTATION_ROADMAP.md`
- **Visual Overview**: `.kiro/VISUAL_OVERVIEW.md`
- **Complete Report**: `.kiro/IMPLEMENTATION_COMPLETE.md`
- **Final Summary**: `.kiro/FINAL_SUMMARY.md`

## Troubleshooting

### Import Errors

```bash
# Install dependencies
pip install PyYAML pydantic python-dotenv

# Verify installation
python3 verify_implementation.py
```

### Module Not Found

```bash
# Make sure you're in the project root
cd /path/to/agentic-sdlc

# Install in development mode
pip install -e .
```

## Next Steps

1. Read `.kiro/FINAL_SUMMARY.md` for complete status
2. Explore examples in `examples/` directory
3. Check documentation in `docs/` directory
4. Run verification: `python3 verify_implementation.py`

## Support

- Issues: https://github.com/truongnat/agentic-sdlc/issues
- Documentation: See `.kiro/` directory
- Examples: See `examples/` directory

---

**Status:** ✅ System is fully functional  
**Version:** 3.0.0  
**Last Updated:** February 11, 2026
