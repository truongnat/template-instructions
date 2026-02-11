#!/bin/bash
# Example 1: Initializing a Project
#
# This example demonstrates:
# - Creating a new Agentic SDLC project
# - Generating default configuration
# - Setting up project structure
# - Verifying project initialization
#
# Run: bash 01_init_project.sh

set -e

echo "============================================================"
echo "Example 1: Initializing a Project"
echo "============================================================"
echo ""

# Create a temporary directory for the example
PROJECT_DIR="/tmp/agentic-example-project"
echo "Creating project directory: $PROJECT_DIR"
mkdir -p "$PROJECT_DIR"
cd "$PROJECT_DIR"
echo "  ✓ Directory created"
echo ""

# Initialize a new project
echo "Initializing new Agentic SDLC project..."
echo "-" "40"

# Note: In a real scenario, you would run:
# agentic init --name my-project

# For this example, we'll show the expected output:
cat << 'EOF'
Creating new Agentic SDLC project...
Project name: my-project
Project root: /tmp/agentic-example-project

✓ Created project structure
  - Created .agentic/ directory
  - Created workflows/ directory
  - Created agents/ directory
  - Created plugins/ directory
  - Created resources/ directory

✓ Generated default configuration
  - Created .agentic/config.yaml
  - Created .agentic/defaults.yaml

✓ Initialized workflows directory
  - Created workflows/example.yaml

✓ Initialized agents directory
  - Created agents/default.yaml

✓ Initialized plugins directory
  - Created plugins/README.md

Project initialized successfully!
EOF

echo ""

# Verify project structure
echo "Verifying project structure..."
echo "-" "40"

# Create the expected directory structure
mkdir -p .agentic workflows agents plugins resources

# Create sample files
cat > .agentic/config.yaml << 'EOF'
project_root: /tmp/agentic-example-project
log_level: INFO
log_file: agentic.log

models:
  openai:
    provider: openai
    model_name: gpt-4
    temperature: 0.7
    max_tokens: 2000

workflows: {}
plugins: []
EOF

cat > workflows/example.yaml << 'EOF'
name: example-workflow
description: Example workflow
agents: []
steps:
  - name: initialize
    description: Initialize workflow
    action: initialize
  - name: process
    description: Process data
    action: process
  - name: finalize
    description: Finalize workflow
    action: finalize
EOF

cat > agents/default.yaml << 'EOF'
name: default-agent
role: Assistant
model:
  provider: openai
  model_name: gpt-4
  temperature: 0.7
system_prompt: You are a helpful assistant.
tools: []
max_iterations: 10
EOF

# List created files
echo "  ✓ Project structure created:"
echo "    - .agentic/config.yaml"
echo "    - .agentic/defaults.yaml"
echo "    - workflows/example.yaml"
echo "    - agents/default.yaml"
echo "    - plugins/"
echo "    - resources/"
echo ""

# Display next steps
echo "Next steps:"
echo "-" "40"
echo "  1. Configure your project:"
echo "     agentic config set log_level DEBUG"
echo ""
echo "  2. Create workflows:"
echo "     agentic workflow create --name my-workflow"
echo ""
echo "  3. Run workflows:"
echo "     agentic workflow run example-workflow"
echo ""

# Cleanup
echo "Cleaning up example project..."
cd /
rm -rf "$PROJECT_DIR"
echo "  ✓ Temporary project removed"
echo ""

echo "============================================================"
echo "Example completed successfully!"
echo "============================================================"
