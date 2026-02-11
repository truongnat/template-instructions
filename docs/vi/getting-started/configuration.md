# Hướng Dẫn Cấu Hình Agentic SDLC

**Phiên bản**: 3.0.0  
**Cập nhật lần cuối**: 11/02/2026


**Phiên bản:** 3.0.0  
**Cập nhật lần cuối:** 2026-02-11

---

## Giới Thiệu

Tài liệu này hướng dẫn chi tiết cách cấu hình Agentic SDLC để phù hợp với nhu cầu dự án của bạn. Hệ thống hỗ trợ nhiều phương thức cấu hình linh hoạt: file YAML, environment variables, và programmatic configuration.

### Yêu Cầu Tiên Quyết

- Đã cài đặt Agentic SDLC (xem [Installation Guide](installation.md))
- Hiểu biết cơ bản về YAML format
- API keys cho các LLM providers bạn muốn sử dụng

---

## Cấu Trúc File config.yaml

File `config.yaml` là phương thức cấu hình chính cho Agentic SDLC. Dưới đây là cấu trúc đầy đủ với tất cả các tham số có thể cấu hình.

### Cấu Trúc Cơ Bản

```yaml
# Agentic SDLC Configuration File
version: "3.0.0"

# Model Configuration
models:
  default:
    provider: "openai"
    model_name: "gpt-4"
    api_key: "${OPENAI_API_KEY}"  # Sử dụng environment variable
    temperature: 0.7
    max_tokens: 2000
    timeout: 60

# Logging Configuration
logging:
  level: "INFO"
  format: "json"
  output: "logs/agentic.log"
  rotation: "daily"
  retention: 30  # days

# Agent Configuration
agents:
  max_iterations: 10
  timeout: 300  # seconds
  retry_on_failure: true
  max_retries: 3

# Workflow Configuration
workflows:
  parallel_execution: true
  max_parallel_tasks: 5
  retry_on_failure: true
  max_retries: 3
  timeout: 600  # seconds

# Intelligence Configuration
intelligence:
  learning:
    enabled: true
    storage_path: "data/learning"
  monitoring:
    enabled: true
    metrics_interval: 60  # seconds
  reasoning:
    enabled: true
    complexity_threshold: 0.7

# Plugin Configuration
plugins:
  enabled: true
  plugin_dir: "plugins"
  auto_load: true

# Database Configuration (Optional)
database:
  neo4j:
    uri: "${NEO4J_URI}"
    user: "${NEO4J_USER}"
    password: "${NEO4J_PASSWORD}"
    database: "neo4j"
```text

### Các Tham Số Quan Trọng

#### 1. Model Configuration

Cấu hình cho các LLM providers:

```yaml
models:
  # Model mặc định
  default:
    provider: "openai"
    model_name: "gpt-4"
    api_key: "${OPENAI_API_KEY}"
    temperature: 0.7
    max_tokens: 2000
    timeout: 60
    
  # Model cho code generation
  code_generator:
    provider: "openai"
    model_name: "gpt-4"
    temperature: 0.2  # Thấp hơn cho code generation
    max_tokens: 4000
    
  # Model cho analysis
  analyzer:
    provider: "anthropic"
    model_name: "claude-3-opus-20240229"
    temperature: 0.5
    max_tokens: 3000
```text

**Tham số**:
- `provider`: LLM provider ("openai", "anthropic", "ollama")
- `model_name`: Tên model cụ thể
- `api_key`: API key (khuyến nghị dùng environment variable)
- `temperature`: Độ sáng tạo (0.0-1.0)
- `max_tokens`: Số tokens tối đa trong response
- `timeout`: Timeout cho API calls (seconds)

#### 2. Logging Configuration

Cấu hình hệ thống logging:

```yaml
logging:
  level: "INFO"  # DEBUG, INFO, WARNING, ERROR, CRITICAL
  format: "json"  # json, text
  output: "logs/agentic.log"
  rotation: "daily"  # daily, weekly, size
  retention: 30  # days
  max_file_size: "100MB"  # Nếu rotation = size
  console_output: true
  file_output: true
```text

