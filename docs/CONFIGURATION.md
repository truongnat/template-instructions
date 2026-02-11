# Configuration Guide

This guide provides comprehensive information about configuring the Agentic SDLC Kit for your specific needs.

## 📋 Configuration Overview

The SDLC Kit uses multiple configuration sources:

1. **Environment Variables** (`.env`) - Secrets and environment-specific settings
2. **Configuration File** (`agentic.yaml`) - Main configuration
3. **Agent Configurations** (`.agent/`) - Agent-specific settings
4. **Workflow Definitions** (`.agent/workflows/`) - Workflow configurations

## 🔧 Environment Variables

### Creating the .env File

```bash
# Copy the template
cp .env.template .env

# Edit with your settings
nano .env  # or your preferred editor
```

### Core Configuration

#### LLM Provider Settings

**OpenAI Configuration:**
```bash
# OpenAI API Key (required for OpenAI models)
OPENAI_API_KEY=sk-your-api-key-here

# OpenAI Organization ID (optional)
OPENAI_ORG_ID=org-your-org-id

# Default model
OPENAI_MODEL=gpt-4

# API base URL (optional, for proxies)
OPENAI_API_BASE=https://api.openai.com/v1
```

**Anthropic Configuration:**
```bash
# Anthropic API Key (required for Claude models)
ANTHROPIC_API_KEY=sk-ant-your-api-key-here

# Default model
ANTHROPIC_MODEL=claude-3-opus-20240229

# API base URL (optional)
ANTHROPIC_API_BASE=https://api.anthropic.com
```

**Local LLM (Ollama) Configuration:**
```bash
# Enable local LLM
USE_LOCAL_LLM=true

# Ollama base URL
OLLAMA_BASE_URL=http://localhost:11434

# Default model
OLLAMA_MODEL=llama2

# Model parameters
OLLAMA_TEMPERATURE=0.7
OLLAMA_TOP_P=0.9
```

#### Brain Configuration

```bash
# Enable brain learning
BRAIN_ENABLED=true

# Learning rate (0.0 to 1.0)
BRAIN_LEARNING_RATE=0.1

# Memory retention (days)
BRAIN_MEMORY_RETENTION=90

# Auto-learning from code changes
BRAIN_AUTO_LEARN=true

# Confidence threshold for decisions
BRAIN_CONFIDENCE_THRESHOLD=0.7
```

#### Logging Configuration

```bash
# Log level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
LOG_LEVEL=INFO

# Log file path
LOG_FILE=logs/agentic-sdlc.log

# Log format (json, text)
LOG_FORMAT=json

# Enable console logging
LOG_CONSOLE=true

# Log rotation
LOG_MAX_SIZE=10485760  # 10MB
LOG_BACKUP_COUNT=5
```

#### Storage Configuration

```bash
# Data directory
DATA_DIR=./data

# State directory
STATE_DIR=./states

# Cache directory
CACHE_DIR=./.cache

# Enable caching
CACHE_ENABLED=true

# Cache TTL (seconds)
CACHE_TTL=3600
```

#### Knowledge Base Configuration

**Neo4j (Graph Database):**
```bash
# Neo4j connection
NEO4J_URI=bolt://localhost:7687
NEO4J_USER=neo4j
NEO4J_PASSWORD=your_password

# Enable knowledge base
KNOWLEDGE_BASE_ENABLED=true

# Auto-sync to knowledge base
KNOWLEDGE_BASE_AUTO_SYNC=true
```

**Redis (Caching):**
```bash
# Redis connection
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_PASSWORD=your_password
REDIS_DB=0

# Enable Redis caching
REDIS_ENABLED=true
```

#### Security Configuration

```bash
# Encryption key (generate with: openssl rand -hex 32)
ENCRYPTION_KEY=your-32-byte-hex-key-here

# Enable audit logging
AUDIT_LOGGING=true

# Audit log file
AUDIT_LOG_FILE=logs/audit.log

# Enable input validation
INPUT_VALIDATION=true

# Enable sandboxing
SANDBOXING_ENABLED=true
```

#### Performance Configuration

```bash
# Max concurrent agents
MAX_CONCURRENT_AGENTS=5

# Request timeout (seconds)
REQUEST_TIMEOUT=300

# Max retries for failed requests
MAX_RETRIES=3

# Retry delay (seconds)
RETRY_DELAY=5

# Enable parallel execution
PARALLEL_EXECUTION=true
```

