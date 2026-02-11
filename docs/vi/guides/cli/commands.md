# Command Reference

**Phiên bản**: 3.0.0  
**Cập nhật lần cuối**: 11/02/2026


## Giới Thiệu

Tài liệu này cung cấp reference đầy đủ cho tất cả commands trong Agentic SDLC CLI. Mỗi command được mô tả chi tiết với syntax, options, arguments, và examples.

## Global Options

Các options này có thể sử dụng với bất kỳ command nào:

```bash
--version              # Hiển thị version và exit
--help, -h             # Hiển thị help message
--verbose, -v          # Enable verbose output
--quiet, -q            # Suppress non-error output
--config PATH          # Path đến config file (default: config.yaml)
--log-level LEVEL      # Set log level: DEBUG, INFO, WARNING, ERROR, CRITICAL
--no-color             # Disable colored output
--output-format FORMAT # Output format: text, json, yaml (default: text)
```text

### Examples

```bash
# Xem version
agentic --version

# Chạy với verbose logging
agentic --verbose run my-workflow

# Sử dụng custom config file
agentic --config production.yaml run deploy

# Output dạng JSON
agentic --output-format json agent list
```text

---

## init - Khởi Tạo Project

Tạo một Agentic SDLC project mới với cấu trúc thư mục và configuration files.

### Syntax

```bash
agentic init [OPTIONS] PROJECT_NAME
```text

### Arguments

- `PROJECT_NAME` (required): Tên của project mới

### Options

```bash
--template TEMPLATE    # Template để sử dụng (default, minimal, full)
--provider PROVIDER    # Default LLM provider (openai, anthropic, ollama)
--model MODEL          # Default model name
--no-git               # Không khởi tạo git repository
--force, -f            # Overwrite nếu directory đã tồn tại
```text

### Examples

```bash
# Khởi tạo project cơ bản
agentic init my-project

# Khởi tạo với OpenAI provider
agentic init my-project --provider openai --model gpt-4

# Khởi tạo với template đầy đủ
agentic init my-project --template full

# Khởi tạo mà không tạo git repo
agentic init my-project --no-git

# Force overwrite existing directory
agentic init my-project --force
```text

### Cấu Trúc Project Được Tạo

```
my-project/
├── config.yaml              # Configuration file
├── .agentic/
│   ├── agents/              # Agent definitions
│   ├── workflows/           # Workflow definitions
│   └── plugins/             # Custom plugins
├── logs/                    # Log files
├── .gitignore
└── README.md
```text

### Exit Codes

- `0`: Project created successfully
- `1`: Project directory already exists (use --force)
- `2`: Invalid project name
- `3`: Permission denied

---

## config - Quản Lý Configuration

Xem và chỉnh sửa configuration settings.

### Subcommands

#### config get

Lấy giá trị của một configuration setting.

```bash
agentic config get [OPTIONS] KEY
```text

**Arguments:**
- `KEY` (required): Configuration key (dot notation)

**Options:**
```bash
--default VALUE    # Default value nếu key không tồn tại
```text

**Examples:**

```bash
# Lấy default provider
agentic config get model.default_provider

# Lấy với default value
agentic config get model.temperature --default 0.7

# Lấy nested value
agentic config get openai.api_key
```text

#### config set

Set giá trị cho một configuration setting.

```bash
agentic config set [OPTIONS] KEY VALUE
```text

**Arguments:**
- `KEY` (required): Configuration key
- `VALUE` (required): New value

**Options:**
```bash
--type TYPE        # Value type: string, int, float, bool, json
--global, -g       # Set trong global config (~/.agentic/config.yaml)
```text

**Examples:**

```bash
# Set string value
agentic config set model.default_provider openai

# Set integer value
agentic config set agents.default_max_iterations 20 --type int

# Set boolean value
agentic config set logging.enabled true --type bool

# Set JSON value
agentic config set model.parameters '{"temperature": 0.7}' --type json

# Set global config
agentic config set openai.api_key sk-... --global
```text

#### config show

Hiển thị tất cả configuration settings.

```bash
agentic config show [OPTIONS]
```text

**Options:**
```bash
--format FORMAT    # Output format: yaml, json, table (default: yaml)
--section SECTION  # Chỉ hiển thị một section (model, logging, agents, etc.)
--include-defaults # Include default values
```text

**Examples:**

```bash
# Hiển thị tất cả config
agentic config show

# Hiển thị dạng JSON
agentic config show --format json

# Chỉ hiển thị model config
agentic config show --section model

# Include default values
agentic config show --include-defaults
```text

**Output Example:**

```yaml
model:
  default_provider: openai
  default_model: gpt-4
  temperature: 0.7

openai:
  api_key: sk-***
  organization: org-xxx

logging:
  level: INFO
  format: json
  output: logs/agentic.log

agents:
  default_max_iterations: 10
  default_timeout: 300
```text

---

## run - Chạy Workflows và Agents

Thực thi workflows hoặc agents.

### Syntax

```bash
agentic run [OPTIONS] WORKFLOW_NAME [PARAMETERS...]
```text

### Arguments