**Log Levels**:
- `DEBUG`: Thông tin chi tiết cho debugging
- `INFO`: Thông tin chung về hoạt động
- `WARNING`: Cảnh báo về vấn đề tiềm ẩn
- `ERROR`: Lỗi không làm dừng hệ thống
- `CRITICAL`: Lỗi nghiêm trọng

#### 3. Agent Configuration

Cấu hình cho agents:

```yaml
agents:
  max_iterations: 10
  timeout: 300  # seconds
  retry_on_failure: true
  max_retries: 3
  retry_delay: 5  # seconds
  
  # Agent-specific settings
  developer:
    model: "code_generator"
    max_iterations: 15
  
  tester:
    model: "analyzer"
    max_iterations: 8
```text

#### 4. Workflow Configuration

Cấu hình cho workflows:

```yaml
workflows:
  parallel_execution: true
  max_parallel_tasks: 5
  retry_on_failure: true
  max_retries: 3
  timeout: 600  # seconds
  checkpoint_enabled: true
  checkpoint_interval: 60  # seconds
```text

---

## Cấu Hình LLM Providers

### 1. OpenAI Configuration

#### Cấu hình trong config.yaml

```yaml
models:
  openai_gpt4:
    provider: "openai"
    model_name: "gpt-4"
    api_key: "${OPENAI_API_KEY}"
    temperature: 0.7
    max_tokens: 2000
    top_p: 1.0
    frequency_penalty: 0.0
    presence_penalty: 0.0
    
  openai_gpt35:
    provider: "openai"
    model_name: "gpt-3.5-turbo"
    api_key: "${OPENAI_API_KEY}"
    temperature: 0.7
    max_tokens: 1500
```text

#### Environment Variables

```bash
# .env file
OPENAI_API_KEY=sk-your-openai-api-key-here
OPENAI_ORG_ID=org-your-org-id  # Optional
```text

#### Các Models OpenAI Được Hỗ Trợ

- `gpt-4`: Model mạnh nhất, tốt cho tasks phức tạp
- `gpt-4-turbo`: Nhanh hơn và rẻ hơn GPT-4
- `gpt-3.5-turbo`: Cân bằng giữa hiệu suất và chi phí
- `gpt-3.5-turbo-16k`: Context window lớn hơn

### 2. Anthropic (Claude) Configuration

#### Cấu hình trong config.yaml

```yaml
models:
  claude_opus:
    provider: "anthropic"
    model_name: "claude-3-opus-20240229"
    api_key: "${ANTHROPIC_API_KEY}"
    temperature: 0.7
    max_tokens: 4000
    
  claude_sonnet:
    provider: "anthropic"
    model_name: "claude-3-sonnet-20240229"
    api_key: "${ANTHROPIC_API_KEY}"
    temperature: 0.7
    max_tokens: 3000
    
  claude_haiku:
    provider: "anthropic"
    model_name: "claude-3-haiku-20240307"
    api_key: "${ANTHROPIC_API_KEY}"
    temperature: 0.7
    max_tokens: 2000
```text

#### Environment Variables

```bash
# .env file
ANTHROPIC_API_KEY=sk-ant-your-anthropic-api-key-here
```text

#### Các Models Claude Được Hỗ Trợ

- `claude-3-opus`: Model mạnh nhất, tốt nhất cho tasks phức tạp
- `claude-3-sonnet`: Cân bằng giữa hiệu suất và chi phí
- `claude-3-haiku`: Nhanh nhất và rẻ nhất

### 3. Ollama (Local LLM) Configuration

#### Cấu hình trong config.yaml

