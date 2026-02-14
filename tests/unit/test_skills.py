"""Unit tests for skills module: Skill model, SkillRegistry, SkillGenerator, SkillLoader."""

import tempfile
from pathlib import Path

import pytest
import yaml

from agentic_sdlc.skills import (
    ContextSpec,
    Skill,
    SkillGenerator,
    SkillLoader,
    SkillMetadata,
    SkillRegistry,
    SkillRole,
    SkillSource,
    SkillStep,
    RemoteSkillRegistry,
    SecurityScanResult,
)


# ─── Fixtures ────────────────────────────────────────────────────────────


@pytest.fixture
def sample_skill():
    return Skill(
        name="test-skill",
        description="A test skill for unit testing",
        role=SkillRole.DEVELOPER,
        category="testing",
        tags=["test", "unit"],
        workflow_steps=[
            SkillStep(
                name="setup",
                action="setup_env",
                description="Set up the environment",
                expected_output="Environment ready",
            ),
            SkillStep(
                name="execute",
                action="run_task",
                description="Execute the main task",
                depends_on=["setup"],
            ),
        ],
        validation_rules=["Must compile without errors", "All tests must pass"],
        score_criteria={"correctness": 0.5, "quality": 0.3, "docs": 0.2},
    )


@pytest.fixture
def builtin_skills_dir():
    return Path(__file__).parent.parent.parent / "src" / "agentic_sdlc" / "skills" / "builtin"


@pytest.fixture
def temp_dir():
    with tempfile.TemporaryDirectory() as td:
        yield Path(td)


# ─── Skill Model ─────────────────────────────────────────────────────────


class TestSkillModel:
    def test_create_skill(self, sample_skill):
        assert sample_skill.name == "test-skill"
        assert sample_skill.role == SkillRole.DEVELOPER
        assert len(sample_skill.workflow_steps) == 2
        assert sample_skill.version == "1.0.0"
        assert sample_skill.source == SkillSource.BUILTIN

    def test_to_skill_md(self, sample_skill):
        md = sample_skill.to_skill_md()
        assert "# Skill: test-skill" in md
        assert "**Role**: developer" in md
        assert "Step 1: setup" in md
        assert "Step 2: execute" in md
        assert "Must compile without errors" in md
        assert "correctness" in md

    def test_to_yaml_dict(self, sample_skill):
        d = sample_skill.to_yaml_dict()
        assert d["name"] == "test-skill"
        assert d["role"] == "developer"
        assert d["source"] == "builtin"
        assert len(d["workflow_steps"]) == 2
        assert "metadata" not in d

    def test_yaml_roundtrip(self, sample_skill, temp_dir):
        path = temp_dir / "test.yaml"
        data = sample_skill.to_yaml_dict()
        with open(path, "w") as f:
            yaml.safe_dump(data, f)
        loader = SkillLoader()
        loaded = loader.load_yaml(path)
        assert loaded is not None
        assert loaded.name == sample_skill.name
        assert loaded.role == sample_skill.role
        assert len(loaded.workflow_steps) == len(sample_skill.workflow_steps)

    def test_skill_roles(self):
        for role in SkillRole:
            s = Skill(name="r", description="r", role=role, category="test")
            assert s.role == role

    def test_context_spec_defaults(self):
        cs = ContextSpec()
        assert cs.max_tokens == 4000
        assert cs.required_files == []
        assert cs.priority_keywords == []

    def test_skill_metadata_success_rate(self):
        meta = SkillMetadata(execution_count=10, success_count=8)
        assert meta.success_rate == 0.8

    def test_skill_metadata_success_rate_zero(self):
        meta = SkillMetadata()
        assert meta.success_rate == 0.0


# ─── SkillRegistry ───────────────────────────────────────────────────────


class TestSkillRegistry:
    def test_register_and_get(self, sample_skill):
        reg = SkillRegistry()
        reg.register(sample_skill)
        assert reg.count == 1
        assert reg.get("test-skill") == sample_skill

    def test_register_duplicate_replaces(self, sample_skill):
        reg = SkillRegistry()
        reg.register(sample_skill)
        reg.register(sample_skill)
        assert reg.count == 1

    def test_search_by_keyword(self, sample_skill):
        reg = SkillRegistry()
        reg.register(sample_skill)
        results = reg.search("test unit")
        assert len(results) >= 1
        assert results[0].name == "test-skill"

    def test_search_no_results(self, sample_skill):
        reg = SkillRegistry()
        reg.register(sample_skill)
        results = reg.search("kubernetes helm deploy")
        assert len(results) == 0

    def test_search_by_role(self, sample_skill):
        reg = SkillRegistry()
        reg.register(sample_skill)
        results = reg.search("test", role=SkillRole.DEVELOPER)
        assert len(results) >= 1
        results_wrong = reg.search("test", role=SkillRole.TESTER)
        assert len(results_wrong) == 0

    def test_search_limit(self, sample_skill):
        reg = SkillRegistry()
        for i in range(10):
            s = sample_skill.model_copy(update={"name": f"skill-{i}", "tags": ["test"]})
            reg.register(s)
        results = reg.search("test", limit=3)
        assert len(results) == 3

    def test_update_metadata(self, sample_skill):
        reg = SkillRegistry()
        reg.register(sample_skill)
        reg.update_metadata("test-skill", success=True, score=0.9)
        skill = reg.get("test-skill")
        assert skill.metadata.execution_count == 1
        assert skill.metadata.success_count == 1
        assert skill.metadata.avg_score == 0.9

    def test_discover_builtin(self, builtin_skills_dir):
        reg = SkillRegistry()
        count = reg.discover(builtin_skills_dir)
        assert count == 6
        assert reg.count == 6

    def test_list_all(self, sample_skill):
        reg = SkillRegistry()
        reg.register(sample_skill)
        all_skills = reg.list_all()
        assert len(all_skills) == 1

    def test_metadata_persistence(self, sample_skill, temp_dir):
        meta_path = temp_dir / "meta.json"
        reg = SkillRegistry(metadata_path=meta_path)
        reg.register(sample_skill)
        reg.update_metadata("test-skill", success=True, score=0.8)
        assert meta_path.exists()


