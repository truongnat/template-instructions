"""Unit tests for the exception hierarchy.

Tests the AgenticSDLCError base exception and all specific exception classes.
"""

import pytest

from agentic_sdlc.core.exceptions import (
    AgenticSDLCError,
    AgentError,
    ConfigurationError,
    ModelError,
    PluginError,
    ValidationError,
    WorkflowError,
)


class TestAgenticSDLCError:
    """Tests for the base AgenticSDLCError exception."""

    def test_exception_creation_with_message_only(self) -> None:
        """Test creating exception with just a message."""
        exc = AgenticSDLCError("Test error")
        assert exc.message == "Test error"
        assert exc.context == {}
        assert str(exc) == "Test error"

    def test_exception_creation_with_context(self) -> None:
        """Test creating exception with message and context."""
        context = {"field": "value", "code": 42}
        exc = AgenticSDLCError("Test error", context=context)
        assert exc.message == "Test error"
        assert exc.context == context

    def test_exception_string_representation_with_context(self) -> None:
        """Test string representation includes context."""
        context = {"field": "value", "code": 42}
        exc = AgenticSDLCError("Test error", context=context)
        exc_str = str(exc)
        assert "Test error" in exc_str
        assert "field" in exc_str
        assert "value" in exc_str
        assert "code" in exc_str
        assert "42" in exc_str

    def test_exception_is_exception_subclass(self) -> None:
        """Test that AgenticSDLCError is an Exception."""
        exc = AgenticSDLCError("Test")
        assert isinstance(exc, Exception)

    def test_exception_can_be_raised_and_caught(self) -> None:
        """Test that exception can be raised and caught."""
        with pytest.raises(AgenticSDLCError) as exc_info:
            raise AgenticSDLCError("Test error")
        assert exc_info.value.message == "Test error"

    def test_exception_with_empty_context(self) -> None:
        """Test exception with explicitly empty context."""
        exc = AgenticSDLCError("Test error", context={})
        assert exc.context == {}
        assert str(exc) == "Test error"


class TestConfigurationError:
    """Tests for ConfigurationError exception."""

    def test_configuration_error_is_agentic_sdlc_error(self) -> None:
        """Test that ConfigurationError is a subclass of AgenticSDLCError."""
        exc = ConfigurationError("Config error")
        assert isinstance(exc, AgenticSDLCError)

    def test_configuration_error_with_context(self) -> None:
        """Test ConfigurationError with context."""
        context = {"path": "/config.yaml", "reason": "file not found"}
        exc = ConfigurationError("Failed to load config", context=context)
        assert exc.message == "Failed to load config"
        assert exc.context == context

    def test_configuration_error_can_be_caught_as_agentic_sdlc_error(self) -> None:
        """Test that ConfigurationError can be caught as AgenticSDLCError."""
        with pytest.raises(AgenticSDLCError):
            raise ConfigurationError("Config error")


class TestValidationError:
    """Tests for ValidationError exception."""

    def test_validation_error_is_agentic_sdlc_error(self) -> None:
        """Test that ValidationError is a subclass of AgenticSDLCError."""
        exc = ValidationError("Validation failed")
        assert isinstance(exc, AgenticSDLCError)

    def test_validation_error_with_context(self) -> None:
        """Test ValidationError with context."""
        context = {"field": "log_level", "value": "INVALID", "valid": ["DEBUG", "INFO"]}
        exc = ValidationError("Invalid log level", context=context)
        assert exc.message == "Invalid log level"
        assert exc.context == context


class TestPluginError:
    """Tests for PluginError exception."""

    def test_plugin_error_is_agentic_sdlc_error(self) -> None:
        """Test that PluginError is a subclass of AgenticSDLCError."""
        exc = PluginError("Plugin failed")
        assert isinstance(exc, AgenticSDLCError)

    def test_plugin_error_with_context(self) -> None:
        """Test PluginError with context."""
        context = {"plugin": "my_plugin", "error": "ImportError"}
        exc = PluginError("Failed to load plugin", context=context)
        assert exc.message == "Failed to load plugin"
        assert exc.context == context


class TestWorkflowError:
    """Tests for WorkflowError exception."""

    def test_workflow_error_is_agentic_sdlc_error(self) -> None:
        """Test that WorkflowError is a subclass of AgenticSDLCError."""
        exc = WorkflowError("Workflow failed")
        assert isinstance(exc, AgenticSDLCError)

    def test_workflow_error_with_context(self) -> None:
        """Test WorkflowError with context."""
        context = {"workflow": "my_workflow", "step": "step_1"}
        exc = WorkflowError("Workflow step failed", context=context)
        assert exc.message == "Workflow step failed"
        assert exc.context == context


class TestAgentError:
    """Tests for AgentError exception."""

    def test_agent_error_is_agentic_sdlc_error(self) -> None:
        """Test that AgentError is a subclass of AgenticSDLCError."""
        exc = AgentError("Agent failed")
        assert isinstance(exc, AgenticSDLCError)

    def test_agent_error_with_context(self) -> None:
        """Test AgentError with context."""
        context = {"agent": "my_agent", "action": "execute"}
        exc = AgentError("Agent execution failed", context=context)
        assert exc.message == "Agent execution failed"
        assert exc.context == context


class TestModelError:
    """Tests for ModelError exception."""

    def test_model_error_is_agentic_sdlc_error(self) -> None:
        """Test that ModelError is a subclass of AgenticSDLCError."""
        exc = ModelError("Model failed")
        assert isinstance(exc, AgenticSDLCError)

    def test_model_error_with_context(self) -> None:
        """Test ModelError with context."""
        context = {"model": "gpt-4", "provider": "openai"}
        exc = ModelError("Model API call failed", context=context)
        assert exc.message == "Model API call failed"
        assert exc.context == context


class TestExceptionHierarchy:
    """Tests for the overall exception hierarchy."""

    def test_all_specific_exceptions_are_agentic_sdlc_errors(self) -> None:
        """Test that all specific exceptions inherit from AgenticSDLCError."""
        exceptions = [
            ConfigurationError("test"),
            ValidationError("test"),
            PluginError("test"),
            WorkflowError("test"),
            AgentError("test"),
            ModelError("test"),
        ]
        for exc in exceptions:
            assert isinstance(exc, AgenticSDLCError)

    def test_catch_all_specific_exceptions_with_base_class(self) -> None:
        """Test that all specific exceptions can be caught with base class."""
        specific_exceptions = [
            ConfigurationError("config"),
            ValidationError("validation"),
            PluginError("plugin"),
            WorkflowError("workflow"),
            AgentError("agent"),
            ModelError("model"),
        ]

        for exc in specific_exceptions:
            with pytest.raises(AgenticSDLCError):
                raise exc

    def test_exception_inheritance_chain(self) -> None:
        """Test the inheritance chain of exceptions."""
        exc = ConfigurationError("test")
        assert isinstance(exc, ConfigurationError)
        assert isinstance(exc, AgenticSDLCError)
        assert isinstance(exc, Exception)
