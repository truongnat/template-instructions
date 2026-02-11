"""Skill schema definition."""

from dataclasses import dataclass, field
from typing import Optional, Dict, Any, List
from models.enums import SkillType


@dataclass
class SkillSchema:
    """Schema for skill configuration.
    
    Attributes:
        id: Unique skill identifier (required)
        type: Skill type (required)
        name: Human-readable skill name
        description: Optional skill description
        implementation: Skill implementation reference (module path or code)
        parameters: Skill parameters and their types
        returns: Return type description
        enabled: Whether the skill is enabled
        config: Skill-specific configuration
        tags: List of tags for categorization
    """
    id: str
    type: SkillType
    name: Optional[str] = None
    description: Optional[str] = None
    implementation: Optional[str] = None
    parameters: Dict[str, str] = field(default_factory=dict)
    returns: Optional[str] = None
    enabled: bool = True
    config: Dict[str, Any] = field(default_factory=dict)
    tags: List[str] = field(default_factory=list)
    
    def __post_init__(self):
        """Validate skill schema after initialization."""
        if not self.id:
            raise ValueError("Skill id is required")
        if not self.type:
            raise ValueError("Skill type is required")
        
        # Convert type to enum if it's a string
        if isinstance(self.type, str):
            self.type = SkillType(self.type)
        
        # Set default name if not provided
        if not self.name:
            self.name = self.id
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert skill schema to dictionary."""
        return {
            'id': self.id,
            'type': self.type.value,
            'name': self.name,
            'description': self.description,
            'implementation': self.implementation,
            'parameters': self.parameters,
            'returns': self.returns,
            'enabled': self.enabled,
            'config': self.config,
            'tags': self.tags,
        }
