"""Swarm Agent Types - Specialized agents for different roles.

Each agent type has its own role, capabilities, and behavior patterns.
Agents communicate through the MessageBus and can delegate tasks
via the handoff protocol.
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import TYPE_CHECKING, Any, Callable, Dict, List, Optional

from ..core.logging import get_logger
from .message_bus import MessageBus, SwarmMessage

if TYPE_CHECKING:
    from ..core.llm import LLMRouter

logger = get_logger(__name__)


class AgentRole(Enum):
    """Predefined agent roles in a swarm team."""
    DEVELOPER = "developer"
    REVIEWER = "reviewer"
    TESTER = "tester"
    RESEARCHER = "researcher"
    ARCHITECT = "architect"
    DOCUMENTER = "documenter"
    SUPERVISOR = "supervisor"


@dataclass
class AgentCapability:
    """A capability that an agent possesses.

    Attributes:
        name: Capability name.
        description: What this capability does.
        domains: Domains this capability applies to.
    """
    name: str
    description: str = ""
    domains: List[str] = field(default_factory=list)


class SwarmAgent:
    """Base class for swarm agents.

    Each agent has a role, capabilities, and can process tasks.
    Agents communicate via a shared MessageBus.

    Attributes:
        agent_id: Unique agent identifier.
        role: Agent's role in the swarm.
        capabilities: List of agent capabilities.
    """

    def __init__(
        self,
        agent_id: str,
        role: AgentRole,
        message_bus: Optional[MessageBus] = None,
        capabilities: Optional[List[AgentCapability]] = None,
        llm: Optional["LLMRouter"] = None,
    ):
        """Initialize a swarm agent.

        Args:
            agent_id: Unique identifier.
            role: Agent role.
            message_bus: Shared message bus.
            capabilities: Agent capabilities.
            llm: Optional LLM router for AI-powered responses.
        """
        self.agent_id = agent_id
        self.role = role
        self.capabilities = capabilities or []
        self._bus = message_bus
        self._llm = llm
        self._task_queue: List[Dict[str, Any]] = []
        self._results: List[Dict[str, Any]] = []

        if self._bus:
            self._bus.subscribe(agent_id, self._handle_message)

    def process_task(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """Process a task and return results.

        Override in subclasses for specialized behavior.

        Args:
            task: Task dictionary with 'description', 'context', etc.

        Returns:
            Result dictionary with 'status', 'output', etc.
        """
        result = {
            "agent": self.agent_id,
            "role": self.role.value,
            "task": task.get("description", ""),
            "status": "completed",
            "output": f"[{self.role.value}] Processed: {task.get('description', '')[:100]}",
        }
        self._results.append(result)
        return result

    def handoff(
        self,
        recipient_id: str,
        task: Dict[str, Any],
        reason: str = "",
    ) -> None:
        """Hand off a task to another agent.

        Args:
            recipient_id: Target agent ID.
            task: Task to hand off.
            reason: Reason for handoff.
        """
        if not self._bus:
            logger.warning("No message bus for handoff")
            return

        self._bus.publish(SwarmMessage(
            sender=self.agent_id,
            recipient=recipient_id,
            type="handoff",
            content=reason or f"Handoff from {self.agent_id}",
            metadata={"task": task},
        ))
        logger.info(f"Handoff: {self.agent_id} -> {recipient_id}")

    def report_status(self, status: str, details: str = "") -> None:
        """Report status to the supervisor.

        Args:
            status: Status string.
            details: Additional details.
        """
        if not self._bus:
            return

        self._bus.publish(SwarmMessage(
            sender=self.agent_id,
            recipient="supervisor",
            type="status",
            content=f"{status}: {details}",
            metadata={"status": status},
        ))

    def _handle_message(self, message: SwarmMessage) -> None:
        """Handle incoming messages.

        Args:
            message: Received message.
        """
        if message.type == "handoff":
            task = message.metadata.get("task", {})
            if task:
                self._task_queue.append(task)
                logger.info(
                    f"Agent {self.agent_id} received handoff from {message.sender}"
                )
        elif message.type == "request":
            self._task_queue.append({
                "description": message.content,
                "from": message.sender,
                "metadata": message.metadata,
            })

    def get_results(self) -> List[Dict[str, Any]]:
        """Get all results from processed tasks."""
        return self._results.copy()

    def get_pending_tasks(self) -> List[Dict[str, Any]]:
        """Get pending tasks in the queue."""
        return self._task_queue.copy()


class DeveloperAgent(SwarmAgent):
    """Specialized agent for code development tasks."""

    def __init__(
        self,
        agent_id: str = "developer",
        message_bus: Optional[MessageBus] = None,
        llm: Optional["LLMRouter"] = None,
    ):
        super().__init__(
            agent_id=agent_id,
            role=AgentRole.DEVELOPER,
            message_bus=message_bus,
            llm=llm,
            capabilities=[
                AgentCapability("code_generation", "Generate code implementations"),
                AgentCapability("refactoring", "Refactor existing code"),
                AgentCapability("debugging", "Debug and fix issues"),
            ],
        )

    def process_task(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """Process a development task."""
        description = task.get("description", "")
        output = f"[Developer] Implementation plan for: {description[:100]}"

        # Use LLM if available
        if self._llm:
            try:
                from ..core.llm import LLMMessage
                prev = task.get("previous_results", [])
                context_parts = [f"Task: {description}"]
                for r in prev:
                    context_parts.append(f"\n{r.get('role', 'agent')} output:\n{r.get('output', '')[:500]}")

                response = self._llm.chat([
                    LLMMessage(
                        role="system",
                        content="You are an expert software developer. Provide concrete, "
                                "actionable implementation plans with code snippets.",
                    ),
                    LLMMessage(role="user", content="\n".join(context_parts)),
                ], temperature=0.3)
                output = response.content
            except Exception as e:
                logger.debug(f"LLM unavailable for developer agent: {e}")

        result = {
            "agent": self.agent_id,
            "role": "developer",
            "task": description,
            "status": "completed",
            "output": output,
            "artifacts": [],
        }
        self._results.append(result)
        return result


class ReviewerAgent(SwarmAgent):
    """Specialized agent for code review tasks."""

    def __init__(
        self,
        agent_id: str = "reviewer",
        message_bus: Optional[MessageBus] = None,
        llm: Optional["LLMRouter"] = None,
    ):
        super().__init__(
            agent_id=agent_id,
            role=AgentRole.REVIEWER,
            message_bus=message_bus,
            llm=llm,
            capabilities=[
                AgentCapability("code_review", "Review code for quality"),
                AgentCapability("security_review", "Check for security issues"),
                AgentCapability("performance_review", "Identify performance issues"),
            ],
        )

    def process_task(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """Process a review task."""
        description = task.get("description", "")
        output = f"[Reviewer] Review for: {description[:100]}"

        # Use LLM if available
        if self._llm:
            try:
                from ..core.llm import LLMMessage
                prev = task.get("previous_results", [])
                dev_output = next(
                    (r.get("output", "") for r in prev if r.get("role") == "developer"),
                    "",
                )
                response = self._llm.chat([
                    LLMMessage(
                        role="system",
                        content="You are an expert code reviewer. Review the implementation "
                                "for quality, security, performance, and best practices.",
                    ),
                    LLMMessage(
                        role="user",
                        content=f"Task: {description}\n\nImplementation to review:\n{dev_output[:3000]}",
                    ),
                ], temperature=0.2)
                output = response.content
            except Exception as e:
                logger.debug(f"LLM unavailable for reviewer agent: {e}")

        result = {
            "agent": self.agent_id,
            "role": "reviewer",
            "task": description,
            "status": "completed",
            "output": output,
            "findings": [],
        }
        self._results.append(result)
        return result


class TesterAgent(SwarmAgent):
    """Specialized agent for testing tasks."""

    def __init__(
        self,
        agent_id: str = "tester",
        message_bus: Optional[MessageBus] = None,
        llm: Optional["LLMRouter"] = None,
    ):
        super().__init__(
            agent_id=agent_id,
            role=AgentRole.TESTER,
            message_bus=message_bus,
            llm=llm,
            capabilities=[
                AgentCapability("unit_testing", "Write and run unit tests"),
                AgentCapability("integration_testing", "Create integration tests"),
                AgentCapability("test_coverage", "Analyze test coverage"),
            ],
        )

    def process_task(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """Process a testing task."""
        result = {
            "agent": self.agent_id,
            "role": "tester",
            "task": task.get("description", ""),
            "status": "completed",
            "output": f"[Tester] Tests for: {task.get('description', '')[:100]}",
            "test_results": [],
        }
        self._results.append(result)
        return result


class ResearcherAgent(SwarmAgent):
    """Specialized agent for research and analysis tasks."""

    def __init__(
        self,
        agent_id: str = "researcher",
        message_bus: Optional[MessageBus] = None,
        llm: Optional["LLMRouter"] = None,
    ):
        super().__init__(
            agent_id=agent_id,
            role=AgentRole.RESEARCHER,
            message_bus=message_bus,
            llm=llm,
            capabilities=[
                AgentCapability("web_research", "Search the internet"),
                AgentCapability("code_analysis", "Analyze codebase patterns"),
                AgentCapability("knowledge_retrieval", "Query knowledge bases"),
            ],
        )

    def process_task(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """Process a research task."""
        result = {
            "agent": self.agent_id,
            "role": "researcher",
            "task": task.get("description", ""),
            "status": "completed",
            "output": f"[Researcher] Research for: {task.get('description', '')[:100]}",
            "sources": [],
        }
        self._results.append(result)
        return result
