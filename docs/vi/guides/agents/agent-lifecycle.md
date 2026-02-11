# Agent Lifecycle Management

**Phiên bản**: 3.0.0  
**Cập nhật lần cuối**: 11/02/2026


## Giới Thiệu

Tài liệu này mô tả chi tiết lifecycle của agents trong Agentic SDLC, từ khâu tạo (creation), đăng ký (registration), cấu hình (configuration), thực thi (execution), monitoring, đến cleanup. Hiểu rõ lifecycle giúp bạn quản lý agents hiệu quả và tối ưu hóa performance.

## Agent Lifecycle Overview

```mermaid
stateDiagram-v2
    [*] --> Created: create_agent()
    Created --> Registered: Auto-register
    Registered --> Configured: Configure settings
    Configured --> Ready: Validation passed
    Ready --> Executing: Assign task
    Executing --> Completed: Task done
    Executing --> Failed: Error occurred
    Completed --> Ready: Available for next task
    Failed --> Ready: Error handled
    Ready --> Archived: Deactivate
    Archived --> [*]: Remove from registry
```javascript

## Phase 1: Creation

### Tạo Agent Mới

Agent được tạo thông qua function `create_agent()`:

```python
from agentic_sdlc import create_agent

# Tạo agent với parameters cơ bản
agent = create_agent(
    name="my-agent",
    role="Developer",
    model_name="gpt-4"
)

print(f"Agent created with ID: {agent.id}")
print(f"Status: Created")
```text

### Validation During Creation

Khi tạo agent, hệ thống validate:

```python
# Validation checks
def validate_agent_creation(agent):
    """Validate agent parameters during creation."""
    if not agent.name:
        raise ValueError("Agent name cannot be empty")
    if not agent.role:
        raise ValueError("Agent role cannot be empty")
    if not agent.model_name:
        raise ValueError("Agent model_name cannot be empty")
    if agent.max_iterations < 1:
        raise ValueError("Agent max_iterations must be at least 1")
```text

### Creation Events

```python
from agentic_sdlc.intelligence import Monitor

monitor = Monitor()

# Log agent creation
monitor.record_metric(
    agent_id=agent.id,
    metric_name="agent_created",
    value=1,
    metadata={
        "name": agent.name,
        "role": agent.role,
        "model": agent.model_name,
        "timestamp": datetime.now().isoformat()
    }
)
```text


## Phase 2: Registration

### Auto-Registration

Agents được tự động đăng ký vào AgentRegistry khi tạo:

```python
from agentic_sdlc import create_agent, get_agent_registry

# Agent tự động registered
agent = create_agent(
    name="auto-registered-agent",
    role="Developer",
    model_name="gpt-4"
)

# Verify registration
registry = get_agent_registry()
assert registry.has_agent(agent.id)
print(f"Agent {agent.name} registered successfully")
```text

### Manual Registration

Có thể register agent manually nếu cần:

```python
from agentic_sdlc.orchestration import Agent, get_agent_registry

# Tạo agent object trực tiếp
agent = Agent(
    name="manual-agent",
    role="Developer",
    model_name="gpt-4"
)

# Register manually
registry = get_agent_registry()
registry.register_agent(agent)

print(f"Agent {agent.id} registered manually")
```text

### Registration Validation

Registry kiểm tra duplicate names:

```python
try:
    # Attempt to register duplicate
    agent1 = create_agent(name="duplicate", role="Dev", model_name="gpt-4")
    agent2 = create_agent(name="duplicate", role="Dev", model_name="gpt-4")
except ValueError as e:
    print(f"Registration failed: {e}")
    # Handle duplicate name error
```text

### Registry Operations

```python
registry = get_agent_registry()

# Get agent by ID
agent = registry.get_agent("agent-id-123")

# Get agent by name
agent = registry.get_agent_by_name("my-agent")

# Check if agent exists
if registry.has_agent("my-agent"):
    print("Agent exists in registry")

# List all agents
all_agents = registry.list_agents()
print(f"Total agents: {len(all_agents)}")

# Remove agent
registry.remove_agent("agent-id-123")
```text

