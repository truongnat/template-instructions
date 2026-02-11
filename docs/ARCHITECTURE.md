# Architecture Overview

This document provides a comprehensive overview of the Agentic SDLC Kit architecture, including system design, component interactions, and key design decisions.

## 🏗️ High-Level Architecture

The SDLC Kit follows a layered architecture with clear separation of concerns:

```
┌─────────────────────────────────────────────────────────┐
│                    CLI Layer                            │
│  (User Interface - Commands, Output Formatting)         │
└─────────────────────────────────────────────────────────┘
                          │
┌─────────────────────────────────────────────────────────┐
│                  Core Business Logic                    │
│  (Orchestration, Intelligence, Infrastructure)          │
└─────────────────────────────────────────────────────────┘
                          │
┌─────────────────────────────────────────────────────────┐
│              Cross-Cutting Concerns                     │
│  (Config, Security, Monitoring, Utils)                  │
└─────────────────────────────────────────────────────────┘
                          │
┌─────────────────────────────────────────────────────────┐
│                  Infrastructure                         │
│  (Models, Schemas, Documentation, Examples)             │
└─────────────────────────────────────────────────────────┘
```

**📊 Detailed Diagram:** See [System Architecture Diagram](diagrams/system_architecture.md) for a comprehensive view with all components and interactions.

## 🎯 Design Principles

### 1. Layered Architecture
The system is organized into three concentric layers:

- **Layer 1: Core** - GEMINI.md, Rules, and Workflows
- **Layer 2: Intelligence** - 26 Sub-Agents (Brain, SwarmRouter, Self-Learning)
- **Layer 3: Infrastructure** - CLI, SDK, AOP (Agent Orchestration Protocol)

### 2. Separation of Concerns
Each component has a single, well-defined responsibility:

- **CLI** - User interaction and command execution
- **Orchestration** - Workflow coordination and agent management
- **Intelligence** - AI reasoning and decision-making
- **Infrastructure** - Core services and utilities

### 3. Modularity
Components are loosely coupled and can be:
- Developed independently
- Tested in isolation
- Replaced or upgraded without affecting others
- Reused across different contexts

### 4. Extensibility
The architecture supports:
- Custom agents and workflows
- Plugin-based extensions
- Multiple LLM providers
- Distributed deployment

## 📦 Component Architecture

### Directory Structure

```
agentic-sdlc/
├── agentic_sdlc/           # Core package
│   ├── core/               # Core functionality
│   │   ├── agents/         # Agent implementations
│   │   ├── workflows/      # Workflow definitions
│   │   └── utils/          # Core utilities
│   ├── orchestration/      # Orchestration layer
│   │   ├── engine/         # Workflow engine
│   │   ├── router/         # Agent routing
│   │   └── coordinator/    # Multi-agent coordination
│   ├── intelligence/       # Intelligence layer
│   │   ├── brain/          # Self-learning brain
│   │   ├── learner/        # Learning algorithms
│   │   └── reasoner/       # Reasoning engine
│   ├── infrastructure/     # Infrastructure services
│   │   ├── llm/            # LLM integrations
│   │   ├── storage/        # Data persistence
│   │   └── cache/          # Caching layer
│   └── cli.py              # CLI entry point
├── config/                 # Configuration management
├── models/                 # Data models and schemas
├── utils/                  # Shared utilities
├── security/               # Security module
├── monitoring/             # Logging and monitoring
├── docs/                   # Documentation
├── examples/               # Usage examples
├── scripts/                # Utility scripts
└── tests/                  # Test suite
```

## 🧩 Core Components

### 1. CLI Layer

**Purpose:** Provide user interface for interacting with the system

**Components:**
- `cli/main.py` - CLI entry point
- `cli/commands/` - Command implementations
- `cli/output/` - Output formatting and styling

**Key Features:**
- Command-line interface with subcommands
- Rich output formatting with colors and tables
- Progress indicators and status updates
- Interactive prompts for user input

**Example Usage:**
```bash
asdlc brain status
asdlc workflow cycle "Feature implementation"
asdlc agent list
```

### 2. Orchestration Layer

**Purpose:** Coordinate workflows and manage agent interactions

