"""
Sprint Manager - Sprint planning and tracking.

Part of Layer 2: Intelligence Layer.
"""

import json
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional


@dataclass
class Sprint:
    """A sprint/iteration."""
    id: str
    name: str
    goal: str
    start_date: str
    end_date: str
    task_ids: List[str] = field(default_factory=list)
    status: str = "planning"  # planning, active, completed
    velocity: int = 0
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "name": self.name,
            "goal": self.goal,
            "start_date": self.start_date,
            "end_date": self.end_date,
            "task_ids": self.task_ids,
            "status": self.status,
            "velocity": self.velocity,
            "created_at": self.created_at
        }


class SprintManager:
    """
    Sprint planning and tracking.
    
    Features:
    - Create and manage sprints
    - Track sprint progress
    - Calculate velocity
    - Generate sprint reports
    """

    def __init__(self, storage_file: Optional[Path] = None):
        self.storage_file = storage_file or Path(".brain-sprints.json")
        self.sprints: Dict[str, Sprint] = {}
        self._load_sprints()

    def _load_sprints(self):
        """Load sprints from storage."""
        if self.storage_file.exists():
            try:
                with open(self.storage_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    for s in data.get("sprints", []):
                        sprint = Sprint(**s)
                        self.sprints[sprint.id] = sprint
            except (json.JSONDecodeError, IOError):
                pass

    def _save_sprints(self):
        """Save sprints to storage."""
        data = {
            "sprints": [s.to_dict() for s in self.sprints.values()],
            "updated_at": datetime.now().isoformat()
        }
        with open(self.storage_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

    def create_sprint(
        self,
        name: str,
        goal: str,
        duration_days: int = 14,
        start_date: Optional[str] = None
    ) -> Sprint:
        """Create a new sprint."""
        sprint_num = len(self.sprints) + 1
        sprint_id = f"SPRINT-{sprint_num:03d}"
        
        if start_date:
            start = datetime.fromisoformat(start_date)
        else:
            start = datetime.now()
        
        end = start + timedelta(days=duration_days)
        
        sprint = Sprint(
            id=sprint_id,
            name=name,
            goal=goal,
            start_date=start.strftime("%Y-%m-%d"),
            end_date=end.strftime("%Y-%m-%d")
        )
        
        self.sprints[sprint_id] = sprint
        self._save_sprints()
        return sprint

    def get_sprint(self, sprint_id: str) -> Optional[Sprint]:
        """Get a sprint by ID."""
        return self.sprints.get(sprint_id)

    def get_active_sprint(self) -> Optional[Sprint]:
        """Get the currently active sprint."""
        for sprint in self.sprints.values():
            if sprint.status == "active":
                return sprint
        return None

    def start_sprint(self, sprint_id: str) -> Optional[Sprint]:
        """Start a sprint."""
        sprint = self.sprints.get(sprint_id)
        if sprint:
            sprint.status = "active"
            sprint.start_date = datetime.now().strftime("%Y-%m-%d")
            self._save_sprints()
        return sprint

    def complete_sprint(self, sprint_id: str, velocity: int = 0) -> Optional[Sprint]:
        """Complete a sprint."""
        sprint = self.sprints.get(sprint_id)
        if sprint:
            sprint.status = "completed"
            sprint.velocity = velocity
            self._save_sprints()
        return sprint

    def add_task_to_sprint(self, sprint_id: str, task_id: str):
        """Add a task to a sprint."""
        sprint = self.sprints.get(sprint_id)
        if sprint and task_id not in sprint.task_ids:
            sprint.task_ids.append(task_id)
            self._save_sprints()

    def remove_task_from_sprint(self, sprint_id: str, task_id: str):
        """Remove a task from a sprint."""
        sprint = self.sprints.get(sprint_id)
        if sprint and task_id in sprint.task_ids:
            sprint.task_ids.remove(task_id)
            self._save_sprints()

    def get_sprint_progress(self, sprint_id: str, task_board=None) -> Dict:
        """Get sprint progress."""
        sprint = self.sprints.get(sprint_id)
        if not sprint:
            return {}
        
        total = len(sprint.task_ids)
        completed = 0
        
        if task_board:
            for task_id in sprint.task_ids:
                task = task_board.get_task(task_id)
                if task and task.status.value == "done":
                    completed += 1
        
        days_total = (datetime.fromisoformat(sprint.end_date) - 
                     datetime.fromisoformat(sprint.start_date)).days
        days_elapsed = (datetime.now() - datetime.fromisoformat(sprint.start_date)).days
        
        return {
            "sprint_id": sprint_id,
            "name": sprint.name,
            "status": sprint.status,
            "total_tasks": total,
            "completed_tasks": completed,
            "completion_percent": round(completed / total * 100, 1) if total > 0 else 0,
            "days_total": days_total,
            "days_elapsed": min(days_elapsed, days_total),
            "days_remaining": max(days_total - days_elapsed, 0)
        }

    def list_sprints(self, status: Optional[str] = None) -> List[Sprint]:
        """List sprints."""
        sprints = list(self.sprints.values())
        if status:
            sprints = [s for s in sprints if s.status == status]
        return sorted(sprints, key=lambda s: s.created_at, reverse=True)

    def get_average_velocity(self, last_n: int = 3) -> float:
        """Calculate average velocity from completed sprints."""
        completed = [s for s in self.sprints.values() if s.status == "completed"]
        completed.sort(key=lambda s: s.created_at, reverse=True)
        
        velocities = [s.velocity for s in completed[:last_n] if s.velocity > 0]
        return sum(velocities) / len(velocities) if velocities else 0


def main():
    """CLI entry point."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Sprint Manager")
    parser.add_argument("--create", type=str, help="Create sprint with name")
    parser.add_argument("--goal", type=str, help="Sprint goal")
    parser.add_argument("--list", action="store_true", help="List sprints")
    parser.add_argument("--active", action="store_true", help="Show active sprint")
    parser.add_argument("--start", type=str, help="Start sprint by ID")
    parser.add_argument("--complete", type=str, help="Complete sprint by ID")
    
    args = parser.parse_args()
    manager = SprintManager()
    
    if args.create:
        sprint = manager.create_sprint(
            name=args.create,
            goal=args.goal or "Sprint goal"
        )
        print(f"✅ Created: {sprint.id} - {sprint.name}")
    
    elif args.list:
        for s in manager.list_sprints():
            print(f"[{s.status}] {s.id}: {s.name} ({s.start_date} - {s.end_date})")
    
    elif args.active:
        sprint = manager.get_active_sprint()
        if sprint:
            print(f"Active: {sprint.id} - {sprint.name}")
            print(f"Goal: {sprint.goal}")
            print(f"Period: {sprint.start_date} - {sprint.end_date}")
        else:
            print("No active sprint")
    
    elif args.start:
        sprint = manager.start_sprint(args.start)
        if sprint:
            print(f"✅ Started: {sprint.id}")
    
    elif args.complete:
        sprint = manager.complete_sprint(args.complete)
        if sprint:
            print(f"✅ Completed: {sprint.id}")
    
    else:
        parser.print_help()


if __name__ == "__main__":
    main()

