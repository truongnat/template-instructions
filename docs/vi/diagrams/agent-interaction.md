# Sơ Đồ Tương Tác Giữa Agents

**Phiên bản**: 3.0.0  
**Cập nhật lần cuối**: 11/02/2026


## Tổng Quan

Tài liệu này cung cấp các sơ đồ chi tiết về cách các agents tương tác và collaborate với nhau trong Agentic SDLC v3.0.0, giúp bạn hiểu rõ các patterns collaboration và communication protocols.

## Basic Agent Interactions

### Single Agent Execution

```mermaid
sequenceDiagram
    participant User
    participant Agent
    participant ModelClient
    participant Tools
    
    User->>+Agent: Submit task
    Agent->>+ModelClient: Generate plan
    ModelClient-->>-Agent: Execution plan
    
    loop For each step
        Agent->>+Tools: Execute tool
        Tools-->>-Agent: Tool result
        Agent->>ModelClient: Analyze result
        ModelClient-->>Agent: Next action
    end
    
    Agent-->>-User: Task complete
```text

### Two-Agent Collaboration

```mermaid
sequenceDiagram
    participant User
    participant Agent1 as Developer Agent
    participant Agent2 as Tester Agent
    participant Coordinator
    
    User->>+Coordinator: Submit feature request
    
    Coordinator->>+Agent1: Implement feature
    Agent1->>Agent1: Write code
    Agent1-->>-Coordinator: Code complete
    
    Coordinator->>+Agent2: Test feature
    Agent2->>Agent2: Run tests
    
    alt Tests passed
        Agent2-->>-Coordinator: Tests passed
        Coordinator-->>User: Feature complete
    else Tests failed
        Agent2-->>Coordinator: Tests failed
        Coordinator->>Agent1: Fix issues
        Agent1->>Agent1: Fix code
        Agent1-->>Coordinator: Fixes complete
        Coordinator->>Agent2: Re-test
    end
```text

### Multi-Agent Pipeline

```mermaid
sequenceDiagram
    participant PM as PM Agent
    participant SA as System Architect
    participant Dev as Developer Agent
    participant Tester as Tester Agent
    participant Deployer as Deployer Agent
    
    PM->>+SA: Requirements
    SA->>SA: Design system
    SA-->>-PM: Architecture
    
    PM->>+Dev: Implement
    Dev->>Dev: Write code
    Dev-->>-PM: Code ready
    
    PM->>+Tester: Test
    Tester->>Tester: Run tests
    Tester-->>-PM: Tests passed
    
    PM->>+Deployer: Deploy
    Deployer->>Deployer: Deploy to prod
    Deployer-->>-PM: Deployed
```text

## Advanced Collaboration Patterns

### Peer Review Pattern

```mermaid
sequenceDiagram
    participant Author as Author Agent
    participant Reviewer1 as Reviewer Agent 1
    participant Reviewer2 as Reviewer Agent 2
    participant Coordinator
    
    Author->>+Coordinator: Submit work
    
    par Request reviews
        Coordinator->>+Reviewer1: Review request
        and
        Coordinator->>+Reviewer2: Review request
    end
    
    Reviewer1->>Reviewer1: Analyze work
    Reviewer1-->>-Coordinator: Review 1
    
    Reviewer2->>Reviewer2: Analyze work
    Reviewer2-->>-Coordinator: Review 2
    
    Coordinator->>Coordinator: Aggregate reviews
    
    alt All approved
        Coordinator-->>Author: Approved
    else Changes requested
        Coordinator-->>Author: Revision needed
        Author->>Author: Make changes
        Author->>Coordinator: Re-submit
    end
```text

### Consensus Building Pattern

```mermaid
sequenceDiagram
    participant Coordinator
    participant Agent1
    participant Agent2
    participant Agent3
    participant Aggregator
    
    Coordinator->>+Agent1: Propose solution
    Coordinator->>+Agent2: Propose solution
    Coordinator->>+Agent3: Propose solution
    
    Agent1->>Agent1: Analyze
    Agent1-->>-Aggregator: Vote + reasoning
    
    Agent2->>Agent2: Analyze
    Agent2-->>-Aggregator: Vote + reasoning
    
    Agent3->>Agent3: Analyze
    Agent3-->>-Aggregator: Vote + reasoning
    
    Aggregator->>Aggregator: Calculate consensus
    
    alt Consensus reached
        Aggregator-->>Coordinator: Agreed solution
    else No consensus
        Aggregator-->>Coordinator: Conflicting views
        Coordinator->>Coordinator: Mediate
        Coordinator->>Agent1: Discuss differences
        Coordinator->>Agent2: Discuss differences
        Coordinator->>Agent3: Discuss differences
    end
```text