**Components:**
- `orchestration/engine/` - Workflow execution engine
- `orchestration/router/` - Agent routing and selection
- `orchestration/coordinator/` - Multi-agent coordination
- `orchestration/planner/` - Execution planning

**Key Features:**
- Workflow definition and execution
- Agent lifecycle management
- Task distribution and load balancing
- Parallel and sequential execution
- Error handling and recovery

**Workflow Execution Flow:**
```
User Request → Workflow Engine → Agent Router → Agent Pool
                     ↓                              ↓
              Execution Plan ← Coordinator ← Agent Execution
                     ↓
              Result Aggregation → User Response
```

**📊 Detailed Diagram:** See [Workflow Flow Diagram](diagrams/workflow_flow.md) for a complete sequence diagram showing all steps, error handling, and learning integration.

### 3. Intelligence Layer

**Purpose:** Provide AI reasoning, learning, and decision-making

**Components:**
- `intelligence/brain/` - Self-learning brain
- `intelligence/learner/` - Learning algorithms
- `intelligence/reasoner/` - Reasoning engine
- `intelligence/memory/` - Context and memory management

**Key Features:**
- Self-learning from code patterns
- Context-aware decision making
- Pattern recognition and prediction
- Knowledge accumulation and retrieval
- Adaptive behavior based on feedback

**Brain Architecture:**
```
┌─────────────────────────────────────────┐
│              Brain Core                 │
│  ┌─────────────────────────────────┐   │
│  │      Learning Engine            │   │
│  │  - Pattern Recognition          │   │
│  │  - Feedback Processing          │   │
│  │  - Model Optimization           │   │
│  └─────────────────────────────────┘   │
│  ┌─────────────────────────────────┐   │
│  │      Memory System              │   │
│  │  - Short-term Context           │   │
│  │  - Long-term Knowledge          │   │
│  │  - Episodic Memory              │   │
│  └─────────────────────────────────┘   │
│  ┌─────────────────────────────────┐   │
│  │      Reasoning Engine           │   │
│  │  - Decision Making              │   │
│  │  - Strategy Selection           │   │
│  │  - Confidence Scoring           │   │
│  └─────────────────────────────────┘   │
└─────────────────────────────────────────┘
```

### 4. Infrastructure Layer

**Purpose:** Provide core services and integrations

**Components:**
- `infrastructure/llm/` - LLM provider integrations
- `infrastructure/storage/` - Data persistence
- `infrastructure/cache/` - Caching layer
- `infrastructure/queue/` - Task queue management

**Key Features:**
- Multiple LLM provider support (OpenAI, Anthropic, Ollama)
- Persistent storage for state and knowledge
- Redis-based caching for performance
- Asynchronous task processing
- Health monitoring and diagnostics

**LLM Integration Architecture:**
```
┌──────────────────────────────────────────┐
│         LLM Abstraction Layer            │
├──────────────────────────────────────────┤
│  ┌────────┐  ┌────────┐  ┌────────┐    │
│  │ OpenAI │  │Anthropic│  │ Ollama │    │
│  │Provider│  │Provider │  │Provider│    │
│  └────────┘  └────────┘  └────────┘    │
├──────────────────────────────────────────┤
│         Common Interface                 │
│  - generate()                            │
│  - stream()                              │
│  - embed()                               │
└──────────────────────────────────────────┘
```

## 🔄 Data Flow

### Request Processing Flow

```
1. User Input (CLI/SDK)
   ↓
2. Command Parser
   ↓
3. Workflow Engine
   ↓
4. Agent Router
   ↓
5. Agent Pool
   ↓
6. LLM Provider
   ↓
7. Response Processing
   ↓
8. Brain Learning
   ↓
9. Output Formatting
   ↓
10. User Response
```

### Agent Execution Flow