```yaml
models:
  ollama_llama2:
    provider: "ollama"
    model_name: "llama2"
    base_url: "${OLLAMA_BASE_URL}"
    temperature: 0.7
    max_tokens: 2000
    
  ollama_codellama:
    provider: "ollama"
    model_name: "codellama"
    base_url: "http://localhost:11434"
    temperature: 0.2
    max_tokens: 4000
    
  ollama_mistral:
    provider: "ollama"
    model_name: "mistral"
    base_url: "http://localhost:11434"
    temperature: 0.7
    max_tokens: 3000
```text

#### Environment Variables

```bash
# .env file
OLLAMA_BASE_URL=http://localhost:11434
```text

#### Cài Đặt Ollama

```bash
# Cài đặt Ollama
curl https://ollama.ai/install.sh | sh

# Pull models
ollama pull llama2
ollama pull codellama
ollama pull mistral

# Chạy Ollama server
ollama serve
```text

#### Các Models Ollama Phổ Biến

- `llama2`: General purpose model
- `codellama`: Chuyên cho code generation
- `mistral`: Hiệu suất cao, context window lớn
- `phi`: Model nhỏ, nhanh
- `neural-chat`: Tốt cho conversation

---

## Cấu Hình Logging

### 1. JSON Format Logging

```yaml
logging:
  level: "INFO"
  format: "json"
  output: "logs/agentic.log"
  
  # JSON-specific settings
  json_indent: 2
  include_timestamp: true
  include_level: true
  include_logger_name: true
  include_thread_name: false
```text

Ví dụ log output:

```json
{
  "timestamp": "2026-02-11T10:30:45.123Z",
  "level": "INFO",
  "logger": "agentic_sdlc.orchestration.agents",
  "message": "Agent 'developer' started task execution",
  "context": {
    "agent_id": "dev-001",
    "task_id": "task-123"
  }
}
```text

### 2. Text Format Logging

```yaml
logging:
  level: "INFO"
  format: "text"
  output: "logs/agentic.log"
  
  # Text-specific settings
  pattern: "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
  date_format: "%Y-%m-%d %H:%M:%S"
```text

Ví dụ log output:

```
2026-02-11 10:30:45 - agentic_sdlc.orchestration.agents - INFO - Agent 'developer' started task execution
```text

### 3. Log Rotation

```yaml
logging:
  rotation: "daily"  # daily, weekly, size
  retention: 30  # days
  max_file_size: "100MB"  # Nếu rotation = size
  backup_count: 10  # Số file backup giữ lại
```text

### 4. Multiple Log Outputs

```yaml
logging:
  outputs:
    - type: "file"
      path: "logs/agentic.log"
      level: "INFO"
      format: "json"
      
    - type: "file"
      path: "logs/errors.log"
      level: "ERROR"
      format: "text"
      
    - type: "console"
      level: "WARNING"
      format: "text"
      colored: true
```text

---

## Loading Configuration

### 1. Load từ File

#### Python Code

```python
from agentic_sdlc.core.config import ConfigurationManager

# Load từ file mặc định (config.yaml)
config = ConfigurationManager()

# Load từ file cụ thể
config = ConfigurationManager(config_path="path/to/config.yaml")

# Truy cập configuration
model_config = config.get_model_config("default")
logging_config = config.get_logging_config()
agent_config = config.get_agent_config()
```text

#### Ví Dụ Đầy Đủ

```python
"""Ví dụ load configuration từ file."""

from agentic_sdlc.core.config import ConfigurationManager
from agentic_sdlc.orchestration.api_model_management import create_model_client

def main():
    # Load configuration
    config = ConfigurationManager(config_path="config.yaml")
    
    # Get model configuration
    model_config = config.get_model_config("default")
    print(f"Using model: {model_config.model_name}")
    print(f"Provider: {model_config.provider}")
    print(f"Temperature: {model_config.temperature}")
    
    # Create model client
    client = create_model_client(model_config)
    
    # Get logging configuration
    logging_config = config.get_logging_config()
    print(f"Log level: {logging_config.level}")
    print(f"Log output: {logging_config.output}")
    
    # Get agent configuration
    agent_config = config.get_agent_config()
    print(f"Max iterations: {agent_config.max_iterations}")
    print(f"Timeout: {agent_config.timeout}")

if __name__ == "__main__":
    main()
```text

