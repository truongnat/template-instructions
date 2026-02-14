import pytest
from pathlib import Path
from agentic_sdlc.bridge.agent_bridge import AgentBridge, AgentResponse
from agentic_sdlc.bridge.formatters import AntigravityFormatter, GeminiFormatter, GenericFormatter
from agentic_sdlc.skills.skill import Skill, SkillRole, SkillSource, SkillMetadata
from agentic_sdlc.sdlc.board import TaskStatus

@pytest.fixture
def sample_skill():
    return Skill(
        name="test-skill",
        description="A test skill",
        role=SkillRole.DEVELOPER,
        category="general",
        tags=["test"],
        prompt_template="Do {{ task }}",
        workflow_steps=[],
        source=SkillSource.BUILTIN
    )

def test_agent_response_model():
    resp = AgentResponse(
        success=True,
        message="Test message",
        skill_instructions="# Instructions",
        prompt="Execute this",
        task_id="task-123"
    )
    assert resp.success is True
    assert resp.task_id == "task-123"
    assert "Instructions" in resp.skill_instructions

def test_antigravity_formatter(sample_skill):
    formatter = AntigravityFormatter()
    output = formatter.format_skill(sample_skill)
    assert "---" in output
    assert f"name: {sample_skill.name}" in output
    assert "# Skill: test-skill" in output
    assert "**Role**: developer" in output
    assert formatter.agent_name == "antigravity"

def test_gemini_formatter(sample_skill):
    formatter = GeminiFormatter()
    output = formatter.format_skill(sample_skill)
    assert f"TASK: {sample_skill.name}" in output
    assert f"ROLE: {sample_skill.role.value}" in output
    assert "STEPS:" in output
    assert formatter.agent_name == "gemini"

def test_generic_formatter(sample_skill):
    formatter = GenericFormatter()
    output = formatter.format_skill(sample_skill)
    assert "test-skill" in output
    assert formatter.agent_name == "generic"

def test_bridge_initialization(tmp_path):
    bridge = AgentBridge(project_dir=tmp_path)
    assert bridge._project_name == tmp_path.name
    assert (tmp_path / ".agentic_sdlc").exists()

def test_bridge_search_skills(tmp_path):
    bridge = AgentBridge(project_dir=tmp_path)
    # Should find builtin skills
    results = bridge.search_skills("requirement")
    assert len(results) > 0
    assert "requirement-analysis" in results[0]["name"]

def test_bridge_process_request(tmp_path):
    bridge = AgentBridge(project_dir=tmp_path)
    resp = bridge.process_request("Analyze requirements for a webapp")
    assert resp.success is True
    assert resp.task_id is not None
    assert "analyst" in resp.metadata["role"]
    assert "requirement-analysis" in resp.metadata["skill_name"]

def test_bridge_get_board(tmp_path):
    bridge = AgentBridge(project_dir=tmp_path)
    bridge.process_request("Test task")
    board_md = bridge.get_board()
    assert "# Board:" in board_md
    assert "Test task" in board_md
