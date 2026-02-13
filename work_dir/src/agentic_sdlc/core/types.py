"""Type definitions and data models for SDK configuration.

This module provides Pydantic models for configuration validation and type safety.
"""

from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field, ConfigDict


class ModelConfig(BaseModel):
    """Model configuration for LLM providers.
    
    Defines how to connect to and configure a language model provider.
    """

    model_config = ConfigDict(extra="forbid")

    provider: str = Field(
        ...,
        description="Model provider (e.g., 'openai', 'anthropic', 'local')",
    )
    model_name: str = Field(..., description="Model identifier (e.g., 'gpt-4', 'claude-3')")
    api_key: Optional[str] = Field(None, description="API key for authentication")
    temperature: float = Field(
        0.7,
        ge=0.0,
        le=2.0,
        description="Sampling temperature (0.0 to 2.0)",
    )
    max_tokens: Optional[int] = Field(
        None,
        gt=0,
        description="Maximum tokens in response",
    )
    timeout: int = Field(
        30,
        gt=0,
        description="Request timeout in seconds",
    )


class AgentConfig(BaseModel):
    """Agent configuration.
    
    Defines how an agent is configured, including its model, role, and capabilities.
    """

    model_config = ConfigDict(extra="forbid")

    name: str = Field(..., description="Agent name")
    role: str = Field(..., description="Agent role or responsibility")
    model: ModelConfig = Field(..., description="Model configuration for this agent")
    system_prompt: Optional[str] = Field(
        None,
        description="System prompt to guide agent behavior",
    )
    tools: List[str] = Field(
        default_factory=list,
        description="List of tool names available to this agent",
    )
    max_iterations: int = Field(
        10,
        gt=0,
        description="Maximum iterations for agent execution",
    )


class WorkflowConfig(BaseModel):
    """Workflow configuration.
    
    Defines a workflow including its agents, steps, and execution parameters.
    """

    model_config = ConfigDict(extra="forbid")

    name: str = Field(..., description="Workflow name")
    description: Optional[str] = Field(None, description="Workflow description")
    agents: List[AgentConfig] = Field(
        ...,
        description="Agents participating in this workflow",
    )
    steps: List[Dict[str, Any]] = Field(
        ...,
        description="Workflow execution steps",
    )
    timeout: int = Field(
        300,
        gt=0,
        description="Workflow timeout in seconds",
    )


class SDKConfig(BaseModel):
    """Main SDK configuration.
    
    Top-level configuration for the entire SDK including project settings,
    logging, models, workflows, and plugins.
    """

    model_config = ConfigDict(extra="forbid")

    project_root: str = Field(..., description="Project root directory path")
    log_level: str = Field(
        "INFO",
        description="Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)",
    )
    log_file: Optional[str] = Field(None, description="Log file path")
    models: Dict[str, Any] = Field(
        default_factory=dict,
        description="Named model configurations",
    )
    workflows: Dict[str, Any] = Field(
        default_factory=dict,
        description="Named workflow configurations",
    )
    plugins: List[str] = Field(
        default_factory=list,
        description="List of plugins to load",
    )
    defaults_dir: Optional[str] = Field(
        None,
        description="Custom defaults directory path",
    )
