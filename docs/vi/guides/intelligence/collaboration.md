# Cộng Tác (Collaboration)

**Phiên bản**: 3.0.0  
**Cập nhật lần cuối**: 11/02/2026


## Giới Thiệu

TeamCoordinator là component trong Intelligence Layer cho phép các agents phối hợp và cộng tác với nhau để hoàn thành các tasks phức tạp. Component này cung cấp khả năng giao tiếp giữa agents, quản lý sessions, và điều phối workflows multi-agent.

## Yêu Cầu Tiên Quyết

- Đã cài đặt Agentic SDLC v3.0.0 hoặc cao hơn
- Hiểu biết cơ bản về agents và workflows
- Python 3.8+

## Mục Tiêu Học Tập

Sau khi hoàn thành tài liệu này, bạn sẽ có thể:
- Tạo và quản lý collaboration sessions
- Giao tiếp giữa các agents
- Điều phối multi-agent workflows
- Xử lý conflicts và dependencies
- Xây dựng intelligent team coordination systems

## Khái Niệm Cơ Bản

### TeamCoordinator là gì?

TeamCoordinator là một component cho phép:
- **Agent Registration**: Đăng ký agents vào collaboration sessions
- **Message Passing**: Giao tiếp giữa agents thông qua messages
- **Session Management**: Quản lý lifecycle của collaboration sessions
- **Conflict Resolution**: Giải quyết conflicts khi nhiều agents làm việc cùng lúc

### Các Chức Năng Chính

1. **create_session**: Tạo collaboration session mới
2. **register_agent**: Đăng ký agent vào session
3. **send_message**: Gửi message giữa agents
4. **coordinate_workflow**: Điều phối multi-agent workflow
5. **resolve_conflict**: Giải quyết conflicts

## Sử Dụng TeamCoordinator

### Khởi Tạo TeamCoordinator

```python
from agentic_sdlc.intelligence import TeamCoordinator

# Tạo TeamCoordinator instance
coordinator = TeamCoordinator(
    storage_path="./collaboration_data",
    max_sessions=100,
    message_retention_hours=24
)
```text

### Tạo Collaboration Session

```python
from agentic_sdlc.intelligence import TeamCoordinator
from agentic_sdlc.orchestration import create_agent

coordinator = TeamCoordinator(storage_path="./collaboration_data")

# Tạo agents
developer = create_agent(name="developer", role="DEV", model_name="gpt-4")
reviewer = create_agent(name="reviewer", role="REVIEWER", model_name="gpt-4")
tester = create_agent(name="tester", role="TESTER", model_name="gpt-4")

# Tạo collaboration session
session = coordinator.create_session(
    session_name="feature_development",
    description="Develop and review user authentication feature",
    agents=[developer, reviewer, tester],
    metadata={
        "project": "user_management",
        "sprint": "sprint_5"
    }
)

print(f"✓ Session created: {session.id}")
print(f"  Participants: {', '.join([a.name for a in session.agents])}")
```text

### Đăng Ký Agents Vào Session

```python
from agentic_sdlc.intelligence import TeamCoordinator
from agentic_sdlc.orchestration import create_agent

coordinator = TeamCoordinator(storage_path="./collaboration_data")

# Tạo session
session_id = coordinator.create_session(
    session_name="code_review",
    description="Review pull request #123"
)

# Đăng ký agents
developer = create_agent(name="developer", role="DEV", model_name="gpt-4")
reviewer = create_agent(name="reviewer", role="REVIEWER", model_name="gpt-4")

coordinator.register_agent(session_id, developer, role="contributor")
coordinator.register_agent(session_id, reviewer, role="reviewer")

print(f"✓ Agents registered to session {session_id}")
```text

### Gửi Messages Giữa Agents

