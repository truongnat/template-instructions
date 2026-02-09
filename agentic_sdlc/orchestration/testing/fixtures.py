"""
Test fixtures for the Multi-Agent Orchestration System

This module provides sample data and fixtures for testing orchestration components.
"""

from datetime import datetime, timedelta
from typing import Dict, Any

from ..models.workflow import WorkflowPlan, OrchestrationPattern
from ..models.agent import (
    AgentConfig, AgentType, ModelTier, TaskInput, TaskOutput, 
    DataFormat, TaskPriority, ModelAssignment, DEFAULT_MODEL_ASSIGNMENTS
)
from ..models.communication import UserRequest, ConversationContext, SharedContext


def sample_workflow_plan() -> WorkflowPlan:
    """Create a sample workflow plan for testing"""
    return WorkflowPlan(
        pattern=OrchestrationPattern.SEQUENTIAL_HANDOFF,
        estimated_duration=120,  # 2 hours
        priority=2
    )


def sample_agent_config(agent_type: AgentType = AgentType.IMPLEMENTATION) -> AgentConfig:
    """Create a sample agent configuration for testing"""
    # Find the model assignment for this agent type
    model_assignment = None
    for assignment in DEFAULT_MODEL_ASSIGNMENTS:
        if assignment.role_type == agent_type:
            model_assignment = assignment
            break
    
    if not model_assignment:
        # Fallback assignment
        model_assignment = ModelAssignment(
            role_type=agent_type,
            model_tier=ModelTier.OPERATIONAL,
            recommended_model="gpt-3.5-turbo",
            fallback_model="claude-3-haiku",
            max_concurrent_instances=3,
            cost_per_token=0.002
        )
    
    return AgentConfig(
        agent_type=agent_type,
        model_assignment=model_assignment,
        max_retries=3,
        timeout_minutes=30,
        resource_limits={
            "cpu_cores": 2.0,
            "memory_mb": 1024.0,
            "disk_mb": 2048.0
        },
        environment_variables={
            "PYTHONPATH": "/app",
            "LOG_LEVEL": "INFO"
        }
    )


def sample_task_input(data_format: DataFormat = DataFormat.JSON) -> TaskInput:
    """Create a sample task input for testing"""
    if data_format == DataFormat.JSON:
        data = {
            "requirements": ["Implement user authentication", "Add password validation"],
            "constraints": ["Must use OAuth 2.0", "Password must be at least 8 characters"],
            "priority": "high"
        }
    elif data_format == DataFormat.TEXT:
        data = "Implement a user authentication system with OAuth 2.0 support and strong password validation."
    elif data_format == DataFormat.MARKDOWN:
        data = """
# User Authentication Requirements

## Features
- OAuth 2.0 integration
- Password validation
- Session management

## Constraints
- Minimum 8 character passwords
- Multi-factor authentication support
"""
    else:
        data = "Sample task data"
    
    return TaskInput(
        data=data,
        format=data_format,
        source="test_suite",
        dependencies=["user_model", "security_config"],
        metadata={
            "created_by": "test_user",
            "version": "1.0",
            "test_case": "sample_input"
        }
    )


def sample_task_output(data_format: DataFormat = DataFormat.JSON) -> TaskOutput:
    """Create a sample task output for testing"""
    if data_format == DataFormat.JSON:
        data = {
            "implementation": {
                "files_created": ["auth.py", "models.py", "tests.py"],
                "functions": ["authenticate_user", "validate_password", "create_session"],
                "dependencies": ["flask", "bcrypt", "jwt"]
            },
            "test_results": {
                "unit_tests": 15,
                "integration_tests": 8,
                "coverage": 95.2
            }
        }
    elif data_format == DataFormat.TEXT:
        data = "Successfully implemented user authentication system with OAuth 2.0 support. Created 3 files with 15 unit tests and 95.2% coverage."
    else:
        data = "Task completed successfully"
    
    return TaskOutput(
        data=data,
        format=data_format,
        confidence=0.92,
        next_actions=[
            "Deploy to staging environment",
            "Run integration tests",
            "Update documentation"
        ]
    )


def sample_user_request() -> UserRequest:
    """Create a sample user request for testing"""
    context = ConversationContext(
        user_id="test_user_123",
        interaction_count=3,
        context_data={
            "project": "e-commerce-platform",
            "previous_requests": ["setup database", "create user model"],
            "preferences": {"framework": "flask", "database": "postgresql"}
        },
        preferences={
            "communication_style": "detailed",
            "technical_level": "intermediate"
        }
    )
    
    return UserRequest(
        user_id="test_user_123",
        content="I need to implement user authentication for my e-commerce platform. It should support OAuth 2.0 and have strong password validation with multi-factor authentication.",
        context=context,
        intent="implement_authentication",
        confidence=0.87,
        metadata={
            "source": "web_interface",
            "session_id": "sess_456789",
            "ip_address": "192.168.1.100"
        }
    )