- `WORKFLOW_NAME` (required): Tên của workflow hoặc agent
- `PARAMETERS`: Key-value pairs cho workflow parameters

### Options

```bash
--file PATH, -f PATH       # Input file
--output PATH, -o PATH     # Output file
--params PATH              # JSON/YAML file chứa parameters
--agent AGENT              # Chỉ định agent để chạy workflow
--timeout SECONDS          # Execution timeout (default: 300)
--async                    # Chạy asynchronously
--watch                    # Watch mode - rerun on file changes
--dry-run                  # Simulate execution without running
--continue-on-error        # Continue nếu có errors
```text

### Examples

```bash
# Chạy workflow cơ bản
agentic run code-review

# Chạy với input file
agentic run code-review --file src/main.py

# Chạy với output file
agentic run code-review --file src/main.py --output report.json

# Chạy với parameters từ file
agentic run deploy --params deploy-params.json

# Chạy với inline parameters
agentic run test-suite --coverage true --parallel 4

# Chạy với specific agent
agentic run code-review --agent senior-reviewer

# Chạy với timeout
agentic run long-workflow --timeout 600

# Dry run để test
agentic run deploy --dry-run

# Watch mode cho development
agentic run test-suite --watch

# Async execution
agentic run background-task --async
```text

### Parameter Formats

**Inline parameters:**
```bash
agentic run workflow --param1 value1 --param2 value2
```text

**JSON file:**
```bash
# params.json
{
  "file": "src/main.py",
  "output": "report.json",
  "options": {
    "strict": true,
    "coverage": 80
  }
}

agentic run workflow --params params.json
```text

**YAML file:**
```bash
# params.yaml
file: src/main.py
output: report.json
options:
  strict: true
  coverage: 80

agentic run workflow --params params.yaml
```text

### Exit Codes

- `0`: Workflow completed successfully
- `1`: Workflow failed
- `2`: Invalid workflow name
- `3`: Timeout exceeded
- `4`: Agent not found
- `5`: Parameter validation error

---

## agent - Quản Lý Agents

Tạo, liệt kê, và quản lý agents.

### Subcommands

#### agent list

Liệt kê tất cả agents trong registry.

```bash
agentic agent list [OPTIONS]
```text

**Options:**
```bash
--role ROLE            # Filter by role
--model MODEL          # Filter by model
--status STATUS        # Filter by status (active, inactive, error)
--format FORMAT        # Output format: table, json, yaml (default: table)
--verbose, -v          # Show detailed information
```text

**Examples:**

```bash
# Liệt kê tất cả agents
agentic agent list

# Filter by role
agentic agent list --role Developer

# Filter by model
agentic agent list --model gpt-4

# JSON output
agentic agent list --format json

# Verbose output
agentic agent list --verbose
```text

**Output Example:**

```
┌──────────────────┬─────────────────┬──────────────┬──────────┬─────────────┐
│ ID               │ Name            │ Role         │ Model    │ Status      │
├──────────────────┼─────────────────┼──────────────┼──────────┼─────────────┤
│ agent-001        │ backend-dev     │ Developer    │ gpt-4    │ active      │
│ agent-002        │ code-reviewer   │ Reviewer     │ gpt-4    │ active      │
│ agent-003        │ test-engineer   │ Tester       │ gpt-3.5  │ active      │
└──────────────────┴─────────────────┴──────────────┴──────────┴─────────────┘
```text

#### agent create

Tạo một agent mới.

```bash
agentic agent create [OPTIONS] NAME
```text

**Arguments:**
- `NAME` (required): Tên của agent

**Options:**
```bash
--role ROLE                # Agent role (required)
--model MODEL              # LLM model (default: from config)
--provider PROVIDER        # LLM provider (default: from config)
--system-prompt TEXT       # System prompt
--tools TOOLS              # Comma-separated list of tools
--max-iterations INT       # Max iterations (default: 10)
--metadata JSON            # JSON metadata
--template TEMPLATE        # Agent template (developer, tester, reviewer, etc.)
```text

**Examples:**

```bash
# Tạo agent cơ bản
agentic agent create my-dev --role Developer --model gpt-4

# Tạo với system prompt
agentic agent create reviewer --role "Code Reviewer" \
  --model gpt-4 \
  --system-prompt "You are an expert code reviewer..."

# Tạo với tools
agentic agent create dev-agent --role Developer \
  --model gpt-4 \
  --tools "code_execution,file_operations,git_operations"

# Tạo với metadata
agentic agent create backend-dev --role Developer \
  --model gpt-4 \
  --metadata '{"team": "backend", "expertise": ["python", "fastapi"]}'

# Tạo từ template
agentic agent create my-tester --template tester --model gpt-3.5-turbo

# Tạo với max iterations
agentic agent create debugger --role "Bug Fixer" \
  --model gpt-4 \
  --max-iterations 20
```text

#### agent status

Xem status và thông tin chi tiết của một agent.

```bash
agentic agent status [OPTIONS] AGENT_ID
```text

**Arguments:**
- `AGENT_ID` (required): ID hoặc name của agent

**Options:**
```bash
--format FORMAT        # Output format: text, json, yaml (default: text)
--show-history         # Show execution history
--show-metrics         # Show performance metrics
```text