```python
from agentic_sdlc.intelligence import TeamCoordinator

coordinator = TeamCoordinator(storage_path="./collaboration_data")

# Developer gửi message cho reviewer
coordinator.send_message(
    session_id=session_id,
    from_agent="developer",
    to_agent="reviewer",
    message_type="request_review",
    content={
        "pull_request": "#123",
        "files_changed": ["auth.py", "user.py"],
        "description": "Implemented OAuth2 authentication"
    }
)

print("✓ Review request sent")

# Reviewer nhận và xử lý message
messages = coordinator.get_messages(
    session_id=session_id,
    agent_name="reviewer",
    unread_only=True
)

for msg in messages:
    print(f"\nMessage from {msg.from_agent}:")
    print(f"  Type: {msg.message_type}")
    print(f"  Content: {msg.content}")
    
    # Reviewer phản hồi
    coordinator.send_message(
        session_id=session_id,
        from_agent="reviewer",
        to_agent="developer",
        message_type="review_feedback",
        content={
            "status": "approved",
            "comments": ["Good implementation", "Consider adding more tests"],
            "rating": 8.5
        },
        in_reply_to=msg.id
    )

print("\n✓ Review feedback sent")
```text

### Điều Phối Multi-Agent Workflow

```python
from agentic_sdlc.intelligence import TeamCoordinator
from agentic_sdlc.orchestration import create_agent, WorkflowBuilder

coordinator = TeamCoordinator(storage_path="./collaboration_data")

# Tạo agents
pm = create_agent(name="pm", role="PM", model_name="gpt-4")
developer = create_agent(name="developer", role="DEV", model_name="gpt-4")
reviewer = create_agent(name="reviewer", role="REVIEWER", model_name="gpt-4")
tester = create_agent(name="tester", role="TESTER", model_name="gpt-4")

# Tạo session
session_id = coordinator.create_session(
    session_name="feature_pipeline",
    agents=[pm, developer, reviewer, tester]
)

# Điều phối workflow
workflow_result = coordinator.coordinate_workflow(
    session_id=session_id,
    workflow_definition={
        "steps": [
            {
                "name": "requirements_analysis",
                "agent": "pm",
                "action": "analyze_requirements",
                "output_to": ["developer"]
            },
            {
                "name": "implementation",
                "agent": "developer",
                "action": "implement_feature",
                "depends_on": ["requirements_analysis"],
                "output_to": ["reviewer"]
            },
            {
                "name": "code_review",
                "agent": "reviewer",
                "action": "review_code",
                "depends_on": ["implementation"],
                "output_to": ["developer", "tester"]
            },
            {
                "name": "testing",
                "agent": "tester",
                "action": "run_tests",
                "depends_on": ["code_review"],
                "output_to": ["pm"]
            }
        ]
    }
)

print(f"✓ Workflow completed")
print(f"  Steps executed: {len(workflow_result.steps)}")
print(f"  Total time: {workflow_result.total_time}s")
```text

## Ví Dụ Thực Tế

### Ví Dụ 1: Collaborative Code Review