## Phase 3: Configuration

### Initial Configuration

Configure agent sau khi tạo:

```python
agent = create_agent(
    name="configurable-agent",
    role="Developer",
    model_name="gpt-4"
)

# Configure system prompt
agent.system_prompt = """You are an expert Python developer.
Focus on clean code, best practices, and comprehensive testing."""

# Add tools
agent.tools = ["code_execution", "file_operations", "git_operations"]

# Set max iterations
agent.max_iterations = 15

# Add metadata
agent.metadata = {
    "team": "backend",
    "expertise": ["python", "fastapi"],
    "version": "1.0.0"
}
```text

### Dynamic Reconfiguration

Update configuration during runtime:

```python
# Get agent from registry
agent = registry.get_agent_by_name("my-agent")

# Update system prompt
agent.system_prompt += "\nAlways include error handling."

# Add new tool
agent.tools.append("database_query")

# Update metadata
agent.metadata["last_updated"] = datetime.now().isoformat()
agent.metadata["version"] = "1.1.0"

print(f"Agent {agent.name} reconfigured")
```text

### Configuration Validation

```python
def validate_agent_config(agent):
    """Validate agent configuration."""
    errors = []
    
    # Check system prompt
    if agent.system_prompt and len(agent.system_prompt) < 10:
        errors.append("System prompt too short")
    
    # Check tools
    valid_tools = ["code_execution", "file_operations", "git_operations"]
    for tool in agent.tools:
        if tool not in valid_tools:
            errors.append(f"Invalid tool: {tool}")
    
    # Check max_iterations
    if agent.max_iterations > 100:
        errors.append("Max iterations too high (>100)")
    
    return errors

# Validate before use
errors = validate_agent_config(agent)
if errors:
    print(f"Configuration errors: {errors}")
else:
    print("Configuration valid")
```text


## Phase 4: Execution

### Task Assignment

Assign tasks to agents trong workflows:

```python
from agentic_sdlc import Workflow, WorkflowStep

# Create workflow
workflow = Workflow(name="development-workflow")

# Assign task to agent
workflow.add_step(
    WorkflowStep(
        name="implement-feature",
        agent=agent,
        action="implement",
        parameters={
            "feature": "user-authentication",
            "requirements": "requirements.md"
        }
    )
)

# Execute workflow
result = workflow.execute()
```text

### Execution States

Agent có các states trong execution:

```python
class AgentState:
    IDLE = "idle"              # Waiting for task
    ASSIGNED = "assigned"      # Task assigned
    EXECUTING = "executing"    # Currently executing
    COMPLETED = "completed"    # Task completed
    FAILED = "failed"          # Execution failed
    PAUSED = "paused"          # Execution paused

# Track agent state
agent.metadata["state"] = AgentState.EXECUTING
agent.metadata["current_task"] = "implement-feature"
agent.metadata["started_at"] = datetime.now().isoformat()
```text

### Iteration Management

Agent thực hiện tasks với max_iterations limit:

```python
def execute_with_iterations(agent, task):
    """Execute task with iteration limit."""
    for iteration in range(agent.max_iterations):
        try:
            result = agent.execute(task)
            if result.success:
                print(f"Task completed in {iteration + 1} iterations")
                return result
        except Exception as e:
            print(f"Iteration {iteration + 1} failed: {e}")
            if iteration == agent.max_iterations - 1:
                raise RuntimeError(f"Max iterations ({agent.max_iterations}) reached")
    
    raise RuntimeError("Task not completed within max iterations")
```text

### Error Handling

Handle errors during execution:

```python
from agentic_sdlc.core.exceptions import AgenticSDLCError

try:
    result = agent.execute(task)
except AgenticSDLCError as e:
    # Log error
    monitor.record_metric(
        agent_id=agent.id,
        metric_name="execution_error",
        value=1,
        metadata={
            "error": str(e),
            "task": task.name,
            "timestamp": datetime.now().isoformat()
        }
    )
    
    # Update agent state
    agent.metadata["state"] = AgentState.FAILED
    agent.metadata["last_error"] = str(e)
    
    # Retry or escalate
    if should_retry(e):
        retry_task(agent, task)
    else:
        escalate_error(agent, task, e)
```text

## Phase 5: Monitoring

### Performance Metrics

Track agent performance:

```python
from agentic_sdlc.intelligence import Monitor

monitor = Monitor()

# Record execution metrics
monitor.record_metric(
    agent_id=agent.id,
    metric_name="task_duration",
    value=execution_time_seconds,
    metadata={
        "task": task.name,
        "iterations": iterations_used,
        "success": True
    }
)

# Record resource usage
monitor.record_metric(
    agent_id=agent.id,
    metric_name="tokens_used",
    value=total_tokens,
    metadata={
        "model": agent.model_name,
        "cost": estimated_cost
    }
)
```text

### Health Checks

Monitor agent health:

```python
def check_agent_health(agent):
    """Check agent health status."""
    health = {
        "agent_id": agent.id,
        "name": agent.name,
        "status": "healthy",
        "issues": []
    }
    
    # Check if agent is responsive
    if not is_agent_responsive(agent):
        health["status"] = "unhealthy"
        health["issues"].append("Agent not responsive")
    
    # Check error rate
    error_rate = get_agent_error_rate(agent)
    if error_rate > 0.5:
        health["status"] = "degraded"
        health["issues"].append(f"High error rate: {error_rate:.2%}")
    
    # Check resource usage
    if agent.metadata.get("tokens_used", 0) > 1000000:
        health["status"] = "warning"
        health["issues"].append("High token usage")
    
    return health

# Periodic health check
health = check_agent_health(agent)
print(f"Agent health: {health['status']}")
if health["issues"]:
    print(f"Issues: {', '.join(health['issues'])}")
```text

### Activity Logging

Log agent activities:

```python
import logging

logger = logging.getLogger(f"agent.{agent.name}")

# Log task start
logger.info(f"Agent {agent.name} starting task: {task.name}")

# Log progress
logger.debug(f"Agent {agent.name} iteration {iteration}/{agent.max_iterations}")

# Log completion
logger.info(f"Agent {agent.name} completed task: {task.name} in {duration}s")

# Log errors
logger.error(f"Agent {agent.name} failed task: {task.name} - {error}")
```text


## Phase 6: Collaboration

### Multi-Agent Coordination

Agents collaborate trong workflows:

```python
from agentic_sdlc.intelligence import TeamCoordinator

# Create team coordinator
coordinator = TeamCoordinator()

# Register agents
coordinator.register_agent(backend_agent)
coordinator.register_agent(frontend_agent)
coordinator.register_agent(reviewer_agent)

# Start collaboration session
session_id = coordinator.start_session(
    session_name="feature-development",
    participants=[backend_agent.name, frontend_agent.name, reviewer_agent.name]
)

# Agents communicate
coordinator.send_message(
    sender=backend_agent.name,
    recipient=frontend_agent.name,
    message_type="request",
    content="API endpoints ready for integration"
)
```text

### Message Passing

Agents exchange messages:

```python
from agentic_sdlc.intelligence import Collaborator, MessageType

# Create collaborator for agent
collaborator = Collaborator(agent_name=agent.name)

# Send message
message = collaborator.send_message(
    recipient="other-agent",
    message_type=MessageType.REQUEST,
    content="Need code review for PR #123",
    metadata={"pr_url": "https://github.com/repo/pull/123"}
)

# Receive messages
messages = collaborator.get_messages(sender="other-agent")
for msg in messages:
    print(f"From {msg.sender}: {msg.content}")
```text

