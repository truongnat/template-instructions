# Quick Reference Architecture

## One-Page System Overview

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         AGENTIC SDLC ARCHITECTURE                           │
│                              Version 3.0.0                                  │
└─────────────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────────────┐
│ USER INTERFACE LAYER                                                        │
├─────────────────────────────────────────────────────────────────────────────┤
│  CLI Commands  │  Python SDK  │  REST API  │  Webhooks  │  Streaming       │
└─────────────────────────────────────────────────────────────────────────────┘
                                    ▲
                                    │
┌─────────────────────────────────────────────────────────────────────────────┐
│ CORE BUSINESS LOGIC LAYER                                                   │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  ┌──────────────────────┐  ┌──────────────────────┐  ┌──────────────────┐ │
│  │  ORCHESTRATION       │  │  INFRASTRUCTURE      │  │  INTELLIGENCE    │ │
│  ├──────────────────────┤  ├──────────────────────┤  ├──────────────────┤ │
│  │ • Agent Registry     │  │ • Workflow Engine    │  │ • Learning       │ │
│  │ • Model Client       │  │ • Execution Engine   │  │ • Monitoring     │ │
│  │ • Workflow Builder   │  │ • Lifecycle Manager  │  │ • Reasoning      │ │
│  │ • Coordinator        │  │ • Bridge Registry    │  │ • Collaboration  │ │
│  │ • LLM Integration    │  │ • Plugin Registry    │  │ • Pattern Store  │ │
│  └──────────────────────┘  └──────────────────────┘  └──────────────────┘ │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
                                    ▲
                                    │
┌─────────────────────────────────────────────────────────────────────────────┐
│ CROSS-CUTTING CONCERNS LAYER                                                │
├─────────────────────────────────────────────────────────────────────────────┤
│  Config Management  │  Logging  │  Error Handling  │  Resource Management  │
└─────────────────────────────────────────────────────────────────────────────┘
                                    ▲
                                    │
┌─────────────────────────────────────────────────────────────────────────────┐
│ EXTERNAL INTEGRATIONS LAYER                                                 │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  ┌──────────────────┐  ┌──────────────────┐  ┌──────────────────────────┐ │
│  │  LLM PROVIDERS   │  │  DATA STORAGE    │  │  EXTERNAL SERVICES       │ │
│  ├──────────────────┤  ├──────────────────┤  ├──────────────────────────┤ │
│  │ • OpenAI (GPT)   │  │ • Neo4j (Graph)  │  │ • GitHub                 │ │
│  │ • Anthropic      │  │ • PostgreSQL     │  │ • Jira                   │ │
│  │ • Ollama (Local) │  │ • Redis (Cache)  │  │ • Slack                  │ │
│  │ • Custom         │  │ • S3/GCS (Files) │  │ • Jenkins                │ │
│  └──────────────────┘  └──────────────────┘  └──────────────────────────┘ │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

## Component Interaction Matrix

```
┌──────────────────────────────────────────────────────────────────────────────┐
│                    COMPONENT INTERACTION MATRIX                              │
├──────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  ORCHESTRATION                                                               │
│  ├─ Agent Registry ◄──────────────────────────────────────────────────────┐ │
│  │  └─ Manages agent lifecycle, registration, lookup                     │ │
│  │                                                                        │ │
│  ├─ Model Client ◄─────────────────────────────────────────────────────┐ │ │
│  │  └─ Abstracts LLM provider differences, handles API calls           │ │ │
│  │                                                                      │ │ │
│  ├─ Workflow Builder ◄──────────────────────────────────────────────┐ │ │ │
│  │  └─ Defines workflows, creates execution plans                   │ │ │ │
│  │                                                                  │ │ │ │
│  └─ Coordinator ◄────────────────────────────────────────────────┐ │ │ │ │
│     └─ Synchronizes agents, manages state, aggregates results   │ │ │ │ │
│                                                                  │ │ │ │ │
│  INFRASTRUCTURE                                                  │ │ │ │ │
│  ├─ Workflow Engine ◄──────────────────────────────────────────┐ │ │ │ │
│  │  └─ Executes workflow steps, manages dependencies           │ │ │ │ │
│  │                                                              │ │ │ │ │
│  ├─ Execution Engine ◄────────────────────────────────────────┐ │ │ │ │
│  │  └─ Dispatches tasks, monitors progress                    │ │ │ │ │
│  │                                                              │ │ │ │ │
│  ├─ Lifecycle Manager ◄──────────────────────────────────────┐ │ │ │ │
│  │  └─ Initializes, configures, cleans up components         │ │ │ │ │
│  │                                                              │ │ │ │ │
│  └─ Bridge Registry ◄────────────────────────────────────────┐ │ │ │ │
│     └─ Integrates external systems, manages adapters         │ │ │ │ │
│                                                                │ │ │ │ │
│  INTELLIGENCE                                                  │ │ │ │ │
│  ├─ Learning Engine ◄──────────────────────────────────────┐ │ │ │ │
│  │  └─ Extracts patterns, stores knowledge                 │ │ │ │ │
│  │                                                          │ │ │ │ │
│  ├─ Monitor ◄────────────────────────────────────────────┐ │ │ │ │
│  │  └─ Tracks metrics, alerts on anomalies              │ │ │ │ │
│  │                                                          │ │ │ │ │
│  ├─ Reasoner ◄──────────────────────────────────────────┐ │ │ │ │
│  │  └─ Analyzes patterns, makes decisions               │ │ │ │ │
│  │                                                          │ │ │ │ │
│  └─ Collaborator ◄────────────────────────────────────┐ │ │ │ │
│     └─ Coordinates agents, resolves conflicts         │ │ │ │ │
│                                                          │ │ │ │ │
│  CORE                                                    │ │ │ │ │
│  ├─ Config Manager ◄──────────────────────────────────┐ │ │ │ │
│  │  └─ Loads, validates, distributes configuration    │ │ │ │ │
│  │                                                      │ │ │ │ │
│  ├─ Logger ◄────────────────────────────────────────┐ │ │ │ │
│  │  └─ Logs events, tracks execution                │ │ │ │ │
│  │                                                      │ │ │ │ │
│  └─ Exception Handler ◄────────────────────────────┐ │ │ │ │
│     └─ Handles errors, provides context            │ │ │ │ │
│                                                      │ │ │ │ │
│  All components receive configuration ──────────────┘ │ │ │ │
│  All components publish events ──────────────────────┘ │ │ │
│  All components use shared state ─────────────────────┘ │ │
│  All components integrate with external services ──────┘ │
│                                                          │
└──────────────────────────────────────────────────────────────────────────────┘
```