```python
from agentic_sdlc.intelligence import TeamCoordinator
from agentic_sdlc.orchestration import create_agent

class CollaborativeCodeReview:
    """Multi-agent code review system."""
    
    def __init__(self):
        self.coordinator = TeamCoordinator(storage_path="./collaboration_data")
        
        # Tạo review team
        self.agents = {
            "author": create_agent(name="author", role="DEV", model_name="gpt-4"),
            "reviewer1": create_agent(name="reviewer1", role="REVIEWER", model_name="gpt-4"),
            "reviewer2": create_agent(name="reviewer2", role="REVIEWER", model_name="gpt-4"),
            "security": create_agent(name="security", role="SECURITY", model_name="gpt-4")
        }
    
    def review_pull_request(self, pr_number: str, files: list):
        """Thực hiện collaborative review."""
        
        # Tạo session
        session_id = self.coordinator.create_session(
            session_name=f"pr_review_{pr_number}",
            description=f"Review pull request #{pr_number}",
            agents=list(self.agents.values())
        )
        
        print(f"Starting collaborative review for PR #{pr_number}")
        print(f"Files to review: {', '.join(files)}")
        
        # Bước 1: Author giới thiệu changes
        self.coordinator.send_message(
            session_id=session_id,
            from_agent="author",
            to_agent="all",
            message_type="pr_introduction",
            content={
                "pr_number": pr_number,
                "files": files,
                "description": "Implemented OAuth2 authentication",
                "changes_summary": "Added OAuth providers, JWT handling, session management"
            }
        )
        
        # Bước 2: Parallel review từ các reviewers
        reviews = []
        
        for reviewer_name in ["reviewer1", "reviewer2", "security"]:
            review = self._conduct_review(
                session_id, reviewer_name, files
            )
            reviews.append(review)
            
            # Gửi review feedback
            self.coordinator.send_message(
                session_id=session_id,
                from_agent=reviewer_name,
                to_agent="author",
                message_type="review_feedback",
                content=review
            )
        
        # Bước 3: Consolidate feedback
        consolidated = self._consolidate_reviews(reviews)
        
        # Bước 4: Author responds
        response = self._author_response(session_id, consolidated)
        
        # Bước 5: Final approval
        final_decision = self._make_final_decision(reviews, response)
        
        print(f"\n{'='*60}")
        print(f"Review Result: {final_decision['status']}")
        print(f"Overall Rating: {final_decision['rating']}/10")
        print(f"{'='*60}")
        
        return final_decision
    
    def _conduct_review(self, session_id, reviewer_name, files):
        """Reviewer thực hiện review."""
        
        agent = self.agents[reviewer_name]
        
        # Simulate review process
        review = {
            "reviewer": reviewer_name,
            "files_reviewed": files,
            "issues": [],
            "suggestions": [],
            "rating": 0
        }
        
        # Agent performs review
        result = agent.execute({
            "type": "code_review",
            "files": files
        })
        
        if result.success:
            review["issues"] = result.output.get("issues", [])
            review["suggestions"] = result.output.get("suggestions", [])
            review["rating"] = result.output.get("rating", 7)
        
        print(f"\n✓ {reviewer_name} completed review:")
        print(f"  Issues found: {len(review['issues'])}")
        print(f"  Rating: {review['rating']}/10")
        
        return review
    
    def _consolidate_reviews(self, reviews):
        """Consolidate feedback từ multiple reviewers."""
        
        all_issues = []
        all_suggestions = []
        avg_rating = 0
        
        for review in reviews:
            all_issues.extend(review["issues"])
            all_suggestions.extend(review["suggestions"])
            avg_rating += review["rating"]
        
        avg_rating /= len(reviews)
        
        # Remove duplicates
        unique_issues = list(set(all_issues))
        unique_suggestions = list(set(all_suggestions))
        
        return {
            "issues": unique_issues,
            "suggestions": unique_suggestions,
            "average_rating": avg_rating
        }
    
    def _author_response(self, session_id, consolidated):
        """Author responds to feedback."""
        
        self.coordinator.send_message(
            session_id=session_id,
            from_agent="author",
            to_agent="all",
            message_type="response_to_feedback",
            content={
                "issues_addressed": len(consolidated["issues"]),
                "changes_made": "Fixed all critical issues, implemented suggestions"
            }
        )
        
        return {"status": "addressed"}
    
    def _make_final_decision(self, reviews, response):
        """Make final approval decision."""
        
        avg_rating = sum(r["rating"] for r in reviews) / len(reviews)
        critical_issues = sum(
            1 for r in reviews 
            for i in r["issues"] 
            if "critical" in str(i).lower()
        )
        
        if avg_rating >= 7 and critical_issues == 0:
            status = "approved"
        elif avg_rating >= 5:
            status = "approved_with_comments"
        else:
            status = "changes_requested"
        
        return {
            "status": status,
            "rating": avg_rating,
            "critical_issues": critical_issues
        }

# Sử dụng
review_system = CollaborativeCodeReview()
result = review_system.review_pull_request(
    pr_number="123",
    files=["auth.py", "user.py", "session.py"]
)
```text

