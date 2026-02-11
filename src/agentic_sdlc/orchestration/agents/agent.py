"""Agent definitions and management."""

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional
from uuid import uuid4


@dataclass
class Agent:
    """Represents an agent in the orchestration system.
    
    An agent is an autonomous entity that can execute tasks, collaborate
    with other agents, and maintain state across workflow executions.
    """
    
    name: str
    role: str
    model_name: str
    system_prompt: Optional[str] = None
    tools: List[str] = field(default_factory=list)
    max_iterations: int = 10
    id: str = field(default_factory=lambda: str(uuid4()))
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def __post_init__(self) -> None:
        """Validate agent configuration."""
        if not self.name:
            raise ValueError("Agent name cannot be empty")
        if not self.role:
            raise ValueError("Agent role cannot be empty")
        if not self.model_name:
            raise ValueError("Agent model_name cannot be empty")
        if self.max_iterations < 1:
            raise ValueError("Agent max_iterations must be at least 1")
