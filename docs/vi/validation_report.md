# Documentation Validation Report

## Summary

- Files with issues: 62
- Errors: 343
- Warnings: 416
- Info: 100

## Issues by File

### CONTRIBUTING.md

⚠️ **heading_hierarchy**: Heading hierarchy skip detected: 'Use Case Template' (level 4 after level 2)
⚠️ **heading_hierarchy**: Heading hierarchy skip detected: 'Code Example Template' (level 4 after level 2)
⚠️ **heading_hierarchy**: Heading hierarchy skip detected: '3. Style Guide và Formatting Rules' (level 3 after level 1)
⚠️ **heading_hierarchy**: Heading hierarchy skip detected: 'Validate Code Examples' (level 4 after level 1)
⚠️ **heading_hierarchy**: Heading hierarchy skip detected: 'Validate Cross-References' (level 4 after level 1)
⚠️ **heading_hierarchy**: Heading hierarchy skip detected: '6. Submission Process' (level 3 after level 1)
❌ **syntax_error** (line 109): Python syntax error in code block: invalid syntax

### README.md

⚠️ **heading_hierarchy**: Heading hierarchy skip detected: 'Code Snippets Cơ Bản' (level 3 after level 1)
⚠️ **language_consistency**: Document in vi/ directory should contain Vietnamese content
ℹ️ **missing_translation**: Technical term 'Agent' appears frequently without Vietnamese explanation
ℹ️ **missing_translation**: Technical term 'Workflow' appears frequently without Vietnamese explanation
ℹ️ **missing_translation**: Technical term 'Plugin' appears frequently without Vietnamese explanation
ℹ️ **missing_translation**: Technical term 'CLI' appears frequently without Vietnamese explanation
ℹ️ **missing_translation**: Technical term 'API' appears frequently without Vietnamese explanation
❌ **broken_link** (line 88): Broken link to 'getting-started/quick-start.md' (text: 'Quick Start')
❌ **broken_link** (line 90): Broken link to 'getting-started/first-workflow.md' (text: 'Workflow Đầu Tiên')
❌ **broken_link** (line 204): Broken link to 'api-reference/orchestration/model-client.md' (text: 'ModelClient API')

### api-reference/README.md

❌ **missing_module_path**: API reference missing module path
⚠️ **language_consistency**: Document in vi/ directory should contain Vietnamese content
ℹ️ **missing_translation**: Technical term 'API' appears frequently without Vietnamese explanation

### api-reference/core/config.md

❌ **missing_module_path**: API reference missing module path
⚠️ **empty_section**: Section 'Tổng Quan

Configuration management for the SDK.

This module provides the Config class for loading, managing, and validating
SDK configuration from multiple sources (files, environment variables, defaults).

---

## Classes

## Class `Config`

**Mô tả:**

Central configuration management for the SDK.

Loads configuration from multiple sources with proper precedence:
1. Defaults (lowest priority)
2. Configuration file (YAML or JSON)
3. Environment variables
4. Programmatic API calls (highest priority)

Supports dot notation for accessing nested values (e.g., "models.openai.temperature").

### Constructor

#### `__init__`

**Chữ ký (Signature):**

```python
__init__(self, config_path: Union[str, pathlib.Path, NoneType] = None) -> None
```text

**Mô tả:**

Initialize configuration.

Args:
    config_path: Optional path to configuration file (YAML or JSON)
    
Raises:
    ConfigurationError: If configuration file cannot be loaded
    ValidationError: If configuration is invalid

**Tham số (Parameters):**

- `config_path` (Union): Tham số config_path

**Giá trị trả về (Returns):**

- `None`: Giá trị trả về

**Ngoại lệ (Raises):**

- `ConfigurationError`

### Methods

#### `get`

**Chữ ký (Signature):**

```python
get(self, key: str, default: Any = None) -> Any
```text

**Mô tả:**

Get configuration value with dot notation support.

Args:
    key: Configuration key (supports dot notation, e.g., "models.openai.temperature")
    default: Default value if key not found
    
Returns:
    Configuration value or default

**Tham số (Parameters):**

- `key` (str): Tham số key
- `default` (Any): Tham số default

**Giá trị trả về (Returns):**

- `Any`: Giá trị trả về

#### `merge`

**Chữ ký (Signature):**

```python
merge(self, other: Dict[str, Any]) -> None
```text

**Mô tả:**

Merge additional configuration with proper precedence.

User-provided values override defaults. Merging is idempotent.

Args:
    other: Configuration dictionary to merge
    
Raises:
    ValidationError: If merged configuration is invalid

**Tham số (Parameters):**

- `other` (Dict): Tham số other

**Giá trị trả về (Returns):**

- `None`: Giá trị trả về

**Ngoại lệ (Raises):**

- `ValidationError`

#### `set`

**Chữ ký (Signature):**

```python
set(self, key: str, value: Any) -> None
```text

**Mô tả:**

Set configuration value with validation.

Args:
    key: Configuration key (supports dot notation)
    value: Value to set
    
Raises:
    ValidationError: If value is invalid

**Tham số (Parameters):**

- `key` (str): Tham số key
- `value` (Any): Tham số value

**Giá trị trả về (Returns):**

- `None`: Giá trị trả về

**Ngoại lệ (Raises):**

- `ValidationError`

#### `to_dict`

**Chữ ký (Signature):**

```python
to_dict(self) -> Dict[str, Any]
```text

**Mô tả:**

Get configuration as dictionary.

Returns:
    Configuration dictionary

**Giá trị trả về (Returns):**

- `Dict`: Giá trị trả về

#### `validate`

**Chữ ký (Signature):**

```python
validate(self) -> None
```text

**Mô tả:**

Validate entire configuration against schema.

Raises:
    ValidationError: If configuration is invalid

**Giá trị trả về (Returns):**

- `None`: Giá trị trả về

**Ngoại lệ (Raises):**

- `ValidationError`

### Ví dụ sử dụng

**Ví dụ cơ bản sử dụng Config**

```python
# Ví dụ sử dụng Config
from agentic_sdlc.core.config import Config

# Tạo instance
obj = Config()
```text

---

## Functions

## Function `get_config`

**Chữ ký (Signature):**

```python
get_config(config_path: Union[str, pathlib.Path, NoneType] = None) -> agentic_sdlc.core.config.Config
```text

**Mô tả:**

Get configuration instance (alias for load_config).

Args:
    config_path: Optional path to configuration file
    
Returns:
    Config instance

**Tham số (Parameters):**

- `config_path` (Union): Tham số config_path

**Giá trị trả về (Returns):**

- `Config`: Giá trị trả về

**Ví dụ:**

```python
# Ví dụ sử dụng get_config
from agentic_sdlc.core.config import get_config

result = get_config()
```text

---

## Function `load_config`

**Chữ ký (Signature):**

```python
load_config(config_path: Union[str, pathlib.Path, NoneType] = None) -> agentic_sdlc.core.config.Config
```text

**Mô tả:**

Load configuration from file or defaults.

Args:
    config_path: Optional path to configuration file
    
Returns:
    Loaded Config instance
    
Raises:
    ConfigurationError: If configuration cannot be loaded
    ValidationError: If configuration is invalid

**Tham số (Parameters):**

- `config_path` (Union): Tham số config_path

**Giá trị trả về (Returns):**

- `Config`: Giá trị trả về

**Ngoại lệ (Raises):**

- `ConfigurationError`

**Ví dụ:**

```python
# Ví dụ sử dụng load_config
from agentic_sdlc.core.config import load_config

result = load_config()
```' has insufficient content
⚠️ **language_consistency**: Document in vi/ directory should contain Vietnamese content
❌ **syntax_error** (line 47): Python syntax error in code block: invalid syntax
❌ **syntax_error** (line 80): Python syntax error in code block: invalid syntax
❌ **syntax_error** (line 108): Python syntax error in code block: invalid syntax
❌ **syntax_error** (line 140): Python syntax error in code block: invalid syntax
❌ **syntax_error** (line 172): Python syntax error in code block: invalid syntax
❌ **syntax_error** (line 191): Python syntax error in code block: invalid syntax
❌ **syntax_error** (line 230): Python syntax error in code block: invalid syntax
❌ **syntax_error** (line 267): Python syntax error in code block: invalid syntax

### api-reference/core/exceptions.md

❌ **missing_module_path**: API reference missing module path
⚠️ **empty_section**: Section 'Tổng Quan

Exception hierarchy for the Agentic SDLC SDK.

All SDK exceptions inherit from AgenticSDLCError, allowing users to catch
all SDK-specific errors with a single except clause.

---

## Classes

## Class `AgentError`

**Mô tả:**

Raised when agent operations fail.

This exception is raised when:
- Agent creation fails
- Agent execution fails
- Agent configuration is invalid

### Constructor

#### `__init__`

**Chữ ký (Signature):**

```python
__init__(self, message: str, context: Optional[Dict[str, Any]] = None) -> None
```text

**Mô tả:**

Initialize the exception.

Args:
    message: The error message
    context: Optional dictionary with additional context (e.g., field names, values)

**Tham số (Parameters):**

- `message` (str): Tham số message
- `context` (Optional): Tham số context

**Giá trị trả về (Returns):**

- `None`: Giá trị trả về

### Methods

#### `__str__`

**Chữ ký (Signature):**

```python
__str__(self) -> str
```text

**Mô tả:**

Return string representation of the exception.

**Giá trị trả về (Returns):**

- `str`: Giá trị trả về

### Ví dụ sử dụng

**Ví dụ cơ bản sử dụng AgentError**

```python
# Ví dụ sử dụng AgentError
from agentic_sdlc.core.exceptions import AgentError

# Tạo instance
obj = AgentError()
```python

---

## Class `AgenticSDLCError`

**Mô tả:**

Base exception for all SDK errors.

This is the root exception class for all errors raised by the Agentic SDLC SDK.
Users can catch this exception to handle any SDK-specific error.

Attributes:
    message: The error message
    context: Optional dictionary with additional context about the error

### Constructor

#### `__init__`

**Chữ ký (Signature):**

```python
__init__(self, message: str, context: Optional[Dict[str, Any]] = None) -> None
```text

**Mô tả:**

Initialize the exception.

Args:
    message: The error message
    context: Optional dictionary with additional context (e.g., field names, values)

**Tham số (Parameters):**

- `message` (str): Tham số message
- `context` (Optional): Tham số context

**Giá trị trả về (Returns):**

- `None`: Giá trị trả về

### Methods

#### `__str__`

**Chữ ký (Signature):**

```python
__str__(self) -> str
```text

**Mô tả:**

Return string representation of the exception.

**Giá trị trả về (Returns):**

- `str`: Giá trị trả về

### Ví dụ sử dụng

**Ví dụ cơ bản sử dụng AgenticSDLCError**

```python
# Ví dụ sử dụng AgenticSDLCError
from agentic_sdlc.core.exceptions import AgenticSDLCError

# Tạo instance
obj = AgenticSDLCError()
```text

---

## Class `ConfigurationError`

**Mô tả:**

Raised when configuration is invalid or cannot be loaded.

This exception is raised when:
- Configuration file is missing or unreadable
- Configuration format is invalid
- Configuration values are out of range

### Constructor

#### `__init__`

**Chữ ký (Signature):**

```python
__init__(self, message: str, context: Optional[Dict[str, Any]] = None) -> None
```text

**Mô tả:**

Initialize the exception.

Args:
    message: The error message
    context: Optional dictionary with additional context (e.g., field names, values)

**Tham số (Parameters):**

- `message` (str): Tham số message
- `context` (Optional): Tham số context

**Giá trị trả về (Returns):**

- `None`: Giá trị trả về

### Methods

#### `__str__`

**Chữ ký (Signature):**

```python
__str__(self) -> str
```text

**Mô tả:**

Return string representation of the exception.

**Giá trị trả về (Returns):**

- `str`: Giá trị trả về

### Ví dụ sử dụng

**Ví dụ cơ bản sử dụng ConfigurationError**

```python
# Ví dụ sử dụng ConfigurationError
from agentic_sdlc.core.exceptions import ConfigurationError

# Tạo instance
obj = ConfigurationError()
```text

---

## Class `ModelError`

**Mô tả:**

Raised when model operations fail.

This exception is raised when:
- Model client initialization fails
- Model API call fails
- Model configuration is invalid

### Constructor

#### `__init__`

**Chữ ký (Signature):**

```python
__init__(self, message: str, context: Optional[Dict[str, Any]] = None) -> None
```text

**Mô tả:**

Initialize the exception.

Args:
    message: The error message
    context: Optional dictionary with additional context (e.g., field names, values)

**Tham số (Parameters):**

- `message` (str): Tham số message
- `context` (Optional): Tham số context

**Giá trị trả về (Returns):**

- `None`: Giá trị trả về

### Methods

#### `__str__`

**Chữ ký (Signature):**

```python
__str__(self) -> str
```text

**Mô tả:**

Return string representation of the exception.

**Giá trị trả về (Returns):**

- `str`: Giá trị trả về

### Ví dụ sử dụng

**Ví dụ cơ bản sử dụng ModelError**

```python
# Ví dụ sử dụng ModelError
from agentic_sdlc.core.exceptions import ModelError

# Tạo instance
obj = ModelError()
```text

---

## Class `PluginError`

**Mô tả:**

Raised when plugin operations fail.

This exception is raised when:
- Plugin fails to load or initialize
- Plugin doesn't implement required interface
- Plugin execution fails

### Constructor

#### `__init__`

**Chữ ký (Signature):**

```python
__init__(self, message: str, context: Optional[Dict[str, Any]] = None) -> None
```text

**Mô tả:**

Initialize the exception.

Args:
    message: The error message
    context: Optional dictionary with additional context (e.g., field names, values)

**Tham số (Parameters):**

- `message` (str): Tham số message
- `context` (Optional): Tham số context

**Giá trị trả về (Returns):**

- `None`: Giá trị trả về

### Methods

#### `__str__`

**Chữ ký (Signature):**

```python
__str__(self) -> str
```text

**Mô tả:**

Return string representation of the exception.

**Giá trị trả về (Returns):**

- `str`: Giá trị trả về

### Ví dụ sử dụng

**Ví dụ cơ bản sử dụng PluginError**

```python
# Ví dụ sử dụng PluginError
from agentic_sdlc.core.exceptions import PluginError

# Tạo instance
obj = PluginError()
```text

---

## Class `ValidationError`

**Mô tả:**

Raised when data validation fails.

This exception is raised when:
- Required fields are missing
- Field values have wrong type
- Field values fail validation rules

### Constructor

#### `__init__`

**Chữ ký (Signature):**

```python
__init__(self, message: str, context: Optional[Dict[str, Any]] = None) -> None
```text

**Mô tả:**

Initialize the exception.

Args:
    message: The error message
    context: Optional dictionary with additional context (e.g., field names, values)

**Tham số (Parameters):**

- `message` (str): Tham số message
- `context` (Optional): Tham số context

**Giá trị trả về (Returns):**

- `None`: Giá trị trả về

### Methods

#### `__str__`

**Chữ ký (Signature):**

```python
__str__(self) -> str
```text

**Mô tả:**

Return string representation of the exception.

**Giá trị trả về (Returns):**

- `str`: Giá trị trả về

### Ví dụ sử dụng

**Ví dụ cơ bản sử dụng ValidationError**

```python
# Ví dụ sử dụng ValidationError
from agentic_sdlc.core.exceptions import ValidationError

# Tạo instance
obj = ValidationError()
```text

---

## Class `WorkflowError`

**Mô tả:**

Raised when workflow execution fails.

This exception is raised when:
- Workflow step fails
- Workflow timeout occurs
- Workflow validation fails

### Constructor

#### `__init__`

**Chữ ký (Signature):**

```python
__init__(self, message: str, context: Optional[Dict[str, Any]] = None) -> None
```text

**Mô tả:**

Initialize the exception.

Args:
    message: The error message
    context: Optional dictionary with additional context (e.g., field names, values)

**Tham số (Parameters):**

- `message` (str): Tham số message
- `context` (Optional): Tham số context

**Giá trị trả về (Returns):**

- `None`: Giá trị trả về

### Methods

#### `__str__`

**Chữ ký (Signature):**

```python
__str__(self) -> str
```text

**Mô tả:**

Return string representation of the exception.

**Giá trị trả về (Returns):**

- `str`: Giá trị trả về

### Ví dụ sử dụng

**Ví dụ cơ bản sử dụng WorkflowError**

```python
# Ví dụ sử dụng WorkflowError
from agentic_sdlc.core.exceptions import WorkflowError

# Tạo instance
obj = WorkflowError()
```' has insufficient content
⚠️ **language_consistency**: Document in vi/ directory should contain Vietnamese content
ℹ️ **missing_translation**: Technical term 'SDK' appears frequently without Vietnamese explanation
❌ **syntax_error** (line 44): Python syntax error in code block: invalid syntax
❌ **syntax_error** (line 71): Python syntax error in code block: invalid syntax
❌ **syntax_error** (line 116): Python syntax error in code block: invalid syntax
❌ **syntax_error** (line 143): Python syntax error in code block: invalid syntax
❌ **syntax_error** (line 186): Python syntax error in code block: invalid syntax
❌ **syntax_error** (line 213): Python syntax error in code block: invalid syntax
❌ **syntax_error** (line 256): Python syntax error in code block: invalid syntax
❌ **syntax_error** (line 283): Python syntax error in code block: invalid syntax
❌ **syntax_error** (line 326): Python syntax error in code block: invalid syntax
❌ **syntax_error** (line 353): Python syntax error in code block: invalid syntax
❌ **syntax_error** (line 396): Python syntax error in code block: invalid syntax
❌ **syntax_error** (line 423): Python syntax error in code block: invalid syntax
❌ **syntax_error** (line 466): Python syntax error in code block: invalid syntax
❌ **syntax_error** (line 493): Python syntax error in code block: invalid syntax

### api-reference/core/logging.md

❌ **missing_module_path**: API reference missing module path
⚠️ **empty_section**: Section 'Tổng Quan

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
```' has insufficient content
⚠️ **language_consistency**: Document in vi/ directory should contain Vietnamese content
ℹ️ **missing_translation**: Technical term 'SDK' appears frequently without Vietnamese explanation
❌ **syntax_error** (line 31): Python syntax error in code block: invalid syntax
❌ **syntax_error** (line 76): Python syntax error in code block: invalid syntax

### api-reference/infrastructure/execution_engine.md

❌ **missing_module_path**: API reference missing module path
⚠️ **empty_section**: Section 'Tổng Quan

Execution engine for running tasks.

---

## Classes

## Class `ExecutionEngine`

**Mô tả:**

Engine for executing multiple tasks.

The ExecutionEngine manages the execution of multiple tasks,
handling dependencies, parallelization, and error handling.

### Constructor

#### `__init__`

**Chữ ký (Signature):**

```python
__init__(self) -> None
```text

**Mô tả:**

Initialize the execution engine.

**Giá trị trả về (Returns):**

- `None`: Giá trị trả về

### Methods

#### `add_task`

**Chữ ký (Signature):**

```python
add_task(self, task: agentic_sdlc.infrastructure.engine.execution_engine.Task) -> None
```text

**Mô tả:**

Add a task to the engine.

Args:
    task: The task to add.

**Tham số (Parameters):**

- `task` (Task): Tham số task

**Giá trị trả về (Returns):**

- `None`: Giá trị trả về

#### `execute`

**Chữ ký (Signature):**

```python
execute(self) -> Dict[str, Any]
```text

**Mô tả:**

Execute all tasks.

Returns:
    Dictionary containing results from all tasks.

**Giá trị trả về (Returns):**

- `Dict`: Giá trị trả về

#### `execute_task`

**Chữ ký (Signature):**

```python
execute_task(self, task_name: str) -> Any
```text

**Mô tả:**

Execute a specific task by name.

Args:
    task_name: The name of the task to execute.
    
Returns:
    The result of executing the task.
    
Raises:
    KeyError: If the task is not found.

**Tham số (Parameters):**

- `task_name` (str): Tham số task_name

**Giá trị trả về (Returns):**

- `Any`: Giá trị trả về

**Ngoại lệ (Raises):**

- `KeyError`

#### `get_result`

**Chữ ký (Signature):**

```python
get_result(self, task_name: str) -> Optional[Any]
```text

**Mô tả:**

Get the result of a previously executed task.

Args:
    task_name: The name of the task.
    
Returns:
    The result if the task has been executed, None otherwise.

**Tham số (Parameters):**

- `task_name` (str): Tham số task_name

**Giá trị trả về (Returns):**

- `Optional`: Giá trị trả về

### Ví dụ sử dụng

**Ví dụ cơ bản sử dụng ExecutionEngine**

```python
# Ví dụ sử dụng ExecutionEngine
from agentic_sdlc.infrastructure.engine.execution_engine import ExecutionEngine

# Tạo instance
obj = ExecutionEngine()
```text

---

## Class `Task`

**Mô tả:**

Represents a task to be executed.

### Constructor

#### `__init__`

**Chữ ký (Signature):**

```python
__init__(self, name: str, func: Callable[..., Any], args: tuple = <factory>, kwargs: Dict[str, Any] = <factory>, timeout: Optional[int] = None) -> None
```text

**Mô tả:**

Initialize self.  See help(type(self)) for accurate signature.

**Tham số (Parameters):**

- `name` (str): Tham số name
- `func` (Callable): Tham số func
- `args` (tuple), mặc định: `<factory>`: Tham số args
- `kwargs` (Dict), mặc định: `<factory>`: Tham số kwargs
- `timeout` (Optional): Tham số timeout

**Giá trị trả về (Returns):**

- `None`: Giá trị trả về

### Methods

#### `__repr__`

**Chữ ký (Signature):**

```python
__repr__(self)
```text

**Mô tả:**

Return repr(self).

**Giá trị trả về (Returns):**

- `Any`: Giá trị trả về

### Ví dụ sử dụng

**Ví dụ cơ bản sử dụng Task**

```python
# Ví dụ sử dụng Task
from agentic_sdlc.infrastructure.engine.execution_engine import Task

# Tạo instance
obj = Task()
```text

---

## Class `TaskExecutor`

**Mô tả:**

Executor for running individual tasks.

The TaskExecutor is responsible for executing a single task with
proper error handling and timeout management.

### Constructor

#### `__init__`

**Chữ ký (Signature):**

```python
__init__(self) -> None
```text

**Mô tả:**

Initialize the task executor.

**Giá trị trả về (Returns):**

- `None`: Giá trị trả về

### Methods

#### `execute`

**Chữ ký (Signature):**

```python
execute(self, task: agentic_sdlc.infrastructure.engine.execution_engine.Task) -> Any
```javascript

**Mô tả:**

Execute a task.

Args:
    task: The task to execute.
    
Returns:
    The result of executing the task.
    
Raises:
    Exception: Any exception raised by the task function.

**Tham số (Parameters):**

- `task` (Task): Tham số task

**Giá trị trả về (Returns):**

- `Any`: Giá trị trả về

### Ví dụ sử dụng

**Ví dụ cơ bản sử dụng TaskExecutor**

```python
# Ví dụ sử dụng TaskExecutor
from agentic_sdlc.infrastructure.engine.execution_engine import TaskExecutor

