# Workflow Patterns

**Phiên bản**: 3.0.0  
**Cập nhật lần cuối**: 11/02/2026


## Giới Thiệu

Tài liệu này mô tả các workflow patterns phổ biến trong Agentic SDLC. Hiểu và áp dụng các patterns này sẽ giúp bạn xây dựng workflows hiệu quả và maintainable hơn.

## Sequential Pattern (Tuần Tự)

### Mô Tả

Sequential pattern thực thi các bước theo thứ tự tuyến tính, mỗi bước chờ bước trước hoàn thành.

### Khi Nào Sử Dụng

- Khi các bước phụ thuộc vào kết quả của bước trước
- Khi thứ tự thực thi quan trọng
- Khi cần đảm bảo data consistency

### Cấu Trúc

```text
Step 1 → Step 2 → Step 3 → Step 4
```

### Ví Dụ: Deployment Pipeline

```python
from agentic_sdlc.orchestration.workflow import WorkflowBuilder
from agentic_sdlc.infrastructure.workflow_engine import WorkflowEngine

builder = WorkflowBuilder(name="deployment_pipeline")

workflow = builder \
    .add_step(
        name="build",
        action="build_application",
        parameters={"target": "production"}
    ) \
    .add_step(
        name="test",
        action="run_tests",
        parameters={"suite": "all"},
        dependencies=["build"]
    ) \
    .add_step(
        name="package",
        action="create_package",
        parameters={"format": "docker"},
        dependencies=["test"]
    ) \
    .add_step(
        name="deploy",
        action="deploy_to_production",
        parameters={"environment": "prod"},
        dependencies=["package"]
    ) \
    .build()

engine = WorkflowEngine()
result = engine.execute_workflow(workflow)
```text

### Use Cases

- Deployment pipelines
- Data processing pipelines
- Sequential approval workflows
- Step-by-step tutorials

## Parallel Pattern (Song Song)

### Mô Tả

Parallel pattern thực thi nhiều bước đồng thời để tăng tốc độ xử lý.

### Khi Nào Sử Dụng

- Khi các bước độc lập với nhau
- Khi cần tối ưu thời gian thực thi
- Khi có đủ resources để chạy song song

### Cấu Trúc

```
        ┌─ Step 2 ─┐
Step 1 ─┤─ Step 3 ─┤─ Step 5
        └─ Step 4 ─┘
```text

### Ví Dụ: Multi-Environment Testing

```python
builder = WorkflowBuilder(name="multi_env_testing")

workflow = builder \
    .add_step(
        name="prepare",
        action="setup_test_data",
        parameters={}
    ) \
    .add_step(
        name="test_chrome",
        action="run_browser_tests",
        parameters={"browser": "chrome"},
        dependencies=["prepare"]
    ) \
    .add_step(
        name="test_firefox",
        action="run_browser_tests",
        parameters={"browser": "firefox"},
        dependencies=["prepare"]
    ) \
    .add_step(
        name="test_safari",
        action="run_browser_tests",
        parameters={"browser": "safari"},
        dependencies=["prepare"]
    ) \
    .add_step(
        name="aggregate",
        action="combine_results",
        parameters={},
        dependencies=["test_chrome", "test_firefox", "test_safari"]
    ) \
    .build()

engine = WorkflowEngine()
result = engine.execute_workflow(workflow, parallel=True)
```text

### Use Cases

- Multi-browser testing
- Parallel code analysis
- Distributed data processing
- Multi-region deployments

## Fan-Out/Fan-In Pattern

### Mô Tả

Fan-out/fan-in pattern chia một task thành nhiều sub-tasks chạy song song, sau đó tổng hợp kết quả.

### Khi Nào Sử Dụng

- Khi cần xử lý nhiều items độc lập
- Khi cần aggregate results từ nhiều sources
- Khi muốn tối ưu throughput

### Cấu Trúc

```
           ┌─ Process A ─┐
Split ────┼─ Process B ─┼──── Merge
           └─ Process C ─┘
```text

