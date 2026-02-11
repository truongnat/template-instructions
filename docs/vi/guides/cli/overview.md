# Tổng Quan về CLI

**Phiên bản**: 3.0.0  
**Cập nhật lần cuối**: 11/02/2026


## Giới Thiệu

Agentic SDLC CLI (Command-Line Interface - Giao diện dòng lệnh) là một công cụ mạnh mẽ cho phép bạn tương tác với Agentic SDLC framework trực tiếp từ terminal mà không cần viết code Python. CLI cung cấp các lệnh để khởi tạo projects, quản lý configuration, chạy workflows, và quản lý agents.

## Tại Sao Sử Dụng CLI?

### 1. Nhanh Chóng và Tiện Lợi

CLI cho phép bạn thực hiện các tác vụ phổ biến với một vài lệnh đơn giản:

```bash
# Khởi tạo project mới trong vài giây
agentic init my-project

# Chạy workflow ngay lập tức
agentic run code-review --file src/main.py
```text

### 2. Tích Hợp CI/CD

CLI dễ dàng tích hợp vào CI/CD pipelines:

```bash
# Trong GitHub Actions hoặc GitLab CI
agentic run automated-tests --config ci-config.yaml
```text

### 3. Scripting và Automation

Kết hợp CLI commands trong shell scripts để tự động hóa workflows:

```bash
#!/bin/bash
# Script tự động review code
agentic run code-review --file $1
agentic run security-scan --file $1
agentic run test-generation --file $1
```text

### 4. Không Cần Viết Code

Phù hợp cho users không muốn viết Python code nhưng vẫn muốn sử dụng Agentic SDLC:

```bash
# Chạy workflow mà không cần viết code
agentic run my-workflow --params input.json
```text

## Cài Đặt CLI

### Cài Đặt với Pip

```bash
# Cài đặt CLI cùng với core package
pip install agentic-sdlc[cli]

# Hoặc cài đặt tất cả dependencies
pip install agentic-sdlc[all]
```text

### Xác Minh Cài Đặt

```bash
# Kiểm tra version
agentic --version

# Xem help
agentic --help
```text

Output mong đợi:

```
Agentic SDLC CLI v3.0.0
Usage: agentic [OPTIONS] COMMAND [ARGS]...

Options:
  --version  Show version and exit
  --help     Show this message and exit

Commands:
  init    Initialize a new Agentic SDLC project
  config  Manage configuration settings
  run     Run a workflow or agent
  agent   Manage agents
```text

## Cấu Trúc Lệnh

### Cú Pháp Cơ Bản

```bash
agentic [GLOBAL_OPTIONS] COMMAND [COMMAND_OPTIONS] [ARGUMENTS]
```text

Ví dụ:

```bash
agentic --verbose run code-review --file main.py --output report.json
```text

Trong đó:
- `--verbose`: Global option (áp dụng cho tất cả commands)
- `run`: Command chính
- `code-review`: Subcommand hoặc argument
- `--file main.py`: Command option với value
- `--output report.json`: Command option khác

### Global Options

Các options áp dụng cho tất cả commands:

```bash
--version              # Hiển thị version
--help                 # Hiển thị help message
--verbose, -v          # Enable verbose logging
--quiet, -q            # Suppress output
--config PATH          # Chỉ định config file
--log-level LEVEL      # Set log level (DEBUG, INFO, WARNING, ERROR)
```text

## Các Lệnh Chính

### 1. init - Khởi Tạo Project

Tạo một Agentic SDLC project mới với cấu trúc thư mục và config files:

```bash
agentic init my-project
```text

### 2. config - Quản Lý Configuration

Xem và chỉnh sửa configuration settings:

```bash
# Xem tất cả config
agentic config show

# Lấy giá trị của một setting
agentic config get model.default_provider

# Set giá trị mới
agentic config set model.default_provider openai
```text

### 3. run - Chạy Workflows

Thực thi workflows hoặc agents:

```bash
# Chạy workflow
agentic run my-workflow

# Chạy với parameters
agentic run code-review --file src/main.py --output report.json
```text

### 4. agent - Quản Lý Agents

Tạo, liệt kê, và quản lý agents:

```bash
# Liệt kê tất cả agents
agentic agent list

# Tạo agent mới
agentic agent create developer --model gpt-4

# Xem status của agent
agentic agent status agent-id-123
```text

## Workflow Cơ Bản

### Bắt Đầu với Project Mới

```bash
# 1. Khởi tạo project
agentic init my-ai-project
cd my-ai-project

# 2. Cấu hình API keys
agentic config set openai.api_key sk-...

# 3. Tạo agent đầu tiên
agentic agent create my-dev --role Developer --model gpt-4

# 4. Chạy workflow đầu tiên
agentic run hello-world
```text

### Sử Dụng Hàng Ngày

```bash
# Chạy code review
agentic run code-review --file src/api.py

# Chạy automated tests
agentic run test-suite --coverage

# Generate documentation
agentic run doc-generator --output docs/

# Deploy application
agentic run deploy --env production
```text

## Configuration Files

### config.yaml

CLI sử dụng file `config.yaml` trong project directory:

