"""
CLI Interface Exceptions

This module defines custom exceptions for CLI interface operations
in the multi-agent orchestration system.
"""

from .base import OrchestrationError


class CLIError(OrchestrationError):
    """Base exception for CLI interface errors"""
    pass


class CLIProcessError(CLIError):
    """Exception raised for general CLI process errors"""
    
    def __init__(self, message: str, process_id: str = None, operation: str = None):
        super().__init__(message)
        self.process_id = process_id
        self.operation = operation


class CLITimeoutError(CLIError):
    """Exception raised when CLI operations timeout"""
    
    def __init__(self, message: str, process_id: str = None, timeout: float = None):
        super().__init__(message)
        self.process_id = process_id
        self.timeout = timeout


class CLICommunicationError(CLIError):
    """Exception raised when CLI communication fails"""
    
    def __init__(self, message: str, process_id: str = None, operation: str = None):
        super().__init__(message)
        self.process_id = process_id
        self.operation = operation


class ProcessSpawnError(CLIError):
    """Exception raised when process spawning fails"""
    
    def __init__(self, message: str, process_id: str = None, command: str = None):
        super().__init__(message)
        self.process_id = process_id
        self.command = command


class ProcessCommunicationError(CLIError):
    """Exception raised when process communication fails"""
    
    def __init__(self, message: str, process_id: str = None, operation: str = None):
        super().__init__(message)
        self.process_id = process_id
        self.operation = operation


class ProcessTerminationError(CLIError):
    """Exception raised when process termination fails"""
    
    def __init__(self, message: str, process_id: str = None, pid: int = None):
        super().__init__(message)
        self.process_id = process_id
        self.pid = pid


class ProcessNotFoundError(CLIError):
    """Exception raised when a process is not found"""
    
    def __init__(self, message: str, process_id: str = None):
        super().__init__(message)
        self.process_id = process_id


class ProcessTimeoutError(CLIError):
    """Exception raised when a process operation times out"""
    
    def __init__(self, message: str, process_id: str = None, timeout: float = None):
        super().__init__(message)
        self.process_id = process_id
        self.timeout = timeout


class ProcessCapacityError(CLIError):
    """Exception raised when process capacity limits are exceeded"""
    
    def __init__(self, message: str, current_count: int = None, max_count: int = None):
        super().__init__(message)
        self.current_count = current_count
        self.max_count = max_count