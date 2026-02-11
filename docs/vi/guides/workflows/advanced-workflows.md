# Advanced Workflows

**Phiên bản**: 3.0.0  
**Cập nhật lần cuối**: 11/02/2026


## Giới Thiệu

Tài liệu này hướng dẫn các kỹ thuật nâng cao để xây dựng workflows phức tạp trong Agentic SDLC, bao gồm conditional execution, error handling, retry logic, và các patterns phức tạp khác.

## Conditional Execution (Thực Thi Có Điều Kiện)

### Dynamic Branching

Thực thi các nhánh khác nhau dựa trên runtime conditions.

#### Ví Dụ 1: Environment-Based Deployment

```python
from agentic_sdlc.orchestration.workflow import WorkflowBuilder, ConditionalStep
from agentic_sdlc.infrastructure.workflow_engine import WorkflowEngine

def should_deploy_to_prod(context):
    """Kiểm tra xem có nên deploy lên production không."""
    test_results = context.get("test_results")
    code_coverage = context.get("code_coverage")
    
    return (
        test_results.success_rate >= 0.95 and
        code_coverage >= 80 and
        context.get("branch") == "main"
    )

builder = WorkflowBuilder(name="conditional_deployment")

workflow = builder \
    .add_step(
        name="run_tests",
        action="execute_tests",
        parameters={"suite": "all"}
    ) \
    .add_step(
        name="calculate_coverage",
        action="measure_coverage",
        parameters={},
        dependencies=["run_tests"]
    ) \
    .add_conditional_step(
        name="deployment_decision",
        condition=should_deploy_to_prod,
        true_step=ConditionalStep(
            name="deploy_production",
            action="deploy",
            parameters={"environment": "production", "strategy": "blue-green"}
        ),
        false_step=ConditionalStep(
            name="deploy_staging",
            action="deploy",
            parameters={"environment": "staging"}
        ),
        dependencies=["calculate_coverage"]
    ) \
    .build()

engine = WorkflowEngine()
result = engine.execute_workflow(workflow)
```text

#### Ví Dụ 2: Multi-Way Branching

```python
def determine_processing_path(context):
    """Xác định path xử lý dựa trên data size."""
    data_size = context.get("data_size")
    
    if data_size < 1000:
        return "small"
    elif data_size < 100000:
        return "medium"
    else:
        return "large"

builder = WorkflowBuilder(name="adaptive_processing")

workflow = builder \
    .add_step(
        name="analyze_data",
        action="get_data_info",
        parameters={"source": "database"}
    ) \
    .add_multi_conditional_step(
        name="processing_decision",
        condition=determine_processing_path,
        branches={
            "small": ConditionalStep(
                name="process_small",
                action="single_thread_process",
                parameters={}
            ),
            "medium": ConditionalStep(
                name="process_medium",
                action="multi_thread_process",
                parameters={"threads": 4}
            ),
            "large": ConditionalStep(
                name="process_large",
                action="distributed_process",
                parameters={"nodes": 10}
            )
        },
        dependencies=["analyze_data"]
    ) \
    .build()

engine = WorkflowEngine()
result = engine.execute_workflow(workflow)
```text

### Dynamic Step Generation

Tạo steps động dựa trên runtime data.

```python
from agentic_sdlc.orchestration.workflow import DynamicWorkflowBuilder

def generate_test_steps(context):
    """Generate test steps cho mỗi module."""
    modules = context.get("modules")
    steps = []
    
    for module in modules:
        step = {
            "name": f"test_{module}",
            "action": "run_module_tests",
            "parameters": {"module": module},
            "dependencies": ["setup"]
        }
        steps.append(step)
    
    return steps

builder = DynamicWorkflowBuilder(name="dynamic_testing")

workflow = builder \
    .add_step(
        name="discover_modules",
        action="scan_codebase",
        parameters={"path": "src/"}
    ) \
    .add_step(
        name="setup",
        action="prepare_test_env",
        parameters={},
        dependencies=["discover_modules"]
    ) \
    .add_dynamic_steps(
        generator=generate_test_steps,
        dependencies=["setup"]
    ) \
    .add_step(
        name="aggregate_results",
        action="combine_test_results",
        parameters={},
        dependencies=["dynamic_steps"]
    ) \
    .build()

engine = WorkflowEngine()
result = engine.execute_workflow(workflow)
```text

## Advanced Error Handling

### Hierarchical Error Handling