### Hierarchical Delegation Pattern

```mermaid
sequenceDiagram
    participant Manager as Manager Agent
    participant Lead1 as Team Lead 1
    participant Lead2 as Team Lead 2
    participant Worker1 as Worker Agent 1
    participant Worker2 as Worker Agent 2
    participant Worker3 as Worker Agent 3
    
    Manager->>+Lead1: Assign task group A
    Manager->>+Lead2: Assign task group B
    
    Lead1->>+Worker1: Subtask A1
    Lead1->>+Worker2: Subtask A2
    
    Lead2->>+Worker3: Subtask B1
    
    Worker1-->>-Lead1: A1 complete
    Worker2-->>-Lead1: A2 complete
    Lead1-->>-Manager: Group A complete
    
    Worker3-->>-Lead2: B1 complete
    Lead2-->>-Manager: Group B complete
    
    Manager->>Manager: Aggregate results
```text

### Expert Consultation Pattern

```mermaid
sequenceDiagram
    participant Primary as Primary Agent
    participant Expert1 as Security Expert
    participant Expert2 as Performance Expert
    participant Expert3 as UX Expert
    
    Primary->>Primary: Working on task
    
    Note over Primary: Need security advice
    Primary->>+Expert1: Consult on security
    Expert1->>Expert1: Analyze
    Expert1-->>-Primary: Security recommendations
    
    Note over Primary: Need performance advice
    Primary->>+Expert2: Consult on performance
    Expert2->>Expert2: Analyze
    Expert2-->>-Primary: Performance tips
    
    Note over Primary: Need UX advice
    Primary->>+Expert3: Consult on UX
    Expert3->>Expert3: Analyze
    Expert3-->>-Primary: UX suggestions
    
    Primary->>Primary: Integrate all advice
```text

## Real-World Collaboration Scenarios

### Code Review Collaboration

```mermaid
sequenceDiagram
    participant Dev as Developer Agent
    participant CodeAnalyzer as Code Analyzer
    participant SecurityAgent as Security Agent
    participant TestAgent as Test Agent
    participant SeniorDev as Senior Dev Agent
    
    Dev->>+CodeAnalyzer: Submit code
    CodeAnalyzer->>CodeAnalyzer: Analyze quality
    CodeAnalyzer-->>-Dev: Quality report
    
    Dev->>+SecurityAgent: Check security
    SecurityAgent->>SecurityAgent: Scan vulnerabilities
    SecurityAgent-->>-Dev: Security report
    
    Dev->>+TestAgent: Run tests
    TestAgent->>TestAgent: Execute test suite
    TestAgent-->>-Dev: Test results
    
    Dev->>+SeniorDev: Request review
    SeniorDev->>SeniorDev: Review code
    
    alt Issues found
        SeniorDev-->>Dev: Request changes
        Dev->>Dev: Fix issues
        Dev->>SeniorDev: Re-submit
    else Approved
        SeniorDev-->>-Dev: Approved
    end
```text

### Feature Development Team

```mermaid
sequenceDiagram
    participant PM as PM Agent
    participant Architect as Architect Agent
    participant Frontend as Frontend Dev
    participant Backend as Backend Dev
    participant Database as DB Engineer
    participant QA as QA Agent
    
    PM->>+Architect: Feature requirements
    Architect->>Architect: Design architecture
    Architect-->>-PM: Architecture plan
    
    PM->>Frontend: Implement UI
    PM->>Backend: Implement API
    PM->>Database: Design schema
    
    par Parallel development
        Frontend->>Frontend: Build UI
        and
        Backend->>Backend: Build API
        and
        Database->>Database: Create schema
    end
    
    Frontend->>Backend: Integrate with API
    Backend->>Database: Connect to DB
    
    Frontend-->>PM: UI complete
    Backend-->>PM: API complete
    Database-->>PM: Schema complete
    
    PM->>+QA: Test feature
    QA->>QA: Run tests
    
    alt Tests passed
        QA-->>-PM: Feature ready
    else Tests failed
        QA-->>PM: Issues found
        PM->>Frontend: Fix UI issues
        PM->>Backend: Fix API issues
    end
```text

### Incident Response Team

