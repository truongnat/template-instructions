"""
HITL - Human-in-the-Loop Module

Part of Layer 2: Intelligence Layer.
"""

from .hitl_manager import (
    ApprovalGate,
    ApprovalRequest,
    ApprovalResult,
    ApprovalStatus,
    HITLManager,
)

__all__ = [
    "ApprovalGate",
    "ApprovalRequest", 
    "ApprovalResult",
    "ApprovalStatus",
    "HITLManager",
]
