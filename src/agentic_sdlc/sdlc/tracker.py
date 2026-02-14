"""SDLC Tracker - Orchestrate the full SDLC flow.

The tracker coordinates the lifecycle: user request → requirement analysis →
skill search → task creation → execution → review → score → done/retry.
It ties together Board, SkillRegistry, PromptGenerator, and SelfReview.
"""

from pathlib import Path
from typing import Any, Dict, List, Optional

from ..core.logging import get_logger
from ..skills.skill import Skill
from .board import Board, Issue, IssueSeverity, Sprint, Task, TaskStatus

logger = get_logger(__name__)


class SDLCTracker:
    """Orchestrate the SDLC flow across skills, tasks, and reviews.

    The tracker is the main coordination point for turning user requests
    into managed, documented development workflows.

    Example:
        >>> tracker = SDLCTracker(project_name="todo-app")
        >>> sprint = tracker.plan("Create a React todo webapp")
        >>> for task in tracker.get_next_tasks():
        ...     instructions = tracker.get_task_instructions(task.id)
        ...     # Agent executes instructions...
        ...     tracker.submit_output(task.id, output, score=0.85)
    """

    def __init__(
        self,
        project_name: str,
        storage_dir: Optional[Path] = None,
    ) -> None:
        """Initialize the tracker.

        Args:
            project_name: Name of the project.
            storage_dir: Directory for persisting board state.
        """
        storage_path = None
        if storage_dir:
            storage_dir.mkdir(parents=True, exist_ok=True)
            storage_path = storage_dir / "sdlc_board.json"

        if storage_path and storage_path.exists():
            try:
                self._board = Board.load(storage_path)
                # Ensure storage_path is set to the correct Path object
                self._board.storage_path = str(storage_path)
                logger.info("Loaded existing board from %s", storage_path)
            except Exception as e:
                logger.error("Failed to load board from %s: %s", storage_path, e)
                self._board = Board(
                    project_name=project_name,
                    storage_path=str(storage_path) if storage_path else None,
                )
        else:
            self._board = Board(
                project_name=project_name,
                storage_path=str(storage_path) if storage_path else None,
            )
        self._current_sprint: Optional[Sprint] = None

    @property
    def board(self) -> Board:
        """Access the underlying board."""
        return self._board

    def plan(
        self,
        description: str,
        skills: Optional[List[Skill]] = None,
    ) -> Sprint:
        """Create a sprint from a user request.

        Breaks the request into tasks based on available skills.
        If skills are provided, creates tasks for each skill.
        Otherwise, creates a single analysis task.

        Args:
            description: User's request description.
            skills: Optional list of skills to use.

        Returns:
            Created Sprint.
        """
        sprint = self._board.create_sprint(
            name=description[:80],
            description=description,
        )
        self._current_sprint = sprint

        if skills:
            for skill in skills:
                task = self._board.create_task(
                    title=f"{skill.role.value}: {skill.name}",
                    skill_ref=skill.name,
                    role=skill.role.value,
                    description=f"Execute skill '{skill.name}' for: {description}",
                )
                self._board.add_task_to_sprint(sprint.id, task.id)
        else:
            # Default: create a requirement analysis task
            task = self._board.create_task(
                title="Analyze Requirements",
                skill_ref="requirement-analysis",
                role="analyst",
                description=f"Analyze: {description}",
            )
            self._board.add_task_to_sprint(sprint.id, task.id)

        logger.info("Planned sprint '%s' with %d tasks", sprint.name, len(sprint.task_ids))
        return sprint

    def get_next_tasks(self) -> List[Task]:
        """Get tasks ready to execute (TODO or RETRY, with dependencies met).

        Returns:
            List of executable tasks.
        """
        ready = []
        for task in self._board.tasks.values():
            if task.status in (TaskStatus.TODO, TaskStatus.RETRY, TaskStatus.BACKLOG):
                # Check if parent is done (if has parent)
                if task.parent_task:
                    parent = self._board.tasks.get(task.parent_task)
                    if parent and parent.status != TaskStatus.DONE:
                        continue
                ready.append(task)
        return ready

    def start_task(self, task_id: str) -> None:
        """Mark a task as in progress."""
        self._board.update_task_status(task_id, TaskStatus.IN_PROGRESS)

    def submit_output(
        self,
        task_id: str,
        output_path: str = "",
        score: Optional[float] = None,
    ) -> Task:
        """Submit task output and optionally set score.

        Args:
            task_id: Task ID.
            output_path: Path to output artifact.
            score: Review score (0.0 - 1.0).

        Returns:
            Updated Task.
        """
        task = self._board.tasks.get(task_id)
        if not task:
            raise ValueError(f"Task not found: {task_id}")

        task.output_ref = output_path

        if score is not None:
            self._board.set_task_score(task_id, score)

            if score >= 0.7:
                self._board.update_task_status(task_id, TaskStatus.DONE)
            else:
                task.retry_count += 1
                if task.retry_count >= task.max_retries:
                    self._board.update_task_status(task_id, TaskStatus.FAILED)
                    self._board.create_issue(
                        title=f"Task failed after {task.max_retries} retries: {task.title}",
                        severity=IssueSeverity.MAJOR,
                        task_ref=task_id,
                    )
                else:
                    self._board.update_task_status(task_id, TaskStatus.RETRY)
        else:
            self._board.update_task_status(task_id, TaskStatus.REVIEW)

        return task

    def complete_sprint(self, sprint_id: Optional[str] = None) -> Dict[str, Any]:
        """Complete a sprint and generate summary.

        Args:
            sprint_id: Sprint to complete. Uses current sprint if None.

        Returns:
            Sprint summary dictionary.
        """
        sid = sprint_id or (self._current_sprint.id if self._current_sprint else None)
        if not sid:
            raise ValueError("No sprint to complete")

        progress = self._board.get_sprint_progress(sid)
        sprint = self._board.sprints[sid]
        sprint.completed_at = __import__("datetime").datetime.now().isoformat()

        self._board._save()
        return progress

    def get_board_markdown(self) -> str:
        """Get board state as markdown."""
        return self._board.to_markdown()
