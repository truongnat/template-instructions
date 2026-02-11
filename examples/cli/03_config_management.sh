#!/bin/bash
# Example 3: Configuration Management
#
# This example demonstrates:
# - Viewing current configuration
# - Setting configuration values
# - Validating configuration
# - Exporting configuration
#
# Run: bash 03_config_management.sh

set -e

echo "============================================================"
echo "Example 3: Configuration Management"
echo "============================================================"
echo ""

# View current configuration
echo "Viewing current configuration..."
echo "-" "40"

cat << 'EOF'
$ agentic config show

Current Configuration:
  project_root: /path/to/project
  log_level: INFO
  log_file: agentic.log

Models:
  openai:
    provider: openai
    model_name: gpt-4
    temperature: 0.7
    max_tokens: 2000
    timeout: 30

  anthropic:
    provider: anthropic
    model_name: claude-3-opus
    temperature: 0.5
    max_tokens: 4000
    timeout: 60

Workflows:
  example-workflow:
    name: example-workflow
    description: Example workflow
    agents: 2
    steps: 3

Plugins:
  - analytics-plugin (v1.0.0)
  - logging-plugin (v1.0.0)

Defaults Directory: ~/.agentic/defaults
EOF

echo ""

# Set configuration values
echo "Setting configuration values..."
echo "-" "40"

cat << 'EOF'
$ agentic config set log_level DEBUG
✓ Set log_level to DEBUG

$ agentic config set project_root /new/project/path
✓ Set project_root to /new/project/path

$ agentic config set models.openai.temperature 0.9
✓ Set models.openai.temperature to 0.9

$ agentic config set models.openai.max_tokens 4000
✓ Set models.openai.max_tokens to 4000
EOF

echo ""

# Get specific configuration values
echo "Getting specific configuration values..."
echo "-" "40"

cat << 'EOF'
$ agentic config get log_level
DEBUG

$ agentic config get project_root
/new/project/path

$ agentic config get models.openai.model_name
gpt-4

$ agentic config get models.openai.temperature
0.9
EOF

echo ""

# Validate configuration
echo "Validating configuration..."
echo "-" "40"

cat << 'EOF'
$ agentic config validate

Validating configuration...
  ✓ project_root is valid
  ✓ log_level is valid (DEBUG)
  ✓ log_file is valid
  ✓ models.openai is valid
  ✓ models.anthropic is valid
  ✓ workflows are valid
  ✓ plugins are valid

Configuration is valid!
EOF

echo ""

# Export configuration
echo "Exporting configuration..."
echo "-" "40"

cat << 'EOF'
$ agentic config export config-backup.yaml
✓ Configuration exported to config-backup.yaml

$ agentic config export config-backup.json
✓ Configuration exported to config-backup.json
EOF

echo ""

# Import configuration
echo "Importing configuration..."
echo "-" "40"

cat << 'EOF'
$ agentic config import config-backup.yaml
Importing configuration from config-backup.yaml...
  ✓ Loaded 15 configuration items
  ✓ Validated all items
  ✓ Applied configuration

Configuration imported successfully!
EOF

echo ""

# Reset configuration
echo "Resetting configuration..."
echo "-" "40"

cat << 'EOF'
$ agentic config reset
Are you sure you want to reset configuration to defaults? (y/n) y
✓ Configuration reset to defaults
EOF

echo ""

# View configuration file
echo "Viewing configuration file..."
echo "-" "40"

cat << 'EOF'
$ agentic config file
Configuration file: ~/.agentic/config.yaml

$ cat ~/.agentic/config.yaml
project_root: /path/to/project
log_level: DEBUG
log_file: agentic.log

models:
  openai:
    provider: openai
    model_name: gpt-4
    temperature: 0.9
    max_tokens: 4000
    timeout: 30

  anthropic:
    provider: anthropic
    model_name: claude-3-opus
    temperature: 0.5
    max_tokens: 4000
    timeout: 60

workflows: {}
plugins: []
EOF

echo ""

# Common configuration commands
echo "Common Configuration Commands:"
echo "-" "40"

cat << 'EOF'
# View all configuration
agentic config show

# Get a specific value
agentic config get key

# Set a value
agentic config set key value

# Set nested value
agentic config set models.openai.temperature 0.8

# Validate configuration
agentic config validate

# Export configuration
agentic config export config.yaml

# Import configuration
agentic config import config.yaml

# Reset to defaults
agentic config reset

# Show configuration file path
agentic config file

# Edit configuration in editor
agentic config edit

# List all configuration keys
agentic config list

# Search configuration
agentic config search log
EOF

echo ""

# Environment variables
echo "Using Environment Variables:"
echo "-" "40"

cat << 'EOF'
Configuration can also be set via environment variables with AGENTIC_ prefix:

$ export AGENTIC_LOG_LEVEL=DEBUG
$ export AGENTIC_PROJECT_ROOT=/path/to/project
$ export AGENTIC_MODELS_OPENAI_TEMPERATURE=0.9

$ agentic config show
Current Configuration:
  log_level: DEBUG (from environment)
  project_root: /path/to/project (from environment)
  models.openai.temperature: 0.9 (from environment)
EOF

echo ""

# Configuration precedence
echo "Configuration Precedence (highest to lowest):"
echo "-" "40"

cat << 'EOF'
1. Command-line arguments (agentic config set ...)
2. Environment variables (AGENTIC_* prefix)
3. Configuration file (~/.agentic/config.yaml)
4. Default values (built-in)

Later values override earlier values.
EOF

echo ""

echo "============================================================"
echo "Example completed successfully!"
echo "============================================================"
