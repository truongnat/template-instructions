"""
Testing utilities and configuration for the Multi-Agent Orchestration System

This module provides testing utilities, property-based testing configuration,
and test fixtures for the orchestration system.
"""

from .property_testing import (
    OrchestrationTestCase,
    workflow_strategy,
    agent_task_strategy,
    agent_result_strategy,
    user_request_strategy
)

from .fixtures import (
    sample_workflow_plan,
    sample_agent_config,
    sample_task_input,
    sample_user_request
)

from .helpers import (
    create_test_workflow,
    create_test_agent,
    create_test_task,
    assert_workflow_valid,
    assert_agent_state_consistent
)

__all__ = [
    # Property testing
    "OrchestrationTestCase",
    "workflow_strategy",
    "agent_task_strategy", 
    "agent_result_strategy",
    "user_request_strategy",
    
    # Fixtures
    "sample_workflow_plan",
    "sample_agent_config",
    "sample_task_input",
    "sample_user_request",
    
    # Helpers
    "create_test_workflow",
    "create_test_agent",
    "create_test_task",
    "assert_workflow_valid",
    "assert_agent_state_consistent"
]