Xử lý errors ở nhiều levels với fallback strategies.

```python
from agentic_sdlc.orchestration.workflow import ErrorHandler, ErrorStrategy

# Define error handlers
primary_handler = ErrorHandler(
    strategy=ErrorStrategy.RETRY,
    max_retries=3,
    retry_delay=5,
    backoff_multiplier=2
)

secondary_handler = ErrorHandler(
    strategy=ErrorStrategy.FALLBACK,
    fallback_action="use_cached_data"
)

final_handler = ErrorHandler(
    strategy=ErrorStrategy.COMPENSATE,
    compensate_action="rollback_changes"
)

builder = WorkflowBuilder(name="resilient_workflow")

workflow = builder \
    .add_step(
        name="fetch_live_data",
        action="api_call",
        parameters={"endpoint": "/live-data"},
        error_handlers=[primary_handler, secondary_handler, final_handler]
    ) \
    .add_step(
        name="process_data",
        action="transform",
        parameters={},
        dependencies=["fetch_live_data"]
    ) \
    .build()

engine = WorkflowEngine()
result = engine.execute_workflow(workflow)
```text

### Custom Error Recovery

Implement custom recovery logic cho specific errors.

```python
from agentic_sdlc.orchestration.workflow import CustomErrorHandler

class DatabaseErrorHandler(CustomErrorHandler):
    """Custom handler cho database errors."""
    
    def can_handle(self, error):
        """Check if this handler can handle the error."""
        return isinstance(error, DatabaseError)
    
    def handle(self, error, context):
        """Handle database error với custom logic."""
        if "connection timeout" in str(error):
            # Retry với different connection pool
            context.set("use_backup_db", True)
            return {"action": "retry", "delay": 10}
        elif "deadlock" in str(error):
            # Retry với exponential backoff
            return {"action": "retry", "delay": context.get("retry_count") * 5}
        else:
            # Fail và notify
            self.notify_admin(error)
            return {"action": "fail"}

builder = WorkflowBuilder(name="db_workflow")

workflow = builder \
    .add_step(
        name="database_operation",
        action="execute_query",
        parameters={"query": "SELECT * FROM users"},
        custom_error_handler=DatabaseErrorHandler()
    ) \
    .build()

engine = WorkflowEngine()
result = engine.execute_workflow(workflow)
```text

### Error Aggregation

Collect và analyze errors từ multiple steps.

```python
from agentic_sdlc.orchestration.workflow import ErrorAggregator

builder = WorkflowBuilder(name="error_tracking_workflow")

error_aggregator = ErrorAggregator(
    collect_all=True,
    fail_threshold=3,  # Fail workflow nếu có 3+ errors
    notify_on_error=True
)

workflow = builder \
    .add_step(
        name="step1",
        action="process_batch_1",
        parameters={},
        continue_on_error=True
    ) \
    .add_step(
        name="step2",
        action="process_batch_2",
        parameters={},
        continue_on_error=True
    ) \
    .add_step(
        name="step3",
        action="process_batch_3",
        parameters={},
        continue_on_error=True
    ) \
    .add_step(
        name="analyze_errors",
        action="error_analysis",
        parameters={},
        dependencies=["step1", "step2", "step3"]
    ) \
    .set_error_aggregator(error_aggregator) \
    .build()

engine = WorkflowEngine()
result = engine.execute_workflow(workflow)

# Access aggregated errors
if result.has_errors:
    for error in result.errors:
        print(f"Step: {error.step_name}, Error: {error.message}")
```text

## Advanced Retry Logic

### Exponential Backoff with Jitter

Implement sophisticated retry strategy với jitter để tránh thundering herd.

```python
from agentic_sdlc.orchestration.workflow import RetryConfig
import random

def exponential_backoff_with_jitter(attempt, base_delay=1, max_delay=60):
    """Calculate delay với exponential backoff và jitter."""
    delay = min(base_delay * (2 ** attempt), max_delay)
    jitter = random.uniform(0, delay * 0.1)  # 10% jitter
    return delay + jitter

retry_config = RetryConfig(
    max_attempts=5,
    delay_calculator=exponential_backoff_with_jitter,
    retry_on_exceptions=[TimeoutError, ConnectionError],
    retry_on_status_codes=[429, 500, 502, 503, 504]
)

builder = WorkflowBuilder(name="smart_retry_workflow")

workflow = builder \
    .add_step(
        name="api_call",
        action="http_request",
        parameters={"url": "https://api.example.com/data"},
        retry_config=retry_config
    ) \
    .build()

engine = WorkflowEngine()
result = engine.execute_workflow(workflow)
```text

