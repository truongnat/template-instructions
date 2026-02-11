# Multi-Agent Workflow Example

This example demonstrates how multiple agents collaborate in the SDLC Kit to complete a complex software development workflow. It showcases agent coordination, task dependencies, and the full development lifecycle from requirements to testing.

## Overview

This workflow simulates a realistic software development scenario where three specialized agents work together:

1. **Business Analyst** - Gathers and documents requirements
2. **Developer** - Designs and implements the solution
3. **Quality Judge** - Reviews code and validates quality

The agents collaborate through a series of dependent tasks, with each agent contributing their specialized expertise.

## Workflow Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    Multi-Agent Workflow                     │
└─────────────────────────────────────────────────────────────┘
                            │
                            ▼
        ┌──────────────────────────────────────┐
        │  1. Gather Requirements              │
        │     Agent: Business Analyst          │
        │     Type: Analysis                   │
        └──────────────────────────────────────┘
                            │
                            ▼
        ┌──────────────────────────────────────┐
        │  2. Design Solution                  │
        │     Agent: Developer                 │
        │     Type: Research                   │
        └──────────────────────────────────────┘
                            │
                            ▼
        ┌──────────────────────────────────────┐
        │  3. Implement Feature                │
        │     Agent: Developer                 │
        │     Type: Implementation             │
        └──────────────────────────────────────┘
                            │
                            ▼
        ┌──────────────────────────────────────┐
        │  4. Code Review                      │
        │     Agent: Quality Judge             │
        │     Type: Validation                 │
        └──────────────────────────────────────┘
                            │
                            ▼
        ┌──────────────────────────────────────┐
        │  5. Run Tests                        │
        │     Agent: Quality Judge             │
        │     Type: Testing                    │
        └──────────────────────────────────────┘
                            │
                            ▼
                      ┌─────────┐
                      │ Complete│
                      └─────────┘
```

## Agent Roles and Responsibilities

### Business Analyst Agent

**Configuration**: `agents/business-analyst.yaml`

**Responsibilities**:
- Gather and document requirements
- Analyze stakeholder needs
- Create user stories and acceptance criteria
- Validate business requirements

**Capabilities**:
- Requirements gathering
- Stakeholder analysis
- User story creation
- Documentation

**Configuration Highlights**:
- Temperature: 0.7 (balanced creativity and consistency)
- Timeout: 10 minutes
- Model: gemini-2.0-flash

### Developer Agent

**Configuration**: `agents/developer-agent.yaml`

**Responsibilities**:
- Design software architecture
- Implement features and functionality
- Write clean, maintainable code
- Create technical documentation

**Capabilities**:
- Code generation
- Architecture design
- Design patterns
- Code refactoring
- Performance optimization

**Configuration Highlights**:
- Temperature: 0.5 (more deterministic for code)
- Timeout: 30 minutes
- Max tokens: 8192 (for larger code outputs)
- Model: gemini-2.0-flash

### Quality Judge Agent

**Configuration**: `agents/quality-judge.yaml`

**Responsibilities**:
- Review code quality
- Validate test coverage
- Check for security vulnerabilities
- Ensure best practices compliance

**Capabilities**:
- Code review
- Quality assessment
- Test validation
- Security analysis
- Performance review

**Configuration Highlights**:
- Temperature: 0.3 (objective, consistent reviews)
- Timeout: 15 minutes
- Model: gemini-2.0-flash

## Workflow Tasks

### Task 1: Gather Requirements
- **Agent**: Business Analyst
- **Type**: Analysis
- **Priority**: Critical
- **Timeout**: 10 minutes
- **Dependencies**: None (first task)

The Business Analyst gathers requirements, creates user stories, and defines acceptance criteria.

### Task 2: Design Solution
- **Agent**: Developer
- **Type**: Research
- **Priority**: High
- **Timeout**: 15 minutes
- **Dependencies**: gather-requirements

The Developer researches approaches and designs the solution architecture based on requirements.

### Task 3: Implement Feature
- **Agent**: Developer
- **Type**: Implementation
- **Priority**: High
- **Timeout**: 30 minutes
- **Dependencies**: design-solution

The Developer implements the feature according to the design, following coding standards.

### Task 4: Code Review
- **Agent**: Quality Judge
- **Type**: Validation
- **Priority**: High
- **Timeout**: 10 minutes
- **Dependencies**: implement-feature

The Quality Judge reviews the code for quality, security, and best practices compliance.

### Task 5: Run Tests
- **Agent**: Quality Judge
- **Type**: Testing
- **Priority**: Critical
- **Timeout**: 15 minutes
- **Dependencies**: code-review

The Quality Judge validates test coverage and runs the test suite.

## Prerequisites

Before running this example, ensure you have:

1. **SDLC Kit installed**:
   ```bash
   pip install -r requirements.txt
   ```

2. **Environment configured**:
   ```bash
   cp .env.template .env
   # Edit .env and set required API keys
   ```

3. **Required API keys**:
   - `GOOGLE_GENAI_API_KEY` for Gemini models

## Running the Example

### Method 1: Using the CLI

```bash
# Validate the workflow configuration
python -m agentic_sdlc.cli workflow validate examples/multi-agent-workflow/workflow.yaml

