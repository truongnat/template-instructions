---
description: Intelligence - Swarm Routing - Intelligent multi-agent routing and orchestration
---

# Swarm Routing Workflow

This workflow utilizes the Swarm Intelligence system to route complex tasks to the most appropriate specialized agent cluster (Swarm).

## 1. Analyze Request
Analyze the user request to determine the required domain expertise and complexity.

## 2. Select Swarm
Identify the best swarm for the job:
- **Dev Swarm**: For implementation and coding (@DEV, @SA, @TESTER)
- **Product Swarm**: For planning and requirements (@PM, @BA, @UIUX)
- **Ops Swarm**: For deployment and infrastructure (@DEVOPS, @CLOUD, @SECA)
- **Research Swarm**: For investigation and analysis (@RESEARCH, @SA)

## 3. Dispatch Task
Route the task to the selected swarm's primary node manager.

## 4. Aggregation
Collect results from the swarm execution and present them to the user.

## Usage
To use this workflow, provide a complex task that requires coordination:
`/swarm "Design and implement a microservices architecture for the payment gateway"`
