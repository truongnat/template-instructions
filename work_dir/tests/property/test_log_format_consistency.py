"""
Property-based tests for Log Format Consistency.

These tests use Hypothesis to verify that all log entries follow a consistent
format across many randomly generated inputs.

Feature: sdlc-kit-improvements
Property 4: Log Format Consistency
Requirements: 5.5
"""

import pytest
import tempfile
import re
import uuid
from pathlib import Path
from datetime import datetime
from hypothesis import given, strategies as st, settings

from monitoring.loggers import SDLCLogger


# Strategy for generating log messages
log_messages = st.text(
    alphabet=st.characters(min_codepoint=32, max_codepoint=126),
    min_size=1,
    max_size=200
).filter(lambda x: x.strip() and '\n' not in x and '\r' not in x).map(lambda x: x.strip())

# Strategy for generating log levels
log_levels = st.sampled_from(['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL'])


# Feature: sdlc-kit-improvements, Property 4: Log Format Consistency
@given(
    message=log_messages,
    level=log_levels,
)
@settings(max_examples=10, deadline=None)
def test_log_format_has_required_components(message, level):
    """
    Property: For any log event, when it is logged through the Monitoring_System,
    the log entry should contain a timestamp, logger name, log level, and message
    in a consistent format.
    
    This property ensures that all log entries follow the standard format:
    {timestamp} - {logger_name} - {level} - {message}
    
    **Validates: Requirements 5.5**
    """
    # Use a unique logger name for each test run to avoid conflicts
    logger_name = f"test_logger_{uuid.uuid4().hex[:8]}"
    
    with tempfile.TemporaryDirectory() as tmpdir:
        # Override the log file location for this test
        log_file = Path(tmpdir) / "test.log"
        original_log_file = SDLCLogger._log_file
        original_log_dir = SDLCLogger._log_dir
        
        SDLCLogger._log_file = log_file
        SDLCLogger._log_dir = Path(tmpdir)
        
        try:
            # Get a logger and log a message
            logger = SDLCLogger.get_logger(logger_name, level=level)
            
            # Log at the specified level
            if level == 'DEBUG':
                logger.debug(message)
            elif level == 'INFO':
                logger.info(message)
            elif level == 'WARNING':
                logger.warning(message)
            elif level == 'ERROR':
                logger.error(message)
            elif level == 'CRITICAL':
                logger.critical(message)
            
            # Flush handlers to ensure log is written
            for handler in logger.handlers:
                handler.flush()
            
            # Read the log file
            assert log_file.exists(), "Log file should be created"
            
            with open(log_file, 'r') as f:
                log_content = f.read().strip()
            
            # Property: Log should contain an entry
            assert log_content, "Log file should contain an entry"
            
            # Get the last line (most recent log entry)
            log_lines = log_content.split('\n')
            last_log_entry = log_lines[-1]
            
            # Property: Log entry should follow the format: timestamp - logger_name - level - message
            # Expected format: YYYY-MM-DD HH:MM:SS,mmm - logger_name - LEVEL - message
            log_pattern = r'^(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2},\d{3}) - (.+?) - (DEBUG|INFO|WARNING|ERROR|CRITICAL) - (.+)$'
            
            match = re.match(log_pattern, last_log_entry)
            assert match is not None, (
                f"Log entry should match format 'timestamp - logger_name - level - message'. "
                f"Got: {last_log_entry}"
            )
            
            # Extract components
            timestamp_str, logged_name, logged_level, logged_message = match.groups()
            
            # Property: Timestamp should be parseable
            try:
                datetime.strptime(timestamp_str, '%Y-%m-%d %H:%M:%S,%f')
            except ValueError as e:
                pytest.fail(f"Timestamp should be valid: {e}")
            
            # Property: Logger name should match
            assert logged_name == logger_name, (
                f"Logger name should be '{logger_name}', got '{logged_name}'"
            )
            
            # Property: Log level should match
            assert logged_level == level, (
                f"Log level should be '{level}', got '{logged_level}'"
            )
            
            # Property: Message should match
            assert logged_message == message, (
                f"Message should be '{message}', got '{logged_message}'"
            )
            
        finally:
            # Restore original paths and clean up
            SDLCLogger._log_file = original_log_file
            SDLCLogger._log_dir = original_log_dir
            # Clean up the logger
            if logger_name in SDLCLogger._loggers:
                del SDLCLogger._loggers[logger_name]


