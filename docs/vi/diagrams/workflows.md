# Sơ Đồ Workflows

**Phiên bản**: 3.0.0  
**Cập nhật lần cuối**: 11/02/2026


## Tổng Quan

Tài liệu này cung cấp các sơ đồ sequence chi tiết cho các workflows phổ biến trong Agentic SDLC v3.0.0, giúp bạn hiểu rõ luồng thực thi và tương tác giữa các components.

## Basic Workflows

### Simple Agent Execution

```mermaid
sequenceDiagram
    participant User
    participant CLI
    participant AgentManager
    participant Agent
    participant ModelClient
    participant LLM
    
    User->>+CLI: Execute command
    CLI->>+AgentManager: Get agent
    AgentManager->>+Agent: Initialize
    Agent-->>-AgentManager: Agent ready
    AgentManager-->>-CLI: Agent instance
    
    CLI->>+Agent: Execute task
    Agent->>+ModelClient: Send prompt
    ModelClient->>+LLM: API request
    LLM-->>-ModelClient: Response
    ModelClient-->>-Agent: Parsed response
    Agent-->>-CLI: Task result
    CLI-->>-User: Display result
```text

### Sequential Workflow

```mermaid
sequenceDiagram
    participant User
    participant WorkflowEngine
    participant Step1
    participant Step2
    participant Step3
    participant Storage
    
    User->>+WorkflowEngine: Start workflow
    
    WorkflowEngine->>+Step1: Execute step 1
    Step1->>Storage: Save state
    Step1-->>-WorkflowEngine: Step 1 complete
    
    WorkflowEngine->>+Step2: Execute step 2
    Step2->>Storage: Save state
    Step2-->>-WorkflowEngine: Step 2 complete
    
    WorkflowEngine->>+Step3: Execute step 3
    Step3->>Storage: Save state
    Step3-->>-WorkflowEngine: Step 3 complete
    
    WorkflowEngine-->>-User: Workflow complete
```text

### Parallel Workflow

```mermaid
sequenceDiagram
    participant User
    participant WorkflowEngine
    participant Task1
    participant Task2
    participant Task3
    participant Aggregator
    
    User->>+WorkflowEngine: Start parallel workflow
    
    par Execute in parallel
        WorkflowEngine->>+Task1: Execute task 1
        and
        WorkflowEngine->>+Task2: Execute task 2
        and
        WorkflowEngine->>+Task3: Execute task 3
    end
    
    Task1-->>-Aggregator: Result 1
    Task2-->>-Aggregator: Result 2
    Task3-->>-Aggregator: Result 3
    
    Aggregator->>WorkflowEngine: Combined results
    WorkflowEngine-->>-User: Workflow complete
```text

## Advanced Workflows

### Conditional Workflow

```mermaid
sequenceDiagram
    participant User
    participant WorkflowEngine
    participant Condition
    participant PathA
    participant PathB
    participant Storage
    
    User->>+WorkflowEngine: Start workflow
    
    WorkflowEngine->>+Condition: Evaluate condition
    Condition-->>-WorkflowEngine: Condition result
    
    alt Condition is true
        WorkflowEngine->>+PathA: Execute path A
        PathA->>Storage: Save state
        PathA-->>-WorkflowEngine: Path A complete
    else Condition is false
        WorkflowEngine->>+PathB: Execute path B
        PathB->>Storage: Save state
        PathB-->>-WorkflowEngine: Path B complete
    end
    
    WorkflowEngine-->>-User: Workflow complete
```text

### Error Handling Workflow

```mermaid
sequenceDiagram
    participant User
    participant WorkflowEngine
    participant Task
    participant ErrorHandler
    participant Retry
    participant Fallback
    
    User->>+WorkflowEngine: Start workflow
    
    WorkflowEngine->>+Task: Execute task
    Task-->>-WorkflowEngine: Error occurred
    
    WorkflowEngine->>+ErrorHandler: Handle error
    
    alt Retry available
        ErrorHandler->>+Retry: Retry task
        Retry->>Task: Execute again
        Task-->>-Retry: Success
        Retry-->>-ErrorHandler: Task succeeded
    else No retry or max retries
        ErrorHandler->>+Fallback: Execute fallback
        Fallback-->>-ErrorHandler: Fallback complete
    end
    
    ErrorHandler-->>-WorkflowEngine: Error handled
    WorkflowEngine-->>-User: Workflow complete
```text

### Workflow with Intelligence

```mermaid
sequenceDiagram
    participant User
    participant WorkflowEngine
    participant Reasoner
    participant Task
    participant Learner
    participant Monitor
    
    User->>+WorkflowEngine: Start workflow
    
    WorkflowEngine->>+Reasoner: Analyze task
    Reasoner-->>-WorkflowEngine: Execution strategy
    
    WorkflowEngine->>+Task: Execute with strategy
    
    par Monitor execution
        Task->>Monitor: Send metrics
    end
    
    Task-->>-WorkflowEngine: Task complete
    
    WorkflowEngine->>+Learner: Learn from execution
    Learner-->>-WorkflowEngine: Learning complete
    
    WorkflowEngine-->>-User: Workflow complete
```text

