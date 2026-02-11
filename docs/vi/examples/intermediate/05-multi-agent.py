"""
Ví Dụ 5: Hệ Thống Multi-Agent (Multi-Agent System)

Ví dụ này minh họa cách xây dựng hệ thống với nhiều agents cộng tác.

Setup Instructions:
1. Cài đặt: pip install agentic-sdlc
2. Cấu hình API keys trong .env
3. Chạy: python 05-multi-agent.py

Dependencies:
- agentic-sdlc>=3.0.0

Expected Output:
- Nhiều agents được tạo với vai trò khác nhau
- Agents cộng tác để hoàn thành task phức tạp
- Kết quả từ mỗi agent
"""

import os
from dotenv import load_dotenv

load_dotenv()


def create_development_team():
    """Tạo team gồm nhiều agents với vai trò khác nhau."""
    from agentic_sdlc.orchestration.agent import Agent, AgentConfig, AgentRegistry
    from agentic_sdlc.core.config import ModelConfig
    
    registry = AgentRegistry()
    
    # Định nghĩa các vai trò trong team
    roles = {
        "product_manager": {
            "description": "Quản lý product và requirements",
            "system_prompt": "Bạn là Product Manager, phân tích requirements và tạo user stories."
        },
        "architect": {
            "description": "Thiết kế kiến trúc hệ thống",
            "system_prompt": "Bạn là Software Architect, thiết kế kiến trúc và technical decisions."
        },
        "developer": {
            "description": "Implement code",
            "system_prompt": "Bạn là Developer, viết code clean và maintainable."
        },
        "tester": {
            "description": "Test và quality assurance",
            "system_prompt": "Bạn là QA Tester, viết tests và verify quality."
        },
        "reviewer": {
            "description": "Code review",
            "system_prompt": "Bạn là Code Reviewer, review code và đưa ra feedback."
        }
    }
    
    # Tạo agents cho mỗi vai trò
    for role, config in roles.items():
        model_config = ModelConfig(
            provider="openai",
            model_name="gpt-4",
            api_key=os.getenv("OPENAI_API_KEY")
        )
        
        agent_config = AgentConfig(
            name=f"{role}-agent",
            role=role,
            description=config["description"],
            model_config=model_config,
            system_prompt=config["system_prompt"]
        )
        
        agent = Agent(config=agent_config)
        registry.register(agent)
    
    print("✓ Development team đã được tạo")
    print(f"  Team size: {len(registry.list_agents())} agents")
    for agent_name in registry.list_agents():
        agent = registry.get(agent_name)
        print(f"    - {agent.config.role}: {agent.config.description}")
    
    return registry


def collaborative_workflow(registry):
    """Workflow với nhiều agents cộng tác."""
    from agentic_sdlc.orchestration.workflow import WorkflowBuilder, WorkflowStep
    
    builder = WorkflowBuilder(name="collaborative-development")
    
    # Step 1: PM phân tích requirements
    builder.add_step(
        WorkflowStep(
            name="analyze_requirements",
            action="analyze",
            description="PM phân tích requirements",
            parameters={
                "input": "Tạo REST API cho user management",
                "agent": "product_manager-agent"
            }
        )
    )
    
    # Step 2: Architect thiết kế
    builder.add_step(
        WorkflowStep(
            name="design_architecture",
            action="design",
            description="Architect thiết kế kiến trúc",
            parameters={
                "requirements": "{{analyze_requirements.output}}",
                "agent": "architect-agent"
            },
            dependencies=["analyze_requirements"]
        )
    )
    
    # Step 3: Developer implement
    builder.add_step(
        WorkflowStep(
            name="implement_code",
            action="implement",
            description="Developer viết code",
            parameters={
                "design": "{{design_architecture.output}}",
                "agent": "developer-agent"
            },
            dependencies=["design_architecture"]
        )
    )
    
    # Step 4: Tester viết tests (parallel với implement)
    builder.add_step(
        WorkflowStep(
            name="write_tests",
            action="test",
            description="Tester viết test cases",
            parameters={
                "design": "{{design_architecture.output}}",
                "agent": "tester-agent"
            },
            dependencies=["design_architecture"]
        )
    )
    
    # Step 5: Reviewer review code
    builder.add_step(
        WorkflowStep(
            name="review_code",
            action="review",
            description="Reviewer review code",
            parameters={
                "code": "{{implement_code.output}}",
                "tests": "{{write_tests.output}}",
                "agent": "reviewer-agent"
            },
            dependencies=["implement_code", "write_tests"]
        )
    )
    
    workflow = builder.build()
    
    print("\n✓ Collaborative workflow đã được tạo")
    print(f"  Workflow: {workflow.name}")
    print(f"  Steps: {len(workflow.steps)}")
    print("  Execution flow:")
    print("    1. PM analyzes requirements")
    print("    2. Architect designs solution")
    print("    3. Developer implements + Tester writes tests (parallel)")
    print("    4. Reviewer reviews everything")
    
    return workflow