## 📄 Main Configuration File (agentic.yaml)

### Basic Structure

```yaml
# Project Information
project:
  name: "My Project"
  version: "1.0.0"
  description: "Project description"

# Core Settings
core:
  # Default LLM provider (openai, anthropic, ollama)
  llm_provider: "openai"
  
  # Default model
  default_model: "gpt-4"
  
  # Temperature for generation
  temperature: 0.7
  
  # Max tokens per request
  max_tokens: 4096

# Brain Settings
brain:
  enabled: true
  learning_rate: 0.1
  memory_retention_days: 90
  auto_learn: true
  confidence_threshold: 0.7

# Agent Settings
agents:
  # Default agent configuration
  defaults:
    timeout: 300
    max_retries: 3
    temperature: 0.7
  
  # Agent-specific overrides
  overrides:
    PM:
      temperature: 0.5
      model: "gpt-4"
    DEV:
      temperature: 0.7
      model: "gpt-4"
    TESTER:
      temperature: 0.3
      model: "gpt-3.5-turbo"

# Workflow Settings
workflows:
  # Default workflow configuration
  defaults:
    timeout: 600
    max_parallel_agents: 3
    retry_on_failure: true
  
  # Workflow-specific overrides
  overrides:
    cycle:
      timeout: 1800
      max_parallel_agents: 5
    planning:
      timeout: 300
      max_parallel_agents: 2

# Monitoring Settings
monitoring:
  enabled: true
  metrics_enabled: true
  health_check_interval: 60
  alert_on_failure: true

# Security Settings
security:
  input_validation: true
  audit_logging: true
  sandboxing: true
  encryption_enabled: true

# Storage Settings
storage:
  data_dir: "./data"
  state_dir: "./states"
  cache_dir: "./.cache"
  backup_enabled: true
  backup_interval: 86400  # 24 hours

# Integration Settings
integrations:
  github:
    enabled: false
    token: "${GITHUB_TOKEN}"
    org: "your-org"
  
  slack:
    enabled: false
    webhook_url: "${SLACK_WEBHOOK_URL}"
    channel: "#sdlc-notifications"
  
  jira:
    enabled: false
    url: "https://your-domain.atlassian.net"
    email: "${JIRA_EMAIL}"
    api_token: "${JIRA_API_TOKEN}"
```

### Configuration Sections Explained

#### Project Section

Defines basic project information:

```yaml
project:
  name: "My Project"           # Project name
  version: "1.0.0"             # Current version
  description: "Description"   # Project description
  repository: "github.com/..."  # Repository URL
  team: ["Alice", "Bob"]       # Team members
```

#### Core Section

Core system settings:

```yaml
core:
  llm_provider: "openai"       # LLM provider
  default_model: "gpt-4"       # Default model
  temperature: 0.7             # Generation temperature
  max_tokens: 4096             # Max tokens per request
  top_p: 0.9                   # Nucleus sampling
  frequency_penalty: 0.0       # Frequency penalty
  presence_penalty: 0.0        # Presence penalty
```

#### Brain Section

Brain learning configuration:

```yaml
brain:
  enabled: true                      # Enable brain
  learning_rate: 0.1                 # Learning rate
  memory_retention_days: 90          # Memory retention
  auto_learn: true                   # Auto-learn from changes
  confidence_threshold: 0.7          # Decision confidence
  pattern_recognition: true          # Enable pattern recognition
  feedback_learning: true            # Learn from feedback
  knowledge_base_sync: true          # Sync to knowledge base
```

#### Agents Section

Agent configuration:

```yaml
agents:
  defaults:
    timeout: 300                     # Default timeout
    max_retries: 3                   # Max retries
    temperature: 0.7                 # Default temperature
    model: "gpt-4"                   # Default model
  
  overrides:
    PM:                              # Project Manager
      temperature: 0.5               # Lower temp for planning
      model: "gpt-4"
      system_prompt: "custom prompt"
    
    DEV:                             # Developer
      temperature: 0.7
      model: "gpt-4"
      max_tokens: 8192               # More tokens for code
    
    TESTER:                          # QA Engineer
      temperature: 0.3               # Lower temp for testing
      model: "gpt-3.5-turbo"         # Faster model
```

