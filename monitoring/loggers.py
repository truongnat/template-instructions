"""Centralized logging configuration for SDLC Kit.

This module provides a consistent logging interface across the entire system
with support for both console and file logging.
"""

import logging
import sys
from pathlib import Path
from typing import Optional


class SDLCLogger:
    """Centralized logging configuration for SDLC Kit.
    
    Provides configured logger instances with consistent formatting
    and support for both console and file output.
    """
    
    _loggers = {}
    _log_dir = Path("logs")
    _log_file = _log_dir / "sdlc-kit.log"
    _initialized = False
    
    @classmethod
    def _ensure_log_directory(cls) -> None:
        """Ensure the logs directory exists."""
        cls._log_dir.mkdir(parents=True, exist_ok=True)
    
    @classmethod
    def get_logger(cls, name: str, level: Optional[str] = None) -> logging.Logger:
        """Get a configured logger instance.
        
        Args:
            name: Logger name (typically module name)
            level: Optional log level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
                  Defaults to INFO if not specified
        
        Returns:
            Configured logger instance
        
        Example:
            >>> logger = SDLCLogger.get_logger(__name__)
            >>> logger.info("Application started")
        """
        # Return cached logger if it exists
        if name in cls._loggers:
            logger = cls._loggers[name]
            if level:
                logger.setLevel(getattr(logging, level.upper()))
            return logger
        
        # Create new logger
        logger = logging.getLogger(name)
        
        # Only configure handlers once per logger
        if not logger.handlers:
            # Ensure log directory exists
            cls._ensure_log_directory()
            
            # Create formatter with consistent format
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
            
            # Console handler (stdout)
            console_handler = logging.StreamHandler(sys.stdout)
            console_handler.setFormatter(formatter)
            logger.addHandler(console_handler)
            
            # File handler
            file_handler = logging.FileHandler(cls._log_file)
            file_handler.setFormatter(formatter)
            logger.addHandler(file_handler)
        
        # Set log level
        log_level = getattr(logging, level.upper()) if level else logging.INFO
        logger.setLevel(log_level)
        
        # Prevent propagation to root logger
        logger.propagate = False
        
        # Cache logger
        cls._loggers[name] = logger
        
        return logger
    
    @classmethod
    def set_global_level(cls, level: str) -> None:
        """Set log level for all existing loggers.
        
        Args:
            level: Log level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        """
        log_level = getattr(logging, level.upper())
        for logger in cls._loggers.values():
            logger.setLevel(log_level)
    
    @classmethod
    def clear_loggers(cls) -> None:
        """Clear all cached loggers. Useful for testing."""
        cls._loggers.clear()