### Ví Dụ: Distributed Code Analysis

```python
builder = WorkflowBuilder(name="distributed_analysis")

workflow = builder \
    .add_step(
        name="split_codebase",
        action="split_by_module",
        parameters={"modules": ["auth", "api", "ui", "db"]}
    ) \
    .add_step(
        name="analyze_auth",
        action="analyze_module",
        parameters={"module": "auth"},
        dependencies=["split_codebase"]
    ) \
    .add_step(
        name="analyze_api",
        action="analyze_module",
        parameters={"module": "api"},
        dependencies=["split_codebase"]
    ) \
    .add_step(
        name="analyze_ui",
        action="analyze_module",
        parameters={"module": "ui"},
        dependencies=["split_codebase"]
    ) \
    .add_step(
        name="analyze_db",
        action="analyze_module",
        parameters={"module": "db"},
        dependencies=["split_codebase"]
    ) \
    .add_step(
        name="merge_results",
        action="aggregate_analysis",
        parameters={},
        dependencies=["analyze_auth", "analyze_api", "analyze_ui", "analyze_db"]
    ) \
    .build()

engine = WorkflowEngine()
result = engine.execute_workflow(workflow, parallel=True)
```text

### Use Cases

- Map-reduce operations
- Distributed testing
- Multi-source data aggregation
- Parallel processing pipelines

## Pipeline Pattern

### Mô Tả

Pipeline pattern xử lý data qua một chuỗi các transformations.

### Khi Nào Sử Dụng

- Khi cần transform data qua nhiều stages
- Khi mỗi stage có responsibility rõ ràng
- Khi muốn reuse individual stages

### Cấu Trúc

```
Input → Stage 1 → Stage 2 → Stage 3 → Output
```text

### Ví Dụ: Data Processing Pipeline

```python
builder = WorkflowBuilder(name="data_pipeline")

workflow = builder \
    .add_step(
        name="extract",
        action="extract_data",
        parameters={"source": "database", "query": "SELECT * FROM users"}
    ) \
    .add_step(
        name="validate",
        action="validate_data",
        parameters={"schema": "user_schema"},
        dependencies=["extract"]
    ) \
    .add_step(
        name="transform",
        action="transform_data",
        parameters={"operations": ["normalize", "enrich"]},
        dependencies=["validate"]
    ) \
    .add_step(
        name="filter",
        action="filter_data",
        parameters={"condition": "active = true"},
        dependencies=["transform"]
    ) \
    .add_step(
        name="load",
        action="load_data",
        parameters={"target": "warehouse"},
        dependencies=["filter"]
    ) \
    .build()

engine = WorkflowEngine()
result = engine.execute_workflow(workflow)
```text

### Use Cases

- ETL (Extract, Transform, Load) processes
- Data cleaning pipelines
- Image processing pipelines
- Text processing workflows

## Conditional Pattern (Có Điều Kiện)

### Mô Tả

Conditional pattern thực thi các bước khác nhau dựa trên điều kiện hoặc kết quả.

### Khi Nào Sử Dụng

- Khi logic thực thi phụ thuộc vào runtime conditions
- Khi cần handle different scenarios
- Khi muốn optimize resource usage

### Cấu Trúc

```
Step 1 → Decision → Step 2A (if condition)
                 → Step 2B (else)
```text

### Ví Dụ: Smart Deployment

```python
from agentic_sdlc.orchestration.workflow import WorkflowBuilder, ConditionalStep

builder = WorkflowBuilder(name="smart_deployment")

workflow = builder \
    .add_step(
        name="run_tests",
        action="execute_tests",
        parameters={"suite": "all"}
    ) \
    .add_conditional_step(
        name="decide_deployment",
        condition=lambda context: context.get("test_results").success_rate > 0.95,
        true_step=ConditionalStep(
            name="deploy_production",
            action="deploy",
            parameters={"environment": "production"}
        ),
        false_step=ConditionalStep(
            name="deploy_staging",
            action="deploy",
            parameters={"environment": "staging"}
        ),
        dependencies=["run_tests"]
    ) \
    .build()

engine = WorkflowEngine()
result = engine.execute_workflow(workflow)
```text

