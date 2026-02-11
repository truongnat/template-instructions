"""
Ví Dụ 2: Tạo Agent Đơn Giản (Simple Agent Creation)

Ví dụ này minh họa cách tạo và sử dụng một agent đơn giản.

Setup Instructions:
1. Cài đặt: pip install agentic-sdlc
2. Cấu hình API key trong .env
3. Chạy: python 02-simple-agent.py

Dependencies:
- agentic-sdlc>=3.0.0

Expected Output:
- Agent được tạo và đăng ký thành công
- Agent thực thi task và trả về kết quả
"""

import os
from dotenv import load_dotenv

load_dotenv()


def create_simple_agent():
    """Tạo một agent đơn giản."""
    from agentic_sdlc.orchestration.agent import Agent, AgentConfig
    from agentic_sdlc.core.config import ModelConfig
    
    # Cấu hình model
    model_config = ModelConfig(
        provider="openai",
        model_name="gpt-4",
        api_key=os.getenv("OPENAI_API_KEY"),
        temperature=0.7
    )
    
    # Cấu hình agent
    agent_config = AgentConfig(
        name="simple-agent",
        role="developer",
        description="Agent đơn giản để xử lý các task cơ bản",
        model_config=model_config,
        system_prompt="Bạn là một developer agent hữu ích.",
        max_iterations=5
    )
    
    # Tạo agent
    agent = Agent(config=agent_config)
    
    print("✓ Agent đã được tạo")
    print(f"  Name: {agent.config.name}")
    print(f"  Role: {agent.config.role}")
    print(f"  Model: {agent.config.model_config.model_name}")
    
    return agent


def execute_simple_task(agent):
    """Thực thi một task đơn giản với agent."""
    from agentic_sdlc.orchestration.agent import Task
    
    # Tạo task
    task = Task(
        id="task-1",
        description="Viết một hàm Python để tính giai thừa của một số",
        context={"language": "python", "style": "clean"}
    )
    
    print("\n✓ Đang thực thi task...")
    print(f"  Task ID: {task.id}")
    print(f"  Description: {task.description}")
    
    # Thực thi task
    result = agent.execute(task)
    
    print("\n✓ Task hoàn thành!")
    print(f"  Status: {result.status}")
    print(f"  Output:\n{result.output}")
    
    return result


def create_specialized_agent():
    """Tạo agent chuyên biệt với tools."""
    from agentic_sdlc.orchestration.agent import Agent, AgentConfig, Tool
    from agentic_sdlc.core.config import ModelConfig
    
    # Định nghĩa tools
    def code_analyzer(code: str) -> dict:
        """Phân tích code Python."""
        import ast
        try:
            tree = ast.parse(code)
            return {
                "valid": True,
                "functions": len([n for n in ast.walk(tree) if isinstance(n, ast.FunctionDef)]),
                "classes": len([n for n in ast.walk(tree) if isinstance(n, ast.ClassDef)])
            }
        except SyntaxError as e:
            return {"valid": False, "error": str(e)}
    
    tools = [
        Tool(
            name="code_analyzer",
            description="Phân tích code Python",
            function=code_analyzer
        )
    ]
    
    # Cấu hình agent với tools
    model_config = ModelConfig(
        provider="openai",
        model_name="gpt-4",
        api_key=os.getenv("OPENAI_API_KEY")
    )
    
    agent_config = AgentConfig(
        name="code-analyzer-agent",
        role="tester",
        description="Agent phân tích code",
        model_config=model_config,
        tools=tools,
        system_prompt="Bạn là một tester agent chuyên phân tích code."
    )
    
    agent = Agent(config=agent_config)
    
    print("\n✓ Specialized agent đã được tạo")
    print(f"  Name: {agent.config.name}")
    print(f"  Tools: {[t.name for t in agent.config.tools]}")
    
    return agent


def register_agent_to_registry():
    """Đăng ký agent vào registry."""
    from agentic_sdlc.orchestration.agent import Agent, AgentConfig, AgentRegistry
    from agentic_sdlc.core.config import ModelConfig
    
    # Tạo registry
    registry = AgentRegistry()
    
    # Tạo và đăng ký nhiều agents
    for role in ["developer", "tester", "reviewer"]:
        model_config = ModelConfig(
            provider="openai",
            model_name="gpt-4",
            api_key=os.getenv("OPENAI_API_KEY")
        )
        
        agent_config = AgentConfig(
            name=f"{role}-agent",
            role=role,
            description=f"Agent với vai trò {role}",
            model_config=model_config
        )
        
        agent = Agent(config=agent_config)
        registry.register(agent)
    
    print("\n✓ Agents đã được đăng ký vào registry")
    print(f"  Total agents: {len(registry.list_agents())}")
    
    # Lấy agent từ registry
    developer_agent = registry.get("developer-agent")
    print(f"  Retrieved: {developer_agent.config.name}")
    
    return registry


if __name__ == "__main__":
    print("=" * 60)
    print("VÍ DỤ: TẠO VÀ SỬ DỤNG AGENT ĐƠN GIẢN")
    print("=" * 60)
    
    # Tạo agent đơn giản
    agent = create_simple_agent()
    
    # Thực thi task
    execute_simple_task(agent)
    
    # Tạo specialized agent
    create_specialized_agent()
    
    # Đăng ký agents
    register_agent_to_registry()
    
    print("\n" + "=" * 60)
    print("✓ Tất cả ví dụ agent đã hoàn thành!")
    print("=" * 60)
