---
description: Process - Concurrent Execution - Execute multiple agent roles in parallel
---

# Concurrent Execution Workflow

This workflow enables the parallel execution of multiple AI agents to speed up diverse tasks.

## 1. Define Parallel Tracks
Identify independent units of work that can be executed simultaneously.

## 2. Assign Roles
Assign each track to a specific agent role:
- Track A: @SA (Architecture Design)
- Track B: @UIUX (Interface Mockups)
- Track C: @PO (User Stories)

## 3. Execute concurrently
// turbo-all
Launch the agents in parallel.

## 4. Synchronize
Wait for all tracks to complete.

## 5. Merge Results
Combine the outputs from all agents into a unified report or artifact set.

## Usage
`/concurrent "Design the login page (@UIUX) while documenting requirements (@PO) and planning the API schema (@SA)"`