def agent_communication():
    """Agents giao tiếp với nhau."""
    from agentic_sdlc.intelligence.collaborator import TeamCoordinator, Message
    from agentic_sdlc.orchestration.agent import Agent, AgentConfig
    from agentic_sdlc.core.config import ModelConfig
    
    # Tạo coordinator
    coordinator = TeamCoordinator()
    
    # Tạo session
    session_id = coordinator.create_session(
        name="code-review-session",
        participants=["developer-agent", "reviewer-agent"]
    )
    
    print("\n✓ Agent communication session")
    print(f"  Session ID: {session_id}")
    
    # Developer gửi code để review
    coordinator.send_message(
        session_id=session_id,
        message=Message(
            from_agent="developer-agent",
            to_agent="reviewer-agent",
            content="Please review this code: def add(a, b): return a + b",
            message_type="code_review_request"
        )
    )
    
    print("  ✓ Developer sent code review request")
    
    # Reviewer gửi feedback
    coordinator.send_message(
        session_id=session_id,
        message=Message(
            from_agent="reviewer-agent",
            to_agent="developer-agent",
            content="Code looks good! Consider adding type hints.",
            message_type="code_review_feedback"
        )
    )
    
    print("  ✓ Reviewer sent feedback")
    
    # Lấy message history
    history = coordinator.get_session_history(session_id)
    print(f"  ✓ Total messages: {len(history)}")
    
    return coordinator


def load_balancing_agents():
    """Load balancing giữa nhiều agents."""
    from agentic_sdlc.orchestration.agent import Agent, AgentConfig, AgentRegistry
    from agentic_sdlc.core.config import ModelConfig
    import random
    
    registry = AgentRegistry()
    
    # Tạo pool of worker agents
    num_workers = 5
    for i in range(num_workers):
        model_config = ModelConfig(
            provider="openai",
            model_name="gpt-4",
            api_key=os.getenv("OPENAI_API_KEY")
        )
        
        agent_config = AgentConfig(
            name=f"worker-{i}",
            role="worker",
            description=f"Worker agent {i}",
            model_config=model_config
        )
        
        agent = Agent(config=agent_config)
        registry.register(agent)
    
    print("\n✓ Worker pool đã được tạo")
    print(f"  Workers: {num_workers}")
    
    # Simulate load balancing
    tasks = [f"task-{i}" for i in range(15)]
    
    print("\n  Distributing tasks:")
    for task in tasks:
        # Round-robin hoặc random selection
        worker_id = random.randint(0, num_workers - 1)
        worker = registry.get(f"worker-{worker_id}")
        print(f"    {task} -> {worker.config.name}")
    
    return registry


if __name__ == "__main__":
    print("=" * 60)
    print("VÍ DỤ: HỆ THỐNG MULTI-AGENT")
    print("=" * 60)
    
    # Tạo development team
    registry = create_development_team()
    
    # Tạo collaborative workflow
    collaborative_workflow(registry)
    
    # Agent communication
    agent_communication()
    
    # Load balancing
    load_balancing_agents()
    
    print("\n" + "=" * 60)
    print("✓ Tất cả ví dụ multi-agent đã hoàn thành!")
    print("=" * 60)