### Use Cases

- Smart deployments based on test results
- Adaptive workflows based on data quality
- Environment-specific processing
- Error recovery workflows

## Retry Pattern

### Mô Tả

Retry pattern tự động thử lại các bước failed với exponential backoff.

### Khi Nào Sử Dụng

- Khi làm việc với unreliable external services
- Khi có transient errors
- Khi muốn improve reliability

### Cấu Trúc

```
Step → Fail? → Retry (with delay) → Fail? → Retry → Success/Fail
```text

### Ví Dụ: Resilient API Call

```python
builder = WorkflowBuilder(name="resilient_api_workflow")

workflow = builder \
    .add_step(
        name="call_external_api",
        action="http_request",
        parameters={
            "url": "https://api.example.com/data",
            "method": "GET"
        },
        retry_count=5,
        retry_delay=2,  # Initial delay in seconds
        retry_backoff=2  # Exponential backoff multiplier
    ) \
    .add_step(
        name="process_response",
        action="process_data",
        parameters={},
        dependencies=["call_external_api"]
    ) \
    .build()

engine = WorkflowEngine()
result = engine.execute_workflow(workflow)
```text

### Use Cases

- External API calls
- Database operations
- Network requests
- File system operations

## Saga Pattern

### Mô Tả

Saga pattern quản lý distributed transactions với compensating actions.

### Khi Nào Sử Dụng

- Khi cần maintain consistency across multiple services
- Khi không thể sử dụng distributed transactions
- Khi cần rollback capabilities

### Cấu Trúc

```
Step 1 → Step 2 → Step 3 (fail) → Compensate 2 → Compensate 1
```text

### Ví Dụ: Order Processing

```python
builder = WorkflowBuilder(name="order_saga")

workflow = builder \
    .add_step(
        name="reserve_inventory",
        action="reserve_items",
        parameters={"order_id": "12345"},
        compensate_action="release_items"
    ) \
    .add_step(
        name="charge_payment",
        action="process_payment",
        parameters={"amount": 100.00},
        dependencies=["reserve_inventory"],
        compensate_action="refund_payment"
    ) \
    .add_step(
        name="create_shipment",
        action="schedule_delivery",
        parameters={"address": "123 Main St"},
        dependencies=["charge_payment"],
        compensate_action="cancel_shipment"
    ) \
    .add_step(
        name="send_confirmation",
        action="send_email",
        parameters={"template": "order_confirmation"},
        dependencies=["create_shipment"]
    ) \
    .build()

engine = WorkflowEngine()
result = engine.execute_workflow(workflow, enable_saga=True)
```text

### Use Cases

- E-commerce order processing
- Multi-service transactions
- Booking systems
- Financial transactions

## Circuit Breaker Pattern

### Mô Tả

Circuit breaker pattern ngăn chặn cascading failures bằng cách fail fast khi service không available.

### Khi Nào Sử Dụng

- Khi gọi external services
- Khi muốn prevent cascading failures
- Khi cần graceful degradation

### Cấu Trúc

```
Request → Circuit Closed? → Call Service
       → Circuit Open? → Return Error
       → Circuit Half-Open? → Try Service
```text

### Ví Dụ: Protected External Call

```python
from agentic_sdlc.orchestration.workflow import CircuitBreakerConfig

builder = WorkflowBuilder(name="protected_workflow")

circuit_breaker = CircuitBreakerConfig(
    failure_threshold=5,  # Open after 5 failures
    timeout=60,  # Try again after 60 seconds
    success_threshold=2  # Close after 2 successes
)

workflow = builder \
    .add_step(
        name="call_service",
        action="http_request",
        parameters={"url": "https://external-service.com/api"},
        circuit_breaker=circuit_breaker
    ) \
    .add_step(
        name="process_result",
        action="process_data",
        parameters={},
        dependencies=["call_service"]
    ) \
    .build()

engine = WorkflowEngine()
result = engine.execute_workflow(workflow)
```text

