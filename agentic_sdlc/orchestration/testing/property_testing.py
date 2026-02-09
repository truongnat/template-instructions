"""
Property-based testing utilities for the Multi-Agent Orchestration System

This module provides Hypothesis strategies and test case base classes for
property-based testing of the orchestration system components.
"""

import unittest
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional

try:
    from hypothesis import given, strategies as st, settings, Verbosity
    from hypothesis.strategies import composite
    HYPOTHESIS_AVAILABLE = True
except ImportError:
    # Fallback for when Hypothesis is not available
    HYPOTHESIS_AVAILABLE = False
    
    # Mock decorators and strategies
    def given(*args, **kwargs):
        def decorator(func):
            return func
        return decorator
    
    class MockStrategies:
        def text(self, **kwargs): return lambda: "test"
        def integers(self, **kwargs): return lambda: 1
        def floats(self, **kwargs): return lambda: 1.0
        def booleans(self): return lambda: True
        def lists(self, *args, **kwargs): return lambda: []
        def dictionaries(self, *args, **kwargs): return lambda: {}
        def one_of(self, *args): return lambda: args[0]() if args else lambda: None
        def just(self, value): return lambda: value
        def datetimes(self, **kwargs): return lambda: datetime.now()
    
    st = MockStrategies()
    
    def composite(func):
        return func
    
    def settings(**kwargs):
        def decorator(func):
            return func
        return decorator
    
    class Verbosity:
        verbose = "verbose"

from ..models.workflow import (
    WorkflowPlan, WorkflowState, OrchestrationPattern, ExecutionStatus
)
from ..models.agent import (
    AgentTask, AgentResult, AgentType, TaskStatus, ModelTier, 
    TaskInput, TaskOutput, DataFormat, TaskPriority
)
from ..models.communication import (
    UserRequest, ConversationContext, SharedContext
)


# Hypothesis strategies for generating test data

@composite
def orchestration_pattern_strategy(draw):
    """Strategy for generating OrchestrationPattern values"""
    return draw(st.one_of([
        st.just(OrchestrationPattern.SEQUENTIAL_HANDOFF),
        st.just(OrchestrationPattern.PARALLEL_EXECUTION),
        st.just(OrchestrationPattern.DYNAMIC_ROUTING),
        st.just(OrchestrationPattern.HIERARCHICAL_DELEGATION)
    ]))


@composite
def agent_type_strategy(draw):
    """Strategy for generating AgentType values"""
    return draw(st.one_of([
        st.just(AgentType.PM),
        st.just(AgentType.BA),
        st.just(AgentType.SA),
        st.just(AgentType.RESEARCH),
        st.just(AgentType.QUALITY_JUDGE),
        st.just(AgentType.IMPLEMENTATION)
    ]))


@composite
def task_status_strategy(draw):
    """Strategy for generating TaskStatus values"""
    return draw(st.one_of([
        st.just(TaskStatus.PENDING),
        st.just(TaskStatus.IN_PROGRESS),
        st.just(TaskStatus.COMPLETED),
        st.just(TaskStatus.FAILED),
        st.just(TaskStatus.CANCELLED)
    ]))


@composite
def data_format_strategy(draw):
    """Strategy for generating DataFormat values"""
    return draw(st.one_of([
        st.just(DataFormat.JSON),
        st.just(DataFormat.TEXT),
        st.just(DataFormat.MARKDOWN),
        st.just(DataFormat.XML),
        st.just(DataFormat.YAML)
    ]))


@composite
def task_priority_strategy(draw):
    """Strategy for generating TaskPriority values"""
    return draw(st.one_of([
        st.just(TaskPriority.CRITICAL),
        st.just(TaskPriority.HIGH),
        st.just(TaskPriority.MEDIUM),
        st.just(TaskPriority.LOW),
        st.just(TaskPriority.BACKGROUND)
    ]))


@composite
def task_input_strategy(draw):
    """Strategy for generating TaskInput instances"""
    data_format = draw(data_format_strategy())
    
    # Generate data based on format
    if data_format == DataFormat.JSON:
        data = draw(st.one_of([
            st.dictionaries(st.text(), st.one_of([st.text(), st.integers(), st.floats()])),
            st.lists(st.dictionaries(st.text(), st.text()))
        ]))
    elif data_format == DataFormat.TEXT:
        data = draw(st.text(min_size=1, max_size=1000))
    else:
        data = draw(st.text(min_size=1, max_size=500))
    
    return TaskInput(
        data=data,
        format=data_format,
        source=draw(st.text(min_size=1, max_size=50)),
        dependencies=draw(st.lists(st.text(min_size=1, max_size=20), max_size=5)),
        metadata=draw(st.dictionaries(st.text(), st.text(), max_size=5))
    )


@composite
def task_output_strategy(draw):
    """Strategy for generating TaskOutput instances"""
    data_format = draw(data_format_strategy())
    
    # Generate data based on format
    if data_format == DataFormat.JSON:
        data = draw(st.dictionaries(st.text(), st.one_of([st.text(), st.integers()])))
    else:
        data = draw(st.text(min_size=1, max_size=500))
    
    return TaskOutput(
        data=data,
        format=data_format,
        confidence=draw(st.floats(min_value=0.0, max_value=1.0)),
        next_actions=draw(st.lists(st.text(min_size=1, max_size=50), max_size=3))
    )