### 2. Load từ Environment Variables

#### Environment Variables

```bash
# .env file

# Model Configuration
AGENTIC_MODEL_PROVIDER=openai
AGENTIC_MODEL_NAME=gpt-4
AGENTIC_MODEL_TEMPERATURE=0.7
AGENTIC_MODEL_MAX_TOKENS=2000

# Logging Configuration
AGENTIC_LOG_LEVEL=INFO
AGENTIC_LOG_FORMAT=json
AGENTIC_LOG_OUTPUT=logs/agentic.log

# Agent Configuration
AGENTIC_AGENT_MAX_ITERATIONS=10
AGENTIC_AGENT_TIMEOUT=300
```text

#### Python Code

```python
"""Ví dụ load configuration từ environment variables."""

import os
from dotenv import load_dotenv
from agentic_sdlc.core.config import ConfigurationManager, ModelConfig

def main():
    # Load environment variables
    load_dotenv()
    
    # Create configuration từ environment variables
    config = ConfigurationManager.from_env()
    
    # Hoặc tạo ModelConfig trực tiếp
    model_config = ModelConfig(
        provider=os.getenv("AGENTIC_MODEL_PROVIDER", "openai"),
        model_name=os.getenv("AGENTIC_MODEL_NAME", "gpt-4"),
        api_key=os.getenv("OPENAI_API_KEY"),
        temperature=float(os.getenv("AGENTIC_MODEL_TEMPERATURE", "0.7")),
        max_tokens=int(os.getenv("AGENTIC_MODEL_MAX_TOKENS", "2000"))
    )
    
    print(f"Model: {model_config.model_name}")
    print(f"Provider: {model_config.provider}")

if __name__ == "__main__":
    main()
```text

### 3. Programmatic Configuration

#### Python Code

```python
"""Ví dụ cấu hình programmatically."""

from agentic_sdlc.core.config import (
    ConfigurationManager,
    ModelConfig,
    LoggingConfig,
    AgentConfig,
    WorkflowConfig
)

def create_custom_config():
    """Tạo configuration programmatically."""
    
    # Model configuration
    model_config = ModelConfig(
        provider="openai",
        model_name="gpt-4",
        api_key="sk-your-api-key",
        temperature=0.7,
        max_tokens=2000,
        timeout=60
    )
    
    # Logging configuration
    logging_config = LoggingConfig(
        level="INFO",
        format="json",
        output="logs/agentic.log",
        rotation="daily",
        retention=30
    )
    
    # Agent configuration
    agent_config = AgentConfig(
        max_iterations=10,
        timeout=300,
        retry_on_failure=True,
        max_retries=3
    )
    
    # Workflow configuration
    workflow_config = WorkflowConfig(
        parallel_execution=True,
        max_parallel_tasks=5,
        retry_on_failure=True,
        max_retries=3,
        timeout=600
    )
    
    # Create configuration manager
    config = ConfigurationManager(
        model_config=model_config,
        logging_config=logging_config,
        agent_config=agent_config,
        workflow_config=workflow_config
    )
    
    return config

def main():
    # Tạo configuration
    config = create_custom_config()
    
    # Sử dụng configuration
    model_config = config.get_model_config("default")
    print(f"Model: {model_config.model_name}")
    
    # Update configuration dynamically
    config.update_model_config("default", temperature=0.5)
    
    # Save configuration to file
    config.save("custom_config.yaml")

if __name__ == "__main__":
    main()
```text

### 4. Hybrid Configuration (File + Environment Variables)

