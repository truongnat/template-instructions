"""Unit tests for test fixtures and factories.

This module tests the factory functions and mock data generators to ensure
they create valid test data.
"""

import pytest
from tests.fixtures import (
    WorkflowFactory,
    AgentFactory,
    ConfigFactory,
    RuleFactory,
    SkillFactory,
    TaskFactory,
    MockDataGenerator,
    SAMPLE_WORKFLOW,
    SAMPLE_AGENT,
    COMPLEX_WORKFLOW,
    AGENT_POOL
)


class TestWorkflowFactory:
    """Tests for WorkflowFactory."""
    
    def test_create_basic_workflow(self):
        """Test creating a basic workflow."""
        workflow = WorkflowFactory.create_basic_workflow()
        
        assert workflow["name"] == "test-workflow"
        assert workflow["version"] == "1.0.0"
        assert "description" in workflow
        assert "agents" in workflow
        assert "tasks" in workflow
        assert "timeout" in workflow
    
    def test_create_basic_workflow_with_overrides(self):
        """Test creating a basic workflow with overrides."""
        workflow = WorkflowFactory.create_basic_workflow(
            name="custom-workflow",
            timeout=7200
        )
        
        assert workflow["name"] == "custom-workflow"
        assert workflow["timeout"] == 7200
    
    def test_create_workflow_with_tasks(self):
        """Test creating a workflow with tasks."""
        workflow = WorkflowFactory.create_workflow_with_tasks(num_tasks=5)
        
        assert len(workflow["tasks"]) == 5
        assert all("id" in task for task in workflow["tasks"])
        assert all("type" in task for task in workflow["tasks"])
    
    def test_create_workflow_with_agents(self):
        """Test creating a workflow with agents."""
        workflow = WorkflowFactory.create_workflow_with_agents(num_agents=3)
        
        assert len(workflow["agents"]) == 3
        assert all(agent.startswith("agent-") for agent in workflow["agents"])
    
    def test_create_complex_workflow(self):
        """Test creating a complex workflow."""
        workflow = WorkflowFactory.create_complex_workflow()
        
        assert workflow["name"] == "complex-workflow"
        assert len(workflow["agents"]) == 3
        assert len(workflow["tasks"]) == 3
        assert "retry_policy" in workflow
        assert workflow["tasks"][1]["dependencies"] == ["task-1"]
    
    def test_create_minimal_workflow(self):
        """Test creating a minimal workflow."""
        workflow = WorkflowFactory.create_minimal_workflow()
        
        assert "name" in workflow
        assert "version" in workflow
        assert len(workflow) == 2  # Only required fields


class TestAgentFactory:
    """Tests for AgentFactory."""
    
    def test_create_agent(self):
        """Test creating a basic agent."""
        agent = AgentFactory.create_agent()
        
        assert agent["id"] == "test-agent"
        assert agent["type"] == "ba"
        assert "capabilities" in agent
        assert "model" in agent
        assert "config" in agent
    
    def test_create_agent_with_type(self):
        """Test creating an agent with specific type."""
        agent = AgentFactory.create_agent(agent_type="pm")
        
        assert agent["type"] == "pm"
    
    def test_create_agent_pool(self):
        """Test creating an agent pool."""
        agents = AgentFactory.create_agent_pool(num_agents=5)
        
        assert len(agents) == 5
        assert all("id" in agent for agent in agents)
        assert all("type" in agent for agent in agents)
    
    def test_create_ba_agent(self):
        """Test creating a BA agent."""
        agent = AgentFactory.create_ba_agent()
        
        assert agent["type"] == "ba"
        assert "requirements_analysis" in agent["capabilities"]
    
    def test_create_pm_agent(self):
        """Test creating a PM agent."""
        agent = AgentFactory.create_pm_agent()
        
        assert agent["type"] == "pm"
        assert "planning" in agent["capabilities"]
    
    def test_create_sa_agent(self):
        """Test creating a SA agent."""
        agent = AgentFactory.create_sa_agent()
        
        assert agent["type"] == "sa"
        assert "architecture_design" in agent["capabilities"]
    
    def test_create_implementation_agent(self):
        """Test creating an implementation agent."""
        agent = AgentFactory.create_implementation_agent()
        
        assert agent["type"] == "implementation"
        assert "coding" in agent["capabilities"]


