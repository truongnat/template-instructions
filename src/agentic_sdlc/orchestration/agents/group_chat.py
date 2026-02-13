"""Group chat orchestration for multiple agents."""

from typing import List, Dict, Any, Optional
from dataclasses import dataclass, field
from .agent import Agent


@dataclass
class ChatMessage:
    """A message in a group chat."""
    sender: str
    content: str
    timestamp: str = field(default_factory=lambda: __import__("datetime").datetime.now().isoformat())


class GroupChat:
    """Orchestrates a conversation among multiple agents.
    
    Equivalent to Swarms' GroupChat logic.
    """
    
    def __init__(self, agents: List[Agent], name: str = "Common Room") -> None:
        """Initialize the group chat.
        
        Args:
            agents: List of agents participating in the chat.
            name: Name of the chat room.
        """
        self.agents = agents
        self.name = name
        self.messages: List[ChatMessage] = []
    
    def broadcast(self, sender: str, content: str) -> None:
        """Broadcast a message to the group chat.
        
        Args:
            sender: Name of the sender.
            content: Message content.
        """
        message = ChatMessage(sender=sender, content=content)
        self.messages.append(message)
    
    def get_history(self) -> List[Dict[str, str]]:
        """Get the chat history.
        
        Returns:
            List of message dictionaries.
        """
        return [
            {"sender": m.sender, "content": m.content, "timestamp": m.timestamp}
            for m in self.messages
        ]
