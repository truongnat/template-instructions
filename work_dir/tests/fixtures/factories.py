"""Factory functions for creating test objects.

This module provides factory functions for creating test instances of various
entities with sensible defaults and optional overrides.
"""

from typing import Dict, Any, List, Optional
import random
import string
from datetime import datetime, timedelta


class WorkflowFactory:
    """Factory for creating test workflow configurations."""
    
    @staticmethod
    def create_basic_workflow(**overrides) -> Dict[str, Any]:
        """Create a basic workflow configuration with optional overrides.
        
        Args:
            **overrides: Key-value pairs to override default values
            
        Returns:
            Dict containing workflow configuration
        """
        workflow = {
            "name": "test-workflow",
            "version": "1.0.0",
            "description": "A test workflow",
            "agents": [],
            "tasks": [],
            "timeout": 3600
        }
        workflow.update(overrides)
        return workflow
    
    @staticmethod
    def create_workflow_with_tasks(num_tasks: int = 3, **overrides) -> Dict[str, Any]:
        """Create a workflow with a specified number of tasks.
        
        Args:
            num_tasks: Number of tasks to include
            **overrides: Key-value pairs to override default values
            
        Returns:
            Dict containing workflow configuration with tasks
        """
        tasks = [
            {
                "id": f"task-{i}",
                "type": "analysis",
                "config": {}
            }
            for i in range(1, num_tasks + 1)
        ]
        
        workflow = WorkflowFactory.create_basic_workflow(tasks=tasks)
        workflow.update(overrides)
        return workflow
    
    @staticmethod
    def create_workflow_with_agents(num_agents: int = 2, **overrides) -> Dict[str, Any]:
        """Create a workflow with a specified number of agents.
        
        Args:
            num_agents: Number of agents to include
            **overrides: Key-value pairs to override default values
            
        Returns:
            Dict containing workflow configuration with agents
        """
        agents = [f"agent-{i}" for i in range(1, num_agents + 1)]
        workflow = WorkflowFactory.create_basic_workflow(agents=agents)
        workflow.update(overrides)
        return workflow
    
    @staticmethod
    def create_complex_workflow(**overrides) -> Dict[str, Any]:
        """Create a complex workflow with agents, tasks, and dependencies.
        
        Args:
            **overrides: Key-value pairs to override default values
            
        Returns:
            Dict containing complex workflow configuration
        """
        workflow = {
            "name": "complex-workflow",
            "version": "1.0.0",
            "description": "A complex test workflow with multiple components",
            "agents": ["agent-1", "agent-2", "agent-3"],
            "tasks": [
                {
                    "id": "task-1",
                    "type": "analysis",
                    "config": {"priority": "high"},
                    "dependencies": []
                },
                {
                    "id": "task-2",
                    "type": "implementation",
                    "config": {"priority": "medium"},
                    "dependencies": ["task-1"]
                },
                {
                    "id": "task-3",
                    "type": "validation",
                    "config": {"priority": "high"},
                    "dependencies": ["task-2"]
                }
            ],
            "timeout": 7200,
            "retry_policy": {
                "max_attempts": 3,
                "backoff_multiplier": 2
            }
        }
        workflow.update(overrides)
        return workflow
    
    @staticmethod
    def create_minimal_workflow(**overrides) -> Dict[str, Any]:
        """Create a minimal workflow with only required fields.
        
        Args:
            **overrides: Key-value pairs to override default values
            
        Returns:
            Dict containing minimal workflow configuration
        """
        workflow = {
            "name": "minimal-workflow",
            "version": "1.0.0"
        }
        workflow.update(overrides)
        return workflow