#### Workflows Section

Workflow configuration:

```yaml
workflows:
  defaults:
    timeout: 600                     # Default timeout
    max_parallel_agents: 3           # Max parallel agents
    retry_on_failure: true           # Retry on failure
    save_artifacts: true             # Save artifacts
  
  overrides:
    cycle:                           # Full cycle workflow
      timeout: 1800                  # Longer timeout
      max_parallel_agents: 5         # More parallelism
      phases:
        - research
        - planning
        - implementation
        - review
    
    planning:                        # Planning workflow
      timeout: 300
      max_parallel_agents: 2
      agents: ["PM", "SA"]
```

## 🤖 Agent Configuration

### Agent Configuration Files

Agent configurations are stored in `.agent/agents/`:

```
.agent/
├── agents/
│   ├── pm.yaml              # Project Manager
│   ├── sa.yaml              # System Architect
│   ├── dev.yaml             # Developer
│   ├── tester.yaml          # QA Engineer
│   └── ...
```

### Agent Configuration Structure

```yaml
# .agent/agents/pm.yaml
agent:
  id: "PM"
  name: "Project Manager"
  type: "planning"
  description: "Manages project planning and coordination"

# Capabilities
capabilities:
  - "project_planning"
  - "task_breakdown"
  - "resource_allocation"
  - "progress_tracking"

# LLM Configuration
llm:
  provider: "openai"
  model: "gpt-4"
  temperature: 0.5
  max_tokens: 4096

# System Prompt
system_prompt: |
  You are an experienced Project Manager for software development.
  Your role is to plan, coordinate, and track project progress.
  
  Key responsibilities:
  - Break down features into tasks
  - Estimate effort and timeline
  - Allocate resources
  - Track progress and blockers
  - Communicate with stakeholders

# Tools and Integrations
tools:
  - "task_creation"
  - "timeline_estimation"
  - "resource_planning"
  - "progress_tracking"

# Behavior Configuration
behavior:
  proactive: true              # Proactively suggest improvements
  collaborative: true          # Work with other agents
  learning_enabled: true       # Learn from feedback
  confidence_threshold: 0.7    # Minimum confidence for decisions

# Constraints
constraints:
  max_tasks_per_sprint: 20
  min_task_size_hours: 1
  max_task_size_hours: 40
```

## 🔄 Workflow Configuration

### Workflow Definition Files

Workflows are defined in `.agent/workflows/`:

```
.agent/
├── workflows/
│   ├── cycle.yaml           # Full development cycle
│   ├── planning.yaml        # Planning workflow
│   ├── review.yaml          # Code review workflow
│   └── ...
```

### Workflow Configuration Structure

```yaml
# .agent/workflows/cycle.yaml
workflow:
  id: "cycle"
  name: "Full Development Cycle"
  description: "Complete development cycle from research to review"
  version: "1.0.0"

# Phases
phases:
  - id: "research"
    name: "Research Phase"
    agents: ["RESEARCH"]
    parallel: false
    timeout: 300
    
  - id: "planning"
    name: "Planning Phase"
    agents: ["PM", "SA"]
    parallel: true
    timeout: 600
    
  - id: "implementation"
    name: "Implementation Phase"
    agents: ["DEV"]
    parallel: false
    timeout: 1800
    
  - id: "review"
    name: "Review Phase"
    agents: ["REVIEWER", "TESTER"]
    parallel: true
    timeout: 600

# Dependencies
dependencies:
  planning: ["research"]
  implementation: ["planning"]
  review: ["implementation"]

# Configuration
config:
  timeout: 3600
  max_retries: 2
  retry_delay: 60
  save_artifacts: true
  notify_on_completion: true

# Gates (Human-in-the-loop)
gates:
  - phase: "planning"
    type: "approval"
    message: "Review and approve the plan"
    
  - phase: "implementation"
    type: "approval"
    message: "Review code before deployment"

# Triggers
triggers:
  on_success:
    - action: "notify"
      channel: "slack"
      message: "Workflow completed successfully"
  
  on_failure:
    - action: "notify"
      channel: "slack"
      message: "Workflow failed"
    - action: "create_issue"
      tracker: "github"
```

## 🔍 Configuration Validation

### Validate Configuration