## Data Flow Diagram

```
┌──────────────────────────────────────────────────────────────────────────────┐
│                         DATA FLOW OVERVIEW                                   │
└──────────────────────────────────────────────────────────────────────────────┘

INPUT
  │
  ├─ User Request (CLI/API)
  ├─ Configuration (File/Env)
  └─ Workflow Definition
       │
       ▼
PROCESSING
  │
  ├─ Config Validation (Core)
  ├─ Workflow Planning (Orchestration)
  ├─ Agent Assignment (Orchestration)
  ├─ Task Distribution (Infrastructure)
  ├─ LLM Calls (Model Client)
  ├─ Result Aggregation (Coordinator)
  ├─ Pattern Learning (Intelligence)
  └─ Metrics Recording (Monitor)
       │
       ▼
OUTPUT
  │
  ├─ Workflow Results
  ├─ Execution Metrics
  ├─ Learned Patterns
  ├─ Recommendations
  └─ Status Updates
       │
       ▼
STORAGE
  │
  ├─ Results → Database
  ├─ Patterns → Knowledge Base
  ├─ Metrics → Monitoring System
  └─ Logs → Log Storage
```

## Execution Timeline

```
┌──────────────────────────────────────────────────────────────────────────────┐
│                      WORKFLOW EXECUTION TIMELINE                             │
└──────────────────────────────────────────────────────────────────────────────┘

T0: INITIALIZATION
    ├─ Load configuration
    ├─ Validate workflow
    └─ Initialize components

T1: PLANNING
    ├─ Analyze dependencies
    ├─ Create execution plan
    └─ Assign agents to tasks

T2: EXECUTION (Parallel)
    ├─ Task 1 ─────────────────────────────────────┐
    │  ├─ Prepare context                          │
    │  ├─ Call LLM                                 │
    │  └─ Process result                           │
    │                                              │
    ├─ Task 2 ─────────────────────────────────────┤ (Concurrent)
    │  ├─ Prepare context                          │
    │  ├─ Call LLM                                 │
    │  └─ Process result                           │
    │                                              │
    └─ Task N ─────────────────────────────────────┘

T3: AGGREGATION
    ├─ Collect all results
    ├─ Merge outputs
    └─ Validate combined result

T4: LEARNING
    ├─ Extract patterns
    ├─ Update knowledge base
    └─ Generate recommendations

T5: COMPLETION
    ├─ Record metrics
    ├─ Format response
    └─ Return to user
```

## Module Dependencies

```
┌──────────────────────────────────────────────────────────────────────────────┐
│                        MODULE DEPENDENCIES                                   │
└──────────────────────────────────────────────────────────────────────────────┘

                              ┌─────────────┐
                              │   CLI       │
                              └──────┬──────┘
                                     │
                                     ▼
                        ┌────────────────────────┐
                        │  Public API (__init__) │
                        └──────────┬─────────────┘
                                   │
                    ┌──────────────┼──────────────┐
                    │              │              │
                    ▼              ▼              ▼
            ┌────────────┐  ┌────────────┐  ┌────────────┐
            │   CORE     │  │ORCHESTRATION
            │            │  │            │  │INTELLIGENCE│
            │ • Config   │  │ • Agents   │  │            │
            │ • Logging  │  │ • Models   │  │ • Learning │
            │ • Errors   │  │ • Workflows│  │ • Monitor  │
            │ • Types    │  │ • Coord.   │  │ • Reasoning│
            └────────────┘  └────────────┘  └────────────┘
                ▲                ▲                ▲
                │                │                │
                └────────────────┼────────────────┘
                                 │
                                 ▼
                        ┌────────────────────────┐
                        │  INFRASTRUCTURE        │
                        │                        │
                        │ • Automation           │
                        │ • Bridge               │
                        │ • Engine               │
                        │ • Lifecycle            │
                        └──────────┬─────────────┘
                                   │
                    ┌──────────────┼──────────────┐
                    │              │              │
                    ▼              ▼              ▼
            ┌────────────┐  ┌────────────┐  ┌────────────┐
            │  PLUGINS   │  │  EXTERNAL  │  │  STORAGE   │
            │            │  │  SERVICES  │  │            │
            │ • Registry │  │            │  │ • Neo4j    │
            │ • Loader   │  │ • Docker   │  │ • SQL      │
            │ • Base     │  │ • APIs     │  │ • Cache    │
            └────────────┘  └────────────┘  └────────────┘
```

