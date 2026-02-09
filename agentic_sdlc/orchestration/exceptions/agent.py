"""
Agent-related exception classes for the Multi-Agent Orchestration System
"""

from typing import Optional, Dict, Any, List
from .base import OrchestrationError


class AgentError(OrchestrationError):
    """Base class for agent-related errors"""
    
    def __init__(
        self,
        message: str,
        agent_id: Optional[str] = None,
        agent_type: Optional[str] = None,
        **kwargs
    ):
        context = kwargs.get("context", {})
        context.update({
            "agent_id": agent_id,
            "agent_type": agent_type
        })
        kwargs["context"] = context
        super().__init__(message, **kwargs)
        self.agent_id = agent_id
        self.agent_type = agent_type


class AgentInitializationError(AgentError):
    """Raised when agent initialization fails"""
    
    def __init__(
        self,
        message: str,
        initialization_errors: Optional[List[str]] = None,
        **kwargs
    ):
        context = kwargs.get("context", {})
        context.update({"initialization_errors": initialization_errors or []})
        kwargs["context"] = context
        super().__init__(message, **kwargs)
        self.initialization_errors = initialization_errors or []


class AgentConfigurationError(AgentError):
    """Raised when agent configuration is invalid"""
    
    def __init__(
        self,
        message: str,
        config_key: Optional[str] = None,
        invalid_value: Optional[Any] = None,
        expected_format: Optional[str] = None,
        **kwargs
    ):
        context = kwargs.get("context", {})
        context.update({
            "config_key": config_key,
            "invalid_value": invalid_value,
            "expected_format": expected_format
        })
        kwargs["context"] = context
        super().__init__(message, **kwargs)
        self.config_key = config_key
        self.invalid_value = invalid_value
        self.expected_format = expected_format


class AgentExecutionError(AgentError):
    """Raised when agent task execution fails"""
    
    def __init__(
        self,
        message: str,
        task_id: Optional[str] = None,
        execution_phase: Optional[str] = None,
        **kwargs
    ):
        context = kwargs.get("context", {})
        context.update({
            "task_id": task_id,
            "execution_phase": execution_phase
        })
        kwargs["context"] = context
        super().__init__(message, **kwargs)
        self.task_id = task_id
        self.execution_phase = execution_phase


class AgentCommunicationError(AgentError):
    """Raised when agent communication fails"""
    
    def __init__(
        self,
        message: str,
        communication_type: Optional[str] = None,
        target_agent: Optional[str] = None,
        **kwargs
    ):
        context = kwargs.get("context", {})
        context.update({
            "communication_type": communication_type,
            "target_agent": target_agent
        })
        kwargs["context"] = context
        super().__init__(message, **kwargs)
        self.communication_type = communication_type
        self.target_agent = target_agent


class AgentTimeoutError(AgentError):
    """Raised when agent operations time out"""
    
    def __init__(
        self,
        message: str,
        timeout_seconds: Optional[int] = None,
        operation: Optional[str] = None,
        **kwargs
    ):
        context = kwargs.get("context", {})
        context.update({
            "timeout_seconds": timeout_seconds,
            "operation": operation
        })
        kwargs["context"] = context
        super().__init__(message, **kwargs)
        self.timeout_seconds = timeout_seconds
        self.operation = operation


class AgentPoolError(AgentError):
    """Raised when agent pool operations fail"""
    
    def __init__(
        self,
        message: str,
        pool_type: Optional[str] = None,
        pool_size: Optional[int] = None,
        operation: Optional[str] = None,
        **kwargs
    ):
        context = kwargs.get("context", {})
        context.update({
            "pool_type": pool_type,
            "pool_size": pool_size,
            "operation": operation
        })
        kwargs["context"] = context
        super().__init__(message, **kwargs)
        self.pool_type = pool_type
        self.pool_size = pool_size
        self.operation = operation


class AgentNotFoundError(AgentError):
    """Raised when a requested agent is not found"""
    pass


class AgentUnavailableError(AgentError):
    """Raised when an agent is unavailable for task assignment"""
    
    def __init__(
        self,
        message: str,
        reason: Optional[str] = None,
        estimated_wait_time: Optional[int] = None,
        **kwargs
    ):
        context = kwargs.get("context", {})
        context.update({
            "reason": reason,
            "estimated_wait_time": estimated_wait_time
        })
        kwargs["context"] = context
        super().__init__(message, **kwargs)
        self.reason = reason
        self.estimated_wait_time = estimated_wait_time


class AgentResourceError(AgentError):
    """Raised when agent resource allocation fails"""
    
    def __init__(
        self,
        message: str,
        resource_type: Optional[str] = None,
        requested_amount: Optional[float] = None,
        available_amount: Optional[float] = None,
        **kwargs
    ):
        context = kwargs.get("context", {})
        context.update({
            "resource_type": resource_type,
            "requested_amount": requested_amount,
            "available_amount": available_amount
        })
        kwargs["context"] = context
        super().__init__(message, **kwargs)
        self.resource_type = resource_type
        self.requested_amount = requested_amount
        self.available_amount = available_amount


class AgentInstanceError(AgentError):
    """Raised when agent instance operations fail"""
    
    def __init__(
        self,
        message: str,
        instance_id: Optional[str] = None,
        instance_status: Optional[str] = None,
        operation: Optional[str] = None,
        **kwargs
    ):
        context = kwargs.get("context", {})
        context.update({
            "instance_id": instance_id,
            "instance_status": instance_status,
            "operation": operation
        })
        kwargs["context"] = context
        super().__init__(message, **kwargs)
        self.instance_id = instance_id
        self.instance_status = instance_status
        self.operation = operation