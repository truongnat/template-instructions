# Tạo và Cấu Hình Agents

**Phiên bản**: 3.0.0  
**Cập nhật lần cuối**: 11/02/2026


## Giới Thiệu

Tài liệu này hướng dẫn chi tiết cách tạo, cấu hình và quản lý agents trong Agentic SDLC. Bạn sẽ học cách sử dụng function `create_agent()`, cấu hình các parameters, và tùy chỉnh agents cho các use cases cụ thể.

## Tạo Agent Cơ Bản

### Sử Dụng create_agent()

Function `create_agent()` là cách đơn giản nhất để tạo agent mới:

```python
from agentic_sdlc import create_agent

# Tạo agent với các parameters tối thiểu
agent = create_agent(
    name="my-first-agent",
    role="Developer",
    model_name="gpt-4"
)

print(f"Agent created: {agent.name}")
print(f"Agent ID: {agent.id}")
print(f"Role: {agent.role}")
```text

### Parameters Bắt Buộc

Ba parameters bắt buộc khi tạo agent:

1. **name** (str): Tên định danh của agent
   - Phải unique trong registry
   - Nên sử dụng kebab-case: `backend-developer`, `code-reviewer`
   - Mô tả rõ chức năng của agent

2. **role** (str): Vai trò/chức năng của agent
   - Mô tả nhiệm vụ chính của agent
   - Ví dụ: "Backend Developer", "Code Reviewer", "Security Auditor"

3. **model_name** (str): Tên của LLM model
   - Ví dụ: "gpt-4", "gpt-4-turbo", "claude-3-opus", "gpt-3.5-turbo"
   - Chọn model phù hợp với độ phức tạp của task

## Cấu Hình Nâng Cao

### System Prompt

System prompt định nghĩa personality và expertise của agent:

```python
agent = create_agent(
    name="python-expert",
    role="Python Developer",
    model_name="gpt-4",
    system_prompt="""Bạn là một Python expert với 10+ năm kinh nghiệm.
    
    Chuyên môn của bạn:
    - Python 3.10+ features và best practices
    - FastAPI, Django, Flask frameworks
    - Async programming với asyncio
    - Database design với SQLAlchemy
    - Testing với pytest
    - Performance optimization
    
    Khi viết code, bạn luôn:
    - Tuân thủ PEP 8 style guide
    - Viết type hints đầy đủ
    - Thêm docstrings cho functions và classes
    - Xử lý errors một cách graceful
    - Viết code dễ maintain và test
    
    Khi review code, bạn focus vào:
    - Code quality và readability
    - Performance issues
    - Security vulnerabilities
    - Best practices violations
    """
)
```text

### Tools Configuration

Cấu hình tools mà agent có thể sử dụng:

```python
agent = create_agent(
    name="full-stack-dev",
    role="Full Stack Developer",
    model_name="gpt-4",
    tools=[
        "code_execution",      # Chạy Python code
        "file_operations",     # Đọc/ghi files
        "git_operations",      # Git commands
        "api_calls",          # HTTP requests
        "database_query",     # SQL queries
        "shell_commands"      # Shell commands
    ]
)

print(f"Agent có {len(agent.tools)} tools")
```text

### Max Iterations

Giới hạn số lần thử cho một task:

```python
# Agent cho tasks đơn giản - ít iterations
formatter = create_agent(
    name="code-formatter",
    role="Code Formatter",
    model_name="gpt-3.5-turbo",
    max_iterations=3
)

# Agent cho tasks phức tạp - nhiều iterations
debugger = create_agent(
    name="bug-hunter",
    role="Debugger",
    model_name="gpt-4",
    max_iterations=20
)

# Agent cho research tasks - rất nhiều iterations
researcher = create_agent(
    name="tech-researcher",
    role="Technology Researcher",
    model_name="gpt-4-turbo",
    max_iterations=50
)
```text

### Metadata

Thêm thông tin bổ sung vào agent:

```python
agent = create_agent(
    name="backend-specialist",
    role="Backend Developer",
    model_name="gpt-4",
    metadata={
        # Team information
        "team": "platform-engineering",
        "squad": "core-services",
        
        # Technical expertise
        "expertise": ["python", "fastapi", "postgresql", "redis", "kafka"],
        "experience_years": 5,
        
        # Operational info
        "availability": "24/7",
        "timezone": "UTC+7",
        "cost_tier": "premium",
        
        # Version and tracking
        "version": "2.1.0",
        "created_by": "admin",
        "environment": "production"
    }
)

# Truy cập metadata
print(f"Team: {agent.metadata['team']}")
print(f"Expertise: {', '.join(agent.metadata['expertise'])}")
```text

## Ví Dụ Thực Tế

### Example 1: Code Review Agent

```python
from agentic_sdlc import create_agent

code_reviewer = create_agent(
    name="senior-code-reviewer",
    role="Senior Code Reviewer",
    model_name="gpt-4-turbo",
    system_prompt="""Bạn là một senior code reviewer với expertise về:
    - Clean Code principles
    - SOLID principles
    - Design patterns
    - Security best practices
    - Performance optimization
    
    Khi review code, bạn cung cấp:
    1. Overall assessment (Approve/Request Changes/Comment)
    2. Detailed feedback cho từng issue
    3. Code examples để fix issues
    4. Suggestions để improve code quality
    5. Security và performance concerns
    
    Feedback của bạn luôn:
    - Constructive và respectful
    - Specific với line numbers
    - Có examples cụ thể
    - Prioritized theo severity
    """,
    tools=["file_operations", "code_analysis"],
    max_iterations=10,
    metadata={
        "review_focus": ["security", "performance", "maintainability"],
        "languages": ["python", "javascript", "typescript"],
        "frameworks": ["fastapi", "react", "nextjs"]
    }
)
```text

### Example 2: Test Generation Agent

```python
test_generator = create_agent(
    name="test-automation-expert",
    role="Test Automation Engineer",
    model_name="gpt-4",
    system_prompt="""Bạn là một test automation expert chuyên về:
    - Unit testing với pytest
    - Integration testing
    - Property-based testing với Hypothesis
    - Test coverage analysis
    - Mocking và fixtures
    
    Khi generate tests, bạn:
    1. Phân tích code để identify test cases
    2. Viết comprehensive unit tests
    3. Cover edge cases và error conditions
    4. Sử dụng fixtures hiệu quả
    5. Ensure tests are maintainable
    
    Test code của bạn:
    - Có descriptive test names
    - Follow AAA pattern (Arrange, Act, Assert)
    - Có clear assertions
    - Independent và isolated
    - Fast execution
    """,
    tools=["code_execution", "file_operations", "pytest"],
    max_iterations=15,
    metadata={
        "test_frameworks": ["pytest", "unittest", "hypothesis"],
        "coverage_target": 90,
        "test_types": ["unit", "integration", "property-based"]
    }
)
```text

### Example 3: Documentation Agent

```python
doc_writer = create_agent(
    name="technical-writer",
    role="Technical Documentation Writer",
    model_name="gpt-4",
    system_prompt="""Bạn là một technical writer chuyên về software documentation.
    
    Bạn viết documentation:
    - Clear và concise
    - Có examples thực tế
    - Structured logic
    - Dễ hiểu cho developers ở mọi level
    
    Bạn tạo:
    1. API documentation với examples
    2. User guides step-by-step
    3. Architecture documentation với diagrams
    4. Code comments và docstrings
    5. README files comprehensive
    
    Documentation của bạn bao gồm:
    - Overview và introduction
    - Prerequisites và setup
    - Detailed instructions
    - Code examples runnable
    - Troubleshooting section
    - Best practices
    """,
    tools=["file_operations", "markdown_generation"],
    max_iterations=8,
    metadata={
        "doc_types": ["api", "user-guide", "architecture", "readme"],
        "formats": ["markdown", "rst", "html"],
        "languages": ["vietnamese", "english"]
    }
)
```text

### Example 4: Security Audit Agent

