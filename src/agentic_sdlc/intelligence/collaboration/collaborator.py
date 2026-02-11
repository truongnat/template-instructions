"""Multi-agent collaboration and coordination."""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Dict, List, Optional, Any
from enum import Enum


class MessageType(Enum):
    """Types of messages in collaboration."""
    REQUEST = "request"
    RESPONSE = "response"
    FEEDBACK = "feedback"
    NOTIFICATION = "notification"


@dataclass
class CollaborationMessage:
    """A message in agent collaboration."""
    sender: str
    recipient: str
    message_type: MessageType
    content: str
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class CollaborationResult:
    """Result of a collaboration session."""
    task: str
    participants: List[str]
    messages: List[CollaborationMessage]
    outcome: str
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())


class Collaborator:
    """Manages collaboration between agents."""

    def __init__(self, agent_name: str):
        """Initialize a collaborator.

        Args:
            agent_name: Name of the agent
        """
        self.agent_name = agent_name
        self.messages: List[CollaborationMessage] = []
        self.collaborations: List[CollaborationResult] = []

    def send_message(
        self,
        recipient: str,
        message_type: MessageType,
        content: str,
        metadata: Optional[Dict] = None,
    ) -> CollaborationMessage:
        """Send a message to another agent.

        Args:
            recipient: Recipient agent name
            message_type: Type of message
            content: Message content
            metadata: Optional metadata

        Returns:
            CollaborationMessage object
        """
        message = CollaborationMessage(
            sender=self.agent_name,
            recipient=recipient,
            message_type=message_type,
            content=content,
            metadata=metadata or {},
        )
        self.messages.append(message)
        return message

    def receive_message(self, message: CollaborationMessage) -> None:
        """Receive a message from another agent.

        Args:
            message: CollaborationMessage to receive
        """
        self.messages.append(message)

    def get_messages(self, sender: Optional[str] = None) -> List[CollaborationMessage]:
        """Get messages, optionally filtered by sender.

        Args:
            sender: Optional sender to filter by

        Returns:
            List of messages
        """
        if sender:
            return [m for m in self.messages if m.sender == sender]
        return self.messages.copy()

    def get_message_history(self) -> List[CollaborationMessage]:
        """Get full message history.

        Returns:
            List of all messages
        """
        return self.messages.copy()

    def record_collaboration(
        self,
        task: str,
        participants: List[str],
        outcome: str,
    ) -> CollaborationResult:
        """Record a collaboration session.

        Args:
            task: Task description
            participants: List of participant agent names
            outcome: Outcome of collaboration

        Returns:
            CollaborationResult object
        """
        result = CollaborationResult(
            task=task,
            participants=participants,
            messages=self.messages.copy(),
            outcome=outcome,
        )
        self.collaborations.append(result)
        return result

    def get_collaboration_history(self) -> List[CollaborationResult]:
        """Get collaboration history.

        Returns:
            List of past collaborations
        """
        return self.collaborations.copy()


class TeamCoordinator:
    """Coordinates collaboration between multiple agents."""

    def __init__(self):
        """Initialize the team coordinator."""
        self.agents: Dict[str, Collaborator] = {}
        self.sessions: List[Dict] = []

    def register_agent(self, agent_name: str) -> Collaborator:
        """Register an agent with the coordinator.

        Args:
            agent_name: Name of the agent

        Returns:
            Collaborator instance for the agent
        """
        if agent_name not in self.agents:
            self.agents[agent_name] = Collaborator(agent_name)
        return self.agents[agent_name]

    def get_agent(self, agent_name: str) -> Optional[Collaborator]:
        """Get a registered agent.

        Args:
            agent_name: Name of the agent

        Returns:
            Collaborator instance or None
        """
        return self.agents.get(agent_name)

    def get_all_agents(self) -> Dict[str, Collaborator]:
        """Get all registered agents.

        Returns:
            Dictionary of agent names to Collaborator instances
        """
        return self.agents.copy()

    def send_message(
        self,
        sender: str,
        recipient: str,
        message_type: MessageType,
        content: str,
        metadata: Optional[Dict] = None,
    ) -> Optional[CollaborationMessage]:
        """Send a message between agents.

        Args:
            sender: Sender agent name
            recipient: Recipient agent name
            message_type: Type of message
            content: Message content
            metadata: Optional metadata

        Returns:
            CollaborationMessage or None if agents not found
        """
        sender_agent = self.get_agent(sender)
        recipient_agent = self.get_agent(recipient)

        if not sender_agent or not recipient_agent:
            return None

        message = sender_agent.send_message(recipient, message_type, content, metadata)
        recipient_agent.receive_message(message)
        return message

    def start_session(self, task: str, participants: List[str]) -> Dict:
        """Start a collaboration session.

        Args:
            task: Task description
            participants: List of participant agent names

        Returns:
            Session dictionary
        """
        session = {
            "task": task,
            "participants": participants,
            "start_time": datetime.now().isoformat(),
            "messages": [],
        }
        self.sessions.append(session)
        return session

    def end_session(self, session_index: int, outcome: str) -> Optional[Dict]:
        """End a collaboration session.

        Args:
            session_index: Index of the session
            outcome: Outcome of the session

        Returns:
            Updated session dictionary or None
        """
        if 0 <= session_index < len(self.sessions):
            session = self.sessions[session_index]
            session["end_time"] = datetime.now().isoformat()
            session["outcome"] = outcome
            return session
        return None

    def get_sessions(self) -> List[Dict]:
        """Get all collaboration sessions.

        Returns:
            List of sessions
        """
        return self.sessions.copy()

    def get_team_stats(self) -> Dict[str, Any]:
        """Get statistics about the team.

        Returns:
            Dictionary with team statistics
        """
        total_messages = sum(len(agent.get_message_history()) for agent in self.agents.values())
        total_collaborations = sum(
            len(agent.get_collaboration_history()) for agent in self.agents.values()
        )

        return {
            "total_agents": len(self.agents),
            "total_messages": total_messages,
            "total_collaborations": total_collaborations,
            "total_sessions": len(self.sessions),
            "agents": list(self.agents.keys()),
        }
