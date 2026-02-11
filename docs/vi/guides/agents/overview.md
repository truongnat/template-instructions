# Tổng Quan về Agents

**Phiên bản**: 3.0.0  
**Cập nhật lần cuối**: 11/02/2026


## Giới Thiệu

Agent (Tác nhân) là một thực thể AI chuyên biệt trong Agentic SDLC, được thiết kế để thực hiện các nhiệm vụ cụ thể trong quy trình phát triển phần mềm. Mỗi agent hoạt động như một thành viên độc lập trong team, có khả năng tự động hóa các công việc phức tạp, học hỏi từ kinh nghiệm, và cộng tác với các agents khác.

## Khái Niệm Cơ Bản

### Agent là gì?

Agent trong Agentic SDLC là một đơn vị thực thi tự động với các đặc điểm sau:

- **Chuyên môn hóa**: Mỗi agent có một vai trò (role) cụ thể như developer, tester, architect
- **Tự động**: Agent có thể thực hiện tasks mà không cần can thiệp thủ công liên tục
- **Thông minh**: Sử dụng Large Language Models (LLMs) để hiểu và xử lý yêu cầu
- **Cộng tác**: Có thể làm việc với các agents khác trong một workflow
- **Có trạng thái**: Duy trì context và metadata qua các lần thực thi

### Cấu Trúc Agent

Mỗi agent trong hệ thống bao gồm các thành phần chính:

```python
@dataclass
class Agent:
    name: str                    # Tên định danh của agent
    role: str                    # Vai trò/chức năng của agent
    model_name: str              # LLM model được sử dụng (vd: gpt-4, claude-3)
    system_prompt: Optional[str] # Hướng dẫn hệ thống cho agent
    tools: List[str]             # Danh sách công cụ agent có thể sử dụng
    max_iterations: int          # Số lần thử tối đa cho một task
    id: str                      # ID duy nhất của agent
    metadata: Dict[str, Any]     # Thông tin bổ sung
```text

## Đặc Điểm Chính

### 1. Chuyên Môn Hóa Theo Vai Trò

Mỗi agent được thiết kế cho một vai trò cụ thể trong SDLC:

- **Business Analyst (BA)**: Phân tích yêu cầu nghiệp vụ
- **Project Manager (PM)**: Quản lý dự án và lập kế hoạch
- **Software Architect (SA)**: Thiết kế kiến trúc hệ thống
- **Developer**: Viết và implement code
- **Tester**: Thực hiện testing và quality assurance
- **Researcher**: Nghiên cứu và đánh giá công nghệ

### 2. Model Configuration

Agents sử dụng các LLM models khác nhau tùy theo yêu cầu:

```python
# Agent với GPT-4 cho tasks phức tạp
architect_agent = Agent(
    name="system-architect",
    role="Software Architect",
    model_name="gpt-4-turbo"
)

# Agent với model nhẹ hơn cho tasks đơn giản
code_formatter = Agent(
    name="formatter",
    role="Code Formatter",
    model_name="gpt-3.5-turbo"
)
```text

### 3. System Prompts

System prompt định nghĩa hành vi và expertise của agent:

```python
agent = Agent(
    name="code-reviewer",
    role="Code Reviewer",
    model_name="gpt-4",
    system_prompt="""Bạn là một code reviewer chuyên nghiệp.
    Nhiệm vụ của bạn là:
    - Kiểm tra code quality và best practices
    - Phát hiện bugs và security issues
    - Đề xuất improvements
    - Đảm bảo code tuân thủ coding standards
    """
)
```text

### 4. Tools và Capabilities

Agents có thể được trang bị các tools để mở rộng khả năng:

```python
agent = Agent(
    name="dev-agent",
    role="Developer",
    model_name="gpt-4",
    tools=[
        "code_execution",      # Chạy code
        "file_operations",     # Đọc/ghi files
        "git_operations",      # Git commands
        "api_calls"           # Gọi external APIs
    ]
)
```text

## Lifecycle của Agent

### 1. Tạo và Đăng Ký

```python
from agentic_sdlc import create_agent, get_agent_registry

# Tạo agent mới
agent = create_agent(
    name="my-agent",
    role="Developer",
    model_name="gpt-4"
)

# Agent tự động được đăng ký vào registry
registry = get_agent_registry()
```text

### 2. Cấu Hình

```python
# Cấu hình system prompt
agent.system_prompt = "You are an expert Python developer..."

# Thêm tools
agent.tools.extend(["pytest", "black", "mypy"])

# Cập nhật metadata
agent.metadata["team"] = "backend"
agent.metadata["expertise"] = ["python", "fastapi", "postgresql"]
```text

### 3. Thực Thi

```python
# Agent thực hiện task trong workflow
from agentic_sdlc import Workflow, WorkflowStep

workflow = Workflow(name="code-review-workflow")
workflow.add_step(
    WorkflowStep(
        name="review-code",
        agent=agent,
        action="review",
        parameters={"file": "src/main.py"}
    )
)
```text

### 4. Monitoring và Logging

