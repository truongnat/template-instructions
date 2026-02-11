# Suy Luận (Reasoning)

**Phiên bản**: 3.0.0  
**Cập nhật lần cuối**: 11/02/2026


## Giới Thiệu

Reasoner là component trong Intelligence Layer cung cấp khả năng phân tích, đánh giá và ra quyết định thông minh cho hệ thống Agentic SDLC. Component này giúp hệ thống tự động phân tích độ phức tạp của tasks, đề xuất execution mode phù hợp, và routing tasks đến agents thích hợp.

## Yêu Cầu Tiên Quyết

- Đã cài đặt Agentic SDLC v3.0.0 hoặc cao hơn
- Hiểu biết cơ bản về agents và workflows
- Python 3.8+

## Mục Tiêu Học Tập

Sau khi hoàn thành tài liệu này, bạn sẽ có thể:
- Phân tích độ phức tạp của tasks
- Đề xuất execution mode tối ưu (sequential, parallel, distributed)
- Routing tasks đến agents phù hợp
- Tối ưu hóa resource allocation
- Xây dựng intelligent decision-making systems

## Khái Niệm Cơ Bản

### Reasoner là gì?

Reasoner là một component cho phép:
- **Task Analysis**: Phân tích và đánh giá độ phức tạp của tasks
- **Execution Planning**: Đề xuất cách thực thi tối ưu
- **Agent Selection**: Chọn agent phù hợp nhất cho từng task
- **Resource Optimization**: Tối ưu hóa việc sử dụng resources

### Các Chức Năng Chính

1. **analyze_task_complexity**: Đánh giá độ phức tạp của task
2. **recommend_execution_mode**: Đề xuất mode thực thi (sequential, parallel, distributed)
3. **route_task**: Routing task đến agent phù hợp nhất
4. **optimize_workflow**: Tối ưu hóa workflow execution plan

## Sử Dụng Reasoner

### Khởi Tạo Reasoner

```python
from agentic_sdlc.intelligence import Reasoner

# Tạo Reasoner instance
reasoner = Reasoner(
    model_name="gpt-4",              # LLM model cho reasoning
    knowledge_base="./reasoning_kb", # Knowledge base path
    use_learning=True                # Sử dụng learning data
)
```text

### Phân Tích Task Complexity

```python
from agentic_sdlc.intelligence import Reasoner

reasoner = Reasoner(model_name="gpt-4")

# Task cần phân tích
task = {
    "type": "feature_development",
    "description": "Implement user authentication with OAuth2",
    "requirements": [
        "Support Google and GitHub OAuth",
        "JWT token management",
        "User session handling",
        "Password reset flow"
    ],
    "estimated_lines": 500,
    "dependencies": ["database", "email_service", "oauth_providers"]
}

# Phân tích complexity
complexity_analysis = reasoner.analyze_task_complexity(task)

print(f"Task Complexity Analysis:")
print(f"Overall Complexity: {complexity_analysis.level}")  # low, medium, high, very_high
print(f"Complexity Score: {complexity_analysis.score}/100")
print(f"\nFactors:")
for factor, value in complexity_analysis.factors.items():
    print(f"  {factor}: {value}")

print(f"\nRecommendations:")
for rec in complexity_analysis.recommendations:
    print(f"  - {rec}")

# Ví dụ output:
# Task Complexity Analysis:
# Overall Complexity: high
# Complexity Score: 78/100
#
# Factors:
#   technical_complexity: high
#   scope: medium
#   dependencies: high
#   estimated_effort: 3-5 days
#   risk_level: medium
#
# Recommendations:
#   - Break down into smaller subtasks
#   - Assign to senior developer
#   - Allocate 4-5 days for implementation
#   - Plan for integration testing
```text

### Đề Xuất Execution Mode

