# Xây Dựng Workflows

**Phiên bản**: 3.0.0  
**Cập nhật lần cuối**: 11/02/2026


## Giới Thiệu

Tài liệu này hướng dẫn chi tiết cách xây dựng workflows trong Agentic SDLC, từ workflows đơn giản đến phức tạp. Bạn sẽ học cách sử dụng WorkflowBuilder để tạo workflows một cách dễ dàng và hiệu quả.

## WorkflowBuilder

WorkflowBuilder là một công cụ mạnh mẽ giúp bạn xây dựng workflows theo cách fluent và dễ đọc.

### Khởi Tạo WorkflowBuilder

```python
from agentic_sdlc.orchestration.workflow import WorkflowBuilder

builder = WorkflowBuilder(name="my_workflow")
```text

### Thêm Steps vào Workflow

#### Cách 1: Sử dụng add_step()

```python
builder.add_step(
    name="step1",
    action="agent_execute",
    parameters={"agent_id": "dev_agent", "task": "Write code"}
)
```text

#### Cách 2: Sử dụng Fluent Interface

```python
builder \
    .add_step("step1", "agent_execute", {"agent_id": "dev_agent"}) \
    .add_step("step2", "run_tests", {"test_suite": "unit"}) \
    .add_step("step3", "deploy", {"environment": "staging"})
```text

### Build Workflow

```python
workflow = builder.build()
```text

## Xây Dựng Sequential Workflow

Sequential workflow thực thi các bước theo thứ tự tuần tự.

### Ví Dụ 1: Simple Code Review Workflow

```python
from agentic_sdlc.orchestration.workflow import WorkflowBuilder
from agentic_sdlc.infrastructure.workflow_engine import WorkflowEngine

# Tạo workflow
builder = WorkflowBuilder(name="code_review")

workflow = builder \
    .add_step(
        name="fetch_changes",
        action="git_diff",
        parameters={"branch": "feature/new-feature"}
    ) \
    .add_step(
        name="static_analysis",
        action="agent_execute",
        parameters={
            "agent_id": "static_analyzer",
            "task": "Analyze code quality"
        },
        dependencies=["fetch_changes"]
    ) \
    .add_step(
        name="security_scan",
        action="agent_execute",
        parameters={
            "agent_id": "security_scanner",
            "task": "Scan for vulnerabilities"
        },
        dependencies=["static_analysis"]
    ) \
    .add_step(
        name="generate_review",
        action="agent_execute",
        parameters={
            "agent_id": "reviewer",
            "task": "Generate review comments"
        },
        dependencies=["security_scan"]
    ) \
    .build()

# Thực thi workflow
engine = WorkflowEngine()
result = engine.execute_workflow(workflow)

print(f"Review completed: {result.success}")
print(f"Comments: {result.output.get('comments')}")
```text

### Ví Dụ 2: Testing Pipeline

```python
builder = WorkflowBuilder(name="testing_pipeline")

workflow = builder \
    .add_step(
        name="setup_environment",
        action="execute_command",
        parameters={"command": "python -m venv venv && source venv/bin/activate"}
    ) \
    .add_step(
        name="install_dependencies",
        action="execute_command",
        parameters={"command": "pip install -r requirements.txt"},
        dependencies=["setup_environment"]
    ) \
    .add_step(
        name="run_unit_tests",
        action="execute_command",
        parameters={"command": "pytest tests/unit/"},
        dependencies=["install_dependencies"]
    ) \
    .add_step(
        name="run_integration_tests",
        action="execute_command",
        parameters={"command": "pytest tests/integration/"},
        dependencies=["run_unit_tests"]
    ) \
    .add_step(
        name="generate_coverage",
        action="execute_command",
        parameters={"command": "coverage report"},
        dependencies=["run_integration_tests"]
    ) \
    .build()

engine = WorkflowEngine()
result = engine.execute_workflow(workflow)
```text

## Xây Dựng Parallel Workflow

Parallel workflow cho phép nhiều bước chạy đồng thời để tăng hiệu suất.

### Ví Dụ 1: Multi-Module Testing

```python
builder = WorkflowBuilder(name="parallel_testing")

workflow = builder \
    .add_step(
        name="setup",
        action="prepare_environment",
        parameters={"env": "test"}
    ) \
    .add_step(
        name="test_module_a",
        action="run_tests",
        parameters={"module": "module_a"},
        dependencies=["setup"]
    ) \
    .add_step(
        name="test_module_b",
        action="run_tests",
        parameters={"module": "module_b"},
        dependencies=["setup"]
    ) \
    .add_step(
        name="test_module_c",
        action="run_tests",
        parameters={"module": "module_c"},
        dependencies=["setup"]
    ) \
    .add_step(
        name="aggregate_results",
        action="combine_results",
        parameters={},
        dependencies=["test_module_a", "test_module_b", "test_module_c"]
    ) \
    .build()

# Các steps test_module_a, test_module_b, test_module_c sẽ chạy song song
engine = WorkflowEngine()
result = engine.execute_workflow(workflow, parallel=True)
```text

