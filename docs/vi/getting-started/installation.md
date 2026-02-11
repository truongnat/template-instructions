# Hướng Dẫn Cài Đặt Agentic SDLC

**Phiên bản**: 3.0.0  
**Cập nhật lần cuối**: 11/02/2026


**Phiên bản:** 3.0.0  
**Cập nhật lần cuối:** 2026-02-11

---

## Giới Thiệu

Agentic SDLC là một Python SDK toàn diện cho phát triển phần mềm được hỗ trợ bởi AI. Tài liệu này hướng dẫn chi tiết các bước cài đặt và thiết lập môi trường để bắt đầu sử dụng Agentic SDLC.

### Yêu Cầu Tiên Quyết

Trước khi cài đặt Agentic SDLC, hãy đảm bảo hệ thống của bạn đáp ứng các yêu cầu sau:

- **Python**: Phiên bản 3.10 hoặc cao hơn (3.10, 3.11, 3.12)
- **pip**: Package installer cho Python (thường đi kèm với Python)
- **Hệ điều hành**: Windows, macOS, hoặc Linux
- **Bộ nhớ**: Tối thiểu 4GB RAM (khuyến nghị 8GB hoặc cao hơn)
- **Dung lượng đĩa**: Tối thiểu 2GB dung lượng trống

### Kiểm Tra Phiên Bản Python

Mở terminal hoặc command prompt và chạy lệnh sau để kiểm tra phiên bản Python:

```bash
python --version
# hoặc
python3 --version
```text