class TestConfigFactory:
    """Tests for ConfigFactory."""
    
    def test_create_config(self):
        """Test creating a basic config."""
        config = ConfigFactory.create_config()
        
        assert "core" in config
        assert "agents" in config
        assert "workflows" in config
    
    def test_create_development_config(self):
        """Test creating a development config."""
        config = ConfigFactory.create_development_config()
        
        assert config["core"]["environment"] == "development"
        assert config["core"]["debug"] is True
        assert config["core"]["log_level"] == "DEBUG"
    
    def test_create_production_config(self):
        """Test creating a production config."""
        config = ConfigFactory.create_production_config()
        
        assert config["core"]["environment"] == "production"
        assert config["core"]["debug"] is False
        assert "security" in config
    
    def test_create_test_config(self):
        """Test creating a test config."""
        config = ConfigFactory.create_test_config()
        
        assert config["core"]["environment"] == "test"
        assert config["monitoring"]["enabled"] is False


class TestTaskFactory:
    """Tests for TaskFactory."""
    
    def test_create_task(self):
        """Test creating a basic task."""
        task = TaskFactory.create_task()
        
        assert task["id"] == "test-task"
        assert task["type"] == "analysis"
        assert "config" in task
        assert "dependencies" in task
    
    def test_create_task_with_type(self):
        """Test creating a task with specific type."""
        task = TaskFactory.create_task(task_type="implementation")
        
        assert task["type"] == "implementation"
    
    def test_create_task_chain(self):
        """Test creating a task chain."""
        tasks = TaskFactory.create_task_chain(num_tasks=4)
        
        assert len(tasks) == 4
        assert tasks[0]["dependencies"] == []
        assert tasks[1]["dependencies"] == ["task-1"]
        assert tasks[2]["dependencies"] == ["task-2"]
        assert tasks[3]["dependencies"] == ["task-3"]
    
    def test_create_parallel_tasks(self):
        """Test creating parallel tasks."""
        tasks = TaskFactory.create_parallel_tasks(num_tasks=3)
        
        assert len(tasks) == 3
        assert all(task["dependencies"] == [] for task in tasks)


class TestMockDataGenerator:
    """Tests for MockDataGenerator."""
    
    def test_random_string(self):
        """Test generating random strings."""
        s1 = MockDataGenerator.random_string(length=10)
        s2 = MockDataGenerator.random_string(length=10)
        
        assert len(s1) == 10
        assert len(s2) == 10
        assert s1 != s2  # Should be different
    
    def test_random_string_with_prefix(self):
        """Test generating random strings with prefix."""
        s = MockDataGenerator.random_string(length=8, prefix="test-")
        
        assert s.startswith("test-")
        assert len(s) == 13  # 5 (prefix) + 8 (random)
    
    def test_random_id(self):
        """Test generating random IDs."""
        id1 = MockDataGenerator.random_id()
        id2 = MockDataGenerator.random_id()
        
        assert id1.startswith("id-")
        assert id2.startswith("id-")
        assert id1 != id2
    
    def test_random_version(self):
        """Test generating random versions."""
        version = MockDataGenerator.random_version()
        
        parts = version.split(".")
        assert len(parts) == 3
        assert all(part.isdigit() for part in parts)
    
    def test_random_timestamp(self):
        """Test generating random timestamps."""
        timestamp = MockDataGenerator.random_timestamp()
        
        assert "T" in timestamp  # ISO format
        assert len(timestamp) > 0
    
    def test_random_workflow(self):
        """Test generating random workflows."""
        workflow = MockDataGenerator.random_workflow()
        
        assert "name" in workflow
        assert "version" in workflow
        assert "agents" in workflow
        assert "tasks" in workflow
        assert len(workflow["agents"]) >= 1
        assert len(workflow["tasks"]) >= 1
    
    def test_random_agent(self):
        """Test generating random agents."""
        agent = MockDataGenerator.random_agent()
        
        assert "id" in agent
        assert "type" in agent
        assert "capabilities" in agent
        assert "model" in agent
        assert agent["type"] in ["ba", "pm", "sa", "implementation", "research", "quality_judge"]
    
    def test_random_config(self):
        """Test generating random configs."""
        config = MockDataGenerator.random_config()
        
        assert "core" in config
        assert "agents" in config
        assert "workflows" in config
        assert config["core"]["log_level"] in ["DEBUG", "INFO", "WARNING", "ERROR"]
    
    def test_random_task(self):
        """Test generating random tasks."""
        task = MockDataGenerator.random_task()
        
        assert "id" in task
        assert "type" in task
        assert "config" in task
        assert task["type"] in ["analysis", "implementation", "validation", "testing", "deployment"]
    
    def test_random_api_response_success(self):
        """Test generating random success API responses."""
        response = MockDataGenerator.random_api_response(success=True)
        
        assert response["status"] == "success"
        assert "data" in response
        assert "id" in response["data"]
    
    def test_random_api_response_error(self):
        """Test generating random error API responses."""
        response = MockDataGenerator.random_api_response(success=False)
        
        assert response["status"] == "error"
        assert "error" in response
        assert "code" in response["error"]
        assert "message" in response["error"]