def sample_shared_context() -> SharedContext:
    """Create a sample shared context for testing"""
    from ..models.communication import Requirement, Constraint, Stakeholder, Timeline, Resource
    
    # Create sample requirements
    requirements = [
        Requirement(
            title="User Authentication",
            description="Users must be able to authenticate using email/password or OAuth providers",
            type="functional",
            priority="high",
            source="product_requirements",
            acceptance_criteria=[
                "Users can register with email and password",
                "Users can login with Google OAuth",
                "Password must meet security requirements",
                "Failed login attempts are rate limited"
            ]
        ),
        Requirement(
            title="Performance",
            description="Authentication should complete within 2 seconds",
            type="non-functional",
            priority="medium",
            source="technical_requirements",
            acceptance_criteria=[
                "Login response time < 2 seconds",
                "Registration response time < 3 seconds",
                "System supports 1000 concurrent users"
            ]
        )
    ]
    
    # Create sample constraints
    constraints = [
        Constraint(
            name="Technology Stack",
            description="Must use Python Flask framework",
            type="technical",
            impact="high",
            is_negotiable=False
        ),
        Constraint(
            name="Compliance",
            description="Must comply with GDPR data protection requirements",
            type="regulatory",
            impact="high",
            is_negotiable=False
        )
    ]
    
    # Create sample stakeholders
    stakeholders = [
        Stakeholder(
            name="Product Manager",
            role="PM",
            influence="high",
            interest="high",
            contact_info={"email": "pm@company.com"},
            expectations=["Feature delivered on time", "Meets user requirements"]
        ),
        Stakeholder(
            name="Security Team",
            role="Security Reviewer",
            influence="medium",
            interest="high",
            contact_info={"email": "security@company.com"},
            expectations=["Secure implementation", "Compliance with security policies"]
        )
    ]
    
    # Create sample timeline
    timeline = Timeline(
        start_date=datetime.now(),
        end_date=datetime.now() + timedelta(days=14),
        buffer_days=2
    )
    timeline.add_milestone("Design Complete", datetime.now() + timedelta(days=3))
    timeline.add_milestone("Implementation Complete", datetime.now() + timedelta(days=10))
    timeline.add_milestone("Testing Complete", datetime.now() + timedelta(days=12))
    
    # Create sample resources
    resources = [
        Resource(
            name="Senior Developer",
            type="human",
            availability=0.8,
            cost_per_unit=100.0,
            unit="hour",
            skills=["Python", "Flask", "OAuth", "Security"]
        ),
        Resource(
            name="Development Environment",
            type="technical",
            availability=1.0,
            cost_per_unit=50.0,
            unit="day",
            skills=["Docker", "PostgreSQL", "Redis"]
        )
    ]
    
    context = SharedContext(
        requirements=requirements,
        constraints=constraints,
        stakeholders=stakeholders,
        timeline=timeline,
        resources=resources,
        shared_data={
            "project_name": "E-commerce Authentication",
            "repository": "https://github.com/company/ecommerce-auth",
            "environment": "development",
            "database_url": "postgresql://localhost/ecommerce_dev"
        }
    )
    
    return context


def sample_workflow_execution_data() -> Dict[str, Any]:
    """Create sample workflow execution data for testing"""
    return {
        "workflow_id": "wf_12345",
        "execution_id": "exec_67890",
        "user_request": sample_user_request(),
        "workflow_plan": sample_workflow_plan(),
        "shared_context": sample_shared_context(),
        "agent_configs": {
            "pm": sample_agent_config(AgentType.PM),
            "ba": sample_agent_config(AgentType.BA),
            "sa": sample_agent_config(AgentType.SA),
            "implementation": sample_agent_config(AgentType.IMPLEMENTATION)
        },
        "expected_outputs": {
            "pm": "User stories and acceptance criteria",
            "ba": "Business analysis and process flows",
            "sa": "Technical architecture and design",
            "implementation": "Working code implementation"
        }
    }


def create_minimal_workflow() -> WorkflowPlan:
    """Create a minimal workflow for basic testing"""
    return WorkflowPlan(
        pattern=OrchestrationPattern.SEQUENTIAL_HANDOFF,
        estimated_duration=30,
        priority=3
    )


def create_complex_workflow() -> WorkflowPlan:
    """Create a complex workflow for advanced testing"""
    from ..models.agent import AgentAssignment, TaskDependency, ResourceRequirement
    
    workflow = WorkflowPlan(
        pattern=OrchestrationPattern.PARALLEL_EXECUTION,
        estimated_duration=240,  # 4 hours
        priority=1
    )
    
    # Add agent assignments
    workflow.add_agent_assignment(AgentAssignment(
        agent_type=AgentType.PM,
        priority=1,
        estimated_duration=60
    ))
    workflow.add_agent_assignment(AgentAssignment(
        agent_type=AgentType.BA,
        priority=1,
        estimated_duration=90
    ))
    workflow.add_agent_assignment(AgentAssignment(
        agent_type=AgentType.SA,
        priority=2,
        estimated_duration=120
    ))
    workflow.add_agent_assignment(AgentAssignment(
        agent_type=AgentType.IMPLEMENTATION,
        priority=3,
        estimated_duration=180
    ))
    
    # Add dependencies
    workflow.add_dependency(TaskDependency(
        dependent_task_id="sa_task",
        prerequisite_task_id="pm_task",
        dependency_type="completion"
    ))
    workflow.add_dependency(TaskDependency(
        dependent_task_id="implementation_task",
        prerequisite_task_id="sa_task",
        dependency_type="completion"
    ))
    
    # Add resource requirements
    workflow.required_resources.extend([
        ResourceRequirement(
            resource_type="compute",
            amount=4.0,
            unit="cpu_cores",
            estimated_cost=50.0
        ),
        ResourceRequirement(
            resource_type="memory",
            amount=8192.0,
            unit="mb",
            estimated_cost=20.0
        )
    ])
    
    return workflow