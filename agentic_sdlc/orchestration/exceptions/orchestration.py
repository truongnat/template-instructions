"""
Orchestration-specific exceptions for the Multi-Agent Orchestration System

This module defines exceptions related to workflow orchestration,
agent coordination, and task distribution.
"""


class OrchestrationError(Exception):
    """Base exception for orchestration-related errors"""
    pass


class WorkflowExecutionError(OrchestrationError):
    """Exception raised when workflow execution fails"""
    pass


class AgentCoordinationError(OrchestrationError):
    """Exception raised when agent coordination fails"""
    pass


class TaskDistributionError(OrchestrationError):
    """Exception raised when task distribution fails"""
    pass


class ExecutionTimeoutError(OrchestrationError):
    """Exception raised when execution times out"""
    pass


class ResourceAllocationError(OrchestrationError):
    """Exception raised when resource allocation fails"""
    pass


class DependencyResolutionError(OrchestrationError):
    """Exception raised when task dependencies cannot be resolved"""
    pass


class StateTransitionError(OrchestrationError):
    """Exception raised when invalid state transitions occur"""
    pass