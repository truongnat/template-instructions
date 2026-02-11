# API Reference: agentic_sdlc.infrastructure.lifecycle.lifecycle

**Phiên bản**: 3.0.0  
**Cập nhật lần cuối**: 11/02/2026


**Module:** `agentic_sdlc.infrastructure.lifecycle.lifecycle`

**Phiên bản:** 3.0.0

**Cập nhật lần cuối:** 2024-01-01

---

## Tổng Quan

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
```

---
