# API Reference: agentic_sdlc.orchestration.workflows.workflow

**Phiên bản**: 3.0.0  
**Cập nhật lần cuối**: 11/02/2026


**Module:** `agentic_sdlc.orchestration.workflows.workflow`

**Phiên bản:** 3.0.0

**Cập nhật lần cuối:** 2024-01-01

---

## Tổng Quan

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
```

---
