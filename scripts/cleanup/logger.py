"""
Logging configuration for the Project Audit and Cleanup System.

This module sets up structured logging with appropriate formatters and handlers
for console and file output.
"""

import logging
import sys
from pathlib import Path
from datetime import datetime
from typing import Optional


class CleanupLogger:
    """Centralized logging configuration for the cleanup system."""
    
    _instance: Optional[logging.Logger] = None
    
    @classmethod
    def get_logger(cls, name: str = "cleanup", verbose: bool = False) -> logging.Logger:
        """Get or create the cleanup logger.
        
        Args:
            name: Logger name (default: "cleanup")
            verbose: Enable verbose (DEBUG) logging
            
        Returns:
            Configured logger instance
        """
        if cls._instance is None:
            cls._instance = cls._setup_logger(name, verbose)
        return cls._instance
    
    @classmethod
    def _setup_logger(cls, name: str, verbose: bool) -> logging.Logger:
        """Set up logger with console and file handlers.
        
        Args:
            name: Logger name
            verbose: Enable verbose logging
            
        Returns:
            Configured logger
        """
        logger = logging.getLogger(name)
        
        # Set level based on verbose flag
        level = logging.DEBUG if verbose else logging.INFO
        logger.setLevel(level)
        
        # Prevent duplicate handlers
        if logger.handlers:
            return logger
        
        # Console handler with colored output
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(level)
        console_formatter = logging.Formatter(
            '%(levelname)s: %(message)s'
        )
        console_handler.setFormatter(console_formatter)
        logger.addHandler(console_handler)
        
        # File handler for detailed logs
        try:
            log_dir = Path("logs")
            log_dir.mkdir(exist_ok=True)
            
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            log_file = log_dir / f"cleanup_{timestamp}.log"
            
            file_handler = logging.FileHandler(log_file)
            file_handler.setLevel(logging.DEBUG)  # Always DEBUG for file
            file_formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                datefmt='%Y-%m-%d %H:%M:%S'
            )
            file_handler.setFormatter(file_formatter)
            logger.addHandler(file_handler)
            logger.info(f"Logging initialized. Log file: {log_file}")
        except (PermissionError, FileNotFoundError) as e:
            logger.warning(f"Could not initialize file logging: {e}. Falling back to console-only logging.")
        
        return logger
    
    @classmethod
    def reset(cls):
        """Reset the logger instance (useful for testing)."""
        if cls._instance:
            for handler in cls._instance.handlers[:]:
                handler.close()
                cls._instance.removeHandler(handler)
        cls._instance = None


def get_logger(name: str = "cleanup", verbose: bool = False) -> logging.Logger:
    """Convenience function to get the cleanup logger.
    
    Args:
        name: Logger name (default: "cleanup")
        verbose: Enable verbose (DEBUG) logging
        
    Returns:
        Configured logger instance
        
    Example:
        >>> logger = get_logger(verbose=True)
        >>> logger.info("Starting cleanup operation")
        >>> logger.debug("Scanning directory: /path/to/dir")
    """
    return CleanupLogger.get_logger(name, verbose)