```
┌─────────────────────────────────────────────┐
│           Workflow Request                  │
└─────────────────┬───────────────────────────┘
                  ↓
┌─────────────────────────────────────────────┐
│        Execution Planner                    │
│  - Analyze requirements                     │
│  - Select agents                            │
│  - Create execution plan                    │
└─────────────────┬───────────────────────────┘
                  ↓
┌─────────────────────────────────────────────┐
│        Agent Coordinator                    │
│  - Distribute tasks                         │
│  - Manage dependencies                      │
│  - Monitor progress                         │
└─────────────────┬───────────────────────────┘
                  ↓
┌─────────────────────────────────────────────┐
│        Agent Execution                      │
│  ┌──────┐  ┌──────┐  ┌──────┐             │
│  │Agent1│  │Agent2│  │Agent3│             │
│  │  PM  │  │  SA  │  │ DEV  │             │
│  └──────┘  └──────┘  └──────┘             │
└─────────────────┬───────────────────────────┘
                  ↓
┌─────────────────────────────────────────────┐
│        Result Aggregation                   │
│  - Collect outputs                          │
│  - Resolve conflicts                        │
│  - Synthesize results                       │
└─────────────────┬───────────────────────────┘
                  ↓
┌─────────────────────────────────────────────┐
│        Brain Learning                       │
│  - Record patterns                          │
│  - Update knowledge                         │
│  - Adjust strategies                        │
└─────────────────┬───────────────────────────┘
                  ↓
┌─────────────────────────────────────────────┐
│           Final Response                    │
└─────────────────────────────────────────────┘
```

## 🎭 Agent Architecture

### Agent Types

The system includes 18 specialized agent types:

**Planning & Management:**
- **PM** (Project Manager) - Planning, tracking, coordination
- **PO** (Product Owner) - Requirements, priorities, stakeholder management

**Design & Architecture:**
- **SA** (System Architect) - System design, architecture decisions
- **UIUX** (UI/UX Designer) - User interface and experience design

**Development:**
- **DEV** (Developer) - Code implementation
- **FRONTEND** - Frontend development
- **BACKEND** - Backend development
- **FULLSTACK** - Full-stack development

**Quality & Testing:**
- **TESTER** (QA Engineer) - Testing, verification, self-healing
- **REVIEWER** - Code review and quality assurance

**Security & Operations:**
- **SECA** (Security Analyst) - Security audits, vulnerability assessment
- **DEVOPS** - Infrastructure, deployment, operations

**Specialized:**
- **RESEARCH** - Technical research, proof of concepts
- **DATA** - Data analysis and engineering
- **ML** - Machine learning and AI
- **DOCS** - Documentation and technical writing

**Support:**
- **SUPPORT** - User support and troubleshooting
- **QUALITY_JUDGE** - Quality assessment and decision making

### Agent Lifecycle

```
┌──────────────┐
│ Registration │ - Agent registers with system
└──────┬───────┘
       ↓
┌──────────────┐
│Initialization│ - Load configuration and context
└──────┬───────┘
       ↓
┌──────────────┐
│    Ready     │ - Waiting for tasks
└──────┬───────┘
       ↓
┌──────────────┐
│  Execution   │ - Processing assigned task
└──────┬───────┘
       ↓
┌──────────────┐
│  Completion  │ - Return results
└──────┬───────┘
       ↓
┌──────────────┐
│   Learning   │ - Update knowledge from execution
└──────┬───────┘
       ↓
┌──────────────┐
│    Ready     │ - Ready for next task
└──────────────┘
```

**📊 Detailed Diagram:** See [Agent Interaction Diagram](diagrams/agent_interaction.md) for a comprehensive view of how all 18 agent types interact with each other and system components.

## 🔐 Security Architecture

### Security Layers

**1. Input Validation**
- Sanitize all user inputs
- Validate against schemas
- Prevent injection attacks

**2. Authentication & Authorization**
- API key management
- Role-based access control
- Secure credential storage

**3. Data Protection**
- Encryption at rest
- Encryption in transit
- Secure secret management

**4. Audit & Monitoring**
- Security event logging
- Anomaly detection
- Compliance reporting

### Security Components

```
security/
├── secrets_manager.py      # Secrets management
├── encryption.py           # Encryption utilities
├── audit_logger.py         # Security audit logging
└── validators.py           # Input validation
```

## 📊 Monitoring & Observability

### Monitoring Stack

**Logging:**
- Structured logging with JSON format
- Multiple log levels (DEBUG, INFO, WARNING, ERROR, CRITICAL)
- Log rotation and retention policies
- Centralized log aggregation

**Metrics:**
- Performance metrics (latency, throughput)
- Resource metrics (CPU, memory, disk)
- Business metrics (workflows executed, agents active)
- Custom metrics via instrumentation