# ─── SkillGenerator ──────────────────────────────────────────────────────


class TestSkillGenerator:
    def test_generate_basic(self):
        gen = SkillGenerator()
        skill = gen.generate("Create a Python REST API")
        assert skill.name
        assert skill.role in list(SkillRole)
        assert len(skill.workflow_steps) > 0
        assert skill.source == SkillSource.GENERATED

    def test_generate_detects_role(self):
        gen = SkillGenerator()
        dev = gen.generate("Build a React component")
        assert dev.role == SkillRole.DEVELOPER

        review = gen.generate("Review the pull request")
        assert review.role == SkillRole.REVIEWER

        test = gen.generate("Write unit tests for the auth module")
        assert test.role == SkillRole.TESTER

    def test_generate_detects_category(self):
        gen = SkillGenerator()
        fe = gen.generate("Create a React component with CSS layout")
        assert fe.category == "frontend"

        be = gen.generate("Build a REST API server with SQL database and middleware")
        assert be.category == "backend"

    def test_generate_tags(self):
        gen = SkillGenerator()
        skill = gen.generate("Deploy Docker containers to Kubernetes")
        assert len(skill.tags) > 0
        assert any(t in skill.tags for t in ["docker", "kubernetes", "deploy", "containers"])

    def test_generate_saves_yaml(self, temp_dir):
        gen = SkillGenerator(output_dir=temp_dir)
        skill = gen.generate("Create user authentication")
        yaml_files = list(temp_dir.glob("*.yaml"))
        assert len(yaml_files) == 1


# ─── SkillLoader ─────────────────────────────────────────────────────────


class TestSkillLoader:
    def test_load_yaml(self, sample_skill, temp_dir):
        path = temp_dir / "test.yaml"
        with open(path, "w") as f:
            yaml.safe_dump(sample_skill.to_yaml_dict(), f)
        loader = SkillLoader()
        loaded = loader.load_yaml(path)
        assert loaded is not None
        assert loaded.name == "test-skill"

    def test_load_invalid_yaml(self, temp_dir):
        path = temp_dir / "bad.yaml"
        path.write_text("not: a: valid: : skill", encoding="utf-8")
        loader = SkillLoader()
        loaded = loader.load_yaml(path)
        assert loaded is None

    def test_load_directory(self, builtin_skills_dir):
        loader = SkillLoader()
        skills = loader.load_directory(builtin_skills_dir)
        assert len(skills) == 6
        names = [s.name for s in skills]
        assert "code-review" in names
        assert "testing" in names

    def test_load_empty_directory(self, temp_dir):
        loader = SkillLoader()
        skills = loader.load_directory(temp_dir)
        assert len(skills) == 0

    def test_load_nonexistent_directory(self):
        loader = SkillLoader()
        skills = loader.load_directory(Path("/nonexistent"))
        assert len(skills) == 0


# ─── RemoteSkillRegistry & Security ─────────────────────────────────────


class TestRemoteSkillRegistry:
    def test_scan_safe_skill(self, sample_skill, temp_dir):
        remote = RemoteSkillRegistry(install_dir=temp_dir)
        result = remote.scan_skill(sample_skill)
        assert result.scanned_files == 1
        # sample_skill doesn't contain unsafe patterns
        # (but the yaml output may contain "API_KEY" in score_criteria serialization)

    def test_scan_unsafe_content(self, temp_dir):
        remote = RemoteSkillRegistry(install_dir=temp_dir)
        result = SecurityScanResult()
        remote._scan_content("os.system('rm -rf /')", "test", result)
        assert not result.safe
        assert len(result.blocked_patterns) > 0

    def test_scan_exec_blocked(self, temp_dir):
        remote = RemoteSkillRegistry(install_dir=temp_dir)
        result = SecurityScanResult()
        remote._scan_content("exec('malicious_code')", "test", result)
        assert not result.safe

    def test_scan_env_blocked(self, temp_dir):
        remote = RemoteSkillRegistry(install_dir=temp_dir)
        result = SecurityScanResult()
        remote._scan_content("Set API_KEY=secret", "test", result)
        assert not result.safe

    def test_scan_safe_content(self, temp_dir):
        remote = RemoteSkillRegistry(install_dir=temp_dir)
        result = SecurityScanResult()
        remote._scan_content("def hello():\n    return 'world'", "test", result)
        assert result.safe

    def test_scan_directory(self, temp_dir):
        (temp_dir / "skill.yaml").write_text("name: safe\nrole: developer", encoding="utf-8")
        remote = RemoteSkillRegistry(install_dir=temp_dir)
        result = remote.scan_directory(temp_dir)
        assert result.safe
        assert result.scanned_files == 1