# Tạo instance
obj = TaskExecutor()
```' has insufficient content
⚠️ **language_consistency**: Document in vi/ directory should contain Vietnamese content
❌ **syntax_error** (line 39): Python syntax error in code block: invalid syntax
❌ **syntax_error** (line 57): Python syntax error in code block: invalid syntax
❌ **syntax_error** (line 80): Python syntax error in code block: invalid syntax
❌ **syntax_error** (line 99): Python syntax error in code block: invalid syntax
❌ **syntax_error** (line 132): Python syntax error in code block: invalid syntax
❌ **syntax_error** (line 180): Python syntax error in code block: invalid syntax
❌ **syntax_error** (line 247): Python syntax error in code block: invalid syntax
❌ **syntax_error** (line 265): Python syntax error in code block: invalid syntax

### api-reference/infrastructure/lifecycle.md

❌ **missing_module_path**: API reference missing module path
⚠️ **empty_section**: Section 'Tổng Quan

Lifecycle management for SDK components.

---

## Classes

## Class `LifecycleManager`

**Mô tả:**

Manager for component lifecycle.

The LifecycleManager handles the lifecycle of SDK components,
managing transitions between phases and executing callbacks.

### Constructor

#### `__init__`

**Chữ ký (Signature):**

```python
__init__(self) -> None
```text

**Mô tả:**

Initialize the lifecycle manager.

**Giá trị trả về (Returns):**

- `None`: Giá trị trả về

### Methods

#### `get_phase`

**Chữ ký (Signature):**

```python
get_phase(self) -> agentic_sdlc.infrastructure.lifecycle.lifecycle.Phase
```text

**Mô tả:**

Get the current lifecycle phase.

Returns:
    The current phase.

**Giá trị trả về (Returns):**

- `Phase`: Giá trị trả về

#### `is_running`

**Chữ ký (Signature):**

```python
is_running(self) -> bool
```text

**Mô tả:**

Check if the component is running.

Returns:
    True if in RUNNING phase, False otherwise.

**Giá trị trả về (Returns):**

- `bool`: Giá trị trả về

#### `is_stopped`

**Chữ ký (Signature):**

```python
is_stopped(self) -> bool
```text

**Mô tả:**

Check if the component is stopped.

Returns:
    True if in STOPPED or SHUTDOWN phase, False otherwise.

**Giá trị trả về (Returns):**

- `bool`: Giá trị trả về

#### `register_callback`

**Chữ ký (Signature):**

```python
register_callback(self, phase: agentic_sdlc.infrastructure.lifecycle.lifecycle.Phase, callback: Callable[[], Any]) -> None
```javascript

**Mô tả:**

Register a callback for a lifecycle phase.

Args:
    phase: The phase to register the callback for.
    callback: The callback function to execute.

**Tham số (Parameters):**

- `phase` (Phase): Tham số phase
- `callback` (Callable): Tham số callback

**Giá trị trả về (Returns):**

- `None`: Giá trị trả về

#### `transition_to`

**Chữ ký (Signature):**

```python
transition_to(self, phase: agentic_sdlc.infrastructure.lifecycle.lifecycle.Phase) -> None
```text

**Mô tả:**

Transition to a new lifecycle phase.

Args:
    phase: The target phase.
    
Raises:
    ValueError: If the transition is invalid.

**Tham số (Parameters):**

- `phase` (Phase): Tham số phase

**Giá trị trả về (Returns):**

- `None`: Giá trị trả về

**Ngoại lệ (Raises):**

- `ValueError`

### Ví dụ sử dụng

**Ví dụ cơ bản sử dụng LifecycleManager**

```python
# Ví dụ sử dụng LifecycleManager
from agentic_sdlc.infrastructure.lifecycle.lifecycle import LifecycleManager

# Tạo instance
obj = LifecycleManager()
```text

---

## Class `Phase`

**Mô tả:**

Lifecycle phases for SDK components.

### Constructor

#### `__init__`

**Chữ ký (Signature):**

```python
__init__(self, *args, **kwds)
```text

**Mô tả:**

Initialize self.  See help(type(self)) for accurate signature.

**Tham số (Parameters):**

- `args` (Any): Tham số args
- `kwds` (Any): Tham số kwds

**Giá trị trả về (Returns):**

- `None`: Giá trị trả về

### Ví dụ sử dụng

**Ví dụ cơ bản sử dụng Phase**

```python
# Ví dụ sử dụng Phase
from agentic_sdlc.infrastructure.lifecycle.lifecycle import Phase

# Tạo instance
obj = Phase()
```' has insufficient content
⚠️ **language_consistency**: Document in vi/ directory should contain Vietnamese content
❌ **syntax_error** (line 39): Python syntax error in code block: invalid syntax
❌ **syntax_error** (line 57): Python syntax error in code block: invalid syntax
❌ **syntax_error** (line 76): Python syntax error in code block: invalid syntax
❌ **syntax_error** (line 95): Python syntax error in code block: invalid syntax
❌ **syntax_error** (line 114): Python syntax error in code block: invalid syntax
❌ **syntax_error** (line 139): Python syntax error in code block: invalid syntax

### api-reference/intelligence/collaborator.md

❌ **missing_module_path**: API reference missing module path
⚠️ **empty_section**: Section 'Tổng Quan

Multi-agent collaboration and coordination.

---

## Classes

## Class `CollaborationMessage`

**Mô tả:**

A message in agent collaboration.

### Constructor

#### `__init__`

**Chữ ký (Signature):**

```python
__init__(self, sender: str, recipient: str, message_type: agentic_sdlc.intelligence.collaboration.collaborator.MessageType, content: str, timestamp: str = <factory>, metadata: Dict[str, Any] = <factory>) -> None
```text

**Mô tả:**

Initialize self.  See help(type(self)) for accurate signature.

**Tham số (Parameters):**

- `sender` (str): Tham số sender
- `recipient` (str): Tham số recipient
- `message_type` (MessageType): Tham số message_type
- `content` (str): Tham số content
- `timestamp` (str), mặc định: `<factory>`: Tham số timestamp
- `metadata` (Dict), mặc định: `<factory>`: Tham số metadata

**Giá trị trả về (Returns):**

- `None`: Giá trị trả về

### Methods

#### `__repr__`

**Chữ ký (Signature):**

```python
__repr__(self)
```text

**Mô tả:**

Return repr(self).

**Giá trị trả về (Returns):**

- `Any`: Giá trị trả về

### Ví dụ sử dụng

**Ví dụ cơ bản sử dụng CollaborationMessage**

```python
# Ví dụ sử dụng CollaborationMessage
from agentic_sdlc.intelligence.collaboration.collaborator import CollaborationMessage

# Tạo instance
obj = CollaborationMessage()
```text

---

## Class `CollaborationResult`

**Mô tả:**

Result of a collaboration session.

### Constructor

#### `__init__`

**Chữ ký (Signature):**

```python
__init__(self, task: str, participants: List[str], messages: List[agentic_sdlc.intelligence.collaboration.collaborator.CollaborationMessage], outcome: str, timestamp: str = <factory>) -> None
```text

**Mô tả:**

Initialize self.  See help(type(self)) for accurate signature.

**Tham số (Parameters):**

- `task` (str): Tham số task
- `participants` (List): Tham số participants
- `messages` (List): Tham số messages
- `outcome` (str): Tham số outcome
- `timestamp` (str), mặc định: `<factory>`: Tham số timestamp

**Giá trị trả về (Returns):**

- `None`: Giá trị trả về

### Methods

#### `__repr__`

**Chữ ký (Signature):**

```python
__repr__(self)
```text

**Mô tả:**

Return repr(self).

**Giá trị trả về (Returns):**

- `Any`: Giá trị trả về

### Ví dụ sử dụng

**Ví dụ cơ bản sử dụng CollaborationResult**

```python
# Ví dụ sử dụng CollaborationResult
from agentic_sdlc.intelligence.collaboration.collaborator import CollaborationResult

# Tạo instance
obj = CollaborationResult()
```text

---

## Class `Collaborator`

**Mô tả:**

Manages collaboration between agents.

### Constructor

#### `__init__`

**Chữ ký (Signature):**

```python
__init__(self, agent_name: str)
```text

**Mô tả:**

Initialize a collaborator.

Args:
    agent_name: Name of the agent

**Tham số (Parameters):**

- `agent_name` (str): Tham số agent_name

**Giá trị trả về (Returns):**

- `None`: Giá trị trả về

### Methods

#### `get_collaboration_history`

**Chữ ký (Signature):**

```python
get_collaboration_history(self) -> List[agentic_sdlc.intelligence.collaboration.collaborator.CollaborationResult]
```text

**Mô tả:**

Get collaboration history.

Returns:
    List of past collaborations

**Giá trị trả về (Returns):**

- `List`: Giá trị trả về

#### `get_message_history`

**Chữ ký (Signature):**

```python
get_message_history(self) -> List[agentic_sdlc.intelligence.collaboration.collaborator.CollaborationMessage]
```text

**Mô tả:**

Get full message history.

Returns:
    List of all messages

**Giá trị trả về (Returns):**

- `List`: Giá trị trả về

#### `get_messages`

**Chữ ký (Signature):**

```python
get_messages(self, sender: Optional[str] = None) -> List[agentic_sdlc.intelligence.collaboration.collaborator.CollaborationMessage]
```text

**Mô tả:**

Get messages, optionally filtered by sender.

Args:
    sender: Optional sender to filter by

Returns:
    List of messages

**Tham số (Parameters):**

- `sender` (Optional): Tham số sender

**Giá trị trả về (Returns):**

- `List`: Giá trị trả về

#### `receive_message`

**Chữ ký (Signature):**

```python
receive_message(self, message: agentic_sdlc.intelligence.collaboration.collaborator.CollaborationMessage) -> None
```text

**Mô tả:**

Receive a message from another agent.

Args:
    message: CollaborationMessage to receive

**Tham số (Parameters):**

- `message` (CollaborationMessage): Tham số message

**Giá trị trả về (Returns):**

- `None`: Giá trị trả về

#### `record_collaboration`

**Chữ ký (Signature):**

```python
record_collaboration(self, task: str, participants: List[str], outcome: str) -> agentic_sdlc.intelligence.collaboration.collaborator.CollaborationResult
```text

**Mô tả:**

Record a collaboration session.

Args:
    task: Task description
    participants: List of participant agent names
    outcome: Outcome of collaboration

Returns:
    CollaborationResult object

**Tham số (Parameters):**

- `task` (str): Tham số task
- `participants` (List): Tham số participants
- `outcome` (str): Tham số outcome

**Giá trị trả về (Returns):**

- `CollaborationResult`: Giá trị trả về

#### `send_message`

**Chữ ký (Signature):**

```python
send_message(self, recipient: str, message_type: agentic_sdlc.intelligence.collaboration.collaborator.MessageType, content: str, metadata: Optional[Dict] = None) -> agentic_sdlc.intelligence.collaboration.collaborator.CollaborationMessage
```text

**Mô tả:**

Send a message to another agent.

Args:
    recipient: Recipient agent name
    message_type: Type of message
    content: Message content
    metadata: Optional metadata

Returns:
    CollaborationMessage object

**Tham số (Parameters):**

- `recipient` (str): Tham số recipient
- `message_type` (MessageType): Tham số message_type
- `content` (str): Tham số content
- `metadata` (Optional): Tham số metadata

**Giá trị trả về (Returns):**

- `CollaborationMessage`: Giá trị trả về

### Ví dụ sử dụng

**Ví dụ cơ bản sử dụng Collaborator**

```python
# Ví dụ sử dụng Collaborator
from agentic_sdlc.intelligence.collaboration.collaborator import Collaborator

# Tạo instance
obj = Collaborator()
```text

---

## Class `MessageType`

**Mô tả:**

Types of messages in collaboration.

### Constructor

#### `__init__`

**Chữ ký (Signature):**

```python
__init__(self, *args, **kwds)
```text

**Mô tả:**

Initialize self.  See help(type(self)) for accurate signature.

**Tham số (Parameters):**

- `args` (Any): Tham số args
- `kwds` (Any): Tham số kwds

**Giá trị trả về (Returns):**

- `None`: Giá trị trả về

### Ví dụ sử dụng

**Ví dụ cơ bản sử dụng MessageType**

```python
# Ví dụ sử dụng MessageType
from agentic_sdlc.intelligence.collaboration.collaborator import MessageType

# Tạo instance
obj = MessageType()
```text

---

## Class `TeamCoordinator`

**Mô tả:**

Coordinates collaboration between multiple agents.

### Constructor

#### `__init__`

**Chữ ký (Signature):**

```python
__init__(self)
```text

**Mô tả:**

Initialize the team coordinator.

**Giá trị trả về (Returns):**

- `None`: Giá trị trả về

### Methods

#### `end_session`

**Chữ ký (Signature):**

```python
end_session(self, session_index: int, outcome: str) -> Optional[Dict]
```text

**Mô tả:**

End a collaboration session.

Args:
    session_index: Index of the session
    outcome: Outcome of the session

Returns:
    Updated session dictionary or None

**Tham số (Parameters):**

- `session_index` (int): Tham số session_index
- `outcome` (str): Tham số outcome

**Giá trị trả về (Returns):**

- `Optional`: Giá trị trả về

#### `get_agent`

**Chữ ký (Signature):**

```python
get_agent(self, agent_name: str) -> Optional[agentic_sdlc.intelligence.collaboration.collaborator.Collaborator]
```text

**Mô tả:**

Get a registered agent.

Args:
    agent_name: Name of the agent

Returns:
    Collaborator instance or None

**Tham số (Parameters):**

- `agent_name` (str): Tham số agent_name

**Giá trị trả về (Returns):**

- `Optional`: Giá trị trả về

#### `get_all_agents`

**Chữ ký (Signature):**

```python
get_all_agents(self) -> Dict[str, agentic_sdlc.intelligence.collaboration.collaborator.Collaborator]
```text

**Mô tả:**

Get all registered agents.

Returns:
    Dictionary of agent names to Collaborator instances

**Giá trị trả về (Returns):**

- `Dict`: Giá trị trả về

#### `get_sessions`

**Chữ ký (Signature):**

```python
get_sessions(self) -> List[Dict]
```text

**Mô tả:**

Get all collaboration sessions.

Returns:
    List of sessions

**Giá trị trả về (Returns):**

- `List`: Giá trị trả về

#### `get_team_stats`

**Chữ ký (Signature):**

```python
get_team_stats(self) -> Dict[str, Any]
```text

**Mô tả:**

Get statistics about the team.

Returns:
    Dictionary with team statistics

**Giá trị trả về (Returns):**

- `Dict`: Giá trị trả về

#### `register_agent`

**Chữ ký (Signature):**

```python
register_agent(self, agent_name: str) -> agentic_sdlc.intelligence.collaboration.collaborator.Collaborator
```text

**Mô tả:**

Register an agent with the coordinator.

Args:
    agent_name: Name of the agent

Returns:
    Collaborator instance for the agent

**Tham số (Parameters):**

- `agent_name` (str): Tham số agent_name

**Giá trị trả về (Returns):**

- `Collaborator`: Giá trị trả về

#### `send_message`

**Chữ ký (Signature):**

```python
send_message(self, sender: str, recipient: str, message_type: agentic_sdlc.intelligence.collaboration.collaborator.MessageType, content: str, metadata: Optional[Dict] = None) -> Optional[agentic_sdlc.intelligence.collaboration.collaborator.CollaborationMessage]
```text

**Mô tả:**

Send a message between agents.

Args:
    sender: Sender agent name
    recipient: Recipient agent name
    message_type: Type of message
    content: Message content
    metadata: Optional metadata

Returns:
    CollaborationMessage or None if agents not found

**Tham số (Parameters):**

- `sender` (str): Tham số sender
- `recipient` (str): Tham số recipient
- `message_type` (MessageType): Tham số message_type
- `content` (str): Tham số content
- `metadata` (Optional): Tham số metadata

**Giá trị trả về (Returns):**

- `Optional`: Giá trị trả về

#### `start_session`

**Chữ ký (Signature):**

```python
start_session(self, task: str, participants: List[str]) -> Dict
```text

**Mô tả:**

Start a collaboration session.

Args:
    task: Task description
    participants: List of participant agent names

Returns:
    Session dictionary

**Tham số (Parameters):**

- `task` (str): Tham số task
- `participants` (List): Tham số participants

**Giá trị trả về (Returns):**

- `Dict`: Giá trị trả về

### Ví dụ sử dụng

**Ví dụ cơ bản sử dụng TeamCoordinator**

```python
# Ví dụ sử dụng TeamCoordinator
from agentic_sdlc.intelligence.collaboration.collaborator import TeamCoordinator

# Tạo instance
obj = TeamCoordinator()
```' has insufficient content
⚠️ **language_consistency**: Document in vi/ directory should contain Vietnamese content
❌ **syntax_error** (line 36): Python syntax error in code block: invalid syntax
❌ **syntax_error** (line 101): Python syntax error in code block: invalid syntax
❌ **syntax_error** (line 165): Python syntax error in code block: invalid syntax
❌ **syntax_error** (line 190): Python syntax error in code block: invalid syntax
❌ **syntax_error** (line 209): Python syntax error in code block: invalid syntax
❌ **syntax_error** (line 228): Python syntax error in code block: invalid syntax
❌ **syntax_error** (line 254): Python syntax error in code block: invalid syntax
❌ **syntax_error** (line 277): Python syntax error in code block: invalid syntax
❌ **syntax_error** (line 307): Python syntax error in code block: invalid syntax
❌ **syntax_error** (line 422): Python syntax error in code block: invalid syntax
❌ **syntax_error** (line 450): Python syntax error in code block: invalid syntax
❌ **syntax_error** (line 476): Python syntax error in code block: invalid syntax
❌ **syntax_error** (line 495): Python syntax error in code block: invalid syntax
❌ **syntax_error** (line 514): Python syntax error in code block: invalid syntax
❌ **syntax_error** (line 533): Python syntax error in code block: invalid syntax
❌ **syntax_error** (line 559): Python syntax error in code block: invalid syntax
❌ **syntax_error** (line 593): Python syntax error in code block: invalid syntax

### api-reference/intelligence/learner.md

❌ **missing_module_path**: API reference missing module path
⚠️ **empty_section**: Section 'Tổng Quan

Self-learning engine for pattern recognition and auto-learning.

---

## Classes

## Class `Learner`

**Mô tả:**

Pattern recognition and auto-learning engine.

### Constructor

#### `__init__`

**Chữ ký (Signature):**

```python
__init__(self, storage_file: Optional[pathlib.Path] = None)
```text

**Mô tả:**

Initialize the learner.

Args:
    storage_file: Optional path to store learned patterns

**Tham số (Parameters):**

- `storage_file` (Optional): Tham số storage_file

**Giá trị trả về (Returns):**

- `None`: Giá trị trả về

### Methods

#### `find_similar`

**Chữ ký (Signature):**

```python
find_similar(self, query: str, pattern_type: Optional[agentic_sdlc.intelligence.learning.learner.PatternType] = None) -> List[agentic_sdlc.intelligence.learning.learner.Pattern]
```text

**Mô tả:**

Find patterns similar to a query.

Args:
    query: Query string to search for
    pattern_type: Optional pattern type to filter by

Returns:
    List of similar patterns

**Tham số (Parameters):**

- `query` (str): Tham số query
- `pattern_type` (Optional): Tham số pattern_type

**Giá trị trả về (Returns):**

- `List`: Giá trị trả về

#### `get_recommendation`

**Chữ ký (Signature):**

```python
get_recommendation(self, task: str) -> Optional[Dict]
```text

**Mô tả:**

Get a recommendation for a task based on learned patterns.

Args:
    task: Description of the task

Returns:
    Recommendation dictionary or None

**Tham số (Parameters):**

- `task` (str): Tham số task

**Giá trị trả về (Returns):**

- `Optional`: Giá trị trả về

#### `get_stats`

**Chữ ký (Signature):**

```python
get_stats(self) -> Dict
```text

**Mô tả:**

Get statistics about learned patterns.

Returns:
    Dictionary with statistics

**Giá trị trả về (Returns):**

- `Dict`: Giá trị trả về

#### `learn`

**Chữ ký (Signature):**

```python
learn(self, description: str, context: Optional[Dict] = None) -> Dict
```text

**Mô tả:**

Learn a general pattern.

Args:
    description: Description of the pattern
    context: Optional context information

Returns:
    Dictionary with learning result

**Tham số (Parameters):**

- `description` (str): Tham số description
- `context` (Optional): Tham số context

**Giá trị trả về (Returns):**

- `Dict`: Giá trị trả về

#### `learn_error`

**Chữ ký (Signature):**

```python
learn_error(self, error: str, resolution: str, context: Optional[Dict] = None) -> Dict
```text

**Mô tả:**

Learn from an error and its resolution.

Args:
    error: Description of the error
    resolution: How the error was resolved
    context: Optional context information

Returns:
    Dictionary with learning result

**Tham số (Parameters):**

- `error` (str): Tham số error
- `resolution` (str): Tham số resolution
- `context` (Optional): Tham số context

**Giá trị trả về (Returns):**

- `Dict`: Giá trị trả về

#### `learn_from_ab_test`

**Chữ ký (Signature):**

```python
learn_from_ab_test(self, test_result: Dict) -> Dict
```text

**Mô tả:**

Learn from A/B test results.

Args:
    test_result: A/B test result dictionary

Returns:
    Dictionary with learning result

**Tham số (Parameters):**

- `test_result` (Dict): Tham số test_result

**Giá trị trả về (Returns):**

- `Dict`: Giá trị trả về

#### `learn_from_judge`

**Chữ ký (Signature):**

```python
learn_from_judge(self, score_result: Dict) -> Dict
```text

**Mô tả:**

Learn from judge scoring results.

Args:
    score_result: Judge scoring result dictionary

Returns:
    Dictionary with learning result

**Tham số (Parameters):**

- `score_result` (Dict): Tham số score_result

**Giá trị trả về (Returns):**

- `Dict`: Giá trị trả về

#### `learn_from_observer`

**Chữ ký (Signature):**

```python
learn_from_observer(self, violations: List[Dict]) -> Dict
```text

**Mô tả:**

Learn from observer violations.

Args:
    violations: List of violation dictionaries

Returns:
    Dictionary with learning result

**Tham số (Parameters):**

- `violations` (List): Tham số violations

**Giá trị trả về (Returns):**

- `Dict`: Giá trị trả về

#### `learn_success`

**Chữ ký (Signature):**

```python
learn_success(self, task: str, approach: str, context: Optional[Dict] = None) -> Dict
```text

**Mô tả:**

Learn from a successful task execution.

Args:
    task: Description of the task
    approach: The approach that was successful
    context: Optional context information

Returns:
    Dictionary with learning result

**Tham số (Parameters):**

- `task` (str): Tham số task
- `approach` (str): Tham số approach
- `context` (Optional): Tham số context

**Giá trị trả về (Returns):**

- `Dict`: Giá trị trả về

#### `list_patterns`

**Chữ ký (Signature):**

```python
list_patterns(self, pattern_type: Optional[agentic_sdlc.intelligence.learning.learner.PatternType] = None) -> List[agentic_sdlc.intelligence.learning.learner.Pattern]
```text

**Mô tả:**

List all patterns, optionally filtered by type.

Args:
    pattern_type: Optional pattern type to filter by

Returns:
    List of patterns

**Tham số (Parameters):**

- `pattern_type` (Optional): Tham số pattern_type

**Giá trị trả về (Returns):**

- `List`: Giá trị trả về

### Ví dụ sử dụng

**Ví dụ cơ bản sử dụng Learner**

```python
# Ví dụ sử dụng Learner
from agentic_sdlc.intelligence.learning.learner import Learner

