"""Exception hierarchy for the Agentic SDLC SDK.

All SDK exceptions inherit from AgenticSDLCError, allowing users to catch
all SDK-specific errors with a single except clause.
"""

from typing import Any, Dict, Optional


class AgenticSDLCError(Exception):
    """Base exception for all SDK errors.

    This is the root exception class for all errors raised by the Agentic SDLC SDK.
    Users can catch this exception to handle any SDK-specific error.

    Attributes:
        message: The error message
        context: Optional dictionary with additional context about the error
    """

    def __init__(
        self, message: str, context: Optional[Dict[str, Any]] = None, **kwargs: Any
    ) -> None:
        """Initialize the exception.

        Args:
            message: The error message
            context: Optional dictionary with additional context (e.g., field names, values)
            **kwargs: Additional context fields to be merged into context
        """
        super().__init__(message)
        self.message = message
        self.context = context or {}
        if kwargs:
            self.context.update(kwargs)

    def __str__(self) -> str:
        """Return string representation of the exception."""
        if self.context:
            context_str = ", ".join(f"{k}={v!r}" for k, v in self.context.items())
            return f"{self.message} ({context_str})"
        return self.message


class ConfigurationError(AgenticSDLCError):
    """Raised when configuration is invalid or cannot be loaded.

    This exception is raised when:
    - Configuration file is missing or unreadable
    - Configuration format is invalid
    - Configuration values are out of range
    """

    pass


class ValidationError(AgenticSDLCError):
    """Raised when data validation fails.

    This exception is raised when:
    - Required fields are missing
    - Field values have wrong type
    - Field values fail validation rules
    """

    pass


class PluginError(AgenticSDLCError):
    """Raised when plugin operations fail.

    This exception is raised when:
    - Plugin fails to load or initialize
    - Plugin doesn't implement required interface
    - Plugin execution fails
    """

    pass


class WorkflowError(AgenticSDLCError):
    """Raised when workflow execution fails.

    This exception is raised when:
    - Workflow step fails
    - Workflow timeout occurs
    - Workflow validation fails
    """

    pass


class AgentError(AgenticSDLCError):
    """Raised when agent operations fail.

    This exception is raised when:
    - Agent creation fails
    - Agent execution fails
    - Agent configuration is invalid
    """

    pass


class ModelError(AgenticSDLCError):
    """Raised when model operations fail.

    This exception is raised when:
    - Model client initialization fails
    - Model API call fails
    - Model configuration is invalid
    """

    pass
