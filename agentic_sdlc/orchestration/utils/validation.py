"""
Validation utilities for the Multi-Agent Orchestration System

This module provides validation functions for various data structures
and configurations used in the orchestration system.
"""

from typing import List, Dict, Any, Optional, Union
from dataclasses import dataclass
from datetime import datetime

from ..models.workflow import WorkflowPlan, OrchestrationPattern
from ..models.agent import AgentConfig, AgentType, TaskInput, DataFormat
from ..exceptions.base import OrchestrationError


@dataclass
class ValidationResult:
    """Result of a validation operation"""
    is_valid: bool
    errors: List[str]
    warnings: List[str]
    
    def __init__(self):
        self.is_valid = True
        self.errors = []
        self.warnings = []
    
    def add_error(self, error: str):
        """Add a validation error"""
        self.errors.append(error)
        self.is_valid = False
    
    def add_warning(self, warning: str):
        """Add a validation warning"""
        self.warnings.append(warning)
    
    def merge(self, other: 'ValidationResult'):
        """Merge another validation result into this one"""
        self.errors.extend(other.errors)
        self.warnings.extend(other.warnings)
        if not other.is_valid:
            self.is_valid = False


def validate_workflow_plan(plan: WorkflowPlan) -> ValidationResult:
    """Validate a workflow plan"""
    result = ValidationResult()
    
    # Check required fields
    if not plan.id:
        result.add_error("Workflow plan must have an ID")
    
    if not isinstance(plan.pattern, OrchestrationPattern):
        result.add_error("Workflow plan must have a valid orchestration pattern")
    
    # Validate agents
    if not plan.agents:
        result.add_warning("Workflow plan has no agents assigned")
    else:
        agent_types = set()
        for agent in plan.agents:
            if not isinstance(agent.agent_type, AgentType):
                result.add_error(f"Invalid agent type: {agent.agent_type}")
            
            if agent.agent_type in agent_types:
                result.add_warning(f"Duplicate agent type: {agent.agent_type}")
            agent_types.add(agent.agent_type)
            
            if agent.estimated_duration < 0:
                result.add_error(f"Agent {agent.agent_type} has negative estimated duration")
    
    # Validate dependencies
    agent_ids = {agent.agent_type.value for agent in plan.agents}
    for dependency in plan.dependencies:
        if dependency.dependent_task_id not in agent_ids:
            result.add_error(f"Dependency references unknown task: {dependency.dependent_task_id}")
        if dependency.prerequisite_task_id not in agent_ids:
            result.add_error(f"Dependency references unknown prerequisite: {dependency.prerequisite_task_id}")
    
    # Validate estimated duration
    if plan.estimated_duration < 0:
        result.add_error("Workflow plan cannot have negative estimated duration")
    
    # Validate priority
    if not 1 <= plan.priority <= 5:
        result.add_error("Workflow plan priority must be between 1 and 5")
    
    # Check for circular dependencies
    if _has_circular_dependencies(plan.dependencies):
        result.add_error("Workflow plan has circular dependencies")
    
    return result


def validate_agent_config(config: AgentConfig) -> ValidationResult:
    """Validate an agent configuration"""
    result = ValidationResult()
    
    # Check required fields
    if not isinstance(config.agent_type, AgentType):
        result.add_error("Agent config must have a valid agent type")
    
    if not config.model_assignment:
        result.add_error("Agent config must have a model assignment")
    else:
        # Validate model assignment
        if config.model_assignment.role_type != config.agent_type:
            result.add_error("Model assignment role type must match agent type")
        
        if not config.model_assignment.recommended_model:
            result.add_error("Model assignment must have a recommended model")
        
        if config.model_assignment.max_concurrent_instances <= 0:
            result.add_error("Model assignment must allow at least 1 concurrent instance")
        
        if config.model_assignment.cost_per_token < 0:
            result.add_error("Model assignment cannot have negative cost per token")
    
    # Validate retry settings
    if config.max_retries < 0:
        result.add_error("Agent config cannot have negative max retries")
    
    if config.max_retries > 10:
        result.add_warning("Agent config has high max retries (>10)")
    
    # Validate timeout
    if config.timeout_minutes <= 0:
        result.add_error("Agent config must have positive timeout")
    
    if config.timeout_minutes > 240:  # 4 hours
        result.add_warning("Agent config has very long timeout (>4 hours)")
    
    # Validate resource limits
    for resource, limit in config.resource_limits.items():
        if isinstance(limit, (int, float)) and limit < 0:
            result.add_error(f"Resource limit for {resource} cannot be negative")
    
    return result


