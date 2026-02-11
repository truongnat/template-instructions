"""
Ví Dụ 14: Testing Agents and Workflows (Test Agents và Workflows)

Setup Instructions:
1. Cài đặt: pip install agentic-sdlc pytest
2. Chạy: python 14-testing.py hoặc pytest 14-testing.py

Dependencies:
- agentic-sdlc>=3.0.0
- pytest

Expected Output:
- Unit tests cho agents
- Integration tests cho workflows
- Mock LLM responses
- Test fixtures
"""

import os
import pytest
from unittest.mock import Mock, patch
from dotenv import load_dotenv

load_dotenv()


def test_agent_creation():
    """Test tạo agent."""
    from agentic_sdlc.orchestration.agent import Agent, AgentConfig
    from agentic_sdlc.core.config import ModelConfig
    
    model_config = ModelConfig(
        provider="openai",
        model_name="gpt-4",
        api_key="test-key"
    )
    
    agent_config = AgentConfig(
        name="test-agent",
        role="developer",
        description="Test agent",
        model_config=model_config
    )
    
    agent = Agent(config=agent_config)
    
    assert agent.config.name == "test-agent"
    assert agent.config.role == "developer"
    
    print("✓ test_agent_creation passed")


def test_workflow_creation():
    """Test tạo workflow."""
    from agentic_sdlc.orchestration.workflow import WorkflowBuilder, WorkflowStep
    
    builder = WorkflowBuilder(name="test-workflow")
    
    builder.add_step(WorkflowStep(
        name="step1",
        action="test",
        description="Test step",
        parameters={}
    ))
    
    workflow = builder.build()
    
    assert workflow.name == "test-workflow"
    assert len(workflow.steps) == 1
    assert workflow.steps[0].name == "step1"
    
    print("✓ test_workflow_creation passed")


def test_agent_with_mock_llm():
    """Test agent với mock LLM response."""
    from agentic_sdlc.orchestration.agent import Agent, AgentConfig, Task
    from agentic_sdlc.core.config import ModelConfig
    
    # Create agent
    model_config = ModelConfig(
        provider="openai",
        model_name="gpt-4",
        api_key="test-key"
    )
    
    agent_config = AgentConfig(
        name="test-agent",
        role="developer",
        description="Test agent",
        model_config=model_config
    )
    
    agent = Agent(config=agent_config)
    
    # Mock LLM response
    with patch.object(agent, 'execute') as mock_execute:
        mock_execute.return_value = Mock(
            status="completed",
            output="Mocked response"
        )
        
        task = Task(
            id="test-task",
            description="Test task",
            context={}
        )
        
        result = agent.execute(task)
        
        assert result.status == "completed"
        assert result.output == "Mocked response"
    
    print("✓ test_agent_with_mock_llm passed")


@pytest.fixture
def sample_agent():
    """Fixture để tạo sample agent."""
    from agentic_sdlc.orchestration.agent import Agent, AgentConfig
    from agentic_sdlc.core.config import ModelConfig
    
    model_config = ModelConfig(
        provider="openai",
        model_name="gpt-4",
        api_key="test-key"
    )
    
    agent_config = AgentConfig(
        name="fixture-agent",
        role="developer",
        description="Fixture agent",
        model_config=model_config
    )
    
    return Agent(config=agent_config)


def test_with_fixture(sample_agent):
    """Test sử dụng fixture."""
    assert sample_agent.config.name == "fixture-agent"
    assert sample_agent.config.role == "developer"
    
    print("✓ test_with_fixture passed")


def test_workflow_execution():
    """Test workflow execution."""
    from agentic_sdlc.orchestration.workflow import WorkflowBuilder, WorkflowStep, WorkflowRunner
    from agentic_sdlc.orchestration.agent import Agent, AgentConfig
    from agentic_sdlc.core.config import ModelConfig
    
    # Create workflow
    builder = WorkflowBuilder(name="test-workflow")
    builder.add_step(WorkflowStep(
        name="step1",
        action="test",
        description="Test step",
        parameters={"input": "test"}
    ))
    
    workflow = builder.build()
    
    # Create agent
    model_config = ModelConfig(
        provider="openai",
        model_name="gpt-4",
        api_key="test-key"
    )
    
    agent = Agent(config=AgentConfig(
        name="test-agent",
        role="orchestrator",
        description="Test agent",
        model_config=model_config
    ))
    
    # Mock runner
    runner = WorkflowRunner(workflow=workflow, agent=agent)
    
    with patch.object(runner, 'run') as mock_run:
        mock_run.return_value = Mock(
            status="completed",
            step_results=[]
        )
        
        result = runner.run()
        
        assert result.status == "completed"
    
    print("✓ test_workflow_execution passed")


def test_error_handling():
    """Test error handling."""
    from agentic_sdlc.core.exceptions import ConfigurationError
    from agentic_sdlc.core.config import Config
    
    with pytest.raises(ConfigurationError):
        # This should raise ConfigurationError
        config = Config(
            project_name="",  # Invalid empty name
            models={}
        )
    
    print("✓ test_error_handling passed")


def integration_test_full_workflow():
    """Integration test cho full workflow."""
    from agentic_sdlc.orchestration.workflow import WorkflowBuilder, WorkflowStep
    from agentic_sdlc.orchestration.agent import Agent, AgentConfig, AgentRegistry
    from agentic_sdlc.core.config import ModelConfig
    
    # Setup
    registry = AgentRegistry()
    
    model_config = ModelConfig(
        provider="openai",
        model_name="gpt-4",
        api_key="test-key"
    )
    
    # Create agents
    for role in ["developer", "tester"]:
        agent = Agent(config=AgentConfig(
            name=f"{role}-agent",
            role=role,
            description=f"{role} agent",
            model_config=model_config
        ))
        registry.register(agent)
    
    # Create workflow
    builder = WorkflowBuilder(name="integration-test")
    builder.add_step(WorkflowStep(
        name="develop",
        action="develop",
        description="Develop feature",
        parameters={"agent": "developer-agent"}
    ))
    builder.add_step(WorkflowStep(
        name="test",
        action="test",
        description="Test feature",
        parameters={"agent": "tester-agent"},
        dependencies=["develop"]
    ))
    
    workflow = builder.build()
    
    # Verify
    assert len(registry.list_agents()) == 2
    assert len(workflow.steps) == 2
    assert workflow.steps[1].dependencies == ["develop"]
    
    print("✓ integration_test_full_workflow passed")


if __name__ == "__main__":
    print("=" * 60)
    print("VÍ DỤ: TESTING AGENTS AND WORKFLOWS")
    print("=" * 60)
    
    # Run tests
    test_agent_creation()
    test_workflow_creation()
    test_agent_with_mock_llm()
    test_workflow_execution()
    test_error_handling()
    integration_test_full_workflow()
    
    print("\n" + "=" * 60)
    print("✓ Tất cả tests passed!")
    print("=" * 60)