# Tạo instance
obj = Learner()
```text

---

## Class `LearningEvent`

**Mô tả:**

Represents a learning event.

### Constructor

#### `__init__`

**Chữ ký (Signature):**

```python
__init__(self, event_type: str, description: str, context: Dict[str, Any], timestamp: str = <factory>) -> None
```text

**Mô tả:**

Initialize self.  See help(type(self)) for accurate signature.

**Tham số (Parameters):**

- `event_type` (str): Tham số event_type
- `description` (str): Tham số description
- `context` (Dict): Tham số context
- `timestamp` (str), mặc định: `<factory>`: Tham số timestamp

**Giá trị trả về (Returns):**

- `None`: Giá trị trả về

### Methods

#### `__repr__`

**Chữ ký (Signature):**

```python
__repr__(self)
```text

**Mô tả:**

Return repr(self).

**Giá trị trả về (Returns):**

- `Any`: Giá trị trả về

#### `to_dict`

**Chữ ký (Signature):**

```python
to_dict(self) -> dict
```text

**Mô tả:**

Convert event to dictionary.

**Giá trị trả về (Returns):**

- `dict`: Giá trị trả về

### Ví dụ sử dụng

**Ví dụ cơ bản sử dụng LearningEvent**

```python
# Ví dụ sử dụng LearningEvent
from agentic_sdlc.intelligence.learning.learner import LearningEvent

# Tạo instance
obj = LearningEvent()
```python

---

## Class `LearningStrategy`

**Mô tả:**

Base class for learning strategies.

### Constructor

#### `__init__`

**Chữ ký (Signature):**

```python
__init__(self, /, *args, **kwargs)
```text

**Mô tả:**

Initialize self.  See help(type(self)) for accurate signature.

**Tham số (Parameters):**

- `args` (Any): Tham số args
- `kwargs` (Any): Tham số kwargs

**Giá trị trả về (Returns):**

- `None`: Giá trị trả về

### Methods

#### `learn`

**Chữ ký (Signature):**

```python
learn(self, data: Dict) -> Dict
```text

**Mô tả:**

Learn from data.

Args:
    data: Data to learn from

Returns:
    Learning result

**Tham số (Parameters):**

- `data` (Dict): Tham số data

**Giá trị trả về (Returns):**

- `Dict`: Giá trị trả về

### Ví dụ sử dụng

**Ví dụ cơ bản sử dụng LearningStrategy**

```python
# Ví dụ sử dụng LearningStrategy
from agentic_sdlc.intelligence.learning.learner import LearningStrategy

# Tạo instance
obj = LearningStrategy()
```text

---

## Class `Pattern`

**Mô tả:**

Represents a learned pattern.

### Constructor

#### `__init__`

**Chữ ký (Signature):**

```python
__init__(self, pattern_type: agentic_sdlc.intelligence.learning.learner.PatternType, description: str, context: Dict[str, Any], timestamp: str = <factory>, frequency: int = 1) -> None
```text

**Mô tả:**

Initialize self.  See help(type(self)) for accurate signature.

**Tham số (Parameters):**

- `pattern_type` (PatternType): Tham số pattern_type
- `description` (str): Tham số description
- `context` (Dict): Tham số context
- `timestamp` (str), mặc định: `<factory>`: Tham số timestamp
- `frequency` (int), mặc định: `1`: Tham số frequency

**Giá trị trả về (Returns):**

- `None`: Giá trị trả về

### Methods

#### `__repr__`

**Chữ ký (Signature):**

```python
__repr__(self)
```text

**Mô tả:**

Return repr(self).

**Giá trị trả về (Returns):**

- `Any`: Giá trị trả về

#### `to_dict`

**Chữ ký (Signature):**

```python
to_dict(self) -> dict
```text

**Mô tả:**

Convert pattern to dictionary.

**Giá trị trả về (Returns):**

- `dict`: Giá trị trả về

### Ví dụ sử dụng

**Ví dụ cơ bản sử dụng Pattern**

```python
# Ví dụ sử dụng Pattern
from agentic_sdlc.intelligence.learning.learner import Pattern

# Tạo instance
obj = Pattern()
```text

---

## Class `PatternType`

**Mô tả:**

Types of patterns that can be learned.

### Constructor

#### `__init__`

**Chữ ký (Signature):**

```python
__init__(self, *args, **kwds)
```text

**Mô tả:**

Initialize self.  See help(type(self)) for accurate signature.

**Tham số (Parameters):**

- `args` (Any): Tham số args
- `kwds` (Any): Tham số kwds

**Giá trị trả về (Returns):**

- `None`: Giá trị trả về

### Ví dụ sử dụng

**Ví dụ cơ bản sử dụng PatternType**

```python
# Ví dụ sử dụng PatternType
from agentic_sdlc.intelligence.learning.learner import PatternType

# Tạo instance
obj = PatternType()
```' has insufficient content
⚠️ **language_consistency**: Document in vi/ directory should contain Vietnamese content
❌ **syntax_error** (line 36): Python syntax error in code block: invalid syntax
❌ **syntax_error** (line 61): Python syntax error in code block: invalid syntax
❌ **syntax_error** (line 89): Python syntax error in code block: invalid syntax
❌ **syntax_error** (line 115): Python syntax error in code block: invalid syntax
❌ **syntax_error** (line 134): Python syntax error in code block: invalid syntax
❌ **syntax_error** (line 162): Python syntax error in code block: invalid syntax
❌ **syntax_error** (line 192): Python syntax error in code block: invalid syntax
❌ **syntax_error** (line 218): Python syntax error in code block: invalid syntax
❌ **syntax_error** (line 244): Python syntax error in code block: invalid syntax
❌ **syntax_error** (line 270): Python syntax error in code block: invalid syntax
❌ **syntax_error** (line 300): Python syntax error in code block: invalid syntax
❌ **syntax_error** (line 348): Python syntax error in code block: invalid syntax
❌ **syntax_error** (line 389): Python syntax error in code block: invalid syntax
❌ **syntax_error** (line 427): Python syntax error in code block: invalid syntax
❌ **syntax_error** (line 450): Python syntax error in code block: invalid syntax
❌ **syntax_error** (line 498): Python syntax error in code block: invalid syntax
❌ **syntax_error** (line 540): Python syntax error in code block: invalid syntax

### api-reference/intelligence/monitor.md

❌ **missing_module_path**: API reference missing module path
⚠️ **empty_section**: Section 'Tổng Quan

System monitoring and metrics collection.

---

## Classes

## Class `HealthStatus`

**Mô tả:**

System health status.

### Constructor

#### `__init__`

**Chữ ký (Signature):**

```python
__init__(self, status: str, timestamp: str = <factory>, metrics: Dict[str, Any] = <factory>, message: str = '') -> None
```text

**Mô tả:**

Initialize self.  See help(type(self)) for accurate signature.

**Tham số (Parameters):**

- `status` (str): Tham số status
- `timestamp` (str), mặc định: `<factory>`: Tham số timestamp
- `metrics` (Dict), mặc định: `<factory>`: Tham số metrics
- `message` (str), mặc định: ``: Tham số message

**Giá trị trả về (Returns):**

- `None`: Giá trị trả về

### Methods

#### `__repr__`

**Chữ ký (Signature):**

```python
__repr__(self)
```text

**Mô tả:**

Return repr(self).

**Giá trị trả về (Returns):**

- `Any`: Giá trị trả về

### Ví dụ sử dụng

**Ví dụ cơ bản sử dụng HealthStatus**

```python
# Ví dụ sử dụng HealthStatus
from agentic_sdlc.intelligence.monitoring.monitor import HealthStatus

# Tạo instance
obj = HealthStatus()
```text

---

## Class `MetricsCollector`

**Mô tả:**

Collects and aggregates metrics.

### Constructor

#### `__init__`

**Chữ ký (Signature):**

```python
__init__(self, storage_file: Optional[pathlib.Path] = None)
```text

**Mô tả:**

Initialize the metrics collector.

Args:
    storage_file: Optional path to store metrics

**Tham số (Parameters):**

- `storage_file` (Optional): Tham số storage_file

**Giá trị trả về (Returns):**

- `None`: Giá trị trả về

### Methods

#### `clear_metric`

**Chữ ký (Signature):**

```python
clear_metric(self, metric_name: str) -> None
```text

**Mô tả:**

Clear a specific metric.

Args:
    metric_name: Name of the metric to clear

**Tham số (Parameters):**

- `metric_name` (str): Tham số metric_name

**Giá trị trả về (Returns):**

- `None`: Giá trị trả về

#### `clear_metrics`

**Chữ ký (Signature):**

```python
clear_metrics(self) -> None
```text

**Mô tả:**

Clear all collected metrics.

**Giá trị trả về (Returns):**

- `None`: Giá trị trả về

#### `collect`

**Chữ ký (Signature):**

```python
collect(self, metric_name: str, value: Any) -> None
```text

**Mô tả:**

Collect a metric value.

Args:
    metric_name: Name of the metric
    value: Value to collect

**Tham số (Parameters):**

- `metric_name` (str): Tham số metric_name
- `value` (Any): Tham số value

**Giá trị trả về (Returns):**

- `None`: Giá trị trả về

#### `get_all_metrics`

**Chữ ký (Signature):**

```python
get_all_metrics(self) -> Dict[str, List[Dict]]
```text

**Mô tả:**

Get all collected metrics.

Returns:
    Dictionary of all metrics

**Giá trị trả về (Returns):**

- `Dict`: Giá trị trả về

#### `get_metric_history`

**Chữ ký (Signature):**

```python
get_metric_history(self, metric_name: str) -> List[Dict]
```text

**Mô tả:**

Get history of a metric.

Args:
    metric_name: Name of the metric

Returns:
    List of metric values with timestamps

**Tham số (Parameters):**

- `metric_name` (str): Tham số metric_name

**Giá trị trả về (Returns):**

- `List`: Giá trị trả về

#### `get_metric_summary`

**Chữ ký (Signature):**

```python
get_metric_summary(self, metric_name: str) -> Dict[str, Any]
```text

**Mô tả:**

Get summary statistics for a metric.

Args:
    metric_name: Name of the metric

Returns:
    Dictionary with summary statistics

**Tham số (Parameters):**

- `metric_name` (str): Tham số metric_name

**Giá trị trả về (Returns):**

- `Dict`: Giá trị trả về

### Ví dụ sử dụng

**Ví dụ cơ bản sử dụng MetricsCollector**

```python
# Ví dụ sử dụng MetricsCollector
from agentic_sdlc.intelligence.monitoring.monitor import MetricsCollector

# Tạo instance
obj = MetricsCollector()
```text

---

## Class `Monitor`

**Mô tả:**

Monitors system health and project metrics.

### Constructor

#### `__init__`

**Chữ ký (Signature):**

```python
__init__(self)
```text

**Mô tả:**

Initialize the monitor.

**Giá trị trả về (Returns):**

- `None`: Giá trị trả về

### Methods

#### `check_health`

**Chữ ký (Signature):**

```python
check_health(self) -> agentic_sdlc.intelligence.monitoring.monitor.HealthStatus
```text

**Mô tả:**

Check system health.

Returns:
    HealthStatus object

**Giá trị trả về (Returns):**

- `HealthStatus`: Giá trị trả về

#### `get_all_metrics`

**Chữ ký (Signature):**

```python
get_all_metrics(self) -> Dict[str, Any]
```text

**Mô tả:**

Get all metrics.

Returns:
    Dictionary of all metrics

**Giá trị trả về (Returns):**

- `Dict`: Giá trị trả về

#### `get_health_history`

**Chữ ký (Signature):**

```python
get_health_history(self) -> List[agentic_sdlc.intelligence.monitoring.monitor.HealthStatus]
```text

**Mô tả:**

Get health check history.

Returns:
    List of health statuses

**Giá trị trả về (Returns):**

- `List`: Giá trị trả về

#### `get_metric`

**Chữ ký (Signature):**

```python
get_metric(self, name: str) -> Optional[Any]
```text

**Mô tả:**

Get a metric value.

Args:
    name: Metric name

Returns:
    Metric value or None

**Tham số (Parameters):**

- `name` (str): Tham số name

**Giá trị trả về (Returns):**

- `Optional`: Giá trị trả về

#### `record_metric`

**Chữ ký (Signature):**

```python
record_metric(self, name: str, value: Any) -> None
```text

**Mô tả:**

Record a metric.

Args:
    name: Metric name
    value: Metric value

**Tham số (Parameters):**

- `name` (str): Tham số name
- `value` (Any): Tham số value

**Giá trị trả về (Returns):**

- `None`: Giá trị trả về

### Ví dụ sử dụng

**Ví dụ cơ bản sử dụng Monitor**

```python
# Ví dụ sử dụng Monitor
from agentic_sdlc.intelligence.monitoring.monitor import Monitor

# Tạo instance
obj = Monitor()
```' has insufficient content
⚠️ **language_consistency**: Document in vi/ directory should contain Vietnamese content
❌ **syntax_error** (line 36): Python syntax error in code block: invalid syntax
❌ **syntax_error** (line 99): Python syntax error in code block: invalid syntax
❌ **syntax_error** (line 124): Python syntax error in code block: invalid syntax
❌ **syntax_error** (line 147): Python syntax error in code block: invalid syntax
❌ **syntax_error** (line 163): Python syntax error in code block: invalid syntax
❌ **syntax_error** (line 188): Python syntax error in code block: invalid syntax
❌ **syntax_error** (line 207): Python syntax error in code block: invalid syntax
❌ **syntax_error** (line 233): Python syntax error in code block: invalid syntax
❌ **syntax_error** (line 299): Python syntax error in code block: invalid syntax
❌ **syntax_error** (line 318): Python syntax error in code block: invalid syntax
❌ **syntax_error** (line 337): Python syntax error in code block: invalid syntax
❌ **syntax_error** (line 356): Python syntax error in code block: invalid syntax
❌ **syntax_error** (line 382): Python syntax error in code block: invalid syntax

### api-reference/intelligence/reasoner.md

❌ **missing_module_path**: API reference missing module path
⚠️ **empty_section**: Section 'Tổng Quan

Reasoning engine for decision-making and task analysis.

---

## Classes

## Class `DecisionEngine`

**Mô tả:**

Engine for making complex decisions.

### Constructor

#### `__init__`

**Chữ ký (Signature):**

```python
__init__(self)
```text

**Mô tả:**

Initialize the decision engine.

**Giá trị trả về (Returns):**

- `None`: Giá trị trả về

### Methods

#### `add_rule`

**Chữ ký (Signature):**

```python
add_rule(self, rule_name: str, rule_logic: Any) -> None
```text

**Mô tả:**

Add a decision rule.

Args:
    rule_name: Name of the rule
    rule_logic: Rule logic or callable

**Tham số (Parameters):**

- `rule_name` (str): Tham số rule_name
- `rule_logic` (Any): Tham số rule_logic

**Giá trị trả về (Returns):**

- `None`: Giá trị trả về

#### `evaluate_all_rules`

**Chữ ký (Signature):**

```python
evaluate_all_rules(self, context: Dict) -> Dict[str, bool]
```text

**Mô tả:**

Evaluate all rules in a given context.

Args:
    context: Context for evaluation

Returns:
    Dictionary of rule names to evaluation results

**Tham số (Parameters):**

- `context` (Dict): Tham số context

**Giá trị trả về (Returns):**

- `Dict`: Giá trị trả về

#### `evaluate_rule`

**Chữ ký (Signature):**

```python
evaluate_rule(self, rule_name: str, context: Dict) -> bool
```text

**Mô tả:**

Evaluate a rule in a given context.

Args:
    rule_name: Name of the rule
    context: Context for evaluation

Returns:
    Boolean result of rule evaluation

**Tham số (Parameters):**

- `rule_name` (str): Tham số rule_name
- `context` (Dict): Tham số context

**Giá trị trả về (Returns):**

- `bool`: Giá trị trả về

#### `get_rules`

**Chữ ký (Signature):**

```python
get_rules(self) -> Dict[str, Any]
```text

**Mô tả:**

Get all decision rules.

Returns:
    Dictionary of rules

**Giá trị trả về (Returns):**

- `Dict`: Giá trị trả về

#### `make_decision`

**Chữ ký (Signature):**

```python
make_decision(self, options: List[Dict], context: Dict) -> Dict
```text

**Mô tả:**

Make a decision using rules and reasoning.

Args:
    options: List of options
    context: Decision context

Returns:
    Decision result

**Tham số (Parameters):**

- `options` (List): Tham số options
- `context` (Dict): Tham số context

**Giá trị trả về (Returns):**

- `Dict`: Giá trị trả về

### Ví dụ sử dụng

**Ví dụ cơ bản sử dụng DecisionEngine**

```python
# Ví dụ sử dụng DecisionEngine
from agentic_sdlc.intelligence.reasoning.reasoner import DecisionEngine

# Tạo instance
obj = DecisionEngine()
```text

---

## Class `ExecutionMode`

**Mô tả:**

Execution mode recommendation based on task analysis.

### Constructor

#### `__init__`

**Chữ ký (Signature):**

```python
__init__(self, *args, **kwds)
```text

**Mô tả:**

Initialize self.  See help(type(self)) for accurate signature.

**Tham số (Parameters):**

- `args` (Any): Tham số args
- `kwds` (Any): Tham số kwds

**Giá trị trả về (Returns):**

- `None`: Giá trị trả về

### Ví dụ sử dụng

**Ví dụ cơ bản sử dụng ExecutionMode**

```python
# Ví dụ sử dụng ExecutionMode
from agentic_sdlc.intelligence.reasoning.reasoner import ExecutionMode

# Tạo instance
obj = ExecutionMode()
```text

---

## Class `Reasoner`

**Mô tả:**

Reasoning engine for decision-making.

### Constructor

#### `__init__`

**Chữ ký (Signature):**

```python
__init__(self)
```text

**Mô tả:**

Initialize the reasoner.

**Giá trị trả về (Returns):**

- `None`: Giá trị trả về

### Methods

#### `analyze_task_complexity`

**Chữ ký (Signature):**

```python
analyze_task_complexity(self, task: str, context: Optional[Dict] = None) -> agentic_sdlc.intelligence.reasoning.reasoner.TaskComplexity
```text

**Mô tả:**

Analyze the complexity of a task.

Args:
    task: Task description
    context: Optional context information

Returns:
    TaskComplexity object

**Tham số (Parameters):**

- `task` (str): Tham số task
- `context` (Optional): Tham số context

**Giá trị trả về (Returns):**

- `TaskComplexity`: Giá trị trả về

#### `clear_history`

**Chữ ký (Signature):**

```python
clear_history(self) -> None
```text

**Mô tả:**

Clear decision history.

**Giá trị trả về (Returns):**

- `None`: Giá trị trả về

#### `get_decision_history`

**Chữ ký (Signature):**

```python
get_decision_history(self) -> List[Dict]
```text

**Mô tả:**

Get decision history.

Returns:
    List of past decisions

**Giá trị trả về (Returns):**

- `List`: Giá trị trả về

#### `make_decision`

**Chữ ký (Signature):**

```python
make_decision(self, options: List[Dict], criteria: Optional[Dict] = None) -> Dict
```text

**Mô tả:**

Make a decision among options based on criteria.

Args:
    options: List of option dictionaries
    criteria: Optional decision criteria

Returns:
    Selected option with reasoning

**Tham số (Parameters):**

- `options` (List): Tham số options
- `criteria` (Optional): Tham số criteria

**Giá trị trả về (Returns):**

- `Dict`: Giá trị trả về

#### `recommend_execution_mode`

**Chữ ký (Signature):**

```python
recommend_execution_mode(self, task: str, context: Optional[Dict] = None) -> agentic_sdlc.intelligence.reasoning.reasoner.ExecutionMode
```text

**Mô tả:**

Recommend execution mode for a task.

Args:
    task: Task description
    context: Optional context information

Returns:
    Recommended ExecutionMode

**Tham số (Parameters):**

- `task` (str): Tham số task
- `context` (Optional): Tham số context

**Giá trị trả về (Returns):**

- `ExecutionMode`: Giá trị trả về

#### `route_task`

**Chữ ký (Signature):**

```python
route_task(self, task: str, available_workflows: List[str]) -> agentic_sdlc.intelligence.reasoning.reasoner.RouteResult
```text

**Mô tả:**

Route a task to an appropriate workflow.

Args:
    task: Task description
    available_workflows: List of available workflow names

Returns:
    RouteResult with routing decision

**Tham số (Parameters):**

- `task` (str): Tham số task
- `available_workflows` (List): Tham số available_workflows

**Giá trị trả về (Returns):**

- `RouteResult`: Giá trị trả về

### Ví dụ sử dụng

**Ví dụ cơ bản sử dụng Reasoner**

```python
# Ví dụ sử dụng Reasoner
from agentic_sdlc.intelligence.reasoning.reasoner import Reasoner

# Tạo instance
obj = Reasoner()
```text

---

## Class `RouteResult`

**Mô tả:**

Result of routing decision.

### Constructor

#### `__init__`

**Chữ ký (Signature):**

```python
__init__(self, workflow: str, confidence: float, reasoning: str, alternatives: List[str]) -> None
```text

**Mô tả:**

Initialize self.  See help(type(self)) for accurate signature.

**Tham số (Parameters):**

- `workflow` (str): Tham số workflow
- `confidence` (float): Tham số confidence
- `reasoning` (str): Tham số reasoning
- `alternatives` (List): Tham số alternatives

**Giá trị trả về (Returns):**

- `None`: Giá trị trả về

### Methods

#### `__repr__`

**Chữ ký (Signature):**

```python
__repr__(self)
```text

**Mô tả:**

Return repr(self).

**Giá trị trả về (Returns):**

- `Any`: Giá trị trả về

### Ví dụ sử dụng

**Ví dụ cơ bản sử dụng RouteResult**

```python
# Ví dụ sử dụng RouteResult
from agentic_sdlc.intelligence.reasoning.reasoner import RouteResult

