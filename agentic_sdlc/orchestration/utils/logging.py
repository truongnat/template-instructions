"""
Logging utilities for the Multi-Agent Orchestration System

This module provides structured logging capabilities with support for
different log levels, formatters, and output destinations.
"""

import logging
import logging.handlers
import json
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, Optional, Union
from contextlib import contextmanager

from ..config.settings import LoggingConfig
from ..config.environment import get_environment, get_log_level


class StructuredFormatter(logging.Formatter):
    """Custom formatter that outputs structured JSON logs"""
    
    def format(self, record: logging.LogRecord) -> str:
        # Create base log entry
        log_entry = {
            "timestamp": datetime.fromtimestamp(record.created).isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno
        }
        
        # Add exception info if present
        if record.exc_info:
            log_entry["exception"] = self.formatException(record.exc_info)
        
        # Add extra fields from the record
        extra_fields = {
            k: v for k, v in record.__dict__.items()
            if k not in {
                'name', 'msg', 'args', 'levelname', 'levelno', 'pathname',
                'filename', 'module', 'lineno', 'funcName', 'created',
                'msecs', 'relativeCreated', 'thread', 'threadName',
                'processName', 'process', 'getMessage', 'exc_info',
                'exc_text', 'stack_info'
            }
        }
        
        if extra_fields:
            log_entry["extra"] = extra_fields
        
        return json.dumps(log_entry, default=str)


class OrchestrationLogger:
    """Enhanced logger for orchestration system with structured logging"""
    
    def __init__(self, name: str, config: Optional[LoggingConfig] = None):
        self.name = name
        self.config = config or LoggingConfig()
        self._logger = logging.getLogger(name)
        self._setup_logger()
    
    def _setup_logger(self):
        """Setup the logger with appropriate handlers and formatters"""
        # Clear existing handlers
        self._logger.handlers.clear()
        
        # Set log level
        level = self.config.get_level_for_component(self.name)
        self._logger.setLevel(getattr(logging, level.upper()))
        
        # Console handler
        if self.config.enable_console:
            console_handler = logging.StreamHandler(sys.stdout)
            console_handler.setLevel(getattr(logging, level.upper()))
            
            # Use structured format for development, simple format for production
            if get_environment().value == "development":
                formatter = logging.Formatter(self.config.format)
            else:
                formatter = StructuredFormatter()
            
            console_handler.setFormatter(formatter)
            self._logger.addHandler(console_handler)
        
        # File handler
        if self.config.enable_file and self.config.file_path:
            file_path = Path(self.config.file_path)
            file_path.parent.mkdir(parents=True, exist_ok=True)
            
            file_handler = logging.handlers.RotatingFileHandler(
                file_path,
                maxBytes=self.config.max_file_size,
                backupCount=self.config.backup_count
            )
            file_handler.setLevel(getattr(logging, level.upper()))
            file_handler.setFormatter(StructuredFormatter())
            self._logger.addHandler(file_handler)
        
        # Prevent propagation to root logger
        self._logger.propagate = False
    
    def debug(self, message: str, **kwargs):
        """Log debug message with optional extra fields"""
        exc_info = kwargs.pop('exc_info', None)
        self._logger.debug(message, exc_info=exc_info, extra=kwargs)
    
    def info(self, message: str, **kwargs):
        """Log info message with optional extra fields"""
        exc_info = kwargs.pop('exc_info', None)
        self._logger.info(message, exc_info=exc_info, extra=kwargs)
    
    def warning(self, message: str, **kwargs):
        """Log warning message with optional extra fields"""
        exc_info = kwargs.pop('exc_info', None)
        self._logger.warning(message, exc_info=exc_info, extra=kwargs)
    
    def error(self, message: str, **kwargs):
        """Log error message with optional extra fields"""
        exc_info = kwargs.pop('exc_info', None)
        self._logger.error(message, exc_info=exc_info, extra=kwargs)
    
    def critical(self, message: str, **kwargs):
        """Log critical message with optional extra fields"""
        self._logger.critical(message, extra=kwargs)
    
    def exception(self, message: str, **kwargs):
        """Log exception with traceback"""
        self._logger.exception(message, extra=kwargs)
    
    @contextmanager
    def context(self, **context_fields):
        """Context manager that adds fields to all log messages within the context"""
        old_factory = logging.getLogRecordFactory()
        
        def record_factory(*args, **kwargs):
            record = old_factory(*args, **kwargs)
            for key, value in context_fields.items():
                setattr(record, key, value)
            return record
        
        logging.setLogRecordFactory(record_factory)
        try:
            yield self
        finally:
            logging.setLogRecordFactory(old_factory)