```python
from agentic_sdlc.intelligence import Reasoner

reasoner = Reasoner(model_name="gpt-4")

# Workflow cần phân tích
workflow = {
    "name": "code_review_pipeline",
    "steps": [
        {"name": "lint_check", "estimated_time": 30, "dependencies": []},
        {"name": "type_check", "estimated_time": 45, "dependencies": []},
        {"name": "security_scan", "estimated_time": 60, "dependencies": []},
        {"name": "code_review", "estimated_time": 300, "dependencies": ["lint_check", "type_check"]},
        {"name": "integration_test", "estimated_time": 180, "dependencies": ["code_review"]},
    ],
    "total_steps": 5,
    "available_resources": {
        "agents": 3,
        "cpu_cores": 4,
        "memory_gb": 8
    }
}

# Đề xuất execution mode
recommendation = reasoner.recommend_execution_mode(workflow)

print(f"Execution Mode Recommendation:")
print(f"Recommended Mode: {recommendation.mode}")  # sequential, parallel, distributed
print(f"Confidence: {recommendation.confidence}%")
print(f"\nReasoning:")
print(f"  {recommendation.reasoning}")

print(f"\nExecution Plan:")
for phase in recommendation.execution_plan:
    print(f"  Phase {phase.number}: {phase.mode}")
    print(f"    Steps: {', '.join(phase.steps)}")
    print(f"    Estimated time: {phase.estimated_time}s")

print(f"\nExpected Benefits:")
for benefit in recommendation.benefits:
    print(f"  - {benefit}")

# Ví dụ output:
# Execution Mode Recommendation:
# Recommended Mode: hybrid
# Confidence: 85%
#
# Reasoning:
#   Steps lint_check, type_check, và security_scan có thể chạy parallel
#   vì không có dependencies. Code_review và integration_test phải chạy
#   sequential sau khi dependencies hoàn thành.
#
# Execution Plan:
#   Phase 1: parallel
#     Steps: lint_check, type_check, security_scan
#     Estimated time: 60s
#   Phase 2: sequential
#     Steps: code_review
#     Estimated time: 300s
#   Phase 3: sequential
#     Steps: integration_test
#     Estimated time: 180s
#
# Expected Benefits:
#   - Giảm total execution time từ 615s xuống 540s (12% faster)
#   - Tối ưu resource utilization
#   - Maintain dependency constraints
```text

### Routing Tasks Đến Agents

```python
from agentic_sdlc.intelligence import Reasoner
from agentic_sdlc.orchestration import create_agent

reasoner = Reasoner(model_name="gpt-4")

# Danh sách available agents
agents = [
    create_agent(name="junior_dev", role="DEV", model_name="gpt-3.5-turbo",
                 skills=["python", "javascript"], experience_level="junior"),
    create_agent(name="senior_dev", role="DEV", model_name="gpt-4",
                 skills=["python", "javascript", "system_design"], experience_level="senior"),
    create_agent(name="security_expert", role="SECURITY", model_name="gpt-4",
                 skills=["security", "penetration_testing"], experience_level="expert"),
    create_agent(name="reviewer", role="REVIEWER", model_name="gpt-4",
                 skills=["code_review", "best_practices"], experience_level="senior"),
]

# Task cần routing
task = {
    "type": "security_audit",
    "description": "Audit authentication system for vulnerabilities",
    "required_skills": ["security", "authentication"],
    "complexity": "high",
    "priority": "critical"
}

# Route task đến agent phù hợp
routing_decision = reasoner.route_task(task, agents)

print(f"Task Routing Decision:")
print(f"Selected Agent: {routing_decision.agent.name}")
print(f"Confidence: {routing_decision.confidence}%")
print(f"\nReasoning:")
print(f"  {routing_decision.reasoning}")

print(f"\nAgent Capabilities:")
for capability, score in routing_decision.capability_match.items():
    print(f"  {capability}: {score}/100")

print(f"\nAlternative Agents:")
for alt in routing_decision.alternatives:
    print(f"  - {alt.agent.name} (confidence: {alt.confidence}%)")

# Ví dụ output:
# Task Routing Decision:
# Selected Agent: security_expert
# Confidence: 95%
#
# Reasoning:
#   security_expert có expertise về security và authentication,
#   experience level expert phù hợp với high complexity task,
#   và priority critical yêu cầu agent có skill cao nhất.
#
# Agent Capabilities:
#   skill_match: 100/100
#   experience_match: 95/100
#   availability: 90/100
#   past_performance: 92/100
#
# Alternative Agents:
#   - senior_dev (confidence: 65%)
#   - reviewer (confidence: 45%)
```text