# Tạo instance
obj = RouteResult()
```text

---

## Class `TaskComplexity`

**Mô tả:**

Task complexity analysis result.

### Constructor

#### `__init__`

**Chữ ký (Signature):**

```python
__init__(self, score: int, factors: List[str], recommendation: str) -> None
```text

**Mô tả:**

Initialize self.  See help(type(self)) for accurate signature.

**Tham số (Parameters):**

- `score` (int): Tham số score
- `factors` (List): Tham số factors
- `recommendation` (str): Tham số recommendation

**Giá trị trả về (Returns):**

- `None`: Giá trị trả về

### Methods

#### `__repr__`

**Chữ ký (Signature):**

```python
__repr__(self)
```text

**Mô tả:**

Return repr(self).

**Giá trị trả về (Returns):**

- `Any`: Giá trị trả về

### Ví dụ sử dụng

**Ví dụ cơ bản sử dụng TaskComplexity**

```python
# Ví dụ sử dụng TaskComplexity
from agentic_sdlc.intelligence.reasoning.reasoner import TaskComplexity

# Tạo instance
obj = TaskComplexity()
```' has insufficient content
⚠️ **language_consistency**: Document in vi/ directory should contain Vietnamese content
❌ **syntax_error** (line 54): Python syntax error in code block: invalid syntax
❌ **syntax_error** (line 79): Python syntax error in code block: invalid syntax
❌ **syntax_error** (line 105): Python syntax error in code block: invalid syntax
❌ **syntax_error** (line 133): Python syntax error in code block: invalid syntax
❌ **syntax_error** (line 152): Python syntax error in code block: invalid syntax
❌ **syntax_error** (line 263): Python syntax error in code block: invalid syntax
❌ **syntax_error** (line 291): Python syntax error in code block: invalid syntax
❌ **syntax_error** (line 307): Python syntax error in code block: invalid syntax
❌ **syntax_error** (line 326): Python syntax error in code block: invalid syntax
❌ **syntax_error** (line 354): Python syntax error in code block: invalid syntax
❌ **syntax_error** (line 382): Python syntax error in code block: invalid syntax
❌ **syntax_error** (line 432): Python syntax error in code block: invalid syntax
❌ **syntax_error** (line 495): Python syntax error in code block: invalid syntax

### api-reference/orchestration/agent.md

❌ **missing_module_path**: API reference missing module path
⚠️ **empty_section**: Section 'Tổng Quan

Agent definitions and management.

---

## Classes

## Class `Agent`

**Mô tả:**

Represents an agent in the orchestration system.

An agent is an autonomous entity that can execute tasks, collaborate
with other agents, and maintain state across workflow executions.

### Constructor

#### `__init__`

**Chữ ký (Signature):**

```python
__init__(self, name: str, role: str, model_name: str, system_prompt: Optional[str] = None, tools: List[str] = <factory>, max_iterations: int = 10, id: str = <factory>, metadata: Dict[str, Any] = <factory>) -> None
```text

**Mô tả:**

Initialize self.  See help(type(self)) for accurate signature.

**Tham số (Parameters):**

- `name` (str): Tham số name
- `role` (str): Tham số role
- `model_name` (str): Tham số model_name
- `system_prompt` (Optional): Tham số system_prompt
- `tools` (List), mặc định: `<factory>`: Tham số tools
- `max_iterations` (int), mặc định: `10`: Tham số max_iterations
- `id` (str), mặc định: `<factory>`: Tham số id
- `metadata` (Dict), mặc định: `<factory>`: Tham số metadata

**Giá trị trả về (Returns):**

- `None`: Giá trị trả về

### Methods

#### `__repr__`

**Chữ ký (Signature):**

```python
__repr__(self)
```text

**Mô tả:**

Return repr(self).

**Giá trị trả về (Returns):**

- `Any`: Giá trị trả về

### Ví dụ sử dụng

**Ví dụ cơ bản sử dụng Agent**

```python
# Ví dụ sử dụng Agent
from agentic_sdlc.orchestration.agents.agent import Agent

# Tạo instance
obj = Agent()
```' has insufficient content
⚠️ **language_consistency**: Document in vi/ directory should contain Vietnamese content
ℹ️ **missing_translation**: Technical term 'Agent' appears frequently without Vietnamese explanation
❌ **syntax_error** (line 39): Python syntax error in code block: invalid syntax

### api-reference/orchestration/client.md

❌ **missing_module_path**: API reference missing module path
⚠️ **empty_section**: Section 'Tổng Quan

Model client for interacting with language models.

---

## Classes

## Class `ModelClient`

**Mô tả:**

Client for interacting with language models.

Provides a unified interface for communicating with different
language model providers.

### Constructor

#### `__init__`

**Chữ ký (Signature):**

```python
__init__(self, config: agentic_sdlc.orchestration.models.model_config.ModelConfig) -> None
```text

**Mô tả:**

Initialize the model client.

Args:
    config: The model configuration

**Tham số (Parameters):**

- `config` (ModelConfig): Tham số config

**Giá trị trả về (Returns):**

- `None`: Giá trị trả về

### Methods

#### `generate`

**Chữ ký (Signature):**

```python
generate(self, prompt: str, system_prompt: Optional[str] = None, **kwargs: Any) -> str
```text

**Mô tả:**

Generate a response from the model.

Args:
    prompt: The user prompt
    system_prompt: Optional system prompt
    **kwargs: Additional parameters for the model
    
Returns:
    The model's response
    
Raises:
    NotImplementedError: This is a base implementation

**Tham số (Parameters):**

- `prompt` (str): Tham số prompt
- `system_prompt` (Optional): Tham số system_prompt
- `kwargs` (Any): Tham số kwargs

**Giá trị trả về (Returns):**

- `str`: Giá trị trả về

**Ngoại lệ (Raises):**

- `NotImplementedError`

#### `generate_with_context`

**Chữ ký (Signature):**

```python
generate_with_context(self, prompt: str, context: Dict[str, Any], system_prompt: Optional[str] = None, **kwargs: Any) -> str
```text

**Mô tả:**

Generate a response with additional context.

Args:
    prompt: The user prompt
    context: Additional context information
    system_prompt: Optional system prompt
    **kwargs: Additional parameters for the model
    
Returns:
    The model's response

**Tham số (Parameters):**

- `prompt` (str): Tham số prompt
- `context` (Dict): Tham số context
- `system_prompt` (Optional): Tham số system_prompt
- `kwargs` (Any): Tham số kwargs

**Giá trị trả về (Returns):**

- `str`: Giá trị trả về

### Ví dụ sử dụng

**Ví dụ cơ bản sử dụng ModelClient**

```python
# Ví dụ sử dụng ModelClient
from agentic_sdlc.orchestration.models.client import ModelClient

# Tạo instance
obj = ModelClient()
```text

---

## Functions

## Function `create_model_client`

**Chữ ký (Signature):**

```python
create_model_client(config: agentic_sdlc.orchestration.models.model_config.ModelConfig) -> agentic_sdlc.orchestration.models.client.ModelClient
```text

**Mô tả:**

Create a model client from configuration.

Args:
    config: The model configuration
    
Returns:
    A new ModelClient instance

**Tham số (Parameters):**

- `config` (ModelConfig): Tham số config

**Giá trị trả về (Returns):**

- `ModelClient`: Giá trị trả về

**Ví dụ:**

```python
# Ví dụ sử dụng create_model_client
from agentic_sdlc.orchestration.models.client import create_model_client

result = create_model_client()
```text

---

## Function `get_model_client`

**Chữ ký (Signature):**

```python
get_model_client(provider: str, model_name: str) -> Optional[agentic_sdlc.orchestration.models.client.ModelClient]
```text

**Mô tả:**

Get a model client by provider and model name.

Args:
    provider: The model provider
    model_name: The model name
    
Returns:
    The ModelClient if found, None otherwise

**Tham số (Parameters):**

- `provider` (str): Tham số provider
- `model_name` (str): Tham số model_name

**Giá trị trả về (Returns):**

- `Optional`: Giá trị trả về

**Ví dụ:**

```python
# Ví dụ sử dụng get_model_client
from agentic_sdlc.orchestration.models.client import get_model_client

result = get_model_client()
```text

---

## Function `register_model_client`

**Chữ ký (Signature):**

```python
register_model_client(provider: str, model_name: str, client: agentic_sdlc.orchestration.models.client.ModelClient) -> None
```text

**Mô tả:**

Register a model client.

Args:
    provider: The model provider
    model_name: The model name
    client: The ModelClient instance

**Tham số (Parameters):**

- `provider` (str): Tham số provider
- `model_name` (str): Tham số model_name
- `client` (ModelClient): Tham số client

**Giá trị trả về (Returns):**

- `None`: Giá trị trả về

**Ví dụ:**

```python
# Ví dụ sử dụng register_model_client
from agentic_sdlc.orchestration.models.client import register_model_client

result = register_model_client()
```' has insufficient content
⚠️ **language_consistency**: Document in vi/ directory should contain Vietnamese content
❌ **syntax_error** (line 39): Python syntax error in code block: invalid syntax
❌ **syntax_error** (line 64): Python syntax error in code block: invalid syntax
❌ **syntax_error** (line 101): Python syntax error in code block: invalid syntax
❌ **syntax_error** (line 149): Python syntax error in code block: invalid syntax
❌ **syntax_error** (line 186): Python syntax error in code block: invalid syntax
❌ **syntax_error** (line 225): Python syntax error in code block: invalid syntax

### api-reference/orchestration/workflow.md

❌ **missing_module_path**: API reference missing module path
⚠️ **empty_section**: Section 'Tổng Quan

Workflow definitions and execution.

---

## Classes

## Class `Workflow`

**Mô tả:**

Represents a workflow definition.

A workflow is a sequence of steps executed by agents to accomplish
a specific goal or task.

### Constructor

#### `__init__`

**Chữ ký (Signature):**

```python
__init__(self, name: str, description: Optional[str] = None, steps: List[agentic_sdlc.orchestration.workflows.workflow.WorkflowStep] = <factory>, timeout: int = 300, id: str = <factory>, metadata: Dict[str, Any] = <factory>) -> None
```text

**Mô tả:**

Initialize self.  See help(type(self)) for accurate signature.

**Tham số (Parameters):**

- `name` (str): Tham số name
- `description` (Optional): Tham số description
- `steps` (List), mặc định: `<factory>`: Tham số steps
- `timeout` (int), mặc định: `300`: Tham số timeout
- `id` (str), mặc định: `<factory>`: Tham số id
- `metadata` (Dict), mặc định: `<factory>`: Tham số metadata

**Giá trị trả về (Returns):**

- `None`: Giá trị trả về

### Methods

#### `__repr__`

**Chữ ký (Signature):**

```python
__repr__(self)
```text

**Mô tả:**

Return repr(self).

**Giá trị trả về (Returns):**

- `Any`: Giá trị trả về

#### `add_step`

**Chữ ký (Signature):**

```python
add_step(self, step: agentic_sdlc.orchestration.workflows.workflow.WorkflowStep) -> None
```text

**Mô tả:**

Add a step to the workflow.

Args:
    step: The step to add

**Tham số (Parameters):**

- `step` (WorkflowStep): Tham số step

**Giá trị trả về (Returns):**

- `None`: Giá trị trả về

#### `get_step`

**Chữ ký (Signature):**

```python
get_step(self, name: str) -> Optional[agentic_sdlc.orchestration.workflows.workflow.WorkflowStep]
```text

**Mô tả:**

Get a step by name.

Args:
    name: The name of the step
    
Returns:
    The step if found, None otherwise

**Tham số (Parameters):**

- `name` (str): Tham số name

**Giá trị trả về (Returns):**

- `Optional`: Giá trị trả về

### Ví dụ sử dụng

**Ví dụ cơ bản sử dụng Workflow**

```python
# Ví dụ sử dụng Workflow
from agentic_sdlc.orchestration.workflows.workflow import Workflow

# Tạo instance
obj = Workflow()
```text

---

## Class `WorkflowStep`

**Mô tả:**

Represents a single step in a workflow.

### Constructor

#### `__init__`

**Chữ ký (Signature):**

```python
__init__(self, name: str, agent_id: str, description: Optional[str] = None, input_keys: List[str] = <factory>, output_keys: List[str] = <factory>, metadata: Dict[str, Any] = <factory>) -> None
```text

**Mô tả:**

Initialize self.  See help(type(self)) for accurate signature.

**Tham số (Parameters):**

- `name` (str): Tham số name
- `agent_id` (str): Tham số agent_id
- `description` (Optional): Tham số description
- `input_keys` (List), mặc định: `<factory>`: Tham số input_keys
- `output_keys` (List), mặc định: `<factory>`: Tham số output_keys
- `metadata` (Dict), mặc định: `<factory>`: Tham số metadata

**Giá trị trả về (Returns):**

- `None`: Giá trị trả về

### Methods

#### `__repr__`

**Chữ ký (Signature):**

```python
__repr__(self)
```text

**Mô tả:**

Return repr(self).

**Giá trị trả về (Returns):**

- `Any`: Giá trị trả về

### Ví dụ sử dụng

**Ví dụ cơ bản sử dụng WorkflowStep**

```python
# Ví dụ sử dụng WorkflowStep
from agentic_sdlc.orchestration.workflows.workflow import WorkflowStep

# Tạo instance
obj = WorkflowStep()
```' has insufficient content
⚠️ **language_consistency**: Document in vi/ directory should contain Vietnamese content
ℹ️ **missing_translation**: Technical term 'Workflow' appears frequently without Vietnamese explanation
❌ **syntax_error** (line 39): Python syntax error in code block: invalid syntax
❌ **syntax_error** (line 82): Python syntax error in code block: invalid syntax
❌ **syntax_error** (line 105): Python syntax error in code block: invalid syntax
❌ **syntax_error** (line 153): Python syntax error in code block: invalid syntax

### api-reference/plugins/base.md

❌ **missing_module_path**: API reference missing module path
⚠️ **empty_section**: Section 'Tổng Quan

Base classes and interfaces for the plugin system.

This module defines the plugin interface that all plugins must implement,
as well as metadata structures for plugin discovery and configuration.

---

## Classes

## Class `Plugin`

**Mô tả:**

Abstract base class for all plugins.

All plugins must inherit from this class and implement the required
abstract properties and methods. The plugin lifecycle consists of:

1. Instantiation: Plugin object is created
2. Initialization: initialize() is called with configuration
3. Operation: Plugin provides its functionality
4. Shutdown: shutdown() is called for cleanup

Example:
    >>> class MyPlugin(Plugin):
    ...     @property
    ...     def name(self) -> str:
    ...         return "my-plugin"
    ...
    ...     @property
    ...     def version(self) -> str:
    ...         return "1.0.0"
    ...
    ...     def initialize(self, config: Dict[str, Any]) -> None:
    ...         # Setup plugin with configuration
    ...         pass
    ...
    ...     def shutdown(self) -> None:
    ...         # Cleanup resources
    ...         pass

### Constructor

#### `__init__`

**Chữ ký (Signature):**

```python
__init__(self, /, *args, **kwargs)
```text

**Mô tả:**

Initialize self.  See help(type(self)) for accurate signature.

**Tham số (Parameters):**

- `args` (Any): Tham số args
- `kwargs` (Any): Tham số kwargs

**Giá trị trả về (Returns):**

- `None`: Giá trị trả về

### Properties

- `name` (str) (chỉ đọc): Get the plugin name.

Returns:
    Unique identifier for this plugin. Should be lowercase with hyphens
    (e.g., "my-plugin"). Must be consistent across plugin versions.
- `version` (str) (chỉ đọc): Get the plugin version.

Returns:
    Version string following semantic versioning (e.g., "1.0.0").
    Used for compatibility checking and dependency resolution.

### Methods

#### `initialize`

**Chữ ký (Signature):**

```python
initialize(self, config: Dict[str, Any]) -> None
```javascript

**Mô tả:**

Initialize the plugin with configuration.

This method is called once when the plugin is loaded. It should
perform any setup required for the plugin to function, such as:
- Validating configuration
- Initializing resources (connections, files, etc.)
- Registering handlers or callbacks
- Loading dependencies

Args:
    config: Configuration dictionary for this plugin. The structure
           depends on the plugin's requirements.

Raises:
    PluginError: If initialization fails for any reason. The error
                should include context about what failed and why.

**Tham số (Parameters):**

- `config` (Dict): Tham số config

**Giá trị trả về (Returns):**

- `None`: Giá trị trả về

**Ngoại lệ (Raises):**

- `PluginError`

#### `shutdown`

**Chữ ký (Signature):**

```python
shutdown(self) -> None
```text

**Mô tả:**

Shut down the plugin and clean up resources.

This method is called when the plugin is being unloaded. It should
perform cleanup such as:
- Closing connections
- Releasing file handles
- Unregistering handlers
- Freeing memory

This method should not raise exceptions. If cleanup fails, it should
log the error but not propagate it.

**Giá trị trả về (Returns):**

- `None`: Giá trị trả về

### Ví dụ sử dụng

**Ví dụ cơ bản sử dụng Plugin**

```python
# Ví dụ sử dụng Plugin
from agentic_sdlc.plugins.base import Plugin

