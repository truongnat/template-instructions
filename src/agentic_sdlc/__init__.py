"""Agentic SDLC - AI-powered Software Development Lifecycle Framework.

This is the public API. All exports from this module are considered stable
and follow semantic versioning.

The Agentic SDLC Kit is an AI-powered Software Development Lifecycle framework
that provides tools for orchestrating agents, managing workflows, and building
intelligent automation systems. It offers a clean separation between the SDK core
and CLI interface, with a plugin architecture for extensibility.

Key Features:
- Configuration management with validation
- Agent orchestration and coordination
- Workflow automation and execution
- Intelligence features (learning, monitoring, reasoning, collaboration)
- Infrastructure components (automation, bridging, lifecycle management)
- Plugin system for extensibility
- Comprehensive logging and error handling

Usage:
    from agentic_sdlc import Config, Agent, Workflow, create_agent
    
    # Load configuration
    config = Config()
    
    # Create and run agents
    agent = create_agent(name="my_agent", role="developer")
    
    # Build and execute workflows
    workflow = Workflow(name="my_workflow")
    # ... add steps and execute
"""

from ._version import __version__

# Core module exports
from .core import (
    # Configuration
    Config,
    get_config,
    load_config,
    # Configuration types
    AgentConfig,
    ModelConfig,
    SDKConfig,
    WorkflowConfig,
    # Exceptions
    AgenticSDLCError,
    AgentError,
    ConfigurationError,
    ModelError,
    PluginError,
    ValidationError,
    WorkflowError,
    # Logging
    get_logger,
    setup_logging,
    # Resources
    get_resource_path,
    list_resources,
    load_resource_text,
)

# Infrastructure module exports
from .infrastructure import (
    Bridge,
    BridgeRegistry,
    ExecutionEngine,
    LifecycleManager,
    Phase,
    TaskExecutor,
    WorkflowEngine,
    WorkflowRunner,
)

# Intelligence module exports
from .intelligence import (
    Collaborator,
    DecisionEngine,
    Learner,
    LearningStrategy,
    MetricsCollector,
    Monitor,
    Reasoner,
    TeamCoordinator,
)

# Orchestration module exports
from .orchestration import (
    # Agents
    Agent,
    AgentRegistry,
    create_agent,
    get_agent_registry,
    # Coordination
    Coordinator,
    ExecutionPlan,
    # Models
    ModelClient,
    create_model_client,
    get_model_client,
    register_model_client,
    # Workflows
    Workflow,
    WorkflowBuilder,
    WorkflowStep,
)

# Plugins module exports
from .plugins import (
    Plugin,
    PluginMetadata,
    PluginRegistry,
    get_plugin_registry,
)

__all__ = [
    # Version
    "__version__",
    # Core - Configuration
    "Config",
    "load_config",
    "get_config",
    # Core - Configuration types
    "AgentConfig",
    "ModelConfig",
    "SDKConfig",
    "WorkflowConfig",
    # Core - Exceptions
    "AgenticSDLCError",
    "ConfigurationError",
    "ValidationError",
    "PluginError",
    "WorkflowError",
    "AgentError",
    "ModelError",
    # Core - Logging
    "setup_logging",
    "get_logger",
    # Core - Resources
    "get_resource_path",
    "load_resource_text",
    "list_resources",
    # Infrastructure
    "WorkflowEngine",
    "WorkflowRunner",
    "Bridge",
    "BridgeRegistry",
    "ExecutionEngine",
    "TaskExecutor",
    "LifecycleManager",
    "Phase",
    # Intelligence
    "Learner",
    "LearningStrategy",
    "Monitor",
    "MetricsCollector",
    "Reasoner",
    "DecisionEngine",
    "Collaborator",
    "TeamCoordinator",
    # Orchestration - Agents
    "Agent",
    "AgentRegistry",
    "create_agent",
    "get_agent_registry",
    # Orchestration - Models
    "ModelClient",
    "create_model_client",
    "get_model_client",
    "register_model_client",
    # Orchestration - Workflows
    "Workflow",
    "WorkflowStep",
    "WorkflowBuilder",
    # Orchestration - Coordination
    "Coordinator",
    "ExecutionPlan",
    # Plugins
    "Plugin",
    "PluginMetadata",
    "PluginRegistry",
    "get_plugin_registry",
]