Nếu phiên bản Python thấp hơn 3.10, vui lòng cập nhật Python từ [python.org](https://www.python.org/downloads/).

---

## Cài Đặt

Agentic SDLC cung cấp nhiều tùy chọn cài đặt tùy thuộc vào nhu cầu sử dụng của bạn.

### 1. Cài Đặt Core Package (Cơ Bản)

Đây là cách cài đặt cơ bản nhất, bao gồm các tính năng core của Agentic SDLC:

```bash
pip install agentic-sdlc
```text

Package core bao gồm:
- Framework cơ bản cho agents và workflows
- Tích hợp với LLM providers (OpenAI, Anthropic, Ollama)
- Intelligence layer (Learner, Monitor, Reasoner)
- Plugin system
- Configuration management

### 2. Cài Đặt với CLI Tools

Nếu bạn muốn sử dụng command-line interface để tương tác với Agentic SDLC:

```bash
pip install agentic-sdlc[cli]
```text

Tùy chọn này bao gồm:
- Tất cả tính năng của core package
- CLI commands (`agentic`, `agentic-sdlc`, `asdlc`)
- Rich terminal output với formatting đẹp mắt

### 3. Cài Đặt Development Environment

Dành cho developers muốn đóng góp vào dự án hoặc phát triển plugins:

```bash
pip install agentic-sdlc[dev]
```mermaid

Tùy chọn này bao gồm:
- Tất cả tính năng của core package
- Testing frameworks (pytest, hypothesis, pytest-cov)
- Code quality tools (black, ruff, pylint, mypy)
- Documentation tools (sphinx, mkdocs)
- Development utilities (ipython, pre-commit)

### 4. Cài Đặt với Graph Database Support

Nếu bạn cần sử dụng Neo4j graph database cho knowledge management:

```bash
pip install agentic-sdlc[graph]
```text

### 5. Cài Đặt với MCP (Model Context Protocol) Support

Để sử dụng các công cụ tìm kiếm nâng cao như Tavily và Brave Search:

```bash
pip install agentic-sdlc[mcp]
```text

### 6. Cài Đặt với Tools Extension

Bao gồm các công cụ mở rộng cho GitHub integration, Neo4j, và AutoGen:

```bash
pip install agentic-sdlc[tools]
```text

### 7. Cài Đặt Đầy Đủ (All Features)

Để cài đặt tất cả các tính năng và dependencies:

```bash
pip install agentic-sdlc[cli,dev,graph,mcp,tools]
```text

### 8. Cài Đặt từ Source Code

Nếu bạn muốn cài đặt phiên bản development mới nhất từ GitHub:

```bash
# Clone repository
git clone https://github.com/truongnat/agentic-sdlc.git
cd agentic-sdlc

# Cài đặt trong chế độ editable
pip install -e .

# Hoặc cài đặt với development dependencies
pip install -e .[dev]
```text

---

## Thiết Lập Môi Trường

Sau khi cài đặt, bạn cần thiết lập môi trường để sử dụng Agentic SDLC.

### 1. Tạo Virtual Environment (Khuyến Nghị)

Sử dụng virtual environment để tránh xung đột dependencies:

```bash
# Tạo virtual environment
python -m venv venv

# Kích hoạt virtual environment
# Trên Windows:
venv\Scripts\activate

# Trên macOS/Linux:
source venv/bin/activate
```text

### 2. Cấu Hình API Keys

Agentic SDLC cần API keys để tương tác với các LLM providers. Tạo file `.env` trong thư mục dự án:

```bash
# Tạo file .env
touch .env
```text

Thêm các API keys vào file `.env`:

```env
# OpenAI API Key
OPENAI_API_KEY=sk-your-openai-api-key-here

# Anthropic API Key (Claude)
ANTHROPIC_API_KEY=sk-ant-your-anthropic-api-key-here

# Ollama Configuration (nếu sử dụng local LLM)
OLLAMA_BASE_URL=http://localhost:11434

# Neo4j Configuration (nếu sử dụng graph database)
NEO4J_URI=bolt://localhost:7687
NEO4J_USER=neo4j
NEO4J_PASSWORD=your-neo4j-password

# GitHub Token (nếu sử dụng GitHub integration)
GITHUB_TOKEN=ghp_your-github-token-here

# Logging Configuration
LOG_LEVEL=INFO
LOG_FORMAT=json
```text

**Lưu ý bảo mật**: 
- Không commit file `.env` vào version control
- Thêm `.env` vào file `.gitignore`
- Sử dụng environment variables trong production

### 3. Tạo File Cấu Hình

Tạo file `config.yaml` để cấu hình hệ thống:

```bash
# Khởi tạo cấu hình mặc định (nếu đã cài CLI)
agentic init

# Hoặc tạo file config.yaml thủ công
touch config.yaml
```text

Nội dung cơ bản của `config.yaml`:

```yaml
# Agentic SDLC Configuration
version: "3.0.0"

# Model Configuration
models:
  default:
    provider: "openai"
    model_name: "gpt-4"
    temperature: 0.7
    max_tokens: 2000

# Logging Configuration
logging:
  level: "INFO"
  format: "json"
  output: "logs/agentic.log"

# Agent Configuration
agents:
  max_iterations: 10
  timeout: 300  # seconds

# Workflow Configuration
workflows:
  parallel_execution: true
  retry_on_failure: true
  max_retries: 3
```text

---

## Xác Minh Cài Đặt

Sau khi cài đặt và cấu hình, hãy xác minh rằng mọi thứ hoạt động đúng.

### 1. Kiểm Tra Package Installation

```bash
# Kiểm tra phiên bản
python -c "import agentic_sdlc; print(agentic_sdlc.__version__)"
```text

Kết quả mong đợi:
```
3.0.0
```text

### 2. Kiểm Tra CLI Commands (nếu đã cài CLI)

```bash
# Kiểm tra CLI
agentic --version

# Hoặc
agentic-sdlc --version

# Hoặc
asdlc --version
```text

Kết quả mong đợi:
```
Agentic SDLC version 3.0.0
```text

### 3. Chạy Test Script

Tạo file `test_installation.py`:

```python
"""Script kiểm tra cài đặt Agentic SDLC."""

from agentic_sdlc.core.config import ConfigurationManager
from agentic_sdlc.orchestration.agents import create_agent
from agentic_sdlc.orchestration.workflows import WorkflowBuilder

def test_basic_functionality():
    """Kiểm tra các chức năng cơ bản."""
    
    print("✓ Import modules thành công")
    
    # Test configuration
    try:
        config = ConfigurationManager()
        print("✓ Configuration manager hoạt động")
    except Exception as e:
        print(f"✗ Configuration error: {e}")
        return False
    
    # Test agent creation
    try:
        agent = create_agent(
            name="test_agent",
            role="developer",
            model_name="gpt-4"
        )
        print("✓ Agent creation hoạt động")
    except Exception as e:
        print(f"✗ Agent creation error: {e}")
        return False
    
    # Test workflow builder
    try:
        workflow = WorkflowBuilder(name="test_workflow")
        print("✓ Workflow builder hoạt động")
    except Exception as e:
        print(f"✗ Workflow builder error: {e}")
        return False
    
    print("\n✓ Tất cả kiểm tra cơ bản đều thành công!")
    return True

if __name__ == "__main__":
    test_basic_functionality()
```text

Chạy script:

```bash
python test_installation.py
```text

### 4. Kiểm Tra LLM Connection

Tạo file `test_llm.py`:

```python
"""Script kiểm tra kết nối với LLM providers."""

import os
from agentic_sdlc.orchestration.api_model_management import create_model_client, ModelConfig

def test_openai_connection():
    """Kiểm tra kết nối OpenAI."""
    if not os.getenv("OPENAI_API_KEY"):
        print("⚠ OPENAI_API_KEY không được cấu hình")
        return False
    
    try:
        config = ModelConfig(
            provider="openai",
            model_name="gpt-3.5-turbo",
            api_key=os.getenv("OPENAI_API_KEY")
        )
        client = create_model_client(config)
        print("✓ OpenAI connection thành công")
        return True
    except Exception as e:
        print(f"✗ OpenAI connection error: {e}")
        return False

def test_anthropic_connection():
    """Kiểm tra kết nối Anthropic."""
    if not os.getenv("ANTHROPIC_API_KEY"):
        print("⚠ ANTHROPIC_API_KEY không được cấu hình")
        return False
    
    try:
        config = ModelConfig(
            provider="anthropic",
            model_name="claude-3-sonnet-20240229",
            api_key=os.getenv("ANTHROPIC_API_KEY")
        )
        client = create_model_client(config)
        print("✓ Anthropic connection thành công")
        return True
    except Exception as e:
        print(f"✗ Anthropic connection error: {e}")
        return False

if __name__ == "__main__":
    print("Kiểm tra kết nối LLM providers...\n")
    test_openai_connection()
    test_anthropic_connection()
```text

Chạy script:

```bash
python test_llm.py
```text

---

## Troubleshooting (Xử Lý Sự Cố)

### Lỗi 1: ModuleNotFoundError

**Triệu chứng**:
```
ModuleNotFoundError: No module named 'agentic_sdlc'
```text

**Nguyên nhân**: Package chưa được cài đặt hoặc virtual environment chưa được kích hoạt.

**Giải pháp**:
```bash
# Kiểm tra virtual environment
which python  # macOS/Linux
where python  # Windows

# Kích hoạt virtual environment nếu cần
source venv/bin/activate  # macOS/Linux
venv\Scripts\activate     # Windows

# Cài đặt lại package
pip install agentic-sdlc
```text

### Lỗi 2: ImportError với Dependencies

**Triệu chứng**:
```
ImportError: cannot import name 'X' from 'Y'
```text

**Nguyên nhân**: Dependencies không tương thích hoặc thiếu.

**Giải pháp**:
```bash
# Cập nhật pip
pip install --upgrade pip

# Cài đặt lại với dependencies đầy đủ
pip uninstall agentic-sdlc
pip install agentic-sdlc[cli,dev]

# Hoặc cài đặt từ requirements.txt
pip install -r requirements.txt
```text

### Lỗi 3: API Key Errors

**Triệu chứng**:
```
AuthenticationError: Invalid API key
```text

**Nguyên nhân**: API key không hợp lệ hoặc chưa được cấu hình.

**Giải pháp**:
```bash
# Kiểm tra file .env
cat .env

# Đảm bảo API keys được set đúng
export OPENAI_API_KEY="sk-your-key-here"  # macOS/Linux
set OPENAI_API_KEY=sk-your-key-here       # Windows

# Hoặc thêm vào file .env
echo "OPENAI_API_KEY=sk-your-key-here" >> .env
```text

### Lỗi 4: Permission Errors

**Triệu chứng**:
```
PermissionError: [Errno 13] Permission denied
```text

**Nguyên nhân**: Không có quyền ghi vào thư mục.

**Giải pháp**:
```bash
# Sử dụng --user flag
pip install --user agentic-sdlc

# Hoặc thay đổi quyền thư mục
chmod -R 755 /path/to/directory

# Hoặc sử dụng sudo (không khuyến nghị)
sudo pip install agentic-sdlc
```text

### Lỗi 5: Version Conflicts

**Triệu chứng**:
```
ERROR: pip's dependency resolver does not currently take into account all the packages that are installed
```text

**Nguyên nhân**: Xung đột phiên bản giữa các packages.

**Giải pháp**:
```bash
# Tạo virtual environment mới
python -m venv fresh_venv
source fresh_venv/bin/activate

# Cài đặt trong môi trường sạch
pip install agentic-sdlc

# Hoặc sử dụng pip-tools để resolve dependencies
pip install pip-tools
pip-compile requirements.in
pip-sync requirements.txt
```text

### Lỗi 6: SSL Certificate Errors

**Triệu chứng**:
```
SSLError: [SSL: CERTIFICATE_VERIFY_FAILED]
```text

**Nguyên nhân**: Vấn đề với SSL certificates.

**Giải pháp**:
```bash
# Cập nhật certificates
pip install --upgrade certifi

# Hoặc tạm thời bỏ qua SSL verification (không khuyến nghị cho production)
pip install --trusted-host pypi.org --trusted-host files.pythonhosted.org agentic-sdlc
```text

### Lỗi 7: Memory Errors

**Triệu chứng**:
```
MemoryError: Unable to allocate array
```text

**Nguyên nhân**: Không đủ RAM cho các models lớn.

**Giải pháp**:
- Sử dụng models nhỏ hơn (gpt-3.5-turbo thay vì gpt-4)
- Tăng swap space
- Giảm batch size trong configuration
- Sử dụng máy có RAM cao hơn

### Lỗi 8: Network Timeout

**Triệu chứng**:
```
TimeoutError: Request timed out
```text

**Nguyên nhân**: Kết nối mạng chậm hoặc không ổn định.

**Giải pháp**:
```bash
# Tăng timeout trong pip
pip install --timeout=300 agentic-sdlc

# Hoặc cấu hình trong config.yaml
# timeout: 600  # seconds
```text

### Lỗi 9: Python Version Incompatibility

**Triệu chứng**:
```
ERROR: Package requires Python '>=3.10' but the running Python is 3.9
```text

**Nguyên nhân**: Phiên bản Python quá cũ.

**Giải pháp**:
```bash
# Cài đặt Python 3.10 hoặc cao hơn
# Trên Ubuntu/Debian:
sudo apt update
sudo apt install python3.10

# Trên macOS với Homebrew:
brew install python@3.10

# Tạo virtual environment với Python 3.10
python3.10 -m venv venv
source venv/bin/activate
pip install agentic-sdlc
```text

### Lỗi 10: Configuration File Not Found

**Triệu chứng**:
```
FileNotFoundError: config.yaml not found
```text

**Nguyên nhân**: File cấu hình không tồn tại hoặc ở sai vị trí.

**Giải pháp**:
```bash
# Tạo file config.yaml mặc định
agentic init

# Hoặc chỉ định đường dẫn config
export AGENTIC_CONFIG_PATH=/path/to/config.yaml

# Hoặc tạo file thủ công
cat > config.yaml << EOF
version: "3.0.0"
models:
  default:
    provider: "openai"
    model_name: "gpt-4"
EOF
```

---

## Các Bước Tiếp Theo

Sau khi cài đặt thành công, bạn có thể:

1. **Đọc hướng dẫn cấu hình**: [Configuration Guide](configuration.md)
2. **Tạo workflow đầu tiên**: [First Workflow Guide](first-workflow.md)
3. **Tìm hiểu về agents**: [Agents Guide](../guides/agents/overview.md)
4. **Xem các use cases**: [Use Cases](../use-cases/README.md)
5. **Khám phá API reference**: [API Reference](../api-reference/README.md)

---

## Hỗ Trợ

Nếu bạn gặp vấn đề không được đề cập trong tài liệu này:

- **GitHub Issues**: [https://github.com/truongnat/agentic-sdlc/issues](https://github.com/truongnat/agentic-sdlc/issues)
- **Documentation**: [https://github.com/truongnat/agentic-sdlc#readme](https://github.com/truongnat/agentic-sdlc#readme)
- **Email**: truongnat@gmail.com

---

*Tài liệu này là một phần của Agentic SDLC v3.0.0*