### Conditional Retry

Retry dựa trên specific conditions.

```python
from agentic_sdlc.orchestration.workflow import ConditionalRetry

def should_retry(error, attempt, context):
    """Quyết định có nên retry không dựa trên error và context."""
    # Không retry nếu là validation error
    if isinstance(error, ValidationError):
        return False
    
    # Retry nếu là rate limit và chưa quá 5 lần
    if isinstance(error, RateLimitError) and attempt < 5:
        return True
    
    # Retry nếu là timeout và data size nhỏ
    if isinstance(error, TimeoutError) and context.get("data_size") < 1000:
        return True
    
    return False

conditional_retry = ConditionalRetry(
    should_retry_func=should_retry,
    max_attempts=10,
    base_delay=2
)

builder = WorkflowBuilder(name="conditional_retry_workflow")

workflow = builder \
    .add_step(
        name="smart_operation",
        action="process_data",
        parameters={},
        conditional_retry=conditional_retry
    ) \
    .build()

engine = WorkflowEngine()
result = engine.execute_workflow(workflow)
```text

### Circuit Breaker Integration

Kết hợp retry logic với circuit breaker pattern.

```python
from agentic_sdlc.orchestration.workflow import CircuitBreaker, RetryWithCircuitBreaker

circuit_breaker = CircuitBreaker(
    failure_threshold=5,
    success_threshold=2,
    timeout=60,
    half_open_max_calls=3
)

retry_with_cb = RetryWithCircuitBreaker(
    circuit_breaker=circuit_breaker,
    max_retries=3,
    retry_delay=5
)

builder = WorkflowBuilder(name="protected_retry_workflow")

workflow = builder \
    .add_step(
        name="external_service_call",
        action="call_service",
        parameters={"service": "payment-api"},
        retry_strategy=retry_with_cb
    ) \
    .build()

engine = WorkflowEngine()
result = engine.execute_workflow(workflow)
```text

## Complex Workflow Patterns

### Saga Pattern với Compensation

Implement distributed transaction với compensating actions.

```python
from agentic_sdlc.orchestration.workflow import SagaBuilder

saga_builder = SagaBuilder(name="order_processing_saga")

saga = saga_builder \
    .add_saga_step(
        name="reserve_inventory",
        action="reserve_items",
        parameters={"items": ["item1", "item2"]},
        compensation="release_items"
    ) \
    .add_saga_step(
        name="process_payment",
        action="charge_card",
        parameters={"amount": 100.00},
        compensation="refund_payment",
        dependencies=["reserve_inventory"]
    ) \
    .add_saga_step(
        name="create_shipment",
        action="schedule_delivery",
        parameters={"address": "123 Main St"},
        compensation="cancel_shipment",
        dependencies=["process_payment"]
    ) \
    .add_saga_step(
        name="send_confirmation",
        action="send_email",
        parameters={"template": "order_confirmation"},
        compensation="send_cancellation_email",
        dependencies=["create_shipment"]
    ) \
    .build()

engine = WorkflowEngine()
result = engine.execute_workflow(saga)

# Nếu bất kỳ step nào fail, compensating actions sẽ chạy theo thứ tự ngược lại
```text

### Event-Driven Workflow

Workflow trigger bởi events thay vì explicit calls.

```python
from agentic_sdlc.orchestration.workflow import EventDrivenWorkflowBuilder
from agentic_sdlc.infrastructure.event_bus import EventBus

event_bus = EventBus()

builder = EventDrivenWorkflowBuilder(
    name="event_driven_workflow",
    event_bus=event_bus
)

workflow = builder \
    .on_event(
        event_type="code.pushed",
        action="run_ci_pipeline",
        parameters={}
    ) \
    .on_event(
        event_type="tests.passed",
        action="deploy_staging",
        parameters={"environment": "staging"}
    ) \
    .on_event(
        event_type="approval.received",
        action="deploy_production",
        parameters={"environment": "production"}
    ) \
    .build()

# Workflow sẽ tự động trigger khi events xảy ra
event_bus.publish("code.pushed", {"commit": "abc123"})
```text

### State Machine Workflow

Workflow với explicit state transitions.