## Real-World Workflows

### Code Review Workflow

```mermaid
sequenceDiagram
    participant Developer
    participant GitHub
    participant WorkflowEngine
    participant CodeAnalyzer
    participant SecurityChecker
    participant TestRunner
    participant Reviewer
    participant Reporter
    
    Developer->>+GitHub: Push code
    GitHub->>+WorkflowEngine: Trigger webhook
    
    WorkflowEngine->>+CodeAnalyzer: Analyze code quality
    CodeAnalyzer-->>-WorkflowEngine: Quality report
    
    WorkflowEngine->>+SecurityChecker: Check security
    SecurityChecker-->>-WorkflowEngine: Security report
    
    WorkflowEngine->>+TestRunner: Run tests
    TestRunner-->>-WorkflowEngine: Test results
    
    WorkflowEngine->>+Reviewer: Review code
    Reviewer-->>-WorkflowEngine: Review comments
    
    WorkflowEngine->>+Reporter: Generate report
    Reporter-->>-WorkflowEngine: Final report
    
    WorkflowEngine->>GitHub: Post review
    GitHub-->>-Developer: Notification
```text

### CI/CD Pipeline Workflow

```mermaid
sequenceDiagram
    participant Developer
    participant Git
    participant CI
    participant Build
    participant Test
    participant Deploy
    participant Monitor
    
    Developer->>+Git: Commit & push
    Git->>+CI: Trigger pipeline
    
    CI->>+Build: Build application
    Build-->>-CI: Build artifacts
    
    CI->>+Test: Run test suite
    
    par Run tests in parallel
        Test->>Test: Unit tests
        and
        Test->>Test: Integration tests
        and
        Test->>Test: E2E tests
    end
    
    Test-->>-CI: Test results
    
    alt Tests passed
        CI->>+Deploy: Deploy to staging
        Deploy-->>-CI: Deployment complete
        
        CI->>+Monitor: Start monitoring
        Monitor-->>-CI: Monitoring active
        
        CI->>+Deploy: Deploy to production
        Deploy-->>-CI: Production deployed
    else Tests failed
        CI->>Developer: Notify failure
    end
    
    CI-->>-Developer: Pipeline complete
```text

### Feature Development Workflow

```mermaid
sequenceDiagram
    participant PM
    participant SA
    participant Dev
    participant Tester
    participant Reviewer
    participant Deployer
    
    PM->>+SA: Create requirements
    SA->>SA: Analyze requirements
    SA-->>-PM: Requirements document
    
    PM->>+Dev: Assign development
    Dev->>Dev: Implement feature
    Dev->>+Tester: Request testing
    
    Tester->>Tester: Run tests
    
    alt Tests passed
        Tester-->>-Dev: Tests passed
        Dev->>+Reviewer: Request review
        Reviewer->>Reviewer: Review code
        
        alt Review approved
            Reviewer-->>-Dev: Approved
            Dev->>+Deployer: Deploy feature
            Deployer-->>-PM: Feature deployed
        else Changes requested
            Reviewer-->>Dev: Request changes
            Dev->>Dev: Make changes
            Dev->>Reviewer: Re-submit
        end
    else Tests failed
        Tester-->>Dev: Tests failed
        Dev->>Dev: Fix issues
        Dev->>Tester: Re-test
    end
```text

### Automated Testing Workflow

```mermaid
sequenceDiagram
    participant Trigger
    participant TestOrchestrator
    participant TestGenerator
    participant TestRunner
    participant ResultAnalyzer
    participant SelfHealer
    participant Reporter
    
    Trigger->>+TestOrchestrator: Start testing
    
    TestOrchestrator->>+TestGenerator: Generate tests
    TestGenerator-->>-TestOrchestrator: Test suite
    
    TestOrchestrator->>+TestRunner: Execute tests
    TestRunner-->>-TestOrchestrator: Test results
    
    TestOrchestrator->>+ResultAnalyzer: Analyze results
    ResultAnalyzer-->>-TestOrchestrator: Analysis report
    
    alt Tests failed
        TestOrchestrator->>+SelfHealer: Attempt self-healing
        SelfHealer->>SelfHealer: Fix issues
        SelfHealer->>TestRunner: Re-run tests
        TestRunner-->>-SelfHealer: New results
        SelfHealer-->>TestOrchestrator: Healing complete
    end
    
    TestOrchestrator->>+Reporter: Generate report
    Reporter-->>-TestOrchestrator: Final report
    
    TestOrchestrator-->>-Trigger: Testing complete
```text

### Intelligent Project Management Workflow

