"""Unit tests for the logging configuration module.

Tests the setup_logging and get_logger functions.
"""

import logging
import tempfile
from pathlib import Path

import pytest

from agentic_sdlc.core.logging import get_logger, setup_logging


class TestSetupLogging:
    """Tests for the setup_logging function."""

    def test_setup_logging_with_default_parameters(self) -> None:
        """Test setup_logging with default parameters."""
        # Clear existing handlers
        root_logger = logging.getLogger()
        for handler in root_logger.handlers[:]:
            root_logger.removeHandler(handler)

        setup_logging()

        # Verify logging is configured
        assert root_logger.level == logging.INFO
        assert len(root_logger.handlers) > 0

    def test_setup_logging_with_debug_level(self) -> None:
        """Test setup_logging with DEBUG level."""
        root_logger = logging.getLogger()
        for handler in root_logger.handlers[:]:
            root_logger.removeHandler(handler)

        setup_logging(level="DEBUG")

        assert root_logger.level == logging.DEBUG

    def test_setup_logging_with_error_level(self) -> None:
        """Test setup_logging with ERROR level."""
        root_logger = logging.getLogger()
        for handler in root_logger.handlers[:]:
            root_logger.removeHandler(handler)

        setup_logging(level="ERROR")

        assert root_logger.level == logging.ERROR

    def test_setup_logging_with_file_output(self) -> None:
        """Test setup_logging with file output."""
        root_logger = logging.getLogger()
        for handler in root_logger.handlers[:]:
            root_logger.removeHandler(handler)

        with tempfile.TemporaryDirectory() as tmpdir:
            log_file = Path(tmpdir) / "test.log"
            setup_logging(log_file=log_file)

            # Verify file handler was added
            file_handlers = [
                h for h in root_logger.handlers if isinstance(h, logging.FileHandler)
            ]
            assert len(file_handlers) > 0

    def test_setup_logging_with_custom_format(self) -> None:
        """Test setup_logging with custom format string."""
        root_logger = logging.getLogger()
        for handler in root_logger.handlers[:]:
            root_logger.removeHandler(handler)

        custom_format = "%(levelname)s - %(message)s"
        setup_logging(format_string=custom_format)

        # Verify format was applied
        for handler in root_logger.handlers:
            if handler.formatter:
                assert handler.formatter._fmt == custom_format

    def test_setup_logging_with_invalid_level_raises_error(self) -> None:
        """Test that invalid log level raises ValueError."""
        with pytest.raises(ValueError) as exc_info:
            setup_logging(level="INVALID")

        assert "Invalid log level" in str(exc_info.value)
        assert "INVALID" in str(exc_info.value)

    def test_setup_logging_case_insensitive_level(self) -> None:
        """Test that log level is case insensitive."""
        root_logger = logging.getLogger()
        for handler in root_logger.handlers[:]:
            root_logger.removeHandler(handler)

        setup_logging(level="debug")
        assert root_logger.level == logging.DEBUG

        for handler in root_logger.handlers[:]:
            root_logger.removeHandler(handler)

        setup_logging(level="WARNING")
        assert root_logger.level == logging.WARNING

    def test_setup_logging_all_valid_levels(self) -> None:
        """Test setup_logging with all valid log levels."""
        root_logger = logging.getLogger()
        valid_levels = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]

        for level in valid_levels:
            for handler in root_logger.handlers[:]:
                root_logger.removeHandler(handler)

            setup_logging(level=level)
            assert root_logger.level == getattr(logging, level)


class TestGetLogger:
    """Tests for the get_logger function."""

    def test_get_logger_returns_logger(self) -> None:
        """Test that get_logger returns a Logger instance."""
        logger = get_logger("test_module")
        assert isinstance(logger, logging.Logger)

    def test_get_logger_prefixes_name(self) -> None:
        """Test that get_logger prefixes the name with 'agentic_sdlc.'."""
        logger = get_logger("test_module")
        assert logger.name == "agentic_sdlc.test_module"

    def test_get_logger_with_dunder_name(self) -> None:
        """Test get_logger with __name__ style input."""
        logger = get_logger("agentic_sdlc.core.config")
        assert logger.name == "agentic_sdlc.agentic_sdlc.core.config"

    def test_get_logger_returns_same_instance(self) -> None:
        """Test that calling get_logger twice returns the same instance."""
        logger1 = get_logger("test_module")
        logger2 = get_logger("test_module")
        assert logger1 is logger2

    def test_get_logger_different_names_different_instances(self) -> None:
        """Test that different names return different logger instances."""
        logger1 = get_logger("module1")
        logger2 = get_logger("module2")
        assert logger1 is not logger2
        assert logger1.name != logger2.name

    def test_get_logger_can_log_messages(self) -> None:
        """Test that returned logger can log messages."""
        logger = get_logger("test_module")

        # This should not raise an exception
        logger.debug("Debug message")
        logger.info("Info message")
        logger.warning("Warning message")
        logger.error("Error message")

    def test_get_logger_with_empty_string(self) -> None:
        """Test get_logger with empty string."""
        logger = get_logger("")
        assert logger.name == "agentic_sdlc."

    def test_get_logger_with_nested_module_name(self) -> None:
        """Test get_logger with nested module names."""
        logger = get_logger("infrastructure.automation.engine")
        assert logger.name == "agentic_sdlc.infrastructure.automation.engine"
