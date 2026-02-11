"""Mock data for testing.

This module provides mock data objects for use in tests.
"""

# Sample workflow configuration
SAMPLE_WORKFLOW = {
    "name": "test-workflow",
    "version": "1.0.0",
    "description": "A test workflow",
    "agents": ["agent-1", "agent-2"],
    "tasks": [
        {
            "id": "task-1",
            "type": "analysis",
            "config": {}
        }
    ],
    "timeout": 3600
}

# Sample agent configuration
SAMPLE_AGENT = {
    "id": "test-agent",
    "type": "ba",
    "capabilities": ["analysis", "planning"],
    "model": "gpt-4",
    "config": {}
}

# Sample rule configuration
SAMPLE_RULE = {
    "id": "test-rule",
    "name": "Test Rule",
    "description": "A test rule",
    "conditions": [],
    "actions": []
}

# Sample skill configuration
SAMPLE_SKILL = {
    "id": "test-skill",
    "name": "Test Skill",
    "description": "A test skill",
    "parameters": []
}

# Sample task configuration
SAMPLE_TASK = {
    "id": "task-1",
    "type": "analysis",
    "config": {
        "priority": "high",
        "timeout": 600
    },
    "dependencies": []
}

# Sample configuration
SAMPLE_CONFIG = {
    "core": {
        "log_level": "INFO",
        "debug": False,
        "environment": "test"
    },
    "agents": {
        "default_model": "gpt-4",
        "timeout": 300
    },
    "workflows": {
        "max_concurrent": 5,
        "retry_attempts": 3
    }
}

# Complex workflow with multiple agents and tasks
COMPLEX_WORKFLOW = {
    "name": "complex-workflow",
    "version": "2.0.0",
    "description": "A complex multi-agent workflow",
    "agents": ["ba-agent", "pm-agent", "sa-agent", "impl-agent"],
    "tasks": [
        {
            "id": "requirements-analysis",
            "type": "analysis",
            "config": {"priority": "high"},
            "dependencies": []
        },
        {
            "id": "architecture-design",
            "type": "design",
            "config": {"priority": "high"},
            "dependencies": ["requirements-analysis"]
        },
        {
            "id": "implementation",
            "type": "implementation",
            "config": {"priority": "medium"},
            "dependencies": ["architecture-design"]
        },
        {
            "id": "testing",
            "type": "validation",
            "config": {"priority": "high"},
            "dependencies": ["implementation"]
        }
    ],
    "timeout": 7200,
    "retry_policy": {
        "max_attempts": 3,
        "backoff_multiplier": 2
    }
}

# Agent pool with different types
AGENT_POOL = [
    {
        "id": "ba-agent",
        "type": "ba",
        "capabilities": ["requirements_analysis", "stakeholder_communication"],
        "model": "gpt-4",
        "config": {"temperature": 0.7, "max_tokens": 2000}
    },
    {
        "id": "pm-agent",
        "type": "pm",
        "capabilities": ["planning", "resource_allocation", "risk_management"],
        "model": "gpt-4",
        "config": {"temperature": 0.5, "max_tokens": 2000}
    },
    {
        "id": "sa-agent",
        "type": "sa",
        "capabilities": ["architecture_design", "technical_decisions"],
        "model": "gpt-4",
        "config": {"temperature": 0.6, "max_tokens": 3000}
    },
    {
        "id": "impl-agent",
        "type": "implementation",
        "capabilities": ["coding", "testing", "debugging"],
        "model": "gpt-4",
        "config": {"temperature": 0.3, "max_tokens": 4000}
    }
]

# API response samples
SAMPLE_SUCCESS_RESPONSE = {
    "status": "success",
    "data": {
        "id": "response-123",
        "result": "completed",
        "timestamp": "2024-01-15T10:30:00Z"
    }
}

SAMPLE_ERROR_RESPONSE = {
    "status": "error",
    "error": {
        "code": "VALIDATION_ERROR",
        "message": "Invalid configuration: missing required field 'name'",
        "timestamp": "2024-01-15T10:30:00Z"
    }
}

# Environment configurations
DEVELOPMENT_CONFIG = {
    "core": {
        "log_level": "DEBUG",
        "debug": True,
        "environment": "development"
    },
    "agents": {
        "default_model": "gpt-3.5-turbo",
        "timeout": 600
    },
    "workflows": {
        "max_concurrent": 3,
        "retry_attempts": 5
    },
    "monitoring": {
        "enabled": True,
        "metrics_interval": 60
    }
}

PRODUCTION_CONFIG = {
    "core": {
        "log_level": "WARNING",
        "debug": False,
        "environment": "production"
    },
    "agents": {
        "default_model": "gpt-4",
        "timeout": 300
    },
    "workflows": {
        "max_concurrent": 10,
        "retry_attempts": 3
    },
    "monitoring": {
        "enabled": True,
        "metrics_interval": 30
    },
    "security": {
        "encryption_enabled": True,
        "audit_logging": True
    }
}

TEST_CONFIG = {
    "core": {
        "log_level": "DEBUG",
        "debug": True,
        "environment": "test"
    },
    "agents": {
        "default_model": "gpt-3.5-turbo",
        "timeout": 120
    },
    "workflows": {
        "max_concurrent": 2,
        "retry_attempts": 1
    },
    "monitoring": {
        "enabled": False
    }
}

# Invalid configurations for testing validation
INVALID_WORKFLOW_MISSING_NAME = {
    "version": "1.0.0",
    "description": "Missing name field"
}

INVALID_WORKFLOW_MISSING_VERSION = {
    "name": "test-workflow",
    "description": "Missing version field"
}

INVALID_WORKFLOW_WRONG_TYPE = {
    "name": 123,  # Should be string
    "version": "1.0.0"
}

INVALID_AGENT_MISSING_ID = {
    "type": "ba",
    "capabilities": []
}

INVALID_AGENT_WRONG_TYPE = {
    "id": "test-agent",
    "type": "invalid-type",  # Not a valid agent type
    "capabilities": []
}

# Edge case data
MINIMAL_WORKFLOW = {
    "name": "minimal",
    "version": "1.0.0"
}

EMPTY_WORKFLOW = {}

WORKFLOW_WITH_CIRCULAR_DEPS = {
    "name": "circular-workflow",
    "version": "1.0.0",
    "tasks": [
        {
            "id": "task-1",
            "type": "analysis",
            "dependencies": ["task-2"]
        },
        {
            "id": "task-2",
            "type": "implementation",
            "dependencies": ["task-1"]
        }
    ]
}

# Large data sets for performance testing
LARGE_WORKFLOW = {
    "name": "large-workflow",
    "version": "1.0.0",
    "agents": [f"agent-{i}" for i in range(1, 51)],  # 50 agents
    "tasks": [
        {
            "id": f"task-{i}",
            "type": "analysis",
            "config": {},
            "dependencies": []
        }
        for i in range(1, 101)  # 100 tasks
    ],
    "timeout": 36000
}