```python
"""Ví dụ kết hợp file và environment variables."""

import os
from dotenv import load_dotenv
from agentic_sdlc.core.config import ConfigurationManager

def main():
    # Load environment variables
    load_dotenv()
    
    # Load base configuration từ file
    config = ConfigurationManager(config_path="config.yaml")
    
    # Override với environment variables
    if os.getenv("OPENAI_API_KEY"):
        config.update_model_config(
            "default",
            api_key=os.getenv("OPENAI_API_KEY")
        )
    
    if os.getenv("AGENTIC_LOG_LEVEL"):
        config.update_logging_config(
            level=os.getenv("AGENTIC_LOG_LEVEL")
        )
    
    # Sử dụng configuration
    model_config = config.get_model_config("default")
    print(f"Model: {model_config.model_name}")
    print(f"API Key: {'***' + model_config.api_key[-4:]}")

if __name__ == "__main__":
    main()
```text

---

## Validation và Error Handling

### 1. Configuration Validation

```python
"""Ví dụ validation configuration."""

from agentic_sdlc.core.config import ConfigurationManager, ValidationError

def validate_config():
    """Validate configuration trước khi sử dụng."""
    
    try:
        # Load configuration
        config = ConfigurationManager(config_path="config.yaml")
        
        # Validate configuration
        validation_result = config.validate()
        
        if validation_result.is_valid:
            print("✓ Configuration hợp lệ")
        else:
            print("✗ Configuration không hợp lệ:")
            for error in validation_result.errors:
                print(f"  - {error}")
                
    except ValidationError as e:
        print(f"Validation error: {e}")
    except FileNotFoundError:
        print("Config file không tồn tại")
    except Exception as e:
        print(f"Unexpected error: {e}")

if __name__ == "__main__":
    validate_config()
```text

### 2. Error Handling

```python
"""Ví dụ error handling cho configuration."""

from agentic_sdlc.core.config import (
    ConfigurationManager,
    ConfigurationError,
    ValidationError
)

def load_config_with_error_handling():
    """Load configuration với error handling."""
    
    try:
        # Thử load configuration
        config = ConfigurationManager(config_path="config.yaml")
        return config
        
    except FileNotFoundError:
        print("Config file không tồn tại, sử dụng default configuration")
        return ConfigurationManager.default()
        
    except ValidationError as e:
        print(f"Configuration không hợp lệ: {e}")
        print("Sử dụng default configuration")
        return ConfigurationManager.default()
        
    except ConfigurationError as e:
        print(f"Configuration error: {e}")
        raise
        
    except Exception as e:
        print(f"Unexpected error: {e}")
        raise

def main():
    config = load_config_with_error_handling()
    
    # Sử dụng configuration
    model_config = config.get_model_config("default")
    print(f"Using model: {model_config.model_name}")

if __name__ == "__main__":
    main()
```text

### 3. Graceful Degradation

```python
"""Ví dụ graceful degradation khi configuration thiếu."""

from agentic_sdlc.core.config import ConfigurationManager

def get_config_with_fallback():
    """Get configuration với fallback values."""
    
    try:
        config = ConfigurationManager(config_path="config.yaml")
    except Exception:
        # Fallback to default
        config = ConfigurationManager.default()
    
    # Get model config với fallback
    try:
        model_config = config.get_model_config("default")
    except KeyError:
        # Fallback to basic OpenAI config
        from agentic_sdlc.core.config import ModelConfig
        model_config = ModelConfig(
            provider="openai",
            model_name="gpt-3.5-turbo",
            temperature=0.7,
            max_tokens=1500
        )
    
    return config, model_config

def main():
    config, model_config = get_config_with_fallback()
    print(f"Using model: {model_config.model_name}")

if __name__ == "__main__":
    main()
```text

---

## Best Practices

### 1. Security Best Practices

```yaml
# ✓ ĐÚNG: Sử dụng environment variables cho sensitive data
models:
  default:
    api_key: "${OPENAI_API_KEY}"

# ✗ SAI: Hardcode API keys trong config file
models:
  default:
    api_key: "sk-actual-api-key-here"  # KHÔNG BAO GIỜ LÀM NHƯ VẦY!
```text