**Health Checks:**
- Component health status
- Dependency health (database, cache, LLM providers)
- System resource availability
- Service readiness probes

**Alerting:**
- Threshold-based alerts
- Anomaly detection
- Alert routing and escalation
- Integration with notification systems

### Monitoring Architecture

```
┌─────────────────────────────────────────────┐
│         Application Layer                   │
│  - Instrumentation                          │
│  - Metrics Collection                       │
│  - Log Generation                           │
└─────────────────┬───────────────────────────┘
                  ↓
┌─────────────────────────────────────────────┐
│         Monitoring Layer                    │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐ │
│  │  Logs    │  │ Metrics  │  │  Health  │ │
│  │Aggregator│  │Collector │  │ Checker  │ │
│  └──────────┘  └──────────┘  └──────────┘ │
└─────────────────┬───────────────────────────┘
                  ↓
┌─────────────────────────────────────────────┐
│         Storage Layer                       │
│  - Log Storage                              │
│  - Metrics Database                         │
│  - Health Status Store                      │
└─────────────────┬───────────────────────────┘
                  ↓
┌─────────────────────────────────────────────┐
│         Visualization Layer                 │
│  - Dashboards                               │
│  - Alerts                                   │
│  - Reports                                  │
└─────────────────────────────────────────────┘
```

## 🔌 Integration Points

### External Integrations

**LLM Providers:**
- OpenAI (GPT-3.5, GPT-4)
- Anthropic (Claude)
- Ollama (Local LLMs)
- Custom providers via adapter pattern

**Knowledge Base:**
- Neo4j (Graph database)
- Vector databases (Pinecone, Weaviate)
- Traditional databases (PostgreSQL, MySQL)

**Development Tools:**
- Git (Version control)
- GitHub/GitLab (Repository hosting)
- CI/CD platforms (GitHub Actions, GitLab CI)
- Issue trackers (Jira, Linear)

**Communication:**
- Slack
- Discord
- Email
- Webhooks

## 🚀 Deployment Architecture

### Deployment Options

**1. Local Development**
```
Developer Machine
├── Python Virtual Environment
├── Local LLM (Ollama)
├── Local Cache (Redis)
└── File-based Storage
```

**2. Docker Deployment**
```
Docker Host
├── SDLC Kit Container
├── Neo4j Container
├── Redis Container
└── Shared Volumes
```

**3. Kubernetes Deployment**
```
Kubernetes Cluster
├── SDLC Kit Pods (Replicated)
├── Neo4j StatefulSet
├── Redis Deployment
├── Ingress Controller
└── Persistent Volumes
```

**4. Distributed Deployment**
```
Multiple Nodes
├── Orchestration Node (Coordinator)
├── Agent Nodes (Workers)
├── Storage Node (Database)
└── Cache Node (Redis)
```

## 📈 Scalability

### Horizontal Scaling

**Agent Pool Scaling:**
- Add more agent instances
- Load balancing across agents
- Dynamic agent allocation

**Workflow Engine Scaling:**
- Multiple workflow engine instances
- Task queue distribution
- Parallel workflow execution

**Storage Scaling:**
- Database replication
- Sharding strategies
- Read replicas

### Vertical Scaling

**Resource Optimization:**
- Memory management
- CPU utilization
- Disk I/O optimization
- Network bandwidth

## 🔄 State Management

### State Types

**1. Application State**
- Current sprint information
- Active workflows
- Agent status
- System configuration

**2. Brain State**
- Learned patterns
- Knowledge base
- Historical decisions
- Performance metrics

**3. Session State**
- User context
- Conversation history
- Temporary data
- Cache entries

### State Persistence

```
states/
├── brain_state.db          # Brain learning state
├── sprint_state.json       # Current sprint state
├── workflow_state.json     # Active workflows
└── agent_state.json        # Agent status
```

## 📚 Further Reading

- **[Configuration Guide](CONFIGURATION.md)** - System configuration
- **[API Reference](api/)** - API documentation
- **[Contributing Guide](../CONTRIBUTING.md)** - Development guidelines
- **[Security Policy](../SECURITY.md)** - Security practices

---

**Questions about the architecture?** Check the [Troubleshooting Guide](TROUBLESHOOTING.md) or open an issue on GitHub.