## Ví Dụ Thực Tế

### Ví Dụ 1: Intelligent Task Dispatcher

```python
from agentic_sdlc.intelligence import Reasoner
from agentic_sdlc.orchestration import create_agent
from typing import List, Dict

class IntelligentTaskDispatcher:
    """Dispatcher tự động phân tích và routing tasks."""
    
    def __init__(self, agents: List):
        self.reasoner = Reasoner(model_name="gpt-4", use_learning=True)
        self.agents = agents
    
    def dispatch_task(self, task: Dict):
        """Phân tích task và dispatch đến agent phù hợp."""
        
        # Bước 1: Phân tích complexity
        print(f"\n{'='*60}")
        print(f"Analyzing task: {task['description']}")
        print(f"{'='*60}")
        
        complexity = self.reasoner.analyze_task_complexity(task)
        print(f"\n1. Complexity Analysis:")
        print(f"   Level: {complexity.level}")
        print(f"   Score: {complexity.score}/100")
        
        # Bước 2: Route đến agent phù hợp
        routing = self.reasoner.route_task(task, self.agents)
        print(f"\n2. Agent Selection:")
        print(f"   Selected: {routing.agent.name}")
        print(f"   Confidence: {routing.confidence}%")
        print(f"   Reasoning: {routing.reasoning}")
        
        # Bước 3: Đề xuất execution strategy
        if complexity.level in ["high", "very_high"]:
            print(f"\n3. Execution Strategy:")
            print(f"   Recommendation: Break down into subtasks")
            
            # Tự động break down task
            subtasks = self._break_down_task(task, complexity)
            print(f"   Subtasks created: {len(subtasks)}")
            
            for i, subtask in enumerate(subtasks, 1):
                print(f"   {i}. {subtask['description']}")
            
            return {
                "strategy": "breakdown",
                "subtasks": subtasks,
                "primary_agent": routing.agent
            }
        else:
            print(f"\n3. Execution Strategy:")
            print(f"   Recommendation: Direct execution")
            
            return {
                "strategy": "direct",
                "agent": routing.agent,
                "task": task
            }
    
    def _break_down_task(self, task: Dict, complexity) -> List[Dict]:
        """Break down complex task thành subtasks."""
        # Sử dụng reasoner để break down
        subtasks = []
        
        # Implementation để break down dựa trên complexity analysis
        # và recommendations
        
        return subtasks

# Sử dụng
agents = [
    create_agent(name="dev1", role="DEV", model_name="gpt-4"),
    create_agent(name="dev2", role="DEV", model_name="gpt-3.5-turbo"),
    create_agent(name="reviewer", role="REVIEWER", model_name="gpt-4"),
]

dispatcher = IntelligentTaskDispatcher(agents)

# Dispatch các tasks
tasks = [
    {
        "type": "feature_development",
        "description": "Implement OAuth2 authentication",
        "requirements": ["Google OAuth", "GitHub OAuth", "JWT tokens"],
        "estimated_lines": 500
    },
    {
        "type": "bug_fix",
        "description": "Fix login button not responding",
        "estimated_lines": 20
    },
    {
        "type": "code_review",
        "description": "Review payment processing module",
        "files": ["payment.py", "transaction.py"]
    }
]

for task in tasks:
    result = dispatcher.dispatch_task(task)
    print(f"\nDispatch result: {result['strategy']}")
```text

### Ví Dụ 2: Adaptive Workflow Optimizer

