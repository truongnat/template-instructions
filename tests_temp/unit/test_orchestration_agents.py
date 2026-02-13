"""Unit tests for orchestration agents module."""

import pytest

from agentic_sdlc.orchestration import Agent, AgentRegistry, create_agent, get_agent_registry


class TestAgent:
    """Tests for Agent class."""
    
    def test_agent_creation(self) -> None:
        """Test creating an agent with valid parameters."""
        agent = Agent(
            name="test_agent",
            role="researcher",
            model_name="gpt-4",
        )
        assert agent.name == "test_agent"
        assert agent.role == "researcher"
        assert agent.model_name == "gpt-4"
        assert agent.max_iterations == 10
        assert agent.tools == []
        assert agent.id is not None
    
    def test_agent_with_all_parameters(self) -> None:
        """Test creating an agent with all parameters."""
        agent = Agent(
            name="test_agent",
            role="researcher",
            model_name="gpt-4",
            system_prompt="You are a researcher",
            tools=["search", "analyze"],
            max_iterations=5,
        )
        assert agent.name == "test_agent"
        assert agent.system_prompt == "You are a researcher"
        assert agent.tools == ["search", "analyze"]
        assert agent.max_iterations == 5
    
    def test_agent_empty_name_raises_error(self) -> None:
        """Test that empty name raises ValueError."""
        with pytest.raises(ValueError, match="Agent name cannot be empty"):
            Agent(name="", role="researcher", model_name="gpt-4")
    
    def test_agent_empty_role_raises_error(self) -> None:
        """Test that empty role raises ValueError."""
        with pytest.raises(ValueError, match="Agent role cannot be empty"):
            Agent(name="test", role="", model_name="gpt-4")
    
    def test_agent_empty_model_name_raises_error(self) -> None:
        """Test that empty model_name raises ValueError."""
        with pytest.raises(ValueError, match="Agent model_name cannot be empty"):
            Agent(name="test", role="researcher", model_name="")
    
    def test_agent_invalid_max_iterations_raises_error(self) -> None:
        """Test that invalid max_iterations raises ValueError."""
        with pytest.raises(ValueError, match="Agent max_iterations must be at least 1"):
            Agent(
                name="test",
                role="researcher",
                model_name="gpt-4",
                max_iterations=0,
            )
    
    def test_agent_unique_ids(self) -> None:
        """Test that agents have unique IDs."""
        agent1 = Agent(name="agent1", role="researcher", model_name="gpt-4")
        agent2 = Agent(name="agent2", role="researcher", model_name="gpt-4")
        assert agent1.id != agent2.id


class TestAgentRegistry:
    """Tests for AgentRegistry class."""
    
    def test_registry_creation(self) -> None:
        """Test creating an agent registry."""
        registry = AgentRegistry()
        assert registry.list_agents() == []
    
    def test_register_agent(self) -> None:
        """Test registering an agent."""
        registry = AgentRegistry()
        agent = Agent(name="test", role="researcher", model_name="gpt-4")
        registry.register(agent)
        assert registry.get(agent.id) == agent
    
    def test_register_duplicate_agent_raises_error(self) -> None:
        """Test that registering duplicate agent raises error."""
        registry = AgentRegistry()
        agent = Agent(name="test", role="researcher", model_name="gpt-4")
        registry.register(agent)
        with pytest.raises(ValueError, match="already registered"):
            registry.register(agent)
    
    def test_unregister_agent(self) -> None:
        """Test unregistering an agent."""
        registry = AgentRegistry()
        agent = Agent(name="test", role="researcher", model_name="gpt-4")
        registry.register(agent)
        registry.unregister(agent.id)
        assert registry.get(agent.id) is None
    
    def test_unregister_nonexistent_agent_raises_error(self) -> None:
        """Test that unregistering nonexistent agent raises error."""
        registry = AgentRegistry()
        with pytest.raises(KeyError, match="not found"):
            registry.unregister("nonexistent")
    
    def test_get_agent_by_name(self) -> None:
        """Test getting agent by name."""
        registry = AgentRegistry()
        agent = Agent(name="test_agent", role="researcher", model_name="gpt-4")
        registry.register(agent)
        found = registry.get_by_name("test_agent")
        assert found == agent
    
    def test_get_nonexistent_agent_by_name(self) -> None:
        """Test getting nonexistent agent by name returns None."""
        registry = AgentRegistry()
        found = registry.get_by_name("nonexistent")
        assert found is None
    
    def test_list_agents(self) -> None:
        """Test listing all agents."""
        registry = AgentRegistry()
        agent1 = Agent(name="agent1", role="researcher", model_name="gpt-4")
        agent2 = Agent(name="agent2", role="analyst", model_name="gpt-3.5")
        registry.register(agent1)
        registry.register(agent2)
        agents = registry.list_agents()
        assert len(agents) == 2
        assert agent1 in agents
        assert agent2 in agents
    
    def test_clear_registry(self) -> None:
        """Test clearing the registry."""
        registry = AgentRegistry()
        agent = Agent(name="test", role="researcher", model_name="gpt-4")
        registry.register(agent)
        registry.clear()
        assert registry.list_agents() == []


class TestCreateAgent:
    """Tests for create_agent function."""
    
    def test_create_agent_basic(self) -> None:
        """Test creating an agent with basic parameters."""
        agent = create_agent(
            name="test",
            role="researcher",
            model_name="gpt-4",
        )
        assert agent.name == "test"
        assert agent.role == "researcher"
        assert agent.model_name == "gpt-4"
    
    def test_create_agent_with_all_parameters(self) -> None:
        """Test creating an agent with all parameters."""
        agent = create_agent(
            name="test",
            role="researcher",
            model_name="gpt-4",
            system_prompt="You are a researcher",
            tools=["search", "analyze"],
            max_iterations=5,
        )
        assert agent.system_prompt == "You are a researcher"
        assert agent.tools == ["search", "analyze"]
        assert agent.max_iterations == 5
    
    def test_create_agent_registers_in_global_registry(self) -> None:
        """Test that created agent is registered in global registry."""
        # Clear the global registry first
        registry = get_agent_registry()
        registry.clear()
        
        agent = create_agent(
            name="test",
            role="researcher",
            model_name="gpt-4",
        )
        
        found = registry.get(agent.id)
        assert found == agent


class TestGlobalAgentRegistry:
    """Tests for global agent registry."""
    
    def test_get_global_registry(self) -> None:
        """Test getting the global registry."""
        registry1 = get_agent_registry()
        registry2 = get_agent_registry()
        assert registry1 is registry2
    
    def test_global_registry_persistence(self) -> None:
        """Test that global registry persists across calls."""
        registry = get_agent_registry()
        registry.clear()
        
        agent = Agent(name="test", role="researcher", model_name="gpt-4")
        registry.register(agent)
        
        registry2 = get_agent_registry()
        assert registry2.get(agent.id) == agent