```python
security_auditor = create_agent(
    name="security-specialist",
    role="Security Auditor",
    model_name="gpt-4-turbo",
    system_prompt="""Bạn là một security expert với chuyên môn về application security.
    
    Bạn audit code để tìm:
    - SQL injection vulnerabilities
    - XSS (Cross-Site Scripting) issues
    - Authentication và authorization flaws
    - Sensitive data exposure
    - Security misconfiguration
    - Insecure dependencies
    - CSRF vulnerabilities
    - API security issues
    
    Cho mỗi vulnerability, bạn cung cấp:
    1. Severity level (Critical/High/Medium/Low)
    2. Detailed description
    3. Proof of concept (nếu có thể)
    4. Remediation steps cụ thể
    5. Code examples để fix
    6. References (OWASP, CWE)
    
    Bạn follow OWASP Top 10 và security best practices.
    """,
    tools=["code_analysis", "security_scan", "dependency_check"],
    max_iterations=12,
    metadata={
        "security_standards": ["OWASP", "CWE", "SANS"],
        "scan_types": ["static", "dependency", "configuration"],
        "severity_levels": ["critical", "high", "medium", "low", "info"]
    }
)
```text

### Example 5: Database Design Agent

```python
db_architect = create_agent(
    name="database-architect",
    role="Database Architect",
    model_name="gpt-4",
    system_prompt="""Bạn là một database architect expert với kinh nghiệm về:
    - Relational database design (PostgreSQL, MySQL)
    - NoSQL databases (MongoDB, Redis)
    - Database normalization
    - Indexing strategies
    - Query optimization
    - Data modeling
    - Migration strategies
    
    Khi design database, bạn:
    1. Analyze requirements kỹ lưỡng
    2. Create normalized schema
    3. Define relationships properly
    4. Plan indexing strategy
    5. Consider scalability
    6. Document design decisions
    
    Bạn cung cấp:
    - ER diagrams
    - SQL migration scripts
    - Indexing recommendations
    - Query optimization tips
    - Scaling strategies
    """,
    tools=["database_query", "schema_analysis", "diagram_generation"],
    max_iterations=10,
    metadata={
        "databases": ["postgresql", "mysql", "mongodb", "redis"],
        "specialties": ["schema-design", "optimization", "migration"],
        "tools": ["sqlalchemy", "alembic", "prisma"]
    }
)
```text

## Quản Lý Agents

### Lấy Agent từ Registry

```python
from agentic_sdlc import get_agent_registry

registry = get_agent_registry()

# Lấy agent theo ID
agent = registry.get_agent("agent-id-123")

# Lấy agent theo tên
agent = registry.get_agent_by_name("code-reviewer")

# Kiểm tra agent có tồn tại không
if registry.has_agent("my-agent"):
    agent = registry.get_agent_by_name("my-agent")
```text

### Liệt Kê Agents

```python
# Lấy tất cả agents
all_agents = registry.list_agents()

print(f"Total agents: {len(all_agents)}")
for agent in all_agents:
    print(f"- {agent.name} ({agent.role})")

# Filter agents theo metadata
backend_agents = [
    agent for agent in all_agents
    if agent.metadata.get("team") == "backend"
]

# Filter agents theo role
reviewers = [
    agent for agent in all_agents
    if "reviewer" in agent.role.lower()
]
```text

### Cập Nhật Agent

```python
# Lấy agent
agent = registry.get_agent_by_name("my-agent")

# Cập nhật system prompt
agent.system_prompt = "Updated system prompt..."

# Thêm tools
agent.tools.append("new_tool")

# Cập nhật metadata
agent.metadata["version"] = "2.0.0"
agent.metadata["updated_at"] = "2024-01-15"

# Thay đổi max_iterations
agent.max_iterations = 15
```text

### Xóa Agent

```python
# Xóa agent theo ID
registry.remove_agent("agent-id-123")

# Xóa agent theo tên
agent = registry.get_agent_by_name("old-agent")
if agent:
    registry.remove_agent(agent.id)
```text

## Model Configuration

### Chọn Model Phù Hợp

```python
# GPT-4 Turbo - Cho tasks phức tạp, cần reasoning cao
architect = create_agent(
    name="system-architect",
    role="Software Architect",
    model_name="gpt-4-turbo"
)

# GPT-4 - Balanced performance và cost
developer = create_agent(
    name="senior-developer",
    role="Senior Developer",
    model_name="gpt-4"
)

# GPT-3.5 Turbo - Cho tasks đơn giản, cost-effective
formatter = create_agent(
    name="code-formatter",
    role="Code Formatter",
    model_name="gpt-3.5-turbo"
)

# Claude 3 Opus - Alternative cho GPT-4
analyst = create_agent(
    name="code-analyst",
    role="Code Analyst",
    model_name="claude-3-opus"
)
```text