```python
from agentic_sdlc.orchestration.workflow import StateMachineBuilder

sm_builder = StateMachineBuilder(name="deployment_state_machine")

state_machine = sm_builder \
    .add_state(
        name="pending",
        on_enter="validate_deployment",
        transitions={
            "approved": "building",
            "rejected": "cancelled"
        }
    ) \
    .add_state(
        name="building",
        on_enter="build_application",
        transitions={
            "success": "testing",
            "failure": "failed"
        }
    ) \
    .add_state(
        name="testing",
        on_enter="run_tests",
        transitions={
            "passed": "deploying",
            "failed": "failed"
        }
    ) \
    .add_state(
        name="deploying",
        on_enter="deploy_to_production",
        transitions={
            "success": "completed",
            "failure": "failed"
        }
    ) \
    .add_state(
        name="completed",
        on_enter="send_success_notification",
        is_final=True
    ) \
    .add_state(
        name="failed",
        on_enter="send_failure_notification",
        is_final=True
    ) \
    .add_state(
        name="cancelled",
        on_enter="cleanup_resources",
        is_final=True
    ) \
    .set_initial_state("pending") \
    .build()

engine = WorkflowEngine()
result = engine.execute_workflow(state_machine)
```text

## Real-World Examples

### Example 1: Intelligent Code Review Workflow

```python
builder = WorkflowBuilder(name="intelligent_code_review")

workflow = builder \
    .add_step(
        name="fetch_pr",
        action="github_get_pr",
        parameters={"pr_number": "${pr_number}"}
    ) \
    .add_step(
        name="analyze_changes",
        action="agent_execute",
        parameters={
            "agent_id": "code_analyzer",
            "task": "Analyze code changes"
        },
        dependencies=["fetch_pr"]
    ) \
    .add_conditional_step(
        name="determine_review_depth",
        condition=lambda ctx: ctx.get("change_complexity") > 0.7,
        true_step=ConditionalStep(
            name="deep_review",
            action="comprehensive_review",
            parameters={"depth": "deep"}
        ),
        false_step=ConditionalStep(
            name="quick_review",
            action="standard_review",
            parameters={"depth": "standard"}
        ),
        dependencies=["analyze_changes"]
    ) \
    .add_step(
        name="security_scan",
        action="agent_execute",
        parameters={
            "agent_id": "security_scanner",
            "task": "Scan for security issues"
        },
        dependencies=["analyze_changes"],
        retry_count=2
    ) \
    .add_step(
        name="performance_analysis",
        action="agent_execute",
        parameters={
            "agent_id": "performance_analyzer",
            "task": "Analyze performance impact"
        },
        dependencies=["analyze_changes"]
    ) \
    .add_step(
        name="aggregate_feedback",
        action="combine_reviews",
        parameters={},
        dependencies=["determine_review_depth", "security_scan", "performance_analysis"]
    ) \
    .add_conditional_step(
        name="approval_decision",
        condition=lambda ctx: ctx.get("review_score") >= 8.0,
        true_step=ConditionalStep(
            name="approve_pr",
            action="github_approve_pr",
            parameters={}
        ),
        false_step=ConditionalStep(
            name="request_changes",
            action="github_request_changes",
            parameters={}
        ),
        dependencies=["aggregate_feedback"]
    ) \
    .build()

engine = WorkflowEngine()
result = engine.execute_workflow(workflow, parallel=True)
```text

### Example 2: Adaptive CI/CD Pipeline

```python
builder = WorkflowBuilder(name="adaptive_cicd")

workflow = builder \
    .add_step(
        name="checkout",
        action="git_checkout",
        parameters={"branch": "${branch}"},
        retry_count=3
    ) \
    .add_step(
        name="detect_changes",
        action="git_diff_analysis",
        parameters={},
        dependencies=["checkout"]
    ) \
    .add_dynamic_steps(
        generator=lambda ctx: generate_build_steps(ctx.get("changed_modules")),
        dependencies=["detect_changes"]
    ) \
    .add_step(
        name="parallel_tests",
        action="run_test_suite",
        parameters={"parallel": True},
        dependencies=["dynamic_steps"],
        timeout=1800
    ) \
    .add_conditional_step(
        name="deployment_strategy",
        condition=lambda ctx: determine_deployment_strategy(ctx),
        branches={
            "canary": ConditionalStep(
                name="canary_deployment",
                action="deploy_canary",
                parameters={"percentage": 10}
            ),
            "blue_green": ConditionalStep(
                name="blue_green_deployment",
                action="deploy_blue_green",
                parameters={}
            ),
            "rolling": ConditionalStep(
                name="rolling_deployment",
                action="deploy_rolling",
                parameters={"batch_size": 5}
            )
        },
        dependencies=["parallel_tests"]
    ) \
    .add_step(
        name="health_check",
        action="monitor_deployment",
        parameters={"duration": 300},
        dependencies=["deployment_strategy"],
        retry_count=5,
        retry_delay=10
    ) \
    .add_conditional_step(
        name="rollback_decision",
        condition=lambda ctx: ctx.get("health_check_passed"),
        true_step=ConditionalStep(
            name="complete_deployment",
            action="finalize_deployment",
            parameters={}
        ),
        false_step=ConditionalStep(
            name="rollback",
            action="rollback_deployment",
            parameters={}
        ),
        dependencies=["health_check"]
    ) \
    .build()

engine = WorkflowEngine()
result = engine.execute_workflow(workflow, parallel=True)
```text