class AgentFactory:
    """Factory for creating test agent configurations."""
    
    @staticmethod
    def create_agent(agent_type: str = "ba", **overrides) -> Dict[str, Any]:
        """Create an agent configuration with optional overrides.
        
        Args:
            agent_type: Type of agent (ba, pm, sa, implementation, research, quality_judge)
            **overrides: Key-value pairs to override default values
            
        Returns:
            Dict containing agent configuration
        """
        agent = {
            "id": "test-agent",
            "type": agent_type,
            "capabilities": [],
            "model": "gpt-4",
            "config": {}
        }
        agent.update(overrides)
        return agent
    
    @staticmethod
    def create_agent_pool(num_agents: int = 3, agent_types: Optional[List[str]] = None) -> List[Dict[str, Any]]:
        """Create a pool of agents.
        
        Args:
            num_agents: Number of agents to create
            agent_types: List of agent types to use (cycles if fewer than num_agents)
            
        Returns:
            List of agent configurations
        """
        if agent_types is None:
            agent_types = ["ba", "pm", "sa"]
        
        agents = []
        for i in range(num_agents):
            agent_type = agent_types[i % len(agent_types)]
            agent = AgentFactory.create_agent(
                agent_type=agent_type,
                id=f"agent-{i+1}"
            )
            agents.append(agent)
        
        return agents
    
    @staticmethod
    def create_ba_agent(**overrides) -> Dict[str, Any]:
        """Create a Business Analyst agent configuration.
        
        Args:
            **overrides: Key-value pairs to override default values
            
        Returns:
            Dict containing BA agent configuration
        """
        agent = {
            "id": "ba-agent",
            "type": "ba",
            "capabilities": ["requirements_analysis", "stakeholder_communication"],
            "model": "gpt-4",
            "config": {
                "temperature": 0.7,
                "max_tokens": 2000
            }
        }
        agent.update(overrides)
        return agent
    
    @staticmethod
    def create_pm_agent(**overrides) -> Dict[str, Any]:
        """Create a Project Manager agent configuration.
        
        Args:
            **overrides: Key-value pairs to override default values
            
        Returns:
            Dict containing PM agent configuration
        """
        agent = {
            "id": "pm-agent",
            "type": "pm",
            "capabilities": ["planning", "resource_allocation", "risk_management"],
            "model": "gpt-4",
            "config": {
                "temperature": 0.5,
                "max_tokens": 2000
            }
        }
        agent.update(overrides)
        return agent
    
    @staticmethod
    def create_sa_agent(**overrides) -> Dict[str, Any]:
        """Create a Software Architect agent configuration.
        
        Args:
            **overrides: Key-value pairs to override default values
            
        Returns:
            Dict containing SA agent configuration
        """
        agent = {
            "id": "sa-agent",
            "type": "sa",
            "capabilities": ["architecture_design", "technical_decisions"],
            "model": "gpt-4",
            "config": {
                "temperature": 0.6,
                "max_tokens": 3000
            }
        }
        agent.update(overrides)
        return agent
    
    @staticmethod
    def create_implementation_agent(**overrides) -> Dict[str, Any]:
        """Create an Implementation agent configuration.
        
        Args:
            **overrides: Key-value pairs to override default values
            
        Returns:
            Dict containing implementation agent configuration
        """
        agent = {
            "id": "impl-agent",
            "type": "implementation",
            "capabilities": ["coding", "testing", "debugging"],
            "model": "gpt-4",
            "config": {
                "temperature": 0.3,
                "max_tokens": 4000
            }
        }
        agent.update(overrides)
        return agent


