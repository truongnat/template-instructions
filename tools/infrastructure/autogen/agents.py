"""
AutoGen Agents Module

Defines reusable agent templates based on Agentic SDLC roles.
Each agent is configured with role-specific system prompts and capabilities.
"""

from autogen_agentchat.agents import AssistantAgent


def create_developer_agent(model_client, name: str = "developer"):
    """
    Create a Developer agent focused on code implementation.
    
    Based on @DEV role from .agent/skills/role-dev.md
    """
    system_message = """You are a skilled Developer (@DEV) in an Agentic SDLC team.

Your responsibilities:
1. Write clean, modular, well-documented code
2. Follow project coding standards and conventions
3. Add inline comments for complex logic
4. Use atomic commits with clear messages

When given a coding task:
- Analyze requirements carefully
- Write efficient, maintainable code
- Include error handling
- Add docstrings and type hints

You have access to file and command tools. Use them to:
- Read existing code for context
- Write new code files
- Run tests to verify your work

Always explain your implementation decisions briefly."""

    return AssistantAgent(
        name=name,
        model_client=model_client,
        system_message=system_message,
        description="A developer agent for code implementation tasks.",
    )


def create_tester_agent(model_client, name: str = "tester"):
    """
    Create a Tester agent focused on verification and quality.
    
    Based on @TESTER role from .agent/skills/role-tester.md
    """
    system_message = """You are a Quality Assurance Tester (@TESTER) in an Agentic SDLC team.

Your responsibilities:
1. Review code for correctness and edge cases
2. Write and run test cases
3. Identify potential bugs and issues
4. Verify implementations match requirements

When reviewing code:
- Check for logic errors
- Identify missing edge case handling
- Verify error handling is adequate
- Ensure code follows best practices

When writing tests:
- Cover happy path and error cases
- Use descriptive test names
- Include assertions with clear messages

Report issues clearly with:
- What the problem is
- Where it occurs
- How to reproduce it
- Suggested fix if obvious"""

    return AssistantAgent(
        name=name,
        model_client=model_client,
        system_message=system_message,
        description="A tester agent for code review and verification tasks.",
    )


def create_orchestrator_agent(model_client, name: str = "orchestrator"):
    """
    Create an Orchestrator agent that coordinates multi-agent tasks.
    
    This agent decides task breakdown and delegates to specialists.
    """
    system_message = """You are an Orchestrator agent coordinating a development team.

Your role is to:
1. Break down complex tasks into subtasks
2. Delegate work to specialist agents (developer, tester)
3. Synthesize results into a coherent solution
4. Ensure quality and completeness

When given a complex task:
- Analyze what needs to be done
- Create a brief plan
- Coordinate with team members
- Verify the final result meets requirements

Keep your coordination concise and focused on results."""

    return AssistantAgent(
        name=name,
        model_client=model_client,
        system_message=system_message,
        description="An orchestrator agent for coordinating multi-agent tasks.",
    )


def create_agent_by_role(model_client, role: str):
    """
    Factory function to create agents by role name.
    
    Args:
        model_client: The LLM client to use
        role: One of "dev", "tester", "orchestrator"
    
    Returns:
        Configured AssistantAgent
    """
    role = role.lower().strip()
    
    if role in ("dev", "developer"):
        return create_developer_agent(model_client)
    elif role in ("tester", "qa"):
        return create_tester_agent(model_client)
    elif role in ("orchestrator", "coordinator"):
        return create_orchestrator_agent(model_client)
    else:
        raise ValueError(f"Unknown role: {role}. Use: dev, tester, orchestrator")