### Ví Dụ 2: Team-Based Feature Development

```python
from agentic_sdlc.intelligence import TeamCoordinator
from agentic_sdlc.orchestration import create_agent

class TeamBasedDevelopment:
    """Multi-agent team development system."""
    
    def __init__(self):
        self.coordinator = TeamCoordinator(storage_path="./collaboration_data")
        
        # Tạo development team
        self.team = {
            "pm": create_agent(name="pm", role="PM", model_name="gpt-4"),
            "architect": create_agent(name="architect", role="SA", model_name="gpt-4"),
            "dev1": create_agent(name="dev1", role="DEV", model_name="gpt-4"),
            "dev2": create_agent(name="dev2", role="DEV", model_name="gpt-4"),
            "tester": create_agent(name="tester", role="TESTER", model_name="gpt-4")
        }
    
    def develop_feature(self, feature_description: str):
        """Develop feature với team collaboration."""
        
        # Tạo session
        session_id = self.coordinator.create_session(
            session_name="feature_development",
            description=feature_description,
            agents=list(self.team.values())
        )
        
        print(f"{'='*60}")
        print(f"Feature Development: {feature_description}")
        print(f"{'='*60}\n")
        
        # Phase 1: Requirements & Design
        print("Phase 1: Requirements & Design")
        requirements = self._gather_requirements(session_id, feature_description)
        design = self._create_design(session_id, requirements)
        
        # Phase 2: Implementation
        print("\nPhase 2: Implementation")
        implementation = self._implement_feature(session_id, design)
        
        # Phase 3: Testing
        print("\nPhase 3: Testing")
        test_results = self._test_feature(session_id, implementation)
        
        # Phase 4: Review & Deploy
        print("\nPhase 4: Review & Deploy")
        final_result = self._review_and_deploy(session_id, test_results)
        
        print(f"\n{'='*60}")
        print(f"Feature Development Complete!")
        print(f"Status: {final_result['status']}")
        print(f"{'='*60}")
        
        return final_result
    
    def _gather_requirements(self, session_id, feature_description):
        """PM gathers requirements."""
        
        pm = self.team["pm"]
        
        # PM analyzes requirements
        result = pm.execute({
            "type": "requirements_analysis",
            "description": feature_description
        })
        
        requirements = result.output if result.success else {}
        
        # PM shares với team
        self.coordinator.send_message(
            session_id=session_id,
            from_agent="pm",
            to_agent="all",
            message_type="requirements_ready",
            content=requirements
        )
        
        print(f"  ✓ Requirements gathered by PM")
        return requirements
    
    def _create_design(self, session_id, requirements):
        """Architect creates design."""
        
        architect = self.team["architect"]
        
        # Architect creates design
        result = architect.execute({
            "type": "system_design",
            "requirements": requirements
        })
        
        design = result.output if result.success else {}
        
        # Share design với developers
        self.coordinator.send_message(
            session_id=session_id,
            from_agent="architect",
            to_agent="all",
            message_type="design_ready",
            content=design
        )
        
        print(f"  ✓ Design created by Architect")
        return design
    
    def _implement_feature(self, session_id, design):
        """Developers implement feature."""
        
        # Split work giữa developers
        tasks = self._split_implementation_tasks(design)
        
        implementations = []
        
        for i, task in enumerate(tasks):
            dev_name = f"dev{(i % 2) + 1}"
            dev = self.team[dev_name]
            
            # Developer implements
            result = dev.execute({
                "type": "implementation",
                "task": task
            })
            
            if result.success:
                implementations.append(result.output)
                
                # Share progress
                self.coordinator.send_message(
                    session_id=session_id,
                    from_agent=dev_name,
                    to_agent="all",
                    message_type="implementation_progress",
                    content={
                        "task": task["name"],
                        "status": "completed"
                    }
                )
                
                print(f"  ✓ {dev_name} completed: {task['name']}")
        
        return implementations
    
    def _split_implementation_tasks(self, design):
        """Split design thành implementation tasks."""
        
        # Simplified task splitting
        return [
            {"name": "backend_api", "description": "Implement backend API"},
            {"name": "frontend_ui", "description": "Implement frontend UI"}
        ]
    
    def _test_feature(self, session_id, implementation):
        """Tester tests feature."""
        
        tester = self.team["tester"]
        
        # Run tests
        result = tester.execute({
            "type": "testing",
            "implementation": implementation
        })
        
        test_results = result.output if result.success else {}
        
        # Share results
        self.coordinator.send_message(
            session_id=session_id,
            from_agent="tester",
            to_agent="all",
            message_type="test_results",
            content=test_results
        )
        
        print(f"  ✓ Testing completed")
        print(f"    Tests passed: {test_results.get('passed', 0)}")
        print(f"    Tests failed: {test_results.get('failed', 0)}")
        
        return test_results
    
    def _review_and_deploy(self, session_id, test_results):
        """PM reviews và approves deployment."""
        
        pm = self.team["pm"]
        
        # PM reviews results
        if test_results.get("failed", 0) == 0:
            decision = {
                "status": "approved",
                "ready_for_deployment": True
            }
        else:
            decision = {
                "status": "needs_fixes",
                "ready_for_deployment": False
            }
        
        # Announce decision
        self.coordinator.send_message(
            session_id=session_id,
            from_agent="pm",
            to_agent="all",
            message_type="deployment_decision",
            content=decision
        )
        
        print(f"  ✓ PM decision: {decision['status']}")
        
        return decision

# Sử dụng
team_dev = TeamBasedDevelopment()
result = team_dev.develop_feature(
    "Implement user authentication with OAuth2 support"
)
```text

