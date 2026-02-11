# API Reference: agentic_sdlc.infrastructure.engine.execution_engine

**Phiên bản**: 3.0.0  
**Cập nhật lần cuối**: 11/02/2026


**Module:** `agentic_sdlc.infrastructure.engine.execution_engine`

**Phiên bản:** 3.0.0

**Cập nhật lần cuối:** 2024-01-01

---

## Tổng Quan

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
```

---
