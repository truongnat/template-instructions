#!/usr/bin/env python3
"""
AutoGen Runner - Main Entry Point

Orchestrates multi-agent conversations for complex tasks.
Usage: python tools/autogen/runner.py --task "..." --team "dev,tester"
"""

import argparse
import asyncio
import sys
import io
from pathlib import Path

# Fix Windows console encoding
if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

# Add project root to path for imports
PROJECT_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))


async def run_single_agent(task: str, role: str, model: str, max_turns: int):
    """Run a single agent to complete a task."""
    from autogen_agentchat.agents import AssistantAgent
    from agentic_sdlc.infrastructure.engine.autogen.config import get_model_client
    from agentic_sdlc.infrastructure.engine.autogen.agents import (
        create_developer_agent,
        create_tester_agent,
        create_orchestrator_agent,
    )
    from agentic_sdlc.infrastructure.engine.autogen.tools_registry import get_tools_for_role
    
    print(f"\n[AGENT] Initializing {role} agent with {model}...")
    
    model_client = get_model_client(model)
    tools = get_tools_for_role(role)
    
    # Get system message based on role
    role_lower = role.lower().strip()
    if role_lower in ("dev", "developer"):
        system_message = """You are a skilled Developer (@DEV) in an Agentic SDLC team.
Your responsibilities: Write clean, modular, well-documented code.
When given a task, analyze requirements carefully and provide a clear response."""
        name = "developer"
    elif role_lower in ("tester", "qa"):
        system_message = """You are a Quality Assurance Tester (@TESTER) in an Agentic SDLC team.
Your responsibilities: Review code for correctness and edge cases.
When reviewing, identify potential bugs and issues."""
        name = "tester"
    else:
        system_message = """You are an Orchestrator agent coordinating a development team.
Your role is to break down complex tasks and coordinate work."""
        name = "orchestrator"
    
    # Create agent with tools
    agent = AssistantAgent(
        name=name,
        model_client=model_client,
        system_message=system_message,
        tools=tools,
    )
    
    print(f"[TASK] {task}\n")
    print("-" * 60)
    
    result = await agent.run(task=task)
    await model_client.close()
    
    return result


async def run_multi_agent(task: str, team: list[str], model: str, max_turns: int):
    """Run a multi-agent team to complete a task."""
    from autogen_agentchat.agents import AssistantAgent
    from autogen_agentchat.teams import RoundRobinGroupChat
    from autogen_agentchat.conditions import MaxMessageTermination, TextMentionTermination
    from autogen_agentchat.ui import Console
    
    from agentic_sdlc.infrastructure.engine.autogen.config import get_model_client
    from agentic_sdlc.infrastructure.engine.autogen.agents import create_agent_by_role
    from agentic_sdlc.infrastructure.engine.autogen.tools_registry import get_tools_for_role
    
    print(f"\n[TEAM] Initializing team: {', '.join(team)} with {model}...")
    
    model_client = get_model_client(model)
    
    # Create agents for each team member
    agents = []
    for role in team:
        agent = create_agent_by_role(model_client, role)
        tools = get_tools_for_role(role)
        
        # Recreate with tools
        agent_with_tools = AssistantAgent(
            name=agent.name,
            model_client=model_client,
            system_message=agent._system_messages[0].content if agent._system_messages else "",
            tools=tools,
            description=agent.description,
        )
        agents.append(agent_with_tools)
    
    # Create termination conditions
    termination = MaxMessageTermination(max_turns) | TextMentionTermination("TASK_COMPLETE")
    
    # Create team
    team_chat = RoundRobinGroupChat(
        participants=agents,
        termination_condition=termination,
    )
    
    print(f"[TASK] {task}\n")
    print("-" * 60)
    
    # Run with console output
    result = await Console(team_chat.run_stream(task=task))
    
    await model_client.close()
    
    return result


async def main():
    parser = argparse.ArgumentParser(
        description="AutoGen Runner - Multi-agent task orchestration",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Single agent
  python runner.py --task "Write a factorial function" --team dev
  
  # Multi-agent team
  python runner.py --task "Write and test a sorting algorithm" --team dev,tester
  
  # With specific model
  python runner.py --task "Debug this code" --team dev --model gpt-4o
        """
    )
    
    parser.add_argument(
        "--task", "-t",
        required=True,
        help="Task description for the agent(s)"
    )
    
    parser.add_argument(
        "--team",
        default="dev",
        help="Comma-separated list of roles: dev, tester, orchestrator (default: dev)"
    )
    
    parser.add_argument(
        "--model", "-m",
        default="gemini-2.0-flash",
        help="Model to use: gemini-2.0-flash, gpt-4o, etc. (default: gemini-2.0-flash)"
    )
    
    parser.add_argument(
        "--max-turns",
        type=int,
        default=10,
        help="Maximum conversation turns (default: 10)"
    )
    
    args = parser.parse_args()
    
    # Parse team
    team = [r.strip() for r in args.team.split(",") if r.strip()]
    
    try:
        if len(team) == 1:
            result = await run_single_agent(args.task, team[0], args.model, args.max_turns)
        else:
            result = await run_multi_agent(args.task, team, args.model, args.max_turns)
        
        print("\n" + "=" * 60)
        print("[OK] Task completed!")
        print("=" * 60)
        
    except ValueError as e:
        print(f"\n[ERROR] Configuration Error: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"\n[ERROR] Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())