# Tạo instance
obj = Plugin()
```python

---

## Class `PluginMetadata`

**Mô tả:**

Metadata describing a plugin.

This model contains information about a plugin including its identity,
version, dependencies, and configuration schema. It's used for plugin
discovery, validation, and documentation.

Attributes:
    name: Unique identifier for the plugin
    version: Plugin version following semantic versioning
    author: Plugin author or organization
    description: Human-readable description of plugin functionality
    dependencies: List of required Python packages
    entry_point: Fully qualified class name for plugin entry point
    config_schema: JSON schema for plugin configuration validation

### Constructor

#### `__init__`

**Chữ ký (Signature):**

```python
__init__(self, /, **data: 'Any') -> 'None'
```text

**Mô tả:**

Create a new model by parsing and validating input data from keyword arguments.

Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
validated to form a valid model.

`self` is explicitly positional-only to allow `self` as a field name.

**Tham số (Parameters):**

- `data` (Any): Tham số data

**Giá trị trả về (Returns):**

- `None`: Giá trị trả về

### Properties

- `model_extra` (dict[str, Any] | None) (chỉ đọc): Get extra fields set during validation.

Returns:
    A dictionary of extra fields, or `None` if `config.extra` is not set to `"allow"`.
- `model_fields_set` (set) (chỉ đọc): Returns the set of fields that have been explicitly set on this model instance.

Returns:
    A set of strings representing the fields that have been set,
        i.e. that were not filled from defaults.

### Methods

#### `__repr__`

**Chữ ký (Signature):**

```python
__repr__(self) -> 'str'
```text

**Mô tả:**

Return repr(self).

**Giá trị trả về (Returns):**

- `str`: Giá trị trả về

#### `__str__`

**Chữ ký (Signature):**

```python
__str__(self) -> 'str'
```text

**Mô tả:**

Return str(self).

**Giá trị trả về (Returns):**

- `str`: Giá trị trả về

#### `copy`

**Chữ ký (Signature):**

```python
copy(self, *, include: 'AbstractSetIntStr | MappingIntStrAny | None' = None, exclude: 'AbstractSetIntStr | MappingIntStrAny | None' = None, update: 'Dict[str, Any] | None' = None, deep: 'bool' = False) -> 'Self'
```text

**Mô tả:**

Returns a copy of the model.

!!! warning "Deprecated"
    This method is now deprecated; use `model_copy` instead.

If you need `include` or `exclude`, use:

```python {test="skip" lint="skip"}
data = self.model_dump(include=include, exclude=exclude, round_trip=True)
data = {**data, **(update or {})}
copied = self.model_validate(data)
```text

Args:
    include: Optional set or mapping specifying which fields to include in the copied model.
    exclude: Optional set or mapping specifying which fields to exclude in the copied model.
    update: Optional dictionary of field-value pairs to override field values in the copied model.
    deep: If True, the values of fields that are Pydantic models will be deep-copied.

Returns:
    A copy of the model with included, excluded and updated fields as specified.

**Tham số (Parameters):**

- `include` (AbstractSetIntStr | MappingIntStrAny | None): Tham số include
- `exclude` (AbstractSetIntStr | MappingIntStrAny | None): Tham số exclude
- `update` (Dict[str, Any] | None): Tham số update
- `deep` (bool), mặc định: `False`: Tham số deep

**Giá trị trả về (Returns):**

- `Self`: Giá trị trả về

#### `dict`

**Chữ ký (Signature):**

```python
dict(self, *, include: 'IncEx | None' = None, exclude: 'IncEx | None' = None, by_alias: 'bool' = False, exclude_unset: 'bool' = False, exclude_defaults: 'bool' = False, exclude_none: 'bool' = False) -> 'Dict[str, Any]'
```text

**Mô tả:**

Method dict

**Tham số (Parameters):**

- `include` (Union): Tham số include
- `exclude` (Union): Tham số exclude
- `by_alias` (bool), mặc định: `False`: Tham số by_alias
- `exclude_unset` (bool), mặc định: `False`: Tham số exclude_unset
- `exclude_defaults` (bool), mặc định: `False`: Tham số exclude_defaults
- `exclude_none` (bool), mặc định: `False`: Tham số exclude_none

**Giá trị trả về (Returns):**

- `Dict`: Giá trị trả về

#### `json`

**Chữ ký (Signature):**

```python
json(self, *, include: 'IncEx | None' = None, exclude: 'IncEx | None' = None, by_alias: 'bool' = False, exclude_unset: 'bool' = False, exclude_defaults: 'bool' = False, exclude_none: 'bool' = False, encoder: 'Callable[[Any], Any] | None' = PydanticUndefined, models_as_dict: 'bool' = PydanticUndefined, **dumps_kwargs: 'Any') -> 'str'
```text

**Mô tả:**

Method json

**Tham số (Parameters):**

- `include` (Union): Tham số include
- `exclude` (Union): Tham số exclude
- `by_alias` (bool), mặc định: `False`: Tham số by_alias
- `exclude_unset` (bool), mặc định: `False`: Tham số exclude_unset
- `exclude_defaults` (bool), mặc định: `False`: Tham số exclude_defaults
- `exclude_none` (bool), mặc định: `False`: Tham số exclude_none
- `encoder` (Optional), mặc định: `PydanticUndefined`: Tham số encoder
- `models_as_dict` (bool), mặc định: `PydanticUndefined`: Tham số models_as_dict
- `dumps_kwargs` (Any): Tham số dumps_kwargs

**Giá trị trả về (Returns):**

- `str`: Giá trị trả về

#### `model_copy`

**Chữ ký (Signature):**

```python
model_copy(self, *, update: 'Mapping[str, Any] | None' = None, deep: 'bool' = False) -> 'Self'
```text

**Mô tả:**

!!! abstract "Usage Documentation"
    [`model_copy`](../concepts/models.md#model-copy)

Returns a copy of the model.

!!! note
    The underlying instance's [`__dict__`][object.__dict__] attribute is copied. This
    might have unexpected side effects if you store anything in it, on top of the model
    fields (e.g. the value of [cached properties][functools.cached_property]).

Args:
    update: Values to change/add in the new model. Note: the data is not validated
        before creating the new model. You should trust this data.
    deep: Set to `True` to make a deep copy of the model.

Returns:
    New model instance.

**Tham số (Parameters):**

- `update` (collections.abc.Mapping[str, Any] | None): Tham số update
- `deep` (bool), mặc định: `False`: Tham số deep

**Giá trị trả về (Returns):**

- `Self`: Giá trị trả về

#### `model_dump`

**Chữ ký (Signature):**

```python
model_dump(self, *, mode: "Literal['json', 'python'] | str" = 'python', include: 'IncEx | None' = None, exclude: 'IncEx | None' = None, context: 'Any | None' = None, by_alias: 'bool | None' = None, exclude_unset: 'bool' = False, exclude_defaults: 'bool' = False, exclude_none: 'bool' = False, exclude_computed_fields: 'bool' = False, round_trip: 'bool' = False, warnings: "bool | Literal['none', 'warn', 'error']" = True, fallback: 'Callable[[Any], Any] | None' = None, serialize_as_any: 'bool' = False) -> 'dict[str, Any]'
```javascript

**Mô tả:**

!!! abstract "Usage Documentation"
    [`model_dump`](../concepts/serialization.md#python-mode)

Generate a dictionary representation of the model, optionally specifying which fields to include or exclude.

Args:
    mode: The mode in which `to_python` should run.
        If mode is 'json', the output will only contain JSON serializable types.
        If mode is 'python', the output may contain non-JSON-serializable Python objects.
    include: A set of fields to include in the output.
    exclude: A set of fields to exclude from the output.
    context: Additional context to pass to the serializer.
    by_alias: Whether to use the field's alias in the dictionary key if defined.
    exclude_unset: Whether to exclude fields that have not been explicitly set.
    exclude_defaults: Whether to exclude fields that are set to their default value.
    exclude_none: Whether to exclude fields that have a value of `None`.
    exclude_computed_fields: Whether to exclude computed fields.
        While this can be useful for round-tripping, it is usually recommended to use the dedicated
        `round_trip` parameter instead.
    round_trip: If True, dumped values should be valid as input for non-idempotent types such as Json[T].
    warnings: How to handle serialization errors. False/"none" ignores them, True/"warn" logs errors,
        "error" raises a [`PydanticSerializationError`][pydantic_core.PydanticSerializationError].
    fallback: A function to call when an unknown value is encountered. If not provided,
        a [`PydanticSerializationError`][pydantic_core.PydanticSerializationError] error is raised.
    serialize_as_any: Whether to serialize fields with duck-typing serialization behavior.

Returns:
    A dictionary representation of the model.

**Tham số (Parameters):**

- `mode` (Union), mặc định: `python`: Tham số mode
- `include` (Union): Tham số include
- `exclude` (Union): Tham số exclude
- `context` (Any | None): Tham số context
- `by_alias` (bool | None): Tham số by_alias
- `exclude_unset` (bool), mặc định: `False`: Tham số exclude_unset
- `exclude_defaults` (bool), mặc định: `False`: Tham số exclude_defaults
- `exclude_none` (bool), mặc định: `False`: Tham số exclude_none
- `exclude_computed_fields` (bool), mặc định: `False`: Tham số exclude_computed_fields
- `round_trip` (bool), mặc định: `False`: Tham số round_trip
- `warnings` (Union), mặc định: `True`: Tham số warnings
- `fallback` (Optional): Tham số fallback
- `serialize_as_any` (bool), mặc định: `False`: Tham số serialize_as_any

**Giá trị trả về (Returns):**

- `dict`: Giá trị trả về

#### `model_dump_json`

**Chữ ký (Signature):**

```python
model_dump_json(self, *, indent: 'int | None' = None, ensure_ascii: 'bool' = False, include: 'IncEx | None' = None, exclude: 'IncEx | None' = None, context: 'Any | None' = None, by_alias: 'bool | None' = None, exclude_unset: 'bool' = False, exclude_defaults: 'bool' = False, exclude_none: 'bool' = False, exclude_computed_fields: 'bool' = False, round_trip: 'bool' = False, warnings: "bool | Literal['none', 'warn', 'error']" = True, fallback: 'Callable[[Any], Any] | None' = None, serialize_as_any: 'bool' = False) -> 'str'
```javascript

**Mô tả:**

!!! abstract "Usage Documentation"
    [`model_dump_json`](../concepts/serialization.md#json-mode)

Generates a JSON representation of the model using Pydantic's `to_json` method.

Args:
    indent: Indentation to use in the JSON output. If None is passed, the output will be compact.
    ensure_ascii: If `True`, the output is guaranteed to have all incoming non-ASCII characters escaped.
        If `False` (the default), these characters will be output as-is.
    include: Field(s) to include in the JSON output.
    exclude: Field(s) to exclude from the JSON output.
    context: Additional context to pass to the serializer.
    by_alias: Whether to serialize using field aliases.
    exclude_unset: Whether to exclude fields that have not been explicitly set.
    exclude_defaults: Whether to exclude fields that are set to their default value.
    exclude_none: Whether to exclude fields that have a value of `None`.
    exclude_computed_fields: Whether to exclude computed fields.
        While this can be useful for round-tripping, it is usually recommended to use the dedicated
        `round_trip` parameter instead.
    round_trip: If True, dumped values should be valid as input for non-idempotent types such as Json[T].
    warnings: How to handle serialization errors. False/"none" ignores them, True/"warn" logs errors,
        "error" raises a [`PydanticSerializationError`][pydantic_core.PydanticSerializationError].
    fallback: A function to call when an unknown value is encountered. If not provided,
        a [`PydanticSerializationError`][pydantic_core.PydanticSerializationError] error is raised.
    serialize_as_any: Whether to serialize fields with duck-typing serialization behavior.

Returns:
    A JSON string representation of the model.

**Tham số (Parameters):**

- `indent` (int | None): Tham số indent
- `ensure_ascii` (bool), mặc định: `False`: Tham số ensure_ascii
- `include` (Union): Tham số include
- `exclude` (Union): Tham số exclude
- `context` (Any | None): Tham số context
- `by_alias` (bool | None): Tham số by_alias
- `exclude_unset` (bool), mặc định: `False`: Tham số exclude_unset
- `exclude_defaults` (bool), mặc định: `False`: Tham số exclude_defaults
- `exclude_none` (bool), mặc định: `False`: Tham số exclude_none
- `exclude_computed_fields` (bool), mặc định: `False`: Tham số exclude_computed_fields
- `round_trip` (bool), mặc định: `False`: Tham số round_trip
- `warnings` (Union), mặc định: `True`: Tham số warnings
- `fallback` (Optional): Tham số fallback
- `serialize_as_any` (bool), mặc định: `False`: Tham số serialize_as_any

**Giá trị trả về (Returns):**

- `str`: Giá trị trả về

#### `model_post_init`

**Chữ ký (Signature):**

```python
model_post_init(self, context: 'Any', /) -> 'None'
```text

**Mô tả:**

Override this method to perform additional initialization after `__init__` and `model_construct`.
This is useful if you want to do some validation that requires the entire model to be initialized.

**Tham số (Parameters):**

- `context` (Any): Tham số context

**Giá trị trả về (Returns):**

- `None`: Giá trị trả về

### Ví dụ sử dụng

**Ví dụ cơ bản sử dụng PluginMetadata**

```python
# Ví dụ sử dụng PluginMetadata
from agentic_sdlc.plugins.base import PluginMetadata

# Tạo instance
obj = PluginMetadata()
```' has insufficient content
⚠️ **language_consistency**: Document in vi/ directory should contain Vietnamese content
ℹ️ **missing_translation**: Technical term 'Plugin' appears frequently without Vietnamese explanation
❌ **syntax_error** (line 65): Python syntax error in code block: invalid syntax
❌ **syntax_error** (line 101): Python syntax error in code block: invalid syntax
❌ **syntax_error** (line 140): Python syntax error in code block: invalid syntax
❌ **syntax_error** (line 201): Python syntax error in code block: invalid syntax
❌ **syntax_error** (line 240): Python syntax error in code block: invalid syntax
❌ **syntax_error** (line 256): Python syntax error in code block: invalid syntax
❌ **syntax_error** (line 272): Python syntax error in code block: invalid syntax
❌ **broken_link** (line 374): Broken link to '../concepts/models.md#model-copy' (text: '`model_copy`')
❌ **broken_link** (line 411): Broken link to '../concepts/serialization.md#python-mode' (text: '`model_dump`')
❌ **broken_link** (line 470): Broken link to '../concepts/serialization.md#json-mode' (text: '`model_dump_json`')

### api-reference/plugins/registry.md

❌ **missing_module_path**: API reference missing module path
⚠️ **empty_section**: Section 'Tổng Quan

Plugin registry for managing plugin lifecycle and discovery.

This module provides the PluginRegistry class which handles plugin registration,
validation, loading, and lifecycle management. It ensures plugins implement
the required interface and isolates plugin failures from SDK operation.

---

## Classes

## Class `PluginRegistry`

**Mô tả:**

Registry for managing plugins.

The PluginRegistry maintains a collection of loaded plugins and provides
methods for registration, retrieval, and lifecycle management. It validates
that plugins implement the required interface and isolates plugin failures
to prevent them from crashing the SDK.

Features:
- Plugin registration with interface validation
- Plugin retrieval by name
- Plugin unregistration
- Loading plugins from setuptools entry points
- Error isolation to prevent plugin failures from crashing SDK
- Comprehensive logging of plugin operations

Example:
    >>> registry = PluginRegistry()
    >>> registry.register(my_plugin)
    >>> plugin = registry.get("my-plugin")
    >>> registry.unregister("my-plugin")

### Constructor

#### `__init__`

**Chữ ký (Signature):**

```python
__init__(self) -> None
```text

**Mô tả:**

Initialize an empty plugin registry.

**Giá trị trả về (Returns):**

- `None`: Giá trị trả về

### Methods

#### `get`

**Chữ ký (Signature):**

```python
get(self, name: str) -> Optional[agentic_sdlc.plugins.base.Plugin]
```text

**Mô tả:**

Get a registered plugin by name.

Args:
    name: Name of the plugin to retrieve

Returns:
    Plugin instance if found, None otherwise

**Tham số (Parameters):**

- `name` (str): Tham số name

**Giá trị trả về (Returns):**

- `Optional`: Giá trị trả về

#### `load_from_entry_points`

**Chữ ký (Signature):**

```python
load_from_entry_points(self) -> None
```text

**Mô tả:**

Load plugins from setuptools entry points.

Discovers and loads plugins registered via setuptools entry points
under the 'agentic_sdlc.plugins' group. Each plugin is loaded with
error isolation - if one plugin fails to load, others continue loading.

Entry point format in setup.py or pyproject.toml:
    [project.entry-points."agentic_sdlc.plugins"]
    my-plugin = "my_package.plugins:MyPlugin"

Logs information about each plugin loaded and any errors encountered.

**Giá trị trả về (Returns):**

- `None`: Giá trị trả về

#### `register`

**Chữ ký (Signature):**

```python
register(self, plugin: agentic_sdlc.plugins.base.Plugin) -> None
```text

**Mô tả:**

Register a plugin with the registry.

Validates that the plugin implements the required Plugin interface
before registration. If validation fails, raises PluginError with
details about missing methods or properties.

Args:
    plugin: Plugin instance to register

Raises:
    PluginError: If plugin doesn't implement required interface or
                if a plugin with the same name is already registered

**Tham số (Parameters):**

- `plugin` (Plugin): Tham số plugin

**Giá trị trả về (Returns):**

- `None`: Giá trị trả về

**Ngoại lệ (Raises):**

- `PluginError`

#### `unregister`

**Chữ ký (Signature):**

```python
unregister(self, name: str) -> None
```text

**Mô tả:**

Unregister a plugin from the registry.

Calls the plugin's shutdown() method before removing it from the registry.
If shutdown fails, logs the error but continues with unregistration.

Args:
    name: Name of the plugin to unregister

Raises:
    PluginError: If plugin is not found in registry

**Tham số (Parameters):**

- `name` (str): Tham số name

**Giá trị trả về (Returns):**

- `None`: Giá trị trả về

**Ngoại lệ (Raises):**

- `PluginError`

### Ví dụ sử dụng

**Ví dụ cơ bản sử dụng PluginRegistry**

```python
# Ví dụ sử dụng PluginRegistry
from agentic_sdlc.plugins.registry import PluginRegistry

# Tạo instance
obj = PluginRegistry()
```text

---

## Functions

## Function `get_plugin_registry`

**Chữ ký (Signature):**

```python
get_plugin_registry() -> agentic_sdlc.plugins.registry.PluginRegistry
```text

**Mô tả:**

Get the global plugin registry singleton.

Returns:
    The global PluginRegistry instance, creating it if necessary

**Giá trị trả về (Returns):**

- `PluginRegistry`: Giá trị trả về

**Ví dụ:**

```python
# Ví dụ sử dụng get_plugin_registry
from agentic_sdlc.plugins.registry import get_plugin_registry

result = get_plugin_registry()
```' has insufficient content
⚠️ **language_consistency**: Document in vi/ directory should contain Vietnamese content
ℹ️ **missing_translation**: Technical term 'Plugin' appears frequently without Vietnamese explanation
❌ **syntax_error** (line 59): Python syntax error in code block: invalid syntax
❌ **syntax_error** (line 77): Python syntax error in code block: invalid syntax
❌ **syntax_error** (line 103): Python syntax error in code block: invalid syntax
❌ **syntax_error** (line 129): Python syntax error in code block: invalid syntax
❌ **syntax_error** (line 164): Python syntax error in code block: invalid syntax
❌ **syntax_error** (line 213): Python syntax error in code block: invalid syntax

### diagrams/agent-interaction.md

⚠️ **language_consistency**: Document in vi/ directory should contain Vietnamese content
ℹ️ **missing_translation**: Technical term 'Agent' appears frequently without Vietnamese explanation
ℹ️ **missing_translation**: Technical term 'API' appears frequently without Vietnamese explanation

### diagrams/architecture.md

⚠️ **language_consistency**: Document in vi/ directory should contain Vietnamese content
ℹ️ **missing_translation**: Technical term 'Agent' appears frequently without Vietnamese explanation
ℹ️ **missing_translation**: Technical term 'Workflow' appears frequently without Vietnamese explanation
ℹ️ **missing_translation**: Technical term 'Plugin' appears frequently without Vietnamese explanation
ℹ️ **missing_translation**: Technical term 'CLI' appears frequently without Vietnamese explanation
ℹ️ **missing_translation**: Technical term 'API' appears frequently without Vietnamese explanation
ℹ️ **missing_translation**: Technical term 'SDK' appears frequently without Vietnamese explanation

### diagrams/data-flow.md

⚠️ **language_consistency**: Document in vi/ directory should contain Vietnamese content
ℹ️ **missing_translation**: Technical term 'Agent' appears frequently without Vietnamese explanation
ℹ️ **missing_translation**: Technical term 'Workflow' appears frequently without Vietnamese explanation
ℹ️ **missing_translation**: Technical term 'Plugin' appears frequently without Vietnamese explanation
ℹ️ **missing_translation**: Technical term 'API' appears frequently without Vietnamese explanation

### diagrams/workflows.md

⚠️ **language_consistency**: Document in vi/ directory should contain Vietnamese content
ℹ️ **missing_translation**: Technical term 'Agent' appears frequently without Vietnamese explanation
ℹ️ **missing_translation**: Technical term 'Workflow' appears frequently without Vietnamese explanation
ℹ️ **missing_translation**: Technical term 'CLI' appears frequently without Vietnamese explanation

### getting-started/configuration.md

⚠️ **heading_hierarchy**: Heading hierarchy skip detected: 'Các Tham Số Quan Trọng' (level 3 after level 1)
⚠️ **heading_hierarchy**: Heading hierarchy skip detected: 'Các Models OpenAI Được Hỗ Trợ' (level 4 after level 1)
⚠️ **heading_hierarchy**: Heading hierarchy skip detected: 'Các Models Claude Được Hỗ Trợ' (level 4 after level 1)
⚠️ **heading_hierarchy**: Heading hierarchy skip detected: 'Cài Đặt Ollama' (level 4 after level 1)
⚠️ **heading_hierarchy**: Heading hierarchy skip detected: 'Các Models Ollama Phổ Biến' (level 4 after level 1)
⚠️ **heading_hierarchy**: Heading hierarchy skip detected: 'Ví Dụ Đầy Đủ' (level 4 after level 1)
⚠️ **heading_hierarchy**: Heading hierarchy skip detected: 'Python Code' (level 4 after level 1)
⚠️ **heading_hierarchy**: Heading hierarchy skip detected: '2. Environment-Specific Configuration' (level 3 after level 1)
⚠️ **heading_hierarchy**: Heading hierarchy skip detected: '3. Configuration Versioning' (level 3 after level 1)
⚠️ **heading_hierarchy**: Heading hierarchy skip detected: '4. Documentation trong Config' (level 3 after level 1)
⚠️ **heading_hierarchy**: Heading hierarchy skip detected: '5. Validation Rules' (level 3 after level 1)
⚠️ **heading_hierarchy**: Heading hierarchy skip detected: 'Lỗi 2: Invalid YAML Syntax' (level 3 after level 1)
⚠️ **heading_hierarchy**: Heading hierarchy skip detected: 'Lỗi 4: Invalid Model Configuration' (level 3 after level 1)
⚠️ **language_consistency**: Document in vi/ directory should contain Vietnamese content
ℹ️ **missing_translation**: Technical term 'Agent' appears frequently without Vietnamese explanation
ℹ️ **missing_translation**: Technical term 'Workflow' appears frequently without Vietnamese explanation
ℹ️ **missing_translation**: Technical term 'API' appears frequently without Vietnamese explanation
⚠️ **empty_code_block** (line 813): Empty text code block found
⚠️ **missing_language** (line 386): Code block missing language specification
⚠️ **missing_language** (line 890): Code block missing language specification
⚠️ **missing_language** (line 905): Code block missing language specification
⚠️ **missing_language** (line 916): Code block missing language specification
⚠️ **missing_language** (line 931): Code block missing language specification
❌ **broken_link** (line 945): Broken link to 'first-workflow.md' (text: 'First Workflow Guide')
❌ **broken_link** (line 946): Broken link to '../api-reference/orchestration/model-client.md' (text: 'Model Client API Reference')

### getting-started/installation.md

⚠️ **heading_hierarchy**: Heading hierarchy skip detected: '2. Cấu Hình API Keys' (level 3 after level 1)
⚠️ **heading_hierarchy**: Heading hierarchy skip detected: '3. Tạo File Cấu Hình' (level 3 after level 1)
⚠️ **heading_hierarchy**: Heading hierarchy skip detected: '2. Kiểm Tra CLI Commands (nếu đã cài CLI)' (level 3 after level 1)
⚠️ **heading_hierarchy**: Heading hierarchy skip detected: '3. Chạy Test Script' (level 3 after level 1)
⚠️ **heading_hierarchy**: Heading hierarchy skip detected: 'Lỗi 2: ImportError với Dependencies' (level 3 after level 1)
⚠️ **heading_hierarchy**: Heading hierarchy skip detected: 'Lỗi 3: API Key Errors' (level 3 after level 1)
⚠️ **heading_hierarchy**: Heading hierarchy skip detected: 'Lỗi 4: Permission Errors' (level 3 after level 1)
⚠️ **heading_hierarchy**: Heading hierarchy skip detected: 'Lỗi 5: Version Conflicts' (level 3 after level 1)
⚠️ **heading_hierarchy**: Heading hierarchy skip detected: 'Lỗi 6: SSL Certificate Errors' (level 3 after level 1)
⚠️ **heading_hierarchy**: Heading hierarchy skip detected: 'Lỗi 7: Memory Errors' (level 3 after level 1)
⚠️ **heading_hierarchy**: Heading hierarchy skip detected: 'Lỗi 9: Python Version Incompatibility' (level 3 after level 1)
⚠️ **heading_hierarchy**: Heading hierarchy skip detected: 'Lỗi 10: Configuration File Not Found' (level 3 after level 1)
⚠️ **language_consistency**: Document in vi/ directory should contain Vietnamese content
ℹ️ **missing_translation**: Technical term 'Workflow' appears frequently without Vietnamese explanation
ℹ️ **missing_translation**: Technical term 'CLI' appears frequently without Vietnamese explanation
ℹ️ **missing_translation**: Technical term 'API' appears frequently without Vietnamese explanation
⚠️ **missing_language** (line 254): Code block missing language specification
⚠️ **missing_language** (line 272): Code block missing language specification
⚠️ **missing_language** (line 400): Code block missing language specification
⚠️ **missing_language** (line 423): Code block missing language specification
⚠️ **missing_language** (line 445): Code block missing language specification
⚠️ **missing_language** (line 467): Code block missing language specification
⚠️ **missing_language** (line 488): Code block missing language specification
⚠️ **missing_language** (line 512): Code block missing language specification
⚠️ **missing_language** (line 530): Code block missing language specification
⚠️ **missing_language** (line 545): Code block missing language specification
⚠️ **missing_language** (line 563): Code block missing language specification
⚠️ **missing_language** (line 588): Code block missing language specification
❌ **broken_link** (line 619): Broken link to 'first-workflow.md' (text: 'First Workflow Guide')

### guides/advanced/deployment.md

⚠️ **heading_hierarchy**: Heading hierarchy skip detected: '2. Configuration Management' (level 3 after level 1)
⚠️ **heading_hierarchy**: Heading hierarchy skip detected: '3. Running Locally' (level 3 after level 1)
⚠️ **heading_hierarchy**: Heading hierarchy skip detected: '2. Docker Compose' (level 3 after level 1)
⚠️ **heading_hierarchy**: Heading hierarchy skip detected: '3. Building và Running' (level 3 after level 1)
⚠️ **heading_hierarchy**: Heading hierarchy skip detected: '2. Helm Chart' (level 3 after level 1)
⚠️ **heading_hierarchy**: Heading hierarchy skip detected: '3. Deploying to Kubernetes' (level 3 after level 1)
⚠️ **heading_hierarchy**: Heading hierarchy skip detected: '2. Grafana Dashboards' (level 3 after level 1)
⚠️ **heading_hierarchy**: Heading hierarchy skip detected: '2. GitLab CI' (level 3 after level 1)
⚠️ **language_consistency**: Document in vi/ directory should contain Vietnamese content
❌ **syntax_error** (line 61): Python syntax error in code block: invalid syntax
❌ **syntax_error** (line 87): Python syntax error in code block: invalid syntax

### guides/advanced/performance.md

⚠️ **heading_hierarchy**: Heading hierarchy skip detected: '2. Agent Configuration Tuning' (level 3 after level 1)
⚠️ **heading_hierarchy**: Heading hierarchy skip detected: '3. Workflow Optimization' (level 3 after level 1)
⚠️ **heading_hierarchy**: Heading hierarchy skip detected: '2. Workflow Result Caching' (level 3 after level 1)
⚠️ **heading_hierarchy**: Heading hierarchy skip detected: '2. Parallel Workflow Steps' (level 3 after level 1)
⚠️ **heading_hierarchy**: Heading hierarchy skip detected: '2. Load Testing' (level 3 after level 1)
⚠️ **heading_hierarchy**: Heading hierarchy skip detected: '3. Memory Profiling' (level 3 after level 1)
⚠️ **heading_hierarchy**: Heading hierarchy skip detected: '❌ Anti-Pattern 2: No Caching' (level 3 after level 1)
⚠️ **heading_hierarchy**: Heading hierarchy skip detected: '❌ Anti-Pattern 3: Unbounded Resource Usage' (level 3 after level 1)
⚠️ **language_consistency**: Document in vi/ directory should contain Vietnamese content
ℹ️ **missing_translation**: Technical term 'Agent' appears frequently without Vietnamese explanation
ℹ️ **missing_translation**: Technical term 'Workflow' appears frequently without Vietnamese explanation
ℹ️ **missing_translation**: Technical term 'API' appears frequently without Vietnamese explanation
❌ **broken_reference** (line 455): Broken reference link ''average'' to '.2f}s")'
❌ **broken_reference** (line 503): Broken reference link ''requests_per_second'' to '.2f}")'
❌ **broken_reference** (line 504): Broken reference link ''avg_response_time'' to '.3f}s")'

### guides/advanced/scalability.md

⚠️ **heading_hierarchy**: Heading hierarchy skip detected: '2. Horizontal Scaling' (level 3 after level 1)
⚠️ **heading_hierarchy**: Heading hierarchy skip detected: '2. Load Balancing' (level 3 after level 1)
⚠️ **heading_hierarchy**: Heading hierarchy skip detected: '3. Distributed State Management' (level 3 after level 1)
⚠️ **heading_hierarchy**: Heading hierarchy skip detected: '2. Fault Tolerance' (level 3 after level 1)
⚠️ **heading_hierarchy**: Heading hierarchy skip detected: '2. Auto-Scaling' (level 3 after level 1)
⚠️ **heading_hierarchy**: Heading hierarchy skip detected: '2. Minimize Network Calls' (level 3 after level 1)
⚠️ **heading_hierarchy**: Heading hierarchy skip detected: '3. Use Async Communication' (level 3 after level 1)
⚠️ **language_consistency**: Document in vi/ directory should contain Vietnamese content
❌ **broken_reference** (line 636): Broken reference link '"healthy"' to 'health["healthy_nodes"] += 1'

### guides/advanced/security.md

⚠️ **heading_hierarchy**: Heading hierarchy skip detected: '2. Secrets Management' (level 3 after level 1)
⚠️ **heading_hierarchy**: Heading hierarchy skip detected: '3. Key Rotation' (level 3 after level 1)
⚠️ **heading_hierarchy**: Heading hierarchy skip detected: '2. Encryption in Transit' (level 3 after level 1)
⚠️ **heading_hierarchy**: Heading hierarchy skip detected: '3. Secure Storage' (level 3 after level 1)
⚠️ **heading_hierarchy**: Heading hierarchy skip detected: '2. Authentication' (level 3 after level 1)
⚠️ **heading_hierarchy**: Heading hierarchy skip detected: '3. API Authentication' (level 3 after level 1)
⚠️ **heading_hierarchy**: Heading hierarchy skip detected: '2. Monitoring Security Metrics' (level 3 after level 1)
⚠️ **heading_hierarchy**: Heading hierarchy skip detected: '2. Defense in Depth' (level 3 after level 1)
⚠️ **heading_hierarchy**: Heading hierarchy skip detected: '3. Regular Security Audits' (level 3 after level 1)
⚠️ **heading_hierarchy**: Heading hierarchy skip detected: '❌ Pitfall 2: Insufficient Input Validation' (level 3 after level 1)
⚠️ **heading_hierarchy**: Heading hierarchy skip detected: '❌ Pitfall 3: Logging Sensitive Data' (level 3 after level 1)
⚠️ **language_consistency**: Document in vi/ directory should contain Vietnamese content
ℹ️ **missing_translation**: Technical term 'API' appears frequently without Vietnamese explanation
❌ **broken_reference** (line 502): Broken reference link '"password_hash"' to 'raise ValueError("Invalid username or password")'

### guides/agents/agent-lifecycle.md

⚠️ **heading_hierarchy**: Heading hierarchy skip detected: 'Validation During Creation' (level 3 after level 1)
⚠️ **heading_hierarchy**: Heading hierarchy skip detected: 'Creation Events' (level 3 after level 1)
⚠️ **heading_hierarchy**: Heading hierarchy skip detected: 'Manual Registration' (level 3 after level 1)
⚠️ **heading_hierarchy**: Heading hierarchy skip detected: 'Registration Validation' (level 3 after level 1)
⚠️ **heading_hierarchy**: Heading hierarchy skip detected: 'Dynamic Reconfiguration' (level 3 after level 1)
⚠️ **heading_hierarchy**: Heading hierarchy skip detected: 'Configuration Validation' (level 3 after level 1)
⚠️ **heading_hierarchy**: Heading hierarchy skip detected: 'Execution States' (level 3 after level 1)
⚠️ **heading_hierarchy**: Heading hierarchy skip detected: 'Iteration Management' (level 3 after level 1)
⚠️ **heading_hierarchy**: Heading hierarchy skip detected: 'Health Checks' (level 3 after level 1)
⚠️ **heading_hierarchy**: Heading hierarchy skip detected: 'Activity Logging' (level 3 after level 1)
⚠️ **heading_hierarchy**: Heading hierarchy skip detected: 'Message Passing' (level 3 after level 1)
⚠️ **heading_hierarchy**: Heading hierarchy skip detected: 'Collaboration Patterns' (level 3 after level 1)
⚠️ **heading_hierarchy**: Heading hierarchy skip detected: 'Performance Optimization' (level 3 after level 1)
⚠️ **heading_hierarchy**: Heading hierarchy skip detected: 'Remove from Registry' (level 3 after level 1)
⚠️ **heading_hierarchy**: Heading hierarchy skip detected: 'Cleanup Resources' (level 3 after level 1)
⚠️ **heading_hierarchy**: Heading hierarchy skip detected: '2. Regular Monitoring' (level 3 after level 1)
⚠️ **heading_hierarchy**: Heading hierarchy skip detected: '3. Graceful Degradation' (level 3 after level 1)
⚠️ **language_consistency**: Document in vi/ directory should contain Vietnamese content
ℹ️ **missing_translation**: Technical term 'Agent' appears frequently without Vietnamese explanation
❌ **broken_reference** (line 25): Broken reference link '*' to 'Remove from registry'
❌ **broken_reference** (line 424): Broken reference link '"issues"' to 'print(f"Issues: {', '.join(health['issues'])}")'

### guides/agents/agent-types.md

⚠️ **empty_section**: Section 'Giới Thiệu

Agentic SDLC hỗ trợ nhiều loại agents chuyên biệt, mỗi loại được thiết kế cho một vai trò cụ thể trong software development lifecycle. Tài liệu này mô tả chi tiết 18 loại agents phổ biến, chức năng, và cách sử dụng của từng loại.

## Agent Types Overview

### Core Agent Types

Các agent types được định nghĩa trong enum `AgentType`:

```python
from models.enums import AgentType

