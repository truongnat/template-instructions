"""
State management exception classes for the Multi-Agent Orchestration System
"""

from typing import Optional, Dict, Any, List
from .base import OrchestrationError


class StateError(OrchestrationError):
    """Base class for state management errors"""
    
    def __init__(
        self,
        message: str,
        state_id: Optional[str] = None,
        state_type: Optional[str] = None,
        **kwargs
    ):
        context = kwargs.get("context", {})
        context.update({
            "state_id": state_id,
            "state_type": state_type
        })
        kwargs["context"] = context
        super().__init__(message, **kwargs)
        self.state_id = state_id
        self.state_type = state_type


class StateCorruptionError(StateError):
    """Raised when state data is corrupted or invalid"""
    
    def __init__(
        self,
        message: str,
        corruption_details: Optional[List[str]] = None,
        last_valid_checkpoint: Optional[str] = None,
        **kwargs
    ):
        context = kwargs.get("context", {})
        context.update({
            "corruption_details": corruption_details or [],
            "last_valid_checkpoint": last_valid_checkpoint
        })
        kwargs["context"] = context
        super().__init__(message, **kwargs)
        self.corruption_details = corruption_details or []
        self.last_valid_checkpoint = last_valid_checkpoint


class StatePersistenceError(StateError):
    """Raised when state persistence operations fail"""
    
    def __init__(
        self,
        message: str,
        operation: Optional[str] = None,
        storage_backend: Optional[str] = None,
        **kwargs
    ):
        context = kwargs.get("context", {})
        context.update({
            "operation": operation,
            "storage_backend": storage_backend
        })
        kwargs["context"] = context
        super().__init__(message, **kwargs)
        self.operation = operation
        self.storage_backend = storage_backend


class StateRecoveryError(StateError):
    """Raised when state recovery operations fail"""
    
    def __init__(
        self,
        message: str,
        recovery_attempt: Optional[int] = None,
        available_checkpoints: Optional[List[str]] = None,
        **kwargs
    ):
        context = kwargs.get("context", {})
        context.update({
            "recovery_attempt": recovery_attempt,
            "available_checkpoints": available_checkpoints or []
        })
        kwargs["context"] = context
        super().__init__(message, **kwargs)
        self.recovery_attempt = recovery_attempt
        self.available_checkpoints = available_checkpoints or []


class StateNotFoundError(StateError):
    """Raised when requested state is not found"""
    pass


class StateVersionMismatchError(StateError):
    """Raised when state version is incompatible"""
    
    def __init__(
        self,
        message: str,
        current_version: Optional[str] = None,
        expected_version: Optional[str] = None,
        **kwargs
    ):
        context = kwargs.get("context", {})
        context.update({
            "current_version": current_version,
            "expected_version": expected_version
        })
        kwargs["context"] = context
        super().__init__(message, **kwargs)
        self.current_version = current_version
        self.expected_version = expected_version


class StateLockError(StateError):
    """Raised when state locking operations fail"""
    
    def __init__(
        self,
        message: str,
        lock_holder: Optional[str] = None,
        lock_timeout: Optional[int] = None,
        **kwargs
    ):
        context = kwargs.get("context", {})
        context.update({
            "lock_holder": lock_holder,
            "lock_timeout": lock_timeout
        })
        kwargs["context"] = context
        super().__init__(message, **kwargs)
        self.lock_holder = lock_holder
        self.lock_timeout = lock_timeout