"""Async Message Bus for inter-agent communication.

Provides a lightweight pub/sub message bus for agents in a swarm
to communicate asynchronously.
"""

import asyncio
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Callable, Dict, List, Optional

from ..core.logging import get_logger

logger = get_logger(__name__)


class MessagePriority(Enum):
    """Message priority levels."""
    LOW = 0
    NORMAL = 1
    HIGH = 2
    URGENT = 3


@dataclass
class SwarmMessage:
    """A message in the swarm communication bus.

    Attributes:
        sender: Agent ID of the sender.
        recipient: Agent ID (or '*' for broadcast).
        type: Message type (request, response, handoff, etc.).
        content: Message content.
        priority: Message priority level.
        metadata: Additional metadata.
        timestamp: When the message was created.
        correlation_id: ID linking related messages.
    """

    sender: str
    recipient: str
    type: str  # "request", "response", "handoff", "feedback", "status"
    content: str
    priority: MessagePriority = MessagePriority.NORMAL
    metadata: Dict[str, Any] = field(default_factory=dict)
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())
    correlation_id: str = ""


class MessageBus:
    """Async message bus for swarm agent communication.

    Supports:
    - Direct messaging between agents
    - Broadcast to all agents
    - Topic-based subscriptions
    - Message history tracking
    - Priority-based ordering

    Example:
        >>> bus = MessageBus()
        >>> bus.subscribe("developer", handler_fn)
        >>> bus.publish(SwarmMessage(
        ...     sender="supervisor",
        ...     recipient="developer",
        ...     type="request",
        ...     content="Implement the login endpoint",
        ... ))
    """

    def __init__(self, max_history: int = 1000):
        """Initialize the message bus.

        Args:
            max_history: Maximum messages to keep in history.
        """
        self._subscribers: Dict[str, List[Callable]] = {}
        self._topic_subscribers: Dict[str, List[Callable]] = {}
        self._history: List[SwarmMessage] = []
        self._max_history = max_history
        self._queue: asyncio.Queue = asyncio.Queue()

    def subscribe(
        self,
        agent_id: str,
        handler: Callable[[SwarmMessage], None],
    ) -> None:
        """Subscribe an agent to receive direct messages.

        Args:
            agent_id: Agent identifier.
            handler: Callback function for received messages.
        """
        if agent_id not in self._subscribers:
            self._subscribers[agent_id] = []
        self._subscribers[agent_id].append(handler)
        logger.debug(f"Agent '{agent_id}' subscribed to message bus")

    def subscribe_topic(
        self,
        topic: str,
        handler: Callable[[SwarmMessage], None],
    ) -> None:
        """Subscribe to a topic for broadcast messages.

        Args:
            topic: Topic name.
            handler: Callback function.
        """
        if topic not in self._topic_subscribers:
            self._topic_subscribers[topic] = []
        self._topic_subscribers[topic].append(handler)

    def publish(self, message: SwarmMessage) -> None:
        """Publish a message to the bus.

        Routes to the correct recipient or broadcasts.

        Args:
            message: Message to publish.
        """
        # Record in history
        self._history.append(message)
        if len(self._history) > self._max_history:
            self._history = self._history[-self._max_history:]

        # Route message
        if message.recipient == "*":
            # Broadcast to all subscribers
            for agent_id, handlers in self._subscribers.items():
                if agent_id != message.sender:
                    for handler in handlers:
                        try:
                            handler(message)
                        except Exception as e:
                            logger.error(f"Handler error for {agent_id}: {e}")
        else:
            # Direct message
            handlers = self._subscribers.get(message.recipient, [])
            for handler in handlers:
                try:
                    handler(message)
                except Exception as e:
                    logger.error(
                        f"Handler error for {message.recipient}: {e}"
                    )

        # Also route to topic subscribers
        topic = message.type
        topic_handlers = self._topic_subscribers.get(topic, [])
        for handler in topic_handlers:
            try:
                handler(message)
            except Exception as e:
                logger.error(f"Topic handler error for {topic}: {e}")

        logger.debug(
            f"Message: {message.sender} -> {message.recipient} [{message.type}]"
        )

    async def publish_async(self, message: SwarmMessage) -> None:
        """Publish a message asynchronously.

        Args:
            message: Message to publish.
        """
        await self._queue.put(message)
        self.publish(message)

    def get_history(
        self,
        agent_id: Optional[str] = None,
        message_type: Optional[str] = None,
        limit: int = 50,
    ) -> List[SwarmMessage]:
        """Get message history with optional filters.

        Args:
            agent_id: Filter by sender or recipient agent.
            message_type: Filter by message type.
            limit: Maximum results.

        Returns:
            List of messages (newest first).
        """
        messages = self._history.copy()

        if agent_id:
            messages = [
                m for m in messages
                if m.sender == agent_id or m.recipient == agent_id
            ]

        if message_type:
            messages = [m for m in messages if m.type == message_type]

        return messages[-limit:]

    def get_conversation(
        self, correlation_id: str
    ) -> List[SwarmMessage]:
        """Get all messages in a conversation thread.

        Args:
            correlation_id: Conversation correlation ID.

        Returns:
            List of messages in the conversation.
        """
        return [
            m for m in self._history
            if m.correlation_id == correlation_id
        ]

    def clear_history(self) -> None:
        """Clear message history."""
        self._history.clear()

    @property
    def message_count(self) -> int:
        """Total messages in history."""
        return len(self._history)

    @property
    def subscriber_count(self) -> int:
        """Number of subscribed agents."""
        return len(self._subscribers)