def validate_task_input(task_input: TaskInput) -> ValidationResult:
    """Validate task input data"""
    result = ValidationResult()
    
    # Check data format consistency
    if not task_input.validate_format():
        result.add_error(f"Task input data does not match specified format: {task_input.format}")
    
    # Validate source
    if not task_input.source:
        result.add_warning("Task input has no source specified")
    
    # Check for empty data
    if task_input.data is None:
        result.add_error("Task input data cannot be None")
    elif isinstance(task_input.data, (list, dict, str)) and len(task_input.data) == 0:
        result.add_warning("Task input data is empty")
    
    # Validate dependencies
    for dep in task_input.dependencies:
        if not isinstance(dep, str) or not dep.strip():
            result.add_error("Task input dependencies must be non-empty strings")
    
    # Validate metadata
    if task_input.metadata:
        for key, value in task_input.metadata.items():
            if not isinstance(key, str):
                result.add_error("Task input metadata keys must be strings")
    
    return result


def validate_json_schema(data: Any, schema: Dict[str, Any]) -> ValidationResult:
    """Validate data against a JSON schema"""
    result = ValidationResult()
    
    try:
        import jsonschema
        jsonschema.validate(data, schema)
    except ImportError:
        result.add_warning("jsonschema library not available, skipping schema validation")
    except jsonschema.ValidationError as e:
        result.add_error(f"Schema validation failed: {e.message}")
    except jsonschema.SchemaError as e:
        result.add_error(f"Invalid schema: {e.message}")
    
    return result


def validate_email_format(email: str) -> bool:
    """Validate email format"""
    import re
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return bool(re.match(pattern, email))


def validate_url_format(url: str) -> bool:
    """Validate URL format"""
    import re
    pattern = r'^https?://(?:[-\w.])+(?:[:\d]+)?(?:/(?:[\w/_.])*(?:\?(?:[\w&=%.])*)?(?:#(?:\w*))?)?$'
    return bool(re.match(pattern, url))


def validate_datetime_range(start: datetime, end: datetime) -> ValidationResult:
    """Validate datetime range"""
    result = ValidationResult()
    
    if start >= end:
        result.add_error("Start datetime must be before end datetime")
    
    now = datetime.now()
    if end < now:
        result.add_warning("End datetime is in the past")
    
    duration = end - start
    if duration.total_seconds() > 365 * 24 * 3600:  # 1 year
        result.add_warning("Datetime range spans more than 1 year")
    
    return result


def validate_resource_allocation(allocation: Dict[str, Union[int, float]]) -> ValidationResult:
    """Validate resource allocation"""
    result = ValidationResult()
    
    required_resources = ["cpu_cores", "memory_mb", "disk_mb"]
    
    for resource in required_resources:
        if resource not in allocation:
            result.add_error(f"Missing required resource: {resource}")
        elif allocation[resource] <= 0:
            result.add_error(f"Resource {resource} must be positive")
    
    # Check reasonable limits
    if "cpu_cores" in allocation and allocation["cpu_cores"] > 64:
        result.add_warning("CPU cores allocation is very high (>64)")
    
    if "memory_mb" in allocation and allocation["memory_mb"] > 64 * 1024:  # 64GB
        result.add_warning("Memory allocation is very high (>64GB)")
    
    if "disk_mb" in allocation and allocation["disk_mb"] > 1024 * 1024:  # 1TB
        result.add_warning("Disk allocation is very high (>1TB)")
    
    return result


def _has_circular_dependencies(dependencies: List) -> bool:
    """Check if dependencies have circular references"""
    # Build adjacency list
    graph = {}
    for dep in dependencies:
        if dep.prerequisite_task_id not in graph:
            graph[dep.prerequisite_task_id] = []
        graph[dep.prerequisite_task_id].append(dep.dependent_task_id)
    
    # DFS to detect cycles
    visited = set()
    rec_stack = set()
    
    def has_cycle(node):
        if node in rec_stack:
            return True
        if node in visited:
            return False
        
        visited.add(node)
        rec_stack.add(node)
        
        for neighbor in graph.get(node, []):
            if has_cycle(neighbor):
                return True
        
        rec_stack.remove(node)
        return False
    
    for node in graph:
        if node not in visited:
            if has_cycle(node):
                return True
    
    return False


def validate_configuration_completeness(config: Dict[str, Any]) -> ValidationResult:
    """Validate that configuration has all required fields"""
    result = ValidationResult()
    
    required_sections = [
        "model", "agent_pool", "logging", "database"
    ]
    
    for section in required_sections:
        if section not in config:
            result.add_error(f"Missing required configuration section: {section}")
    
    # Validate model configuration
    if "model" in config:
        model_config = config["model"]
        if not model_config.get("openai_api_key") and not model_config.get("anthropic_api_key"):
            result.add_warning("No API keys configured for model providers")
    
    # Validate database configuration
    if "database" in config:
        db_config = config["database"]
        if db_config.get("type") == "sqlite" and not db_config.get("sqlite_path"):
            result.add_error("SQLite database path not configured")
    
    return result