### Ví Dụ 3: Conflict Resolution

```python
from agentic_sdlc.intelligence import TeamCoordinator

class ConflictResolver:
    """System để resolve conflicts trong collaboration."""
    
    def __init__(self):
        self.coordinator = TeamCoordinator(storage_path="./collaboration_data")
    
    def resolve_merge_conflict(self, session_id, conflict_info):
        """Resolve merge conflict với agent collaboration."""
        
        print(f"Resolving merge conflict...")
        print(f"Files in conflict: {conflict_info['files']}")
        
        # Lấy opinions từ các agents
        opinions = []
        
        for agent_name in conflict_info["involved_agents"]:
            opinion = self._get_agent_opinion(
                session_id, agent_name, conflict_info
            )
            opinions.append(opinion)
        
        # Analyze conflicts
        resolution = self._analyze_and_resolve(opinions, conflict_info)
        
        # Broadcast resolution
        self.coordinator.send_message(
            session_id=session_id,
            from_agent="system",
            to_agent="all",
            message_type="conflict_resolved",
            content=resolution
        )
        
        print(f"\n✓ Conflict resolved: {resolution['strategy']}")
        
        return resolution
    
    def _get_agent_opinion(self, session_id, agent_name, conflict_info):
        """Get agent's opinion về conflict."""
        
        # Request opinion
        self.coordinator.send_message(
            session_id=session_id,
            from_agent="system",
            to_agent=agent_name,
            message_type="conflict_opinion_request",
            content=conflict_info
        )
        
        # Wait for response
        messages = self.coordinator.get_messages(
            session_id=session_id,
            agent_name="system",
            message_type="conflict_opinion_response"
        )
        
        if messages:
            return messages[-1].content
        
        return {"opinion": "no_preference"}
    
    def _analyze_and_resolve(self, opinions, conflict_info):
        """Analyze opinions và determine resolution."""
        
        # Count votes
        votes = {}
        for opinion in opinions:
            strategy = opinion.get("preferred_strategy", "manual")
            votes[strategy] = votes.get(strategy, 0) + 1
        
        # Choose strategy với most votes
        winning_strategy = max(votes.items(), key=lambda x: x[1])[0]
        
        return {
            "strategy": winning_strategy,
            "votes": votes,
            "confidence": votes[winning_strategy] / len(opinions)
        }

# Sử dụng
resolver = ConflictResolver()

conflict = {
    "files": ["auth.py"],
    "involved_agents": ["dev1", "dev2"],
    "conflict_type": "merge_conflict"
}

resolution = resolver.resolve_merge_conflict(session_id, conflict)
```text

