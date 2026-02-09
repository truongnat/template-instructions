"""
Base exception classes for the Multi-Agent Orchestration System

This module defines the base exception classes that all other orchestration
exceptions inherit from.
"""

from typing import Optional, Dict, Any
from datetime import datetime


class OrchestrationError(Exception):
    """Base exception class for all orchestration system errors"""
    
    def __init__(
        self,
        message: str,
        error_code: Optional[str] = None,
        context: Optional[Dict[str, Any]] = None,
        cause: Optional[Exception] = None
    ):
        super().__init__(message)
        self.message = message
        self.error_code = error_code or self.__class__.__name__
        self.context = context or {}
        self.cause = cause
        self.timestamp = datetime.now()
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert exception to dictionary for serialization"""
        return {
            "error_type": self.__class__.__name__,
            "error_code": self.error_code,
            "message": self.message,
            "context": self.context,
            "timestamp": self.timestamp.isoformat(),
            "cause": str(self.cause) if self.cause else None
        }
    
    def __str__(self) -> str:
        base_msg = f"[{self.error_code}] {self.message}"
        if self.context:
            context_str = ", ".join(f"{k}={v}" for k, v in self.context.items())
            base_msg += f" (Context: {context_str})"
        if self.cause:
            base_msg += f" (Caused by: {self.cause})"
        return base_msg


class OrchestrationWarning(UserWarning):
    """Base warning class for orchestration system warnings"""
    
    def __init__(
        self,
        message: str,
        warning_code: Optional[str] = None,
        context: Optional[Dict[str, Any]] = None
    ):
        super().__init__(message)
        self.message = message
        self.warning_code = warning_code or self.__class__.__name__
        self.context = context or {}
        self.timestamp = datetime.now()
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert warning to dictionary for serialization"""
        return {
            "warning_type": self.__class__.__name__,
            "warning_code": self.warning_code,
            "message": self.message,
            "context": self.context,
            "timestamp": self.timestamp.isoformat()
        }
    
    def __str__(self) -> str:
        base_msg = f"[{self.warning_code}] {self.message}"
        if self.context:
            context_str = ", ".join(f"{k}={v}" for k, v in self.context.items())
            base_msg += f" (Context: {context_str})"
        return base_msg