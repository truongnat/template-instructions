"""SDLC Board - Project board with Tasks, Issues, and Sprints.

The Board is the central state manager for the SDLC lifecycle.
Each user request becomes a Sprint, broken into Tasks that reference Skills.
Issues track problems discovered during review.
"""

import json
import uuid
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field

from ..core.logging import get_logger

logger = get_logger(__name__)


class TaskStatus(str, Enum):
    """Status of an SDLC task."""

    BACKLOG = "backlog"
    TODO = "todo"
    IN_PROGRESS = "in_progress"
    REVIEW = "review"
    DONE = "done"
    FAILED = "failed"
    RETRY = "retry"


class IssueSeverity(str, Enum):
    """Severity of an issue."""

    CRITICAL = "critical"
    MAJOR = "major"
    MINOR = "minor"
    SUGGESTION = "suggestion"


class Task(BaseModel):
    """An SDLC task linked to a skill execution.

    Tasks represent units of work assigned to agents via skills.
    Each task tracks its lifecycle from creation through completion.
    """

    id: str = Field(default_factory=lambda: str(uuid.uuid4())[:8])
    title: str
    description: str = ""
    status: TaskStatus = TaskStatus.BACKLOG
    skill_ref: str = Field(default="", description="Skill name to execute")
    assigned_role: str = ""
    output_ref: str = Field(default="", description="Path to output artifact")
    review_score: Optional[float] = None
    parent_task: Optional[str] = None
    subtasks: List[str] = Field(default_factory=list)
    created_at: str = Field(default_factory=lambda: datetime.now().isoformat())
    updated_at: str = Field(default_factory=lambda: datetime.now().isoformat())
    retry_count: int = 0
    max_retries: int = 3
    metadata: Dict[str, Any] = Field(default_factory=dict)

    def transition(self, new_status: TaskStatus) -> None:
        """Transition task to a new status with timestamp update."""
        self.status = new_status
        self.updated_at = datetime.now().isoformat()


class Issue(BaseModel):
    """An issue discovered during review or testing."""

    id: str = Field(default_factory=lambda: str(uuid.uuid4())[:8])
    title: str
    description: str = ""
    severity: IssueSeverity = IssueSeverity.MINOR
    task_ref: str = Field(default="", description="Related task ID")
    created_at: str = Field(default_factory=lambda: datetime.now().isoformat())
    resolved: bool = False
    resolution: str = ""


class Sprint(BaseModel):
    """A sprint grouping related tasks from a single user request."""

    id: str = Field(default_factory=lambda: str(uuid.uuid4())[:8])
    name: str
    description: str = ""
    task_ids: List[str] = Field(default_factory=list)
    created_at: str = Field(default_factory=lambda: datetime.now().isoformat())
    completed_at: Optional[str] = None

    @property
    def is_complete(self) -> bool:
        return self.completed_at is not None


