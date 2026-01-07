"""
Task Board - Kanban-style task management.

Part of Layer 2: Intelligence Layer.
"""

import json
import uuid
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional


class TaskStatus(Enum):
    """Task status values."""
    BACKLOG = "backlog"
    TODO = "todo"
    IN_PROGRESS = "in_progress"
    REVIEW = "review"
    DONE = "done"
    BLOCKED = "blocked"


class TaskPriority(Enum):
    """Task priority levels."""
    CRITICAL = 1
    HIGH = 2
    MEDIUM = 3
    LOW = 4


@dataclass
class Task:
    """A single task."""
    id: str
    title: str
    description: str
    status: TaskStatus = TaskStatus.TODO
    priority: TaskPriority = TaskPriority.MEDIUM
    assignee: Optional[str] = None
    labels: List[str] = field(default_factory=list)
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())
    updated_at: str = field(default_factory=lambda: datetime.now().isoformat())
    due_date: Optional[str] = None
    parent_id: Optional[str] = None
    metadata: Dict = field(default_factory=dict)

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "title": self.title,
            "description": self.description,
            "status": self.status.value,
            "priority": self.priority.value,
            "assignee": self.assignee,
            "labels": self.labels,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
            "due_date": self.due_date,
            "parent_id": self.parent_id,
            "metadata": self.metadata
        }

    def update(self):
        """Update timestamp."""
        self.updated_at = datetime.now().isoformat()