```python
from agentic_sdlc.intelligence import Reasoner
from agentic_sdlc.orchestration import WorkflowBuilder

class AdaptiveWorkflowOptimizer:
    """Optimizer tự động tối ưu workflow execution."""
    
    def __init__(self):
        self.reasoner = Reasoner(model_name="gpt-4", use_learning=True)
    
    def optimize_workflow(self, workflow_definition: Dict):
        """Phân tích và tối ưu workflow."""
        
        print(f"Optimizing workflow: {workflow_definition['name']}")
        
        # Phân tích workflow
        analysis = self._analyze_workflow(workflow_definition)
        
        # Đề xuất execution mode
        mode_recommendation = self.reasoner.recommend_execution_mode(
            workflow_definition
        )
        
        print(f"\nExecution Mode: {mode_recommendation.mode}")
        print(f"Expected speedup: {mode_recommendation.speedup}x")
        
        # Tạo optimized workflow
        optimized = self._create_optimized_workflow(
            workflow_definition,
            mode_recommendation
        )
        
        # So sánh performance
        self._compare_performance(workflow_definition, optimized)
        
        return optimized
    
    def _analyze_workflow(self, workflow: Dict):
        """Phân tích workflow structure."""
        
        print(f"\nWorkflow Analysis:")
        print(f"  Total steps: {len(workflow['steps'])}")
        
        # Phân tích dependencies
        dependency_graph = self._build_dependency_graph(workflow['steps'])
        print(f"  Dependency chains: {len(dependency_graph)}")
        
        # Identify parallelizable steps
        parallel_groups = self._identify_parallel_groups(workflow['steps'])
        print(f"  Parallelizable groups: {len(parallel_groups)}")
        
        # Identify bottlenecks
        bottlenecks = self._identify_bottlenecks(workflow['steps'])
        if bottlenecks:
            print(f"  Bottlenecks found:")
            for bottleneck in bottlenecks:
                print(f"    - {bottleneck['step']}: {bottleneck['reason']}")
        
        return {
            "dependency_graph": dependency_graph,
            "parallel_groups": parallel_groups,
            "bottlenecks": bottlenecks
        }
    
    def _build_dependency_graph(self, steps):
        """Build dependency graph."""
        # Implementation
        return []
    
    def _identify_parallel_groups(self, steps):
        """Identify steps có thể chạy parallel."""
        # Implementation
        return []
    
    def _identify_bottlenecks(self, steps):
        """Identify performance bottlenecks."""
        # Implementation
        return []
    
    def _create_optimized_workflow(self, original, recommendation):
        """Tạo optimized workflow."""
        
        builder = WorkflowBuilder(name=f"{original['name']}_optimized")
        
        # Build workflow theo execution plan
        for phase in recommendation.execution_plan:
            if phase.mode == "parallel":
                # Add parallel steps
                for step_name in phase.steps:
                    step = self._find_step(original['steps'], step_name)
                    builder.add_step(
                        name=step['name'],
                        action=step['action'],
                        parallel=True
                    )
            else:
                # Add sequential steps
                for step_name in phase.steps:
                    step = self._find_step(original['steps'], step_name)
                    builder.add_step(
                        name=step['name'],
                        action=step['action'],
                        dependencies=step.get('dependencies', [])
                    )
        
        return builder.build()
    
    def _find_step(self, steps, name):
        """Find step by name."""
        return next(s for s in steps if s['name'] == name)
    
    def _compare_performance(self, original, optimized):
        """So sánh performance."""
        
        print(f"\nPerformance Comparison:")
        
        original_time = sum(s['estimated_time'] for s in original['steps'])
        optimized_time = self._calculate_optimized_time(optimized)
        
        print(f"  Original: {original_time}s")
        print(f"  Optimized: {optimized_time}s")
        print(f"  Improvement: {((original_time - optimized_time) / original_time * 100):.1f}%")
    
    def _calculate_optimized_time(self, workflow):
        """Calculate optimized execution time."""
        # Implementation để tính time với parallel execution
        return 0

# Sử dụng
optimizer = AdaptiveWorkflowOptimizer()

workflow_def = {
    "name": "ci_cd_pipeline",
    "steps": [
        {"name": "checkout", "estimated_time": 10, "dependencies": []},
        {"name": "lint", "estimated_time": 30, "dependencies": ["checkout"]},
        {"name": "test", "estimated_time": 120, "dependencies": ["checkout"]},
        {"name": "build", "estimated_time": 60, "dependencies": ["lint", "test"]},
        {"name": "deploy", "estimated_time": 45, "dependencies": ["build"]},
    ]
}

optimized_workflow = optimizer.optimize_workflow(workflow_def)
```text

