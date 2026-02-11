"""Schema validation logic for SDLC Kit data models."""

from dataclasses import dataclass, field
from typing import Dict, Any, List, Optional, Type
from models.schemas.workflow import WorkflowSchema
from models.schemas.agent import AgentSchema
from models.schemas.rule import RuleSchema
from models.schemas.skill import SkillSchema
from models.schemas.task import TaskSchema
from models.enums import WorkflowStatus, AgentType, TaskStatus, RuleType, SkillType


@dataclass
class ValidationResult:
    """Result of a validation operation.
    
    Attributes:
        is_valid: Whether the validation passed
        errors: List of validation error messages
        warnings: List of validation warning messages
    """
    is_valid: bool
    errors: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    
    def add_error(self, error: str) -> None:
        """Add an error message and mark validation as failed."""
        self.errors.append(error)
        self.is_valid = False
    
    def add_warning(self, warning: str) -> None:
        """Add a warning message."""
        self.warnings.append(warning)


class SchemaValidator:
    """Validator for SDLC Kit data schemas."""
    
    @staticmethod
    def validate_workflow(data: Dict[str, Any]) -> ValidationResult:
        """Validate workflow data against WorkflowSchema.
        
        Args:
            data: Dictionary containing workflow data
            
        Returns:
            ValidationResult with validation status and any errors
        """
        result = ValidationResult(is_valid=True)
        
        # Check required fields
        if 'name' not in data or not data['name']:
            result.add_error("Field 'name' is required and cannot be empty")
        
        if 'version' not in data or not data['version']:
            result.add_error("Field 'version' is required and cannot be empty")
        
        # Validate field types
        if 'name' in data and not isinstance(data['name'], str):
            result.add_error(f"Field 'name' must be a string, got {type(data['name']).__name__}")
        
        if 'version' in data and not isinstance(data['version'], str):
            result.add_error(f"Field 'version' must be a string, got {type(data['version']).__name__}")
        
        if 'description' in data and data['description'] is not None and not isinstance(data['description'], str):
            result.add_error(f"Field 'description' must be a string, got {type(data['description']).__name__}")
        
        if 'agents' in data:
            if not isinstance(data['agents'], list):
                result.add_error(f"Field 'agents' must be a list, got {type(data['agents']).__name__}")
            else:
                for i, agent in enumerate(data['agents']):
                    if not isinstance(agent, str):
                        result.add_error(f"Field 'agents[{i}]' must be a string, got {type(agent).__name__}")
        
        if 'tasks' in data:
            if not isinstance(data['tasks'], list):
                result.add_error(f"Field 'tasks' must be a list, got {type(data['tasks']).__name__}")
            else:
                for i, task in enumerate(data['tasks']):
                    if not isinstance(task, dict):
                        result.add_error(f"Field 'tasks[{i}]' must be a dictionary, got {type(task).__name__}")
        
        if 'timeout' in data:
            if not isinstance(data['timeout'], int):
                result.add_error(f"Field 'timeout' must be an integer, got {type(data['timeout']).__name__}")
            elif data['timeout'] < 1:
                result.add_error(f"Field 'timeout' must be at least 1, got {data['timeout']}")
        
        if 'status' in data:
            if isinstance(data['status'], str):
                try:
                    WorkflowStatus(data['status'])
                except ValueError:
                    valid_values = [s.value for s in WorkflowStatus]
                    result.add_error(f"Field 'status' must be one of {valid_values}, got '{data['status']}'")
            elif not isinstance(data['status'], WorkflowStatus):
                result.add_error(f"Field 'status' must be a string or WorkflowStatus enum, got {type(data['status']).__name__}")
        
        if 'config' in data and not isinstance(data['config'], dict):
            result.add_error(f"Field 'config' must be a dictionary, got {type(data['config']).__name__}")
        
        # Try to create the schema object if validation passed so far
        if result.is_valid:
            try:
                WorkflowSchema(**data)
            except (ValueError, TypeError) as e:
                result.add_error(f"Schema validation failed: {str(e)}")
        
        return result
    
    @staticmethod
    def validate_agent(data: Dict[str, Any]) -> ValidationResult:
        """Validate agent data against AgentSchema.
        
        Args:
            data: Dictionary containing agent data
            
        Returns:
            ValidationResult with validation status and any errors
        """
        result = ValidationResult(is_valid=True)
        
        # Check required fields
        if 'id' not in data or not data['id']:
            result.add_error("Field 'id' is required and cannot be empty")
        
        if 'type' not in data or not data['type']:
            result.add_error("Field 'type' is required and cannot be empty")
        
        # Validate field types
        if 'id' in data and not isinstance(data['id'], str):
            result.add_error(f"Field 'id' must be a string, got {type(data['id']).__name__}")
        
        if 'type' in data:
            if isinstance(data['type'], str):
                try:
                    AgentType(data['type'])
                except ValueError:
                    valid_values = [t.value for t in AgentType]
                    result.add_error(f"Field 'type' must be one of {valid_values}, got '{data['type']}'")
            elif not isinstance(data['type'], AgentType):
                result.add_error(f"Field 'type' must be a string or AgentType enum, got {type(data['type']).__name__}")
        
        if 'name' in data and data['name'] is not None and not isinstance(data['name'], str):
            result.add_error(f"Field 'name' must be a string, got {type(data['name']).__name__}")
        
        if 'description' in data and data['description'] is not None and not isinstance(data['description'], str):
            result.add_error(f"Field 'description' must be a string, got {type(data['description']).__name__}")
        
        if 'capabilities' in data:
            if not isinstance(data['capabilities'], list):
                result.add_error(f"Field 'capabilities' must be a list, got {type(data['capabilities']).__name__}")
            else:
                for i, cap in enumerate(data['capabilities']):
                    if not isinstance(cap, str):
                        result.add_error(f"Field 'capabilities[{i}]' must be a string, got {type(cap).__name__}")
        
        if 'model' in data and data['model'] is not None and not isinstance(data['model'], str):
            result.add_error(f"Field 'model' must be a string, got {type(data['model']).__name__}")
        
        if 'config' in data and not isinstance(data['config'], dict):
            result.add_error(f"Field 'config' must be a dictionary, got {type(data['config']).__name__}")
        
        if 'enabled' in data and not isinstance(data['enabled'], bool):
            result.add_error(f"Field 'enabled' must be a boolean, got {type(data['enabled']).__name__}")
        
        # Try to create the schema object if validation passed so far
        if result.is_valid:
            try:
                AgentSchema(**data)
            except (ValueError, TypeError) as e:
                result.add_error(f"Schema validation failed: {str(e)}")
        
        return result
    
    @staticmethod
    def validate_task(data: Dict[str, Any]) -> ValidationResult:
        """Validate task data against TaskSchema.
        
        Args:
            data: Dictionary containing task data
            
        Returns:
            ValidationResult with validation status and any errors
        """
        result = ValidationResult(is_valid=True)
        
        # Check required fields
        if 'id' not in data or not data['id']:
            result.add_error("Field 'id' is required and cannot be empty")
        
        if 'type' not in data or not data['type']:
            result.add_error("Field 'type' is required and cannot be empty")
        
        # Validate field types
        if 'id' in data and not isinstance(data['id'], str):
            result.add_error(f"Field 'id' must be a string, got {type(data['id']).__name__}")
        
        if 'type' in data and not isinstance(data['type'], str):
            result.add_error(f"Field 'type' must be a string, got {type(data['type']).__name__}")
        
        if 'name' in data and data['name'] is not None and not isinstance(data['name'], str):
            result.add_error(f"Field 'name' must be a string, got {type(data['name']).__name__}")
        
        if 'description' in data and data['description'] is not None and not isinstance(data['description'], str):
            result.add_error(f"Field 'description' must be a string, got {type(data['description']).__name__}")
        
        if 'agent_id' in data and data['agent_id'] is not None and not isinstance(data['agent_id'], str):
            result.add_error(f"Field 'agent_id' must be a string, got {type(data['agent_id']).__name__}")
        
        if 'dependencies' in data:
            if not isinstance(data['dependencies'], list):
                result.add_error(f"Field 'dependencies' must be a list, got {type(data['dependencies']).__name__}")
            else:
                for i, dep in enumerate(data['dependencies']):
                    if not isinstance(dep, str):
                        result.add_error(f"Field 'dependencies[{i}]' must be a string, got {type(dep).__name__}")
        
        if 'timeout' in data:
            if not isinstance(data['timeout'], int):
                result.add_error(f"Field 'timeout' must be an integer, got {type(data['timeout']).__name__}")
            elif data['timeout'] < 1:
                result.add_error(f"Field 'timeout' must be at least 1, got {data['timeout']}")
        
        if 'status' in data:
            if isinstance(data['status'], str):
                try:
                    TaskStatus(data['status'])
                except ValueError:
                    valid_values = [s.value for s in TaskStatus]
                    result.add_error(f"Field 'status' must be one of {valid_values}, got '{data['status']}'")
            elif not isinstance(data['status'], TaskStatus):
                result.add_error(f"Field 'status' must be a string or TaskStatus enum, got {type(data['status']).__name__}")
        
        if 'config' in data and not isinstance(data['config'], dict):
            result.add_error(f"Field 'config' must be a dictionary, got {type(data['config']).__name__}")
        
        if 'inputs' in data and not isinstance(data['inputs'], dict):
            result.add_error(f"Field 'inputs' must be a dictionary, got {type(data['inputs']).__name__}")
        
        if 'outputs' in data and not isinstance(data['outputs'], dict):
            result.add_error(f"Field 'outputs' must be a dictionary, got {type(data['outputs']).__name__}")
        
        if 'metadata' in data and not isinstance(data['metadata'], dict):
            result.add_error(f"Field 'metadata' must be a dictionary, got {type(data['metadata']).__name__}")
        
        # Try to create the schema object if validation passed so far
        if result.is_valid:
            try:
                TaskSchema(**data)
            except (ValueError, TypeError) as e:
                result.add_error(f"Schema validation failed: {str(e)}")
        
        return result
    
    @staticmethod
    def validate_rule(data: Dict[str, Any]) -> ValidationResult:
        """Validate rule data against RuleSchema.
        
        Args:
            data: Dictionary containing rule data
            
        Returns:
            ValidationResult with validation status and any errors
        """
        result = ValidationResult(is_valid=True)
        
        # Check required fields
        if 'id' not in data or not data['id']:
            result.add_error("Field 'id' is required and cannot be empty")
        
        if 'type' not in data or not data['type']:
            result.add_error("Field 'type' is required and cannot be empty")
        
        # Validate field types
        if 'id' in data and not isinstance(data['id'], str):
            result.add_error(f"Field 'id' must be a string, got {type(data['id']).__name__}")
        
        if 'type' in data:
            if isinstance(data['type'], str):
                try:
                    RuleType(data['type'])
                except ValueError:
                    valid_values = [t.value for t in RuleType]
                    result.add_error(f"Field 'type' must be one of {valid_values}, got '{data['type']}'")
            elif not isinstance(data['type'], RuleType):
                result.add_error(f"Field 'type' must be a string or RuleType enum, got {type(data['type']).__name__}")
        
        if 'name' in data and data['name'] is not None and not isinstance(data['name'], str):
            result.add_error(f"Field 'name' must be a string, got {type(data['name']).__name__}")
        
        if 'description' in data and data['description'] is not None and not isinstance(data['description'], str):
            result.add_error(f"Field 'description' must be a string, got {type(data['description']).__name__}")
        
        if 'condition' in data and data['condition'] is not None and not isinstance(data['condition'], str):
            result.add_error(f"Field 'condition' must be a string, got {type(data['condition']).__name__}")
        
        if 'action' in data and data['action'] is not None and not isinstance(data['action'], str):
            result.add_error(f"Field 'action' must be a string, got {type(data['action']).__name__}")
        
        if 'priority' in data and not isinstance(data['priority'], int):
            result.add_error(f"Field 'priority' must be an integer, got {type(data['priority']).__name__}")
        
        if 'enabled' in data and not isinstance(data['enabled'], bool):
            result.add_error(f"Field 'enabled' must be a boolean, got {type(data['enabled']).__name__}")
        
        if 'config' in data and not isinstance(data['config'], dict):
            result.add_error(f"Field 'config' must be a dictionary, got {type(data['config']).__name__}")
        
        if 'tags' in data:
            if not isinstance(data['tags'], list):
                result.add_error(f"Field 'tags' must be a list, got {type(data['tags']).__name__}")
            else:
                for i, tag in enumerate(data['tags']):
                    if not isinstance(tag, str):
                        result.add_error(f"Field 'tags[{i}]' must be a string, got {type(tag).__name__}")
        
        # Try to create the schema object if validation passed so far
        if result.is_valid:
            try:
                RuleSchema(**data)
            except (ValueError, TypeError) as e:
                result.add_error(f"Schema validation failed: {str(e)}")
        
        return result
    
    @staticmethod
    def validate_skill(data: Dict[str, Any]) -> ValidationResult:
        """Validate skill data against SkillSchema.
        
        Args:
            data: Dictionary containing skill data
            
        Returns:
            ValidationResult with validation status and any errors
        """
        result = ValidationResult(is_valid=True)
        
        # Check required fields
        if 'id' not in data or not data['id']:
            result.add_error("Field 'id' is required and cannot be empty")
        
        if 'type' not in data or not data['type']:
            result.add_error("Field 'type' is required and cannot be empty")
        
        # Validate field types
        if 'id' in data and not isinstance(data['id'], str):
            result.add_error(f"Field 'id' must be a string, got {type(data['id']).__name__}")
        
        if 'type' in data:
            if isinstance(data['type'], str):
                try:
                    SkillType(data['type'])
                except ValueError:
                    valid_values = [t.value for t in SkillType]
                    result.add_error(f"Field 'type' must be one of {valid_values}, got '{data['type']}'")
            elif not isinstance(data['type'], SkillType):
                result.add_error(f"Field 'type' must be a string or SkillType enum, got {type(data['type']).__name__}")
        
        if 'name' in data and data['name'] is not None and not isinstance(data['name'], str):
            result.add_error(f"Field 'name' must be a string, got {type(data['name']).__name__}")
        
        if 'description' in data and data['description'] is not None and not isinstance(data['description'], str):
            result.add_error(f"Field 'description' must be a string, got {type(data['description']).__name__}")
        
        if 'implementation' in data and data['implementation'] is not None and not isinstance(data['implementation'], str):
            result.add_error(f"Field 'implementation' must be a string, got {type(data['implementation']).__name__}")
        
        if 'parameters' in data:
            if not isinstance(data['parameters'], dict):
                result.add_error(f"Field 'parameters' must be a dictionary, got {type(data['parameters']).__name__}")
            else:
                for key, value in data['parameters'].items():
                    if not isinstance(value, str):
                        result.add_error(f"Field 'parameters[{key}]' must be a string, got {type(value).__name__}")
        
        if 'returns' in data and data['returns'] is not None and not isinstance(data['returns'], str):
            result.add_error(f"Field 'returns' must be a string, got {type(data['returns']).__name__}")
        
        if 'enabled' in data and not isinstance(data['enabled'], bool):
            result.add_error(f"Field 'enabled' must be a boolean, got {type(data['enabled']).__name__}")
        
        if 'config' in data and not isinstance(data['config'], dict):
            result.add_error(f"Field 'config' must be a dictionary, got {type(data['config']).__name__}")
        
        if 'tags' in data:
            if not isinstance(data['tags'], list):
                result.add_error(f"Field 'tags' must be a list, got {type(data['tags']).__name__}")
            else:
                for i, tag in enumerate(data['tags']):
                    if not isinstance(tag, str):
                        result.add_error(f"Field 'tags[{i}]' must be a string, got {type(tag).__name__}")
        
        # Try to create the schema object if validation passed so far
        if result.is_valid:
            try:
                SkillSchema(**data)
            except (ValueError, TypeError) as e:
                result.add_error(f"Schema validation failed: {str(e)}")
        
        return result
    
    @staticmethod
    def validate(data: Dict[str, Any], schema_type: str) -> ValidationResult:
        """Validate data against a specific schema type.
        
        Args:
            data: Dictionary containing data to validate
            schema_type: Type of schema to validate against
                        ('workflow', 'agent', 'task', 'rule', 'skill')
            
        Returns:
            ValidationResult with validation status and any errors
            
        Raises:
            ValueError: If schema_type is not recognized
        """
        validators = {
            'workflow': SchemaValidator.validate_workflow,
            'agent': SchemaValidator.validate_agent,
            'task': SchemaValidator.validate_task,
            'rule': SchemaValidator.validate_rule,
            'skill': SchemaValidator.validate_skill,
        }
        
        if schema_type not in validators:
            raise ValueError(f"Unknown schema type: {schema_type}. Must be one of {list(validators.keys())}")
        
        return validators[schema_type](data)