### Collaboration Patterns

```python
# Sequential collaboration
def sequential_workflow(agents, task):
    """Agents work sequentially."""
    result = task
    for agent in agents:
        result = agent.execute(result)
    return result

# Parallel collaboration
def parallel_workflow(agents, task):
    """Agents work in parallel."""
    results = []
    for agent in agents:
        result = agent.execute(task)
        results.append(result)
    return merge_results(results)

# Review pattern
def review_workflow(developer, reviewer, task):
    """Developer implements, reviewer reviews."""
    implementation = developer.execute(task)
    review = reviewer.execute(implementation)
    if review.approved:
        return implementation
    else:
        return developer.execute(review.feedback)
```text

## Phase 7: Maintenance

### Agent Updates

Update agents over time:

```python
# Version upgrade
agent.metadata["version"] = "2.0.0"
agent.metadata["updated_at"] = datetime.now().isoformat()

# Update system prompt
agent.system_prompt = """Updated system prompt with new guidelines..."""

# Add new capabilities
agent.tools.append("new_tool")

# Log update
logger.info(f"Agent {agent.name} updated to version {agent.metadata['version']}")
```text

### Performance Optimization

Optimize agent configuration:

```python
def optimize_agent(agent):
    """Optimize agent based on performance data."""
    metrics = get_agent_metrics(agent)
    
    # Adjust max_iterations based on average
    avg_iterations = metrics["avg_iterations"]
    if avg_iterations < agent.max_iterations * 0.5:
        agent.max_iterations = int(avg_iterations * 1.5)
        logger.info(f"Reduced max_iterations to {agent.max_iterations}")
    
    # Switch model if needed
    if metrics["avg_task_complexity"] < 0.5:
        agent.model_name = "gpt-3.5-turbo"  # Use cheaper model
        logger.info(f"Switched to {agent.model_name} for cost optimization")
    
    # Update metadata
    agent.metadata["optimized_at"] = datetime.now().isoformat()
    agent.metadata["optimization_reason"] = "performance_tuning"
```text

### Backup và Recovery

Backup agent configuration:

```python
import json

def backup_agent(agent, backup_file):
    """Backup agent configuration."""
    config = {
        "name": agent.name,
        "role": agent.role,
        "model_name": agent.model_name,
        "system_prompt": agent.system_prompt,
        "tools": agent.tools,
        "max_iterations": agent.max_iterations,
        "metadata": agent.metadata
    }
    
    with open(backup_file, 'w') as f:
        json.dump(config, f, indent=2)
    
    logger.info(f"Agent {agent.name} backed up to {backup_file}")

def restore_agent(backup_file):
    """Restore agent from backup."""
    with open(backup_file, 'r') as f:
        config = json.load(f)
    
    agent = create_agent(
        name=config["name"],
        role=config["role"],
        model_name=config["model_name"],
        system_prompt=config["system_prompt"],
        tools=config["tools"],
        max_iterations=config["max_iterations"],
        metadata=config["metadata"]
    )
    
    logger.info(f"Agent {agent.name} restored from {backup_file}")
    return agent
```text

## Phase 8: Deactivation và Cleanup

### Deactivate Agent

Deactivate agent khi không còn cần:

```python
def deactivate_agent(agent):
    """Deactivate agent."""
    # Update state
    agent.metadata["state"] = "deactivated"
    agent.metadata["deactivated_at"] = datetime.now().isoformat()
    
    # Log deactivation
    logger.info(f"Agent {agent.name} deactivated")
    
    # Archive metrics
    archive_agent_metrics(agent)
    
    # Keep in registry but mark as inactive
    agent.metadata["active"] = False

# Deactivate
deactivate_agent(agent)
```text

### Remove from Registry

Remove agent hoàn toàn:

```python
def remove_agent(agent_id):
    """Remove agent from registry."""
    registry = get_agent_registry()
    
    # Get agent
    agent = registry.get_agent(agent_id)
    
    # Backup before removal
    backup_agent(agent, f"backups/{agent.name}.json")
    
    # Archive final metrics
    archive_agent_metrics(agent)
    
    # Remove from registry
    registry.remove_agent(agent_id)
    
    logger.info(f"Agent {agent.name} removed from registry")

# Remove
remove_agent(agent.id)
```text

### Cleanup Resources

Clean up agent resources:

```python
def cleanup_agent_resources(agent):
    """Clean up agent resources."""
    # Clear cached data
    clear_agent_cache(agent)
    
    # Close connections
    close_agent_connections(agent)
    
    # Delete temporary files
    delete_agent_temp_files(agent)
    
    # Clear metrics
    clear_agent_metrics(agent)
    
    logger.info(f"Resources cleaned up for agent {agent.name}")
```text

## Lifecycle Best Practices

### 1. Proper Initialization

```python
# Good: Complete initialization
agent = create_agent(
    name="well-configured-agent",
    role="Developer",
    model_name="gpt-4",
    system_prompt="Detailed system prompt...",
    tools=["code_execution", "file_operations"],
    max_iterations=15,
    metadata={"team": "backend", "version": "1.0.0"}
)

# Bad: Minimal initialization
agent = create_agent(name="agent", role="Dev", model_name="gpt-4")
```text

### 2. Regular Monitoring

```python
# Monitor agent health periodically
def monitor_agents():
    """Monitor all agents periodically."""
    registry = get_agent_registry()
    for agent in registry.list_agents():
        health = check_agent_health(agent)
        if health["status"] != "healthy":
            alert_admin(agent, health)

# Schedule monitoring
schedule.every(5).minutes.do(monitor_agents)
```text

### 3. Graceful Degradation

```python
def execute_with_fallback(agent, task):
    """Execute with fallback to simpler model."""
    try:
        return agent.execute(task)
    except Exception as e:
        logger.warning(f"Agent {agent.name} failed, trying fallback")
        
        # Create fallback agent with simpler model
        fallback = create_agent(
            name=f"{agent.name}-fallback",
            role=agent.role,
            model_name="gpt-3.5-turbo"
        )
        
        return fallback.execute(task)
```text

### 4. Lifecycle Documentation

```python
# Document lifecycle events
agent.metadata["lifecycle_events"] = [
    {"event": "created", "timestamp": "2024-01-15T10:00:00"},
    {"event": "configured", "timestamp": "2024-01-15T10:05:00"},
    {"event": "first_execution", "timestamp": "2024-01-15T10:10:00"},
    {"event": "optimized", "timestamp": "2024-01-20T15:30:00"},
    {"event": "updated", "timestamp": "2024-02-01T09:00:00"}
]
```

## Tài Liệu Liên Quan

- [Tổng Quan về Agents](overview.md)
- [Tạo và Cấu Hình Agents](creating-agents.md)
- [Các Loại Agents](agent-types.md)
- [Monitoring và Metrics](../intelligence/monitoring.md)
- [Team Collaboration](../intelligence/collaboration.md)
- [Workflow Execution](../workflows/building-workflows.md)

## Tóm Tắt

Agent lifecycle trong Agentic SDLC bao gồm 8 phases chính:

1. **Creation**: Tạo agent với `create_agent()`
2. **Registration**: Auto-register vào AgentRegistry
3. **Configuration**: Configure system prompt, tools, metadata
4. **Execution**: Thực thi tasks trong workflows
5. **Monitoring**: Track performance và health
6. **Collaboration**: Multi-agent coordination
7. **Maintenance**: Updates, optimization, backup
8. **Deactivation**: Cleanup và removal

Hiểu rõ lifecycle giúp bạn quản lý agents hiệu quả, optimize performance, và ensure reliability trong production environments.