### Ví Dụ 3: Smart Resource Allocator

```python
from agentic_sdlc.intelligence import Reasoner
from typing import List, Dict

class SmartResourceAllocator:
    """Allocator tự động phân bổ resources cho tasks."""
    
    def __init__(self, available_resources: Dict):
        self.reasoner = Reasoner(model_name="gpt-4")
        self.available_resources = available_resources
        self.allocated_resources = {}
    
    def allocate_resources(self, tasks: List[Dict]):
        """Phân bổ resources cho danh sách tasks."""
        
        print(f"Allocating resources for {len(tasks)} tasks")
        print(f"Available resources: {self.available_resources}")
        
        # Phân tích từng task
        task_analyses = []
        for task in tasks:
            complexity = self.reasoner.analyze_task_complexity(task)
            task_analyses.append({
                "task": task,
                "complexity": complexity,
                "priority": task.get("priority", "medium")
            })
        
        # Sắp xếp theo priority và complexity
        sorted_tasks = self._prioritize_tasks(task_analyses)
        
        # Phân bổ resources
        allocations = []
        remaining_resources = self.available_resources.copy()
        
        for task_analysis in sorted_tasks:
            task = task_analysis["task"]
            complexity = task_analysis["complexity"]
            
            # Tính toán resources cần thiết
            required = self._calculate_required_resources(complexity)
            
            # Kiểm tra availability
            if self._can_allocate(required, remaining_resources):
                allocation = {
                    "task": task["description"],
                    "resources": required,
                    "estimated_time": complexity.estimated_effort
                }
                allocations.append(allocation)
                
                # Update remaining resources
                for resource, amount in required.items():
                    remaining_resources[resource] -= amount
                
                print(f"\n✓ Allocated to: {task['description']}")
                print(f"  Resources: {required}")
            else:
                print(f"\n✗ Insufficient resources for: {task['description']}")
                print(f"  Required: {required}")
                print(f"  Available: {remaining_resources}")
        
        print(f"\nAllocation Summary:")
        print(f"  Tasks allocated: {len(allocations)}/{len(tasks)}")
        print(f"  Remaining resources: {remaining_resources}")
        
        return allocations
    
    def _prioritize_tasks(self, task_analyses):
        """Sắp xếp tasks theo priority và complexity."""
        
        priority_order = {"critical": 0, "high": 1, "medium": 2, "low": 3}
        
        return sorted(
            task_analyses,
            key=lambda x: (
                priority_order.get(x["priority"], 2),
                -x["complexity"].score  # Higher complexity first
            )
        )
    
    def _calculate_required_resources(self, complexity):
        """Tính toán resources cần thiết dựa trên complexity."""
        
        base_resources = {
            "agents": 1,
            "cpu_cores": 1,
            "memory_gb": 2
        }
        
        # Scale dựa trên complexity
        multiplier = {
            "low": 1.0,
            "medium": 1.5,
            "high": 2.0,
            "very_high": 3.0
        }.get(complexity.level, 1.0)
        
        return {
            resource: int(amount * multiplier)
            for resource, amount in base_resources.items()
        }
    
    def _can_allocate(self, required, available):
        """Kiểm tra có đủ resources không."""
        
        for resource, amount in required.items():
            if available.get(resource, 0) < amount:
                return False
        return True

# Sử dụng
allocator = SmartResourceAllocator(
    available_resources={
        "agents": 5,
        "cpu_cores": 8,
        "memory_gb": 16
    }
)

tasks = [
    {
        "description": "Implement authentication",
        "type": "feature_development",
        "priority": "critical",
        "estimated_lines": 500
    },
    {
        "description": "Fix login bug",
        "type": "bug_fix",
        "priority": "high",
        "estimated_lines": 20
    },
    {
        "description": "Add logging",
        "type": "enhancement",
        "priority": "low",
        "estimated_lines": 100
    },
    {
        "description": "Security audit",
        "type": "security",
        "priority": "critical",
        "estimated_lines": 0
    }
]

allocations = allocator.allocate_resources(tasks)
```text

## Best Practices

