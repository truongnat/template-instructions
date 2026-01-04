---
description: [Support] Pre-flight workflow checker - Run BEFORE any task
---
# Pre-Flight Workflow
> **MANDATORY:** This workflow MUST be executed conceptually before ANY task.
## Step 1: Identify Task Type
Analyze user request and determine:
- Is this a new feature? -> Use /orchestrator
- Is this a bug fix? -> Use /cycle
- Is this investigation? -> Use /explore
- Is this emergency? -> Use /emergency
## Step 2: Read Workflow File
`bash
# For /orchestrator tasks
cat .agent/workflows/orchestrator.md
# For /cycle tasks  
cat .agent/workflows/cycle.md
`
## Step 3: Search Knowledge Base
`bash
grep -r "relevant_keyword" .agent/knowledge-base/
`
## Step 4: Check Brain State
`bash
python tools/brain/brain_cli.py status
`
## Step 5: Identify Required Roles
Based on task type, activate roles:
- @PM for planning
- @SA for architecture  
- @DEV for implementation
- @TESTER for testing
## Step 6: Proceed with Workflow
Now follow the identified workflow file step-by-step.
#preflight #mandatory #enforcement
