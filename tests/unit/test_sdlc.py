"""Unit tests for SDLC module: Board, Task, Issue, Sprint, SDLCTracker."""

import tempfile
from pathlib import Path

import pytest

from agentic_sdlc.sdlc import Board, Issue, Sprint, Task, TaskStatus, SDLCTracker
from agentic_sdlc.sdlc.board import IssueSeverity
from agentic_sdlc.skills import Skill, SkillRole, SkillStep


# ─── Fixtures ────────────────────────────────────────────────────────────


@pytest.fixture
def board():
    return Board(project_name="test-project")


@pytest.fixture
def temp_dir():
    with tempfile.TemporaryDirectory() as td:
        yield Path(td)


@pytest.fixture
def skills():
    return [
        Skill(
            name="requirement-analysis",
            description="Analyze requirements",
            role=SkillRole.ANALYST,
            category="general",
        ),
        Skill(
            name="code-implementation",
            description="Implement code",
            role=SkillRole.DEVELOPER,
            category="general",
        ),
    ]


# ─── Task Model ──────────────────────────────────────────────────────────


class TestTask:
    def test_create_task(self):
        task = Task(title="Build API")
        assert task.title == "Build API"
        assert task.status == TaskStatus.BACKLOG
        assert task.retry_count == 0
        assert task.id  # auto-generated

    def test_transition(self):
        task = Task(title="Test")
        old_ts = task.updated_at
        task.transition(TaskStatus.IN_PROGRESS)
        assert task.status == TaskStatus.IN_PROGRESS
        assert task.updated_at >= old_ts


# ─── Board ───────────────────────────────────────────────────────────────


class TestBoard:
    def test_create_sprint(self, board):
        sprint = board.create_sprint("Sprint 1", "First sprint")
        assert sprint.name == "Sprint 1"
        assert sprint.id in board.sprints

    def test_create_task(self, board):
        task = board.create_task("Build API", skill_ref="code-implementation")
        assert task.title == "Build API"
        assert task.skill_ref == "code-implementation"
        assert task.id in board.tasks

    def test_create_issue(self, board):
        issue = board.create_issue("Bug found", severity=IssueSeverity.CRITICAL)
        assert issue.title == "Bug found"
        assert issue.severity == IssueSeverity.CRITICAL

    def test_add_task_to_sprint(self, board):
        sprint = board.create_sprint("S1")
        task = board.create_task("T1")
        board.add_task_to_sprint(sprint.id, task.id)
        assert task.id in sprint.task_ids

    def test_update_task_status(self, board):
        task = board.create_task("T1")
        board.update_task_status(task.id, TaskStatus.IN_PROGRESS)
        assert board.tasks[task.id].status == TaskStatus.IN_PROGRESS

    def test_set_task_score(self, board):
        task = board.create_task("T1")
        board.set_task_score(task.id, 0.85)
        assert board.tasks[task.id].review_score == 0.85

    def test_get_tasks_by_status(self, board):
        board.create_task("T1")
        t2 = board.create_task("T2")
        board.update_task_status(t2.id, TaskStatus.DONE)
        done = board.get_tasks_by_status(TaskStatus.DONE)
        assert len(done) == 1
        assert done[0].id == t2.id

    def test_sprint_progress(self, board):
        sprint = board.create_sprint("S1")
        t1 = board.create_task("T1")
        t2 = board.create_task("T2")
        board.add_task_to_sprint(sprint.id, t1.id)
        board.add_task_to_sprint(sprint.id, t2.id)
        board.update_task_status(t1.id, TaskStatus.DONE)
        progress = board.get_sprint_progress(sprint.id)
        assert progress["total_tasks"] == 2
        assert progress["done"] == 1
        assert progress["progress_pct"] == 50.0

    def test_to_markdown(self, board):
        sprint = board.create_sprint("Sprint 1")
        task = board.create_task("Build API")
        board.add_task_to_sprint(sprint.id, task.id)
        board.update_task_status(task.id, TaskStatus.DONE)
        md = board.to_markdown()
        assert "# Board: test-project" in md
        assert "Sprint 1" in md
        assert "✅" in md

    def test_parent_subtask(self, board):
        parent = board.create_task("Parent")
        child = board.create_task("Child", parent_task=parent.id)
        assert child.id in board.tasks[parent.id].subtasks

    def test_persistence(self, temp_dir):
        path = str(temp_dir / "sdlc_board.json")
        board = Board(project_name="persist-test", storage_path=path)
        board.create_sprint("S1")
        board.create_task("T1")
        assert Path(path).exists()
        loaded = Board.load(Path(path))
        assert loaded.project_name == "persist-test"
        assert len(loaded.sprints) == 1
        assert len(loaded.tasks) == 1


# ─── SDLCTracker ─────────────────────────────────────────────────────────


class TestSDLCTracker:
    def test_plan_with_skills(self, skills):
        tracker = SDLCTracker("test-project")
        sprint = tracker.plan("Build a webapp", skills)
        assert len(sprint.task_ids) == 2
        assert sprint.name.startswith("Build a webapp")

    def test_plan_without_skills(self):
        tracker = SDLCTracker("test-project")
        sprint = tracker.plan("Some task")
        assert len(sprint.task_ids) == 1  # default analysis task

    def test_get_next_tasks(self, skills):
        tracker = SDLCTracker("test-project")
        tracker.plan("Build", skills)
        next_tasks = tracker.get_next_tasks()
        assert len(next_tasks) == 2

    def test_start_task(self, skills):
        tracker = SDLCTracker("test-project")
        tracker.plan("Build", skills)
        tasks = tracker.get_next_tasks()
        tracker.start_task(tasks[0].id)
        assert tracker.board.tasks[tasks[0].id].status == TaskStatus.IN_PROGRESS

    def test_submit_output_pass(self, skills):
        tracker = SDLCTracker("test-project")
        tracker.plan("Build", skills)
        tasks = tracker.get_next_tasks()
        tracker.start_task(tasks[0].id)
        result = tracker.submit_output(tasks[0].id, "/tmp/out.md", score=0.85)
        assert result.status == TaskStatus.DONE

    def test_submit_output_fail_retry(self, skills):
        tracker = SDLCTracker("test-project")
        tracker.plan("Build", skills)
        tasks = tracker.get_next_tasks()
        tracker.start_task(tasks[0].id)
        result = tracker.submit_output(tasks[0].id, "/tmp/out.md", score=0.3)
        assert result.status == TaskStatus.RETRY
        assert result.retry_count == 1

    def test_submit_output_max_retries(self, skills):
        tracker = SDLCTracker("test-project")
        tracker.plan("Build", skills)
        tasks = tracker.get_next_tasks()
        tid = tasks[0].id
        tracker.start_task(tid)
        for _ in range(3):
            tracker.submit_output(tid, "/tmp/out.md", score=0.2)
        assert tracker.board.tasks[tid].status == TaskStatus.FAILED
        # Should have created an issue
        assert len(tracker.board.issues) == 1

    def test_complete_sprint(self, skills):
        tracker = SDLCTracker("test-project")
        sprint = tracker.plan("Build", skills)
        progress = tracker.complete_sprint(sprint.id)
        assert "total_tasks" in progress

    def test_get_board_markdown(self, skills):
        tracker = SDLCTracker("test-project")
        tracker.plan("Build", skills)
        md = tracker.get_board_markdown()
        assert "# Board" in md

    def test_persistence(self, skills, temp_dir):
        tracker = SDLCTracker("persist-test", storage_dir=temp_dir)
        tracker.plan("Build", skills)
        assert (temp_dir / "sdlc_board.json").exists()
