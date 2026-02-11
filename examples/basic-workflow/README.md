# Basic Workflow Example

This example demonstrates the fundamental concepts of SDLC Kit workflows. It's designed to help you understand how to create and run a simple workflow with a single agent.

## Overview

This workflow includes:
- **Single Agent**: An analyst agent that performs requirement analysis
- **Single Task**: A basic analysis task with timeout and priority configuration
- **Retry Policy**: Automatic retry on failure with exponential backoff
- **Environment Configuration**: Set up for development environment

## Workflow Structure

The workflow follows this simple flow:

```
Start → Analyze Requirements → Complete
```

## Configuration Details

### Workflow Settings
- **Name**: `basic-workflow-example`
- **Version**: `1.0.0`
- **Timeout**: 30 minutes (1800 seconds)
- **Environment**: Development

### Agent Configuration
- **Agent ID**: `analyst-agent`
- **Role**: Performs requirement analysis

### Task Configuration
- **Task ID**: `analyze-requirements`
- **Type**: Analysis
- **Priority**: High
- **Timeout**: 5 minutes (300 seconds)
- **Dependencies**: None (first task in workflow)

### Retry Policy
- **Max Attempts**: 3
- **Backoff Multiplier**: 2 (exponential backoff: 1s, 2s, 4s)

## Prerequisites

Before running this example, ensure you have:

1. **SDLC Kit installed**:
   ```bash
   pip install -r requirements.txt
   ```

2. **Environment configured**:
   - Copy `.env.template` to `.env`
   - Set required API keys (e.g., `GOOGLE_GENAI_API_KEY`)

3. **Agent configuration**:
   - Ensure the `analyst-agent` is configured in your agent pool
   - Or use the default agent configuration

## Running the Example

### Method 1: Using the CLI

```bash
# Validate the workflow configuration
python -m agentic_sdlc.cli workflow validate examples/basic-workflow/workflow.yaml

# Run the workflow
python -m agentic_sdlc.cli workflow run examples/basic-workflow/workflow.yaml
```

### Method 2: Using Python Script

Create a Python script to run the workflow:

```python
from agentic_sdlc.orchestration.engine.workflow_engine import WorkflowEngine
from config.validators import ConfigValidator
import yaml

# Load and validate the workflow configuration
with open('examples/basic-workflow/workflow.yaml', 'r') as f:
    workflow_config = yaml.safe_load(f)

validator = ConfigValidator()
result = validator.load_and_validate(
    'examples/basic-workflow/workflow.yaml',
    'config/schemas/workflow.schema.json'
)

if result.is_valid:
    # Initialize and run the workflow
    engine = WorkflowEngine(workflow_config)
    result = engine.execute()
    print(f"Workflow completed with status: {result.status}")
else:
    print(f"Validation failed: {result.errors}")
```

### Method 3: Using the Workflow Test Runner

```bash
# Run using the test runner
python agentic_sdlc/testing/workflow_test_runner.py examples/basic-workflow/workflow.yaml
```

## Expected Output

When you run this workflow, you should see:

1. **Initialization**: Workflow engine starts and loads configuration
2. **Agent Activation**: The analyst agent is initialized
3. **Task Execution**: The analysis task runs
4. **Completion**: Workflow completes with success status

Example output:
```
[INFO] Starting workflow: basic-workflow-example (v1.0.0)
[INFO] Initializing agent: analyst-agent
[INFO] Executing task: analyze-requirements (type: analysis)
[INFO] Task completed successfully
[INFO] Workflow completed with status: SUCCESS
```

## Customization

You can customize this example by:

### 1. Changing the Agent
Edit the `agents` list in `workflow.yaml`:
```yaml
agents:
  - "your-custom-agent"
```

### 2. Modifying Task Configuration
Adjust task parameters:
```yaml
tasks:
  - id: "analyze-requirements"
    type: "analysis"
    config:
      priority: "medium"  # Change priority
      timeout: 600        # Increase timeout
```

### 3. Adding More Tasks
Extend the workflow with additional tasks:
```yaml
tasks:
  - id: "analyze-requirements"
    type: "analysis"
    config:
      priority: "high"
      timeout: 300
    dependencies: []
    
  - id: "validate-analysis"
    type: "validation"
    config:
      priority: "medium"
      timeout: 180
    dependencies: ["analyze-requirements"]  # Runs after analysis
```

### 4. Adjusting Retry Policy
Modify retry behavior:
```yaml
retry_policy:
  max_attempts: 5          # More retry attempts
  backoff_multiplier: 1.5  # Slower backoff
```

## Troubleshooting

### Validation Errors

If you see validation errors:
```bash
# Check the workflow against the schema
python scripts/validate-config.py
```

Common issues:
- **Missing required fields**: Ensure `name` and `version` are present
- **Invalid version format**: Use semantic versioning (e.g., `1.0.0`)
- **Invalid agent IDs**: Check that agent IDs match your configuration

### Execution Errors

If the workflow fails to execute:
- **Check logs**: Look in `logs/` directory for detailed error messages
- **Verify agent configuration**: Ensure agents are properly configured
- **Check API keys**: Verify environment variables are set correctly
- **Review timeout settings**: Increase timeout if tasks are timing out

### Agent Not Found

If you see "Agent not found" errors:
- Ensure the agent is registered in your agent pool
- Check agent configuration files
- Verify agent ID matches exactly (case-sensitive)

## Next Steps

After running this basic example, you can:

1. **Explore Multi-Agent Workflows**: See `examples/multi-agent-workflow/`
2. **Learn About Integrations**: Check `examples/integrations/`
3. **Read the Documentation**: Visit `docs/WORKFLOW_GUIDE.md`
4. **Create Your Own Workflow**: Use this as a template

## Related Examples

- **Multi-Agent Workflow**: `examples/multi-agent-workflow/` - Multiple agents collaborating
- **GitHub Integration**: `examples/integrations/github/` - Integrate with GitHub
- **Slack Integration**: `examples/integrations/slack/` - Send notifications to Slack

## Additional Resources

- [Workflow Schema Documentation](../../config/schemas/README.md)
- [Agent Configuration Guide](../../docs/CONFIGURATION.md)
- [CLI Reference](../../docs/CLI_REFERENCE.md)
- [Troubleshooting Guide](../../docs/TROUBLESHOOTING.md)

## Support

If you encounter issues or have questions:
- Check the [Troubleshooting Guide](../../docs/TROUBLESHOOTING.md)
- Review [GitHub Issues](https://github.com/your-org/sdlc-kit/issues)
- Join our community discussions

---

**Happy workflow building!** 🚀