```mermaid
sequenceDiagram
    participant PM
    participant Reasoner
    participant TaskAnalyzer
    participant ComplexityEstimator
    participant ResourceAllocator
    participant Scheduler
    participant Monitor
    
    PM->>+Reasoner: Submit project plan
    
    Reasoner->>+TaskAnalyzer: Analyze tasks
    TaskAnalyzer-->>-Reasoner: Task breakdown
    
    Reasoner->>+ComplexityEstimator: Estimate complexity
    ComplexityEstimator-->>-Reasoner: Complexity scores
    
    Reasoner->>+ResourceAllocator: Allocate resources
    ResourceAllocator-->>-Reasoner: Resource plan
    
    Reasoner->>+Scheduler: Create schedule
    Scheduler-->>-Reasoner: Project timeline
    
    Reasoner-->>-PM: Project plan
    
    PM->>+Monitor: Start monitoring
    
    loop Daily monitoring
        Monitor->>Monitor: Track progress
        Monitor->>PM: Status updates
        
        alt Behind schedule
            Monitor->>Reasoner: Request optimization
            Reasoner->>ResourceAllocator: Reallocate resources
            ResourceAllocator-->>Monitor: Updated plan
        end
    end
```text

## Workflow Patterns

### Fan-Out/Fan-In Pattern

```mermaid
sequenceDiagram
    participant Coordinator
    participant Worker1
    participant Worker2
    participant Worker3
    participant Aggregator
    
    Coordinator->>+Worker1: Task 1
    Coordinator->>+Worker2: Task 2
    Coordinator->>+Worker3: Task 3
    
    Worker1-->>-Aggregator: Result 1
    Worker2-->>-Aggregator: Result 2
    Worker3-->>-Aggregator: Result 3
    
    Aggregator->>Coordinator: Combined result
```text

### Pipeline Pattern

```mermaid
sequenceDiagram
    participant Input
    participant Stage1
    participant Stage2
    participant Stage3
    participant Output
    
    Input->>+Stage1: Data
    Stage1->>Stage1: Process
    Stage1->>+Stage2: Transformed data
    Stage2->>Stage2: Process
    Stage2->>+Stage3: Transformed data
    Stage3->>Stage3: Process
    Stage3-->>-Output: Final result
```text

### Saga Pattern (Distributed Transaction)

```mermaid
sequenceDiagram
    participant Coordinator
    participant Service1
    participant Service2
    participant Service3
    
    Coordinator->>+Service1: Execute step 1
    Service1-->>-Coordinator: Success
    
    Coordinator->>+Service2: Execute step 2
    Service2-->>-Coordinator: Success
    
    Coordinator->>+Service3: Execute step 3
    Service3-->>-Coordinator: Failure
    
    Note over Coordinator: Compensate previous steps
    
    Coordinator->>+Service2: Compensate step 2
    Service2-->>-Coordinator: Compensated
    
    Coordinator->>+Service1: Compensate step 1
    Service1-->>-Coordinator: Compensated
```text

### Circuit Breaker Pattern

```mermaid
sequenceDiagram
    participant Client
    participant CircuitBreaker
    participant Service
    
    Client->>+CircuitBreaker: Request
    
    alt Circuit closed (normal)
        CircuitBreaker->>+Service: Forward request
        Service-->>-CircuitBreaker: Response
        CircuitBreaker-->>-Client: Response
    else Circuit open (failing)
        CircuitBreaker-->>Client: Fast fail
    else Circuit half-open (testing)
        CircuitBreaker->>+Service: Test request
        alt Success
            Service-->>-CircuitBreaker: Response
            Note over CircuitBreaker: Close circuit
            CircuitBreaker-->>Client: Response
        else Failure
            Service-->>CircuitBreaker: Error
            Note over CircuitBreaker: Keep circuit open
            CircuitBreaker-->>Client: Fast fail
        end
    end
```

## Best Practices

### Workflow Design

1. **Keep workflows simple**: Tránh tạo workflows quá phức tạp
2. **Use meaningful names**: Đặt tên rõ ràng cho steps và workflows
3. **Handle errors gracefully**: Luôn có error handling và fallback
4. **Make workflows idempotent**: Workflows có thể chạy lại an toàn
5. **Log everything**: Log tất cả steps để dễ debug

### Performance Optimization

1. **Parallelize when possible**: Chạy các tasks độc lập song song
2. **Use caching**: Cache kết quả của các operations tốn kém
3. **Implement timeouts**: Đặt timeout cho tất cả operations
4. **Monitor execution**: Theo dõi performance metrics
5. **Optimize critical paths**: Tối ưu các paths được thực thi thường xuyên

### Error Handling

1. **Retry transient failures**: Retry các lỗi tạm thời với exponential backoff
2. **Implement circuit breakers**: Ngăn chặn cascading failures
3. **Use compensation**: Implement compensation logic cho distributed transactions
4. **Fail fast**: Fail nhanh khi không thể recover
5. **Provide clear error messages**: Error messages phải rõ ràng và actionable

## Tài Liệu Liên Quan

- [Architecture Diagrams](architecture.md) - Sơ đồ kiến trúc hệ thống
- [Agent Interaction Diagrams](agent-interaction.md) - Sơ đồ tương tác agents
- [Data Flow Diagrams](data-flow.md) - Sơ đồ luồng dữ liệu
- [Building Workflows Guide](../guides/workflows/building-workflows.md) - Hướng dẫn xây dựng workflows
- [Advanced Workflows Guide](../guides/workflows/advanced-workflows.md) - Workflows nâng cao