```bash
# Validate all configuration files
asdlc config validate

# Validate specific file
asdlc config validate agentic.yaml

# Validate agent configuration
asdlc config validate .agent/agents/pm.yaml

# Validate workflow configuration
asdlc config validate .agent/workflows/cycle.yaml
```

### Configuration Schema

The kit validates configurations against JSON schemas:

```
config/
├── schemas/
│   ├── agentic.schema.json      # Main config schema
│   ├── agent.schema.json        # Agent config schema
│   ├── workflow.schema.json     # Workflow config schema
│   └── ...
```

## 🎛️ Runtime Configuration

### View Current Configuration

```bash
# Show all configuration
asdlc config show

# Show specific section
asdlc config show core
asdlc config show agents
asdlc config show workflows

# Show in different formats
asdlc config show --format json
asdlc config show --format yaml
```

### Update Configuration

```bash
# Set configuration value
asdlc config set core.temperature 0.8
asdlc config set brain.learning_rate 0.2

# Reset to defaults
asdlc config reset

# Reset specific section
asdlc config reset agents
```

## 🔐 Security Best Practices

### Secrets Management

**DO:**
- ✅ Store secrets in `.env` file
- ✅ Use environment variables for sensitive data
- ✅ Add `.env` to `.gitignore`
- ✅ Use encryption for stored secrets
- ✅ Rotate API keys regularly

**DON'T:**
- ❌ Commit secrets to version control
- ❌ Hard-code API keys in configuration
- ❌ Share `.env` files
- ❌ Use weak encryption keys
- ❌ Store secrets in plain text

### Configuration Security

```yaml
# Use environment variable references
integrations:
  github:
    token: "${GITHUB_TOKEN}"      # ✅ Good
    # token: "ghp_xxx"            # ❌ Bad
  
  slack:
    webhook_url: "${SLACK_WEBHOOK}"  # ✅ Good
    # webhook_url: "https://..."     # ❌ Bad
```

## 📊 Configuration Examples

### Development Environment

```yaml
# agentic.yaml (development)
core:
  llm_provider: "ollama"          # Local LLM
  default_model: "llama2"
  temperature: 0.7

brain:
  enabled: true
  auto_learn: true

monitoring:
  enabled: true
  metrics_enabled: true

security:
  sandboxing: false               # Disabled for dev
  audit_logging: false
```

### Production Environment

```yaml
# agentic.yaml (production)
core:
  llm_provider: "openai"
  default_model: "gpt-4"
  temperature: 0.5                # Lower for consistency

brain:
  enabled: true
  auto_learn: false               # Manual learning in prod
  confidence_threshold: 0.9       # Higher threshold

monitoring:
  enabled: true
  metrics_enabled: true
  alert_on_failure: true

security:
  sandboxing: true                # Enabled for security
  audit_logging: true
  encryption_enabled: true
```

### Testing Environment

```yaml
# agentic.yaml (testing)
core:
  llm_provider: "openai"
  default_model: "gpt-3.5-turbo"  # Faster/cheaper
  temperature: 0.3                # Deterministic

brain:
  enabled: false                  # Disabled for tests

monitoring:
  enabled: true
  metrics_enabled: false

security:
  sandboxing: true
  audit_logging: false
```

## 🐛 Troubleshooting Configuration

### Common Issues

**Issue: Configuration not loading**
```bash
# Check file exists
ls -la agentic.yaml

# Validate syntax
asdlc config validate agentic.yaml

# Check permissions
chmod 644 agentic.yaml
```

**Issue: Environment variables not working**
```bash
# Check .env file exists
ls -la .env

# Verify variables are set
echo $OPENAI_API_KEY

# Source .env manually
export $(cat .env | xargs)
```

**Issue: Invalid configuration values**
```bash
# Validate against schema
asdlc config validate

# Reset to defaults
asdlc config reset

# Show current values
asdlc config show
```

## 📚 Further Reading

- **[Getting Started Guide](GETTING_STARTED.md)** - Quick start tutorial
- **[Architecture Overview](ARCHITECTURE.md)** - System architecture
- **[Troubleshooting Guide](TROUBLESHOOTING.md)** - Common issues
- **[Security Policy](../SECURITY.md)** - Security guidelines

---

**Need help with configuration?** Check the [Troubleshooting Guide](TROUBLESHOOTING.md) or open an issue on GitHub.