# Validate agent configurations
python -m agentic_sdlc.cli agent validate examples/multi-agent-workflow/agents/business-analyst.yaml
python -m agentic_sdlc.cli agent validate examples/multi-agent-workflow/agents/developer-agent.yaml
python -m agentic_sdlc.cli agent validate examples/multi-agent-workflow/agents/quality-judge.yaml

# Run the workflow
python -m agentic_sdlc.cli workflow run examples/multi-agent-workflow/workflow.yaml \
  --agent-configs examples/multi-agent-workflow/agents/
```

### Method 2: Using Python Script

```python
from agentic_sdlc.orchestration.engine.workflow_engine import WorkflowEngine
from config.validators import ConfigValidator
import yaml
import glob

# Load workflow configuration
with open('examples/multi-agent-workflow/workflow.yaml', 'r') as f:
    workflow_config = yaml.safe_load(f)

# Load agent configurations
agent_configs = {}
for agent_file in glob.glob('examples/multi-agent-workflow/agents/*.yaml'):
    with open(agent_file, 'r') as f:
        agent_config = yaml.safe_load(f)
        agent_configs[agent_config['id']] = agent_config

# Validate configurations
validator = ConfigValidator()

# Validate workflow
workflow_result = validator.load_and_validate(
    'examples/multi-agent-workflow/workflow.yaml',
    'config/schemas/workflow.schema.json'
)

if not workflow_result.is_valid:
    print(f"Workflow validation failed: {workflow_result.errors}")
    exit(1)

# Validate agents
for agent_id, agent_config in agent_configs.items():
    agent_result = validator.validate(agent_config, 'agent')
    if not agent_result.is_valid:
        print(f"Agent {agent_id} validation failed: {agent_result.errors}")
        exit(1)

# Initialize and run the workflow
engine = WorkflowEngine(workflow_config, agent_configs)
result = engine.execute()

print(f"Workflow completed with status: {result.status}")
print(f"Tasks completed: {result.tasks_completed}/{result.total_tasks}")
```

### Method 3: Using the Workflow Test Runner

```bash
python agentic_sdlc/testing/workflow_test_runner.py \
  examples/multi-agent-workflow/workflow.yaml \
  --agent-dir examples/multi-agent-workflow/agents/
```

## Expected Output

When you run this workflow, you should see output similar to:

```
[INFO] Starting workflow: multi-agent-collaboration (v1.0.0)
[INFO] Loading 3 agents: business-analyst, developer-agent, quality-judge
[INFO] Initializing agent: business-analyst
[INFO] Initializing agent: developer-agent
[INFO] Initializing agent: quality-judge

[INFO] === Task 1/5: gather-requirements ===
[INFO] Assigned to: business-analyst
[INFO] Executing analysis task...
[INFO] Business Analyst: Gathering requirements...
[INFO] Business Analyst: Created 5 user stories
[INFO] Business Analyst: Defined acceptance criteria
[INFO] Task completed successfully (Duration: 45s)

[INFO] === Task 2/5: design-solution ===
[INFO] Assigned to: developer-agent
[INFO] Executing research task...
[INFO] Developer: Analyzing requirements...
[INFO] Developer: Designing architecture...
[INFO] Developer: Selected design patterns: Factory, Observer
[INFO] Task completed successfully (Duration: 120s)

[INFO] === Task 3/5: implement-feature ===
[INFO] Assigned to: developer-agent
[INFO] Executing implementation task...
[INFO] Developer: Implementing feature...
[INFO] Developer: Generated 450 lines of code
[INFO] Developer: Created unit tests
[INFO] Task completed successfully (Duration: 380s)

[INFO] === Task 4/5: code-review ===
[INFO] Assigned to: quality-judge
[INFO] Executing validation task...
[INFO] Quality Judge: Reviewing code quality...
[INFO] Quality Judge: Checking security vulnerabilities...
[INFO] Quality Judge: Code quality score: 8.5/10
[INFO] Quality Judge: Found 2 minor issues (documented)
[INFO] Task completed successfully (Duration: 95s)

[INFO] === Task 5/5: run-tests ===
[INFO] Assigned to: quality-judge
[INFO] Executing testing task...
[INFO] Quality Judge: Running test suite...
[INFO] Quality Judge: 45 tests passed, 0 failed
[INFO] Quality Judge: Code coverage: 87%
[INFO] Task completed successfully (Duration: 180s)

