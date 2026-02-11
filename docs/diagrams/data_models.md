# Data Models and Class Hierarchy

## Core Data Models

```
┌─────────────────────────────────────────────────────────────────┐
│                    CONFIGURATION MODELS                         │
└─────────────────────────────────────────────────────────────────┘

                    ┌─────────────────────┐
                    │  SDKConfig          │
                    │  (Root Config)      │
                    ├─────────────────────┤
                    │ • project_root      │
                    │ • log_level         │
                    │ • log_file          │
                    │ • models: {}        │
                    │ • workflows: {}     │
                    │ • plugins: []       │
                    │ • defaults_dir      │
                    └──────────┬──────────┘
                               │
        ┌──────────────────────┼──────────────────────┐
        │                      │                      │
        ▼                      ▼                      ▼
    ┌────────────┐      ┌────────────┐      ┌────────────┐
    │ ModelConfig│      │ AgentConfig│      │WorkflowConfig
    │            │      │            │      │            │
    │ • name     │      │ • name     │      │ • name     │
    │ • provider │      │ • role     │      │ • steps    │
    │ • api_key  │      │ • model    │      │ • timeout  │
    │ • params   │      │ • tools    │      │ • metadata │
    │ • settings │      │ • settings │      │ • config   │
    └────────────┘      └────────────┘      └────────────┘
```

## Agent and Workflow Models

```
┌─────────────────────────────────────────────────────────────────┐
│                    AGENT HIERARCHY                              │
└─────────────────────────────────────────────────────────────────┘

                    ┌─────────────────────┐
                    │  Agent              │
                    │  (Dataclass)        │
                    ├─────────────────────┤
                    │ • id: str           │
                    │ • name: str         │
                    │ • role: str         │
                    │ • model_name: str   │
                    │ • system_prompt: str│
                    │ • tools: List[str]  │
                    │ • max_iterations: int
                    │ • metadata: Dict    │
                    └──────────┬──────────┘
                               │
                    ┌──────────┴──────────┐
                    │                     │
                    ▼                     ▼
            ┌────────────────┐    ┌────────────────┐
            │  Agent State   │    │  Agent Config  │
            │  (Runtime)     │    │  (Definition)  │
            │                │    │                │
            │ • status       │    │ • name         │
            │ • current_task │    │ • role         │
            │ • iterations   │    │ • model        │
            │ • results      │    │ • tools        │
            │ • errors       │    │ • settings     │
            └────────────────┘    └────────────────┘

┌─────────────────────────────────────────────────────────────────┐
│                    WORKFLOW HIERARCHY                           │
└─────────────────────────────────────────────────────────────────┘

                    ┌─────────────────────┐
                    │  Workflow           │
                    │  (Dataclass)        │
                    ├─────────────────────┤
                    │ • id: str           │
                    │ • name: str         │
                    │ • description: str  │
                    │ • steps: List[Step] │
                    │ • timeout: int      │
                    │ • metadata: Dict    │
                    └──────────┬──────────┘
                               │
                    ┌──────────┴──────────┐
                    │                     │
                    ▼                     ▼
            ┌────────────────┐    ┌────────────────┐
            │  WorkflowStep  │    │  Workflow      │
            │  (Dataclass)   │    │  Execution     │
            │                │    │  (Runtime)     │
            │ • name: str    │    │                │
            │ • agent_id: str│    │ • status       │
            │ • description  │    │ • current_step│
            │ • input_keys   │    │ • results      │
            │ • output_keys  │    │ • errors       │
            │ • metadata     │    │ • start_time   │
            └────────────────┘    │ • end_time     │
                                  └────────────────┘
```

## Execution Models

```
┌─────────────────────────────────────────────────────────────────┐
│                    EXECUTION MODELS                             │
└─────────────────────────────────────────────────────────────────┘

                    ┌─────────────────────┐
                    │  ExecutionPlan      │
                    ├─────────────────────┤
                    │ • workflow_id       │
                    │ • steps: List[Step] │
                    │ • dependencies: {}  │
                    │ • parallel_groups   │
                    │ • estimated_time    │
                    └──────────┬──────────┘
                               │
        ┌──────────────────────┼──────────────────────┐
        │                      │                      │
        ▼                      ▼                      ▼
    ┌────────────┐      ┌────────────┐      ┌────────────┐
    │ Task       │      │ TaskResult │      │ TaskError  │
    │            │      │            │      │            │
    │ • id       │      │ • task_id  │      │ • task_id  │
    │ • name     │      │ • status   │      │ • error    │
    │ • agent_id │      │ • output   │      │ • type     │
    │ • input    │      │ • duration │      │ • context  │
    │ • status   │      │ • timestamp│      │ • timestamp│
    │ • deps     │      │ • metadata │      │ • metadata │
    └────────────┘      └────────────┘      └────────────┘
```