## Best Practices

### 1. Sử Dụng Clear Message Types

```python
# ✓ Tốt: Message types rõ ràng
MESSAGE_TYPES = {
    "request_review": "Request code review",
    "review_feedback": "Provide review feedback",
    "implementation_complete": "Implementation completed",
    "test_results": "Test execution results"
}

coordinator.send_message(
    session_id=session_id,
    from_agent="developer",
    to_agent="reviewer",
    message_type="request_review",
    content={"pr": "#123"}
)
```text

### 2. Quản Lý Session Lifecycle

```python
# Tạo session
session_id = coordinator.create_session(...)

try:
    # Thực hiện collaboration
    result = coordinator.coordinate_workflow(...)
finally:
    # Cleanup session
    coordinator.close_session(session_id)
```text

### 3. Handle Message Failures

```python
try:
    coordinator.send_message(
        session_id=session_id,
        from_agent="dev",
        to_agent="reviewer",
        message_type="request",
        content=data
    )
except MessageDeliveryError as e:
    print(f"Failed to deliver message: {e}")
    # Retry hoặc fallback
```text

### 4. Monitor Collaboration Health

```python
from agentic_sdlc.intelligence import Monitor

monitor = Monitor(storage_path="./monitoring_data")

# Monitor collaboration metrics
monitor.record_metric(
    metric_name="collaboration_session",
    value=session_duration,
    tags={
        "session_id": session_id,
        "agents_count": len(agents),
        "messages_exchanged": message_count
    }
)
```text

### 5. Use Timeouts

```python
# Set timeout cho message responses
response = coordinator.wait_for_response(
    session_id=session_id,
    message_id=msg_id,
    timeout=30  # seconds
)

if response is None:
    print("Timeout waiting for response")
```text

## Troubleshooting

### Messages Không Được Delivered

**Nguyên nhân**: Agent không active hoặc session closed

**Giải pháp**:
```python
# Kiểm tra agent status
status = coordinator.get_agent_status(session_id, agent_name)

if status != "active":
    print(f"Agent {agent_name} is {status}")
    # Reactivate hoặc choose alternative agent
```text

### Session Conflicts

**Nguyên nhân**: Multiple sessions với same agents

**Giải pháp**:
```python
# Check agent availability
available = coordinator.is_agent_available(agent_name)

if not available:
    print(f"Agent {agent_name} is busy in another session")
    # Wait hoặc use different agent
```text

### Memory Issues Với Large Sessions

**Nguyên nhân**: Too many messages stored

**Giải pháp**:
```python
# Cleanup old messages
coordinator.cleanup_messages(
    session_id=session_id,
    older_than_hours=24
)

# Hoặc limit message retention
coordinator = TeamCoordinator(
    storage_path="./collaboration_data",
    message_retention_hours=12
)
```

## Tài Liệu Liên Quan

- [Learning](learning.md) - Học từ execution results
- [Monitoring](monitoring.md) - Theo dõi metrics và health
- [Reasoning](reasoning.md) - Phân tích và ra quyết định
- [Workflows](../workflows/overview.md) - Xây dựng workflows
- [API Reference - TeamCoordinator](../../api-reference/intelligence/collaborator.md)