**Khuyến nghị**:
- Luôn sử dụng environment variables cho API keys
- Thêm `config.yaml` vào `.gitignore` nếu chứa sensitive data
- Sử dụng secrets management tools trong production (AWS Secrets Manager, HashiCorp Vault)
- Rotate API keys định kỳ

### 2. Environment-Specific Configuration

```bash
# Development
config.dev.yaml

# Staging
config.staging.yaml

# Production
config.prod.yaml
```text

```python
"""Load configuration theo environment."""

import os
from agentic_sdlc.core.config import ConfigurationManager

def load_config():
    env = os.getenv("ENVIRONMENT", "dev")
    config_file = f"config.{env}.yaml"
    return ConfigurationManager(config_path=config_file)
```text

### 3. Configuration Versioning

```yaml
# Luôn include version trong config
version: "3.0.0"

# Metadata
metadata:
  created_at: "2026-02-11"
  updated_at: "2026-02-11"
  author: "team@example.com"
  description: "Production configuration for Agentic SDLC"
```text

### 4. Documentation trong Config

```yaml
# Model Configuration
# Supported providers: openai, anthropic, ollama
# Temperature range: 0.0 (deterministic) to 1.0 (creative)
models:
  default:
    provider: "openai"  # LLM provider
    model_name: "gpt-4"  # Model identifier
    temperature: 0.7  # Creativity level
    max_tokens: 2000  # Maximum response length
```text

### 5. Validation Rules

```python
"""Custom validation rules."""

from agentic_sdlc.core.config import ConfigurationManager

def validate_production_config(config: ConfigurationManager) -> bool:
    """Validate configuration cho production environment."""
    
    # Check API keys are set
    model_config = config.get_model_config("default")
    if not model_config.api_key or model_config.api_key.startswith("${"):
        print("ERROR: API key chưa được set")
        return False
    
    # Check logging is configured
    logging_config = config.get_logging_config()
    if logging_config.level == "DEBUG":
        print("WARNING: Log level là DEBUG trong production")
    
    # Check timeout values
    agent_config = config.get_agent_config()
    if agent_config.timeout < 60:
        print("WARNING: Agent timeout quá thấp")
    
    return True
```text

---

## Troubleshooting

### Lỗi 1: Configuration File Not Found

```
FileNotFoundError: config.yaml not found
```text

**Giải pháp**:
```bash
# Tạo config file mặc định
agentic init

# Hoặc chỉ định đường dẫn
export AGENTIC_CONFIG_PATH=/path/to/config.yaml
```text

### Lỗi 2: Invalid YAML Syntax

```
yaml.scanner.ScannerError: mapping values are not allowed here
```text

**Giải pháp**:
- Kiểm tra indentation (phải dùng spaces, không dùng tabs)
- Validate YAML syntax với online tools
- Sử dụng YAML linter

### Lỗi 3: Environment Variable Not Resolved

```
ValueError: Environment variable OPENAI_API_KEY not found
```text

**Giải pháp**:
```bash
# Set environment variable
export OPENAI_API_KEY=sk-your-key

# Hoặc load từ .env file
python -c "from dotenv import load_dotenv; load_dotenv()"
```text

### Lỗi 4: Invalid Model Configuration

```
ValidationError: Invalid model provider: xyz
```

**Giải pháp**:
- Kiểm tra provider name (phải là "openai", "anthropic", hoặc "ollama")
- Kiểm tra model name có hợp lệ với provider
- Xem documentation của provider

---

## Tài Liệu Liên Quan

- [Installation Guide](installation.md)
- [First Workflow Guide](first-workflow.md)
- [Model Client API Reference](../api-reference/orchestration/model-client.md)
- [Configuration API Reference](../api-reference/core/config.md)

---

*Tài liệu này là một phần của Agentic SDLC v3.0.0*
