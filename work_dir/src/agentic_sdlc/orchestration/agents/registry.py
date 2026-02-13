"""Agent registry for managing agent instances."""

from typing import Dict, Optional

from .agent import Agent


class AgentRegistry:
    """Registry for managing agent instances.
    
    Provides centralized management of agents including registration,
    retrieval, and lifecycle management.
    """
    
    def __init__(self) -> None:
        """Initialize the agent registry."""
        self._agents: Dict[str, Agent] = {}
    
    def register(self, agent: Agent) -> None:
        """Register an agent in the registry.
        
        Args:
            agent: The agent to register
            
        Raises:
            ValueError: If an agent with the same ID already exists
        """
        if agent.id in self._agents:
            raise ValueError(f"Agent with ID {agent.id} already registered")
        self._agents[agent.id] = agent
    
    def unregister(self, agent_id: str) -> None:
        """Unregister an agent from the registry.
        
        Args:
            agent_id: The ID of the agent to unregister
            
        Raises:
            KeyError: If the agent is not found
        """
        if agent_id not in self._agents:
            raise KeyError(f"Agent with ID {agent_id} not found")
        del self._agents[agent_id]
    
    def get(self, agent_id: str) -> Optional[Agent]:
        """Get an agent by ID.
        
        Args:
            agent_id: The ID of the agent to retrieve
            
        Returns:
            The agent if found, None otherwise
        """
        return self._agents.get(agent_id)
    
    def get_by_name(self, name: str) -> Optional[Agent]:
        """Get an agent by name.
        
        Args:
            name: The name of the agent to retrieve
            
        Returns:
            The first agent with the given name, or None if not found
        """
        for agent in self._agents.values():
            if agent.name == name:
                return agent
        return None
    
    def list_agents(self) -> list[Agent]:
        """List all registered agents.
        
        Returns:
            A list of all registered agents
        """
        return list(self._agents.values())
    
    def clear(self) -> None:
        """Clear all agents from the registry."""
        self._agents.clear()


# Global registry instance
_global_registry: Optional[AgentRegistry] = None


def get_agent_registry() -> AgentRegistry:
    """Get the global agent registry.
    
    Returns:
        The global AgentRegistry instance
    """
    global _global_registry
    if _global_registry is None:
        _global_registry = AgentRegistry()
    return _global_registry


def create_agent(
    name: str,
    role: str,
    model_name: str,
    system_prompt: Optional[str] = None,
    tools: Optional[list[str]] = None,
    max_iterations: int = 10,
) -> Agent:
    """Create and register a new agent.
    
    Args:
        name: The name of the agent
        role: The role of the agent
        model_name: The model to use for the agent
        system_prompt: Optional system prompt for the agent
        tools: Optional list of tools available to the agent
        max_iterations: Maximum iterations for agent execution
        
    Returns:
        The created Agent instance
    """
    agent = Agent(
        name=name,
        role=role,
        model_name=model_name,
        system_prompt=system_prompt,
        tools=tools or [],
        max_iterations=max_iterations,
    )
    get_agent_registry().register(agent)
    return agent
