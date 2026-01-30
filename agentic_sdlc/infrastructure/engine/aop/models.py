"""
Agent Orchestration Protocol (AOP) - Data Models.

Defines the standard schema for inter-agent and agent-to-server communication
in a distributed environment.
"""

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional


class TaskPriority(Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class AgentStatus(Enum):
    IDLE = "idle"
    BUSY = "busy"
    OFFLINE = "offline"
    ERROR = "error"


@dataclass
class AgentRegistration:
    """Agent self-registration data."""
    id: str
    role: str
    capabilities: List[str]
    endpoint: str
    status: AgentStatus = AgentStatus.IDLE
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class AgentTask:
    """Task assigned to an agent via AOP."""
    id: str
    objective: str
    priority: TaskPriority = TaskPriority.MEDIUM
    context: Dict[str, Any] = field(default_factory=dict)
    timeout_seconds: int = 300
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())


@dataclass
class AgentResponse:
    """Standard response from an agent."""
    task_id: str
    agent_id: str
    output: str
    success: bool
    duration_seconds: float
    error: Optional[str] = None
    completed_at: str = field(default_factory=lambda: datetime.now().isoformat())
    artifacts: List[str] = field(default_factory=list)


def to_dict(obj: Any) -> Dict[str, Any]:
    """Helper to convert AOP objects to dictionaries."""
    if hasattr(obj, "__dict__"):
        res = {}
        for k, v in obj.__dict__.items():
            if isinstance(v, Enum):
                res[k] = v.value
            elif isinstance(v, list):
                res[k] = [to_dict(i) for i in v]
            elif isinstance(v, dict):
                res[k] = {nk: to_dict(nv) for nk, nv in v.items()}
            else:
                res[k] = to_dict(v)
        return res
    return obj
