# API Reference: agentic_sdlc.core.exceptions

**Phiên bản**: 3.0.0  
**Cập nhật lần cuối**: 11/02/2026


**Module:** `agentic_sdlc.core.exceptions`

**Phiên bản:** 3.0.0

**Cập nhật lần cuối:** 2024-01-01

---

## Tổng Quan

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
```

---