class TaskBoard:
    """
    Kanban-style task management board.
    
    Features:
    - Create and manage tasks
    - Move tasks between columns (statuses)
    - Track progress
    - Filter and search tasks
    """

    def __init__(self, storage_file: Optional[Path] = None):
        self.storage_file = storage_file or Path(".brain-tasks.json")
        self.tasks: Dict[str, Task] = {}
        self.columns = list(TaskStatus)
        self._load_tasks()

    def _load_tasks(self):
        """Load tasks from storage."""
        if self.storage_file.exists():
            try:
                with open(self.storage_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    for t in data.get("tasks", []):
                        task = Task(
                            id=t["id"],
                            title=t["title"],
                            description=t["description"],
                            status=TaskStatus(t.get("status", "todo")),
                            priority=TaskPriority(t.get("priority", 3)),
                            assignee=t.get("assignee"),
                            labels=t.get("labels", []),
                            created_at=t.get("created_at"),
                            updated_at=t.get("updated_at"),
                            due_date=t.get("due_date"),
                            parent_id=t.get("parent_id"),
                            metadata=t.get("metadata", {})
                        )
                        self.tasks[task.id] = task
            except (json.JSONDecodeError, IOError):
                pass

    def _save_tasks(self):
        """Save tasks to storage."""
        data = {
            "tasks": [t.to_dict() for t in self.tasks.values()],
            "updated_at": datetime.now().isoformat()
        }
        with open(self.storage_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

    def create_task(
        self,
        title: str,
        description: str = "",
        priority: TaskPriority = TaskPriority.MEDIUM,
        assignee: Optional[str] = None,
        labels: Optional[List[str]] = None
    ) -> Task:
        """Create a new task."""
        task_id = f"TASK-{uuid.uuid4().hex[:8].upper()}"
        
        task = Task(
            id=task_id,
            title=title,
            description=description,
            priority=priority,
            assignee=assignee,
            labels=labels or []
        )
        
        self.tasks[task_id] = task
        self._save_tasks()
        return task

    def get_task(self, task_id: str) -> Optional[Task]:
        """Get a task by ID."""
        return self.tasks.get(task_id)

    def update_task(self, task_id: str, **updates) -> Optional[Task]:
        """Update a task."""
        task = self.tasks.get(task_id)
        if not task:
            return None
        
        for key, value in updates.items():
            if hasattr(task, key):
                if key == "status" and isinstance(value, str):
                    value = TaskStatus(value)
                elif key == "priority" and isinstance(value, int):
                    value = TaskPriority(value)
                setattr(task, key, value)
        
        task.update()
        self._save_tasks()
        return task

    def move_task(self, task_id: str, new_status: TaskStatus) -> Optional[Task]:
        """Move a task to a new status."""
        return self.update_task(task_id, status=new_status)

    def delete_task(self, task_id: str) -> bool:
        """Delete a task."""
        if task_id in self.tasks:
            del self.tasks[task_id]
            self._save_tasks()
            return True
        return False

    def list_tasks(
        self,
        status: Optional[TaskStatus] = None,
        assignee: Optional[str] = None,
        labels: Optional[List[str]] = None,
        priority: Optional[TaskPriority] = None
    ) -> List[Task]:
        """List tasks with optional filters."""
        tasks = list(self.tasks.values())
        
        if status:
            tasks = [t for t in tasks if t.status == status]
        
        if assignee:
            tasks = [t for t in tasks if t.assignee == assignee]
        
        if labels:
            tasks = [t for t in tasks if any(l in t.labels for l in labels)]
        
        if priority:
            tasks = [t for t in tasks if t.priority == priority]
        
        # Sort by priority then created date
        tasks.sort(key=lambda t: (t.priority.value, t.created_at))
        return tasks

    def get_board(self) -> Dict[str, List[Task]]:
        """Get the full board organized by columns."""
        board = {status.value: [] for status in TaskStatus}
        
        for task in self.tasks.values():
            board[task.status.value].append(task)
        
        # Sort each column
        for status in board:
            board[status].sort(key=lambda t: (t.priority.value, t.created_at))
        
        return board

    def get_stats(self) -> Dict:
        """Get board statistics."""
        total = len(self.tasks)
        by_status = {}
        by_priority = {}
        
        for task in self.tasks.values():
            s = task.status.value
            p = task.priority.name.lower()
            by_status[s] = by_status.get(s, 0) + 1
            by_priority[p] = by_priority.get(p, 0) + 1
        
        done = by_status.get("done", 0)
        in_progress = by_status.get("in_progress", 0)
        
        return {
            "total": total,
            "done": done,
            "in_progress": in_progress,
            "progress_percent": round(done / total * 100, 1) if total > 0 else 0,
            "by_status": by_status,
            "by_priority": by_priority
        }


def main():
    """CLI entry point."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Task Board - Layer 2 Intelligence")
    parser.add_argument("--create", type=str, help="Create new task with title")
    parser.add_argument("--list", action="store_true", help="List all tasks")
    parser.add_argument("--status", type=str, help="Filter by status")
    parser.add_argument("--move", nargs=2, metavar=("TASK_ID", "STATUS"), help="Move task")
    parser.add_argument("--board", action="store_true", help="Show full board")
    parser.add_argument("--stats", action="store_true", help="Show statistics")
    
    args = parser.parse_args()
    board = TaskBoard()
    
    if args.create:
        task = board.create_task(args.create)
        print(f"✅ Created: {task.id} - {task.title}")
    
    elif args.list:
        status = TaskStatus(args.status) if args.status else None
        for task in board.list_tasks(status=status):
            print(f"[{task.status.value}] {task.id}: {task.title}")
    
    elif args.move:
        task_id, new_status = args.move
        task = board.move_task(task_id, TaskStatus(new_status))
        if task:
            print(f"✅ Moved {task_id} to {new_status}")
        else:
            print(f"❌ Task not found: {task_id}")
    
    elif args.board:
        b = board.get_board()
        for status, tasks in b.items():
            print(f"\n📋 {status.upper()} ({len(tasks)})")
            for task in tasks[:5]:
                print(f"   • {task.id}: {task.title}")
    
    elif args.stats:
        print(json.dumps(board.get_stats(), indent=2))
    
    else:
        parser.print_help()


if __name__ == "__main__":
    main()

