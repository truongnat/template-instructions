"""Rule schema definition."""

from dataclasses import dataclass, field
from typing import Optional, Dict, Any, List
from models.enums import RuleType


@dataclass
class RuleSchema:
    """Schema for rule configuration.
    
    Attributes:
        id: Unique rule identifier (required)
        type: Rule type (required)
        name: Human-readable rule name
        description: Optional rule description
        condition: Rule condition expression
        action: Action to take when rule is triggered
        priority: Rule priority (higher values execute first)
        enabled: Whether the rule is enabled
        config: Rule-specific configuration
        tags: List of tags for categorization
    """
    id: str
    type: RuleType
    name: Optional[str] = None
    description: Optional[str] = None
    condition: Optional[str] = None
    action: Optional[str] = None
    priority: int = 0
    enabled: bool = True
    config: Dict[str, Any] = field(default_factory=dict)
    tags: List[str] = field(default_factory=list)
    
    def __post_init__(self):
        """Validate rule schema after initialization."""
        if not self.id:
            raise ValueError("Rule id is required")
        if not self.type:
            raise ValueError("Rule type is required")
        
        # Convert type to enum if it's a string
        if isinstance(self.type, str):
            self.type = RuleType(self.type)
        
        # Set default name if not provided
        if not self.name:
            self.name = self.id
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert rule schema to dictionary."""
        return {
            'id': self.id,
            'type': self.type.value,
            'name': self.name,
            'description': self.description,
            'condition': self.condition,
            'action': self.action,
            'priority': self.priority,
            'enabled': self.enabled,
            'config': self.config,
            'tags': self.tags,
        }