# Core agent types
AgentType.BA              # Business Analyst
AgentType.PM              # Project Manager
AgentType.SA              # Software Architect
AgentType.IMPLEMENTATION  # Implementation Developer
AgentType.RESEARCH        # Research Specialist
AgentType.QUALITY_JUDGE   # Quality Assurance
AgentType.CUSTOM          # Custom Agent
```text

## 1. Business Analyst (BA)

### Mô Tả

Business Analyst agent chuyên về phân tích yêu cầu nghiệp vụ, thu thập requirements, và tạo specifications.

### Chức Năng Chính

- Phân tích business requirements
- Tạo user stories và use cases
- Định nghĩa acceptance criteria
- Stakeholder communication
- Requirements documentation

### Ví Dụ

```python
from agentic_sdlc import create_agent

ba_agent = create_agent(
    name="business-analyst",
    role="Business Analyst",
    model_name="gpt-4",
    system_prompt="""Bạn là Business Analyst chuyên nghiệp.
    
    Nhiệm vụ:
    - Phân tích business requirements từ stakeholders
    - Tạo detailed user stories với acceptance criteria
    - Identify business rules và constraints
    - Document functional và non-functional requirements
    - Facilitate communication giữa business và technical teams
    
    Output format:
    - User stories: As a [role], I want [feature] so that [benefit]
    - Acceptance criteria: Given-When-Then format
    - Business rules: Clear và testable
    """,
    metadata={
        "agent_type": "BA",
        "expertise": ["requirements-analysis", "user-stories", "business-rules"]
    }
)
```text


## 2. Project Manager (PM)

### Mô Tả

Project Manager agent quản lý project planning, task allocation, timeline tracking, và team coordination.

### Chức Năng Chính

- Project planning và scheduling
- Resource allocation
- Risk management
- Progress tracking
- Team coordination
- Stakeholder reporting

### Ví Dụ

```python
pm_agent = create_agent(
    name="project-manager",
    role="Project Manager",
    model_name="gpt-4",
    system_prompt="""Bạn là Project Manager có kinh nghiệm.
    
    Nhiệm vụ:
    - Create và maintain project plans
    - Allocate tasks to team members
    - Track progress và identify blockers
    - Manage risks và dependencies
    - Facilitate team communication
    - Report status to stakeholders
    
    Bạn sử dụng:
    - Agile/Scrum methodologies
    - Gantt charts và burndown charts
    - Risk matrices
    - Status reports
    """,
    metadata={
        "agent_type": "PM",
        "methodologies": ["agile", "scrum", "kanban"]
    }
)
```text

## 3. Software Architect (SA)

### Mô Tả

Software Architect agent thiết kế system architecture, technical decisions, và architectural patterns.

### Chức Năng Chính

- System architecture design
- Technology stack selection
- Design patterns application
- Scalability planning
- Technical documentation
- Architecture reviews

### Ví Dụ

```python
sa_agent = create_agent(
    name="software-architect",
    role="Software Architect",
    model_name="gpt-4-turbo",
    system_prompt="""Bạn là Software Architect senior.
    
    Expertise:
    - Microservices architecture
    - Cloud-native design
    - Distributed systems
    - API design (REST, GraphQL, gRPC)
    - Database architecture
    - Security architecture
    
    Khi design architecture:
    - Consider scalability, reliability, maintainability
    - Apply SOLID principles
    - Use appropriate design patterns
    - Document architectural decisions (ADRs)
    - Consider trade-offs
    """,
    metadata={
        "agent_type": "SA",
        "patterns": ["microservices", "event-driven", "layered"]
    }
)
```text


## 4. Implementation Developer

### Mô Tả

Implementation Developer agent viết code, implement features, và develop applications.

### Chức Năng Chính

- Code implementation
- Feature development
- Bug fixing
- Code refactoring
- Unit testing
- Code documentation

### Ví Dụ

```python
impl_agent = create_agent(
    name="implementation-developer",
    role="Implementation Developer",
    model_name="gpt-4",
    system_prompt="""Bạn là Implementation Developer expert.
    
    Chuyên môn:
    - Python, JavaScript, TypeScript
    - Backend: FastAPI, Django, Node.js
    - Frontend: React, Vue, Angular
    - Databases: PostgreSQL, MongoDB, Redis
    
    Khi implement code:
    - Write clean, maintainable code
    - Follow coding standards
    - Add comprehensive tests
    - Document complex logic
    - Handle errors gracefully
    - Optimize performance
    """,
    tools=["code_execution", "file_operations", "git_operations"],
    metadata={
        "agent_type": "IMPLEMENTATION",
        "languages": ["python", "javascript", "typescript"]
    }
)
```text

## 5. Research Specialist

### Mô Tả

Research Specialist agent nghiên cứu technologies, evaluate solutions, và provide recommendations.

### Chức Năng Chính

- Technology research
- Solution evaluation
- Proof of concepts
- Benchmarking
- Documentation review
- Best practices research

### Ví Dụ

```python
research_agent = create_agent(
    name="research-specialist",
    role="Research Specialist",
    model_name="gpt-4-turbo",
    system_prompt="""Bạn là Research Specialist chuyên sâu.
    
    Nhiệm vụ:
    - Research emerging technologies
    - Evaluate frameworks và libraries
    - Compare solutions objectively
    - Create proof of concepts
    - Document findings thoroughly
    - Provide actionable recommendations
    
    Research process:
    1. Define research questions
    2. Gather information from reliable sources
    3. Analyze pros and cons
    4. Create comparison matrices
    5. Test with POCs
    6. Document recommendations
    """,
    max_iterations=50,
    metadata={
        "agent_type": "RESEARCH",
        "focus_areas": ["frameworks", "libraries", "tools", "patterns"]
    }
)
```text

## 6. Quality Judge

### Mô Tả

Quality Judge agent đánh giá code quality, perform reviews, và ensure standards compliance.

### Chức Năng Chính

- Code quality assessment
- Code reviews
- Standards compliance
- Best practices validation
- Performance evaluation
- Security assessment

### Ví Dụ

```python
quality_agent = create_agent(
    name="quality-judge",
    role="Quality Judge",
    model_name="gpt-4",
    system_prompt="""Bạn là Quality Judge với standards cao.
    
    Đánh giá criteria:
    - Code quality: readability, maintainability
    - Best practices: SOLID, DRY, KISS
    - Performance: efficiency, optimization
    - Security: vulnerabilities, best practices
    - Testing: coverage, quality
    - Documentation: completeness, clarity
    
    Review process:
    1. Analyze code structure
    2. Check standards compliance
    3. Identify issues và improvements
    4. Provide specific feedback
    5. Suggest concrete solutions
    6. Rate overall quality
    """,
    tools=["code_analysis", "security_scan"],
    metadata={
        "agent_type": "QUALITY_JUDGE",
        "standards": ["pep8", "eslint", "sonarqube"]
    }
)
```' has insufficient content
⚠️ **language_consistency**: Document in vi/ directory should contain Vietnamese content

### guides/agents/creating-agents.md

⚠️ **heading_hierarchy**: Heading hierarchy skip detected: 'Parameters Bắt Buộc' (level 3 after level 1)
⚠️ **heading_hierarchy**: Heading hierarchy skip detected: 'Metadata' (level 3 after level 1)
⚠️ **heading_hierarchy**: Heading hierarchy skip detected: 'Liệt Kê Agents' (level 3 after level 1)
⚠️ **heading_hierarchy**: Heading hierarchy skip detected: 'Cập Nhật Agent' (level 3 after level 1)
⚠️ **heading_hierarchy**: Heading hierarchy skip detected: 'Xóa Agent' (level 3 after level 1)
⚠️ **heading_hierarchy**: Heading hierarchy skip detected: 'Model Configuration với ModelConfig' (level 3 after level 1)
⚠️ **heading_hierarchy**: Heading hierarchy skip detected: '2. System Prompt Guidelines' (level 3 after level 1)
⚠️ **heading_hierarchy**: Heading hierarchy skip detected: '3. Tool Selection' (level 3 after level 1)
⚠️ **heading_hierarchy**: Heading hierarchy skip detected: '4. Metadata Organization' (level 3 after level 1)
⚠️ **heading_hierarchy**: Heading hierarchy skip detected: 'Duplicate Agent Names' (level 3 after level 1)
⚠️ **language_consistency**: Document in vi/ directory should contain Vietnamese content
ℹ️ **missing_translation**: Technical term 'Agent' appears frequently without Vietnamese explanation

### guides/agents/overview.md

⚠️ **heading_hierarchy**: Heading hierarchy skip detected: '3. System Prompts' (level 3 after level 1)
⚠️ **heading_hierarchy**: Heading hierarchy skip detected: '2. Cấu Hình' (level 3 after level 1)
⚠️ **heading_hierarchy**: Heading hierarchy skip detected: '3. Thực Thi' (level 3 after level 1)
⚠️ **heading_hierarchy**: Heading hierarchy skip detected: '4. Monitoring và Logging' (level 3 after level 1)
⚠️ **heading_hierarchy**: Heading hierarchy skip detected: '2. Chọn Model Phù Hợp' (level 3 after level 1)
⚠️ **heading_hierarchy**: Heading hierarchy skip detected: '3. Viết System Prompts Chi Tiết' (level 3 after level 1)
⚠️ **heading_hierarchy**: Heading hierarchy skip detected: 'Multi-Agent Collaboration' (level 3 after level 1)
⚠️ **heading_hierarchy**: Heading hierarchy skip detected: 'Agent Specialization' (level 3 after level 1)
⚠️ **language_consistency**: Document in vi/ directory should contain Vietnamese content
ℹ️ **missing_translation**: Technical term 'Agent' appears frequently without Vietnamese explanation

### guides/cli/commands.md

⚠️ **heading_hierarchy**: Heading hierarchy skip detected: 'Cấu Trúc Project Được Tạo' (level 3 after level 1)
⚠️ **heading_hierarchy**: Heading hierarchy skip detected: 'config set' (level 4 after level 1)
⚠️ **heading_hierarchy**: Heading hierarchy skip detected: 'config show' (level 4 after level 1)
⚠️ **heading_hierarchy**: Heading hierarchy skip detected: 'Parameter Formats' (level 3 after level 1)
⚠️ **heading_hierarchy**: Heading hierarchy skip detected: 'Exit Codes' (level 3 after level 1)
⚠️ **heading_hierarchy**: Heading hierarchy skip detected: 'agent create' (level 4 after level 1)
⚠️ **heading_hierarchy**: Heading hierarchy skip detected: 'agent status' (level 4 after level 1)
⚠️ **heading_hierarchy**: Heading hierarchy skip detected: 'agent update' (level 4 after level 1)
⚠️ **heading_hierarchy**: Heading hierarchy skip detected: 'agent delete' (level 4 after level 1)
⚠️ **heading_hierarchy**: Heading hierarchy skip detected: 'Environment Variables' (level 3 after level 1)
⚠️ **heading_hierarchy**: Heading hierarchy skip detected: 'Configuration Precedence' (level 3 after level 1)
⚠️ **heading_hierarchy**: Heading hierarchy skip detected: 'Batch Operations' (level 3 after level 1)
⚠️ **heading_hierarchy**: Heading hierarchy skip detected: 'Debugging' (level 3 after level 1)
⚠️ **language_consistency**: Document in vi/ directory should contain Vietnamese content
ℹ️ **missing_translation**: Technical term 'Agent' appears frequently without Vietnamese explanation
ℹ️ **missing_translation**: Technical term 'CLI' appears frequently without Vietnamese explanation
⚠️ **missing_language** (line 89): Code block missing language specification
⚠️ **missing_language** (line 389): Code block missing language specification
⚠️ **missing_language** (line 488): Code block missing language specification

### guides/cli/examples.md

⚠️ **heading_hierarchy**: Heading hierarchy skip detected: 'Example 2: Cấu Hình API Keys' (level 3 after level 1)
⚠️ **heading_hierarchy**: Heading hierarchy skip detected: 'Example 3: Tạo Agent Đầu Tiên' (level 3 after level 1)
⚠️ **heading_hierarchy**: Heading hierarchy skip detected: 'Example 5: Test Generation' (level 3 after level 1)
⚠️ **heading_hierarchy**: Heading hierarchy skip detected: 'Example 6: Documentation Generation' (level 3 after level 1)
⚠️ **heading_hierarchy**: Heading hierarchy skip detected: 'Example 7: Bug Fixing' (level 3 after level 1)
⚠️ **heading_hierarchy**: Heading hierarchy skip detected: 'Example 9: GitLab CI Integration' (level 3 after level 1)
⚠️ **heading_hierarchy**: Heading hierarchy skip detected: 'Example 10: Pre-commit Hooks' (level 3 after level 1)
⚠️ **heading_hierarchy**: Heading hierarchy skip detected: 'Example 12: Code Refactoring' (level 3 after level 1)
⚠️ **heading_hierarchy**: Heading hierarchy skip detected: 'Example 14: Parallel Execution' (level 3 after level 1)
⚠️ **heading_hierarchy**: Heading hierarchy skip detected: 'Example 15: Watch Mode for Development' (level 3 after level 1)
⚠️ **heading_hierarchy**: Heading hierarchy skip detected: 'Example 16: Debugging và Troubleshooting' (level 3 after level 1)
⚠️ **heading_hierarchy**: Heading hierarchy skip detected: 'Example 17: Batch Processing' (level 3 after level 1)
⚠️ **heading_hierarchy**: Heading hierarchy skip detected: 'Example 19: Jira Integration' (level 3 after level 1)
⚠️ **heading_hierarchy**: Heading hierarchy skip detected: 'Example 20: Docker Integration' (level 3 after level 1)
⚠️ **heading_hierarchy**: Heading hierarchy skip detected: 'Example 22: Daily Report Generator' (level 3 after level 1)
⚠️ **language_consistency**: Document in vi/ directory should contain Vietnamese content
ℹ️ **missing_translation**: Technical term 'CLI' appears frequently without Vietnamese explanation
ℹ️ **missing_translation**: Technical term 'API' appears frequently without Vietnamese explanation

### guides/cli/overview.md

⚠️ **heading_hierarchy**: Heading hierarchy skip detected: '2. Tích Hợp CI/CD' (level 3 after level 1)
⚠️ **heading_hierarchy**: Heading hierarchy skip detected: '3. Scripting và Automation' (level 3 after level 1)
⚠️ **heading_hierarchy**: Heading hierarchy skip detected: '4. Không Cần Viết Code' (level 3 after level 1)
⚠️ **heading_hierarchy**: Heading hierarchy skip detected: 'Xác Minh Cài Đặt' (level 3 after level 1)
⚠️ **heading_hierarchy**: Heading hierarchy skip detected: '3. run - Chạy Workflows' (level 3 after level 1)
⚠️ **heading_hierarchy**: Heading hierarchy skip detected: '4. agent - Quản Lý Agents' (level 3 after level 1)
⚠️ **heading_hierarchy**: Heading hierarchy skip detected: 'Sử Dụng Hàng Ngày' (level 3 after level 1)
⚠️ **heading_hierarchy**: Heading hierarchy skip detected: 'Environment Variables' (level 3 after level 1)
⚠️ **heading_hierarchy**: Heading hierarchy skip detected: 'Table Output' (level 3 after level 1)
⚠️ **heading_hierarchy**: Heading hierarchy skip detected: 'Verbose Output' (level 3 after level 1)
⚠️ **heading_hierarchy**: Heading hierarchy skip detected: 'Exit Codes' (level 3 after level 1)
⚠️ **heading_hierarchy**: Heading hierarchy skip detected: '2. Version Control' (level 3 after level 1)
⚠️ **heading_hierarchy**: Heading hierarchy skip detected: '3. Scripting' (level 3 after level 1)
⚠️ **heading_hierarchy**: Heading hierarchy skip detected: '4. Logging' (level 3 after level 1)
⚠️ **heading_hierarchy**: Heading hierarchy skip detected: '5. CI/CD Integration' (level 3 after level 1)
⚠️ **heading_hierarchy**: Heading hierarchy skip detected: 'Zsh Completion' (level 3 after level 1)
⚠️ **heading_hierarchy**: Heading hierarchy skip detected: 'Fish Completion' (level 3 after level 1)
⚠️ **language_consistency**: Document in vi/ directory should contain Vietnamese content
ℹ️ **missing_translation**: Technical term 'CLI' appears frequently without Vietnamese explanation
ℹ️ **missing_translation**: Technical term 'API' appears frequently without Vietnamese explanation
⚠️ **missing_language** (line 79): Code block missing language specification

### guides/intelligence/collaboration.md

⚠️ **heading_hierarchy**: Heading hierarchy skip detected: 'Tạo Collaboration Session' (level 3 after level 1)
⚠️ **heading_hierarchy**: Heading hierarchy skip detected: 'Đăng Ký Agents Vào Session' (level 3 after level 1)
⚠️ **heading_hierarchy**: Heading hierarchy skip detected: 'Gửi Messages Giữa Agents' (level 3 after level 1)
⚠️ **heading_hierarchy**: Heading hierarchy skip detected: 'Điều Phối Multi-Agent Workflow' (level 3 after level 1)
⚠️ **heading_hierarchy**: Heading hierarchy skip detected: 'Ví Dụ 2: Team-Based Feature Development' (level 3 after level 1)
⚠️ **heading_hierarchy**: Heading hierarchy skip detected: 'Ví Dụ 3: Conflict Resolution' (level 3 after level 1)
⚠️ **heading_hierarchy**: Heading hierarchy skip detected: '2. Quản Lý Session Lifecycle' (level 3 after level 1)
⚠️ **heading_hierarchy**: Heading hierarchy skip detected: '3. Handle Message Failures' (level 3 after level 1)
⚠️ **heading_hierarchy**: Heading hierarchy skip detected: '5. Use Timeouts' (level 3 after level 1)
⚠️ **heading_hierarchy**: Heading hierarchy skip detected: 'Session Conflicts' (level 3 after level 1)
⚠️ **heading_hierarchy**: Heading hierarchy skip detected: 'Memory Issues Với Large Sessions' (level 3 after level 1)
⚠️ **language_consistency**: Document in vi/ directory should contain Vietnamese content
ℹ️ **missing_translation**: Technical term 'Agent' appears frequently without Vietnamese explanation
❌ **broken_reference** (line 275): Broken reference link '"reviewer1", "reviewer2", "security"' to 'review = self._conduct_review('
❌ **broken_reference** (line 648): Broken reference link '"involved_agents"' to 'opinion = self._get_agent_opinion('

### guides/intelligence/integrated-example.md

⚠️ **heading_hierarchy**: Heading hierarchy skip detected: 'Bước 4: Advanced Features' (level 3 after level 1)
⚠️ **heading_hierarchy**: Heading hierarchy skip detected: '2. Incremental Learning' (level 3 after level 1)
⚠️ **heading_hierarchy**: Heading hierarchy skip detected: '3. Monitor Intelligence Performance' (level 3 after level 1)
⚠️ **heading_hierarchy**: Heading hierarchy skip detected: '4. Graceful Degradation' (level 3 after level 1)
⚠️ **language_consistency**: Document in vi/ directory should contain Vietnamese content
ℹ️ **missing_translation**: Technical term 'Agent' appears frequently without Vietnamese explanation
❌ **syntax_error** (line 111): Python syntax error in code block: unexpected indent
⚠️ **missing_language** (line 46): Code block missing language specification
❌ **broken_reference** (line 268): Broken reference link ''avg_duration'' to '.2f}s")'
❌ **broken_reference** (line 270): Broken reference link '"common_issues"' to 'print(f"  Common issues to avoid: {len(insights['common_issues'])}")'
❌ **broken_reference** (line 273): Broken reference link '"best_practices"' to 'print(f"  Best practices found: {len(insights['best_practices'])}")'
❌ **broken_reference** (line 352): Broken reference link '"success"' to 'print(f"  ✗ Stage failed: {result.get('error', 'Unknown error')}")'
❌ **broken_reference** (line 504): Broken reference link ''duration'' to '.2f}s")'
❌ **broken_reference** (line 543): Broken reference link '"build", "test", "deploy"' to 'stage_stats = self.monitor.get_statistics('
❌ **broken_reference** (line 657): Broken reference link ''avg_duration'' to '.2f}s "'
❌ **broken_reference** (line 669): Broken reference link '"build", "test"' to 'if stage in stage_durations and stage_durations[stage]:'

### guides/intelligence/learning.md

⚠️ **heading_hierarchy**: Heading hierarchy skip detected: 'Học Từ Thành Công' (level 3 after level 1)
⚠️ **heading_hierarchy**: Heading hierarchy skip detected: 'Học Từ Thất Bại' (level 3 after level 1)
⚠️ **heading_hierarchy**: Heading hierarchy skip detected: 'Tìm Kiếm Execution Tương Tự' (level 3 after level 1)
⚠️ **heading_hierarchy**: Heading hierarchy skip detected: 'Ví Dụ 2: Learning-Enhanced Test Generator' (level 3 after level 1)
⚠️ **heading_hierarchy**: Heading hierarchy skip detected: 'Ví Dụ 3: Adaptive Error Recovery' (level 3 after level 1)
⚠️ **heading_hierarchy**: Heading hierarchy skip detected: '2. Sử Dụng Metadata Có Ý Nghĩa' (level 3 after level 1)
⚠️ **heading_hierarchy**: Heading hierarchy skip detected: '3. Học Từ Cả Thành Công Và Thất Bại' (level 3 after level 1)
⚠️ **heading_hierarchy**: Heading hierarchy skip detected: '4. Định Kỳ Dọn Dẹp Knowledge Base' (level 3 after level 1)
⚠️ **heading_hierarchy**: Heading hierarchy skip detected: '5. Sử Dụng Similarity Threshold Phù Hợp' (level 3 after level 1)
⚠️ **heading_hierarchy**: Heading hierarchy skip detected: 'Knowledge Base Quá Lớn' (level 3 after level 1)
⚠️ **heading_hierarchy**: Heading hierarchy skip detected: 'Learning Chậm' (level 3 after level 1)
⚠️ **language_consistency**: Document in vi/ directory should contain Vietnamese content

### guides/intelligence/monitoring.md

⚠️ **heading_hierarchy**: Heading hierarchy skip detected: 'Ghi Lại Metrics' (level 3 after level 1)
⚠️ **heading_hierarchy**: Heading hierarchy skip detected: 'Ghi Custom Metrics' (level 4 after level 1)
⚠️ **heading_hierarchy**: Heading hierarchy skip detected: 'Kiểm Tra Health Status' (level 3 after level 1)
⚠️ **heading_hierarchy**: Heading hierarchy skip detected: 'Kiểm Tra Workflow Health' (level 4 after level 1)
⚠️ **heading_hierarchy**: Heading hierarchy skip detected: 'Kiểm Tra System Health' (level 4 after level 1)
⚠️ **heading_hierarchy**: Heading hierarchy skip detected: 'Thu Thập Statistics' (level 3 after level 1)
⚠️ **heading_hierarchy**: Heading hierarchy skip detected: 'Ví Dụ 2: Performance Dashboard' (level 3 after level 1)
⚠️ **heading_hierarchy**: Heading hierarchy skip detected: 'Ví Dụ 3: Alerting System' (level 3 after level 1)
⚠️ **heading_hierarchy**: Heading hierarchy skip detected: '2. Sử Dụng Tags Nhất Quán' (level 3 after level 1)
⚠️ **heading_hierarchy**: Heading hierarchy skip detected: '3. Thiết Lập Health Checks Định Kỳ' (level 3 after level 1)
⚠️ **heading_hierarchy**: Heading hierarchy skip detected: '4. Aggregate Metrics Để Tiết Kiệm Storage' (level 3 after level 1)
⚠️ **heading_hierarchy**: Heading hierarchy skip detected: '5. Monitor Cả Success và Failure' (level 3 after level 1)
⚠️ **heading_hierarchy**: Heading hierarchy skip detected: 'Performance Chậm Khi Query Metrics' (level 3 after level 1)
⚠️ **language_consistency**: Document in vi/ directory should contain Vietnamese content
ℹ️ **missing_translation**: Technical term 'Agent' appears frequently without Vietnamese explanation
ℹ️ **missing_translation**: Technical term 'Workflow' appears frequently without Vietnamese explanation
❌ **broken_reference** (line 514): Broken reference link ''issues'' to 'print("\nIssues:")'
❌ **broken_reference** (line 516): Broken reference link ''issues'' to 'print(f"  ⚠ {issue}")'
❌ **broken_reference** (line 549): Broken reference link '"error_rate"' to 'alerts.append({'
❌ **broken_reference** (line 560): Broken reference link '"response_time_p95"' to 'alerts.append({'
❌ **broken_reference** (line 571): Broken reference link '"success_rate"' to 'alerts.append({'

### guides/intelligence/reasoning.md

⚠️ **heading_hierarchy**: Heading hierarchy skip detected: 'Phân Tích Task Complexity' (level 3 after level 1)
⚠️ **heading_hierarchy**: Heading hierarchy skip detected: 'Đề Xuất Execution Mode' (level 3 after level 1)
⚠️ **heading_hierarchy**: Heading hierarchy skip detected: 'Routing Tasks Đến Agents' (level 3 after level 1)
⚠️ **heading_hierarchy**: Heading hierarchy skip detected: 'Ví Dụ 2: Adaptive Workflow Optimizer' (level 3 after level 1)
⚠️ **heading_hierarchy**: Heading hierarchy skip detected: 'Ví Dụ 3: Smart Resource Allocator' (level 3 after level 1)
⚠️ **heading_hierarchy**: Heading hierarchy skip detected: '2. Sử Dụng Learning Data' (level 3 after level 1)
⚠️ **heading_hierarchy**: Heading hierarchy skip detected: '3. Validate Routing Decisions' (level 3 after level 1)
⚠️ **heading_hierarchy**: Heading hierarchy skip detected: '4. Monitor Reasoning Performance' (level 3 after level 1)
⚠️ **heading_hierarchy**: Heading hierarchy skip detected: '5. Combine Multiple Reasoning Strategies' (level 3 after level 1)
⚠️ **heading_hierarchy**: Heading hierarchy skip detected: 'Low Confidence Scores' (level 3 after level 1)
⚠️ **heading_hierarchy**: Heading hierarchy skip detected: 'Reasoning Chậm' (level 3 after level 1)
⚠️ **language_consistency**: Document in vi/ directory should contain Vietnamese content
ℹ️ **missing_translation**: Technical term 'Agent' appears frequently without Vietnamese explanation
❌ **broken_reference** (line 287): Broken reference link '"high", "very_high"' to 'print(f"\n3. Execution Strategy:")'
❌ **broken_reference** (line 313): Broken reference link 'Dict' to '"""Break down complex task thành subtasks."""'

### guides/plugins/best-practices.md

⚠️ **language_consistency**: Document in vi/ directory should contain Vietnamese content
ℹ️ **missing_translation**: Technical term 'Plugin' appears frequently without Vietnamese explanation
ℹ️ **missing_translation**: Technical term 'API' appears frequently without Vietnamese explanation
❌ **broken_reference** (line 40): Broken reference link 'str, Any' to '"""Process data with validation."""'
❌ **broken_reference** (line 72): Broken reference link 'str, Any' to '"""Process batch with partial failure handling."""'
❌ **broken_reference** (line 145): Broken reference link 'str, Any' to '"""Fetch data with retry."""'
❌ **broken_reference** (line 718): Broken reference link 'Dict' to '"""Fetch multiple URLs concurrently."""'
❌ **broken_reference** (line 764): Broken reference link 'str, Any' to '"""Process data and return results.'

### guides/plugins/creating-plugins.md

⚠️ **heading_hierarchy**: Heading hierarchy skip detected: 'Use Plugin in Agent' (level 3 after level 1)
⚠️ **heading_hierarchy**: Heading hierarchy skip detected: 'Use Plugin in Workflow' (level 3 after level 1)
⚠️ **language_consistency**: Document in vi/ directory should contain Vietnamese content
ℹ️ **missing_translation**: Technical term 'Agent' appears frequently without Vietnamese explanation
ℹ️ **missing_translation**: Technical term 'Plugin' appears frequently without Vietnamese explanation
ℹ️ **missing_translation**: Technical term 'API' appears frequently without Vietnamese explanation
❌ **broken_reference** (line 225): Broken reference link 'str, Any' to '"""Get current weather for a city.'
❌ **broken_reference** (line 384): Broken reference link 'str, Any' to '"""Get current weather for a city.'
❌ **broken_reference** (line 571): Broken reference link 'str' to '"""List of required plugin names."""'
❌ **broken_reference** (line 615): Broken reference link '"cache"' to 'return self.state["cache"][task]'
❌ **broken_reference** (line 623): Broken reference link 'str, Any' to '"""Get plugin statistics."""'
❌ **broken_reference** (line 646): Broken reference link 'str, Any' to '"""Async data fetching."""'

### guides/plugins/overview.md

⚠️ **heading_hierarchy**: Heading hierarchy skip detected: '2. Plugin Lifecycle' (level 3 after level 1)
⚠️ **heading_hierarchy**: Heading hierarchy skip detected: '3. Configuration Management' (level 3 after level 1)
⚠️ **heading_hierarchy**: Heading hierarchy skip detected: 'Manual Registration' (level 3 after level 1)
⚠️ **heading_hierarchy**: Heading hierarchy skip detected: '2. Version Plugins Properly' (level 3 after level 1)
⚠️ **language_consistency**: Document in vi/ directory should contain Vietnamese content
ℹ️ **missing_translation**: Technical term 'Plugin' appears frequently without Vietnamese explanation
❌ **broken_reference** (line 146): Broken reference link 'str' to '"""List of required plugins."""'
❌ **broken_reference** (line 176): Broken reference link 'Tool' to '"""Return list of tools."""'

### guides/plugins/plugin-examples.md

⚠️ **language_consistency**: Document in vi/ directory should contain Vietnamese content
ℹ️ **missing_translation**: Technical term 'Plugin' appears frequently without Vietnamese explanation
ℹ️ **missing_translation**: Technical term 'API' appears frequently without Vietnamese explanation
❌ **broken_reference** (line 300): Broken reference link 'str, Any' to '"""Send message to Slack channel.'
❌ **broken_reference** (line 334): Broken reference link 'str, Any' to '"""Send formatted notification.'
❌ **broken_reference** (line 373): Broken reference link 'str, Any' to '"""Send workflow status update.'
❌ **broken_reference** (line 417): Broken reference link 'str, Any' to '"""Upload file to Slack.'
❌ **broken_reference** (line 575): Broken reference link 'str, Any' to '"""Create GitHub issue.'
❌ **broken_reference** (line 655): Broken reference link 'str, Any' to '"""Create pull request.'
❌ **broken_reference** (line 845): Broken reference link 'Any' to '"""Get value from cache.'

### guides/workflows/advanced-workflows.md

⚠️ **heading_hierarchy**: Heading hierarchy skip detected: 'Custom Error Recovery' (level 3 after level 1)
⚠️ **heading_hierarchy**: Heading hierarchy skip detected: 'Event-Driven Workflow' (level 3 after level 1)
⚠️ **heading_hierarchy**: Heading hierarchy skip detected: 'State Machine Workflow' (level 3 after level 1)
⚠️ **language_consistency**: Document in vi/ directory should contain Vietnamese content
ℹ️ **missing_translation**: Technical term 'Workflow' appears frequently without Vietnamese explanation

### guides/workflows/building-workflows.md

⚠️ **heading_hierarchy**: Heading hierarchy skip detected: 'Ví Dụ 2: Testing Pipeline' (level 3 after level 1)
⚠️ **heading_hierarchy**: Heading hierarchy skip detected: 'Ví Dụ 2: Parallel Code Analysis' (level 3 after level 1)
⚠️ **heading_hierarchy**: Heading hierarchy skip detected: 'Sử dụng Step Output' (level 3 after level 1)
⚠️ **heading_hierarchy**: Heading hierarchy skip detected: '2. Dependency Management' (level 3 after level 1)
⚠️ **heading_hierarchy**: Heading hierarchy skip detected: '3. Error Handling' (level 3 after level 1)
⚠️ **heading_hierarchy**: Heading hierarchy skip detected: '4. Resource Management' (level 3 after level 1)
⚠️ **language_consistency**: Document in vi/ directory should contain Vietnamese content
ℹ️ **missing_translation**: Technical term 'Workflow' appears frequently without Vietnamese explanation
❌ **syntax_error** (line 505): Python syntax error in code block: positional argument follows keyword argument

### guides/workflows/overview.md

⚠️ **language_consistency**: Document in vi/ directory should contain Vietnamese content
ℹ️ **missing_translation**: Technical term 'Workflow' appears frequently without Vietnamese explanation
⚠️ **missing_language** (line 73): Code block missing language specification
⚠️ **missing_language** (line 83): Code block missing language specification
⚠️ **missing_language** (line 96): Code block missing language specification
⚠️ **missing_language** (line 107): Code block missing language specification

### guides/workflows/workflow-patterns.md

⚠️ **language_consistency**: Document in vi/ directory should contain Vietnamese content
ℹ️ **missing_translation**: Technical term 'API' appears frequently without Vietnamese explanation
⚠️ **missing_language** (line 27): Code block missing language specification
⚠️ **missing_language** (line 88): Code block missing language specification
⚠️ **missing_language** (line 156): Code block missing language specification
⚠️ **missing_language** (line 230): Code block missing language specification
⚠️ **missing_language** (line 296): Code block missing language specification
⚠️ **missing_language** (line 356): Code block missing language specification
⚠️ **missing_language** (line 410): Code block missing language specification
⚠️ **missing_language** (line 473): Code block missing language specification
⚠️ **missing_language** (line 532): Code block missing language specification

### migration/from-v2.md

⚠️ **heading_hierarchy**: Heading hierarchy skip detected: '2. Enhanced Workflow Engine' (level 3 after level 1)
⚠️ **heading_hierarchy**: Heading hierarchy skip detected: '3. Multi-Model Support' (level 3 after level 1)
⚠️ **heading_hierarchy**: Heading hierarchy skip detected: '4. Enhanced CLI' (level 3 after level 1)
⚠️ **heading_hierarchy**: Heading hierarchy skip detected: '5. Plugin Lifecycle Management' (level 3 after level 1)
⚠️ **language_consistency**: Document in vi/ directory should contain Vietnamese content
ℹ️ **missing_translation**: Technical term 'Agent' appears frequently without Vietnamese explanation
ℹ️ **missing_translation**: Technical term 'Workflow' appears frequently without Vietnamese explanation
ℹ️ **missing_translation**: Technical term 'Plugin' appears frequently without Vietnamese explanation
ℹ️ **missing_translation**: Technical term 'API' appears frequently without Vietnamese explanation

### migration/upgrade-guide.md

⚠️ **heading_hierarchy**: Heading hierarchy skip detected: '1.2 Kiểm Tra Phiên Bản Hiện Tại' (level 3 after level 1)
⚠️ **heading_hierarchy**: Heading hierarchy skip detected: '2.2 Update Requirements File' (level 3 after level 1)
⚠️ **heading_hierarchy**: Heading hierarchy skip detected: '9.2 Downgrade Package' (level 3 after level 1)
⚠️ **language_consistency**: Document in vi/ directory should contain Vietnamese content
ℹ️ **missing_translation**: Technical term 'Agent' appears frequently without Vietnamese explanation
ℹ️ **missing_translation**: Technical term 'Workflow' appears frequently without Vietnamese explanation
ℹ️ **missing_translation**: Technical term 'Plugin' appears frequently without Vietnamese explanation
ℹ️ **missing_translation**: Technical term 'API' appears frequently without Vietnamese explanation
❌ **syntax_error** (line 660): Python syntax error in code block: invalid syntax
⚠️ **missing_language** (line 656): Code block missing language specification
⚠️ **missing_language** (line 669): Code block missing language specification
⚠️ **missing_language** (line 679): Code block missing language specification
⚠️ **missing_language** (line 693): Code block missing language specification

### troubleshooting/common-errors.md

⚠️ **heading_hierarchy**: Heading hierarchy skip detected: 'Fallback Mechanism' (level 3 after level 1)
⚠️ **heading_hierarchy**: Heading hierarchy skip detected: 'Graceful Degradation' (level 3 after level 1)
⚠️ **heading_hierarchy**: Heading hierarchy skip detected: 'Fallback Mechanism' (level 3 after level 1)
⚠️ **heading_hierarchy**: Heading hierarchy skip detected: 'Graceful Degradation' (level 3 after level 1)
⚠️ **heading_hierarchy**: Heading hierarchy skip detected: 'Graceful Degradation' (level 3 after level 1)
⚠️ **heading_hierarchy**: Heading hierarchy skip detected: 'Graceful Degradation' (level 3 after level 1)
⚠️ **heading_hierarchy**: Heading hierarchy skip detected: 'Fallback Mechanism' (level 3 after level 1)
⚠️ **heading_hierarchy**: Heading hierarchy skip detected: 'Graceful Degradation' (level 3 after level 1)
⚠️ **language_consistency**: Document in vi/ directory should contain Vietnamese content
ℹ️ **missing_translation**: Technical term 'Agent' appears frequently without Vietnamese explanation
ℹ️ **missing_translation**: Technical term 'Workflow' appears frequently without Vietnamese explanation
ℹ️ **missing_translation**: Technical term 'Plugin' appears frequently without Vietnamese explanation
ℹ️ **missing_translation**: Technical term 'API' appears frequently without Vietnamese explanation
⚠️ **missing_language** (line 19): Code block missing language specification
⚠️ **missing_language** (line 66): Code block missing language specification
⚠️ **missing_language** (line 108): Code block missing language specification
⚠️ **missing_language** (line 178): Code block missing language specification
⚠️ **missing_language** (line 238): Code block missing language specification
⚠️ **missing_language** (line 319): Code block missing language specification
⚠️ **missing_language** (line 395): Code block missing language specification
⚠️ **missing_language** (line 456): Code block missing language specification
⚠️ **missing_language** (line 517): Code block missing language specification
⚠️ **missing_language** (line 581): Code block missing language specification
⚠️ **missing_language** (line 649): Code block missing language specification
⚠️ **missing_language** (line 692): Code block missing language specification

### troubleshooting/debugging.md

⚠️ **heading_hierarchy**: Heading hierarchy skip detected: '2. Logging Levels' (level 3 after level 1)
⚠️ **heading_hierarchy**: Heading hierarchy skip detected: '2. Inspect Workflow State' (level 3 after level 1)
⚠️ **heading_hierarchy**: Heading hierarchy skip detected: '3. Monitor API Calls' (level 3 after level 1)
⚠️ **heading_hierarchy**: Heading hierarchy skip detected: '4. Debug Plugin Issues' (level 3 after level 1)
⚠️ **heading_hierarchy**: Heading hierarchy skip detected: '5. Memory Profiling' (level 3 after level 1)
⚠️ **heading_hierarchy**: Heading hierarchy skip detected: '6. Performance Profiling' (level 3 after level 1)
⚠️ **heading_hierarchy**: Heading hierarchy skip detected: 'Scenario 2: Workflow Steps Failing' (level 3 after level 1)
⚠️ **heading_hierarchy**: Heading hierarchy skip detected: 'Scenario 3: Memory Leaks' (level 3 after level 1)
⚠️ **heading_hierarchy**: Heading hierarchy skip detected: 'Scenario 4: API Rate Limiting' (level 3 after level 1)
⚠️ **heading_hierarchy**: Heading hierarchy skip detected: '2. Log Aggregation' (level 3 after level 1)
⚠️ **heading_hierarchy**: Heading hierarchy skip detected: '3. Distributed Tracing' (level 3 after level 1)
⚠️ **heading_hierarchy**: Heading hierarchy skip detected: '2. Context Managers cho Debugging' (level 3 after level 1)
⚠️ **heading_hierarchy**: Heading hierarchy skip detected: '3. Conditional Debugging' (level 3 after level 1)
⚠️ **language_consistency**: Document in vi/ directory should contain Vietnamese content
ℹ️ **missing_translation**: Technical term 'Agent' appears frequently without Vietnamese explanation
ℹ️ **missing_translation**: Technical term 'Workflow' appears frequently without Vietnamese explanation
ℹ️ **missing_translation**: Technical term 'Plugin' appears frequently without Vietnamese explanation
ℹ️ **missing_translation**: Technical term 'API' appears frequently without Vietnamese explanation
⚠️ **missing_language** (line 97): Code block missing language specification
⚠️ **missing_language** (line 116): Code block missing language specification
⚠️ **missing_language** (line 140): Code block missing language specification
⚠️ **missing_language** (line 155): Code block missing language specification
⚠️ **missing_language** (line 200): Code block missing language specification
❌ **broken_reference** (line 315): Broken reference link ':10' to 'print(stat)'

### troubleshooting/faq.md

⚠️ **heading_hierarchy**: Heading hierarchy skip detected: 'Q2: Python version nào được support?' (level 3 after level 1)
⚠️ **heading_hierarchy**: Heading hierarchy skip detected: 'Q3: Làm thế nào để verify installation thành công?' (level 3 after level 1)
⚠️ **heading_hierarchy**: Heading hierarchy skip detected: 'Q4: Có cần API key không?' (level 3 after level 1)
⚠️ **heading_hierarchy**: Heading hierarchy skip detected: 'Q6: Làm thế nào để switch giữa các LLM providers?' (level 3 after level 1)
⚠️ **heading_hierarchy**: Heading hierarchy skip detected: 'Q7: Có thể sử dụng local LLM không?' (level 3 after level 1)
⚠️ **heading_hierarchy**: Heading hierarchy skip detected: 'Q8: Làm thế nào để configure logging?' (level 3 after level 1)
⚠️ **heading_hierarchy**: Heading hierarchy skip detected: 'Q12: Làm thế nào để limit agent execution time?' (level 3 after level 1)
⚠️ **heading_hierarchy**: Heading hierarchy skip detected: 'Q14: Có thể run workflow steps parallel không?' (level 3 after level 1)
⚠️ **heading_hierarchy**: Heading hierarchy skip detected: 'Q15: Làm thế nào để handle workflow errors?' (level 3 after level 1)
⚠️ **heading_hierarchy**: Heading hierarchy skip detected: 'Q16: Có thể save và resume workflow không?' (level 3 after level 1)
⚠️ **heading_hierarchy**: Heading hierarchy skip detected: 'Q19: Có thể monitor agent performance không?' (level 3 after level 1)
⚠️ **heading_hierarchy**: Heading hierarchy skip detected: 'Q20: Reasoner giúp gì?' (level 3 after level 1)
⚠️ **heading_hierarchy**: Heading hierarchy skip detected: 'Q23: Plugin có thể có dependencies không?' (level 3 after level 1)
⚠️ **heading_hierarchy**: Heading hierarchy skip detected: 'Q26: Làm thế nào để reduce API costs?' (level 3 after level 1)
⚠️ **heading_hierarchy**: Heading hierarchy skip detected: 'Q28: Workflow bị stuck, làm sao?' (level 3 after level 1)
⚠️ **heading_hierarchy**: Heading hierarchy skip detected: 'Q29: Memory usage cao, làm gì?' (level 3 after level 1)
⚠️ **heading_hierarchy**: Heading hierarchy skip detected: 'Q30: Làm thế nào để report bugs?' (level 3 after level 1)
⚠️ **language_consistency**: Document in vi/ directory should contain Vietnamese content
ℹ️ **missing_translation**: Technical term 'Agent' appears frequently without Vietnamese explanation
ℹ️ **missing_translation**: Technical term 'Workflow' appears frequently without Vietnamese explanation
ℹ️ **missing_translation**: Technical term 'Plugin' appears frequently without Vietnamese explanation
ℹ️ **missing_translation**: Technical term 'API' appears frequently without Vietnamese explanation
❌ **broken_reference** (line 506): Broken reference link 'str' to 'return ["requests", "pandas", "numpy"]'
❌ **broken_reference** (line 645): Broken reference link ':10' to 'print(stat)'

### use-cases/README.md

❌ **missing_section**: Use case missing required section: Tổng Quan
❌ **missing_section**: Use case missing required section: Kịch Bản
❌ **missing_section**: Use case missing required section: Triển Khai
⚠️ **language_consistency**: Document in vi/ directory should contain Vietnamese content
ℹ️ **missing_translation**: Technical term 'Workflow' appears frequently without Vietnamese explanation

### use-cases/automated-code-review.md

⚠️ **heading_hierarchy**: Heading hierarchy skip detected: 'Bước 2: Xây dựng workflow' (level 3 after level 1)
⚠️ **heading_hierarchy**: Heading hierarchy skip detected: 'Bước 3: Tích hợp với GitHub' (level 3 after level 1)
⚠️ **heading_hierarchy**: Heading hierarchy skip detected: 'Bước 5: Xử lý kết quả và reporting' (level 3 after level 1)
⚠️ **language_consistency**: Document in vi/ directory should contain Vietnamese content
ℹ️ **missing_translation**: Technical term 'Agent' appears frequently without Vietnamese explanation
❌ **broken_reference** (line 258): Broken reference link ''opened', 'synchronize'' to 'return {'status': 'ignored'}, 200'
❌ **broken_reference** (line 372): Broken reference link ''issues'' to 'section += "**Issues Found:**\n"'
❌ **broken_reference** (line 374): Broken reference link ''issues'' to 'severity_emoji = {'
❌ **broken_reference** (line 386): Broken reference link ''suggestions'' to 'section += "\n**Suggestions:**\n"'
❌ **broken_reference** (line 388): Broken reference link ''suggestions'' to 'section += f"- 💡 {suggestion}\n"'

### use-cases/automated-testing.md

⚠️ **language_consistency**: Document in vi/ directory should contain Vietnamese content
ℹ️ **missing_translation**: Technical term 'Agent' appears frequently without Vietnamese explanation
❌ **syntax_error** (line 141): Python syntax error in code block: unterminated triple-quoted string literal (detected at line 32)
❌ **syntax_error** (line 147): Python syntax error in code block: unexpected indent
❌ **syntax_error** (line 184): Python syntax error in code block: unexpected indent
❌ **syntax_error** (line 355): Python syntax error in code block: unterminated triple-quoted string literal (detected at line 46)
❌ **syntax_error** (line 365): Python syntax error in code block: unexpected indent
⚠️ **missing_language** (line 226): Code block missing language specification
⚠️ **missing_language** (line 421): Code block missing language specification
❌ **broken_reference** (line 309): Broken reference link ''execution_time'' to '.2f}s - {r['timestamp']}")'
❌ **broken_reference** (line 417): Broken reference link '"file"' to 'related.append(change)'

### use-cases/ci-cd-automation.md

⚠️ **heading_hierarchy**: Heading hierarchy skip detected: 'Bước 2: Tạo Intelligent CI/CD Workflow' (level 3 after level 1)
⚠️ **heading_hierarchy**: Heading hierarchy skip detected: 'Bước 3: Implement Build Optimization Logic' (level 3 after level 1)
⚠️ **language_consistency**: Document in vi/ directory should contain Vietnamese content
ℹ️ **missing_translation**: Technical term 'Agent' appears frequently without Vietnamese explanation

### use-cases/custom-workflow.md

⚠️ **heading_hierarchy**: Heading hierarchy skip detected: 'Bước 2: Implement Quality Gates' (level 3 after level 1)
⚠️ **heading_hierarchy**: Heading hierarchy skip detected: 'Bước 3: Implement Traceability' (level 3 after level 1)
⚠️ **language_consistency**: Document in vi/ directory should contain Vietnamese content
ℹ️ **missing_translation**: Technical term 'Agent' appears frequently without Vietnamese explanation
ℹ️ **missing_translation**: Technical term 'Workflow' appears frequently without Vietnamese explanation
❌ **broken_reference** (line 438): Broken reference link '"code_files"' to 'data["tests"].extend(test_files)'

### use-cases/distributed-system.md

⚠️ **heading_hierarchy**: Heading hierarchy skip detected: 'Bước 2: Implement Distributed Task Queue' (level 3 after level 1)
⚠️ **language_consistency**: Document in vi/ directory should contain Vietnamese content
ℹ️ **missing_translation**: Technical term 'Agent' appears frequently without Vietnamese explanation

### use-cases/github-integration.md

⚠️ **heading_hierarchy**: Heading hierarchy skip detected: 'Bước 2: Implement Issue Triage' (level 3 after level 1)
⚠️ **language_consistency**: Document in vi/ directory should contain Vietnamese content
ℹ️ **missing_translation**: Technical term 'Agent' appears frequently without Vietnamese explanation
ℹ️ **missing_translation**: Technical term 'API' appears frequently without Vietnamese explanation
❌ **syntax_error** (line 181): Python syntax error in code block: unterminated triple-quoted string literal (detected at line 18)
⚠️ **missing_language** (line 217): Code block missing language specification
❌ **broken_reference** (line 296): Broken reference link ''opened', 'synchronize'' to 'result = review_pull_request('

### use-cases/intelligent-project-mgmt.md

⚠️ **language_consistency**: Document in vi/ directory should contain Vietnamese content
ℹ️ **missing_translation**: Technical term 'Agent' appears frequently without Vietnamese explanation

### use-cases/slack-integration.md

⚠️ **heading_hierarchy**: Heading hierarchy skip detected: 'Bước 2: Implement Message Handling' (level 3 after level 1)
⚠️ **language_consistency**: Document in vi/ directory should contain Vietnamese content
ℹ️ **missing_translation**: Technical term 'Agent' appears frequently without Vietnamese explanation

### validation_report.md

⚠️ **heading_hierarchy**: Heading hierarchy skip detected: 'api-reference/core/exceptions.md' (level 3 after level 1)
⚠️ **heading_hierarchy**: Heading hierarchy skip detected: 'api-reference/core/logging.md' (level 3 after level 1)
⚠️ **heading_hierarchy**: Heading hierarchy skip detected: 'api-reference/infrastructure/execution_engine.md' (level 3 after level 1)
⚠️ **heading_hierarchy**: Heading hierarchy skip detected: 'api-reference/infrastructure/lifecycle.md' (level 3 after level 1)
⚠️ **heading_hierarchy**: Heading hierarchy skip detected: 'api-reference/intelligence/collaborator.md' (level 3 after level 1)
⚠️ **heading_hierarchy**: Heading hierarchy skip detected: 'api-reference/intelligence/learner.md' (level 3 after level 1)
⚠️ **heading_hierarchy**: Heading hierarchy skip detected: 'api-reference/intelligence/monitor.md' (level 3 after level 1)
⚠️ **heading_hierarchy**: Heading hierarchy skip detected: 'api-reference/intelligence/reasoner.md' (level 3 after level 1)
⚠️ **heading_hierarchy**: Heading hierarchy skip detected: 'api-reference/orchestration/agent.md' (level 3 after level 1)
⚠️ **heading_hierarchy**: Heading hierarchy skip detected: 'api-reference/orchestration/client.md' (level 3 after level 1)
⚠️ **heading_hierarchy**: Heading hierarchy skip detected: 'api-reference/orchestration/workflow.md' (level 3 after level 1)
⚠️ **heading_hierarchy**: Heading hierarchy skip detected: 'api-reference/plugins/base.md' (level 3 after level 1)
⚠️ **heading_hierarchy**: Heading hierarchy skip detected: 'api-reference/plugins/registry.md' (level 3 after level 1)
⚠️ **heading_hierarchy**: Heading hierarchy skip detected: 'diagrams/agent-interaction.md' (level 3 after level 1)
⚠️ **language_consistency**: Document in vi/ directory should contain Vietnamese content
ℹ️ **missing_translation**: Technical term 'Agent' appears frequently without Vietnamese explanation
ℹ️ **missing_translation**: Technical term 'Workflow' appears frequently without Vietnamese explanation
ℹ️ **missing_translation**: Technical term 'Plugin' appears frequently without Vietnamese explanation
ℹ️ **missing_translation**: Technical term 'CLI' appears frequently without Vietnamese explanation
ℹ️ **missing_translation**: Technical term 'API' appears frequently without Vietnamese explanation
ℹ️ **missing_translation**: Technical term 'SDK' appears frequently without Vietnamese explanation
❌ **syntax_error** (line 95): Python syntax error in code block: invalid syntax
❌ **syntax_error** (line 128): Python syntax error in code block: invalid syntax
❌ **syntax_error** (line 156): Python syntax error in code block: invalid syntax
❌ **syntax_error** (line 188): Python syntax error in code block: invalid syntax
❌ **syntax_error** (line 220): Python syntax error in code block: invalid syntax
❌ **syntax_error** (line 239): Python syntax error in code block: invalid syntax
❌ **syntax_error** (line 278): Python syntax error in code block: invalid syntax
❌ **syntax_error** (line 315): Python syntax error in code block: invalid syntax
❌ **syntax_error** (line 406): Python syntax error in code block: invalid syntax
❌ **syntax_error** (line 433): Python syntax error in code block: invalid syntax
❌ **syntax_error** (line 478): Python syntax error in code block: invalid syntax
❌ **syntax_error** (line 505): Python syntax error in code block: invalid syntax
❌ **syntax_error** (line 548): Python syntax error in code block: invalid syntax
❌ **syntax_error** (line 575): Python syntax error in code block: invalid syntax
❌ **syntax_error** (line 618): Python syntax error in code block: invalid syntax
❌ **syntax_error** (line 645): Python syntax error in code block: invalid syntax
❌ **syntax_error** (line 688): Python syntax error in code block: invalid syntax
❌ **syntax_error** (line 715): Python syntax error in code block: invalid syntax
❌ **syntax_error** (line 758): Python syntax error in code block: invalid syntax
❌ **syntax_error** (line 785): Python syntax error in code block: invalid syntax
❌ **syntax_error** (line 828): Python syntax error in code block: invalid syntax
❌ **syntax_error** (line 855): Python syntax error in code block: invalid syntax
❌ **syntax_error** (line 935): Python syntax error in code block: invalid syntax
❌ **syntax_error** (line 980): Python syntax error in code block: invalid syntax
❌ **syntax_error** (line 1063): Python syntax error in code block: invalid syntax
❌ **syntax_error** (line 1081): Python syntax error in code block: invalid syntax
❌ **syntax_error** (line 1104): Python syntax error in code block: invalid syntax
❌ **syntax_error** (line 1123): Python syntax error in code block: invalid syntax
❌ **syntax_error** (line 1156): Python syntax error in code block: invalid syntax
❌ **syntax_error** (line 1204): Python syntax error in code block: invalid syntax
❌ **syntax_error** (line 1271): Python syntax error in code block: invalid syntax
❌ **syntax_error** (line 1289): Python syntax error in code block: invalid syntax
❌ **syntax_error** (line 1374): Python syntax error in code block: invalid syntax
❌ **syntax_error** (line 1392): Python syntax error in code block: invalid syntax
❌ **syntax_error** (line 1411): Python syntax error in code block: invalid syntax
❌ **syntax_error** (line 1430): Python syntax error in code block: invalid syntax
❌ **syntax_error** (line 1449): Python syntax error in code block: invalid syntax
❌ **syntax_error** (line 1474): Python syntax error in code block: invalid syntax
❌ **syntax_error** (line 1595): Python syntax error in code block: invalid syntax
❌ **syntax_error** (line 1660): Python syntax error in code block: invalid syntax
❌ **syntax_error** (line 1724): Python syntax error in code block: invalid syntax
❌ **syntax_error** (line 1749): Python syntax error in code block: invalid syntax
❌ **syntax_error** (line 1768): Python syntax error in code block: invalid syntax
❌ **syntax_error** (line 1787): Python syntax error in code block: invalid syntax
❌ **syntax_error** (line 1813): Python syntax error in code block: invalid syntax
❌ **syntax_error** (line 1836): Python syntax error in code block: invalid syntax
❌ **syntax_error** (line 1866): Python syntax error in code block: invalid syntax
❌ **syntax_error** (line 1981): Python syntax error in code block: invalid syntax
❌ **syntax_error** (line 2009): Python syntax error in code block: invalid syntax
❌ **syntax_error** (line 2035): Python syntax error in code block: invalid syntax
❌ **syntax_error** (line 2054): Python syntax error in code block: invalid syntax
❌ **syntax_error** (line 2073): Python syntax error in code block: invalid syntax
❌ **syntax_error** (line 2092): Python syntax error in code block: invalid syntax
❌ **syntax_error** (line 2118): Python syntax error in code block: invalid syntax
❌ **syntax_error** (line 2152): Python syntax error in code block: invalid syntax
❌ **syntax_error** (line 2256): Python syntax error in code block: invalid syntax
❌ **syntax_error** (line 2281): Python syntax error in code block: invalid syntax
❌ **syntax_error** (line 2309): Python syntax error in code block: invalid syntax
❌ **syntax_error** (line 2335): Python syntax error in code block: invalid syntax
❌ **syntax_error** (line 2354): Python syntax error in code block: invalid syntax
❌ **syntax_error** (line 2382): Python syntax error in code block: invalid syntax
❌ **syntax_error** (line 2412): Python syntax error in code block: invalid syntax
❌ **syntax_error** (line 2438): Python syntax error in code block: invalid syntax
❌ **syntax_error** (line 2464): Python syntax error in code block: invalid syntax
❌ **syntax_error** (line 2490): Python syntax error in code block: invalid syntax
❌ **syntax_error** (line 2520): Python syntax error in code block: invalid syntax
❌ **syntax_error** (line 2568): Python syntax error in code block: invalid syntax
❌ **syntax_error** (line 2609): Python syntax error in code block: invalid syntax
❌ **syntax_error** (line 2647): Python syntax error in code block: invalid syntax
❌ **syntax_error** (line 2670): Python syntax error in code block: invalid syntax
❌ **syntax_error** (line 2718): Python syntax error in code block: invalid syntax
❌ **syntax_error** (line 2760): Python syntax error in code block: invalid syntax
❌ **syntax_error** (line 2894): Python syntax error in code block: invalid syntax
❌ **syntax_error** (line 2957): Python syntax error in code block: invalid syntax
❌ **syntax_error** (line 2982): Python syntax error in code block: invalid syntax
❌ **syntax_error** (line 3005): Python syntax error in code block: invalid syntax
❌ **syntax_error** (line 3021): Python syntax error in code block: invalid syntax
❌ **syntax_error** (line 3046): Python syntax error in code block: invalid syntax
❌ **syntax_error** (line 3065): Python syntax error in code block: invalid syntax
❌ **syntax_error** (line 3091): Python syntax error in code block: invalid syntax
❌ **syntax_error** (line 3157): Python syntax error in code block: invalid syntax
❌ **syntax_error** (line 3176): Python syntax error in code block: invalid syntax
❌ **syntax_error** (line 3195): Python syntax error in code block: invalid syntax
❌ **syntax_error** (line 3214): Python syntax error in code block: invalid syntax
❌ **syntax_error** (line 3240): Python syntax error in code block: invalid syntax
❌ **syntax_error** (line 3347): Python syntax error in code block: invalid syntax
❌ **syntax_error** (line 3372): Python syntax error in code block: invalid syntax
❌ **syntax_error** (line 3398): Python syntax error in code block: invalid syntax
❌ **syntax_error** (line 3426): Python syntax error in code block: invalid syntax
❌ **syntax_error** (line 3445): Python syntax error in code block: invalid syntax
❌ **syntax_error** (line 3556): Python syntax error in code block: invalid syntax
❌ **syntax_error** (line 3584): Python syntax error in code block: invalid syntax
❌ **syntax_error** (line 3600): Python syntax error in code block: invalid syntax
❌ **syntax_error** (line 3619): Python syntax error in code block: invalid syntax
❌ **syntax_error** (line 3647): Python syntax error in code block: invalid syntax
❌ **syntax_error** (line 3675): Python syntax error in code block: invalid syntax
❌ **syntax_error** (line 3725): Python syntax error in code block: invalid syntax
❌ **syntax_error** (line 3788): Python syntax error in code block: invalid syntax
❌ **syntax_error** (line 3900): Python syntax error in code block: invalid syntax
❌ **syntax_error** (line 3986): Python syntax error in code block: invalid syntax
❌ **syntax_error** (line 4011): Python syntax error in code block: invalid syntax
❌ **syntax_error** (line 4048): Python syntax error in code block: invalid syntax
❌ **syntax_error** (line 4096): Python syntax error in code block: invalid syntax
❌ **syntax_error** (line 4133): Python syntax error in code block: invalid syntax
❌ **syntax_error** (line 4172): Python syntax error in code block: invalid syntax
❌ **syntax_error** (line 4248): Python syntax error in code block: invalid syntax
❌ **syntax_error** (line 4291): Python syntax error in code block: invalid syntax
❌ **syntax_error** (line 4314): Python syntax error in code block: invalid syntax
❌ **syntax_error** (line 4362): Python syntax error in code block: invalid syntax
❌ **syntax_error** (line 4480): Python syntax error in code block: invalid syntax
❌ **syntax_error** (line 4516): Python syntax error in code block: invalid syntax
❌ **syntax_error** (line 4555): Python syntax error in code block: invalid syntax
❌ **syntax_error** (line 4616): Python syntax error in code block: invalid syntax
❌ **syntax_error** (line 4655): Python syntax error in code block: invalid syntax
❌ **syntax_error** (line 4671): Python syntax error in code block: invalid syntax
❌ **syntax_error** (line 4687): Python syntax error in code block: invalid syntax
❌ **syntax_error** (line 5049): Python syntax error in code block: invalid syntax
❌ **syntax_error** (line 5067): Python syntax error in code block: invalid syntax
❌ **syntax_error** (line 5093): Python syntax error in code block: invalid syntax
❌ **syntax_error** (line 5119): Python syntax error in code block: invalid syntax
❌ **syntax_error** (line 5154): Python syntax error in code block: invalid syntax
❌ **syntax_error** (line 5203): Python syntax error in code block: invalid syntax
❌ **broken_link** (line 4789): Broken link to '../concepts/models.md#model-copy' (text: '`model_copy`')
❌ **broken_link** (line 4826): Broken link to '../concepts/serialization.md#python-mode' (text: '`model_dump`')
❌ **broken_link** (line 4885): Broken link to '../concepts/serialization.md#json-mode' (text: '`model_dump_json`')
❌ **broken_reference** (line 6287): Broken reference link 'stage' to '''