### Use Cases

- Microservices communication
- External API integrations
- Database connections
- Third-party service calls

## Batch Processing Pattern

### Mô Tả

Batch processing pattern xử lý nhiều items trong batches để tối ưu performance.

### Khi Nào Sử Dụng

- Khi xử lý large datasets
- Khi muốn optimize throughput
- Khi có rate limits

### Cấu Trúc

```
Items → Batch 1 → Process
      → Batch 2 → Process
      → Batch 3 → Process
```text

### Ví Dụ: Bulk Email Sending

```python
builder = WorkflowBuilder(name="bulk_email")

workflow = builder \
    .add_step(
        name="fetch_recipients",
        action="get_users",
        parameters={"filter": "subscribed = true"}
    ) \
    .add_step(
        name="create_batches",
        action="batch_items",
        parameters={"batch_size": 100},
        dependencies=["fetch_recipients"]
    ) \
    .add_step(
        name="send_batch",
        action="send_emails",
        parameters={"template": "newsletter"},
        dependencies=["create_batches"],
        batch_processing=True,
        batch_delay=1  # 1 second delay between batches
    ) \
    .build()

engine = WorkflowEngine()
result = engine.execute_workflow(workflow)
```text

### Use Cases

- Bulk email sending
- Large data imports
- Batch API calls
- Mass updates

## Real-World Example: CI/CD Pipeline

Kết hợp nhiều patterns để tạo một CI/CD pipeline hoàn chỉnh:

```python
builder = WorkflowBuilder(name="complete_cicd")

workflow = builder \
    .add_step(
        name="checkout",
        action="git_checkout",
        parameters={"branch": "main"}
    ) \
    .add_step(
        name="build_backend",
        action="build",
        parameters={"target": "backend"},
        dependencies=["checkout"],
        retry_count=3
    ) \
    .add_step(
        name="build_frontend",
        action="build",
        parameters={"target": "frontend"},
        dependencies=["checkout"],
        retry_count=3
    ) \
    .add_step(
        name="unit_tests_backend",
        action="run_tests",
        parameters={"suite": "backend/unit"},
        dependencies=["build_backend"]
    ) \
    .add_step(
        name="unit_tests_frontend",
        action="run_tests",
        parameters={"suite": "frontend/unit"},
        dependencies=["build_frontend"]
    ) \
    .add_step(
        name="integration_tests",
        action="run_tests",
        parameters={"suite": "integration"},
        dependencies=["unit_tests_backend", "unit_tests_frontend"]
    ) \
    .add_conditional_step(
        name="decide_deployment",
        condition=lambda ctx: ctx.get("test_results").all_passed,
        true_step=ConditionalStep(
            name="deploy_production",
            action="deploy",
            parameters={"environment": "production"}
        ),
        false_step=ConditionalStep(
            name="notify_failure",
            action="send_notification",
            parameters={"message": "Tests failed, deployment skipped"}
        ),
        dependencies=["integration_tests"]
    ) \
    .build()

engine = WorkflowEngine()
result = engine.execute_workflow(workflow, parallel=True)
```

## Best Practices

### 1. Choose the Right Pattern

- Analyze your requirements carefully
- Consider performance vs. complexity tradeoffs
- Start simple, add complexity only when needed

### 2. Combine Patterns Wisely

- Patterns can be combined for complex workflows
- Ensure combinations don't create conflicts
- Document pattern usage for maintainability

### 3. Handle Errors Gracefully

- Always implement error handling
- Use retry patterns for transient errors
- Implement compensating actions for critical operations

### 4. Monitor and Optimize

- Track workflow execution metrics
- Identify bottlenecks
- Optimize based on real-world usage

## Tài Liệu Liên Quan

- [Workflow Overview](overview.md) - Tổng quan về workflows
- [Building Workflows](building-workflows.md) - Xây dựng workflows
- [Advanced Workflows](advanced-workflows.md) - Workflows nâng cao