```mermaid
sequenceDiagram
    participant Monitor as Monitor Agent
    participant Coordinator as Incident Coordinator
    participant Investigator as Investigator Agent
    participant Fixer as Fixer Agent
    participant Communicator as Communication Agent
    
    Monitor->>Monitor: Detect issue
    Monitor->>+Coordinator: Alert incident
    
    Coordinator->>+Investigator: Investigate root cause
    Investigator->>Investigator: Analyze logs
    Investigator->>Investigator: Check metrics
    Investigator-->>-Coordinator: Root cause found
    
    Coordinator->>+Fixer: Fix issue
    Fixer->>Fixer: Apply fix
    Fixer-->>-Coordinator: Fix applied
    
    par Parallel communication
        Coordinator->>+Communicator: Notify stakeholders
        Communicator->>Communicator: Send updates
        Communicator-->>-Coordinator: Notifications sent
    end
    
    Coordinator->>Monitor: Verify resolution
    Monitor->>Monitor: Check health
    Monitor-->>Coordinator: Issue resolved
```text

### Research and Development Team

```mermaid
sequenceDiagram
    participant Lead as Research Lead
    participant Researcher1 as Researcher 1
    participant Researcher2 as Researcher 2
    participant Experimenter as Experimenter Agent
    participant Analyzer as Data Analyzer
    participant Reporter as Report Writer
    
    Lead->>+Researcher1: Research approach A
    Lead->>+Researcher2: Research approach B
    
    Researcher1->>Researcher1: Literature review
    Researcher1-->>-Lead: Findings A
    
    Researcher2->>Researcher2: Literature review
    Researcher2-->>-Lead: Findings B
    
    Lead->>+Experimenter: Design experiments
    Experimenter->>Experimenter: Run experiments
    Experimenter-->>-Lead: Experiment data
    
    Lead->>+Analyzer: Analyze data
    Analyzer->>Analyzer: Statistical analysis
    Analyzer-->>-Lead: Analysis results
    
    Lead->>+Reporter: Write report
    Reporter->>Reporter: Compile findings
    Reporter-->>-Lead: Final report
```text

### DevOps Pipeline Team

```mermaid
sequenceDiagram
    participant Dev as Developer Agent
    participant Builder as Build Agent
    participant Tester as Test Agent
    participant SecurityScanner as Security Scanner
    participant Deployer as Deploy Agent
    participant Monitor as Monitor Agent
    
    Dev->>+Builder: Commit code
    Builder->>Builder: Build application
    Builder-->>-Dev: Build artifacts
    
    Dev->>+Tester: Run tests
    Tester->>Tester: Execute test suite
    Tester-->>-Dev: Test results
    
    Dev->>+SecurityScanner: Security scan
    SecurityScanner->>SecurityScanner: Scan vulnerabilities
    SecurityScanner-->>-Dev: Security report
    
    alt All checks passed
        Dev->>+Deployer: Deploy to staging
        Deployer->>Deployer: Deploy
        Deployer-->>-Dev: Staging deployed
        
        Deployer->>+Monitor: Start monitoring
        Monitor->>Monitor: Check health
        Monitor-->>-Deployer: Health OK
        
        Dev->>Deployer: Deploy to production
        Deployer->>Deployer: Deploy
        Deployer-->>Dev: Production deployed
    else Checks failed
        Dev->>Dev: Fix issues
    end
```text

## Communication Patterns

### Broadcast Pattern

```mermaid
sequenceDiagram
    participant Broadcaster
    participant Agent1
    participant Agent2
    participant Agent3
    participant Agent4
    
    Broadcaster->>Agent1: Message
    Broadcaster->>Agent2: Message
    Broadcaster->>Agent3: Message
    Broadcaster->>Agent4: Message
    
    Agent1-->>Broadcaster: Ack
    Agent2-->>Broadcaster: Ack
    Agent3-->>Broadcaster: Ack
    Agent4-->>Broadcaster: Ack
```text

### Request-Reply Pattern

```mermaid
sequenceDiagram
    participant Requester
    participant Responder
    
    Requester->>+Responder: Request
    Responder->>Responder: Process
    Responder-->>-Requester: Reply
```text

### Publish-Subscribe Pattern