class TestMockData:
    """Tests for mock data constants."""
    
    def test_sample_workflow(self):
        """Test SAMPLE_WORKFLOW is valid."""
        assert SAMPLE_WORKFLOW["name"] == "test-workflow"
        assert SAMPLE_WORKFLOW["version"] == "1.0.0"
        assert len(SAMPLE_WORKFLOW["agents"]) == 2
        assert len(SAMPLE_WORKFLOW["tasks"]) == 1
    
    def test_sample_agent(self):
        """Test SAMPLE_AGENT is valid."""
        assert SAMPLE_AGENT["id"] == "test-agent"
        assert SAMPLE_AGENT["type"] == "ba"
        assert len(SAMPLE_AGENT["capabilities"]) == 2
    
    def test_complex_workflow(self):
        """Test COMPLEX_WORKFLOW is valid."""
        assert COMPLEX_WORKFLOW["name"] == "complex-workflow"
        assert len(COMPLEX_WORKFLOW["agents"]) == 4
        assert len(COMPLEX_WORKFLOW["tasks"]) == 4
        assert "retry_policy" in COMPLEX_WORKFLOW
    
    def test_agent_pool(self):
        """Test AGENT_POOL is valid."""
        assert len(AGENT_POOL) == 4
        assert all("id" in agent for agent in AGENT_POOL)
        assert all("type" in agent for agent in AGENT_POOL)
        
        # Check all agent types are present
        types = [agent["type"] for agent in AGENT_POOL]
        assert "ba" in types
        assert "pm" in types
        assert "sa" in types
        assert "implementation" in types


class TestFactoryIntegration:
    """Integration tests for factories working together."""
    
    def test_create_workflow_with_factory_agents(self):
        """Test creating a workflow using factory-generated agents."""
        agents = AgentFactory.create_agent_pool(num_agents=3)
        agent_ids = [agent["id"] for agent in agents]
        
        workflow = WorkflowFactory.create_basic_workflow(agents=agent_ids)
        
        assert len(workflow["agents"]) == 3
        assert workflow["agents"] == agent_ids
    
    def test_create_workflow_with_factory_tasks(self):
        """Test creating a workflow using factory-generated tasks."""
        tasks = TaskFactory.create_task_chain(num_tasks=3)
        
        workflow = WorkflowFactory.create_basic_workflow(tasks=tasks)
        
        assert len(workflow["tasks"]) == 3
        assert workflow["tasks"][1]["dependencies"] == ["task-1"]
    
    def test_create_complete_workflow_system(self):
        """Test creating a complete workflow system with all components."""
        # Create agents
        agents = AgentFactory.create_agent_pool(num_agents=3)
        agent_ids = [agent["id"] for agent in agents]
        
        # Create tasks
        tasks = TaskFactory.create_task_chain(num_tasks=4)
        
        # Create workflow
        workflow = WorkflowFactory.create_basic_workflow(
            name="integration-test-workflow",
            agents=agent_ids,
            tasks=tasks
        )
        
        # Create config
        config = ConfigFactory.create_test_config()
        
        # Verify everything is connected
        assert workflow["name"] == "integration-test-workflow"
        assert len(workflow["agents"]) == 3
        assert len(workflow["tasks"]) == 4
        assert config["core"]["environment"] == "test"
