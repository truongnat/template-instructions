#!/usr/bin/env python3
"""
Example 3: Creating and Using Agents

This example demonstrates:
- Creating agents with specific roles and configurations
- Configuring agent models and parameters
- Executing agent tasks
- Managing agent lifecycle

Run: python 03_agent_creation.py
"""

from agentic_sdlc import (
    Config,
    setup_logging,
    get_logger,
    Agent,
    AgentRegistry,
    create_agent,
    ModelConfig,
)


def main():
    """Main example function."""
    
    print("=" * 60)
    print("Example 3: Creating and Using Agents")
    print("=" * 60)
    print()
    
    # Setup logging
    setup_logging(level="INFO")
    logger = get_logger(__name__)
    
    # Load configuration
    print("Loading configuration...")
    config = Config()
    logger.info("Configuration loaded")
    print()
    
    # Create model configuration
    print("Creating model configuration...")
    print("-" * 40)
    
    try:
        model_config = ModelConfig(
            provider="openai",
            model_name="gpt-4",
            temperature=0.7,
            max_tokens=2000,
            timeout=30
        )
        logger.info(f"Model configured: {model_config.model_name}")
        print(f"  ✓ Provider: {model_config.provider}")
        print(f"  ✓ Model: {model_config.model_name}")
        print(f"  ✓ Temperature: {model_config.temperature}")
        print(f"  ✓ Max Tokens: {model_config.max_tokens}")
        print()
        
    except Exception as e:
        logger.error(f"Failed to create model configuration: {e}")
        return
    
    # Create agents
    print("Creating agents...")
    print("-" * 40)
    
    agents = []
    
    try:
        # Create first agent
        agent1 = create_agent(
            name="analyzer",
            role="Code Analyzer",
            model=model_config,
            system_prompt="You are an expert code analyzer. Analyze code for quality and issues.",
            tools=["code_parser", "linter"],
            max_iterations=5
        )
        agents.append(agent1)
        logger.info(f"Agent created: {agent1.name}")
        print(f"  ✓ Agent: {agent1.name}")
        print(f"    Role: {agent1.role}")
        print(f"    Tools: {', '.join(agent1.tools)}")
        print()
        
        # Create second agent
        agent2 = create_agent(
            name="executor",
            role="Task Executor",
            model=model_config,
            system_prompt="You are an expert task executor. Execute tasks efficiently and reliably.",
            tools=["task_runner", "debugger"],
            max_iterations=10
        )
        agents.append(agent2)
        logger.info(f"Agent created: {agent2.name}")
        print(f"  ✓ Agent: {agent2.name}")
        print(f"    Role: {agent2.role}")
        print(f"    Tools: {', '.join(agent2.tools)}")
        print()
        
    except Exception as e:
        logger.error(f"Failed to create agents: {e}")
        return
    
    # Register agents
    print("Registering agents...")
    print("-" * 40)
    
    try:
        registry = AgentRegistry()
        
        for agent in agents:
            registry.register(agent)
            logger.info(f"Agent registered: {agent.name}")
            print(f"  ✓ Registered: {agent.name}")
        
        print()
        
    except Exception as e:
        logger.error(f"Failed to register agents: {e}")
        return
    
    # Retrieve and use agents
    print("Retrieving and using agents...")
    print("-" * 40)
    
    try:
        # Retrieve agent from registry
        analyzer = registry.get("analyzer")
        
        if analyzer:
            logger.info(f"Retrieved agent: {analyzer.name}")
            print(f"  ✓ Retrieved: {analyzer.name}")
            print(f"    Role: {analyzer.role}")
            print(f"    Model: {analyzer.model.model_name}")
            print(f"    Max Iterations: {analyzer.max_iterations}")
            print()
        else:
            logger.warning("Agent not found in registry")
        
    except Exception as e:
        logger.error(f"Failed to retrieve agent: {e}")
        return
    
    # Display agent summary
    print("Agent Summary:")
    print("-" * 40)
    
    for agent in agents:
        print(f"  Agent: {agent.name}")
        print(f"    Role: {agent.role}")
        print(f"    Model: {agent.model.model_name}")
        print(f"    Tools: {len(agent.tools)}")
        print(f"    Max Iterations: {agent.max_iterations}")
        print()
    
    # Example: Agent lifecycle
    print("Example: Agent lifecycle management:")
    print("-" * 40)
    
    try:
        # Initialize agent
        print("  1. Initializing agent...")
        analyzer.initialize()
        logger.info(f"Agent initialized: {analyzer.name}")
        print("     ✓ Agent initialized")
        
        # Use agent (simulated)
        print("  2. Using agent...")
        print(f"     ✓ Agent '{analyzer.name}' ready for tasks")
        
        # Shutdown agent
        print("  3. Shutting down agent...")
        analyzer.shutdown()
        logger.info(f"Agent shutdown: {analyzer.name}")
        print("     ✓ Agent shutdown complete")
        
        print()
        
    except Exception as e:
        logger.error(f"Agent lifecycle error: {e}")
        return
    
    print("=" * 60)
    print("Example completed successfully!")
    print("=" * 60)


if __name__ == "__main__":
    main()