## Learning Models

```
┌─────────────────────────────────────────────────────────────────┐
│                    LEARNING MODELS                              │
└─────────────────────────────────────────────────────────────────┘

                    ┌─────────────────────┐
                    │  Pattern            │
                    │  (Dataclass)        │
                    ├─────────────────────┤
                    │ • pattern_type      │
                    │ • description       │
                    │ • context: Dict     │
                    │ • timestamp         │
                    │ • frequency: int    │
                    └──────────┬──────────┘
                               │
        ┌──────────────────────┼──────────────────────┐
        │                      │                      │
        ▼                      ▼                      ▼
    ┌────────────┐      ┌────────────┐      ┌────────────┐
    │ Error      │      │ Success    │      │ Task       │
    │ Pattern    │      │ Pattern    │      │ Pattern    │
    │            │      │            │      │            │
    │ • error    │      │ • strategy │      │ • task_type│
    │ • cause    │      │ • result   │      │ • approach │
    │ • solution │      │ • metrics  │      │ • tools    │
    │ • context  │      │ • context  │      │ • context  │
    └────────────┘      └────────────┘      └────────────┘

                    ┌─────────────────────┐
                    │  LearningEvent      │
                    │  (Dataclass)        │
                    ├─────────────────────┤
                    │ • event_type        │
                    │ • description       │
                    │ • context: Dict     │
                    │ • timestamp         │
                    └─────────────────────┘
```

## Plugin Models

```
┌─────────────────────────────────────────────────────────────────┐
│                    PLUGIN MODELS                                │
└─────────────────────────────────────────────────────────────────┘

                    ┌─────────────────────┐
                    │  PluginMetadata     │
                    │  (Pydantic Model)   │
                    ├─────────────────────┤
                    │ • name: str         │
                    │ • version: str      │
                    │ • author: str       │
                    │ • description: str  │
                    │ • dependencies: []  │
                    │ • entry_point: str  │
                    │ • config_schema: {} │
                    └──────────┬──────────┘
                               │
                               ▼
                    ┌─────────────────────┐
                    │  Plugin             │
                    │  (Abstract Base)    │
                    ├─────────────────────┤
                    │ • name: str         │
                    │ • version: str      │
                    │                     │
                    │ Methods:            │
                    │ • initialize()      │
                    │ • shutdown()        │
                    │ • get_hooks()       │
                    │ • validate_config() │
                    └──────────┬──────────┘
                               │
        ┌──────────────────────┼──────────────────────┐
        │                      │                      │
        ▼                      ▼                      ▼
    ┌────────────┐      ┌────────────┐      ┌────────────┐
    │ Custom     │      │ Integration│      │ Extension  │
    │ Plugin 1   │      │ Plugin     │      │ Plugin     │
    │            │      │            │      │            │
    │ • Custom   │      │ • Bridges  │      │ • Extends  │
    │   logic    │      │   external │      │   core     │
    │ • Hooks    │      │   systems  │      │   features │
    │ • Config   │      │ • Config   │      │ • Config   │
    └────────────┘      └────────────┘      └────────────┘
```

## Exception Hierarchy