class Board(BaseModel):
    """Project board managing the full SDLC lifecycle.

    The board is the single source of truth for project state.
    It tracks tasks, issues, and sprints, and persists state to disk.

    Example:
        >>> board = Board(project_name="todo-app")
        >>> sprint = board.create_sprint("Build todo app")
        >>> task = board.create_task("Implement API", skill_ref="code-implementation")
        >>> board.add_task_to_sprint(sprint.id, task.id)
    """

    project_name: str
    tasks: Dict[str, Task] = Field(default_factory=dict)
    issues: Dict[str, Issue] = Field(default_factory=dict)
    sprints: Dict[str, Sprint] = Field(default_factory=dict)
    storage_path: Optional[str] = None

    def create_sprint(self, name: str, description: str = "") -> Sprint:
        """Create a new sprint."""
        sprint = Sprint(name=name, description=description)
        self.sprints[sprint.id] = sprint
        self._save()
        logger.info("Created sprint: %s (%s)", sprint.name, sprint.id)
        return sprint

    def create_task(
        self,
        title: str,
        skill_ref: str = "",
        role: str = "",
        parent_task: Optional[str] = None,
        description: str = "",
    ) -> Task:
        """Create a new task."""
        task = Task(
            title=title,
            description=description,
            skill_ref=skill_ref,
            assigned_role=role,
            parent_task=parent_task,
        )
        self.tasks[task.id] = task

        # Link to parent
        if parent_task and parent_task in self.tasks:
            self.tasks[parent_task].subtasks.append(task.id)

        self._save()
        logger.info("Created task: %s (%s) → skill:%s", task.title, task.id, skill_ref)
        return task

    def create_issue(
        self,
        title: str,
        severity: IssueSeverity = IssueSeverity.MINOR,
        task_ref: str = "",
        description: str = "",
    ) -> Issue:
        """Create a new issue."""
        issue = Issue(
            title=title,
            description=description,
            severity=severity,
            task_ref=task_ref,
        )
        self.issues[issue.id] = issue
        self._save()
        logger.info("Created issue: %s [%s]", issue.title, issue.severity.value)
        return issue

    def add_task_to_sprint(self, sprint_id: str, task_id: str) -> None:
        """Add a task to a sprint."""
        if sprint_id in self.sprints and task_id in self.tasks:
            self.sprints[sprint_id].task_ids.append(task_id)
            self._save()

    def update_task_status(self, task_id: str, status: TaskStatus) -> None:
        """Update task status."""
        if task_id in self.tasks:
            self.tasks[task_id].transition(status)
            self._save()

    def set_task_score(self, task_id: str, score: float) -> None:
        """Set the review score for a task."""
        if task_id in self.tasks:
            self.tasks[task_id].review_score = score
            self._save()

    def get_tasks_by_status(self, status: TaskStatus) -> List[Task]:
        """Get all tasks with a given status."""
        return [t for t in self.tasks.values() if t.status == status]

    def get_sprint_progress(self, sprint_id: str) -> Dict[str, Any]:
        """Get progress summary for a sprint."""
        sprint = self.sprints.get(sprint_id)
        if not sprint:
            return {}

        tasks = [self.tasks[tid] for tid in sprint.task_ids if tid in self.tasks]
        total = len(tasks)
        done = sum(1 for t in tasks if t.status == TaskStatus.DONE)
        failed = sum(1 for t in tasks if t.status == TaskStatus.FAILED)

        return {
            "sprint": sprint.name,
            "total_tasks": total,
            "done": done,
            "failed": failed,
            "in_progress": total - done - failed,
            "progress_pct": (done / total * 100) if total > 0 else 0,
        }

    def to_markdown(self) -> str:
        """Render board state as markdown for agent consumption."""
        lines = [f"# Board: {self.project_name}", ""]

        for sprint in self.sprints.values():
            lines.extend([f"## Sprint: {sprint.name}", ""])
            progress = self.get_sprint_progress(sprint.id)
            lines.append(
                f"Progress: {progress.get('done', 0)}/{progress.get('total_tasks', 0)} "
                f"({progress.get('progress_pct', 0):.0f}%)"
            )
            lines.append("")

            for tid in sprint.task_ids:
                task = self.tasks.get(tid)
                if task:
                    status_icon = {
                        TaskStatus.DONE: "✅",
                        TaskStatus.IN_PROGRESS: "🔄",
                        TaskStatus.REVIEW: "👀",
                        TaskStatus.FAILED: "❌",
                        TaskStatus.RETRY: "🔁",
                        TaskStatus.TODO: "📋",
                        TaskStatus.BACKLOG: "📦",
                    }.get(task.status, "❓")
                    score = f" (score: {task.review_score:.2f})" if task.review_score else ""
                    lines.append(f"- {status_icon} **{task.title}** [{task.status.value}]{score}")

            lines.append("")

        if self.issues:
            lines.extend(["## Open Issues", ""])
            for issue in self.issues.values():
                if not issue.resolved:
                    lines.append(f"- [{issue.severity.value}] {issue.title}")
            lines.append("")

        return "\n".join(lines)

    def _save(self) -> None:
        """Persist board state to disk."""
        if not self.storage_path:
            return
        try:
            path = Path(self.storage_path)
            path.parent.mkdir(parents=True, exist_ok=True)
            with open(path, "w", encoding="utf-8") as f:
                json.dump(self.model_dump(), f, indent=2, default=str)
        except Exception as e:
            logger.error("Failed to save board: %s", e)

    @classmethod
    def load(cls, path: Path) -> "Board":
        """Load board from disk."""
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
        return cls.model_validate(data)
