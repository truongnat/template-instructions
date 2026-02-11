#!/bin/bash
# Example 2: Running Workflows via CLI
#
# This example demonstrates:
# - Listing available workflows
# - Running a workflow from the command line
# - Monitoring workflow execution
# - Viewing workflow results
#
# Run: bash 02_run_workflow.sh

set -e

echo "============================================================"
echo "Example 2: Running Workflows via CLI"
echo "============================================================"
echo ""

# List available workflows
echo "Listing available workflows..."
echo "-" "40"

cat << 'EOF'
$ agentic workflow list

Available Workflows:
  1. example-workflow
     Description: Example workflow
     Agents: 2
     Steps: 3
     Status: Ready

  2. data-processing
     Description: Process and analyze data
     Agents: 3
     Steps: 5
     Status: Ready

  3. code-review
     Description: Review code quality
     Agents: 2
     Steps: 4
     Status: Ready

Total: 3 workflows available
EOF

echo ""

# Run a workflow
echo "Running a workflow..."
echo "-" "40"

cat << 'EOF'
$ agentic workflow run example-workflow

Running workflow: example-workflow
Starting at: 2024-02-11 10:30:00

Step 1/3: Initialize agents
  ✓ Agent 'analyzer' initialized
  ✓ Agent 'executor' initialized
  Duration: 0.5s

Step 2/3: Execute analysis
  ✓ Analysis completed
  ✓ Generated 5 insights
  Duration: 2.5s

Step 3/3: Execute tasks
  ✓ Tasks completed
  ✓ Processed 10 items
  Duration: 5.2s

Workflow completed successfully!
Total time: 8.2s
Results saved to: results/example-workflow-20240211-103000.json
EOF

echo ""

# Run workflow with parameters
echo "Running workflow with parameters..."
echo "-" "40"

cat << 'EOF'
$ agentic workflow run data-processing --param input_file=data.csv --param output_format=json

Running workflow: data-processing
Starting at: 2024-02-11 10:35:00

Parameters:
  input_file: data.csv
  output_format: json

Step 1/5: Load data
  ✓ Loaded 1000 records from data.csv
  Duration: 0.3s

Step 2/5: Validate data
  ✓ Validation passed
  ✓ 0 errors, 0 warnings
  Duration: 0.2s

Step 3/5: Transform data
  ✓ Applied 5 transformations
  ✓ Generated 1000 output records
  Duration: 1.5s

Step 4/5: Analyze data
  ✓ Analysis completed
  ✓ Generated statistics
  Duration: 2.1s

Step 5/5: Export results
  ✓ Exported to output.json
  ✓ File size: 245 KB
  Duration: 0.4s

Workflow completed successfully!
Total time: 4.5s
Results saved to: results/data-processing-20240211-103500.json
EOF

echo ""

# View workflow status
echo "Viewing workflow status..."
echo "-" "40"

cat << 'EOF'
$ agentic workflow status example-workflow

Workflow Status: example-workflow
Last Run: 2024-02-11 10:30:00
Status: Completed
Duration: 8.2s
Result: Success

Last 5 Runs:
  1. 2024-02-11 10:30:00 - Completed (8.2s)
  2. 2024-02-11 10:15:00 - Completed (8.1s)
  3. 2024-02-11 10:00:00 - Completed (8.3s)
  4. 2024-02-11 09:45:00 - Failed (5.2s)
  5. 2024-02-11 09:30:00 - Completed (8.0s)

Success Rate: 80% (4/5)
Average Duration: 8.0s
EOF

echo ""

# View workflow results
echo "Viewing workflow results..."
echo "-" "40"

cat << 'EOF'
$ agentic workflow results example-workflow

Workflow Results: example-workflow
Run ID: 20240211-103000
Status: Completed
Duration: 8.2s

Step Results:
  1. Initialize agents
     Status: Completed
     Duration: 0.5s
     Output: 2 agents initialized

  2. Execute analysis
     Status: Completed
     Duration: 2.5s
     Output: 5 insights generated

  3. Execute tasks
     Status: Completed
     Duration: 5.2s
     Output: 10 items processed

Summary:
  Total Steps: 3
  Completed: 3
  Failed: 0
  Skipped: 0

Artifacts:
  - results/example-workflow-20240211-103000.json
  - logs/example-workflow-20240211-103000.log
EOF

echo ""

# Common workflow commands
echo "Common Workflow Commands:"
echo "-" "40"

cat << 'EOF'
# List all workflows
agentic workflow list

# Run a workflow
agentic workflow run workflow-name

# Run with parameters
agentic workflow run workflow-name --param key=value

# View workflow status
agentic workflow status workflow-name

# View workflow results
agentic workflow results workflow-name

# Create a new workflow
agentic workflow create --name my-workflow

# Edit a workflow
agentic workflow edit workflow-name

# Delete a workflow
agentic workflow delete workflow-name

# View workflow logs
agentic workflow logs workflow-name

# Cancel running workflow
agentic workflow cancel workflow-name
EOF

echo ""

echo "============================================================"
echo "Example completed successfully!"
echo "============================================================"
