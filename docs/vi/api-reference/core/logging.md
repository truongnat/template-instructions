# API Reference: agentic_sdlc.core.logging

**Phiên bản**: 3.0.0  
**Cập nhật lần cuối**: 11/02/2026


**Module:** `agentic_sdlc.core.logging`

**Phiên bản:** 3.0.0

**Cập nhật lần cuối:** 2024-01-01

---

## Tổng Quan

Logging configuration for the Agentic SDLC SDK.

This module provides functions to configure logging for the SDK and get
module-specific loggers.

---

## Functions

## Function `get_logger`

**Chữ ký (Signature):**

```python
get_logger(name: str) -> logging.Logger
```python

**Mô tả:**

Get a logger for a specific module.

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

**Tham số (Parameters):**

- `name` (str): Tham số name

**Giá trị trả về (Returns):**

- `Logger`: Giá trị trả về

**Ví dụ:**

```python
# Ví dụ sử dụng get_logger
from agentic_sdlc.core.logging import get_logger

result = get_logger()
```text

---

## Function `setup_logging`

**Chữ ký (Signature):**

```python
setup_logging(level: str = 'INFO', log_file: Optional[pathlib.Path] = None, format_string: Optional[str] = None) -> None
```python

**Mô tả:**

Configure SDK logging.

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

**Tham số (Parameters):**

- `level` (str), mặc định: `INFO`: Tham số level
- `log_file` (Optional): Tham số log_file
- `format_string` (Optional): Tham số format_string

**Giá trị trả về (Returns):**

- `None`: Giá trị trả về

**Ngoại lệ (Raises):**

- `ValueError`

**Ví dụ:**

```python
# Ví dụ sử dụng setup_logging
from agentic_sdlc.core.logging import setup_logging

result = setup_logging()
```

---