@composite
def agent_task_strategy(draw):
    """Strategy for generating AgentTask instances"""
    return AgentTask(
        type=draw(st.text(min_size=1, max_size=50)),
        input=draw(task_input_strategy()),
        priority=draw(task_priority_strategy()),
        deadline=draw(st.one_of([
            st.none(),
            st.datetimes(min_value=datetime.now(), max_value=datetime.now() + timedelta(days=30))
        ]))
    )


@composite
def agent_result_strategy(draw):
    """Strategy for generating AgentResult instances"""
    return AgentResult(
        task_id=draw(st.text(min_size=1, max_size=50)),
        instance_id=draw(st.text(min_size=1, max_size=50)),
        status=draw(task_status_strategy()),
        output=draw(task_output_strategy()),
        confidence=draw(st.floats(min_value=0.0, max_value=1.0)),
        execution_time=draw(st.floats(min_value=0.0, max_value=3600.0)),
        recommendations=draw(st.lists(st.text(min_size=1, max_size=100), max_size=5))
    )


@composite
def conversation_context_strategy(draw):
    """Strategy for generating ConversationContext instances"""
    return ConversationContext(
        user_id=draw(st.text(min_size=1, max_size=50)),
        interaction_count=draw(st.integers(min_value=0, max_value=100)),
        context_data=draw(st.dictionaries(st.text(), st.text(), max_size=10)),
        preferences=draw(st.dictionaries(st.text(), st.text(), max_size=5))
    )


@composite
def user_request_strategy(draw):
    """Strategy for generating UserRequest instances"""
    user_id = draw(st.text(min_size=1, max_size=50))
    context = draw(st.one_of([st.none(), conversation_context_strategy()]))
    
    # Ensure context user_id matches request user_id if context exists
    if context:
        context.user_id = user_id
    
    return UserRequest(
        user_id=user_id,
        content=draw(st.text(min_size=1, max_size=1000)),
        context=context,
        intent=draw(st.one_of([st.none(), st.text(min_size=1, max_size=100)])),
        confidence=draw(st.floats(min_value=0.0, max_value=1.0)),
        metadata=draw(st.dictionaries(st.text(), st.text(), max_size=5))
    )


@composite
def workflow_strategy(draw):
    """Strategy for generating WorkflowPlan instances"""
    return WorkflowPlan(
        pattern=draw(orchestration_pattern_strategy()),
        estimated_duration=draw(st.integers(min_value=1, max_value=1440)),  # 1 minute to 24 hours
        priority=draw(st.integers(min_value=1, max_value=5))
    )


class OrchestrationTestCase(unittest.TestCase):
    """Base test case class with orchestration-specific assertions"""
    
    def setUp(self):
        """Set up test case"""
        if not HYPOTHESIS_AVAILABLE:
            self.skipTest("Hypothesis not available")
    
    def assertWorkflowValid(self, workflow: WorkflowPlan):
        """Assert that a workflow plan is valid"""
        self.assertIsNotNone(workflow.id)
        self.assertIsInstance(workflow.pattern, OrchestrationPattern)
        self.assertGreaterEqual(workflow.estimated_duration, 0)
        self.assertIn(workflow.priority, range(1, 6))
    
    def assertAgentTaskValid(self, task: AgentTask):
        """Assert that an agent task is valid"""
        self.assertIsNotNone(task.id)
        self.assertIsNotNone(task.type)
        self.assertIsInstance(task.input, TaskInput)
        self.assertIsInstance(task.priority, TaskPriority)
        
        if task.deadline:
            self.assertGreater(task.deadline, datetime.now() - timedelta(days=1))
    
    def assertAgentResultValid(self, result: AgentResult):
        """Assert that an agent result is valid"""
        self.assertIsNotNone(result.task_id)
        self.assertIsNotNone(result.instance_id)
        self.assertIsInstance(result.status, TaskStatus)
        self.assertIsInstance(result.output, TaskOutput)
        self.assertGreaterEqual(result.confidence, 0.0)
        self.assertLessEqual(result.confidence, 1.0)
        self.assertGreaterEqual(result.execution_time, 0.0)
    
    def assertUserRequestValid(self, request: UserRequest):
        """Assert that a user request is valid"""
        self.assertIsNotNone(request.id)
        self.assertIsNotNone(request.user_id)
        self.assertIsNotNone(request.content)
        self.assertGreaterEqual(request.confidence, 0.0)
        self.assertLessEqual(request.confidence, 1.0)
        
        if request.context:
            self.assertIsInstance(request.context, ConversationContext)
    
    def assertTaskInputValid(self, task_input: TaskInput):
        """Assert that task input is valid"""
        self.assertIsNotNone(task_input.data)
        self.assertIsInstance(task_input.format, DataFormat)
        self.assertTrue(task_input.validate_format())
    
    def assertTaskOutputValid(self, task_output: TaskOutput):
        """Assert that task output is valid"""
        self.assertIsNotNone(task_output.data)
        self.assertIsInstance(task_output.format, DataFormat)
        self.assertGreaterEqual(task_output.confidence, 0.0)
        self.assertLessEqual(task_output.confidence, 1.0)


# Property test configuration
if HYPOTHESIS_AVAILABLE:
    # Configure Hypothesis settings
    settings.register_profile("default", max_examples=100, deadline=None)
    settings.register_profile("ci", max_examples=1000, deadline=None)
    settings.register_profile("dev", max_examples=10, verbosity=Verbosity.verbose)
    
    # Load profile based on environment
    import os
    profile = os.getenv("HYPOTHESIS_PROFILE", "default")
    settings.load_profile(profile)