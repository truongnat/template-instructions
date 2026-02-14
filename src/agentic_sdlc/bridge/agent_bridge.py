"""Agent Bridge - Main interface between core and CLI/IDE agents.

The AgentBridge is the primary entry point for external agents.
It processes user requests, finds relevant skills, generates prompts,
manages SDLC state, and handles output submission with review.
"""

from pathlib import Path
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field

from ..core.logging import get_logger
from ..prompts.generator import PromptGenerator
from ..prompts.context_optimizer import ContextOptimizer, ContextItem
from ..sdlc.board import TaskStatus
from ..sdlc.tracker import SDLCTracker
from ..skills.generator import SkillGenerator
from ..skills.registry import SkillRegistry
from ..skills.skill import Skill

logger = get_logger(__name__)


class AgentResponse(BaseModel):
    """Response from the AgentBridge to the calling agent.

    Contains the generated instructions, context, and metadata
    the agent needs to execute the task.
    """

    success: bool = True
    message: str = ""
    skill_instructions: str = Field(default="", description="SKILL.md content for agent")
    prompt: str = Field(default="", description="Optimized execution prompt")
    board_state: str = Field(default="", description="Current board markdown")
    task_id: Optional[str] = None
    sprint_id: Optional[str] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)


class AgentBridge:
    """Bridge between agentic-sdlc core and external CLI/IDE agents.

    This is the main coordination class. It handles:
    1. Processing user requests into skill lookups
    2. Generating optimized prompts for agent execution
    3. Managing SDLC board state
    4. Submitting and reviewing outputs

    Example:
        >>> bridge = AgentBridge(project_dir=Path("."))
        >>> response = bridge.process_request("Create a todo webapp")
        >>> # Agent reads response.skill_instructions and executes
        >>> result = bridge.submit_output(response.task_id, "output here")
    """

    def __init__(
        self,
        project_dir: Path,
        project_name: Optional[str] = None,
    ) -> None:
        """Initialize the bridge.

        Args:
            project_dir: Project root directory.
            project_name: Project name (defaults to directory name).
        """
        self._project_dir = project_dir
        self._project_name = project_name or project_dir.name

        # Storage directories
        self._data_dir = project_dir / ".agentic_sdlc"
        self._skills_dir = self._data_dir / "skills"
        self._generated_dir = self._skills_dir / "generated"

        # Initialize components
        self._registry = SkillRegistry(
            metadata_path=self._data_dir / "skill_metadata.json"
        )
        self._generator = SkillGenerator(output_dir=self._generated_dir)
        self._prompt_gen = PromptGenerator()
        self._context_opt = ContextOptimizer()
        self._tracker = SDLCTracker(
            project_name=self._project_name,
            storage_dir=self._data_dir,
        )

        # Load built-in skills
        builtin_dir = Path(__file__).parent.parent / "skills" / "builtin"
        self._registry.discover(builtin_dir)

        # Load generated skills
        if self._generated_dir.exists():
            self._registry.discover(self._generated_dir)

        # Load user skills
        user_skills_dir = project_dir / ".agentic_sdlc" / "skills"
        if user_skills_dir.exists():
            self._registry.discover(user_skills_dir)

        logger.info(
            "AgentBridge initialized: %s (%d skills)",
            self._project_name,
            self._registry.count,
        )

    def process_request(
        self,
        user_input: str,
        context: Optional[Dict[str, Any]] = None,
        agent_type: str = "antigravity",
    ) -> AgentResponse:
        """Process a user request into actionable agent instructions.

        Flow:
        1. Search for matching skills
        2. Generate new skill if none found
        3. Create SDLC sprint + tasks
        4. Generate optimized prompt
        5. Return instructions for agent

        Args:
            user_input: User's natural language request.
            context: Optional project context.
            agent_type: Target agent (antigravity, gemini, cursor, generic).

        Returns:
            AgentResponse with instructions and metadata.
        """
        context = context or {}

        # Step 1: Find matching skills
        skills = self._registry.search(user_input, limit=5)

        # Step 2: Generate skill if no good matches
        if not skills:
            logger.info("No matching skills found, generating...")
            generated = self._generator.generate(user_input, context)
            self._registry.register(generated)
            skills = [generated]

        # Step 3: Create SDLC sprint
        sprint = self._tracker.plan(user_input, skills)

        # Step 4: Get first task
        next_tasks = self._tracker.get_next_tasks()
        if not next_tasks:
            return AgentResponse(
                success=False,
                message="No tasks to execute",
                sprint_id=sprint.id,
            )

        task = next_tasks[0]
        self._tracker.start_task(task.id)

        # Step 5: Find the skill for this task
        skill = self._registry.get(task.skill_ref) or skills[0]

        # Step 6: Generate optimized prompt
        prompt = self._prompt_gen.generate(skill, context, agent_type)
        skill_md = skill.to_skill_md()

        return AgentResponse(
            success=True,
            message=f"Ready to execute: {task.title}",
            skill_instructions=skill_md,
            prompt=prompt,
            board_state=self._tracker.get_board_markdown(),
            task_id=task.id,
            sprint_id=sprint.id,
            metadata={
                "skill_name": skill.name,
                "role": skill.role.value,
                "category": skill.category,
                "total_tasks": len(sprint.task_ids),
            },
        )

    def get_task_instructions(
        self,
        task_id: str,
        agent_type: str = "antigravity",
    ) -> AgentResponse:
        """Get instructions for a specific task.

        Args:
            task_id: Task ID from the board.
            agent_type: Target agent type.

        Returns:
            AgentResponse with skill instructions.
        """
        task = self._tracker.board.tasks.get(task_id)
        if not task:
            return AgentResponse(success=False, message=f"Task not found: {task_id}")

        skill = self._registry.get(task.skill_ref)
        if not skill:
            return AgentResponse(
                success=False,
                message=f"Skill not found: {task.skill_ref}",
            )

        self._tracker.start_task(task_id)
        prompt = self._prompt_gen.generate(skill, agent_type=agent_type)

        return AgentResponse(
            success=True,
            message=f"Instructions for: {task.title}",
            skill_instructions=skill.to_skill_md(),
            prompt=prompt,
            task_id=task_id,
            metadata={"skill_name": skill.name},
        )

    def submit_output(
        self,
        task_id: str,
        output: str,
        score: Optional[float] = None,
    ) -> AgentResponse:
        """Submit task output for review and scoring.

        Args:
            task_id: Task ID.
            output: Agent's output text.
            score: Optional review score (0.0-1.0).

        Returns:
            AgentResponse with review result.
        """
        task = self._tracker.board.tasks.get(task_id)
        if not task:
            return AgentResponse(success=False, message=f"Task not found: {task_id}")

        # Store output
        output_dir = self._data_dir / "outputs"
        output_dir.mkdir(parents=True, exist_ok=True)
        output_path = output_dir / f"{task_id}.md"
        output_path.write_text(output, encoding="utf-8")

        # Submit to tracker
        updated_task = self._tracker.submit_output(
            task_id, str(output_path), score
        )

        # Update skill metadata
        if task.skill_ref:
            self._registry.update_metadata(
                task.skill_ref,
                success=(updated_task.status == TaskStatus.DONE),
                score=score,
            )

        # Generate review prompt if no score provided
        review_prompt = ""
        if score is None:
            skill = self._registry.get(task.skill_ref)
            if skill:
                review_prompt = self._prompt_gen.generate_review_prompt(output, skill)

        return AgentResponse(
            success=True,
            message=f"Task {task_id}: {updated_task.status.value}",
            prompt=review_prompt,
            board_state=self._tracker.get_board_markdown(),
            task_id=task_id,
            metadata={
                "status": updated_task.status.value,
                "score": score,
                "retry_count": updated_task.retry_count,
            },
        )

    def get_board(self) -> str:
        """Get current board state as markdown."""
        return self._tracker.get_board_markdown()

    def search_skills(self, query: str, limit: int = 10) -> List[Dict[str, Any]]:
        """Search the skill registry.

        Args:
            query: Search query.
            limit: Max results.

        Returns:
            List of skill summaries.
        """
        skills = self._registry.search(query, limit=limit)
        return [
            {
                "name": s.name,
                "description": s.description[:100],
                "role": s.role.value,
                "category": s.category,
                "tags": s.tags,
                "success_rate": s.metadata.success_rate,
            }
            for s in skills
        ]

    def generate_skill(
        self, description: str, context: Optional[Dict] = None
    ) -> Dict[str, Any]:
        """Generate a new skill from description.

        Args:
            description: Task description.
            context: Optional context.

        Returns:
            Generated skill summary.
        """
        skill = self._generator.generate(description, context)
        self._registry.register(skill)
        return {
            "name": skill.name,
            "role": skill.role.value,
            "category": skill.category,
            "steps": len(skill.workflow_steps),
            "skill_md": skill.to_skill_md(),
        }