### Ví Dụ 2: Parallel Code Analysis

```python
builder = WorkflowBuilder(name="code_analysis")

workflow = builder \
    .add_step(
        name="fetch_code",
        action="git_clone",
        parameters={"repo": "https://github.com/user/repo.git"}
    ) \
    .add_step(
        name="lint_check",
        action="agent_execute",
        parameters={"agent_id": "linter", "task": "Check code style"},
        dependencies=["fetch_code"]
    ) \
    .add_step(
        name="type_check",
        action="agent_execute",
        parameters={"agent_id": "type_checker", "task": "Check types"},
        dependencies=["fetch_code"]
    ) \
    .add_step(
        name="complexity_analysis",
        action="agent_execute",
        parameters={"agent_id": "complexity_analyzer", "task": "Analyze complexity"},
        dependencies=["fetch_code"]
    ) \
    .add_step(
        name="security_audit",
        action="agent_execute",
        parameters={"agent_id": "security_auditor", "task": "Security audit"},
        dependencies=["fetch_code"]
    ) \
    .add_step(
        name="generate_report",
        action="create_report",
        parameters={"format": "html"},
        dependencies=["lint_check", "type_check", "complexity_analysis", "security_audit"]
    ) \
    .build()

engine = WorkflowEngine()
result = engine.execute_workflow(workflow, parallel=True)
```text

## Xây Dựng Workflow với Dependencies Phức Tạp

### Ví Dụ: CI/CD Pipeline

```python
builder = WorkflowBuilder(name="cicd_pipeline")

workflow = builder \
    .add_step(
        name="checkout_code",
        action="git_checkout",
        parameters={"branch": "main"}
    ) \
    .add_step(
        name="build_backend",
        action="build",
        parameters={"target": "backend"},
        dependencies=["checkout_code"]
    ) \
    .add_step(
        name="build_frontend",
        action="build",
        parameters={"target": "frontend"},
        dependencies=["checkout_code"]
    ) \
    .add_step(
        name="test_backend",
        action="run_tests",
        parameters={"suite": "backend"},
        dependencies=["build_backend"]
    ) \
    .add_step(
        name="test_frontend",
        action="run_tests",
        parameters={"suite": "frontend"},
        dependencies=["build_frontend"]
    ) \
    .add_step(
        name="integration_tests",
        action="run_tests",
        parameters={"suite": "integration"},
        dependencies=["test_backend", "test_frontend"]
    ) \
    .add_step(
        name="build_docker_image",
        action="docker_build",
        parameters={"tag": "latest"},
        dependencies=["integration_tests"]
    ) \
    .add_step(
        name="push_to_registry",
        action="docker_push",
        parameters={"registry": "docker.io"},
        dependencies=["build_docker_image"]
    ) \
    .add_step(
        name="deploy_staging",
        action="deploy",
        parameters={"environment": "staging"},
        dependencies=["push_to_registry"]
    ) \
    .build()

engine = WorkflowEngine()
result = engine.execute_workflow(workflow, parallel=True)
```text

## Passing Data Between Steps

Workflows thường cần truyền dữ liệu giữa các steps.

### Sử dụng Workflow Context

```python
from agentic_sdlc.orchestration.workflow import WorkflowContext

# Step 1: Tạo dữ liệu
def analyze_code(context: WorkflowContext):
    issues = ["Issue 1", "Issue 2", "Issue 3"]
    context.set("code_issues", issues)
    return {"status": "completed", "issue_count": len(issues)}

# Step 2: Sử dụng dữ liệu từ step 1
def create_tickets(context: WorkflowContext):
    issues = context.get("code_issues")
    tickets = []
    for issue in issues:
        ticket = create_jira_ticket(issue)
        tickets.append(ticket)
    return {"tickets": tickets}

# Tạo workflow
builder = WorkflowBuilder(name="issue_tracking")

workflow = builder \
    .add_step(
        name="analyze",
        action=analyze_code,
        parameters={}
    ) \
    .add_step(
        name="create_tickets",
        action=create_tickets,
        parameters={},
        dependencies=["analyze"]
    ) \
    .build()
```text

### Sử dụng Step Output

```python
builder = WorkflowBuilder(name="data_pipeline")

workflow = builder \
    .add_step(
        name="extract_data",
        action="extract",
        parameters={"source": "database"},
        output_key="raw_data"
    ) \
    .add_step(
        name="transform_data",
        action="transform",
        parameters={"input": "${raw_data}"},  # Reference output từ step trước
        dependencies=["extract_data"],
        output_key="transformed_data"
    ) \
    .add_step(
        name="load_data",
        action="load",
        parameters={"data": "${transformed_data}", "target": "warehouse"},
        dependencies=["transform_data"]
    ) \
    .build()
```text