```python
# Theo dõi hoạt động của agent
from agentic_sdlc.intelligence import Monitor

monitor = Monitor()
monitor.record_metric(
    agent_id=agent.id,
    metric_name="tasks_completed",
    value=1
)
```text

## Agent Registry

AgentRegistry quản lý tất cả agents trong hệ thống:

```python
from agentic_sdlc import get_agent_registry

registry = get_agent_registry()

# Lấy agent theo ID
agent = registry.get_agent("agent-id-123")

# Lấy agent theo tên
agent = registry.get_agent_by_name("my-agent")

# Liệt kê tất cả agents
all_agents = registry.list_agents()

# Xóa agent
registry.remove_agent("agent-id-123")
```text

## Best Practices

### 1. Đặt Tên Agent Rõ Ràng

```python
# Tốt: Tên mô tả rõ chức năng
agent = create_agent(
    name="python-code-reviewer",
    role="Code Reviewer"
)

# Tránh: Tên chung chung
agent = create_agent(
    name="agent1",
    role="Agent"
)
```text

### 2. Chọn Model Phù Hợp

```python
# Sử dụng model mạnh cho tasks phức tạp
architect = create_agent(
    name="system-architect",
    role="Software Architect",
    model_name="gpt-4-turbo"  # Model mạnh cho architectural decisions
)

# Sử dụng model nhẹ cho tasks đơn giản
formatter = create_agent(
    name="code-formatter",
    role="Code Formatter",
    model_name="gpt-3.5-turbo"  # Model nhẹ đủ cho formatting
)
```text

### 3. Viết System Prompts Chi Tiết

```python
agent = create_agent(
    name="security-auditor",
    role="Security Auditor",
    model_name="gpt-4",
    system_prompt="""Bạn là một security expert chuyên về application security.
    
    Nhiệm vụ của bạn:
    1. Phân tích code để tìm security vulnerabilities
    2. Kiểm tra OWASP Top 10 issues
    3. Đánh giá authentication và authorization logic
    4. Review data validation và sanitization
    5. Đề xuất security improvements cụ thể
    
    Luôn cung cấp:
    - Mô tả chi tiết về vulnerability
    - Severity level (Critical, High, Medium, Low)
    - Code examples để fix
    - References đến security standards
    """
)
```text

### 4. Sử dụng Metadata Hiệu Quả

```python
agent = create_agent(
    name="backend-dev",
    role="Backend Developer",
    model_name="gpt-4",
    metadata={
        "team": "platform",
        "expertise": ["python", "fastapi", "postgresql", "redis"],
        "availability": "24/7",
        "cost_tier": "standard",
        "version": "1.0.0"
    }
)
```text

### 5. Giới Hạn Iterations Hợp Lý

```python
# Cho tasks đơn giản
simple_agent = create_agent(
    name="formatter",
    role="Code Formatter",
    model_name="gpt-3.5-turbo",
    max_iterations=3  # Ít iterations cho tasks đơn giản
)

# Cho tasks phức tạp
complex_agent = create_agent(
    name="debugger",
    role="Bug Fixer",
    model_name="gpt-4",
    max_iterations=20  # Nhiều iterations cho debugging
)
```text

## Patterns Phổ Biến

### Single Agent Pattern

Một agent xử lý toàn bộ task:

```python
agent = create_agent(
    name="full-stack-dev",
    role="Full Stack Developer",
    model_name="gpt-4"
)

# Agent xử lý cả frontend và backend
```text

### Multi-Agent Collaboration

Nhiều agents chuyên môn hóa làm việc cùng nhau:

```python
# Tạo team of agents
backend_dev = create_agent(name="backend-dev", role="Backend Developer")
frontend_dev = create_agent(name="frontend-dev", role="Frontend Developer")
reviewer = create_agent(name="reviewer", role="Code Reviewer")

# Agents cộng tác trong workflow
```text

### Agent Specialization

Agents chuyên sâu cho từng công nghệ:

```python
python_expert = create_agent(
    name="python-expert",
    role="Python Developer",
    model_name="gpt-4",
    system_prompt="Expert in Python, FastAPI, SQLAlchemy..."
)

react_expert = create_agent(
    name="react-expert",
    role="Frontend Developer",
    model_name="gpt-4",
    system_prompt="Expert in React, TypeScript, Next.js..."
)
```

## Tài Liệu Liên Quan

- [Tạo và Cấu Hình Agents](creating-agents.md)
- [Các Loại Agents](agent-types.md)
- [Agent Lifecycle Management](agent-lifecycle.md)
- [Multi-Agent Workflows](../workflows/building-workflows.md)
- [Intelligence Features](../intelligence/collaboration.md)

## Tóm Tắt

Agents là building blocks cơ bản của Agentic SDLC, cho phép tự động hóa các tasks trong software development lifecycle. Bằng cách hiểu rõ cách agents hoạt động, bạn có thể:

- Tạo agents phù hợp cho từng loại task
- Cấu hình agents để tối ưu performance và cost
- Xây dựng multi-agent systems hiệu quả
- Tận dụng intelligence features để cải thiện chất lượng

Tiếp theo, tìm hiểu cách [tạo và cấu hình agents](creating-agents.md) trong hệ thống của bạn.