```mermaid
sequenceDiagram
    participant Publisher
    participant MessageBroker
    participant Subscriber1
    participant Subscriber2
    participant Subscriber3
    
    Subscriber1->>MessageBroker: Subscribe to topic
    Subscriber2->>MessageBroker: Subscribe to topic
    Subscriber3->>MessageBroker: Subscribe to topic
    
    Publisher->>MessageBroker: Publish message
    
    MessageBroker->>Subscriber1: Deliver message
    MessageBroker->>Subscriber2: Deliver message
    MessageBroker->>Subscriber3: Deliver message
```text

### Message Queue Pattern

```mermaid
sequenceDiagram
    participant Producer1
    participant Producer2
    participant Queue
    participant Consumer1
    participant Consumer2
    
    Producer1->>Queue: Enqueue task 1
    Producer2->>Queue: Enqueue task 2
    Producer1->>Queue: Enqueue task 3
    
    Consumer1->>Queue: Dequeue
    Queue-->>Consumer1: Task 1
    
    Consumer2->>Queue: Dequeue
    Queue-->>Consumer2: Task 2
    
    Consumer1->>Queue: Dequeue
    Queue-->>Consumer1: Task 3
```text

## Coordination Mechanisms

### Leader Election

```mermaid
sequenceDiagram
    participant Agent1
    participant Agent2
    participant Agent3
    participant Coordinator
    
    Note over Agent1,Agent3: Leader election starts
    
    Agent1->>Coordinator: Propose self
    Agent2->>Coordinator: Propose self
    Agent3->>Coordinator: Propose self
    
    Coordinator->>Coordinator: Evaluate proposals
    Coordinator->>Agent2: You are leader
    
    Agent2->>Agent1: Assign task
    Agent2->>Agent3: Assign task
```text

### Work Stealing

```mermaid
sequenceDiagram
    participant Worker1
    participant Worker2
    participant Queue1
    participant Queue2
    
    Note over Worker1: Queue1 has many tasks
    Note over Worker2: Queue2 is empty
    
    Worker2->>Queue1: Check for work
    Queue1-->>Worker2: Task available
    Worker2->>Queue1: Steal task
    Queue1-->>Worker2: Task transferred
    
    Worker2->>Worker2: Execute stolen task
```text

### Barrier Synchronization

```mermaid
sequenceDiagram
    participant Agent1
    participant Agent2
    participant Agent3
    participant Barrier
    
    par Phase 1
        Agent1->>Agent1: Work
        and
        Agent2->>Agent2: Work
        and
        Agent3->>Agent3: Work
    end
    
    Agent1->>Barrier: Arrive
    Agent2->>Barrier: Arrive
    Agent3->>Barrier: Arrive
    
    Note over Barrier: All arrived, release
    
    Barrier-->>Agent1: Continue
    Barrier-->>Agent2: Continue
    Barrier-->>Agent3: Continue
    
    par Phase 2
        Agent1->>Agent1: Work
        and
        Agent2->>Agent2: Work
        and
        Agent3->>Agent3: Work
    end
```

## Best Practices

### Agent Communication

1. **Use clear protocols**: Định nghĩa rõ ràng message formats và protocols
2. **Handle timeouts**: Đặt timeout cho tất cả communications
3. **Implement retries**: Retry failed communications với exponential backoff
4. **Use async when possible**: Sử dụng async communication để tránh blocking
5. **Log all interactions**: Log tất cả agent interactions để debug

### Collaboration Design

1. **Define clear roles**: Mỗi agent có role và responsibilities rõ ràng
2. **Minimize dependencies**: Giảm thiểu dependencies giữa agents
3. **Use coordination patterns**: Áp dụng proven coordination patterns
4. **Handle conflicts**: Có mechanism để resolve conflicts
5. **Monitor collaboration**: Theo dõi collaboration metrics

### Error Handling

1. **Graceful degradation**: Hệ thống vẫn hoạt động khi một agent fails
2. **Fallback mechanisms**: Có fallback khi primary agent không available
3. **Circuit breakers**: Ngăn chặn cascading failures
4. **Retry logic**: Retry transient failures
5. **Clear error messages**: Error messages phải rõ ràng và actionable

## Tài Liệu Liên Quan

- [Architecture Diagrams](architecture.md) - Sơ đồ kiến trúc hệ thống
- [Workflow Diagrams](workflows.md) - Sơ đồ workflows
- [Data Flow Diagrams](data-flow.md) - Sơ đồ luồng dữ liệu
- [Agent Guide](../guides/agents/overview.md) - Hướng dẫn về agents
- [Collaboration Guide](../guides/intelligence/collaboration.md) - Hướng dẫn collaboration