### Example 3: Feature Development Workflow

```python
saga_builder = SagaBuilder(name="feature_development")

saga = saga_builder \
    .add_saga_step(
        name="create_branch",
        action="git_create_branch",
        parameters={"branch_name": "feature/${feature_name}"},
        compensation="delete_branch"
    ) \
    .add_saga_step(
        name="generate_boilerplate",
        action="agent_execute",
        parameters={
            "agent_id": "code_generator",
            "task": "Generate boilerplate code"
        },
        compensation="remove_generated_files",
        dependencies=["create_branch"]
    ) \
    .add_saga_step(
        name="implement_feature",
        action="agent_execute",
        parameters={
            "agent_id": "developer",
            "task": "Implement feature logic"
        },
        compensation="revert_implementation",
        dependencies=["generate_boilerplate"],
        retry_count=2
    ) \
    .add_saga_step(
        name="write_tests",
        action="agent_execute",
        parameters={
            "agent_id": "tester",
            "task": "Write comprehensive tests"
        },
        compensation="remove_tests",
        dependencies=["implement_feature"]
    ) \
    .add_saga_step(
        name="run_tests",
        action="execute_tests",
        parameters={"suite": "all"},
        compensation="none",
        dependencies=["write_tests"]
    ) \
    .add_saga_step(
        name="code_review",
        action="agent_execute",
        parameters={
            "agent_id": "reviewer",
            "task": "Review code quality"
        },
        compensation="none",
        dependencies=["run_tests"]
    ) \
    .add_saga_step(
        name="create_pr",
        action="github_create_pr",
        parameters={
            "title": "Feature: ${feature_name}",
            "base": "main"
        },
        compensation="close_pr",
        dependencies=["code_review"]
    ) \
    .build()

engine = WorkflowEngine()
result = engine.execute_workflow(saga)
```text

## Performance Optimization

### Parallel Execution Tuning

```python
from agentic_sdlc.orchestration.workflow import ParallelConfig

parallel_config = ParallelConfig(
    max_workers=10,
    worker_type="thread",  # or "process"
    timeout_per_step=300,
    fail_fast=False  # Continue even if some parallel steps fail
)

builder = WorkflowBuilder(name="optimized_workflow")

workflow = builder \
    .add_step("step1", ...) \
    .add_step("step2", ..., dependencies=["step1"]) \
    .add_step("step3", ..., dependencies=["step1"]) \
    .add_step("step4", ..., dependencies=["step1"]) \
    .set_parallel_config(parallel_config) \
    .build()

engine = WorkflowEngine()
result = engine.execute_workflow(workflow, parallel=True)
```text

### Caching Strategy

```python
from agentic_sdlc.orchestration.workflow import CacheConfig

cache_config = CacheConfig(
    enabled=True,
    ttl=3600,  # 1 hour
    cache_key_generator=lambda params: f"{params['module']}_{params['version']}"
)

builder = WorkflowBuilder(name="cached_workflow")

workflow = builder \
    .add_step(
        name="expensive_operation",
        action="analyze_codebase",
        parameters={"module": "core"},
        cache_config=cache_config
    ) \
    .build()
```

## Tài Liệu Liên Quan

- [Workflow Overview](overview.md) - Tổng quan về workflows
- [Building Workflows](building-workflows.md) - Xây dựng workflows cơ bản
- [Workflow Patterns](workflow-patterns.md) - Các patterns phổ biến
- [Agent Documentation](../agents/overview.md) - Tìm hiểu về agents
