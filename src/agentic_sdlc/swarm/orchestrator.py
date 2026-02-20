"""Swarm Orchestrator - Multi-agent team management and task distribution.

Manages the lifecycle of agent teams, distributes tasks, coordinates
execution (sequential/parallel), and collects results.
"""

import asyncio
import hashlib
from dataclasses import dataclass, field
from datetime import datetime
from typing import TYPE_CHECKING, Any, Dict, List, Optional

from ..core.logging import get_logger
from .agents import (
    AgentRole,
    DeveloperAgent,
    ResearcherAgent,
    ReviewerAgent,
    SwarmAgent,
    TesterAgent,
)
from .message_bus import MessageBus, SwarmMessage

if TYPE_CHECKING:
    from ..core.llm import LLMRouter

logger = get_logger(__name__)


@dataclass
class SwarmConfig:
    """Configuration for a swarm execution.

    Attributes:
        team_roles: Roles to include in the team.
        execution_mode: "sequential", "parallel", or "pipeline".
        max_iterations: Max rounds of agent collaboration.
        timeout_seconds: Timeout for the entire swarm execution.
        enable_review: Whether to include a review step.
        enable_testing: Whether to include a testing step.
    """

    team_roles: List[AgentRole] = field(
        default_factory=lambda: [
            AgentRole.RESEARCHER,
            AgentRole.DEVELOPER,
            AgentRole.REVIEWER,
        ]
    )
    execution_mode: str = "pipeline"  # sequential, parallel, pipeline
    max_iterations: int = 3
    timeout_seconds: int = 300
    enable_review: bool = True
    enable_testing: bool = False


@dataclass
class SwarmResult:
    """Result from a swarm execution.

    Attributes:
        session_id: Unique session identifier.
        task: Original task description.
        agents: Participating agent roles.
        results: Results from each agent.
        combined_output: Merged output from all agents.
        status: Overall execution status.
        messages: Inter-agent messages during execution.
        duration_ms: Execution duration in milliseconds.
        timestamp: When the execution completed.
    """

    session_id: str
    task: str
    agents: List[str]
    results: List[Dict[str, Any]] = field(default_factory=list)
    combined_output: str = ""
    status: str = "pending"  # pending, running, completed, failed
    messages: List[Dict[str, Any]] = field(default_factory=list)
    duration_ms: int = 0
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())