class ConfigFactory:
    """Factory for creating test configuration objects."""
    
    @staticmethod
    def create_config(**overrides) -> Dict[str, Any]:
        """Create a basic configuration with optional overrides.
        
        Args:
            **overrides: Key-value pairs to override default values
            
        Returns:
            Dict containing configuration
        """
        config = {
            "core": {
                "log_level": "INFO",
                "debug": False
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
        config.update(overrides)
        return config
    
    @staticmethod
    def create_development_config(**overrides) -> Dict[str, Any]:
        """Create a development environment configuration.
        
        Args:
            **overrides: Key-value pairs to override default values
            
        Returns:
            Dict containing development configuration
        """
        config = {
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
        config.update(overrides)
        return config
    
    @staticmethod
    def create_production_config(**overrides) -> Dict[str, Any]:
        """Create a production environment configuration.
        
        Args:
            **overrides: Key-value pairs to override default values
            
        Returns:
            Dict containing production configuration
        """
        config = {
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
        config.update(overrides)
        return config
    
    @staticmethod
    def create_test_config(**overrides) -> Dict[str, Any]:
        """Create a test environment configuration.
        
        Args:
            **overrides: Key-value pairs to override default values
            
        Returns:
            Dict containing test configuration
        """
        config = {
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
        config.update(overrides)
        return config


class RuleFactory:
    """Factory for creating test rule configurations."""
    
    @staticmethod
    def create_rule(**overrides) -> Dict[str, Any]:
        """Create a rule configuration with optional overrides.
        
        Args:
            **overrides: Key-value pairs to override default values
            
        Returns:
            Dict containing rule configuration
        """
        rule = {
            "id": "test-rule",
            "name": "Test Rule",
            "description": "A test rule",
            "conditions": [],
            "actions": []
        }
        rule.update(overrides)
        return rule


class SkillFactory:
    """Factory for creating test skill configurations."""
    
    @staticmethod
    def create_skill(**overrides) -> Dict[str, Any]:
        """Create a skill configuration with optional overrides.
        
        Args:
            **overrides: Key-value pairs to override default values
            
        Returns:
            Dict containing skill configuration
        """
        skill = {
            "id": "test-skill",
            "name": "Test Skill",
            "description": "A test skill",
            "parameters": []
        }
        skill.update(overrides)
        return skill


class TaskFactory:
    """Factory for creating test task configurations."""
    
    @staticmethod
    def create_task(task_type: str = "analysis", **overrides) -> Dict[str, Any]:
        """Create a task configuration with optional overrides.
        
        Args:
            task_type: Type of task (analysis, implementation, validation, etc.)
            **overrides: Key-value pairs to override default values
            
        Returns:
            Dict containing task configuration
        """
        task = {
            "id": "test-task",
            "type": task_type,
            "config": {},
            "dependencies": []
        }
        task.update(overrides)
        return task
    
    @staticmethod
    def create_task_chain(num_tasks: int = 3, **overrides) -> List[Dict[str, Any]]:
        """Create a chain of dependent tasks.
        
        Args:
            num_tasks: Number of tasks to create
            **overrides: Key-value pairs to override default values
            
        Returns:
            List of task configurations with dependencies
        """
        tasks = []
        for i in range(1, num_tasks + 1):
            task = {
                "id": f"task-{i}",
                "type": "analysis" if i == 1 else "implementation",
                "config": {},
                "dependencies": [] if i == 1 else [f"task-{i-1}"]
            }
            tasks.append(task)
        return tasks
    
    @staticmethod
    def create_parallel_tasks(num_tasks: int = 3, **overrides) -> List[Dict[str, Any]]:
        """Create parallel tasks with no dependencies.
        
        Args:
            num_tasks: Number of tasks to create
            **overrides: Key-value pairs to override default values
            
        Returns:
            List of independent task configurations
        """
        tasks = []
        for i in range(1, num_tasks + 1):
            task = {
                "id": f"task-{i}",
                "type": "analysis",
                "config": {},
                "dependencies": []
            }
            tasks.append(task)
        return tasks


# ============================================================================
# Mock Data Generators
# ============================================================================

class MockDataGenerator:
    """Generator for creating mock test data."""
    
    @staticmethod
    def random_string(length: int = 10, prefix: str = "") -> str:
        """Generate a random string.
        
        Args:
            length: Length of random string
            prefix: Optional prefix for the string
            
        Returns:
            Random string with optional prefix
        """
        chars = string.ascii_lowercase + string.digits
        random_part = ''.join(random.choice(chars) for _ in range(length))
        return f"{prefix}{random_part}" if prefix else random_part
    
    @staticmethod
    def random_id(prefix: str = "id") -> str:
        """Generate a random ID.
        
        Args:
            prefix: Prefix for the ID
            
        Returns:
            Random ID string
        """
        return MockDataGenerator.random_string(length=8, prefix=f"{prefix}-")
    
    @staticmethod
    def random_version() -> str:
        """Generate a random semantic version.
        
        Returns:
            Version string in format X.Y.Z
        """
        major = random.randint(0, 5)
        minor = random.randint(0, 20)
        patch = random.randint(0, 50)
        return f"{major}.{minor}.{patch}"
    
    @staticmethod
    def random_timestamp(days_ago: int = 0) -> str:
        """Generate a random ISO timestamp.
        
        Args:
            days_ago: Number of days in the past (0 for now)
            
        Returns:
            ISO format timestamp string
        """
        base_time = datetime.now() - timedelta(days=days_ago)
        random_offset = timedelta(
            hours=random.randint(0, 23),
            minutes=random.randint(0, 59),
            seconds=random.randint(0, 59)
        )
        timestamp = base_time - random_offset
        return timestamp.isoformat()
    
    @staticmethod
    def random_workflow(**overrides) -> Dict[str, Any]:
        """Generate a random workflow configuration.
        
        Args:
            **overrides: Key-value pairs to override generated values
            
        Returns:
            Dict containing random workflow configuration
        """
        workflow = {
            "name": MockDataGenerator.random_string(prefix="workflow-"),
            "version": MockDataGenerator.random_version(),
            "description": f"Random test workflow {MockDataGenerator.random_id()}",
            "agents": [MockDataGenerator.random_id("agent") for _ in range(random.randint(1, 5))],
            "tasks": [
                {
                    "id": MockDataGenerator.random_id("task"),
                    "type": random.choice(["analysis", "implementation", "validation"]),
                    "config": {}
                }
                for _ in range(random.randint(1, 5))
            ],
            "timeout": random.choice([1800, 3600, 7200])
        }
        workflow.update(overrides)
        return workflow
    
    @staticmethod
    def random_agent(**overrides) -> Dict[str, Any]:
        """Generate a random agent configuration.
        
        Args:
            **overrides: Key-value pairs to override generated values
            
        Returns:
            Dict containing random agent configuration
        """
        agent_types = ["ba", "pm", "sa", "implementation", "research", "quality_judge"]
        models = ["gpt-3.5-turbo", "gpt-4", "gpt-4-turbo"]
        
        agent = {
            "id": MockDataGenerator.random_id("agent"),
            "type": random.choice(agent_types),
            "capabilities": [
                MockDataGenerator.random_string(prefix="cap-")
                for _ in range(random.randint(1, 4))
            ],
            "model": random.choice(models),
            "config": {
                "temperature": round(random.uniform(0.1, 1.0), 1),
                "max_tokens": random.choice([1000, 2000, 3000, 4000])
            }
        }
        agent.update(overrides)
        return agent
    
    @staticmethod
    def random_config(**overrides) -> Dict[str, Any]:
        """Generate a random configuration.
        
        Args:
            **overrides: Key-value pairs to override generated values
            
        Returns:
            Dict containing random configuration
        """
        log_levels = ["DEBUG", "INFO", "WARNING", "ERROR"]
        
        config = {
            "core": {
                "log_level": random.choice(log_levels),
                "debug": random.choice([True, False]),
                "environment": random.choice(["development", "test", "production"])
            },
            "agents": {
                "default_model": random.choice(["gpt-3.5-turbo", "gpt-4"]),
                "timeout": random.choice([120, 300, 600])
            },
            "workflows": {
                "max_concurrent": random.randint(1, 10),
                "retry_attempts": random.randint(1, 5)
            }
        }
        config.update(overrides)
        return config
    
    @staticmethod
    def random_task(**overrides) -> Dict[str, Any]:
        """Generate a random task configuration.
        
        Args:
            **overrides: Key-value pairs to override generated values
            
        Returns:
            Dict containing random task configuration
        """
        task_types = ["analysis", "implementation", "validation", "testing", "deployment"]
        
        task = {
            "id": MockDataGenerator.random_id("task"),
            "type": random.choice(task_types),
            "config": {
                "priority": random.choice(["low", "medium", "high"]),
                "timeout": random.choice([300, 600, 1200])
            },
            "dependencies": []
        }
        task.update(overrides)
        return task
    
    @staticmethod
    def random_api_response(success: bool = True, **overrides) -> Dict[str, Any]:
        """Generate a random API response.
        
        Args:
            success: Whether to generate a success or error response
            **overrides: Key-value pairs to override generated values
            
        Returns:
            Dict containing random API response
        """
        if success:
            response = {
                "status": "success",
                "data": {
                    "id": MockDataGenerator.random_id(),
                    "result": random.choice(["completed", "pending", "processing"]),
                    "timestamp": MockDataGenerator.random_timestamp()
                }
            }
        else:
            error_codes = ["VALIDATION_ERROR", "TIMEOUT_ERROR", "INTERNAL_ERROR", "NOT_FOUND"]
            response = {
                "status": "error",
                "error": {
                    "code": random.choice(error_codes),
                    "message": f"Error: {MockDataGenerator.random_string()}",
                    "timestamp": MockDataGenerator.random_timestamp()
                }
            }
        response.update(overrides)
        return response