# Feature: sdlc-kit-improvements, Property 4: Log Format Consistency
@given(
    messages=st.lists(
        st.tuples(log_messages, log_levels),
        min_size=1,
        max_size=10
    )
)
@settings(max_examples=10, deadline=None)
def test_multiple_log_entries_have_consistent_format(messages):
    """
    Property: For any sequence of log events from the same logger, when they
    are logged, all entries should follow the same consistent format.
    
    This property ensures format consistency across multiple log entries.
    
    **Validates: Requirements 5.5**
    """
    logger_name = f"test_logger_{uuid.uuid4().hex[:8]}"
    
    with tempfile.TemporaryDirectory() as tmpdir:
        log_file = Path(tmpdir) / "test.log"
        original_log_file = SDLCLogger._log_file
        original_log_dir = SDLCLogger._log_dir
        
        SDLCLogger._log_file = log_file
        SDLCLogger._log_dir = Path(tmpdir)
        
        try:
            logger = SDLCLogger.get_logger(logger_name, level='DEBUG')
            
            for message, level in messages:
                if level == 'DEBUG':
                    logger.debug(message)
                elif level == 'INFO':
                    logger.info(message)
                elif level == 'WARNING':
                    logger.warning(message)
                elif level == 'ERROR':
                    logger.error(message)
                elif level == 'CRITICAL':
                    logger.critical(message)
            
            for handler in logger.handlers:
                handler.flush()
            
            with open(log_file, 'r') as f:
                log_content = f.read().strip()
            
            log_lines = log_content.split('\n')
            assert len(log_lines) == len(messages)
            
            log_pattern = r'^(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2},\d{3}) - (.+?) - (DEBUG|INFO|WARNING|ERROR|CRITICAL) - (.+)$'
            
            for i, log_line in enumerate(log_lines):
                match = re.match(log_pattern, log_line)
                assert match is not None, f"Log entry {i} should match format. Got: {log_line}"
                
                timestamp_str, logged_name, logged_level, logged_message = match.groups()
                expected_message, expected_level = messages[i]
                
                assert logged_name == logger_name
                assert logged_level == expected_level
                assert logged_message == expected_message
        
        finally:
            SDLCLogger._log_file = original_log_file
            SDLCLogger._log_dir = original_log_dir
            if logger_name in SDLCLogger._loggers:
                del SDLCLogger._loggers[logger_name]


# Feature: sdlc-kit-improvements, Property 4: Log Format Consistency
@given(
    message=log_messages,
)
@settings(max_examples=10, deadline=None)
def test_all_log_levels_use_same_format(message):
    """
    Property: For any logger, when logging at different levels (DEBUG, INFO,
    WARNING, ERROR, CRITICAL), all entries should follow the same format
    with only the level field changing.
    
    This property ensures format consistency across all log levels.
    
    **Validates: Requirements 5.5**
    """
    logger_name = f"test_logger_{uuid.uuid4().hex[:8]}"
    
    with tempfile.TemporaryDirectory() as tmpdir:
        log_file = Path(tmpdir) / "test.log"
        original_log_file = SDLCLogger._log_file
        original_log_dir = SDLCLogger._log_dir
        
        SDLCLogger._log_file = log_file
        SDLCLogger._log_dir = Path(tmpdir)
        
        try:
            logger = SDLCLogger.get_logger(logger_name, level='DEBUG')
            
            logger.debug(message)
            logger.info(message)
            logger.warning(message)
            logger.error(message)
            logger.critical(message)
            
            for handler in logger.handlers:
                handler.flush()
            
            with open(log_file, 'r') as f:
                log_content = f.read().strip()
            
            log_lines = log_content.split('\n')
            assert len(log_lines) == 5
            
            log_pattern = r'^(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2},\d{3}) - (.+?) - (DEBUG|INFO|WARNING|ERROR|CRITICAL) - (.+)$'
            expected_levels = ['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL']
            
            for i, (log_line, expected_level) in enumerate(zip(log_lines, expected_levels)):
                match = re.match(log_pattern, log_line)
                assert match is not None
                
                timestamp_str, logged_name, logged_level, logged_message = match.groups()
                assert logged_name == logger_name
                assert logged_level == expected_level
                assert logged_message == message
        
        finally:
            SDLCLogger._log_file = original_log_file
            SDLCLogger._log_dir = original_log_dir
            if logger_name in SDLCLogger._loggers:
                del SDLCLogger._loggers[logger_name]
