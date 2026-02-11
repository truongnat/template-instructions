"""Agent schema definition."""

from dataclasses import dataclass, field
from typing import List, Optional, Dict, Any
from models.enums import AgentType


@dataclass
class AgentSchema:
    """Schema for agent configuration.
    
    Attributes:
        id: Unique agent identifier (required)
        type: Agent type (required)
        name: Human-readable agent name
        description: Optional agent description
        capabilities: List of agent capabilities
        model: LLM model to use for this agent
        config: Agent-specific configuration
        enabled: Whether the agent is enabled
    """
    id: str
    type: AgentType
    name: Optional[str] = None
    description: Optional[str] = None
    capabilities: List[str] = field(default_factory=list)
    model: Optional[str] = None
    config: Dict[str, Any] = field(default_factory=dict)
    enabled: bool = True
    
    def __post_init__(self):
        """Validate agent schema after initialization."""
        if not self.id:
            raise ValueError("Agent id is required")
        if not self.type:
            raise ValueError("Agent type is required")
        
        # Convert type to enum if it's a string
        if isinstance(self.type, str):
            self.type = AgentType(self.type)
        
        # Set default name if not provided
        if not self.name:
            self.name = self.id
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert agent schema to dictionary."""
        return {
            'id': self.id,
            'type': self.type.value,
            'name': self.name,
            'description': self.description,
            'capabilities': self.capabilities,
            'model': self.model,
            'config': self.config,
            'enabled': self.enabled,
        }
