# CLI Usage Examples

This directory contains examples demonstrating how to use the Agentic SDLC command-line interface.

## Examples

### 1. Initializing a Project
**File**: `01_init_project.sh`

Demonstrates:
- Creating a new Agentic SDLC project
- Generating default configuration
- Setting up project structure
- Verifying project initialization

**Run**: `bash 01_init_project.sh`

### 2. Running Workflows via CLI
**File**: `02_run_workflow.sh`

Demonstrates:
- Listing available workflows
- Running a workflow from the command line
- Monitoring workflow execution
- Viewing workflow results

**Run**: `bash 02_run_workflow.sh`

### 3. Configuration Management
**File**: `03_config_management.sh`

Demonstrates:
- Viewing current configuration
- Setting configuration values
- Validating configuration
- Exporting configuration

**Run**: `bash 03_config_management.sh`

## Prerequisites

Install the SDK with CLI support:

```bash
pip install agentic-sdlc[cli]
```

Verify CLI is available:

```bash
agentic --version
```

## Running Examples

Each example script is self-contained and can be run independently:

```bash
bash 01_init_project.sh
bash 02_run_workflow.sh
bash 03_config_management.sh
```

## Common CLI Commands

### Project Initialization

```bash
# Initialize a new project
agentic init

# Initialize with custom name
agentic init --name my-project

# Initialize with custom config
agentic init --config custom-config.yaml
```

### Workflow Management

```bash
# List available workflows
agentic workflow list

# Run a workflow
agentic workflow run workflow-name

# Run with parameters
agentic workflow run workflow-name --param key=value

# View workflow status
agentic workflow status workflow-name
```

### Configuration Management

```bash
# View current configuration
agentic config show

# Set a configuration value
agentic config set log_level DEBUG

# Get a specific value
agentic config get log_level

# Validate configuration
agentic config validate

# Export configuration
agentic config export config.yaml
```

### Agent Management

```bash
# List available agents
agentic agent list

# Create a new agent
agentic agent create --name my-agent --role developer

# View agent details
agentic agent show my-agent

# Delete an agent
agentic agent delete my-agent
```

### Plugin Management

```bash
# List installed plugins
agentic plugin list

# Install a plugin
agentic plugin install plugin-name

# Uninstall a plugin
agentic plugin uninstall plugin-name

# View plugin details
agentic plugin show plugin-name
```

## Output Examples

### Project Initialization

```
$ agentic init
Creating new Agentic SDLC project...
Project name: my-project
Project root: /path/to/my-project

✓ Created project structure
✓ Generated default configuration
✓ Initialized workflows directory
✓ Initialized agents directory
✓ Initialized plugins directory

Project initialized successfully!
Next steps:
  1. Configure your project: agentic config set ...
  2. Create workflows: agentic workflow create ...
  3. Run workflows: agentic workflow run ...
```

### Workflow Execution

```
$ agentic workflow run example-workflow
Running workflow: example-workflow
Starting at: 2024-02-11 10:30:00

Step 1: Initialize agents
  ✓ Agent 'analyzer' initialized
  ✓ Agent 'executor' initialized

Step 2: Execute analysis
  ✓ Analysis completed in 2.5s

Step 3: Execute tasks
  ✓ Tasks completed in 5.2s

Workflow completed successfully!
Total time: 7.7s
Results saved to: results/example-workflow-20240211-103000.json
```

### Configuration Display

```
$ agentic config show
Current Configuration:
  log_level: INFO
  log_file: agentic.log
  project_root: /path/to/project
  
Models:
  openai:
    provider: openai
    model_name: gpt-4
    temperature: 0.7
    max_tokens: 2000
    
Workflows:
  example-workflow:
    name: example-workflow
    description: Example workflow
    agents: 2
    steps: 3
    
Plugins:
  - custom-plugin (v1.0.0)
  - analytics-plugin (v2.1.0)
```

## Troubleshooting

### CLI Not Found

If `agentic` command is not found:

```bash
# Verify installation
pip list | grep agentic-sdlc

# Reinstall with CLI support
pip install --force-reinstall agentic-sdlc[cli]

# Check Python path
which python
```

### Permission Denied

If you get permission errors:

```bash
# Run with sudo (not recommended)
sudo agentic init

# Or fix permissions
chmod +x examples/cli/*.sh
```

### Configuration Errors

If configuration commands fail:

```bash
# Validate configuration
agentic config validate

# Reset to defaults
agentic config reset

# Check configuration file
cat ~/.agentic/config.yaml
```

## Next Steps

- Read the [Getting Started Guide](../../docs/GETTING_STARTED.md)
- Explore the [API Documentation](../../docs/api/)
- Learn about [Plugin Development](../../docs/PLUGIN_DEVELOPMENT.md)
- Check the [Architecture Guide](../../docs/architecture/)