### Model Configuration với ModelConfig

```python
from agentic_sdlc import create_agent, ModelConfig

# Tạo model config
model_config = ModelConfig(
    provider="openai",
    model_name="gpt-4-turbo",
    temperature=0.7,
    max_tokens=2000,
    api_key="your-api-key"
)

# Sử dụng với agent
agent = create_agent(
    name="configured-agent",
    role="Developer",
    model=model_config
)
```text

## Best Practices

### 1. Naming Conventions

```python
# Tốt: Descriptive names
create_agent(name="python-backend-developer", role="Backend Developer")
create_agent(name="react-frontend-specialist", role="Frontend Developer")
create_agent(name="security-code-auditor", role="Security Auditor")

# Tránh: Generic names
create_agent(name="agent1", role="Agent")
create_agent(name="dev", role="Developer")
```text

### 2. System Prompt Guidelines

```python
# Tốt: Detailed và specific
system_prompt = """Bạn là Python expert chuyên về FastAPI.
Expertise: REST API design, async programming, database integration.
Luôn viết type hints, docstrings, và handle errors properly.
"""

# Tránh: Vague và generic
system_prompt = "You are a developer."
```text

### 3. Tool Selection

```python
# Tốt: Chỉ tools cần thiết
agent = create_agent(
    name="code-reviewer",
    role="Code Reviewer",
    tools=["file_operations", "code_analysis"]  # Chỉ tools cho review
)

# Tránh: Quá nhiều tools không cần thiết
agent = create_agent(
    name="code-reviewer",
    role="Code Reviewer",
    tools=["file_operations", "code_analysis", "database_query", 
           "api_calls", "shell_commands", "git_operations"]  # Quá nhiều!
)
```text

### 4. Metadata Organization

```python
# Tốt: Structured metadata
metadata = {
    "team": {"name": "platform", "squad": "core"},
    "technical": {"languages": ["python"], "frameworks": ["fastapi"]},
    "operational": {"availability": "24/7", "cost_tier": "standard"},
    "tracking": {"version": "1.0.0", "created_at": "2024-01-15"}
}

# Tránh: Flat và unorganized
metadata = {
    "team": "platform",
    "lang1": "python",
    "available": True,
    "v": "1.0"
}
```text

## Troubleshooting

### Agent Creation Fails

```python
try:
    agent = create_agent(
        name="my-agent",
        role="Developer",
        model_name="gpt-4"
    )
except ValueError as e:
    print(f"Creation failed: {e}")
    # Kiểm tra: name không empty, role không empty, model_name valid
```text

### Agent Not Found in Registry

```python
registry = get_agent_registry()

# Kiểm tra agent tồn tại trước khi get
if not registry.has_agent("my-agent"):
    print("Agent not found, creating new one...")
    agent = create_agent(name="my-agent", role="Developer", model_name="gpt-4")
else:
    agent = registry.get_agent_by_name("my-agent")
```text

### Duplicate Agent Names

```python
# Kiểm tra trước khi tạo
registry = get_agent_registry()

if registry.has_agent("my-agent"):
    print("Agent already exists!")
    # Option 1: Use existing agent
    agent = registry.get_agent_by_name("my-agent")
    
    # Option 2: Remove old agent và tạo mới
    old_agent = registry.get_agent_by_name("my-agent")
    registry.remove_agent(old_agent.id)
    agent = create_agent(name="my-agent", role="Developer", model_name="gpt-4")
else:
    agent = create_agent(name="my-agent", role="Developer", model_name="gpt-4")
```

## Tài Liệu Liên Quan

- [Tổng Quan về Agents](overview.md)
- [Các Loại Agents](agent-types.md)
- [Agent Lifecycle Management](agent-lifecycle.md)
- [Model Configuration](../../getting-started/configuration.md)
- [Multi-Agent Workflows](../workflows/building-workflows.md)

## Tóm Tắt

Trong tài liệu này, bạn đã học:

- Cách tạo agents với `create_agent()`
- Cấu hình system prompts, tools, và metadata
- Các ví dụ thực tế cho different agent types
- Quản lý agents trong registry
- Best practices cho agent creation
- Troubleshooting common issues

Tiếp theo, tìm hiểu về [các loại agents](agent-types.md) có sẵn trong Agentic SDLC.