[INFO] Workflow completed with status: SUCCESS
[INFO] Total duration: 820 seconds (13.7 minutes)
[INFO] Tasks completed: 5/5
```

## Customization

### Adding More Agents

You can add additional agents to the workflow:

1. Create a new agent configuration file in `agents/`:
   ```yaml
   # agents/security-analyst.yaml
   id: "security-analyst"
   type: "security_analyst"
   name: "Security Analyst Agent"
   # ... rest of configuration
   ```

2. Add the agent to the workflow:
   ```yaml
   agents:
     - "business-analyst"
     - "developer-agent"
     - "quality-judge"
     - "security-analyst"  # New agent
   ```

3. Create tasks for the new agent:
   ```yaml
   - id: "security-audit"
     type: "validation"
     config:
       priority: "critical"
       timeout: 600
       assigned_agent: "security-analyst"
     dependencies: ["code-review"]
   ```

### Modifying Task Dependencies

You can change the workflow structure by modifying dependencies:

```yaml
# Parallel execution: design and implement can run simultaneously
tasks:
  - id: "design-solution"
    dependencies: ["gather-requirements"]
    
  - id: "implement-feature"
    dependencies: ["gather-requirements"]  # Changed from design-solution
    
  - id: "code-review"
    dependencies: ["design-solution", "implement-feature"]  # Wait for both
```

### Adjusting Agent Behavior

Modify agent configuration to change behavior:

```yaml
# Make developer more creative
config:
  temperature: 0.8  # Increased from 0.5
  
# Give agent more time
timeout: 3600  # 1 hour instead of 30 minutes

# Add more capabilities
capabilities:
  - "code_generation"
  - "architecture_design"
  - "machine_learning"  # New capability
```

## Monitoring and Debugging

### Enable Verbose Logging

```bash
# Set log level to DEBUG
export SDLC_LOG_LEVEL=DEBUG

# Run workflow with verbose output
python -m agentic_sdlc.cli workflow run \
  examples/multi-agent-workflow/workflow.yaml \
  --verbose
```

### Check Workflow State

```bash
# View workflow execution state
python -m agentic_sdlc.cli workflow status <workflow-id>

# View task details
python -m agentic_sdlc.cli workflow task-status <workflow-id> <task-id>
```

### Review Logs

```bash
# View workflow logs
tail -f logs/sdlc-kit.log

# Filter by agent
grep "business-analyst" logs/sdlc-kit.log

# Filter by task
grep "gather-requirements" logs/sdlc-kit.log
```

## Troubleshooting

### Agent Initialization Fails

**Problem**: Agent fails to initialize

**Solutions**:
- Verify agent configuration file is valid YAML
- Check that agent ID matches in workflow and agent config
- Ensure API keys are set in environment
- Validate agent config against schema

### Task Timeout

**Problem**: Task exceeds timeout limit

**Solutions**:
- Increase task timeout in workflow.yaml
- Increase agent timeout in agent config
- Check for API rate limiting
- Review task complexity

### Dependency Errors

**Problem**: Task dependencies not satisfied

**Solutions**:
- Verify dependency task IDs are correct
- Check that dependency tasks completed successfully
- Review task execution order
- Ensure no circular dependencies

### Validation Errors

**Problem**: Configuration validation fails

**Solutions**:
```bash
# Validate workflow
python scripts/validate-config.py

# Check specific validation errors
python -m agentic_sdlc.cli workflow validate \
  examples/multi-agent-workflow/workflow.yaml --verbose
```

## Performance Optimization

### Parallel Task Execution

Enable parallel execution for independent tasks:

```yaml
# In workflow.yaml
execution:
  mode: "parallel"
  max_concurrent_tasks: 3
```

### Agent Caching

Enable response caching to speed up repeated operations:

```yaml
# In agent config
config:
  enable_caching: true
  cache_ttl: 3600  # 1 hour
```

### Reduce Model Tokens

Optimize token usage for faster responses:

```yaml
config:
  max_tokens: 2048  # Reduced from 4096
```

## Best Practices

1. **Clear Task Dependencies**: Define explicit dependencies to ensure correct execution order
2. **Appropriate Timeouts**: Set realistic timeouts based on task complexity
3. **Agent Specialization**: Assign tasks to agents based on their capabilities
4. **Error Handling**: Configure retry policies for transient failures
5. **Monitoring**: Enable logging and metrics for production workflows
6. **Documentation**: Document agent roles and task purposes
7. **Validation**: Always validate configurations before deployment

## Related Examples

- **Basic Workflow**: `examples/basic-workflow/` - Simple single-agent workflow
- **GitHub Integration**: `examples/integrations/github/` - Integrate with GitHub
- **Slack Integration**: `examples/integrations/slack/` - Send notifications

## Additional Resources

- [Workflow Schema Documentation](../../config/schemas/README.md)
- [Agent Configuration Guide](../../docs/CONFIGURATION.md)
- [Multi-Agent Patterns](../../docs/MULTI_AGENT_PATTERNS.md)
- [Troubleshooting Guide](../../docs/TROUBLESHOOTING.md)

## Support

If you encounter issues:
- Check the [Troubleshooting Guide](../../docs/TROUBLESHOOTING.md)
- Review [GitHub Issues](https://github.com/your-org/sdlc-kit/issues)
- Join our community discussions

---

**Happy collaborating!** 🤝
