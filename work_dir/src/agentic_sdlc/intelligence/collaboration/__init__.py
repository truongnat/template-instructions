"""Collaboration module for multi-agent collaboration and coordination."""

from .collaborator import Collaborator, TeamCoordinator, CollaborationMessage, CollaborationResult, MessageType

__all__ = [
    "Collaborator",
    "TeamCoordinator",
    "CollaborationMessage",
    "CollaborationResult",
    "MessageType",
]