```
┌─────────────────────────────────────────────────────────────────┐
│                    EXCEPTION HIERARCHY                          │
└─────────────────────────────────────────────────────────────────┘

                    ┌─────────────────────┐
                    │  Exception          │
                    │  (Python Built-in)  │
                    └──────────┬──────────┘
                               │
                               ▼
                    ┌─────────────────────┐
                    │  AgenticSDLCError   │
                    │  (Base Exception)   │
                    ├─────────────────────┤
                    │ • message: str      │
                    │ • context: Dict     │
                    │ • cause: Exception  │
                    └──────────┬──────────┘
                               │
        ┌──────────────────────┼──────────────────────┐
        │                      │                      │
        ▼                      ▼                      ▼
    ┌────────────┐      ┌────────────┐      ┌────────────┐
    │ Configuration
    │ Error      │      │ Agent      │      │ Workflow   │
    │            │      │ Error      │      │ Error      │
    │ • Invalid  │      │            │      │            │
    │   config   │      │ • Invalid  │      │ • Invalid  │
    │ • Missing  │      │   config   │      │   workflow │
    │   file     │      │ • Execution│      │ • Execution│
    │ • Parse    │      │   failed   │      │   failed   │
    │   error    │      │ • Timeout  │      │ • Timeout  │
    └────────────┘      └────────────┘      └────────────┘
        │                      │                      │
        ▼                      ▼                      ▼
    ┌────────────┐      ┌────────────┐      ┌────────────┐
    │ Validation │      │ Model      │      │ Plugin     │
    │ Error      │      │ Error      │      │ Error      │
    │            │      │            │      │            │
    │ • Type     │      │ • API call │      │ • Load     │
    │   mismatch │      │   failed   │      │   failed   │
    │ • Missing  │      │ • Invalid  │      │ • Invalid  │
    │   field    │      │   response │      │   config   │
    │ • Invalid  │      │ • Token    │      │ • Execution│
    │   value    │      │   exceeded │      │   failed   │
    └────────────┘      └────────────┘      └────────────┘
```

## Type System

```
┌─────────────────────────────────────────────────────────────────┐
│                    TYPE DEFINITIONS                             │
└─────────────────────────────────────────────────────────────────┘

Core Types:
├── AgentId = str (UUID)
├── WorkflowId = str (UUID)
├── TaskId = str (UUID)
├── PatternId = str (UUID)
│
Configuration Types:
├── ModelConfig = Dict[str, Any]
├── AgentConfig = Dict[str, Any]
├── WorkflowConfig = Dict[str, Any]
├── PluginConfig = Dict[str, Any]
│
Execution Types:
├── ExecutionStatus = Enum(PENDING, RUNNING, COMPLETED, FAILED, TIMEOUT)
├── TaskStatus = Enum(PENDING, RUNNING, COMPLETED, FAILED, SKIPPED)
├── AgentStatus = Enum(IDLE, BUSY, ERROR, SHUTDOWN)
│
Learning Types:
├── PatternType = Enum(ERROR, SUCCESS, TASK)
├── PatternFrequency = int
├── PatternContext = Dict[str, Any]
│
Result Types:
├── TaskResult = Dict[str, Any]
├── WorkflowResult = Dict[str, Any]
├── ExecutionMetrics = Dict[str, Any]
│
Error Types:
├── ErrorType = Enum(CONFIGURATION, VALIDATION, EXECUTION, TIMEOUT, PLUGIN)
├── ErrorContext = Dict[str, Any]
├── ErrorSeverity = Enum(INFO, WARNING, ERROR, CRITICAL)
```

## Relationship Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                    MODEL RELATIONSHIPS                          │
└─────────────────────────────────────────────────────────────────┘

                    ┌─────────────────────┐
                    │  SDKConfig          │
                    └──────────┬──────────┘
                               │
                ┌──────────────┼──────────────┐
                │              │              │
                ▼              ▼              ▼
        ┌────────────┐  ┌────────────┐  ┌────────────┐
        │ ModelConfig│  │ AgentConfig│  │WorkflowConfig
        └────────────┘  └────────────┘  └────────────┘
                │              │              │
                ▼              ▼              ▼
        ┌────────────┐  ┌────────────┐  ┌────────────┐
        │ ModelClient│  │   Agent    │  │  Workflow  │
        └────────────┘  └────────────┘  └────────────┘
                │              │              │
                └──────────────┼──────────────┘
                               │
                               ▼
                    ┌─────────────────────┐
                    │  ExecutionPlan      │
                    └──────────┬──────────┘
                               │
                ┌──────────────┼──────────────┐
                │              │              │
                ▼              ▼              ▼
        ┌────────────┐  ┌────────────┐  ┌────────────┐
        │   Task     │  │ TaskResult │  │  TaskError │
        └────────────┘  └────────────┘  └────────────┘
                │              │              │
                └──────────────┼──────────────┘
                               │
                               ▼
                    ┌─────────────────────┐
                    │  Learning Engine    │
                    └──────────┬──────────┘
                               │
                ┌──────────────┼──────────────┐
                │              │              │
                ▼              ▼              ▼
        ┌────────────┐  ┌────────────┐  ┌────────────┐
        │  Pattern   │  │LearningEvent
        │            │  │            │  │ Knowledge  │
        │            │  │            │  │   Base     │
        └────────────┘  └────────────┘  └────────────┘
```