class SwarmOrchestrator:
    """Orchestrates multi-agent swarm execution.

    Manages agent teams, distributes tasks according to execution mode,
    coordinates agent collaboration via the message bus, and collects
    results.

    Execution Modes:
    - **Sequential**: Agents process task one after another
    - **Parallel**: All agents work simultaneously
    - **Pipeline**: Research → Develop → Review → Test

    Example:
        >>> orchestrator = SwarmOrchestrator()
        >>> result = orchestrator.execute(
        ...     task="Build a REST API with auth",
        ...     config=SwarmConfig(
        ...         team_roles=[AgentRole.RESEARCHER, AgentRole.DEVELOPER],
        ...         execution_mode="pipeline",
        ...     ),
        ... )
        >>> print(result.combined_output)
    """

    def __init__(
        self,
        message_bus: Optional[MessageBus] = None,
        llm: Optional["LLMRouter"] = None,
    ):
        """Initialize the swarm orchestrator.

        Args:
            message_bus: Shared message bus. Creates one if not provided.
            llm: Optional LLM router. Passed to all created agents.
        """
        self._bus = message_bus or MessageBus()
        self._llm = llm
        self._agents: Dict[str, SwarmAgent] = {}
        self._sessions: List[SwarmResult] = []

    def execute(
        self,
        task: str,
        config: Optional[SwarmConfig] = None,
        context: Optional[Dict[str, Any]] = None,
    ) -> SwarmResult:
        """Execute a task with a swarm of agents.

        Args:
            task: Task description.
            config: Swarm configuration.
            context: Additional context for agents.

        Returns:
            SwarmResult with all agent outputs.
        """
        config = config or SwarmConfig()
        context = context or {}
        start_time = datetime.now()

        # Generate session ID
        session_id = hashlib.md5(
            f"{task}:{start_time.isoformat()}".encode()
        ).hexdigest()[:12]

        # Create agent team
        team = self._create_team(config.team_roles)

        result = SwarmResult(
            session_id=session_id,
            task=task,
            agents=[a.agent_id for a in team],
            status="running",
        )

        try:
            # Execute based on mode
            if config.execution_mode == "parallel":
                agent_results = self._execute_parallel(team, task, context)
            elif config.execution_mode == "sequential":
                agent_results = self._execute_sequential(team, task, context)
            else:  # pipeline
                agent_results = self._execute_pipeline(team, task, context)

            result.results = agent_results
            result.combined_output = self._combine_outputs(agent_results)
            result.status = "completed"

        except Exception as e:
            logger.error(f"Swarm execution failed: {e}")
            result.status = "failed"
            result.combined_output = f"Execution failed: {str(e)}"

        # Record timing and messages
        end_time = datetime.now()
        result.duration_ms = int((end_time - start_time).total_seconds() * 1000)
        result.messages = [
            {
                "sender": m.sender,
                "recipient": m.recipient,
                "type": m.type,
                "content": m.content[:200],
            }
            for m in self._bus.get_history(limit=100)
        ]

        self._sessions.append(result)
        logger.info(
            f"Swarm session {session_id}: {result.status} "
            f"({len(team)} agents, {result.duration_ms}ms)"
        )
        return result

    def get_sessions(self) -> List[SwarmResult]:
        """Get all swarm sessions."""
        return self._sessions.copy()

    def _create_team(self, roles: List[AgentRole]) -> List[SwarmAgent]:
        """Create a team of agents for the given roles.

        Args:
            roles: Roles to fill.

        Returns:
            List of created agents.
        """
        team: List[SwarmAgent] = []
        role_factories = {
            AgentRole.DEVELOPER: DeveloperAgent,
            AgentRole.REVIEWER: ReviewerAgent,
            AgentRole.TESTER: TesterAgent,
            AgentRole.RESEARCHER: ResearcherAgent,
        }

        for role in roles:
            factory = role_factories.get(role)
            if factory:
                agent = factory(message_bus=self._bus, llm=self._llm)
                team.append(agent)
                self._agents[agent.agent_id] = agent
            else:
                # Generic agent for unregistered roles
                agent = SwarmAgent(
                    agent_id=role.value,
                    role=role,
                    message_bus=self._bus,
                    llm=self._llm,
                )
                team.append(agent)
                self._agents[agent.agent_id] = agent

        return team

    def _execute_pipeline(
        self,
        team: List[SwarmAgent],
        task: str,
        context: Dict[str, Any],
    ) -> List[Dict[str, Any]]:
        """Execute in pipeline mode: each agent feeds into the next.

        Execution order follows SDLC:
        Research → Develop → Review → Test

        Args:
            team: Agent team.
            task: Task description.
            context: Additional context.

        Returns:
            List of results from each agent.
        """
        # Define pipeline order
        role_order = [
            AgentRole.RESEARCHER,
            AgentRole.DEVELOPER,
            AgentRole.REVIEWER,
            AgentRole.TESTER,
        ]

        # Sort team by pipeline order
        ordered = sorted(
            team,
            key=lambda a: (
                role_order.index(a.role) if a.role in role_order else 99
            ),
        )

        results = []
        accumulated_context = {**context}

        for agent in ordered:
            task_data = {
                "description": task,
                "context": accumulated_context,
                "previous_results": results,
            }

            # Notify via bus
            self._bus.publish(SwarmMessage(
                sender="orchestrator",
                recipient=agent.agent_id,
                type="request",
                content=f"Process task: {task[:100]}",
                metadata=task_data,
            ))

            # Process
            result = agent.process_task(task_data)
            results.append(result)

            # Feed result into next agent's context
            accumulated_context[f"{agent.role.value}_output"] = result.get("output", "")

        return results

    def _execute_sequential(
        self,
        team: List[SwarmAgent],
        task: str,
        context: Dict[str, Any],
    ) -> List[Dict[str, Any]]:
        """Execute sequentially: agents process one after another."""
        results = []
        for agent in team:
            task_data = {
                "description": task,
                "context": context,
                "previous_results": results,
            }
            result = agent.process_task(task_data)
            results.append(result)
        return results

    def _execute_parallel(
        self,
        team: List[SwarmAgent],
        task: str,
        context: Dict[str, Any],
    ) -> List[Dict[str, Any]]:
        """Execute in parallel: all agents process simultaneously.

        For sync execution, we simulate parallelism by running
        all agents and collecting results.
        """
        results = []
        for agent in team:
            task_data = {
                "description": task,
                "context": context,
            }
            result = agent.process_task(task_data)
            results.append(result)
        return results

    def _combine_outputs(self, results: List[Dict[str, Any]]) -> str:
        """Combine outputs from multiple agents into a single string.

        Args:
            results: Agent results.

        Returns:
            Combined output string.
        """
        parts = []
        for result in results:
            role = result.get("role", "agent")
            output = result.get("output", "")
            status = result.get("status", "unknown")
            parts.append(f"## {role.title()} [{status}]\n{output}")

        return "\n\n---\n\n".join(parts)