### 1. Cung Cấp Context Đầy Đủ Cho Analysis

```python
# ✓ Tốt: Context đầy đủ
task = {
    "type": "feature_development",
    "description": "Implement OAuth2 authentication",
    "requirements": ["Google OAuth", "GitHub OAuth", "JWT"],
    "estimated_lines": 500,
    "dependencies": ["database", "email_service"],
    "priority": "high",
    "deadline": "2024-03-01"
}

complexity = reasoner.analyze_task_complexity(task)

# ✗ Không tốt: Context thiếu
task = {"description": "Implement auth"}
complexity = reasoner.analyze_task_complexity(task)
```text

### 2. Sử Dụng Learning Data

```python
# Enable learning để cải thiện reasoning
reasoner = Reasoner(
    model_name="gpt-4",
    use_learning=True,
    knowledge_base="./reasoning_kb"
)
```text

### 3. Validate Routing Decisions

```python
# Kiểm tra confidence trước khi execute
routing = reasoner.route_task(task, agents)

if routing.confidence < 70:
    print(f"⚠ Low confidence ({routing.confidence}%), consider manual review")
    # Có thể fallback sang manual selection
else:
    selected_agent = routing.agent
```text

### 4. Monitor Reasoning Performance

```python
from agentic_sdlc.intelligence import Monitor

monitor = Monitor(storage_path="./monitoring_data")

# Monitor reasoning decisions
routing = reasoner.route_task(task, agents)

monitor.record_metric(
    metric_name="reasoning_decision",
    value=routing.confidence,
    tags={
        "decision_type": "task_routing",
        "selected_agent": routing.agent.name
    }
)
```text

### 5. Combine Multiple Reasoning Strategies

```python
# Sử dụng multiple factors cho decision making
def make_intelligent_decision(task, agents):
    # Phân tích complexity
    complexity = reasoner.analyze_task_complexity(task)
    
    # Route dựa trên complexity
    routing = reasoner.route_task(task, agents)
    
    # Đề xuất execution mode
    mode = reasoner.recommend_execution_mode({
        "steps": [task],
        "available_resources": get_available_resources()
    })
    
    # Combine tất cả factors
    return {
        "agent": routing.agent,
        "execution_mode": mode.mode,
        "estimated_time": complexity.estimated_effort
    }
```text

## Troubleshooting

### Reasoning Trả Về Kết Quả Không Chính Xác

**Nguyên nhân**: Thiếu context hoặc training data

**Giải pháp**:
```python
# Cung cấp more context
task = {
    **task,
    "context": {
        "project_type": "web_application",
        "tech_stack": ["python", "react"],
        "team_size": 5
    }
}

# Enable learning
reasoner = Reasoner(use_learning=True)
```text

### Low Confidence Scores

**Nguyên nhân**: Ambiguous task description hoặc không đủ agent information

**Giải pháp**:
```python
# Làm rõ task description
task["description"] = "Implement OAuth2 authentication with Google and GitHub providers, including JWT token management and session handling"

# Cung cấp detailed agent information
agents = [
    create_agent(
        name="dev1",
        role="DEV",
        model_name="gpt-4",
        skills=["python", "oauth", "security"],
        experience_level="senior",
        past_performance={"success_rate": 95}
    )
]
```text

### Reasoning Chậm

**Nguyên nhân**: Complex analysis hoặc large knowledge base

**Giải pháp**:
```python
# Sử dụng lighter model cho simple tasks
reasoner = Reasoner(
    model_name="gpt-3.5-turbo",  # Faster cho simple reasoning
    use_cache=True                # Cache reasoning results
)

# Hoặc limit knowledge base size
reasoner = Reasoner(
    knowledge_base="./reasoning_kb",
    max_kb_size=1000  # Limit số entries
)
```

## Tài Liệu Liên Quan

- [Learning](learning.md) - Học từ execution results
- [Monitoring](monitoring.md) - Theo dõi metrics và health
- [Collaboration](collaboration.md) - Phối hợp giữa các agents
- [Workflows](../workflows/overview.md) - Xây dựng workflows
- [API Reference - Reasoner](../../api-reference/intelligence/reasoner.md)