## Workflow Configuration

### Thiết Lập Timeout

```python
builder = WorkflowBuilder(name="my_workflow")

workflow = builder \
    .add_step(
        name="long_running_task",
        action="process_data",
        parameters={"dataset": "large"},
        timeout=3600  # 1 hour timeout
    ) \
    .build()
```text

### Thiết Lập Retry Logic

```python
builder = WorkflowBuilder(name="resilient_workflow")

workflow = builder \
    .add_step(
        name="api_call",
        action="call_external_api",
        parameters={"endpoint": "/data"},
        retry_count=3,
        retry_delay=5  # 5 seconds between retries
    ) \
    .build()
```text

### Thiết Lập Priority

```python
builder = WorkflowBuilder(name="prioritized_workflow")

workflow = builder \
    .add_step(
        name="critical_task",
        action="process",
        parameters={},
        priority="high"
    ) \
    .add_step(
        name="normal_task",
        action="process",
        parameters={},
        priority="normal"
    ) \
    .build()
```text

## Workflow Validation

Validate workflow trước khi thực thi:

```python
from agentic_sdlc.infrastructure.workflow_engine import WorkflowEngine

engine = WorkflowEngine()

# Validate workflow structure
validation_result = engine.validate_workflow(workflow)

if not validation_result.is_valid:
    print("Workflow validation failed:")
    for error in validation_result.errors:
        print(f"  - {error}")
else:
    print("Workflow is valid")
    result = engine.execute_workflow(workflow)
```text

## Best Practices

### 1. Naming Conventions

```python
# Good: Descriptive names
builder.add_step("fetch_user_data", ...)
builder.add_step("validate_input", ...)
builder.add_step("send_notification", ...)

# Bad: Vague names
builder.add_step("step1", ...)
builder.add_step("do_stuff", ...)
builder.add_step("process", ...)
```text

### 2. Dependency Management

```python
# Good: Clear dependencies
workflow = builder \
    .add_step("fetch", ...) \
    .add_step("process", ..., dependencies=["fetch"]) \
    .add_step("save", ..., dependencies=["process"]) \
    .build()

# Bad: Circular dependencies (will fail validation)
workflow = builder \
    .add_step("step1", ..., dependencies=["step2"]) \
    .add_step("step2", ..., dependencies=["step1"]) \
    .build()
```text

### 3. Error Handling

```python
# Good: Proper error handling
workflow = builder \
    .add_step(
        "api_call",
        action="call_api",
        parameters={},
        retry_count=3,
        on_error="continue"  # Continue workflow even if this step fails
    ) \
    .build()
```text

### 4. Resource Management

```python
# Good: Cleanup steps
workflow = builder \
    .add_step("setup", action="create_resources", ...) \
    .add_step("process", action="do_work", ..., dependencies=["setup"]) \
    .add_step("cleanup", action="delete_resources", ..., 
              dependencies=["process"], always_run=True) \
    .build()
```text

## Ví Dụ Thực Tế

### Feature Development Workflow

```python
builder = WorkflowBuilder(name="feature_development")

workflow = builder \
    .add_step(
        name="create_branch",
        action="git_branch",
        parameters={"branch_name": "feature/new-feature"}
    ) \
    .add_step(
        name="generate_code",
        action="agent_execute",
        parameters={
            "agent_id": "developer",
            "task": "Implement feature based on requirements"
        },
        dependencies=["create_branch"]
    ) \
    .add_step(
        name="write_tests",
        action="agent_execute",
        parameters={
            "agent_id": "tester",
            "task": "Write unit tests for new feature"
        },
        dependencies=["generate_code"]
    ) \
    .add_step(
        name="run_tests",
        action="execute_command",
        parameters={"command": "pytest tests/"},
        dependencies=["write_tests"]
    ) \
    .add_step(
        name="code_review",
        action="agent_execute",
        parameters={
            "agent_id": "reviewer",
            "task": "Review code quality and suggest improvements"
        },
        dependencies=["run_tests"]
    ) \
    .add_step(
        name="create_pr",
        action="github_create_pr",
        parameters={
            "title": "New Feature Implementation",
            "base": "main",
            "head": "feature/new-feature"
        },
        dependencies=["code_review"]
    ) \
    .build()

engine = WorkflowEngine()
result = engine.execute_workflow(workflow)
```

## Tài Liệu Liên Quan

- [Workflow Overview](overview.md) - Tổng quan về workflows
- [Workflow Patterns](workflow-patterns.md) - Các patterns phổ biến
- [Advanced Workflows](advanced-workflows.md) - Workflows nâng cao