class LoggerMixin:
    """Mixin class that provides logging capabilities to other classes"""
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._logger = None
    
    @property
    def logger(self) -> OrchestrationLogger:
        """Get logger instance for this class"""
        if self._logger is None:
            class_name = self.__class__.__name__
            module_name = self.__class__.__module__
            logger_name = f"{module_name}.{class_name}"
            self._logger = get_logger(logger_name)
        return self._logger
    
    def log_operation(self, operation: str, **context):
        """Log an operation with context"""
        return self.logger.context(operation=operation, **context)


# Global logger registry
_loggers: Dict[str, OrchestrationLogger] = {}
_default_config: Optional[LoggingConfig] = None


def setup_logging(config: Optional[LoggingConfig] = None):
    """Setup global logging configuration"""
    global _default_config
    _default_config = config or LoggingConfig()
    
    # Clear existing loggers
    _loggers.clear()
    
    # Setup root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(getattr(logging, get_log_level()))


def configure_logging(config: Optional[LoggingConfig] = None):
    """Alias for setup_logging"""
    setup_logging(config)


def get_logger(name: str, config: Optional[LoggingConfig] = None) -> OrchestrationLogger:
    """Get or create a logger instance"""
    if name not in _loggers:
        effective_config = config or _default_config or LoggingConfig()
        _loggers[name] = OrchestrationLogger(name, effective_config)
    return _loggers[name]


class StructuredLogger:
    """Convenience class for structured logging with predefined fields"""
    
    def __init__(
        self,
        name: str,
        component: Optional[str] = None,
        workflow_id: Optional[str] = None,
        agent_id: Optional[str] = None
    ):
        self.logger = get_logger(name)
        self.default_context = {}
        
        if component:
            self.default_context["component"] = component
        if workflow_id:
            self.default_context["workflow_id"] = workflow_id
        if agent_id:
            self.default_context["agent_id"] = agent_id
    
    def _log(self, level: str, message: str, **kwargs):
        """Internal logging method that merges default context"""
        context = {**self.default_context, **kwargs}
        getattr(self.logger, level)(message, **context)
    
    def debug(self, message: str, **kwargs):
        self._log("debug", message, **kwargs)
    
    def info(self, message: str, **kwargs):
        self._log("info", message, **kwargs)
    
    def warning(self, message: str, **kwargs):
        self._log("warning", message, **kwargs)
    
    def error(self, message: str, **kwargs):
        self._log("error", message, **kwargs)
    
    def critical(self, message: str, **kwargs):
        self._log("critical", message, **kwargs)
    
    def exception(self, message: str, **kwargs):
        self._log("exception", message, **kwargs)
    
    def log_workflow_event(self, event: str, phase: str, **kwargs):
        """Log a workflow-specific event"""
        self.info(
            f"Workflow event: {event}",
            event=event,
            phase=phase,
            **kwargs
        )
    
    def log_agent_event(self, event: str, task_id: Optional[str] = None, **kwargs):
        """Log an agent-specific event"""
        context = {"event": event}
        if task_id:
            context["task_id"] = task_id
        context.update(kwargs)
        
        self.info(f"Agent event: {event}", **context)
    
    def log_performance_metric(self, metric_name: str, value: Union[int, float], unit: str = "", **kwargs):
        """Log a performance metric"""
        self.info(
            f"Performance metric: {metric_name}",
            metric_name=metric_name,
            metric_value=value,
            metric_unit=unit,
            **kwargs
        )
    
    def log_error_with_context(self, error: Exception, operation: str, **kwargs):
        """Log an error with full context"""
        self.error(
            f"Error in {operation}: {str(error)}",
            operation=operation,
            error_type=type(error).__name__,
            error_message=str(error),
            **kwargs
        )