"""Logging configuration for the Agentic SDLC SDK.

This module provides functions to configure logging for the SDK and get
module-specific loggers.
"""

import logging
from pathlib import Path
from typing import Optional


def setup_logging(
    level: str = "INFO",
    log_file: Optional[Path] = None,
    format_string: Optional[str] = None,
) -> None:
    """Configure SDK logging.

    Sets up logging for the entire SDK with the specified level, optional file output,
    and custom format. This function should be called once at SDK initialization.

    Args:
        level: Log level as string (DEBUG, INFO, WARNING, ERROR, CRITICAL).
               Defaults to INFO.
        log_file: Optional path to write logs to a file. If None, logs only go to stderr.
        format_string: Optional custom format string for log messages.
                      If None, uses default format with timestamp, logger name, level, and message.

    Raises:
        ValueError: If level is not a valid logging level.

    Example:
        >>> from agentic_sdlc.core.logging import setup_logging
        >>> setup_logging(level="DEBUG", log_file=Path("app.log"))
    """
    if format_string is None:
        format_string = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"

    # Validate log level
    try:
        log_level = getattr(logging, level.upper())
    except AttributeError:
        raise ValueError(
            f"Invalid log level: {level}. Must be one of: "
            "DEBUG, INFO, WARNING, ERROR, CRITICAL"
        )

    # Create handlers
    handlers: list[logging.Handler] = [logging.StreamHandler()]
    if log_file:
        handlers.append(logging.FileHandler(log_file))

    # Configure root logger
    logging.basicConfig(
        level=log_level,
        format=format_string,
        handlers=handlers,
        force=True,  # Override any existing configuration
    )


def get_logger(name: str) -> logging.Logger:
    """Get a logger for a specific module.

    Returns a logger instance with the module name prefixed with "agentic_sdlc.".
    This ensures all SDK loggers are grouped together in logging output.

    Args:
        name: Logger name, typically __name__ from the calling module.

    Returns:
        Configured logger instance for the module.

    Example:
        >>> from agentic_sdlc.core.logging import get_logger
        >>> logger = get_logger(__name__)
        >>> logger.info("Starting operation")
    """
    return logging.getLogger(f"agentic_sdlc.{name}")
