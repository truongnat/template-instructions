"""
Workflow-related exception classes for the Multi-Agent Orchestration System
"""

from typing import Optional, Dict, Any, List
from .base import OrchestrationError


class WorkflowError(OrchestrationError):
    """Base class for workflow-related errors"""
    pass


class WorkflowValidationError(WorkflowError):
    """Raised when workflow validation fails"""
    
    def __init__(
        self,
        message: str,
        validation_errors: Optional[List[str]] = None,
        workflow_id: Optional[str] = None,
        **kwargs
    ):
        context = kwargs.get("context", {})
        context.update({
            "workflow_id": workflow_id,
            "validation_errors": validation_errors or []
        })
        kwargs["context"] = context
        super().__init__(message, **kwargs)
        self.validation_errors = validation_errors or []
        self.workflow_id = workflow_id


class WorkflowExecutionError(WorkflowError):
    """Raised when workflow execution fails"""
    
    def __init__(
        self,
        message: str,
        workflow_id: Optional[str] = None,
        execution_id: Optional[str] = None,
        phase: Optional[str] = None,
        **kwargs
    ):
        context = kwargs.get("context", {})
        context.update({
            "workflow_id": workflow_id,
            "execution_id": execution_id,
            "phase": phase
        })
        kwargs["context"] = context
        super().__init__(message, **kwargs)
        self.workflow_id = workflow_id
        self.execution_id = execution_id
        self.phase = phase


class WorkflowTimeoutError(WorkflowError):
    """Raised when workflow execution times out"""
    
    def __init__(
        self,
        message: str,
        workflow_id: Optional[str] = None,
        execution_id: Optional[str] = None,
        timeout_seconds: Optional[int] = None,
        **kwargs
    ):
        context = kwargs.get("context", {})
        context.update({
            "workflow_id": workflow_id,
            "execution_id": execution_id,
            "timeout_seconds": timeout_seconds
        })
        kwargs["context"] = context
        super().__init__(message, **kwargs)
        self.workflow_id = workflow_id
        self.execution_id = execution_id
        self.timeout_seconds = timeout_seconds


class WorkflowStateError(WorkflowError):
    """Raised when workflow state is invalid or corrupted"""
    
    def __init__(
        self,
        message: str,
        workflow_id: Optional[str] = None,
        execution_id: Optional[str] = None,
        state_issues: Optional[List[str]] = None,
        **kwargs
    ):
        context = kwargs.get("context", {})
        context.update({
            "workflow_id": workflow_id,
            "execution_id": execution_id,
            "state_issues": state_issues or []
        })
        kwargs["context"] = context
        super().__init__(message, **kwargs)
        self.workflow_id = workflow_id
        self.execution_id = execution_id
        self.state_issues = state_issues or []


class WorkflowNotFoundError(WorkflowError):
    """Raised when a requested workflow is not found"""
    
    def __init__(
        self,
        message: str,
        workflow_id: Optional[str] = None,
        **kwargs
    ):
        context = kwargs.get("context", {})
        context.update({"workflow_id": workflow_id})
        kwargs["context"] = context
        super().__init__(message, **kwargs)
        self.workflow_id = workflow_id


class WorkflowConflictError(WorkflowError):
    """Raised when there's a conflict in workflow execution"""
    
    def __init__(
        self,
        message: str,
        workflow_id: Optional[str] = None,
        conflicting_workflows: Optional[List[str]] = None,
        **kwargs
    ):
        context = kwargs.get("context", {})
        context.update({
            "workflow_id": workflow_id,
            "conflicting_workflows": conflicting_workflows or []
        })
        kwargs["context"] = context
        super().__init__(message, **kwargs)
        self.workflow_id = workflow_id
        self.conflicting_workflows = conflicting_workflows or []


class WorkflowEngineError(WorkflowError):
    """Raised when workflow engine encounters an error"""
    
    def __init__(
        self,
        message: str,
        engine_id: Optional[str] = None,
        operation: Optional[str] = None,
        **kwargs
    ):
        context = kwargs.get("context", {})
        context.update({
            "engine_id": engine_id,
            "operation": operation
        })
        kwargs["context"] = context
        super().__init__(message, **kwargs)
        self.engine_id = engine_id
        self.operation = operation


class WorkflowMatchingError(WorkflowEngineError):
    """Raised when workflow matching fails"""
    
    def __init__(
        self,
        message: str,
        request_id: Optional[str] = None,
        engine_id: Optional[str] = None,
        **kwargs
    ):
        context = kwargs.get("context", {})
        context.update({
            "request_id": request_id,
            "engine_id": engine_id
        })
        kwargs["context"] = context
        super().__init__(message, engine_id=engine_id, operation="workflow_matching", **kwargs)
        self.request_id = request_id