## State Machine

```
┌──────────────────────────────────────────────────────────────────────────────┐
│                      WORKFLOW STATE MACHINE                                  │
└──────────────────────────────────────────────────────────────────────────────┘

                    ┌─────────────────────┐
                    │  INITIALIZED        │
                    │  (Config loaded)    │
                    └──────────┬──────────┘
                               │
                               ▼
                    ┌─────────────────────┐
                    │  PLANNING           │
                    │  (Exec plan built)  │
                    └──────────┬──────────┘
                               │
                               ▼
                    ┌─────────────────────┐
                    │  EXECUTING          │
                    │  (Tasks running)    │
                    └──────────┬──────────┘
                               │
                    ┌──────────┴──────────┐
                    │                     │
                    ▼                     ▼
            ┌────────────────┐    ┌────────────────┐
            │  AGGREGATING   │    │  FAILED        │
            │  (Results)     │    │  (Error state) │
            └────────┬───────┘    └────────┬───────┘
                     │                     │
                     ▼                     ▼
            ┌────────────────┐    ┌────────────────┐
            │  LEARNING      │    │  CLEANUP       │
            │  (Patterns)    │    │  (Rollback)    │
            └────────┬───────┘    └────────┬───────┘
                     │                     │
                     ▼                     ▼
            ┌────────────────┐    ┌────────────────┐
            │  COMPLETED     │    │  ABORTED       │
            │  (Success)     │    │  (Terminated)  │
            └────────────────┘    └────────────────┘
```

## Configuration Hierarchy

```
┌──────────────────────────────────────────────────────────────────────────────┐
│                    CONFIGURATION HIERARCHY                                   │
└──────────────────────────────────────────────────────────────────────────────┘

Priority (Highest to Lowest):
  1. Programmatic API calls
  2. Environment variables (AGENTIC_SDLC_*)
  3. Configuration file (config.yaml / config.json)
  4. Default values

Configuration Structure:
  ├─ project_root
  ├─ log_level
  ├─ log_file
  ├─ models
  │  ├─ openai
  │  │  ├─ api_key
  │  │  ├─ model
  │  │  └─ temperature
  │  ├─ anthropic
  │  │  ├─ api_key
  │  │  ├─ model
  │  │  └─ max_tokens
  │  └─ custom
  │     └─ ...
  ├─ workflows
  │  ├─ workflow_name
  │  │  ├─ steps
  │  │  ├─ timeout
  │  │  └─ metadata
  │  └─ ...
  ├─ plugins
  │  ├─ plugin_name
  │  │  ├─ enabled
  │  │  └─ config
  │  └─ ...
  └─ defaults_dir
```

## Error Handling Strategy

```
┌──────────────────────────────────────────────────────────────────────────────┐
│                      ERROR HANDLING STRATEGY                                 │
└──────────────────────────────────────────────────────────────────────────────┘

Error Detection
  │
  ├─ Configuration Errors
  │  └─ Validation Error → Log → Return to user
  │
  ├─ Agent Errors
  │  ├─ Retryable → Retry with backoff
  │  ├─ Timeout → Escalate or abort
  │  └─ Fatal → Abort workflow
  │
  ├─ Workflow Errors
  │  ├─ Step failure → Check dependencies
  │  ├─ Dependency failure → Skip or abort
  │  └─ Timeout → Escalate
  │
  ├─ Model Errors
  │  ├─ API error → Retry or fallback
  │  ├─ Rate limit → Backoff
  │  └─ Invalid response → Log and retry
  │
  └─ System Errors
     ├─ Resource exhaustion → Queue or reject
     ├─ Database error → Retry or failover
     └─ External service down → Fallback or queue

Error Response
  ├─ Log error with context
  ├─ Update metrics
  ├─ Notify monitoring system
  ├─ Attempt recovery
  └─ Return error to user
```

---

**Quick Links:**
- [Full System Architecture](system_architecture.md)
- [Workflow Execution Flow](workflow_flow.md)
- [Component Interactions](component_interactions.md)
- [Data Models](data_models.md)
- [Deployment & Integration](deployment_integration.md)