**Examples:**

```bash
# Xem status cơ bản
agentic agent status agent-001

# Xem với execution history
agentic agent status my-dev --show-history

# Xem với metrics
agentic agent status my-dev --show-metrics

# JSON output
agentic agent status my-dev --format json
```text

**Output Example:**

```
Agent: backend-dev (agent-001)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Status:           active
Role:             Developer
Model:            gpt-4
Provider:         openai
Max Iterations:   10
Created:          2024-01-15 10:30:00
Last Active:      2024-01-15 14:25:30

System Prompt:
  You are an expert Python developer specializing in backend development...

Tools:
  • code_execution
  • file_operations
  • git_operations
  • api_calls

Metadata:
  team: backend
  expertise: [python, fastapi, postgresql]
  version: 1.0.0

Recent Activity:
  • 2024-01-15 14:25:30 - Completed: code-review-workflow
  • 2024-01-15 13:15:20 - Completed: test-generation
  • 2024-01-15 12:00:10 - Completed: bug-fix-task
```text

#### agent update

Cập nhật configuration của một agent.

```bash
agentic agent update [OPTIONS] AGENT_ID
```text

**Arguments:**
- `AGENT_ID` (required): ID hoặc name của agent

**Options:**
```bash
--role ROLE                # Update role
--model MODEL              # Update model
--system-prompt TEXT       # Update system prompt
--tools TOOLS              # Update tools (comma-separated)
--max-iterations INT       # Update max iterations
--metadata JSON            # Update metadata
```text

**Examples:**

```bash
# Update model
agentic agent update my-dev --model gpt-4-turbo

# Update system prompt
agentic agent update my-dev --system-prompt "New prompt..."

# Update tools
agentic agent update my-dev --tools "code_execution,pytest,black"

# Update metadata
agentic agent update my-dev --metadata '{"version": "2.0.0"}'
```text

#### agent delete

Xóa một agent khỏi registry.

```bash
agentic agent delete [OPTIONS] AGENT_ID
```text

**Arguments:**
- `AGENT_ID` (required): ID hoặc name của agent

**Options:**
```bash
--force, -f            # Skip confirmation prompt
```text

**Examples:**

```bash
# Xóa với confirmation
agentic agent delete my-dev

# Force delete
agentic agent delete my-dev --force
```text

---

## Advanced Usage

### Piping và Chaining

```bash
# Pipe output đến jq
agentic agent list --format json | jq '.agents[] | select(.role=="Developer")'

# Chain commands
agentic run tests && agentic run build && agentic run deploy

# Conditional execution
agentic run tests || echo "Tests failed!"
```text

### Environment Variables

```bash
# Set API keys
export OPENAI_API_KEY=sk-...
export ANTHROPIC_API_KEY=sk-ant-...

# Set config location
export AGENTIC_CONFIG=/path/to/config.yaml

# Set log level
export AGENTIC_LOG_LEVEL=DEBUG

# Disable color output
export NO_COLOR=1
```text

### Configuration Precedence

CLI loads configuration theo thứ tự ưu tiên:

1. Command-line options (highest priority)
2. Environment variables
3. Project config file (`./config.yaml`)
4. Global config file (`~/.agentic/config.yaml`)
5. Default values (lowest priority)

```bash
# Command-line option overrides config file
agentic --config custom.yaml run workflow

# Environment variable overrides config file
export AGENTIC_LOG_LEVEL=DEBUG
agentic run workflow  # Uses DEBUG level
```text

### Batch Operations

```bash
# Tạo multiple agents
for role in Developer Tester Reviewer; do
  agentic agent create "${role,,}-agent" --role "$role" --model gpt-4
done

# Run multiple workflows
for workflow in test build deploy; do
  agentic run "$workflow" || break
done

# Process multiple files
find src/ -name "*.py" | while read file; do
  agentic run code-review --file "$file"
done
```text

### Debugging

```bash
# Enable verbose logging
agentic --verbose run workflow

# Enable debug log level
agentic --log-level DEBUG run workflow

# Dry run để test
agentic run workflow --dry-run

# Save logs to file
agentic --verbose run workflow 2>&1 | tee execution.log
```

## Tài Liệu Liên Quan

- [CLI Overview](overview.md) - Giới thiệu về CLI
- [CLI Examples](examples.md) - Ví dụ thực tế
- [Configuration Guide](../../getting-started/configuration.md) - Hướng dẫn cấu hình
- [Workflows](../workflows/overview.md) - Xây dựng workflows
- [Agents](../agents/overview.md) - Quản lý agents

## Tóm Tắt

CLI cung cấp các commands chính:

- **init**: Khởi tạo projects mới
- **config**: Quản lý configuration (get, set, show)
- **run**: Chạy workflows và agents
- **agent**: Quản lý agents (list, create, status, update, delete)

Mỗi command có nhiều options và subcommands để customize behavior. Sử dụng `--help` với bất kỳ command nào để xem chi tiết.

Tiếp theo, xem [CLI Examples](examples.md) để học cách sử dụng CLI trong các tình huống thực tế.