```yaml
# config.yaml
model:
  default_provider: openai
  default_model: gpt-4

openai:
  api_key: ${OPENAI_API_KEY}
  organization: org-xxx

logging:
  level: INFO
  format: json
  output: logs/agentic.log

agents:
  default_max_iterations: 10
  default_timeout: 300
```text

### Environment Variables

CLI hỗ trợ environment variables:

```bash
# Set API key
export OPENAI_API_KEY=sk-...
export ANTHROPIC_API_KEY=sk-ant-...

# Set config file location
export AGENTIC_CONFIG=/path/to/config.yaml

# Set log level
export AGENTIC_LOG_LEVEL=DEBUG
```text

## Output Formats

### JSON Output

```bash
# Output dạng JSON cho scripting
agentic run workflow --output-format json

# Kết hợp với jq để parse
agentic agent list --output-format json | jq '.agents[] | .name'
```text

### Table Output

```bash
# Output dạng table (default)
agentic agent list

# Output:
# ┌──────────────┬────────────┬───────────┬──────────┐
# │ Name         │ Role       │ Model     │ Status   │
# ├──────────────┼────────────┼───────────┼──────────┤
# │ dev-agent    │ Developer  │ gpt-4     │ active   │
# │ test-agent   │ Tester     │ gpt-3.5   │ active   │
# └──────────────┴────────────┴───────────┴──────────┘
```text

### Verbose Output

```bash
# Enable verbose logging
agentic --verbose run workflow

# Output bao gồm:
# - Detailed execution steps
# - API calls và responses
# - Timing information
# - Debug messages
```text

## Error Handling

### Common Errors

```bash
# Error: Config file not found
Error: Configuration file not found at config.yaml
Solution: Run 'agentic init' or specify config with --config

# Error: Invalid API key
Error: Authentication failed. Invalid API key.
Solution: Check your API key with 'agentic config get openai.api_key'

# Error: Agent not found
Error: Agent 'my-agent' not found in registry
Solution: List agents with 'agentic agent list'
```text

### Exit Codes

CLI sử dụng standard exit codes:

- `0`: Success
- `1`: General error
- `2`: Invalid usage (wrong arguments)
- `3`: Configuration error
- `4`: Authentication error
- `5`: Execution error

```bash
# Check exit code trong scripts
agentic run workflow
if [ $? -eq 0 ]; then
    echo "Success!"
else
    echo "Failed with code $?"
fi
```text

## Best Practices

### 1. Sử Dụng Config Files

```bash
# Tốt: Sử dụng config file cho settings phức tạp
agentic --config production.yaml run deploy

# Tránh: Truyền quá nhiều options qua command line
agentic run deploy --api-key xxx --model gpt-4 --timeout 300 ...
```text

### 2. Version Control

```bash
# Commit config files (không bao gồm secrets)
git add config.yaml
git add .agentic/workflows/

# Sử dụng .gitignore cho secrets
echo "config.secrets.yaml" >> .gitignore
```text

### 3. Scripting

```bash
# Sử dụng set -e để stop on errors
#!/bin/bash
set -e

agentic run tests
agentic run build
agentic run deploy
```text

### 4. Logging

```bash
# Enable logging cho debugging
agentic --log-level DEBUG run workflow 2>&1 | tee debug.log

# Hoặc configure trong config.yaml
logging:
  level: DEBUG
  output: logs/agentic.log
```text

### 5. CI/CD Integration

```bash
# GitHub Actions example
- name: Run Agentic SDLC workflow
  run: |
    pip install agentic-sdlc[cli]
    agentic config set openai.api_key ${{ secrets.OPENAI_API_KEY }}
    agentic run ci-workflow --output-format json > results.json
```text

## Shell Completion

### Bash Completion

```bash
# Enable bash completion
eval "$(_AGENTIC_COMPLETE=bash_source agentic)"

# Hoặc add vào ~/.bashrc
echo 'eval "$(_AGENTIC_COMPLETE=bash_source agentic)"' >> ~/.bashrc
```text

### Zsh Completion

```bash
# Enable zsh completion
eval "$(_AGENTIC_COMPLETE=zsh_source agentic)"

# Hoặc add vào ~/.zshrc
echo 'eval "$(_AGENTIC_COMPLETE=zsh_source agentic)"' >> ~/.zshrc
```text

### Fish Completion

```bash
# Enable fish completion
eval (env _AGENTIC_COMPLETE=fish_source agentic)
```

## Tài Liệu Liên Quan

- [Command Reference](commands.md) - Chi tiết về tất cả commands
- [CLI Examples](examples.md) - Ví dụ thực tế sử dụng CLI
- [Configuration Guide](../../getting-started/configuration.md) - Hướng dẫn cấu hình
- [Workflows](../workflows/overview.md) - Xây dựng workflows

## Tóm Tắt

Agentic SDLC CLI cung cấp một cách nhanh chóng và tiện lợi để:

- Khởi tạo và quản lý projects
- Cấu hình settings và API keys
- Chạy workflows và agents
- Tích hợp vào CI/CD pipelines
- Tự động hóa development tasks

CLI đặc biệt hữu ích cho:
- Quick prototyping và testing
- CI/CD automation
- Shell scripting
- Users không muốn viết Python code

Tiếp theo, xem [Command Reference](commands.md) để tìm hiểu chi tiết về từng lệnh.
